"""P3 混合檢索 API — 語義 kNN + pg_trgm 逐字回查、逐字可溯源引用。

🎯 哲學素養框架 L2 知識檢索層核心(學習計畫 P3):給查詢 → e5-small 嵌入 → pgvector cosine kNN
   → 回逐字 chunk + Citation(work/thinker/chapter/char_range/source_url),供顧問引經據典。
   只回 DB 既存逐字字串、溯源三元組強制、pg_trgm 存在性回查閘防「潤飾原文」。
守 #1(只回逐字原文、不生成不改寫)· #28(本地嵌入、零 LLM API)·
   憲章 v1.17.0(檢索層對預測表零寫入、與預測管線物理隔離)· #18。
"""
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
    """pg_trgm 逐字回查:確認 citation.text 原封不動存在於來源 work_text(防潤飾/改寫)。回 bool。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT t.content FROM philosophy_work_text t "
                    "JOIN philosophy_chunk c ON c.text_id = t.text_id WHERE c.chunk_id = %s",
                    (citation.chunk_id,))
        row = cur.fetchone()
        return bool(row) and citation.text in row[0]
