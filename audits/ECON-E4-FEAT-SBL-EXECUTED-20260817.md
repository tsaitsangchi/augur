---
status: executed
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:42+08:00
go: audits/ECON-E4-FEAT-SBL-GO-20260817.md
fired: audits/ECON-E4-FEAT-SBL-FIRED-20260817.md
report: reports/augur_econ_e4_feat_sbl_short_balance_log_r17_20260817.md
json: reports/augur_econ_e4_feat_sbl_short_balance_log_r17_20260817.json
script: scripts/run_econ_e4_feat_funnel.py
candidate: sbl_short_balance_log
verdict: dead_prediag
died_at: 0
self_reported: true
layer: "[I]"
---

# EXECUTED｜E4 漏斗 `sbl_short_balance_log`

## 判決

**死於 (0) 預診**。vs `turnover_mean_20d` |median ρ|＝**0.758**。未建值、未 #14、未付 N、未提拔。

短名單就緒 5：**三死兩勿送**。canonical-not-prodset 3＋1 路徑無就緒下一支。

## 核對

- trial_ledger=32；active=3；econ_eval_run=9  
- staging 本欄=0；總列 819467  
- 未寫 `feature_values`；verdict 未改

## 下一句

不要再送就緒 5 殘餘。不要 E5／promote／放寬 0.6。另開須新 GO。
