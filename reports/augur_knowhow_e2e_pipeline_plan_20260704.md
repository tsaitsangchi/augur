# augur know-how 端到端管線總綱計畫（七段一驅）v1.0

**檔案**：`reports/augur_knowhow_e2e_pipeline_plan_20260704.md`（憲章第六部 SSOT；30 分鐘可讀）
**性質**：三架構師骨架（A 一條通／B 可替換抽象／C 誠實對話倒推）× 對抗審查 30 條 verdicts 之合成終稿；化學域=首跑實例、非硬編碼對象。每段標【既有】／【缺件】；每個數字出處=§1 實測定錨（未另註者皆出自該表）。
**治權從屬**：憲章 v1.23.0 philosophy 層「知識域端到端管線（七段一驅）」準則（本計畫 §12 附文）+共同不變式①-④；CLAUDE.md #28（usage 經濟）/#29（script 四件事）。

---

## 0. 目標誠實定位

- 用戶目標語「**具備全能全知的我**」=引述之**漸近北極星**（計畫敘述得引用戶目標）；系統一切宣稱一律 **coverage／漸近形**——forbidden_pat（truth|omniscien|全知|真理）掃描維持 0，字面禁入 schema／表名／欄名／code／DB 註解（命門 2）。
- 「逐字逐句交互對應理解（定義／意涵／思想之相關性與相關係數）」的**合法承載全集**：
  - **逐字**=item_text／sentence／concordance 原文（S3）；
  - **定義**=公版辭書 lexicon（S3，`build_lexicon` 既有）；
  - **相關性／相關係數**=統計層 `counting／closed_form_stat／string_rule／sql_join` 四值封閉集（S4，`method_key NOT NULL` FK+CHECK=DB 硬擋）。
  - **embedding 相似度與 LLM 判斷永不以「理解」入庫**（紅線①）；嵌入=索引非內容（紅線③）；ANN distance 永不寫入任何 knowledge_* 表（四值 CHECK 無合法 kind 可載）。
- AI 詮釋唯一時點=回答時刻、不落庫；對話記錄留 harness／檔案層（命門 1/5，紅線⑨）。
- 誠實雙向：編造與假不知道**同罪**（命門 9）——本計畫 guard 域條款（拍板 P8）正是為杜絕「知識域系統性假不知道」而設，非鬆閘。
- **排序公理**：逐字鏈完整性 > 理解載體窮盡 > 索引擴張（資料側入庫順序）。對話骨架（S7）先行**不違**此公理——骨架先行=零資料宣稱：語料為 0 時空檢索→固定誠實句（`advise.py:31-35` 既有機械行為）本身即 R0 級可驗收誠實；先立閘、再灌知識、每灌一段升一 R 級（採 C 案主張，資料側順序從 A/B）。

## 1. 實測定錨（單一出處節，#15）

| # | 數字／事實 | 值 | 出處 |
|---|---|---|---|
| 1 | 化學 taxonomy 節點 | 128（field 3/subfield 13/topic 112） | DB 唯讀實查 2026-07-04 |
| 2 | 化學 query | 119 全 enabled | DB 實查 |
| 3 | 化學 source | 7 列 5 enabled（materials_project／nist_webbook 停用） | DB 實查 |
| 4 | 化學 staging | 3,160=crossref 2,903 pending+dbpedia 250 promoted+compound/material 7 pending | DB 實查 |
| 5 | knowledge_item 總量／化學 | 25,031／**0** | DB 實查 |
| 6 | knowledge_item_text | **0 列**（8 欄：itext_id/item_id/seq/content/language/source_url/license/fetched_at，無 sha1 欄） | `\d` 實查 |
| 7 | sentence | zh 33,319／en 1,505,700 | DB 實查 |
| 8 | sentence_embedding | 33,314（全 zh，model_tag='intfloat/multilingual-e5-small'；**en 0 未嵌**） | DB 實查 |
| 9 | lexicon／lexicon_embedding | 154,875／154,875 | DB 實查 |
| 10 | 統計層 | term_stats 2.76M／affinity 2.96M／cooc 6.5M | DB 實查 |
| 11 | 群統計有界預算 | domain 12→pair 66 全量；taxonomy 4,798→pair ~1.15e7 觸 10⁷ 界 | DB 實查+算式 |
| 12 | 第二域現成量 | chemical_engineering staging 323（query 13 enabled） | DB 實查 |
| 13 | GPU 嵌入速率 | 842 句/s（e5-small 384） | embed_knowledge 實測（資產盤點） |
| 14 | pymilvus／Milvus Lite | 3.0.0／dim=384 開檔煙測過（`~/milvus_eval/eval.db`） | `venv` 實測 |
| 15 | Open WebUI | v0.10.2；`OPENAI_API_BASE_URLS` 分號多端點（config.py:331-337）；`ENABLE_OPENAI_API` default True（:309）；title/tags/follow-up 生成 default True（:2220-2224） | 本地安裝原始碼實查 |
| 16 | Ollama | qwen3:8b Q4_K_M 8.2B ctx 40960 於 :11434；GPU=GTX 1650 4GB（Q4 權重約 5GB>4GB→必部分 CPU offload） | /api/tags 實查+規格 |
| 17 | 雙 venv | `venv`=torch 2.12.1+cu126+pymilvus（主環境）；`.venv` 無 torch/pymilvus | pip 實查 |
| 18 | 既有 code 行號群 | `promote_knowledge.py:125,127,131-165,173-175`；`build_sentences.py:89-92,200,216`；`build_concordance.py:18,49-51,91,160-163`；`embed_knowledge.py:25,32-34,63-67,72-76,110-114,126`；`advise.py:13,26,31-35`；`guard.py:12,15,19,23,34-35,51,60`；`retrieval.py:18,39,47,75,124`；`fetch_oa_fulltext.py:36-37,40-43`；`acquire_knowledge.py:227-250,264-267`；`harvest_knowledge.py:350-356`；`backfill_knowhow_pipeline.py:41（check=False）`；CLAUDE.md #29 四件事（:60-66） | 逐行實查（資產盤點+對抗審查+本合成複核） |

