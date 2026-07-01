#!/usr/bin/env python
"""augur 跨表深度交互掃描 — 角度D:跨群兩兩 raw 欄交互之未來報酬橫斷面 IC(344 宇宙、本地零 usage #28)。

🎯 這支在做什麼(白話):前輪窮盡了「群內」raw 交互(價量/法人/融資券/外資/估值各自內部)→ 飽和。
本支補唯一沒做過的角度——**跨表跨群兩兩交互**(價量×財報、籌碼×估值、融資券×法人、月營收×量能…):
- 28 panel × 每 panel as-of 核心(core_universe_asof、point-in-time #8)
- 每條腿 as-of 取值:raw 每股 `date<=panel_date` 最新列;財報/月營收經 release_lag gate(#8 命門)
- 跨群配對:z 乘積(協同)/ z 差(分歧)兩種 transform → 橫斷面 rank IC(spearman) vs H=20/60/120
- HAC-t(metrics.effective_t_hac、去重疊窗自相關 G8);增量測 = |IC| vs 兩成分單欄 max
判讀:|IC|>成分 max 且 |HAC|≥3 且 H60/H120 多數一致 = 真新訊號;否則證實跨表也飽和。
#1 缺即略、#8 t+1 還原價 label(label.labels)、#15 凡數字出自本次 stdout。
用法:PYTHONPATH=src venv/bin/python3 scripts/run_cross_table_interaction_scan.py [t2lag]
"""
import sys
import itertools

import numpy as np

from augur.core import db
from augur.evaluation import baseline, label, metrics
from augur.features import release_lag

HS = [20, 60, 120]


# ---------- 橫斷面工具 ----------
def _zscore(d):
    """{sid:val} → {sid:z}(winsorize±3、缺/常數略、≥30 股)。"""
    items = [(s, float(v)) for s, v in d.items() if v is not None and np.isfinite(float(v))]
    if len(items) < 30:
        return {}
    vals = np.array([v for _, v in items])
    mu, sd = vals.mean(), vals.std()
    if sd == 0:
        return {}
    z = np.clip((vals - mu) / sd, -3, 3)
    return {s: float(zz) for (s, _), zz in zip(items, z)}


def _spearman(sig, lab):
    common = [s for s in sig if s in lab]
    if len(common) < 30:
        return None
    x = np.array([sig[s] for s in common])
    y = np.array([lab[s] for s in common])
    xr = np.argsort(np.argsort(x))
    yr = np.argsort(np.argsort(y))
    if xr.std() == 0 or yr.std() == 0:
        return None
    return float(np.corrcoef(xr, yr)[0, 1])


# ---------- as-of 取值(date<=panel 最新) ----------
def _asof_latest(cur, table, col, panel, stocks, *, where_extra=""):
    """每股取 date<=panel 之最新一列之 col → {sid: val}。DISTINCT ON (stock_id) ORDER date DESC。"""
    cur.execute(
        f'SELECT DISTINCT ON (stock_id) stock_id, "{col}" FROM "{table}" '
        f'WHERE date <= %s AND stock_id = ANY(%s) {where_extra} '
        f'ORDER BY stock_id, date DESC', (panel, stocks))
    out = {}
    for s, v in cur.fetchall():
        if v is not None:
            try:
                out[str(s)] = float(v)
            except (TypeError, ValueError):
                pass
    return out


def _asof_inst_net(cur, panel, stocks, who):
    """法人 who 之 as-of 最新單日淨買(buy-sell)→ {sid: net}(取 date<=panel 最新該法人列)。"""
    cur.execute(
        'SELECT DISTINCT ON (stock_id) stock_id, COALESCE(buy,0)-COALESCE(sell,0) '
        'FROM "TaiwanStockInstitutionalInvestorsBuySell" '
        'WHERE date <= %s AND stock_id = ANY(%s) AND name = %s '
        'ORDER BY stock_id, date DESC', (panel, stocks, who))
    return {str(s): float(v) for s, v in cur.fetchall() if v is not None}


def _adj_close_asof(cur, panel, stocks, back_days):
    """取 panel 當下與往前 back_days 交易日之還原收盤,算 log 動能 → {sid: mom}。
    用 as-of:close@latest(date<=panel) / close@(latest 之前第 back 列)。"""
    cur.execute(
        'SELECT stock_id, date, close FROM "TaiwanStockPriceAdj" '
        'WHERE date <= %s AND stock_id = ANY(%s) AND close > 0 '
        'ORDER BY stock_id, date DESC', (panel, stocks))
    by = {}
    for s, d, c in cur.fetchall():
        by.setdefault(str(s), []).append(float(c))   # 已 date DESC
    out = {}
    for s, seq in by.items():
        if len(seq) > back_days:
            cur_px, past_px = seq[0], seq[back_days]
            if cur_px > 0 and past_px > 0:
                out[s] = float(np.log(cur_px / past_px))
    return out


