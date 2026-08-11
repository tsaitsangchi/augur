---
status: executed
series: s4_models
track: NF-C
date: 2026-08-07
until: "2026-07-31"
horizon: 60
depends_on:
  - audits/NF-C-SEQ-R-GO-20260807.md
  - audits/NF-C-SEQ-PLAN-ADOPTED-20260807.md
log: /tmp/nf-c-seq-r-0731/phase0b.log
paste: "NF-C-SEQ path-R | until=2026-07-31 | H60 | seeds=1,2,42"
viewpoint: 2026-08-07T20:50+08:00
self_reported: true
---

# EXECUTED｜NF-C SeqLSTM path-R · until=2026-07-31／H60

> RC=0 · ~48.5 min · **STOP promote**（未過冠軍門）· no-serve-swap · hold-#1  
> CLI：`train_sequence_ranker.py --run --since 2021-01-01 --until 2026-07-31 --horizon 60 --window 60 --seeds 1,2,42`

## 結果

| seed | net Sharpe | net hit |
|---:|---:|---:|
| 1 | 1.1311 | 0.5789 |
| 2 | 1.1649 | 0.5789 |
| 42 | 1.1517 | 0.5263 |
| **min** | **1.1311** | — |

預凍對照 RankRidge H60 net Sharpe **1.3016**／hit **0.6316** → min 未勝 → **STOP promote**。  
與 `S4-SEQLSTM-EVAL-20260804` 數字實質一致（同尺再驗 ≠ 翻案）。

通道：保留 27／排除 6；n_folds=19（宣告 20）。

*完。*
