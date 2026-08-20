---
status: executed
series: s1s5_loop
track: HIST-RIDGE-WF
product_id: HIST-RIDGE-WF-v1
phase: P1-collect
date: 2026-08-20
viewpoint: 2026-08-20T11:00+08:00
asof: "2014-01-27"
price_max: "2026-08-19"
rc: 0
n_core: 477
n_tip_core: 285
n_feat_values: 27119
n_roster: 760
standing_unchanged: true
go: audits/HIST-RIDGE-WF-MONTHENDS-GO-20260820.md
fired: audits/HIST-RIDGE-WF-MONTHENDS-FIRED-20260820.md
plan: reports/augur_hist_ridge_wf_plan_r21_20260820.md
shell: scripts/run_hist_ridge_wf_batch.py
self_reported: true
layer: "[I]"
---

# EXECUTED｜月尾 P1-collect 首日＠2014-01-27

`run_hist_ridge_wf_batch.py --month-ends --collect-only --apply --limit 1` **RC=0** · **~60 s**。

| 步 | 結果 |
|---|---|
| feat＠01-27 | 760 股、27 119 值 |
| core＠01-27 | **477**（當時只有 1 片 since-2014 panel，完整度較寬） |
| core＠08-19 | **285 未變** |
| 訓／分 | 跳過（P1-collect） |
| standing | 未改 |

2014-01 以前沒有 PIT 核心，本月尾**不能**誠實訓八窗。剩餘缺月尾約 **87** 日續跑 collect。
