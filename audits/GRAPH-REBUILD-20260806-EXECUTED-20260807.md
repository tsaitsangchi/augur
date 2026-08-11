---
status: executed
series: s3_graph
date: 2026-08-07
asof: "2026-08-06"
depends_on:
  - audits/GRAPH-REBUILD-20260806-GO-20260807.md
log: /tmp/graph-rebuild-0806/commit.log
viewpoint: 2026-08-07T14:10+08:00
self_reported: true
---

# EXECUTED｜GRAPH-REBUILD · stock_graph_edge＠2026-08-06

> **GO**：`GRAPH-REBUILD-2026-08-06-go | FZ/GATE-keep | skip-sync | no-SIM-apply | --commit`  
> RC=0 · 寫入 **33,622** 列（core n=285；industry 3,019 + corr60 16,101 + corr120 14,502）

| asof | n |
|---:|---:|
| 2026-06-30 | 13,021（保留） |
| 2026-08-04 | 33,513 |
| 2026-08-05 | 33,695 |
| **2026-08-06** | **33,622**（max＝價／core 頂） |

**S-EQ probe**：`load_edges(…, 2026-08-06)` → `n=33622` · `graph_asof=2026-08-06`（先前 `graph_asof_missing` **解除**）。

**Hard doors**：#1 hold｜≠ B3／訓／SIM-apply｜≠ 自動 G3／GNN。

*完。*