## 2. 七段架構圖（七段一驅）

```
 外部 know-how                本地 PostgreSQL（真兆 SSOT）                    serving／對話（可拋棄・可替換）
┌─────────────┐ S1 ┌─────────┐ S2 ┌────────┐ S3 ┌──────────────────────────┐
│ registry 三表│──→│ staging │──→│  item  │──→│ item_text → sentence      │
│ ×13 adapter │    │(lineage)│    │(domain/│    │ → concordance / lexicon  │
└─────────────┘    └─────────┘    │tax 落欄)│    │  （逐字鏈+定義,零 AI）     │
                                  └────────┘    └────────┬─────────────────┘
                                                 S4 ↓            S5 ↓
                                        ┌───────────────┐  ┌────────────┐ S6 ┌─────────────┐
                                        │ 統計理解層     │  │ pgvector   │───→│ Milvus      │
                                        │（四值 method,  │  │ SSOT 索引  │單向│ 可拋棄索引   │
                                        │ 群統計 domain/ │  │ +HNSW      │匯出│ id+distance │
                                        │ taxonomy）     │  └────────────┘    └──────┬──────┘
                                        └───────────────┘                           │
        S7 對話層：query→textnorm→exact SQL→確定性擴展→ANN(id+distance)→PG JOIN 取原文
           →verify_verbatim→advise(llm_fn=Ollama qwen3)→guard 單閘→OpenAI 相容殼→Open WebUI

 驅動器 refresh_knowledge_pipeline.py：S1→S2→S3→S4→S5→S6（批次段 DAG）；S7=常駐 serving 不入 DAG
```

段=契約邊界：各段獨立可跑（#29a）亦可被驅動器串（硬要求②）；DB=段間匯流排；每段冪等可重放。

## 3. 每段=既有工具+缺件清單

### S1 來源窮舉與取得（registry→staging）——【既有 100%，缺件 0 code】
- 沿用：`knowledge_source/query/taxonomy` registry（定錨 #1-3）；`acquire_knowledge.py`（13 adapter；PubChem/ChEMBL 走 `adapter_generic_json` :227-250，registry `adapter_config` 定義=零 code）；`harvest_knowledge.py`（harvest_log PK(query_id,source_key) resume+per-source 限速矩陣+連 5 錯熔斷+429/503 不 attempts++）。
- 營運項（非 code）：materials_project API key／nist_webbook 處置=拍板 P13。
- 契約不變式：lineage 四鏈（item→staging→query→taxonomy→source）；external_id 優先序明文；#25 首輪 `--batch 10` 最小驗證才放量。

### S2 晉升落地（staging→item）——【既有 100%，缺件 0 code，只差執行】
- 沿用：`promote_knowledge.py`（`ITEM_TYPES` 已含 compound/material :125、`EXTID_PRIORITY` 已含 chembl_id/cid :127、`promote_item` :131-165；**真實旗標僅 `--entity-type/--domain/--source/--dry-run`（argparse :173-175）——C 案 `--batch` 為捏造旗標，本稿否決**）。
- 契約：external_id 去重優先序；無則 title+year partial unique；`item.domain`+`taxonomy_id` 必落欄（=S4 分組 JOIN 之根）。

### S3 逐字文本鏈（item→item_text→sentence→concordance/lexicon）——【既有 code-ready；缺件=閘+蓋章】
- 沿用：**`scripts/fetch_oa_fulltext.py` 已存在**（DOI→Unpaywall→license 四值白名單 DB CHECK（LICENSE_MAP :40-43；公版+cc-by/cc-by-sa/cc0，NC/ND/未明停 metadata）→規則剝標零 AI→8000 字/seq 寫 item_text→NOT EXISTS 冪等→0.5s 步調+連 5 錯熔斷 :36-37；`--domain/--limit`；需 `UNPAYWALL_EMAIL`）。**對抗審查裁定：B/C 新建 `acquire_item_fulltext.py`=knowledge_item_text 第二寫端、違 #12，否決；缺的是執行非 code**。`build_sentences.py --scope items`（:89-92 itext_id 側+NOT EXISTS resume）；`build_concordance.py --scope items --language en --run`（:49-51,:160-163）；`build_lexicon`（既有）。
- 缺件：**M3** `fetch_oa_fulltext.py` 加 `src_text_sha1` 世代蓋章（item_text 現 8 欄無 sha1 欄→**schema 變更=拍板 P5**，DDL 併單一 migrate 住所）；**N1** `corpus.py` CLEAN+CLEAN_ITEM 對偶述詞（fail-closed、NULL 不放行；entity_type 准入=拍板 P4）；textnorm 化學樣本契約測例（IUPAC 命名／化學式 vs Porter/jieba **實證列驗收、非假設**）。
- 契約：命門 1（零 AI 入庫）；雙軌准入 DB CHECK；textnorm 三方契約（禁 inline 複本）；verify_verbatim 定位基準涵蓋 item_text `substring(FROM char_start+1)` 他證；誠實註記：crossref works 多無 OA 全文→首跑分子預期小，coverage 錶照實記、不虛灌。

