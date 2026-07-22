# 元憲章落地地圖（GROUNDING-MAP）[I]

- **快照日**：2026-07-17（生產庫資料至 2026-07-16——此值未附產生指令＝**未驗**，僅與審查現實錨定相符；本審禁連 DB 無法補跑）
- **性質**：資訊性 [I]。本文件不創設任何義務，權威悉依各 [N] 條款原文（AUGUR-MC v1.3、AUGUR-WM v1.0、AUGUR-ID v1.0、AUGUR-KS v1.0）。本文件不宣稱任何充任或生效；一切 apply／生效認定屬 Constitution Steward（MC §8.1）。
- **產生方法**：三路獨立盤點（義務官：憲章條文逐條抽出 44 項物理義務＋3 項程序性歸併；現實官：生產 schema 唯讀抽出物逐表比對；載具官：已寫成但未 apply 之 migration／程式盤點）之統整。衝突以現實官之 schema 行號證據為準。
- **證據紀律**：凡數字必附產生指令；凡「已存在」必附 schema 行證據；凡「不存在」必附 grep 零命中證明；不確定者明標「不確定」。**未採信任何文件自陳**（本專案已五度實證文件自陳不可信，含 ENVIRONMENT-SPEC 整份描述另一台機器、HANDOFF 鐵證數字全錯——凡引 HANDOFF/審計處均另附獨立實跑證據或明標未驗）。
- **抽出物**（唯讀，未連 DB；`$SP` ≡ `/tmp/claude-1001/-home-giga-augur/c804a0f7-f5fe-40c6-98ea-d200c3a65c0b/scratchpad`）：
  - `$SP/augur-schema.sql`（pg_dump 17.9 schema-only，17690 行：`wc -l` 實測）——下稱 `$S`
  - `$SP/augur-rowcounts.txt`（253 行＝253 表列數）
  - `$SP/augur-triggers.txt`（12 條 trigger 清單）
- **狀態圖例**：已落地✅｜載具已備🚚（程式/DDL 已寫成、生產 grep 零命中、未 apply）｜需新工🔨｜現況不可落地⛔｜純程序性📜（無 DB 落點）

---

## 一、現實基線（本機實測）

| 項 | 實測值 | 產生指令 |
|---|---|---|
| 平台 | WSL2 Linux 6.18.33.2-microsoft-standard-WSL2，x86_64 | `uname -m` |
| CPU | 12 核 | `nproc` → 12 |
| RAM | 15 GB | `free -g` → total 15 |
| GPU | **無** | `command -v nvidia-smi` → not found；`ls /dev/nvidia*` → 無 |
| 生產 DB | PG 17.9 於 127.0.0.1:5432，庫 augur ≈55GB、**253 表** | 253 表：rowcounts 253 行（`wc -l`）；≈55GB **未附產生指令＝未驗**（scratchpad 無 size 類抽出物；與審查現實錨定相符；補驗指令＝`SELECT pg_size_pretty(pg_database_size('augur'))`，需 DB 權限，本審禁連） |
| pgvector | 0.8.4 | `$SP/augur-extensions.txt` |
| 不可回改 trigger | 12 條（**實質護欄 10 條**，2 條僅 ttai touch updated_at——現實官逐一讀函式體認定） | `grep -c 'CREATE TRIGGER' $S` → 12；函式體 `sed -n '94,390p' $S` |
| 沙盒 | ✅ **augur_sandbox 已落成（2026-07-18）**：pg_restore error 0、240 表、TaiwanStockPrice 至 2026-07-16、55 GB；生產庫同時確認未動 | build_sandbox.sh [4/4] 自帶驗證輸出（tasks/bd9tr5yc3）；複驗：`psql -d augur_sandbox -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"` |
| 環境缺件 | ✅ **已補（2026-07-18）**：augur-code/venv/（psycopg2 2.9.12、pytest 9.1.1、requests、python-dotenv） | `venv/bin/python -c 'import psycopg2, pytest'` |

> ⚠️ **infrastructure/ENVIRONMENT-SPEC.md 描述的是另一台不可達的 GB10 機器——與本機實測全面不符，屬主動誤導文件，本圖全程未引用，待重寫（見 §六-5）。**

---

## 二、逐原則落地表

合併三路 items；同一物理不變式之上下位條款併列。狀態衝突以現實官 schema 證據為準。SQL 判定式（需 DB 權限）供 Steward 於沙盒/生產執行，本次未連 DB。

### P1 — Reality First（真實世界優先）

