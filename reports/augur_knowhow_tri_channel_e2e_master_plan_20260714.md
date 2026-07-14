# augur know-how e2e 打通 master 計畫書 — 三進料通道 × K 契約七段

- **日期**：2026-07-14
- **性質**：#20 計畫先行（新子系統/介面/架構變更）；產出後待 hugo 拍板才實作
- **範圍**：把 know-how 從**外部窮舉抓入本地 PostgreSQL → 逐字逐句交互理解（定義/意涵/思想相關性/相關係數）→ 寫向量（Qdrant/pgvector）→ 接 qwen → 接 web UI**，一條路真打通；且**三種進料通道皆為 K 七段完整公民**（① 主題抓取 API ② 本機匯入 ③ 遠端 SFTP），並窮舉補齊存量多域 entity（report/book/compound/material/paper）之全文。
- **素材來源**：兩份對抗式深讀 workflow（wgagyaqu7 七段 + wa647e03m 五段，共 12 段 code+DB 實證）+ 23 份 report 目錄計畫書 + 本檔作者 2026-07-14 DB 實查。所有數字皆 (a)stdout/(b)DB query/(c)API 出處（#9/#15）。
- **治權定位**：全屬**素養層**（隔離不變式：零量化、不進預測管線、domain 欄隔離）；全文抓取受**全文准入三軌** license gate；每源啟用（proposed→active）與放量抓取為**決策層人拍板**（AI 不自 approve/放量，#26 碰護欄即停）。

> **一句話版**：管線十段已建九段半；三通道之中「主題抓取」是完整公民、「本機匯入」與「遠端 SFTP」尚非治理公民（source_key=NULL、繞過審批狀態機、無 resume 帳本）；補齊此二通道為公民 + 存量 entity 全文窮舉補抓 + 驅動器統一三通道編排 + 統一治權界閘 = 一條路真打通。

---

## 第一部　現況全景（DB 實證 2026-07-14）

### 1.1 管線規模（psql 實查）

| 表 | 列數 | 說明 |
|---|---:|---|
| knowledge_source | 3,601 | active 69 / approved 3 / proposed 3,528 / suspended 1 |
| knowledge_query | 4,709 | 抓取查詢矩陣 |
| knowledge_staging | 302,650 | promoted 259,609 + rejected 43,041 + pending 0（全 churn 完） |
| knowledge_item | 254,176 | 見 1.2 |
| knowledge_item_text | 151,811 | owned_local 150,685 + cc-by 1,084 + cc-by-sa 33 + public_domain 9 |
| knowledge_sentence | 1,756,817 | 逐句 |
| knowledge_sentence_embedding | 1,696,984 | 單一 model_tag=intfloat/multilingual-e5-small 384d |
| knowledge_lexicon | 154,875 | 定義（dictionary 149,986＋注疏 3,846＋thesaurus 1,043） |
| knowledge_term_affinity | 3,076,918 | philosophy 2,957,154＋items 119,764（相關係數 npmi/jaccard/llr） |
| knowledge_concordance | 52,365,336 | 意涵（出現處 postings） |
| field_knowhow_lexical_affinity | 59,706 | **語意橋**（raw 欄位 ↔ know-how 詞面共現） |
| field_term_map | 5,972 | 欄位→詞映射（覆蓋 746/769 欄位·特徵·表） |

### 1.2 存量 entity_type × 全文覆蓋（本檔作者實查，= 用戶點名對象）

| entity_type | items | 有全文 text | 主要來源 | license 軌（初判） |
|---|---:|---:|---|---|
| document | 141,825 | 141,825（100%） | ERP TipTop（erp_extract） | owned_local（已滿覆蓋） |
| **paper** | 105,665 | **352**（0.3%） | crossref 77,644 / openalex 5,677 / europepmc 3,759 / zenodo 3,736 / hal 3,528 / eric 3,364 / plos 2,685 / arxiv 2,617 / datacite 2,299 / semantic 351 | abstract 補抓（見件 B-0） |
| **book** | 5,915 | **0** | internet_archive 2,626 / openlibrary 3,266 / 策展 23 | 公版掃描→public_domain；餘 metadata |
| **report** | 322 | **0** | osti_energy 322 | 261 未試 / 30 skip_license / 14 no_oa |
| **compound** | 237 | **0** | chembl 236 / pubchem 1 | ChEMBL＝CC-BY-SA |
| **material** | 212 | **0** | cod_crystals 206 / uniprot 3 / gbif 3 | COD＝CC0、UniProt＝CC-BY |

**關鍵事實**：book/report/compound/material **全數 0 全文**（`knowledge_item_text` 一列都沒有、`fulltext_status` 多為 NULL＝從未試抓）；paper 僅 0.3%。它們是「已入庫 metadata、全文從未流過 懂→存→答」的空殼。窮舉補抓的核心對象即此。

### 1.3 K 契約七段落地狀態

| 段 | 狀態 | 實證 |
|---|---|---|
| ①抓 | 已建＋部分執行 | 三層管線活；Wave1 僅煙測（帳本 2,199 組合＝估算 6-8 萬的 3.7%）；#24 quota 引擎僅半套（health/cursor 表 0 列、quota_limit 全 NULL） |
| ②懂 | 已建 | lexicon/concordance/affinity/語意橋全落地；但**投資語料近零**（economics 82 items/business 101 items）→items 相關係數近雜訊（誠實里程碑：豐度待抓段跑完） |
| ③存 | 已建＋cutover 已切 | 1.7M 嵌入；`sentence_items` config=qdrant_server 但**6333 未起**→每查詢先撞 connection-refused 再降級 pgvector；qdrant_sync_state 僅 2 列 |
| ④答 | 已建＋已接線 | chat:8090→advisor:8399→ollama qwen3:8b 全 active；guard 五閘完整；但**檢索內容飢餓**（投資 know-how 問答走 NO_KNOWLEDGE/通識路，R6 未解） |
| ⑤換 | 已建（4 接縫皆資料/env） | embedspec 世代＋vectorstore_config＋qwen env；但**三通道機器本地前置未載入交接文件**（SFTP config/key、ORACLE_*、erp dump-only 性質） |
| ⑥驅 | 部分 | refresh_knowledge_pipeline.py 8 段 DAG＋flock＋心跳＋--reap；但**缺 bridge/stats_items 兩段、無 timer、stage-0 只驅通道①** |
| ⑦界 | 有界誠實 | 審批狀態機 live、三層 fail-closed 閘活；但**只作用於 API/staging 通道，本機/SFTP 繞過**（source_key=NULL、直寫 knowledge_item） |

