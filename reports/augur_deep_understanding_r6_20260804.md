---
status: final
series: deep_understanding
round: r6
supersedes:
  - reports/augur_deep_understanding_r5_20260803.md
---

# augur 深化理解報告 r6（2026-08-04）——優化地基・第六輪（S1→S5 落地日收斂）

> **性質**：[I] 全專案現況之深化理解，作為 `reports/augur_project_optimization_plan_r6_20260804.md`（另檔）之依據。**不創設治權判準**、不改任何 [N] 文字。
> **承接**：r5（08-03 夜）→ **本檔 r6（08-04，S1→S5 閉環單日落地收斂）**。
> **self-reported（CLAUDE #32a）**：本檔判讀為 AI 自陳；數字附 (a) stdout／(b) DB／(c) audit 路徑；子系統章節由 explore 子代理唯讀勘查產出，本檔整理彙編。
> **定版**：五路 explore **5/5 已收**（KH/進化/sim/arena；S3–S5 現況債；src 結構；scripts 全量分類；治理層）＋本檔親查 12 項 DB 真值錨。本檔為 r6 定版；優化計畫書另見 `reports/augur_project_optimization_plan_r6_20260804.md`。

---

## §0 一頁摘要

### 0.1 專案體量（本輪首次全量盤點，定版數字）

| 維度 | 數字 |
|---|---|
| `src/augur/` | 16 package／104 library 模組（100% `if __name__=="__main__"`；104/104 具等價 `--selftest`） |
| `scripts/` | 354 支 .py＋7 支 .sh，歸 12 功能桶（最大＝knowledge/KH ~75、archive/migration ~93） |
| 根目錄 shell／`tools/`／`ops/` | 9 支換機／封存工具；4 個 MCP 套件；GPU 驗證＋githooks＋歷史 runbook |
| 生產排程 | 15 條 cron＋6 常駐服務＋7 timers（2 個 disabled 待開閘） |
| 治權層 | L0–L7＋5 份領域治權檔（CLAUDE.md v1.35＝35 條）；RULING 現至 043；AL 現至 047；audits/ 現 334 檔 |
| DB | 350 表；`feature_values` 854 萬列；`knowledge_item` 28.5 萬列 |

### 0.2 r5→r6 當日結構增量（S1→S5 閉環單日跑通一整圈）

| # | 增量 | 證據 |
|---|---|---|
| 1 | **S1 資料補至 2026-08-03**＋核心宇宙重建 225 股（完整入不完整排） | `audits/DATA-FILL-TO-20260803-20260804.md`；`audits/S1-CORE-COMPLETE-ONLY-EXECUTED-20260804.md` |
| 2 | **S2-KH L1–L3**：市場軸探針 15→21；OpenAlex promote 19（全文 license 阻擋 19＝誠實終態）；語料品質仍 spurious-high | `audits/S2-KH-L2/L3-EXECUTED-20260804.md` |
| 3 | **S3 Wave A/B EXECUTED**：組 1–7 覆蓋（38 feat／113 panel）＋組 8–9 候選材料化（85,050 列）＋市場 PIT 刷新 | `audits/S3-WAVE-{A,B}-EXECUTED-20260804.md` |
| 4 | **S4 taxonomy A–G 全波次收口**：≈12 大類／≈35 變體族普查完成；生產熱路徑仍 Wave A 三臂 | `audits/S4-WAVE-{A..G}-EXECUTED-20260804.md` |
| 5 | **C2 閉環（S4↔S5）雙向跑通**：正向 OOS（`S5-OOS-20260804.md`）＋回饋 backlog（`S4-REOPT-BACKLOG-20260804.md`） | `audits/LOOP-S4-TO-S5-EXECUTED-20260804.md`／`LOOP-S5-TO-S4-OPT-EXECUTED-20260804.md` |
| 6 | **API 有界解凍**（INV1∧INV2 成立）但**仍否**放量／Dividend／寬窗 | `audits/API-THAW-20260804.md` |

**live DB 真值錨（本檔親查，2026-08-04 15:3x+08）**

| 錨 | 值 |
|---|---|
| 表總數 | **350** |
| `feature_values` | **8,540,787** 列／38 特徵／113 panel／max **2026-06-30**／3,094 distinct stock_id |
| core 宇宙 | **225**（asof 2026-06-30） |
| prodset | active **3**／removed 8 |
| `model_registry` | **26** 列／**7** 族 |
| `fred_series` | max **2026-08-03** |
| `TaiwanStockPrice`／`PriceAdj` | max **2026-08-03** |
| `market_direction_feature` | 82,665 列／20 特徵／max 2026-06-30 |
| `feature_candidate_values` | 475,324 列 |
| `knowledge_source` | 3,605／`knowledge_item` **285,259** |
| `measure_registry` | 11（尺 SSOT，非全量） |
| `world_concept_registry_current` | 17 |

