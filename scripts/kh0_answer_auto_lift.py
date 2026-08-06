#!/usr/bin/env python
"""KH0-ANSWER-AUTO-LIFT CLI — R-hybrid 核可＋抬層（T2 預設機械 activate）。

🎯 這支在做什麼(白話):對給定答／引文跑 R-cite（或 --human-pass），通過則抬
   item admit 至最多 KH2；寫 lift_log。T2：可機械 approve／activate 來源
  （每批 ≤1 source；需 has_text）。``--no-activate-source`` 關。不掛 advise。
守 AUTO-LIFT go· v1.48·T2-go· FZ-keep· no-web/dialog-approve。

執行指令矩陣:
  python scripts/kh0_answer_auto_lift.py --selftest
  python scripts/kh0_answer_auto_lift.py --dry-run --query Q --answer A --item-id 1 --cite-text T
  python scripts/kh0_answer_auto_lift.py --apply --query Q --answer A --item-id 1 --cite-text T
  python scripts/kh0_answer_auto_lift.py --apply --no-activate-source ...
  python scripts/kh0_answer_auto_lift.py --apply --human-pass --query Q --answer A --item-id 1 --cite-text T
"""
from __future__ import annotations

import sys
from types import SimpleNamespace as S

import _bootstrap  # noqa: F401


def selftest() -> int:
    from augur.knowledge import answer_auto_lift as m

    return m._selftest()


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--human-pass", action="store_true", help="R-human 旁路（R-hybrid 邊界）")
    ap.add_argument(
        "--no-activate-source",
        action="store_true",
        help="關閉 T2 機械 activate（預設開啟）",
    )
    ap.add_argument("--query", default="")
    ap.add_argument("--answer", default="")
    ap.add_argument("--item-id", type=int, action="append", default=[])
    ap.add_argument("--cite-text", action="append", default=[], help="與 --item-id 對齊或共用")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not args.apply and not args.dry_run:
        print(__doc__)
        return 0

    apply = bool(args.apply) and not args.dry_run
    texts = args.cite_text or [""]
    cites = []
    for i, iid in enumerate(args.item_id):
        t = texts[i] if i < len(texts) else texts[-1]
        cites.append(S(item_id=iid, text=t, item_title=""))

    from augur.core import db
    from augur.knowledge import answer_auto_lift as m

    with db.connect() as conn, conn.cursor() as cur:
        if apply:
            cur.execute("SELECT to_regclass('public.knowhow_answer_lift_log')")
            if not cur.fetchone()[0]:
                print("✗ lift_log 表未建：先跑 scripts/migrate_kh0_answer_lift_log_ddl.py --apply")
                return 2
        out = m.maybe_auto_lift_after_answer(
            cur,
            query=args.query,
            answer=args.answer,
            citations=cites,
            apply=apply,
            human_pass=args.human_pass,
            activate_source=not args.no_activate_source,
        )
        if apply:
            conn.commit()
        else:
            conn.rollback()
    print(
        f"lifted={out['lifted']} cite_pass={out['cite']['pass']} "
        f"human={out['human_pass']} activate={out.get('activate_source')} "
        f"items={out['item_ids']} lift_id={out.get('lift_id')} apply={apply}"
    )
    for r in out.get("results") or []:
        print(
            f"  item={r['item_id']} depth {r['before']}→{r['after']} ok={r['ok']} "
            f"act={r.get('activate_attempted')} src={r.get('source_key')} "
            f"src_actions={r.get('source_actions')}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
