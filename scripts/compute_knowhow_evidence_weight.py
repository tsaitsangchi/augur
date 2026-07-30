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
  python scripts/compute_knowhow_evidence_weight.py --widen --limit 600 --apply   # 擴大母體(使鑑別力閘自解)
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
    ap.add_argument("--widen", action="store_true",

                    help="擴大加權母體:取 depth<7 有原文者(使三分量出現變異、鑑別力閘自解)")
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
            if args.widen:
                # ── 母體擴大（hugo 拍板 2026-07-30「把 KH8 母體擴大」）
                # 病灶：原僅對 min_depth=7 之 item 加權 ⇒ terminal／embed／kh4_ok 對全母體恆 1.0
                #（母體選擇效應）⇒ score 底線恆 0.72、必落 high ⇒ 指標**結構上不可能鑑別**。
                # 治本＝把「未終態／未嵌入／非 eligible」者一併納入加權母體，使三分量出現變異；
                # 鑑別力閘（evidence.population_discriminates）隨之自動解除——非放寬判準，
                # 而是讓判準所需之變異真實存在。
                ids = aa.list_candidate_item_ids(cur, limit=args.limit, max_depth_lt=7)
                print(f"[--widen] 取 depth<7 有原文者 {len(ids)} 顆（擴大加權母體）")
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
