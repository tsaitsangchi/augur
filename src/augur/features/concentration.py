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
