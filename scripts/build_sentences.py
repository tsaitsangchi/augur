#!/usr/bin/env python
"""逐句切分引擎(T3)— 全文段(work_text/item_text)以確定性 regex 切句入 knowledge_sentence。

🎯 這支在做什麼(白話):讀 L1 全文層(philosophy_work_text 公版全文 + knowledge_item_text OA 全文),
   用**確定性 regex**(零 ML、半年重跑一致)逐段切句,帶 char_start/char_end(相對該段 content,
   content[char_start:char_end] == sentence 可精確切回原文)寫入 knowledge_sentence(L2 結構層)。
   前置 backfill:上游 language IS NULL 者先以確定性規則回填(非空白字元中 CJK 佔比>30%→zh、否則 en)。
   排除 review_flag=true 之 work(T-1 歸屬稽核契約);resume=每段 WHERE NOT EXISTS;批 500 段/commit。
   已知侷限(誠實記,v1 不追完美句界):西文縮寫(Mr. 等)誤切、非 zh/en 語言一律走西文規則。
守 #1(逐字原文切片、零 AI 改寫)· #6(冪等/resume,重跑零重複)· #15(統計誠實印出)· CLAUDE #29。

執行指令矩陣:
  python scripts/build_sentences.py                               # 無參數:印矩陣+待切統計(唯讀)
  python scripts/build_sentences.py --scope philosophy --limit 3  # 小樣本微測(3 段)
  python scripts/build_sentences.py --scope philosophy            # 哲學側全量(work_text)
  python scripts/build_sentences.py --scope items                 # item 側(knowledge_item_text)
  python scripts/build_sentences.py --scope all                   # 兩側全跑
  python scripts/build_sentences.py --text-id 247                 # 指定單段(如道德經第一章)
"""
import re
import sys
import time
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from psycopg2.extras import execute_values

from augur.core import db

# ── 確定性規則(計畫 §三T3;不用 ML) ─────────────────────────────────
CJK_RE = re.compile(r"[一-鿿]")                       # U+4E00–U+9FFF(與 §二6 term 契約同範圍)
_ZH_TERM = "。!?;!?;"                               # 中文句末:全形。+ 半全形 !?;(兩制式皆收)
_ZH_CLOSE = "」』”’》〉】)\"')]"            # 引號/括號閉合:句末標點後隨附歸前句
ZH_END_RE = re.compile("[" + re.escape(_ZH_TERM) + "]+[" + re.escape(_ZH_CLOSE) + "]*")
EN_CUT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")  # 西文:句末標點+空白+大寫/引號起頭處切


def detect_language(text):
    """確定性語言回填規則:非空白字元中 CJK(一-鿿)佔比 >30% → zh,否則 en。"""
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return "en"
    cjk = sum(1 for c in chars if CJK_RE.match(c))
    return "zh" if cjk / len(chars) > 0.30 else "en"


def _trim_span(content, start, end):
    """去除段首尾空白並回傳調整後 (start, end)——保證 content[start:end] 首尾非空白。"""
    seg = content[start:end]
    left = len(seg) - len(seg.lstrip())
    right = len(seg) - len(seg.rstrip())
    return start + left, end - right


def split_sentences(content, language):
    """回傳 [(char_start, char_end), ...];content[s:e] 即句子(offset 相對原 content,可切回)。"""
    spans, prev = [], 0
    if language == "zh":
        for m in ZH_END_RE.finditer(content):
            s, e = _trim_span(content, prev, m.end())
            if e > s:
                spans.append((s, e))
            prev = m.end()
    else:
        for m in EN_CUT_RE.finditer(content):
            s, e = _trim_span(content, prev, m.start())
            if e > s:
                spans.append((s, e))
            prev = m.end()
    if prev < len(content):                            # 無終止符之尾段自成一句
        s, e = _trim_span(content, prev, len(content))
        if e > s:
            spans.append((s, e))
    return spans


