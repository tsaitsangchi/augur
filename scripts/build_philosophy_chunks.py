#!/usr/bin/env python
"""P1/T5 全文語義切塊 — philosophy_work_text + knowledge_item_text → philosophy_chunk(可嵌入單位)。

🎯 把公版全文(約 1.6 億字、段落極不均、最大 6.5 萬字/段)語義切成 ~500 token 可嵌入塊,
   保留 char_range 逐字溯源(chunk.content == 來源 content[char_start:char_end])。
   哲學素養框架 L2 知識檢索層基建(學習計畫 P1)。切塊邊界:段落 > 句末標點;塊間重疊 ~15%。
   T5 泛化(text 計畫 v1.6):knowledge_item_text(OA 全文)走同一切塊管線——itext_id 帶入、
   text_id/work_id NULL(二擇一,DDL 住 migrate_text_understanding_ddl.py;未遷移則僅哲學路徑並明說)。
   T-1 稽核閘:review_flag work(誤配/未稽核)一律排除不入塊。
守 #1(逐字不改一字、char_range 可回驗、無 AI 摘要、稽核閘防誤配假兆)· #28(本地零 usage)·
   #6(DB-driven resume)· #18。

執行指令矩陣:python scripts/build_philosophy_chunks.py [--force]
"""
import re
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

TARGET_TOK = 500
OVERLAP_TOK = 75
CJK = re.compile(r"[一-鿿㐀-䶿豈-﫿]")
BOUND = re.compile(r"[。！？!?][\"')\]」』]?\s*|\n\s*\n")   # 句末標點(含收尾引號)或空行段落

DDL = """
CREATE TABLE IF NOT EXISTS philosophy_chunk (
  chunk_id   SERIAL PRIMARY KEY,
  text_id    INT NOT NULL REFERENCES philosophy_work_text(text_id) ON DELETE CASCADE,
  work_id    INT NOT NULL REFERENCES philosophy_work(work_id) ON DELETE CASCADE,
  chunk_seq  INT NOT NULL,
  content    TEXT NOT NULL,
  char_start INT NOT NULL,
  char_end   INT NOT NULL,
  token_est  INT NOT NULL,
  UNIQUE(text_id, chunk_seq)
);
CREATE INDEX IF NOT EXISTS idx_philosophy_chunk_work ON philosophy_chunk(work_id);
"""


def est_tokens(s):
    cjk = len(CJK.findall(s))
    return int(cjk + (len(s) - cjk) * 0.25)   # CJK ~1 tok/char、拉丁 ~0.25(粗估;P2 tokenizer 精算)


def chunk_positions(content):
    """回 [(char_start, char_end)];塊在語義邊界切、~TARGET_TOK、相鄰重疊 ~OVERLAP_TOK。
    無語義邊界的超長段(如無標點的 CJK 古籍)以二分硬切,保證無塊超嵌入窗。"""
    sem = [0]
    for m in BOUND.finditer(content):
        if m.end() > sem[-1]:
            sem.append(m.end())
    if sem[-1] != len(content):
        sem.append(len(content))
    bounds = [0]                                   # 補硬邊界:語義邊界間過長 → 二分插硬切點(防超窗)
    for b in sem[1:]:
        prev = bounds[-1]
        while est_tokens(content[prev:b]) > TARGET_TOK * 1.4:
            lo, hi = prev + 1, b
            while lo < hi:
                mid = (lo + hi) // 2
                if est_tokens(content[prev:mid]) < TARGET_TOK:
                    lo = mid + 1
                else:
                    hi = mid
            if lo >= b:
                break
            bounds.append(lo)
            prev = lo
        bounds.append(b)
    bounds = sorted(set(bounds))
    out, start = [], 0
    while start < len(content):
        end = len(content)
        for b in bounds:
            if b <= start:
                continue
            end = b
            if est_tokens(content[start:b]) >= TARGET_TOK:
                break
        out.append((start, end))
        if end >= len(content):
            break
        nxt = end                                   # 回退 ~OVERLAP_TOK 到最近邊界
        for b in bounds:
            if start < b < end and est_tokens(content[b:end]) <= OVERLAP_TOK:
                nxt = b
                break
        start = nxt if nxt > start else end          # 保證前進、防無限迴圈
    return out


