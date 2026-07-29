#!/usr/bin/env python
"""KH7 對抗可答性 runner — 讀 probe_run → 機械裁決 → 寫帳本。

🎯 這支在做什麼(白話):從 `knowhow_interaction_probe_result`（--from-run）或
   最新 run 載入探針摘要，呼叫 `kh7_eligibility.decide_eligibility`，寫入
   `knowhow_kh7_eligibility`。可選把裁決附註進 KH4 evidence（**不改** answer_status）。
   禁 approve／activate；零 FinMind／FRED；非答案 SSOT。
守 #29a/d· #1· HUMAN-APPROVE-keep· NHC-keep· FZ-keep。

執行指令矩陣:
  python scripts/run_kh7_eligibility.py                         # 安全預設:印矩陣
  python scripts/run_kh7_eligibility.py --from-run 1            # 回放 run_id（dry）
  python scripts/run_kh7_eligibility.py --from-run 1 --apply    # 寫帳本
  python scripts/run_kh7_eligibility.py --latest --apply        # 最新 run
  python scripts/run_kh7_eligibility.py --from-run 1 --apply --annotate-kh4
  python scripts/run_kh7_eligibility.py --selftest              # 零 DB 紅綠
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import kh4
from augur.knowledge import kh7_eligibility as kh7


def _row_to_summary(row: dict) -> dict:
    """ledger 列 → decide_eligibility 輸入形狀。"""
    hc = row.get("hit_counts") or {}
    if isinstance(hc, str):
        try:
            hc = json.loads(hc)
        except json.JSONDecodeError:
            hc = {}
    gap = row.get("gap_flags") or []
    if isinstance(gap, str):
        try:
            gap = json.loads(gap)
        except json.JSONDecodeError:
            gap = []
    axis = {}
    if isinstance(hc, dict):
        axis = hc.get("axis") or {}
        if isinstance(axis, str):
            try:
                axis = json.loads(axis)
            except json.JSONDecodeError:
                axis = {}
    tops = row.get("top_hits_json") or row.get("top_hits") or []
    if isinstance(tops, str):
        try:
            tops = json.loads(tops)
        except json.JSONDecodeError:
            tops = []
    axes = row.get("axis_hit_json") or row.get("axes") or []
    if isinstance(axes, str):
        try:
            axes = json.loads(axes)
        except json.JSONDecodeError:
            axes = []
    # 若 raw_json 有完整摘要則優先
    raw = row.get("raw_json")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = None
    if isinstance(raw, dict) and raw.get("merged_hits") is not None:
        return {
            "probe_id": raw.get("probe_id") or row.get("probe_id"),
            "merged_hits": raw.get("merged_hits"),
            "multi_source_hits": raw.get("multi_source_hits"),
            "axis_hit_counts": raw.get("axis_hit_counts") or axis,
            "gap_flags": raw.get("gap_flags") or gap,
            "spurious_risk": raw.get("spurious_risk") or row.get("spurious_risk"),
            "top_hits": raw.get("top_hits") or tops,
            "axes": raw.get("axes") or axes,
            "queries": raw.get("queries") or [],
        }
    return {
        "probe_id": row.get("probe_id"),
        "merged_hits": int((hc or {}).get("merged") or 0) if isinstance(hc, dict) else 0,
        "multi_source_hits": int((hc or {}).get("multi_source") or 0) if isinstance(hc, dict) else 0,
        "axis_hit_counts": axis if isinstance(axis, dict) else {},
        "gap_flags": gap if isinstance(gap, list) else [],
        "spurious_risk": row.get("spurious_risk"),
        "top_hits": tops if isinstance(tops, list) else [],
        "axes": axes if isinstance(axes, list) else [],
    }


def _load_run(cur, run_id: int) -> list[dict]:
    cur.execute(
        "SELECT probe_id, arity, interaction_kind, expanded_prompt, "
        "       axis_hit_json, hit_counts, gap_flags, spurious_risk, "
        "       top_hits_json, raw_json "
        "FROM knowhow_interaction_probe_result WHERE run_id=%s ORDER BY probe_id",
        (run_id,),
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _latest_run_id(cur) -> int | None:
    cur.execute(
        "SELECT run_id FROM knowhow_interaction_probe_run "
        "ORDER BY run_id DESC LIMIT 1"
    )
    row = cur.fetchone()
    return int(row[0]) if row else None


def _write_eligibility(cur, *, run_id: int, decisions: list[dict], note: str | None) -> int:
    n = 0
    for d in decisions:
        cur.execute(
            """
            INSERT INTO knowhow_kh7_eligibility
              (run_id, probe_id, status, reasons, evidence, script, note)
            VALUES (%s,%s,%s,%s::jsonb,%s::jsonb,'run_kh7_eligibility.py',%s)
            """,
            (
                run_id,
                d["probe_id"],
                d["status"],
                json.dumps(d.get("reasons") or [], ensure_ascii=False),
                json.dumps(d.get("evidence") or {}, ensure_ascii=False),
                note,
            ),
        )
        n += 1
    return n


def _annotate_kh4(cur, decisions: list[dict], *, run_id: int) -> int:
    """附註 evidence.kh7_last；閘欄（answer_status 等）一律不動。"""
    if not kh4._table_exists(cur, "knowledge_kh4_state"):
        print("  annotate-kh4: knowledge_kh4_state 未建——略過")
        return 0
    # 從 evidence 無法直接得 item_ids；改以 run 的 top_hits
    cur.execute(
        "SELECT probe_id, top_hits_json FROM knowhow_interaction_probe_result "
        "WHERE run_id=%s",
        (run_id,),
    )
    tops_by_probe = {}
    for pid, tops in cur.fetchall():
        if isinstance(tops, str):
            try:
                tops = json.loads(tops)
            except json.JSONDecodeError:
                tops = []
        tops_by_probe[pid] = tops or []

    n = 0
    for d in decisions:
        item_ids = sorted({
            int(h["item_id"])
            for h in tops_by_probe.get(d["probe_id"], [])
            if isinstance(h, dict) and h.get("kind") == "item" and h.get("item_id") is not None
        })
        if not item_ids:
            continue
        note = {
            "probe_id": d["probe_id"],
            "run_id": run_id,
            "status": d["status"],
            "reasons": d.get("reasons") or [],
            "annotated_at": datetime.now(timezone.utc).isoformat(),
        }
        cur.execute(
            """
            UPDATE knowledge_kh4_state
               SET evidence = COALESCE(evidence, '{}'::jsonb)
                              || jsonb_build_object('kh7_last', %s::jsonb),
                   updated_at = now()
             WHERE item_id = ANY(%s)
            """,
            (json.dumps(note, ensure_ascii=False), item_ids),
        )
        n += cur.rowcount
    return n


def run(conn, args) -> int:
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_interaction_probe_result')")
        if not cur.fetchone()[0]:
            print("knowhow_interaction_probe_result 未建——先跑 probe runner --write-ledger")
            return 1
        run_id = args.from_run
        if args.latest or run_id is None:
            run_id = _latest_run_id(cur)
        if run_id is None:
            print("無可用 run_id")
            return 1
        rows = _load_run(cur, int(run_id))
    if not rows:
        print(f"run_id={run_id} 無 result 列")
        return 1

    summaries = [_row_to_summary(r) for r in rows]
    decisions = kh7.batch_decide(summaries)

    print(f"── KH7 eligibility run_id={run_id} n={len(decisions)} ──")
    for d in decisions:
        print(
            f"  {d['probe_id']}: {d['status']}  reasons={d.get('reasons')}  "
            f"merged={d['evidence'].get('merged_hits')} "
            f"multi={d['evidence'].get('multi_source_hits')} "
            f"spur={d['evidence'].get('spurious_risk')}"
        )

    if not args.apply:
        print("(dry；加 --apply 才寫帳本)")
        return 0

    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_kh7_eligibility')")
        if not cur.fetchone()[0]:
            print("knowhow_kh7_eligibility 未建——先跑 migrate_kh7_eligibility_ddl.py --apply")
            return 1
        n = _write_eligibility(
            cur, run_id=int(run_id), decisions=decisions, note=args.note
        )
        print(f"wrote eligibility rows={n}")
        if args.annotate_kh4:
            ann = _annotate_kh4(cur, decisions, run_id=int(run_id))
            print(f"kh4 evidence annotated rows={ann} (answer_status 未改)")
    return 0


def selftest() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    import ast

    src = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls = []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                calls.append(fn.id)
            elif isinstance(fn, ast.Attribute):
                calls.append(fn.attr)

    check("指令矩陣含 --from-run/--apply/--selftest",
          all(x in src for x in ("--from-run", "--apply", "--selftest")))
    check("零 FinMind/FRED",
          not any("finmind" in (m or "").lower() or (m or "").lower() == "fred"
                  for m in imports))
    check("禁 approve/activate 呼叫",
          "approve" not in calls and "activate" not in calls
          and "transition" not in calls)
    # annotate SQL 不改 gate：只掃 UPDATE 片段（docstring 可提禁令字樣）
    upd_start = src.find("UPDATE knowledge_kh4_state")
    upd_end = src.find("return n", upd_start)
    annotate_sql = src[upd_start:upd_end] if upd_start >= 0 else ""
    check("annotate UPDATE 不改 answer_status",
          "answer_status" not in annotate_sql and "kh7_last" in annotate_sql)
    check("SET evidence only", "SET evidence" in annotate_sql)

    # 形狀轉換單元
    s = _row_to_summary({
        "probe_id": "P",
        "hit_counts": {"axis": {"a": 2, "b": 1}, "merged": 3, "multi_source": 1},
        "gap_flags": [],
        "spurious_risk": "low",
    })
    d = kh7.decide_eligibility(s)
    check("ledger 形狀可裁", d["status"] == "eligibility_pass")

    # library selftest
    check("library selftest", kh7._selftest() == 0)

    print("runner 自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KH7 adversarial eligibility runner")
    ap.add_argument("--from-run", type=int, help="probe_run run_id")
    ap.add_argument("--latest", action="store_true", help="用最新 run_id")
    ap.add_argument("--apply", action="store_true", help="寫 knowhow_kh7_eligibility")
    ap.add_argument("--annotate-kh4", action="store_true",
                    help="附註 KH4 evidence.kh7_last（不改 answer_status）")
    ap.add_argument("--note")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.from_run is None and not args.latest:
        print(__doc__)
        return 0

    with db.connect() as conn:
        return run(conn, args)


if __name__ == "__main__":
    sys.exit(main())
