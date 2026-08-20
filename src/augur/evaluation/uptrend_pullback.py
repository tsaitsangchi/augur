"""UP-PULL-v1 硬閘／排序 — 長線結構 × 短線進出（純函式；探針與自測共用）。

🎯 這支在做什麼（白話）：把「做多＝長窗往上＋短窗拉回」「做空＝長窗往下＋短窗反彈」
   收成可機算四閘 AND＋過閘後排序。θ 凍結＝計畫書 v1。不是 RankRidge、不是未來漲跌幅、
   不是可交易／可空。改 θ 須改 VERSION。

執行指令矩陣（本檔=library #18；自測免 DB 免 API）:
  python -m augur.evaluation.uptrend_pullback
  python -m augur.evaluation.uptrend_pullback --selftest
"""
from __future__ import annotations

from typing import Mapping, Optional

VERSION = "UP-PULL-v1"
POLICY_STRICT = "strict"
H_TRACK = (5, 10, 20, 40, 60, 90, 120, 240)
H_LONG = (40, 60, 90, 120, 240)
H_SHORT = (5, 10)
H_PATH_SHORT = (5, 10, 20)  # 顯示用短窗（含 H20）；進場閘 L-B／S-B 仍只 H5+H10
H_RANK = (60, 120, 240)

LONG_DD_LO = -0.15
LONG_DD_HI = -0.03
LONG_DD_SWEET = -0.08
LONG_CYC_MIN = 0.40
LONG_P2H_MIN = 0.80

SHORT_BU_LO = 0.03
SHORT_BU_HI = 0.15
SHORT_BU_SWEET = 0.08
SHORT_CYC_MAX = 0.60
SHORT_P2H_MAX = 0.90


def log_to_pct(log_ret: Optional[float]) -> Optional[float]:
    """log 報酬 → 簡單報酬％（×100）。缺 → None。"""
    if log_ret is None:
        return None
    import math
    return (math.exp(float(log_ret)) - 1.0) * 100.0


def mean_rank_ret(rets: Mapping[int, float]) -> Optional[float]:
    """排序主鍵：mean(H60, H120, H240) log 報酬。缺一則 None。"""
    vals = []
    for h in H_RANK:
        v = rets.get(h)
        if v is None:
            return None
        vals.append(float(v))
    return sum(vals) / len(vals)


def gate_long_a(rets: Mapping[int, float]) -> bool:
    """L-A：長窗 log 報酬全＞0。"""
    return all(rets.get(h) is not None and float(rets[h]) > 0 for h in H_LONG)


def gate_long_b(rets: Mapping[int, float]) -> bool:
    """L-B：H5 與 H10 全＜0。"""
    return all(rets.get(h) is not None and float(rets[h]) < 0 for h in H_SHORT)


def gate_long_c(dd20: Optional[float]) -> bool:
    """L-C：20 日高回撤 ∈ [−0.15, −0.03]。"""
    if dd20 is None:
        return False
    x = float(dd20)
    return LONG_DD_LO <= x <= LONG_DD_HI


def gate_long_d(cycle: Optional[float], p2h: Optional[float]) -> bool:
    """L-D：結構未破。"""
    if cycle is None or p2h is None:
        return False
    return float(cycle) >= LONG_CYC_MIN and float(p2h) >= LONG_P2H_MIN


def gate_short_a(rets: Mapping[int, float]) -> bool:
    """S-A：長窗 log 報酬全＜0。"""
    return all(rets.get(h) is not None and float(rets[h]) < 0 for h in H_LONG)


def gate_short_b(rets: Mapping[int, float]) -> bool:
    """S-B：H5 與 H10 全＞0。"""
    return all(rets.get(h) is not None and float(rets[h]) > 0 for h in H_SHORT)


def gate_short_c(bu20: Optional[float]) -> bool:
    """S-C：20 日低反彈 ∈ [+0.03, +0.15]。"""
    if bu20 is None:
        return False
    x = float(bu20)
    return SHORT_BU_LO <= x <= SHORT_BU_HI


