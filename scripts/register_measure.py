#!/usr/bin/env python3
"""🎯 登錄一把尺進 `measure_registry`——「引用數字必附口徑」之寫入口（M-N2）。

本支只 INSERT／UPSERT `(measure_key, ruler_key)`；**不代標 `authoritative`**（標權威必具名＝
Steward；AI 預設 `authoritative=false`）。設計 SSOT＝
`reports/augur_optimization_master_plan_20260803.md` 第 20 步／附(a)。

守原則 #6（寫入須明示旗標）#12（口徑住表不手抄）#15 #29a/d。

執行指令矩陣
------------
    python3 scripts/register_measure.py                         # 無參數＝印矩陣＋--list
    python3 scripts/register_measure.py --list                   # 唯讀：已登錄尺
    python3 scripts/register_measure.py --check                  # 唯讀：每 measure_key 權威計數（0＝報而不擋）
    python3 scripts/register_measure.py --register-defaults      # 登錄 M-N1 基線尺（冪等；authoritative=false）
    python3 scripts/register_measure.py --register KEY RULER \\
        --definition '...' --repro-cmd '...'                    # 登錄一把尺
    python3 scripts/register_measure.py --selftest               # 免 DB 免 API
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

# (measure_key, ruler_key, definition, repro_cmd)——基線尺；權威標定另案 Steward
DEFAULTS = [
    (
        "treaty_1014_probe",
        "line_snapshot",
        "2026-10-14 併結／同綁項之現場快照（勾選狀態或機械計數字串）；結清可否由 Steward 裁，"
        "本尺只承載可重跑之觀測字串。",
        "python3 scripts/read_treaty_probes.py --check",
    ),
    (
        "public_table_count",
        "relkind_r",
        "public schema 之 base table 數（pg_class.relkind='r'；不含分區父表視角之第二把尺）。",
        "psql -d augur -Atc \"SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
        "WHERE n.nspname='public' AND c.relkind='r'\"",
    ),
    (
        "script_entry_count",
        "cmd_matrix_scope",
        "check_cmd_matrix 受檢入口數（含 scripts/ 外之 __main__；非 ls scripts/*.py）。",
        "python3 scripts/check_cmd_matrix.py 2>/dev/null | tail -3",
    ),
    # —— doc 族（M-N1 第 19 步：文件硬編數字→探針）之尺；權威標定仍 Steward ——
    (
        "crontab_entries",
        "grep_leading_numeric",
        "使用者 crontab 之排程行數（行首為數字或 * 者；不含註解與環境變數行）。",
        "crontab -l | grep -c '^[0-9*]'",
    ),
    (
        "deferred_work_uncleared",
        "sql_cleared_at_null",
        "evolution_deferred_work 未清件數（cleared_at IS NULL）。",
        "venv/bin/python -c 'from augur.core import config; import psycopg2; conn=psycopg2.connect(**config.DB_PARAMS); cur=conn.cursor(); "
        "cur.execute(\"SELECT count(*) FROM evolution_deferred_work WHERE cleared_at IS NULL\"); "
        "print(cur.fetchone()[0])'",
    ),
    (
        "validation_evidence_status",
        "sql_group_by_status",
        "validation_evidence 全表列數與 green/red/unverified 分布（status GROUP BY；"
        "verify_validation_evidence.py 同口徑）。",
        "venv/bin/python -c 'from augur.core import config; import psycopg2; conn=psycopg2.connect(**config.DB_PARAMS); cur=conn.cursor(); "
        "cur.execute(\"SELECT status, count(*) FROM validation_evidence GROUP BY 1\"); "
        "d=dict(cur.fetchall()); print(\"total=%d green=%d red=%d unverified=%d\" % "
        "(sum(d.values()), d.get(\"green\",0), d.get(\"red\",0), d.get(\"unverified\",0)))'",
    ),
    (
        "lint_total_errors",
        "report_json",
        "constitution_lint report 機器區塊之 total_errors（github-workflow.yml 檔頭同源數）。",
        "venv/bin/python -m tools.constitution_lint report 2>/dev/null | "
        "grep -oE '\"total_errors\": [0-9]+' | grep -oE '[0-9]+$'",
    ),
    (
        "lint_selftest_status",
        "rc_pass_fail",
        "constitution_lint --selftest 之 rc 化約（PASS/FAIL；取代文件手抄「selftest 現為全綠」類現況句）。",
        "venv/bin/python -m tools.constitution_lint --selftest >/dev/null 2>&1 && echo PASS || echo FAIL",
    ),
    (
        "wm36_registry_tables",
        "pg_class_concept_like",
        "public 內 relname LIKE '%concept%' 之 base table 數（F2 §1「Registry 表本體」同尺現查；"
        "是否達 WM.36 七欄要件另屬 Steward 裁決域）。",
        "venv/bin/python -c 'from augur.core import config; import psycopg2; conn=psycopg2.connect(**config.DB_PARAMS); cur=conn.cursor(); "
        "cur.execute(\"SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
        "WHERE n.nspname=%s AND c.relname LIKE %s AND c.relkind=%s\", (\"public\",\"%concept%\",\"r\")); "
        "print(cur.fetchone()[0])'",
    ),
    (
        "vendor_direct_bind",
        "grep_from_taiwan_src_scripts",
        "src+scripts 內含 FROM \"Taiwan 直綁之 .py 檔數（GROUNDING-MAP 同尺；"
        "權威尺選定＝M-N7 未裁，本尺 authoritative=false）。",
        "grep -rlE 'FROM\\s+\"Taiwan' src scripts --include='*.py' | wc -l",
    ),
    (
        "pg_memory_settings",
        "show_three",
        "live PostgreSQL shared_buffers／work_mem／maintenance_work_mem 三值快照（機器漂移偵測）。",
        "venv/bin/python -c 'from augur.core import config; import psycopg2; conn=psycopg2.connect(**config.DB_PARAMS); cur=conn.cursor(); "
        "cur.execute(\"SHOW shared_buffers\"); a=cur.fetchone()[0]; "
        "cur.execute(\"SHOW work_mem\"); b=cur.fetchone()[0]; "
        "cur.execute(\"SHOW maintenance_work_mem\"); c=cur.fetchone()[0]; "
        "print(\"shared_buffers=\"+a+\" work_mem=\"+b+\" maintenance_work_mem=\"+c)'",
    ),
]


def _conn():
    from augur.core import db
    return db.connect()


def cmd_list() -> int:
    with _conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.measure_registry')")
        if cur.fetchone()[0] is None:
            print("✗ measure_registry 不在——先跑 migrate_measure_registry_ddl.py --apply")
            return 1
        cur.execute(
            "SELECT measure_key, ruler_key, authoritative, authoritative_by, "
            "left(definition,60) FROM measure_registry ORDER BY 1,2"
        )
        rows = cur.fetchall()
        if not rows:
            print("（空——--register-defaults 或 --register）")
            return 0
        for r in rows:
            auth = f"auth={r[2]}" + (f" by={r[3]}" if r[3] else "")
            print(f"  {r[0]} / {r[1]}  [{auth}]  {r[4]}…")
        print(f"共 {len(rows)} 列")
    return 0


def cmd_check() -> int:
    with _conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.measure_registry')")
        if cur.fetchone()[0] is None:
            print("✗ 表不在")
            return 1
        cur.execute(
            """SELECT measure_key,
                      count(*) FILTER (WHERE authoritative) AS n_auth,
                      count(*) AS n_rulers
               FROM measure_registry GROUP BY 1 ORDER BY 1"""
        )
        bad = 0
        for mk, n_auth, n_r in cur.fetchall():
            tag = "ok" if n_auth == 1 else ("no_authoritative" if n_auth == 0 else "multi_authoritative")
            if tag != "ok":
                bad += 1
            print(f"  {mk}: rulers={n_r} authoritative={n_auth} → {tag}")
        if bad:
            print(f"⚠ {bad} 組尚無恰 1 把權威（報而不擋；標定屬 Steward）")
        return 0


def _upsert(cur, measure_key, ruler_key, definition, repro_cmd) -> None:
    cur.execute(
        """INSERT INTO measure_registry (measure_key, ruler_key, definition, repro_cmd)
           VALUES (%s,%s,%s,%s)
           ON CONFLICT (measure_key, ruler_key) DO UPDATE
             SET definition = EXCLUDED.definition,
                 repro_cmd  = EXCLUDED.repro_cmd
           WHERE measure_registry.authoritative IS FALSE""",
        (measure_key, ruler_key, definition, repro_cmd),
    )


def cmd_register(args) -> int:
    if not args.definition or not args.repro_cmd:
        print("✗ --register 須同時給 --definition 與 --repro-cmd")
        return 2
    if args.authoritative:
        print("✗ 本支拒代標 authoritative（須 Steward 另路徑具名；見 never-type-human-signature）")
        return 2
    from augur.core import db
    with _conn() as conn, db.transaction(conn) as cur:
        _upsert(cur, args.register[0], args.register[1], args.definition, args.repro_cmd)
    print(f"✓ 登錄 {args.register[0]} / {args.register[1]}（authoritative=false）")
    return 0


def cmd_defaults() -> int:
    from augur.core import db
    with _conn() as conn, db.transaction(conn) as cur:
        for row in DEFAULTS:
            _upsert(cur, *row)
    print(f"✓ 基線尺 {len(DEFAULTS)} 把就緒（authoritative=false；標權威另裁）")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    keys = {(m, r) for m, r, *_ in DEFAULTS}
    chk("defaults 非空且鍵不撞", len(DEFAULTS) >= 1 and len(keys) == len(DEFAULTS))
    chk("每把尺 definition/repro 非空", all(d.strip() and c.strip() for *_, d, c in DEFAULTS))
    chk("含 treaty_1014 基線尺", ("treaty_1014_probe", "line_snapshot") in keys)
    # #35：餵真 args 驗拒代標；不掃含自測字串之 haystack
    class _AuthArgs:
        register = ("x", "y")
        definition = "d"
        repro_cmd = "c"
        authoritative = True
    import io
    from contextlib import redirect_stdout
    _buf = io.StringIO()
    with redirect_stdout(_buf):
        _rc = cmd_register(_AuthArgs())
    chk("拒代標 authoritative（rc=2 且訊息）",
        _rc == 2 and "拒代標" in _buf.getvalue())
    # 矩陣旗標在 docstring／本體（切掉 _selftest 段，免字面恆真）
    body = open(__file__, encoding="utf-8").read().split("def _selftest")[0]
    chk("執行指令矩陣含 --selftest／--register-defaults",
        "--selftest" in body and "--register-defaults" in body)
    print("自測：" + ("全通過 ✓" if ok else "失敗 ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--list", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--register-defaults", action="store_true")
    p.add_argument("--register", nargs=2, metavar=("MEASURE", "RULER"))
    p.add_argument("--definition")
    p.add_argument("--repro-cmd")
    p.add_argument("--authoritative", action="store_true",
                   help="（拒收）保留旗標以免誤用；本支永遠拒絕")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.register_defaults:
        return cmd_defaults()
    if args.register:
        return cmd_register(args)
    if args.check:
        return cmd_check()
    if args.list or len(sys.argv) <= 1:
        if len(sys.argv) <= 1:
            print(__doc__)
        return cmd_list()
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
