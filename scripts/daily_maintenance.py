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
    ap.add_argument("--audit-only", action="store_true",
                    help="跳過 by-date 全量 pre-sync,直接對現況 DB 對帳(#31:避 --audit-all 回填 audit-豁免之 stalled "
                         "snapshot 表〔JapanStockInfo 自2019〕白燒額度;被審 byte 表由日常 sync 維持當前、--heal 仍 targeted 補差異日)")
    ap.add_argument("--full-universe", action="store_true",
                    help="roster-scoped 表逐股對帳**全真名冊**(3,114 真股、排除權證污染;非抽樣 40 股)——全宇宙真義 attest,"
                         "sampled_n 歸零、名實相符。~84k FinMind calls/~14h(#24/#25:額度充足+主機不睡眠#22 才跑;過夜須 resume-safe)")
    args = ap.parse_args()
    if args.audit_days and not args.audit_since:   # 滾動窗:啟動時計算、整輪固定(不隨跨日午夜漂移)
        args.audit_since = (date.today() - timedelta(days=args.audit_days)).isoformat()

    with db.connect() as conn:
        with db.transaction(conn) as cur:           # PHASE 1：確保 infra log 表存在（冪等）
            schema.bootstrap_infra(cur)

        if args.audit_only:                          # #31:跳過全量 pre-sync,直接對帳現況 DB(避回填豁免表白燒額度)
            with db.transaction(conn) as cur:
                # #31:只審 catalog 有 reconcile_scope 且**表實存**者——tick/intraday 等 catalog 有條目但 augur 不儲存(表不存在)
                # 之污染排除(2026-07-14 --audit-only 暴露 11 張 UndefinedTable);表存在性 to_regclass 判(免逐表 information_schema)
                cur.execute("SELECT dataset FROM dataset_catalog "
                            "WHERE reconcile_scope IS NOT NULL AND to_regclass('\"'||dataset||'\"') IS NOT NULL"
                            + (" AND dataset = ANY(%s)" if args.datasets else "")
                            + " ORDER BY dataset", (args.datasets,) if args.datasets else ())
                audit_set = [{"dataset": r[0]} for r in cur.fetchall()]
            print(f"\n(--audit-only:跳過 by-date 全量 sync,直接對帳現況 DB {len(audit_set)} 表;--heal 仍 targeted 補差異日)")
        else:
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
            def _route(ds, scope, mode, until):     # 共用政策路由(#12,(B)):豁免+端點皆走 reconcile.attest_route
                return reconcile.attest_route(conn, ds, scope=scope, mode=mode, since=args.audit_since,
                                              until=until,
                                              sample_n=None if args.full_universe else AUDIT_SAMPLE_STOCKS,
                                              roster_only=args.full_universe, progress=_plog)
            for i, r in enumerate(audit_set, 1):
                ds = r["dataset"]
                scope, mode, lag = cat.get(ds, ("by-date", "byte", 1))
                until = args.audit_until or (today - timedelta(days=lag)).isoformat()   # (a) 滾動安全邊緣
                print(f"  對帳 [{i}/{n}] {ds}（{scope}/{mode}、窗至 {until}）…", flush=True)
                try:                                    # #7 韌性:一表對帳錯(schema/DB 錯)→記 incomplete、續跑不崩全部
                    kind, res = _route(ds, scope, mode, until)
                    if kind == "exempt":                # attestation_mode 豁免(SSOT reconcile.EXEMPT_*)——與 reconcile_audit 同政策
                        print(f"    豁免({res['mode']}——{res['reason']};catalog #7(b))", flush=True)
                        exempt.append((ds, res["mode"]))
                        continue
                    if args.heal and kind in ("byte", "roster"):   # daily 特有 heal(#31 ③ roster+by-date 對稱):diff 日 by-date 重抓補邊緣舊值再驗
                        fixd = sorted(res.get("fix_dates") or reconcile.fixable_dates(res))
                        if fixd:
                            print(f"    heal:重抓 {len(fixd)} 日 {fixd[:5]}{'…' if len(fixd) > 5 else ''}", flush=True)
                            for d in fixd:
                                # AUD-02:heal 覆寫前快照被取代原值(P4.E5;reason='daily_heal',run_id 決策 B 事後回填)
                                sync.sync_by_date(conn, ds, start=d, end=d, snapshot_reason="daily_heal")
                            _, res = _route(ds, scope, mode, until)     # 補後再驗
                    recs.append(res)
                except Exception as e:                  # noqa: BLE001  對帳需韌性:單表失敗記帳續跑,不讓一表崩掉全量 attest
                    conn.rollback()                     # 清該表殘留錯誤交易態,免污染後續表
                    print(f"    ⚠ {ds} 對帳失敗,記 incomplete、跳過:{type(e).__name__}: {str(e)[:80]}", flush=True)
                    recs.append({"table": ds, "matched": 0, "value_mismatch": 0, "missing_in_db": 0,
                                 "extra_in_db": 0, "errors": [{"dataset": ds, "error": str(e)}], "incomplete": True})
            v = reconcile.verdict(*recs)
            asym = sum(r.get("endpoint_asym_ex", 0) for r in recs)   # A 案:by-date 證實之端點不對稱假 EX 扣抵(#15 誠實)
            retr = sum(r.get("upstream_retracted", 0) for r in recs)  # 撤列容忍(雙端點證實 API 現況無;hugo 拍 A 2026-07-16)
            gaps = v.get("coverage_gap") or []   # 空視窗表=從未對帳(死 feed 跌破窗/低頻窗內無料)→ 不得計綠(#15 假綠 blocker 修)
            samp = v.get("sampled") or []        # #29-2:roster 抽樣表=部分覆蓋(非全宇宙 byte-equal)→ headline 誠實揭露、不當無條件「無幻像」
            inc = v.get("incomplete_tables") or []   # 抓取失敗未比對之表(擋綠)→ headline 列名供診斷(#8 不藏錯)
            tag = "✅ PASS（DB byte-equal API，無幻像）" if v["passed"] else "❌ FAIL（須查根因）"
            print(f"attestation：{tag} | matched={v['matched']:,} "
                  f"value_mismatch={v['value_mismatch']} extra_in_db={v['extra_in_db']} "
                  f"missing_in_db={v['missing_in_db']:,}"
                  + (f" | ⚠部分覆蓋 {len(samp)} 表(roster 抽樣 {AUDIT_SAMPLE_STOCKS} 股、非全宇宙)" if samp else "")
                  + (f" | 豁免 {len(exempt)} 表({'、'.join(d for d, _ in exempt)})" if exempt else "")
                  + (f" | 端點不對稱假 EX 扣抵 {asym}(by-date 證實存在、非幻像)" if asym else "")
                  + (f" | 上游撤列容忍 {retr}(雙端點證實 API 現況無=合法 restatement,DB 保留 as-of 真相)" if retr else "")
                  + (f" | ⚠ 未對帳 {len(gaps)} 表(空視窗/死 feed,須 re-sync 或 catalog 豁免:{'、'.join(gaps)})" if gaps else "")
                  + (f" | ⚠ 未完整 {len(inc)} 表(抓取失敗、擋綠:{'、'.join(inc)})" if inc else ""))
            if not args.datasets:            # (a) 正典全量 attest 才留檔:寫 attestation_result(E1 gate 讀「最近 PASS 且夠新」;run 與 gate 檢查解耦)
                drv = "daily_maintenance" + (" --audit-only" if args.audit_only else "") + (" --heal" if args.heal else "")
                with db.transaction(conn) as cur:
                    cur.execute(
                        "INSERT INTO attestation_result (driver,passed,matched,value_mismatch,extra_in_db,"
                        "missing_in_db,exempt_n,sampled_n,coverage_gap_n,incomplete_n,audit_since,note) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (drv, v["passed"], v["matched"], v["value_mismatch"], v["extra_in_db"], v["missing_in_db"],
                         len(exempt), len(samp), len(gaps), len(inc), args.audit_since,
                         (f"豁免 {len(exempt)}、部分覆蓋 {len(samp)}、端點扣抵 {asym}"
                          + (f"、未對帳 {gaps}" if gaps else "") + (f"、未完整 {inc}" if inc else ""))))
                print(f"  → attestation_result 留檔(driver={drv}, passed={v['passed']})", flush=True)
            if not v["passed"]:
                # 三態分離(rc=0≠PASS 曾致 selfheal/watchdog/Monitor 三層假綠,2026-07-14 實證):
                # rc=3=可重試(僅 fetch 錯未完整、VM/EX=0、無空視窗);
                # rc=2=終態(重試不會變綠)= 對帳紅(VM/EX>0) 或 coverage_gap(空視窗死 feed,須人 re-sync/exempt)。
                retryable = (v["value_mismatch"] == 0 and v["extra_in_db"] == 0
                             and v["incomplete"] and not gaps)
                sys.exit(3 if retryable else 2)


if __name__ == "__main__":
    main()
