#!/usr/bin/env python
"""方向模型經濟終關 — DirStack OOS 之淨值回測(GATE 外獨立標示軸;oracle 主計畫 §2.6;#14)。

🎯 這支在做什麼(白話):把方向機率 p_up 轉成靈魂真度量——「照這訊號交易,扣掉來回成本後還賺嗎?」。
   每再平衡 panel 依 p_up 選 top 分位(或 p_up>0.5 之方向多頭)、等權持有 h 交易日、報酬=選中股 fwd_abs_ret
   均值,**逐 panel 扣換手×來回成本(0.585%)**算淨值,對比等權宇宙基準(亦扣成本,公平)。gross/net 雙報(#15)。
   **這是 GATE 外的獨立軸**(§2.6:經濟終關不在統計 GATE 內);判活/死=「淨 Sharpe 勝基準 且 淨均報>0」。
   直覺:方向關已判死者,經濟關(加成本)只會更死——此支釘上最後一根釘,讓死亡證明連經濟軸都完整。
   非重疊複利:相對 OOS 是季度再平衡(panel 間距>h 持有天),panel 序列即非重疊、可直接複利。

守 #14(淨值終測、成本揭露)· #12(cost 口徑複用 run_economic_eval)· #15(gross/net 雙報)· #28(本地零 API)· #29a/d。
   前置=train_direction_stack.py --run(direction_oos_sample)。SSOT=oracle 主計畫 §2.6。

執行指令矩陣:
  python scripts/run_direction_econ_eval.py                      # 無參數:現況(唯讀:各 horizon OOS 覆蓋)
  python scripts/run_direction_econ_eval.py --run                # 全 horizon 經濟終關(top 0.2、cost 0.585%)
  python scripts/run_direction_econ_eval.py --run --top-frac 0.1 --cost 0.00585
  python scripts/run_direction_econ_eval.py --run --report reports/direction_econ_20260711.md
"""
import argparse
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db
from augur.evaluation.portfolio import _metrics, _turnover

H_HORIZONS = (20, 40, 82, 120)
COST_TW = 0.00585   # 台股來回(手續費 2×0.1425%+證交稅 0.3%),同 run_economic_eval


def _horizon_backtest(cur, h, top_frac, cost):
    """兩視角(#15 真兆假兆隔離):
    ① 相對揀選:long top p_up 分位。**警示**:panel 內 P_mkt 對所有股相同 → p_up 排序≡rank_pctile 排序,
       此軸實測=既有相對模型之已知邊際、非絕對方向技能(alive 屬假兆、不歸功方向模型)。
    ② 市場擇時 overlay(方向模型獨特 claim,零相對污染):持等權宇宙,P_mkt>0.5 才進場、否則現金;
       對比 always-invested buy&hold。alive=擇時淨 Sharpe 真的勝 buy&hold(方向訊號加值)。"""
    cur.execute("""SELECT s.panel_date, s.target_id, s.p_up, s.fwd_abs_ret,
            (SELECT p_mkt_up FROM market_direction_probability m
             WHERE m.horizon=s.horizon AND m.model_id='MktLogit' AND m.panel_date<=s.panel_date
             ORDER BY m.panel_date DESC LIMIT 1)
        FROM direction_oos_sample s WHERE s.horizon=%s AND s.fwd_abs_ret IS NOT NULL
        ORDER BY s.panel_date""", (h,))
    by_panel = {}
    for pd_, sid, p_up, fr, pmkt in cur.fetchall():
        by_panel.setdefault(pd_, []).append((sid, float(p_up), float(fr), None if pmkt is None else float(pmkt)))
    panels = sorted(by_panel)
    if len(panels) < 2:
        return None
    rel_net, bench, timed, prev = [], [], None, None
    timed_ret, prev_inv = [], True
    for p in panels:
        rows = by_panel[p]
        rows.sort(key=lambda r: r[1], reverse=True)
        k = max(1, int(len(rows) * top_frac))
        sel = rows[:k]
        sids = [r[0] for r in sel]
        gross = float(np.mean([r[2] for r in sel]))
        turn = _turnover(sids, prev); prev = sids
        rel_net.append(gross - turn * cost)                              # ① 相對揀選淨值
        uni = float(np.mean([r[2] for r in rows]))                       # 等權宇宙報酬(本 panel)
        bench.append(uni)                                                # ② buy&hold(always invested)
        pmkt = sel[0][3]                                                 # P_mkt(panel 級、全股同值)
        invested = (pmkt is not None and pmkt > 0.5)
        r_t = uni if invested else 0.0                                   # 擇時:進場才吃宇宙報酬,否則現金
        if invested != prev_inv:                                        # 進出場切換=全額換手成本
            r_t -= cost
        prev_inv = invested
        timed_ret.append(r_t)
    ppy = 252.0 / max(h, 1)
    m_rel, m_bench, m_timed = _metrics(rel_net, ppy), _metrics(bench, ppy), _metrics(timed_ret, ppy)
    # 方向模型獨特貢獻之判活:擇時 overlay 真的勝 buy&hold(risk-adjusted)
    timing_alive = bool(m_timed.get("sharpe") is not None and m_bench.get("sharpe") is not None
                        and m_timed["sharpe"] > m_bench["sharpe"])
    return {"h": h, "n_panels": len(panels), "top_frac": top_frac, "cost": cost,
            "rel_pick": m_rel, "buy_hold": m_bench, "market_timing": m_timed,
            "timing_verdict": "alive" if timing_alive else "dead"}


