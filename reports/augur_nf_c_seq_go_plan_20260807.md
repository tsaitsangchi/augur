---
title: NF-C-SEQ · 序列 DL go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-C-SEQ
date: 2026-08-07
paste: "NF-C-SEQ-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1"
prior_eval: audits/S4-SEQLSTM-EVAL-20260804.md
seq_mod: src/augur/models/sequence_ranker.py
layer: "[I]"
self_reported: true
---

# NF-C-SEQ-go-plan｜Wave C／D 序列 · asof=2026-07-31

> **一句**：SeqLSTM Phase 0b **未過門**（min Sharpe≪冠軍）史料保留 → 本刀＝有界**再契約**（同尺重驗或 Transformer 薄殼），asof 釘 **2026-07-31**＋prodset／序列窗；**≠** 默訓、**勿把舊 STOP 塗綠**。  
> 碼：`sequence_ranker`／`train_sequence_ranker` **已在**。

## 護欄

```text
NF-C-SEQ-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others | hold-#1
# ≠ NF-C-SEQ-go；≠ 升格；≠ 塞 B3
```

## 候選執行（另句擇一）

| 徑 | 內容 |
|---|---|
| **R** | SeqLSTM 同尺有界重驗＠**07-31**（預期仍難升格；誠實） |
| **T** | Transformer／小序列薄殼 0a→0b（新 adapter 契約） |
| **S** | SKIP 收口（接受未過門；專心 #1／P6） |

預凍（若 R／T）：#11≥3 seed；#14 vs 冠軍門寫死後再跑；不過 → **STOP promote**。

## Paste

```text
NF-C-SEQ-plan-adopt | FZ/GATE-keep | no-train | hold-#1 | asof=2026-07-31
NF-C-SEQ-go | … | path=R|T|S | asof=2026-07-31 | no-promote
```

*完。[I]*
