#!/usr/bin/env python
"""augur 跨鏡交互特徵複核(Track A)— 3 個量×形/位交互候選,計算 + 過提拔關卡。

🎯 這支在做什麼(白話):lens-correlation 深析指出之跨鏡交互前沿,做成 3 候選(全用既有特徵衍生、as-of 安全),
過第4道提拔關卡(as-of HAC + 多 seed 多因子增量):
- A1 x_gini_resid_size:volume_gini_60d 對 market_cap_log 橫斷面 OLS 殘差(剔 size 之異常量能集中、量×形)
- A2 x_flow_phase_divergence:z(inst_cumflow_position_120d) − z(institutional_net_buy_ratio_20d)(吸籌相位 vs 近期流向背離、位×量)
- A3 x_price_flow_divergence:range_position_120d − inst_cumflow_position_120d(價相位 vs 流相位背離、位×位跨域)

cutoff-free(#9:OLS 係數/z/相位差皆 data-driven)、橫斷面同 panel ≤t(#8)、算不出缺列(#1)。實驗寫 x_ 前綴、驗後可清。

守 #8 · #9 · #11 · #12 · #15 · #28(本地零 usage)。
執行指令矩陣:python scripts/verify_interaction_candidates.py --seeds 3 --h 20,60 [--clear]
"""
import argparse

import numpy as np
from psycopg2.extras import execute_values

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import feature_candidate as fc
from augur.core import db
from augur.evaluation import baseline, metrics
from augur.evaluation import label as label_mod

INTERACTIONS = ["x_gini_resid_size", "x_flow_phase_divergence", "x_price_flow_divergence"]


def _asof_panels(cur):
    cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
    return [r[0] for r in cur.fetchall()]


def _compute(conn, panels):
    fc.ensure_candidate_table(conn)
    written = 0
    for pd_ in panels:
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            gini = fc._panel_feature(cur, pd_, "volume_gini_60d", stk)
            mcap = fc._panel_feature(cur, pd_, "market_cap_log", stk)
            cumf = fc._panel_feature(cur, pd_, "inst_cumflow_position_120d", stk)
            inet = fc._panel_feature(cur, pd_, "institutional_net_buy_ratio_20d", stk)
            rpos = fc._panel_feature(cur, pd_, "range_position_120d", stk)
        rows = []
        # A1:量能集中對 size 之 OLS 殘差(剔規模後異常集中)
        common = list(set(gini) & set(mcap))
        if len(common) >= 10:
            X = np.array([mcap[s] for s in common]); Y = np.array([gini[s] for s in common])
            if np.isfinite(X).all() and X.std() > 0:
                b1, b0 = np.polyfit(X, Y, 1)
                for s in common:
                    rows.append((pd_, s, "x_gini_resid_size", round(float(Y[common.index(s)] - (b0 + b1 * mcap[s])), 6)))
        # A2:流相位 vs 近期流向背離(橫斷面 z 差)
        zc, zn = fc._zscore(cumf), fc._zscore(inet)
        for s in set(zc) & set(zn):
            rows.append((pd_, s, "x_flow_phase_divergence", round(zc[s] - zn[s], 6)))
        # A3:價相位 vs 流相位背離(兩 0-1 相位直接差)
        for s in set(rpos) & set(cumf):
            rows.append((pd_, s, "x_price_flow_divergence", round(rpos[s] - cumf[s], 6)))
        if rows:
            with db.transaction(conn) as cur:
                execute_values(cur, f"INSERT INTO {fc.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                               f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
            written += len(rows)
    return written


def _clear(conn):
    with db.transaction(conn) as cur:
        cur.execute(f"DELETE FROM {fc.FEATURE_TABLE} WHERE feature = ANY(%s)", (INTERACTIONS,))
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
            print(f"清交互候選:{_clear(conn)} 列刪"); return
        with db.transaction(conn) as cur:
            panels = _asof_panels(cur)
        print(f"算交互候選… 寫入 {_compute(conn, panels):,} 值（{len(panels)} panel）")
        cal = label_mod.full_calendar(conn)
        canon = baseline.canonical_features(conn, panels)

        print(f"\n══ 1. as-of 單因子 IC + 去相關 HAC（H60）══")
        print(f"{'interaction':26s} {'IC':>8s} {'iid-t':>7s} {'HAC-t':>7s} {'勝率':>5s} {'n':>3s}")
        for f in INTERACTIONS:
            s = metrics.summarize(_ic_series(conn, panels, 60, f, cal))
            hac = metrics.effective_t_hac(_ic_series(conn, panels, 60, f, cal))
            if s["mean_ic"] is None:
                print(f"{f:26s}  n/a"); continue
            print(f"{f:26s} {s['mean_ic']:>+8.4f} {s['effective_t']:>7.2f} {(hac if hac is not None else float('nan')):>7.2f} {s['hit_rate']:>5.2f} {s['n_panels']:>3d}")

        base_feats = [f for f in canon if f not in INTERACTIONS]   # 排除交互(canonical intersection 已自動納入)
        print(f"\n══ 2. 多 seed（{args.seeds}）多因子增量:生產 {len(base_feats)}(含交互之成分)vs +交互 ══")
        for h in hs:
            base = _mean_ladder(conn, panels, h, base_feats, args.seeds)
            add = _mean_ladder(conn, panels, h, base_feats + INTERACTIONS, args.seeds)
            for m in ("B2_ridge", "M1_gbdt"):
                print(f"  H={h:>3d} {m:10s} 生產 {base[m]:+.4f} → +交互 {add[m]:+.4f}  Δ={add[m]-base[m]:+.4f}")
        print("\n判讀:HAC-t |≥2| + 多 seed Δ 穩定為正 → 提拔;否則 --clear。")


if __name__ == "__main__":
    main()
