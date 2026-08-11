---
status: executed
series: s4_models
track: NF-E
date: 2026-08-07
depends_on:
  - audits/NF-E-GNN-0A-GO-20260807.md
  - audits/GRAPH-REBUILD-20260731-EXECUTED-20260807.md
asof_pin: "2026-07-31"
paste: "NF-E-GNN-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | numpy-mp"
viewpoint: 2026-08-07T16:02+08:00
self_reported: true
---

# EXECUTED｜NF-E-GNN-0a · `GcnSmall`（numpy）＋selftest

> RC=0 · 零 DB · **不安裝 torch_geometric** · no-train-prod · 未 registry · 未塞 B3 · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**（圖已 rebuild）

| 項 | 值 |
|---|---|
| 模組 | `src/augur/models/gnn_small.py` |
| class | **`GcnSmall`** · `normalized_adjacency` |
| 實作 | 對稱歸一化 Â · 兩層 ReLU GCN · 可選淺 MSE 步 |
| selftest | **全通過** |

未做：庫內 0b（`graph_consume`＋prodset＠07-31）／PyG／serve。

```text
NF-E-GNN-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | no-promote | no-serve-swap | hold-#1
```

*完。*
