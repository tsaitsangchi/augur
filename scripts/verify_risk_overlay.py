#!/usr/bin/env python
"""階段 2 驗收 — 風控 overlay 套進回測,確認「風控後淨 Sharpe 仍 ≥ 基準」(部署計畫 §2c/驗收)。

🎯 這支在做什麼(白話):把 execution.risk_control 的 DD 熔斷 overlay 逐 rebalance 套在 headline 投組
   (Ridge H60/H120 LO top10%)之淨報酬序列上——每期用**已控權益之當前回檔**呼叫 `risk_control.dd_circuit`
   (#12 複用實際風控邏輯、不重造判斷),觸閾值(H60 −20%/H120 −25%,讀 risk_policy #29b)→ 該期曝險降半
   (reduce_half:0.5×投組報酬 + 0.5×現金)。比對【原始淨】vs【風控後淨】vs【基準】之 Sharpe/Calmar/MaxDD。

   **驗收判準(靈魂經濟價值 #14)**:風控後淨 Sharpe 仍 ≥ 基準 → 風控沒殺掉 edge(合格)。
   **誠實預期(#15)**:全期 MaxDD 若 < 熔斷閾值,DD 熔斷**不觸發**、風控後 == 原始(dormant 但無害);
   近期較深回檔段(如 2021 起)才可能觸——如實印觸發次數,不假裝風控「改善」了不存在的觸發。
   單標的 cap 對等權 top-decile(1/N ≤ cap)本就不觸(#25),換手為告警不改報酬——本驗收聚焦 DD 熔斷。

守 #8(DD 判斷只用已控權益歷史、純過去) · #12(複用 risk_control.dd_circuit + portfolio 回測/指標) ·
   #14(經濟價值判準) · #15(觸發與否如實、dormant 誠實揭露) · #29(個別可執行 + 指令矩陣) ·
   靈魂(風控=建議降倉、非自動下單) · 部署計畫 §2c。

執行指令矩陣:
  python scripts/verify_risk_overlay.py                       # H60、since2014 + since2021 兩期驗收
  python scripts/verify_risk_overlay.py --h 120               # H120(熔斷閾 −25%)
  python scripts/verify_risk_overlay.py --since 2021          # 只跑近期(較深回檔、較可能觸熔斷)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
import numpy as np

from augur.core import db
from augur.evaluation import portfolio
from augur.execution import risk_control


def apply_dd_overlay(net_series, conn, horizon, stress_thr=None):
    """逐期套 DD 熔斷:用已控權益歷史當前回檔 → 觸閾值該期曝險降半。回 (controlled_series, n_triggered, thr)。
    stress_thr(如 −0.10):壓力測試用,覆寫 risk_policy 閾值以強制觸發、驗機制運作(非生產閾值)。"""
    pol = risk_control.load_policies(conn, horizon)
    ddpol = pol.get("dd_circuit")
    if stress_thr is not None and ddpol is not None:
        ddpol = {**ddpol, "threshold": float(stress_thr)}      # 壓測覆寫(不動 DB、僅本次評估)
    controlled, hist, n_trig = [], [], 0
    for r in net_series:
        sig = risk_control.dd_circuit(hist, ddpol) if hist else {"triggered": False}
        exposure = 0.5 if sig.get("triggered") else 1.0     # reduce_half:半倉半現金(現金報酬 0)
        n_trig += int(bool(sig.get("triggered")))
        cr = exposure * r
        controlled.append(cr)
        hist.append(cr)
    return controlled, n_trig, (ddpol["threshold"] if ddpol else None)


def _fmt(m):
    if not m:
        return "(n<3)"
    return (f"Sharpe {m['sharpe']:>6.3f} | Calmar {(m['calmar'] if m['calmar'] is not None else 0):>5.2f} | "
            f"MaxDD {m['max_drawdown']:>+6.1%} | CAGR {(m['cagr'] or 0):>+6.1%}")


def run_one(conn, since, h, top_frac, stress_thr=None):
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date",
                    (f"{since}-01-01",))
        panels = [r[0] for r in cur.fetchall()]
    # 非重疊(H120 抽半年;H60 季度 ~no-op)——同 run_economic_eval 口徑
    need = h * 1.45 * 0.9
    pans = [panels[0]]
    for p in panels[1:]:
        if (p - pans[-1]).days >= need:
            pans.append(p)
    r = portfolio.run_backtest(conn, pans, h, model="B2_ridge", top_frac=top_frac,
                               weight="equal", cost=0.00585, asof=True)
    if not r:
        return None
    ppy = r["ppy"]
    ctrl, n_trig, thr = apply_dd_overlay(r["net_series"], conn, h, stress_thr)
    raw_m = portfolio._metrics(r["net_series"], ppy)
    ctrl_m = portfolio._metrics(ctrl, ppy)
    bench_m = portfolio._metrics(r["bench_series"], ppy)
    return {"span": r["span"], "n": r["n_periods"], "thr": thr, "n_trig": n_trig,
            "raw": raw_m, "ctrl": ctrl_m, "bench": bench_m}


def main(argv=None):
    ap = argparse.ArgumentParser(description="階段 2 驗收:風控 overlay 套回測、淨 Sharpe 仍勝基準?")
    ap.add_argument("--h", type=int, default=60)
    ap.add_argument("--top-frac", type=float, default=0.1)
    ap.add_argument("--since", default=None, help="只跑單一起點年(預設跑 2014+2021 兩期)")
    ap.add_argument("--stress-threshold", type=float, default=None, dest="stress_thr",
                    help="壓力測試:覆寫 DD 熔斷閾值以強制觸發、驗機制運作(如 -0.10;不動 DB、非生產閾值)")
    args = ap.parse_args(argv)
    sinces = [args.since] if args.since else ["2014", "2021"]
    ok_all = True
    with db.connect() as conn:
        for since in sinces:
            res = run_one(conn, since, args.h, args.top_frac, args.stress_thr)
            print("=" * 78)
            if not res:
                print(f"since{since} H{args.h}: 回測回空(panel 不足)"); continue
            print(f"風控 overlay 驗收 — H{args.h} LO top{args.top_frac:.0%} since{since}  "
                  f"({res['span']}, n={res['n']}, DD 熔斷閾={res['thr']:+.0%})")
            print("=" * 78)
            print(f"  DD 熔斷觸發次數 = {res['n_trig']}/{res['n']}  "
                  f"{'(全期未觸=風控 dormant 但無害、#15 誠實)' if res['n_trig']==0 else '(近期深回檔段觸發降倉)'}")
            print(f"  原始淨   : {_fmt(res['raw'])}")
            print(f"  風控後淨 : {_fmt(res['ctrl'])}")
            print(f"  基準     : {_fmt(res['bench'])}")
            cs = res["ctrl"]["sharpe"] if res["ctrl"] else None
            bs = res["bench"]["sharpe"] if res["bench"] else None
            ok = cs is not None and bs is not None and cs >= bs
            ok_all &= ok
            print(f"  驗收(風控後淨 Sharpe {cs:.3f} ≥ 基準 {bs:.3f}?)= {'✅ PASS' if ok else '❌ FAIL'}")
    print("\n" + ("✅ 全期驗收 PASS:風控 overlay 未殺掉 edge、淨值仍勝基準(#14)。"
                  if ok_all else "❌ 有期別未過:風控傷及 edge,須調閾值/重估(#15 不護短)。"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