def main():
    force = "--force" in sys.argv
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute(DDL)
            if force:
                cur.execute("TRUNCATE philosophy_chunk RESTART IDENTITY")
            # T5 就緒偵測:itext_id 欄(T0 遷移)與 knowledge_item_text 表皆在才走 item 路徑
            cur.execute("SELECT count(*) FROM information_schema.columns "
                        "WHERE table_name='philosophy_chunk' AND column_name='itext_id'")
            has_col = cur.fetchone()[0] > 0
            cur.execute("SELECT to_regclass('knowledge_item_text')")
            itext_ok = has_col and cur.fetchone()[0] is not None
            cur.execute("SELECT DISTINCT text_id FROM philosophy_chunk WHERE text_id IS NOT NULL")
            done_text = {r[0] for r in cur.fetchall()}
            done_itext = set()
            if itext_ok:
                cur.execute("SELECT DISTINCT itext_id FROM philosophy_chunk WHERE itext_id IS NOT NULL")
                done_itext = {r[0] for r in cur.fetchall()}
        with db.transaction(conn) as cur:
            # T-1 稽核閘:review_flag(true=誤配、NULL=未稽核)一律不入塊
            phil_sql = ("SELECT t.text_id, t.work_id, NULL::int AS itext_id, t.content "
                        "FROM philosophy_work_text t JOIN philosophy_work w USING (work_id) "
                        "WHERE NOT w.review_flag")
            if itext_ok:
                cur.execute(phil_sql + " UNION ALL "
                            "SELECT NULL::int, NULL::int, x.itext_id, x.content FROM knowledge_item_text x "
                            "ORDER BY text_id NULLS LAST, itext_id")
            else:
                print("(itext_id 欄/knowledge_item_text 未就緒——先跑 migrate_text_understanding_ddl.py;本輪僅哲學路徑)")
                cur.execute(phil_sql + " ORDER BY text_id")
            rows = cur.fetchall()
        added = 0
        for text_id, work_id, itext_id, content in rows:
            if not content or (itext_id is None and text_id in done_text) or (itext_id in done_itext):
                continue
            positions = chunk_positions(content)
            with db.transaction(conn) as cur:
                for seq, (cs, ce) in enumerate(positions, 1):
                    chunk = content[cs:ce]
                    if itext_ok:
                        cur.execute(
                            "INSERT INTO philosophy_chunk (text_id,work_id,itext_id,chunk_seq,content,char_start,char_end,token_est) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                            (text_id, work_id, itext_id, seq, chunk, cs, ce, est_tokens(chunk)))
                    else:
                        cur.execute(
                            "INSERT INTO philosophy_chunk (text_id,work_id,chunk_seq,content,char_start,char_end,token_est) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s)", (text_id, work_id, seq, chunk, cs, ce, est_tokens(chunk)))
            added += len(positions)
        with db.transaction(conn) as cur:
            cur.execute("SELECT count(*), count(DISTINCT text_id), avg(token_est)::int, max(token_est), "
                        "count(*) FILTER (WHERE token_est>1000) FROM philosophy_chunk")
            n, nt, avg, mx, over = cur.fetchone()
            ni = nx = 0
            if itext_ok:
                cur.execute("SELECT count(*), count(DISTINCT itext_id) FROM philosophy_chunk WHERE itext_id IS NOT NULL")
                nx, ni = cur.fetchone()
        print(f"✓ philosophy_chunk:本次 +{added:,} 塊、共 {n:,} 塊 / {nt} text"
              + (f" + {nx:,} 塊 / {ni} itext" if itext_ok else ""))
        print(f"  token_est: avg {avg} / max {mx} / >1000tok {over} 塊")


if __name__ == "__main__":
    main()