| 條款 | 原文名 | 物理要求 | 現況 | 證據或指令 |
|---|---|---|---|---|
| MC §P1.E1 | 開放來源：資料來源不得成為最高抽象 | 外部觀測以鏡像表落地 | ✅ | raw 觀測鏡像 84 表（83 張 CamelCase FinMind＋fred_series）：`awk -F'\|' '{print $1}' $SP/augur-rowcounts.txt \| grep -c '^[A-Z]'` → 83；最大 USStockPrice\|35,057,083 |
| MC §P1.E2 / WM.14、WM.37 / KS.25 | 共同世界模型語義；語義唯一性；唯一權威表徵 | World Concept 權威表徵指定欄＋事實對多來源映射 | 🔨 | `grep -iE 'CREATE TABLE.*(registry\|concept)' $S` → 僅 model_registry（非世界概念登錄） |
| WM.36 | World Concept Registry 七欄一級結構 | registry 表＋消費經 registry 解析（禁供應商表名直綁） | 🔨 | 同上 grep 零跡象；code 面直綁現值 37 檔：`grep -rlE 'FROM\s+"Taiwan' src scripts --include='*.py' \| wc -l` → 37（augur-code 下實跑） |
| WM.35 | 落地即整合；unmapped 顯式存量 | 通道映射登錄＋unmapped 旗標＋消費閘 | 🔨 | `grep -icE 'unmapped\|channel_mapping' "$S"`（判定式；registry 本體既無，映射必無） |
| WM.31 | 通道時間屬性雙宣告 | ts_semantics＋knowability_rule 二欄 | 🔨 | 判定式：`grep -icE 'knowability\|ts_semantics\|time_semantics' "$S"`；條文 WM:283-290 |
| WM.32 / KS.54 | 觀測定案性；重編留痕 | non-final 標記＋改寫必新版本＋restatement 分類 | 🔨（部分載具候選） | `grep -icE 'non_final\|finality' "$S"`（判定式）；生產已有 restatement_review_queue 表（治理帳表 22 之列，`$SP/cat_gov.txt`）——覆蓋面未驗＝不確定 |

### P2 — Representation Before Intelligence（表徵先於智慧）

| 條款 | 原文名 | 物理要求 | 現況 | 證據或指令 |
|---|---|---|---|---|
| MC §P2.E1 | 禁 AI 直接從 raw 建永久 Knowledge | 衍生層與 raw 分表 | ✅ | 衍生特徵/預測 29 表（`$SP/cat_deriv.txt`，wc -l → 29）；feature_values 純衍生 schema（$S L8712）；daily_direction_feature_values\|19,281,992 |
| MC §P2（表徵載具） | 向量僅為表徵載具 | pgvector 本地落地 | ✅ | vector 0.8.4（extensions.txt）；vector(384) 恰 3 表：CREATE TABLE 行 $S L9647/L9773/L10448；vector 欄行 L9649/L9775/L10450（`grep -n 'vector(' $S` → 9649、9775、10450） |
| MC §P2.E3 / WM.33 / KS.21 | 十類永久標記表達力；self-reported | 十標記欄位＋隨轉引存續 | 🔨 | 實跑：`grep -ciE 'self_reported\|synthetic' $S` → **0**；supersede/retracted/invalidated/tombstone 家族 → **22** 命中（部分載具已備跡象，覆蓋面不確定） |
| WM.18 | 候選斷言狀態閉集 candidate→established→… | 狀態 CHECK 閉集＋Evidence/Confidence 槽 | 🔨 | 判定式：`grep -icE "'candidate'\|'established'" "$S"`；條文 WM:204-208 |
| MC §P2.E5 / WM.29 | Fail-safe 三狀態容納 | 污染標記、暫停狀態、降級旗標 | 🔨 | 判定式：`grep -icE 'quarantine\|suspended\|degraded\|reassess' "$S"`；條文 MC:219、WM:270-272 |

### P3 — Identity（同一性）

生產庫**全空**：`for t in entity_type_catalog entity_registry entity_alias identity_claim identity_lifecycle_event entity_attribute_version; do grep -c $t $S; done` → 全 0；`grep -c 'augur:' $S` → 0。載具＝步 11 六表 DDL（`augur-code/scripts/migrate_identity_ddl.py`）＋identity 模組，**未 apply**。

