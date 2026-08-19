"""TREND-PB 閉集規則閘 — W1 路徑族＋W2 指標族＋W3 Elder 兩屏近似（純函式；T01 呼叫 UP-PULL-v1）。

🎯 這支在做什麼（白話）：給每股已發生路徑／均線／RSI／布林／週 MACD 柱，判斷它過閉集哪一閘。
   不是未來漲跌幅、不是可交易、不是倒進 canonical 31。改 θ＝新 ID。波次不符 → 探針拒。
   T07 ≠ 原書三屏（日頻無盤中框；approx=elder_2screen_daily）。

執行指令矩陣（本檔=library #18；自測免 DB 免 API）:
  python -m augur.evaluation.trend_pullback_catalog
  python -m augur.evaluation.trend_pullback_catalog --selftest
"""
from __future__ import annotations

from typing import Mapping, Optional, Sequence

from augur.evaluation import uptrend_pullback as up

VERSION = "TREND-PB-CATALOG"
POLICY_STRICT = "strict"

T_IDS = ("T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T09", "T10", "T11", "T12")
C_IDS = ("C01", "C02", "C03", "C04", "C05", "C06", "C07")
CLOSED_IDS = T_IDS + C_IDS

WAVE = {
    "T01": "W1", "T02": "W1", "T11": "W1",
    "C01": "W1", "C02": "W1", "C03": "W1", "C06": "W1", "C07": "W1",
    "T03": "W2", "T04": "W2", "T05": "W2", "T06": "W2", "T08": "W2", "T12": "W2", "C04": "W2",
    "T07": "W3",
    "T09": "W4", "T10": "W4", "C05": "W4",
}
W1_DEFAULT = ("T01", "T02", "T11", "C01", "C03", "C06", "C07")
W2_DEFAULT = ("T03", "T04", "T05", "T06", "T08", "T12", "C04")
W3_DEFAULT = ("T07",)
WAVE_DEFAULT = {"W1": W1_DEFAULT, "W2": W2_DEFAULT, "W3": W3_DEFAULT}

C06_LONG_MIN = 0.90
C06_SHORT_MAX = 0.10
SMA_PB_LO = -0.15
SMA_PB_HI = -0.03
SMA_BU_LO = 0.03
SMA_BU_HI = 0.15
SMA_PB_SWEET = -0.08
RSI2_LONG = 10.0
RSI2_LONG_STRICT = 5.0
RSI2_SHORT = 90.0
RSI2_SHORT_STRICT = 95.0
RSI14_LONG_LO, RSI14_LONG_HI = 30.0, 50.0
RSI14_SHORT_LO, RSI14_SHORT_HI = 50.0, 70.0
AT_EXTREME_EPS = 1e-12
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9
WEEKLY_STRIDE = 5
T07_RSI2_LONG = 50.0
T07_RSI2_SHORT = 50.0
T07_APPROX = "elder_2screen_daily"


def parse_families(raw: str, *, wave: Optional[str] = None) -> tuple[list[str], Optional[str]]:
    """CSV／all → ID 列。不在閉集或波次不符 → ( [], 錯誤字 )。"""
    s = (raw or "").strip()
    if not s:
        return [], "✗ --families 空"
    if s.lower() == "all":
        w = wave or "W1"
        if w not in WAVE_DEFAULT:
            return [], f"✗ --wave {w} 無預設列（W1／W2／W3）"
        ids = list(WAVE_DEFAULT[w])
    else:
        ids = [x.strip().upper() for x in s.split(",") if x.strip()]
    if not ids:
        return [], "✗ --families 空"
    for i in ids:
        if i not in CLOSED_IDS:
            return [], f"✗ 不在閉集：{i}"
        if wave and WAVE.get(i) != wave:
            return [], f"✗ {i} 屬 {WAVE.get(i)}，本波次={wave}（另 GO）"
    return ids, None


def sma(xs: Sequence[float], n: int) -> Optional[float]:
    """最近 n 點算術平均。不足 → None。"""
    if n <= 0 or xs is None or len(xs) < n:
        return None
    chunk = [float(x) for x in xs[-n:]]
    return sum(chunk) / n


