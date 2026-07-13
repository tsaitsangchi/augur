"""augur 預測標籤 — H 日後向前還原報酬 + 橫斷面標準化（evaluation 層、#8 紅線）。

🎯 這支在做什麼（白話）：給 as-of 面板日 t + 一批核心股，算每股「未來 H 交易日的相對強弱標籤」：
- **t+1 進場口徑**（#8）：panel_date t 當日算特徵、**次一交易日進場**、持有 H 個交易日後出場
  （不用 t 當日尚未實現/未收盤之資訊；進出場日由全市場交易日曆決定）。
- **還原價（PriceAdj）log return**（#1）：除權息跳空非真報酬 → 一律用還原價，log(close_出場/close_進場)。
- **橫斷面標準化**：同一 panel 內跨股 rank（0-1 百分位）——augur 預測「誰相對強」、非絕對漲跌（靈魂）。

label **只在 evaluation/training 構造、不入 feature 層**（#8）；label 窗與訓練集之 purge/embargo 由
walkforward 層負責（本層只造 label、不切分）。

#8 anti-leakage：t+1 進場 + 還原價；#1 source-pure：PriceAdj 真值、算不出（資料不足/停牌 close≤0）→ 缺列。
#12 SSOT：label 構造唯一住此、所有 validator import（跨模型/週期可比）。
守 #8（anti-leakage：t+1 進場 + 還原價）· #1（source-pure：算不出即缺列）· #12（SSOT：label 構造唯一住此）。
"""
from __future__ import annotations

import numpy as np

from augur.core import db

ADJ_TABLE = "TaiwanStockPriceAdj"
HORIZONS = (5, 20, 60, 252)   # 週/月/季/年（calendar 慣例；H=252 經 purge 後獨立觀測少、屬探索性，F3 plan 修正）


def _calendar(cur, start):
    """全市場交易日曆（PriceAdj distinct date > start，升序）——進出場日對齊全市場、非個股缺日。"""
    cur.execute(f'SELECT DISTINCT date FROM "{ADJ_TABLE}" WHERE date > %s ORDER BY date', (start,))
    return [r[0] for r in cur.fetchall()]


def full_calendar(conn):
    """全市場交易日曆一次性 query（升序全 date）——供 evaluation 批次重用，免 walk-forward N² 全表掃描。

    呼叫端（如 baseline 階梯）開頭取一次，逐 panel 傳入 forward_returns(calendar=...) 以記憶體 filter
    取代每折每 panel 重複掃描 PriceAdj（11M 列）。結果與逐 panel `_calendar` 完全一致（同一升序全市場日曆）。
    """
    with db.transaction(conn) as cur:
        cur.execute(f'SELECT DISTINCT date FROM "{ADJ_TABLE}" ORDER BY date')
        return [r[0] for r in cur.fetchall()]


def _entry_exit(calendar, h):
    """t+1 進場口徑：calendar=panel_date 之後（>）的交易日 → entry=calendar[0]（次一交易日）、exit=calendar[h]。
    非交易日 panel（如月底週末）entry 同為次一交易日、不漂移為 t+2。
    日曆不足（panel_date 太近 max date、湊不到 1+h 個交易日）→ (None, None)（label 算不出、#8 不外推）。"""
    if len(calendar) < h + 1:
        return None, None
    return calendar[0], calendar[h]


def forward_returns(conn, panel_date, stock_ids, h, *, calendar=None):
    """每股 t+1 進場、持有 h 交易日之還原價 log return → {stock_id: ret}（算不出之股不含、#1 缺列）。

    entry/exit 日由全市場交易日曆定（t+1 / t+1+h）；close≤0（停牌/異常）或缺價 → 該股不含。
    `calendar`（升序全市場日曆，full_calendar 取得）傳入時以記憶體 filter（>panel_date）取代 DB 掃描，
    結果與逐 panel `_calendar` 一致——批次 evaluation 免 N² 全表掃描。
    """
    with db.transaction(conn) as cur:
        cal = [d for d in calendar if d > panel_date] if calendar is not None else _calendar(cur, panel_date)
        entry, exit_ = _entry_exit(cal, h)
        if entry is None:
            return {}
        cur.execute(
            f'SELECT stock_id, date, close FROM "{ADJ_TABLE}" '
            f'WHERE stock_id = ANY(%s) AND date IN (%s, %s)',
            (list(stock_ids), entry, exit_))
        rows = cur.fetchall()
    px = {}                                                  # {stock_id: {date: close}}
    for sid, d, c in rows:
        px.setdefault(str(sid), {})[d] = c
    out = {}
    for sid, dc in px.items():
        pe, px_ = dc.get(entry), dc.get(exit_)
        if pe is None or px_ is None:
            continue                                         # 缺進場或出場價 → 算不出（#1 缺列）
        try:
            pe, px_ = float(pe), float(px_)
        except (TypeError, ValueError):
            continue
        if pe <= 0 or px_ <= 0:
            continue                                         # 停牌/異常價 → 缺列
        v = float(np.log(px_ / pe))
        if np.isfinite(v):
            out[sid] = v
    return out


def cross_sectional_rank(returns):
    """同 panel 跨股 forward return → 橫斷面百分位 rank（0-1；最弱 0、最強 1）。

    augur 預測相對強弱（靈魂）：絕對 return 僅中間量、rank 才是 label。tie 取平均序位、單股 panel → 0.5。
    """
    items = [(s, r) for s, r in returns.items() if r is not None and np.isfinite(r)]
    n = len(items)
    if n == 0:
        return {}
    if n == 1:
        return {items[0][0]: 0.5}
    order = sorted(items, key=lambda x: x[1])                # 升序：弱→強
    ranks = {}
    i = 0
    while i < n:                                             # tie 取平均序位（同 return 同 rank）
        j = i
        while j + 1 < n and order[j + 1][1] == order[i][1]:
            j += 1
        avg_pos = (i + j) / 2.0
        for k in range(i, j + 1):
            ranks[order[k][0]] = avg_pos / (n - 1)           # 標準化 0-1
        i = j + 1
    return ranks


def labels(conn, panel_date, stock_ids, h, *, calendar=None):
    """一站式：forward_returns → cross_sectional_rank → {stock_id: rank_label}（H 日相對強弱）。
    回 {stock_id: 0-1 rank}；算不出之股不含（#1）。raw return 需要時呼叫 forward_returns 取。
    `calendar`：批次評估時傳 full_calendar 結果，免重複全表掃描（向後相容、預設 None=自行 query）。"""
    return cross_sectional_rank(forward_returns(conn, panel_date, stock_ids, h, calendar=calendar))
