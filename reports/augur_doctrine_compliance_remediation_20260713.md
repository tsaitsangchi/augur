# augur 符憲檢視與修復報告（2026-07-13）

**基準**：靈魂 v1.8.0／原則精華 v1.9.0／憲章 v1.45.0／CLAUDE v1.27／README＋建構理解 v4（`augur_construction_understanding_20260713.md`）。
**方法**：v4 已確認之斷線/債（§9/§11＋90 節級債）分級處置＋本地零-usage 靜態掃描（#29a/#29d/#18/#5）＋#29b 補獵＋逐項對抗複驗。
**分級判準**（CLAUDE #26）：「改正確/補完整」＝執行層→已修＋實測；「變更判準/架構/新機械閘」＝決策層→本報告 §2 待 hugo 拍板。
**紅線**：開賽鏈三支（verify_validation_evidence / preregister_unfreeze_gate / run_arena_round）在 evaluate 完成前凍結未動。

---

## §1 執行層已修（全部附實測證據）

| # | 修復 | 違反 | 實測證據 |
|---|---|---|---|
| 1 | **guard 符號翻轉漏洞**：`guard.py:121` suspects 加 `-?`＋`_NUM_TOKEN`（:82）白名單保留負號（成對修，不誤傷誠實負值）| #1 零幻像（citation 0.9987→輸出 -0.9987 曾可放行）；棘輪方向=更嚴 ✓ | `pytest test_advisor_guard.py` 22 passed＋3 紅測（翻轉必攔/誠實正負值皆放行）；advisor 服務 inactive 無需重啟 |
| 2 | **redline 治權檔 pattern 失聯**：`deliberation_redline_trigger` 三列 UPDATE 為版本無關前綴（`docs/系統核心思想_v` 等）| 憲章 #19/#26「治權宣稱強制人裁」被 stale pattern 架空 | `redlines.consult` 實測：現行三檔＋未來版號全命中、非治權 anchor 不誤觸 |
| 3 | **README 狀態句版本漂移**：v1.5.0/v1.43.0/v1.25 → v1.8.0/v1.45.0/v1.27 | #12（README 自身連結表與狀態句互相矛盾）| 檔面比對 |
| 4 | **HANDOFF CLAUDE 版本引用**：兩處寫死 v1.25 → 「版本見檔頭」（治本：引用不再隨升版過期）| #12 | 檔面比對 |
| 5 | **sync_memory 路徑推導**：`replace('/','-')` → `re.sub(r'[^A-Za-z0-9]','-')`——依本機 `~/.claude/projects/` 實證（`stock_backend/.claude-worktrees/...`→`stock-backend--claude-worktrees-...`，`_`與`.`皆轉）| #31（含 `.`/`_` 路徑 clone 會分岔指錯 memory 目錄）| 兩案例單測 ✓＋`python3 sync_memory.py` status 實跑 ✓（現路徑行為不變）；首次實跑抓到漏 `import re` 已補 |
| 6 | **import_database.sh migrate footgun**：gated 批無參數「靜默 no-op 卻印 ✓」→ 三段嘗試（--migrate→--run→無參數）＋顯式納入 `migrate_source_governance.py`（原不入 glob）＋標頭「13 支」死數字改 glob 全量句 | #29（假 ✓ 掩蓋未跑）/#8 誠實 | `bash -n` ✓；**runtime 未實跑**（audit 尾段對帳中、DDL 取鎖有 #30 鎖風暴風險）——冪等設計、下次匯入即實證，誠實標註 |
| 7 | **#18 標頭 18 件**（12 缺 🎯／6 缺「守原則 #」）| CLAUDE #18 | 修復 agent＋對抗複驗進行中（原則號須真實對應、亂貼=退回），結果見附錄 |
| 8 | （今日稍早）CLAUDE.md 條號修復＋v1.26 #21 背景任務可見＋v1.27 #28 模型分派表；v4 報告終審 16 findings 修補 | — | 已各自驗證 |

