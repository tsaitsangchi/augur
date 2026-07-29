#!/usr/bin/env python
"""KNI-S3 固定評測套件 — 跑 suite case＋消融／decline 機械斷言。

🎯 這支在做什麼(白話):讀 `knowhow_eval_suite_case` active 列，複用
   `run_knowhow_interaction_probes.run_probe` 實跑檢索＋RRF，產出指標表／報告。
   禁答案樹、禁 approve、零 FinMind／FRED。
守 #29a/d· #1· #15· NHC-keep· FZ-keep· RKI-keep· predict-vs-market-api。

執行指令矩陣:
  python scripts/eval_knowhow_interaction_probes.py              # 安全預設:印矩陣+--show
  python scripts/eval_knowhow_interaction_probes.py --show       # 列 active suite cases
  python scripts/eval_knowhow_interaction_probes.py --run        # live 跑四 case
  python scripts/eval_knowhow_interaction_probes.py --run --report reports/augur_kni_s3_eval_20260729.md
  python scripts/eval_knowhow_interaction_probes.py --run --write-ledger
  python scripts/eval_knowhow_interaction_probes.py --selftest   # 零 DB 紅綠
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

# 複用 S2 runner（不改閘語意）
from run_knowhow_interaction_probes import (  # noqa: E402
    _load_probes,
    _print_result,
    _write_ledger,
    run_probe,
)


def _load_suite(cur, *, case_ids=None):
    sql = (
        "SELECT case_id, probe_id, role, expect_json, active, note "
        "FROM knowhow_eval_suite_case WHERE active"
    )
    params: list = []
    if case_ids:
        sql += " AND case_id = ANY(%s)"
        params.append(list(case_ids))
    sql += " ORDER BY case_id"
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def show(conn) -> int:
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_eval_suite_case')")
        if not cur.fetchone()[0]:
            print("knowhow_eval_suite_case 未建——先跑 migrate_knowhow_eval_suite_ddl.py --apply")
            return 1
        rows = _load_suite(cur)
    print(f"── eval suite cases:{len(rows)} ──")
    for r in rows:
        print(f"  {r['case_id']} → {r['probe_id']} [{r['role']}]")
    return 0


def _assert_decline(result: dict, expect_json) -> tuple[bool, str]:
    """expect_decline：no_corpus／空命中／ungrounded_hits／KH7 fail。"""
    from augur.knowledge import kh7_eligibility as kh7

    gap = result.get("gap_flags") or []
    if "no_corpus" in gap or int(result.get("merged_hits") or 0) <= 0:
        return True, "no_corpus∈gap_or_empty"
    if (
        "ungrounded_hits" in gap
        or result.get("ungrounded_hits")
        or kh7.detect_ungrounded(result)
    ):
        return True, "ungrounded_hits"
    if isinstance(expect_json, str):
        try:
            expect_json = json.loads(expect_json)
        except json.JSONDecodeError:
            expect_json = {}
    expect_json = expect_json or {}
    status = result.get("kh7_status")
    if status is None:
        status = kh7.decide_eligibility(result)["status"]
        result["kh7_status"] = status
    if status == expect_json.get("or_kh7", "eligibility_fail"):
        return True, f"kh7_{status}"
    return False, (
        f"expected decline but gap={gap} merged={result.get('merged_hits')} "
        f"kh7={status}"
    )

def _write_report(path: Path, rows: list[dict], *, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_role = {r["role"]: r for r in rows}
    lines = [
        f"# KNI-S3 eval [I] ({meta.get('started')})",
        "",
        "* 性質：[I] 評測產物；非答案 SSOT；非 [N]",
        f"* cases: {', '.join(r['case_id'] for r in rows)}",
        f"* run_id: {meta.get('run_id')}",
        f"* decline_ok: {meta.get('decline_ok')}",
        "",
        "## 逐 case 指標",
        "",
        "| case_id | role | probe_id | merged | multi_src | spurious | gap_flags |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for r in rows:
        gap = json.dumps(r.get("gap_flags") or [], ensure_ascii=False)
        lines.append(
            f"| {r['case_id']} | {r['role']} | {r['probe_id']} | "
            f"{r.get('merged_hits')} | {r.get('multi_source_hits')} | "
            f"{r.get('spurious_risk')} | `{gap}` |"
        )
    lines.append("")
    lines.append("## 消融對照（full vs no-FP vs no-AI）")
    lines.append("")
    full = by_role.get("full_triple") or {}
    no_fp = by_role.get("ablation_no_principle") or {}
    no_ai = by_role.get("ablation_no_ai") or {}
    lines.append("| arm | merged | multi_src | spurious | Δmulti vs full | Δspur note |")
    lines.append("|---|---:|---:|---|---:|---|")
    for label, arm in (
        ("full_triple", full),
        ("ablation_no_principle", no_fp),
        ("ablation_no_ai", no_ai),
    ):
        if not arm:
            lines.append(f"| {label} | — | — | — | — | missing |")
            continue
        d_multi = (
            int(arm.get("multi_source_hits") or 0)
            - int(full.get("multi_source_hits") or 0)
            if full
            else 0
        )
        lines.append(
            f"| {label} | {arm.get('merged_hits')} | {arm.get('multi_source_hits')} | "
            f"{arm.get('spurious_risk')} | {d_multi:+d} | "
            f"spur={arm.get('spurious_risk')} vs full={full.get('spurious_risk')} |"
        )
    lines.append("")
    decline = by_role.get("expect_decline") or {}
    lines.append("## expect_decline 機械斷言")
    lines.append("")
    lines.append(f"- probe: `{decline.get('probe_id')}`")
    lines.append(f"- gap_flags: `{decline.get('gap_flags')}`")
    lines.append(f"- merged_hits: {decline.get('merged_hits')}")
    lines.append(
        f"- decline 判準: no_corpus ∨ ungrounded_hits ∨ KH7=eligibility_fail"
        f"（e5 top‑k 近鄰≠落地）"
    )
    lines.append(
        f"- assert: **{meta.get('decline_msg')}** → "
        f"{'PASS' if meta.get('decline_ok') else 'FAIL'}"
    )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report → {path}")


def run(conn, args) -> int:
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_eval_suite_case')")
        if not cur.fetchone()[0]:
            print("knowhow_eval_suite_case 未建——先跑 migrate_knowhow_eval_suite_ddl.py --apply")
            return 1
        suite = _load_suite(cur, case_ids=args.case_id or None)
        if not suite:
            print("無 active suite case")
            return 1
        probe_ids = [s["probe_id"] for s in suite]
        probes = _load_probes(cur, probe_ids=probe_ids)
        by_pid = {p["probe_id"]: p for p in probes}

    scope = (True, frozenset(), None)  # steward 診斷 scope；非聊天入口
    from augur.knowledge import kh7_eligibility as kh7

    results_meta = []
    probe_results = []
    for case in suite:
        row = by_pid.get(case["probe_id"])
        if not row:
            print(f"  ✗ probe 缺列: {case['probe_id']} (case={case['case_id']})")
            return 1
        # live 檢索（含 expect_decline）：無意義軸靠 ungrounded_hits 機械 decline，
        # 不假裝 KNN 會回空（e5 top‑k 幾乎永有鄰居）。
        result = run_probe(
            row,
            k_per_query=args.k,
            dry_run=False,
            scope=scope,
        )
        kh7_d = kh7.decide_eligibility(result)
        result = dict(result)
        result["kh7_status"] = kh7_d["status"]
        result["kh7_reasons"] = kh7_d["reasons"]
        _print_result(result)
        print(f"  kh7: {kh7_d['status']} reasons={kh7_d['reasons']}")
        entry = {
            "case_id": case["case_id"],
            "role": case["role"],
            "expect_json": case.get("expect_json") or {},
            **result,
        }
        results_meta.append(entry)
        probe_results.append(result)

    decline_ok = True
    decline_msg = "n/a"
    for entry in results_meta:
        if entry["role"] == "expect_decline":
            decline_ok, decline_msg = _assert_decline(entry, entry.get("expect_json"))
            print(f"\n── decline assert: {'PASS' if decline_ok else 'FAIL'} ({decline_msg}) ──")

    run_id = None
    if args.write_ledger:
        with db.transaction(conn) as cur:
            run_id = _write_ledger(
                cur,
                results=probe_results,
                params_json={
                    "suite": "kni-s3",
                    "case_ids": [r["case_id"] for r in results_meta],
                    "k": args.k,
                },
                note=args.note or "kni-s3-eval",
            )
        print(f"ledger run_id={run_id}")

    if args.report:
        _write_report(
            Path(args.report),
            results_meta,
            meta={
                "started": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                "run_id": run_id,
                "decline_ok": decline_ok,
                "decline_msg": decline_msg,
            },
        )

    print("\n── 消融摘要 ──")
    for r in results_meta:
        print(
            f"  {r['role']}: merged={r['merged_hits']} multi={r['multi_source_hits']} "
            f"spur={r['spurious_risk']} gap={r['gap_flags']}"
        )

    return 0 if decline_ok else 2


def selftest() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    import ast

    src = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    imports = []
    calls = []
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

    check("指令矩陣含 --run/--selftest/--report",
          all(x in src for x in ("--run", "--selftest", "--report")))
    check("複用 run_probe", "run_probe" in src)
    check("零 FinMind/FRED import",
          not any("finmind" in (m or "").lower() or (m or "").lower() == "fred"
                  or (m or "").endswith(".fred") for m in imports))
    check("禁 approve/activate 呼叫",
          "approve" not in calls and "activate" not in calls)
    ok_d, msg = _assert_decline(
        {"gap_flags": ["no_corpus"], "merged_hits": 0},
        {"gap_contains": "no_corpus"},
    )
    check("decline assert 綠路徑", ok_d and "no_corpus" in msg)
    ok_u, msg_u = _assert_decline(
        {"gap_flags": ["ungrounded_hits"], "merged_hits": 16, "ungrounded_hits": True},
        {},
    )
    check("decline assert ungrounded 綠", ok_u and "ungrounded" in msg_u)
    bad_d, _ = _assert_decline(
        {"gap_flags": [], "merged_hits": 5, "kh7_status": None},
        {},
    )
    check("decline assert 紅路徑", not bad_d)
    print("eval 自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KNI-S3 knowhow eval suite")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--case-id", action="append")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--write-ledger", action="store_true")
    ap.add_argument("--report", help="markdown 報告路徑")
    ap.add_argument("--note")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not any((args.show, args.run)):
        print(__doc__)
        args.show = True

    with db.connect() as conn:
        if args.show and not args.run:
            return show(conn)
        if args.run:
            if args.show:
                show(conn)
            return run(conn, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