### S4 統計理解層（domain/taxonomy 群延伸）——【既有骨架；缺件=延伸非新支】
- 沿用：`build_cross_school_stats.py`（phase 制+`--run/--smoke/--limit` 游標；method_key 憲欄四值 CHECK=DB 硬擋）。
- 缺件（**M4**）：① group_kind CHECK 擴 `('school','thinker','domain','taxonomy')`（**封閉集變更=拍板 P1**）；② `knowledge_domain` 維度表發 int id+收編 domain_map 為域啟用單一 SSOT（拍板 P2）；③ item 側分母鏈三選一（**拍板 P3，建議平行表 `knowledge_item_term_stats` PK(term,language,item_id)；禁擴/放寬既有 `philosophy_work` FK**）；④ method_key 種子 `agg_domain_rollup`/`agg_taxonomy_rollup`（kind=sql_join、definition 逐字載明群定義與 rollup 限同 level/closure——合法擴列、零判準變更）；⑤ DDL 全部併 `migrate_text_understanding_ddl.py` 單一住所（IF NOT EXISTS；新表先印全文過目）。
- 契約：有界物化判準（domain pair 66 全量；taxonomy ~1.15e7 觸界→top-K 或限同 level、rank 落欄）；fail-closed 建好等鏈（item_text 少量時分子誠實=實數）；閘參數=操作值印 log 不鑄 schema（#27）。

### S5 嵌入（pgvector=真兆同庫 SSOT 索引）——【既有引擎；**「零改 code」宣稱撤回**，缺件=M1 四改】
對抗審查三案共病裁定：`embed_knowledge.py` 現行 fetch_batch 述詞 `(s.text_id IS NULL OR w.review_flag=false)`（:63-67）對 item 側句=**無閘 fail-open**；游標單 scope 依 sent_id 序走全表（:110-114）=化學 item 句被 1.5M 工作側 en 債綁死；`MODEL_TAG` 寫死常數（:25）+PK=sent_id 單欄（:32-34）+`ON CONFLICT DO NOTHING`（:126）=換模重嵌**靜默零寫入假成功**。故 **M1（修改 embed_knowledge.py）為硬前置**：
- (a) **CLEAN_ITEM 閘**：述詞改 side-aware——works 側沿用 `w.review_flag=false`；items 側 JOIN item_text/item 過 `corpus.CLEAN_ITEM`（fail-closed：license∈白名單 AND entity_type∈P4 准入集；NULL 不放行）；三端契約（builder/embed/retrieval）強制 import 同一 SSOT。
- (b) **scope 分側**：游標 scope 細分 `embed_sentence_{side}_{lang}`（works/items）——items 側先行、**不吞 1.5M 工作側 en 債**（該債另排=拍板 P7）；**禁手撥游標**（毀機器等式）；每 scope 獨立成立「嵌入數+排除數=來源數」。
- (c) **embedspec 接入**：MODEL_TAG/dim 由 `embedspec.py`（N2）供給+新增 `--model` 旗標（預設現行 e5-small；現行 argparse :72-76 無此旗標——**M1 落地前 SOP 不得使用**）。
- (d) **換模 schema 前置（拍板 P6）**：PK 遷移 `(sent_id, model_tag)` 複合鍵（lexicon_embedding 同型）、ON CONFLICT 鍵同步；**異維模型=新表世代**（`vector(384)` 欄寫死，embedspec 命名）；排除帳落庫非 stdout（既定契約）。
- 契約：分語/分域先於放量（順序硬約束——嵌後再分=數 GB 重灌不可逆）；放量前首千列實測四件套封包{embed 時數/heap GB/HNSW GB/index build 分}+RAM 算式印出。

### S6 serving 索引（pgvector→Milvus 單向匯出）——【缺件=N3+N4 新支】
- 沿用：pymilvus 3.0.0+Milvus Lite（定錨 #14）；stats schema 報告末節 Milvus 銜接契約逐條繼承。
- 缺件：**N3** `src/augur/knowledge/vectorindex.py`（**library 層**——對抗審查裁定：介面住 scripts=殼須 import CLI 或寫複本、違 #12/#18；介面封閉集=`ensure_collection(spec)`/`upsert(rows)`/`delete(pg_pks)`/`search(vec,k,filters)→[(pg_pk,distance)]`/`stats()`；Lite/Standalone/他牌=adapter 實作）；**N4** `scripts/export_milvus_index.py`（薄 CLI 用 N3）。
- 契約：collection 名=**`embedspec.collection_name(layer, side, model_tag, textnorm_ver)`**——真實 model_tag 'intfloat/multilingual-e5-small' 含 '/' 為 Milvus 非法字元且超長→**縮寫映射函數單一住所=embedspec（N2），禁文件/SOP 手寫縮寫**（治 A 案 `e5s_tn1` 命名歧義）；payload=pg_pk+{domain,entity_type,taxonomy_id,language} 窄 scalar（PG JOIN 匯出；domain 重校只刷 payload 不重算向量）；partition key=language；游標記 build_meta（scope=`mv_{collection}` ≤32 字）與資料同 tx；upsert by pg_pk 冪等；**對帳=雙向 anti-join**（治三案共病「殭屍向量」）：missing（PG 有 Milvus 無）→upsert、orphan（Milvus 有 PG 無，如 item_text 重抓後舊 sent_id）→**同 run 刪除傳播**；結束斷言 synced==source 差=0、差值 append coverage_metric；**全量重建觸發判準（機器）**：embedspec 世代變更（model_tag/textnorm_ver）或 orphan 比例>閾值（操作值印 log，#27）→DROP 從 PG 全量重建；統計表任何欄不餵向量；digest 未拍板禁建；不為 Milvus 新增任何 PG 表。

