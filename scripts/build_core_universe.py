#!/usr/bin/env python
"""augur 核心股 build — 呼叫 universe.core_gate 算純完整度核心股（pan-historical + as-of 快照、冪等）。

🎯 這支在做什麼（白話）：以 feature_values 既有面板，跑 core_gate.build_universe（pan-historical 單名單、含
look-ahead）與（可選）build_universe_asof（逐 as-of 面板 point-in-time、消 survivorship #8）→ 寫 core_universe /
core_universe_asof。可選流動性分位 gate（--liquidity-pct、動態相對 #9）與月營收對金融保險之 conditional 豁免
（--exempt-revenue-financial：金融業無月營收申報制度、靠財報、不因此誤排）。純 DB 計算、不放 API、可逆。

組合根：把 universe 層接上薄 CLI；核心股判準（地板/conditional）屬決策層，CLI 只暴露參數、不寫死判準（#9/#20）。

守 #1（只收 source-pure 完整股）· #8（asof 消 survivorship）· #10（純完整度、不評分排名）· #18（命名/標頭慣例）。

用法：PYTHONPATH=src python scripts/build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof
      PYTHONPATH=src python scripts/build_core_universe.py                  （pan-historical、全面板、無 gate）
"""
import argparse

from augur.core import db
from augur.universe import core_gate

# 月營收 conditional 豁免之產業（金融保險無月營收申報制度、靠財報）—— TaiwanStockInfo.industry_category 實證值（2026-06-26）
FINANCIAL_INDUSTRIES = ("金融保險", "金融業")


def _panel_dates(cur, since):
    sql = "SELECT DISTINCT panel_date FROM feature_values"
    params = ()
    if since:
        sql += " WHERE panel_date >= %s"
        params = (since,)
    cur.execute(sql + " ORDER BY panel_date", params)
    return [r[0] for r in cur.fetchall()]


def main():
    ap = argparse.ArgumentParser(description="build core_universe（純完整度 gate）")
    ap.add_argument("--since", help="面板起始日 YYYY-MM-DD（預設全部既有面板）")
    ap.add_argument("--liquidity-pct", type=float, help="流動性下界百分位 0-100（動態相對、#9）")
    ap.add_argument("--exempt-revenue-financial", action="store_true", help="月營收對金融保險豁免完整度要求")
    ap.add_argument("--asof", action="store_true", help="同時建 core_universe_asof（point-in-time、消 survivorship）")
    args = ap.parse_args()

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            pds = _panel_dates(cur, args.since)
        if not pds:
            print("無面板（feature_values 空）")
            return
        cond = {"monthly_revenue_yoy": FINANCIAL_INDUSTRIES} if args.exempt_revenue_financial else None
        print(f"build core_universe：{len(pds)} 面板（{pds[0]}..{pds[-1]}）"
              f" liquidity_pct={args.liquidity_pct} 月營收豁免金融={bool(cond)}")
        res = core_gate.build_universe(conn, pds, liquidity_pct=args.liquidity_pct, conditional=cond)
        msg = f"  pan-historical 核心：{res['core']} 股 / {res['canonical_features']} 特徵"
        if args.liquidity_pct is not None:
            msg += f" / 流動性閾值 {res.get('liquidity_threshold')}"
        print(msg)
        if args.asof:
            summ = core_gate.build_universe_asof(conn, pds, liquidity_pct=args.liquidity_pct, conditional=cond)
            vals = list(summ.values())
            print(f"  as-of 快照：{len(summ)} 面板，核心數 {min(vals)}..{max(vals)}（早→晚）")


if __name__ == "__main__":
    main()
