---
status: draft
series: s4_model_families
depends_on:
  - audits/S3-WAVE-C-EXECUTED-20260804.md
  - reports/augur_s4_wave_a_sklearn_adapters_plan_20260804.md
---

# S4-DIRFAMILY-GENERALIZE — DirStack「僅認 RankRidge」缺口 plan-first（2026-08-04）

> **性質**：[I] plan-first（憲章第六部；CLAUDE #20——本案觸碰確立級 direction／arena 生產鏈,跨 4 個 package,屬高風險門檔）。**不含**任何 `--run`／`model_registry`／`direction_gate` 寫入；**不改**任何 gate 判準（FZ/GATE-keep）。
> **觸發**：`audits/S3-WAVE-C-EXECUTED-20260804.md` §4 查核中發現、誠實記錄「超出本波字面範圍」之缺口，本文件即該項之獨立範圍界定。
> **self-reported（#32a）**：本文為 AI 呈案；一切數字待 Phase 0 實跑後以 stdout 為準。

---

## 0. 一句話

**`probability_oos_sample`／`calibrate_relative_probability`／`train_direction_stack` 三支「相對分量」鏈全程硬編碼 `RankRidge`，Wave-A 現有 7 族新挑戰者無法參與 DirStack；本計畫把「能否讓其他族也餵 DirStack」拆成安全的程式泛化（Phase 0，零新寫入）與需另裁的「是否真的產出、是否真的贏」（Phase 1，條件觸發），並在泛化過程中一併修補查核中發現的一個既有潛在資料汙染風險（`calibrator_id` 未含 family、`train_direction_stack._load_joined` 未過濾 family）。**

---

## 1. 現況鏈路盤點（讀碼＋DB 內省，非猜測）

```text
predict_asof.py --family X --run          （已泛型,零改動,見 S4-Wave-A 計畫§1「零特判 estimator」）
    → prediction_values（model_id 含 family,如 RankRidge_H60_...）
        → calibrate_relative_probability.py --emit
          （硬編 MODEL_FAMILY="RankRidge" 過濾 model_registry.family)
            → prediction_probability（PK: panel_date,model_id,stock_id——已 family-safe,因 model_id 已含族)

build_probability_oos_sample.py --run     （硬編 MODEL_FAMILY="RankRidge",inline 重寫 Ridge fit,非呼叫 ranker.py)
    → probability_oos_sample（PK: horizon,panel_date,model_family,stock_id——已 family-safe)
        → calibrate_relative_probability.py --fit
          （硬編 MODEL_FAMILY 讀 §_load,serve 校準器寫 probability_calibrator)
            → probability_calibrator（PK: calibrator_id 單獨——⚠️ id=f"platt_h{h}_asof{FREEZE}_g{git7}",
                                        未含 family,見§2 風險 R1)
        → train_direction_stack.py --run/--run-v2
          （_load_joined 讀 probability_oos_sample **零 model_family 過濾**,見§2 風險 R2)
            → direction_oos_sample（PK 含 model_id="DirStack"/"DirStackM"——本身固定,非隨輸入族變化)
                → evaluate_direction_gate.py（已有獨立防線:criteria 無 estimand 且偵測多 model_id→拒判,
                                               但此防線防的是「同表多 model_id」,不防「同一 model_id 吃了
                                               混族訓練資料」——見§2,此為兩種不同失效模式)
```

**結論**：三支腳本之「硬編 RankRidge」表面上是同一問題,但 **DB 層安全性各不相同**——`probability_oos_sample`／`prediction_probability` 之 PK 已含足夠鑑別欄（family 或 model_id）、多族共存不衝突；`probability_calibrator` 與 `train_direction_stack._load_joined` 則有**真實潛在資料汙染風險**（§2 R1/R2）,獨立於「是否要泛化 Wave-A 族」皆值得修補。

---

## 2. 風險盤點（本次查核新發現,非計畫前已知）

