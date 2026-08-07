---
title: 全部市場預測模型資料檔（庫內＋taxonomy 普查）
status: inventory
series: s4_models
date: 2026-08-07
viewpoint: 2026-08-07T09:40+08:00
role: 本專案「所有預測模型」登記帳（可對帳）
layer: "[I]"
ssot_for: all_prediction_models
depends_on:
  - reports/augur_s4_market_model_families_opt_plan_20260804.md
  - audits/S4-MODELS-TRIED-LIST-20260804.md
  - audits/S4-V1-REVERIFY-EXECUTED-20260806.md
  - audits/S4-V1-REVERIFY-H20-EXECUTED-20260807.md
  - audits/S4-REOPT-BACKLOG-20260807.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
self_reported: true
---

# 全部市場預測模型資料檔 · 2026-08-07

> **一句**：本檔＝專案內**全部預測模型**登記帳——含（A）庫內 `model_registry`／LIVE 掛載、（B）S4 taxonomy Wave A–G 普查族（含誠實 SKIP）。  
> **≠** 確立級／可交易核准；`direction_gate.evaluated_pass=0`。  
> **冠軍（相對／#14）**：`RankRidge`≡B2 · **H60** 主尺 · seed42 · asof-train `2026-06-30`。  
> **LIVE（本檔）**：PriceAdj／`prediction_probability` 頂＝**2026-08-06**；日更主掛 **H20＋H60**。

---

## 0. 計數總覽

| 尺 | 數 | 說明 |
|---|---|---|
| `model_registry` 列 | **27** | 含歷史／ghost；非皆 LIVE |
| registry **family** 字面 | **8** | RankRidge／RankGBDT／DailyGBDT／DailyGBDT_cal／DailyLogit／MktLogit／DirStackM（＋MktLogit_v2 id） |
| LIVE 生產相對掛載（pp＠08-06） | **2** | RankRidge H20＋H60 |
| 架構臂已試（可跑數字） | **5** | RankRidge／RankGBDT·M1／DailyGBDT_cal／MktLogit／DirStackM |
| taxonomy 變體族（計畫矩陣） | **≈35** | Wave A–G；多數 SKIP |
| NF-pause | **on** | 禁默開新族 adapter／train |

---

## 1. LIVE 生產掛載（as-of panel **2026-08-06**）

| H | model_id | econ_verdict | 角色 |
|---|---|---|---|
| **20** | `RankRidge_H20_2026-06-30_seed42_56d03625463b3eba` | **dead** | 短窗相對；V1·H20 net Sharpe≈1.21＞bench |
| **60** | `RankRidge_H60_2026-06-30_seed42_56d03625463b3eba` | thin_unestablished | **主尺**；V1·H60 net Sharpe≈1.25＞bench |

旁掛（較近日 panel 可見、非每日 B3 必出）：H40／H82／H120 同族 `…56d036…`（頂多見至 08-05）。

**非冠軍（已重覆驗·不升格）**：`M1_gbdt`／`RankGBDT`／`ENS_ridge_gbdt`（econ eval 臂；ENS **未**入 registry）。

---

## 2. 庫內 `model_registry` 全表（2026-08-07 傾印）

> 來源：DB `model_registry`（27 列）。`H=0`＝日頻／堆疊方向臂。

