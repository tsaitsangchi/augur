# Augur 全能全知端到端主計畫 v3 —「相對機率誠實層 ⊕ know-how 一條路 ⊕ 未來適用接縫」(定稿)

**日期** 2026-07-10 ｜ **檔案** `reports/augur_omniscient_e2e_master_plan_20260710.md` ｜ **性質** plan-first(#20,拍板後才實作/入憲)
**合併取代**:`augur_omniscient_master_plan_20260709.md` + `augur_omniscient_advisor_plan_20260709.md` + `augur_prediction_short_horizon_model_plan_20260709.md`(+`augur_short_horizon_verdict_20260709.md`,H20/H40 已執行、結果引 §1.2)+ `augur_vectorstore_qdrant_migration_plan_20260707.md` + `augur_knowledge_cross_doctrine_graph_plan_20260707.md`。
**對抗審查**:四鏡(治權/誠實/工程/經濟)A-1..A-36 逐項留痕於 §7(CLAUDE #20 高風險門檻:跨 ≥2 治權檔+治權判準草擬)。
**不可違三則(全文橫貫)**:① know-how 不進預測管線(#8 隔離不鬆動;import_isolation AST 閘+`augur_predict` DB role 雙閘既有、本計畫零觸碰其判準);② FREEZE(原則精華 v1.8.0)下無新市場資料——機率層全用**既有 walk-forward OOS 折**校準;③ 禁 AI 生成內容入庫(含煙測 sentinel,§2.3)。

---

## 0. 三十秒 + 七需求對照表

**一句話**:把用戶的「30/60/120 天股價走向機率」**誠實轉譯**為靈魂唯一相容的「橫斷面相對強弱之校準機率」P(勝過同儕中位數 | as-of, H)(§1,walk-forward OOS 折 purge 校準+可靠度硬綁揭露),並把 know-how 端到端一條路(外部窮舉抓取→PostgreSQL→逐字逐句交互理解→Qdrant→qwen→web UI「全能全知的我」)焊成**單命令、零 Claude token、resume-safe** 的本地背景管線(§2–§3),四個未來接縫(新來源/換向量模型/換 qwen/換向量後端)全收斂為**資料列或 env 一行**(§4)。新表 5 張全附 DDL(§5)、新/改程式 9 支全附用途+CLI 指令矩陣+輸入輸出(§6),分階段 P1–P8+驗收+拍板點(§6.11),末附入憲草案 v1.40.0(§8)。

| 需求(用戶拍板方向) | 承載章節 | 一句話 |
|---|---|---|
| **(1) 新預測輸出:30/60/120 天走向「機率」** | §1(轉譯+四誠實標記+校準設計)· §5.2–5.5(DDL)· §6.1–6.4(程式)· §8.2(判準入憲) | 禁絕對漲跌機率(紅線);唯一合法=橫斷面相對機率+purge 校準+可靠度硬綁 |
| **(2) know-how 端到端一條路打通** | §2(S1–S10 地圖+D7 驅動器+煙測+Qdrant cutover)· §6.6/6.7/6.9 | 每支可串接、單命令背景可跑全鏈;暢通=煙測機械判定 |
| **(3) 全程本地 python 背景、零 Claude token、resume-safe** | §3(橫切紀律,逐段 resume 機制矩陣) | 唯 S10 本機 qwen 推理(v1.37.0 本機不在此限) |
| **(4) 未來適用** | §4(四接縫:INSERT 一列/embedspec SOP-A/**換 qwen ollama 參數**/config 資料列) | 擴充=資料列;換模=env 一行+重啟(#7);零改碼 |
| **(5) 憲章 v1.39.0 計畫完整性** | §5(每張表 DDL)+ §6(每支程式 用途+CLI 矩陣+I/O)+ §6.11(分階段+驗收+拍板點) | 本節即自證 |
| **(6) 對抗審查發現表留痕** | §7(A-1..A-36,四鏡) | CLAUDE #20 高風險門檻履行 |
| **(7) 入憲草案** | §8(憲章 v1.40.0 兩條文+修訂列草文) | 主 session 拍板後實際套用 |
| **(8) 硬體平台雙軌(GPU / CPU-only)** | §9(段別敏感度矩陣+自動偵測+qwen tier 表+兩檔時間預算) | 全鏈唯 S10 重 GPU;CPU-only 功能不縮只慢;偵測落帳自動調參 |

---

## 1. 需求(1) 機率層 — 靈魂紅線之誠實轉譯

### 1.0 紅線與轉譯(拍板題 D0)

用戶原句「個股 2026-05-31 之後 30/60/120 天股價走向機率」若照字面做=**輸出絕對漲跌機率=假兆**(HANDOFF 誠實紅線;個股絕對方向由市場 beta 主導、系統無 market-timing 證據、FREEZE 下未來未實現亦無校準對象)。**本計畫向用戶明示轉譯**:系統交付的唯一合法口徑=

> **P(該股於 horizon H 之已實現報酬 勝過 同儕橫斷面中位數 | as-of=2026-05-31, H)** —— 橫斷面相對強弱之校準機率。

為何唯一合法:模型本身即 rank 模型(RankRidge 橫斷面分位)、四關驗證全是橫斷面口徑(as-of IC/分位投組);OOS 折之**相對標籤已於 FREEZE 內實現** → 有真實對樣本可校準(#9);「會不會漲」則無。此轉譯=D0 拍板題,**未簽核不動工**。

### 1.1 四項誠實標記(與機率數字硬綁,缺一即 `verify_advisor_regression` FAIL)

| # | 標記 | 固定用語承載 |
|---|---|---|
| ① | **橫斷面口徑聲明** | 「P=在同儕中勝過中位數之機率(as-of 2026-05-31、橫斷面相對、**非**『會漲的機率』);逐折 n=25/25/25/14(H20/40/60/120),n 小屬 exploratory」——含 as-of 日期(FREEZE 下非即時,A-29)與逐折 n(A-26) |
| ② | **日曆日↔交易日對映偏差** | 每欄帶日曆日標籤+偏差:P30←H20(≈29 cal,−3%)/P60←H40(≈58 cal,−3%)/P120←H120(≈174 cal,**+45%**)或 H82(≈119 cal,−1%,條件觸發) |
| ③ | **經濟判死標籤** | `econ_verdict` 與機率同列不可分離(D2):H20='dead'(淨 Sharpe +0.27 < 基準 +0.30、無經濟 alpha);H40/H60/H120='thin_unestablished'(DSR 0.308/0.407/0.771 < 0.95) |
| ④ | **同族近似聲明**(A-36) | 「校準器 fit 於 walk-forward 逐折 refit 之同族(RankRidge)模型,serve 套於 train_ranker 全樣本 artifact 之分位——**同 family、非同一模型**,機率為同族近似值」——固定 caveat 用語與 P2 規格②/P6 同帶 |

**硬綁機制**:四標記由**確定性渲染層**(承 `_render_picks_table` 之 payload ground-truth 注入路線,不經弱 LLM)與機率數字同段輸出;機率值納 `payload.numbers()` guard 數字白名單(A-10);渲染逐值等同 DB=回歸斷言(§6.5)。

### 1.2 30/60/120 日曆日對映決策建議(拍板題 D1/D2;證據=`augur_short_horizon_verdict_20260709.md`,已執行)

horizon 單位=交易日,1 td ≈ 1.45 cal(實查):

| 用戶「N 天」(日曆日) | 對映 | ≈日曆日(偏差) | 已知證據(#9,revalidation_ledger) | 裁決 |
|---|---|---|---|---|
| 30 | **H20** | 29(−3%) | IC +0.113/HAC-t +6.09;淨 Sharpe +0.27 < 基準 +0.30;DSR 0.001;n=25 | **判死**(D2:P30 照出+`econ_verdict='dead'` 硬綁) |
| 60 | **H40** | 58(−3%) | IC +0.150;淨 Sharpe +1.11 vs 0.88(alpha +0.23);DSR 0.308;n=25 | 未確立(薄) |
| (部署主欄) | **H60** | 87 | IC +0.152;淨 Sharpe +1.20 vs 0.76(alpha +0.43);DSR 0.407;n=25 | 未確立(薄);picks 主欄 |
| 120 | **(b) H120** 主建議 | 174(**+45%**,明示) | IC +0.155;淨 Sharpe +1.25 vs 0.94;DSR 0.771;n=14 | 未確立(薄);最強候選 |
| 120 | **(a) H82** 條件觸發 | 119(−1%) | 未訓;embargo=82+62=144<252 可訓 | 用戶不接受 +45% 偏差時於 P8 訓+四關+emit |

### 1.3 walk-forward OOS 折校準設計(purge;拍板題 D3 落表)

- **對樣本**=`probability_oos_sample`(§5.2,D3 拍板「落表」:#10 可溯源、`exit_date` 併落=purge 機械斷言依據)。折=revalidate 同一 `walkforward.splits`(#12 零雙軌);逐折 emit(股, rank 分位, 已實現相對標籤, exit_date)。
- **校準輸入=橫斷面 rank 分位**(尺度無關,A-7),**分位方向契約:1=最強、與標籤同向**(入庫 CHECK+§8.2)。
- **expanding + purge**:評估折 i 之校準**僅得 fit 於「標籤窗已完全實現於折 i as-of 之前」之折**(`exit_date < as-of(i)`),**非裸「前折」**(A-3:H120 標籤窗 182td、相鄰折標籤未實現即用=洩漏)。機械斷言=`exit_date` 欄+`purge_verified` 落庫。
- **方法**:主法 **Platt**(2 參數 logistic;折 n 小時 isotonic 過擬合,A-8);pooled 樣本夠大才以 isotonic 對照。品質揭露=逐折 Brier 對基線(base-rate 常數)/ECE(10-bin)/可靠度分箱(含各箱樣本數),**逐折口徑、禁 iid 顯著性宣稱**(A-6/G8)。
- **serve**:最終校準器 fit 於全部 `exit_date ≤ 2026-05-31` 之折,套於 `predict_asof` 全樣本 artifact 之 as-of 分位 → `prediction_probability`(§5.4;同族近似聲明④同帶)。
- **誠實預期(#15)**:校準後機率預期集中 0.5 附近窄帶(薄 edge)——**這是誠實輸出、非失敗**;可靠度分箱單調性破碎之 horizon 標 exploratory。

---

## 2. 需求(2) know-how 端到端一條路(外部窮舉 → PG → 交互理解 → Qdrant → qwen → web UI)

### 2.1 十段 stage 地圖(DB 為總線;上游輸出表=下游輸入表)

| stage | script | DB in → out | resume | 狀態 |
|---|---|---|---|---|
| S1 | `acquire_knowledge.py` / `harvest_knowledge.py` | `knowledge_source`(3,593)→`knowledge_staging`(pending) | harvest_log | BUILT |
| S2 | `promote_knowledge.py` | staging → item/work/thinker/citation(冪等 upsert) | idempotent | BUILT |
| S3 | `fetch_oa_fulltext.py` | item → item_text(三軌 license gate;非授權止於 metadata+`fulltext_blocked`) | build_meta | BUILT |
| S4 | `build_sentences.py` | item_text(CLEAN)→ knowledge_sentence(1.72M) | cursor | BUILT |
| S5 | `build_concordance.py` | sentence → concordance(≈49.8M;**逐字對應理解:定義錨點**) | cursor | BUILT |
| S6 | `build_lexicon.py` | 六源公版辭書 → knowledge_lexicon(154,875;**定義**) | 分段 | BUILT |
| S7 | `build_cross_school_stats.py` | ★**思想相關性/相關係數**★ → term_affinity(2.96M)/group_affinity(npmi/jaccard/llr/tfidf-cosine,method_key FK CHECK 封死=零 AI) | `--phase` 游標 | BUILT(`--domain finance` 擴域零改碼) |
| S8 | `embed_knowledge.py` / `embed_philosophy_chunks.py` | sentence/lexicon → `*_embedding`(e5-small,embedspec 世代) | cursor | BUILT(works/en 1.5M 債列冊,D9) |
| S9 | `export_qdrant_index.py` | pgvector →(CLEAN 閘)→ Qdrant;**段名改 `vector_export`、讀 `knowledge_vectorstore_config` 選匯出器**(A-34;export_milvus_index 退役列冊) | qdrant_sync_state | BUILT/cutover 待 D6 |
| S10 | `serve_chat_ui:8090`→`serve_advisor_openai:8399`→`advise()`→Ollama qwen3:8b | retrieval(vectorstore factory)+concordance/lexicon/**concept_graph(G6 RBAC 收窄後接線,硬先決 A-11)**→guard 五閘→web UI | — | BUILT/接線於 P3 |

「意涵」層=advisor 對真統計數字+逐字原文之即時解讀、**不入庫**(禁 AI 生成入庫);嵌入=索引非內容(紅線③),affinity 庫零向量。

### 2.2 單命令背景鏈 + D7 orchestrator 擴充

全鏈唯一驅動器=`refresh_knowledge_pipeline.py`(D7 拍板:**擴充既有、不另建**)。單命令背景:
`nohup python scripts/refresh_knowledge_pipeline.py --domain finance > logs/refresh_finance.log 2>&1 &`
D7 新增四件:**心跳**(每段 tick 寫 `knowledge_build_meta` scope=`orchestrator/heartbeat`)、**殭屍收斂**(`--reap`:心跳逾時→終止孤兒 process group+清 stale 鎖,A-14)、**單例鎖**(fcntl.flock+DB 心跳雙保險,A-13)、**per-stage 量參數**(`--stage-limit stage=N`,A-15)。CLI 矩陣+I/O 見 §6.9。

### 2.3 端到端煙測(§8.1 暢通不變式之機械判定工具)=`scripts/verify_knowledge_e2e_smoke.py`(新)

流程:(1) INSERT 一列 sentinel 來源(**公版短句+唯一 nonce**,`domain='smoke_test'`;禁 AI 生成文本作 sentinel,A-17)→(2) 驅動器全鏈跑至嵌入 →(3) **正向斷言**:檢索以 nonce 命中、逐字 byte-equal;`--with-llm` 時 advise() 輸出含逐字引用 →(4) **fail-closed 反向斷言**:sentinel 之 `access_scope='local_private'` 對照列**不可**被無授權檢索到 →(5) **語料隔離斷言**:smoke_test 域零列進 term_affinity 正式統計 →(6) `--clean` 拆除。**煙測綠(exit 0)=暢通;破=管線債,修復優先於擴容**(§8.1)。CLI 矩陣+I/O 見 §6.6。

### 2.4 Qdrant 影子評測與 cutover(拍板題 D6)+ fallback 降級

- **範圍**:僅 `sentence_items`(本計畫唯一有意義 scope);**前提**=`augur-qdrant` systemd unit 常駐(A-18)。
- **門檻**:`verify_qdrant_shadow.py` 50 題(確定性取樣 seed=42,A-32)top-10 重疊率 ≥0.90(數字可調),結果落 `vectorstore_shadow_eval`(#10,§5.6)。
- **cutover/退回**=UPDATE `knowledge_vectorstore_config` 一列;**fallback 常備**:讀端偵測 Qdrant 不健康→自動降級 pgvector+印降級事件(A-20);稽核後走 SOP-B 全量重建、不增量改 payload(防陳舊快照繞 CLEAN 閘,A-21)。

---

## 3. 需求(3) 零 Claude token + resume-safe(橫切紀律)

- **零 Claude/雲端 LLM usage**:S1–S9+機率層全為本地 python/SQL;唯 S10 本機 qwen 推理(**v1.37.0 本機推理不在此限**,A-35/§8.1);G3 建構時 assert 最終 url host∈{localhost,127.0.0.1,內網 allowlist}(A-12)。
- **resume 機制矩陣**:S1=harvest_log ｜ S2=冪等 upsert ｜ S3/S4/S5/S8=build_meta 游標/NOT EXISTS ｜ S7=`--phase` 游標 ｜ S9=qdrant_sync_state ｜ 機率層=per-fold/per-(panel,model) DELETE+INSERT 冪等 ｜ 驅動器自身無狀態(殺掉重跑冪等)。
- **背景紀律(#28)**:nohup+log+完成單次通知不輪詢;殭屍收斂+單例鎖(§2.2)保證中斷不留半完成不可逆狀態。

---

## 4. 需求(4) 未來適用 — 四接縫全收斂為資料列/env 一行

### 4.1 新 know-how 來源 = INSERT 一列(#29b)
`knowledge_source` INSERT 一列(adapter+查詢模板)即入鏈,**零 code 變動**;新「來源協定」才寫 adapter、新 entity_type 才加 mapping。煙測 sentinel(§2.3)即此路徑之常備活體證明。re3data 3,524 源維持 disabled、逐域人拍板(D8,能抓≠該抓)。

### 4.2 換向量模型 = embedspec 世代重嵌 SOP-A(D9/D11)
`embedspec.MODEL_DIMS` 登記新 tag+dim → `embed_knowledge --model` 分批重嵌(新世代、舊不覆蓋;collection 名烘世代)→ `verify_qdrant_shadow` 影子門檻 → UPDATE config `embed_model/dims`。**讀端機械斷言 config=embedspec 世代 SSOT,不一致 fail-loud 拒服務**(§8.1)。異維換模(384→1024)儲存策略=D11 拍板題,**未拍板前異維換模不得執行**;works/en 1.5M 嵌入債=GPU 到位後 SOP-A 分批(D9)。

### 4.3 換 qwen(ollama 參數)
- **換模型=env 一行**:`OLLAMA_MODEL`(如 `qwen3:8b`→`qwen3:14b`)+`ollama pull <model>`+`systemctl restart augur-advisor`(#7:http.server 不熱更新,改後必重啟再實測)。
- **推理參數**(temperature/top_p/num_ctx/keep_alive)=`ollama.make_llm_fn` options 單一住所,env 可覆寫;**G3 host allowlist 建構時 assert 不因換模鬆動**(斷言最終 url,非只 base_url(),A-12)。
- **治權零影響**:guard 五閘 fail-closed 於輸出層、模型無關;picks/機率=確定性渲染不經 LLM。**驗收**=`verify_advisor_regression.py --run --with-llm` 全綠。

### 4.4 換向量後端 = config 資料列
`knowledge_vectorstore_config` UPDATE 一列(pgvector↔qdrant_server);cutover 前提+影子門檻+fallback 見 §2.4;退回同樣=UPDATE 一列。索引雙庫鐵則(ANN 只回 id+distance、內容/RBAC 回 PG)引用憲章 v1.23.0 條、不複述(A-33)。

---

## 5. table schema 全集(需求(5) 表側;每張附 DDL)

### 5.1 `knowledge_vectorstore_config`(新;DDL 住 `scripts/migrate_vectorstore_config_ddl.py`,冪等)

```sql
CREATE TABLE IF NOT EXISTS knowledge_vectorstore_config (
  scope        text PRIMARY KEY,                 -- 'sentence_items'/'sentence_works'/'lexicon'/'philosophy_chunk'
  backend      text NOT NULL DEFAULT 'pgvector'
                 CHECK (backend IN ('pgvector','qdrant_embedded','qdrant_server')),
  embed_model  text NOT NULL,                    -- 須=embedspec 世代 SSOT;讀端機械斷言、不一致 fail-loud 拒服務(§8.1)
  dims         int  NOT NULL,                    -- embedspec MODEL_DIMS
  endpoint     text,                             -- qdrant url/path(pgvector 為 NULL)
  fallback     text NOT NULL DEFAULT 'pgvector'
                 CHECK (fallback IN ('pgvector','none')),   -- D6 自動降級目標(常備)
  updated_at   timestamptz NOT NULL DEFAULT now()
);  -- 換後端/退回=UPDATE 一列(#29b);唯一 sanctioned host 由 G3 allowlist 另管
```

### 5.2 `probability_oos_sample`(新;D3「OOS 對樣本落表」,DDL 住 `scripts/migrate_probability_ddl.py`)

```sql
CREATE TABLE IF NOT EXISTS probability_oos_sample (
  horizon           int  NOT NULL CHECK (horizon IN (20,40,60,82,120)),   -- 82=D1(a) 條件觸發保留
  panel_date        date NOT NULL,               -- OOS 折之 as-of 預測時點
  model_family      text NOT NULL,               -- 'RankRidge'(逐折 refit 同族;A-36 聲明④)
  stock_id          text NOT NULL,
  score             double precision NOT NULL,   -- 折內 OOS 分數(溯源用;校準輸入=rank_pctile)
  rank_pctile       double precision NOT NULL CHECK (rank_pctile BETWEEN 0 AND 1),
                                                 -- 分位方向契約:1=最強、與標籤同向(§8.2)
  fwd_ret           double precision NOT NULL,   -- 已實現 forward return(FREEZE 內、非未來 #8)
  peer_median_ret   double precision NOT NULL,   -- 同折橫斷面中位數(#10 可溯源)
  label_beat_median boolean NOT NULL,            -- fwd_ret > peer_median_ret
  exit_date         date NOT NULL,               -- 標籤窗完全實現日=panel_date+h 交易日(purge 機械斷言依據,D3)
  git_sha           text NOT NULL,
  created_at        timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (horizon, panel_date, model_family, stock_id)
);
CREATE INDEX IF NOT EXISTS ix_prob_oos_h_exit ON probability_oos_sample (horizon, exit_date);
```

### 5.3 `probability_calibrator`(新;§8.2 calibrator provenance 承載,同 migrate)

```sql
CREATE TABLE IF NOT EXISTS probability_calibrator (
  calibrator_id    text PRIMARY KEY,             -- 如 'platt_h60_asof2026-05-31_g<git7>'(provenance,§8.2)
  horizon          int  NOT NULL CHECK (horizon IN (20,40,60,82,120)),
  method           text NOT NULL CHECK (method IN ('platt','isotonic')),
  fit_asof         date NOT NULL,                -- fit 評估點(僅用 exit_date < 此點之折)
  n_fit_samples    int  NOT NULL,
  n_fit_folds      int  NOT NULL,                -- 誠實揭露:H120 折 n=14 屬 exploratory
  purge_verified   boolean NOT NULL,             -- 機械斷言:全 fit 樣本 exit_date < fit_asof
  params           jsonb NOT NULL,               -- 係數(platt a,b / isotonic 節點)——可重現(#15)
  brier            double precision,             -- 逐折平均(OOS)
  brier_baseline   double precision,             -- 基線=base-rate 常數(對照;禁 iid 顯著性宣稱)
  ece              double precision,             -- 10-bin ECE
  reliability_bins jsonb,                        -- 可靠度分箱(邊界/預測均值/實現率/各箱樣本數)
  family_note      text NOT NULL,                -- A-36 同族近似聲明固定用語
  git_sha          text NOT NULL,
  created_at       timestamptz NOT NULL DEFAULT now()
);
```

### 5.4 `prediction_probability`(新;D5 機率之 DB 承載,同 migrate)+ picks 呈現契約

```sql
CREATE TABLE IF NOT EXISTS prediction_probability (
  panel_date    date NOT NULL,
  model_id      text NOT NULL REFERENCES model_registry(model_id),
  stock_id      text NOT NULL,
  horizon       int  NOT NULL CHECK (horizon IN (20,40,60,82,120)),
  rank_pctile   double precision NOT NULL CHECK (rank_pctile BETWEEN 0 AND 1),  -- 1=最強(方向契約)
  p_beat_median double precision NOT NULL CHECK (p_beat_median > 0 AND p_beat_median < 1),
                -- 唯一合法口徑:P(勝過同儕中位數|as-of,H)(§8.2;禁絕對漲跌機率)
  calibrator_id text NOT NULL REFERENCES probability_calibrator(calibrator_id), -- provenance 入庫(§8.2)
  econ_verdict  text NOT NULL CHECK (econ_verdict IN ('dead','thin_unestablished','established')),
                -- D2 硬綁:判死標籤與機率同列不可分離
  calendar_days int  NOT NULL,                   -- 日曆日近似(20→29/40→58/60→87/82→119/120→174),呈現偏差之推導 SSOT(A-27)
  created_at    timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (panel_date, model_id, stock_id)
);
CREATE INDEX IF NOT EXISTS ix_pred_prob_panel_h ON prediction_probability (panel_date, horizon);
-- 隔離:僅 advisor 唯讀;PIPELINE 7 pkg 零回讀、augur_predict role 不授 SELECT(A-28,預測輸出不自迴圈)
```

**picks「表」呈現契約(D5)**:picks **非 DB 表**=advisor 呈現層(`PredictionPayload.picks` → `_render_picks_table` 確定性渲染),**故無 ALTER;DB 承載=上表 `prediction_probability`**。呈現欄位契約(逐值等同 DB=回歸斷言):

| 欄 | 來源 | 內容 |
|---|---|---|
| 主欄 **H60** | prediction_values(部署 horizon) | rank/score(≈87 cal 標籤) |
| 附欄 **P30** | prediction_probability H20 | p+「≈29 天(−3%)」+**判死 'dead' 硬綁** |
| 附欄 **P60** | prediction_probability H40 | p+「≈58 天(−3%)」+薄標籤 |
| 附欄 **P120** | prediction_probability H120(或 H82 觸發後) | p+「≈174 天(**+45%** 偏差)」/「≈119 天(−1%)」+薄標籤 |
| 尾段 | §1.1 | 四項誠實標記固定用語 |

`StockPick` 擴選填機率欄、`payload.numbers()` 納機率值(guard 白名單);horizon 封閉集={20,40,60,(82),120}。

### 5.5 `prediction_values`(既有;D4 in_portfolio 語意修法+重跑重寫——schema 對應段)

```sql
-- 既有表現況(information_schema 實查,不改欄):
-- prediction_values(
--   panel_date   date    NOT NULL,
--   model_id     text    NOT NULL,
--   stock_id     text    NOT NULL,
--   score        float8  NOT NULL,
--   rank         int     NOT NULL,
--   in_portfolio boolean NOT NULL DEFAULT false,
--   weight       float8  NOT NULL DEFAULT 0.0,
--   PRIMARY KEY (panel_date, model_id, stock_id));  -- + ix_pred_panel_model
```

**D4 語意修法**:現況 H60 部署列 in_portfolio=true、H20/H40/H120 全 false(「候選」不可讀,A-9)。修法=in_portfolio 語意統一為「**該 horizon top-frac 候選組合成員**」(非「已部署」;部署事實由 payload `_DEPLOY_HORIZON` 讀 registry 獨立承載)。**重寫程式規劃**:載具=`predict_asof.py --candidate --rewrite-all`(§6.4),對四 horizon 既有列 per-(panel_date,model_id) DELETE+INSERT 冪等重寫(投組建構複用 `portfolio.build_long_portfolio`,#12 零雙軌)。**驗收 SQL**:每 (panel_date,model_id) 之 in_portfolio 數=top_frac×宇宙之 **floor**(P2 實測修正 2026-07-10:共用 fn `portfolio.build_long_portfolio` 為 int 截斷語意,344×0.1→34;#12 共用 fn 為權威,原 ⌈⌉ 式差 1)、Σweight=1、rank 連續無洞。

### 5.6 `vectorstore_shadow_eval`(新;D6 影子評測落表,住 `migrate_vectorstore_config_ddl.py`)

```sql
CREATE TABLE IF NOT EXISTS vectorstore_shadow_eval (
  run_at        timestamptz NOT NULL DEFAULT now(),
  scope         text NOT NULL,                  -- 'sentence_items'(D6 唯一有意義 scope)
  backend_ref   text NOT NULL,                  -- 參照端(pgvector)
  backend_cand  text NOT NULL,                  -- 候選端(qdrant_server)
  n_queries     int  NOT NULL,                  -- 預設 50
  top_k         int  NOT NULL,                  -- 預設 10
  mean_overlap  double precision NOT NULL,
  min_overlap   double precision NOT NULL,
  threshold     double precision NOT NULL,      -- 預設 0.90(D6,數字可調)
  passed        boolean NOT NULL,               -- mean_overlap >= threshold(cutover 機械門檻)
  detail        jsonb NOT NULL,                 -- 逐題 overlap+題集 seed/雜湊(可重現 #10,A-32)
  PRIMARY KEY (run_at, scope)
);
```

### 5.7 既有表觸及矩陣(不改 schema)

`model_registry`(讀;H20/H40 列已在)· `revalidation_ledger`/`trial_ledger`(讀;econ_verdict 判定來源)· `feature_values`/`core_universe_asof`(讀,#8 as-of)· knowledge 全鏈表(§2.1;S1–S9 各自寫入既有)· `knowledge_build_meta`(驅動器心跳/游標)· `qdrant_sync_state`(S9 帳本)· `app_user`/`group_domain_grant`(RBAC,G6 讀之)。

---

## 6. python 程式規畫(需求(5) 程式側;每支=用途+CLI 指令矩陣+輸入輸出;全支 `import _bootstrap`,#29a)

### 6.1 `scripts/migrate_probability_ddl.py`(新)
**用途**:冪等建 §5.2/5.3/5.4 三表(IF NOT EXISTS+CHECK/FK)。
```
python scripts/migrate_probability_ddl.py            # 無參數:印本矩陣+三表現況(唯讀)
python scripts/migrate_probability_ddl.py --run      # 冪等建三表
python scripts/migrate_probability_ddl.py --verify   # 斷言三表+CHECK/FK 就位(exit 0/1)
```
**輸入→輸出**:— → probability_oos_sample/probability_calibrator/prediction_probability。

### 6.2 `scripts/build_probability_oos_sample.py`(新;P2)
**用途**:對每 horizon 以 revalidate 同一 walk-forward 折(#12)逐折 refit 同族模型、emit OOS 對樣本(分位/已實現相對標籤/exit_date)落表。
```
python scripts/build_probability_oos_sample.py                        # 無參數:各 horizon 折覆蓋矩陣(唯讀)
python scripts/build_probability_oos_sample.py --run --horizon 60     # 單 horizon(冪等 per-fold DELETE+INSERT)
python scripts/build_probability_oos_sample.py --run --all            # 封閉集 {20,40,60,120}
python scripts/build_probability_oos_sample.py --run --horizon 60 --limit-folds 2   # 最小驗證(#25)
python scripts/build_probability_oos_sample.py --verify               # purge 斷言:exit_date 全非 NULL 且=panel_date+h td
```
**輸入→輸出**:feature_values/core_universe_asof/label(on-the-fly)/walkforward.splits → probability_oos_sample。

### 6.3 `scripts/calibrate_relative_probability.py`(新;P6 校準器 fit/serve)
**用途**:§1.3 校準器——`--fit`=expanding purge fit(品質指標同落);`--emit`=套最終校準器於 as-of 分位出機率。
```
python scripts/calibrate_relative_probability.py                       # 無參數:各 horizon 校準現況矩陣(唯讀)
python scripts/calibrate_relative_probability.py --fit --horizon 60    # purge fit → probability_calibrator
python scripts/calibrate_relative_probability.py --fit --all           # {20,40,60,120} 全 fit
python scripts/calibrate_relative_probability.py --emit --horizon 60 --asof 2026-05-31  # → prediction_probability
python scripts/calibrate_relative_probability.py --report              # 可靠度報告(逐折 Brier/ECE/分箱)→ stdout+reports/
```
**輸入→輸出**:probability_oos_sample+prediction_values+model_registry+revalidation_ledger(econ_verdict 來源)→ probability_calibrator+prediction_probability(+reports/)。

### 6.4 `scripts/predict_asof.py`(改;D4 `--candidate` 重跑載具)
**用途**:既有 as-of 出單 CLI 加 `--candidate`:以「候選組合成員」語意寫 in_portfolio/weight;`--rewrite-all`=D4 全量重寫。
```
python scripts/predict_asof.py                                                    # 既有:印矩陣(不預測)
python scripts/predict_asof.py --run --horizon 40 --asof 2026-05-31 --candidate   # 候選語意單 horizon 重跑
python scripts/predict_asof.py --candidate --rewrite-all --asof 2026-05-31        # 四 horizon 既有列冪等重寫(per (panel_date,model_id) DELETE+INSERT)
```
**輸入→輸出**:model_registry/feature_values/core_universe_asof → prediction_values(語意修法後)。驗收 SQL 見 §5.5。

### 6.5 `scripts/verify_advisor_regression.py`(新;P5 交付=P6 之驗收工具,依賴倒置已解)
**用途**:顧問回歸驗證器——金題集過 advise() 全鏈,機械斷言:picks 渲染=DB ground truth 逐值等同、機率∈`payload.numbers()`、§1.1 四誠實標記在場、`_FUTURE_LEAK` 反斷言、判死 horizon 帶 'dead'、引文逐字、guard 五閘全過。
```
python scripts/verify_advisor_regression.py                     # 無參數:印矩陣+金題集現況(唯讀)
python scripts/verify_advisor_regression.py --run --no-llm      # 結構模式:payload/渲染/標記/guard 靜態斷言(CI 可重現,A-30)
python scripts/verify_advisor_regression.py --run --with-llm    # 全鏈模式:經 ollama 生成後過 guard(需 augur-advisor 健在;改碼後 #7 先重啟)
python scripts/verify_advisor_regression.py --run --json        # 機器可讀(exit 0=全過,A-31)
python scripts/verify_advisor_regression.py --baseline record   # 錄基線 → tests/advisor_golden/(傳輸工件、非來源 SSOT)
```
**輸入→輸出**:金題集(tests/advisor_golden_questions.json)+prediction_values/prediction_probability/model_registry/knowledge_* → stdout PASS/FAIL 矩陣+exit code(+reports/ 選配)。

### 6.6 `scripts/verify_knowledge_e2e_smoke.py`(新;§2.3/§8.1 端到端煙測)
**用途**:暢通不變式機械判定——sentinel 一列入鏈→逐字命中+fail-closed 反向斷言+語料隔離斷言→拆除。
```
python scripts/verify_knowledge_e2e_smoke.py                    # 無參數:印矩陣+上次煙測狀態(唯讀)
python scripts/verify_knowledge_e2e_smoke.py --run              # 全鏈:INSERT sentinel→refresh(domain=smoke_test)→三斷言→--clean
python scripts/verify_knowledge_e2e_smoke.py --run --with-llm   # 加末段:advise() 對 nonce 提問、輸出含逐字引用
python scripts/verify_knowledge_e2e_smoke.py --run --keep       # 保留 sentinel 除錯(後續手動 --clean)
python scripts/verify_knowledge_e2e_smoke.py --clean            # 拆除 smoke_test 域全部列(冪等)
python scripts/verify_knowledge_e2e_smoke.py --run --json       # 機器可讀(exit 0=綠=暢通)
```
**輸入→輸出**:自造 sentinel(公版短句+nonce)→ 觸 knowledge_source/staging/item/item_text/sentence/concordance/*_embedding(domain='smoke_test' 隔離)→ exit 0/≠0(+--json)。

### 6.7 `scripts/verify_qdrant_shadow.py`(新;D6 影子評測)
**用途**:pgvector(參照)vs Qdrant(候選)同題 top-k 重疊率評測,cutover 機械門檻。
```
python scripts/verify_qdrant_shadow.py                          # 無參數:印矩陣+config/兩後端現況(唯讀)
python scripts/verify_qdrant_shadow.py --run                    # 預設:scope=sentence_items n=50 topk=10 threshold=0.90 seed=42
python scripts/verify_qdrant_shadow.py --run --n 50 --topk 10 --threshold 0.90 --seed 42
python scripts/verify_qdrant_shadow.py --run --questions <file> # 自訂題集(傳輸工件)
```
**輸入→輸出**:knowledge_vectorstore_config+*_embedding(pgvector)+Qdrant+確定性取樣題集 → vectorstore_shadow_eval 一列(#10)+stdout 逐題 overlap+exit 0(mean≥threshold)/1。

### 6.8 `scripts/migrate_vectorstore_config_ddl.py`(新)
**用途**:冪等建 §5.1/§5.6 兩表+種子 scope 列(backend='pgvector')。
```
python scripts/migrate_vectorstore_config_ddl.py            # 無參數:印矩陣+表現況(唯讀)
python scripts/migrate_vectorstore_config_ddl.py --run      # 冪等建表+種子列
python scripts/migrate_vectorstore_config_ddl.py --verify   # 斷言 config.embed_model=embedspec 世代(不一致 exit 1=fail-loud)
```
**輸入→輸出**:embedspec(世代 SSOT)→ knowledge_vectorstore_config+vectorstore_shadow_eval。

### 6.9 `scripts/refresh_knowledge_pipeline.py`(擴充;D7)
**用途**:知識域端到端唯一驅動器(只編排不計算、無狀態冪等)——D7 加心跳/殭屍收斂/單例鎖/per-stage 量參數;段序 `milvus_export`→`vector_export`(讀 config 選匯出器,A-34)。
```
python scripts/refresh_knowledge_pipeline.py                             # 各段待辦計數矩陣(唯讀純 SQL)
python scripts/refresh_knowledge_pipeline.py --status                    # D7 新:心跳/單例鎖/上次段位/殭屍偵測(唯讀)
python scripts/refresh_knowledge_pipeline.py --domain finance            # 全鏈實跑(自動 flock 單例鎖+每段心跳)
python scripts/refresh_knowledge_pipeline.py --domain finance --stage-limit embed=5000 --stage-limit stats=20000  # D7 新:per-stage 量
python scripts/refresh_knowledge_pipeline.py --from-stage sentences --until embed --limit 1000
python scripts/refresh_knowledge_pipeline.py --reap                      # D7 新:殭屍收斂(心跳逾時→終止孤兒 process group+清 stale 鎖)
nohup python scripts/refresh_knowledge_pipeline.py --domain finance > logs/refresh_finance.log 2>&1 &   # 單命令背景(需求(2)/(3))
```
**輸入→輸出**:STAGES 常數表+DB 待辦純 SQL → 自身只寫心跳/鎖(knowledge_build_meta scope='orchestrator/*');實質資料由各子 CLI 落表。殭屍判準=心跳齡>2×段預期 或 pid 不存活;雙實例並跑=第二實例 flock 失敗即退(exit≠0)。

### 6.10 既有工具沿用矩陣(參數即擴充,零新 code)
`train_ranker.py --horizon {20,40,82} --run` · `revalidate.py --run`(B/CD_HORIZONS 常數已含 20/40)· `deflate_headline_verdict.py --horizon N` · `report_short_horizon_verdict.py` · `build_cross_school_stats.py --domain finance` · `embed_knowledge.py` · `export_qdrant_index.py` · `harvest_knowledge.py`/`promote_knowledge.py`/`fetch_oa_fulltext.py`/`build_sentences.py`/`build_concordance.py`/`build_lexicon.py` · `serve_{chat_ui,advisor_openai,admin_console}.py`(改碼後 #7 重啟)。

### 6.11 分階段 P1–P8(驗收+拍板點;每階段完成逐段呈用戶過目 #19)

> **執行狀態(2026-07-10 晚,commit 24e87a3)**:P1 ✅(兩 migrate 綠+G3 焊+隔離綠)| P2 ✅(42,456 列 OOS+D4 重寫,verify 綠)| P3 ◕ 3/4(G6/W2/D7 done;缺 §6.6 煙測)| P5 ✅(回歸器 exit 0)| P6 ✅(4 校準器 purge_verified+1,376 機率+picks 附欄四標記硬綁)| P4/P7/P8 未動。

| P | 內容 | 驗收(機械) | 依賴/拍板 |
|---|---|---|---|
| **P1** | DDL+閘先行:§6.1/§6.8 migrate --run;import_isolation 複驗;G3/G6 焊點複驗 | 兩 migrate `--verify` 綠;`check_isolation()==[]` | D0 簽核後動工 |
| **P2** | 預測側承載:①§6.2 emit(H60 先行→全集)②同族近似聲明④固定用語定稿 ③§6.4 `--candidate --rewrite-all`(D4) | §6.2 `--verify` purge 斷言綠;§5.5 驗收 SQL 綠;**H60 emit 完成=P6 讀端前提** | D1/D2/D3/D4 |
| **P3** | know-how 側:D7 驅動器擴充+§6.6 煙測交付首跑;concept_graph 接線(**G6 收窄=硬先決**,A-11) | 煙測 exit 0(正向+反向+隔離);`--status` 心跳/鎖可見 | D7/D8 |
| **P4** | Qdrant:augur-qdrant systemd unit→export→§6.7 影子 ≥0.90→config UPDATE cutover(僅 sentence_items)+fallback 降級演練 | shadow_eval passed=true 落表;停 qdrant→自動降級 pgvector 實測 | D6;**依賴 systemd unit 就位** |
| **P5** | §6.5 `verify_advisor_regression.py` 交付+基線錄製(尚無機率欄=基線版) | `--run --no-llm`/`--with-llm` exit 0 | — |
| **P6** | 機率層合流(**最後做**,D5):§6.3 fit/emit→StockPick 擴欄→確定性渲染 picks(H60 主欄+P30/P60/P120 附欄+四標記硬綁)→回歸加機率斷言 | 渲染=DB 逐值等同;四標記在場;guard 白名單含機率;§6.5 全綠 | D5;依賴 P2(H60 emit)+P5(工具) |
| **P7**(常備) | 運維常綠:煙測+回歸+影子評測納 daily_maintenance/背景排程;管線債冊(works/en);降級監測 | 三驗證器 exit 0 常綠 | — |
| **P8**(條件觸發) | H82 訓練+四關+emit(D1a)/works-en SOP-A 分批(D9)/異維換模(D11) | 各自四關/影子門檻 | D1(a)/D9/D11 拍板後 |

---

## 7. 對抗審查發現表(四鏡:治權/誠實/工程/經濟;CLAUDE #20 高風險留痕)

| # | 鏡 | 級 | 發現 | 修正落點 | 狀態 |
|---|---|---|---|---|---|
| A-1 | 治權 | blocker | 需求原文「30/60/120 天股價走向機率」照字面做=絕對漲跌機率假兆、違靈魂紅線 | §1.0 轉譯為橫斷面相對機率+D0 拍板明示 | 已修 |
| A-2 | 治權 | blocker | know-how 若進機率/預測任何數字通道=破 #8 隔離 | 機率層只用半-1 輸出;know-how 僅進 advisor 引文通道;雙閘判準零觸碰 | 已修 |
| A-3 | 誠實 | blocker | 校準器 fit 於裸「前折」=標籤窗未實現即用=洩漏(H120 窗 182td) | §1.3 purge:僅 fit 於 exit_date<評估折 as-of;exit_date 落表機械斷言(D3) | 已修 |
| A-4 | 經濟 | major | H20 經濟判死(淨 Sharpe +0.27<基準 +0.30)卻照出 P30=誤導 | D2:照出+econ_verdict='dead' 與機率同列硬綁(§5.4 CHECK) | 已修 |
| A-5 | 誠實 | major | 「120 天」對映 H120 實為 ~174 cal(+45% 偏差);H82(~119)精確但未訓 | D1:(b) H120+偏差明示為主;(a) H82 條件觸發 P8 | 已修 |
| A-6 | 誠實 | major | 機率顯著性若用 iid 檢定=重疊窗高估(G8 舊病) | §1.3 逐折 Brier/ECE 口徑、禁 iid 顯著性宣稱;§8.2 明文 | 已修 |
| A-7 | 工程 | major | raw score 尺度跨折漂移→餵校準器不穩 | §1.3 校準輸入=橫斷面 rank 分位(尺度無關);方向契約 1=最強入庫 CHECK | 已修 |
| A-8 | 誠實 | major | isotonic 於折 n 小(H120 n=14)過擬合 | §1.3 主法 Platt;pooled 夠大才 isotonic 對照;n 逐折揭露 | 已修 |
| A-9 | 工程 | major | in_portfolio 語意混雜(H60 true=部署、其餘全 false)=「候選」不可讀 | D4 語意統一「top-frac 候選成員」+§6.4 --candidate 重跑重寫+§5.5 驗收 SQL | 已修 |
| A-10 | 治權 | major | 機率若經 LLM 轉述=白名單外幻覺風險 | D5 確定性渲染(payload ground-truth 注入)+機率納 payload.numbers() | 已修 |
| A-11 | 治權 | blocker | concept_graph.cooccurrence_evidence 零 RBAC 收窄接入 advise()=owned_local 逐字洩漏(承 0709 F1) | G6 clean_item_sql 收窄=接線硬先決(P3) | 已修 |
| A-12 | 治權 | major | make_llm_fn `base=` 參數繞過 base_url() host 閘(承 0709 F2) | G3 assert 最終 url host∈allowlist;§4.3 換 qwen 不鬆動 | 已修 |
| A-13 | 工程 | major | 驅動器無單例鎖:雙實例並跑=游標競態/重複工作 | D7 flock 單例鎖+DB 心跳雙保險(§6.9) | 已修 |
| A-14 | 工程 | major | 驅動器被殺後子行程殘留=殭屍續寫 DB、鎖殘留 | D7 心跳+--reap 殭屍收斂(process group 終止+stale 鎖清除) | 已修 |
| A-15 | 工程 | minor | 放量無 per-stage 粒度(--limit 一刀切) | D7 --stage-limit stage=N 重複旗標 | 已修 |
| A-16 | 工程 | major | 煙測只驗正向可檢索=假綠燈(fail-closed 面不驗) | §2.3 反向斷言(local_private 不可檢索)+語料隔離斷言 | 已修 |
| A-17 | 誠實 | major | 煙測 sentinel 殘留正式庫=測試/AI 生成資料污染入庫 | §2.3 sentinel=公版短句+nonce、domain='smoke_test' 隔離、--clean 拆除;禁 AI 生成文本 | 已修 |
| A-18 | 工程 | major | Qdrant cutover 無 server 常駐前提=embedded 單行程鎖死 serving | D6:augur-qdrant systemd unit 為前提;P4 依賴之 | 已修 |
| A-19 | 工程 | major | cutover 無影子門檻=品質回退不可知 | D6:50 題 top-10 ≥0.90 機械門檻+vectorstore_shadow_eval 落表(#10) | 已修 |
| A-20 | 工程 | major | Qdrant 掛掉無 fallback=對話層停擺 | §2.4 讀端自動降級 pgvector(config.fallback)+降級事件 log+演練驗收 | 已修 |
| A-21 | 治權 | major | Qdrant payload 陳舊快照可繞 CLEAN 閘(稽核後仍檢索到) | SOP-B 重建非增量改;RBAC 留 PG;僅 sentence_items scope | 已修 |
| A-22 | 誠實 | minor | 換向量模型若覆蓋舊 collection=世代混嵌不可比 | §4.2 SOP-A:新世代新表、collection 名烘世代、舊不覆蓋;讀端 embedspec 斷言 | 已修 |
| A-23 | 工程 | minor | 異維換模(384→1024)pgvector 欄型別鎖死 | D11 拍板題;未拍板前異維換模不得執行(SOP-A ② 明文) | 已修 |
| A-24 | 治權 | minor | re3data 3,524 源隨「暢通」自動啟用=能抓≠該抓破功 | D8:維持 disabled、逐域人拍板 | 已修 |
| A-25 | 誠實 | minor | school 層語料空集→該粒度統計輸出空而不 fail | D10 三選一列點、不默認可得 | 已修 |
| A-26 | 誠實 | major | 機率呈現不帶折數 n=薄樣本假精確(H120 n=14) | §1.1 標記①含逐折 n;可靠度分箱各箱樣本數同列 | 已修 |
| A-27 | 工程 | minor | 30/60/120 日曆日陳述散落各處易漂移 | §1.2 對映表=SSOT;calendar_days 欄由 horizon 常數推導非手寫 | 已修 |
| A-28 | 治權 | major | 機率若回流 feature/因子鏈=預測輸出自迴圈污染 | prediction_probability 僅 advisor 唯讀;PIPELINE 零回讀、augur_predict 不授 SELECT(§5.4) | 已修 |
| A-29 | 誠實 | major | FREEZE 下機率只到 as-of 2026-05-31,不明示=誤為即時 | §1.1 標記①硬綁 as-of 日期;payload.as_of 承載 | 已修 |
| A-30 | 工程 | minor | 回歸驗證依賴 live ollama=CI 不可重現 | §6.5 --no-llm 結構模式與 --with-llm 全鏈模式分離 | 已修 |
| A-31 | 工程 | minor | 煙測/回歸無固定 exit code 契約=無法機械判定 | §2.3/§6.5:exit 0=綠、≠0=紅、--json 機器可讀 | 已修 |
| A-32 | 誠實 | minor | 影子題集每次隨機=門檻不可重現 | §6.7 --seed 固定取樣+題集雜湊入 detail jsonb | 已修 |
| A-33 | 治權 | minor | 入憲草文若複述雙庫鐵則/接縫層=雙 SSOT 漂移 | §8.1 採引用不複述(SSOT #12) | 已修 |
| A-34 | 工程 | minor | 驅動器段序殘留 milvus_export=與 Qdrant 路線矛盾 | §2.1/§6.9 段改 vector_export、讀 config 選匯出器;export_milvus_index 退役列冊 | 已修 |
| A-35 | 治權 | major | 暢通不變式若寫死「全段×全 scope 恆綠+零 LLM usage」:S10 本機 qwen 推理即 LLM usage、已知嵌入債(works/en 1.5M cursor=0 等)於採納當下即違反 | §8.1 改「零 Claude/雲端 LLM usage(本機推理不在此限,承 v1.37.0)」;不變式範圍限定「已啟用之段×scope 矩陣」,已知債列冊為管線債、以煙測綠燈為暢通判準 | 已修 |
| A-36 | 治權 | minor | P6 校準器適用性未揭露:fit 於逐折 refit 模型、serve 套於 train_ranker 全樣本 artifact——同 family 非同一模型,近似假設不得只講「分位尺度不變」 | §1.1 誠實標記④「同族近似聲明」+P2 規格②+P6 caveat 固定用語同帶 | 已修 |

---

## 8. 入憲草案:憲章 v1.40.0

### 8.1 新條文一:端到端知識素養管線暢通不變式(第三部 philosophy 層,**以增補子彈附掛於 v1.23.0「知識域端到端管線(七段一驅)」條**——既有「索引雙庫鐵則」(ANN 只回 id+distance、內容與 RBAC 一律回 PostgreSQL)與「可替換=接縫層」規定**採引用不複述**(SSOT #12:一概念一權威家);段鏈以七段正典為準,全文擷取(fulltext)歸屬「晉升落地」段之延伸、加註不另立段)

> **端到端知識素養管線暢通不變式〔v1.40.0,v1.23.0 條之增補〕**:七段一驅之管線於**已啟用之段×scope 矩陣**內,須恆常保持「**單命令可驅、零 Claude/雲端 LLM usage(本機推理不在此限,承 v1.37.0)、DB-driven resume-safe**」之暢通狀態;暢通與否以**端到端煙測**(新來源 INSERT 一列→對話逐字引用,含 fail-closed 反向斷言與語料隔離斷言)**機械判定**——煙測綠=暢通;煙測破=管線債,修復優先於擴容;已知未啟用範圍(如 works/en 嵌入債)列冊為管線債、不構成破。新增來源=資料列、新增段=編排常數列。向量索引後端之**切換機制=`knowledge_vectorstore_config` 資料列**(接縫層之 DB 化——後端實作與讀路遵本條既有「可替換=接縫層」與「索引雙庫鐵則」規定,不另立判準),切換與退回皆為 UPDATE 一列,且讀端須機械斷言 config 之 embed_model 與 code 世代 SSOT(embedspec)一致、不一致即 fail-loud 拒服務。

### 8.2 新條文二:相對機率誠實判準(第三部 validate 層)

> **相對機率誠實判準〔v1.40.0〕**:系統對個股未來走向之機率輸出,**唯一合法口徑=橫斷面相對機率** P(勝過同儕中位數 | as-of, horizon),以 walk-forward OOS 折之(橫斷面分位,已實現標籤)對樣本作 expanding 校準——**校準器僅得 fit 於「標籤窗已完全實現於評估折 as-of 之前」之折(purge),非裸「前折」**——並隨數字揭露可靠度(Brier 對基線/ECE/可靠度分箱,逐折口徑,禁 iid 顯著性宣稱)。**禁止輸出或暗示絕對漲跌機率**(「N 天會漲的機率」=假兆)。橫斷面口徑聲明、日曆日↔交易日對映偏差、經濟判死標籤、模型同族近似聲明須與機率數字**硬綁呈現**,不得只出數字;分位方向契約(1=最強,與標籤同向)與校準器 provenance(calibrator_id)入庫可溯源。第一部產物列「分數/機率+可信度」同步明確化為此口徑。

### 8.3 修訂歷程列草文(體例:3 行封頂;前列 v1.39.0 改 SUPERSEDED;檔名 rename)

| 版本 | 日期 | 修訂說明 | 狀態 |
|---|---|---|---|
| v1.40.0 | 2026-07-10 | 架構不變式+判準新增:第三部 philosophy 層 v1.23.0 條增補「端到端知識素養管線暢通不變式」(已啟用段×scope 矩陣單命令可驅/零 Claude/雲端 LLM usage/resume-safe/煙測機械驗收/向量後端 config 資料列切換+世代一致性斷言;既有雙庫鐵則與接縫層規定引用不複述);第三部 validate 層新增「相對機率誠實判準」(橫斷面相對機率唯一合法口徑、purge 校準、禁絕對漲跌機率、四項誠實標記硬綁、方向契約與 provenance 可溯源)。動因=全能全知端到端主計畫 v3 定稿(reports/augur_omniscient_e2e_master_plan_20260710.md)四鏡對抗審查後人拍板。同步:原則精華對憲章版本交叉引用、README 版本+連結、檔名 v1.39.0→v1.40.0、第一部產物列口徑明確化。 | ACTIVE |
| v1.39.0 | (原日期) | (原文不動) | **SUPERSEDED** |

---

## 9. 硬體平台雙軌設計(GPU / CPU-only)〔用戶 directive 2026-07-10;主 session 實測為據〕

### 9.1 本機實測事實(#9/#10 可溯源:`/usr/lib/wsl/lib/nvidia-smi` + powershell Win32_* 實查 2026-07-10)

| 項 | 實測值 |
|---|---|
| GPU | NVIDIA GTX 1650 **4GB VRAM**(WSL2 直通;`nvidia-smi` 不在 PATH,須 `/usr/lib/wsl/lib/nvidia-smi`)、CUDA 12.6 |
| CPU/RAM | Ryzen 5 3600(6C12T)/ 主機 32GB(WSL2 配額 16GB) |
| 既知瓶頸 | qwen3:8b Q4(>4GB)裝不進 VRAM → ollama 部分層落 CPU → **3-6 分/回**(S10 唯一重 GPU 段) |

### 9.2 段別硬體敏感度矩陣(全鏈僅 S10 重 GPU;CPU-only 平台**功能不縮、只慢**)

| 段 | 硬體敏感度 | CPU-only 影響 |
|---|---|---|
| S1–S3(acquire/promote/fulltext)、S5–S7(concordance/lexicon/**cross_school 相關係數**) | 純 CPU+I/O | 無差 |
| S4(sentences)、機率層(§1 校準/Ridge/LGBM)、Qdrant(HNSW) | CPU/RAM | 無差 |
| S8(embed,e5-small ~130MB) | GPU 可加速、CPU 可跑 | batch 調小、時間 ×3-8 |
| **S10(qwen 推理)** | **GPU 敏感(唯一)** | 依 9.4 tier 換檔,功能不縮 |

### 9.3 自動偵測(掛 D7 驅動器,不另建程式)

`refresh_knowledge_pipeline.py` 開跑先 probe:`nvidia-smi`(PATH→`/usr/lib/wsl/lib/` 兩路徑)+ `ollama ps` PROCESSOR 欄 → 硬體 profile 寫 `knowledge_build_meta`(scope=`orchestrator/hw_profile`,沿用 §6.9 心跳同表;**零新表**)→ 依 tier 自動調參:S8 embed batch、`OLLAMA num_gpu`;煙測 `--with-llm` 於 CPU-only 檔自動放寬 timeout。

### 9.4 qwen tier 推薦表(與 §4 換 qwen 接縫整合:換檔=env 一行+重啟 #7 + `verify_advisor_regression`)

| tier | 推薦 | 效果 |
|---|---|---|
| CPU-only | qwen3:4b(可用性優先) | 全功能,回覆分鐘級 |
| **4GB(本機現況)** | **8b 部分卸載(質優,3-6 分)或 4b 全 GPU(速優,數十秒)雙檔並存,env 切換** | 拍板題 D12 |
| ≥8GB | 8b 全 GPU | 秒-分鐘級 |
| ≥12GB | 可上 14b+ | 質速兼得 |

### 9.5 驗收時間預算(兩檔分列;數字為估計、實跑後依 #27 回填)

端到端煙測(§2.3):GPU 檔 ≤15 分/CPU-only 檔 ≤45 分;`--with-llm` 單輪:GPU(4b)≤2 分/現況(8b 部分卸載)≤8 分/CPU-only ≤15 分。逾時=FAIL 查因,不放寬標準遷就。

---

## 附:拍板題總表(執行前用戶逐題簽核)

> **✅ 拍板記錄:2026-07-10 用戶簽核「D0-D12 依建議簽核」**——全數依「建議」欄通過(D10 依其建議=屆時三選一列點不默認、D11 依其建議=遇異維換模時再拍板)。實作自 P1 起動工,每階段完成逐段呈過目(#19)。

| # | 題 | 建議 |
|---|---|---|
| D0 | 「機率」=橫斷面相對機率之轉譯簽核(紅線;含四項誠實標記硬綁) | 准(靈魂相容之唯一路) |
| D1 | 120 天對映三選一 | (b) H120+偏差明示;(a) H82 條件觸發 |
| D2 | H20(30 天)機率照出與否 | 照出+econ_verdict='dead' 硬綁 |
| D3 | OOS 對樣本落表 vs 即時重生 | 落表(#10 可溯源;exit_date 併落=purge 機械斷言依據) |
| D4 | in_portfolio 語意修法(--candidate+重跑重寫) | 准 |
| D5 | 機率進 advisor payload/呈現 | P6 最後做;確定性渲染;picks 表 H60 主欄+P30/P60/P120 附欄(各帶日曆日標籤+偏差+判死) |
| D6 | Qdrant cutover 時點/門檻 | **僅 sentence_items(本計畫唯一有意義 scope);qdrant_server 常駐為前提**;影子門檻 50 題 top-10 ≥0.90(數字可調);fallback+自動降級常備 |
| D7 | orchestrator 形態 | 擴 refresh_knowledge_pipeline(不另建);心跳/殭屍收斂/單例鎖/per-stage 量參數一併入 |
| D8 | re3data 3,524 源啟用範圍 | 維持 disabled、逐域人拍板(能抓≠該抓) |
| D9 | works/en 1.5M 嵌入債時點 | GPU 到位後以 SOP-A 載具分批;②′成本估算為拍板材料 |
| D10 | school 層語料空集補救 | 三選一列點、不默認可得 |
| D11 | 異維換模儲存策略(新世代表 vs 無型別 vector 欄+per-tag expression index) | 遇異維換模時拍板;未拍板前異維換模不得執行(SOP-A ② 明文) |
| D12 | S10 對話模型檔位(§9.4,現況 4GB) | 雙檔並存:8b 部分卸載(質)為預設、4b 全 GPU(速)為快檔,env 一行切換+回歸測試 |

**執行順序與依賴**:P1 →(P2 ∥ P3)→ P4 → P5 → P6 → P7(常備)→ P8(條件觸發)。依賴要點:P6 之驗收工具 `verify_advisor_regression.py` 於 **P5 交付**(依賴倒置已解);P6 讀端依賴 **P2 對 H60 之 emit 完成**(horizon 封閉集保證);P4 serving cutover 依賴 augur-qdrant systemd unit 就位;每階段完成=逐段呈用戶過目(#19),拍板題未簽核之階段不動工(plan-first 執行前四判準確認後開跑)。