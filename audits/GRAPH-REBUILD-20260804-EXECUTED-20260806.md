---
status: executed
series: s3_graph
date: 2026-08-06
asof: "2026-08-04"
depends_on:
  - audits/GRAPH-REBUILD-20260804-GO-20260806.md
log: /tmp/graph-commit-0804.log
self_reported: true
---

# EXECUTED｜GRAPH-REBUILD · stock_graph_edge＠2026-08-04

> **GO**：`GRAPH-REBUILD-2026-08-04-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **窗**：≈08:26:33+08 · RC=0  

## 結果

| asof | 邊合計 | industry_same | corr_60d | corr_120d |
|---|---:|---:|---:|---:|
| **2026-08-04**（新） | **33,513** | 3,006 | 15,724 | 14,783 |
| 2026-06-30（保留） | 13,021 | 1,831 | 5,089 | 6,101 |

核心＠08-04＝**283**；WM.36 經 `tw.daily_bar_adjusted`／`tw.stock_industry_category`。

## 誠實界

- `industry_same`＝最新產業分類（非嚴格 PIT；與腳本標頭一致）  
- `return_corr_*`＝`date<=as_of` 嚴格  
- **未**寫 08-05；**未**改消費端 adapter；**未**撤 NF  

## 開債

- R8-03：06-30 錯位 **緩解**（max asof→08-04）；若要對齊最新價 D＝08-05 須另 GO  

*完。*