### 1.4 三進料通道現況

| 通道 | 傳輸/入庫 code | 治理公民？ | DB 落地 | 缺口摘要 |
|---|---|---|---|---|
| **① 主題抓取** | acquire_knowledge.py（14 adapters）+ harvest_knowledge.py + promote_knowledge.py | ✅ 完整 | 254,176 item | Wave1 未放量、#24 引擎半套 |
| **② 本機匯入** | acquire_local_files.py + fileparse.py + webupload.py | ❌ source_key=NULL、繞 staging | **0 列**（`source_type='local_upload'`）；150,685 owned_local 實由**另一條 ERP loader**（erp_extract）落，非此 script | 未註冊 registry、lineage 二分、缺 apk/image/audio 抽取器 |
| **③ 遠端 SFTP** | sftpbrowse.py（paramiko 傳輸層）+ admin console 面板 | ❌ 完全未註冊 | **0 列** | 無 knowledge_source 列、無 adapter、無 sftp_sync_state、無 CLI、無 resume、paramiko 未宣告依賴、憑證不隨換機 |

**核心洞見**：三通道**差別只在「抓」的取得機制**，下游 promote→fulltext→sentences→concordance→stats→embed→vector_export 完全 channel-agnostic——實證：owned_local 150,685 段 100% 已切句、151,849 句已嵌入（一旦落 item_text 即被共用 builder 納入）。**故打通策略＝把「抓」抽象為 per-channel adapter，下游一律共用**。

---

## 第二部　統一架構：通道 × 七段矩陣

```
              ①抓(通道別)         ②懂          ③存        ④答      ⑤換      ⑥驅       ⑦界
主題抓取   API adapter ─┐                                                          
本機匯入   local walk  ─┼─→ promote→fulltext→ 逐字理解 →pgvector→ qwen  ┐         統一
遠端SFTP   sftp pull   ─┘    →sentences→      (定義/意涵/  SSOT  →Qdrant→ +Web │  跨機   單命令   admission
                            concordance→      思想相關性/  serving  UI   │  交接   三通道   _gate
                            stats→stats_items  相關係數)                   │  補強   編排     (source
                            →bridge→embed                                 │         +timer   active/
                            →vector_export       ↑語意橋:欄位↔know-how    │                  license/
                                                                          │                  owned_local/
        (三通道共用下游·channel-agnostic 已實證) ←──────────────────────┘                  非AI)
```

**設計原則**：
1. **抓分通道、下游共用**：新通道＝新 adapter（#29b「新來源協定才寫新 adapter」），通道參數住 `adapter_config` JSONB（不 hardcode）。
2. **單一驅動器**：擴 `refresh_knowledge_pipeline.py`（不另建第二驅動器，#12；退役 backfill 前例）。
3. **統一治權界閘**：抽 `admission_gate` 單一住所，三通道入庫前一律過四件（source active / license 白名單 / owned_local⇒local_private / source_type≠ai_generated）。
4. **可拋棄 serving**：pgvector＝SSOT 真源，Qdrant＝可重建 serving 索引（隨時 DROP 從 PG 重建）。
5. **零 token 執行**：全執行層本地 Python+PostgreSQL+本機 qwen，Claude 只出現在此計畫理解與審查（#28）。

---

## 第三部　分件計畫

> 依 K 七段組織；每件標【拍板點】= 需 hugo 決策層核可者。件序＝建議實作順序（前件不阻後件時可並行）。

### 件 A — 抓：三通道統一為治理公民

#### A1　本機匯入通道成公民（②）
- **問題**：`acquire_local_files.py:97` 寫 `source_key=NULL`、直寫 knowledge_item 繞過 staging；且與 ERP loader（erp_extract）並存＝lineage 二分債。
- **步驟**：
  1. INSERT `knowledge_source` 一列：`source_key='local_files_<域>'`、`adapter='local_files'`、`protocol='local_file'`、`license_regime` 依三軌、`adapter_config={root_dir, default_license, access_scope, domain}`、`approval_status='proposed'`。
  2. 改 `acquire_local_files.py`：加 `--source-key` 參數，把 `source_key` 回填該列（不再 NULL）；統一 `source_type`（收斂 erp_extract/local_upload 命名爭議——建議保留 erp_extract 為 ERP 專屬歷史值、新增 local 走 `local_upload`，兩者皆 registry 有列）。
  3. 補 apk：新 `scripts/decompile_apk_to_owned.py`（jadx `-d` 反組譯 → `--include-package` 自有前綴 allowlist 排第三方版權碼 → 交 acquire_local_files `--license owned_local`）；jadx 為 OS 依賴（#23 前置）；反組譯確定性非 AI（合 #1）；`source_type='apk_decompile'`；零新表。
