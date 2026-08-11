---
title: NF-D-PATCH · PatchTST 序列排序薄殼 go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-D-PATCH
date: 2026-08-08
paste: "NF-D-PATCH-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1"
prior_tfm: audits/NF-C-TFM-0B-EXECUTED-20260807.md
prior_timesfm: audits/NF-D-TIMESFM-0B-EXECUTED-20260808.md
seq_tfm: src/augur/models/sequence_transformer.py
layer: "[I]"
self_reported: true
---

# NF-D-PATCH-go-plan｜Wave D · D-6c PatchTST · asof=2026-07-31

> **一句**：TimesFM 0b＠07-31 **NaN-gate STOP／SKIP**；預訓練三支＋FTTR／TFM／Seq 皆已觸 → 下一族＝**PatchTST 小排序薄殼**（純 torch 自訓；patchify 時序）；asof 釘 **2026-07-31**＋既有 sequence panel；**≠** 塗綠 TFM／LSTM、**≠** 默升格、**≠** hub 預訓練權重。  
> Steward：family＝patchtst · depth＝**plan only**（本檔）。

## 護欄

```text
NF-D-PATCH-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others | hold-#1
# ≠ 0a／0b 默跑；≠ registry／serve-swap；≠ 塞 B3；CPU-only 誠實
# ≠ 重掃 TimesFM NaN；≠ 下載 patchtst／transformers TS 大權重
```

## 為什麼是這族（佇列）

| 前序 | 狀態 |
|---|---|
| NF-D Chronos／Moirai／TimesFM | 0b 觸完；TimesFM＝NaN SKIP |
| NF-C SeqLSTM／TFM · NF-A FTTR · NF-E GNN | 皆 STOP promote |
| Wave D 殘 | **D-6c PatchTST** 仍 taxonomy SKIP（無 adapter） |
| 前提 | S3-WAVE-D 序列窗契約**已在** →「無窗」SKIP 理由已解鎖；殘＝薄殼碼 |

## 分階

| 階 | 內容 | Gate |
|---|---|---|
| **plan**（本檔） | 契約＋paste；零碼 | Steward `plan-adopt` |
| **0a**（另授） | `SeqPatchTSTSmall`＋`--selftest`（合成 3D；train 統計凍結） | selftest 綠；零 DB |
| **0b**（另授） | 有界 WF＠**07-31**；≥3 seed；預凍 vs RankRidge／naive | 不過 → **STOP promote** |
| Phase1 | registry／predict_asof | **另句** |

## 契約（拟）

- 資料形：`(n, window, channels)`＝同 `stack_windows`／SeqLSTM／`SeqTransformerSmall`  
- API：`fit(X,y_rank)`／`predict(X)→(n,)`  
- 正規化：僅用 train mean／std 凍結（#8）  
- 架構示意：非重疊／可配置 patch → 線性投影 → 小 `TransformerEncoder` → 池化 → Linear；**不安**大型預訓練／Informer 全家桶本窗  
- ⊥ NF-C-TFM（token＝逐步）· ⊥ hub TimesFM／Chronos

## Paste

```text
NF-D-PATCH-plan-adopt | FZ/GATE-keep | no-train | hold-#1 | asof=2026-07-31
NF-D-PATCH-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | no-SIM-apply
NF-D-PATCH-0b-go | … | asof=2026-07-31 | no-promote   # 另授
```

*完。[I] · plan-only；等 adopt。*