**一句話現況（相對 r5「執行力在元閘與 WM 試點上已動刀」）**：r6 補一句——**S1→S5 predict 閉環的「普查覆蓋」在單日內大幅推進（S3/S4 全波次、C2 雙向），但「生產熱路徑」幾乎未變（仍 Wave A 三臂＋prodset 3）**——普查廣度與生產深度是兩條不同曲線，前者今日衝很快，後者仍受 dgate pass=0／#14 經濟終關把關，尚未有新族翻越。

**架構體檢一句話（本輪首次全量結構盤點）**：augur 的**機械閘密度與治權留痕紀律**遠高於一般專案（16 package 全數不變式寫成程式、104 模組 100% 具自測、334 份 audit 逐步留痕、四層治權地圖），但**體積只增不減**（scripts/ 12 桶多處同型冗餘未收斂、audits/ 帳本式增長）與**少數接線斷點**（`action_log` 零消費端、`l2-deliberation`/`knowhow-refresh` timer 待開、CS 版號漂移）並存——結構強項是「閘在、留痕在」，結構債是「閘與閘之間的收斂／接線」尚未追上普查速度。

---

## §1 覆蓋方法（誠實）

| 方法 | 做了什麼 | 標級 |
|---|---|---|
| **DB 直查（psycopg2）** | 表數／feature_values／core/prodset/registry/fred/market_direction/candidate/knowledge/measure/concept 等 12 項唯讀 count/max | (b) DB，本檔親驗 |
| **explore 子代理×5（fan-out）** | src/augur 16 package 結構；scripts 362 支＋root shell 分類；治理層（constitution/specs/docs/CLAUDE.md/HANDOFF）；KH/進化/sim/arena；S3-S5 現況債 | [I]；唯讀勘查，未改檔案 |
| **本 session 歷史動作** | 本輪對話內親執行 S3-WAVE-A/B、S4-WAVE-A–G 之 GO/EXECUTED（見各 audit） | (a) stdout＋(b) DB，第一手 |

### 1.1 未覆蓋風險（顯性）

- 未逐字重讀靈魂／原則精華／領域大憲章全文（沿用治理層子代理摘要＋既有引用）。
- 未重跑 `check_cmd_matrix.py`／`check_false_assertions.py`／vendor scan 全量（沿用既有稽核結論時點標註）。
- 未親驗 direction_gate 逐列 status（子代理報告引用既有 audit 之 pass=0／approved 11／evaluated_fail 12 分布，本檔未重查）。
- project-memory 索引新鮮度未查（本輪 recall 於 Wave-B 段落已用過，未見過時警語，暫信任）。

---

## §2 軸：知識管線／進化（TWEVO/PME）／Sim 校準／Arena

> 來源：explore 子代理唯讀勘查（[知識/KH/進化/sim管線探勘](9a8cae6b-9b50-49c5-90f2-a78533a28c3f)），本節整理其發現、補充交叉引用。

### 2.1 S2-KH 三層知識管線

**架構**：`knowledge_source`（registry，3,605 列）→ `acquire_knowledge.py`（12 adapter：OpenAlex/Crossref/arXiv/Semantic Scholar/Wikidata/Gutenberg…）→ `knowledge_staging`→ `promote_knowledge.py`（冪等晉升）→ `knowledge_item`（285,259 列）→ 全文終態鏈（`fetch_pd_fulltext`／`fetch_oa_fulltext`／`fetch_confirmed_fulltext`／`fetch_entity_fulltext`）→ `build_sentences.py`（確定性 regex，零 AI 改寫）→ `embed_knowledge.py`（三粒度→pgvector）。

**准入四閘**（`admission.py:37`，fail-closed）：source active（人 TTY 核准）∧ license 白名單（`public_domain/cc-by/cc-by-sa/cc0/owned_local`）∧ owned_local⇒local_private（DB CHECK 雙保險）∧ source_type 白名單且禁 `ai_generated`。

**債**：全文 `unattempted` 曾達 121,389（日班回填中）；L3（08-04）19 篇 DOI 全文落地 **0**（license/OA 阻擋）——誠實終態，非漏做。

### 2.2 RKI/PME 探針與 S2-KH L1–L3（本輪落地）

| 層 | 做了什麼 |
|---|---|
| L1 | 盤點：active 15/15、runs=7；**市場特徵組交互幾乎空白**（現役探針偏哲學／太陽能／AI 元層）；排 P0＝組 8/9 |
| L2 | INSERT 6 市場軸探針＋5 glossary；active→**21**；六針 dry-run 全 `no_corpus` |
| L3 | OpenAlex×6 查詢→promote 19；OA 全文阻擋 19／落地 0；`no_corpus` 解除但 **spurious/ungrounded high** |

**核心判讀**：探針有 hit **≠** 概念橋成立 **≠** G-PROM——本輪誠實記帳品質缺口，未虛報進度。

### 2.3 進化（TWEVO／PME／prodset）

