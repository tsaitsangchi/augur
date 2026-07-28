# 跨域 Know-how 顧問作答 ＋ gov 覆蓋率自動審批狀態機（整合計畫）

**日期**：2026-07-28  
**性質**：[I] 執行層計畫（plan-first；CLAUDE #16／#20；**本輪只出計畫、不實作**；不改治權 [N]）  
**觸發**：Steward——「本專案所有 know-how 都不應分域，因皆具備相關性」；同輪追加——`/gov`「來源治權＋覆蓋率」審批狀態機亦做**自動審批**並與跨域作答整合  
**結構**：單一主檔（跨域＋審批整合）；姊妹對照＝`reports/augur_knowledge_fulltext_coverage_plan_20260728.md`（FT-COV；已 DASH／EMBED／HAR-ext 近程 CLOSED）  
**實證時點**：分域／狀態機＝code 親查；覆蓋分桶數字＝FT-COV 計畫 2026-07-28 live（本檔撰寫時本機 PG 暫時離線，開工前須重跑對帳）

---

## 0. 雙目標一句＋結論

| 軸 | 一句目標 |
|---|---|
| **跨域 know-how** | 顧問／素養檢索作答**不因 domain 閘死**；「孫子兵法在企業管理上的運用」等跨域題應能**最佳回答**（跨域召回＋誠實引用＋禁幻造＋license 終態） |
| **自動審批** | 在**不觸動「approve 唯人」**前提下，對覆蓋／終態管線建**執行層自動推進狀態機**（pending→answerable｜terminal_blocked；庫內 promote／句子／embed），oracle 可驗自動綠、不可驗 escalate 人裁 |

**結論（應寫計畫再實作＝yes）**：現行「分域」同時落在**策展／harvest／RBAC／儀表**與**可選檢索 filter**；跨域作答的主阻塞是「強制／預設 domain 收窄＋可答終態不足＋相關度閘過嚴／過鬆」，不是「缺孫子原文入庫」 alone。自動審批若誤做成「自動 approve／activate 來源」＝違憲章 v1.41.0 與 Sole Steward 決策層——本計畫**明示禁止**，改把「自動」鎖在**執行層終態推進**與**前置審議報告**。

---

## 1. What／Why／非目標

### 1.1 What

1. **統一 know-how 檢索空間（顧問軸）**：hybrid／RRF／query 擴展；**不作答閘**強制 `domain=`；`domain` 降為**策展標籤**（儀表／harvest 圈選／RBAC 邊界可並行，語意分離）。  
2. **跨域評測集＋答案品質**：孫子×企管、漿料×材料×電子等；成功＝可引用終態＋guard 過，非 IC／非可交易。  
3. **gov 自動審批狀態機（覆蓋軸）**：釐清現行來源審批轉移；設計**可自動／須人裁**邊界；與 FT-COV 分桶、HAR-ext、license 三軌對齊。  
4. **整合**：跨域作答依賴「可答終態」庫存 → 自動推進只啃 pending／已文未嵌，**不放寬版權、不自動活化未審來源**。

### 1.2 Why

- Steward 定錨：know-how **相關性跨域**——分域閘會系統性擋住「古典×現代管理／材料×電子」類最佳回答。  
- `/gov` 已呈現審批分佈＋FT-COV 四欄；治理缺口（bulk-seed active 無人追認）與 pending 巨量並存——需要**狀態機語言**把「人該裁什麼／機器可推進什麼」說死，避免假自動綠。  
- 跨 ≥3 模組（retrieval／RBAC／harvest／gov／fulltext／promote）且碰決策層邊界 → #20 計畫先行。

### 1.3 非目標（硬紅線）