- **增補（Task #16 深讀補完，件 A1 原三步未涵蓋之子需求）**：
  4. **lineage 收斂需明訂遷移動作**（非僅命名）：真正分歧＝acquire_local_files 走**直插 knowledge_item**（繞 staging）vs ERP loader 走 **staging→promote**；須拍板二擇一——(A) acquire_local_files 改走 staging 對齊 ERP，或 (B) 明訂本機通道正式豁免 staging + 補 admission_gate 補償。（實證：150,685 erp_extract 列 source_key 已是 ttai_erp_pilot、已走 staging；acquire_local_files 自身落 0 列。）
  5. **webupload 三入口連帶修改**（step2 隱含）：admin console `/api/folder`(:873)、`/api/upload`(:903)、`/api/sftp/ingest`(:934) 三處皆 subprocess 呼 acquire_local_files 但**均未帶 `--source-key`**；step2 加參數後三處須同步帶入，否則 UI 路徑仍落 NULL。
  6. **RBAC owner 接線**：`--owner-user-id` 與 owner_user_id 欄位/FK 皆在，但 admin UI 呼叫時從不傳 uid（session＝env 單密碼、未解析 uid）→ local_private「僅本人+super 可檢索」收窄（corpus.clean_item_sql:45-57）形同 owner=NULL；須接 admin session→uid→`--owner-user-id`（與件 H RBAC 綁）。
  7. **懂存答自動閉環**：acquire_local_files 尾行（:122）**只印提示**、不自動接 build_sentences→embed（現況止於 item_text）；件 A2（SFTP）已要求「自動達可檢索終態」，本件須對等補（或由驅動 DAG 節點承接，見件 G）。
  8. **domain 無 CHECK/FK + source_type 無白名單**：`knowledge_item.domain` 自由字串（`--domain` 預設 'local' 無約束）、`chk_itext_source_type` 僅黑名單擋 ai_generated（local_upload/erp_extract/apk_decompile 命名靠程式紀律）；建議件 A1 或件 H 補 domain 收斂/驗證 + source_type 升 DB 白名單 CHECK。
  9. **staging trigger 對 manual_file 直接放行**（治理注意）：`trg_staging_source_gate()` 首行 `IF adapter='manual_file' THEN RETURN NEW`——即使本機改走 staging，只要 adapter=manual_file 就繞過 approval gate；件 H 統一界閘須補此洞（active 人核 gate 對本機/curation 現缺席於機械層）。
- **【拍板點 R-A1】**：image/audio（類 B）之 OCR/ASR 抽取器**不含在本件**——屬 #1 修憲卡點（見件 H-OCR）；本件僅類 A（word/excel/txt/json/code/apk 文字）。

#### A2　遠端 SFTP 通道成公民（③，全新子系統）
- **問題**：sftpbrowse.py 傳輸層存在但（a）非 registry 公民（無 knowledge_source 列/adapter/protocol=sftp）（b）無 resume 帳本（download_tree 每次全樹重抓）（c）無 CLI（僅 admin HTTP）（d）paramiko 未宣告（e）憑證不隨換機。
- **步驟**：
  1. 宣告依賴：`pyproject.toml` 加 `paramiko>=3.0`（remote extra 或併 admin extra）；import smoke（#23）。
  2. **新表 `sftp_sync_state`**（增量帳本，DDL 見第四部）：`UNIQUE(source_key, remote_path)` 供 #6 冪等增量（只下載 remote_mtime/size 變更或新增檔）。
  3. INSERT `knowledge_source` 一列：`adapter='sftp'`、`protocol='sftp'`、`license_regime='owned_local'`、`query_template={host,port,base_path,glob}`（#29b 主機/路徑住 DB）、`approval_status='proposed'`（**憑證絕不寫此列**）。
  4. 憑證入 `.env`（#5+#31 換機覆蓋）：`SFTP_<NAME>_USER` / `SFTP_<NAME>_KEYPATH`（沿用 SSH 金鑰路徑、不存密碼）；adapter 由 `os.environ` 讀，不落 log/DB/git。（替代：保留 `~/.config/augur-sftp.json` 但納入 HANDOFF §3 人工前置清單。）
  5. 增量 module：延展 `sftpbrowse.py` 或新增 sibling（`sftpsync.py`，#18 領域名詞非通用角色名）——headless「list→比對 sftp_sync_state→只抓變更/新增」，resume-safe（#6）。
  6. **新 `scripts/acquire_remote_files.py`** CLI（#29a `import _bootstrap`、#29d 指令矩陣+實測、無參數 graceful）：讀 sftp source 列 + .env 憑證 → 增量 sync → 複用 acquire_local_files 入庫路徑 → 自動接 build_sentences→embed 達可檢索終態（#29b(b) v1.20「harvest 完成＝可答終態」）。
- **【拍板點 R-A2】**：SFTP 拓樸抉擇——**建議 B 案**（傳輸層 CLI + registry provenance 列，複用 acquire_local_files/fileparse，與現況 sftpbrowse 一致、最小改動）；A 案（純 ADAPTERS dict）因「檔案≠JSONB payload」本質不合。

#### A3　主題抓取深化（①）
- **步驟**（皆執行層，但 Wave1 放量與每源 approve 屬拍板）：
  1. #24 對偶引擎補完：`acquire_knowledge.py` 接 quota gate（讀 quota_limit/window、達 90% 停）、health 持久化（knowledge_source_health）、honor Retry-After、cooldown 指數階梯、跨行程 pg_advisory_lock。
  2. 目錄回填：`migrate_source_governance.py` 套用深抓 §1 六軌逐源 pace/quota/wave/license/abstract_policy（現僅 72/3,601 源有值）；quota 值取各源官方 ToS（OpenAlex 100k/day、arXiv 3s、SEC 10rps，可溯源 #10）；`--apply` 前 pg_dump 快照（#30）。
- **【拍板點 R-A3】**：Wave1 投資/經濟域放量 + proposed→active 逐源 TTY 人核（`review_knowledge_source.py`，AI 永不自 approve，憲章 v1.41.0）。

### 件 B — 抓：存量多域 entity 全文窮舉補抓（用戶點名對象）

> 全屬素養層、零量化不進預測管線；每型走各源專屬 fulltext resolver（#29b adapter），license 逐源判、誠實 blocked 旗標。

#### B-★　可行性已實證（#25 最小單位探測 2026-07-14，全五型抓得到）

單一 item 打各源 API 實證，**五型全部證實抓得到**（證據＝(c)API 回應）：