# ── DB 寫入 ────────────────────────────────────────────────────────────
INSERT_SQL = ("INSERT INTO knowledge_sentence (text_id, itext_id, seq, sentence, language, char_start, char_end) "
              "VALUES %s ON CONFLICT DO NOTHING")

SIDES = {
    # side: (上游表, id 欄, 來源 SELECT;review_flag 排除=T-1 契約,item 側無 work 歸屬故無此閘)
    "philosophy": ("philosophy_work_text", "text_id",
                   "SELECT wt.text_id, wt.content, wt.language FROM philosophy_work_text wt "
                   "JOIN philosophy_work w USING (work_id) "
                   "WHERE w.review_flag IS NOT TRUE AND COALESCE(w.work_type,'') NOT IN ('dictionary','thesaurus') "
                   "AND wt.text_id > %s "
                   "AND NOT EXISTS (SELECT 1 FROM knowledge_sentence s WHERE s.text_id = wt.text_id) "),
    "items": ("knowledge_item_text", "itext_id",
              "SELECT it.itext_id, it.content, it.language FROM knowledge_item_text it "
              "WHERE it.itext_id > %s "
              "AND NOT EXISTS (SELECT 1 FROM knowledge_sentence s WHERE s.itext_id = it.itext_id) "),
}


def _table_exists(cur, name):
    cur.execute("SELECT to_regclass(%s)", (name,))
    return cur.fetchone()[0] is not None


def _insert_rows(cur, rows, page=5000):
    """分頁 execute_values;每頁單一 statement 使 rowcount=實際插入數(ON CONFLICT 略過不計)。"""
    inserted = 0
    for i in range(0, len(rows), page):
        chunk = rows[i:i + page]
        execute_values(cur, INSERT_SQL, chunk, page_size=len(chunk))
        inserted += cur.rowcount
    return inserted


def backfill_language(conn):
    """前置 backfill:上游 language IS NULL 以確定性規則回填;回傳各表回填數(表未建=None)。"""
    result = {}
    for table, idcol in (("philosophy_work_text", "text_id"), ("knowledge_item_text", "itext_id")):
        with db.transaction(conn) as cur:
            if not _table_exists(cur, table):
                result[table] = None
                continue
            cur.execute(f"SELECT {idcol}, content FROM {table} WHERE language IS NULL")
            updates = [(detect_language(c), i) for i, c in cur.fetchall()]
            if updates:
                cur.executemany(f"UPDATE {table} SET language=%s WHERE {idcol}=%s", updates)
            result[table] = len(updates)
    return result


def build_side(conn, side, limit=None, text_id=None):
    """切一側(philosophy/items);批 500 段/commit;回傳統計 dict。"""
    table, idcol, base_sql = SIDES[side]
    with db.transaction(conn) as cur:
        if not _table_exists(cur, table):
            print(f"  [{side}] 上游表 {table} 未建(計畫②/T0 未跑)→ 誠實跳過")
            return {"texts": 0, "sentences": 0, "inserted": 0, "empty": 0}
    stats = {"texts": 0, "sentences": 0, "inserted": 0, "empty": 0}
    cursor_id = 0                                      # 跑內游標:防空白段(切出 0 句)無限重取
    remaining = limit
    while True:
        n = 500 if remaining is None else min(500, remaining)
        if n <= 0:
            break
        with db.transaction(conn) as cur:
            sql, params = base_sql, [cursor_id]
            if text_id is not None:
                sql += f"AND wt.{idcol} = %s "
                params.append(text_id)
            cur.execute(sql + "ORDER BY 1 LIMIT %s", params + [n])
            batch = cur.fetchall()
            if not batch:
                break
            rows = []
            for tid, content, lang in batch:
                lang = lang or detect_language(content)   # 兜底:跑間新插入之 NULL,同一確定性規則
                spans = split_sentences(content, lang)
                if not spans:
                    stats["empty"] += 1
                for seq, (s, e) in enumerate(spans):
                    ref = (tid, None) if side == "philosophy" else (None, tid)
                    rows.append(ref + (seq, content[s:e], lang, s, e))
                cursor_id = tid
            stats["inserted"] += _insert_rows(cur, rows)
            stats["texts"] += len(batch)
            stats["sentences"] += len(rows)
        if remaining is not None:
            remaining -= len(batch)
        print(f"  [{side}] 批完成:段累計 {stats['texts']}、句累計 {stats['sentences']}(cursor={cursor_id})",
              flush=True)
    return stats


