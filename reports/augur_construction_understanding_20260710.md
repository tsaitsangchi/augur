augur 建構理解報告 v3（定稿）

> 版本：v3-final（2026-07-10）｜性質：**理解報告**（非計畫）｜取代：`reports/augur_construction_understanding_20260709.md`（v2 過度壓縮、半-2 幾近空白）
> 讀法：這份報告回答「**這個專案是怎麼建的**」。每個承重宣稱都附 `file:line` 或表名/常數值可溯源（原則精華 #10）。凡經對抗驗證判 REFUTED / 過度宣稱者，本報告一律採**驗證後的正確版**、並在第 11 節留摘要留痕（#15 誠實）。死碼、stale docstring、provisioned-but-unwired（已備位但未接線）、docstring-sourced 未複現數字皆據實標明。
> 目標讀者：一位懂量化的工程師，30–40 分鐘讀完即懂全系統建構脈絡。

---

## 0. 三十秒核心框架

augur 是一套「**只用真實資料、誠實預測台股相對強弱**」的 source-pure 量化系統，外加一個「**誠實博學投資顧問**」。source-pure＝所有落地值都能溯源到真實 API / DB / 程式輸出，不含推估補值。

**兩個半系統**：

- **半-1 量化預測管線**：`raw → feature → universe → model → validate`，加上橫切基礎層 `core`（DB/建表/密鑰）、`audit`（稽核/對帳）、`catalog`（dataset 元資料登錄）、`execution`（部署後風控 overlay）。
- **半-2 顧問／知識層**：`philosophy`（哲學素養）、`knowledge`（三部曲知識管線）、`advisor`（顧問對話前端）＋三個 stdlib web server。

**兩條、且僅兩條耦合線**把兩半接起來：

1. **PostgreSQL 當 message bus**——兩半共用同一個 DB，但預測管線寫 `feature_values / core_universe_asof / prediction_values`，顧問層唯讀這些表；資料靠表流動，不靠函式呼叫跨半。
2. **`PredictionPayload`（frozen 唯讀 dataclass）**——顧問層要引用真實預測數字時，唯一入口是這個凍結 dataclass（`advisor/payload.py:20`），拿到的是不可變快照，改不了預測。

**單向依賴由機械強制**：`augur.audit.import_isolation.check_isolation()`（`import_isolation.py:160`）用 AST 靜態稽核，保證預測 7 個 package **零 import** 素養層前綴（`augur.philosophy / augur.advisor / augur.knowledge`）。實跑零違規。

**三個敵人 × 管線** 是全系統的組織原理，每一條紀律都在防這三個：

| 敵人 | 命門原則 | 機械落地 |
|---|---|---|
| ① 假資料（AI 幻像） | #1 零幻像 | `guard.py` 數字白名單、`core_gate.py` 純完整度、DB CHECK `<>'ai_generated'` |
| ② 偷看未來（look-ahead） | #8 anti-leakage | `release_lag.py` 發布日 gate、`walkforward.splits` embargo、`import_isolation` 單向依賴 |
| ③ 自我欺騙（不誠實） | #15 誠實 out-of-sample | `metrics.effective_t_hac` HAC 去相關、`deflation` Deflated Sharpe、缺列不補 |

三條基石**一條守一敵**：#1 / #8 / #15。20 條原則全部在防這三個。

---

## 0.1 術語與代碼速覽

本報告與 code 反覆出現的 shorthand，一次講清（後文首次出現不再重述）：

- **三敵人**：①假資料 ②偷看未來 ③自我欺騙。
- **三鏡頭**（特徵發現方法論的三個思想根源鏡頭）：**第一性原理 / 八二（Pareto 80/20 集中律）/ 康波（Kondratieff 長波，40-60 年經濟長週期）**。三者都是**假說鏡頭、非真兆**——採不採用由 out-of-sample + 經濟價值裁決，特定數字（0.80/0.20、40-60 年）**不得入 feature 公式**（#9）。SSOT＝`reports/augur_feature_discovery_methodology_20260626.md` §四。
- **四道漏斗**：特徵候選入生產前方法論 §四 的四道遞進篩選關卡（as-of 口徑、去相關 Eff-t、多 seed 多因子增量貢獻、經濟價值終關），任一不過即淘汰。各關卡→工具對映見該報告 §四。
- **五鏡合判**：訓練前特徵去留的五個診斷鏡頭合判（見 §3.7 `five_mirror`）。
- **四鏡對抗驗證**：顧問 relevance 閘的四路對抗式相關度判定（把「命中但不相關」判成實質空檢索→誠實 decline，見 §4.3）。
- **G8**：特徵審查清單第 G8 條——「IC 顯著性禁裸用 iid `effective_t`（重疊 label 窗高估）」。
- **DP7 GATE**：蒸餾題生成的 out-of-corpus 佔比下界（≥55%）關卡。
- **R2 架構**：guard fail 的安全架構（2026-07-04 起）——「LLM 杜撰內容不進回覆本體」，取代舊的「死比對誠實句字串」。
- **SOP-A / SOP-E**：標準作業程序。SOP-A＝換嵌入模型→走新世代重嵌；SOP-E＝換 jieba（textnorm）版本→升 `TEXTNORM_VER` 重建 concordance。
- **界線 A/B/C**（蒸餾隔離界線）：界線-A＝蒸餾產物（`advisor_distill_*`）零回流預測管線；界線-B＝context（真兆檢索）與 target_response（teacher 示範）DB 分欄；界線-C＝蒸餾 staging 專用 super scope 復現失敗路徑之隔離（本次未逐字核實其憲章定義，故不臆測細節）。
- **tests 情境碼 N5/N6/N8/M2/T1-a**：顧問對話回歸測試的內部案例編號（各對應一種對話族回歸：如 M2＝注入 retrieve_fn 一律後驗 verify_verbatim、T1-a＝離題 decline）。
- **P0/P3/P5/P8/S1-S7/D4b**：計畫階段/子系統代號（P0 隔離測試、P3 混合檢索、S1-S7 蒸餾與知識管線步、D4b 弱模型繞道等），出現處即點明。

---

## 1. 治權脊椎：doctrine 如何組織與防漂移

augur 的最上層不是 code，是四份**治權文件**。它們不是可執行程式，而是所有 code/架構/決策從中長出的 SSOT（single source of truth，單一權威來源）。四檔分層各司一職、互引不複述：

| 層 | 檔案 | 職責 | 版本 |
|---|---|---|---|
| 靈魂（WHAT/WHY） | `docs/系統核心思想_v1.5.0.md` | 一句話定義＋三敵人表＋北極星 3 問＋世界觀，讀完懂 80% | v1.5.0 |
| 原則精華（法律全文 SSOT） | `docs/原則精華_v1.8.0.md` | 20 條「不可違反法律」，每條 WHAT｜WHY｜ENFORCE 三元組 | v1.8.0 |
| 憲章（HOW 框架） | `docs/系統架構大憲章_v1.39.0.md` | 把 20 法律 map 到三敵×管線＋12-PHASE 維運＋升版規則 | v1.39.0 |
| CLAUDE（AI 工具規則） | `CLAUDE.md` | 「如何用 AI 工具編輯本專案」的短半衰期協作規則 | v1.22 |

### 1.1 憲章的雙軸脊椎與六部結構

憲章（**360 行**〔wc -l〕；含尾行 Read 顯 361）以「**三敵人（WHY 軸）× 管線（HOW 軸）**」組織，六部各司一職：第一部系統本質（`treaty:12`，含 v1.26.0「PostgreSQL＝唯一真相來源」總綱 `:26`）；第二部三個敵人＋防線地圖表（`:38`、地圖表 `:62`，把 20 原則釘到每個管線層）；第三部管線分層（`:81`，承載特徵發現方法論 `:103` 與 philosophy/knowledge/advisor 橫切層 `:138`）；第四部 20 條原則**純索引表**（`:172`，明文「法律全文以原則精華為 SSOT、本憲章不改寫」避免漂移）；第五部 12-PHASE 維運矩陣（`:217`，見 §2.4）；第六部升版規則（`:253`，含計畫先行 `:261` / 計畫完整性 `:268`）。三附錄：A 經驗結論（**刻意留空**，#15 不搬未在 Augur 重跑的數字）、B 考古索引（stock_backend 只查不搬）、C 理論定位（外部背書＋四項自陳缺口，見 §1.5）。修訂歷程 v1.0.0→v1.39.0 共 **41 版**（`grep -cE '^\| v[0-9]'`＝41）。

### 1.2 SSOT 三分與防漂移機制

- **一概念一權威家**：靈魂只住核心思想、法律全文只住原則精華、架構/維運只住憲章。憲章第四部只 INDEX 法律、明文「不改寫全文避免漂移」——**不能拿憲章第四部當法律 SSOT**。
- **升版連動有明確判準**：絕大多數版本是「僅憲章升版、原則精華維持不動」（架構/維運/方法承載 ≠ 新法律）；只有**新增/改判準法律**才連動升原則精華。v1.38.0 FREEZE 是首次連動原則精華內容升版（v1.7.1→v1.8.0）。誤判會讓治權檔版本不一致。
- **條號非連續是刻意設計**：按「新增順序編、分類歸區」，故 A 資料紀律〔#1-7,#17,#18〕· B 建模〔#8-12〕· C 風險治理〔#13-15,#19〕· D 開發協作〔#16,#20〕跳號。新增法律只 append，條號穩定。讀者若期待連續會誤判「缺條」。

### 1.3 as-of / FREEZE 凍結日

全系統以 **2026-05-31** 為資料完整/凍結基準（v1.9.1 立 as-of、v1.38.0 擴為 FREEZE「develop-on-frozen-snapshot」）。

**重要澄清（親驗修正）**：2026-05-31 這個字串 hardcode 只活在 `payload.py:76`（`empty_payload()` 建的 `KnowledgePayload`）與 demo/一般問答 payload。**生產選股路徑** `build_prediction_payload():159-164` 的 `as_of` 取自 DB `max(panel_date)`、**非 hardcode**。所以「as-of hardcoded 於 payload.py、改它須改 code」只對 demo 路徑為真；FREEZE 凍結本質是 doctrine 約定，不是全由常數強制。（reader 原將 `:61` 標為 KnowledgePayload 亦錯——`:61` 是 `example_payload()` 建的 `PredictionPayload`。）

### 1.4 CLAUDE.md 的三大執行哲學

- **clean-room（#16/#17）**：只依 5 治權檔＋自身 schema＋live API，**零 stock_backend 回流**（不讀、不參考、不移植其 code/資料/報告/數字）。
- **plan-first（#20，v1.39.0 強化）**：一切規劃類工作先產計畫報告＋用戶拍板，計畫須附 table schema＋python 程式規畫段。
- **最小 usage（#28）＋執行/理解二分**：裁決句「搞錯會不會沉默污染下游？會→理解軸窮盡；僅慢→執行軸省」。理解層再深仍不鬆三敵零容忍。

**版本漂移陷阱（親驗）**：本任務 system-reminder 注入的 CLAUDE.md 是**舊 v1.18**，但 on-disk 實檔是 **v1.22**（README 亦引 v1.22）。務必以 on-disk 為準。

### 1.5 憲章附錄 C：自陳的四項理論缺口

憲章附錄 C（理論定位，`treaty:297`）除了給外部背書（Screaming Architecture / Hexagonal / Medallion / ML-leakage 防治），還**誠實揭露四項「理論指出、現分層夠用故暫緩」的 provisioned-but-未實作缺口**（#15 揭露而非粉飾）：① 正式 ports/adapters（Hexagonal）介面（現分層依賴已夠用）；② data-contract schema 版本化；③ as-of/bitemporal 形式化（vintage 表）；④ train/serve 一致性（俟真的上 serving 才需）。這四項是 by-design 的 open debt，第 10 節未來債清單一併列入。

---

## 2. 系統全景

### 2.1 兩半架構與單向依賴

- **預測 7 package**（受隔離約束）：`features / models / universe / evaluation / ingestion / audit / catalog`（`import_isolation.py:31` `PIPELINE`）。
- **素養層 3 前綴**（禁被 import）：`augur.philosophy / augur.advisor / augur.knowledge`（`:33` `FORBIDDEN`）。
- **`core` 刻意不在 PIPELINE**：它是共用地基，不受 AST import 稽核（非對稱設計，見 2.3）。

`check_isolation()`（`:160`）串接四道稽核：(a) `_import_violations`（`:63`，AST-walk 預測 package 的 import 節點比對 FORBIDDEN 前綴）、(b) `_string_ref_violations`（`:88`，字面 substring 掃描，擋「字串拼 SQL 繞過 import」）、(c) `_placement_violations`（`:104`，確認 resolver 住 knowledge、chat_history 住 advisor、core 不含其 API）、(d) `_scripts_predict_leak_violations`（`:129`，只查 import 預測 package 的腳本是否又字面觸及 RBAC/chat）。實跑 `python -m augur.audit.import_isolation` → exit 0、零違規（已驗）。

**enforcement 比憲章文字更廣（親驗）**：憲章 `line 151` 仍點名 `tests/test_philosophy_isolation.py`，但實際邏輯 SSOT 已移入 `audit.import_isolation`（test 只是薄殼委派）。且實際 enforcement 涵蓋 chat-history 隔離、RBAC 字面旁路、scripts 洩漏面、界線-A `advisor_distill_*`（`DISTILL_LITERALS:41`）——憲章文字未完全反映此廣度（輕微 stale）。

### 2.2 PostgreSQL 當 message bus + 唯一耦合 dataclass

兩半只被兩件事接起：DB 表（唯讀 `PredictionPayload`/`KnowledgePayload` 之外，顧問層對預測/知識/哲學表全 SELECT 零寫，僅自家 `chat_session/chat_message` 讀寫且 owner 收窄），與 `advisor/payload.py` 的 frozen dataclass。`PredictionPayload`（`:20`）與 `KnowledgePayload`（`:40`）皆 frozen，攜帶 `.numbers()` 方法（`:27`/`:53`）供 guard 當數字白名單。

### 2.3 縱深防禦：AST 靜態閘 + DB 動態閘（double-gate）

單靠 AST import 稽核擋不到「動態拼 SQL 讀素養表」。故有第二道 **DB 層 GRANT/REVOKE**：`scripts/setup_predict_role.py` 建受限 role `augur_predict`，對素養層 62 表＋`advisor_distill_*` REVOKE、只 GRANT 預測表（`FORBIDDEN_PREFIXES:32` 含 `advisor_distill_`、`apply:85` REVOKE `:100`/GRANT `:103`）。

**重要親驗澄清**：這道 DB 動態閘保護的是「**素養→預測**」單向依賴（預測 role 讀不到素養表）。它**不**阻止 pipeline 讀 `prediction_values` 當特徵——`prediction_values` 本身在 `setup_predict_role.py:39 WRITABLE` 被 GRANT 給 predict role 可讀可寫。「prediction_values 禁被回讀當特徵」僅由 `migrate_prediction_ddl.py:56` 的 DB COMMENT **約定**承載、非機械閘（models 子系統 key_invariant #5 原宣稱「AST+DB GRANT 雙閘強制」經判 **REFUTED**）。

