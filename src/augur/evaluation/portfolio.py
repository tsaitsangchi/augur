"""augur 經濟價值回測 — 模型預測 → 橫斷面投組 → CAGR/Sharpe/MaxDD/Calmar(#14 真成功度量、非 IC)。

🎯 這支在做什麼(白話):靈魂成功定義是**經濟價值**(MaxDD/Calmar)非 AUC/IC。本模組把模型(Ridge/GBDT)之
purged walk-forward 預測,每 panel 依預測排序組投組(long top 分位、可選 long-short、可選預測加權),用實際前向報酬
(`label.forward_returns`、t+1 進場、還原價)算每期報酬 → 串成權益曲線 → 經濟指標,並對比等權基準。

**交易成本(#14 誠實終測)**:追蹤每次再平衡之**換手率**(投組成分變動比例),套用來回成本(台股約手續費 2×
0.1425% + 證交稅 0.3% ≈ 0.585%)算**淨報酬**——邊際扛不住成本即非真 alpha。基準亦計其宇宙換手成本(公平比)。

口徑 reuse baseline 之 walk-forward / as-of(#12);log→simple 報酬正確複利;holding=h 須與 panel 間距對齊(季度⇄h≈60)。
守 #8 · #12 · #14 · #15(gross/net 雙報、換手揭露、對比基準)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
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
    **向後相容(2026-07-17 破窗修)**:傳 ids 序列(list/tuple/set)→自動轉等權 dict——五個既有呼叫點
    (predict_asof/risk_control/direction_econ/survivorship×2)零改動、語意=等權半和(等檔數時≡交集法)。
    prev_ret={sid: 持有窗簡單報酬}給了→前期權重先按報酬**漂移**再比(0.5·Σ|w_cur−w_prev_drifted|;
    P0 §1a 實證含漂移口徑);缺股報酬視 0(保守)。等權配方下與交集法幾乎重合(P0:+2.8% 相對)。"""
    def _as_w(x):
        if x is None or isinstance(x, dict):
            return x
        xs = [str(s) for s in x]
        return {s: 1.0 / len(xs) for s in xs} if xs else {}
    cur_w, prev_w = _as_w(cur_w), _as_w(prev_w)
    if prev_w is None or not cur_w:
        return 1.0
    if prev_ret is not None:
        drift = {s: w * (1.0 + float(prev_ret.get(s, 0.0))) for s, w in prev_w.items()}
        tot = sum(drift.values())
        prev_w = {s: v / tot for s, v in drift.items()} if tot > 0 else prev_w
    union = set(cur_w) | set(prev_w)
    return 0.5 * sum(abs(cur_w.get(s, 0.0) - prev_w.get(s, 0.0)) for s in union)


def build_long_portfolio(sids, preds, top_frac=0.2, weight="equal", prev_ids=None, exit_frac=None):
    """預測 → top-frac long 選取 + 權重(#12 命門:backtest 與 live 唯一選股邏輯住所)。

    sids/preds 同序、任意尺度(只看序位)。回 [(stock_id, weight, rank), ...] 依預測降序、
    weight 和為 1。weight='equal'(等權 1/N)或 'pred'(rank 加權:第 1 名權重最大、線性遞減)。
    nt=max(1, int(N*top_frac))。**run_backtest 與 predict_asof 皆呼叫此支**,選股位元一致零漂移。

    **buffer-zone 遲滯(P1,alpha 計畫 1-3;預設關=行為零漂移)**:prev_ids+exit_frac 給了→
    已持有股 rank 仍在前 exit_frac 內則**保留**(遲滯帶抑制 rank 噪音換手),空位由未持有之
    最強新股補至 nt;進場帶=top_frac、出場帶=exit_frac(exit>entry,如 0.1/0.2 預註冊單點)。
    保留股權重序位=其當期 rank(誠實:非凍結舊權重)。
    """
    import numpy as _np
    preds = _np.asarray(preds, dtype=float)
    n = len(sids)
    if n == 0:
        return []
    order = _np.argsort(preds)[::-1]                     # 分數降序=相對強
    nt = max(1, int(n * top_frac))
    if prev_ids and exit_frac:
        rank_of = {str(sids[k]): i for i, k in enumerate(order)}      # 0-based 當期序位
        nx = max(nt, int(n * exit_frac))
        keep = [s for s in prev_ids if rank_of.get(str(s), n) < nx]   # 未跌出出場帶之舊股
        kept = set(keep)
        fill = [str(sids[k]) for k in order if str(sids[k]) not in kept][:max(0, nt - len(keep))]
        chosen = sorted(set(keep) | set(fill), key=lambda s: rank_of[s])[:max(nt, len(keep))]
        m = len(chosen)
        if weight == "pred":
            w = _np.arange(m, 0, -1, dtype=float); w /= w.sum()
        else:
            w = _np.full(m, 1.0 / m)
        return [(s, float(w[j]), rank_of[s] + 1) for j, s in enumerate(chosen)]
    top_idx = order[:nt]
    if weight == "pred":                                 # 預測 rank 加權(正權重、和為 1、第一名最大)
        w = _np.arange(nt, 0, -1, dtype=float); w /= w.sum()
    else:                                                # 等權
        w = _np.full(nt, 1.0 / nt)
    return [(str(sids[k]), float(w[j]), j + 1) for j, k in enumerate(top_idx)]


