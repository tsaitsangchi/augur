# 知識層全文缺口收尾 Master 計畫（plan-first #20；待 hugo 拍板）

**日期**：2026-07-13 ｜ **性質**：執行層擴充（不動治權判準；全文准入三軌 gate 原樣沿用、隔離不變式不動）
**目的**：把三份既有子計畫（fulltext resolvers 本機落地／PDF extraction／K 殘餘之全文相關段）串成**一條有依賴、有順序、有護欄**的收尾路線，供一次拍板。
**基準**：本機 07-12 dump 實證（下表數字皆 live DB 查得）＋子計畫書 `knowledge_fulltext_source_resolvers_plan_20260712.md`、`knowledge_pdf_extraction_plan_20260712.md`、`augur_knowhow_e2e_upgrade_plan_20260712.md`。

---

## §0 範圍界定（先誠實劃界，否則計畫會誇大）

「全文缺口」＝已 harvest 進 `knowledge_item`（有 metadata）但全文未落 `knowledge_item_text` 且無終態帳的 item。**本機 live 總積壓 >10 萬件**，但按來源形狀分三類，**本 master 只收其中兩類、~3,656 件**：

| 類 | 來源 | 積壓（本機實證）| 解法 | 是否本 master 範圍 |
|---|---|---|---|---|
| **OA 學術源** | crossref 63,989／openalex 3,341／europepmc 3,489／hal 3,528／zenodo/eric/plos/arxiv… | **>90,000** | 既有 `fetch_oa_fulltext.py`（Unpaywall OA 路徑）；大宗落 `skip_no_oa`（無 OA 全文＝license 現實）| ❌ **不在**（既有管線、非缺口，是誠實終態）|
| **text/html 專屬源** | internet_archive **2,619**／sec_edgar／fraser | ~2,620 | **resolvers 計畫**（djvu.txt／EDGAR 組裝／FRASER textUrl）| ✅ 件 1 |
| **PDF-only** | oapen_books＋`skip_pdf` **976**＋IA 404 fallback | ~1,037 | **PDF 計畫**（pypdf＋五道品質閘）| ✅ 件 2 |
| **本地自有多格式**（類 A）| word/excel/txt/json/程式碼/自有 apk 反組譯碼 | 依你的檔量 | **acquire_local_files.py + fileparse**（已建，多格式現成）| ✅ 件 3（2026-07-13 hugo 定）|

> **收尾語意精確化**：件 1/2 讓「resolvers＋PDF 可及的 ~3,656 件」全歸終態；OA 學術源的巨量積壓是**另一條既有管線的常態**，非本計畫債；件 3 是**本地自有檔新入庫**（非補既有 item 的全文，是另一入口 `acquire_local_files.py`）。**不得**宣稱「本計畫收尾全部全文積壓」。
>
> **件 3 範圍鐵律（治權，不因格式鬆動）**：類 A＝**確定性可抽逐字文字**之格式（`fileparse` 非 AI、逐字無摘要，合 #1）；一律過 **license 三軌**（自有走 `owned_local`＋硬綁 `access_scope='local_private'`，DB CHECK `chk_itext_owned_local_private`）。**明確排除**：image/audio（類 B，另議、需向量新世代拍板）、AI 轉文字（OCR/ASR/caption＝違 #1）、第三方版權碼（apk 內非自有 package）。

**第三件「K 殘餘」的定位（誠實降級）**：K 計畫主體九段半已建（語意橋 `field_knowhow_lexical_affinity` 59,706 已在）；其殘餘中與全文相關的是**深抓 S2-S4**（investment/economics 域內容近零、抓**新來源**）——**這是「上游供給」（會產生更多待抓全文的 item），不是「已有 item 的全文缺口」**，屬 `augur_knowledge_deep_harvest_plan_20260710` 的執行、另軸。本 master **不納為執行項**，僅在 §2 依賴圖標其上游關係。Qdrant works collection 上 live server＝下游 serving，亦不在本收尾範圍。

---

## §1 三件的依賴關係圖

