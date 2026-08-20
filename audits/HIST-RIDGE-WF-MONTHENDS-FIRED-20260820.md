---
status: fired
series: s1s5_loop
track: HIST-RIDGE-WF
product_id: HIST-RIDGE-WF-v1
phase: P1-collect
date: 2026-08-20
viewpoint: 2026-08-20T10:56+08:00
asof_first: "2014-01-27"
go: audits/HIST-RIDGE-WF-MONTHENDS-GO-20260820.md
log: /tmp/hist-ridge-wf-monthends-collect.log
layer: "[I]"
self_reported: true
---

# FIRED｜HIST-RIDGE-WF 月尾 P1-collect

`python scripts/run_hist_ridge_wf_batch.py --month-ends --collect-only --apply`

先單日驗證 2014-01-27，再續跑剩餘缺月尾。tip 核心＠08-19 須保持 **285**。
