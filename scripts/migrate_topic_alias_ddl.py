#!/usr/bin/env python
"""建 knowledge_topic_alias 表(主題別名→domain 映射住 DB)+ 初始種子 — #29b 去 hardcode。

🎯 這支在做什麼(白話):把原本寫死在 acquire_topic.py 的 TOPIC_ALIAS Python dict(中文主題詞→
   domain ILIKE 樣式)遷成 **PostgreSQL 表** `knowledge_topic_alias`;runtime(acquire_topic)改讀此表,
   **新增別名＝admin INSERT 一列、零改碼**(#29b 資料驅動、來源住 DB、別名/映射也是資料)。
   下方 SEED 僅一次性 bootstrap 初始策展別名(等同 knowledge_source 之種子),之後 SSOT＝DB 表、
   admin 增修;非 runtime hardcode(runtime 只讀表)。
守 #29b(資料驅動、映射住 DB、擴充零 code)· #6(冪等 ON CONFLICT、可重跑)· #29a(bootstrap/指令矩陣)。

執行指令矩陣:
  python scripts/migrate_topic_alias_ddl.py            # 建表 + seed(冪等,可重跑)
  python scripts/migrate_topic_alias_ddl.py --show     # 只列現有別名(不改)
"""
import argparse

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS knowledge_topic_alias (
    alias_id       BIGSERIAL PRIMARY KEY,
    alias_term     TEXT NOT NULL,                       -- 使用者輸入之主題詞(中/英)
    domain_pattern TEXT NOT NULL,                       -- 對應 knowledge_query.domain 之 ILIKE 樣式
    note           TEXT,
    enabled        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (alias_term, domain_pattern)
);
COMMENT ON TABLE knowledge_topic_alias IS
  '主題別名→domain 映射(#29b 資料驅動;runtime acquire_topic 讀此表,新增別名 INSERT 零改碼)';
"""

# 一次性 bootstrap 種子(SSOT 遷入後＝DB 表;此僅初始策展別名,非 runtime hardcode)
SEED = {
    "財經": ["econom%finance%", "business_management%"],
    "投資": ["econom%finance%", "business_management%"], "投資管理": ["business_management%"],
    "經濟": ["econom%"], "管理": ["business_management%", "decision_sciences"],
    "化學": ["chemistry"], "材料": ["materials_science"], "材料科學": ["materials_science"],
    "醫學": ["medicine", "health_professions"], "電腦": ["computer_science"],
    "物理": ["physics%"], "數學": ["mathematics"], "心理": ["psychology"],
    "生物": ["biochem%", "agricultural%bio%", "immunology%"],
    "太陽能": ["solar_materials"], "太陽能材料": ["solar_materials"], "光伏": ["solar_materials"],
    "半導體": ["electronics", "materials_science"], "電子": ["electronics"],
    "能源": ["energy"], "工程": ["engineering"], "環境": ["environmental_science"],
}


def show(cur):
    cur.execute("SELECT alias_term, array_agg(domain_pattern ORDER BY domain_pattern) "
                "FROM knowledge_topic_alias WHERE enabled GROUP BY alias_term ORDER BY alias_term")
    rows = cur.fetchall()
    print(f"── knowledge_topic_alias:{len(rows)} 別名 ──")
    for term, pats in rows:
        print(f"  {term} → {', '.join(pats)}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--show", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            if args.show:
                show(cur); return
            cur.execute(DDL)
            n = 0
            for term, pats in SEED.items():
                for pat in pats:
                    cur.execute("INSERT INTO knowledge_topic_alias(alias_term, domain_pattern) "
                                "VALUES (%s, %s) ON CONFLICT (alias_term, domain_pattern) DO NOTHING", (term, pat))
                    n += cur.rowcount
            print(f"  knowledge_topic_alias 建表 + seed:新增 {n} 列(冪等)")
        with db.transaction(conn) as cur:
            show(cur)


if __name__ == "__main__":
    main()
