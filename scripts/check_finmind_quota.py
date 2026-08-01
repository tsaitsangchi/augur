#!/usr/bin/env python3
"""🎯 讀一次 FinMind 權威額度錶並留一行紀錄——讓「配額現況」每交易日有確定性可見點。

守原則 #24（配額一律問錶不本地推算——rolling 視窗＋未知成分，本地計數必錯）、
#25（讀錶=最小單位、非資料 API 放量；/user_info 讀錶不自計額度）、#28（本地零 usage）。

起因（登錄冊 E4，2026-08-01）：`/user_info` 只在 sync 迴圈內每 120 call 附帶讀
（`finmind.py:88-121`），**無 sync 的日子配額狀態＝UNKNOWN**——人與日誌皆無確定性可見點，
出問題時只能事後猜。本支＝每交易日 arena 出單前讀一次錶、印一行、非零頭寸即警示。

接入點＝既有 arena cron 行**前綴一步**（不新增 cron 條目＝不增自動鏈長，#26 OCV C 分量不動）。

執行指令矩陣
------------
    python3 scripts/check_finmind_quota.py            # 無參數＝--read（讀錶一次，印一行）
    python3 scripts/check_finmind_quota.py --read     # 同上；headroom<0 時 exit 1（供管線可見）
    python3 scripts/check_finmind_quota.py --selftest # 紅綠自測（免 API：判定邏輯純函式驗證）
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys

import _bootstrap  # noqa: F401


def quota_line(count, limit, headroom_reserve, now_iso):
    """讀數 → (一行紀錄, exit_code)。**純函式**——自測餵真形狀輸入、免 API。

    exit 1 之判準＝剩餘 headroom（limit−count−保留頭寸）< 0：錶已進入保留區，
    後續放量會撞 402/403。非零退出讓前綴管線（`check && pipeline`）自然短路。
    """
    remain = limit - count - headroom_reserve
    line = (f"{now_iso} finmind_quota {count}/{limit} "
            f"headroom={limit - count} reserve={headroom_reserve} "
            + ("OK" if remain >= 0 else "**LOW——保留區已破,放量將撞限**"))
    return line, (0 if remain >= 0 else 1)


def _read() -> int:
    from augur.ingestion.finmind import QUOTA_HEADROOM, _user_quota
    try:
        count, limit = _user_quota()
    except Exception as e:  # noqa: BLE001
        # 讀錶失敗≠配額滿：誠實印失敗、exit 2（與 LOW 的 1 區分），不猜數字（#9）。
        print(f"{dt.datetime.now().astimezone().isoformat(timespec='seconds')} "
              f"finmind_quota READ_FAIL {type(e).__name__}: {e}")
        return 2
    line, rc = quota_line(count, limit, QUOTA_HEADROOM,
                          dt.datetime.now().astimezone().isoformat(timespec="seconds"))
    print(line)
    return rc


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # 純函式餵真形狀輸入，紅綠雙向（禁字面斷言）
    l1, r1 = quota_line(100, 6000, 200, "T")
    chk("餘裕充足 ⇒ OK 且 exit 0", r1 == 0 and "OK" in l1)
    l2, r2 = quota_line(5900, 6000, 200, "T")
    chk("進入保留區 ⇒ LOW 且 exit 1", r2 == 1 and "LOW" in l2)
    l3, r3 = quota_line(5800, 6000, 200, "T")
    chk("恰在保留線上（remain=0）⇒ 仍 OK（>=0 含界）", r3 == 0)
    chk("行內含原始讀數（可事後對帳,#10）", "5900/6000" in l2)
    l4, r4 = quota_line(6100, 6000, 200, "T")
    chk("錶超限（count>limit）⇒ LOW 非崩潰", r4 == 1)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="FinMind 權威額度錶讀取（每交易日一行）")
    ap.add_argument("--read", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    return _read()


if __name__ == "__main__":
    sys.exit(main())
