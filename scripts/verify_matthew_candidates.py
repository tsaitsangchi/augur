#!/usr/bin/env python
"""augur Track B 馬太 rank 動態複核 — 八二 P6 之 per-stock 可驗軸(支配地位慣性/變化)。

🎯 這支在做什麼(白話):八二法則「支配地位有慣性(馬太效應)」之 per-stock 量化——橫斷面 rank 之**變化動態**
(非 rank 水位,水位多與既有特徵共線)。建 2 候選、過提拔關卡:
- x_mktcap_rank_chg:市值橫斷面 rank-pct 之 ~1yr 變化(相對規模成長=馬太贏家;升 rank=愈強)
- x_mom_rank_chg:momentum_60d 橫斷面 rank-pct 之 ~1yr 變化(動能地位之加速/衰退)

註:breadth/市場 regime 屬 context(每 panel 全股同值)→ 橫斷面 rank IC 恆 0、無法驗,本支不含。
cutoff-free(rank-pct、差分皆 data-driven #9)、as-of ≤t(#8)、算不出缺列(#1)。實驗 x_ 前綴、驗後 --clear。

守 #8 · #9 · #11 · #12 · #15 · #28。
執行指令矩陣:python scripts/verify_matthew_candidates.py --seeds 3 --h 20,60 [--clear]
"""
import argparse

import numpy as np
import pandas as pd
from psycopg2.extras import execute_values

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import feature_candidate as fc
from augur.core import db
from augur.evaluation import baseline, metrics
from augur.evaluation import label as label_mod

MATTHEW = ["x_mktcap_rank_chg", "x_mom_rank_chg"]
LOOKBACK_DAYS = 365   # ~1yr 前之 panel(找最近且 ≤ t−365 者)做 rank 變化基期


def _asof_panels(cur):
    cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
    return [r[0] for r in cur.fetchall()]


def _rank_pct(cur, pd_, feat, stk):
    """某 panel 某特徵之橫斷面 percentile rank {stock: pct}(限 stk)。"""
    d = fc._panel_feature(cur, pd_, feat, stk)
    if len(d) < 5:
        return {}
    s = pd.Series(d).rank(pct=True)
    return {k: float(v) for k, v in s.items()}


def _compute(conn, panels):
    written = 0
    for i, pd_ in enumerate(panels):
        prior = next((p for p in reversed(panels[:i]) if (pd_ - p).days >= LOOKBACK_DAYS), None)
        if prior is None:
            continue
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (prior,))
            stk0 = [str(r[0]) for r in cur.fetchall()]
            cfg = [("x_mktcap_rank_chg", "market_cap_log"), ("x_mom_rank_chg", "momentum_60d")]
            rows = []
            for name, base in cfg:
                r_now = _rank_pct(cur, pd_, base, stk)
                r_old = _rank_pct(cur, prior, base, stk0)
                for s in set(r_now) & set(r_old):
                    rows.append((pd_, s, name, round(r_now[s] - r_old[s], 6)))   # rank 變化(馬太升降)
        if rows:
            with db.transaction(conn) as cur:
                execute_values(cur, f"INSERT INTO {fc.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                               f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
            written += len(rows)
    return written


def _clear(conn):
    with db.transaction(conn) as cur:
        cur.execute(f"DELETE FROM {fc.FEATURE_TABLE} WHERE feature = ANY(%s)", (MATTHEW,))
        return cur.rowcount


def _ic_series(conn, panels, h, feat, cal):
    out = {}
    for pd_ in panels:
        stk = baseline._asof_stocks(conn, pd_)
        sids, X = baseline._panel_matrix(conn, pd_, stk, [feat])
        if len(sids) < 5:
            continue
        lab = label_mod.labels(conn, pd_, sids, h, calendar=cal)
        ic = metrics.rank_ic({s: X[i, 0] for i, s in enumerate(sids)}, lab)
        if ic is not None:
            out[pd_] = ic
    return out


def _mean_ladder(conn, panels, h, feats, seeds):
    acc = {"B2_ridge": [], "M1_gbdt": []}
    for k in range(seeds):
        r = baseline.run_ladder(conn, panels, h, None, feats=feats, seed=42 + k, asof=True)
        for m in acc:
            if r[m]["mean_ic"] is not None:
                acc[m].append(r[m]["mean_ic"])
    return {m: (float(np.mean(v)) if v else float("nan")) for m, v in acc.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--clear", action="store_true")
    args = ap.parse_args()
    hs = [int(x) for x in args.h.split(",")]
    with db.connect() as conn:
        if args.clear:
            print(f"清馬太候選:{_clear(conn)} 列刪"); return
        with db.transaction(conn) as cur:
            panels = _asof_panels(cur)
        print(f"算馬太候選… 寫入 {_compute(conn, panels):,} 值")
        cal = label_mod.full_calendar(conn)
        canon = [f for f in baseline.canonical_features(conn, panels) if f not in MATTHEW]
        print(f"\n══ 1. as-of 單因子 IC + HAC（H60）══")
        print(f"{'candidate':22s} {'IC':>8s} {'iid-t':>7s} {'HAC-t':>7s} {'勝率':>5s} {'n':>3s}")
        for f in MATTHEW:
            s = metrics.summarize(_ic_series(conn, panels, 60, f, cal))
            hac = metrics.effective_t_hac(_ic_series(conn, panels, 60, f, cal))
            if s["mean_ic"] is None:
                print(f"{f:22s}  n/a"); continue
            print(f"{f:22s} {s['mean_ic']:>+8.4f} {s['effective_t']:>7.2f} {(hac if hac is not None else float('nan')):>7.2f} {s['hit_rate']:>5.2f} {s['n_panels']:>3d}")
        print(f"\n══ 2. 多 seed（{args.seeds}）多因子增量:生產 {len(canon)} vs +馬太 ══")
        for h in hs:
            base = _mean_ladder(conn, panels, h, canon, args.seeds)
            add = _mean_ladder(conn, panels, h, canon + MATTHEW, args.seeds)
            for m in ("B2_ridge", "M1_gbdt"):
                print(f"  H={h:>3d} {m:10s} 生產 {base[m]:+.4f} → +馬太 {add[m]:+.4f}  Δ={add[m]-base[m]:+.4f}")
        print("\n判讀:HAC-t |≥2| + 多 seed Δ 穩定為正 → 提拔;否則 --clear。")


if __name__ == "__main__":
    main()
