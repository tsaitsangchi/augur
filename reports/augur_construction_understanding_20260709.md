# Augur 建構作法完整理解(How augur is constructed)

**日期**:2026-07-09 ｜ **性質**:全專案深讀後之建構理解(9 子系統平行深讀 src+scripts+docs+tests 全文合成)
**範圍**:src/augur ~70 模組(9,565 行)· scripts ~110 支(17,156 行)· docs 治權 4 檔 · tests 16 支 · reports 108
**用途**:記住「此專案怎麼建構的」——架構分層、建構模式/慣例、設計理由、關鍵不變式、跨層接線

---

## 0. 三十秒:augur 是什麼 × 建構脊椎

augur =「**觀兆者**」:clean-room、**只用真實資料誠實預測台股相對強弱**(誰相對強、非絕對漲跌)+ 橫切「**博學投資顧問**」素養層。建構脊椎兩軸貫穿每一層:

- **WHY 軸 = 三個敵人**:① 假資料(#1 零 AI 幻像)· ② 偷看未來(#8 anti-leakage)· ③ 自我欺騙(#15 誠實)。三敵 ↔ 三基石法律。
- **HOW 軸 = 管線**:`raw → feature → universe → model → validate` + 橫切(core / audit / catalog / philosophy / knowledge / advisor)。每條法律/測試/層 = (敵人 × 管線層)之對映。

**核心建構信念**:把三敵零容忍**從口號變成機械不變式**——用 schema/型別/封閉集/AST 稽核/正則閘/CHECK 約束**結構性封死**,不靠自律。

---

## 1. 治權脊椎(建構的最高依據、SSOT 分層防漂移 #12)

- **靈魂**(系統核心思想 v1.5.0)= WHAT/WHY(精神);**原則精華**(v1.8.0)= 不可違反 20 條法律全文(WHAT|WHY|ENFORCE 三元組,可證偽可執行);**憲章**(v1.38.0)= HOW(架構分層+12-PHASE 維運+升版規則+命名慣例),**只承載框架、交叉引用方法論報告、拒複述**(anti-drift);**方法論報告**= 詳法(feature_discovery_methodology / sop_master)。
- **SSOT 一概念一權威家**:憲章不複述法律(只索引原則精華)、修訂歷程只記現行法(3 行體例,棄 stock_backend「255 treaty 累積病」)。故**原則精華在憲章 ~30 版間維持 v1.7.1,唯 FREEZE 屬實質法律擴展才首次連動升 v1.8.0**。
- **治權→code 接線**:隔離不變式住 `audit/import_isolation.py`、被 `tests/test_philosophy_isolation.py` 當 SSOT import;命名慣例(library=領域名詞、CLI=動作動詞)、標頭慣例(🎯 docstring+守原則行+指令矩陣)全治權明訂。
- **現行版本**:靈魂 v1.5.0 / 原則精華 v1.8.0 / 憲章 v1.38.0 / CLAUDE v1.21。as-of 2026-05-31 = 治權參數 + 全系統 FREEZE(develop-on-frozen-snapshot)。

## 2. 預測管線 raw→feature→universe→model→validate(怎麼建)

### 2.1 raw 層(ingestion + core)— 真實 API → DB,零幻像
- **嚴格關注點分層、SSOT per 概念**:`sync`(排程)→ `ingest`(guard+audit)→ `generic_schema`(型別/PK/DDL/upsert)→ `db`(transaction)→ PostgreSQL;`finmind`/`fred` 為葉端 fetch client 只回 `list[dict]`。`core/config.py` 是唯一 .env 讀者(DB_PARAMS/token)。
- **FinMind 三層限速**(`_protected_get` 每 attempt 依序):① `_quota_gate` 主動額度閘(每 120 call 問權威錶 /user_info、撞上限前全 worker 一起停)② `_pace`(MIN_INTERVAL=0.9s、鎖內佔 slot 鎖外睡→**start-rate 受 pace 非 concurrency 綁**)③ 反應式重試(403→固定 QUOTA_COOLDOWN=1800s 不風暴、429/5xx→honor retry_after 指數退避)。**驗證與全史走同一 fetch 同防護**。
- **資料驅動零 hardcode**:dataset 全集靠 **422-enum probe**(送非法 dataset→FinMind 422 回合法 enum)非寫死;`generic_schema` 型別/PK 全推斷(infer_schema 值→PG 型、detect_keys 貪婪最小 PK、ensure_table SAVEPOINT 容併發首建、只增不減 widen)。
- **零幻像由建構保證**:client 回 API 值逐字;唯一轉換是「無值」映射(FRED `.`→None、`_NULL` placeholder→NULL);**source-pure「算不出→省列不偽造」延到 feature 層,raw 層只鏡射 API**。
- **#8 anti-leakage 在建構裡**:FRED vintage PK 強制 `(date,realtime_start)` 防多 vintage 塌陷、`_fred_pk_ok` 硬擋;FinMind 公告欄(Dividend.AnnouncementDate/MonthRevenue.create_time…)因 #2 保全欄逐字保留供 feature 層 as-of。
- ⚠ `FULL_START='1990-01-01'` 僅 FinMind backward-probe 下界、**非全史保證**(API 於 start_date 截斷,GoldPrice 真起點 1979 曾被夾)。

### 2.2 feature 層(features/*)— source-pure、missing-row 紀律
- **統一 per-module 契約**:每支 `compute_*_features(cur, sid, panel_date)` 回 `{feature: value}` 只含有限值;`panel.build_panel` 為組合根 fan-out 各模組 `feats.update(...)`。
- **missing-row 紀律處處一致**:`{k: float(v) for k,v in out.items() if v is not None and np.isfinite(v)}` + inline 範圍檢查(-1≤ratio≤1…)先剔不合理;**算不出的特徵永不成 key = feature_values 缺列,零 fake/zero-fill**。
- **調整價單一基礎**(TaiwanStockPriceAdj):除息缺口非真報酬、且調整表無 close=0 停牌哨兵(raw 有 28 萬)→自動移停牌日防 252 窗被 lo=0 污染。這是 #8/#1 正確性決策。
- **#8 命門 release_lag**:發布日 gate(REVENUE_DAY=15、FIN_LAG_QUARTER=45、FIN_LAG_ANNUAL=90)——財報/月營收只在法定公告後才可見,防用未公告資料。三鏡頭(第一性/八二/康波)為特徵假說旋轉視角。

### 2.3 universe 層(core_gate)— 核心股四道閘
- 候選空間(排 ETF 505+污染)→ 完整度閘(每 panel 全 canonical 特徵齊)→ 流動性 P25 → conditional;`core_universe_asof` 為 **point-in-time(消 survivorship #8)**。

### 2.4 model+validate 層(models + evaluation)— predict then validate honestly
- **建構模式=「evaluation 是數學 SSOT + models 薄殼」雙軌零漂移**:`baseline.canonical_features`(HAVING count(DISTINCT panel)=全 → 維度資料驅動)/`_panel_matrix`/`_asof_stocks`/`_fold_xy` 為共用;`models/ranker.py`(RankRidge=StandardScaler+Ridge 確定性、RankGBDT=LightGBM 多seed)為生產薄殼。
- **誠實驗證四關**:purged walk-forward(`walkforward.splits`,`_FEATURE_LAG_TD=62` embargo #8、`_H_FORBIDDEN=252` 硬擋)→ rank IC + **HAC `effective_t_hac`**(重疊窗自相關高估→禁裸 iid、審查 G8)→ 經濟回測(`portfolio.run_backtest` net=gross−turn×cost、cost 0.00585 台股 round-trip、#14)→ **deflation DSR**(Bailey-LdP,**per-period 命門**非年化、`trial_ledger` N 機械 count DISTINCT 禁人手)。
- `forward_returns` on-the-fly 由 `label.py` 從 TaiwanStockPriceAdj 算(**無 forward_returns 表**);`feats_hash`=sha256(sorted feats)[:16] order-independent(重排不失效、換特徵集失效)。**靈魂:IC 撐住≠可交易、成功定義是經濟價值**。

## 3. 橫切層(怎麼建)

### 3.1 core(共用 infra)= config/db/generic_schema/schema
- 見 2.1;三種建表模式:① generic 自動 schema(API 表)② 明確 DDL bootstrap(infra log,PHASE 1)③ builder 自 DDL(feature_/core_ 計算表)。

### 3.2 audit(anti-leakage 稽核)= 把治權變機械閘
- **建構慣元:純計算 kernel + I/O orchestrator 分離**(reconcile.compare / risk_control.dd_circuit / catalog.optimal_mode 皆純函式,外殼才 I/O)。
- **import_isolation(#8 命門)三偵測面**:AST import-walk + literal 掃描(補 raw SQL string 繞道)+ resolver 定位;`PIPELINE=(features,models,universe,evaluation,ingestion,audit,catalog)` **禁 import** `FORBIDDEN=(augur.philosophy,advisor,knowledge)`——素養層物理隔離、永不入預測。
- reconcile(#7 對帳 API vs DB、attestation=value_mismatch=0∧無多列)、feature_diagnostics(五鏡 #11)、field_correlation(raw 探索)。

### 3.3 execution(風控 overlay)= 部署時決策支援
- `risk_control.apply_overlay`:DD 熔斷/position cap/turnover budget;**複用鐵律**——`_turnover=portfolio._turnover`、`drawdown_series` 直接呼叫 portfolio(DD 算法零重造 #12)。系統建議、人決策、不下單。

### 3.4 catalog(dataset 抓法治理)
- `optimal_mode(c)` 純推導(catalog raw 欄→(mode,est_calls))被 sync 消費;官方 datasets.md 驅動去硬編。

### 3.5 knowledge(素養擷取管線)= 11 支 library 模組
- **三層 DB-driven 管線**:`knowledge_source`(registry:adapter+query_template+adapter_config JSONB)→ `acquire`(通用引擎 adapter dispatch)→ `knowledge_staging`(payload+provenance pending)→ `promote`(mapper per entity_type 冪等寫正式表)。**擴新領域=INSERT 一列 registry 零改碼**(#29b)。
- **三敵結構性封死**:license 白名單三處硬同步(`corpus.LICENSE_WHITELIST`=DB CHECK=`webupload.LICENSES`,('public_domain','cc-by','cc-by-sa','cc0','owned_local'))、lexicon 定義**一律逐字原文子串**(parser 只段切絕不改寫摘要)、`chk_item_text_no_ai_generated` CHECK。
- **建構慣元**:述詞 SSOT(`corpus.clean_item_sql` 回 (frag,params) 消手工位置對齊)、契約函式(`textnorm.tokenize/norm_headword` 同輸入同輸出保 JOIN、Porter 手寫零依賴、jieba HMM=False 延遲載入)、六同型 parser(`lexicon_parsers` 每源 parse_<source>→(entries,failed) 共用 LexEntry+flush)。`vectorindex`=pgvector-SSOT+可拋棄外部索引抽象(stats pk 枚舉自驗)。

### 3.6 philosophy + advisor(顧問層)= 「有紀律顧問非自動駕駛」對話端落地
- **philosophy 框架**:真實大師文獻→「可證偽因子假說」(原則→augur 特徵→預期 IC direction+來源)落 6 表;**策展常數 SEED + 冪等 upsert 引擎**(先 SELECT 補缺、**避 blanket DELETE**,因下游掛 stock_philosophy_tag/factor_map validated_ic/work→chunk);明文從屬三敵(哲學=假說非真兆、DB CHECK 擋 AI 生成、validated_ic 須 augur 自證回填)。
- **advisor 三通道 + 抽象界面 + 生成後機械閘**:數字通道(唯讀 PredictionPayload)⊕ 引文通道(逐字檢索)⊕ 定義通道(lexicon)組 prompt → 抽象 `llm_fn`(**v1.37.0 本機限定**、換 LLM=改一行)→ **guard 五閘 fail-closed**:① 引號≥8字須逐字∈citation ② 顯著小數/IC/Sharpe∈payload.numbers() ③ 無未來/保證語 #8 ④ 逆向不翻轉 ⑤ 股名須與 payload 相容;外加 guard_attribution(裸出處捏造)、guard_empty_retrieval(檢索空必回誠實閉集二句)、guard_definition(定義附 source_locator)。
- **核心信念:弱本機 LLM 不可信**(幻覺股名/數字/引文/出處)→ **逐字原文與確定性 picks 由系統注入、LLM 只負責它可靠的白話解讀**、一切輸出過 guard;誠實閉集變更=憲章判準(執行層不得自改)。
- **隔離不變式**:advisor 對預測/哲學表**唯讀零寫**;payload.build_prediction_payload 讀 prediction_values/model_registry/revalidation_* 唯讀。

## 4. Ops 層(scripts + services、怎麼跑)

- **scripts=薄 CLI 組合根**(#29,~110 支):標頭(🎯 docstring+守原則行+執行指令矩陣)、`import _bootstrap` 首行(#29a 個別可執行、任何 cwd)、安全無參數(印矩陣+唯讀統計、放量才 --run/--apply、不裸 traceback)、單一 DB 連線。**複用鐵律**:train/predict/revalidate/deflation 全共用同一 evaluation helper=零雙軌漂移。
- **預測鏈**:full_market_sync/sync_macro/daily_maintenance → build_catalog/reconcile_audit → build_feature_panel → build_core_universe → run_evaluation/run_economic_eval → train_ranker → predict_asof → revalidate/revalidate_baseline/revalidate_verdict/run_revalidation_cycle → deflate_*/survivorship_economic_verdict。
- **知識鏈**:acquire→harvest→promote(三層引擎)→ fetch_oa_fulltext→build_sentences→build_concordance→build_lexicon→embed_knowledge(至可檢索終態);migrate_*.py DDL 遷移慣例。
- **三服務(stdlib HTTP、systemd/手動)**:advisor OpenAI 相容殼 :8399(薄殼包 guard 編排)、chat Web UI :8090(proxy+檔案入庫)、admin 控制台 :8500(RBAC 觸發 harvest/ingest 背景工)。

## 5. 反覆出現的建構模式(meta-patterns)

1. **純 kernel + I/O orchestrator 分離**(全專案):compare/dd_circuit/optimal_mode/tokenize 純函式,外殼才 I/O → 可測、可複用。
2. **SSOT 複用鐵律 #12**:一算法一住所(drawdown_series/_turnover/canonical_features/deflated_floor/COST 0.00585 口徑),offline 驗證與 live 預測共用同路徑=零雙軌漂移。
3. **資料驅動零 hardcode**:generic_schema 推斷型別/PK、422-enum probe、knowledge_source registry(INSERT 一列=新領域)、missing-row(算不出省列)。
4. **三敵機械化不變式**(非自律):license 白名單三同步+DB CHECK、import_isolation AST 閘、guard 五正則閘、trial_ledger N 機械 count、per-period DSR、發布日 release_lag gate。
5. **fail-closed 漏斗**:advise() 層層 verify_verbatim→relevance→translate→分派→guard;缺資料回誠實閉集非杜撰;下限恆≥現行。
6. **冪等 resume-safe**:ON CONFLICT DO UPDATE、SAVEPOINT、游標表(knowledge_build_meta)、小 transaction 批 commit、DB-driven resume floor。
7. **治權標頭/命名慣例**:library=領域名詞(finmind/reconcile/core_gate)、CLI=動作動詞(full_market_sync/build_catalog);標頭 30 秒看懂。

## 6. 關鍵不變式/常數(記住)

| 域 | 常數/不變式 |
|---|---|
| 限速 | MIN_INTERVAL=0.9s · QUOTA_COOLDOWN=1800 · QUOTA_HEADROOM=200 · PER_STOCK_WORKERS=32 · 403→固定冷卻不風暴 |
| 成本 | COST_TW=**0.00585**(2×0.1425%費+0.3%稅 round-trip、SSOT 口徑;portfolio default 0.0 絕不作終判) |
| 驗證 | `_FEATURE_LAG_TD=62` embargo · `_H_FORBIDDEN=252` 硬擋 · HORIZONS=(5,20,60,252) · GBDT_SEEDS=(42,43,44) 中位/Ridge 確定性 · trial_ledger N=count DISTINCT(model,top_frac,weight,feats_hash,cost,horizon) 機械 · DSR per-period 命門 |
| 特徵 | MAX_STALE_CALENDAR_DAYS=45 · release_lag(15/45/90)· 調整價單一基礎 · missing-row 不 fake · feats_hash sha256 sorted[:16] |
| 隔離 | PIPELINE=(features,models,universe,evaluation,ingestion,audit,catalog)禁 import FORBIDDEN=(philosophy,advisor,knowledge) |
| 顧問 | guard 五閘 fail-closed · llm_fn 本機限定(v1.37.0)· 確定性 picks 注入 · 誠實閉集二句(變更=憲章)· advisor 唯讀零寫 |
| license | ('public_domain','cc-by','cc-by-sa','cc0','owned_local')三處硬同步 · owned_local⇒access_scope=local_private |
| 資料 | as-of=2026-05-31(治權參數+全系統 FREEZE develop-on-frozen-snapshot)· FULL_START 1990 非全史保證 |

---

**一句話**:augur 的建構作法 = 「**治權定 WHY/法律 → 嚴格分層 SSOT 定 HOW → 三敵零容忍全部結構性機械化(schema/AST/正則/CHECK/純函式複用)→ 資料驅動零 hardcode → fail-closed 冪等**」;每一行 code 都能溯回 (敵人 × 管線層 × 某條治權)。
