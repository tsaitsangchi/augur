# WM.35／36 合規弧實作規畫呈案——World Concept Registry 落地＋vendor 直綁絞殺（2026-08-02）

**性質**：#20 計畫先行之呈案報告（規畫、零施作；本輪全程唯讀親驗）。
**呈案人**：AI（Fable 5；本報告全部內容為 AI 草擬與證據整備，依 `AUGUR-MC v1.6 §8.1` 不含任何條文解釋或裁決——解釋落點一律列 §9 待 Steward）。
**上游**：`reports/augur_1014_review_evidence_prep_20260801.md` §1（F2 備料）；`RULING-2026-030` 第五(b)；`RULING-2026-039` 二.2／九.2；`CODE-MIGRATION-PLAN.md` Phase 6。
**Steward 決定欄**：見 §10（留白待 hugo）。

---

## §0 義務一句話（條文原文錨）

> WM.36（`specs/WORLD-MODEL-SPECIFICATION.md:344-358`）：「系統**必須**維護『世界概念 → 來源 Observation 位置』映射之 **World Concept Registry**……為一級結構。登錄項最低含七欄……任何消費世界模型之模組對世界事實之引用，**必須**以世界概念為鍵、經 Registry 解析至權威表徵，**不得**以來源位置字面（供應商表名、欄名、series 識別碼）直接繫結。……**自 Steward 補正期裁定所載到期日之翌日起**，前句禁令對其無條件適用，無待另為決定。」
> RULING-2026-030:81：「補正期到期日＝**2026-10-14**；自 **2026-10-15** 起 WM.36 直綁消費禁令無條件適用。」RULING-2026-039 二.2：「**不提早結清**。」

可判定判準（WM.36 原文 :358）：「消費模組對世界事實之引用可解析至 Registry 之世界概念鍵者為合規；**補正期屆滿後仍以來源位置字面繫結者違規**。」
配套（WM.35 :336-340）：任何**新**通道落地即須登錄映射（unmapped 為顯式合法過渡態）；unmapped／未登錄通道之資料**僅具 Observation 地位**——「得保存、**對帳**、**追溯**，不得被消費為 Representation 或 Knowledge 之依據」。既存通道之登錄義務與既存消費同享同一補正期。

**距 10-14 併審日：73 日。本項為七項 checklist 中唯一「到期即法律效果自動切換」者（F2 §8 原話）。**

---

## §1 現況親驗（2026-08-02，全部指令可獨立重跑）

| 事實 | 指令（cwd=/home/hugo/project/augur） | 本日實跑值 |
|---|---|---|
| F2 口徑直綁檔數 | `grep -rlE 'FROM\s+"Taiwan' src scripts --include='*.py' \| wc -l` | **50**（F2 08-01＝47；07-17＝37） |
| 直綁出現處總數 | 同上去 `-l` 加 `wc -l` | **140 處** |
| 廣口徑（全 CamelCase 引號表） | `grep -rlE 'FROM\s+"[A-Z][A-Za-z]+"' …` | 50（與 Taiwan 集合相同；US 家族 1 檔已含於內） |
| fred_series 直綁（F2 口徑外） | `grep -rlE 'FROM\s+fred_series' …` | **+2 檔**（`scripts/reconcile_audit.py`、`src/augur/features/macro_vintage.py`；另 backfill_entity_registry 已在 50 內） |
| **合計直綁檔數（廣口徑）** | 上二集合聯集 | **52 檔** |
| 47→50 漂移根因 | `git log --diff-filter=A -- scripts/{evaluate_sim_calibration,run_sim_calibration_cell,settle_sim_outcomes}.py` | commit `92647f0`（**2026-08-02 本日**，sim 證據時鐘四件套）——**無 lint 閘、出血進行中**：07-17→08-02 淨增 +13 檔 |
| Registry 表本體 | `psql … pg_class WHERE relname ILIKE '%registry%' OR '%concept%' OR '%channel%'` | **零 world-concept 形制**；現存 `entity_registry`(3,503 列)／`model_registry`／`simulation_method_registry`，均非世界概念登錄 |
| 既有載體候選（A.17 [I] 註記） | live DB | `dataset_catalog` **97 列／27 欄**（含 anti_leakage_note、finalize_lag_days、source_provenance）、`column_catalog` **769 列／12 欄**（欄位級、含 anti_leakage_flag） |
| 同構先例 | live DB | `knowledge_source` 3,605 列（adapter＋查詢模板 registry，#29(b) 三層管線）——「來源定義住 DB、消費經解析」思想同構 |
| S22 code 層證據 | `venv/bin/python -c "from augur.audit.import_isolation import check_isolation; …"` | 本輪未重跑（F2 08-01 實跑 violations=0）；**量的是素養層隔離＋supersede/identity 字面**（`SUPERSEDE_LITERALS`/`IDENTITY_LITERALS` 等），**不含 vendor 表名**——與 WM.36 判準不同構，詳 §9 Q2 |
| 註解誤傷檢查 | grep 首欄過濾 `#/"""` | **零**——140 處全為可執行 SQL 字串，無「只是註解」之虛胖 |

