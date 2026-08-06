#!/usr/bin/env python
"""建 knowhow_answer_lift_log — KH0 答對自動抬層帳（R-hybrid／AUTO-LIFT）。

🎯 這支在做什麼(白話):顧問答對核可後自動抬 admit 至 KH1／KH2 之**留痕表**；
   不存來源 approve；不掛交易。
守 #6 冪等· #15 誠實· FZ-keep· no-source-approve-by-AI。

執行指令矩陣:
  python scripts/migrate_kh0_answer_lift_log_ddl.py            # 預設 check
  python scripts/migrate_kh0_answer_lift_log_ddl.py --check
  python scripts/migrate_kh0_answer_lift_log_ddl.py --apply
  python scripts/migrate_kh0_answer_lift_log_ddl.py --selftest
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401

TABLE = "knowhow_answer_lift_log"

DDL = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
  lift_id       BIGSERIAL PRIMARY KEY,
  query_hash    TEXT NOT NULL,
  ruler         TEXT NOT NULL
                CHECK (ruler IN ('R-cite','R-human','R-hybrid','R-judge')),
  cite_pass     BOOLEAN NOT NULL,
  human_pass    BOOLEAN NOT NULL DEFAULT false,
  lifted        BOOLEAN NOT NULL DEFAULT false,
  item_ids      BIGINT[] NOT NULL DEFAULT '{{}}',
  depths_before JSONB NOT NULL DEFAULT '{{}}'::jsonb,
  depths_after  JSONB NOT NULL DEFAULT '{{}}'::jsonb,
  note          TEXT NOT NULL DEFAULT '',
  actor         TEXT NOT NULL DEFAULT 'system:kh0_answer_auto_lift',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_kh0_lift_created
  ON {TABLE} (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_kh0_lift_query
  ON {TABLE} (query_hash, created_at DESC);
COMMENT ON TABLE {TABLE} IS
  'KH0 AUTO-LIFT: 答對核可→admit 抬層留痕（≠source approve／≠tradable）';
"""


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("表名", TABLE in DDL)
    for r in ("R-cite", "R-human", "R-hybrid", "R-judge"):
        chk(f"ruler {r}", f"'{r}'" in DDL)
    cols = DDL.split("COMMENT", 1)[0].lower()
    chk("無 approval_status", "approval_status" not in cols)
    chk("無 activate 欄", "activate" not in cols)
    chk("指令矩陣", "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{TABLE}",))
        exists = bool(cur.fetchone()[0])
        print(f"  {TABLE}: {'yes' if exists else 'NO'}")
        if exists:
            cur.execute(f"SELECT count(*) FROM {TABLE}")
            print(f"  rows: {cur.fetchone()[0]}")
    return 0


def apply_ddl() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(DDL)
        conn.commit()
    print(f"  applied {TABLE}")
    return check_live()


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.apply:
        return apply_ddl()
    print(__doc__)
    return check_live()


if __name__ == "__main__":
    sys.exit(main())
