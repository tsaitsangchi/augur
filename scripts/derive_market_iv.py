#!/usr/bin/env python
"""台指隱含波動推導 — TaiwanOptionDaily(TXO)→ 近月平價 IV 日序列(oracle 主計畫 §4.4;本地零新源)。

🎯 這支在做什麼(白話):用在庫 TXO 選擇權日資料本地推導「台版 VIX 替身」——每交易日:
   ①取最近未到期契約月(結算=該月第三個星期三);②ATM 定位=|call−put| 收盤價差最小之履約價
   (put-call parity,免精確現貨);③IV 以 Brenner-Subrahmanyam 平價近似 σ≈(C+P)/(2·0.398·K·√T)
   ——**明標近似口徑**(v1 特徵用途;非交易級定價)。落 market_iv_daily(自建表,冪等 DELETE+INSERT/日)。
   #8:同源 t 收盤資料,visible=t(lag 0);trading_session='position' 日盤限定(夜盤排除 §3.3)。

守 #8(t 收盤可見)· #9(全出 DB 實算)· #10(近似口徑明標)· #28(本地零 API)· #29a。

執行指令矩陣:
  python scripts/derive_market_iv.py                    # 無參數:現況(唯讀)
  python scripts/derive_market_iv.py --run              # 全期推導(2002+,冪等)
  python scripts/derive_market_iv.py --run --since 2020-01-01   # 增量段
"""
import argparse
import math
import sys
from datetime import date, timedelta

import _bootstrap  # noqa: F401
from augur.core import db

BS_CONST = 0.398   # Brenner-Subrahmanyam:ATM 選擇權價 ≈ 0.398·S·σ·√T(近似口徑,明標)

DDL = """
CREATE TABLE IF NOT EXISTS market_iv_daily (
  panel_date date PRIMARY KEY,
  iv double precision NOT NULL CHECK (iv > 0 AND iv < 5),
  atm_strike double precision NOT NULL,
  contract_date text NOT NULL,
  t_years double precision NOT NULL,
  n_quotes int NOT NULL,
  method text NOT NULL DEFAULT 'brenner_subrahmanyam_atm',
  created_at timestamptz NOT NULL DEFAULT now());
COMMENT ON TABLE market_iv_daily IS
  'TXO 近月平價隱含波動(本地推導,零新源;Brenner-Subrahmanyam 近似口徑明標;v1 特徵用途非定價;oracle 主計畫 §4.4)';
"""


def _third_wednesday(yyyymm):
    y, m = int(yyyymm[:4]), int(yyyymm[4:6])
    d = date(y, m, 1)
    wed = [d + timedelta(days=i) for i in range(31)
           if (d + timedelta(days=i)).month == m and (d + timedelta(days=i)).weekday() == 2]
    return wed[2]


def run(since):
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(DDL)
        conn.commit()
        cur.execute("""SELECT date, contract_date, strike_price::float8, call_put, close::float8
                       FROM "TaiwanOptionDaily"
                       WHERE option_id='TXO' AND trading_session='position' AND close > 0
                         AND date >= %s AND date <= '2026-05-31'
                       ORDER BY date""", (since,))
        rows = cur.fetchall()
    by_day = {}
    for d, cm, k, cp, px in rows:
        by_day.setdefault(d, {}).setdefault(cm, {}).setdefault(k, {})[cp] = px
    out = []
    for d in sorted(by_day):
        # 近月=結算日 > d 之最小契約月(純數字月份;排除週別如 202601W1)
        cms = [cm for cm in by_day[d] if cm.isdigit() and len(cm) == 6 and _third_wednesday(cm) > d]
        if not cms:
            continue
        cm = min(cms)
        chain = by_day[d][cm]
        pairs = [(k, v["call"], v["put"]) for k, v in chain.items() if "call" in v and "put" in v]
        if len(pairs) < 3:
            continue
        k_atm, c, p = min(pairs, key=lambda x: abs(x[1] - x[2]))     # parity ATM 定位
        t = max(( _third_wednesday(cm) - d).days, 1) / 365.0
        iv = (c + p) / (2 * BS_CONST * k_atm * math.sqrt(t))
        if not (0 < iv < 5):
            continue
        out.append((d, iv, k_atm, cm, t, len(pairs)))
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM market_iv_daily WHERE panel_date >= %s", (since,))
        cur.executemany("INSERT INTO market_iv_daily (panel_date, iv, atm_strike, contract_date, t_years, n_quotes) "
                        "VALUES (%s,%s,%s,%s,%s,%s)", out)
        conn.commit()
    print(f"✓ 推導 {len(out)} 交易日(since {since});近似口徑=Brenner-Subrahmanyam ATM")
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--since", default="2002-01-01")
    args = ap.parse_args()
    if args.run:
        return run(args.since)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.market_iv_daily')")
        if cur.fetchone()[0]:
            cur.execute("SELECT count(*), min(panel_date), max(panel_date), round(avg(iv)::numeric,4) FROM market_iv_daily")
            print("現況:", cur.fetchone())
        else:
            print("現況:(表未建,--run 會自建)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
