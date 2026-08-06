---
status: go
series: graph_consume
phase: G1
date: 2026-08-06
viewpoint: 2026-08-06T09:10+08:00
paste: "GRAPH-CONSUME-probe-go | FZ/GATE-keep | skip-sync | read-only"
plan: reports/augur_graph_consume_plan_first_20260806.md
adopted: audits/GRAPH-CONSUME-PLAN-FIRST-ADOPTED-20260806.md
self_reported: true
---

# GO｜GRAPH-CONSUME G1 probe · 2026-08-06

Steward 明示 paste：`GRAPH-CONSUME-probe-go`。

| 允 | 禁 |
|---|---|
| 唯讀 DB：`stock_graph_edge` count／asof／edge_type | 寫庫／rebuild `--commit` |
| 碼樹 grep：src 是否 SELECT 該表 | 改業務碼／adapter／prodset |
| 對照 PriceAdj／core 頂 vs 圖 asof（S-EQ 敘事） | 撤 NF-pause · 改 B3 · sim-apply |

∥ hold #1+#2+#10。
