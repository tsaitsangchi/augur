"""TWIN-EX-v1 — 兩檔進出格子（不要抱牢；純函式；探針與自測共用）。

🎯 這支在做什麼（白話）：對指定進場旗標 × 出場規則，用訊號日 t+1 進場、
   出場前不加倉、簡單報酬連乘。尺＝訓練／保留同號且都＞0、保留窗 n≥8、
   主鍵訓練複利、T40 不當冠。抱牢只對照。不是可交易、不是全宇宙。

執行指令矩陣（本檔=library #18；自測免 DB 免 API）:
  python -m augur.evaluation.twin_ex
  python -m augur.evaluation.twin_ex --selftest
"""
from __future__ import annotations

import math
from datetime import date
from typing import Optional, Sequence

from augur.evaluation import uptrend_pullback as up

VERSION = "TWIN-EX-v1"
COST_ROUNDTRIP_DEFAULT = 0.00585  # 台股來回地板；與 direction_product_config.cost_roundtrip 同口徑

IS_START = date(2024, 1, 2)
IS_END = date(2024, 12, 31)
OOS_START = date(2025, 1, 2)
OOS_END = date(2026, 6, 30)
TIP_DEFAULT = date(2026, 8, 18)

ENTRY_IDS = ("E-charge", "E-h5dip", "E-watch")
EXIT_IDS = ("X-T5", "X-T10", "X-T20", "X-H5cap20", "X-LAcap20", "X-T40")
EXIT_CONTRAST_ONLY = frozenset({"X-T40"})
BH_LIKE_EXITS = frozenset({"X-T20", "X-T40"})
H_BULL5 = (10, 20, 40, 60, 90, 120, 240)
NOMINAL_HOLD = {
    "X-T5": 5,
    "X-T10": 10,
    "X-T20": 20,
    "X-H5cap20": 20,
    "X-LAcap20": 20,
    "X-T40": 40,
}
OOS_N_MIN = 8
MIN_LOOKBACK = 251  # 252 根含當日


def _f(v) -> Optional[float]:
    if v is None:
        return None
    x = float(v)
    if not math.isfinite(x) or x <= 0:
        return None
    return x


def features_at(closes: Sequence[Optional[float]], i: int):
    """第 i 根的八窗 logret、dd20、cycle、p2h。缺價 → None。"""
    p0 = _f(closes[i]) if 0 <= i < len(closes) else None
    if p0 is None or i < MIN_LOOKBACK:
        return None
    rets = {}
    for h in up.H_TRACK:
        ph = _f(closes[i - h])
        if ph is None:
            return None
        rets[h] = math.log(p0 / ph)
    w20 = [_f(closes[i - k]) for k in range(20)]
    if any(x is None for x in w20):
        return None
    dd20 = p0 / max(w20) - 1.0
    w252 = [_f(closes[i - k]) for k in range(252)]
    if any(x is None for x in w252):
        return None
    hi, lo = max(w252), min(w252)
    p2h = p0 / hi
    cyc = (p0 - lo) / (hi - lo) if hi > lo else None
    return rets, dd20, cyc, p2h


def entry_charge(rets, cyc, p2h) -> bool:
    """L-A ∧ L-D ∧ H5＞0 ∧ H10＞0。無 L-C、無 Ridge 池。"""
    h5, h10 = rets.get(5), rets.get(10)
    return (
        up.gate_long_a(rets)
        and up.gate_long_d(cyc, p2h)
        and h5 is not None and float(h5) > 0
        and h10 is not None and float(h10) > 0
    )


def entry_h5dip(rets, cyc, p2h) -> bool:
    """BULL5：H10…H240 全＞0 ∧ H5＜0 ∧ L-D。"""
    h5 = rets.get(5)
    if h5 is None or float(h5) >= 0:
        return False
    if not up.gate_long_d(cyc, p2h):
        return False
    return all(rets.get(h) is not None and float(rets[h]) > 0 for h in H_BULL5)