**Annex F 啟動條目**（`specs/WORLD-MODEL-SPECIFICATION.md:937-`）：六條施工啟動集已隨卷——DailyBar／CorporateAction.除權息／匯率／TradingCalendar／Roster 成員資格／Delisting；「**採認與登錄由 Steward 附卷裁定**」（[I] 地位聲明原文）。
**既有規畫**：`CODE-MIGRATION-PLAN.md` Phase 6 已載三件套（DDL＋解析 API＋逐檔絞殺「雙讀影子比對、diff 零才切、非零熔斷回退」）與順序（低風險 audit/scripts 先、feature/panel 次、advisor/predict 最後）；本報告為其 #20 級細化，兩處修訂見 §5 註記。

---

## §2 52 檔分類（逐檔親驗歸類；完整清單見 §11 附錄）

| 類 | 定義 | 檔數 | 代表 |
|---|---|---|---|
| **A 生產消費鏈** | 產出進 Representation／Knowledge（特徵、訓練、預測、arena、sim、顧問） | **29** | `src/augur/features/`×7（含 macro_vintage）、`advisor/payload.py`、`arena/adapters.py`、build_*×6、train_*×3、produce_direction_probability、derive_market_iv、arena 管線×4、sim 管線×5 |
| **B 候選驗證／研究掃描** | 提拔關卡 verify_*×9、interaction scan×3、audit 相關性×2、TSFM benchmark×1——讀數成為**晉升裁決之依據** | **15** | `verify_candidate_promotion.py`、`run_deep_interaction_scan.py`（12 處）、`audit/field_correlation.py`（26 處＝最重檔） |
| **C 對帳／attestation** | WM.35 明文「得……對帳、追溯」之 Observation 層作業 | **3** | `full_universe_attest.py`、`verify_units.py`、`reconcile_audit.py` |
| **D 觀測層維運** | identity 鑄造／lifecycle／修復 writer／catalog 探測 | **5** | `backfill_entity_registry.py`、`backfill_lifecycle_retire.py`、`sync_attribute_versions.py`、`repair_priceadj_basis.py`、`catalog/__init__.py` |

出現處分布：最重 14 檔佔 92 處（field_correlation 26／run_deep_interaction_scan 12／build_market_direction 8／chip 7／build_daily_direction 7…）；36 檔僅 1–2 處。

---

## §3 兩讀法並陳（以條文為準；歸類傾向為 AI self-reported 證據整備，裁決權在 Steward）

**讀法甲（全量絞殺）**：「消費世界模型之模組」從寬——凡讀 vendor 表產生任何下游判斷者皆屬之 ⇒ **52 檔全改線**。優點：與 Phase 1 既載判準「grep → 0」全等、機器可稽核零白名單。代價：C／D 8 檔之改線與 WM.35 明文「得保存、對帳、追溯」的觀測層地位重疊（對帳工具本來就該直讀 raw 鏡像逐 byte 對——經 registry 間接層反而弱化對帳獨立性，A.17 [I]「catalog 只驅動怎麼抓、不保證資料對；對帳獨立裁決」同旨）。

