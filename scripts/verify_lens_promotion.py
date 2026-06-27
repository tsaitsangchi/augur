#!/usr/bin/env python
"""augur 鏡頭新特徵提拔複核 — 對 holistic 五鏡存活之八二/康波新特徵,過第4道提拔關卡。

🎯 這支在做什麼(白話):holistic 五鏡篩出強勢存活之新特徵(量能集中/流相位/價格相位),但單因子顯著
≠ 可入生產。本支過方法論 §四第4道關卡:
1. **去相關 Eff-t**:每存活特徵 as-of IC 序列 iid vs Newey-West HAC(禁裸 iid、解 G8)
2. **多 seed 多因子增量**:生產基準 vs +存活集,run_ladder ≥3 seed Ridge/GBDT,看 IC 真增量
3. **剪枝確認**:同時測剪 gov_bank_net_buy_60d + volatility_20d(五鏡 LOO 顯示有害/共線)是否維持/改善

如此一次答「新特徵該不該進、舊特徵該不該剪」。實驗讀既有 feature_values、不寫不刪。

守 #8(as-of)· #11(五鏡)· #12(SSOT helper)· #15(雙口徑 t、誠實)· #28(本地、零 usage)。
用法:PYTHONPATH=src python scripts/verify_lens_promotion.py --seeds 3 --h 20,60
"""
import argparse

import numpy as np

from augur.core import db
from augur.evaluation import baseline, metrics
from augur.evaluation import label as label_mod

# 八二/康波全 25 新特徵(從生產基準排除,以乾淨比較)
NEW_ALL = [
    "holding_gini", "holding_hhi", "holding_entropy", "holding_owner_skew", "holding_hhi_chg_60d",
    "inst_flow_hhi_20d", "inst_flow_max_share_20d", "volume_gini_20d", "volume_gini_60d",
    "volume_max_share_20d", "volume_max_share_60d", "return_skew_60d", "return_kurt_60d",
    "return_gini_60d", "return_max_share_60d",
    "range_position_60d", "range_position_120d", "days_since_high_252d", "days_since_low_252d",
    "max_drawdown_252d", "momentum_accel_60d", "momentum_resonance", "vol_term_structure",
    "inst_cumflow_position_60d", "inst_cumflow_position_120d",
]
# holistic 五鏡強勢存活者(顯著 IC + Eff-t≥2 或 LOO 必要)
SURVIVORS = [
    "inst_cumflow_position_120d", "inst_cumflow_position_60d",       # 康波 C4 流相位
    "volume_gini_60d", "volume_gini_20d", "volume_max_share_60d", "volume_max_share_20d",  # 八二 P3 量能集中
    "range_position_120d", "days_since_high_252d",                   # 康波 C2 價格相位
]
PRUNE = ["gov_bank_net_buy_60d", "volatility_20d"]                   # 五鏡 LOO 害/共線 → 剪


def _asof_panels(cur):
    cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
    return [r[0] for r in cur.fetchall()]


def _asof_ic_series(conn, panels, h, feat, cal):
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
    """多 seed run_ladder as-of → {model: mean over seeds}。"""
    acc = {"B2_ridge": [], "M1_gbdt": []}
    for k in range(seeds):
        r = baseline.run_ladder(conn, panels, h, None, feats=feats, seed=42 + k, asof=True)
        for m in acc:
            if r[m]["mean_ic"] is not None:
                acc[m].append(r[m]["mean_ic"])
    return {m: (float(np.mean(v)) if v else float("nan")) for m, v in acc.items()}


def main():
    ap = argparse.ArgumentParser(description="鏡頭新特徵提拔複核(as-of + HAC + 多 seed)")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--h", default="20,60")
    args = ap.parse_args()
    hs = [int(x) for x in args.h.split(",")]

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            panels = _asof_panels(cur)
        cal = label_mod.full_calendar(conn)
        canonical = baseline.canonical_features(conn, panels)
        prod_full = [f for f in canonical if f not in NEW_ALL]        # 原生產集(排新特徵)
        prod_pruned = [f for f in prod_full if f not in PRUNE]        # 剪枝後
        promoted = prod_pruned + [f for f in SURVIVORS if f in canonical]
        print(f"as-of {len(panels)} panel；生產 {len(prod_full)} → 剪枝 {len(prod_pruned)} → +存活 {len(promoted)}")

        print(f"\n══ 1. 存活特徵 as-of 去相關 Eff-t（iid vs HAC、H60）══")
        print(f"{'feature':28s} {'IC':>8s} {'iid-t':>7s} {'HAC-t':>7s} {'勝率':>5s} {'n':>3s}")
        for f in SURVIVORS:
            ser = _asof_ic_series(conn, panels, 60, f, cal)
            s = metrics.summarize(ser)
            hac = metrics.effective_t_hac(ser)
            if s["mean_ic"] is None:
                print(f"{f:28s}   n/a"); continue
            print(f"{f:28s} {s['mean_ic']:>+8.4f} {s['effective_t']:>7.2f} "
                  f"{(hac if hac is not None else float('nan')):>7.2f} {s['hit_rate']:>5.2f} {s['n_panels']:>3d}")

        print(f"\n══ 2. 多 seed（{args.seeds}）多因子增量:生產 vs 剪枝 vs 剪枝+存活 ══")
        for h in hs:
            base = _mean_ladder(conn, panels, h, prod_full, args.seeds)
            pruned = _mean_ladder(conn, panels, h, prod_pruned, args.seeds)
            promo = _mean_ladder(conn, panels, h, promoted, args.seeds)
            print(f"\n  H={h}:")
            for m in ("B2_ridge", "M1_gbdt"):
                print(f"    {m:10s} 生產 {base[m]:+.4f} → 剪枝 {pruned[m]:+.4f}（Δ{pruned[m]-base[m]:+.4f}）"
                      f" → +存活 {promo[m]:+.4f}（Δ{promo[m]-pruned[m]:+.4f}、總Δ{promo[m]-base[m]:+.4f}）")

        print("\n判讀:存活 HAC-t 仍 |≥2| + 剪枝 Δ≥0 + 加存活總 Δ 穩定為正 → 提拔存活、剪 PRUNE;否則保留現狀。")


if __name__ == "__main__":
    main()
