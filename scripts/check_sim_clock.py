#!/usr/bin/env python3
"""🎯 sim 時鐘哨——下一格 asof／待結算列數／K 進度（M-M4；掛週日 09:00 週報）。

白話:catch-up 冪等只保證「晚跑不掉格」，不保證「有人會跑」。本支唯讀現查
  sim_run_link／sim_realized_outcome／門日曆，印 master §7.3 週報一行。
  **永不 acquire heavy_slot**；零 API。

格式（驗收①）:「sim 時鐘：K=n/3，下一格 <date|未實現|無門>，待結算 <n> 列」

守原則 #15（數字出 DB）· #8（下一格不猜未實現日曆）· #28 · #29a/d · #35。

執行指令矩陣
------------
    python3 scripts/check_sim_clock.py              # 無參數＝--check（唯讀＋週報行）
    python3 scripts/check_sim_clock.py --check      # 同上；印詳情＋週報行；rc=0（哨＝告知、非硬閘）
    python3 scripts/check_sim_clock.py --week-line  # 只印週報一行
    python3 scripts/check_sim_clock.py --json
    python3 scripts/check_sim_clock.py --selftest   # 零 DB：純函式紅綠
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date

import _bootstrap  # noqa: F401

GATE_ID = "SIM-CAL-R1"
K_TARGET = 3
H_TD = 21
ARM = "live"


def format_week_line(*, k: int, k_max: int, next_asof, pending: int) -> str:
    """週報一行（master §7.3）。純函式。"""
    if next_asof is None:
        nxt = "未實現"
    elif next_asof == "無門":
        nxt = "無門"
    else:
        nxt = str(next_asof)
    return f"sim 時鐘：K={int(k)}/{int(k_max)}，下一格 {nxt}，待結算 {int(pending)} 列"


def next_grid_asof(cal: list, produced: set, anchor) -> object:
    """下一缺產格點；日曆未含 anchor／無後續格 → None（不猜未來）。純函式。"""
    if not cal or anchor is None or anchor not in cal:
        return None
    grid = cal[cal.index(anchor)::H_TD]
    for g in grid:
        if g not in produced:
            return g
    return None  # 已產完可見格；未來格等日曆伸長


def k_progress(produced_asofs: set, k_max: int = K_TARGET) -> int:
    """已產 distinct asof 數，上限 k_max（校準窗以 3 格為終點）。純函式。"""
    return min(len(produced_asofs), int(k_max))


def _snapshot(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT status, (approved_at AT TIME ZONE 'Asia/Taipei')::date
               FROM evolution_prereg_gate WHERE gate_id=%s""",
            (GATE_ID,),
        )
        row = cur.fetchone()
        if not row:
            return {
                "gate": None, "k": 0, "pending": 0, "next_asof": "無門",
                "produced": [], "week_line": format_week_line(
                    k=0, k_max=K_TARGET, next_asof="無門", pending=0),
            }
        status, approved = row[0], row[1]
        cur.execute(
            """SELECT r.asof_date, count(*)::int,
                      count(*) FILTER (
                        WHERE NOT EXISTS (
                          SELECT 1 FROM sim_realized_outcome o WHERE o.run_id=l.run_id
                        ))::int AS pending
               FROM sim_run_link l
               JOIN mc_simulation_run r ON r.run_id=l.run_id
               WHERE l.gate_id=%s AND l.arm=%s
               GROUP BY 1 ORDER BY 1""",
            (GATE_ID, ARM),
        )
        by_asof = cur.fetchall()
        produced = {r[0] for r in by_asof}
        pending = sum(r[2] for r in by_asof)
        # anchor＝approved 次一已實現交易日（與 runner 同口徑；表經 registry、禁 vendor 直綁）
        from augur.catalog.world_concept import resolve_sql
        cal_tbl = resolve_sql("tw.daily_bar", conn=conn)
        cur.execute(
            f"SELECT date FROM {cal_tbl} WHERE stock_id=%s AND date > %s ORDER BY date",
            ("TAIEX", approved),
        )
        cal = [r[0] for r in cur.fetchall()]
        anchor = cal[0] if cal else None
        nxt = next_grid_asof(cal, produced, anchor) if status == "approved" else None
        k = k_progress(produced)
        line = format_week_line(k=k, k_max=K_TARGET, next_asof=nxt, pending=pending)
        return {
            "gate": GATE_ID,
            "status": status,
            "approved": str(approved) if approved else None,
            "anchor": str(anchor) if anchor else None,
            "k": k,
            "k_max": K_TARGET,
            "pending": pending,
            "produced": [str(d) for d in sorted(produced)],
            "next_asof": None if nxt is None else str(nxt),
            "week_line": line,
        }


def _check(*, as_json=False, week_line_only=False) -> int:
    from augur.core import db

    with db.connect() as conn:
        snap = _snapshot(conn)
    if week_line_only:
        print(snap["week_line"])
        return 0
    if as_json:
        print(json.dumps(snap, ensure_ascii=False, indent=2, default=str))
        return 0
    print("── sim 時鐘哨（M-M4；告知哨，rc 恆 0）──")
    print(f"  gate={snap.get('gate')} status={snap.get('status')}")
    print(f"  anchor={snap.get('anchor')} produced={snap.get('produced')}")
    print(f"  {snap['week_line']}")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    line = format_week_line(k=0, k_max=3, next_asof=None, pending=0)
    chk("週報行格式定錨", line == "sim 時鐘：K=0/3，下一格 未實現，待結算 0 列")
    line2 = format_week_line(k=1, k_max=3, next_asof=date(2026, 9, 1), pending=52)
    chk("有下一格＋待結算", "K=1/3" in line2 and "2026-09-01" in line2 and "待結算 52" in line2)
    chk("無門字樣", "無門" in format_week_line(k=0, k_max=3, next_asof="無門", pending=0))

    cal = [date(2026, 8, 3) + __import__("datetime").timedelta(days=i) for i in range(0, 70, 1)]
    # 簡化：用連續日當「交易日」測步進
    a0 = cal[0]
    produced: set = set()
    chk("無產 → 下一格=anchor", next_grid_asof(cal, produced, a0) == a0)
    produced.add(a0)
    nxt = next_grid_asof(cal, produced, a0)
    chk("產首格後下一格= +21", nxt == cal[H_TD])
    chk("k_progress 上限 3", k_progress({1, 2, 3, 4}, 3) == 3)
    chk("空曆 → None", next_grid_asof([], set(), a0) is None)

    body = open(__file__, encoding="utf-8").read().split("def _selftest")[0]
    chk("不 acquire heavy_slot", "HeavySlot" not in body and ".acquire(" not in body)
    chk("閘 id 定錨 SIM-CAL-R1", GATE_ID == "SIM-CAL-R1")

    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="sim 時鐘哨（M-M4）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--week-line", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    return _check(as_json=a.json, week_line_only=a.week_line)


if __name__ == "__main__":
    sys.exit(main())
