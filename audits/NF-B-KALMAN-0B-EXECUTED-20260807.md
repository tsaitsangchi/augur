---
status: executed
series: s4_models
track: NF-B-KALMAN
date: 2026-08-07
asof: "2026-07-31"
horizon: 20
depends_on:
  - audits/NF-B-KALMAN-0B-GO-20260807.md
  - audits/NF-B-KALMAN-0A-EXECUTED-20260807.md
log: /tmp/nf-b-kalman-0b-20260807/full-0731-h20.log
script: scripts/probe_kalman_phase0b.py
paste: "NF-B-KALMAN-0b-go | asof=2026-07-31 | H20 | full-core | no-promote"
viewpoint: 2026-08-07T15:20+08:00
self_reported: true
---

# EXECUTED｜NF-B-KALMAN-0b · 全 core＠2026-07-31／H20

> RC=0 · **有證據** · **no-promote／no-serve-swap** · 未 registry · hold-#1  
> CLI：`probe_kalman_phase0b.py --run --n-stocks 300 --horizon 20 --asof 2026-07-31`  
> 輸入：log close · `KalmanLocalLevel`（local level）

## 結果

| 尺 | 值 |
|---|---|
| 宇宙 | **204／204**（0 SKIP） |
| Kalman mean hit | **0.5108**（min／med／max＝0.306／0.500／0.722） |
| naive mean hit | **0.4850**（min／med／max＝0.250／0.500／0.722） |
| 每股贏地板 | **108／204** |
| 預凍門 | **✓ 有證據**（mean Kalman > naive） |

## 硬邊界（未做）

≠ 可交易／#14 · ≠ registry／CHK · ≠ SERVE-SWAP · ≠ 自動 P1

*完。*