- **熱路徑**：TWEVO 夜輪 cron 23:00（`run_evolution_iteration.py` I0–I9；I3 實測 7–10hr/輪）；`heavy_slot` 單槽互斥，搶不到寫 `evolution_deferred_work`（rc=75）非 silent skip。
- **八閘**：G-PROM（as-of IC／HAC-t≥2／≥3 seed）、G-ECON（#14 淨 Sharpe＋MaxDD floor）等 8 閘 all-green 才可 APPLY；APPLY 須人 `--queue-id --allow-apply`（一次一顆，禁 `--force` 跳閘）。
- **prodset**：active **3**（08-02 hugo 逐顆親簽，556/599＝首兩顆引擎自掙晉升）。
- **V2-SUNSET 澄清（重要）**：原 deadline 2026-10-31 **已 superseded**——07-31 GATE-raise 為 V2-SUNSET-r2（deadline 07-31），同日 TTY 親簽 `evaluated_pass`（basis=R1）→**三軸續命**。`evaluated_pass=0` 語意＝**`direction_gate` 之 arena 方向門從未被評估**（NULL，非評後不合格）。
- **結構債**：SUNSET consequence（三軸整體停止）**無機械載體**——kill_switch 四 scope 全 clear、無封存腳本（`settle_sunset_gate.py` 自陳）。

### 2.4 Sim 校準（SIM-CAL-R1）

W5（`run_sim_calibration_cell.py` 產格／`settle_sim_outcomes.py` 結算）→W3（`evaluate_sim_calibration.py` 五臂：live/ceiling/floor/shuffled/mismatched）→W4（`decide_sim_verdict.py` 只寫 killed/undecidable，**promoted 須人三鎖親簽**）。**sim 尺（校準品質）與 predict 尺（IC/經濟價值）分離**，各自預註冊門，互不冒用。GARCH（`simulate_mc_paths.py`／`simulate_portfolio_risk.py`）＝風險側歷史重抽／情境重放，**非**預測 tilt。

### 2.5 Arena

- 每日 cron：20:00 `run_arena_daily_pipeline.py`（sync→macro→IV→方向特徵→round）；21:30 結算＋scoreboard。
- **頂部雙機械閘（AND）**：閘一 `direction_gate` approved `dgate_arena%`；閘二 `arena_admission_gate` G1（as-of PIN 2026-06-30）＋G2 anti-leakage。
- **債（M-G10）**：`data_id_required` 之 6 表（含 TRI）sync 推不動——接線已備（`AUGUR_DIM_SYNC=1`）但預設關、須另授。

### 2.6 跨子系統一句總結

五個子系統共享同一治理型態：**機械閘 fail-closed＋人閘（TTY 親簽）不可代簽＋帳本終態不可逆**；共通債＝「閘的文字凍結了，但解釋閘的程式與 consequence 的機械載體未必跟上」（SUNSET consequence 無載體、M-G10 維度斷檔、市場 KH 語料 spurious-high）。

---

## §3 軸：S1→S5 predict 閉環現況（本輪 S3/S4/S5/C1/C2 全景）

> 來源：explore 子代理（[S3–S5 現況債探勘](02581897-0030-4e31-8df8-db4144a14056)），交叉本 session 親執行之 Wave 帳。

### 3.1 S3 特徵軸

- Wave A（組 1–7）／Wave B（組 8–9）**EXECUTED**；三層表分工：`feature_candidate_values`（staging）→`feature_values`（canonical）→prodset（`evolution_production_feature_set.set_status=active`）。
- **prodset active 3**：`cycle_position_252d`／`inst_cumflow_position_120d`／`lending_fee_rate_mean_30d`。
- 債：Wave B 多 seed 正式表 in-flight；4 候選未晉升；組 12–13（序列窗／圖邊）＝S4 Wave C/D/E SKIP 根因。
- 待授：`S3-WAVE-C-go`／`S3-WAVE-D-go`／`S3-WAVE-E-go`。

### 3.2 S4 模型軸

- **Wave A–G 全收口**；已試 distinct 架構 **5**（RankRidge／RankGBDT／DailyGBDT_cal／MktLogit_v2／DirStackM-threelens）。
- 生產熱路徑數字：RankRidge H60 #14 net Sharpe **1.30**（bench 1.09）；RankGBDT econ≈基準不升格；DailyGBDT_cal pooled hit **0.5157**。
- Wave B–G＝誠實 SKIP／partial（詳見本檔前輪各 Wave EXECUTED 帳，本報告不重複列）。
- 回饋帳 `S4-REOPT-BACKLOG`：H60＞H20≫H40；H120 defer（n=8）；RankGBDT STOP promote。

### 3.3 S5 預測軸

- OOS 已跑（`S5-OOS-20260804.md`）：B2_ridge H20 net hit 0.639／H60 0.632／Sharpe 1.30；**H40 劣 bench**（方向警示）；H120 n=8 勿終局。
- **dgate evaluated_pass=0**（approved 11／evaluated_fail 12／superseded 6）——**禁假確立級**。
- `prediction_values` **未寫**；sim 首格未落地。
- 待授：`predict-asof-write-go`／`SIM-FIRST-CELL-go`／`evaluate_direction_gate`。

### 3.4 S1 資料軸

