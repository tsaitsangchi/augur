#!/usr/bin/env python
"""pgvector→Milvus 單向匯出 — S6 serving 索引薄 CLI(可拋棄索引:id+distance,內容永在 PG)。

🎯 這支在做什麼(白話):把已嵌入 pgvector 的句向量(knowledge_sentence_embedding)按
   (layer, side, language) 匯出到 Milvus Lite 單檔索引——payload 只帶 pg_pk+窄 scalar
   (domain/entity_type/taxonomy_id/language),collection 名一律出自 embedspec(禁手寫縮寫);
   全量模式做雙向 anti-join 對帳(missing→補 upsert、orphan→同 run 刪除傳播)、
   斷言 synced==source 差=0、差值 append knowledge_coverage_metric、游標記 knowledge_build_meta
   (先 Milvus 成功再推游標,重跑=upsert 冪等;不為 Milvus 新增任何 PG 表)。
守 #12(介面住 knowledge.vectorindex、規格住 embedspec,本支只編排)· #15(對帳=實數斷言非宣稱)·
   #27(orphan 重建閾值=操作值印 log 不鑄 schema)· #29(四件事)· 紅線③ · e2e 計畫 §3-S6。

執行指令矩陣:
  python scripts/export_milvus_index.py                                                  # 無參數:PG↔Milvus 同步矩陣(唯讀零副作用)
  python scripts/export_milvus_index.py --layer sentence --side works --language zh --dry-run    # 列印將執行計數,零寫入
  python scripts/export_milvus_index.py --layer sentence --side works --language zh --limit 100  # 驗證模式:只匯前 100 列,PG 零寫入
  python scripts/export_milvus_index.py --layer sentence --side items --language en              # 全量:游標增量+雙向對帳+coverage 落庫
  python scripts/export_milvus_index.py --layer sentence --side items --language en --rebuild    # DROP 後從 PG 全量重建(破壞性,明示才做 #6)
  # --db-path PATH:Milvus Lite 檔(預設 ~/milvus_eval/knowledge.db;操作值印 log #27)
"""
import argparse
import json
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import embedspec
from augur.knowledge.vectorindex import CollectionSpec, MilvusLiteIndex

DEFAULT_DB_PATH = os.path.expanduser("~/milvus_eval/knowledge.db")
ORPHAN_REBUILD_RATIO = 0.5   # orphan/source 超過即要求 --rebuild(操作值,#27:印 log 不鑄 schema)
BATCH = 1000

_SIDE_PRED = {"works": "s.text_id IS NOT NULL", "items": "s.itext_id IS NOT NULL"}
# 缺值哨兵(誠實標注非猜值):works 側無 domain/entity_type/taxonomy 欄→''/0;items 側 taxonomy NULL→0
_SELECT = {
    "works": """SELECT e.sent_id, e.embedding::text, '', '', 0, s.language
        FROM knowledge_sentence_embedding e JOIN knowledge_sentence s USING (sent_id)""",
    "items": """SELECT e.sent_id, e.embedding::text, i.domain, i.entity_type, COALESCE(i.taxonomy_id, 0), s.language
        FROM knowledge_sentence_embedding e JOIN knowledge_sentence s USING (sent_id)
        JOIN knowledge_item_text x ON x.itext_id = s.itext_id
        JOIN knowledge_item i ON i.item_id = x.item_id""",
}
_COUNT = """SELECT count(*), COALESCE(max(e.sent_id), 0)
    FROM knowledge_sentence_embedding e JOIN knowledge_sentence s USING (sent_id)
    WHERE {pred} AND s.language = %s AND e.model_tag = %s"""
_PKSET = """SELECT e.sent_id
    FROM knowledge_sentence_embedding e JOIN knowledge_sentence s USING (sent_id)
    WHERE {pred} AND s.language = %s AND e.model_tag = %s"""


def fetch_rows(cur, side, language, where_extra, params, limit):
    cur.execute(f"{_SELECT[side]} WHERE {_SIDE_PRED[side]} AND s.language = %s AND e.model_tag = %s"
                f" AND {where_extra} ORDER BY e.sent_id LIMIT %s",
                (language, embedspec.MODEL_TAG, *params, limit))
    return [{"pg_pk": r[0], "vector": json.loads(r[1]), "domain": r[2] or "",
             "entity_type": r[3] or "", "taxonomy_id": r[4], "language": r[5]}
            for r in cur.fetchall()]


