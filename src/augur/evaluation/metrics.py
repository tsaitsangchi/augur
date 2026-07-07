"""augur 可信度指標 — rank IC / Effective-t / 勝率 / IC 衰變（evaluation 層、#12 SSOT · #15）。

🎯 這支在做什麼（白話）：把「模型預測（每股 score/rank）」與「實際 forward 報酬 label」比，算 augur 信不信
這個模型的可信度指標——**全部是橫斷面相對強弱口徑、非絕對漲跌準確率**（#14）：
- **rank IC**：單 panel 內 predictions vs labels 的 Spearman rank 相關（-1~1；正=排序預測有效）。
- **跨 panel 彙總**：mean IC、IC 標準差、**Effective-t**（IC 序列 t-stat=mean/std×√n，是否顯著非零）、
  **勝率**（IC>0 的 panel 比例）、IC 半衰（按 H 比較需呼叫端跨 H）。

#12 SSOT：rank IC 與彙總公式**唯一住此**，所有 validator import——跨模型/跨週期才可比（憲章 #12）。
#15 誠實：raw + purged 雙口徑由呼叫端傳「哪些 panel 的 IC」決定（raw=全 test 折、purged=walkforward
embargo 後折）；本層只算指標、不選樣本（樣本選擇＝walkforward 層職責）。stochastic ≥3 seed 統計由呼叫端跑。
#14 經濟價值（top-N 報酬/MaxDD/Calmar）非本層——本層只到「排序預測力」；經濟價值需 portfolio 構造另計。
"""
from __future__ import annotations

import numpy as np
from scipy.stats import norm

_EULER_GAMMA = 0.5772156649015329   # Euler-Mascheroni 常數 γ(DSR SR_0 期望最大值近似需)


def _spearman(xs, ys):
    """Spearman rank 相關（兩序列 → 各自轉 rank → Pearson）。n<2 或零變異 → None（無從算）。"""
    n = len(xs)
    if n < 2:
        return None
    rx, ry = _ranks(xs), _ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx <= 0 or vy <= 0:
        return None                                   # 零變異（全同值）→ 相關無定義
    return cov / (vx * vy) ** 0.5


def _ranks(vals):
    """值序列 → 平均序位 rank（tie 取平均）。"""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def rank_ic(predictions, labels):
    """單 panel rank IC：predictions {stock_id: score} vs labels {stock_id: rank/return}。

    取兩 dict 之共同 stock_id（都有預測 + 都有 label）→ Spearman rank 相關。
    共同股 < 2 → None（該 panel 無從算 IC）。
    """
    common = [s for s in predictions if s in labels]
    if len(common) < 2:
        return None
    p = [predictions[s] for s in common]
    l = [labels[s] for s in common]
    return _spearman(p, l)


def summarize(ic_by_panel):
    """跨 panel IC 序列（{panel_date: ic} 或 list）→ 可信度彙總（#15 誠實揭露）。

    回 {n_panels, mean_ic, ic_std, effective_t, hit_rate, min_ic, max_ic}；
    Effective-t = mean_ic / ic_std × √n（IC 是否顯著非零）；hit_rate = IC>0 之 panel 比例。
    n<1 或全 None → 各值 None（沒比到 ≠ 比過且乾淨，#15）。
    """
    ics = list(ic_by_panel.values()) if isinstance(ic_by_panel, dict) else list(ic_by_panel)
    ics = [x for x in ics if x is not None and np.isfinite(x)]
    n = len(ics)
    if n == 0:
        return {"n_panels": 0, "mean_ic": None, "ic_std": None,
                "effective_t": None, "hit_rate": None, "min_ic": None, "max_ic": None}
    arr = np.array(ics, dtype=float)
    mean_ic = float(arr.mean())
    ic_std = float(arr.std(ddof=1)) if n >= 2 else None
    eff_t = float(mean_ic / ic_std * np.sqrt(n)) if ic_std and ic_std > 0 else None
    return {"n_panels": n, "mean_ic": mean_ic, "ic_std": ic_std,
            "effective_t": eff_t, "hit_rate": float((arr > 0).mean()),
            "min_ic": float(arr.min()), "max_ic": float(arr.max())}


def effective_t_hac(ic_by_panel, *, lag=None):
    """IC 序列之 Newey-West（HAC）去相關 t-stat——校正 IC 序列自相關（重疊 label 窗致 IC 正相關 →
    iid `effective_t` 高估顯著性,審查 G8）。Bartlett 核;lag=None → 經驗法則 floor(4*(n/100)^(2/9))。

    LRV = γ0 + 2·Σ_{l=1}^L (1−l/(L+1))·γ_l;se = √(LRV/n);t = mean/se。n<3 或 LRV≤0 → None。
    """
    ics = list(ic_by_panel.values()) if isinstance(ic_by_panel, dict) else list(ic_by_panel)
    ics = [x for x in ics if x is not None and np.isfinite(x)]
    n = len(ics)
    if n < 3:
        return None
    x = np.array(ics, dtype=float)
    e = x - x.mean()
    if lag is None:
        lag = max(1, int(np.floor(4 * (n / 100) ** (2 / 9))))
    lrv = float(e @ e) / n                                   # γ0
    for l in range(1, min(lag, n - 1) + 1):
        w = 1 - l / (lag + 1)                                # Bartlett 權
        lrv += 2 * w * float(e[l:] @ e[:-l]) / n             # 2·w·γ_l
    if lrv <= 0:
        return None
    se = (lrv / n) ** 0.5
    return float(x.mean() / se) if se > 0 else None


