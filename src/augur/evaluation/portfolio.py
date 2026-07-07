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


def drawdown_series(simple_rets):
    """simple 報酬序列 → (equity, drawdown) 兩序列(DD 算法單一住所,#12)。

    equity=cumprod(1+r);drawdown=equity/peak−1(peak=歷來高點,≤0)。當前回檔=drawdown[-1]、
    最深回檔=drawdown.min()。**_metrics 與風控 execution.risk_control 皆呼叫此支**——DD 算法零重造。
    回 (equity ndarray, drawdown ndarray);空/單點序列回 (空, 空)。
    """
    a = np.array([r for r in simple_rets if r is not None and np.isfinite(r)], float)
    if len(a) < 1:
        return np.array([]), np.array([])
    eq = np.cumprod(1 + a)
    peak = np.maximum.accumulate(eq)
    return eq, eq / peak - 1


def _metrics(simple_rets, ppy):
    a = np.array([r for r in simple_rets if r is not None and np.isfinite(r)], float)
    if len(a) < 2:
        return {}
    eq, dd = drawdown_series(a)
    yrs = max(len(a) / ppy, 1e-9)
    cagr = float(eq[-1] ** (1 / yrs) - 1) if eq[-1] > 0 else None
    sd = a.std(ddof=1)
    sharpe = float(a.mean() / sd * np.sqrt(ppy)) if sd > 0 else None
    maxdd = float(dd.min())
    calmar = float(cagr / abs(maxdd)) if (cagr is not None and maxdd < 0) else None
    return {"n": int(len(a)), "total_return": float(eq[-1] - 1), "cagr": cagr, "sharpe": sharpe,
            "max_drawdown": maxdd, "calmar": calmar, "hit_rate": float((a > 0).mean())}


def _turnover(cur_ids, prev_ids):
    """投組成分變動比例(0=完全不變、1=全換);prev None → 1(初次建倉)。"""
    if prev_ids is None or not cur_ids:
        return 1.0
    return 1.0 - len(set(cur_ids) & set(prev_ids)) / len(cur_ids)


def build_long_portfolio(sids, preds, top_frac=0.2, weight="equal"):
    """預測 → top-frac long 選取 + 權重(#12 命門:backtest 與 live 唯一選股邏輯住所)。

    sids/preds 同序、任意尺度(只看序位)。回 [(stock_id, weight, rank), ...] 依預測降序、
    weight 和為 1。weight='equal'(等權 1/N)或 'pred'(rank 加權:第 1 名權重最大、線性遞減)。
    nt=max(1, int(N*top_frac))。**run_backtest 與 predict_asof 皆呼叫此支**,選股位元一致零漂移。
    """
    import numpy as _np
    preds = _np.asarray(preds, dtype=float)
    n = len(sids)
    if n == 0:
        return []
    order = _np.argsort(preds)[::-1]                     # 分數降序=相對強
    nt = max(1, int(n * top_frac))
    top_idx = order[:nt]
    if weight == "pred":                                 # 預測 rank 加權(正權重、和為 1、第一名最大)
        w = _np.arange(nt, 0, -1, dtype=float); w /= w.sum()
    else:                                                # 等權
        w = _np.full(nt, 1.0 / nt)
    return [(str(sids[k]), float(w[j]), j + 1) for j, k in enumerate(top_idx)]


def run_backtest(conn, panels, h, *, feats=None, model="B2_ridge", top_frac=0.2,
                 long_short=False, weight="equal", seed=42, asof=True, cost=0.0, interactions=None,
                 short_borrow=0.0):
    """模型預測 → 投組 → 經濟指標(gross/net)+ 等權基準。

    weight：'equal'（等權 top）或 'pred'（預測值 rank 加權，正權重）。cost：來回成本（如 0.00585）套於換手。
    short_borrow：放空**年化**借券/融券成本（如 0.02=2%/年,long_short=True 才套）——每期按持有期 h/252 折算、
      套於短腿名目（dollar-neutral LS 短腿≈1×多腿）；預設 0=不計短腿摩擦（=既有行為，向後相容）。
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
        ret_by_id = {common[k]: simple[k] for k in range(len(common))}
        port = build_long_portfolio(common, pred, top_frac=top_frac, weight=weight)  # #12 共用選股(backtest≡live)
        top_ids = [sid for sid, _, _ in port]
        long_ret = float(sum(w * ret_by_id[sid] for sid, w, _ in port))
        order = np.argsort(pred)[::-1]
        nt = len(port)
        g = long_ret - (float(simple[order[-nt:]].mean()) if long_short else 0.0)
        turn = _turnover(top_ids, prev_top)
        bturn = _turnover(common, prev_uni)
        prev_top, prev_uni = top_ids, common
        sb = (short_borrow * h / 252.0) if long_short else 0.0        # 放空借券成本:年化→持有期、套短腿名目
        gross.append(g)
        net.append(g - turn * cost - sb)                              # 淨=毛 − 換手成本 − 放空借券成本
        bench.append(float(simple.mean()) - bturn * cost)             # 基準亦計宇宙換手成本(公平;基準無放空)
        turns.append(turn); bturns.append(bturn); dates.append(tpd)
    if len(dates) < 3:
        return {}
    ppy = len(dates) / max((dates[-1] - dates[0]).days / 365.0, 1e-9)
    return {"portfolio_gross": _metrics(gross, ppy), "portfolio_net": _metrics(net, ppy),
            "benchmark_net": _metrics(bench, ppy), "avg_turnover": float(np.mean(turns)),
            "bench_turnover": float(np.mean(bturns)), "n_periods": len(dates),
            "periods_per_year": round(ppy, 2), "span": f"{dates[0]}..{dates[-1]}",
            "dates": dates, "net_series": net, "gross_series": gross, "bench_series": bench, "ppy": ppy}
