---
status: contract_accepted
pack: P2
go: audits/S3-MACRO-STOCK-CONTRACT-v2-P2-GO-20260805.md
date: 2026-08-05
---

# CONTRACT-v2-P2｜壓力／匯率三名

| # | feature | 定義 |
|---|---|---|
| **D** | `beta60_x_hyoas` | β60（同 v1）× `macro_vintage.as_of(BAMLH0A0HYM2, panel)` |
| **E** | `z_vol60_x_vix_chg` | 同 panel z(`volatility_60d`) × (VIX_panel − VIX_prev_panel) |
| **F** | `beta60_x_dextaus_chg` | β60 × (DEXTAUS_panel − DEXTAUS_prev_panel) |

PIT＝`macro_vintage`；缺列不補；候選表 only。
