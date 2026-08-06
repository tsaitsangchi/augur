#!/usr/bin/env python
"""逐字索引引擎(T4)— knowledge_sentence 經 textnorm 契約斷詞入 knowledge_concordance(hash 分區表)。

🎯 這支在做什麼(白話):讀 L2 句子(knowledge_sentence),以 term 正規化契約(SSOT=
   `augur.knowledge.textnorm`,計畫 §二6:zh NFC+逐字+jieba HMM=False、en lowercase+Porter,
   全確定性)產 (term, language, sent_id, position),批次 1 萬列/commit 寫入 knowledge_concordance
   (16 hash 分區)。resume=游標記 knowledge_build_meta(scope key='concordance_{scope}_{language}',
   與資料同 transaction commit,崩潰一致);PK ON CONFLICT DO NOTHING 兜底。
   **分期紀律**:預設 --scope philosophy --language zh(p0 量小先驗中文路徑);吞吐統計印出供
   p1/全量外推(全 corpus 數億列=分區+分期,計畫 §三T4)。排除 review_flag=true 之 work(T-1 契約)。
守 #6(游標 resume+冪等,重跑零重複)· #15(吞吐/計數誠實印出)· #28(本地零 usage)· CLAUDE #29。

執行指令矩陣:
  python scripts/build_concordance.py                        # 無參數:印矩陣+游標/待處理統計(唯讀)
  python scripts/build_concordance.py --limit 3              # 微測:3 句(預設 philosophy/zh)
  python scripts/build_concordance.py --run                  # p0:philosophy×zh 全量
  python scripts/build_concordance.py --language en --limit 1000       # p1:en 抽樣吞吐實測
  python scripts/build_concordance.py --scope items --language en --run
  python scripts/build_concordance.py --backfill-local-eligible --limit 5   # #1e 微測(不動主游標)
  python scripts/build_concordance.py --backfill-local-eligible --run       # #1e local×eligible 缺列補建(zh)
  python scripts/build_concordance.py --backfill-local-eligible --language en --run
"""
import sys
import time
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from psycopg2.extras import execute_values

from augur.core import db
from augur.knowledge import corpus   # W2.5:CLEAN 述詞 SSOT(review_flag=false ∧ corpus_class='literary')

try:
    from augur.knowledge import textnorm               # §二6 契約 SSOT(三方 JOIN 鍵同一函式)
except ImportError:
    textnorm = None

FETCH_N = 2000                                         # 每次自 DB 取句數(記憶體上限)
FLUSH_N = 10000                                        # 批 1 萬列/commit(計畫 §三T4)

INSERT_SQL = ("INSERT INTO knowledge_concordance (term, language, sent_id, position) "
              "VALUES %s ON CONFLICT DO NOTHING")
META_SQL = ("INSERT INTO knowledge_build_meta (scope, cursor_sent_id, updated_at) VALUES (%s, %s, now()) "
            "ON CONFLICT (scope) DO UPDATE SET cursor_sent_id = EXCLUDED.cursor_sent_id, updated_at = now()")

FETCH_SQL = {
    # scope: 句子來源(review_flag 排除=T-1 契約,僅 philosophy 側有 work 歸屬)
    "philosophy": ("SELECT s.sent_id, s.sentence FROM knowledge_sentence s "
                   "JOIN philosophy_work_text wt ON wt.text_id = s.text_id "
                   "JOIN philosophy_work w ON w.work_id = wt.work_id "
                   f"WHERE {corpus.clean_work_sql('w')} AND s.language = %s AND s.sent_id > %s "
                   "ORDER BY s.sent_id LIMIT %s"),
    "items": ("SELECT s.sent_id, s.sentence FROM knowledge_sentence s "
              "WHERE s.itext_id IS NOT NULL AND s.language = %s AND s.sent_id > %s "
              "ORDER BY s.sent_id LIMIT %s"),
}


def _table_exists(cur, name):
    cur.execute("SELECT to_regclass(%s)", (name,))
    return cur.fetchone()[0] is not None


def sentence_terms(sentence, language):
    """呼叫契約 SSOT textnorm.tokenize;容 [(term,position)] 或 [term](後者以 token 序為 position)。"""
    out = textnorm.tokenize(sentence, language)
    terms = []
    for i, t in enumerate(out):
        if isinstance(t, (tuple, list)) and len(t) >= 2:
            terms.append((str(t[0]), int(t[1])))
        else:
            terms.append((str(t), i))
    return terms


def _insert_rows(cur, rows, page=10000):
    """分頁 execute_values;每頁單一 statement 使 rowcount=實際插入數(ON CONFLICT 略過不計)。"""
    inserted = 0
    for i in range(0, len(rows), page):
        chunk = rows[i:i + page]
        execute_values(cur, INSERT_SQL, chunk, page_size=len(chunk))
        inserted += cur.rowcount
    return inserted