**讀法乙（分層絞殺，條文字面）**：
- **A 類 29 檔＝禁令核心射程無疑義**（特徵→模型→預測→顧問即「消費為 Representation／Knowledge 之依據」的正身），10-14 前必改。
- **B 類 15 檔傾向在射程內**（verify_* 讀數→晉升裁決＝Knowledge 依據；WM.34(a) 引用鏈語境），但「研究讀數不進管線」（benchmark_tsfm 自我宣告）者是否除外＝條文歧義 → §9 Q1。
- **C／D 8 檔依 WM.35 明文屬觀測層准許作業**（對帳、追溯、保存），**不改線、以 lint 白名單顯式登錄豁免依據**——白名單每列須引 WM.35 該句＋Steward 核可。
⇒ 讀法乙工作量＝44 檔（或 Steward 就 B 另裁後 29–44 檔）。

**第三讀法檢驗（「Registry＋lint 閘即合規、消費點漸進」）——依條文不成立**：WM.36 可判定判準原文「補正期屆滿後**仍以來源位置字面繫結者違規**」——Registry 存在與否不改變消費檔字面繫結之違規性；lint 閘只擋新增、不洗白存量。此路**唯一**合法化途徑＝Steward 依 `AUGUR-MC v1.6 §8.4` 對 WM.36 之「履行時程」核發**有明確到期日**之書面豁免（附補正計畫、公開登錄）——而 §8.4 可用性本身有解釋疑點（§9 Q3），AI 不代裁。本讀法列為**後備案**，非建議。

**建議案＝讀法乙**（理由：條文字面已自帶 C／D 除外之明文依據，不需解釋擴張；工作量集中於真消費鏈；對帳工具保持直讀＝對帳獨立性不受間接層污染）。**證偽條件**：(i) Steward 解釋「消費模組」及於對帳工具 → 升級讀法甲、工作量 +8 檔；(ii) 任一檔雙讀影子比對 diff≠0 → 該檔熔斷回退、停手問（映射錯誤即資料真實性事件）；(iii) 10-14 前 A 類無法完成 → 即時呈報改走 §8.4 豁免聲請（不得靜默逾期）。

---

## §4 Registry 表 DDL 草案（#20 (a)；最小合規形制、逐欄溯源）

實作載體為 [I] 資訊、DEFER D18（WM.36 :357 原文「既有 catalog 擴充、view、中介表等」皆許）——本案採**二表正規化**：概念主表＋通道映射表（欄 3 一對多、欄位級，單表無法承載）。「登錄項七欄俱全且各欄可解析」由二表 join 呈現，符合可判定判準（七欄=登錄項之邏輯欄非物理單表）。

```sql
-- ① 概念主表（承 WM.36 欄 1/2/4/5/6/7＋WM.37 衝突落點）
CREATE TABLE world_concept_registry (
    concept_key        text PRIMARY KEY,      -- 欄1 世界概念（具名、繫結 Identity 語義；命名空間例 'tw.daily_bar'）
    category           text NOT NULL
        CHECK (category IN ('entity','event','state','relation','quantity')),  -- 欄2 歸類閉集（WM.36:348）
    authoritative_binding_id bigint,          -- 欄4 權威表徵指定（WM.14 恰一；FK→②，DDL 尾補；NULL=尚未指定=WM.14 違反態、不得被消費）
    ts_semantics       text NOT NULL,         -- 欄5a 時間戳語義（WM.31(a)）
    knowability_rule   text NOT NULL,         -- 欄5b 可知規則（WM.31(b)；anti-leakage 錨、#8）
    cross_market_axis  text,                  -- 欄5c A.35 第三項跨市場軸對映（如適用；RULING-2026-030 §五(f)）
    provenance         jsonb NOT NULL,        -- 欄6（來源、作成依據、採認狀態；Annex F 條目載明三要素）
    finality_predicate text NOT NULL DEFAULT '未宣告',  -- 欄7 定案性述語（WM.32/A.37；'未宣告'→推定 non-final）
    conflict_set_ref   text,                  -- WM.37 多通道衝突保存落點（預留承載位，非七欄之一）
    decided_by         text,                  -- 採認人（Annex F：Steward 附卷裁定；hugo 親簽、AI 不代打）
    decided_at         timestamptz,
    created_at         timestamptz NOT NULL DEFAULT now(),
    superseded_at      timestamptz            -- WM.13/WM.25 版本化：變更＝新列、舊列標時戳（append-only，不 UPDATE 內容欄）
);

-- ② 通道映射表（承 WM.36 欄 3：欄位級、一對多；WM.35 unmapped 顯式存量）
CREATE TABLE world_channel_binding (
    binding_id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    concept_key    text REFERENCES world_concept_registry(concept_key),  -- NULL ⇔ unmapped
    source_table   text NOT NULL,             -- 供應商表名（字面之唯一合法住所；如 'TaiwanStockPrice'、'fred_series'）
    source_column  text,                      -- 欄位級粒度（NULL＝表級暫登，見 §9 Q5）
    channel_role   text NOT NULL DEFAULT 'observation'
        CHECK (channel_role IN ('observation','derived')),  -- WM.15 衍生觀測（如 PriceAdj 對 Price）
    mapping_status text NOT NULL CHECK (mapping_status IN ('mapped','unmapped')),
    CHECK ((mapping_status='mapped') = (concept_key IS NOT NULL)),  -- unmapped 顯式、不得曖昧
    provenance     jsonb NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now(),
    superseded_at  timestamptz
);
ALTER TABLE world_concept_registry ADD CONSTRAINT fk_auth_binding
    FOREIGN KEY (authoritative_binding_id) REFERENCES world_channel_binding(binding_id);

-- ③ 絞殺帳本（非條文義務；#20 落地憑證機器可稽核——「紅燈會亮」：diff≠0 記紅列、不覆寫）
CREATE TABLE vendor_binding_strangler_ledger (
    file_path      text NOT NULL,
    batch          text NOT NULL,             -- 'A1-features' … 見 §6
    occurrences    int  NOT NULL,             -- 改線當下該檔直綁處數
    shadow_diff_rows bigint,                  -- 雙讀影子比對 diff 列數（0=可切；>0=熔斷紅列）
    verdict        text NOT NULL CHECK (verdict IN ('green','red','pending')),
    evidence_ref   text,                      -- 比對輸出留檔路徑
    verified_at    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (file_path, verified_at)
);
```