| model_id | family | H | seed | train asof | created | 註 |
|---|---|---|---|---|---|---|
| `DailyGBDT` | DailyGBDT | 0 | 0 | 2026-05-31 | 2026-07-11 | direction／日頻 |
| `DailyGBDT_cal` | DailyGBDT_cal | 0 | 0 | 2026-05-31 | 2026-07-11 | **已試**；多 seed OOS |
| `DailyLogit` | DailyLogit | 0 | 0 | 2026-05-31 | 2026-07-11 | direction |
| `DirStackM` | DirStackM | 0 | 0 | 2026-05-31 | 2026-07-11 | **已試** stacking |
| `MktLogit` | MktLogit | 0 | 0 | 2026-05-31 | 2026-07-11 | 大盤方向 |
| `MktLogit_v2` | MktLogit | 0 | 0 | 2026-05-31 | 2026-07-11 | **已試** v2 |
| `RankGBDT_H20_…_seed1_56d036…` | RankGBDT | 20 | 1 | 2026-06-30 | 2026-08-04 | artifact；非熱路徑 |
| `RankGBDT_H20_…_seed2_56d036…` | RankGBDT | 20 | 2 | 2026-06-30 | 2026-08-04 | 同上 |
| `RankGBDT_H20_…_seed42_56d036…` | RankGBDT | 20 | 42 | 2026-06-30 | 2026-08-04 | 同上 |
| `RankGBDT_H60_…_seed1_56d036…` | RankGBDT | 60 | 1 | 2026-06-30 | 2026-08-04 | 同上 |
| `RankGBDT_H60_…_seed2_56d036…` | RankGBDT | 60 | 2 | 2026-06-30 | 2026-08-04 | 同上 |
| `RankGBDT_H60_…_seed42_56d036…` | RankGBDT | 60 | 42 | 2026-06-30 | 2026-08-04 | 同上 |
| `RankRidge_H20_…_ce62866…` | RankRidge | 20 | 42 | 2026-05-31 | 2026-07-11 | 史檔 |
| `RankRidge_H20_…_3a4e66…` | RankRidge | 20 | 42 | 2026-05-31 | 2026-07-11 | 史檔 |
| `RankRidge_H20_…_56d036…` | RankRidge | 20 | 42 | 2026-06-30 | 2026-08-04 | **LIVE** |
| `RankRidge_H40_…_3a4e66…` | RankRidge | 40 | 42 | 2026-05-31 | 2026-07-11 | 史檔 |
| `RankRidge_H40_…_ce62866…` | RankRidge | 40 | 42 | 2026-05-31 | 2026-07-11 | 史檔 |
| `RankRidge_H40_…_56d036…` | RankRidge | 40 | 42 | 2026-06-30 | 2026-08-04 | 旁掛 |
| `RankRidge_H60_…_ce62866…` | RankRidge | 60 | 42 | 2026-05-31 | 2026-07-11 | 史檔 |
| `RankRidge_H60_…_3a4e66…` | RankRidge | 60 | 42 | 2026-05-31 | 2026-07-11 | 史檔 |
| `RankRidge_H60_…_9a880399…` | RankRidge | 60 | 42 | 2026-05-31 | 2026-07-29 | 舊 serve（漂移根因） |
| `RankRidge_H60_…_56d036…` | RankRidge | 60 | 42 | 2026-06-30 | 2026-08-04 | **LIVE 主尺** |
| `RankRidge_H82_…_3a4e66…` | RankRidge | 82 | 42 | 2026-05-31 | 2026-07-11 | **GHOST**（無 artifact） |
| `RankRidge_H82_…_56d036…` | RankRidge | 82 | 42 | 2026-06-30 | 2026-08-06 | 已補 artifact |
| `RankRidge_H120_…_3a4e66…` | RankRidge | 120 | 42 | 2026-05-31 | 2026-07-11 | 史檔 |
| `RankRidge_H120_…_ce62866…` | RankRidge | 120 | 42 | 2026-05-31 | 2026-07-11 | 史檔 |
| `RankRidge_H120_…_56d036…` | RankRidge | 120 | 42 | 2026-06-30 | 2026-08-04 | 旁掛；OOS n 小 |

（表中 `…`＝完整 id 見庫或 §2 全 id 區塊：完整字串在傾印 `/tmp/model-registry-dump-20260807.txt` 與下表。）

### 2.1 RankRidge／RankGBDT 完整 model_id

