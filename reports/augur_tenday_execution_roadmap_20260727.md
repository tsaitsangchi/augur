# augur 十天逐步執行路線圖（2026-07-27 → 08-06）

> **性質**：[I] 執行層路線圖（#20 計畫先行；hugo 2026-07-27 指示「列出逐步執行的計畫書」、範圍選「全專案十天路線圖」）。
> **上位不變**：v2 總控（三軸 SSOT）／`V2-AUTOADVANCE`（R1–R7 自動推進，ENACTED）／整合計畫七邊（`INTEG-P-yes`）／乙案兩機歸屬。本檔**只排序與拆步，不新增判準**；任何判準變更另案。
> **時鐘**：`V2-SUNSET` 期限 **2026-10-31（剩 96 天）**，現況 **0/3**。本路線圖的十天目標＝**把三條件中至少一條推到可判定**。

## 〇、讀法（三分鐘）

- 每步格式：**前置｜動作｜驗收（機械）｜停損｜執行者**。執行者只有兩種：**🤖 機器**（含排程與我）與 **🧑 hugo**（人閘／跨機／實體）。
- **🤖 步驟不需你出手**；🧑 步驟每項都標了「為何機器不能代」。
- 十天內**不新增自動化升級**（`TRI-CADENCE-yes` 維持未拍），R6 digest 為唯一新監督面。

## 一、狀態錨（2026-07-27 17:00 實查，非記憶）

| 軸 | 現況 |
|---|---|
| SUNSET | (a) arena 已結 4,128 但方向門 `evaluated_pass=0`（cluster **2/60**）｜(b) prodset active=**1**（今日 7 支反向除役）｜(c) LLM 臂有效列=**0**（跑中） |
| TWEVO | 尺已修（FAIL_SIGN＋對照臂偽陽率 9.0%/10.5%→GATE-raise p95=2.643）；driver 未寫 |
| LAIEVO | 凍結集＋四離線臂本機複現；LLM 臂跑中；RUBRIC v2 已拍待換尺 |
| RAWEVO | 本機 ledger 0 列（DESKTOP 有 3 輪待搬）；driver 在 |
| 平台 | chat/advisor/admin/probability live；ttai+rdai know-how 已入庫（檢索通、答題行為待進化） |
| 風險模擬 | 七法＋八情境齊（M1/M2/M3 今日收官） |
| 帳本 | qledger 1,175 題（真待辦 6）｜awaiting_hugo 142｜digest 週報上線 |

## 二、D1（07-27 今晚）：臂收尾＋arena 首夜

| # | 步驟 | 前置 | 驗收 | 停損 | 執行者 |
|---|---|---|---|---|---|
| 1.1 | LLM 臂三連發完成（grammar→behavior→pack） | — | `local_model_eval_run` ≥7 列、`is_invalid=false` | 若三臂皆 100% `done_reason=length` → 停手查 harness 不改判準 | 🤖 |
| 1.2 | 判準 A 判讀＋SUNSET(c) 半條閉合 | 1.1 | behavior `F@L1 > 0.167`（shuffled）且 >0 | 不過 → LAIEVO 退回 S0、誠實記「零訓練無增益」 | 🤖 |
| 1.3 | H2：`pack:pp_3ab2efebb04e` 證據呈報 | 1.1 | `evidence_level` 出爐（同尺可比） | — | 🤖 產證據／🧑 決定去留 |
| 1.4 | **arena 首夜**（20:00 出單／21:30 結算） | 排程 | `direction_arena_prediction` +1 pred_date；log 無 traceback | 資料未到＝誠實缺席 exit 0（已修 fail-loud） | 🤖 |

## 三、D2–D3（07-28～29）：RUBRIC 換尺＋8b 檔位

| # | 步驟 | 前置 | 驗收 | 停損 | 執行者 |
|---|---|---|---|---|---|
| 2.1 | `eval_local_model --model` 旗標 | 1.1 完成（跑時凍碼） | selftest 綠；`model` 欄落庫 | — | 🤖 |
| 2.2 | 8b 三臂（grammar/behavior/pack） | 2.1 | 三列 `model='qwen3:8b'`；跨 model 比較不觸 fail-loud | 單臂 >2h → 降 `--limit` 並標統計力 | 🤖 |
| 2.3 | **P-A 接線判定** | 2.2 | pack `evidence_level ≥ weak` 且 ≥grammar → 接線；否則**誠實不接**（預註冊之合法終局） | — | 🤖 判定／🧑 若接線則簽 `promoted_by` |
| 2.4 | **RUBRIC v2 換尺**（A 軸內容敏感＋跨域擴材） | 2.2/2.3（舊尺收尾） | 新尺：ceiling A=1.0、**shuffled A@L3/L4 由 0.967 崩落**、floor/mismatched 仍 0；新 `set_id` 凍結 | shuffled 未崩 → 子判準無效，重設計不硬上 | 🤖 |
| 2.5 | 跨域母體驗證 | 2.4 | 新集含 philosophy/ttai/rdai/raw catalog 四域題；L4 出現真實跨域歧義 | 任一題 live DB 不可查核 → 剔除不降判準 | 🤖 |

