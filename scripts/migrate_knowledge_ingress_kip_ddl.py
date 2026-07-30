#!/usr/bin/env python
"""建 knowledge_ingress_kip_run — LSR-INGRESS-S0。

🎯 這支在做什麼(白話):三通道強制入庫管線(KIP)跑批帳本 DDL；記錄 channel／
   trigger／item_ids／各段 stages_json／終態。非答案 SSOT、非預測特徵。
守 #6(冪等)· #15· #29a/d· FZ-keep· LSR-INGRESS-PLAN。

執行指令矩陣:
  python scripts/migrate_knowledge_ingress_kip_ddl.py              # 安全預設:印矩陣+--check
  python scripts/migrate_knowledge_ingress_kip_ddl.py --check
  python scripts/migrate_knowledge_ingress_kip_ddl.py --apply
  python scripts/migrate_knowledge_ingress_kip_ddl.py --selftest
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401

DDL = """
CREATE TABLE IF NOT EXISTS knowledge_ingress_kip_run (
    kip_run_id     BIGSERIAL PRIMARY KEY,
    channel        TEXT NOT NULL
                   CHECK (channel IN (
                     'topic_harvest','local_files','sftp','manual_cli','backfill')),
    trigger_ref    TEXT,
    item_ids       BIGINT[] NOT NULL DEFAULT '{}',
    status         TEXT NOT NULL DEFAULT 'pending'
                   CHECK (status IN (
                     'pending','running','done','partial','failed','skipped_explicit')),
    stages_json    JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_text     TEXT,
    actor          TEXT NOT NULL DEFAULT 'system',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at    TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_kip_run_channel_time
  ON knowledge_ingress_kip_run (channel, created_at DESC);
COMMENT ON TABLE knowledge_ingress_kip_run IS
  'KIP: 三通道入庫強制管線跑批帳（#15；非答案 SSOT／非預測）';
"""


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 含 kip_run 表", "knowledge_ingress_kip_run" in DDL)
    chk("channel 含三通道", all(
        c in DDL for c in ("topic_harvest", "local_files", "sftp")))
    chk("status 含 done/partial", "done" in DDL and "partial" in DDL)
    chk("有 stages_json", "stages_json" in DDL)
    chk("指令矩陣", "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    chk("FZ-keep 標頭", "FZ-keep" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.knowledge_ingress_kip_run')")
        exists = bool(cur.fetchone()[0])
        print(f"knowledge_ingress_kip_run={'已在' if exists else '缺'}")
        if not exists:
            return 1
        cur.execute("SELECT count(*) FROM knowledge_ingress_kip_run")
        print(f"rows={cur.fetchone()[0]}")
        cur.execute(
            """
            SELECT channel, status, count(*)
            FROM knowledge_ingress_kip_run
            GROUP BY 1, 2 ORDER BY 1, 2
            """
        )
        rows = cur.fetchall()
        if rows:
            print("by_channel_status=", rows)
    return 0


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="LSR-INGRESS kip_run DDL")
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
    print("  ✓ kip_run DDL 冪等完成")
    return check_live()


if __name__ == "__main__":
    sys.exit(main())