| 型 | 源 | 探測結果 | license | 路由 |
|---|---|---|---|---|
| paper | arxiv | ✅ `<summary>` 全 abstract | arXiv | Atom `<summary>` |
| paper | semantic_scholar | ✅ 439 字 abstract + OA PDF | — | graph/v1/paper/DOI:{doi}?fields=abstract |
| paper | europepmc | ✅ 1863 字 abstractText | — | rest/search?query=DOI |
| paper | plos/hal/eric/inspire | ✅ 皆有 abstract/description | PLOS=CC-BY | 各 REST |
| paper | zenodo/datacite | ✅ description（license **逐筆異**） | 逐筆 | api/records、api/datacite |
| paper | openalex/crossref | ⚠️ 部分 item 閉取/無 abstract | 逐筆 | inverted_index / message.abstract |
| book | internet_archive | ✅ `_djvu.txt` 全文，`copyright=LoC unaware` | ≈public_domain | archive.org/metadata → djvu.txt |
| book | openlibrary | ✅ ocaid 找到，但**借閱版=在版權** | 借閱≠公版→metadata | works→editions→ocaid→IA license 判 |
| report | osti_energy | ✅ links 含 fulltext+citation_doe_pages | OA(DOE PAGES) | osti.gov/api/v1/records?doi |
| compound | chembl | ✅ pref_name+80 別名+mechanism | CC-BY-SA | molecule.json + mechanism.json |
| compound | pubchem | ✅ 145 字 description | — | rest/pug/compound/cid/{cid}/description |
| material | cod | ✅ CIF（化學名+期刊） | CC0 | crystallography.net/cod/{id}.cif |
| material | uniprot | ✅ function 76 字 | CC-BY | rest.uniprot.org/uniprotkb/{acc}.json |
| material | gbif | ⚠️ 此物種 descriptions=0（僅 3 件稀疏） | 次要 | api.gbif.org/species/{key}/descriptions |

**實作洞見（三 ⚠️ 為逐篇覆蓋落差、非路徑失敗）**：
1. **paper abstract 多源 fallback**：crossref/openalex 逐篇覆蓋不全 → 同 DOI 依序轉打 semantic_scholar→europepmc→openalex（S2 對 crossref DOI 覆蓋廣），覆蓋率最大化；`acquire_abstract.py` 須設計為 per-item 多源接力，非單源。
2. **license 逐筆判、不可一律套源**：zenodo/datacite 每筆授權不同（軟體 bsd/mit vs CC vs 未明）→ 逐筆讀 rights 欄，非白名單者 deny 停 metadata；openlibrary 借閱版＝在版權→止 metadata（不抓全文）；IA「LoC unaware of copyright」→public_domain 候選。
3. **gbif 3 件稀疏**次要（descriptions 空→fallback vernacular 或誠實 none）；其餘源全綠。

#### B-0　paper abstract 補抓（105,313 空殼 → 可嵌可答）
- **設計**：新 `scripts/acquire_abstract.py`（鏡射 `fetch_oa_fulltext.py` 骨架）；PENDING_WHERE=`entity_type='paper' AND abstract_policy='allow' AND NOT EXISTS(item_text)`；per source_key 分派；識別子＝`COALESCE(external_id, url 擷取)`（9,353 件 external_id NULL 須從 url 擷取：hal/eric/datacite/europepmc 各異）。
- **多源路由（確定性抽取、零 AI #1；#25 已實證）**：crossref→JATS XML 剝 `<jats:*>`；openalex→`abstract_inverted_index` 依位置重建；arxiv→Atom `<summary>`；europepmc→abstractText HTML 剝標；plos→Solr abstract；semantic_scholar→graph API abstract；hal→abstract_s；eric→description；inspire→abstracts；zenodo/datacite→description（license 逐筆判）。
- **per-item 多源接力（實證洞見）**：crossref/openalex 逐篇覆蓋不全（探測到閉取 item 無 abstract）→ 同 DOI 依序轉打 semantic_scholar→europepmc→openalex，最大化覆蓋；acquire_abstract 須設計為 per-item 多源 fallback（非單源一次過），命中即止、全空記 abstract_none 誠實終態。
- **寫入**：`knowledge_item_text`（`source_type='abstract'`、per-source license∈白名單、`access_scope='public'`、source_url 可溯源）。
- **seq 碰撞解**：abstract 用專屬 `seq=0`，並讓 `fetch_oa_fulltext` 的 PENDING_WHERE 改認「NOT EXISTS 非-abstract item_text」，使 abstract **不封殺**日後 OA 全文。
- **誠實終態**：擴 `knowledge_fulltext_status` CHECK 增 `abstract_none`/`abstract_fetch_error`（migrate DDL，#30 audit 綠後跑），使重跑收斂。
- **投資槓桿**：finance/investment/economics/accounting/business 六域共 12,962 paper 幾乎全靠 abstract 才有內容→直接解件 C 的語料飢荒。
- **【拍板點 R-B0】**：治權裁定「abstract＝metadata（CC0 基礎）」——crossref/openalex/semantic 為 `license_regime='metadata_only'`，須人正式裁定方可對其 `abstract_policy='allow'`（openalex inverted_index、crossref abstract 皆 CC0 為據）；不明者 deny 停 metadata。AI 不自裁（#19/#26）。

#### B-1　book 全文（5,915）
- **路由**：internet_archive（2,626）→ `archive.org/metadata` 逐件版權判定→公版才抓 `_djvu.txt`；openlibrary（3,266）→ editions→ocaid→IA 同路；curation_*（23）＝策展 JSON 種子無 API 源（skip_no_resolver 誠實）。
- **實作狀態**：已寫 `fetch_entity_fulltext.py` res_ia/res_openlibrary，#25 實測——公版件 `pilgrimfromirela00carn` 抓得 168,804 字全文、借閱版正確 skip_license。
- **⚠ 語料現實（#15 實證 2026-07-14）**：IA「book」語料組成＝text-id 疑真書 2,236 + osf-registrations 256 + numeric-id 134；但抽樣顯示 text-id 多為 `*0000*` **IA 借閱館（在版權、受控數位借閱）**→正確 skip_license，**僅少數真公版掃描（「LoC unaware of copyright」）可抓**。故 book 全文 yield 有限（license 現實、非 bug）；借閱版由 fail-closed 逐件擋下（寧缺勿錯抓）。

#### B-2　report 全文（322）
- **路由**：osti_energy → OSTI fulltext/PDF endpoint；261 NULL（未試）重跑；30 skip_license/14 no_oa 留誠實 blocked 旗標（license 阻擋非漏做）。
- **工具**：`fetch_pd_fulltext.py` OSTI 策略 或新 OSTI resolver + PDF 抽取（pdfminer，深抓 P3）。

