# 知識層全文覆蓋率提升計畫（plan-first #20；待 Steward 拍板）

**日期**：2026-07-28  
**性質**：[I] 執行層計畫（不動治權 [N] 判準；全文准入三軌／能抓≠該抓／素養層不進預測管線原樣）  
**觸發**：admin `http://localhost:8500/gov`「來源治權 + 覆蓋率」per-domain 覆蓋極低（用戶觀測）  
**本輪範圍**：**只寫計畫、不實作**放量 harvest／fetch（用戶明示）  
**實證時點**：2026-07-28 本機 PostgreSQL 唯讀查詢（下表數字皆 live，非估算）

---

## 0. 一句結論

**應寫本計畫再實作（yes）**。儀表「覆蓋」＝`length(content)>200` 的 item 占比，**≠** CLAUDE #29(b)「license 允許的可檢索終態」。主因分桶：**多數學術域 0%＝未嘗試全文（pending）**；**computer_science 等低％多為 skip_no_oa／skip_license 終態帳（授權／OA 現實，分子本來就不該進）**；**erp_tiptop 7%＝短文門檻假低（已 100% 有 `owned_local` 全文且已 embed）**。

---

## 1. What／Why／非目標

### 1.1 What

1. **對齊覆蓋率定義**與分桶診斷帳（授權可抓未抓／license・OA 阻擋／已抓未切句・未 embed／儀表假低）。  
2. **有界提高「真覆蓋」**：僅對**授權可抓且尚未終態**的庫存，走既有 `fetch_oa_fulltext`／resolvers／PDF（另案）→ `build_sentences` → `embed_knowledge`（#29b 終態鏈）。  
3. **儀表誠實化**：gov 頁分母／分子改為可機驗之終態分桶，禁止把 blocked 或短文 ERP 讀成「沒抓」。

### 1.2 Why

- 用戶看到的「0%／7%」易被誤讀為系統失敗；若不先分桶，放量抓取會違「能抓≠該抓」、浪費 Unpaywall 額度、或把 NC／未 OA 硬當洞。  
- 庫存事實（G-HAR-1 partial／U6 F-U6-3）：大量 metadata **無全文亦無** `knowledge_fulltext_status`＝**未做**，與「已 blocked」不同。  
- HANDOFF **件 B**：harvest 熔斷停於 ~99k abstracts 待續——與今日 **global pending ≈ 108,022** 同族債。  
- 跨 harvest／license／embed／多域、≥3 步 → CLAUDE #20 plan-first。

### 1.3 非目標（硬邊界）

| 不做 | 理由 |
|---|---|
| 盲目把 gov「覆蓋％」拉高當 KPI | 覆蓋≠可答；blocked 不得進分子 |
| 變更全文准入三軌／鬆 license CHECK | 憲章 v1.36.0+；G-FT-1＝none |
| FinMind／FRED／市場 sync | API 凍結；本計畫零市場 API |
| 太陽能↔儲能等他域進化閉環 | HANDOFF 近程不做 |
| 素養層進預測管線／產因子 | 隔離命門 |
| 本計畫拍板前放量 Unpaywall／IA／深抓 | 本輪明示不實作；放量另碼 |
| 宣稱「全域 harvest 完成／可答完備」 | R6／U6 已禁；僅分階段驗收 |

---

## 2. 現況實證（2026-07-28）

### 2.1 儀表公式（code 事實）

`scripts/serve_admin_console.py` `_gov_data`：

- **items**＝`knowledge_item` per domain  
- **fulltext**＝同 domain 存在 `knowledge_item_text` 且 `length(content)>200` 的 distinct `item_id`  
- **覆蓋**＝`100 * fulltext // items`  

頁面標題寫「至可檢索終態」，但公式**未**檢查：sentences／embed／`knowledge_fulltext_status`／license 允許分母。旁註已承認 `skip_license`／`skip_no_oa`＝終態非漏做——與分子定義**不一致**。

### 2.2 全域

| 指標 | 數值 |
|---|---|
| `knowledge_item` | 270,333 |
| gov 口徑全文（`length>200`） | 14,339 |
| `knowledge_fulltext_status` 列 | 18,885 |
| **無全文且無 status（pending／未嘗試）** | **108,022** |
| **無全文但有 status（blocked／skip 終態）** | **16,374** |
| `crossref_works` pending／有 status／有 text／總 | 63,622／13,719／3,091／77,972 |

**終態帳 status 全域分佈（前段）**：`skip_no_oa` 9,228 · `skip_license` 3,978 · `abstract_none` 1,552 · `abstract_fetch_error` 1,204 · `skip_pdf` 1,173 · `skip_fetch_error` 894 · …