- raw 已補至 **2026-08-03**（56/83 catalog OK）；FRED 31 series 6 達當日；attestation PASS（matched 388,490／VM 0）。
- 核心宇宙 225 股（`build_core_universe.py --liquidity-pct 25 --exempt-revenue-financial`）。
- **as-of 缺口**：raw 到 08-03，但 **feature panel 仍釘 2026-06-30**——predict-orthogonal 下此非硬閘，但為「普查廣度 vs 生產深度落差」之直接證據。
- 仍否：Dividend rebuild／寬窗／`--with-dim-sync`（dim-only 3 表）。

### 3.5 C1／C2／C0 閉環 DONE vs 待 GO

**已消費＋EXECUTED**：主計畫、S3 Wave A/B、S4 Wave A–G、C2 正向＋回饋、C0 地圖採納、C1 Arc A（L1–L3）、S1 核心閘。

**待 GO（尚未消費）**：C1 Arc B（`LOOP-S2-TO-S1-EXPAND-go`）／Arc C（`LOOP-CYCLE-1-go`）；S2-KH L4；S3 Wave C/D/E；S5 寫庫／sim（`predict-asof-write-go`／`SIM-FIRST-CELL-go`）；S1 另授取數（dim-sync／ExchangeRate／Dividend／News）。

---

## §4 軸：src/augur 結構

> 來源：explore 子代理（[src/augur結構探勘](988b40bd-3adf-4365-84cb-b453f94f1ad2)）。範圍：16 package、104 個 library 模組（不含 `__init__.py`；含 17 個 `__init__.py` 共 121 檔）。

### 4.1 逐 package 角色（依熱度排序）

| package | 模組數 | 角色 | 熱路徑代表 |
|---|---:|---|---|
| `core` | 6 | 地基橫切層 | `db.py`（**全 repo 最熱**，380+ 次引用）／`config.py`／`prodset_contract.py`（禁 philosophy import） |
| `knowledge` | 24（最大） | 三層知識管線＋KH 系列＋RBAC | `admission.py`（入庫治權界閘）→`ingress_kip.py`→`corpus.py`→`embedspec.py`→`vectorindex.py`；KH4/KH7/KH8/KH9/KH10 |
| `advisor` | 12 | L3 顧問前端（服務側熱路徑） | `payload.py`（唯讀通道）／`guard.py`（防幻覺機械閘）／`safe_general.py` |
| `deliberation` | 11 | 本地審議引擎（零 Claude token） | `verifiers.py`（唯一合法 confirmed 來源）／`anchors.py`／`consensus.py` |
| `audit` | 11 | 稽核／防呆層 | `reconcile.py`（#7）／`import_isolation.py`（#8 命門）／`scan_floor.py`（#35 落地區） |
| `features` | 10 | 特徵層（anti-leakage 重鎮） | `panel.py`（唯一入口）／`release_lag.py`（#8 命門）／`macro_vintage.py` |
| `evaluation` | 7 | 評估層（#8 第二重鎮） | `label.py`／`baseline.py`／`metrics.py`（`effective_t_hac`）／`portfolio.py`（#14） |
| `philosophy` | 5 | 哲學框架橫切層（單向素養層） | `evolution.py`（PME 閉環，19 次引用）／`interpretation.py`（零回流預測） |
| `identity` | 5 | 世界實體身份 | `resolve.py`（resolve-or-mint）／`attribute_version.py`（SCD-2） |
| `ingestion` | 4 | 取數通道（API 門側） | `finmind.py`（`_quota_gate`／`QUOTA_COOLDOWN=1800s`）／`fred.py` |
| `models` | 3 | 預測模型層 | `artifact.py`／`ranker.py`／`registry.py` |
| `execution` | 2 | 部署執行層 | `risk_control.py`（✅ predict_asof 熱）／`action_log.py`（**零消費端**） |
| `arena`／`evolution`／`catalog`／`universe` | 各 1 | 單模組 package | `adapters.py`／`behavior_rubric.py`／`world_concept.py`／`core_gate.py` |

### 4.2 生產熱路徑 trace（四支關鍵 script 實測）

| Script | 直接消費之 library 模組 |
|---|---|
| `train_ranker.py` | `core.db`、`evaluation.baseline/label`、`models.artifact/registry/ranker` |
| `build_feature_panel.py` | `core.db`、`features.panel`（間接：chip/concentration/fundamentals/margin_cycle/phase/release_lag/valuation） |
| `daily_maintenance.py` | `core.db/schema`、`ingestion.sync`、`audit.reconcile` |
| `predict_asof.py` | `core.db`、`evaluation.baseline/label/portfolio`、`execution.risk_control`、`models.artifact/registry` |

scripts 全量最熱排序：`core.db`（380+）≫ `evaluation.label`（21+）> `philosophy.evolution`（19）> `evaluation.baseline` > `philosophy.retrieval`、`advisor.payload/ollama`、`core.heavy_slot`、`audit.evolution_contract`。**取數（ingestion）與預測（evaluation/models/execution）入口確實分離**，符合 predict-orthogonal 規則。

### 4.3 執行指令矩陣覆蓋（CLAUDE #18）

- `if __name__=="__main__"`：**104/104 非 init 模組 = 100%**。
- 字面 `--selftest`：102/104；餘 2 支（`audit/import_isolation.py`、`knowledge/admission.py`）具等價零外部依賴自測路徑——**實質 104/104 合規**。

