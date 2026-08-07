---
status: adopted
series: s4_s5_verify
track: V2
date: 2026-08-07
viewpoint: 2026-08-07T09:45+08:00
adopted: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
parent: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
layer: "[I]"
role: SKIP 族×歷史窗契約排隊（零開訓·零撤 NF）
self_reported: true
---

# V2｜缺 adapter 族 · 歷史資料訓練／驗証排隊 · 2026-08-07

> **Steward**：依 INVENTORY；「用過去資料做特徵收集＋訓練＋驗証」→ **先文件排隊**。  
> **一句**：可以、且本專案**本來就**用過去庫內 as-of 資料做 walk-forward——但 **新族須 adapter＋撤 NF**；本檔**只排優先、不開訓**。

---

## §0 歷史資料徑（原則答）

| 問 | 答 |
|---|---|
| 可否用過去資料？ | **可**——價／特徵／panel 皆庫內歷史；`until`／`asof` 釘網格（例 `2026-06-30` prodset） |
| 怎麼算「合法」？ | **as-of 凍結**＋purged／embargo walk-forward；禁偷看未來窗；#11≥3 seed（隨機臂）；#14 econ；方向≠確立級 |
| 既有族？ | RankRidge／M1／direction：**已**用歷史重覆驗（V1·H60／H20）；可再重跑但不須新特徵宇宙 |
| SKIP 新族？ | 先 **adapter**；特徵契約對齊 S3 矩陣；再開 `NF-*-go-plan` 撤 pause 後 train |
| 現在能默訓嗎？ | **否**——NF-pause **on**；本檔≠授權 train |

```text
V2-QUEUE-plan | FZ/GATE-keep | NF-pause | no-train | hold-#1
# 歷史窗預設: since=2021-01-01 until=2026-06-30 feature_source=prodset（或族契約明示）
```

---

## §1 與開問題板

| # | ∥？ | 本檔 |
|---|---|---|
| **1** A→B3＠08-07 | 主軸；本檔不搶 | hold |
| **18** 其他模型 | V2＝本檔 | 文件 ✅ |
| **10** NF | 疊加 pause | 不撤 |

---

## §2 SKIP 優先排隊（歷史可訓性）

> 尺：資料是否已在庫＋契約是否夠＋adapter 缺口大小。1＝可率先薄殼探針（仍須另 GO）。

| 優先 | 族（INVENTORY ID） | 歷史資料？ | 缺什麼 | 建議下一句（另授） |
|---|---|---|---|---|
| **1** | A-3b XGBoost | 同截面 panel／prodset | ranker adapter＋CLI | `NF-A-XGB-go-plan` → thin shell |
| **1** | A-3d Random Forest | 同 | **`RankRF` 碼已在**；前評未過門；plan=`reports/augur_nf_a_rf_go_plan_20260807.md` | `NF-A-RF-go-plan` ✅ 本窗；執行另 `NF-A-RF-go` |
| **2** | A-3c CatBoost | 同 | 套件＋族字面 | `NF-A-CAT-go-plan` |
| **2** | A-2b／A-2e SVM／淺 MLP | 同 | adapter | 低優先於樹模 |
| **3** | B-1a ARIMA | 單股價序列有 | 截面彙總尺＋薄殼 | `S4-ARIMA-P1-go`（另決策） |
| **3** | B-1c VAR | 多序列契約 | panel 契約 | defer |
| **4** | C／D 序列 DL／Transformer | 序列窗契約（S3-D 已有部分落地） | **訓練 adapter 仍缺** | 契約復查後再排隊 |
| **5** | E 圖 GNN | `stock_graph_edge` 有邊≠消費 | GRAPH-CONSUME G2→再 adapter | 先 #7 G2 |
| **6** | F RL | — | 禁自動下單；另尺 | defer |
| **7** | G NLP／貝氏／GP… | 多數缺預測頭 | — | SKIP 維持 |

**不排進「歷史重訓」**：LIVE 冠軍 RankRidge（已夠）；ENS 未過門；advisor／LLM（非價預測器）。

---

## §3 歷史特徵收集契約（文件）

| 步 | 做什麼 | 不做什麼 |
|---|---|---|
| F1 | 讀 prodset／canonical 特徵名與 as-of 覆蓋 | 為新族 silently 寫入 production `feature_values` |
| F2 | 候選先 `feature_candidate_values`（若開材料化） | 偷看驗證窗 |
| F3 | 與族需求對照 S3 特徵矩陣 | 把 SKIP 改稱「已收集＝已驗通過」 |

既有熱路徑特徵（active3）：`cycle_position_252d`／`inst_cumflow_position_120d`／`lending_fee_rate_mean_30d`——**夠 RankRidge／M1**；新樹模可先同尺，再談增量特徵。

---

## §4 驗証尺（開訓後才用；本檔不跑）

1. #11 多 seed 分布（禁單 seed 勝）  
2. #14 `run_economic_eval --feature-source=prodset --until <釘>`  
3. 與 RankRidge H60 預凍對照（冠軍門檻寫死後再跑）  
4. `evaluated_pass` **不得**因本訓變綠  

---

## §5 Paste-ready

```text
V2-QUEUE-adopt | FZ/GATE-keep | NF-pause | no-train | hold-#1
```

開第一個歷史薄殼（另決策＋撤 pause）：

```text
NF-A-RF-go-plan
# 或 NF-A-XGB-go-plan | GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30
```

---

## §6 驗收（本檔）

1. 能復述：過去資料**可以**訓／驗，路徑＝as-of purged。  
2. 現況 **不能**默開 SKIP 族 train（NF-pause）。  
3. 優先 1–2 族已點名（XGB／RF）。  
4. 未開訓、未改 dgate、未假 B3。

*完。[I] plan_first。*
