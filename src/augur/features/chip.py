"""augur 籌碼特徵 — 從法人/融資券/借券/外資/大戶 7 表算 source-pure 籌碼面特徵(F2b)。

🎯 這支在做什麼(白話):給一個 as-of 面板日期 + 一個 stock_id,query 7 表算 7 個籌碼面特徵
(法人淨買比、融資使用率、外資持股、大戶比、借券賣壓、借券費率、官股淨買),嚴格 source-pure:
算不出(無資料/分母 0/不在合理範圍)→ 不含該 key(缺列、不存 fake/zero-fill,#1)。

對應 F2 roadmap(reports/augur_f2_feature_expansion_roadmap_20260612.md)F2b 籌碼/法人期:
- f1 institutional_net_buy_ratio_20d:三大法人 20 日淨買 / 總交額(範圍 [-1,1]、軸②資金流)
- f2 margin_usage_ratio:融資使用率(融資餘額/限額、信用循環相位 P1 個股槓桿)
- f3 foreign_holding_pct:外資持股 %(level、軸②籌碼)
- f4 top_holders_pct:大戶比('more than 1,000,001' 級距 percent、Pareto P1 思想)
- f5 sbl_short_balance_log:借券賣空餘額 log(空方壓力、軸②)
- f6 lending_fee_rate_mean_30d:借券費率 30 日均(放空成本、軸②)
- f7 gov_bank_net_buy_60d:官股 60 日淨買金額(sign×log1p、護盤訊號、軸⑤事件型)

邊界:不抓 API、不選股;只算特徵(#3)。所有特徵以「panel_date 當下已知」之 raw 計算(P/E 類、anti-leakage #8;
但籌碼盤後公布之 T+1 規則此版採保守 date<=panel_date 同日含、上線後待 probe 公布時刻);算不出即缺列(#1)。

⚠️ 已知限制(2026-06-25 v3 實證、待 P/E 重構):本 7 features 含**稀疏 E 類**——`lending_fee_rate_mean_30d`(借券費率)
/`sbl_short_balance_log`(借券餘額)/`gov_bank_net_buy_60d`(官股淨買)為借券/官股事件型、非每股每期有。
目前全當 P 類「算不出即缺列」→ 入完整度必齊 gate 時變過嚴排除器(借券標的每期變動、跨多 panel 交集→0,
v3 原版實證核心=0 股)。**正解**(F2 roadmap E 類定義):E 類應真零語意(無借券=無放空壓力=0、不缺列)、
不入完整度必齊集;唯連續 P 類(`foreign_holding_pct`/`margin_usage_ratio`/`institutional_net_buy_ratio_20d`
/`top_holders_pct`、活躍股每期有)入 gate。實證:2014+ × 19 連續 features → 742 核心。詳見
reports/augur_phase78_core_universe_pilot_v3_20260625.md。

守 #1(算不出即缺列、不存無源值)· #8(籌碼 as-of ≤t)· #5(numeric)· F2 roadmap F2b。
"""
from __future__ import annotations

import numpy as np

# 1) 法人買賣(多 name/日,各法人別 buy/sell 金額;group 由 date sum 為當日合計後算 20 日比)
_INST_SQL = (
    'SELECT date, sum(buy)::float8 AS dbuy, sum(sell)::float8 AS dsell '
    'FROM "TaiwanStockInstitutionalInvestorsBuySell" '
    'WHERE stock_id=%s AND date <= %s '
    'GROUP BY date ORDER BY date DESC LIMIT 30'
)
# 2) 融資餘額(最近一筆;融資使用率 = MarginPurchaseTodayBalance / MarginPurchaseLimit)
_MARGIN_SQL = (
    'SELECT "MarginPurchaseTodayBalance"::float8, "MarginPurchaseLimit"::float8 '
    'FROM "TaiwanStockMarginPurchaseShortSale" WHERE stock_id=%s AND date <= %s '
    'ORDER BY date DESC LIMIT 1'
)
# 3) 外資持股(最近一筆;ForeignInvestmentSharesRatio 0-100)
_SHARE_SQL = (
    'SELECT "ForeignInvestmentSharesRatio"::float8 '
    'FROM "TaiwanStockShareholding" WHERE stock_id=%s AND date <= %s '
    'ORDER BY date DESC LIMIT 1'
)
# 4) 大戶比(最近一筆,「more than 1,000,001」為最高級距 % = 持股 ≥100 萬股以上之股本佔比)
_HOLD_SQL = (
    'SELECT percent::float8 FROM "TaiwanStockHoldingSharesPer" '
    "WHERE stock_id=%s AND date <= %s AND \"HoldingSharesLevel\"='more than 1,000,001' "
    'ORDER BY date DESC LIMIT 1'
)
# 5) SBL 借券賣空餘額(最近一筆,絕對量、log1p 處理)
_SBL_SQL = (
    'SELECT "SBLShortSalesCurrentDayBalance"::float8 '
    'FROM "TaiwanDailyShortSaleBalances" WHERE stock_id=%s AND date <= %s '
    'ORDER BY date DESC LIMIT 1'
)
# 6) 借券費率(近 30 日各筆 fee_rate 平均)
_LEND_SQL = (
    'SELECT fee_rate::float8 FROM "TaiwanStockSecuritiesLending" '
    'WHERE stock_id=%s AND date <= %s '
    'ORDER BY date DESC LIMIT 100'
)
# 7) 官股各銀行買賣(多 bank_name/日,group 為當日合計、取 60 日累計)
_GOVBANK_SQL = (
    'SELECT date, (sum(buy_amount)-sum(sell_amount))::float8 AS net '
    'FROM "TaiwanStockGovernmentBankBuySell" '
    'WHERE stock_id=%s AND date <= %s '
    'GROUP BY date ORDER BY date DESC LIMIT 60'
)


