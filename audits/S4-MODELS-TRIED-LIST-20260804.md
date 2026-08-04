# S4 已試模型清單 · 2026-08-04

> **位階**：[I] 唯讀盤點（非 META [N]）。  
> **窗**：P1-DRIFT A＋C ＋ **S4-WAVE-A**（`audits/S4-WAVE-A-EXECUTED-20260804.md`）＋ LOOP-S4-TO-S5 OOS（若有）。  
> **證據**：`/tmp/s4-wave-a-20260804/` · `audits/S4-WAVE-A-EXECUTED-20260804.md` · `audits/P1-DRIFT-C-EXECUTED-20260804.md`。  
> **計畫對照**：`reports/augur_s4_market_model_families_opt_plan_20260804.md` Wave A（**≠**全普查完成）。  
> **as-of**：`2026-06-30` prodset。

---

## 1. 計數（本窗累積）

| 尺 | 數 | 說明 |
|---|---|---|
| **distinct 模型族（架構）** | **5** | (1) RankRidge／B2 (2) RankGBDT／M1 (3) DailyGBDT_cal (4) MktLogit_v2 (5) DirStackM／threelens HistGBM |
| train 登錄 artifact 族 | **2** | RankRidge＋RankGBDT（截面 ranker） |
| direction 臂 | **3** | DailyGBDT_cal＋MktLogit_v2＋DirStackM／threelens |
| SKIP（missing adapter） | **8** | XGB／Cat／RF／LTR／SVM／KNN／NB／淺 MLP |

---

## 2. 已試清單

### 2.1 RankRidge（生產 train）

| horizon | seed | model_id | 來源 | #14 top20%/equal net Sharpe（vs 基準） |
|---|---|---|---|---|
| H60 | 42 | `RankRidge_H60_2026-06-30_seed42_56d03625463b3eba` | A／C／Wave A resume | **1.30**（基準 1.09） |
| H20 | 42 | `RankRidge_H20_2026-06-30_seed42_56d03625463b3eba` | C／Wave A resume | （P1-C／S5；本窗未重跑全表 econ） |
| H40 | 42 | `RankRidge_H40_2026-06-30_seed42_56d03625463b3eba` | Wave A 新訓 | **1.14**（基準 1.07） |
| H120 | 42 | `RankRidge_H120_2026-06-30_seed42_56d03625463b3eba` | Wave A 新訓 | **1.22**（基準 1.00；僅 8 期——小樣本） |

### 2.2 RankGBDT（Wave A train；非生產熱路徑）

| horizon | seed(s) | model_id 形 | note |
|---|---|---|---|
| H60 | 1／2／42 | `RankGBDT_H60_2026-06-30_seed{1,2,42}_56d03625463b3eba` | artifact 落地；econ M1 top20% net≈基準 |
| H20 | 1／2／42 | `RankGBDT_H20_2026-06-30_seed{1,2,42}_56d03625463b3eba` | artifact 落地 |

### 2.3 M1_gbdt（#14／#11）

| horizon | seed(s) | top20%/equal net Sharpe |
|---|---|---|
| H60 | 1／2／42 | min／med／max／mean＝**1.031／1.090／1.153／1.091**（基準 1.094）——**不得**單 seed 勝出 |
| H20 | 1／2／42 | min／med／max／mean＝**0.625／0.659／0.672／0.652**（基準 0.869）——皆劣 |

### 2.4 Direction

| 臂 | model_id | seeds | metrics |
|---|---|---|---|
| DailyGBDT_cal（A-D1） | `DailyGBDT_cal` k=5 | 3 | hit seed0/1/2＝0.5161／0.5149／0.5161；pooled **0.5157**；brier 0.2551；n=3,626,103 |
| MktLogit_v2（A-D2） | `MktLogit_v2` | — | H20 folds=4189；大盤基率 p̄=0.646 |
| DirStackM（A-D2） | DirStackM | — | H20 月頻 OOS 35356 列；p̄=0.516 |
| threelens（A-D2） | HistGBM 冒煙 | 3 avg | H40 OOS hit **0.5218** brier 0.2553（≠gate） |

---

## 3. 歷史錨（非本窗新族）

| 項 | 值 |
|---|---|
| 舊 serve（漂移根因） | `RankRidge_H60_2026-05-31_seed42_9a88039981b5a128` |

---

## 4. 未試／殘餘

| 項 | 狀態 |
|---|---|
| XGB／Cat／RF／LTR／SVM／KNN／NB／淺 MLP | **SKIP** until adapter |
| 字面 B0_random／B1_momentum 臂 | PARTIAL（僅 econ 基準） |
| direction_gate evaluate／確立級 | **未做** |
| predict 寫庫／SIM apply | **未做** |
| Wave B+ | 另句 GO |

---

## 5. 一句

**Wave A：RankRidge×4H＋RankGBDT×2H×3seed＋DailyGBDT_cal×3seed＋A-D2 三臂已落地；GBDT H20 經濟尺劣基準；missing 八族 SKIP；≠確立級。**

*完。*
