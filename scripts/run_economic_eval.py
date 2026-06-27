#!/usr/bin/env python
"""augur 經濟價值評估 run(Track D)— 呼叫 evaluation.portfolio 回測 34 特徵生產模型之經濟指標。

🎯 這支在做什麼(白話):把 headline IC 轉成靈魂真度量(#14 經濟價值)——對 Ridge/GBDT 之 walk-forward 預測
組投組(long top 分位 + long-short),算 CAGR/Sharpe/MaxDD/Calmar、對比等權基準。預設季度段(2021+、與 h=60 tile)。

守 #8 · #12 · #14 · #15 · #28(本地零 usage)。
用法:PYTHONPATH=src python scripts/run_economic_eval.py --since 2021-01-01 --h 60 --top 0.2
"""
import argparse

from augur.core import db
from augur.evaluation import portfolio


def _row(tag, m):
    if not m:
        return f"  {tag:24s} (n<3、略)"
    return (f"  {tag:24s} 總報酬 {m['total_return']:>+7.1%} | CAGR {m['cagr']:>+6.1%} | "
            f"Sharpe {m['sharpe'] if m['sharpe'] is None else round(m['sharpe'],2):>5} | "
            f"MaxDD {m['max_drawdown']:>+6.1%} | Calmar {m['calmar'] if m['calmar'] is None else round(m['calmar'],2):>5} | "
            f"勝率 {m['hit_rate']:>4.0%}")


def main():
    ap = argparse.ArgumentParser(description="經濟價值回測(#14)")
    ap.add_argument("--since", default="2021-01-01", help="回測起(季度段、與 h tile)")
    ap.add_argument("--h", type=int, default=60)
    ap.add_argument("--top", type=float, default=0.2, help="long top 分位")
    args = ap.parse_args()

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", (args.since,))
            panels = [r[0] for r in cur.fetchall()]
        print(f"經濟回測:{len(panels)} panel（{args.since}+）× h={args.h} × top {args.top:.0%}（as-of、purged walk-forward）")
        for model in ("B2_ridge", "M1_gbdt"):
            print(f"\n══ {model} ══")
            lo = portfolio.run_backtest(conn, panels, args.h, model=model, top_frac=args.top, long_short=False)
            ls = portfolio.run_backtest(conn, panels, args.h, model=model, top_frac=args.top, long_short=True)
            meta = lo or ls
            if meta:
                print(f"  期數 {meta['n_periods']}、{meta['periods_per_year']}/yr、{meta['span']}")
            print(_row(f"long top{args.top:.0%}", lo.get("portfolio") if lo else None))
            print(_row(f"long-short top/bot", ls.get("portfolio") if ls else None))
            print(_row("等權基準(benchmark)", (lo or ls).get("benchmark") if (lo or ls) else None))
        print("\n判讀(#14):投組 Sharpe/Calmar 顯著優於等權基準、MaxDD 可控 → 模型有真經濟價值;否則 IC 未轉成可交易 alpha。")


if __name__ == "__main__":
    main()
