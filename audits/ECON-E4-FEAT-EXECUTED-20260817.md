---
status: executed
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:32+08:00
go: audits/ECON-E4-FEAT-GO-20260817.md
fired: audits/ECON-E4-FEAT-FIRED-20260817.md
report: reports/augur_econ_e4_feat_range_mean_20d_r17_20260817.md
json: reports/augur_econ_e4_feat_range_mean_20d_r17_20260817.json
script: scripts/run_econ_e4_feat_funnel.py
candidate: range_mean_20d
verdict: dead_prediag
died_at: 0
self_reported: true
layer: "[I]"
---

# EXECUTED｜E4 漏斗 `range_mean_20d`

## 判決

**死於 (0) 預診**。vs `volatility_60d` |median ρ|＝**0.901** ≥ 0.6。未建值、未 #14、未付 N、未提拔。

## 核對

- trial_ledger=32；active=3；econ_eval_run=9  
- staging 本欄=0；總列 819467 未清別人  
- 未寫 `feature_values`；verdict 未改

## 下一句（另貼才跑）

`E4-feat-go | candidate=dividend_yield | isolation-table`  
或停。不要 evaluate／promote。