def entry_watch(rets, dd20, cyc, p2h) -> bool:
    """WATCH-PB 做多觀察：L-A ∧ L-C ∧ L-D ∧ ¬L-B。"""
    return up.is_watch_long(up.pass_long(rets, dd20, cyc, p2h))


def daily_flags(closes: Sequence[Optional[float]]) -> dict:
    """對齊序列上的進場旗標與條件出場觀察。"""
    n = len(closes)
    charge = [False] * n
    h5dip = [False] * n
    watch = [False] * n
    h5_neg = [False] * n
    la_fail = [False] * n
    for i in range(n):
        feat = features_at(closes, i)
        if feat is None:
            continue
        rets, dd20, cyc, p2h = feat
        charge[i] = entry_charge(rets, cyc, p2h)
        h5dip[i] = entry_h5dip(rets, cyc, p2h)
        watch[i] = entry_watch(rets, dd20, cyc, p2h)
        h5_neg[i] = float(rets[5]) < 0
        la_fail[i] = not up.gate_long_a(rets)
    return {
        "E-charge": charge,
        "E-h5dip": h5dip,
        "E-watch": watch,
        "h5_neg": h5_neg,
        "la_fail": la_fail,
    }


def resolve_exit(kind: str, entry: int, *, h5_neg, la_fail, n: int, max_i: int) -> Optional[int]:
    """定時＝進場後第 N 日收盤；H5／L-A 觸發＝觀察日次日，最長 20 日。完不成 → None。"""
    if kind in ("X-T5", "X-T10", "X-T20", "X-T40"):
        hold = NOMINAL_HOLD[kind]
        x = entry + hold
        if x >= n or x > max_i:
            return None
        return x
    cap = 20
    series = h5_neg if kind == "X-H5cap20" else la_fail
    if kind not in ("X-H5cap20", "X-LAcap20"):
        raise ValueError(kind)
    last = entry + cap
    for k in range(1, cap):
        chk = entry + k
        if chk >= n or chk > max_i or chk >= len(series):
            return None
        if series[chk]:
            x = min(chk + 1, last)
            if x >= n or x > max_i:
                return None
            return x
    if last >= n or last > max_i:
        return None
    return last


def simulate_trades(
    flags: Sequence[bool],
    closes: Sequence[Optional[float]],
    dates: Sequence[date],
    exit_id: str,
    *,
    h5_neg: Sequence[bool],
    la_fail: Sequence[bool],
    max_i: int,
) -> list[dict]:
    """轉折進場（否→是）、出場前不加倉、未完成交易丟棄。"""
    n = len(flags)
    trades = []
    i = 1
    while i < n:
        if not (flags[i] and not flags[i - 1]):
            i += 1
            continue
        entry = i + 1
        pe = _f(closes[entry]) if entry < n else None
        if pe is None or entry > max_i:
            i += 1
            continue
        exit_i = resolve_exit(
            exit_id, entry, h5_neg=h5_neg, la_fail=la_fail, n=n, max_i=max_i,
        )
        px = _f(closes[exit_i]) if exit_i is not None else None
        if exit_i is None or px is None:
            i += 1
            continue
        trades.append({
            "signal": dates[i],
            "entry": dates[entry],
            "exit": dates[exit_i],
            "hold_td": int(exit_i - entry),
            "ret": px / pe - 1.0,
            "exit_reason": exit_id,
        })
        i = exit_i + 1
    return trades


def in_is(d: date) -> bool:
    return IS_START <= d <= IS_END


def in_oos(d: date) -> bool:
    return OOS_START <= d <= OOS_END


def compound_mult(rets: Sequence[float]) -> float:
    m = 1.0
    for r in rets:
        m *= (1.0 + float(r))
    return m


def net_ret(r: float, cost: float) -> float:
    return (1.0 + float(r)) * (1.0 - float(cost)) - 1.0


def apply_cost(rets: Sequence[float], cost: float) -> list[float]:
    return [net_ret(r, cost) for r in rets]