| 條款 | 原文名 | 物理要求 | 現況 | 證據或指令 |
|---|---|---|---|---|
| ID.11 | 系統鑄造義務 | 系統 identifier 表＋外部碼 alias 映射 | 🚚（表）＋🔨（runtime 接線） | DDL：migrate_identity_ddl.py:64-77；mint/resolve：src/augur/identity/identifier.py:31-70。**identifier.py:15-17 自揭攝取路徑未接線**；`grep -rn 'resolve_or_mint\|identity.identifier' src/augur/ingestion/` → 0 命中 |
| ID.12 / P3.E3（型別面） | 型別化命名空間隔離 | type/namespace 欄＋唯一性 | 🚚 | migrate_identity_ddl.py:48（entity_type_catalog）；`PYTHONPATH=src python3 scripts/seed_entity_type_catalog.py --selftest` → 本機實跑全通過（UPSERT 不回溯改寫 ID.12 不變式） |
| MC §P3.E1 / ID.50、ID.21 / KS.23 | 未解析不得升級 Knowledge | provisional 旗標＋升級閘 | 🚚（結構）＋🔨（閘接線 Phase 5） | entity_alias（外部碼降 provisional）DDL 已備；`grep -icE 'provisional' $S`（生產判定式）；接線零呼叫（上列 grep 0） |
| MC §P3.E2 / ID.13、ID.14 / WM.22 | identifier 永不刪除 | 無 DELETE 路徑（trigger/權限） | 🚚 | DDL 附 no_delete/no_truncate trigger＋de_identify 受控繞過（migrate_identity_ddl.py）；`--selftest` 本機實跑全通過 |
| ID.20 | 採認行為五要素 | criterion_adoption append-only 表 | 🔨 | 三路皆無此載具：`grep -icE 'criterion_adoption\|adoption' "$S"`（判定式）；條文 ID:171-173 |
| ID.30、ID.31 / KS.90、KS.91 | identity claim 四要件 | identity_claim 表＋缺要件即拒 | 🚚 | migrate_identity_ddl.py:94；claim.py:36-48（缺 criterion_ref/evidence_ref 即 ValueError）、:95（L4 值域不 pin 回歸鎖） |
| ID.40、ID.44 / KS.26 | 生命週期事件之 Evidence 義務 | 事件表（六欄＋型別開放集） | 🚚 | migrate_identity_ddl.py:113；src/augur/identity/lifecycle.py（125 行） |
| ID.41、ID.43 | 轉指全程可追溯；存續邊界截斷 | redirect 鏈重建＋代碼重用紅旗登錄 | 🚚（表含紅旗欄）＋🔨（偵測邏輯未驗） | 載具官：identity_lifecycle_event 含 lineage＋代碼重用紅旗；紅旗自動偵測之運行未實證＝不確定 |
| ID.42 / KS.53 / MC §P3.E2 例外 | 法規抹除留痕（tombstone） | tombstone＋抹除事件 provenance | 🚚 | raw 層：PR #2 tombstone SECURITY DEFINER 受控函式（tests/test_raw_supersede_log.py:213）；identity 層：DDL de_identify 受控繞過。生產 `grep -icE 'tombstone\|erasure' $S` 屬 22 命中家族內、無獨立表 |
| ID.51 / WM.15 | 未解析存量三指標；待決同一性存量 | provisional 時間戳＋待決登錄 | 🔨 | 表既不存在指標必不可盤點（生產六表 grep 全 0，見本節首） |
| ID.60 / P4.E2（身份面） | 身份屬性 as-of 繫結 | 屬性 SCD-2 雙時間版本表 | 🚚（表）＋🔨（消費端 Phase 2） | migrate_identity_ddl.py:132（entity_attribute_version）＋attribute_version.py（93 行）；消費端 core_gate 產業判定仍直讀 TaiwanStockInfo 當前值（Phase 2 未做） |
| MC §P3.E3 / ID.53 | instance/type 標記存續 | binding 欄隨轉引存續 | 🚚（型錄面）＋🔨（Knowledge 欄位面） | entity_type_catalog 含 binding（seed selftest 綠）；Knowledge 面判定式：`grep -icE 'instance_type\|is_instance\|binding_kind' "$S"` |

### P4 — Evidence Before Conclusion（證據先於結論）

