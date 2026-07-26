#!/usr/bin/env python
"""進化緊急停機開關 — Steward／ops 置 evolution_kill_switch clear｜halt（PME-KILL／TRI-HALT）。

🎯 這支在做什麼（白話）：人打緊急停 → 寫 DB kill-switch；halt 時對應軸引擎拒絕開新輪。
   **V2 Phase 2.4（C6）**：由單列升為**逐 scope 一列**（tw／lai／raw／global）——
   `TRI-HALT`＝寫 `scope=global` 之 halt；各軸 driver 開輪前查 `scope IN (自軸,'global')`、
   任一 halt 即停（OR、fail-safe）。撤回原 TRI-v1 之 cross_notify 專用表（死碼設計）。
   環境變數 AUGUR_EVOLUTION_KILL_SWITCH=halt 亦可強制 halt（OR；不寫 DB）。零 FinMind／FRED。

守 #15 #26 #29；PME 計畫 §4.1 G-KILL；v2 總控 §3.3 C6。

執行指令矩陣:
  python scripts/set_evolution_kill_switch.py                 # 現況（唯讀:四 scope 全列）
  python scripts/set_evolution_kill_switch.py --status        # 同上
  python scripts/set_evolution_kill_switch.py --halt --by steward --reason "ops"          # 預設 scope=global(=TRI-HALT)
  python scripts/set_evolution_kill_switch.py --halt --scope lai --by steward --reason "x" # 單軸停
  python scripts/set_evolution_kill_switch.py --clear --scope lai --by steward --reason "resume"
  python scripts/set_evolution_kill_switch.py --selftest      # 免 DB
"""
from __future__ import annotations

import argparse
import os
import sys

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import (
    KILL_CLEAR,
    KILL_HALT,
    KILL_SCOPES,
    effective_kill_state,
    normalize_kill_state,
)


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
    chk("四 scope 封閉集", set(KILL_SCOPES) == {"tw", "lai", "raw", "global"})
    chk("scoped OR:任一 halt 即 halt", effective_kill_state(["clear", "halt"]) == KILL_HALT)
    chk("scoped OR:全 clear 即 clear", effective_kill_state(["clear", "clear"]) == KILL_CLEAR)
    chk("scoped:空序列=表無列=clear(建表前相容)", effective_kill_state([]) == KILL_CLEAR)
    chk("scoped:env 仍可強制 halt", effective_kill_state(["clear"], env_halt=True) == KILL_HALT)
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
        cur.execute("SELECT scope, state, set_at, set_by, reason FROM evolution_kill_switch "
                    "ORDER BY CASE scope WHEN 'global' THEN 0 ELSE 1 END, scope")
        rows = cur.fetchall()
    print("── evolution kill-switch(逐 scope;任一相干 halt 即停)──")
    for scope, state, at, by, reason in rows:
        print(f"  {scope:<7} {state:<6} @{at:%Y-%m-%d %H:%M} by={by}" + (f" ({reason})" if reason else ""))
    print(f"  env AUGUR_EVOLUTION_KILL_SWITCH halt={env}")
    for axis in ("tw", "lai", "raw"):
        eff = effective_kill_state([s for sc, s, *_ in rows if sc in (axis, "global")], env_halt=env)
        print(f"  effective[{axis}]: {eff}")
    return 0


def set_state(state: str, *, scope: str, by: str, reason: str) -> int:
    from augur.core import db

    state = normalize_kill_state(state)
    if scope not in KILL_SCOPES:
        print(f"✗ 非法 scope:{scope}(合法={KILL_SCOPES})")
        return 2
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.evolution_kill_switch')")
        if cur.fetchone()[0] is None:
            print("✗ 表未建 — 先 migrate --run")
            return 1
        cur.execute(
            "UPDATE evolution_kill_switch SET state=%s, set_by=%s, reason=%s, set_at=now() WHERE scope=%s",
            (state, by, reason, scope),
        )
        if cur.rowcount == 0:
            print(f"✗ scope={scope} 無列——先跑 migrate --run 補 scope 種子")
            return 1
    print(f"✓ kill-switch[{scope}] → {state} (by={by})" + ("  ＝TRI-HALT" if scope == "global" and state == KILL_HALT else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--halt", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--scope", default="global", choices=list(KILL_SCOPES))
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
        return set_state(KILL_HALT, scope=args.scope, by=args.by, reason=args.reason or "PME-KILL halt")
    if args.clear:
        return set_state(KILL_CLEAR, scope=args.scope, by=args.by, reason=args.reason or "PME-KILL clear")
    return show_status()


if __name__ == "__main__":
    raise SystemExit(main())
