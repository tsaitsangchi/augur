#!/usr/bin/env python3
"""🎯 寫入／更新 `treaty_probe_binding`——條文↔live 探針綁定（M-N1／M-W1）。

本支**只綁定、不量測**；量測走 `read_treaty_probes.py`。尺須已在 `measure_registry`
（先 `register_measure.py --register-defaults`）。設計 SSOT＝master plan §1.4 M-N1／第 33 步
（七框＋六同綁＝13；deadline=2026-10-14）。

人裁框 `owner=Steward`：AI 讀值時 verdict 被 DB CHECK 鎖成 undecidable（禁代勾）。

守原則 #6 #12 #15 #29a/d；RULING-2026-039 禁假關。

執行指令矩陣
------------
    python3 scripts/sync_treaty_probes.py                    # 無參數＝印矩陣＋--status
    python3 scripts/sync_treaty_probes.py --status           # 唯讀：綁定列況
    python3 scripts/sync_treaty_probes.py --seed-1014        # 冪等 upsert ≥13 條 10-14 綁定
    python3 scripts/sync_treaty_probes.py --seed-doc         # 冪等 upsert doc 族（第 19 步：文件數字→探針）
    python3 scripts/sync_treaty_probes.py --selftest         # 免 DB
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
DEADLINE = "2026-10-14"
MEASURE = ("treaty_1014_probe", "line_snapshot")

# (probe_id, clause_ref, owner, check_cmd, expect_expr)
# expect_expr 對 Steward＝字面 undecidable（人裁）；對 AI＝可機判短語（本種子全 Steward）
SEED_1014 = [
    (
        "1014_wm35_36",
        "ULTRACODE-SCHEDULE.md:116",
        "Steward",
        "sed -n '116p' ULTRACODE-SCHEDULE.md",
        "undecidable",
    ),
    (
        "1014_025_stages",
        "ULTRACODE-SCHEDULE.md:117",
        "Steward",
        "sed -n '117p' ULTRACODE-SCHEDULE.md",
        "undecidable",
    ),
    (
        "1014_029_l5",
        "ULTRACODE-SCHEDULE.md:118",
        "Steward",
        "sed -n '118p' ULTRACODE-SCHEDULE.md",
        "undecidable",
    ),
    (
        "1014_l716_matrix",
        "ULTRACODE-SCHEDULE.md:119",
        "Steward",
        "sed -n '119p' ULTRACODE-SCHEDULE.md",
        "undecidable",
    ),
    (
        "1014_kdo4_ldo4",
        "ULTRACODE-SCHEDULE.md:120",
        "Steward",
        "sed -n '120p' ULTRACODE-SCHEDULE.md",
        "undecidable",
    ),
    (
        "1014_020_m2",
        "ULTRACODE-SCHEDULE.md:121",
        "Steward",
        "sed -n '121p' ULTRACODE-SCHEDULE.md",
        "undecidable",
    ),
    (
        "1014_gov3b_evidence",
        "ULTRACODE-SCHEDULE.md:122",
        "Steward",
        "sed -n '122p' ULTRACODE-SCHEDULE.md",
        "undecidable",
    ),
    # —— 六項同綁 ——
    (
        "1014_r002_body2",
        "constitution/RULING-2026-002-LAYER1-ADOPTION.md:23",
        "Steward",
        "sed -n '23,37p' constitution/RULING-2026-002-LAYER1-ADOPTION.md | head -c 400",
        "undecidable",
    ),
    (
        "1014_r002_body5",
        "constitution/RULING-2026-002-LAYER1-ADOPTION.md:47",
        "Steward",
        "sed -n '47,53p' constitution/RULING-2026-002-LAYER1-ADOPTION.md | head -c 400",
        "undecidable",
    ),
    (
        "1014_ldi7_l7",
        "specs/INFRASTRUCTURE-SPECIFICATION.md:608",
        "Steward",
        "sed -n '608p' specs/INFRASTRUCTURE-SPECIFICATION.md",
        "undecidable",
    ),
    (
        "1014_d_prin_2",
        "docs/compliance/CS-原則精華_v1.12.0.md:69",
        "Steward",
        "sed -n '69p' docs/compliance/CS-原則精華_v1.12.0.md",
        "undecidable",
    ),
    (
        "1014_ve_manual_expiry",
        "reports/augur_optimization_master_plan_20260803.md:782",
        "Steward",
        "venv/bin/python scripts/probe_ve_manual_1014_window.py",
        "undecidable",
    ),
    (
        "1014_r012_phase7",
        "constitution/RULING-2026-012-MIGRATION-PLAN-ADOPTION.md:13",
        "Steward",
        "sed -n '13,16p' constitution/RULING-2026-012-MIGRATION-PLAN-ADOPTION.md | head -c 400",
        "undecidable",
    ),
]

# doc 族（M-N1 第 19 步：文件硬編數字→探針 diff）。owner=AI＝機讀快照；deadline 無。
# (probe_id, clause_ref, owner, measure_key, ruler_key, check_cmd)
# 文件端以 <!--probe:ID-->值<!--/probe--> 標記；read_treaty_probes.py --check 對標記驗 diff。
_PY = "venv/bin/python -c 'from augur.core import config; import psycopg2; conn=psycopg2.connect(**config.DB_PARAMS); cur=conn.cursor(); "
_CMD_MATRIX = (
    "venv/bin/python scripts/check_cmd_matrix.py 2>/dev/null | "
    "grep -oE '受檢 [0-9]+ 支' | grep -oE '[0-9]+'"
)
_CMD_VE = (
    _PY + "cur.execute(\"SELECT status, count(*) FROM validation_evidence GROUP BY 1\"); "
    "d=dict(cur.fetchall()); print(\"total=%d green=%d red=%d unverified=%d\" % "
    "(sum(d.values()), d.get(\"green\",0), d.get(\"red\",0), d.get(\"unverified\",0)))'"
)
SEED_DOC = [
    (
        "doc_handoff_cron_lines",
        "HANDOFF.md:26",
        "AI",
        "crontab_entries",
        "grep_leading_numeric",
        "crontab -l | grep -c '^[0-9*]'",
    ),
    (
        "doc_handoff_deferred_uncleared",
        "HANDOFF.md:50",
        "AI",
        "deferred_work_uncleared",
        "sql_cleared_at_null",
        _PY + "cur.execute(\"SELECT count(*) FROM evolution_deferred_work "
        "WHERE cleared_at IS NULL\"); print(cur.fetchone()[0])'",
    ),
    (
        "doc_handoff_ve_status",
        "HANDOFF.md:51",
        "AI",
        "validation_evidence_status",
        "sql_group_by_status",
        _CMD_VE,
    ),
    (
        # 綁定先立；CLAUDE.md 為治權檔，標記落文＝M-N3（需裁，#19 逐段呈）
        "doc_claude_scripts_matrix",
        "CLAUDE.md:127",
        "AI",
        "script_entry_count",
        "cmd_matrix_scope",
        _CMD_MATRIX,
    ),
    (
        "doc_workflow_lint_errors",
        "tools/constitution_lint/github-workflow.yml:35",
        "AI",
        "lint_total_errors",
        "report_json",
        "venv/bin/python -m tools.constitution_lint report 2>/dev/null | "
        "grep -oE '\"total_errors\": [0-9]+' | grep -oE '[0-9]+$'",
    ),
    (
        "doc_workflow_selftest_status",
        "tools/constitution_lint/github-workflow.yml:66",
        "AI",
        "lint_selftest_status",
        "rc_pass_fail",
        "venv/bin/python -m tools.constitution_lint --selftest >/dev/null 2>&1 "
        "&& echo PASS || echo FAIL",
    ),
    (
        "doc_f2_registry_tables",
        "reports/augur_1014_review_evidence_prep_20260801.md:43",
        "AI",
        "wm36_registry_tables",
        "pg_class_concept_like",
        _PY + "cur.execute(\"SELECT count(*) FROM pg_class c JOIN pg_namespace n "
        "ON n.oid=c.relnamespace WHERE n.nspname=%s AND c.relname LIKE %s AND c.relkind=%s\", "
        "(\"public\",\"%concept%\",\"r\")); print(cur.fetchone()[0])'",
    ),
    (
        "doc_f2_vendor_bind_grep",
        "reports/augur_1014_review_evidence_prep_20260801.md:49",
        "AI",
        "vendor_direct_bind",
        "grep_from_taiwan_src_scripts",
        "grep -rlE 'FROM\\s+\"Taiwan' src scripts --include='*.py' | wc -l",
    ),
    (
        "doc_mem_tgs_matrix",
        "handoff_memory/augur-three-gate-strengths.md:13",
        "AI",
        "script_entry_count",
        "cmd_matrix_scope",
        _CMD_MATRIX,
    ),
    (
        "doc_mem_tgs_ve",
        "handoff_memory/augur-three-gate-strengths.md:17",
        "AI",
        "validation_evidence_status",
        "sql_group_by_status",
        _CMD_VE,
    ),
    (
        "doc_mem_pg_tuning",
        "handoff_memory/db-import-tuning-hnsw-oom.md:32",
        "AI",
        "pg_memory_settings",
        "show_three",
        _PY + "cur.execute(\"SHOW shared_buffers\"); a=cur.fetchone()[0]; "
        "cur.execute(\"SHOW work_mem\"); b=cur.fetchone()[0]; "
        "cur.execute(\"SHOW maintenance_work_mem\"); c=cur.fetchone()[0]; "
        "print(\"shared_buffers=\"+a+\" work_mem=\"+b+\" maintenance_work_mem=\"+c)'",
    ),
]


def _conn():
    from augur.core import db
    return db.connect()


def cmd_status() -> int:
    with _conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.treaty_probe_binding')")
        if cur.fetchone()[0] is None:
            print("✗ treaty_probe_binding 不在——先 migrate_treaty_probe_ddl.py --apply")
            return 1
        cur.execute(
            """SELECT count(*),
                      count(*) FILTER (WHERE deadline = DATE %s),
                      count(*) FILTER (WHERE owner='Steward')
               FROM treaty_probe_binding""",
            (DEADLINE,),
        )
        n, n14, n_st = cur.fetchone()
        print(f"綁定 {n} 條｜deadline={DEADLINE} {n14}（目標≥13）｜Steward {n_st}")
        if n14 < 13:
            print(f"⚠ 未達 13——跑 --seed-1014")
            return 1
        return 0


def cmd_seed() -> int:
    from augur.core import db
    mk, rk = MEASURE
    with _conn() as conn, db.transaction(conn) as cur:
        cur.execute(
            "SELECT 1 FROM measure_registry WHERE measure_key=%s AND ruler_key=%s",
            (mk, rk),
        )
        if not cur.fetchone():
            print(f"✗ 尺 {mk}/{rk} 未登錄——先 register_measure.py --register-defaults")
            return 1
        for probe_id, clause_ref, owner, check_cmd, expect_expr in SEED_1014:
            cur.execute(
                """INSERT INTO treaty_probe_binding
                     (probe_id, clause_ref, deadline, measure_key, ruler_key,
                      check_cmd, expect_expr, owner)
                   VALUES (%s,%s,%s::date,%s,%s,%s,%s,%s)
                   ON CONFLICT (probe_id) DO UPDATE SET
                     clause_ref=EXCLUDED.clause_ref,
                     deadline=EXCLUDED.deadline,
                     measure_key=EXCLUDED.measure_key,
                     ruler_key=EXCLUDED.ruler_key,
                     check_cmd=EXCLUDED.check_cmd,
                     expect_expr=EXCLUDED.expect_expr,
                     owner=EXCLUDED.owner""",
                (probe_id, clause_ref, DEADLINE, mk, rk, check_cmd, expect_expr, owner),
            )
    print(f"✓ 冪等 upsert {len(SEED_1014)} 條 deadline={DEADLINE}")
    return cmd_status()


def cmd_seed_doc() -> int:
    from augur.core import db
    with _conn() as conn, db.transaction(conn) as cur:
        for probe_id, clause_ref, owner, mk, rk, check_cmd in SEED_DOC:
            cur.execute(
                "SELECT 1 FROM measure_registry WHERE measure_key=%s AND ruler_key=%s",
                (mk, rk),
            )
            if not cur.fetchone():
                print(f"✗ 尺 {mk}/{rk} 未登錄——先 register_measure.py --register-defaults")
                return 1
            cur.execute(
                """INSERT INTO treaty_probe_binding
                     (probe_id, clause_ref, deadline, measure_key, ruler_key,
                      check_cmd, expect_expr, owner)
                   VALUES (%s,%s,NULL,%s,%s,%s,'undecidable',%s)
                   ON CONFLICT (probe_id) DO UPDATE SET
                     clause_ref=EXCLUDED.clause_ref,
                     measure_key=EXCLUDED.measure_key,
                     ruler_key=EXCLUDED.ruler_key,
                     check_cmd=EXCLUDED.check_cmd,
                     owner=EXCLUDED.owner""",
                (probe_id, clause_ref, mk, rk, check_cmd, owner),
            )
    print(f"✓ 冪等 upsert {len(SEED_DOC)} 條 doc 族（owner=AI、無 deadline）")
    return cmd_status()


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    ids = [p[0] for p in SEED_1014]
    chk("恰 ≥13 條種子", len(SEED_1014) >= 13)
    chk("probe_id 不撞", len(ids) == len(set(ids)))
    chk("全 Steward（禁 AI 代勾人裁框）", all(p[2] == "Steward" for p in SEED_1014))
    chk("expect 皆 undecidable", all(p[4] == "undecidable" for p in SEED_1014))
    chk("clause_ref 具 file:line", all(":" in p[1] and not p[1].endswith(":") for p in SEED_1014))
    missing = [p[1].split(":")[0] for p in SEED_1014 if not (ROOT / p[1].split(":")[0]).exists()]
    chk("clause 檔皆存在於 repo", missing == [])
    # —— doc 族（第 19 步）——
    doc_ids = [p[0] for p in SEED_DOC]
    chk("doc 族 ≥11 條且 id 不撞（含跨 1014 族）",
        len(SEED_DOC) >= 11 and len(set(ids + doc_ids)) == len(ids) + len(doc_ids))
    chk("doc 族全 owner=AI（機讀快照）", all(p[2] == "AI" for p in SEED_DOC))
    chk("doc 族 clause_ref 具 file:line",
        all(":" in p[1] and not p[1].endswith(":") for p in SEED_DOC))
    chk("doc 族 check_cmd 非空", all(p[5].strip() for p in SEED_DOC))
    doc_missing = [p[1].split(":")[0] for p in SEED_DOC
                   if not (ROOT / p[1].split(":")[0]).exists()]
    chk("doc 族 clause 檔皆存在於 repo", doc_missing == [])
    print("自測：" + ("全通過 ✓" if ok else "失敗 ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--status", action="store_true")
    p.add_argument("--seed-1014", action="store_true")
    p.add_argument("--seed-doc", action="store_true")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.seed_1014:
        return cmd_seed()
    if args.seed_doc:
        return cmd_seed_doc()
    if args.status or len(sys.argv) <= 1:
        if len(sys.argv) <= 1:
            print(__doc__)
        return cmd_status()
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