種子：Annex F 六條 → ① 六列（provenance.採認狀態='pending'、decided_by **留空待 hugo**）；`dataset_catalog` 97 列 → ② 全量通道登錄（初始 mapping_status='unmapped' 為誠實預設，Annex F 涉及之通道六概念先 mapped）。**不新增 honesty trigger 於本批**（treaty 表閘另案，避免 #3 越界）；append-only 紀律先以慣例＋lint 承載，是否上閘列 §10 供裁。

---

## §5 程式規畫（#20 (b)；檔・函式・職責・輸入輸出）

| # | 檔 | 職責與簽名 | 輸入→輸出 |
|---|---|---|---|
| 1 | `scripts/migrate_world_concept_ddl.py`（新） | DDL＋種子；`--check`（沙盒驗）／`--dry-run`（只印）／`--apply`（**需 hugo #6 明示**）；冪等 `to_regclass` guard | 讀 `dataset_catalog`、Annex F 文本 → 建 ①②③ 表＋種子列 |
| 2 | `src/augur/catalog/world_concept.py`（新） | 解析 API：`resolve(concept_key) -> Binding(table, column, role)`（經 ① 權威指定→②）；`resolve_sql(concept_key) -> str`（回引號表名，供 f-string 組 SQL）；`lru_cache`；`--selftest`＝凍結 fixture 零 DB 結構斷言（#18 v1.28）＋執行指令矩陣 | 讀 ①② → 回繫結物件；**vendor 字面自此只活在 DB 資料列** |
| 3 | `scripts/check_vendor_binding.py`（新） | lint 閘：掃描口徑＝`FROM\s+"[A-Z][A-Za-z]+"` ∪ `FROM\s+fred_series`（**比 F2 口徑寬**，含 US／fred 家族）；比對凍結 baseline（52 檔逐檔逐數）；**新增檔或增處即 exit≠0**；`--update-baseline` 須顯式旗標＋列印 diff；白名單（C/D 豁免）逐列附條文依據欄。零 DB 零 API 零 usage（#28、同 `check_cmd_matrix.py` 形制、掛 pre-commit/CI） | 讀 src/scripts 原始碼＋baseline 檔（repo 內 JSON＝**lint 工件非資料 SSOT**，#29(b) 豁免款：安全繫於機械閘之品質工程詞表屬邏輯側） |
| 4 | `scripts/compare_shadow_binding.py`（新） | 雙讀影子比對 runner（Phase 6(c) 協定）：對指定檔之每條改線 SQL，舊直綁 vs 新解析**同參數雙跑**、逐列 hash diff；結果落 ③ 帳本（green/red）；`--file`／`--batch`；diff≠0 即紅列＋exit≠0（熔斷、不切） | 讀 live DB 雙路 → 寫 ③（唯一寫入面、追加式） |
| 5 | 改線本體（A 類 29 檔、批次見 §6） | 每檔：`'FROM "TaiwanStockPrice"'` → `f'FROM {resolve_sql("tw.daily_bar")}'`；**不改語意、不順手重構**（#3）；每批 #19 過目 | 行為零變更（影子比對硬閘保證） |

