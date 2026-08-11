---
title: STRUCT-CYCLE-EXPLORE go-plan（零改碼）
status: plan_first
series: infrastructure
track: STRUCT-CYCLE
date: 2026-08-07
paste: "STRUCT-CYCLE-EXPLORE-go-plan | FZ/GATE-keep | zero-code | asof=2026-07-31 | hold-#1"
prior: reports/augur_u0_struct_next_paths_20260804.md
layer: "[I]"
self_reported: true
---

# STRUCT-CYCLE-EXPLORE-go-plan｜循環依賴／結構债 · 唯讀探索

> **一句**：盤點 registry／binding／腳本循環與待出口债（80／97 等），產出 explore 帳；**零 DDL、零 COMMIT、零業務碼**。  
> asof＝文件截止視角 **2026-07-31**（非預測 asof）。

## 護欄

```text
STRUCT-CYCLE-EXPLORE-go-plan | FZ/GATE-keep | zero-code | hold-#1
# ≠ REGISTRY-GO；≠ sunset COMMIT；≠ 改熱路徑
```

## 探索清單（執行 `…-go` 時）

1. 引用環：`world_concept` ↔ scripts ↔ features 入邊出邊表  
2. 殘 U0：binding **80**／**97** 出口狀態一句  
3. `scripts` 冗餘候選（只列表，不刪）→ 可餵 #14  

## Paste

```text
STRUCT-CYCLE-EXPLORE-plan-adopt | FZ/GATE-keep | zero-code | hold-#1
STRUCT-CYCLE-EXPLORE-go | FZ/GATE-keep | zero-code | hold-#1
```

## 可重跑探針（已收成）

```bash
python scripts/explore_struct_cycles.py --selftest
python scripts/explore_struct_cycles.py --run
```

帳：`audits/STRUCT-CYCLE-PROBE-SCRIPT-EXECUTED-20260807.md`

*完。[I]*
