# TTAI / Tiptop ERP raw data 整合進 augur 知識層 — 整體做法 SOP 主計劃書

> **文件性質**：**plan-first 計劃書（非實作）**。本檔只寫「整合的整體做法、逐表映射、管線設計、治權隔離、分期 gate、決策清單、驗收判準」；**不含任何對 DB 的 INSERT/DDL 執行**。是否整合、以何治權承載，一律**決策層人拍板**後方進實作（憲章 v1.31–v1.33 plan-first 精神、CLAUDE #20 多步驟先計畫）。
> **撰寫日**：2026-07-06 ｜ **範圍錨**：ttai DB `buffer` schema 16 表（recon 實證時點）× augur 知識層三層管線 + 逐字語意層。
> **實證原則**：每個現況/數字標來源（ttai DB / augur code / 檔案）；本檔所引 augur code 事實均本輪親讀核對（見 §附錄 A 實證清單），非憑記憶。

---

## 標頭：定位與四組關係

| 面向 | 立場 |
|---|---|
| **性質** | 計劃書。整合與否、domain/license/access 承載方式**由人拍板**（§⑩）；未拍板前不落任何資料。 |
| **範圍** | ttai `buffer` schema 16 表 raw data（ERP 語意知識緩衝層）→ augur 知識層（`knowledge_item(_text)` + 語意層 + advisor 檢索）。 |
| **目標** | ERP know-how 可被 augur advisor **問答檢索**（表/欄位/程式/函式/代碼值/關係），逐條可溯源。 |
| **與 augur 治權的關係** | **素養/解讀層整合**：ERP 知識**零量化價值、不產因子、不進台股預測管線**（憲章 v1.19；import-lint `tests/test_philosophy_isolation.py` 物理擋 7 預測 package import `augur.knowledge`）。整合後只供 advisor 問答。 |
| **與 TTAI 專案的關係** | TTAI（`/home/hugo/project/ttai`）是成熟的 Tiptop ERP 語意抽取系統，有自己的治權檔/DB/Qdrant。本整合**只取 TTAI 的資料（4gl/4fd/欄位/程式語意）當 raw data**；**clean-room #16**：TTAI 的 loader/parser/exporter code **絕不回流 augur codebase**，augur 端 loader 依 5 治權檔重寫，可參考設計思想、不移植實作。 |

---

## ① 整合目標與定位

### 為何整合
augur advisor 已具「誠實博學的我」檢索問答骨架（哲學 works / 財經 items 兩域）。TTAI 已把 Tiptop ERP（Informix-4GL/Genero + Oracle 11.2.0.4.0）的不透明程式碼與 schema 忠實語意化成 142,040 個結構化知識單元、逐條帶溯源。整合後，advisor 多一個 **erp_tiptop** 素養域，回答企業 ERP 運維/開發的 know-how 問題。

### 整合後 advisor 能答什麼 ERP 問題（示例）

> ⚠ **檢索路徑現況（誠實 scope、決策點 D12）**：advisor 唯一組合檢索器 `retrieve_all`（`philosophy/retrieval.py:324`）只跑 **concordance + sentence-embedding over item_text**——**不查 `erp_edge` / 8 細節表**。故下列「**關係圖問答**」（reads/writes/uses_code 圖、哪些程式讀寫 `gap_file`、value_flow 衍生鏈）**現階段不由 `retrieve_all` 涵蓋、屬未來工作**（現版僅落地圖資料、不提供圖問答；是否建 ERP 關係圖檢索路徑見 §⑩ D12）。可由現版 sentence-embedding 回答者＝**item_text 逐字內容命中類**（表/欄位/程式的白話語意、代碼值註解等已入 item_text 者）。

- 「`gap_file` 這張表是做什麼的？有哪些欄位？」（table/column unit + `has_column` 關係）**〔圖問答部分＝未來工作 D12〕**
- 「哪些 4GL 程式會讀寫 `gap_file`？」（`reads`/`writes` 關係圖）**〔圖問答＝未來工作 D12、現版不涵蓋〕**
- 「`gap01` 欄位的合法代碼值有哪些？」（code_value + `uses_code` 關係）**〔圖問答＝未來工作 D12〕**
- 「程式 `p_develop` 的表單畫面欄位綁定到哪些 DB 欄位？」（form_field）**〔圖問答＝未來工作 D12〕**
- 「哪些 SQL 帶 `active_flag='Y'` 謂詞？」（sql_predicate）**〔圖問答＝未來工作 D12〕**
- 「這個欄位的值是怎麼從別的欄位衍生出來的？」（value_flow 衍生事實）**〔圖問答＝未來工作 D12〕**

### 明確邊界（治權鐵則，不可違反）
1. **零量化價值 / 不產因子 / 不進台股預測**：ERP 資料寫在 `augur.knowledge` / `augur.advisor` 前綴下，import-lint 保證 `features/models/universe/evaluation/ingestion/audit/catalog` 七 package 零 import knowledge（`tests/test_philosophy_isolation.py`）。
2. **三敵零容忍**：①每筆帶真實來源 provenance、禁 AI 生成入庫 ②#8 此域無時序預測、以 provenance/真實性為主 ③#15 誠實（不臆造、不佯稱）。
3. **clean-room #16**：ERP 4gl/4fd/程式碼/欄位是**資料**、可入知識層當 raw data；TTAI code 絕不回流。
4. **domain 隔離**：新增 `erp_tiptop` domain 須**人拍板**、domain 欄隔離保因子鏈純度。

---

## ② 來源盤點：ttai DB `buffer` schema 16 表 raw data 全貌

> 來源：`ttai/db/schema/001_buffer.sql` / `007_detail_tables.sql` / `008_column_meta.sql` / `002_export_view.sql` DDL；row counts 為 recon 提供時點（augur 帳號對 `buffer` schema **無 USAGE，SELECT 被拒 permission denied**，數字取自另一有權 session，見 §⑨ 權限陷阱）。

星狀知識圖，以 `knowledge_unit` 為中心：

