---
status: executed
series: s4_models
track: NF-E
date: 2026-08-13
viewpoint: 2026-08-13T08:58+08:00
go: audits/NF-E-GNN-0812-0B-GO-20260813.md
inventory: audits/NF-E-GNN-0812-INVENTORY-20260813.md
tip: "2026-08-12"
asof_train: "2026-06-30"
asof_test: "2026-08-06"
horizon: 4
log: /tmp/nf-e-gnn-0812/transfer-h4.log
script: scripts/probe_gnn_phase0b.py
paste: "NF-E-GNN-0812-0b-EXECUTED | tip=08-12 | train=06-30 | test=08-06 | H4 | GNN>naive | EVIDENCE | no-promote | no-serve-swap"
promote: false
self_reported: true
layer: "[I]"
---

# EXECUTED｜NF-E-GNN · tip 世界 08-12 · 轉移探針 · **有證據（仍 no-promote）**

```text
RC=0 | GNN mean hit=0.6761 > naive=0.4859 | eval_n=284 | no-promote | ≠可交易
```

## 網格
| | 值 |
|---|---|
| tip 世界 | **2026-08-12**（其後無價 → 不可 tip-forward H20/60） |
| train | **2026-06-30** · 圖 13,021 · nodes 225 |
| test | **2026-08-06** · 圖 33,622 · eval 284 |
| H | **4** |

## 結果
| 尺 | 值 |
|---|---|
| GNN mean hit | **0.6761**（192／284） |
| naive mean hit | **0.4859**（138／284） |
| 預凍門 | **✓ 有證據**（嚴格 > naive） |

## 對讀前次 0b＠07-31
前次 **STOP**（GNN 0.735 < naive 0.784）。本窗不同 test 日／圖密度——**不**自動翻案升格；僅記「tip 世界下此網格有證據」。

## 護欄
**no-promote** · no-serve-swap · 未 registry · ≠#14 可交易 · NF 他族仍 pause

*完。*
