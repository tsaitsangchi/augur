#!/usr/bin/env python
"""抓公版中文戰略/哲學古典原文入庫 — 本地直抓維基文庫 raw wikitext、零 Claude usage。

🎯 把公版古典(道德經/武經七書/三十六計…)逐字原文落地 philosophy_work_text,
作哲學框架的原典參考/可解釋性素材。本地 urllib 抓 + 程式解析(非 WebFetch 小模型,
故逐字無摘要/改寫),冪等可續(work 已有全文則跳過)、可 cron 排程。

守 #1(本地解析逐字、不靠 AI 摘要改寫→無假兆)· #28(本地優先、零 usage)·
   #15(來源限公版、source_url 可溯源、license DB CHECK=public_domain)· #18。
⚠️ 誠實:古典全文不進預測管線、對量化無 alpha;僅原典參考素材。
⚠️ CLAUDE #29b 傳輸工件(transport artifact):CLASSICS(8 部+thinker 傳記)硬編策展清單為一次性
   seed 載體,內容已落 philosophy_thinker/work/work_text(2026-07-04 稽核實查確認),預設不執行
   (無參數只印矩陣)。新增策展一律走 acquire_knowledge --source manual_curation → promote_knowledge
   管線,不回頭擴充本檔;傳記欄位 DBpedia/Wikidata 覆核與本檔退役列後續、待用戶裁示(#19)。

執行指令矩陣:
  python scripts/fetch_public_domain_classics.py                  # 無參數:印本矩陣(傳輸工件、預設不執行)
  python scripts/fetch_public_domain_classics.py --run [--force]  # 明示重放(冪等;--force 重抓已有全文)
"""
import re
import sys
import time
import urllib.request
import urllib.parse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

UA = {"User-Agent": "augur-research/1.0 (public-domain classics archival)"}
WIKI = "https://zh.wikisource.org/wiki/"
RAW = "https://zh.wikisource.org/w/index.php?title={}&action=raw"

# 公版古典清單:thinker=(name_zh,name,birth,death,nat,bio)
# mode=inline(原文在主頁、==篇==) / subpages(主頁目錄、原文在子頁)
# colon='note'(冒號行=註,濾除,如道德經王弼註) / 'text'(冒號行=原文,去冒號,如唐李問對對話)
CLASSICS = [
    {"work_zh": "道德經", "work_en": "Tao Te Ching", "year": -400, "wtype": "philosophy_classic",
     "thinker": ("老子", "Laozi", -571, -471, "中國", "春秋時期思想家,道家學派創始人,著《道德經》五千言,主張無為、反者道之動。"),
     "mode": "inline", "page": "道德經 (王弼本)", "colon": "note"},
    {"work_zh": "吳子兵法", "work_en": "Wuzi", "year": -400, "wtype": "strategy_classic",
     "thinker": ("吳起", "Wu Qi", -440, -381, "中國", "戰國軍事家、政治家,與孫武並稱「孫吳」,著《吳子兵法》。"),
     "mode": "inline", "page": "吳子", "colon": "note"},
    {"work_zh": "六韜", "work_en": "Six Secret Teachings", "year": -400, "wtype": "strategy_classic",
     "thinker": ("姜尚", "Jiang Ziya", -1128, -1015, "中國", "周初軍事家(姜太公),輔佐文武滅商,後世託名其撰《六韜》。"),
     "mode": "inline", "page": "六韜", "colon": "note"},
    {"work_zh": "三略", "work_en": "Three Strategies of Huang Shigong", "year": -200, "wtype": "strategy_classic",
     "thinker": ("黃石公", "Huang Shigong", None, None, "中國", "秦末傳奇隱士,傳授張良兵法,後世託名撰《三略》。"),
     "mode": "inline", "page": "三略", "colon": "note"},
    {"work_zh": "司馬法", "work_en": "Sima Fa", "year": -400, "wtype": "strategy_classic",
     "thinker": ("司馬穰苴", "Sima Rangju", None, None, "中國", "春秋齊國軍事家(田穰苴),《司馬法》託其名輯成。"),
     "mode": "inline", "page": "司馬法", "colon": "note"},
    {"work_zh": "孫臏兵法", "work_en": "Sun Bin's Art of War", "year": -350, "wtype": "strategy_classic",
     "thinker": ("孫臏", "Sun Bin", -380, -316, "中國", "戰國軍事家,孫武後裔,圍魏救趙、馬陵之戰,著《孫臏兵法》。"),
     "mode": "inline", "page": "孫臏兵法", "colon": "note"},
    {"work_zh": "三十六計", "work_en": "Thirty-Six Stratagems", "year": 1500, "wtype": "strategy_classic",
     "thinker": ("檀道濟", "Tan Daoji", None, 436, "中國", "南北朝名將,《三十六計》託其名(實輯成於明清),集兵家詭道之大成。"),
     "mode": "subpages", "page": "三十六計",
     "subs": ["勝戰計", "敵戰計", "攻戰計", "混戰計", "並戰計", "敗戰計"], "colon": "note"},
    {"work_zh": "唐李問對", "work_en": "Questions and Replies between Tang Taizong and Li Weigong",
     "year": 700, "wtype": "strategy_classic",
     "thinker": ("李靖", "Li Jing", 571, 649, "中國", "唐初軍事家,《唐李問對》(武經七書之一)記其與唐太宗論兵。"),
     "mode": "subpages", "page": "唐李問對", "subs": ["卷上", "卷中", "卷下"], "colon": "text"},
]