| 不做 | 理由 |
|---|---|
| **解凍 FinMind／FRED**／市場 sync／Dividend 重建 | API 凍結；本計畫零市場 API（`FZ-keep`） |
| **預測熱路徑吃 know-how**／灌因子／進 feature／panel | #8／`import_isolation`；素養層隔離 |
| **近程異域進化閉環灌因子**（孫子↔ERP、太陽能↔儲能等） | HANDOFF 近程紅線；見 §1.4 正交說明 |
| **自動 `approve`／`activate`／`resume`／`reopen` 來源** | 憲章 v1.41.0「approve 唯人」；TTY＋superuser；AI／腳本 fail-closed |
| **把 blocked（skip_license／skip_no_oa）洗成全文** | 能抓≠該抓；FT-COV 明示 |
| **改全文准入三軌／鬆 license CHECK** | 治權 [N]；另開案 |
| **本輪實作 code** | Steward：只出計畫 |

### 1.4 與「近程不做異域進化閉環」正交（必讀）

| | **本計畫主張** | **HANDOFF 近程紅線** |
|---|---|---|
| 是什麼 | 顧問／素養：**跨域檢索作答**（引用孫子談企管、漿料談電子） | **不做**把他域進化結果**灌進台股預測因子**／開異域 PME 閉環計畫 |
| 不是什麼 | 不是把孫子向量當特徵權重；不是 ERP 列進 `prediction_values` | 不是禁止顧問回答跨域問題 |
| 機械鎖 | know-how 仍住 knowledge／advisor；`import_isolation`＋test_philosophy_isolation 不鬆 | 進化閉環／factor_map／#14 提拔另案；本計畫 **U 階段不接** |

**一句**：跨域＝**讀與答**；異域進化閉環＝**寫進預測**——正交、不衝突、本計畫不偷開後者。

---

## 2. 必做診斷：現況「分域」落在哪（實證）

### 2.1 落點總表（造成「孫子×企管」「太陽能漿料」答不出／被閘死的機制）

| # | 落點 | 住所（code） | 作用 | 對跨域作答的效應 |
|---|---|---|---|---|
| D1 | **`knowledge_item.domain`** | `varchar NOT NULL`；FK 政策上可延後 | 策展標籤＋**RBAC 授權邊界**＋歷史「因子鏈純度」語意 | 標錯／過窄授域 → 授權收窄後撈不到他域句 |
| D2 | **harvest 矩陣／`knowledge_domain_map`** | `harvest_knowledge.py`：未 map 的 OpenAlex field **天然排除**；`--domain X` 圈跑 | 入庫節奏分域 | 某域 pending 永不補 → 跨域題缺料（覆蓋問題，非檢索語意） |
| D3 | **`retrieve_items(..., domain=)`** | `philosophy/retrieval.py`：可選 `AND i.domain = %s` | **作答閘**（若呼叫端傳入） | 顯式單域＝跨域硬死 |
| D4 | **`clean_item_sql` RBAC** | `knowledge/corpus.py`：非 super → `domain = ANY(allowed_domains)`；空授＝`AND false` | **授權閘**（非策展） | Sole Steward／super 可跨域；窄 grant 群組則分域＝產品設計。**跨域目標預設對象＝Steward／廣授顧問身份** |
| D5 | **`retrieve_all`** | works 全登入公開＋public items 走 D4＋private 擁有者收窄；**本身不硬 filter 單一 domain**（D13 已定） | 合併檢索 | 跨域在「授權夠寬」時**架構上已可能**；失敗常在 D6／D7／終態不足 |
| D6 | **相關度閘 `relevant_citations`** | `advise.py`：詞重疊過濾；CJK→英譯 fallback | 防離題 confabulate | 過嚴＝真跨域命中被丟→誠實 decline；過鬆＝噪音引文→幻答 |
| D7 | **可答終態不足** | FT-COV：pending≈108k；多學術域 answerable≈0 | 無 embed 句＝無可引用 | 「答不出」常是**沒終態**，被誤讀成「分域哲學」 |
| D8 | **gov 覆蓋率分桶** | `serve_admin_console.py` `_gov_data`（FT-COV-DASH 已改四欄） | **儀表**按 domain | 不直接閘答；但誘導「按域補洞」思維——與跨域檢索正交，可保留為診斷標籤 |
| D9 | **embedding collection** | `embedspec`／`sentence_items` 等；payload 可帶 domain scalar | 索引 | HNSW＋**post-filter domain** 曾有「過濾後 0 列」陷阱（handoff_memory）；跨域去閘後應 **pre-filter 勿過度、或 RRF 多路再收斂** |
| D10 | **來源審批 `approval_status`** | `curation.TRANSITIONS`；staging trigger 非 active 拒寫 | **能抓≠該抓**機械閘 | 未 active 源進不了 staging——正確；**與作答 domain 無關**，但自動審批若誤觸升級＝紅線 |
| D11 | **guard／ultracode「機械可驗域」** | deliberate oracle；frontend backbone F3：來源審批＝母幹化**前置**、green 唯人 | 審議 | 可自動的是**前置報告**，不是批准本身 |

