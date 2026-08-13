---
status: executed
series: s4_models
track: NF-B-VAR
date: 2026-08-13
viewpoint: 2026-08-13T08:56+08:00
go: audits/NF-B-VAR-0812-0B-GO-20260813.md
asof: "2026-08-12"
horizon: 20
log: /tmp/nf-b-var-0812/k3-n60-0812-h20.log
script: scripts/probe_var_phase0b.py
paste: "NF-B-VAR-0812-0b-EXECUTED | asof=2026-08-12 | H20 | k=3 | n60 | VAR>naive | EVIDENCE | no-promote | no-serve-swap"
promote: false
self_reported: true
layer: "[I]"
---

# EXECUTED｜NF-B-VAR-0b · asof＝**2026-08-12**／H20 · **有證據（仍 no-promote）**

```text
RC=0 | VAR mean hit=0.5096 > naive=0.4869 | 180 股槽／60 系 | no-promote
```

## 網格
`probe_var_phase0b.py --run --asof 2026-08-12 --horizon 20 --k 3 --n-systems 60 --p 1`

## 結果
| 尺 | 值 |
|---|---|
| 系／股槽 | **60／60** · **180**（0 SKIP） |
| VAR mean hit | **0.5096**（min／med／max＝0.250／0.500／0.722） |
| naive mean hit | **0.4869**（min／med／max＝0.194／0.472／0.722） |
| 每股贏地板 | **93／180** |
| 預凍門 | **✓ 有證據** |

## 對讀＠07-31
前次亦有證據（VAR 0.514＞naive 0.480）。本窗 tip＝08-12 再探——**仍 no-promote**／≠ registry／≠#14 可交易。

## 護欄
no-serve-swap · 未 VECM · 未默 P1 · NF 他族 pause（GNN 另帳）

*完。*
