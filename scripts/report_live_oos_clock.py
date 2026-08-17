#!/usr/bin/env python
"""E4b live OOS 鐘 — 從指定出門 as-of 數非重疊已實現 H 期（唯讀、不算報酬）。

🎯 這支在做什麼（白話）：確立閘要 live_oos_k=4 個非重疊已實現持有。本支只回答
   「現在數到幾、下一筆何時到期、是否仍 WAIT」。價未蓋滿 → 不編 PnL。
   每日重疊出門不當獨立 T。H20 可附印，不當復活證據。

對齊 E4b-clock-go。進出場＝evaluation.label._entry_exit。非重疊＝h×1.45×0.9 日曆日
（與 run_economic_eval / 閘 criteria 同尺）。已實現＝PriceAdj tip ≥ exit。
未來 as-of 用 TaiwanStockTradingDate 投影（不是 PriceAdj，PriceAdj 不含未來日）。
日曆不夠長 → 誠實印 calendar_exhausted，不編假日。

守 #8（不外推價、不用 08-15/16/17 當 as-of）· #14（鐘 ≠ 報酬）· #15。

執行指令矩陣:
  python scripts/report_live_oos_clock.py --origin 2026-08-14 --h 60
  python scripts/report_live_oos_clock.py --selftest
"""
from __future__ import annotations

import argparse
import json
from datetime import date

import _bootstrap  # noqa: F401
from augur.core import asof_ready, db
from augur.core.closed_horizons import CAL_DAYS, H_TRACK
from augur.evaluation import label as label_mod

K_DEFAULT = 4
CAL_TABLE = "TaiwanStockTradingDate"


def _nonoverlap(panels, h):
    if not panels:
        return []
    need = h * 1.45 * 0.9
    out = [panels[0]]
    for p in panels[1:]:
        if (p - out[-1]).days >= need:
            out.append(p)
    return out


def _window(cal, asof, h):
    after = [d for d in cal if d > asof]
    return label_mod._entry_exit(after, h)


def _status(asof, entry, exit_, *, tip, emitted, cal_max):
    if entry is None or exit_ is None:
        return "calendar_exhausted"
    if not emitted:
        if asof > tip:
            return "scheduled"
        return "no_emit"
    if tip < entry:
        return "waiting_entry_px"
    if tip < exit_:
        return "waiting_exit"
    return "realized_calendar"  # 價蓋到 exit；本支仍不算報酬


def _emit_horizons(conn, asof):
    with db.transaction(conn) as cur:
        cur.execute(
            """
            SELECT mr.horizon, count(*)
              FROM prediction_values pv
              JOIN model_registry mr USING (model_id)
             WHERE pv.panel_date=%s
             GROUP BY 1 ORDER BY 1
            """,
            (asof,),
        )
        return {int(h): int(n) for h, n in cur.fetchall()}


def _load_cal_and_tip(conn):
    with db.transaction(conn) as cur:
        cur.execute(f'SELECT date FROM "{CAL_TABLE}" ORDER BY date')
        cal = [r[0] for r in cur.fetchall()]
        tip = asof_ready.taiex_price_max(cur)
        cur.execute(
            "SELECT gate_id, status, approved_at FROM econ_establishment_gate"
        )
        gate = cur.fetchone()
        cur.execute(
            "SELECT horizon, verdict FROM econ_verdict_rule "
            "WHERE horizon IN (20, 60) ORDER BY 1"
        )
        verd = list(cur.fetchall())
    return cal, tip, gate, verd


def _periods(cal, origin, h, k, *, tip, origin_emitted):
    cands = [d for d in cal if d >= origin]
    if origin not in cands:
        cands = [origin] + cands
    seq = _nonoverlap(cands, h)
    rows = []
    for i, asof in enumerate(seq[:k], 1):
        entry, exit_ = _window(cal, asof, h)
        emitted = origin_emitted if asof == origin else False
        st = _status(asof, entry, exit_, tip=tip, emitted=emitted, cal_max=cal[-1] if cal else None)
        if entry is None or exit_ is None:
            st = "window_beyond_calendar"
        elif asof > tip and asof != origin:
            st = "scheduled"
        rows.append(
            {
                "k": i,
                "asof": asof,
                "entry": entry,
                "exit": exit_,
                "emitted": bool(asof == origin and origin_emitted),
                "status": st,
            }
        )
        if st == "window_beyond_calendar":
            break
    return rows, h * 1.45 * 0.9