| 條款 | 原文名 | 物理要求 | 現況 | 證據或指令 |
|---|---|---|---|---|
| MC §P4（對帳留痕） | DB↔API 對帳結果落表 | attestation_result | ✅（覆蓋率誠實有限） | $S L7421-7434（14 欄；L7420 為 CREATE TABLE、L7435 為右括號；`sed -n '7421,7434p' $S \| wc -l` → 14）；rowcounts：attestation_result\|**3**（表在、僅 3 列） |
| MC §P4.E1/E6（留痕面） | 寫入/對帳逐筆留痕 | data_audit_log | ✅ | $S L7726-7734；rowcounts：data_audit_log\|**259,975**（實際在用） |
| MC §P4.E1 / KS.20-24、KS.26 | Knowledge 五元組（不可豁免核心） | 五槽俱在可機器解析 | 🔨 | 現實官精確陳述為準：public schema（236 表）**零** confidence 欄；僅 ttai_import 遺留二欄（$S L11850/L12014）＋一 view（L12149）：`grep -ci confidence $S` → 5，逐行檢視全在 ttai_import（義務官 `grep -cE '^\s+confidence'` → 2 為欄位計數，不衝突） |
| MC §P4.E2 / WM.30 / KS.22、KS.40 | 雙時間性 | valid time＋transaction time 二獨立槽 | 🔨（部分✅＋部分🚚） | ✅僅 fred_series vintage（$S L8831-8836，realtime_start NOT NULL 入 PK；rowcounts 344,063）；**84 張 FinMind 鏡像皆無 tx-time**；欄名模式全庫 0：`grep -cE '^\s+(valid_time\|valid_from\|valid_to\|transaction_time\|tx_time)\s' $S` → 0；🚚 entity_attribute_version（身份屬性面） |
| KS.41、KS.42、KS.46 | As-of 能力分級（A0 禁止） | 表級 tier 登錄結構 | 🔨 | 判定式：`grep -icE 'asof\|as_of_tier\|capability_tier' "$S"`；條文 KS:336-348 |
| KS.43 | 已呈現結論不可靜默重寫 | 新版本＋superseded 標記；禁 DELETE+INSERT | 🔨（部分✅＋🚚） | ✅僅 arena 二 trigger：trg_arena_pred_immutable（fn $S L161）＋trg_arena_pred_no_backfill（fn L190）——僅覆蓋 arena 表；🚚 prediction_serving_log（migrate_prediction_serving_ddl.py:37，`--selftest` 本機綠）；prediction_values 本體切換（Phase 4）未動 |
| KS.45 | point-in-time 成員集可重建 | 成員版本欄（A2/A3） | 🔨（不確定） | core_universe×5 表存在於衍生清單（cat_deriv.txt）；其 as-of 可重建性未驗＝**不確定**；判定式：`SELECT count(*) FROM <universe表> WHERE valid_from IS NULL` |
| MC §P4.E3 / KS.50 | 只失效不刪除 | 標記欄＋禁刪 trigger/權限隔離 | 🚚（raw 層）＋部分✅（gate/arena）＋🔨（Knowledge 面全覆蓋） | 🚚 raw_supersede_log：`grep -c 'CREATE TABLE.*raw_supersede_log' $S` → **0**（未 apply）；載具 scripts/migrate_raw_supersede_ddl.py（240 行）＋schema.py:77-88；✅ arena/gate 凍結 trigger 10 條；augur-triggers.txt 無任何 append-only trigger（`grep -cE 'no_update\|no_delete\|append'` → 0） |
| KS.51、KS.52 | Supersede Relation 六欄一級物件＋DAG 無環 | 獨立六欄表＋無環驗證 | 🔨 | raw_supersede_log 僅為 raw 層近似載具（old_row 快照＋reason＋actor），非 KS.51 六欄一級 Supersede Relation；條文 KS:376-382 |
| KS.55 | 衍生物禁全量 DELETE 重建 | 版本化＋supersede | 🔨 | 判定式：`SELECT relname FROM pg_stat_user_tables WHERE n_tup_del>0 AND relname IN (…)`（需 DB） |
| MC §P4.E5 / WM.16 / KS.60-63 | 矛盾保存；Conflict Set 一級物件；禁 LWW | conflict 標記＋Conflict Set 表 | 🔨（部分✅＋🚚） | ✅「證據不足」可表達：$S L8365 deliberation_verdict CHECK verdict ∈ {confirmed,refuted,**undecidable**}；🚚 raw_supersede_log 禁 LWW（heal 前 pre-image 快照，generic_schema.py:277、:315 fail-loud）；Conflict Set 一級物件零跡象：`grep -icE 'conflict_set' "$S"`（判定式） |
| MC §P4.E6 / KS.70 | Evidence 一級物件、遞迴溯源（不可豁免核心） | evidence 節點/邊表、鏈終止於 Observation | 🔨（部分✅＋🚚） | ✅骨幹：deliberation_verdict_check「非 undecidable 必附 evidence」由 DB 執法（$S L8356-8366）；model_registry 六凍結欄全 NOT NULL（L10310-10324，**惟無 immutability trigger**）；🚚 raw_supersede_log.actor/reason/attestation_run_id FK（schema.py:76-77）；遞迴 Evidence 一級表不存在：`grep -icE 'CREATE TABLE.*(evidence\|provenance)' "$S"`（判定式） |
| KS.71 | Evidence 三分類 | evidence_class 欄 | 🔨 | 判定式：`grep -icE 'evidence_class\|evidence_type' "$S"` |
| MC §P4.E7 / KS.72-74 | Trust Rank；NoLaundering；synthetic 永久標記 | trust_rank＋synthetic 欄隨衍生存續 | 🔨 | 實跑：`grep -ciE 'synthetic\|self_reported' $S` → **0**（全庫零欄位） |
| KS.75-77 | 獨立性判準；高風險證據要求；self-reported 不升信 | 獨立性機器判定＋人類確認留痕表 | 🔨（部分✅候選） | 人類確認留痕之既有候選＝direction_gate 簽核（chk_dg_approved_signed，$S L8515-8534）與 knowledge_source_review_log（L9886-9899）；通用 human_confirmation 表無 |
| KS.78 | 通道白名單完整性 | 維度白名單表＋解析 | 🔨 | 判定式：`grep -icE 'whitelist\|dimension_roster' "$S"` |
| KS.79 | 審議 Evidence 強度分級；claim 繫結 Identity | deliberation confidence 欄＋identity FK | 🔨 | deliberation_claim 表在（$S grep 命中）、confidence/identity 欄零跡象：`grep -A30 'CREATE TABLE public.deliberation_claim' $S \| grep -cE 'confidence\|identity'`（判定式） |
| MC §P4.E8 / KS.30、KS.31 | 單一論域 L_C 有界偏序格 | L_C enum/CHECK＋各物件映射 | 🔨 | 判定式：`grep -icE "CREATE TYPE.*confidence\|'INSUF'\|'DETERMINISTIC'" "$S"`；confidence 本體零欄（見 P4.E1 列） |
| KS.32、KS.33 | Grading Method 可追溯；banding | grading_method 引用欄＋閾值登錄表 | 🔨 | 判定式：`grep -icE 'grading_method\|banding' "$S"` |
| KS.34、KS.35 | 傳播上限；消費最低約束 | 推理鏈邊表＋Action basis FK | 🔨 | 條文 KS:251-263；前提結構（Evidence 邊表、action 表）均未落地 |
| MC §P4.E4 / KS.36 | 可謬性；失效連動重評 | 無頂錨預設、無不可修正標記 | 🔨 | 判定式：`SELECT … WHERE column_name ILIKE '%confidence%' AND column_default IS NOT NULL`（需 DB） |
| KS.37 / Annex CM | 官方映射（既有可信狀態映入 L_C） | lc_mapping 登錄表 | 🔨 | 判定式：`grep -icE 'lc_mapping\|confidence_mapping' "$S"`；CM.1(a) 十一列映射在卷（KS:281-325） |
| KS.38 | 暫行期保守規則（無 Confidence＝INSUF） | 消費視圖 COALESCE-to-INSUF 閘 | 🔨 | 判定式：`grep -icE "COALESCE.*(INSUF\|confidence)" "$S"` |
| MC §P4＋§8.3（預註冊） | 可證偽賭注預註冊 | direction_gate 判準先寫死＋簽核 | ✅ | $S L8515-8534：status DEFAULT 'preregistered'、狀態機閉集、chk_dg_approved_signed；rowcounts：direction_gate\|21；配套 trg_direction_no_goalpost（fn L207） |

