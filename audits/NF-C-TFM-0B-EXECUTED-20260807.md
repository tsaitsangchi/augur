---
status: executed
series: s4_models
track: NF-C-TFM
date: 2026-08-07
until: "2026-07-31"
horizon: 60
depends_on:
  - audits/NF-C-TFM-0B-GO-20260807.md
  - audits/NF-C-TFM-0A-EXECUTED-20260807.md
log: /tmp/nf-c-tfm-0b-0731/phase0b.log
smoke: /tmp/nf-c-tfm-0b-0731/smoke.log
paste: "NF-C-TFM-0b-go | until=2026-07-31 | H60 | family=SeqTransformerSmall | no-promote"
viewpoint: 2026-08-07T22:45+08:00
self_reported: true
---

# EXECUTED｜NF-C-TFM-0b · SeqTransformerSmall · until=2026-07-31／H60

> RC=0 · ~50 min compute（+面板抓取）· **STOP promote** · no-serve-swap · hold-#1  
> CLI：`train_sequence_ranker.py --run --family SeqTransformerSmall --until 2026-07-31 --horizon 60 --window 60 --seeds 1,2,42`

## 結果

| seed | net Sharpe | net hit |
|---:|---:|---:|
| 1 | 1.1545 | 0.6842 |
| 2 | 1.2444 | 0.6316 |
| 42 | 1.1996 | 0.7895 |
| **min** | **1.1545** | — |

預凍對照 RankRidge H60 net Sharpe **1.3016** → min 未勝 → **STOP promote**。  
對照 SeqLSTM path-R min **1.1311**：TFM 略高仍遠低於冠軍門；**≠升格／≠塗綠**。

通道：保留 27／排除 6；n_folds=19（宣告 20；末折無 fwd 標籤跳過，同 LSTM）。  
誠實殘差：部分折 `nanmean` 空切片 RuntimeWarning（稀通道／空窗邊角）；輸出閘仍依淨 Sharpe。

*完。勿重掃當綠。*