```
【上游·另計畫】深抓 S2-S4(deep_harvest)──產生更多 item──┐
                                                          ↓
【前置·零風險】件0 config 落地(adapter_config.fulltext 三源 UPDATE)
                                                          ↓
        ┌──────────────┬──────────────┐
   件1 resolvers(text/html)      件2 PDF extraction(PDF)
   IA/EDGAR/FRASER               OAPEN + skip_pdf 976
   ▲已驗證(原機),本機缺資料       ▲P0未拍板+需CHECK DDL
        └──────────────┴──────────────┘
                          ↓ 共用同一支 fetch_pd_fulltext.py dispatcher
                    knowledge_item_text(逐字零 AI #1)  ←──┐
                                                          │ 另一入口(獨立)
   件3 類A本地自有多格式 ── acquire_local_files.py + fileparse ┘
   word/excel/txt/json/程式碼(▲已驗證可即做) + 自有apk(jadx反組譯)
   owned_local 硬綁 local_private;第三方 package 排除
                          ↓ build_sentences
                    knowledge_sentence
                          ↓ embed(03:30 timer,已建)
                    knowledge_sentence_embedding(pgvector SSOT)
                          ↓ 單向同步【下游·另段】
                    Qdrant serving 索引 → advisor 檢索作答
```

**三個硬依賴**（決定順序）：
1. **件0 前置於件1/件2**：本機 `adapter_config.fulltext` 四源**全 NULL**（實證）→ dispatcher 讀不到策略＝空轉；config 不落，件1/件2 都跑不動。
2. **件1 與件2 共用 `fetch_pd_fulltext.py`**：件2 是在件1 的 dispatcher 上**增 `pdf_extract` 內容模式**（PDF 計畫 §2）→ 件1 的 dispatcher 骨架應先穩定。
3. **件2 前置於自身 P1**：件2 需 `fulltext_status` CHECK 擴列 DDL（破壞性 schema 變更）→ 須 hugo P0 拍板＋audit 綠後跑（#30）。

---

## §2 執行順序（階段化，附前置條件）

| 序 | 階段 | 動作 | 前置 | 護欄 |
|---|---|---|---|---|
| **0** | **config 落地**（零風險） | 三源 `adapter_config.fulltext` UPDATE（§3 件0 SQL）| 無 | #29b 純資料、零 API、可逆 |
| **1a** | **resolvers 本機資料落地——路徑抉擇**（決策層）| A 搬 20260713 dump 重匯入／B 本機重跑 IA 放量／C 等原機 dump | 件0 完成 | 見 §4 三路徑權衡；B 涉 IA 放量（#24/#26 授權）|
| **1b** | resolvers 端到端驗證 | 每源最小 3 件（fetch→item_text→句→embed）| 1a | 逐字 sha 級、誠實終態 |
| **2** | **PDF P0 拍板** | hugo 核 PDF 計畫（含 CHECK DDL＋pypdf）| — | 動 DDL＝決策層 |
| **3** | PDF P1：`pdf_text.py`＋五閘＋單測＋CHECK DDL | P0＋**audit 綠**（DDL #30）| 四型負向樣本全被閘擋 |
| **4** | PDF P2/P3：OAPEN 61＋skip_pdf 976 分批 | P1＋OAPEN item 存在（本機現 0，待深抓或 dump）| OCR 不啟動、品質閘 fail-closed、200/批 |
| **3a** | **件3 word/excel/txt/json/程式碼**：`acquire_local_files.py --license owned_local` | 無（**零開發、可即做**）| owned_local 硬綁 local_private、確定性抽取 |
| **3b** | **件3 apk**：裝 jadx（OS 依賴）→反組譯→過濾自有 package→acquire | jadx 安裝＋你指定自有 package | 第三方 package 排除、確定性反組譯 |

> **關鍵時序**：件0 與**件3a 皆可立即做**（不阻塞任何在跑的東西、走 owned_local 現成管線）；件1 路徑抉擇待你定；件2 全鏈與件3b 的 jadx **不搶 audit 鎖**（件2 CHECK DDL 須 audit 綠後 #30；件3 全程無 DDL）。**與開賽鏈零衝突**（不碰預測層、不碰 FinMind）。件3 獨立於件0-2（不同入口 `acquire_local_files.py`）。

