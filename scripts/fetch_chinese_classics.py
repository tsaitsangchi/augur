#!/usr/bin/env python
"""窮舉補齊中文諸子經典 — 維基文庫子頁全文,補 seed thinker(孔孟莊墨荀韓…)之著作。

🎯 補跑(fetch_all_thinker_works)只用 Gutenberg 英文、漏了中文哲學家的維基文庫著作。
   本 script 以 MediaWiki API 取每部諸子的子頁清單(各篇)、逐子頁抓逐字全文,對映現有 thinker。
   哲學素養庫窮舉補齊之中文缺口。本地零 usage、逐字無 AI 摘要、冪等(已有全文則跳)。
守 #1(逐字、禁 AI 摘要)· #15(公版可溯源 license CHECK)· #28(本地零 usage)· #18。
⚠️ CLAUDE #29b 傳輸工件(transport artifact):CLASSICS(12 部諸子對映)硬編策展清單為一次性
   seed 載體,內容已落 philosophy_thinker/work/work_text(2026-07-04 稽核實查確認),預設不執行
   (無參數只印矩陣)。新增策展一律走 acquire_knowledge --source manual_curation → promote_knowledge
   管線,不回頭擴充本檔;本檔退役列後續、待用戶裁示(#19)。

執行指令矩陣:
  python scripts/fetch_chinese_classics.py                  # 無參數:印本矩陣(傳輸工件、預設不執行)
  python scripts/fetch_chinese_classics.py --run [--force]  # 明示重放(冪等;--force 重抓已有全文)
"""
import re
import sys
import json
import time
import socket
import urllib.request
import urllib.parse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

socket.setdefaulttimeout(30)
UA = {"User-Agent": "augur-research/1.0 (public-domain classics archival)"}
WIKI = "https://zh.wikisource.org/wiki/"

# (work_zh, thinker_zh);thinker 對映 seed 已建者(by name_zh)、無則建
CLASSICS = [
    ("論語", "孔子"), ("孟子", "孟子"), ("莊子", "莊子"), ("墨子", "墨子"),
    ("荀子", "荀子"), ("韓非子", "韓非子"), ("列子", "列子"), ("公孫龍子", "公孫龍"),
    ("管子", "管仲"), ("商君書", "商鞅"), ("鶡冠子", "鶡冠子"), ("尹文子", "尹文"),
]
SKIP_SUB = ("全覽", "各篇", "目錄", "參見", "序", "四庫全書", "凡例")


def api_subpages(prefix):
    url = ("https://zh.wikisource.org/w/api.php?action=query&list=allpages&apprefix="
           + urllib.parse.quote(prefix + "/") + "&aplimit=300&format=json")
    for attempt in range(5):
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode())
            return [p["title"] for p in d.get("query", {}).get("allpages", [])]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(25)
            else:
                raise
    raise RuntimeError("429 多次重試仍失敗")


def fetch_raw(title):
    url = "https://zh.wikisource.org/w/index.php?title=" + urllib.parse.quote(title, safe="/") + "&action=raw"
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace")


def clean(raw):
    t = raw
    t = re.sub(r"-\{(?:[a-zA-Z-]+:)?([^{}|;]*)(?:;[^{}]*)?\}-", r"\1", t)   # MediaWiki 繁簡轉換 -{X}- → X
    for _ in range(6):                                          # 巢狀/多行模板多輪清(-{}-先清否則其 { 阻斷)
        t2 = re.sub(r"\{\{[^{}]*\}\}", "", t)
        if t2 == t:
            break
        t = t2
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"^\s*=+.*?=+\s*$", "", t, flags=re.M)           # 去章標題行(1-4 等號、含單=;目錄頁去後即空)
    t = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"'''?", "", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def main():
    if "--run" not in sys.argv:
        print(__doc__.split("執行指令矩陣:")[1].strip())
        return
    force = "--force" in sys.argv
    added = 0
    with db.connect() as conn:
        for work_zh, thinker_zh in CLASSICS:
            with db.transaction(conn) as cur:
                cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s", (thinker_zh,))
                r = cur.fetchone()
                if r:
                    tid = r[0]
                else:
                    cur.execute("INSERT INTO philosophy_thinker (name,name_zh,nationality) VALUES (%s,%s,'中國') RETURNING thinker_id",
                                (thinker_zh, thinker_zh))
                    tid = cur.fetchone()[0]
                cur.execute("SELECT work_id FROM philosophy_work WHERE title_zh=%s", (work_zh,))
                r = cur.fetchone()
                if r:
                    wid = r[0]
                else:
                    cur.execute("INSERT INTO philosophy_work (thinker_id,title,title_zh,work_type,note) "
                                "VALUES (%s,%s,%s,'philosophy_classic','公版原典、維基文庫') RETURNING work_id", (tid, work_zh, work_zh))
                    wid = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM philosophy_work_text WHERE work_id=%s", (wid,))
                if cur.fetchone()[0] > 0:
                    if not force:
                        print(f"⏭  《{work_zh}》已有全文,跳過")
                        continue
                    cur.execute("DELETE FROM philosophy_work_text WHERE work_id=%s", (wid,))
            try:
                subs = api_subpages(work_zh)
            except Exception as e:
                print(f"❌ 《{work_zh}》子頁 API 失敗: {e}")
                continue
            rows = []
            for sub in subs:
                leaf = sub.split("/")[-1]
                if any(k in leaf for k in SKIP_SUB):
                    continue
                try:
                    content = clean(fetch_raw(sub))
                    time.sleep(0.25)
                except Exception:
                    continue
                if len(content) > 50:
                    rows.append((leaf, content, WIKI + urllib.parse.quote(sub.replace(" ", "_"), safe="/")))
            if not rows:
                print(f"❌ 《{work_zh}》無子頁全文(維基文庫結構特殊或無)")
                continue
            with db.transaction(conn) as cur:
                for seq, (ch, ct, url) in enumerate(rows, 1):
                    cur.execute("INSERT INTO philosophy_work_text (work_id,chapter,seq,content,source_url,license) "
                                "VALUES (%s,%s,%s,%s,%s,'public_domain')", (wid, ch, seq, ct, url))
            total = sum(len(r[1]) for r in rows)
            print(f"✓ 《{work_zh}》{thinker_zh}: {len(rows)} 篇、{total:,} 字")
            added += 1
    print(f"\n完成:窮舉補中文諸子 {added} 部")


if __name__ == "__main__":
    main()