### S7 對話層（advisor 管線+OpenAI 殼+WebUI）——【既有管線；缺件=N5-N8+M2】
- 沿用：advisor 四件（payload/prompt/advise/guard，E5 已升級：空檢索直誠實句/verify_verbatim 前置/locator 強制）；`retrieval.py`；Ollama qwen3:8b；WebUI Connections 機制（定錨 #15，零改 WebUI code）。
- 缺件：
  - **N5** `src/augur/advisor/ollama.py`（llm_fn 實作：Ollama HTTP；model 名=config 操作值不寫死；**qwen3 `<think>` 段機械剝除**後才過閘且不呈現——治 guard 假陽性源，剝除規則入 P8 閘鏈定義）。
  - **N6** **KnowledgePayload 對偶**（frozen；`.numbers()`=本回合真兆 SQL 結果集白名單）+**guard 域條款（拍板 P8=憲章級）**：② 數字白名單雙源=payload.numbers() ∪ 本回合真兆 SQL 結果集，且**已過 ① 逐字驗證之引文段內數字豁免 ②**（引文=文獻原文非系統宣稱，如 114.32 g/mol）；③ _FUTURE_LEAK 對已驗逐字引文段豁免（科學文本 "pressure will rise" 非投資建議）；④ 逆向閘於無 picks 之知識 payload 自然 no-op——治三案共病「guard 域錯配→系統性假不知道」（命門 9）。
  - **N7** item 側 retrieve_fn：**擴充既有 `retrieval.py` 為雙側**（非另立平行模組——避免行為等價複本）；讀路徑鐵則=query→textnorm 全形集→(a)exact SQL 零向量優先→(b)確定性 query 擴展（affinity top-K npmi）→(c)`vectorindex.search` 回 **id+distance 而已**→一律回 PG JOIN 取內容→verify_verbatim（item_text substring 他證）。
  - **M2** `advise.py` 一行級機械收斂：**注入之 retrieve_fn 結果一律後驗 verify_verbatim**（現僅 default 路徑套 :26——治「注入繞過 verify」洞）。
  - **N8** `src/augur/advisor/oai_compat.py`+`scripts/serve_advisor_openai.py`：`/v1/models`+`/v1/chat/completions`；**殼=薄 adapter，唯一出口=呼叫 `advise()`**（對抗審查裁定：A 案殼內固定管線=第二編排器、漏空檢索誠實句分支，否決）；**guard fail=回固定誠實句閉集**（非 LLM 原輸出；閉集變更=拍板 P9 憲章級）；**偽 SSE**：先回 role/keepalive chunk、全文過閘後分塊 emit（stream:true 預設 × guard 全文後置閘之唯一合規形）+ 逾時揭露（qwen3:8b 於 4GB GTX 1650 必部分 CPU offload、單回合可達分鐘級，定錨 #16；驗收先 curl 後 WebUI；不堪用時 llm_fn 一行切更小 model=可替換性紅利）；coverage 尾註=**閘後機械模板**（零 LLM 內容、值出自 DB SQL∈雙源白名單、與 LLM 文本分隔線區隔，定義入 P8 閘鏈=非旁路，治 C 案閘後注入疑義）；API key 收任意值（本地）；殼住 advisor package=**自動入既有 AST 隔離稽核**（拍板 P14）；殼對全部表唯讀零寫（命門 5/6）。
- WebUI 接線（拍板 P10）：唯一 model=advisor 殼；**不配置任何 Ollama 直連**（紅線④已定「直連=繞閘」——可拍的是停法非是否停，治 A「或改名隔離」降格與 C「與否」重開）；**title/tags/follow-up 三項生成停用**（default True :2220-2224→否則 meta-prompt 打殼、guard 產「知識庫中無此內容」標題+弱 GPU 負載倍增）。

## 4. 新增與修改 code 封閉集（全表；此外無其他）

| # | 件 | 落點 | 段 |
|---|---|---|---|
| N1 | `corpus.py` CLEAN+CLEAN_ITEM 述詞（W1 既定+對偶） | `src/augur/knowledge/` | S3/S5/S7 三端 |
| N2 | `embedspec.py`（model_tag/dim/textnorm_ver/collection 縮寫命名函數 SSOT；收編 retrieval.py:18 硬編 MODEL） | `src/augur/knowledge/` | S5/S6/S7 |
| N3 | `vectorindex.py`（五方法介面+Lite adapter） | `src/augur/knowledge/` | S6/S7 |
| N4 | `export_milvus_index.py`（薄 CLI） | `scripts/` | S6 |
| N5 | `ollama.py`（llm_fn adapter+`<think>` 剝除） | `src/augur/advisor/` | S7 |
| N6 | KnowledgePayload 對偶+guard 域條款（P8 拍板後） | `src/augur/advisor/` | S7 |
| N7 | retrieval.py 擴雙側（item 檢索+verify_verbatim item_text 基準） | 既有檔擴充 | S7 |
| N8 | `oai_compat.py`+`serve_advisor_openai.py`（殼） | advisor package+scripts | S7 |
| N9 | `refresh_knowledge_pipeline.py`（唯一驅動器，見 §7） | `scripts/` | 驅動 |
| M1 | embed_knowledge.py 四改（CLEAN 閘/scope 分側/embedspec+--model/複合鍵） | 既有檔 | S5 |
| M2 | advise.py 注入後驗 verify_verbatim 收斂 | 既有檔 | S7 |
| M3 | fetch_oa_fulltext.py 加 src_text_sha1 蓋章（P5 後） | 既有檔 | S3 |
| M4 | build_cross_school_stats.py groupstats 延伸（P1-P3 後） | 既有檔 | S4 |
| M5 | DDL 併 `migrate_text_understanding_ddl.py` 單一住所 | 既有檔 | S3-S5 |
| R1 | **退役** `backfill_knowhow_pipeline.py`（收編進 N9；其 :41 `check=False` 假驗收反例終結） | 刪除/封存 | 驅動 |

