# 本地 AI 股市模擬自進化——實作計畫書（2026-07-31）

* **依據**：`reports/augur_plain_language_full_report_20260730.md`（說人話報告書・世界建構版 v2）
* **Steward 指示**：「本地AI股市模擬自進化計畫依目前的 Augur 全專案說人話報告書做出一版最佳的實作計畫書」
* **性質**：**計畫書，非實作**。依 CLAUDE #20 計畫先行——**拍板後才動工**。
* **繕打**：claude（Fable 5）〔不冒充親簽 `AUGUR-MC v1.6 §8.1`；治權提案由 Steward 決議〕
* **完整性自陳**：本書依 CLAUDE #20 **v1.39.0** 撰寫，含 (a) 表 schema〔新表 DDL ＋所讀既有表〕
  與 (b) python 程式規畫〔檔·函式·角色·簽名·輸入輸出表〕，另附元件、端點、分階段、驗收。

---

## 〇、一頁摘要

**這件事是什麼**：讓「用什麼方法模擬市場風險形狀」這件事，自己走完報告書 §四那條**同一條路**
——候選 → 預先凍結判準之證據通道 → 人類授權門 → 晉升或判死留檔 → 後果回流。
它同時是報告書八行走者中的 **④AI 能力宣稱**、**⑤模擬方法**、**⑦迭代程序本身**三重身分。

**為什麼是「模擬」而不是「預測」**：憲章 §1.2 與世界模型 A.38 把**逐日價格點位／路徑／目標價**
列為**永久除外項、無 GATE 可解**（解除唯再修憲）。路徑類需求**唯得以蒙地卡羅模擬情境滿足**，
且硬綁「模擬非預測」。所以本計畫的自進化**目標函數只能是「風險形狀的校準品質」**——
不是方向命中率、不是報酬。這不是保守，是硬邊界。

**現在最關鍵的三個事實**（我親驗，非轉述）：

| # | 事實 | 實證 |
|---|---|---|
| 1 | **法源已成立、不再空懸** | 憲章 v1.50.0「普遍晉升路徑（總則）」明文涵蓋「能力宣稱（含 AI 自身）」與「方法採用（模擬法、估計法）」。報告書 §四「④⑤在治權層無明文」之誠實標注**已被同日入憲追過**。 |
| 2 | **但「專章」不存在 ⇒ 一開工即路徑空懸** | `evolution_prereg_gate` 實查**僅 1 列**（V2-SUNSET）；其 `axis` CHECK 實查＝`('tw','lai','raw','program')`，**無 `'sim'`**——模擬軸**連預註冊都寫不進去**。總則明文「專章缺任一節點即路徑空懸，補正前不得作『已確立』級宣稱」。 |
| 3 | **既有模擬資產無任何誠實閘** | `mc_simulation_run` **540 列、0 個 trigger**（實查）——可被無痕 DELETE。而 `CHECK (is_simulation)` 在，四鎖之一守住。 |

**要 Steward 拍板的，只有三件**（見 §九）：專章文字與終審定性、`axis` 加 `'sim'` 之修憲位階認定、
以及是否接受「人簽為偵測而非預防」（本機 `pg_roles` 實查**無 `hugo` 角色**，機器分不出人與 AI）。

---

## 一、錨與硬邊界（每條標明強制落點）

報告書把股市定位為**第一個登錄域**——「在憲法眼裡，金融工具與工廠、機器地位相同，都只是例子」、
「把第一個域換成氣象或醫療，八層正文一字不必改」、「**路屬世界，足跡屬域**」。
故本計畫**不是替股市造一條新路**，而是讓模擬方法走上**既有的同一條路**。

### 硬邊界清單

## 硬邊界清單（不得逾越；每條註明強制落點）

| # | 邊界（來源原文） | 強制落點（實作） |
|---|---|---|
| **H-1** | 逐日價格點位／路徑／目標價**無合法模態表徵位置、無 GATE 可解**（`docs/系統架構大憲章_v1.52.0.md:139`「解除唯再修憲」；WM A.38） | 八張新表 DDL **無任何逐路徑欄**；`mc_simulation_run_is_simulation_check CHECK (is_simulation)` 維持；驗收 V6.4 |
| **H-2** | **不以任何模型預測 tilt 抽樣**（`scripts/simulate_mc_paths.py:8-9`） | `simulation_method_registry.tilt_free boolean CHECK (tilt_free)`（DB 級）＋`augur/simulation/candidate.py:FORBIDDEN_KEY_PATTERNS`（code 級）＋驗收 V4.3 |
| **H-3** | 自進化之**合法目標函數只能是風險形狀校準**，不得是方向命中率／報酬（H-1＋H-2 之推論） | `sim_evolution_iteration_ledger.gain_basis CHECK IN ('calibration_delta','none','incomparable')`——**DB 層即無方向/報酬 basis 可寫** |
| **H-4** | **判準須先於資料凍結、以指紋錨定，評估時不符即拒**（憲章 v1.50.0 節點 2） | `evolution_prereg_gate` trigger `prereg_gate_no_goalpost()`（實查：criteria_sha 不可改、終態不可改）＋`eval_contract.verify_frozen()` 評估前覆算 |
| **H-5** | **換尺＝換身分**（ONT T.28：GATE 同一 iff〔預註冊識別 × 判準凍結序〕） | `sim_calibration_eval` UNIQUE 鍵含 `eval_code_hash`；換尺開新 `gate_id`、舊列轉 `superseded`；`sim_candidate_forward_only()` 擋身分欄改動 |
| **H-6** | **地板臂不可省**；地板未被顯著超越者，該分數不得作能力宣稱（記憶級鐵律，07-26 / 07-28 兩度實犯） | `eval_contract.arms_required()` 五臂；驗收 V3.2／V3.3；`floor_beaten(..., margin)` 由凍結 criteria 提供 margin |
| **H-7** | **終審須明文定性為統計級**（v1.50.0 節點 2 括號） | P1 專章文字＋`evolution_prereg_gate.criteria.terminal_tier='statistical'`；缺此即「路徑空懸」，一切輸出不得作「已確立」宣稱 |
| **H-8** | **人閘不可自動化、AI 不得代簽**；A.53 PME-AUTO-B 豁免**不及於**模擬方法（lens 1 §3.4） | `chk_sev_promote_signed`（DB CHECK）＋`gate_ref` FK→`governance_proposal`＋兩支 CLI `_require_tty()`＋**不設人名旗標**＋driver `_selftest` 斷言程式體不含 `promoted_by/decided_by/approved_by` 字面。**誠實登記：本機無 hugo 角色（`pg_roles` 實查），此為偵測非預防** |
| **H-9** | **OCV 單向棘輪**：不得以 Learning 落地任何降低監督之變更；度量不可自我洗白（L6.17／L6.19／L6.18(c)） | 迭代 driver 之可調維度白名單只含模擬參數；**不得**把「減少人工確認／延長自動鏈／放寬門檻」列為候選；`apply_allowed` 預設 false 且本軸**無 auto-APPLY 路徑** |
| **H-10** | **self-reported 不得單獨升信**；model output 永久攜 synthetic、TR-C ≤ MODERATE（KS.76/77／L5.7） | `sim_llm_proposal.is_synthetic CHECK(is_synthetic)`＋`trust_rank CHECK='TR-C'`；`sim_evolution_candidate` 同兩欄；晉升證據必含**非 LLM 產出**之校準讀數 |
| **H-11** | **禁任何外部／雲端 LLM**；可靠度不足只能換本機模型／GPU／量化（憲章 :192） | `propose_simulation_candidates.py` 常數 `OLLAMA="http://127.0.0.1:11434/api/generate"`、`MODEL="qwen3:4b"`；無任何 http client 指向外部；`grid_fallback()` 為 LLM 不可用時之零-LLM 後路 |
| **H-12** | **節制取用**：不得成為外部 API 壓力源；撞限額即停不重試風暴（#24／#28） | 本軸**零 FinMind／零 FRED 呼叫**（只讀庫內 `TaiwanStockPriceAdj`）；LLM 每輪 `MAX_CALLS_PER_RUN=40`、flock `-n` 搶不到即降級；驗收 V4.5 |
| **H-13** | **clean-room**：禁前身系統 code／數字／設定回流（#17） | 新 package `src/augur/simulation/` 全新寫；量尺為解析式標準統計量（非移植） |
| **H-14** | **fail-closed 須為 DB trigger 級，非僅腳本自律**（憲章 :136；L7 :253「證明形式為可執行測試」） | 五道 DB 級：`CHECK(is_simulation)`／`CHECK(tilt_free)`／`chk_sev_promote_signed`／`chk_sro_forward`／`honesty_delete_only_guard`；驗收 V2.2 以 `pg_trigger` 實查 |
| **H-15** | **判死留檔不可靜默消失、終局不可事後翻案**（v1.50.0 節點 4） | `sim_evolution_verdict` 掛 delete/truncate guard＋`honesty_ledger_guard`（UPDATE 須 `SET LOCAL augur.honesty_write='on'`）；翻案唯經 `reopen_of` 新列 |
| **H-16** | **三敵人不是試錯對象**（原則精華 :140） | 逐級逼近只作用於模擬參數；`chk_sro_forward CHECK (label_date > asof_date)`＋`unsettleable` 不得帶值（零補值 #1）＋驗收 V4.4 |
| **H-17** | **不是自動駕駛**：不得自改治權判準、不得自動下單、人得緊急停（`docs/系統核心思想_v1.9.0.md:126`） | 本軸**無 APPLY 步驟**（S0–S6 無 apply）；`evolution_kill_switch` scope='sim' 開輪即查（OR fail-safe）；`risk_policy` 單向唯讀、驗收 V6.3 |
| **H-18** | **落日債**：世界概念直綁禁令 2026-10-14 生效（報告書 :179） | 新程式讀價一律經單一 reader 函式（`score_simulation_calibration.py` 內），Registry 到位時只換一處；計畫書須誠實登記此為**已知未清之債**，非已解 |

---

## 二、缺口表

## 缺口表（報告書錨 ↔ 現況 ↔ 差距 ↔ 補法）

補法分類：**新建**＝目前無載體／無程式；**改造**＝既有物需加欄/加閘/擴 CHECK；**接線**＝兩端都在、中間沒接。