def flush(conn, key, rows, language, last_sid):
    """一批入庫+游標推進(同 transaction commit → 崩潰一致);回傳實插列數。"""
    with db.transaction(conn) as cur:
        inserted = _insert_rows(cur, [(t, language, sid, pos) for t, sid, pos in rows]) if rows else 0
        cur.execute(META_SQL, (key, last_sid))
    return inserted


def run(conn, scope, language, limit=None):
    key = f"concordance_{scope}_{language}"
    with db.transaction(conn) as cur:
        cur.execute("SELECT cursor_sent_id FROM knowledge_build_meta WHERE scope = %s", (key,))
        r = cur.fetchone()
    cursor = r[0] if r else 0
    print(f"scope key={key} 起始游標 sent_id={cursor}")
    return _run_loop(conn, FETCH_SQL[scope], key, language, cursor, limit=limit, advance_meta=True)


def run_backfill_local_eligible(conn, language, limit=None):
    """#1e：只補 local×eligible 且句尚無 concordance 之句；**不推進** concordance_items_* 主游標。

    先撈該語全部 local×eligible 句，再以 `sent_id = ANY(...)` 一次差集（避逐批 NOT EXISTS 掃 55M 分區）。
    meta key=`conc_bf_local_elig_{lang}` 僅作本刀進度（可重跑冪等 ON CONFLICT）。
    """
    key = f"conc_bf_local_elig_{language}"  # ≤32: knowledge_build_meta.scope varchar(32)
    t0 = time.time()
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT s.sent_id, s.sentence FROM knowledge_sentence s "
            "JOIN knowledge_item_text t ON t.itext_id = s.itext_id "
            "JOIN knowledge_item i ON i.item_id = t.item_id "
            "JOIN knowledge_kh4_state k ON k.item_id = i.item_id "
            "WHERE i.domain = 'local' AND k.answer_status = 'eligible' "
            "  AND s.language = %s "
            "ORDER BY s.sent_id",
            (language,),
        )
        all_rows = cur.fetchall()
    sids = [r[0] for r in all_rows]
    print(f"backfill-local-eligible key={key} local×eligible×{language} 句={len(sids)}（主游標 items 不動）")
    have = set()
    if sids:
        with db.transaction(conn) as cur:
            # 分頁 ANY，避免超大參數
            for i in range(0, len(sids), 5000):
                chunk = sids[i:i + 5000]
                cur.execute(
                    "SELECT DISTINCT sent_id FROM knowledge_concordance WHERE sent_id = ANY(%s)",
                    (chunk,),
                )
                have.update(r[0] for r in cur.fetchall())
    gaps = [(sid, sent) for sid, sent in all_rows if sid not in have]
    if limit is not None:
        gaps = gaps[: int(limit)]
    print(f"  已有 conc 句={len(have)}；待補={len(gaps)}（limit={limit}）")
    buf, sent_done, attempted, inserted = [], 0, 0, 0
    last_sid = 0
    for sid, sentence in gaps:
        for term, pos in sentence_terms(sentence, language):
            buf.append((term, sid, pos))
        sent_done += 1
        last_sid = sid
        if len(buf) >= FLUSH_N:
            attempted += len(buf)
            inserted += flush(conn, key, buf, language, last_sid)
            buf = []
            el = time.time() - t0
            print(f"  flush:句 {sent_done}/{len(gaps)}、列累計 {attempted}(實插 {inserted})、"
                  f"{sent_done / el:.1f} 句/s", flush=True)
    if buf or (sent_done and last_sid):
        attempted += len(buf)
        inserted += flush(conn, key, buf, language, last_sid or 0)
    el = time.time() - t0
    rate_s = sent_done / el if el > 0 else 0.0
    print(f"完成:句 {sent_done}、term 列 {attempted}、實插 {inserted}(conflict 略過 {attempted - inserted});"
          f"耗時 {el:.1f}s = {rate_s:.1f} 句/s; last_sid → {last_sid}")
    return sent_done, inserted