# ── Deflated Sharpe Ratio(DSR)——多重比較 deflation 之機讀真兆閘(#15/#14) ─────────
# 出處:Bailey, D. H. & López de Prado, M. (2014), "The Deflated Sharpe Ratio: Correcting
#   for Selection Bias, Backtest Overfitting and Non-Normality", Journal of Portfolio
#   Management, 40(5), 94-107. 亦見 SSOT sop_master 債 d / §6 decision-G7。
# 直覺:試了 N 個策略後挑出最好的一個,即使全無 skill,「試 N 次之最大 Sharpe」期望也 >0——
#   SR_0 就是這個 null 期望最大值。DSR = 觀測 SR 顯著超過 SR_0(且校正偏度/峰度/樣本量)的機率。


def expected_max_sharpe(n_trials, sr_var):
    """N 次試驗下 null 之期望最大 Sharpe SR_0(Bailey & López de Prado 2014 式 (5))。

    SR_0 = sqrt(Var(SR_trials)) · [ (1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N·e)) ],γ=Euler-Mascheroni。
    直覺:試驗越多(N↑)或試驗間 Sharpe 越分散(Var↑)→ 光靠選型挑最大就能得到越高的 SR_0(該扣越多血)。
    退化:N≤1 → 只試一個、無選型偏誤 → SR_0=0;Var(SR)=0(全同值)→ SR_0=0(無分散可挑)。
    """
    if n_trials is None or sr_var is None:
        return None
    n = float(n_trials)
    v = float(sr_var)
    if n <= 1 or v <= 0:
        return 0.0
    z1 = norm.ppf(1.0 - 1.0 / n)                      # Φ⁻¹(1−1/N)
    z2 = norm.ppf(1.0 - 1.0 / (n * np.e))             # Φ⁻¹(1−1/(N·e))
    return float(np.sqrt(v) * ((1.0 - _EULER_GAMMA) * z1 + _EULER_GAMMA * z2))


def deflated_sharpe(sr_obs, n_periods, *, n_trials, sr_var, skew=0.0, kurt=3.0):
    """Deflated Sharpe Ratio(Bailey & López de Prado 2014 式 (9))——扣多重比較後之真兆機率。

    先算 SR_0=期望最大 Sharpe(見 expected_max_sharpe);再:
      DSR = Φ[ (SR_obs − SR_0)·sqrt(T−1) / sqrt(1 − skew·SR_obs + ((kurt−1)/4)·SR_obs²) ]
    T=報酬期數(n_periods),skew/kurt=報酬分布偏度/峰度(kurt 為原始峰度、常態=3;非常態放大分母 → DSR 降)。
    回 dict:{sr_0, haircut, dsr, n_trials, n_periods, ...}。haircut=SR_obs−SR_0(直覺「扣了多少血」)。
    退化(#15 誠實揭露):N≤1 → SR_0=0、haircut=SR_obs(無選型扣血)、DSR=未 deflate 之單尾機率;
      Var(SR)=0 同上;T<2 → 無從算方差、DSR=None。輸入 None/非有限 → None。
    """
    if sr_obs is None or n_periods is None or not np.isfinite(sr_obs):
        return None
    t = int(n_periods)
    if t < 2:
        return {"sr_obs": float(sr_obs), "sr_0": None, "haircut": None,
                "dsr": None, "n_trials": n_trials, "n_periods": t,
                "note": "T<2 無從算標準誤,DSR 未定義"}
    sr0 = expected_max_sharpe(n_trials, sr_var)
    if sr0 is None:
        return None
    # 非常態校正分母(Sharpe 估計量之漸近標準差 × sqrt(T−1));kurt 為原始峰度(常態=3)。
    denom_var = 1.0 - skew * sr_obs + ((kurt - 1.0) / 4.0) * sr_obs ** 2
    if denom_var <= 0:
        return {"sr_obs": float(sr_obs), "sr_0": float(sr0),
                "haircut": float(sr_obs - sr0), "dsr": None,
                "n_trials": n_trials, "n_periods": t,
                "note": "非常態校正分母 ≤0,DSR 未定義(極端偏度/峰度)"}
    z = (sr_obs - sr0) * np.sqrt(t - 1) / np.sqrt(denom_var)
    return {"sr_obs": float(sr_obs), "sr_0": float(sr0),
            "haircut": float(sr_obs - sr0), "dsr": float(norm.cdf(z)),
            "n_trials": int(n_trials) if n_trials is not None else None,
            "n_periods": t, "skew": float(skew), "kurt": float(kurt)}


def sharpe_trial_variance(sharpes):
    """試驗間 Sharpe 之樣本方差 Var(SR_trials)(DSR 之 SR_0 需)。<2 個有限值 → None(無從算分散)。"""
    xs = [float(s) for s in sharpes if s is not None and np.isfinite(s)]
    if len(xs) < 2:
        return None
    return float(np.var(np.array(xs, dtype=float), ddof=1))