| # | 報告書要求 X（錨） | 現況 Y（實證） | 差距 Z | 補法 |
|---|---|---|---|---|
| **A. 普遍晉升路徑（憲章 v1.50.0 五節點，`docs/系統架構大憲章_v1.52.0.md:204-218`）** |
| A1 | 節點1「候選：明示 origin 與所依證據；候選期間不得被表述為已確立」 | 無任何「模擬方法候選」載體。`mc_simulation_run` 540 列只有已跑結果，無 candidate/origin/status 欄（實查 12 欄無一為狀態欄） | 模擬方法候選在 DB 中不存在 | **新建** `sim_evolution_candidate` |
| A2 | 節點2「判準須**先於資料凍結**、以指紋錨定，評估時不符即拒」 | `evolution_prereg_gate` 僅 1 列（V2-SUNSET, axis='program', evaluated_at NULL）；`axis` CHECK 實查＝`('tw','lai','raw','program')`，**無 'sim'** | 模擬軸連預註冊都寫不進去（CHECK 會拒） | **改造**（ALTER CHECK 加 'sim'）＋**新建** gate 列（人簽） |
| A3 | 節點2 括號「無經濟對價者須於**專章明文**宣告以何為終審，並載明其為**統計級非實效級**」 | 無任何文件為模擬方法作此宣告（lens 1 查無） | 缺此句＝路徑空懸，永不得作「已確立」宣稱 | **新建**（治權專章文字＋寫入 gate.criteria.terminal_tier='statistical'） |
| A4 | 節點3「人類授權門；AI 不得代簽」 | 本機 `pg_roles` 非系統角色僅 `augur/augur_predict/postgres/rdai/stock/ttai`（實查），**無 hugo**；`mc_simulation_run` **零 trigger**（實查 `pg_trigger` count=0） | 模擬側完全無人閘，且機器無法區分人／AI | **新建**（gate_ref 強制 FK→`governance_proposal` ＋ CLI 不設人名旗標；誠實登記為偵測非預防） |
| A5 | 節點4「判死留檔、永不靜默消失、終局不可翻案」 | `mc_simulation_run` 無 verdict/superseded 欄、**無 append-only guard**（實查 0 trigger、僅 PK 索引）；lens 1 所稱「四法一輪結案」在 DB 查無 verdict 列 | 判死節點在模擬軸物理上不存在；且已跑結果可被無痕 DELETE | **新建** `sim_evolution_verdict`＋**改造** `mc_simulation_run` 掛 `honesty_delete_only_guard` |
| A6 | 節點5「後果回流成新觀測」 | 模擬跑完後無「實現值 vs 分位錐」的比對載體 | 沒有回流腿＝無法量校準、無法自進化 | **新建** `sim_realized_outcome` |
| **B. 硬邊界（A.38／憲章 §1.2 四鎖）** |
| B1 | 「逐日價格點位/路徑/目標價無合法模態表徵位置、無 GATE 可解」 | `mc_simulation_run_is_simulation_check CHECK (is_simulation)` 已存在（實查）；只存 summary 分位錐 | 邊界本身已守住 | **維持**（新表一律不得存逐路徑；DDL 內不設 path 欄） |
| B2 | 「不以任何模型預測 tilt 抽樣」（`scripts/simulate_mc_paths.py:8-9`） | 現行引擎守住，但只是 docstring 自律，**無機械閘**阻止未來候選帶 tilt 參數 | 自進化一旦可提參數，就可能提出 tilt 型參數而無人擋 | **新建**（`simulation_method_registry.tilt_free boolean CHECK (tilt_free)`＋候選 spec 白名單校驗函式） |
| B3 | 方法白名單為事實人閘 vs CLAUDE #29(b) 禁 hardcode | `mc_simulation_run_method_check` 實查為 **20 值 CHECK**（寫死在 DDL） | 新方法＝改 DDL；且違 #29(b) | **改造**（改 `simulation_method_registry` 註冊表＋FK，「新增一列」本身設為人閘動作，兩者兼得） |
| **C. 三敵人與量尺（H-3／H-6）** |
| C1 | 「判準先凍結再看資料」「地板臂不可省」 | 現行 `local_model_eval_run.arm` 實查值有 ceiling/floor/shuffled/mismatched/robot/behavior；但 `evolution_evidence_run_arm_check` 實查＝`('ceiling','floor','shuffled','mismatched','live')`，**無 'robot'**；`axis_check`＝`('tw','raw')`，**無 'sim'/'lai'** | 統一證據帳擋掉模擬軸與 robot 臂 | **改造**（ALTER 兩個 CHECK） |
| C2 | 「終審為統計級」須有機械可算之量尺 | `grep -rn "pinball\|crps\|CRPS"` 全 repo **零命中**；repo 內 "PIT" 一律指 point-in-time（`run_raw_interaction_ic.py:74` 等），非機率積分變換 | **校準量尺完全不存在**——覆蓋率/pinball/CRPS/PIT-KS 一支都沒寫 | **新建** `src/augur/simulation/calibration.py` |
| C3 | `#8` anti-leakage | raw 側**無發布日欄**（實查：`TaiwanStockFinancialStatements` 全欄＝date,stock_id,type,value,origin_name）；靠 `src/augur/features/release_lag.py:33-36` 法定滯後推算；該檔 `:19` 自陳金融保險業 60 日未分支 | 模擬本身只吃日價（風險較低），但若候選 spec 允許引入財報條件抽樣即觸洞 | **改造**（spec 白名單只准價量來源，禁財報條件；於候選校驗函式強制） |
| **D. 反身性鏈（T.28／ID.11／KS.76-77／L6.19／L7.5）** |
| D1 | T.28「GATE 同一 iff〔預註冊識別 × **判準凍結序**〕」 | `prereg_gate_no_goalpost()` 實查已擋 criteria_sha 變更與終態改動 | 機制已在，模擬軸只是沒用它 | **接線**（模擬軸 gate 一律走此表） |
| D2 | ID.11「Augur 自身個體須鑄 identifier、永不刪除永不重用」 | 模擬方法／每一代配置無 identifier | 無 | **新建**（`candidate_id='simc_'||sha256(spec)[:12]`，UNIQUE spec_sha） |
| D3 | KS.76/77＋L5.7「self-reported 不得單獨升信；model output 永久攜 synthetic、TR-C 天花板」 | 無任何欄位記錄 LLM 產物之 synthetic 標記 | 若 LLM 產候選，其產物在證據法上無標記 | **新建** `sim_llm_proposal`（`is_synthetic CHECK(is_synthetic)`、`trust_rank CHECK='TR-C'`） |
| D4 | L6.19「Learning 不得直寫世界狀態、不得降低 OCV」；L7.5「先登錄自身 kill-switch」 | `evolution_kill_switch` 4 列（global/tw/lai/raw 全 clear，皆為種子列從未被人動過）；`augur.philosophy.evolution.KILL_SCOPES=('tw','lai','raw','global')` **無 'sim'** | 模擬軸無自己的停機開關 | **改造**（KILL_SCOPES 加 'sim'＋種子列） |
| **E. 迭代程序（行走者⑦）與現有基礎設施** |
| E1 | 「每一步留痕可回放」 | 帳本骨架已有兩份：`evolution_iteration_ledger`（CHECK `axis='tw'`）、`local_ai_iteration_ledger`（CHECK `axis='lai'`，**0 列**）——實查兩表各自硬綁單一 axis | 模擬軸無帳本；且既有表 CHECK 擋住 | **新建** `sim_evolution_iteration_ledger`（照抄骨架，axis='sim'） |
| E2 | 「後果回流成新觀測」之排程可行性 | `evolution_deferred_work` 4 列 **cleared_at 全 NULL**；TWEVO 07-28/07-29 defer、07-30 I3 `TimeoutExpired 7200s`；`available` RAM 實測 806 MiB、`llama-server` RSS 5.1 GB、loadavg 29.96/12 核 | 23:00 車道已壞；新軸若排夜間必再 defer | **改造**（排白天窗 06:20–20:00；經 `HeavySlot('sim_evolution')`；預算 ≈300-380 次 qwen3:4b/日） |
| E3 | 報告書 §四「本地 AI 是憲法要求」 | ollama 三模型實查：qwen3:4b(2.5GB)/qwen3:8b(5.23GB)/nomic-embed-text；`OLLAMA_MAX_LOADED_MODELS=1` | 只能單模型串行；8b 需先卸 4b | **接線**（候選產生器固定 qwen3:4b、flock `/tmp/augur_llm.lock`） |
| E4 | 權重級自進化 | venv 實查**無 peft/trl/bitsandbytes/gguf**；`local_model_version` 4 列 `lora_path` 全 NULL、全 retired、serving=0 | 微調路線本機 no-go | **明確不做**（P7 選配，須列環境前置） |
| **F. 落日債與跨軸** |
| F1 | 世界概念直綁消費禁令落日 **2026-10-14**（報告書 :179） | 本機無 World Concept Registry 載體；消費端直綁 `TaiwanStockPriceAdj` | 新元件若直綁＝落日前 75 天新增違規債 | **改造**（新程式讀價一律經單一 reader 函式，留 Registry 換插點；本計畫不建 Registry） |
| F2 | 「後果回流」跨軸 | `evolution_hypothesis_hint` 三重防護（CHECK＋`hint_decision_forward_only`＋`honesty_delete_only_guard`，實查）是全庫最完整人閘樣板 | 模擬軸沒接跨軸傳遞 | **接線**（模擬軸產出以 hint 形式回流，沿用既有表） |
| F3 | 風險畫像「保守值入」單向 | `risk_policy` 6 列（實查 7 欄：horizon/policy_key/threshold/action/source_ref/note/updated_at）；`simulate_portfolio_risk.py:11` 明文「單向唯讀不回寫」 | 需明文延續 | **維持**（自進化嚴禁寫 `risk_policy`；於驗收哨兵斷言列數/內容未變） |

---

## 三、(a) 表 schema

## (a) 需新建之表 — 可直接執行之 DDL

