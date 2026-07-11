#!/usr/bin/env python
"""D 軌日頻特徵 — 個股每交易日方向特徵 → daily_direction_feature_values(oracle 主計畫 §3.3;#8 逐欄可見)。

🎯 這支在做什麼(白話):D 軌(逐日方向)的特徵層——核心宇宙每檔股每交易日一組特徵。v1 特徵集(全在庫零新源):
   個股價量(TaiwanStockPriceAdj,t 收盤即定 **lag 0**):d_ret_1/5/20(動能)、d_vol_20(波動)、d_dist_ma20
   (乖離)、d_hilo_20(20 日區間位置)、d_turnover_z(量能 z);市場 context(panel 級、全股同值):
   m_iv(market_iv_daily,lag 0)、m_taiex_ret5(TAIEX 5 日動能,lag 0)。宇宙=core_universe_asof 之 **PIT
   成分**(每 panel 取最近 as_of≤panel 快照,#8 無倖存者偏誤)。籌碼(法人/融資,lag 1)列 v2 擴充、不入 v1。
   冪等:逐日期段 DELETE+INSERT。向量化 pandas(~95 萬列、本地零 API)。resume:--since 增量段。

守 #8(價量 lag 0=t 收盤已知;宇宙 PIT 成分;市場 context lag 0)· #9(來源在庫可溯)· #28(本地零 usage)· #29a/d。
   前置=core_universe_asof(宇宙)+market_iv_daily(IV)+TaiwanStockTotalReturnIndex(TAIEX)。SSOT=oracle 主計畫 §3.3。

執行指令矩陣:
  python scripts/build_daily_direction_features.py                    # 無參數:現況(唯讀:已建覆蓋)
  python scripts/build_daily_direction_features.py --run              # 全期(宇宙最早 as_of ~ FREEZE)
  python scripts/build_daily_direction_features.py --run --since 2020-01-01   # 增量段
  python scripts/build_daily_direction_features.py --run --stocks 20         # 小樣測試(前 20 檔,#25)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd
from augur.core import db

START, FREEZE = "2015-01-01", "2026-05-31"
FEATS = ["d_ret_1", "d_ret_5", "d_ret_20", "d_vol_20", "d_dist_ma20", "d_hilo_20", "d_turnover_z",
         "m_iv", "m_taiex_ret5"]


def _universe_pit(cur):
    """core_universe_asof → {as_of_date: set(stock_id)},升冪(供逐 panel 取最近≤panel 之 PIT 成分)。"""
    cur.execute("SELECT as_of_date, stock_id FROM core_universe_asof ORDER BY as_of_date")
    snaps = {}
    for a, s in cur.fetchall():
        snaps.setdefault(a, set()).add(s)
    return sorted(snaps.items())


def _market_context(cur):
    """market_iv_daily.iv + TAIEX 5 日動能,逐交易日一列(全股同值)。回 DataFrame[date, m_iv, m_taiex_ret5]。"""
    cur.execute("SELECT panel_date, iv FROM market_iv_daily ORDER BY panel_date")
    iv = pd.DataFrame(cur.fetchall(), columns=["date", "m_iv"])
    cur.execute("SELECT date, price FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX' ORDER BY date")
    tri = pd.DataFrame(cur.fetchall(), columns=["date", "px"])
    tri["px"] = tri["px"].astype(float)
    tri["m_taiex_ret5"] = tri["px"].pct_change(5)
    ctx = iv.merge(tri[["date", "m_taiex_ret5"]], on="date", how="outer").sort_values("date")
    ctx["m_iv"] = ctx["m_iv"].astype(float)
    return ctx


def run(since, n_stocks):
    since = since or START
    with db.connect() as conn:
        cur = conn.cursor()
        snaps = _universe_pit(cur)
        all_stocks = sorted({s for _, ss in snaps for s in ss})
        if n_stocks:
            all_stocks = all_stocks[:n_stocks]
        print(f"宇宙:{len(all_stocks)} 檔(PIT 成分,{len(snaps)} 快照);建置段 since={since}")
        ctx = _market_context(cur)

        # 價量:多拉 60 td 緩衝(trailing 窗)後於 since 起算特徵
        cur.execute("""SELECT stock_id, date, close, "Trading_money" FROM "TaiwanStockPriceAdj"
            WHERE stock_id = ANY(%s) AND date >= %s AND date <= %s ORDER BY stock_id, date""",
            (all_stocks, str(pd.Timestamp(since) - pd.Timedelta(days=120)).split()[0], FREEZE))
        px = pd.DataFrame(cur.fetchall(), columns=["stock_id", "date", "close", "money"])
        if px.empty:
            print("✗ 無價量資料"); return 1
        px["close"] = px["close"].astype(float)
        px["money"] = px["money"].astype(float)
        px = px.sort_values(["stock_id", "date"])
        g = px.groupby("stock_id", group_keys=False)
        px["d_ret_1"] = g["close"].pct_change(1)
        px["d_ret_5"] = g["close"].pct_change(5)
        px["d_ret_20"] = g["close"].pct_change(20)
        px["d_vol_20"] = g["d_ret_1"].transform(lambda s: s.rolling(20).std())
        px["ma20"] = g["close"].transform(lambda s: s.rolling(20).mean())
        px["d_dist_ma20"] = px["close"] / px["ma20"] - 1
        mn = g["close"].transform(lambda s: s.rolling(20).min())
        mx = g["close"].transform(lambda s: s.rolling(20).max())
        px["d_hilo_20"] = np.where(mx > mn, (px["close"] - mn) / (mx - mn), 0.5)
        m_mean = g["money"].transform(lambda s: s.rolling(60).mean())
        m_std = g["money"].transform(lambda s: s.rolling(60).std())
        px["d_turnover_z"] = np.where(m_std > 0, (px["money"] - m_mean) / m_std, 0.0)

        px = px.merge(ctx, on="date", how="left")
        px = px[px["date"] >= pd.Timestamp(since).date()].copy()

        # PIT 宇宙成分濾:每列 date 取最近 as_of≤date 之成分集(向量化:snap_idx + 允許 (idx,stock) 集)
        snap_dates = np.array([a for a, _ in snaps])
        allowed = {(si, st) for si, (_, ss) in enumerate(snaps) for st in ss}
        snap_idx = np.searchsorted(snap_dates, px["date"].to_numpy(), side="right") - 1
        keep = [(si >= 0 and (si, st) in allowed) for si, st in zip(snap_idx, px["stock_id"])]
        px = px[keep]

        # 落地:long 格式 (panel_date, target_id, feature, value)
        long = px.melt(id_vars=["date", "stock_id"], value_vars=FEATS, var_name="feature", value_name="value")
        long = long[long["value"].notna() & np.isfinite(long["value"])]
        rows = list(long.itertuples(index=False, name=None))
        cur.execute("DELETE FROM daily_direction_feature_values WHERE panel_date >= %s", (pd.Timestamp(since).date(),))
        from psycopg2.extras import execute_values
        execute_values(cur, "INSERT INTO daily_direction_feature_values (panel_date, target_id, feature, value) "
                            "VALUES %s", [(d, s, f, float(v)) for d, s, f, v in rows], page_size=10000)
        conn.commit()
        print(f"✓ D 軌特徵 {len(rows)} 列({px['date'].nunique()} 交易日 × {px['stock_id'].nunique()} 檔 × {len(FEATS)} 特徵)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*), count(DISTINCT panel_date), count(DISTINCT target_id), count(DISTINCT feature), "
                    "min(panel_date), max(panel_date) FROM daily_direction_feature_values")
        r = cur.fetchone()
    print(f"daily_direction_feature_values:{r[0]} 列 / {r[1]} 交易日 / {r[2]} 檔 / {r[3]} 特徵 ({r[4]}~{r[5]})")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--since")
    ap.add_argument("--stocks", type=int)
    args = ap.parse_args()
    if args.run:
        return run(args.since, args.stocks)
    return status()


if __name__ == "__main__":
    sys.exit(main())
