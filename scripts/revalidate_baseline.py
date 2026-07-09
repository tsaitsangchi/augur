#!/usr/bin/env python
"""再驗證 baseline 定錨(harness P0)— 凍結兩宇宙 deflated 地板為軌B 衰減比較基準。

🎯 這支在做什麼(白話):把「edge 建置時之 deflated 地板」凍結進 revalidation_baseline——
   兩宇宙並存(用戶拍板):**asof_incumbent**(全史齊、predict_asof 實際部署交易口徑=軌B 操作 baseline)
   + **pit_broad**(廣宇宙、incumbency 修正後之誠實地板錨,net~1.00)。逐宇宙記 net_sharpe/bench/超額/
   HAC-t/DSR/deflated 有效 Sharpe。DSR 走 #12 共用 helper(`evaluation.deflation`)、N 由 trial_ledger 機械。

   **凍結語義(#15)**:baseline 一旦定錨即為軌B 之固定參照(edge 是否從此惡化);冪等(ON CONFLICT 覆寫=
   明示 re-freeze,換部署模型/宇宙判準時才做)。純本地零 API、不進預測管線。

守 #8(as-of/清算 label 口徑同 SSOT)· #12(deflation helper + survivorship/portfolio 複用、不重造)·
   #14 · #15(兩宇宙誠實、DSR 屬軌A 標註)· #28 · #29a。SSOT=部署計畫 harness P0。

執行指令矩陣:
  python scripts/revalidate_baseline.py            # 凍結 ridge_H60_LO 兩宇宙錨(冪等覆寫)
  python scripts/revalidate_baseline.py --dry-run  # 只算+印、不寫 revalidation_baseline
  python scripts/revalidate_baseline.py --cell ridge_H120_LO --horizon 120 --role candidate  # 凍結 H120 追蹤候選(非部署)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
import numpy as np

from augur.core import db
from augur.evaluation import baseline, deflation, portfolio
from deflate_headline_verdict import _nonoverlap, _ppy_for
from survivorship_economic_verdict import build_pit_universe, run_pit_economic

COST = 0.00585
TOP = 0.1
H = 60
SINCE = "2014-01-01"
CELL = "ridge_H60_LO"


def _trials_per_period(conn, pds):
    """trial_ledger 試驗集 → per-period(逐 horizon 各自 ppy;#12 helper)。回 (trials_pp, n_trials)。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT horizon FROM trial_ledger")
        hs = sorted(r[0] for r in cur.fetchall())
        cur.execute("SELECT horizon, metric_value FROM trial_ledger WHERE metric_name='net_sharpe'")
        trials = cur.fetchall()
    ppy_by_h = {}
    for h in hs:
        r = _ppy_for(conn, SINCE, h, "B2_ridge", TOP, COST)
        ppy_by_h[h] = r["ppy"] if r else None
    pp = deflation.trials_per_period(trials, ppy_by_h)
    return pp, len(pp)


def _deploy_hac_t(conn):
    """部署 cell 之 as-of IC HAC-t(最新 as_of;reuse revalidation_ledger,#12,無則 None)。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT hac_t FROM revalidation_ledger WHERE stage='B' AND horizon=%s "
                    "AND model='B2_ridge' AND config='asof_ic' AND hac_t IS NOT NULL "
                    "ORDER BY as_of_date DESC LIMIT 1", (H,))
        r = cur.fetchone()
    return float(r[0]) if r else None


def freeze(dry_run=False, role="deploy"):
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            pds_all = [r[0] for r in cur.fetchall()]
        pds = _nonoverlap(pds_all, H)   # 非重疊再平衡(同 Stage D/deflate 口徑;H60 spacing<panel gap→全保留不變、H120 隔期取→ baseline 與 ledger/eval 一致,#12/#15 命門:原僅 run_backtest splits=重疊窗、H120 灌水)
        feats = baseline.canonical_features(conn, pds_all)
        trials_pp, n_trials = _trials_per_period(conn, pds)
        hac = _deploy_hac_t(conn)

        # ── 全史齊部署(asof_incumbent):run_backtest + deflation helper ──
        rd = portfolio.run_backtest(conn, pds, H, model="B2_ridge", top_frac=TOP,
                                    weight="equal", cost=COST, asof=True)
        d_defl = deflation.deflated_floor(rd["net_series"], rd["ppy"], trials_pp, n_trials)
        d_net, d_bench = rd["portfolio_net"]["sharpe"], rd["benchmark_net"]["sharpe"]

        # ── 廣宇宙誠實錨(pit_broad):survivorship PIT + 清算 label + deflation helper ──
        pit_map = build_pit_universe(conn, pds, feats, liquidity_pct=25)
        rp = run_pit_economic(conn, pds, H, feats, pit_map, top_frac=TOP)
        p_defl = deflation.deflated_floor(rp["net_series"], rp["ppy"], trials_pp, n_trials)
        p_net, p_bench = rp["net"]["sharpe"], rp["bench"]["sharpe"]

        cand = "【追蹤候選·非部署(in_portfolio=0)·軌B 待新資料追衰減】" if role == "candidate" else ""
        asof_src = ("augur_prediction_h120_deployment_eval_20260709.md" if role == "candidate"
                    else "augur_prediction_deflation_verdict_20260708.md")
        rows = [
            ("asof_incumbent", d_net, d_bench, hac, d_defl, rd["portfolio_net"]["n"], asof_src,
             cand + "全史齊口徑(predict_asof 交易);軌B 操作 baseline"),
            ("pit_broad", p_net, p_bench, None, p_defl, rp["n"],
             "augur_prediction_survivorship_economic_verdict_20260708.md",
             cand + "廣宇宙 incumbency 修正誠實錨(−16.5%);HAC-t 另口徑不填"),
        ]
        print("=" * 78)
        print(f"再驗證 baseline 定錨 — cell={CELL}  as_of={pds[-1]}  N={n_trials}(trial_ledger 機械)")
        print("=" * 78)
        for uni, net, bench, ht, defl, n, src, note in rows:
            print(f"\n[{uni}]  net_sharpe={net:.4f}  bench={bench:.4f}  超額={net-bench:+.4f}  "
                  f"HAC-t={ht if ht is not None else 'n/a'}  n={n}")
            print(f"   DSR={defl['dsr']:.4f}({defl['dsr']*100:.1f}%,軌A 標註)  "
                  f"deflated 年化有效 Sharpe≈{defl['deflated_ann']:.3f}  ({note})")

        if dry_run:
            print("\n[dry-run] 不寫 revalidation_baseline。")
            return 0
        with db.transaction(conn) as cur:
            for uni, net, bench, ht, defl, n, src, note in rows:
                cur.execute(
                    "INSERT INTO revalidation_baseline "
                    "(cell, universe, as_of_date, net_sharpe, bench_sharpe, net_excess, hac_t, dsr, deflated_ann, n_periods, source_ref, note) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                    "ON CONFLICT (cell, universe) DO UPDATE SET "
                    "frozen_at=now(), as_of_date=EXCLUDED.as_of_date, net_sharpe=EXCLUDED.net_sharpe, "
                    "bench_sharpe=EXCLUDED.bench_sharpe, net_excess=EXCLUDED.net_excess, hac_t=EXCLUDED.hac_t, "
                    "dsr=EXCLUDED.dsr, deflated_ann=EXCLUDED.deflated_ann, n_periods=EXCLUDED.n_periods, "
                    "source_ref=EXCLUDED.source_ref, note=EXCLUDED.note",
                    (CELL, uni, pds[-1], net, bench, net - bench, ht,
                     defl["dsr"], defl["deflated_ann"], n, src, note))
        print(f"\n✓ 凍結 revalidation_baseline:{len(rows)} 列(cell={CELL})。")
    return 0


def main(argv=None):
    global H, CELL           # helper 讀 module global;由 CLI override(路徑單一住所、不散參數穿多層)
    ap = argparse.ArgumentParser(description="再驗證 baseline 定錨(P0、兩宇宙;--horizon+--cell 凍結追蹤候選)")
    ap.add_argument("--dry-run", action="store_true", help="只算+印、不寫 revalidation_baseline")
    ap.add_argument("--cell", default=CELL, help="baseline cell(如 ridge_H120_LO 凍結 H120 追蹤候選)")
    ap.add_argument("--horizon", type=int, default=H, help="horizon(cell 對映;預設 60=部署)")
    ap.add_argument("--role", default="deploy", choices=["deploy", "candidate"],
                    help="deploy=部署主投組軌B操作 baseline;candidate=追蹤候選(非部署、in_portfolio=0、軌B 待新資料追衰減)")
    args = ap.parse_args(argv)
    H, CELL = args.horizon, args.cell
    return freeze(dry_run=args.dry_run, role=args.role)


if __name__ == "__main__":
    sys.exit(main())