> 前提實查：PostgreSQL **17.10**；guard 函式 `honesty_delete_only_guard()`／`honesty_ledger_guard()` 已存在於 public schema（`pg_proc` 實查）。所有 DDL 建議由 `scripts/migrate_sim_evolution_ddl.py --apply` 執行（#6 破壞性操作須明示）。
> **通則**：所有新表一律不得有「逐路徑」欄（H-1）；一律掛 append-only guard（H-16）。

### 1. `simulation_method_registry` — 取代 20 值硬寫 CHECK（#29b）＋方法採用之人閘

```sql
CREATE TABLE IF NOT EXISTS simulation_method_registry (
    method        text PRIMARY KEY,
    family        text NOT NULL CHECK (family IN
                  ('bootstrap','parametric','episode_replay','episode_analog','copula','evt')),
    purpose       text NOT NULL,
    param_schema  jsonb NOT NULL DEFAULT '{}'::jsonb,
    tilt_free     boolean NOT NULL DEFAULT true CHECK (tilt_free),
    status        text NOT NULL DEFAULT 'registered'
                  CHECK (status IN ('registered','retired')),
    gate_ref      text REFERENCES governance_proposal(proposal_id),
    approved_by   text,
    approved_at   timestamptz,
    registered_at timestamptz NOT NULL DEFAULT now(),
    git_sha       text NOT NULL,
    note          text,
    CONSTRAINT chk_smr_registered_signed CHECK (
        status <> 'registered'
        OR (approved_by IS NOT NULL AND approved_at IS NOT NULL AND gate_ref IS NOT NULL))
);
CREATE TRIGGER smr_no_delete   BEFORE DELETE   ON simulation_method_registry
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER smr_no_truncate BEFORE TRUNCATE ON simulation_method_registry
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
COMMENT ON COLUMN simulation_method_registry.tilt_free IS
    'H-2 硬綁:CHECK(tilt_free) 使「以模型預測 tilt 抽樣」之方法在 DB 層永遠註冊不進來';
```
**必要性**：`tilt_free` 的 `CHECK (tilt_free)` 是 H-2 的 DB 級落地（仿 `mc_simulation_run_is_simulation_check` 之寫法，實查該 CHECK 即 `CHECK (is_simulation)`）；`chk_smr_registered_signed` 使「新增一列方法」在機器上必然帶人簽＋提案指標。

### 2. `sim_evolution_candidate` — 節點1「候選」

```sql
CREATE TABLE IF NOT EXISTS sim_evolution_candidate (
    candidate_id  text PRIMARY KEY,                       -- 'simc_'||left(sha256(canonical_spec),12)
    method        text NOT NULL REFERENCES simulation_method_registry(method),
    spec          jsonb NOT NULL,
    spec_sha      text NOT NULL UNIQUE,
    origin        text NOT NULL CHECK (origin IN ('llm_local','grid','human','carryover')),
    origin_ref    text,
    is_synthetic  boolean NOT NULL DEFAULT true,
    trust_rank    text NOT NULL DEFAULT 'TR-C' CHECK (trust_rank = 'TR-C'),
    status        text NOT NULL DEFAULT 'candidate'
                  CHECK (status IN ('candidate','evaluating','evaluated','promoted','killed','superseded')),
    iteration_uid text,
    gate_ref      text REFERENCES evolution_prereg_gate(gate_id),
    created_at    timestamptz NOT NULL DEFAULT now(),
    git_sha       text NOT NULL,
    note          text
);
CREATE INDEX IF NOT EXISTS idx_simc_status  ON sim_evolution_candidate (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_simc_method  ON sim_evolution_candidate (method);

CREATE OR REPLACE FUNCTION sim_candidate_forward_only() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.status IN ('promoted','killed','superseded')
       AND NEW.status IS DISTINCT FROM OLD.status THEN
        RAISE EXCEPTION 'candidate % 已終態(%)不可回改——單向前進(P4.E3);翻案走新列+新證據',
            OLD.candidate_id, OLD.status;
    END IF;
    IF NEW.spec_sha IS DISTINCT FROM OLD.spec_sha OR NEW.method IS DISTINCT FROM OLD.method THEN
        RAISE EXCEPTION 'candidate % 身分欄不可改(T.28 同一 iff);換 spec=新列', OLD.candidate_id;
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER simc_forward_only BEFORE UPDATE   ON sim_evolution_candidate
    FOR EACH ROW       EXECUTE FUNCTION sim_candidate_forward_only();
CREATE TRIGGER simc_no_delete    BEFORE DELETE   ON sim_evolution_candidate
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER simc_no_truncate  BEFORE TRUNCATE ON sim_evolution_candidate
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
```
**必要性**：`spec_sha` UNIQUE＋身分欄不可改＝T.28 同一性；forward-only 仿實查之 `hint_decision_forward_only()`。

### 3. `sim_run_link` — 把既有 `mc_simulation_run` 掛進本軸（**不 ALTER 生產表**，守 #3 最小邊界）

```sql
CREATE TABLE IF NOT EXISTS sim_run_link (
    run_id        text PRIMARY KEY REFERENCES mc_simulation_run(run_id),
    candidate_id  text NOT NULL REFERENCES sim_evolution_candidate(candidate_id),
    gate_id       text NOT NULL REFERENCES evolution_prereg_gate(gate_id),
    iteration_uid text NOT NULL,
    arm           text NOT NULL CHECK (arm IN ('live','ceiling','floor','shuffled','mismatched','robot')),
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_simlink_cand ON sim_run_link (candidate_id, arm);
CREATE TRIGGER simlink_no_delete   BEFORE DELETE   ON sim_run_link
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER simlink_no_truncate BEFORE TRUNCATE ON sim_run_link
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
```

### 4. `sim_realized_outcome` — 節點5「後果回流」

```sql
CREATE TABLE IF NOT EXISTS sim_realized_outcome (
    run_id         text PRIMARY KEY REFERENCES mc_simulation_run(run_id),
    target_id      text NOT NULL,
    asof_date      date NOT NULL,
    horizon_td     integer NOT NULL,
    label_date     date NOT NULL,
    realized_close double precision,
    realized_logret double precision,
    settle_mode    text NOT NULL CHECK (settle_mode IN ('normal','last_trade','unsettleable')),
    settled_at     timestamptz NOT NULL DEFAULT now(),
    git_sha        text NOT NULL,
    CONSTRAINT chk_sro_forward CHECK (label_date > asof_date),
    CONSTRAINT chk_sro_unsettleable_null CHECK (
        settle_mode <> 'unsettleable' OR realized_logret IS NULL)
);
CREATE INDEX IF NOT EXISTS idx_sro_asof ON sim_realized_outcome (asof_date, horizon_td);
CREATE TRIGGER sro_no_delete   BEFORE DELETE   ON sim_realized_outcome
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER sro_no_truncate BEFORE TRUNCATE ON sim_realized_outcome
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
```
**必要性**：`chk_sro_forward` 是 anti-leakage 的 DB 級最後一道（label 日必嚴格晚於 as-of）；`unsettleable` 不得帶值＝#1 零補值。

### 5. `sim_calibration_eval` — 統計級終審之讀數（含強制對照臂）

```sql
CREATE TABLE IF NOT EXISTS sim_calibration_eval (
    eval_id        bigserial PRIMARY KEY,
    gate_id        text NOT NULL REFERENCES evolution_prereg_gate(gate_id),
    candidate_id   text REFERENCES sim_evolution_candidate(candidate_id),
    arm            text NOT NULL CHECK (arm IN ('live','ceiling','floor','shuffled','mismatched','robot')),
    eval_set_id    text NOT NULL,
    eval_code_hash text NOT NULL,
    n_runs         integer NOT NULL,
    n_valid        integer NOT NULL,
    n_excluded     integer NOT NULL DEFAULT 0,
    is_invalid     boolean NOT NULL DEFAULT false,
    cov_p50        double precision,
    cov_p80        double precision,
    cov_p90        double precision,
    pinball_mean   double precision,
    crps_mean      double precision,
    pit_ks_stat    double precision,
    pit_ks_p       double precision,
    detail         jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at     timestamptz NOT NULL DEFAULT now(),
    git_sha        text NOT NULL,
    CONSTRAINT chk_sce_valid_le_runs CHECK (n_valid <= n_runs)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_sce_cell ON sim_calibration_eval
    (gate_id, coalesce(candidate_id,'-'), arm, eval_set_id, eval_code_hash);
CREATE TRIGGER sce_no_delete   BEFORE DELETE   ON sim_calibration_eval
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER sce_no_truncate BEFORE TRUNCATE ON sim_calibration_eval
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
```
**必要性**：`eval_code_hash` 進 UNIQUE 鍵＝換尺即換格（H-5，仿 `local_model_eval_run` 之 `eval_code_hash` 實查欄）；`is_invalid` 供截斷/不足樣本誠實記錄（不補分，#1）。

### 6. `sim_evolution_verdict` — 節點4「晉升或判死留檔」

```sql
CREATE TABLE IF NOT EXISTS sim_evolution_verdict (
    verdict_id        bigserial PRIMARY KEY,
    candidate_id      text NOT NULL REFERENCES sim_evolution_candidate(candidate_id),
    gate_id           text NOT NULL REFERENCES evolution_prereg_gate(gate_id),
    verdict           text NOT NULL CHECK (verdict IN ('promoted','killed','undecidable')),
    basis             jsonb NOT NULL,
    evidence_eval_ids bigint[] NOT NULL,
    decided_by        text,
    decided_at        timestamptz,
    gate_proposal_ref text REFERENCES governance_proposal(proposal_id),
    reopen_of         bigint REFERENCES sim_evolution_verdict(verdict_id),
    created_at        timestamptz NOT NULL DEFAULT now(),
    git_sha           text NOT NULL,
    CONSTRAINT chk_sev_promote_signed CHECK (
        verdict <> 'promoted'
        OR (decided_by IS NOT NULL AND decided_at IS NOT NULL AND gate_proposal_ref IS NOT NULL)),
    CONSTRAINT chk_sev_evidence_nonempty CHECK (array_length(evidence_eval_ids,1) >= 1)
);
CREATE INDEX IF NOT EXISTS idx_sev_cand ON sim_evolution_verdict (candidate_id, created_at DESC);
CREATE TRIGGER sev_no_delete   BEFORE DELETE   ON sim_evolution_verdict
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER sev_no_truncate BEFORE TRUNCATE ON sim_evolution_verdict
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER sev_no_update   BEFORE UPDATE   ON sim_evolution_verdict
    FOR EACH ROW       EXECUTE FUNCTION honesty_ledger_guard();
```
**必要性**：`chk_sev_promote_signed` ＝節點3 人閘之 DB 級落地（**仿實查之 `chk_dg_approved_signed`／`model_version_no_goalpost()`**）；`reopen_of` 使「唯經新證據重走本路」可留痕而不竄改原判。`honesty_ledger_guard` 使 UPDATE 須 `SET LOCAL augur.honesty_write='on'`（實查該函式原文即此語意）。

