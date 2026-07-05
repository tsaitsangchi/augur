#!/usr/bin/env python
"""三粒度知識嵌入引擎 — lexicon 定義級 / sentence 句級(works|items 分側) → pgvector(增量游標)。

🎯 這支在做什麼(白話):把逐字定義(knowledge_lexicon)與原典/文獻句(knowledge_sentence)嵌入
   向量庫,與既有 chunk 嵌入成三粒度分工(定義級/句級/段落級)。M1 四改(e2e 計畫 §3-S5):
   (a) CLEAN 閘=corpus SSOT — works 側 review_flag=false;items 側 license×entity_type
       fail-closed(entity_type 准入=P4 建議值,用戶拍板前不得對 items 側放量嵌入)
   (b) scope 分側 embed_sentence_{works|items}_{lang} — items 不吞 1.5M 工作側 en 債(P7);
       禁手撥游標(毀「嵌入數+排除數=來源數」機器等式)
   (c) 模型規格=embedspec SSOT+--model 旗標(換模走 SOP-A,未登記 tag=錯得大聲)
   (d) 嵌入表複合鍵相容(P6):PK 世代自動偵測;單欄 PK+異 tag=停手不靜默;整跑 0 新列=exit 1
       (SOP-A ③ 防呆);排除帳落庫 knowledge_embed_ledger 非 stdout
   DDL 單一住所=migrate_text_understanding_ddl.py(本支只讀 schema、不建表,#12)。
守 命門7(嵌入=索引非內容,嵌的都是真兆原文)· #1/#12/#15 · junk 分語言(zh 短句=真訓詁不得剔)· #29。

執行指令矩陣:
  python scripts/embed_knowledge.py                                  # 無參數:各層/各側待嵌統計(唯讀)
  python scripts/embed_knowledge.py --layer lexicon --smoke          # 10 筆煙測
  python scripts/embed_knowledge.py --layer sentence --language zh   # works 側 zh(預設 scope=works)
  python scripts/embed_knowledge.py --layer sentence --language en --scope items --limit 1000 --smoke
  python scripts/embed_knowledge.py --layer sentence --language en --scope items   # items 側(P4 拍板後)
  python scripts/embed_knowledge.py --layer sentence --scope items --model <tag>   # 換模(P6 遷移後,SOP-A)
  python scripts/embed_knowledge.py --build-index                    # 灌完後建 HNSW
"""
import re
import sys
import argparse

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import corpus, embedspec

BATCH = 64
PASSAGE_PREFIX = "passage: "   # e5 系嵌庫端前綴(查詢端 "query: " 在 philosophy/retrieval)

_SYMBOL_ONLY = re.compile(r"^[\W_]+$")


def is_junk(sentence, language):
    """junk 分語言(v2.0 guard:zh 短句=真訓詁「翕,盛貌。」不得剔)。"""
    if _SYMBOL_ONLY.match(sentence or ""):
        return True
    if language == "en" and (len(sentence) < 10 or len(sentence) > 1000):
        return True
    return False


def load_model(model_tag):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_tag)


def precheck(cur, need_ledger=False):
    """schema 先決(DDL 單一住所=migrate_text_understanding_ddl.py,本支不建表)。"""
    tables = ["knowledge_lexicon_embedding", "knowledge_sentence_embedding", "knowledge_build_meta"]
    if need_ledger:
        tables.append("knowledge_embed_ledger")
    cur.execute("SELECT " + ", ".join("to_regclass(%s)" for _ in tables), tables)
    missing = [t for t, ok in zip(tables, cur.fetchone()) if not ok]
    if missing:
        sys.exit(f"schema 先決缺:{missing}(DDL 單一住所)→ 先跑 python scripts/migrate_text_understanding_ddl.py")


def _pk_cols(cur, table):
    cur.execute("""SELECT a.attname FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = to_regclass(%s) AND i.indisprimary""", (table,))
    return {r[0] for r in cur.fetchall()}


def resolve_write_target(cur, table, idcol, model_tag):
    """P6 複合鍵相容:回 ON CONFLICT 鍵;單欄 PK 世代+異 tag=停手(防 DO NOTHING 靜默零寫入假成功)。"""
    if "model_tag" in _pk_cols(cur, table):
        return f"{idcol}, model_tag"
    cur.execute(f"SELECT DISTINCT model_tag FROM {table} LIMIT 2")
    tags = [r[0] for r in cur.fetchall()]
    if tags and tags != [model_tag]:
        sys.exit(f"{table} 仍為單欄 PK 世代且既有 model_tag={tags} ≠ {model_tag!r}:"
                 "換模重嵌會靜默零寫入(SOP-A/P6)→ 先跑 python scripts/migrate_text_understanding_ddl.py")
    return idcol


