"""augur 核心股 raw 欄位相關性分析 — 每股各 raw 欄位兩兩相關係數（Pearson/Spearman × level/change）。

🎯 這支在做什麼（白話）：對每支股，把散在 ~12 張 raw 表的數值欄聚合成「每日對齊面板」（~22 欄：
價量/籌碼/估值/月營收），算欄位兩兩相關係數——**level**（原始水位）與 **change**（日一階差）兩 basis、
**Pearson** 與 **Spearman** 兩法——存進 `field_correlation` 表。供探索 raw 欄位間正/負相關、輔助特徵發現。

對齊：以 `TaiwanStockPriceAdj` 交易日為基準左併各源；月頻（月營收）as-of 前向填補；多列表（法人/大戶/官股）
先 GROUP BY date 聚合為每股每日標量。某欄某日無資料 → NaN → 該對相關以 pairwise 可用 obs 算（#1 不補值）。

邊界（audit 唯讀）：不改 raw、不選股、不入模。**探索性、非 as-of**：用全史探 raw 欄位關係；若日後用於
特徵須另過 #8 anti-leakage / #11 五鏡漏斗（本表非生產特徵）。

守 #1（真值、缺即 NaN 不補）· #5（NUMERIC）· #6（upsert 冪等）· #15（n_obs 揭露、相關無定義即不寫、不靜默）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from psycopg2.extras import execute_values

from augur.core import db

TABLE = "field_correlation"
MIN_OBS = 60   # 一對欄位至少 N 個共同非空 obs 才算相關（少於即不寫；operational、透明揭露 #15）

DDL = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    stock_id    VARCHAR(255) NOT NULL,
    field_a     VARCHAR(64)  NOT NULL,
    field_b     VARCHAR(64)  NOT NULL,
    method      VARCHAR(16)  NOT NULL,   -- pearson / spearman
    basis       VARCHAR(16)  NOT NULL,   -- level / change
    n_obs       INTEGER      NOT NULL,
    corr        NUMERIC(8,6) NOT NULL,   -- 相關係數 [-1,1]
    computed_at TIMESTAMP    NOT NULL DEFAULT now(),
    PRIMARY KEY (stock_id, field_a, field_b, method, basis)
)"""

# ── 欄位源（每項：欄名 → SQL 取 (date, 值...)；多列表已於 SQL GROUP BY 聚合）──
# 價量一次取多欄；其餘逐欄/逐源。皆 WHERE stock_id=%s。
_PRICE_SQL = ('SELECT date, close, "Trading_Volume" volume, "Trading_money" money, '
              '"Trading_turnover" turnover, "max" high, "min" low, spread '
              'FROM "TaiwanStockPriceAdj" WHERE stock_id=%s AND close>0 ORDER BY date')
# (欄位, SQL) — SQL 回 (date, value) 單值序列；多列表 GROUP BY date 聚合
_SRC = [
    ("inst_net",       'SELECT date, (sum(buy)-sum(sell))::float8 FROM "TaiwanStockInstitutionalInvestorsBuySell" WHERE stock_id=%s GROUP BY date'),
    ("inst_gross",     'SELECT date, (sum(buy)+sum(sell))::float8 FROM "TaiwanStockInstitutionalInvestorsBuySell" WHERE stock_id=%s GROUP BY date'),
    ("margin_balance", 'SELECT date, "MarginPurchaseTodayBalance"::float8 FROM "TaiwanStockMarginPurchaseShortSale" WHERE stock_id=%s'),
    ("margin_limit",   'SELECT date, "MarginPurchaseLimit"::float8 FROM "TaiwanStockMarginPurchaseShortSale" WHERE stock_id=%s'),
    ("foreign_holding",'SELECT date, "ForeignInvestmentSharesRatio"::float8 FROM "TaiwanStockShareholding" WHERE stock_id=%s'),
    ("top_holders",    "SELECT date, percent::float8 FROM \"TaiwanStockHoldingSharesPer\" WHERE stock_id=%s AND \"HoldingSharesLevel\"='more than 1,000,001'"),
    ("sbl_balance",    'SELECT date, "SBLShortSalesCurrentDayBalance"::float8 FROM "TaiwanDailyShortSaleBalances" WHERE stock_id=%s'),
    ("lending_fee",    'SELECT date, avg(fee_rate)::float8 FROM "TaiwanStockSecuritiesLending" WHERE stock_id=%s GROUP BY date'),
    ("govbank_net",    'SELECT date, (sum(buy_amount)-sum(sell_amount))::float8 FROM "TaiwanStockGovernmentBankBuySell" WHERE stock_id=%s GROUP BY date'),
    ("per",            'SELECT date, "PER"::float8 FROM "TaiwanStockPER" WHERE stock_id=%s'),
    ("pbr",            'SELECT date, "PBR"::float8 FROM "TaiwanStockPER" WHERE stock_id=%s'),
    ("dividend_yield", 'SELECT date, dividend_yield::float8 FROM "TaiwanStockPER" WHERE stock_id=%s'),
    ("market_value",   'SELECT date, market_value::float8 FROM "TaiwanStockMarketValue" WHERE stock_id=%s'),
    ("tenyr",          'SELECT date, close::float8 FROM "TaiwanStock10Year" WHERE stock_id=%s'),
    ("revenue",        'SELECT date, revenue::float8 FROM "TaiwanStockMonthRevenue" WHERE stock_id=%s'),   # 月頻 → ffill
]
_FFILL = {"revenue"}   # 月頻欄 as-of 前向填補到日；其餘日頻、缺即 NaN（不補）