### 7. `sim_llm_proposal` — L5.7 synthetic 永久標記／KS.77 self-reported 隔離

```sql
CREATE TABLE IF NOT EXISTS sim_llm_proposal (
    proposal_id   bigserial PRIMARY KEY,
    iteration_uid text NOT NULL,
    model         text NOT NULL,
    prompt_sha    text NOT NULL,
    raw_output    text NOT NULL,
    parsed_ok     boolean NOT NULL,
    reject_reason text,
    candidate_id  text REFERENCES sim_evolution_candidate(candidate_id),
    is_synthetic  boolean NOT NULL DEFAULT true CHECK (is_synthetic),
    trust_rank    text NOT NULL DEFAULT 'TR-C' CHECK (trust_rank = 'TR-C'),
    latency_ms    integer,
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_simllm_iter ON sim_llm_proposal (iteration_uid, created_at);
CREATE TRIGGER simllm_no_delete   BEFORE DELETE   ON sim_llm_proposal
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER simllm_no_truncate BEFORE TRUNCATE ON sim_llm_proposal
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
```

### 8. `sim_evolution_iteration_ledger` — 行走者⑦（照抄實查骨架，axis 綁 'sim'）

```sql
CREATE TABLE IF NOT EXISTS sim_evolution_iteration_ledger (
    iteration_id        bigserial PRIMARY KEY,
    iteration_uid       text NOT NULL UNIQUE
                        CHECK (iteration_uid ~ '^sim-[0-9]{8}-r[0-9]{2}$'),
    axis                text NOT NULL DEFAULT 'sim' CHECK (axis = 'sim'),
    opened_at           timestamptz NOT NULL DEFAULT now(),
    closed_at           timestamptz,
    status              text NOT NULL DEFAULT 'planned'
                        CHECK (status IN ('planned','running','succeeded','failed','halted','stopped_no_gain')),
    trigger_code        varchar(64) NOT NULL,
    steps_json          jsonb NOT NULL DEFAULT '[]'::jsonb,
    gain                boolean,
    gain_basis          varchar(32)
                        CHECK (gain_basis IS NULL OR gain_basis IN
                              ('calibration_delta','none','incomparable')),
    gain_evidence       jsonb NOT NULL DEFAULT '{}'::jsonb,
    consecutive_no_gain integer NOT NULL DEFAULT 0,
    stop_reason         text,
    hints_in            jsonb NOT NULL DEFAULT '[]'::jsonb,
    hints_out           jsonb NOT NULL DEFAULT '[]'::jsonb,
    gate_ref            text REFERENCES evolution_prereg_gate(gate_id),
    eval_set_id         text,
    eval_code_hash      text,
    n_trials            integer,
    selection_scope     text,
    apply_allowed       boolean NOT NULL DEFAULT false,
    closed_by           text,
    superseded_by       text,
    evidence_hash       text,
    notes               text
);
CREATE TRIGGER sim_iter_no_delete   BEFORE DELETE   ON sim_evolution_iteration_ledger
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER sim_iter_no_truncate BEFORE TRUNCATE ON sim_evolution_iteration_ledger
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
```
**理由（為何不共用既有表）**：實查 `evolution_iteration_ledger` 有 `CHECK (axis = 'tw')`、`local_ai_iteration_ledger` 有 `CHECK (axis = 'lai')`——本專案既定樣式即「一軸一表、CHECK 焊死」，故新軸新表為最小邊界寫法；`gain_basis` 只給 `calibration_delta`（**不給任何方向/報酬類 basis**，H-2 的判準層落地）。

---

## 對既有表之遷移（同一 migrate 腳本，逐項 `--apply` 明示；#6）

```sql
-- M1 讓預註冊閘容納模擬軸（實查現行 CHECK 為 tw/lai/raw/program）
ALTER TABLE evolution_prereg_gate DROP CONSTRAINT evolution_prereg_gate_axis_check;
ALTER TABLE evolution_prereg_gate ADD  CONSTRAINT evolution_prereg_gate_axis_check
    CHECK (axis IN ('tw','lai','raw','program','sim'));

-- M2 統一證據帳容納模擬軸與 robot 臂（實查現行 axis=tw/raw、arm 無 robot）
ALTER TABLE evolution_evidence_run DROP CONSTRAINT evolution_evidence_run_axis_check;
ALTER TABLE evolution_evidence_run ADD  CONSTRAINT evolution_evidence_run_axis_check
    CHECK (axis IN ('tw','raw','lai','sim'));
ALTER TABLE evolution_evidence_run DROP CONSTRAINT evolution_evidence_run_arm_check;
ALTER TABLE evolution_evidence_run ADD  CONSTRAINT evolution_evidence_run_arm_check
    CHECK (arm IN ('ceiling','floor','shuffled','mismatched','robot','live'));

-- M3 生產模擬表補上 append-only（實查目前 0 個非內部 trigger＝可被無痕刪）
CREATE TRIGGER mcsim_no_delete   BEFORE DELETE   ON mc_simulation_run
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER mcsim_no_truncate BEFORE TRUNCATE ON mc_simulation_run
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();

-- M4 查詢效能（實查目前僅 PK 一個索引，540 列尚可但自進化會放大）
CREATE INDEX IF NOT EXISTS idx_mcsim_target_asof
    ON mc_simulation_run (target_id, asof_date, horizon_td, method);

-- M5【選配・須 Steward 另裁】方法白名單 CHECK → 註冊表 FK（H-17 之解）
-- ALTER TABLE mc_simulation_run DROP CONSTRAINT mc_simulation_run_method_check;
-- ALTER TABLE mc_simulation_run ADD  CONSTRAINT mc_simulation_run_method_fk
--     FOREIGN KEY (method) REFERENCES simulation_method_registry(method);
-- 前置：registry 須先 seed 完現行 20 值，否則 ADD FK 會失敗（540 列既有值須全部命中）
```
**M5 不預設執行**：它同時是「解 #29(b) 違反」與「移除一道已生效機械閘」的動作，屬 L6.18(b-1) 定義窄化敏感區，須人閘明裁。

## (a) 需讀取之既有表 — 實查真實欄位＋本計畫取什麼＋結果落哪

> 所有欄位皆以 `information_schema.columns` / `pg_constraint` 實查（2026-07-31，唯讀）。

### 1. `mc_simulation_run`（540 列；asof_date 全為 2026-05-31）
**實查全欄**：`run_id text NOT NULL｜target_id text NOT NULL｜asof_date date NOT NULL｜horizon_td integer NOT NULL｜method text NOT NULL｜block_len_td integer NULL｜n_paths integer NOT NULL｜seed integer NOT NULL｜summary jsonb NOT NULL｜is_simulation boolean NOT NULL｜git_sha text NOT NULL｜created_at timestamptz NOT NULL`
**實查約束**：`PK(run_id)`／`CHECK (is_simulation)`／`method` 20 值 CHECK／**非內部 trigger 數＝0**／唯一索引僅 PK。
**取什麼**：`summary` 內之分位錐（`p5/p25/p50/p75/p95`，由 `simulate_mc_paths.py:36 PCTS=(5,25,50,75,95)`）＋`target_id/asof_date/horizon_td/method/seed/n_paths`。
**落哪**：`sim_run_link`（掛軸）→ `sim_realized_outcome`（配實現值）→ `sim_calibration_eval`（校準讀數）。
**本計畫不改其寫入路徑**，僅新增 M3/M4 之 guard 與索引。

### 2. `TaiwanStockPriceAdj`（11,187,891 列；1992-01-04 ~ 2026-07-30）
**實查時點欄**：僅 `date date`（**無公告日欄**）。
**取什麼**：`(stock_id, date, close)` — (i) 模擬輸入之 ≤as-of 歷史對數報酬（`simulate_mc_paths.py:33 HIST_WINDOW_TD=756`）；(ii) label 日之實現收盤。
**落哪**：`sim_realized_outcome.realized_close/realized_logret`。
**紀律**：讀取一律經單一 reader 函式（F1 落日債換插點）；label 日以已實現交易日曆推算，仿 `settle_arena_labels.py`（`UNSETTLE_GAP_DAYS=30`、`FACTOR_TOL=0.005`）。

### 3. `evolution_prereg_gate`（1 列 = V2-SUNSET）
**實查全欄**：`gate_id text NOT NULL｜axis text NOT NULL｜purpose text NOT NULL｜criteria jsonb NOT NULL｜criteria_sha text NOT NULL｜status text NOT NULL｜preregistered_at timestamptz NOT NULL｜approved_by text｜approved_at timestamptz｜git_sha text｜evaluated_at timestamptz｜result_snapshot jsonb｜evaluation_ref text｜note text`
**實查約束**：`PK(gate_id)`／`axis CHECK IN ('tw','lai','raw','program')`／`status CHECK IN ('preregistered','approved','evaluated_pass','evaluated_fail','superseded')`／trigger `prereg_gate_no_goalpost`（實查函式原文：DELETE 拒、終態不可改、**`criteria_sha` 不可改**）。
**取什麼**：`criteria`（凍結判準：地板臂顯著超越門檻、`min_clusters`、`terminal_tier='statistical'`）＋`criteria_sha`（評估前覆算，不符即拒）。
**落哪**：評估後由 `evaluate_sim_prereg_gate.py` 寫回同表 `status/result_snapshot/evaluated_at`。**需 M1 遷移**否則 axis='sim' 寫不進。