**對 CODE-MIGRATION-PLAN Phase 6 之兩處修訂註記**：(i) 原案 `src/augur/core/registry.py` 之模組名 `registry` 撞 CLAUDE.md #18 **禁通用角色名清單**（build·registry·probe…）——改 `catalog/world_concept.py`（領域名詞、與載體候選 dataset_catalog 同 package）；(ii) 原案判準「37 檔 grep → 0」之計數已過期（現 52），判準句改「**A 類（暨 Steward 核定射程）grep → 0＋豁免白名單恰好＝lint 綠**」。

---

## §6 分階段與時程（#20 分階段；最晚里程碑倒推）

| 階段 | 內容 | 完成判準（驗收） | 最晚完成 |
|---|---|---|---|
| **G0** | 本呈案 Steward 拍板：讀法（§3）＋B 類歸屬（§9 Q1）＋DDL 形制（§4）＋§10 各欄 | hugo 書面裁示 | **08-16**（關鍵路徑起點；逾此壓縮 M3） |
| **M1** | DDL＋種子落地（沙盒 `--check` 綠→hugo 准 `--apply` 生產）；Annex F 六條 hugo 親簽採認 | ①=6 概念（decided_by=hugo）、②=通道全量（97 dataset 對映、unmapped 顯式）、`to_regclass` 非 NULL | 08-23 |
| **M2** | 解析 API＋**lint 閘上線**（pre-commit/CI 掛勾）——**封出血點**（07-17→08-02 淨增 +13 之止血；可提前至 G0 前先行凍結 baseline，止血不待拍板） | `world_concept.py --selftest` 綠；lint 閘**紅燈實證**＝故意加一行直綁確認 exit≠0（回歸鎖唯一有效驗法）後還原 | 08-30 |
| **M3** | A 類 29 檔絞殺五批：A1 features lib×7 → A2 build_*×6 → A3 train/produce×5（含 derive_market_iv）→ A4 arena×4＋sim×5 → A5 advisor/payload **最後**（Phase 6 順序：低風險先、advisor/predict 殿後）；每檔影子比對 green 才切、每批 #19 過目 | ③ 帳本 29 綠列；A 類 grep → 0 | **10-05**（本案最晚硬里程碑） |
| **M4** | B 類 15 檔（若 G0 裁入射程）；C/D 白名單登錄（逐列附 WM.35 句） | B 類 grep → 0 或白名單恰好；lint 全綠 | 10-10 |
| **M5** | 10-14 併審證據包：lint 綠證據＋③ 帳本全景＋grep 口徑數字＋殘餘白名單與依據＋（若有）豁免聲請草稿 | 證據包呈 hugo；**併審裁決屬 Steward，AI 僅整備** | 10-13 |

**工作量估計（附依據，self-reported）**：140 處／52 檔。36 檔×1–2 處：改線＋影子比對＋實測 ≈ 0.5 工作日/檔＝18 日；14 重檔（3–26 處）≈1.5 日/檔＝21 日 → 全量 ≈ **39 工作日**；讀法乙 A 類先行 ≈ **22 工作日**（29 檔含 5 重檔）。估計基礎＝每處為模板式替換＋每檔一輪雙讀 DB 比對（同尺四查：改前先驗該檔 SQL 覆蓋參數網格）；**未含**未知歧義（如動態組表名之檔——本輪 grep 未見但未逐檔 AST 排除，M3 逐批時親驗）。以 08-18 開工、Opus 檔位執行層＋每批過目節奏，10-05 前完成 A 類**可行但無鬆弛**；G0 每晚一週、M3 鬆弛減一週。