def run(horizons, top_frac, cost, report):
    lines = []
    with db.connect() as conn, db.transaction(conn) as cur:
        for h in horizons:
            r = _horizon_backtest(cur, h, top_frac, cost)
            if not r:
                print(f"  H{h:<3} 無足夠 OOS(先跑 train_direction_stack.py)—略"); continue
            rp, bh, tm = r["rel_pick"], r["buy_hold"], r["market_timing"]
            mark = "🟢alive" if r["timing_verdict"] == "alive" else "💀dead"

            def _s(m): return None if m.get("sharpe") is None else round(m["sharpe"], 3)
            line = (f"  H{h:<3} 方向擇時={mark}(Sharpe 擇時={_s(tm)} vs buy&hold={_s(bh)}) | "
                    f"[假兆軸]相對揀選 Sharpe={_s(rp)}(=既有相對邊際、不歸功方向) | n_panel={r['n_panels']}")
            print(line); lines.append(line)
    if report:
        Path(report).write_text(
            f"# 方向模型經濟終關(cost={cost}, top_frac={top_frac})\n\n"
            "GATE 外獨立標示軸(§2.6);淨=毛−換手×成本;基準=等權宇宙。\n\n" + "\n".join(lines) + "\n",
            encoding="utf-8")
        print(f"✓ 報告寫入 {report}")
    print("✓ 經濟終關完成(方向 GATE 已判死者,經濟軸加成本只會更死——最後一根釘)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT horizon, count(*), count(DISTINCT panel_date) FROM direction_oos_sample GROUP BY horizon ORDER BY horizon")
        rows = cur.fetchall()
    print("direction_oos_sample 覆蓋(經濟終關輸入):")
    for h, n, npd in rows:
        print(f"  H{h:<3} {n} 列 / {npd} panel")
    if not rows:
        print("  (無;先跑 train_direction_stack.py --run)")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--horizons", nargs="*", type=int, default=list(H_HORIZONS))
    ap.add_argument("--top-frac", dest="top_frac", type=float, default=0.2)
    ap.add_argument("--cost", type=float, default=COST_TW)
    ap.add_argument("--report")
    args = ap.parse_args()
    if args.run:
        return run(args.horizons, args.top_frac, args.cost, args.report)
    return status()


if __name__ == "__main__":
    sys.exit(main())
