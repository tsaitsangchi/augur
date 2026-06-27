"""augur 經濟價值回測 — 模型預測 → 橫斷面投組 → CAGR/Sharpe/MaxDD/Calmar(#14 真成功度量、非 IC)。

🎯 這支在做什麼(白話):靈魂成功定義是**經濟價值**(MaxDD/Calmar)非 AUC/IC。本模組把模型(Ridge/GBDT)之
purged walk-forward 預測,每 panel 依預測排序組投組(long top 分位、可選 long-short),用實際前向報酬
(`label.forward_returns`、t+1 進場、還原價)算每期報酬 → 串成權益曲線 → 經濟指標,並對比等權基準。

口徑:reuse baseline 之 walk-forward / as-of / _fold_xy / _panel_matrix(#12 一致可比);log→simple 報酬正確複利。
**holding=h 交易日須與 panel 間距對齊才 tile**(季度 panel ⇄ h≈60);早年年度 panel 與 h=60 有 gap、預設 --since 2021 取季度段。

守 #8(as-of/purged)· #12(SSOT helper)· #14(經濟指標)· #15(對比基準、誠實揭露 n/span)。
"""
from __future__ import annotations

import numpy as np

from augur.evaluation import baseline, walkforward
from augur.evaluation import label as label_mod


def _metrics(simple_rets, ppy):
    """每期 simple 報酬序列 → 經濟指標(CAGR/Sharpe/MaxDD/Calmar/hit)。"""
    a = np.array([r for r in simple_rets if r is not None and np.isfinite(r)], float)
    if len(a) < 2:
        return {}
    eq = np.cumprod(1 + a)
    yrs = max(len(a) / ppy, 1e-9)
    cagr = float(eq[-1] ** (1 / yrs) - 1) if eq[-1] > 0 else None
    sd = a.std(ddof=1)
    sharpe = float(a.mean() / sd * np.sqrt(ppy)) if sd > 0 else None
    peak = np.maximum.accumulate(eq)
    maxdd = float((eq / peak - 1).min())
    calmar = float(cagr / abs(maxdd)) if (cagr is not None and maxdd < 0) else None
    return {"n": int(len(a)), "total_return": float(eq[-1] - 1), "cagr": cagr, "sharpe": sharpe,
            "max_drawdown": maxdd, "calmar": calmar, "hit_rate": float((a > 0).mean()),
            "mean_period_ret": float(a.mean())}


def run_backtest(conn, panels, h, *, feats=None, model="B2_ridge", top_frac=0.2, long_short=False, seed=42, asof=True):
    """模型預測 → 投組 → 經濟指標 + 等權基準。回 {portfolio, benchmark, n_periods, periods_per_year, span}。"""
    from lightgbm import LGBMRegressor
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler

    feats = feats or baseline.canonical_features(conn, panels)
    folds = walkforward.splits(panels, h)
    cal = label_mod.full_calendar(conn)
    port, bench, dates = [], [], []
    for fold in folds:
        tpd = fold["test"]
        stocks = baseline._asof_stocks(conn, tpd) if asof else None
        sids, Xte = baseline._panel_matrix(conn, tpd, stocks, feats)
        if len(sids) < 10:
            continue
        fwd = label_mod.forward_returns(conn, tpd, sids, h, calendar=cal)
        common = [s for s in sids if s in fwd]
        if len(common) < 10:
            continue
        Xtr, ytr = baseline._fold_xy(conn, fold["train"], stocks, feats, h, calendar=cal, asof=asof)
        if len(ytr) < 50:
            continue
        ci = [sids.index(s) for s in common]
        Xc = Xte[ci]
        if model == "B2_ridge":
            sc = StandardScaler().fit(Xtr)
            pred = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr).predict(sc.transform(Xc))
        else:
            pred = LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=15,
                                 min_child_samples=30, subsample=0.8, colsample_bytree=0.8,
                                 random_state=seed, verbose=-1).fit(Xtr, ytr).predict(Xc)
        simple = np.array([float(np.expm1(fwd[s])) for s in common])    # log→simple(正確複利)
        order = np.argsort(pred)[::-1]                                  # 高預測在前
        nt = max(1, int(len(common) * top_frac))
        top = float(simple[order[:nt]].mean())
        p = top - float(simple[order[-nt:]].mean()) if long_short else top
        port.append(p)
        bench.append(float(simple.mean()))
        dates.append(tpd)
    if len(dates) < 3:
        return {}
    ppy = len(dates) / max((dates[-1] - dates[0]).days / 365.0, 1e-9)
    return {"portfolio": _metrics(port, ppy), "benchmark": _metrics(bench, ppy),
            "n_periods": len(dates), "periods_per_year": round(ppy, 2), "span": f"{dates[0]}..{dates[-1]}"}
