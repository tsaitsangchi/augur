---
status: executed
series: s4_probability
date: 2026-08-08
freeze: "2026-08-07"
depends_on:
  - audits/P6-REFIT-FREEZE-20260807-GO-20260808.md
  - reports/augur_p6_refit_freeze_20260807_plan_20260808.md
log_dir: /tmp/p6-refit-20260807
paste: "P6-REFIT-FREEZE-2026-08-07-go | FZ/GATE-keep | skip-sync | no-SIM-apply | H20+H60"
viewpoint: 2026-08-08T10:02+08:00
self_reported: true
---

# EXECUTED｜P6 REFIT FREEZE→2026-08-07 · H20＋H60

> **GO** 跑完 · `PIPELINE_COMPLETE` · ≠改 dgate · ≠確立級 · ≠換 RankRidge 主模

## 結果

| 步 | 產出 |
|---|---|
| OOS H20 | **104** 折／**35,055** 列 |
| OOS H60 | **102** 折／**34,607** 列 |
| fit H20 | `platt_RankRidge_h20_asof2026-08-07_ga329426` · Brier **0.2476** vs 0.2500 · ECE **0.0016** · purge=True |
| fit H60 | `platt_RankRidge_h60_asof2026-08-07_ga329426` · Brier **0.2452** vs 0.2500 · ECE **0.0076** · purge=True |
| emit＠08-07 | H20／H60 各 **285** 檔 → 上列新 calibrator |

| emit 誠實形 | |
|---|---|
| H20 | p∈[0.413,0.585] · econ=**dead** |
| H60 | p∈[0.373,0.626] · econ=**thin_unestablished** |

## 誠實界

- 與 08-06 P6 數字實質同形（OOS 折／Brier／ECE）——前進 FREEZE 日、校準器 id 換 **asof2026-08-07**  
- 未改 `evaluated_pass`／未宣稱可交易  
- 未重訓 RankRidge 主模型（僅 P6 校準臂）  
- tip serve 模型 id 仍＠**07-31**

log：`/tmp/p6-refit-20260807/pipeline.log`

*完。*
