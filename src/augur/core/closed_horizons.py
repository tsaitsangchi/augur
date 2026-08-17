"""v1 方向／截面 H 軌作業封閉集（2026-08-16：另開 H10；H90 取代 H82 已刪；H5＝2026-08-14）。

🎯 這支在做什麼（白話）：所有**新訓／出單／日更覆蓋**的 H 窗只准這一組。
   5＝5 個交易日（≠ 日頻 D 軌 k=5）；10＝10 個交易日（≠ KH10）；90＝90 個交易日。
   庫內 H82 已刪；CHECK 不准 82。
   凍結家族（v2 K=4／arena／A3 threelens）之 H82 **假說配方仍留在代碼**（不改 SHA）。

執行指令矩陣（本檔=library；自測免 DB）:
  python -m augur.core.closed_horizons
"""
from __future__ import annotations

# v1 作業閉集。順序固定，供殼／覆蓋探測對位。
H_TRACK = (5, 10, 20, 40, 60, 90, 120, 240)

# DirStackM 月頻相對分位；H120 不在 monthly ranks。
H_MONTHLY_RANKS = (5, 10, 20, 40, 60, 90, 240)

# DDL 准許集＝作業閉集（不含 82）。
CHECK_ANY = H_TRACK

# 日曆日近似（交易日 × 365/252 四捨五入；A-27 呈現偏差推導）。
CAL_DAYS = {
    5: 7,
    10: 14,
    20: 29,
    40: 58,
    60: 87,
    90: 131,
    120: 174,
    240: 348,
}

# 非重疊 n ≈ 213 × 20 / h（H20 錨 213）。
NONOVERLAP_N = {
    5: 852,
    10: 426,
    20: 213,
    40: 106,
    60: 71,
    90: 47,
    120: 35,
    240: 17,
}


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
        if not cond:
            ok = False

    print("[closed_horizons selftest]")
    chk("H_TRACK 長度 8", len(H_TRACK) == 8)
    chk("含 5、10 與 90", 5 in H_TRACK and 10 in H_TRACK and 90 in H_TRACK)
    chk("不含 82", 82 not in H_TRACK)
    chk("月頻含 5／10 無 82 無 120", H_MONTHLY_RANKS == (5, 10, 20, 40, 60, 90, 240))
    chk("CHECK=H_TRACK 不准 82", CHECK_ANY == H_TRACK and 82 not in CHECK_ANY)
    chk("CAL_DAYS[10]=14", CAL_DAYS[10] == 14 and CAL_DAYS[5] == 7 and 82 not in CAL_DAYS)
    chk("NONOVERLAP_N[10]=426", NONOVERLAP_N[10] == 426 and NONOVERLAP_N[5] == 852 and 82 not in NONOVERLAP_N)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