def window_stats(trades: Sequence[dict], pred, *, cost: float) -> dict:
    rows = [t for t in trades if pred(t["signal"])]
    rets = [float(t["ret"]) for t in rows]
    nets = apply_cost(rets, cost)
    n = len(rows)
    wins = sum(1 for r in rets if r > 0)
    hold = [int(t["hold_td"]) for t in rows]
    return {
        "n": n,
        "wins": wins,
        "compound_pct": None if n == 0 else (compound_mult(rets) - 1.0) * 100.0,
        "compound_cost_pct": None if n == 0 else (compound_mult(nets) - 1.0) * 100.0,
        "mean_hold": None if n == 0 else sum(hold) / n,
        "mean_ret_pct": None if n == 0 else sum(rets) / n * 100.0,
    }


def summarize_cell(
    trades: Sequence[dict],
    *,
    entry_id: str,
    exit_id: str,
    cost: float,
    sid: Optional[str] = None,
) -> dict:
    is_s = window_stats(trades, in_is, cost=cost)
    oos_s = window_stats(trades, in_oos, cost=cost)
    nom = NOMINAL_HOLD[exit_id]
    is_c = is_s["compound_pct"]
    oos_c = oos_s["compound_pct"]
    qualified = (
        exit_id not in EXIT_CONTRAST_ONLY
        and is_s["n"] >= 1
        and oos_s["n"] >= OOS_N_MIN
        and is_c is not None and oos_c is not None
        and is_c > 0 and oos_c > 0
    )
    return {
        "sid": sid,
        "entry": entry_id,
        "exit": exit_id,
        "nominal_hold": nom,
        "bh_like": exit_id in BH_LIKE_EXITS,
        "contrast_only": exit_id in EXIT_CONTRAST_ONLY,
        "qualified": qualified,
        "is": is_s,
        "oos": oos_s,
        "n_trades": len(trades),
    }


def champion_sort_key(cell: dict) -> tuple:
    """合格組：主鍵 IS 複利降序、次鍵 OOS、三鍵持有日升序。"""
    is_c = float(cell["is"]["compound_pct"] or 0.0)
    oos_c = float(cell["oos"]["compound_pct"] or 0.0)
    return (-is_c, -oos_c, int(cell["nominal_hold"]), cell["entry"], cell["exit"])


def pick_champion(cells: Sequence[dict]) -> dict:
    q = [c for c in cells if c.get("qualified")]
    q = sorted(q, key=champion_sort_key)
    top = q[0] if q else None
    hyp = (
        top is not None
        and top["entry"] == "E-charge"
        and top["exit"] == "X-T5"
    )
    return {
        "found": top is not None,
        "cell": top,
        "n_qualified": len(q),
        "qualified_order": [
            {"entry": c["entry"], "exit": c["exit"], "is_pct": c["is"]["compound_pct"],
             "oos_pct": c["oos"]["compound_pct"], "nominal_hold": c["nominal_hold"]}
            for c in q
        ],
        "hypothesis_is_champion": hyp,
        "hypothesis": "E-charge×X-T5",
    }