### 2.3 用戶所列 domain 分桶（誠實判決）

| domain | items | gov_ft | pending（無文無帳） | blocked／skip（無文有帳） | 判決 |
|---|---:|---:|---:|---:|---|
| erp_tiptop | 141,873 | 10,652 | 0 | 0 | **儀表假低**：全部 `owned_local`+`local_private` 已有 text；**全部已 embed 可檢索**；僅 `length≤200` 占大多數（0–50：84,088；51–200：48,622） |
| medicine | 12,262 | 0 | 12,262 | 0 | **未做**（全 pending；源=`crossref_works`；DOI 形≈全） |
| social_sciences | 12,252 | 0 | 12,252 | 0 | **未做** |
| engineering | 9,568 | 0 | 9,568 | 0 | **未做** |
| chemistry | 9,444 | 92 | 8,994 | 61 | **主因未做**；另有短文／embed 缺口（any_text 389；sent 未嵌≈382） |
| computer_science | 7,351 | 85 | 187 | 7,079 | **主因授權／OA 擋**（`skip_no_oa` 4,611＋`skip_license` 1,579 等）；pending 僅 187 |
| agricultural_and_biological_sciences | 4,870 | 0 | 4,869 | 1 | **未做** |
| physics | 4,586 | 0 | 4,586 | 0 | **未做** |
| arts_and_humanities | 4,350 | 0 | 4,350 | 0 | **未做** |
| electronics | 4,259 | 0 | 4,259 | 0 | **未做** |
| biochemistry_genetics_and_molecular_biology | 3,634 | 0 | 3,634 | 0 | **未做** |
| environmental_science | 3,345 | 43 | 1,832 | 1,470 | **混合**（pending≈半；blocked 以 `skip_no_oa`/`skip_license` 為主） |

> **誠實答用戶「0% 是授權擋還是未做？」**  
> - **medicine／social_sciences／engineering／physics／arts_and_humanities／electronics／biochem／agri（幾乎全部）→ 未做（pending）**，不是授權擋帳。  
> - **computer_science → 多為授權／OA 擋已落帳**；gov 0–1% 不可靠當「漏抓」。  
> - **environmental_science → 混合**。  
> - **erp_tiptop 7% → 非缺口**，是 `length>200` 與「可檢索」錯位。

### 2.4 對照既有管線／裁決

| 環節 | 落點 | 備註 |
|---|---|---|
| 終態定義 | CLAUDE #29(b)；R6 `TERMINAL_VOCAB` | 允許終態＝全文→句→embed；或 blocked 帳 |
| 全文三軌 | 憲章第三部（公版／CC 白名單／`owned_local`+`local_private`） | G-FT-1 CHECK 已親驗 |
| OA 抓取 | `scripts/fetch_oa_fulltext.py` | Unpaywall；白名單才入庫；其餘寫 status |
| PD／源解析器 | `fetch_pd_fulltext.py`＋resolvers 計畫（07-12 已拍） | 非 crossref 大宗 |
| 切句／嵌入 | `build_sentences`／`embed_knowledge`；`refresh_knowledge_pipeline` | chemistry 等有「已文未嵌」本地債 |
| 熔斷／半套 | HANDOFF 件 B；G-HAR-1 partial；U6 F-U6-3 | pending 庫存≠ blocked |
| 閉合先例 | `augur_knowledge_fulltext_closure_master_plan_20260713.md` | 明示 OA 巨量積壓**另軸**；本計畫承接「診斷＋儀表＋有界 OA／embed」 |

---

## 3. 覆蓋率定義（計畫鎖定，供拍板）

### 3.1 三個互不混淆的指標

| 指標 | 定義 | 用途 |
|---|---|---|
| **A. 可答覆蓋（真終態）** | 有 `item_text` 且至少一句已 embed（或 owned_local 等同可檢索）／**或**有 `knowledge_fulltext_status` 終態列 | 對齊 #29(b)；advisor 可引用或誠實不可答 |
| **B. 授權可抓待辦** | 無 text、無 status（pending）；可選再篩 DOI／有 resolver | **唯一應放量提高的分子池** |
| **C. gov 舊式全文率** | `length(content)>200`／items（現行） | 僅歷史對照；**不得**單獨當「可檢索覆蓋」headline |

### 3.2 分母誠實化（建議拍板後改 UI）

對每個 domain 同時顯示四欄（唯讀 SQL，零寫）：

1. `items`  
2. `answerable`（有 embed 或等價）  
3. `terminal_blocked`（有 status、無 text）  
4. `pending`（無 text、無 status）  