# 最終參與相關之欄位（含衍生）；helper 欄（high/low/margin_limit/tenyr）算完衍生後剔除
_DROP_AFTER_DERIVE = ("high", "low", "margin_limit", "tenyr")


def bootstrap(cur):
    cur.execute(DDL)


def build_stock_panel(conn, stock_id):
    """組單股每日對齊面板（DataFrame，index=date，欄=各 raw 欄位 + 衍生）。無價量列 → None。"""
    with db.transaction(conn) as cur:
        cur.execute(_PRICE_SQL, (stock_id,))
        prows = cur.fetchall()
        if not prows:
            return None
        df = pd.DataFrame(prows, columns=["date", "close", "volume", "money", "turnover", "high", "low", "spread"]).set_index("date")
        df = df.astype(float)
        for col, sql in _SRC:
            cur.execute(sql, (stock_id,))
            rows = cur.fetchall()
            s = pd.Series({d: (float(v) if v is not None else np.nan) for d, v in rows}, dtype=float, name=col)
            df = df.join(s, how="left")
    if "revenue" in df.columns:
        for col in _FFILL:
            df[col] = df[col].ffill()                                    # 月頻 as-of 前向填補
    # 衍生欄（純 raw 數學轉換）
    with np.errstate(divide="ignore", invalid="ignore"):
        df["range"] = (df["high"] - df["low"]) / df["close"]
        df["margin_usage"] = df["margin_balance"] / df["margin_limit"].where(df["margin_limit"] > 0)
        df["inst_net_ratio"] = df["inst_net"] / df["inst_gross"].where(df["inst_gross"] > 0)
        df["price_to_10yr"] = df["close"] / df["tenyr"].where(df["tenyr"] > 0)
    df = df.drop(columns=[c for c in _DROP_AFTER_DERIVE if c in df.columns])
    return df.replace([np.inf, -np.inf], np.nan)


def compute_correlations(df, *, min_obs=MIN_OBS):
    """單股面板 → [(field_a, field_b, method, basis, n_obs, corr)]（level+change × pearson+spearman；
    上三角、corr 有定義且 n_obs≥min_obs 才回）。"""
    out = []
    cols = sorted(df.columns)
    for basis, X in (("level", df), ("change", df.diff())):
        # pairwise 共同非空 obs 數（一次算全矩陣）
        mask = X[cols].notna().astype(float)
        nmat = mask.T.values @ mask.values                              # n_obs[i,j]
        for method in ("pearson", "spearman"):
            C = X[cols].corr(method=method, min_periods=min_obs)
            cv = C.values
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    n = int(nmat[i, j])
                    c = cv[i, j]
                    if n >= min_obs and c is not None and np.isfinite(c):
                        out.append((cols[i], cols[j], method, basis, n, round(float(c), 6)))
    return out


def analyze_stock(conn, stock_id, *, min_obs=MIN_OBS):
    """單股:建面板 → 算相關 → upsert field_correlation。回寫入列數（無價量 → 0）。"""
    df = build_stock_panel(conn, stock_id)
    if df is None or len(df) < min_obs:
        return 0
    rows = compute_correlations(df, min_obs=min_obs)
    if not rows:
        return 0
    data = [(stock_id, *r) for r in rows]
    with db.transaction(conn) as cur:
        bootstrap(cur)
        execute_values(
            cur,
            f"INSERT INTO {TABLE} (stock_id, field_a, field_b, method, basis, n_obs, corr) VALUES %s "
            f"ON CONFLICT (stock_id, field_a, field_b, method, basis) DO UPDATE SET "
            f"n_obs=EXCLUDED.n_obs, corr=EXCLUDED.corr, computed_at=now()",
            data, page_size=1000)
    return len(data)


