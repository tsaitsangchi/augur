# 全文落地與逐字理解計畫 v3.0(還債收斂版:verbatim integrity → 載體窮盡 → 全向量化)

**日期**:2026-07-04(v3.0;v1.x→v2.0 歷程見 §十一)　**系列**:知識三部曲之三
**修訂依據**:六鏡對抗審查 **15 案全數確認**(9 high/6 medium,每案皆 psql/grep/EXPLAIN 實錘,見 §五)+ 用戶全向量化與逐字意涵思想窮盡 directive + 今晨合規稽核債(stale chunk/textnorm 查詢端違約/framework 非冪等/治權升版)納入
**合成法**:三架構師對抗骨架合成——A(逐字理解優先)為主幹 × B(工程落地優先)之 Phase 0 債務前置鏈+共同不變式塊 × C(角色成果優先)之 R0-R4 角色驗收階梯
**治權**:靈魂 v1.4.0 · 原則精華 v1.7.1 · **憲章 v1.22.0**(「共同不變式」+「檢索與顧問前端」小節;v2.0 檔內 v1.20.0 引註已同步)· CLAUDE #28/#29
**排序公理**:逐字鏈完整性(verbatim integrity)**>** 理解載體窮盡(定義/意涵/思想入庫)**>** 索引擴張(嵌入)。嵌入=索引非內容(命門 7),故 en 全向量化永遠排在逐字鏈修復與載體完備之後。

---

## 〇、命門定錨(v2.0 七條不變 + v3.0 新增三條)

1. **逐字逐句定義不由 AI 生成入庫**;合法載體=公版辭書/註疏(已實現:lexicon 154,875 條)+ concordance(已實現:49,106,830 處,「道」5,026 處)+ 純計算統計 + 真實文獻 citation。AI 只在回答時刻組織真兆。
2. **用戶終極目標僅以「漸近全知北極星」形式表述**;字面不得鑄入 schema/表名/措辭(omniscience 一律稱 coverage;禁字掃描現況=0 出現,升為 verify 常備機器證明);系統必答「不知道」且分三級(§九)。
3. 多域知識素養層**零量化價值**、不進預測管線、不產因子(隔離不變式擴及 `augur.knowledge`,機器強制)。
4. **確定性優先**:結構/統計/對齊/圖譜各層一律計數、閉式公式、字串規則;禁 LLM 判斷入庫(derivation_method 封閉集=DB 硬擋)。
5. **AI 記憶物理隔離**:v3.0 建議改採**「不落庫」案**(拍板 5)——AI 產出留 harness/檔案層,DB 零 AI 產出,「不落庫」寫成 charter 可查宣稱。理由:憲章 v1.22 僅有「禁 AI 生成入庫」+「顧問唯讀零寫回」,隔離籠落庫=未經憲章授權之新寫路徑;**禁先建籠後補憲**(現況真空合規:僅 public schema、零 is_ai_generated 欄、advisor 零 INSERT/UPDATE,psql/grep 實查)。
6. **宣稱誠實化**:各層能力邊界入庫可查(charter 小表);guard 措辭閘——統計陳述不得升格為知識斷言。
7. **嵌入=索引非內容**:向量化的都是真兆原文;向量命中後 guard 仍逐字引用原文(v3.0:升為定位驗證,見命門 8)。
8. **〔新〕逐字承諾=機器閘非顯示層**:verify_verbatim 必在 guard 閘鏈內,引文雙基準=「∈ citation **且** ∈ 現行 work_text 定位子串」——「引用作答」對原文**他證**、非對副本自證。實錘:1,189 個 stale chunk 全數已嵌可穿閘(guard.py:23 只驗 chunk 副本;verify_verbatim〔retrieval.py:74〕唯一呼叫者=CLI 顯示層 query_philosophy.py:18)=憲章 v1.22 line 133-134 防幻覺承諾與實作之真矛盾。
9. **〔新〕誠實雙向**:假不知道與編造同罪。實錘:textnorm 查詢端失守 → `lexicon_lookup('knowledge')=0`(庫存 'knowledg' 3 筆)、`concordance_lookup('philosophy')=0`(庫存 'philosophi' 18,310 處)、簡體 '学'=0(庫存 '學' 2 筆)——系統對明明擁有的知識以固定誠實句說謊。誠實率測例必雙向覆蓋(false-positive 編造+false-negative 假不知道)。
10. **〔新〕物化完成 ≠ 驗收通過**:每 W 拆「灌庫/驗收」雙欄分記(落地格式見 §八狀態表),「竣工」一詞保留給驗收通過。實錘:W5 嵌入量屬實但驗收零落地——rank@10 全 repo 零執行體、117 junk chunk 在 HNSW 佔槽位、lexicon/sentence 嵌入表全 repo 無讀端(write-only)。

## 一、八層金字塔(v3.0 修訂)

```
L6   治理橫切   共同不變式(a)-(d)· verify_text_integrity(含 C-chunk 定位子串)· hash 蓋章
               · 游標生命週期 · derivation_method 憲欄 · charter 宣稱表 · AI 產出不落庫(拍板5)
L5   角色層     「誠實博學的我」:answer.py=檢索編排器(單閘 guard)· 三級誠實 · R0-R4 階梯
               · coverage 四指標+instance 身分 · profile 自報機器/時點
L4   語意層     三粒度嵌入:chunk 63,601 已嵌 · lexicon 154,875 已嵌 · zh 句 33,314 已嵌 · en 句 0(拍板)
               · 讀端三 API(現 write-only,W8 補)· zh/en 句分表(拍板 1,先於放量)
L3.5 衍生層     經-注-疏對齊 · 跨語平行(章節錨定)· 詞義歷時 · 引文網(n-gram)· knowledge_edge
               · school_thinker(現 0.41%:揭露先行/回填後行,拍板 4)
L3   定義層     knowledge_lexicon 154,875(寫入端 done;查詢端 textnorm 履約=債 W2.7)
L2.5 統計層     knowledge_term_stats(~448k 列)+ 三層可解率視圖(窮盡度量化)+ 共現 PMI 按需 SQL
L2   結構層     sentence 1,539,019(全量 0 stale 已驗)· concordance 49,106,830(zh 字面驗 0 錯 0 orphan)
L1   全文層     work_text 31,778 · item_text 0(誠實標示:item 鏈未起步,拍板 12)· corpus_class 閘落 builder(債 W2.5)
L0   來源層     registry 三表(query 4,706/source 3,592/taxonomy 4,798)· 兩機 merge 先決(W0)
```

