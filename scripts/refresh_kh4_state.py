#!/usr/bin/env python
"""KH4 狀態刷新器 — 依 item/source/domain 回填最小 answer gate 狀態。

🎯 這支在做什麼(白話):讀現有 knowledge item / text / sentence / embed / import qualification /
   fulltext blocked 等帳本，回填 `knowledge_kh4_state`。供 local/topic/SFTP 入口與 pipeline/ATA
   在各階段刷新共同狀態；answer gate 讀此表，而不是各自重算。
守 #12(單一刷新入口)· #15(不讓 provisional 直接進一般回答空間)· #29。

執行指令矩陣:
  python scripts/refresh_kh4_state.py
  python scripts/refresh_kh4_state.py --dry-run
  python scripts/refresh_kh4_state.py --item-id 123
  python scripts/refresh_kh4_state.py --source-key local_files_local
  python scripts/refresh_kh4_state.py --domain finance --limit 200
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import kh4


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="刷新 knowledge_kh4_state")
    ap.add_argument("--item-id", type=int, action="append")
    ap.add_argument("--source-key")
    ap.add_argument("--domain")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if args.dry_run:
        print("dry-run:將刷新 KH4 狀態"
              f" item_ids={args.item_id or '-'} source_key={args.source_key or '-'}"
              f" domain={args.domain or '-'} limit={args.limit or '-'}")
        return 0

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT to_regclass('knowledge_kh4_state')")
            if not cur.fetchone()[0]:
                sys.exit("knowledge_kh4_state 未建——先跑 scripts/migrate_kh4_state_ddl.py --apply")
            n = kh4.refresh_items(
                cur,
                item_ids=args.item_id,
                source_key=args.source_key,
                domain=args.domain,
                limit=args.limit,
            )
        print(f"KH4 refreshed: {n} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
