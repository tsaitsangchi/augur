# S4 已試模型清單 · 2026-08-04

> **位階**：[I] 唯讀盤點（非 META [N]）。  
> **窗**：P1-DRIFT A＋C ＋ **S4-WAVE-A…G**（**全波次收口**） ＋ LOOP-S4-TO-S5 OOS（若有）。  
> **證據**：`/tmp/s4-wave-{a,b,c,d,e,f}-20260804/` · Wave A–G EXECUTED。  
> **計畫對照**：`reports/augur_s4_market_model_families_opt_plan_20260804.md` Wave A–G（taxonomy ≈12 大類普查收官；≠逐族全訓練）。  
> **as-of**：`2026-06-30` prodset。

---

## 1. 計數（本窗累積）

| 尺 | 數 | 說明 |
|---|---|---|
| **distinct 模型族（架構）** | **5** | (1) RankRidge／B2 (2) RankGBDT／M1 (3) DailyGBDT_cal (4) MktLogit_v2 (5) DirStackM／threelens HistGBM |
| train 登錄 artifact 族 | **2** | RankRidge＋RankGBDT（截面 ranker） |
| direction 臂 | **3** | DailyGBDT_cal＋MktLogit_v2＋DirStackM／threelens |
| SKIP（missing adapter）Wave A | **8** | XGB／Cat／RF／LTR／SVM／KNN／NB／淺 MLP |
| SKIP（missing／n/a-sim）Wave B | **5** | ARIMA／GARCH(預測)／VAR／Kalman／協整（GARCH sim＝n/a-sim 分尺） |
| SKIP（missing）Wave C | **5** | RNN／LSTM／GRU／CNN-LSTM／TCN（無 sequence panel） |
| SKIP（missing）Wave D | **3** | Transformer／Informer／Autoformer／PatchTST（`transformers` 套件在≠adapter） |
| SKIP（missing）Wave E | **2** | GCN／GAT；產業／相關性圖（`knowledge_edge`＝KH 知識圖≠股票圖） |
| SKIP／defer Wave F | **3** | DQN／PPO／A2C；portfolio RL；MARL（碼庫確認無 RL 套件／無自動下單） |
| partial（既有，不重訓）Wave G | **2** | `DirStackM`（stacking）；advisor／Ollama（LLM 輔助，非價預測器） |
| SKIP Wave G | **8** | GBDT+LSTM／真 ensemble／新聞情緒／事件抽取／主題模型／貝氏／GP／符號回歸 |

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
| ARIMA／SARIMA／VAR／Kalman／協整 | **SKIP**（Wave B 列帳；薄殼另 plan） |
| GARCH（預測熱路徑） | **SKIP**；sim GARCH＝**n/a-sim**（不得冒充預測綠） |
| RNN／LSTM／GRU／CNN-LSTM／TCN | **SKIP**（Wave C；缺 sequence panel／adapter） |
| Transformer／Informer／Autoformer／PatchTST | **SKIP**（Wave D；同一序列窗契約缺口） |
| GCN／GAT／股票圖邊 | **SKIP**（Wave E；無圖套件／無股票圖邊表） |
| DQN／PPO／A2C／portfolio RL／MARL | **SKIP／defer**（Wave F；另尺；禁自動下單；無 RL 套件） |
| GBDT+LSTM／真 ensemble／新聞情緒／事件頭／主題模型／貝氏／GP／符號回歸 | **SKIP**（Wave G；8 族；advisor／LLM 非價預測器已明註） |
| 字面 B0_random／B1_momentum 臂 | PARTIAL（僅 econ 基準） |
| direction_gate evaluate／確立級 | **未做** |
| predict 寫庫／SIM apply | **未做** |
| **S4 Wave A–G** | **已全波次收口**（本帳）；非「新 Wave」，後續＝C2 回饋或 S3 序列窗契約 |
| **追記 2026-08-04**：S3-WAVE-D | Wave C/D/E 之「序列窗契約缺／圖邊表缺」根因**已解（含資料落地，Phase 2c）**（`audits/S3-WAVE-D-EXECUTED-20260804.md`：序列窗 library 已測 225/225 足窗；`stock_graph_edge` 13,021 邊已寫入）；下表 Wave C/D/E 之 SKIP 理由**維持原始紀錄不改**（歷史留痕），現況更新見該檔——殘餘 SKIP 理由已轉為「adapter 訓練碼仍缺」，非「無序列/圖契約或資料」 |

---

## 5. 一句

**Wave A**：RankRidge×4H＋RankGBDT×2H×3seed＋DailyGBDT_cal×3seed＋A-D2 三臂已落地；GBDT H20 經濟尺劣基準；missing 八族 SKIP；≠確立級。  
**Wave B**：classical TS 五族 **誠實 SKIP**／GARCH＝n/a-sim；≠假訓。  
**Wave C**：sequence DL 五族 **誠實 SKIP**（無 sequence panel；torch 在≠adapter）。  
**Wave D**：Transformer TS 三族 **誠實 SKIP**（同序列窗契約缺口；`transformers` 在≠adapter）。  
**Wave E**：圖／關係兩族 **誠實 SKIP**（無圖套件；`knowledge_edge`＝KH 知識圖，**≠**股票／產業圖邊）。  
**Wave F**：RL 三族 **誠實 SKIP／defer**（另尺；碼庫確認無 RL 套件／無自動下單路徑；初篩 2 檔字面誤配已逐一核實非 RL）。  
**Wave G**：混合／NLP／LLM／貝氏 **2 partial 既有**（`DirStackM`／advisor）**＋8 誠實 SKIP**；advisor 明註非價預測器、DDL 禁流入 `feature_values`。

**S4 taxonomy A–G 全波次收口（本帳里程）**：≈12 大類／≈35 變體族普查完成——生產熱路徑仍僅 Wave A 三臂（RankRidge／RankGBDT／direction）；餘皆誠實 SKIP／partial，**非**逐族全訓練。**IC／SKIP 普查 ≠ 可交易**（dgate pass=0 仍在）。

*完。*
