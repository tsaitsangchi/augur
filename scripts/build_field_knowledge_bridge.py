#!/usr/bin/env python
"""欄位↔know-how 語意橋 builder(K 計畫 K1):field_term_map + field_knowhow_lexical_affinity。

🎯 這支在做什麼(白話):把 raw data 欄位定義文字(column_catalog 欄名/中文名/髒值註、dataset_catalog
   表註、feature 目錄)經 textnorm 契約斷詞落 field_term_map;再 JOIN 統計鏈(term_affinity×cooccurrence,
   philosophy+items 雙語料)物化 field_knowhow_lexical_affinity——**詞面共現關聯,非資料值相關**
   (免責住表 COMMENT;cooc_sents≥30 CHECK 閘擋稀疏假係數)。

守 #6(冪等 --rebuild)· #15(lexical 誠實定義)· 隔離不變式(素養層唯讀;預測 package 字面掃描擋引用)。

執行指令矩陣:
  python scripts/build_field_knowledge_bridge.py            # 無參數:現況+覆蓋分佈(唯讀)
  python scripts/build_field_knowledge_bridge.py --run      # 全量重建橋(分鐘級)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import textnorm

M_MAP = "rule_field_term_map"
M_AFF = "join_field_lexical_affinity"
MIN_COOC_BRIDGE = 30  # 與 DDL CHECK 同值(schema 為 SSOT)


def _terms(text, language):
    if not text:
        return []
    try:
        return [t for t, _ in textnorm.tokenize(str(text), language)]
    except Exception:
        return []


def build_map(cur):
    cur.execute("DELETE FROM field_term_map")
    rows = []
    cur.execute("SELECT dataset, column_name, column_name_zh, dirty_value_note FROM column_catalog")
    for ds, col, zh, note in cur.fetchall():
        for t in _terms(col, "en"):
            rows.append((ds, col, t, "en", "column_name"))
        for t in _terms(zh, "zh"):
            rows.append((ds, col, t, "zh", "column_name_zh"))
        for t in _terms(note, "zh"):
            rows.append((ds, col, t, "zh", "dirty_value_note"))
    cur.execute("SELECT dataset, table_name_zh, notes FROM dataset_catalog")
    for ds, zh, notes in cur.fetchall():
        for t in _terms(zh, "zh") + _terms(notes, "zh"):
            rows.append((ds, "_dataset_", t, "zh", "dataset_notes"))
    cur.execute("SELECT DISTINCT feature FROM feature_values")
    for (feat,) in cur.fetchall():
        for t in _terms(feat.replace("_", " "), "en"):
            rows.append(("feature", feat, t, "en", "feature_name"))
    seen = set()
    uniq = [r for r in rows if not (r[:2] + (r[2], r[4]) in seen or seen.add(r[:2] + (r[2], r[4])))]
    cur.executemany(
        "INSERT INTO field_term_map (dataset, column_name, term, language, source_field, method_key) "
        f"VALUES (%s,%s,%s,%s,%s,'{M_MAP}') ON CONFLICT DO NOTHING", uniq)
    cur.execute("SELECT count(*), count(DISTINCT (dataset, column_name)) FROM field_term_map")
    n, cols = cur.fetchone()
    print(f"field_term_map:{n:,} 列 / 覆蓋 {cols} 個欄位·特徵·表")


def build_affinity(cur):
    cur.execute("DELETE FROM field_knowhow_lexical_affinity")
    cur.execute(f"""INSERT INTO field_knowhow_lexical_affinity
          (dataset, column_name, knowhow_term, language, stat_key, stat_value,
           cooc_sents, corpus_n, corpus, method_key)
        SELECT DISTINCT ON (f.dataset, f.column_name, kh.knowhow_term, a.stat_key, a.corpus)
               f.dataset, f.column_name, kh.knowhow_term, a.language, a.stat_key, a.stat_value,
               c.cooc_sents, a.basis_n, a.corpus, '{M_AFF}'
        FROM field_term_map f
        JOIN knowledge_term_affinity a
          ON a.language = f.language AND (a.term_a = f.term OR a.term_b = f.term)
        CROSS JOIN LATERAL (SELECT CASE WHEN a.term_a = f.term THEN a.term_b ELSE a.term_a END AS knowhow_term) kh
        JOIN knowledge_term_cooccurrence c
          ON c.language = a.language AND c.corpus = a.corpus
         AND c.term_a = LEAST(a.term_a, a.term_b) AND c.term_b = GREATEST(a.term_a, a.term_b)
        WHERE c.cooc_sents >= %s
        ORDER BY f.dataset, f.column_name, kh.knowhow_term, a.stat_key, a.corpus, a.stat_value DESC""",
        (MIN_COOC_BRIDGE,))
    print(f"field_knowhow_lexical_affinity:{cur.rowcount:,} 列(cooc_sents≥{MIN_COOC_BRIDGE})")


def report(cur):
    cur.execute("SELECT corpus, count(*), count(DISTINCT (dataset, column_name)) "
                "FROM field_knowhow_lexical_affinity GROUP BY 1")
    for corpus, n, cols in cur.fetchall():
        print(f"  [{corpus}] {n:,} 係數 / {cols} 欄覆蓋")
    cur.execute("""SELECT dataset||'.'||column_name, knowhow_term, round(stat_value::numeric,3), cooc_sents
        FROM field_knowhow_lexical_affinity WHERE corpus='items' AND stat_key='npmi'
        ORDER BY stat_value DESC LIMIT 5""")
    for r in cur.fetchall():
        print(f"  樣例(items npmi):{r[0]} ↔ {r[1]} = {r[2]}(共現 {r[3]} 句)")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        if args.run:
            build_map(cur)
            build_affinity(cur)
            conn.commit()
            report(cur)
            print("✓ 橋重建完成(冪等)")
            return 0
        report(cur)
        print(__doc__.split("執行指令矩陣:")[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
