---
title: E4 漏斗墓碑 — sbl_short_balance_log
status: dead_prediag
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:42+08:00
layer: "[I]"
candidate: sbl_short_balance_log
died_at: 0
until: "2026-04-30"
h: 60
self_reported: true
paste: "E4-feat-go | candidate=sbl_short_balance_log | isolation-table"
---

# 墓碑｜`sbl_short_balance_log`（死於漏斗 0 預診）

> **一句**：對現役 3 欄可過（ρmax 0.255），對 canonical 是規模／周轉重編碼——vs `turnover_mean_20d` **|median ρ|=0.758**。未建值、未 #14、未付 N、未提拔。  
> **短名單就緒 5 已耗盡**：三支實跑全死於 (0)；其餘兩支（`pe_ratio`、`margin_usage_ratio`）已被對稱 ρ 暗示死亡，**不要再送**。

## 死點

漏斗 **(0) 預診**。until／H／hash 與前兩墓碑同尺。不放寬 0.6。

| 對照 | max \|median ρ\| | 最近鄰 | 判 |
|---|---:|---|---|
| 現役 3 | 0.255 | `lending_fee_rate_mean_30d` | 過 |
| canonical\{自己} | **0.758** | **`turnover_mean_20d`** | **死** |

canonical 最近 5：

| 欄 | \|median ρ\| |
|---|---:|
| `turnover_mean_20d` | **0.758** |
| `market_cap_log` | **0.732** |
| `dollar_volume_log_20d` | **0.704** |
| `foreign_holding_pct` | 0.557 |
| `volume_gini_60d` | 0.345 |

現役 3：`cycle_position_252d` 0.123／`inst_cumflow_position_120d` 0.075／`lending_fee_rate_mean_30d` 0.255。

借券餘額 log 在 34 欄裡跟周轉／市值／成交額同一捆（稀疏籌碼 E 類的已知偏 size），不是新軸。

## 後續道次

未跑。(1) 未寫（staging 本欄 0→0）。(2)(3)(4)(5) 停。`trial_ledger` 仍 32。prodset 仍 3。`econ_eval_run` 仍 9。

機讀：`reports/augur_econ_e4_feat_sbl_short_balance_log_r17_20260817.json`。

## 就緒 5 結案

| 欄 | 對 canonical | 漏斗 (0) |
|---|---|---|
| `range_mean_20d` | `volatility_60d` 0.901 | **已死** |
| `dividend_yield` | `pe_ratio` 0.616 | **已死** |
| `sbl_short_balance_log` | `turnover_mean_20d` 0.758 | **已死** |
| `pe_ratio` | `dividend_yield` 0.616 | 預期死 · **勿送** |
| `margin_usage_ratio` | `range_mean_20d` 0.605 | 預期死 · **勿送** |

E3 的「34 欄翻 2021 在位」是**捆**的效果，不是「從 31 欄抽一支加進現役 3 欄」。把 canonical 倒進 prodset 仍禁。不要從短名單 WAIT／預診失敗列再挑一支碰運氣（那些不是 HAC 不足、就是 ΔIC≤0、就是 ρ 更高）。

## 下一句

本路徑（canonical-not-prodset、一次一支、現役 3＋1）**沒有就緒下一支**。不要 `E5-evaluate-go`。不要放寬 0.6。不要 `PROMOTE-feat-go`。

若要另開，須新 GO，且角度須新（不是這 31 欄的族內重編碼），例如另點名的新候選或 E4b live OOS 鐘。本支不預跑。