```
RankRidge_H20_2026-05-31_seed42_ce62866bb62de38b
RankRidge_H20_2026-05-31_seed42_3a4e66fae8cfa2fa
RankRidge_H20_2026-06-30_seed42_56d03625463b3eba
RankRidge_H40_2026-05-31_seed42_3a4e66fae8cfa2fa
RankRidge_H40_2026-05-31_seed42_ce62866bb62de38b
RankRidge_H40_2026-06-30_seed42_56d03625463b3eba
RankRidge_H60_2026-05-31_seed42_ce62866bb62de38b
RankRidge_H60_2026-05-31_seed42_3a4e66fae8cfa2fa
RankRidge_H60_2026-05-31_seed42_9a88039981b5a128
RankRidge_H60_2026-06-30_seed42_56d03625463b3eba
RankRidge_H82_2026-05-31_seed42_3a4e66fae8cfa2fa
RankRidge_H82_2026-06-30_seed42_56d03625463b3eba
RankRidge_H120_2026-05-31_seed42_3a4e66fae8cfa2fa
RankRidge_H120_2026-05-31_seed42_ce62866bb62de38b
RankRidge_H120_2026-06-30_seed42_56d03625463b3eba
RankGBDT_H20_2026-06-30_seed1_56d03625463b3eba
RankGBDT_H20_2026-06-30_seed2_56d03625463b3eba
RankGBDT_H20_2026-06-30_seed42_56d03625463b3eba
RankGBDT_H60_2026-06-30_seed1_56d03625463b3eba
RankGBDT_H60_2026-06-30_seed2_56d03625463b3eba
RankGBDT_H60_2026-06-30_seed42_56d03625463b3eba
```

---

## 3. 已試架構臂（有數字·非僅 registry）

| # | 族／臂 | 熱路徑？ | 最近 #14／方向尺 | 裁決 |
|---|---|---|---|---|
| 1 | **RankRidge／B2_ridge** | **是** | H60≈1.25；H20≈1.21（V1 20260806–07） | **冠軍** |
| 2 | RankGBDT／M1_gbdt | 否（對照） | H60 M1 0.97–1.18（seed2＜bench）；H20 0.75–0.81 全＜bench | **不升格** |
| 3 | DailyGBDT_cal | direction | hit≈0.515–0.516×3 seed | 弱；≠gate |
| 4 | MktLogit_v2 | direction | 大盤基率側 | ≠gate |
| 5 | DirStackM／threelens | direction | hit≈0.50–0.54 | 弱；≠gate |
| — | ENS_ridge_gbdt | eval only | H60／H20 不超 B2 | **不升格**；未入 registry |
| — | B0_random／B1_momentum | econ 基準 | 對照臂 | PARTIAL |

詳見：`audits/S4-MODELS-TRIED-LIST-20260804.md` · V1 EXECUTED 帳。

---

## 4. Taxonomy 全部變體族（市場「應納入 S4 盤點」的模型表）

> SSOT 計畫：`reports/augur_s4_market_model_families_opt_plan_20260804.md`。  
> **狀態字**：`exists`／`partial`／`missing`／`n/a-sim`；Wave 結果＝PASS／SKIP／PARTIAL／defer。

### Wave A — tabular／ranker／direction

| ID | 變體族 | adapter | Wave 結果 |
|---|---|---|---|
| A-3a | LightGBM（M1／RankGBDT） | exists | PASS（不升生產） |
| A-3b | XGBoost | missing | SKIP |
| A-3c | CatBoost | missing | SKIP |
| A-3d | Random Forest | missing | SKIP |
| A-4a | Ridge／RankRidge≡B2 | exists | **PASS／LIVE** |
| A-4b | pairwise／listwise LTR | missing | SKIP |
| A-4c | 截面因子＋shrinkage | partial | PARTIAL |
| A-2a | 線性／邏輯（DailyLogit 等） | partial／exists | PASS（方向） |
| A-2b | SVM | missing | SKIP |
| A-2c | KNN | missing | SKIP |
| A-2d | 樸素貝氏 | missing | SKIP |
| A-2e | 淺層 MLP | missing | SKIP |
| A-D1 | DailyGBDT_cal | exists | PASS |
| A-D2 | market／stack／threelens | exists | PASS |
| A-B0 | B0_random | exists | PARTIAL 基準 |
| A-B1 | B1_momentum | exists | PARTIAL 基準 |