def _run_loop(conn, fetch_sql, key, language, cursor, limit=None, advance_meta=True):
    buf, sent_done, attempted, inserted = [], 0, 0, 0
    last_fetch, last_sid = cursor, cursor
    t0 = time.time()
    while True:
        n = FETCH_N if limit is None else min(FETCH_N, limit - sent_done)
        if n <= 0:
            break
        with db.transaction(conn) as cur:
            cur.execute(fetch_sql, (language, last_fetch, n))
            batch = cur.fetchall()
        if not batch:
            break
        for sid, sentence in batch:
            for term, pos in sentence_terms(sentence, language):
                buf.append((term, sid, pos))
            sent_done += 1
            last_sid = sid
            if len(buf) >= FLUSH_N:
                attempted += len(buf)
                if advance_meta:
                    inserted += flush(conn, key, buf, language, last_sid)
                else:
                    with db.transaction(conn) as cur:
                        inserted += _insert_rows(cur, [(t, language, sid, pos) for t, sid, pos in buf])
                buf = []
                el = time.time() - t0
                print(f"  flush:句 {sent_done}、列累計 {attempted}(實插 {inserted})、"
                      f"{sent_done / el:.1f} 句/s、{attempted / el:.0f} 列/s(游標={last_sid})", flush=True)
        last_fetch = batch[-1][0]
    if buf or last_sid > cursor:
        attempted += len(buf)
        if advance_meta:
            inserted += flush(conn, key, buf, language, last_sid)
        else:
            with db.transaction(conn) as cur:
                if buf:
                    inserted += _insert_rows(cur, [(t, language, sid, pos) for t, sid, pos in buf])
    el = time.time() - t0
    rate_s = sent_done / el if el > 0 else 0.0
    rate_r = attempted / el if el > 0 else 0.0
    print(f"完成:句 {sent_done}、term 列 {attempted}、實插 {inserted}(conflict 略過 {attempted - inserted});"
          f"耗時 {el:.1f}s = {rate_s:.1f} 句/s、{rate_r:.0f} 列/s;游標 → {last_sid}")
    print("→ 外推(分期紀律):待處理句數請以 SQL 實算,除以上列吞吐即得該期預估時程(計畫值=快照非承諾)")
    return sent_done, inserted


def print_info(conn):
    """無參數唯讀模式:指令矩陣+游標/待處理統計。"""
    print(__doc__.split("執行指令矩陣:")[1])
    print(f"textnorm 契約模組:{'已載入' if textnorm else '未落地(augur.knowledge.textnorm,並行分派)'}")
    with db.transaction(conn) as cur:
        for t in ("knowledge_sentence", "knowledge_concordance", "knowledge_build_meta"):
            if not _table_exists(cur, t):
                print(f"⚠ {t} 未建 → 先跑 T0:python scripts/migrate_text_understanding_ddl.py")
                return
        cur.execute("SELECT CASE WHEN text_id IS NOT NULL THEN 'philosophy' ELSE 'items' END, language, count(*) "
                    "FROM knowledge_sentence GROUP BY 1, 2 ORDER BY 1, 2")
        rows = cur.fetchall()
        print("knowledge_sentence 現況:" + ("(空)" if not rows else ""))
        for side, lang, n in rows:
            print(f"  {side:10} {lang:4} {n} 句")
        cur.execute("SELECT scope, cursor_sent_id, updated_at FROM knowledge_build_meta ORDER BY scope")
        metas = cur.fetchall()
        print("build_meta 游標:" + ("(無)" if not metas else ""))
        for scope, cur_id, ts in metas:
            print(f"  {scope:32} cursor_sent_id={cur_id}({ts:%Y-%m-%d %H:%M})")
        cur.execute("SELECT coalesce(sum(greatest(reltuples, 0)), 0)::bigint FROM pg_class "
                    "WHERE relname ~ '^knowledge_concordance_p\\d+$'")  # 未 ANALYZE 之分區 reltuples=-1,夾 0
        print(f"knowledge_concordance 列數估計(pg_class.reltuples,ANALYZE 後準):{cur.fetchone()[0]}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--scope", choices=["philosophy", "items"])
    ap.add_argument("--language", choices=["zh", "en"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--backfill-local-eligible", action="store_true",
                    help="#1e:補 local×eligible 且句無 concordance 之列；不推進 items 主游標")
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        if not (args.run or args.scope or args.language or args.limit or args.backfill_local_eligible):
            print_info(conn)
            return
        if textnorm is None:
            sys.exit("textnorm 契約模組未落地(src/augur/knowledge/textnorm.py,計畫 §二6 SSOT)→ 先待該分派完成")
        with db.transaction(conn) as cur:
            for t in ("knowledge_sentence", "knowledge_concordance", "knowledge_build_meta"):
                if not _table_exists(cur, t):
                    sys.exit(f"{t} 未建 → 先跑 T0:python scripts/migrate_text_understanding_ddl.py")
        lang = args.language or "zh"
        if args.backfill_local_eligible:
            # --limit  alone = micro；--run 或有 limit 皆可跑；無 --run 且無 limit → 印提示
            if not (args.run or args.limit):
                print("#1e backfill-local-eligible：請加 --limit N（微測）或 --run（全量）。主游標 items 不動。")
                return
            run_backfill_local_eligible(conn, lang, limit=args.limit if not args.run else None)
            return
        run(conn, args.scope or "philosophy", lang, limit=args.limit)


if __name__ == "__main__":
    main()
