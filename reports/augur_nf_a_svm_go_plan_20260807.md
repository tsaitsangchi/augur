---
title: NF-A-SVM · LinearSVR 族 plan-first（有界撤 pause · H20）
status: adopted
series: s4_models
track: NF-A-SVM
date: 2026-08-07
viewpoint: 2026-08-07T10:45+08:00
paste: "NF-A-SVM-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30 | H20"
prior_eval: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
v2: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
layer: "[I]"
role: A-2b RankSVM H20 有界重驗；08-04 唯一真贏組合；go_now；no-promote-default
self_reported: true
---

# NF-A-SVM-go-plan｜RankSVM · H20 · 2026-08-07

> **Steward**：下一族 → **SVM · H20 go_now**（非 H60）。  
> **誠實先驗**：08-04 為 Wave-A **唯一真贏**（H20 min Sharpe 1.2258＞冠軍 1.1684；hit 持平）；H60 未過。  
> **本窗**：同尺重驗；**仍 no-promote-default**（真贏≠自動換 LIVE）。

```text
NF-A-SVM-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H20 | until=2026-06-30 | no-promote-default
```

| 尺 | 預凍（S5-OOS／EVAL 寫死） |
|---|---|
| H20 冠軍 RankRidge | net Sharpe **1.1684**／hit **0.6393** |
| 升格觸發（僅帳上記） | 三 seed 皆優於門檻且 hit 不劣 — **仍須另句 promote GO** |

*完。[I]*