`core` 的非對稱設計：`core` 不在 PIPELINE，故 `_import_violations` 完全不 AST-檢查 core 是否 import FORBIDDEN；core 只受字面掃描（`SCAN_STR` 含 core）＋placement 兩面約束。理論殘留缺口：core 若 `import augur.knowledge` 的某個非敏感命名部分（不含任何 RBAC/CHAT/DISTILL 字面）會四面皆偵測不到——但 core 實際零 import FORBIDDEN（已 grep 驗），此缺口尚未觸發。

### 2.4 12-PHASE 維運矩陣（從零重建脊椎）

憲章第五部（`treaty:217`）不是選單、是**強制序列**：它定義「一台空機器如何從零把整個系統重建出來」的 PHASE 0→11（+子階段 2b），共 **13 列**。三條語意約束（doctrine 約定，非機械閘）：

1. **不可跳 PHASE**：後階段依賴前階段的落地產物（沒有 raw 表就算不了 feature，沒有 feature 就選不了 universe）。
2. **不可改 order**：序列反映真實資料依賴拓撲。
3. **每 PHASE 過 audit gate 才進下一**：每階段以稽核/對帳確認真兆落地，才往下走（呼應 #7 對帳、#15 誠實）。

三種建法澄清（`treaty:237`）——建表不全由 ingestion：① generic auto-schema→API 原始表（無白名單）；② explicit DDL bootstrap→infra log（PHASE 1 最早建）；③ builder 自建 DDL→計算型表（feature/universe/model 各自 PHASE）。

**可驗證的 PHASE 錨點**（其餘逐 PHASE 標籤 SSOT 在憲章第五部，本報告不逐字複述）：PHASE 1＝infra log 表 explicit DDL（最早建）；PHASE 2b＝FRED 總經前置子階段；PHASE 8 ≈ as-of / 完整性判準（`core_universe_asof` 快照落地，`core_gate.py DDL_ASOF`）。第 7.1 節的 end-to-end 故事即這條 PHASE 序列的粗粒度展開（取數→登錄→對帳→特徵→宇宙→訓練→驗證→出單，PHASE 遞增）。

---

## 3. 半-1 逐子系統 HOW-built

### 3.1 ingestion（真實 API → DB 落地）

**▶ 一句話**：把兩個外部真實來源忠實落地成 PostgreSQL 表，全靠單一限速門 + adaptive 探測，零 hardcode 清單、葉端只回 API 原值。

**做什麼**：半-1 最上游取數層，把 FinMind v4 台股全 dataset、FRED/ALFRED 總經的原始列忠實落地成表，不算特徵、不選股。

**關鍵檔案:符號**：`finmind.py`（薄 client＋三層限速）：`_pace:58`、`_quota_gate:84`、`_protected_get:120`、`fetch:161`、`_RETRY_STATUS:53`。`fred.py`：`fetch:38`。`ingest.py`（單來源 orchestrator）：`ingest_finmind:95`、`ingest_fred:116`、`store:133`、`_fred_pk_ok:103`、`is_intraday:51`、`INTRADAY:22`、`OUT_OF_UNIT:34`。`sync.py`（全市場排程引擎）：`sync_finmind_dataset:318`、`_adaptive_sync:359`、`sync_by_date:431`、`_per_stock_sync:174`、`sync_fred:491`、`sync_all:517`、`FULL_START:36`、`PER_STOCK_WORKERS:38`。

**建構作法**：分層薄化＋adaptive 而非 hardcoded。client 層只做「一個 dataset/series → 韌性化 GET → `list[dict]`」，欄名逐字照 API、`"."`→None，落地/建表外包給 `generic_schema`（葉端零 DB 依賴，故可 `ThreadPoolExecutor` 並發）。**三層防護全走單一 `_protected_get`**（fetch/dedicated/list_datasets/translation/datalist 共用），確保「驗證與全史同一門、同一限速」：第 1 層 `_pace`（鎖內預約時槽、鎖外 sleep，thread-safe 維持 start 間隔 ≥ `MIN_INTERVAL`）；第 2 層 `_quota_gate`（每 120 call 問權威錶 `/user_info`，≥limit−200 持 `_quota_lock` 全員暫停）；第 3 層 403 固定冷卻（保險網）。**零 hardcode 清單**：dataset 全集靠送無效 dataset 觸發 422、用 `_DATASET_RE` 解 enum；抓取起點靠對 API 逐年逐月探測。

**不變式（enforced_where）**：
- 所有 FinMind 請求無一例外先 `_quota_gate` 再 `_pace`（`finmind.py:127-128`，六個公開函式一律呼叫 `_protected_get`）。
- 403 一律 `sleep(max(QUOTA_COOLDOWN, ra))`（`finmind.py:145-146`）——**至少 1800s 下界**（非嚴格固定值，親驗修正）；429/5xx 才 `backoff*=2`（僅 `:149` else 分支）。
- 422 **不在** `_RETRY_STATUS`（`:53`）→ `list_datasets` 才拿得到 dataset enum（若列入重試則永遠拿不到）。
- intraday 8 表一律不落地（`ingest.py:97-98` raise、`sync.py:324/439` 前置閘）。
- `fred_series` 恆為 `(series_id,date,realtime_start)` 複合 PK；既有表 PK 不含 realtime_start 即拒落地（`ingest.py:123-127` `_fred_pk_ok` 讀 pg_index），根因是 `generic_schema.ensure_table` PK 首建固定、`require_keys` 對舊表無效。
- FRED 非 vintage 列 `realtime_start`＝觀測日本身（`fred.py:106`，市場當日即知＝正確 PIT）；超單頁寧可 raise 不靜默截斷（`fred.py:97-98`，#15）。
- 抓取失敗（rows is None）記入 failed 帳本、真無資料（`[]`）不記（`sync.py:201-202`）——不記則 resume 只看 max(date) 會成永久空洞。

**治權接線**：#1（葉端只回 API 原值）、#8（FRED vintage 的 realtime_start PIT）、#15（超單頁明失敗）、#17（三層防護 SSOT）、#24（限速）、#27（`MIN_INTERVAL` 逐級試錯）。

**關鍵常數**：`MIN_INTERVAL=0.9`（`:38`，2026-06-20 由 0.7 升）、`QUOTA_COOLDOWN=1800`（`:41`）、`QUOTA_HEADROOM=200`（`:47`）、`PER_STOCK_WORKERS=32`（`:38`）、`FULL_START=1990-01-01`（`sync.py:36`）、`INTRADAY`＝8 表 frozenset、`OUT_OF_UNIT`＝3 表 frozenset（分點/權證/鉅額分點）。

**gotchas**：
- **「兩型 403」是概念區分、非 code 分支**：docstring 把 403 分「額度型」與「IP sustained 型」，但 `finmind.py:145-146` 對所有 403 都同一冷卻，不會偵測 IP 型另行處理。
- **`FULL_START` 最易誤讀**：它只是 backward-search 的查詢下界，不是資料起點保證（API 以 start_date 截斷，GoldPrice 真起點 1979 被截成 1990）；per-stock 真起點是 `_data_era_start` 探得的 API 元年，FRED 用 `start=None` 全史。
- `sync_fred` **刻意不 resume**（`:505` 每次 `start_date=None` 全抓），因為 resume 用 max(date) 起點會漏掉「首抓被 1990 截掉的史」。
- `_data_era_start` 的 fallback 探測種子股號硬編在 `sync.py:143`（reader 標 145，親驗**行號偏移**修正）——但這是探測啟發種子（不入庫），與 #3「資料來源不 hardcode」邊界相容。
- 兩把鎖分離（`_pace_lock` `:55` / `_quota_lock` `:51`），暫停時無死結（worker 都卡在 gate 內、無請求發出）。

**未完成債**：`BACKFILL_DEFERRED = frozenset()`（`ingest.py:42`）為空集的 provisioned-but-unwired 框架；`fetch_dedicated` 在自動 sync 路徑**未被啟用**（唯一觸點 `_fetch_for_store` 之 dedicated 參數無上游傳非空值）；FRED 分頁未支援（靠 limit=100000 夠大）；`MIN_INTERVAL/PER_STOCK_WORKERS` 為「實驗中」操作值。

---

### 3.2 core + catalog（建表 / DB / secrets / 元資料登錄）

**▶ 一句話**：橫切地基——三種建表模式各司其職、數字永不經 float 保精度、catalog「存原料即時重算」把「怎麼抓」持久化成登錄表。

**做什麼**：`config.py`（密鑰唯一住所）、`db.py`（連線/交易 context manager）、`generic_schema.py`（看 API 資料自動推型別建表冪等 upsert）、`schema.py`（explicit DDL 建運維表）；`catalog` 對每 dataset 探測，把元資料持久化成 `dataset_catalog` + `column_catalog`。

**三種建表模式**（全子系統核心設計）：
1. **generic auto-schema**：API 原始表由 `generic_schema.provision_and_upsert:271` 一站式建（`infer_schema:108`→`detect_keys:127`→`ensure_table:188`→`upsert:252`），無 dataset 白名單、API 即權威（#3）。唯一 wiring 點是 `ingest.py`。
2. **explicit DDL**：系統自產運維/登錄表手寫 DDL——`schema.py:25 INFRA_DDL`（BIGSERIAL/TIMESTAMP/TEXT，刻意不套 API 表的 VARCHAR/NUMERIC 規則）、`catalog.bootstrap_catalog_tables:222`。
3. **builder 自 DDL**：下游計算型表各自 `CREATE TABLE`，core 只提供連線與交易邊界。

`catalog` 核心巧思是「**存原料、即時重算**」：`optimal_mode:273` 是純函式（只吃一個 dict 算最少呼叫抓取模式，無 DB/API I/O），不凍結會變的 n_dates；metadata 分「已落地表全讀 DB 真值」vs「未落地走 finmind 分類探測」；抓法由官方 `docs/finmind-references/datasets.md` 解析驅動（`_parse_official_datasets`），失敗才退硬編/probe 備援。

**catalog 的 anti-leakage 面向（親驗補充，#8）**：`_anti_leakage_flag`（`catalog:374`）偵測 dataset 是否自帶 API 公告日/as-of 時點欄（供下游正確設 PIT）；`KEY_CANDIDATES` 把 `realtime_start` 納入 FRED ALFRED vintage PIT 取版鍵（防同 (series,date) 多版塌成一列）。`optimal_mode` 的**國際股防呆**：只有 `data_id_source=='roster'`（台股名冊來源）才走 per-stock（`catalog:287`）；國際股 `src=='none'` 改走 by-date 全市場抓法，**刻意避免用台股 id（2330）去漏抓 UK/US/Japan**（2026-06-16 實證 bug）。

**不變式（enforced_where）**：
- **數字精度**：`_coerce`（`generic_schema.py:245-249`）純 pass-through、不呼叫 float()，精確 cast 全交 PostgreSQL。**範圍限縮（親驗）**：此不變式只對「被存的值」成立；`_digits`（`:87,:89`）確有 `float()` 但只用於推 NUMERIC 精度定寬、不碰落地值。且端到端「永不經 float」只在 API 以字串遞送數值時完全成立（JSON 數字字面量在 `resp.json()` parse 時就成 IEEE754 double）。
- **主鍵穩定**：表已存在時沿用 DB 既有 PK（`ensure_table:242` `db_primary_key`），不讓後續小樣本推更窄鍵覆蓋資料。
- **多 worker 併發首建安全**：`SAVEPOINT _ct` 隔離 CREATE，撞 `DuplicateTable` → ROLLBACK TO SAVEPOINT 改走補欄（`:198-210`）。
- **型別只擴不縮**：auto-widen；跨型別降級用 `trim_scale()::text` 去尾零保 byte-equal（`:240`，`200710.000000`→`'200710'` 與 API 原字串相同，守 #7）。
- **密鑰單一住所**：`FINMIND_TOKEN/FRED_API_KEY/DB 密碼`只在 `config.py:42/46/47` 讀 env。**範圍限縮（親驗）**：config 是唯一**密鑰** reader，但**非**唯一 env reader——`ollama.py:50/65/67`、`query_translation.py:69`、`finmind.py:90`（`FINMIND_QUOTA_GATE`）直接讀 operational flag env。

**關鍵常數**：`VARCHAR_LEN=255`、`NUMERIC(20,6)`（scale 上限 12）、`connect_timeout=10`、`page_size=1000`、`QUOTA_EXPIRY='2026-06-24'`（已過期）。

**gotchas / 死碼**：
- `catalog` 模組 docstring（`:14`）稱 `build()/refresh()` 會打 API，但**檔內無 `def refresh`**（grep 0 命中）；真正 refresh-like 路徑是 `build(db_only=True)`。stale docstring。
- `QUOTA_EXPIRY='2026-06-24'` 已過期（今 2026-07-10）：`_SPONSOR_ONLY:204-209` 為硬編 set，sponsor-only 抓法到期後 catalog metadata 與可抓性可能不一致。
- `require=('date',)` **只在首建表生效**（親驗）：`ensure_table` 對已存在表一律沿用 DB 既有 PK，故舊表若當初漏 date，須 DROP 重建方能修，非靠 require 補救。
- snapshot 表 date-insensitive（永遠回現值）：`_refine_earliest_below:762` 用 1955 哨兵窗偵測「不可能有真資料卻回值」→ earliest 標 None。
- `column_catalog` **無獨立 provenance 欄**（親驗）：欄級可溯源由 `zh_source`＋`last_verified` 承載；dataset 級才有 `source_provenance`。

**未完成債**：`BACKFILL_DEFERRED` 空集致 `probe_dataset:853-858` 分支目前 dead；`_DIRTY_VALUE_NOTES/_SPONSOR_ONLY/_SINGLE_DAY` 等硬編 dict 是需人維護的軟白名單，與 #29「repo 內資料＝另一種 hardcode」有張力。

---

### 3.3 features（35 特徵 → feature_values EAV）

**▶ 一句話**：每股從 source-pure raw 算 35 特徵寫長窄 EAV；非統一 per-module 契約、兩種缺列 regime（P 類缺列 / E 類真零）、發布日 gate 是 #8 命門。

**做什麼**：給定 as-of 面板日 `panel_date` + 一批 stock_ids，對每股算特徵，以長窄 EAV（Entity-Attribute-Value，`(panel_date, stock_id, feature, value)` 一列一特徵）寫入 `feature_values`。實測 **35 個生產特徵**＝19 個純還原價 df 特徵 + 16 個需查 DB 表特徵。其中含**八二（Pareto 80/20 集中律）** P3 量能集中 4 特徵、**康波（Kondratieff 長波）** C2 價格相位 + C4 法人流 + C3 毛利循環——皆為思想假說鏡頭（見 §0.1），**不以特定數字入公式**（#9），用 cutoff-free Gini / 資料自身極值定相位。