**「覆蓋（可答）」**＝`answerable / items`；另列 **「終態完成率」**＝`(answerable + terminal_blocked) / items`（含誠實不可答）。  
**禁止**用 `answerable / (items - blocked)` 悄悄抬高而不標註。

---

## 4. 如何提高覆蓋率（執行策略，非本輪動工）

提高＝只啃 **B. pending**，並補 **已抓未 embed**；**不**把 blocked 洗成全文。

| 槓桿 | 做法 | 預期對儀表／真覆蓋 | 授權 |
|---|---|---|---|
| **L0 儀表對齊** | 改 `_gov_data`／HTML 分桶 | erp 由「7%」改讀「可答≈100%」；0% 域改顯 pending 大 | `FT-COV-DASH`（可先於放量） |
| **L1 診斷帳固化** | 唯讀 script／admin API 輸出分桶 JSON＋snapshot | 可複現、防口語假兆 | 含於 L0 或 `FT-COV-LEDGER` |
| **L2 本地補洞** | `build_sentences --scope items`＋`embed_knowledge`（chemistry 等 sent_no_emb） | 真可答↑；不打外部 API | `FT-COV-EMBED`（庫內） |
| **L3 OA pending 有界批次** | `fetch_oa_fulltext.py --domain X --limit N`（#25 先 3；步調既有；熔斷既有） | pending→（少數 fetched＋多數 skip_* 終態）；**終態完成率↑、gov 全文率僅溫和↑** | **`HAR-ext`**（知識外部 API；≠解凍 FinMind／FRED） |
| **L4 非 OA 專屬源** | 沿用 resolvers／PDF 另案 | 僅該源積壓 | 既有拍板碼或另開 |
| **L5 上游深抓** | harvest 再開 | **增加** pending，不直接提高覆蓋 | 件 B 續跑另授權；本計畫不預設 |

**預期誠實敘事**：L3 跑完某域後，gov「全文％」可能仍低（大量 `skip_no_oa`），但 **「終態完成率」應趨近 100%**——這才是成功，不是硬灌 CC 全文。

---

## 5. 分階段（建議）

| 階段 | 名稱 | 內容 | 驗收 | 依賴拍板 |
|---|---|---|---|---|
| **P0** | 診斷帳＋儀表 | 固化 §2 類 SQL 為可重跑腳本；gov 改 §3.2 四欄；標題去「可檢索」誤導或改寫 | 頁面數字＝腳本輸出；erp 可答≈100% 可見 | `FT-COV-DASH` |
| **P1** | 庫內 embed／句子補洞 | 掃 `ft_no_sent`／`sent_no_emb`；chemistry 優先；走 refresh DAG 或單腳本 | 該池歸零或 ledger 記 junk／CLEAN 排除 | `FT-COV-EMBED` |
| **P2** | pending 域最小探測 | 每重點域 `fetch_oa_fulltext --limit 3`；記 fetched／skip_* 比例 | #25 煙測帳；估 L3 產量 | `HAR-ext`（窄窗） |
| **P3** | 有界放量 | 按 P2 比例選域；`--limit` 批次＋resume；見訊號即停 | 該域 `(answerable+blocked)/items` 目標（建議 ≥95% 終態完成；**不**訂 gov 全文％ KPI） | `HAR-ext`＋節奏碼（如 `FT-COV-BATCH`） |
| **P4** |（可選）件 B／深抓銜接 | 僅當 Steward 要擴 metadata | 另計畫；本檔只留接口 | 另碼 |

**建議近程一次拍**：`FT-COV-P01`＝P0＋P1（零外部放量）＋P2 最小探測授權併入或拆開。

---

## 6. Schema／Python 規畫（憲章 v1.39.0）

### 6.1 表（不產新表為預設）

| 物件 | 角色 | 本計畫讀／寫 |
|---|---|---|
| `knowledge_item` | metadata；domain／source_key／external_id | 讀 |
| `knowledge_item_text` | 全文；license／access_scope | 讀；L3 寫（既有 writer） |
| `knowledge_fulltext_status` | blocked／skip 終態帳 | 讀；L3 寫 |
| `knowledge_sentence`／`knowledge_sentence_embedding` | 切句／可檢索 | 讀；P1 寫 |
| `knowledge_staging` | 上游；本計畫不主攻 pending staging | 讀（對帳） |
| `knowledge_source` | adapter／approval | 讀；**不**擅自 activate |

**可選（僅當 P0 要歷史對照）**：`knowledge_coverage_snapshot`（若已有則复用；無則 **可不建**——admin 即時查即可，避免 DDL 搶 #30）。

