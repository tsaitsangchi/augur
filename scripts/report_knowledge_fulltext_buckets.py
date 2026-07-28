#!/usr/bin/env python
"""知識全文終態分桶報告（FT-COV-DASH P0）— 唯讀、零外部 API。

🎯 這支在做什麼(白話):對每個 domain 印 items／answerable／terminal_blocked／pending
   （＋舊式 length>200 對照欄），對齊 CLAUDE #29(b)「license 允許的可檢索終態」分桶，
   禁止把 skip_*／blocked 或短文 ERP 讀成「沒抓」。數字皆 live SQL，非估算。

守 #1 #9 #15 #28 #29；計畫 FT-COV §3.2／§6.2；FZ-keep。

執行指令矩陣:
  python scripts/report_knowledge_fulltext_buckets.py              # 印分桶矩陣（唯讀）
  python scripts/report_knowledge_fulltext_buckets.py --json       # JSON stdout
  python scripts/report_knowledge_fulltext_buckets.py --limit 20   # 多印幾個 domain
  python scripts/report_knowledge_fulltext_buckets.py --selftest   # 免 DB 純紅綠
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

BUCKET_SQL = """
WITH ans AS (
  SELECT DISTINCT t.item_id
  FROM knowledge_item_text t
  JOIN knowledge_sentence s ON s.itext_id = t.itext_id
  JOIN knowledge_sentence_embedding e ON e.sent_id = s.sent_id
),
txt AS (SELECT DISTINCT item_id FROM knowledge_item_text),
blk AS (SELECT DISTINCT item_id FROM knowledge_fulltext_status),
legacy AS (SELECT DISTINCT item_id FROM knowledge_item_text WHERE length(content) > 200)
SELECT i.domain,
  count(*)::bigint AS items,
  count(*) FILTER (WHERE a.item_id IS NOT NULL)::bigint AS answerable,
  count(*) FILTER (WHERE b.item_id IS NOT NULL AND t.item_id IS NULL)::bigint AS terminal_blocked,
  count(*) FILTER (WHERE t.item_id IS NULL AND b.item_id IS NULL)::bigint AS pending,
  count(*) FILTER (WHERE l.item_id IS NOT NULL)::bigint AS legacy_ft_gt200
FROM knowledge_item i
LEFT JOIN ans a ON a.item_id = i.item_id
LEFT JOIN txt t ON t.item_id = i.item_id
LEFT JOIN blk b ON b.item_id = i.item_id
LEFT JOIN legacy l ON l.item_id = i.item_id
GROUP BY 1
ORDER BY 2 DESC
LIMIT %s
"""

GAP_SQL = """
SELECT
  (SELECT count(*) FROM knowledge_item_text t
   WHERE NOT EXISTS (SELECT 1 FROM knowledge_sentence s WHERE s.itext_id = t.itext_id)
  ) AS ft_no_sent,
  (SELECT count(*) FROM knowledge_sentence s
   WHERE s.itext_id IS NOT NULL
     AND NOT EXISTS (SELECT 1 FROM knowledge_sentence_embedding e WHERE e.sent_id = s.sent_id)
  ) AS sent_no_emb
"""


def _pct(n: int, d: int) -> int:
    return (100 * n // d) if d else 0


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("pct 100", _pct(141873, 141873) == 100)
    chk("pct 7 legacy-style", _pct(10652, 141873) == 7)
    chk("pct zero denom", _pct(1, 0) == 0)
    # 終態完成率不得用 answerable/(items-blocked) 抬高
    items, ans, blk = 100, 10, 80
    term = _pct(ans + blk, items)
    sneaky = _pct(ans, items - blk)
    chk("terminal_rate honest", term == 90)
    chk("forbid sneaky uplift as terminal", sneaky == 50 and sneaky != term)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def fetch_buckets(cur, limit: int = 12) -> list[dict]:
    cur.execute(BUCKET_SQL, (limit,))
    rows = []
    for domain, items, ans, blk, pend, legacy in cur.fetchall():
        rows.append({
            "domain": domain,
            "items": int(items),
            "answerable": int(ans),
            "terminal_blocked": int(blk),
            "pending": int(pend),
            "legacy_ft_gt200": int(legacy),
            "answerable_pct": _pct(int(ans), int(items)),
            "terminal_done_pct": _pct(int(ans) + int(blk), int(items)),
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--selftest", action="store_true")
    args, _ = ap.parse_known_args()
    if args.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn, db.transaction(conn) as cur:
        # 表缺席誠實降級（零 DDL）
        cur.execute("SELECT to_regclass('public.knowledge_item')")
        if not cur.fetchone()[0]:
            print("knowledge_item 未建", file=sys.stderr)
            return 1
        buckets = fetch_buckets(cur, limit=max(1, args.limit))
        gaps = {"ft_no_sent": None, "sent_no_emb": None}
        cur.execute("SELECT to_regclass('public.knowledge_sentence')")
        if cur.fetchone()[0]:
            cur.execute(GAP_SQL)
            a, b = cur.fetchone()
            gaps = {"ft_no_sent": int(a), "sent_no_emb": int(b)}
    payload = {
        "definition": {
            "answerable": "至少一句已 embed（可檢索）",
            "terminal_blocked": "有 knowledge_fulltext_status、無 item_text（skip_*／blocked 終態，非漏做）",
            "pending": "無 text、無 status（未嘗試）",
            "answerable_pct": "answerable/items",
            "terminal_done_pct": "(answerable+terminal_blocked)/items",
            "legacy_ft_gt200": "舊 gov length>200；不得當可檢索 headline",
        },
        "gaps": gaps,
        "domains": buckets,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print(__doc__.split("執行指令矩陣:")[1].strip())
    print()
    print(f"gaps: ft_no_sent={gaps['ft_no_sent']}  sent_no_emb={gaps['sent_no_emb']}")
    print(f"{'domain':40} {'items':>8} {'ans':>8} {'blocked':>8} {'pending':>8} "
          f"{'可答%':>6} {'終態%':>6} {'舊>200':>8}")
    for r in buckets:
        print(f"{(r['domain'] or '')[:40]:40} {r['items']:8,} {r['answerable']:8,} "
              f"{r['terminal_blocked']:8,} {r['pending']:8,} "
              f"{r['answerable_pct']:5}% {r['terminal_done_pct']:5}% {r['legacy_ft_gt200']:8,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
