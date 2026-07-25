#!/usr/bin/env python
"""跨域原理映射表 DDL — principle_domain_map 冪等落地(憲章 v1.47.0;人閘首案 gp_8f3121e2251d hugo 核可)。
🎯 這支在做什麼(白話):建「基本原理×應用域」映射表(例:第一性原理→投資、孫子兵法→企業管理)。
   schema 由憲章 v1.47.0 指定:注記兩型封閉(verbatim_quote/human_authored,AI 生成詮釋 DB CHECK 硬擋)、
   citation NOT NULL(真實文獻錨)、domain=應用注記軸**非量化資格**(量化鏈頭不變=investment school 全鏈)。
守 #6(冪等)· #12(DDL 單一住所=本檔)· #29a/d · 共同不變式①②。
執行指令矩陣:
  python scripts/migrate_principle_domain_map_ddl.py            # 安全預設:印矩陣+--check
  python scripts/migrate_principle_domain_map_ddl.py --check    # 唯讀現況
  python scripts/migrate_principle_domain_map_ddl.py --apply    # 冪等建表
  python scripts/migrate_principle_domain_map_ddl.py --selftest # 零 DB 紅綠
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS principle_domain_map (
  map_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  principle_id integer NOT NULL REFERENCES philosophy_principle(principle_id) ON DELETE CASCADE,
  domain text NOT NULL,
  note_kind text NOT NULL CHECK (note_kind IN ('verbatim_quote','human_authored')),
  application_note text NOT NULL,
  citation text NOT NULL,
  source_type text NOT NULL CHECK (source_type <> 'ai_generated'),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (principle_id, domain));
COMMENT ON TABLE principle_domain_map IS
  '跨域原理映射(憲章 v1.47.0):基本原理×應用域;注記兩型封閉、AI 生成詮釋硬擋;domain=應用注記軸非量化資格(量化鏈頭=investment school 全鏈共同不變式②);人閘首案 gp_8f3121e2251d';
"""


def check(conn):
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('principle_domain_map') IS NOT NULL")
        exists = cur.fetchone()[0]
        print(f"  principle_domain_map: {'已建' if exists else '未建'}")
        if exists:
            cur.execute("""SELECT count(*) FROM pg_constraint
                WHERE conrelid='principle_domain_map'::regclass AND contype='c'""")
            print(f"  CHECK 約束數: {cur.fetchone()[0]}(應 ≥2:note_kind 封閉+source_type 禁 ai_generated)")
            cur.execute("SELECT count(*) FROM principle_domain_map")
            print(f"  映射列數: {cur.fetchone()[0]}")
    return 0


def apply(conn):
    with db.transaction(conn) as cur:
        cur.execute(DDL)
    print("✓ principle_domain_map 落地(冪等)")
    return check(conn)


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("注記兩型封閉", "note_kind IN ('verbatim_quote','human_authored')" in DDL)
    chk("AI 生成硬擋", "source_type <> 'ai_generated'" in DDL)
    chk("citation NOT NULL(真實文獻錨)", "citation text NOT NULL" in DDL)
    chk("FK→philosophy_principle CASCADE", "REFERENCES philosophy_principle(principle_id) ON DELETE CASCADE" in DDL)
    chk("(principle_id,domain) UNIQUE(冪等 upsert 錨)", "UNIQUE (principle_id, domain)" in DDL)
    chk("表 COMMENT 載『非量化資格』", "非量化資格" in DDL)
    chk("冪等", "IF NOT EXISTS" in DDL)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    with db.connect() as conn:
        if "--apply" in argv:
            return apply(conn)
        if "--check" in argv:
            return check(conn)
        print(__doc__)
        return check(conn)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
