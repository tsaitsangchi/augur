---
status: executed
series: graph_consume
phase: G2
date: 2026-08-07
viewpoint: 2026-08-07T14:10+08:00
paste: "GRAPH-CONSUME-adapter-stub-go | FZ/GATE-keep | NF-pause | hold-#1"
go: audits/GRAPH-CONSUME-ADAPTER-STUB-GO-20260807.md
plan: reports/augur_graph_consume_plan_first_20260806.md
module: src/augur/features/graph_consume.py
asof_strategy: S-EQ
self_reported: true
layer: "[I]"
---

# EXECUTED｜GRAPH-CONSUME G2 adapter stub · 2026-08-07

```text
GRAPH-CONSUME-adapter-stub-go | FZ/GATE-keep | NF-pause | hold-#1 | no-train
```

## 交付

| 項 | 值 |
|---|---|
| 模組 | `src/augur/features/graph_consume.py` |
| 策略 | **S-EQ**（圖 asof ≡ 讀者 D） |
| 邊型（實名） | `industry_same`／`return_corr_60d`／`return_corr_120d` |
| API | `load_edges`／`load_edges_seq`／`neighbor_map`／失敗碼例外 |
| 掛 B3／train | **無** |
| NF-pause | **keep** |

## 驗收

| 測 | 結果 |
|---|---|
| `--selftest` | **全綠**（missing／leakage／undeclared／empty） |
| `--probe-asof 2026-08-05` | **n=33695** S-EQ ok |
| `--probe-asof 2026-08-06` | **SKIP `graph_asof_missing`**（預期：圖尚未 rebuild＠08-06） |

## 不做

- GNN／Rank 族訓練；改 prodset；塞進 `run_daily_asof_predict`  
- 假綠塗 08-06 S-EQ（需另 `GRAPH-REBUILD-2026-08-06-go`）

## 對 r12 #7

G1✅／G2 stub ✅／G3 train 仍須 `NF-*-go-plan`。

*完。[I]*