---

## §7 lint／CI 閘設計要點（#20 (c)）

1. **口徑寬於 F2**：`FROM\s+"[A-Z][A-Za-z]+"` ∪ `FROM\s+fred_series`（F2 之 `FROM\s+"Taiwan` 漏 fred 家族 2 檔——本報告已補；口徑本身凍在 baseline 檔頭、hash 自證）。
2. **凍結 baseline＋只降不升**：存量 52 檔逐檔處數；任何新檔或既有檔增處＝紅；改線後處數下降＝自動收緊（棘輪）。
3. **豁免白名單非裸名單**：每列 `{file, 條文依據, Steward 核可日}` 三欄俱全才生效；缺依據＝紅。
4. **紅燈會亮之自證**：`--selftest` 內建「植入直綁樣本→必紅」回歸鎖（防呆機制自己靜默失效之七型教訓；綠燈量的必須是它宣稱在量的東西）。
5. 掛勾點：pre-commit＋CI＋`check_cmd_matrix.py` 同節奏本地稽核；零 Claude usage。

---

## §8 選項比較

| 選項 | 內容 | 10-15 條文地位 | 工作量 | 建議 |
|---|---|---|---|---|
| 甲 全量絞殺 52 檔 | Registry＋52 檔改線 | 合規（無白名單） | ~39 工作日 | 次選（C/D 改線與 WM.35 觀測層明文重疊、對帳獨立性受間接層污染） |
| **乙 分層絞殺（建議）** | Registry＋A（＋B 依裁）改線＋C/D 白名單附 WM.35 依據 | 合規（判準句逐字滿足：消費模組解析至概念鍵；觀測層作業非「消費」） | ~22–37 工作日 | **建議案**；證偽條件見 §3 |
| 丙 Registry＋lint、消費點漸進 | 不改存量消費檔 | **10-15 起 A/B 類違規**（判準句原文）；唯 §8.4 有到期日豁免可救 | ~8 工作日 | 僅後備；豁免可用性見 §9 Q3 |
| 丁 什麼都不做 | — | 10-15 起生產管線整面落入消費禁令語境（F2 §8 原話） | 0 | 不可（039「不提早結清」反面＝也不得假關或放任） |

---

## §9 條文歧義——待 Steward 解釋（`AUGUR-MC v1.6 §8.1`；AI 不解釋、僅列問題與兩造證據）

1. **「消費世界模型之模組」射程是否及於 B 類（提拔關卡／研究掃描）？** 兩造：讀數成為晉升 Knowledge 之依據（WM.34(a) 語境→屬消費）vs「研究讀數、不進預測管線」自我宣告（benchmark_tsfm 檔頭）。C 類對帳依 WM.35 :338「得……對帳、追溯」字面似明文除外——**是否如此讀、亦請一併確認**。
2. **S22 code 層證據可否充當過渡等價？**（F2 §1(d) 原句之問）本報告證據整備：`import_isolation.py` 之字面集為 `SUPERSEDE_LITERALS`／`IDENTITY_LITERALS`／素養層 import——**不含任何 vendor 表名**；其 violations=0 與「WM.36 消費引用可解析至概念鍵」不同構，且自載三弱點（動態 SQL 不擋、射程 7 package＋core、無人機分辨力；GROUNDING-MAP S22 定案原文）。AI 呈事實：**不同構**；等價與否屬裁決。
3. **§8.4 豁免可用性**：WM.36 為 L1 [N] 非 MC 核心條款，落 §8.4「核心條款以外之 [N] 條款……履行時程」豁免範圍字面；但其消費規則為「不得」句，§8.4 又明示「**本憲章**任何禁止性規定（MUST NOT）均不得豁免」——「本憲章」是否及於 L1 規格之禁止句＝解釋問題（若及於，丙案後備即不存在）。
4. **Registry 條目採認程序**：Annex F「採認與登錄由 Steward 附卷裁定」——六條 seed 之 decided_by 是否即以本案 §10 簽核充當附卷裁定、或另立 RULING？（不代打人簽紀律：該欄一律 hugo 親跑寫入。）
5. **欄 3「粒度至欄位級」與表級暫登**：② 表 `source_column` NULL 之表級登錄是否構成「登錄完成」（七欄可解析）、抑或僅為 unmapped 同級之過渡態？影響 M1 驗收判準之嚴格度。