### 4. `evolution_kill_switch`（4 列，global/tw/lai/raw 全 clear）
**實查全欄**：`switch_id smallint NOT NULL｜state varchar NOT NULL｜set_at timestamptz NOT NULL｜set_by varchar NOT NULL｜reason text｜scope text NOT NULL`
**取什麼**：開輪前查 `scope IN ('sim','global')`，任一 `halt` 即停（OR、fail-safe，仿 `set_evolution_kill_switch.py:37 _env_halt()`）。
**落哪**：不寫（除 P0 一次性 seed 一列 scope='sim'，屬人閘動作）。

### 5. `evolution_deferred_work`（4 列，`cleared_at` 全 NULL）
**實查全欄**：`defer_id bigint NOT NULL｜axis text NOT NULL｜step_key text NOT NULL｜requested_at timestamptz NOT NULL｜reason text NOT NULL｜cleared_at timestamptz｜cleared_by text｜detail jsonb NOT NULL`
**取什麼**：無（只寫）。**落哪**：搶不到 `HeavySlot` 時寫一列 `axis='sim'`（不 silent skip）。

### 6. `evolution_evidence_run`（4 列，全 tw 軸 2026-07-27）
**實查全欄**：`evidence_id bigint｜axis text｜suite_id text｜code_hash text｜arm text｜metric_name text｜metric_value double precision｜n_items integer｜n_valid integer｜n_excluded integer｜is_invalid boolean｜n_trials integer｜selection_scope text｜detail jsonb｜created_at timestamptz`
**實查約束**：`UNIQUE(axis,suite_id,code_hash,arm,metric_name)`／`axis CHECK IN ('tw','raw')`／`arm CHECK IN ('ceiling','floor','shuffled','mismatched','live')`。
**取什麼**：無。**落哪**：`sim_calibration_eval` 之摘要以 `axis='sim'` 併寫此表（跨軸統一證據帳）。**需 M2 遷移**。

### 7. `governance_proposal`（3 列）
**實查全欄**：`proposal_id text NOT NULL｜kind text NOT NULL｜title text NOT NULL｜diff_text text NOT NULL｜evidence_refs jsonb NOT NULL｜proposed_by text NOT NULL｜status text NOT NULL｜decided_by text｜decided_at timestamptz｜decision_note text｜created_at timestamptz NOT NULL`
**取什麼**：晉升/註冊列之 `gate_ref` FK 目標（人閘偵測配套，報告書 :147）。
**落哪**：不寫（提案由 `scripts/governance_queue.py` 既有 CLI 落）。

### 8. `risk_policy`（6 列）
**實查全欄**：`horizon integer NOT NULL｜policy_key text NOT NULL｜threshold double precision NOT NULL｜action text NOT NULL｜source_ref text NOT NULL｜note text｜updated_at timestamptz NOT NULL`
**取什麼**：`threshold`（H60 dd_circuit −0.2、H120 −0.25 等）作為模擬摘要之比對閾值。
**落哪**：**不寫回**（單向唯讀，`simulate_portfolio_risk.py:11` 明文）；驗收哨兵須斷言本表列數與 `updated_at` 未變。

### 9. `evolution_hypothesis_hint`（10 列，全 approved）
**實查 trigger**：`hint_decision_forward_only`（UPDATE 單向）＋`hint_no_delete`／`hint_no_truncate`（`honesty_delete_only_guard`）。
**取什麼**：跨軸樣板（本計畫之 forward-only guard 照抄其函式寫法）。
**落哪**：模擬軸之跨軸回流以本表 `from_axis='sim'` 落（**不新建跨軸表**）——需確認其 `from_axis` 是否有 CHECK（見 unknowns U6）。

### 10. `direction_arena_candidate`（11 列）
**實查全欄**：`model_key text NOT NULL｜team text NOT NULL｜track text NOT NULL｜gate_eligible boolean NOT NULL｜spec jsonb NOT NULL｜code_sha text NOT NULL｜weights_hash text｜registry_model_id text｜frozen_at timestamptz NOT NULL｜status text NOT NULL｜retire_note text`
**取什麼**：僅作**設計範本**（凍結 spec／退役不刪之樣式）。
**落哪**：不讀不寫。**本計畫不新增 arena 參賽者**（見 out_of_scope）。

### 11. `local_model_eval_run` / `local_model_eval_item`（59 / 252 列）
**實查約束**：`local_model_eval_run` 僅 `PK(run_id)`（**arm 為自由文字、無 CHECK**）；`local_model_eval_item_layer_check` 為九值知識/語意題型 CHECK（**零市場格**）。
**取什麼**：對照臂方法論（ceiling/floor/mismatched/robot 五臂）與 `eval_code_hash` 換尺 fail-loud 之寫法。
**落哪**：不寫（模擬軸讀數落 `sim_calibration_eval`，**不混入本地 LLM 行為尺**）。

---

## 四、(b) python 程式規畫

## (b) Python 程式規畫（檔·角色·簽名·輸入表→輸出表）

> 全部須守 CLAUDE #18/#29：白話 docstring＋「守原則 #X」一行＋**執行指令矩陣**＋`--selftest`（零 DB 零 API）＋無參數 graceful；`import _bootstrap` 先於 `import augur`。

### 【新建・library（`src/augur/simulation/`，新 package）】

**1. `src/augur/simulation/calibration.py` — 角色：純函式量尺（零 IO）**
本計畫的統計級終審核心。`grep` 實證全 repo 無 pinball/CRPS 實作，故為全新。
```python
def coverage_rate(lows: Sequence[float], highs: Sequence[float],
                  realized: Sequence[float]) -> float
def pinball_loss(quantile: float, q_hat: Sequence[float],
                 realized: Sequence[float]) -> float
def crps_from_quantiles(levels: Sequence[float], q_hat: Sequence[Sequence[float]],
                        realized: Sequence[float]) -> float
def pit_values(levels: Sequence[float], q_hat: Sequence[Sequence[float]],
               realized: Sequence[float]) -> list[float]
def pit_ks(pit: Sequence[float]) -> tuple[float, float]      # (D 統計量, p)；scipy 1.18.0 實查在
def summarize(levels, q_hat, realized) -> dict               # 一次回全部讀數
def _selftest() -> int                                        # 已知分布之解析解回歸鎖
```
**輸入表**：無（純函式）。**輸出表**：無。

**2. `src/augur/simulation/candidate.py` — 角色：候選正規化＋合法性強制（零 IO）**
H-2/H-3 的 code 級落地：spec 白名單，任何帶預測 tilt、帶財報條件、帶未來窗之鍵一律 reject。
```python
ALLOWED_KEYS: frozenset[str]        # {method, block_len_td, hist_window_td, n_paths, seed, horizon_td}
FORBIDDEN_KEY_PATTERNS: tuple[str, ...]   # ('tilt','drift','forecast','target_ret','pred','label',...)
def canonical_spec(spec: dict) -> dict            # 排序+型別正規化
def spec_sha(spec: dict) -> str                   # sha256(canonical json)
def candidate_id(spec: dict) -> str               # 'simc_'+spec_sha[:12]
def validate_spec(spec: dict, *, param_schema: dict) -> tuple[bool, str|None]
def _selftest() -> int                            # 斷言 tilt 型 spec 必被拒
```

**3. `src/augur/simulation/eval_contract.py` — 角色：判準凍結與換尺偵測（零 IO）**
```python
def eval_code_hash(paths: Sequence[str]) -> str        # 含 calibration.py 全文＋量尺常數
def criteria_sha(criteria: dict) -> str
def verify_frozen(criteria: dict, criteria_sha_db: str) -> None   # 不符 raise（H-4 不符即拒）
def arms_required() -> tuple[str, ...]                 # ('live','ceiling','floor','mismatched','robot')
def floor_beaten(live: dict, floor: dict, *, margin: float) -> bool   # H-6
def _selftest() -> int
```

### 【新建・scripts】

**4. `scripts/migrate_sim_evolution_ddl.py` — 角色：建表／遷移**
```python
def status() -> int              # 無參數:唯讀印現行約束與缺表清單
def apply(dry: bool) -> int      # 建 8 新表 + M1..M4；M5 需額外 --allow-method-fk
def _current_checks(cur) -> dict
def _selftest() -> int
```
輸入表：`information_schema` / `pg_constraint`。輸出：DDL（8 新表＋4 遷移）。

**5. `scripts/register_simulation_method.py` — 角色：人閘 CLI（方法採用）**
```python
def list_methods() -> int
def seed_from_check(dry: bool) -> int        # 一次性把現行 20 值 CHECK 遷入 registry（bootstrap）
def register(method: str, family: str, param_schema_file: str, gate_ref: str) -> int
def retire(method: str, note: str) -> int
def _require_tty() -> None                   # 仿 review_evolution_candidates.py:48（禁管道/AI 代裁）
```
**紀律**：**不設 `--approved-by` 旗標**；`approved_by` 由互動式 TTY 由 hugo 自行輸入（H-8）。
輸入表：`mc_simulation_run`（seed 用）。輸出表：`simulation_method_registry`。

**6. `scripts/propose_simulation_candidates.py` — 角色：候選產生（LLM，本地）**
```python
OLLAMA = "http://127.0.0.1:11434/api/generate"     # 實查 :11434 在跑
MODEL  = "qwen3:4b"                                 # 實查 OLLAMA_MAX_LOADED_MODELS=1
MAX_CALLS_PER_RUN = 40                              # #28 配額護欄（日預算 ≈300-380 次）
def _ask(prompt: str, *, timeout: int = 150) -> tuple[str, int]
def propose(iteration_uid: str, n: int, dry: bool) -> int
def grid_fallback(n: int) -> list[dict]             # LLM 不可用時之零-LLM 後路
def status() -> int
def _selftest() -> int                              # 離線:餵固定字串驗 parse+reject 路徑
```
**紀律**：flock `/tmp/augur_llm.lock`（**不搶、`-n` 搶不到即走 grid_fallback**）；每次呼叫落 `sim_llm_proposal`（含 raw_output 與 reject_reason，parse 失敗**不重試風暴**）。
輸入表：`simulation_method_registry`、`sim_evolution_candidate`（去重）。輸出表：`sim_llm_proposal`、`sim_evolution_candidate`。

