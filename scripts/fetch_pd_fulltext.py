#!/usr/bin/env python
"""公版 items 全文抓取(深抓計畫 S3/P8 方案A;K3;源專屬解析器計畫 20260712 T2)。

🎯 這支在做什麼(白話):對「license_regime='public_domain' 之 active 源」的 knowledge_item(有 url、
   尚無全文)逐件抓純文字→knowledge_item_text;抓法依 knowledge_source.adapter_config.fulltext
   策略分派(#29b 策略住 DB):url_template(IA _djvu.txt)/edgar_archive(組檔案 URL)/fraser_api
   (title API 取 location.textUrl);無策略=直鏈 text/plain(向後相容)。html_strip 模式複用
   fetch_oa_fulltext.strip_html 逐字剝標;不可抓=誠實記 fulltext_status(upsert,策略源之
   skip_ctype 舊章自動重試);每源 pace 讀 DB。

守 #1(逐字零 AI)· #6(冪等)· #25(--limit/--source 首輪最小)· 憲章三軌(唯 public_domain 源)。

執行指令矩陣:
  python scripts/fetch_pd_fulltext.py                                # 現況:可抓件數(唯讀)
  python scripts/fetch_pd_fulltext.py --run --limit 3                # 首輪最小(#25)
  python scripts/fetch_pd_fulltext.py --run --limit 3 --source fraser_stlouisfed   # 單源最小
  python scripts/fetch_pd_fulltext.py --run --limit 200 --source internet_archive  # IA 分批放量(D3=200/批)
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request

import _bootstrap  # noqa: F401
from augur.core import db
from fetch_oa_fulltext import strip_html  # 同目錄 script;逐字剝標(#1)共用單一實作

UA = {"User-Agent": "augur-research/1.0 (public-domain full-text archival)",
      "Accept": "*/*"}   # Accept 必帶:FRASER 等 WAF 對無 Accept 之請求靜默掛住(2026-07-12 實證)

Q = """
SELECT i.item_id, i.url, i.external_id, i.staging_id, s.pace_seconds, s.adapter_config
FROM knowledge_item i
JOIN knowledge_source s ON s.source_key = i.source_key
WHERE s.approval_status='active' AND s.license_regime='public_domain'
  AND i.url IS NOT NULL AND i.url <> ''
  AND (%(src)s IS NULL OR i.source_key = %(src)s)
  AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id)
  AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status f WHERE f.item_id = i.item_id)
ORDER BY i.item_id
"""


def _status(cur, item_id, status, reason):
    cur.execute("INSERT INTO knowledge_fulltext_status (item_id, status, reason) VALUES (%s,%s,%s) "
                "ON CONFLICT (item_id) DO UPDATE SET status=EXCLUDED.status, reason=EXCLUDED.reason, "
                "checked_at=now()", (item_id, status, (reason or "")[:80]))


def resolve_target(cur, item_id, url, external_id, staging_id, acfg):
    """依 adapter_config.fulltext 策略解析 (抓取URL, 內容模式, headers);解析失敗回 (None, 原因, None)。"""
    ft = (acfg or {}).get("fulltext")
    if not ft:
        return url, "text", dict(UA)
    strat, mode = ft.get("strategy"), ft.get("content", "text")
    if strat == "url_template":
        if not external_id:
            return None, "url_template: 缺 external_id", None
        return ft["template"].replace("{external_id}", external_id), mode, dict(UA)
    if strat == "edgar_archive":
        cur.execute("SELECT payload->>'cik' FROM knowledge_staging WHERE staging_id=%s", (staging_id,))
        row = cur.fetchone()
        cik = row[0] if row else None
        adsh, _, fname = (url or "").partition(":")
        if not (cik and adsh and fname):
            return None, "edgar_archive: cik/adsh/filename 組件缺", None
        contact = os.environ.get("UNPAYWALL_EMAIL", "research contact")
        return (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/{fname}",
                mode, {**UA, "User-Agent": f"augur-research/1.0 ({contact})"})
    if strat == "fraser_api":
        m = re.search(r"-(\d+)$", url or "")
        if not m:
            return None, "fraser_api: url 尾無 title id", None
        hdrs = dict(UA)
        ah = (acfg or {}).get("auth_header")
        v = os.environ.get(ah.get("env", ""), "") if ah else ""
        if v:
            hdrs[ah["name"]] = v
        api = json.loads(urllib.request.urlopen(urllib.request.Request(
            f"https://fraser.stlouisfed.org/api/title/{m.group(1)}?format=json", headers=hdrs),
            timeout=60).read().decode())
        tu = ((api.get("records") or [{}])[0].get("location") or {}).get("textUrl") or []
        if not tu:
            return None, "fraser_api: 無 textUrl(掃描件無 born-digital 文字)", None
        return tu[0], mode, dict(UA)
    return None, f"未知 fulltext strategy: {strat}", None


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--source", default=None)
    args = ap.parse_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(Q, {"src": args.source})
        rows = cur.fetchall()
        print(f"可抓件數(pd 源、未有全文、未 skip{'、源=' + args.source if args.source else ''}):{len(rows)}")
        if not args.run:
            print(__doc__.split("執行指令矩陣:")[1])
            return 0
        ok = skip = fail = 0
        for item_id, url, external_id, staging_id, pace, acfg in rows[: args.limit]:
            time.sleep(float(pace or 1.0))
            cur.execute("SAVEPOINT sp_item")
            try:
                target, mode, hdrs = resolve_target(cur, item_id, url, external_id, staging_id, acfg)
                if target is None:
                    _status(cur, item_id, "skip_fetch_error", mode)   # mode 位=解析失敗原因
                    skip += 1
                    continue
                r = urllib.request.urlopen(urllib.request.Request(target, headers=hdrs), timeout=60)
                ctype = (r.headers.get("Content-Type") or "").lower()
                raw = r.read().decode("utf-8", errors="replace")
                if mode == "html_strip" and "text/html" in ctype:
                    text = strip_html(raw)
                elif "text/plain" in ctype:
                    text = raw
                else:
                    _status(cur, item_id, "skip_ctype", f"{mode}|{ctype}")
                    skip += 1
                    continue
                if len(text) < 2000:
                    _status(cur, item_id, "skip_short", str(len(text)))
                    skip += 1
                    continue
                cur.execute("INSERT INTO knowledge_item_text (item_id, seq, content, language, source_url, "
                            "license, source_type, access_scope) VALUES (%s,1,%s,'en',%s,'public_domain','pd_fetch','public')",
                            (item_id, text, target))
                ok += 1
            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT sp_item")
                _status(cur, item_id, "skip_fetch_error", str(e))
                fail += 1
        print(f"✓ 抓 {ok}、skip {skip}、error {fail}(fulltext_status 誠實留痕;→ build_sentences --scope items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