### P5 — Accountability Before Action（可歸責先於行動）

| 條款 | 原文名 | 物理要求 | 現況 | 證據或指令 |
|---|---|---|---|---|
| MC §P5.E1 / WM.27 / §F6 / §P5.W1 | Action 六元組；禁無法歸責之 Action | authorization_grant＋automation_action_log 六元組留痕 | 🚚（表＋helper）＋🔨（接線 Phase 5） | `grep -c 'authorization_grant\|automation_action_log' $S` → **0**；載具 migrate_automation_action_ddl.py:37,49＋action_log.py:1-30（缺 actor_identity 即 ValueError），`--selftest` 本機實跑綠；現行 watchdog/selfheal 仍寫家目錄純文字 log（audit_selfheal.sh:9 → $HOME/audit_retry.log） |
| MC §P5.E2 | 風險分級 DEFER：分級表生效前一律最高風險、人類事前逐案核准 | human_approval 留痕＋暫行分級欄 | 🔨（部分✅候選） | 通用 human_approval 表零跡象（判定式 `grep -icE 'human_approval\|pre_approval' "$S"`）；既有候選＝direction_gate 簽核閘（僅覆蓋 gate 流程） |
| MC §P5.W2 | 授權鏈根節點必須是人類權威 | fail-closed 產物閘＋人簽 | ✅ | direction_product_gate_guard fn（$S L248-262）：gate 非 evaluated_pass 即 RAISE，掛 daily_direction_probability＋direction_probability（L15608、L15622）；staging_source_gate（L15573）；knowledge_source_review_log 11 動作 actor NOT NULL（L9886-9899，rowcounts\|81） |
| MC §P5.W2（item 層缺口） | knowledge_item 層來源門 | trg_item_source_gate 掛表執法 | 🔨 | **函式在庫未掛表**：fn $S L288-312 存在，`grep -c 'EXECUTE FUNCTION public.trg_item_source_gate' $S` → **0**（現實官發現；僅 staging 層有執法） |
| MC §P5.W4 | 最小權限 | prediction_serving_log＋predict 角色隔離 | 🚚 | `grep -c 'prediction_serving_log' $S` → 0；載具 migrate_prediction_serving_ddl.py:37＋setup_predict_role.py＋test_predict_role_isolation.py |
| MC §P5（執行留痕） | 管線執行留痕 | pipeline_execution_log | ✅結構＋🔨接線 | $S L10701-10710 表在；rowcounts：pipeline_execution_log\|**0**——表在但零列，執法未接線 |

### §8 與跨層條款

| 條款 | 原文名 | 物理要求 | 現況 | 證據或指令 |
|---|---|---|---|---|
| MC §8.3（末項）/ WM.34 | 核心不變式必須可機器稽核 | (a) K→E→Observation 鏈可遍歷無環；(b) Action→Actor 單值 FK | 🔨（部分✅） | ✅可判定性 CHECK 已由 DB 執法：deliberation_claim anchor 非空/verifier 閉集/status 閉集（$S L7921-7938）＋verdict evidence CHECK（L8356-8366；rowcounts claim\|396、verdict\|352）；🔨稽核工具 audit_lint.py 僅 120 行純檔案掃描骨架（`wc -l` → 120）：零 DB 連線（全檔 grep 無 psycopg2/connect）、_STUB_RULES 明示三組未實作（audit_lint.py:102-106） |
| MC §8.4 | 豁免期間標記義務 | exemption/evidence_gap 標記欄＋豁免登錄（到期日） | 🔨 | 判定式：`grep -icE 'exemption\|waiver\|evidence_gap' "$S"`；條文 MC:504-509 |
| MC §8.1、§8.2、§8.5、§8.6 | Steward 權威；違憲審查；修訂程序；版本語義 | 文件/治理載體，無 DB 落點 | 📜 | MC:470-527；存檔檢查：`grep -l 'Amendment Log' constitution/*.md` |
| MC §8.3（聲明段）/ WM.39-45 / ID.80-81 / KS.110-111 | 合規聲明義務 | 每份生效規格內含聲明 | 📜 | `grep -lc 'Constitutional Compliance Statement' specs/*-SPECIFICATION.md` |
| WM.4、WM.24 / KS.39、KS.100-102 / ID.61、ID.70-71 | 層間管轄分界 | 約束規格文本自身 | 📜 | 實體義務已由各上位條款列出，無獨立 DB 落點 |

