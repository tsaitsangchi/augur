#!/usr/bin/env python
"""augur Track C 衛生/精瘦驗證 — C1 穩健標準化(pe 尾)+ C2 位軸去冗餘。

🎯 這支在做什麼(白話):Track C 兩項模型層 hygiene,測對 headline 之影響、決定是否採用:
- C1:Ridge 用 RobustScaler(median/IQR、抗 pe_ratio 14500x 尾)vs 現行 StandardScaler。
- C2:位軸 range-position 三尺度高冗餘(cycle_position_252d ~ range_position_120d +0.845、~ price_to_252d_high +0.81)
  → 測 drop 冗餘者 headline 是否維持(維持即精瘦、#10)。

純讀既有 feature_values、不改特徵;as-of、多 seed。守 #11/#12/#15/#28(本地零 usage)。
執行指令矩陣:python scripts/verify_hygiene.py --seeds 3
"""
import argparse

import numpy as np

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.evaluation import baseline


def _mean(conn, panels, h, feats, seeds, robust=False):
    acc = {"B2_ridge": [], "M1_gbdt": []}
    for k in range(seeds):
        r = baseline.run_ladder(conn, panels, h, None, feats=feats, seed=42 + k, asof=True, robust=robust)
        for m in acc:
            if r[m]["mean_ic"] is not None:
                acc[m].append(r[m]["mean_ic"])
    return {m: (float(np.mean(v)) if v else float("nan")) for m, v in acc.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", ("2014-01-01",))
            panels = [r[0] for r in cur.fetchall()]
        canon = baseline.canonical_features(conn, panels)
        print(f"as-of {len(panels)} panel、canonical {len(canon)} 特徵、{args.seeds} seed")

        print(f"\n══ C1:Ridge 標準化器(StandardScaler vs RobustScaler 抗 pe 尾)══")
        for h in (20, 60):
            std = _mean(conn, panels, h, canon, args.seeds, robust=False)
            rob = _mean(conn, panels, h, canon, args.seeds, robust=True)
            print(f"  H={h:>3d} Ridge Standard {std['B2_ridge']:+.4f} → Robust {rob['B2_ridge']:+.4f}  Δ={rob['B2_ridge']-std['B2_ridge']:+.4f}")

        print(f"\n══ C2:位軸去冗餘(H60、drop 後 headline 是否維持)══")
        drops = {
            "full": canon,
            "−cycle_position_252d": [f for f in canon if f != "cycle_position_252d"],
            "−price_to_252d_high": [f for f in canon if f != "price_to_252d_high"],
            "−cycle&price(留 range_position)": [f for f in canon if f not in ("cycle_position_252d", "price_to_252d_high")],
        }
        base = None
        for name, feats in drops.items():
            r = _mean(conn, panels, 60, feats, args.seeds)
            if base is None:
                base = r
            print(f"  {name:34s} Ridge {r['B2_ridge']:+.4f}（Δ{r['B2_ridge']-base['B2_ridge']:+.4f}）GBDT {r['M1_gbdt']:+.4f}（Δ{r['M1_gbdt']-base['M1_gbdt']:+.4f}）")

        print("\n判讀:C1 robust Δ≥0 → 採用;C2 drop Δ≥0 → 去冗餘精瘦(#10)。")


if __name__ == "__main__":
    main()
