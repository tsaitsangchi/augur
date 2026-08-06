---
status: executed
series: s3_graph
date: 2026-08-06
asof: "2026-08-05"
depends_on:
  - audits/GRAPH-REBUILD-20260805-GO-20260806.md
  - audits/GRAPH-REBUILD-20260804-EXECUTED-20260806.md
log: /tmp/graph-commit-0805.log
self_reported: true
---

# EXECUTED｜GRAPH-REBUILD · stock_graph_edge＠2026-08-05

> **GO**：`GRAPH-REBUILD-2026-08-05-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> RC=0 · 寫入 **33,695** 列（core n=285）

| asof | n |
|---:|---:|
| 2026-06-30 | 13,021（保留） |
| 2026-08-04 | 33,513 |
| **2026-08-05** | **33,695**（max） |

**R8-03**：與價／core 頂 **08-05** 對齊 → **關閉**（消費端是否讀新 asof＝另刀）。

*完。*