def source_count(cur, side, language):
    cur.execute(_COUNT.format(pred=_SIDE_PRED[side]), (language, embedspec.MODEL_TAG))
    return cur.fetchone()


def print_matrix(db_path):
    """無參數模式:各 (side, language) PG 已嵌量 vs Milvus 已同步量(唯讀;Milvus 檔不存在不創建)。"""
    print(f"S6 同步矩陣(model_tag={embedspec.MODEL_TAG}、db-path={db_path}):")
    idx = None
    if os.path.exists(db_path):
        idx = MilvusLiteIndex(db_path)
    else:
        print("  (Milvus 檔不存在=尚未匯出;本模式唯讀、不創建)")
    with db.connect() as conn, db.transaction(conn) as cur:
        for side in ("works", "items"):
            cur.execute(f"""SELECT s.language, count(*) FROM knowledge_sentence_embedding e
                JOIN knowledge_sentence s USING (sent_id)
                WHERE {_SIDE_PRED[side]} AND e.model_tag = %s GROUP BY 1 ORDER BY 1""",
                        (embedspec.MODEL_TAG,))
            rows = cur.fetchall() or [("-", 0)]
            coll = embedspec.collection_name("sentence", side)
            for lang, n in rows:
                synced = "-"
                if idx is not None and lang != "-" and idx.has(coll):
                    idx.ensure_collection(CollectionSpec(name=coll, dim=embedspec.dim_for()))
                    synced = idx.stats(filters={"language": lang})["row_count"]
                print(f"  sentence/{side:5}/{lang:2}  PG 已嵌 {n:>9,} | Milvus {coll} 已同步 {synced}")
    if idx is not None:
        idx.close()


def reconcile(idx, cur, side, language, repair):
    """雙向 anti-join;repair=True(全量模式)才修復:missing→補 upsert、orphan→刪除傳播;
    repair=False(驗證模式)=純報告零寫入。回 (missing, orphan, source_n, synced_n)。"""
    cur.execute(_PKSET.format(pred=_SIDE_PRED[side]), (language, embedspec.MODEL_TAG))
    pg_pks = {r[0] for r in cur.fetchall()}
    mv = idx.stats(include_pks=True, filters={"language": language})
    missing = pg_pks - mv["pg_pks"]
    orphan = mv["pg_pks"] - pg_pks
    if repair:
        for chunk in (sorted(missing)[i:i + BATCH] for i in range(0, len(missing), BATCH)):
            idx.upsert(fetch_rows(cur, side, language, "e.sent_id = ANY(%s)", (list(chunk),), len(chunk)))
        if orphan:
            idx.delete(sorted(orphan))
    synced = idx.stats(filters={"language": language})["row_count"]
    return len(missing), len(orphan), len(pg_pks), synced


