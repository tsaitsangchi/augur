---
status: executed
series: s4_probability
depends_on:
  - audits/P6-REFIT-FREEZE-20260804-GO-20260805.md
  - reports/augur_p6_refit_freeze_20260804_plan_20260805.md
---

# EXECUTED｜P6 REFIT FREEZE→2026-08-04 · H20+H60 · 2026-08-05

> **GO**：`P6-REFIT-FREEZE-2026-08-04-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **self-reported（#32a）**。

## 結果

| 步 | 產出 |
|---|---|
| OOS H20 | **104** 折／**~35k** 列；panel 頂 **2026-06-30**（exit≤07-30） |
| OOS H60 | **102** 折／**34607** 列；panel 頂 **2026-04-30**（exit≤07-29） |
| fit H20 | `platt_RankRidge_h20_asof2026-08-04_g0fb5c95` · Brier **0.2476** vs 0.2500 · ECE 0.0016 · **purge=True** |
| fit H60 | `platt_RankRidge_h60_asof2026-08-04_g0fb5c95` · Brier **0.2452** vs 0.2500 · ECE 0.0076 · **purge=True** |
| emit＠08-04 | H20／H60 各 **204** 檔 → 指向上列新 calibrator |

## 誠實界

- 機率仍貼近 0.5 窄帶（薄 edge）＝預期誠實形，非失敗  
- 未改 dgate／未宣稱確立級  
- 未重訓 RankRidge；DEFAULT_FREEZE 常數未改（CLI `--asof`）

log：`/tmp/p6-refit-20260804/`

*完。*
