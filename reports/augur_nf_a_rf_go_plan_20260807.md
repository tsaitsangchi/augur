---
title: NF-A-RF · Random Forest 族 plan-first（有界撤 pause）
status: adopted
series: s4_models
track: NF-A-RF
date: 2026-08-07
viewpoint: 2026-08-07T09:48+08:00
adopted: audits/NF-A-RF-PLAN-ADOPTED-20260807.md
paste: "NF-A-RF-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30"
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
v2: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
prior_eval: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
layer: "[I]"
role: A-3d RankRF 有界解凍計畫；零默訓；誠實記「碼已在、前評未過門」
self_reported: true
---

# NF-A-RF-go-plan｜RankRF（Random Forest）· 2026-08-07

> **Steward 選**：`NF-A-RF-go-plan`（非 XGB）。  
> **一句**：對 **A-3d／`RankRF`** 開「有界撤 NF」**計畫**——歷史 prodset 可再訓／再 #14；**本檔≠開訓 GO**。  
> **誠實前提**：`src/augur/models/ranker.py` 之 **`RankRF` 薄殼已存在**；`train_ranker --family RankRF` 可 dispatch；`audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md` 已評 **未過冠軍門**（H60／H20）。INVENTORY 寫 `missing`＝taxonomy 舊 SKIP 標，**碼實況＝exists／前評未升格**。

---

## §0 護欄

```text
NF-A-RF-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30 | hold-#1
# ≠ NF-A-RF-go（執行訓）；≠ 撤全域 NF-pause；≠ 升格生產；≠ 假 pass
```

| 可（本計畫書） | 不可 |
|---|---|
| 寫解凍邊界／歷史窗／#11·#14 尺／預凍冠軍門檻 | 本句開 `train_ranker --run` |
| 釐清 adapter **已在** | 把 08-04 未過門改稱通過 |
| 排執行 GO paste | 連帶解凍 XGB／GNN／ARIMA |
| hold #1 B3＠08-07 | sim `--apply`；改 dgate |

---

## §1 為什麼是 RF（對 V2）

| 項 | 值 |
|---|---|
| V2 優先 | **1**（與 XGB 並列；Steward 選 RF） |
| 歷史資料 | 同 RankRidge：prodset active3 · `until=2026-06-30` |
| adapter | **`RankRF` exists**（非從零寫碼） |
| 前評 | sklearn-EVAL：**未過門**（H60 max Sharpe≈1.12＜冠軍 1.30；H20 亦未過） |
| 再開意義 | 可選**同尺重覆驗**（V1 軟差域／特徵凍結後）— **預期仍難升格**；誠實重跑≠赌贏 |

---

## §2 有界撤 pause（僅 A-3d）

若 Steward 後續貼 **`NF-A-RF-go`**（執行句）：

1. **僅**授權 `family=RankRF` 歷史窗作業；**全域** `NF-pause` 對其他族 **仍 keep**。  
2. 預設指令矩陣（執行波·示意）：

```bash
# 註：須另句 NF-A-RF-go 才跑
for s in 42 1 2; do
  PYTHONPATH=src ./venv/bin/python scripts/train_ranker.py --run \
    --family RankRF --horizon 60 --seed "$s" --asof 2026-06-30 --feature-source=prodset
done
# #14：現行 run_economic_eval 主迴圈為 B2/M1/ENS——RankRF 終關路徑須接 portfolio 已有
# _WAVE_A_SKLEARN_FAMILIES 或等價 probe（見 prior EVAL）；執行帳須標數字來源
```

3. 驗收：#11 min／med／max；#14 vs **預凍**冠軍（寫死後再跑）：

| 尺 | 預凍對照（CLAUDE #32b） |
|---|---|
| H60 RankRidge | net Sharpe **1.3016**／hit **0.6316**（S5-OOS；或 V1 重跑 1.25／58% 作軟參照、門檻以寫死值為準） |
| 升格 | 三 seed **皆**優於冠軍門檻且 hit 不劣 bench——否則 **STOP promote**（與 GBDT／ENS 同） |

4. **禁**：單 seed 勝出謊；默換 LIVE serve；改 `evaluated_pass`。

---

## §3 與既有交叉

| 檔 | 關係 |
|---|---|
| `S4-NF-PAUSE-ACCEPTED` | 本 plan＝其「另句 `NF-*-go-plan`」路徑 |
| `S4-V2-SKIP-HIST-QUEUE-ADOPTED` | RF＝優先 1；歷史窗契約沿用 |
| `S4-WAVE-A-SKLEARN-EVAL` | 前評未過門＝本再開之先驗 |
| `ranker.RankRF`／`train_ranker` | 執行期零新 class（除非缺陷修復另 GO） |

---

## §4 Paste-ready

採納本計畫（仍零開訓）：

```text
NF-A-RF-plan-adopt | FZ/GATE-keep | NF-pause-others | no-train | hold-#1
```

有界執行（歷史重訓＋#14；另句）：

```text
NF-A-RF-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default
```

維持 pause、不開 RF：

```text
NF-pause-keep
```

---

## §5 驗收（本計畫書）

1. 能復述：RankRF **碼已在**、08-04 **未過門**、本檔只 plan。  
2. 有界撤 pause ≠ 全域解凍。  
3. 歷史窗／#11／#14／預凍門檻已寫。  
4. 未開訓、未假 B3、未改 dgate。

*完。[I] plan_first。*
