#!/usr/bin/env python
"""🎯 全真名冊全宇宙 attestation 編排器(resume-safe)——roster-scoped 表逐股對帳全 3,114 真股(非抽樣 40)。

白話:arena G1 前置(D-5 hugo 拍板 2026-07-16)=全宇宙 byte 對帳、排除權證污染,讓「真綠」名實相符。
~84k FinMind calls/~14h 過夜作業→**必 resume-safe**:逐表 checkpoint 進 full_attest_progress,
重啟跳過已完成表(中斷最多損單表~30分、非 14h);全表完才彙整寫**一筆** attestation_result。
守 #7(誠實對帳) #12(沿用 reconcile.attest_route 政策單一住所) #22(resume 後路) #24/#25(逐表前置探測、見 ban 即停) #29(個別可執行/指令矩陣/graceful/selftest)。

執行指令矩陣:
  python scripts/full_universe_attest.py                              # 無參數:印矩陣+進度(唯讀)
  python scripts/full_universe_attest.py --dry-run --audit-days 14    # 列計畫+progress、不抓(0 call)
  python scripts/full_universe_attest.py --run --audit-days 14        # 放量:逐表全宇宙對帳、checkpoint、寫 attestation_result
  python scripts/full_universe_attest.py --run --run-id fullattest_20260716 --audit-since 2026-07-02  # 續跑(pin run_id+窗)
  python scripts/full_universe_attest.py --run ... --heal             # 對差異日 heal(達真綠;首跑建議先不 heal 量 baseline)
  python scripts/full_universe_attest.py --selftest                   # 純函式紅綠(零 IO)+ DDL 結構斷言
"""
import _bootstrap  # noqa: F401
import argparse
import json
import sys
from datetime import date, timedelta

from augur.core import db, schema
from augur.audit import reconcile
from augur.ingestion import sync, finmind

PROGRESS_DDL = """
CREATE TABLE IF NOT EXISTS full_attest_progress (
  run_id   text NOT NULL,
  dataset  text NOT NULL,
  done_at  timestamptz NOT NULL DEFAULT now(),
  result   jsonb NOT NULL,
  PRIMARY KEY (run_id, dataset)
)"""

BAN_PROBE_STOCK = "2330"          # 台積電——逐表前置 IP 健康探測用(單股單日 #25)
BAN_ABS_ERRORS = 100              # 單表 fetch 錯 ≥ 此數 → 疑 re-ban → 立即探測;失敗即停(#24/#25 見訊號即停)
EXIT_BAN = 42                     # 專用退出碼:IP ban 停(watchdog 不得自動重試、須退回休息 #25)


def _plan(cur):
    """全 audit_set(=daily_maintenance --audit-only 同集):catalog reconcile_scope 非空且表實存。
    回 [(dataset, scope, mode, finalize_lag_days)];roster-scoped=全宇宙貴段,其餘(by-date/fred/market/dim)便宜。"""
    cur.execute("SELECT dataset, COALESCE(reconcile_scope,'by-date'), attestation_mode, "
                "COALESCE(finalize_lag_days,1) FROM dataset_catalog "
                "WHERE reconcile_scope IS NOT NULL AND to_regclass('\"'||dataset||'\"') IS NOT NULL "
                "ORDER BY dataset")
    return [(ds, sc, m, lg) for ds, sc, m, lg in cur.fetchall()]


def _clean(res):
    """留 verdict/headline 需之可序列化欄(棄 fix_dates set / per_stock dict → JSONB 相容)。"""
    return {"kind": "recs", "table": res.get("table"),
            "matched": int(res.get("matched", 0)),
            "value_mismatch": int(res.get("value_mismatch", 0)),
            "extra_in_db": int(res.get("extra_in_db", 0)),
            "missing_in_db": int(res.get("missing_in_db", 0)),
            "incomplete": bool(res.get("incomplete")),
            "coverage_gap": bool(res.get("coverage_gap")),
            "sampled": bool(res.get("sampled")),
            "endpoint_asym_ex": int(res.get("endpoint_asym_ex", 0)),
            "errors": res.get("errors", []),
            "frame": res.get("frame")}


