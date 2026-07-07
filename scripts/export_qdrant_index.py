#!/usr/bin/env python
"""pgvector→Qdrant CLEAN 匯出 — 影子索引批次同步 CLI(向量遷移階段 0;可拋棄索引,內容永在 PG)。

🎯 這支在做什麼(白話):把已嵌入 pgvector 的句向量按 (side, language) **經 CLEAN 命門過閘後**匯出至
   Qdrant——point id=pg_pk、payload=窄 scalar(domain/entity_type/taxonomy_id/language)。
   **與 export_milvus 的關鍵差異=CLEAN 命門**:匯到外部 Qdrant 前一律經 augur.knowledge.corpus
   之閘(works 側 review_flag=false∧corpus_class=literary;items 側 license∈白名單∧entity_type∈
   語意准入∧**access_scope='public'**)——**access_scope='local_private' 之自有私有(ERP)一律不外流**
   (外部索引無 RBAC 收窄、放進去即洩漏;憲章 v1.36.0 owned_local⇒local_private)。COUNT/PKSET/SELECT
   三處共用同一 CLEAN 述詞(#12,杜絕 count 與 fetch 口徑漂移的假對帳)。

   游標/同步量記 qdrant_sync_state(先 Qdrant 成功再推游標,重跑=upsert 冪等);全量模式做雙向
   anti-join 對帳(missing→補、orphan→刪)、斷言 synced==n_source_clean 差=0;
   **反差 n_source_total−n_source_clean=被擋在影子索引外之私有列**,誠實印出。
   讀取路徑現仍走 pgvector(遷移未 cutover);Qdrant 隨時可 DROP 從 PG 全量重建(SOP-B)。

守 #6(冪等 resume)· #12(CLEAN 述詞 SSOT=corpus.py、介面住 vectorindex)· #15(對帳=實數斷言、
   CLEAN 反差可稽核非宣稱)· #27(orphan 重建閾值=操作值印 log 不鑄 schema)· #29(四件事)·
   紅線③(嵌入=索引非內容)· 憲章 v1.36.0 全文准入三軌 · Qdrant 遷移計畫階段 0/§3.6。

執行指令矩陣:
  python scripts/export_qdrant_index.py                                                    # 無參數:CLEAN 反差矩陣(唯讀零副作用,免 qdrant-client)
  python scripts/export_qdrant_index.py --side items --language zh --dry-run               # 印將匯出計數+CLEAN 反差,零寫入(免 qdrant-client)
  python scripts/export_qdrant_index.py --side items --language en --limit 100 --path ~/qdrant_local   # 驗證:只匯前 100 列、PG 零寫入
  python scripts/export_qdrant_index.py --side works --language zh --path ~/qdrant_local   # 全量:游標增量+雙向對帳+帳本落庫(embedded)
  python scripts/export_qdrant_index.py --side items --language en --url http://localhost:6333        # 全量(server)
  python scripts/export_qdrant_index.py --side items --language en --path ~/qdrant_local --rebuild     # DROP 後全量重建(破壞性,明示才做 #6)
  # 需先 pip install qdrant-client、並 python scripts/migrate_qdrant_sync_ddl.py 建帳本表
"""
import argparse
import json
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import embedspec
from augur.knowledge.corpus import clean_item_sql, clean_work_sql

DEFAULT_PATH = os.path.expanduser("~/qdrant_local")
ORPHAN_REBUILD_RATIO = 0.5   # orphan/source 超過即要求 --rebuild(操作值,#27:印 log 不鑄 schema)
BATCH = 1000
LAYER = "sentence"           # 首跑範圍(lexicon 層另案,同 export_milvus)

_SIDE_PRED = {"works": "s.text_id IS NOT NULL", "items": "s.itext_id IS NOT NULL"}
# 缺值哨兵(誠實標注非猜值):works 側無 domain/entity_type/taxonomy 欄→''/0
_SELECT_COLS = {
    "works": "e.sent_id, e.embedding::text, '', '', 0, s.language",
    "items": "e.sent_id, e.embedding::text, i.domain, i.entity_type, COALESCE(i.taxonomy_id, 0), s.language",
}


