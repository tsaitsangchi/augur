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

**E/P 類設計(2026-06-25 E 類已改真零)**:本 7 features 分兩類——
- **連續 P 類**(4):`institutional_net_buy_ratio_20d`/`margin_usage_ratio`/`foreign_holding_pct`/`top_holders_pct`
  (活躍股每期有)→ 算不出即缺列(#1)、入完整度 gate。
- **稀疏 E 類**(3):`sbl_short_balance_log`/`lending_fee_rate_mean_30d`/`gov_bank_net_buy_60d`(借券/官股事件型)
  → **真零語意**:無事件填中性 0(無賣壓/無成本/無官股介入)、全 roster 皆得真值。前提=該 3 表 sync 完整至 as-of
  (#7/#1「無列=真無事件」,實證 2026-06-25:max date 皆到 as-of、覆蓋符合事件型稀疏;
  此前提由 _table_covers 雙側機械 gate 強制——min ≤ panel 且 max ≥ panel − 容忍,非僅註記)。
原誤當 P 類「算不出即缺列」→ 入完整度 gate 跨多 panel 交集→0(v3 原版核心=0 股之教訓);真零後可安全入 gate
(全 roster 有值、不誤殺)。詳見 reports/augur_phase78_core_universe_pilot_v3_20260625.md。

守 #1(算不出即缺列、不存無源值)· #8(籌碼 as-of ≤t)· #5(numeric)· F2 roadmap F2b。
"""
from __future__ import annotations

from datetime import date

import numpy as np

# 源表覆蓋範圍快取(E 類真零前提、審查 G2/G3 + 稽核 E11):(min,max);panel 不在覆蓋內時「無列」＝未 sync、非真無事件 → 該 E 特徵缺列、不填 0(防捏造零、守 #1)。
_TABLE_DATE_RANGE = {}

# 近端容忍(日曆日):3 表 table-level 相鄰事件日 gap 實測 max=13(2026-07-04 DB 實查、CNY 長假)→ 容 14 天無新列仍屬覆蓋,超過視為 sync 未達 as-of。
_MAX_STALENESS_DAYS = 14


def _table_covers(cur, table, panel_date):
    """源表是否已覆蓋 panel_date(min <= panel 且 max >= panel − 容忍;真零前提之機械 gate、E11)。範圍查一次快取(table-level、非 per-stock)。"""
    if table not in _TABLE_DATE_RANGE:
        cur.execute(f'SELECT min(date), max(date) FROM "{table}"')
        _TABLE_DATE_RANGE[table] = cur.fetchone()
    mn, mx = _TABLE_DATE_RANGE[table]
    if mn is None or mx is None:
        return False
    p = panel_date if hasattr(panel_date, "year") else date.fromisoformat(str(panel_date)[:10])
    m = mn if hasattr(mn, "year") else date.fromisoformat(str(mn)[:10])
    x = mx if hasattr(mx, "year") else date.fromisoformat(str(mx)[:10])
    return m <= p and (p - x).days <= _MAX_STALENESS_DAYS

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

    # ── f5-f7 稀疏 E 類事件型 → 真零語意（F2 roadmap E 類定義 + pilot v3 修正）──
    # 前提（#7/#1）：3 表 sync 完整至 as-of（實證 2026-06-25：max date 皆到 as-of、覆蓋符合事件型稀疏）
    # → 「無列＝真無事件」成立 → 無事件填中性 0（非缺列）、全 roster 皆得真值、不入完整度 gate 時誤殺。
    # 別於 P 類「算不出即缺列」：E 類「有事件用真值、無事件＝0」（無賣壓/無成本/無官股介入之中性值）；
    # 去 P 類少樣本門檻（原 ≥5/≥30）——有 1 筆事件即真實訊號，門檻是 P 類思維、不適 E 類（pilot v3 教訓）。

    # 真零前提（審查 G2/G3 + 稽核 E11）：源表須已覆蓋該 panel——起始側 min ≤ panel（如 gov_bank 表 2021-07 起,
    # 早於此之 panel 不覆蓋）+ 近端側 max ≥ panel − 容忍（panel 超過 sync 進度時「無列」＝未 sync 非真無事件）
    # → 任一側不覆蓋即缺列、不填 0（防捏造零）。

    # f5 SBL 借券賣空餘額 log1p（無借券賣空＝無賣壓＝0；表覆蓋下之真零）
    if _table_covers(cur, "TaiwanDailyShortSaleBalances", panel_date):
        cur.execute(_SBL_SQL, (sid, panel_date))
        row = cur.fetchone()
        bal = float(row[0]) if row and row[0] is not None and row[0] >= 0 else 0.0
        out["sbl_short_balance_log"] = float(np.log1p(bal))

    # f6 借券費率 30 日平均（無借券＝無放空成本壓力＝0；有借券即用真實費率均值）
    if _table_covers(cur, "TaiwanStockSecuritiesLending", panel_date):
        cur.execute(_LEND_SQL, (sid, panel_date))
        fees = [r[0] for r in cur.fetchall() if r[0] is not None]
        out["lending_fee_rate_mean_30d"] = float(np.mean(fees)) if fees else 0.0

    # f7 官股 60 日淨買 sign × log1p(|net|)（無官股交易＝無介入＝0；累計有幾日算幾日）
    if _table_covers(cur, "TaiwanStockGovernmentBankBuySell", panel_date):
        cur.execute(_GOVBANK_SQL, (sid, panel_date))
        total = sum((r[1] or 0) for r in cur.fetchall()[:60])
        out["gov_bank_net_buy_60d"] = float(np.sign(total) * np.log1p(abs(total)))

    return out