**7. `scripts/score_simulation_calibration.py` — 角色：消費／評分（**本軸主力，零 LLM**）**
```python
def link_runs(iteration_uid: str, gate_id: str, dry: bool) -> int
def settle(asof_until: date, dry: bool) -> int          # 配實現值(三態 normal/last_trade/unsettleable)
def score(gate_id: str, arms: Sequence[str], dry: bool) -> int
def _quantiles_from_summary(summary: dict) -> tuple[list[float], list[float]]
def _arm_synthetic(arm: str, real: Sequence[float]) -> Sequence[float]   # ceiling/floor/mismatched/robot
def status() -> int
def _selftest() -> int
```
輸入表：`mc_simulation_run`、`sim_run_link`、`TaiwanStockPriceAdj`、`evolution_prereg_gate`。
輸出表：`sim_realized_outcome`、`sim_calibration_eval`、`evolution_evidence_run(axis='sim')`。

**8. `scripts/evaluate_sim_prereg_gate.py` — 角色：機械裁判（只讀 criteria、不改 criteria）**
```python
def _guards(cur, gate_id: str) -> dict       # status 須 approved；criteria_sha 覆算不符即拒(H-4)
def evaluate(gate_id: str) -> int
def check(gate_id: str) -> int               # 唯讀預演
def _verdict(live: dict, arms: dict, criteria: dict) -> tuple[str, dict]
def status() -> int
def _selftest() -> int
```
輸入表：`sim_calibration_eval`、`evolution_prereg_gate`。
輸出表：`evolution_prereg_gate`（status/result_snapshot/evaluated_at）、`sim_evolution_verdict`（`verdict='killed'` 或 `'undecidable'`；**`'promoted'` 不由本程式寫**）。

**9. `scripts/promote_simulation_candidate.py` — 角色：人閘晉升（TTY only）**
```python
def _require_tty() -> None
def show(candidate_id: str) -> int           # 印全部證據列供 hugo 過目
def promote(candidate_id: str, gate_proposal_ref: str) -> int
```
**紀律**：無 `--decided-by` 旗標；`decided_by` 互動輸入；`gate_proposal_ref` 必填且 FK 檢核（H-8）。
輸入表：`sim_calibration_eval`、`sim_evolution_verdict`、`governance_proposal`。輸出表：`sim_evolution_verdict`（verdict='promoted'）。

**10. `scripts/run_sim_evolution_iteration.py` — 角色：driver（S0–S6）**
```python
STEPS = ("S0_open","S1_propose","S2_simulate","S3_settle","S4_score","S5_gate","S6_close")
TRIGGER_CODE = "SIMEVO-S1-go"
RC_SLOT_BUSY = 75
def open_round(dry: bool) -> str
def _do_step(cur, uid: str, step: str, dry: bool) -> dict
def run_round(steps: Sequence[str], dry: bool) -> int
def close_round(uid: str, dry: bool) -> int
def status() -> int
def _selftest() -> int    # 含「零代簽」斷言:程式體不得出現 promoted_by/decided_by/approved_by 字面
```
**紀律**：開輪查 `evolution_kill_switch` scope IN ('sim','global')；重活經 `HeavySlot("sim_evolution")`，搶不到寫 `evolution_deferred_work` 並 rc=75。
輸入表：上列全部。輸出表：`sim_evolution_iteration_ledger`。

**11. `scripts/verify_sim_evolution_acceptance.py` — 角色：強制／驗收哨兵（唯讀）**
```python
def check_all() -> int     # A1..A8，任一紅即 exit≠0
```
斷言：(A1) 每列 `sim_evolution_verdict.verdict='promoted'` 皆有 `decided_by`＋`gate_proposal_ref`；(A2) 每個 gate 評估輪皆有 floor＋ceiling＋mismatched＋robot 四臂列；(A3) `risk_policy` 列數與 `updated_at` 未變；(A4) `mc_simulation_run` 全列 `is_simulation=true`；(A5) 無任何 `sim_evolution_candidate.spec` 含禁用鍵；(A6) `criteria_sha` 與 criteria 覆算一致；(A7) `sim_realized_outcome.label_date > asof_date` 全成立；(A8) `sim_llm_proposal` 全列 `is_synthetic=true`。

### 【改造既有・附現行檔:行號】

**12. `scripts/simulate_mc_paths.py`（改造）**
現行：`FREEZE = "2026-05-31"`(:31)、`DEFAULT_HORIZONS=(21,42,63,126)`(:32)、`HIST_WINDOW_TD=756`(:33)、`BLOCK_LEN=21`(:34)、`PCTS=(5,25,50,75,95)`(:36)、`run(stocks, asof, horizons, n_paths, seed, window)`(:136)、`status()`(:166)、`main()`(:178)。
改造點：(i) 新增 `run_from_candidate(candidate_id: str, asof: date, targets: Sequence[str], dry: bool) -> int`，參數由 `sim_evolution_candidate.spec` 取代 CLI 硬帶；(ii) `method` 合法性改查 `simulation_method_registry`（先於 DB CHECK 之友善拒絕）；(iii) **不動四鎖、不動 `DISCLAIMER`(:36)、不新增逐路徑落地**。

**13. `src/augur/philosophy/evolution.py`（改造）**
現行：`KILL_SCOPES = ('tw','lai','raw','global')`(:242)、`effective_kill_state(states, *, env_halt=False)`(:245)、`normalize_kill_state(...)`(:232)。
改造點：`KILL_SCOPES` 加 `'sim'`；`_selftest` 補一格。

**14. `scripts/set_evolution_kill_switch.py`（改造）**
現行：`set_state(state, *, scope, by, reason)`(:83)、`_env_halt()`(:37)。
改造點：scope 參數說明加 `sim`；P0 由 hugo 親跑 seed 一列。

**15. `scripts/report_triple_evolution_week.py`（改造）**
現行：`:152-153` 查 serving 無 promoted_by。
改造點：加第四軸區塊——列出本週所有 `sim_evolution_verdict` 宣稱人簽之列供掃視認領（報告書 :147 之偵測配套）。

**16. `src/augur/core/heavy_slot.py`（不改，僅接線）**
現行：`LOCK_NAME = "augur_evolution_heavy_slot"`(:25)、`HeavySlot(owner, lock_name).acquire()/verify()/release()/defer()`。
接線：`run_sim_evolution_iteration.py` 以 `HeavySlot("sim_evolution")` 取車道；**不得用 `db.connect()`**（其 finally 會靜默放鎖，檔頭已警示）。

**17. `scripts/check_cmd_matrix.py`（既有稽核，不改）**
新增之 11 支程式一律須在首次提交當下通過（CLAUDE #18 v1.30 向前生效義務）。

---

## 五、元件與端點

## 元件與端點

### 現有服務實況（`systemctl --user` 實查）
| unit | port | 現況 | 與本計畫關係 |
|---|---|---|---|
| `augur-probability.service` | :8600 | running；`serve_probability_ui.py` GET `/`、`/simulate?stock=&h=`、`/direction`；POST 僅 `/login`；**零 approve/promote/trade/ingest 端點** | 唯一可能呈現模擬結果之處 |
| `augur-ollama.service` | :11434 | running；`OLLAMA_MAX_LOADED_MODELS=1`；三模型 qwen3:4b / qwen3:8b / nomic-embed-text | 候選產生器唯一 LLM 來源（本機，H-11） |
| `augur-advisor` | :8399 | — | **本計畫不接**（模擬數字不入對話層，四鎖第③） |
| `augur-chat` | :8090 | activating auto-restart（實查，疑 crash loop） | **本計畫不接** |
| `augur-admin` | :8500 | activating auto-restart（實查） | **本計畫不接** |

### 本計畫之端點決定
**不新增任何 HTTP 端點。** 理由與契約：
1. **零寫入端點**：晉升／人簽一律走 TTY CLI（`promote_simulation_candidate.py`），不開 web approve——否則等同把人閘搬到一個 AI 也能 POST 的地方（H-8）。
2. **:8600 `/simulate` 若要顯示新方法之錐**：契約不變——(i) `DISCLAIMER`「模擬非預測」與數字同一 DOM 節點硬綁；(ii) 只讀 `mc_simulation_run.summary`，不讀 `sim_calibration_eval`（校準讀數屬 review 級，不對外）；(iii) 伺服端確定性渲染，**NOT LLM**。此為**選配**，非本計畫必要交付。
3. **內部介面**＝`HeavySlot("sim_evolution")`（PG advisory lock `augur_evolution_heavy_slot`）＋`flock /tmp/augur_llm.lock`（LLM 車道）。兩者皆為既有機制，不新增鎖。
4. **排程契約**（cron，白天窗；理由見 phases P0）：
   - `10 8 * * 1-5  run_sim_evolution_iteration.py --run`（08:10，避開 01:30 演化鏈、04:15/10:15 evolve_cycle、20:00 arena、23:00 TWEVO）
   - `0 7 * * 6     score_simulation_calibration.py --settle`（週六結算，錯開週六 09:00 RAWEVO）
   - **不掛 systemd timer**（本專案 evolution 側慣例在 crontab，實查）。

---

## 六、分階段與機械驗收

## 分階段（每階段：前置／產出／可機械驗收之判準）

---
### **P0 — 環境前置與車道確認（無 GPU、無微調棧）**
**前置**：無。
**產出**：環境事實表（寫入計畫書，不寫 DB）；`sim` kill-switch 種子列（**由 hugo 親跑**）；排程窗確認。
**驗收（機械）**：
```bash
# V0.1 微調棧確認為「不存在」——本計畫不得依賴（誠實記錄，非安裝）
/home/hugo/project/augur/venv/bin/pip list | grep -E "^(peft|trl|bitsandbytes|gguf) " ; echo "rc=$? (期望 1=無此四者)"
# V0.2 量尺依賴在位
/home/hugo/project/augur/venv/bin/python -c "import numpy,scipy,scipy.stats;print(numpy.__version__,scipy.__version__)"
# V0.3 無 GPU（誠實記錄）
command -v nvidia-smi ; echo "rc=$? (期望 1)"
# V0.4 LLM 車道可用且不搶佔
curl -s localhost:11434/api/tags | head -c 200
fuser /tmp/augur_llm.lock ; echo "rc=$?"
# V0.5 heavy_slot 現況（期望 0 列＝無人持有）
psql -Atc "select count(*) from pg_locks where locktype='advisory';"
```
```sql
-- V0.6 kill switch 種子（hugo 親跑；AI 不代寫 set_by）
SELECT scope, state, set_by FROM evolution_kill_switch ORDER BY scope;
-- 期望完成後含一列 scope='sim'
```
**阻塞項（須先解或明示接受）**：`evolution_deferred_work` 4 列 `cleared_at` 全 NULL、TWEVO 07-30 I3 `TimeoutExpired 7200s`——若不解，08:10 白天窗仍可能與殘留重活相撞。驗收：
```sql
SELECT defer_id, axis, step_key, requested_at, cleared_at FROM evolution_deferred_work ORDER BY defer_id;
```

