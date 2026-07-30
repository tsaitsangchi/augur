#!/usr/bin/env python
"""刷 KH4 state（LSR-S23）— 對 resplit ledger 影響之 item 重算 answer_status。

🎯 這支在做什麼(白話):讀 knowledge_sentence_resplit_ledger（items 側）→
   對應 item_id → kh4.refresh_items。不改 gate 欄語意、零市場 API。
守 #15· #29a/d· FZ-keep· LSR-PLAN S3。

執行指令矩陣:
  python scripts/refresh_kh4_after_resplit.py              # 矩陣+--check
  python scripts/refresh_kh4_after_resplit.py --check      # 影響 item 數
  python scripts/refresh_kh4_after_resplit.py --apply      # 刷新 KH4
  python scripts/refresh_kh4_after_resplit.py --selftest
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("指令矩陣", "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    chk("零 FinMind", "finmind" not in (__doc__ or "").lower())
    from augur.knowledge import kh4
    chk("kh4.refresh_items 可呼叫", callable(kh4.refresh_items))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def affected_item_ids(cur, *, note_like: str | None = None):
    sql = """
      SELECT DISTINCT t.item_id
      FROM knowledge_sentence_resplit_ledger l
      JOIN knowledge_item_text t ON t.itext_id = l.parent_id
      WHERE l.side = 'items'
    """
    params: list = []
    if note_like:
        sql += " AND l.note = %s"
        params.append(note_like)
    sql += " ORDER BY 1"
    cur.execute(sql, params)
    return [r[0] for r in cur.fetchall()]


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="KH4 refresh after LSR resplit")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--note", default="LSRS-S01-20260730")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    from augur.core import db
    from augur.knowledge import kh4

    if not (args.check or args.apply):
        print(__doc__)
        args.check = True

    with db.connect() as conn, conn.cursor() as cur:
        ids = affected_item_ids(cur, note_like=args.note)
        print(f"affected_items={len(ids)} note={args.note}")
        if args.check and not args.apply:
            if ids:
                cur.execute(
                    """
                    SELECT answer_status, count(*)
                    FROM knowledge_kh4_state
                    WHERE item_id = ANY(%s)
                    GROUP BY 1 ORDER BY 2 DESC
                    """,
                    (ids,),
                )
                print("kh4_before=", cur.fetchall())
            return 0
        n = kh4.refresh_items(cur, item_ids=ids)
        conn.commit()
        print(f"refreshed={n}")
        cur.execute(
            """
            SELECT answer_status, count(*)
            FROM knowledge_kh4_state
            WHERE item_id = ANY(%s)
            GROUP BY 1 ORDER BY 2 DESC
            """,
            (ids,),
        )
        print("kh4_after=", cur.fetchall())
    return 0


if __name__ == "__main__":
    sys.exit(main())
