---
status: fired
series: s1s5_loop
track: HIST-RIDGE-WF
product_id: HIST-RIDGE-WF-v1
phase: P2-train-asof-D
date: 2026-08-20
from: "2014-01-02"
log: /tmp/hist-ridge-wf-alldays.log
progress: audits/HIST-RIDGE-WF-ALLDAYS-PROGRESS.json
go: audits/HIST-RIDGE-WF-ALLDAYS-8H-GO-20260820.md
layer: "[I]"
self_reported: true
---

# FIRED｜全交易日 asof=D 八窗

`python scripts/run_hist_ridge_wf_batch.py --all-days --train-predict --apply --from 2014-01-02`

第一日＝2014-01-02。已完成八窗分的日（2014-08-19 等）跳過。