全部 scripts 新支守 CLAUDE #29 四件事（§7 詳）；新 module=領域名詞、CLI=動作動詞片語（#18）。

## 5. 化學域首跑 SOP（逐指令；全程本地背景；旗標=實查既存者，M 件新旗標明標）

```bash
# 環境（雙 venv 陷阱：.venv 無 torch/pymilvus；一律 venv）
cd /home/hugo/project/augur && source venv/bin/activate

# ── [1] S2 promote（既有；真實旗標僅 --domain/--entity-type/--source/--dry-run）
python scripts/promote_knowledge.py --domain chemistry --entity-type compound --dry-run   # 最小單位=7 列 #25
python scripts/promote_knowledge.py --domain chemistry --entity-type compound
python scripts/promote_knowledge.py --domain chemistry --dry-run                          # 全量預覽（crossref 2,903）
python scripts/promote_knowledge.py --domain chemistry
# 驗收: SELECT count(*) FROM knowledge_item WHERE domain='chemistry';  -- 0→實數;lineage 四鏈抽查 3 列

# ── [2] S1 補量 harvest（可選;#25 首輪最小）
python scripts/harvest_knowledge.py --domain chemistry --batch 10 --dry-run
nohup python scripts/harvest_knowledge.py --domain chemistry --batch 10 > /tmp/claude-1000/.../hv_chem.log 2>&1 &
# 首輪過才 --rounds 3 --max-minutes 120 放量;完跑回 [1] 再 promote。一次啟動一次通知,不輪詢(#28)

# ── [3] S3 全文落地（既有 fetch_oa_fulltext.py;M3 sha1 於 P5 後補,不阻首跑）
UNPAYWALL_EMAIL=$EMAIL python scripts/fetch_oa_fulltext.py --domain chemistry --limit 3    # 最小探測 #25
nohup env UNPAYWALL_EMAIL=$EMAIL python scripts/fetch_oa_fulltext.py --domain chemistry > /tmp/.../ft_chem.log 2>&1 &
# 驗收: item_text>0;license 100%∈四值白名單(0 NULL);skip 記數帳對上;items_with_fulltext coverage 首筆(分子照實)

# ── [4] S3 句子/concordance（既有 --scope items）
python scripts/build_sentences.py --scope items
python scripts/build_concordance.py --scope items --language en --run
# 驗收: itext 句>0;連跑兩次計數不變(冪等);textnorm 化學測例(IUPAC/化學式)固定測例過

# ── [5] S4 統計（前置:拍板 P1-P4 過+M4/M5 落地+DDL 印全文過目）
python scripts/migrate_text_understanding_ddl.py
python scripts/build_cross_school_stats.py --phase groupstats --smoke --run
python scripts/build_cross_school_stats.py --phase groupstats --run --limit N   # 游標放量
# 驗收: 衍生列 method_key 100% NOT NULL 四值;domain pair≤66;taxonomy 有界(top-K rank 落欄)

# ── [6] S5 嵌入（前置:M1 全落+P6/P7 拍板;items 側 scope 先行,不吞 1.5M en 債）
python scripts/embed_knowledge.py --layer sentence --language en --scope items --limit 1000 --smoke   # (--scope/--model=M1 新旗標)
# → 首千列印四件套封包{embed 時數/heap GB/HNSW GB/index build 分}+RAM 算式 → 過目才放量
nohup python scripts/embed_knowledge.py --layer sentence --language en --scope items > /tmp/.../emb_items.log 2>&1 &
python scripts/embed_knowledge.py --layer sentence --language en --scope items --build-index
# 驗收: 該 scope 嵌入數+排除數(落庫)=來源數;CLEAN_ITEM 隔離測例(非法 license item 之句 0 入嵌=fail-closed 實證)

# ── [7] S6 Milvus 匯出（N3/N4;collection 名由 embedspec 函數產生,不手寫縮寫）
python scripts/export_milvus_index.py --layer sentence --side items --language en --dry-run
nohup python scripts/export_milvus_index.py --layer sentence --side items --language en > /tmp/.../mv.log 2>&1 &
# 驗收: 雙向 anti-join 差=0(missing=orphan=0);差值已 append coverage_metric;DROP→全量重建演練一次(可拋棄性實證)

# ── [8] S7 殼+WebUI（N5-N8+M2;P8/P9/P10/P14 拍板後）
nohup python scripts/serve_advisor_openai.py --port 8091 > /tmp/.../adv.log 2>&1 &
curl -s http://localhost:8091/v1/models    # 回 ["augur-advisor"]
# WebUI Admin Settings→Connections: 僅加 http://localhost:8091/v1;不配置 Ollama 直連;停用 title/tags/follow-up 生成(P10)

# ── [9] 對話驗收（先 curl 免逾時,後 WebUI;R0/R1 雙向）
curl -s -X POST http://localhost:8091/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"augur-advisor","messages":[{"role":"user","content":"<庫內已知化學句提問>"}]}'   # 須逐字引+locator+guard pass
curl -s ... -d '{...“<庫外虛構化合物提問>"}'                                                     # 須固定誠實句、不經 LLM

# ── [10] 之後全鏈一鍵（N9）
python scripts/refresh_knowledge_pipeline.py                       # 無參數=印各段待辦計數矩陣(純 SQL,#29a)
python scripts/refresh_knowledge_pipeline.py --domain chemistry --dry-run
nohup python scripts/refresh_knowledge_pipeline.py --domain chemistry > /tmp/.../pipe_chem.log 2>&1 &
```