def rsi_wilder(closes: Sequence[float], period: int) -> Optional[float]:
    """Wilder RSI（末值）。不足 period+1 點 → None。無下跌 → 100。"""
    if period <= 0 or closes is None or len(closes) < period + 1:
        return None
    chg = [float(closes[i]) - float(closes[i - 1]) for i in range(1, len(closes))]
    gains = [max(x, 0.0) for x in chg]
    losses = [max(-x, 0.0) for x in chg]
    ag = sum(gains[:period]) / period
    al = sum(losses[:period]) / period
    for i in range(period, len(chg)):
        ag = (ag * (period - 1) + gains[i]) / period
        al = (al * (period - 1) + losses[i]) / period
    if al == 0.0:
        return 100.0 if ag > 0 else 50.0
    rs = ag / al
    return 100.0 - 100.0 / (1.0 + rs)


def bollinger_last(closes: Sequence[float], n: int = 20, k: float = 2.0):
    """末根布林 (中, 下, 上)；σ＝母體标准差。不足 → (None,None,None)。"""
    mid = sma(closes, n)
    if mid is None:
        return None, None, None
    chunk = [float(x) for x in closes[-n:]]
    var = sum((x - mid) ** 2 for x in chunk) / n
    sd = var ** 0.5
    kk = float(k)
    return mid, mid - kk * sd, mid + kk * sd


def fill_w2_indicators(rec: dict, closes: Sequence[float]) -> dict:
    """就地寫入 SMA／RSI／布林（closes 舊→新、末＝asof）。不足 201 點則指標保持缺。"""
    rec = dict(rec)
    if closes is None or len(closes) < 201:
        return rec
    rec["close"] = float(closes[-1])
    rec["sma20"] = sma(closes, 20)
    rec["sma60"] = sma(closes, 60)
    rec["sma200"] = sma(closes, 200)
    rec["sma200_prev"] = sma(list(closes)[:-1], 200)
    rec["rsi2"] = rsi_wilder(closes, 2)
    rec["rsi14"] = rsi_wilder(closes, 14)
    mid, lo, hi = bollinger_last(closes, 20, 2.0)
    rec["bb_mid"], rec["bb_low"], rec["bb_up"] = mid, lo, hi
    if rec["sma20"] and rec["sma20"] > 0:
        rec["px_sma20"] = rec["close"] / rec["sma20"] - 1.0
    rec["at_hi20"] = abs(float(rec.get("dd20") or 0.0)) <= AT_EXTREME_EPS
    rec["at_lo20"] = abs(float(rec.get("bu20") or 0.0)) <= AT_EXTREME_EPS
    return fill_w3_indicators(rec, closes)


def sample_stride(xs: Sequence[float], stride: int = WEEKLY_STRIDE) -> list[float]:
    """舊→新；末點＝asof，再每 stride 交易日往回抽。"""
    if xs is None or stride < 1:
        return []
    out: list[float] = []
    i = len(xs) - 1
    while i >= 0:
        out.append(float(xs[i]))
        i -= stride
    out.reverse()
    return out


def ema_series(xs: Sequence[float], n: int) -> Optional[list[Optional[float]]]:
    """標準 EMA；種＝前 n 點 SMA。不足 → None。"""
    if n <= 0 or xs is None or len(xs) < n:
        return None
    k = 2.0 / (n + 1.0)
    seed = sum(float(x) for x in xs[:n]) / n
    out: list[Optional[float]] = [None] * (n - 1) + [seed]
    prev = seed
    for x in xs[n:]:
        prev = float(x) * k + prev * (1.0 - k)
        out.append(prev)
    return out


def macd_histogram_series(
    closes: Sequence[float],
    *,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL,
) -> Optional[list[Optional[float]]]:
    """MACD 柱序列（與 close 等長；前段 None）。不足 → None。"""
    e_f = ema_series(closes, fast)
    e_s = ema_series(closes, slow)
    if e_f is None or e_s is None:
        return None
    macd: list[Optional[float]] = []
    for a, b in zip(e_f, e_s):
        macd.append(None if a is None or b is None else float(a) - float(b))
    i0 = next((i for i, v in enumerate(macd) if v is not None), None)
    if i0 is None:
        return None
    rest = [float(macd[i]) for i in range(i0, len(macd))]
    sig = ema_series(rest, signal)
    if sig is None:
        return None
    hist: list[Optional[float]] = [None] * len(closes)
    for j, (m, s) in enumerate(zip(rest, sig)):
        if s is None:
            continue
        hist[i0 + j] = m - float(s)
    return hist


