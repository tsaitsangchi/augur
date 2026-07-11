#!/usr/bin/env python
"""人裁佇列 CLI — deliberation_escalation 之第一個真 consumer(D5 人裁閉環;補完計畫 §4)。

🎯 這支在做什麼(白話):escalation 的 resolved/resolution/resolved_at 欄過去零程式讀者(vaporware)——
   本工具:(a) --list 讀未裁佇列;(b) --resolve 人裁落帳(outcome∈human_confirmed/human_refuted/wont_fix)。
   **機械鎖不鬆(關鍵)**:人裁只寫 escalation 三欄,**絕不**改 claim.status 為 confirmed——confirmed 唯一
   寫點仍=verify_claim;人若認定為真,正道=補可機驗 anchor 重新裁決,非人手升格(#15 多數與人意見皆不造真)。
   (c) --watch 供 daily_green:殭屍 session(heartbeat 落後>15 分)+ 人裁積壓警示(#21/#22;警示不擋)。

守 #15(人裁不造 confirmed)· #10(resolution 留痕)· #29a。

執行指令矩陣:
  python scripts/resolve_escalation.py                     # 無參數:印矩陣+佇列統計(唯讀)
  python scripts/resolve_escalation.py --list              # 未裁佇列(前 20)
  python scripts/resolve_escalation.py --resolve 12 --outcome human_refuted --resolution "錨寫錯,宣稱本身不成立"
  python scripts/resolve_escalation.py --watch             # daily_green 段:殭屍 session+積壓警示(exit 0 warn-only)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

OUTCOMES = ("human_confirmed", "human_refuted", "wont_fix")
BACKLOG_WARN = 60    # 積壓警示閾(操作值、警示不擋)


def _list(cur, limit=20):
    cur.execute("""SELECT e.escalation_id, e.reason, c.claim_text, c.assigned_verifier, c.anchor
                   FROM deliberation_escalation e JOIN deliberation_claim c USING(claim_id)
                   WHERE NOT e.resolved ORDER BY e.escalation_id LIMIT %s""", (limit,))
    rows = cur.fetchall()
    print(f"未裁佇列(前 {limit}):")
    for eid, reason, txt, ver, anc in rows:
        print(f"  #{eid} [{reason}] {txt[:60]}")
        print(f"      {ver}:{(anc or '')[:70]}")
    return len(rows)


def _resolve(cur, eid, outcome, resolution):
    if outcome not in OUTCOMES:
        sys.exit(f"✗ outcome 須 ∈ {OUTCOMES}")
    if not resolution:
        sys.exit("✗ 需 --resolution(人裁理由留痕 #10)")
    cur.execute("UPDATE deliberation_escalation SET resolved=true, resolution=%s, resolved_at=now() "
                "WHERE escalation_id=%s AND NOT resolved RETURNING claim_id",
                (f"[{outcome}] {resolution}", eid))
    row = cur.fetchone()
    if not row:
        sys.exit(f"✗ escalation {eid} 不存在或已裁")
    # 機械鎖不鬆:不改 claim.status=confirmed;human_refuted 可誠實標 refuted?——否:status 寫入權
    # 全歸 verify_claim,人裁一律只留 escalation 帳(正道=補 anchor 重裁)。
    print(f"✓ escalation {eid} 已裁 [{outcome}](claim {row[0]};claim.status 不動——正道=補可機驗 anchor 重裁)")


def _watch(cur):
    warn = 0
    cur.execute("SELECT count(*) FROM deliberation_session WHERE status='open' "
                "AND heartbeat_at IS NOT NULL AND heartbeat_at < now() - interval '15 minutes'")
    zombies = cur.fetchone()[0]
    if zombies:
        print(f"⚠ 殭屍 session:{zombies} 個 open session heartbeat 落後 >15 分(D3 watchdog)"); warn += 1
    cur.execute("SELECT count(*) FROM deliberation_escalation WHERE NOT resolved")
    backlog = cur.fetchone()[0]
    if backlog > BACKLOG_WARN:
        print(f"⚠ 人裁積壓:{backlog} > {BACKLOG_WARN}(D5;跑 --list 消化)"); warn += 1
    if not warn:
        print(f"✓ 審議 watchdog 綠(殭屍 0、積壓 {backlog} ≤ {BACKLOG_WARN})")
    return 0   # warn-only(#21 警示不擋 daily_green)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--resolve", type=int)
    ap.add_argument("--outcome")
    ap.add_argument("--resolution")
    ap.add_argument("--watch", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        if args.resolve:
            _resolve(cur, args.resolve, args.outcome, args.resolution)
            conn.commit(); return 0
        if args.list:
            _list(cur); return 0
        if args.watch:
            return _watch(cur)
        print(__doc__.split("執行指令矩陣:")[1])
        cur.execute("SELECT resolved, count(*) FROM deliberation_escalation GROUP BY 1")
        print("佇列統計:", dict(cur.fetchall()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
