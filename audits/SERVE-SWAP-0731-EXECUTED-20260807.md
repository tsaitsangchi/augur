---
status: executed
series: s4_retrain
track: SERVE-SWAP-0731
date: 2026-08-07
viewpoint: 2026-08-07T13:55+08:00
paste: "SERVE-SWAP-0731-go"
go: audits/SERVE-SWAP-0731-GO-20260807.md
retrain: audits/RETRAIN-ASOF-0731-EXECUTED-20260807.md
tip_panel: 2026-08-06
horizons: [20, 40, 60, 82, 120]
logdir: /tmp/serve-swap-0731/
self_reported: true
layer: "[I]"
---

# EXECUTED｜SERVE-SWAP-0731 · tip＝2026-08-06 · 五 horizon

## 護欄
FZ/GATE · no-SIM-apply · 未假 B3＠08-07 · 未改 dgate — **守**。

## 機制
`registry.latest(RankRidge, H, asof≥2026-07-31)` → 0731 產物。  
本 GO＝tip panel **重 predict＋emit**，並清掉同 panel 殘留之 **06-30** pv／pp（避免 emit join 雙 model 撞 PK）。

## tip＠2026-08-06（FINAL）

| H | model_id | econ | n |
|---|---|---|---|
| 20 | `RankRidge_H20_2026-07-31_seed42_56d03625463b3eba` | **dead** | 285 |
| 40 | `RankRidge_H40_2026-07-31_seed42_56d03625463b3eba` | thin_unestablished | 285 |
| 60 | `RankRidge_H60_2026-07-31_seed42_56d03625463b3eba` | thin_unestablished | 285 |
| 82 | `RankRidge_H82_2026-07-31_seed42_56d03625463b3eba` | thin_unestablished | 285 |
| 120 | `RankRidge_H120_2026-07-31_seed42_56d03625463b3eba` | thin_unestablished | 285 |

## 過程誠實
首輪 predict 五窗 OK；emit 因 H20／H60 同 panel 仍留 06-30 列 → UniqueViolation。  
修復：刪 tip 上舊 06-30 pv／pp → 五窗 re-emit **全 OK**（FAIL=0）。

## 後續
- 之後 B3＠新 D（含候中之 08-07）將自動吃 0731（`asof_snapshot≤D`）。  
- 更早 panel（＜07-31）仍可合法指 06-30（PIT）。  
- H20 仍 **econ=dead**（換掛≠修綠）。

*完。[I] serve swapped @ tip 08-06.*