**關鍵檔案:符號**：`panel.py`（唯一常態生產寫入者＋組合根）：`build_panel:124`、`compute_features:88`（13 價量特徵）、`_compute_revenue_yoy:57`、`DDL:36`、`MAX_STALE_CALENDAR_DAYS:35`。`chip.py`（7 籌碼）：`compute_chip_features:107`、`_table_covers:44`。`valuation.py`（5 估值）：`compute_valuation_features:39`。`concentration.py`（八二 P3 量能集中 4）：`_gini:22`、`_max_share:34`。`phase.py`（康波 C2 價格相位 2＋C4 法人流 2）：`_price_phase:33`、`_inst_flow_cycle:53`。`margin_cycle.py`（康波 C3 毛利循環 1）：`compute_margin_cycle_features:55`、`MIN_QUARTERS:25`。`release_lag.py`（#8 命門）：`revenue_released:37`、`financial_released:42`、`REVENUE_DAY:20`、`FIN_LAG_QUARTER:21`、`FIN_LAG_ANNUAL:22`。

**建構作法**：`build_panel:124` 是**組合根 fan-out**——對每股跑「兩段 DB transaction + 一段 insert」：第一段查還原價/月營收＋呼叫 chip/valuation（`:130-136`），第二段呼叫 phase/margin_cycle（`:155-157`），concentration 不需 cursor（`:154`）。**刻意的非統一 per-module 契約**：`compute_features(df)`/`concentration(price_df)` 只吃純還原價 df；chip/valuation/margin 簽章是 `(cur, sid, panel_date)` 需查 DB；phase 混合——反映「哪些特徵是純價格數學轉換 vs 哪些要跨表 join」的本質差異，不強行統一介面。

**兩種缺列 regime（刻意非對稱）**：
- **P 類（連續、活躍股每期有值）**：算不出即 dict 不含該 key（缺列），末尾 `{k: float(v) for ... if v is not None and np.isfinite(v)}` 純函式濾網（`panel.py:121`、`concentration.py:56`、`phase.py:43/76`）。
- **E 類（chip f5-f7 借券/官股事件型稀疏）**：真零語意——無事件填中性 0，**但只在 `_table_covers` 雙邊 gate 通過時**才填 0（`chip.py:157/164/170`），否則仍缺列（防捏造零）。`_table_covers` = `min<=panel AND (panel-max).days<=14`（`_MAX_STALENESS_DAYS=14`）。

**不變式（enforced_where）**：
- feature_values PK=`(panel_date, stock_id, feature)`、value `NUMERIC(20,6) NOT NULL`（`panel.py:41-42`），upsert 冪等。
- **anti-leakage**：全 SQL `date <= %s` 純後向；月營收套 `revenue_released`（`panel.py:147-148`）、財報套 `financial_released`（`margin_cycle.py:44`）；`release_lag` 三常數（`REVENUE_DAY=15/FIN_LAG_QUARTER=45/FIN_LAG_ANNUAL=90`）是**法定公告期限（法律事實）非知識閾值**，不違 #9。
- **還原價 master gate**：無 ≤t 價量列 或 最近價距 panel >45 日 → 整股完全不寫任何特徵（含已算好的 chip/valuation 也丟棄）（`panel.py:137-144` `rows=[]` 觸發 `continue`）。

**gotchas（親驗）**：
- **「panel 唯一寫 feature_values」是過度宣稱**：正確版為「唯一**常態生產**寫入者」。另有 8 支離線候選腳本（`verify_signal_promotion.py:80`、`verify_economic_candidate.py:63` 等）直接 `INSERT INTO feature_values`（注入候選→DELETE 復原）。
- `revenue_release_date` 在 `release_lag.py:25-28`（reader 標 37-39 錯——37-39 是 `revenue_released` 布林函式）。
- **名實不符特徵**：`lending_fee_rate_mean_30d` 名 30d 實為最近 100 筆借券成交（`_LEND_SQL LIMIT 100` 無日期下界，`chip.py:88-95`）；`gov_bank_net_buy_60d` 名 60d 實為最近 ≤60 個官股事件日（`LIMIT 60`）。因 rename 漣漪 4 檔/77k+48k 列故保留舊名。
- `volatility_20d` **已因與 `range_mean_20d` 共線 +0.94 被五鏡剪枝**（`panel.py:105` `for w in (60,)`），docstring/記憶提及但 code 不產。
- off-by-one：momentum_252d 需 253 列（`n > w`，`:102`），price_to_252d_high/cycle_position 只需 252 列（`n >= 252`，`:112`）。
- `price_to_10yr` **基礎不一致（開放點）**：分子用 `TaiwanStockPriceAdj` 還原收盤（`valuation.py:34`），分母用 `TaiwanStock10Year close`（`:31`），兩表基礎是否一致 code **零對齊零校正**（`:70 cr[0]/tr[0]-1.0`）——需 DB 語意核實方能定實質影響。
- `chip.py:16-17` 承認：籌碼盤後 T+1 精確公布時刻 gate 未做，現採保守同日含 `date <= panel_date`，「上線後待 probe」——已知未修的 anti-leakage 邊角。

**未完成債**：`macro.py` 宣告的 31 檔 FRED series（22 Tier A + 9 Tier B）**未 wire 進 build_panel**（`panel.py:30` 只 import chip/concentration/margin_cycle/phase/release_lag/valuation），走獨立 `sync_macro.py → fred_series`，總經因子與 per-stock 特徵在 feature 層是分離的、如何在 model 層合流不在此子系統落地。

---

### 3.4 universe（核心股四道閘 core_gate）

**▶ 一句話**：不評分不排名不設上限，唯一判準是「資料完整＋真台股個股空間」；完整度分母是「市場實際可算組合數」、PIT 迴圈消完整度 survivorship。

**做什麼**：核心股（core universe）＝「值得被模型排序的乾淨可交易股集合」的選拔閘。輸出兩份名單：`core_universe`（pan-historical 單一名單，含 look-ahead，供探索）與 `core_universe_asof`（逐 as-of 日 PIT 名單，消完整度 survivorship，供誠實 walk-forward）。

**關鍵檔案:符號**（`universe/core_gate.py`）：`_select_core:108`（四道閘單一 SQL、required 計算）、`canonical_features:102`（寬 union 特徵集，由資料判定）、`build_universe:175`（pan_hist）、`build_universe_asof:202`（逐 t PIT）、`_write_build_meta:91`、`ETF_INDUSTRY:72`、`_REAL_STOCK_PREDICATE:75`、`DDL:31 / DDL_ASOF:41 / DDL_META:54`。

**建構作法**：整個選拔是「一條資料驅動 SQL ＋一個 PIT 迴圈」，無硬編、無評分。四道閘全部組合進 `_select_core` 的單一查詢：候選空間（真股碼 `~'^[0-9]'` regex + NOT EXISTS ETF）與流動性 EXISTS 放 WHERE（列級）；完整度 `HAVING count(*)=required` 與 conditional 豁免放 HAVING（聚合後）。**完整度分母是關鍵設計**：`required` **不是** `len(panel)×len(feat)`，而是「市場上實際可算出的 `(panel,feature)` 組合數」（`SELECT count(*) FROM (SELECT DISTINCT panel_date,feature ...)`，`:120-123`）；某特徵在某 panel 全市場 0 覆蓋（結構性不存在）就不計入 required，避免誤殺或靜默 0-core，差額存 `absent_combos` 揭露（#15）。流動性閾值＝latest panel 的 `dollar_volume_log_20d` 之 `percentile_cont(pct)`（動態相對分位、不寫死金額）。

**不變式（enforced_where）**：
- 完整度分母 required ＝市場實際可算組合數（`:120-125`），結構性缺格不計、差額存 absent_combos。
- core stock 必須 `HAVING count(*)=required`（`:170`，靠 PK `(panel,stock,feature)` 保證 `count(*)≤required`）。
- as-of t 只用 ≤t 面板算（`:217-219` 迴圈 `sub=pds[:i+1]`，point-in-time 消 survivorship）。
- 候選空間＝真股碼 ∧ 非 ETF（`:165-168`）。
- 流動性動態相對分位（`:130-135`）。

**關鍵常數（實測，親驗須加 config-scope 註記）**：`ETF_INDUSTRY`＝505 檔、`FINANCIAL_INDUSTRIES=('金融保險','金融業')`。以下數字**全部在生產配置 `--since 2014-01-01 --exempt-revenue-financial` 下成立**：28 面板（2014-12-31→2026-05-31）、`required=943`（=33×28 + 19，gov_bank 只在 19 面板）、`absent=9`、`core_count=344`、流動性 `pct=25→threshold=14.929`、union=35 vs intersection=34。**原表現況**（不加 --since）：35 面板 2007-2026、union=35、**intersection=28**（非 34）、required=971、absent=39。

**gotchas（親驗）**：
- **完整度與流動性時點口徑不對稱**：完整度是 pan-historical（≤t 所有面板都要齊），流動性只檢查 latest panel（`:140-142`）——core 股須「歷史一路完整」但「只需在 t 這天夠流動」。刻意設計、易誤解。
- **`canonical_features` 兩個同名相反實作**：core_gate 用「寬 union」（35 含 gov_bank）、`baseline.py:30` 用「嚴 intersection」（`HAVING count(DISTINCT panel_date)=len(pds)`，34）。
- **「core 股必然齊 baseline 34 特徵」在豁免配置下無機制保證（親驗）**：金融業 core 對 `monthly_revenue_yoy` 被豁免，而該特徵落在 baseline intersection-34 內，故機制上不保證 core⊇baseline 特徵集；當前僅因 4 檔保險 core（2832/2850/2851/2852）恰好都有該特徵而**經驗成立**。
- **兩個「34」是不同集合**：「28×34」的 34 是 universal 特徵數（union 35 減 conditional monthly_revenue_yoy）；「35 vs 34」的 34 是 baseline intersection（union 35 減 gov_bank）。數值巧合、集合不同。
- 硬字面：`'dollar_volume_log_20d'`/`'feature_values'` 在 liq 子查詢是硬字面（非 `FEATURE_TABLE` 常數）；thr=None → liq_filter 空字串 → 流動性 gate 靜默停用（graceful 但靜默 no-op 風險）。
- gov_bank 源表最早面板實為 **2021-09-30**（非 code 註解 line 118 的 2021-07，差 1 季，不影響 19/28 結論）。

**未完成債**：**survivorship 債 b 未閉環**（`scripts/train_ranker.py:36` 明標）：`core_universe_asof` 的 PIT 迴圈只消「完整度 look-ahead」，但 `feature_values` 本身建自「當前存活 roster」，在 now 之前就下市的股從未進 raw → 從未被任何 as_of 名單納入。故 as-of IC 仍帶樂觀（存活）偏誤、須明標。`core_universe`（pan_hist）含 look-ahead，須確保永不流入生產 walk-forward（雙軌陷阱）。

---

### 3.5 evaluation（誠實驗證的數學 SSOT）

**▶ 一句話**：所有驗證數學的單一住所——手刻零黑箱庫、五層職責切分；靈魂成功定義是經濟價值非 IC，排序力全是橫斷面相對強弱口徑。

**做什麼**：所有 validator/harness/predict 腳本 import 這裡的 helper，確保「rank IC、折切分、label 構造、DSR、投組經濟指標」跨模型/跨週期口徑一致才可比（#12）。

**關鍵檔案:符號**：`metrics.py`（指標 SSOT，純 numpy+scipy）：`rank_ic:53`、`summarize:67`、`effective_t_hac:89`（Newey-West Bartlett 核）、`expected_max_sharpe:122`、`deflated_sharpe:140`。`walkforward.py`：`_FEATURE_LAG_TD:17`（=62）、`_H_FORBIDDEN:18`（=252）、`splits:37`。`label.py`：`full_calendar:31`、`_entry_exit:42`、`forward_returns:51`、`cross_sectional_rank:88`、`HORIZONS:22`。`portfolio.py`：`drawdown_series:21`、`_turnover:51`、`build_long_portfolio:58`、`run_backtest:80`。`deflation.py`：`per_period_stats:20`、`deflated_floor:44`。`baseline.py`：`canonical_features:30`、`_panel_matrix:41`、`run_ladder:98`、`B2_ridge:141`、`M1_gbdt:145`。`cross_section.py`：`INTERACTIONS:22`、`_z:27`、`augment:32`。

**建構作法**：全部 clean-room 手寫、核心指標零外部統計庫依賴（Spearman/HAC/DSR 都手刻，讓每條公式可 trace）。五層職責切分：metrics 只算指標不選樣本；walkforward 只產索引切分不碰資料；label 只造 label 不切分；baseline/portfolio 是組裝層；`deflation.py` 是「per-period 正確口徑」共用住所（docstring 明寫「禁平行重寫」，因本 session 踩過「年化 SR 配 sqrt(T-1) 使 z 灌水 √ppy 倍、DSR 高估~14pp」的 units bug——**此「~14pp」為 deflation docstring 自陳、本次未獨立複現，見第 11 節 UNVERIFIABLE**）。一個貫穿效能決策：`label.full_calendar(conn)` 開頭取一次全市場交易日曆、逐折傳入，以記憶體 filter 取代對 11M 列 PriceAdj 的 N² 全表掃描。

**不變式（enforced_where）**：
- **H≥252 禁入 walk-forward**（結構性洩漏硬閘）：`walkforward.py:48` `if h_days >= _H_FORBIDDEN: raise ValueError`（執行期 raise、非 assert）。
- **embargo 保證下界＝h_days + 62 交易日**（label 窗＋特徵最大滯後）：`:51,57-63` 逐折用真實交易日索引 `bisect` 回推（`guaranteed=True`），非估算。
- `canonical_features` 只取每 panel 都出現的交集，且只讀 `feature_values` 不看 candidate 表（`baseline.py:36-38`）。
- **label t+1 進場**：`entry=calendar[0]`（次一交易日）、`exit=calendar[h]`（`label.py:48`）；forward return 用還原價 log return，`close≤0`（停牌哨兵）或缺價該股缺列（`:74-84`）。
- **DSR per-period（非年化）**：`deflation.py:28-29 sr_pp=a.mean()/sd`，防 units bug；共用單一函式（禁平行重寫）。
- **drawdown_series 單一住所**：`portfolio.py:21` 被 `execution.risk_control:51` 複用。
- **backtest ≡ live 選股邏輯零漂移**：同一支 `build_long_portfolio`。

**cross_section 交互特徵（易誤用製造假增量，親驗補充）**：`cross_section.py` 提供橫斷面交互特徵（z 乘積）動態變換。註冊表 `INTERACTIONS`（`:22`）目前僅一個 `inter_fh_x_p10yr`（foreign_holding_pct × price_to_10yr 的 z 乘積）。它**宇宙相依**故**刻意不入 `feature_values`**、而在 eval 層 `augment()`（`:32`）尾端 append；且是 **opt-in、僅限 374 核心宇宙**——換寬宇宙（1245 股含中小型）ΔIC 轉負（−0.0005），故**不設生產預設**。誤用到擴展宇宙會製造假增量。

