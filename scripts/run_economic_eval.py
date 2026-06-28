#!/usr/bin/env python
"""augur 經濟價值評估 run(Track D 深化)— 回測生產模型之經濟指標 + 交易成本/換手率(#14 誠實終測)。

🎯 這支在做什麼(白話):把 headline IC 轉成靈魂真度量(#14)——Ridge/GBDT walk-forward 預測組 long-only 投組,
算 CAGR/Sharpe/MaxDD/Calmar,並**扣交易成本(換手×來回成本)算淨值**、掃 top 分位 + 加權,對比等權基準(亦扣成本)。
答:**邊際扛得住成本嗎?最佳 top 分位/加權?**(空方 Track D 已證無效 → 專注 long-only)。

守 #8 · #12 · #14 · #15(gross/net 雙報、換手揭露)· #28(本地零 usage)。
用法:PYTHONPATH=src python scripts/run_economic_eval.py --since 2021-01-01 --h 60 --cost 0.00585
"""
import argparse

from augur.core import db
from augur.evaluation import portfolio

COST_TW = 0.00585   # 台股來回:手續費 2×0.1425% + 證交稅 0.3%(保守、未計折讓)


def _fmt(m):
    if not m:
        return "(n<3)"
    s = m["sharpe"]; c = m["calmar"]
    return (f"CAGR {m['cagr']:>+6.1%} | Sharpe {('%.2f' % s) if s is not None else ' n/a':>5} | "
            f"MaxDD {m['max_drawdown']:>+6.1%} | Calmar {('%.2f' % c) if c is not None else ' n/a':>5} | 勝率 {m['hit_rate']:>4.0%}")


def main():
    ap = argparse.ArgumentParser(description="經濟價值回測 + 交易成本(#14)")
    ap.add_argument("--since", default="2021-01-01")
    ap.add_argument("--h", type=int, default=60)
    ap.add_argument("--cost", type=float, default=COST_TW, help="來回交易成本(預設台股 0.585%%)")
    args = ap.parse_args()

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", (args.since,))
            panels = [r[0] for r in cur.fetchall()]
        print(f"經濟回測:{len(panels)} panel（{args.since}+）× h={args.h} × 來回成本 {args.cost:.3%}（as-of、purged walk-forward）")
        for model in ("B2_ridge", "M1_gbdt"):
            print(f"\n══ {model}（long-only）══")
            for top in (0.1, 0.2, 0.3):
                for wt in ("equal", "pred"):
                    r = portfolio.run_backtest(conn, panels, args.h, model=model, top_frac=top, weight=wt, cost=args.cost)
                    if not r:
                        continue
                    tag = f"top{top:.0%}/{wt}"
                    print(f"  {tag:12s} 換手 {r['avg_turnover']:>4.0%} | gross[{_fmt(r['portfolio_gross'])}]")
                    print(f"  {'':12s}            | net  [{_fmt(r['portfolio_net'])}]")
            rb = portfolio.run_backtest(conn, panels, args.h, model=model, top_frac=0.2, cost=args.cost)
            if rb:
                print(f"  {'基準(淨)':12s} 換手 {rb['bench_turnover']:>4.0%} | net  [{_fmt(rb['benchmark_net'])}]  ({rb['n_periods']}期/{rb['periods_per_year']}per-yr)")
        print("\n判讀(#14):net(扣成本)Sharpe/Calmar 仍優於基準 net → 真可交易;若成本吃掉邊際 → IC 非真 alpha。最佳 top/加權看 net。")


if __name__ == "__main__":
    main()