## 四、D3–D5（07-29～31）：TWEVO driver＋Phase 6 前置

| # | 步驟 | 前置 | 驗收 | 停損 | 執行者 |
|---|---|---|---|---|---|
| 3.1 | `heavy_slot.py` v2（pg advisory lock） | — | selftest 含「巢狀 `with connect()` 進出後鎖仍在」；搶不到寫 `evolution_deferred_work` | 掉鎖靜默 → fail-loud 不續跑 | 🤖 |
| 3.2 | `run_evolution_iteration.py`（TWEVO driver） | 3.1 | 一輪 I0–I8 寫 `evolution_iteration_ledger`；`steps_json` 每步含 rc/started/finished | 半套前進 → fail-closed 回滾 | 🤖 |
| 3.3 | `verify_evolution_acceptance.py`（A0–A12） | 3.2 | 12 條逐條 rc=0 或誠實標「腳本驗收非引擎裁決」 | — | 🤖 |
| 3.4 | RAWEVO 首輪（唯讀 R0–R3） | — | `raw_table_coverage_snapshot` ≥86 列；`feature_values`/prodset 零寫入（機械斷言） | 觸 API → 立即 halt | 🤖 |
| 3.5 | hint 批次呈報 | 3.4 | digest 列出 pending hints | — | 🤖 產／**🧑 `RAWEVO-HINT-approve`**（判準層，機器不得代） |

## 五、D5–D7（07-31～08-02）：整合七邊殘項

| # | 步驟 | 前置 | 驗收 | 執行者 |
|---|---|---|---|---|
| 4.1 | **P-B** probe 礦工（chat 拒答→L3/L4 候選） | 2.4 新 set_id | `advisor_probe_candidate` 落列；私有 session 零洩漏斷言；**僅入新 set_id** | 🤖 產候選／🧑 審核 approved_* |
| 4.2 | **P-D** admin digest 頁 | B3 已完 | GET 零寫入斷言；hint 批覆走同一 decision 路徑 | 🤖 |
| 4.3 | **F2** ttai 對帳 | — | `v_qdrant_export` 142,040 vs 知識層逐計數；差額列缺口帳 | 🤖 |
| 4.4 | **F3/G3** 方法論評估 | — | embed_cache 接入評估報告；T0–T4 權威分級之 `knowledge_source` 升級評估（**另案再落 DDL**） | 🤖 產評估／🧑 拍板是否落地 |
| 4.5 | qledger H2 解決器 | 車道空 | 6 題真待辦經 advisor 作答並回寫 `resolution_ref` | 🤖 |

## 六、D7–D10（08-02～06）：三軸開輪與週期化

| # | 步驟 | 前置 | 驗收 | 停損 | 執行者 |
|---|---|---|---|---|---|
| 5.1 | Phase 5 契約落地（hint/ledger/slot） | 跨軸邊有實料（arena settled ✓ 或 approved hint） | pytest「三表由同一常數清單生成」；`validate_evolution_contract --scan` rc=0 | 任一軸拒契約必要欄 → 停手不部分採納 | 🤖 |
| 5.2 | Phase 6 三軸開輪 | 5.1 | 三 ledger 各 ≥1 輪 `closed_at` 非空；停損計數啟動 | `gain=NULL`（不可比）**不計停損** | 🤖 |
| 5.3 | 首份 R6 digest 認領 | 週日 09:00 cron | hugo 掃視並回應 | **連 2 週無認領 → 自動降回逐案人閘**（R6 硬條款） | 🧑 |
| 5.4 | arena 週觀察 | 1.4 起每交易日 | cluster 由 2 增；計分板 Δ 欄持續誠實 | 出單連 3 日缺席 → 查資料鏈 | 🤖 |

## 七、🧑 hugo 專屬清單（全部，共 5 項）

