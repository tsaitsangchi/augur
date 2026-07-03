#!/usr/bin/env python
"""三粒度知識嵌入引擎 — lexicon 定義級 / sentence 句級 → pgvector(e5-small,增量游標)。

🎯 這支在做什麼(白話):把逐字定義(knowledge_lexicon)與原典句(knowledge_sentence)嵌入向量庫,
   與既有 chunk 嵌入成三粒度分工(定義級=這字什麼意思/句級=哪句講到/段落級=論證脈絡)。
   分表(HNSW post-filter 陷阱實測)、build_meta 游標增量、灌完才建 HNSW。
守 v2.0 命門7(嵌入=索引非內容,嵌的都是真兆原文)· W1 述詞(review_flag=false fail-closed)·
   junk 過濾分語言(zh 短句=真訓詁不得剔)· #15(每期首千列實測重投影、排除計數誠實印)· #29。

執行指令矩陣:
  python scripts/embed_knowledge.py                          # 無參數:各層待嵌統計+用法
  python scripts/embed_knowledge.py --layer lexicon --smoke  # 10 筆煙測
  python scripts/embed_knowledge.py --layer lexicon          # p0 全量(~155k 條,估 5-6h)
  python scripts/embed_knowledge.py --layer sentence --language zh   # p1 zh 句(~29k 句)
  python scripts/embed_knowledge.py --layer sentence --language en --limit 100000  # en 子集(拍板 C)
  python scripts/embed_knowledge.py --build-index            # 灌完後建 HNSW(前置調 maintenance_work_mem)
"""
import re
import sys
import argparse

import _bootstrap  # noqa: F401
from augur.core import db

MODEL_TAG = "intfloat/multilingual-e5-small"
BATCH = 64

DDL = """
CREATE TABLE IF NOT EXISTS knowledge_lexicon_embedding (
  lex_id INT PRIMARY KEY REFERENCES knowledge_lexicon(lex_id) ON DELETE CASCADE,
  embedding vector(384) NOT NULL, model_tag VARCHAR(64) NOT NULL);
CREATE TABLE IF NOT EXISTS knowledge_sentence_embedding (
  sent_id INT PRIMARY KEY REFERENCES knowledge_sentence(sent_id) ON DELETE CASCADE,
  embedding vector(384) NOT NULL, model_tag VARCHAR(64) NOT NULL);
INSERT INTO knowledge_build_meta (scope, cursor_sent_id) VALUES
  ('embed_lexicon', 0), ('embed_sentence_zh', 0), ('embed_sentence_en', 0)
  ON CONFLICT (scope) DO NOTHING;
"""

_SYMBOL_ONLY = re.compile(r"^[\W_]+$")


def is_junk(sentence, language):
    """junk 分語言(v2.0 guard:zh 短句=真訓詁「翕,盛貌。」不得剔)。"""
    if _SYMBOL_ONLY.match(sentence or ""):
        return True
    if language == "en" and (len(sentence) < 10 or len(sentence) > 1000):
        return True
    return False


def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_TAG)