def check_dim(cur, table, dim):
    """表維度(pgvector atttypmod=dim)須等於 embedspec 維度;異維模型=新表世代,不寫本表。"""
    cur.execute("SELECT atttypmod FROM pg_attribute WHERE attrelid = to_regclass(%s) AND attname = 'embedding'",
                (table,))
    row = cur.fetchone()
    table_dim = row[0] if row else -1
    if table_dim > 0 and table_dim != dim:
        sys.exit(f"{table} 維度 {table_dim} ≠ 模型維度 {dim}:異維模型=新表世代(embedspec 命名,P6),停手")


def ensure_scope(cur, scope, layer, side, language):
    """游標種子(冪等)。works 側繼承 legacy embed_sentence_{lang} 游標=機器遷移非手撥
    (legacy 述詞時代 item 句=0,DB 實查 2026-07-04,故 legacy 游標全屬 works 側)。"""
    if layer == "sentence" and side == "works":
        cur.execute("""INSERT INTO knowledge_build_meta (scope, cursor_sent_id)
            SELECT %s, COALESCE((SELECT cursor_sent_id FROM knowledge_build_meta WHERE scope = %s), 0)
            ON CONFLICT (scope) DO NOTHING""", (scope, f"embed_sentence_{language}"))
    else:
        cur.execute("INSERT INTO knowledge_build_meta (scope, cursor_sent_id) VALUES (%s, 0) "
                    "ON CONFLICT (scope) DO NOTHING", (scope,))


def fetch_batch(cur, layer, language, side, cursor, n=2000):
    """CLEAN 閘=corpus SSOT(三端同閘;fail-closed,NULL 不放行)。"""
    if layer == "lexicon":
        cur.execute(f"""SELECT l.lex_id, COALESCE(l.term_display, l.term), left(l.definition, 1000)
            FROM knowledge_lexicon l JOIN philosophy_work w ON w.work_id = l.source_work_id
            WHERE {corpus.clean_work_sql('w')} AND l.lex_id > %s ORDER BY l.lex_id LIMIT %s""", (cursor, n))
        return [(r[0], f"{PASSAGE_PREFIX}{r[1]}: {r[2]}") for r in cur.fetchall()]
    if side == "items":
        item_clean, _ = corpus.clean_item_sql('i', 'x', is_super=True)   # 嵌入端＝非讀取路徑,不做 RBAC domain 收窄(嵌全部 CLEAN 內容)
        cur.execute(f"""SELECT s.sent_id, s.sentence FROM knowledge_sentence s
            JOIN knowledge_item_text x ON x.itext_id = s.itext_id
            JOIN knowledge_item i ON i.item_id = x.item_id
            WHERE s.language = %s AND {item_clean}
              AND s.sent_id > %s ORDER BY s.sent_id LIMIT %s""", (language, cursor, n))
    else:
        cur.execute(f"""SELECT s.sent_id, s.sentence FROM knowledge_sentence s
            JOIN philosophy_work_text t ON t.text_id = s.text_id
            JOIN philosophy_work w ON w.work_id = t.work_id
            WHERE s.language = %s AND {corpus.clean_work_sql('w')}
              AND s.sent_id > %s ORDER BY s.sent_id LIMIT %s""", (language, cursor, n))
    return [(r[0], r[1]) for r in cur.fetchall()]


