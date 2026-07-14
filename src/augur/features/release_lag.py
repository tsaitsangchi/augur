"""augur 發布滯後 gate — 期間型財報/營收之「公開可得日」(#8 anti-leakage 命門)。

🎯 這支在做什麼(白話):財報/月營收的 `date` 是資料期間或公告月、**非精確公開日**——用 date 當 as-of
就是偷看未來。本模組依**台灣法定公告期限**算「公開可得日」,供 builder 以 `release_date ≤ panel_date`
做 point-in-time gate(取代錯誤的 `date ≤ panel`)。

法定期限(保守取上限、資料屆時必已公開):
- **月營收**:`date` 實=**公告月**(資料月+1;DB 實證 474,246/474,246 列 date 恆=資料月+1、如 5 月營收 date=6/1)
  → release = **該公告月 15 日**(法定 10 + buffer、保守;稽核決3 修正 2026-07-04:原誤把 date 當資料月又加次月
  → 過度滯後約一個月、損時效)。
- **財報**:date=季底 → Q1/Q2/Q3 +45 日(法定);**年報(Q4)季底 + 90 日**(次年 3/31)。

思想≠特定值(#9):此處之 10/45/90 非「知識字典閾值」,而是**法律事實**(公告期限)——屬 #8 anti-leakage
之正確 as-of 口徑、非預測用硬編。日期算術、無模型。

**已知潛在缺口(2026-07-10 審計;現況休眠、非急迫)**:財報 lag 一律 45/90 日、無產業別分支;金融保險/
證券/期貨業法定 Q1/Q3 為 **60 日**(證交法 §36 但書),對其低估滯後 → 若消費該類股財報即偏早可見(#8)。
**現況無生產消費者**:唯一消費 `financial_released` 的生產特徵 `gross_margin_pctile`(margin_cycle.py)已因
#15 陳舊守衛排除金融股(其 IFRS 後無 GrossProfit、停於 2010)、且生產 panel 皆季末 → 此缺口目前不觸發。
正解(未來,超出 as-of FREEZE):接真實公告日(TWSE/MOPS)精準 gate,或令 `financial_release_date` 產業感知
(收 stock_id→industry,金融類 Q1/Q3 用 60);屆時須改簽名+穿線全消費者、逐檔驗口徑。**未實作前勿讓 panel
改為季中/月頻消費金融股財報**(會顯現此漏)。
守 #8(anti-leakage:公開可得日 PIT gate、取代錯誤 date≤panel)· #9(10/45/90 為法律事實、非知識字典閾值)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.release_lag              # 印用途+公開入口（唯讀）
  python -m augur.features.release_lag --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from datetime import date, timedelta

REVENUE_DAY = 15          # 月營收次月公告日(法定 10 日 + buffer、保守)
FIN_LAG_QUARTER = 45      # Q1/Q2/Q3 財報:季底後法定天數
FIN_LAG_ANNUAL = 90       # 年報(Q4):季底後法定天數(次年 3/31)
HOLDINGS_LAG_DAYS = 7     # 集保股權分散表(週五快照、TDCC 延後公布):保守 +7 日=次週五必已公開
                          # (2026-07-11 審計 1A 拍板;無發布日欄可查,寧晚勿早 #8;待 probe 公布時刻可精修)


def revenue_release_date(d: date) -> date:
    """月營收 date(實=公告月,資料月+1)→ 公開可得日(**該公告月 15 日**;稽核決3 修正)。
    例:5 月營收 date=6/1 → release=6/15(法定 6/10 + buffer、保守),而非舊誤算之 7/15。"""
    return date(d.year, d.month, REVENUE_DAY)


def financial_release_date(d: date) -> date:
    """財報 date(季底 3/31·6/30·9/30·12/31)→ 公開可得日(年報 +90、其餘 +45 日)。"""
    lag = FIN_LAG_ANNUAL if d.month == 12 else FIN_LAG_QUARTER
    return d + timedelta(days=lag)


def revenue_released(d: date, panel_date: date) -> bool:
    """月營收 d 於 panel_date 是否已公告(可 as-of 使用)。"""
    return revenue_release_date(d) <= panel_date


def financial_released(d: date, panel_date: date) -> bool:
    """財報 d 於 panel_date 是否已公告(可 as-of 使用)。"""
    return financial_release_date(d) <= panel_date


def holdings_release_date(d: date) -> date:
    """集保股權分散快照 date(週五)→ 公開可得日(快照 + 7 日、保守)。"""
    return d + timedelta(days=HOLDINGS_LAG_DAYS)


def holdings_visible_cutoff(panel_date: date) -> date:
    """panel_date 當下「可見」之集保快照上界:snapshot ≤ panel − 7(等價 holdings_release_date ≤ panel;
    供 SQL date <= cutoff 直用)。"""
    p = panel_date if isinstance(panel_date, date) else date.fromisoformat(str(panel_date)[:10])
    return p - timedelta(days=HOLDINGS_LAG_DAYS)


def _selftest():
    """純紅綠自測(零 IO):合成日期→斷言 as-of 口徑不變式(法定期限算術)。"""
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # 月營收:date=公告月(資料月+1)→ 該公告月 15 日(5 月營收 date=6/1 → 6/15)
    chk("revenue_release 6/1→6/15", revenue_release_date(date(2026, 6, 1)) == date(2026, 6, 15))
    chk("revenue_released 邊界(6/15 已公告、6/14 未)",
        revenue_released(date(2026, 6, 1), date(2026, 6, 15))
        and not revenue_released(date(2026, 6, 1), date(2026, 6, 14)))
    # 財報:Q1/Q2/Q3 季底 +45、年報(Q4)季底 +90(次年 3/31)
    chk("financial_release Q1 3/31→+45=5/15", financial_release_date(date(2026, 3, 31)) == date(2026, 5, 15))
    chk("financial_release 年報 12/31→+90=次年3/31", financial_release_date(date(2026, 12, 31)) == date(2027, 3, 31))
    chk("financial_released 邊界(5/15 已、5/14 未)",
        financial_released(date(2026, 3, 31), date(2026, 5, 15))
        and not financial_released(date(2026, 3, 31), date(2026, 5, 14)))
    # 集保:snapshot +7=公開日;cutoff 為其反函式(接受 date 與字串)
    chk("holdings_release +7", holdings_release_date(date(2026, 7, 10)) == date(2026, 7, 17))
    chk("holdings_cutoff date/str 皆 -7",
        holdings_visible_cutoff(date(2026, 7, 17)) == date(2026, 7, 10)
        and holdings_visible_cutoff("2026-07-17") == date(2026, 7, 10))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.features.release_lag --selftest;免 DB 免 API)")
