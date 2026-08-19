"""CHARGE-T5-v1 — 衝勢 5 日進出（規則模型；純函式；探針與自測共用）。

🎯 這支在做什麼（白話）：長窗仍多、結構未破、近 5／10 日還在漲的第一天進，
   五個交易日出。同日多名依 mean(H60,H120,H240) 取最多 k=10、等權。
   兩檔研究不是本模型績效。不是 RankRidge、不是可交易。T20／T40／抱牢只對照。

執行指令矩陣（本檔=library #18；自測免 DB 免 API）:
  python -m augur.evaluation.charge_t5
  python -m augur.evaluation.charge_t5 --selftest
"""
from __future__ import annotations

from datetime import date
from typing import Mapping, Optional, Sequence

import math

from augur.evaluation import twin_ex as tx
from augur.evaluation import uptrend_pullback as up

VERSION = "CHARGE-T5-v1"
K_DEFAULT = 10
HOLD_MODEL = 5
CONTRAST_HOLDS = (10, 20, 40)
COST_ROUNDTRIP_DEFAULT = tx.COST_ROUNDTRIP_DEFAULT
IS_START = tx.IS_START
IS_END = tx.IS_END
OOS_START = tx.OOS_START
OOS_END = tx.OOS_END
TIP_DEFAULT = tx.TIP_DEFAULT


def pit_sets(snaps: Sequence[tuple[date, set]], cal: Sequence[date]) -> list:
    """每個交易日的 PIT 宇宙＝最近 as_of≤該日。完全沒有更早快照 → None（跳過）。"""
    ordered = sorted((d, set(sids)) for d, sids in snaps)
    out = [None] * len(cal)
    j = -1
    n_sn = len(ordered)
    for i, d in enumerate(cal):
        while j + 1 < n_sn and ordered[j + 1][0] <= d:
            j += 1
        out[i] = None if j < 0 else ordered[j][1]
    return out


def sid_series(closes: Sequence[Optional[float]]):
    """逐日 E-charge 旗標與排序鍵。缺特徵 → flag False、score None。"""
    n = len(closes)
    flags = [False] * n
    scores = [None] * n
    arr = [None] * n
    for i, c in enumerate(closes):
        v = tx._f(c)
        arr[i] = v
    need = tx.MIN_LOOKBACK
    for i in range(need, n):
        p0 = arr[i]
        if p0 is None:
            continue
        rets = {}
        ok = True
        for h in up.H_TRACK:
            ph = arr[i - h]
            if ph is None:
                ok = False
                break
            rets[h] = math.log(p0 / ph)
        if not ok:
            continue
        w20 = arr[i - 19: i + 1]
        if any(x is None for x in w20):
            continue
        w252 = arr[i - 251: i + 1]
        if any(x is None for x in w252):
            continue
        hi, lo = max(w252), min(w252)
        p2h = p0 / hi
        cyc = (p0 - lo) / (hi - lo) if hi > lo else None
        flags[i] = tx.entry_charge(rets, cyc, p2h)
        scores[i] = up.mean_rank_ret(rets)
    return flags, scores


def timed_exit(entry: int, hold: int, *, n: int, max_i: int) -> Optional[int]:
    x = entry + int(hold)
    if x >= n or x > max_i:
        return None
    return x