### 4.4 架構強項（子代理判讀）

- 不變式寫成程式而非註解：#8 anti-leakage 三重機械強制（`release_lag`／`macro_vintage`／`walkforward`＋`import_isolation`＋`prodset_contract`）；#24 quota gate 內建 `finmind.py`；#32 對照臂寫進 `evidence_protocol.py`。
- SSOT 紀律強：deflation／embedspec／textnorm／corpus 述詞／DDL 常數各有單一住所並在 docstring 明示 #12。
- 命名合規度高：104 模組全為領域名詞，無 util/helper/manager/handler/service。

### 4.5 缺口／債（併入 §7 綜合債表）

1. **`execution/action_log.py` 零消費端**——六元組留痕 helper 已建、DDL 已遷，但無任何程式呼叫寫入；AUD-10/11 接線未完。
2. **兩處輕微循環依賴**：`advisor↔deliberation`、`core↔audit`（地基層回頭依賴稽核層）。
3. `models/registry.py` 命名觸 #18 禁用詞邊界（語境為 model registry 領域概念，屬可接受邊界案例）。
4. `evaluation/portfolio.py` 有 `SyntaxWarning`（docstring `\w` 未 raw-string，小 lint 債）。
5. `knowledge/evidence.py`／`synthesis.py`／`interaction_probe.py`／`kh7_eligibility.py` 自標「min-LAND／最小 slice」——設計上漸進落地，非爛尾，屬已知 partial 另帳（與 §2.2 呼應）。

---

## §5 軸：scripts／ops／tools 全量分類

> 來源：explore 子代理（[scripts全量分類](8b86aee5-48de-4ae1-8703-b0d833b2c107)）。範圍：`scripts/`（**354 支 .py＋7 支 .sh**）、根目錄 9 支 shell、`tools/`（4 個 MCP／lint 套件）、`ops/`。

### 5.1 十二功能桶

| # | 桶 | 約數 | 代表 |
|---|---|---:|---|
| 1 | ingestion/sync | ~14 | `full_market_sync.py`／`daily_maintenance.py`／`sync_macro.py` |
| 2 | build/panel | ~14 | `build_feature_panel.py`／`build_catalog.py`／`build_core_universe.py` |
| 3 | train | 5 | `train_ranker.py`／`train_daily_direction.py`／`train_direction_threelens.py` |
| 4 | predict/serving | ~7 | `predict_asof.py`／`produce_direction_probability.py`／`serve_probability_ui.py` |
| 5 | evaluate/verify/gates | ~65（最密） | `verify_*` 37 支／`run_economic_eval.py`／`evaluate_direction_gate.py` |
| 6 | sim/evolution/arena | ~45 | `run_evolution_iteration.py`／`run_arena_daily_pipeline.py`／`decide_sim_verdict.py` |
| 7 | knowledge/KH | ~75（最大） | `acquire_knowledge.py`→`promote_knowledge.py`；`run_kh_chain.py`（KH0→KH9） |
| 8 | knowledge/admission | ~8 | `review_knowledge_source.py`（人閘）／`probe_knowledge_source.py` |
| 9 | admin/registry | ~12 | `serve_admin_console.py`／`manage_rbac_user.py` |
| 10 | ops/monitoring/稽核 | ~35 | `deliberate.py`／`check_cmd_matrix.py`／`check_false_assertions.py` |
| 11 | archive/migration | ~93（次大） | `migrate_*_ddl.py` **83 支**／`archive_push.sh` |
| 12 | one-off/diagnostic | ~25 | `observe_twevo_run22.py`／`repair_priceadj_basis.py` |

**基建**：`_bootstrap.py`（每支 script 免 `PYTHONPATH` 直跑）；`check_cmd_matrix.py`（RULING-2026-026 機械稽核，MIN_CHECKED=300，08-03 現況約 470 支受檢）。

### 5.2 生產熱路徑（cron／systemd）

**Cron（15 條，SSOT＝`install_cron.sh`）**：01:30 演化七段鏈；04:15/10:15/16:15/22:15 `evolve_cycle`；每 6h `evolve_self_seek`；07:10 證據重驗＋全文日班；週六 07:30 備份；週一 08:00 VACUUM；週一 08:40 工具週測；週六 09:00 RAWEVO；**平日 20:00 arena 出單全鏈**（daily_maintenance→sync_macro→IV→方向特徵→round）；平日 21:30 arena 結算；**平日 23:00 TWEVO 夜輪**（`--slot-wait 10800`，實測 7–10hr）；每 2h Steward 提問帳本／DESKTOP 增量拉取；週日 09:00 三軸週儀表。

**systemd**：6 常駐服務（qdrant/ollama/advisor/chat/admin/probability）＋7 timers（embed-catchup、ata-advance、admission-assist、audit-watchdog、drain-deferred 已開；**l2-deliberation、knowhow-refresh 預設 disabled 待開閘**）。

### 5.3 冗餘／債務發現（9 項，子代理原話精煉）

