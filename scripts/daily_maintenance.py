#!/usr/bin/env python
"""augur 每日維護入口 — 全市場 by-date 增量 + 可選 #7 對帳。

這支在做什麼（白話）：每天跑一次，把全市場日頻資料補到最新（by-date：不帶 data_id 逐交易日抓整個
市場，每 dataset 只用「範圍內交易日數」筆請求、非逐股 3100 筆），再（可選）對帳近期日確認 DB 與
API byte 相等。薄 CLI——邏輯都在 src（`ingestion.sync` + `audit.reconcile`），本檔只解析參數 + 串接 + 印。

執行指令矩陣:
  python scripts/daily_maintenance.py                          # 全日頻 dataset by-date 增量到今天
  python scripts/daily_maintenance.py --datasets TaiwanStockPrice TaiwanStockMarginPurchaseShortSale
  python scripts/daily_maintenance.py --end 2026-06-09         # 增量到指定日
  python scripts/daily_maintenance.py --audit-since 2026-06-01 # 增量後對帳 2026-06-01 起（#7 attestation）

守 #6（resume 增量）· #3/#4（動態列舉去 intraday）· #17（by-date 省 request）· #7（對帳）· #15（數字皆實跑）。
"""
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db, schema
from augur.audit import reconcile
from augur.ingestion import sync


def main():
    ap = argparse.ArgumentParser(description="augur 每日維護：by-date 全市場增量 + 可選對帳")
    ap.add_argument("--datasets", nargs="*", help="指定 dataset（預設全部日頻）")
    ap.add_argument("--end", help="增量截止日 YYYY-MM-DD（預設今日）")
    ap.add_argument("--audit-since", help="對帳起始日 YYYY-MM-DD（給了才對帳本次更新之 by-date 表）")
    args = ap.parse_args()

    with db.connect() as conn:
        with db.transaction(conn) as cur:           # PHASE 1：確保 infra log 表存在（冪等）
            schema.bootstrap_infra(cur)

        results = sync.sync_all_by_date(conn, datasets=args.datasets, end=args.end)
        synced = [r for r in results if r["mode"] == "by-date" and r["rows"]]
        skipped = [r for r in results if r["mode"] != "by-date"]
        print(f"\n增量完成：{len(synced)} dataset 有更新、共 {sum(r['rows'] for r in synced):,} 列；"
              f"{len(skipped)} dataset 略過（no-baseline / not-by-date-capable / intraday）")
        failed = [(r["dataset"], r["failed_days"]) for r in results if r.get("failed_days")]
        if failed:   # 漏抓日（單日錯被跳過;resume 只看 max(date) 不會自補）→ 印出供 scoped 重跑（#6 不掉資料）
            print(f"⚠ {len(failed)} dataset 有失敗日（漏抓;resume 不自補,須 sync_by_date 明確 start=該日重跑補洞）：")
            for ds, days in failed:
                print(f"  {ds}: {len(days)} 日 {days[:10]}{'…' if len(days) > 10 else ''}")

        if args.audit_since and synced:
            print(f"\n對帳（#7，since={args.audit_since}）…")
            recs = [reconcile.reconcile_by_date(conn, r["dataset"], since=args.audit_since) for r in synced]
            v = reconcile.verdict(*recs)
            tag = "✅ PASS（DB byte-equal API，無幻像）" if v["passed"] else "❌ FAIL（須查根因）"
            print(f"attestation：{tag} | matched={v['matched']:,} "
                  f"value_mismatch={v['value_mismatch']} extra_in_db={v['extra_in_db']} "
                  f"missing_in_db={v['missing_in_db']:,}")


if __name__ == "__main__":
    main()