def last_two_finite(xs: Sequence[Optional[float]]):
    """序列末兩筆有限值；(t, t-1)。不足 → (None, None)。"""
    finite = [float(x) for x in xs if x is not None]
    if len(finite) < 2:
        return None, None
    return finite[-1], finite[-2]


def fill_w3_indicators(
    rec: dict, closes: Sequence[float], stride: int = WEEKLY_STRIDE
) -> dict:
    """週線代理 MACD 柱末兩根（closes 舊→新、末＝asof）。不寫庫。"""
    rec = dict(rec)
    rec["t07_approx"] = T07_APPROX
    if closes is None or stride < 1:
        return rec
    weekly = sample_stride(closes, stride)
    rec["weekly_n"] = len(weekly)
    hist = macd_histogram_series(
        weekly, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL
    )
    if hist is None:
        return rec
    h_t, h_p = last_two_finite(hist)
    rec["macd_hist_weekly"] = h_t
    rec["macd_hist_weekly_prev"] = h_p
    if h_t is not None and h_p is not None:
        rec["macd_hist_weekly_slope"] = float(h_t) - float(h_p)
    return rec


def _pos(rets: Mapping[int, float], h: int) -> bool:
    v = rets.get(h)
    return v is not None and float(v) > 0


def _neg(rets: Mapping[int, float], h: int) -> bool:
    v = rets.get(h)
    return v is not None and float(v) < 0


def _gt(a, b) -> bool:
    return a is not None and b is not None and float(a) > float(b)


def _lt(a, b) -> bool:
    return a is not None and b is not None and float(a) < float(b)


def _le(a, b) -> bool:
    return a is not None and b is not None and float(a) <= float(b)


def _ge(a, b) -> bool:
    return a is not None and b is not None and float(a) >= float(b)


def _band(x, lo, hi) -> bool:
    return x is not None and float(lo) <= float(x) <= float(hi)


def pass_long(fid: str, rec: Mapping) -> bool:
    """做多閘。C02 不是路徑閘（探針 skip）。"""
    fid = str(fid).upper()
    rets = rec.get("rets") or {}
    if fid == "T01":
        return bool(up.pass_long(rets, rec.get("dd20"), rec.get("cyc"), rec.get("p2h"))["pass"])
    if fid == "T02":
        return _pos(rets, 60) and _neg(rets, 5)
    if fid == "T11":
        return _pos(rets, 120) and _neg(rets, 5) and up.gate_long_c(rec.get("dd20"))
    if fid == "C01":
        return all(_pos(rets, h) for h in up.H_TRACK)
    if fid == "C03":
        return _pos(rets, 120)
    if fid == "C06":
        c = rec.get("cyc")
        return c is not None and float(c) >= C06_LONG_MIN
    if fid == "C07":
        return _neg(rets, 5)
    if fid == "C02":
        return False
    if fid == "T03":
        return (
            _gt(rec.get("close"), rec.get("sma200"))
            and _gt(rec.get("sma200"), rec.get("sma200_prev"))
            and _band(rec.get("px_sma20"), SMA_PB_LO, SMA_PB_HI)
        )
    if fid == "T04":
        return _gt(rec.get("close"), rec.get("sma60")) and _band(
            rec.get("px_sma20"), SMA_PB_LO, SMA_PB_HI
        )
    if fid == "T05":
        return _gt(rec.get("close"), rec.get("sma200")) and _lt(rec.get("rsi2"), RSI2_LONG)
    if fid == "T06":
        return _gt(rec.get("close"), rec.get("sma200")) and _lt(rec.get("rsi2"), RSI2_LONG_STRICT)
    if fid == "T08":
        return _gt(rec.get("close"), rec.get("sma200")) and _band(
            rec.get("rsi14"), RSI14_LONG_LO, RSI14_LONG_HI
        )
    if fid == "T12":
        return _gt(rec.get("close"), rec.get("sma200")) and _le(rec.get("close"), rec.get("bb_low"))
    if fid == "C04":
        return bool(rec.get("at_hi20"))
    if fid == "T07":
        return _lt(rec.get("rsi2"), T07_RSI2_LONG) and _gt(
            rec.get("macd_hist_weekly"), rec.get("macd_hist_weekly_prev")
        )
    raise ValueError(f"本殼不跑 {fid}")


