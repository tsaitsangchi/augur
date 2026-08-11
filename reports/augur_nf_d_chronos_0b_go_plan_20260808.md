---
title: NF-D-CHRONOS-0b go-plan（asof=2026-07-31 · 零默跑）
status: plan_first
series: s4_models
track: NF-D-CHRONOS
date: 2026-08-08
paste: "NF-D-CHRONOS-0b-go-plan | FZ/GATE-keep | asof=2026-07-31 | no-promote | offline-local"
prior_0a: audits/NF-D-CHRONOS-0A-EXECUTED-20260808.md
prior_moirai: audits/NF-D-MOIRAI-0B-EXECUTED-20260808.md
layer: "[I]"
self_reported: true
---

# NF-D-CHRONOS-0b-go-plan｜方向 hit vs naive

> **一句**：比照 Moirai 0b 尺——全 core＠**07-31**／H20 · `log(q50/末價)` 符號 vs naive；**offline-local**；即使有證據亦 **STOP promote**（預凍）。  
> 腳本草案：複用／旁路 `probe_moirai_phase0b` 形態 → `probe_chronos_phase0b.py`（執行時另建）。

## 預凍門

| # | 門 |
|---|---|
| 1 | mean(Chronos hit) **>** mean(naive) → 有證據 |
| 2 | **no-promote**／no-registry／no-serve-swap |
| 3 | `HF_HUB_OFFLINE`／`local_files_only` |

```text
NF-D-CHRONOS-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply
| asof=2026-07-31 | H20 | full-core | offline-local | no-promote | hold-#1
```

*完。*