**治權接線**：#12、#8（t+1 + purged embargo + `core_universe_asof` PIT + cross_section 交互 z 只用當前 panel 橫斷面）、#15（`effective_t_hac` HAC 去相關 + Deflated Sharpe 多重比較扣血 + gross/net 雙報）、#14（net=gross−換手成本）、#1（還原價 + 停牌缺列）。

**gotchas / latent 缺陷（親驗全 CONFIRMED）**：
- **`COST_TW=0.00585` 不是 evaluation 模組常數**：`run_backtest` 的 `cost` 參數**預設 0.0**（`portfolio.py:82`），意即 caller 若忘記傳 cost，net==gross。0.585% 散落在多支 scripts（`run_economic_eval/revalidate/predict_asof`）各自定義。「net=gross−turn×COST_TW」只在 caller 傳 cost=0.00585 時成立。
- **`run_backtest(asof=False)` 是壞路（latent dead）**：`portfolio.py:101` `stocks=None` → `baseline.py:44 set(None)` TypeError。預設 asof=True 且全庫 17 處呼叫無一傳 asof=False，故此路從未被走到。
- **long-short 短腿永遠等權**：`portfolio.py:137 simple[order[-nt:]].mean()`，即使 weight='pred' 長腿 rank 加權，短腿仍算術平均（非對稱設計）。
- `metrics.summarize` 仍回傳 iid `effective_t`（`:83`），#11/G8 明令禁裸用——防線僅靠 `run_ladder` 併陳 HAC 之**慣例**，無機械攔阻。
- `label.HORIZONS` 仍列 252，但 `splits` 對 h≥252 raise——兩檔常數未對齊的張力（stale advertise）。
- `run_ladder` 簽名只有 `seed`（單 seed），docstring 提到的 `seeds` 參數不存在（stale docstring）。
- **枚舉修正（親驗）**：`build_long_portfolio` 至少 3 個 caller（`run_backtest`/`predict_asof.py:132`/`survivorship_economic_verdict.py:156`，reader 說 2）；`deflation` importer 實為 4 支（reader/docstring 皆低估，漏 `deflate_cost_sensitivity.py`）。

---

### 3.6 models（薄殼 ranker + registry + artifact）

**▶ 一句話**：把 X fit 成相對強弱分數的最薄一層；超參是 baseline 的孿生字面複本靠人工同步無機械綁定、feats_hash 防漂移未實作。

**做什麼**：契約只有 `fit(X,y_rank)→self` / `predict(X)→ndarray`。三支各司一職：`ranker`（RankRidge 默認/RankGBDT 挑戰者）、`registry`（`model_registry` CRUD + PIT 載回 + resume）、`artifact`（joblib 序列化 + 凍結特徵集/as-of）。刻意不放 SHAP（留 audit）。

**關鍵檔案:符號**：`ranker.py`：`RankRidge:16`（`__init__(alpha=1.0):21`、fit lazy import `:26`）、`RankGBDT:41`（`fit LGBMRegressor 固定超參:50`）。`registry.py`：`git_sha:16`、`register:25`、`latest:41`（`asof_snapshot<=asof` PIT）、`exists:55`。`artifact.py`：`feats_hash:18`（sha256 sorted [:16]）、`save:23`、`load:36`、`MODELS_DIR:15`。CLI：`scripts/train_ranker.py:train:58`、`scripts/predict_asof.py:predict:102`。

**建構作法**：核心是「複用鐵律（#12）+ 薄殼」。估計器組態不是共享 code，而是把 `evaluation/baseline.py` 的 `B2_ridge`/`M1_gbdt` 超參**字面複製**到 `ranker.py`（RankRidge=StandardScaler+Ridge(alpha=1.0)、RankGBDT=LGBMRegressor 固定 7 超參）——兩份是靠人工慣例同步的孿生字面複本，**無任何 assert/test 把它們綁在一起**。`train_ranker` 全複用 baseline helper。sklearn/lightgbm 採 fit 內 lazy import（package import 輕、隔離乾淨，代價是相依錯誤延到 fit 才爆）。

**不變式（enforced_where）**：
- family 只能 RankRidge/RankGBDT：`migrate_prediction_ddl.py:37` DB CHECK + `train_ranker.py:94` argparse choices 雙閘。
- register 對同 model_id 冪等 upsert，**只更新 metrics/artifact_path/git_sha/created_at**（`registry.py:34-36`）。**親驗修正**：`git_sha` **非凍結**——每次 ON CONFLICT 用 `EXCLUDED.git_sha` 覆寫（`:36`）；真正凍結的是 feats_hash/seed/family/horizon/train_span/asof_snapshot。
- PIT 選模：`latest` 用 `asof_snapshot<=%s ORDER BY asof_snapshot DESC, created_at DESC LIMIT 1`（`:47`），絕不載 as-of 後訓練的模型。
- feats_hash 順序無關：`sha256("\n".join(sorted(feats)))[:16]`（`artifact.py:20`）。

**gotchas / 過度宣稱（親驗）**：
- **REFUTED：「prediction_values 禁被回讀當特徵由 AST + DB GRANT 雙閘強制」**——雙閘保護的是「素養→預測」方向；`prediction_values` 本身被 GRANT 給 predict role 可讀寫（`setup_predict_role.py:39`），無機械閘阻止 pipeline 讀它當特徵，僅 `migrate_prediction_ddl.py:56` COMMENT 約定。且可執行的 GRANT code 住 `setup_predict_role.py`、非 `migrate_prediction_ddl.py`（後者只有 COMMENT）。
- **`predict_asof.py:120 cur_feats` 是死變數**：算出當下 canonical 特徵集後**再也沒被讀**。緊接的 feats_hash 檢查（`:121`）是 `artifact.feats_hash(art["feats"]) != reg["feats_hash"]`＝artifact↔registry 自檢（偵測損壞），**不是**偵測「當下 canonical vs 凍結」漂移。三處 docstring 宣稱的「防漂移拒載」**未實作**。實效：若凍結特徵被移除→無股達標→predict `<5` 中止（誤打誤撞擋住）；若 canonical **新增**特徵→靜默用舊特徵集出單、漂移未被偵測。
- **RankRidge seed 是無效標籤**：RankRidge `__init__` 無 seed 參數，`train_ranker.py:78` 對 RankRidge 呼叫 `est_cls()` 不傳 seed；但 model_id/registry 仍記 seed=42（誤導性裝飾）。
- **config 靠慣例同步、有實質分歧**：RankRidge 永遠 StandardScaler；但 baseline B2_ridge 是 `RobustScaler if robust else StandardScaler`（`baseline.py:141`）。「逐值等同」只在 robust=False（預設）成立；一旦 baseline 以 robust=True 跑，離線估計器就與上線 RankRidge 分歧，無綁定不會自動同步。
- `latest()` 同 asof 多 seed 共存時 tiebreak 靠 `created_at DESC`，而 re-register 刷 created_at=now() → 重跑登錄會改變勝者。
- `artifact.MODELS_DIR`（models_artifacts）與 `config.MODELS_DIR`（models）不同名，後者於此層未用（命名易混）。

---

### 3.7 audit（隔離命門 + DB↔API 對帳 + 特徵候選/五鏡/相關性）

**▶ 一句話**：把治權鐵則變可自動執行的檢查——隔離 AST 稽核、DB↔API 對帳三類差異非對稱處置、候選機制性隔離、五鏡合判；全層唯讀（唯一例外 heal_by_date 經 sync 寫生產）。

**做什麼**：五個獨立職責：(1) `import_isolation` 把「素養層零進預測管線」變可跑不變式；(2) `reconcile` 逐列重抓 API 真值、逐值比對證明 DB 無 AI 幻像（#7）；(3) `feature_candidate` 把相關性浮現的候選做成 as-of 安全特徵、寫獨立 staging 表；(4) `feature_diagnostics` 訓練前用五鏡診斷特徵去留；(5) `field_correlation` 探索 raw 欄位相關與 lead-lag。

**關鍵檔案:符號**：`import_isolation.py`（見 2.1）。`reconcile.py`：`compare:61`（純比對四類計數）、`_norm:37`、`verdict:404`（三-clause）、`fixable_dates:171`、`flagged_dates:181`、`heal_by_date:186`、`reconcile_per_stock:204`、`reconcile_market:314`、`reconcile_coverage:332`、`reconcile_fred:367`。`feature_candidate.py`：`compute_candidates:66`、`CANDIDATES:30`、`FEATURE_TABLE:29`（feature_candidate_values）。`feature_diagnostics.py`：`five_mirror:98`、`single_factor_ic:26`、`collinearity:48`、`leave_one_out:66`、`shap_importance:82`。`field_correlation.py`：`build_stock_panel:89`、`compute_correlations:123`、`compute_leadlag:181`、`MIN_OBS:24`。

**建構作法**：五支各自獨立、共享「唯讀稽核 + 只寫自建分析表」邊界。import_isolation 用純檔案系統＋AST 靜態分析（不 import 被檢查的 code）。reconcile 以純函式 `compare()` 為核心（無 I/O、四類計數 matched/value_mismatch/missing_in_db/extra_in_db），外層各 `reconcile_*` 對齊寫入端點重抓（per-stock 用 per-stock 端點、by-dim-id 逐維度 id），刻意同源比對消除「端點差造成的假 VM」。feature_candidate 寫 schema 同構的獨立 staging 表，由 `baseline._panel_matrix` 條件式併讀（僅補 feats 內明點名者）、而 `canonical_features` 不看此表 → **機制性（非紀律性）隔離**候選污染核心特徵集。feature_diagnostics 全部 reuse evaluation helper。

**三類差異的非對稱處置（親驗展開）**：`compare()` 產四類計數，其中兩類擋 attestation（VM=value_mismatch、EX=extra_in_db），兩類不擋（matched、MIS=missing_in_db）。處置**非對稱**：`fixable_dates`（`:171`，VM/MIS＝可重跑 sync 補的覆蓋缺口）→ `heal_by_date`（`:186`）回灌 `sync.sync_by_date` 的 upsert 路徑（非 hand-patch）；`flagged_dates`（`:181`，EX＝DB 有 API 無＝幻像/PK 碰撞紅旗）→**不自動補也不自動刪、須人查根因**（EX 是最嚴重訊號，可能是塌列或 AI 幻像）。市場級/單序列表用 `reconcile_market`（`:314`）單批對帳；`reconcile_coverage`（`:332`）用列數量級比（非逐值）、`COVERAGE_MISS_TOL=0.2` 容忍。**抽樣須誠實知會**：`reconcile_per_stock`（sample_n）/`reconcile_coverage`（sample_days）是部分覆蓋非全股 attest，`agg['sampled']` 旗標須由呼叫端誠實知會（#15）——否則「抽樣過了」會給全庫乾淨的假信心。

**五鏡是哪五鏡（親驗定義）**：`five_mirror`（`:98`）合判五個診斷鏡頭——① 單因子有號 IC（`single_factor_ic:26`，附 HAC Eff-t）、② 共線性相關矩陣（`collinearity:48`）、③ leave-one-out ablation（`leave_one_out:66`）、④ TreeSHAP 重要度（`shap_importance:82`）、⑤ 增量/穩健綜合（併於 ①③ 的有號 IC 與去一 delta）。合判規則：**任一單一指標不得判生死**，`'drop?'` 裁定需 `weak_shap ∧ weak_ic ∧ ablation_safe` 三條件同時成立（`:125` AND）。

**不變式（enforced_where）**：
- 預測 7 package 零 import 素養層（`_import_violations:63-85`，實跑 exit 0）。
- attestation 通過＝`value_mismatch=0 ∧ extra_in_db=0 ∧ not incomplete`（`verdict:404-413`）；missing_in_db 不入判定（覆蓋缺口≠幻像）。
- **正規化後值相等比對**：bool 必在 float 前判（否則 `float(True)=1.0` 把 DB 'true' vs API bool 誤成假 EX/MIS）、前導零識別碼（'0050'）保 str（`_norm:41-42,47-48`）。
- 候選機制性隔離：`baseline._panel_matrix` 用 `to_regclass` 守 + feats 過濾，`canonical_features` 完全不讀候選表。

**關鍵常數**：`PIPELINE`（7 package）、`FORBIDDEN`（3 前綴）、`SCAN_DISTILL`（界線-A 涵蓋素養層寫入者）、`COVERAGE_MISS_TOL=0.2`、`MODEL='M1_gbdt'`（leave-one-out 裁定模型）、`MIN_OBS=60`。

**gotchas / 頂層過度概括（親驗）**：
- **「全層唯讀絕不碰生產」有例外**：`reconcile.heal_by_date`（`:186-201`）偵測到 fixable 日期後呼叫 `sync.sync_by_date`（`:196`）回灌，那是對**生產 raw 表**的 upsert 寫入（走正常 sync 路徑、非 hand-patch）。正確版：對帳/相關/五鏡函式皆唯讀，唯 heal_by_date 為「偵測+重跑 sync」orchestrator。
- **「byte-level attestation」是修辭**：實作是**正規化後值相等**比對（float round 6 位、bool 轉小寫、前導零保 str），非原始 byte 相等。
- **`heal_by_date` 的 passed 只有 2-clause**（`:201` VM=0 ∧ EX=0），缺 `not incomplete`，與正典 `verdict()` 三-clause 不一致——若 heal 後 after 仍有抓取失敗，heal 仍可能回 passed=True（違 #15 精神）。
- `_scripts_predict_leak_violations`（`:129`）只掃 RBAC+CHAT literals、**未掃 DISTILL_LITERALS**——import 預測 package 的腳本若字面觸及 `advisor_distill_*` 不會被此面抓到（偵測面不對稱）。
- `reconcile_coverage` 的 `since` 參數 **provisioned-but-unused**（docstring 自陳）。
- reconcile_fred Tier A/B 容忍非對稱：Tier B（vintage=True）逐版精確零容忍；Tier A 套 restatement 容忍（僅 `not is_vintage` 分支 `:392`，只扣 EX 計數不刪 DB 真值）。

**未完成債**：reconcile guard/roster 過濾整合測試待補（`test_reconcile.py:7` docstring）；`feature_candidate.CANDIDATES` 為硬編 4 個實驗候選（通過五鏡才提拔進 features/ 生產）。

---

### 3.8 execution（部署後風控 overlay）

**▶ 一句話**：在 long 投組上疊唯讀 advisory 風控——閾值全住 DB、只有 cap 改寫落庫權重、DD/換手只出旗標絕不下單；本機 risk_policy 表尚未建故 dormant。

**做什麼**：三件事：DD 熔斷（權益回檔觸閾值→建議降倉）、單標的部位上限 cap（削頂並按比例重分配）、換手預算（超預算告警）。三類閾值全讀 DB `risk_policy` 表、**零 hardcode**。只有 cap 會機械改寫落庫權重（可逆正規化）——機械落地靈魂「系統建議、人決策；防守用規則不靠預測」。

