#!/usr/bin/env python
"""P2 本地嵌入 — philosophy_chunk → philosophy_chunk_embedding(bge-m3 CPU、檢索用向量)。

🎯 為每個 chunk 產生檢索用向量(bge-m3 多語 1024 維、CPU、normalize),存 pgvector + HNSW 索引。
   L2 知識檢索層基建(學習計畫 P2)。增量只跑未嵌入塊、每 batch commit(#6 resume-safe)。
守 #1(embedding 是檢索用數值指紋、非真兆、絕不進 feature/預測管線)· #28(本地 CPU、零 LLM API)·
   #22(長跑 resume-safe)· #18。model_tag 供重嵌溯源。

執行指令矩陣:python scripts/embed_philosophy_chunks.py [--limit N] [--smoke]
"""
import sys
import time

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

MODEL = "intfloat/multilingual-e5-small"   # 多語(含 CJK)、384 維、CPU 快;bge-m3 CPU 53.7h 太久(D2)
DIM = 384
BATCH = 64

DDL = f"""
CREATE TABLE IF NOT EXISTS philosophy_chunk_embedding (
  chunk_id  INT PRIMARY KEY REFERENCES philosophy_chunk(chunk_id) ON DELETE CASCADE,
  embedding vector({DIM}) NOT NULL,
  model_tag VARCHAR(64) NOT NULL
);
"""


def vec_literal(emb):
    return "[" + ",".join(f"{x:.6f}" for x in emb) + "]"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    smoke = "--smoke" in sys.argv
    from sentence_transformers import SentenceTransformer
    t0 = time.time()
    model = SentenceTransformer(MODEL, device="cpu")
    print(f"模型載入 {time.time()-t0:.1f}s", flush=True)

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            if "--reset" in sys.argv:
                cur.execute("DROP TABLE IF EXISTS philosophy_chunk_embedding")
            cur.execute(DDL)
            q = ("SELECT chunk_id, content FROM philosophy_chunk "
                 "WHERE chunk_id NOT IN (SELECT chunk_id FROM philosophy_chunk_embedding) ORDER BY chunk_id")
            if limit:
                q += f" LIMIT {limit}"
            cur.execute(q)
            todo = cur.fetchall()
        print(f"待嵌入 {len(todo):,} 塊", flush=True)
        te = time.time()
        for i in range(0, len(todo), BATCH):
            batch = todo[i:i + BATCH]
            embs = model.encode(["passage: " + c for _, c in batch], normalize_embeddings=True, batch_size=BATCH)
            with db.transaction(conn) as cur:
                for (cid, _), emb in zip(batch, embs):
                    cur.execute("INSERT INTO philosophy_chunk_embedding (chunk_id,embedding,model_tag) "
                                "VALUES (%s,%s,%s) ON CONFLICT (chunk_id) DO NOTHING", (cid, vec_literal(emb), MODEL))
            if i % (BATCH * 20) == 0 and i:
                rate = (i) / (time.time() - te)
                print(f"  {i:,}/{len(todo):,}  {rate:.1f} 塊/s  剩 ~{(len(todo)-i)/rate/60:.0f} min", flush=True)
        dur = time.time() - te
        if todo and not smoke:
            with db.transaction(conn) as cur:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunk_emb_hnsw ON philosophy_chunk_embedding "
                            "USING hnsw (embedding vector_cosine_ops)")
        with db.transaction(conn) as cur:
            cur.execute("SELECT count(*) FROM philosophy_chunk_embedding")
            done = cur.fetchone()[0]
    if todo:
        print(f"✓ 本次嵌入 {len(todo):,} 塊 / {dur:.0f}s = {len(todo)/dur:.1f} 塊/s;累計 {done:,} 塊", flush=True)
        if smoke:
            total = 77318
            print(f"  [smoke] 全量 {total:,} 塊估時 ~{total/(len(todo)/dur)/3600:.1f} 小時", flush=True)
    else:
        print(f"✓ 已全部嵌入、累計 {done:,} 塊", flush=True)


if __name__ == "__main__":
    main()
