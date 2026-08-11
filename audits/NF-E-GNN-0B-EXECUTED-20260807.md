---
status: executed
series: s4_models
track: NF-E
date: 2026-08-07
asof_test: "2026-07-31"
asof_train: "2026-06-30"
horizon: 4
depends_on:
  - audits/NF-E-GNN-0B-GO-20260807.md
  - audits/NF-E-GNN-0A-EXECUTED-20260807.md
log: /tmp/nf-e-gnn-0b-20260807/transfer-h4.log
script: scripts/probe_gnn_phase0b.py
paste: "NF-E-GNN-0b-go | asof=2026-07-31 | H4 | no-promote"
viewpoint: 2026-08-07T16:15+08:00
self_reported: true
---

# EXECUTED｜NF-E-GNN-0b · 轉移探針 · **STOP promote**

> RC=2 · **無證據**（GNN hit **未**嚴格 > naive）· no-serve-swap · 未 registry · hold-#1  
> **H 誠實降階**：Steward 意向 H5＠07-31；PriceAdj 頂僅 **4** 交易日 → 網格 **H4**  
> train＝`GcnSmall`＠**2026-06-30**（S-EQ 圖＋prodset3 · 40 steps）→ `rebind` test＠**2026-07-31**

## 結果

| 尺 | 值 |
|---|---|
| train 節點／邊 | 225／13,021 |
| test 評測股 | **204／204** |
| GNN mean hit | **0.7353**（150／204） |
| naive mean hit | **0.7843**（160／204） |
| 預凍門 | **✗ 無證據** → **STOP promote** |

## 硬邊界（守）

≠ 可交易／#14 · ≠ registry／CHK · ≠ SERVE-SWAP · ≠ 塞 B3  
（另：短 horizon 下 naive 亦偏高——不作翻案敘事）

*完。*
