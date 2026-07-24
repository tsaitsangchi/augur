#!/usr/bin/env python
"""進化緊急停機開關 — Steward／ops 置 evolution_kill_switch clear｜halt（PME-KILL）。

🎯 這支在做什麼（白話）：人打緊急停 → 寫 DB 單列 kill-switch；halt 時 APPLY 引擎拒絕上線。
   環境變數 AUGUR_EVOLUTION_KILL_SWITCH=halt 亦可強制 halt（OR；不寫 DB）。零 FinMind／FRED。

守 #15 #26 #29；計畫 §4.1 G-KILL／§6 set_evolution_kill_switch。

執行指令矩陣:
  python scripts/set_evolution_kill_switch.py                 # 現況（唯讀）
  python scripts/set_evolution_kill_switch.py --status        # 同上
  python scripts/set_evolution_kill_switch.py --halt --by steward --reason "ops"
  python scripts/set_evolution_kill_switch.py --clear --by steward --reason "resume"
  python scripts/set_evolution_kill_switch.py --selftest      # 免 DB
"""
from __future__ import annotations

import argparse
import os
import sys

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import KILL_CLEAR, KILL_HALT, normalize_kill_state


def _env_halt() -> bool:
    return os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == KILL_HALT


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("normalize clear", normalize_kill_state("clear") == KILL_CLEAR)
    chk("normalize halt", normalize_kill_state("HALT") == KILL_HALT)
    chk("env OR halt", normalize_kill_state("clear", env_halt=True) == KILL_HALT)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def show_status() -> int:
    from augur.core import db

    env = _env_halt()
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.evolution_kill_switch')")
        if cur.fetchone()[0] is None:
            print("✗ evolution_kill_switch 未建 — 先: python scripts/migrate_philosophy_evolution_ddl.py --run")
            return 1
        cur.execute("SELECT state, set_at, set_by, reason FROM evolution_kill_switch WHERE switch_id=1")
        row = cur.fetchone()
    effective = normalize_kill_state(row[0] if row else None, env_halt=env)
    print("── evolution kill-switch ──")
    print(f"  db_state: {row}")
    print(f"  env AUGUR_EVOLUTION_KILL_SWITCH halt={env}")
    print(f"  effective: {effective}")
    return 0


def set_state(state: str, *, by: str, reason: str) -> int:
    from augur.core import db

    state = normalize_kill_state(state)
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.evolution_kill_switch')")
        if cur.fetchone()[0] is None:
            print("✗ 表未建 — 先 migrate --run")
            return 1
        cur.execute(
            "INSERT INTO evolution_kill_switch (switch_id, state, set_by, reason, set_at) "
            "VALUES (1, %s, %s, %s, now()) "
            "ON CONFLICT (switch_id) DO UPDATE SET "
            "state=EXCLUDED.state, set_by=EXCLUDED.set_by, reason=EXCLUDED.reason, set_at=now()",
            (state, by, reason),
        )
    print(f"✓ kill-switch → {state} (by={by})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--halt", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--by", default="steward")
    ap.add_argument("--reason", default="")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.halt and args.clear:
        print("✗ --halt 與 --clear 互斥")
        return 2
    if args.halt:
        return set_state(KILL_HALT, by=args.by, reason=args.reason or "PME-KILL halt")
    if args.clear:
        return set_state(KILL_CLEAR, by=args.by, reason=args.reason or "PME-KILL clear")
    return show_status()


if __name__ == "__main__":
    raise SystemExit(main())
