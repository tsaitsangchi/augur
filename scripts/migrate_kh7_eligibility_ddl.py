#!/usr/bin/env python
"""建 knowhow_kh7_eligibility 表 — KH7-S1。

🎯 這支在做什麼(白話):對抗可答性帳本 DDL（pass／fail／human_review 閉集）。
   非答案 SSOT；不改 approval_status／answer_status；零市場 API。
守 #6(冪等)· #29a/d· HUMAN-APPROVE-keep· FZ-keep。

執行指令矩陣:
  python scripts/migrate_kh7_eligibility_ddl.py              # 安全預設:印矩陣+--check
  python scripts/migrate_kh7_eligibility_ddl.py --check      # 唯讀現況
  python scripts/migrate_kh7_eligibility_ddl.py --apply      # 冪等建表
  python scripts/migrate_kh7_eligibility_ddl.py --selftest   # 零 DB 紅綠
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401

DDL = """
CREATE TABLE IF NOT EXISTS knowhow_kh7_eligibility (
  eligibility_id   BIGSERIAL PRIMARY KEY,
  run_id           BIGINT REFERENCES knowhow_interaction_probe_run(run_id) ON DELETE SET NULL,
  probe_id         TEXT NOT NULL,
  status           TEXT NOT NULL
                   CHECK (status IN (
                     'unchecked','eligibility_pass','eligibility_fail',
                     'contradiction_found','needs_human_review')),
  reasons          JSONB NOT NULL DEFAULT '[]'::jsonb,
  evidence         JSONB NOT NULL DEFAULT '{}'::jsonb,
  decided_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  script           TEXT NOT NULL DEFAULT 'run_kh7_eligibility.py',
  note             TEXT
);
CREATE INDEX IF NOT EXISTS idx_kh7_elig_probe_time
  ON knowhow_kh7_eligibility (probe_id, decided_at DESC);
COMMENT ON TABLE knowhow_kh7_eligibility IS
  'KH7-S1: 探針對抗可答性帳本（非答案 SSOT；不改 approval_status）';
"""


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 建 knowhow_kh7_eligibility", "knowhow_kh7_eligibility" in DDL)
    for s in (
        "unchecked",
        "eligibility_pass",
        "eligibility_fail",
        "contradiction_found",
        "needs_human_review",
    ):
        chk(f"閉集含 {s}", f"'{s}'" in DDL)
    chk("禁 approve 欄", "approval_status" not in DDL and "approve" not in DDL)
    chk("禁 activate", "activate" not in DDL)
    chk("指令矩陣含 --apply/--selftest",
        "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.knowhow_kh7_eligibility')")
        exists = bool(cur.fetchone()[0])
        print(f"knowhow_kh7_eligibility={'已在' if exists else '缺'}")
        if not exists:
            return 1
        cur.execute("SELECT count(*) FROM knowhow_kh7_eligibility")
        n = cur.fetchone()[0]
        cur.execute(
            "SELECT status, count(*) FROM knowhow_kh7_eligibility GROUP BY 1 ORDER BY 1"
        )
        buckets = cur.fetchall()
        print(f"rows={n}")
        if buckets:
            print("buckets=" + ", ".join(f"{k}:{c}" for k, c in buckets))
    return 0


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="KH7 eligibility DDL")
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
        # run 表可能尚未建——先確保 FK 目標存在（runner ledger DDL 冪等）
        cur.execute("SELECT to_regclass('public.knowhow_interaction_probe_run')")
        if not cur.fetchone()[0]:
            # 最小 run 表骨架（與 run_knowhow_interaction_probes.LEDGER_DDL 對齊）
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS knowhow_interaction_probe_run (
                    run_id        BIGSERIAL PRIMARY KEY,
                    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
                    finished_at   TIMESTAMPTZ,
                    script        TEXT NOT NULL DEFAULT 'run_knowhow_interaction_probes.py',
                    git_sha       TEXT,
                    note          TEXT,
                    params_json   JSONB NOT NULL DEFAULT '{}'::jsonb
                )
                """
            )
        cur.execute(DDL)
        conn.commit()
    print("  ✓ KH7 eligibility DDL 冪等完成")
    return check_live()


if __name__ == "__main__":
    sys.exit(main())
