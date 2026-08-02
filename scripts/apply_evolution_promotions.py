#!/usr/bin/env python
"""進化晉升自動 APPLY — PME-AUTO-B：消費 pending_auto、查閘＋kill-switch、寫 status／prodset／apply_log。

🎯 這支在做什麼（白話）：引擎自動上線特徵／原則**狀態**（非下單）。kill-switch=halt →
   拒絕 APPLY（queue→halted、exit≠0）。閘未全綠不得 APPLY；`--force` **禁止跳閘**。
   APPLY 成功時：翻 philosophy_principle.status ＋ **真寫** `evolution_production_feature_set`
   （promote→active／demote→removed；≠可交易／確立級）。`--backfill-prodset` 可對已 applied
   重放登錄。無人簽核參數（B）；可 `--dry-run`。零 FinMind／FRED。
   TWEVO-APPLY-go「一次一顆」（S-i 逐顆人裁）：`--queue-id N` 僅消費該顆 pending_auto、
   他列一概不碰；**真寫須併用 `--allow-apply --gate-ref TWEVO-APPLY-go`（hugo 親跑＝授權載體）**，
   無 --allow-apply 時 --queue-id 只允許 --dry-run 預覽單顆（唯讀）。八閘裁決路與
   decided_by='evolution_engine' 照舊（判準一字不動）。

守 #14 #15 #26 #29；計畫 §4 S3／§4.1／§6／驗收 A5／A6。

執行指令矩陣:
  python scripts/apply_evolution_promotions.py              # 消費 pending_auto（寫入）
  python scripts/apply_evolution_promotions.py --dry-run     # 只印裁決
  python scripts/apply_evolution_promotions.py --run-id N    # 限某 run
  python scripts/apply_evolution_promotions.py --dry-run --queue-id N   # 預覽單顆（唯讀;免旗標）
  python scripts/apply_evolution_promotions.py --queue-id N --allow-apply --gate-ref TWEVO-APPLY-go
                                                            # 一次一顆真寫（S-i;hugo 親跑）
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


AUTO_GATE_REF = "V2-AUTOADVANCE"    # 既有整批自動路之落帳碼（語意不變）
HUMAN_GATE_REF = "TWEVO-APPLY-go"   # S-i 逐顆人裁閘碼（開閘授權＝hugo 親跑指令本身）


def _env_halt() -> bool:
    return os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == KILL_HALT


def select_queue_rows(items: list, queue_id: int | None) -> list:
    """篩選謂詞（純函式；S-i 一次一顆）：queue_id=None→原批次全保留（既有語意）；
    否則僅留 queue_id 相符之列——他列一概不碰。查無回空集，由上層大聲說明 rc=1。"""
    if queue_id is None:
        return list(items)
    return [r for r in items if r[0] == queue_id]


def single_apply_gate(*, queue_id: int | None, allow_apply: bool,
                      gate_ref: str | None, dry_run: bool) -> tuple[bool, str]:
    """--queue-id 武裝判準（純函式）：真寫須 --allow-apply 且 gate_ref==TWEVO-APPLY-go；
    無 --allow-apply 時僅 --dry-run 預覽（唯讀）。整批路（queue_id=None）不經此閘、語意不變。"""
    if queue_id is None:
        return True, "batch mode（既有語意）"
    if dry_run:
        return True, f"dry-run 預覽單顆 q={queue_id}（唯讀）"
    if not allow_apply:
        return False, (f"--queue-id {queue_id} 真寫需 --allow-apply --gate-ref {HUMAN_GATE_REF}"
                       "（現無 --allow-apply → 僅允許 --dry-run 預覽）")
    if gate_ref != HUMAN_GATE_REF:
        return False, f"--gate-ref 須為 {HUMAN_GATE_REF}（收到 {gate_ref!r}）"
    return True, f"armed:{HUMAN_GATE_REF} 一次一顆 q={queue_id}"


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
        "G-ISO", "G-MAP", "G-PROM", "G-ECON", "G-ATTEST", "G-KILL", "G-NOEXEC", "G-SIGN"
    )}
    chk("gates green（八閘含 G-SIGN）", all_gates_green(green))
    # R6:舊世代七鍵（無 G-SIGN）green 不得放行——APPLY 端與 library 同判
    old7 = {g: {"verdict": "PASS"} for g in (
        "G-ISO", "G-MAP", "G-PROM", "G-ECON", "G-ATTEST", "G-KILL", "G-NOEXEC"
    )}
    chk("R6:七鍵 green → all_gates_green=False", not all_gates_green(old7))
    ok_o7, r_o7 = may_apply(kill_state=KILL_CLEAR, gate_json=old7,
                            queue_status="pending_auto", action="promote")
    chk("R6:七鍵 green promote 拒（gates not all PASS）",
        (not ok_o7) and r_o7 == "gates not all PASS")
    # R5:舊七鍵 demote FAIL_SIGN 仍自動放行（除役通道不經 all_gates_green；舊列相容）
    old7_sign = dict(old7)
    old7_sign["G-PROM"] = {"verdict": "FAIL_SIGN", "evidence": {"hac_t": -3.966}}
    ok_o7s, _ = may_apply(kill_state=KILL_CLEAR, gate_json=old7_sign,
                          queue_status="pending_auto", action="demote")
    chk("R5:舊七鍵 demote FAIL_SIGN 經 may_apply 仍放行", ok_o7s)
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
    # —— --queue-id 一次一顆（TWEVO-APPLY-go S-i;I5B）:純函式餵真輸入 ——
    import inspect
    fx = [
        (555, 21, 77, "cycle_position_252d", "promote", {}, "pending_auto"),
        (565, 21, 85, "debt_ratio", "demote", {}, "pending_auto"),
        (599, 21, 107, "lending_fee_rate_mean_30d", "promote", {}, "pending_auto"),
    ]
    chk("queue-id 篩選:3 列僅中指定 1 顆", select_queue_rows(fx, 565) == [fx[1]])
    chk("queue-id 篩選:查無→空集(上層大聲 rc=1)", select_queue_rows(fx, 999) == [])
    chk("queue-id 篩選:None→原批次全保留(既有語意)", select_queue_rows(fx, None) == fx)
    ok_q1, _ = single_apply_gate(queue_id=565, allow_apply=False,
                                 gate_ref=HUMAN_GATE_REF, dry_run=False)
    chk("queue-id 真寫無 --allow-apply → 拒", not ok_q1)
    ok_q2, _ = single_apply_gate(queue_id=565, allow_apply=True,
                                 gate_ref=AUTO_GATE_REF, dry_run=False)
    chk("queue-id 真寫 gate-ref 非人閘碼 → 拒", not ok_q2)
    ok_q3, r_q3 = single_apply_gate(queue_id=565, allow_apply=True,
                                    gate_ref=HUMAN_GATE_REF, dry_run=False)
    chk("queue-id 真寫 --allow-apply+人閘碼 → 武裝", ok_q3 and "armed" in r_q3)
    ok_q4, _ = single_apply_gate(queue_id=565, allow_apply=False, gate_ref=None, dry_run=True)
    chk("queue-id --dry-run 免武裝可預覽(唯讀)", ok_q4)
    ok_q5, _ = single_apply_gate(queue_id=None, allow_apply=False, gate_ref=None, dry_run=False)
    chk("無 queue-id 整批路不受影響(既有語意)", ok_q5)
    # 佈線鎖:haystack 限定該函式原始碼(非整檔,避免自我匹配假綠)
    chk("main 真寫前經 single_apply_gate", "single_apply_gate(" in inspect.getsource(main))
    chk("apply_pending 套 queue-id 篩選謂詞",
        "select_queue_rows(" in inspect.getsource(apply_pending))
    chk("矩陣含 --queue-id 用法", (__doc__ or "").count("--queue-id") >= 2)
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


def apply_pending(*, dry_run: bool, run_id: int | None,
                  queue_id: int | None = None,
                  gate_ref_label: str = AUTO_GATE_REF) -> int:
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

        # S-i 一次一顆:--queue-id 篩選謂詞(純函式);查無/非 pending_auto/被 --run-id 排除=大聲 rc=1
        if queue_id is not None:
            picked = select_queue_rows(items, queue_id)
            if not picked:
                cur.execute(
                    "SELECT queue_status, feature, run_id FROM promotion_queue WHERE queue_id=%s",
                    (queue_id,),
                )
                row = cur.fetchone()
                if row is None:
                    print(f"✗ --queue-id {queue_id}: promotion_queue 查無此列——不消費（rc=1）")
                elif row[0] != "pending_auto":
                    print(f"✗ --queue-id {queue_id}: queue_status={row[0]!r}"
                          f"（feature={row[1]} run={row[2]}）非 pending_auto——不消費（rc=1）")
                else:
                    print(f"✗ --queue-id {queue_id}: 該列 pending_auto 但 run={row[2]} 被 --run-id 篩掉"
                          f"（feature={row[1]}）——不消費（rc=1）")
                return 1
            items = picked

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

    scope = f" queue_id={queue_id} gate_ref={gate_ref_label}" if queue_id is not None else ""
    print(f"── PME APPLY (AUTO-B) kill={kill_eff} pending={len(items)} dry_run={dry_run}{scope} ──")
    if ctrl:
        print(f"  對照臂篩: 偽陽率(最壞)={ctrl['fp_rate_worst']:.1%} p95={ctrl['p95_worst']:.3f} "
              f"→ {'升嚴生效(R2c)' if ctrl['fp_rate_worst'] > 0.10 else '未觸發(≤10%)'}")
    else:
        print("  對照臂篩: 無 control_arms 證據——未加篩(誠實)")

    if kill_eff == KILL_HALT:
        # A5：halt 時拒絕一切 APPLY；可選把 pending 標 halted
        if not dry_run and items:
            with db.connect() as conn, db.transaction(conn) as cur:
                cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4-P2a)
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
                        cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4-P2a)
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
                        # R6:自動決策落帳可稽——gate_ref + 依據規則號(週日 digest 掃此);
                        # 整批路恆 V2-AUTOADVANCE(語意不變);--queue-id 武裝路落 TWEVO-APPLY-go(S-i 留痕)
                        json.dumps({"gate_json": gate_json, "run_id": rid,
                                    "gate_ref": gate_ref_label,
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
    ap.add_argument(
        "--queue-id", type=int, default=None,
        help="一次一顆（S-i）:僅消費該 queue_id 之 pending_auto;"
             f"真寫須併 --allow-apply --gate-ref {HUMAN_GATE_REF}、否則僅 --dry-run 預覽",
    )
    ap.add_argument(
        "--allow-apply", action="store_true",
        help=f"與 --queue-id 併用:允許單顆真寫（{HUMAN_GATE_REF};hugo 親跑＝授權載體）",
    )
    ap.add_argument(
        "--gate-ref", default=None,
        help=f"單顆真寫之人閘碼（須={HUMAN_GATE_REF};僅與 --queue-id 併用）",
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
    if args.queue_id is None and (args.allow_apply or args.gate_ref is not None):
        print("✗ --allow-apply / --gate-ref 僅與 --queue-id 併用（S-i 一次一顆）；"
              "整批路沿既有無旗標語意——未觸 DB、零寫入")
        return 2
    if args.queue_id is not None and args.backfill_prodset:
        print("✗ --queue-id 不適用於 --backfill-prodset——未觸 DB、零寫入")
        return 2
    if args.backfill_prodset:
        return backfill_prodset(dry_run=args.dry_run, run_id=args.run_id)
    ok_gate, gate_reason = single_apply_gate(
        queue_id=args.queue_id, allow_apply=args.allow_apply,
        gate_ref=args.gate_ref, dry_run=args.dry_run,
    )
    if not ok_gate:
        print(f"✗ {gate_reason}——未觸 DB、零寫入")
        return 2
    gate_label = HUMAN_GATE_REF if (args.queue_id is not None and args.allow_apply) else AUTO_GATE_REF
    return apply_pending(dry_run=args.dry_run, run_id=args.run_id,
                         queue_id=args.queue_id, gate_ref_label=gate_label)


if __name__ == "__main__":
    raise SystemExit(main())