### 2.2 來源審批狀態機（現行——`/gov` 呈現之「審批狀態機分佈」）

**狀態集**（`chk_ks_approval_status`）：

`proposed` → `approved` → `active` ⇄ `suspended` → `exhausted`；另 `rejected`；`reopen` 特例。

**轉移表**（`src/augur/knowledge/curation.py` `TRANSITIONS`）：

| action | 合法舊態 | 新態 | 誰可執行 |
|---|---|---|---|
| `approve` | proposed | approved | **HUMAN_ONLY**（TTY＋`app_user.is_superuser`；近 30 日 probe 200，local_file／sftp 豁免） |
| `activate` | approved／suspended | active | **HUMAN_ONLY**（同上） |
| `suspend` | active | suspended | 人 **或** `system=True`（harvest 降級） |
| `resume` | suspended | active | **HUMAN_ONLY** |
| `exhaust` | active | exhausted | （系統／人；非 HUMAN_ONLY 升級集） |
| `reject` | proposed | rejected | 人 |
| `reopen` | exhausted／rejected | active／proposed | **HUMAN_ONLY**＋reason |
| `probe`／`ratify`／`propose`／`edit` | （帳本動作） | 多半不改態或追認 | probe＝可腳本；**ratify＝人 TTY 批次追認**（不動狀態、補治理覆蓋率） |

**三層閘**：① CLI 身分（TTY＋superuser）② `chk_ks_active_needs_approval`（approved／active ⇒ `approved_by NOT NULL`）③ staging `BEFORE INSERT`：非 `active` 源 RAISE（`manual_file` 豁免）。

**`/gov` 行為**（`serve_admin_console.py`）：**唯讀**——審批分佈、governed_active／active、FT-COV 四欄、fulltext status、近 15 筆 `knowledge_source_review_log`；升級只印 copy-ready CLI，**web 零寫**。

**治理覆蓋率**：`governed`＝review_log 曾有 `approve`／`activate`／`ratify` 的 distinct source；`< active` 時頁面警告 bulk-seed 無真人留痕——**合法路＝人跑 `--ratify-all-active`，禁止自動 approve 灌覆蓋率**（CLI docstring 已寫死）。

### 2.3 覆蓋／終態狀態機（現行——與「審批」不同軸）

對齊 FT-COV §3（每 item，可聚合 per-domain **標籤**）：

| 桶 | 定義 | 可否自動推進 |
|---|---|---|
| **answerable** | 有 `item_text` 且至少一句已 embed | 目標終態（可引用） |
| **terminal_blocked** | 無 text、有 `knowledge_fulltext_status`（skip_license／skip_no_oa…） | **誠實終態**；不得洗全文 |
| **pending** | 無 text、無 status | **唯一應啃的自動池**（在源已 active＋授權下） |
| （隱）ft_no_sent／sent_no_emb | 有文未句／有句未嵌 | **庫內自動**（FT-COV-EMBED 已 CLOSED 先例） |

### 2.4 「最佳回答」成功定義（非 IC／非可交易）

1. **跨域召回**：單次查詢可同時命中 ≥2 策展 domain 之相關句（或 works＋items），且通過 `relevant_citations`。  
2. **誠實引用**：`verify_verbatim`＋guard 引文／出處閘過；禁幻造書名／數據。  
3. **license 終態**：引用列屬三軌允許之可檢索終態，或誠實 decline／「僅 metadata／blocked」。  
4. **非目標指標**：不評 IC／Sharpe／可交易；評測集人工／半自動打分即可。

