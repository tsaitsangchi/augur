"""BULL5-v1 — 長線多頭 × 5 日回跌（純函式；探針與自測共用）。

🎯 這支在做什麼（白話）：現價高於 10／20／40／60／90／120／240 日前收，
   且近 5 日為負。不是累積％遞減、不是均線排列、不是 UP-PULL 進場。
   過閘 ≠ 可交易。做空鏡像 ≠ 可空。

執行指令矩陣（本檔=library #18；自測免 DB 免 API）:
  python -m augur.evaluation.bull5
  python -m augur.evaluation.bull5 --selftest
"""
from __future__ import annotations

from typing import Mapping, Optional

from augur.evaluation import uptrend_pullback as up

VERSION = "BULL5-v1"
H_STACK = (10, 20, 40, 60, 90, 120, 240)
LONG_TAG = "長線多頭、5日回跌；≠可交易"
SHORT_TAG = "長線空頭、5日反彈；≠可空"


def _pos(rets: Mapping[int, float], h: int) -> bool:
    v = rets.get(h)
    return v is not None and float(v) > 0


def _neg(rets: Mapping[int, float], h: int) -> bool:
    v = rets.get(h)
    return v is not None and float(v) < 0


def gate_long_a(rets: Mapping[int, float]) -> bool:
    """B5-A：H10…H240 全＞0。"""
    return all(_pos(rets, h) for h in H_STACK)


def gate_long_b(rets: Mapping[int, float]) -> bool:
    """B5-B：H5＜0。"""
    return _neg(rets, 5)


def gate_short_a(rets: Mapping[int, float]) -> bool:
    """B5-A′：H10…H240 全＜0。"""
    return all(_neg(rets, h) for h in H_STACK)


def gate_short_b(rets: Mapping[int, float]) -> bool:
    """B5-B′：H5＞0。"""
    return _pos(rets, 5)


def is_bull5_long(rets: Mapping[int, float]) -> bool:
    return gate_long_a(rets) and gate_long_b(rets)


def is_bull5_short(rets: Mapping[int, float]) -> bool:
    return gate_short_a(rets) and gate_short_b(rets)


def long_sort_key(sid: str, rets: Mapping[int, float]) -> tuple:
    """主鍵長窗均勻降序、次鍵 H5 升序（跌深在前）、三鍵代號。"""
    mu = up.mean_rank_ret(rets)
    mu_s = float(mu) if mu is not None else float("-inf")
    h5 = rets.get(5)
    h5_s = float(h5) if h5 is not None else float("inf")
    return (-mu_s, h5_s, str(sid))


def short_sort_key(sid: str, rets: Mapping[int, float]) -> tuple:
    """主鍵長窗均勻升序、次鍵 H5 降序、三鍵代號。"""
    mu = up.mean_rank_ret(rets)
    mu_s = float(mu) if mu is not None else float("inf")
    h5 = rets.get(5)
    h5_s = float(h5) if h5 is not None else float("-inf")
    return (mu_s, -h5_s, str(sid))


def long_tag() -> str:
    return LONG_TAG


def short_tag() -> str:
    return SHORT_TAG


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("VERSION", VERSION == "BULL5-v1")
    chk("H_STACK", H_STACK == (10, 20, 40, 60, 90, 120, 240))
    good = {5: -0.02, 10: 0.03, 20: 0.04, 40: 0.05, 60: 0.10, 90: 0.12, 120: 0.15, 240: 0.20}
    chk("做多過", is_bull5_long(good))
    chk("做多拒 H5≥0", not is_bull5_long({**good, 5: 0.01}))
    chk("做多拒 H5=0", not is_bull5_long({**good, 5: 0.0}))
    chk("做多拒 H10≤0", not is_bull5_long({**good, 10: -0.01}))
    chk("不做 UP-PULL L-B（H10 仍正）", not up.gate_long_b(good))
    dn = up.negate_rets(good)
    chk("空方鏡像", is_bull5_short(dn) and not is_bull5_long(dn))
    deep = {**good, 5: -0.10}
    chk("同長窗 H5 更深排前", long_sort_key("2376", deep) < long_sort_key("2362", good))
    strong = {**good, 240: 0.40}
    chk("長窗更強排前", long_sort_key("2484", strong) < long_sort_key("6605", good))
    chk("標不含可當進場條件", "可當進場條件" not in LONG_TAG and "可當進場條件" not in SHORT_TAG)
    chk("標含 ≠可交易", "≠可交易" in LONG_TAG)
    chk("標含 ≠可空", "≠可空" in SHORT_TAG)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測: python -m augur.evaluation.bull5 --selftest；免 DB 免 API)")