---
### **P1 — 治權專章與判準凍結（**判準必須先於資料**，H-4）**
**前置**：P0。
**產出**：(i) 模擬方法／自進化元件之**專章五節點門檻**文字（含「**本軸終審＝統計級（校準檢定），非實效級 #14 經濟終關**」之明文宣告，A3）；(ii) `governance_proposal` 一列（kind='criteria_change'，由 `scripts/governance_queue.py --submit`）；(iii) hugo 人簽 approve→enact。
**驗收（機械）**：
```sql
SELECT proposal_id, kind, status, decided_by, decided_at FROM governance_proposal
 WHERE title LIKE '%模擬%' ORDER BY created_at DESC LIMIT 3;   -- 期望 status='enacted' 且 decided_by 非 NULL
```
**紀律**：本階段**不得**提出任何降低 OCV 之條款（L6.19／H-9）；提案由 AI 草擬、**由 hugo 決議**。

---
### **P2 — 表與遷移（DDL）**
**前置**：P1 enacted。
**產出**：8 新表＋M1–M4 遷移；M5 不執行。
**驗收（機械）**：
```sql
-- V2.1 八表俱在
SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN
 ('simulation_method_registry','sim_evolution_candidate','sim_run_link','sim_realized_outcome',
  'sim_calibration_eval','sim_evolution_verdict','sim_llm_proposal','sim_evolution_iteration_ledger');
-- 期望 8
-- V2.2 append-only guard 已掛（含既有 mc_simulation_run）
SELECT c.relname, count(*) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
 WHERE NOT t.tgisinternal AND c.relname IN ('mc_simulation_run','sim_evolution_verdict','sim_calibration_eval')
 GROUP BY 1;   -- 期望 mc_simulation_run >= 2（現況實查為 0）
-- V2.3 axis CHECK 已擴
SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='evolution_prereg_gate_axis_check';
-- 期望字串含 'sim'
-- V2.4 反挪門柱 guard 有效（唯讀驗證方式：讀函式定義，不實測破壞）
SELECT proname FROM pg_proc WHERE proname IN ('prereg_gate_no_goalpost','sim_candidate_forward_only');
```
```bash
# V2.5 method registry 已 seed 完現行 20 值（否則未來 M5 加 FK 必失敗）
psql -Atc "select count(*) from simulation_method_registry;"   # 期望 >= 20
psql -Atc "select count(distinct method) from mc_simulation_run m
           where not exists (select 1 from simulation_method_registry r where r.method=m.method);"  # 期望 0
```

---
### **P3 — 量尺先於候選（三臂鐵律，H-6）**
**前置**：P2。
**產出**：`calibration.py`＋`eval_contract.py`＋`score_simulation_calibration.py`；一列 `evolution_prereg_gate`（axis='sim'，criteria 含地板臂 margin、min_runs、terminal_tier='statistical'），**hugo 人簽 approved 後才進 P4**。
**驗收（機械）**：
```bash
/home/hugo/project/augur/venv/bin/python -m augur.simulation.calibration --selftest   # rc=0
/home/hugo/project/augur/venv/bin/python -m augur.simulation.eval_contract --selftest # rc=0
python3 /home/hugo/project/augur/scripts/check_cmd_matrix.py                            # rc=0
```
```sql
-- V3.1 gate 已凍且人簽
SELECT gate_id, axis, status, approved_by, approved_at, criteria_sha
  FROM evolution_prereg_gate WHERE axis='sim';         -- 期望 status='approved'、approved_by 非 NULL
-- V3.2 四對照臂已有讀數（在任何 live 臂之前）
SELECT arm, count(*) FROM sim_calibration_eval GROUP BY 1 ORDER BY 1;
-- 期望 ceiling/floor/mismatched/robot 皆 >=1
-- V3.3 地板臂尚未被超越時不得有任何 promoted
SELECT count(*) FROM sim_evolution_verdict WHERE verdict='promoted';   -- 本階段期望 0
```
**停止條件**：若 `robot` 或 `floor` 臂讀數與 `live` 臂無顯著差距 → **該量尺判為缺陷、不得作能力宣稱**，退回改尺（換尺＝新 gate_id、舊列 superseded，H-5）。

---
### **P4 — 候選產生與一輪閉環（無晉升）**
**前置**：P3 gate approved。
**產出**：`candidate.py`、`propose_simulation_candidates.py`、`run_sim_evolution_iteration.py`；第一輪 `sim-YYYYMMDD-r01`。
**驗收（機械）**：
```sql
-- V4.1 一輪已閉且未 APPLY
SELECT iteration_uid, status, apply_allowed, gain_basis, closed_at
  FROM sim_evolution_iteration_ledger ORDER BY iteration_id DESC LIMIT 3;  -- 期望 apply_allowed=false
-- V4.2 LLM 產物全帶 synthetic 標記
SELECT count(*) FROM sim_llm_proposal WHERE is_synthetic IS NOT TRUE;      -- 期望 0
-- V4.3 無任何候選帶禁用鍵（H-2/H-3）
SELECT candidate_id FROM sim_evolution_candidate
 WHERE spec::text ~* '(tilt|drift|forecast|target_ret|label)';             -- 期望 0 列
-- V4.4 as-of 前視零違規
SELECT count(*) FROM sim_realized_outcome WHERE label_date <= asof_date;   -- 期望 0
-- V4.5 配額未爆
SELECT count(*) FROM sim_llm_proposal WHERE created_at::date = current_date;  -- 期望 <= 40/輪
```
```bash
python3 /home/hugo/project/augur/scripts/verify_sim_evolution_acceptance.py   # rc=0
```

---
### **P5 — 裁判與判死留檔**
**前置**：P4 至少 N 輪（N 由 P3 gate criteria 之 `min_runs` 定，**不在此處拍腦袋**）。
**產出**：`evaluate_sim_prereg_gate.py`；`sim_evolution_verdict` 首批 `killed`／`undecidable` 列。
**驗收（機械）**：
```sql
-- V5.1 gate 已評估且 criteria_sha 未變（未挪門柱）
SELECT gate_id, status, evaluated_at, criteria_sha FROM evolution_prereg_gate WHERE axis='sim';
-- V5.2 判死留檔存在且證據非空
SELECT verdict, count(*), min(array_length(evidence_eval_ids,1)) FROM sim_evolution_verdict GROUP BY 1;
-- V5.3 判死不可刪（唯讀驗證：guard 已掛）
SELECT count(*) FROM pg_trigger WHERE tgrelid='sim_evolution_verdict'::regclass AND NOT tgisinternal;  -- >=3
-- V5.4 樣本不足時誠實 undecidable，不得 fail 充數
SELECT verdict, (basis->>'reason') FROM sim_evolution_verdict WHERE verdict='undecidable';
```

---
### **P6 — 人閘晉升與風險畫像消費**
**前置**：P5 有候選達 gate 門檻。
**產出**：`promote_simulation_candidate.py`；`governance_proposal` 一列＋hugo 親簽；週報第四軸。
**驗收（機械）**：
```sql
-- V6.1 每列 promoted 皆帶人簽與提案指標
SELECT verdict_id, candidate_id, decided_by, decided_at, gate_proposal_ref
  FROM sim_evolution_verdict WHERE verdict='promoted';    -- 三欄皆不得 NULL（CHECK 已保證）
-- V6.2 CLI 未代打（全 repo 靜態驗）
-- bash: grep -n "decided_by\|approved_by\|promoted_by" scripts/promote_simulation_candidate.py
--       期望僅出現在 SQL 欄名與互動輸入，無任何 argparse 旗標
-- V6.3 risk_policy 未被回寫（H-3/F3）
SELECT policy_key, horizon, threshold, updated_at FROM risk_policy ORDER BY 1,2;
-- 期望與 P0 快照逐欄相同
-- V6.4 產物仍全為模擬
SELECT count(*) FROM mc_simulation_run WHERE is_simulation IS NOT TRUE;   -- 期望 0
```

---
### **P7 —（選配・預設不做）權重級自進化**
**前置（缺一即 no-go，實查 2026-07-31）**：venv 無 `peft`/`trl`/`gguf`；`nvidia-smi` 不存在；`available` RAM 806 MiB、`llama-server` RSS 5.1 GB；`local_model_version.lora_path` 4 列全 NULL。
**若未來要做，最小前置清單**：`pip install peft trl gguf` → import smoke → llama.cpp `convert_lora_to_gguf` 工具鏈 → 解 heavy_slot 車道爭用 → 重估 RAM。
**本計畫立場**：**列為明確不做**（見 out_of_scope），僅保留 `local_model_version` 既有欄位不動。

---

## 七、明確不做

## 明確不做（範圍外；避免計畫膨脹）

