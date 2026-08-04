"""augur 序列窗張量 — 把既有日頻 raw 對齊面板，reshape 成 LSTM/Transformer 可吃的 (stocks, window, channels) 張量。

🎯 這支在做什麼（白話）：S3 組 12「序列窗」之契約——**不新增表**，只在讀取時把
`audit.field_correlation.build_stock_panel`（既有的單股每日對齊面板，合併 ~12 張 raw 表）依 as-of
切到 `window_len` 天、多股疊成張量。序列窗＝既有 raw 之重排列（零新資訊），materialize 一張新表只會
與 raw 重複儲存、每次 as-of 前進就要重建——故序列窗契約住在這支 library、不住 DB（#12 SSOT）。

歷史不足 `window_len` 之股票**排除**（不 zero-fill、不前補，#1）；缺值格保留 NaN，由訓練端決定丟棄
或遮罩。純函式 `stack_windows` 只吃「已經抓好的逐股面板 dict」（零 DB）——`build_sequence_tensor`
才是接 DB 的薄殼，負責逐股呼叫 `build_stock_panel`。

邊界：唯讀；不寫庫；不訓練；不是 `feature_values` 之替代品——序列窗以 `TaiwanStockPriceAdj`／籌碼
raw 表為底（日頻），與 `feature_values`（月頻 canonical 特徵）為不同資料層，不可混用。

守 #1（缺值不補）· #8（as-of 篩、不看未來）· #12（不重複造表）。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.sequence              # 印用途+公開入口（唯讀）
  python -m augur.features.sequence --selftest   # 純紅綠自測（零 IO；合成面板餵 stack_windows）
"""
from __future__ import annotations

import datetime as _dt

import numpy as np
import pandas as pd

from augur.audit.field_correlation import build_stock_panel


def stack_windows(panels: dict, as_of, window_len: int, channels: list | None = None):
    """純函式：逐股面板 dict（stock_id -> DataFrame|None，index=date）→ 疊成張量。

    - 篩 `index <= as_of`（不看未來，#8）；不足 `window_len` 列之股票排除（不補值，#1）。
    - `channels` 為 None 時，取第一支合格股面板之 `sorted(columns)` 為準（各股面板欄位集恆一致，
      因 `build_stock_panel` 對每股皆 join 相同 `_SRC` 欄位表，缺源只會是 NaN 而非缺欄）。
    - 缺值格保留 `NaN`；**不**前補、不 zero-fill。

    回傳 `(tensor, ok_stock_ids, excluded_stock_ids, channel_names)`：
      tensor.shape == (len(ok_stock_ids), window_len, len(channel_names))；
      ok_stock_ids 依字母序（可重現、非插入序）。
    """
    ok_ids: list[str] = []
    mats: list[np.ndarray] = []
    excluded: list[str] = []
    channel_names = list(channels) if channels else None

    for sid in sorted(panels):
        df = panels[sid]
        if df is None or len(df) == 0:
            excluded.append(sid)
            continue
        sub = df[df.index <= as_of]
        if len(sub) < window_len:
            excluded.append(sid)
            continue
        sub = sub.tail(window_len)
        if channel_names is None:
            channel_names = sorted(sub.columns)
        missing = [c for c in channel_names if c not in sub.columns]
        if missing:
            raise ValueError(f"channel(s) not present in panel for {sid}: {missing}")
        mats.append(sub[channel_names].to_numpy(dtype=float))
        ok_ids.append(sid)

    if not mats:
        return np.zeros((0, window_len, len(channel_names or []))), [], excluded, (channel_names or [])
    return np.stack(mats, axis=0), ok_ids, excluded, channel_names


def build_sequence_tensor(conn, stock_ids, as_of, window_len: int, channels: list | None = None):
    """DB 薄殼：逐股呼叫既有 `build_stock_panel` 取面板，交給純函式 `stack_windows` 處理。

    `as_of` 可為 `datetime.date` 或 ISO 字串；內部正規化為 `date`。
    """
    if isinstance(as_of, str):
        as_of = _dt.date.fromisoformat(as_of)
    panels = {sid: build_stock_panel(conn, sid) for sid in stock_ids}
    return stack_windows(panels, as_of, window_len, channels)


