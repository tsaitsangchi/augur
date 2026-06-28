#!/usr/bin/env python
"""augur regime-conditional 投組 — 驗過之 C1 regime 訊號套到 top10% 投組(部位調節)。

🎯 這支在做什麼(白話):regime 擇時已於 23 年 TAIEX 驗過(lead_nt_rising:MaxDD −54%→−15%、Sharpe 0.75→1.04)。
本支把它套到生產 top10%/equal 投組:每季再平衡時查 C1 regime(發布日 lag),regime-on 持投組、off 持現金,
比 static(滿倉)之淨 Sharpe/MaxDD/Calmar。誠實:投組僅 18 季、regime 訊號本身才是長樣本驗過者。

守 #8(發布日 lag)· #14(經濟指標)· #15(對比 static、揭露在市%)· #28(本地零 usage)。
用法:PYTHONPATH=src python scripts/verify_regime_portfolio.py --lag 2 --cost 0.00585
"""
import argparse

import numpy as np
import pandas as pd

from augur.core import db
from augur.evaluation import portfolio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lag", type=int, default=2)
    ap.add_argument("--cost", type=float, default=0.00585)
    ap.add_argument("--since", default="2021-01-01")
    args = ap.parse_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", (args.since,))
            panels = [r[0] for r in cur.fetchall()]
            cur.execute('SELECT date, leading_notrend FROM "TaiwanBusinessIndicator" ORDER BY date')
            c1 = pd.DataFrame(cur.fetchall(), columns=["date", "lead_nt"]).astype({"lead_nt": float})
        # top10%/equal 生產投組(Ridge、含成本)→ 逐季淨報酬
        r = portfolio.run_backtest(conn, panels, 60, model="B2_ridge", top_frac=0.1, weight="equal", cost=args.cost)
        if not r:
            print("投組 n<3"); return
        dates, net, ppy = r["dates"], np.array(r["net_series"], float), r["ppy"]

        # C1 regime:lead_nt_rising(3 月動能升),發布日 lag
        c1["m"] = pd.to_datetime(c1["date"]).dt.to_period("M")
        c1 = c1.set_index("m").sort_index()
        rising = (c1["lead_nt"] > c1["lead_nt"].shift(3)).astype(float)
        regime = []
        for d in dates:
            cutoff = pd.Period(pd.Timestamp(d), "M") - args.lag       # 發布日 lag:只用 ≤ panel月−lag 之 C1
            avail = rising[rising.index <= cutoff]
            regime.append(float(avail.iloc[-1]) if len(avail) else 1.0)
        regime = np.array(regime)
        reg_net = net * regime                                        # regime-off → 現金(0)

        m_static = portfolio._metrics(net, ppy)
        m_regime = portfolio._metrics(reg_net, ppy)
        print(f"regime-conditional 投組:{len(dates)} 季（{r['span']}）、lag {args.lag}月、在市 {regime.mean():.0%}")
        print(f"\n{'策略':22s} {'CAGR':>7s} {'Sharpe':>7s} {'MaxDD':>7s} {'Calmar':>7s}")

        def _row(tag, m):
            return f"{tag:22s} {m['cagr']:>+7.1%} {m['sharpe']:>7.2f} {m['max_drawdown']:>+7.1%} {m['calmar']:>7.2f}" if m else f"{tag}: n/a"
        print(_row("top10% static(滿倉)", m_static))
        print(_row("top10% + C1 regime", m_regime))
        print(_row("等權基準(淨)", portfolio._metrics(np.array(r['bench_series'], float), ppy)))
        off = [str(d) for d, g in zip(dates, regime) if g == 0]
        print(f"\nregime-off(持現金)季: {off if off else '(無)'}")
        print("判讀:18 季樣本小——regime 訊號本身已 23 年驗過;此處看套用效果(尤 MaxDD)。off 季是否避開大跌為關鍵。")


if __name__ == "__main__":
    main()
