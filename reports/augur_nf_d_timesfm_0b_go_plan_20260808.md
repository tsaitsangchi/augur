---
title: NF-D-TIMESFM-0b go-plan（asof=2026-07-31 · 零默升格）
status: plan_first
series: s4_models
track: NF-D-TIMESFM
date: 2026-08-08
paste: "NF-D-TIMESFM-0b-go-plan | FZ/GATE-keep | asof=2026-07-31 | no-promote | offline-local"
prior_0a: audits/NF-D-TIMESFM-0A-EXECUTED-20260808.md
prior_chronos: audits/NF-D-CHRONOS-0B-EXECUTED-20260808.md
layer: "[I]"
self_reported: true
---

# NF-D-TIMESFM-0b-go-plan｜方向 hit vs naive · NaN 先決

> **一句**：比照 Chronos／Moirai 0b 尺——全 core＠**07-31**／H20 · `log(q50/末價)` 符號 vs naive；**offline-local**；即使有證據亦 **STOP promote**。  
> **先決（0a 殘差）**：真載 `forecast` **非 NaN 覆蓋率** 過門；否則整輪 **誠實 SKIP／STOP**（≠塗綠 stub）。

## 預凍門

| # | 門 |
|---|---|
| 0 | 預熱／樣本 fold：finite 分數覆蓋率 **≥** 門檻（預設 0.5）→ 否則 STOP／SKIP |
| 1 | mean(TimesFM hit) **>** mean(naive) → 有證據 |
| 2 | **no-promote**／no-registry／no-serve-swap |
| 3 | `HF_HUB_OFFLINE`／`local_files_only`；≠ hub 下載 |

```text
NF-D-TIMESFM-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply
| asof=2026-07-31 | H20 | full-core | offline-local | no-promote | hold-#1
# 先決：forecast 非 NaN 覆蓋率 gate；否則 STOP／SKIP
```

腳本：`scripts/probe_timesfm_phase0b.py`

*完。[I]*