def fetch_raw(title):
    url = RAW.format(urllib.parse.quote(title, safe="/"))
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def clean(t):
    """wiki markup → 純文字(逐字保留正文)。"""
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)              # <onlyinclude> 等 tag
    t = re.sub(r"\{\{[^{}]*\}\}", "", t)       # 模板(含 {{*|...}})
    t = re.sub(r"\[\[[^\[\]|]*\|([^\[\]]*)\]\]", r"\1", t)  # [[x|y]]→y
    t = re.sub(r"\[\[([^\[\]]*)\]\]", r"\1", t)            # [[x]]→x
    t = re.sub(r"'''?", "", t)
    return t.strip()


def parse_body(raw, colon):
    """有 ==標題== → 按章切;回 [(chapter, content)]。"""
    out, chap, buf = [], None, []
    for line in raw.split("\n"):
        st = line.strip()
        m = re.match(r"^(={2,4})\s*(.+?)\s*\1$", st)
        if m:
            if chap and buf:
                out.append((chap, "\n".join(buf).strip()))
            chap, buf = clean(m.group(2)), []
            continue
        if chap is None or not st:
            continue
        if st[0] in "{|*[":                    # 模板/目錄/category
            continue
        if st.startswith(":"):
            if colon == "note":
                continue
            st = st.lstrip(":").strip()
        c = clean(st)
        if c:
            buf.append(c)
    if chap and buf:
        out.append((chap, "\n".join(buf).strip()))
    return out


def parse_flat(raw, colon):
    """無 ==標題== 的子頁(如唐李問對對話)→ 整頁正文。"""
    buf = []
    for line in raw.split("\n"):
        st = line.strip()
        if not st or st[0] in "{|*[":
            continue
        if st.startswith(":"):
            if colon == "note":
                continue
            st = st.lstrip(":").strip()
        c = clean(st)
        if c:
            buf.append(c)
    return "\n".join(buf).strip()


def collect(c):
    """回 [(chapter, content, source_url)]。"""
    rows = []
    if c["mode"] == "inline":
        raw = fetch_raw(c["page"])
        url = WIKI + urllib.parse.quote(c["page"].replace(" ", "_"), safe="/")
        for chap, content in parse_body(raw, c["colon"]):
            if content:
                rows.append((chap, content, url))
    else:  # subpages
        for sub in c["subs"]:
            title = f"{c['page']}/{sub}"
            url = WIKI + urllib.parse.quote(title.replace(" ", "_"), safe="/")
            try:
                raw = fetch_raw(title)
            except Exception as e:
                print(f"      ⚠ 子頁 {title} 抓取失敗: {e}")
                continue
            if re.search(r"^={2,4}.+={2,4}$", raw, re.M):
                for chap, content in parse_body(raw, c["colon"]):
                    if content:
                        rows.append((f"{sub}‧{chap}", content, url))
            else:
                content = parse_flat(raw, c["colon"])
                if content:
                    rows.append((sub, content, url))
            time.sleep(0.5)  # 友善步調
    return rows


def upsert_thinker(cur, th):
    name_zh, name, birth, death, nat, bio = th
    cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s", (name_zh,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute(
        "INSERT INTO philosophy_thinker (name,name_zh,birth_year,death_year,nationality,bio) "
        "VALUES (%s,%s,%s,%s,%s,%s) RETURNING thinker_id",
        (name, name_zh, birth, death, nat, bio))
    return cur.fetchone()[0]


def upsert_work(cur, c, thinker_id):
    cur.execute("SELECT work_id FROM philosophy_work WHERE title_zh=%s", (c["work_zh"],))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute(
        "INSERT INTO philosophy_work (thinker_id,title,title_zh,year,work_type,note) "
        "VALUES (%s,%s,%s,%s,%s,%s) RETURNING work_id",
        (thinker_id, c["work_en"], c["work_zh"], c["year"], c["wtype"], "公版原典、維基文庫"))
    return cur.fetchone()[0]


def main():
    if "--run" not in sys.argv:
        print(__doc__.split("執行指令矩陣:")[1].strip())
        return
    force = "--force" in sys.argv
    with db.connect() as conn:
        for c in CLASSICS:
            with db.transaction(conn) as cur:
                tid = upsert_thinker(cur, c["thinker"])
                wid = upsert_work(cur, c, tid)
                cur.execute("SELECT count(*) FROM philosophy_work_text WHERE work_id=%s", (wid,))
                existing = cur.fetchone()[0]
            if existing and not force:
                print(f"⏭  《{c['work_zh']}》已有 {existing} 篇全文,跳過(--force 重抓)")
                continue
            try:
                rows = collect(c)
            except Exception as e:
                print(f"❌ 《{c['work_zh']}》抓取失敗: {e}")
                continue
            # 濾噪音:卷分隔標題章(內容過短、如六韜「文韜」)、音義附錄(讀音註非原文)
            rows = [(ch, ct, u) for ch, ct, u in rows if len(ct) >= 15 and "音義" not in ch]
            if not rows:
                print(f"❌ 《{c['work_zh']}》解析無內容(來源結構或不適配)")
                continue
            with db.transaction(conn) as cur:
                if force:
                    cur.execute("DELETE FROM philosophy_work_text WHERE work_id=%s", (wid,))
                for seq, (chap, content, url) in enumerate(rows, 1):
                    cur.execute(
                        "INSERT INTO philosophy_work_text (work_id,chapter,seq,content,source_url,license) "
                        "VALUES (%s,%s,%s,%s,%s,'public_domain')", (wid, chap, seq, content, url))
            total = sum(len(r[1]) for r in rows)
            print(f"✓ 《{c['work_zh']}》{c['thinker'][0]}: {len(rows)} 篇/章、{total:,} 字入庫")


if __name__ == "__main__":
    main()
