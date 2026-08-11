---
status: executed
series: graph_consume
phase: G3
path: A
date: 2026-08-08
viewpoint: 2026-08-08T10:30+08:00
go: audits/GRAPH-G3-HOTPATH-GO-20260808.md
plan: reports/augur_graph_g3_hotpath_go_plan_20260807.md
module: src/augur/features/graph_candidate.py
cli: scripts/build_graph_candidates.py
paste: "GRAPH-G3-HOTPATH-go | path=A | FZ/GATE-keep | NF-pause | hold-#1 | no-train | no-prodset"
self_reported: true
layer: "[I]"
---

# EXECUTED｜GRAPH-G3-HOTPATH path=A · 2026-08-08

```text
GRAPH-G3-HOTPATH-go | path=A | FZ/GATE-keep | NF-pause | hold-#1 | no-train | no-prodset
```

## 交付

| 項 | 值 |
|---|---|
| library | `src/augur/features/graph_candidate.py` |
| CLI | `scripts/build_graph_candidates.py` |
| 名 | `graph_ind_deg_xsec`／`graph_corr60_wdeg_xsec`／`graph_corr60_meanw_xsec` |
| 策略 | G2 **S-EQ**；邊無向展開 → xsec percentile |
| 落表 | **僅** `feature_candidate_values` |
| 熱路徑／prodset／GNN 訓 | **未動** |

## 材料化

| panel | 結果 |
|---|---|
| 2026-06-30 | OK edges=13021 rows=675 |
| 2026-07-31 | OK edges=17296 rows=612 |
| 2026-08-04 | OK edges=33513 rows=849 |
| 2026-08-05 | OK edges=33695 rows=855 |
| 2026-08-06 | OK edges=33622 rows=855 |
| 2026-08-07 | **SKIP `graph_asof_missing`**（誠實；無填舊圖） |

合計寫入 **3,846** 值（每名 1,282 列・`2026-06-30`…`08-06`）。

## 自測／IC

| 測 | 結果 |
|---|---|
| `--selftest` | **全綠**（無向度、xsec、缺圖 raise） |
| as-of IC | 僅 **1** panel 有 H20 label（06-30）：三名 mean_ic≈−0.39／−0.32／−0.16、**HAC n/a**；H60／07-31+ **n/a**（fwd 未齊）→ **不**達提拔門 |

## 不做（本窗兌現）

- `verify_candidate_promotion`／入 `feature_values`／改 prodset  
- RankRidge `--with-graph`（path B）  
- GNN／NF-E 翻案；GRAPH-REBUILD＠08-07  

## 對看板

G1✅／G2 stub ✅／**G3 path=A 候選旁路 ✅**；提拔閘＝另 `VERIFY-go`（證據薄・勿默綠）。NF-pause keep。

*完。[I]*
