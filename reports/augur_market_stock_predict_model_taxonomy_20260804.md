# 市場股票預測模型分類學（實務筆記）· 2026-08-04

> **位階**：[I] 研究筆記（非 META [N]；非全球普查、非「恰好 N 種」權威計數）  
> **關鍵詞**：stock prediction · taxonomy · ML · DL · RL · LLM · cross-section · time-series  
> **對照**：`audits/S4-MODELS-TRIED-LIST-20260804.md`（專案已試集 ≠ 市場版圖）  
> **來源性質**：2025–2026 綜述／產業常見用法之合成；數字為**實務分桶**，非 census。

---

## 1. 「共有多少種？」誠實判決

**沒有單一權威的全球總數。**  
「股票預測模型」的計數邊界會隨下列軸漂移，故任何「全世界恰好 N 種」皆屬假精確：

| 軸 | 為何會把 N 拉大／拉小 |
|---|---|
| 任務 | 價格回歸／方向分類／截面排序／波動／組合／下單策略 |
| 粒度 | 架構族 vs 具體實作（含 hyperparam／特徵集）vs 論文變體名 |
| 市場 | 單資產時序 vs 全市場截面 vs 多資產／多模態 |
| 是否含交易決策 | 純預測 vs RL／執行一體化 |

**實務可說**：約 **10–12 大類**、其下約 **30–40 常見變體族**；論文／產品命名則遠多於此、且持續增生。

---

## 2. 實務分類表（約 2025–2026）

| # | 大類（family） | 常見變體族（例） | 典型任務 |
|---|---|---|---|
| 1 | 古典統計／計量 | ARIMA／SARIMA、GARCH 族、VAR／VECM、狀態空間／Kalman、協整 | 單序列價／波動／均值回歸 |
| 2 | 古典監督式 ML | 線性／邏輯回歸、SVM、KNN、樸素貝氏、淺層 MLP | 方向／收益回歸 |
| 3 | 樹集成／GBDT | Random Forest、XGBoost、LightGBM、CatBoost | 截面排序、異質特徵表 |
| 4 | 截面排序／Learning-to-Rank | Ridge／線性 ranker、pairwise／listwise LTR、截面因子＋shrinkage | 全市場相對強弱（非單股點預測） |
| 5 | 時序深度學習 | RNN、LSTM／BiLSTM、GRU、CNN-LSTM、TCN | 單／多序列價量路徑 |
| 6 | Attention／Transformer 時序 | Transformer、Informer／Autoformer 類、PatchTST 類時序 foundation | 長依賴時序、多變量 |
| 7 | 圖／關係網路 | GCN／GAT、股權／產業／相關性圖＋時序混合 | 跨股聯動、產業結構 |
| 8 | 強化學習交易 | DQN／PPO／A2C、portfolio RL、MARL | 序列決策／下單／倉位（≠純點預測） |
| 9 | 混合／堆疊集成 | ML+DL stacking、GBDT+LSTM、blending／ensemble | 降方差、多信號融合 |
| 10 | 另類資料／情緒 NLP | 新聞／社群情緒、事件抽取、主題模型＋下游預測頭 | 文本→信號 |
| 11 | Foundation／LLM 輔助 | LLM 特徵／情緒、檢索增強假說、agentic 研究輔助（常作特徵或流程，少作唯一價預測器） | 文本理解＋管線編排 |
| 12 | 貝氏／機率與演化（較niche） | 貝氏層級、GP、遺傳規劃／符號回歸 | 不確定性、可解釋結構搜尋 |

**計數摘要（本筆記分桶）**：大類 **≈12**；上表列舉之常見變體族合計約 **35±5**（可再細拆、亦可合併）。

---

## 3. 與 augur S4 已試集對照（勿混淆）

來源：`audits/S4-MODELS-TRIED-LIST-20260804.md`（P1-DRIFT A＋C 窗）。

| 尺 | 市場景觀（本筆記） | augur S4 本窗 |
|---|---|---|
| 模型族（架構） | 約 10–12 大類 | **2**：RankRidge（含 econ `B2_ridge`）、`M1_gbdt` |
| 對應大類 | — | 落在 **#4 截面排序** 與 **#3 樹集成／GBDT** |
| 未覆蓋（相對市場） | #1–2、#5–12 等 | direction 族、RankGBDT train、時序 DL、RL、LLM 等皆**未試** |

一句：**市場版圖 ≠ 專案已試集**；S4「多種模型」指計畫內多架構／多 horizon／多 seed，不是宣稱已覆蓋市場各大類。

---

## 4. 參考錨（綜述方向，非窮舉）

- 傳統→ML/DL/RL→LLM 統一分類取向（Computational Economics 2025 綜述類）
- NN 架構 meta-review（ANN/MLP、CNN、LSTM、GRU、hybrid；2010–2025）
- 階層圖常見四分：ensemble／DL／classical time-series／ML regression（Frontiers 等 AI 市場預測綜述）

---

## 5. 與 augur 計畫閉環交叉（2026-08-04）

| 檔 | 角色 |
|---|---|
| `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` | 管線 S0–S5＋C1／C2／C0 |
| `reports/augur_s3_features_for_market_model_families_20260804.md` | 本 taxonomy → S3 特徵類別 |
| `reports/augur_s4_market_model_families_opt_plan_20260804.md` | 本 taxonomy → S4 波次驗証 |
| `reports/augur_s1_s2_s3_closed_loop_plan_20260804.md` | 閉環 C1：S3→S2→擴大 S1→重驗 |

*完。*
