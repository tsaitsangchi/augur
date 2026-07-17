"""augur 經濟價值回測 — 模型預測 → 橫斷面投組 → CAGR/Sharpe/MaxDD/Calmar(#14 真成功度量、非 IC)。

🎯 這支在做什麼(白話):靈魂成功定義是**經濟價值**(MaxDD/Calmar)非 AUC/IC。本模組把模型(Ridge/GBDT)之
purged walk-forward 預測,每 panel 依預測排序組投組(long top 分位、可選 long-short、可選預測加權),用實際前向報酬
(`label.forward_returns`、t+1 進場、還原價)算每期報酬 → 串成權益曲線 → 經濟指標,並對比等權基準。

**交易成本(#14 誠實終測)**:追蹤每次再平衡之**換手率**(投組成分變動比例),套用來回成本(台股約手續費 2×
0.1425% + 證交稅 0.3% ≈ 0.585%)算**淨報酬**——邊際扛不住成本即非真 alpha。基準亦計其宇宙換手成本(公平比)。

口徑 reuse baseline 之 walk-forward / as-of(#12);log→simple 報酬正確複利;holding=h 須與 panel 間距對齊(季度⇄h≈60)。
守 #8 · #12 · #14 · #15(gross/net 雙報、換手揭露、對比基準)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.evaluation.portfolio              # 印用途+公開入口（唯讀）
  python -m augur.evaluation.portfolio --selftest   # 純紅綠自測（零 IO）
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


def _turnover(cur_w, prev_w, prev_ret=None):
    """換手率=半和口徑 0.5·Σ|Δw|(P2 量尺校準,alpha 計畫 1-2/hugo 開工 2026-07-17;
    取代交集法——交集法只看成分不看權重,pred 加權下系統性低估)。
    cur_w/prev_w={sid: weight}(和為 1);prev None→1.0(初次建倉)。
    prev_ret={sid: 持有窗簡單報酬}給了→前期權重先按報酬**漂移**再比(0.5·Σ|w_cur−w_prev_drifted|;
    P0 §1a 實證含漂移口徑);缺股報酬視 0(保守)。等權配方下與交集法幾乎重合(P0:+2.8% 相對)。"""
    if prev_w is None or not cur_w:
        return 1.0
    if prev_ret is not None:
        drift = {s: w * (1.0 + float(prev_ret.get(s, 0.0))) for s, w in prev_w.items()}
        tot = sum(drift.values())
        prev_w = {s: v / tot for s, v in drift.items()} if tot > 0 else prev_w
    union = set(cur_w) | set(prev_w)
    return 0.5 * sum(abs(cur_w.get(s, 0.0) - prev_w.get(s, 0.0)) for s in union)


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
    prev_top, prev_uni, prev_ret = None, None, None
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
        elif model == "ENS_ridge_gbdt":   # 階段3 挑戰者:等權 rank-average(Ridge+GBDT),零調權=最低過擬合、抗 regime
            from scipy.stats import rankdata
            sc = StandardScaler().fit(Xtr)
            p_r = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr).predict(sc.transform(Xc))
            p_g = LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=15, min_child_samples=30,
                                subsample=0.8, colsample_bytree=0.8, random_state=seed, verbose=-1).fit(Xtr, ytr).predict(Xc)
            pred = (rankdata(p_r) + rankdata(p_g)) / 2.0
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
        cur_w = {sid: w for sid, w, _ in port}                       # P2 半和口徑:權重 dict(等權/pred 加權皆真權重)
        uni_w = {s: 1.0 / len(common) for s in common}
        turn = _turnover(cur_w, prev_top, prev_ret)
        bturn = _turnover(uni_w, prev_uni, prev_ret)
        prev_top, prev_uni, prev_ret = cur_w, uni_w, ret_by_id
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


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：合成資料紅綠測純函式——
    drawdown_series/_metrics/_turnover/build_long_portfolio 核心不變式回歸鎖。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # drawdown_series:eq=cumprod(1+r)、dd=eq/peak−1≤0;+0.5 後 −0.5 → 最深回檔 −0.5
    eq, dd = drawdown_series([0.5, -0.5])
    chk("drawdown_series eq 複利([1.5,0.75])", abs(eq[0] - 1.5) < 1e-9 and abs(eq[1] - 0.75) < 1e-9)
    chk("drawdown_series 最深回檔=−0.5", abs(dd.min() - (-0.5)) < 1e-9 and dd.max() <= 1e-12)
    e0, d0 = drawdown_series([])
    chk("drawdown_series 空序列→空", len(e0) == 0 and len(d0) == 0)

    # _turnover:0=不變、1=全換、None=初次建倉、半換=0.5
    eq = {"a": 0.5, "b": 0.5}
    chk("_turnover 半和:完全不變=0", _turnover(eq, {"a": 0.5, "b": 0.5}) == 0.0)
    chk("_turnover 半和:等權半換=0.5", _turnover(eq, {"a": 0.5, "c": 0.5}) == 0.5)
    chk("_turnover prev=None→1(初次)", _turnover(eq, None) == 1.0)
    chk("_turnover 半和:權重變動被計(交集法盲區)",
        abs(_turnover({"a": 0.8, "b": 0.2}, {"a": 0.2, "b": 0.8}) - 0.6) < 1e-12)
    chk("_turnover 漂移:a 翻倍後權重漂移被計入",
        abs(_turnover(eq, eq, {"a": 1.0, "b": 0.0}) - abs(0.5 - 2.0 / 3.0)) < 1e-12)
    chk("_turnover 漂移:零報酬=無漂移(同無 prev_ret)", _turnover(eq, eq, {"a": 0.0, "b": 0.0}) == 0.0)

    # _metrics:全正報酬 hit_rate=1、len<2→{}
    m = _metrics([0.1, 0.1, 0.1], 1.0)
    chk("_metrics 全正 hit_rate=1 · n=3", m.get("n") == 3 and m.get("hit_rate") == 1.0)
    chk("_metrics len<2→{}", _metrics([0.1], 1.0) == {})

    # build_long_portfolio:降序選 top、權重和=1、pred 加權第一名最大、空→[]
    port = build_long_portfolio(["a", "b", "c", "d", "e"], [1, 2, 3, 4, 5], top_frac=0.4, weight="equal")
    chk("build_long_portfolio nt=2 · 最強在前(e)", len(port) == 2 and port[0][0] == "e" and port[0][2] == 1)
    chk("build_long_portfolio 等權和=1", abs(sum(w for _, w, _ in port) - 1.0) < 1e-9)
    pw = build_long_portfolio(["a", "b", "c", "d", "e"], [1, 2, 3, 4, 5], top_frac=0.6, weight="pred")
    chk("build_long_portfolio pred 加權第一名最大·和=1",
        pw[0][1] > pw[-1][1] and abs(sum(w for _, w, _ in pw) - 1.0) < 1e-9)
    chk("build_long_portfolio 空輸入→[]", build_long_portfolio([], []) == [])

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.evaluation.portfolio --selftest;免 DB 免 API)")