def _clean_scope(side):
    """回 (from_join_sql, clean_where_sql, clean_params) — CLEAN 命門過閘之來源界定。
    COUNT/PKSET/SELECT 三處共用此一份(#12);items 側取 access_scope='public'+is_super
    (公開 CLEAN、無 RBAC 收窄=影子索引只帶公開內容,私有 local_private 天然排除、不外流)。"""
    if side == "works":
        frm = ("FROM knowledge_sentence_embedding e "
               "JOIN knowledge_sentence s USING (sent_id) "
               "JOIN philosophy_work_text wt ON wt.text_id = s.text_id "
               "JOIN philosophy_work w ON w.work_id = wt.work_id")
        return frm, f"s.text_id IS NOT NULL AND {clean_work_sql('w')}", []
    frm = ("FROM knowledge_sentence_embedding e "
           "JOIN knowledge_sentence s USING (sent_id) "
           "JOIN knowledge_item_text x ON x.itext_id = s.itext_id "
           "JOIN knowledge_item i ON i.item_id = x.item_id")
    frag, params = clean_item_sql("i", "x", access_scope="public", is_super=True)
    return frm, f"s.itext_id IS NOT NULL AND {frag}", params


def fetch_rows(cur, side, language, extra_where, extra_params, limit):
    frm, where, cp = _clean_scope(side)
    cur.execute(f"SELECT {_SELECT_COLS[side]} {frm} "
                f"WHERE {where} AND s.language = %s AND e.model_tag = %s AND {extra_where} "
                f"ORDER BY e.sent_id LIMIT %s",
                (*cp, language, embedspec.MODEL_TAG, *extra_params, limit))
    return [{"pg_pk": r[0], "vector": json.loads(r[1]), "domain": r[2] or "",
             "entity_type": r[3] or "", "taxonomy_id": r[4], "language": r[5]}
            for r in cur.fetchall()]


def clean_source_count(cur, side, language):
    """CLEAN 過閘後之來源筆數 + max pk(=應匯出量、對帳基準)。"""
    frm, where, cp = _clean_scope(side)
    cur.execute(f"SELECT count(*), COALESCE(max(e.sent_id), 0) {frm} "
                f"WHERE {where} AND s.language = %s AND e.model_tag = %s",
                (*cp, language, embedspec.MODEL_TAG))
    return cur.fetchone()


def total_embed_count(cur, side, language):
    """未過閘之總嵌入筆數(該 side/language)——反差 total−clean=被擋在影子索引外之私有/未稽核列。"""
    cur.execute("SELECT count(*) FROM knowledge_sentence_embedding e "
                "JOIN knowledge_sentence s USING (sent_id) "
                f"WHERE {_SIDE_PRED[side]} AND s.language = %s AND e.model_tag = %s",
                (language, embedspec.MODEL_TAG))
    return cur.fetchone()[0]


def clean_pkset(cur, side, language):
    frm, where, cp = _clean_scope(side)
    cur.execute(f"SELECT e.sent_id {frm} WHERE {where} AND s.language = %s AND e.model_tag = %s",
                (*cp, language, embedspec.MODEL_TAG))
    return {r[0] for r in cur.fetchall()}


def _upsert_state(cur, coll, language, *, cursor=None, n_synced=None,
                  n_clean=None, n_total=None, note=None):
    """qdrant_sync_state 冪等 upsert(只更非 None 之欄;先 Qdrant 成功再推游標)。"""
    cur.execute("INSERT INTO qdrant_sync_state (collection, language) VALUES (%s, %s) "
                "ON CONFLICT (collection, language) DO NOTHING", (coll, language))
    sets, params = ["last_run_at = now()"], []
    for col, val in (("cursor_pk", cursor), ("n_synced", n_synced),
                     ("n_source_clean", n_clean), ("n_source_total", n_total), ("note", note)):
        if val is not None:
            sets.append(f"{col} = %s")
            params.append(val)
    cur.execute(f"UPDATE qdrant_sync_state SET {', '.join(sets)} WHERE collection=%s AND language=%s",
                (*params, coll, language))


