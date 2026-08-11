---
status: executed
series: s4_models
track: NF-D-MOIRAI
date: 2026-08-08
asof: "2026-07-31"
horizon: 20
depends_on:
  - audits/NF-D-MOIRAI-0B-GO-20260808.md
  - audits/NF-D-MOIRAI-0A-EXECUTED-20260808.md
log: /tmp/nf-d-moirai-0b-0731/phase0b.log
script: scripts/probe_moirai_phase0b.py
paste: "NF-D-MOIRAI-0b-go | asof=2026-07-31 | H20 | full-core | offline-local | no-promote"
viewpoint: 2026-08-08T00:34+08:00
self_reported: true
---

# EXECUTED｜NF-D-MOIRAI-0b · 全 core＠2026-07-31／H20

> RC=0 · **有證據** · **仍 STOP promote** · offline-local · no-serve-swap · 未 registry · hold-#1  
> CLI：`probe_moirai_phase0b.py --run --asof 2026-07-31 --horizon 20 --n-stocks 300`

## 結果

| 尺 | 值 |
|---|---|
| 宇宙 | **204／204** |
| Moirai mean hit | **0.5206**（min／med／max＝0.250／0.542／0.833） |
| naive mean hit | **0.4902**（min／med／max＝0.167／0.500／0.750） |
| 每股贏地板 | **106／204** |
| 預凍證據門 | **✓** mean Moirai > naive |
| 升格 | **STOP promote**（預凍禁升） |

分數＝`log(q50終／末價)` 符號 vs 實現方向；月步 WF · max_folds=24 · 上下文≤asof。

## 硬邊界（未做）

≠ #14／可交易 · ≠ registry／SERVE-SWAP · ≠ 塗綠 TimesFM · ≠ 默把有證據當升格

*完。*