def gate_short_d(cycle: Optional[float], p2h: Optional[float]) -> bool:
    """S-D：結構未修。"""
    if cycle is None or p2h is None:
        return False
    return float(cycle) <= SHORT_CYC_MAX and float(p2h) <= SHORT_P2H_MAX


def pass_long(rets, dd20, cycle, p2h) -> dict[str, bool]:
    """做多四閘。"""
    bits = {
        "L-A": gate_long_a(rets),
        "L-B": gate_long_b(rets),
        "L-C": gate_long_c(dd20),
        "L-D": gate_long_d(cycle, p2h),
    }
    bits["pass"] = all(bits.values())
    return bits


def pass_short(rets, bu20, cycle, p2h) -> dict[str, bool]:
    """做空四閘。"""
    bits = {
        "S-A": gate_short_a(rets),
        "S-B": gate_short_b(rets),
        "S-C": gate_short_c(bu20),
        "S-D": gate_short_d(cycle, p2h),
    }
    bits["pass"] = all(bits.values())
    return bits


def long_sort_key(sid: str, rets: Mapping[int, float], dd20: float) -> tuple:
    """做多：長窗均勻降序、回撤距 −8% 升序、代號升序。"""
    mu = mean_rank_ret(rets)
    mu_s = float(mu) if mu is not None else float("-inf")
    dist = abs(float(dd20) - LONG_DD_SWEET)
    return (-mu_s, dist, str(sid))


def short_sort_key(sid: str, rets: Mapping[int, float], bu20: float) -> tuple:
    """做空：長窗均勻升序（愈負愈前）、反彈距 +8% 升序、代號升序。"""
    mu = mean_rank_ret(rets)
    mu_s = float(mu) if mu is not None else float("inf")
    dist = abs(float(bu20) - SHORT_BU_SWEET)
    return (mu_s, dist, str(sid))


def take_strict(rows: list, k: int) -> list:
    """strict：過閘幾檔列幾檔，上限 k，不補。"""
    k = int(k)
    if k < 0:
        return []
    return list(rows[:k])


WAIT_PB_TAG = "高位相對強，等回撤；≠進場"
PASS_ENTRY_TAG = "已過 UP-PULL-v1 做多閘"
LONG_GATE_ZH = {
    "L-A": "長窗未全正",
    "L-B": "短窗尚未拉回（H5／H10 未全負）",
    "L-C": "20日高回撤不在 −15%～−3%",
    "L-D": "結構未過（cycle／距年線高）",
}


def wait_pullback_annot(long_bits: Mapping[str, bool]) -> dict:
    """Ridge 相對強名單用標。過閘才算進場；未過＝等回撤（不是預測跌幅）。"""
    bits = long_bits or {}
    if bits.get("pass"):
        return {
            "tag": PASS_ENTRY_TAG,
            "wait": False,
            "missing": [],
            "reason_zh": "",
        }
    missing = [k for k in ("L-A", "L-B", "L-C", "L-D") if not bits.get(k)]
    reasons = [LONG_GATE_ZH[k] for k in missing]
    return {
        "tag": WAIT_PB_TAG,
        "wait": True,
        "missing": missing,
        "reason_zh": "；".join(reasons) if reasons else "未過做多閘",
    }


def render_ridge_wait_line(
    rank: int,
    sid: str,
    name: str,
    avg_score: Optional[float],
    annot: Mapping,
) -> str:
    """欄 A 單行。score 無單位。"""
    sc = "—" if avg_score is None else ("%.4f" % float(avg_score))
    tag = str(annot.get("tag") or WAIT_PB_TAG)
    why = str(annot.get("reason_zh") or "")
    tail = ("  缺：" + why) if annot.get("wait") and why else ""
    return "%2d  %s %s  avg_score=%s  %s%s" % (int(rank), sid, name or "", sc, tag, tail)


