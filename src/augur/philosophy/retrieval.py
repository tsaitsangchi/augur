"""P3 混合檢索 API — 語義 kNN + verbatim 逐字子字串回查、逐字可溯源引用。

🎯 哲學素養框架 L2 知識檢索層核心(學習計畫 P3):給查詢 → e5-small 嵌入 → pgvector cosine kNN
   → 回逐字 chunk + Citation(work/thinker/chapter/char_range/source_url),供顧問引經據典。
   只回 DB 既存逐字字串、溯源三元組強制、verbatim 子字串存在性回查閘防「潤飾原文」。
   L5 擴充(text 計畫 v1.6):lexicon_lookup(公版辭書/註疏定義)+ concordance_lookup(逐字用例);
   L2/L3 表未建或庫無此詞 → 誠實回空 [](誠實率 100% 機制,配 advisor.guard 固定誠實句)。
守 #1(只回逐字原文、不生成不改寫)· #28(本地嵌入、零 LLM API)·
   憲章 v1.17.0(檢索層對預測表零寫入、與預測管線物理隔離)· #18。
"""
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

from augur.core import db

MODEL = "intfloat/multilingual-e5-small"


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
    return SentenceTransformer(MODEL, device="cpu")


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
    """verbatim 逐字回查(DB 原文子字串比對):確認 citation.text 原封不動存在於來源 work_text(防潤飾/改寫)。回 bool。"""
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
    """查詢詞寬鬆形:NFC 原形 + 小寫(西文)。完整正規化契約(jieba/Porter)SSOT=augur.knowledge.textnorm,
    此處不重複實作 stemmer;呼叫端可先以 textnorm 正規化再查。"""
    t = unicodedata.normalize("NFC", (term or "").strip())
    return t, t.lower()


def lexicon_lookup(term):
    """辭書/註疏定義查詢(L3→L5):回 [LexEntry](逐字定義+出處+locator)。
    庫無此詞或 knowledge_lexicon 未建 → 誠實回空 [](不生成、不猜)。"""
    t, tl = _term_forms(term)
    if not t:
        return []
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        if not _tables_exist(cur, "knowledge_lexicon"):
            return []
        cur.execute("""
        SELECT l.term, l.term_display, l.language, l.definition,
               COALESCE(w.title_zh, w.title), l.source_locator, l.lex_type
        FROM knowledge_lexicon l
        JOIN philosophy_work w ON w.work_id = l.source_work_id
        WHERE l.term IN (%s, %s) OR l.term_display IN (%s, %s)
        ORDER BY l.lex_type, l.lex_id
        """, (t, tl, t, tl))
        for r in cur.fetchall():
            out.append(LexEntry(term=r[0], term_display=r[1], language=r[2], definition=r[3],
                                work_title=r[4], source_locator=r[5], lex_type=r[6]))
    return out


def concordance_lookup(term, limit=10):
    """逐字用例查詢(L2→L5):回 [ConcordanceHit](原句+char_range+work/item 標題)。
    庫無此詞或 L2 表未建 → 誠實回空 []。"""
    t, tl = _term_forms(term)
    if not t:
        return []
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        if not _tables_exist(cur, "knowledge_concordance", "knowledge_sentence",
                             "knowledge_item_text", "knowledge_item"):
            return []
        cur.execute("""
        SELECT c.term, s.sentence, s.char_start, s.char_end,
               COALESCE(w.title_zh, w.title, i.title_zh, i.title, '') AS source_title,
               s.sent_id, c.position
        FROM knowledge_concordance c
        JOIN knowledge_sentence s ON s.sent_id = c.sent_id
        LEFT JOIN philosophy_work_text wt ON wt.text_id = s.text_id
        LEFT JOIN philosophy_work w ON w.work_id = wt.work_id
        LEFT JOIN knowledge_item_text x ON x.itext_id = s.itext_id
        LEFT JOIN knowledge_item i ON i.item_id = x.item_id
        WHERE c.term IN (%s, %s)
        ORDER BY s.sent_id, c.position
        LIMIT %s
        """, (t, tl, limit))
        for r in cur.fetchall():
            out.append(ConcordanceHit(term=r[0], sentence=r[1], char_start=r[2], char_end=r[3],
                                      source_title=r[4], sent_id=r[5], position=r[6]))
    return out