def pass_short(fid: str, rec: Mapping) -> bool:
    """做空閘（鏡像）。"""
    fid = str(fid).upper()
    rets = rec.get("rets") or {}
    if fid == "T01":
        return bool(up.pass_short(rets, rec.get("bu20"), rec.get("cyc"), rec.get("p2h"))["pass"])
    if fid == "T02":
        return _neg(rets, 60) and _pos(rets, 5)
    if fid == "T11":
        return _neg(rets, 120) and _pos(rets, 5) and up.gate_short_c(rec.get("bu20"))
    if fid == "C01":
        return all(_neg(rets, h) for h in up.H_TRACK)
    if fid == "C03":
        return _neg(rets, 120)
    if fid == "C06":
        c = rec.get("cyc")
        return c is not None and float(c) <= C06_SHORT_MAX
    if fid == "C07":
        return _pos(rets, 5)
    if fid == "C02":
        return False
    if fid == "T03":
        return (
            _lt(rec.get("close"), rec.get("sma200"))
            and _lt(rec.get("sma200"), rec.get("sma200_prev"))
            and _band(rec.get("px_sma20"), SMA_BU_LO, SMA_BU_HI)
        )
    if fid == "T04":
        return _lt(rec.get("close"), rec.get("sma60")) and _band(
            rec.get("px_sma20"), SMA_BU_LO, SMA_BU_HI
        )
    if fid == "T05":
        return _lt(rec.get("close"), rec.get("sma200")) and _gt(rec.get("rsi2"), RSI2_SHORT)
    if fid == "T06":
        return _lt(rec.get("close"), rec.get("sma200")) and _gt(rec.get("rsi2"), RSI2_SHORT_STRICT)
    if fid == "T08":
        return _lt(rec.get("close"), rec.get("sma200")) and _band(
            rec.get("rsi14"), RSI14_SHORT_LO, RSI14_SHORT_HI
        )
    if fid == "T12":
        return _lt(rec.get("close"), rec.get("sma200")) and _ge(rec.get("close"), rec.get("bb_up"))
    if fid == "C04":
        return bool(rec.get("at_lo20"))
    if fid == "T07":
        return _gt(rec.get("rsi2"), T07_RSI2_SHORT) and _lt(
            rec.get("macd_hist_weekly"), rec.get("macd_hist_weekly_prev")
        )
    raise ValueError(f"本殼不跑 {fid}")


def long_sort_key(fid: str, rec: Mapping) -> tuple:
    """過閘後排序（做多）。"""
    fid = str(fid).upper()
    sid = str(rec.get("sid") or "")
    rets = rec.get("rets") or {}
    if fid in ("T01", "T02", "T11"):
        return up.long_sort_key(sid, rets, float(rec.get("dd20") or 0.0))
    if fid == "C01":
        mu = sum(float(rets[h]) for h in up.H_TRACK) / len(up.H_TRACK)
        return (-mu, sid)
    if fid == "C03":
        return (-float(rets.get(120) or 0.0), sid)
    if fid == "C06":
        return (-float(rec.get("cyc") or 0.0), sid)
    if fid == "C07":
        return (float(rets.get(5) or 0.0), sid)
    if fid in ("T03", "T04"):
        return (abs(float(rec.get("px_sma20") or 0.0) - SMA_PB_SWEET), sid)
    if fid in ("T05", "T06", "T07"):
        return (float(rec.get("rsi2") if rec.get("rsi2") is not None else 999.0), sid)
    if fid == "T08":
        r = rec.get("rsi14")
        return (abs(float(r) - 40.0) if r is not None else 999.0, sid)
    if fid == "T12":
        px, lo = rec.get("close"), rec.get("bb_low")
        dist = float("inf") if px is None or lo is None else float(px) - float(lo)
        return (dist, sid)
    if fid == "C04":
        return up.long_sort_key(sid, rets, float(rec.get("dd20") or 0.0))
    return (sid,)


