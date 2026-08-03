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