def fetch_batch(cur, layer, language, cursor, n=2000):
    if layer == "lexicon":
        cur.execute("""SELECT l.lex_id, COALESCE(l.term_display, l.term), left(l.definition, 1000)
            FROM knowledge_lexicon l JOIN philosophy_work w ON w.work_id = l.source_work_id
            WHERE w.review_flag = false AND l.lex_id > %s ORDER BY l.lex_id LIMIT %s""", (cursor, n))
        return [(r[0], f"passage: {r[1]}: {r[2]}") for r in cur.fetchall()]
    cur.execute("""SELECT s.sent_id, s.sentence FROM knowledge_sentence s
        LEFT JOIN philosophy_work_text t ON t.text_id = s.text_id
        LEFT JOIN philosophy_work w ON w.work_id = t.work_id
        WHERE s.language = %s AND (s.text_id IS NULL OR w.review_flag = false)
          AND s.sent_id > %s ORDER BY s.sent_id LIMIT %s""", (language, cursor, n))
    return [(r[0], r[1]) for r in cur.fetchall()]


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--layer"); ap.add_argument("--language", default="zh")
    ap.add_argument("--limit", type=int); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--build-index", action="store_true", dest="build_index")
    args, _ = ap.parse_known_args()
    import time
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute(DDL)
        if args.build_index:
            with db.transaction(conn) as cur:
                cur.execute("SET maintenance_work_mem = '2GB'")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_lex_emb_hnsw ON knowledge_lexicon_embedding USING hnsw (embedding vector_cosine_ops)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_sent_emb_hnsw ON knowledge_sentence_embedding USING hnsw (embedding vector_cosine_ops)")
            print("HNSW 兩索引建置完成")
            return
        if not args.layer:
            print(__doc__.split("執行指令矩陣:")[1])
            with db.transaction(conn) as cur:
                for scope, q in [("lexicon", "SELECT count(*) FROM knowledge_lexicon"),
                                 ("sentence zh", "SELECT count(*) FROM knowledge_sentence WHERE language='zh'"),
                                 ("sentence en", "SELECT count(*) FROM knowledge_sentence WHERE language='en'")]:
                    cur.execute(q); total = cur.fetchone()[0]
                    t = "knowledge_lexicon_embedding" if scope == "lexicon" else "knowledge_sentence_embedding"
                    cur.execute(f"SELECT count(*) FROM {t}")
                    print(f"  {scope:12} 全量 {total:>9,} / 已嵌 {cur.fetchone()[0]:,}")
            return
        scope = "embed_lexicon" if args.layer == "lexicon" else f"embed_sentence_{args.language}"
        table, idcol = (("knowledge_lexicon_embedding", "lex_id") if args.layer == "lexicon"
                        else ("knowledge_sentence_embedding", "sent_id"))
        model = load_model()
        done = skipped = 0
        t0 = time.time()
        limit = 10 if args.smoke else (args.limit or 10**9)
        while done < limit:
            with db.transaction(conn) as cur:
                cur.execute("SELECT cursor_sent_id FROM knowledge_build_meta WHERE scope=%s", (scope,))
                cursor = cur.fetchone()[0]
                rows = fetch_batch(cur, args.layer, args.language, cursor, min(2000, limit - done))
            if not rows:
                break
            keep = [(i, tx) for i, tx in rows
                    if args.layer == "lexicon" or not is_junk(tx, args.language)]
            skipped += len(rows) - len(keep)
            texts = [tx if tx.startswith("passage: ") else f"passage: {tx}" for _, tx in keep]
            if texts:
                vecs = model.encode(texts, batch_size=BATCH, normalize_embeddings=True, show_progress_bar=False)
                with db.transaction(conn) as cur:
                    for (rid, _), v in zip(keep, vecs):
                        cur.execute(f"INSERT INTO {table} ({idcol}, embedding, model_tag) VALUES (%s,%s,%s) "
                                    "ON CONFLICT DO NOTHING", (rid, list(map(float, v)), MODEL_TAG))
            with db.transaction(conn) as cur:
                cur.execute("UPDATE knowledge_build_meta SET cursor_sent_id=%s, updated_at=now() WHERE scope=%s",
                            (rows[-1][0], scope))
            done += len(rows)
            if done <= 2000 or done % 10000 < 2000:
                rate = done / max(time.time() - t0, 1)
                print(f"  {scope}: {done:,} 筆(skip {skipped})、{rate:.1f} 筆/s(首千列實測重投影 #15)", flush=True)
        print(f"完成 {scope}: 處理 {done:,}、junk 排除 {skipped:,}(逐類誠實)、耗時 {(time.time()-t0)/60:.1f} 分", flush=True)


if __name__ == "__main__":
    main()