---

## §3 對應 schema 與程式規畫（v1.39.0 雙落實）

### 件0：config 落地（零新表、零新 code，純資料 UPDATE）
**讀寫表**：`knowledge_source.adapter_config`（JSONB）。**落地 SQL**（三源，計畫書 §1 原樣）：
```sql
UPDATE knowledge_source SET adapter_config = adapter_config || '{"fulltext":{"strategy":"url_template","template":"https://archive.org/download/{external_id}/{external_id}_djvu.txt","content":"text"}}'::jsonb WHERE source_key='internet_archive';
UPDATE knowledge_source SET adapter_config = adapter_config || '{"fulltext":{"strategy":"edgar_archive","content":"html_strip"}}'::jsonb WHERE source_key='sec_edgar_fulltext';
UPDATE knowledge_source SET adapter_config = adapter_config || '{"fulltext":{"strategy":"fraser_api","content":"text","auth":"auth_header"}}'::jsonb WHERE source_key='fraser_stlouisfed';
```
**驗收**：`SELECT adapter_config->'fulltext' FROM knowledge_source WHERE source_key IN(...)` 三列非 NULL。

### 件1：resolvers（零新表、code 已在本機）
**讀**：`knowledge_item(item_id, source_key, external_id, url)`＋`knowledge_source(adapter_config, pace_seconds, license_regime, approval_status)`＋`knowledge_staging(payload)`（EDGAR cik/adsh 回查）。
**寫**：`knowledge_item_text(item_id, seq, content, language, source_url, license, access_scope, source_type)`（既有欄；source_type∈{pd_fetch, edgar_archive, fraser_api}）＋`knowledge_fulltext_status`（skip_* 終態）。
**程式**：`scripts/fetch_pd_fulltext.py`（**已在本機**，三策略 dispatcher `resolve_fulltext_url` 已實作）——本機**無需改 code**，只缺件0 的 config。
**函式**（現況）：`resolve_fulltext_url(item, acfg) -> (url, content_mode)|None`；`--run --limit --source` 矩陣。

### 件3：本地自有多格式 owned_local 落地（類 A；**基礎已建，補 apk＋副檔名**）
**現況實證（2026-07-13 live）**：`scripts/acquire_local_files.py`（資料夾遞迴入庫入口，三軌 license＋owned_local 硬綁 local_private）＋ `src/augur/knowledge/fileparse.py`（`extract_text(path)->(text,reason)` 通用抽取器）**已建並實跑**——ERP 已入 `owned_local/erp_extract` **150,685 段**（先例）。`fileparse._TEXT_EXT` 已含 txt/md/csv/log/json/xml＋程式碼 `.py/.js/.ts/.java/.c/.cpp/.h/.go/.rs/.sh/.sql/.r`；專屬 reader 已含 `.pdf/.docx/.pptx/.xlsx/.epub`；依賴（python-docx/openpyxl/chardet…）已在 pyproject `admin` extra。

**∴ word/excel/txt/json/程式碼＝零開發，現在就能入**：
```bash
python scripts/acquire_local_files.py --dir <自有目錄> --license owned_local --owner-user-id <id>   # 強制 local_private
```

**真正的新增（3 小項，皆最小邊界 #3）**：
1. **apk 反組譯前處理**（唯一實質新增）：apk＝zip＋Dalvik bytecode，須先確定性反組譯成程式碼文字。工具＝**jadx**（apk→java 原始碼，Java-based **OS 依賴**、非 pip、#23 前置）。流程＝`jadx -d <out> app.apk` →（過濾自有 package）→ `acquire_local_files.py --dir <out/自有package> --license owned_local`。反組譯器**確定性非 AI**（合 #1）。可薄封裝 `scripts/decompile_apk_to_owned.py`（jadx wrapper＋package allowlist＋呼叫 acquire），或純文件化流程。
2. **第三方 package 排除**（法律護欄）：apk 含第三方 SDK（Firebase/廣告 SDK…非你版權）。jadx 按 package 分目錄→`--dir` 只指自有 package，或 wrapper 加 `--include-package <你的域名前綴>` allowlist；**非自有 package 不入**（過不了 owned_local「自有」前提）。
3. **補副檔名**（若缺）：檢 `fileparse._TEXT_EXT` 是否含 `.kt`(Kotlin)/`.swift`/`.smali`/`.4gl`/`.4fd`（ERP 已入→可能已支援）；缺者＝**UPDATE 一個集合、零架構**。

