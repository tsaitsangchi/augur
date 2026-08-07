---
title: NF-A-XGB · XGBoost 族 plan-first（有界撤 pause）
status: adopted
series: s4_models
track: NF-A-XGB
date: 2026-08-07
viewpoint: 2026-08-07T10:24+08:00
paste: "NF-A-XGB-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30"
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
v2: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
prior_eval: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
prior_rf: audits/NF-A-RF-EXECUTED-20260807.md
layer: "[I]"
role: A-3b RankXGB 有界解凍計畫；誠實記「碼已在、前評未過門」；本窗 Steward 選 go_now
self_reported: true
---

# NF-A-XGB-go-plan｜RankXGB（XGBoost）· 2026-08-07

> **Steward**：開訓 → 選 XGB；**plan＋立刻 go**。  
> **一句**：對 **A-3b／`RankXGB`** 有界撤 NF——歷史 prodset 訓／#14；**全域 NF-pause 其他族 keep**。  
> **誠實前提**：`ranker.RankXGB` **已在**；08-04 sklearn-EVAL **H60／H20 均未過門**；RF 同窗重驗仍 STOP promote。

---

## §0 護欄

```text
NF-A-XGB-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30 | hold-#1
# go ≠ 升格；≠ 撤全域 pause；≠ 假 B3；≠ 改 dgate
```

| 可 | 不可 |
|---|---|
| 僅 `family=RankXGB` 歷史窗 | 連帶解凍 CAT／GNN／ARIMA |
| #11≥3 seed · #14 vs 預凍冠軍 | 單 seed 謊勝；默換 LIVE |
| orphan joblib（若 registry CHK 擋） | 自動 ALTER `model_family_chk` |

---

## §1 為什麼是 XGB（對 V2）

| 項 | 值 |
|---|---|
| V2 優先 | **1**（與 RF 並列；RF 已 EXECUTED STOP） |
| 歷史窗 | prodset active3 · `until=2026-06-30` |
| adapter | **`RankXGB` exists** |
| 前評 H60 | seed1/2/42 ≈ 1.1905 / 1.1075 / 1.1116；min＜冠軍 1.3016 |

---

## §2 執行句（本窗 go_now）

```text
NF-A-XGB-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default
```

```bash
# #14：portfolio.run_backtest model=RankXGB（同 RF probe 口徑）
# train：train_ranker --family RankXGB --horizon 60 --seed {42,1,2} --asof 2026-06-30 --feature-source=prodset
```

| 尺 | 預凍 |
|---|---|
| H60 冠軍 | net Sharpe **1.3016**／hit **0.6316** |
| 升格 | 三 seed 皆優於門檻且 hit 不劣——否則 **STOP promote** |

---

## §3 Paste-ready（若要再跑）

```text
NF-A-XGB-plan-adopt | FZ/GATE-keep | NF-pause-others | no-train | hold-#1
NF-A-XGB-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default
```

*完。[I]*