1. **自標過時未刪**：`drain_knowhow_admit_to_ceiling.sh`（檔頭明寫「已過時，改用 `run_kh_chain.py`」）、`arena_settle_oneshot.sh`（cron 已取代，自測甚至斷言「oneshot 已退場」）仍在庫。
2. **Milvus vs Qdrant 雙軌殘留**：`export_milvus_index.py` 疑似死碼（現行 serving＝Qdrant）。
3. **`sync_memory.sh` 外來殘片**：寫死他人他機路徑（`/home/giga/.gemini/...`）且會自動 `git commit`＋`push origin main`——**與 CLAUDE #14「commit/push 須明示授權」相牴**。
4. **全文抓取族八代同堂**：早期 hardcode 種子批（`fetch_gutenberg_classics` 等 4 支）與現行通用化 `fetch_*fulltext` 系列並存，依 #29(c) 可收斂。
5. **`curate_pme_xdom_*` 三胞胎**：同型逐 domain 腳本，依 #29(b) 可參數化收斂。
6. **`migrate_*_ddl.py` 83 支**＝最大量體，非死碼（換機還原依賴），但「刻意維護的體積債」。
7. **run 綁定腳本**：`observe_twevo_run22.py`／`watch_run22_step1_ready.sh`——run 結束即失效。
8. **`train_direction_threelens.py`** 自述「非 gate、不入庫、一次跑不迭代」＝一次性冒煙卻住 train 家族名下。
9. **暫存檔散住根目錄**：`tmp_runners/`（驗紅證據）、`scratchpad/`——未歸 `audits/`。

### 5.4 一次性 vs 持續維護

持續維護 ≈120 支（cron/timer/服務入口＋機械稽核族＋換機五件套＋`migrate_*` 全族＋預測 SOP 鏈＋KH 鏈）；一次性/歷史 ≈40–50 支（`backfill_*`／`seed_*`／`repair_*`／`observe_twevo_run22` 等）。專案文化「留檔不刪」（audits 留痕慣例）使 `scripts/` 體積只增不減——**與 #29(c) 收斂目標之間為已知張力**（併入 §7）。

---

## §6 軸：治理層（constitution/specs/docs/CLAUDE.md/HANDOFF）

> 來源：explore 子代理（[治理層探勘](d4fa73b8-81a5-4033-86a5-44cf17f5cdfe)）。

### 6.1 層級地圖 L0→L7＋領域三件套

統一入口＝`constitution/GOVERNANCE-MAP.md`；L0 lex superior（`AUGUR-MC v1.6 §0.6(a)`）。

| 層 | 現行版本 | 生效依據 |
|---|---|---|
| L0 Meta-Constitution | AUGUR-MC **v1.6** | AL-2026-044／RULING-2026-040 |
| L1 World Model | AUGUR-WM v1.0 | RULING-2026-002 充任 |
| L2 Ontology | AUGUR-ONT v1.0 | RULING-2026-003 |
| L3 Identity | AUGUR-ID v1.0 | RULING-2026-004 |
| L4 Knowledge System | AUGUR-KS v1.1 | RULING-2026-016 |
| L5 Cognitive Kernel | AUGUR-L5 v1.0（provisional 已解除） | RULING-2026-029；**復審 2026-10-14** |
| L6 Agent Runtime | AUGUR-L6 **v1.2**（唯一經 §8.2 實質審查充任者） | RULING-2026-007/013/016 |
| L7 Infrastructure | AUGUR-L7 v1.0（residual (iii)(iv)(vi) **復審 2026-10-14**） | RULING-2026-011＋025 |

**領域治權檔**：靈魂 v1.10.0（L1）／原則精華 v1.12.0（L4，20 條、#1/#8/#15 三基石）／領域大憲章 v1.54.0（L7）／CLAUDE.md **v1.35**（L6，35 條）。⚠ 版號小時級變動——已拍板**刪除硬編版號**、引用前一律 `ls docs/` 現查。

### 6.2 治權機制四件套

- **RULING**：現至 **043**（待簽，見 6.4）；決策人＝Constitution Steward（Sole Steward）；AI 不得參與修憲與解釋。
- **Amendment Log**：`AL-2026-047`（現行最新）；分級 major/minor/patch。
- **合規聲明（CS）**：五份領域治權檔各存 `docs/compliance/CS-*.md`；補正期 **2026-10-14**。
- **探針機制**：`<!--probe:ID-->`（活數字，`read_treaty_probes.py --check` 重跑核對）＋`<!--lint:KEY-->`（`constitution_lint report --sync`）；已知逃逸口——`HANDOFF-governance.md` 65 處標記凍結於 07-17（脫離 `bound_docs`）。

### 6.3 CLAUDE.md v1.35（35 條，五章）日常最承重

**#9**（數字唯 (a)(b)(c) 三來源）、**#20**（plan-first）、**#26**（決策層人拍板／執行層 AI 主動）、**#28**（本地零 usage＞背景不輪詢＞模型檔位）、**#32**（self-reported＋三對照臂）、**#35**（回歸鎖三規則＋`check_false_assertions.py --gate`）。⚠ 條號前綴紀律：裸 `#N` 指 CLAUDE 條號，引用原則精華須寫「原則精華 #N」。