def print_stats(cur):
    """無參數安全預設:各層/各側待嵌統計(唯讀、零副作用,#29a)。"""
    cur.execute("SELECT count(*) FROM knowledge_lexicon")
    total = cur.fetchone()[0]
    cur.execute("SELECT count(DISTINCT lex_id) FROM knowledge_lexicon_embedding")
    print(f"  {'lexicon':16} 全量 {total:>9,} / 已嵌 {cur.fetchone()[0]:,}")
    for side, src_where in (("works", "s.text_id IS NOT NULL"), ("items", "s.itext_id IS NOT NULL")):
        for lang in ("zh", "en"):
            cur.execute(f"SELECT count(*) FROM knowledge_sentence s WHERE {src_where} AND s.language = %s",
                        (lang,))
            total = cur.fetchone()[0]
            cur.execute(f"""SELECT count(DISTINCT e.sent_id) FROM knowledge_sentence_embedding e
                JOIN knowledge_sentence s USING (sent_id) WHERE {src_where} AND s.language = %s""", (lang,))
            print(f"  {f'sentence {side} {lang}':16} 全量 {total:>9,} / 已嵌 {cur.fetchone()[0]:,}")
    for t in ("knowledge_lexicon_embedding", "knowledge_sentence_embedding"):
        gen = "複合鍵(P6)" if "model_tag" in _pk_cols(cur, t) else "單欄 PK(P6 遷移待執行)"
        print(f"  PK 世代 {t}:{gen}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--layer"); ap.add_argument("--language", default="zh")
    ap.add_argument("--scope", choices=("works", "items"), default="works", dest="side")
    ap.add_argument("--model", default=None)
    ap.add_argument("--limit", type=int); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--build-index", action="store_true", dest="build_index")
    args, _ = ap.parse_known_args()
    import time
    try:
        model_tag = args.model or embedspec.MODEL_TAG
        dim = embedspec.dim_for(model_tag)
    except KeyError as e:
        sys.exit(str(e))
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            precheck(cur, need_ledger=bool(args.layer))
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
                print_stats(cur)
            return
        scope = "embed_lexicon" if args.layer == "lexicon" else f"embed_sentence_{args.side}_{args.language}"
        table, idcol = (("knowledge_lexicon_embedding", "lex_id") if args.layer == "lexicon"
                        else ("knowledge_sentence_embedding", "sent_id"))
        with db.transaction(conn) as cur:
            check_dim(cur, table, dim)
            conflict_cols = resolve_write_target(cur, table, idcol, model_tag)
            ensure_scope(cur, scope, args.layer, args.side, args.language)
        model = load_model(model_tag)
        done = skipped = kept_total = inserted = 0
        t0 = time.time()
        limit = 10 if args.smoke else (args.limit or 10**9)
        while done < limit:
            with db.transaction(conn) as cur:
                cur.execute("SELECT cursor_sent_id FROM knowledge_build_meta WHERE scope=%s", (scope,))
                cursor = cur.fetchone()[0]
                rows = fetch_batch(cur, args.layer, args.language, args.side, cursor, min(2000, limit - done))
            if not rows:
                break
            keep = [(i, tx) for i, tx in rows
                    if args.layer == "lexicon" or not is_junk(tx, args.language)]
            skipped += len(rows) - len(keep)
            kept_total += len(keep)
            texts = [tx if tx.startswith(PASSAGE_PREFIX) else f"{PASSAGE_PREFIX}{tx}" for _, tx in keep]
            if texts:
                vecs = model.encode(texts, batch_size=BATCH, normalize_embeddings=True, show_progress_bar=False)
                with db.transaction(conn) as cur:
                    for (rid, _), v in zip(keep, vecs):
                        cur.execute(f"INSERT INTO {table} ({idcol}, embedding, model_tag) VALUES (%s,%s,%s) "
                                    f"ON CONFLICT ({conflict_cols}) DO NOTHING",
                                    (rid, list(map(float, v)), model_tag))
                        inserted += cur.rowcount
            with db.transaction(conn) as cur:
                cur.execute("UPDATE knowledge_build_meta SET cursor_sent_id=%s, updated_at=now() WHERE scope=%s",
                            (rows[-1][0], scope))
            done += len(rows)
            if done <= 2000 or done % 10000 < 2000:
                rate = done / max(time.time() - t0, 1)
                print(f"  {scope}: {done:,} 筆(skip {skipped})、{rate:.1f} 筆/s(首千列實測重投影 #15)", flush=True)
        suspect = done > 0 and kept_total > 0 and inserted == 0   # SOP-A ③:整跑 0 新列=疑靜默假成功
        note = "smoke" if args.smoke else None
        if suspect:
            note = "ZERO_INSERT_SUSPECT(SOP-A ③)"
        with db.transaction(conn) as cur:   # 排除帳落庫非 stdout(P6 既定契約)
            cur.execute("INSERT INTO knowledge_embed_ledger (scope, model_tag, processed, embedded, junk_excluded, note) "
                        "VALUES (%s,%s,%s,%s,%s,%s)", (scope, model_tag, done, inserted, skipped, note))
        print(f"完成 {scope}[{model_tag}]: 處理 {done:,}、新嵌 {inserted:,}、junk 排除 {skipped:,}(帳已落庫)、"
              f"耗時 {(time.time()-t0)/60:.1f} 分", flush=True)
        if suspect:
            sys.exit(f"處理 {kept_total:,} 句但 0 新列:疑換模未遷 PK/游標錯位之靜默假成功(SOP-A ③)→ 停手查核")


if __name__ == "__main__":
    main()
