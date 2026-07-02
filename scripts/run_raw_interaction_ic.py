#!/usr/bin/env python
"""augur raw 欄位交互橫斷面 IC 掃描 — 找未知預測訊號(13 raw 單欄 + 78 對非線性 z-乘積交互)。

🎯 這支在做什麼(白話):前輪做的是 within-stock 單欄相關 + featurized 交互;**這支補唯一沒做過的角度**——
直接對 raw 欄位之**橫斷面 rank IC**(靈魂正確鏡頭:預測誰相對強)+ **欄位兩兩 z-乘積非線性交互**:
- 月頻 panel(~每 21 交易日)× core_universe,as-of panel_date 取 13 raw 訊號(估值/籌碼/流動/動能)
- 單欄:cross-sectional spearman(signal, H=20 未來報酬 rank);跨 panel 取均 + t-stat
- 交互:z_i × z_j 全 78 對 → 同樣 IC;**增量測 = |IC(交互)| vs max(|IC(成分)|)**(交互不顯著高於成分 = 線性冗餘)
判讀:找 |IC| 高且**交互 >> 成分**者 = 真新訊號;否則證實飽和。本地零 usage(#28)、#8 t+1 還原價、#1 缺即略。
執行指令矩陣:python scripts/run_raw_interaction_ic.py
"""
import itertools

import numpy as np

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.evaluation import label

H = 20
STEP = 21          # panel 間隔(交易日)≈月頻
START = "2022-01-01"


def _zscore(d):
    """{sid:val} → {sid:z}(winsorize±3、缺/常數略)。"""
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
    """{sid:x} vs {sid:rank} → spearman(共同 sid、≥30)。"""
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


def _pull(cur, table, col, dates, stocks, agg=None):
    """{(date,sid): val} for table.col at exact dates(daily as-of)。agg='instnet' 特例聚合。"""
    if agg == "instnet":
        cur.execute('SELECT date, stock_id, sum(COALESCE(buy,0)-COALESCE(sell,0)) '
                    'FROM "TaiwanStockInstitutionalInvestorsBuySell" '
                    'WHERE date::text = ANY(%s) AND stock_id = ANY(%s) GROUP BY date, stock_id', (dates, stocks))
    else:
        cur.execute(f'SELECT date, stock_id, "{col}" FROM "{table}" '
                    f'WHERE date::text = ANY(%s) AND stock_id = ANY(%s)', (dates, stocks))
    out = {}
    for d, s, v in cur.fetchall():
        if v is not None:
            try:
                out[(str(d), str(s))] = float(v)
            except (TypeError, ValueError):
                pass
    return out


