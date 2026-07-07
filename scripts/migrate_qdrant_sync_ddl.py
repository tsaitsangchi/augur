#!/usr/bin/env python
"""Qdrant 影子索引同步帳本 schema 遷移 — qdrant_sync_state 一表冪等落地(向量庫遷移階段 0)。

🎯 這支在做什麼(白話):建立 pgvector→Qdrant 匯出的**同步帳本**——逐 (collection, language)
   記錄:游標(cursor_pk,resume 用)、已同步筆數(n_synced)、**CLEAN 過閘後之來源筆數
   (n_source_clean)**、與**未過閘前之總嵌入筆數(n_source_total)**。
   **命門(#15 誠實反差)**:`n_source_total − n_source_clean` = 被 CLEAN 命門擋在影子索引外之列
   (items 側 access_scope='local_private' 之自有私有 ERP 等)——這些**只住 pgvector、永不進外部
   Qdrant**(避免 RBAC 收窄在外部索引失效而洩漏,憲章 v1.36.0 owned_local⇒local_private)。
   帳本讓「影子索引到底放行了哪些、擋掉了幾列」可稽核,不靠宣稱。

   本表**唯記錄面**:不進預測管線(素養層隔離不變式外);Qdrant 索引隨時可 DROP 從 pgvector
   (SSOT)全量重建(SOP-B 可拋棄性);讀取路徑現仍走 pgvector(遷移未 cutover)。

守 #6(冪等重跑安全)· #12(DDL 單一住所)· #15(CLEAN 反差可稽核、非宣稱)· #29a(個別可執行 +
   指令矩陣 + 冪等 + bootstrap)· 憲章 v1.36.0 全文准入三軌(owned_local 私有不外流)·
   SSOT=reports/augur_vectorstore_qdrant_migration_plan_20260707.md 階段 0 / §3.6。

執行指令矩陣:
  python scripts/migrate_qdrant_sync_ddl.py            # 冪等執行 DDL + 印驗證清單(安全預設)
  python scripts/migrate_qdrant_sync_ddl.py --check    # 唯讀:只印驗證清單與現況、不執行 DDL
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

DDL = [
    ("table qdrant_sync_state", """
        CREATE TABLE IF NOT EXISTS qdrant_sync_state (
          collection      text NOT NULL,               -- embedspec.collection_name(禁手寫縮寫)
          language        text NOT NULL,               -- 分割維度(zh/en/...)
          cursor_pk       bigint NOT NULL DEFAULT 0,   -- resume 游標(已匯出之最大 sent_id)
          n_synced        bigint NOT NULL DEFAULT 0,   -- Qdrant 內實際筆數(對帳後)
          n_source_clean  bigint NOT NULL DEFAULT 0,   -- CLEAN 過閘後之 pgvector 來源筆數(=應匯出量)
          n_source_total  bigint NOT NULL DEFAULT 0,   -- 未過閘之總嵌入筆數(該 side/language)
          last_run_at     timestamptz,
          note            text,
          PRIMARY KEY (collection, language)
        )"""),
    ("comment qdrant_sync_state", """
        COMMENT ON TABLE qdrant_sync_state IS
        'pgvector→Qdrant 影子索引同步帳本(向量遷移階段 0);逐 (collection,language) 記游標/同步量/CLEAN 來源量;唯記錄面、不進預測管線;Qdrant 可 DROP 從 pgvector 全量重建'"""),
    ("comment col n_source_clean", """
        COMMENT ON COLUMN qdrant_sync_state.n_source_clean IS
        'CLEAN 命門(augur.knowledge.corpus)過閘後之來源筆數=應匯出至 Qdrant 之量;works 側 review_flag=false∧corpus_class=literary,items 側 license∈白名單∧entity_type∈語意准入∧access_scope=public'"""),
    ("comment col n_source_total", """
        COMMENT ON COLUMN qdrant_sync_state.n_source_total IS
        '該 side/language 未過閘之總嵌入筆數;n_source_total−n_source_clean=被 CLEAN 擋在影子索引外之列(如 local_private 自有 ERP),只住 pgvector、永不外流至 Qdrant(#15 誠實反差、憲章 v1.36.0)'"""),
]

VERIFY = [
    ("qdrant_sync_state 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='qdrant_sync_state'"),
    ("主鍵", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='qdrant_sync_state_pkey'"),
    ("表 COMMENT", "SELECT obj_description('qdrant_sync_state'::regclass)"),
    ("現有列數", "SELECT count(*) FROM qdrant_sync_state"),
]


def _verify(cur):
    print("── 驗證清單 ──")
    for label, sql in VERIFY:
        try:
            cur.execute(sql)
            row = cur.fetchone()
            print(f"  {label}: {(row[0] if row and row[0] is not None else '(無)')}")
        except Exception as e:  # noqa: BLE001  表未建時 count/comment 會失敗 → 誠實印,不中斷
            print(f"  {label}: (查詢失敗:{e})")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Qdrant 同步帳本 DDL 遷移(qdrant_sync_state;冪等)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單、不執行 DDL")
    args = ap.parse_args(argv)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
        _verify(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