# ══ lead-lag(predictive):X 在 t vs t+1 進場之未來 h 日報酬 — 找可預測 alpha 候選 ══
LEADLAG_TABLE = "field_return_leadlag"
LEADLAG_HORIZONS = (1, 5, 20)
DDL_LEADLAG = f"""
CREATE TABLE IF NOT EXISTS {LEADLAG_TABLE} (
    stock_id    VARCHAR(255) NOT NULL,
    field       VARCHAR(64)  NOT NULL,
    basis       VARCHAR(16)  NOT NULL,   -- level / change
    method      VARCHAR(16)  NOT NULL,   -- pearson / spearman
    horizon     INTEGER      NOT NULL,   -- 未來 h 交易日
    n_obs       INTEGER      NOT NULL,
    corr        NUMERIC(8,6) NOT NULL,   -- corr(predictor_t, fwd_ret) [-1,1]
    computed_at TIMESTAMP    NOT NULL DEFAULT now(),
    PRIMARY KEY (stock_id, field, basis, method, horizon)
)"""


def compute_leadlag(df, *, horizons=LEADLAG_HORIZONS, min_obs=MIN_OBS):
    """單股面板 → [(field, basis, method, horizon, n_obs, corr)]。
    predictor=X_t（level 或 ΔX）;target=t+1 進場、持有 h 日之還原價 log return（#8 anti-leakage:
    predictor 用 ≤t、報酬用 t+1 起,predictor 早於報酬窗）。corr 有定義且 n_obs≥min_obs 才回。"""
    c = df["close"].astype(float)
    cols = sorted(df.columns)
    out = []
    with np.errstate(divide="ignore", invalid="ignore"):
        for h in horizons:
            fwd = np.log(c.shift(-(1 + h)) / c.shift(-1))                # t→ 報酬[t+1, t+1+h]、index 在 t
            fwd = fwd.replace([np.inf, -np.inf], np.nan)
            for basis, X in (("level", df), ("change", df.diff())):
                for method in ("pearson", "spearman"):
                    for f in cols:
                        pair = pd.concat([X[f], fwd], axis=1).dropna()
                        if len(pair) >= min_obs:
                            cc = pair.iloc[:, 0].corr(pair.iloc[:, 1], method=method)
                            if cc is not None and np.isfinite(cc):
                                out.append((f, basis, method, h, len(pair), round(float(cc), 6)))
    return out


def analyze_stock_leadlag(conn, stock_id, *, min_obs=MIN_OBS):
    """單股 lead-lag:建面板 → 算 X_t vs 未來報酬 → upsert field_return_leadlag。回寫入列數。"""
    df = build_stock_panel(conn, stock_id)
    if df is None or len(df) < min_obs:
        return 0
    rows = compute_leadlag(df, min_obs=min_obs)
    if not rows:
        return 0
    data = [(stock_id, *r) for r in rows]
    with db.transaction(conn) as cur:
        cur.execute(DDL_LEADLAG)
        execute_values(
            cur,
            f"INSERT INTO {LEADLAG_TABLE} (stock_id, field, basis, method, horizon, n_obs, corr) VALUES %s "
            f"ON CONFLICT (stock_id, field, basis, method, horizon) DO UPDATE SET "
            f"n_obs=EXCLUDED.n_obs, corr=EXCLUDED.corr, computed_at=now()",
            data, page_size=1000)
    return len(data)


def cross_stock_leadlag_summary(conn, *, method="spearman", basis="change", horizon=20, min_stocks=30):
    """跨股 lead-lag 聚合:每 field 在多股之 corr(X, 未來報酬) → 中位/正負一致率/顯著率。
    依 |median| 降序——最一致之可預測欄位（alpha 候選）。"""
    with db.transaction(conn) as cur:
        cur.execute(
            f"SELECT field, count(*) n_stocks, "
            f"  percentile_cont(0.5) WITHIN GROUP (ORDER BY corr) median_corr, "
            f"  avg((corr>0)::int)::float8 pct_pos, avg((abs(corr)>=0.03)::int)::float8 pct_signal "
            f"FROM {LEADLAG_TABLE} WHERE method=%s AND basis=%s AND horizon=%s "
            f"GROUP BY field HAVING count(*)>=%s "
            f"ORDER BY abs(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)) DESC",
            (method, basis, horizon, min_stocks))
        cols = [d[0] for d in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


def cross_stock_summary(conn, *, method="spearman", basis="change", min_stocks=30):
    """跨股聚合:每 (field_a, field_b) 在多股之相關 → 中位/均值/正負一致率/顯著(|median|≥0.1)。
    回 DataFrame，依 |median_corr| 降序（最一致之正/負相關欄位對）。"""
    with db.transaction(conn) as cur:
        cur.execute(
            f"SELECT field_a, field_b, count(*) n_stocks, "
            f"  percentile_cont(0.5) WITHIN GROUP (ORDER BY corr) median_corr, avg(corr) mean_corr, "
            f"  avg((corr>0)::int)::float8 pct_pos, avg((abs(corr)>=0.3)::int)::float8 pct_strong "
            f"FROM {TABLE} WHERE method=%s AND basis=%s "
            f"GROUP BY field_a, field_b HAVING count(*)>=%s "
            f"ORDER BY abs(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)) DESC",
            (method, basis, min_stocks))
        cols = [d[0] for d in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)