| # | 風險 | 觸發條件 | 後果 | 修法 |
|---|---|---|---|---|
| **R1** | `probability_calibrator.calibrator_id = f"platt_h{h}_asof{FREEZE}_g{git7}"` **未含 family** | 對同一 horizon 校準第二個 family | `ON CONFLICT (calibrator_id) DO UPDATE`——**靜默覆蓋** RankRidge 既有校準器列（PK 只有 `calibrator_id`,見 DB 內省） | `calibrator_id` 改含 family（如 `platt_{family}_h{h}_...`） |
| **R2** | `train_direction_stack.py._load_joined` 之 SQL **零 `model_family` 過濾**（`SELECT ... FROM probability_oos_sample s ...`,無 `WHERE s.model_family=...`） | `probability_oos_sample` 內同時存在 ≥2 個 family 之列 | DirStack 合成器 fit 於**混族攤平**之訓練集（不同族分數尺度/誤差結構不同,非同一量）——寫入之 `direction_oos_sample` 仍掛既有 `model_id="DirStack"`,**外觀正常但內容已汙染** | `_load_joined` 加 `AND s.model_family=%s`（預設 `"RankRidge"`,保留現狀行為) |
| R3（已有防線,非新增修法） | `evaluate_direction_gate.py` 對「同表多 model_id 且 criteria 無 estimand」已拒判（`_fetch_samples` 既有機制) | 若未來刻意讓 DirStack 產生多個 model_id（如 `DirStack_RankXGB`） | 湖評無 estimand 指名時**機械拒判**,非本計畫需處理——僅記錄「此防線與 R2 是不同失效面,不互相替代」 | 無需修改;Phase 1 若真做多族 DirStack 比較,新 model_id + criteria 明示 estimand 即可沿用此既有防線 |

**R1／R2 的共同點**：**與是否推進 Wave-A 多族評測無關**——即使本計畫止步於 Phase 0（純評測、零新 family 寫入 `probability_oos_sample`）,R1／R2 本身已是**既有程式碼的潛在缺陷**（單一 family 現況下不會觸發,但下一個手動或誤觸的 family 寫入就會觸發）,建議**一併修**,屬防禦性加固（成本低、風險零,因預設值保留現狀）。

---

## 3. (a) 對應 table schema——零新表,現況全數列出

| 表 | 現有 PK／鑑別欄 | 本計畫是否改 schema |
|---|---|---|
| `probability_oos_sample` | `(horizon, panel_date, model_family, stock_id)` | 否——已 family-safe |
| `probability_calibrator` | `(calibrator_id)` 單欄 | 否（**改 `calibrator_id` 之值產生方式**,非改 schema／欄位) |
| `prediction_probability` | `(panel_date, model_id, stock_id)` | 否——已 model_id-safe |
| `direction_oos_sample` | `(model_id, target_id, panel_date, horizon, seed)` | 否（Phase 1 若要多族比較,用**新 model_id 值**,非改表） |
| `model_registry` | 既有 | 否 |

---

## 4. (b) 對應 python 程式規畫

### Phase 0（本計畫唯一要求授權執行的範圍）——程式泛化＋防禦性加固,零新資料寫入

| 檔 | 動作 | 內容 |
|---|---|---|
| `scripts/build_probability_oos_sample.py` | 修改 | `MODEL_FAMILY` 常數 → `--model-family` CLI 參數（`default="RankRidge"`,`choices=` 動態取 `ranker.ALL_FAMILIES` 之 family 名）；`emit_horizon` 內**移除 inline 重寫 Ridge fit**,改複用 `augur.models.ranker`（`est_cls = {c.family: c for c in ranker.ALL_FAMILIES}[model_family]`,同 `portfolio.py` 既有 dispatch 模式,#12）——**注意**：現況 inline fit 用 `StandardScaler+Ridge(alpha=1.0)`,與 `ranker.RankRidge` 建構參數須逐一核對一致（#12 零漂移),此為本檔既有 inline 邏輯遷移,非新邏輯 |
| `scripts/calibrate_relative_probability.py` | 修改 | `MODEL_FAMILY` 常數 → `--model-family` CLI 參數（同上 default）；`_load()` 之 SQL 參數改用該值（現已參數化,僅需換常數來源）；`emit_horizon` 之 `model_registry.family` 過濾同步改用該值；**R1 修法**：`cid = f"platt_h{h}_asof{FREEZE}_g{git7}"` → `cid = f"platt_{model_family}_h{h}_asof{FREEZE}_g{git7}"` |
| `scripts/train_direction_stack.py` | 修改（**R2 修法,獨立於是否用新 family**） | `_load_joined(cur, h)` → `_load_joined(cur, h, model_family="RankRidge")`,SQL 加 `AND s.model_family=%s`（`params` 增一項）；`run()`／`run_v2()` 呼叫處傳入同一參數（預設值保留現況行為,不影響既有 `DirStack`／`DirStackM` 產出——**驗收見§6 行為不變性**） |
| `src/augur/models/ranker.py`／`train_ranker.py`／`portfolio.py` | **零改動** | 本計畫消費既有介面（S4-Wave-A 已完成之 `ALL_FAMILIES`／dispatch),不再新增族或改既有契約 |

### Phase 1（條件觸發,本計畫不含,需另句授權）

僅在 Wave-A Phase 0 評測（`audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md`,現正背景執行中）顯示**某族 3-seed net Sharpe min 真贏 RankRidge**（比照 #32b 預凍對照臂紀律）時才有意義討論；即便如此,「該族單獨贏」與「該族餵 DirStack 後,DirStack 整體是否比現況更好」是**兩個不同問題**——Phase 1 範圍：

