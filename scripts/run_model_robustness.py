#!/usr/bin/env python
"""模型級穩健性五軸 — 子期間校準/rank 自相關/LOFO/特徵擾動/宇宙子集(驗證總綱 V1 缺口②)。

🎯 這支在做什麼(白話):在**既有** OOS/特徵面板上重算(零新資料、FREEZE 內),量「機率數字可不可信」:
   (a) calib:era 分解(年頻 2016-2020 vs 季頻 2021+)之折級 Brier skill/ECE——近代校準有沒有失效;
   (b) rank:相鄰季頻 panel score Spearman——量換手率(低≠不穩健,F9 語意防誤讀);
   (c) lofo:**真 LOFO 全 walk-forward 重訓**(§2.0 凍結口徑;棄用固定係數法)——單點依賴紅旗;
   (d) perturb:標準化特徵加 N(0,0.1²) 噪聲(seeds 41/42/43)之 score Spearman——描述性、不設判準;
   (e) subset:宇宙隨機半切 IC 同號率。
   **先凍後跑**:開跑守門斷言 R 軌 5 列 frozen 皆在,否則 exit 1;R 軌性質=annotate/review 非自動判停
   (econ 已判 thin;觸紅→人裁)。結果落 revalidation_ledger stage='R'(#29c 復用、不建新表)。

守 #8(全在凍結快照)· #11(隨機處固定 seeds{41,42,43})· #12(折邏輯鏡射 build_probability_oos_sample、
   helper 同一住所)· #15(min/max 誠實展示非只中位)· #28(本地零 usage)· #29a/c/d。
   SSOT=reports/augur_prediction_validation_master_plan_20260711.md §2。

執行指令矩陣:
  python scripts/run_model_robustness.py                          # 無參數:印矩陣+R 軌凍結現況(唯讀)
  python scripts/run_model_robustness.py --axis calib --horizon 60 --dry-run   # 單軸單 horizon 算不落帳
  python scripts/run_model_robustness.py --axis calib --run       # 單軸全 horizon 落帳
  python scripts/run_model_robustness.py --axis all --run         # 五軸全跑(lofo 重、小時級)
"""
import argparse
import json
import math
import statistics
import sys

import _bootstrap  # noqa: F401
import numpy as np

from augur.core import db
from augur.evaluation import baseline, walkforward
from augur.evaluation import label as label_mod

HORIZONS = (20, 40, 60, 120)
AS_OF = "2026-05-31"
MODEL_FAMILY = "RankRidge"
ERA_SPLIT = "2021-01-01"       # 年頻→季頻 cadence 邊界(§2.1 按資料節奏切、非折數均分)
PERTURB_SIGMA = 0.1            # N(0,0.1²)(計畫建議值;用戶 2026-07-11 依計畫拍板)
SEEDS = (41, 42, 43)           # #11 ≥3


def _spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 5 or np.std(x) == 0 or np.std(y) == 0:
        return None
    xr = np.argsort(np.argsort(x)); yr = np.argsort(np.argsort(y))
    return float(np.corrcoef(xr, yr)[0, 1])


def _assert_prereg_frozen(cur):
    """先凍後跑守門(§2.0):R 軌 5 列 frozen=true 皆在,否則 exit 1。"""
    cur.execute("SELECT count(*) FROM judgestop_threshold WHERE track='R_robust' AND frozen")
    n = cur.fetchone()[0]
    if n < 5:
        sys.exit(f"✗ 先凍後跑:R_robust frozen 列僅 {n}/5——判準未凍結,拒跑(§2.0)")


def _write(cur, h, axis, cfg, metric, value, n_periods, note=None):
    cur.execute("INSERT INTO revalidation_ledger (as_of_date, stage, horizon, model, config, "
                "metric_name, metric_value, n_periods, hac_t, note) VALUES (%s,'R',%s,%s,%s,%s,%s,%s,NULL,%s)",
                (AS_OF, h, MODEL_FAMILY, json.dumps(dict(cfg, axis=axis), ensure_ascii=False),
                 metric, value, n_periods, note))


# ── (a) calib:era 分解折級 Brier skill/ECE ─────────────────────────────────
def _platt_fit(x, y):
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression(C=1e6, solver="lbfgs")
    lr.fit(np.asarray(x).reshape(-1, 1), np.asarray(y, dtype=int))
    return float(lr.coef_[0][0]), float(lr.intercept_[0])