### 2.5 對照既有

| 既有 | 關係 |
|---|---|
| `augur_omniscient_advisor_plan_20260709.md` | 十段鏈已 BUILT；強調隔離＋接線。跨域本計畫＝在其檢索／相關度層**去作答分域閘**＋評測，不重造管線。若仍待拍板，本檔拍板碼可**並採**「跨域增量」而不綁死全能計畫全文。 |
| FT-COV／HAR-ext（2026-07-28） | DASH＋EMBED＋HAR-ext／BATCH 近程 **CLOSED**；本計畫**消費**其分桶與有界 OA 先例，自動審批＝把「可重複推進」狀態機化，不另開市場 API。 |
| soul↔raw | 作答引用＝raw 觀測呈現；跨域相關性＝概念交互——**不**把整庫 raw 升格靈魂 [N]。 |
| CLAUDE #29 | source→acquire→staging→promote→（license）fulltext→sentences→embed；「完成」＝license 允許終態。自動審批只加速此鏈之**執行段**。 |
| frontend ultracode backbone F3-B／C | 來源審批／staging 疑難＝**panel 前置＋人終裁**；與本計畫「自動≠approve」一致。 |

---

## 3. 架構

### 3.1 統一 know-how 檢索空間（顧問）

```
query
  →（可選）query 擴展：原文 + 譯文 + 輕量別名（DB topic_alias 類，#29b；禁硬編碼大表）
  → hybrid：exact concordance ∪ ANN（pgvector／factory）
  → RRF／交錯合併（works ∪ public items ∪ private）
  → RBAC（D4：授權邊界保留；Steward／super 預設跨域）
  → **不**傳 `domain=` 作答閘（D3 預設關閉；除明示「只搜某標籤」UI）
  → relevant_citations（調參：跨域題允許較寬但保 min_terms）
  → prompt + guard
```

**`domain` 角色重劃**：

| 用途 | 保留？ | 說明 |
|---|---|---|
| 策展／harvest 圈選／覆蓋儀表 | ✅ | 標籤；gov 仍可 per-domain 診斷 |
| RBAC `group_domain_grant` | ✅（產品邊界） | 多租戶隔離；Sole Steward 廣授或 is_super |
| 因子鏈「investment 唯一」 | ✅（預測側） | **與顧問檢索分離**；顧問跨域不改預測 domain 純度 |
| `retrieve_items(domain=)` 預設 | ❌ 關閉 | 僅「用戶勾選標籤過濾」時開啟 |

### 3.2 自動審批狀態機（覆蓋／執行層）——設計原則

**命名消歧（拍板時必讀）**：

- **來源審批狀態機**（`knowledge_source.approval_status`）＝**決策層**；升級 **永不自動**。  
- **覆蓋終態狀態機**（item 級 answerable／blocked／pending＋管線游標）＝**執行層**；本計畫「自動審批」**只指這一軸**（可稱 **Auto-Terminal Advance，ATA**），避免與 approve 混淆。  
- **可選**：審議引擎對 proposed 源產「建議書」＝自動**建議**、非自動**批准**（F3-B）。

#### 3.2.1 可機械自動／拒絕／escalate

| 對象 | 自動核准（執行） | 自動拒絕／誠實終態 | Escalate 人裁 |
|---|---|---|---|
| pending item（源已 active；DOI／resolver 具備；HAR-ext 節奏內） | 跑 `fetch_oa_fulltext`（或 PD resolver）→ 寫 text **或** status | license／OA 不符 → `skip_*` 終態（非失敗） | 灰區 license、疑似 NC 誤標 |
| 有文未句／未嵌 | `build_sentences`／`embed_knowledge` | CLEAN 排除／junk pattern | — |
| staging 列（源 active；mapping 確定；norm_doi 無衝突） | `promote_knowledge` 冪等 | 重複／黑名單 AI | dedupe 邊界、domain **標籤**歸屬爭議、license 疑義 |
| proposed→approved／active | **禁止自動** | — | 一律人；可附 panel 前置報告 |
| 治理覆蓋率 ratify | **禁止自動** | — | 人 `--ratify-all-active` |
| 新 domain／新 source_key 納入 harvest map | **禁止自動** | — | 能抓≠該抓；決策層 INSERT |