1. `build_probability_oos_sample.py --model-family RankXXX --run --all`（materialize 該族 OOS 樣本,新增列,不動既有 RankRidge 列)
2. `calibrate_relative_probability.py --model-family RankXXX --fit --all`（新 `calibrator_id`,不覆蓋既有)
3. `train_direction_stack.py` 需再擴充一個 `--model-family` 參數＋**新 `model_id`**（如 `DirStack_RankXXX`,避免覆蓋現有 `DirStack` 列,呼應§2 R3 表述)
4. 比較新 `model_id` 之 OOS 表現 vs 既有 `DirStack`——**僅供研究比較,不得直接視為 arena／direction_gate 候選**（升格需另一輪 Steward 明示,不因「贏了」自動晉升,承 FZ/GATE-keep 硬邊界)

---

## 5. 分階段與驗收門檻

| 階段 | 內容 | Gate | 需另授權？ |
|---|---|---|---|
| **Phase 0** | §4 表列 3 支腳本之 `--model-family` 參數化＋R1/R2 防禦性加固 | **行為不變性**：`--model-family` 未傳（或傳預設 `RankRidge`）時,三支腳本之輸出須與修改前**逐位元／逐數字相同**（`--fit --horizon 60`／`--run` 重跑一次,diff 新舊 `probability_calibrator`／`direction_oos_sample` 相關列） | 否（純程式泛化+防禦性加固,零新資料寫入,同 Wave-A/RankEnsemble Phase 0 先例之「零風險部分」） |
| **Phase 1** | 條件觸發：Wave-A 某族真贏後,materialize 該族 OOS＋校準＋新 `model_id` DirStack 比較 | 見§4 Phase 1 條列 | **是**——觸碰確立級 direction 生產鏈之新資料寫入,須 Steward 明示範圍 |
| **升格** | 若 Phase 1 顯示新 DirStack 變體優於現況 | 本計畫不含,需另一輪 plan-first＋`direction_gate`／arena 準入審查 | 是（FZ/GATE-keep 硬邊界,不因評測贏自動晉升） |

---

## 6. 風險與硬邊界

- **零預設會有 Phase 1**——Wave-A Phase 0 探針現正跑著,**極可能 6 族全數不如 RankRidge**（承 RankEnsemble／SeqLSTM 兩次先例:橫斷面 Ridge 護城河比預期深）;若如此,本計畫止於 Phase 0（純防禦性加固+可重用泛化,零族真正投入 DirStack)。
- **R1/R2 修補建議獨立於 Phase 1 是否發生都執行**——這是本次查核發現的既有程式碼潤在缺陷,防禦性加固成本低（3 處程式碼修改,皆有預設值保留現況行為),不應因「暫無第二族」而擱置。
- **FZ/GATE-keep**：Phase 0／Phase 1 皆不改 `direction_gate`／`arena_admission_gate` 任何 criteria；升格判準不變。
- **no-SIM-apply／skip-sync**：全程零 FinMind／FRED、零 sim。
- **行為不變性為第一驗收項**——若 Phase 0 改完後,`RankRidge`（預設族）路徑之既有輸出有任何一位元差異,視為未過驗收,须回頭修正而非「大致一樣就好」。

---

## 7. 驗收方式

- Phase 0：`git diff` 對照三支腳本改動範圍；重跑 `--fit --horizon 60`／既有 H60 `--run` 前後輸出逐項比對（diff）；`ReadLints` 確認無新增 lint。
- 完成後寫 `audits/S4-DIRFAMILY-GENERALIZE-EXECUTED-20260804.md`（或當日日期),含行為不變性 diff 證據。

---

*定版（2026-08-04）。下一手＝待 Steward 授權 Phase 0（程式泛化＋R1/R2 防禦性加固,零新資料寫入)；Phase 1 純屬條件觸發,取決於現正背景執行之 Wave-A Phase 0 探針結果。*

---

## 執行後記（2026-08-04）

Steward 已授權（「approve_now」）,Phase 0 三支腳本編輯＋驗證已完成,詳見 `audits/S4-DIRFAMILY-GENERALIZE-EXECUTED-20260804.md`——行為不變性以演算法等價性直接證明（Ridge dispatch 位元級相同）+ 無資料成長干擾路徑逐值相同（H20 DirStack 前後 bit-exact）雙證據確立;R1/R2 修補生效。查核中另誠實揭露一項**與本計畫無關**之既有 AS_OF/exit_date 邊界問題（該 audit §3）,留 Steward 另裁。Phase 1 仍未觸發,待 Wave-A 探針完整結束後再評估。

---