RIDGE_THEN_PB_WAIT = "等回撤，不是進場"
RIDGE_THEN_PB_SHORT_WAIT = "等反彈，不是進場"
RIDGE_THEN_PB_ENTRY = "可當進場條件"
SHORT_GATE_ZH = {
    "S-A": "長窗未全負",
    "S-B": "短窗尚未反彈（H5／H10 未全正）",
    "S-C": "20日低反彈不在 +3%～+15%",
    "S-D": "結構未過（cycle／距年線高）",
}


def wait_bounce_annot(short_bits: Mapping[str, bool]) -> dict:
    """相對弱池用標。過齊做空四閘才算進場條件；未過＝等反彈（不是可空）。"""
    bits = short_bits or {}
    if bits.get("pass"):
        return {
            "tag": RIDGE_THEN_PB_ENTRY,
            "wait": False,
            "missing": [],
            "reason_zh": "",
        }
    missing = [k for k in ("S-A", "S-B", "S-C", "S-D") if not bits.get(k)]
    reasons = [SHORT_GATE_ZH[k] for k in missing]
    return {
        "tag": RIDGE_THEN_PB_SHORT_WAIT,
        "wait": True,
        "missing": missing,
        "reason_zh": "；".join(reasons) if reasons else "未過做空閘",
    }


def dd20_dist_to_long_band(dd20: Optional[float]) -> float:
    """距做多回撤帶 [−15%, −3%] 的距離；帶內＝0。缺 → inf。"""
    if dd20 is None:
        return float("inf")
    x = float(dd20)
    if LONG_DD_LO <= x <= LONG_DD_HI:
        return 0.0
    if x > LONG_DD_HI:
        return x - LONG_DD_HI
    return LONG_DD_LO - x


def short_window_rise_penalty(rets: Mapping[int, float]) -> float:
    """H5／H10 仍為正的 logret 加總（已雙負＝0）。缺窗 → inf。"""
    p = 0.0
    for h in H_SHORT:
        v = rets.get(h)
        if v is None:
            return float("inf")
        p += max(0.0, float(v))
    return p


def bu20_dist_to_short_band(bu20: Optional[float]) -> float:
    """距做空反彈帶 [+3%, +15%] 的距離；帶內＝0。缺 → inf。"""
    if bu20 is None:
        return float("inf")
    x = float(bu20)
    if SHORT_BU_LO <= x <= SHORT_BU_HI:
        return 0.0
    if x < SHORT_BU_LO:
        return SHORT_BU_LO - x
    return x - SHORT_BU_HI


def short_window_fall_penalty(rets: Mapping[int, float]) -> float:
    """H5／H10 仍為負的 |logret| 加總（已雙正＝0）。缺窗 → inf。"""
    p = 0.0
    for h in H_SHORT:
        v = rets.get(h)
        if v is None:
            return float("inf")
        p += max(0.0, -float(v))
    return p


def ridge_then_pb_sort_key(
    sid: str,
    rets: Mapping[int, float],
    dd20: Optional[float],
    long_bits: Mapping[str, bool],
) -> tuple:
    """池內回撤近→遠：距 −15%～−3% 帶近的在前；短窗已拉其次；還在 20 日高的在後。

    過齊四閘只決定標籤，不插隊（還沒回撤的相對強仍留在池裡）。
    """
    _ = long_bits
    return (
        dd20_dist_to_long_band(dd20),
        short_window_rise_penalty(rets),
        str(sid),
    )


def ridge_then_pb_tag(long_bits: Mapping[str, bool]) -> str:
    """過齊四閘才叫可當進場條件；否則等回撤。"""
    if (long_bits or {}).get("pass"):
        return RIDGE_THEN_PB_ENTRY
    return RIDGE_THEN_PB_WAIT


