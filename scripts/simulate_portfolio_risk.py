#!/usr/bin/env python
"""組合層前瞻風險模擬 — 候選組合之 MaxDD 分布與歷史情境重放(模擬非預測;A 軌縮版 2026-07-25 hugo 拍板)。
🎯 這支在做什麼(白話):對單一部署 cell(預設 RankRidge_H60,33 檔等權**候選組合**——in_portfolio=候選、
   非部署事實)把成分股聚合成**一條投組日報酬序列**(固定權重;共同覆蓋日交集、缺值日剔除揭露、零補值 #1),
   然後:(a) 複用 simulate_mc_paths 既有 bootstrap 引擎模 n_paths 條 h 日路徑 → 終值/MaxDD 分布 +
   P(MaxDD<risk_policy 閾值)——**參考用**;(b) 2008/2020/2022 歷史片段確定性重放——**主結論**(能引入
   756td 窗外的尾部;bootstrap 產不出窗內不存在的事件=窗偏差,summary 硬綁揭露)。
   四鎖繼承 simulate_mc_paths:①模擬非預測 disclaimer 硬綁 ②只存 summary ③不入 chat payload ④憲章
   「路徑類需求唯以模擬情境滿足」(v1.46.0 第三部 validate);風控閾值單向唯讀(不回寫 risk_policy、不觸發降倉)。
守 #1(零補值)· #8(僅 ≤as-of;as-of 機械綁權重 panel_date)· #3/#12(複用引擎與 mc_simulation_run 表、零新表)·
   #15(裸投組無 overlay=保守口徑、窗偏差、存活者偏誤全硬綁揭露)· #28 · #29a/d。
執行指令矩陣:
  python scripts/simulate_portfolio_risk.py                       # 無參數:現況(唯讀:已存 PORT_ run)
  python scripts/simulate_portfolio_risk.py --run                 # RankRidge_H60 全套:bootstrap(h=60)+三 episode
  python scripts/simulate_portfolio_risk.py --run --episode 2008  # 只跑指定情境重放
  python scripts/simulate_portfolio_risk.py --run --cell RankRidge_H120 --n-paths 10000 --seed 42
  python scripts/simulate_portfolio_risk.py --compare --cell RankRidge_H60 # 四法對照表(唯讀帳本、零重算)
  python scripts/simulate_portfolio_risk.py --selftest            # 零 DB 純紅綠(聚合數學/MaxDD 一致/揭露欄鎖)
註:bootstrap 族=四法(iid/block/stationary/garch_fhs;後二為 2026-07-26 方法擴充對照組——拆固定塊長/
   波動齊性假設;仍同窗重抽、episode 主結論地位不變)。garch_fhs 依賴 arch 套件、缺席 graceful SKIP。
"""
import argparse
import hashlib
import json
import sys

import _bootstrap  # noqa: F401
import numpy as np

from augur.core import db
from augur.evaluation.portfolio import drawdown_series
from augur.execution.risk_control import load_policies
from simulate_mc_paths import BLOCK_LEN, PCTS, _garch_fhs_paths, _git7, _simulate, _stationary_paths

BOOT_METHODS = ("iid_bootstrap", "block_bootstrap", "stationary_bootstrap", "garch_fhs")

MIN_COMMON_TD = 252            # 共同覆蓋誠實下限(不足=fail-closed 拒跑、不硬出數字)
WINDOW_TD = 756
EPISODES = {"2008": ("2008-09-01", "2009-03-31"), "2020": ("2020-01-15", "2020-04-30"),
            "2022": ("2022-01-01", "2022-12-31")}
MIN_EPISODE_W_COVER = 0.70     # 情境重放權重覆蓋誠實下限
DISCLAIMER = ("組合層模擬情境(模擬非預測):候選組合歷史報酬之重抽/重放統計,非模型預測、非熔斷預告;"
              "固定權重無風控 overlay=裸投組保守口徑;與方向軸機率/risk_control 實際觸發判定分欄、永不混排。")


