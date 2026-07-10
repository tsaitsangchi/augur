# augur 全球知識庫深度抓取計畫 v2(2026-07-10)

**檔名(建議落點)**:`reports/augur_knowledge_deep_harvest_plan_20260710.md`(CLAUDE #16 命名)
**狀態**:v2=四鏡對抗審查(doctrine/completeness/engineering/ops)修訂版——6 blocker+25 major+16 minor 全數修入,發現與處置全表見 §9;待用戶拍板(#20 計畫先行;拍板點 P0-P12 見 §8)
**上游治權**:憲章 **v1.40.0**「知識層多域擴充準則」(:146)+「全文准入三軌」(v1.36.0 條文)+ 共同不變式①-④(:142)+ 隔離不變式 + 隱私上限(:166)(行號 2026-07-10 grep 實查);CLAUDE #24/#25/#28/#29
**下游邊界**:本計畫終點=`knowledge_staging`/`knowledge_item`/`knowledge_item_text` 落庫。之後的 sentences→concordance→embed→milvus/Qdrant→qwen→UI 屬「端到端主計畫」既有 S2+ 段(`refresh_knowledge_pipeline.py` 八段 DAG 已通),**本計畫不重複規劃下游**。
**憲章登錄慣例**:定稿後依憲章詳計畫登錄慣例將本檔登錄為知識層詳計畫 SSOT;若 §3 之審批狀態機被視為架構準則變更,同步憲章一行(**v1.41.0**——現行檔已是 v1.40.0,原擬 v1.40.0 撞號已更正;拍板點 P0)。

---

## 0. 三十秒摘要與「想辦法抓到」之合法解框架

### 0.1 三十秒

用戶要求「知識層從全世界知識庫**深度抓取**——想辦法就是要抓到」。實查現況:協定層已世界級(13 adapters、6 類協定),但**查詢矩陣極稀疏**(3,593 列 knowledge_source 中真正掛模板且 enabled 的查詢型來源僅 25;4,709 條 query 有 ~3,027 條因 domain_map 未拍板而閒置)、**公開全文近乎為零**(item_text 中 cc-by 800 + cc-by-sa 7 段,對比 owned_local 150,685)、**限速/審批/儀表三件治理機件全缺**。

本計畫=四件事:
1. **來源目錄驅動**:把「世界知識庫宇宙」窮舉成資料列(擴充 `knowledge_source` 為單一 SSOT 目錄,含 license_regime/限速/配額/波次/審批狀態/abstract 政策欄),3,507 個 re3data stub 即現成候選池;
2. **波次推進**:Wave 1 放大查詢矩陣(INSERT 資料列)→ Wave 2 新協定 adapter(OAI-PMH)+全文深化(PDF 抽取/公版書/CORE/OA 書籍)→ Wave 3 長尾(re3data 激活工作流、dump loader);
3. **人拍板閘機械化**:審批狀態機 `proposed→approved→active→suspended/exhausted` 落 DB;**非 active 之源被三層 fail-closed 機械閘擋於庫外——(一)harvest/acquire 排程 SQL 閘、(二)promote 入庫 JOIN 閘、(三)`knowledge_staging` BEFORE INSERT trigger(§3.7)**;審批動作走 admin 控制台(:8500)或具身分閘之 CLI(TTY 檢查+superuser 對映,§4.1)並留痕;**approve/activate 屬決策層動作,AI 永不自行執行(同 #14 commit/push 級授權邊界)**;
4. **#24 對偶機械化**:per-source pace/**視窗額度閘(quota gate,呼叫前原子計數,達 90% 即停至視窗重置)**/cooldown 住 DB,引擎讀表執行、honor Retry-After、見訊號即停;**temp 錯走 cooldown 指數階梯自癒(15m→24h 封頂)、perm 錯才 auto-suspend**;健康度持久化;**跨行程 advisory lock 互斥(pace 不被併行進程稀釋)**。

全程本地 Python + PostgreSQL,零 Claude token(#28)、純 CPU+I/O、776G 磁碟上界內配額。

### 0.2 「想辦法抓到」的合法解框架

「想辦法」的解**不是**繞 license,而是**窮舉合法面積再逐格填滿**:

```
抓取面積 = Σ(來源宇宙每一源) × 該源合法深度
  ├─ A 軌 公版源     → 全文逐字入庫(license='public_domain';逐件判定規則表 P7、OCR 政策 P8)
  ├─ B 軌 CC 白名單源 → 逐篇 license ∈ {cc-by, cc-by-sa, cc0} 才入全文;NC/ND/未明→停 metadata;
  │                     任意上傳型/dump 型之全文另受 P9(上游 AI 文本)獨立拍板
  ├─ C 軌 版權學術源  → metadata + abstract(依 abstract_policy 欄逐源 ToS 裁決)+ OA 副本路徑
  │                     (Unpaywall/CORE)過白名單才入全文
  └─ (owned_local 軌不經任何外部 adapter,只走本機匯入,與本計畫外抓管線完全隔離)
```

現況最大未填面積(按 ROI 排序):
| 缺口 | 現況 | 合法填法 |
|---|---|---|
| 查詢矩陣閒置 | ~3,027 條 query 無域映射、專業域僅 193 條 manual query | domain_map 拍板 + 專業域 query 策展(零新碼) |
| PDF 全文跳過 | fetch_oa_fulltext 對 PDF 一律 skip_pdf(既有終態帳 448 筆) | pdfminer 逐字抽取(license gate 不變,拍板 P3)**+落地後一次性 requeue 既有 skip_pdf** |
| 公版書全文(knowledge_item_text 側)未接 | **更正(四鏡實查)**:repo 已有五支公版全文 fetcher 落 `philosophy_work_text`(柏拉圖全集/國富論/Reminiscences 等已在庫);knowledge_item_text 側未接,**雙落點分工未裁決** | 新 `fetch_pd_fulltext.py` + **分工裁決與同書去重閘(拍板 P10,§4.3)** |
| 投資/經濟域 A 軌富礦全缺 | FRASER/FOMC/EDGAR/CRS 政府公版全文、DOAB/OAPEN OA 學術書全文未列 | §1 政府公版子表 + B 軌書籍源(多為 generic_json 資料列=近零新碼) |
| 15 個具名源模板 NULL | repec/pubmed/core/opencitations… 停擺 | 補 query_template + probe + 人審(**probe 後定案:pubmed/biorxiv 屬新機制移 W2,非全數零新碼**) |
| OAI-PMH 協定缺 | BASE/OpenAIRE/World Bank OKR 抓不到 | 新 adapter 一枚(#29b)+ **durable datestamp 游標**(§3.5) |
| re3data 3,507 stub 死庫 | enabled=false、模板全 NULL、無啟用工具鏈 | activation 工作流(URL 驗證+probe→補模板→人審;首輪批次範圍拍板 P11) |

**能抓≠該抓的機械化**:每一源(**含全文通道 pseudo-source,§1 F 軌**)從「目錄中的一列」到「進 harvest 排程/入庫」之間,必經人按下 admin 控制台的 approve 鈕或具身分閘之審批 CLI——上述**三層 fail-closed 機械閘**(排程 SQL+promote JOIN+staging trigger;誠實註明殘餘面:superuser 直接 psql 改 DB 不在防線內,那屬決策層自身行為)。這是治權硬閘「新來源入庫=決策層人拍板」的機械落地,本計畫不鬆動它,只讓它從「psql 手工 UPDATE enabled」升級為「有留痕、有 probe 證據、有 UI 的工作流」。

**「想辦法抓到」永遠不含**:影子圖書館(Sci-Hub/LibGen/Anna's Archive/Z-Library 及同類)、繞 robots.txt/ToS 之 HTML 爬蟲、帳號牆/付費牆內容——負面清單與 URL allowlist 機制見 **§6.2-8**;**KPI 永不凌駕 gate**(達不到=誠實回報缺口,不放寬判準)。

---

## 1. 世界來源目錄(source universe)

以下為 `knowledge_source` 目錄擴充後的填充內容(§3 DDL 之資料面)。**pace 初值全為保守起點**,依 CLAUDE #27 逐級逼近、重覆驗證後才回填更優值;**quota 值=各源官方 ToS/文件明文上限**(來源可溯 #10),引擎以 §4.2 quota gate 機械執行;「預估規模」為公開資訊之計畫估算(非實測 metric,落庫數以 harvest 帳本為準,#9)。**全部來源之 endpoint 僅限 registry 內宣告(URL allowlist,§6.2-8);新 endpoint=新拍板。**

### A 軌:公版全文源(`license_regime='public_domain'`,fulltext_eligible=true)

> **全文來源分級**:A 軌首波全文僅限「有編輯/策展閘」之來源;**逐件公版判定規則表=拍板 P7、OCR 政策=拍板 P8**(未拍板前 OCR 文本路徑不啟動)。

| 來源 | 協定 | adapter 對映 | domain | 波次 | pace 初值 | 預估規模 | 備註 |
|---|---|---|---|---|---|---|---|
| Project Gutenberg | REST-JSON(gutendex)+官方 mirror/catalog dump | `gutendex`(既有)+ `fetch_pd_fulltext` | general/philosophy | W1 放大 + W2 全文 | 1.0s | ~75,000 部 | **PG 主站明文禁機器人批量直抓(違者 IP ban)**:全文一律走官方 mirror(rsync/harvest 介面)或 RDF/CSV catalog dump 離線解析,**零 gutenberg.org 主站批量直抓**;metadata 放大查詢改自架 gutendex(官方開源)或 catalog dump(gutendex.com 為社群小服務,不對其放量);逐本 gate=gutendex `copyright=false` 才入(P7 規則表) |
| Wikisource | MediaWiki API / dump | `generic_json` 新列(W2);dump(W3) | philosophy/general | W2 | 1.0s | 多語公版原典 | 僅收「**原著+譯者皆逾版權期**」之頁——license 模板**機讀**判定,判不動→skip 記帳(P7);CC-BY-SA 當代譯本層不入 A 軌;中英哲學經典原文首選 |
| Internet Archive | scraping API | `internet_archive`(既有) | general | W1 放大(metadata) | 1.5s | 數百萬卷 | 全文僅 `licenseurl` 明示 PD/CC0 之卷(possible-copyright-status 出名不可靠,不作依據);`_djvu.txt`=Abbyy **OCR 產物、非 born-digital 逐字原文**→是否入庫屬 **P8 拍板,未拍板前 IA 全文路徑不啟動** |
| Kanripo 漢籍 | GitHub raw/API | `generic_json` 新列 | philosophy | W2-W3 | 1.0s | 漢籍公版原典 | 中文原典補強(與 Wikisource 中文互補);逐 repo 判公版(P7) |
| Aozora 青空文庫 | REST/CSV 目錄 | `generic_json`(既有 `aozora_books`) | general(日文) | W2 | 1.0s | ~17,000 部 | backfill 後排程唯一閘=approval_status(enabled 已退役,§3.2),activate 即入排程;全文路徑走 fetch_pd_fulltext |
| HathiTrust | Bib API / Data API | `generic_json`(`hathitrust_bib`,模板 NULL) | general | W3 | 1.0s | 17M+ 卷 | 公版卷全文需申請 research access(外部副作用,P12 逐項拍板) |

**A 軌政府公版子表(新增;美國聯邦政府著作=公版,投資/經濟域最大 A 軌富礦)**:

| 來源 | 協定 | adapter 對映 | domain | 波次 | pace 初值 | 備註 |
|---|---|---|---|---|---|---|
| FRASER(St. Louis Fed) | REST-JSON API | `generic_json` 新列 | economics/finance_mgmt | W2 | 1.0s | 金融經濟史數位圖書館(全文);聯邦公版為主,逐件 rights 欄判定(P7) |
| Fed/FOMC 歷史文獻 | REST/bulk(多經 FRASER 涵蓋) | `generic_json` 新列 | economics | W2 | 1.0s | 會議記錄/聲明/報告,聯邦公版 |
| SEC EDGAR 全文 | REST-JSON(full-text search/bulk) | `generic_json` 新列 | investment_mgmt | W2 | 0.5s | 10-K/股東信等公開申報文件;SEC fair-access 政策要求宣告 User-Agent、上限 10 rps(取保守 0.5s) |
| CRS 報告 | REST(crsreports.congress.gov) | `generic_json` 新列 | economics | W3 | 1.0s | 國會研究處報告,聯邦公版 |

### B 軌:CC 白名單全文源(`license_regime='cc_whitelist'`,逐篇 gate)

> **全文來源分級(P9)**:首波 fulltext 僅限**有編輯/策展閘**之源(PLOS/PMC OA/World Bank OKR/DOAB/OAPEN/公版原典);**任意上傳型(Zenodo)與 dump 型(Wikipedia/Stack Exchange)之全文另立獨立拍板 P9**(上游 AI 文本風險;選項含 revision cutoff)。

| 來源 | 協定 | adapter 對映 | domain | 波次 | pace 初值 | 預估規模 | 備註 |
|---|---|---|---|---|---|---|---|
| DOAJ | REST-JSON | `generic_json`(`doaj_articles`,既有) | general | W1 | 1.0s | 2 萬刊 | 逐篇 CC 判 |
| PLOS | REST-JSON | `generic_json`(`plos_search`,既有) | 科學 | W1(metadata)/W2(全文 XML) | 1.0s | 全 OA CC-BY | 全庫 CC-BY,全文率最佳試點 |
| Europe PMC / PMC OA | REST-JSON | `generic_json`(`europepmc`,既有) | 生醫 | W1 / W2 全文 | 1.0s | OA subset 全文 XML | CC 逐篇;版權部分停 abstract(abstract_policy=allow,ToS 明文) |
| **DOAB** | REST-JSON | `generic_json` 新列(零新碼) | general | W2 | 1.0s | 8 萬+ OA 學術書目 | **B 軌書籍級缺口補位**;逐本 CC 判 |
| **OAPEN** | REST-JSON / OAI-PMH | `generic_json` 新列 / `oai_pmh` | general | W2 | 1.0s | 數萬本 CC 學術書全文 | 逐本 license gate;全文 PDF 走 P3 路徑 |
| **Perseus Digital Library** | REST/XML | `generic_json` 新列 | philosophy | W2-W3 | 1.0s | 希臘羅馬經典 | CC-BY-SA 編修文本,philosophy 域直接對口 |
| bioRxiv / medRxiv | REST-JSON | `generic_json`(`biorxiv_details`) | 生醫 | **W2** | 1.0s | preprints | **ID/日期區間驅動、無關鍵詞端點——不含 {query} 天然不入查詢排程**,改 W2 date-window 深抓型(cursor 表承接);多 CC-BY,NC 停 metadata;preprint 全文受 P9 分級 |
| Zenodo | REST-JSON | `generic_json`(`zenodo_records`,既有) | general | W1(metadata) | 1.0s | 混雜 | **任意上傳型(無編輯閘)=上游 AI 文本風險:metadata 先行,全文暫緩至 P9 拍板**;逐筆判 license |
| HAL(法國) | REST-JSON | `generic_json`(`hal_france`,既有) | general | W1 | 1.0s | 法國 OA 檔案 | 部分 CC |
| World Bank OKR | OAI-PMH / REST | **`oai_pmh`(新,W2)** | economics | W2 | 1.5s | CC-BY 報告 | 開發經濟全文可入,投資域相鄰;有編輯閘=首波全文合格 |
| CORE | REST-JSON | `generic_json`(`core_uk`,模板 NULL)+ fulltext 後援 | general | W2 | 2.0s(5req/10s) | 3 億篇聚合 | **需註冊 API key(拍板 P4)**;全文逐篇 license;quota=免費層日額(註冊後以官方數值回填) |
| Wikipedia | XML dump | **`dump_loader`(新,W3)** | general | W3 | —(本地解析) | dump 壓縮 ~20GB+/語言 | CC-BY-SA;選域抽取(P6);**2022-11 後條目含 AI 生成風險→是否入庫+revision cutoff=P9 拍板**(`--revision-before` 參數已規劃) |
| Stack Exchange dump | 7z XML dump | **`dump_loader`(新,W3)** | general | W3 | — | ~百 GB 級 | CC-BY-SA 4.0;官方 2023 停傳 archive.org、取得管道與非商用條款須人審(P6);AI 答案風險=P9 |

### C 軌:metadata-only 學術骨幹(`license_regime='metadata_only'`,fulltext_eligible=false;全文僅經 OA 副本路徑)

| 來源 | 協定 | adapter 對映 | 波次 | pace 初值 | 預估規模 | 備註(quota/abstract_policy) |
|---|---|---|---|---|---|---|
| OpenAlex | 專用 REST | `openalex`(既有) | W1 放大 + W2 cursor 深抓 | 0.5s(polite mailto) | 2.5 億 works | CC0 metadata;**quota=100,000 calls/day+10 rps(官方明文)→quota_limit=100000/86400s**;超大批量走官方 snapshot;abstract 僅 inverted_index(不重組全文) |
| Crossref | 專用 REST | `crossref`(既有) | W1 | 1.0s | 1.5 億 DOI | polite pool 需 mailto;**abstract_policy='deny' 預設**——abstract 再利用權由出版社逐一設定、不可考(OpenAlex 正因此不發原文) |
| Semantic Scholar | 專用 REST | `semantic_scholar`(既有;key 已在 .env) | W1 | 1.0s(官方要求 exp backoff) | 2 億 papers | abstract 逐字可入(abstract_policy='allow',ToS 明文);**`tldr` 為 SciTLDR 模型自動生成=AI 內容,欄位級一律不取(不變式①,§6.2-1)** |
| arXiv | Atom-XML | `arxiv`(既有) | W1 | **3.0s(官方下限)** | 2.4M preprints | abstract_policy='allow';全文 bulk 屬 W3 候選 |
| PubMed E-utilities | REST-JSON | **兩段式 esearch→esummary(新機制,W2)** | **W2** | 0.4s(無 key 3 rps=quota) | 37M 引文 | **esearch 只回裸 PMID 列表,generic_json 單請求模型表達不了→移 W2 隨 pagination 機制落地**;abstract_policy='allow'(NLM) |
| Unpaywall | 專用 REST | `unpaywall`(既有;email 已在 .env) | 常設 | 0.5s | DOI→OA 裁決 | 全文路徑 license 裁決器,非內容源;**quota=100,000 calls/day(官方明文)→quota gate 必經;backlog >100k 一律走官方 DB snapshot(週更 dump,ToS 認可之 bulk 路),API 留增量** |
| OpenCitations | REST | `generic_json`(`opencitations`,NULL→W1 補) | W1 | 1.0s | 引文網 CC0 | probe 後定案 |
| DBLP | REST | `generic_json`(`dblp_cs`,既有) | W1 | 1.0s | CS 書目 ODC-BY | |
| INSPIRE-HEP / DataCite | REST | `generic_json`(既有) | W1 | 1.0s | | 既有續用 |
| BASE / OpenAIRE | OAI-PMH | **`oai_pmh`(新,W2)** | W2 | 1.5s | 3 億+ 聚合 | repository 宇宙入口;**durable 游標=datestamp 窗(§3.5),非 resumptionToken** |
| ORCID / NASA ADS / IEEE Xplore | REST | `generic_json`(NULL) | W3 | 1.0s | | NASA ADS 需 token(P12);IEEE ToS 嚴→候選降級(拍板) |
| Wikidata / DBpedia | SPARQL | `wikidata_sparql`/`dbpedia_sparql`(既有) | W1 放大 | 3.0s | 結構化骨幹 | 查詢矩陣續放大(獎項/人物/概念) |
| OpenLibrary | 專用 REST | `openlibrary`(既有) | W1 | 1.0s | 書目 CC0 | 連 IA 公版卷(W2 全文,受 P7/P8) |
| ctext 中國哲學電子化 | REST-JSON | `generic_json`(既有 `ctext_books`) | W1 續用(metadata) | 1.5s | 先秦兩漢諸子 | **自 A 軌移入本軌:license_regime='metadata_only'、fulltext_eligible=false**(API ToS 商用受限、非標準公版宣告);原典全文改道 Wikisource/Kanripo 公版本(P5 裁決留痕)——避免 backfill 照 A 軌表灌值成破軌口 |

### D 軌:投資/經濟域(**最高 ROI——現況 finance/investment 域各僅 2-7 列**)

> 政府公版全文富礦(FRASER/FOMC/EDGAR/CRS)見 **A 軌政府公版子表**——economics/investment 域最大公版面積在彼。

| 來源 | 協定 | adapter 對映 | 波次 | pace 初值 | 備註 |
|---|---|---|---|---|---|
| RePEc / IDEAS | REST | `generic_json`(`repec_ideas`,NULL) | W1(probe 後定案) | 1.0s | 經濟學最大書目庫;**API 需申請 token=外部副作用→拍板 P12**;probe 通過才 approve,目標值以 probe 結果回填(#9) |
| NBER working papers | REST/RSS | `generic_json` 新列 | W1 | 1.0s | metadata;全文 PDF 走 W2 OA 路徑 |
| World Bank OKR | OAI-PMH | `oai_pmh`(新) | W2 | 1.5s | CC-BY 全文(B 軌重列) |
| IMF / BIS / OECD papers | REST/OAI | `generic_json` 新列 / `oai_pmh` | W2 | 1.5s | 政策研究 metadata,多開放 PDF |
| **投資經典公版書單(pre-1930)** | 策展書單(定向 query+catalog dump) | 既有 adapter 資料列 | W2 | — | **專項策展書單=拍板**(併 P10 之 philosophy_work_text 既有書單盤點,避免同書重抓——Reminiscences/群眾瘋狂/國富論等已在庫);不靠 gutendex 主題查詢碰運氣 |
| SSRN | 受限 API | `generic_json`(`ssrn`,NULL) | **W3 或 retired** | — | Elsevier 所有、API 受限→保守降級(拍板) |
| FRED/ALFRED 關聯文獻 | — | — | W3 長尾 | — | 文獻價值有限 |

### E 軌:科學實體庫長尾(已運作續用;**domain 欄隔離、零量化價值不進預測管線**)

PubChem/UniProt/ChEMBL/GBIF/COD/ERIC(6 源,W1 續跑)、materials_project/nist_webbook/rcsb_pdb(NULL,W3 補)、**re3data 3,507 stub(W3 activation 工作流主體;probe 前置 URL 驗證+首輪批次範圍拍板 P11)**。

### F 軌:全文通道 pseudo-source(治理收編——全文抓取不得游離於審批/限速/健康度體系之外)

fetch_pd_fulltext/fetch_oa_fulltext 讀 `knowledge_item` 驅動、不經 query×source 排程——若無收編,「沒有任何源可以不經人手進入排程」對全文通道不成立(suspend 了 gutendex,工具照打 gutenberg.org)。故 **M3 一併 INSERT 五列 pseudo-source**(無 query_template,天然不入 harvest 排程;僅供全文工具查閘與記帳):

| pseudo-source 列 | 綁定工具 | 說明 |
|---|---|---|
| `gutenberg_files` | fetch_pd_fulltext | PG 官方 mirror/catalog 全文下載通道 |
| `ia_fulltext` | fetch_pd_fulltext | IA 卷全文(**P8 拍板前維持 suspended**) |
| `wikisource_files` | fetch_pd_fulltext | Wikisource 頁全文 |
| `core_fulltext` | fetch_oa_fulltext | CORE 後援(P4 後 activate) |
| `oa_publisher_pool` | fetch_oa_fulltext | OA 副本出版商散點(**per-host 分桶 pace**) |

每列同受 `approval_status`/`pace`/`quota`/`health` 治理:工具啟動先查對應 pseudo-source `active` 才跑、每呼叫記同一 health 表。repo 既有游離 fetch_*(fetch_gutenberg_classics 等五支)之收編/豁免裁決見 §4.3(P10)。

---

## 2. 波次推進設計

### Wave 0:治理基建(先行,無新來源)

**內容**:§3 DDL migration(M1-M5+trigger)+ §4 引擎改讀表(閘/pace/quota/互斥/cooldown)+ §5 admin 審批 UI。此波是後續一切的閘與儀表,**必先落地**——否則「放大」等於在無限速表、無審批留痕下放量,違 #24/治權閘。

**驗收**:
- **三層 fail-closed 實測**:(a) 排程層:`approval_status='proposed'` 之源在 harvest 排程組合數=0;(b) trigger 層:**psql 直插非 active 源之 staging 列必須失敗**(manual_file 豁免列須成功);(c) promote 層:人工塞入之非 active 源 pending 列不被 promote;
- **probe 無痕實測**:對 proposed 源 probe 後 `SELECT count(*) FROM knowledge_staging WHERE source_key=…` 增量=0;
- **quota gate 實測**:對 quota_limit=3 之測試源,第 4 次呼叫被閘(cooldown_until=視窗重置點);
- **互斥實測**:並行第二個 harvest 進程被 advisory lock 拒(回「已有 harvest 在跑」);
- **cooldown 自癒實測**:模擬 5xx 風暴→源進 cooldown 階梯、到期自動回排程(不被永久 suspend);
- pace 讀表實測:log 中相鄰兩次呼叫間隔 ≥ 該源 `pace_seconds`;probe 工具最小單位實測(#25:單 query、limit=1);
- **CLI 身分閘實測**:非 TTY 下(`echo | python review_knowledge_source.py --approve …`)approve 被拒;actor 非 superuser 被拒;
- admin approve/suspend 動作寫入 `knowledge_source_review_log` 且 audit log 留痕;
- **migration 全量對帳**:`SELECT approval_status, count(*)` 加總=**3,593 且零 NULL 桶**——53(enabled 有模板查詢/單跑型)→active、16(manual_file 導管)→active、3,524(re3data 3,507+具名 NULL 15+deliberately disabled 2)→proposed;**enabled 與 approval_status 零矛盾列**(enabled 退役對帳);
- **DOI 正規化驗收**:M4 後跨形態 DOI 重複對=0(基線實查 152 對);
- `--dry-run` 輸出之 **fulltext_eligible=true 源清單人工過目**;
- **backfill 前置**:`pg_dump -Fc -t knowledge_source` 快照已落地(#6/#30,--apply 自動檢查)。

### Wave 1:放大查詢矩陣(以 INSERT/UPDATE 資料列為主)

| 槓桿 | 動作 | 釋放量(估算) |
|---|---|---|
| 1. domain_map 拍板 | INSERT `knowledge_domain_map` 新域列(候選:economics/business/medicine/computer_science/social_sciences 等 OpenAlex fields;**用戶勾選,拍板 P2**) | 每域釋放閒置 query,全開約 +3,027 query × 14 general 源 ≈ +42,000 組合 |
| 2. 專業域 query 策展 | 從 `knowledge_taxonomy` 相關 subfield topics 批量產 query(`origin='curated_20260710'`),finance_mgmt/investment_mgmt/economics 各 ≥300 條,人審清單後 INSERT | 投資域深度從 193 條 manual → 千級 |
| 3. 補具名 NULL 模板(**probe 後定案**) | 逐源 probe→定案:opencitations、orcid_search 可望零新碼;repec_ideas(**token 申請=拍板 P12**)、core_uk(待 P4 key)、nasa_ads(待 token,W3);**pubmed_eutils 移 W2**(esearch→esummary 兩段式=新機制)、**biorxiv_details 移 W2**(ID/日期驅動,date-window 深抓);ieee_xplore/ssrn 降級 | **活源增量以 probe 結果回填,不預寫目標數**(#9 不預寫未實證數字) |
| 4. 既有源查詢放大 | gutendex 主題×多語言(**經自架 instance 或 catalog dump,不對 gutendex.com 放量**)、dbpedia/wikidata SPARQL 模板增列、IA 公版 collection 查詢 | 公版書目 metadata 廣度 |

**時程估算(誠實化)**:現成待跑組合 22,640,放大後估 60,000-80,000 組合。每組合=subprocess 冷啟+DB connect+API 往返,**實務 3-5s/combo ≈ 3-5 天純跑時間**(原估 30-45h 漏算行程開銷);**W0 先實測 100 組合取中位數回填本節**(#9)。可選優化=acquire 支援單行程多 query 批次(pace 照舊、不上併發)。分數晚背景跑(帳本+cursor 表 resume-safe,#22;全程 advisory lock 單飛)。

**驗收**:待跑組合 ≥60,000;promoted 淨增量與 staged→promoted 轉化率不低於基線 85.8%(現況 259,539/302,555);finance/investment/economics 域 query 各 ≥300;引擎程式零額外變更(僅資料列;W0 已交付之機制除外);每源健康度無 sustained 429;**KPI 未達≠放寬 gate——達不到即誠實回報缺口(§6.2-7)**。

### Wave 2:新協定與全文深化(新碼,#29b)

| 交付 | 說明 |
|---|---|
| `oai_pmh` adapter | ListRecords;**resumptionToken 僅存活於單次 session 記憶體(多數 repository token 短命,不可押過夜)**;**durable 游標=from/until datestamp 窗,存 `knowledge_source_cursor`(§3.5),不塞 harvest note(note 會被 upsert 覆寫)**;排程單位=每 set/日期窗 INSERT 一列虛擬 query(`origin='oai_set'`)落入既有 query×source 模型 |
| cursor 分頁深抓 | acquire 通用 pagination(adapter_config 宣告)+`--deep --max-pages`(讀 `max_pages` 欄=磁碟預算機械上限);**頁級 commit+cursor 表斷點**(400 頁抓到 300 頁死掉→從 301 續);回滿頁記 `status='partial'` 待重排(§3.2 M5) |
| PDF→text 抽取 | fetch_oa_fulltext 擴充(pdfminer.six 逐字,零 AI、零 OCR;**拍板 P3**);**P3 落地即一次性 requeue 既有 `skip_pdf` 終態(現查 448 筆),requeue 數入驗收與 review_log** |
| `fetch_pd_fulltext.py` | 公版書全文;**逐源公版判定規則表(P7)+OCR 政策(P8)+work_text 分工與同書去重(P10)+Gutenberg mirror 政策**;pseudo-source 閘+per-host pace(§4.1) |
| CORE 接入 | 註冊 key(拍板 P4)→ search adapter 列 + fulltext 後援源(`core_fulltext` pseudo-source);**落地即 requeue `skip_no_oa` 終態(現查 5,634 筆)中可能有 OA 副本者** |
| DOAB/OAPEN 接入 | B 軌書籍級 OA 全文(generic_json 資料列=近零新碼;OAPEN 可走 oai_pmh) |

**驗收**:oai_pmh 斷點實測升級為「**kill -9 後跨行程續傳 + resumptionToken 過期後以 datestamp 窗續**」;PDF 抽取抽樣 20 篇人工逐字比對(無 AI 改寫、剝標正確);公版書 ≥1,000 部入 item_text(**排除 philosophy_work_text 既有已抓部數——先跑 `--inventory` 盤點,驗收數字不灌水**);**license 判定正確性抽樣審計:每一全文源抽 N≥20 筆人工對源頁核授權(DB CHECK 通過=驗值不驗真,不得作為唯一驗收)**;公開全文段數從現況 807 段 → ≥50,000 段(**未達=誠實回報缺口,永不放寬 gate**);所有新入 item_text 之 license 欄 100% 通過既有 DB CHECK;**零 gutenberg.org 主站批量直抓(log 稽核)**;**promote 規模實測:單輪 staged 10 萬列時 promote 於輪內收斂(批次化驗證,§4.2)**。

### Wave 3:長尾(activation 工作流 + dump)

- **re3data 3,507 stub 激活漏斗**:`curate_source_candidates.py` 解析 note 中 API 線索(839 REST/580 OAI)→ 產模板草稿 → **URL 驗證(僅 https、host 與 re3data 登錄 repository domain 同源、拒 IP 直連/內網段)** → `probe_knowledge_source.py` 批次探測(保守步調;**首輪批次範圍 N 源清單=拍板 P11**——對數百未知主機之批次探測本身是外部副作用)→ probe 通過者列 admin 待審清單 → 人逐一/逐批 approve。**預期多數冷門庫停在 proposed——能抓≠該抓,探測通過≠應納入**;
- **dump_loader**:Wikipedia/Wikisource/Stack Exchange 選域抽取(**選域清單=P6;上游 AI 文本與 revision cutoff=P9**;`--revision-before` 參數落實);
- HathiTrust research access、arXiv bulk、NASA ADS token 等外部申請類(P12 逐項拍板)。

**驗收**:激活漏斗數字留痕(probe 通過率/approve 率);dump 落地 GB 與磁碟水位在 §7 預算內(**啟動+每 checkpoint 檢查**);每一 active 長尾源有 review_log approve 記錄;dump 之 revision cutoff 落實查核(P9 裁決值 vs 實際載入 revision)。

---

## 3. Table Schema(完整 DDL)

### 3.1 裁決:擴充 `knowledge_source`,不另建 source_catalog 表

**理由**:(a) 3,507 個 re3data stub 已住 `knowledge_source`,它**本來就是**世界來源目錄,另建新表=雙 SSOT(違原則精華 #12)+ 3,593 列遷移;(b) `knowledge_harvest_log`/`knowledge_item`/`knowledge_staging` 三表 FK 已指向它;(c) 審批/限速/波次是「來源」的屬性,不是另一實體。**wave 為欄不為表**;全文通道以 pseudo-source 列收編(§1 F 軌),同樣不另建表。

### 3.2 `knowledge_source` 擴欄(冪等 migration)

```sql
-- M1:目錄治理欄(全部 ADD COLUMN IF NOT EXISTS,冪等)
ALTER TABLE knowledge_source
  ADD COLUMN IF NOT EXISTS approval_status      varchar(16) NOT NULL DEFAULT 'proposed',
  ADD COLUMN IF NOT EXISTS approved_by          varchar(64),
  ADD COLUMN IF NOT EXISTS approved_at          timestamptz,
  ADD COLUMN IF NOT EXISTS license_regime       varchar(16),
  ADD COLUMN IF NOT EXISTS fulltext_eligible    boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS wave                 smallint,
  ADD COLUMN IF NOT EXISTS protocol             varchar(24),   -- 'rest_json'|'sparql'|'atom_xml'|'oai_pmh'|'dump'|'local_file'|'fulltext_channel'
  ADD COLUMN IF NOT EXISTS pace_seconds         numeric(6,2),  -- #24 對偶:每呼叫最小間隔
  ADD COLUMN IF NOT EXISTS quota_limit          integer,       -- 視窗內呼叫上限(NULL=無硬額度;§4.2 quota gate 機械執行)
  ADD COLUMN IF NOT EXISTS quota_window_seconds integer,
  ADD COLUMN IF NOT EXISTS cooldown_seconds     integer,       -- 429/403 預設冷卻(Retry-After 優先)
  ADD COLUMN IF NOT EXISTS max_pages            integer,       -- W2 深抓每 query 頁數硬上限(§7 磁碟預算之機械落點)
  ADD COLUMN IF NOT EXISTS abstract_policy      varchar(8),    -- 'allow'|'deny':abstract 逐字入 payload 之逐源 ToS 裁決(§6.1;允者須註 ToS 依據)
  ADD COLUMN IF NOT EXISTS est_scale            text;          -- 預估規模(人讀,計畫值非實測)

-- M2:CHECK 約束(Postgres 無 ADD CONSTRAINT IF NOT EXISTS,以 DO 塊防重,下同)
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ks_approval_status') THEN
    ALTER TABLE knowledge_source ADD CONSTRAINT chk_ks_approval_status
      CHECK (approval_status IN ('proposed','approved','active','suspended','exhausted','rejected'));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ks_license_regime') THEN
    ALTER TABLE knowledge_source ADD CONSTRAINT chk_ks_license_regime
      CHECK (license_regime IS NULL OR license_regime IN ('public_domain','cc_whitelist','metadata_only','owned_local'));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ks_active_needs_approval') THEN
    ALTER TABLE knowledge_source ADD CONSTRAINT chk_ks_active_needs_approval
      CHECK (approval_status NOT IN ('approved','active') OR approved_by IS NOT NULL);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ks_abstract_policy') THEN
    ALTER TABLE knowledge_source ADD CONSTRAINT chk_ks_abstract_policy
      CHECK (abstract_policy IS NULL OR abstract_policy IN ('allow','deny'));
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_ks_approval ON knowledge_source(approval_status, wave);
```

**狀態機語意**(轉移動作全走 §4 `augur.knowledge.curation`,寫 review_log):
```
proposed ──approve──> approved ──activate──> active ──suspend──> suspended ──resume──> active
   │                                            │──exhaust──> exhausted ──reopen──> active(superuser,需 reason)
   └──reject──> rejected ──reopen──> proposed(superuser,需 reason;來源方改 license/ToS 之再議路徑)
(system:harvest 僅得寫 cooldown 與 auto-suspend——只降不升;cooldown 非狀態變更)
```
- `approved`=人已批、待 probe/模板完備;`active`=**唯一**可入 harvest 排程之狀態;
- **人拍板閘**:`approve`/`activate`/`resume`/`reopen` 僅 superuser(admin UI 或具身分閘之 CLI,§4.1);**approve/activate 前置條件=review_log 存在近 30 日 action='probe' 且 http_status=200 之記錄**(§4.2 curation);
- **`enabled` 欄裁決(退役)**:backfill 以 enabled 推導初始 approval_status 後,**排程 SQL 唯一判 `approval_status='active'`,`enabled` 自 `_Q_CORE`/`_S_CORE` 全面移除**;欄本身降為歷史唯讀(migration 後不再讀寫;穩定一波後由後續 migration DROP,review_log 可考古)——單一 SSOT(#12),杜絕「activate 了卻被 enabled=false 靜默擋住」死角(實查 aozora_books/ssrn/repec_ideas 均 enabled=false)。

**M3 backfill(需用戶執行確認,拍板 P1)——全量對帳矩陣(逐 adapter×enabled×模板窮舉,加總必=3,593、零 NULL 桶)**:

| 群組 | 判準 | 列數(live 實查) | 目標 approval_status | license_regime 等 |
|---|---|---|---|---|
| 查詢/單跑型既有生產源 | enabled ∧ 模板非空 ∧ adapter≠manual_file | **53** | `active`(approved_by=執行者;既往生產拍板之追認) | 按 §1 目錄逐列 UPDATE |
| manual_file 匯入導管 | adapter='manual_file' | **16** | `active`(sanctioned 策展/owned_local 匯入導管之追認——**W0 上線當天不得切斷 `acquire_knowledge --source manual_curation` 既有標準路**) | license_regime=NULL(license 逐筆隨匯入內容,非源級屬性);protocol='local_file';harvest 既有 `adapter<>'manual_file'` 續排除排程;**acquire 閘與 staging trigger 豁免明文(§3.7/§4.2)** |
| re3data stub | 3,507 | **3,507** | `proposed` | — |
| 具名 NULL 模板源 | base_bielefeld…ssrn 等 | **15** | `proposed` | 按 §1 填 license_regime/wave |
| deliberately disabled | aozora_books/googlebooks | **2** | `proposed` | 按 §1 |
| **加總** | | **3,593** | | **W0 驗收=分佈加總相符、零 NULL 桶、enabled 零矛盾** |

另 M3 一併:(a) INSERT §1 F 軌 **5 列 pseudo-source**(protocol='fulltext_channel'、無模板不入排程;`ia_fulltext` 初始 suspended 待 P8);(b) license_regime/wave/pace/quota/max_pages/abstract_policy 按 §1 目錄表逐列 UPDATE(migration script 內建資料,`--dry-run` 預覽含 **fulltext_eligible=true 清單**);(c) **--apply 前置=`pg_dump -Fc -t knowledge_source` 快照**(#6/#30 復原後路)。

**M4:external_id(DOI)正規化+一次性合併(promote_knowledge 因此移出「零修改」名單)**:
- 病灶(live 實查):openalex 存 URL 形 DOI(`https://doi.org/10.…`,5,359 列)、crossref/europepmc/s2 存裸形(`10.…`,88,377 列),`uq_item_extid` 原始字串比對→**既有跨形態重複 152 對**;W1 多源扇出後必爆萬級=顧問檢索沉默污染(#8 下游污染型);
- 修法:`norm_doi`(剝 `https://doi.org/`/`dx.doi.org/`/`doi:` 前綴+lowercase)自 fetch_oa_fulltext **上移 `augur/knowledge/curation.py` 為 SSOT**;promote 入庫前一律過此函式;一次性合併 migration:對既有重複對重指 `knowledge_item_text.item_id`/`knowledge_fulltext_status`/staging 回溯欄至贏家(EXTID_PRIORITY 高者)後刪輸家,`--dry-run` 預覽;
- 驗收:**跨形態 DOI 重複對=0**(W0)。

**M5:harvest 帳本增可重排狀態 `partial`(承接 W2 深抓/OAI 增量語意——現制 status='ok' 即永不重排)**:
```sql
ALTER TABLE knowledge_harvest_log DROP CONSTRAINT IF EXISTS knowledge_harvest_log_status_check;
ALTER TABLE knowledge_harvest_log ADD CONSTRAINT knowledge_harvest_log_status_check
  CHECK (status IN ('ok','empty','error','partial'));
```
`_Q_CORE`/`_S_CORE` 排程條件納入 `partial`(回滿頁未盡=可重排);帳本 PK(query_id,source_key)不動。

### 3.3 審批日誌表(新)

```sql
CREATE TABLE IF NOT EXISTS knowledge_source_review_log (
  review_id    bigserial PRIMARY KEY,
  source_key   varchar(64) NOT NULL REFERENCES knowledge_source(source_key),
  action       varchar(16) NOT NULL
               CHECK (action IN ('propose','probe','approve','activate','suspend','resume','exhaust','reject','reopen','edit')),
  old_status   varchar(16),
  new_status   varchar(16),
  actor        varchar(64) NOT NULL,   -- app_user.username / 'system:harvest'(僅降級動作)
  os_user      varchar(64),            -- CLI 路徑併記 os user 與 tty(§4.1 身分閘留痕)
  reason       text,
  probe_result jsonb,                  -- probe:{rows, elapsed_ms, sample_keys, http_status, probed_with}
  created_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ksrl_source ON knowledge_source_review_log(source_key, created_at DESC);
```

### 3.4 來源健康度表(新;熔斷持久化 + Retry-After/quota 落點)

```sql
CREATE TABLE IF NOT EXISTS knowledge_source_health (
  source_key         varchar(64) PRIMARY KEY REFERENCES knowledge_source(source_key),
  total_calls        bigint  NOT NULL DEFAULT 0,
  total_errors       bigint  NOT NULL DEFAULT 0,
  consecutive_errors integer NOT NULL DEFAULT 0,
  cooldown_level     smallint NOT NULL DEFAULT 0,  -- 自癒階梯級數(0=無;15m/1h/6h/24h)
  calls_in_window    integer NOT NULL DEFAULT 0,   -- quota gate 視窗計數(原子 UPDATE 遞增,勿讀-改-寫)
  window_started_at  timestamptz,
  last_ok_at         timestamptz,
  last_call_at       timestamptz,                  -- 跨行程 pace 依此判斷,非行程內時鐘
  last_error_at      timestamptz,
  last_error_kind    varchar(16),                  -- '429'|'403'|'5xx'|'timeout'|'parse'|'perm'
  cooldown_until     timestamptz,                  -- honor Retry-After;排程 SQL 層直接過濾(§4.2)
  updated_at         timestamptz NOT NULL DEFAULT now()
);
```
**錯誤兩級制(取代「連錯即永久 suspend」——無人值守長跑不得單調流失活源)**:
- **temp 錯(429/5xx/timeout)→ cooldown 指數階梯自癒**:15m→1h→6h→封頂 24h(Retry-After 優先);cooldown 到期自動回排程——**cooldown 非狀態變更,不違「系統只降不升」**;成功一次即歸零階梯;
- **perm 錯(4xx 語意/parse)或冷卻階梯走滿後再連錯 ≥2 輪 → auto-suspend** + review_log(actor='system:harvest'),等人工 resume;
- **兩套閾值關係明文**:輪內連錯 5=跳過本輪(既有熔斷,行為不變);跨輪 `consecutive_errors ≥ 8` 或 24h 錯誤率 >50%=**進 cooldown 階梯**(非直接 suspend);suspend 僅上述 perm/階梯走滿路徑。
- FinMind 教訓平移(#24 地圖):429/403 **不本地推算恢復時點**,一律 honor Retry-After 或 cooldown_seconds,見訊號即停、絕不重試風暴。

### 3.5 斷點表(新):dump 與深抓/OAI 游標

```sql
CREATE TABLE IF NOT EXISTS knowledge_dump_checkpoint (
  source_key   varchar(64) NOT NULL REFERENCES knowledge_source(source_key),
  dump_file    text        NOT NULL,
  byte_offset  bigint      NOT NULL DEFAULT 0,
  items_loaded bigint      NOT NULL DEFAULT 0,
  finished     boolean     NOT NULL DEFAULT false,
  updated_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (source_key, dump_file)
);

-- 深抓/OAI durable 游標(取代「token 存 harvest note」——note 被 upsert 覆寫且 token 短命,過夜必失效)
CREATE TABLE IF NOT EXISTS knowledge_source_cursor (
  source_key   varchar(64) NOT NULL REFERENCES knowledge_source(source_key),
  scope        text        NOT NULL,   -- 查詢型='q:<query_id>';OAI='oai:<set_spec>';單跑='s:0'
  cursor_kind  varchar(16) NOT NULL CHECK (cursor_kind IN ('page_cursor','oai_datestamp')),
  cursor_value text,                   -- cursor 深抓=下一頁 cursor;OAI=last_datestamp(from/until 窗)
  pages_done   integer NOT NULL DEFAULT 0,
  rows_loaded  bigint  NOT NULL DEFAULT 0,
  finished     boolean NOT NULL DEFAULT false,
  updated_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (source_key, scope)
);
```
語意:resumptionToken 只活在單次 session 記憶體,失效即以 datestamp 窗重切;**頁級 commit**(mid-combo 斷點,kill -9 可續);OAI 排程單位=每 set/日期窗一列虛擬 query(`origin='oai_set'`)落入既有 query×source 模型。

### 3.6 覆蓋率:索引+視圖+輪末快照(儀表資料層)

```sql
-- staging 現況實查僅 pkey/(entity_type,status)/payload md5 三索引——per-source 聚合=全表掃,先補:
CREATE INDEX IF NOT EXISTS idx_staging_source ON knowledge_staging(source_key, status);

CREATE OR REPLACE VIEW v_knowledge_coverage_source AS
SELECT s.source_key, s.adapter, s.domain, s.approval_status, s.wave, s.license_regime,
       count(st.staging_id)                                AS staged_total,
       count(*) FILTER (WHERE st.status='promoted')        AS promoted,
       count(*) FILTER (WHERE st.status='rejected')        AS rejected,
       count(*) FILTER (WHERE st.status='pending')         AS pending,
       round(100.0*count(*) FILTER (WHERE st.status='promoted')
             / nullif(count(st.staging_id),0), 1)          AS promote_rate_pct
FROM knowledge_source s
LEFT JOIN knowledge_staging st USING (source_key)
GROUP BY 1,2,3,4,5,6;

-- 每域覆蓋+全文率(欄名依 code 事實定稿:knowledge_item.domain varchar(64) NOT NULL——
-- harvest_knowledge.py:57;knowledge_item_text(itext_id,item_id,seq,content,license 五值 CHECK)
-- ——migrate_text_understanding_ddl.py:41;原「若 item 無 domain 欄」hedge 與事實不符,已刪)
CREATE OR REPLACE VIEW v_knowledge_coverage_domain AS
SELECT d.domain, d.items, d.items_with_text, d.items_open_fulltext, d.items_owned_local,
       d.open_segments, COALESCE(q.queries, 0) AS queries
FROM (
  SELECT i.domain,
         count(DISTINCT i.item_id) AS items,
         count(DISTINCT t.item_id) AS items_with_text,
         count(DISTINCT t.item_id) FILTER (WHERE t.license IN ('public_domain','cc-by','cc-by-sa','cc0'))
                                   AS items_open_fulltext,
         count(DISTINCT t.item_id) FILTER (WHERE t.license = 'owned_local') AS items_owned_local,
         count(t.itext_id) FILTER (WHERE t.license IN ('public_domain','cc-by','cc-by-sa','cc0'))
                                   AS open_segments
  FROM knowledge_item i LEFT JOIN knowledge_item_text t USING (item_id)
  GROUP BY 1
) d
LEFT JOIN (
  SELECT m.augur_domain AS domain, count(*) AS queries
  FROM knowledge_query kq JOIN knowledge_domain_map m ON m.openalex_field = kq.domain
  WHERE kq.enabled GROUP BY 1
) q USING (domain);

CREATE OR REPLACE VIEW v_knowledge_harvest_progress AS
SELECT h.source_key, count(*) AS combos_done,
       count(*) FILTER (WHERE h.status='ok')      AS ok,
       count(*) FILTER (WHERE h.status='partial') AS partial,
       count(*) FILTER (WHERE h.status='empty')   AS empty,
       count(*) FILTER (WHERE h.status='error')   AS error,
       sum(h.rows_staged) AS rows_staged
FROM knowledge_harvest_log h GROUP BY 1;

-- 輪末快照(admin 儀表讀此,O(源數);live 聚合視圖降為 ad-hoc/report 用——
-- staging 上看億級後,30s 輪詢 live 聚合=常態 seq-scan 與 harvest 寫入互擾)
CREATE TABLE IF NOT EXISTS knowledge_coverage_snapshot (
  snapped_at   timestamptz NOT NULL DEFAULT now(),
  source_key   varchar(64) NOT NULL,
  staged_total bigint, promoted bigint, rejected bigint, pending bigint,
  PRIMARY KEY (source_key, snapped_at)
);  -- harvest 輪末 INSERT…SELECT FROM v_knowledge_coverage_source
```

### 3.7 staging 入庫 trigger(真.第三層 fail-closed 閘)

> 原稿宣稱「狀態機+DB CHECK+引擎 SQL 閘三層保證」不實——M2 CHECK 只約束 knowledge_source 自身欄值,對「非 active 源之資料寫入 staging」零約束力。本 trigger 補上真第三層:任何路徑(psql 直插/未來新 script 忘加閘)皆被擋。

```sql
CREATE OR REPLACE FUNCTION trg_staging_source_gate() RETURNS trigger AS $$
DECLARE st text; ad text;
BEGIN
  SELECT approval_status, adapter INTO st, ad FROM knowledge_source WHERE source_key = NEW.source_key;
  IF ad = 'manual_file' THEN RETURN NEW; END IF;  -- 本機匯入導管豁免:條件寫進閘內,非繞過(§3.2 M3)
  IF st IS DISTINCT FROM 'active' THEN
    RAISE EXCEPTION 'staging gate: source % is %, need active (charter: human approval)', NEW.source_key, st;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS staging_source_gate ON knowledge_staging;
CREATE TRIGGER staging_source_gate BEFORE INSERT ON knowledge_staging
  FOR EACH ROW EXECUTE FUNCTION trg_staging_source_gate();
```
效能:per-row PK 點查極輕;W0 驗收含「psql 直插非 active 源列必須失敗」實測。

**既有表變更面(誠實列舉,取代原「零 schema 變更」宣稱)**:`knowledge_harvest_log` status CHECK 增 `'partial'`(M5);`knowledge_staging` 增 (source_key,status) 索引與 BEFORE INSERT trigger(§3.7);`knowledge_item.external_id` 值一次性正規化合併(M4,結構不動)。`knowledge_query`(UNIQUE(domain,query)+origin)、`knowledge_domain_map`、`knowledge_item_text`(license/access_scope CHECK)、`knowledge_fulltext_status` 結構全部不動。

---

## 4. Python 程式規畫

**通則**:每支守 CLAUDE #29(a)`import _bootstrap` 個別可執行、(b)資料驅動零 hardcode、(d)標頭指令矩陣+實測;唯讀類實跑、放量類 import 級+最小單位驗證(#25)。共用審批/狀態機/身分閘/`norm_doi` 邏輯住新 library 模組 **`src/augur/knowledge/curation.py`**(領域名詞:來源策展治理;CLI 與 admin UI 同一 code path,#12)。**新 adapter code review 常設檢核點:欄位級 AI-provenance 篩查(任何 API 之模型生成欄位——tldr、AI keywords、auto-summary——一律不取,§6.2-1)。**

### 4.1 新程式

| 程式 | 用途 | CLI 矩陣 | I/O |
|---|---|---|---|
| `scripts/migrate_source_governance.py` | W0 一次性:§3 全部 DDL(M1-M5+§3.7 trigger)+ §1 目錄資料 backfill(**全量對帳矩陣 53+16+3,524=3,593**)+ **M4 DOI 正規化合併** | `--dry-run`(印將執行 SQL+變更列數+**fulltext_eligible=true 清單人工過目**+DOI 合併預覽)/ `--apply`(**前置自動檢查:`pg_dump -Fc -t knowledge_source` 快照已存在,無則拒跑**,#6/#30)/ `--backfill-active --confirm`(列 53+16 源名單需明示確認=拍板 P1) | in:無;out:DDL+UPDATE+合併執行報告(stdout);驗收=加總 3,593、零 NULL 桶、DOI 重複對=0 |
| `scripts/probe_knowledge_source.py` | #25 最小單位探測:單 query、limit=1。**機制保證不落庫(E-2 處置):probe path 不呼叫 stage()——adapter 執行後以收集器承接列數/樣本鍵/耗時,唯一落點=review_log.probe_result;staging 零寫入**。**URL 驗證前置**:僅 https、host 與 registry 登錄 domain 同源、拒 IP 直連/內網段 | `--source KEY [--query "test"]`(單源)/ `--use-draft`(讀 adapter_config.draft 組請求,probe_result 註 `probed_with='draft'`——re3data stub 漏斗賴此)/ `--batch --status proposed --limit 20`(pace 讀表;**首輪批次範圍=拍板 P11**)/ 無參數=印指令矩陣 | in:knowledge_source 列;out:review_log(action='probe');**無模板亦無草稿→回 `no_template` 終態非報錯** |
| `scripts/review_knowledge_source.py` | 審批 CLI(admin UI 之對偶,共用 curation.py)。**身分閘三件(D-2 處置)**:① 升級動作(approve/activate/resume/reopen)檢 `sys.stdin.isatty()`,**非 TTY fail-closed 拒執行**(自動化腳本/subprocess 天然被擋);② `--actor` 須對映 `app_user` 且 `is_superuser=true`(查表驗證,非自報),review_log 併記 os_user+tty;③ **approve/activate 屬決策層動作,AI 永不自行執行(同 #14 commit/push 級授權邊界,§6.2-2)** | `--approve KEY --reason "..."` / `--activate KEY` / `--suspend KEY --reason` / `--resume KEY` / `--reject KEY --reason` / `--reopen KEY --reason` / `--list --status proposed` | in/out:knowledge_source.approval_status + review_log |
| `scripts/report_knowledge_coverage.py` | 覆蓋率報表(零 token 本地):每源/每域進度、轉化率、全文率、健康度、**磁碟水位列**;讀 §3.6 輪末快照+視圖 | 無參數=全景 text 摘要 / `--json` / `--source KEY` / `--domain X` / `--wave N` | in:§3.6 views+snapshot+health;out:stdout(admin /api/coverage 同資料層) |
| `scripts/fetch_pd_fulltext.py` | 公版書逐字全文入庫,**逐源公版判定規則表(P7,入 code 常數+單測)**:Gutenberg=gutendex `copyright=false` 才入+剝 PG boilerplate(規則 regex,零 AI),**全文一律走官方 mirror/rsync 或 RDF/CSV catalog dump——零 gutenberg.org 主站批量直抓(PG 機器人政策,違者 IP ban)**;Wikisource=license 模板機讀判定(原著+譯者皆逾版權期),判不動→skip 記帳;IA=僅 `licenseurl` 明示 PD/CC0,且 `_djvu.txt`=OCR 產物→**P8 拍板前 IA 路徑不啟動**。**啟動閘=對應 pseudo-source(gutenberg_files/ia_fulltext/wikisource_files)approval_status='active'+per-host 分桶 pace+health 記帳**(§1 F 軌)。**同書去重閘(P10)**:先跑 philosophy_work_text 既有書單盤點(gutenberg_id/title 對映),重疊書單不重抓。8000 字/段,license='public_domain' | `--inventory`(既有 work_text 書單盤點,唯讀)/ `--source gutendex --limit 50` / `--item-id N`(單本,最小單位)/ `--dry-run` | in:knowledge_item(無 DOI 書目)+官方 catalog/mirror;out:knowledge_item_text + knowledge_fulltext_status 終態帳(**複用 fetch_oa_fulltext 之 gate/帳本/熔斷模式**) |
| `scripts/curate_source_candidates.py` | W3 re3data 激活漏斗前段:解析 note API 線索(839 REST/580 OAI)→ 產 query_template/adapter_config **草稿**(寫 adapter_config `draft` 鍵,不啟用)→ **產草稿時即做 URL 驗證(同 probe:https/同源/拒內網),不合格標 `invalid_endpoint`** → 輸出候選清單供 probe+人審 | `--parse-notes --limit 100` / `--list-drafts` / `--promote-draft KEY`(草稿轉正,仍停 proposed) | in:re3data stub note 文字;out:adapter_config.draft + 候選清單 stdout |
| `scripts/load_knowledge_dump.py` | W3 bulk dump 串流 loader:XML/7z 串流解析(iterparse,常數記憶體)→ 選域過濾(P6)→ **`--revision-before DATE`(P9 revision cutoff)** → knowledge_staging(md5 去重天然冪等) | `--source-key X --dump-file F --domain-filter "..." --revision-before DATE --max-items N --max-bytes G` / `--resume`(讀 checkpoint) | in:本地 dump 檔;out:staging 列 + knowledge_dump_checkpoint;**磁碟水位檢查=啟動+每 checkpoint 寫入點(shutil.disk_usage),<100G 即停**(§7) |

### 4.2 既有程式修改(#29c 複用明標)

| 程式 | 修改 | 不動 |
|---|---|---|
| `scripts/acquire_knowledge.py` | ① main() 讀 registry 後加閘:`approval_status!='active'` 拒跑(**adapter='manual_file'/protocol='local_file' 豁免明文**——既有策展入口不斷路;`--probe` 模式=共用 probe 收集器 path,**不寫 staging**,取代原「proposed 可單發」例外);② per-source pace:**run 內分頁間** sleep `pace_seconds`(讀表,NULL→1.5s 保守預設;組合間節流住 harvest 端——雙落點分工明文);③ honor Retry-After:429/503 讀 header 寫 health.cooldown_until 後**即停**(不重試);④ health 記帳(每呼叫 upsert,含 last_call_at);⑤ 通用分頁:adapter_config `pagination` 鍵(`{"mode":"cursor"or"offset",...,"max_pages":N}`)+ `--deep --max-pages N` CLI+**頁級 commit 寫 knowledge_source_cursor(mid-combo 斷點)**;⑥ **新 adapter `oai_pmh`**(ListRecords;resumptionToken 僅 session 內;**durable 游標=from/until datestamp 存 cursor 表,不塞 note**);⑦ **quota gate(#24 _quota_gate 對偶,原缺此條=有欄無閘)**:每呼叫前**原子 UPDATE 遞增 `health.calls_in_window`(SQL 端含視窗滾動歸零,勿讀-改-寫)**,達 `quota_limit×0.9` 即寫 cooldown_until=視窗重置點並停該源;⑧ **per-source advisory lock(`pg_try_advisory_lock(hashtext(source_key))`)**——跨行程同源併打=pace×N,直接違 #24 | 13 既有 adapter 函式、fill() 模板機制、stage() 去重、--query-id lineage 全不動 |
| `scripts/harvest_knowledge.py` | ① `_Q_CORE`/`_S_CORE`:`s.enabled` **移除**、改唯一判 `AND s.approval_status='active'`(**fail-closed 機械閘落點**)+ `LEFT JOIN knowledge_source_health h … AND (h.cooldown_until IS NULL OR h.cooldown_until < now())`(冷卻中源 SQL 層直接不排,免每組合 spawn 立即退出之空轉)+ **status='partial' 納入重排**;② `pace()` hardcode 前綴表改讀 `pace_seconds`(讀不到→既有前綴表 fallback,#27 已驗證值維持);**組合間 pace 依 health.last_call_at(跨行程),非行程內時鐘**;③ 熔斷持久化:輪內連錯同步寫 health,依 §3.4 兩級制(cooldown 階梯自癒/perm 才 auto-suspend+review_log);④ `--wave N` 參數;⑤ 輪末印固定 sentinel+**輪末寫 coverage snapshot(§3.6)**;⑥ **啟動即取全域 advisory lock(`pg_try_advisory_lock(hashtext('harvest'))`),取不到即報「已有 harvest 在跑」退出**;⑦ wave≥2 源組指令附 `--deep --max-pages`(讀 max_pages 欄),回滿頁記 `partial` 非 `ok`;⑧ 輪末 promote 呼叫改 `--batch` 且 timeout 取消(隨 promote 批次化) | 排程矩陣結構、resume 帳本 PK(query_id,source_key)、attempts<2、temp 錯分類不動(**原「帳本全不動」宣稱刪除——status 增 partial,M5**) |
| `scripts/fetch_oa_fulltext.py` | ① `PACE_SEC` 常數改讀 pseudo-source(unpaywall/oa_publisher_pool)之 pace_seconds+**per-host 分桶 pace**(現行單一全域 0.5s 打所有出版商 host);② **PDF 路徑(拍板 P3 後)**:content-type application/pdf 且過 license gate → pdfminer.six 逐字抽取(≤20MB;無文字層→`skip_pdf_noext` 終態;**零 OCR、零 AI**)→ 同一剝標/分段管線;**P3 落地即一次性 requeue 既有 `skip_pdf`(448 筆),留痕 review_log**;③ CORE 後援(拍板 P4 後):Unpaywall 無 OA 位置時問 CORE,license 仍過同一 LICENSE_MAP;**P4 落地即 requeue `skip_no_oa`(5,634 筆)**;**fallback 鏈尾明文封底:查無合法 OA 副本→`skip_no_oa` 終態,永不降級至非法管道(§6.2-8)**;④ **啟動閘=對應 pseudo-source active+health 記帳**;⑤ **Unpaywall quota gate(100k/day 官方明文);backlog >100k 走官方 DB snapshot(ToS 認可 bulk 路),API 留增量** | LICENSE_MAP 白名單、knowledge_fulltext_status 終態帳、8000 字分段、熔斷模式全不動 |
| `scripts/promote_knowledge.py` | **自「零修改」名單移出(E-1/E-2/E-3 處置)**:① **批次化**:全量 fetchall+單一交易改 `LIMIT N` 迴圈+逐批 commit(百萬級 pending 下原制必 OOM/超時 rollback=livelock);② **入庫閘(fail-closed 第二道)**:pending 排程 SELECT 加 `JOIN knowledge_source USING(source_key) AND (approval_status='active' OR adapter='manual_file')`;③ **DOI 正規化**:入庫前過 curation.norm_doi(M4 SSOT) | **staging→正式表之欄位契約/mapper 介面不變(下游端到端主計畫對齊點仍守)** |
| `scripts/expand_knowledge_registry.py` | P2 產 stub 時直接填 `approval_status='proposed'`+protocol 線索欄(取代 note 藏字) | P1 taxonomy/P3 獎項不動 |
| `scripts/refresh_knowledge_pipeline.py` | **零修改**(八段 DAG 接手點不變) | 全部 |
| `src/augur/knowledge/curation.py`(新 library) | 狀態機轉移函式(驗證合法轉移+寫 review_log+audit);**approve()/activate() 前置條件=review_log 存在近 30 日 action='probe' 且 probe_result.http_status=200,否則拒絕回「請先 probe」(`--force` 需 reason,留痕)——紅線 6「probe 通過才 approve」之機械落點**;**superuser 身分驗證(app_user 查表)**;probe 收集器(不落 staging);**`norm_doi` SSOT**;覆蓋率查詢——admin UI 與 CLI 共用 | — |

### 4.3 既有全文資產盤點與分工裁決(P10;修正原稿「公版書全文未接」之錯誤前提)

repo 實況:**五支既有公版全文 fetcher**(`fetch_gutenberg_classics.py`/`fetch_all_thinker_works.py`/`fetch_chinese_classics.py`/`fetch_public_domain_classics.py`/`fetch_confirmed_fulltext.py`)早已抓 Gutenberg/維基文庫逐字全文,落點=`philosophy_work_text`(柏拉圖全集、Reminiscences、群眾瘋狂、國富論等已在庫)。未裁決即上 fetch_pd_fulltext=雙全文落點+同書重抓(違 #12 單一住所/#29c)。

**拍板 P10 二擇一**:
- **方案 A(建議)**:明定語意邊界——`philosophy_work_text`=哲學素養原典(thinker/work 鏈)、`knowledge_item_text`=知識層全文(item 鏈);fetch_pd_fulltext 掛**同書去重閘**(gutenberg_id/title 對映既有 work_text,重疊不抓),W2 驗收數字排除既有部數;
- **方案 B**:合流(單一全文住所)——工程量大、動下游 sentences 雙源 FK,不建議本計畫承擔。

配套:既有五支 fetcher 標頭已載退役方向(策展一律走 acquire→promote);**既有游離 fetch_* 一併收編 pseudo-source 體系或明文豁免留痕(review_log)**,不留治理外全文通道(O-4)。

---

## 5. Admin 控制台擴充(serve_admin_console.py :8500)

**掛載點依偵察行號**;單檔已 905 行,本次新增之 SQL/狀態機邏輯**全部住 `augur.knowledge.curation`**,console 只留 route 分派與 HTML(結構決策:不再增肥單檔)。改後 `systemctl restart augur-admin` 再實測(#7)。

### 5.1 新增 UI(nav :438-449 加兩鈕,section 樣板照 :461-471)

| Section | 內容 |
|---|---|
| `sec-sources` 來源審批 | 表格:source_key/adapter/domain/license_regime/wave/approval_status/最近 probe 結果;**預設篩選 status='proposed'+分頁(limit 100/offset)——3,507 列 proposed 不整頁傾倒**;篩選(status/wave/adapter);每列動作鈕 probe/approve/activate/suspend/resume/reject/reopen(**approve/activate/resume/reopen 僅 superuser**,`app_user.is_superuser` 判定照 :709-712);動作需填 reason;**無 probe 成功記錄之源,approve 鈕 disabled+提示「請先 probe」(前端呼應 curation 前置條件,後端仍為權威閘)**;wave 觸發鈕(選 wave+可選 domain → 背景 harvest,**僅 superuser**) |
| `sec-coverage` 覆蓋率儀表 | 三塊:每源進度(staged/promoted/轉化率/健康度紅黃綠)、每域覆蓋(query 數/item 數/全文率,v_knowledge_coverage_domain 口徑)、全文率總覽(公開全文段數 vs owned_local vs 目標);純 HTML 表+inline bar;**資料層=knowledge_coverage_snapshot 輪末快照(O(源數)),非 live 全表聚合;輪詢 60s**(harvest 未跑時資料不變) |

### 5.2 新增 API(route 分派加在 do_GET :658 / do_POST :717 if-chain)

| 端點 | 同步/背景 | 說明 |
|---|---|---|
| `GET /api/sources?status=proposed&wave=&adapter=&limit=100&offset=0` | 同步 | 來源清單(curation 查詢);**預設 status 篩選+分頁必帶** |
| `POST /api/source/action` `source_key=&action=&reason=` | 同步短寫 | **body 格式從眾既有 console 慣例=urlencoded form(:757 parse_qs 唯一解析路),不新增 JSON 分支**;狀態機轉移;superuser gate;**無 probe 記錄之 approve 拒絕(HTTP 400+提示)**;寫 review_log+_audit(:137) |
| `POST /api/source/probe` `source_key=` | 同步(timeout 60s) | subprocess `probe_knowledge_source.py --source KEY`(#25 最小單位);**superuser gate(外呼未審 endpoint=外部副作用)**;批次 probe 同 |
| `GET /api/coverage?by=source\|domain` | 同步 | 儀表 JSON,**讀 snapshot 表非 live 聚合** |
| `POST /api/wave` `wave=&domain=` | **背景** | 複用 /api/topic 放量模板(:768-787):`Popen(harvest_knowledge.py --wave N, start_new_session)` + `harvest_<hex>.log` + `_JOBS` + progress 頁(:310-343);`_DONE_MARKS`(:148)tuple 擴一個 harvest sentinel;**superuser gate(放量=#24/#26 決策層動作,與 approve 同級)+寫 _audit**;**觸發前置=advisory lock 預檢+_JOBS 存活檢查,已有 harvest 在跑即拒(HTTP 409)——_JOBS 為記憶體 dict、admin 重啟即失憶,故 DB lock 為權威** |

安全機件全複用::667/:748 `_valid` fail-closed、:87/:151 realpath 圍欄、subprocess 參數陣列 shell=False、審計照舊。

---

## 6. 治權合規

### 6.1 三軌全文/metadata 分流矩陣(逐筆 gate,住 DB CHECK+規則表非 UI)

| license_regime | metadata | abstract | 全文入 item_text | license 欄值 | gate 落點 |
|---|---|---|---|---|---|
| public_domain(A 軌) | ✅ | ✅ | ✅ 逐字(**逐件判定規則表 P7+OCR 政策 P8**) | `public_domain` | fetch_pd_fulltext **逐源判定規則表(依據欄+接受值入 code 常數+單測:Gutenberg `copyright=false`/Wikisource license 模板機讀/IA `licenseurl` PD/CC0)** + `knowledge_item_text_license_check`;**W2 抽樣審計每源 N≥20 人工對源頁(驗真;DB CHECK 只驗值——CHECK 通過≠判定正確,不得循環論證)** |
| cc_whitelist(B 軌) | ✅ | ✅ | 逐篇 license ∈ {cc-by,cc-by-sa,cc0} 才入;NC/ND/未明→**停 metadata**;**任意上傳型/dump 型另受 P9(上游 AI 文本)獨立拍板** | 實際 CC 值 | fetch_oa_fulltext `LICENSE_MAP`(既有,不動)+ 全文來源分級(§1 B 軌) |
| metadata_only(C 軌) | ✅(API ToS 內) | **依 `abstract_policy` 欄逐源裁決**(allow 須 ToS 明文依據並註於目錄;Semantic Scholar/PubMed/EuropePMC=allow;**Crossref 預設 deny**——出版社逐一授權不可考) | ❌ 直抓;僅經 Unpaywall/CORE OA 副本且過白名單 | — | 同上 |
| owned_local | **不經本計畫任何外部 adapter** | — | 僅本機匯入(acquire_local_files/manual_file 導管) | `owned_local`+`local_private` | `chk_itext_owned_local_private`(既有) |

**硬條款(新增)**:**payload 內任何內文欄位(abstract 等)永不遷入 `knowledge_item_text`**——item_text 唯一入口=三軌 fetch 工具之 license gate;abstract 只活在 metadata payload,僅供顯示/檢索,無「日後搬進全文表」路徑。

### 6.2 硬性紅線(逐條)

1. **AI 生成零入庫(不變式①,憲章 :142)**:全部路徑逐字轉載+規則 regex 剝標;PDF 抽取=pdfminer 文字層逐字、零摘要;**OCR 政策=P8 拍板,未拍板前 OCR 文本(IA `_djvu.txt`)不入**;**adapter 欄位級 AI-provenance 篩查=新 adapter code review 常設檢核點+S0 驗收項——任何 API 之模型生成欄位(Semantic Scholar `tldr`〔SciTLDR〕、AI keywords、auto-summary)一律不取,payload 經 promote 入正式表即已入庫、不因「只是 metadata」豁免**;`chk_itext_source_type` 誠實定位=自標籤約束(僅擋 `source_type='ai_generated'` 自報),**對上游 AI 文本零偵測力——上游防線=全文來源分級(§1)+P9 拍板,不以 CHECK 自欺**;
2. **人拍板閘(三層 fail-closed)**:`approval_status='active'` 為 harvest 排程唯一入場券(SQL 層)+promote 入庫 JOIN 閘+staging BEFORE INSERT trigger(§3.7);approve/activate 僅 superuser——**admin UI 走 :709-712 判定,CLI 走 TTY 檢查+app_user 對映(§4.1)**;**approve/activate 屬決策層動作,AI 永不自行執行(同 #14 commit/push 級授權邊界;CLAUDE #26 有界自主授權不含此類動作)**;系統只可降級;domain_map 新域=INSERT 前人拍板(P2);**全文通道亦經 pseudo-source 審批閘(§1 F 軌)——suspend 即停,無治理外通道**;殘餘面誠實註明:superuser 直接 psql 改 DB 不在機械防線內(屬決策層自身行為,review_log 以外之直改視同手工 hand-patch,#12 禁);
3. **domain 隔離**:staging/query/source 之 domain 欄照舊;多域知識零量化價值不進預測管線;預測 7 package 零 import `augur.knowledge`——**本計畫所有新 scripts/模組納入 `tests/test_philosophy_isolation.py` AST 掃描**;
4. **隱私上限(憲章 :166)**:owned_local 內容**永不作為外部 API 之 query 參數**——明文禁止「以自有文件內容找相關論文」型設計;新 adapter code review 檢核點;
5. **#24 對偶(pace+quota+cooldown 三件俱全)**:per-source pace/**quota gate(呼叫前原子計數,90% 即停至視窗重置——「低於速率上限≠安全」,FinMind 教訓)**/cooldown 住 DB(§3.2/§3.4),引擎讀表;honor Retry-After;429/403 見訊號即停不重試風暴;**跨行程 advisory lock 互斥(單源實效速率恆=pace)**;新安全值依 #27 重覆實證才回填;
6. **#25 最小單位+probe 機械前置**:一切新源必先 probe(單 query limit=1)通過才 approve——**非人工紀律而是 curation.approve() 前置條件(近 30 日 probe http 200 記錄,§4.2),`--force` 需 reason 留痕**;probe 不落 staging(收集器 path);放量後緊盯前段(health 儀表);
7. **絕不繞 license+KPI 永不凌駕 gate**:「想辦法抓到」=窮舉合法面積(§0.2),NC/ND/版權未明永遠停 metadata;ctext 類 ToS 模糊源保守處理(metadata_only 落表,P5 留痕);**任何波次 KPI(含 W2「≥50,000 段」)未達=誠實回報缺口(#8),不得以放寬 gate、降低判準、擴大詮釋達標**;
8. **來源負面清單(明文,新增)**:**禁影子圖書館——Sci-Hub、LibGen、Anna's Archive、Z-Library 及一切同類鏡像/種子管道,無論其內容是否「本應開放」**;**禁「API 拒絕/無 API 就改爬 HTML」、禁繞 robots.txt、禁違 ToS 抓取**;**禁帳號牆/付費牆內容(含以個人帳號 cookie 模擬瀏覽器)**;機制配套=**引擎只准呼叫 `knowledge_source` registry 內宣告之 endpoint(URL allowlist),新 endpoint=新拍板**(probe/curate 之 URL 驗證同源檢查為其前哨);OA 後援鏈(Unpaywall→CORE)**鏈尾明文封底**:查無合法 OA 副本→`skip_no_oa` 終態,fallback 永不延伸至清單外管道。

---

## 7. 營運

- **零 Claude token(#28)**:全鏈=本地 Python + PostgreSQL + 目標 API;admin 觸發=subprocess;監看=logfile 輪詢+DB 快照/視圖;無任何 Claude model 呼叫。唯計畫執行中之「理解層」問題(license 判讀爭議、doctrine 詮釋)回到對話,執行層全本地;
- **resume 全 DB-driven**:harvest=`knowledge_harvest_log`(+`partial` 狀態);深抓/OAI=`knowledge_source_cursor`(頁級 commit,kill -9 可續);全文=`knowledge_fulltext_status`;dump=`knowledge_dump_checkpoint`;限速冷卻=`health.cooldown_until`(階梯自癒);任何中斷/暫停皆冪等可續(#22/#28);
- **互斥與跨行程紀律**:harvest 全域 advisory lock 單飛、acquire per-source lock、admin 觸發前 DB lock 預檢(§4.2/§5.2)——**同一源任何時刻實效速率恆=pace,不因併行進程稀釋**;
- **磁碟預算(WSL ext4 餘 776G,DB 現 ~44G;staging payload 實測 avg 171B/列、302k 列=151MB)**:

| 項目 | 估算上限 | 護欄 |
|---|---|---|
| W1 metadata staging(~80k 組合×25 列;實測 171B/列——原估 2KB/列高估 12 倍,保守方向) | ~1-5G | 帳本自然收斂 |
| **W2 深抓 metadata(新增行項——原稿漏列,為預算最大乘數)** | **≤60G**(60k query×`max_pages` 預設 80 頁×25 列≈1.2 億列,含索引) | **硬上界由 `max_pages` 欄機械控制(§3.2)**;**staging 歸檔策略:promoted 且 item 已建者 payload 截斷/移歸檔表**(`knowledge_item.staging_id` 故意無 FK 已為此預留,DDL 註釋明言)——防億級 staging 拖垮 #30 跨機 pg_dump 交接 |
| W2 公開全文(HTML/XML/公版書) | ~20-40G | 逐段入庫無原檔留存 |
| W2 PDF 暫存 | 50G 硬上限 | 解析後即刪原檔;暫存住 scratchpad 型目錄 |
| W3 dump 原檔+抽取 | 100G 硬上限 | `--max-bytes`+選域抽取;**磁碟水位檢查=啟動+每 checkpoint 寫入點(shutil.disk_usage),<100G 即全線停**(百 GB 級載入是多小時作業,僅啟動檢查不足) |
| **總計** | **≤250G,恆留 >400G headroom** | `report_knowledge_coverage.py` 附磁碟水位列 |

- **GPU 無關**:本計畫純 CPU+I/O(抓取/解析/落庫);embed 以下屬下游主計畫;
- **長跑紀律**:過夜 wave 走 admin 背景路(detached Popen+logfile);≥5 分鐘任務 log 內每輪印進度(#21);WSL2 主機睡眠設定由用戶確認(#22);**auto-cooldown 自癒(§3.4)保無人值守長跑不單調流失活源——temp 錯到期自動回排,僅 perm 錯留給人**;
- **時程誠實**:W1 全輪 3-5s/combo(subprocess 冷啟+connect+API 往返)≈3-5 天純跑,W0 實測 100 組合中位數回填(#9);bulk 需求(Unpaywall backlog >100k)走官方 snapshot 而非 API 硬跑。

---

## 8. 分階段+驗收+拍板點

| 階段 | 內容 | 驗收(§2 詳) | 拍板點 |
|---|---|---|---|
| **S0** 治理基建 | §3 DDL(M1-M5+trigger)+ migration/backfill + acquire/harvest/promote 三層閘 + quota gate + advisory lock + curation.py(身分閘/probe 前置/norm_doi)+ probe/review CLI | **三層 fail-closed 實測、probe 無痕、quota gate、互斥、cooldown 自癒、CLI 身分閘、對帳 3,593 零 NULL、DOI 重複對=0、fulltext_eligible 清單過目、pg_dump 快照前置**(§2 W0 全清單) | **P0**:本計畫書整體(含「擴 knowledge_source 不另建表」、狀態機七動作含 reopen、三層閘架構、enabled 退役);**P1**:backfill 全量對帳矩陣(53 active+16 manual_file active+3,524 proposed=3,593)名單確認 |
| **S1** admin UI | sec-sources(分頁/probe 前置提示)/sec-coverage(snapshot 資料層)+ 5 API(全動作 superuser gate)+ restart 實測(#7) | 審批動作留痕、儀表數字對帳 psql、superuser gate 實測(**含 /api/wave 與 probe 端點**)、無 probe 記錄 approve 鈕 disabled、併行觸發被 409 拒 | (P0 涵蓋 UI 契約) |
| **S2** Wave 1 放大 | domain_map 新域、專業域 query 策展、具名源補模板+probe+審批(probe 後定案)、背景輪跑 | 組合 ≥60k、轉化率 ≥85.8% 基線、投資域 query ≥300×3 域、健康度無 sustained 429、**KPI 未達=誠實回報** | **P2**:domain_map 新域勾選清單(能抓≠該抓核心閘);**P12**:RePEc token 申請(外部副作用);每源 approve(常設) |
| **S3** Wave 2 深化 | oai_pmh(datestamp 游標)、cursor 深抓(partial+頁級斷點)、PDF 抽取+requeue、fetch_pd_fulltext(規則表/mirror/去重)、CORE+requeue、DOAB/OAPEN | 公開全文 807 段→≥50,000 段(未達誠實回報)、PDF 抽樣 20 篇逐字比對、公版書 ≥1,000 部(**排除既有已抓**)、**license 判定抽樣審計 N≥20/源**、kill -9 續傳、**零 gutenberg.org 主站直抓**、promote 十萬列輪內收斂 | **P3**:PDF 解析(pdfminer 依賴+路徑+skip_pdf requeue);**P4**:CORE key 註冊+skip_no_oa requeue;**P5**:ctext 全文停用改道(metadata_only 落表);**P7**:公版判定規則表+PD 轄區基準(建議:採來源方自身宣告+US-PD,存 provenance 供覆核);**P8**:OCR 政策二擇一(A=公版全文僅 born-digital 純文字〔Gutenberg txt/Wikisource/Aozora〕,IA 降 metadata+連結;B=OCR 文本可入+payload 註 `provenance='ocr'`+抽樣 N 卷人工比對頁影品質關);**P9**:不變式①詮釋——上游 AI 文本是否入庫(治權詮釋,不默採寬鬆解);任意上傳型(Zenodo)/dump 型(Wikipedia/SE)全文獨立拍板,選項含 revision cutoff(如 2022-11 前版本);**P10**:philosophy_work_text vs knowledge_item_text 全文分工(§4.3 方案 A/B)+投資經典策展書單 |
| **S4** Wave 3 長尾 | re3data 激活漏斗(URL 驗證)、dump loader(revision cutoff)、外部申請類 | 漏斗留痕、磁碟水位(啟動+每 checkpoint)、逐源 approve、revision cutoff 查核 | **P6**:dump 選域清單;**P11**:首輪批次 probe 範圍(N 源清單=對數百未知主機之外部副作用);P12 續:HathiTrust research access/NASA ADS token 等逐項 |

> **✅ 拍板記錄:2026-07-10 用戶簽核「P0-P12 整批依建議」**——P0 准(含入憲 v1.41.0)|P7=來源方宣告+US-PD+provenance|**P8=方案 A**(born-digital 純文字;IA 降 metadata+連結)|**P9=保守解**(上游 AI 文本不入庫;Zenodo/dump 全文不啟用,revision cutoff 屆時逐項)|**P10=方案 A**(雙住所分工+同書去重閘)|清單類(P1/P2/P6/P11/P12)=依建議框架、實作時逐清單過目(常設拍板閘不變:每源 approve 仍人手)。

**拍板點總表**:P0 計畫整體|P1 backfill 矩陣|P2 domain_map|P3 PDF|P4 CORE|P5 ctext|P6 dump 選域|**P7 公版判定規則+PD 轄區**|**P8 OCR 政策**|**P9 上游 AI 文本詮釋(不變式①)**|**P10 全文分工+經典書單**|**P11 批次 probe 範圍**|**P12 外部 token/註冊申請逐項**。

**常設拍板閘**(貫穿全程,非一次性):每一源 `proposed→approved→active` 之兩次升級動作=決策層人按鈕(UI superuser 或 TTY+superuser CLI),留痕於 review_log——**沒有任何源(含全文通道 pseudo-source)可以不經人手進入排程或入庫(三層機械閘保證)**;**approve/activate 屬決策層動作,AI 永不自行執行**;**KPI 永不凌駕 gate**。

**實作紀律**:每階段逐支/逐段過目(#19);改 serve_admin_console 後 restart 服務再實測(#7);憲章同步(若 P0 認定狀態機屬架構準則,升 **v1.41.0**)一併於 S0 提交;四鏡發現全數登錄 §9,拍板時逐條過目。

---

## 9. 對抗發現表(留痕)

> 依 CLAUDE #20 高風險門檻(跨治權檔詮釋+外部副作用+跨多 package):本計畫 v1 草稿經**四鏡平行對抗審查**(doctrine 治權鏡/completeness 完整性鏡/engineering 工程鏡〔含 live DB 實證〕/ops 營運鏡),共 **47 項發現(6 blocker/25 major/16 minor),全數修入 v2**;逐條處置如下,拍板前後之異議續登錄於此。

| # | 鏡別 | 嚴重度 | 發現 | 處置 |
|---|---|---|---|---|
| D-1 | doctrine | **blocker** | C 軌放行 Semantic Scholar `tldr`(SciTLDR 模型生成)入 payload=AI 生成入庫,直接違不變式①(payload 經 promote 即入庫,不因 metadata 豁免) | 刪 tldr 提案,C 軌僅逐字欄位;§6.2-1 增「adapter 欄位級 AI-provenance 篩查」為新 adapter 常設檢核+S0 驗收(§1/§4/§6.2)——已修 |
| D-2 | doctrine | **blocker** | 審批 CLI `--actor` 自報、無身分驗證——人拍板閘可被任何本地進程(含 #26 自主推進之 AI)機械繞過,核心安全主張被自家設計否證 | 三件並行:非 TTY fail-closed 拒升級動作;actor 對映 app_user.is_superuser 查表驗證+併記 os_user/tty;明文「approve/activate 屬決策層,AI 永不自行執行(#14 級)」(§4.1/§6.2-2)——已修 |
| D-3 | doctrine | major | 上游 AI 生成內容零防線(Zenodo 任意上傳/2022 後 Wikipedia/SE AI 答案掛 CC 即全過);`chk_itext_source_type` 僅自標籤約束;不變式①詮釋默採寬鬆解未交拍板 | 全文來源分級(首波僅編輯/策展閘源);任意上傳/dump 型全文獨立拍板+revision cutoff 選項;**不變式①詮釋列 P9 交用戶**(§1/§6.2-1/§8)——已修+拍板 P9 |
| D-4 | doctrine | major | 影子圖書館/爬蟲繞道/帳號牆之負面清單通篇缺席;「5 萬段 KPI」與 gate 間無「KPI 不凌駕」條款——最危險的一條缺席紅線 | 新紅線 §6.2-8:點名禁 Sci-Hub/LibGen/Anna's Archive/Z-Library、禁繞 robots.txt/ToS、禁帳號牆;URL allowlist 機制;fallback 鏈尾封底;「KPI 未達≠放寬 gate」入驗收(§0.2/§2/§4.2/§6.2)——已修 |
| D-5 | doctrine | major | 「零 OCR」紅線與 IA `_djvu.txt`(Abbyy OCR 產物)自相矛盾——對 PDF 說 OCR 不夠格、對 IA 直接吃 OCR | OCR 政策二擇一明列 P8(A=born-digital only/B=OCR 可入+provenance 標記+抽樣品質關),不得默認;P8 前 IA 全文不啟動、`ia_fulltext` pseudo-source 初始 suspended(§1/§4.1/§8)——已修+拍板 P8 |
| D-6 | doctrine | major | `enabled` 與 `approval_status` 雙旗並存未裁決=排程閘雙 SSOT(違 #12;實查 aozora enabled=false,activate 後仍被靜默擋) | enabled 退役:backfill 推導初始狀態後排程 SQL 唯一判 approval_status;對帳驗收「兩欄零矛盾」(§3.2/§4.2/§2)——已修 |
| D-7 | doctrine | major | 「三層保證」誇大——DB CHECK 只管 knowledge_source 欄值,對非 active 源寫 staging 零約束,真閘僅兩層腳本 | 補真第三層:staging BEFORE INSERT trigger(manual_file 豁免寫進 trigger 內)+W0「psql 直插必失敗」實測;§0 宣稱同步改述(§3.7/§0/§2)——已修 |
| D-8 | doctrine | major | C 軌 abstract 版權灰區被「✅(API ToS 內)」壓成勾號(Crossref abstract 再利用權出版社逐一設定);無「不遷入 item_text」防線 | 目錄增 `abstract_policy` 欄逐源填 ToS 依據(S2/PubMed/EuropePMC allow、Crossref 預設 deny);§6.1 硬條款「payload 內文欄位永不遷入 item_text」(§3.2/§1/§6.1)——已修 |
| D-9 | doctrine | major | A 軌「逐卷公版判定」無判定機制(Gutenberg 有版權書、Wikisource 混當代譯本、IA metadata 不可靠);CHECK 驗值不驗真=循環論證 | 逐源判定規則表(Gutenberg copyright=false/Wikisource 模板機讀/IA licenseurl PD/CC0)入 code+單測;W2 每源 N≥20 抽樣人工對源頁審計(§4.1/§6.1/§2)——已修+拍板 P7 |
| D-10 | doctrine | minor | 憲章版本錨定過期(v1.39.0/:141/:145/:165)且擬升版 v1.40.0 撞現行號 | 全檔重錨 v1.40.0(:142/:146/:166,grep 實查);入憲改擬 v1.41.0(文件頭/§6.2/文末)——已修 |
| D-11 | doctrine | minor | ctext 列 A 軌表但裁決 metadata-only——backfill 照表灌 license_regime 即成破軌口 | ctext 移 C 軌(metadata_only、fulltext_eligible=false,P5 備註保留);--dry-run 驗收加 fulltext_eligible=true 清單人工過目(§1/§2)——已修 |
| D-12 | doctrine | minor | `/api/wave` 放量觸發僅 `_valid` session,無 superuser gate(RBAC 下受控群組亦可放量) | /api/wave 與 probe 端點同 approve 之 superuser gate+寫 _audit(§5.2)——已修 |
| D-13 | doctrine | minor | W3 批次 probe 自動外呼 re3data note 解析出的任意 URL,無驗證即打數百未知主機 | URL 驗證前置(https/同源/拒 IP 直連內網);首輪批次範圍列拍板 P11(§4.1/§2/§8)——已修+拍板 P11 |
| C-1 | completeness | **blocker** | M3 backfill 未窮舉 3,593 列(69+3,507+2=3,578,manual_file 16 源未定)——fail-closed 上線當天切斷 manual_curation 既有 sanctioned 策展路 | 全量對帳矩陣逐群組窮舉:53 active+16 manual_file active(追認+閘/trigger 豁免明文)+3,524 proposed=3,593;W0 驗收=加總相符零 NULL 桶(§3.2/§4.2/§2)——已修+拍板 P1 |
| C-2 | completeness | major | 「公版書全文未接」與 repo 事實不符——五支既有 fetcher 已落 philosophy_work_text,新工具將雙落點重抓(違 #12/#29c) | §0.2 前提更正;§4.3 分工裁決(方案 A/B)列 P10;同書去重閘+`--inventory` 盤點;W2 驗收排除既有部數(§0/§4.3/§2/§8)——已修+拍板 P10 |
| C-3 | completeness | major | OAI-PMH(set/日期流式)與 query×source 排程模型結構不相容,計畫未 spec | 排程單位=set/日期窗虛擬 query(origin='oai_set')+`knowledge_source_cursor` 表完整 DDL(§3.5/§4.2)——已修 |
| C-4 | completeness | major | quota_limit/quota_window_seconds 是死欄——§4.2 修改清單無任何視窗額度閘實作(FinMind `_quota_gate` 對偶缺席) | acquire 修改補 ⑦ quota gate(原子遞增+視窗滾動+90% 停);W0 驗收「quota_limit=3 第 4 次被閘」實測(§4.2/§2)——已修 |
| C-5 | completeness | major | 紅線「probe 通過才 approve」無機械落點——UI 對未 probe 源照樣可按 approve | curation.approve/activate 前置=近 30 日 probe http 200 記錄,否則拒;--force 需 reason 留痕;UI 鈕 disabled+提示(§4.2/§5.1/§6.2-6)——已修 |
| C-6 | completeness | major | 來源宇宙漏大戶:美聯邦公版(FRASER/FOMC/EDGAR/CRS)、OA 書籍(DOAB/OAPEN)、Perseus/Kanripo、pre-1930 投資經典書單——恰在自稱最高 ROI 之投資/經濟域 | §1 增 A 軌政府公版子表+B 軌 DOAB/OAPEN/Perseus+Kanripo+D 軌投資經典策展書單(併 P10)(§1/§8)——已修 |
| C-7 | completeness | major | A 軌合規核心「逐件公版判定演算法」全空白;PD 司法轄區(US-PD vs 台灣 life+50)未拍板 | 併 D-9 判定規則表;PD 轄區基準列 P7(建議採來源方宣告+US-PD 存 provenance)(§4.1/§8)——已修+拍板 P7 |
| C-8 | completeness | major | /api/wave 背景併發無互斥(_JOBS 僅記憶體 dict,admin 重啟失憶)——多進程同打一源=pace×N | harvest 啟動 pg_try_advisory_lock 單飛;/api/wave 觸發前 DB lock 預檢拒併行(409);W0 並行第二進程被拒實測(§4.2/§5.2/§2)——已修 |
| C-9 | completeness | major | v_knowledge_coverage_domain 留「SELECT ...;」佔位,違本計畫自訂 v1.39.0 逐表 DDL 標準;P2 拍板時儀表不存在=盲拍 | 依 code 事實(knowledge_item.domain NOT NULL/item_text license CHECK)寫全完整 SQL 入 §3.6——已修 |
| C-10 | completeness | minor | 狀態機不完備:圖示稱 exhausted 可 reopen 但無 reopen 動作;rejected 死終態無再議路徑 | action CHECK 補 'reopen';轉移補 exhausted→active、rejected→proposed(皆 superuser+reason)(§3.2/§3.3)——已修 |
| C-11 | completeness | minor | probe 對模板 NULL 之 proposed 源無從組請求——re3data 激活鏈條中斷 | probe 補 `--use-draft`(讀 adapter_config.draft,probed_with='draft');無模板無草稿→'no_template' 終態(§4.1)——已修 |
| C-12 | completeness | minor | admin 三處具體度缺口:3.5k 列無分頁/coverage 30s 全表聚合/POST 格式與既有 urlencoded 慣例不一致 | /api/sources 預設篩選+limit/offset;coverage 讀輪末 snapshot+輪詢 60s;action 端點從眾 urlencoded(§5)——已修 |
| C-13 | completeness | minor | migration 無復原路徑(3,593 列 UPDATE 錯置無後路,違 #6) | --apply 前置=pg_dump -Fc -t knowledge_source 快照(#30),入 S0 驗收(§4.1/§2)——已修 |
| E-1 | engineering | **blocker** | DOI 形態異質致跨源去重失效:URL 形 5,359 vs 裸形 88,377、既有重複 152 對實證;W1 多源扇出必爆萬級重複=顧問檢索沉默污染(#8) | M4:norm_doi 上移 curation.py 為 SSOT+promote 入庫前正規化+一次性合併 migration(--dry-run);W0 驗收跨形態重複對=0;promote 移出零修改名單(§3.2/§4.2/§2)——已修 |
| E-2 | engineering | **blocker** | probe 例外+promote 零修改組合出洩漏路:probe proposed 源→staging pending→輪末全域 promote→未拍板資料入生產庫 | probe path 不呼叫 stage()(收集器,staging 零寫入)+promote JOIN active 第二道+trigger 第三道;W0「probe 後 staging 增量=0」實測(§4.1/§4.2/§3.7/§2)——已修 |
| E-3 | engineering | major | promote 單交易全量 fetchall+900s subprocess timeout——百萬級 staging 必超時 rollback=livelock+長交易鎖表 | promote 批次化(LIMIT N 迴圈+逐批 commit,介面/mapper 不動);harvest 輪末 timeout 取消;W2 十萬列輪內收斂實測(§4.2/§2)——已修 |
| E-4 | engineering | major | W2 深抓/增量語意與帳本不相容:status='ok' 即永不重排,token 存 note=死狀態;單跑 limit 硬編 500 | M5 status 增 'partial' 納排程+cursor 表頁級斷點;harvest 對 wave≥2 附 --deep --max-pages,回滿頁記 partial;刪「帳本全不動」宣稱(§3.2/§3.5/§4.2)——已修 |
| E-5 | engineering | major | P3/P4 解鎖後既有終態帳(skip_pdf 448/skip_no_oa 5,634)被 PENDING_WHERE 永久排除,最現成的全文永不重試 | P3/P4 拍板附帶一次性 requeue,數字入 W2 驗收與 review_log(§2/§4.2/§8)——已修 |
| E-6 | engineering | major | 覆蓋率視圖=對最熱寫入表 30s 全表聚合(staging 無 source_key 索引,規模化後常態 seq-scan) | 補 (source_key,status) 索引+輪末 snapshot 表,admin 讀 rollup、視圖降 ad-hoc(§3.6/§5)——已修 |
| E-7 | engineering | major | W1「零新碼補 15 具名 NULL」不成立:pubmed 兩段式 esearch→esummary、biorxiv ID/日期驅動無 {query} 進不了排程;repec 需 token;「+7~10 活源」未實證(#9) | lever 3 改「probe 後定案」:pubmed/biorxiv 移 W2;repec token 列 P12;目標值以 probe 結果回填不預寫(§2/§1/§8)——已修+拍板 P12 |
| E-8 | engineering | minor | 「69 源→active」數字錯:實查 enabled=69 中僅 53 有模板,16 為 manual_file 導管——照計畫 W0 對帳必失敗 | backfill 矩陣改 53/16 分列並各定語意(併 C-1)(§3.2)——已修 |
| E-9 | engineering | minor | pace 職責雙落點未分工;cooldown 只在 acquire 檢查——harvest 冷卻期仍 spawn 立即退出之 subprocess 空轉數小時 | 明定 harvest=組合間 pace、acquire=分頁間 pace;排程 SQL LEFT JOIN health 直接濾除 cooldown 中源(§4.2)——已修 |
| E-10 | engineering | minor | coverage_domain 佔位之 hedge(「若 item 無 domain 欄」)與 code 事實矛盾——knowledge_item.domain NOT NULL 且有索引(#15「我以為」) | 依實查欄名寫全視圖、刪 hedge(併 C-9)(§3.6)——已修 |
| E-11 | engineering | minor | enabled/approval_status 雙旗無一致性不變式(approve 了卻默默不跑型死角) | enabled 退役、排程唯一閘=approval_status(併 D-6)(§3.2)——已修 |
| O-1 | ops | **blocker** | quota 有欄無閘:Unpaywall/OpenAlex 官方 100k calls/day,pace 0.5s 連跑=172.8k/day 必破;254k DOI backlog 首日撞牆——FinMind 教訓原樣重演(「低於速率上限≠安全」) | quota gate 機械落地(併 C-4)+§1 逐源填官方 quota 值+backlog>100k 走官方 DB snapshot(ToS 認可 bulk 路)(§1/§4.2/§7)——已修 |
| O-2 | ops | major | 跨行程限速零協調:pace 為行程內狀態,/api/topic 可重複點擊生多個 detached harvest=n×pace,IP-sustained-ban 標準成因 | advisory lock(harvest 全域+acquire per-source)+API 觸發前 DB lock 預檢+跨行程 pace 依 health.last_call_at(§4.2/§5.2/§2)——已修 |
| O-3 | ops | major | OAI 斷點押短命 resumptionToken(過夜必 badResumptionToken)且 note 欄被 upsert 覆寫=無 durable 游標;深分頁無 mid-combo checkpoint | durable 游標=from/until datestamp 窗存 cursor 表;token 僅 session 內;頁級 commit;驗收升級 kill -9 跨行程續傳(§3.5/§4.2/§2)——已修 |
| O-4 | ops | major | 全文抓取路徑(fetch_pd/oa_fulltext 直打任意 host)整條游離於審批/限速/健康度體系外——suspend gutendex 照打 gutenberg.org | 五列 pseudo-source 收編(§1 F 軌):工具啟動查 active+per-host 分桶 pace+同 health 記帳;§6.2-2 補「全文通道亦經審批閘」;既有游離 fetch_* 收編或豁免留痕(§1/§4.1/§4.3/§6.2)——已修 |
| O-5 | ops | major | Project Gutenberg 官方明文禁機器人批量直抓主站(違者 IP ban);gutendex.com 為社群小服務不堪放量 | 全文走官方 mirror/rsync 或 RDF/CSV catalog dump 離線解析;metadata 放大改自架 gutendex/catalog dump;W2 驗收「零主站批量直抓」log 稽核(§1/§4.1/§2)——已修 |
| O-6 | ops | major | auto-suspend 只降不升:一次維護窗/網路抖動即永久踢出排程,無人值守過夜批單調流失活源;輪內 5 連錯與健康表 8 連錯兩套閾值未對齊 | 錯誤兩級制:temp 錯走 cooldown 指數階梯自癒(15m→24h 封頂,非狀態變更不違「只降不升」),perm/階梯走滿才 suspend;兩套閾值關係明文;5xx 風暴自癒實測(§3.4/§2)——已修 |
| O-7 | ops | minor | W1 時程漏 per-combo subprocess 開銷(直譯器冷啟+connect 1-2s)——實為 3-5s/combo≈3-5 天,非 30-45h | 估算誠實化+W0 實測 100 組合中位數回填(#9);可選單行程多 query 批次、不上併發(§2/§7)——已修 |
| O-8 | ops | minor | 覆蓋率視圖現況 79ms@302k 無虞,但億級後 30s 輪詢=常態全表掃與 harvest 爭 I/O | 輪末 snapshot 表(O(源數))+輪詢 60s(併 E-6)(§3.6/§5)——已修 |
| O-9 | ops | minor | 磁碟預算漏 W2 深抓 metadata 行項(最大乘數,可達 60G+)且 staging 無保留策略,億級 staging 拖垮 #30 跨機 dump | 預算補行項(max_pages 欄推硬上界)+staging 歸檔策略(promoted payload 截斷/移歸檔表,staging_id 無 FK 已預留);「25 列×2KB」修正為實測 171B/列(§7/§3.2)——已修 |
| O-10 | ops | minor | dump 磁碟水位僅啟動檢查——百 GB 級多小時載入,可能越線後才發現 | load_knowledge_dump 每 checkpoint 寫入點 shutil.disk_usage 檢查,越線即停(checkpoint 保 resume-safe)(§4.1/§7)——已修 |

---

*本計畫遵守:憲章 **v1.40.0** 知識層多域擴充準則(:146)+全文准入三軌+共同不變式①-④(:142)+隔離不變式+隱私上限(:166);CLAUDE.md v1.18 #1/#6/#8/#9-12/#15/#20/#24/#25/#28/#29/#30;偵察事實基礎=2026-07-10 live DB 實查+六支引擎全讀(machinery/treaty-console/world-catalog 三視角)+**四鏡對抗審查修訂(doctrine/completeness/engineering/ops,47 項發現全數修入,§9 留痕)**。*