| # | 事項 | 為何機器不能代 | 時機 |
|---|---|---|---|
| H-1 | DESKTOP runbook 兩步（貼公鑰／停其 arena+evolution 排程） | 跨機破壞性變更（#6）；停別台設定須人執行 | 它下次開機 |
| H-2 | `RAWEVO-HINT-approve <ids>` | 決定哪條假說進量化鏈＝判準層（H3） | D5 起每週一次 |
| H-3 | serving pack 晉升 `promoted_by`（若 P-A 接線） | P5.W2 憲章層 | D3 |
| H-4 | R6 digest 掃視認領 | 監督之實（否則規則簽淪為無人監督） | 每週日 |
| H-5 | H5 `volume_gini_60d` 回溯處置確認 | 已 APPLY 之生產狀態（R3 已自動 demote，確認即可） | 隨時 |

## 八、十天目標與誠實預期

**目標**：SUNSET 三條件**至少一條達成**。逐條機率評估（誠實、非樂觀）：

| 條件 | 十天內達成機率 | 理由 |
|---|---|---|
| (c) LAIEVO F@L1 | **最高** | 臂今晚出數；DESKTOP 曾得 0.933；本機四臂已逐位元複現＝複現路徑已通 |
| (a) arena 方向門 | 低 | cluster 2/60，每交易日 +1，十天約 +7 → 仍遠低於 60 |
| (b) prodset 成長 | 低 | 現 active=1；需新特徵過**升嚴後**門檻（\|hac_t\|≥2.643） |

**明確不做**（十天內）：解凍 API、降任何閘、`TRI-CADENCE-yes`、DCC、GitHub MCP、PAT 更換（已定案維持）、stock-backend 任何觸點。

**停損總則**：任一步連 2 輪驗收紅 → 該步 halt、不阻他步；`gain=NULL` 不計停損；所有停損後果須人裁。

## 九、執行進度（D1 當日實記，2026-07-27 18:30；只記已驗證者）

| 步 | 狀態 | 實證 |
|---|---|---|
| 3.1 heavy_slot v2 | ✅ | selftest 含巢狀 `with connect()` 回歸；**並修 `defer()` 死路**——原寫 `(axis,task,reason,payload)`，實表欄為 `(axis,step_key,reason,detail)`，UndefinedColumn 被 except 吞成一行 stderr → 「不 silent skip」的機制本身 silent skip（實測 0 列）。自測改為真插一列再刪 |
| 3.2 TWEVO driver | ✅ | `run_evolution_iteration.py` 十步齊；實跑 `tw-20260727-r01`：open→I4→`--close` **遭拒**（缺 9 步）→`--partial` 結成 `halted`。重活步因 llama-server 佔 5.8/12 核、可用記憶體 2GB 而延後，已落 `evolution_deferred_work` |
| 3.3 A0–A12 驗收器 | ✅ | `verify_evolution_acceptance.py`；今日三度演進 **PASS 8 → 11 → 12**、FAIL 0、N/A 1 |
| 3.4 RAWEVO 首輪 | ✅ | `raw-20260727-r01`：覆蓋快照 **97 表**（驗收 ≥86）、缺口分類 `ok 54/semantic_ok 19/freeze_gap 12/schema_gap 11/true_gap 1`、新 hint 10 則 pending。零寫入實查：prodset 仍 active=1、`feature_values` 未動 |
| 3.5 hint 批次呈報 | 🧑 待 | 10 則 pending 待 `RAWEVO-HINT-approve`（H-2） |
| 4.3 F2 ttai 對帳 | ✅ | 142,040 逐計數：五個假說被自己的資料否證後定位損失在 acquire 段；48 列走三層管線補灌並接至可檢索終態，**未解釋 0、rc=0**；ttai 全文覆蓋 141,825 → **141,873/141,873** |
| 5.1 Phase 5 契約落地 | ✅ | pytest 8 條（含 live DB 層）＋`validate_evolution_contract --scan` rc=0。寫測試時自撞兩個靜默 skip（env 變數名當旗標、`db.connect().__enter__()` 之 CM 被 GC）並修正 |

**尚待臂收尾者（Ollama 車道序列化）**：1.1 LLM 三臂 → 1.2 判準 A 判讀／SUNSET(c) → 2.1 `--model` 旗標（**跑中不得改碼**，會動 `eval_code_hash`）→ 2.2 8b 三臂 → 2.3 P-A 判定 → 2.4 RUBRIC v2 換尺；另 `eval_local_model` 應接 heavy_slot（現走 flock，driver 看不見臂在跑）。
