#!/usr/bin/env python
"""augur 核心股 build — 呼叫 universe.core_gate 算純完整度核心股（pan-historical + as-of 快照、冪等）。

🎯 這支在做什麼（白話）：以 feature_values 既有面板，跑 core_gate.build_universe（pan-historical 單名單、含
look-ahead）與（可選）build_universe_asof（逐 as-of 面板 point-in-time、消 survivorship #8）→ 寫 core_universe /
core_universe_asof。可選流動性分位 gate（--liquidity-pct、動態相對 #9）與月營收對金融保險之 conditional 豁免
（--exempt-revenue-financial：金融業無月營收申報制度、靠財報、不因此誤排）。純 DB 計算、不放 API、可逆。

B1（2026-08-05）：`--asof --incremental --asof-date D` 只 upsert 單日 asof（禁全表 DELETE）；
`--asof`／`--asof --full-rebuild`＝既有全量重灌。日更偏好 incremental（見 runbook）。

組合根：把 universe 層接上薄 CLI；核心股判準（地板/conditional）屬決策層，CLI 只暴露參數、不寫死判準（#9/#20）。

守 #1（只收 source-pure 完整股）· #8（asof 消 survivorship）· #10（純完整度、不評分排名）· #18（命名/標頭慣例）。

執行指令矩陣:
  python scripts/build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof
  python scripts/build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial \\
      --asof --incremental --asof-date 2026-08-04
  python scripts/build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial \\
      --asof --incremental --asof-date 2026-08-04 --asof-compare-only
  python -m augur.universe.core_gate --selftest
"""
from __future__ import annotations

import argparse
from datetime import date

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
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


def _diff(a, b):
    sa, sb = set(a), set(b)
    return sorted(sa - sb), sorted(sb - sa)


def main():
    ap = argparse.ArgumentParser(description="build core_universe（純完整度 gate）")
    ap.add_argument("--since", help="面板起始日 YYYY-MM-DD（預設全部既有面板）")
    ap.add_argument("--liquidity-pct", type=float, help="流動性下界百分位 0-100（動態相對、#9）")
    ap.add_argument("--exempt-revenue-financial", action="store_true", help="月營收對金融保險豁免完整度要求")
    ap.add_argument("--asof", action="store_true", help="同時建／更新 core_universe_asof（point-in-time）")
    ap.add_argument("--incremental", action="store_true",
                    help="B1a：只 upsert --asof-date（禁全表 DELETE；須既有 asof 史）")
    ap.add_argument("--full-rebuild", action="store_true",
                    help="B1c：明示全量 DELETE 再灌（與裸 --asof 相同；與 --incremental 互斥）")
    ap.add_argument("--asof-date", help="incremental 目標日 YYYY-MM-DD")
    ap.add_argument("--asof-compare-only", action="store_true",
                    help="對照臂：只比較「公式＠D」vs「表＠D」差分，不寫庫（須 --asof --asof-date）")
    ap.add_argument("--skip-pan-hist", action="store_true",
                    help="略過 pan-historical core_universe（日更僅動 asof 時用）")
    args = ap.parse_args()

    asof_date = date.fromisoformat(args.asof_date) if args.asof_date else None
    if args.asof_compare_only:
        if not args.asof or asof_date is None:
            raise SystemExit("--asof-compare-only 須 --asof 與 --asof-date")
    else:
        err = core_gate.validate_asof_cli_flags(
            asof=args.asof, incremental=args.incremental, full_rebuild=args.full_rebuild,
            asof_date=args.asof_date)
        if err:
            raise SystemExit(err)

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            pds = _panel_dates(cur, args.since)
        if not pds:
            print("無面板（feature_values 空）")
            return
        cond = {"monthly_revenue_yoy": FINANCIAL_INDUSTRIES} if args.exempt_revenue_financial else None
        print(f"build core_universe：{len(pds)} 面板（{pds[0]}..{pds[-1]}）"
              f" liquidity_pct={args.liquidity_pct} 月營收豁免金融={bool(cond)}")

        if args.asof_compare_only:
            formula = core_gate.compute_core_at_asof(
                conn, pds, asof_date, liquidity_pct=args.liquidity_pct, conditional=cond)
            stored = core_gate.read_core_at_asof(conn, asof_date)
            only_f, only_s = _diff(formula["stock_ids"], stored)
            print(f"  對照＠{asof_date}: 公式={formula['core'] if 'core' in formula else len(formula['stock_ids'])} "
                  f"表={len(stored)} 只在公式={len(only_f)} 只在表={len(only_s)}")
            if only_f[:5] or only_s[:5]:
                print(f"    sample 只在公式={only_f[:5]} 只在表={only_s[:5]}")
            print("  對照結果:" + ("差分∅ PASS" if not only_f and not only_s else "差分非空 FAIL"))
            raise SystemExit(0 if not only_f and not only_s else 2)

        if not args.skip_pan_hist:
            res = core_gate.build_universe(conn, pds, liquidity_pct=args.liquidity_pct, conditional=cond)
            msg = f"  pan-historical 核心：{res['core']} 股 / {res['canonical_features']} 特徵"
            if args.liquidity_pct is not None:
                msg += f" / 流動性閾值 {res.get('liquidity_threshold')}"
            print(msg)
        else:
            print("  pan-historical：跳過（--skip-pan-hist）")

        if args.asof:
            if args.incremental:
                before = core_gate.read_core_at_asof(conn, asof_date)
                formula = core_gate.compute_core_at_asof(
                    conn, pds, asof_date, liquidity_pct=args.liquidity_pct, conditional=cond)
                only_f, only_s = _diff(formula["stock_ids"], before)
                print(f"  增量前對照＠{asof_date}: 公式={len(formula['stock_ids'])} 表={len(before)} "
                      f"差公式={len(only_f)} 差表={len(only_s)}")
                out = core_gate.build_universe_asof_incremental(
                    conn, pds, asof_date, liquidity_pct=args.liquidity_pct, conditional=cond)
                after = core_gate.read_core_at_asof(conn, asof_date)
                d1, d2 = _diff(formula["stock_ids"], after)
                print(f"  as-of incremental＠{asof_date}: 寫入 {out['core']} 股 "
                      f"(panels≤D={out['panels']}, feats={out['canonical_features']})")
                print(f"  增量後對照: 差分∅={'PASS' if not d1 and not d2 else 'FAIL'} "
                      f"(只公式={len(d1)} 只表={len(d2)})")
                if d1 or d2:
                    raise SystemExit(2)
            else:
                # full rebuild（裸 --asof 或 --full-rebuild）
                tag = "full-rebuild" if args.full_rebuild else "asof(全量)"
                summ = core_gate.build_universe_asof(
                    conn, pds, liquidity_pct=args.liquidity_pct, conditional=cond)
                vals = list(summ.values())
                print(f"  as-of {tag}：{len(summ)} 面板，核心數 {min(vals)}..{max(vals)}（早→晚）")


if __name__ == "__main__":
    main()
