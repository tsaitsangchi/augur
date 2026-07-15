#!/usr/bin/env python
"""augur 每日維護入口 — 全市場 by-date 增量 + 可選 #7 對帳。

這支在做什麼（白話）：每天跑一次，把全市場日頻資料補到最新（by-date：不帶 data_id 逐交易日抓整個
市場，每 dataset 只用「範圍內交易日數」筆請求、非逐股 3100 筆），再（可選）對帳近期日確認 DB 與
API byte 相等。薄 CLI——邏輯都在 src（`ingestion.sync` + `audit.reconcile`），本檔只解析參數 + 串接 + 印。

對帳（#7,hugo 2026-07-14 拍板 (a)+(b)）:
  (a) 滾動安全邊緣——各 dataset 對帳窗上限=today−finalize_lag_days(catalog;未定稿邊緣日排除,
      外盤/夜盤/T+1 類 lag=2),過夜對帳收斂、增量持續被 attest(僅滯後一天);
  (b) 分類感知路由——catalog reconcile_scope 選對帳端點(by-date/roster-scoped 抽樣/by-dim-id;
      端點錯配=假 VM/EX,2026-07-14 EX 84,996 之 94% 實證)+ attestation_mode 豁免
      (snapshot 名錄快照型/restating 重述型→誠實列印不計入;coverage→量級對帳)。
  exit code 三態:0=綠(attestation PASS)/2=對帳紅(VM/EX>0,重試不會變綠,終態)/3=未完整(抓取錯,可重試)。

執行指令矩陣:
  python scripts/daily_maintenance.py                          # 全日頻 dataset by-date 增量到今天
  python scripts/daily_maintenance.py --datasets TaiwanStockPrice TaiwanStockMarginPurchaseShortSale
  python scripts/daily_maintenance.py --end 2026-06-09         # 增量到指定日
  python scripts/daily_maintenance.py --audit-since 2026-07-01 # 增量後對帳本次更新之表（#7,固定起日）
  python scripts/daily_maintenance.py --audit-days 14 --audit-all --heal
                                                               # 滾動窗全量 attest+差異日自動 heal(生產預設,selfheal 用)

守 #6（resume 增量）· #3/#4（動態列舉去 intraday）· #17（by-date 省 request）· #7（對帳）· #15（數字皆實跑）。
"""
import argparse
import sys
from datetime import date, timedelta

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db, schema
from augur.audit import reconcile
from augur.ingestion import sync

AUDIT_SAMPLE_STOCKS = 40   # roster-scoped 抽樣股數(等距確定性;全 roster ~2600/dataset 太貴——抽樣=部分覆蓋,印出誠實知會 #7)


