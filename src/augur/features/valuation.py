"""augur 估值特徵 — PER/PBR/殖利率/市值（F2c、第一性軸④ 價格-價值缺口）。

🎯 這支在做什麼（白話）：給 as-of 面板日 t + 一個 stock_id，query 估值表算 5 個估值面特徵：
本益比、淨值比、殖利率、市值規模、（可選）價格相對 10 年線位置。as-of ≤t 最近一筆。

對應 F2 roadmap F2c 期、第一性計畫軸④（估值水位）：
- f1 pe_ratio：本益比 PER（估值水位、raw 值；樹自學分界、不硬編「便宜」閾值 #9）
- f2 pb_ratio：淨值比 PBR
- f3 dividend_yield：殖利率（%）
- f4 market_cap_log：log(市值)（size 規模因子；log 壓縮量綱）
- f5 price_to_10yr：原始收盤 / 10 年線 − 1（超長期均值回歸位置；需 TaiwanStockPrice + 10Year，缺則略；
  #8：用原始收盤而非前向還原 PriceAdj，避免未來股利/分割因子回溯注入歷史價之偷看）

**無 P-lag 風險**（別於財報三表 #8）：PER/PBR/殖利率/市值皆交易所**每日公布**（基於最近財報 EPS + 當日價）→
date ≤ panel_date 即 as-of 安全。**#9**：估值 raw 值入 feature（不設「PER<15 便宜」硬閾值，相對化交給樹/橫斷面）。
**#1**：算不出（無資料 / PER≤0 虧損 / 市值≤0）→ 不含該 key（缺列、不存 fake）。

守 #1（算不出即缺列）· #8（as-of ≤t、無 P-lag）· #9（估值不硬編閾值）· #5（numeric）· F2 roadmap F2c。
"""
from __future__ import annotations

import numpy as np

_PER_SQL = (
    'SELECT "PER"::float8, "PBR"::float8, dividend_yield::float8 '
    'FROM "TaiwanStockPER" WHERE stock_id=%s AND date <= %s ORDER BY date DESC LIMIT 1'
)
_MV_SQL = (
    'SELECT market_value::float8 FROM "TaiwanStockMarketValue" '
    'WHERE stock_id=%s AND date <= %s ORDER BY date DESC LIMIT 1'
)
_TENYR_SQL = (
    'SELECT close::float8 FROM "TaiwanStock10Year" WHERE stock_id=%s AND date <= %s ORDER BY date DESC LIMIT 1'
)
_RAW_CLOSE_SQL = (   # #8 修正(2026-07-10 審計):原讀 TaiwanStockPriceAdj——前向還原把「未來」股利/分割因子
    # 回溯注入歷史價(adj/raw 比值隨錨點日漂移)=偷看未來;改讀原始 TaiwanStockPrice,與 raw-basis 之
    # TaiwanStock10Year 同 point-in-time 口徑(消除 restatement 洩漏並修正混口徑)。
    'SELECT close::float8 FROM "TaiwanStockPrice" WHERE stock_id=%s AND date <= %s ORDER BY date DESC LIMIT 1'
)


def compute_valuation_features(cur, sid, panel_date):
    """對 sid + panel_date 算估值 features → {feature: value}；算不出 → 不含該 key（缺列、#1）。"""
    out = {}

    # f1-f3 PER/PBR/殖利率（同一表最近一筆）
    cur.execute(_PER_SQL, (sid, panel_date))
    row = cur.fetchone()
    if row:
        per, pbr, dy = row
        if per is not None and per > 0 and np.isfinite(per):          # 本益比>0（虧損股 PER 負/無意義→缺）
            out["pe_ratio"] = float(per)
        if pbr is not None and pbr > 0 and np.isfinite(pbr):
            out["pb_ratio"] = float(pbr)
        if dy is not None and dy >= 0 and np.isfinite(dy):            # 殖利率≥0（0=不配息、真值）
            out["dividend_yield"] = float(dy)

    # f4 市值 log（size 因子）
    cur.execute(_MV_SQL, (sid, panel_date))
    row = cur.fetchone()
    if row and row[0] is not None and row[0] > 0:
        v = float(np.log(row[0]))
        if np.isfinite(v):
            out["market_cap_log"] = v

    # f5 還原收盤 / 10 年線 − 1（超長期均值回歸位置；10Year 2011 起、缺則略）
    cur.execute(_TENYR_SQL, (sid, panel_date))
    tr = cur.fetchone()
    if tr and tr[0] is not None and tr[0] > 0:
        cur.execute(_RAW_CLOSE_SQL, (sid, panel_date))
        cr = cur.fetchone()
        if cr and cr[0] is not None and cr[0] > 0:
            v = float(cr[0] / tr[0] - 1.0)
            if np.isfinite(v):
                out["price_to_10yr"] = v

    return out
