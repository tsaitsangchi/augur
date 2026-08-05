---
status: executed
series: s4_probability
date: 2026-08-06
D_freeze: "2026-08-04"
horizons: [40, 82, 120]
depends_on:
  - audits/P6-OTHER-H-FIT-20260804-GO-20260805.md
log: /tmp/p6-other-h-20260804/run.log
self_reported: true
---

# EXECUTED｜P6 OTHER-H FIT · H40／H82／H120 · FREEZE asof=2026-08-04

> **GO**：`P6-OTHER-H-FIT-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **窗**：≈2026-08-05 23:46 → 2026-08-06 00:23+08（~37 min）  
> **self-reported（#32a）**。

## 結果

| H | OOS | fit calibrator | Brier vs base | ECE | purge |
|---|---|---|---|---|---|
| **40** | 103 折／34829 列 | `platt_RankRidge_h40_asof2026-08-04_g0fb5c95` | 0.2464 vs 0.2500 | 0.0046 | True |
| **82** | 101 折／34380 列 | `platt_RankRidge_h82_asof2026-08-04_g0fb5c95` | 0.2446 vs 0.2500 | 0.0138 | True |
| **120** | 98 折／33709 列 | `platt_RankRidge_h120_asof2026-08-04_g0fb5c95` | 0.2443 vs 0.2500 | 0.0058 | True |

H20／H60 未重 fit（仍為既有 `…asof2026-08-04…`）。

## 後續｜predict＋emit＠2026-08-05（Steward `predict_emit_0805`）

| H | predict | emit＠08-05 |
|---|---|---|
| **40** | OK · `RankRidge_H40_…2026-06-30…` · 285 列 | OK · 285 · `platt_RankRidge_h40_asof2026-08-04…` · econ=`thin_unestablished` |
| **82** | **BLOCKED** · registry 唯一列＝ghost `GHOST_NO_ARTIFACT` → `latest`＝None | 跳過（pp 仍頂 2026-05-31） |
| **120** | OK · `RankRidge_H120_…2026-06-30…` · 285 列 | OK · 285 · `platt_RankRidge_h120_asof2026-08-04…` · econ=`thin_unestablished` |

log：fit=`/tmp/p6-other-h-20260804/run.log`；emit=`predict_emit_0805.log`／`predict_emit_h120.log`

## 誠實界

- 機率仍可呈 0.5 附近窄帶＝薄 edge 誠實形  
- **未**改 dgate／未宣稱確立級／未 sim-apply／未 train H82  
- H82 要 live 出單須另 GO `train_ranker`（非本刀）

*完。fit ＋ H40／H120＠08-05 emit 關閉；H82 卡 artifact。*
