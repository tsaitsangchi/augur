---
status: executed
series: s3_graph
date: 2026-08-08
asof: "2026-08-07"
viewpoint: 2026-08-08T15:15+08:00
go: audits/GRAPH-REBUILD-20260807-GO-20260808.md
log: /tmp/graph-rebuild-0807/commit.log
paste: "GRAPH-REBUILD-2026-08-07-go | FZ/GATE-keep | skip-sync | no-SIM-apply | --commit | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜GRAPH-REBUILD · stock_graph_edge＠2026-08-07

```text
GRAPH-REBUILD-2026-08-07-go | FZ/GATE-keep | skip-sync | no-SIM-apply | --commit | hold-#1
```

## 寫側

| 項 | 值 |
|---|---|
| script | `build_stock_graph_edges.py --asof 2026-08-07 --commit` |
| core | **285** |
| industry_same | 3,036 |
| return_corr_60d | 16,113 |
| return_corr_120d | 14,418 |
| **合計寫入** | **33,567** |

## S-EQ／G3 旁路接線

| 測 | 結果 |
|---|---|
| `graph_consume --probe-asof 2026-08-07` | **n=33567** · S-EQ ok（先前 `graph_asof_missing` **解除**） |
| `graph_candidate`＠08-07 | **855** 列（三名×285）；候選 max 升至 **08-07** |

## 不做

- GNN／產線熱路徑開圖；提拔閘；SIM-apply；B3／serve  

*完。[I]*