#### B-3　compound 描述（237）
- **路由**：ChEMBL API 取 molecule description / mechanism_of_action / indication 結構欄位（CC-BY-SA 3.0→`license=cc-by-sa`）；文字短但為化學域素養內容。
- **工具**：新 chembl resolver（讀 external_id=ChEMBL ID → API → 描述欄 → item_text）。

#### B-4　material 描述（212）
- **路由**：COD（206，CC0→public_domain）取 CIF `_publ_section_title`+化學名+結構描述；UniProt（3，CC-BY）取 protein function annotation；GBIF（3，CC-BY）取物種描述。
- **工具**：新 cod/uniprot/gbif resolver（各讀 external_id → API → 描述 → item_text）。
- **誠實註**：compound/material 文字短（結構化欄位、非長全文），yield 有限但為有效多域素養內容；隔離不變式下本就零量化。

#### B-下游（B-0~B-4 共用，無新碼）
`build_sentences.py --scope items`（source_type 無關，自動切句）→ concordance → `build_items_knowhow_stats.py`（items 語料統計）→ `embed_knowledge.py`（03:30 timer）→ 可檢索。
- **【拍板點 R-B】**：各 entity 全文放量授權（外部 API 放量須 #26 授權）+ 各源 license 逐源判定。

### 件 C — 懂：逐字理解閉環（定義/意涵/思想相關性/相關係數）

- **現況**：定義（lexicon 154,875）、意涵（concordance 52M）、相關係數（term_affinity 3.08M，npmi/jaccard/llr 閉式）、語意橋（field_knowhow_lexical_affinity 59,706）皆已建且接進 advisor（`_concept_block`/`_bridge_block`）；no-AI 機械閘（derivation_method.method_kind 四值封閉，embedding/LLM 係數 DB 硬擋）活。
- **打通缺口**：`refresh_knowledge_pipeline.py` 的 STAGES（8 段）**未含 `stats_items` 與 `bridge`**（grep 確認無任何編排器呼叫此二 builder）→ 新語料經抓取落地後，items 相關係數與語意橋**不會自動重建**（靜默陳舊）。
- **步驟**：
  1. STAGES 加兩段（K 計畫 §4 已規）：`stats_items`（build_items_knowhow_stats.py，排 concordance 後）、`bridge`（build_field_knowledge_bridge.py，排 stats_items 後、embed 前）；標頭段名封閉集 8→10。
  2. 補待辦計數（`pending_lines`）：stats_items（item_term_stats 列數）、bridge（field_term_map 覆蓋欄 + lexical_affinity cooc_sents≥30 有效列）。
  3. 語料放量後（依賴件 B）：`build_items_knowhow_stats.py` 補 items llr（Dunning，現只算 npmi/jaccard）。
- **【拍板點 R-C】**：改管線 STAGES 屬編排常數列變更；W1 可先於件 B 掛上（空跑安全、resume-safe）；R2 corpus PK 重建（6.5M 列）屬破壞性 DDL，排 dump 後（#30）。

### 件 D — 存：Qdrant serving 收攏（D6 決策）

- **問題**：`sentence_items` config=qdrant_server 但 6333 未起→每查詢先撞 connection-refused 再降級 pgvector（成本+log 噪）；qdrant_sync_state 僅 2 列（items/en 落後 7 列、zh 147k 未上、works 未上）；且 6333 若貿然起來，`retrieval.py:330` 無條件 return 會讓 local_private 私有中文檢索被餓死（正確性回歸）。
- **【拍板點 R-D6】二擇一**：
  - **(a) Qdrant 作真 serving**：建 `~/.config/systemd/user/augur-qdrant.service`（augur 專屬 storage `~/qdrant_augur`，勿共用 ttai）→`export_qdrant_index.py` 補齊 items/zh(147k)+works(1.46M)→qdrant_sync_state 逐語言追平→`verify_qdrant_shadow.py`（≥0.90）→**先修 retrieval.py:317-334 私有讀路回歸**才 live。
  - **(b) 誠實退 pgvector（推薦短期）**：`UPDATE knowledge_vectorstore_config SET backend='pgvector' WHERE scope='sentence_items'`（一列），消除每查詢 connection-refused 開銷；待語料/GPU 就緒再 cutover（遷移 SSOT 07-07 本裁「481k 甜蜜點不該 cutover」，現總量 1.7M < 5M 硬門檻仍未觸發 Qdrant 優勢）。
- **附**：補 `chk_itext_owned_local_private` 之 ADD CONSTRAINT 遷移（現只活在 live、無遷移＝clean-room 漂移，#12）。

### 件 E — 答：檢索品質（R6）+ 服務硬化

- **現況**：全鏈接線完備（chat→advisor→qwen、guard 五閘、語意橋免責硬綁）；**真正關卡＝know-how 檢索品質**——投資問答目前回離題哲學 chunk / ERP 欄位，經 relevance 閘多判空走通識路。根因＝(1) 投資語料上游近空（件 B 解）(2) e5-small 對財經 CJK 不可靠。
- **步驟**：
  1. R6 檢索命中率量測：建投資域（finance/economics/business items）命中率 eval（擴 verify_knowledge_e2e_smoke.py --with-llm 或新腳本）。
  2. 不達門檻→經 embedspec 世代機制評估換嵌入模型；和/或 advise.py 加 rerank 或「非空但離題→confabulate」拒答門檻。
  3. secret 載入硬化（執行層）：`augur-advisor.service` 加 `EnvironmentFile=%h/project/augur/.env`，使 RBAC secret 不依賴 import 順序副作用（現為脆弱點：靜默轉 deny-all 風險）。
  4. 接答段活體煙測進背景（P3）：sentinel nonce→advisor 逐字引用+fail-closed 反向斷言。
- **【拍板點 R-E/R6】**：rerank/拒答門檻/換嵌入模型判準＝憲章判準變更須人拍板（§26 碰護欄即停）。

