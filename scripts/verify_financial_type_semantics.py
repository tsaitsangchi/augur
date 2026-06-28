#!/usr/bin/env python
"""augur 財報 type 語意逐一驗 — 224 type 之累計YTD/單季/snapshot 用多股數據定論(非抽樣推斷)。

🎯 這支在做什麼(白話):上次累計語意只抽 1 股 1 type 推斷整表。本支對**每個 type**、跨**多股**驗:
同年四季 |value| 是否單調↑(=累計 YTD)。多數股單調→累計;否→單季/snapshot。
資產負債表(存量)另標 snapshot(其 type 本為時點水位、非流量)。輸出每 type 之數據定論 + 測試股數。

唯讀、本地、零 usage(#28)。守 #15(逐一驗、揭露測試 n、不抽樣推斷)。
用法:PYTHONPATH=src python scripts/verify_financial_type_semantics.py
"""
import argparse

import numpy as np

from augur.core import db

TABLES = {
    "TaiwanStockFinancialStatements": "損益(income)",
    "TaiwanStockCashFlowsStatement": "現金流(cashflow)",
    "TaiwanStockBalanceSheet": "資產負債(balance、存量)",
}
YEAR = 2023


def classify_type(cur, table, ty):
    """跨股驗某 type 同年四季單調性 → (語意, 測試股數, 單調比例)。"""
    cur.execute(f'SELECT stock_id, date, value FROM "{table}" WHERE type=%s '
                f"AND date >= '{YEAR}-01-01' AND date < '{YEAR+1}-01-01' AND value IS NOT NULL "
                f'ORDER BY stock_id, date', (ty,))
    by_stock = {}
    for sid, d, v in cur.fetchall():
        by_stock.setdefault(sid, []).append(float(v))
    mono = tested = 0
    for sid, vals in by_stock.items():
        if len(vals) >= 3:
            tested += 1
            av = [abs(x) for x in vals]
            if all(av[i] <= av[i + 1] + 1e-6 for i in range(len(av) - 1)):
                mono += 1
    if tested < 5:
        return "?(樣本不足)", tested, None
    frac = mono / tested
    sem = "累計YTD" if frac >= 0.8 else ("單季" if frac <= 0.4 else "混合?")
    return sem, tested, frac


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", help="只驗單表")
    args = ap.parse_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            tables = [args.table] if args.table else list(TABLES)
            for table in tables:
                cur.execute(f'SELECT DISTINCT type FROM "{table}" ORDER BY type')
                types = [r[0] for r in cur.fetchall()]
                print(f"\n### {table}（{TABLES.get(table,'')}、{len(types)} type）")
                agg = {}
                for ty in types:
                    sem, n, frac = classify_type(cur, table, ty)
                    agg[sem] = agg.get(sem, 0) + 1
                    fs = f"{frac:.0%}" if frac is not None else "-"
                    print(f"  {ty[:52]:52s} {sem:10s} (單調{fs}、{n}股)")
                print(f"  → 彙總: {agg}")


if __name__ == "__main__":
    main()
