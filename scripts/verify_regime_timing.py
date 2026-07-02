#!/usr/bin/env python
"""augur regime 擇時驗證 — C1 景氣訊號在 23 年 TAIEX 報酬指數上之擇時力(長樣本、避 18 季過配)。

🎯 這支在做什麼(白話):regime-conditional 前置驗證——先問「C1 景氣訊號到底能不能擇時大盤?」(用長樣本)。
用 `TaiwanBusinessIndicator`(月頻)之領先/同時去趨勢 + monitoring 分數做 data-driven regime 規則,**發布日 lag 2 月**(#8),
在 TAIEX 報酬指數(2003-2026、~23 年/276 月)上做擇時(regime-on 持有、off 持現金)vs 買進持有,比 CAGR/Sharpe/MaxDD/Calmar。

紀律:#9 不硬編燈號分界——用 sign(動能)/官方趨勢中心 100 之相對/own-history。#8 發布日 lag。#15 對比買持、誠實。
**通過(擇時改善風險調整或大降 MaxDD)才套到投組;否則 18 季擇時不可信、不做。** 本地零 usage(#28)。
執行指令矩陣:python scripts/verify_regime_timing.py --lag 2
"""
import argparse

import numpy as np
import pandas as pd

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db


def _metrics(rets):
    a = np.asarray(rets, float); a = a[np.isfinite(a)]
    if len(a) < 12:
        return {}
    eq = np.cumprod(1 + a)
    cagr = float(eq[-1] ** (12 / len(a)) - 1) if eq[-1] > 0 else None
    sd = a.std(ddof=1)
    sharpe = float(a.mean() / sd * np.sqrt(12)) if sd > 0 else None
    maxdd = float((eq / np.maximum.accumulate(eq) - 1).min())
    calmar = float(cagr / abs(maxdd)) if (cagr is not None and maxdd < 0) else None
    return {"cagr": cagr, "sharpe": sharpe, "maxdd": maxdd, "calmar": calmar}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lag", type=int, default=2, help="發布日 lag 月數(C1 訊號延後可用)")
    args = ap.parse_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute('SELECT date, "leading", leading_notrend, coincident_notrend, monitoring FROM "TaiwanBusinessIndicator" ORDER BY date')
            c1 = pd.DataFrame(cur.fetchall(), columns=["date", "leading", "lead_nt", "coin_nt", "monitoring"]).set_index("date").astype(float)
            cur.execute("SELECT date, price FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX' ORDER BY date")
            mkt = pd.DataFrame(cur.fetchall(), columns=["date", "price"]).set_index("date")
    c1.index = pd.to_datetime(c1.index).to_period("M")
    px = mkt["price"].astype(float)
    px.index = pd.to_datetime(px.index)
    mret = px.resample("ME").last().pct_change()                     # 月報酬
    mret.index = mret.index.to_period("M")

    # data-driven regime 規則(#9):sign(動能)/官方趨勢中心 100
    sig = pd.DataFrame(index=c1.index)
    sig["lead_nt_above"] = (c1["lead_nt"] > 100).astype(float)        # 領先去趨勢 > 趨勢線(官方定義中心)
    sig["lead_nt_rising"] = (c1["lead_nt"] > c1["lead_nt"].shift(3)).astype(float)   # 3 月動能升
    sig["coin_nt_rising"] = (c1["coin_nt"] > c1["coin_nt"].shift(3)).astype(float)
    sig["monitoring_rising"] = (c1["monitoring"] > c1["monitoring"].shift(3)).astype(float)
    sig["lead_above_and_rising"] = ((c1["lead_nt"] > 100) & (c1["lead_nt"] > c1["lead_nt"].shift(3))).astype(float)
    sig = sig.shift(args.lag)                                         # 發布日 lag(#8)

    df = sig.join(mret.rename("mret"), how="inner").dropna(subset=["mret"])
    bh = _metrics(df["mret"].values)
    print(f"regime 擇時驗證:{len(df)} 月（{df.index.min()}..{df.index.max()}）、發布日 lag {args.lag} 月")
    print(f"\n{'策略':24s} {'CAGR':>7s} {'Sharpe':>7s} {'MaxDD':>7s} {'Calmar':>7s} {'在市%':>6s}")
    print(f"{'買進持有(基準)':24s} {bh['cagr']:>+7.1%} {bh['sharpe']:>7.2f} {bh['maxdd']:>+7.1%} {bh['calmar']:>7.2f} {'100%':>6s}")
    for col in [c for c in sig.columns]:
        on = df[col].fillna(0)
        strat = df["mret"] * on                                      # regime-on 持有、off 現金(0)
        m = _metrics(strat.values)
        if not m:
            continue
        print(f"{col:24s} {m['cagr']:>+7.1%} {m['sharpe']:>7.2f} {m['maxdd']:>+7.1%} {m['calmar']:>7.2f} {on.mean():>6.0%}")
    print("\n判讀:擇時 Sharpe/Calmar 顯著優於買持(尤大降 MaxDD)→ regime 訊號有擇時力、可套投組;否則不做(18 季不可信)。")


if __name__ == "__main__":
    main()
