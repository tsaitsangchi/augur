# Augur 建構作法完整理解 v2 — code-verified 全系統合成(對抗審查+自我迭代)

**日期**:2026-07-09 ｜ **性質**:理解報告(非計畫;v1.39.0 計畫完整性不適用,但仍以 file:func+schema 錨定)｜ **方法**:ultracode 20-agent pipeline(9 子系統 deepRead → 對抗驗證懷疑者 re-read code 找錯/補漏 → 完整性 critic → 綜合)+ 主作者親驗承重修正(#15)。**本版 supersede 同日第一版(9-reader 版)**——修正其錯誤/過度宣稱、補其空白、加跨系統合成。
**範圍**:src/augur 12 packages · scripts ~110 支 · docs 治權 4 檔 · tests 16 支 · DB 2 schemas(public 178 表 + ttai_import 16 表)。

---

## 0. 三十秒 × 核心框架

**augur = 兩個半系統,只被兩條線接起來**:
- **半-1 = 量化預測管線**(packages:features / models / universe / evaluation / ingestion / catalog / audit)——「只用真實資料誠實預測台股**相對強弱**」。
- **半-2 = 博學顧問 / 知識服務層**(packages:philosophy / advisor / knowledge + 3 web servers)。
- **唯二耦合**:(a) **PostgreSQL 就是 message bus**;(b) **一個唯讀 dataclass `PredictionPayload`**(payload.py)。除此**零 cross-half Python coupling**——`audit/import_isolation.py` 機械強制單向依賴:半-2 可讀半-1 之**輸出**,半-1 對半-2 **零反向 import**(本輪實跑 `check_isolation()==[]`、`test_philosophy_isolation` 7 passed,不變式現正成立)。

**建構脊椎兩軸**:WHY = 三個敵人(①假資料 #1 / ②偷看未來 #8 / ③自我欺騙 #15);HOW = 管線 `raw→feature→universe→model→validate` + 橫切(core/audit/catalog/execution/philosophy/knowledge/advisor)。**核心信念:三敵零容忍從口號變機械不變式**——schema / 型別 / 封閉集 / AST 稽核 / 正則閘 / DB CHECK / **DB role** / 純函式複用 結構性封死,不靠自律。

**本版相對第一版(9-reader)之修正/新增**(親驗過):
- **版本錨過時更正**:憲章 v1.38.0→**v1.39.0**、CLAUDE v1.21→**v1.22**(第一版寫 stale)。
- **live 驗證(第一版純靜態)**:isolation `[]`;harness 已實例化(2 models/688 preds/105 revalidation/4 baselines);augur_predict role **LIVE**。
- **補齊第一版幾乎空白的半-2**:serving 三 server 拓撲、advise() 完整漏斗、RBAC/identity/access 全鏈、蒸餾子系統、revalidation 判停 loop、TTAI schema。
- **修正承重精度誤差**(§7 corrections log):feats_hash「防漂移」是死碼過度宣稱、per-module 契約非統一、missing-row 兩 regime、quota-gate 兩獨立 120、jieba floor 非 pin、philosophy 9 表非 6、FRED PK 含 series_id。

---

## 1. 治權脊椎(建構最高依據 · SSOT 分層防漂移 #12)

- **靈魂《系統核心思想 v1.5.0》**=WHAT/WHY;北極星 3 問(真 API①?決策當下可見②?OOS 撐住③?)及於一切判斷含 operational。
- **原則精華 v1.8.0 = 20 條不可違反法律**,WHAT|WHY|ENFORCE 三元組(ENFORCE 點名機制)。★基石=#1 零幻像/#8 anti-leakage/#15 誠實,一敵一法。條號刻意非連續按分類:A 資料 #1-7,17,18 · B 建模 #8-12 · C 風險治理 #13-15,19 · D 開發協作 #16,20。
- **憲章《系統架構大憲章 v1.39.0》=HOW**:6 部;只承載框架、交叉引用方法論、**拒複述法律全文**(「SSOT 鐵律:法律全文只住原則精華」)。
- **CLAUDE.md v1.22**=AI 工具規則(最低位階、半衰期 6-12 月)。
- **升版連動精確 trigger**:架構/方法承載 or 判準擴充(non-loosening 三敵)→ 憲章單獨升;唯有被改判準之 SSOT 文字實體住原則精華才 co-bump(「原則精華維持 v1.7.1」在憲章 sync 條出現 22 次;唯一 co-bump=v1.38.0 FREEZE 因完整性判準子條住原則精華 A 段)。
- **三敵×管線防線地圖**:敵①=#1-7,9,10,16-18;敵②=**僅 #8**;敵③=#10-16,19,20。層鐵律:**選股不算特徵、特徵不抓 API、驗證不讀訓練產物**。
- **as-of 2026-05-31 = 治權參數 + 全系統 FREEZE**(develop-on-frozen-snapshot)。
- **治權→code 接線**:隔離不變式住 `audit/import_isolation.py`、被 `tests/test_philosophy_isolation.py` 當 SSOT import;命名(library=領域名詞/CLI=動作動詞);標頭(🎯 docstring+守原則行+指令矩陣)。

---

## 2. 各層 HOW-built(逐層 file:func + schema · code-verified)

### 2.1 raw(ingestion+core)— 真實 API → DB 零幻像
`sync.py`(排程/adaptive/resume)→`ingest.py`(#4 守門+data_id→PK+audit)→`generic_schema.py`(型別/PK/DDL/upsert)→`db.py`(transaction)→PG。`finmind/fred` 葉端只回 `list[dict]`、欄名逐字照 API(#2)、不補值(#1)。`config.py`=唯一 secrets 讀者(9 os.getenv 全在此;唯一例外 finmind.py:90 讀 ops-flag)。
**FinMind 三層防護**(`_protected_get` per attempt,fetch 5 attempts):① `_quota_gate`(序列化 `_quota_lock`)——每 QUOTA_METER_EVERY=**120 call** OR **≥120s**(⚠ line 93 硬寫字面 120、與常數湊巧相等但獨立)→ 讀權威錶 user_info → count≥limit−**QUOTA_HEADROOM(200)** 則**持鎖**暫停、每 QUOTA_POLL=150s 重讀退到 (limit−HEADROOM)//2;**持鎖=全 worker 一起停**、閾值隨 limit 動態;逃生閥 `FINMIND_QUOTA_GATE=off`(undocumented);錶失聯→放行。② `_pace`(獨立 `_pace_lock`、**兩把鎖**)——鎖內預約 slot、鎖外 sleep → start-INTERVAL≥**MIN_INTERVAL=0.9s**;**start rate 受 pace 非並發**(降並發無效)。③ 反應式 `_RETRY_STATUS=(402,429,403,500,502,503,504)`(**含 402**);403→固定 QUOTA_COOLDOWN=1800s 不風暴;422 刻意**不在** retry(留給 enum-probe)。全 fetch 路共用 `_protected_get`(#24);`_user_quota` 讀錶 bypass pace/gate、打不同 host、403 期間可讀。
**資料驅動零 hardcode**:`list_datasets` 送 `__augur_probe_invalid__`→422 body enum→`_DATASET_RE`;fetch 單日型自適應(msg 含 end_date+none→遞迴去 end_date)。
**generic_schema 精度不變式(#1)**:`_coerce` 數值以**原始 API 字串**傳 PG cast、**永不經 Python float**;`_NULL` 統一 sampling/PK/write;全欄皆 key→upsert DO NOTHING;detect_keys require-keys 只在 greedy-success 尊重。建表模式①=generic 自動 schema(widen only、SAVEPOINT 容併發首建)。
⚠ **core/schema.py ≠ generic_schema.py**:前者持 INFRA_DDL(pipeline_execution_log/data_audit_log 顯式 DDL、模式②)。`FULL_START='1990-01-01'` 僅 backward-probe 下界、**非全史保證**(GoldPrice 真起點 1979 曾被夾)。

### 2.2 feature(features/*)— 35 特徵 → 一張 EAV 表
組合根 `panel.build_panel` fan-out 6 module,寫 `feature_values(panel_date,stock_id,feature,value NUMERIC(20,6) NOT NULL, PK(3欄))` ON CONFLICT DO UPDATE;builder-owns-DDL(模式③,live 2.42M 列)。
**35 特徵**:panel.compute_features(**PURE, price df**)14(含 volatility_**60d 僅**、剪共線 20d);chip(cur,sid,pd)7;valuation 5;concentration(**PURE**)4;phase(+第4 price_df 參數)4;margin_cycle 1;`macro.py` 貢獻 **0**。
**INVARIANT 1 — per-module 契約 NON-UNIFORM**(⚠ 第一版過度宣稱統一):純核 concentration/panel 只吃 price df 無 cur/DB;chip/valuation/margin_cycle 才 (cur,sid,pd);phase 多第 4 參;macro 無 compute。
**INVARIANT 2 — 兩種缺列 regime**(⚠ 第一版壓平):(a) P 類算不出→**省列**(isfinite 過濾,僅 panel/concentration/phase 有);(b) E 類無事件=**真零**(chip 借券/官股填 0)。`chip._table_covers` 雙邊 gate(≤panel AND panel−max≤`_MAX_STALENESS_DAYS=14`)+ `_TABLE_DATE_RANGE` cache:**表未涵蓋此日→拒填零**(gov_bank pre-2021-07→全缺列→不進 required→無 0-core 誤殺)。
**三鏡頭=方法論/計畫層綜合、非每模組 in-file**(只 concentration/phase/margin_cycle docstring 自標)。**#8 命門 release_lag**:發布日 gate(15/45/90);調整價單一基礎(自動移停牌 close=0)。

### 2.3 universe(core_gate)— 四道閘
`build_universe_asof`→`core_universe_asof`(PIT 消 survivorship #8,live 12,394)。候選空間→**完整度閘**→流動性 P25(script-supplied 非 gate 常數)→conditional(金融保險豁免,真集=build_core_universe.py:23「金融保險/金融業」非 docstring 例)。**最深機制=資料驅動完整性不變式**:`required = 市場實際可算 (panel,feature) 組合數`(非 len×len)、absent_combos surface(#15);跨模組綁 chip._table_covers。⚠ **core_gate.canonical_features(寬 union)≠ baseline.canonical_features(嚴 intersection HAVING count(DISTINCT panel)=len)**。

### 2.4 model+validate(models+evaluation)— predict then validate honestly
**脊椎**:evaluation=數學 SSOT;models=薄殼;scripts=orchestration;DB=ledger。
**models(tiny)**:RankRidge=StandardScaler+Ridge(α=1.0);RankGBDT=LGBM(200/0.05/15…)。⚠ 這些 config 是 baseline.py:141-148 的**字面複本**、靠慣例同步**非共享碼**(比 portfolio live≡backtest 強共享弱)。`registry.register`=idempotent、family/horizon/train_span/asof/feats_hash/seed **凍結**;`latest(family,h,asof)`=WHERE asof_snapshot≤asof(**PIT 絕不選 as-of 後模型 #8**)。`artifact.feats_hash`=sha256(sorted feats)[:16] order-independent。
⚠ **feats_hash「防漂移」是過度宣稱(親驗死碼)**:predict_asof.py:120 `cur_feats=canonical_features(...)` **算了但 121 行比對用 `feats`(artifact 自己凍結集)** → `cur_feats` 死碼、只查 artifact↔registry **竄改**、**非防 live pipeline 漂移**;docstring「換特徵集失效」stale。
**evaluation**:`canonical_features` INTERSECTION、**只讀 feature_values 絕不讀 candidate**(audit boundary);`walkforward` `_FEATURE_LAG_TD=62`/`_H_FORBIDDEN=252`、splits GUARANTEED 路(有 calendar 逐折保證 emb;無 calendar 單估×0.69「勿作終判」);`metrics` 手寫 Spearman、`effective_t_hac` Newey-West、`deflated_sharpe` Bailey-LdP。
**deflation.py(SSOT 防年化-units bug)**:`√(T−1)` 施年化 SR 膨脹 z≈√ppy(+14pp);deflated_ann=haircut×√ppy=**DISPLAY-ONLY**。**兩層保守-N EMPIRICALLY VERIFIED**(--horizon 120):n_fam=8→DSR 95.8% PASS / n_all=16→93.6% FAIL → 跨越取保守 → **未確立**。⚠ **操作 N=16**(trial_ledger row count 含 sample_since)非 SOP-strict DISTINCT=8。**靈魂:IC≠可交易、成功=經濟價值**(net=gross−turn×COST_TW=0.00585 #14)。

### 2.5 core / 2.6 audit / 2.7 catalog / 2.8 execution
- **core**:三建表模式(①generic auto ②顯式 DDL bootstrap ③builder 自 DDL)。
- **audit `import_isolation`(#8 命門)= 可執行架構不變式**:`PIPELINE=(features,models,universe,evaluation,ingestion,audit,catalog)`(**排除 core 共用/FORBIDDEN/execution 下游**);`FORBIDDEN=(philosophy,advisor,knowledge)`;`check_isolation()` **四偵測面**:①AST-walk import(submodule 也抓)②字面掃(補 string-SQL,self-exclusion)③反-錯置(resolver 須住 knowledge、不得住 core)④scripts-predict-leak AST-gated。**非對稱:core 只在 literal+placement 掃**(危險是 core 攜帶 resolver→開 pipeline→core→knowledge leak)。本輪 exit 0。reconcile verdict=**VM=0 ∧ EX=0 ∧ not incomplete**(⚠ 第一版漏第三 clause)。
- **catalog**:optimal_mode 純函式;`build_catalog --db-only`(token 過期對齊 catalog↔DB)。
- **execution**:risk_control DD/cap/turnover 閾值全從 risk_policy 表(#29b),複用 portfolio.drawdown_series;唯讀 advisory 絕不下單;⚠ **不在 PIPELINE(下游 overlay)**。

### 2.9-2.16 半-2(顧問/知識/服務,第一版幾乎空白)
- **knowledge(11 模組)**:`textnorm` 契約 SSOT(NFC、**無繁簡轉**、zh 逐字+jieba HMM=False、手刻 Porter 零 nltk;⚠ **jieba>=0.42.1 是 floor 非 pin**→determinism 未機械強制、「pinned」aspirational);`corpus.clean_work_sql`=review_flag=false ∧ corpus_class='literary'(NULL fail-closed);schema #1 閘實名 `chk_itext_source_type`(⚠ 第一版誤命名 chk_item_text_no_ai_generated);`knowledge_lexicon.license` **public_domain-ONLY**(比 item_text 更嚴、無 CC);`concept_graph.py` **zero importers unwired**(build-vs-integration gap)。三層 DB-driven 引擎住 scripts。
- **philosophy**:`framework.DDL` **9 表**(⚠ 非 6、docstring stale);**假說非真理刻進 schema**:`principle_factor_map.direction`(文獻假說)vs `validated_ic`(NULLable augur 回填)+`status DEFAULT 'untested'`;#1=CHECK(source/work <>'ai_generated');**idempotent upsert NEVER blanket DELETE**(下游 FK 掛住)。
- **advisor(11 模組)**:`advise.advise()`=**唯一編排出口**;漏斗 retrieve→relevance 過濾→translate(fail-closed)→白名單路→honesty 3-tier→payload-type dispatch→guard 鏈(guard/guard_knowledge/attribution/empty/definition 五閘 fail-closed)。**llm_fn 本機限定(v1.37.0 code-verified)**;⚠ advise.py:9「可接 Claude API」docstring stale vs 治權。**D4b 確定性 picks 注入**(qwen3:8b 幻覺→picks 由 payload ground-truth `_render_picks_table` 注入、LLM 只寫 caveat)。
- **RBAC/identity/access(第一版=0)**:`identity` pbkdf2 240k + constant-time(破 user-enum)+ 12h TTL fail-closed;`access.resolve_allowed_domains` 3-state、**任何 exception→(False,∅) 絕不 None=ALL**、**刻意住 knowledge/ 非 core/**;X-Augur-Internal+Session→scope。表 app_user/session/user_group/group_domain_grant。
- **distillation(第一版=0)**:advisor_distill_{context,questions,teacher,validate} S1-S5 self-QA、界線 A/B/C、distill artifacts 從 predict role REVOKE。
- **revalidation harness**:`run_revalidation_cycle` #8-gate→revalidate→verdict→alert;**兩軌三態判停**(Track A DSR 絕對=annotate-only NEVER-stop、Track B 相對衰減;三態 deploying/suspected/confirmed;判停=建議人決定永不自動下架)。LIVE:2 models/688 preds/105 ledger/4 baselines/verdict=deploying_unestablished。
- **serving(3 server 全 127.0.0.1)**:browser→serve_chat_ui:8090(proxy+「+」attach/ingest)→serve_advisor_openai:8399(OpenAI-compat 殼)→advise()→Ollama qwen3:8b:11434;admin serve_admin_console:8500。Mode A(ingest KB、license CHECK gated)vs Mode B(attach for-turn、bypass whitelist 仍 verify_verbatim)。
- **knowledge 引擎**:`acquire_knowledge`(**13 adapters**、adapter_config JSONB `_walk()` dot-path、新域=INSERT 一列零碼 #29b);`promote`(EXTID dedup、_year 容 BC);`harvest`=BATCH DRIVER(subprocess-orchestrate、擁 DDL 單一住所、pace 在 harvest 非 acquire、governance gate JOIN domain_map)。

---

## 3. 跨系統 meta-patterns(建構房規)
1. **SINGLE-ORCHESTRATION-EXIT**:每子系統恰一組合根、薄 CLI funnel through、零第二 orchestrator(advise/panel.build_panel/run_ladder/build_universe)。
2. **DOUBLE-GATE 縱深防禦**:isolation AST-gate **+** DB-role dynamic-gate(setup_predict_role 阻 dynamic-SQL bypass);finmind 兩把鎖;guard 雙數字源;revalidation 兩軌。
3. **FAIL-CLOSED at trust boundaries**:access→(False,∅);identity→None;oai_compat default deny;#8 gate abort;corpus NULL 不納。
4. **每 operational 閾值住 DB 表(#29b)**:risk_policy/judgestop_threshold/knowledge_source/topic_alias/finmind ops。
5. **Builder-owns-DDL(模式③)vs Explicit-migrate(~13 migrate_*_ddl.py)**:raw/feature/universe 前者;serving/harness/RBAC/risk/prediction 後者。
6. **純 kernel + I/O orchestrator 分離**(reconcile.compare/catalog.optimal_mode/portfolio.build_long_portfolio 純函式)。
7. **LLM-ceiling→mechanical-workaround**(確定性 picks 注入);**provisioned-but-not-wired 誠實 gap**(concept_graph/qdrant_sync_state);**literal-duplicate vs shared-code #12 光譜**(ranker↔baseline 弱同步 vs portfolio 強共享)。

## 4. End-to-End 資料流(一個故事)
RAW(sync→ingest #4→generic_schema→83 raw 表)→ FEATURE(panel.build_panel→feature_values EAV 2.42M)→ UNIVERSE(core_gate→core_universe_asof PIT 12,394)→ MODEL(train_ranker→model_registry 2+prediction_values 688)→ VALIDATE(run_evaluation 無持久表)→ HARNESS(run_revalidation_cycle→baseline 4/ledger 105/verdict)→ **SEAM(唯一 join `payload.build_prediction_payload`:讀 prediction_values+model_registry+TaiwanStockInfo+revalidation_ledger→frozen PredictionPayload)** → SERVE(chat_ui:8090→advisor:8399→Ollama:11434)。**兩半唯一耦合=DB + PredictionPayload;import_isolation 保證單向。**

## 5. 治權→code enforcement wiring
| 法律 | 機械 enforcement | 型態 |
|---|---|---|
| #1 零幻像 | philosophy_source/work CHECK<>'ai_generated' · knowledge chk_itext_source_type · generic_schema _coerce 原字串 cast | DB CHECK+型別 |
| #8 靜態 | import_isolation.check_isolation() 四面(本輪[]) · test 當 SSOT | AST+字面 |
| #8 動態 | setup_predict_role role augur_predict REVOKE 素養層/GRANT predict(LIVE) | DB role |
| #8 timing | release_lag 發布日 · registry.latest asof≤ PIT · walkforward 62td/禁252 | 純函式閘 |
| #12 no dual-track | canonical_features 只讀 feature_values · portfolio live≡backtest 共享 · deflation SSOT | 共享碼 |
| #15 誠實 | reconcile VM=0∧EX=0∧not incomplete · deflation 兩層保守-N · 判停=建議 | 三-clause 閘 |
| #29b 資料非碼 | risk_policy/judgestop/knowledge_source/adapter_config JSONB | DB 表 |
| owned_local | chk_itext_access_scope IN(public,local_private) · llm_fn 本機限定 v1.37.0 | DB CHECK+治權 |

## 6. 關鍵常數/不變式(記住)
限速:MIN_INTERVAL 0.9s · QUOTA_HEADROOM 200 · QUOTA_POLL 150s · QUOTA_COOLDOWN 1800 · _RETRY_STATUS 含 402 · 422 不 retry(留 enum-probe)。成本:COST_TW 0.00585。驗證:_FEATURE_LAG_TD 62 · _H_FORBIDDEN 252 · feats_hash sha256(sorted)[:16] · DSR per-period 保守 N=16 · GBDT_SEEDS (42,43,44) 中位/Ridge 確定性。特徵:35(macro 0)· volatility 僅 60d · missing-row 兩 regime · _MAX_STALENESS_DAYS 14。隔離:PIPELINE 7 pkg 禁 import FORBIDDEN(philosophy/advisor/knowledge);core 只 literal+placement 掃。顧問:guard 五閘 · llm_fn 本機 · 確定性 picks 注入 · 誠實閉集二句(變更=憲章)。RBAC:pbkdf2 240k · 12h TTL · resolve→(False,∅) fail-closed。license:lexicon public_domain-only(嚴於 item_text 之公版/CC/owned_local)。as-of 2026-05-31 FREEZE。

## 7. Corrections-to-prior log(對第一版 20260709 之修正,親驗)
1. **feats_hash 防漂移=死碼過度宣稱**(親驗 predict_asof.py:120 cur_feats unused、121 比對 artifact 自身 feats)——實=偵測 artifact↔registry 竄改、非 live 漂移。
2. **per-module 契約非統一**(concentration/panel 純 price_df、phase 4 參、macro 無 compute)。
3. **missing-row 兩 regime**(P 省列 / E 真零),第一版壓平。
4. **quota-gate 120=兩獨立值**(常數 QUOTA_METER_EVERY vs line93 硬寫 120)。
5. **FRED 有效 PK=(series_id,date,realtime_start)**、_RETRY_STATUS **含 402**(第一版漏)。
6. **jieba>=0.42.1 floor 非 pin**、schema 閘實名 `chk_itext_source_type`(非 chk_item_text_no_ai_generated)。
7. **philosophy framework.DDL 9 表非 6**(docstring stale)· reconcile verdict 三-clause · core_gate vs baseline canonical_features 不同 · 完整度閘=可算組合數(資料驅動非 len×len)。
8. **版本錨**:憲章 v1.39.0 / CLAUDE v1.22(第一版 stale v1.38.0/v1.21)。

---

**方法論**:ultracode 20-agent pipeline(DeepRead×9→對抗驗證×9 懷疑者 re-read code+run tools→完整性 critic→synthesis)+ 主作者親驗承重修正(feats_hash 死碼 ✅ / philosophy 9 表 ✅ / isolation exit 0 ✅)。此為 code-verified v2、supersede 同日第一版;對應 memory `augur-construction-map`。
