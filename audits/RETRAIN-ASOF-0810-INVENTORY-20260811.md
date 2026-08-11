---
title: 模型重訓盤點 · as-of 2026-08-10
subtitle: inventory_then；分清 B3 日更／rank 重訓／方向臂／NF
status: inventory
date: 2026-08-11
viewpoint: 2026-08-11T08:15+08:00
layer: "[I]"
paste: "RETRAIN-ASOF-0810-inventory | FZ/GATE-keep | NF-pause | no-promote | no-SIM-apply | tip-ready"
price_tip: 2026-08-10
fv_max: 2026-08-07
core_max: 2026-08-07
pred_panel_max: 2026-08-07
watcher: "TIMEOUT@08-10T23:50（當時 tip 未到）；現 tip 已到 → 可補跑"
self_reported: true
---

# INVENTORY｜重訓／as-of 2026-08-10（2026-08-11）

> Steward：`做所有模型的重訓到 as-of 2026-08-10` → 選 **inventory_then**。  
> **LIVE**：PriceAdj **已到 08-10**；watcher 昨夜 TIMEOUT（誠實不假跑）。  
> **阻塞**：`feature_values`／`core_universe_asof`／`prediction_values` 仍停 **08-07** —— **重訓前須先把 feat（＋core）推到 08-10**，否則 `--asof 2026-08-10` 實際訓練窗仍無 08-10 panel。

## §0 三件事（勿混）

| 代號 | 是什麼 | 是「重訓」？ | as-of 08-10 意義 |
|---|---|---|---|
| **B3** | feat→core→**predict**→emit | **否**（用已登錄模型出單） | 預測日 D=08-10 |
| **Rank 重訓** | `train_ranker.py --asof 2026-08-10` | **是** | 訓練凍結日＝panel≤08-10 |
| **日向／NF** | Daily*／TimesFM 等 | 另臂；**NF-pause** | 本盤點預設**不開** |

## §1 可重訓族（`train_ranker` · 8 族）

| family | registry 現況（最新 train asof） | 已登錄 H | 建議 08-10 重訓 H |
|---|---|---|---|
| **RankRidge**（冠／serve） | **2026-07-31** ×五 H | 20,40,60,82,120 | **五 H**（對齊 0731 先例） |
| RankGBDT | 2026-06-30 | 20,60 | 20,60（或跟 Ridge 五 H＝另裁） |
| RankXGB | 2026-06-30 | 60 | 60 |
| RankCat | 2026-06-30 | 60 | 60 |
| RankRF | 2026-06-30 | 60 | 60 |
| RankSVM | 2026-06-30 | 20 | 20 |
| RankKNN | 2026-06-30 | 60 | 60 |
| RankMLP | 2026-06-30 | 60 | 60 |

入口：`scripts/train_ranker.py --run --family F --horizon H --asof 2026-08-10 --seed 42`（prodset）。  
先例：`audits/RETRAIN-ASOF-0731-*`（**只 Ridge 五 H**；challenger 未同批）。

## §2 不納入本「所有模型」預設

| 族／臂 | 因 |
|---|---|
| DailyGBDT／DailyLogit／MktLogit／DirStackM 等 | 方向臂；train asof 停 05-31；**另 GO** |
| NF 挑戰（TimesFM／PatchTST／GNN…） | **NF-pause**；多已 STOP；禁默重掃 |
| SeqPatchTST 等 | 已 STOP promote；另契約 |

## §3 建議執行序（確認後才跑）

| 步 | 動作 | 驗收 |
|---|---|---|
| **0** | `run_daily_asof_predict.sh --date 2026-08-10 --horizons 20,60`（或先 `--skip-predict --skip-emit` 只推 feat/core） | fv_max＝core_max＝**08-10** |
| **1** | RankRidge × H∈{20,40,60,82,120} `@08-10` | registry 五列 model_id 含 `2026-08-10` |
| **2** | Challenger 8 族按其「已登錄 H」各 1 槍 `@08-10`（可 `--resume`） | 各 family 有 08-10 產物 |
| **3** | （可選）B3 predict／emit 改掛 08-10 產物 | **另** `SERVE-SWAP`／明示；**預設 no-promote** |

護欄：FZ/GATE · skip-sync · no-SIM-apply · **no-promote-default** · NF-pause。

## §4 工作量粗估

| 包 | 約 |
|---|---|
| 步0 B3（含 predict 20,60） | 既有日更級（小時級視機） |
| 步1 Ridge×5 | 對齊 0731（曾約數分鐘級／H；視資料） |
| 步2 challenger ~9–11 槍 | GBDT／RF／MLP 明顯較慢 |

## §5 Paste 候選（待圈選）

```text
# A 補日更（必／先）
B3-0810-go | D=2026-08-10 | horizons=20,60 | FZ/GATE-keep | no-fake-B3

# B 冠軍重訓
RETRAIN-ASOF-0810-Ridge-go | H=20,40,60,82,120 | seed=42 | no-promote

# C「所有 rank 族」
RETRAIN-ASOF-0810-ALL-RANK-go | Ridge五H + challengers既有H | seed=42 | no-promote | NF-pause
```

*完。inventory-only；未開訓。*
