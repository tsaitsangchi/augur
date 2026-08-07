---
title: NF-A-CAT · CatBoost 族 plan-first（有界撤 pause）
status: adopted
series: s4_models
track: NF-A-CAT
date: 2026-08-07
viewpoint: 2026-08-07T10:40+08:00
paste: "NF-A-CAT-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30"
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
v2: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
prior_eval: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
prior_xgb: audits/NF-A-XGB-EXECUTED-20260807.md
layer: "[I]"
role: A-3c RankCat 有界解凍；碼已在、前評未過門；go_now
self_reported: true
---

# NF-A-CAT-go-plan｜RankCat（CatBoost）· 2026-08-07

> **Steward**：下一族再開 → **Cat · go_now**。  
> **一句**：僅 **`RankCat`** 歷史 prodset 訓／#14；其他族 NF-pause **keep**；**no-promote-default**。  
> **誠實**：`ranker.RankCat` 已在；08-04 H60 min≈1.0049 ≪ 冠軍 1.3016。

```text
NF-A-CAT-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default
```

| 尺 | 預凍 |
|---|---|
| H60 冠軍 | Sharpe **1.3016**／hit **0.6316** |
| 升格 | 三 seed 皆優於門檻且 hit 不劣——否則 STOP |

*完。[I]*