def print_matrix():
    """無參數模式:各 (side, language) CLEAN 反差矩陣(唯讀;免 qdrant-client、不連 Qdrant)。"""
    print(f"Qdrant CLEAN 反差矩陣(model_tag={embedspec.MODEL_TAG}、layer={LAYER}):")
    print(f"{'side':6} {'lang':4} {'總嵌入':>10} {'CLEAN放行':>10} {'私有擋下':>10}  影子索引已同步")
    with db.connect() as conn, db.transaction(conn) as cur:
        for side in ("works", "items"):
            coll = embedspec.collection_name(LAYER, side)
            cur.execute("SELECT DISTINCT s.language FROM knowledge_sentence_embedding e "
                        "JOIN knowledge_sentence s USING (sent_id) "
                        f"WHERE {_SIDE_PRED[side]} AND e.model_tag = %s ORDER BY 1",
                        (embedspec.MODEL_TAG,))
            langs = [r[0] for r in cur.fetchall()] or ["-"]
            for lang in langs:
                if lang == "-":
                    print(f"{side:6} {'-':4} {'(該 side 尚未嵌入)':>10}")
                    continue
                total = total_embed_count(cur, side, lang)
                clean, _ = clean_source_count(cur, side, lang)
                cur.execute("SELECT n_synced FROM qdrant_sync_state WHERE collection=%s AND language=%s",
                            (coll, lang))
                row = cur.fetchone()
                synced = f"{row[0]:,}" if row else "(未建)"
                print(f"{side:6} {lang:4} {total:>10,} {clean:>10,} {total - clean:>10,}  {synced}")
    print("\n私有擋下=access_scope='local_private' 自有內容(只住 pgvector、不外流至 Qdrant,憲章 v1.36.0)")
    print("用法見標頭執行指令矩陣(--help)")


def reconcile(idx, cur, side, language, repair):
    """雙向 anti-join(對 CLEAN pkset);repair=True 才修:missing→補 upsert、orphan→刪。
    回 (missing, orphan, source_clean_n, synced_n)。"""
    pg_pks = clean_pkset(cur, side, language)
    q = idx.stats(include_pks=True, filters={"language": language})
    missing = pg_pks - q.get("pg_pks", set())
    orphan = q.get("pg_pks", set()) - pg_pks
    if repair:
        for chunk in (sorted(missing)[i:i + BATCH] for i in range(0, len(missing), BATCH)):
            idx.upsert(fetch_rows(cur, side, language, "e.sent_id = ANY(%s)", (list(chunk),), len(chunk)))
        if orphan:
            idx.delete(sorted(orphan))
    synced = idx.stats(filters={"language": language})["row_count"]
    return len(missing), len(orphan), len(pg_pks), synced