---

## 三、已落地清單（生產庫既有合憲結構——憲章不是空想的證據）

每項附 schema 行號或可重跑指令：

1. **attestation_result**（P4 對帳留痕）：14 欄全列（$S L7421-7434）；僅 3 列（rowcounts）——覆蓋率誠實有限。
2. **data_audit_log**（P4.E1/E6）：$S L7726-7734；**259,975 列**實際在用。
3. **審議可判定性 CHECK 群**（§8.3）：claim anchor 非空、verifier 七值閉集、status 五值閉集（$S L7921-7938）；**verdict 非 undecidable 必附 evidence 直接由 DB 執法**（L8356-8366）；「證據不足」為合法一級狀態（undecidable ∈ 值域，L8365，P4.E5）。
4. **direction_gate 預註冊賭注**（P4）：criteria+criteria_sha+git_sha NOT NULL、status DEFAULT 'preregistered'、狀態機閉集、approved 強制簽核（$S L8515-8534）；21 列。
5. **10 條實質護欄 trigger**（$S L15573-15650；函式體 L94-390）：挪門柱鎖×3（arena_admission、direction_gate、unfreeze_gate）、arena 凍結/反回填×3、fail-closed 輸出契約×2（gate 非 evaluated_pass 不得寫產物表）、洩漏迴歸鎖×1（feature_panel_hash_baseline）、staging 來源門×1。**誠實揭露**：12 條中 2 條（trg_ku_touch/trg_vf_touch@ttai_import）僅 touch updated_at，非憲章護欄。
6. **fred_series 雙時間 vintage**（P4.E2）：realtime_start NOT NULL 入 PK（$S L8831-8836）；344,063 列。**僅此一表**；84 張 FinMind 鏡像無 transaction-time。
7. **knowledge_source_review_log**（P5.W2）：11 動作閉集、actor NOT NULL、os_user、probe_result（$S L9886-9899）；81 列；配套 staging_source_gate trigger。
8. **model_registry 六凍結欄**（P4.E6）：train_span/asof_snapshot/feats_hash/seed/git_sha/artifact_path 全 NOT NULL（$S L10310-10324）；15 列。**誠實揭露**：無 immutability trigger，凍結靠欄位約定非 DB 執法。
9. **pgvector 表徵層**（P2）：vector 0.8.4；三張 vector(384) 嵌入表＋向量治理配套（qdrant_sync_state、vectorstore_shadow_eval 等）。
10. **層次分離**（P1.E1/P2.E1）：raw 鏡像 84｜衍生 29｜治理帳表 22｜審議 16｜知識/哲學 68｜向量 7｜使用者/RBAC 10｜ttai_import 16＝252 唯一表名＋1 跨 schema 重名（knowledge_source）＝253（`cat $SP/cat_*.txt | sort | uniq | wc -l` → 252）。
11. **漂移揭露**：knowledge_sent_terms_stage 在 rowcounts 有、schema dump 無 CREATE TABLE（comm 導出）——兩抽出物間庫有變動或 dump 遺漏；各數字以各自產生指令為準。

---

## 四、載具清單與落地序（沙盒驗證 → P5 拍板 → 生產 apply）

**核心事實**：十張新表（raw_supersede_log＋步 11 九表）於生產 17690 行 dump **全部 grep 零命中**；12 條既有 trigger 無任何 append-only 者。即全部結構載具「一張都未 apply 生產」。

### 載具清單

| 載具 | 落什麼條款 | 位置 | 本機驗證現況 |
|---|---|---|---|
| PR #2：raw_supersede_log（origin/remediation/aud-02-consolidated） | P4.E5（禁 LWW）、P4.E3（tombstone 例外留痕）、P4.E6（actor/reason/run_id 溯源） | scripts/migrate_raw_supersede_ddl.py（240 行硬化）＋src/augur/core/schema.py:77-88＋generic_schema.py:277,315,387-399 | 15 測試檔案實存（`git show origin/remediation/aud-02-consolidated:tests/test_raw_supersede_log.py \| grep -c 'def test_'` → 15）；**「PG 16.14 全綠」宣稱現機不可獨立重驗**（find 全 /home/giga 查無 micromamba/pg_ctl/initdb → 零命中）——必以 augur_sandbox 實跑為準；migrate 腳本模組層 import psycopg2 致 `--selftest` 現機不可跑 |
| 步 11 六 identity 表 | P3.E1/E2/E3、P4.E2（ID.11-14/30-32/40-44/60-61） | scripts/migrate_identity_ddl.py:48-132＋src/augur/identity/（identifier/claim/lifecycle/attribute_version.py）＋seed_entity_type_catalog.py | `--selftest` 本機實跑全通過（identity_ddl、seed 二支）；ID.11 runtime 義務自揭未接線 |
| 步 11 二行動表 | P5.E1、F6 | scripts/migrate_automation_action_ddl.py:37,49＋src/augur/execution/action_log.py | `--selftest` 本機實跑全通過 |
| 步 11 一 serving 表 | P4.E3/KS.43（prediction 面） | scripts/migrate_prediction_serving_ddl.py:37＋setup_predict_role.py＋test_predict_role_isolation.py | `--selftest` 本機實跑全通過 |
| audit_lint（#22） | §8.3 機器稽核 | tools/constitution_lint/audit_lint.py（120 行） | 🔨非🚚：僅三種子規則純檔案掃描；缺 DB 連線層、SQL 不變式檢查集、DB 面政策分流 |

