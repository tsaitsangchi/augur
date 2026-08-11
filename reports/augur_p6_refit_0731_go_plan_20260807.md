---
title: P6-REFIT＠2026-07-31 go-plan（零默 fit）
status: plan_first
series: s4_probability
track: P6-REFIT
date: 2026-08-07
paste: "P6-REFIT-0731-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1"
prior: reports/augur_p6_refit_freeze_20260804_plan_20260805.md
layer: "[I]"
self_reported: true
---

# P6-REFIT-0731-go-plan｜FREEZE→2026-07-31 · H20／H60

> **一句**：把相對機率校準器重 fit 到 **asof=2026-07-31**（先 rebuild OOS sample → `--fit` → 可選 emit）；**⊥日更 B3**；**本檔≠開 fit**。

## 護欄

```text
P6-REFIT-0731-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | hold-#1
# family=RankRidge；horizons=20,60；exit_date>FREEZE 不進 fit
```

## 執行序（另 `P6-REFIT-0731-go`）

1. `build_probability_oos_sample --horizon {20,60} --asof 2026-07-31`  
2. `calibrate_relative_probability --fit --horizon {20,60} --asof 2026-07-31`  
3. 可選 emit＠tip（另句；≠改 dgate）

## Paste

```text
P6-REFIT-0731-plan-adopt | FZ/GATE-keep | no-fit | hold-#1
P6-REFIT-0731-go | FZ/GATE-keep | skip-sync | no-SIM-apply | H=20,60 | asof=2026-07-31 | hold-#1
```

*完。[I]*
