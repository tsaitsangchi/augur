"""P3 混合檢索 API — 語義 kNN + verbatim 逐字子字串回查、逐字可溯源引用。

🎯 哲學素養框架 L2 知識檢索層核心(學習計畫 P3):給查詢 → e5-small 嵌入 → pgvector cosine kNN
   → 回逐字 chunk + Citation(work/thinker/chapter/char_range/source_url),供顧問引經據典。
   只回 DB 既存逐字字串、溯源三元組強制、verbatim 子字串存在性回查閘防「潤飾原文」。
   L5 擴充(text 計畫 v1.6):lexicon_lookup(公版辭書/註疏定義)+ concordance_lookup(逐字用例);
   N7 擴充(e2e 計畫 §3-S7):雙側檢索——retrieve_items(items 側文獻句;CLEAN_ITEM 閘=corpus SSOT;
   讀路徑=textnorm 全形集→exact SQL 零向量優先→ANN 補位→一律 PG JOIN 取原文)+
   verify_verbatim 雙側分派(item 側=item_text substring(FROM char_start+1) 定位他證)。
   L2/L3 表未建或庫無此詞 → 誠實回空 [](誠實率 100% 機制,配 advisor.guard 固定誠實句)。
守 #1(只回逐字原文、不生成不改寫)· #28(本地嵌入、零 LLM API)·
   憲章 v1.17.0(檢索層對預測表零寫入、與預測管線物理隔離)· #18。
"""
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from itertools import zip_longest

from augur.core import db
from augur.knowledge import corpus, embedspec, textnorm


@dataclass
class Citation:
    """一筆逐字可溯源的哲學引用。"""
    chunk_id: int
    work_id: int
    work_title: str
    thinker: str
    chapter: str
    char_start: int
    char_end: int
    source_url: str
    text: str        # 逐字原文(== work_text.content[char_start:char_end])
    score: float     # cosine 相似度(0~1)


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(embedspec.MODEL_TAG, device=embedspec.QUERY_DEVICE)


def _query_vec(query):
    emb = _model().encode(["query: " + query], normalize_embeddings=True)[0]
    return "[" + ",".join(f"{x:.6f}" for x in emb) + "]"


def retrieve(query, k=8, work_id=None):
    """語義檢索;回 [Citation](逐字可溯源、按相似度降序)。work_id 可限縮單一著作。"""
    qv = _query_vec(query)
    where = "WHERE c.work_id = %s" if work_id else ""
    sql = f"""
    SELECT c.chunk_id, c.work_id, COALESCE(w.title_zh, w.title), th.name_zh,
           t.chapter, c.char_start, c.char_end, t.source_url, c.content,
           1 - (e.embedding <=> %s::vector) AS score
    FROM philosophy_chunk_embedding e
    JOIN philosophy_chunk c USING(chunk_id)
    JOIN philosophy_work w USING(work_id)
    JOIN philosophy_thinker th ON th.thinker_id = w.thinker_id
    JOIN philosophy_work_text t ON t.text_id = c.text_id
    {where}
    ORDER BY e.embedding <=> %s::vector
    LIMIT %s
    """
    params = [qv] + ([work_id] if work_id else []) + [qv, k]
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(sql, params)
        for r in cur.fetchall():
            out.append(Citation(chunk_id=r[0], work_id=r[1], work_title=r[2], thinker=r[3],
                                chapter=r[4], char_start=r[5], char_end=r[6], source_url=r[7],
                                text=r[8], score=float(r[9])))
    return out


def verify_verbatim(citation):
    """verbatim 逐字回查(雙側分派;M2 注入後驗共用單一入口):
    Citation(work chunk)=原文子字串存在性比對;ItemCitation=item_text 定位他證。回 bool。"""
    if isinstance(citation, ItemCitation):
        return verify_verbatim_item(citation)
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT t.content FROM philosophy_work_text t "
                    "JOIN philosophy_chunk c ON c.text_id = t.text_id WHERE c.chunk_id = %s",
                    (citation.chunk_id,))
        row = cur.fetchone()
        return bool(row) and citation.text in row[0]


@dataclass
class LexEntry:
    """一則公版辭書/註疏定義(L3,逐字、可溯源)。"""
    term: str            # 正規化詞形(JOIN 鍵,契約 SSOT=augur.knowledge.textnorm)
    term_display: str    # 原詞條形(繁簡/大小寫原貌)
    language: str
    definition: str      # 逐字定義原文(公版來源,無 AI 改寫)
    work_title: str      # 出處著作(philosophy_work)
    source_locator: str  # 卷/部首/頁碼(引用必附,見 advisor.guard)
    lex_type: str        # dictionary/commentary/thesaurus


@dataclass
class ConcordanceHit:
    """一處逐字用例(L2:knowledge_concordance → knowledge_sentence 回句)。"""
    term: str
    sentence: str        # 逐字原句
    char_start: int      # 相對來源 content 之 char_range(逐字回溯)
    char_end: int
    source_title: str    # work 或 item 標題
    sent_id: int
    position: int