def main():
    ap = argparse.ArgumentParser(description="pgvector→Milvus 單向匯出(S6)")
    ap.add_argument("--layer", choices=["sentence"], help="首跑範圍=sentence(lexicon 層另案)")
    ap.add_argument("--side", choices=["works", "items"])
    ap.add_argument("--language")
    ap.add_argument("--limit", type=int, help="驗證模式:只匯前 N 列、PG 零寫入、不對帳刪除")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rebuild", action="store_true", help="DROP 後全量重建(破壞性;不可與 --limit 併用)")
    ap.add_argument("--db-path", default=DEFAULT_DB_PATH)
    args = ap.parse_args()

    if not args.layer and not args.side and not args.language:
        print_matrix(args.db_path)
        print("\n用法見標頭執行指令矩陣(python scripts/export_milvus_index.py --help)")
        return
    if not (args.layer and args.side and args.language):
        sys.exit("--layer/--side/--language 三者須齊(或全省略=唯讀矩陣)")
    if args.rebuild and args.limit:
        sys.exit("--rebuild 不可與 --limit 併用(重建=全量語意)")
    if args.limit is not None and args.limit <= 0:
        sys.exit("--limit 須為正整數(0/負值不得靜默轉為全量)")

    coll = embedspec.collection_name(args.layer, args.side)
    scope = embedspec.sync_scope(coll, args.language)
    spec = CollectionSpec(name=coll, dim=embedspec.dim_for())
    full = not args.limit and not args.dry_run

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            src_n, src_max = source_count(cur, args.side, args.language)
            cur.execute("SELECT cursor_sent_id FROM knowledge_build_meta WHERE scope = %s", (scope,))
            row = cur.fetchone()
            cursor = row[0] if row else 0
        print(f"collection={coll} scope={scope} db-path={args.db_path}\n"
              f"PG 來源 {src_n:,} 列(max pk {src_max:,})、游標 {cursor:,}、"
              f"模式={'dry-run' if args.dry_run else ('驗證 --limit' if args.limit else '全量')}"
              f"{'+rebuild' if args.rebuild else ''}(orphan 重建閾值={ORPHAN_REBUILD_RATIO} 操作值 #27)")
        if src_n == 0:
            print("來源 0 列(該 side/language 尚未嵌入)——無事可匯,誠實結束")
            return
        if args.dry_run:
            print(f"[dry-run] 將 upsert pk>{cursor} 之列,全量模式將另做雙向對帳+coverage 落庫;零寫入結束")
            return

        idx = MilvusLiteIndex(args.db_path)
        try:
            idx.ensure_collection(spec, rebuild=args.rebuild)
            if args.rebuild and full:
                with db.transaction(conn) as cur:
                    cur.execute("UPDATE knowledge_build_meta SET cursor_sent_id = 0, updated_at = now() "
                                "WHERE scope LIKE %s", (f"mv_{coll}_%",))
                cursor = 0
                print(f"[rebuild] 已 DROP {coll} 並歸零全部語言游標;他語言分割區須各自重跑全量")
            if full:
                with db.transaction(conn) as cur:
                    cur.execute("INSERT INTO knowledge_build_meta (scope, cursor_sent_id) VALUES (%s, 0) "
                                "ON CONFLICT (scope) DO NOTHING", (scope,))
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
                if full:   # 先 Milvus 成功、再推游標(重跑=upsert 冪等,游標永不超前資料)
                    with db.transaction(conn) as cur:
                        cur.execute("UPDATE knowledge_build_meta SET cursor_sent_id = %s, updated_at = now() "
                                    "WHERE scope = %s", (start, scope))
                if done % 10000 < BATCH:
                    print(f"  upsert 進度 {done:,}(pk 至 {start:,})", flush=True)
            print(f"upsert 完成 {done:,} 列")

            with db.transaction(conn) as cur:   # 先純測量(零寫入),重建判準才有效
                missing, orphan, src, synced = reconcile(idx, cur, args.side, args.language,
                                                         repair=False)
            if not full:
                print(f"[驗證模式] 對帳僅報告不修:PG 來源 {src:,}、Milvus 已同步 {synced:,}、"
                      f"missing {missing:,}、orphan {orphan:,};PG 零寫入(游標/coverage 未動)")
                return
            if orphan and orphan / max(src, 1) > ORPHAN_REBUILD_RATIO:
                sys.exit(f"orphan 比例 {orphan}/{src} 超過重建閾值 {ORPHAN_REBUILD_RATIO}"
                         f"——依 §3-S6 機器判準應 DROP 全量重建:加 --rebuild 重跑(本次已中止)")
            with db.transaction(conn) as cur:
                missing, orphan, src, synced = reconcile(idx, cur, args.side, args.language,
                                                         repair=True)
            diff = synced - src
            note = f"missing_fixed={missing} orphan_deleted={orphan} model_tag={embedspec.MODEL_TAG}"
            with db.transaction(conn) as cur:
                cur.execute("""INSERT INTO knowledge_coverage_metric
                    (metric_date, metric_key, numerator, denominator, note)
                    VALUES (CURRENT_DATE, %s, %s, %s, %s)
                    ON CONFLICT (metric_date, metric_key) DO UPDATE SET
                    numerator = EXCLUDED.numerator, denominator = EXCLUDED.denominator, note = EXCLUDED.note""",
                            (scope, synced, src, note))
            print(f"對帳:source {src:,} | synced {synced:,} | missing→補 {missing:,} | "
                  f"orphan→刪 {orphan:,} | 差={diff}(coverage_metric 已記 {scope})")
            if diff != 0:
                sys.exit(f"同步斷言失敗:synced-source 差={diff}≠0(不得宣稱竣工)")
        finally:
            idx.close()


if __name__ == "__main__":
    main()
