---
status: executed
series: s1s5_loop
track: HIST-RIDGE-WF
product_id: HIST-RIDGE-WF-v1
date: 2026-08-20
viewpoint: 2026-08-20T10:47+08:00
asof: "2026-07-07"
price_max: "2026-08-19"
rc: 0
elapsed_ms: 258092
n_core: 284
n_tip_core: 285
n_pv_per_h: 284
horizons: [5, 10, 20, 40, 60, 90, 120, 240]
wrote_prediction_values: true
standing_unchanged: true
go: audits/HIST-RIDGE-WF-0707-GO-20260820.md
fired: audits/HIST-RIDGE-WF-0707-FIRED-20260820.md
log: /tmp/hist-ridge-wf-0707.log
plan: reports/augur_hist_ridge_wf_plan_r21_20260820.md
shell: scripts/run_hist_ridge_wf.sh
self_reported: true
layer: "[I]"
---

# EXECUTED｜HIST-RIDGE-WF 第一日＠2026-07-07

`bash scripts/run_hist_ridge_wf.sh --date 2026-07-07 --apply` **RC=0** · **~4.3 min**。

| 步 | 結果 |
|---|---|
| feat | 760 股、27 923 值 |
| core＠07-07 | **284**（增量；公式對表差分∅） |
| core＠08-19 | **285 未變** |
| RankRidge 八窗訓 | H5…H240 皆 `prodset` 3 欄、asof≤07-07 |
| 分數寫庫 | 八窗各 **284** 列 |
| standing | 未改 H20+H60 |
| 08-20 | 未當 as-of |

這是鏈通的第一日，**不是**「已證明 Ridge 池較準」。2014 起仍缺約 **3,005** 個交易日。2000–2013 本槍不做。續跑：`bash scripts/run_hist_ridge_wf.sh --date <下一缺日> --apply`。