def main():
    ap = argparse.ArgumentParser(description="augur 每日維護：by-date 全市場增量 + 可選對帳")
    ap.add_argument("--datasets", nargs="*", help="指定 dataset（預設全部日頻）")
    ap.add_argument("--end", help="增量截止日 YYYY-MM-DD（預設今日）")
    ap.add_argument("--audit-since", help="對帳起始日 YYYY-MM-DD（給了才對帳本次更新之 by-date 表）")
    ap.add_argument("--audit-days", type=int,
                    help="滾動對帳窗:since=today−N(hugo 2026-07-14 拍板 N=14;取代寫死日期——寫死窗會隨時間"
                         "膨脹重演 IP throttle;滾出窗之日以最後一次 attest 定案,同 05-31 凍結先例)")
    ap.add_argument("--audit-all", action="store_true",
                    help="對帳全部日頻表(非只本次有更新者;全量 attest 用)")
    ap.add_argument("--audit-until", help="對帳窗上限覆寫 YYYY-MM-DD(預設=各表 today−finalize_lag_days)")
    ap.add_argument("--heal", action="store_true",
                    help="對帳後對差異日(VM/MIS)自動 sync 重抓再驗(by-date 表;EX 紅旗仍不自動碰)")
    args = ap.parse_args()
    if args.audit_days and not args.audit_since:   # 滾動窗:啟動時計算、整輪固定(不隨跨日午夜漂移)
        args.audit_since = (date.today() - timedelta(days=args.audit_days)).isoformat()

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

        audit_set = ([r for r in results if r["mode"] == "by-date"] if args.audit_all else synced)
        if args.audit_since and audit_set:
            n = len(audit_set)
            print(f"\n對帳（#7，since={args.audit_since}{'、全量' if args.audit_all else ''}"
                  f"{'、heal' if args.heal else ''}）… 共 {n} dataset", flush=True)
            # per-dataset+per-date progress:對帳為 75 dataset×數十交易日之長作業(30分-數時),
            # 舊 list-comprehension 中間零 log→必觸 45 分靜默看門狗誤殺→重試死循環(2026-07-14 實證修)。
            _plog = lambda m: print(m, flush=True)
            with db.transaction(conn) as cur:   # (b) 分類感知:scope 路由端點+mode 豁免+lag 安全邊緣(#29b 住 catalog)
                cur.execute("SELECT dataset, COALESCE(reconcile_scope,'by-date'), attestation_mode, "
                            "finalize_lag_days FROM dataset_catalog WHERE dataset = ANY(%s)",
                            ([r["dataset"] for r in audit_set],))
                cat = {d: (sc, m, lg) for d, sc, m, lg in cur.fetchall()}
            today = date.today()
            recs, exempt = [], []
            for i, r in enumerate(audit_set, 1):
                ds = r["dataset"]
                scope, mode, lag = cat.get(ds, ("by-date", "byte", 1))
                if mode in ("snapshot", "restating", "cadence", "dim_only"):   # 豁免非靜默:逐支列印+彙總(誠實 #15)
                    why = {"snapshot": "名錄快照型:API 僅現況宇宙、DB=as-of 保存",
                           "restating": "重述型:除權息季全序列合法重算",
                           "cadence": "低頻/事件表:滾動窗常空非死、以自身 cadence 定案(#7(b) 2026-07-14)",
                           "dim_only": "維度端點專屬:by-date 回 PK-null 髒列不可 sync、零預測用途→誠實豁免 byte attest(#31 2026-07-14)"}[mode]
                    print(f"  對帳 [{i}/{n}] {ds}: 豁免({mode}——{why};catalog #7(b))", flush=True)
                    exempt.append((ds, mode))
                    continue
                until = args.audit_until or (today - timedelta(days=lag)).isoformat()   # (a) 滾動安全邊緣
                print(f"  對帳 [{i}/{n}] {ds}（scope={scope}、窗至 {until}）…", flush=True)
                if mode == "coverage":                  # 新聞流:量級對帳(逐條 byte 不適用)
                    recs.append(reconcile.reconcile_coverage(conn, ds, progress=_plog))
                elif scope == "roster-scoped":          # per-stock 端點(by-date 對會假 VM/EX);抽樣=部分覆蓋
                    print(f"    (roster-scoped 抽樣 {AUDIT_SAMPLE_STOCKS} 股=部分覆蓋,#7 誠實知會)", flush=True)
                    recs.append(reconcile.reconcile_per_stock(
                        conn, ds, since=args.audit_since, until=until,
                        sample_n=AUDIT_SAMPLE_STOCKS, progress=_plog))
                elif scope == "by-dim-id":              # 逐維度 id 端點
                    recs.append(reconcile.reconcile_by_dim_id(conn, ds, since=args.audit_since, progress=_plog))
                else:                                   # by-date byte-equal(預設)
                    rr = reconcile.reconcile_by_date(conn, ds, since=args.audit_since, until=until, progress=_plog)
                    fix = reconcile.fixable_dates(rr)
                    if args.heal and fix:               # 差異日自動 heal:sync 重抓(冪等覆蓋、非 hand-patch)再驗
                        print(f"    heal:重抓 {len(fix)} 日 {fix[:5]}{'…' if len(fix) > 5 else ''}", flush=True)
                        for d in fix:
                            sync.sync_by_date(conn, ds, start=d, end=d)
                        rr = reconcile.reconcile_by_date(conn, ds, since=args.audit_since, until=until, progress=_plog)
                    recs.append(rr)
            v = reconcile.verdict(*recs)
            asym = sum(r.get("endpoint_asym_ex", 0) for r in recs)   # A 案:by-date 證實之端點不對稱假 EX 扣抵(#15 誠實)
            gaps = v.get("coverage_gap") or []   # 空視窗表=從未對帳(死 feed 跌破窗/低頻窗內無料)→ 不得計綠(#15 假綠 blocker 修)
            samp = v.get("sampled") or []        # #29-2:roster 抽樣表=部分覆蓋(非全宇宙 byte-equal)→ headline 誠實揭露、不當無條件「無幻像」
            tag = "✅ PASS（DB byte-equal API，無幻像）" if v["passed"] else "❌ FAIL（須查根因）"
            print(f"attestation：{tag} | matched={v['matched']:,} "
                  f"value_mismatch={v['value_mismatch']} extra_in_db={v['extra_in_db']} "
                  f"missing_in_db={v['missing_in_db']:,}"
                  + (f" | ⚠部分覆蓋 {len(samp)} 表(roster 抽樣 {AUDIT_SAMPLE_STOCKS} 股、非全宇宙)" if samp else "")
                  + (f" | 豁免 {len(exempt)} 表({'、'.join(d for d, _ in exempt)})" if exempt else "")
                  + (f" | 端點不對稱假 EX 扣抵 {asym}(by-date 證實存在、非幻像)" if asym else "")
                  + (f" | ⚠ 未對帳 {len(gaps)} 表(空視窗/死 feed,須 re-sync 或 catalog 豁免:{'、'.join(gaps)})" if gaps else ""))
            if not v["passed"]:
                # 三態分離(rc=0≠PASS 曾致 selfheal/watchdog/Monitor 三層假綠,2026-07-14 實證):
                # rc=3=可重試(僅 fetch 錯未完整、VM/EX=0、無空視窗);
                # rc=2=終態(重試不會變綠)= 對帳紅(VM/EX>0) 或 coverage_gap(空視窗死 feed,須人 re-sync/exempt)。
                retryable = (v["value_mismatch"] == 0 and v["extra_in_db"] == 0
                             and v["incomplete"] and not gaps)
                sys.exit(3 if retryable else 2)


if __name__ == "__main__":
    main()
