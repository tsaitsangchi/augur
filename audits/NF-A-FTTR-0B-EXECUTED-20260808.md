---
status: executed
series: s4_models
track: NF-A-FTTR
date: 2026-08-08
until: "2026-07-31"
horizon: 60
depends_on:
  - audits/NF-A-FTTR-0B-GO-20260808.md
  - audits/NF-A-FTTR-0A-EXECUTED-20260808.md
log: /tmp/nf-a-fttr-0b-0731/phase0b.log
script: scripts/probe_fttr_phase0b.py
paste: "NF-A-FTTR-0b-go | until=2026-07-31 | H60 | RankFTTransformer | no-promote"
viewpoint: 2026-08-08T01:02+08:00
self_reported: true
---

# EXECUTED｜NF-A-FTTR-0b · RankFTTransformer · until=2026-07-31／H60

> RC=0 · **STOP promote** · portfolio 評測支路 only · **未**入 `ALL_FAMILIES`／registry／serve · hold-#1  
> CLI：`probe_fttr_phase0b.py --run --until 2026-07-31 --horizon 60 --seeds 1,2,42`

## 尺

| 項 | 值 |
|---|---|
| panel_hash | `d3fc623092` · n_panels=23 · n_folds=19 |
| feats | prodset active **3**=`cycle_position_252d`／`inst_cumflow_position_120d`／`lending_fee_rate_mean_30d`（＝RankRidge＠07-31 artifact） |

## 結果

| seed | net Sharpe | hit |
|---:|---:|---:|
| 1 | 1.2358 | 0.6316 |
| 2 | 1.0071 | 0.6316 |
| 42 | 1.4836 | 0.7895 |
| **min** | **1.0071** | **0.6316** |

預凍：min Sharpe **>** 1.3016 **且** min hit ≥ 0.6316 → Sharpe 未過 → **STOP promote**。  
（單 seed 42 勝冠軍 **不計**；#32b 禁中桶。）

*完。勿重掃當綠。*