**關鍵檔案:符號**（`execution/risk_control.py`）：`load_policies:25`（唯一讀 risk_policy）、`dd_circuit:39`（複用 `portfolio.drawdown_series`）、`apply_position_cap:68`（收斂迴圈）、`turnover_check:105`、`apply_overlay:129`（orchestrator）。DDL：`scripts/migrate_risk_policy_ddl.py:DDL:30 / SEED:55`。

**建構作法**：「三層委派 + 唯讀 advisory + 資料驅動閾值」。零重造：DD 算法/換手率/選股全部委派給 `portfolio` 單一住所（#12）。程式碼**無任何硬編閾值數字**（grep 確認 0.10/0.75 僅在 docstring，執行碼唯一小數是 1e-12 浮點容差），閾值全走 `load_policies` 從 `risk_policy` 讀（#29b）。整個模組**零寫操作**（唯一是一條 SELECT）。cap 用迭代收斂（每輪夾頂+按比例重分配，上界 `len(sids)+1` 保證停），且刻意在 `N×cap<1` 退化投組回權重和 <1 而非硬塞回 1（硬塞會反推回集中）。

**不變式（enforced_where）**：
- 風控唯讀 advisory 不下單（全檔零 INSERT/UPDATE/DELETE）；`apply_overlay:146` controlled_port 僅含 cap 後權重。
- 閾值零 hardcode（`risk_control.py:32-34` 唯一來源 SELECT FROM risk_policy）；DB CHECK 鎖 `policy_key IN('dd_circuit','max_position','turnover_budget')`（`migrate:39-40`）。
- DD 熔斷 anti-leakage（#8）：只用已關閉 forward 窗之已實現報酬（`predict_asof.py:67` `if future[h]>asof: continue`）。
- 熔斷觸發用**當前**回檔 `dd[-1]` 非最深回檔（`:56,59`）；max_dd 純供報告。
- 遷移冪等（`CREATE IF NOT EXISTS` + `ON CONFLICT DO NOTHING`）。

**治權接線**：靈魂「防守用規則，不靠預測」＋原則精華 #13「規則地板優先」。execution 是橫切下游 overlay 的**機械證據**：全 repo 只有兩支 output-stage 腳本 import `augur.execution`（`predict_asof.py:32`、`verify_risk_overlay.py:31`），無任何 feature/universe/model 引用它。

**關鍵常數**：`dd_circuit` H60/H120＝-0.20/-0.25（action=reduce_half）、`max_position=0.10`（cap）、`turnover_budget=0.75`（warn）、`COST_TW=0.00585`。

**gotchas / 開放債（親驗）**：
- 熔斷用當前回檔非最深：已從深谷回升的投組即使歷史 max_dd 很深也不觸發（正確語意、易誤讀為「看歷史最深」）。
- cap 退化投組合法回權重和 <1（實測 5 檔×0.10→sum=0.5）——下游不可假設 controlled_port 權重必和為 1。
- **`risk_policy` 表在本機 live DB 尚未建立**（`to_regclass('risk_policy')=None`，而 prediction_values/feature_values 皆存在）——`migrate_risk_policy_ddl.py` 尚未在此機執行，風控**實際 dormant**（load_policies 回空 dict）。
- **DD 熔斷 live dormant**：`_deployed_dd_returns` 需已關閉 forward 窗，現況多為 1 期/窗未關 → 回 `[]`。
- **doctrine 機制落差**：靈魂/原則 #13 指定規則地板＝「波動目標 × 趨勢（vol-target × trend）」，但實作的是 DD 熔斷+cap+換手——是規則型防守但非 doctrine 明言的機制，屬部分落地。
- 極輕微：`DDL:28` 是 `DDL = [` 常數起點，真正 CREATE TABLE 在 `:30`。

---

### 3.9 預測層 harness（持續再驗證 / deflation / survivorship / GRANT）

**▶ 一句話**：把「edge 薄且近期小樣本」機械化成可長期自我監督的部署後管線——判停只出旗標給人；編排層零數值邏輯全複用 evaluation/models helper。

**做什麼**：九支 script 分四群：(1) 再驗證 harness（`revalidate/baseline/verdict/cycle`）逐輪重跑 B/C/D + deflation、凍結建置基線、兩軌三態判停但只出旗標；(2) 出單（`predict_asof`）PIT 選 registry 模型建投組寫 prediction_values；(3) deflation 誠實裁決把 headline「淨 Sharpe~1.2」用 Deflated Sharpe 釘成真兆地板；(4) survivorship 經濟閉環拆下市偏誤 vs incumbency 宇宙定義；外加 `setup_predict_role` DB 動態閘。

**關鍵檔案:符號**：`revalidate.py`：`stage_b:163`、`stage_cd:230`、`refresh_trial_ledger:284`、`track:318`。`revalidate_verdict.py`：`evaluate:39`（純函式判停器）。`predict_asof.py`：`predict:102`、`_deployed_dd_returns:50`。`deflate_headline_verdict.py`：`_ppy_for:49`、`_nonoverlap:39`。`survivorship_economic_verdict.py`：`build_pit_universe:43`、`run_pit_economic:128`。`setup_predict_role.py`：`FORBIDDEN_PREFIXES:32`、`classify:45`、`apply:85`。

**建構作法**：核心是「編排層 + SSOT helper」：九支幾乎不含自有數值邏輯，一律複用 evaluation/models helper，自己只負責「取 panel → 呼叫 helper → 逐列寫記錄表 → 印裁決」。判停器 `evaluate()` 是**純函式**（吃 baseline/current/thr/prior_streak、回 dict），閾值全外置到 `judgestop_threshold` 表。腳本間互相 import 複用（`revalidate_baseline` import `deflate_headline_verdict._nonoverlap` 與 `survivorship.build_pit_universe`），不 fork 邏輯。cadence 走 #28 資料驅動（`--skip-existing`）、非常駐 daemon。

**不變式（enforced_where）**：
- 判停三態純函式：`evaluate:39` 軌 A 之 DSR 只 append 進標註串列 a、**絕不進軌 B 判停串列 b**（`:45-46`），DSR 機械不可能觸發判停。
- walkforward calendar 路把 #8 embargo `h+62td` 下界做成逐折真實交易日回推（非估算），H≥252 raise。
- `setup_predict_role.apply:99-111` 把素養層 anti-leakage 從 AST 靜態閘補上 DB 動態 GRANT 閘。

**關鍵常數**：`COST/REF_COST=0.00585`、`TOP_FRAC=0.1`（deployment 口徑，helper `build_long_portfolio` 預設實為 0.2、caller override）、`GBDT_SEEDS=(42,43,44)`、`VERDICT_N_DEFAULT=20`、`RECENCY_TD=63`、judgestop `dsr_annotate=0.95`（frozen=true）/ `consecutive_k=2`、`net_excess_rel_drop=0.5`（frozen=false 校準中）、`CANONICAL_FEATS_HASH='canonical34_stageB_20260706'`。

**gotchas / 過度宣稱（親驗）**：
- **`predict_asof` 的「feats_hash 防漂移」是 over-claim**（同 models 3.6）：`cur_feats` 死變數，`:121` 只做 artifact↔registry 自檢。
- 軌 B 之 `net_excess_rel_drop`/`consecutive_k` 閾值 **frozen=false 校準中**，判停敏感度未定案。
- **STAGE C vs D 是同一批回測矩陣的事後歸類**（`:249` 只把「2014 起 ridge H60 LO」標 C、其餘標 D）。
- **deflation N「保守取大」方向反直覺**：同頻家族 N 小=樂觀上界、混頻 N 大=保守下界，取 `dsr_lo`。**H120 since2014 實證 N=8 過（95.8%）、N=16 未過（93.6%）→ 判未確立**（此組數字為 code docstring/inline 註記自陳、本次未在 DB 重跑複現，見第 11 節 UNVERIFIABLE）。
- `classify()` 的 elif/else 兩支都 `allowed.append`（冗餘分支）。
- **survivorship 裁決**：下市 survivorship 偏誤 ①≈0（+0.0023 Sharpe）、incumbency 宇宙定義 ②＝**−16.5%**（1.20→1.00）——**此為 `survivorship_economic_verdict.py:9` docstring 自陳、本次未在 DB 重跑複現**（見第 11 節）。
- **REFUTED：「grep 確認 augur_predict 僅出現在 setup 腳本自身」**——role 名亦在 `tests/test_predict_role_isolation.py:18`；但實質結論（role provisioned-but-unwired、predict runtime 走單一 `config.DB_PARAMS`、`DB_PARAMS_PREDICT` 尚未實作）仍 CONFIRMED。

**未完成債**：`augur_predict` role 動態閘 provisioned-but-unwired（`predict_asof.py` 走預設 role、`setup_predict_role.py:82` 自陳「role 尚未建、暫緩實建」）；H120 近期優勢待定論（since2021 n<20 小樣本）。

---

## 4. 半-2 逐子系統 HOW-built

### 4.1 knowledge（11 模組知識層 library）

**▶ 一句話**：純函式 + 契約 SSOT + 安全閘的 library 群；RBAC resolver 刻意住 knowledge 讓預測經 core 也達不到、serving 索引只回 pk 不回內容。