def _monthrev_yoy_asof(cur, panel, stocks):
    """月營收 YoY:取 release<=panel 已公告之最新月,對去年同月。release_lag gate(#8)。"""
    cur.execute(
        'SELECT stock_id, revenue_year, revenue_month, revenue, date '
        'FROM "TaiwanStockMonthRevenue" WHERE date <= %s AND stock_id = ANY(%s)',
        (panel, stocks))
    rec = {}   # {sid: {(y,m): rev}}
    latest = {}  # {sid: (y,m)} 已公告最新
    for s, y, m, rev, d in cur.fetchall():
        if rev is None:
            continue
        s = str(s)
        if not release_lag.revenue_released(d, panel):
            continue
        rec.setdefault(s, {})[(int(y), int(m))] = float(rev)
        cur_lm = latest.get(s)
        if cur_lm is None or (int(y), int(m)) > cur_lm:
            latest[s] = (int(y), int(m))
    out = {}
    for s, (y, m) in latest.items():
        prev = rec[s].get((y - 1, m))
        cur_rev = rec[s][(y, m)]
        if prev and prev != 0:
            out[s] = (cur_rev - prev) / abs(prev)
    return out


def _gross_margin_asof(cur, panel, stocks):
    """毛利率 = GrossProfit/Revenue,取 financial_released<=panel 之最新季(release_lag gate #8)。"""
    cur.execute(
        'SELECT stock_id, date, type, value FROM "TaiwanStockFinancialStatements" '
        'WHERE date <= %s AND stock_id = ANY(%s) AND type IN (%s, %s)',
        (panel, stocks, "GrossProfit", "Revenue"))
    rec = {}  # {sid: {date: {type:val}}}
    for s, d, t, v in cur.fetchall():
        if v is None:
            continue
        if not release_lag.financial_released(d, panel):
            continue
        rec.setdefault(str(s), {}).setdefault(d, {})[t] = float(v)
    out = {}
    for s, byd in rec.items():
        latest_d = max(byd)
        gp = byd[latest_d].get("GrossProfit")
        rv = byd[latest_d].get("Revenue")
        if gp is not None and rv and rv != 0:
            out[s] = gp / rv
    return out


# ---------- 主流程 ----------
def build_panel_legs(cur, panel, stocks, t2_back=0):
    """組該 panel 全候選腿之 {sid:val} dict。t2_back>0 則動能/估值取更早(t-2 lag 對抗證)。"""
    legs = {}
    # 價量群
    legs["mom20"] = _adj_close_asof(cur, panel, stocks, 20)
    legs["mom60"] = _adj_close_asof(cur, panel, stocks, 60)
    vol = _asof_latest(cur, "TaiwanStockPrice", "Trading_Volume", panel, stocks)
    money = _asof_latest(cur, "TaiwanStockPrice", "Trading_money", panel, stocks)
    tno = _asof_latest(cur, "TaiwanStockPrice", "Trading_turnover", panel, stocks)
    rmax = _asof_latest(cur, "TaiwanStockPrice", "max", panel, stocks)
    rmin = _asof_latest(cur, "TaiwanStockPrice", "min", panel, stocks)
    close = _asof_latest(cur, "TaiwanStockPrice", "close", panel, stocks)
    legs["volume"] = vol
    legs["dollar_vol"] = money
    legs["turnover"] = tno
    legs["range"] = {s: (rmax[s] - rmin[s]) / close[s] for s in rmax
                     if s in rmin and s in close and close.get(s)}
    # 籌碼/法人群
    legs["foreign_net"] = _asof_inst_net(cur, panel, stocks, "Foreign_Investor")
    legs["trust_net"] = _asof_inst_net(cur, panel, stocks, "Investment_Trust")
    legs["foreign_ratio"] = _asof_latest(cur, "TaiwanStockShareholding",
                                         "ForeignInvestmentSharesRatio", panel, stocks)
    # 融資券群
    legs["margin_bal"] = _asof_latest(cur, "TaiwanStockMarginPurchaseShortSale",
                                      "MarginPurchaseTodayBalance", panel, stocks)
    legs["short_bal"] = _asof_latest(cur, "TaiwanStockMarginPurchaseShortSale",
                                     "ShortSaleTodayBalance", panel, stocks)
    # 估值群
    legs["per"] = _asof_latest(cur, "TaiwanStockPER", "PER", panel, stocks)
    legs["pbr"] = _asof_latest(cur, "TaiwanStockPER", "PBR", panel, stocks)
    legs["divyield"] = _asof_latest(cur, "TaiwanStockPER", "dividend_yield", panel, stocks)
    # 財報/月營收群(release_lag gate)
    legs["monthrev_yoy"] = _monthrev_yoy_asof(cur, panel, stocks)
    legs["gross_margin"] = _gross_margin_asof(cur, panel, stocks)
    return legs