**逐層修訂要點**(數字出處統一見 §五):

- **L0 來源層**:前置**兩機 merge 不變式**——舊機 41,888 vs 本機 25,031 item(差 16,857),pg_dump+`external_id ON CONFLICT` 冪等灌入(分鐘級零 API,vs 重抓=已付過的限速 API 時數再付一次+對第三方重複施載);**harvest_log 必須一併**(resume 心臟,不併則本機把舊機已 ok 的 query×source 再打一遍);拍板單一寫入機(拍板 6)。expansion TODO ①-⑥ 與本計畫脫鉤、不阻塞。
- **L1 全文層**:corpus_class 閘**現況零 builder 引用**——chunk builder(build_philosophy_chunks.py:115-117)無任何 reference 閘、sentence builder(build_sentences.py:86)用 work_type 白名單且實證漏接 Roget(work_type='book')與三部注疏('philosophy_classic');reference chunk=0/句=0 **純屬「未重跑」僥倖非閘門保證**。修法:閘門鍵一律 `corpus_class='literary'` 單一語意欄、廢 work_type 白名單(債 W2.5);DEFAULT 'literary' fail-open 修法列拍板 13。**item_text=0 誠實標示**:sentence/concordance/chunk 鏈 100% 建於 philosophy 語料,item 內文理解鏈尚未起步——逐字窮盡現僅及 philosophy 語料,後續邊界列拍板 12。
- **L2 結構層**:句 1,539,019 全量 0 stale(實測 real 6m15s)、zh concordance 708,443 列字面驗 0 錯 0 orphan——標「**已驗**」非「假設潔淨」;en concordance 48,398,387 列未逐列字面驗,列 verify 常備項(串流化後可負擔)。新增 **hash 蓋章**(chunk↔work_text 世代指紋):work_text 再清洗即令下游指紋失配、錯得大聲——builder resume 對再清洗無感知正是 1,189 stale 的病根(寫入時未留可鑑別記號)。
- **L2.5 統計層**:term_stats ~448k 列(distinct en 436,572+zh 11,553,計數實測 10.9s)=分鐘級;列 refresh DAG **末端節點**(concordance 下游),附 build 時戳+來源 concordance 計數入帳,防 term_stats 版 stale 重演。新增**三層可解率視圖**(§二)。
- **L3 定義層**:寫入端 done(154,875 全嵌);**讀路徑列債**——`retrieval._term_forms` 只做 NFC+lower(retrieval.py:113-118),庫內 en term 鍵已 Porter 化、繁簡未做 → en exact 檢索實測全滅(命門 9 實錘)。修法=債 W2.7(自 v2.0 之「W8 硬先決」**提前至債務期**——A 骨架命門 9 本身即要求此序)。
- **L3.5 衍生層**:合規骨架(derivation_method 封閉集 DDL+charter)**先於任何衍生寫入**;school_thinker 現況 19 列/17 thinker(全來自策展 SEED),對 4,134 thinker 覆蓋僅 0.41%,harvest 晉升 4,100+ thinker 零回填——L5「七維 JOIN」之 school 維幾近空轉;處置=拍板 4(誠實揭露先行)。
- **L4 語意層**:W5 拆帳 **W5a=灌庫(done:三嵌 100%+HNSW 三索引在位)/W5b=驗收(open)**。三粒度嵌入從 write-only 補**讀端三 API**(definition-kNN/sentence-kNN/chunk-kNN;現況 retrieve() 只 JOIN philosophy_chunk_embedding〔retrieval.py:54〕)。junk 清理:19 symbol-only+98 低字母比 chunk(98 全嵌)+5 zh junk 句。**zh/en 句嵌分表拍板前置於任何 en 嵌入**(post-filter 陷阱:現況 iterative_scan=off/ef_search=40;en 進場後 zh 過濾選擇率 33,319/1,539,019≈2.2%,ef_search=40 期望 zh 候選<1、k=10 常回 0~少數列;**嵌後再分表=數 GB 重灌,順序不可逆**)。
- **L5 角色層**:answer.py 定位=**檢索編排器非第二閘/第二出口**,最終輸出一律過欽定 `advisor.guard` 單一機械閘 SSOT(自建閘違 #12、繞閘違憲章防幻覺條款);guard 數字白名單擴**雙源**=payload.numbers() ∪ 本次真兆 SQL 查詢結果集之數字(可溯源 #15,擴源規格明文、不因知識層放鬆閘檢);三級誠實補第三級(151 部 review_flag=true 有全文族群,現被唯一固定句「知識庫中無此內容」誤答為全無〔guard.py:12/:51-52 二值〕);coverage_metric 加 instance 身分(拍板 6)。**R0-R4 角色階梯為本層驗收主軸疊加層**(§九)。
- **L6 治理橫切**:CLEAN_WORK SSOT 建 `src/augur/knowledge/corpus.py`(現況:**該檔不存在**;四支 builder 三種述詞並存——`review_flag IS NOT TRUE`〔fail-open,build_sentences.py:86/build_concordance.py:47〕vs `NOT w.review_flag` vs `= false`;檢索端 retrieve()/lookup SQL 完全無 review 述詞=答時 fail-open;零實害純屬資料僥倖——57 個 NULL work 全無全文)。W1 治理**資料面 done/程式面 open 明文分欄**:四欄+蓋章(audit 794/provenance 523)已在 DB,但 reviewed_by/corpus_class 全 repo .py/.sql 零命中=一次性手工操作、clean-room 不可重現。verify_text_integrity **C 族明文涵蓋 chunk↔work_text 定位子串驗**(v2.0 §八只點 C2 句/C6 定義,正好漏掉憲章點名的那層)。游標生命週期歸 refresh 驅動器(游標遺物實錘:concordance 游標 1,543,732/1,567,854 > max(sent_id)=1,539,019,曾有尾段 28,835 個 sent_id 配發後整批刪除;sequence 若 RESTART 即靜默跳過回填列)。
- **L6 共同不變式(a)-(d)〔承憲章 v1.22.0 同名小節,v3.0 明文入計畫〕**:
  - **(a) 共享策展脊椎表(school/thinker/work/work_text)禁 DELETE-rebuild;禁以放寬 FK 為修法**——knowledge_sentence.text_id 與 knowledge_lexicon.source_work_id 之 NO ACTION FK 現為唯一防滅庫保險(誤改 CASCADE,一次 framework 重跑=靜默滅 1,374 work/31,778 全文/63,601 chunk/1.54M 句/154,875 lexicon/49.1M concordance)。
  - **(b) 契約函式三方(寫入/查詢/驗收)import 同一 SSOT+跨端回歸測例**——textnorm 之查詢端違約與 expansion §八1(契約寫進計畫≠寫進 code)為同型病;凡宣告之 SSOT/契約一律 grep 實證存在於 code,**不受理行為等價 inline 複本**。
  - **(c) 排除帳目落庫可重放,不只 stdout**——zh 句差 5=junk 排除(embed_knowledge.py 僅 print 不落庫),DB 定錨曾誤判「背景增量」;帳目機器等式見驗收 5。
  - **(d) build/promote 冪等重放為驗收硬項**——連跑兩次 exit 0 且計數不變;framework.py:265/:356 DELETE 重建現撞 NO ACTION FK 必炸(docstring 自稱冪等=失實),且該 build 排夜跑鏈中段(&& 串接),unattended 炸=報廢整段剩餘鏈。

## 二、「定義/意涵/思想」真兆載體(對映用戶目標;v3.0 新增節,本計畫核心)

用戶目標(「將內文用窮舉方式逐字逐句了解其每個字與句子的定義與意涵與思想,並匯入向量資料庫」)之系統化=**每一字/句的三層真兆,載體全封閉、全確定性、全可溯源**;終態以「漸近全知北極星」表述、以 coverage 度量。

**每一字/詞的三層:**

| 層 | 載體(合法全集) | 現況 |
|---|---|---|
| **定義** | knowledge_lexicon(公版辭書:Webster 113,425/康熙 26,730/說文 9,831/Roget 1,043)+ 注疏(王弼 405/論語注疏 1,701/孟子注疏 1,740=**人寫的**意涵解釋,非 AI) | 154,875 已入庫全嵌 |
| **意涵** | 「意涵=用法之總和」確定性版:concordance 出現處(49.1M,「道」5,026 處)+ term_stats(頻次/散佈/keyness,閉式公式)+ 共現 PMI(按需 SQL)+ 經-注-疏對齊 + 跨語平行對齊 + 詞義歷時(按 work 年代切片計數)+ textnorm 詞形/繁簡對映(確定性映射,釘版本) | concordance done;term_stats/對齊=W6/W7 |
| **思想** | 引文網(n-gram 重合=誰引誰,純字串)+ knowledge_edge 圖譜(term↔thinker↔school↔taxonomy;predicate 封閉集;provenance ∈ join/string_rule/counting)+ school_thinker(限策展/string_rule/人審)+ 真實文獻 citation | W7;school 維 0.41% 待拍板 4 |

**每一句的三層**:定義=逐字原文+locator(sentence 本體,已全量 0 stale);意涵=所在 chunk/章節語境+跨語對齊句;思想=引文網節點歸屬+work→thinker→school 鏈。

**鐵律(機器強制)**:derivation_method.method_kind 封閉集 ∈ {counting, closed_form_stat, string_rule, sql_join}——**LLM/embedding 相似度不在合法 kind 集=DB 硬擋**;AI 生成之釋義/評註/摘要零入庫;AI 唯一詮釋時點=回答時刻,詮釋不落庫(命門 1/4/5);嵌入=索引非內容,命中後 guard 逐字引原文且過定位驗證(命門 7/8)。

**窮盡度量化(v3.0 新增,「窮舉了解每個字」的可量測形)**:per-term 三層可解率——分母=distinct term 448,125(en 436,572+zh 11,553,實測 10.9s);分子分列:有定義(lexicon 命中)/有出現處(concordance 命中)/有思想鏈(edge 可達)。入 coverage 四指標,append-only。

**誠實邊界(charter 明文)**:本系統之「意涵/思想」=真兆載體之組織呈現,非語意理解本身;philosophy+item 語料 ≠ 人類全部知識(工藝/隱性 know-how 無 API 可窮舉,承 expansion 計畫誠實邊界)。

## 三、schema 增補(v2.0 §二 (a)-(f) 維持;v3.0 增補全部併入 T0 `migrate_text_understanding_ddl.py` 同一冪等住所,#12)

```sql
-- (g) W1 程式面補課:四欄 ALTER(review_reason/reviewed_by/reviewed_at/corpus_class)補入 T0 DDL
--     現況:四欄已在 DB 而 migrate DDL 零涵蓋(僅 review_flag @line93)=clean-room 不可重現,必須補回程式事實

-- (h) chunk 世代指紋(hash 蓋章,斷絕 stale 再生;0-based 定位慣例經 probe 確立)
ALTER TABLE philosophy_chunk ADD COLUMN IF NOT EXISTS src_text_sha1 char(40);
--   builder 寫入時蓋 work_text 內容 hash;verify C-chunk 以「hash 相符 + content=substring(t.content FROM char_start+1 FOR char_end-char_start)」雙驗
--   work_text 任何再清洗即全 chunk 指紋失配、錯得大聲(寫入時留可鑑別記號)

-- (i) 句嵌分表(拍板 1 採分表案時;en 進場前執行,順序不可逆)
--   knowledge_sentence_embedding 依 language 分 zh/en 兩表(HNSW 各自建);同表混語=post-filter 陷阱(§五 EXPLAIN 實錘)
--   若拍板 2 採 C 子集案:en 嵌入表加 subset_tag 標記欄,防 coverage 分母混淆

-- (j) coverage instance 身分(拍板 6 先決;先於首期 append,append-only 失真會被鑄死)
ALTER TABLE knowledge_coverage_metric ADD COLUMN IF NOT EXISTS instance varchar(32);

-- (k) build_meta 游標世代(重建時寫入依據)
ALTER TABLE knowledge_build_meta
  ADD COLUMN IF NOT EXISTS generation int, ADD COLUMN IF NOT EXISTS note text;

-- (l) corpus_class DEFAULT 修法(拍板 13):(a) 去 DEFAULT、寫入端必顯式給值(錯得大聲)
--     或 (b) 保留 DEFAULT + verify 稽核項「reference 來源之 work 若 corpus_class='literary' 即違規」
```

## 四、程式增補(全 #29:矩陣/冪等/resume/graceful;v2.0 §三表維持,以下為 v3.0 差分)

| 支 | v3.0 職責 | 對應 W |
|---|---|---|
| `src/augur/knowledge/corpus.py`(新) | CLEAN_WORK(`w.review_flag = false`,fail-closed、NULL 不放行)+ `corpus_class='literary'` 述詞**單一住所**;builder(建時)/embed(嵌時)/retrieval+answer(答時 JOIN=fail-closed 雙保險)三端強制 import | W1 |
| `migrate_text_understanding_ddl.py`(擴) | §三 (g)-(l) 全數併入;ALTER 一律 IF NOT EXISTS 可安全重放 | W1 |
| `audit_work_attribution.py`(擴) | `--incremental`(只稽核 NULL)+蓋 reviewed_by/reviewed_at/review_reason——蓋章邏輯從手工遺產落回 code | W1 |
| `review_flagged_works.py`(新) | 151 部 flag 人審 CLI(--list 佇列+證據/--accept/--reject);人審=決策層,AI 只呈證據;三級誠實第三級族群的唯一出口 | W1 |
| `verify_text_integrity.py`(新) | C 族含 **C-chunk 定位子串(0-based)+hash 失配**、C2 句、C6 定義、cursor≤sequence last_value、零 orphan(concordance/embedding)、reference 洩漏(chunk=0 且句=0)、禁字掃 schema/表欄名/註解;**串流化**(一次投資換掉永久十分鐘級全掃);exit 1 擋管線 | W2 |
| 兩支 builder(改) | build_philosophy_chunks.py/build_sentences.py:閘改 corpus.py 述詞(廢 work_type 白名單);hash 蓋章寫入;**移除 --force TRUNCATE 壞槓桿**(chunk_embedding FK 建立後已壞死@line100),改 scoped rebuild primitive | W2.5 |
| `retrieval._term_forms` 重寫(改) | import textnorm 產**查詢全形集**={NFC 原形, lower, Porter/norm_headword 形, zh jieba 詞形, 繁簡雙形(釘版本之確定性映射)};SQL 改 IN(全形集);term_display 加正規化第二鍵+索引(避免 ILIKE 全掃) | W2.7 |
| chunk scoped 修復(新,可併入 refresh) | 41 text_id 之 1,863 chunk DELETE(CASCADE 清嵌入)→重切→重嵌;同批清 junk 98+19+5;chunk 重嵌路徑補 junk 閘(與 sentence 層**同一 is_junk SSOT**,勿兩處各寫) | W3 |
| `verify_verbatim` 升級+guard 閘鏈(改) | 定位精確驗證(substring FROM char_start+1)併入 guard;引文雙基準(命門 8)。二擇一:(i) 閘鏈升級〔建議,改動小〕/(ii) 根治=retrieve() 以 work_text 定位 substring 為 text 權威來源、chunk.content 降級純索引欄〔W8 檢索層重構時評估〕 | W3 |
| `framework.py`(改) | 廢 :265/:356 DELETE-rebuild,改 upsert-by-natural-key(ON CONFLICT;name/title+thinker UNIQUE 已在)或 scoped delete(僅刪 SEED 內列);明文「不得以放寬 FK 為修法」 | W4 |
| 跨語驗收 harness(新) | rank@10 固定測例(en→zh/zh→en × 單字/短語/長句三型);每次執行 append-only 落 coverage_metric+快照 model_tag/ef_search/iterative_scan GUC;「清理前/後」兩組真值證明修復可歸因 | W5b |
| `build_term_stats`(新) | ~448k 列物化;DAG 末端;build 時戳+來源 concordance 計數入帳 | W6 |
| `answer.py`(新) | 四段:問題→規則檢索計畫(exact〔textnorm 全形集〕優先→semantic〔粒度細優先〕補→graph〔W7 後〕)→多層真兆 JOIN→引用作答;**輸出 100% 過 guard 單閘**;三級誠實分級器=檢索空時加「隔離館藏旁查」(review_flag IS DISTINCT FROM false AND EXISTS 全文,外加 staging pending)分流第三級 | W8 |
| `profile.py`(新) | 自我知識視圖(harvest_log/build_meta/coverage 可查詢化);**每次輸出自報「本視圖=哪台機、哪個時點」**(繫拍板 6) | W8 |
| `report_knowledge_coverage.py`(新) | 四指標+三層可解率;誠實率=固定測例重放且**雙向**;固定測例住版本化 SSOT(fixtures 檔或 DB 小表),新增/修改=用戶過目 | W8 |
| `refresh_text_understanding.py`(新) | 顯式依賴 DAG:work_text→sentence→concordance→term_stats(末端);work_text→chunk→chunk_emb;sentence→sent_emb;lexicon→lex_emb。**擁有游標生命週期**:scoped 刪除/重建與對應游標重置同 transaction;游標 resume 僅限 append-only 上游,回填/重建走 scoped 全重算 | 常設 |
| `embed_knowledge.py`(改) | is_junk 單一 SSOT(zh 全符號規則+en 規則:純符號/純縮寫+句點/長度閾);**排除帳落庫非 stdout**;分表路由;`--limit 1000` 首千列實測重投影 | W5b/W9 |

## 五、實測定錨(本節=全計畫數字之唯一出處錨;正文數字未另註者皆出自本表。全部 2026-07-03/04 本機唯讀實查,#15)

| 項 | 實測值 | 出處 |
|---|---|---|
| 語料主計數 | work 1,374/work_text 31,778/句 1,539,019(en 1,505,700+zh 33,319)/concordance 49,106,830(en 48,398,387/zh 708,443)/chunk 63,601/lexicon 154,875 | psql count(*)/GROUP BY(2026-07-04 06:16-06:20 snapshot) |
| 三嵌覆蓋 | lexicon 154,875/154,875;zh 句 33,314/33,319;chunk 63,601/63,601;**en 句 0/1,505,700(游標 embed_sentence_en=0)**;HNSW 三索引在位 | psql LEFT JOIN embedding/GROUP BY model_tag/pg_indexes;knowledge_build_meta |
| zh 句差 5 | =_SYMBOL_ONLY junk skip(「。」×3/「……」/「□□□□……」;sent_id 2228/2401/2773/3533/1460881 全<游標 1,514,500,重跑不撿)——**更正:非背景增量** | psql sent_id 實查+embed_knowledge.py:117-133(skip 僅 print) |
| stale chunk | **1,189/63,601(1.87%)**;三分解=1,132 內容漂移至別處(locator 說謊)+**57 全文已無(真逐字鏈斷裂)**;42 筆越界(char_end>length);載體 **41 text_id/21 work**;41 text_id 全 chunk=1,863;**1,189/1,189 已有 embedding**;與 review_flag NULL 之 57 works 僅巧合同數,禁混述 | psql 全量 0-based substring 比對+position() 分組+JOIN chunk_embedding |
| 下游潔淨 | 句 stale=0/1,539,019(real 6m15s);41 stale text_id 上 21,409 句 0 stale;zh concordance 字面驗 0 錯 0 orphan → **污染僅限 chunk 層,絕不需重灌 48.4M en concordance** | psql 全量驗 |
| junk 在索引 | chunk:19 symbol-only+98 低字母比(<0.3),98 全嵌 | psql regex+JOIN embedding |
| textnorm 失守 | 'knowledge'=0(庫存 'knowledg':lexicon 3/concordance 26,869)/'philosophy'=0('philosophi' 18,310)/'学'=0('學' 2)/'happiness' 大小寫 miss | psql 實測;retrieval.py:113-118;textnorm.py:7,168-187 |
| framework FK | sentence.text_id/lexicon.source_work_id=NO ACTION('a');work/work_text/chunk/三嵌=CASCADE('c');school_thinker 19 列/17 thinker vs thinker 4,134(0.41%) | pg_constraint confdeltype;psql |
| 治理現況 | review_flag false 1,166/true 151(全有全文族群=第三級)/NULL 57(全無全文);reviewed_by audit 794/provenance 523/NULL 57;corpus_class literary 1,367/reference 7(Webster 27,936,778 字/康熙 2,248,945 字);**reviewed_by/corpus_class 全 repo code 零命中** | psql;grep -rln --include='*.py' --include='*.sql' |
| 游標遺物 | concordance_en=1,543,732/zh=1,567,854 > max(sent_id)=1,539,019=count(*)(無空洞);sequence last_value=1,567,854;尾段 28,835 個 id 曾配發後整批刪除 | psql build_meta/sequence/max |
| 嵌入吞吐(本機) | lexicon 46.7 筆/s(154,875/3,315s;舊機 10.2 → 4.6 倍,成立)/zh 句 128/s(33,314/260s;舊機 77.1 → **僅 1.66 倍,非 5 倍**) | build_meta updated_at 推算 |
| en 成本折算 | en 句均長 187.1 字(281,662,193/1,505,700)vs zh 24.2(7.7 倍)→ 折算 en 專屬吞吐 ≈66-91 句/s → 扣 junk 後 1,452,924 句 ≈**4.4-6.1h**(HNSW build 另計未測);儲存 3,669B/row 實測外推 ≈**5.3GB**。**「~3.1h」=zh 吞吐天真外插,不得入正文** | psql avg length/per-row 實測;折算=閉式換算 |
| RAM 真約束 | en HNSW 圖 ≈2.9-3.0GB(1.97KB/向量〔idx_sent 64MB/33,314〕與 1.98KB/向量〔idx_lex 300MB/154,875〕交叉相符)> v2.0 死數 2GB;伺服器現值 maintenance_work_mem=**64MB**/shared_buffers=128MB;DB 43GB/機 15GB RAM/12 核;磁碟餘 873GB=**非約束**;PG 17.9+pgvector 0.8.4 | psql pg_relation_size/SHOW/pg_database_size;df/free/nproc |
| post-filter | iterative_scan=off/ef_search=40(全 repo 零 SET);EXPLAIN:句表 language 過濾走 HNSW 後 Filter(en 進場後 zh 選擇率 2.2% 即爆);chunk 表 work_id 過濾 planner 走 btree+精確排序(無陷阱)——主戰場在句級大表 | SHOW/EXPLAIN/grep |
| en 去重崩塌 | distinct 1,132,616(重複 373,084=24.8%),主體=碎片('Cleo.' 1,632/'Hor.' 1,604/'Mr.' 1,244/'CHAP.' 861) | psql GROUP BY |
| 統計層規模 | distinct term en 436,572+zh 11,553≈448k(real 10.9s) | psql |
| 兩機分歧 | 本機 item 25,031 vs 舊機 41,888(差 16,857);staging pending 背景鏈活躍(+500/190s≈2.6 筆/s) | psql 兩時點;舊機既定錨 |
| 零 LLM 實證 | 全 build 鏈(harvest/promote/builder/embed)grep 零 LLM 呼叫;嵌入=本地 CPU SentenceTransformer——**#28 本地零 usage 已 100% 達成**,answer.py 為唯一 LLM 觸點且僅在回答時刻(與命門 1 互為表裡,入計畫不變式) | grep -rlE 'anthropic\|openai\|claude\|gpt-' scripts/ src/augur/=0 |
| lineage 現值 | chunk 可溯源率 62,412/63,601≈**98.13%**(誠實入帳,不等修完才記) | psql(63,601−1,189) |
| guard/verbatim 路徑 | advise.py 僅呼叫 guard();guard.py:23 引文閘基準=chunk 副本;verify_verbatim 唯一呼叫者=query_philosophy.py:18;guard.py:12 固定句二值;guard.py:31 數字白名單=payload.numbers();guard.py:14-17 措辭 regex hardcode | grep/code 複驗 |
| 承諾程式缺席 | verify_text_integrity.py/answer.py/profile.py/refresh_text_understanding.py/review_flagged_works.py/corpus.py 皆不存在;audit 無 --incremental;rank@10 harness 零執行體;coverage_metric 表不存在 | ls/grep 複驗 |

## 六、全向量化路線(en 句嵌入;拍板 1→2 重議,實測定錨 §五)

用戶 directive=全向量化;架構師合成立場:**逐字窮盡在載體層已 100%**(en 句+concordance 全落庫、可 exact 檢索),嵌入屬索引——**A′(全量)為終態方向**(索引覆蓋亦應窮盡),但**序位讓給逐字鏈完整性**(排序公理),且裁決以 L5 真值非估算(「能嵌≠該嵌」)。

**路線(順序不可逆)**:

1. **R1 分表拍板**(拍板 1,先於任何 en 嵌入):zh/en 句嵌入分表〔建議〕——嵌後再分=數 GB 重灌;同表混語正是 v2.0「分表防 post-filter」決策要防的同型病。
2. **R2 en junk 寫入側規則**:純符號/純縮寫+句點/長度閾值,排除計數逐類誠實落庫;**刪 v2.0 選項 B(去重)**——en 重複僅 24.8% 且主體為碎片,省 ~1h+1.5GB 卻背 canonical 映射查詢端複雜度,價值崩塌;同批垃圾用規則過濾幾乎零成本,兼解 ANN 碎片污染(zh 單字 0.84 junk 之 en 對偶)。
3. **R3 首千列實測**:`--layer sentence --language en --limit 1000`(<10 分鐘、零風險、cursor 可續),以實測吞吐重投影**四件套封包**{embed 時數, heap GB, HNSW GB, index build 分鐘}連同 ≈5.3GB 呈拍。
4. **R4 拍板範圍**(拍板 2):A′=全量+junk 規則 vs C=子集(高頻 term 命中句/投資域 work;圈選 SQL **必用 textnorm 正規形 term**,否則 stem 不匹配系統性漏圈;拍 C 則嵌入表加 subset_tag 防 coverage 分母混淆)。**裁決軸=L5 實需非算力**:W8 上線後以固定測例實測「無 en 句嵌 vs 有」答案品質差,用真值拍。
5. **R5 放量**:session 級 `SET maintenance_work_mem` 以「實測 KB/列 × 列數」算式計算並印出(**4GB 起,不沿用 2GB 死數**;en 圖實測外推 ≈2.9-3.0GB)+`max_parallel_maintenance_workers` 吃滿 12 核;「灌完才建」維持;retrieval 層寫死 relaxed_order/ef_search GUC 並入 coverage 記錄。
6. **R6 W5b 驗收擴 en**:rank@10 有/無 en 嵌兩組真值(=R4 級驗收)。

**資源節據實改寫**:磁碟(餘 873GB)與算力=**非約束**;真硬約束=**HNSW build RAM 峰值+重複全掃時間**;全 build 鏈零 LLM(§五實證)=「#28 本地零 usage」明文入計畫不變式。shared_buffers 128MB→2-4GB 列 ops 工單(拍板 10,#27 逐級)。

## 七、拍板點清單(全數決策層;每點附建議+成本)

> **拍板紀錄(用戶「照建議」2026-07-04)**:採各點建議值,例外標註如下——
> - **已鎖定採建議(1/4先降級/5不落庫/6本機權威/7維持ref/8維持chapter-quote/9 DB載入/10逐級/11閘外/13去DEFAULT)**:baked into W1-W9 建置,建置時落地。
> - **拍板2(en範圍)**:兩段式=C過渡、A′終態;**GPU 現被 D4 之 87k chunk 嵌入佔用(~3.7h)**+待 L5 證實需求,en 全量排該之後、R3 首千列封包呈用戶再定。**未執行。**
> - **拍板3(誠實句閉集擴充)**:=憲章防幻覺條款判準變更→**保留待用戶單獨確認後才動憲章**(AI 未逕改治權檔)。
> - **拍板12(item_text 鏈)**:列 v3.x 後續(W10+)、獨立計畫;本版 coverage 誠實標邊界。
> - **阻塞(非決策問題)**:拍板6之兩機 merge=需舊機 dump(本機無、待跨機遷移);拍板10之 postgresql.conf 調參=需 sudo(用戶執行)。


**前言通則〔承 C 骨架〕:「誠實揭露先行、能力補課後行」**——凡能力缺口(school 維/隔離館藏/固定句分級),一律先以 charter/coverage 誠實揭露現況,再排能力補課;角色的可信度優先於角色的能力面積。統攝拍板 3/4/5。

1. **zh/en 句嵌分表 vs relaxed_order vs partial index**。建議:**分表**(根治 post-filter,與 v2.0 分表決策一致)。成本:DDL+embed 路由改動小時級;**不先拍即嵌=數 GB 重灌不可逆**。順序:先於拍板 2 與 W9。
2. **en 句嵌入範圍 A′/C**(選項 B 已刪)。建議:兩段式——R3 首千列封包呈拍後定;傾向 A′ 為終態方向、C 為 L5 實需未證時的過渡。成本:A′≈4.4-6.1h embed+HNSW build 另計+heap ≈5.3GB+RAM 前置 4GB 起;C=圈選 SQL+subset_tag,規模依子集。
3. **三級誠實固定句閉集擴充**(第三級第二固定句,如「庫中存有此著作但歸屬未驗,不予引用」)。**=憲章防幻覺條款判準變更(v1.22 line 134),不得執行層自改**。建議:擴為固定句閉集+隔離館藏旁查分級器。成本:guard+answer 分級器小時級+憲章升版一次。
4. **school_thinker:誠實降級 vs 回填工具**。建議:**先降級**(charter 明文 school 歸派僅覆蓋策展 17 人+coverage 揭露 0.41%,分鐘級),回填工具列後續能力補課(獨立冪等工,合法來源限 string_rule/citation 證據或人審 CLI,**禁 AI/embedding 歸派**;日級)。二擇一必明文,不得留空。
5. **AI 記憶隔離**:(a) **不落庫**〔建議:零修憲、與「顧問唯讀零寫回」零衝突;寫成 charter 可查宣稱,成本一列〕vs (b) 落庫=先修憲+三件套機器強制(獨立 schema+恆真 CHECK+GRANT 層物理擋 public 寫權;日級)。順序:先於 answer.py 任何持久化;禁先建籠後補憲。
6. **兩機權威+coverage instance**:單一權威 DB(建議=本機)+coverage_metric 加 instance 欄雙保險;固定測例給版本化 SSOT 住所(新增/修改=用戶過目)。成本:merge 分鐘級零 API+ALTER 一次。順序:**先於 coverage 首期 append**(append-only 失真會被鑄死)。
7. **註疏 corpus_class**:建議維持 reference(只走 lexicon);要語意檢索則 W2.5 閘落地後單欄 UPDATE 改 literary(可逆,成本一句 SQL)。
8. **句級對齊 grain**:建議維持 chapter/quote 封閉集;開放句級=判準變更另拍。成本:零(不動)。
9. **charter forbidden_pat 住所**:(A) guard 啟動載入 charter=資料驅動閘(DB=SSOT,改閘=改列=用戶過目)〔建議,消 regex 雙住所漂移〕vs (B) regex SSOT 留 guard.py、charter 列引用常數名。成本:(A) 小時級。
10. **ops 調參**:shared_buffers 128MB→2-4GB+maintenance_work_mem 常態值(#27 可控逐級,受益一切重複掃描:concordance build/全量 verify/term_stats)。成本:conf+重啟分鐘級。
11. **後續窮盡邊界啟用**:未拍板 16 field 詞(~3,000 詞)。建議:維持閘外,俟 L5 首版驗證後按域拍。成本:決策層 INSERT 零 code。
12. **item_text 理解鏈起步**(現=0,sentence/concordance/chunk 全建於 philosophy 側):建議列 v3.x 後續 W(W10+),本版先以 coverage 誠實標示邊界。成本:harvest/promote 全文擴展=獨立計畫。
13. **corpus_class DEFAULT 修法**:(a) 去 DEFAULT、寫入端必顯式給值(錯得大聲)〔建議〕vs (b) 保留 DEFAULT+verify 稽核項「reference 來源而 literary=違規」(無論何案,verify 稽核項都建)。成本:ALTER+promote 寫入端補值,小時級。

## 八、執行序(v3.0 重排:Phase 0 還債前置;W2 verify 先於 W3 修復以取同工具前/後基線;兩線平行)

**現況雙欄狀態表(命門 10 落地格式;「done」僅指灌庫)**:

| 項 | 灌庫(物化) | 驗收 |
|---|---|---|
| lexicon 寫入+嵌入 | done(154,875 全嵌) | **open**(查詢端契約測例=W2.7 後) |
| zh 句嵌入 | done(33,314;5=junk 排除) | **open**(W5b;排除帳未落庫) |
| chunk 嵌入 | done(63,601+HNSW) | **open**(stale 1,189 未修;junk 117 在索引;W5b) |
| en 句斷句落地 | done(1,505,700) | open(嵌入 0=拍板 2 後) |
| concordance | done(49.1M) | zh 字面驗過;en 未逐列字面驗=verify 常備項 |
| W1 治理 | 資料面 done(四欄+蓋章 1,317 部) | **程式面 open**(code 零存在=不可重現) |

**Phase 0 還債(D 系列;全部分鐘-小時級;順序內硬依賴)**

- **W0〔新〕兩機 merge(D7)**:舊機 dump knowledge_item(+staging promoted+harvest_log)→本機 external_id ON CONFLICT 冪等灌入;指定單一寫入機(拍板 6)。分鐘級零 API,**先於任一機下輪放量與 coverage 首期**。
- **W1 治理程式化(D1a)**:§三 (g) 四欄 ALTER 入 T0;蓋章落 `audit --incremental`;**corpus.py CLEAN_WORK+literary 述詞單一住所、三端強制 import**;人審 CLI(151 部佇列出口)。**W1 未落地前禁止重跑任何 builder**;工單 B 之 NULL work 不得先掛全文。
- **W2 verify_text_integrity 上線(D3)**:C 族全集(含 C-chunk 定位子串+hash)+游標不變式+零 orphan+reference 洩漏+禁字掃;串流化;exit 1。**以同一常備工具打修復前基線(stale=1,189),供 W3 後對照=0 之證據鏈**(此即 verify 先於修復之理由)。
- **W2.5 corpus_class 閘落兩支 builder(D1b)**:**硬性先於 W3**——否則修復重跑 builder 即灌 Webster 27,936,778 字入語意層、重演 junk 0.84 污染;閘鍵一律 corpus_class 單欄(work_type 白名單實證漏接 book/philosophy_classic)。
- **W2.7 textnorm 查詢端履約(D4;自 v2.0 W8 先決提前至債務期)**:_term_forms 全形集重寫+查詢端契約測例;**R0 阻斷級**——修「對已有知識說謊」為全計畫價值/成本比最高之單項。
- **W3 chunk 層 scoped 修復(D2+D6)**:41 text_id 之 1,863 chunk DELETE(CASCADE 清嵌入)→重切(帶 hash 蓋章+junk 閘)→重嵌;同批清 junk 98+19+5;verify_verbatim 定位版併入 guard 閘鏈(命門 8;根治備選見 §四)。**分鐘級;絕不編列全鏈重建、絕不動 48.4M en concordance**(§五實證不需)。
- **W4 framework 冪等修(D5)**:upsert-by-natural-key/scoped delete;禁 DELETE-rebuild+禁放寬 FK(共同不變式 a);移除 --force TRUNCATE;夜跑鏈中段炸點解除。獨立小工單,可即插。

**Phase 1 塔身(兩線平行;輸入層已全量驗潔淨,互不阻塞)**

- **線 A(逐字鏈)**:**W5b 跨語驗收 harness**(rank@10 固定測例+GUC 快照;「清理前/後」兩組真值;instance 拍板 6 先決)。
- **線 B(統計/衍生)**:**W6 term_stats+三層可解率**(分鐘級;DAG 末端)→ **W7 L3.5**(derivation_method+charter 合規骨架先行→對齊/引文網/edge;school 維按拍板 4 先降級揭露)。

**Phase 2:W8 answer.py+profile.py+coverage 首期**——三級誠實分級器(隔離館藏旁查+第二固定句〔拍板 3 後〕);三粒度讀端 API+合成路徑 exact→semantic→graph,每支出口過定位 verbatim;guard 單閘 SSOT+數字雙源;profile 自報機器/時點;coverage 首期四指標 append(lineage 率以 98.13% 現值誠實入帳)。

**Phase 3:W9 en 句嵌入(最後)**:§六 R1-R6;全計畫**價值最未證、成本最集中**的一步——理由=「**R0-R3 全不依賴 en 句嵌**」(zh 句+lexicon+chunk 三嵌 100% 在位、en concordance 全量 exact 可查),此為 W9 排最後之裁決依據。

**常設**:refresh_text_understanding.py 顯式 DAG+游標生命週期+verify 常備。

**順序硬約束總表**(執行 checklist):

| # | 約束 | 違反後果(實錘) |
|---|---|---|
| 1 | W1 閘門 SSOT → 任何 builder 重跑 | 述詞三寫並存、答時 fail-open |
| 2 | W2 verify 基線 → W3 修復 → W5b 驗收 → 任何檢索演示 | 修復不可歸因;stale 穿閘被引為逐字原文 |
| 3 | W2.5 corpus_class 閘 → W3 | Webster 27.9M 字入語意層 |
| 4 | W2.7 textnorm → W8;R0 測例先於誠實率首期入庫 | 假不知道鑄入 append-only 指標 |
| 5 | 拍板 1(分表)→ 拍板 2(範圍)→ W9 | 嵌後分表=數 GB 重灌不可逆 |
| 6 | 拍板 5(AI 產出住所)→ answer.py 任何持久化 | 未經憲章授權寫路徑 |
| 7 | W0+拍板 6(instance)→ coverage 首期 append | append-only 雙腦失真被鑄死 |
| 8 | W1 → 工單 B(NULL work 掛全文) | fail-open 述詞放行未審全文 |
| 9 | W6 term_stats=refresh DAG 末端(concordance 下游) | term_stats 版 stale 重演 |
| 10 | RAM 前置(4GB 算式)+「灌完才建」→ W9 放量 | 磁碟建圖劣化數量級+未編列長尾 |

## 九、「誠實博學的我」(L5;含 R0-R4 角色能力階梯=驗收主軸疊加層)

- **能力形**:任一字/句 → 出現處(concordance 49.1M)× 定義(lexicon 154,875)× 解經(註疏)× 語意近鄰(三粒度向量)× 統計(term_stats/PMI)× 對齊 × 知識圖譜(term↔thinker↔school↔taxonomy)七維 JOIN,逐字引用+locator+**定位驗證**(命門 8);semantic 支路必經三粒度讀端(終結 write-only)。
- **誠實形**:三級誠實(全無/部分有/**有但未驗**〔151 部隔離館藏+staging pending〕)機器分級;coverage 四指標+三層可解率 append-only 時序(instance 身分先決);charter 表明文「我能答什麼/不能答什麼」+「意涵/思想=真兆載體之組織呈現」+「AI 產出不落庫」宣稱;誠實率=固定測例重放且**雙向**。
- **記憶形**:知識庫=長期記憶;harvest_log/build_meta=學習履歷(profile 可查詢化、自報機器/時點);AI 對話產出依拍板 5(建議不落庫)。

**R0-R4 角色能力階梯(每級=可對話+可機器驗收;通過才升級)**:

| 級 | 角色能力(可對話形) | 對應 W | 驗收形 |
|---|---|---|---|
| R0 | 能誠實說不知道(**且不假不知道**) | W1+W2.7 | 查詢端契約測例雙向('knowledge'/'markets'/'学' 固定測例)各觸發 |
| R1 | 能逐字引經據典(引文=現行原文**他證**) | W2.5+W3(命門 8) | 引文雙基準測例;C-chunk 定位子串全量 0 違反 |
| R2 | 能講字與句的意涵(統計真兆) | W6+三粒度讀端 | 定義×出現×統計×語意近鄰四維一問通 |
| R3 | 能講思想(圖譜/引文網/對齊) | W7 | edge/引文網測例+charter school 0.41% 揭露列;三級誠實含隔離館藏 |
| R4 | 雙語全量博學 | W9(拍板 1/2 後) | rank@10「有/無 en 嵌」兩組真值 |

## 十、驗收判準(v2.0 五條→十二條;全部機器可重放;計畫自述不作數——expansion 三輪修訂之失實史教訓:每次對抗審查都翻出「已完成」不實)

1. **逐字鏈全量 0**:chunk↔work_text 定位子串(0-based)+hash 全量 0 違反;sentence/concordance 維持 0;verify `--full` exit 1 擋管線;修復前基線 1,189→修復後 0 同工具可對照。
2. **guard 雙基準測例**:對已知 stale 樣本,引文閘必擋(∈ citation 且 ∈ 現行原文定位)——消「guard 過、稽核不過」兩套判準。
3. **查詢端契約測例**:每 lex_type×language 抽 N 詞條以「用戶表面形」查詢必命中;誠實率雙向(編造+假不知道)各有測例。
4. **冪等重放**:framework/promote/全 builder 連跑兩次 exit 0 且計數不變(測試庫實跑或交易內重放 ROLLBACK);驗收 subprocess 一律 `check=True`(expansion P4 check=False=假驗收之教訓)。
5. **排除帳機器等式**:嵌入數+verifier 重算之 is_junk 排除數=來源數(verify/coverage/embed import 同一 is_junk SSOT;zh 差 5 句=junk 排除,文本已更正)。
6. **clean-room 可重現**:凡計畫宣告之 SSOT/契約 grep 實證存在於 code(不受理行為等價 inline 複本);W1 四欄+蓋章可由 script 重跑再現;NULL-with-fulltext=0 常備不變式。
7. **隔離測例**:人工 flag 之測試 work,retrieve()/lexicon_lookup() 必不回其內容(答時 fail-closed 實證);reference 語料 chunk=0 且句=0 **由閘保證非僥倖**。
8. **三級誠實**:三級各觸發一例;151 部族群配第二固定句測例(拍板 3 後之閉集)。
9. **coverage 首期**:lineage 可溯源率以 62,412/63,601≈98.13% 現值誠實入帳(不等修完);三層可解率入四指標;固定測例住版本化 SSOT,變更=用戶過目;每筆 append 帶 instance+GUC/model_tag 快照可重放。
10. **禁字常備掃描**:命門 2 禁字於 schema/表欄名/code/DB 註解=0(現況合規,升 verify 機器證明)。
11. **數字口徑+治權同步**:v3.0 正文一律 1,189/1,132/57(chunk 三分解)+41 text_id/21 work;「57 work」混述禁用(57=review_flag NULL 未審 work 數,巧合同數);治權欄=憲章 v1.22.0。
12. **R 級驗收**:R0-R3 各級固定測例通過才升級;R4=en 嵌後 rank@10 兩組真值;七維 JOIN 一問通(school 維附 0.41% 揭露);answer 出口=guard 單一閘(grep/AST 稽核)。

## 十一、修訂歷程

v1.0→v1.3(三輪 solo:7→5→8 缺口)→ v1.4(五鏡 confirmed 11 項)→ v1.5(憲章 v1.20.0 CC 雙軌)→ v1.6(雙重驗證 7 縫:T-1 稽核閘)→ v2.0(重生:五鏡 27 案+向量專鏡+執行實測定錨;新增 L2.5/L3.5/L6、三粒度嵌入、治理常備化、誠實化條款群)→ **v3.0(還債收斂:六鏡對抗審查 15 案全數確認〔9 high/6 medium〕+ 用戶全向量化與逐字意涵思想窮盡 directive + 今晨稽核債納入——stale chunk 1,189/textnorm 查詢端違約/framework 非冪等/corpus_class 閘缺席/W1 code 零存在/W5 拆帳/post-filter/RAM 真約束/游標遺物/兩機分歧;新增命門 8/9/10、真兆載體節+三層可解率、Phase 0 債務前置鏈、共同不變式 (a)-(d)〔承憲章 v1.22.0〕、R0-R4 角色階梯、順序硬約束總表;en 嵌入選項刪 B、改兩段式實測拍板;治權欄同步憲章 v1.22.0。合成=A 骨架(逐字理解優先)× B 執行安全鏈 × C 角色里程碑)**。

**檔案錨**:本檔=reports/augur_knowledge_text_understanding_plan_20260704.md(v2.0 基底=同名 _20260702.md);src/augur/philosophy/framework.py(W4);src/augur/knowledge/textnorm.py+retrieval.py(W2.7);src/augur/advisor/guard.py(命門 8/拍板 9);scripts/build_philosophy_chunks.py+build_sentences.py(W2.5);scripts/embed_knowledge.py(W3/W9);src/augur/knowledge/corpus.py+scripts/verify_text_integrity.py+refresh_text_understanding.py+answer.py 等=待建(§四)。