#### 3.2.2 與 FT-COV／HAR-ext／三軌

- ATA 的 KPI＝**終態完成率**↑（answerable＋blocked）／items，**不是** gov 舊 length>200％。  
- HAR-ext 已 CLOSED 的有界批次＝ATA 的**授權先例**；後續放量仍要節奏碼（或 Steward 新句），ATA 引擎本身不解凍市場 API。  
- 全文寫入仍過 LICENSE_WHITELIST／owned_local⇒local_private。

#### 3.2.3 domain 降標籤後，審批按什麼切？

| 狀態機 | 切分鍵 | 說明 |
|---|---|---|
| 來源審批 | **`source_key`** | 全局／按來源；**不按 domain 批准** |
| ATA 終態推進 | **item_id**（可選 filter：source_key、legacy domain **標籤**僅作排程優先序） | 「先啃 medicine pending」＝排程策略，非作答閘 |
| gov 儀表 | 仍可 **GROUP BY domain 標籤** | 診斷用；headline＝可答／終態％ |

---

## 4. 整合點（跨域 × ATA）

1. **跨域檢索依賴可答終態** → ATA 優先把「跨域評測集會打到的源／標籤池」之 pending／未嵌推到 answerable｜blocked，避免「檢索去閘了但仍全 decline」。  
2. **評測集驅動排程**：S2 題目反查缺句 → 回填 ATA 佇列（執行層），**不**因此自動 activate 新源。  
3. **相關度閘與噪音**：去 domain 閘後噪音↑ → S3 調 `relevant_citations`／RRF／可選「標籤加權不硬濾」；ATA 不負責降噪。  
4. **RBAC**：跨域作答預設在 Steward／super 或「knowhow_broad」grant；窄 grant 產品行為另文件化，不與「know-how 不分域」哲學衝突（哲學＝庫內相關性；產品＝誰被授權讀哪些標籤）。  
5. **gov 頁演進（拍板後）**：保留審批分佈＋四欄；增「ATA 佇列／最近自動推進／escalation」唯讀塊；**仍零寫 approve**。

---

## 5. 分階段（共同分階；交叉依賴）

| 階段 | 名稱 | 內容 | 依賴 | 驗收摘要 |
|---|---|---|---|---|
| **S0** | 診斷帳 | 固化 D1–D11；重跑 PG 對帳；列「作答曾傳 domain=」呼叫點；審批／ATA 兩軸狀態圖入 repo | 無（唯讀） | 報告數字可複現；呼叫點清單完整 |
| **S1** | 檢索去作答分域閘 | 預設關閉 D3；Steward 路徑 RRF／hybrid；文件化 RBAC≠策展；**不**改 HUMAN_ONLY | S0 | 孫子×企管類 query 在授權夠時可命中多標籤句（或誠實缺料，非 domain= 空） |
| **S1b** | ATA 骨架 | 新／薄編排：讀 pending｜ft_no_sent｜sent_no_emb → 呼叫既有 script；寫 `knowledge_*` 帳本或复用 build_meta；**禁**呼叫 approve／activate | S0；FT-COV 工具 | dry-run 清單；system 觸 HUMAN_ONLY → 必 FAIL 測試 |
| **S2** | 跨域評測集 | 題集（孫子×企管、漿料×材料×電子、…）＋自動跑 retrieve／advise 記 citations domains | S1 | ≥N 題有多 domain 命中或標註缺終態 |
| **S2b** | ATA 對準評測缺口 | 依 S2 缺料排程有界 fetch／embed（沿 HAR-ext 節奏；新放量另碼） | S1b＋S2；外部需授權 | 評測缺料題終態完成率↑ |
| **S3** | 答案品質／引用 | 調相關度；guard 回歸；引用 UI／出處 | S1＋S2 | 幻答↓；verbatim 過；空庫 decline 穩 |
| **S3b** | gov 整合呈現 | ATA 進度＋escalation 佇列上 `/gov`；審批 CLI 連結不變 | S1b | 唯讀；無 web approve |
| **U** | 凍結／回歸 | import_isolation；approve 唯人測試；跨域評測基線；**不**接異域進化閉環 | 上列近程綠 | 紅線測試全綠 |

