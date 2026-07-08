#!/usr/bin/env python
"""成本敏感度帶 — deflation 地板在多個成本假設下的脆弱度(#15:無 tick 資料不假裝單一「真實成本」)。

🎯 這支在做什麼(白話):headline 成本用平坦 0.585%(手續費 2×0.1425% + 證交稅 0.3% 混合率),
   **未計** bid-ask 價差 / 市場衝擊 / 借券稀缺。台股真實成本對低流動性小型股可達 1-2%+。
   我們**沒有真實 tick/價差資料**(intraday 是唯一真排除 BACKFILL_DEFERRED)→ 硬報單一「真實成本」
   數字 = 製造假兆(敵①)。故改報**敏感度帶**:地板在 cost ∈ {0.585%(現), 1.0%, 1.5%, 2.0%, 3.0%}
   下各報 net Sharpe / per-period SR / DSR / deflated 有效 Sharpe,誠實呈現地板對成本假設的脆弱度、
   不假裝精確。兩宇宙(全史齊 asof_incumbent 上界對照 + 廣宇宙 pit_broad 主誠實地板)並列。

   **效率關鍵**:cost 只作用最後一步 net = gross − turn×cost(LO 無放空 sb=0),不影響選股/訓練/turnover。
   故每 (universe,horizon) 只跑一次回測取 (gross, turn) per-period 序列,再對每個 cost 解析套用(省 N× 重跑,#28)。

   **誠實邊界**:試驗搜尋變異(N、trial SR 分散)固定在 ledger 0.585% 基準;對 headline 換成本掃描而不重跑
   全 N 試驗——重跑試驗會使 SR_0 略降(部分抵消),故此帶之 DSR 降幅為**偏嚴上界**(保守方向,#15)。

守 #12(DSR/portfolio/pit 經濟回測複用 SSOT、無 forked cost 邏輯)· #14(經濟終判前置)· #15(敏感度帶不造假兆)·
   #28(本地零 API、解析套用省重跑)· #29(個別可執行 + 指令矩陣)。

執行指令矩陣:
  python scripts/deflate_cost_sensitivity.py                                   # 兩宇宙 × H60 × 成本帶
  python scripts/deflate_cost_sensitivity.py --horizon 120                     # H120 候選之成本帶
  python scripts/deflate_cost_sensitivity.py --costs 0.00585 0.01 0.015 0.02   # 自訂成本點
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
import numpy as np

import deflate_headline_verdict as dhv          # 複用 _ppy_for(逐 horizon ppy 同口徑,#12)
import survivorship_economic_verdict as sv      # 複用 build_pit_universe + run_pit_economic(#12)
from augur.core import db
from augur.evaluation import baseline, deflation, portfolio

REF_COST = 0.00585                               # trial_ledger 基準成本(反推 turn 用)
DEFAULT_COSTS = (0.00585, 0.010, 0.015, 0.020, 0.030)


def _turn_from(gross, net, cost):
    """從 (gross, net@cost) 反推 per-period turnover:net = gross − turn×cost(LO sb=0)→ turn 精確代數。"""
    g, n = np.asarray(gross, float), np.asarray(net, float)
    return (g - n) / cost


def _band(gross, turn, ppy, costs, pp_fam, n_fam, pp_all, n_all):
    """對 gross/turn 序列掃 costs,每 cost 解析算 net → deflated_floor(N=fam 上界 / N=all 下界)。"""
    g, t = np.asarray(gross, float), np.asarray(turn, float)
    rows = []
    for c in costs:
        net_c = list(g - t * c)
        sr_pp, T, sk, ku = deflation.per_period_stats(net_c)
        sr_ann = float(sr_pp * np.sqrt(ppy)) if sr_pp is not None else None
        d_fam = deflation.deflated_floor(net_c, ppy, pp_fam, n_fam)
        d_all = deflation.deflated_floor(net_c, ppy, pp_all, n_all)
        rows.append(dict(cost=c, sr_ann=sr_ann, sr_pp=sr_pp, T=T,
                         dsr_fam=d_fam["dsr"], eff_fam=d_fam["deflated_ann"],
                         dsr_all=d_all["dsr"], eff_all=d_all["deflated_ann"]))
    return rows


def _print_band(title, span, rows, ref_cost):
    print(f"── {title}  (span {span}) ──")
    print(f"   {'cost':>7} {'net Sharpe':>11} {'perpd SR':>9} "
          f"{'DSR(N=8)':>9} {'DSR(N=16)':>10} {'defl.eff':>9}")
    for r in rows:
        tag = "  ← 現用" if abs(r["cost"] - ref_cost) < 1e-9 else ""
        dfam = f"{r['dsr_fam']*100:5.1f}%" if r["dsr_fam"] is not None else "   n/a"
        dall = f"{r['dsr_all']*100:5.1f}%" if r["dsr_all"] is not None else "   n/a"
        eff = f"{r['eff_all']:+.3f}" if r["eff_all"] is not None else " n/a"
        print(f"   {r['cost']*100:6.3f}% {r['sr_ann']:11.4f} {r['sr_pp']:9.4f} "
              f"{dfam:>9} {dall:>10} {eff:>9}{tag}")
    print()


def main(argv=None):
    ap = argparse.ArgumentParser(description="deflation 地板之成本敏感度帶(兩宇宙並列)")
    ap.add_argument("--horizon", type=int, default=60)
    ap.add_argument("--top-frac", type=float, default=0.1)
    ap.add_argument("--since", default="2014")
    ap.add_argument("--costs", type=float, nargs="+", default=list(DEFAULT_COSTS))
    ap.add_argument("--skip-pit", action="store_true", help="只跑 asof_incumbent(省 PIT 重回測)")
    args = ap.parse_args(argv)
    h, since_date = args.horizon, f"{args.since}-01-01"
    costs = sorted(set(args.costs))

    with db.connect() as conn:
        # ── 試驗集 + 逐 horizon ppy(N 機械得出;與 deflate_headline_verdict 同口徑,#12)──
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT horizon FROM trial_ledger")
            horizons = sorted(r[0] for r in cur.fetchall())
            cur.execute("SELECT horizon, metric_value FROM trial_ledger WHERE metric_name='net_sharpe'")
            trials = cur.fetchall()

        # ── asof_incumbent(全史齊)headline 回測一次取 gross/net@REF_COST ──
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            pds = [r[0] for r in cur.fetchall()]
        r_asof = portfolio.run_backtest(conn, pds, h, model="B2_ridge", top_frac=args.top_frac,
                                        weight="equal", cost=REF_COST, asof=True)
        if not r_asof:
            sys.exit(f"asof headline 回測回空(h={h} since={since_date})")
        ppy_by_h = {h: r_asof["ppy"]}
        for hh in horizons:
            if hh not in ppy_by_h:
                rr = dhv._ppy_for(conn, since_date, hh, "B2_ridge", args.top_frac, REF_COST)
                ppy_by_h[hh] = rr["ppy"] if rr else r_asof["ppy"]

        # ── 試驗 per-period SR(逐 horizon ppy 轉)+ N ──
        pp_fam = deflation.trials_per_period([(hz, s) for hz, s in trials if hz == h], ppy_by_h)
        pp_all = deflation.trials_per_period(trials, ppy_by_h)
        n_fam, n_all = len(pp_fam), len(pp_all)

        turn_asof = _turn_from(r_asof["gross_series"], r_asof["net_series"], REF_COST)
        band_asof = _band(r_asof["gross_series"], turn_asof, r_asof["ppy"], costs,
                          pp_fam, n_fam, pp_all, n_all)

        # ── pit_broad(廣宇宙、當下可算)headline 回測一次取 gross/turn@REF_COST ──
        band_pit, pit_span, pit_turn_avg = None, None, None
        if not args.skip_pit:
            feats = baseline.canonical_features(conn, pds)
            pit_map = sv.build_pit_universe(conn, pds, feats, liquidity_pct=25)
            r_pit = sv.run_pit_economic(conn, pds, h, feats, pit_map,
                                        top_frac=args.top_frac, cost=REF_COST)
            if r_pit:
                pit_span = r_pit["span"]
                pit_turn_avg = float(np.mean(r_pit["turn_series"]))
                band_pit = _band(r_pit["gross_series"], np.asarray(r_pit["turn_series"], float),
                                 r_pit["ppy"], costs, pp_fam, n_fam, pp_all, n_all)

    print("=" * 78)
    print(f"成本敏感度帶 — Ridge H{h} LO top{args.top_frac:.0%} since{args.since}  "
          f"(N: 同頻家族={n_fam} / 混頻={n_all})")
    print("=" * 78)
    print(f"avg turnover: asof={float(np.mean(turn_asof)):.3f}"
          + (f"  pit={pit_turn_avg:.3f}" if pit_turn_avg is not None else "") + "\n")
    _print_band("asof_incumbent(全史齊、穩定核心=上界對照)", r_asof["span"], band_asof, REF_COST)
    if band_pit:
        _print_band("pit_broad(廣宇宙、當下可算=主誠實地板)", pit_span, band_pit, REF_COST)
    print("=" * 78)
    print("裁決(#15 誠實):成本從 0.585%(現)升向台股真實 1-2%+,地板單調下滑;")
    print("  DSR 已 <95%(未確立),更貼近真實成本只會更低=樂觀上界被進一步夯實。")
    print("  ⚠ 試驗搜尋 N/變異固定於 ledger 0.585% 基準(重跑試驗會使 SR_0 略降=部分抵消),故此帶為偏嚴上界。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
