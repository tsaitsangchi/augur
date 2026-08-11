---
title: NF-C-TFM · 序列 Transformer 薄殼 go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-C-TFM
date: 2026-08-07
paste: "NF-C-TFM-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1"
prior_seq: reports/augur_nf_c_seq_go_plan_20260807.md
prior_r: audits/NF-C-SEQ-R-EXECUTED-20260807.md
seq_lstm: src/augur/models/sequence_ranker.py
layer: "[I]"
self_reported: true
---

# NF-C-TFM-go-plan｜Wave C path=T · Transformer · asof=2026-07-31

> **一句**：SeqLSTM path=R＠07-31 **STOP promote** → 下一族＝**序列 Transformer 薄殼**（新 adapter）；asof 釘 **2026-07-31**＋既有 sequence panel；**≠** 塗綠 LSTM、**≠** 默升格。  
> Steward：family＝tfm · depth＝plan→0a。

## 護欄

```text
NF-C-TFM-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others | hold-#1
# ≠ 0b 默跑；≠ registry／serve-swap；≠ 塞 B3；CPU-only 誠實
```

## 分階

| 階 | 內容 | Gate |
|---|---|---|
| **0a** | `SeqTransformerSmall` library＋`--selftest`（合成 3D 張量；train 統計凍結） | selftest 全綠；零 DB |
| **0b**（另授） | 有界 WF／轉移探針＠**07-31**；≥3 seed；預凍 vs RankRidge／naive | 不過 → **STOP promote** |
| Phase1 | registry／predict_asof | **另句** |

## 契約

- 資料形：`(n, window, channels)`＝同 `stack_windows`／SeqLSTM  
- API：`fit(X,y_rank)`／`predict(X)→(n,)`  
- 正規化：僅用 train mean／std 凍結（#8）  
- 架構：小 `TransformerEncoder`（少層／少頭／小 d_model）＋池化／末步＋線性頭；**不安**大型預訓練權重

## Paste

```text
NF-C-TFM-plan-adopt | FZ/GATE-keep | no-train | hold-#1 | asof=2026-07-31
NF-C-TFM-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | no-SIM-apply
NF-C-TFM-0b-go | … | asof=2026-07-31 | no-promote   # 另授
```

*完。[I]*