def compute_chip_features(cur, sid, panel_date):
    """對 sid + panel_date 算 7 個籌碼 features → {feature: value};算不出 → 不含該 key(缺列、#1)。"""
    out = {}

    # f1 三大法人 20 日淨買比(-1~1);<20 日資料 / gross=0 → 缺
    cur.execute(_INST_SQL, (sid, panel_date))
    inst = cur.fetchall()
    if len(inst) >= 20:
        net_sum = sum((r[1] or 0) - (r[2] or 0) for r in inst[:20])
        gross_sum = sum((r[1] or 0) + (r[2] or 0) for r in inst[:20])
        if gross_sum > 0:
            v = net_sum / gross_sum
            if np.isfinite(v) and -1.0 <= v <= 1.0:
                out["institutional_net_buy_ratio_20d"] = float(v)

    # f2 融資使用率(0~10 安全上界、實務 0~1 居多);無資料 / Limit≤0 → 缺
    cur.execute(_MARGIN_SQL, (sid, panel_date))
    row = cur.fetchone()
    if row and row[0] is not None and row[1] and row[1] > 0:
        v = row[0] / row[1]
        if np.isfinite(v) and 0.0 <= v <= 10.0:
            out["margin_usage_ratio"] = float(v)

    # f3 外資持股 %(0~100);無 → 缺
    cur.execute(_SHARE_SQL, (sid, panel_date))
    row = cur.fetchone()
    if row and row[0] is not None:
        v = row[0]
        if np.isfinite(v) and 0.0 <= v <= 100.0:
            out["foreign_holding_pct"] = float(v)

    # f4 大戶比 %(0~100);無 → 缺
    cur.execute(_HOLD_SQL, (sid, panel_date))
    row = cur.fetchone()
    if row and row[0] is not None:
        v = row[0]
        if np.isfinite(v) and 0.0 <= v <= 100.0:
            out["top_holders_pct"] = float(v)

    # f5 SBL 借券餘額 log1p(≥0);無 → 缺
    cur.execute(_SBL_SQL, (sid, panel_date))
    row = cur.fetchone()
    if row and row[0] is not None and row[0] >= 0:
        v = float(np.log1p(row[0]))
        if np.isfinite(v):
            out["sbl_short_balance_log"] = v

    # f6 借券費率 30 日平均;<5 筆 → 缺
    cur.execute(_LEND_SQL, (sid, panel_date))
    fees = [r[0] for r in cur.fetchall() if r[0] is not None]
    if len(fees) >= 5:
        v = float(np.mean(fees))
        if np.isfinite(v):
            out["lending_fee_rate_mean_30d"] = v

    # f7 官股 60 日淨買金額(sign × log1p(|net|));<30 日有官股交易 → 缺
    cur.execute(_GOVBANK_SQL, (sid, panel_date))
    rows = cur.fetchall()
    if len(rows) >= 30:
        total = sum(r[1] or 0 for r in rows[:60])
        v = float(np.sign(total) * np.log1p(abs(total)))
        if np.isfinite(v):
            out["gov_bank_net_buy_60d"] = v

    return out
