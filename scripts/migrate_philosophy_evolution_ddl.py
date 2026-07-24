#!/usr/bin/env python
"""哲學↔市場進化閉環 DDL — evolution_run／coverage／promotion_queue／apply_log／kill_switch。

🎯 這支在做什麼（白話）：冪等建 PME 新表（計畫 §5.2），含全域 kill-switch 單列種子。
   不觸 FinMind／FRED；不改 philosophy 既有表資料。

守 #6 #12 #15 #29；SSOT＝reports/augur_philosophy_market_evolution_loop_plan_20260724.md §5.2。

執行指令矩陣:
  python scripts/migrate_philosophy_evolution_ddl.py            # 無參數:現況（唯讀）
  python scripts/migrate_philosophy_evolution_ddl.py --run      # 冪等建表 + kill_switch 種子 clear
  python scripts/migrate_philosophy_evolution_ddl.py --verify   # 表＋種子斷言（exit 0/1）
  python scripts/migrate_philosophy_evolution_ddl.py --selftest # 紅綠鎖（免 DB）
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import EVOLUTION_DDL, EVOLUTION_DDL_POST

TABLES = (
    "evolution_run",
    "evolution_coverage_snapshot",
    "promotion_queue",
    "evolution_apply_log",
    "evolution_kill_switch",
)


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 五段", len(EVOLUTION_DDL) == 5)
    chk("每段含 CREATE TABLE", all("CREATE TABLE IF NOT EXISTS" in d for d in EVOLUTION_DDL))
    for t in TABLES:
        chk(f"DDL 含 {t}", any(t in d for d in EVOLUTION_DDL))
    chk("kill_switch CHECK clear|halt", any("clear|halt" in d or "'clear','halt'" in d for d in EVOLUTION_DDL))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def status() -> int:
    from augur.core import db

    with db.connect() as conn, db.transaction(conn) as cur:
        print("── PME evolution DDL 現況（唯讀）──")
        for t in TABLES:
            cur.execute("SELECT to_regclass(%s) IS NOT NULL", (f"public.{t}",))
            exists = cur.fetchone()[0]
            n = None
            if exists:
                cur.execute(f"SELECT count(*) FROM {t}")  # noqa: S608 — 表名白名單 TABLES
                n = cur.fetchone()[0]
            print(f"  {'✓' if exists else '✗'} {t}" + (f"  rows={n}" if exists else "  (absent)"))
        cur.execute("SELECT to_regclass('public.evolution_kill_switch') IS NOT NULL")
        if cur.fetchone()[0]:
            cur.execute("SELECT state, set_by, reason FROM evolution_kill_switch WHERE switch_id=1")
            row = cur.fetchone()
            print(f"  kill_switch: {row}")
    return 0


def run() -> int:
    from augur.core import db

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            for ddl in EVOLUTION_DDL:
                cur.execute(ddl)
            for ddl in EVOLUTION_DDL_POST:
                cur.execute(ddl)
            cur.execute(
                "INSERT INTO evolution_kill_switch (switch_id, state, set_by, reason) "
                "VALUES (1, 'clear', 'migrate_philosophy_evolution_ddl', 'PME-KILL seed') "
                "ON CONFLICT (switch_id) DO NOTHING"
            )
        print("✓ --run 完成（冪等）: evolution_* + promotion_queue + kill_switch 種子")
    return 0


def verify() -> int:
    from augur.core import db

    with db.connect() as conn, db.transaction(conn) as cur:
        missing = []
        for t in TABLES:
            cur.execute("SELECT to_regclass(%s) IS NOT NULL", (f"public.{t}",))
            if not cur.fetchone()[0]:
                missing.append(t)
        kill_ok = False
        if "evolution_kill_switch" not in missing:
            cur.execute("SELECT state FROM evolution_kill_switch WHERE switch_id=1")
            row = cur.fetchone()
            kill_ok = row is not None and row[0] in ("clear", "halt")
    ok = not missing and kill_ok
    print(f"{'✓' if ok else '✗'} verify: missing={missing or '[]'} kill_seed={kill_ok}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.run:
        return run()
    if args.verify:
        return verify()
    return status()


if __name__ == "__main__":
    raise SystemExit(main())
