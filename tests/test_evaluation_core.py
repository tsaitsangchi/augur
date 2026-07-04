"""evaluation 核心純函數回歸測試(不打 API、不依賴 DB;clean-room)。

覆蓋合規稽核 執14(2026-07-04)點名之最小防線:
- metrics.effective_t_hac:已知序列手推值 / AR(1) 正自相關收縮 t(HAC<iid、審查 G8)/ 白噪音近等 / n<3 → None
- label._entry_exit:t+1 進場口徑——交易日與非交易日 panel 進場日一致(執2 修後語意,不漂移 t+2)
- walkforward.splits:train/test 不重疊 + embargo gap + expanding(#8 anti-leakage)
守原則 #8 #15。
"""
import datetime as dt

import numpy as np
import pytest

from augur.evaluation import label, metrics, walkforward


# ── metrics.effective_t_hac ──
def test_effective_t_hac_known_series_lag1():
    # 手推(lag=1, Bartlett):mean=0.18, γ0=0.0056, γ1=0.00032,
    # LRV=0.0056+2·0.5·0.00032=0.00592, t=0.18/√(0.00592/5)=5.231143743471868
    t = metrics.effective_t_hac([0.1, 0.2, 0.3, 0.2, 0.1], lag=1)
    assert t == pytest.approx(5.231143743471868, rel=1e-9)


def test_effective_t_hac_shrinks_under_positive_autocorrelation():
    # AR(1) φ=0.6 正自相關 IC 序列:HAC t 必須 < iid effective_t(重疊窗高估、G8)
    rng = np.random.default_rng(42)
    ics = [0.05]
    for _ in range(199):
        ics.append(0.6 * ics[-1] + 0.02 + rng.normal(0, 0.05))
    iid_t = metrics.summarize(ics)["effective_t"]
    hac_t = metrics.effective_t_hac(ics)
    assert hac_t is not None and iid_t is not None
    assert hac_t < iid_t


def test_effective_t_hac_close_to_iid_under_white_noise():
    # 白噪音(無自相關):HAC 與 iid 近等(僅取樣誤差)
    rng = np.random.default_rng(7)
    ics = (0.03 + rng.normal(0, 0.05, 200)).tolist()
    iid_t = metrics.summarize(ics)["effective_t"]
    hac_t = metrics.effective_t_hac(ics)
    assert hac_t == pytest.approx(iid_t, rel=0.15)


def test_effective_t_hac_n_too_small_returns_none():
    assert metrics.effective_t_hac([0.1, 0.2]) is None


# ── label._entry_exit(t+1 口徑、執2 修後) ──
# 全市場交易日曆(平日):2024-01-02(二)~2024-01-12(五),無 1/6、1/7(週末)
_CAL = [dt.date(2024, 1, d) for d in (2, 3, 4, 5, 8, 9, 10, 11, 12)]


def _filtered(panel_date):
    # 鏡射 forward_returns/_calendar 之過濾口徑:d > panel_date(嚴格大於)
    return [d for d in _CAL if d > panel_date]


def test_entry_exit_trading_day_panel():
    # panel_date=1/5(五、交易日)→ entry=次一交易日 1/8、exit=cal[3]=1/11
    entry, exit_ = label._entry_exit(_filtered(dt.date(2024, 1, 5)), 3)
    assert entry == dt.date(2024, 1, 8)
    assert exit_ == dt.date(2024, 1, 11)


def test_entry_exit_non_trading_day_panel_no_drift():
    # panel_date=1/6(六、非交易日)→ entry 同為 1/8(真 t+1),不漂移為 t+2(1/9)
    entry, exit_ = label._entry_exit(_filtered(dt.date(2024, 1, 6)), 3)
    assert entry == dt.date(2024, 1, 8)
    assert exit_ == dt.date(2024, 1, 11)
    # 兩情境口徑一致(執2 修後不變式)
    assert (entry, exit_) == label._entry_exit(_filtered(dt.date(2024, 1, 5)), 3)


def test_entry_exit_insufficient_calendar_returns_none():
    # 湊不到 1+h 個交易日 → (None, None)(#8 不外推)
    assert label._entry_exit(_filtered(dt.date(2024, 1, 10)), 3) == (None, None)


# ── walkforward.splits(#8 不重疊) ──
_PANELS = [dt.date(2024, m, 28) for m in range(1, 11)]   # 10 個月度 panel


def test_splits_no_overlap_and_embargo_gap():
    emb = 2
    folds = walkforward.splits(_PANELS, 20, embargo=emb, min_train=1)
    assert folds                                          # 至少一折
    for f in folds:
        assert f["test"] not in f["train"]                # test 永不入 train
        assert all(d < f["test"] for d in f["train"])     # train 全在 test 之前
        # embargo gap:最後一個 train panel 與 test 間恰隔 emb 個 panel
        gap = _PANELS.index(f["test"]) - _PANELS.index(f["train"][-1]) - 1
        assert gap == emb


def test_splits_expanding_train():
    folds = walkforward.splits(_PANELS, 20, embargo=1, min_train=1)
    for a, b in zip(folds, folds[1:]):
        assert set(a["train"]) < set(b["train"])          # 逐折 expanding(嚴格擴張)
        assert a["test"] < b["test"]                      # test 時序前進
