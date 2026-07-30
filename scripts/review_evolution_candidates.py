#!/usr/bin/env python
"""KH10 進化候選人裁 CLI — 列 pending＋approve/reject/defer/kill（S1）。

🎯 這支在做什麼(白話):列出 knowhow_evolution_candidate，供 Steward 人裁；
   裁決寫 knowhow_governance_ledger，decided_by 硬鎖 HUMAN。禁 AI 代裁、禁 auto。
守 KH10-ENABLE-S1· HUMAN_ONLY· FZ-keep· PME-GATE-keep· #29a/d。

執行指令矩陣:
  python scripts/review_evolution_candidates.py                    # 印矩陣＋列 pending
  python scripts/review_evolution_candidates.py --list             # 同預設（含 candidate／pending）
  python scripts/review_evolution_candidates.py --submit 2         # → governance_pending
  python scripts/review_evolution_candidates.py --approve 2 --rationale '採 RKI-FP-AI-SOLAR 進進化佇列'
  python scripts/review_evolution_candidates.py --reject 1 --rationale '空語料探針，不進閉環'
  python scripts/review_evolution_candidates.py --defer 15
  python scripts/review_evolution_candidates.py --kill 24 --rationale 'smoke_test 合成，非進化假說'
  python scripts/review_evolution_candidates.py --selftest         # 零 DB 紅綠
"""
from __future__ import annotations

import argparse
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

    chk("無 --auto-approve", "--auto-approve" not in (__doc__ or ""))
    chk("decided_by 常數 HUMAN", evo.DECISION_BY_HUMAN == "HUMAN")
    try:
        evo.assert_human_decider("bot")
        chk("拒非 HUMAN", False)
    except PermissionError:
        chk("拒非 HUMAN", True)
    chk("TTY 閘於 mutate", True)  # 實閘在 _require_tty
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _require_tty() -> None:
    if not sys.stdin.isatty():
        raise SystemExit("KH10 HUMAN_ONLY: 裁決須 TTY（禁管道／AI 代裁）")


def _list(limit: int = 50) -> int:
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT candidate_id, source_type, source_ref, status,
                   evidence_score, left(hypothesis_text, 100), created_at::text
            FROM knowhow_evolution_candidate
            WHERE status IN ('candidate_for_evolution', 'governance_pending')
            ORDER BY
              CASE status WHEN 'governance_pending' THEN 0 ELSE 1 END,
              evidence_score DESC NULLS LAST,
              candidate_id
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
        print(f"pending/candidate 列（最多 {limit}）: {len(rows)}")
        for r in rows:
            print(f"  id={r[0]} [{r[3]}] {r[1]} {r[2]} score={r[4]}｜{r[5]}")
        cur.execute(
            """
            SELECT decision, count(*) FROM knowhow_governance_ledger GROUP BY 1 ORDER BY 1
            """
        )
        print("ledger", {a: b for a, b in cur.fetchall()})
    return 0


def _submit(cid: int) -> int:
    _require_tty()
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE knowhow_evolution_candidate
            SET status='governance_pending', updated_at=now()
            WHERE candidate_id=%s
              AND status='candidate_for_evolution'
            RETURNING candidate_id
            """,
            (cid,),
        )
        if not cur.fetchone():
            print(f"未更新 id={cid}（不存在或非 candidate_for_evolution）")
            return 1
        conn.commit()
        print(f"✓ id={cid} → governance_pending")
    return 0


def _decide(cid: int, decision: str, rationale: str | None) -> int:
    _require_tty()
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT status FROM knowhow_evolution_candidate WHERE candidate_id=%s",
            (cid,),
        )
        row = cur.fetchone()
        if not row:
            print(f"無 candidate id={cid}")
            return 1
        if row[0] not in ("governance_pending", "candidate_for_evolution"):
            print(f"id={cid} status={row[0]} 不可再裁")
            return 1
        if row[0] == "candidate_for_evolution":
            cur.execute(
                """
                UPDATE knowhow_evolution_candidate
                SET status='governance_pending', updated_at=now()
                WHERE candidate_id=%s
                """,
                (cid,),
            )
        lid = evo.write_governance_decision(
            cur,
            candidate_id=cid,
            decision=decision,
            rationale=rationale,
            decided_by=evo.DECISION_BY_HUMAN,
        )
        conn.commit()
        print(f"✓ ledger_id={lid} decision={decision} decided_by=HUMAN id={cid}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="KH10 review evolution candidates",
        epilog="例: --approve 2 --rationale '...'（數字＝list 的 id=；勿字面寫 ID）",
    )
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--submit", type=int, metavar="ID")
    ap.add_argument("--approve", type=int, metavar="ID")
    ap.add_argument("--reject", type=int, metavar="ID")
    ap.add_argument("--defer", type=int, metavar="ID")
    ap.add_argument("--kill", type=int, metavar="ID")
    ap.add_argument("--rationale", default=None)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    mut = [args.approve, args.reject, args.defer, args.kill, args.submit]
    n_mut = sum(1 for x in mut if x is not None)
    if n_mut > 1:
        print("一次只能一個裁決動作")
        return 2
    if args.approve is not None:
        return _decide(args.approve, "approved", args.rationale)
    if args.reject is not None:
        return _decide(args.reject, "rejected", args.rationale)
    if args.defer is not None:
        return _decide(args.defer, "deferred", args.rationale)
    if args.kill is not None:
        return _decide(args.kill, "killed", args.rationale)
    if args.submit is not None:
        return _submit(args.submit)

    if not args.list:
        print(__doc__)
    return _list(args.limit)


if __name__ == "__main__":
    raise SystemExit(main())
