---
status: executed
series: s4_models
track: NF-D-PATCH
date: 2026-08-08
until: "2026-07-31"
horizon: 60
depends_on:
  - audits/NF-D-PATCH-0B-GO-20260808.md
  - audits/NF-D-PATCH-0A-EXECUTED-20260808.md
log: /tmp/nf-d-patch-0b-0731/phase0b.log
smoke: /tmp/nf-d-patch-0b-0731/smoke.log
script: scripts/train_sequence_ranker.py
paste: "NF-D-PATCH-0b-go | until=2026-07-31 | H60 | family=SeqPatchTSTSmall | no-promote"
viewpoint: 2026-08-08T19:05+08:00
self_reported: true
---

# EXECUTED｜NF-D-PATCH-0b · SeqPatchTSTSmall · until=2026-07-31／H60

> RC=0 · ~21 min 評測（+面板抓取 ~4.4 min）· **STOP promote** · no-serve-swap · hold-#1  
> CLI：`train_sequence_ranker.py --run --family SeqPatchTSTSmall --until 2026-07-31 --horizon 60 --window 60 --seeds 1,2,42`

## 結果

| seed | net Sharpe | net hit |
|---:|---:|---:|
| 1 | 1.1552 | 0.6842 |
| 2 | 1.1538 | 0.5789 |
| 42 | 1.2024 | 0.6316 |
| **min** | **1.1538** | **0.5789** |

預凍對照 RankRidge H60 net Sharpe **1.3016** → min 未勝 → **STOP promote**。  
hit 門 min≥**0.6316**：seed=2 **未過**（雙重未過門）。

對照 SeqTransformerSmall min **1.1545**／SeqLSTM path-R min **1.1311**：PatchTST ≈ TFM，仍遠低於冠軍門；**≠升格／≠塗綠**。

通道：保留 27／排除 6；n_folds=19（宣告 20；末折無 fwd 標籤跳過，同 LSTM／TFM）。  
誠實殘差：部分折 `nanmean` 空切片 RuntimeWarning（稀通道／空窗邊角；同 TFM 帳）。

*完。勿重掃當綠。*
