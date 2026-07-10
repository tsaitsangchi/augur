#!/usr/bin/env python
"""Qdrant 影子評測 — pgvector(SSOT)vs Qdrant 候選端 top-k 重疊率,cutover 機械門檻(e2e P4/§6.7,D6)。

🎯 這支在做什麼(白話):cutover 前的機械守門——50 題確定性題集(seed 固定,可重現 A-32)同打兩端,
   量 top-10 sent_id 重疊率;mean ≥ 0.90(D6 門檻,數字可調)→ passed=true 落 vectorstore_shadow_eval
   → 才允許 UPDATE config 一列切 qdrant_server。**pgvector 永遠是 SSOT**(雙庫鐵則),影子只驗
   「可拋棄外部索引」是否忠實鏡射。

守 #10(題集 seed+逐題 overlap 落 detail 可重現)· #15(門檻機械、不達不切)· v1.40.0。
   前置=augur-qdrant unit 常駐+export_qdrant_index 匯出完成。

執行指令矩陣:
  python scripts/verify_qdrant_shadow.py                  # 無參數:印矩陣+上次評測(唯讀)
  python scripts/verify_qdrant_shadow.py --run            # 50 題×top10,落 vectorstore_shadow_eval
  python scripts/verify_qdrant_shadow.py --run --n 20 --k 10 --threshold 0.9
"""
import argparse
import hashlib
import json
import random
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.knowledge import embedspec
from augur.knowledge.vectorindex import CollectionSpec, QdrantIndex

SCOPE = "sentence_items"


def _queries(cur, n, seed=42):
    """確定性題集:自 items 側真實句子取樣(seed 固定→同題可重現;句長 40-160 過濾雜訊)。"""
    cur.execute("""SELECT s.sentence FROM knowledge_sentence s
                   WHERE s.itext_id IS NOT NULL AND s.language='en'
                     AND length(s.sentence) BETWEEN 40 AND 160
                   ORDER BY s.sent_id LIMIT 5000""")
    pool = [r[0] for r in cur.fetchall()]
    rng = random.Random(seed)
    return rng.sample(pool, min(n, len(pool))), seed


def _pg_topk(cur, qv, k):
    """pgvector 參照端 top-k——謂詞**完全鏡射 export**(#12 同一 CLEAN 口徑,否則假對帳):
    en + itext 鏈 + clean_item_sql(license 白名單∧entity_type∧access_scope='public')。"""
    from augur.knowledge import corpus
    cfrag, cparams = corpus.clean_item_sql("i", "x", access_scope="public", is_super=True)
    cur.execute(f"""SELECT e.sent_id FROM knowledge_sentence_embedding e
                   JOIN knowledge_sentence s USING (sent_id)
                   JOIN knowledge_item_text x ON x.itext_id = s.itext_id
                   JOIN knowledge_item i ON i.item_id = x.item_id
                   WHERE s.itext_id IS NOT NULL AND s.language='en' AND e.model_tag=%s AND {cfrag}
                   ORDER BY e.embedding <=> %s::vector LIMIT %s""",
                (embedspec.MODEL_TAG, *cparams, qv, k))
    return [r[0] for r in cur.fetchall()]


def run(n, k, threshold, url):
    from augur.philosophy.retrieval import _query_vec
    idx = QdrantIndex(url=url)
    coll = embedspec.collection_name("sentence", "items")
    idx.ensure_collection(CollectionSpec(name=coll, dim=embedspec.dim_for()))   # 綁定既有 collection(不 rebuild)
    overlaps, detail = [], []
    with db.connect() as conn, db.transaction(conn) as cur:
        qs, seed = _queries(cur, n)
        for q in qs:
            qv = _query_vec(q)
            pg = set(_pg_topk(cur, qv, k))
            qd = {int(h[0]) for h in idx.search([float(v) for v in qv.strip("[]").split(",")], k)}
            ov = len(pg & qd) / k
            overlaps.append(ov)
            detail.append({"q": q[:60], "overlap": ov})
        mean_ov = sum(overlaps) / len(overlaps)
        min_ov = min(overlaps)
        passed = mean_ov >= threshold
        cur.execute("""INSERT INTO vectorstore_shadow_eval
                       (scope, backend_ref, backend_cand, n_queries, top_k, mean_overlap, min_overlap,
                        threshold, passed, detail)
                       VALUES (%s,'pgvector','qdrant_server',%s,%s,%s,%s,%s,%s,%s)""",
                    (SCOPE, len(qs), k, round(mean_ov, 4), round(min_ov, 4), threshold, passed,
                     json.dumps({"seed": seed, "queries_sha": hashlib.sha256(
                         "".join(q for q in qs).encode()).hexdigest()[:16], "per_query": detail},
                         ensure_ascii=False)))
        conn.commit()
    print(f"mean_overlap={mean_ov:.4f} min={min_ov:.4f} threshold={threshold} → "
          f"{'✓ PASSED(可 cutover:UPDATE config 一列)' if passed else '✗ FAILED(不切;查索引/匯出)'}")
    return 0 if passed else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--threshold", type=float, default=0.90)
    ap.add_argument("--url", default="http://127.0.0.1:6333")
    args = ap.parse_args()
    if args.run:
        return run(args.n, args.k, args.threshold, args.url)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT run_at::timestamp(0), mean_overlap, passed FROM vectorstore_shadow_eval "
                    "ORDER BY run_at DESC LIMIT 3")
        for r in cur.fetchall():
            print(f"  {r[0]} mean={r[1]} passed={r[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
