"""L6 跨學說思想關聯圖 — 查詢介面（整合既有 affinity + concordance,零 AI 生成、逐字可溯源、唯讀）。

🎯 這支在做什麼（白話）：給 advisor／人查「思想家/字詞之間 **computed 的統計關聯** + **逐字共現證據**」。
   節點＝既有真實實體（thinker/school/lexicon term）;邊＝既有 affinity 表之統計值（npmi/cosine…,
   全 method_key FK 到 knowledge_derivation_method＝結構上封死 AI 生成）;證據＝concordance 逐字共現句。
   **純查既有 computed 資料——不生成關係意義、不落新庫、不引 e5 跨語 cosine（已證弱）。**
   關係的「意義/詮釋」由 advisor **即時**對著這些數字+逐字原文說,不由本層產生、不入庫。
守 #1（關聯＝既有 computed stat、非 AI 生成）· #15（coverage 誠實、junk/缺口不掩蓋）·
   隔離不變式（素養層、住 augur.knowledge＝import_isolation 前綴自動覆蓋、零量化價值不進預測管線）。
"""
from augur.core import db


def related_thinkers(name_or_id, language="zh", top_n=8):
    """某思想家的 top-N 相關思想家（group_affinity tfidf_cosine_counts,count-based 同語言、非 e5）。
    回 [(thinker_id, name_zh, cosine, n_support)]。查不到 → []（該思想家未進 group_affinity）。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE thinker_id::text=%s OR name=%s OR name_zh=%s LIMIT 1",
                    (str(name_or_id), name_or_id, name_or_id))
        row = cur.fetchone()
        if not row:
            return []
        tid = str(row[0])
        # group_a < group_b（CHECK）→ 兩向都查
        cur.execute(
            "SELECT CASE WHEN group_a=%s THEN group_b ELSE group_a END peer, stat_value, basis_n "
            "FROM knowledge_group_affinity "
            "WHERE group_kind='thinker' AND language=%s AND stat_key='tfidf_cosine_counts' "
            "  AND (group_a=%s OR group_b=%s) ORDER BY stat_value DESC LIMIT %s",
            (tid, language, tid, tid, top_n))
        peers = cur.fetchall()
        out = []
        for peer, cos, n in peers:
            cur.execute("SELECT name_zh, name FROM philosophy_thinker WHERE thinker_id::text=%s", (str(peer),))
            nm = cur.fetchone()
            out.append((str(peer), (nm[0] or nm[1]) if nm else str(peer), float(cos), int(n)))
        return out


def related_terms(term, language="zh", top_n=8, min_support=3):
    """某字詞的 top-N 相關詞（term_affinity npmi）。回 [(term_b, npmi, n_support)]。
    min_support：共現句數下界（濾單次巧合/boilerplate 假高 npmi,#15 品質閘）。查不到 → []（該詞未進 stat_vocab）。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            "SELECT term_b, stat_value, basis_n FROM knowledge_term_affinity "
            "WHERE term_a=%s AND language=%s AND stat_key='npmi' AND basis_n>=%s "
            "ORDER BY stat_value DESC LIMIT %s",
            (term, language, min_support, top_n))
        return [(b, float(v), int(n)) for b, v, n in cur.fetchall()]


def cooccurrence_evidence(term_a, term_b, language="zh", limit=5):
    """兩詞的**逐字共現句**（concordance 交集 → knowledge_sentence 原文 + char_range）＝關聯的逐字證據。
    回 [(sent_id, sentence, char_start, char_end)]。這是「答案 trace 逐字原文」命門的落地（#1）。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            "SELECT s.sent_id, s.sentence, s.char_start, s.char_end "
            "FROM knowledge_concordance ca "
            "JOIN knowledge_concordance cb ON cb.sent_id=ca.sent_id AND cb.term=%s AND cb.language=%s "
            "JOIN knowledge_sentence s ON s.sent_id=ca.sent_id "
            "WHERE ca.term=%s AND ca.language=%s "
            "ORDER BY s.sent_id LIMIT %s",
            (term_b, language, term_a, language, limit))
        return [(int(sid), sent, cs, ce) for sid, sent, cs, ce in cur.fetchall()]


def term_coverage(term, language="zh"):
    """某詞在 L6 圖的 coverage 誠實旗標（#15：分清「無關聯」vs「語料未涵蓋」）。
    回 {in_vocab, n_edges, in_corpus_stats}——in_vocab=False 表『未進 stat_vocab、無法成邊』（非『無關聯』）。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM knowledge_term_affinity WHERE term_a=%s AND language=%s", (term, language))
        n_edges = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM knowledge_term_corpus_stats WHERE term=%s AND language=%s", (term, language))
        in_corpus = cur.fetchone()[0] > 0
        return {"term": term, "in_vocab": n_edges > 0, "n_edges": n_edges, "in_corpus_stats": in_corpus}