**靜態掃描全綠項**（本地零-usage，`compliance_scan.txt`）：#29(a) 個別可執行 **0 違規**（173/173 scripts bootstrap 正確）；#29(d) 指令矩陣 **0 違規**；#5 追蹤檔密鑰 **0 件**。

## §2 決策層待 hugo 拍板（依 v1.39.0 附 schema＋程式規畫）

### 2.1 predict role 接線（#8 動態閘由 provisioned→實際載入）
- **現況**：role＋GRANT 已 live（153 預測表 SELECT、素養表 0），但 `core/config.py` 無 `DB_PARAMS_PREDICT`、`db.connect()` 單一 superuser 參數——**無任何生產 code 用此 role 連線**。
- **程式規畫**：(a) `config.py` 加 `DB_PARAMS_PREDICT`（讀 `.env` 之 `DB_PREDICT_PASSWORD`，已存在）；(b) `db.connect(role='predict')` 參數化；(c) 預測入口（train/predict/panel builder）逐支切換——**逐支切、每支實測**（#19）。
- **Schema**：無新表；沿用既有 GRANT。
- **風險**：切換後任何漏 GRANT 表會即刻報錯（fail-closed、預期行為）；建議開賽鏈完成後做。

### 2.2 prediction_values 禁回讀之機械化（v3/v4 兩度確認僅 COMMENT）
- **提案**：不動 DB——擴 `import_isolation` 字面掃描（比照 BRIDGE_LITERALS 手法）：PIPELINE 7 package 禁字面 `prediction_values`（白名單=其唯一合法 writer 模組）。零 DDL、AST 層強制、test 常備。
- **程式規畫**：`import_isolation.py` 加 `PREDICTION_READBACK_LITERALS`＋掃描段；`tests/test_philosophy_isolation.py` 加斷言。

### 2.3 macro PIT reader（latent 埋雷，接 macro 特徵前的硬前置）
- **現況**：`fred_series` PK 含 realtime_start（vintage 結構就緒）、無 PIT reader、Tier B 濾版僅 docstring。**現零 macro 消費者、不爆**。
- **提案**：任何 macro 特徵立項時，reader 先行（`ingestion/macro_vintage.py`：`read_asof(series_id, panel_date)` 內建 `realtime_start<=panel_date` 濾版）＋測試。**現在不建**（無消費者、避免為假想未來加抽象 #3）——入債追蹤即可。
- **Schema**：無新表（讀 `fred_series`）。

### 2.4 A3 三鏡頭三門簽核狀態確認（人裁）
- DB 事實：`dgate_a3_threelens_{20,40,82}` status=**preregistered、approved_by 空**（07-12 17:39 重新預註冊）、無任何 `_r2` gate_id——與「_r2 三門已簽」記憶/commit 訊息不符。**待 hugo 確認**：是否補簽（TTY approve）或維持 preregistered。
- 開賽鏈九選手/六 arena 門不受影響（六門 approved 07-12 09:28 在案）。

### 2.5 `_METRIC_NUM` 負號延伸（§1-1 的同類殘餘）
- `_METRIC_NUM`（guard.py:27）對「IC -0.2」型 metric 鄰接負值仍掉號（影響 guard 與 guard_knowledge 兩者）。方向同棘輪更嚴；因觸 `guard()` 主閘行為，依「guard 單向棘輪需審慎」慣例列裁而非逕修。**建議核准後與 §1-1 同法成對修**。

### 2.6 憲章 v1.45.0 已知殘餘（v4 §9/§11 記錄在案、非本輪新增）
- owned_local 跨欄 CHECK 反向 SSOT 漂移（live 有、遷移無→clean-room 不重現，違 #12）——修法＝補進對應 migrate DDL（一段 ADD CONSTRAINT IF NOT EXISTS）；屬 DDL 變更，建議 audit 綠後做。
- 方向/幅度兩軸 enforcement 不對稱（by design，v1.45.0 明文僅約束方向）——**無行動**、記錄知情。

## §3 驗收矩陣