### 6.2 Python／腳本

| 檔 | 角色 | 階段 |
|---|---|---|
| `scripts/serve_admin_console.py` | `_gov_data`／`gov_dashboard_html` 分桶 | P0 |
| **新** `scripts/report_knowledge_fulltext_buckets.py`（建議） | 無參印矩陣；`--json` 輸出 §2 類分桶；零 API | P0 |
| `scripts/fetch_oa_fulltext.py` | OA pending→text 或 status | P2–P3 |
| `scripts/build_sentences.py`／`embed_knowledge.py` | 補洞 | P1 |
| `scripts/refresh_knowledge_pipeline.py` | `--status`／有界 DAG | P1／監看 |
| `scripts/verify_roadmap_r6_s12.py` | 終態詞彙哨兵不回退 | 回歸 |
| 既有 resolvers／PDF／local_files | 非 crossref 大宗 | 另案引用 |

**強制不變式**：license CHECK；owned_local⇒local_private；逐字零 AI；predict 零 import knowledge。

---

## 7. 驗收

| ID | 條件 | 否證 |
|---|---|---|
| V1 | gov 同時顯示 answerable／blocked／pending | 仍只顯示 length>200％ 當「可檢索」 |
| V2 | 用戶表內「未做」域在 P2 後有 status 或 text 樣本（每域≥3 嘗試帳） | 仍全 pending 卻稱已處理 |
| V3 | P1 後 chemistry（等）sent_no_emb 池實測下降 | 只改文件 |
| V4 | P3 目標域終態完成率≥約定閾；skip_* 計入完成 | 用 gov 全文％當唯一 KPI |
| V5 | 全程無 FinMind／FRED 呼叫；無他域進化閉環開工 | 混進市場 API／太陽能↔儲能 |
| V6 | 不宣稱全域可答完備 | 口語／報告越權 |

---

## 8. 風險與護欄

| 風險 | 處置 |
|---|---|
| 把 skip_no_oa 當 bug 狂重試 | PENDING 排除已有 status；禁刪帳重問當「提高覆蓋」 |
| Unpaywall／源站 ban | #24 步調＋連錯熔斷；當日停、翌日再議 |
| 儀表改完仍口語說「0%＝失敗」 | P0 文案＋本計畫 §0 句 |
| ERP 短文被誤刪／重抓 | erp 走 owned_local dump-only；L3 **排除** erp_tiptop |
| DDL 與 dump 鎖衝突 | P0 預設零 DDL |
| 與件 B 搶跑 | P3 前確認 harvest 靜止或錯峰 |

---

## 9. Steward 拍板碼（建議）

| 碼 | 含義 | 建議預設 |
|---|---|---|
| **`FT-COV-PLAN`** | 核准本計畫書（what／分桶／階段／非目標） | **請先拍** |
| **`FT-COV-DASH`** | 核准 P0 儀表＋分桶腳本（零外部 API） | 建議與 PLAN 同批 |
| **`FT-COV-EMBED`** | 核准 P1 庫內句子／嵌入補洞 | 建議同批 |
| **`HAR-ext`** | 知識域外部 OA／fetch 窄窗或放量（R6 既有語彙） | **另句**；本輪不預設執行 |
| **`FT-COV-BATCH`** | P3 批次大小／域清單／停損 | 僅在 HAR-ext 後 |
| **`FZ-keep`** | FinMind／FRED 維持凍結（本計畫不觸） | 預設維持 |

**建議回覆句例**：`FT-COV-PLAN + FT-COV-DASH + FT-COV-EMBED`（先儀表與庫內）／或 `FT-COV-PLAN` 僅收計畫、實作另開。

---

## 10. 與既有文件關係

- **承接**：R6 終態定義；U6／G-HAR-1 partial；`knowledge_fulltext_source_resolvers_plan_20260712`；`augur_knowledge_fulltext_closure_master_plan_20260713`（OA 巨量＝另軸——本計畫把「診斷＋儀表＋有界 OA」正式立軸）。  
- **不取代**：PDF 抽取計畫、件 A 三通道、深抓 S2–S4。  
- **位階**：[I]；入憲改 [N] 另開案。

---

## 11. 本輪交付清單

- [x] DB 唯讀分桶實證（§2）  
- [x] gov 公式對照 code（§2.1）  
- [x] 本計畫書落地  
- [ ] 實作／放量——**明示不做，待拍板碼**

---

**本檔完。標 [I]。零 FinMind／FRED。提高覆蓋＝清 pending＋補 embed＋儀表誠實；≠灌全文進授權擋項。**
