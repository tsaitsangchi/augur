---
title: E4 短名單 — canonical 未進 prodset
status: shortlist
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:27+08:00
layer: "[I]"
until: "2026-04-30"
h: 60
first: range_mean_20d
self_reported: true
paste: "E4-shortlist-go | from=canonical-not-prodset | h=60 | until=2026-04-30 | isolation-table | no-promote | no-pay-n"
---

# E4 短名單（≠ 提拔、≠ #14）

> **一句**：31 支 canonical 未進產的欄裡，漏斗就緒 5 支；凍結排序第一支是 **`range_mean_20d`**（2021 在位 Ridge ΔIC +0.0263）。這不是可交易、不是進 prodset。  
> **until／H**：與 E3 同尺（H60、2026-04-30）。panel hash 2014=`01656be2c953f7e0`、2021=`ca1b6ff3791f6f15`。  
> **未做**：寫 staging、改 prodset、付 N、evaluate、救 H20。

## 凍結排序（跑前鎖死）

候選＝E3 同尺 canonical 34 ∖ 現役 3。只讀 `feature_values`（欄已在生產表；**不**為短名單寫 `feature_candidate_values`）。

1. 預診：對現役 3 欄 max |median Spearman ρ| ≥ 0.6 → 墓碑，不當第一。  
2. 單因子 as-of rank IC vs H60；顯著性＝**HAC Eff-t lag=2**，|t|≥2；同號 panel ≥60%。禁裸 iid。  
3. 增量：2021 在位 RankRidge walk-forward（19 折）3+1 vs 3，seed 42；Δ mean IC > 0。  
4. 現役 `removed` 不當第一（不復活）。  
5. 就緒者按 ΔIC 降序，平手看 |HAC t|。

現役 3：`cycle_position_252d`、`inst_cumflow_position_120d`、`lending_fee_rate_mean_30d`。  
prodset-3 在 2021 WF 的 mean rank IC＝**0.0863**（n=19）。單因子 as-of panel＝104（皆有 H60 label）。

## 第一支

**`range_mean_20d`**＝近 20 日 `(high−low)/close` 均值。median IC **−0.0576**（高振幅 → 後續 H60 相對偏弱）、HAC t **−2.136**、同號 62%、ΔIC **+0.0263**（3+1 mean IC 0.1126）、ρmax **0.221**（對 `lending_fee_rate_mean_30d`）。

| 對現役 | |ρ| median |
|---|---|
| `cycle_position_252d` | 0.126 |
| `inst_cumflow_position_120d` | 0.161 |
| `lending_fee_rate_mean_30d` | 0.221 |

**脆點（#15）**：HAC |t| 只剛過 2（iid t=−2.87，正是 G8 會高估的方向）。`volatility_20d` 早因與本欄 +0.94 共線被剪；`volatility_60d` ΔIC +0.018 但 HAC −1.88 **未過** ②，本輪不當第一。

**不是第二支 GO**：`dividend_yield` 同屬就緒，HAC **+3.707**、median IC **+0.102**、ρmax 0.130、ΔIC +0.0214。單因子更穩、增量略低。若 Steward 要較不脆的 ②，下一句改貼它；**一次仍只一支**。

## 就緒 5

| 欄 | median IC | HAC t | 同號 | ΔIC 2021 | ρmax |
|---|---:|---:|---:|---:|---:|
| **range_mean_20d** | −0.0576 | −2.136 | 0.62 | **+0.0263** | 0.221 |
| dividend_yield | +0.1021 | +3.707 | 0.72 | +0.0214 | 0.130 |
| margin_usage_ratio | −0.0642 | −2.713 | 0.68 | +0.0143 | 0.508 |
| pe_ratio | −0.0803 | −3.574 | 0.71 | +0.0055 | 0.083 |
| sbl_short_balance_log | −0.0237 | −2.097 | 0.62 | +0.0022 | 0.255 |

`margin_usage_ratio` ρ=0.508（對借券費），離 0.6 不遠。`pe_ratio` 單因子很強但增量幾乎被 3 欄吃掉。

## 墓碑（不當第一）

**預診 ρ≥0.6**（多半貼著 `cycle_position_252d`）：`momentum_252d`（ΔIC 最高 +0.044 但 ρ=0.70、HAC 1.12）、`momentum_120d`、`momentum_60d`、`price_to_252d_high`、`range_position_120d`、`institutional_net_buy_ratio_20d`、`inst_cumflow_position_60d`、`days_since_high_252d`。

**已 removed**：`top_holders_pct`、`volume_gini_*`、`volume_max_share_*`。`volume_gini_60d` HAC −4.90 仍不復活。

**單因子過 ② 但 2021 ΔIC≤0**（例）：`monthly_revenue_yoy`（HAC +4.32、ΔIC −0.0065）、`gross_margin_pctile`（HAC +2.73、ΔIC −0.011）。

完整 31 列機讀：`reports/augur_econ_e4_shortlist_r17_20260817.json`。

## 隔離／未動

- 未寫 `feature_candidate_values`（既有 819467 列未變用途；本支只讀 `feature_values`）。  
- `evolution_production_feature_set` active 仍 3。  
- `trial_ledger` 仍 32。`econ_eval_run` 仍 9。閘仍 `approved`。  
- H20 `dead`／H60 `thin_unestablished`。IC ≠ 報酬％ ≠ established。

## 下一句（一次一支）

```text
E4-feat-go | candidate=range_mean_20d | isolation-table
```

漏斗 0–4 對**這一支**；#14 只在 0–4 過了才准。仍 no-promote、no-pay-n，除非另句。不要 `E5-evaluate-go`。