## Phase 1 具體設計（2026-08-04 追記,觸發條件已滿足,待授權）

`RankSVM`@H20 已真贏且經獨立跨期分半複驗確認穩健（`audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md` §2/§7）——原§4 條件觸發成立。**但**證據**僅限 H20**（`RankSVM`@H60 未過門;H40/H82/H120 未經 Wave-A 探針評測),故 Phase 1 應**精準限於 H20**,不外推其餘 DirStack horizon。

**較原§4 outline 精簡之處**（讀碼複查後發現可省之步驟）：`train_direction_stack.py::_load_joined` 之 SQL 只讀 `probability_oos_sample`(rank_pctile/fwd_ret)與 `market_direction_probability`,**從未讀** `probability_calibrator`／`prediction_probability`——即 DirStack 合成**不需要**先跑 `calibrate_relative_probability.py --fit`(原§4 item 2)。本次 Phase 1 若僅為「研究比較 RankSVM 是否讓 DirStack 更好」,可省略此步,縮小改動面。

### 具體步驟

1. `python scripts/build_probability_oos_sample.py --model-family RankSVM --run --horizon 20`——materialize RankSVM 之 H20 OOS 樣本(新增列,`(horizon,panel_date,model_family,stock_id)` 唯一鍵下與既有 `RankRidge` 列共存、零覆蓋)。
2. **程式改動**（`train_direction_stack.py`)：`main()` 新增 `--model-family` CLI(預設 `"RankRidge"`,不破壞現況呼叫方式);`run()` 新增 `model_id` 參數(預設 `MODEL_ID="DirStack"`,傳入時如 `f"DirStack_{model_family}"`),取代寫死之 `MODEL_ID` 常數於 INSERT 處——**新 model_id 是必要(非選配)**:`direction_oos_sample` 之唯一鍵含 `model_id`,若不換 id,`RankSVM` 版本會透過 `ON CONFLICT ... DO UPDATE` **覆蓋既有 `DirStack`(RankRidge)列**,污染現況(呼應原§2 R3 表述精神)。
3. `python scripts/train_direction_stack.py --run --horizons 20 --model-family RankSVM`——寫入 `direction_oos_sample` 之 `model_id='DirStack_RankSVM'`(H20 限定,`DirStack` 既有列不受影響)。
4. **研究比較(新增一支一次性腳本,非產品碼,比照 Wave-A 探針之性質)**：讀 `direction_oos_sample` 兩個 `model_id`(`DirStack` vs `DirStack_RankSVM`)於 H20 之逐折 `p_up`/`y_up`,算基本分類指標(如 Brier、hit-rate、AUC)對照——**明確不用** `evaluate_direction_gate.py`(該路徑吃 `criteria`/`estimand` registry,登記等同「送審 GATE」,超出研究比較範圍)。

### 明確不做(non-goals,呼應原§4 item 4 與 FZ/GATE-keep)

- **不**於 `direction_gate_criteria`(或等義 registry)新增任何指向 `DirStack_RankSVM` 之列——那等同啟動一次 GATE 送審程序,需另一輪(第三輪)Steward 明示授權,非本 Phase 1 範圍。
- **不**跑 `calibrate_relative_probability.py --model-family RankSVM`(上述讀碼確認非 DirStack 之必要前置;若 Steward 認為仍想要完整 P6 鏈路支援 RankSVM,屬另一個獨立問題,可另案)。
- **不**改動 `arena_admission_gate`／任何 live serve 路徑。
- 若研究比較顯示 `DirStack_RankSVM` 優於 `DirStack`——**仍不自動晉升**,止於誠實記錄於 EXECUTED audit,升格需第三輪 plan-first。

### 風險與範圍確認

- 新增之 `probability_oos_sample`(RankSVM,H20)與 `direction_oos_sample`(`DirStack_RankSVM`,H20)皆為**加法**,零覆蓋既有 `RankRidge`/`DirStack` 列——回滾成本低(可直接 `DELETE WHERE model_family='RankSVM'`／`WHERE model_id='DirStack_RankSVM'`)。
- `train_direction_stack.py` 之程式改動(`--model-family` CLI＋`model_id` 參數化)本身**不影響**預設呼叫(`RankRidge`/`DirStack`)之既有行為——同 Phase 0 之行為不變性紀律,執行後應驗證預設路徑仍 bit-exact。
- 估計耗時：步驟 1(H20 OOS materialize,≈90-110s×folds,量級同 Wave-A 探針之 H20 RankSVM 段)+步驟 3(DirStack 合成,幾秒級,同 Phase 0 驗證時之 H20 DirStack 速度)+步驟 4(SQL 聚合,秒級)——總計預估 <5 分鐘,遠低於 Wave-A/DIRFAMILY 驗證之規模。
