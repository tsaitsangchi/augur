#!/usr/bin/env python
"""每日自主審議 — L2 自主級上線之 cron 入口(2026-07-11 用戶核可形狀;GATE+A5 過後掛)。

🎯 這支在做什麼(白話):零 token 的每日一輪「系統自審」——讀 deliberation_daily_topic(enabled)常備題庫,
   逐題跑 panel(多視角+loop-until-dry;lens 住 DB)→ confirmed/refuted 落帳、escalated 進人裁佇列
   (resolve_escalation --list 消化)。收尾印佇列積壓+今日增量摘要。**靈魂落地:系統建議、人決策**——
   本工具永不改資料/不 commit/不觸外部 API;裁決效力止於帳本,人只看佇列。增題=INSERT 一列(#29b)。
   watchdog=daily_green delib-watch 段(殭屍 session/積壓警示,已在)。

守 #26(護欄內自主:唯讀審+落帳,零外部副作用)· #28(全本地 qwen 零 Claude)· #29a/b/d。
   cron 範例(GATE+A5 過後掛):15 6 * * * cd ~/project/augur && venv/bin/python scripts/run_daily_deliberation.py --run >> ~/delib_daily.log 2>&1

執行指令矩陣:
  python scripts/run_daily_deliberation.py                 # 無參數:印矩陣+題庫+佇列現況(唯讀)
  python scripts/run_daily_deliberation.py --run           # 跑一輪(全部 enabled 題;panel 2 輪 dry-k 1)
  python scripts/run_daily_deliberation.py --run --topic core_invariants   # 單題
  python scripts/run_daily_deliberation.py --run --model qwen3:8b          # 深檔(慢,週末批用)
"""
import argparse
import sys
import time

import _bootstrap  # noqa: F401
from augur.core import db
from augur.deliberation import engine
from augur.deliberation.lens import lens_keys


def _topics(cur, only=None):
    q = "SELECT topic_key, topic FROM deliberation_daily_topic WHERE enabled"
    if only:
        q += " AND topic_key=%s"
        cur.execute(q, (only,))
    else:
        cur.execute(q + " ORDER BY topic_key")
    return cur.fetchall()


def _queue_stats(cur):
    cur.execute("SELECT count(*) FROM deliberation_escalation WHERE NOT resolved")
    backlog = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM deliberation_escalation WHERE NOT resolved AND created_at > now() - interval '1 day'")
    return backlog, cur.fetchone()[0]


def run(only, model, timeout):
    t0 = time.time()
    with db.connect() as conn, db.transaction(conn) as cur:
        topics = _topics(cur, only)
    if not topics:
        print("✗ 無 enabled 題(deliberation_daily_topic;增題=INSERT)"); return 1
    lenses = lens_keys()
    print(f"═══ 每日自主審議({len(topics)} 題 × lens {lenses} × panel 2 輪)═══")
    total = {}
    for key, topic in topics:
        print(f"── [{key}] ──")
        r = engine.deliberate_panel(topic, "", lenses, model, 6, timeout, max_rounds=2, dry_k=1)
        for a in r["aggregate"]:
            total[a["verdict"]] = total.get(a["verdict"], 0) + 1
    with db.connect() as conn, db.transaction(conn) as cur:
        backlog, today = _queue_stats(cur)
    print(f"\n═══ 今日摘要({(time.time() - t0) / 60:.1f} 分)═══")
    print(f"  聚合裁決:{total}")
    print(f"  人裁佇列:積壓 {backlog}(今日新增 {today})→ python scripts/resolve_escalation.py --list")
    print("  (系統建議、人決策:本工具零副作用,裁決效力止於帳本)")
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--topic")
    ap.add_argument("--model", default="qwen3:4b")
    ap.add_argument("--timeout", type=float, default=600)
    args = ap.parse_args()
    if args.run:
        return run(args.topic, args.model, args.timeout)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.deliberation_daily_topic')")
        if cur.fetchone()[0]:
            for k, t in _topics(cur):
                print(f"  [{k}] {t[:70]}")
            backlog, today = _queue_stats(cur)
            print(f"佇列:積壓 {backlog}(今日 {today})")
        else:
            print("(題庫表未建:migrate_deliberation_ddl.py --run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
