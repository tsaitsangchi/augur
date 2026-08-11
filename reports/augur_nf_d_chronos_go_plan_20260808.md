---
title: NF-D-CHRONOS · Chronos-Bolt 排序薄殼 go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-D-CHRONOS
date: 2026-08-08
paste: "NF-D-CHRONOS-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1"
prior_tfm: audits/NF-C-TFM-0B-EXECUTED-20260807.md
arena: src/augur/arena/adapters.py
layer: "[I]"
self_reported: true
---

# NF-D-CHRONOS-go-plan｜預訓練時序 → 截面排序 · asof=2026-07-31

> **一句**：SeqLSTM／TFM＠07-31 皆 **STOP** → 下一族＝**Chronos-Bolt-small** 排序薄殼（本地權重；arena 已有方向臂 ≠ 本排序尺）；asof 釘 **2026-07-31**；**≠** 默升格、**≠** 搶下載／線上 hub。  
> Steward：family＝chronos · variant＝bolt · depth＝plan→0a。

## 護欄

```text
NF-D-CHRONOS-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others | hold-#1
# HF_HUB_OFFLINE／local_files_only 預設；缺權重＝誠實 SKIP
# ≠ registry／serve；≠ 塗綠 arena dgate；≠ 假 B3
```

## 分階

| 階 | 內容 | Gate |
|---|---|---|
| **0a** | `ChronosRankBolt` library＋`--selftest`（可 stub／可選離線真載） | selftest 綠；零 DB；預設不抓網 |
| **0b**（另授） | 有界 core／panel＠**07-31**；分數＝log(q50終／末價)；vs RankRidge／naive 預凍 | 不過 → **STOP promote** |
| Phase1 | registry／predict_asof | **另句** |

## 契約

- 輸入：每股 1D 價上下文（≤512）· **非** `feature_values` 2D  
- 輸出：`(n,)` 截面可比分數（預設：終點 median 相對末價之 log 比）  
- 權重：`amazon/chronos-bolt-small` **僅 local_files_only**  
- ⊥ `MarketChronos` 方向 P 口徑（可複用 pipeline，**升格尺不同**）

## Paste

```text
NF-D-CHRONOS-plan-adopt | FZ/GATE-keep | no-train | hold-#1 | asof=2026-07-31
NF-D-CHRONOS-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | offline-local
NF-D-CHRONOS-0b-go | … | asof=2026-07-31 | no-promote   # 另授
```

*完。[I]*
