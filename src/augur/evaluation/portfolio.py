"""augur 經濟價值回測 — 模型預測 → 橫斷面投組 → CAGR/Sharpe/MaxDD/Calmar(#14 真成功度量、非 IC)。

🎯 這支在做什麼(白話):靈魂成功定義是**經濟價值**(MaxDD/Calmar)非 AUC/IC。本模組把模型(Ridge/GBDT)之
purged walk-forward 預測,每 panel 依預測排序組投組(long top 分位、可選 long-short、可選預測加權),用實際前向報酬
(`label.forward_returns`、t+1 進場、還原價)算每期報酬 → 串成權益曲線 → 經濟指標,並對比等權基準。

**交易成本(#14 誠實終測)**:追蹤每次再平衡之**換手率**(投組成分變動比例),套用來回成本(台股約手續費 2×
0.1425% + 證交稅 0.3% ≈ 0.585%)算**淨報酬**——邊際扛不住成本即非真 alpha。基準亦計其宇宙換手成本(公平比)。

口徑 reuse baseline 之 walk-forward / as-of(#12);log→simple 報酬正確複利;holding=h 須與 panel 間距對齊(季度⇄h≈60)。
守 #8 · #12 · #14 · #15(gross/net 雙報、換手揭露、對比基準)。
"""
from __future__ import annotations

import numpy as np

from augur.evaluation import baseline, cross_section, walkforward
from augur.evaluation import label as label_mod


def _metrics(simple_rets, ppy):
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
            "max_drawdown": maxdd, "calmar": calmar, "hit_rate": float((a > 0).mean())}


def _turnover(cur_ids, prev_ids):
    """投組成分變動比例(0=完全不變、1=全換);prev None → 1(初次建倉)。"""
    if prev_ids is None or not cur_ids:
        return 1.0
    return 1.0 - len(set(cur_ids) & set(prev_ids)) / len(cur_ids)


def run_backtest(conn, panels, h, *, feats=None, model="B2_ridge", top_frac=0.2,
                 long_short=False, weight="equal", seed=42, asof=True, cost=0.0, interactions=None):
    """模型預測 → 投組 → 經濟指標(gross/net)+ 等權基準。

    weight：'equal'（等權 top）或 'pred'（預測值 rank 加權，正權重）。cost：來回成本（如 0.00585）套於換手。
    回 {portfolio_gross, portfolio_net, benchmark_net, avg_turnover, bench_turnover, n_periods, periods_per_year, span}。
    """
    from lightgbm import LGBMRegressor
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler

    feats = feats or baseline.canonical_features(conn, panels)
    cal = label_mod.full_calendar(conn)
    folds = walkforward.splits(panels, h, calendar=cal)   # 保證 embargo 下界 = h+62td(#8、A'-3 口徑a、逐折真實交易日)
    gross, net, bench, dates, turns, bturns = [], [], [], [], [], []
    prev_top, prev_uni = None, None
    for fold in folds:
        tpd = fold["test"]
        stocks = baseline._asof_stocks(conn, tpd) if asof else None
        sids, Xte = baseline._panel_matrix(conn, tpd, stocks, feats)
        if len(sids) < 10:
            continue
        if interactions:
            Xte, _ = cross_section.augment(Xte, feats, interactions)     # test 側逐 panel 橫斷面 z（當下宇宙、同 train 口徑）
        fwd = label_mod.forward_returns(conn, tpd, sids, h, calendar=cal)
        common = [s for s in sids if s in fwd]
        if len(common) < 10:
            continue
        Xtr, ytr = baseline._fold_xy(conn, fold["train"], stocks, feats, h, calendar=cal, asof=asof, interactions=interactions)
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
        simple = np.array([float(np.expm1(fwd[s])) for s in common])
        order = np.argsort(pred)[::-1]
        nt = max(1, int(len(common) * top_frac))
        top_idx = order[:nt]
        top_ids = [common[k] for k in top_idx]
        if weight == "pred":                                          # 預測 rank 加權(正權重、和為 1)
            w = np.arange(nt, 0, -1, dtype=float); w /= w.sum()
            long_ret = float((simple[top_idx] * w).sum())
        else:
            long_ret = float(simple[top_idx].mean())
        g = long_ret - (float(simple[order[-nt:]].mean()) if long_short else 0.0)
        turn = _turnover(top_ids, prev_top)
        bturn = _turnover(common, prev_uni)
        prev_top, prev_uni = top_ids, common
        gross.append(g)
        net.append(g - turn * cost)                                   # 成本套於換手比例
        bench.append(float(simple.mean()) - bturn * cost)             # 基準亦計宇宙換手成本(公平)
        turns.append(turn); bturns.append(bturn); dates.append(tpd)
    if len(dates) < 3:
        return {}
    ppy = len(dates) / max((dates[-1] - dates[0]).days / 365.0, 1e-9)
    return {"portfolio_gross": _metrics(gross, ppy), "portfolio_net": _metrics(net, ppy),
            "benchmark_net": _metrics(bench, ppy), "avg_turnover": float(np.mean(turns)),
            "bench_turnover": float(np.mean(bturns)), "n_periods": len(dates),
            "periods_per_year": round(ppy, 2), "span": f"{dates[0]}..{dates[-1]}",
            "dates": dates, "net_series": net, "gross_series": gross, "bench_series": bench, "ppy": ppy}