### 落地序與各步之閘

1. ✅ **環境補件完成（2026-07-18）**：venv 建立、`venv/bin/python -c 'import pytest, psycopg2'` 通過。
2. ✅ **augur_sandbox 還原完成（2026-07-18）**：240 表、55 GB、pg_restore error 0、生產庫未動（[4/4] 驗證輸出）。
3. ✅ **沙盒實測完成（2026-07-18）——元憲章首次物理落地**：
   - **十張憲章新表全數 apply 沙盒**（`DB_NAME=augur_sandbox` shell 覆蓋 .env，load_dotenv override=False 實測驗證）：raw_supersede_log（append-only＋no-truncate trigger、tombstone SECURITY DEFINER✓、PUBLIC mutate 無殘餘）；identity 六表（10 條 permanence trigger、lifecycle 九型別 Evidence 硬義務 CHECK、de_identify SECURITY DEFINER✓）＋type catalog seed 4 列；automation 二表（P5.E1 六元組欄全、雙 FK）；prediction_serving_log（A1 能力 COMMENT、僅 superseded_by 可 UPDATE）。
   - **PR #2 十五測試 15/15 PASSED**（`DB_NAME=augur_sandbox venv/bin/python -m pytest tests/test_raw_supersede_log.py` → `15 passed in 0.33s`，生產同版 **PG 17.9**、55GB 完整複本）——六不變式全數行為驗證：gate 非 heal 不留痕／byte-differ 入帳／no-op 不入帳／append-only 擋 UPDATE+DELETE／TRUNCATE 擋／tombstone 受控抹除／同交易回滾。**取代原不可重驗之「PG 16.14 全綠」宣稱（§五該列解消）**。
   - 三支 migration `--check` 沙盒綠；終驗：生產 augur 240 表、raw_supersede_log 不存在（未動）；沙盒 250 表（240＋10）。
4. ✅ **P5 拍板（2026-07-18）**：Steward（tsaitsangchi）於工作對話書面指示「apply進生產」。
5. ✅ **生產 apply 完成（2026-07-18）**：
   - 前置：生產快照（240 表、TaiwanStockPrice 至 2026-07-16＝與 dump 同步、prediction_values 1695／feature_values 2,510,040／deliberation_claim 396、活躍寫入者 0）；回滾態勢＝新增式（DROP 十新表即復原）＋9.9G dump 雙保險。
   - Apply：五支 migration＋seed 依沙盒同序 → 生產 `augur`。
   - 事後驗證（全唯讀）：**250 表**；快照三表列數**逐一相等**（1695／2,510,040／396）；**18 條護欄 trigger 在位**（pg_trigger 唯讀列舉）；tombstone/de_identify **SECURITY DEFINER✓**；**十新表對 augur_predict SELECT 全拒**（has_table_privilege 逐表查證——WM.35 消費閘已達，setup_predict_role --apply 僅餘 Phase 4 之 serving 寫權授予、非隔離必需）。
   - 行為證據承接：同一份 DDL 於沙盒經 PR #2 **15/15 行為測試**驗證（含 append-only 擋改刪、TRUNCATE 擋、tombstone 受控、同交易回滾）。
   - **殘餘（誠實揭露）**：表 owner＝augur＝應用角色——owner 分離未落地（owner 可 DISABLE TRIGGER），列 §五既有 ⛔ 族、待部署層處置；runtime 接線（Phase 1/2/4/5）未動，新表現全零列屬預期。
6. **Runtime 接線另案**（各有完成判準）：Phase 1 vendor 直綁消除（判準：37 檔 grep → 0）、Phase 2 屬性 as-of 消費、Phase 4 serving_log 消費切換、Phase 5 resolve-or-mint＋action_log 接線（判準：ingestion grep 出現接線且沙盒 entity_registry 有 mint 記錄）。

---

## 五、現況不可落地者（誠實清單）

