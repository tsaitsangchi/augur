#!/usr/bin/env python
"""建 knowledge_sentence_resplit_ledger — LSR-S0。

🎯 這支在做什麼(白話):長句重切帳本 DDL（可溯源 old/new sent_id）；非答案 SSOT。
守 #6(冪等)· #29a/d· FZ-keep· LSR-PLAN。

執行指令矩陣:
  python scripts/migrate_sentence_resplit_ddl.py              # 安全預設:印矩陣+--check
  python scripts/migrate_sentence_resplit_ddl.py --check
  python scripts/migrate_sentence_resplit_ddl.py --apply
  python scripts/migrate_sentence_resplit_ddl.py --selftest
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401

DDL = """
CREATE TABLE IF NOT EXISTS knowledge_sentence_resplit_ledger (
    ledger_id      BIGSERIAL PRIMARY KEY,
    side           TEXT NOT NULL CHECK (side IN ('items','works')),
    parent_id      BIGINT NOT NULL,
    old_sent_ids   BIGINT[] NOT NULL,
    new_sent_ids   BIGINT[] NOT NULL DEFAULT '{}',
    max_chars      INT NOT NULL,
    old_count      INT NOT NULL,
    new_count      INT NOT NULL,
    bytes_in       BIGINT,
    script         TEXT NOT NULL DEFAULT 'resplit_long_sentences.py',
    git_sha        TEXT,
    note           TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_resplit_parent
  ON knowledge_sentence_resplit_ledger (side, parent_id);
COMMENT ON TABLE knowledge_sentence_resplit_ledger IS
  'LSRS-S0: 長句重切帳本（#15；非答案 SSOT／非預測特徵）';
"""


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 含 ledger 表", "knowledge_sentence_resplit_ledger" in DDL)
    chk("side 閉集 items/works", "'items'" in DDL and "'works'" in DDL)
    chk("有 old_sent_ids", "old_sent_ids" in DDL)
    chk("指令矩陣", "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.knowledge_sentence_resplit_ledger')")
        exists = bool(cur.fetchone()[0])
        print(f"knowledge_sentence_resplit_ledger={'已在' if exists else '缺'}")
        if not exists:
            return 1
        cur.execute("SELECT count(*) FROM knowledge_sentence_resplit_ledger")
        print(f"rows={cur.fetchone()[0]}")
        # 盤點口徑（計畫 §1.2）
        cur.execute(
            """
            SELECT language,
              count(*) FILTER (WHERE length(sentence)>1000) AS gt1000,
              count(*) FILTER (
                WHERE length(sentence)>1000 AND NOT EXISTS (
                  SELECT 1 FROM knowledge_sentence_embedding e WHERE e.sent_id=s.sent_id)
              ) AS gt1000_no_emb,
              count(*) AS n
            FROM knowledge_sentence s
            GROUP BY 1 ORDER BY 1
            """
        )
        print("sent_len_buckets=", cur.fetchall())
        cur.execute(
            """
            SELECT count(DISTINCT itext_id) FROM knowledge_sentence
            WHERE itext_id IS NOT NULL AND length(sentence)>1000
              AND NOT EXISTS (
                SELECT 1 FROM knowledge_sentence_embedding e
                WHERE e.sent_id=knowledge_sentence.sent_id)
            """
        )
        print(f"items_itext_gt1000_no_emb={cur.fetchone()[0]}")
    return 0


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="LSRS resplit ledger DDL")
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
    print("  ✓ resplit ledger DDL 冪等完成")
    return check_live()


if __name__ == "__main__":
    sys.exit(main())