def _load_cell_portfolio(cur, cell):
    cur.execute("""SELECT panel_date, stock_id, weight FROM prediction_values
        WHERE model_id LIKE %s AND in_portfolio
          AND panel_date=(SELECT max(panel_date) FROM prediction_values)
        ORDER BY stock_id""", (cell + "%",))
    rows = cur.fetchall()
    if not rows:
        raise RuntimeError(f"cell {cell} 無候選組合列(prediction_values in_portfolio)")
    panel = rows[0][0]
    members = [(sid, float(w)) for _, sid, w in rows]
    wsum = sum(w for _, w in members)
    assert abs(wsum - 1.0) < 1e-6, f"權重和 {wsum} ≠ 1(cell 圈選錯誤?)"
    return panel, members


def _member_closes(cur, sids, since, until):
    cur.execute("""SELECT stock_id, date, close FROM "TaiwanStockPriceAdj"
        WHERE stock_id = ANY(%s) AND date BETWEEN %s AND %s AND close > 0
        ORDER BY date""", (list(sids), since, until))
    by_stock = {}
    for sid, d, c in cur.fetchall():
        by_stock.setdefault(sid, {})[d] = float(c)
    return by_stock


def _portfolio_returns(members, by_stock, dates_all):
    """共同覆蓋日交集 → 固定權重投組簡單報酬序列。回 (rets, common_dates, dropped_n)。零補值(#1)。"""
    sids = [s for s, _ in members]
    common = [d for d in dates_all if all(d in by_stock.get(s, {}) for s in sids)]
    dropped = len(dates_all) - len(common)
    if len(common) < 2:
        return np.array([]), common, dropped
    rets = []
    for prev, cur_d in zip(common, common[1:]):
        r = sum(w * (by_stock[s][cur_d] / by_stock[s][prev] - 1.0) for s, w in members)
        rets.append(r)
    return np.array(rets), common, dropped


def _maxdd_per_path(paths):
    """paths=累積簡單報酬[n,h] → 各路徑 MaxDD(負值)。與 drawdown_series 同義之向量化版(selftest 鎖一致)。"""
    wealth = 1.0 + paths
    runmax = np.maximum.accumulate(wealth, axis=1)
    return (wealth / runmax - 1.0).min(axis=1)


def _bootstrap_summary(logr, h, n_paths, method, seed, policies, window_maxdd, meta):
    rng = np.random.default_rng(seed)
    fit_diag = None
    if method == "stationary_bootstrap":             # 方法擴充 2026-07-26:對照組(拆固定塊長假設)
        paths = _stationary_paths(logr, h, n_paths, BLOCK_LEN, rng)
    elif method == "garch_fhs":                      # 對照組(拆波動齊性假設);缺 arch → None=SKIP
        try:
            paths, fit_diag = _garch_fhs_paths(logr, h, n_paths, rng)
        except ImportError:
            return None
    else:
        paths = _simulate(logr, h, n_paths, method, BLOCK_LEN, rng)
    term, mdd = paths[:, -1], _maxdd_per_path(paths)
    dd_gate = policies.get("dd_circuit", {})
    thr = dd_gate.get("threshold")
    summ = {
        "disclaimer": DISCLAIMER, "kind": "bootstrap_reference", **meta,
        "terminal": {f"ret_p{p}": round(float(np.percentile(term, p)), 5) for p in PCTS},
        "maxdd": {f"p{p}": round(float(np.percentile(mdd, p)), 5) for p in PCTS},
        "p_maxdd_lt_policy": (None if thr is None else round(float((mdd < thr).mean()), 4)),
        "policy_threshold": thr,
        "p_maxdd_lt_info": {f"{t:+.0%}": round(float((mdd < t).mean()), 4) for t in (-0.10, -0.15)},
        "window_actual_maxdd": round(window_maxdd, 5),
        "note_policy": "P(MaxDD<閾)=歷史重抽之模擬統計,非模型預測、非熔斷預告;閾值唯讀自 risk_policy、"
                       "模擬結果不回寫不觸發;-10%/-15% 檔位=資訊性分位、非既有閾值",
        "note_window_bias": "重抽窗內無某級事件→該檔位機率≈0 係窗的性質、非安全證據;窗內實際最深回檔="
                            f"{window_maxdd:+.1%}(錨);主結論請看 episode_replay 列",
    }
    if fit_diag:
        summ["fit_diag"] = fit_diag                  # garch_fhs 擬合品質入帳可稽(方法擴充計畫 §二)
    return summ


