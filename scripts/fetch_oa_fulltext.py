#!/usr/bin/env python
"""T1 OA 全文擷取 — knowledge_item(external_id 為 DOI、尚無全文)→ Unpaywall OA 判定 → knowledge_item_text。

🎯 這支在做什麼(白話):對 harvest 落地的知識條目(knowledge_item),拿 DOI 問 Unpaywall
   `best_oa_location`;**license 白名單四值才入庫**(public_domain / cc-by / cc-by-sa / cc0;
   Unpaywall 之 US-Gov 'pd' 對映 'public_domain';NC/ND/null 版權未明一律 skip 記數、停在 metadata)
   → 抓 OA 全文(content-type 限 text/html、text/plain;**PDF 一律跳過記數**)→ 規則剝 HTML 標籤
   (零 AI、逐字)→ 分段(8000 字/seq)寫 `knowledge_item_text`(license 逐字、source_url 可溯源)。
守 #1(逐字全文、license/來源可溯源、零 AI 摘要)· 憲章 v1.20.0(公版+CC 白名單雙軌、版權未明停 metadata)·
   #17/#24(0.5s 步調、連 5 錯熔斷、per-DOI 錯誤續下筆)· #6(WHERE NOT EXISTS 冪等、逐 item commit 可續)·
   #28(本地零 usage)· CLAUDE #29。

執行指令矩陣:
  python scripts/fetch_oa_fulltext.py                       # 無參數:印矩陣+待抓統計(不打 API)
  python scripts/fetch_oa_fulltext.py --limit 3             # 最小驗證(#25):只跑 3 筆 DOI
  python scripts/fetch_oa_fulltext.py --domain energy_materials --limit 50
  python scripts/fetch_oa_fulltext.py --domain finance_mgmt # 圈域全跑(背景批)
  # 需環境變數 UNPAYWALL_EMAIL(Unpaywall 要求聯絡信箱)
"""
import os
import re
import sys
import html
import json
import time
import socket
import argparse
import urllib.parse
import urllib.request

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

socket.setdefaulttimeout(60)
UA = {"User-Agent": "augur-knowledge/1.0 (OA fulltext; contact via UNPAYWALL_EMAIL)"}
PACE_SEC = 0.5        # Unpaywall 要求的禮貌步調(#17)
BREAK_AFTER = 5       # 連續錯誤熔斷(系統性故障不硬衝)
SEG_CHARS = 8000      # item_text 分段長(UNIQUE(item_id,seq) 冪等鍵配套)
MIN_CHARS = 200       # 剝標後過短=非全文(landing/擋牆殘頁),誠實 skip 記數不入庫
LICENSE_MAP = {       # Unpaywall license → DB CHECK 白名單四值;其餘(nc/nd/null/出版社專屬…)一律 skip
    "cc-by": "cc-by", "cc-by-sa": "cc-by-sa", "cc0": "cc0",
    "pd": "public_domain", "public-domain": "public_domain", "publicdomain": "public_domain",
}
CJK = re.compile(r"[一-鿿㐀-䶿豈-﫿]")
DOI_PREFIX = re.compile(r"(?i)^(https?://(dx\.)?doi\.org/|doi:)")

_last_call = [0.0]


def _pace():
    wait = _last_call[0] + PACE_SEC - time.time()
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.time()


def http_get(url, max_bytes=8_000_000):
    """步調受控 GET;回 (content_type_lower, body_bytes)。"""
    _pace()
    resp = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90)
    return (resp.headers.get("Content-Type") or "").lower(), resp.read(max_bytes)


