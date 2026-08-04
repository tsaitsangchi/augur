#!/usr/bin/env python3
"""🎯 Steward 待裁積壓探針——`awaiting_hugo` 名實／懸置年齡之機械燈（M-G13）。

守原則 #15（積壓變長不得安靜變綠）· #9（數字出自真 query）· #28（零 API）· #29a/d。

起因（優化計畫書 20260803 第 23 步／r4 G9·D25）：`steward_question_ledger` 之
`awaiting_hugo` 百餘列、最舊 `asked_at` 懸置四十餘日，而 `resolved_by='hugo'` 恆 **0**
（六個值全是 rules_*）——「待裁」名實與「人可否決／可結案」可達性無燈可量。
Q22／G13 臂住 `ops/steward_opt_arms.json`（`machine-supersede-ok`）；
**本支仍唯讀、不改列**——寫入走 `resolve_questions.py --sweep-awaiting`
（須臂准；年齡門＝本探針同口徑 `>` max-age-days）。

探針門檻（master 原文）：最舊 `awaiting_hugo` 懸置 **> 30 日即紅**。
附帶量測（不改判準）：`resolved_by='hugo'` 列數——現況 0＝否決路徑無實證。

執行指令矩陣
------------
    python3 scripts/check_steward_question_backlog.py              # 無參數＝--check（唯讀）
    python3 scripts/check_steward_question_backlog.py --check      # 懸置 >30 日 → rc=1
    python3 scripts/check_steward_question_backlog.py --check --json
    python3 scripts/check_steward_question_backlog.py --check --max-age-days 45
    python3 scripts/check_steward_question_backlog.py --selftest   # 純紅綠（免 DB）
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone

import _bootstrap  # noqa: F401

DEFAULT_MAX_AGE_DAYS = 30
STATUS_AWAITING = "awaiting_hugo"


def age_days(asked_on: date, as_of: date) -> int:
    """懸置日數（日曆日；純函式）。"""
    return (as_of - asked_on).days


def backlog_rc(*, oldest_age_days, max_age_days=DEFAULT_MAX_AGE_DAYS) -> int:
    """最舊 awaiting 懸置 > max_age → 1；無 awaiting（None）→ 0。純函式。"""
    if oldest_age_days is None:
        return 0
    return 1 if oldest_age_days > max_age_days else 0


def _as_date(v) -> date | None:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    return date.fromisoformat(str(v)[:10])


def _scan(conn, *, as_of: date):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*), min(asked_at), max(asked_at) "
            "FROM steward_question_ledger WHERE status = %s",
            (STATUS_AWAITING,),
        )
        n, oldest, newest = cur.fetchone()
        cur.execute(
            "SELECT count(*) FROM steward_question_ledger WHERE resolved_by = %s",
            ("hugo",),
        )
        n_hugo = cur.fetchone()[0]
        cur.execute(
            "SELECT status, count(*) FROM steward_question_ledger GROUP BY 1 ORDER BY 2 DESC"
        )
        by_status = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute(
            "SELECT resolved_by, count(*) FROM steward_question_ledger "
            "WHERE resolved_by IS NOT NULL GROUP BY 1 ORDER BY 2 DESC"
        )
        by_resolver = {r[0]: r[1] for r in cur.fetchall()}
    oldest_d = _as_date(oldest)
    newest_d = _as_date(newest)
    oldest_age = age_days(oldest_d, as_of) if oldest_d else None
    return {
        "as_of": as_of.isoformat(),
        "awaiting_n": int(n),
        "oldest_asked_at": oldest_d.isoformat() if oldest_d else None,
        "newest_asked_at": newest_d.isoformat() if newest_d else None,
        "oldest_age_days": oldest_age,
        "resolved_by_hugo": int(n_hugo),
        "by_status": by_status,
        "by_resolver": by_resolver,
    }


def _check(*, as_json=False, max_age_days=DEFAULT_MAX_AGE_DAYS, as_of=None) -> int:
    from augur.core import db
    from _steward_opt_arms import (
        load_arms, arm_of, machine_supersede_authorized, G13_KEY,
    )

    as_of = as_of or date.today()
    with db.connect() as conn:
        snap = _scan(conn, as_of=as_of)
    rc = backlog_rc(oldest_age_days=snap["oldest_age_days"], max_age_days=max_age_days)
    arms = load_arms()
    q22 = arm_of(arms, G13_KEY)
    snap["max_age_days"] = max_age_days
    snap["g13_q22_arm"] = q22
    snap["machine_supersede_ok"] = machine_supersede_authorized(arms)
    snap["rc"] = rc
    if as_json:
        print(json.dumps(snap, ensure_ascii=False, indent=2, default=str))
        return rc

    print(f"── Steward 待裁積壓探針（M-G13；門檻 >{max_age_days} 日即紅）──")
    print(f"  G13-Q22 臂：{q22 or '（未登錄）'}"
          f"；機器 supersede={'准' if snap['machine_supersede_ok'] else '否'}"
          "（寫入＝resolve_questions --sweep-awaiting；本支唯讀）")
    print(f"  awaiting_hugo：{snap['awaiting_n']} 列"
          f"；最舊={snap['oldest_asked_at'] or '—'}（懸置 {snap['oldest_age_days']} 日）"
          f"；最新={snap['newest_asked_at'] or '—'}")
    print(f"  resolved_by='hugo'：{snap['resolved_by_hugo']} 列"
          + ("——**否決／人結案路徑無實證**" if snap["resolved_by_hugo"] == 0 else ""))
    if snap["by_resolver"]:
        top = ", ".join(f"{k}={v}" for k, v in list(snap["by_resolver"].items())[:6])
        print(f"  resolved_by 分布（前）：{top}")
    if rc:
        print(f"  → **紅** rc=1：最舊懸置 {snap['oldest_age_days']} 日 > {max_age_days}"
              "（名實積壓仍在；臂≠自動清列，本支不改列）")
    else:
        print(f"  → 綠 rc=0：無 awaiting 或最舊 ≤ {max_age_days} 日"
              "——⚠ 若 live 積壓仍在卻綠＝門檻／時區口徑可疑，先覆核")
    return rc


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    from _steward_opt_arms import (
        machine_supersede_authorized, ARM_MACHINE_SUPERSEDE_OK, G13_KEY, load_arms,
    )

    chk("age：06-22→08-03＝42", age_days(date(2026, 6, 22), date(2026, 8, 3)) == 42)
    chk("age：同日＝0", age_days(date(2026, 8, 3), date(2026, 8, 3)) == 0)
    chk("rc：42 > 30 → 紅", backlog_rc(oldest_age_days=42) == 1)
    chk("rc：30 日邊＝綠（僅 > 才紅）", backlog_rc(oldest_age_days=30) == 0)
    chk("rc：31 → 紅", backlog_rc(oldest_age_days=31) == 1)
    chk("rc：無 awaiting → 綠", backlog_rc(oldest_age_days=None) == 0)
    chk("rc：門檻參數化（45 日閾、42 日齡→綠）",
        backlog_rc(oldest_age_days=42, max_age_days=45) == 0)
    # #35：臂閘——壞臂必拒；live ops 檔若已登錄 machine-supersede-ok 則准
    chk("臂閘：keep-awaiting → 拒（先驗紅）",
        not machine_supersede_authorized({G13_KEY: {"arm": "keep-awaiting"}}))
    chk("臂閘：machine-supersede-ok → 准",
        machine_supersede_authorized({G13_KEY: {"arm": ARM_MACHINE_SUPERSEDE_OK}}))
    live = load_arms()
    if live:
        chk("live ops：G13 臂＝machine-supersede-ok",
            machine_supersede_authorized(live))
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Steward awaiting_hugo 積壓探針（M-G13）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS,
                    help=f"最舊懸置超過此日數即紅（預設 {DEFAULT_MAX_AGE_DAYS}）")
    ap.add_argument("--as-of", help="覆寫比較日 YYYY-MM-DD（預設今天；自測／複現用）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    as_of = date.fromisoformat(a.as_of) if a.as_of else None
    return _check(as_json=a.json, max_age_days=a.max_age_days, as_of=as_of)


if __name__ == "__main__":
    sys.exit(main())
