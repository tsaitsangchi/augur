---
status: go
series: s4_models
track: NF-C-SEQ
path: R
date: 2026-08-07
viewpoint: 2026-08-07T19:55+08:00
plan: reports/augur_nf_c_seq_go_plan_20260807.md
adopt: audits/NF-C-SEQ-PLAN-ADOPTED-20260807.md
prior_0b: audits/S4-SEQLSTM-EVAL-20260804.md
paste: "NF-C-SEQ-go | path=R | asof=2026-07-31 | no-promote | FZ/GATE-keep | hold-#1"
self_reported: true
---

# GO｜NF-C-SEQ path=R · asof=2026-07-31

> Steward AskQuestion → **R**。  
> **一句**：SeqLSTM 同尺有界重驗——`train_sequence_ranker --run --until 2026-07-31`；**≠** 塗綠 08-04 STOP；**no-promote**。

## 護欄

```text
NF-C-SEQ-go | path=R | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others
| asof/until=2026-07-31 | hold-#1 | no-promote | no-registry-write
```

## 預凍門檻（跑前寫死 · #32b）

| # | 門 | 通過條件 |
|---|---|---|
| 1 | #11 | seeds=`1,2,42` |
| 2 | #14 vs 冠軍 | 3-seed **min** net Sharpe **>** `RankRidge_H60` **1.3016**（`audits/S5-OOS-20260804.md`） |
| 3 | 禁中桶 | 禁單 seed／median 單獨宣稱勝出 |

未過 → **STOP promote**（策略可正收益仍不算過門）。

## 指令

```bash
PYTHONPATH=src HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  ./venv/bin/python scripts/train_sequence_ranker.py --run \
  --since 2021-01-01 --until 2026-07-31 \
  --horizon 60 --window 60 --seeds 1,2,42 --nan-threshold 0.3
```

log：`/tmp/nf-c-seq-r-0731/phase0b.log`

*go；執行見 EXECUTED 帳。*
