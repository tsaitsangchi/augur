#!/usr/bin/env python
"""KH10 進化候選收集 — 從 KH6／KH7／KH9 掃描 INSERT candidate（S1）。

🎯 這支在做什麼(白話):讀庫內 KH7 eligibility_pass、KH6 probe、KH9 synthesis
   高分列，冪等寫入 knowhow_evolution_candidate。只 propose、不人裁、不 APPLY。
守 KH10-ENABLE-S1· #1(假說句非 raw 灌列)· FZ-keep· HUMAN_ONLY· #29a/d。

執行指令矩陣:
  python scripts/collect_evolution_candidates.py                 # 印矩陣＋現況
  python scripts/collect_evolution_candidates.py --dry-run       # 試算將收幾筆（零寫入）
  python scripts/collect_evolution_candidates.py --apply         # 寫入 candidate
  python scripts/collect_evolution_candidates.py --apply --pending  # 直接進 governance_pending
  python scripts/collect_evolution_candidates.py --sources kh7,kh6  # 限來源
  python scripts/collect_evolution_candidates.py --limit-syn 20   # KH9 上限（預設 20）
  python scripts/collect_evolution_candidates.py --selftest      # 零 DB 紅綠
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import evolution as evo


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("hypothesis_from_kh7", "KH7" in evo.hypothesis_from_kh7({"probe_id": "X", "status": "eligibility_pass", "reasons": []}))
    chk("無 auto-approve 旗標於矩陣", "--auto-approve" not in (__doc__ or ""))
    chk("指令矩陣含 --apply/--selftest", "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _status_counts(cur) -> dict:
    cur.execute(
        "SELECT status, count(*) FROM knowhow_evolution_candidate GROUP BY 1 ORDER BY 1"
    )
    return {r[0]: r[1] for r in cur.fetchall()}


def collect(dry: bool, pending: bool, sources: set[str], limit_syn: int) -> int:
    status = "governance_pending" if pending else "candidate_for_evolution"
    inserted = {"kh7": 0, "kh6": 0, "kh9": 0, "skip": 0}
    with db.connect() as conn, conn.cursor() as cur:
        if "kh7" in sources:
            cur.execute(
                """
                SELECT eligibility_id, run_id, probe_id, status, reasons, evidence
                FROM knowhow_kh7_eligibility
                WHERE status = 'eligibility_pass'
                ORDER BY eligibility_id
                """
            )
            rows = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
            for row in rows:
                ref = f"kh7:{row['eligibility_id']}:{row['probe_id']}"
                hyp = evo.hypothesis_from_kh7(row)
                ev = row.get("evidence")
                score = None
                if isinstance(ev, dict) and ev.get("merged_hits") is not None:
                    try:
                        score = float(ev["merged_hits"])
                    except (TypeError, ValueError):
                        score = None
                if dry:
                    print(f"  [dry] kh7 {ref}｜{hyp[:80]}")
                    inserted["kh7"] += 1
                    continue
                cid = evo.insert_candidate(
                    cur,
                    source_type="kh7_contradiction",
                    source_ref=ref,
                    hypothesis_text=hyp,
                    axes_json=ev if isinstance(ev, (dict, list)) else [],
                    evidence_score=score,
                    status=status,
                    note="collect_evolution_candidates.py",
                )
                if cid is None:
                    inserted["skip"] += 1
                else:
                    inserted["kh7"] += 1

        if "kh6" in sources:
            cur.execute(
                """
                SELECT DISTINCT ON (probe_id)
                       probe_id, interaction_kind, spurious_risk, expanded_prompt, run_id
                FROM knowhow_interaction_probe_result
                WHERE COALESCE(spurious_risk, 'low') IN ('low', 'medium')
                ORDER BY probe_id, created_at DESC
                """
            )
            rows = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
            for row in rows:
                ref = f"kh6:{row['run_id']}:{row['probe_id']}"
                hyp = evo.hypothesis_from_probe(row)
                if dry:
                    print(f"  [dry] kh6 {ref}｜{hyp[:80]}")
                    inserted["kh6"] += 1
                    continue
                cid = evo.insert_candidate(
                    cur,
                    source_type="kh6_probe",
                    source_ref=ref,
                    hypothesis_text=hyp,
                    status=status,
                    note="collect_evolution_candidates.py",
                )
                if cid is None:
                    inserted["skip"] += 1
                else:
                    inserted["kh6"] += 1

        if "kh9" in sources:
            cur.execute(
                """
                SELECT synthesis_id, item_id, query_text, answer_state, evidence_score
                FROM knowhow_synthesis_run
                WHERE evidence_score IS NOT NULL AND evidence_score >= 0.8
                ORDER BY evidence_score DESC, synthesis_id DESC
                LIMIT %s
                """,
                (limit_syn,),
            )
            rows = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
            for row in rows:
                ref = f"kh9:{row['synthesis_id']}"
                hyp = evo.hypothesis_from_synthesis(row)
                score = float(row["evidence_score"]) if row.get("evidence_score") is not None else None
                if dry:
                    print(f"  [dry] kh9 {ref}｜{hyp[:80]}")
                    inserted["kh9"] += 1
                    continue
                cid = evo.insert_candidate(
                    cur,
                    source_type="kh9_synthesis",
                    source_ref=ref,
                    hypothesis_text=hyp,
                    evidence_score=score,
                    status=status,
                    note="collect_evolution_candidates.py",
                )
                if cid is None:
                    inserted["skip"] += 1
                else:
                    inserted["kh9"] += 1

        if not dry:
            conn.commit()
        print("inserted", inserted, "status=", status, "dry=" + str(dry))
        print("candidate_status", _status_counts(cur))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KH10 collect evolution candidates")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--pending", action="store_true", help="寫入 status=governance_pending")
    ap.add_argument("--sources", default="kh7,kh6,kh9", help="逗號分隔 kh7,kh6,kh9")
    ap.add_argument("--limit-syn", type=int, default=20)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if not args.apply and not args.dry_run:
        print(__doc__)
        with db.connect() as conn, conn.cursor() as cur:
            print("現況 candidate_status", _status_counts(cur))
            for t, q in (
                ("kh7_pass", "SELECT count(*) FROM knowhow_kh7_eligibility WHERE status='eligibility_pass'"),
                ("kh6_probe", "SELECT count(DISTINCT probe_id) FROM knowhow_interaction_probe_result"),
                ("kh9_hi", "SELECT count(*) FROM knowhow_synthesis_run WHERE evidence_score>=0.8"),
            ):
                cur.execute(q)
                print(f"  source {t}={cur.fetchone()[0]}")
        return 0

    sources = {s.strip().lower() for s in args.sources.split(",") if s.strip()}
    return collect(dry=args.dry_run and not args.apply, pending=args.pending, sources=sources, limit_syn=args.limit_syn)


if __name__ == "__main__":
    raise SystemExit(main())
