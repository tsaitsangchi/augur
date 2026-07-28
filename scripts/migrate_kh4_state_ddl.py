#!/usr/bin/env python
"""KH4 最小狀態表 DDL — knowledge_kh4_state。

🎯 這支在做什麼(白話):建立 KH4 最小 item 級狀態 SSOT，讓 local/topic/SFTP 匯入與
   answer gate 有共同狀態表可寫。此表只記最小四層狀態與一般回答資格，**不**做 approve/activate、
   **不**改治權 [N]、**不**碰市場 API。
守 #6(冪等 DDL)· #29a/d· KH4-ANSWER-ORCH 最小 slice· FZ-keep。

執行指令矩陣:
  python scripts/migrate_kh4_state_ddl.py
  python scripts/migrate_kh4_state_ddl.py --dry-run
  python scripts/migrate_kh4_state_ddl.py --apply
  python scripts/migrate_kh4_state_ddl.py --check
  python scripts/migrate_kh4_state_ddl.py --selftest
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

DDL = """
CREATE TABLE IF NOT EXISTS knowledge_kh4_state (
    item_id               integer PRIMARY KEY REFERENCES knowledge_item(item_id) ON DELETE CASCADE,
    source_key            varchar(64) REFERENCES knowledge_source(source_key),
    source_channel        varchar(16) NOT NULL CHECK (source_channel IN ('local','topic','sftp')),
    domain                varchar(64) NOT NULL,
    qualification_state   varchar(16) NOT NULL CHECK (qualification_state IN ('pending','passed','blocked')),
    kh_axis_state         varchar(16) NOT NULL CHECK (kh_axis_state IN ('pending','ready','blocked')),
    interaction_state     varchar(16) NOT NULL CHECK (interaction_state IN ('pending','ready','blocked')),
    answer_state          varchar(16) NOT NULL CHECK (answer_state IN ('provisional','eligible','blocked','ineligible')),
    answer_status         varchar(16) NOT NULL CHECK (answer_status IN ('provisional','eligible','blocked','ineligible')),
    status_reason         text NOT NULL,
    evidence              jsonb NOT NULL DEFAULT '{}'::jsonb,
    updated_at            timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_kh4_answer_status
  ON knowledge_kh4_state (answer_status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_kh4_source
  ON knowledge_kh4_state (source_key, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_kh4_domain
  ON knowledge_kh4_state (domain, answer_status);
"""


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 建 knowledge_kh4_state", "knowledge_kh4_state" in DDL)
    chk("source_channel 三路齊", all(x in DDL for x in ("'local'", "'topic'", "'sftp'")))
    chk("answer gate 四態齊", all(x in DDL for x in ("'provisional'", "'eligible'", "'blocked'", "'ineligible'")))
    chk("approve/activate 未入 DDL", "approve" not in DDL and "activate" not in DDL)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.knowledge_kh4_state')")
        exists = bool(cur.fetchone()[0])
        print(f"knowledge_kh4_state={'已在' if exists else '缺'}")
        if not exists:
            return 1
        cur.execute("SELECT count(*) FROM knowledge_kh4_state")
        rows = cur.fetchone()[0]
        cur.execute("SELECT answer_status, count(*) FROM knowledge_kh4_state GROUP BY 1 ORDER BY 1")
        buckets = cur.fetchall()
        print(f"rows={rows}")
        print("buckets=" + ", ".join(f"{k}:{n}" for k, n in buckets))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KH4 最小狀態表 DDL")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.check:
        return check_live()

    from augur.core import db

    apply = bool(args.apply) and not args.dry_run
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.knowledge_kh4_state')")
        exists = bool(cur.fetchone()[0])
        print(f"KH4 DDL 現況: knowledge_kh4_state {'已在' if exists else '待建'}")
    if not apply:
        print("(唯讀 dry-run；--apply 才套用。)")
        return 0

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(DDL)
        conn.commit()
    print("  ✓ KH4 DDL 冪等完成")
    return check_live()


if __name__ == "__main__":
    sys.exit(main())
