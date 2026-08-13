---
status: executed
series: s4_models
track: NF-B-GARCH
date: 2026-08-13
asof: "2026-08-12"
horizon: 20
universe: full_core
depends_on:
  - audits/NF-B-GARCH-0812-0B-GO-20260813.md
prior_0731: audits/NF-B-GARCH-0B-EXECUTED-20260807.md
prior_coint_0812: audits/NF-B-COINT-0812-0B-EXECUTED-20260813.md
log: /tmp/nf-b-garch-0812/full-0812-h20.log
cli: "probe_garch_phase0b.py --run --asof 2026-08-12 --horizon 20 --n-stocks 300 --max-folds 36"
paste: "NF-B-GARCH-0812-0b-go | asof=2026-08-12 | H20 | full-core | EVIDENCE | pred-arm-only | no-promote"
viewpoint: 2026-08-13T09:52+08:00
self_reported: true
layer: "[I]"
---

# EXECUTED｜NF-B-GARCH-0b · 全 core＠2026-08-12／H20（預測臂）

> **GO**：`audits/NF-B-GARCH-0812-0B-GO-20260813.md`  
> 尺：條件均值方向 hit vs naive · **pred-arm-only** · ⊥ `simulate_*` · **no-promote／no-serve-swap**

## 結果

| 尺 | 值 |
|---|---|
| 宇宙 | **284／284** |
| GARCH mean hit | **0.5115**（min／med／max＝0.306／0.500／0.750） |
| naive mean hit | **0.4870**（min／med／max＝0.250／0.500／0.722） |
| 每股贏地板 | **149／284** |
| 預凍門 | **✓ 有證據**（mean GARCH > naive） |

## 對照＠07-31

| asof | n | GARCH | naive | 贏地板 |
|---|---:|---:|---:|---:|
| 2026-07-31 | 204 | 0.5170 | 0.4850 | 116／204 |
| **2026-08-12** | **284** | **0.5115** | **0.4870** | **149／284** |

方向一致；宇宙擴大後略收斂，仍過門。

## 硬邊界（未做）

≠ 可交易／#14 · ≠ 引用 sim GARCH 綠 · ≠ registry／SERVE-SWAP · ≠ 自動 P1

## 0812 旁刀收口（Wave B＋GNN）

| 族 | ＠0812 | 門 |
|---|---|---|
| ARIMA／VAR／Kalman／COINT／GARCH／GNN | 皆已 0b／P1 有界 | EVIDENCE 或既帳；**皆 no-promote** |

再「下一族再開＠0812」須點名新殘格（勿重掃假綠）或收口停。

*完。*