def select_book(
    flags_by: Mapping[str, Sequence[bool]],
    scores_by: Mapping[str, Sequence[Optional[float]]],
    uni_by_i: Sequence[Optional[set]],
    closes_by: Mapping[str, Sequence[Optional[float]]],
    dates: Sequence[date],
    *,
    k: int = K_DEFAULT,
    hold: int = HOLD_MODEL,
    max_i: int,
) -> list[dict]:
    """日曆序：在宇宙內、轉折、未在倉、T5 能完成者，當日依 score 降序取 k。"""
    n = len(dates)
    busy_until = {sid: -1 for sid in flags_by}
    trades = []
    for i in range(1, n):
        uni = uni_by_i[i]
        if not uni:
            continue
        cands = []
        for sid in uni:
            fl = flags_by.get(sid)
            sc = scores_by.get(sid)
            if fl is None or sc is None:
                continue
            if busy_until.get(sid, -1) >= i:
                continue
            if not (fl[i] and not fl[i - 1]):
                continue
            score = sc[i]
            if score is None:
                continue
            entry = i + 1
            exit_i = timed_exit(entry, hold, n=n, max_i=max_i)
            px_e = tx._f(closes_by.get(sid, [None] * n)[entry] if entry < n else None)
            px_x = (
                tx._f(closes_by.get(sid, [None] * n)[exit_i])
                if exit_i is not None else None
            )
            if exit_i is None or px_e is None or px_x is None:
                continue
            cands.append((float(score), str(sid), entry, exit_i, px_e, px_x))
        cands.sort(key=lambda r: (-r[0], r[1]))
        truncated = max(0, len(cands) - int(k))
        for score, sid, entry, exit_i, px_e, px_x in cands[: int(k)]:
            trades.append({
                "sid": sid,
                "signal": dates[i],
                "signal_i": i,
                "entry": dates[entry],
                "exit": dates[exit_i],
                "hold_td": int(exit_i - entry),
                "ret": px_x / px_e - 1.0,
                "score": score,
                "n_cands": len(cands),
                "truncated": truncated,
            })
            busy_until[sid] = exit_i
    return trades


def ret_at_hold(
    trade: dict,
    closes_by: Mapping[str, Sequence[Optional[float]]],
    dates: Sequence[date],
    hold: int,
    *,
    max_i: int,
) -> Optional[float]:
    """同一進場、改持有日。完不成 → None。"""
    cal_i = {d: j for j, d in enumerate(dates)}
    entry_i = cal_i.get(trade["entry"])
    if entry_i is None:
        return None
    n = len(dates)
    exit_i = timed_exit(entry_i, hold, n=n, max_i=max_i)
    closes = closes_by.get(trade["sid"], [])
    pe = tx._f(closes[entry_i] if entry_i < len(closes) else None)
    px = tx._f(closes[exit_i] if exit_i is not None and exit_i < len(closes) else None)
    if pe is None or px is None:
        return None
    return px / pe - 1.0


def baskets_from_trades(trades: Sequence[dict]) -> list[dict]:
    """同訊號日等權。"""
    by = {}
    for t in trades:
        by.setdefault(t["signal"], []).append(t)
    out = []
    for sig in sorted(by):
        rows = by[sig]
        rets = [float(t["ret"]) for t in rows]
        n = len(rows)
        out.append({
            "signal": sig,
            "n": n,
            "ret": sum(rets) / n if n else 0.0,
            "truncated": int(rows[0].get("truncated") or 0),
            "n_cands": int(rows[0].get("n_cands") or n),
            "sids": [t["sid"] for t in rows],
        })
    return out


def window_from_baskets(baskets: Sequence[dict], pred, *, cost: float) -> dict:
    rows = [b for b in baskets if pred(b["signal"])]
    rets = [float(b["ret"]) for b in rows]
    nets = tx.apply_cost(rets, cost)
    n = len(rows)
    wins = sum(1 for r in rets if r > 0)
    names = sum(int(b["n"]) for b in rows)
    trunc_days = sum(1 for b in rows if int(b.get("truncated") or 0) > 0)
    return {
        "n_baskets": n,
        "n_names": names,
        "wins": wins,
        "compound_pct": None if n == 0 else (tx.compound_mult(rets) - 1.0) * 100.0,
        "compound_cost_pct": None if n == 0 else (tx.compound_mult(nets) - 1.0) * 100.0,
        "mean_ret_pct": None if n == 0 else sum(rets) / n * 100.0,
        "mean_n": None if n == 0 else names / n,
        "trunc_days": trunc_days,
    }


def window_from_trades(trades: Sequence[dict], pred, *, cost: float) -> dict:
    return tx.window_stats(trades, pred, cost=cost)


def both_windows_positive(is_s: dict, oos_s: dict) -> bool:
    ic = is_s.get("compound_pct")
    oc = oos_s.get("compound_pct")
    return ic is not None and oc is not None and float(ic) > 0 and float(oc) > 0


