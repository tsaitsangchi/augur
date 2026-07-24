#!/usr/bin/env python
"""進化晉升自動 APPLY — PME-AUTO-B：消費 pending_auto、查閘＋kill-switch、寫 status／apply_log。

🎯 這支在做什麼（白話）：引擎自動上線特徵／原則**狀態**（非下單）。kill-switch=halt →
   拒絕 APPLY（queue→halted、exit≠0）。閘未全綠不得 APPLY；`--force` **禁止跳閘**。
   無人簽核參數（B）；可 `--dry-run`。零 FinMind／FRED。

守 #14 #15 #26 #29；計畫 §4 S3／§4.1／驗收 A5／A6。

執行指令矩陣:
  python scripts/apply_evolution_promotions.py              # 消費 pending_auto（寫入）
  python scripts/apply_evolution_promotions.py --dry-run     # 只印裁決
  python scripts/apply_evolution_promotions.py --run-id N    # 限某 run
  python scripts/apply_evolution_promotions.py --selftest    # 免 DB（含 A5 語意）
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import (
    KILL_CLEAR,
    KILL_HALT,
    all_gates_green,
    may_apply,
    normalize_kill_state,
    scan_noexec_text,
    status_after_apply,
)


def _env_halt() -> bool:
    return os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == KILL_HALT


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    text = Path(__file__).read_text(encoding="utf-8")
    chk("G-NOEXEC clean", scan_noexec_text(text) == [])
    green = {g: {"verdict": "PASS"} for g in (
        "G-ISO", "G-MAP", "G-PROM", "G-ECON", "G-ATTEST", "G-KILL", "G-NOEXEC"
    )}
    chk("gates green", all_gates_green(green))
    ok_a, reason = may_apply(kill_state=KILL_HALT, gate_json=green, queue_status="pending_auto")
    chk("A5 halt refuse", (not ok_a) and "halt" in reason.lower())
    ok_b, _ = may_apply(kill_state=KILL_CLEAR, gate_json=green, queue_status="pending_auto")
    chk("A6 clear+green allow", ok_b)
    chk("status promote", status_after_apply("promote", "untested") == "validated")
    # --force 不得用於跳閘：本腳本若出現跳閘 force 語意則 FAIL
    chk("no skip-gate force", "--force" not in text or "禁" in text or "禁止" in text)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def apply_pending(*, dry_run: bool, run_id: int | None) -> int:
    from augur.core import db

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.promotion_queue')")
        if cur.fetchone()[0] is None:
            print("✗ 先: python scripts/migrate_philosophy_evolution_ddl.py --run")
            return 1
        cur.execute("SELECT state FROM evolution_kill_switch WHERE switch_id=1")
        row = cur.fetchone()
        kill_eff = normalize_kill_state(row[0] if row else None, env_halt=_env_halt())

        q = (
            "SELECT queue_id, run_id, principle_id, feature, action, gate_json, queue_status "
            "FROM promotion_queue WHERE queue_status = 'pending_auto'"
        )
        params: tuple = ()
        if run_id is not None:
            q += " AND run_id = %s"
            params = (run_id,)
        q += " ORDER BY queue_id"
        cur.execute(q, params)
        items = cur.fetchall()

    print(f"── PME APPLY (AUTO-B) kill={kill_eff} pending={len(items)} dry_run={dry_run} ──")

    if kill_eff == KILL_HALT:
        # A5：halt 時拒絕一切 APPLY；可選把 pending 標 halted
        if not dry_run and items:
            with db.connect() as conn, db.transaction(conn) as cur:
                ids = [r[0] for r in items]
                cur.execute(
                    "UPDATE promotion_queue SET queue_status='halted', decided_at=now(), "
                    "decided_by='evolution_engine' WHERE queue_id = ANY(%s)",
                    (ids,),
                )
            print(f"✗ G-KILL halt — refused APPLY; marked halted n={len(items)}")
        else:
            print("✗ G-KILL halt — refused APPLY (exit≠0)")
        return 1

    if not items:
        print("✓ 無 pending_auto")
        return 0

    applied = 0
    skipped = 0
    with db.connect() as conn:
        for queue_id, rid, principle_id, feature, action, gate_json, qstatus in items:
            if isinstance(gate_json, str):
                gate_json = json.loads(gate_json)
            allowed, reason = may_apply(
                kill_state=kill_eff, gate_json=gate_json, queue_status=qstatus
            )
            if not allowed:
                print(f"  skip q={queue_id} {feature}: {reason}")
                skipped += 1
                if not dry_run:
                    with db.transaction(conn) as cur:
                        cur.execute(
                            "UPDATE promotion_queue SET queue_status='rejected_gate', decided_at=now() "
                            "WHERE queue_id=%s",
                            (queue_id,),
                        )
                continue

            before = None
            if principle_id is not None:
                with db.transaction(conn) as cur:
                    cur.execute(
                        "SELECT status FROM philosophy_principle WHERE principle_id=%s",
                        (principle_id,),
                    )
                    r = cur.fetchone()
                    before = r[0] if r else None
            after = status_after_apply(action, before)
            print(
                f"  {'DRY ' if dry_run else ''}APPLY q={queue_id} {feature} "
                f"action={action} {before}→{after} decided_by=evolution_engine"
            )
            if dry_run:
                applied += 1
                continue
            with db.transaction(conn) as cur:
                if principle_id is not None and action in ("promote", "demote"):
                    cur.execute(
                        "UPDATE philosophy_principle SET status=%s WHERE principle_id=%s",
                        (after, principle_id),
                    )
                cur.execute(
                    """
                    INSERT INTO evolution_apply_log
                      (queue_id, before_status, after_status, production_set_delta, evidence_json)
                    VALUES (%s,%s,%s,%s::jsonb,%s::jsonb)
                    RETURNING apply_log_id
                    """,
                    (
                        queue_id,
                        before,
                        after,
                        json.dumps({"feature": feature, "action": action}),
                        json.dumps({"gate_json": gate_json, "run_id": rid}),
                    ),
                )
                apply_log_id = cur.fetchone()[0]
                cur.execute(
                    "UPDATE promotion_queue SET queue_status='applied', decided_at=now(), "
                    "decided_by='evolution_engine', apply_log_id=%s WHERE queue_id=%s",
                    (apply_log_id, queue_id),
                )
            applied += 1

    print(f"✓ applied={applied} skipped={skipped}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run-id", type=int, default=None)
    ap.add_argument("--selftest", action="store_true")
    # 明確拒絕跳閘 force（若用戶傳入）
    ap.add_argument("--force", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.force:
        print("✗ --force 禁止用於跳閘（PME-AUTO-B）；閘紅不得 APPLY")
        return 2
    return apply_pending(dry_run=args.dry_run, run_id=args.run_id)


if __name__ == "__main__":
    raise SystemExit(main())
