---
title: STRUCT-CYCLE-BREAK go-plan（零默改碼）
status: plan_first
series: struct
date: 2026-08-08
paste: "STRUCT-CYCLE-BREAK-go-plan | FZ/GATE-keep | zero-code-default"
prior: audits/STRUCT-CYCLE-EXPLORE-EXECUTED-20260807.md
layer: "[I]"
self_reported: true
---

# STRUCT-CYCLE-BREAK-go-plan

> **一句**：EXPLORE 已列 5 個 2-cycles → 本刀＝**斷環策略 plan**（優先級／邊界／每輪一環）；**預設零改碼**直至另 `STRUCT-CYCLE-BREAK-go` 明示單環。

## 建議順位（草案）

| 順位 | 環 | 理由 |
|---:|---|---|
| 1 | `audit` ↔ `core` | 基礎設施；影響面可測 |
| 2 | `audit` ↔ `features` | 特徵建置 |
| 3 | `advisor` ↔ `deliberation`／`knowledge` | 應用層；可後置 |

## 護欄

- 每 GO **一環**；可編譯／import 煙測  
- **禁**一次清多環；**禁**默動 `predict_asof`／B3／serve  
- 長環（audit→catalog→core）另帳

```text
STRUCT-CYCLE-BREAK-plan-adopt | FZ/GATE-keep | zero-code-default
STRUCT-CYCLE-BREAK-go | ring=audit-core | …   # 另授
```

*完。*
