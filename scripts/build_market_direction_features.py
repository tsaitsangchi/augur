#!/usr/bin/env python
"""市場方向特徵 — 在庫市場表 → market_direction_feature 日面板(oracle 主計畫 §3.3/§4;#8 visible_date 逐欄)。

🎯 這支在做什麼(白話):H 軌市場分量的特徵層——每交易日一組市場級特徵,**逐欄帶 visible_date**
   (#8:盤後公布類 lag 1 交易日;t 收盤即定類 lag 0;VIX 走 macro_vintage PIT reader=首個真消費者)。
   v1 特徵集(全在庫零新源,#9 溯源 source_table 欄):
   TRI(TAIEX):ret_1/5/20/60、vol_20、dist_high_60(lag0)|market_iv_daily:iv、iv_chg_5(lag0)|
   三大法人合計淨買(lag1)|融資餘額 5 日變動(lag1)|大盤融資維持率(lag1)|
   期貨外資淨 OI(2018+,晚生誠實 NULL)(lag1)|FearGreed(美國曆→台北 lag1)|VIXCLS(macro_vintage PIT)。
   冪等:逐日 DELETE+INSERT。訓練端只用 visible_date<=panel 之列(builder 落格,#8 消費端強制)。

守 #8(visible_date 逐欄)· #9/#10(source_table 溯源)· #28(本地零 API)· #29a。

執行指令矩陣:
  python scripts/build_market_direction_features.py                     # 無參數:現況(唯讀)
  python scripts/build_market_direction_features.py --run               # 全期(2008-12-31~FREEZE)
  python scripts/build_market_direction_features.py --run --since 2025-01-01   # 增量段
"""
import argparse
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np

from augur.core import db
from augur.features import macro_vintage

START, FREEZE = "2008-12-31", "2026-05-31"


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _series(cur, sql, args=()):
    cur.execute(sql, args)
    return dict(cur.fetchall())


def run(since):
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        # 交易日曆=TAIEX TRI 日期(≥START)
        cur.execute('SELECT date, price::float8 FROM "TaiwanStockTotalReturnIndex" '
                    "WHERE stock_id='TAIEX' AND date <= %s ORDER BY date", (FREEZE,))
        tri = cur.fetchall()
        cal = [d for d, _ in tri]
        px = {d: p for d, p in tri}
        idx = {d: i for i, d in enumerate(cal)}
        iv = _series(cur, "SELECT panel_date, iv FROM market_iv_daily WHERE panel_date <= %s", (FREEZE,))
        cur.execute('SELECT date, sum(buy::float8 - sell::float8) FROM "TaiwanStockTotalInstitutionalInvestors" '
                    "WHERE date <= %s GROUP BY date", (FREEZE,))
        inst = dict(cur.fetchall())
        cur.execute('SELECT date, sum("TodayBalance"::float8) FROM "TaiwanStockTotalMarginPurchaseShortSale" '
                    "WHERE name LIKE %s AND date <= %s GROUP BY date", ("Margin%", FREEZE))
        marg = dict(cur.fetchall())
        mm = _series(cur, 'SELECT date, "TotalExchangeMarginMaintenance"::float8 '
                          'FROM "TaiwanTotalExchangeMarginMaintenance" WHERE date <= %s', (FREEZE,))
        cur.execute('SELECT date, sum(long_open_interest_balance_volume::float8 - 0) '
                    'FROM "TaiwanFuturesInstitutionalInvestors" '
                    "WHERE futures_id='TX' AND institutional_investors LIKE %s AND date <= %s GROUP BY date",
                    ("%外資%", FREEZE))
        futoi = dict(cur.fetchall())
        fg = _series(cur, 'SELECT date, fear_greed::float8 FROM "CnnFearGreedIndex" WHERE date <= %s', (FREEZE,))

        rows = []
        for d in cal:
            if str(d) < since or str(d) < START:
                continue
            i = idx[d]
            f = {}
            if i >= 60:
                f["mkt_ret_1"] = (px[d] / px[cal[i - 1]] - 1, "TaiwanStockTotalReturnIndex", d)
                f["mkt_ret_5"] = (px[d] / px[cal[i - 5]] - 1, "TaiwanStockTotalReturnIndex", d)
                f["mkt_ret_20"] = (px[d] / px[cal[i - 20]] - 1, "TaiwanStockTotalReturnIndex", d)
                f["mkt_ret_60"] = (px[d] / px[cal[i - 60]] - 1, "TaiwanStockTotalReturnIndex", d)
                rets = [px[cal[j]] / px[cal[j - 1]] - 1 for j in range(i - 19, i + 1)]
                f["mkt_vol_20"] = (float(np.std(rets)), "TaiwanStockTotalReturnIndex", d)
                hi60 = max(px[cal[j]] for j in range(i - 59, i + 1))
                f["mkt_dist_high_60"] = (px[d] / hi60 - 1, "TaiwanStockTotalReturnIndex", d)
            if d in iv:
                f["mkt_iv"] = (float(iv[d]), "market_iv_daily", d)
                if i >= 5 and cal[i - 5] in iv:
                    f["mkt_iv_chg_5"] = (float(iv[d]) - float(iv[cal[i - 5]]), "market_iv_daily", d)
            nx = cal[i + 1] if i + 1 < len(cal) else d + timedelta(days=1)   # lag1 → 次一交易日可見
            if d in inst:
                f["inst_net_total"] = (inst[d], "TaiwanStockTotalInstitutionalInvestors", nx)
            if d in marg and i >= 5 and cal[i - 5] in marg and marg[cal[i - 5]]:
                f["margin_bal_chg_5"] = (marg[d] / marg[cal[i - 5]] - 1, "TaiwanStockTotalMarginPurchaseShortSale", nx)
            if d in mm:
                f["margin_maintenance"] = (mm[d], "TaiwanTotalExchangeMarginMaintenance", nx)
            if d in futoi:      # 2018-06 起;晚生誠實缺列(不補 0)
                f["fut_foreign_oi"] = (futoi[d], "TaiwanFuturesInstitutionalInvestors", nx)
            if d in fg:         # 美國曆 → 台北 lag1
                f["fear_greed"] = (fg[d], "CnnFearGreedIndex", nx)
            vix = macro_vintage.as_of(cur, "VIXCLS", d)          # PIT 直讀 realtime_start(首個真消費者)
            if vix:
                f["vixcls"] = (vix[0], "fred_series", d)
            for name, (val, src, vis) in f.items():
                if val is not None and np.isfinite(val):
                    rows.append((d, name, float(val), src, vis, git7))
        cur.execute("DELETE FROM market_direction_feature WHERE panel_date >= %s", (since,))
        cur.executemany("INSERT INTO market_direction_feature (panel_date, feature, value, source_table, "
                        "visible_date, git_sha) VALUES (%s,%s,%s,%s,%s,%s)", rows)
        conn.commit()
    print(f"✓ 市場特徵 {len(rows)} 列(since {since};#8 visible_date 逐欄;VIX=macro_vintage PIT)")
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--since", default=START)
    args = ap.parse_args()
    if args.run:
        return run(args.since)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*), count(DISTINCT panel_date), count(DISTINCT feature) FROM market_direction_feature")
        print("現況(rows, days, features):", cur.fetchone())
    return 0


if __name__ == "__main__":
    sys.exit(main())