def print_info(conn):
    """無參數唯讀模式:指令矩陣+待切統計。"""
    print(__doc__.split("執行指令矩陣:")[1])
    with db.transaction(conn) as cur:
        if not _table_exists(cur, "knowledge_sentence"):
            print("⚠ knowledge_sentence 未建 → 先跑 T0:python scripts/migrate_text_understanding_ddl.py")
            return
        cur.execute("SELECT count(*), count(*) FILTER (WHERE language IS NULL) FROM philosophy_work_text")
        total, lang_null = cur.fetchone()
        cur.execute("SELECT count(*) FROM philosophy_work_text wt JOIN philosophy_work w USING (work_id) "
                    "WHERE w.review_flag IS TRUE")
        flagged = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM philosophy_work_text wt JOIN philosophy_work w USING (work_id) "
                    "WHERE w.review_flag IS NOT TRUE AND COALESCE(w.work_type,'') NOT IN ('dictionary','thesaurus') "
                    "AND NOT EXISTS (SELECT 1 FROM knowledge_sentence s WHERE s.text_id = wt.text_id)")
        pending = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM knowledge_sentence")
        done = cur.fetchone()[0]
        print(f"philosophy 側:全 {total} 段(language NULL {lang_null}、review 排除 {flagged})"
              f" → 待切 {pending} 段;knowledge_sentence 現有 {done} 句")
        if _table_exists(cur, "knowledge_item_text"):
            cur.execute("SELECT count(*) FROM knowledge_item_text it "
                        "WHERE NOT EXISTS (SELECT 1 FROM knowledge_sentence s WHERE s.itext_id = it.itext_id)")
            print(f"items 側:待切 {cur.fetchone()[0]} 段")
        else:
            print("items 側:knowledge_item_text 未建(計畫②/T0 未跑)")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--scope", choices=["philosophy", "items", "all"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--text-id", dest="text_id", type=int)
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        if not (args.scope or args.limit or args.text_id):
            print_info(conn)
            return
        with db.transaction(conn) as cur:
            if not _table_exists(cur, "knowledge_sentence"):
                sys.exit("knowledge_sentence 未建 → 先跑 T0:python scripts/migrate_text_understanding_ddl.py")
        t0 = time.time()
        bf = backfill_language(conn)
        for table, n in bf.items():
            print(f"language backfill:{table} = {'表未建,跳過' if n is None else f'{n} 列回填'}")
        scope = args.scope or "philosophy"             # 分期紀律:預設哲學側
        sides = ["philosophy", "items"] if scope == "all" else [scope]
        if args.text_id is not None:
            sides = ["philosophy"]                     # --text-id 僅哲學側定址
        grand = {"texts": 0, "sentences": 0, "inserted": 0, "empty": 0}
        for side in sides:
            st = build_side(conn, side, limit=args.limit, text_id=args.text_id)
            for k in grand:
                grand[k] += st[k]
        el = time.time() - t0
        print(f"完成:段 {grand['texts']}、切句 {grand['sentences']}、實插 {grand['inserted']}"
              f"(conflict 略過 {grand['sentences'] - grand['inserted']})、零句段 {grand['empty']};"
              f"耗時 {el:.1f}s({grand['texts'] / el if el > 0 else 0:.1f} 段/s)")
        print("→ 下一步:python scripts/build_concordance.py --limit 3(T4 微測)")


if __name__ == "__main__":
    main()