def vol_target_series(series, ppy, target_ann_vol=None, lookback=4, max_scale=1.0):
    """波動率目標 overlay(P4,alpha 1-4;誠實化籃=分母工程):逐期以 **trailing ≤t−1** 已實現 vol 縮放曝險。

    scale_t = min(max_scale, target/realized_{t-lookback..t-1});首 lookback 期無足夠歷史→scale=1
    (dormant,誠實揭露);target_ann_vol=None→用全序列已實現年化 vol(口徑內生、零外生魔數,預註冊單點)。
    long-only 無槓桿:max_scale=1.0=只縮不放(縮=部分轉現金,現金報酬 0 保守)。
    回 (scaled_series, scales, dormant_n)。#8:scale_t 嚴禁用 t 期當期報酬。純函式(selftest 可測)。"""
    s = np.asarray(series, float)
    n = len(s)
    if n == 0:
        return [], [], 0
    if target_ann_vol is None:
        target_ann_vol = float(np.std(s, ddof=1)) * float(np.sqrt(ppy)) if n > 1 else 0.0
    scales, dormant = [], 0
    for t in range(n):
        if t < lookback:
            scales.append(1.0); dormant += 1
            continue
        rv = float(np.std(s[t - lookback:t], ddof=1)) * float(np.sqrt(ppy))   # ≤t−1 窗(#8)
        scales.append(1.0 if rv <= 0 else min(max_scale, target_ann_vol / rv))
    return [float(s[t] * scales[t]) for t in range(n)], scales, dormant


def run_backtest(conn, panels, h, *, feats=None, model="B2_ridge", top_frac=0.2,
                 long_short=False, weight="equal", seed=42, asof=True, cost=0.0, interactions=None,
                 short_borrow=0.0, exit_frac=None):
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
        port = build_long_portfolio(common, pred, top_frac=top_frac, weight=weight,   # #12 共用選股(backtest≡live)
                                    prev_ids=(list(prev_top) if prev_top else None), exit_frac=exit_frac)
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
    chk("_turnover ids 相容:list 呼法=等權半和(破窗修 2026-07-17;等檔數≡交集法)",
        _turnover(["a", "b"], ["a", "c"]) == 0.5 and _turnover(["a", "b"], ["a", "b"]) == 0.0
        and _turnover(["a", "b"], None) == 1.0)
    # P4 vol targeting(1-4)紅綠:≤t−1 無前視/dormant 揭露/高 vol 期縮/只縮不放
    calm = [0.01] * 6
    spike = calm + [0.30, -0.30, 0.30, -0.30]
    vt, sc, dn = vol_target_series(spike, ppy=4.0, lookback=4)
    chk("vol_target:首 lookback 期 dormant=scale 1", dn == 4 and all(x == 1.0 for x in sc[:4]))
    chk("vol_target:高 vol 段被縮(scale<1)", sc[-1] < 1.0 and abs(vt[-1]) < abs(spike[-1]))
    chk("vol_target:平靜段不放大(max_scale=1)", all(x <= 1.0 for x in sc))
    _, sc2, _ = vol_target_series(calm + [9.9], ppy=4.0, lookback=4)
    chk("vol_target:#8 無前視——t 期爆量不影響 t 期 scale(仍由 ≤t−1 決定)", sc2[-1] == sc[len(calm)] or sc2[-1] == 1.0)

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
    # P1 buffer-zone(1-3)紅綠:遲滯保留/跌出即換/無 prev=原行為
    sids5 = ["a", "b", "c", "d", "e"]
    p5 = [5.0, 4.0, 3.0, 2.0, 1.0]                      # a 最強…e 最弱
    base = build_long_portfolio(sids5, p5, top_frac=0.4)                       # top2=a,b
    buf_same = build_long_portfolio(sids5, p5, top_frac=0.4, prev_ids=None, exit_frac=0.8)
    chk("buffer:無 prev=原行為零漂移", [s for s, _, _ in base] == [s for s, _, _ in buf_same] == ["a", "b"])
    held = build_long_portfolio(sids5, p5, top_frac=0.4, prev_ids=["c"], exit_frac=0.8)
    chk("buffer:持有 c(rank3<出場帶4)保留+補最強 a", set(s for s, _, _ in held) == {"a", "c"})
    drop = build_long_portfolio(sids5, p5, top_frac=0.4, prev_ids=["e"], exit_frac=0.6)
    chk("buffer:持有 e(rank5>出場帶3)跌出→換回 top2", set(s for s, _, _ in drop) == {"a", "b"})
    wsum = sum(w for _, w, _ in held)
    chk("buffer:權重和=1", abs(wsum - 1.0) < 1e-12)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.evaluation.portfolio --selftest;免 DB 免 API)")