def axis_calib(conn, h, sink):
    cur = conn.cursor()
    cur.execute("SELECT panel_date, rank_pctile, label_beat_median FROM probability_oos_sample "
                "WHERE horizon=%s AND model_family=%s ORDER BY panel_date", (h, MODEL_FAMILY))
    rows = cur.fetchall()
    panels = sorted({r[0] for r in rows})
    by = {p: ([], []) for p in panels}
    for p, x, y in rows:
        by[p][0].append(float(x)); by[p][1].append(bool(y))
    fold_stats = []                                    # (panel, skill, probs, ys)
    for i in range(1, len(panels)):
        xs = [v for p in panels[:i] for v in by[p][0]]
        ys = [v for p in panels[:i] for v in by[p][1]]
        if len(set(ys)) < 2:
            continue
        a, b = _platt_fit(xs, ys)
        xt, yt = by[panels[i]]
        pt = [1.0 / (1.0 + math.exp(-(a * x + b))) for x in xt]
        brier = float(np.mean([(p - y) ** 2 for p, y in zip(pt, yt)]))
        base = float(np.mean([(0.5 - y) ** 2 for y in yt]))
        fold_stats.append((panels[i], base - brier, pt, [float(y) for y in yt]))
    from datetime import date
    era_cut = date.fromisoformat(ERA_SPLIT)
    for era, sel in (("yearly", [f for f in fold_stats if f[0] < era_cut]),
                     ("quarterly", [f for f in fold_stats if f[0] >= era_cut])):
        if not sel:
            continue
        skills = [f[1] for f in sel]
        probs = [p for f in sel for p in f[2]]
        ys = [y for f in sel for y in f[3]]
        # era ECE(10 bin、era 內合併)
        bins = np.clip((np.asarray(probs) * 10).astype(int), 0, 9)
        ece = float(sum(abs(np.mean(np.asarray(probs)[bins == b2]) - np.mean(np.asarray(ys)[bins == b2]))
                        * np.sum(bins == b2) for b2 in range(10) if np.sum(bins == b2)) / len(probs))
        note = "年頻 era 描述性參照(4-5 折,不設判準)" if era == "yearly" else None
        sink(h, "calib_era", {"era": era}, "brier_skill_median", float(statistics.median(skills)), len(sel), note)
        sink(h, "calib_era", {"era": era}, "brier_skill_min", float(min(skills)), len(sel), note)
        sink(h, "calib_era", {"era": era}, "brier_skill_max", float(max(skills)), len(sel), note)
        sink(h, "calib_era", {"era": era}, "ece_era", ece, len(sel), note)
        print(f"  H{h} calib[{era}]: skill med={statistics.median(skills):+.4f} "
              f"[{min(skills):+.4f},{max(skills):+.4f}] ece={ece:.4f}({len(sel)} 折)")


# ── (b) rank:相鄰 panel score Spearman ────────────────────────────────────
def axis_rank(conn, h, sink):
    cur = conn.cursor()
    cur.execute("SELECT panel_date, stock_id, score FROM probability_oos_sample "
                "WHERE horizon=%s AND model_family=%s", (h, MODEL_FAMILY))
    by = {}
    for p, s, sc in cur.fetchall():
        by.setdefault(p, {})[s] = float(sc)
    panels = sorted(by)
    from datetime import date
    era_cut = date.fromisoformat(ERA_SPLIT)
    qs, ys_, bd = [], [], []
    for a, b in zip(panels, panels[1:]):
        common = set(by[a]) & set(by[b])
        rho = _spearman([by[a][s] for s in common], [by[b][s] for s in common])
        if rho is None:
            continue
        if a >= era_cut and b >= era_cut:
            qs.append(rho)
        elif a < era_cut and b < era_cut:
            ys_.append(rho)
        else:
            bd.append(rho)
    note_f9 = "量換手率:低≠不穩健(F9);觸發=annotate+換手成本一致性複核,非紅旗裁決"
    if qs:
        sink(h, "rank_autocorr", {"era": "quarterly"}, "spearman_median", float(statistics.median(qs)), len(qs), note_f9)
        sink(h, "rank_autocorr", {"era": "quarterly"}, "spearman_min", float(min(qs)), len(qs), note_f9)
    if ys_:
        sink(h, "rank_autocorr", {"era": "yearly"}, "spearman_median", float(statistics.median(ys_)), len(ys_),
             "年頻對描述性(間隔不同不與季頻混評)")
    if bd:
        sink(h, "rank_autocorr", {"era": "boundary"}, "spearman_median", float(statistics.median(bd)), len(bd),
             "跨節奏邊界對(2020-12→2021-03)描述性")
    print(f"  H{h} rank: 季頻 med={statistics.median(qs):+.3f}({len(qs)} 對) 年頻 {len(ys_)} 對 邊界 {len(bd)} 對")