1. **權重級微調（LoRA/QLoRA/全量）** — 本機實查無 `peft`/`trl`/`bitsandbytes`/`gguf`、無 GPU、`available` RAM 806 MiB。本計畫**不安裝、不試跑**；`local_model_version.lora_path` 維持 NULL。（列為 P7 選配前置清單，非交付）
2. **把模擬改造成 RL 訓練環境**（step/action/reward 介面、逐路徑落地） — 直接撞 H-1 與四鎖第②條「絕不存逐路徑」，須先修憲，不在本計畫。
3. **新增 arena 參賽者／讓自進化推出新隊伍** — 需同改 `adapters.py` REGISTRY（自測硬斷言 `len(REGISTRY)==10`）＋`register_arena_candidate.py` DEFAULTS(:37-88)＋DB trigger `arena_candidate_frozen`。屬行走者⑥，另案。
4. **讓 LLM 產出市場方向預測** — 現況實查零此路徑；且方向軸 v1/v2 家族全 `evaluated_fail`、no-v3 已入憲。本計畫之 LLM 角色**僅限提模擬參數候選**。
5. **修 TWEVO 23:00 卡輪／清 `evolution_deferred_work` 積壓** — 是本計畫的排程前置（P0 阻塞項），但修復本身屬既有軸維運，另案。
6. **接通 KH10 `approved_for_loop` 的下游消費／補寫 `knowhow_evolution_feedback`** — lens 2 之 G1/G2，屬行走者①，另案。
7. **為 `knowhow_governance_ledger` 補 DB 級 append-only guard** — lens 2 之 G3（全庫誠實帳本體系唯一破口），應補但屬 KH10 軸，另案（本計畫僅在缺口表誠實登記）。
8. **建 World Concept Registry** — 落日 2026-10-14 之正解，但屬 L1 表徵層工程，另案；本計畫只做「單一 reader 函式」的換插點準備。
9. **`mc_simulation_run.method` CHECK → FK 之切換（M5）** — DDL 已備妥但**不預設執行**，須 Steward 另裁（同時涉「解 #29(b) 違反」與「移除既生效機械閘」）。
10. **`prediction_probability` / `direction_probability` 等產品輸出表之任何變更** — 模擬數字不入產品層、不入 chat payload（四鎖第③）。
11. **重跑或擴充 arena replay（4,783,375 列）／meta replay** — 屬行走者⑥⑦既有工程。
12. **新增任何 HTTP 端點或修改 advisor/chat/admin** — 見 endpoints；人閘一律 TTY CLI。
13. **修改凍結評測集 `4183475c5089`／`4e15a143ff4b` 或 `local_model_eval_item_layer_check`** — 模擬軸自有量尺，**不混入本地 LLM 行為尺**（避免一尺量兩事）。

---

## 八、未知與風險（誠實登記，不以推測填補）

## 未知與風險（誠實登記；不以推測填補）

**U1【條號不一致・已呈但未裁】** 報告書 :128 稱治權空懸者為「④與⑤」；憲章 v1.50.0 修訂記錄 `:428` 與治權計畫書 §九 P1 導言稱「④與⑦」；§九 P5 又回到「④與⑤」。三處記載不一致。本計畫涉④⑤⑦三者故不影響設計，但**須併陳 Steward**。

**U2【報告書自身已被追過】** 報告書 §四「誠實標注」稱 ④⑤ 在治權層無明文——但憲章 v1.50.0（同日 2026-07-30 拍板）已成文涵蓋「能力宣稱」與「方法採用（模擬法、估計法）」。**計畫書不得建立在「法源真空」之假設上**；報告書該段須降級／更新（屬報告書側，非治權檔）。

**U3【模擬方法「四法一輪結案」之判死列查無載體】** 報告書所稱「四法一輪結案（天真法把尾巴低估一個數量級）」——DB 中查無任何模擬方法之 verdict 表或列。**該結案可能僅存於報告文字**。若是，則行走者⑤之「判死留檔」節點在本計畫之前**從未存在過載體**（這正是新建 `sim_evolution_verdict` 的理由），但**我無法證實該結案的原始數據落在何處**。

**U4【`evolution_hypothesis_hint.from_axis` 是否有 CHECK 未查】** 本計畫規劃以 `from_axis='sim'` 走既有跨軸回流表，但**未查該欄是否有 CHECK 限定 axis 值**。若有，需一併加入 M2 遷移。**動工前必查**。

**U5【`direction_gate` 之 arena live 六門與 A4 二門 criteria 未展開】** 8 個 approved 未 evaluate 之門的評估觸發條件寫在 `criteria` jsonb 內，本輪未逐門讀。若其評估時程落在白天窗，會與 08:10 之 sim 輪搶 heavy_slot。

**U6【23:00 heavy_slot 的持有者查不到】** `evolution_deferred_work` 記 07-28/07-29「heavy slot busy」，但 `pg_locks` 事後無法回溯持有者（實查現時 0 列 advisory lock）。**誰在 23:00 佔用車道是未解之謎**，直接影響 P0 排程窗之安全性。

**U7【各既有排程單次耗時多半未實測】** 已測：演化鏈 49–51 分（log 時戳）、arena pipeline ≈250 分（cron 起點＋mtime 推算，**該 log 無時戳故無法分段歸因**）、TWEVO I3 逾 7200s。**未測**：embed-catchup(03:30)、ata-advance(04:00，且該 service 實查為 **failed**)、admission-assist(05:00)、l2-deliberation(06:15)、evolve_cycle(*/6)、self_seek(*/6)。故「白天窗 ≈12.2 h」與「日預算 300–380 次 LLM」皆為**估算，非承諾**。

**U8【qwen3:8b 延遲未實測】** 只有 qwen3:4b + `format=json` 62–76 s 之給定實證。8b 之「150–190 次/日」係由參數量外推，**非實測**；且 8b(5.23 GB) 需先卸載 4b（`OLLAMA_MAX_LOADED_MODELS=1`），切換成本未量。

**U9【RAM 量測為單點快照】** `available 806 MiB`（2026-07-31 08:2x，當時 loadavg 29.96/12 核、llama-server RSS 5.1 GB）。**未取日間閒時基線**，故「新迴圈常駐 RSS < 1 GiB」偏保守，實際餘裕可能較大——但不得反向假設寬裕。

**U10【三個服務異常未查因】** `augur-ata-advance.service` = **failed**（timer 每日 04:00 觸發）；`augur-admin.service`、`augur-chat.service` = **activating auto-restart**（疑 crash loop）。**是否吃 CPU/RAM 未確認**，可能污染 P0 之窗口估算。

**U11【`freeze_manifest` 0 列】** 「凍結期快照留檔可複現」之帳本表建了卻從未寫入。若計畫書要主張本軸之 as-of 快照可複現，此為**應填未填之洞**——本計畫未規劃填它（範圍外），須誠實登記。

**U12【金融保險業財報 60 日 lag 未實作】** `src/augur/features/release_lag.py:19` 自陳缺口，`:34-35` 只有 45/90 兩檔。本計畫之模擬只吃日價故不觸發；**但若未來任何候選 spec 引入財報條件抽樣，此洞立即現形**——已在 `candidate.py` 之來源白名單擋住，惟該擋法為 code 級非 DB 級。

**U13【`sim_calibration_eval` 之 min_runs／margin 具體數值未定】** 這兩個門檻**必須由 Steward 在 P1/P3 凍結判準時拍板**，不得由 AI 事後依看到的資料選（否則即挪門柱）。本骨架刻意不填數字。

**U14【`local_model_eval_run.arm` 實查無 CHECK】** 該表 arm 為自由文字（僅 PK 約束），與 `evolution_evidence_run` 之 arm CHECK 不一致。本計畫新表採 CHECK 版；**兩表口徑不一致是既有事實**，未在本計畫解。

---

## 九、請 Steward 拍板（三件，其餘皆執行層）

1. **專章文字與終審定性**：模擬方法／自進化元件之五節點門檻，須明文宣告
   「**本軸終審＝統計級（校準檢定），非實效級 `#14` 經濟終關**」——依 v1.50.0 節點 2 括號，
   無經濟對價者得如此宣告，但**須載明其為統計級而非實效級**。缺此句即路徑空懸。
2. **`axis` 加 `'sim'` 之位階認定**：擴 CHECK 值域屬 patch 或重大判準修正？
   依 `GOVERNANCE-ANNEX v1.1` 第 2 條第 3 款，**patch 之性質認定屬 Steward 保留、Agent 不得自行認定**。
3. **是否接受「人簽為偵測而非預防」**：本機 `pg_roles` **無 `hugo` 角色**（我親驗），
   故 DB 無法區分人與 AI；`chk_*_signed` 類 CHECK 只能驗「欄位非空」，不能驗「填的人是人」。
   本書據此把人閘設計為**偵測級**（CHECK ＋ FK→`governance_proposal` ＋ CLI 不設人名旗標
   ＋ driver selftest 斷言程式體不含 `promoted_by/decided_by/approved_by` 字面）。
   **若要預防級，須先做角色分離**（另案、屬破壞性變更）。


---

## 十、我的獨立核驗記錄（哪些親驗、哪些照收）

本書之地基由四路平行 agent 蒐集（workflow `wf_f83dd3ac-471`）。**我未照單全收**，
就下列承重宣稱**逐項親驗**（唯讀 SQL，2026-07-31）：

| 宣稱 | 我的親驗結果 |
|---|---|
| `evolution_prereg_gate.axis` CHECK 無 `'sim'` | ✓ 實查＝`CHECK (axis = ANY (ARRAY['tw','lai','raw','program']))` |
| `mc_simulation_run` 零 trigger | ✓ 實查非內部 trigger 數＝**0** |
| `CHECK (is_simulation)` 存在 | ✓ 實查＝`CHECK (is_simulation)` |
| `pg_roles` 無 `hugo` | ✓ **無**——故人簽在本機為**偵測非預防** |
| `evolution_prereg_gate` 列數 | ✓ **1** 列 |
| `mc_simulation_run` 列數 | ✓ **540** 列 |

**未親驗、照收 agent 回報者**（讀者請以此為 PLAUSIBLE 級）：各既有排程之單次耗時、
`honesty_delete_only_guard()` 等 guard 函式之存在、`hint_decision_forward_only()` 之寫法、
以及 §八 U1–U10 各項。**動工前須逐項複驗**（U4 已明示「動工前必查」）。

---

## 十一、與既有文件之關係

- `reports/augur_self_evolution_execution_plan_20260730.md`（並行 session）＝**波次排程**，
  非本書之替代：實測其 `schema` 0 處、`CREATE TABLE` 0 處、`函式` 0 處、`簽名` 0 處，
  未達 #20 v1.39.0 之完整性；二者互補（該書排「何時做」，本書定「做什麼、怎麼驗」）。
- 本書**不涵蓋**深化理解報告（另件，`wbxikh6k9` 進行中）。
