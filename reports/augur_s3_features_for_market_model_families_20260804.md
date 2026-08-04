# S3｜市場模型族所需特徵類別矩陣 · 2026-08-04

> **位階**：[I] 計畫／接續記憶（非 META [N]）  
> **觸發**：Steward「實務約 10–12 大類／30–40 常見變體族，列出需要產生的特徵值有哪些，並納入 S3」  
> **taxonomy SSOT**：`reports/augur_market_stock_predict_model_taxonomy_20260804.md`  
> **管線 SSOT**：`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §0.5／§2 S3／§0.6  
> **S4 對齊**：`reports/augur_s4_market_model_families_opt_plan_20260804.md`（Wave A–G）——特徵缺口＝該族誠實 SKIP；不另開第二套特徵尺  
> **閉環 C1（S3→S2→S1→S3）**：`reports/augur_s1_s2_s3_closed_loop_plan_20260804.md` · `audits/SIM-S1-S2-S3-CLOSED-LOOP-20260804.md`（GO＝`LOOP-S3-TO-S2-go`／`LOOP-S2-TO-S1-EXPAND-go`／`LOOP-CYCLE-N-go`）  
> **C1·Arc A**：`reports/augur_s2_kh_optimize_after_s3_plan_20260804.md` · `audits/S2-KH-AFTER-S3-LOOP-20260804.md`  
> **閉環 C2／C0**：S5 可選下鑽特徵缺口→本檔／C1——`reports/augur_s4_s5_closed_loop_plan_20260804.md` · `audits/SIM-S4-S5-CLOSED-LOOP-20260804.md`  

> **約束**：零 FinMind 放量；本檔**不**開全模型訓練；存在／缺口皆須可溯 code／handoff／audit；LOB／NLP／LLM＝gated／缺 infra 誠實標示  
> **登錄**：`audits/S3-FEATURES-MARKET-FAMILIES-20260804.md`  
> **status**：**Steward-approved 2026-08-04**（`S3-FEATURES-PLAN-go`）→ `audits/S3-FEATURES-PLAN-GO-20260804.md`（**≠** `S3-WAVE-*-go` build）

---

## 0. 一句定錨

S3「最佳化特徵完整」＝依市場 **≈12 大類** 模型族，產出／對齊其所需**特徵類別**（feature classes），經提拔閘＋#11 重覆驗証後誠實進 panel／prodset——**不是**發明假 FinMind 欄名，也**不是**宣稱已覆蓋全部另類／LOB 基建。

---

## 1. 現況錨（有證據；非 live DB 普查）

| 錨 | 狀態 | 出處 |
|---|---|---|
| `feature_values` 價量＋籌碼＋估值＋八二／康波＋毛利循環＋roe／debt | **have**（記憶錨約 **35** 名；builder＝`panel`／`chip`／`valuation`／`concentration`／`phase`／`margin_cycle`／`fundamentals`） | `handoff_memory/augur-feature-values.md`；`src/augur/features/panel.py` |
| prodset **active** | **3**：`cycle_position_252d`／`inst_cumflow_position_120d`／`lending_fee_rate_mean_30d` | `reports/augur_project_optimization_plan_20260804.md` |
| 截面相對化候選（`pb_xsec_rank`／`pb_industry_demean` 等） | **partial**（候選／漏斗曾跑；多數淘汰、未進 prodset） | `src/augur/audit/feature_candidate.py`；handoff 殘留盲點 |
| FRED macro 清單＋PIT 讀門 | **partial**：`macro.SERIES`＋`macro_vintage` **有**；`feature_values` **零** macro 股級特徵（模組自陳）；市場方向表有消費 VIX／利差 | `src/augur/features/macro.py`／`macro_vintage.py`；`scripts/build_market_direction_features.py` |
| 日／市場方向特徵表 | **have**（旁路表，非 canonical `feature_values`）：`daily_direction_feature_values`、`market_direction_feature` | `scripts/build_daily_direction_features.py`／`build_market_direction_features.py` |
| 圖／LOB L2／新聞 NLP→預測特徵 | **missing／N/A／gated** | 知識圖≠股圖；LOB 無 L2 基建；knowledge **禁**當預測特徵（計畫 §1.2） |
| 飽和定論（歷史） | 同宇宙 H20–60 曾判「勿再挖特徵」——**不**廢止本檔「按族對齊類別」；新開＝缺口族／新宇宙／新 horizon／honest SKIP | handoff 2026-06-27 戰役 |

**誠實**：本檔未於寫作當下對 live DB `SELECT DISTINCT feature`；列名以 code／handoff／既有報告為準。執行波次前應用 `psql`／`build_feature_panel` 現查刷新覆蓋。

---

## 2. 矩陣：模型大類 → 所需特徵**類別** → 例 → 狀態

狀態語意：

| 標籤 | 含義 |
|---|---|
| **have** | 已有 builder／表列，可庫內 as-of 消費 |
| **partial** | 有部分落地或旁路表／候選，未成 S3 完整契約或未進 prodset |
| **missing** | 類別對該族重要，但尚無可測生產路徑 |
| **N/A／gated** | 缺市場資料或治權禁入（LOB L2、knowledge 當特徵等）——計畫記帳、**不得**假綠 |

| # | 模型大類（taxonomy） | 所需特徵**類別**（非具體 API 欄） | augur 例（若有） | 狀態 |
|---|---|---|---|---|
| 1 | 古典統計／計量 | 單序列價量路徑；波動／殘差輸入；可選利率／匯率外生 | `return_1d`、`volatility_60d`、價序列（PriceAdj raw）；外生→FRED PIT | **have**（價量）／**partial**（macro 外生進股級 panel） |
| 2 | 古典監督式 ML | 異質表格：價量＋估值＋籌碼＋基本面；可選截面秩 | 35 名表格式特徵；`roe`／`debt_ratio`；xsec 候選 | **have**／截面 **partial** |
| 3 | 樹集成／GBDT | 同 #2（容忍缺列／異質型）；交互／稀疏籌碼友善 | 同上；chip 族；interaction 候選腳本 | **have** |
| 4 | 截面排序／LTR | 截面可比特徵＋**相對化**（rank／industry demean）；流動性／規模控制 | prodset 3；`market_cap_log`；`pb_xsec_rank` 候選 | **partial**（相對化弱；多數仍 raw） |
| 5 | 時序深度學習 | 固定窗**張量**（多通道價量±籌碼）；非僅扁平表 | 可由 PriceAdj／chip 重建序列；**無**正式 sequence panel builder | **partial**（原料有、契約缺） |
| 6 | Attention／Transformer 時序 | 同 #5＋較長窗／多變量對齊；可選 macro 通道 | 同 #5；macro 通道 **partial** | **partial** |
| 7 | 圖／關係網路 | 節點特徵（同表格）＋**邊**（產業／相關／供應鏈） | 產業欄在 Info；**無**股圖特徵／adjacency 產物進預測 | **missing**（邊）／節點 **have** |
| 8 | 強化學習交易 | 狀態＝市場＋部位＋約束特徵；獎勵對齊 #14 尺 | 預測特徵可複用；**無**專用 RL state／portfolio-state 特徵集 | **partial**（觀測）／**missing**（RL 狀態契約） |
| 9 | 混合／堆疊集成 | 各臂輸出＋底層特徵並存（meta-features） | direction stack／P_mkt 計畫路徑；ranker＋econ 臂 | **partial** |
| 10 | 另類資料／情緒 NLP | 文本情緒／事件強度（時點對齊、license 終態） | knowledge 管線存在；**禁** embedding 當預測特徵 | **gated**（治權）／另類 raw **missing** |
| 11 | Foundation／LLM 輔助 | LLM 衍生分數／檢索假說→**須**經提拔閘之數值特徵；非唯一價預測器 | advisor／local-llm＝流程輔助；無生產 LLM 特徵欄 | **gated／missing** |
| 12 | 貝氏／機率與演化 | 同表格＋不確定性／殘差特徵；符號回歸輸入＝可解釋因子 | 表格 **have**；顯式 uncertainty／GP kernel 特徵 **missing** | **partial** |

**LOB L2（跨多族常被論文引用）**：台股深度簿 **N/A**（無 L2 落地基建）→ 凡依賴 order-book imbalance 之類別一律 **N/A／gated**，不得用幻造欄補齊。

---

## 3. S3 應產生／對齊之特徵**組**總表（master list）

下列＝S3 漏斗應涵蓋之 **feature groups**（組級；組內具體名由既有 builder／候選擴充，禁臆造 FinMind column）：

1. **Price／return／momentum** — 還原價報酬與多窗動能（例：`return_1d`、`momentum_*d`）→ **have**
2. **Volatility／range／cycle position** — 波動、振幅、高低位置（例：`volatility_60d`、`range_*`、`cycle_position_252d`、`price_to_252d_high`）→ **have**
3. **Liquidity／volume／concentration** — 成交額、週轉、量能噴出、八二量能集中（例：`dollar_volume_log_20d`、`volume_gini_*`）→ **have**
4. **Technical／path shape（扁平）** — 與 #2–3 重疊之技術形狀；序列族另見組 12 → **have**（扁）／序列契約 **partial**
5. **Valuation** — PE／PB／殖利率／市值／長年分位（例：`pe_ratio`、`pb_ratio`、`dividend_yield`、`market_cap_log`、`price_to_10yr`）→ **have**（離群 winsorize 仍為已知債）
6. **Fundamentals／quality／margin cycle** — 財報閘後品質與循環（例：`roe`、`debt_ratio`、`gross_margin_pctile`、`monthly_revenue_yoy`）→ **have**
7. **Flow／chip／short／lending** — 法人／外資／融資券／借券費（例：`institutional_net_buy_ratio_20d`、`lending_fee_rate_mean_30d`⚠名實窗、`foreign_holding_pct`）→ **have**（名實／覆蓋債已知）
8. **Cross-section ranks／industry relative** — 同日百分位、產業 demean、規模中性化 → **partial**（候選有、prod 弱）
9. **Macro／FRED PIT** — 利差／VIX／匯率／通膨預期／Tier-B vintage（經 `macro_vintage`）→ 市場方向表 **partial**；股級 `feature_values` **missing**
10. **Market-level／regime／direction panel** — 大盤／選擇權／景氣燈號等（`market_direction_feature`、日方向 `d_*`）→ **have**（旁路表；與 ranker panel **契約分離**）
11. **Interaction／composite candidates** — 跨鏡交互、引擎假說候選 → **partial**（腳本有；晉升嚴格）
12. **Sequence／tensor windows** — 供 LSTM／Transformer 之對齊多通道窗 → **partial／missing**（原料有、正式 builder／表契約缺）
13. **Graph inputs** — 產業／相關／供應邊＋節點對齊 → **missing**（邊產物）
14. **Alt-data／NLP／LLM-derived（gated）** — 僅在 Steward 明示＋license＋提拔閘後；預設 **gated**
15. **LOB／microstructure L2（N/A）** — **N/A** 直至有真來源基建
16. **RL state／portfolio context** — 部位、約束、成本狀態（≠純 alpha 特徵）→ **missing**（專用契約）

**S3 優先波次（建議；授權後才 build）**

| 波 | 組 | 理由 |
|---|---|---|
| **S3-A** | 1–7 誠實覆蓋＋提拔／#11 重覆驗＋prodset 契約 | 已服務 #2–4 與現役 S4 基線；先閉「完整≠填洞」 |
| **S3-B** | 8–9 截面相對化＋股級 macro PIT | 解鎖 LTR／計量外生／多臂可比 |
| **S3-C** | 10–11 方向表與 ranker panel 契約對齊／meta | 服務 direction／stacking（S4 Wave A／E） |
| **S3-D** | 12–13 序列窗＋圖邊（plan-first） | 服務 DL／GNN；缺則 **SKIP** 不假綠 |
| **S3-E** | 14–16 | 僅 Steward 明示；否則維持 gated／N/A |

---

## 4. 與 S4 對齊（S3↔S4）

S4 SSOT＝`reports/augur_s4_market_model_families_opt_plan_20260804.md` §2 Wave A–G。

| S4 Wave | taxonomy | 依賴本檔特徵組 | S3 就緒判準 |
|---|---|---|---|
| **A** tabular／ranker／direction | #2–4＋direction | 1–8、10–11 | S3-A＋建議 S3-B（截面）；方向旁路＝S3-C |
| **B** classical TS | #1 | 1–2、9 | 價量 have；macro 外生→S3-B |
| **C** sequence DL | #5 | 12（＋1–3、9） | S3-D 契約或誠實 SKIP |
| **D** Transformer TS | #6 | 同 C | 同 C |
| **E** graph | #7 | 13＋節點 1–7 | S3-D 邊產物或 SKIP |
| **F** RL | #8 | 16＋1–10 | S3-E 或 SKIP（另尺） |
| **G** hybrid／NLP／LLM／Bayesian | #9–12 | 11、14（＋1–8） | S3-A 底＋14 gated；未授權＝SKIP |

**一句**：S4 不得因「模型 adapter 已寫」略過 S3 類別缺口；缺特徵＝該族 **SKIP／記帳**（對齊 S4 §3 SKIP 表），不是用 median-fill 假完整。

### 4.1 閉環 C1（S3→S2→S1→S3｜必讀）

本檔 16 feature groups **不是**單向交給 S4 即止。波次收口或特徵庫存可引用後，須依 parent §0.6／C1 全弧：

1. **Arc A**：`feature group → raw 表族 → 缺的 KH 交互概念 → S2 優化`（`augur_s2_kh_optimize_after_s3_plan_20260804.md`）  
2. **Arc B**：KH／特徵缺口 → **raw gap list** → THAW-bounded **擴大 S1**（Dividend／寬窗另句）  
3. **Arc C**：擴大後重驗 S2／S3 驗收  

全弧＝`reports/augur_s1_s2_s3_closed_loop_plan_20260804.md`。KH＝概念／關係（非整庫 raw）；predict ⊥ live API；指導假說、**不加權** runtime。

---

## 5. 驗收（對齊 §0.5 S3）

| # | 判準 | 機械 |
|---|---|---|
| 1 | **多種**特徵組入漏斗（非單特徵一次過） | 本檔 master list＋candidates |
| 2 | 提拔閘 | `verify_candidate_promotion`：as-of＋`effective_t_hac`＋多因子增量 |
| 3 | **重覆驗証** | CLAUDE #11 ≥3／多 seed；陳報 min／median／max／mean |
| 4 | panel 誠實覆蓋 | 有列真算、缺列不 zero-/median-fill 偽 100% |
| 5 | 完整≠可交易 | 仍須後續 #14；禁假確立級 |
| 6 | 族覆蓋可追溯 | 上表 12 大類皆有狀態標籤；N/A／gated 書面 |

**非驗收**：全 FinMind 欄齊、LOB 幻造、knowledge embedding 進因子、未授權放量 build。

---

## 6. 開工授權

### 6.1 計畫採納（已消費）

```text
S3-FEATURES-PLAN-go + GATE-keep + NHC-keep + API-THAW-bounded + no-SIM-apply
```

✅ **GO-EXECUTED** ≈13:35+08 → `audits/S3-FEATURES-PLAN-GO-20260804.md`。  
本報告＝S3 特徵類別 **approved SSOT**；本句**不**含 FinMind 放量、不含全模型訓練、不含 sim `--apply`、**不含**放量 build。

### 6.2 波次 build（仍開／另句）

```text
S3-WAVE-A-go | FZ/GATE-keep | skip-sync | no-SIM-apply
S3-WAVE-B-go | …
```

收口後進閉環 C1（**不**默授 ingest／sync／build）：

```text
LOOP-S3-TO-S2-go + GATE-keep + NHC-keep + API-THAW-bounded
```

```text
LOOP-S2-TO-S1-EXPAND-go + GATE-keep + NHC-keep + API-THAW-bounded
```

```text
LOOP-CYCLE-1-go + GATE-keep + NHC-keep + API-THAW-bounded + no-SIM-apply
```

---

## 7. 變更紀錄

| 日 | 內容 |
|---|---|
| 2026-08-04 | 初版：12 大類×特徵類別矩陣＋16 組 master list＋S3↔S4 對齊；零碼零 API |
| 2026-08-04 | 交叉：S4 檔已落地；§4.1 S3→S2 回饋＋`S2-KH-OPT-AFTER-S3-go` 指針 |
| 2026-08-04 | §4.1 升格閉環 C1 Arc A／B／C；鏈 `augur_s1_s2_s3_closed_loop_plan_20260804.md` |
| 2026-08-04 | `S3-FEATURES-PLAN-go` **GO-EXECUTED**（approved SSOT）；≠ Wave build |

*完。self-reported（#32a）。PLAN 已拍；build 另授。*
