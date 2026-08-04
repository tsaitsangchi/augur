---
title: S4 市場模型族最佳化驗証計畫
status: Steward-approved 2026-08-04
date: 2026-08-04
approved: 2026-08-04T13:21+08:00
layer: "[I]"
role: S4 taxonomy 全族波次驗証 SSOT（詳細矩陣；已拍）
ssot_code: S4-FAMILIES-PLAN-go
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
taxonomy: reports/augur_market_stock_predict_model_taxonomy_20260804.md
baseline_tried: audits/S4-MODELS-TRIED-LIST-20260804.md
audit: audits/S4-MARKET-FAMILIES-PLAN-20260804.md
go_audit: audits/S4-FAMILIES-PLAN-GO-20260804.md
s4_s5_loop: reports/augur_s4_s5_closed_loop_plan_20260804.md
s4_s5_loop_audit: audits/SIM-S4-S5-CLOSED-LOOP-20260804.md
self_reported: true
---

# S4 市場模型族最佳化驗証計畫 · 2026-08-04

> **位階**：[I] 計畫書（CLAUDE #16／#20）。**不創設治權判準**；不改 [N]；不代簽。  
> **狀態**：**Steward-approved 2026-08-04**（`S4-FAMILIES-PLAN-go`；留痕 `audits/S4-FAMILIES-PLAN-GO-20260804.md`）。  
> **本輪**：計畫已拍——**仍零全族開訓**、**零 sim `--apply`**、**不疊 A1**；Wave 開訓另需 `S4-WAVE-*-go`。  
> **parent**：`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §0.5／§2 S4／§7.2b（approved+s4-fam-go）。  
> **閉環 C2**：Wave／artifact 收口後進 S5 漲跌比 OOS，再回饋重選——`reports/augur_s4_s5_closed_loop_plan_20260804.md`（GO＝`LOOP-S4-TO-S5-go`／`LOOP-S5-TO-S4-OPT-go`）。  
> **閉環 C1（上游）**：特徵／KH／raw 缺口回饋——`reports/augur_s1_s2_s3_closed_loop_plan_20260804.md`；S3 特徵＝`reports/augur_s3_features_for_market_model_families_20260804.md`（缺特徵＝本檔 SKIP，不假綠）。

---

## 0. Steward mandate（逐字）

```
實務約 10–12 大類／30–40 常見變體族，均加入S4計畫並進行最佳化驗証
```

**解讀（執行邊界）**

| 是 | 不是 |
|---|---|
| 把 taxonomy 各大類／常見變體族**寫進 S4 計畫**並排程**最佳化重覆驗証** | 本 session 一次訓完 ≈40 族 |
| 缺資料／infra → **誠實 SKIP**（記帳） | SKIP 當 pass／假確立級 |
| 庫內 as-of；predict ⊥ API；#11／#14／anti-leakage | 為補洞解凍放量／Dividend rebuild |
| 逐波 Steward GO（A→G） | 默授全波＋APPLY＋sim apply |

**基線（不得誤當完成）**：`audits/S4-MODELS-TRIED-LIST-20260804.md`＝**2 族**（RankRidge／B2_ridge · M1_gbdt）。

**時程誠實**：Wave A＝日～週；全普查（含 missing adapter 實作＋重覆驗）＝**多週**。本檔只定地圖與驗收尺。

---

## 1. 硬邊界（繼承 parent §1）

- **predict ⊥ API**：train／eval 走 DB as-of；`--skip-sync`；禁 live FinMind／FRED 硬閘。  
- **#8 anti-leakage**：切分／label／圖邊／文本時點皆 PIT。  
- **#11**：stochastic ≥3 seed（min／median／max／mean）；單次極值須註明。  
- **#14**：經濟終關可跑且數字 (a)(b)(c)；**IC≠可交易**。  
- **禁假確立級**：唯 `direction_gate.status='evaluated_pass'`；現況 pass＝0 則誠實呈報。  
- **GATE-keep／NHC／API-THAW-bounded**：禁偷 APPLY、禁降閘；THAW≠放量。  
- **RL／LLM／另類**：另尺或 license 門；不得與截面 #14 混稱「可交易完成」。

---

## 2. 波次總覽

| Wave | 名稱 | taxonomy 大類 | 優先 | 預估跨度 |
|---|---|---|---|---|
| **A** | tabular／ranker／direction | #2（表格式）· #3 · #4 · direction | **Wave-1** | 數日～2 週 |
| **B** | classical TS／計量 | #1 | 2 | 1–2 週（含 adapter） |
| **C** | sequence DL | #5 | 3 | 2–4 週 |
| **D** | Attention／Transformer TS | #6 | 3 | 2–4 週 |
| **E** | 圖／關係 | #7 | 4 | 2–3 週（圖資料債） |
| **F** | RL 交易 | #8 | 5（另尺） | 多週；可能長期 defer |
| **G** | 混合／另類 NLP／LLM／貝氏 | #9–#12 | 4–5 | 多週；高 SKIP 率預期 |

每波結束寫 `audits/S4-WAVE-<X>-YYYYMMDD.md`：跑過／SKIP／數字來源／是否觸 #14。

---

## 3. 通用驗收模板（每變體族）

通過（**Verified**）須同時：

1. **Adapter**：存在可個別執行之 train／eval 入口（或明示走 `run_economic_eval`／baseline 臂）。  
2. **重覆驗証**：適用則多 seed（#11 ≥3）＋適用 horizon 臂；陳報分布。  
3. **#14**：截面排序／組合尺可跑者必須；純波動／單序列任務須**另書量尺**並標「非可交易宣稱」。  
4. **anti-leakage**：as-of／purge／embargo 可述。  
5. **來源**：數字僅 (a) stdout／(b) DB／(c) API——本波預測側通常僅 (a)(b)。

**SKIP**（誠實；**≠ pass**）觸發例：

| 條件 | 例 |
|---|---|
| 無 adapter | XGBoost／CatBoost／LSTM 無 `models.*`＋CLI |
| 無資料 | LOB Level-2、未落地新聞全文、產業圖邊表 |
| 無 infra | GPU／序記憶體不足且無 CPU 可行替代 |
| 治權禁 | 自動下單 RL；未授權全文 NLP |
| 任務錯位 | 把 sim 風險 GARCH 冒充預測熱路徑綠燈 |

---

## 4. 完整矩陣（family → adapter → wave → cmds → GO）

> **adapter 狀態**：`exists`＝預測／econ／direction 熱路徑可跑；`partial`＝套件或旁路有、無預測薄殼；`missing`＝需 plan-first 新建；`n/a-sim`＝僅 sim／風險、**不得**計入 S4 預測通過。  
> 變體族列舉對齊 taxonomy §2（約 **35** 列；可併可拆，計數非 census）。

### Wave A — tabular／ranker／direction

> **Wave A 執行（2026-08-04）**：Steward `S4-WAVE-A-go | FZ/GATE-keep | no-SIM-apply | skip-sync` → 帳＝`audits/S4-WAVE-A-EXECUTED-20260804.md`（as-of `2026-06-30`）。

| ID | 大類 | 變體族 | adapter | 建議 verify cmds（庫內；示意） | Steward | Wave A |
|---|---|---|---|---|---|---|
| A-3a | #3 | LightGBM（M1／RankGBDT） | **exists**（econ `M1_gbdt`；`train_ranker --family RankGBDT`） | `train_ranker.py --run --family RankGBDT --horizon {20,60} --seed {1,2,42} --asof <asof>`；`run_economic_eval.py --h {H} --seed {s} --feature-source=prodset` | `S4-WAVE-A-go` | [x] PASS |
| A-3b | #3 | XGBoost | **missing**（套件或有；無 ranker 族） | SKIP until adapter；驗收後同 A-3a 多 seed／#14 | 同 A；實作另句 | [x] SKIP |
| A-3c | #3 | CatBoost | **missing** | SKIP until adapter | 同 A | [x] SKIP |
| A-3d | #3 | Random Forest | **missing** | SKIP until adapter（或 sklearn 薄殼） | 同 A | [x] SKIP |
| A-4a | #4 | Ridge／線性 ranker（RankRidge≡B2） | **exists** | `train_ranker.py --run --family RankRidge --horizon {20,40,60,120} --seed 42 --asof <asof>`；`run_economic_eval.py --h {H}` | `S4-WAVE-A-go` | [x] PASS |
| A-4b | #4 | pairwise／listwise LTR | **missing** | SKIP | 同 A | [x] SKIP |
| A-4c | #4 | 截面因子＋shrinkage | **partial**（B1 momentum／特徵側；非獨立 model family） | 以 baseline B1＋文件對照；不冒充新族 pass | 同 A | [x] PARTIAL |
| A-2a | #2 | 線性／邏輯回歸 | **partial**（DailyLogit direction；截面 Ridge＝A-4a） | `train_daily_direction.py --run-v2 --ks 5 --seeds 3` | `S4-WAVE-A-go` | [x] PASS（併 D1／4a） |
| A-2b | #2 | SVM | **missing** | SKIP | 同 A | [x] SKIP |
| A-2c | #2 | KNN | **missing** | SKIP | 同 A | [x] SKIP |
| A-2d | #2 | 樸素貝氏 | **missing** | SKIP | 同 A | [x] SKIP |
| A-2e | #2 | 淺層 MLP | **missing** | SKIP | 同 A | [x] SKIP |
| A-D1 | direction | DailyGBDT_cal（D 軌） | **exists** | `train_daily_direction.py --run-v2`（≥3 seeds） | `S4-WAVE-A-go` | [x] PASS |
| A-D2 | direction | market／stack／threelens | **exists**（scripts 在） | `train_market_direction.py`／`train_direction_stack.py`／`train_direction_threelens.py`（無參印矩陣；`--run` 依各檔） | `S4-WAVE-A-go` | [x] PASS |
| A-B0 | 地板 | B0_random | **exists**（baseline） | 經 `run_economic_eval`／baseline 階梯（對照臂） | 隨 A | [~] PARTIAL（基準臂） |
| A-B1 | 地板 | B1_momentum | **exists** | 同上 | 隨 A | [~] PARTIAL（基準臂） |

**Wave A 最低完成定義（建議）**

1. [x] RankRidge × 多 horizon（至少殘餘 H40／H120 若仍缺）artifact 可溯。  
2. [x] RankGBDT **train** ≥3 seed × 主 horizon＋#14 統計（非僅 econ 臂）。  
3. [x] direction 至少一臂 v2 多 seed 數字可陳。  
4. [x] XGB／Cat／RF／LTR／SVM…：**SKIP 列帳**或另授 adapter 實作後再驗——**不得**為湊數假訓。

### Wave B — classical TS／計量（#1）

> **Wave B 執行（2026-08-04）**：Steward `S4-WAVE-B-go | FZ/GATE-keep | no-SIM-apply | skip-sync` → 帳＝`audits/S4-WAVE-B-EXECUTED-20260804.md`（**誠實 SKIP 普查**；無預測 adapter 假訓）。

| ID | 變體族 | adapter | verify／SKIP | Steward |
|---|---|---|---|---|
| B-1a | ARIMA／SARIMA | **missing**（預測熱路徑） | **SKIP**（本窗已列帳）→statsmodels 薄殼＋單股／截面彙總尺**另書** | `S4-WAVE-B-go` ✅ |
| B-1b | GARCH 族 | **n/a-sim**（`simulate_*` 風險）／預測 **missing** | **SKIP（預測）**；**禁止**用 sim GARCH 綠冒充 S4 預測通過 | 同 B ✅ |
| B-1c | VAR／VECM | **missing** | **SKIP**（需多序列面板契約） | 同 B ✅ |
| B-1d | 狀態空間／Kalman | **missing** | **SKIP** | 同 B ✅ |
| B-1e | 協整 | **missing** | **SKIP** | 同 B ✅ |

### Wave C — sequence DL（#5）

> **Wave C 執行（2026-08-04）**：Steward `S4-WAVE-C-go | FZ/GATE-keep | no-SIM-apply | skip-sync` → 帳＝`audits/S4-WAVE-C-EXECUTED-20260804.md`（**誠實 SKIP**；torch 在≠adapter）。

| ID | 變體族 | adapter | verify／SKIP | Steward |
|---|---|---|---|---|
| C-5a | RNN | **missing** | **SKIP**（需 sequence panel builder） | `S4-WAVE-C-go` ✅ |
| C-5b | LSTM／BiLSTM | **missing** | **SKIP** | 同 C ✅ |
| C-5c | GRU | **missing** | **SKIP** | 同 C ✅ |
| C-5d | CNN-LSTM | **missing** | **SKIP** | 同 C ✅ |
| C-5e | TCN | **missing** | **SKIP** | 同 C ✅ |

驗收加碼：序列窗 as-of、embargo、≥3 seed；GPU 不可用→CPU smoke 或 SKIP——**本窗因缺契約一律 SKIP、未冒煙**。

### Wave D — Attention／Transformer TS（#6）

> **Wave D 執行（2026-08-04）**：Steward `S4-WAVE-D-go | FZ/GATE-keep | no-SIM-apply | skip-sync` → 帳＝`audits/S4-WAVE-D-EXECUTED-20260804.md`（**誠實 SKIP**；`transformers` 套件在≠adapter）。

| ID | 變體族 | adapter | verify／SKIP | Steward |
|---|---|---|---|---|
| D-6a | Transformer（時序） | **missing**（transformers 套件≠預測 adapter） | **SKIP** | `S4-WAVE-D-go` ✅ |
| D-6b | Informer／Autoformer 類 | **missing** | **SKIP** | 同 D ✅ |
| D-6c | PatchTST 類 | **missing** | **SKIP** | 同 D ✅ |

### Wave E — 圖／關係（#7）

> **Wave E 執行（2026-08-04）**：Steward `S4-WAVE-E-go | FZ/GATE-keep | no-SIM-apply | skip-sync` → 帳＝`audits/S4-WAVE-E-EXECUTED-20260804.md`（**誠實 SKIP**；`knowledge_edge`＝KH 知識圖，**≠**股票／產業圖邊）。

| ID | 變體族 | adapter | verify／SKIP | Steward |
|---|---|---|---|---|
| E-7a | GCN／GAT | **missing** | **SKIP**（無圖神經網路套件；無圖邊 as-of 表） | `S4-WAVE-E-go` ✅ |
| E-7b | 股權／產業／相關性圖＋時序混合 | **missing** | 無產業圖／相關性邊→**SKIP** | 同 E ✅ |

### Wave F — RL（#8）

> **Wave F 執行（2026-08-04）**：Steward `S4-WAVE-F-go | FZ/GATE-keep | no-SIM-apply | skip-sync | RL-separate-ruler` → 帳＝`audits/S4-WAVE-F-EXECUTED-20260804.md`（**誠實 SKIP／defer**；碼庫確認無 RL 套件／自動下單路徑）。

| ID | 變體族 | adapter | verify／SKIP | Steward |
|---|---|---|---|---|
| F-8a | DQN／PPO／A2C | **missing** | **SKIP／defer**；**禁自動下單** | `S4-WAVE-F-go`（另尺） ✅ |
| F-8b | portfolio RL | **missing** | 同上；不得與 #14 混稱 | 同 F ✅ |
| F-8c | MARL | **missing** | 同上 | 同 F ✅ |

### Wave G — 混合／另類／LLM／貝氏（#9–#12）

> **Wave G 執行（2026-08-04；S4 A–G 收官波）**：Steward `S4-WAVE-G-go | FZ/GATE-keep | no-SIM-apply | skip-sync` → 帳＝`audits/S4-WAVE-G-EXECUTED-20260804.md`（**2 partial 既有文件化＋8 誠實 SKIP**；advisor／LLM 明註非價預測器）。

| ID | 變體族 | adapter | verify／SKIP | Steward |
|---|---|---|---|---|
| G-9a | ML+DL stacking | **partial**（`DirStackM` 已落地；Logit 無隨機性→seed=0） | **既有**，不重訓 | `S4-WAVE-G-go` ✅ |
| G-9b | GBDT+LSTM | **missing** | **SKIP** | 同 G ✅ |
| G-9c | blending／ensemble（多模型融合） | **missing**（`threelens`＝特徵層融合，非真 ensemble） | **SKIP** | 同 G ✅ |
| G-10a | 新聞／社群情緒 | **partial**（knowledge 管線≠預測頭） | 無授權全文／無預測頭→**SKIP** | 同 G ✅ |
| G-10b | 事件抽取→預測頭 | **missing** | **SKIP** | 同 G ✅ |
| G-10c | 主題模型＋下游頭 | **missing** | **SKIP** | 同 G ✅ |
| G-11a | LLM 特徵／情緒 | **partial**（advisor／Ollama；**非**價預測器；DDL 明禁流入 `feature_values`） | 不得自稱 S4 價預測 Verified；輔助流程另帳 | 同 G ✅ |
| G-11b | RAG 假說／agentic 研究 | **partial**（advisor） | 同上；**不加權** runtime | 同 G ✅ |
| G-12a | 貝氏層級 | **missing** | **SKIP** | 同 G ✅ |
| G-12b | GP | **missing** | **SKIP** | 同 G ✅ |
| G-12c | 遺傳規劃／符號回歸 | **missing**（`src/augur/evolution/`僅`behavior_rubric.py`——非 GP 族） | **SKIP**；未把 TWEVO 假稱為 GP 族 pass | 同 G ✅ |

**LOB Level-2**：taxonomy 未單列但常見——**DB 無 L2 → 凡依賴 L2 之族一律 SKIP**。

---

## 5. schema／程式規劃（#20；本輪不實作）

| 產物 | 既有 | 缺口 |
|---|---|---|
| `model_registry`／artifact | `augur.models.registry`／`artifact`；`train_ranker` | 新 family 字面須登錄契約 |
| 生產薄殼 | `RankRidge`／`RankGBDT` | XGB／Cat／RF／LTR／TS／DL… |
| 經濟尺 | `run_economic_eval`／`baseline` B0–M1 | 非截面任務之量尺表（Wave B/F） |
| direction | `train_daily_direction*` | 與截面 ranker 尺分離文件 |
| 序列／圖 panel | （無統一 builder） | Wave C–E 前置；特徵類別＝`reports/augur_s3_features_for_market_model_families_20260804.md`（S3↔S4） |
| 結果落點 | stdout＋可選 `audits/S4-WAVE-*`；registry 列 | **禁** hand-patch 歷史列 |

---

## 6. Steward GO（paste-ready）

**① 採納本計畫（擴張 S4；不開訓）**

```text
S4-FAMILIES-PLAN-go + GATE-keep + NHC-keep + API-THAW-bounded + no-SIM-apply
```

**② 開工 Wave A（Wave-1）**

```text
S4-WAVE-A-go | FZ/GATE-keep | no-SIM-apply | skip-sync
```

**③ 後續波次（各另句）**

```text
S4-WAVE-B-go | FZ/GATE-keep | no-SIM-apply | skip-sync
S4-WAVE-C-go | FZ/GATE-keep | no-SIM-apply | skip-sync
S4-WAVE-D-go | FZ/GATE-keep | no-SIM-apply | skip-sync
S4-WAVE-E-go | FZ/GATE-keep | no-SIM-apply | skip-sync
S4-WAVE-F-go | FZ/GATE-keep | no-SIM-apply | skip-sync | RL-separate-ruler
S4-WAVE-G-go | FZ/GATE-keep | no-SIM-apply | skip-sync
```

效力邊界：採納句 **≠** 全族訓練；Wave-A-go **≠** APPLY／predict 寫庫／sim apply／放量 API。

---

## 7. 與 parent／基線對照

| 尺 | 值 |
|---|---|
| parent S4 enrichment | approved+s4-fam-go（本檔已拍） |
| taxonomy 大類 | ≈12 |
| 本矩陣變體列 | ≈35（A–G 表） |
| 已試（基線→Wave A） | ≥5 架構臂（見 `audits/S4-MODELS-TRIED-LIST-20260804.md`） |
| 本輪執行 | **Wave A–G 全波次 EXECUTED**（B–G＝誠實 SKIP／defer／既有 partial 文件化；帳 `S4-WAVE-{B,C,D,E,F,G}-EXECUTED-20260804.md`）；**S4 taxonomy 收口** |

---

## 修訂

| 版 | 日 | 說明 |
|---|---|---|
| draft | 2026-08-04 | 初版：mandate＋Wave A–G 矩陣＋GO；零開訓 |
| approved | 2026-08-04 | Steward `S4-FAMILIES-PLAN-go + GATE-keep + NHC-keep + API-THAW-bounded + no-SIM-apply` → 本檔＝SSOT；留痕 `audits/S4-FAMILIES-PLAN-GO-20260804.md`；**≠** Wave-A train |
| crosslink-c2 | 2026-08-04 | 交叉 **C2** S4↔S5 閉環計畫指針（零開訓） |
| crosslink-c1 | 2026-08-04 | 交叉 **C1** S1–S2–S3 閉環＋S3 特徵矩陣指針（零開訓） |
| wave-a-exec | 2026-08-04 | Steward `S4-WAVE-A-go | FZ/GATE-keep | no-SIM-apply | skip-sync` → Wave A 矩陣勾選＋帳 `audits/S4-WAVE-A-EXECUTED-20260804.md` |
| wave-b-exec | 2026-08-04 | Steward `S4-WAVE-B-go | …` → 五族誠實 SKIP／n/a-sim；帳 `audits/S4-WAVE-B-EXECUTED-20260804.md` |
| wave-c-exec | 2026-08-04 | Steward `S4-WAVE-C-go | …` → sequence DL 五族誠實 SKIP；帳 `audits/S4-WAVE-C-EXECUTED-20260804.md` |
| wave-d-exec | 2026-08-04 | Steward `S4-WAVE-D-go | …` → Transformer TS 三族誠實 SKIP；帳 `audits/S4-WAVE-D-EXECUTED-20260804.md` |
| wave-e-exec | 2026-08-04 | Steward `S4-WAVE-E-go | …` → 圖／關係兩族誠實 SKIP（KH 知識圖≠股票圖）；帳 `audits/S4-WAVE-E-EXECUTED-20260804.md` |
| wave-f-exec | 2026-08-04 | Steward `S4-WAVE-F-go | … \| RL-separate-ruler` → RL 三族誠實 SKIP／defer（碼庫確認無 RL 套件／自動下單）；帳 `audits/S4-WAVE-F-EXECUTED-20260804.md` |
| wave-g-exec | 2026-08-04 | Steward `S4-WAVE-G-go | …` → 混合／NLP／LLM／貝氏 2 partial（既有）＋8 SKIP；帳 `audits/S4-WAVE-G-EXECUTED-20260804.md`；**S4 A–G 全波次收口** |

---

*完。self-reported（#32a）。**已拍** `S4-FAMILIES-PLAN-go`；**Wave A–G 全波次 EXECUTED**（taxonomy ≈12 大類／≈35 變體族普查收官；多誠實 SKIP，生產熱路徑仍＝Wave A 三臂）。下一刀（另句）＝`LOOP-S5-TO-S4-OPT-go`（消費 OOS 回饋）或 `S3-WAVE-D-go`（序列窗契約，解 C／D 根因）。*