**做什麼**：四類事：(1) `textnorm` 提供三方 JOIN 的 term 正規化契約；(2) `corpus`（准入述詞 SSOT）+ `embedspec`（嵌入世代命名 SSOT）；(3) RBAC 身分（`identity`）與授權（`access`）——**刻意住 knowledge/ 而非 core/**；(4) `fileparse`/`webupload`/`sftpbrowse` 逐字入庫 + `lexicon_parsers` 六 regex parser 切辭書。`vectorindex`（Milvus Lite/Qdrant 雙 adapter 可拋棄 serving 索引）；`concept_graph`（L6 跨學說關聯圖唯讀查詢）。

**關鍵檔案:符號**：`textnorm.py`：`normalize:52`、`tokenize:168`（zh 逐字 U+4E00-9FFF + jieba HMM=False；西文手刻 Porter 1980）、`porter_stem:107`。`corpus.py`：`clean_work_sql:29`、`clean_item_sql:38`、`LICENSE_WHITELIST:17`（5 值）、`SEMANTIC_ENTITY_TYPES:22`。`access.py`：`resolve_allowed_domains:17`（三態 fail-closed）。`identity.py`：`hash_password:24`、`verify_password:31`（`hmac.compare_digest`）、`issue_session:63`、`verify_session:74`。`vectorindex.py`：`VectorIndex:27`、`MilvusLiteIndex:52`、`QdrantIndex:159`、`stats:108/217`。`concept_graph.py`：`related_thinkers:14`。`fileparse.py`：`extract_text:99`。`lexicon_parsers.py`：`parse_shuowen:41`、`_parse_commentary:237`。

**建構作法**：全走「純函式 + 封閉集 fail-loud/fail-closed + 單一住所」。契約集中：textnorm/corpus/embedspec 都是被多腳本 import 的 SSOT，禁 inline 複本；textnorm 手刻 Porter stemmer（零 nltk）與 jieba HMM=False 詞典驅動分詞換取確定性可重現。**安全字面內插 vs 參數化二分**：`corpus.clean_item_sql` 把封閉集常數（license/entity_type/access_scope）直接內插進 SQL，把使用者資料（owner_user_id/allowed_domains）一律走 psycopg 參數化。fail-closed 為預設（access.resolve 任何異常/查無/inactive/無 grant 都收斂成 `(False, ∅)`）。serving 索引以五方法抽象基類封裝，`search` 只回 `(pg_pk, distance)` 永不回內容（內容永遠回 PG JOIN），pgvector 為 SSOT、外部索引隨時可 DROP 重建。

**不變式（enforced_where）**：
- item_text license 只准 5 值白名單（`corpus.py:17` 內插 + DB CHECK `migrate_text_understanding_ddl.py:48`）。
- 禁 AI 生成入庫：DB CHECK `chk_itext_source_type = CHECK(source_type <> 'ai_generated')`（`migrate:149-150`）。
- `knowledge_lexicon.license` 恆 `'public_domain'`（單值等式 CHECK `migrate:88`，嚴於 item_text）。
- RBAC 三態 fail-closed：`access.py:19-37`（super→(True,∅)、有 grant→(False,聯集)、其餘→(False,∅)）；下游 `clean_item_sql:65` 空 allowed→`'AND false'`。
- **RBAC resolver 物理住 `augur.knowledge`**（FORBIDDEN 前綴），由 `test_philosophy_isolation.py:53-64` + `import_isolation._placement_violations` 雙重釘死。
- identity：pbkdf2-sha256 240k（`_ITER:20`）、`hmac.compare_digest`、DB 只存 `sha256(token)`、SESSION 12h TTL、authenticate 無帳號跑 dummy verify、verify_session 全 AND fail-closed（`:82`）。
- serving search 只回 `(pg_pk, distance)`；stats pk 枚舉自驗 `len==count` 否則 raise（`:120-121`，親驗：Milvus 僅無 filters 時觸發；Qdrant 全程）。

**RBAC 治權層面向（v1.28.0/v1.29.0，親驗補充）**：這層 RBAC 對應憲章 v1.28.0/v1.29.0 的**系統定位擴張**——單一主使用者→superuser + 受控多群組。機制已建（`access.py` resolver + DB CHECK），但**多使用者群組實際 provisioning 屬「永遠決策層人拍板」的待決政策層**、非全自動；`access.resolve` 的 fail-closed 只保證「未授權即 deny」，不代表多群組政策已定案。

**關鍵常數**：`MODEL_TAG=intfloat/multilingual-e5-small`（`embedspec:15`，reader 標 16 為 off-by-one）、`MODEL_DIMS[e5-small]=384`、`TEXTNORM_VER=1`、`_NAME_MAX=26`、`N_PARTITIONS=16`、`MAX_BYTES=50MB`、`MAX_TREE_FILES=5000`（`sftpbrowse:21`）。

**gotchas（親驗全 CONFIRMED）**：
- **jieba floor 非 pin**：`pyproject.toml:17` 是 `jieba>=0.42.1`（下限非釘版），而 textnorm docstring 宣稱「jieba 版本釘於 pyproject…半年重跑一致」＝**過度宣稱**。TEXTNORM_VER 的「同輸入必同輸出」只在 jieba 版不動時成立；jieba minor 升版可悄改分詞→JOIN 鍵漂移而 TEXTNORM_VER 不變（靜默污染）。確定性靠人工 SOP-E 非機器強制。
- **assert 作安全驗證（反模式）**：`corpus.clean_item_sql:55` 用 `assert access_scope in (...)` 後才字面內插進 SQL；`python -O` 下 assert 被剝除→非封閉集字串直接內插＝SQL 注入面。實務上呼叫端皆傳封閉集內值、風險低。
- **CJK 範圍不對稱→JOIN 鍵邊緣不齊**：`textnorm._is_cjk`＝U+4E00–9FFF，但 `lexicon_parsers._parse_commentary` 抽 term 用 U+3400–9FFF（`:259`）；首字落 ExtA 的註疏 term 是合法 lexicon 詞條卻不會被 concordance tokenize（古籍罕見、實務影響小）。
- **S4 stats 層 inline CLEAN 複本**：`build_cross_school_stats.py:58` 自定 CLEAN 字串未 import `corpus.clean_work_sql`（#12 漂移風險）。
- embedspec 命名預算貼地零餘裕（實跑：sentence collection 剛好 26 字、sync_scope(zh) 剛好 32 字、eng 即 fail loud）。
- `corpus.py` 自身 docstring 仍寫「四值白名單」但常數已 5 值（v1.36.0 加 owned_local）——**code 內 docstring stale，非 reader 之誤**。

**未完成債**：**`concept_graph.py` 為 provisioned-but-unwired**（grep 全 repo 除自身外零 import，L6 查詢介面已建但無呼叫端，且依賴 S4 stats 層已 populate）；fileparse PDF OCR 未實作（掃描檔→'no_text'）；Qdrant adapter 實測成熟度較 Milvus Lite 低；`SEMANTIC_ENTITY_TYPES` 首期僅 paper/report/document（book/compound 等首期不入語意層）。

---

### 4.2 philosophy（哲學素養層）

**▶ 一句話**：把投資大師智慧結構化成「可證偽因子假說」——schema 刻意把文獻假說(direction)與 augur 實證(validated_ic)分離、冪等 upsert NEVER DELETE、DB CHECK 硬擋 AI 生成。

**做什麼**：`framework.py` 將 23 個投資學派拆成「原則→augur 特徵→預期 IC 方向」+ 17 位思想家/著作策展，寫進 **9 張 `philosophy_*` 表**；`retrieval.py` 提供語義 kNN + 逐字可溯源引用的檢索 API 供顧問引經據典。**建構最高 WHY**：哲學是**假說、非真兆**——「驗證活下來、非大師說了算」。

**關鍵檔案:符號**：`framework.py`：`DDL:20`（9 表）、`bootstrap:253`、`build:259`（upsert NEVER DELETE）、`build_people:372`、`SEED:93`（23 學派）、`THINKERS:311`（17 思想家）。`retrieval.py`：`retrieve:64`（works 側 e5 kNN + scope 閘）、`retrieve_items:265`（exact→ann 零向量優先）、`retrieve_all:324`、`verify_verbatim:110`、`lexicon_lookup:165`、`concordance_lookup:190`、`is_low_content:98`、`Citation:23`。

**建構作法**：DDL 以 Python list of `CREATE TABLE IF NOT EXISTS`（9 表）→ `bootstrap` 逐條 execute、冪等自建。策展資料以 in-code literals 承載（手工策展自真實文獻、非 AI 生成、非 DB seed 檔）。核心建構決策＝「**冪等 upsert，NEVER blanket DELETE**」：build 全用 ON CONFLICT DO UPDATE / SELECT-then-INSERT；關鍵是 `UPDATE philosophy_principle` 只動 hypothesis 不動 status、`UPDATE principle_factor_map` 只動 direction 不動 validated_ic/econ（`:298`）→ seed 重建時 augur 回填存活。刻意不 DELETE 的理由寫死在 docstring：下游 FK 已掛他管線列。retrieval 走「零向量優先、逐字可溯源」：items 側先 exact concordance 計數，只在不足且真有嵌入時才載模型跑 ANN 補位（#28）。

**不變式（enforced_where）**：
- #1 禁 AI 生成：`framework.py:48 CHECK(source_type<>'ai_generated')` + `:82 CHECK(work_type<>'ai_generated')` 雙表 DB 硬約束。
- 假說非真理刻進 schema：`direction SMALLINT NOT NULL`（文獻假說 `:39`）vs `validated_ic DOUBLE PRECISION` 可 NULL（augur 回填 `:40`）vs `principle.status DEFAULT 'untested'`（`:33`）。
- 冪等 NEVER DELETE（`build:269-302` 無 DELETE 語句）。
- RBAC fail-closed（`retrieve:68-69` scope=None→[]、`corpus:60/66` owner/domain 缺→AND false、`retrieve_all:330` 無 scope→全 deny）。
- verbatim 逐字他證：`retrieval.py:123` work 側 citation.text ⊂ row[0]；`:353/356` item 側位置+內容雙驗。
- 素養層絕不進預測管線（`import_isolation.py:33` FORBIDDEN 含 augur.philosophy，實跑 exit 0）。

**關鍵常數**：DDL 表數＝**9**（bootstrap docstring `:254` 誤稱 6，**stale**）、SEED＝23 學派、THINKERS＝17、`MODEL_TAG=multilingual-e5-small`、`LICENSE_WHITELIST`（5 值）。

**gotchas（親驗）**：
- `retrieve_all` **是 server 注入路徑、非 library 預設**：`advise()` 預設 src_fn=works-only 的 `retrieve`（`advise.py:50`）；三路徑 retrieve_all 用於 (a) server 注入之對話服務（`serve_advisor_openai.py:72`）與 (b) **蒸餾 context 建置腳本**（`advisor_distill_build_context.py:49`，親驗補充——reader 稱「唯一生效點=server 注入」不完整）。
- `concordance_lookup`（`:190`）**不過 clean_item_sql 的 domain/owner 收窄**且零呼叫點——若未來接入顧問讀取路徑而未先補 RBAC 閘，會繞過收窄洩漏。
- `principle_factor_map.feature` 是裸 VARCHAR(255) **無 FK**——待建 feature（roe/debt_ratio/piotroski_fscore/peg_ratio/macro_regime）照樣 INSERT，但無可算特徵 → validated_ic 永 NULL。
- `philosophy_build_meta` 只記 4 個 count，不記 build_people 維護的 thinkers/works/links（低估實際維護範圍）。
- in-code 策展（SEED/THINKERS 寫死 Python）與 CLAUDE #29「repo 檔＝另一種 hardcode」有張力；此走「principle→factor 假說映射本質是 code」的哲學層特例路。
- `is_low_content` 的「52/126,609≈0.04% junk chunk」與 e5-small「0.80~0.88 窄帶」是 **docstring-sourced 統計**（本次無 DB 連線不可驗，判 UNVERIFIABLE，見第 11 節）。

**未完成債**：`stock_philosophy_tag` 表 DDL 建好但**全 repo 零 writer**（橫斷面哲學標籤未實作）；`validated_ic/validated_econ` 目前全 NULL、status 全 'untested'（假說須過四道漏斗+#14 實證回填的 backlog 尚未執行）；items 側檢索依賴 L2/L3 表未穩定落地時誠實回 `[]`（優雅降級）。

---

### 4.3 advisor（11 模組顧問層）

**▶ 一句話**：唯一編排出口 advise()、三敵防護從 prompt 自律升級為生成後機械 guard 五閘；弱模型能力天花板靠 D4b 確定性 picks 表結構性繞道。

**做什麼**：把量化本體的真實預測數字（唯讀 payload）+ 素養庫逐字檢索引文，經**本機** LLM（qwen3:8b）翻成引經據典的白話解讀。核心不是「答得多」而是「不說謊」。唯一編排出口＝`advise()`；OpenAI 相容殼只做協定翻譯、零第二編排器。

**關鍵檔案:符號**：`advise.py`：`advise:34`（唯一編排出口）、`_render_picks_table:20`、`_clean:53`、`guard dispatch(isinstance):112-125`、`picks prepend(免guard):126-127`。`guard.py`：`guard:45`（五閘）、`guard_knowledge:91`、`guard_empty_retrieval:137`、`guard_attribution:147`、`HONESTY_CLOSED_SET:20`、`_FUTURE_LEAK:22`。`payload.py`：`PredictionPayload:20`、`KnowledgePayload:40`、`build_prediction_payload:146`。`prompt.py`：`SYSTEM_PROMPT:28`、`build_prompt:102`、`_payload_block:63`。`oai_compat.py`：`chat_completion:96`、`_reply_text:73`、`_resolve_scope:173`。`ollama.py`：`make_llm_fn:53`、`strip_think:38`、`DEFAULT_MODEL:20`。`relevance.py`：`relevant_citations:119`、`picking_intent:159`、`RELEVANCE_FLOOR:41`。`safe_general.py`：`general_safe_answerable:102`。`answer.py`：`honesty_level:38`。

**建構作法**：(1) **單一編排出口**——`advise.advise():34` 是唯一動筆處，`oai_compat.chat_completion():96` 只翻協定。漏斗順序寫死在 advise() 函式體：retrieve_fn → `_clean`（verify_verbatim + is_low_content 濾 junk）→ `relevant_citations` 相關度過濾（**四鏡對抗驗證**，把命中但不相關判成實質空檢索）→（全不相關）`translate_for_retrieval` 英文 fallback 再檢索 → honesty/whitelist gate → build_prompt → llm_fn → guard dispatch → picks 注入。(2) **三敵防護機械化**——guard 把「數字∈payload、引號⊂檢索、無未來語、逆向不翻轉、股名相符」寫成五條正則+集合成員閘。(3) **payload-type dispatch**——`advise():112` isinstance 分派：KnowledgePayload→guard_knowledge，其餘→guard。(4) **弱模型能力天花板的結構性繞道（D4b）**——qwen3:8b 實證會幻覺選哪些股+股名+迴圈重複，故把 picks 從 LLM 手中拿走：`_render_picks_table` 純 f-string 從 payload ground truth 排版，於 guard 之後 prepend（免 guard，因數字皆出 payload）。(5) **零 usage 純正則判定層**——relevance/safe_general/query_translation/answer 全零 ML 零 LLM。(6) **本機限定接縫**——llm_fn 由 `serve_advisor_openai.py:59` wiring 成 `ollama.make_llm_fn`。

**不變式（enforced_where）**：
- 顧問輸出的顯著小數/IC 鄰接數字必須 ∈ `payload.numbers()` 白名單（`guard.py:56-60`，實測 stray IC 0.25→pass=False）。
- 回覆引號內 ≥8 字須逐字 ∈ citation（`guard.py:50-53`）。
- 檢索全空時回覆必為誠實固定句閉集之一（`guard.py:142` `HONESTY_CLOSED_SET` 二句，憲章 v1.25.0 控）。
- 出處斷言閘（第五條）：`guard_attribution:147` `_ATTRIBUTION_OUT` 正則 + citations blob 比對。
- RBAC scope 無身分→預設 fail-closed deny（`oai_compat._resolve_scope:180-194`、`retrieve_all` scope falsy→全 deny）。
- chat_history 所有讀寫以 user_id 收窄（`chat_history.py:41/114` 先驗 owner，IDOR fail-closed）。
- 翻譯 fail-closed：譯文只換檢索 query、不入 citation/guard；任何失敗→None 不 raise（`query_translation.py:75-77`）。

**關鍵常數**：`RELEVANCE_FLOOR=0.30`（死碼傾向，判準已改 `_strong_distinctive` 專詞共現）、`_COST_PCT=0.585`、`DEFAULT_MODEL=qwen3:8b`、`temperature=0.15/num_predict=900/think=False`、`DEFAULT_PORT=8399`、`MODEL_ID=augur-advisor`、`min_terms=2`、`_DEPLOY_FAMILY/CELL=RankRidge/ridge_H60_LO`、引文逐字門檻 ≥8 字。

**gotchas（親驗全 CONFIRMED）**：
- **`advise.py:9` docstring STALE**：仍寫「llm_fn 可接 Claude API 或本地 LLM 或 mock」，但憲章 v1.37.0（2026-07-08）已明文禁外部 LLM、僅限本機推理。advise() 本身不機械強制本機（接受任意 llm_fn），本機限定僅由 `serve_advisor_openai.py:59` wiring 落地——docstring 易誤導「可接雲端」。
- **選股題 guard fail 丟失確定性 picks 表**：`_render_picks_table` 於 guard 之後 prepend（無論 verdict），但 `oai_compat._reply_text:88` 於 guard fail body=NO_KNOWLEDGE_RESPONSE→picks 表一起丟棄→對有真實 payload 的選股題回「知識庫中無此內容」語意矛盾（非對稱 fail-closed 代價）。
- **guard 與 guard_knowledge 負號正則不對稱**：`guard.py:57` 用 `-?\d+\.\d{2,}`（捕負號），`guard_knowledge:121` 用 `\d+\.\d{2,}`（無負號）→ 知識域對負值 sign-blind（實跑：`-0.1392` 走 guard_knowledge pass=True、走 guard pass=False），可誤放行符號相反的編造值。
- `citation_numbers`（`:85-88`）抽 citations **全部**數字 token 入知識域白名單（含頁碼/年份/非逐字引段數字）——放寬面。
- **default `payload_fn=example_payload`**（`oai_compat.py:96,251`）含示範 picks（2330/2317/2454 假 score）→若未覆寫會注入假選股；production serve 覆寫成 empty_payload（潛在陷阱非現行 bug）。
- `_reply_text` 一律隱藏公版「引經據典」逐字區塊（`oai_compat.py:90`，v1.30.0 用戶 directive）；guard 內部仍用 citations 逐字校驗（只隱藏呈現）。僅 Mode B 附加檔顯示逐字區塊。
- **`retrieve_all` scope-deny 在 `retrieval.py:330`**（reader 標 331，off-by-one）。
- **「gemini.py 已刪除」措辭不精**：v1.37.0 為「已移除**擬建**之 advisor/gemini.py」（proposed、從無 git 提交史）；「不存在」正確但「刪除」隱含曾 committed。

**未完成債**：`example_payload` 為 P5 架構測試殘留仍為預設 payload_fn（應改預設 empty_payload）；`build_prediction_payload` 依賴 harness 產物表（未建則 caveat 缺 deflated 地板，graceful 不 abort）；`RELEVANCE_FLOOR`/`best_overlap` 已成死碼傾向。

---

### 4.4 serving + 蒸餾 + 知識引擎 scripts

**▶ 一句話**：三個 stdlib-only 常駐 server 把顧問端到端接起、蒸餾 S1-S5 把 guard 前置到訓練資料生成期、registry 驅動知識 harvest；全綁 127.0.0.1 零 Claude usage。

**做什麼**：分三塊：(1) 三個 **stdlib-only 常駐 web server**（瀏覽器登入→proxy→OpenAI 相容殼→advise()+guard→本地 Ollama）；(2) advisor 自問自答蒸餾管線 S1-S5，把 guard 三閘前置到訓練資料生成期產 SFT jsonl；(3) 資料驅動的全球公開知識 harvest 引擎。

**關鍵檔案:符號**：`serve_chat_ui.py`（對話前台 :8090）。`serve_advisor_openai.py`（OpenAI 相容殼 :8399）。`serve_admin_console.py`（知識控制台 :8500）。蒸餾：`advisor_distill_generate_questions.py`（S2 三情境模板題）、`build_context.py`（S3 真兆 context）、`teacher.py`（S4 骨架）、`validate.py`（S5 硬校驗→SFT jsonl）、`migrate_advisor_distill_ddl.py`。知識引擎：`acquire_knowledge.py`（13 adapter）、`promote_knowledge.py`（EXTID 去重）、`harvest_knowledge.py`（批次驅動 + harvest DDL 唯一住所）、`export_qdrant_index.py`、`setup_predict_role.py`。

**建構作法**：刻意反框架——三個 server 全用 Python stdlib http.server + urllib 手刻（明文避開 Open WebUI 的 HuggingFace 嵌入 crash-loop、無 node/Docker/HF）。拓撲＝薄殼分層：`serve_chat_ui`（同源 proxy + RBAC 登入前台，把身分用 header 傳給殼、把 SSE 逐行 pipe 回瀏覽器）；`serve_advisor_openai`（零編排薄 CLI，只組 llm_fn + 把唯一編排出口 advise() 交給 `oai_compat.make_server`）。蒸餾五步用「界線 A/B/C」隔離（見 §0.1）。知識引擎走 registry 驅動：`acquire` 從 `knowledge_source`（DB）讀 adapter+查詢模板寫 `knowledge_staging`；`promote` 用 MAPPERS dict 分派七類 mapper、EXTID 去重晉升；`harvest` 用 subprocess 逐組合呼叫、`harvest_log` 當 resume 帳本、`pace()` 在 harvest 層限速。

**不變式（enforced_where）**：
- 三個 server 綁 127.0.0.1（`serve_chat_ui.py:692`、`serve_admin_console.py:882` 字面硬編；`serve_advisor_openai.py:38` 是 argparse default 可覆寫）。
- 無 `AUGUR_INTERNAL_SECRET` 前台拒啟動（`serve_chat_ui.py:686` sys.exit）；殼端無機密且未開 `--insecure-loopback-admin` → fail-closed deny、預設非 super（`oai_compat.py:192-194`，紅隊 HIGH 修補）。
- 上傳 license 必 ∈ 白名單（三層：app 檢查 × `webupload.py:16 LICENSES` × DB CHECK）。
- owned_local/local_private 永不外流至外部索引：`export_qdrant_index.py:67 clean_item_sql(access_scope='public')`，withheld 反差誠實印。
- 界線-A：蒸餾產物零進預測 7 package（`setup_predict_role.py:32 FORBIDDEN_PREFIXES` REVOKE + 命名 + AST 三重）。
- 界線-B：context（真實檢索）與 target_response（teacher 示範）DB 分欄（`migrate_advisor_distill_ddl.py:57`）。
- S5 複用生產 guard byte-identical（`validate.py:83` 直接 import guard_knowledge/attribution/empty_retrieval）。
- export CLEAN 對帳：COUNT/PKSET/SELECT 三處共用同一 `_clean_scope`（`:53`，#12）；synced−clean 差 ≠0 → sys.exit（`:264`）。

**關鍵常數**：ports 8399/8090/8500/11434、qwen3:8b/temp0.15/num_predict900/think=False、`RELEVANCE_FLOOR=0.30`、**DP7 GATE 0.55**（S2 out-of-corpus 佔比下界）/ S5 drop 0.40、pbkdf2 `_ITER=240000`、`SESSION_TTL=3600`、`MAX_UPLOAD=300MB`、attach cap 400000、`SEMANTIC_ENTITY_TYPES=('paper','report','document')`、pace 矩陣（openalex0.5/crossref1.0/dbpedia3.0/其餘1.5）、`EXTID_PRIORITY` 全序、`DISTILL_TEACHER_MODEL=claude-opus-4-8`。

**gotchas（親驗）**：
- **任務描述「distill DDL 從 predict role REVOKE」錯置**：`migrate_advisor_distill_ddl.py` 內**沒有**任何 REVOKE；蒸餾產物對 predict role 的 REVOKE 真正機制在 `setup_predict_role.py:32`。界線-A 是三重閘（命名前綴 + AST + DB GRANT）。
- **S3 build_context 刻意用 super scope** `_SCOPE=(True,frozenset(),1)`（`:33`）復現生產失敗路徑——與對外服務 scope（`access_scope='public'` RBAC 收窄）完全不同（此即界線-C 的隔離用意）。
- **Mode B 附加檔繞開 corpus 的 license/access_scope 白名單**（走 retrieve_attached 切段、不查 DB），但 verify_verbatim 仍成立（AttachedCitation.text 是 doc_text 逐字子字串）、guard 照常逐字把關。「繞白名單」≠「繞誠實」。
- **S4 teacher 是骨架**：`_call_teacher`（`teacher.py:64`）直接 raise NotImplementedError。連帶 target_response 全 NULL → S5 產不出 sft.jsonl。整條 S1-S5 已 ready 但實質**斷在 S4**、目前無訓練資料產出（最大 provisioned-but-unwired 缺口）。
- **限速（pace）住 harvest 層、非 acquire 內建**：acquire 對這些知識 API **無內建 rate limit**（不同於 FinMind 三層防護）；acquire 整個 run 是**單一交易**，adapter 中途例外→整批 rollback。
- admin「帳號留空」是 env 緊急後門（`serve_admin_console.py:725-731`，臨時 superuser 等效，標「相容期」）。
- `export_qdrant` 讀取路徑仍走 pgvector（遷移未 cutover）；orphan 比例 >0.5 會 sys.exit 要求 `--rebuild`。
- **generate_questions 的 `ratio<0.55→sys.exit(1)` 不在 stats() 內**（`stats:199` 只 return），真正的閘在 main `:255-257`（親驗行號歸屬修正）。

**未完成債**：S4 teacher 未接線（A/B/C 三機制皆待用戶拍板）；`augur_predict` role DB 層動態 REVOKE 雙閘可能**尚未 apply**（`setup_predict_role.py:82` 自陳「role 尚未建、暫緩實建」，需 `--apply --confirm`）；export 遷移未 cutover、LAYER 硬編 'sentence'；正式 WebUI 整合待拍板。

---

## 5. 測試作為可執行 SSOT

augur 的 `tests/` 不是覆蓋率測試，而是把「三敵零容忍」與治權條文轉成**可自動檢測、可 fail 的架構不變式**。16 支測試的核心設計決策：SSOT 委派（test 只 import 治權原文、不重寫判準）、**負向自證**（沒有能證明自己會抓到違規的守門測試視為假守門）、復用 production 路徑、誠實 skip 非假 pass。

### 5.1 測試 → 所護不變式對映

| 測試檔 | 護的不變式 | 機制型態 |
|---|---|---|
| `test_philosophy_isolation.py` | 預測 7 pkg 零 import 素養層 + RBAC/chat 字面旁路 + resolver/chat_history 對位 | 薄殼委派 `import_isolation.check_isolation()`（實跑零違規） |
| `test_release_lag_antileakage.py` | T 不用 release>T 財報/月營收 + **負向自證**（leak_mode 假 gate 使 pctile 0.625→1.0 必相異） | 對真 production build 注入 `ZZTEST_LEAK` synthetic、注入前 assert 零碰撞、測試後硬 DELETE |
| `test_predict_role_isolation.py` | augur_predict role 對素養表 SELECT 拒/預測表准/輸出可寫 | DB `has_table_privilege` 查詢；role/DB 缺誠實 skip |
| `test_advisor_guard.py` | 引文逐字/數字白名單/未來洩漏/逆向翻轉 + P8 雙源，正反例全覆蓋防 regex 靜默放行 | 正則+集合純函數閘、monkeypatch 替身免 DB |
| `test_advisor_dialogue.py` | strip_think fail-closed、M2（注入 retrieve_fn 後驗 verify_verbatim）、T1-a（離題 decline）、引經據典外洩回歸釘死 | monkeypatch verify_verbatim/honesty_level |
| `test_rbac_enforcement.py` | clean_item_sql 預設 deny/'AND false'、local_private owner 收窄、resolver fail-closed | 純函數閘 + DB 恆 deny |
| `test_evaluation_core.py` | effective_t_hac 正自相關收縮 t（G8）、label t+1 不漂移、walkforward embargo gap + expanding 不重疊 | 純函數 in-memory |
| `test_knowledge_vectorindex.py` | search 只回 (pk,distance) 永不回內容（紅線③）、filter 封閉集 fail loud | 真跑 Milvus Lite（非 mock） |
| `test_knowledge_embedspec.py` | slug pin 字面常數（`ime5s30b1cd`，`:17`）逼有意識同步 | 常數閘 + 長度預算 |
| `test_generic_schema.py` / `test_reconcile.py` | Dealer is_after_hour 須入 PK、前導零不轉 float、verdict incomplete→fail-closed | 純函數（實證 2026-06 血淚） |
| `test_finmind.py` / `test_fred.py` | 5xx 退避、429 honor retry_after、單日型移 end_date；FRED vintage PIT + 超單頁明拋 | 退避/PIT 迴歸 |
| `test_models_ranker.py` | RankRidge≡baseline B2 逐值 np.allclose 防雙軌漂移、feats_hash order-invariant | 純函數 |

（N5/N6/N8 等其餘對話族情境碼同屬 `test_advisor_dialogue.py` 的內部案例編號。）

### 5.2 測試套件實跑真相（親驗，多處 REFUTED）

- **REFUTED「anti-leakage DB 注入測試在 CI 全 skip」**：本環境 DB 可用，注入型/整合型 anti-leakage 測試**實跑並通過**，僅 predict_role 3 支因 role 未建而 skip。「全 skip」只在無 DB 情境成立。
- **REFUTED「numpy/jieba 未裝、125 通過/14 fail」**：專案有兩 venv——`.venv` 無 numpy/jieba，但 `venv/` 有 numpy 2.4.6 + jieba。以 `venv/` 實跑全 `tests/` ＝ **165 passed / 1 failed / 3 skipped**。「125 通過/14 ImportError fail」是缺件降級環境、非 canonical。
- **REFUTED「測試全綠」**：存在 1 支真實 FAILED——`test_advisor_dialogue.py:161 test_chat_completion_guard_pass_has_verdict_tail`（guard-pass 回覆被前置 as-of top3 區塊，startswith 斷言失敗），與 numpy/jieba 無關。
- **REFUTED / 混淆「引經據典/999.99 not in body :165/:224」**：`:173` 斷言「引經據典」not in；`:224` 斷言的是 `'0.9999' not in body_shown`（非 999.99）；999.99 是另一支 `test_gk_unverified_quote`（`:83-86`）斷言它**在 issues 內**（語意相反）。
- **負向自證的隱形耦合前提**：`margin_cycle.py:44` 以「模組屬性 `release_lag.financial_released`」呼叫才使 monkeypatch 切到 production；若改綁名匯入，負向自證會失效。
- **DB 硬閘實效依賴部署 apply**：predict_role DB 測試在無 DB CI 全 skip、非 pass——隔離硬閘實效依賴部署方真的跑過 `setup_predict_role.py --apply`。

---

## 6. 跨系統 meta-patterns（建構房規）

反覆出現的「房規」——這些是理解 augur code 的最高槓桿抽象：

1. **single-orchestration-exit（單一編排出口）**：一個管線只有一個動筆處，其餘只是 adapter。features 的 `panel.build_panel`（唯一常態寫 feature_values）、universe 的 `_select_core`、advisor 的 `advise()`、evaluation 的 `build_long_portfolio`（backtest≡live）。

2. **double-gate 縱深防禦**：一條紀律配兩道異質閘。隔離＝AST 靜態閘（import_isolation）+ DB 動態閘（setup_predict_role GRANT）；准入＝Python 應用層 + DB CHECK；owned_local＝寫入層語意 + DB vocabulary CHECK。**但要注意雙閘保護的方向**——見第 11 節 owned_local/prediction_values 兩處 over-claim。

3. **fail-closed 為預設**：RBAC 任何異常→(False,∅)；guard 任一閘不過→退回誠實固定句；reconcile incomplete→fail；identity 壞格式→None。空集＝deny 非「不濾」。

4. **閾值住 DB（#29b）**：risk_policy、judgestop_threshold、knowledge_source registry 都把「會變的判準參數」外置到 DB，擴閾值＝UPDATE 一列零改碼（但新增**類型**仍是 code/DDL 變動）。

5. **builder-owns-DDL vs explicit-migrate**：計算型表（feature/universe/audit/philosophy）自寫 `CREATE TABLE IF NOT EXISTS` 冪等自建；運維/登錄/schema 型表走 `scripts/migrate_*_ddl.py` 顯式遷移。API 原始表則走 generic auto-schema（第三條路）。

6. **純 kernel + I/O 分離**：`reconcile.compare` / `catalog.optimal_mode` / `walkforward.splits` / `revalidate_verdict.evaluate` / `metrics.*` ——都把「算什麼」與「從哪取/往哪寫」切開，讓 kernel 可單測、可跨檔複用。

7. **LLM-ceiling → mechanical-workaround**：弱本機模型（qwen3:8b）能力天花板明確，故 D4b 把 picks 從 LLM 手裡拿走用 `_render_picks_table` 確定性排版、prompt 刻意移除照抄誘餌、guard 兜底三敵。不靠 prompt 自律，靠機械閘。

8. **provisioned-but-unwired 明碼**：框架先掛好、接線待拍板（BACKFILL_DEFERRED 空集、concept_graph 零呼叫端、S4 teacher raise、augur_predict role 未 apply、stock_philosophy_tag 零 writer、fetch_dedicated 自動路徑不可達、DD 熔斷 dormant、附錄 C 四項理論缺口）。這是**特徵不是缺陷**，但讀 code 時必須知道「哪些路目前不通」。

9. **SSOT-委派、禁 inline 複本（#12）**：deflation per-period 口徑、corpus CLEAN 述詞、drawdown_series、estimator 超參——都設計成單一住所。**但親驗發現數處孿生字面複本靠人工同步無機械綁定**（ranker↔baseline 超參、S4 stats inline CLEAN、corpus↔DB license CHECK），是 #12 的實際脆弱點。

10. **negative self-test（負向自證）**：anti-leakage 測試每個「不洩漏」斷言配一個 leak_mode 版證明測試路徑真能被洩漏影響——沒有負向自證的守門測試＝假守門。

---

## 7. End-to-End 兩個故事

### 7.1 預測流：raw → prediction_values（對映 12-PHASE 遞增）

1. **取數（≈PHASE 1-2b）**：`scripts/full_market_sync.py` → `sync.sync_all` → `finmind.fetch`（三層限速）/`fred.fetch`（vintage PIT，FRED 前置＝PHASE 2b）→ `ingest.store`（#4 intraday 守門）→ `generic_schema.provision_and_upsert`（自動建表冪等 upsert）→ `TaiwanStockPriceAdj` 等 API 原始表 + `data_audit_log`。（infra log 表 PHASE 1 最早建。）
2. **登錄**：`catalog.build` 探測每 dataset → `dataset_catalog`/`column_catalog`（怎麼抓的元資料）。
3. **對帳（PHASE audit gate）**：`reconcile.verdict` 三-clause attestation，每 PHASE 過閘才進下一。
4. **算特徵**：`scripts/build_feature_panel.py` → `panel.build_panel`（每股兩段 transaction fan-out 5 模組）→ 35 特徵 → `feature_values` EAV。月營收/財報經 `release_lag` 發布日 gate（#8）。
5. **選核心股（≈PHASE 8，as-of/完整性判準）**：`scripts/build_core_universe.py` → `core_gate.build_universe_asof`（逐 t PIT 四道閘）→ `core_universe_asof`（消完整度 survivorship）。
6. **訓練**：`scripts/train_ranker.py` → `baseline._fold_xy` 疊 (X,y) → `RankRidge.fit` → `artifact.save`（.joblib）+ `registry.register`（`model_registry`）。
7. **驗證**：`baseline.run_ladder`（rank_ic + HAC t）+ `portfolio.run_backtest`（net Sharpe/MaxDD/Calmar）+ `deflation.deflated_floor`（DSR 扣血）。持續再驗證由 `revalidate.py` 逐輪重跑 + `revalidate_verdict.evaluate` 兩軌三態判停。
8. **出單**：`scripts/predict_asof.py` → `registry.latest`（PIT ≤as-of）→ `artifact.load` → `estimator.predict` → `portfolio.build_long_portfolio`（top-decile long）→（可選 `execution.apply_overlay` 風控）→ `prediction_values`。

（逐 PHASE 精確標籤 SSOT 在憲章第五部；此處為粗粒度對映，PHASE 不可跳、不可改 order、每階段過 audit gate 才進下一。）

### 7.2 顧問流：browser → chat_ui → advisor → Ollama

1. 瀏覽器 → `serve_chat_ui:8090`（`identity.verify_session` 登入閘）→ 同源 `/chat`。
2. → urllib POST `http://127.0.0.1:8399/v1/chat/completions`（帶 `X-Augur-Internal` 機密 + `X-Augur-Session`）。
3. `oai_compat` 殼驗機密後 `_resolve_scope`（fail-closed）→ `picking_intent` 判選股意圖 → `build_prediction_payload`（真 as-of 預測）否則 `empty_payload`。
4. → `advise()`：`retrieve_all(scope)` 檢索 `philosophy_work`/`knowledge_item` → `verify_verbatim` + `is_low_content` 過濾 → `relevant_citations` 相關度 →（空）英文 fallback → honesty/whitelist gate → `build_prompt` → `ollama` llm_fn（`strip_think`）→ **Ollama qwen3:8b @ localhost:11434** → guard 三閘 → picks prepend。
5. → `_reply_text`（隱藏公版引文區塊、guard fail→NO_KNOWLEDGE_RESPONSE）→ SSE 逐行 pipe 回瀏覽器。

**注意**：這條流目前 `risk_policy` 表未建（風控 dormant）；顧問層對所有 DB 表唯讀（僅 chat_session/chat_message 讀寫且 owner 收窄）。

---

## 8. 治權 → code enforcement wiring 表

| 法律 | 機械 enforcement | 型態 |
|---|---|---|
| #1 零幻像 | `core_gate` 純完整度、`guard` 數字白名單、DB CHECK `<>'ai_generated'`（`migrate:149-150`）、`_coerce` 不引 float（值路徑） | DB 純函式 gate + 正則 + DB CHECK |
| #8 anti-leakage | `import_isolation.check_isolation`（AST+字面+對位+scripts）、`release_lag` 發布日 gate、`walkforward.splits` embargo=h+62td、`core_universe_asof` PIT、FRED realtime_start | AST 稽核 + 純日期算術 + 索引切分 + DB PK |
| #8 素養→預測單向 | `import_isolation` FORBIDDEN + `setup_predict_role` GRANT（**保護此方向、非 prediction_values 回讀**） | AST 靜態閘 + DB 動態閘 |
| #11 提拔關卡 | `metrics.effective_t_hac`（禁裸用 iid）、`verify_candidate_promotion.py`、五鏡 `five_mirror` 三條件 AND | 純函式統計校正 |
| #14 經濟終關 | `portfolio` net=gross−成本、`deflated_floor` DSR、MaxDD/Calmar | 純函式 |
| #15 誠實 | `HONESTY_CLOSED_SET` 二句、`guard_empty_retrieval`、缺列不補、absent_combos 揭露、reconcile incomplete→fail | 型別/常數閘 + fail-closed |
| #12 SSOT | config 密鑰、evaluation helper、corpus CLEAN、harvest DDL 唯一住所（**部分靠人工同步無機械綁定**） | import 委派 |
| owned_local | `webupload.py:16 LICENSES` + DB `chk_itext_access_scope`（**兩條獨立 vocabulary CHECK、無跨欄綁定**、Python `acquire_local_files.py:63-65` sys.exit 才強制綁定） | 應用層 + DB vocabulary CHECK |
| RBAC fail-closed | `access.resolve_allowed_domains`、`corpus.clean_item_sql`、`_resolve_scope` | SQL 述詞 + guard 分支 |
| 隔離不變式常備 | `tests/test_philosophy_isolation.py`（薄殼委派 audit 模組） | 常備測試 |

---

## 9. 關鍵常數 / 不變式速查

- **as-of / FREEZE**：2026-05-31（生產 payload 取自 DB max(panel_date)、demo 才 hardcode）
- **三敵 = 三基石**：①假資料 #1 ／②偷看未來 #8 ／③自我欺騙 #15
- **PIPELINE 7 package**：features/models/universe/evaluation/ingestion/audit/catalog（不含 core、不含 philosophy）
- **FORBIDDEN 3 前綴**：augur.philosophy / augur.advisor / augur.knowledge
- **12-PHASE**：PHASE 0-11 + 2b（FRED 前置子階段）＝維運矩陣 13 列；不可跳、不可改 order、每階段過 audit gate
- **FinMind 限速**：MIN_INTERVAL=0.9s、QUOTA_COOLDOWN=1800s、QUOTA_HEADROOM=200
- **FULL_START=1990-01-01**（僅查詢下界、非全史保證）
- **型別下限**：VARCHAR(255) / NUMERIC(20,6)、只擴不縮
- **walk-forward**：H≥252 禁入、embargo=h+62td 逐折真實交易日保證下界
- **成本**：COST_TW=0.00585（散在 caller、非 eval 模組常數、`run_backtest` 預設 cost=0.0）
- **top-decile**：TOP_FRAC=0.1（caller override；helper `build_long_portfolio` 函式預設實為 0.2）
- **35 特徵**：19 純還原價 df + 16 查表；recency gate 45 日；chip E 類真零容忍 14 日
- **release_lag**：REVENUE_DAY=15 / FIN_LAG_QUARTER=45 / FIN_LAG_ANNUAL=90（法定期限）
- **嵌入**：e5-small 384 維、TEXTNORM_VER=1、jieba HMM=False（floor 非 pin）
- **誠實閉集**：「知識庫中無此內容」/「知識庫存有此著作但歸屬未驗證,不予引用」（僅二句）
- **引文閘**：≥8 字逐字 ∈ citations；數字閘 ∈ payload.numbers()
- **RELEVANCE_FLOOR=0.30**（死碼傾向，判準已改專詞共現）
- **ports**：advisor 殼 8399 / chat 前台 8090 / admin 8500 / Ollama 11434
- **本機 LLM**：qwen3:8b / temp 0.15 / think=False / num_predict 900
- **憲章修訂**：v1.0.0→v1.39.0 共 41 版

---

## 10. 未完成債 / 下一棒

**跨系統最大缺口**：
- **models（F3）核心訓練階段是階段 A 骨幹**：端到端已跑通，但 survivorship 債 b 未閉環（`core_universe_asof` 實為當前存活名單、as-of IC 帶樂觀偏誤，`train_ranker.py:36` 明標）。
- **蒸餾管線斷在 S4**：`teacher._call_teacher` raise NotImplementedError → 無 gold → S5 產不出 sft.jsonl（A/B/C 三機制待用戶拍板）。
- **augur_predict role 尚未 apply**：DB 層動態隔離閘 provisioned-but-unwired（`predict_asof` 走預設 role、`DB_PARAMS_PREDICT` 未實作）。當前隔離主要靠 AST 靜態閘 + 命名。
- **風控 live dormant**：`risk_policy` 表未在本機建、DD 熔斷無歷史序列可評估；且 doctrine「vol-target × trend」規則地板未實作（現為 DD/cap/turnover）。
- **concept_graph（L6）零呼叫端**：查詢介面已建但無接線，依賴 S4 stats 層 populate。

**憲章附錄 C 自陳的四項理論缺口（by-design open debt）**：① 正式 ports/adapters（Hexagonal）介面（現分層夠用）；② data-contract schema 版本化；③ as-of/bitemporal 形式化（vintage 表）；④ train/serve 一致性（俟上 serving）。

**RBAC 多群組政策層待人拍板**：v1.28.0/v1.29.0 的 superuser + 受控多群組機制已建（`access.py` + DB CHECK），但多使用者群組實際 provisioning 屬「永遠決策層人拍板」的待決政策層、非全自動。

**已備位但未接線 / 部分落地**：
- `stock_philosophy_tag` 零 writer；`philosophy` 的 validated_ic/econ 全 NULL、status 全 'untested'（假說須過四道漏斗+#14 回填的 backlog）。
- `macro.py` 31 檔 FRED 未 wire 進 feature_values（總經因子如何在 model 層合流未落地）。
- export Qdrant 遷移未 cutover（讀仍 pgvector、LAYER 硬編 sentence）。
- `BACKFILL_DEFERRED` 空集、`fetch_dedicated` 自動路徑不可達、`concordance_lookup` 缺 RBAC 閘未接。

**資料凍結是明文延後的技術債**：FREEZE 子條把「接入最新資料」明文延後至「整體系統完美後」——現階段不追新資料、不掛排程（設計選擇非缺陷）。

**已知未修 bug / stale**：
- generic_schema 非「date」名之日期欄，樣本不含 sentinel `-1` 會誤推 DATE（`test_generic_schema.py` 記錄但未修）。
- guard 數字閘整數/1 位小數邊界屬「執5 待修判準」、測試明載不鎖。
- 多處 stale docstring：catalog `refresh` 不存在、philosophy `bootstrap` 稱 6 表（實 9）、advise.py:9 稱可接 Claude API、corpus 稱四值白名單（實 5）、models cur_feats 防漂移未實作。

---

## 11. 對 v2（20260709）之承重差異摘要（親驗）

v3 相對 v2 的兩大結構性改進：(a) 半-2（knowledge/philosophy/advisor/serving+蒸餾）與半-1**等深覆蓋**；(b) 全面採用對抗驗證後的正確版。正文各 gotcha 已就地標「親驗修正」，此處只留**承重差異摘要表**（非承重的行號 off-by-one 與 stale docstring 已就地標於正文，不再重列）。

### 11.1 REFUTED（承重宣稱推翻，正文一律採驗證版）

| # | v2 原宣稱 | 驗證後正確版 |
|---|---|---|
| 1 | owned_local 隔離由 DB CHECK `chk_itext_owned_local_private` 綁死（已驗機械不變式） | **無此具名約束**（DDL 與 live DB 皆無）。綁定由 Python `acquire_local_files.py:63-65 sys.exit` 強制；DB 只有兩條獨立 vocabulary CHECK，`license='owned_local' AND access_scope='public'` 不會被任何 DB CHECK 擋。且本機 live DB 之 license CHECK 尚未含 owned_local（code↔DB 漂移）。 |
| 2 | prediction_values 禁被回讀當特徵由 AST+DB GRANT 雙閘強制 | 雙閘保護「素養→預測」方向；prediction_values 被 GRANT 給 predict role 可讀寫，無機械閘阻止 pipeline 讀它當特徵，僅 DDL COMMENT 約定。 |
| 3 | grep 確認 augur_predict 僅在 setup 腳本自身 | role 名亦在 `tests/test_predict_role_isolation.py:18`（結論「role provisioned-but-unwired」仍成立）。 |
| 4 | 測試套件全 skip / 125 通過 14 fail / 全綠 | canonical＝165 passed / **1 failed** / 3 skipped（`venv/`）；存在真實失敗 `test_advisor_dialogue.py:161`。 |

### 11.2 過度宣稱 / 範圍限縮（正文採限縮版）

| # | 收斂為 |
|---|---|
| 5 | as-of 2026-05-31 hardcode 只對 demo payload；生產 `build_prediction_payload:159-164` 取自 DB max(panel_date)。 |
| 6 | 「panel 唯一寫 feature_values」→「唯一**常態生產**寫入者」（另有 8 支離線 verify 腳本 INSERT）。 |
| 7 | audit「全層唯讀絕不碰生產」：`heal_by_date` 經 sync 寫生產 raw 表為例外。 |
| 8 | 「byte-level attestation」實為正規化後值相等（非原始 byte）。 |
| 9 | `git_sha` 非凍結（每次 ON CONFLICT 覆寫）；凍結的是 feats_hash/seed/family/horizon/train_span/asof_snapshot。 |
| 10 | config 是唯一密鑰 reader、非唯一 env reader（OLLAMA_*/FINMIND_QUOTA_GATE 直讀 env）。 |
| 11 | 精度不變式只對值路徑成立（`_digits` 有 float() 但只定 NUMERIC 寬度）。 |
| 12 | universe 所有「實測」數字是 config-scoped（`--since 2014 --exempt-revenue-financial`）；原表現況為 35 面板、intersection=28（非 34）、required=971。 |
| 13 | 「core 股必然齊 baseline 34 特徵」在豁免配置下無機制保證（僅 4 檔保險 core 經驗成立）。 |
| 14 | build_long_portfolio 有 3 caller、deflation 有 4 importer（reader/docstring 皆低估）。 |
| 15 | RankRidge≡baseline B2 靠人工孿生字面複本無機械綁定、robust=True 時分歧；RankRidge seed 是無效裝飾。 |
| 16 | predict_asof/harness 的 feats_hash 防漂移未實作（cur_feats 死變數）。 |
| 17 | 蒸餾產物對 predict role REVOKE 在 `setup_predict_role.py:32`，非 `migrate_advisor_distill_ddl.py`（後者無 REVOKE）。 |
| 18 | 「gemini.py 已刪除」→「擬建、從無 git 提交史」（v1.37.0 移除的是擬建檔）。 |

### 11.3 UNVERIFIABLE（誠實標明未親驗、正文出現處已加 inline caveat）

- deflation「DSR 高估 ~14pp」（deflation docstring-sourced，未獨立複現）。
- survivorship incumbency＝−16.5%（1.20→1.00）、下市偏誤 +0.0023 Sharpe（`survivorship_economic_verdict.py:9` docstring，未在 DB 重跑複現）。
- deflation N=8 過 95.8% / N=16 未過 93.6%（`deflate_headline_verdict.py:134` inline 註記，未在 DB 重跑複現）。
- philosophy `is_low_content` 52/126,609≈0.04% 與 e5-small 0.80~0.88 窄帶（docstring-sourced，無 DB 連線不可驗）。
- 原則精華「255 treaty + 77 迭代去重成 20 條」provenance（背景陳述，未在正文核實）。
- `augur_predict` role 是否已 apply（部署狀態，本次未驗）。

---

*報告完。所有承重宣稱附 file:line / 表名 / 常數；凡 REFUTED 一律採驗證版並於第 11 節留痕（#15）。docstring-sourced 未複現數字於正文出現處即標明。此報告為理解基準，不含未親驗數字之搬運。*