止點紀律：每步驗收 SQL 過才進下步；背景跑=nohup+log+完成單次通知；撞限額錯誤即停不 retry（#24/#28）。

## 6. 可替換性設計（六軸接縫；判準=換元件只動接縫+SOP，其他段 git diff=0）

| 軸 | 抽象載體 | 替換動作 | 不動的段 |
|---|---|---|---|
| 域 | registry 三表+knowledge_domain 維度表（P2） | 決策層 INSERT 列，零 code（#29b） | 全管線 |
| 內文通道 | `knowledge_source.adapter_config` 子鍵（P5 形制）；license 雙軌 DB CHECK | 改 registry config | S3 下游全部 |
| 嵌入模型 | `embedspec.py`（N2）：model_tag/dim/縮寫命名 SSOT；model_tag 落欄 | 改 embedspec→SOP-A | 取數/逐字鏈/guard/LLM/UI |
| 向量 serving 庫 | `vectorindex.py`（N3）五方法介面；pgvector=SSOT 永在 | 換 adapter→SOP-B | pgvector 及以上全部 |
| LLM | `llm_fn`（advise.py:13 既有）+config（base_url/model tag） | 改設定一行→SOP-C | payload/prompt/guard/檢索/嵌入 |
| UI | OpenAI 相容協定（殼=穩定契約） | 換任何 OpenAI client | 殼以下全部 |

**SOP-A 換嵌入模型**（含 silent-failure 防呆——治「重嵌=靜默零寫入假成功」）：① 改 embedspec（新 model_tag/dim；異維=新表世代）② 重嵌 `--model <new_tag>`（複合鍵下新 tag 新列、舊列不覆蓋，雙 tag 可 A/B）③ **斷言：新 tag 列數>0 且=該 scope 來源數，0 列=exit≠0 fail**（機器防呆）④ 建新 HNSW ⑤ 新 collection（embedspec 命名含新 tag）匯出+對帳 ⑥ retrieval 經 embedspec 切讀新 tag ⑦ 驗收過後 DROP 舊 tag 列+舊 collection（破壞性=先確認 #6）。
**SOP-B 換向量庫**：① vectorindex 新 adapter ② 棄舊 collection ③ 從 PG 全量重建（可拋棄性=設計保證）④ 對帳差=0。
**SOP-C 換 LLM**：① 改 config 一行 ② guard 固定測例全綠（閘與模型正交之證明）、code diff=0。
**SOP-D 新域**：① INSERT source/query/taxonomy/domain 列 ② adapter_config 填妥 ③ 驅動器 `--domain X` 直跑；**驗收用現成真第二域 chemical_engineering（staging 323）dry-run 演練、code diff=0**——B 案「INSERT 假域列」=治權 registry 摻假資料，否決。
**SOP-E 換 textnorm/jieba 版**：統計表全值域重建+新 collection（textnorm_ver 入名）；三方契約回歸測例先過。

## 7. 串接驅動器設計（一支 refresh 驅動全鏈；CLAUDE #29 四件事逐條落地）

**`scripts/refresh_knowledge_pipeline.py`**（N9；唯一驅動器）：
- **(29a) 個別可執行**：`import _bootstrap`；**無參數=印各段待辦計數矩陣**（staging pending/item 無 text/句未切/未嵌/Milvus 差…全 DB-driven 純 SQL、零副作用、零 Claude 判斷）；不裸 traceback。
- **(29b) 資料驅動不 hardcode**：待辦量全出自 DB；`--domain` 參數化，新域零改驅動器；**段序 registry=code 內常數表、非 DB 表**（避免「先建籠後補憲」——C 案 stage registry DB 表疑義，否決；驅動器自身無狀態=殺掉重跑冪等）。
- **(29c) 通用可重用**：單一驅動器收編三名分（拍板 P11）——顯式 DAG=`S1 harvest→S2 promote→S3 fulltext→sentences→concordance→S4 stats→S5 embed→S6 milvus_export`（**含 S1**——C 案漏 harvest 段，補正；S7=常駐 serving 不入批次 DAG）；**退役 `backfill_knowhow_pipeline.py`**（既存全鏈驅動器，:41 check=False=假驗收反例——治三案共病「雙驅動器違 #12」）；**承接** text 計畫規劃中 `refresh_text_understanding.py`（scripts/ 實查未落地）之 DAG 名分。
- **(29d) 指令矩陣+實測**：標頭執行指令矩陣；每節點=subprocess 呼叫既有 CLI 且 **`check=True`**；段間機器等式 gate 不過即停、印段名+log 路徑 exit≠0。
- 介面：`--domain/--stage/--from-stage/--until/--limit/--dry-run`；**只編排不計算**（零統計/嵌入邏輯內嵌，單一住所在各 builder）；resume 全 DB-driven（harvest_log/NOT EXISTS/build_meta 游標）；scoped 重建與游標重置同 tx（在各 builder 內）；游標 resume 僅限 append-only 上游；src_text_sha1 失配=錯得大聲。
- 背景規約：nohup+log 落檔+完成單次通知；不輪詢、不自掛喚醒鏈（#28）。
- **端到端煙測（硬要求②實證）**：單一指令走「取 1 item→text→句→嵌→Milvus→curl 殼得 guard-pass 回應」（#25 最小單位）。