### 6.4 開放治權債（子代理親查，5 項）

| 債 | 內容 |
|---|---|
| **043 待簽** | RULING-2026-043（B4 UPDATE-GUC 擴閘，15 表）AL-2026-047 定案欄明載「待 Steward 簽核」；HANDOFF「043＝B」為圈選裁示、非親簽 |
| **CS 漂移** | `CS-系統架構大憲章` 標題仍作 v1.53.0（SSOT 已 v1.54.0）；`HANDOFF-governance.md` lint 凍結於 07-17 |
| **2026-10-14 日曆項（多筆）** | L7 residual 復審／L5 §8.2 條件復審／WM.35/36 消費禁令生效／CS 補正期／L7.16 全棧矩陣併審／`validation_evidence` 90 天效期到期——備料已在 `reports/augur_1014_review_evidence_prep_20260801.md` |
| **V2-SUNSET 2026-10-31** | `evolution_prereg_gate` deadline；續命三條全未達成；arena live 門 250 clusters vs 已結算 2＝**物理不可達**；治權檔「≥60」vs 凍結值 250 判準級矛盾**已呈裁未裁** |
| **其他殘餘** | superuser 可繞閘（DISABLE TRIGGER／session_replication_role）；OCV 六分量零機械實作；致命 Conflict 分級判準未登錄 |

### 6.5 Audit 帳本紀律

現 **334 檔**，命名＝`主題碼-階段-YYYYMMDD.md`；階段詞彙固定：`*-GO-*`（拍板留痕）→`*-EXECUTED/CLOSED-*`（施作）→`*-BLOCKED-*`（受阻）；`*-HONESTY-PASSPORT-*`（治權表寫入 GUC 通行證）；`*-RED-*`（#35 先驗紅證）；`ARCHIVE-PUSH/CHECKPOINT-*`（封存）。運作鏈：計畫→GO audit→施作→EXECUTED audit→HANDOFF 指針→ARCHIVE-PUSH。

---

## §7 綜合債表（定版；36 項，按軸歸類、供優化計畫書排序用）

標記：**[治]**治理／**[資]**資料S1／**[知]**知識S2/KH／**[徵]**特徵S3／**[模]**模型S4／**[測]**預測S5／**[構]**程式結構／**[腳]**scripts體積。

### 7.1 高影響（卡住下一階段判斷或有明確矛盾）

| # | 債 | 標記 | 影響 | 來源 |
|---|---|---|---|---|
| 1 | `direction_gate` evaluated_pass=0；治權檔「≥60」vs 凍結值「250」判準級矛盾**已呈裁未裁** | [測][治] | 禁假確立級；arena live 門物理不可達 | §2.5／§3.3／§6.4 |
| 2 | V2-SUNSET deadline 2026-10-31 續命三條全未達成 | [治][模] | 三軸自進化存續之治理風險 | §2.3／§6.4 |
| 3 | SUNSET consequence 無機械載體（kill_switch 四 scope 全 clear、無封存腳本） | [治][構] | 若真觸發 SUNSET，缺程式強制執行 | §2.3 |
| 4 | RULING-2026-043 待 Steward 簽核；HANDOFF「043＝B」為圈選裁示非親簽 | [治] | B4 UPDATE-GUC 擴閘（15 表）效力未定 | §6.4 |
| 5 | raw 已到 2026-08-03，但 feature panel／prodset as-of 仍釘 2026-06-30 | [資][徵] | 普查廣度與生產深度落差之直接證據 | §3.4 |
| 6 | ~~序列窗／圖邊契約缺口~~——**2026-08-04 已解（全數，含 Phase 2c）**：`S3-WAVE-D` GO＋EXECUTED（`features/sequence.py`；`stock_graph_edge` 13,021 邊已寫入＠2026-06-30）；殘餘＝adapter 訓練碼仍缺（另債，非本項） | [徵][模] | 原＝S4 Wave C/D/E 全 SKIP 之根因；契約解除後 SKIP 理由改「缺 adapter」 | `audits/S3-WAVE-D-EXECUTED-20260804.md` |

### 7.2 中影響（品質／可信度缺口，非阻斷）

