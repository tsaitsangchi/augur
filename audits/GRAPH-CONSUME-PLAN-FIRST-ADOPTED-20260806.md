---
status: adopted
series: graph_consume
open_problem: "r10 #7"
date: 2026-08-06
decided_by: hugo
plan: reports/augur_graph_consume_plan_first_20260806.md
self_reported: true
---

# ADOPTED｜GRAPH-CONSUME-plan-first · 2026-08-06

## Steward 確認（契約要旨）

> 產線意向 **S-EQ**（須有 `asof=D`，否則 SKIP）；禁硬編碼 06-30／無聲明 `MAX(asof)`／讀 `asof>D`；**不**撤 NF-pause、**不**塞進 B3。

```text
GRAPH-CONSUME-plan-first-adopt | FZ/GATE-keep | NF-pause | hold-#1
# S-EQ 產線意向；零改碼本裁；≠ probe／train／B3 改 standing
```

## 生效

| 項 | 裁判 |
|---|---|
| 消費選刀 SSOT | `reports/augur_graph_consume_plan_first_20260806.md` |
| draft＠08-05 | 降為史料 |
| r10 #7 | 📄 plan sealed（adapter／碼仍 🔴 至另 GO） |
| G1 probe／G2 stub／G3 train | **未授**；各須新句 |
| NF-pause／B3 standing | **不變** |

*adopted。*
