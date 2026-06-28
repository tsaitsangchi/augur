#!/usr/bin/env python
"""augur horizon × 宇宙掃描 — 換 horizon/宇宙是否解鎖不同 alpha 結構(特徵飽和後之逃脫方向)。

🎯 這支在做什麼(白話):特徵層五輪飽和;換「問題」可能解鎖不同 alpha:
- **horizon**:模型 IC 於 H=5/20/60/120/252(as-of core)——哪個持有期預測結構最強。
- **宇宙**:關鍵特徵單因子 rank IC 於 core(848)vs 擴大(per-panel 全特徵齊備股、全 roster)——alpha 是否推廣到更多名。

口徑 reuse baseline/label/metrics(#12);as-of。守 #8 · #12 · #15 · #28(本地零 usage)。
用法:PYTHONPATH=src python scripts/run_horizon_universe_scan.py --mode both --seeds 3
"""
import argparse

import numpy as np

from augur.core import db
from augur.evaluation import baseline, metrics
from augur.evaluation import label as label_mod

KEY_FEATS = ["pb_ratio", "cycle_position_252d", "inst_cumflow_position_120d", "volume_gini_60d", "momentum_60d"]


def _feature_complete(conn, panel, feats):
    """某 panel 全特徵齊備之股(擴大宇宙、不限 core_gate)。"""
    with db.transaction(conn) as cur:
        cur.execute(f"SELECT stock_id FROM feature_values WHERE panel_date=%s AND feature = ANY(%s) "
                    f"GROUP BY stock_id HAVING count(DISTINCT feature) = %s", (panel, feats, len(feats)))
        return [str(r[0]) for r in cur.fetchall()]


def _sf_ic(conn, panels, h, feat, cal, universe):
    """單因子 rank IC 序列(universe: 'core'=as-of core / 'expanded'=全特徵齊備)。"""
    out = {}
    for pd_ in panels:
        stk = baseline._asof_stocks(conn, pd_) if universe == "core" else _feature_complete(conn, pd_, [feat])
        sids, X = baseline._panel_matrix(conn, pd_, stk, [feat])
        if len(sids) < 10:
            continue
        lab = label_mod.labels(conn, pd_, sids, h, calendar=cal)
        ic = metrics.rank_ic({s: X[i, 0] for i, s in enumerate(sids)}, lab)
        if ic is not None:
            out[pd_] = ic
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="both", choices=["horizon", "universe", "both"])
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", ("2014-01-01",))
            panels = [r[0] for r in cur.fetchall()]
        cal = label_mod.full_calendar(conn)

        if args.mode in ("horizon", "both"):
            print(f"══ horizon 掃描(as-of core、{args.seeds} seed、模型 mean IC)══")
            print(f"{'H':>5s} {'B2_ridge':>10s} {'M1_gbdt':>10s} {'B1_mom':>10s}")
            for h in (5, 20, 60, 120, 252):
                acc = {"B2_ridge": [], "M1_gbdt": [], "B1_momentum": []}
                for k in range(args.seeds):
                    r = baseline.run_ladder(conn, panels, h, None, seed=42 + k, asof=True)
                    for m in acc:
                        if r[m]["mean_ic"] is not None:
                            acc[m].append(r[m]["mean_ic"])
                f = lambda m: (np.mean(acc[m]) if acc[m] else float("nan"))
                print(f"{h:>5d} {f('B2_ridge'):>+10.4f} {f('M1_gbdt'):>+10.4f} {f('B1_momentum'):>+10.4f}")

        if args.mode in ("universe", "both"):
            print(f"\n══ 宇宙掃描(H60、關鍵特徵單因子 rank IC:core vs 擴大)══")
            print(f"{'feature':28s} {'core IC':>9s} {'core n':>6s} {'expand IC':>10s} {'expand n':>8s}")
            for feat in KEY_FEATS:
                c = metrics.summarize(_sf_ic(conn, panels, 60, feat, cal, "core"))
                e = metrics.summarize(_sf_ic(conn, panels, 60, feat, cal, "expanded"))
                if c["mean_ic"] is None or e["mean_ic"] is None:
                    print(f"{feat:28s}  n/a"); continue
                # 擴大宇宙平均股數
                print(f"{feat:28s} {c['mean_ic']:>+9.4f} {c['n_panels']:>6d} {e['mean_ic']:>+10.4f} {e['n_panels']:>8d}")
        print("\n判讀:horizon——IC 最強之 H 為較佳持有期;宇宙——擴大 IC 維持→alpha 推廣(可交易更多名)、衰退→core-gate 必要。")


if __name__ == "__main__":
    main()
