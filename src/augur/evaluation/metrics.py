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
