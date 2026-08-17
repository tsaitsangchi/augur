---
status: go
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:19+08:00
paste: "E4-shortlist-go | from=canonical-not-prodset | h=60 | until=2026-04-30 | isolation-table | no-promote | no-pay-n"
plan: reports/augur_econ_prove_edge_plan_r17_20260817.md
e3: reports/augur_econ_e3_measure_r17_20260817.md
self_reported: true
layer: "[I]"
---

# GO｜E4 短名單（canonical 未進 prodset）

## 准

- 讀 `feature_values`（canonical 已在生產表；**不**新建值、不寫 staging、不寫 prodset）
- until＝2026-04-30、H＝60
- 預診：vs 現役 3 欄 max |median ρ|＜0.6
- 單因子 as-of rank IC + HAC Eff-t（lag＝2）
- 增量：現役 3＋1 vs 3 的 RankRidge walk-forward IC（**2021 在位**，E3 失敗格）
- 排出第一支建議；報告

## 禁

- `PROMOTE-feat-go`／改 `evolution_production_feature_set`
- 寫 `trial_ledger`、經濟終關、evaluate 閘
- 一次多支、救 H20、開 D1 三表、假 B3