### 件 F — 換：三通道換機交接補強（#31）

- **問題**：HANDOFF §3 的 .env 清單**通道命脈不全**（漏 FRASER_API_KEY/SEMANTIC_SCHOLAR_API_KEY/GITHUB_TOKEN/ORACLE_*）；SFTP config/SSH 私鑰未列人工前置；erp_tiptop（150K 最大語料）為 **dump-only、augur 無重抓路徑**（源為外部 Oracle ERP）未載明警語；resume_project.sh 不檢 SFTP config。
- **步驟**（純機械執行層）：
  1. HANDOFF §3 .env 清單改**按通道分組表**，逐鍵標「屬哪通道命脈」。
  2. §3「不在 git 須重建」清單加：`~/.config/augur-sftp.json` + SSH 私鑰（與 .env、dump 同列人工前置）。
  3. §3 DB 段加警語：owned_local erp_tiptop **dump 為唯一換機載具、augur 無重抓路徑**。
  4. resume_project.sh 加非阻塞 SFTP 前置檢查（缺 config 只 warn 不 exit，SFTP 為選配）。
  5.（可選）read_handoff.py 加「三通道換機檢查」小節（主題抓取 key / owned_local 隔離角色 / SFTP config-key 到位）。

### 件 G — 驅：單命令三通道編排 + 排程

- **問題**：驅動器 stage-0「抓」只呼叫一種 acquire（harvest_knowledge.py=通道①，且 `adapter<>'manual_file'` 結構排除本機/SFTP）；無 for-each-channel；無 timer。
- **步驟**：
  1. STAGES harvest 段改「通道迭代 acquire」：驅動器讀 `knowledge_source WHERE approval_status='active'` 之通道集，for-each 呼對應 acquire（API→harvest_knowledge.py；local/sftp→acquire_knowledge.py --source `<key>` 統一 dispatch）；其餘七段共用。
  2. fulltext 段對已自帶全文之通道（local/sftp）顯式 skip（依 adapter 判，取代目前僅靠 NOT EXISTS 巧合）。
  3. resume 帳本統一：local/sftp 於 knowledge_harvest_log 記帳（sentinel query_id），使待辦矩陣看得到三通道進度。
- **【拍板點 R-G/R3】**：建 `~/.config/systemd/user/augur-knowhow-refresh.{service,timer}`（週日 02:00、`--domain finance`、flock 防重疊、僅 active 源、零 token）；systemd timer 掛載＝排程核可。

### 件 H — 界：統一治權閘

- **問題**：本機②/SFTP③ 通道**繞過來源審批狀態機**（source_key=NULL、直寫 knowledge_item、不經 staging）→三層 fail-closed 閘（尤閘三 staging trigger）對其全不觸發；「能抓≠該抓」的來源 active 人拍板 gate **缺席於機械層**（僅靠 admin 誠信宣告 --license）。RBAC uid 未接線（env 單密碼、uid 未由 app_session 解析）。
- **步驟**：
  1. 抽 `admission_gate(source_key, license, access_scope, source_type)` 單一住所（放 augur.knowledge，比照 corpus.clean_item_sql SSOT #12）；三通道入 item/staging 前一律過四件：(i) source approval_status='active'（**本機/SFTP 現漏此件，核心補洞**）(ii) license∈白名單 (iii) owned_local⇒local_private (iv) source_type≠ai_generated。
  2. 界閘註冊審議引擎 oracle 常備斷言（db_query/information_schema/import_isolation，零 token 機械複驗）：如 `owned_local AND access_scope<>local_private => ==0`、`source_type=ai_generated => ==0`、check_isolation→三通道治權不變式。
  3. RBAC uid 接線（承 permission model §5）：admin 登入改查 app_user+寫 app_session、uid 由受驗 session 解析、owner 收窄消費接線。
- **【拍板點 R-H1】**：本機/SFTP 走 staging（方案 A，改寫 knowledge_staging 使三層閘生效）vs 明文入憲豁免（方案 B，比照 manual_file 豁免 harvest，以 license DB CHECK+cli_identity TTY 身分閘為治權）——二擇一須人拍板。
- **【拍板點 R-H-OCR】**：image/audio（類 B）之 OCR/ASR 是否入 item_text＝ #1 修憲卡點（已有 v1/v2 提案，結構張力未解：轉錄≠AI 生成 vs whisper 流利幻覺無自動檢出）；未裁前類 B 維持 `unknown_ext` 誠實跳過。**AI 不得執行層自定「逐字轉錄不算 AI 生成」**（§8.2 判準變更須人拍板）。

---

## 第四部　Table Schema（#20 v1.39.0 要求）

### 4.1 新表 DDL

```sql
-- 件 A2：SFTP 增量同步帳本（resume-safe #6）
CREATE TABLE IF NOT EXISTS sftp_sync_state (
    sync_id       bigserial PRIMARY KEY,
    source_key    varchar   NOT NULL REFERENCES knowledge_source(source_key),
    remote_host   text      NOT NULL,
    remote_path   text      NOT NULL,
    remote_mtime  bigint,                       -- 遠端 mtime（epoch）供增量比對
    size_bytes    bigint,
    content_sha1  char(40),                      -- 內容去重
    item_id       bigint    REFERENCES knowledge_item(item_id),
    first_seen    timestamptz NOT NULL DEFAULT now(),
    last_synced   timestamptz NOT NULL DEFAULT now(),
    UNIQUE(source_key, remote_path)              -- #6 冪等增量鍵
);
```

### 4.2 既有表補遷移（收斂漂移 / 誠實終態）

```sql
-- 件 D 附：補 owned_local 硬綁 CHECK 之遷移（現只活 live、無遷移＝clean-room 漂移 #12）
ALTER TABLE knowledge_item_text
  ADD CONSTRAINT chk_itext_owned_local_private
  CHECK (license <> 'owned_local' OR access_scope = 'local_private');  -- 冪等：IF NOT EXISTS 包裝

-- 件 B-0 附：abstract 誠實終態標籤（擴 CHECK；#30 audit 綠後、避 dump 窗）
ALTER TABLE knowledge_fulltext_status DROP CONSTRAINT <現有 status CHECK>;
ALTER TABLE knowledge_fulltext_status ADD CONSTRAINT <status CHECK>
  CHECK (status IN (<現 6 skip_*>, 'abstract_none', 'abstract_fetch_error', 'abstract_ok'));
```

