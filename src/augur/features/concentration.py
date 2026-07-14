"""augur 量能集中度特徵 — 八二法則「分布形狀」鏡頭之存活軸(P3 量能時間集中)。

🎯 這支在做什麼(白話):八二法則的本質不是 0.8/0.2,而是「分布有多不均」。對每股、as-of 面板日 t,
把 rolling 窗內**日成交量分布**用 cutoff-free 泛函量成「集中度」:量集中少數日(事件/主力進出)vs 均勻吸納。
- `volume_gini_{20,60}d`:日量分布 Gini(不均度)
- `volume_max_share_{20,60}d`:最大單日量佔窗內總量(max-share)

**提拔複核結論(2026-06-27、過第4道關卡)**:八二六軸中**僅 P3 量能集中存活**(as-of HAC-t |3.4-4.5|、多因子增量正);
P1 持股集中(holding Gini/HHI/熵)**與既有 `top_holders_pct` 共線 +0.97、冗餘淘汰**;P2 資金流集中、P4 報酬集中
(skew/kurt)**單因子弱淘汰**。淘汰者之探索碼見 git 史 + `reports/augur_pareto_principle_research_20260627.md`。

思想可入、數字不回流(#9/#16):禁 0.8/0.2、decile 切點;只用連續泛函 + calendar 視窗慣例。anti-leakage(#8):
只用 ≤t 後向窗。source-pure(#1):算不出(窗不足/零變異)→ 不含該 key(缺列、不補)。型別 #5。

守 #1 · #8 · #9(cutoff-free 泛函) · #5 · 八二法則設計六軸之 P3(存活軸)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.concentration              # 印用途+公開入口（唯讀）
  python -m augur.features.concentration --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import numpy as np


def _gini(arr):
    """Gini 不均度(0=全均 … →1=極端集中);連續、無切點。負值/空/零和 → None。"""
    a = np.asarray([x for x in arr if x is not None and np.isfinite(x)], dtype=float)
    a = a[a >= 0]
    if a.size < 2 or a.sum() <= 0:
        return None
    a = np.sort(a)
    n = a.size
    idx = np.arange(1, n + 1)
    return float((2 * (idx * a).sum()) / (n * a.sum()) - (n + 1) / n)


def _max_share(arr):
    """最大單一貢獻者佔比 max/Σ(連續泛函、非「前 N」);無切點。零和/空 → None。"""
    a = np.asarray([x for x in arr if x is not None and np.isfinite(x)], dtype=float)
    a = a[a >= 0]
    s = a.sum()
    return float(a.max() / s) if a.size >= 2 and s > 0 else None


def compute_concentration_features(price_df):
    """八二 P3 量能集中度(用 panel 已抓之還原價 df、無需重查)→ {feature: value};算不出缺列(#1)。"""
    if price_df is None or not len(price_df):
        return {}
    out = {}
    vol = price_df["volume"].astype(float).to_numpy()
    for w in (20, 60):
        if len(vol) >= w:
            seg = vol[-w:]
            g, ms = _gini(seg), _max_share(seg)
            if g is not None:
                out[f"volume_gini_{w}d"] = g
            if ms is not None:
                out[f"volume_max_share_{w}d"] = ms
    return {k: float(v) for k, v in out.items() if v is not None and np.isfinite(v)}


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    import pandas as pd
    # _gini:全均→0、集中→高、不足/零和→None
    chk("gini 全均→0", abs(_gini([5, 5, 5, 5])) < 1e-9)
    chk("gini 集中→0.75", abs(_gini([0, 0, 0, 100]) - 0.75) < 1e-9)
    chk("gini 單元素→None", _gini([5]) is None)
    chk("gini 零和→None", _gini([0, 0]) is None)
    # _max_share:均分→1/n、獨佔→1、不足→None
    chk("max_share 均分→0.25", abs(_max_share([1, 1, 1, 1]) - 0.25) < 1e-9)
    chk("max_share 獨佔→1", abs(_max_share([0, 0, 0, 10]) - 1.0) < 1e-9)
    chk("max_share 單元素→None", _max_share([9]) is None)
    # compute:None/短窗→{}、足窗→四鍵齊備
    chk("compute None→{}", compute_concentration_features(None) == {})
    chk("compute 短窗→{}", compute_concentration_features(pd.DataFrame({"volume": [1.0] * 10})) == {})
    full = compute_concentration_features(pd.DataFrame({"volume": [1.0] * 60}))
    chk("compute 足窗→四鍵", set(full) == {
        "volume_gini_20d", "volume_gini_60d", "volume_max_share_20d", "volume_max_share_60d"})
    chk("compute 全均量→gini 0", abs(full.get("volume_gini_20d", 9)) < 1e-9)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.features.concentration --selftest;免 DB 免 API)")
