---
status: executed
series: s4_models
track: NF-B-P1
date: 2026-08-13
asof: "2026-08-12"
horizon: 20
universe: full_core
depends_on:
  - audits/S4-ARIMA-P1-0812-GO-20260813.md
prior: audits/S4-ARIMA-P1-EXECUTED-0731-20260807.md
log: /tmp/s4-arima-p1-0812/full-0812-h20.log
cli: "probe_classical_ts_phase0b.py --run --asof 2026-08-12 --horizon 20 --n-stocks 300 --max-folds 36"
paste: "S4-ARIMA-P1-0812-go | asof=2026-08-12 | H20 | full-core | EVIDENCE | no-promote | no-serve-swap"
viewpoint: 2026-08-13T09:20+08:00
self_reported: true
layer: "[I]"
---

# EXECUTED｜S4-ARIMA-P1 · 全 core＠2026-08-12／H20

> **GO**：`audits/S4-ARIMA-P1-0812-GO-20260813.md`  
> 尺：**另書方向 hit vs naive**（≠ RankRidge #14）· **no-promote／no-serve-swap** · NF-pause-others

## 結果

| 尺 | 值 |
|---|---|
| 宇宙 | **284／284**（core＠08-12；0 SKIP） |
| ARIMA mean hit | **0.5082**（min／med／max＝0.250／0.500／0.750） |
| naive mean hit | **0.4870**（min／med／max＝0.250／0.500／0.722） |
| 每股贏地板 | **157／284** |
| 預凍門 | **✓ 有證據**（mean ARIMA > naive） |

## 對照＠07-31

| asof | n | ARIMA | naive | 贏地板 |
|---|---:|---:|---:|---:|
| 2026-07-31 | 204 | 0.5139 | 0.4850 | 112／204 |
| **2026-08-12** | **284** | **0.5082** | **0.4870** | **157／284** |

方向一致；宇宙擴大後均值略收斂，仍過門。

## 硬邊界（未做）

- **≠** 可交易／確立級  
- **≠** `model_registry`／CHK 加 `ArimaUnivariate`  
- **≠** SERVE-SWAP／改 `predict_asof` 默認  
- **≠** 混截面 #14；≠ 撤全域 NF-pause  

可選下一句：`S4-ARIMA-P1-registry-go | … | no-serve-swap`（另明示）或收口停。

*完。*
