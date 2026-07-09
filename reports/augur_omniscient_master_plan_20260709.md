# Augur 統一 Master 計畫 —「全能全知的我」端到端(know-how 顧問 ⊕ 多 horizon 誠實預測 ⊕ 合流對話)

**日期** 2026-07-09 ｜ **性質** plan-first(#20,拍板後才實作/入憲)｜ **框架** UNIFIED-END-TO-END-FIRST + TREATY-AIRTIGHT
**合併** `reports/augur_omniscient_advisor_plan_20260709.md`(軌 A know-how)+ `reports/augur_prediction_short_horizon_model_plan_20260709.md`(軌 B 多 horizon)為**一條路**,軌 C=顧問合流。**建構 SSOT** `reports/augur_construction_understanding_20260709.md`(v2,code-verified)。
**主作者親查 code/DB(2026-07-09、venv python 直查,#15 不轉述 agent)** — 承重聲稱與對抗修正逐項複驗屬實(§附錄 A)。
**性質判定** 主體=**執行層補鏈/接線/補閘 + 既有工具加 `--horizon` 參數**;**無靈魂/憲章判準變更**(§8 逐條論證);唯 **G3 + G6 兩命門焊死後留痕**。
**⭐本次 consolidation 對抗審查關鍵新 catch(既有 2 計畫漏、親驗證實)**:**F1/G6** — 把 `concept_graph.cooccurrence_evidence` 接進 `advise()` **無 RBAC 收窄** = 逐字洩漏 owned_local(TTAI ERP)/domain 受限私有內容給登入者、**guard 擋不到**(查捏造非查授權)、破憲章 v1.36.0;code 自證:`concept_graph.py:52-64` 回原始 `s.sentence` 零 `clean_item_sql`,而 `retrieval.py:190-195` docstring **自己明令**接入前必收窄 → **G6 為接入 advise() 之硬 blocker**。**F2/G3** — `make_llm_fn` 之 `base=` 參數繞過 `base_url()` host 閘(ollama.py:66 `url=(base or base_url())`)→ G3 須 assert **最終 url** 非只 base_url()。此為 consolidation 相對前兩計畫之真增量。

---

## §0 三十秒 + 三張治權張力調解

**一句話**:augur 是**兩個半系統**(半-1 量化預測管線:features/models/universe/evaluation/ingestion/catalog/audit;半-2 博學顧問+知識層:philosophy/advisor/knowledge + 3 web server),**只被 PostgreSQL(訊息總線)+ 一個唯讀 dataclass `PredictionPayload`(payload.py)** 接起來。`audit/import_isolation.py` 機械保證單向:半-2 可讀半-1 之**輸出**、半-1 對半-2 **零反向 import**(本輪 `check_isolation()==[]`、`test_philosophy_isolation` 7 passed)。本 master 計畫把三條需求焊成**一條可串接的 local-python-background pipeline**:(A) know-how 窮舉→本地 DB raw→逐字逐句交互理解(定義/意涵/思想相關性/相關係數,**真統計零 AI**)→向量→本機 qwen→web UI;(B) 多 horizon {H20/H40/H60/H120}(+候選 H80)誠實模型走誠實四關、FREEZE 凍結快照、標**真實(多半薄)可信度**;(C) 顧問把 (B) 相對強弱+可信度 ⊕ (A) know-how 解讀合流對話。**~90% 已 BUILT**;**唯一真新 code = 向量後端 factory `vectorstore.py` + migrate + 裁決報告腳本 + G3 assert + G6 RBAC 收窄**。

| # | 治權張力 | 調解(code-anchored、機械) | 誠實維持點 |
|---|---------|---------------------------|-----------|
| **T1** 「未來 30/60/120 天走向」vs 靈魂**橫斷面相對強弱排序、禁 AI 占卜大師** | 顧問回**真實模型相對強弱排序 + 薄可信度 + know-how 解讀**;`PredictionPayload`/`StockPick`(payload.py:10-36)**無機率欄**只有 rank/score/validation;`_render_picks_table`(advise.py)由 payload ground-truth **確定性注入**(不經弱 LLM);caveat 硬編「相對強弱方向性排名、非精確數值/絕對漲跌機率」 | 排序 100% 來自 `prediction_values`;guard `_FUTURE_LEAK` 機械攔「保證/必漲」、`_REVERSE`;數字白名單 ∈ `payload.numbers()`;可信度=`deflated_sharpe_broad` 廣宇宙誠實地板 |
| **T2** know-how 餵系統 vs **#8 素養層/know-how 零量化價值不進預測管線** | know-how **只進 advisor 解讀層**(advisor ∉ PIPELINE、import 合法);唯一新模組 `augur.knowledge.vectorstore` 住 knowledge/ = **自動被 import_isolation 閘覆蓋**;know-how 進 prompt **引文/定義通道、不進數字通道** | `PIPELINE=(features,models,universe,evaluation,ingestion,audit,catalog)` **禁 import** `FORBIDDEN=(philosophy,advisor,knowledge)`(AST+字面+DB role 三重焊死);B 模型零 import 素養層;know-how domain 欄隔離、不進因子鏈純度 |
| **T3** FREEZE(市場資料 as-of 2026-05-31)vs know-how 抓取 | 原則精華 v1.8.0 FREEZE **只鎖股市市場資料**;know-how ≠ 市場資料、**明許進行**;advisor **雙態**:預測側讀凍結 panel(受 FREEZE)/ know-how 側不受 FREEZE | 預測通道嚴守 as-of 凍結(`registry.latest` asof≤ / `build_universe_asof` PIT / `walkforward` embargo);B 模型只讀凍結 panel 做 OOS walk-forward、**不為「要預測未來」去抓新資料**;know-how 通道獨立不污染預測數字 |

**主作者親查三承重聲稱全證實**:① 思想相關係數=真統計非 AI(`knowledge_derivation_method` CHECK `method_kind IN (counting/closed_form_stat/string_rule/sql_join)` 結構排除 embedding/llm;`term_affinity` 2,957,154 列 0 NULL FK)· ② know-how 隔離(`import_isolation` exit 0 + 7 passed)· ③ G3 命門真實(`ollama.base_url()` ollama.py:48-50 純回 env、`make_llm_fn` :66 裸接 `+"/api/generate"` 零 host 驗證)。**對抗最重修正 F1**:`concept_graph.cooccurrence_evidence`(concept_graph.py:52-64)回原始 `s.sentence` **零 `clean_item_sql`/access_scope 收窄**,而 `retrieval.py:190-195` `concordance_lookup` docstring **自己明令**「若未來接入顧問讀取路徑,必先加 clean_item_sql 收窄」→ **G6 收窄為 concept_graph 接入 advise() 之硬先決**。

---

## §1 一條路打通 — 統一可串接 background stage 清單(DB 為總線)

**接縫契約 = 上游 DB 輸出表即下游輸入表**;每支 `import _bootstrap`(#29a)、背景可跑、resume 靠 DB cursor/ledger;stage 間**零 Claude/subagent/per-item LLM**(#28,唯 S10/C 本機 qwen 推理)。**粗體 = 須補的極小表面。**

### 軌 A — know-how 端到端管線(半-2,寫 `knowledge_*`;advisor 唯讀讀之)

| stage | script | DB in → out | resume | zero-token | 狀態 |
|---|---|---|---|---|---|
| S1 | `acquire_knowledge.py` | `knowledge_source`(3,593)→`knowledge_staging`(pending) | harvest_log | 純 python fetch | **BUILT** |
| S2 | `promote_knowledge.py` | staging → item/work/thinker/citation(冪等 upsert、EXTID dedup) | idempotent | 本地 | **BUILT** |
| S3 | `fetch_oa_fulltext.py` | item → item_text(三軌 license gate 公版/CC/owned_local;非授權止於 metadata + `fulltext_blocked` 誠實旗標) | build_meta | 本地 | **BUILT** |
| S4 | `build_sentences.py` | item_text(CLEAN ∧ review_flag=false)→ knowledge_sentence(1.72M) | build_meta cursor | 本地 | **BUILT** |
| S5 | `build_concordance.py` | sentence + textnorm 契約斷詞 → concordance(≈49.8M,char_range byte-equal) | cursor | 本地 | **BUILT** |
| S6 | `build_lexicon.py` | 六源公版辭書 → knowledge_lexicon(154,875,子串零 AI;license public_domain-only) | 分段 | 本地 | **BUILT** |
| **S7** | `build_cross_school_stats.py` | ★相關性/相關係數引擎★ sentence/concordance → term_affinity(2,957,154)/group_affinity(6,968)/term_group_affinity(npmi/jaccard/llr/tfidf-cosine,method_key FK CHECK 封死) | `--phase` 游標/`--limit` | 本地 | **BUILT**(`--domain finance` 擴域零改碼) |
| S8 | `embed_knowledge.py` | sentence/lexicon → `*_embedding`(三粒度,模型可換) | cursor(works/en 1.5M 句 cursor=0 待補跑 W9) | 本機 e5-small | **BUILT / 待補跑** |
| S9 | `export_qdrant_index.py` | pgvector → Qdrant + cutover(現況無 server、讀路徑零走 Qdrant) | qdrant_sync_state | 本地 | **BUILT / 門檻觸發** |
| S10 | `serve_chat_ui:8090`→`serve_advisor_openai:8399`→`advise()`→Ollama qwen3:8b:11434 | retrieval→prompt→guard 五閘→web UI | — | 本機 qwen | **BUILT / 部分未接**(concept_graph 未接) |

**★S7 誠實推導對照**(親查 `build_cross_school_stats.py`,method_key FK→derivation_method):定義=lexicon 逐字子串｜意涵=advisor 對數字+逐字原文即時解讀**不入庫**｜詞↔詞=npmi/jaccard/llr-Dunning **共現計數封閉式**｜思想家↔思想家=tfidf-cosine **count-based 詞頻**(非 e5 跨語)｜群↔詞=keyness-llr/log-odds。**紅線③**:嵌入=索引非內容,affinity 庫零向量、跨語 cosine 已證弱不入相關性庫。

**軌 A 須補**:①**W-fix-1 harvest 補鏈尾**(`harvest_knowledge.py` 現只 acquire→promote,違 #29 v1.20 端到端終態;排程矩陣尾加**條件式接續 subprocess**:promote 完→license∈白名單→自動 fetch_oa→sentences→concordance→embed,非授權止於 metadata+`fulltext_blocked`;**全呼叫既有 script、harvest 不含新邏輯、不得繞過 items 側 P4 人拍板閘**)②**W-fix-2 總驅動**(沿用既有 `refresh_knowledge_pipeline.py` 八段 DAG,補 `--domain finance --to <stage>`)③**W-fix-3 唯一真新 code=向量後端 factory**(§6)。

### 軌 B — 多 horizon 誠實預測模型 matrix(半-1,寫 `prediction_values`/`revalidation_ledger`;零 import 素養層)

| stage | script | DB in → out | resume | zero-token | 狀態 |
|---|---|---|---|---|---|
| B1 | `train_ranker.py --horizon {20,40} --run` | feature_values/core_universe_asof → model_registry(H60/H120 已訓) | registry idempotent | 本地(Ridge 確定性 / GBDT seeds 42,43,44 取中位) | **既有(參數)/ 須跑 H20/H40** |
| B2 | `predict_asof.py --horizon {20,40}` | model_registry/feature_values(**只讀 as-of 2026-05-31 凍結 panel**)→ prediction_values(in_portfolio=0 候選) | PIT `registry.latest` asof≤ | 本地 | **既有(參數)** |
| B3 | `revalidate.py --run` | feature_values → revalidation_ledger(Stage B IC+HAC-t / C/D 經濟)+ trial_ledger | ledger upsert | 本地 | **改**(B_HORIZONS 加 40 / CD_HORIZONS 加 20,40) |
| B4 | `deflate_headline_verdict.py --horizon {20,40}` | revalidation_ledger/trial_ledger → 裁決印出(per-period DSR、取保守 N) | — | 本地 | **既有(參數)** |
| B5 | `report_multi_horizon_verdict.py` | revalidation_ledger/trial_ledger → reports/(H20/40/60/120 對比 + 日曆日對映 + 真實可信度) | — | 本地 | **新(唯一 B 側新 code)** |

**四關全複用既有 evaluation SSOT**(baseline/walkforward/metrics/portfolio/deflation),零雙軌漂移(#12);horizon 只是參數。embargo 下界=`h + _FEATURE_LAG_TD(62)`、`_H_FORBIDDEN=252`(H20=82/H40=102/H60=122/H80=142/H120=182 皆 <252,全可訓)。

### 軌 C — 顧問合流(半-2 讀半-1 輸出,`advise()` 三通道分離)

| stage | 元件 | 通道 | 治權維持 |
|---|---|---|---|
| C1 | `build_prediction_payload`(payload.py 唯一 join) | **① 數字通道(受 FREEZE)**:讀 prediction_values + model_registry + TaiwanStockInfo + revalidation_ledger → frozen payload;picks=對應 horizon in_portfolio rank **確定性注入** | 排序 100% 來自 prediction_values;無機率欄 |
| C2 | retrieve(pgvector kNN + verify_verbatim)+ lexicon_lookup + **concept_graph(W2 新接、G6 收窄後)** | **② 引文/定義通道(不受 FREEZE)**:related_thinkers/related_terms/cooccurrence_evidence → prompt 引文段 | know-how 只進引文通道、不進數字通道;數字白名單 ∈ payload.numbers() |
| C3 | `deflated_sharpe_broad` + 四 caveat | **③ 薄可信度通道** | 誠實錨「淨 Sharpe~1.20=樂觀上界、非已驗證終判」 |

**guard 五閘 fail-closed**(guard.py):① 引文逐字 ② 數字白名單 ③ `_FUTURE_LEAK` ④ `_REVERSE` ⑤ 幻覺股名;檢索空回誠實閉集二句。

---

## §2 多 horizon 誠實 matrix(H20/H40/H60/H120 + 候選 H80)

### 2.1 「30/60/120 天」單位釐清(命門,先釘清才不誤導)

horizon 單位是**交易日**;1 交易日 ≈ 1.45 日曆日(親查)。用戶「N 天」須釐清日曆日 vs 交易日:

| 用戶說法 | 若=**日曆日** → 交易日 | 若=**交易日** | 對應 horizon | 狀態 |
|---|---|---|---|---|
| 30 天 | ≈ **H20**(20 td ≈ 28-30 cal) | H30(≈ H20 近似) | **H20** | 既有評估:IC 0.113、經濟 cell=0 **判死** |
| 60 天 | ≈ **H40**(40 td ≈ 58 cal) | **H60** | **H40**(新)或 **H60**(已部署) | H40 未訓練;H60 IC 0.152/DSR 0.756 未確立 |
| 120 天 | ≈ **H80**(80 td ≈ 116-120 cal) | **H120** | **H80**(新候選)或 **H120**(已訓) | H80 未訓;H120 已訓=最強候選 |
| (H60 已部署) | 60 td ≈ 84 cal ≈ 3 月 | — | H60 | deploying_unestablished |

**計畫做 horizon 矩陣 {H20, H40, H60, H120}**(H20/H40 新訓、H60/H120 既有);**H80 為「日曆 120 天」精確對應之新候選,是否訓練列 §7 拍板**(因 H120 已為最強候選、H80 增量存疑)。由驗證結果 + 用戶確認「日曆日 vs 交易日」定採哪個。

### 2.2 誠實四關管線(全複用既有 SSOT)

```
train_ranker.py --horizon {20,40} --run    # RankRidge 確定性 + RankGBDT 多 seed
  → 第1關 purged walk-forward(walkforward.splits,embargo=h+62td,H<252 允許;guaranteed 路才作準)
  → 第2關 as-of rank IC + HAC effective_t_hac(禁裸 iid effective_t、審查 G8;|HAC-t|≥2)
  → 第3關 經濟價值 #14(portfolio.run_backtest,net=gross−turn×COST_TW 0.00585,long top10% vs 基準;IC≠可交易、成功=經濟價值)
  → 第4關 deflation DSR(deflate_headline_verdict --horizon N,per-period,兩層保守-N 取 min;trial_ledger 機械 count)
  → revalidation_ledger(B/C/D)+ trial_ledger + 誠實 verdict(標真實可信度、n 小 exploratory 揭露)
```

### 2.3 各 horizon 已知證據 + 誠實裁決(#15,基於親查)

| horizon | ≈ 日曆日 | 已知證據(親查) | 誠實裁決 |
|---|---|---|---|
| **H20** | ≈ 30 天 | IC 0.113、經濟 cell=**0** | **判死**(維持;大概率過不了經濟價值) |
| **H40** | ≈ 60 天 | 新、介於 H20/H60 | **未知,預判薄**(短 horizon + 特徵飽和) |
| **H60** | ≈ 84 天(3 月) | 已部署;IC 0.152、DSR 0.756 | **未確立**(deflation 未過) |
| **H80** | ≈ 120 天 | 新候選、未訓;介於 H60/H120 | 待 §7 拍板是否訓;預判介於兩者 |
| **H120** | ≈ 174 天(6 月) | 已訓=**最強候選**;asof IC 0.155、**headline DSR 0.9359(93.6%)、deflated_sharpe 0.533、n=14** | **⚠ 仍未確立**:headline 93.6% 係 n_fam=8 之 95.8% PASS 與 **n_all=16 之 93.6% FAIL 跨越取保守 → 未達 95% 門檻 → deploying_unestablished**;淨 Sharpe~1.20=樂觀上界、deflation/survivorship/成本閘未完全建(memory `prediction-headline-undeflated`),**非已驗證終判** |

**H120 增量框定(誠實)**:H120 是既有最強候選、方向性反證「越長 horizon 越強、短的更難」,但**保守 N=16 下 deflation FAIL、仍屬未確立**——本計畫把 H120 當「最強候選、標好薄可信度餵顧問」,**不宣稱為可靠 6 月漲跌預言**(違靈魂)。誠實結論預期:「30/60 天」比 H60/H120 **更難確立**,多半是薄 edge、誠實標籤交付即成功(#15)。

---

## §3 可換接縫表(全已抽象;唯一真缺口=向量後端 factory)

| 接縫 | 現況(親查) | 換法 | 新 code |
|---|---|---|---|
| know-how 來源 | `knowledge_source` 3,593 列 + 13 adapter(含 generic_json adapter_config JSONB) | INSERT 一列(#29b) | 無 |
| 嵌入模型 | `embedspec.MODEL_DIMS` fail-loud、collection 名烘世代 | 登記 tag+dim + `--model` | 無 |
| **向量後端** | `vectorindex.py` 有 `VectorIndex`(:27)/`MilvusLiteIndex`(:52)/`QdrantIndex`(:159) 各具 `.search()`;但 retrieval.py **4 處裸 `<=>`**(:77/84/310/314)、**缺 `PgvectorIndex` 與單一 factory** | 建 `knowledge/vectorstore.py`:`make_index(config)` + `PgvectorIndex(VectorIndex)` 走同介面 + DB 一列 `knowledge_vectorstore_config`;換後端=UPDATE 一列 | **是(唯一真新)** |
| qwen/LLM | `ollama.make_llm_fn` + `base_url()` env 覆寫(**零 host 驗證**) | `OLLAMA_MODEL` env 一行 | 無(**須補 G3 host 閘**) |
| web UI | serve_chat_ui:8090→serve_advisor:8399→Ollama:11434 live | 前端指向 /v1 | 無 |
| horizon | `train_ranker/predict_asof --horizon`(default 60、主戰場 20/60) | `--horizon N` 參數 | 無(revalidate.py 加常數) |

**紅線③守恆**:`make_index().search()` 只回 `(pg_pk, score)`、不落私有向量到抽象層外。

---

## §4 新增機械閘 G1-G6(換接縫後仍守治權;G6=對抗 F1 最重修正)

> 基礎設計 G1-G5(omniscient §4);**對抗審查新增 G6(concept_graph RBAC 收窄)為接入 advise() 之硬先決**——F1 為最重單一治權缺陷(HIGH,owned_local/RBAC 洩漏)。

| 閘 | 職責 | code-anchor / 不變式 | 型態 |
|---|---|---|---|
| **G1 隔離擴充** | vectorstore.py 及任何新模組加進 import_isolation 對位稽核 | 住 knowledge/advisor 前綴 → 自動被 `check_isolation()` 四偵測面覆蓋;`import_isolation` exit 0、新模組列入 SCAN | AST+字面 |
| **G2 向量私有洩漏閘** | 嵌入表只落 pg_pk+scalar、不落私有明文 | **在 pgvector 階段即建**(不等 Qdrant cutover);`make_index().search()→[(pg_pk,score)]` | 不變式測試 |
| **G3 本機 LLM 閘**(v1.37.0 唯一未焊命門) | `make_llm_fn` **建構時 assert** `base_url` host ∈ {localhost,127.0.0.1,內網 allowlist}、**非等 HTTP 呼叫** | ollama.py:66 現裸接 `+"/api/generate"` 零驗證 → prompt(含 owned_local citations)一旦連外即洩漏;焊後 `OLLAMA_BASE_URL=http://evil make_llm_fn()`→raise(送 prompt 前) | 建構時 assert |
| **G4 derivation FK 閘** | affinity 列 method_key FK→derivation_method(已存在);擴投資域驗零 NULL | `knowledge_derivation_method` CHECK `method_kind IN (counting/closed_form_stat/string_rule/sql_join)` DB 硬擋 embedding/llm | DB CHECK+FK |
| **G5 CLEAN 述詞多端共用** | `corpus.CLEAN`(NULL fail-closed)於 build/embed/retrieve 三端一致 | corpus.clean_work_sql=review_flag=false ∧ literary(NULL fail-closed) | 共享述詞 |
| **G6 concept_graph RBAC 收窄**(對抗 F1、接入前硬先決) | `cooccurrence_evidence` 接入 advise() 前**必先加 `corpus.clean_item_sql` 收窄**(access_scope/owner_user_id/domain fail-closed);`related_thinkers`(group_affinity thinker,literary 較安全)/`related_terms`(term_affinity 聚合統計無原文,最安全)可保留 | concept_graph.py:52-64 現回原始 `s.sentence` 零收窄;retrieval.py:190-195 docstring 自警;retrieve_items(:265-277)`corpus.clean_item_sql("i","x",...)` 為 RBAC 先例。**guard 擋不到**(洩漏是逐字真句、無捏造數字→五閘全隱形)→ 必用 RBAC 收窄 | SQL 收窄 fail-closed |

**G3/G6 為兩道命門**:G3 焊死 v1.37.0 本機限定、G6 焊死 owned_local/RBAC(憲章 v1.36.0)。二者皆執行層補閘、非判準變更,焊後留痕(§8)。

---

## §5 分階段 W1..W12 + 驗收(閘優先=閘在資料/接線之前)

每階段 resume-safe、中斷重跑冪等、零 Claude usage(唯 S10/C 本機 qwen)。改常駐服務(chat/advisor/admin)之碼後**須重啟載入新碼再實測**(#7)。

### Phase I — 機械閘先行(閘在資料之前)

| 階段 | 內容 | 驗收(唯讀 SQL/測試) |
|---|---|---|
| **W1** | G1 隔離閘擴充(新增 vectorstore 前先擴 import_isolation SCAN) | `import_isolation` exit 0、新模組列入 SCAN |
| **W2** | **G6 concept_graph RBAC 收窄**(F1 修正、接入前硬先決):`cooccurrence_evidence` 加 clean_item_sql | 對 local_private/domain 受限 item 查詢回空或收窄;grep 證 cooccurrence_evidence 帶 clean_item_sql |
| **W3** | G3 本機 LLM 閘:`make_llm_fn` 建構時 host allowlist assert | `OLLAMA_BASE_URL=http://evil` → raise(送 prompt 前);localhost 通過 |
| **W4** | **向量後端 factory(唯一真新 code)**:`make_index`+`PgvectorIndex`+config 表(G2) | UPDATE config 一列切 pgvector↔Qdrant 不改讀路徑碼;G2 測試:嵌入表無私有明文 |

### Phase II — know-how 接線

| 階段 | 內容 | 驗收 |
|---|---|---|
| **W5** | **concept_graph 接進 advise()**(G6 收窄後、最高槓桿近零新 code)+ retrieval 加 affinity 通道 | advise() 引文帶 term_affinity basis_n;grep 證 concept_graph 被 advisor import、零 import 預測管線 |
| **W6** | harvest 補鏈尾(W-fix-1、守 items 側 P4 拍板閘)+ 投資域 harvest + works/en 嵌入補完(背景) | harvest 一組合跑到 embed 終態或 fulltext_blocked;works 側 embedding>0 |

### Phase III — 多 horizon 誠實 matrix

| 階段 | 內容 | 驗收 |
|---|---|---|
| **W7** | forward_returns@H40 口徑確認(label.py on-the-fly、無表;embargo=102td<252) | `walkforward.splits(pds,40,cal)` 不 raise、逐折 embargo≥102td guaranteed |
| **W8** | train H20/H40(RankRidge+GBDT 多 seed)+ predict_asof 凍結快照(只讀 as-of 2026-05-31) | model_registry 加 H20/H40 列、prediction_values 出(in_portfolio=0 候選) |
| **W9** | 誠實四關:revalidate.py(B_HORIZONS 加 40 / CD_HORIZONS 加 20,40)Stage B IC+HAC-t、C/D 經濟、deflation 取保守 N | revalidation_ledger 補 H20/H40 B/C/D;deflate --horizon 40 出 DSR |
| **W10** | 誠實裁決報告 `report_multi_horizon_verdict.py`:H20/H40/H60/H120 對比(IC/Sharpe/Calmar/DSR/deflated)+ 日曆日對映 | 報告 reports/;每 horizon 標【確立/未確立/判死】+ n 小 exploratory 揭露 |

### Phase IV — 顧問合流(軌 C)

| 階段 | 內容 | 驗收 |
|---|---|---|
| **W11** | 三通道合流:數字(受 FREEZE)+ 引文/定義(know-how)+ 薄可信度就位;顧問對「30/60/120 天」回對應 horizon | 端到端:「2330 未來 60 天?」→ 相對強弱排序 + deflated_sharpe + know-how 逐字引文+相關係數 + 四 caveat;guard 五閘全過 |

### Phase V — 門檻觸發(現況建議不做)

| 階段 | 內容 | 驗收 |
|---|---|---|
| **W12**(門檻觸發) | Qdrant cutover + G2 完整化(48 萬向量 pgvector+HNSW 甜蜜點、5-10M 才划算) | 拍板後:Qdrant search 回 (pg_pk,score) 與 pgvector top-k 一致率≥閾值 |

**W1-W4 先行=閘在資料/接線之前**(G6 為 W5 接入之硬先決);部署切換(某 horizon 過關)屬決策層人拍板(#26,AI 不自改 in_portfolio)。

---

## §6 table schema(DDL + 既有表)+ python 程式規畫(憲章 v1.39.0 計畫完整性)

### 6.1 唯一新表 = 向量後端 factory config(DDL 住 `scripts/migrate_vectorstore_config_ddl.py`、冪等 guard)

```sql
CREATE TABLE IF NOT EXISTS knowledge_vectorstore_config (
  scope        text PRIMARY KEY,                 -- 'sentence'/'lexicon'/'philosophy_chunk' 三粒度
  backend      text NOT NULL DEFAULT 'pgvector'
                 CHECK (backend IN ('pgvector','qdrant_embedded','qdrant_server')),
  embed_model  text NOT NULL,                    -- embedspec MODEL_TAG(世代烘入 collection 名)
  dims         int  NOT NULL,                    -- embedspec MODEL_DIMS
  endpoint     text,                             -- qdrant url/path(pgvector 為 NULL)
  updated_at   timestamptz NOT NULL DEFAULT now()
);  -- 換後端 = UPDATE 一列(#29b 決定行為的資料住 DB;唯一 sanctioned host 由 G3 allowlist 另管)
```

### 6.2 多 horizon:**無新表**(全落既有;schema 權威=DB information_schema #2)

| 既有表 | PK / 關鍵欄 | 本計畫寫入 |
|---|---|---|
| `model_registry` | model_id;family/horizon/feats_hash/seed/metrics/train_span/asof_snapshot | 加 H20/H40 列(H60/H120 已在) |
| `prediction_values` | (panel_date,model_id,stock_id);rank/score/in_portfolio | 加 H20/H40:in_portfolio=0 候選 |
| `revalidation_ledger` | (run_at,as_of_date,stage,horizon,model,config,metric_name);metric_value/n_periods/hac_t | 補 H20/H40 之 B/C/D 列 |
| `trial_ledger` | (model,horizon,top_frac,weight,feats_hash,cost,sample_since);seed 揭露欄 | 加 H20/H40 試驗列(保守 N=機械 count) |
| (deflation) | 讀 trial_ledger + portfolio 即時重算 | 不落新表(裁決印出) |

### 6.3 軌 A 所讀/所觸既有表(不改 schema、唯讀或既有寫入)

knowledge_source/staging/item/item_text/sentence/concordance/lexicon(素養)· term_affinity/group_affinity/term_group_affinity/derivation_method(★相關係數,唯讀,method_key FK)· *_embedding 三粒度(向量,唯讀檢索)· prediction_values/model_registry/revalidation_ledger/baseline/verdict(預測側,advisor 唯讀)· qdrant_sync_state/knowledge_build_meta(游標)· app_user/session/group_domain_grant(RBAC,G6 讀之)。

### 6.4 python 程式規畫(v1.39.0;守 #12 複用鐵律)

| 程式 | 新/改 | 職責·關鍵函式 | 輸入表→輸出表 |
|---|---|---|---|
| `src/augur/knowledge/vectorstore.py` | **新** | `make_index(config)→VectorIndex`;`PgvectorIndex(VectorIndex)` 走同介面;`.search()→[(pg_pk,score)]`(紅線③) | knowledge_vectorstore_config →(index handle) |
| `scripts/migrate_vectorstore_config_ddl.py` | **新** | 建 config 表 + 種子三粒度列(冪等) | — → knowledge_vectorstore_config |
| `scripts/report_multi_horizon_verdict.py` | **新** | W10:H20/40/60/120 對比 + 真實可信度 + 日曆日對映 | revalidation_ledger/trial_ledger → reports/ |
| `src/augur/advisor/ollama.py::make_llm_fn` | **改** | G3:建構時 assert base_url host∈allowlist、非等 HTTP(v1.37.0) | env OLLAMA_BASE_URL(驗證) |
| `src/augur/knowledge/concept_graph.py::cooccurrence_evidence` | **改** | G6/F1:接入前加 corpus.clean_item_sql 收窄(access_scope/owner/domain fail-closed) | concordance/sentence(收窄)→ 引文段 |
| `src/augur/advisor/{advise,retrieval}.py` | **改** | W5:concept_graph(related_thinkers/terms/cooccurrence 收窄後)進引文通道;retrieval 走 make_index() | affinity/embedding → prompt 引文段 |
| `src/augur/audit/import_isolation.py` | **改** | G1:SCAN 納 `knowledge.vectorstore`(自動覆蓋) | — |
| `scripts/revalidate.py` | **改** | B3:`B_HORIZONS=(20,60,120)` 加 40 / `CD_HORIZONS=(60,120)` 加 20,40 | feature_values → revalidation_ledger + trial_ledger |
| `scripts/harvest_knowledge.py` | **改** | W-fix-1:矩陣尾條件式接 fetch_oa→sentences→concordance→embed(守 items P4 拍板閘) | knowledge_staging →(既有鏈) |
| `scripts/refresh_knowledge_pipeline.py` | **改** | W-fix-2:總驅動補 `--domain finance --to <stage>` | (編排既有 script) |
| `scripts/train_ranker.py --horizon {20,40} --run` | 既有(參數) | RankRidge 確定性 + RankGBDT 多 seed | feature_values/core_universe_asof → model_registry |
| `scripts/predict_asof.py --horizon {20,40}` | 既有(參數) | 凍結快照預測、in_portfolio=0 候選 | model_registry/feature_values → prediction_values |
| `scripts/deflate_headline_verdict.py --horizon {20,40}` | 既有(參數) | per-period DSR 取保守 N | revalidation_ledger/trial_ledger →(裁決印出) |
| `scripts/verify_candidate_promotion.py` | 既有 | 提拔關卡 HAC-t(禁裸 iid) | revalidation_ledger →(裁決) |
| `scripts/build_cross_school_stats.py` | 既有 | S7 ★相關係數引擎★(`--phase vocab --domain finance` 擴域零改碼) | sentence/concordance → term/group_affinity |
| `scripts/embed_knowledge.py` | 既有 | S8 三粒度嵌入(`--scope works/en` 補跑) | sentence/lexicon → *_embedding |
| `scripts/{serve_advisor_openai,serve_chat_ui}.py` | 既有(改碼後 #7 重啟) | S10/C 顧問殼 + web UI | — |

**唯一真新 code** = vectorstore.py + migrate + report_multi_horizon_verdict.py + G3 assert + G6 收窄;其餘=既有程式加參數/接線。

---

## §7 用戶拍板決策清單(決策層護欄,碰護欄停 #26)

1. **「30/60/120 天」= 日曆日還是交易日?** — 日曆日→{H20,H40,H80};交易日→{H20/H30,H60,H120}。定 matrix 採哪組。
2. **接受「多半薄/未確立」誠實預期?** — 以誠實可信度標籤交付,**非保證贏、非可靠漲跌預言**(H120 最強候選亦保守 N=16 下 FAIL)。
3. **是否訓練 H80?**(日曆 120 天精確對應) — H120 已為最強候選,H80 增量存疑;訓 or 依 H120。
4. **W2/G6 concept_graph RBAC 收窄為接入 advise() 之硬 blocker(對抗 F1)** — 確認接入前必焊 G6(否則繞過 RBAC 洩漏 local_private/domain 受限逐字內容)。
5. **W12 Qdrant cutover 是否啟動?** — 現況 48 萬向量 pgvector+HNSW 甜蜜點,**建議不啟**(5-10M 才划算)。
6. **W4/嵌入換模放量重嵌時機 + items 側放量嵌入 P4 拍板** — 影響全庫+跨機 DB(#30 dump),建議先小樣本評估;harvest 補鏈尾之 items 側受此閘。
7. **concept_graph 相關係數對外呈現粒度** — 顯示係數 vs 只顯示解讀。
8. **某 horizon 過四關後是否部署?**(改 in_portfolio) — 決策層人拍板,AI 不自改。

---

## §8 拍板後入憲項(AFTER approval、實測後才動治權檔 #19 跨檔一致)

1. **CLAUDE.md #29**:補「知識管線端到端終態含向量後端 seam;vectorstore config 住 DB」——工具層慣例、**不動憲章**。
2. **憲章 import-isolation 條**:G1 明列 `augur.knowledge.vectorstore` 受閘覆蓋。
3. **v1.37.0 本機 LLM 命門**:G3 host allowlist 從「靠 default localhost」升為「建構時機械 assert」——**命門焊死後入憲留痕**(執行層補閘、非判準變更)。
4. **憲章 v1.36.0 owned_local/RBAC 命門**:G6 concept_graph `cooccurrence_evidence` clean_item_sql 收窄——**F1 命門焊死後入憲留痕**(RBAC 收窄擴至 concept_graph 讀取路徑)。
5. **horizon 矩陣結果 + FREEZE 綁定**:結果記憲章修訂歷程/方法論;若某 horizon 過四關且人拍板部署→ payload `_DEPLOY_HORIZON` + revalidation baseline(承 H120 tracked-candidate 慣例);FREEZE 綁定(只凍結快照、接最新資料明文延後)留痕。
6. **知識層多域擴充準則**:投資 know-how domain 納端到端終態、記 domain 欄隔離(不進因子鏈純度)。

**判定**:主體=執行層補鏈/接線/補閘 + 既有工具加 `--horizon` 參數;**無靈魂/憲章判準變更**(相對強弱 + 誠實四關 + FREEZE + #8 隔離皆既有法律之落地);**唯 G3 + G6 兩命門焊死後留痕**。此為 plan-first(#20),拍板後才實作與入憲。

---

## 附錄 A — 實查證據錨(2026-07-09、venv python 直查、#15)

- **相關係數=真統計**:`knowledge_derivation_method` CHECK `method_kind IN (counting/closed_form_stat/string_rule/sql_join)`;`term_affinity` **2,957,154**(0 NULL FK)· `group_affinity` **6,968** · `lexicon` **154,875** · concordance ≈**49.8M** · sentence **1,724,122** · `knowledge_source` **3,593**。
- **隔離**:`import_isolation` exit 0 + `test_philosophy_isolation` 7 passed;`PIPELINE` 7 pkg 禁 import `FORBIDDEN=(philosophy,advisor,knowledge)`。
- **G3 缺口**(ollama.py:48-50,66):`base_url()` 純回 env、`make_llm_fn` 裸接 `+"/api/generate"` 零 host 驗證 → 證實。
- **F1/G6 缺口**(concept_graph.py:52-64):`cooccurrence_evidence` 回原始 `s.sentence` 零 clean_item_sql;`retrieval.py:190-195` docstring 自警「接入顧問讀取路徑必先加 clean_item_sql 收窄」;`retrieve_items`(:265-277)為 RBAC 先例;concept_graph **0 importers(unwired)** 證實。
- **向量 factory 缺口**(vectorindex.py):有 `VectorIndex`(:27)/`MilvusLiteIndex`(:52)/`QdrantIndex`(:159)、**無 `PgvectorIndex`/`make_index`**;retrieval.py 4 處裸 `<=>`(:77/84/310/314)。
- **horizon**:`revalidate.py:48-49` `B_HORIZONS=(20,60,120)` / `CD_HORIZONS=(60,120)`;`train_ranker/predict_asof --horizon` default 60(主戰場 20/60);embargo 下界=`h+62`、`_H_FORBIDDEN=252`(H20=82/H40=102/H60=122/H80=142/H120=182 皆 <252)。
- **H120 誠實**:asof IC 0.155、headline DSR **0.9359** 係 n_fam=8 之 95.8% PASS 與 **n_all=16 之 93.6% FAIL 跨越取保守 → 未確立**;deflated_sharpe 0.533、n=14;淨 Sharpe~1.20=樂觀上界。

**相關檔案(絕對路徑)**:
- `/home/hugo/project/augur/reports/augur_omniscient_advisor_plan_20260709.md`(軌 A 來源)
- `/home/hugo/project/augur/reports/augur_prediction_short_horizon_model_plan_20260709.md`(軌 B 來源)
- `/home/hugo/project/augur/reports/augur_construction_understanding_20260709.md`(建構 SSOT)
- `/home/hugo/project/augur/src/augur/advisor/ollama.py`(G3)· `/home/hugo/project/augur/src/augur/knowledge/concept_graph.py`(G6/F1)· `/home/hugo/project/augur/src/augur/philosophy/retrieval.py`(RBAC 先例+F1 docstring 自警)· `/home/hugo/project/augur/src/augur/knowledge/vectorindex.py`(向量 factory 缺口)· `/home/hugo/project/augur/scripts/revalidate.py`(horizon 常數)· `/home/hugo/project/augur/src/augur/audit/import_isolation.py`(G1)