def strip_html(raw):
    """規則剝標(零 AI、確定性):去 script/style/註解 → 塊級標籤換行 → 去標籤 → 實體還原 → 空白收斂。"""
    s = re.sub(r"(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>", " ", raw)
    s = re.sub(r"(?s)<!--.*?-->", " ", s)
    s = re.sub(r"(?i)</?(p|div|br|li|tr|h[1-6]|blockquote|section|article)[^>]*>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()


def detect_language(text):
    """確定性語言規則(text 計畫 T3 同式、可重現 #15):CJK 占比 >30% → 'zh',否則 'en'。"""
    return "zh" if text and len(CJK.findall(text)) / len(text) > 0.30 else "en"


def norm_doi(external_id):
    """external_id → 純 DOI('10.…');非 DOI 回 None(不猜測)。"""
    v = DOI_PREFIX.sub("", (external_id or "").strip())
    return v if v.startswith("10.") else None


# DOI 條目篩選(external_id 容納 harvest 各源之 doi 寫法)+ 冪等(已有全文不重抓)
PENDING_WHERE = """
  (i.external_id LIKE '10.%%' OR i.external_id ILIKE 'https://doi.org/10.%%'
   OR i.external_id ILIKE 'http://doi.org/10.%%' OR i.external_id ILIKE 'https://dx.doi.org/10.%%'
   OR i.external_id ILIKE 'http://dx.doi.org/10.%%' OR i.external_id ILIKE 'doi:10.%%')
  AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id)
"""


def tables_missing(cur):
    """先決檢查:knowledge_item(計畫② harvest)與 knowledge_item_text(計畫③ T0)須已建。"""
    cur.execute("SELECT to_regclass('knowledge_item'), to_regclass('knowledge_item_text')")
    item, itext = cur.fetchone()
    out = []
    if not item:
        out.append("knowledge_item(先跑 scripts/harvest_knowledge.py 建表)")
    if not itext:
        out.append("knowledge_item_text(先跑 scripts/migrate_text_understanding_ddl.py)")
    return out


def print_pending_stats(cur, domain):
    sql = f"SELECT i.domain, count(*) FROM knowledge_item i WHERE {PENDING_WHERE}"
    params = []
    if domain:
        sql += " AND i.domain = %s"
        params.append(domain)
    cur.execute(sql + " GROUP BY 1 ORDER BY 2 DESC", params)
    rows = cur.fetchall()
    print("待抓統計(有 DOI、尚無 item_text):" + ("(無)" if not rows else ""))
    for d, n in rows:
        print(f"  {d:24} {n} 筆")


def fetch_one(conn, item_id, doi, email, stats):
    """單筆 DOI 全流程;回 'ok' 或 skip 原因字串;例外由呼叫端捕捉計 error。"""
    q = urllib.parse.quote(doi, safe="/")
    _, body = http_get(f"https://api.unpaywall.org/v2/{q}?email={urllib.parse.quote(email)}")
    r = json.loads(body.decode())
    loc = r.get("best_oa_location") or {}
    if not (r.get("is_oa") and loc.get("url")):
        return "skip_no_oa"
    lic = LICENSE_MAP.get((loc.get("license") or "").strip().lower())
    if not lic:                                   # NC/ND/null 版權未明 → 停 metadata(憲章 v1.20.0)
        return "skip_license"
    ctype, body = http_get(loc["url"])
    if "pdf" in ctype:
        return "skip_pdf"                         # PDF v1 誠實不做(text 計畫 T1)
    if not ("text/html" in ctype or "text/plain" in ctype):
        return "skip_ctype"
    text = body.decode("utf-8", errors="replace")
    if "text/html" in ctype:
        text = strip_html(text)
    else:
        text = text.strip()
    if len(text) < MIN_CHARS:
        return "skip_short"
    lang = detect_language(text)
    with db.transaction(conn) as cur:             # 逐 item commit:中斷可續(#6)
        for seq in range(0, len(text), SEG_CHARS):
            cur.execute(
                "INSERT INTO knowledge_item_text (item_id, seq, content, language, source_url, license) "
                "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (item_id, seq) DO NOTHING",
                (item_id, seq // SEG_CHARS + 1, text[seq:seq + SEG_CHARS], lang, loc["url"], lic))
        stats["rows"] += len(range(0, len(text), SEG_CHARS))
    return "ok"


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--domain")
    ap.add_argument("--limit", type=int)
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            missing = tables_missing(cur)
            if args.domain is None and args.limit is None:   # 無參數:安全預設,不打 API
                print(__doc__.split("執行指令矩陣:")[1])
                if missing:
                    print("先決未備,尚無法抓取:\n  " + "\n  ".join(missing))
                else:
                    print_pending_stats(cur, None)
                return
            if missing:
                sys.exit("先決未備:\n  " + "\n  ".join(missing))
            email = os.environ.get("UNPAYWALL_EMAIL")
            if not email:
                sys.exit("需環境變數 UNPAYWALL_EMAIL(Unpaywall 要求任一聯絡信箱)")
            sql = f"SELECT i.item_id, i.external_id FROM knowledge_item i WHERE {PENDING_WHERE}"
            params = []
            if args.domain:
                sql += " AND i.domain = %s"
                params.append(args.domain)
            sql += " ORDER BY i.item_id"
            if args.limit:
                sql += " LIMIT %s"
                params.append(args.limit)
            cur.execute(sql, params)
            todo = [(iid, norm_doi(eid)) for iid, eid in cur.fetchall()]
        stats = {"ok": 0, "rows": 0, "skip_no_oa": 0, "skip_license": 0, "skip_pdf": 0,
                 "skip_ctype": 0, "skip_short": 0, "error": 0}
        streak = 0
        for i, (item_id, doi) in enumerate(todo, 1):
            if not doi:
                continue
            try:
                stats[fetch_one(conn, item_id, doi, email, stats)] += 1
                streak = 0                        # 成功/明確 skip 皆重置熔斷計數
            except Exception as e:
                stats["error"] += 1
                streak += 1
                print(f"  ✗ item {item_id} doi={doi}:{type(e).__name__}: {e}", flush=True)
                if streak >= BREAK_AFTER:
                    print(f"連續 {BREAK_AFTER} 錯 → 熔斷停止(剩 {len(todo) - i} 筆;冪等可續)", flush=True)
                    break
            if i % 25 == 0:
                print(f"  … {i}/{len(todo)}(全文 {stats['ok']} 筆落地)", flush=True)
        print(f"✓ 掃 {len(todo)} 筆 DOI → 全文落地 {stats['ok']} 筆 / item_text +{stats['rows']} 段")
        print(f"  skip:no_oa {stats['skip_no_oa']} / license(版權未明含 NC-ND) {stats['skip_license']} / "
              f"pdf {stats['skip_pdf']} / ctype {stats['skip_ctype']} / short {stats['skip_short']};"
              f"error {stats['error']}")


if __name__ == "__main__":
    main()
