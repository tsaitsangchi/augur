# augur 知識控制台(Admin 後台)計畫 — 主題自動抓取 × 資料夾多格式解析 × 誠實對話【定稿 v2】

**日期**:2026-07-04　**性質**:功能規劃(尚未實作;治權定位在最前,違則不建)
**治權**:靈魂 v1.4.0 · 原則精華 v1.7.1 · 憲章 v1.25.0(philosophy 橫切/知識端到端管線 v1.23.0 七段一驅)· CLAUDE #29
**用戶 directive(2026-07-04)**:AI 後台可 admin 登入;輸入如「財經資料」即自動從外部抓所有相關財經資料入庫供對話;`+資料夾` 遞迴讀取夾內(含子夾)任意副檔名檔案、解析入庫。
**本稿=定稿**:吸收三決議者(治權安全/複用最大/admin 可用)之長 + 對抗審查 fatal/major 全數 fix。凡與草案 v1 分歧處,以本稿為準;差異摘要見 §九。

---

## 〇、治權定位(**最重要,先讀;設計的邊界,不是裝飾**)

用戶說「抓資料**到模型**」——此處「模型」**只能是知識/素養層(RAG,供「誠實博學的我」對話),絕不是預測模型**。理由(命門,不可繞):

1. **預測模型受 #1 Source-Pure 命門管**:只能吃 FinMind/FRED 之 source-pure 值(真實 API × 數學轉換)。把外部抓來的任意財經資料/檔案灌進預測模型 = 注入假資料(敵人①)→ 模型無意義。**本計畫之任何資料一律不進 `feature_values`／不進預測管線。** 若後續現「餵預測」意圖 → 與 #1 衝突、**停下討論不逕自實作**(決策層)。
2. **知識層 ↔ 預測管線隔離之機器保證現況(誠實揭露,#15)**:
   - **AST import-lint 已在(單向)**:`tests/test_philosophy_isolation.py` 之 `PIPELINE=(features,models,universe,evaluation,ingestion,audit,catalog)` 禁 import `FORBIDDEN=(augur.philosophy,augur.advisor,augur.knowledge)`。新件 `fileparse.py` 落 `src/augur/knowledge/` **天然受此不變式管**;新 package 名**絕不加進 `PIPELINE` tuple**。
   - **反向護欄尚未存在→本計畫補為硬要求**:現行 lint 只保證「預測不 import 素養層」,不保證「admin/知識新件不反向 import 預測管線、不寫 `feature_values`」。本計畫新增觸發器/檔案入庫器正是最易手滑處 → §四列為驗收硬門檻(非建議級)。
   - **DB role 隔離尚未落地(誠實揭露)**:實查 `current_user=augur`、`rolsuper=false`,但**單一 login role 同時讀寫預測表與知識表**;無獨立唯讀-預測-表的 advisor role。**本稿不得把「DB role 隔離」當既成事實**;本輪以 code 層(雙向 import-lint + 寫入斷言)為主護欄,DB role 列為後續強化項(運維動作、決策層,§四附註)。
3. **知識層准入判準仍全套適用**(不因「admin 手動」放鬆):① 真實來源＋provenance 可溯源(#1／#15);② **license 白名單硬擋**(`public_domain`/`cc-by`/`cc-by-sa`/`cc0`;NC/ND/版權未明停 metadata;DB CHECK,實查確認四值);③ **禁 AI 生成內容入庫**——**誠實現況:此 DB CHECK 目前只在 `philosophy_source`/`philosophy_work`,知識側 `knowledge_item*` 無此欄無此 CHECK**(草案 v1 §〇.3③ 之「知識側有 DB CHECK」係把哲學側約束記憶推估到知識側之假兆,已刪);`+資料夾`/`local_upload` 正是引入 AI 生成內容之新入口 → 本稿列 P0 補 `knowledge_item_text.source_type` 欄＋CHECK(見拍板 P3新);④ 逐字入庫、AI 只在回答時刻組織(命門);⑤ `domain` 欄隔離因子鏈純度(財經知識＝素養層、量化零價值、不產因子)。
4. **對話仍過 guard 單閘**(憲章 v1.25.0 防幻覺機械閘＋三級誠實固定句閉集)——admin 抓再多資料,回答仍逐字可溯源、閉集誠實、模型零即興。後台**不得**新增任何繞過 `advise()` 的對話路徑(含後台內「快速問答」捷徑、私有池直查)。

> 一句話:本控制台是**知識/素養層的 admin 管理與擷取前端**,讓「誠實博學的我」更博學;它**不改預測、不鬆三敵、不繞 guard**。

---

## 一、三大功能 × 既有基建對映(複用為主、缺件最小)

| 用戶要的 | 既有基建(複用) | 缺件 |
|---|---|---|
| **A. 輸入「財經資料」→ 自動抓所有相關入庫** | 知識三層管線 `knowledge_source`→`acquire_knowledge.py`(13 adapter)→`knowledge_staging`→`promote_knowledge.py`;財經域已在 registry(`economics_econometrics_and_finance` **實查 107 query**／`finance_mgmt` 12／`investment_mgmt` 12);批次 `harvest_knowledge.py`(排程矩陣+限速+熔斷+resume) | 主題→查詢展開(薄查詢,從 registry 選域)＋ admin 觸發/監看 UI |
| **B. `+資料夾` 遞迴讀任意副檔名、解析入庫** | `knowledge_item_text` 全文表＋license CHECK;T3 切句/T4 concordance/嵌入鏈(`--scope items`);HTML 剝標樣板 `fetch_oa_fulltext.py:strip_html`(**純 stdlib `re`+`html`,零依賴**) | **遞迴多格式檔案抽取器**(新,見 §三)＋ `+路徑` 觸發語法。**模板=`fetch_oa_fulltext.py:145-152`(建 item metadata + 寫 item_text),非 `adapter_manual_file`** |
| **C. 「誠實博學的我」消費上述知識對話** | advisor 對話棧(`serve_advisor_openai.py` OpenAI 相容殼＋`serve_chat_ui.py` 前端＋guard 單閘＋Ollama qwen3);pgvector 檢索 | **對話端接線 `retrieve_items`(真缺件,見 §三死點)**＋對話 UI 內嵌 `+` 語法 |
| **D. Admin 登入後台** | (無,全新橫切元件) | **admin web 後台＋認證＋任務監看**(新,見 §四) |

**事實錨更正(草案 v1 之三假兆,#15)**:
- ✗ **`adapter_manual_file` 非 `+資料夾` 複用點**:實證 `acquire_knowledge.py:76-79` 它收 `--file <json>` payload 陣列進 `knowledge_staging`(metadata),**不解析任何檔案內容**。`+資料夾` 全文入庫走 `fetch_oa_fulltext.py` 模板另建。
- ✗ **`openpyxl`「已裝」→ 未裝**:實查 venv 已裝僅 `PIL`/`jieba`/`sentence_transformers`/`psycopg2`/`yaml`;`openpyxl`/`pypdf`/`python-docx`/`python-pptx`/`ebooklib`/`pytesseract`/`fastapi`/`uvicorn`/`bcrypt` **全未裝、須補**。
- ✗ **殼埠 `:8500`/`:8091`→ 實為 `127.0.0.1:8399`**:`serve_advisor_openai.py` 殼綁 `127.0.0.1:8399`、`serve_chat_ui.py` 綁 `:8090`;新 admin 後台綁 `127.0.0.1:8500`。

---

## 二、架構(Admin 控制台＝知識層之管理前端,八段一驅之「操作面」)

```
┌──────────────── Admin 後台(新,127.0.0.1:8500)認證後 ────────────────┐
│  [搜尋列] 輸入「財經資料」→ 展開既有 registry query 集 → 確認頁(N query/  │
│           預估額度/首輪 --batch 10)→ admin 確認才觸發 harvest            │
│  [+資料夾] +/path/to/dir → 遞迴掃描(逐檔 realpath 圍欄)→ 多格式解析      │
│           → item_text(access_scope=local_private)                        │
│  [任務監看] harvest/parse 進度、staging pending、coverage 錶、skip 分類報表│
│  [對話] 內嵌/反代既有 :8399 殼(過 guard、引經據典)                       │
└───────────────┬───────────────────────────────┬───────────────────────┘
   觸發(subprocess 白名單/背景/唯讀啟動)      對話反代(零改 advise/guard/殼)
                ▼                                 ▼
   既有知識管線(本地背景、零 Claude usage)      既有 advisor 棧(:8399)
   source→acquire→staging→promote→item_text     retrieve_items(接線後)
   →T3/T4→嵌入(pgvector)                          →advise→guard→Ollama
                │
        全程受 §〇 治權護欄(license/scope/provenance/禁AI生成/domain/隔離)
```

**鐵則**:後台**只觸發既有本地 script**(subprocess 參數陣列、`shell=False`),**不重造管線、不自建第二編排**;抓取/解析全走既有限速＋license 閘＋provenance;對話全走既有 guard 單閘(唯一編排入口=`advise()`)。

---

## 三、缺件:遞迴多格式檔案抽取器(`+資料夾` 核心)

新 `src/augur/knowledge/fileparse.py`(library、領域名詞、純規則零 LLM)＋ `scripts/acquire_local_files.py`(CLI 動詞片語):

- **遞迴掃描**:`+/path` → `os.walk(root, followlinks=False)` 夾內＋所有子夾;每檔記 provenance(絕對 realpath＋mtime＋sha1＋`source_type='local_upload'`)。
- **多格式文字抽取矩陣**(每副檔名 → 抽取器;**純規則、零 LLM/零 API**;抽不出＝誠實跳過並記數,不硬湊):

| 類 | 副檔名 | 抽取器(本地、零 API) | 階段 |
|---|---|---|---|
| 純文字 | txt/md/csv/tsv/log/json/xml/yaml | 直讀(`chardet` 偵編碼、`errors='replace'` 兜底,複用 `fetch_oa_fulltext.py:137` 慣例) | P1 |
| 文件 | pdf | `pypdf`/`pdfplumber`(掃描檔→P5 可選 OCR) | P1 |
| Office | docx | `python-docx` | P1 |
| Office | pptx/xlsx | `python-pptx`/`openpyxl` | P5 |
| 網頁 | html/htm | **複用既有 `fetch_oa_fulltext.py:strip_html`(零依賴 stdlib,不引 bs4)** | P5 |
| 電子書 | epub | `ebooklib` | P5 |
| 影像 | png/jpg/tiff | OCR(`pytesseract`,標 `extraction_method='ocr'`;預設關) | P5 |
| 程式碼 | py/js/… | 直讀(當純文字) | P1 |
| 未知/二進位/損壞/加密 | * | **跳過＋記 skip 分類(parse_error/encrypted/oversize/decode_error/symlink_escape/unknown_ext);不入庫、不杜撰內容** | 全 |

- **落地**(模板=`fetch_oa_fulltext.py:145-152`,逐檔一個 `db.transaction`):抽出文字 → 建 `knowledge_item`(metadata)＋寫 `knowledge_item_text`,欄值:
  - `license`＝**真實授權事實**(本機他人著作多為版權未明 → **停 metadata、不入嵌入**);**license 四值白名單不動、不擴 `local_owned`**(見拍板 P2)。
  - `access_scope='local_private'`(新欄,拍板 P2)。
  - `source_type='local_upload'`(新欄,拍板 P3新;DB CHECK `<> 'ai_generated'` 硬擋)。
  - `entity_type` 落點=**拍板 P2附**(見下「死點②」;需入 `SEMANTIC_ENTITY_TYPES` 否則嵌入端 0 入池)。
  - 冪等鍵=`sha1`(入庫前 `SELECT NOT EXISTS` 跳過,仿 `fetch_oa_fulltext` PENDING)。
- **治權**:逐字入庫(禁 AI 摘要改寫,#1)＋provenance 全套;版權他人著作放本機**不代表可轉為公開真兆**——`access_scope=local_private`、僅供 admin 自身素養對話、**不外流**(不入對外檢索池,見拍板 P2 機器保證)。

### 死點①(真缺件,對抗審查點名):對話端未接 `retrieve_items` → 抓了問不到

實證:`advise.py:30` `src_fn = retrieve if retrieve_fn is None else retrieve_fn`;`serve_advisor_openai.py`/`oai_compat.make_server` **從不傳 `retrieve_fn`** → 預設 `None` → 對話只走 work 側(哲學/文學語料);items 側 `retrieve_items`(`retrieval.py:225`,**已存在**)從未接線。**意涵:抓來的財經知識/本機檔即使入庫、切句、嵌入,現行對話棧檢索端零命中**——整個控制台價值兌現點不成立。
**仲裁(定稿)**:採「admin 可用優先」主張,**接線提前為 P1.5**(最小檔案入庫後立即驗端到端),**不甩給未排期之 e2e N7**——理由:這是控制台成立的唯一硬判準,不能依賴外部未定件。接線本身極小(`serve_advisor_openai` 傳入 `retrieve_fn=retrieve_items` 或雙側合併檢索),零改 advise/guard 本體。接線後**仍須保留 `access_scope='public'` 過濾**(不為讓 items 通而放行 local_private)。

### 死點②(FATAL,對抗審查點名):`entity_type` CLEAN 閘 fail-closed → 本機檔嵌入 0 入池

實證:`corpus.py:19` `SEMANTIC_ENTITY_TYPES = ("paper","report")`,`clean_item_sql`(`corpus.py:42-43`)之述詞 `entity_type IN ('paper','report')` 為 **concordance(exact)路徑與 ANN 路徑共同、唯一的擋牆**(`retrieval.py` `retrieve_items` 兩路徑均套 `clean`)。若本機檔給 `entity_type='book'/'document'/'local_upload'`,則其句在 embed 端 0 入池、且 concordance exact 路徑亦 0 返 → **即使死點①接了 `retrieve_items`,向量庫裡也根本沒有它,「抓了問得到」在 entity_type 層就已斷**。
**拍板 P2附(P0 前置)**:本機檔 `entity_type` 落點須與 CLEAN 閘一致。**採方案 B(較誠實)**:新增 entity_type 值 `'document'` 並同步加入 `corpus.py:19 SEMANTIC_ENTITY_TYPES`(跨檔一致 #19:若 `entity_type` 有 DB CHECK 亦同步)。**不採方案 A**(把本機檔硬標 `'report'` 復用白名單)——語意失真、把私文件當報告,踩 #15。驗收綁死:入一筆本機檔→跑 `build_sentences --scope items`→`embed_knowledge --scope items`→實查 `knowledge_sentence_embedding` 該 sent_id **有列(非 0)**。

---

## 四、缺件:Admin 後台＋認證＋安全設計(#5 OWASP,逐條 fail-closed)

**後端框架(拍板 P4)**:**stdlib `http.server`**,綁 `127.0.0.1:8500`。**不引 FastAPI/uvicorn/flask**——既有 `oai_compat.py`/`serve_chat_ui.py` 已證 stdlib 足夠(唯讀、loopback、薄編排),多一框架=多一批 CVE 面(最小攻擊面)+ 全未裝需補(#28)。認證雜湊:**`argon2id`(argon2-cffi)或 `bcrypt`(cost≥12)單一依賴,不自捲 scrypt 參數**(避 OWASP A02 密碼學失誤)。

以下為對抗審查所有 fatal/major 安全 fix,列為**硬要求**(非建議),逐條進驗收:

### 4.1 認證與密鑰儲存(對抗 FATAL:.env world-readable)
- admin 密碼雜湊**與 DB_PASSWORD 分離**:存獨立檔 `secrets/admin_credential`(**權限 600、gitignore**),非與 DB 密碼同 `.env`(降單檔洩漏爆炸半徑)。
- 啟動時斷言 `os.stat(credential).st_mode & 0o077 == 0`,非 600 則**拒啟(fail-closed)**。
- 雜湊用 `argon2id`/`bcrypt(cost≥12)`,逐帳號隨機 salt 一同存。
- 密碼雜湊/salt **禁進 git**:驗收 `git log -p` 全歷史 grep 確認從未進 git。
- **登入失敗計數 + 鎖定**(對抗 A07):連 N 次失敗(如 5)鎖定或指數退避;審計 log 記 `login_success`/`login_fail`/`logout`。session token `secrets.token_urlsafe(32)` + HttpOnly + `Secure` + `SameSite=Strict`,設過期(如 8h)+ 閒置逾時,不做永久 session。

### 4.2 CSRF / 對話端重用(對抗 FATAL:反代無認證殼 + 無 CSRF)
- **對話端(唯讀問答)與觸發端(subprocess)物理分兩類 handler**。任何**改變狀態**端點(觸發 subprocess/`+資料夾`/抓取)一律過三檢:① CSRF token(每 session 發 `secrets.token_urlsafe(32)`,雙重提交比對 header `X-CSRF-Token`)② `Origin`/`Referer` 須 `== http://127.0.0.1:8500`(缺或不符即 403,防 DNS rebinding+跨站)③ session 驗證。
- **不可直接反代未改的 `:8399` 殼作觸發面**(`:8399` 設計為無認證本機工具);**對話反代可、觸發絕不可走它**。

### 4.3 路徑穿越 / 符號連結逃逸(對抗 MAJOR:os.walk symlink 逃逸)
- `--dir` 白名單根:**清單存 config、非 admin 執行時任意輸入;禁設為 `$HOME`/`/`/`/home`,須明確狹窄目錄**。
- **逐檔硬斷言**(非只驗 `--dir` 入口):對 `os.walk` 產出的**每個檔案** `os.path.realpath(f)` 須 `startswith(realpath(白名單根)+os.sep)`,否則 skip+記 `symlink_escape`(不 open、不 sha1)。
- `os.walk(root, followlinks=False)` 明示;每個 dirpath 亦做 realpath 圍欄。
- 開檔用 `os.open(f, os.O_RDONLY | os.O_NOFOLLOW)`(最後一段 symlink 報 ELOOP 即拒);`os.path.isfile()` 過濾特殊檔(FIFO/device/socket)。

### 4.4 subprocess 注入 / argument injection(對抗 MAJOR)
- `subprocess` 參數**陣列非 shell 字串**、`shell=False`(防 metacharacter 注入)。
- **進 argv 的使用者控制值先過白名單/正規化**(防 argument injection):`--domain` 必 ∈ registry 已知 domain 集(拒任意值)、`--dir` 必 ∈ 白名單根、topic 映射到 registry `query_id` 而非自由字串拼 `--query`。
- 子 script(`acquire_local_files`/`expand_topic_queries`)自身 argparse 對 `--domain` 用 `choices=`、數值旗標設上限(雙層防護)。
- **長跑 subprocess 非阻塞**:觸發 harvest/embed 一律 `Popen` fire-and-forget(不在 HTTP handler 內 `subprocess.run(check=True)` 等到跑完,避免阻塞 `ThreadingHTTPServer` 執行緒 + UI 假死);進度落 `harvest_log`/audit_log 供任務看板唯讀輪詢,handler 立即回 202。

### 4.5 惡意檔案解析(對抗 MAJOR:zip bomb / XXE / OOM)
- 逐檔大小上限(如 >50MB 直接 skip 記 `oversize`),抽取前先 `os.path.getsize`。
- zip 類(docx/pptx/xlsx/epub)解壓前檢查壓縮比(>100:1 或解壓總量超限即拒,防 zip bomb)。
- XML(docx/xml/svg)用 **`defusedxml` 或關閉外部實體/DTD**(`resolve_entities=False`),**絕不用預設 `ElementTree` 解析不受信任 XML**(防 XXE/billion-laughs)。
- 每檔抽取包 **try/except 隔離**(任一例外→記 skip 帶原因,絕不讓單檔炸掉整夾)+ wall-clock timeout(如 `signal.alarm`,防解析器無限迴圈)。巨檔分塊讀、不一次 `read()`。

### 4.6 綁定位址暴露(對抗 MAJOR:--host 0.0.0.0)
- admin console **硬綁 `127.0.0.1`(硬編碼,不提供 `--host` 參數)**;若必須提供,啟動斷言 `host in {"127.0.0.1","::1","localhost"}` 否則拒啟。
- 設請求體上限(`Content-Length` 超限即 413)防記憶體耗盡。
- 驗收 `ss`/`netstat` 實查 LISTEN 為 `127.0.0.1` 非 `0.0.0.0`。

### 4.7 審計 log
- append-only、**權限 600、與資料分離、輪替**;記「觸發者/時間/命令陣列(完整 argv)/退出碼/影響列數」+ 認證事件。

### 4.8 隔離機器保證(對抗 MAJOR:反向 lint 缺、DB role 虛報)——升為硬門檻
- **反向 import-lint 斷言**:`fileparse`/`acquire_local_files`/`serve_admin_console` **禁 import `augur.{features,models,universe,evaluation}`**(進 `test_philosophy_isolation.py` 或新 `test_admin_console_isolation.py`,CI 綠燈,fail 即不合併)。
- **寫入斷言**:AST/grep 稽核新件源碼**零 `feature_values` 之 INSERT/UPDATE**。
- **新 package 名絕不加進 `PIPELINE` tuple**(明文入邊界)。
- **DB role 隔離標「尚未落地」**:本輪以 code 層護欄為主;要真落地=另建唯讀-預測-表 role + `REVOKE INSERT/UPDATE ON feature_values` + admin 後台以該 role 連線(運維動作、決策層,列後續強化)。

---

## 五、拍板決議(依用戶授權自行決議、對抗後定稿)

| # | 拍板 | 決議值 | 依據 |
|---|---|---|---|
| **P1** | 「到模型」範圍 | **知識/RAG 素養層(非預測模型)**;零進 `feature_values`/預測管線;三重機器保證(AST 雙向 lint + 寫入斷言 + 觸發白名單不含預測 script);現餵預測意圖→停 | §〇、#1 命門 |
| **P2** | 本機檔 license/scope | **不擴 license 白名單納 `local_owned`**;維持四值不動;**新增 `knowledge_item_text.access_scope∈{public,local_private}`**,本機檔=`local_private`+license 照填真實授權(未知→停 metadata、不入嵌入);`local_private` 句**不進對外檢索池** | 對抗 FATAL(license 後門)、#1/#15 |
| **P2附** | 本機檔 entity_type | **新增 `'document'` 入 `SEMANTIC_ENTITY_TYPES`**(方案B,較誠實;不硬標 report);跨檔一致同步 corpus.py+DDL | 對抗 FATAL(嵌入 0 入池死點) |
| **P3新** | 知識側禁 AI 生成硬擋 | **補 `knowledge_item_text.source_type varchar(24) NOT NULL DEFAULT 'external' CHECK (source_type <> 'ai_generated')`**;DDL 併 `migrate_text_understanding_ddl.py` 單一住所 | 對抗 MAJOR(假兆/新入口風險) |
| **P4** | 後端框架 | **stdlib `http.server`**(與 `oai_compat` 一致、零新後端依賴);認證補單一 `argon2`/`bcrypt` 依賴 | 對抗 FATAL(密碼學)、#18/#28 |
| **P5** | OCR | **預設關**;開啟時純光學(pytesseract)、標 `extraction_method='ocr'`、**零 AI 摘要/改寫** | 對抗 MAJOR(抽取器 AI 內容) |
| **P6** | 抓取範圍 | 初始 query 集=registry `economics_econometrics_and_finance`(**107**)+`finance_mgmt`(12)+`investment_mgmt`(12),**不即興擴域**;搜尋列展開後**確認頁(N query/預估額度/首輪 `--batch 10`)admin 確認才觸發**;放量走既有 `harvest_knowledge.py` 三層限速/熔斷/resume,撞 403 見停不 retry | §六⑤、#24/#25 |
| **P7** | 認證強度 | **單 admin + `127.0.0.1` 本機硬綁**;遠端/多用戶排除(另議,需 HTTPS+authz+CSRF 全套) | 對抗 FATAL/MAJOR、#5 |

---

## 六、缺件最終封閉集(4 新 + 2 改 + 1 接線 + 1 測)

**新增(3 支 script + 建議 1 測)**:

| 檔(絕對路徑) | 類型 | 職責 |
|---|---|---|
| `/home/hugo/project/augur/src/augur/knowledge/fileparse.py` | library(領域名詞) | 純規則多格式抽取(零 LLM);副檔名→抽取器矩陣;每檔 try/except 隔離+大小/zip-bomb/XXE/timeout 護欄;html 複用 `strip_html`;抽不出→回 `None`+skip 分類;OCR 標 `extraction_method` |
| `/home/hugo/project/augur/scripts/acquire_local_files.py` | CLI(動詞片語) | `--dir X --domain Y [--ocr off]`:`os.walk(followlinks=False)`+逐檔 realpath 圍欄+sha1/mtime→`fileparse`→建 `knowledge_item`+寫 `knowledge_item_text`(`access_scope=local_private`/`source_type=local_upload`/`entity_type=document`/真實 license)→接切句/嵌入鏈;**逐檔一交易+`sha1` 冪等 resume**;模板=`fetch_oa_fulltext.py:145-152` |
| `/home/hugo/project/augur/scripts/serve_admin_console.py` | CLI(動詞片語) | stdlib `http.server` 硬綁 `127.0.0.1:8500`;argon2 認證+失敗鎖定+session;對話/觸發雙 handler(觸發過 CSRF+Origin+session 三檢);`--dir` 白名單根;subprocess 陣列 `shell=False`+argv 白名單+fire-and-forget;審計 log 600;對話反代既有 `:8399`(零改殼) |
| `/home/hugo/project/augur/tests/test_admin_console_isolation.py`(或擴 `test_philosophy_isolation.py`) | test | 反向斷言(admin/fileparse 側零 import 預測 4 pkg)+ 寫入斷言(零 `feature_values` 寫入)+ 新 package 不在 `PIPELINE` |

**改既有(2 處,DDL 單一住所 M5,非第二遷移)**:

| 檔 | 改動 |
|---|---|
| `/home/hugo/project/augur/scripts/migrate_text_understanding_ddl.py` | `knowledge_item_text` **+2 欄**:`access_scope∈{public,local_private}`(P2)、`source_type CHECK <> 'ai_generated'`(P3新);IF NOT EXISTS;新欄先印全文過目 |
| `/home/hugo/project/augur/src/augur/knowledge/corpus.py` | (a) `SEMANTIC_ENTITY_TYPES` **+`'document'`**(P2附);(b) `clean_item_sql` 述詞 **+`access_scope='public'`**(P2 fail-closed,加在 SSOT 本體→concordance+ANN 兩路徑同受管);license 白名單值**不動** |

**真缺件接線(P1.5,不甩外部)**:

| 檔 | 改動 |
|---|---|
| `/home/hugo/project/augur/scripts/serve_advisor_openai.py`(+`oai_compat.make_server` 呼叫處) | 傳 `retrieve_fn=retrieve_items`(或雙側合併檢索),接 `retrieval.py:225`;保留 `access_scope='public'` 過濾 |

**零改**:advisor 既有件(`advise/oai_compat/guard/payload/prompt/ollama`)本體、`harvest_knowledge.py`/`acquire_knowledge.py`/`promote_knowledge.py`/`build_sentences.py`/`build_concordance.py`/`embed_knowledge.py`、`serve_chat_ui.py`、預測管線任一檔。git diff 驗收:既有 harvest/promote/embed/advisor 件 **diff=0**。

**依賴補裝**:P1 最小集=`pypdf`(或 pdfplumber)+`python-docx`+`chardet`+`argon2-cffi`(或 bcrypt)+`defusedxml`;P5 才補 `openpyxl`+`python-pptx`+`ebooklib`+`pytesseract`+tesseract OS 層。html 用既有 `strip_html` 零依賴。

---

## 七、分階段執行(治權硬擋前置、對話死點提前、每階段自身可驗)

| 階段 | 內容 | 前置硬約束/自身驗收 |
|---|---|---|
| **P0 DDL 硬擋(前置)** | 改 `migrate_text_understanding_ddl.py`(+`access_scope`+`source_type` CHECK);改 `corpus.py`(+`document` entity_type、CLEAN +`access_scope='public'`);跑 migration | **順序鐵律=先立硬擋再開資料入口**;DB 實測拒 `ai_generated`/拒非法 scope;違則不進 P1 |
| **P1 檔案 MVP(CLI)** | `fileparse.py`+`acquire_local_files.py`(txt/md/csv/json/pdf/docx 六格式);依賴補裝;寫 `access_scope=local_private`/`entity_type=document` | 反向 import-lint+寫入斷言綠;抽取零 LLM 實測;provenance 逐檔落地;跑真夾增列;skip 分類帳對得上 |
| **P1.5 對話接線(死點先解)** | `serve_advisor_openai` 接 `retrieve_items` | 起殼、對 P1 入庫檔提問、**回答 citations 逐字∈該檔 item_text、過 guard**;`local_private` 檢索排除實測——控制台 go/no-go |
| **P2 主題 MVP(CLI)** | `expand_topic_queries`(107+12+12 薄展開)+`--batch 10` 觸發 harvest | 首輪 batch 10 之 license 命中率/provenance 完整率實查;#25 通了才放量 |
| **P3 後台骨架+認證** | `serve_admin_console.py`(stdlib+argon2+session+CSRF+路徑防穿越+subprocess 白名單+審計 log) | `../`/symlink 逃逸拒;`shell=False`;`.env`/credential 600 不進 git;硬綁 `127.0.0.1`;CSRF/Origin 三檢 |
| **P4 對話整合** | 反代既有 `:8399` 殼進後台;`+/path` UI;`local_private` 徽章 | 對話**全過既有 guard 單閘**、後台**零繞閘路徑**(含快速問答捷徑亦禁);依 P1.5 接線已落地 |
| **P5 擴格式/OCR** | pptx/xlsx/epub/html(零依賴 `strip_html`)/OCR(標 `extraction_method`);未知格式誠實跳過報表 | OCR 純光學零 AI 改寫;塞加密PDF/mojibake txt/0-byte docx 掃描不崩、各記正確 skip 原因 |

**全程 #29**:每 script 個別可執行＋指令矩陣＋冪等 resume＋本地背景零 Claude usage。

---

## 八、驗收判準(可實測、fail-closed;計畫自述不作數)

**治權/隔離**:
1. `test_philosophy_isolation.py`(+反向斷言)綠:預測 7 pkg 零 import 素養層 + admin/知識新件零 import 預測 4 pkg + 新 package 不在 `PIPELINE`。
2. 寫入斷言:新件 grep 零 `feature_values` 寫入;`feature_values` 列數在本控制台任何操作前後不變。

**DB 硬擋(P0)**:
3. `INSERT knowledge_item_text(source_type='ai_generated')` 被 DB CHECK 拒(exit≠0)。
4. `INSERT ... access_scope='typo'` 被拒;`local_owned` 寫 license 仍被拒(白名單未擴)。
5. 入一筆 `access_scope='local_private'` 句→建 concordance+嵌入→`retrieve_items` **零返該句(concordance 路徑亦擋)**——CLEAN SSOT `access_scope='public'` 兩路徑實證。

**嵌入鏈通(死點②)**:
6. 入一筆本機檔(`entity_type='document'`)→`build_sentences --scope items`→`embed_knowledge --scope items`→實查 `knowledge_sentence_embedding` 該 sent_id **有列(非 0)**。

**對話可用(死點①,go/no-go)**:
7. 對 P1 入庫檔提問→回答 citations **逐字∈該檔 item_text**、過 guard、數字白名單、三級誠實閉集固定、`local_private` 徽章正確。

**抽取誠實(P5)**:
8. 抽取路徑**零 LLM 呼叫**(監控無 Ollama/OpenAI call);skip 帳與實際二進位/未知/損壞檔數對上;OCR 產物全標 `extraction_method='ocr'`;加密PDF/mojibake/0-byte 各記正確 skip 原因不崩。
9. 冪等:`acquire_local_files` 同夾連跑兩次 `knowledge_item_text` 列數不變。

**抓取界(P6)**:
10. query 集僅 registry 三組;搜尋列展開有確認頁;首輪 `--batch 10`;夜批走既有限速熔斷,撞 403 見停不 retry(log 佐證)。

**安全(#5)**:
11. credential 600 且啟動斷言 fail-closed;`git log -p` grep 確認雜湊/salt 從未進 git;登入失敗鎖定生效。
12. `--dir ../`/指向樹外 symlink 被拒(逐檔 realpath+`O_NOFOLLOW`);subprocess `shell=False` 陣列+argv 白名單;`ss` 實查 LISTEN=`127.0.0.1` 非 `0.0.0.0`;請求體上限生效。
13. 觸發端過 CSRF+Origin+session 三檢(缺 token/Origin 不符即 403);zip bomb/加密/巨檔各有護欄。

**對話單閘(③)**:
14. 後台唯一對話出口=既有 `advise()`+guard;grep 後台 code 零繞閘直連 LLM;不反代 `:8399` 作觸發面。

**複用證**:
15. git diff 僅落 3 新 script + 2 改(DDL/corpus)+ 1 接線 + 反向測;既有 harvest/promote/embed/advisor 件 diff=0。

---

## 九、與草案 v1 分歧摘要(定稿修正處)

1. **§〇.3③**:刪「知識側有 `<> ai_generated` DB CHECK」假兆→誠實現況(僅哲學側有)+ 列 P3新 補欄。
2. **§〇.2**:刪「DB role 隔離已在」既成陳述→標「尚未落地」;補反向 import-lint 為硬要求。
3. **§一/§三/檔案錨**:`adapter_manual_file` 複用點→更正模板=`fetch_oa_fulltext.py`。
4. **§三落地欄/拍板②**:`local_owned` 擴 license 白名單→`access_scope∈{public,local_private}` 正交分欄(license 四值不動、私有不冒充公版、不入對外檢索池)。
5. **新增 §三死點①②**:對話端 `retrieve_items` 未接(P1.5 先解)、`entity_type` CLEAN 閘 fail-closed(P2附 +`document`)——兩死點草案 v1 全漏。
6. **§四後端**:去 FastAPI→定 stdlib;補全 OWASP fatal/major fix(credential 分離+600 斷言、CSRF+Origin、逐檔 realpath+O_NOFOLLOW、argv 白名單、zip-bomb/XXE 護欄、硬綁 loopback、失敗鎖定)。
7. **§三依賴表**:`openpyxl`「已裝」→未裝;html 去 bs4 用既有 `strip_html`;埠 `:8399`(殼)/`:8500`(後台)校正。
8. **§五分階段**:插 P0 DDL 前置;對話整合 P1.5 提前(死點先解)。

---

## 十、與 e2e 七段一驅計畫一致性

**一致、無重造、無撞車**:本控制台=七段管線之**第八操作面(admin 前端)**,只 subprocess 觸發 S1-S6 既有 script + 反代 S7 既有 advisor 殼。`+資料夾` 之 `local_upload` 走既有 `staging→promote→item_text→切句→嵌入` 鏈全文分支(新 `source_type`/`access_scope`/`entity_type`,**非新管線**)。**唯一新增資料側動作=兩 DDL 欄 + corpus 兩處微調**,落七段「DDL 單一住所 M5」範疇,不另立第二遷移。`retrieve_items` 對話接線**本計畫 P1.5 自解**(不甩 N7,理由:控制台成立唯一硬判準,不依賴外部未定件);若 e2e N7 同時推進,兩者收斂同一接線點、不重造。

**檔案錨**:本檔=`/home/hugo/project/augur/reports/augur_admin_knowledge_console_plan_20260704.md`;複用=`scripts/{harvest_knowledge,acquire_knowledge,promote_knowledge,build_sentences,build_concordance,embed_knowledge,fetch_oa_fulltext,serve_chat_ui,serve_advisor_openai}.py`+`src/augur/advisor/*`+`src/augur/philosophy/retrieval.py:225`;改=`scripts/migrate_text_understanding_ddl.py`+`src/augur/knowledge/corpus.py`;新建=`src/augur/knowledge/fileparse.py`+`scripts/acquire_local_files.py`+`scripts/serve_admin_console.py`+`tests/test_admin_console_isolation.py`;venv=`/home/hugo/project/augur/venv/`。