def coverage_report(panels_or_conn, stock_ids_or_none, as_of, window_lens, channels=None, *, from_db=False):
    """多個 window_len 之覆蓋率彙總（唯讀報告用）：回 {window_len: {"ok": n, "excluded": n, "nan_rate": {...}}}。

    `from_db=True` 時 `panels_or_conn` 為 DB connection、`stock_ids_or_none` 為股票清單；
    否則 `panels_or_conn` 直接是已抓好之 panels dict（零 DB，供 selftest／單元測試用）。
    """
    if from_db:
        panels = {sid: build_stock_panel(panels_or_conn, sid) for sid in stock_ids_or_none}
    else:
        panels = panels_or_conn
    out = {}
    for wl in window_lens:
        tensor, ok_ids, excluded, chans = stack_windows(panels, as_of, wl, channels)
        nan_rate = {}
        if tensor.size:
            for i, c in enumerate(chans):
                col = tensor[:, :, i]
                nan_rate[c] = float(np.isnan(col).mean())
        out[wl] = {"ok": len(ok_ids), "excluded": len(excluded),
                    "excluded_sample": excluded[:10], "channels": chans, "nan_rate": nan_rate}
    return out


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    dates = pd.date_range("2026-01-01", periods=10, freq="D").date
    full = pd.DataFrame({"close": range(10), "vol": range(10, 20)}, index=dates)
    short = pd.DataFrame({"close": range(3), "vol": range(3)}, index=dates[:3])
    with_nan = pd.DataFrame({"close": [1.0, np.nan, 3.0], "vol": [1.0, 2.0, np.nan]}, index=dates[:3])

    panels = {"A": full, "B": short, "C": None}
    tensor, ok_ids, excluded, chans = stack_windows(panels, dates[-1], window_len=5)
    chk("足窗股入選（A）", "A" in ok_ids)
    chk("不足窗股排除（B）", "B" in excluded)
    chk("None 面板排除（C）", "C" in excluded)
    chk("tensor shape 對齊 ok_ids×window×channels", tensor.shape == (1, 5, 2))
    chk("channel_names 由資料判定（非硬編）", chans == sorted(full.columns))

    # as-of 邊界：只用 <= as_of 之列，不看未來（#8 下游絆線——真的餵「更早的 as_of」驗證視窗會變短而排除）
    tensor2, ok2, excl2, _ = stack_windows({"A": full}, dates[2], window_len=5)
    chk("as_of 太早（僅 3 列可用）→ 不足窗排除（真絆線，非拆窗口邏輯）", "A" in excl2 and ok2 == [])

    # 缺值不補（#1）：NaN 格必須原樣保留，不能被悄悄填掉
    tensor3, ok3, _, chans3 = stack_windows({"D": with_nan}, dates[2], window_len=3)
    close_idx = chans3.index("close")
    chk("NaN 保留、未被補值（#1 下游絆線）",
        "D" in ok3 and np.isnan(tensor3[0, 1, close_idx]))

    # 缺 channel 明確報錯（非靜默排除該欄）
    try:
        stack_windows({"A": full}, dates[-1], window_len=5, channels=["close", "not_a_real_channel"])
        chk("要求不存在之 channel → 應報錯", False)
    except ValueError as e:
        chk("要求不存在之 channel → 報錯（fail loud，非靜默丟欄）", "not_a_real_channel" in str(e))

    # 空輸入邊界
    tensor4, ok4, excl4, chans4 = stack_windows({}, dates[-1], window_len=5)
    chk("空 panels → 空張量、shape 仍含 window_len", tensor4.shape == (0, 5, 0) and ok4 == [] and excl4 == [])

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.features.sequence --selftest;免 DB 免 API)")
    print("公開入口:stack_windows(純函式)／build_sequence_tensor(接 DB)／coverage_report(唯讀彙總)")
