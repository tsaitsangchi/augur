#!/usr/bin/env python
"""PME MAP-E012 S2 — 庫內可建基本面特徵寫入 feature_values（零市場 API）。

🎯 這支在做什麼（白話）：僅對 S0 標 db_buildable 之 `roe`／`debt_ratio`，在既有 panel
   上算值寫入 feature_values（ON CONFLICT 更新）。peg／F-Score／macro_regime **不建**。
   算不出→缺列（#1）。不放 FinMind／FRED。

守 #1 #8 #29；MAP §3 S2／§6 A3；FZ-keep。

執行指令矩陣:
  python scripts/build_pme_fundamental_features.py --selftest
  python scripts/build_pme_fundamental_features.py --dry-run --asof --since 2021-01-01
  python scripts/build_pme_fundamental_features.py --run --asof --since 2021-01-01
  python scripts/build_pme_fundamental_features.py --run --asof --panels 2026-06-30
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from augur.features.fundamentals import compute_fundamental_features, _selftest as _fund_selftest


def _selftest() -> int:
    rc = _fund_selftest()
    print("script 層: 僅允許 roe／debt_ratio")
    return rc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MAP-E012 S2 建 roe／debt_ratio")
    ap.add_argument("--run", action="store_true", help="寫入 feature_values")
    ap.add_argument("--dry-run", action="store_true", help="只算不寫")
    ap.add_argument("--since", default=None, help="panel_date ≥")
    ap.add_argument("--panels", default=None, help="逗號分隔 panel 日")
    ap.add_argument("--asof", action="store_true", help="限 core_universe_asof")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.run and not args.dry_run:
        print(__doc__)
        print("需 --run 或 --dry-run（或 --selftest）")
        return 0

    from psycopg2.extras import execute_values

    from augur.core import db
    from augur.features.panel import FEATURE_TABLE

    if not db.ping():
        print("SKIP: DB 不可達", file=sys.stderr)
        return 2

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            if args.panels:
                pds = sorted(p.strip() for p in args.panels.split(","))
            else:
                sql = "SELECT DISTINCT panel_date FROM feature_values"
                params: tuple = ()
                if args.since:
                    sql += " WHERE panel_date >= %s"
                    params = (args.since,)
                cur.execute(sql + " ORDER BY panel_date", params)
                pds = [r[0] for r in cur.fetchall()]
            if args.asof:
                cur.execute("SELECT DISTINCT stock_id FROM core_universe_asof ORDER BY stock_id")
            else:
                cur.execute('SELECT DISTINCT stock_id FROM "TaiwanStockInfo" ORDER BY stock_id')
            roster = [r[0] for r in cur.fetchall()]

        print(f"S2 fundamentals: {len(pds)} panels × {len(roster)} stocks；write={args.run}")
        n_roe = n_debt = n_rows = 0
        for pd_ in pds:
            batch = []
            with db.transaction(conn) as cur:
                for sid in roster:
                    feats = compute_fundamental_features(cur, sid, pd_)
                    if "roe" in feats:
                        n_roe += 1
                        batch.append((pd_, sid, "roe", feats["roe"]))
                    if "debt_ratio" in feats:
                        n_debt += 1
                        batch.append((pd_, sid, "debt_ratio", feats["debt_ratio"]))
            if args.run and batch:
                with db.transaction(conn) as cur:
                    execute_values(
                        cur,
                        f"INSERT INTO {FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                        f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value = EXCLUDED.value",
                        batch,
                    )
                n_rows += len(batch)
            print(f"  {pd_}: batch={len(batch)} (cum roe_cells={n_roe} debt_cells={n_debt})")
        print(
            f"完成: roe_cells={n_roe} debt_cells={n_debt} "
            f"written_rows={n_rows if args.run else 0} dry={args.dry_run}"
        )
        print("未建: peg_ratio／piotroski_fscore／macro_regime（deferred／FZ）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