**建議近程一次拍**：`KH-XDOM-P01`＝S0＋S1＋S1b（零市場 API；OA 僅用既有已授權節奏或 dry-run）；S2＋以後另碼或同包擴充。

---

## 6. Schema／Python 規畫（憲章計畫完整性）

### 6.1 表（預設不產新表）

| 物件 | 角色 | 本計畫 |
|---|---|---|
| `knowledge_item`／`.domain` | 策展標籤 | 讀；不改語意為作答閘 |
| `knowledge_item_text`／sentences／embeddings | 可答終態 | ATA 寫（既有 writer） |
| `knowledge_fulltext_status` | blocked 終態 | ATA 寫 |
| `knowledge_source`／`approval_status` | 來源審批 | **只讀**（除人 CLI） |
| `knowledge_source_review_log` | 審批軌跡 | 人／probe／ratify；ATA **可**另寫 action=`ata_advance` 類（若欄位允許）或獨立帳本 |
| `knowledge_staging` | 晉升上游 | 機械 promote；疑難 escalate |
| `knowledge_domain`／`group_domain_grant` | RBAC | 不廢；跨域靠授寬／super |
| `knowledge_domain_map`／`knowledge_query` | harvest | 新域仍人 INSERT |
| `deliberation_*` | 前置建議 | 可選接 F3-B／C（零寫目標表） |

**可選新表（僅當 review_log 不宜塞 ATA）**：`knowledge_terminal_advance_log`（item_id, from_bucket, to_bucket, script, evidence_json, created_at）——S1b 定案；**非必須**才能開工（可先 stdout＋既有 build_meta）。

### 6.2 Python／腳本落點

| 檔 | 角色 | 階段 |
|---|---|---|
| `src/augur/philosophy/retrieval.py` | 去預設 domain 閘；RRF／合併 | S1 |
| `src/augur/advisor/advise.py`／`relevance.py` | 跨域相關度調參 | S1／S3 |
| `src/augur/knowledge/corpus.py` | RBAC 不變；文件註解區分標籤／授權 | S1 |
| `src/augur/knowledge/curation.py` | **不改** HUMAN_ONLY；可加 selftest「ATA 不得 import 升級」 | S1b |
| `scripts/review_knowledge_source.py` | 人閘不變 | — |
| `scripts/serve_admin_console.py` | `/gov` ATA 唯讀塊 | S3b |
| **新** `scripts/advance_knowledge_terminal.py`（建議名） | ATA 編排：`--dry-run`／`--apply`／`--limit`；只 subprocess 既有 fetch／build／embed／promote | S1b |
| **新** `scripts/eval_cross_domain_advisor.py` | 評測集跑分 | S2 |
| `scripts/fetch_oa_fulltext.py` 等 | 被 ATA 呼叫 | S2b |
| `tests/test_philosophy_isolation.py`＋新測 | 隔離＋禁自動 approve | U |

**強制不變式**：predict 零 import knowledge；ATA `system` 路徑呼叫 `transition(..., approve)` → 測試必須紅；license CHECK 不鬆。

---

## 7. 風險

| 風險 | 緩解 |
|---|---|
| 檢索噪音／離題引文↑ | RRF＋relevant_citations 調參；評測回歸；必要時「標籤加權」非硬濾 |
| 假自動綠（以為來源已治理） | governed 與 ATA 進度分欄；禁止自動 ratify／approve |
| 跳過人裁／Sole Steward 衝突 | HUMAN_ONLY 機械鎖＋紅燈測試；審議只產建議書 |
| 版權／能抓≠該抓 | blocked 終態；新源／新域人拍；不放寬三軌 |
| 幻答 | guard＋空檢索 decline；相關度過嚴寧可 decline |
| 與異域進化閉環混淆 | §1.4 寫入驗收 U；HANDOFF 紅線不改 |
| HNSW post-filter 空結果 | 避免 ANN 端硬 domain filter；過濾放 PG CLEAN／RBAC |

