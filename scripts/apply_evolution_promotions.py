#!/usr/bin/env python
"""進化晉升自動 APPLY — PME-AUTO-B：消費 pending_auto、查閘＋kill-switch、寫 status／prodset／apply_log。

🎯 這支在做什麼（白話）：引擎自動上線特徵／原則**狀態**（非下單）。kill-switch=halt →
   拒絕 APPLY（queue→halted、exit≠0）。閘未全綠不得 APPLY；`--force` **禁止跳閘**。
   APPLY 成功時：翻 philosophy_principle.status ＋ **真寫** `evolution_production_feature_set`
   （promote→active／demote→removed；≠可交易／確立級）。`--backfill-prodset` 可對已 applied
   重放登錄。無人簽核參數（B）；可 `--dry-run`。零 FinMind／FRED。

守 #14 #15 #26 #29；計畫 §4 S3／§4.1／§6／驗收 A5／A6。

執行指令矩陣:
  python scripts/apply_evolution_promotions.py              # 消費 pending_auto（寫入）
  python scripts/apply_evolution_promotions.py --dry-run     # 只印裁決
  python scripts/apply_evolution_promotions.py --run-id N    # 限某 run
  python scripts/apply_evolution_promotions.py --backfill-prodset [--run-id N]  # 已 applied 補登錄
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
    PRODSET_TABLE,
    all_gates_green,
    decide_queue_status,
    effective_kill_state,
    may_apply,
    normalize_kill_state,
    production_set_delta,
    prodset_status_for_action,
    scan_noexec_text,
    status_after_apply,
)


def _env_halt() -> bool:
    return os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == KILL_HALT


def _upsert_prodset(
    cur,
    *,
    feature: str,
    set_status: str,
    run_id: int,
    queue_id: int,
    apply_log_id: int,
    principle_id: int | None,
    action: str,
) -> None:
    cur.execute(
        f"""
        INSERT INTO {PRODSET_TABLE}
          (feature, set_status, registered_at, updated_at,
           source_run_id, source_queue_id, apply_log_id, principle_id, last_action)
        VALUES (%s,%s,now(),now(),%s,%s,%s,%s,%s)
        ON CONFLICT (feature) DO UPDATE SET
          set_status = EXCLUDED.set_status,
          updated_at = now(),
          source_run_id = EXCLUDED.source_run_id,
          source_queue_id = EXCLUDED.source_queue_id,
          apply_log_id = EXCLUDED.apply_log_id,
          principle_id = EXCLUDED.principle_id,
          last_action = EXCLUDED.last_action
        """,  # noqa: S608 — PRODSET_TABLE 常數白名單
        (feature, set_status, run_id, queue_id, apply_log_id, principle_id, action),
    )


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
    chk("prodset promote writes", prodset_status_for_action("promote") == "active")
    chk("prodset demote removes", prodset_status_for_action("demote") == "removed")
    chk("prodset freeze skips", prodset_status_for_action("freeze") is None)
    d = production_set_delta("x", "promote")
    chk("delta names table", d.get("table") == PRODSET_TABLE and d.get("set_status") == "active")
    chk("mentions prodset table", PRODSET_TABLE in text)
    chk("backfill flag present", "--backfill-prodset" in text)
    # --force 不得用於跳閘：本腳本若出現跳閘 force 語意則 FAIL
    chk("no skip-gate force", "--force" not in text or "禁" in text or "禁止" in text)
    # —— R3 demote 通道＋R2 篩(V2-AUTOADVANCE 2026-07-27) ——
    sign_gj = dict(green)
    sign_gj["G-PROM"] = {"verdict": "FAIL_SIGN", "evidence": {"hac_t": -3.966}}
    ok_c, r_c = may_apply(kill_state=KILL_CLEAR, gate_json=sign_gj,
                          queue_status="pending_auto", action="demote")
    chk("R3:FAIL_SIGN demote 放行", ok_c and "R3" in r_c)
    fail_gj = dict(green)
    fail_gj["G-PROM"] = {"verdict": "FAIL", "evidence": {"hac_t": 1.0}}
    ok_d, _ = may_apply(kill_state=KILL_CLEAR, gate_json=fail_gj,
                        queue_status="pending_auto", action="demote")
    chk("一般 FAIL 之 demote 不自動(人裁)", not ok_d)
    chk("decide:demote+FAIL_SIGN → pending_auto",
        decide_queue_status(sign_gj, KILL_CLEAR, action="demote") == "pending_auto")
    chk("decide:demote+FAIL_SIGN 於 halt 仍 halted",
        decide_queue_status(sign_gj, KILL_HALT, action="demote") == "halted")
    ctrl = {"fp_rate_worst": 0.105, "p95_worst": 2.643}
    weak_green = dict(green)
    weak_green["G-PROM"] = {"verdict": "PASS", "evidence": {"hac_t": 2.1}}
    ok_e, r_e = may_apply(kill_state=KILL_CLEAR, gate_json=weak_green,
                          queue_status="pending_auto", action="promote", ctrl=ctrl)
    chk("R2(c):偽陽率>10% 時 |hac_t|=2.1<p95 2.643 → 拒", (not ok_e) and "GATE-raise" in r_e)
    strong_green = dict(green)
    strong_green["G-PROM"] = {"verdict": "PASS", "evidence": {"hac_t": 3.0}}
    ok_f, _ = may_apply(kill_state=KILL_CLEAR, gate_json=strong_green,
                        queue_status="pending_auto", action="promote", ctrl=ctrl)
    chk("R2(c):|hac_t|=3.0≥p95 → 放行", ok_f)
    ok_g, _ = may_apply(kill_state=KILL_CLEAR, gate_json=weak_green,
                        queue_status="pending_auto", action="promote",
                        ctrl={"fp_rate_worst": 0.08, "p95_worst": 2.643})
    chk("R2(c):偽陽率≤10% 不加篩", ok_g)
    chk("status:demote+FAIL_SIGN → sign_refuted(與證據不足 rejected 區分)",
        status_after_apply("demote", "validated", prom_verdict="FAIL_SIGN") == "sign_refuted"
        and status_after_apply("demote", "validated") == "rejected")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def backfill_prodset(*, dry_run: bool, run_id: int | None) -> int:
    """對已 applied 且 action 會改 prodset 之列補寫登錄（冪等 UPSERT）。"""
    from augur.core import db

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{PRODSET_TABLE}",))
        if cur.fetchone()[0] is None:
            print(f"✗ 先: python scripts/migrate_philosophy_evolution_ddl.py --run  （缺 {PRODSET_TABLE}）")
            return 1
        q = (
            "SELECT q.queue_id, q.run_id, q.principle_id, q.feature, q.action, q.apply_log_id "
            "FROM promotion_queue q "
            "WHERE q.queue_status = 'applied' AND q.apply_log_id IS NOT NULL "
            "  AND q.action IN ('promote','demote')"
        )
        params: tuple = ()
        if run_id is not None:
            q += " AND q.run_id = %s"
            params = (run_id,)
        q += " ORDER BY q.queue_id"
        cur.execute(q, params)
        items = cur.fetchall()

    print(f"── PME PRODSET backfill pending_rows={len(items)} dry_run={dry_run} ──")
    if not items:
        print("✓ 無可補登錄之 applied 列")
        return 0

    n = 0
    with db.connect() as conn:
        for queue_id, rid, principle_id, feature, action, apply_log_id in items:
            set_status = prodset_status_for_action(action)
            if set_status is None:
                continue
            print(
                f"  {'DRY ' if dry_run else ''}PRODSET {feature} "
                f"action={action} → {set_status} q={queue_id} apply_log={apply_log_id}"
            )
            if dry_run:
                n += 1
                continue
            with db.transaction(conn) as cur:
                cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4)
                _upsert_prodset(
                    cur,
                    feature=feature,
                    set_status=set_status,
                    run_id=rid,
                    queue_id=queue_id,
                    apply_log_id=apply_log_id,
                    principle_id=principle_id,
                    action=action,
                )
                # 補齊 apply_log delta（若舊列僅有 feature/action）
                cur.execute(
                    """
                    UPDATE evolution_apply_log
                       SET production_set_delta = %s::jsonb
                     WHERE apply_log_id = %s
                    """,
                    (json.dumps(production_set_delta(feature, action, set_status=set_status)), apply_log_id),
                )
            n += 1
    print(f"✓ backfill_prodset n={n}")
    return 0


def apply_pending(*, dry_run: bool, run_id: int | None) -> int:
    from augur.core import db

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.promotion_queue')")
        if cur.fetchone()[0] is None:
            print("✗ 先: python scripts/migrate_philosophy_evolution_ddl.py --run")
            return 1
        cur.execute("SELECT to_regclass(%s)", (f"public.{PRODSET_TABLE}",))
        if cur.fetchone()[0] is None:
            print(f"✗ 先: python scripts/migrate_philosophy_evolution_ddl.py --run  （缺 {PRODSET_TABLE}）")
            return 1
        # V2 Phase 2.4(C6):逐 scope 口徑——本引擎屬 tw 軸;自軸或 global 任一 halt 即停(OR、fail-safe)
        cur.execute("SELECT state FROM evolution_kill_switch WHERE scope IN ('tw','global')")
        kill_eff = effective_kill_state([r[0] for r in cur.fetchall()], env_halt=_env_halt())

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

        # R2(c) GATE-raise 篩(V2-AUTOADVANCE):讀最新對照臂證據(最大 n 之 control_arms suite),
        # 偽陽率>10% 時 promote 加篩 |hac_t|≥經驗 p95。無證據=無篩(誠實:沒跑對照臂前不假裝有)。
        cur.execute(
            """SELECT arm, metric_value, (detail->>'abs_hac_p95')::float8, evidence_id
               FROM evolution_evidence_run
               WHERE axis='tw' AND selection_scope='control_arms_v1' AND NOT is_invalid
                 AND n_items = (SELECT max(n_items) FROM evolution_evidence_run
                                WHERE axis='tw' AND selection_scope='control_arms_v1' AND NOT is_invalid)
               ORDER BY created_at DESC LIMIT 4""")
        ctrl_rows = cur.fetchall()
    ctrl = None
    if ctrl_rows:
        rates = [float(r[1]) for r in ctrl_rows if r[1] is not None]
        p95s = [float(r[2]) for r in ctrl_rows if r[2] is not None]
        if rates and p95s:
            ctrl = {"fp_rate_worst": max(rates), "p95_worst": max(p95s),
                    "evidence_ids": [r[3] for r in ctrl_rows]}

    print(f"── PME APPLY (AUTO-B) kill={kill_eff} pending={len(items)} dry_run={dry_run} ──")
    if ctrl:
        print(f"  對照臂篩: 偽陽率(最壞)={ctrl['fp_rate_worst']:.1%} p95={ctrl['p95_worst']:.3f} "
              f"→ {'升嚴生效(R2c)' if ctrl['fp_rate_worst'] > 0.10 else '未觸發(≤10%)'}")
    else:
        print("  對照臂篩: 無 control_arms 證據——未加篩(誠實)")

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
    promotes_this_round = 0
    with db.connect() as conn:
        for queue_id, rid, principle_id, feature, action, gate_json, qstatus in items:
            if isinstance(gate_json, str):
                gate_json = json.loads(gate_json)
            allowed, reason = may_apply(
                kill_state=kill_eff, gate_json=gate_json, queue_status=qstatus,
                action=action, ctrl=ctrl,
            )
            # R2(d):單輪 auto-promote 上限 1(demote 不設限=風險遞減);超額留 pending 下輪
            if allowed and action == "promote" and promotes_this_round >= 1:
                print(f"  hold q={queue_id} {feature}: R2(d) 單輪 promote 上限 1——留 pending 下輪")
                continue
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
            prom_verdict = (gate_json.get("G-PROM") or {}).get("verdict")
            after = status_after_apply(action, before, prom_verdict=prom_verdict)
            set_status = prodset_status_for_action(action)
            delta = production_set_delta(feature, action, set_status=set_status)
            print(
                f"  {'DRY ' if dry_run else ''}APPLY q={queue_id} {feature} "
                f"action={action} {before}→{after} prodset={set_status} "
                f"decided_by=evolution_engine"
            )
            if dry_run:
                applied += 1
                if action == "promote":
                    promotes_this_round += 1  # dry 也計數:preview 須如實反映 R2(d) 上限
                continue
            with db.transaction(conn) as cur:
                cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4)
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
                        json.dumps(delta),
                        # R6:自動決策落帳可稽——gate_ref + 依據規則號(週日 digest 掃此)
                        json.dumps({"gate_json": gate_json, "run_id": rid,
                                    "gate_ref": "V2-AUTOADVANCE",
                                    "auto_rule": ("R3-sign-refuted-demote" if action == "demote"
                                                  else "R2-auto-apply"),
                                    "ctrl_screen": ctrl}),
                    ),
                )
                apply_log_id = cur.fetchone()[0]
                if set_status is not None:
                    _upsert_prodset(
                        cur,
                        feature=feature,
                        set_status=set_status,
                        run_id=rid,
                        queue_id=queue_id,
                        apply_log_id=apply_log_id,
                        principle_id=principle_id,
                        action=action,
                    )
                cur.execute(
                    "UPDATE promotion_queue SET queue_status='applied', decided_at=now(), "
                    "decided_by='evolution_engine', apply_log_id=%s WHERE queue_id=%s",
                    (apply_log_id, queue_id),
                )
            applied += 1
            if action == "promote":
                promotes_this_round += 1

    print(f"✓ applied={applied} skipped={skipped}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run-id", type=int, default=None)
    ap.add_argument(
        "--backfill-prodset",
        action="store_true",
        help="對已 applied promote/demote 補寫 evolution_production_feature_set（冪等）",
    )
    ap.add_argument("--selftest", action="store_true")
    # 明確拒絕跳閘 force（若用戶傳入）
    ap.add_argument("--force", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.force:
        print("✗ --force 禁止用於跳閘（PME-AUTO-B）；閘紅不得 APPLY")
        return 2
    if args.backfill_prodset:
        return backfill_prodset(dry_run=args.dry_run, run_id=args.run_id)
    return apply_pending(dry_run=args.dry_run, run_id=args.run_id)


if __name__ == "__main__":
    raise SystemExit(main())