# ── 共用:in-memory 折迴圈(鏡射 build_probability_oos_sample.emit_horizon;#12) ──
def _fold_ics(conn, h, feats, panels, cal):
    """walk-forward 逐折(train 腿 as-of 宇宙 rank label→Ridge→test 打分)→逐折 rank IC。零落帳。"""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    ics = []
    for fold in walkforward.splits(panels, h, calendar=cal):
        test_pd = fold["test"]
        ts_sids, Xte = baseline._panel_matrix(conn, test_pd, baseline._asof_stocks(conn, test_pd), feats)
        if len(ts_sids) < 5:
            continue
        fwd = label_mod.forward_returns(conn, test_pd, ts_sids, h, calendar=cal)
        keep = [i for i, s in enumerate(ts_sids) if s in fwd]
        if len(keep) < 5:
            continue
        Xte, ts_sids = Xte[keep], [ts_sids[i] for i in keep]
        Xs, ys = [], []
        for pd_ in fold["train"]:
            sids, X = baseline._panel_matrix(conn, pd_, baseline._asof_stocks(conn, pd_), feats)
            if len(sids) == 0:
                continue
            l2 = label_mod.labels(conn, pd_, sids, h, calendar=cal)
            k2 = [(i, s) for i, s in enumerate(sids) if s in l2]
            if not k2:
                continue
            Xs.append(X[[i for i, _ in k2]])
            ys.append(np.array([l2[s] for _, s in k2]))
        if not Xs:
            continue
        Xtr, ytr = np.vstack(Xs), np.concatenate(ys)
        if len(ytr) < 50:
            continue
        sc = StandardScaler().fit(Xtr)
        rdg = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr)
        pred = rdg.predict(sc.transform(Xte))
        ic = _spearman(pred, [fwd[s] for s in ts_sids])
        if ic is not None:
            ics.append(ic)
    return ics


def axis_lofo(conn, h, sink):
    """(c) 真 LOFO 全 walk-forward 重訓(§2.0 凍結口徑)。"""
    cal = label_mod.full_calendar(conn)
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date <= %s ORDER BY 1", (AS_OF,))
        panels = [r[0] for r in cur.fetchall()]
    feats = baseline.canonical_features(conn, panels)
    base_ics = _fold_ics(conn, h, feats, panels, cal)
    base_med = float(statistics.median(base_ics))
    sink(h, "lofo", {"feature": None}, "median_rank_ic", base_med, len(base_ics), "基準(28 特徵全)")
    print(f"  H{h} lofo 基準 IC med={base_med:+.4f}({len(base_ics)} 折);逐特徵剔除 {len(feats)}…", flush=True)
    for i, f in enumerate(feats):
        sub = [x for x in feats if x != f]
        ics = _fold_ics(conn, h, sub, panels, cal)
        med = float(statistics.median(ics)) if ics else None
        flag = "⚠翻負" if (med is not None and med < 0 <= base_med) else ""
        sink(h, "lofo", {"feature": f}, "median_rank_ic", med, len(ics),
             f"剔除 {f};邊際={base_med - med:+.4f}" if med is not None else f"剔除 {f};無可評折")
        print(f"    [{i + 1}/{len(feats)}] -{f}: med={med:+.4f} Δ={base_med - med:+.4f} {flag}", flush=True)