def _episode_summary(members, by_stock, dates_all, name, policies, meta):
    sids = [s for s, _ in members]
    covered = [(s, w) for s, w in members if any(d in by_stock.get(s, {}) for d in dates_all)]
    w_cover = sum(w for _, w in covered)
    if w_cover < MIN_EPISODE_W_COVER:
        return {"disclaimer": DISCLAIMER, "kind": "episode_refused", **meta,
                "episode": name, "weight_coverage": round(w_cover, 4),
                "note": f"權重覆蓋 {w_cover:.0%} < {MIN_EPISODE_W_COVER:.0%} 誠實下限→拒答(不硬出數字,#15)"}
    renorm = [(s, w / w_cover) for s, w in covered]
    rets, common, dropped = _portfolio_returns(renorm, by_stock, dates_all)
    if len(rets) < 20:
        return {"disclaimer": DISCLAIMER, "kind": "episode_refused", **meta, "episode": name,
                "note": f"共同覆蓋僅 {len(rets)} td→拒答"}
    cum = float(np.prod(1.0 + rets) - 1.0)
    mdd = float(drawdown_series(list(rets))[1].min())
    return {
        "disclaimer": DISCLAIMER, "kind": "episode_replay", **meta,
        "episode": name, "span": [str(common[0]), str(common[-1])], "n_td": len(rets),
        "cum_return": round(cum, 5), "maxdd": round(mdd, 5),
        "weight_coverage": round(w_cover, 4), "n_members_covered": len(covered),
        "dropped_dates": dropped,
        "note_single_scenario": "歷史情境重放=單一確定性路徑,非機率、非分布、非預測;與 bootstrap 分布分欄永不混排",
        "note_survivor": "本重放含存活者偏誤:成分=今日候選組合(活到今天的股)、非當年可選集,結果偏樂觀",
        "note_renorm": f"未覆蓋成分已剔除、權重再正規化(={len(covered)}/{len(members)} 檔之縮水投組,明標非原組合)",
    }


def run(cell, episodes, n_paths, seed, h):
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        panel, members = _load_cell_portfolio(cur, cell)
        horizon = int(cell.rsplit("_H", 1)[-1]) if "_H" in cell else h
        policies = load_policies(conn, horizon)
        target = f"PORT_{cell}_{panel}"
        meta = {"cell": cell, "panel_date": str(panel), "n_members": len(members),
                "note_candidate": "in_portfolio=候選組合成員(非部署事實;predict_asof D4 語意)"}
        # 聚合(≤panel、共同覆蓋、零補值)
        cur.execute("""SELECT DISTINCT date FROM "TaiwanStockPriceAdj"
            WHERE stock_id=%s AND date<=%s AND close>0 ORDER BY date DESC LIMIT %s""",
            (members[0][0], panel, WINDOW_TD + 1))
        dates_win = [r[0] for r in cur.fetchall()][::-1]
        by_stock = _member_closes(cur, [s for s, _ in members], dates_win[0], panel)
        rets, common, dropped = _portfolio_returns(members, by_stock, dates_win)
        if len(rets) < MIN_COMMON_TD:
            print(f"✗ 共同覆蓋 {len(rets)} td < {MIN_COMMON_TD} 誠實下限→拒跑(fail-closed)"); return 1
        logr = np.log1p(rets)
        window_maxdd = float(drawdown_series(list(rets))[1].min())
        print(f"候選組合 {cell}@{panel}:{len(members)} 檔|共同覆蓋 {len(rets)} td(剔除 {dropped} 日)|"
              f"窗內實際 MaxDD={window_maxdd:+.1%}")
        rows = []
        for method in BOOT_METHODS:
            summ = _bootstrap_summary(logr, horizon, n_paths, method, seed, policies, window_maxdd,
                                      {**meta, "effective_window_td": len(rets), "dropped_dates": dropped})
            if summ is None:
                print(f"  [參考] {method:<19} SKIP(arch 未安裝——graceful、非失敗)"); continue
            rows.append((method, BLOCK_LEN if method in ("block_bootstrap", "stationary_bootstrap") else None,
                         horizon, summ))
            fd = summ.get("fit_diag")
            print(f"  [參考] {method:<19} h={horizon} | MaxDD p50={summ['maxdd']['p50']:+.1%} "
                  f"p95={summ['maxdd']['p95']:+.1%} | P(MaxDD<{summ['policy_threshold']})={summ['p_maxdd_lt_policy']}"
                  + (f" | persistence={fd['persistence']}" if fd else ""))
        for ep in episodes:
            s, e = EPISODES[ep]
            cur.execute("""SELECT DISTINCT date FROM "TaiwanStockPriceAdj"
                WHERE date BETWEEN %s AND %s ORDER BY date""", (s, e))
            ep_dates = [r[0] for r in cur.fetchall()]
            ep_closes = _member_closes(cur, [x for x, _ in members], s, e)
            summ = _episode_summary(members, ep_closes, ep_dates, ep, policies, meta)
            rows.append((f"episode_replay_{ep}", None, summ.get("n_td", 0) or 1, summ))
            tag = (f"cum={summ['cum_return']:+.1%} MaxDD={summ['maxdd']:+.1%} 權重覆蓋={summ['weight_coverage']:.0%}"
                   if summ["kind"] == "episode_replay" else summ["note"])
            print(f"  [主結論] episode {ep}: {tag}")
        for method, blk, hh, summ in rows:
            key = f"mc_{target}_{panel}_{hh}_{method}_{seed}"
            run_id = "mc_" + hashlib.sha256(key.encode()).hexdigest()[:16]
            cur.execute("""INSERT INTO mc_simulation_run
                (run_id, target_id, asof_date, horizon_td, method, block_len_td, n_paths, seed,
                 summary, is_simulation, git_sha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true,%s)
                ON CONFLICT (run_id) DO UPDATE SET summary=EXCLUDED.summary, created_at=now()""",
                (run_id, target, panel, hh, method, blk,
                 n_paths if method.endswith("bootstrap") else 1, seed,
                 json.dumps(summ, ensure_ascii=False, default=str), git7))
        conn.commit()
    print(f"✓ 完成(is_simulation=true;只存摘要;seed={seed} 可重現)\n  ⚠ {DISCLAIMER}")
    return 0