## 8. 拍板點（決策層；執行前逐一過目；附建議）

| # | 拍板項 | 建議 |
|---|---|---|
| P1 | group_kind CHECK 擴 `('domain','taxonomy')`（封閉集變更） | 准 |
| P2 | `knowledge_domain` 維度表發 int id+收編 domain_map 為域啟用單一 SSOT；taxonomy 群用 tax_id（a+b 並行；rollup 限同 level/closure、method definition 逐字載明） | 准 a+b |
| P3 | item 側 term_stats 分母鏈三選一 | 平行表 `knowledge_item_term_stats`；禁擴/放寬既有 FK |
| P4 | CLEAN_ITEM 述詞+entity_type 語意層准入 | paper/report=literary 對偶先行；compound/material/dataset 首期不入語意層（metadata 檢索可） |
| P5 | item_text 加 `src_text_sha1` 欄（DDL 單一住所）+fetch 通道擴充 | sha1 准；通道首期僅 Unpaywall，PMC OA/arXiv 另案 |
| P6 | 嵌入換模 schema 前置：PK `(sent_id,model_tag)` 複合鍵（lexicon 同型）+異維=新表世代+`--model` 旗標 | 准（否則硬要求③=假成功） |
| P7 | 分側 scope 游標+en 1.5M 工作側債排程 | items 側先行；1.5M 債四件套實測後另排；禁手撥游標 |
| P8 | **guard 知識域條款（憲章級）**：KnowledgePayload 對偶+數字白名單雙源+①過驗引文段豁免②③+`<think>` 機械剝除+coverage 機械尾註定義 | 按 §3-S7 形准；閘規則變更永不執行層自改 |
| P9 | 三級誠實固定句閉集 | 沿用「知識庫中無此內容」不擴；若需擴=憲章判準變更 |
| P10 | WebUI 接線形制 | 唯一 model=殼；零直連配置；title/tags/follow-up 停用；API key dummy |
| P11 | 驅動器名分：N9 收編退役 backfill_knowhow_pipeline.py+承接 refresh_text_understanding DAG | 准（單驅動器=#12） |
| P12 | Milvus Lite→Standalone 時點 | Lite 首期；實測觸界（容量/延遲）才升，vectorindex adapter 換裝零上游改動 |
| P13 | materials_project API key／nist_webbook | key 緩議；nist 維持停用（能抓≠該抓） |
| P14 | 殼落點+AST 稽核 | oai_compat 住 advisor package（自動入既有隔離稽核）；CLI 在 scripts |
| P15 | 入憲文字+升版 v1.22.0→v1.23.0 | §12 附文，用戶過目後入 |

## 9. 驗收判準（機器可重放；計畫自述不作數）

- **R0-R4 階梯**（每級=可對話+可機器驗收、通過才升）：
  - **R0 誠實雙向**：庫外虛構化合物→固定誠實句（不經 LLM，機械保證）；庫內已知句→必答不假不知道；固定測例住版本化 SSOT（含 IUPAC/化學式 textnorm 全形集樣本）、變更須過目；隔離測例=非法 license/flagged 語料 0 洩漏**由閘保證非僥倖**（fail-closed 實證）。
  - **R1 逐字引**：verify_verbatim 對 item_text `substring(FROM char_start+1)` 他證；locator 必附（guard_definition 課）。
  - **R2 意涵統計**：回答統計數字 100%∈雙源白名單；衍生列 method_key 100% 四值。
  - **R3 思想圖譜**：graph 擴展確定性（同 query 重放同結果）；rerank 只准 counts 類分數。
  - **R4 全量索引**：Milvus 雙向對帳差=0+排除帳落庫等式；**rank@10 有/無索引兩組真值證增量**。
- **冪等**：驅動器與各段連跑兩次 exit 0、計數不變；subprocess 全 check=True。
- **可替換性四證**：(a) 換模 1k 句走 SOP-A，git diff 只落 embedspec+預期表/collection，**新 tag 列數斷言>0**；(b) 換 LLM 改設定一行、guard 測例全綠、code diff=0；(c) Milvus DROP→PG 全量重建→對帳 0 差；(d) chemical_engineering 真第二域 dry-run、code diff=0。
- **繞閘防堵**：殼輸出唯一出口=advise()+guard（grep/AST 實證無旁路 return）；WebUI 配置稽核（無直連端點）；新增 code 全入 `test_philosophy_isolation.py`（預測 7 package 零 import philosophy/advisor/knowledge）。
- **coverage 對偶錶**：`items_with_fulltext`（現分子 0=誠實現況）、`domains_with_clean_text`（/12）、`mv_synced/source`；append-only 帶 instance+model_tag 快照。
- **宣稱誠實**：forbidden_pat 掃描 0（新 schema/code/註解全掃）。
- **格式**：W 雙欄狀態表（§11）+順序硬約束總表為執行 checklist；「竣工」保留給驗收通過；修法前後同一 verify 工具打基線。

## 10. Token 經濟（全程零 usage 證明；#28/#29）

| 環節 | 執行主體 | 執行期 Claude usage |
|---|---|---|
| S1-S4 harvest/promote/fulltext/切句/統計 | 本地 python+PostgreSQL（外部 API 限速受控） | **0** |
| S5 嵌入 | 本地 GPU（`venv` torch，842 句/s 實測） | **0** |
| S6 匯出對帳 | 本地 python+Milvus Lite | **0** |
| S7 對話 | 本地 Ollama qwen3:8b+殼（常駐） | **0** |
| 驅動器/待辦矩陣/驗收測例 | 純 SQL+curl+exit code，用戶可自跑（#29 效益） | **0** |
| Claude 唯一消耗 | 缺件開發（N1-N9/M1-M5 一次性）+拍板 P1-P15+驗收判讀（讀摘要行非全 log） | 一次性、最小化 |