def axis_perturb(conn, h, sink):
    """(d) 特徵擾動(描述性):全樣本 production-同法模型,逐 panel score vs 擾動 score Spearman。"""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    cal = label_mod.full_calendar(conn)
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date <= %s ORDER BY 1", (AS_OF,))
        panels = [r[0] for r in cur.fetchall()]
    feats = baseline.canonical_features(conn, panels)
    Xs, ys, Xp = [], [], {}
    for pd_ in panels:
        sids, X = baseline._panel_matrix(conn, pd_, baseline._asof_stocks(conn, pd_), feats)
        if len(sids) == 0:
            continue
        Xp[pd_] = X
        l2 = label_mod.labels(conn, pd_, sids, h, calendar=cal)
        k2 = [(i, s) for i, s in enumerate(sids) if s in l2]
        if k2:
            Xs.append(X[[i for i, _ in k2]]); ys.append(np.array([l2[s] for _, s in k2]))
    sc = StandardScaler().fit(np.vstack(Xs))
    rdg = Ridge(alpha=1.0).fit(sc.transform(np.vstack(Xs)), np.concatenate(ys))
    rhos = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        for pd_, X in Xp.items():
            z = sc.transform(X)
            r = _spearman(rdg.predict(z), rdg.predict(z + rng.normal(0, PERTURB_SIGMA, z.shape)))
            if r is not None:
                rhos.append(r)
    sink(h, "perturb", {"sigma": PERTURB_SIGMA, "seeds": list(SEEDS)}, "score_spearman_median",
         float(statistics.median(rhos)), len(rhos), "描述性、不設判準(§2.2 b3)")
    sink(h, "perturb", {"sigma": PERTURB_SIGMA, "seeds": list(SEEDS)}, "score_spearman_min",
         float(min(rhos)), len(rhos), None)
    print(f"  H{h} perturb: med={statistics.median(rhos):+.3f} min={min(rhos):+.3f}({len(rhos)} panel×seed)")


def axis_subset(conn, h, sink):
    """(e) 宇宙隨機半切 IC 同號率(seeds×2 半=每 panel 6 子集)。"""
    cur = conn.cursor()
    cur.execute("SELECT panel_date, stock_id, score, fwd_ret FROM probability_oos_sample "
                "WHERE horizon=%s AND model_family=%s", (h, MODEL_FAMILY))
    by = {}
    for p, s, sc, fr in cur.fetchall():
        by.setdefault(p, []).append((float(sc), float(fr)))
    agree = tot = 0
    for p, rows in sorted(by.items()):
        full = _spearman([r[0] for r in rows], [r[1] for r in rows])
        if full is None:
            continue
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            idx = rng.permutation(len(rows))
            for half in (idx[: len(rows) // 2], idx[len(rows) // 2:]):
                sub = [rows[i] for i in half]
                ic = _spearman([r[0] for r in sub], [r[1] for r in sub])
                if ic is None:
                    continue
                tot += 1
                agree += (ic > 0) == (full > 0)
    rate = agree / tot if tot else None
    sink(h, "subset", {"seeds": list(SEEDS), "halves": 2}, "sign_agree_rate", rate, tot, None)
    print(f"  H{h} subset: 同號率={rate:.3f}({tot} 子集)")


AXES = {"calib": axis_calib, "rank": axis_rank, "lofo": axis_lofo, "perturb": axis_perturb, "subset": axis_subset}


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--axis", choices=list(AXES) + ["all"])
    ap.add_argument("--horizon", type=int, choices=HORIZONS)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry-run", dest="dry", action="store_true")
    args = ap.parse_args()
    if not args.axis:
        print(__doc__.split("執行指令矩陣:")[1])
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("SELECT policy_key, threshold, frozen FROM judgestop_threshold WHERE track='R_robust' ORDER BY 1")
            print("R 軌凍結現況:")
            for r in cur.fetchall():
                print(f"  {r[0]:<26} {r[1]}(frozen={r[2]})")
        return 0
    if not (args.run or args.dry):
        sys.exit("需 --run(落帳)或 --dry-run(算不落帳)")
    hs = [args.horizon] if args.horizon else list(HORIZONS)
    axes = list(AXES) if args.axis == "all" else [args.axis]
    with db.connect() as conn:
        cur = conn.cursor()
        _assert_prereg_frozen(cur)
        buf = []

        def sink(h, axis, cfg, metric, value, n, note=None):
            buf.append((h, axis, cfg, metric, value, n, note))
        for ax in axes:
            for h in hs:
                AXES[ax](conn, h, sink)
        if args.dry:
            print(f"(dry-run:{len(buf)} 列不落帳)")
            return 0
        for h, ax, cfg, metric, value, n, note in buf:
            _write(cur, h, ax, cfg, metric, value, n, note)
        conn.commit()
        print(f"✓ 落帳 revalidation_ledger stage='R':{len(buf)} 列")
    return 0


if __name__ == "__main__":
    sys.exit(main())
