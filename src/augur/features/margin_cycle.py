"""augur 毛利循環相位特徵 — 康波「基本面循環」鏡頭之 C3 存活軸(毛利率自身歷史相位)。

🎯 這支在做什麼(白話):康波 C3＝基本面循環。毛利率會循環(擴張↔壓縮);重點不是絕對毛利率(產業天生高低差、
污染橫斷面),而是「現在毛利率在自身歷史循環的哪裡」。對每股、as-of 面板日 t:
- `gross_margin_pctile`:當季毛利率(單季 GrossProfit/Revenue)在自身**已公告**歷史之百分位(0＝史低、1＝史高)

發布日 gate(#8 命門):財報 `date` 是季底、非公開日 → 用 `release_lag.financial_released` 只取 panel 當下**已公告**者
(季+45/年報+90 日),禁用未公告財報偷看未來。相對化(母原則③):自身百分位、非絕對毛利率。

提拔結論(2026-06-28、過四道漏斗＋#14 經濟＋#15 穩健):公平增量(同宇宙)Ridge+GBDT×H20/60 4格全正;
**Ridge/H60 穩健**(ΔSharpe +0.12/ΔCalmar +0.23、逐期 t=2.05、前後半同向、LOO 不翻負)＝適度真實之長 horizon
基本面分散器(H120 +0.62 Calmar 經穩健測證為部分噪音、不採)。歷史曾因 5 候選綑綁＋增量測覆蓋假象被冤殺、公平重檢翻案。

思想可入、數字不回流(#9):無固定循環長度、相位由自身歷史定義。anti-leakage(#8):只用已公告財報。
source-pure(#1):算不出(已公告歷史 <8 季 / Revenue≤0)→ 缺列。型別 #5。

守 #1 · #8(發布日 gate)· #9(自身相位、無硬編)· #5 · 康波 C3 存活軸 · 母原則③相對化。
"""
from __future__ import annotations

from datetime import date

from augur.features import release_lag

MIN_QUARTERS = 8   # 自身百分位需 ≥8 季已公告歷史(穩健測口徑)

_MARGIN_SQL = (
    'SELECT date, type, value::float8 FROM "TaiwanStockFinancialStatements" '
    "WHERE stock_id=%s AND type IN ('GrossProfit','Revenue') AND date <= %s AND value IS NOT NULL "
    'ORDER BY date'
)


def _gross_margin_pctile(cur, sid, panel_date):
    """當季毛利率在自身已公告歷史之百分位(0-1);已公告 <8 季 / 算不出 → None(#1 缺列)。"""
    cur.execute(_MARGIN_SQL, (sid, panel_date))
    by_date = {}
    for d, t, v in cur.fetchall():
        by_date.setdefault(d, {})[t] = v
    pdt = panel_date if isinstance(panel_date, date) else date.fromisoformat(str(panel_date)[:10])
    margins = []
    for d in sorted(by_date):                                  # 升序 → margins[-1]＝當季
        dd = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
        if not release_lag.financial_released(dd, pdt):        # 發布日 gate:只取已公告(#8)
            continue
        gp, rev = by_date[d].get("GrossProfit"), by_date[d].get("Revenue")
        if gp is not None and rev is not None and rev > 0:
            margins.append(gp / rev)                           # 單季毛利率(GrossProfit/Revenue)
    if len(margins) < MIN_QUARTERS:
        return None
    cur_m = margins[-1]
    return float(sum(1.0 for x in margins if x <= cur_m) / len(margins))


def compute_margin_cycle_features(cur, sid, panel_date):
    """康波 C3 毛利循環相位 → {feature: value};算不出缺列(#1)。"""
    v = _gross_margin_pctile(cur, sid, panel_date)
    return {"gross_margin_pctile": float(v)} if v is not None else {}
