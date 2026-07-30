#!/usr/bin/env python
"""meta-replay 引擎 — 凍結程序之逐 cutoff walk-forward(META-REPLAY-go,hugo 2026-07-29)。

🎯 這支在做什麼(白話):對每個 cutoff:用**凍結程序**與 ≤cutoff 資料選 prodset(三關:單因子 HAC
   |t|≥2 → 增量(僅新過關者,2 seeds) → 符號(map 快照方向;首 cutoff 跳增量=bootstrap,記錄於
   decisions)→ 量測次期 panel 之「程序集 vs 靜態基準(首 cutoff 集凍住)」IC 差。程序版=proc_sha
   (程序碼+參數+特徵池+map 快照之雜湊)——**中途任何變動=新 sha 新家族,舊列不覆**。
   宣稱域章(每次輸出首行):固定現行工具箱與判準之程序歷史逐期 OOS 增益;非「當年就會賺」。
守 #8(panels ≤cutoff 斷言+label 窗防越 next panel)· #12(複用 vcp/vss/baseline 機具)· #15 · #29a/d。
SSOT=reports/augur_meta_replay_plan_20260729.md §三;meta 門判準另評(evaluate 先凍後跑)。

執行指令矩陣:
  python scripts/run_meta_replay.py                  # 無參數:現況(帳本進度,唯讀)
  python scripts/run_meta_replay.py --probe-one      # #25 單 cutoff(現網格倒數第2 panel)
  python scripts/run_meta_replay.py --from 2018-01-01 --to 2026-04-30 --step quarter --run
  python scripts/run_meta_replay.py --selftest       # 零 DB 紅綠(程序鎖/防越斷言)
"""
import argparse
import hashlib
import inspect
import json
import sys
from datetime import timedelta

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db

SCOPE_STAMP = ("【宣稱域】固定現行工具箱與判準之程序歷史逐期 OOS 增益(META-REPLAY 計畫 §二);"
               "工具箱含後見之明,禁『當年就會賺』解讀")
PROC_PARAMS = {"h": 20, "hac_t_min": 2.0, "gate2_seeds": [42, 43], "sign_boot_seeds": 5,
               "bootstrap_rule": "首 cutoff 跳 gate2", "min_ic_panels": 8,
               "label_guard": "train panel + h*1.45 日曆日 ≤ next panel"}


def gate1_hac(ic_sub, t_min):
    """單因子關:HAC |t|≥t_min 且 n≥min_ic_panels。純函式(吃 metrics)。"""
    from augur.evaluation import metrics
    if len(ic_sub) < PROC_PARAMS["min_ic_panels"]:
        return (False, None)
    t = metrics.effective_t_hac(ic_sub)
    return (t is not None and abs(t) >= t_min, t)


def label_guarded_train(panels_k, next_p, h):
    """訓練 panel 防越:label 窗(h×1.45 日曆日)不越 next panel(#8)。純函式。"""
    return [p for p in panels_k if p + timedelta(days=int(h * 1.45)) <= next_p]


def compute_proc_sha(pool, map_snap, panels):
    """程序身分=碼+參數+池+map 快照+**panel 網格**(網格變=另一家族;GRID-A 加密後自動分家,防混帳)。"""
    h = hashlib.sha256()
    for fn in (gate1_hac, label_guarded_train, run_cutoffs):
        h.update(inspect.getsource(fn).encode())
    h.update(json.dumps(PROC_PARAMS, sort_keys=True).encode())
    h.update(json.dumps(sorted(pool)).encode())
    h.update(json.dumps({k: str(v) for k, v in sorted(map_snap.items())}).encode())
    h.update(json.dumps([str(p) for p in panels]).encode())
    return h.hexdigest()[:12]


def next_panel_ic(conn, train_panels, next_p, feats, seed):
    """單折次期 IC:train=防越後 panels(as-of)、test=next panel。鏡射 baseline 模型規格(#12)。"""
    from lightgbm import LGBMRegressor
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    from augur.evaluation import baseline, metrics
    from augur.evaluation import label as label_mod
    cal = label_mod.full_calendar(conn)
    stocks = baseline._asof_stocks(conn, next_p)
    ts_sids, Xte = baseline._panel_matrix(conn, next_p, stocks, feats)
    if len(ts_sids) < 5:
        return {}
    lab = label_mod.labels(conn, next_p, ts_sids, PROC_PARAMS["h"], calendar=cal)
    keep = [i for i, s in enumerate(ts_sids) if s in lab]
    if len(keep) < 5:
        return {}
    Xte, ts_sids = Xte[keep], [ts_sids[i] for i in keep]
    ylab = {s: lab[s] for s in ts_sids}
    Xtr, ytr = baseline._fold_xy(conn, train_panels, None, feats, PROC_PARAMS["h"], calendar=cal, asof=True)
    if Xtr is None or len(ytr) < 50:
        return {}
    out = {}
    sc = StandardScaler().fit(Xtr)
    rdg = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr)
    out["B2_ridge"] = metrics.rank_ic(dict(zip(ts_sids, rdg.predict(sc.transform(Xte)))), ylab)
    gbm = LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=15,
                        min_child_samples=30, subsample=0.8, colsample_bytree=0.8,
                        random_state=seed, verbose=-1).fit(Xtr, ytr)
    out["M1_gbdt"] = metrics.rank_ic(dict(zip(ts_sids, gbm.predict(Xte))), ylab)
    out["_n"] = len(ts_sids)
    return out


