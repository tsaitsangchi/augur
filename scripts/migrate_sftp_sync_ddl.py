#!/usr/bin/env python
"""🎯 件 A2 SFTP 增量同步帳本 sftp_sync_state 之 DDL 遷移(冪等、可 dry-run)。

建 sftp_sync_state(#6 resume-safe 增量帳本):(source_key,remote_path) 唯一,remote_mtime+size 驅動增量、
content_sha1 稽核;change_kind∈new/changed/skip;superseded_item_id 記 changed 撤回之舊 item(對抗審查修正)。
item_id 型別=int(對齊實證 knowledge_item.item_id=integer,非 master plan 誤寫 bigint);連線設定住
knowledge_source.adapter_config JSONB(非此表、非 query_template)。

守 #12(DDL 單一住所)· #6(CREATE IF NOT EXISTS 冪等、--check 唯讀)· #29a/#29d· #30(dump 後+audit 綠再 --apply)。

執行指令矩陣:
  python scripts/migrate_sftp_sync_ddl.py           # 無參數=dry-run(印現況、不建)
  python scripts/migrate_sftp_sync_ddl.py --apply   # 冪等建表(#30:dump 後+audit 綠)
  python scripts/migrate_sftp_sync_ddl.py --check    # 唯讀驗證(表存在否+列數)
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS sftp_sync_state (
    sync_id            bigserial PRIMARY KEY,
    source_key         varchar(64) NOT NULL REFERENCES knowledge_source(source_key),
    remote_host        text        NOT NULL,
    remote_path        text        NOT NULL,
    remote_mtime       bigint,                                   -- 遠端 st_mtime(epoch 秒)供增量比對
    size_bytes         bigint,                                    -- 遠端 st_size 供增量比對
    content_sha1       char(40),                                  -- 下載內容 sha1(稽核)
    item_id            int  REFERENCES knowledge_item(item_id),   -- 對齊 integer PK(非 bigint);skip 時 NULL
    superseded_item_id int,                                       -- changed 撤回之舊 item(對抗審查:changed 不遺棄舊版)
    change_kind        varchar(8),                                -- 'new'|'changed'|'skip'
    first_seen         timestamptz NOT NULL DEFAULT now(),
    last_synced        timestamptz NOT NULL DEFAULT now(),
    UNIQUE(source_key, remote_path)                              -- #6 冪等增量鍵(ON CONFLICT upsert)
);
COMMENT ON TABLE sftp_sync_state IS
  'SFTP 通道增量同步帳本(件 A2,#6 resume-safe);(source_key,remote_path) 唯一,mtime+size 驅動增量、content_sha1 稽核';
"""


def verify(cur):
    cur.execute("SELECT to_regclass('sftp_sync_state')")
    exists = bool(cur.fetchone()[0])
    print(f"  {'✓' if exists else '✗'} table sftp_sync_state")
    if exists:
        cur.execute("SELECT count(*), count(DISTINCT source_key) FROM sftp_sync_state")
        n, s = cur.fetchone()
        print(f"  現有 {n} 列 / {s} 源")
    return exists


def main():
    check = "--check" in sys.argv
    apply = ("--apply" in sys.argv) and not check
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT to_regclass('knowledge_item'), to_regclass('knowledge_source')")
            item, src = cur.fetchone()
        if not (item and src):
            sys.exit("先決缺:knowledge_item/knowledge_source 未建(FK 依賴)")
        if apply:
            with db.transaction(conn) as cur:
                cur.execute(DDL)
            print("DDL 冪等完成:sftp_sync_state")
        else:
            print("(dry-run;--apply 才建表。⚠ #30:dump 後+audit 綠再 --apply)")
        with db.transaction(conn) as cur:
            ok = verify(cur)
    return 0 if (ok or not apply) else 1


if __name__ == "__main__":
    sys.exit(main())
