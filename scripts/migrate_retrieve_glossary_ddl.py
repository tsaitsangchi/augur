#!/usr/bin/env python
"""建 retrieve_glossary 表(CJK→EN 檢索詞表住 DB)+ 漿料／光伏種子 — #29b 去 hardcode。

🎯 這支在做什麼(白話):把原本寫死在 query_translation._GLOSSARY 的 CJK→EN 檢索詞對
   遷成 **PostgreSQL 表** `retrieve_glossary`;runtime(query_translation)改讀此表,
   **新增詞對＝admin INSERT 一列、零改碼**(#29b)。SEED 僅一次性 bootstrap;之後 SSOT＝DB。
   只服務 retrieve query 擴展;非 citation／非答案／非 guard 輸入。
守 #29b(策展映射住 DB)· #6(冪等)· #29a/d(指令矩陣) · FZ-keep(零市場 API)。

執行指令矩陣:
  python scripts/migrate_retrieve_glossary_ddl.py            # 安全預設:印矩陣+--check
  python scripts/migrate_retrieve_glossary_ddl.py --check    # 唯讀現況
  python scripts/migrate_retrieve_glossary_ddl.py --apply    # 冪等建表+種子
  python scripts/migrate_retrieve_glossary_ddl.py --show     # 列 active 詞對
  python scripts/migrate_retrieve_glossary_ddl.py --selftest # 零 DB 紅綠
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS retrieve_glossary (
    glossary_id      BIGSERIAL PRIMARY KEY,
    src_cjk          TEXT NOT NULL,
    tgt_en           TEXT NOT NULL,
    priority         INT  NOT NULL DEFAULT 0,
    require_cooccur  BOOLEAN NOT NULL DEFAULT FALSE,
    active           BOOLEAN NOT NULL DEFAULT TRUE,
    provenance       TEXT,
    note             TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (src_cjk, tgt_en)
);
CREATE INDEX IF NOT EXISTS idx_retrieve_glossary_active_prio
  ON retrieve_glossary (active, priority DESC, char_length(src_cjk) DESC)
  WHERE active;
COMMENT ON TABLE retrieve_glossary IS
  'CJK→EN 檢索詞表(#29b；runtime query_translation 讀表；只服務 retrieve query；非 citation／非答案／非 guard 輸入)';
"""

# 一次性 bootstrap(SSOT 遷入後＝DB;非 runtime hardcode)。漿料過寬→require_cooccur。
SEED = (
    ("導電漿料", "conductive paste", False),
    ("正面銀漿", "front silver paste", False),
    ("背面鋁漿", "rear aluminum paste", False),
    ("銀漿", "silver paste", False),
    ("鋁漿", "aluminum paste", False),
    ("金屬化", "metallization", False),
    ("太陽能電池", "solar cell", False),
    ("多主柵", "multi busbar", False),
    ("鈣鈦礦", "perovskite", False),
    ("光伏", "photovoltaic", False),
    ("半導體", "semiconductor", False),
    ("矽晶", "silicon wafer", False),
    ("漿料", "paste", True),
)
PROVENANCE = "steward_seed_20260728"


def check(conn):
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('retrieve_glossary') IS NOT NULL")
        exists = cur.fetchone()[0]
        print(f"  retrieve_glossary: {'已建' if exists else '未建'}")
        if not exists:
            return 1
        cur.execute("SELECT count(*) FROM retrieve_glossary WHERE active")
        n = cur.fetchone()[0]
        cur.execute(
            "SELECT require_cooccur FROM retrieve_glossary "
            "WHERE src_cjk=%s AND active",
            ("漿料",),
        )
        row = cur.fetchone()
        paste_ok = bool(row and row[0] is True)
        print(f"  active 列數: {n}(種子目標 13)")
        print(f"  漿料.require_cooccur: {paste_ok}")
        return 0 if n >= 13 and paste_ok else 1


def show(conn):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT src_cjk, tgt_en, require_cooccur, priority "
            "FROM retrieve_glossary WHERE active "
            "ORDER BY priority DESC, char_length(src_cjk) DESC, src_cjk"
        )
        rows = cur.fetchall()
    print(f"── retrieve_glossary:{len(rows)} active ──")
    for src, tgt, co, pri in rows:
        flag = " [cooccur]" if co else ""
        print(f"  {src} → {tgt}{flag} (prio={pri})")
    return 0


def apply(conn):
    with db.transaction(conn) as cur:
        cur.execute(DDL)
        n = 0
        for src, tgt, co in SEED:
            cur.execute(
                "INSERT INTO retrieve_glossary"
                "(src_cjk, tgt_en, priority, require_cooccur, active, provenance) "
                "VALUES (%s, %s, 0, %s, TRUE, %s) "
                "ON CONFLICT (src_cjk, tgt_en) DO UPDATE SET "
                "require_cooccur=EXCLUDED.require_cooccur, "
                "active=TRUE, updated_at=now(), "
                "provenance=COALESCE(retrieve_glossary.provenance, EXCLUDED.provenance)",
                (src, tgt, co, PROVENANCE),
            )
            n += cur.rowcount
        print(f"  retrieve_glossary 建表 + seed:upsert 影響 {n} 列(冪等)")
    return check(conn)


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("IF NOT EXISTS 冪等", "IF NOT EXISTS" in DDL)
    chk("UNIQUE(src_cjk,tgt_en)", "UNIQUE (src_cjk, tgt_en)" in DDL)
    chk("require_cooccur 欄", "require_cooccur" in DDL)
    chk("種子 13 列", len(SEED) == 13)
    paste = [s for s in SEED if s[0] == "漿料"]
    chk("漿料.require_cooccur=True", len(paste) == 1 and paste[0][2] is True)
    chk("其餘種子非 cooccur", all(s[2] is False for s in SEED if s[0] != "漿料"))
    chk("COMMENT 載 #29b／retrieve", "#29b" in DDL and "retrieve" in DDL)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    with db.connect() as conn:
        if "--apply" in argv:
            return apply(conn)
        if "--show" in argv:
            return show(conn)
        if "--check" in argv:
            return check(conn)
        print(__doc__)
        return check(conn)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