def _err_count(res):
    """單表 fetch 錯數(ban 偵測用;純函式可測)。"""
    return len(res.get("errors") or [])


def _ip_probe(conn, probe_day):
    """單股單日 IP 健康探測(#25;1 call)→ True=健康。"""
    try:
        finmind.fetch("TaiwanStockPrice", data_id=BAN_PROBE_STOCK, start_date=probe_day, end_date=probe_day)
        return True
    except Exception:
        return False


def _done_set(cur, run_id):
    cur.execute("SELECT dataset, result FROM full_attest_progress WHERE run_id=%s", (run_id,))
    return {ds: res for ds, res in cur.fetchall()}


def _persist(conn, run_id, ds, result):
    with db.transaction(conn) as cur:
        cur.execute("INSERT INTO full_attest_progress (run_id,dataset,result) VALUES (%s,%s,%s) "
                    "ON CONFLICT (run_id,dataset) DO UPDATE SET result=EXCLUDED.result, done_at=now()",
                    (run_id, ds, json.dumps(result, ensure_ascii=False, default=str)))


def _probe_day(conn):
    with db.transaction(conn) as cur:
        cur.execute('SELECT max(date) FROM "TaiwanStockPrice"')
        d = cur.fetchone()[0]
    return d.isoformat() if not isinstance(d, str) else d


def _aggregate_and_record(conn, run_id, audit_since):
    """全表完 → 彙整 progress → 寫一筆 attestation_result(driver=full_universe;sampled_n=0 名實相符)。"""
    with db.transaction(conn) as cur:
        done = _done_set(cur, run_id)
    recs = [r for r in done.values() if r.get("kind") == "recs"]
    exempt = [r for r in done.values() if r.get("kind") == "exempt"]
    v = reconcile.verdict(*recs) if recs else {"passed": False, "matched": 0, "value_mismatch": 0,
                                               "extra_in_db": 0, "missing_in_db": 0, "coverage_gap": [],
                                               "sampled": [], "incomplete_tables": ["<無 recs>"]}
    asym = sum(r.get("endpoint_asym_ex", 0) for r in recs)
    gaps, samp, inc = v["coverage_gap"], v["sampled"], v.get("incomplete_tables", [])
    tag = "✅ PASS(全宇宙 byte-equal API、無幻像)" if v["passed"] else "❌ FAIL(須查根因)"
    print(f"\n═══ 全宇宙 attestation:{tag} ═══")
    print(f"  matched={v['matched']:,} value_mismatch={v['value_mismatch']} extra_in_db={v['extra_in_db']} "
          f"missing_in_db={v['missing_in_db']:,} | 豁免 {len(exempt)} | 端點扣抵 {asym}"
          + (f" | ⚠部分覆蓋 {len(samp)}" if samp else " | 抽樣 0(全宇宙)")
          + (f" | ⚠未對帳 {gaps}" if gaps else "") + (f" | ⚠未完整 {inc}" if inc else ""))
    drv = "full_universe"
    note = (f"全真名冊全宇宙(roster_only、3114 真股、排除權證);豁免 {len(exempt)}、端點扣抵 {asym}"
            + (f"、未對帳 {gaps}" if gaps else "") + (f"、未完整 {inc}" if inc else ""))
    with db.transaction(conn) as cur:
        cur.execute("INSERT INTO attestation_result (driver,passed,matched,value_mismatch,extra_in_db,"
                    "missing_in_db,exempt_n,sampled_n,coverage_gap_n,incomplete_n,audit_since,note) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (drv, v["passed"], v["matched"], v["value_mismatch"], v["extra_in_db"], v["missing_in_db"],
                     len(exempt), len(samp), len(gaps), len(inc), audit_since, note))
    print(f"  → attestation_result 留檔(driver={drv}, passed={v['passed']}, sampled_n={len(samp)})")
    return 0 if v["passed"] else 2


