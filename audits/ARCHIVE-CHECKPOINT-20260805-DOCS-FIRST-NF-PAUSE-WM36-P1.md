---
status: checkpoint
series: archive
depends_on:
  - audits/S4-NF-PAUSE-ACCEPTED-20260805.md
  - audits/WM36-PRICEADJ-P1-EXECUTED-20260805.md
  - audits/LOOP-7-8-GO-ALIGN-DRAFT-20260805.md
---

# ARCHIVE-CHECKPOINT｜docs_first NF-pause + WM36-P1 + LOOP 7/8 draft · 2026-08-05

> **授權**：Steward `archive` → `ARCHIVE-go`（slug=`docs-first-nf-pause-wm36-p1`）。  
> **硬邊界**：本輪碼改僅 WM36 P1 六檔＋書面；**無** β2 `#11`／ARIMA P1／新族 train。  
> **self-reported（#32a）**。

## 1. 納入

| 類 | 路徑 |
|---|---|
| ACCEPT | `audits/S4-NF-PAUSE-ACCEPTED-20260805.md` |
| EXECUTED | `audits/WM36-PRICEADJ-P1-EXECUTED-20260805.md` |
| DRAFT | `audits/LOOP-7-8-GO-ALIGN-DRAFT-20260805.md` |
| plan 對齊 | `reports/augur_s4_next_family_adapter_plan_20260805.md`（nf_pause_accepted） |
| P1 碼 | `scripts/train_direction_stack.py`／`train_direction_threelens.py`／`produce_direction_probability.py`／`build_direction_stack_monthly.py`／`train_daily_direction.py`／`build_daily_direction_features.py` |

## 2. 明確不納／未做

- β2 `#11` 未續；β5 stop 仍有效  
- ARIMA Phase 1 未開  
- LOOP 7／8 僅 GO 對齊草稿，無重訓  
- WM36 P2／vendor baseline 收斂未做  

## 3. 煙測摘要

- P1 六檔 `TaiwanStockPriceAdj` quoted FROM＝**CLEAR**  
- 五支無參數唯讀 OK；`resolve_sql(tw.daily_bar_adjusted)`＋2330 close OK  

## 4. Tag／SHA（已封）

- commit：`ac109e6de88d32a459ef62b35c21291cb11fc232`
- tag：`archive-20260805-docs-first-nf-pause-wm36-p1`