def _tables_exist(cur, *names):
    cur.execute("SELECT " + ", ".join("to_regclass(%s)" for _ in names), names)
    return all(cur.fetchone())


def _term_forms(term):
    """查詢詞形集合(去重保序):NFC 原形 + 小寫 + textnorm 正規形(zh 原貌/en Porter stem),
    履行三方 JOIN 契約(SSOT=augur.knowledge.textnorm);空詞回 []。"""
    t = unicodedata.normalize("NFC", (term or "").strip())
    if not t:
        return []
    forms = [t, t.lower(), textnorm.norm_headword(t, "zh"), textnorm.norm_headword(t, "en")]
    return list(dict.fromkeys(f for f in forms if f))


def lexicon_lookup(term):
    """辭書/註疏定義查詢(L3→L5):回 [LexEntry](逐字定義+出處+locator)。
    庫無此詞或 knowledge_lexicon 未建 → 誠實回空 [](不生成、不猜)。"""
    forms = _term_forms(term)
    if not forms:
        return []
    ph = ", ".join("%s" for _ in forms)
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        if not _tables_exist(cur, "knowledge_lexicon"):
            return []
        cur.execute(f"""
        SELECT l.term, l.term_display, l.language, l.definition,
               COALESCE(w.title_zh, w.title), l.source_locator, l.lex_type
        FROM knowledge_lexicon l
        JOIN philosophy_work w ON w.work_id = l.source_work_id
        WHERE l.term IN ({ph}) OR l.term_display IN ({ph})
        ORDER BY l.lex_type, l.lex_id
        """, (*forms, *forms))
        for r in cur.fetchall():
            out.append(LexEntry(term=r[0], term_display=r[1], language=r[2], definition=r[3],
                                work_title=r[4], source_locator=r[5], lex_type=r[6]))
    return out


def concordance_lookup(term, limit=10):
    """逐字用例查詢(L2→L5):回 [ConcordanceHit](原句+char_range+work/item 標題)。
    庫無此詞或 L2 表未建 → 誠實回空 []。"""
    forms = _term_forms(term)
    if not forms:
        return []
    ph = ", ".join("%s" for _ in forms)
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        if not _tables_exist(cur, "knowledge_concordance", "knowledge_sentence",
                             "knowledge_item_text", "knowledge_item"):
            return []
        cur.execute(f"""
        SELECT c.term, s.sentence, s.char_start, s.char_end,
               COALESCE(w.title_zh, w.title, i.title_zh, i.title, '') AS source_title,
               s.sent_id, c.position
        FROM knowledge_concordance c
        JOIN knowledge_sentence s ON s.sent_id = c.sent_id
        LEFT JOIN philosophy_work_text wt ON wt.text_id = s.text_id
        LEFT JOIN philosophy_work w ON w.work_id = wt.work_id
        LEFT JOIN knowledge_item_text x ON x.itext_id = s.itext_id
        LEFT JOIN knowledge_item i ON i.item_id = x.item_id
        WHERE c.term IN ({ph})
        ORDER BY s.sent_id, c.position
        LIMIT %s
        """, (*forms, limit))
        for r in cur.fetchall():
            out.append(ConcordanceHit(term=r[0], sentence=r[1], char_start=r[2], char_end=r[3],
                                      source_title=r[4], sent_id=r[5], position=r[6]))
    return out


# ── items 側(N7,e2e 計畫 §3-S7)──────────────────────────────────────────────

@dataclass
class ItemCitation:
    """一筆逐字可溯源的知識文獻句引用(items 側)。"""
    sent_id: int
    itext_id: int
    item_id: int
    item_title: str
    domain: str
    entity_type: str
    char_start: int      # 相對 item_text.content 之定位(verify_verbatim_item 他證基準)
    char_end: int
    source_url: str
    license: str
    text: str            # 逐字原句(== item_text.content[char_start:char_end])
    score: float         # via='exact':查詢詞命中比(counts 類);via='ann':cosine 相似度
    via: str             # 'exact' | 'ann'


_ITEM_COLS = """s.sent_id, s.itext_id, i.item_id, COALESCE(i.title_zh, i.title), i.domain,
           i.entity_type, s.char_start, s.char_end, x.source_url, x.license, s.sentence"""
_ITEM_JOIN = """FROM knowledge_sentence s
        JOIN knowledge_item_text x ON x.itext_id = s.itext_id
        JOIN knowledge_item i ON i.item_id = x.item_id"""


def _guess_language(text):
    """查詢語言判定(確定性、零 ML):含 CJK 即 zh,否則 en。"""
    return "zh" if any("一" <= ch <= "鿿" for ch in text or "") else "en"


def _item_citations(cur, where, params, order, scores, via):
    cur.execute(f"SELECT {_ITEM_COLS} {_ITEM_JOIN} WHERE {where} ORDER BY {order}", params)
    return [ItemCitation(sent_id=r[0], itext_id=r[1], item_id=r[2], item_title=r[3], domain=r[4],
                         entity_type=r[5], char_start=r[6], char_end=r[7], source_url=r[8],
                         license=r[9], text=r[10], score=scores[r[0]], via=via)
            for r in cur.fetchall()]


