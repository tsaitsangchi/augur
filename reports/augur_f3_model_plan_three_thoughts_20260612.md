# augur F3 模型計畫 — 三思想特徵體系 → 預測模型可行性與設計(2026-06-12)

**性質**:設計計畫(#15:計畫、非成果;一切預測力主張皆為假說,唯 walk-forward 裁決)。
**前提**:三思想特徵(第一性/Pareto 思想/康波循環思想)已產生、完整且準確(F2 完成後)。
**命題**:以此三思想為基礎,建「預測個股股價」的新模型,是否可行?

---

## 〇、可行性判斷(誠實 #15)

**結論:可行——但必須先正名,且預測力是假說、不是承諾。**

1. **正名(靈魂判準,不可違)**:augur 不預測「股價」(絕對價格/點位)——那是明牌思維。
   可行且該做的是:**給定 as-of 日 t,預測各核心股未來 H 日的橫斷面相對強弱(排序)→ top-N**,
   H ∈ 週/月/季/年,並附可信度(walk-forward IC / Effective-t / 勝率)。以下「模型」皆指此。
2. **為什麼可行**:
   - 三族特徵=三個**互補**資訊鏡頭(內容/分布形狀/時間結構),異質表格特徵正是樹家族(GBDT)的主場;
   - 樹模型天然擅長非線性交互(相位×集中度×動能),與三思想的交互假說(共振/支配/缺口)對口;
   - augur 防護鏈完整(#8 purged walk-forward/#11 五鏡/#12 單一引用源/#14 經濟價值/#15 誠實)→
     就算 alpha 微弱,**結論本身可信**——這是 augur 對「可行」的定義。
3. **誠實邊界**:台股橫斷面 alpha 可能微弱(rank IC 0.02-0.05 級即具實用價值);成功定義=
   「每個數字可溯源、out-of-sample 撐住、半年後重跑一致」,**不是**「回測賺很多」。
   若三思想特徵經消融證明無增量 → 負結果同樣入檔(#15),那也是可行性研究的合法產出。
4. **「新模型」的定義**:非發明新演算法;是「**三思想特徵體系 × 樹家族 ensemble × 多週期
   purged walk-forward**」之 augur 專屬組合。transformer 為輔、後期(隔離 venv,deferred)。

## 一、模型設計

### 1.1 預測目標(label;#8 紅線)
- **label = H 日後向前報酬**(還原價 `PriceAdj` log return,t+1 進場口徑)→ **同日橫斷面標準化**
  (rank/z;可選產業內中性化)。H ∈ {5, 20, 60, 252}(週/月/季/年,calendar 慣例)。
- label 僅在 evaluation/training 構造,**不入 feature 層**;label 窗與訓練集 purge + embargo(#8)。

### 1.2 特徵輸入
- 三族 transform 全集(F2 產出):水位/動能族 + 集中度泛函族 + 相位/共振族;
  context 廣播交互(個股×regime)。全 source-pure(#1)、發布日 gate(#8)。
- 入模前過 **PHASE 9 五鏡 audit**(#11):IC+sign 穩定/共線群/leave-one-out/SHAP/purged-CV 合判。

### 1.3 模型家族(基準階梯——不贏前一階=無存在意義)
| 階 | 模型 | 角色 |
|---|---|---|
| B0 | 隨機排序 | 零假設地板 |
| B1 | 單因子動能(20/60d 還原報酬 rank) | 最廉價可行解 |
| B2 | Ridge 線性(三族特徵) | 線性可達上限 |
| **M1** | **GBDT 樹家族(LightGBM/XGBoost/CatBoost)** | **主軸**:非線性交互 |
| M2 | GBDT ensemble(跨 seed × 跨家族平均) | 穩健化(#15 stochastic ≥3 seed 取統計) |
| M3 | transformer 輔助(deferred,隔離 venv) | 後期增量實驗 |

### 1.4 多週期
每 H 一套獨立模型與驗證(週/月/季/年);跨週期共用 panel/metric SSOT helpers(#12),結果才可比。

## 二、訓練協議(#8 全鏈防洩漏)

- **Purged walk-forward**:expanding(或 rolling)train → embargo(≥ label 窗 + 特徵最大滯後)→ test;
  逐折前進、**test 永不回流調參**;超參數只在 train 內 nested 選擇。
- **宇宙**:逐 rebalance 日採「**當日 core_universe 快照**」(含當期已下市股,#8 survivorship)——
  前置:core_universe 加 as-of 維度(F2 roadmap 已列)。
- **可重現**(#15):固定 random_state 集、pipeline 確定性;產物=artifacts + model_registry(PHASE 10)。

## 三、驗證協議(PHASE 11;evaluation 自包含雙軌)

- **雙軌獨立**:evaluation **不讀 model artifacts**(自己 train→predict;防 artifact 汙染)。
- **單一引用源**(#12):panel 日曆 + metric 公式只住一個 helper,全 validator import。
- **可信度指標**:rank IC(**raw + purged 雙口徑必附**)、Effective-t、勝率、IC 衰變(按 H);
- **經濟價值**(#14):top-N 組合(靈魂產品形態)vs 大盤:MaxDD / Calmar / Sharpe + **逐空頭子期**;
  交易成本敏感度註明;**不以 AUC/準確率宣稱有效**。
- **防自欺電池**:
  - 基準階梯逐階比較(M1 不贏 B2 → 非線性無增量,誠實記錄);
  - **三族消融**(僅第一性 / 僅 Pareto / 僅康波 / 兩兩 / 全合)→ 驗證「三思想各自與合體增量」——
    這直接回答本計畫命題;
  - 隨機 label / 特徵打亂 之 sanity 負對照;
  - stochastic ≥3 seed 統計(min/median/max);單次極值不報。
- **風控分界**(#13):模型只產排序;空頭防護走規則地板(波動目標×趨勢),不混入預測模型。

## 四、落地序列(對映 12-PHASE)

| 步 | 內容 | 前置 |
|---|---|---|
| M-0 | label/panel/metric SSOT helpers(#12)+ core_universe as-of 快照 | F2b 起步即可並行 |
| M-1 | 基準階梯 B0-B2 + 單週期(月 H=20)GBDT MVP | F2b-c 特徵落地 + PHASE 9 五鏡 |
| M-2 | 多週期(5/60/252)+ ensemble + 可信度報告 v1 | M-1 過 walk-forward |
| M-3 | 三族消融研究(本命題的實證答案) | M-2 |
| M-4 | transformer 輔助實驗(隔離 venv) | deferred |

## 五、風險誠實列表(#15)

- alpha 微弱/不穩定風險(IC 可能在某些 H 不顯著)→ 負結果入檔;
- 三族特徵同源共線(同欄位三鏡頭)→ 五鏡共線群裁決(#11);
- regime 依賴(特徵在多頭/空頭表現不對稱)→ 逐子期報告(#14);
- 交易成本/流動性未入 label → 報告層敏感度註明;
- 資料期間偏某 regime(樣本期偏誤)→ 多子期 + 滾動窗檢驗。

## 六、與既有文件鏈

特徵內容=三部曲(`first_principles`/`pareto_thought`/`cycle_thought` 20260612)· 落地順序=
`f2_feature_expansion_roadmap` · 治權=原則精華 v1.6.0(#8/#11/#12/#13/#14/#15/#19)· 架構=憲章第三部
(model/evaluation 雙軌)+ 12-PHASE(9→10→11)。
