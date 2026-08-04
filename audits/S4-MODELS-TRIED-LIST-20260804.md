# S4 已試模型清單 · 2026-08-04

> **位階**：[I] 唯讀盤點（非 META [N]）。  
> **窗**：P1-DRIFT A＋C（S4 主刀路徑＝`P1-DRIFT: C-go`）。  
> **證據**：`audits/P1-DRIFT-C-EXECUTED-20260804.md` · `audits/P1-DRIFT-A-EXECUTED-20260804.md` · `/tmp/p1-drift-c-*.log`。  
> **DB**：本輪 `psql` connection refused——未用 registry 補列。  
> **計畫對照**：`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §0.5／§2 S4（「多種模型」＝多架構／多 horizon 臂＋多 seed；≠單臂單 seed）。  
> **市場族擴張（待 GO）**：`reports/augur_s4_market_model_families_opt_plan_20260804.md` · 登錄 `audits/S4-MARKET-FAMILIES-PLAN-20260804.md`——taxonomy ≈12 大類／≈35 變體族入 S4 波次；**本清單仍僅 2 族基線，≠普查完成**。

---

## 1. 計數（本窗）

| 尺 | 數 | 說明 |
|---|---|---|
| **distinct 模型族（架構）** | **2** | (1) Ridge／RankRidge（含 econ `B2_ridge`；`train_ranker` 註 RankRidge≡B2）(2) GBDT／`M1_gbdt` |
| train 登錄 artifact 族 | 1 | 僅 `RankRidge`（`RankGBDT` **未** `--family` 訓練） |
| econ ladder 標籤 | 2 | `B2_ridge`＋`M1_gbdt`（`run_economic_eval` 固定雙臂） |

---

## 2. 已試清單

### 2.1 RankRidge（生產 train／serve）

| horizon | seed | model_id | 來源 | metric／驗收 note |
|---|---|---|---|---|
| H60 | 42 | `RankRidge_H60_2026-06-30_seed42_56d03625463b3eba` | A 重產；C `--resume` 跳過 | prodset active3；dry-run 綠；經濟尺見 B2 |
| H20 | 42 | `RankRidge_H20_2026-06-30_seed42_56d03625463b3eba` | C 新產 | 同上；artifact 落地 |

### 2.2 B2_ridge（經濟終關；對齊 RankRidge 族）

| horizon | seed | model_id | note |
|---|---|---|---|
| H60 | （確定性） | （無獨立 train model_id；walk-forward） | top20%/equal net Sharpe **1.30**＞基準 **1.09** |
| H20 | （確定性） | 同上 | 各 top 分位 net Sharpe／Calmar 皆優於基準（基準 0.87） |

### 2.3 M1_gbdt（經濟終關；非生產熱路徑）

| horizon | seed(s) | model_id | note |
|---|---|---|---|
| H60 | 1／2／42（#11 三 seed） | （無 RankGBDT artifact） | top20%/equal net Sharpe min／median／max／mean＝**1.031／1.090／1.153／1.091**；中位≈基準 1.094——**不得**單 seed 宣稱勝出 |
| H20 | 42 only | 同上 | top10/20/30 equal net Sharpe 0.69／0.66／0.76 **皆劣於**基準 0.87 |

---

## 3. 同 audit 歷史錨（非本窗「新試族」）

| 項 | 值 |
|---|---|
| A 執行前舊 serve | `RankRidge_H60_2026-05-31_seed42_9a88039981b5a128`（prodset n_feats=2；`mean_20d` 雙顆——漂移拒載根因） |
| 族 | 仍為 RankRidge；**不算**新家族 |

---

## 4. 未試（相對 S4 計畫／C 殘餘）

| 項 | 狀態 |
|---|---|
| H40／H120 prodset 重產 | **未做**（C §6） |
| `train_ranker --family RankGBDT` | **未做**（僅 econ `M1_gbdt`） |
| direction 族（`train_daily_direction` 等） | **未做**（S4 計畫「至少 ranker／direction」之 direction 臂） |
| H20 GBDT ≥3 seed | **未做**（C 殘；單 seed 已劣基準） |
| B canonical-arm | **未授權** |
| TWEVO／PME 八閘→人 APPLY | **非**本 C 執行帳範圍（S4 完整驗收仍缺此段） |
| predict 寫庫／SIM apply／direction_gate／確立級 | **未做** |

---

## 5. 一句對 parent

**本窗實際試過 2 種模型族（RankRidge／B2_ridge · M1_gbdt）；train artifact 僅 RankRidge×H20/H60×seed42；GBDT 僅經濟臂（H60 三 seed、H20 單 seed）。H40/H120、RankGBDT train、direction 族皆未試。**

*完。*