**Schema**：**零新表零 DDL**——全走既有 `knowledge_item_text`（`source_type='local_file'` 或 `apk_decompile` 區分、可溯源 #10）；owned_local DB CHECK 已在。
**程式**：word/excel/txt/json/程式碼＝**0 開發**；apk＝1 薄 wrapper（可選）＋`fileparse._TEXT_EXT` 補集合。

### 件2：PDF extraction（1 新表變更 DDL＋1 新模組＋1 修改）
**Schema 變更（破壞性、需 audit 綠後）**：
```sql
-- migrate_fulltext_status_ddl.py 擴 CHECK(冪等:先 DROP 再 ADD)
ALTER TABLE knowledge_fulltext_status DROP CONSTRAINT knowledge_fulltext_status_status_check;
ALTER TABLE knowledge_fulltext_status ADD CONSTRAINT knowledge_fulltext_status_status_check
  CHECK (status IN ('skip_no_oa','skip_license','skip_pdf','skip_ctype','skip_short','skip_fetch_error','skip_pdf_no_textlayer','skip_pdf_quality'));
```
（現值 6 標籤已實證，新增 2；`skip_pdf` 語意由「PDF 未抽」收斂為「尚未嘗試」→ 抽取後歸終態。）
**寫**：`knowledge_item_text`（`source_type='pdf_extract'`，與 pd_fetch/OA 區隔、可溯源 #10）。
**程式（1 新增＋1 修改）**：
- **新** `src/augur/knowledge/pdf_text.py`（領域名詞 #18）：`extract(pdf_bytes) -> (text, metrics) | QualityFail`——pypdf 抽取＋五道機械閘（text_ratio≥300字/頁、mojibake<0.5%、dehyphen、boilerplate_strip、len≥2000）全在此、可單測。
- **修** `scripts/fetch_pd_fulltext.py`：dispatcher 增 `pdf_extract` 模式（下載 PDF→`pdf_text.extract`→閘過才 INSERT）。
**依賴**：`pypdf`——**已在** `pyproject.toml` `admin` extra（`pypdf>=4.0`，實證），P1 不需另裝、#23 smoke 併驗。

---

## §4 件1 本機資料落地——三路徑權衡（決策層，需你拍板）

本機 code 在、config 缺（件0 補）、**491 件 resolvers 成果在原機、本機無**（v4 major finding 實證）。三路徑：

| 路徑 | 做法 | 優 | 劣 | 建議 |
|---|---|---|---|---|
| **A 搬 20260713 dump 重匯入** | 取含成果的 dump、`import_database.sh --force` | 零 API 放量、與原機一致 | dump 不在本機（搬 6.6GB）；**破壞性覆蓋今日 audit 增量**（須重跑）| 若原機成果權威且今日 audit 可棄 |
| **B 本機重跑 IA 放量** | 件0＋`fetch_pd_fulltext.py --run` 抓 IA 2,619 件 | 保留今日工作、本機自主、驗證 code 真能跑 | IA API 放量（13 批、授權＋200/批熔斷＋resume-safe）| ✅ 若本機為主力（今日工作皆在此）|
| **C 等原機下次 dump** | — | 零成本 | 前提「原機仍主力」——但本機現為唯一在用機、前提不成立 | ✗ |

**推薦 B**（本機主力＋DB 跨機獨立＋順帶驗證解析器 code）；除非你要拿原機一致成果且 20260713 dump 可搬。

---

## §5 統一護欄（三件共同，逐條可機驗）

