"""augur purged walk-forward 切分 — 防洩漏的訓練/測試折產生器（evaluation 層、#8 紅線）。

🎯 這支在做什麼（白話）：把一串 as-of 面板日切成「逐折前進」的 train/test——
- **expanding**：每個 test panel 的 train = 它**之前**的所有 panel（時序前進、test 永不回流調參）。
- **purge + embargo**（#8）：train 與 test 之間挖掉 `embargo` 個 panel，避免 test 的 label 窗（H 交易日後向）
  與最後幾個 train panel 的特徵/標籤時間重疊（洩漏未來）。embargo 須 ≥ label 窗 + 特徵最大滯後。

只產「哪些 panel 當 train、哪個 panel 當 test」之索引切分；**不碰資料、不訓練、不算 label**（純切分邏輯）。
label 由 label 層造、特徵由 feature 層造，本層只決定時間切分的防洩漏邊界。

#8 anti-leakage：expanding（不用未來 panel 訓練）+ purge/embargo（剔 label 窗重疊）+ test 不回流。
#12 SSOT：切分邏輯唯一住此、所有 validator import（折定義一致才可比）。
守 #8（anti-leakage：expanding + purge/embargo + test 不回流）· #12（SSOT：切分邏輯唯一住此）。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.evaluation.walkforward              # 印用途+公開入口（唯讀）
  python -m augur.evaluation.walkforward --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations


_FEATURE_LAG_TD = 62     # 特徵最大滯後(年報法定 90 日 ≈ 62 交易日);(a) 下界 = h + 此(belt-and-suspenders,拍板 2026-07-06)
_H_FORBIDDEN = 252      # H≥此禁入(結構性洩漏,拍板2);walkforward 層 gate 擋 evaluation 直呼旁路(train_ranker CLI gate 外之第二道)


def embargo_panels_for(panel_dates, h_days, *, feature_lag_td=_FEATURE_LAG_TD):
    """(a) 下界之 panel 數**估算**(無真實日曆時的退回路,**非保證、僅開發近似**)。

    目標下界 = `h_days + feature_lag_td` 交易日(label 窗 h ＋ 特徵最大滯後,#8);
    以 panel 間距中位(~0.69×日曆日估)算 embargo = ceil(目標 / 間距),至少 1。
    **保證下界請走 `splits(..., calendar=)`**——本函式非保證(splits 標 guaranteed=False)。
    """
    pd = sorted(panel_dates)
    target_td = max(1, h_days + feature_lag_td)
    if len(pd) < 2:
        return 1
    gaps = sorted((pd[i + 1] - pd[i]).days for i in range(len(pd) - 1))
    median_td = max(1, round(gaps[len(gaps) // 2] * 0.69))   # 日曆日→交易日估
    return max(1, -(-target_td // median_td))                # ceil(目標 / 間距)


def splits(panel_dates, h_days, *, embargo=None, min_train=1,
           calendar=None, feature_lag_td=_FEATURE_LAG_TD):
    """expanding purged walk-forward 折 → list of {train, test, embargo, guaranteed}(#8 紅線)。

    embargo **保證下界**(拍板 2026-07-06 口徑 a)= `h_days + feature_lag_td` **交易日**(label 窗 ＋ 特徵最大滯後):
    - `calendar`(排序之全交易日序列,如 `label.full_calendar(conn)`)給定 → **逐折保證**:每折自 train 尾往回加 panel、
      直到「train 尾 panel 距 test 之**實際交易日** ≥ 目標」,不足自動加(`guaranteed=True`);唯一非估算路。
    - 無 calendar → 退回 `embargo_panels_for` 單一估算(`guaranteed=False`、標明、僅開發用,勿作終判)。
    - `embargo` 明給 → 用該值(不自動、guaranteed=False)。
    **H≥252 禁入**(拍板2、結構性洩漏)→ raise(擋 evaluation 直呼旁路)。
    """
    if h_days >= _H_FORBIDDEN:
        raise ValueError(f"H={h_days} 禁入(≥{_H_FORBIDDEN}、結構性洩漏,拍板2);walkforward 拒切分")
    pd = sorted(panel_dates)
    target_td = max(1, h_days + feature_lag_td)
    folds = []
    if embargo is None and calendar is not None:               # ── 保證下界路(逐折、真實交易日)──
        import bisect
        cal = sorted(set(calendar))
        pos = [bisect.bisect_left(cal, d) for d in pd]         # panel → 交易日索引
        for i in range(len(pd)):
            emb = 1
            while i - emb - 1 >= 0 and (pos[i] - pos[i - emb - 1]) < target_td:
                emb += 1                                        # train 尾距 test 未達目標 → 再加一 panel
            train = pd[: i - emb] if i - emb > 0 else []
            if len(train) >= min_train:
                folds.append({"train": train, "test": pd[i], "embargo": emb, "guaranteed": True})
        return folds
    emb = embargo if embargo is not None else embargo_panels_for(pd, h_days, feature_lag_td=feature_lag_td)
    for i in range(len(pd)):
        train = pd[: i - emb] if i - emb > 0 else []            # 估算路(非保證):單一 emb
        if len(train) >= min_train:
            folds.append({"train": train, "test": pd[i], "embargo": emb, "guaranteed": False})
    return folds


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：合成 panel 日紅綠測 embargo_panels_for/splits——
    固化 #8 三不變式（H≥252 禁入、expanding 訓練皆早於 test、train∩test=∅）為回歸鎖。"""
    from datetime import date, timedelta
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    base = date(2024, 1, 1)
    pd6 = [base + timedelta(days=30 * i) for i in range(6)]

    # (1) H≥252 禁入(結構性洩漏,拍板2)→ raise(擋 evaluation 直呼旁路)
    try:
        splits(pd6, _H_FORBIDDEN)
        chk("H≥252 禁入 raise", False)
    except ValueError:
        chk("H≥252 禁入 raise", True)

    # (2) embargo_panels_for 恆 ≥1、回整數(退回估算路下界)
    e = embargo_panels_for(pd6, 5)
    chk("embargo_panels_for≥1 且為 int", isinstance(e, int) and e >= 1)

    # (3) 估算路(明給 embargo):expanding — 每折 train 皆嚴格早於 test 且不含 test(#8 不回流)
    fs = splits(pd6, 5, embargo=2, min_train=1)
    exp_ok = all(f["train"] and all(t < f["test"] for t in f["train"])
                 and f["test"] not in f["train"] for f in fs)
    chk("splits expanding: train 全早於 test 且 test 不回流", bool(fs) and exp_ok)
    chk("splits 估算路 guaranteed=False", all(f["guaranteed"] is False for f in fs))

    # (4) train 為 pd[:i-emb] 前綴(expanding 累積):後折 train 涵蓋前折 train
    trains = [len(f["train"]) for f in fs]
    chk("expanding: train 長度單調不減", trains == sorted(trains))

    # (5) 保證下界路(給 calendar):逐折 guaranteed=True、embargo≥1、仍守 expanding
    cal = [base + timedelta(days=i) for i in range(200)]   # 連續交易日序列
    gs = splits(pd6, 5, calendar=cal, min_train=1)
    guar_ok = all(f["guaranteed"] is True and f["embargo"] >= 1
                  and all(t < f["test"] for t in f["train"]) for f in gs)
    chk("calendar 保證路 guaranteed=True 且守 expanding", bool(gs) and guar_ok)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("入口:embargo_panels_for / splits")
    print("(自測:python -m augur.evaluation.walkforward --selftest;免 DB 免 API)")
