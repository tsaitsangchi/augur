"""MA-STACK-v1 做多均線排列＋均價壓縮（純函式；探針與自測共用）。

🎯 這支在做什麼（白話）：還原收盤 SMA5>SMA10>SMA20>SMA40>SMA60>SMA90>SMA120>SMA240
   （嚴格大於），且八條均價 (最高−最低)/最低 ≤limit（預設 10%，另有 20% 閘），才標可當進場條件。
   缺窗不編造。不是做多四閘、不是路徑％、不是可交易。

執行指令矩陣（本檔=library #18；自測免 DB 免 API）:
  python -m augur.evaluation.ma_stack
  python -m augur.evaluation.ma_stack --selftest
"""
from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from augur.evaluation.uptrend_pullback import RIDGE_THEN_PB_ENTRY

VERSION = "MA-STACK-v1"
MA_WINDOWS = (5, 10, 20, 40, 60, 90, 120, 240)
MA_SPREAD_MAX = 0.10  # (max-min)/min，含
MA_SPREAD_MAX_20 = 0.20
MA_STACK_WAIT = "未過均線閘，不是進場"
MA_STACK_ENTRY = RIDGE_THEN_PB_ENTRY


def sma_last(closes: Optional[Sequence[Optional[float]]], n: int) -> Optional[float]:
    """對齊序列末 n 點算術平均。不足、缺點、非正價 → None。"""
    if n <= 0 or closes is None or len(closes) < n:
        return None
    chunk = list(closes)[-n:]
    out = []
    for x in chunk:
        if x is None:
            return None
        v = float(x)
        if v <= 0:
            return None
        out.append(v)
    return sum(out) / n


def sma_map(
    closes: Optional[Sequence[Optional[float]]],
    windows: Sequence[int] = MA_WINDOWS,
) -> dict[str, Optional[float]]:
    return {str(n): sma_last(closes, int(n)) for n in windows}


def ma_strict_stack(
    smas: Optional[Mapping[str, Optional[float]]],
    windows: Sequence[int] = MA_WINDOWS,
) -> tuple[bool, str]:
    """SMA 短窗嚴格大於下一檔長窗。缺或非嚴格 → False。"""
    prev = None
    prev_h = None
    for h in windows:
        v = None if not smas else smas.get(str(h))
        if v is None:
            return False, "缺 SMA%s" % h
        x = float(v)
        if prev is not None and not (prev > x):
            return False, "SMA%s≯SMA%s" % (prev_h, h)
        prev, prev_h = x, h
    return True, ""


def ma_spread_within(
    smas: Optional[Mapping[str, Optional[float]]],
    limit: float = MA_SPREAD_MAX,
    windows: Sequence[int] = MA_WINDOWS,
) -> tuple[bool, Optional[float], str]:
    """八條均價皆有且 (max−min)/min ≤ limit。spread 為比率（0.10＝10%）。"""
    vals = []
    missing = []
    for h in windows:
        v = None if not smas else smas.get(str(h))
        if v is None:
            missing.append("SMA%s" % h)
            continue
        x = float(v)
        if x <= 0:
            missing.append("SMA%s" % h)
            continue
        vals.append(x)
    if missing:
        return False, None, "缺 " + "／".join(missing)
    mn = min(vals)
    mx = max(vals)
    spread = (mx - mn) / mn
    lim = float(limit)
    if spread > lim:
        return False, spread, "均價差 %.2f%% 逾 ±%s%%" % (
            spread * 100.0,
            str(int(lim * 100)) if lim * 100 == int(lim * 100) else str(lim * 100),
        )
    return True, spread, ""


def apply_ma_stack_row(
    row: Mapping[str, Any],
    closes: Optional[Sequence[Optional[float]]],
    *,
    limit: float = MA_SPREAD_MAX,
) -> dict:
    """池列不剔除；均線多頭排列且均價差≤limit 才可當進場條件。"""
    r = dict(row)
    smas = sma_map(closes)
    r["sma"] = {k: (None if v is None else round(float(v), 6)) for k, v in smas.items()}
    stack_ok, stack_why = ma_strict_stack(smas)
    band_ok, spread, spread_why = ma_spread_within(smas, limit)
    r["ma_stack"] = stack_ok
    r["ma_band"] = band_ok
    r["ma_limit_pct"] = round(float(limit) * 100.0, 4)
    r["ma_band10"] = band_ok if abs(float(limit) - MA_SPREAD_MAX) < 1e-12 else False
    r["ma_band20"] = band_ok if abs(float(limit) - MA_SPREAD_MAX_20) < 1e-12 else False
    r["ma_spread_pct"] = None if spread is None else round(float(spread) * 100.0, 4)
    bits = []
    if not stack_ok:
        bits.append(stack_why)
    if not band_ok:
        bits.append(spread_why)
    if stack_ok and band_ok:
        r["tag"] = MA_STACK_ENTRY
        r["reason_zh"] = ""
    else:
        r["tag"] = MA_STACK_WAIT
        r["reason_zh"] = "；".join(b for b in bits if b)
    return r