def short_sort_key(fid: str, rec: Mapping) -> tuple:
    """過閘後排序（做空）。"""
    fid = str(fid).upper()
    sid = str(rec.get("sid") or "")
    rets = rec.get("rets") or {}
    if fid in ("T01", "T02", "T11"):
        return up.short_sort_key(sid, rets, float(rec.get("bu20") or 0.0))
    if fid == "C01":
        mu = sum(float(rets[h]) for h in up.H_TRACK) / len(up.H_TRACK)
        return (mu, sid)
    if fid == "C03":
        return (float(rets.get(120) or 0.0), sid)
    if fid == "C06":
        return (float(rec.get("cyc") or 0.0), sid)
    if fid == "C07":
        return (-float(rets.get(5) or 0.0), sid)
    if fid in ("T03", "T04"):
        return (abs(float(rec.get("px_sma20") or 0.0) - 0.08), sid)
    if fid in ("T05", "T06", "T07"):
        return (-float(rec.get("rsi2") if rec.get("rsi2") is not None else 0.0), sid)
    if fid == "T08":
        r = rec.get("rsi14")
        return (abs(float(r) - 60.0) if r is not None else 999.0, sid)
    if fid == "T12":
        px, hi = rec.get("close"), rec.get("bb_up")
        dist = float("inf") if px is None or hi is None else float(hi) - float(px)
        return (dist, sid)
    if fid == "C04":
        return up.short_sort_key(sid, rets, float(rec.get("bu20") or 0.0))
    return (sid,)


def jaccard(a: set, b: set) -> Optional[float]:
    """兩集合 Jaccard；皆空 → None。"""
    u = set(a) | set(b)
    if not u:
        return None
    return len(set(a) & set(b)) / len(u)