| 表 | 列數 | 角色 | 關鍵欄 |
|---|---:|---|---|
| **knowledge_unit** ★核心 | 142,040 | 語意單元（1:1 對應 Qdrant point） | `unit_type`(十型 CHECK)/`erp_identifier`/`parent_id`(自參照樹)/`title`/**`semantic_text`**(繁中 Textualization)/`business_meaning`/`attributes` jsonb/`status`(六態)/`confidence`/`stable_key`(UNIQUE, UUIDv5 種子)/`content_hash` |
| **knowledge_source** | 102,564 | 溯源（每 unit ≥1） | `source_kind`∈{fgl_source, schema_dict, official_doc}/`source_ref`(檔:行號或 schema 物件)/`excerpt`(原文) |
| **knowledge_relation** | 67,914 | 知識圖的邊 | `from_unit_id`/`to_unit_id`/`relation_type`(FK→relation_type, **NOT VALID**)/`attributes` jsonb；UNIQUE(from,to,type) |
| **column_meta** | 39,563 | ERP 欄位結構（升一等） | `column_unit_id` PK/`table_name`/`data_type`/`char_length`/`nullable`/`ordinal`（來源 Oracle all_tab_columns） |
| **knowledge_unit_lang** | 13,934 | 逐語言 title/semantic_text | PK(unit_id,lang)/`lang`∈{'0'繁,'1'英,'2'簡}；缺語退繁中 |
| **function_meta** | 5,348 | 4GL 函式 | `program`/`signature`/`tables_used` text[](GIN)/`line_start`/`line_end`/`loc` |
| **buffer_embedding** | 3,482 | Qdrant 向量同步追蹤 | `embedding_model`(BAAI/bge-m3)/`embedding_dim`(1024)/`qdrant_collection`(ttai_kb_tiptop_11_2)/`qdrant_point_id` uuid/`status`。⚠ 3,482 ≪ 142,040＝PG 端追蹤不全，真態在 Qdrant |
| **sql_predicate** | 1,984 | SQL WHERE 謂詞（升一等） | `field`/`op`/`value`/`is_join`/`role`(wintitle/active_flag/lang_filter…) |
| **form_field** | 1,962 | 4FD 畫面欄位 | `form_unit_id`/`column_unit_id`/`col_name`/`sql_tab`/`label`/`widget`/`data_type`/`ordinal` |
| **program_meta** | 874 | 4GL 程式 | `module`(zz011)/`zz_class`(I/M/O/P/Q/R/S/T/U)/`origin`(standard/custom)/`is_hardcode`/`report_header`/`version_no`/`actions` jsonb/`links` text[]/`features`/`source_path` |
| **code_value** | 390 | 欄位合法代碼值 | `column_unit_id`/`code_value`/`label`/`lang`/`value_origin`。**憲章§5.1：raw data 不嵌向量、以 `uses_code` 連回** |
| **field_reference** | 121 | 欄位值參照 | `column_unit_id`→`ref_table_unit_id`/`via_form`/`mechanism`(controlp/INFIELD) |
| **extraction_run** | 74 | 抽取批次稽核 | `pipeline_stage`(extract/parse/textualize/link/buffer/verify)/`status`/`params` jsonb/`stats` jsonb |
| **value_flow** | 41 | 跨欄值衍生事實 | `target_unit_id`←`source_unit_id`/`source_expr`/`guard`/`join_left=join_right`/`fallback_seq`/`raw_sql`/`semantic_text` |
| **relation_type** | 17 | 受控詞表 | has_column/belongs_to_module/reads/writes/references/calls/has_function/has_sql/accesses/has_form/displays/uses_code/has_action/links/fk_ref/header_detail/sourced_from |
| **erp_system** | 1 | ERP 版本錨 | name(TiPTOP)/db_kind(oracle)/db_version(11.2.0.4.0)/schema_owner(ds)。守敵人③不混版 |

`v_qdrant_export` view：把每 unit 投影成 Qdrant point（`embed_text`=COALESCE(semantic_text, title, erp_identifier)；payload=核心欄+attributes+sources+relations+related_by+8 細節表 details；point id=UUIDv5(NAMESPACE 'ttai.knowledge_buffer', stable_key)）。

**`unit_type` 十型**：module / program / table / column / code / relation / process / function / form / sql。

---

## ③ 目標 schema：augur 知識層接口

> 來源：本輪親讀 `src/augur/knowledge/corpus.py`、`scripts/promote_knowledge.py`、`scripts/acquire_local_files.py`、`scripts/acquire_knowledge.py`；DB CHECK 為 `psql -d augur` 實查。

augur 知識層＝「來源 registry → acquire → staging → promote → 正式表」三層管線 + 逐字語意層。TTAI 有**兩條合法接口**：

- **接口 A（metadata 軌，registry）**：INSERT 一列 `knowledge_source` → `acquire_knowledge.py` 寫 `knowledge_staging`(pending) → `promote_knowledge.py` 寫 `knowledge_item`。**只寫 metadata，不寫 item_text**（實證：`promote_knowledge.py` 無任何 item_text INSERT）。⚠ 對 `--entity-type document` **未加 `MAPPERS['document']` 前於 l187 直接 sys.exit、整批 0 落地**（非誤判 dup）——修法見 §③關鍵表段 / §⑨ R8。
- **接口 B（逐字全文/本機檔軌）**：`acquire_local_files.py` 直寫 `knowledge_item`(entity_type='document') + `knowledge_item_text`，繞過 staging，`source_type='local_upload'` 硬編、`access_scope`/`license`/`owner_user_id` 由參數帶。**切句/嵌入/檢索唯一吃 item_text**，故 advisor 問答能力來自此軌。

### 關鍵表/常數（實查值）

- **`knowledge_item`**：`item_id`/`domain`(NOT NULL, 隔離鍵)/`entity_type` varchar32/`title`(NOT NULL)/`title_zh`/`year`/`authors`/`external_id`(跨源去重鍵)/`url`/`taxonomy_id`/`source_key`(可 NULL)/`staging_id`。去重 `uq_item_extid=(entity_type, external_id) WHERE extid NOT NULL`、`uq_item_title=(entity_type, md5(title), year) WHERE extid NULL`。
- **`knowledge_item_text`**：`content` text NOT NULL / `language` varchar8 / `source_url` NOT NULL / `license` varchar64 NOT NULL / `source_type` varchar24 / `access_scope` varchar16 DEFAULT public / `owner_user_id` bigint。**三道 DB CHECK 硬牆（實查）**：
  - `knowledge_item_text_license_check`：`license ∈ {public_domain, cc-by, cc-by-sa, cc0}`（**四值，不含自有資料值**）。
  - `chk_itext_source_type`：`source_type IS NULL OR source_type <> 'ai_generated'`。
  - `chk_itext_access_scope`：`access_scope ∈ {public, local_private}`（**僅二值**，無 internal/org）。
- **`corpus.py` CLEAN 閘（語意層唯一 SSOT，license 三道閘之核心）**：`LICENSE_WHITELIST = ("public_domain","cc-by","cc-by-sa","cc0")`；`SEMANTIC_ENTITY_TYPES = ("paper","report","document")`（**document 已在准入集**）。此常數同時餵**三個消費點**（親讀 code 實證，CLAUDE #19 一改須全鏈同步）：
  - **(閘 1) DB INSERT CHECK**：`knowledge_item_text_license_check` 與 `LICENSE_WHITELIST` 同集（入庫時擋）。
  - **(閘 2) 檢索/嵌入 CLEAN**：`clean_item_sql(item,itext)` 述詞 = `itext.license IN (LICENSE_WHITELIST) AND item.entity_type IN (SEMANTIC_ENTITY_TYPES)`（`corpus.py`:49），檢索器與 **`embed_knowledge.py` items 側**（`fetch_batch` l111-115，`is_super=True` 不做 RBAC 收窄但**仍吃 license×entity_type 閘**）皆經此。
  - **(閘 3) argparse choices**：`acquire_local_files.py:39` `--license choices=list(corpus.LICENSE_WHITELIST)`（入口即擋，比 DB CHECK 更早，見 §⑥.4）。
  - RBAC 收窄（僅檢索路徑、`is_super=False`）：local_private→owner_user_id 單人收窄（非 super 且 owner 缺→AND false deny）；public→domain=ANY(allowed_domains) 群組收窄。
- **`promote_knowledge.py`**（**親讀 l141-143 / l168-169 / l186-187 / l213 修正機制**）：`ITEM_TYPES=(paper,report,dataset,compound,material,protein,species)`；`EXTID_PRIORITY=(doi,arxiv_id,chembl_id,cid,uniprot_id,gbif_id,…)`（**不含 ttai key**）；`MAPPERS`（l168-169）= `{thinker,work,citation,school}` + ITEM_TYPES 七類，**無 `document` 鍵**。
  - **關鍵機制（R8 修正）**：`--entity-type document` 於 l186-187 `if args.etype not in MAPPERS: sys.exit(...)` **直接退出**——`document ∉ MAPPERS` → **整批 promote 硬失敗、0 落地**，**不是**「落 title+year 誤判 dup」。
  - 所謂「work 後援路」是 l213 `if res=='no_thinker' and args.etype=='work' and ...`——**僅對 `etype=='work'` 觸發，與 document 無關**；而 promote_item 內 l141-143 的 work_type 後援（`etype not in ITEM_TYPES → etype=p.get("work_type") or "paper"` → `ext=next(EXTID_PRIORITY…)` 落 None → title+year 去重）是**已 dispatch 到 promote_item 之後**才跑，document 在未加 MAPPERS 前**從未 dispatch 到那裡**。
  - **兩修法有先後依賴**：先加 `MAPPERS['document']=promote_item`（否則 l187 硬退出）→ 加了才輪到 promote_item l143 `ext` 落 None → **此時**才暴露 title+year 誤判 dup（ERP 大量同名欄位）→ 須再擴 `EXTID_PRIORITY += 'ttai_stable_key'`。順序不可倒，見 §⑨ R8 / §⑧ P1 gate。
- **`fileparse._TEXT_EXT`**：`{.txt,.md,.markdown,.csv,.tsv,.log,.json,.xml,…}` — **不含 .4gl/.4fd**（走本機檔路徑會 unknown_ext 靜默跳過）。
- **現有 domain（40 個）**：medicine/…/energy_materials/business_mgmt/finance_mgmt/investment_mgmt 等九管理域；**無 erp_tiptop**（整合須新增）。

### 整合寫法裁決（按治權鐵則排序）
1. **推薦＝逐字軌 document 路（仿 `acquire_local_files.py`）**：ERP 逐字真兆 → `knowledge_item(domain='erp_tiptop', entity_type='document')` + `knowledge_item_text`，天然過 CLEAN 閘（document ∈ 准入集）、接切句/嵌入/檢索。
2. **metadata 軌（registry）**：TTAI DB=新來源，寫專屬 DB-read adapter（TTAI 非 HTTP JSON → `generic_json` 不適用）。
3. **混合**：結構化欄位（column_meta/function_meta）metadata 入 item + 全文/註解逐字入 item_text（本計劃採此）。

---

## ④ 逐表逐欄映射表（ttai → augur）

> 原則：`knowledge_unit`→`knowledge_item`（一 unit 一列）；**逐字真實源**→`knowledge_item_text`；**`semantic_text`（Textualization 白話改寫）不入逐字表**（避 #1 爭議，見 §⑨ 命門）；8 張細節表→augur 端**旁掛 `erp_*_meta` 表**（保結構不硬塞泛型欄）；relation→**旁掛 `erp_edge` 表**（不塞哲學封閉集的 `knowledge_edge`）。

### 4.1 核心 unit → knowledge_item

| ttai `knowledge_unit` 欄 | augur `knowledge_item` 欄 | 轉換規則 |
|---|---|---|
| `stable_key`(UUIDv5 種子) | `external_id` | `'ttai:'+stable_key`（冪等去重鍵、**單一 item 設計之唯一 item 鍵**——metadata 軌〔G4〕建此 item；逐字軌〔G5〕只掛 item_text 到同一 item、不另建 item，見下方 ⚠ 衝突點）。⚠ 兩修法依賴序（R8）：①先 `MAPPERS['document']=promote_item`（否則 promote l187 硬退出、0 落地）②後擴 `EXTID_PRIORITY += 'ttai_stable_key'`（否則落 title+year 誤判 dup） |
| `erp_identifier`(gap_file / gap01 / p_zz) | `title` | 直填（穩定識別碼） |
| `title` / `knowledge_unit_lang(lang=0)` | `title_zh` | 繁中顯示名 |
| `unit_type`(十型) | `entity_type` | **統一映 `'document'`**（過 CLEAN 閘、零改 corpus）；unit_type 細分存旁掛 metadata。（替代：擴 `SEMANTIC_ENTITY_TYPES` 保留 program/table/column 細分，須拍板 P4） |
| （固定值） | `domain` | `'erp_tiptop'`（須人拍板新增） |
| `erp_identifier` | `url`(provenance) | `'ttai://'+erp_identifier` |
| `semantic_text` / `business_meaning` | **不入 item_text**；存 `title_zh` + 旁掛 `erp_unit_meta.semantic_text` 供顯示/圖檢索 | Textualization 白話改寫，降為 metadata（§⑨ 命門） |
| `year`/`authors` | NULL | ERP 無此語意 |

> ⚠ **雙軌建 item 去重命門（誠實設計修正 / 決策點 D11）**：metadata 軌（G4，`external_id='ttai:'+stable_key`）與逐字軌（G5 `acquire_local_files.py`，**現硬編 `external_id='localfile:'+sha1`**）對同一 unit 會**各建一列、彼此不去重** → knowledge_item(erp_tiptop) 計數翻倍、§⑪.3 對帳不可判定。**明訂單一 item 設計**：G4 metadata 軌建 item（`external_id='ttai:'+stable_key`）為**唯一 item**；逐字軌**只 ADD `item_text` 掛到同一 item、不另建 item**。**衝突點**：`acquire_local_files.py` 現硬編 `localfile:sha1` external_id 會另建 item——故逐字全文須改由 `promote_item` 掛 text，**或**本計畫明列此為需解的**介面缺口 + 決策點 D11「逐字文本掛載路徑」**（見 §⑩）。

### 4.2 逐字真兆 → knowledge_item_text（只入真實逐字源）

| ttai 來源 | augur `knowledge_item_text` 欄 | 規則 |
|---|---|---|
| `knowledge_source.excerpt`(4gl 檔頭 Descriptions/中文行內註解原文) + Oracle 資料字典欄位定義 + gat/gaq/gaz 多語真實名 | `content` | **只入逐字原文，不含 semantic_text** |
| `knowledge_unit_lang.lang` 0/1/2 | `language` | 0繁→`zh` / 1英→`en` / 2簡→`zh-cn`（對齊 augur ISO 慣例）。⚠ 此語碼轉換（'0'/'1'/'2' text）**僅適用 `knowledge_unit_lang.lang`（text）**；`code_value.lang` 為 **smallint（0/1/2）**、型別不同，若一併轉須先轉型別。 |
| `knowledge_source.source_kind`+`source_ref` | `source_url` | `'ttai://'+source_kind+':'+source_ref`（#1 可溯源） |
| （固定） | `license` | §⑩ D4 拍板值（現 CHECK 四值不含自有資料 → 須擴 CHECK 或走 metadata-only） |
| （固定） | `source_type` | `'local_upload'`（非 ai_generated，過 chk_itext_source_type） |
| （固定） | `access_scope` | `'local_private'`（或 public+domain grant，§⑩ D3） |
| （固定） | `owner_user_id` | ERP admin app_user（須先建列；若 public 則 NULL） |

### 4.3 relation → 旁掛 erp_edge（不塞 knowledge_edge）

`knowledge_relation`(67,914 邊, 17 型) → 新建 `erp_edge(edge_id / from_item_id FK / to_item_id FK / relation_type varchar32 / attributes jsonb, UNIQUE(from,to,type))`。`from/to_item_id` 經 `external_id='ttai:'+stable_key` JOIN 回 augur item_id。理由：`knowledge_edge.predicate` CHECK 是哲學封閉集，ERP 17 型塞不進。⚠ `relation_type` FK 是 **NOT VALID**，既有列可能有詞表外值，建 CHECK 前須 `EXCEPT` 實查去重（§⑨）。

### 4.4 8 細節表 → 旁掛 erp_*_meta（保結構不失真）

| ttai 表 | augur 旁掛表（皆 FK→knowledge_item.item_id） | 列數（recon 時點量級參考、非驗收基準） |
|---|---|---:|
| column_meta | `erp_column_meta`(table_name/data_type/char_length/nullable/ordinal) | 39,563 |
| function_meta | `erp_function_meta`(program/signature/tables_used text[]/line_start/line_end/loc) | 5,348 |
| program_meta | `erp_program_meta`(module/zz_class/origin/is_hardcode/report_header/version_no/actions jsonb/links text[]) | 874 |
| form_field | `erp_form_field`(col_name/sql_tab/label/widget/data_type/ordinal) | 1,962 |
| code_value | `erp_code_value`(code_value/label/lang/value_origin)。**§5.1 raw data 不嵌向量、只以 relation 連回** | 390 |
| sql_predicate | `erp_sql_predicate`(field/op/value/is_join/role) | 1,984 |
| value_flow | `erp_value_flow`(target←source/source_expr/guard/join/fallback_seq/raw_sql) | 41 |
| field_reference | `erp_field_reference`(ref_table/via_form/mechanism) | 121 |

> 表中括號欄為**示意、非完整 DDL**（l3 plan-first；如 value_flow 尚有 15+ 欄、program_meta 尚有 features/source_path 未列全）；各旁掛表權威欄規格見 ttai `007_detail_tables.sql` / `008_column_meta.sql`。

`extraction_run`/`run_id`＝ttai 內部管線稽核，**不重建**、僅作 provenance metadata。`buffer_embedding`（bge-m3/1024/Qdrant）**不遷移**（§⑦）。`erp_system`（版本錨）存 item.attributes 或旁掛 meta 保混版防護。

> **旁掛 9 表（erp_edge + 8 erp_*_meta）是實質 schema 變更**（非零 code 擴域），命名走 screaming architecture（`erp_column_meta` 是領域名詞，合規）；須治權審 + 人拍板（§⑩）。替代（輕）：整段收進 `knowledge_item.attributes` jsonb（失真、不推薦重度用）。

---

## ⑤ 擷取管線設計（指令級）

> 雙軌並用；**逐字必走接口 B**（advisor 問答關鍵）。取數走 `pg_dump -n buffer` 快照或人 GRANT（§⑥）。**唯一新 code＝一支 clean-room DB-read loader**，不移植 ttai code。

### G0 取數（繞權限牆）
```bash
# augur 帳號實測對 buffer schema permission denied → 二選一（人拍板）：
# (a) ttai 端授權（唯讀、可撤）
psql -d ttai -c "GRANT USAGE ON SCHEMA buffer TO augur; GRANT SELECT ON ALL TABLES IN SCHEMA buffer TO augur;"
# (b) 平行 dump（#30：先寫 ext4 後搬 drvfs）
pg_dump -n buffer -d ttai -Fd -j4 -Z1 -f /home/hugo/.../ttai_buffer_dump
#   → restore 進 augur 側唯讀 staging schema ttai_import（不污染 public）
# ⚠ 不動用 ttai/.env 跨專案憑證（classifier 正確擋 credential exploration）
# GATE：psql -d augur -c "SELECT count(*) FROM ttai_import.knowledge_unit" 回 142040
```

### G1 治權前置（人拍板後執行，見 §⑥/§⑩）
domain 註冊、license 承載、entity_type 閘、owner app_user。

### G2 註冊來源（metadata 軌，registry）
```bash
# INSERT knowledge_source 一列（manual_file adapter，沿用既有、不寫線上 DB adapter）
#   source_key='ttai_erp_units', adapter='manual_file', domain='erp_tiptop',
#   entity_type='document', note='Tiptop ERP knowledge_unit export, pg_dump -n buffer provenance'
python scripts/acquire_knowledge.py            # 無參 → 列出 ttai_erp_units（graceful #29a）
```

### G3 導出器 `scripts/acquire_ttai_erp.py`（唯一新 code，clean-room 重寫）
讀 ttai_import.knowledge_unit（JOIN knowledge_source 取逐字 excerpt、JOIN knowledge_unit_lang 取多語真實欄），分流：**metadata payload**（title/title_zh/external_id/url/relations/細節表）→ 攤平 JSONL 供 metadata 軌；**逐字 .txt**（4gl 檔頭/欄位註解/schema 字典，**不含 semantic_text**）→ 逐字目錄供接口 B。
```bash
python scripts/acquire_ttai_erp.py             # 無參 → 印指令矩陣（#29a graceful）
python scripts/acquire_ttai_erp.py --dry-run   # 印前 5 unit 攤平 JSON、0 traceback
# GATE：JSONL 行數=unit 數；每列有 external_id + ≥1 provenance source_ref（#1）
```

### G4 metadata 軌落地
```bash
python scripts/acquire_knowledge.py --source ttai_erp_units --file ttai_units.json \
    --domain erp_tiptop --entity-type document          # manual_file 逐列 stage()，ON CONFLICT 冪等
python scripts/promote_knowledge.py --entity-type document --domain erp_tiptop --dry-run  # 預覽
python scripts/promote_knowledge.py --entity-type document --domain erp_tiptop            # 正式
# ⚠ 修法一（必先）：MAPPERS 無 'document' 鍵 → 未加時 promote 於 l187 sys.exit「未知 entity_type」
#   整批 0 落地（非 title+year dup）→ 須加 MAPPERS['document']=promote_item（一行，執行層）
# ⚠ 修法二（依賴修法一）：加了 MAPPERS 才 dispatch 到 promote_item，此時 'ttai:'+stable_key 不在
#   EXTID_PRIORITY → l143 ext 落 None → 走 title+year 去重、ERP 同名欄位誤判 dup → 須擴 EXTID_PRIORITY += 'ttai_stable_key'
# GATE：SELECT count(*) FROM knowledge_item WHERE domain='erp_tiptop' = 匯入 unit 數
```

### G5 逐字文本軌落地（advisor 問答關鍵）
```bash
# ⚠ 單一 item 設計（決策點 D11，見 §④ 4.1 / §⑩）：逐字軌只 ADD item_text 到 G4 建的同一 item（external_id='ttai:'+stable_key）、
#   不另建 item。但 acquire_local_files.py 現硬編 external_id='localfile:'+sha1 → 對同一 unit 會另建第二列 item（去重命門、對帳翻倍）。
#   故逐字全文須改由 promote_item 掛 text 到既有 item，或先解此介面缺口（D11 未拍板前不得放量、否則對帳不可判定）。
# 逐字目錄一律 .txt 副檔名（fileparse._TEXT_EXT 不認 .4gl/.4fd）
python scripts/acquire_local_files.py --dir <erp逐字目錄> \
    --license <D4拍板值> --access-scope local_private --domain erp_tiptop --owner-user-id <admin>
#   直寫 item(entity_type='document') + item_text(source_type='local_upload' 硬編)、sha1 冪等
#   ⚠ 此路徑 external_id='localfile:sha1' 會另建 item ≠ G4 的 'ttai:stable_key' item（D11 衝突點）
# GATE：抽 10 unit content byte-equal 對 ttai excerpt；無任一列 content=semantic_text；
#       每 unit 僅一列 knowledge_item（逐字 item_text 掛在 G4 建的同一 item、無第二列 item）
```

### G6 語意層 + 檢索接通
```bash
python scripts/build_sentences.py --scope items     # 全庫增量切句（WHERE NOT review_flag）→ knowledge_sentence；
#   非 ERP-only 過濾——ERP 過濾在下游 embed CLEAN 閘（license×entity_type）與 P4 domain 計數
# ⚠ embed_knowledge.py 預設 scope=works（docstring l19）→ 對 ERP items 一句都不嵌;
#   須明指 --scope items --language <lang>;items 側再吃第三道 license×entity_type CLEAN 閘（clean_item_sql,
#   corpus.py:49）→ 若 D4 走 (b) metadata-only 或 license 未進 corpus.LICENSE_WHITELIST，縱使切句成功
#   也「嵌入 0 列、檢索永遠空手」（D4 採 (a) 須確認 proprietary_owned 已進 whitelist，embed 才吃得到）
python scripts/embed_knowledge.py --layer sentence --scope items --language zh   # e5-small dim384 重嵌 zh
python scripts/embed_knowledge.py --layer sentence --scope items --language en   #   en（棄 ttai bge-m3/buffer_embedding）
# retrieve_all 天然走 items 路徑（零改檢索器）；跨域隔離靠 RBAC grant 拓撲（單域對單群組部署）、
#   非 code 層 domain 過濾——retrieve_all 本身不 filter domain（D13，見 §⑦/§⑩）；private 路徑再吃 owner 收窄
# GATE：(1) SELECT count(*) FROM knowledge_sentence_embedding se JOIN knowledge_sentence s USING(sent_id)
#           JOIN knowledge_item_text x ON x.itext_id=s.itext_id JOIN knowledge_item i ON i.item_id=x.item_id
#           WHERE i.domain='erp_tiptop' —— 對 erp_tiptop 非零（防「切句成功但嵌 0 列」靜默失敗）
#       (2) retrieve_items('gap_file', domain='erp_tiptop') 回真命中且逐字回查 byte-equal
```

### G7 增量 / 冪等 / resume
三重去重：staging `uq_staging_payload=(entity_type, md5(payload))`、item `uq_item_extid=(document,'ttai:'+stable_key)`、item_text sha1。增量 `--since`（**單一鍵**：依 `ttai_import.knowledge_unit.content_hash`〔隨 pg_dump 帶入〕過濾變更 unit；extraction_run 未遷移〔§④ 4.4〕、故不用 finished_at）→ 重跑 G4/G5 天然 ON CONFLICT DO NOTHING 跳已存在；content_hash 變者走 review_flag 重嵌。排程非必要不建 cron（ttai 非高頻更新）；若要 harvest 型走 `harvest_knowledge.py` 單跑型（query_template 無 {query}）。

---

## ⑥ domain 註冊與治權隔離落實

1. **domain 註冊（阻塞真偽——誠實標註實查）**：走 sanctioned 工具（非手 INSERT）`python scripts/manage_rbac_user.py --add-domain --domain erp_tiptop --label 'Tiptop ERP 知識' --authz-boundary`（`manage_rbac_user.py` 僅有 store_true 的 `--authz-boundary`、無 `--no-authz-boundary`；§⑩ D3 已拍板走 boundary=true 之 public 授權邊界路）。`is_investment` 天然 false（seed 邏輯僅 domain=='investment' 才 true）＝因子鏈純度宣告鎖。`knowledge_domain_map` 走手動域恆等列供 harvest JOIN 治理閘（未對映天然排除）。
   - **⚠ 阻塞程度誠實（實查 code、勿高估 DB 硬牆）**：`knowledge_item.domain` **無 FK、無 CHECK**（僅 `varchar NOT NULL`）；`acquire_local_files.py --domain` 亦**無 domain 存在性校驗**。故「新增 domain 須人拍板」是**治權治理規則、非 DB 物理擋**——任何 INSERT `domain='erp_tiptop'` 的 item 不觸任何約束即落地。**真正吃 `knowledge_domain` 字典硬擋的只有**：(a) RBAC 授權——`manage_rbac_user.py --grant-domain` 於 `manage_rbac_user.py:145` `sys.exit「不在字典（先 --add-domain 由決策層拍板）」`（只在 grant 時擋，且 l147 再擋未拍為 authz_boundary）；(b) harvest 的 `knowledge_domain_map` JOIN 治理閘（未對映天然排除）。
   - **路徑差異的落地後果**：若走 D3 建議的 **public + group_domain_grant**，grant 時字典硬擋（good，DB 背書）；但若走 **local_private owner 收窄**，item 落地**完全繞過 `knowledge_domain` 字典**、「人拍板」**無 DB 背書**、只能人工核（P1 gate「domain 已拍板」屬人工判準）。若要 DB 級鎖「未拍板域不得落 item」，須另加 `knowledge_item.domain` 的 CHECK/FK→`knowledge_domain`（屬 schema 變更，人拍板，見 §⑩ D1）。
2. **import-lint 隔離（不變式）**：ERP loader 住 `augur.knowledge` 前綴（既有 `FORBIDDEN` 集）。跑 `pytest tests/test_philosophy_isolation.py` 綠＝7 預測 package 零 import knowledge。`grep -rn 'erp_tiptop' src/augur/{features,models,universe,evaluation,ingestion,audit,catalog}` 零命中。
3. **access_scope / RBAC**：`corpus.clean_item_sql` 兩軸——local_private→owner_user_id 單人收窄（fail-closed）；public→domain grant 群組收窄。ERP 全公司共享語意用單人 owner 不貼切 → **建議 public + 升 erp_tiptop 為 is_authz_boundary=true + group_domain_grant 授 ERP 顧問群組**（§⑩ D3 人拍板）。前置：app_user 須有對應列。
4. **provenance / license（三個連動點、非兩處，實查 code）**：每筆帶 ttai `knowledge_source`(source_kind/source_ref) → `item_text.source_url`；license 現 CHECK 四值不含自有資料 → §⑩ D4 拍板。若 D4=(a) 加 `proprietary_owned`，**須同一提交同步三個連動點**（CLAUDE #19 一處改全鏈對齊，缺一則某層先炸）：
   - **(i) DB CHECK** `knowledge_item_text_license_check`（不改 → INSERT 違 CHECK）。
   - **(ii) `corpus.LICENSE_WHITELIST`**——此常數**一改連動兩個下游**：`clean_item_sql` 述詞（不改 → 逐字入了也「檢索/嵌入 CLEAN 空手」）**及** `acquire_local_files.py:39` 的 `--license choices=list(corpus.LICENSE_WHITELIST)`（不改 → 逐字軌 **argparse 入口即拒**，比 DB CHECK 更早炸）。
   - **依賴鏈易漏認**：審者易誤以為「改 DB CHECK 就夠」——實則改 DB 而未改 corpus，逐字軌在 argparse 層（(ii)）即被拒、根本進不到 DB CHECK。**幸而 argparse choices 讀的正是 `corpus.LICENSE_WHITELIST`，故改 corpus 一處即連動 argparse choices + clean_item_sql 兩處**；但 DB CHECK 是獨立的一處，須另改。三者同一提交（P1 gate 加驗，見 §⑧）。

   `source_type='local_upload'`（非 ai_generated，過 chk_itext_source_type）。若 D4=(b) metadata-only，則明示 advisor 對 ERP「零逐字可嵌、檢索空手」的能力後果（見 §⑦/§⑩ D4）。
5. **clean-room #16 稽核**：新 loader header 標「clean-room 重寫、不移植 ttai code」；`git diff` 新增檔無 ttai 路徑 import；人工 review 無 ttai code 片段。

---

## ⑦ 文本理解與嵌入/檢索整合

- **統一向量空間（不遷 ttai 向量）**：ttai=bge-m3/dim1024/Qdrant/具名 zh-en-cn/Cosine；augur=e5-small/dim384/pgvector。維度+模型+query prefix+embedspec 世代全異，`embedspec.dim_for` **fail-closed 擋異維**。`buffer_embedding`（僅 3,482 列）遷移無意義 → **augur 端重嵌全量**。ttai 三語具名向量在 augur 以 `knowledge_sentence.language` 分區近似。
- **粒度**：結構化 item（每 ERP 物件一 knowledge_item），**非逐字 concordance/lexicon**——4gl/4fd 高噪（關鍵字/變數名/omef## 欄位碼污染逐字層，類 zh 單字 junk 前例）。逐字 concordance 僅對「含中文說明類 unit」有效；純程式碼 unit 走 metadata/圖資料。⚠ **「圖檢索/圖問答」現版不存在**——`retrieve_all` 不查 `erp_edge`、圖資料僅落地不可問答（決策點 D12、屬未來工作，見 §①/§⑩）。
- **嵌什麼（命門）**：只嵌**逐字真兆**（4gl 中文檔頭/欄位行內註解/gat-gaq-gaz 多語欄/Oracle 資料字典）；`semantic_text` 降 metadata 不進向量索引；`code_value` 沿 §5.1 分界不嵌。
- **嵌入指令與第三道 CLEAN 閘（易漏，實查 `embed_knowledge.py`）**：`embed_knowledge.py` **預設 `scope=works`**（docstring l19）→ 對 ERP items 不加 `--scope items --language <lang>` **一句都不嵌**（docstring l7 明文「用戶拍板前不得對 items 側放量嵌入」＝治權級閘）。且 items 側（`fetch_batch` l111-115）硬套 `corpus.clean_item_sql(is_super=True)`，其述詞 = `license IN LICENSE_WHITELIST AND entity_type IN SEMANTIC_ENTITY_TYPES`（`corpus.py:49`）——故 license **不只在 INSERT CHECK 一處**，而是「**INSERT CHECK + 檢索 CLEAN + 嵌入 CLEAN**」三道，全鎖同一 `LICENSE_WHITELIST`。**後果**：若 D4 走 (b) metadata-only 或 license 未進 `corpus.LICENSE_WHITELIST`，ERP 逐字 item 縱使入了 item_text 也「切句成功但**嵌入 0 列、檢索永遠空手**」，而 P4 gate「嵌入覆蓋達標」會**靜默失敗查不出因**。故：D4 採 (a) 須確認 `proprietary_owned` 進 `corpus.LICENSE_WHITELIST` 後 embed 才吃得到；採 (b) 明示 advisor 對 ERP 零逐字可嵌之能力後果。P4 gate 須加驗 `knowledge_sentence_embedding` 對 erp_tiptop 非零（見 §⑧）。
- **三域共檢索零改檢索器（跨域隔離靠 RBAC grant 拓撲、非 code 層 domain 過濾）**：`retrieve_all` 三路徑（works 公開 / public items **RBAC allowed_domains 群組收窄** / private items **owner 擁有者收窄**）zip 合併，**本身不傳 domain 過濾參數**。故跨域隔離**倚賴 RBAC grant 拓撲**——部署為**單域對單群組**（ERP 顧問群組只獲授 `erp_tiptop`、財經分析師只獲授 finance），而**非 code 層 domain 硬過濾**。若要 code 層 domain 硬過濾（不依賴 grant 拓撲）須改 `retrieve_all`（決策點 D13，見 §⑩）。
- **guard 把關**：引文閘（引號≥8 字須逐字 ⊂ citation）+ `verify_verbatim_item`（citation.text == content substring）天然把關 ERP 引文＝真實 ERP 源逐字。因 content 只入逐字源，此閘對 ERP 自動生效、無須改。空檢索 → `NO_KNOWLEDGE_RESPONSE` 固定句。

---

## ⑧ 分期執行序（pilot → 放量，每期 audit gate）

| 期 | 內容 | audit gate（可驗證判準） |
|---|---|---|
| **P0 治權前置 + 快照取數 + 命門實查** | pg_dump/GRANT 取數；抽樣 `SELECT unit_type, semantic_text, business_meaning FROM buffer.knowledge_unit LIMIT 200` **逐筆判 semantic_text 是否 AI/LLM 生成**；決策 license 承載 | (1) semantic_text AI 判定**有實查證據非推測** (2) 每 unit trace 回 source_ref (3) license 承載經人拍板且 code 一致；缺一停 |
| **P1 domain 註冊 + mapper（zero-data DDL）** | INSERT domain_map 恆等列；擴/確認 entity_type 閘；寫 loader；**先**加 `MAPPERS['document']`、**後**加 `EXTID_PRIORITY += 'ttai_stable_key'`（依賴序，見 R8）；D4=(a) 時三連動點同一提交（DB CHECK + corpus.LICENSE_WHITELIST〔連動 clean_item_sql + argparse choices〕）；**D1=(採 DB 級鎖) 時鏡射 D4 條件化 pattern**——若採加 `knowledge_item.domain` 的 CHECK/FK→`knowledge_domain`（DB 級鎖「未拍板域不得落 item」），P1 實跑確認該 CHECK/FK 已落地 | (1) domain_map/CHECK 全綠、`\d knowledge_item_text` CHECK 含承載值 (2) mapper 5 筆手造 dry-run **實跑 `promote_knowledge.py --entity-type document` 確認不在 l187 sys.exit**、external_id 唯一（驗 ttai_stable_key 生效非落 title+year） (3) D4=(a) 時 `acquire_local_files.py --license proprietary_owned --dry-run` **不被 argparse choices 拒**（驗 corpus.LICENSE_WHITELIST 已連動） (4) `pytest tests/test_philosophy_isolation.py` 綠 (5) **D1=(採 DB 級鎖) 時**：`\d knowledge_item` 顯示 domain CHECK/FK 已落地、INSERT 未拍板域 item 被擋（驗 DB 級鎖生效非僅人工核） |
| **P2 pilot 100 unit** | **(plan-first；各 gate 通過且 §⑩ 決策全拍板後方執行)** 單 transaction 落 100 unit（跨 unit_type：table/column/function/program/form 各 20）→ item+item_text → build_sentences → embed → retrieve 5 題 | (1) 100/100 provenance 可溯 (2) content byte-equal 對快照零失真 (3) 重跑 dup 全跳 (4) retrieve 命中且 access_scope 收窄正確 (5) **ROLLBACK 演練**：DELETE WHERE domain='erp_tiptop' 級聯清乾淨、他域列數不變 |
| **P3 中量 2k + 去重/衝突稽核** | **(plan-first；各 gate 通過且 §⑩ 決策全拍板後方執行)** 落 2,000 unit（全型分層）；跨域撞名稽核（omef03/gap01 vs 既有域）；concordance junk 率抽查 | (1) uq_item_extid/uq_item_title 零違反 (2) 跨域撞名人審無語意混淆（domain 已物理隔離） (3) junk 率可接受、否則該類標 metadata-only (4) 全程可 rollback |
| **P4 全量 142k + 嵌入** | **(plan-first；各 gate 通過且 §⑩ 決策全拍板後方執行)** 游標分批（每批 5k，DB-driven resume by external_id）背景跑；**嵌入須 `embed_knowledge.py --layer sentence --scope items --language zh`（及 en）**（預設 scope=works 對 ERP 零嵌）；e5-small CPU 本地零 usage（#28）；#22 過夜 systemd-inhibit | (1) item 數=快照 unit 數（扣 metadata-only/review_flag）無漏 (2) provenance 100%（source_url IS NULL count=0） (3) **嵌入覆蓋非零且達標**——`SELECT count(*) FROM knowledge_sentence_embedding se JOIN knowledge_sentence s USING(sent_id) JOIN knowledge_item_text x ON x.itext_id=s.itext_id JOIN knowledge_item i ON i.item_id=x.item_id WHERE i.domain='erp_tiptop'` **> 0**（防第三道 CLEAN 閘致「切句成功嵌 0 列」靜默失敗）、embedspec 世代正確 (4) import-lint 再綠 (5) advisor 30 題抽測誠實無臆造 |
| **P5 誠實紅線最終驗證** | **(plan-first；各 gate 通過且 §⑩ 決策全拍板後方執行)** 確證未污染台股預測、無假兆入庫；寫整合報告附每 gate 數字 | (1) 隔離測試綠 (2) features/models/universe 產物零 erp_tiptop 欄 (3) 全 item_text source_type 非 ai_generated (4) 每 gate 數字可 trace(#9/#10) |

---

## ⑨ 風險與誠實紅線

| # | 風險 | 緩解 |
|---|---|---|
| R1 **#1 命門（最高）** | ttai `semantic_text`=Textualization 白話語意化（憲章§2.1）。**視角提供的實證線索**：`textualize_from_details.py` 以 f-string 從真實細節表（value_flow/code_value）**確定性組裝、非 LLM 生成**（對映 `knowledge_edge.provenance='string_rule'` 同構）。但 `business_meaning` 若有 `enrich_*.py` LLM 環節則違 #1。**本輪未逐一實查全部 enrich 腳本，且 augur 帳號無 buffer SELECT 權無法抽樣**。 | 合規路：**只嵌逐字真兆**、semantic_text 降 metadata。judgment 須 **P0 實查抽樣後拍板，不可憑推測**。判 AI 生成則絕不入 item_text（chk_itext_source_type 硬擋 + verbatim guard 必炸）。 |
| R2 **license 三道閘（非單一 CHECK）** | license 鎖同一 `LICENSE_WHITELIST` 於**三處**：(1) DB INSERT CHECK `knowledge_item_text_license_check`〔僅 {public_domain,cc-by,cc-by-sa,cc0}〕 (2) 檢索/嵌入 `clean_item_sql` 述詞（`corpus.py:49`；含 `embed_knowledge.py` items 側 `is_super=True` 仍吃） (3) `acquire_local_files.py:39` argparse `choices=list(corpus.LICENSE_WHITELIST)`（入口最早炸）。TTAI 自有非 CC → 任一未同步即某層失敗；最隱者＝改 DB 未改 corpus → 逐字入了也「嵌入 0 列、檢索空手」。 | §⑩ D4 先拍板；D4=(a) 須**三連動點同一提交**（DB CHECK + corpus.LICENSE_WHITELIST〔連動 clean_item_sql + argparse〕，CLAUDE #19）；或走 metadata-only（明示零逐字可嵌）。未決不得進 pilot。 |
| R3 **ttai 權限陷阱** | augur 帳號實測 **permission denied for schema buffer**；task/recon「augur 帳號可讀」與實測不符。 | P0 強制先 GRANT 或 pg_dump -n buffer；不動用 ttai/.env 跨專案憑證。 |
| R4 **向量混維違憲** | 直搬 buffer_embedding(bge-m3/1024)進 pgvector(e5/384)=混語意空間，embedspec.dim_for fail-closed 擋。 | 一律 augur 端重嵌，不遷向量。 |
| R5 **relation_type FK NOT VALID** | 既有列可能有 17 型詞表外值。 | 建 erp_edge CHECK 前 `SELECT DISTINCT relation_type EXCEPT SELECT code FROM relation_type` 實查去重。 |
| R6 **4gl/4fd 逐字高噪** | 程式關鍵字/變數名/omef## 欄位碼污染 concordance。 | 純程式碼 unit 走 metadata/圖檢索、逐字 concordance 僅對含中文說明 unit。 |
| R7 **promote_item 只寫 metadata** | 誤以為 registry 軌就能餵 advisor 問答→切句/嵌入無料。 | 明確雙軌，逐字必走接口 B。 |
| R8 **document promote 硬失敗 → 去重（兩段機制、順序不可倒）** | 實碼機制（親讀 promote_knowledge.py）：**(段一) 未加 MAPPERS['document'] 時 `--entity-type document` 於 l186-187 `sys.exit`，整批 0 落地**（非「落 title+year 誤判 dup」——所謂 work 後援路 l213 只對 etype=='work' 觸發、與 document 無關；l141-143 work_type 後援在 dispatch 之後、document 未 dispatch 到那）。**(段二) 加 MAPPERS['document']=promote_item 後才 dispatch**，此時 'ttai:'+stable_key 不在 EXTID_PRIORITY → l143 ext 落 None → title+year 去重，ERP 同名欄位誤判 dup 漏入。 | **兩修法先後依賴**：①先 `MAPPERS['document']=promote_item`（解 l187 硬退出）②後 `EXTID_PRIORITY += 'ttai_stable_key'`（解 title+year dup，加了 MAPPERS 才暴露）。**不可塞進 openalex_id 等既有鍵造假 provenance（違 #1）**。P1 gate 實跑 `--entity-type document` 確認不 exit。 |
| R9 **staging md5(payload) 漏去重** | payload 微異（relation 順序/fetched_at）→ md5 變 → 漏去重。 | export payload 鍵排序穩定化 + 依賴 item 側 external_id 為真去重層（走接口 B 直入更穩）。 |
| R10 **fileparse 不認 .4gl/.4fd** | 走本機檔路徑 unknown_ext 靜默漏。 | 逐字 export 一律 .txt；只餵抽出的中文註解段非整檔。 |
| R11 **旁掛 9 表 schema 膨脹** | 非零 code 擴域、實質 schema 變更。 | 治權審 + 人拍板；命名 screaming architecture；clean-room 不移植 ttai schema code。 |
| R12 **台股預測污染（誠實紅線）** | 理論上 domain 隔離+import-lint 已擋，但誤引入 features/。 | P5 隔離測試 + 產物實查雙驗；任何 ERP 欄出現在預測產物即整合失敗回滾。 |
| R13 **覆蓋誤判** | buffer_embedding 3,482 ≪ 142,040=PG 端追蹤不全，真態在 Qdrant。 | augur 端一律重嵌全量、不信 ttai 覆蓋數。 |

---

## ⑩ 決策層拍板清單（所有 decision points 匯總）

> 全屬「變更判準 / 新增域 / DB schema 變更 / 授權政策 / 外部副作用」＝**決策層人拍板**（CLAUDE #26 護欄）；AI 不自行跨越。

| ID | 決策 | 選項 | 建議 | 阻塞 |
|---|---|---|---|---|
| **D1** | 新增 domain | `erp_tiptop`（保 ERP 版本錨、未來多 ERP 可再開）vs `software_erp`（通用） | `erp_tiptop` | **⚠ item.domain 無 FK/CHECK（實查）**：拍板是**治理性質、非 DB 物理擋**（任何人可 INSERT 該 domain item 不觸約束）；唯 public+`--grant-domain` 路徑經 `knowledge_domain` 字典硬擋（`manage_rbac_user.py:145`）、harvest domain_map JOIN 治理閘吃字典。若要 DB 級鎖「未拍板域不得落 item」須另加 CHECK/FK（schema 變更、併此拍板）；否則 gate「domain 已拍板」僅能人工核。 |
| **D2** | `is_investment` 確認 | 維持 false（宣告式純度鎖 + import-lint） | false（永不翻 investment） | 因子鏈純度 |
| **D3** | access_scope 政策 | local_private 單人 owner 收窄 vs **public + is_authz_boundary=true + group_domain_grant 群組共享** | 後者（ERP 全公司共享語意；owner 單人不貼切） | RBAC 授權邊界、可見性 |
| **D4** | license 承載（**命門**） | (a) 擴 `proprietary_owned`——須**三連動點同一提交**：DB CHECK ＋ `corpus.LICENSE_WHITELIST`（此常數同時餵 clean_item_sql 述詞 ＋ acquire_local_files argparse choices；改 DB 未改 corpus → argparse 先炸／逐字入了也嵌入 0 列檢索空手），改 DB CHECK 屬治權變更 vs (b) 純 metadata 不入 item_text（**advisor 對 ERP 零逐字可嵌、檢索空手**、問答能力大減，須明示此能力後果） vs (c) 借 cc0（語意造假，不推薦） | (a) 最合自有資料治理原意 | item_text 能否逐字入、**且嵌入層第三道 CLEAN 閘能否吃到**（G5/G6/P4 全卡於此） |
| **D5** | `semantic_text` 去留（**#1 命門**） | 實查判定是否 AI 生成：AI→只存 metadata；規則/人工→可入逐字 | **P0 實查後拍板**（不可推測） | 整合能嵌什麼、整合價值核心 |
| **D6** | entity_type 粒度 | 統一 `document`（零改 corpus、天然過閘） vs 擴 SEMANTIC_ENTITY_TYPES 納 program/table/column（改封閉集 P4） | `document` 統一 | 檢索粒度、是否進切句/嵌入 |
| **D7** | 向量策略 | **重嵌 e5-small dim384**（棄 ttai bge-m3） vs 雙後端 advisor 融合 | 重嵌（本地批跑省 usage；混維違憲不可直搬） | 檢索一致性 |
| **D8** | ttai 取數授權 | ttai 端 GRANT SELECT vs `pg_dump -n buffer` 快照 | dump（符 clean-room、不需長期跨庫權） | P0 前無法進行 |
| **D9** | 細節表整合深度 | 建 9 張旁掛 `erp_*_meta`（重、保真） vs 收進 item.attributes jsonb（輕、失真） | 旁掛表保真（須治權審 R11） | schema 變更範圍 |
| **D10** | ERP admin app_user | 若走 local_private 須先建 owner 使用者列 | 依 D3 定（public 則免） | owner_user_id FK |
| **D11** | 逐字文本掛載路徑（**去重命門**） | (a) 改由 `promote_item` 把逐字 item_text 掛到 G4 建的**同一 item**（`external_id='ttai:'+stable_key`） vs (b) 沿用 `acquire_local_files.py`（現硬編 `external_id='localfile:'+sha1`、對同一 unit **另建第二列 item**→對帳翻倍不可判定） | ✅**已定 (a)**（用戶 2026-07-06）：G4 建唯一 item、逐字走 `promote_item` 掛同一 item（不用 acquire_local_files 另建） | knowledge_item 計數是否翻倍、§⑪.3 對帳可否判定 |
| **D12** | ERP 關係圖檢索路徑 | (a) 現版**僅落地圖資料（erp_edge/8 細節表）、不提供圖問答**——`retrieve_all` 只跑 concordance+sentence-embedding、不查 erp_edge vs (b) 擴 `retrieve_all` 或新建檢索器讀 erp_edge（未來工作） | ✅**已定 (a)**（用戶 2026-07-06）：圖問答列未來工作、現版只落圖資料備查 | §①/§⑦/§④.3 承諾之「reads/writes/uses_code 圖問答」是否現版可用 |
| **D13** | domain 是否 code 層硬過濾 | (a) 現版**靠 RBAC grant 拓撲**跨域隔離（單域對單群組部署）、`retrieve_all` 本身**不 filter domain** vs (b) 改 `retrieve_all` 加 code 層 domain 硬過濾（不依賴 grant 拓撲） | ✅**已定 (a)**（用戶 2026-07-06）：靠 RBAC 單域對單群組拓撲、`retrieve_all` 不 filter domain；前提=授權拓撲乾淨（不單一 principal 跨授 finance+erp） | 跨域隔離倚賴 grant 拓撲抑或 code 過濾 |

---

## ⑪ 資源估算與驗收判準

### 資源估算
- **資料量級**：142,040 unit，逐字真兆平均數百字/unit，量級可控（現庫 item_text 語料以哲學/財經為主；ERP 是首個大批 document 域）。
- **取數**：pg_dump -n buffer（ttai DB 214MB，buffer 為主體）→ 平行 dump（#30）分鐘級。
- **嵌入**：e5-small dim384 CPU 本地批跑＝**零 Claude usage**（執行層 #28 本地優先，不繞 model/subagent）；游標分批 resume-safe。
- **usage 原則**：整合屬執行層（機械落地/計算）→ 省 usage 為先（本地腳本、批次、背景不輪詢）；唯 D5 semantic_text 真兆判讀屬理解層 → ultracode 窮盡實查（#28 二分）。

### 整合完成驗收判準（全綠才宣告完成，否則明說未竟）
1. **provenance 100%**：`SELECT count(*) FROM knowledge_item_text it JOIN knowledge_item i USING(item_id) WHERE i.domain='erp_tiptop' AND source_url IS NULL` = 0。
2. **零 AI 生成入庫**：`SELECT DISTINCT source_type ... WHERE domain='erp_tiptop'` 無 'ai_generated'；若 semantic_text 判 AI 則確認未入 item_text。
3. **列數對帳**：對帳基準 = **P0 快照（`pg_dump -n buffer` / GRANT 後 augur 端實 count）**、§④ 4.4 之 recon 數僅量級參考、非驗收基準。單一 item 設計（見 §④ 4.1 / §⑤ G4-G5）下 knowledge_item(erp_tiptop) = 快照 **unit 數（一 unit 一 item、逐字軌只掛 text 不另建 item）**（扣 metadata-only/review_flag）；erp_*_meta 逐表 count 與 P0 快照逐表 count 全等。
4. **隔離不變式**：`pytest tests/test_philosophy_isolation.py` 綠；features/models/universe 產物零 ERP 欄。
5. **檢索可用（跨域隔離倚賴 RBAC grant 拓撲、非 code 層 domain 過濾）**：retrieve_all（ERP admin/群組）回真命中、逐字 byte-equal、access_scope 收窄正確。跨域隔離**在單域對單群組部署下驗**——ERP 顧問群組只獲授 `erp_tiptop`（財經分析師只獲授 finance），故其 query 天然不回他域；`retrieve_all` 本身不 filter domain（若要 code 層 domain 硬過濾須改 retrieve_all，D13）。
6. **guard 通過**：ERP 引文逐字 ⊂ 真實源 → guard pass；潤飾一字 → guard 攔；空檢索 → 固定句。
7. **每 gate 數字可 trace**（#9/#10）；整合報告寫入 `reports/`。

---

## 附錄 A：本輪 augur code 實證清單（非憑記憶）

- `src/augur/knowledge/corpus.py`：`LICENSE_WHITELIST=("public_domain","cc-by","cc-by-sa","cc0")`（**:15**）；`SEMANTIC_ENTITY_TYPES=("paper","report","document")`（**:20**）；`clean_item_sql` license×entity_type 述詞 `license IN LICENSE_WHITELIST AND entity_type IN SEMANTIC_ENTITY_TYPES`（**:49-50**）+ RBAC 收窄（此二常數同餵 DB CHECK 集、clean_item_sql、argparse choices 三消費點）。
- `scripts/promote_knowledge.py`：`ITEM_TYPES`(7 類, l125)；`EXTID_PRIORITY`(doi/arxiv_id/… 不含 ttai, l127)；`MAPPERS`(l168-169)＝{thinker,work,citation,school}+ITEM_TYPES、**無 document 鍵**；l186-187 `if args.etype not in MAPPERS: sys.exit`（document 於此硬退出、0 落地）；l213 no_thinker 後援**僅 etype=='work'**；l141-143 work_type→ext None→title+year 去重（dispatch 後才跑）。
- `scripts/embed_knowledge.py`：docstring l7「用戶拍板前不得對 items 側放量嵌入」、l19「預設 scope=works」；`fetch_batch` l111-115 items 側硬套 `corpus.clean_item_sql('i','x',is_super=True)`（第三道 license×entity_type 閘）。
- `scripts/acquire_local_files.py`:39：`--license choices=list(corpus.LICENSE_WHITELIST)`（argparse 第二道閘）；:80-115：直寫 item(entity_type='document' 硬編)+item_text(source_type='local_upload' 硬編)、sha1 dup 檢查、license/access_scope/owner_user_id 由參數帶。
- `scripts/manage_rbac_user.py`:110-115 `--add-domain` 純 INSERT knowledge_domain（不對 item 落地設任何約束）；:145 `--grant-domain` `sys.exit「不在字典」`（僅 grant 時吃字典）；:147 未拍 authz_boundary 擋。`knowledge_item.domain` 實查無 FK/CHECK。
- `src/augur/knowledge/fileparse.py`:17,106：`_TEXT_EXT` 不含 .4gl/.4fd。
- DB 實查 `knowledge_item_text` CHECK：`knowledge_item_text_license_check`(4 值)、`chk_itext_source_type`(NULL or <>'ai_generated')、`chk_itext_access_scope`(public/local_private)。

## 附錄 B：TTAI 來源引用

- ttai DB `buffer` schema 16 表（`\d buffer.<t>` catalog；augur 帳號 SELECT 被拒，數字取自另一有權時點）。
- `ttai/db/schema/001_buffer.sql`:41-93 / `007_detail_tables.sql`:21-225 / `008_column_meta.sql` / `002_export_view.sql`:8-48 / `009_qdrant_export_details.sql`:26-35。
- `ttai/scripts/export_buffer_to_qdrant.py` / `textualize_from_details.py`（semantic_text f-string 確定性組裝）/ `rag_ask.py` / `kb_retrieve.py`。
- `ttai/專案憲章.md`:§2.1 Textualization / §2.3 語意單元 / §2.4 Qdrant / §5.1 多語 + raw data 分界 / 第三章三敵。
- `ttai/reports/`：ERP轉Qdrant通用系統設計_20260624.md / embedding選型PoC_20260624.md / 三層語意緩衝層_整體抽測_20260629.md / ERP架構來源表_盤點_20260623.md（語言碼 0繁1英2簡）。

## 附錄 C：clean-room #16 邊界聲明

ERP 4gl/4fd/程式碼/欄位定義是**資料**，經 pg_dump/GRANT 讀入 augur 知識層當 raw data 合法。TTAI 的 loader/parser/exporter/retriever code（export_buffer_to_qdrant.py、kb_retrieve.py 等）**只可參考設計思想、絕不 copy 進 augur codebase**；augur 端 `acquire_ttai_erp.py` 及旁掛 schema 依 5 治權檔 clean-room 重寫，header 標明「clean-room 重寫、不移植 ttai code」。
