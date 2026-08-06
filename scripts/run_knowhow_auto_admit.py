#!/usr/bin/env python
"""KH10 漸進自動入庫 CLI — 對庫內 item 跑 admit_depth update（S1）。

🎯 這支在做什麼(白話):庫內資料已准入；本 CLI 逐層 KH update 抬高精準水印。
   --apply-raw＝只確保 depth0；--apply-up-to N＝推進至 N（受 max_auto_depth）；
   --min-depth M＝只掃已達 M 的候選（專抬 4→6，不被 depth0 海量占滿）。
   預設 dry-run。可機械 activate 來源（v1.48.0）。零 FinMind／FRED。
守 憲章 v1.48.0· #29a/d· FZ-keep· PME-GATE-keep· NHC-keep。

執行指令矩陣:
  python scripts/run_knowhow_auto_admit.py                     # 印矩陣+--check
  python scripts/run_knowhow_auto_admit.py --check             # gate／state 摘要
  python scripts/run_knowhow_auto_admit.py --dry-run --limit 5
  python scripts/run_knowhow_auto_admit.py --apply-raw --limit 20
  python scripts/run_knowhow_auto_admit.py --apply-up-to 4 --limit 10
  python scripts/run_knowhow_auto_admit.py --apply-up-to 6 --min-depth 4 --limit 500
  python scripts/run_knowhow_auto_admit.py --until-empty --apply-up-to 6 --limit 5000
  python scripts/run_knowhow_auto_admit.py --apply-up-to 4 --item-id 277861
  python scripts/run_knowhow_auto_admit.py --selftest

誠實天花板（2026-07-29 KH8-KH9-min-LAND）: gate.max_auto_depth=9；
KH8/9 可評估（權重／合成帳；≠approve≠tradable）；KH10 仍屬治理列帳。
--apply-up-to 10 受 gate.max_auto_depth 夾（現 9）。
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

import _bootstrap  # noqa: F401


def count_repromote_held(results: list[dict]) -> int:
    """D4 clamp 之 held 計數——§4 證偽條件度量載體（週 >10 件應議白名單）。純函式可自測。"""
    return sum(
        1 for r in results
        if r.get("ok") and any(
            a.get("action") == "held_at_floor" for a in (r.get("actions") or []))
    )


def selftest() -> int:
    from augur.knowledge import auto_admit as aa

    rc = aa._selftest()
    fixture = [
        {"ok": True, "actions": [{"layer": "repromote", "action": "held_at_floor"}]},
        {"ok": False, "actions": [{"action": "held_at_floor"}]},   # 失敗列不計
        {"ok": True, "actions": [{"layer": 4, "action": "kh4_refresh"}]},
        {"ok": True},                                              # 無 actions
    ]
    ok_held = count_repromote_held(fixture) == 1
    print(f"  {'✓' if ok_held else '✗FAIL'} D4 repromote_held 計數（fixture 恰 1/4）")
    return 0 if (rc == 0 and ok_held) else 1


def check() -> int:
    from augur.core import db
    from augur.knowledge import auto_admit as aa

    with db.connect() as conn, conn.cursor() as cur:
        g = aa.load_gate(cur)
        print("gate=", json.dumps(g, ensure_ascii=False))
        if aa._table_exists(cur, "knowhow_auto_admit_state"):
            cur.execute(
                "SELECT admit_depth, count(*) FROM knowhow_auto_admit_state "
                "GROUP BY 1 ORDER BY 1"
            )
            rows = cur.fetchall()
            print("state buckets=", dict(rows) if rows else {})
        else:
            print("state 表未建——先 migrate --apply")
            return 1
        # count(DISTINCT)：`knowledge_item_text` 以 (item_id, seq) 一 item 多列存原文
        # （158,064 列／146,348 distinct item）。用 count(*) 會印原文列數而非 item 數，
        # 使本支與同鏈之 run_kh_chain.py --check 印出兩個互相矛盾的數字。
        cur.execute(
            "SELECT count(DISTINCT i.item_id) FROM knowledge_item i "
            "JOIN knowledge_item_text x ON x.item_id=i.item_id"
        )
        print(f"items_with_text={cur.fetchone()[0]}")
        print(
            "ceiling_note=實務最高 depth 9（KH8/9 min-LAND；≠approve≠tradable；"
            f"max_auto_depth={g['max_auto_depth']}）"
        )
    return 0


def run_batch(*, up_to: int, limit: int, apply: bool, item_id: int | None,
              activate_source: bool, min_depth: int | None,
              quiet: bool = False) -> dict:
    from augur.core import db
    from augur.knowledge import auto_admit as aa

    with db.connect() as conn, conn.cursor() as cur:
        if item_id is not None:
            ids = [item_id]
        else:
            # depth < up_to：排除已達標（否則 min-depth 4 會先掃到一堆 6→6）
            ids = aa.list_candidate_item_ids(
                cur,
                limit=limit,
                max_depth_lt=up_to,
                min_depth=min_depth,
            )
        print(
            f"candidates={len(ids)} up_to={up_to} min_depth={min_depth} apply={apply}"
        )
        results = []
        for iid in ids:
            r = aa.progressive_item(
                cur, iid, up_to=up_to, apply=apply, activate_source=activate_source,
            )
            results.append(r)
            if quiet:
                continue
            if r.get("ok"):
                print(
                    f"  item={iid} depth {r['admit_depth_before']}→{r['admit_depth_after']} "
                    f"run_id={r.get('run_id')}"
                )
            else:
                print(f"  item={iid} ERR {r.get('error')}")
        if apply:
            conn.commit()
        else:
            conn.rollback()
        advanced = sum(
            1 for r in results
            if r.get("ok") and r["admit_depth_after"] > r["admit_depth_before"]
        )
        stuck = sum(
            1 for r in results
            if r.get("ok") and r["admit_depth_after"] == r["admit_depth_before"]
            and not r.get("seeded")
        )
        seeded = sum(1 for r in results if r.get("ok") and r.get("seeded"))
        ok_n = sum(1 for r in results if r.get("ok"))
        held = count_repromote_held(results)
        print(
            f"done ok={ok_n} advanced={advanced} seeded={seeded} "
            f"unchanged={stuck} repromote_held={held}"
        )
        return {
            "n": len(ids),
            "ok": ok_n,
            "advanced": advanced,
            "seeded": seeded,
            "unchanged": stuck,
            "held": held,
        }


def run_until_empty(*, up_to: int, limit: int, activate_source: bool,
                    min_depth: int | None, max_rounds: int) -> int:
    """連續批次直到候選耗盡或本輪 advanced=0。"""
    # 實務 cap：gate 再夾；KH8/9 min-LAND → 最高 9（≠tradable／≠PME）
    effective = min(up_to, 9) if up_to >= 9 else up_to
    if up_to > 9:
        print(
            f"note: 請求 up_to={up_to}，drain 用 effective={effective} "
            f"（gate／KH10 治理列另議）；≠approve≠tradable"
        )
    total_adv = 0
    total_seed = 0
    for rnd in range(1, max_rounds + 1):
        ts = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        print(f"=== round {rnd}/{max_rounds} {ts} ===")
        stats = run_batch(
            up_to=effective,
            limit=limit,
            apply=True,
            item_id=None,
            activate_source=activate_source,
            min_depth=min_depth,
            quiet=True,
        )
        total_adv += stats["advanced"]
        total_seed += stats.get("seeded", 0)
        if stats["n"] == 0:
            print(
                f"queue empty after {rnd} rounds; total_advanced={total_adv} "
                f"total_seeded={total_seed}"
            )
            break
        if stats["advanced"] == 0 and stats.get("seeded", 0) == 0:
            print(
                f"no advance (stuck queue) after round {rnd}; "
                f"total_advanced={total_adv} total_seeded={total_seed}"
            )
            break
    else:
        print(
            f"hit max_rounds={max_rounds}; total_advanced={total_adv} "
            f"total_seeded={total_seed}"
        )
    return check()


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="KH10-AUTO-ADMIT progressive S1")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="評估不寫庫（可配 --apply-up-to）")
    ap.add_argument("--apply-raw", action="store_true", help="寫庫 up_to=0")
    ap.add_argument("--apply-up-to", type=int, metavar="N", help="寫庫推進至 depth N")
    ap.add_argument(
        "--until-empty",
        action="store_true",
        help="連續批次直到候選耗盡（配 --apply-up-to；實務最高 6）",
    )
    ap.add_argument(
        "--max-rounds",
        type=int,
        default=200,
        help="--until-empty 最大輪數（預設 200×limit）",
    )
    ap.add_argument(
        "--min-depth",
        type=int,
        default=None,
        metavar="M",
        help="只掃 admit_depth≥M（例: --min-depth 4 --apply-up-to 6）",
    )
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--item-id", type=int, default=None)
    ap.add_argument("--no-activate-source", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    want_run = (
        args.dry_run or args.apply_raw or args.apply_up_to is not None
        or args.until_empty
    )
    if args.check or not want_run:
        rc = check()
        if not want_run:
            if not args.check:
                print(__doc__)
                print("例: --until-empty --apply-up-to 6 --limit 5000")
            return rc

    if args.apply_raw:
        up_to = 0
    elif args.apply_up_to is not None:
        up_to = args.apply_up_to
    else:
        up_to = 6

    if args.until_empty:
        if args.dry_run:
            print("--until-empty 不支援 --dry-run")
            return 2
        return run_until_empty(
            up_to=up_to,
            limit=args.limit,
            activate_source=not args.no_activate_source,
            min_depth=args.min_depth,
            max_rounds=args.max_rounds,
        )

    apply = (args.apply_raw or args.apply_up_to is not None) and not args.dry_run
    if args.dry_run:
        apply = False

    run_batch(
        up_to=up_to,
        limit=args.limit,
        apply=apply,
        item_id=args.item_id,
        activate_source=not args.no_activate_source,
        min_depth=args.min_depth,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
