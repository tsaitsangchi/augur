#!/usr/bin/env python
"""know-how 語意橋 schema(K 計畫 §3;欄位詞↔know-how 詞面共現,非資料值相關)。

🎯 這支在做什麼(白話):建 field_term_map(raw 欄位/特徵名經 textnorm 斷詞→詞)與
   field_knowhow_lexical_affinity(欄位詞×know-how 詞之詞面共現係數,cooc_sents≥30 最小分母閘);
   統計鏈三表(cooccurrence/affinity/corpus_stats)加 corpus 判別欄+PK 重建(philosophy/items 分治);
   先 seed 4 列 derivation method(method_key≠method_kind,審查修訂)。

守 #6(冪等)· #12(DDL 單一住所)· #15(lexical≠數值相關,表註免責)· 憲章隔離不變式(橋=素養層)。

執行指令矩陣:
  python scripts/migrate_knowhow_bridge_ddl.py           # 無參數:現況(唯讀)
  python scripts/migrate_knowhow_bridge_ddl.py --run     # 冪等落全部 DDL(PK 重建動 6.5M 列,#30 dump 已先行)
  python scripts/migrate_knowhow_bridge_ddl.py --verify  # 負向測試:低支持 pair 被 CHECK 拒(必 ROLLBACK)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

SEED = """
INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES
  ('rule_field_term_map',         'string_rule', '欄名/中文名/髒值註/表註/特徵名經 textnorm 契約斷詞→詞'),
  ('join_field_lexical_affinity', 'sql_join',    'field_term_map JOIN term_affinity/cooccurrence 之物化(零新事實)'),
  ('cnt_item_term',               'counting',    'items 語料 term×item tf 計數'),
  ('stat_items_corpus_marginal',  'counting',    'items 語料句級邊際分母 df_sents/N(items 獨立分母,絕不沿用哲學分母)')
ON CONFLICT (method_key) DO NOTHING;
"""

TABLES = """
CREATE TABLE IF NOT EXISTS field_term_map (
  dataset      text NOT NULL,
  column_name  text NOT NULL,
  term         text NOT NULL,
  language     text NOT NULL CHECK (language IN ('zh','en')),
  source_field text NOT NULL CHECK (source_field IN
    ('column_name','column_name_zh','dirty_value_note','dataset_notes','feature_name')),
  method_key   text NOT NULL REFERENCES knowledge_derivation_method(method_key),
  created_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (dataset, column_name, term, source_field));

CREATE TABLE IF NOT EXISTS field_knowhow_lexical_affinity (
  dataset      text NOT NULL,
  column_name  text NOT NULL,
  knowhow_term text NOT NULL,
  language     text NOT NULL,
  stat_key     text NOT NULL CHECK (stat_key IN ('npmi','jaccard','llr')),
  stat_value   double precision NOT NULL,
  cooc_sents   bigint NOT NULL CHECK (cooc_sents >= 30),
  corpus_n     bigint NOT NULL,
  corpus       text NOT NULL CHECK (corpus IN ('philosophy','items')),
  method_key   text NOT NULL REFERENCES knowledge_derivation_method(method_key),
  built_at     timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (dataset, column_name, knowhow_term, stat_key, corpus));
COMMENT ON TABLE field_knowhow_lexical_affinity IS
  '詞面共現關聯(lexical):欄位名稱詞×know-how 詞之語料句共現統計;非資料值相關;素養層唯讀、免責硬綁';

CREATE TABLE IF NOT EXISTS knowledge_item_term_stats (
  term text NOT NULL, language text NOT NULL,
  item_id integer NOT NULL REFERENCES knowledge_item(item_id),
  tf integer NOT NULL,
  method_key text NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (term, item_id));

ALTER TABLE knowledge_term_cooccurrence ADD COLUMN IF NOT EXISTS corpus text NOT NULL DEFAULT 'philosophy';
ALTER TABLE knowledge_term_affinity     ADD COLUMN IF NOT EXISTS corpus text NOT NULL DEFAULT 'philosophy';
ALTER TABLE knowledge_term_corpus_stats ADD COLUMN IF NOT EXISTS corpus text NOT NULL DEFAULT 'philosophy';
"""

PK_REBUILD = {  # 表 → (新 PK 欄序)
    "knowledge_term_cooccurrence": "language, term_a, term_b, corpus",
    "knowledge_term_affinity": "term_a, term_b, language, stat_key, corpus",
    "knowledge_term_corpus_stats": "term, language, corpus",
}


def _pk_has_corpus(cur, table):
    cur.execute("""SELECT bool_or(a.attname='corpus') FROM pg_index i
        JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey)
        WHERE i.indrelid=%s::regclass AND i.indisprimary""", (table,))
    return bool(cur.fetchone()[0])


def status(cur):
    for t in ("field_term_map", "field_knowhow_lexical_affinity", "knowledge_item_term_stats"):
        cur.execute("SELECT to_regclass(%s)", (t,))
        n = "-"
        if cur.fetchone()[0]:
            cur.execute(f"SELECT count(*) FROM {t}")
            n = cur.fetchone()[0]
        print(f"  {t}: {n}")
    for t in PK_REBUILD:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name='corpus'", (t,))
        has_col = bool(cur.fetchone())
        print(f"  {t}: corpus 欄={'有' if has_col else '無'} PK含corpus={_pk_has_corpus(cur, t) if has_col else '-'}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        if args.run:
            cur.execute(SEED)
            cur.execute(TABLES)
            for t, cols in PK_REBUILD.items():
                if not _pk_has_corpus(cur, t):
                    cur.execute(f"ALTER TABLE {t} DROP CONSTRAINT {t}_pkey")
                    cur.execute(f"ALTER TABLE {t} ADD PRIMARY KEY ({cols})")
                    print(f"✓ {t} PK 重建含 corpus")
            conn.commit()
            print("✓ 橋 schema 就位(冪等)")
            status(cur)
            return 0
        if args.verify:
            ok = False
            try:
                cur.execute("INSERT INTO field_knowhow_lexical_affinity VALUES "
                            "('t','t','t','en','npmi',0.1, 5, 100,'items','join_field_lexical_affinity',now())")
            except Exception:
                ok = True
                print("✓ 低支持 pair(cooc_sents=5<30)被 CHECK 拒")
            conn.rollback()
            return 0 if ok else 1
        status(cur)
        print(__doc__.split("執行指令矩陣:")[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