| 驗收 | 結果 |
|---|---|
| 隔離命門 AST 八道 | 待 §1-7 完成後重跑 `check_isolation()`＋`pytest test_philosophy_isolation.py`（修復僅動 docstring，預期 0 violations 不變）|
| guard 測試 | 22 passed＋3 紅測 ✓ |
| redlines 實測 | 6 案例全對 ✓ |
| scripts 紀律 | 173/173 #29(a)(d) ✓ |
| 密鑰 | 追蹤檔 0 件 ✓ |
| #29b hardcode 補獵 | agent 進行中，結果見附錄 |
| 開賽鏈凍結 | 三支未動 ✓（git diff 可證）|

**未 commit**（#14 待授權）；與稍早已 push 之 `a59423b` 分開成批。

---

## 附錄 A：#18 標頭修復結果（17 修＋1 正確跳過）

- **13 檔補 🎯**（advisor/prompt、audit/reconcile、core/config·db·generic_schema·schema、features/macro·panel、ingestion/finmind·fred·ingest·sync、universe/core_gate）——僅 emoji 前綴、原文零改寫。
- **4 檔補「守原則 #」行**（evaluation/label #8#1#12、metrics #12#15#11、walkforward #8#12、features/release_lag #8#9）——原則號經逐條對照原則精華、對應模組真實職責。
- **1 檔正確跳過**：`knowledge/curation.py` 實質已合規（既有「守 憲章 v1.41.0 · #12 · #15」行）——是**掃描器正則誤報**（`守\s*#` 不容「守 憲章…#N」詞序）；正解＝放寬檢查正則、不改寫原文（agent 判斷正確）。
- **複驗仲裁**：複驗者 `ok=false` 之三條主訴均屬**誤判**——其把主 session 先前已修＋已測的 `guard.py` 符號翻轉修復（本報告 §1-1、22 測+3 紅測）誤認為標頭批次夾帶；修復 agent 實際上已在 skipped 中誠實揭露該檔為「開工前既有工作樹改動、我未觸碰」。最終仲裁以 git diff 逐檔驗證定案：**17 檔確為 docstring-only**。複驗者唯一有效 minor＝metrics.py 守原則行措辭取自 CLAUDE #11 而非原則精華 #11 本文（號碼對映正確、僅措辭出處）——接受不改。
- **最終機械驗收**：AST 隔離八道 0 violations ✓｜pytest（isolation+guard+evaluation+ranker）43 passed ✓｜全模組 import 煙測 ✓。

## 附錄 B：#29(b) hardcode 補獵——7 件 borderline、0 件 clear（全屬可辯、列 backlog 待裁）

| 檔:行 | 內容 | 判讀 | 建議 |
|---|---|---|---|
| `ingestion/ingest.py:22` | INTRADAY/OUT_OF_UNIT frozenset 分類 gate 抓取 | 物理事實分類可辯；但與「catalog 單一驅動」自述矛盾（雙路徑）| 改讀 dataset_catalog、退役 code set |
| `ingestion/ingest.py:61` | `_AGGREGATE_DAILY` 2 列 table→聚合欄映射 | 量小偏邏輯側 | 可遷 catalog 欄位（低優先）|
| `catalog/__init__.py:199+` | `_DEDICATED_URL`/`_CATEGORY_FALLBACK`/`_DIRTY_VALUE_NOTES` 等策展註記 | 下游 SSOT 已落 DB、code 為 build 來源 | 遷 curated 來源、probe 改讀 DB |
| `scripts/advisor_distill_generate_questions.py:36,70` | `_OOC_TOPICS`/`_IMPOSSIBLE_TOPICS` 策展主題清單 | 與情境1 走 DB 之口徑不一 | 建 `advisor_distill_seed_topic` 表 |
| `scripts/annotate_schema_comments.py:21` | 2 張 infra 表中文名 dict | 未入 catalog 之殘留 | 補進 catalog 或小型 curated 表 |
| `scripts/expand_knowledge_registry.py:107` | AWARDS 12 獎項清單 | bootstrap 種子、多半豁免 | 可維持；徹底一致則入 DB |
| `scripts/harvest_knowledge.py:41` | DOMAIN_MAP_OVERRIDES 種子 | **已符 #29b bootstrap-seed 豁免**（DB 為 SSOT）| 維持現狀 |

