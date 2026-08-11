---
status: executed
series: s4_models
track: NF-B-P1
date: 2026-08-07
asof: "2026-07-31"
horizon: 20
universe: full_core
depends_on:
  - audits/S4-ARIMA-P1-GO-0731-20260807.md
log: /tmp/s4-arima-p1-20260807/full-0731-h20.log
paste: "S4-ARIMA-P1-go | asof=2026-07-31 | H20 | full-core | no-promote | no-serve-swap"
viewpoint: 2026-08-07T14:45+08:00
self_reported: true
---

# EXECUTED｜S4-ARIMA-P1 · 全 core＠2026-07-31／H20

> **GO**：擴宇宙改釘 **07-31** · 全 core · H20 · **no-promote／no-serve-swap** · hold-#1  
> CLI：`probe_classical_ts_phase0b.py --run --n-stocks 300 --horizon 20 --asof 2026-07-31 --max-folds 36`  
> 尺：**另書方向 hit vs naive**（≠ RankRidge #14）

## 結果

| 尺 | 值 |
|---|---|
| 宇宙 | **204／204**（core＠07-31；0 SKIP） |
| ARIMA mean hit | **0.5139**（min／med／max＝0.250／0.528／0.750） |
| naive mean hit | **0.4850**（min／med／max＝0.250／0.500／0.722） |
| 每股贏地板 | **112／204** |
| 預凍門 | **✓ 有證據**（mean ARIMA > naive） |

## 硬邊界（未做）

- **≠** 可交易／確立級  
- **≠** `model_registry` 登錄／CHK 加 `ArimaUnivariate`  
- **≠** SERVE-SWAP／改 `predict_asof` 默認  
- **≠** 混截面 #14 冠軍門  

可選下一句：`S4-ARIMA-P1-registry-go | … | no-serve-swap`（另明示）或收口停。

*完。*