### 4.3 既有表 schema（所讀/所寫，供對照）

- **knowledge_source**（抓）：source_key, adapter, protocol, query_template JSONB, adapter_config JSONB, approval_status, license_regime, pace_seconds, quota_limit, quota_window_seconds, abstract_policy, wave, fulltext_eligible …
- **knowledge_staging**（抓）：staging_id, source_key, domain, entity_type, payload JSONB, source_url, fetched_at, status, promoted_at, query_id
- **knowledge_item**（抓）：item_id, domain, entity_type, title, title_zh, year, authors, external_id, venue, url, taxonomy_id, source_key, staging_id, ingested_at
- **knowledge_item_text**（抓/懂）：itext_id, item_id, seq, content, language, source_url, license, fetched_at, source_type, access_scope, owner_user_id（CHECK: license 5 值白名單、source_type≠ai_generated、owned_local⇒local_private）
- **knowledge_fulltext_status**（抓）：item_id, status, reason, source_url, checked_at
- **knowledge_sentence**（懂/存）：sent_id, text_id, itext_id, seq, sentence, language, char_start, char_end
- **knowledge_sentence_embedding**（存）：model_tag, pgvector 384d
- **knowledge_vectorstore_config**（存/換）：scope, backend, endpoint, embed_model, dims（cutover＝UPDATE 一列）
- **field_term_map / field_knowhow_lexical_affinity / knowledge_term_affinity**（懂·語意橋/相關係數）：method_key FK→derivation_method（kind CHECK 四值封閉）

---

## 第五部　Python 程式規畫（#20 v1.39.0 要求）

### 5.1 新增 script

| 檔 | 角色 | 關鍵簽名/職責 | 輸入→輸出表 | 狀態 |
|---|---|---|---|---|
| `scripts/acquire_abstract.py` | 件 B-0·abstract 補抓 | `main()`；11 源 resolver + DOI fallback 接力；`rebuild_inverted(idx)` 確定性重建；fail-closed by abstract_policy/abstract_license | knowledge_source/knowledge_item(讀) → knowledge_item_text(seq=0) + fulltext_status | **✅ 已寫+驗證**（graceful+fail-closed 0 待抓待 R-B0） |
| `scripts/fetch_entity_fulltext.py` | 件 B-1~B-4 | RESOLVERS registry(8 源)：book(IA 逐件公版判定)/report(OSTI)/compound(ChEMBL/pubchem)/material(COD/UniProt/GBIF)；`--dry-run`；fail-closed by license_regime/fulltext_license | knowledge_item(讀) → knowledge_item_text + fulltext_status | **✅ 已寫+#25 實測**（IA 公版 168k 字、借閱版 skip、chembl fail-closed） |
| `scripts/acquire_remote_files.py` | 件 A2·SFTP 通道 CLI | `main()` 讀 sftp source 列+.env 憑證→sftpsync 增量→fileparse→入庫→接下游 | knowledge_source(讀) + sftp_sync_state(讀寫) → knowledge_item/item_text | 待寫（件 A2） |
| `scripts/decompile_apk_to_owned.py` | 件 A1·apk | 薄 wrapper：jadx→allowlist→acquire_local_files | apk 檔 → knowledge_item_text(apk_decompile) | 待寫（件 A1） |

### 5.2 改動既有 script/module

| 檔 | 改動 | 守則 |
|---|---|---|
| `src/augur/knowledge/sftpsync.py`（新 module，#18 領域名詞） | headless 增量 list→比對 sftp_sync_state→下載變更 | #6 resume-safe |
| `scripts/acquire_local_files.py` | 加 `--source-key`/`--source-type`；source_key 不再 NULL；收斂 lineage | #29b provenance |
| `scripts/acquire_knowledge.py` | 加 quota/health/Retry-After/cooldown/advisory lock（#24 引擎）；（B 案 SFTP 不入 ADAPTERS） | #24 對偶 |
| `scripts/refresh_knowledge_pipeline.py` | STAGES 加 stats_items/bridge/abstract 三段；harvest 段改通道迭代；fulltext 段 per-channel skip | #12 單一驅動器 |
| `src/augur/knowledge/admission.py`（新 module） | `admission_gate(source_key,license,access_scope,source_type)` 四件閘單一住所 | #12 SSOT / 件 H |
| `scripts/migrate_source_governance.py` | 六軌目錄回填 UPDATE（pace/quota/wave/license/abstract_policy） | #10 可溯源 |
| `build_items_knowhow_stats.py` | 語料放量後補 items llr（Dunning） | 件 C |
| `pyproject.toml` | 加 paramiko>=3.0 | #23 |

### 5.3 消費/驗證

- `verify_knowledge_e2e_smoke.py`：擴為**三通道各一 sentinel**（API nonce 源列 / 本機 nonce 檔 / SFTP nonce 檔 → 單命令驅動器 → advisor 逐字引用 + fail-closed 私有不外洩 + 隔離斷言零列進 term_affinity）。
- `deliberate.py`（審議引擎）：件 H 界閘斷言常備（零 token 機械複驗）。
- `report_knowledge_coverage.py --snapshot`：全鏈末落 knowledge_coverage_snapshot 供窮舉進度趨勢。

---

## 第六部　分階段 + 拍板點