def apply_ma_stack_payload(
    payload: Mapping[str, Any],
    closes_by_sid: Mapping[str, Sequence[Optional[float]]],
    *,
    limit: float = MA_SPREAD_MAX,
) -> dict:
    """重標做多列。closes_by_sid 缺股＝均線缺，不編造。"""
    out = dict(payload)
    pack = dict(out.get("long") or {})
    rows = []
    for r in pack.get("rows") or []:
        sid = str(r.get("sid") or "")
        rows.append(apply_ma_stack_row(r, closes_by_sid.get(sid), limit=limit))
    n_entry = sum(1 for r in rows if r.get("tag") == MA_STACK_ENTRY)
    pack["rows"] = rows
    pack["n_pool"] = len(rows)
    pack["n_entry"] = n_entry
    pack["n_wait"] = len(rows) - n_entry
    out["long"] = pack
    out["n_entry"] = n_entry
    out["n_wait"] = pack["n_wait"]
    return out


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    print("[ma_stack selftest]")
    chk("版號", VERSION == "MA-STACK-v1")
    chk("八窗", list(MA_WINDOWS) == [5, 10, 20, 40, 60, 90, 120, 240])
    chk("SMA 不足", sma_last([1, 2], 3) is None)
    chk("SMA 缺點", sma_last([1, None, 3], 3) is None)
    chk("SMA 3", abs((sma_last([1.0, 2.0, 3.0], 3) or 0) - 2.0) < 1e-12)
    up = [100.0 + 0.02 * i for i in range(240)]
    sm = sma_map(up)
    st, _ = ma_strict_stack(sm)
    bd, sp, _ = ma_spread_within(sm, 0.10)
    chk("緩升多頭排列", st is True)
    chk("緩升均價差≤10%", bd is True and sp is not None and sp <= 0.10)
    steep = [50.0 + i for i in range(240)]
    st2, _ = ma_strict_stack(sma_map(steep))
    bd2, sp2, why2 = ma_spread_within(sma_map(steep), 0.10)
    chk("陡升仍排列", st2 is True)
    chk("陡升均價差拒", bd2 is False and sp2 is not None and sp2 > 0.10 and "逾" in why2)
    dn = list(reversed(up))
    st3, why3 = ma_strict_stack(sma_map(dn))
    chk("下跌非多頭", st3 is False and "≯" in why3)
    flat = {str(h): 100.0 for h in MA_WINDOWS}
    chk("均價相等非嚴格大於", ma_strict_stack(flat)[0] is False)
    tight = {str(h): 100.0 - 0.1 * i for i, h in enumerate(MA_WINDOWS)}
    chk("緊排列＋差≤10 過", ma_strict_stack(tight)[0] and ma_spread_within(tight, 0.10)[0])
    edge = {"5": 110.0, "10": 108.0, "20": 106.0, "40": 104.0,
            "60": 103.0, "90": 102.0, "120": 101.0, "240": 100.0}
    chk("恰 10% 含", ma_spread_within(edge, 0.10)[0] is True)
    over = dict(edge)
    over["5"] = 110.01
    chk("逾 10% 拒", ma_spread_within(over, 0.10)[0] is False)
    edge20 = {"5": 120.0, "10": 116.0, "20": 112.0, "40": 108.0,
              "60": 106.0, "90": 104.0, "120": 102.0, "240": 100.0}
    chk("恰 20% 含", ma_spread_within(edge20, MA_SPREAD_MAX_20)[0] is True)
    mid18 = {**edge20, "5": 118.0}
    chk("18% 過 20 拒 10",
        ma_spread_within(mid18, 0.20)[0] and not ma_spread_within(mid18, 0.10)[0])
    over20 = dict(edge20)
    over20["5"] = 120.01
    chk("逾 20% 拒", ma_spread_within(over20, MA_SPREAD_MAX_20)[0] is False)
    packed20 = apply_ma_stack_payload(
        {"long": {"rows": [{"sid": "a"}, {"sid": "b"}]}},
        {"a": up, "b": steep},
        limit=MA_SPREAD_MAX_20,
    )
    chk("20% 閘緩升仍進場", packed20["n_entry"] >= 1)
    row = apply_ma_stack_row({"sid": "2330", "tag": "x"}, steep)
    chk("陡升等均線閘", row["tag"] == MA_STACK_WAIT and row["ma_stack"] is True)
    row2 = apply_ma_stack_row({"sid": "2330"}, up)
    chk("緩升可當進場", row2["tag"] == MA_STACK_ENTRY)
    packed = apply_ma_stack_payload(
        {"long": {"rows": [{"sid": "a"}, {"sid": "b"}]}},
        {"a": up, "b": steep},
    )
    chk("payload 只 1 檔進場", packed["n_entry"] == 1 and packed["long"]["n_wait"] == 1)
    chk("進場文案", MA_STACK_ENTRY == "可當進場條件")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測: python -m augur.evaluation.ma_stack --selftest；免 DB 免 API)")