def run(args, dry=False):
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            schema.bootstrap_infra(cur)
            cur.execute(PROGRESS_DDL)
        since = args.audit_since or (date.today() - timedelta(days=args.audit_days)).isoformat()
        run_id = args.run_id or f"fullattest_{date.today().isoformat()}"
        with db.transaction(conn) as cur:
            plan = _plan(cur)
            done = _done_set(cur, run_id)
        today = date.today()
        pending = [p for p in plan if p[0] not in done]
        print(f"run_id={run_id}  since={since}  計畫 {len(plan)} 表、已完成 {len(done)}、待跑 {len(pending)}")
        print(f"（續跑指令:python scripts/full_universe_attest.py --run --run-id {run_id} --audit-since {since}"
              + (" --heal" if args.heal else "") + "）")
        if dry:
            for ds, sc, m, lg in plan:
                st = "✓done" if ds in done else ("豁免" if m in reconcile.EXEMPT_MODES else "待跑")
                print(f"  [{st:6s}] {ds:44s} {sc}/{m}")
            print("(--dry-run:0 FinMind call)")
            return 0
        probe_day = _probe_day(conn)
        for i, (ds, scope, mode, lag) in enumerate(plan, 1):
            if ds in done:
                continue
            # #25 逐表前置 IP 探測(僅需真抓之表;豁免表跳過探測)
            if mode not in reconcile.EXEMPT_MODES and not _ip_probe(conn, probe_day):
                print(f"  ✗ [{i}/{len(plan)}] 前置探測失敗 @ {ds}——疑 IP ban,停(#25 退回休息);"
                      f"progress 已存 {len(done)} 表,額度恢復後同指令續跑", flush=True)
                return EXIT_BAN
            until = args.audit_until or (today - timedelta(days=lag)).isoformat()
            print(f"  對帳 [{i}/{len(plan)}] {ds}（{scope}/{mode}、窗 {since}~{until}、全宇宙）…", flush=True)
            try:
                kind, res = reconcile.attest_route(conn, ds, scope=scope, mode=mode, since=since,
                                                   until=until, sample_n=None, roster_only=True,
                                                   progress=lambda msg: print(msg, flush=True))
                if kind == "exempt":
                    print(f"    豁免({res['mode']}——{res['reason']})", flush=True)
                    _persist(conn, run_id, ds, {"kind": "exempt", "table": ds, "mode": res["mode"]})
                    continue
                if args.heal and kind in ("byte", "roster"):
                    fixd = sorted(res.get("fix_dates") or reconcile.fixable_dates(res))
                    if fixd:
                        print(f"    heal:重抓 {len(fixd)} 日再驗", flush=True)
                        for d in fixd:
                            # AUD-02:heal 覆寫前快照被取代原值(P4.E5;此亦 heal 呼叫端,不透傳=靜默 last-write-wins)
                            sync.sync_by_date(conn, ds, start=d, end=d, snapshot_reason="full_universe_heal")
                        _, res = reconcile.attest_route(conn, ds, scope=scope, mode=mode, since=since,
                                                        until=until, sample_n=None, roster_only=True,
                                                        progress=lambda msg: print(msg, flush=True))
                clean = _clean(res)
                _persist(conn, run_id, ds, clean)
                # ban 偵測:單表大量 fetch 錯 → 探測確認;失敗即停(不 plow 過所有表)
                if _err_count(res) >= BAN_ABS_ERRORS and not _ip_probe(conn, probe_day):
                    print(f"    ✗ {ds} 錯 {_err_count(res)} 且探測失敗——疑 mid-table IP ban,停(#25);"
                          f"該表已 checkpoint、續跑會重驗", flush=True)
                    return EXIT_BAN
                print(f"    ✓ VM={clean['value_mismatch']} EX={clean['extra_in_db']} "
                      f"MIS={clean['missing_in_db']:,} matched={clean['matched']:,}"
                      + (f" ⚠err={_err_count(res)}" if _err_count(res) else ""), flush=True)
            except Exception as e:   # noqa: BLE001  韌性:單表失敗記 incomplete、續跑不崩全部(#7)
                conn.rollback()
                print(f"    ⚠ {ds} 失敗,記 incomplete:{type(e).__name__}: {str(e)[:80]}", flush=True)
                _persist(conn, run_id, ds, {"kind": "recs", "table": ds, "matched": 0, "value_mismatch": 0,
                                            "extra_in_db": 0, "missing_in_db": 0, "incomplete": True,
                                            "coverage_gap": False, "sampled": False, "endpoint_asym_ex": 0,
                                            "errors": [{"dataset": ds, "error": str(e)}]})
        return _aggregate_and_record(conn, run_id, since)