### Wave B — classical TS

| ID | 變體族 | 結果 |
|---|---|---|
| B-1a | ARIMA／SARIMA | SKIP |
| B-1b | GARCH（預測 missing；sim＝n/a-sim） | SKIP／n/a-sim |
| B-1c | VAR／VECM | SKIP |
| B-1d | Kalman／狀態空間 | SKIP |
| B-1e | 協整 | SKIP |

### Wave C — sequence DL

| ID | 變體族 | 結果 |
|---|---|---|
| C-5a | RNN | SKIP |
| C-5b | LSTM／BiLSTM | SKIP |
| C-5c | GRU | SKIP |
| C-5d | CNN-LSTM | SKIP |
| C-5e | TCN | SKIP |

### Wave D — Transformer TS

| ID | 變體族 | 結果 |
|---|---|---|
| D-6a | Transformer TS | SKIP |
| D-6b | Informer／Autoformer | SKIP |
| D-6c | PatchTST | SKIP |

### Wave E — 圖

| ID | 變體族 | 結果 |
|---|---|---|
| E-7a | GCN／GAT | SKIP |
| E-7b | 股權／產業／相關性圖＋時序 | SKIP |

### Wave F — RL

| ID | 變體族 | 結果 |
|---|---|---|
| F-8a | DQN／PPO／A2C | SKIP／defer |
| F-8b | portfolio RL | SKIP／defer |
| F-8c | MARL | SKIP／defer |

### Wave G — 混合／NLP／LLM／貝氏

| ID | 變體族 | 結果 |
|---|---|---|
| G-9a | ML+DL stacking（DirStackM） | partial 既有 |
| G-9b | GBDT+LSTM | SKIP |
| G-9c | 真 ensemble／blending | SKIP（ENS eval≠registry） |
| G-10a | 新聞／社群情緒 | SKIP／partial 非預測頭 |
| G-10b | 事件抽取→預測頭 | SKIP |
| G-10c | 主題模型＋下游 | SKIP |
| G-11a | LLM 特徵／情緒 | partial（advisor；**非**價預測器） |
| G-11b | RAG／agentic | partial（advisor） |
| G-12a | 貝氏層級 | SKIP |
| G-12b | GP | SKIP |
| G-12c | 遺傳規劃／符號回歸 | SKIP |

---

## 5. 與「其他模型驗証」對照

| 軌 | 狀態 | 本檔關係 |
|---|---|---|
| V0 | ✅ | 本檔＝刷新後的全量登記 |
| V5／V1·H60／V1·H20／V3 | ✅ | §1–3 已吸收結論 |
| V2／V4 | NF-pause | §4 SKIP 池待撤 pause 後才開訓 |

---

## 6. 路徑與刷新

| 產物 | 路徑 |
|---|---|
| **本資料檔（SSOT）** | `audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md` |
| 族計畫 | `reports/augur_s4_market_model_families_opt_plan_20260804.md` |
| 已試清單（08-04） | `audits/S4-MODELS-TRIED-LIST-20260804.md` |
| 再優 backlog | `audits/S4-REOPT-BACKLOG-20260807.md` |
| registry 傾印（作業暫存） | `/tmp/model-registry-dump-20260807.txt` |

刷新條件：新 family 入庫、LIVE 換掛、或 Wave／V1 重跑後另開 `…-INVENTORY-<date>.md`（本檔可留作基線）。

---

## 7. 誠實界

1. **列出 ≠ 已訓通過 ≠ 可交易**。  
2. SKIP 族不得改稱已驗証綠。  
3. advisor／Ollama **不是**價預測模型。  
4. sim／GARCH 風險路徑 **不得**冒充 S4 預測通過。  
5. `evaluated_pass=0` → 禁絕對方向確立級宣稱。

*完。[I] inventory；self-reported。*
