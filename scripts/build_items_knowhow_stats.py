#!/usr/bin/env python
"""items 語料統計軌(K 計畫 K2):投資 know-how 詞之 corpus_stats/cooccurrence/affinity(corpus='items')。

🎯 這支在做什麼(白話):對 items 側 CLEAN 語料(license 過閘全文×投資三域)以既有 concordance
   postings∩stat_vocab 計:①items 獨立分母(corpus_stats,絕不沿用哲學分母 #15)②term×item tf
   ③句級共現 ④npmi/jaccard/llr 閉式係數——全確定性 SQL、零 LLM(derivation method CHECK 硬擋)。
   哲學軌不動(build_cross_school_stats 已 corpus-scoped);groupstats 學派 keyness 對 items 無定義、不移植。

守 #6(冪等:DELETE corpus='items' 重建)· #9/#10(分母可溯源)· #15(items 分母獨立)· 隔離不變式(素養層)。

執行指令矩陣:
  python scripts/build_items_knowhow_stats.py            # 無參數:現況+CLEAN 語料量(唯讀)
  python scripts/build_items_knowhow_stats.py --run      # 全量重建 items 軌(語料小,分鐘級)
  python scripts/build_items_knowhow_stats.py --language en --run
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

CLEAN_DOMAINS = ("economics_econometrics_and_finance", "business_management_and_accounting", "decision_sciences")
MIN_COOC = 5  # 內部共現下限(同哲學軌操作值);橋層另有 cooc_sents>=30 CHECK 閘

CLEAN_SENTS = """
SELECT s.sent_id, it.item_id, s.language
FROM knowledge_sentence s
JOIN knowledge_item_text it ON s.itext_id = it.itext_id
JOIN knowledge_item i ON i.item_id = it.item_id
WHERE i.domain = ANY(%s) AND it.access_scope IN ('public','local_private')
"""


def run(cur, lang):
    cur.execute(f"CREATE TEMP TABLE _clean AS {CLEAN_SENTS} AND s.language=%s", (list(CLEAN_DOMAINS), lang))
    cur.execute("SELECT count(*) FROM _clean")
    n_sents = cur.fetchone()[0]
    print(f"[{lang}] CLEAN items 句={n_sents:,}")
    if not n_sents:
        cur.execute("DROP TABLE _clean")
        return
    # postings = concordance ∩ CLEAN ∩ vocab(詞彙閘沿用)
    cur.execute("""CREATE TEMP TABLE _t AS
        SELECT c.term, cl.sent_id, cl.item_id FROM knowledge_concordance c
        JOIN _clean cl ON cl.sent_id = c.sent_id
        JOIN knowledge_stat_vocab v ON v.term = c.term AND v.language = %s
        WHERE c.language = %s""", (lang, lang))
    cur.execute("SELECT count(*) FROM _t")
    print(f"[{lang}] vocab 閘後 postings={cur.fetchone()[0]:,}")

    # ① items 獨立分母(corpus_stats corpus='items')
    cur.execute("DELETE FROM knowledge_term_corpus_stats WHERE corpus='items' AND language=%s", (lang,))
    cur.execute("""INSERT INTO knowledge_term_corpus_stats
          (term, language, tf_total, df_works, df_sents, method_key, corpus)
        SELECT term, %s, count(*), count(DISTINCT item_id), count(DISTINCT sent_id),
               'stat_items_corpus_marginal', 'items'
        FROM _t GROUP BY term""", (lang,))
    print(f"[{lang}] corpus_stats(items)={cur.rowcount:,}")

    # ② term×item tf
    cur.execute("DELETE FROM knowledge_item_term_stats WHERE language=%s", (lang,))
    cur.execute("""INSERT INTO knowledge_item_term_stats (term, language, item_id, tf, method_key)
        SELECT term, %s, item_id, count(*), 'cnt_item_term' FROM _t GROUP BY term, item_id""", (lang,))
    print(f"[{lang}] item_term_stats={cur.rowcount:,}")

    # ③ 句級共現(term_a<term_b)
    cur.execute("DELETE FROM knowledge_term_cooccurrence WHERE corpus='items' AND language=%s", (lang,))
    cur.execute("""INSERT INTO knowledge_term_cooccurrence
          (term_a, term_b, language, cooc_sents, cooc_works, method_key, corpus)
        SELECT a.term, b.term, %s, count(DISTINCT a.sent_id), count(DISTINCT a.item_id),
               'cnt_cooc_sentence', 'items'
        FROM (SELECT DISTINCT term, sent_id, item_id FROM _t) a
        JOIN (SELECT DISTINCT term, sent_id, item_id FROM _t) b
          ON b.sent_id = a.sent_id AND b.term > a.term
        GROUP BY 1, 2 HAVING count(DISTINCT a.sent_id) >= %s""", (lang, MIN_COOC))
    print(f"[{lang}] cooccurrence(items,≥{MIN_COOC})={cur.rowcount:,}")

    # ④ 閉式係數(items 分母 N=CLEAN 句數;basis_n=N 可溯源)
    cur.execute("DELETE FROM knowledge_term_affinity WHERE corpus='items' AND language=%s", (lang,))
    cur.execute("""INSERT INTO knowledge_term_affinity
          (term_a, term_b, language, stat_key, stat_value, basis_n, rank_in_a, method_key, corpus)
        WITH d AS (
          SELECT term_a AS a, term_b AS b, cooc_sents FROM knowledge_term_cooccurrence
          WHERE language=%s AND corpus='items'
          UNION ALL
          SELECT term_b, term_a, cooc_sents FROM knowledge_term_cooccurrence
          WHERE language=%s AND corpus='items'
        ), j AS (
          SELECT d.a, d.b, d.cooc_sents::double precision AS cab,
                 ca.df_sents::double precision AS ca, cb.df_sents::double precision AS cb,
                 %s::double precision AS nn
          FROM d
          JOIN knowledge_term_corpus_stats ca ON ca.term=d.a AND ca.language=%s AND ca.corpus='items'
          JOIN knowledge_term_corpus_stats cb ON cb.term=d.b AND cb.language=%s AND cb.corpus='items'
        ), s AS (
          SELECT a, b, v.stat_key, v.stat_value FROM j CROSS JOIN LATERAL (VALUES
            ('npmi', CASE WHEN cab < nn THEN ln(cab*nn/(ca*cb)) / (-ln(cab/nn)) END),
            ('jaccard', cab/(ca+cb-cab))
          ) v(stat_key, stat_value)
          WHERE v.stat_value IS NOT NULL
        ), r AS (
          SELECT *, row_number() OVER (PARTITION BY a, stat_key ORDER BY stat_value DESC, b) AS rk FROM s
        )
        SELECT a, b, %s, stat_key, stat_value, %s::bigint, rk,
               CASE stat_key WHEN 'npmi' THEN 'stat_npmi' ELSE 'stat_jaccard' END, 'items'
        FROM r""", (lang, lang, n_sents, lang, lang, lang, n_sents))
    print(f"[{lang}] affinity(items)={cur.rowcount:,}(npmi/jaccard;llr 留待語料放量後加)")
    cur.execute("DROP TABLE _t"); cur.execute("DROP TABLE _clean")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--language", default=None)
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        if not args.run:
            cur.execute(f"SELECT language, count(*) FROM ({CLEAN_SENTS}) q GROUP BY 1", (list(CLEAN_DOMAINS),))
            for lang, n in cur.fetchall():
                print(f"  CLEAN items[{lang}]:{n:,} 句")
            for t in ("knowledge_term_corpus_stats", "knowledge_term_cooccurrence", "knowledge_term_affinity"):
                cur.execute(f"SELECT count(*) FROM {t} WHERE corpus='items'")
                print(f"  {t}(items):{cur.fetchone()[0]:,}")
            print(__doc__.split("執行指令矩陣:")[1])
            return 0
        langs = [args.language] if args.language else ["en", "zh"]
        for lang in langs:
            run(cur, lang)
            conn.commit()
        print("✓ items 軌完成(冪等)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
