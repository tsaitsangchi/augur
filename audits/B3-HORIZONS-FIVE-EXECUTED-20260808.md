---
status: executed
series: daily_b3
track: B3-HORIZONS-FIVE
date: 2026-08-08
tip: "2026-08-07"
horizons: [20, 40, 60, 82, 120]
depends_on:
  - audits/B3-HORIZONS-FIVE-GO-20260808.md
  - audits/SERVE-FIVE-H-GO-20260808.md
log: /tmp/b3-five-0807/phase.log
paste: "B3-HORIZONS-FIVE-go | tip=2026-08-07 | horizons=20,40,60,82,120 | hold-#1"
paired_exec: audits/SERVE-FIVE-H-EXECUTED-20260808.md
viewpoint: 2026-08-08T19:26+08:00
self_reported: true
---

# EXECUTED｜B3-HORIZONS-FIVE · tip＝2026-08-07（A）

> RC=0 · `run_daily_asof_predict.sh --date 2026-08-07 --horizons 20,40,60,82,120` · accept 2330@H20＝tip  
> **與 B 同窗同 log**（一跑雙交）。

## 結果

| H | emit n | econ | calibrator |
|---:|---:|---|---|
| 20 | 285 | **dead** | `platt_*_asof2026-08-07_*` |
| 40 | 285 | thin_unestablished | `platt_*_asof2026-08-04_*`（誠實：非 08-07 P6） |
| 60 | 285 | thin_unestablished | `platt_*_asof2026-08-07_*` |
| 82 | 285 | thin_unestablished | `platt_*_asof2026-08-04_*` |
| 120 | 285 | thin_unestablished | `platt_*_asof2026-08-04_*` |

feat／core＠tip **SKIP**（已有）。standing 預設 `HORIZONS=20,60` **未改**。

*完。≠修綠／≠改 dgate／≠升格。*
