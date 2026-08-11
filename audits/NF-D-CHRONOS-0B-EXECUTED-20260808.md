---
status: executed
series: s4_models
track: NF-D-CHRONOS
date: 2026-08-08
asof: "2026-07-31"
horizon: 20
depends_on:
  - audits/NF-D-CHRONOS-0B-GO-20260808.md
  - audits/NF-D-CHRONOS-0A-EXECUTED-20260808.md
log: /tmp/nf-d-chronos-0b-0731/phase0b.log
script: scripts/probe_chronos_phase0b.py
paste: "NF-D-CHRONOS-0b-go | asof=2026-07-31 | H20 | full-core | offline-local | no-promote"
viewpoint: 2026-08-08T10:10+08:00
self_reported: true
---

# EXECUTED｜NF-D-CHRONOS-0b · 全 core＠2026-07-31／H20

> RC=0 · **有證據（薄）** · **仍 STOP promote** · offline-local · 未 registry · 未 serve  
> CLI：`probe_chronos_phase0b.py --run --asof 2026-07-31 --horizon 20 --n-stocks 300`

## 結果

| 尺 | 值 |
|---|---|
| 宇宙 | **204／204** |
| Chronos mean hit | **0.4949**（min／med／max＝0.250／0.500／0.792） |
| naive mean hit | **0.4902**（min／med／max＝0.167／0.500／0.750） |
| 每股贏地板 | **91／204** |
| 預凍證據門 | **✓** mean Chronos > naive（邊際） |
| 升格 | **STOP promote** |

對照 Moirai 0b：Moirai mean **0.5206**／贏地板 106／204 — Chronos 證據更薄。

*完。勿重掃當綠／默升格。*
