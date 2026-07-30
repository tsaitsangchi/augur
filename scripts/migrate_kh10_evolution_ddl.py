#!/usr/bin/env python
"""建 KH10 Evolution & Governance 三表 — KH10-ENABLE-S0。

🎯 這支在做什麼(白話):冪等建立進化候選佇列、治理裁決帳本、回饋閉環帳本。
   只 DDL／空表；不收 candidate、不人裁、不 APPLY、不寫 philosophy。
守 #6(冪等)· #29a/d(指令矩陣)· HUMAN_ONLY· FZ-keep。
   計畫 SSOT＝reports/augur_kh10_enable_plan_20260729.md §3／§6-S0。

執行指令矩陣:
  python scripts/migrate_kh10_evolution_ddl.py              # 安全預設:印矩陣+--check
  python scripts/migrate_kh10_evolution_ddl.py --check      # 唯讀現況
  python scripts/migrate_kh10_evolution_ddl.py --apply      # 冪等建 3 表
  python scripts/migrate_kh10_evolution_ddl.py --selftest   # 零 DB 紅綠
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401

TABLES = (
    "knowhow_evolution_candidate",
    "knowhow_governance_ledger",
    "knowhow_evolution_feedback",
)

DDL = """
CREATE TABLE IF NOT EXISTS knowhow_evolution_candidate (
    candidate_id     BIGSERIAL PRIMARY KEY,
    source_type      TEXT NOT NULL
                     CHECK (source_type IN (
                       'kh9_synthesis','kh6_probe','pme_xdom_map',
                       'manual','kh7_contradiction')),
    source_ref       TEXT NOT NULL,
    hypothesis_text  TEXT NOT NULL,
    target_domain    TEXT NOT NULL DEFAULT 'investment',
    axes_json        JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_score   REAL,
    status           TEXT NOT NULL DEFAULT 'candidate_for_evolution'
                     CHECK (status IN (
                       'candidate_for_evolution',
                       'governance_pending',
                       'approved_for_loop',
                       'rejected_for_loop',
                       'superseded')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    note             TEXT
);
CREATE INDEX IF NOT EXISTS idx_evo_cand_status
  ON knowhow_evolution_candidate (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_evo_cand_source
  ON knowhow_evolution_candidate (source_type, source_ref);
COMMENT ON TABLE knowhow_evolution_candidate IS
  'KH10-S0: 進化候選佇列（系統可 propose；approve/APPLY 唯人；≠prodset）';

CREATE TABLE IF NOT EXISTS knowhow_governance_ledger (
    ledger_id        BIGSERIAL PRIMARY KEY,
    candidate_id     BIGINT NOT NULL REFERENCES knowhow_evolution_candidate(candidate_id),
    decision         TEXT NOT NULL
                     CHECK (decision IN (
                       'approved','rejected','deferred','superseded','killed')),
    decided_by       TEXT NOT NULL DEFAULT 'HUMAN',
    rationale        TEXT,
    downstream_ref   TEXT,
    decided_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_gov_ledger_cand
  ON knowhow_governance_ledger (candidate_id, decided_at DESC);
COMMENT ON TABLE knowhow_governance_ledger IS
  'KH10-S0: 治理裁決帳本（decided_by 預設 HUMAN；AI 只 propose）';

CREATE TABLE IF NOT EXISTS knowhow_evolution_feedback (
    feedback_id      BIGSERIAL PRIMARY KEY,
    ledger_id        BIGINT NOT NULL REFERENCES knowhow_governance_ledger(ledger_id),
    feedback_type    TEXT NOT NULL
                     CHECK (feedback_type IN (
                       'eval_set_update','weight_tune','probe_retire',
                       'replay_annotation','kill_propagation')),
    payload_json     JSONB NOT NULL DEFAULT '{}'::jsonb,
    applied_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    script           TEXT NOT NULL DEFAULT 'apply_evolution_feedback.py'
);
COMMENT ON TABLE knowhow_evolution_feedback IS
  'KH10-S0: 回饋閉環帳本（接 ledger；S2 才寫）';
"""


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    for t in TABLES:
        chk(f"DDL 含 {t}", t in DDL)
    for s in (
        "candidate_for_evolution",
        "governance_pending",
        "approved_for_loop",
        "rejected_for_loop",
        "superseded",
    ):
        chk(f"status 閉集含 {s}", f"'{s}'" in DDL)
    for d in ("approved", "rejected", "deferred", "superseded", "killed"):
        chk(f"decision 閉集含 {d}", f"'{d}'" in DDL)
    chk("decided_by 預設 HUMAN", "DEFAULT 'HUMAN'" in DDL)
    chk("禁 auto_apply 欄", "auto_apply" not in DDL.lower())
    chk("禁 FinMind/FRED", "finmind" not in DDL.lower() and "fred" not in DDL.lower())
    chk("指令矩陣含 --apply/--selftest",
        "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    missing = []
    with db.connect() as conn, conn.cursor() as cur:
        for t in TABLES:
            cur.execute("SELECT to_regclass(%s)", (f"public.{t}",))
            exists = bool(cur.fetchone()[0])
            if not exists:
                missing.append(t)
                print(f"{t}=缺")
                continue
            cur.execute(f"SELECT count(*) FROM {t}")  # noqa: S608 — 表名閉集
            n = cur.fetchone()[0]
            print(f"{t}=已在 rows={n}")
        if not missing and "knowhow_evolution_candidate" not in missing:
            cur.execute(
                """
                SELECT conname, pg_get_constraintdef(oid)
                FROM pg_constraint
                WHERE conrelid = 'knowhow_evolution_candidate'::regclass
                  AND contype = 'c'
                ORDER BY 1
                """
            )
            for name, defn in cur.fetchall():
                print(f"  CHECK {name}: {defn}")
    return 1 if missing else 0


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="KH10 evolution DDL (S0)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.check:
        return check_live()

    from augur.core import db

    if not args.apply:
        print(__doc__)
        print("(唯讀；--apply 才套用)")
        return check_live()

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(DDL)
        conn.commit()
    print("  ✓ KH10 evolution DDL 冪等完成（3 表）")
    return check_live()


if __name__ == "__main__":
    sys.exit(main())
