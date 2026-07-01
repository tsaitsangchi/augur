#!/usr/bin/env python
"""遍歷 philosophy_thinker、抓每位哲學家之公版著作全文入庫(Gutenberg、零 usage)。

🎯 對 philosophy_thinker 每位,經 gutendex 找其 Gutenberg 公版著作,本地下載解析逐字入庫
(work + work_text),補哲學素養框架(憲章 v1.17.0)之著作全文。去重(title 已存跳過)、限速、冪等可續。

守 #1(逐字無 AI 摘要、來源實證 Gutenberg)· #15(限公版 license DB CHECK)· #28(本地零 usage)·
   #25(限速友善)· #18。
⚠️ 僅公版(現代/在世哲學家版權著作 Gutenberg 無→自然不抓、合法);冷僻哲學家 Gutenberg 多無。
⚠️ 哲學全文量化零價值、不進預測管線(憲章 v1.17.0 邊界)。

用法:PYTHONPATH=src python scripts/fetch_all_thinker_works.py [--per-author N] [--limit M]
"""
import re
import sys
import time
import json
import urllib.request
import urllib.parse

from augur.core import db

UA = {"User-Agent": "augur-research/1.0 (public-domain philosophy archival)"}
CHAP_RE = r"^\s*(BOOK [IVXLC]+|THE [A-Z]+ BOOK|CHAPTER [IVXLC]+|MEDITATION [IVX]+|PART [IVX]+|SECTION [IVX]+)\.?\s*$"


def gutendex_works(name, per_author):
    """gutendex 找該作者之公版 txt 著作;回 [(gid, title, txt_url)]。"""
    surname = name.split()[-1].lower()
    url = "https://gutendex.com/books?search=" + urllib.parse.quote(name)
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode())
    except Exception:
        return []
    works = []
    for b in d.get("results", []):
        if b.get("languages") != ["en"]:        # 只取英文版本(避免德/法原文與重複多語版)
            continue
        authors = [a["name"].lower() for a in b.get("authors", [])]
        if not any(surname in a for a in authors):
            continue
        txt = None
        for k, u in b["formats"].items():
            if "text/plain" in k and not u.endswith(".zip"):
                txt = u
                break
        if txt:
            works.append((b["id"], b["title"], txt))
    return works[:per_author]


def download(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read().decode("utf-8", "replace")


def strip_gutenberg(txt):
    s = re.search(r"\*\*\* ?START OF TH[EI][^*]*\*\*\*", txt)
    start = s.end() if s else 0
    e = re.search(r"\*\*\* ?END OF TH[EI][^*]*\*\*\*", txt) or re.search(r"\nEnd of (?:the )?Project Gutenberg", txt)
    end = e.start() if e else len(txt)
    return txt[start:end].strip()


def split_chapters(body):
    ms = list(re.finditer(CHAP_RE, body, re.M))
    if len(ms) < 2:
        paras, chunks, buf = re.split(r"\n\s*\n", body), [], ""
        for p in paras:
            buf += p.strip() + "\n\n"
            if len(buf) > 8000:
                chunks.append(buf.strip()); buf = ""
        if buf.strip():
            chunks.append(buf.strip())
        return [(f"段{i}", c) for i, c in enumerate(chunks, 1) if len(c) > 60]
    out = []
    pre = re.sub(r"\n{3,}", "\n\n", body[:ms[0].start()]).strip()
    if len(pre) > 500:
        out.append(("前言", pre))
    for i, m in enumerate(ms):
        title = re.sub(r"\s+", " ", m.group(1).strip())[:60]
        content = re.sub(r"\n{3,}", "\n\n", body[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(body)]).strip()
        if len(content) > 60:
            out.append((title, content))
    return out


def main():
    per_author = int(sys.argv[sys.argv.index("--per-author") + 1]) if "--per-author" in sys.argv else 6
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 10**9
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT thinker_id, name FROM philosophy_thinker WHERE name IS NOT NULL ORDER BY thinker_id")
            thinkers = cur.fetchall()
            cur.execute("SELECT lower(title) FROM philosophy_work")
            seen = {r[0] for r in cur.fetchall()}
        authors_hit = works_added = 0
        for idx, (tid, name) in enumerate(thinkers):
            if idx >= limit:
                break
            works = gutendex_works(name, per_author)
            time.sleep(0.4)
            if not works:
                continue
            got = 0
            for gid, title, txt_url in works:
                if title.lower() in seen:
                    continue
                try:
                    rows = split_chapters(strip_gutenberg(download(txt_url)))
                except Exception:
                    continue
                if not rows:
                    continue
                src = f"https://www.gutenberg.org/ebooks/{gid}"
                with db.transaction(conn) as cur:
                    cur.execute("INSERT INTO philosophy_work (thinker_id,title,title_zh,year,work_type,note) "
                                "VALUES (%s,%s,%s,%s,%s,%s) RETURNING work_id",
                                (tid, title, None, None, "philosophy_classic", "公版原典、Project Gutenberg(自動遍歷)"))
                    wid = cur.fetchone()[0]
                    for seq, (chap, content) in enumerate(rows, 1):
                        cur.execute("INSERT INTO philosophy_work_text (work_id,chapter,seq,content,source_url,license) "
                                    "VALUES (%s,%s,%s,%s,%s,'public_domain')", (wid, chap, seq, content, src))
                seen.add(title.lower())
                works_added += 1
                got += 1
                time.sleep(1.2)            # Gutenberg 友善限速
            if got:
                authors_hit += 1
                print(f"✓ {name}: +{got} 部")
    print(f"\n完成:{authors_hit} 位哲學家有公版著作、新增 {works_added} 部全文")


if __name__ == "__main__":
    main()
