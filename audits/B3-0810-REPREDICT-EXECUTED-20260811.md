---
status: executed
series: daily_asof
date: 2026-08-11
viewpoint: 2026-08-11T08:30+08:00
go: audits/B3-0810-REPREDICT-GO-20260811.md
log: /tmp/retrain-asof-0810/repredict.log
reemit: /tmp/retrain-asof-0810/reemit.log
paste: "B3-0810-repredict-EXECUTED | Ridge@2026-08-10 | H20/60 | emit-fixed-latest-asof"
self_reported: true
layer: "[I]"
---

# EXECUTED｜B3 repredict＠08-10 · 新 Ridge

## 結果

| 步 | 結果 |
|---|---|
| predict H20 | `RankRidge_H20_2026-08-10_seed42_56d03625463b3eba` · 285 列 · top1=2330 |
| predict H60 | `RankRidge_H60_2026-08-10_…` · 285 列 · top1=2301 |
| emit（首輪） | **FAIL** UniqueViolation（同 panel 0731+0810 雙 model 混 emit） |
| 碼修 | `calibrate_relative_probability.emit_horizon`：只取 **max(asof_snapshot)** 那槍 |
| emit（重跑） | H20／H60 **RC=0** · 285 檔 · 掛 **08-10** model_id |

## 殘

`prediction_values`／`prediction_probability` 於 08-10 仍保留 0731 歷史列（並行）；新服務路徑以最新 asof 為準。可另清理 GO。

*完。*