---

## §10 Steward 決定欄（留白待 hugo）

| # | 決定事項 | 選項 | 裁示 |
|---|---|---|---|
| 1 | 讀法（§3／§8） | 甲／乙／丙＋§8.4 聲請／其他 | **乙：分層絞殺**（Steward 圈選 2026-08-02＝條文解釋裁示；AskUserQuestion 留痕） |
| 2 | B 類 15 檔歸屬（§9 Q1） | 入射程／除外／逐檔另裁 | **入射程、排 A 後批**（M3 只硬綁 A；B 於 10-14 前盡力、不及則列併審誠實殘項） |
| 3 | DDL 形制（§4）與 append-only 是否上 trigger | 照案／修改 | **照案**（二表七欄溯源＋trigger 同 honesty 家族） |
| 4 | Annex F 六條採認方式（§9 Q4） | 本案簽核即附卷／另立 RULING | **簽核即附卷** |
| 5 | G0 拍板日與 M3 硬里程碑（§6） | 照案（08-16／10-05）／調整 | **G0＝2026-08-02（提前 14 日）**；M3＝10-05 硬不變 |
| 6 | lint 閘可否於 G0 前先行上線止血（僅凍 baseline、不含白名單） | 准／不准 | **准**（今晚即建；僅凍基線、新增即紅） |

---

## §11 附錄：52 檔逐檔清單（類別｜處數）

**A（29）**：src/augur/features/{chip 7｜fundamentals 2｜margin_cycle 1｜panel 2｜phase 1｜valuation 4｜macro_vintage fred}｜src/augur/advisor/payload.py 1｜src/augur/arena/adapters.py 1｜scripts/{build_daily_direction_features 7｜build_direction_stack_monthly 2｜build_feature_panel 1｜build_interaction_candidates 1｜build_market_direction_features 8｜build_pme_fundamental_features 1｜train_daily_direction 1｜train_direction_stack 1｜train_direction_threelens 1｜produce_direction_probability 1｜derive_market_iv 1｜run_arena_daily_pipeline 1｜run_arena_replay 2｜run_arena_round 2｜settle_arena_labels 2｜simulate_mc_paths 1｜simulate_portfolio_risk 3｜settle_sim_outcomes 1｜evaluate_sim_calibration 2｜run_sim_calibration_cell 1}
**B（15）**：scripts/verify_{candidate_promotion 1｜daytrade_candidates 1｜economic_candidate 1｜fundamental_candidates 4｜incremental_fair 3｜interaction_promotion 2｜regime_portfolio 1｜regime_timing 1｜signal_promotion 3}｜scripts/run_{cross_table_interaction_scan 4｜deep_interaction_scan 12｜raw_interaction_ic 2}｜src/augur/audit/{feature_candidate 1｜field_correlation 26}｜scripts/benchmark_tsfm_taiwan 1
**C（3）**：scripts/{full_universe_attest 1｜verify_units 3｜reconcile_audit fred}
**D（5）**：scripts/{backfill_entity_registry 3+fred｜backfill_lifecycle_retire 5｜sync_attribute_versions 2｜repair_priceadj_basis 2}｜src/augur/catalog/__init__.py 2

---

## §12 誠實揭露（L6.18(c)／`AUGUR-MC v1.6 §P4.E7`／CLAUDE.md #32）

本報告全部分類、歸類傾向、工作量估計為 **AI self-reported**，不構成「世界如此」之權威確認；全部量化數字出自本日唯讀實跑（指令逐條載於 §1，**任何人可零 AI 獨立重跑覆核**——此為不受提案 Agent 支配之覆核路徑，L6.18(c) 之滿足方式）。本案涉治理閘（lint）與 Registry 之新設，其**核准主體須為人類權威**（L6.18(a)）；本報告僅呈案。未做：未跑 S22（引 F2 08-01 值並註明）、未逐檔 AST 排除動態組表名（列 §6 估計未含項）、未驗 dataset_catalog 97 列與 84 raw 表之逐列對映完備性（M1 施工項）。本報告寫入 `reports/` 為本輪唯一產出；零 DDL、零 DB 寫入、零 commit。