| 項 | 憲章關聯 | 不可落地原因（實測） | 最小解法 |
|---|---|---|---|
| 本機 LLM 推論（L5 類義務之算力前提） | ⛔ | 無 GPU：`command -v nvidia-smi` → not found；`ls /dev/nvidia*` → 無；12 核/15GB（`nproc`、`free -g`）不足以本地推論實用規模模型 | 外部 API 推論＋一切 AI 產出依 KS.74 永久攜 synthetic 標記、受信任天花板；或待可達之 GPU 硬體到位後遷移（注意：ENVIRONMENT-SPEC 所述 GB10 不可達，不得作為規劃依據） |
| kill-switch 實體獨立 | ⛔ | 單機：DB、應用、審計載體同在一台 WSL2（本圖 §一全部實測同機產生）——不存在可獨立斷電/斷網之第二實體 | 程序級替代：獨立 OS 帳號持有之 revoke 腳本＋DB 角色權限收斂＋異地備份；並依 §8.4 登錄為豁免（附到期日與補正計畫）；建議 Steward 裁定：豁免登錄不宜宣稱等效實體獨立（裁量屬 §8.1） |
| 雙人核准（two-person rule） | ⛔ | 單一自然人：Steward 與操作者為同一人（治理文件在卷；人數屬物理事實非文件自陳） | 時間延遲核准（cooling-off 期）＋不可回改留痕（append-only 表）替代第二人在場；依 §8.4 明記豁免與 Evidence 缺口標記 |
| ~~PR #2「PG 16.14 全綠」之獨立重驗~~ | ✅ **已解消（2026-07-18）** | 原不可重驗（micromamba 環境查無）；已依 §四步 3 於 augur_sandbox（生產同版 PG 17.9、55GB 複本）重跑 → **15/15 passed**，宣稱由新鮮實證取代 | — |
| 55GB 級沙盒之常駐並存 | ⛔（邊際） | 磁碟/記憶體邊際：15GB RAM、生產庫 55GB——沙盒與生產同機並存屬緊平衡（沙盒還原中，實際佔用未量測＝**不確定**） | 沙盒驗證完成即釋放；或僅還原驗證所需子集 |
| **生效規格文本自身之標記可信度** | ⛔（引用前提受損） | 本圖以「權威悉依各 [N] 條款原文」為據並引用規格條文行號（WM:283-290、KS:336-348 等），惟同 repo HANDOFF.md:11/57/64/161 錨定：4 份生效規格（L3-L6）**151 個誤標**（MC 側 109／上層側 42）＋ **L2 真值未知**（其 56 列 Annex TR 矩陣從未受檢、卻曾以 ✅ PASS 發布並支撐 RULING-2026-003）。此二數屬文件錨定值，依鐵律**本圖未獨立重驗＝未驗** | 本圖所引條文以規格檔案原文為準，其 **[N]/[I] 標記不得逕信**；Steward 裁決 #22 前應令 gate 重跑出證（見 §六-3） |

---

## 六、給 Steward 的落地決策點

本節僅陳列決策點，不預作任何決定；一切核准屬 §8.1。

1. **PR #2 apply**（raw_supersede_log）：前置＝§四落地序步 1-3（沙盒 15 測試全綠為硬閘，取代不可重驗之 PG 16.14 宣稱）。附帶裁決：attestation_run_id nullable（決策 B）維持與否。
2. **步 11 九表沙盒實測後 apply**：六 identity 表＋二行動表＋一 serving 表；本機四支 `--selftest` 已綠，沙盒 `--check` 與行為測試為硬閘。附帶裁決：authorization_ref 是否 NOT NULL（升裁決項 C）；apply ≠ 落實——ID.11/P5.E1 之 runtime 接線（Phase 1/2/4/5）各為獨立後續案。
3. **#22 audit_lint 與 CI 接線**：現為 120 行檔案掃描骨架（零 DB）。**#22 之由來即 4 份生效規格 151 個誤標＋L2 真值未知**（HANDOFF.md:161 錨定，依鐵律本圖未重驗；見 §五末列）——裁決前應令 gate 重跑出證、確認數值已收斂。決策：是否授權新增 `--db` 模式（驗收判準＝能對 augur_sandbox 重現 12 條 gate trigger 在位檢查）＋DB 面 legacy 豁免清單之建立。
4. **L7 六阻斷**：本三路盤點未涵蓋其細節（**不確定**——僅列為既有議程項）；建議 Steward 以與本圖同等之證據紀律（每數字附指令）要求其盤點後再議。
5. **ENVIRONMENT-SPEC.md 重寫**：現版整份描述另一台不可達之 GB10——主動誤導。決策：作廢並以本圖 §一實測基線（含產生指令）重寫；建議裁定：重寫前凍結該文件之引用（是否凍結屬 §8.1 裁量）。
6. **既有缺口之快速接線裁決**（低成本高收益，均有 schema 證據）：(a) trg_item_source_gate 函式在庫未掛表（$S L288-312、CREATE TRIGGER 零命中）；(b) pipeline_execution_log 表在零列（rowcounts\|0）；(c) model_registry 無 immutability trigger；(d) 84 張 FinMind 鏡像無 transaction-time（補正方向與 as-of tier 宣告 KS.42 一併議）。

---

*本文件 [I]：資訊性，不創設義務，不宣稱任何充任或生效。統整自三路盤點（義務官 44＋3 項、現實官 22 項、載具官 14 項），衝突以現實官 schema 行號證據為準。快照日 2026-07-17。*