def main(argv=None):
    ap = argparse.ArgumentParser(description="pgvector→Qdrant CLEAN 匯出(影子索引,階段 0)")
    ap.add_argument("--side", choices=["works", "items"])
    ap.add_argument("--language")
    ap.add_argument("--limit", type=int, help="驗證模式:只匯前 N 列、PG 零寫入、不對帳刪除")
    ap.add_argument("--dry-run", action="store_true", help="印計數+CLEAN 反差,零寫入(免 qdrant-client)")
    ap.add_argument("--rebuild", action="store_true", help="DROP 後全量重建(破壞性;不可與 --limit 併用)")
    ap.add_argument("--url", help="Qdrant server(如 http://localhost:6333)")
    ap.add_argument("--path", help=f"Qdrant embedded 檔目錄(預設 {DEFAULT_PATH})")
    args = ap.parse_args(argv)

    if not args.side and not args.language:
        print_matrix()
        return 0
    if not (args.side and args.language):
        sys.exit("--side/--language 兩者須齊(或全省略=唯讀 CLEAN 反差矩陣)")
    if args.rebuild and args.limit:
        sys.exit("--rebuild 不可與 --limit 併用(重建=全量語意)")
    if args.limit is not None and args.limit <= 0:
        sys.exit("--limit 須為正整數(0/負值不得靜默轉為全量)")
    if args.url and args.path:
        sys.exit("--url 與 --path 僅可擇一(server 或 embedded)")

    coll = embedspec.collection_name(LAYER, args.side)
    spec = None   # 延遲到需要 Qdrant 時才建(dry-run 免 qdrant-client)
    full = not args.limit and not args.dry_run

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            total = total_embed_count(cur, args.side, args.language)
            clean_n, clean_max = clean_source_count(cur, args.side, args.language)
            cur.execute("SELECT cursor_pk FROM qdrant_sync_state WHERE collection=%s AND language=%s",
                        (coll, args.language))
            row = cur.fetchone()
            cursor = row[0] if row else 0
        withheld = total - clean_n
        print(f"collection={coll} language={args.language}\n"
              f"總嵌入 {total:,} | CLEAN 放行 {clean_n:,}(max pk {clean_max:,})| "
              f"私有擋下 {withheld:,} | 游標 {cursor:,} | "
              f"模式={'dry-run' if args.dry_run else ('驗證 --limit' if args.limit else '全量')}"
              f"{'+rebuild' if args.rebuild else ''}(orphan 重建閾值={ORPHAN_REBUILD_RATIO} #27)")
        if withheld:
            print(f"  ⓘ 私有擋下 {withheld:,} 列(access_scope='local_private')只住 pgvector、"
                  f"不匯至外部 Qdrant(憲章 v1.36.0、#15 誠實反差)")
        if clean_n == 0:
            print("CLEAN 放行 0 列(該 side/language 無公開可匯內容)——無事可匯,誠實結束")
            return 0
        if args.dry_run:
            print(f"[dry-run] 將 upsert CLEAN∧pk>{cursor} 之列;全量另做雙向對帳+帳本落庫;零寫入結束")
            return 0

        from augur.knowledge.vectorindex import CollectionSpec, QdrantIndex
        spec = CollectionSpec(name=coll, dim=embedspec.dim_for())
        idx = QdrantIndex(url=args.url, path=args.path or (None if args.url else DEFAULT_PATH))
        try:
            idx.ensure_collection(spec, rebuild=args.rebuild)
            if args.rebuild and full:
                with db.transaction(conn) as cur:
                    _upsert_state(cur, coll, args.language, cursor=0, n_synced=0,
                                  note="rebuild:DROP 後歸零游標")
                cursor = 0
                print(f"[rebuild] 已 DROP {coll} 並歸零游標")
            done, cap = 0, args.limit or 10**12
            start = cursor if full else 0   # 驗證模式不讀寫游標:固定從頭、可重放
            while done < cap:
                with db.transaction(conn) as cur:
                    rows = fetch_rows(cur, args.side, args.language, "e.sent_id > %s", (start,),
                                      min(BATCH, cap - done))
                if not rows:
                    break
                idx.upsert(rows)
                start = rows[-1]["pg_pk"]
                done += len(rows)
                if full:   # 先 Qdrant 成功、再推游標(重跑=upsert 冪等,游標永不超前資料)
                    with db.transaction(conn) as cur:
                        _upsert_state(cur, coll, args.language, cursor=start,
                                      n_clean=clean_n, n_total=total)
                if done % 10000 < BATCH:
                    print(f"  upsert 進度 {done:,}(pk 至 {start:,})", flush=True)
            print(f"upsert 完成 {done:,} 列")

            with db.transaction(conn) as cur:   # 先純測量(零寫入),重建判準才有效
                missing, orphan, src, synced = reconcile(idx, cur, args.side, args.language, repair=False)
            if not full:
                print(f"[驗證模式] 對帳僅報告不修:CLEAN 來源 {src:,}、Qdrant 已同步 {synced:,}、"
                      f"missing {missing:,}、orphan {orphan:,};PG 零寫入(游標/帳本未動)")
                return 0
            if orphan and orphan / max(src, 1) > ORPHAN_REBUILD_RATIO:
                sys.exit(f"orphan 比例 {orphan}/{src} 超過重建閾值 {ORPHAN_REBUILD_RATIO}"
                         f"——應 DROP 全量重建:加 --rebuild 重跑(本次已中止)")
            with db.transaction(conn) as cur:
                missing, orphan, src, synced = reconcile(idx, cur, args.side, args.language, repair=True)
                _upsert_state(cur, coll, args.language, cursor=clean_max, n_synced=synced,
                              n_clean=src, n_total=total,
                              note=f"missing_fixed={missing} orphan_deleted={orphan} withheld={total - src}")
            diff = synced - src
            print(f"對帳:CLEAN 來源 {src:,} | synced {synced:,} | missing→補 {missing:,} | "
                  f"orphan→刪 {orphan:,} | 差={diff} | 私有擋下 {total - src:,}(帳本已記)")
            if diff != 0:
                sys.exit(f"同步斷言失敗:synced−clean_source 差={diff}≠0(不得宣稱竣工)")
        finally:
            idx.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