def _status():
    """無參數 graceful:印矩陣+各 run_id 進度(唯讀)。"""
    print(__doc__.split("執行指令矩陣:")[0].strip())
    print("\n執行指令矩陣:" + __doc__.split("執行指令矩陣:")[1])
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            if cur.execute("SELECT to_regclass('public.full_attest_progress')") or cur.fetchone()[0]:
                cur.execute("SELECT run_id, count(*), max(done_at) FROM full_attest_progress GROUP BY run_id ORDER BY 3 DESC")
                for rid, n, mx in cur.fetchall():
                    print(f"  進度 {rid}: {n} 表完成 @ {mx}")
    except Exception as e:   # noqa: BLE001
        print(f"(進度讀取略過:{type(e).__name__})")
    return 0


def _selftest():
    """純函式紅綠(零 IO)+ DDL 結構斷言(#29a;IO-bound 部分僅結構/序列化不變式)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("PROGRESS_DDL 冪等 CREATE + PK", "CREATE TABLE IF NOT EXISTS" in PROGRESS_DDL and "PRIMARY KEY" in PROGRESS_DDL)
    sample = {"table": "T", "matched": 5, "value_mismatch": 1, "extra_in_db": 0, "missing_in_db": 2,
              "incomplete": False, "coverage_gap": False, "sampled": False, "endpoint_asym_ex": 3,
              "errors": [{"stock_id": "x", "error": "e"}], "fix_dates": {"2026-07-01"}, "per_stock": {"x": {}}}
    c = _clean(sample)
    chk("_clean 棄 set/per_stock(JSONB 相容)", "fix_dates" not in c and "per_stock" not in c)
    chk("_clean JSON 可序列化", json.dumps(c) and json.loads(json.dumps(c))["value_mismatch"] == 1)
    chk("_clean kind=recs", c["kind"] == "recs")
    chk("_err_count 數 errors", _err_count(sample) == 1 and _err_count({"errors": []}) == 0)
    # _clean 之欄餵 verdict 不缺鍵(全宇宙彙整不變式)
    v = reconcile.verdict(_clean({**sample, "value_mismatch": 0, "extra_in_db": 0, "errors": []}))
    chk("_clean → verdict 不缺鍵、健康列 passed", v["passed"] is True)
    chk("_clean(VM>0) → verdict 擋綠", reconcile.verdict(c)["passed"] is False)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--run", action="store_true", help="放量:逐表全宇宙對帳、checkpoint、寫 attestation_result")
    ap.add_argument("--dry-run", action="store_true", help="列計畫+progress、不抓(0 FinMind call)")
    ap.add_argument("--run-id", help="pin run_id 續跑(預設 fullattest_<today>;跨日續跑須明給以免 run_id 漂移)")
    ap.add_argument("--audit-since", help="對帳起始日 YYYY-MM-DD(續跑須 pin,以免 today−days 漂移)")
    ap.add_argument("--audit-days", type=int, default=14, help="滾動窗 since=today−N(預設 14;--audit-since 覆寫)")
    ap.add_argument("--audit-until", help="窗上限覆寫 YYYY-MM-DD(預設各表 today−finalize_lag_days)")
    ap.add_argument("--heal", action="store_true", help="對差異日 heal 再驗(達真綠;首跑建議先不 heal 量 baseline)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.dry_run:
        return run(args, dry=True)
    if args.run:
        return run(args, dry=False)
    return _status()


if __name__ == "__main__":
    sys.exit(main())
