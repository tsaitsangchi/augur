#!/usr/bin/env python
"""augur 對帳總驗 driver — 全 API 表 #7 byte-level attestation,依 catalog reconcile_scope 路由。

🎯 白話:把 DB 既有 API 資料表逐表對 FinMind/FRED 真值比對,**依 catalog `reconcile_scope` 走對的對帳法**——
- by-date(逐交易日全市場):價量/法人/期權 → reconcile_by_date(近 recent_days 定案日;GoldPrice 等聚合表自動對齊日級)。
- roster-scoped(per-stock 端點):籌碼/財報等逐股抓 → reconcile_per_stock(抽樣 ROSTER_SAMPLE 股、部分覆蓋知會 #7)。
- by-dim-id(逐維度碼):總經/匯率/利率 → reconcile_by_dim_id(datalist 驅動)。
- coverage(事件流):News 同日多則文本 → reconcile_coverage(列數量級、非逐 byte)。
- fred_series:逐 series 全史 → reconcile_fred(走 FRED 額度、不佔 FinMind)。
全表清單 = catalog excluded=f(動態、非硬編 #18);infra log 表跳過。逐表即時印,末了彙總 #7 verdict。對帳唯讀、冪等、中斷重跑無害。

守 #7(DB↔API 對帳)· #15(未定案/抽樣/coverage 誠實標註)· #24/#25(走 finmind 內建限速)· #16/#17(clean-room)。
執行指令矩陣:PYTHONPATH=src caffeinate -dimsu venv/bin/python scripts/reconcile_audit.py
      [--only by-date|roster-scoped|by-dim-id|coverage|fred] [--tables A,B] [--recent-days 30]
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import reconcile
from augur.core import db
from augur.features import macro
from augur.ingestion.ingest import FRED_TABLE, _AGGREGATE_DAILY

SKIP = {"data_audit_log", "pipeline_execution_log"}   # infra log,非 API 資料 → 不對帳
RECENT_DAYS = 30
UNSETTLED_BUFFER = 2     # 日頻:最近 N 個交易日視為未定案(當日盤後仍在校正,對帳天然差異)→ 不計 verdict
ROSTER_SAMPLE = 50       # roster-scoped per-stock 對帳抽樣股數(全 roster×31 表太貴;部分覆蓋、報告標註 #7/#15)


def _p(msg):
    print(msg, flush=True)


def _iso(d):
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def _catalog_tables(conn):
    """從 catalog 讀全 excluded=f 表 + reconcile_scope(動態、非硬編 #18)。回 [(dataset, scope)];
    無 reconcile_scope → 預設 by-date;infra log 表略過。catalog 未建 → 空(呼叫端報錯)。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('dataset_catalog')")
        if cur.fetchone()[0] is None:
            return []
        cur.execute("SELECT dataset, COALESCE(reconcile_scope,'by-date') "
                    "FROM dataset_catalog WHERE NOT excluded ORDER BY dataset")
        return [(ds, scope) for ds, scope in cur.fetchall() if ds not in SKIP]


def _recent_since(conn, table, recent_days):
    """近 recent_days(+緩衝)個 distinct date 下限,限對帳近窗加速;表無 date/無資料 → None(全史)。"""
    try:
        with db.transaction(conn) as cur:
            cur.execute(f'SELECT DISTINCT date FROM "{table}" ORDER BY date DESC LIMIT %s',
                        (recent_days + UNSETTLED_BUFFER,))
            dates = [r[0] for r in cur.fetchall()]
        return _iso(dates[-1]) if dates else None   # 回 str(isoformat)：reconcile 各函數 since 比較/SQL/fetch 一律期望 str，免 str>=date 型別錯
    except Exception:
        return None


def _unsettled(conn, table):
    """最近 UNSETTLED_BUFFER 個 distinct date(未定案、不計 verdict);表無 date → 空。"""
    try:
        with db.transaction(conn) as cur:
            cur.execute(f'SELECT DISTINCT date FROM "{table}" ORDER BY date DESC LIMIT %s', (UNSETTLED_BUFFER,))
            return {_iso(r[0]) for r in cur.fetchall()}
    except Exception:
        return set()


def _audit(conn, dataset, scope, recent_days):
    """依 catalog reconcile_scope 路由到正解對帳函數 → 統一 summary。"""
    if dataset == FRED_TABLE:                                  # fred_series:走 FRED API、全 series 全史
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT series_id FROM fred_series ORDER BY series_id")
            sids = [r[0] for r in cur.fetchall()]
        _p(f"[{dataset}] fred:{len(sids)} series 全史")
        return _summary(dataset, "fred",
                        reconcile.reconcile_fred(conn, sids, vintage_map=macro.vintage_map(), progress=_p))

    since = _recent_since(conn, dataset, recent_days)
    sincestr = _iso(since) if since else "全史"
    if scope == "by-dim-id":
        _p(f"[{dataset}] by-dim-id:逐維度 id 重抓 since {sincestr}")
        return _summary(dataset, "by-dim-id", reconcile.reconcile_by_dim_id(conn, dataset, since=since, progress=_p))
    if scope == "roster-scoped":
        _p(f"[{dataset}] roster-scoped:per-stock 抽樣 {ROSTER_SAMPLE} 股 since {sincestr}")
        return _summary(dataset, "roster-scoped",
                        reconcile.reconcile_per_stock(conn, dataset, since=since, sample_n=ROSTER_SAMPLE, progress=_p))
    if _AGGREGATE_DAILY.get(dataset) == "all":                 # News 事件流 → coverage(列數量級、非逐 byte)
        _p(f"[{dataset}] coverage:事件流列數量級對帳")
        return _summary(dataset, "coverage", reconcile.reconcile_coverage(conn, dataset, progress=_p))
    # by-date(含 GoldPrice 聚合,reconcile_by_date 內已對齊日級):排除未定案日 from verdict
    unsettled = _unsettled(conn, dataset)
    _p(f"[{dataset}] by-date:近窗 since {sincestr};未定案緩衝 {sorted(unsettled)}")
    agg = reconcile.reconcile_by_date(conn, dataset, since=since, progress=_p)
    return _summary(dataset, "by-date", agg, unsettled=unsettled)


def _summary(dataset, kind, agg, *, unsettled=None):
    """統一抽出 vm/ex/mis + verdict + 誠實標註(未定案排除 / 抽樣部分覆蓋 / coverage / vintage)。"""
    note = ""
    if kind == "by-date" and unsettled:                        # 排除未定案日(當日盤後校正,非真差異)
        per = agg.get("per_date", {})
        sett = {d: c for d, c in per.items() if d not in unsettled}
        vm = sum(c["value_mismatch"] for c in sett.values())
        ex = sum(c["extra_in_db"] for c in sett.values())
        mis = sum(c["missing_in_db"] for c in sett.values())
        if any(d in unsettled for d in per):
            note = f"未定案 {sorted(unsettled)} 不計 verdict"
    else:
        vm, ex, mis = agg.get("value_mismatch", 0), agg.get("extra_in_db", 0), agg.get("missing_in_db", 0)
    inc = bool(agg.get("incomplete") or agg.get("errors"))
    if kind == "coverage":
        passed = bool(agg.get("coverage_ok"))
        note = f"coverage {'OK' if passed else 'FAIL'}(漏 {mis}、列數量級非逐 byte)"
    else:
        passed = vm == 0 and ex == 0 and not inc
    if agg.get("sampled"):
        note = (note + " ｜ " if note else "") + f"抽樣 {agg.get('stocks', '?')} 股(部分覆蓋 #7)"
    if agg.get("fred_vintage"):
        note = (note + " ｜ " if note else "") + f"Tier A restatement 容忍 {agg['fred_vintage']}"
    # by-date examples 混未定案日差異(無 date 無法乾淨過濾)→ 不放,定案日真差異另查
    examples = [] if kind == "by-date" else agg.get("examples", [])[:3]
    return {"table": dataset, "kind": kind, "matched": agg.get("matched", 0),
            "vm": vm, "ex": ex, "mis": mis, "incomplete": inc, "note": note,
            "examples": examples, "errors": agg.get("errors", [])[:3], "passed": passed}


def _print_row(r):
    """逐表即時印一行(長跑進度監看 #21)+ 標註/差異/錯誤附註。"""
    _p(f"{r['table']:46s} {r['kind']:14s} {r['matched']:>9,} VM{r['vm']:<4} EX{r['ex']:<4} MIS{r['mis']:<7,} "
       f"{'PASS ✅' if r['passed'] else 'FAIL ❌'}")
    if r["note"]:
        _p(f"    └ {r['note']}")
    if r["examples"]:
        _p(f"    └ 差異範例:{r['examples']}")
    if r["errors"]:
        _p(f"    └ ⚠️ 抓取錯誤:{r['errors']}")


def _parse(argv):
    only, tables, recent = None, None, RECENT_DAYS
    i = 0
    while i < len(argv):
        if argv[i] == "--only":
            only = argv[i + 1]; i += 2
        elif argv[i] == "--tables":
            tables = set(argv[i + 1].split(",")); i += 2
        elif argv[i] == "--recent-days":
            recent = int(argv[i + 1]); i += 2
        else:
            i += 1
    return only, tables, recent


def main(argv):
    only, tables, recent = _parse(argv)
    results = []
    with db.connect() as conn:
        plan = _catalog_tables(conn)
        if not plan:
            _p("⚠️ catalog 無 excluded=f 表(catalog 未建?)→ 無表可對帳")
            return 1
        for dataset, scope in plan:
            if tables and dataset not in tables:
                continue
            if only and scope != only and not (only == "fred" and dataset == FRED_TABLE):
                continue
            r = _audit(conn, dataset, scope, recent)
            results.append(r)
            _print_row(r)
    if not results:
        _p("(無符合條件之表)")
        return 0
    all_pass = all(r["passed"] for r in results)
    _p("=" * 78)
    _p(f"#7 對帳總驗 {len(results)} 表 verdict:"
       f"{'全表 PASS ✅(value_mismatch=0 ∧ extra_in_db=0,無幻像)' if all_pass else '有表 FAIL ❌ — 見上逐表'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