# 群歸屬(只測跨群配對)
GROUP = {
    "mom20": "price", "mom60": "price", "volume": "price", "dollar_vol": "price",
    "turnover": "price", "range": "price",
    "foreign_net": "chip", "trust_net": "chip", "foreign_ratio": "chip",
    "margin_bal": "margin", "short_bal": "margin",
    "per": "value", "pbr": "value", "divyield": "value",
    "monthrev_yoy": "fund", "gross_margin": "fund",
}


def main():
    t2 = len(sys.argv) > 1 and sys.argv[1] == "t2lag"
    with db.connect() as conn:
        cal = label.full_calendar(conn)
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            panels = [r[0] for r in cur.fetchall()]
        print(f"跨表交互掃描:{len(panels)} panel × as-of 核心 × H={HS}{' (t-2 lag 對抗證)' if t2 else ''}\n")

        legnames = list(GROUP)
        single = {l: {h: [] for h in HS} for l in legnames}
        pairs = [(a, b) for a, b in itertools.combinations(legnames, 2) if GROUP[a] != GROUP[b]]
        prod_ic = {p: {h: [] for h in HS} for p in pairs}
        diff_ic = {p: {h: [] for h in HS} for p in pairs}

        for panel in panels:
            stocks = baseline._asof_stocks(conn, panel)
            if len(stocks) < 30:
                continue
            with db.transaction(conn) as cur:
                legs = build_panel_legs(cur, panel, stocks)
            labs = {h: label.labels(conn, panel, stocks, h, calendar=cal) for h in HS}
            if all(len(labs[h]) < 30 for h in HS):
                continue
            z = {l: _zscore(legs[l]) for l in legnames}
            for h in HS:
                lab = labs[h]
                if len(lab) < 30:
                    continue
                for l in legnames:
                    ic = _spearman(legs[l], lab)
                    if ic is not None:
                        single[l][h].append(ic)
                for a, b in pairs:
                    if not z[a] or not z[b]:
                        continue
                    common = [s for s in z[a] if s in z[b]]
                    if len(common) < 30:
                        continue
                    prod = {s: z[a][s] * z[b][s] for s in common}
                    diff = {s: z[a][s] - z[b][s] for s in common}
                    ic = _spearman(prod, lab)
                    if ic is not None:
                        prod_ic[(a, b)][h].append(ic)
                    ic = _spearman(diff, lab)
                    if ic is not None:
                        diff_ic[(a, b)][h].append(ic)

    def stat(arr):
        a = np.array(arr)
        if len(a) < 3:
            return (a.mean() if len(a) else 0.0, None, len(a))
        ht = metrics.effective_t_hac(list(a))
        return (float(a.mean()), ht, len(a))

    # 單欄基準(每腿取 H60 為代表 max)
    sic = {}
    print("— 單欄 cross-sectional rank IC (H60、HAC-t、n_panel) —")
    for l in legnames:
        m, t, n = stat(single[l][60])
        sic[l] = abs(m)
        print(f"  {l:14s} IC={m:>+.4f}  HAC-t={('%.2f'%t) if t else 'NA':>6s}  ({n})")

    def report(label_, ic_dict):
        print(f"\n— {label_} top 20(H60 排序;含 H20/H120 與增量測)—")
        rows = []
        for (a, b), hd in ic_dict.items():
            m60, t60, n60 = stat(hd[60])
            if n60 < 10:
                continue
            m20, t20, _ = stat(hd[20])
            m120, t120, _ = stat(hd[120])
            comp = max(sic.get(a, 0), sic.get(b, 0))
            rows.append((a, b, m20, t20, m60, t60, m120, t120, comp, n60))
        rows.sort(key=lambda r: -abs(r[4]))
        print(f"  {'pair':30s} {'IC20':>7s}{'t20':>6s} {'IC60':>7s}{'t60':>6s} {'IC120':>7s}{'t120':>6s} {'cmax':>6s} {'新?':>4s}")
        for a, b, m20, t20, m60, t60, m120, t120, comp, n in rows[:20]:
            consist = (m60 * m120 > 0) and (m20 * m60 > 0)
            new = "Y" if abs(m60) > comp and t60 and abs(t60) >= 3 and consist else "-"
            t20s = ('%+.1f' % t20) if t20 else 'NA'
            t60s = ('%+.1f' % t60) if t60 else 'NA'
            t120s = ('%+.1f' % t120) if t120 else 'NA'
            print(f"  {a+'*'+b:30s} {m20:>+.4f}{t20s:>6s} {m60:>+.4f}{t60s:>6s} {m120:>+.4f}{t120s:>6s} {comp:>6.3f} {new:>4s}")

    report("z 乘積(協同)交互", prod_ic)
    report("z 差(分歧)交互", diff_ic)


if __name__ == "__main__":
    main()