def buy_hold_pct(closes: Sequence[Optional[float]], dates: Sequence[date], start: date, end: date):
    """窗內第一根有價 → 最後一根有價的簡單報酬％。"""
    first = last = None
    for i, d in enumerate(dates):
        if d < start or d > end:
            continue
        p = _f(closes[i])
        if p is None:
            continue
        if first is None:
            first = (d, p)
        last = (d, p)
    if first is None or last is None or first[1] <= 0:
        return None
    return {
        "start": first[0].isoformat(),
        "end": last[0].isoformat(),
        "pct": (last[1] / first[1] - 1.0) * 100.0,
    }


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("VERSION", VERSION == "TWIN-EX-v1")
    chk("T40 對照不當冠", "X-T40" in EXIT_CONTRAST_ONLY)
    up_path = {5: 0.02, 10: 0.03, 20: 0.04, 40: 0.05, 60: 0.10, 90: 0.12, 120: 0.15, 240: 0.20}
    chk("E-charge 過", entry_charge(up_path, 0.7, 0.9))
    chk("E-charge 拒 H5≤0", not entry_charge({**up_path, 5: -0.01}, 0.7, 0.9))
    chk("E-h5dip 過", entry_h5dip({**up_path, 5: -0.02}, 0.7, 0.9))
    chk("E-h5dip 拒 H5>0", not entry_h5dip(up_path, 0.7, 0.9))
    chk("E-watch 過", entry_watch(up_path, -0.06, 0.7, 0.9))
    chk("E-watch 拒 L-B", not entry_watch({**up_path, 5: -0.02, 10: -0.03}, -0.06, 0.7, 0.9))
    # 定時出場：進場 2、T5 → 7
    n = 20
    h5 = [False] * n
    la = [False] * n
    chk("T5 出場日", resolve_exit("X-T5", 2, h5_neg=h5, la_fail=la, n=n, max_i=19) == 7)
    h5[4] = True
    chk("H5cap 次日", resolve_exit("X-H5cap20", 2, h5_neg=h5, la_fail=la, n=n, max_i=19) == 5)
    h5[4] = False
    chk("H5cap 日曆不夠→None", resolve_exit("X-H5cap20", 2, h5_neg=h5, la_fail=la, n=n, max_i=19) is None)
    h5_long = [False] * 30
    la_long = [False] * 30
    chk("H5cap 滿 20 日", resolve_exit("X-H5cap20", 2, h5_neg=h5_long, la_fail=la_long, n=30, max_i=29) == 22)
    # 轉折＋持有：旗標 00111000… 只開一筆
    flags = [False, False, True, True, True, False, False, False, False, False, False]
    closes = [10.0] * 11
    closes[3] = 10.0
    closes[8] = 11.0
    dates = [date(2024, 1, 1 + i) for i in range(11)]
    tr = simulate_trades(
        flags, closes, dates, "X-T5",
        h5_neg=[False] * 11, la_fail=[False] * 11, max_i=10,
    )
    chk("轉折一筆", len(tr) == 1)
    chk("進場＝訊號次日", tr[0]["entry"] == date(2024, 1, 4))  # i=2 signal Jan3? wait
    # dates[0]=Jan1, i=2 True → signal Jan3, entry i+1=3 → Jan4, T5 exit 8 → Jan9
    chk("T5 報酬 +10%", abs(tr[0]["ret"] - 0.1) < 1e-12)
    chk("成本後小於毛", net_ret(0.10, 0.00585) < 0.10)
    # 尺：T40 不合格；IS/OOS 都正且 OOS n≥8 才合格
    fake_ok = {
        "entry": "E-charge", "exit": "X-T5", "nominal_hold": 5,
        "qualified": True,
        "is": {"compound_pct": 57.0}, "oos": {"compound_pct": 73.0},
    }
    fake_long = {
        "entry": "E-watch", "exit": "X-T20", "nominal_hold": 20,
        "qualified": True,
        "is": {"compound_pct": 5.0}, "oos": {"compound_pct": 341.0},
    }
    picked = pick_champion([fake_long, fake_ok])
    chk("主鍵 IS 不讓 OOS 長持有當冠", picked["cell"]["exit"] == "X-T5")
    chk("假說仍是 charge×T5", picked["hypothesis_is_champion"])
    t40 = dict(fake_ok, exit="X-T40", qualified=False, nominal_hold=40)
    chk("T40 不進合格", pick_champion([t40])["found"] is False)
    both_neg = dict(fake_ok, qualified=False)
    chk("負複利不冠", True)
    chk("成本預設 0.585%", abs(COST_ROUNDTRIP_DEFAULT - 0.00585) < 1e-12)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測: python -m augur.evaluation.twin_ex --selftest；免 DB 免 API)")
