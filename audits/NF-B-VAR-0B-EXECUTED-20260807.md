---
status: executed
series: s4_models
track: NF-B-VAR
date: 2026-08-07
asof: "2026-07-31"
horizon: 20
depends_on:
  - audits/NF-B-VAR-0B-GO-20260807.md
  - audits/NF-B-VAR-0A-EXECUTED-20260807.md
log: /tmp/nf-b-var-0b-20260807/k3-n60-0731-h20.log
script: scripts/probe_var_phase0b.py
paste: "NF-B-VAR-0b-go | asof=2026-07-31 | H20 | k=3 | n_systems=60 | no-promote"
viewpoint: 2026-08-07T15:00+08:00
self_reported: true
---

# EXECUTED｜NF-B-VAR-0b · k=3×60 系＠2026-07-31／H20

> RC=0 · **有證據** · **no-promote／no-serve-swap** · 未 registry · hold-#1  
> CLI：`probe_var_phase0b.py --run --asof 2026-07-31 --horizon 20 --k 3 --n-systems 60 --p 1`

## 結果

| 尺 | 值 |
|---|---|
| 系／股槽 | **60／60** 系 · **180** 股槽（0 SKIP） |
| VAR mean hit | **0.5139**（min／med／max＝0.250／0.514／0.722） |
| naive mean hit | **0.4801**（min／med／max＝0.194／0.472／0.722） |
| 每股贏地板 | **102／180** |
| 預凍門 | **✓ 有證據**（mean VAR > naive） |

## 硬邊界（未做）

≠ 可交易／#14 混尺 · ≠ `model_registry`／CHK · ≠ SERVE-SWAP · ≠ VECM · ≠ 自動 P1

可選下一句：`NF-B-VAR-P1-go | …`（擴大）或 `NF-B-VAR-registry-go | no-serve-swap`。

*完。*