def ridge_then_pb_short_sort_key(
    sid: str,
    rets: Mapping[int, float],
    bu20: Optional[float],
    short_bits: Mapping[str, bool],
) -> tuple:
    """池內反彈近→遠：距 +3%～+15% 帶近的在前；短窗已彈其次；還在 20 日低的在後。

    過齊四閘只決定標籤，不插隊（還沒反彈的相對弱仍留在池裡）。不是可空。
    """
    _ = short_bits
    return (
        bu20_dist_to_short_band(bu20),
        short_window_fall_penalty(rets),
        str(sid),
    )


def ridge_then_pb_short_tag(short_bits: Mapping[str, bool]) -> str:
    """過齊做空四閘才叫可當進場條件；否則等反彈。不是可空。"""
    if (short_bits or {}).get("pass"):
        return RIDGE_THEN_PB_ENTRY
    return RIDGE_THEN_PB_SHORT_WAIT


def path_window_pass(rets: Mapping[int, float], *, side: str) -> dict[str, Optional[bool]]:
    """個別窗路徑是否過（已實現、往回看）。做多：H5/10/20＜0、H40+＞0；做空相反。缺窗＝None。"""
    want_short_neg = str(side).lower() == "long"
    out: dict[str, Optional[bool]] = {}
    for h in H_TRACK:
        v = rets.get(h)
        if v is None:
            out[str(h)] = None
            continue
        x = float(v)
        if h in H_PATH_SHORT:
            out[str(h)] = (x < 0) if want_short_neg else (x > 0)
        else:
            out[str(h)] = (x > 0) if want_short_neg else (x < 0)
    return out


def format_window_pass(bits: Mapping[str, Optional[bool]]) -> str:
    """H5過 H10未 …；None＝缺。"""
    parts = []
    for h in H_TRACK:
        v = bits.get(str(h))
        if v is None:
            s = "缺"
        else:
            s = "過" if v else "未"
        parts.append("H%s%s" % (h, s))
    return " ".join(parts)


WATCH_PB_VERSION = "WATCH-PB-v1"
WATCH_PB_LONG_TAG = "等回撤，不是進場"
WATCH_PB_SHORT_TAG = "等反彈，不是進場"


def is_watch_long(long_bits: Mapping[str, bool]) -> bool:
    """觀察多：L-A∧L-C∧L-D 且尚未 L-B（短窗仍衝）。不是進場。"""
    b = long_bits or {}
    return bool(b.get("L-A") and b.get("L-C") and b.get("L-D") and not b.get("L-B"))


def is_watch_short(short_bits: Mapping[str, bool]) -> bool:
    """觀察空：S-A∧S-C∧S-D 且尚未 S-B（短窗仍弱）。不是可空。"""
    b = short_bits or {}
    return bool(b.get("S-A") and b.get("S-C") and b.get("S-D") and not b.get("S-B"))


def watch_long_sort_key(sid: str, rets: Mapping[int, float]) -> tuple:
    """短窗仍漲多→少，再長窗強→弱，再代號。"""
    mu = mean_rank_ret(rets)
    mu_s = float(mu) if mu is not None else float("-inf")
    return (-short_window_rise_penalty(rets), -mu_s, str(sid))


def watch_short_sort_key(sid: str, rets: Mapping[int, float]) -> tuple:
    """短窗仍跌多→少，再長窗弱→強，再代號。"""
    mu = mean_rank_ret(rets)
    mu_s = float(mu) if mu is not None else float("inf")
    return (-short_window_fall_penalty(rets), mu_s, str(sid))


def watch_long_tag() -> str:
    return WATCH_PB_LONG_TAG


def watch_short_tag() -> str:
    return WATCH_PB_SHORT_TAG


