#!/usr/bin/env python
"""建 knowledge_fulltext_status 表(全文擷取終態帳本)— #15 誠實記「license 阻擋、非漏做」。

🎯 這支在做什麼(白話):harvest 只到 metadata,下游 fetch_oa_fulltext 對 DOI 問 Unpaywall——
   多數文獻**非 OA / 非 CC 白名單 / 僅 PDF**,全文抓不了。原本這些條目與「尚未嘗試」者
   在 DB 無法區分(兩者皆「無 item_text」),故 fetch 每輪重掃、待辦計數永不收斂、看似漏做。
   本表為每個「已嘗試但未落地全文」之 item 記一列(status+reason+checked_at),使:
   (a) 冪等——已判定 blocked 者下次不重問 Unpaywall(#6/#28 省 API);
   (b) 收斂——「待抓」= 無全文且尚未有終態帳;
   (c) 誠實(#15)——blocked 是 license 現實非系統漏抓,可溯源、可回報「N 筆 license 阻擋」。
   status='ok' 之列不入本表(全文已在 knowledge_item_text=終態載體);本表只收 blocked 終態。
守 #15(誠實帳本、blocked≠漏做)· #6(冪等 ON CONFLICT、可重跑)· #12(DDL 單一住所)· #29a(bootstrap/指令矩陣)。

執行指令矩陣:
  python scripts/migrate_fulltext_status_ddl.py           # 建表(冪等,可重跑)+ 印驗證
  python scripts/migrate_fulltext_status_ddl.py --check   # 唯讀:只印驗證清單、不執行 DDL
"""
import sys
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

# status 封閉集=三支 resolver 之非 'ok' 終態(跨檔一致 #19;新增型別須同步此 CHECK):
#   fetch_oa_fulltext.py:      skip_no_oa/skip_license/skip_pdf/skip_ctype/skip_short/skip_fetch_error
#   fetch_entity_fulltext.py:  + skip_no_fulltext/skip_no_resolver/skip_no_license(件 B-1~B-4)
#   acquire_abstract.py:       + abstract_none/abstract_no_license/abstract_short/abstract_fetch_error(件 B-0)
STATUS_VALUES = ("skip_no_oa", "skip_license", "skip_pdf", "skip_ctype", "skip_short", "skip_fetch_error",
                 "skip_no_fulltext", "skip_no_resolver", "skip_no_license",
                 "abstract_none", "abstract_no_license", "abstract_short", "abstract_fetch_error")

DDL = f"""
CREATE TABLE IF NOT EXISTS knowledge_fulltext_status (
    item_id    int PRIMARY KEY REFERENCES knowledge_item(item_id),
    status     varchar(24) NOT NULL
               CHECK (status IN ({", ".join(f"'{s}'" for s in STATUS_VALUES)})),
    reason     text,                                    -- 人可讀說明(誠實記 license/OA 現實)
    source_url text,                                    -- 若查到 OA location(license 未過)則留存溯源
    checked_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE knowledge_fulltext_status IS
  '全文擷取終態帳本(#15):已嘗試但 license/OA 阻擋之 item 終態;status=ok 不入(全文在 item_text)';
"""

# 既有表(舊 6 值 CHECK)升級為 superset:CREATE IF NOT EXISTS 不改既有 CHECK,須顯式 DROP+ADD
# (#30:小表 16k 列、superset 驗證即時、audit 非 dump/不碰本表 → ACCESS EXCLUSIVE 安全)。
MIGRATE = f"""
DO $$
DECLARE cname text;
BEGIN
  IF to_regclass('knowledge_fulltext_status') IS NULL THEN RETURN; END IF;
  FOR cname IN
    SELECT conname FROM pg_constraint
    WHERE conrelid='knowledge_fulltext_status'::regclass AND contype='c'
      AND pg_get_constraintdef(oid) LIKE '%status%'
  LOOP
    EXECUTE 'ALTER TABLE knowledge_fulltext_status DROP CONSTRAINT ' || quote_ident(cname);
  END LOOP;
  ALTER TABLE knowledge_fulltext_status
    ADD CONSTRAINT chk_fulltext_status
    CHECK (status IN ({", ".join(f"'{s}'" for s in STATUS_VALUES)}));
END $$;
"""


def verify(cur):
    cur.execute("SELECT to_regclass('knowledge_fulltext_status')")
    exists = bool(cur.fetchone()[0])
    print(f"  {'✓' if exists else '✗'} table knowledge_fulltext_status")
    if exists:
        cur.execute("SELECT status, count(*) FROM knowledge_fulltext_status GROUP BY 1 ORDER BY 1")
        rows = cur.fetchall()
        print("  現有終態帳:" + ("(空)" if not rows else "; ".join(f"{s} {n}" for s, n in rows)))
    return exists


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--check", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT to_regclass('knowledge_item')")
            if not cur.fetchone()[0]:
                sys.exit("先決缺:knowledge_item 未建(FK 依賴)→ 先跑 python scripts/harvest_knowledge.py --migrate-only")
        if not args.check:
            with db.transaction(conn) as cur:
                cur.execute(DDL)
            with db.transaction(conn) as cur:            # 既有表 CHECK 升級為 superset(冪等)
                cur.execute(MIGRATE)
            print("DDL 冪等完成:knowledge_fulltext_status(CHECK 已含 13 狀態值)")
        with db.transaction(conn) as cur:
            ok = verify(cur)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