| 階段 | 內容 | 依賴 | 拍板點 |
|---|---|---|---|
| **P0** 執行層先行（零風險、可先做） | 件 C-W1（STAGES 加 bridge/stats_items 空跑掛上）、件 F（HANDOFF 交接補強）、件 D-附（chk CHECK 遷移）、件 A3-1（#24 引擎補完 code） | — | 無（改正確/補完整） |
| **P1** 三通道公民化 | 件 A1（本機成公民）、件 A2（SFTP 全套：DDL+registry+CLI+paramiko+憑證） | P0 | R-A1 / R-A2 |
| **P2** 存量全文窮舉 | 件 B-0（abstract）、B-1~B-4（book/report/compound/material） | P1 | R-B0 / R-B |
| **P3** 統一治權界閘 | 件 H（admission_gate、審議斷言、本機/SFTP staging 抉擇） | P1 | R-H1 / R-H-OCR |
| **P4** 驅動器統一 + 排程 | 件 G（通道迭代、timer）、件 A3-2（Wave1 放量） | P1-P3 | R-G/R3 / R-A3 |
| **P5** 存/答收攏 | 件 D（Qdrant D6）、件 E（R6 檢索品質、secret 硬化） | P2（語料到位） | R-D6 / R-E |
| **P6** 語料放量後補強 | 件 C-W3（items llr）、覆蓋率快照趨勢 | P2/P4 | — |

**端到端單命令（打通後）**：
```
nohup venv/bin/python scripts/refresh_knowledge_pipeline.py --domain finance \
  > logs/refresh_finance.log 2>&1 &
# 十二段：harvest(三通道迭代)→promote→fulltext→abstract→sentences→concordance
#         →stats→stats_items→bridge→embed→vector_export→(coverage snapshot)
```

---

## 第七部　治權約束總表（三通道共用，不可逾）

| 約束 | 內容 | 機械強制點 |
|---|---|---|
| **全文准入三軌** | public_domain / cc_whitelist(cc-by/cc-by-sa/cc0) / owned_local；版權未明止於 metadata+fulltext_blocked | item_text license CHECK 5 值 + chk_itext_owned_local_private |
| **#1 禁 AI 生成入庫** | 逐字入庫、禁摘要改寫；abstract/inverted 重建/剝標=確定性非 AI；OCR/ASR 未裁=卡點 | chk_itext_source_type≠ai_generated；derivation_method kind 四值封閉 |
| **隔離不變式** | 素養層零量化、不進預測管線、domain 欄隔離；量化回流唯 school→principle→factor_map→#14 | import_isolation AST + BRIDGE_LITERALS 字面掃描；test_philosophy_isolation |
| **能抓≠該抓** | 新源/新域決策層人拍板；approve/activate 唯人 TTY，AI 永不自執行 | approval_status='active' fail-closed 閘（三層）；curation.HUMAN_ONLY+cli_identity |
| **#5 密鑰治理** | SFTP 私鑰/ORACLE_*/API key 住 .env 或 ~/.config 0600，不入 git/DB | 憑證絕不寫 knowledge_source 列；審議 file_grep _SECRET_DENY |
| **owned_local 永不離本機** | advisor llm_fn/embedspec 必本機推理，禁外部 LLM（citations 可能含私有） | ollama.py host allowlist（v1.37.0） |
| **#28 零 Claude token** | 全執行層本地 Python+PG+本機 qwen；Claude 只在理解與審查 | — |
| **#31 換機本地優先** | 三通道交接走既有五支本地工具擴充，憑證人工前置 | resume_project.sh / HANDOFF |
| **#6/#30 資料安全** | resume-safe 冪等；破壞性 DDL 排 dump 後避鎖風暴 | pg_dump 快照 + audit 綠後 DDL |

---

## 第八部　驗收準則

1. **三通道各一 sentinel 端到端綠**：API nonce 源列 / 本機 nonce 檔 / SFTP nonce 檔 → 單命令驅動器跑至嵌入 → advisor 逐字引用命中 + fail-closed（owned_local 不被無授權檢索）+ 隔離斷言（素養層零列進 term_affinity）→ exit 0。
2. **存量 entity 全文覆蓋提升**：book/report/compound/material 之 knowledge_item_text 由 0 轉有值（license 允許者）；paper abstract ≥ 已 allow 源之候選數；每型誠實 blocked 帳可解釋（license 阻擋非漏做）。
3. **通道治理對等**：本機/SFTP 皆有 knowledge_source 列（source_key≠NULL）、經 admission_gate 四件、審議引擎斷言零違反。
4. **驅動器單命令可驅三通道**：`refresh_knowledge_pipeline.py` 十二段涵蓋三通道 active 源，DB-driven resume，零 token。
5. **換機可復現**：新機 resume_project.sh 檢出三通道命脈（.env 分組、SFTP config、owned_local dump-only 警語）。
6. **治權零違反**：`deliberate.py --run` 界閘斷言全 PASS（owned_local⇒local_private==0 違反、ai_generated==0、隔離不變式）。

---

## 附：拍板點總覽（hugo 決策層）

| # | 拍板點 | 建議 |
|---|---|---|
| R-A1 | 類 B（image/audio）本件排除、僅類 A | 同意（類 B 走 R-H-OCR 修憲） |
| R-A2 | SFTP 拓樸 A/B | **B 案**（傳輸層 CLI+registry provenance） |
| R-A3 | Wave1 放量 + 逐源 approve | 依 IP 健康、TTY 人核 |
| R-B0 | abstract=metadata（CC0）治權裁定 | 待裁（openalex/crossref CC0 為據） |
| R-B | 各 entity 全文放量 + license 逐源判 | 待裁 |
| R-C | STAGES 改（+bridge/stats_items）；R2 PK 重建 | W1 可先掛（空跑安全） |
| R-D6 | Qdrant 起 server vs 退 pgvector | **短期退 pgvector**（<5M 未觸發優勢） |
| R-E/R6 | rerank/拒答門檻/換嵌入模型 | 待 R6 命中率量測後裁 |
| R-G/R3 | systemd timer 排程掛載 | 待裁 |
| R-H1 | 本機/SFTP 走 staging vs 明文豁免 | 待裁（A 案閘更嚴、B 案改動小） |
| R-H-OCR | 類 B OCR/ASR 修憲（轉錄≠AI 生成？） | **結構張力未解**（v1/v2 均被對抗駁回，見該二報告） |

---

*本計畫書依 #20 計畫先行產出；執行前確認①完整②內部一致③與 code 一致④可實作。所有放量抓取、code 改動、DDL、治權判準變更皆待 hugo 拍板；AI 碰護欄即停（#26）。*