| # | 債 | 標記 | 影響 | 來源 |
|---|---|---|---|---|
| 7 | 市場軸 KH 語料 spurious-high（探針 hit≠概念橋成立≠G-PROM） | [知] | S2-KH L4 前需先解語料品質 | §2.2 |
| 8 | M-G10 維度斷檔：TRI 等 6 表 `data_id_required` sync 推不動（接線在、預設關） | [資][測] | arena 少一維、需另授 `--with-dim-sync` | §2.5 |
| 9 | Wave B `verify_candidate_promotion --seeds 3` 多 seed 正式表 in-flight 未回填 | [徵] | 4 候選截面特徵晉升判斷未完 | §3.1 |
| 10 | H40 方向警示（劣於 bench）；H120 樣本量 n=8 勿終局 | [模][測] | horizon 選擇之經濟意義風險 | §3.2／§3.3 |
| 11 | RankGBDT econ≈基準不升格；H20 GBDT 3-seed OOS 對稱補未做 | [模] | 已試模型中唯一非 Ridge 挑戰者卡關 | §3.2 |
| 12 | 8 族 missing adapter（XGB/Cat/RF/LTR/SVM/KNN/NB/MLP）until adapter | [模] | S4-REOPT-BACKLOG 待實作項 | §3.2 |
| 13 | `prediction_values` 未寫、sim 首格未落地（`sim_run_link=0`） | [測] | S5 生產輸出尚未真正落庫 | §3.3 |
| 14 | CS 版號漂移：`CS-系統架構大憲章` 標題仍 v1.53.0（SSOT 已 v1.54.0） | [治] | 合規聲明與治權檔不同步 | §6.4 |
| 15 | `HANDOFF-governance.md` lint 標記脫離 `bound_docs`，凍結於 07-17 | [治] | 探針機制已知逃逸口 | §6.2 |
| 16 | 2026-10-14 六筆日曆項並列（L7/L5 復審、CS 補正、90 天效期等） | [治] | 單日多筆到期須集中備審 | §6.4 |

### 7.3 結構／程式層（本輪首次全量盤點新增發現）

| # | 債 | 標記 | 影響 | 來源 |
|---|---|---|---|---|
| 17 | `execution/action_log.py` 零消費端——六元組留痕 helper 已建、DDL 已遷，無程式呼叫寫入 | [構] | AUD-10/11 接線未完，留痕義務空轉 | §4.5 |
| 18 | 兩處輕微循環依賴：`advisor↔deliberation`、`core↔audit`（地基層回頭依賴稽核層） | [構] | 分層倒置，長期維護風險 | §4.5 |
| 19 | `models/registry.py` 命名觸 #18 禁用詞邊界（語境可接受但邊界案例） | [構] | 命名慣例稽核之灰區 | §4.5 |
| 20 | `evaluation/portfolio.py` docstring `\w` 未 raw-string 之 SyntaxWarning | [構] | 小 lint 債 | §4.5 |
| 21 | `sync_memory.sh` 外來殘片：寫死他人他機路徑＋自動 `git commit`/`push origin main` | [腳][治] | **直接牴觸 CLAUDE #14**（commit/push 須明示授權） | §5.3 |
| 22 | 自標過時未刪：`drain_knowhow_admit_to_ceiling.sh`／`arena_settle_oneshot.sh` | [腳] | 已被取代仍在庫，誤用風險 | §5.3 |
| 23 | Milvus vs Qdrant 雙軌殘留（`export_milvus_index.py` 疑似死碼） | [腳] | serving 索引已全面轉 Qdrant | §5.3 |
| 24 | 全文抓取族八代同堂（早期 hardcode 種子批 vs 現行通用化 `fetch_*fulltext`） | [腳] | #29(c) 收斂空間 | §5.3 |
| 25 | `curate_pme_xdom_*` 三胞胎同型腳本 | [腳] | #29(b) 參數化收斂空間 | §5.3 |
| 26 | `migrate_*_ddl.py` 83 支＝`scripts/` 近四分之一體積（非死碼，換機依賴） | [腳] | 刻意維護的體積債 | §5.3 |
| 27 | run 綁定腳本（`observe_twevo_run22.py` 等）run 結束即失效仍留庫 | [腳] | 一次性腳本未歸檔 | §5.3 |
| 28 | `train_direction_threelens.py` 一次性冒煙卻住 train 家族名下 | [腳][模] | 家族命名與實際用途不一致 | §5.3 |
| 29 | 暫存驗證檔散住根目錄（`tmp_runners/`、`scratchpad/`）未歸 `audits/` | [腳] | 留痕慣例不一致 | §5.3 |
| 30 | 2 個 systemd timer（`l2-deliberation`、`knowhow-refresh`）預設 disabled 待開閘 | [構][腳] | 已建但未啟用之產能 | §5.2 |
| 31 | scripts/ 體積只增不減，與 CLAUDE #29(c)「同型合併」目標之間存在張力 | [腳] | 專案文化（留檔不刪）vs 收斂原則 | §5.4 |

### 7.4 既有已知債（前輪延續，不重複展開）

| # | 債 | 標記 | 來源 |
|---|---|---|---|
| 32 | pe 離群 winsorize、lending_fee 名實窗（S3 已知債） | [徵] | §3.1 |
| 33 | 股級 macro feature_values 誠實 SKIP（無 builder） | [徵] | §2.3／§3.1 |
| 34 | ExchangeRate 長回填、Dividend rebuild、News coverage 補洞（均另授取數） | [資] | §3.4 |
| 35 | dim-only 3 表待 `--with-dim-sync` 另授 | [資] | §3.4 |
| 36 | OCV 六分量零機械實作（人簽為軟強度） | [治] | §6.4 |

---

*定版（2026-08-04）——五路 explore＋DB 親查全部併入；優化計畫書見 `reports/augur_project_optimization_plan_r6_20260804.md`。*
