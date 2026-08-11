---
title: NF-D-MOIRAI · Moirai-2 排序薄殼 go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-D-MOIRAI
date: 2026-08-08
paste: "NF-D-MOIRAI-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1"
prior_tfm: audits/NF-D-TIMESFM-0A-EXECUTED-20260808.md
arena: src/augur/arena/adapters.py
layer: "[I]"
self_reported: true
---

# NF-D-MOIRAI-go-plan｜預訓練時序 → 截面排序 · asof=2026-07-31

> **一句**：Chronos／TimesFM 0a 後 → 同軌第三支＝**Moirai-2.0-R-small** 排序薄殼（本地權重；arena 方向臂 ≠ 本排序尺）；asof 釘 **2026-07-31**；**≠** 默升格、**≠** hub 下載。  
> Steward：family＝moirai · depth＝plan→0a。

## 護欄

```text
NF-D-MOIRAI-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others | hold-#1
# local_files_only／HF_HUB_OFFLINE；缺權重＝誠實 SKIP
# ≠ registry／serve；≠ 與 Chronos／TimesFM 0b 默併
```

## 分階

| 階 | 內容 | Gate |
|---|---|---|
| **0a** | `MoiraiRank2Small`＋`--selftest`（stub／可選離線真載） | selftest 綠；零 DB |
| **0b**（另授） | 有界＠**07-31**；分數＝log(q50終／末價)；vs 冠軍預凍 | 不過 → **STOP promote** |
| Phase1 | registry／predict_asof | **另句** |

## 契約

- 輸入：每股 1D 價上下文（≤512）；gluonts `ListDataset`  
- 輸出：`(n,)` — 複用 `chronos_rank.score_from_quantiles`  
- 權重：`Salesforce/moirai-2.0-R-small` · **local_files_only**  
- ⊥ `MarketMoirai2` 方向 P

## Paste

```text
NF-D-MOIRAI-plan-adopt | FZ/GATE-keep | no-train | hold-#1 | asof=2026-07-31
NF-D-MOIRAI-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | offline-local
NF-D-MOIRAI-0b-go | … | asof=2026-07-31 | no-promote   # 另授
```

*完。[I]*
