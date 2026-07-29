#!/usr/bin/env python
"""統一 evidence weighting CLI — KH8 min-LAND。

🎯 這支在做什麼(白話):對指定 item（或候選清單）算 KH8 權重並可寫帳本。
   預設 dry-run。零 FinMind／FRED；權重≠approve≠tradable。
守 #29a/d· #15· FZ-keep· PME-GATE-keep。

執行指令矩陣:
  python scripts/compute_knowhow_evidence_weight.py                 # 印矩陣
  python scripts/compute_knowhow_evidence_weight.py --item-id 1     # dry
  python scripts/compute_knowhow_evidence_weight.py --item-id 1 --apply
  python scripts/compute_knowhow_evidence_weight.py --limit 3 --apply
  python scripts/compute_knowhow_evidence_weight.py --selftest
"""
from __future__ import annotations

import json
import sys

import _bootstrap  # noqa: F401


def selftest() -> int:
    from augur.knowledge import evidence as ev

    return ev._selftest()


def main(argv=None) -> int:
    import argparse

    from augur.core import db
    from augur.knowledge import auto_admit as aa
    from augur.knowledge import evidence as ev

    ap = argparse.ArgumentParser(description="KH8 evidence weighting")
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
            ids = aa.list_candidate_item_ids(cur, limit=args.limit, min_depth=7)
            if not ids:
                ids = aa.list_candidate_item_ids(cur, limit=args.limit)
        print(f"n={len(ids)} apply={args.apply}")
        for iid in ids:
            snap = aa._item_snapshot(cur, iid)
            if not snap:
                print(f"  item={iid} missing")
                continue
            if args.apply:
                r = ev.evaluate_item_evidence(cur, snap)
                print(f"  item={iid} {r['verdict']} {r.get('note')}")
            else:
                inputs = ev.gather_item_inputs(cur, iid, snap)
                w = ev.compute_evidence_weight(**inputs)
                print(f"  item={iid} dry band={w['confidence_band']} score={w['evidence_score']}")
        if args.apply:
            conn.commit()
        else:
            conn.rollback()
    return 0


if __name__ == "__main__":
    sys.exit(main())