def main():
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe ORDER BY stock_id")
            stocks = [r[0] for r in cur.fetchall()]
        cal = label.full_calendar(conn)
        cal = [d for d in cal if str(d) >= START]
        panels = cal[::STEP]
        panels = [p for p in panels if cal.index(p) + H + 2 < len(cal)]   # 留足 H+1 出場
        pdates = [str(p) for p in panels]
        print(f"raw 交互 IC 掃描:{len(stocks)} 股 × {len(panels)} panel(月頻 {START}+)× H={H}\n")

        # adj close for momentum：取 panel 及前 20/60 交易日
        idx = {str(d): i for i, d in enumerate(cal)}
        need_dates = set(pdates)
        for p in pdates:
            i = idx[p]
            for back in (20, 60):
                if i - back >= 0:
                    need_dates.add(str(cal[i - back]))
        with db.transaction(conn) as cur:
            cur.execute('SELECT date, stock_id, close FROM "TaiwanStockPriceAdj" '
                        'WHERE date::text = ANY(%s) AND stock_id = ANY(%s) AND close > 0',
                        (sorted(need_dates), stocks))
            adj = {(str(d), str(s)): float(c) for d, s, c in cur.fetchall()}

            per = _pull(cur, "TaiwanStockPER", "PER", pdates, stocks)
            pbr = _pull(cur, "TaiwanStockPER", "PBR", pdates, stocks)
            dy = _pull(cur, "TaiwanStockPER", "dividend_yield", pdates, stocks)
            fpct = _pull(cur, "TaiwanStockShareholding", "ForeignInvestmentSharesRatio", pdates, stocks)
            marg = _pull(cur, "TaiwanStockMarginPurchaseShortSale", "MarginPurchaseTodayBalance", pdates, stocks)
            shrt = _pull(cur, "TaiwanStockMarginPurchaseShortSale", "ShortSaleTodayBalance", pdates, stocks)
            vol = _pull(cur, "TaiwanStockPrice", "Trading_Volume", pdates, stocks)
            mon = _pull(cur, "TaiwanStockPrice", "Trading_money", pdates, stocks)
            tno = _pull(cur, "TaiwanStockPrice", "Trading_turnover", pdates, stocks)
            rng_max = _pull(cur, "TaiwanStockPrice", "max", pdates, stocks)
            rng_min = _pull(cur, "TaiwanStockPrice", "min", pdates, stocks)
            inet = _pull(cur, None, None, pdates, stocks, agg="instnet")

        # 每 panel 建橫斷面訊號 dict
        SIGNALS = ["per", "pbr", "divyield", "foreign_pct", "margin", "short", "volume", "money", "turnover", "range", "mom20", "mom60", "inst_net"]
        single_ics = {s: [] for s in SIGNALS}
        pair_ics = {p: [] for p in itertools.combinations(SIGNALS, 2)}

        for p in pdates:
            i = idx[p]
            d20 = str(cal[i - 20]) if i - 20 >= 0 else None
            d60 = str(cal[i - 60]) if i - 60 >= 0 else None
            raw = {s: {} for s in SIGNALS}
            for sid in stocks:
                k = (p, sid)
                if k in per: raw["per"][sid] = per[k]
                if k in pbr: raw["pbr"][sid] = pbr[k]
                if k in dy: raw["divyield"][sid] = dy[k]
                if k in fpct: raw["foreign_pct"][sid] = fpct[k]
                if k in marg: raw["margin"][sid] = marg[k]
                if k in shrt: raw["short"][sid] = shrt[k]
                if k in vol: raw["volume"][sid] = vol[k]
                if k in mon: raw["money"][sid] = mon[k]
                if k in tno: raw["turnover"][sid] = tno[k]
                if k in rng_max and k in rng_min and k in adj and adj.get(k):
                    raw["range"][sid] = (rng_max[k] - rng_min[k]) / adj[k] if adj[k] else None
                if d20 and (d20, sid) in adj and k in adj and adj[(d20, sid)] > 0:
                    raw["mom20"][sid] = np.log(adj[k] / adj[(d20, sid)])
                if d60 and (d60, sid) in adj and k in adj and adj[(d60, sid)] > 0:
                    raw["mom60"][sid] = np.log(adj[k] / adj[(d60, sid)])
                if k in inet: raw["inst_net"][sid] = inet[k]

            lab = label.labels(conn, cal[i], stocks, H, calendar=cal)
            if len(lab) < 30:
                continue
            z = {s: _zscore(raw[s]) for s in SIGNALS}
            for s in SIGNALS:
                ic = _spearman(raw[s], lab)
                if ic is not None:
                    single_ics[s].append(ic)
            for a, b in pair_ics:
                if not z[a] or not z[b]:
                    continue
                prod = {sid: z[a][sid] * z[b][sid] for sid in z[a] if sid in z[b]}
                ic = _spearman(prod, lab)
                if ic is not None:
                    pair_ics[(a, b)].append(ic)

    def stat(arr):
        a = np.array(arr)
        return (a.mean(), a.mean() / a.std() * np.sqrt(len(a)) if len(a) > 1 and a.std() > 0 else 0.0, len(a))

    print("— 單欄 cross-sectional rank IC(均、t、panel數)—")
    srows = sorted(((s, *stat(v)) for s, v in single_ics.items() if v), key=lambda r: -abs(r[1]))
    sic = {}
    for s, m, t, n in srows:
        sic[s] = m
        print(f"  {s:14s} IC={m:>+.4f}  t={t:>+5.1f}  ({n} panel)")

    print("\n— 交互(z-乘積)IC top 15、含增量測(交互 vs 成分 max)—")
    prows = sorted(((p, *stat(v)) for p, v in pair_ics.items() if v), key=lambda r: -abs(r[1]))
    print(f"  {'pair':28s} {'IC':>8s} {'t':>6s} {'成分max':>7s} {'增量?':>6s}")
    for (a, b), m, t, n in prows[:15]:
        comp = max(abs(sic.get(a, 0)), abs(sic.get(b, 0)))
        incr = "✅新" if abs(m) > comp * 1.3 and abs(t) > 2 else "冗餘"
        print(f"  {a+'×'+b:28s} {m:>+.4f} {t:>+6.1f} {comp:>7.4f} {incr:>6s}")


if __name__ == "__main__":
    main()
