#!/usr/bin/env python
"""哲學原則 status A7 對齊 — 誠實分類／可機械收斂（禁假綠翻 validated）。

🎯 這支在做什麼（白話）：依 evolution.classify_status_alignment 盤點 principle.status
   ↔ map validated_* ↔ promotion APPLY 證據。raw untested∩validated_* 在閘紅拒上線時
   歸 map_evidence_gate_rejected（誠實殘留），**絕不**靜默 UPDATE 成 validated。
   僅 apply_lag→set_validated、fake_validated→rollback_untested 可 --apply。

守 #1 #15 #29；計畫驗收 A7；FZ-keep；對齊 U-PME F-U-PME-5（禁假關）。

執行指令矩陣:
  python scripts/sync_philosophy_principle_status.py              # 唯讀審計（印分類）
  python scripts/sync_philosophy_principle_status.py --json       # JSON 摘要
  python scripts/sync_philosophy_principle_status.py --apply      # 僅 heal apply_lag／fake_validated
  python scripts/sync_philosophy_principle_status.py --apply --dry-run
  python scripts/sync_philosophy_principle_status.py --selftest   # 免 DB
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import (
    A7_VIOLATION_CLASSES,
    STATUS_ALIGNMENT_CLASSES,
    classify_coverage,
    classify_status_alignment,
    is_a7_violation,
    sync_action_for_alignment,
)


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("classes pinned", len(STATUS_ALIGNMENT_CLASSES) == 8)
    chk("violations pinned", A7_VIOLATION_CLASSES == frozenset({"fake_validated", "apply_lag"}))
    # 禁：有 validated_* + rejected → 不得建議 set_validated
    align = classify_status_alignment(
        status="untested",
        has_map_validated=True,
        has_promote_applied=False,
        has_rejected_gate=True,
    )
    chk("rejected class", align == "map_evidence_gate_rejected")
    chk("rejected no sync", sync_action_for_alignment(align) is None)
    # 禁：missing／blocked 不得當已對齊 validated
    align_b = classify_status_alignment(
        status="untested",
        has_map_validated=False,
        has_promote_applied=False,
        coverage_classes={"missing", "blocked_div"},
    )
    chk("blocked class", align_b == "coverage_blocked_or_missing")
    chk("blocked no set_validated", sync_action_for_alignment(align_b) is None)
    # 可：apply_lag 收斂
    chk(
        "apply_lag sync",
        sync_action_for_alignment(
            classify_status_alignment(
                status="untested", has_map_validated=True, has_promote_applied=True
            )
        )
        == "set_validated",
    )
    # 可：假綠回滾
    chk(
        "fake rollback",
        sync_action_for_alignment(
            classify_status_alignment(
                status="validated", has_map_validated=True, has_promote_applied=False
            )
        )
        == "rollback_untested",
    )
    chk("classify_coverage still blocked", classify_coverage("dividend_yield", in_feature_values=True) == "blocked_div")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _load_principle_rows(cur) -> list[dict]:
    cur.execute(
        """
        SELECT p.principle_id, p.status,
               EXISTS(
                 SELECT 1 FROM principle_factor_map m
                 WHERE m.principle_id = p.principle_id
                   AND (m.validated_ic IS NOT NULL OR m.validated_econ IS NOT NULL)
               ) AS has_map_validated,
               EXISTS(
                 SELECT 1 FROM promotion_queue q
                 JOIN evolution_apply_log a ON a.queue_id = q.queue_id
                 WHERE q.principle_id = p.principle_id
                   AND q.action = 'promote'
                   AND q.queue_status = 'applied'
               ) AS has_promote_applied,
               EXISTS(
                 SELECT 1 FROM promotion_queue q
                 WHERE q.principle_id = p.principle_id
                   AND q.queue_status = 'pending_auto'
               ) AS has_pending_auto,
               EXISTS(
                 SELECT 1 FROM promotion_queue q
                 WHERE q.principle_id = p.principle_id
                   AND q.queue_status = 'rejected_gate'
               ) AS has_rejected_gate
        FROM philosophy_principle p
        ORDER BY p.principle_id
        """
    )
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]

    # coverage classes per principle（用於 blocked/missing 誠實類）
    cur.execute(
        """
        SELECT m.principle_id, m.feature,
               EXISTS(SELECT 1 FROM feature_values fv WHERE fv.feature = m.feature) AS in_fv
        FROM principle_factor_map m
        """
    )
    cov_by: dict[int, set[str]] = {}
    for pid, feature, in_fv in cur.fetchall():
        cov_by.setdefault(pid, set()).add(
            classify_coverage(feature, in_feature_values=bool(in_fv))
        )
    for r in rows:
        r["coverage_classes"] = frozenset(cov_by.get(r["principle_id"], ()))
        r["alignment"] = classify_status_alignment(
            status=r["status"],
            has_map_validated=bool(r["has_map_validated"]),
            has_promote_applied=bool(r["has_promote_applied"]),
            has_pending_auto=bool(r["has_pending_auto"]),
            has_rejected_gate=bool(r["has_rejected_gate"]),
            coverage_classes=r["coverage_classes"],
        )
        r["sync_action"] = sync_action_for_alignment(r["alignment"])
        r["a7_violation"] = is_a7_violation(r["alignment"])
    return rows


def audit_and_maybe_apply(*, do_apply: bool, dry_run: bool, as_json: bool) -> int:
    from augur.core import db

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.philosophy_principle')")
        if cur.fetchone()[0] is None:
            print("✗ philosophy_principle 不存在")
            return 1
        rows = _load_principle_rows(cur)

    tallies = Counter(r["alignment"] for r in rows)
    raw_desync = sum(
        1
        for r in rows
        if r["status"] == "untested" and r["has_map_validated"]
    )
    violations = [r for r in rows if r["a7_violation"]]
    syncable = [r for r in rows if r["sync_action"]]
    a7_ok = len(violations) == 0

    summary = {
        "n_principles": len(rows),
        "principle_status": dict(Counter(r["status"] for r in rows)),
        "raw_desync_untested_cap_validated_star": raw_desync,
        "alignment_tallies": dict(tallies),
        "a7_violations": len(violations),
        "a7_closed": a7_ok,
        "syncable": len(syncable),
        "note": (
            "raw_desync 在 map_evidence_gate_rejected 下≠A7 違規；"
            "禁把 missing／blocked_div／gate_rejected 翻 validated"
        ),
    }

    if as_json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("── PME A7 status alignment ──")
        print(f"  principles={summary['n_principles']}  status={summary['principle_status']}")
        print(f"  raw_desync(untested∩validated_*)={raw_desync}")
        print(f"  alignment={dict(tallies)}")
        print(f"  a7_violations={len(violations)}  a7_closed={a7_ok}")
        print(f"  syncable={len(syncable)}  ({'dry-run' if dry_run else 'live'} apply={do_apply})")
        print(f"  ⚠ {summary['note']}")
        for r in rows:
            if r["alignment"] in (
                "aligned_untested_clean",
                "aligned_validated",
            ) and not r["sync_action"]:
                continue
            flag = "✗" if r["a7_violation"] else ("→" if r["sync_action"] else "·")
            print(
                f"  {flag} pid={r['principle_id']} status={r['status']:10} "
                f"align={r['alignment']:28} sync={r['sync_action']}"
            )

    if not do_apply:
        return 0 if a7_ok else 1

    # --apply：只 heal 允許的 sync_action；永不對 gate_rejected 翻 validated
    healed = 0
    with db.connect() as conn:
        for r in syncable:
            action = r["sync_action"]
            new_status = "validated" if action == "set_validated" else "untested"
            print(
                f"  {'DRY ' if dry_run else ''}HEAL pid={r['principle_id']} "
                f"{r['status']}→{new_status} via {action} (align={r['alignment']})"
            )
            if dry_run:
                healed += 1
                continue
            with db.transaction(conn) as cur:
                cur.execute(
                    "UPDATE philosophy_principle SET status=%s WHERE principle_id=%s",
                    (new_status, r["principle_id"]),
                )
            healed += 1
    print(f"✓ healed={healed}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--apply", action="store_true", help="僅 apply_lag／fake_validated")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    return audit_and_maybe_apply(
        do_apply=args.apply, dry_run=args.dry_run, as_json=args.json
    )


if __name__ == "__main__":
    raise SystemExit(main())