def run_cutoffs(cutoffs, probe=False):
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    import verify_candidate_promotion as vcp
    import verify_sign_consistency as vss
    from augur.evaluation import baseline
    from augur.evaluation import label as label_mod
    print(SCOPE_STAMP)
    with db.connect() as conn:
        cur = conn.cursor()
        panels = vcp._asof_panels(cur)
        cur.execute("SELECT DISTINCT feature FROM feature_values ORDER BY 1")
        pool = [r[0] for r in cur.fetchall()]
        map_snap = {f: vss.map_direction(cur, f) for f in pool}
        psha = compute_proc_sha(pool, map_snap, panels)
        cal = label_mod.full_calendar(conn)
        print(f"proc_sha={psha} 池={len(pool)} 特徵 panels={len(panels)}")
        ic_cache = {}

        def ic_series(f):
            if f not in ic_cache:
                ic_cache[f] = vcp._asof_ic_series(conn, panels, PROC_PARAMS["h"], f, cal)
            return ic_cache[f]

        h = PROC_PARAMS["h"]
        ladder_cache = {}   # (tuple(feats), tuple(panels_k), seed) -> run_ladder 結果(跨 cutoff 重用;
                            # incumbent 常數段免重算——preview 44 分/cutoff 之主刀)
        for ci, cutoff in enumerate(cutoffs):
            cur.execute("SELECT 1 FROM meta_replay_cutoff WHERE proc_sha=%s AND cutoff_date=%s", (psha, cutoff))
            if cur.fetchone():
                continue
            panels_k = [p for p in panels if p <= cutoff]
            assert all(p <= cutoff for p in panels_k)
            nxt = [p for p in panels if p > cutoff]
            if not nxt:
                print(f"  {cutoff}: 無次期 panel——跳過")
                continue
            next_p = nxt[0]
            cur.execute("""SELECT prodset FROM meta_replay_cutoff WHERE proc_sha=%s AND cutoff_date<%s
                           ORDER BY cutoff_date DESC LIMIT 1""", (psha, cutoff))
            row = cur.fetchone()
            incumbent = list(row[0]) if row else None
            dec = {}
            passers13 = []
            for f in pool:
                sub = {p: v for p, v in ic_series(f).items() if p <= cutoff}
                ok1, t = gate1_hac(sub, PROC_PARAMS["hac_t_min"])
                d = map_snap[f]
                ok3 = None
                if ok1 and d in (1, -1):
                    ics = np.array(list(sub.values()))
                    boots = [float(ics[np.random.default_rng(42 + k).integers(0, len(ics), len(ics))].mean())
                             for k in range(PROC_PARAMS["sign_boot_seeds"])]
                    ok3 = vss.judge_sign(float(ics.mean()), boots, d) == "PASS"
                dec[f] = {"g1": ok1, "hac_t": (round(t, 2) if t is not None else None),
                          "dir": d if d in (1, -1) else str(d), "g3": ok3}
                if ok1 and ok3:
                    passers13.append(f)
            if not incumbent:   # None 或空集皆 bootstrap——空集無從測增量;且 run_ladder(feats=[]) 會
                                # falsy 退回全 canonical 當基準(2026-07-29 preview 抓到的卡空雷)
                prodset = sorted(passers13)
                dec["_bootstrap"] = "無現任(None/空)跳 gate2 直收 passers(凍結規則)"
            else:
                drop = [f for f in incumbent if f in dec and dec[f]["g3"] is False]
                keep = [f for f in incumbent if f not in drop]
                add = []
                def _ladder(feats_l, seed):
                    key = (tuple(feats_l), tuple(panels_k), seed)
                    if key not in ladder_cache:
                        ladder_cache[key] = baseline.run_ladder(conn, panels_k, h, None,
                                                                feats=feats_l, seed=seed, asof=True)
                    return ladder_cache[key]

                for f in [x for x in passers13 if x not in incumbent]:
                    deltas = []
                    for seed in PROC_PARAMS["gate2_seeds"]:
                        rb = _ladder(keep, seed)
                        ra = _ladder(keep + [f], seed)
                        dv = [(ra[m]["mean_ic"] or 0) - (rb[m]["mean_ic"] or 0) for m in ("B2_ridge", "M1_gbdt")]
                        deltas.append(float(np.mean(dv)))
                    dec[f]["g2_deltas"] = [round(x, 5) for x in deltas]
                    if all(x > 0 for x in deltas):
                        add.append(f)
                prodset = sorted(keep + add)
                dec["_moves"] = {"add": add, "drop": drop}
            cur.execute("""INSERT INTO meta_replay_cutoff (proc_sha, cutoff_date, prodset, decisions)
                VALUES (%s,%s,%s,%s)""", (psha, cutoff, json.dumps(prodset), json.dumps(dec, ensure_ascii=False)))
            conn.commit()
            # 靜態基準=首個**非空** prodset 凍住(空集無 IC,不能當基準——preview 家族二之 靜態=None 教訓;
            # 「起點集」之唯一合理操作化,落註)
            cur.execute("""SELECT prodset FROM meta_replay_cutoff WHERE proc_sha=%s
                           AND jsonb_array_length(prodset) > 0 ORDER BY cutoff_date LIMIT 1""", (psha,))
            row_s = cur.fetchone()
            static_set = list(row_s[0]) if row_s else []
            tr = label_guarded_train(panels_k, next_p, h)
            perf = next_panel_ic(conn, tr, next_p, prodset, 42) if prodset else {}
            perf_s = next_panel_ic(conn, tr, next_p, static_set, 42) if static_set else {}
            for m in ("B2_ridge", "M1_gbdt"):
                cur.execute("""INSERT INTO meta_replay_perf
                    (proc_sha, cutoff_date, model, ic_next, ic_next_static, n_stocks)
                    VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                    (psha, cutoff, m, perf.get(m), perf_s.get(m), perf.get("_n")))
            conn.commit()
            print(f"  ✓ {cutoff}: prodset {len(prodset)} 檔"
                  + (f"(+{len(dec.get('_moves', {}).get('add', []))}/-{len(dec.get('_moves', {}).get('drop', []))})"
                     if incumbent else "(bootstrap)")
                  + f" 次期IC ridge={perf.get('B2_ridge')} vs 靜態={perf_s.get('B2_ridge')}", flush=True)
            if probe:
                print("  (probe:決策 JSON)")
                print(json.dumps({k: v for k, v in list(dec.items())[:6]}, ensure_ascii=False, indent=1)[:900])
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.meta_replay_cutoff')")
        if cur.fetchone()[0] is None:
            print("  (帳本未建;migrate_meta_replay_ddl --apply)")
            return 0
        cur.execute("""SELECT proc_sha, count(*) FROM meta_replay_cutoff GROUP BY 1""")
        print("  帳本:", cur.fetchall() or "(空)")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    from datetime import date
    tr = label_guarded_train([date(2026, 1, 31), date(2026, 3, 31)], date(2026, 3, 31), 20)
    chk("label 防越:近 cutoff panel 被剔(20td≈29 日曆日)", tr == [date(2026, 1, 31)])
    chk("宣稱域章在(每輸出首行)", "禁『當年就會賺』" in SCOPE_STAMP)
    src = inspect.getsource(run_cutoffs)
    chk("panels≤cutoff 斷言", "assert all(p <= cutoff" in src)
    chk("resume:同 (sha,cutoff) 跳過", "SELECT 1 FROM meta_replay_cutoff" in src)
    chk("bootstrap 規則記錄於 decisions", "_bootstrap" in src)
    chk("空現任=bootstrap(run_ladder 空列表 falsy 雷,preview 2026-07-29)", "if not incumbent:" in src)
    chk("sign-refuted 現任剔除(同 R3 精神)", '"g3"] is False' in src)
    chk("靜態基準=首 cutoff 集(帳本讀,非重算)", "ORDER BY cutoff_date LIMIT 1" in src)
    chk("proc_sha 含程序碼+參數+池+map 快照+panel 網格(網格變=分家)",
        "map_snap" in inspect.getsource(compute_proc_sha)
        and "panels" in inspect.getsource(compute_proc_sha))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="meta-replay 引擎(凍結程序 walk-forward)")
    ap.add_argument("--from", dest="w_from")
    ap.add_argument("--to", dest="w_to")
    ap.add_argument("--step", choices=["quarter", "month", "panel"], default="panel")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--probe-one", action="store_true", dest="probe")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.probe:
        with db.connect() as conn, db.transaction(conn) as cur:
            sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
            import verify_candidate_promotion as vcp
            panels = vcp._asof_panels(cur)
        return run_cutoffs(panels[-2:-1], probe=True)
    if a.run and a.w_from and a.w_to:
        from datetime import date
        f, t = date.fromisoformat(a.w_from), date.fromisoformat(a.w_to)
        with db.connect() as conn, db.transaction(conn) as cur:
            sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
            import verify_candidate_promotion as vcp
            panels = vcp._asof_panels(cur)
        cutoffs = [p for p in panels if f <= p <= t]
        if a.step == "quarter":
            cutoffs = [p for p in cutoffs if p.month in (3, 6, 9, 12)]
        return run_cutoffs(cutoffs)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
