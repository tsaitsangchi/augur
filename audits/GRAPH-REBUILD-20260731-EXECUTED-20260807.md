---
status: executed
series: s3_graph
date: 2026-08-07
asof: "2026-07-31"
depends_on:
  - audits/GRAPH-REBUILD-20260731-GO-20260807.md
  - audits/NF-E-GNN-PLAN-ADOPTED-20260807.md
log: /tmp/graph-rebuild-0731/commit.log
viewpoint: 2026-08-07T15:56+08:00
self_reported: true
---

# EXECUTED｜GRAPH-REBUILD · stock_graph_edge＠2026-07-31

> **GO**：為 NF-E S-EQ 補圖 · RC=0 · **--commit** · ≠ GNN 訓 · hold-#1  
> 寫入 **17,296** 列（core n=**204**；industry 1,452＋corr60 8,046＋corr120 7,798）

| asof | n |
|---:|---:|
| 2026-06-30 | 13,021 |
| **2026-07-31** | **17,296** |
| 2026-08-04 | 33,513 |
| 2026-08-05 | 33,695 |
| 2026-08-06 | 33,622 |

**S-EQ**：`load_edges(…, 2026-07-31)` → `n=17296` · `graph_asof_missing` **解除**。

下一刀（另句）：`NF-E-GNN-0a-go | …`

*完。*