def overlap_vs(base: set, other: set) -> dict:
    """相對 base 的交集規模。"""
    inter = set(base) & set(other)
    return {
        "n_base": len(base),
        "n_other": len(other),
        "n_inter": len(inter),
        "jaccard": jaccard(base, other),
    }


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("VERSION catalog", VERSION == "TREND-PB-CATALOG")
    ids, err = parse_families("T01,T02,T11", wave="W1")
    chk("parse W1 列", ids == ["T01", "T02", "T11"] and err is None)
    _, err2 = parse_families("T05", wave="W1")
    chk("parse T05 拒於 W1", err2 is not None and "W2" in (err2 or ""))
    _, err_t01w2 = parse_families("T01", wave="W2")
    chk("parse T01 拒於 W2", err_t01w2 is not None and "W1" in (err_t01w2 or ""))
    ids_w2, err_w2 = parse_families("all", wave="W2")
    chk("all＝W2 預設 7", ids_w2 == list(W2_DEFAULT) and err_w2 is None)
    ids_w3, err_w3 = parse_families("all", wave="W3")
    chk("all＝W3 預設 T07", ids_w3 == list(W3_DEFAULT) and err_w3 is None)
    _, err_t07w2 = parse_families("T07", wave="W2")
    chk("parse T07 拒於 W2", err_t07w2 is not None and "W3" in (err_t07w2 or ""))
    _, err_t05w3 = parse_families("T05", wave="W3")
    chk("parse T05 拒於 W3", err_t05w3 is not None and "W2" in (err_t05w3 or ""))
    ids_t07, err_t07 = parse_families("T07", wave="W3")
    chk("parse T07＠W3", ids_t07 == ["T07"] and err_t07 is None)
    _, err3 = parse_families("FOO")
    chk("parse 閉集外拒", err3 is not None)
    ids_all, err_all = parse_families("all", wave="W1")
    chk("all＝W1 預設 7", ids_all == list(W1_DEFAULT) and err_all is None)

    up_path = {5: -0.02, 10: -0.03, 20: 0.04, 40: 0.05, 60: 0.10, 90: 0.12, 120: 0.15, 240: 0.20}
    rec_t01 = {"sid": "3231", "rets": up_path, "dd20": -0.08, "bu20": 0.08, "cyc": 0.7, "p2h": 0.9}
    chk("T01 做多＝UP-PULL", pass_long("T01", rec_t01) is True)
    chk("T01 不做空", pass_short("T01", rec_t01) is False)
    rec_t02 = {
        "sid": "X",
        "rets": {**up_path, 10: 0.01},
        "dd20": -0.08,
        "bu20": 0.08,
        "cyc": 0.7,
        "p2h": 0.9,
    }
    chk("T02 過（H10 正仍可）", pass_long("T02", rec_t02))
    chk("T01 拒同一檔（H10 非負）", not pass_long("T01", rec_t02))
    rec_c01 = {
        "sid": "2301",
        "rets": {h: 0.01 for h in up.H_TRACK},
        "dd20": 0.0,
        "bu20": 0.05,
        "cyc": 1.0,
        "p2h": 1.0,
    }
    chk("C01 八窗全正", pass_long("C01", rec_c01))
    chk("C01 不是 T01（無拉回）", not pass_long("T01", rec_c01))
    rec_c03 = {"sid": "Y", "rets": {**{h: -0.01 for h in up.H_TRACK}, 120: 0.05}, "dd20": 0, "bu20": 0, "cyc": 0.5, "p2h": 0.9}
    chk("C03 只看 H120", pass_long("C03", rec_c03))
    rec_c06 = {"sid": "Z", "rets": up_path, "dd20": 0, "bu20": 0, "cyc": 0.91, "p2h": 1.0}
    chk("C06 年線高位", pass_long("C06", rec_c06) and not pass_short("C06", rec_c06))
    rec_c07 = {"sid": "W", "rets": {**{h: 0.02 for h in up.H_TRACK}, 5: -0.01}, "dd20": 0, "bu20": 0, "cyc": 0.2, "p2h": 0.7}
    chk("C07 無長線過濾", pass_long("C07", rec_c07))
    rec_t11 = {"sid": "T", "rets": {**up_path, 40: -0.01}, "dd20": -0.08, "bu20": 0.08, "cyc": 0.5, "p2h": 0.9}
    chk("T11 不要求 40–240 全正", pass_long("T11", rec_t11) and not pass_long("T01", rec_t11))
    ov = overlap_vs({"a", "b"}, {"b", "c"})
    chk("overlap n_inter=1", ov["n_inter"] == 1 and abs((ov["jaccard"] or 0) - 1 / 3) < 1e-12)
    chk("T01 不複製 θ 常數", up.LONG_DD_LO == -0.15)

    chk("sma 3", abs((sma([1, 2, 3], 3) or 0) - 2.0) < 1e-12)
    chk("sma 不足", sma([1, 2], 3) is None)
    up_closes = [float(i) for i in range(1, 30)]
    chk("RSI 上升序列近 100", (rsi_wilder(up_closes, 2) or 0) > 90)
    dn_closes = [float(i) for i in range(30, 0, -1)]
    dn_rsi = rsi_wilder(dn_closes, 2)
    chk("RSI 下降序列近 0", dn_rsi is not None and dn_rsi < 10)
    rec_t03 = {
        "sid": "A",
        "rets": up_path,
        "dd20": -0.08,
        "bu20": 0.08,
        "close": 100.0,
        "sma200": 90.0,
        "sma200_prev": 89.0,
        "sma20": 108.0,
        "px_sma20": 100 / 108 - 1.0,
    }
    chk("T03 年線上＋SMA20 回撤", pass_long("T03", rec_t03) and SMA_PB_LO <= rec_t03["px_sma20"] <= SMA_PB_HI)
    rec_t03_hi = {**rec_t03, "sma20": 100.0, "px_sma20": 0.0}
    chk("T03 拒無回撤", not pass_long("T03", rec_t03_hi))
    rec_t05 = {**rec_t03, "rsi2": 8.0}
    chk("T05 RSI(2)<10", pass_long("T05", rec_t05) and not pass_long("T06", rec_t05))
    rec_t06 = {**rec_t03, "rsi2": 4.0}
    chk("T06 嚴 ⊂ T05", pass_long("T06", rec_t06) and pass_long("T05", rec_t06))
    rec_t08 = {**rec_t03, "rsi14": 40.0}
    chk("T08 RSI14 帶", pass_long("T08", rec_t08))
    rec_t12 = {**rec_t03, "bb_low": 101.0, "close": 100.0, "sma200": 90.0}
    chk("T12 上年線觸下軌", pass_long("T12", rec_t12))
    rec_c04 = {"sid": "B", "rets": up_path, "dd20": 0.0, "bu20": 0.05, "at_hi20": True, "at_lo20": False}
    chk("C04 做多＝20日高", pass_long("C04", rec_c04) and not pass_short("C04", rec_c04))
    rec_c04s = {"sid": "C", "rets": up_path, "dd20": -0.1, "bu20": 0.0, "at_hi20": False, "at_lo20": True}
    chk("C04 做空＝20日低", pass_short("C04", rec_c04s))
    rec_t07 = {
        "sid": "E",
        "rsi2": 40.0,
        "macd_hist_weekly": 0.2,
        "macd_hist_weekly_prev": 0.1,
    }
    chk("T07 兩屏做多", pass_long("T07", rec_t07) and not pass_short("T07", rec_t07))
    rec_t07_slope = {**rec_t07, "macd_hist_weekly": 0.05, "macd_hist_weekly_prev": 0.2}
    chk("T07 柱斜率負拒", not pass_long("T07", rec_t07_slope))
    rec_t07_rsi = {**rec_t07, "rsi2": 50.0}
    chk("T07 RSI2＝50 拒（須嚴格＜50）", not pass_long("T07", rec_t07_rsi))
    rec_t07s = {
        "sid": "S",
        "rsi2": 60.0,
        "macd_hist_weekly": -0.2,
        "macd_hist_weekly_prev": -0.1,
    }
    chk("T07 兩屏做空", pass_short("T07", rec_t07s) and not pass_long("T07", rec_t07s))
    flat_ema = ema_series([10.0] * 20, 5)
    chk("EMA 常數＝常數", flat_ema is not None and all(abs(x - 10.0) < 1e-12 for x in flat_ema if x is not None))
    hist_flat = macd_histogram_series([10.0] * 50)
    finite_h = [x for x in (hist_flat or []) if x is not None]
    chk("平價 MACD 柱≈0", bool(finite_h) and all(abs(x) < 1e-9 for x in finite_h[-5:]))
    wk = sample_stride(list(range(1, 21)), 5)
    chk("週抽樣含末點", wk[-1] == 20 and wk == [5, 10, 15, 20])
    flat = [10.0] * 210
    filled = fill_w2_indicators({"sid": "F", "dd20": 0.0, "bu20": 0.0}, flat)
    chk("fill_w2 sma200", filled.get("sma200") == 10.0 and filled.get("sma200_prev") == 10.0)
    chk("fill_w2 斜率平", not _gt(filled.get("sma200"), filled.get("sma200_prev")))
    chk("fill_w3 approx", filled.get("t07_approx") == T07_APPROX)
    chk("平價 T07 拒（RSI2＝50 且柱平）", not pass_long("T07", filled) and not pass_short("T07", filled))
    up_cl = [100.0 + 0.2 * i for i in range(220)]
    filled_up = fill_w2_indicators({"sid": "U", "dd20": 0.0, "bu20": 0.0}, up_cl)
    chk("純上升有週柱", filled_up.get("macd_hist_weekly") is not None)
    chk("純上升 RSI2 不＜50 故 T07 拒", not pass_long("T07", filled_up))
    p = 100.0
    rocket = []
    for _ in range(200):
        p *= 1.01
        rocket.append(p)
    for _ in range(18):
        p *= 1.02
        rocket.append(p)
    rocket.append(rocket[-1] * 0.98)
    filled_dip = fill_w2_indicators({"sid": "D", "dd20": -0.04, "bu20": 0.0}, rocket)
    chk(
        "強加速潮＋末日約2%拉回過 T07",
        pass_long("T07", filled_dip)
        and _lt(filled_dip.get("rsi2"), T07_RSI2_LONG)
        and _gt(filled_dip.get("macd_hist_weekly"), filled_dip.get("macd_hist_weekly_prev")),
    )
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測: python -m augur.evaluation.trend_pullback_catalog --selftest；免 DB 免 API)")
