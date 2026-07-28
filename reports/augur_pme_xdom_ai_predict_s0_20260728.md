# PME-XDOM-AI-PREDICT S0 範圍裁切／三桶診斷 [I]（2026-07-28）

* **性質**：[I] 診斷帳；**零寫 DB**（本檔僅書面）。  
* **授權**：`PME-XDOM-AI-PREDICT`＋`GATE-keep`＋`FZ-keep`＋`NHC-keep` → `audits/PME-XDOM-AI-PREDICT-APPROVED-20260728.md`  
* **短計畫**：`reports/augur_pme_xdom_ai_predict_plan_20260728.md`  
* **DB 親驗時點**：2026-07-28（`feature_values`／`philosophy_*`／`principle_factor_map`；distinct feature＝38；maps＝67）

---

## 1. 近程範圍（釘死）

| 項 | 決定 |
|---|---|
| **閉環** | AI 模型進化 × 投資／預測模型進化**文獻橋**（investment school 載體＝新建 `ml_predict_evolution`） |
| **進** | 可核 citation 之人撰原則 → `principle_factor_map`（庫內已有 feature） |
| **不進** | ERP dump；太陽能；RKI 探針列當資格；embedding／knowledge 當 feature；AI 造原則 |
| **閘** | 本輪**不跑** S3；標待開 `PME-XDOM-AI-PREDICT-S3` |
| **對照** | RKI 同軸探針＝檢索-only；本軸＝寫假說鏈 |

---

## 2. 候選假說（5 條；假說≠真兆）

| ID | 方法論錨（可核） | 投資／預測假說（人撰） | 建議市場對映 | 可否證條件 |
|---|---|---|---|---|
| H1 | OOS／偏差—變異數／低噪訓練（ESL；AFML purged CV 精神） | 預測模型應偏愛低噪、受控振幅之觀測代理 | `volatility_60d`（−）／`range_mean_20d`（−） | 閘後 IC 方向與假說同號且雙綠才算活；否則誠實 FAIL |
| H2 | 正則化／奧卡姆（ESL；Applied Predictive Modeling） | 較簡之財務品質訊號優於過度參數化 | `debt_ratio`（−）／`roe`（＋） | 同上 |
| H3 | 集成多樣性（Dietterich 2000） | 多資訊源籌碼代理 ≈ 弱學習器多樣 | `institutional_net_buy_ratio_20d`（＋）／`foreign_holding_pct`（＋） | 同上 |
| H4 | 迭代回饋／誤差修正（線上學習精神；AFML 再驗） | 極端位置後之均值回歸代理「錯誤修正」 | `range_position_120d`（−）／`days_since_high_252d`（＋） | 同上 |
| H5 | 第一性拆解為可觀測基本面（因果／特徵工程紀律） | 估值與成長基本量為可拆解假說骨架 | `pe_ratio`（−）／`monthly_revenue_yoy`（＋） | 同上 |
| H6 | ERP／探針字面／embedding | （靈感-only） | — | **近程不可對映**——拒 SEED |

---

## 3. 三桶（對 `feature_values`；親驗）

### A. 可對映（庫內已有序列 → S1 可 SEED）

| feature | FV 列數（約） | panel 窗 | S1 動作 |
|---|---|---|---|
| `volatility_60d` | 78957 | 2007–2026-06-30 | 新掛 ml_predict_evolution |
| `range_mean_20d` | 79637 | 2007–2026-06-30 | 新 |
| `debt_ratio` | 16140 | 2021–2026-06-30 | 新 |
| `roe` | 16182 | 2021–2026-06-30 | 新 |
| `institutional_net_buy_ratio_20d` | 67472 | 2012–2026-06-30 | 新 |
| `foreign_holding_pct` | 68839 | 2007–2026-06-30 | 新 |
| `range_position_120d` | 78042 | 2007–2026-06-30 | 新 |
| `days_since_high_252d` | 76126 | 2007–2026-06-30 | 新 |
| `pe_ratio` | 46889 | 2007–2026-06-30 | 新 |
| `monthly_revenue_yoy` | 65802 | 2007–2026-06-30 | 新 |

### B. 缺特徵（概念相關、庫內無 → S2 候選；本輪不建）

| 概念代理 | 缺 feature | 備註 |
|---|---|---|
| 模型 OOS IC 穩定度 | `model_ic_stability_*` | 無 FV；**不**把 `model_registry` 列當 feature |
| purged／組合 CV 分數 | `purged_cv_score` | 無；閘內評價另屬 S3 |
| 集成分歧度 | `ensemble_disagreement` | 無 |
| 毛利水準（非分位） | `gross_margin`／`operating_margin` | 與 SUNZI S0 同缺口 |

### C. 不可對映（近程拒 SEED）

| 概念 | 理由 |
|---|---|
| ERP／Tiptop dump、4gl | 無市場觀測定義；未授權 |
| RKI probe 命中／顧問 cite 率 | 探針≠量化資格 |
| knowledge／advisor embedding | A.16；永不作 feature |
| AI 生成 statement／citation | #1；NHC／禁 ai_generated |
| 太陽能漿料製程 | 範圍外（`PME-XDOM-SOLAR`） |

---

## 4. 驗收錨（S0）

| ID | 結果 |
|---|---|
| 範圍書面可複現 | ✅ 本檔 |
| 三桶可複現 | ✅ §3 |
| 零寫 DB | ✅ |
| ERP／RKI／embedding／solar 明示排除 | ✅ |

**下一步**：S1＝`scripts/curate_pme_xdom_ai_predict_map.py --apply`；**不**跑閘。
