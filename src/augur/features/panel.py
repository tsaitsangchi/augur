"""augur 特徵面板 — 從 source-pure raw 算每股每面板之特徵（嚴格 source-pure）。

這支在做什麼（白話）：給一個 as-of 面板日期 + 一批股，對每股拉它 ≤ 該日的價量序列
（`TaiwanStockPrice`），算成一組數值特徵（報酬 / 動能 / 波動 / 流動性 / 位置）存進 `feature_values`。

嚴格 source-pure（#1）：特徵一律「真實 API 價量值經數學轉換（log/ratio/rolling）」；**算不出**
（歷史不足 / 除零 / NaN / inf）→ **不寫該列（缺列），不存 fake / 不存 zero-fill**。完整度交 universe 層判定。
思想≠特定值（#9）：純 log/ratio/std/mean，視窗用 5/20/60/120/252 calendar 慣例（Tier 0-1）；**無 hardcoded
知識字典 / 特定閾值**（無 Pareto 0.80、無 K-wave 40-60、無 theme keyword）。
anti-leakage（#8）：面板日 t 之特徵只用價量 ≤ t（純後向 rolling）；label（未來報酬）**不在此層**。

邊界：只算特徵（不抓 API、不選股）；自建 `feature_values` 表（自建 DDL，CREATE IF NOT EXISTS）。

守 #1（算不出即缺列、不存無源值）· #9（無 hardcoded 特定值）· #8（as-of ≤t 後向）· #5（NUMERIC 型別）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from psycopg2.extras import execute_values

from augur.core import db

FEATURE_TABLE = "feature_values"
DDL = f"""
CREATE TABLE IF NOT EXISTS {FEATURE_TABLE} (
    panel_date  DATE NOT NULL,
    stock_id    VARCHAR(255) NOT NULL,
    feature     VARCHAR(255) NOT NULL,
    value       NUMERIC(20,6) NOT NULL,
    PRIMARY KEY (panel_date, stock_id, feature)
)"""

_PRICE_SQL = (
    'SELECT date, close, "Trading_Volume" AS volume, "Trading_money" AS money, '
    '"Trading_turnover" AS turnover, "max" AS high, "min" AS low '
    'FROM "TaiwanStockPrice" WHERE stock_id = %s AND date <= %s ORDER BY date'
)
# 基本面 D:月營收 YoY(log)——最近月 vs 12 個月前;算不出(無歷史 / revenue≤0 / 缺 -12 月那筆)→ 缺列(#1)
_REVENUE_SQL = (
    'SELECT date, revenue FROM "TaiwanStockMonthRevenue" '
    'WHERE stock_id = %s AND date <= %s ORDER BY date DESC LIMIT 14'
)


def _compute_revenue_yoy(rev_rows):
    """月營收 YoY(log return,nat log)——最近月 vs 該月 -12 月之 revenue。逐筆對 (年-1, 同月) 回查。
    算不出(無資料/<13 筆/revenue<=0/查無 -12 月那筆)→ None(缺列、嚴格 source-pure)。"""
    if len(rev_rows) < 13:
        return None
    last_d, last_r = rev_rows[0]
    try:
        last_r = float(last_r) if last_r is not None else 0
    except (TypeError, ValueError):
        return None
    if last_r <= 0:
        return None
    target_year, target_month = last_d.year - 1, last_d.month
    for d, r in rev_rows[1:]:
        if d.year == target_year and d.month == target_month:
            try:
                r12 = float(r) if r is not None else 0
            except (TypeError, ValueError):
                return None
            if r12 > 0:
                v = float(np.log(last_r / r12))
                return v if np.isfinite(v) else None
            return None
    return None


def bootstrap(cur):
    """建 feature_values 表（自建 DDL，冪等）。"""
    cur.execute(DDL)


def compute_features(df):
    """df 已按 date 升序，欄：close/volume/money/turnover/high/low → {feature: value}（只含 finite）。

    嚴格 source-pure：算不出之特徵**不出現在回傳 dict**（→ 缺列）。全為純後向（as-of df 末列）。
    """
    c = df["close"].astype(float)
    n = len(c)
    out = {}
    # 無效價(0/負/停牌)致 log→nan/inf 屬預期 → 靜音 warning,最後 isfinite 濾掉(→缺列)
    with np.errstate(divide="ignore", invalid="ignore"):
        ret = np.log(c / c.shift(1))               # 每日 log 報酬
        if n >= 2:
            out["return_1d"] = ret.iloc[-1]
        for w in (5, 20, 60, 120, 252):            # 動能：跨 週/月/季/半年/年（calendar 慣例）
            if n > w:
                out[f"momentum_{w}d"] = np.log(c.iloc[-1] / c.iloc[-1 - w])
        for w in (20, 60):                         # 波動：日報酬 rolling std
            if ret.iloc[-w:].notna().sum() >= w:
                out[f"volatility_{w}d"] = ret.iloc[-w:].std()
        if n >= 20:                                # 流動性 / 區間
            out["dollar_volume_log_20d"] = np.log(df["money"].iloc[-20:].astype(float).mean())
            out["turnover_mean_20d"] = df["turnover"].iloc[-20:].astype(float).mean()
            out["range_mean_20d"] = ((df["high"] - df["low"]).astype(float) / c).iloc[-20:].mean()
        if n >= 252:                               # 年度位置
            hi, lo = c.iloc[-252:].max(), c.iloc[-252:].min()
            out["price_to_252d_high"] = c.iloc[-1] / hi
            if hi > lo:
                out["cycle_position_252d"] = (c.iloc[-1] - lo) / (hi - lo)
        if n >= 60:                                # 量能噴出
            v5, v60 = df["volume"].iloc[-5:].astype(float).mean(), df["volume"].iloc[-60:].astype(float).mean()
            if v60 > 0:
                out["volume_surge_5_60"] = v5 / v60
    return {k: float(v) for k, v in out.items() if v is not None and np.isfinite(v)}   # 缺列：去 NaN/inf


def build_panel(conn, panel_date, stock_ids, *, progress=None):
    """對 panel_date 之每股算特徵 → 存 feature_values（算不出之特徵缺列、整股無特徵則整股不出現）。"""
    with db.transaction(conn) as cur:
        bootstrap(cur)
    written = stocks = 0
    for i, sid in enumerate(stock_ids, 1):
        with db.transaction(conn) as cur:
            cur.execute(_PRICE_SQL, (sid, panel_date))
            rows = cur.fetchall()
            cur.execute(_REVENUE_SQL, (sid, panel_date))                 # D:月營收(部分股無 → 自然缺列)
            rev_rows = cur.fetchall()
        if not rows:
            continue
        df = pd.DataFrame(rows, columns=["date", "close", "volume", "money", "turnover", "high", "low"])
        feats = compute_features(df)
        rev_yoy = _compute_revenue_yoy(rev_rows)                        # D:加月營收 YoY(算不出→缺列,自然排除非營利股/新上市無歷史股)
        if rev_yoy is not None:
            feats["monthly_revenue_yoy"] = rev_yoy
        if not feats:
            continue
        data = [(panel_date, sid, f, v) for f, v in feats.items()]
        with db.transaction(conn) as cur:
            execute_values(
                cur,
                f"INSERT INTO {FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value = EXCLUDED.value",
                data)
        written += len(data)
        stocks += 1
        if progress and i % 200 == 0:
            progress(f"  feature panel {panel_date}: {i}/{len(stock_ids)} 股、{written} 值")
    return {"panel_date": str(panel_date), "stocks": stocks, "values": written}
