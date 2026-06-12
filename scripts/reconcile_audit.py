#!/usr/bin/env python
"""augur 對帳總驗 driver — 全 API 表 #7 byte-level attestation(近期切片 + 低成本表全史)。

🎯 白話:把 DB 既有 API 資料表逐表對 FinMind/FRED 真值逐欄 byte 比對,分策略控成本——
- 日頻大表:對近 ~30 個「定案」交易日(排除最近未定案緩衝日;當日盤後資料還在累積/校正,不可對)。
- 季/低頻表(財報三表):全史對帳(distinct date 少、成本低)。
- FRED:逐 series 全史對帳(走 FRED 額度,不佔 FinMind)。
- 名冊 roster:一次抓比對。infra log 表(非 API 資料)跳過。
逐表即時印結果,末了彙總 #7 verdict(value_mismatch=0 ∧ extra_in_db=0)。對帳唯讀、冪等,中斷重跑無害。

守 #7(DB↔API 對帳)· #15(未定案日差異誠實標註、非當資料錯)· #24/#25(走 finmind 內建限速、最小擾動)· #16/#17(clean-room)。
用法:PYTHONPATH=src caffeinate -dimsu venv/bin/python scripts/reconcile_audit.py
      [--only daily|quarterly|fred|roster] [--tables A,B] [--recent-days 30]
"""
from __future__ import annotations

import sys

from augur.audit import reconcile
from augur.core import db

DAILY = [
    "TaiwanStockPrice", "TaiwanStockPriceAdj", "TaiwanStockPER",
    "TaiwanStockInstitutionalInvestorsBuySell", "TaiwanStockTotalInstitutionalInvestors",
    "TaiwanStockGovernmentBankBuySell", "TaiwanDailyShortSaleBalances", "TaiwanStockShareholding",
]
QUARTERLY = ["TaiwanStockBalanceSheet", "TaiwanStockFinancialStatements", "TaiwanStockCashFlowsStatement"]
ROSTER = ["TaiwanStockInfo"]
SKIP = ["data_audit_log", "pipeline_execution_log"]   # infra log,非 API 資料 → 不對帳

RECENT_DAYS = 30
UNSETTLED_BUFFER = 2   # 日頻:最近 N 個交易日視為未定案(當日盤後仍在校正,對帳天然差異)


def _p(msg):
    print(msg, flush=True)


def _iso(d):
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def audit_daily(conn, table, recent_days):
    """日頻表:對近 recent_days 定案日 byte 對帳;最近 UNSETTLED_BUFFER 日另標(不計 verdict)。"""
    with conn.cursor() as cur:
        cur.execute(f'SELECT DISTINCT date FROM "{table}" ORDER BY date DESC LIMIT %s',
                    (recent_days + UNSETTLED_BUFFER,))
        dates = [r[0] for r in cur.fetchall()]
    since = dates[-1]
    unsettled = {_iso(d) for d in dates[:UNSETTLED_BUFFER]}
    _p(f"[{table}] 日頻:近 {len(dates)} 交易日 since {_iso(since)};未定案緩衝 {sorted(unsettled)}")
    agg = reconcile.reconcile_by_date(conn, table, since=since, progress=_p)
    settled = {d: c for d, c in agg["per_date"].items() if d not in unsettled}
    uns = {d: c for d, c in agg["per_date"].items() if d in unsettled}
    svm = sum(c["value_mismatch"] for c in settled.values())
    sex = sum(c["extra_in_db"] for c in settled.values())
    smis = sum(c["missing_in_db"] for c in settled.values())
    # 日頻 examples 混入未定案日差異(無 date 無法乾淨過濾)→ 不放,定案日真差異另查
    return {"table": table, "kind": "daily", "matched": agg["matched"], "days": agg["days"],
            "vm": svm, "ex": sex, "mis": smis, "unsettled": uns, "errors": agg["errors"],
            "examples": [], "passed": svm == 0 and sex == 0 and not agg["errors"]}


