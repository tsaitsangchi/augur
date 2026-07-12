#!/usr/bin/env python
"""知識覆蓋率報告+輪末快照(深抓計畫 S4;K 計畫 K3)。

🎯 這支在做什麼(白話):讀三個 coverage 視圖印覆蓋率(域×items×全文×open 段),--snapshot 把
   per-source staged/promoted/rejected/pending 落 knowledge_coverage_snapshot(輪末留痕,趨勢可比)。

守 #9(數字全出自 DB)· #6(snapshot 冪等追加)· #28(本地零 usage)。

執行指令矩陣:
  python scripts/report_knowledge_coverage.py             # 覆蓋率報告(唯讀)
  python scripts/report_knowledge_coverage.py --snapshot  # 報告+落輪末快照
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--snapshot", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        print("== 域覆蓋(v_knowledge_coverage_domain)==")
        cur.execute("SELECT domain, items, items_with_text, items_open_fulltext, items_owned_local "
                    "FROM v_knowledge_coverage_domain ORDER BY items DESC LIMIT 15")
        for d, n, wt, of, ol in cur.fetchall():
            print(f"  {d[:36]:38} items={n:>7,} 全文={wt or 0:>7,} open={of or 0:>6,} owned={ol or 0:>7,}")
        print("== harvest 進度(v_knowledge_harvest_progress)==")
        cur.execute("SELECT * FROM v_knowledge_harvest_progress LIMIT 8")
        for r in cur.fetchall():
            print("  " + " | ".join(str(x) for x in r))
        if args.snapshot:
            cur.execute("""INSERT INTO knowledge_coverage_snapshot
                  (snapped_at, source_key, staged_total, promoted, rejected, pending)
                SELECT now(), source_key,
                       count(*), count(*) FILTER (WHERE status='promoted'),
                       count(*) FILTER (WHERE status='rejected'), count(*) FILTER (WHERE status='pending')
                FROM knowledge_staging GROUP BY source_key""")
            print(f"✓ snapshot 落 {cur.rowcount} 列(per-source)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
