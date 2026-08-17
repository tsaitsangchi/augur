---
title: E4 可點名「真名」誠實卡 — 沒有最佳剩餘 3＋1
status: honesty
series: econ_establishment
round: r18
date: 2026-08-17
viewpoint: 2026-08-17T10:59+08:00
layer: "[I]"
depends_on:
  - reports/augur_econ_e4_shortlist_r17_20260817.md
  - reports/taiwan_alpha_improvement_plan_20260717.md
self_reported: true
---

# E4「真名有哪些最佳」誠實卡（2026-08-17）

> **一句**：能直接貼進 `E4-feat-go` 的庫內欄裡，**沒有最佳剩餘**。短名單就緒 5 已耗盡。期望值最高的下一族是 **D1 財務三表複合異象**，但那些名字**還不在** `feature_values`，現在貼會空跑。  
> 本檔＝答詢，**不是** GO。未跑漏斗。

`E4-feat-go` 現役腳本只吃 `feature_values` 已有欄（再拷進隔離表）。08-14 生產表＝**37** 欄。

## 1. 不要貼（已死／暗示死／鎖）

| 真名 | 為什麼 |
|---|---|
| `range_mean_20d` | 漏斗 (0) 死；vs `volatility_60d` ρ=0.901 |
| `dividend_yield` | 漏斗 (0) 死；vs `pe_ratio` ρ=0.616 |
| `sbl_short_balance_log` | 漏斗 (0) 死；vs `turnover_mean_20d` ρ=0.758 |
| `pe_ratio` | 與股利對稱，暗示死；勿送 |
| `margin_usage_ratio` | vs `range_mean_20d` ρ=0.605；勿送 |
| 動能／位置族 | vs 現役 `cycle_position_252d` ρ≥0.6：`momentum_252d/120d/60d`、`price_to_252d_high`、`range_position_120d`、`days_since_high_252d`、`institutional_net_buy_ratio_20d`、`inst_cumflow_position_60d` |
| `monthly_revenue_yoy`、`gross_margin_pctile` | HAC 過、2021 ΔIC≤0 |
| `top_holders_pct`、`volume_gini_*`、`volume_max_share_*` | 已 removed；不復活 |
| `debt_ratio`、`gov_bank_net_buy_60d` | 歷史 removed／D2 半墓碑；不復活 |
| HAC／同號未過的其餘 canonical | 釣魚；OPT-R18 鎖 `no-canonical-3plus1` |

E3「34 欄翻盤」是**捆**，不是抽一支加進現役 3。

## 2. 庫內唯一還沒進短名單的欄（≠最佳）

**`roe`**：08-14 有值（753 列），不在 canonical 34、不在就緒 5。  
同屬獲利能力，近親 `gross_margin_pctile` 已 ΔIC **−0.011**。這不是「最佳真名」，只是「還沒送過的既有欄」。要送須 Steward **具名**，並接受很可能死於 (0) 或 (4)。

現役 3 不要送：`cycle_position_252d`、`inst_cumflow_position_120d`、`lending_fee_rate_mean_30d`。

## 3. 期望值最高、但現在不是 E4-feat-go 真名

依已採納 `taiwan_alpha_improvement_plan_20260717.md` **D1**（相對最高；預期 0–2/6 族存活，不是大概率成功）。特徵層目前**零使用**，須先建值（staging），才有可點名的欄：

| 族（計畫用語，非庫欄） | 現在能 `E4-feat-go`？ |
|---|---|
| asset growth | **否**（未建） |
| accruals（盈餘−營運現金流） | **否** |
| NOA | **否** |
| FCF yield | **否** |
| net issuance | **否** |
| capex 成長 | **否** |

前置：BalanceSheet 缺季、CashFlows YTD 去累計、金融股 60 日 `release_lag`（D1∧P6）。另 GO，不是本句漏斗。

D2 法人 name 維度：C-M3 降評；無「與死者的新角度差異」書面者不進。D3 漲跌停／D4 約束**事件**（≠借券水位重掃）同理：先建值才有真名。

## 4. 若仍要貼 E4-feat-go

只接受**無角括號的庫內欄名**，一次一支。本檔**不代填、不推薦**從 §1 再抽。全專案主軸仍是 M1b WAIT；本路徑機械下一槍仍是 E4b 鐘。
