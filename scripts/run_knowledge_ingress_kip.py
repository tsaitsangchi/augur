#!/usr/bin/env python
"""知識入庫強制管線(KIP) CLI — LSR-INGRESS-S1。

🎯 這支在做什麼(白話):依 job_id／source_key／item-ids 解析本批 items，
   跑 sentences→resplit→embed→qdrant(可選)→kh4→admit≤9，寫 kip_run 帳。
   三通道對稱入口；不接 FinMind／FRED；不自動 KH10。
守 #29a/d· #15· FZ-keep· LSR-INGRESS-PLAN。

執行指令矩陣:
  python scripts/run_knowledge_ingress_kip.py
  python scripts/run_knowledge_ingress_kip.py --selftest
  python scripts/run_knowledge_ingress_kip.py --channel topic_harvest --domain chemistry --needs-kip --apply --skip-qdrant
  python scripts/run_knowledge_ingress_kip.py --channel local_files --job-id 4 --apply --skip-qdrant
  python scripts/run_knowledge_ingress_kip.py --channel sftp --source-key my_sftp --limit 5 --dry-run
  python scripts/run_knowledge_ingress_kip.py --channel topic_harvest --item-ids 1,2,3 --dry-run
  python scripts/run_knowledge_ingress_kip.py --channel manual_cli --item-ids 1 --apply \\
      --qdrant-url http://127.0.0.1:6333
  python scripts/run_knowledge_ingress_kip.py --channel backfill --item-ids 1 --apply --until-stage kh4
"""
from __future__ import annotations

import json
import sys

import _bootstrap  # noqa: F401


def selftest() -> int:
    from augur.knowledge import ingress_kip as kip

    rc = kip.selftest()
    ok = rc == 0

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("指令矩陣含 --apply/--selftest", "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    chk("FZ-keep", "FZ-keep" in (__doc__ or ""))
    chk("零 FinMind 標頭", "FinMind" in (__doc__ or "") and "不接" in (__doc__ or ""))
    print("CLI 自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import argparse

    from augur.knowledge import ingress_kip as kip

    ap = argparse.ArgumentParser(description="LSR-INGRESS KIP runner")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true", help="唯讀:解析 item 數＋最近 kip_run")
    ap.add_argument("--dry-run", action="store_true", help="規劃段序＋開帳 dry（不切句／不嵌）")
    ap.add_argument("--apply", action="store_true", help="實跑 KIP 各段")
    ap.add_argument(
        "--channel",
        choices=list(kip.CHANNELS),
        default=None,
    )
    ap.add_argument("--job-id", type=int, default=None)
    ap.add_argument("--source-key", default=None)
    ap.add_argument("--domain", default=None, help="依 domain 解析 items（可配 --needs-kip）")
    ap.add_argument(
        "--needs-kip",
        action="store_true",
        help="只取缺句／缺嵌／非 eligible／admit<9 之 item",
    )
    ap.add_argument("--item-ids", default=None, help="逗號分隔 item_id")
    ap.add_argument("--trigger-ref", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-chars", type=int, default=kip.DEFAULT_MAX_CHARS)
    ap.add_argument("--admit-up-to", type=int, default=kip.DEFAULT_ADMIT_UP_TO)
    ap.add_argument("--qdrant-url", default=None)
    ap.add_argument("--skip-qdrant", action="store_true")
    ap.add_argument(
        "--skip-stage",
        action="append",
        default=[],
        choices=list(kip.STAGE_ORDER),
        help="可重覆；明示跳過某段",
    )
    ap.add_argument(
        "--until-stage",
        choices=list(kip.STAGE_ORDER),
        default=None,
    )
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not (args.check or args.dry_run or args.apply):
        print(__doc__)
        print("(唯讀；加 --check／--dry-run／--apply)")
        args.check = True

    from augur.core import db

    item_ids = None
    if args.item_ids:
        item_ids = [int(x.strip()) for x in args.item_ids.split(",") if x.strip()]

    with db.connect() as conn, conn.cursor() as cur:
        if args.check and not (args.dry_run or args.apply):
            cur.execute("SELECT to_regclass('public.knowledge_ingress_kip_run')")
            print(f"kip_run_table={'已在' if cur.fetchone()[0] else '缺'}")
            ids = kip.resolve_item_ids(
                cur,
                item_ids=item_ids,
                job_id=args.job_id,
                source_key=args.source_key,
                domain=args.domain,
                needs_kip=bool(args.needs_kip),
                limit=args.limit,
            )
            print(
                f"resolved_items={len(ids)} "
                f"channel={args.channel} job_id={args.job_id} "
                f"source_key={args.source_key} domain={args.domain} "
                f"needs_kip={args.needs_kip}"
            )
            if ids:
                print(f"sample={ids[:10]}")
            cur.execute(
                """
                SELECT kip_run_id, channel, status, cardinality(item_ids), created_at
                FROM knowledge_ingress_kip_run
                ORDER BY kip_run_id DESC LIMIT 5
                """
            )
            rows = cur.fetchall()
            print("recent_kip_runs=", rows)
            return 0

        ids = kip.resolve_item_ids(
            cur,
            item_ids=item_ids,
            job_id=args.job_id,
            source_key=args.source_key,
            domain=args.domain,
            needs_kip=bool(args.needs_kip),
            limit=args.limit,
        )

    if not args.channel:
        print("須 --channel", file=sys.stderr)
        return 2
    if not ids:
        msg = "無 item_ids 可跑（檢查 --job-id／--source-key／--domain／--item-ids）"
        if args.needs_kip:
            print(f"{msg}；needs-kip 空＝本批已收束", flush=True)
            return 0
        print(msg, file=sys.stderr)
        return 1

    trigger = args.trigger_ref
    if trigger is None:
        if args.job_id is not None:
            trigger = f"job:{args.job_id}"
        elif args.source_key:
            trigger = f"source:{args.source_key}"
        elif args.domain:
            trigger = f"domain:{args.domain}"
        else:
            trigger = f"items:{len(ids)}"

    result = kip.run_kip_for_items(
        ids,
        channel=args.channel,
        trigger_ref=trigger,
        apply=bool(args.apply),
        dry_run=bool(args.dry_run) and not args.apply,
        max_chars=args.max_chars,
        admit_up_to=args.admit_up_to,
        qdrant_url=args.qdrant_url,
        skip_qdrant=bool(args.skip_qdrant),
        skip_stages=set(args.skip_stage or []),
        until_stage=args.until_stage,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
