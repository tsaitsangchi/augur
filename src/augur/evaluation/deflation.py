"""Deflated Sharpe per-period 計算 SSOT — headline 裁決與 harness 再驗證共用單一住所(#12)。

🎯 這支在做什麼(白話):把「淨報酬序列 → per-period Sharpe/skew/kurt/T + 試驗 SR 分散 → DSR」這條
   **per-period 正確口徑**(非年化 bug)抽成共用函式,供 `deflate_headline_verdict`(headline 終判)與
   `revalidate`(harness 逐輪 deflation 整合)兩處呼叫——**禁平行重寫**(平行重寫=年化 units bug 復發風險,
   本 session 已踩:年化 SR 配 sqrt(T-1) 使 z 灌水 √ppy 倍、DSR 高估~14pp)。

   命門(#8/#15):sr_obs/SR_0/sqrt(T-1) 一律 per-period(Bailey-LdP 2014 / Lo 2002 標準誤口徑);
   試驗 SR 逐 horizon 各自 ppy 轉 per-period 才並池算 Var(SR);N 由 trial_ledger 機械(禁人手,SOP §6 G7)。

守 #8(per-period 正確口徑) · #12(DSR 計算單一住所、reuse metrics.deflated_sharpe) · #15(誠實、非年化)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.evaluation.deflation              # 印用途+公開入口（唯讀）
  python -m augur.evaluation.deflation --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import numpy as np

from augur.evaluation import metrics


def per_period_stats(net_series):
    """淨報酬序列 → (sr_pp, T, skew, kurt)。sr_pp=per-period Sharpe(mean/sd ddof=1、非年化);
    kurt=原始峰度(常態=3)。<2 有限值 → (None, n, 0.0, 3.0)(無從算)。"""
    from scipy.stats import kurtosis as _kurt
    from scipy.stats import skew as _skew
    a = np.array([r for r in net_series if r is not None and np.isfinite(r)], float)
    if len(a) < 2:
        return None, len(a), 0.0, 3.0
    sd = a.std(ddof=1)
    sr_pp = float(a.mean() / sd) if sd > 0 else None
    return sr_pp, len(a), float(_skew(a)), float(_kurt(a, fisher=False))


def trials_per_period(trials, ppy_by_horizon):
    """試驗集 [(horizon, annualized_sharpe)] → per-period SR list(逐 horizon 各自 ppy 轉)。
    ppy_by_horizon={h: ppy};缺 horizon 之 ppy → 該試驗略過(不猜、#15)。"""
    out = []
    for h, ann in trials:
        ppy = ppy_by_horizon.get(h)
        if ppy and ppy > 0 and ann is not None and np.isfinite(ann):
            out.append(float(ann) / np.sqrt(ppy))
    return out


def deflated_floor(net_series, ppy, trials_pp, n_trials):
    """cell 之 deflated 地板:net_series(per-period 序列)+ ppy + 試驗 per-period SR 集 + N → dict。

    reuse metrics.deflated_sharpe(per-period sr_obs + 真實 skew/kurt);另附 deflated_ann(haircut 換算年化
    展示值 = haircut_pp × √ppy,非另一次 deflation)。sr_pp/T 不足或 Var 算不出 → dsr=None(誠實)。
    回 {sr_pp, T, skew, kurt, sr_0, haircut, dsr, deflated_ann, n_trials, sr_var}。
    """
    sr_pp, T, sk, ku = per_period_stats(net_series)
    var = metrics.sharpe_trial_variance(trials_pp)
    if sr_pp is None or var is None:
        return {"sr_pp": sr_pp, "T": T, "skew": sk, "kurt": ku, "sr_0": None,
                "haircut": None, "dsr": None, "deflated_ann": None,
                "n_trials": n_trials, "sr_var": var}
    r = metrics.deflated_sharpe(sr_pp, T, n_trials=n_trials, sr_var=var, skew=sk, kurt=ku)
    haircut = r.get("haircut") if r else None
    return {"sr_pp": sr_pp, "T": T, "skew": sk, "kurt": ku,
            "sr_0": (r.get("sr_0") if r else None), "haircut": haircut,
            "dsr": (r.get("dsr") if r else None),
            "deflated_ann": (float(haircut * np.sqrt(ppy)) if haircut is not None else None),
            "n_trials": n_trials, "sr_var": var}


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # per_period_stats:已知 mean=0.2/sd=0.1(ddof=1) → sr_pp=2.0、T=3
    sr, T, _sk, _ku = per_period_stats([0.1, 0.2, 0.3])
    chk("per_period_stats 基本 sr_pp≈2.0/T=3", sr is not None and abs(sr - 2.0) < 1e-9 and T == 3)
    # None/NaN 一律濾除,不影響結果
    sr2, T2, _, _ = per_period_stats([0.1, None, 0.2, float("nan"), 0.3])
    chk("per_period_stats 濾 None/NaN 後同基本", sr2 is not None and abs(sr2 - 2.0) < 1e-9 and T2 == 3)
    # <2 有限值 → (None, n, 0.0, 3.0)(無從算)
    chk("per_period_stats <2 值 → None/0.0/3.0", per_period_stats([1.0]) == (None, 1, 0.0, 3.0))
    # sd=0(常數序列)→ sr_pp None、T 仍計
    sr3, T3, _, _ = per_period_stats([5.0, 5.0, 5.0])
    chk("per_period_stats 常數(sd=0) → sr_pp None", sr3 is None and T3 == 3)
    # trials_per_period:逐 horizon 各自 ppy 轉 per-period;缺 ppy/None 之試驗略過(#15)
    tp = trials_per_period([(1, 10.0), (2, None), (3, 5.0), (4, 8.0)], {1: 100, 3: 25})
    chk("trials_per_period 轉換+略過缺 ppy/None", tp == [1.0, 1.0])
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.evaluation.deflation --selftest;免 DB 免 API)")