def negate_rets(rets: Mapping[int, float]) -> dict[int, float]:
    """自測用：所有窗 log 報酬變號（A／B 閘多空對調）。"""
    return {int(h): -float(v) for h, v in rets.items()}


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("VERSION v1", VERSION == "UP-PULL-v1")
    chk("H_TRACK 8", H_TRACK == (5, 10, 20, 40, 60, 90, 120, 240))
    up = {5: -0.02, 10: -0.03, 20: 0.04, 40: 0.05, 60: 0.10, 90: 0.12, 120: 0.15, 240: 0.20}
    chk("L-A 長窗全正", gate_long_a(up))
    chk("L-B 短窗全負", gate_long_b(up))
    chk("S-A 同組為假", not gate_short_a(up))
    dn = negate_rets(up)
    chk("變號後 S-A", gate_short_a(dn))
    chk("變號後 S-B", gate_short_b(dn))
    chk("變號後非 L-A", not gate_long_a(dn))
    chk("L-C 含 −3%", gate_long_c(-0.03))
    chk("L-C 含 −15%", gate_long_c(-0.15))
    chk("L-C 拒 −2.9%", not gate_long_c(-0.029))
    chk("L-C 拒 −15.1%", not gate_long_c(-0.151))
    chk("L-C 拒 None", not gate_long_c(None))
    chk("S-C 含 +3%", gate_short_c(0.03))
    chk("S-C 拒 +2.9%", not gate_short_c(0.029))
    chk("L-D 過", gate_long_d(0.40, 0.80))
    chk("L-D 拒 cycle", not gate_long_d(0.39, 0.90))
    chk("S-D 過", gate_short_d(0.60, 0.90))
    chk("S-D 拒 p2h", not gate_short_d(0.50, 0.91))
    bits = pass_long(up, -0.08, 0.7, 0.9)
    chk("做多四閘全過", bits["pass"])
    bits_s = pass_short(dn, 0.08, 0.2, 0.7)
    chk("做空四閘全過（變號+結構）", bits_s["pass"])
    k1 = long_sort_key("2006", up, -0.08)
    k2 = long_sort_key("3231", {**up, 240: 0.30}, -0.08)
    chk("做多 長窗更強排前", k2 < k1)
    sk1 = short_sort_key("1215", dn, 0.08)
    sk2 = short_sort_key("8099", {**dn, 240: -0.05}, 0.08)
    chk("做空 長窗更負排前", sk1 < sk2)
    chk("strict 截 k", take_strict([1, 2, 3], 2) == [1, 2])
    chk("strict 不足不補", take_strict([1, 2], 10) == [1, 2])
    wait = wait_pullback_annot({"L-A": True, "L-B": False, "L-C": False, "L-D": True, "pass": False})
    chk("等回撤 wait", wait["wait"] is True and wait["tag"] == WAIT_PB_TAG)
    chk("缺 L-B L-C", wait["missing"] == ["L-B", "L-C"])
    chk("文案不寫等回跌", "回跌" not in wait["reason_zh"] and "回跌" not in wait["tag"])
    passed = wait_pullback_annot({"L-A": True, "L-B": True, "L-C": True, "L-D": True, "pass": True})
    chk("過閘不算等回撤", passed["wait"] is False and passed["tag"] == PASS_ENTRY_TAG)
    line = render_ridge_wait_line(1, "2301", "光寶科", 0.5476, wait)
    chk("Ridge 行含等回撤", "等回撤" in line and "2301" in line and "≠進場" in line)
    chk("帶內距=0", dd20_dist_to_long_band(-0.08) == 0.0)
    chk("貼高距帶", abs(dd20_dist_to_long_band(0.0) - 0.03) < 1e-12)
    near = ridge_then_pb_sort_key("2454", {**up, 10: 0.005}, -0.08, {"pass": False})
    far = ridge_then_pb_sort_key("2301", {**up, 5: 0.02, 10: 0.08}, 0.0, {"pass": False})
    chk("回撤近排前", near < far)
    at_high = ridge_then_pb_sort_key("2301", up, 0.0, {"pass": True})
    chk("貼高在後不論過齊標", near < at_high)
    chk("過齊標進場條件", ridge_then_pb_tag({"pass": True}) == RIDGE_THEN_PB_ENTRY)
    chk("未過標等回撤", ridge_then_pb_tag({"pass": False}) == RIDGE_THEN_PB_WAIT)
    chk("反彈帶內距=0", bu20_dist_to_short_band(0.08) == 0.0)
    chk("貼低距帶", abs(bu20_dist_to_short_band(0.0) - 0.03) < 1e-12)
    s_near = ridge_then_pb_short_sort_key("1215", {**dn, 5: 0.01}, 0.08, {"pass": False})
    s_far = ridge_then_pb_short_sort_key("3548", {**dn, 5: -0.04, 10: -0.02}, 0.0, {"pass": False})
    chk("反彈近排前", s_near < s_far)
    at_low = ridge_then_pb_short_sort_key("3548", dn, 0.0, {"pass": True})
    chk("貼低在後不論過齊標", s_near < at_low)
    chk("過齊標做空進場", ridge_then_pb_short_tag({"pass": True}) == RIDGE_THEN_PB_ENTRY)
    chk("未過標等反彈", ridge_then_pb_short_tag({"pass": False}) == RIDGE_THEN_PB_SHORT_WAIT)
    wp = path_window_pass(up, side="long")
    chk("做多 H5 過（已拉）", wp["5"] is True)
    chk("做多 H20 未（此組 H20>0）", wp["20"] is False)
    chk("做多 H40 過（長窗上）", wp["40"] is True)
    wps = path_window_pass(dn, side="short")
    chk("做空 H5 過（已彈）", wps["5"] is True)
    chk("做空 H40 過（長窗下）", wps["40"] is True)
    chk("窗文案含過未", "H5過" in format_window_pass(wp) and "H20未" in format_window_pass(wp))
    bounce = wait_bounce_annot({"S-A": True, "S-B": False, "S-C": False, "S-D": True, "pass": False})
    chk("等反彈 wait", bounce["wait"] is True and bounce["tag"] == RIDGE_THEN_PB_SHORT_WAIT)
    chk("做空文案不寫等回撤", "回撤" not in bounce["tag"] and "回撤" not in bounce["reason_zh"])
    chk("缺 S-B S-C", bounce["missing"] == ["S-B", "S-C"])
    charging = {5: 0.10, 10: 0.15, 20: 0.04, 40: 0.05, 60: 0.10, 90: 0.12, 120: 0.15, 240: 0.20}
    wbits = pass_long(charging, -0.06, 0.7, 0.9)
    chk("觀察多：在帶且短窗仍衝", is_watch_long(wbits) and not wbits["L-B"] and wbits["L-C"])
    chk("進場不是觀察多", not is_watch_long(pass_long(up, -0.08, 0.7, 0.9)))
    milder = {**charging, 5: 0.01, 10: 0.02}
    chk("仍漲多排前", watch_long_sort_key("3017", charging) < watch_long_sort_key("5511", milder))
    chk("觀察多標等回撤", watch_long_tag() == WATCH_PB_LONG_TAG)
    s_chg = {5: -0.03, 10: -0.10, 20: -0.04, 40: -0.05, 60: -0.10, 90: -0.12, 120: -0.15, 240: -0.20}
    sbits = pass_short(s_chg, 0.07, 0.2, 0.7)
    chk("觀察空：在帶且短窗仍弱", is_watch_short(sbits) and not sbits["S-B"] and sbits["S-C"])
    chk("進場空不是觀察空", not is_watch_short(pass_short(dn, 0.08, 0.2, 0.7)))
    chk("觀察空標等反彈", watch_short_tag() == WATCH_PB_SHORT_TAG)
    chk("WATCH 版號", WATCH_PB_VERSION == "WATCH-PB-v1")
    z = log_to_pct(0.0)
    chk("pct 0 log=0", z is not None and abs(z) < 1e-12)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測: python -m augur.evaluation.uptrend_pullback --selftest；免 DB 免 API)")
