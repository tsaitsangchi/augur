"""augur purged walk-forward 切分 — 防洩漏的訓練/測試折產生器（evaluation 層、#8 紅線）。

🎯 這支在做什麼（白話）：把一串 as-of 面板日切成「逐折前進」的 train/test——
- **expanding**：每個 test panel 的 train = 它**之前**的所有 panel（時序前進、test 永不回流調參）。
- **purge + embargo**（#8）：train 與 test 之間挖掉 `embargo` 個 panel，避免 test 的 label 窗（H 交易日後向）
  與最後幾個 train panel 的特徵/標籤時間重疊（洩漏未來）。embargo 須 ≥ label 窗 + 特徵最大滯後。

只產「哪些 panel 當 train、哪個 panel 當 test」之索引切分；**不碰資料、不訓練、不算 label**（純切分邏輯）。
label 由 label 層造、特徵由 feature 層造，本層只決定時間切分的防洩漏邊界。

#8 anti-leakage：expanding（不用未來 panel 訓練）+ purge/embargo（剔 label 窗重疊）+ test 不回流。
#12 SSOT：切分邏輯唯一住此、所有 validator import（折定義一致才可比）。
"""
from __future__ import annotations


def embargo_panels_for(panel_dates, h_days):
    """依 label 窗（h 交易日）+ panel 間距，算需挖掉幾個 panel 才不重疊（#8）。

    panel 間距（中位交易日數，~0.69×日曆日估）vs label 窗 h：embargo = ceil(h / 間距)，至少 1。
    例：季度 panel（~63 交易日間距）+ H=20 → embargo 1；+ H=252 → embargo 4（年 label 跨 4 季）。
    panel_dates < 2 → 0（無從估間距）。
    """
    pd = sorted(panel_dates)
    if len(pd) < 2:
        return 1
    gaps = [(pd[i + 1] - pd[i]).days for i in range(len(pd) - 1)]
    gaps.sort()
    median_cal = gaps[len(gaps) // 2]
    median_td = max(1, round(median_cal * 0.69))   # 日曆日→交易日估
    return max(1, -(-h_days // median_td))          # ceil(h / 間距)


def splits(panel_dates, h_days, *, embargo=None, min_train=1):
    """expanding purged walk-forward 折 → list of {train:[panel_dates], test:panel_date, embargo:int}。

    每個 test panel（自第 min_train+embargo 個起）：train = 它之前、剔掉最近 `embargo` 個 panel 的所有 panel。
    `embargo`=None → 自動 `embargo_panels_for`（依 h 與 panel 間距）。`min_train`：train 至少幾 panel 才成折。
    test 永不入 train（時序前進）；train 與 test 間 embargo gap（purge label 窗重疊，#8）。
    """
    pd = sorted(panel_dates)
    emb = embargo if embargo is not None else embargo_panels_for(pd, h_days)
    folds = []
    for i in range(len(pd)):
        train = pd[: i - emb] if i - emb > 0 else []        # test=pd[i]；剔最近 emb 個 panel（embargo gap）
        if len(train) >= min_train:
            folds.append({"train": train, "test": pd[i], "embargo": emb})
    return folds
