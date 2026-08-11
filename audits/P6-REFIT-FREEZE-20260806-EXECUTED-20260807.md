---
status: executed
series: s4_probability
date: 2026-08-07
freeze: "2026-08-06"
depends_on:
  - audits/P6-REFIT-FREEZE-20260806-GO-20260807.md
  - reports/augur_p6_refit_freeze_20260806_plan_20260807.md
log_dir: /tmp/p6-refit-20260806
paste: "P6-REFIT-FREEZE-2026-08-06-go | FZ/GATE-keep | skip-sync | no-SIM-apply | H20+H60"
viewpoint: 2026-08-07T20:50+08:00
self_reported: true
---

# EXECUTED｜P6 REFIT FREEZE→2026-08-06 · H20＋H60

> **GO** 已跑完 · `PIPELINE_COMPLETE` · hold-#1（A＠08-07 仍 WAIT）· ≠改 dgate · ≠確立級

## 結果

| 步 | 產出 |
|---|---|
| OOS H20 | **104** 折／**35,055** 列（panel 頂可用至 **2026-06-30**／exit≤07-30） |
| OOS H60 | **102** 折／**34,607** 列（panel 頂可用至 **2026-04-30**／exit≤07-29） |
| fit H20 | `platt_RankRidge_h20_asof2026-08-06_ga329426` · Brier **0.2476** vs 0.2500 · ECE **0.0016** · purge=True |
| fit H60 | `platt_RankRidge_h60_asof2026-08-06_ga329426` · Brier **0.2452** vs 0.2500 · ECE **0.0076** · purge=True |
| emit＠08-06 | H20／H60 各 **285** 檔 → 上列新 calibrator |

| emit 誠實形 | |
|---|---|
| H20 | p∈[0.413,0.585] · econ=**dead** |
| H60 | p∈[0.373,0.626] · econ=**thin_unestablished** |

## 誠實界

- 機率仍貼近 0.5 窄帶＝預期；非失敗  
- 未改 `evaluated_pass`／未宣稱可交易  
- 未重訓 RankRidge 主模型（僅 P6 校準臂）  
- #1 watcher 仍候 PriceAdj≥08-07  

log：`/tmp/p6-refit-20260806/`

*完。*