def audit_quarterly(conn, table):
    """季頻表:全史逐(季)日對帳。最新季若未完全定案 → 於報告標註,人工判斷。"""
    _p(f"[{table}] 季頻:全史對帳")
    agg = reconcile.reconcile_by_date(conn, table, since=None, progress=_p)
    return {"table": table, "kind": "quarterly", "matched": agg["matched"], "days": agg["days"],
            "vm": agg["value_mismatch"], "ex": agg["extra_in_db"], "mis": agg["missing_in_db"],
            "unsettled": {}, "errors": agg["errors"], "examples": agg["examples"],
            "passed": agg["value_mismatch"] == 0 and agg["extra_in_db"] == 0 and not agg["errors"]}


def audit_fred(conn):
    """FRED:逐 series 全史對帳(走 FRED 額度,不佔 FinMind)。"""
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT series_id FROM fred_series ORDER BY series_id")
        sids = [r[0] for r in cur.fetchall()]
    _p(f"[fred_series] FRED:{len(sids)} series 全史對帳")
    agg = reconcile.reconcile_fred(conn, sids, progress=_p)
    return {"table": "fred_series", "kind": "fred", "matched": agg["matched"], "days": len(sids),
            "vm": agg["value_mismatch"], "ex": agg["extra_in_db"], "mis": agg["missing_in_db"],
            "unsettled": {}, "errors": agg.get("errors", []), "examples": agg["examples"],
            "passed": agg["value_mismatch"] == 0 and agg["extra_in_db"] == 0}


def audit_roster(conn, table):
    """名冊 roster:API 一次抓比對全表。"""
    _p(f"[{table}] roster:一次抓比對")
    agg = reconcile.reconcile_market(conn, table, progress=_p)
    return {"table": table, "kind": "roster", "matched": agg["matched"], "days": 1,
            "vm": agg["value_mismatch"], "ex": agg["extra_in_db"], "mis": agg["missing_in_db"],
            "unsettled": {}, "errors": agg.get("errors", []), "examples": agg["examples"],
            "passed": agg["value_mismatch"] == 0 and agg["extra_in_db"] == 0 and not agg.get("errors")}


def _print_row(r):
    """逐表即時印結果一行(供長跑進度監看 #21)+ 差異/未定案/錯誤附註。"""
    _p(f"{r['table']:44s} {r['matched']:>10,} VM{r['vm']:<4} EX{r['ex']:<4} MIS{r['mis']:<7,} "
       f"{'PASS ✅' if r['passed'] else 'FAIL ❌'}")
    if r["unsettled"]:
        _p(f"    └ 未定案日(預期差異,不計 verdict):{r['unsettled']}")
    if r["examples"]:
        _p(f"    └ 差異範例:{r['examples'][:3]}")
    if r["errors"]:
        _p(f"    └ ⚠️ 抓取錯誤:{r['errors'][:3]}")


def _parse(argv):
    only, tables, recent = None, None, RECENT_DAYS
    i = 0
    while i < len(argv):
        if argv[i] == "--only":
            only = argv[i + 1]; i += 2
        elif argv[i] == "--tables":
            tables = argv[i + 1].split(","); i += 2
        elif argv[i] == "--recent-days":
            recent = int(argv[i + 1]); i += 2
        else:
            i += 1
    return only, tables, recent


def main(argv):
    only, tables, recent = _parse(argv)
    results = []

    def run(r):
        results.append(r)
        _print_row(r)

    with db.connect() as conn:
        if only in (None, "daily"):
            for t in (tables or DAILY):
                if t in DAILY:
                    run(audit_daily(conn, t, recent))
        if only in (None, "quarterly"):
            for t in (tables or QUARTERLY):
                if t in QUARTERLY:
                    run(audit_quarterly(conn, t))
        if only in (None, "fred") and (not tables or "fred_series" in tables):
            run(audit_fred(conn))
        if only in (None, "roster"):
            for t in (tables or ROSTER):
                if t in ROSTER:
                    run(audit_roster(conn, t))

    all_pass = all(r["passed"] for r in results)
    _p("=" * 72)
    _p(f"#7 對帳總驗 verdict:{'全表 PASS ✅(value_mismatch=0 ∧ extra_in_db=0,無幻像)' if all_pass else '有表 FAIL ❌ — 見上逐表'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
