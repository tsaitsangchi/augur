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
    print("自測：" + ("全通過 ✓" if ok else "失敗 ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--status", action="store_true")
    p.add_argument("--seed-1014", action="store_true")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.seed_1014:
        return cmd_seed()
    if args.status or len(sys.argv) <= 1:
        if len(sys.argv) <= 1:
            print(__doc__)
        return cmd_status()
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
