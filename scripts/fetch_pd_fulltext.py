#!/usr/bin/env python
"""公版 items 全文抓取(深抓計畫 S3/P8 方案A:born-digital 純文字;K 計畫 K3)。

🎯 這支在做什麼(白話):對「license_regime='public_domain' 之 active 源」的 knowledge_item(有 url、
   尚無全文)逐件抓純文字→knowledge_item_text(license='public_domain', access_scope='public');
   content-type 非 text/plain=skip_nontext 誠實記 fulltext_status(P8:OCR 路徑不啟動);每源 pace 讀 DB。

守 #1(逐字零 AI)· #6(NOT EXISTS 冪等)· #25(--limit 首輪最小)· 憲章三軌(唯 public_domain 源)。

執行指令矩陣:
  python scripts/fetch_pd_fulltext.py               # 現況:可抓件數(唯讀)
  python scripts/fetch_pd_fulltext.py --run --limit 3   # 首輪最小(#25)
  python scripts/fetch_pd_fulltext.py --run --limit 200 # 放量(源健康確認後)
"""
import argparse
import sys
import time
import urllib.request

import _bootstrap  # noqa: F401
from augur.core import db

UA = {"User-Agent": "augur-research/1.0 (public-domain full-text archival)"}

Q = """
SELECT i.item_id, i.url, s.pace_seconds FROM knowledge_item i
JOIN knowledge_source s ON s.source_key = i.source_key
WHERE s.approval_status='active' AND s.license_regime='public_domain'
  AND i.url IS NOT NULL AND i.url <> ''
  AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id)
  AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status f WHERE f.item_id = i.item_id)
ORDER BY i.item_id
"""


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--limit", type=int, default=3)
    args = ap.parse_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(Q)
        rows = cur.fetchall()
        print(f"可抓件數(pd 源、未有全文、未 skip):{len(rows)}")
        if not args.run:
            print(__doc__.split("執行指令矩陣:")[1])
            return 0
        ok = skip = fail = 0
        for item_id, url, pace in rows[: args.limit]:
            time.sleep(float(pace or 1.0))
            cur.execute("SAVEPOINT sp_item")
            try:
                r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60)
                ctype = (r.headers.get("Content-Type") or "").lower()
                if "text/plain" not in ctype:
                    cur.execute("INSERT INTO knowledge_fulltext_status (item_id, status, reason) "
                                "VALUES (%s,'skip_ctype',%s) ON CONFLICT DO NOTHING", (item_id, ctype[:80]))
                    skip += 1
                    continue
                text = r.read().decode("utf-8", errors="replace")
                if len(text) < 2000:
                    cur.execute("INSERT INTO knowledge_fulltext_status (item_id, status, reason) "
                                "VALUES (%s,'skip_short',%s) ON CONFLICT DO NOTHING", (item_id, str(len(text))))
                    skip += 1
                    continue
                cur.execute("INSERT INTO knowledge_item_text (item_id, seq, content, language, source_url, "
                            "license, source_type, access_scope) VALUES (%s,1,%s,'en',%s,'public_domain','pd_fetch','public')",
                            (item_id, text, url))
                ok += 1
            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT sp_item")
                cur.execute("INSERT INTO knowledge_fulltext_status (item_id, status, reason) "
                            "VALUES (%s,'skip_fetch_error',%s) ON CONFLICT DO NOTHING", (item_id, str(e)[:80]))
                fail += 1
        print(f"✓ 抓 {ok}、skip {skip}、error {fail}(fulltext_status 誠實留痕;→ build_sentences --scope items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
