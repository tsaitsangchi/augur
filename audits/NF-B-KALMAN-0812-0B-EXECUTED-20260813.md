---
status: executed
series: s4_models
track: NF-B-KALMAN
date: 2026-08-13
asof: "2026-08-12"
horizon: 20
universe: full_core
depends_on:
  - audits/NF-B-KALMAN-0812-0B-GO-20260813.md
prior_0731: audits/NF-B-KALMAN-0B-EXECUTED-20260807.md
log: /tmp/nf-b-kalman-0812/full-0812-h20.log
cli: "probe_kalman_phase0b.py --run --asof 2026-08-12 --horizon 20 --n-stocks 300 --max-folds 36"
paste: "NF-B-KALMAN-0812-0b-go | asof=2026-08-12 | H20 | full-core | EVIDENCE | no-promote | no-serve-swap"
viewpoint: 2026-08-13T09:40+08:00
self_reported: true
layer: "[I]"
---

# EXECUTED｜NF-B-KALMAN-0b · 全 core＠2026-08-12／H20

> **GO**：`audits/NF-B-KALMAN-0812-0B-GO-20260813.md`  
> 尺：另書方向 hit vs naive · **no-promote／no-serve-swap** · NF-pause-others  
> 輸入：log close · `KalmanLocalLevel`

## 結果

| 尺 | 值 |
|---|---|
| 宇宙 | **284／284**（0 SKIP） |
| Kalman mean hit | **0.5124**（min／med／max＝0.306／0.514／0.722） |
| naive mean hit | **0.4870**（min／med／max＝0.250／0.500／0.722） |
| 每股贏地板 | **155／284** |
| 預凍門 | **✓ 有證據**（mean Kalman > naive） |

## 對照＠07-31

| asof | n | Kalman | naive | 贏地板 |
|---|---:|---:|---:|---:|
| 2026-07-31 | 204 | 0.5108 | 0.4850 | 108／204 |
| **2026-08-12** | **284** | **0.5124** | **0.4870** | **155／284** |

方向一致；宇宙擴大後仍過門。

## 硬邊界（未做）

≠ 可交易／#14 · ≠ registry／CHK · ≠ SERVE-SWAP · ≠ 自動 P1 · ≠ 撤全域 NF-pause

佇列下一可談（另句）：**NF-B-COINT**（Kalman 後 B-1e）或 **NF-B-GARCH** 預測臂＠0812。

*完。*
