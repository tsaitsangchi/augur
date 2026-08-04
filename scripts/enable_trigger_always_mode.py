#!/usr/bin/env python3
"""🎯 非內部 trigger 改 ENABLE ALWAYS——M-G16 臂 `enable-always-go` 之寫入路徑。

守原則 #15（無臂不得 DDL）· #9 · #28 · #29a/d · #35。

探針 `check_trigger_always_mode.py` **永不 DDL**；本支才寫。
Steward 臂＝`ops/steward_opt_arms.json` G16-ALWAYS＝`enable-always-go` 才准 `--apply`；
dry-run 永遠可預覽候選。不動 M-G15／不改判準文字（[I] 執行層硬化）。

執行指令矩陣
------------
    python3 scripts/enable_trigger_always_mode.py                 # 無參數＝dry-run
    python3 scripts/enable_trigger_always_mode.py --dry-run       # 列出 origin→ALWAYS 候選
    python3 scripts/enable_trigger_always_mode.py --apply         # 須臂准；ALTER TABLE … ENABLE ALWAYS TRIGGER
    python3 scripts/enable_trigger_always_mode.py --selftest
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401
from psycopg2 import sql


def apply_authorized(arms: dict) -> bool:
    """G16＝enable-always-go 才准寫入。純函式（轉呼叫臂模組）。"""
    from _steward_opt_arms import always_enable_authorized
    return always_enable_authorized(arms)


def _list_origin(conn) -> list[tuple[str, str]]:
    """非內部且 tgenabled='O' 之 (relname, tgname)。"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT c.relname, t.tgname FROM pg_trigger t "
            "JOIN pg_class c ON c.oid = t.tgrelid "
            "JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE NOT t.tgisinternal AND t.tgenabled = 'O' "
            "AND n.nspname = 'public' "
            "ORDER BY c.relname, t.tgname"
        )
        return [(r[0], r[1]) for r in cur.fetchall()]


def _count_always(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*)::int FROM pg_trigger "
            "WHERE NOT tgisinternal AND tgenabled = 'A'"
        )
        return int(cur.fetchone()[0])


def run(*, apply: bool) -> int:
    from augur.core import db
    from _steward_opt_arms import load_arms, arm_of, G16_KEY

    arms = load_arms()
    g16 = arm_of(arms, G16_KEY)
    auth = apply_authorized(arms)
    print(f"  G16-ALWAYS 臂={g16 or '（未登錄）'}；ENABLE ALWAYS 寫入="
          f"{'准' if auth else '否（fail-closed）'}")
    if apply and not auth:
        print("  → 拒寫：需 Steward `G16-ALWAYS: enable-always-go` 登錄"
              " ops/steward_opt_arms.json（dry-run 可預覽）")
        return 2

    with db.connect() as conn:
        before = _count_always(conn)
        rows = _list_origin(conn)
        print(f"  現況 ALWAYS={before}；origin 候選={len(rows)}")
        for rel, tg in rows[:8]:
            print(f"    · {rel}.{tg}")
        if len(rows) > 8:
            print(f"    …另 {len(rows) - 8} 支")
        if not apply:
            print(f"  [dry-run] 將 ENABLE ALWAYS {len(rows)} 支（未寫庫）")
            return 0
        with conn.cursor() as cur:
            for rel, tg in rows:
                cur.execute(
                    sql.SQL("ALTER TABLE {} ENABLE ALWAYS TRIGGER {}").format(
                        sql.Identifier(rel), sql.Identifier(tg)
                    )
                )
            conn.commit()
        after = _count_always(conn)
    print(f"  已 APPLY：ALWAYS {before} → {after}（本批 origin→ALWAYS {len(rows)}）")
    return 0 if after >= 1 else 1


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    from _steward_opt_arms import (
        ARM_ENABLE_ALWAYS_GO, ARM_ENABLE_PROBE_ONLY, G16_KEY, load_arms,
    )

    chk("臂：enable-probe-only → 拒寫（先驗紅）",
        not apply_authorized({G16_KEY: {"arm": ARM_ENABLE_PROBE_ONLY}}))
    chk("臂：enable-always-go → 准",
        apply_authorized({G16_KEY: {"arm": ARM_ENABLE_ALWAYS_GO}}))
    chk("臂：缺 → 拒", not apply_authorized({}))
    chk("臂：defer → 拒", not apply_authorized({G16_KEY: {"arm": "defer"}}))
    live = load_arms()
    if live:
        chk("live ops：G16＝enable-always-go 且准寫",
            apply_authorized(live))
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="M-G16 ENABLE ALWAYS 寫入（須臂）")
    ap.add_argument("--dry-run", action="store_true",
                    help="預覽候選（預設；與無參數同）")
    ap.add_argument("--apply", action="store_true",
                    help="真寫 ALTER TABLE … ENABLE ALWAYS TRIGGER（須臂准）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.apply and a.dry_run:
        print("拒：--apply 與 --dry-run 互斥", file=sys.stderr)
        return 2
    return run(apply=bool(a.apply))


if __name__ == "__main__":
    sys.exit(main())