---

## 8. 驗收

| ID | 條件 | 否證 |
|---|---|---|
| V-XD1 | Steward／super 路徑預設檢索**無**強制單 domain | 仍預設 `domain=` |
| V-XD2 | 評測集含孫子×企管；有終態時可多標籤引用或可解釋缺料 | 有料仍因 domain 閘空 |
| V-XD3 | guard／verbatim 回歸綠；幻造書名擋 | 鬆 guard 換「流暢」 |
| V-ATA1 | ATA dry-run／apply **從不**改 `approval_status` 升級 | log 出現 auto-approve |
| V-ATA2 | pending→answerable｜blocked 可複現；blocked 不灌全文 | skip_license 被改寫全文 |
| V-ATA3 | `/gov` 可區分來源治理覆蓋 vs 終態完成率 vs ATA 進度 | 單一％誤導 |
| V-ISO | `import_isolation`＋philosophy isolation 綠 | know-how 進 predict |
| V-ORTH | 文件與 U 測試聲明不做異域進化灌因子 | 接上 factor_map 當本計畫交付 |

---

## 9. Steward 拍板碼（建議組合）

| 碼 | 含義 | 建議 |
|---|---|---|
| **`KH-XDOM-PLAN`** | 採納本整合計畫 what／非目標／正交／分階 | 必拍 |
| **`KH-XDOM-S01`** | 開工 S0＋S1＋S1b（檢索去閘＋ATA 骨架；零市場 API） | 近程建議 |
| **`KH-XDOM-EVAL`** | S2 評測集＋跑分腳本 | 可併或次拍 |
| **`KH-ATA-EXEC`** | S2b ATA 對準缺口之有界外部 fetch（知識 OA；**≠**解凍 FinMind／FRED） | 須明示；可沿用／延伸 HAR-ext 節奏 |
| **`KH-XDOM-QUAL`** | S3＋S3b 品質與 gov 呈現 | 次拍 |
| **`FZ-keep`** | 市場 API 維持凍結 | 預設附帶 |
| **`PME-XDOM-NO`** | 確認近程**不做**異域進化閉環灌因子（正交鎖定） | 建議與 PLAN 同句 |

**建議合併拍板句（示意）**：  
`KH-XDOM-PLAN`＋`KH-XDOM-S01`＋`PME-XDOM-NO`＋`FZ-keep`（S2／ATA 外部另句或同包加 `KH-XDOM-EVAL`）。

**人裁邊界（一句）**：來源活化／追認／新域納入／license 灰區／治權判準＝**人**；pending 終態推進／庫內 embed／確定 mapping 之 promote＝**可自動（執行層）**。

---

## 10. 回報摘要（給拍板頁）

| 項 | 內容 |
|---|---|
| **路徑** | `reports/augur_knowhow_cross_domain_advisor_plan_20260728.md`（本檔；含審批整合章，無須另檔） |
| **跨域一句** | know-how 作答不分域閘，追求跨域最佳回答（引用＋誠實） |
| **自動審批一句** | 自動的是**覆蓋終態推進（ATA）**，不是來源 approve |
| **建議拍板** | `KH-XDOM-PLAN`＋`KH-XDOM-S01`＋`PME-XDOM-NO`＋`FZ-keep` |
| **正交** | 跨域檢索作答 ≠ 異域進化灌預測因子 |

---

## 11. 修訂／對照

| 日期 | 說明 |
|---|---|
| 2026-07-28 | 初版：跨域顧問＋gov ATA 整合；對照 FT-COV／omniscient／HANDOFF；本輪不實作 |

**姊妹互鏈**：FT-COV＝`reports/augur_knowledge_fulltext_coverage_plan_20260728.md`；全能顧問＝`reports/augur_omniscient_advisor_plan_20260709.md`；HANDOFF 近程「不做他域進化閉環」。
