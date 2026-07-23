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
source-pure(#1):算不出(已公告歷史 <8 季 / Revenue≤0 / 當季毛利陳舊 >400 日 #15)→ 缺列。型別 #5。

守 #1 · #8(發布日 gate)· #9(自身相位、無硬編)· #5 · 康波 C3 存活軸 · 母原則③相對化。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.margin_cycle              # 印用途+公開入口（唯讀）
  python -m augur.features.margin_cycle --selftest   # 純紅綠自測（零 IO：假 cursor 驅動 pctile 邏輯）
"""
from __future__ import annotations

from datetime import date

from augur.features import release_lag

MIN_QUARTERS = 8   # 自身百分位需 ≥8 季已公告歷史(穩健測口徑)
MAX_STALE_DAYS = 400   # #15 陳舊守衛:最新已公告毛利季須離 panel ≤400 日(≈4 季+緩衝);否則「當季」實為
                       # 停報之陳舊值(如保險業 IFRS 後無 GrossProfit、停於 2010),不得冒充當季 → 缺列

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
    last_q = None                                              # 最新已公告毛利季之季底日(陳舊守衛用)
    for d in sorted(by_date):                                  # 升序 → margins[-1]＝當季
        dd = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
        if not release_lag.financial_released(dd, pdt):        # 發布日 gate:只取已公告(#8)
            continue
        gp, rev = by_date[d].get("GrossProfit"), by_date[d].get("Revenue")
        if gp is not None and rev is not None and rev > 0:
            margins.append(gp / rev)                           # 單季毛利率(GrossProfit/Revenue)
            last_q = dd
    if len(margins) < MIN_QUARTERS:
        return None
    if last_q is None or (pdt - last_q).days > MAX_STALE_DAYS:  # #15:當季毛利已陳舊(停報)→ 不冒充當季、缺列
        return None
    cur_m = margins[-1]
    return float(sum(1.0 for x in margins if x <= cur_m) / len(margins))


def compute_margin_cycle_features(cur, sid, panel_date):
    """康波 C3 毛利循環相位 → {feature: value};算不出缺列(#1)。"""
    v = _gross_margin_pctile(cur, sid, panel_date)
    return {"gross_margin_pctile": float(v)} if v is not None else {}


def _selftest():
    """自測（零 DB/零 API #29a）：以假 cursor 驅動真 pctile 邏輯 + 純日期 gate，紅綠鎖核心不變式——
    自身百分位、發布日 gate 排未公告(#8)、<8 季/當季陳舊>400 日缺列(#1/#15)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    class _Cur:                                   # 假 cursor:純記憶體、零 IO(不觸 DB)
        def __init__(self, rows): self._rows = rows
        def execute(self, *a): pass
        def fetchall(self): return self._rows

    def _rows(pairs):                             # (季底日, 毛利率)→ (date,type,value) 列;Revenue 固定 100
        out = []
        for d, m in pairs:
            out.append((d, "GrossProfit", m * 100.0))
            out.append((d, "Revenue", 100.0))
        return out

    def eq(a, b):
        return a is not None and abs(a - b) < 1e-9

    q8 = [date(2023, 12, 31), date(2024, 3, 31), date(2024, 6, 30), date(2024, 9, 30),
          date(2024, 12, 31), date(2025, 3, 31), date(2025, 6, 30), date(2025, 9, 30)]
    panel = date(2025, 12, 31)                    # Q3/2025 已公告(+45<panel)、離 panel 92 日(未陳舊)
    asc = list(zip(q8, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]))   # 當季(末季)=史高

    chk("當季=史高→pctile 1.0", eq(_gross_margin_pctile(_Cur(_rows(asc)), "1234", panel), 1.0))

    cmin = list(zip(q8, [0.5, 0.6, 0.7, 0.8, 0.9, 0.4, 0.3, 0.2]))  # 當季(末季)=0.2=史低
    chk("當季=史低→pctile 0.125", eq(_gross_margin_pctile(_Cur(_rows(cmin)), "1234", panel), 0.125))

    chk("已公告 <8 季→缺列 None", _gross_margin_pctile(_Cur(_rows(asc[:7])), "1234", panel) is None)

    chk("當季陳舊 >400 日→缺列 None(#15)",
        _gross_margin_pctile(_Cur(_rows(asc)), "1234", date(2027, 6, 30)) is None)

    leak = asc + [(date(2025, 12, 31), 0.05)]     # 未公告 Q4/2025(release 2026-03-31>panel)+極端值
    chk("未公告財報被 gate 排除(#8;混入不改結果)",
        eq(_gross_margin_pctile(_Cur(_rows(leak)), "1234", panel), 1.0))

    chk("compute 可算→{'gross_margin_pctile': v}",
        compute_margin_cycle_features(_Cur(_rows(asc)), "1234", panel) == {"gross_margin_pctile": 1.0})
    chk("compute 算不出→{}(缺列)",
        compute_margin_cycle_features(_Cur(_rows(asc[:7])), "1234", panel) == {})

    chk("常數 MIN_QUARTERS=8 / MAX_STALE_DAYS=400", MIN_QUARTERS == 8 and MAX_STALE_DAYS == 400)
    chk("SQL 讀財報表 + GrossProfit/Revenue",
        "TaiwanStockFinancialStatements" in _MARGIN_SQL
        and "GrossProfit" in _MARGIN_SQL and "Revenue" in _MARGIN_SQL)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("入口:compute_margin_cycle_features(cur, sid, panel_date)")
    print("(自測:python -m augur.features.margin_cycle --selftest;免 DB 免 API)")