def compare(cell):
    """四法對照(唯讀帳本、零重算;方法擴充計畫 P3):MaxDD 分位並排+P(MaxDD<閾)。判讀按計畫 §一預註冊規則。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT method, summary FROM mc_simulation_run
            WHERE target_id LIKE %s AND method = ANY(%s) ORDER BY array_position(%s::text[], method)""",
            (f"PORT_{cell}_%", list(BOOT_METHODS), list(BOOT_METHODS)))
        rows = cur.fetchall()
    if not rows:
        print(f"(cell {cell} 無 bootstrap 族 run;先 --run)"); return 1
    print(f"{cell} 四法對照(參考層;主結論=episode_replay、不在此表):")
    print(f"  {'method':<20}{'MaxDD p5':>10}{'p25':>8}{'p50':>8}{'p95':>8}{'P(<閾)':>9}")
    for m, s in rows:
        md, p = s["maxdd"], s.get("p_maxdd_lt_policy")
        print(f"  {m:<20}{md['p5']:>10.1%}{md['p25']:>8.1%}{md['p50']:>8.1%}{md['p95']:>8.1%}"
              f"{('n/a' if p is None else format(p, '.4f')):>9}")
        fd = s.get("fit_diag")
        if fd:
            print(f"      fit: ω={fd['omega']} α={fd['alpha']} β={fd['beta']} "
                  f"persistence={fd['persistence']} converged={fd['converged']}")
    print("  ⚠ 窗偏差不變:四法皆重抽同一窗、變不出窗外事件;episode 重放主結論地位不變")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT target_id, method, horizon_td,
                       coalesce(summary->'maxdd'->>'p95', summary->>'maxdd') AS mdd
                       FROM mc_simulation_run WHERE target_id LIKE 'PORT_%' ORDER BY created_at DESC LIMIT 12""")
        rows = cur.fetchall()
    if not rows:
        print("(尚無 PORT_ 組合層模擬 run;--run 產生)")
    for t, m, h, mdd in rows:
        print(f"  {t} {m:<22} h={h:<4} maxdd(p95或情境)={mdd}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    import datetime as dt
    d = [dt.date(2026, 1, i) for i in range(1, 6)]
    by = {"A": {d[0]: 100, d[1]: 110, d[2]: 99, d[3]: 99, d[4]: 120},
          "B": {d[0]: 50, d[1]: 55, d[2]: 45, d[4]: 60}}          # B 缺 d[3]
    rets, common, dropped = _portfolio_returns([("A", .5), ("B", .5)], by, d)
    chk("共同覆蓋剔缺值日(#1 零補值)", dropped == 1 and len(common) == 4)
    chk("聚合數學:等權兩股首日報酬=(10%+10%)/2", abs(rets[0] - 0.10) < 1e-12)
    paths = np.array([[0.10, -0.10, 0.20]])
    chk("MaxDD 向量化=drawdown_series 同義",
        abs(_maxdd_per_path(paths)[0] - drawdown_series([0.10, (0.9 / 1.1) - 1, (1.2 / 0.9) - 1])[1].min()) < 1e-12)
    ep = _episode_summary([("A", .5), ("B", .5)], {"A": by["A"]}, d, "2008", {}, {})
    chk("episode 權重覆蓋<70%→誠實拒答", ep["kind"] == "episode_refused")
    bs = _bootstrap_summary(np.log1p(np.array([0.01, -0.02] * 130)), 5, 50, "iid_bootstrap", 42,
                            {"dd_circuit": {"threshold": -0.2}}, -0.05, {})
    for note in ("note_policy", "note_window_bias", "disclaimer"):
        chk(f"揭露欄硬綁:{note}", note in bs and bool(bs[note]))
    d30 = [dt.date(2026, 2, 1) + dt.timedelta(days=i) for i in range(30)]
    by30 = {"A": {dd: 100 + i for i, dd in enumerate(d30)}}
    ep_ok = _episode_summary([("A", 1.0)], by30, d30, "x", {}, {})
    chk("情境揭露欄硬綁三件", ep_ok["kind"] == "episode_replay" and all(
        k in ep_ok for k in ("note_single_scenario", "note_survivor", "note_renorm")))
    # 方法擴充增項(2026-07-26 計畫 P1)
    lr = np.tile(np.array([0.01, -0.02, 0.005, 0.003]), 75)
    p_a = _stationary_paths(lr, 8, 5, BLOCK_LEN, np.random.default_rng(7))
    chk("stationary:同 seed 逐位重現", np.array_equal(
        p_a, _stationary_paths(lr, 8, 5, BLOCK_LEN, np.random.default_rng(7))))
    chk("stationary:形狀/有限", p_a.shape == (5, 8) and np.isfinite(p_a).all())
    big = _stationary_paths(lr, 6, 3, 10 ** 9, np.random.default_rng(3))
    stp = np.diff(np.concatenate([np.zeros((3, 1)), np.log1p(big)], axis=1), axis=1)
    m = len(lr)
    chk("stationary:mean_block→∞ 退化為環繞連續片段", all(
        any(np.allclose(stp[i], np.take(lr, (np.arange(6) + st) % m)) for st in range(m)) for i in range(3)))
    try:
        import arch  # noqa: F401
        rng = np.random.default_rng(11)
        syn = np.concatenate([rng.normal(0, .005, 200), rng.normal(0, .03, 100), rng.normal(0, .005, 200)])
        gp, fd = _garch_fhs_paths(syn, 10, 50, np.random.default_rng(5))
        chk("garch_fhs:persistence∈(0,1) 且收斂", 0 < fd["persistence"] < 1 and fd["converged"])
        chk("garch_fhs:形狀/有限/fit_diag 齊", gp.shape == (50, 10) and np.isfinite(gp).all()
            and all(k in fd for k in ("omega", "alpha", "beta", "n_obs", "note_fit")))
    except ImportError:
        print("  ⊘ garch_fhs 兩項 SKIP(arch 未安裝——graceful 非 FAIL)")
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="組合層前瞻風險模擬(模擬非預測)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--cell", default="RankRidge_H60")
    ap.add_argument("--episode", choices=[*EPISODES, "all"], default="all")
    ap.add_argument("--n-paths", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.compare:
        return compare(a.cell)
    if not a.run:
        print(__doc__)
        return status()
    eps = list(EPISODES) if a.episode == "all" else [a.episode]
    return run(a.cell, eps, a.n_paths, a.seed, 60)


if __name__ == "__main__":
    sys.exit(main())
