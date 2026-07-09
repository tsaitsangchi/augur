# 博學全能顧問「全能全知的我」端到端計畫(治權相容、對抗審查 + 主作者親查驗證)

**日期**:2026-07-09 ｜ **性質**:plan-first(#20,拍板後才實作/入憲)｜ **方法**:ultracode 10-agent workflow(ground→design×3 視角→adversarial×3→synthesis)+ 主作者親查 code/DB 驗證承重聲稱(#15,非採信 agent 自述)
**性質判定**:主體=**執行層補鏈/接線/補閘**;**無須靈魂/憲章判準變更**(逐條論證於 §7);對抗審查三判皆 **NEEDS-FIX(非 VIOLATES-SOUL)**,修正已納入。

---

## 0. 三十秒 + 主作者親查驗證

**一句話**:目標所述鏈「外部 know-how 窮舉 → 本地 DB raw → raw 逐字逐句交互對應理解(定義/意涵/思想相關性/相關係數)→ Qdrant → qwen → web UI 對話 = 全能全知顧問」——**10 個 stage 全部已 BUILT、大半已 populated**,尤其被視為最難的「思想相關性/相關係數」層**已完整落地**。本計畫**不是從零蓋管線**,而是把散裝鏈**焊成一條可串接的 local-python-background pipeline + 每個新接縫補一道機械閘**,使違反治權在架構上不可能。

**主作者親查(2026-07-09、venv python 直查,#15 不轉述 agent)——3 承重聲稱全證實**:
- ✅ **思想相關係數=真統計非 AI**:`knowledge_derivation_method` CHECK `method_kind IN (counting/closed_form_stat/string_rule/sql_join)`(結構排除 embedding/llm);`knowledge_term_affinity` **2,957,154 列、0 NULL method_key**(FK 行行綁死)。
- ✅ **know-how 隔離於預測**:`python -m augur.audit.import_isolation` exit 0「隔離不變式通過」+ `test_philosophy_isolation` 7 passed。
- ✅ **G3 命門真實**:`ollama.base_url()`=env 覆寫**零 host 驗證**→ 可被指向外部、含 owned_local 私有 citations 之 prompt 外洩、違 v1.37.0(此為計畫唯一「真新閘」缺口)。

---

## 1. 治權張力調解(誠實維持什麼)—— 全程無判準變更

| # | 張力 | 調解 | 誠實維持點 |
|---|------|------|-----------|
| **T1** know-how 餵系統 vs #8 隔離 | know-how 只進 advisor 解讀層(advisor ∉ PIPELINE、import 合法);唯一新模組 `vectorstore.py` 住 `augur.knowledge`=自動被 import_isolation 閘覆蓋 | 排序 100% 來自 `prediction_values` 確定性注入;know-how 只進 prompt 引文/定義通道、**不進數字通道**(guard 數字白名單 ∈ payload.numbers()) |
| **T2** 「30/60 天走向」vs 靈魂禁占卜 | 顧問回真實模型**相對強弱排序 + 薄可信度 + know-how 解讀**,不偽造絕對機率(payload picks 只有 rank/score 無機率欄、caveat 硬編「相對強弱方向性排名、非精確數值」) | 可信度=`deflated_sharpe_broad` 廣宇宙誠實地板 + 四 caveat;guard `_FUTURE_LEAK` 機械攔「保證/必漲」 |
| **T3** FREEZE(市場資料 as-of 2026-05-31)vs know-how 抓取 | 原則精華 v1.8.0 FREEZE 只鎖**股市市場資料**;know-how≠市場資料、**明許進行**;advisor 雙態:預測側讀凍結 panel(受 FREEZE)、know-how 側不受 FREEZE | 預測通道嚴守 as-of 凍結;know-how 通道獨立不污染預測 |

---

## 2. 唯一端到端鏈 — 十個可串接 local-background stage

接縫契約 = 上游 DB 輸出表即下游輸入表(**DB 為唯一總線**);每支 `import _bootstrap`(#29a)、背景可跑、resume 靠 `knowledge_build_meta` cursor / `harvest_log` / `qdrant_sync_state`;stage 間**零 Claude/subagent/per-item LLM**(#28)。**粗體=須補的極小表面。**

```
S1 acquire_knowledge.py      [BUILT] 外部真實來源 → knowledge_staging(pending)  in: knowledge_source 3,593 列
S2 promote_knowledge.py      [BUILT] staging → item/work/thinker/citation(冪等 upsert)
S3 fetch_oa_fulltext.py      [BUILT] 三軌 license gate(公版/CC 白名單/owned_local)才入全文 + fulltext_blocked 誠實旗標
S4 build_sentences.py        [BUILT] 切句(review_flag=false ∧ CLEAN 才入)  resume: build_meta cursor
S5 build_concordance.py      [BUILT] textnorm 契約斷詞 → 逐字出現處(char_range byte-equal)  ≈49.8M 列
S6 build_lexicon.py          [BUILT] 六源公版辭書 → 逐字定義(段切/子串、零 AI)  154,875 條
S7 build_cross_school_stats.py [BUILT] ★思想相關性/相關係數引擎★(§2.1)  resume: --phase 游標/--limit 護欄
S8 embed_knowledge.py        [BUILT/待補跑] 三粒度嵌入(模型可換);works/en 1.5M 句 cursor=0=待跑(W6 背景)
S9 export_qdrant_index.py    [BUILT/門檻觸發] pgvector→Qdrant+cutover(現況無 server、讀路徑零走 Qdrant)
S10 advise/retrieval/concept_graph/serve_advisor:8399/serve_chat_ui:8090 [BUILT/部分未接] 檢索→prompt→本機 qwen:11434→guard 五閘→web UI
```

### 2.1 「思想相關性/相關係數」誠實推導(零 AI 生成)—— 已建、計畫只接線

**已經是這樣做的**(親查 `build_cross_school_stats.py`):

| 面向 | 誠實推導(method_key) | 存表(親查量) |
|------|---------------------|-------------|
| 定義 | 六源公版辭書逐字子串 | `knowledge_lexicon` 154,875 |
| 意涵 | concordance 即時解讀(advisor 對數字+逐字原文說)**不入庫** | 即時、不落表 |
| 詞↔詞相關性 | npmi / jaccard / llr-Dunning(共現計數封閉式統計) | `knowledge_term_affinity` **2,957,154** |
| 思想家↔思想家 | tfidf-cosine(**count-based 詞頻**向量、非 e5 跨語嵌入) | `knowledge_group_affinity` 6,968 |
| 群組↔詞 keyness | keyness-llr / log-odds-dirichlet | `knowledge_term_group_affinity` |
| (向量 cosine) | 僅作**索引**(紅線③、統計永不進 embedding) | `*_embedding`(檢索用) |

**紅線③**:嵌入=索引非內容,affinity 庫零向量、跨語 cosine 已證弱不入相關性庫。**擴投資 domain=`--phase vocab --domain finance` 零改碼。**

### 2.2 唯一須補(補鏈尾 + 總驅動 + 一個新 seam)
- **W-fix-1 harvest 補鏈尾**:`harvest_knowledge.py` 現只 acquire→promote(違 #29 v1.20 端到端終態)。排程矩陣尾加**條件式接續 subprocess**:promote 完→(license∈白名單)自動 fetch_oa_fulltext→build_sentences→build_concordance→embed_knowledge;**全呼叫既有 script、harvest 不含新邏輯**;非授權止於 metadata+fulltext_blocked。⚠**對抗修正**:items 側 license×entity_type 放量嵌入須 P4 用戶拍板(code 有 live fail-closed block),harvest 自動接 embed **不得繞過** items 側人拍板閘。
- **W-fix-2 總驅動**:沿用既有 `refresh_knowledge_pipeline.py`(八段 DAG)為 orchestrator,補投資域參數;`--domain X --to <stage>` 依序 subprocess、每支 resume、中斷重跑冪等。
- **W-fix-3 唯一真新 code=向量後端 factory**(§3)。

---

## 3. 可換接縫表(全已抽象,唯一真缺口=向量後端 factory)

| 接縫 | 現況(親查) | 換法 | 新 code |
|------|-----------|------|---------|
| know-how 來源 | `knowledge_source` 3,593 列 + generic_json adapter | INSERT 一列(#29b) | 無 |
| 嵌入模型 | `embedspec.MODEL_DIMS` fail-loud、collection 名烘世代 | 登記 tag+dim + `--model` | 無 |
| **向量後端** | VectorIndex 抽象基類 + Qdrant/Milvus 已存在;但 retrieval.py **4 處裸 `<=>`**、無單一 factory | 建 `knowledge/vectorstore.py`:`make_index(config)` + `PgvectorIndex(VectorIndex)` 讓 pgvector 走同介面 + DB 一列 `knowledge_vectorstore_config`;換後端=UPDATE 一列 | **是(唯一)** |
| qwen/LLM | `ollama.make_llm_fn` + `base_url()` env 覆寫 | `OLLAMA_MODEL` env 一行 | 無(**須補 G3 host 閘**) |
| web UI | serve_chat_ui:8090→serve_advisor:8399→Ollama:11434 live | 前端指向 /v1 | 無 |

**紅線③守恆**:`make_index().search()` 只回 (pg_pk, score)、不落私有向量到抽象層外。

---

## 4. 「全能全知的我」對話設計(誠實預測 ⊕ know-how 解讀 ⊕ guard、#8 隔離)

**三通道分離**:
1. **數字通道(受 FREEZE、預測側)**:`build_prediction_payload` 回 frozen payload;picks=`prediction_values` H60 in_portfolio rank **確定性注入**(不經弱 LLM);排序 100% 來自 prediction_values。
2. **引文/定義通道(不受 FREEZE、know-how 側)**:retrieve(pgvector kNN+verify_verbatim 逐字回查)+lexicon_lookup+**W2 新接 concept_graph**(related_thinkers/related_terms/cooccurrence_evidence)→進 prompt 引文段、**不進數字通道**。
3. **薄可信度通道**:`deflated_sharpe_broad` 廣宇宙誠實地板 + 四 caveat;誠實錨「淨 Sharpe~1.20=樂觀上界、非已驗證終判」。

**guard 五閘 fail-closed**:①引文逐字 ②數字白名單(∈payload.numbers()) ③_FUTURE_LEAK ④_REVERSE ⑤幻覺股名;檢索空回誠實句閉集。

**本計畫核心新增交付 = 五道「換接縫後仍守治權」的機械閘**:
- **G1 隔離擴充**:vectorstore.py + 任何新模組加進 import_isolation 對位稽核(住 knowledge/advisor 前綴、自動覆蓋)。
- **G2 向量私有洩漏閘**:不變式「嵌入表只落 pg_pk+scalar、不落私有明文」**在 pgvector 階段即建**(不等 Qdrant cutover)。
- **G3 本機 LLM 閘(v1.37.0 唯一未焊命門、親查證實)**:`make_llm_fn` **建構時即 assert** base_url ∈ {localhost,127.0.0.1,內網 allowlist}、**非等 HTTP 呼叫**(prompt 一旦連外即洩漏 owned_local)。
- **G4 derivation FK 閘**:affinity 列 method_key FK→derivation_method(已存在);擴投資域驗零 NULL。
- **G5 CLEAN 述詞三端共用**:corpus.CLEAN(NULL fail-closed)於 build/embed/retrieve 三端一致。

---

## 5. 最小 token 紀律(#28)—— 全 local background、零 per-item LLM

- 每 stage=本地 python script、DB 為總線、cursor resume;**零 Claude/subagent、零 per-item LLM/embedding 繞道**(嵌入走本機 e5-small、推理走本機 qwen)。
- 唯一「模型呼叫」=S10 顧問回合之本機 qwen 推理(#28 允許、本機零外部 usage;v1.37.0 本機限定)。
- 長跑背景 + resume-safe + 冪等,符合 #22/#25/#28。

---

## 6. 分階段 W1..W8(閘優先=閘在資料之前)+ 驗收

| 階段 | 內容 | 驗收(唯讀 SQL/測試) |
|------|------|----------------------|
| **W1** | 隔離閘擴充(G1):新增 vectorstore 前先擴 import_isolation | `import_isolation` exit 0、新模組列入 SCAN |
| **W2** | **concept_graph 接進 advise()**(最高槓桿、近零新 code)+ retrieval 加 affinity 通道 | advise() 引文帶 term_affinity basis_n;grep 證 concept_graph 被 advisor import、零 import 預測管線 |
| **W3** | 預測×解讀合流:三通道分離、薄可信度就位 | 「2330 未來 60 天?」→相對強弱排序+deflated_sharpe+know-how+四 caveat;guard 五閘全過 |
| **W4** | **向量後端 factory(唯一新 code)**:make_index+PgvectorIndex+config 表(G2) | UPDATE config 一列切 pgvector↔Qdrant 不改讀路徑碼;G2 test:嵌入表無私有明文 |
| **W5** | 本機 LLM 閘(G3):make_llm_fn 建構時 host allowlist assert | `OLLAMA_BASE_URL=http://evil make_llm_fn()`→raise(送 prompt 前);localhost 通過 |
| **W6** | harvest 補鏈尾(W-fix-1、守 items 拍板閘)+ 投資域 harvest + works/en 嵌入補完(背景) | harvest 一組合跑到 embed 終態或 fulltext_blocked;works 側 embedding>0 |
| **W7** | 顧問 know-how 解讀強化:concept_graph 多面向組裝進 prompt | 回答含逐字引文+相關係數+共現證據三面向、全 byte-equal 回鏈 |
| **W8**(門檻觸發) | Qdrant cutover + G2 完整化(現況建議不做) | 拍板後:Qdrant search 回 (pg_pk,score) 與 pgvector top-k 一致率≥閾值 |

**W1/W5 先行=閘在資料之前**;每階段 resume-safe、中斷重跑冪等、零 Claude usage(唯 S10 qwen 本機推理)。

---

## 7. 用戶拍板決策清單(決策層護欄,非判準變更、碰護欄停 #26)

**無任何靈魂/憲章判準變更**。以下屬護欄須拍板不自決:
1. **是否新建 H30/H60 誠實 horizon 模型**:屬**新預測模型、須另立預測管線計畫**——零 import knowledge/philosophy(#8)、走誠實四關(walk-forward→deflation→經濟價值 #14→標薄可信度)、**且對抗修正:須 FREEZE 綁凍結快照(只讀 as-of 2026-05-31 panel、接最新資料明文延後)**。本計畫**預設不新建**;若建則此為唯一 FREEZE 觸點。
2. **W8 Qdrant cutover 是否啟動**:現況 48 萬向量 pgvector+HNSW 甜蜜點,**建議不啟**(門檻未達;5-10M 才划算)。
3. **W4/嵌入換模放量重嵌時機**:影響全庫+跨機 DB(#30 dump),**建議先小樣本評估**。
4. **items 側放量嵌入 P4 拍板**(harvest 補鏈尾之 items 側受此閘)。
5. **concept_graph 相關係數對外呈現粒度**(顯示係數 vs 只顯示解讀)。

---

## 8. 拍板後入憲項(AFTER approval、實測後才動治權檔 #19 跨檔一致)
1. **CLAUDE.md #29**:補「知識管線端到端終態含向量後端 seam;vectorstore config 住 DB」——工具層慣例、**不動憲章**。
2. **憲章 import-isolation 條**:G1 明列 `augur.knowledge.vectorstore` 受閘覆蓋。
3. **v1.37.0 本機 LLM 命門**:G3 host allowlist 從「靠 default localhost」升為「建構時機械 assert」——命門焊死後入憲留痕(執行層補閘、非判準變更)。
4. **知識層多域擴充準則**:投資 know-how domain 納端到端終態、記 domain 欄隔離(不進因子鏈純度)。
5. **若拍板建 horizon 模型(決策1)**:另立計畫,其誠實四關+FREEZE 綁定另行入憲。

**判定**:主體=執行層補鏈/接線/補閘;入憲項多為 CLAUDE.md 工具層記載 + G3 命門焊死留痕,**無靈魂/憲章判準變更**。

---

## 附:實查證據錨(2026-07-09、venv python 直查、#15)
derivation_method **17**(四值 CHECK)· term_affinity **2,957,154**(0 NULL FK)· group_affinity **6,968** · lexicon **154,875** · concordance ≈**49.8M** · sentence **1,724,122** · knowledge_item **254,038** · knowledge_source **3,593** · import_isolation exit 0 + 7 passed · G3 缺口(ollama.base_url 無 host 驗證)證實。

**方法論**:ultracode 10-agent workflow(ground×3〔1 schema 爆、2 成〕→design×3 視角→adversarial×3 全判 NEEDS-FIX 非 VIOLATES-SOUL→synthesis)+ 主作者親查承重聲稱。**此為 plan-first(#20),拍板後才實作與入憲。**
