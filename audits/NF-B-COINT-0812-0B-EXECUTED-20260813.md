---
status: executed
series: s4_models
track: NF-B-COINT
date: 2026-08-13
asof: "2026-08-12"
horizon: 20
n_pairs: 100
depends_on:
  - audits/NF-B-COINT-0812-0B-GO-20260813.md
prior_0731: audits/NF-B-COINT-0B-EXECUTED-20260807.md
prior_kalman_0812: audits/NF-B-KALMAN-0812-0B-EXECUTED-20260813.md
log: /tmp/nf-b-coint-0812/n100-0812-h20.log
cli: "probe_coint_phase0b.py --run --asof 2026-08-12 --horizon 20 --n-pairs 100 --max-folds 36"
paste: "NF-B-COINT-0812-0b-go | asof=2026-08-12 | H20 | n_pairs=100 | EVIDENCE | no-promote | no-serve-swap"
viewpoint: 2026-08-13T09:43+08:00
self_reported: true
layer: "[I]"
---

# EXECUTED｜NF-B-COINT-0b · 100 對＠2026-08-12／H20

> **GO**：`audits/NF-B-COINT-0812-0B-GO-20260813.md`  
> 尺：對內 **y** 方向 hit vs naive · **no-promote／no-serve-swap** · ≠可套利  
> CLI 如上；EG／`CointPairEG`

## 結果

| 尺 | 值 |
|---|---|
| 對 | **100／100**（0 SKIP） |
| coint mean hit | **0.5044**（min／med／max＝0.306／0.500／0.694） |
| naive mean hit | **0.4850**（min／med／max＝0.278／0.472／0.694） |
| 每對贏地板 | **54／100** |
| 預凍門 | **✓ 有證據**（mean coint > naive） |

## 對照＠07-31

| asof | n | coint | naive | 贏地板 |
|---|---:|---:|---:|---:|
| 2026-07-31 | 100 | 0.4922 | 0.4839 | 48／100 |
| **2026-08-12** | **100** | **0.5044** | **0.4850** | **54／100** |

利差仍薄，但過門；方向同。

## 硬邊界（未做）

≠ 可交易／可套利／#14 · ≠ registry／CHK · ≠ SERVE-SWAP · ≠ 自動 P1  
≠ 同句開 **GARCH**（須另貼 `NF-B-GARCH-0812-0b-go`）

Wave B classical＠**0812**（ARIMA／VAR／Kalman／協整）有界鏈可標 **收尾**；GARCH 預測臂仍分尺另句。

*完。*
