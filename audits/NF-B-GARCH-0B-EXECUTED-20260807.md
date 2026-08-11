---
status: executed
series: s4_models
track: NF-B-GARCH
date: 2026-08-07
asof: "2026-07-31"
horizon: 20
depends_on:
  - audits/NF-B-GARCH-0B-GO-20260807.md
  - audits/NF-B-GARCH-0A-EXECUTED-20260807.md
log: /tmp/nf-b-garch-0b-20260807/full-0731-h20.log
script: scripts/probe_garch_phase0b.py
paste: "NF-B-GARCH-0b-go | asof=2026-07-31 | H20 | full-core | no-promote"
viewpoint: 2026-08-07T16:40+08:00
self_reported: true
---

# EXECUTED｜NF-B-GARCH-0b · 全 core＠2026-07-31／H20（預測臂）

> RC=0 · **有證據** · **pred-arm-only** · ⊥ `simulate_*` · **no-promote／no-serve-swap** · 未 registry · hold-#1  
> CLI：`probe_garch_phase0b.py --run --asof 2026-07-31 --horizon 20 --n-stocks 300`  
> 信號：條件**均值**累積方向（σ 不入主門）

## 結果

| 尺 | 值 |
|---|---|
| 宇宙 | **204／204** |
| GARCH mean hit | **0.5170**（min／med／max＝0.306／0.528／0.750） |
| naive mean hit | **0.4850**（min／med／max＝0.250／0.500／0.722） |
| 每股贏地板 | **116／204** |
| 預凍門 | **✓ 有證據**（mean GARCH > naive） |

## 硬邊界（未做）

≠ 可交易／#14 · ≠ 引用 sim GARCH 綠 · ≠ registry／SERVE-SWAP

> Wave B：**預測臂 GARCH** 本窗亦有證據；classical＋GARCH 有界探針鏈可標更完整收口（升格仍另軌）。

*完。*
