---
status: executed
series: s4_models
track: NF-B-COINT
date: 2026-08-07
asof: "2026-07-31"
horizon: 20
depends_on:
  - audits/NF-B-COINT-0B-GO-20260807.md
  - audits/NF-B-COINT-0A-EXECUTED-20260807.md
log: /tmp/nf-b-coint-0b-20260807/n100-0731-h20.log
script: scripts/probe_coint_phase0b.py
paste: "NF-B-COINT-0b-go | asof=2026-07-31 | H20 | n_pairs=100 | no-promote"
viewpoint: 2026-08-07T15:40+08:00
self_reported: true
---

# EXECUTED｜NF-B-COINT-0b · 100 對＠2026-07-31／H20

> RC=0 · **有證據（邊際）** · **no-promote／no-serve-swap** · ≠可套利 · 未 registry · hold-#1  
> CLI：`probe_coint_phase0b.py --run --asof 2026-07-31 --horizon 20 --n-pairs 100`  
> 主尺：對內 **y**（EG panel 第 0 欄）方向 hit vs naive

## 結果

| 尺 | 值 |
|---|---|
| 對 | **100／100**（0 SKIP） |
| coint mean hit | **0.4922**（min／med／max＝0.278／0.500／0.694） |
| naive mean hit | **0.4839**（min／med／max＝0.278／0.500／0.722） |
| 每對贏地板 | **48／100** |
| 預凍門 | **✓ 有證據**（mean coint > naive；**利差薄**） |

## 硬邊界（未做）

≠ 可交易／可套利／#14 · ≠ registry／CHK · ≠ SERVE-SWAP · ≠ 自動 P1

> Wave B classical（ARIMA／VAR／Kalman／協整）本窗有界探針鏈可標 **收尾**；GARCH 預測臂仍另分尺。

*完。*
