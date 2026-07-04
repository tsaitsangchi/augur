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
"""
from __future__ import annotations

from datetime import date, timedelta

REVENUE_DAY = 15          # 月營收次月公告日(法定 10 日 + buffer、保守)
FIN_LAG_QUARTER = 45      # Q1/Q2/Q3 財報:季底後法定天數
FIN_LAG_ANNUAL = 90       # 年報(Q4):季底後法定天數(次年 3/31)


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