**判讀**：無一屬 `TOPIC_ALIAS` 型明確違規；全部有豁免論證或已 DB-SSOT。是否逐項遷移＝決策層（成本 vs 一致性），列 backlog 待 hugo 裁。
**裁定（2026-07-13 hugo）**：做 1＋2＋5；4 綁蒸餾重啟；3/6/7 維持結案。實作計畫＝附錄 C。

## 附錄 C：1＋2＋5 實作計畫（已拍板；v1.39.0 schema＋程式雙落實）

**設計三前提（實查定案）**：(a) `catalog build()` 讀 ingest 集合**寫** catalog（code→DB）——直接反轉＝循環依賴＋bootstrap 空表守門失效；(b) 純 catalog 選表會在 catalog 過期時漏新 dataset（違 #3 動態無白名單）；(c) audit 進行中不動既有表 DDL（#30）。

**架構**：清單動態問 API（`list_datasets()`，#3 不變）＋**排除集查 dataset_catalog**（runtime 單一 DB 路徑）＋code frozenset 降級為「catalog-build seed＋DB 不可用時 fail-safe 後備」（#29b sanctioned seed 模式，同 DOMAIN_MAP_OVERRIDES）＋ingest 硬守門（raise）保留為縱深（防禦性冗餘、只更嚴）。

| 件 | 程式 | Schema |
|---|---|---|
| 1 INTRADAY/OUT_OF_UNIT | `ingest.catalog_exclusions(cur)`（查 `excluded=true` 集合；空/例外→None）；`sync.daily_datasets(conn=None)` DB-first、fallback 舊 code-set 路徑（行為等價）| 無新欄（`excluded/excluded_reason/frequency` 既有）|
| 2 `_AGGREGATE_DAILY` | `ingest.aggregate_method(dataset, cur=None)`：catalog 欄優先、欄不存在/無值→code dict（過渡零風險，audit selfheal 重啟也安全）；`ingest_finmind`/`reconcile` 改走 helper | **新欄 `aggregate_daily_method varchar(8)`＝冪等 migrate script、audit 綠後才跑** |
| 5 infra 中文 | `annotate_schema_comments.py`：dict 降級 seed→upsert 進 catalog（`excluded=true, source='infra'` 防誤入 sync 路徑；build 實證不清手植列）→統一讀 catalog | 無新欄（`table_name_zh/column_name_zh/zh_source` 既有）|

**驗收（2026-07-13 實跑全綠）**：
- 新舊 `daily_datasets` live DB 逐項等價（88=88 完全一致）且 **DB 路徑實際生效**（catalog 排除集 11 個）✓
- `aggregate_method` 過渡語意：欄未建 → 輸出＝seed dict（GoldPrice=close/News=all/Price=None 全對）✓
- annotate 實跑：infra seed 入 catalog（`source='infra', excluded=true`）＋86 表/698 欄 COMMENT；`daily_datasets` 仍 88、infra 不入選表 ✓
- `column_catalog` 無唯一鍵 → seed 改 build 同款 DELETE+INSERT（實作中抓到、未上線就修）✓
- pytest test_ingest＋test_reconcile 20 passed ✓；6 檔 py_compile ✓；migrate script 無參數 graceful（#29d）✓
- **`migrate_catalog_aggregate_ddl.py --migrate`（建欄+seed 回填）待 audit 綠後執行**（#30 DDL 紀律）；欄建成後 `aggregate_method` 自動交棒 DB SSOT。
- 修改檔案：`ingest.py`（helpers＋store 切換）/`sync.py`（daily_datasets DB-first）/`reconcile.py`＋`reconcile_audit.py`（切 helper）/`annotate_schema_comments.py`（seed-upsert 統一讀）/新增 `migrate_catalog_aggregate_ddl.py`。audit 進程（記憶體舊碼）不受影響；selfheal 若重啟＝載新碼亦安全（fallback 行為等價）。