def retrieve_items(query, k=8, domain=None, language=None, access_scope="public"):
    """items 側檢索(讀路徑鐵則 §3-S7):query→textnorm 全形集→(a)exact SQL 零向量優先
    →(c)ANN 補位→一律 PG JOIN 取原文;CLEAN_ITEM 閘=corpus SSOT(fail-closed,NULL 不放行)。
    (b) affinity 確定性擴展與 vectorindex(Milvus) 為既定接縫待 N3 接線,ANN 現由 pgvector(SSOT 索引)承。
    access_scope='public'(預設,對外對話;local_private 本機檔不入,拍板P2 機器保證);admin 私有可傳其值。
    語料空/表未建 → 誠實回空 []。回 [ItemCitation](exact 先、ann 補位)。"""
    if not (query or "").strip():
        return []
    clean = corpus.clean_item_sql("i", "x", access_scope=access_scope)
    extra, extra_params = "", []
    if domain:
        extra += " AND i.domain = %s"; extra_params.append(domain)
    if language:
        extra += " AND s.language = %s"; extra_params.append(language)
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        if not _tables_exist(cur, "knowledge_item", "knowledge_item_text", "knowledge_sentence"):
            return []
        terms = list({t for t, _ in textnorm.tokenize(query, language or _guess_language(query))})
        if terms and _tables_exist(cur, "knowledge_concordance"):
            cur.execute(f"""SELECT c.sent_id, count(DISTINCT c.term) AS n
                FROM knowledge_concordance c
                JOIN knowledge_sentence s ON s.sent_id = c.sent_id
                JOIN knowledge_item_text x ON x.itext_id = s.itext_id
                JOIN knowledge_item i ON i.item_id = x.item_id
                WHERE c.term = ANY(%s) AND {clean}{extra}
                GROUP BY c.sent_id ORDER BY n DESC, c.sent_id LIMIT %s""",
                        (terms, *extra_params, k))
            scores = {sid: n / len(terms) for sid, n in cur.fetchall()}
            if scores:
                out = _item_citations(cur, f"s.sent_id = ANY(%s) AND {clean}",
                                      (list(scores), ), "s.sent_id", scores, "exact")
                out.sort(key=lambda c: (-c.score, c.sent_id))
        need = k - len(out)
        if need > 0 and _tables_exist(cur, "knowledge_sentence_embedding"):
            cur.execute("SELECT 1 FROM knowledge_sentence_embedding e "
                        "JOIN knowledge_sentence s USING (sent_id) WHERE s.itext_id IS NOT NULL LIMIT 1")
            if cur.fetchone():   # 零向量優先:items 側無嵌入=不載模型(#28)
                qv = _query_vec(query)
                seen = [c.sent_id for c in out]
                dedup = " AND s.sent_id != ALL(%s)" if seen else ""
                cur.execute(f"""SELECT {_ITEM_COLS}, 1 - (e.embedding <=> %s::vector) AS score
                    {_ITEM_JOIN}
                    JOIN knowledge_sentence_embedding e ON e.sent_id = s.sent_id
                    WHERE e.model_tag = %s AND {clean}{extra}{dedup}
                    ORDER BY e.embedding <=> %s::vector LIMIT %s""",
                            (qv, embedspec.MODEL_TAG, *extra_params, *([seen] if seen else []), qv, need))
                for r in cur.fetchall():
                    out.append(ItemCitation(sent_id=r[0], itext_id=r[1], item_id=r[2], item_title=r[3],
                                            domain=r[4], entity_type=r[5], char_start=r[6], char_end=r[7],
                                            source_url=r[8], license=r[9], text=r[10],
                                            score=float(r[11]), via="ann"))
    return out


def retrieve_all(query, k=6, access_scope="public"):
    """work(哲學/文學語料)+ item(知識/財經/本機檔)合併檢索 — 死點① 接線(計畫 §三)。
    對話端唯一組合檢索器:兩側各取半、交錯合併(均露臉、財經知識不被哲學語料淹沒)、cap k;
    回混合 [Citation|ItemCitation](均含 .text/.char_start/.char_end/.source_url,verify_verbatim 型別感知、
    prompt/guard 已 getattr 相容)。access_scope='public' 對外(local_private 不入,拍板P2)。"""
    half = max(2, (k + 1) // 2)
    works = retrieve(query, k=half)
    items = retrieve_items(query, k=half, access_scope=access_scope)
    merged = [c for pair in zip_longest(works, items) for c in pair if c is not None]
    return merged[:k]

def verify_verbatim_item(citation):
    """item_text 定位基準他證(§3-S7):citation.text 須==content 之 substring(FROM char_start+1
    FOR char_end-char_start)——位置+內容雙重驗證,嚴於子字串存在性(防 char_range 錯位/潤飾)。回 bool。"""
    n = citation.char_end - citation.char_start
    if n <= 0:
        return False
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT substring(content FROM %s + 1 FOR %s) FROM knowledge_item_text WHERE itext_id = %s",
                    (citation.char_start, n, citation.itext_id))
        row = cur.fetchone()
        return bool(row) and row[0] == citation.text
