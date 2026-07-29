#!/usr/bin/env python
"""建 knowhow_eval_suite_case＋decline 探針種子 — KNI-S3。

🎯 這支在做什麼(白話):固定評測題組住 DB（四 case：full／兩消融／expect_decline），
   並冪等 upsert 無意義軸探針 `KNI-EVAL-EMPTY-CORPUS`（供 decline 機械斷言）。
   策展列≠答案樹 SSOT；runner／eval 讀表；零 FinMind／FRED；不碰 approve。
守 #29b(策展住 DB)· #6(冪等)· #29a/d· NHC-keep· FZ-keep· HUMAN-APPROVE-keep。

執行指令矩陣:
  python scripts/migrate_knowhow_eval_suite_ddl.py              # 安全預設:印矩陣+--check
  python scripts/migrate_knowhow_eval_suite_ddl.py --check      # 唯讀現況
  python scripts/migrate_knowhow_eval_suite_ddl.py --apply      # 冪等建表+種子
  python scripts/migrate_knowhow_eval_suite_ddl.py --show       # 列 active cases
  python scripts/migrate_knowhow_eval_suite_ddl.py --selftest   # 零 DB 紅綠
"""
from __future__ import annotations

import json
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS knowhow_eval_suite_case (
  case_id          TEXT PRIMARY KEY,
  probe_id         TEXT NOT NULL REFERENCES knowhow_interaction_probe(probe_id),
  role             TEXT NOT NULL,
  expect_json      JSONB NOT NULL DEFAULT '{}'::jsonb,
  active           BOOLEAN NOT NULL DEFAULT true,
  note             TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_knowhow_eval_suite_active
  ON knowhow_eval_suite_case (active, role)
  WHERE active;
COMMENT ON TABLE knowhow_eval_suite_case IS
  'KNI-S3: 固定評測題組（策展列；禁答案樹 SSOT）';
"""

DECLINE_PROBE_ID = "KNI-EVAL-EMPTY-CORPUS"
PROVENANCE = "steward_seed_kni_s3_20260729"

# 無意義軸：期望檢索無命中 → no_corpus／eligibility_fail（非答案樹）
DECLINE_PROBE = {
    "probe_id": DECLINE_PROBE_ID,
    "prompt_template": (
        "「{{axis_a}}」與「{{axis_b}}」之交互？（評測用無意義軸；"
        "期望缺料 decline；禁寫死專答）"
    ),
    "knowhow_axis": "ZZZZ-NONEXISTENT-AXIS-ALPHA-KNI-EVAL",
    "raw_axis": "ZZZZ-NONEXISTENT-AXIS-BETA-KNI-EVAL",
    "expected_family": "eval_decline",
    "interaction_kind": "kh_x_kh",
    "template_params": {
        "axis_a": "ZZZZ-NONEXISTENT-AXIS-ALPHA-KNI-EVAL",
        "axis_b": "ZZZZ-NONEXISTENT-AXIS-BETA-KNI-EVAL",
    },
    "arity": 2,
    "axes": [
        {"role": "axis_a", "label": "ZZZZ-NONEXISTENT-AXIS-ALPHA-KNI-EVAL"},
        {"role": "axis_b", "label": "ZZZZ-NONEXISTENT-AXIS-BETA-KNI-EVAL"},
    ],
    "note": (
        "KNI-S3 expect_decline；無意義軸＋eval null-corpus fixture"
        "（empty ranked→no_corpus；非答案樹）"
    ),
}

# (case_id, probe_id, role, expect_json, note)
SEED_CASES = (
    (
        "KNI-S3-FULL-FP-AI-SOLAR",
        "RKI-FP-AI-SOLAR",
        "full_triple",
        {},
        "三元 full；消融對照基準臂",
    ),
    (
        "KNI-S3-ABL-NO-FP",
        "RKI-AI-SOLAR-RD",
        "ablation_no_principle",
        {},
        "消融：缺第一性軸",
    ),
    (
        "KNI-S3-ABL-NO-AI",
        "RKI-FP-SOLAR-CORE",
        "ablation_no_ai",
        {},
        "消融：缺 AI 軸",
    ),
    (
        "KNI-S3-EXPECT-DECLINE",
        DECLINE_PROBE_ID,
        "expect_decline",
        {"gap_contains": "no_corpus", "or_kh7": "eligibility_fail"},
        "機械期望 no_corpus∈gap 或 KH7=eligibility_fail",
    ),
)


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 建 knowhow_eval_suite_case", "knowhow_eval_suite_case" in DDL)
    chk("種子四 case", len(SEED_CASES) == 4)
    roles = {c[2] for c in SEED_CASES}
    chk("角色齊（full/abl/decline）",
        roles == {"full_triple", "ablation_no_principle", "ablation_no_ai", "expect_decline"})
    chk("decline probe 種子", DECLINE_PROBE["probe_id"] == DECLINE_PROBE_ID)
    chk("無意義軸字樣", "ZZZZ-NONEXISTENT" in DECLINE_PROBE["knowhow_axis"])
    chk("approve/activate 未入", "approve" not in DDL.lower() and "activate" not in DDL.lower())
    chk("指令矩陣含 --apply/--selftest",
        "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _upsert_decline_probe(cur) -> None:
    p = DECLINE_PROBE
    cur.execute(
        """
        INSERT INTO knowhow_interaction_probe (
          probe_id, prompt_template, knowhow_axis, raw_axis, expected_family,
          interaction_kind, template_params, arity, axes, active, provenance, note
        ) VALUES (
          %s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb,true,%s,%s
        )
        ON CONFLICT (probe_id) DO UPDATE SET
          prompt_template = EXCLUDED.prompt_template,
          knowhow_axis = EXCLUDED.knowhow_axis,
          raw_axis = EXCLUDED.raw_axis,
          expected_family = EXCLUDED.expected_family,
          interaction_kind = EXCLUDED.interaction_kind,
          template_params = EXCLUDED.template_params,
          arity = EXCLUDED.arity,
          axes = EXCLUDED.axes,
          active = true,
          provenance = EXCLUDED.provenance,
          note = EXCLUDED.note,
          updated_at = now()
        """,
        (
            p["probe_id"],
            p["prompt_template"],
            p["knowhow_axis"],
            p["raw_axis"],
            p["expected_family"],
            p["interaction_kind"],
            json.dumps(p["template_params"], ensure_ascii=False),
            p["arity"],
            json.dumps(p["axes"], ensure_ascii=False),
            PROVENANCE,
            p["note"],
        ),
    )
    print(f"  decline probe upsert: {p['probe_id']}")


def _upsert_cases(cur) -> None:
    for case_id, probe_id, role, expect_json, note in SEED_CASES:
        cur.execute(
            """
            INSERT INTO knowhow_eval_suite_case
              (case_id, probe_id, role, expect_json, active, note)
            VALUES (%s,%s,%s,%s::jsonb,true,%s)
            ON CONFLICT (case_id) DO UPDATE SET
              probe_id = EXCLUDED.probe_id,
              role = EXCLUDED.role,
              expect_json = EXCLUDED.expect_json,
              active = true,
              note = EXCLUDED.note
            """,
            (
                case_id,
                probe_id,
                role,
                json.dumps(expect_json, ensure_ascii=False),
                note,
            ),
        )
    print(f"  eval cases upsert: {len(SEED_CASES)}")


def check(conn) -> int:
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_interaction_probe')")
        if not cur.fetchone()[0]:
            print("  knowhow_interaction_probe: 未建")
            return 1
        cur.execute("SELECT to_regclass('knowhow_eval_suite_case')")
        exists = bool(cur.fetchone()[0])
        print(f"  knowhow_eval_suite_case: {'已建' if exists else '未建'}")
        if not exists:
            return 1
        cur.execute(
            "SELECT count(*) FROM knowhow_interaction_probe WHERE probe_id=%s AND active",
            (DECLINE_PROBE_ID,),
        )
        decline_ok = cur.fetchone()[0] == 1
        print(f"  decline probe active: {decline_ok}")
        cur.execute(
            "SELECT case_id FROM knowhow_eval_suite_case WHERE active ORDER BY 1"
        )
        present = {r[0] for r in cur.fetchall()}
        want = {c[0] for c in SEED_CASES}
        missing = sorted(want - present)
        print(f"  active cases: {len(present)} (目標 {len(want)})")
        if missing:
            print(f"  missing={missing}")
        return 0 if decline_ok and not missing else 1


def show(conn) -> int:
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_eval_suite_case')")
        if not cur.fetchone()[0]:
            print("knowhow_eval_suite_case 未建")
            return 1
        cur.execute(
            "SELECT case_id, probe_id, role, active, note "
            "FROM knowhow_eval_suite_case ORDER BY case_id"
        )
        rows = cur.fetchall()
    print(f"── knowhow_eval_suite_case:{len(rows)} ──")
    for case_id, probe_id, role, active, note in rows:
        flag = "" if active else " [inactive]"
        print(f"  {case_id} → {probe_id} [{role}]{flag}")
        if note:
            print(f"    note: {note[:80]}")
    return 0


def apply(conn) -> int:
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_interaction_probe')")
        if not cur.fetchone()[0]:
            print("knowhow_interaction_probe 未建——先跑 migrate_knowhow_interaction_probe_ddl.py --apply")
            return 1
        _upsert_decline_probe(cur)
        cur.execute(DDL)
        _upsert_cases(cur)
    print("  ✓ KNI-S3 eval suite DDL 冪等完成")
    return check(conn)


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--selftest" in args:
        return selftest()

    do_apply = "--apply" in args
    do_show = "--show" in args
    do_check = "--check" in args or (not do_apply and not do_show)

    if not any((do_apply, do_show, do_check, "--selftest" in args)):
        print(__doc__)
        do_check = True

    with db.connect() as conn:
        if do_apply:
            return apply(conn)
        if do_show:
            return show(conn)
        return check(conn)


if __name__ == "__main__":
    sys.exit(main())