def run(*, origin: date, h: int, k: int) -> int:
    if h not in H_TRACK:
        print(f"✗ H={h} 不在 H_TRACK")
        return 2
    with db.connect() as conn:
        cal, tip, gate, verd = _load_cal_and_tip(conn)
        emits = _emit_horizons(conn, origin)
    origin_emitted = (h in emits) and emits[h] > 0
    rows, need = _periods(cal, origin, h, k, tip=tip, origin_emitted=origin_emitted)
    n_real = sum(1 for r in rows if r["status"] == "realized_calendar")
    first_open = next((r for r in rows if r["status"] != "realized_calendar"), None)
    clock = "WAIT" if n_real < k else "K_REACHED"
    next_due = None
    if first_open:
        next_due = first_open.get("exit") or first_open.get("asof")

    # H20 披露
    rows20 = []
    if h != 20:
        e20 = (20 in emits) and emits[20] > 0
        rows20, _ = _periods(cal, origin, 20, 1, tip=tip, origin_emitted=e20)

    payload = {
        "origin": str(origin),
        "h": h,
        "k_required": k,
        "already_realized_nonoverlap": n_real,
        "next_due_date": str(next_due) if next_due else None,
        "clock": clock,
        "priceadj_tip": str(tip),
        "trading_cal_max": str(cal[-1]) if cal else None,
        "nonoverlap_need_days": need,
        "origin_emit_rows": emits,
        "origin_emitted_h": origin_emitted,
        "gate": {
            "id": gate[0] if gate else None,
            "status": gate[1] if gate else None,
            "approved_at": str(gate[2]) if gate else None,
        },
        "verdict": verd,
        "periods": [
            {
                **{kk: (str(vv) if isinstance(vv, date) else vv) for kk, vv in r.items()}
            }
            for r in rows
        ],
        "h20_disclosure": [
            {kk: (str(vv) if isinstance(vv, date) else vv) for kk, vv in r.items()}
            for r in rows20
        ],
        "cal_days_approx": CAL_DAYS.get(h),
        "no_realized_pnl": True,
    }

    print(f"origin={origin} H={h} K={k}  PriceAdj_tip={tip}  cal_max={cal[-1] if cal else None}")
    print(f"emit@{origin}: {emits}")
    print(f"nonoverlap_need={need:.1f} 日曆日  (h×1.45×0.9)")
    print(f"already_realized_nonoverlap={n_real}  clock={clock}  next_due_date={next_due}")
    print(f"{'k':>2} {'asof':<12} {'entry':<12} {'exit':<12} {'emit':<5} status")
    for r in rows:
        print(
            f"{r['k']:>2} {str(r['asof']):<12} {str(r['entry'] or '—'):<12} "
            f"{str(r['exit'] or '—'):<12} {str(r['emitted']):<5} {r['status']}"
        )
    if rows20:
        r = rows20[0]
        print(
            f"H20 披露（≠復活）: asof={r['asof']} entry={r['entry']} "
            f"exit={r['exit']} status={r['status']}"
        )
    print("no-realized-pnl: 本支不編報酬／Sharpe／淨值")
    outp = f"/tmp/e4b-clock-H{h}-{origin.isoformat()}.json"
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)
    print(f"json {outp}")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    cal = [date(2026, 1, d) for d in range(2, 32) if date(2026, 1, d).weekday() < 5]
    cal += [date(2026, 2, d) for d in range(1, 29) if date(2026, 2, d).weekday() < 5]
    origin = date(2026, 1, 2)
    e, x = _window(cal, origin, 5)
    chk("entry=origin 次一交易日", e == date(2026, 1, 5))
    chk("_entry_exit 日曆不足→None", _window(cal, date(2026, 2, 27), 5) == (None, None))
    seq = _nonoverlap(cal, 60)
    chk("非重疊第一個=序列首", seq[0] == cal[0])
    if len(seq) >= 2:
        chk("非重疊間距≥h×1.45×0.9", (seq[1] - seq[0]).days >= 60 * 1.45 * 0.9)
    st = _status(origin, date(2026, 1, 5), date(2026, 4, 1), tip=date(2026, 1, 2), emitted=True, cal_max=cal[-1])
    chk("tip<entry → waiting_entry_px", st == "waiting_entry_px")
    st2 = _status(origin, date(2026, 1, 5), date(2026, 4, 1), tip=date(2026, 4, 1), emitted=True, cal_max=cal[-1])
    chk("tip≥exit → realized_calendar", st2 == "realized_calendar")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="E4b live OOS 鐘（唯讀、不算報酬）")
    ap.add_argument("--origin", default="2026-08-14")
    ap.add_argument("--h", type=int, default=60)
    ap.add_argument("--k", type=int, default=K_DEFAULT)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    return run(origin=date.fromisoformat(args.origin), h=args.h, k=args.k)


if __name__ == "__main__":
    raise SystemExit(main())