def contrast_hold_baskets(
    trades: Sequence[dict],
    closes_by,
    dates,
    hold: int,
    *,
    max_i: int,
    cost: float,
) -> dict:
    rows = []
    for t in trades:
        r = ret_at_hold(t, closes_by, dates, hold, max_i=max_i)
        if r is None:
            continue
        rows.append({**t, "ret": r, "hold_td": hold})
    bsk = baskets_from_trades(rows)
    return {
        "hold": hold,
        "n_complete": len(rows),
        "is": window_from_baskets(bsk, tx.in_is, cost=cost),
        "oos": window_from_baskets(bsk, tx.in_oos, cost=cost),
        "bh_like": hold >= 20,
        "contrast_only": hold >= 40,
    }


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("VERSION", VERSION == "CHARGE-T5-v1")
    chk("k=10", K_DEFAULT == 10)
    chk("模型持有 5", HOLD_MODEL == 5)
    chk("T40 對照", 40 in CONTRAST_HOLDS)
    chk("切窗同 TWIN-EX", IS_START == tx.IS_START and OOS_END == tx.OOS_END)

    cal = [date(2024, 1, 1 + i) for i in range(20)]
    snaps = [(date(2023, 12, 31), {"A", "B", "C"})]
    uni = pit_sets(snaps, cal)
    chk("PIT 帶前", uni[0] == {"A", "B", "C"} and uni[-1] == {"A", "B", "C"})
    chk("無快照跳過", pit_sets([(date(2024, 6, 1), {"A"})], cal)[0] is None)

    n = 16
    dates = [date(2024, 1, 1 + i) for i in range(n)]
    # 12 檔同日轉折：score = 序號，取最高 10
    flags_by, scores_by, closes_by = {}, {}, {}
    uni_sets = [None] + [{"%02d" % j for j in range(12)}] * (n - 1)
    for j in range(12):
        sid = "%02d" % j
        fl = [False] * n
        fl[2] = True  # 轉折於 i=2
        sc = [None] * n
        sc[2] = float(j)
        cl = [10.0] * n
        cl[3] = 10.0
        cl[8] = 11.0 + j * 0.0  # 全 +10%
        flags_by[sid] = fl
        scores_by[sid] = sc
        closes_by[sid] = cl
    tr = select_book(
        flags_by, scores_by, uni_sets, closes_by, dates,
        k=10, hold=5, max_i=n - 1,
    )
    chk("同日 k 上限", len(tr) == 10)
    chk("取分數高者", set(t["sid"] for t in tr) == {"%02d" % j for j in range(2, 12)})
    chk("截斷數", tr[0]["truncated"] == 2)
    bsk = baskets_from_trades(tr)
    chk("一籃", len(bsk) == 1 and abs(bsk[0]["ret"] - 0.10) < 1e-12)

    # 兩籃等權連乘
    t2 = [
        {"sid": "X", "signal": date(2024, 2, 1), "ret": 0.10, "truncated": 0, "n_cands": 1},
        {"sid": "Y", "signal": date(2024, 2, 1), "ret": 0.00, "truncated": 0, "n_cands": 2},
        {"sid": "Z", "signal": date(2024, 3, 1), "ret": 0.10, "truncated": 0, "n_cands": 1},
    ]
    b2 = baskets_from_trades(t2)
    chk("等權第一籃 +5%", abs(b2[0]["ret"] - 0.05) < 1e-12)
    w = window_from_baskets(b2, lambda d: True, cost=0.0)
    chk("兩籃連乘", abs(w["compound_pct"] - ((1.05 * 1.10) - 1.0) * 100.0) < 1e-9)

    is_pos = {"compound_pct": 1.0}
    oos_pos = {"compound_pct": 2.0}
    chk("兩窗同號", both_windows_positive(is_pos, oos_pos))
    chk("OOS 負不當綠", not both_windows_positive(is_pos, {"compound_pct": -1.0}))
    chk("成本預設同 TWIN-EX", abs(COST_ROUNDTRIP_DEFAULT - 0.00585) < 1e-12)
    # sid_series 與 features_at 同閘
    path = [100.0 * (1.001 ** i) for i in range(300)]
    fl, sc = sid_series(path)
    feat = tx.features_at(path, 280)
    chk("sid_series 對齊 features_at", feat is not None and fl[280] == tx.entry_charge(feat[0], feat[2], feat[3]))
    chk("sid_series 有排序鍵", sc[280] is not None)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測: python -m augur.evaluation.charge_t5 --selftest；免 DB 免 API)")
