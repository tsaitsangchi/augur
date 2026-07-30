"""KH10 Evolution & Governance helpers — candidate 形成＋人裁邊界（S1）。

🎯 這支在做什麼(白話):把 KH6 probe／KH7 eligibility／KH9 synthesis 收成
   knowhow_evolution_candidate 列；governance 裁決**只允許 decided_by=HUMAN**。
   系統可 propose；禁 auto-approve／禁寫 philosophy／禁 APPLY prodset。
守 KH10-ENABLE-S1· HUMAN_ONLY· FZ-keep· PME-GATE-keep· #1(假說非 raw 列)· #29。

執行指令矩陣(library #18):
  python -m augur.knowledge.evolution
  python -m augur.knowledge.evolution --selftest
"""
from __future__ import annotations

import json
import sys
from typing import Any

DECISION_BY_HUMAN = "HUMAN"
SOURCE_TYPES = (
    "kh9_synthesis",
    "kh6_probe",
    "pme_xdom_map",
    "manual",
    "kh7_contradiction",
)
CANDIDATE_STATUSES = (
    "candidate_for_evolution",
    "governance_pending",
    "approved_for_loop",
    "rejected_for_loop",
    "superseded",
)
DECISIONS = ("approved", "rejected", "deferred", "superseded", "killed")

# 裁決後 status 對映
_DECISION_STATUS = {
    "approved": "approved_for_loop",
    "rejected": "rejected_for_loop",
    "deferred": "governance_pending",
    "superseded": "superseded",
    "killed": "rejected_for_loop",
}


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


def assert_human_decider(decided_by: str) -> None:
    if decided_by != DECISION_BY_HUMAN:
        raise PermissionError(
            f"KH10 HUMAN_ONLY: decided_by 必須為 {DECISION_BY_HUMAN!r}，得 {decided_by!r}"
        )


def hypothesis_from_kh7(row: dict) -> str:
    probe = row.get("probe_id") or "?"
    status = row.get("status") or "?"
    reasons = row.get("reasons") or []
    if isinstance(reasons, str):
        try:
            reasons = json.loads(reasons)
        except json.JSONDecodeError:
            reasons = [reasons]
    why = ",".join(str(r) for r in reasons[:4]) if reasons else "n/a"
    return f"KH7 {status} probe={probe} reasons=[{why}] → 是否值得進入進化閉環？"


def hypothesis_from_probe(row: dict) -> str:
    probe = row.get("probe_id") or "?"
    kind = row.get("interaction_kind") or "?"
    risk = row.get("spurious_risk") or "?"
    prompt = (row.get("expanded_prompt") or "")[:120]
    return f"KH6 probe={probe} kind={kind} spurious={risk}｜{prompt}"


def hypothesis_from_synthesis(row: dict) -> str:
    sid = row.get("synthesis_id")
    iid = row.get("item_id")
    score = row.get("evidence_score")
    q = (row.get("query_text") or "")[:100]
    return f"KH9 synthesis_id={sid} item_id={iid} evidence_score={score}｜{q}"


def existing_source_refs(cur, source_type: str) -> set[str]:
    cur.execute(
        "SELECT source_ref FROM knowhow_evolution_candidate WHERE source_type=%s",
        (source_type,),
    )
    return {str(r[0]) for r in cur.fetchall()}


def insert_candidate(
    cur,
    *,
    source_type: str,
    source_ref: str,
    hypothesis_text: str,
    target_domain: str = "investment",
    axes_json: Any = None,
    evidence_score: float | None = None,
    status: str = "candidate_for_evolution",
    note: str | None = None,
) -> int | None:
    """冪等 INSERT：同 (source_type, source_ref) 已存在則回 None。"""
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"bad source_type={source_type}")
    if status not in CANDIDATE_STATUSES:
        raise ValueError(f"bad status={status}")
    cur.execute(
        """
        SELECT candidate_id FROM knowhow_evolution_candidate
        WHERE source_type=%s AND source_ref=%s LIMIT 1
        """,
        (source_type, source_ref),
    )
    hit = cur.fetchone()
    if hit:
        return None
    cur.execute(
        """
        INSERT INTO knowhow_evolution_candidate
          (source_type, source_ref, hypothesis_text, target_domain,
           axes_json, evidence_score, status, note)
        VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s,%s)
        RETURNING candidate_id
        """,
        (
            source_type,
            str(source_ref),
            hypothesis_text,
            target_domain,
            _json(axes_json if axes_json is not None else []),
            evidence_score,
            status,
            note,
        ),
    )
    return int(cur.fetchone()[0])


def write_governance_decision(
    cur,
    *,
    candidate_id: int,
    decision: str,
    rationale: str | None = None,
    downstream_ref: str | None = None,
    decided_by: str = DECISION_BY_HUMAN,
) -> int:
    """寫 ledger＋更新 candidate status。decided_by 硬鎖 HUMAN。"""
    if decision not in DECISIONS:
        raise ValueError(f"bad decision={decision}")
    assert_human_decider(decided_by)
    new_status = _DECISION_STATUS[decision]
    cur.execute(
        """
        INSERT INTO knowhow_governance_ledger
          (candidate_id, decision, decided_by, rationale, downstream_ref)
        VALUES (%s,%s,%s,%s,%s)
        RETURNING ledger_id
        """,
        (candidate_id, decision, decided_by, rationale, downstream_ref),
    )
    ledger_id = int(cur.fetchone()[0])
    cur.execute(
        """
        UPDATE knowhow_evolution_candidate
        SET status=%s, updated_at=now()
        WHERE candidate_id=%s
        """,
        (new_status, candidate_id),
    )
    return ledger_id


def selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("SOURCE_TYPES 含 kh7/kh6/kh9", {"kh7_contradiction", "kh6_probe", "kh9_synthesis"} <= set(SOURCE_TYPES))
    chk("DECISION_BY_HUMAN", DECISION_BY_HUMAN == "HUMAN")
    try:
        assert_human_decider("AI")
        chk("拒 AI decider", False)
    except PermissionError:
        chk("拒 AI decider", True)
    h = hypothesis_from_kh7({"probe_id": "P", "status": "eligibility_pass", "reasons": ["a"]})
    chk("kh7 hypothesis 非空", "KH7" in h and "P" in h)
    chk("approved→approved_for_loop", _DECISION_STATUS["approved"] == "approved_for_loop")
    chk("無 auto_approve API", not hasattr(sys.modules[__name__], "auto_approve"))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="KH10 evolution helpers")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    print(__doc__)
    print("用途: insert_candidate / write_governance_decision（由 collect／review CLI 呼叫）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
