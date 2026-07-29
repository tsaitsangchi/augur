#!/usr/bin/env python
"""回放／合成 CLI — KH9 min-LAND。

🎯 這支在做什麼(白話):對指定 item 讀最新 KH8 權重，寫／預覽 synthesis replay。
   預設 dry-run。零市場 API；合成≠approve≠PME APPLY。
守 #29a/d· #15· FZ-keep· HUMAN-APPROVE-keep· PME-GATE-keep。

執行指令矩陣:
  python scripts/replay_knowhow_run.py                    # 印矩陣
  python scripts/replay_knowhow_run.py --item-id 1        # dry
  python scripts/replay_knowhow_run.py --item-id 1 --apply
  python scripts/replay_knowhow_run.py --limit 3 --apply
  python scripts/replay_knowhow_run.py --selftest
"""
from __future__ import annotations

import json
import sys

import _bootstrap  # noqa: F401


def selftest() -> int:
    from augur.knowledge import synthesis as syn

    return syn._selftest()


def main(argv=None) -> int:
    import argparse

    from augur.core import db
    from augur.knowledge import auto_admit as aa
    from augur.knowledge import evidence as ev
    from augur.knowledge import synthesis as syn

    ap = argparse.ArgumentParser(description="KH9 synthesis / replay")
    ap.add_argument("--item-id", type=int, default=None)
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.item_id is None and not args.apply and len(sys.argv) <= 1:
        print(__doc__)
        print("(例: --item-id N [--apply])")
        return 0

    with db.connect() as conn, conn.cursor() as cur:
        if args.item_id is not None:
            ids = [args.item_id]
        else:
            ids = aa.list_candidate_item_ids(cur, limit=args.limit, min_depth=8)
            if not ids:
                ids = aa.list_candidate_item_ids(cur, limit=args.limit, min_depth=7)
        print(f"n={len(ids)} apply={args.apply}")
        for iid in ids:
            snap = aa._item_snapshot(cur, iid)
            if not snap:
                print(f"  item={iid} missing")
                continue
            if args.apply:
                r = syn.evaluate_item_synthesis(cur, snap)
                print(f"  item={iid} {r['verdict']} {r.get('note')}")
            else:
                w = ev.latest_weight_for_item(cur, iid)
                if not w:
                    print(f"  item={iid} dry no KH8 weight")
                    continue
                s = syn.build_synthesis(item_id=iid, weight=w, snap=snap)
                print(
                    f"  item={iid} dry state={s['answer_state']} "
                    f"score={s['evidence_score']} run_id={s['run_id']}"
                )
                print(f"    replay={json.dumps(s['replay_json'], ensure_ascii=False)[:200]}…")
        if args.apply:
            conn.commit()
        else:
            conn.rollback()
    return 0


if __name__ == "__main__":
    sys.exit(main())
