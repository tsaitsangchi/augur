---
title: GRAPH-G3-HOTPATH · 圖消費進熱路徑 go-plan（零默訓）
status: plan_first
series: s3_graph
date: 2026-08-07
paste: "GRAPH-G3-HOTPATH-go-plan | FZ/GATE-keep | NF-pause | hold-#1"
prior_g2: audits/GRAPH-CONSUME-ADAPTER-STUB-EXECUTED-20260807.md
prior_gnn: audits/NF-E-GNN-0B-EXECUTED-20260807.md
layer: "[I]"
self_reported: true
---

# GRAPH-G3-HOTPATH-go-plan｜#7 G3

> **一句**：G2 stub 已可 S-EQ 讀邊；G3＝**是否／如何**讓日更／ranker **可選**消費圖——**預設仍關閉**。  
> NF-E 0b **STOP** → 禁把 G3 當 GNN 翻案升格。

| 路徑草案 | 說明 |
|---|---|
| A 旁路特徵 | graph 聚合→`feature_candidate_values`→提拔閘（長） |
| B 推理旁路 | predict 可選 `--with-graph`（預設 off） |
| C 不接 | 維持唯讀 stub至有證據模型 |

本窗：**只 plan**；執行須 `GRAPH-G3-HOTPATH-go`。

*完。*
