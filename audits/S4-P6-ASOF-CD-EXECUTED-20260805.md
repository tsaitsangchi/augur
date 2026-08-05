---
status: executed
series: s4_probability
depends_on:
  - reports/augur_s4_p6_asof_cd_architecture_plan_20260805.md
---

# P6 AS_OF 選項 C／D — 執行帳（2026-08-05）

> **裁示**：Steward「1,2,3,4」採推薦＝**C-param-default-pin ＋ D 紀律句**（不滾動重灌）。  
> **self-reported（#32a）**。

## 完成

| 項 | 結果 |
|---|---|
| `build_probability_oos_sample.py` | `DEFAULT_AS_OF`＋`--asof`（預設 2026-05-31）；docstring D 紀律 |
| `calibrate_relative_probability.py` | `--asof` 同時作 fit FREEZE 上界（預設釘死）；D 紀律 |
| 滾動重灌 | **未做**（須另句） |

## 硬邊界

FZ/GATE-keep · skip-sync · no-SIM-apply · 未改 live 服務 · 未改 DEFAULT 錨值本身之語意（仍 2026-05-31）。
