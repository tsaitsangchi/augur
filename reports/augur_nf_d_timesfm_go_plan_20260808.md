---
title: NF-D-TIMESFM · TimesFM-2.5 排序薄殼 go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-D-TIMESFM
date: 2026-08-08
paste: "NF-D-TIMESFM-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1"
prior_chronos: audits/NF-D-CHRONOS-0A-EXECUTED-20260808.md
arena: src/augur/arena/adapters.py
layer: "[I]"
self_reported: true
---

# NF-D-TIMESFM-go-plan｜預訓練時序 → 截面排序 · asof=2026-07-31

> **一句**：Chronos-Bolt 0a 已就緒 → 姊妹族＝**TimesFM-2.5-200m** 排序薄殼（本地權重；arena 方向臂 ≠ 本排序尺）；asof 釘 **2026-07-31**；**≠** 默升格、**≠** hub 下載。  
> Steward：family＝timesfm · depth＝plan→0a。

## 護欄

```text
NF-D-TIMESFM-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others | hold-#1
# local_files_only／HF_HUB_OFFLINE；缺權重＝誠實 SKIP
# ≠ registry／serve；≠ Chronos 0b 默併
```

## 分階

| 階 | 內容 | Gate |
|---|---|---|
| **0a** | `TimesFMRank25`＋`--selftest`（stub／可選離線真載） | selftest 綠；零 DB |
| **0b**（另授） | 有界＠**07-31**；分數＝log(q50終／末價)；vs 冠軍預凍 | 不過 → **STOP promote** |
| Phase1 | registry／predict_asof | **另句** |

## 契約

- 輸入：每股 1D 價上下文（≤512）  
- 輸出：`(n,)` — 複用 `chronos_rank.score_from_quantiles` 口徑  
- 權重：`google/timesfm-2.5-200m-pytorch` · **local_files_only**  
- ⊥ `MarketTimesFM` 方向 P

## Paste

```text
NF-D-TIMESFM-plan-adopt | FZ/GATE-keep | no-train | hold-#1 | asof=2026-07-31
NF-D-TIMESFM-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | offline-local
NF-D-TIMESFM-0b-go | … | asof=2026-07-31 | no-promote   # 另授
```

*完。[I]*
