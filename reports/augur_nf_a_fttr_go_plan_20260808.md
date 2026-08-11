---
title: NF-A-FTTR · FT-Transformer 表格排序 go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-A-FTTR
date: 2026-08-08
paste: "NF-A-FTTR-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1"
prior_mlp: audits/NF-A-MLP-EXECUTED-20260807.md
prior_moirai: audits/NF-D-MOIRAI-0B-EXECUTED-20260808.md
layer: "[I]"
self_reported: true
---

# NF-A-FTTR-go-plan｜月頻 fv 表格 DL · asof=2026-07-31

> **一句**：預訓練時序三支已觸 → 下一族＝**FT-Transformer 小表格排序**（純 torch；**不安** `pytorch-tabnet`）；吃 `feature_values` 2D；asof 釘 **2026-07-31**；**≠** 默升格、**≠** 塗綠 RankMLP STOP。  
> Steward：family＝tabnet→**FT-TR** · depth＝plan→0a · 實作＝ft_torch。

## 護欄

```text
NF-A-FTTR-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others | hold-#1
# ≠ pip install pytorch-tabnet；≠ registry／serve；≠ 塞 B3
```

## 分階

| 階 | 內容 | Gate |
|---|---|---|
| **0a** | `RankFTTransformer`＋`--selftest` | selftest 綠；零 DB |
| **0b**（另授） | 有界 WF＠**07-31**；≥3 seed；vs RankRidge H60 **1.3016** | 不過 → **STOP promote** |
| Phase1 | registry／predict_asof | **另句** |

## 契約

- `fit(X,y_rank)`／`predict(X)→(n,)`＝RankRidge 同構  
- train：StandardScaler 凍結＋NaN→0  
- 架構：每特徵→token · 小 TransformerEncoder · CLS／mean-pool → Linear  
- CPU-only 誠實

## Paste

```text
NF-A-FTTR-plan-adopt | FZ/GATE-keep | no-train | hold-#1 | asof=2026-07-31
NF-A-FTTR-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | no-SIM-apply
NF-A-FTTR-0b-go | … | asof=2026-07-31 | no-promote   # 另授
```

*完。[I]*