1. **全文准入三軌 gate 原樣**：public_domain／cc_whitelist／owned_local 才抓全文；非授權止於 metadata＋誠實旗標（憲章全文准入三軌，不動）。
2. **逐字零 AI（#1）**：resolvers＝原文直取；PDF＝**確定性抽取（pypdf 非 LLM）＋品質閘 fail-closed**（閘不過＝維持 skip、不入半壞內容）；抽取驗收＝抽查比對原件（#15）。
3. **誠實終態非漏做**：所有無法抓者落 `fulltext_status` skip_* 帳；`skip=`被擋非漏做。
4. **OCR 不啟動**：掃描件（無文字層）＝`skip_pdf_no_textlayer`，P8 裁定不動。
5. **隔離不變式不動**：素養層零量化價值進預測管線；量化回流唯 `school→principle→factor_map→#14` 一條合法路。
6. **API 放量護欄（#24/#26）**：IA/OAPEN 放量需你授權；**非 FinMind（不撞 audit）**但仍外部放量；200/批＋403/429>30 熔斷＋resume-safe＋harness 可見任務登記（#21）。
7. **DDL 時序（#30）**：件2 的 CHECK 擴列**須 audit 綠後**跑（不與對帳搶鎖）。
8. **token 經濟**：件0-2 執行**全本地零 Claude token**；Claude 只出現在本計畫書（已花）。
9. **與開賽鏈零衝突**：不碰預測資料層、不碰 FinMind；可與開賽鏈並行（除件2 DDL 讓行 audit）。
10. **件3 owned_local 三防**：① 自有前提（apk 排除第三方 package、image/audio 非本計畫）② 確定性抽取（fileparse/jadx 非 AI，逐字合 #1）③ 硬綁 `local_private`（DB CHECK `chk_itext_owned_local_private`，永不公開、擁有者收窄）——**owned_local「非拿來繞他人版權」**（acquire_local_files.py 標頭原文）。

---

## §6 驗收矩陣

| 件 | 驗收（可機驗）|
|---|---|
| 0 | 三源 `adapter_config.fulltext` 非 NULL；`fetch_pd_fulltext.py` 無參數列出可抓積壓 |
| 1 | 每源 ≥1 件 `knowledge_item_text` 落地（FRASER 若判 blocked 則旗標）；IA 2,619 全歸終態（fetched/skip_* 有帳）；sha 級逐字 |
| 2 | pytest：四型負向 PDF 樣本全被閘擋；OAPEN 抽出文抽查 3 段 vs 原 PDF 逐字一致；`skip_pdf` 殘量→0（全轉 fetched/no_textlayer/quality）|
| 3a | word/excel/txt/json/程式碼各 ≥1 檔入 `owned_local`、`access_scope='local_private'`（DB 驗）；抽出文抽查 vs 原檔逐字一致 |
| 3b | apk：jadx 反組譯→自有 package 入庫、第三方 package 零入（package allowlist 驗）；smali/java 逐字 |
| 全 | coverage snapshot 前後對比；隔離不變式 `check_isolation()` 0 violations 不變；owned_local 內容零進預測管線 |

---

## §7 拍板點（一次決策）

- **D1** ✅ 已定（2026-07-13 hugo）：範圍＝resolvers＋PDF＋**類 A 多格式**（不含 OA 學術源/深抓/Qdrant；image/audio/AI轉文字排除）
- **D2** 件0 config 落地：**現在做**（零風險）還是綁整體？
- **D3** 件1 路徑：A／**B（建議）**／C？
- **D4** 件2 PDF 計畫 P0：核准（含 CHECK DDL＋pypdf）還是暫緩？
- **D5** OAPEN item 本機為 0（實證）——件2 P2/P3 需先有 OAPEN item（待深抓或 dump），是否納入前置？
- **D6** 件3a（word/excel/txt/json/程式碼）**零開發可即做**——你把自有檔放某目錄、指定 owner-user-id，我就能入庫；要現在做嗎？
- **D7** 件3b（apk）：確認 ① 是你**自有** app（非他人）② 允許裝 jad（OS 依賴外部工具）③ 你的自有 package 名（allowlist 前綴，排除第三方）？

**執行前確認**（#20/§26）：拍板後動工前，我會再核 ①config SQL 對本機 adapter_config 結構 ②`fetch_pd_fulltext.py` 現況簽名與計畫一致 ③audit 綠狀態（件2 DDL 前置），有落差先修計畫。