背景規約：nohup+log+完成單次通知；不輪詢不自掛喚醒鏈；配額近滿=停下等（resume 全 DB-driven 無半途不一致）。

## 11. W 工作項雙欄表+順序硬約束總表

| W | 工作項 | 灌庫/落地 | 驗收 |
|---|---|---|---|
| W0 | 拍板批次 P1-P14 | — | 逐項過目紀錄 |
| W1 | N1 corpus CLEAN+CLEAN_ITEM | 待 | fail-closed 測例 |
| W2 | S2 promote 化學 | 待 | 計數+lineage 抽查 |
| W3 | S3 fulltext 首跑（+M3 sha1） | 待 | coverage 首筆+license 0 NULL |
| W4 | S3 切句/concordance items 側 | 待 | 冪等重放+textnorm 化學測例 |
| W5 | S4 統計延伸（M4/M5） | 待 | method_key 100%+有界預算 |
| W6 | N2 embedspec+M1 embed 四改+嵌入 | 待 | 機器等式+換模防呆斷言 |
| W7 | N3/N4 vectorindex+匯出+雙向對帳 | 待 | 差=0+DROP 重建演練 |
| W8 | N5/N6/N7/M2 對話管線件 | 待 | R0/R1 curl 雙向 |
| W9 | N8 殼+WebUI 接線（P10） | 待 | AST+配置稽核+偽 SSE 實測 |
| W10 | N9 驅動器+R1 退役 backfill | 待 | 連跑兩次冪等+端到端煙測 |
| W11 | R0-R4 化學驗收+可替換性四證 | 待 | 全綠 |

**順序硬約束總表**（約束→違反後果）：① CLEAN_ITEM 接進 embed **先於**任何 items 句嵌入→索引汙染、清=重灌；② P6 複合鍵+embedspec **先於**換模演練→靜默零寫入假成功；③ 分側/分語 scope **先於** en 放量→數 GB 重灌不可逆；④ P1-P3 拍板**先於** S4 DDL→封閉集變更未經決策層；⑤ P8 guard 域條款**先於** WebUI 對話驗收→系統性假不知道；⑥ #25 最小單位**先於**一切放量→IP ban+假信心；⑦ 殼經 advise() **先於** WebUI 接線→第二編排器/繞閘；⑧ backfill 退役**同批於**驅動器上線→雙驅動器違 #12。

## 12. 入憲掛靠（v1.22.0→v1.23.0）

憲章 philosophy 層新增精簡小節「知識域端到端管線（七段一驅）」（草文=本次交付 charter_section），從屬共同不變式①-④、不複誦三敵；修訂歷程新列 3 行封頂體例（草文=charter_history_row）；**僅憲章升版** v1.22.0→v1.23.0、原則精華維持 v1.7.1；同步清單=原則精華交叉引用+README 連結+CLAUDE.md #28/#29 對應條+檔名改版。本計畫=第六部詳計畫 SSOT。

## 附錄：對抗審查修正錄（major 全數處置）

| verdict（共病歸併） | 本稿處置 |
|---|---|
| B/C：fetch_oa_fulltext.py 已存在仍列新建=第二寫端違 #12 | §3-S3 改為沿用既有+M3 sha1 增量；新建否決 |
| 三案：embed item 側 fail-open 與「零改 code」矛盾 | §3-S5「零改」宣稱撤回；M1(a) CLEAN 閘=硬前置；順序硬約束① |
| 三案：en 1.5M 游標耦合未揭露 | M1(b) 分側 scope+P7；禁手撥游標 |
| A/B/C：換模 SOP 於現 schema=靜默假成功（MODEL_TAG 寫死/PK 單欄/DO NOTHING/384 寫死） | P6 schema 前置+M1(c)(d)+SOP-A 列數斷言防呆 |
| 三案：guard 域錯配→系統性假不知道（②③、<think>） | N6 KnowledgePayload+P8 憲章級域條款+N5 機械剝除 |
| A：殼重造編排=第二編排器、漏空檢索分支、guard fail 未定義 | N8 殼=薄 adapter 唯一出口 advise()；guard fail=固定誠實句閉集（P9） |
| A/B/C：WebUI 現實三缺（SSE/title-gen/逾時） | N8 偽 SSE+P10 停用三生成+逾時揭露、先 curl 後 WebUI |
| 三案：backfill_knowhow_pipeline.py 未收編=雙驅動器 | P11+R1 退役；check=False 反例終結（N9 全 check=True） |
| A/C：collection 縮寫無 SSOT（model_tag 含 '/' 非法） | N2 embedspec 命名函數單一住所；禁手寫縮寫 |
| A/C：殭屍向量無刪除傳播/重建判準 | §3-S6 雙向 anti-join+同 run 刪除傳播+機器重建觸發判準 |
| B：假域列驗收摻假資料 | SOP-D 改用真第二域 chemical_engineering |
| C：promote --batch/embed --model 捏造旗標 | §5 SOP 全用實查旗標；M1 新旗標明標「落地後才可用」 |
| B/C：verify_verbatim 注入繞過 | M2 advise() 一律後驗機械收斂 |
| A：向量介面住 scripts | N3 移 src/ library 層 |
| C：閘後 coverage 注入 | 機械模板零 LLM 內容+定義入 P8 閘鏈 |
| C：驅動器漏 S1+stage registry DB 表 | §7 DAG 含 harvest；段序=code 內常數表 |