# know-how 全通管線升級計畫(K 計畫;2026-07-12 草案・待拍板)

> **性質**:計畫先行(憲章第六部 v1.39.0)。用戶指示(2026-07-12):外部股票投資 know-how →本地
> PostgreSQL→「raw data 逐字逐句交互對應理解(定義/意涵/思想相關性/相關係數)」→Qdrant→qwen→Web UI,
> 全本地背景跑、最少 token、每支可端到端串接、換料換模皆適用,一條路打通;並「重新驗證是否完美產生
> 對應 table schema 與 python 程式計畫」。本計畫以 **4-agent 平行實證理解**(每項 claim 附檔:行/DB 證據)
> 為地基,只規畫真缺口、不重複建設。

## §0 用戶規格之 Claude 最佳語意(=你問的「怎麼講最準」;拍板即成為本計畫的規格 SSOT)

> **K 契約**:「維持並補完一條**全本地、零 Claude token、背景自動**的知識管線:
> ①【抓】經治權審批(每源 approve=人閘)的外部股票投資 know-how 來源,自動增量抓入本地 PostgreSQL
> (staging→promote,provenance 可溯源,全文依 license 三軌);
> ②【懂】對語料做**確定性逐字逐句理解**——定義=lexicon 辭書錨定、意涵=concordance 出現處組織、
> 思想相關性/相關係數=npmi/jaccard/llr **閉式統計**(DB CHECK 硬擋 LLM/embedding 冒充係數)——
> 並**新建雙向語意橋**:know-how 詞句 ↔ 本專案 raw data 欄位定義(column_catalog 754 欄+特徵目錄)。
> **橋上係數的誠實定義(對抗審查修訂)**:它是「欄位**名稱/定義文字**斷出的詞」與 know-how 詞在語料句中的
> **詞面共現關聯(lexical affinity)**——**不是**「該欄實際數值與投資結果的統計相關」;raw 數值從不進入計算。
> 呈現時此免責與係數硬綁;
> ③【存】嵌入向量以 embedspec 世代紀律入 **pgvector(SSOT)**,單向同步 **Qdrant(serving 索引,
> 可拋棄可重建)**;
> ④【答】qwen(Ollama 本機)經 advisor 檢索引用作答於 Web UI,guard 逐字防幻覺,檢索空=誠實拒答;
> ⑤【換】新來源=INSERT 一列、換向量後端=config UPDATE 一列、換 embed 模型=embedspec 登記+分批重嵌、
> 換 qwen=env/DB tiers 一列——四接縫全為資料列/env,零改架構;
> ⑥【驅】單命令 `refresh_knowledge_pipeline.py` 端到端可驅(段名封閉集),每支 script 亦個別可執行,
> systemd timer 常態背景排程,DB-driven resume;
> ⑦【界】素養層零量化價值進預測管線(相關係數=解讀素材;量化回流唯 school→principle→factor_map→#14
> 一條合法路);「全能全知」=**有界誠實**(能力上限=已審批語料×guard,非無所不答)。」

一句話版:**「管線十段已建九段半;把『know-how↔raw 欄位語意橋』補上、把已拍板的深抓 S2-S4 跑完、
把排程掛上——一條路就真的打通了。」**

## §1 現況對照(4-agent 實證;規格逐項 vs 事實)

| 規格詞 | 現況(證據=DB 實查/檔:行) | 判 |
|---|---|---|
| 抓外部 know-how→PostgreSQL | ✅ 三層管線活著:source 3,598→staging 302,650→item 254,176→item_text 151,810(license 三軌+誠實 skip 16,548) | 已建 |
| 逐字理解(定義/意涵) | ✅ lexicon 154,875 定義(六源公版)+concordance **52.2M** 逐字 postings(16 分區,四游標建畢) | 已建 |
| 思想相關性/相關係數 | ◕ term_cooccurrence 6.53M+term_affinity **2.96M**(npmi/jaccard/llr 閉式,method FK 可溯源)——**但只算哲學語料**(JOIN philosophy_work_text);投資 items 語料在統計鏈外 | 缺半 |
| **↔raw data 交互對應** | ❌ **知識側與 column_catalog(754 欄)之間零 JOIN 零橋表零 builder**;最近似=principle_factor_map 42 列(原則↔特徵粒度)+field_lens_map 342 列(欄位↔三鏡頭類別,無係數無 know-how 連結) | **真缺口** |
| 寫入 Qdrant | ◕ 已接線且 sentence_items 已 cutover(影子 eval 0.912≥0.90);**架構=pgvector 為 SSOT、Qdrant 為可拋棄 serving 索引**(憲章雙庫鐵則,刻意設計);sync 落後 ~4.7k、works collection 未上 live server | 已建待補 |
| 接 qwen+Web UI | ✅ chat(:8090)→advisor(:8399,guard 防幻覺)→ollama qwen3:8b,四服務常駐、concept_graph 已接線 | 已建 |
| 換向量/qwen 模型 | ✅ embedspec 世代(fail-loud)+vectorstore_config 逐 scope+fallback 降級;qwen=env/DB tiers/--model | 已建 |
| 每支端到端串接 | ✅ refresh_knowledge_pipeline 八段 DAG(flock/心跳/--reap/resume)+e2e 煙測今日綠 | 已建 |
| 背景自動跑 | ◕ embed 補嵌 03:30/daily green 07:30/L2 自審 06:15 已排程;**harvest/refresh 無任何 cron/timer**=新料進鏈靠手動 | 缺排程 |
| 窮舉抓取 | ◕ 深抓計畫 P0-P12 已簽核(2026-07-10)但 **S2-S4 未執行**:來源目錄 pace/quota/license_regime 全 NULL、引擎三層閘只活第 3 層、Wave 1 未跑、S3/S4 四支 script 不存在;投資/經濟域全文近零(economics 82/business 100) | 缺執行 |
| 全能全知 | ⚠ 治權定義為**有界誠實**:每源 approve 永為人閘(AI 永不 approve)、現代版權投資著作全文依法不可入庫(metadata 級)——「無人值守自動擴源」憲章不允許 | 邊界 |

**今日紅燈(已修,本計畫 K0)**:daily_green regression 紅——方向分類器裸「未來N天」樣式誤傷 g1 相對選股題;
已修(共現判定)、10 例單測+regression 全綠、advisor 重啟(commit 77cee4b)。

## §2 真缺口(=本計畫的全部工作)

- **K1 語意橋(核心新建)**:know-how 詞句 ↔ raw 欄位定義 的確定性對應+相關係數。
- **K2 統計鏈擴 items 語料**:investment know-how 的詞進 cooccurrence/affinity(現只算哲學)。
- **K3 深抓 S2-S4 執行**(已拍板計畫的落地):目錄 backfill+引擎閘接線+Wave 1 投資域+四支新 script。
- **K4 排程掛載**:refresh 管線上 systemd timer(僅 active 源,治權相容的自動化)。
- **K5 Qdrant 完備**:sync 落後清償+works collection 重匯;其餘 scope cutover 屬 D6 變更需另裁。
- **K6(後置)W7 對齊層**:knowledge_alignment 句對句 builder(哲學向,投資軸非關鍵)。

## §3 Table Schema(v1.39.0(a);DDL 住 `migrate_knowhow_bridge_ddl.py`(新))

```sql
-- 前置:method registry seed(審查修訂:string_rule/sql_join 是 method_KIND 非 method_KEY,須先註冊新 key)
INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES
  ('rule_field_term_map',           'string_rule',      '欄名/中文名/髒值註/表註/特徵名經 textnorm 契約斷詞→詞'),
  ('join_field_lexical_affinity',   'sql_join',         'field_term_map JOIN term_affinity 之物化(零新事實)'),
  ('cnt_item_term',                 'counting',         'items 語料 term×item tf 計數'),
  ('stat_items_corpus_marginal',    'counting',         'items 語料句級邊際分母 df_sents/N(items 獨立分母 SSOT)')
ON CONFLICT (method_key) DO NOTHING;

-- K1a 橋:raw 欄位 ↔ 正規化詞(確定性 string_rule;textnorm 契約與 concordance 同)
CREATE TABLE IF NOT EXISTS field_term_map (
  dataset      text NOT NULL,              -- column_catalog.dataset 或 'feature'(特徵目錄)
  column_name  text NOT NULL,              -- 欄名或 feature 名
  term         text NOT NULL,
  language     text NOT NULL CHECK (language IN ('zh','en')),
  source_field text NOT NULL CHECK (source_field IN
    ('column_name','column_name_zh','dirty_value_note','dataset_notes','feature_name')),  -- 審查修訂:dataset_desc 不存在→dataset_catalog.notes/table_name_zh
  method_key   text NOT NULL REFERENCES knowledge_derivation_method(method_key),  -- ='rule_field_term_map'
  created_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (dataset, column_name, term, source_field));

-- K1b 橋上係數:欄位詞 ↔ know-how 詞「詞面共現關聯」(審查修訂:改名 lexical、加 pair 支持度+最小分母閘)
CREATE TABLE IF NOT EXISTS field_knowhow_lexical_affinity (
  dataset      text NOT NULL,
  column_name  text NOT NULL,
  knowhow_term text NOT NULL,
  language     text NOT NULL,
  stat_key     text NOT NULL CHECK (stat_key IN ('npmi','jaccard','llr')),
  stat_value   double precision NOT NULL,
  cooc_sents   bigint NOT NULL CHECK (cooc_sents >= 30),  -- pair 真支持度;最小分母閘(操作值,遠嚴於內部 min_cooc=5)
  corpus_n     bigint NOT NULL,            -- 語料句總數 N(npmi 邊際分母;審查修訂:非 pair 支持度,誠實分開兩欄)
  corpus       text NOT NULL CHECK (corpus IN ('philosophy','items')),
  method_key   text NOT NULL REFERENCES knowledge_derivation_method(method_key),  -- ='join_field_lexical_affinity'
  built_at     timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (dataset, column_name, knowhow_term, stat_key, corpus));
COMMENT ON TABLE field_knowhow_lexical_affinity IS
  '詞面共現關聯(lexical):欄位名稱詞×know-how 詞之語料句共現統計;非資料值相關;素養層唯讀、免責硬綁';

-- K2 統計鏈語料判別(審查修訂:PK 重建明文化+分母表也要 corpus-split)
ALTER TABLE knowledge_term_cooccurrence ADD COLUMN IF NOT EXISTS corpus text NOT NULL DEFAULT 'philosophy';
ALTER TABLE knowledge_term_affinity     ADD COLUMN IF NOT EXISTS corpus text NOT NULL DEFAULT 'philosophy';
ALTER TABLE knowledge_term_corpus_stats ADD COLUMN IF NOT EXISTS corpus text NOT NULL DEFAULT 'philosophy';
-- PK 重建(ACCESS EXCLUSIVE,6.53M/2.96M/0.45M 列數十秒級;#30 dump 後執行、避開 dump 窗)
ALTER TABLE knowledge_term_cooccurrence DROP CONSTRAINT knowledge_term_cooccurrence_pkey,
  ADD PRIMARY KEY (language, term_a, term_b, corpus);
ALTER TABLE knowledge_term_affinity DROP CONSTRAINT knowledge_term_affinity_pkey,
  ADD PRIMARY KEY (term_a, term_b, language, stat_key, corpus);
ALTER TABLE knowledge_term_corpus_stats DROP CONSTRAINT knowledge_term_corpus_stats_pkey,
  ADD PRIMARY KEY (term, language, corpus);
-- K2 items 側 tf(item_id integer 對齊 knowledge_item PK 型別;審查修訂)
CREATE TABLE IF NOT EXISTS knowledge_item_term_stats (
  term text NOT NULL, language text NOT NULL,
  item_id integer NOT NULL REFERENCES knowledge_item(item_id),
  tf integer NOT NULL,
  method_key text NOT NULL REFERENCES knowledge_derivation_method(method_key),  -- ='cnt_item_term'
  PRIMARY KEY (term, item_id));
```

**items 語料 CLEAN 判準(審查修訂:items 無 corpus_class/review_flag,須明定)**:
`knowledge_sentence JOIN knowledge_item_text USING(text_id) JOIN knowledge_item USING(item_id)
WHERE item.domain IN ('finance','economics','business') AND item_text.license_ok(三軌過閘之全文)
AND item_text.access_scope IN ('public','local_private')`——**license 過閘全文=items 的 CLEAN**;
分母 df_sents/N 於此集合內獨立計算(corpus='items' 之 corpus_stats 列),**絕不沿用哲學語料分母**(#15)。

**所讀既有表**:column_catalog(754 欄)/dataset_catalog(95 表)/feature_values(特徵名目錄)/
knowledge_sentence·concordance·term_affinity·derivation_method/knowledge_source(+22 治理欄)。
**K3 零新表**(深抓五表已在,0 列待引擎寫入);**K5/K6 零新表**(qdrant_sync_state、knowledge_alignment 已有 DDL)。
**機械鎖不動**:derivation_method.method_kind CHECK 四值封閉——橋層一切係數只能是 counting/closed_form_stat/
string_rule/sql_join,**embedding/LLM 係數 DB 硬擋**(嵌入=檢索索引非內容,查詢時用、不落統計表)。

## §4 Python 程式規畫(v1.39.0(b))

| 檔 | 職責(I/O) |
|---|---|
| `scripts/migrate_knowhow_bridge_ddl.py`(新) | §3 DDL 冪等+corpus 欄遷移(6.53M/2.96M 列,dump 後執行守 #30)+現況唯讀 |
| `scripts/build_field_knowledge_bridge.py`(新) | K1:讀 column_catalog+dataset_catalog(table_name_zh/notes)+feature_values(distinct feature)→textnorm 斷詞→field_term_map;再 JOIN term_affinity(corpus∈both)物化 field_knowhow_lexical_affinity(**cooc_sents≥30 最小分母閘**;低支持 pair 不物化);resume-safe、`--rebuild` 冪等 |
| `scripts/build_cross_school_stats.py`(改) | K2:`--corpus items` 軌,**範圍=term-corpus/cooccurrence/affinity 三 phase 而已**(審查修訂:groupstats 學派/思想家 keyness 對 items 無定義、不移植——此為實質新分支非 FETCH 換行);items CLEAN 判準見 §3;分母獨立計(corpus_stats corpus='items');**DELETE 述詞與 ON CONFLICT 全帶 corpus**(防跨語料互刪/覆寫) |
| `scripts/harvest_knowledge.py`(改) | K3 閘一:_Q_CORE/_S_CORE 加 `approval_status='active'`+cooldown LEFT JOIN+advisory lock+`--wave` |
| `scripts/acquire_knowledge.py`(改) | K3 閘二:讀 knowledge_source.pace_seconds/quota_*/cooldown(DB 限速 #24 對偶)+health 記帳+honor Retry-After;`oai_pmh` adapter(+1,ADAPTERS 第 14 個) |
| `scripts/promote_knowledge.py`(改) | K3 閘二:入庫 JOIN active 閘+norm_doi 前置+批次化 |
| `scripts/fetch_pd_fulltext.py`(新,深抓 §6 已規) | 公版全文抓取(FRASER/Gutenberg 財經公版;P8 方案A born-digital) |
| `scripts/curate_source_candidates.py`+`load_knowledge_dump.py`+`report_knowledge_coverage.py`(新,深抓已規) | 候選源策展/dump 載入/覆蓋率報告(寫 coverage_snapshot) |
| `scripts/refresh_knowledge_pipeline.py`(改) | 段名封閉集 +2:`stats_items`、`bridge`(排 stats 之後、embed 之前);其餘不動 |
| `~/.config/systemd/user/augur-knowhow-refresh.{service,timer}`(新) | K4:每週日 02:00 `refresh_knowledge_pipeline --domain finance`(flock 防重疊、僅 active 源、零 token) |
| `src/augur/advisor/advise.py`(改) | 橋接線:欄位/特徵相關問句→引 field_knowhow_lexical_affinity+concordance 出處作**解讀素材**(唯讀,同 concept_graph 模式、G6 RBAC 收窄沿用);**回答硬綁免責「詞面共現,非資料值與報酬之相關」** |
| `src/augur/audit/import_isolation.py`+`tests/test_philosophy_isolation.py`(改) | **隔離機械鎖(審查 blocker 修訂)**:新增 `BRIDGE_LITERALS=('field_term_map','field_knowhow_lexical_affinity','knowledge_item_term_stats')` 入**字面掃描**(預測 7 package+core+scripts 洩漏掃描——import 稽核看不到 raw SQL,字面掃描才鎖得住「SELECT stat_value 當特徵」旁路);測試加 fail-closed 反斷言 |
| `scripts/verify_knowledge_e2e_smoke.py`(改) | +橋斷言:sentinel 欄位詞→field_term_map 命中→lexical_affinity 查得(cooc_sents≥閘)→advisor 回答含逐字出處+免責;+fail-closed 反斷言(低支持 pair 不出現) |

## §5 治權約束(不變式對照;先講死)

1. **隔離不變式不動(機械鎖=字面掃描,審查 blocker 修訂)**:橋層住素養側;因橋表結構恰是「每欄一係數」
   形狀(最貼近特徵表的旁路風險),機械鎖用 import_isolation.py 的**字面掃描**擴 `BRIDGE_LITERALS`
   (AST import 稽核看不到 raw SQL,字面掃描才能攔「預測 package 零 import 直接 SELECT stat_value」);
   此擴閘涉隔離安全邊界=**列拍板點 R5**,非執行層自改。橋上係數=**解讀素材**,永不直接當特徵。
2. **量化回流唯一合法路**:若某橋映射看起來有預測價值 → 走 school(domain='investment')→principle→
   factor_map→#14 經濟驗證鏈,人拍板才進;**本計畫不開任何旁路**。
3. **每源 approve=常設人閘**(憲章 v1.41.0):K4 排程自動化的是「**已 approve 源的增量**」;新源/升級
   永遠 TTY 人核。「窮舉」=治理下的有界窮舉。
4. **全文准入三軌不動**:投資 know-how 的現代版權著作止於 metadata+誠實 fulltext_blocked;富礦=公版
   (FRASER/EDGAR/經典)+OA+自有 owned_local。
5. **禁 AI 生成入庫**:橋與統計全確定性(textnorm/SQL/閉式公式);「意涵」=advisor 即時解讀不落庫。

## §6 分階段・驗收・拍板點

| 階段 | 內容 | 驗收(#7 實測) | 依賴 |
|---|---|---|---|
| **K0** | green 紅燈修復 | ✅ 已完成(77cee4b,regression 三段 PASS) | — |
| **T0** | 本計畫拍板(含 R1-R4) | — | — |
| **K1** | 橋 DDL+builder+隔離字面閘+advisor 接線+煙測擴 | field_term_map 覆蓋 754 欄+特徵目錄;**lexical_affinity 有效列分佈報告**(cooc_sents≥30 之欄覆蓋數/每欄 top 詞,非「非空」即過);sentinel 欄位問答引逐字出處+免責;隔離字面掃描紅綠雙向測試 | K2(係數面) |
| **K2** | 統計鏈擴 items(migration+builder 三 phase 分支) | philosophy 側三表 count 遷移前後**雙向不變**(零損+零覆寫);items 分母獨立(corpus_stats corpus='items' 列存在且 N=items CLEAN 句數);跑 items 軌後 philosophy 列數再驗不變 | dump 先行(#30) |
| **K3** | 深抓 S2-S4(目錄 backfill+三閘接線+Wave 1+四 script) | 三層閘負向測試(proposed 源被三層各自擋);Wave 1 投資域 item_text 增量達 probe 預估下限;coverage_snapshot 首列 | R4 人核源清單 |
| **K4** | 排程掛載 | timer 首跑 log 綠、flock 防重驗證、零 token 佐證 | K3 |
| **K5** | Qdrant sync 清償+works 重匯 | qdrant_sync_state 追平嵌入數;shadow eval 續綠 | — |
| **K6**(後置) | W7 對齊 builder | 引文對齊有效列(對齊對抽樣人核) | 另裁 |

**誠實里程碑(審查修訂,先講死)**:**係數橋的「豐度」是 K3 之後的獨立里程碑**——投資域全文現況近零
(economics 82/business 100,受 license 三軌硬約束),K1/K2 完成時 items 側 lexical_affinity 將**近空,
屬語料限制非 bug**;哲學語料側(150K 全文)先行可用。「打通」宣稱僅指管線暢通,不指係數豐度。

**拍板點**:**R1** 橋層定性=解讀素材唯讀+詞面共現免責硬綁(建議案,§5.1-5.2)|**R2** corpus 遷移核可
(動 6.5M 列三表 PK 重建,dump 後執行)|**R3** 排程掛載核可(週日 02:00)|**R4** Wave 1 投資域源清單:
probe 報告出爐後 TTY 逐源 approve(人閘)|**R5** 隔離字面閘擴 BRIDGE_LITERALS(涉安全邊界,憲章高風險
門檻)|**R6** 投資語料檢索品質債:e5-small 對財經 CJK 已實證不可靠(advise.py:113 out-of-corpus 高分離題
→confabulate;relevance.py:9 窄帶),投資語料上線前先量測檢索命中率,不合格→評估換嵌入模型(embedspec
世代機制已支援);「檢索非空但離題」之處置(rerank/拒答門檻)一併定。

**token 經濟**:全計畫執行層零 Claude token(builder/遷移/抓取/嵌入/同步全本地);Claude 只出現在
本計畫的理解與審查(已花)。**與擂台/解凍鏈零衝突**(不碰預測資料層)。

## §7 對抗審查發現表(Opus 4.8 三視角;1 blocker+9 major+3 minor,全數吸收)

| # | 視角 | 發現(摘) | 裁處 |
|---|---|---|---|
| B1(blocker) | 治權 | 隔離機械鎖引錯機制:AST import 稽核看不到 raw SQL;橋表=「每欄一係數」形狀,零 import 的 `SELECT stat_value` 即靜默繞過共同不變式② | 改字面掃描擴 BRIDGE_LITERALS;升拍板點 R5 |
| M1 | 完整誠實 | **偷換規格核心詞**:橋上「相關係數」實為欄位**名稱詞**與 know-how 詞的詞面共現,非資料值相關,易誤讀為數據訊號 | §0 誠實定義+表改名 lexical_affinity+advisor 免責硬綁(R1 前提) |
| M2 | 治權+工程 | items 分母 SSOT 缺:corpus_stats 未 split,items 係數會沉默沿用哲學分母=假兆 | corpus_stats 加 corpus 欄+items 獨立算分母+驗收斷言 |
| M3 | 工程 | 「PK 重建含 corpus」散文有 SQL 無:舊 PK 下 items 與 philosophy 互撞/互刪(builder DELETE-by-language 連 items 清掉) | DDL 補三表 DROP/ADD PK;builder DELETE/ON CONFLICT 全帶 corpus;雙向零損驗收 |
| M4 | 工程 | items CLEAN 判準未定義(items 無 corpus_class/review_flag) | 明定=license 三軌過閘全文+domain 過濾(§3) |
| M5 | 工程 | 「FETCH 換行」低估:build_cross_school_stats 核心是學派 keyness(items 無學派結構),僅 term 三 phase 可移植 | K2 範圍明定三 phase;誠實標實質新分支 |
| M6 | 工程 | dataset_desc 欄不存在 | 改 dataset_catalog.notes/table_name_zh(dataset_notes) |
| M7 | 完整誠實 | basis_n 註解與事實矛盾(=語料 N 常數非 pair 支持度);無最小分母閘,稀疏語料出無意義係數 | 分開 cooc_sents(CHECK≥30)與 corpus_n 兩欄;低支持不物化 |
| M8 | 完整誠實 | 驗收「非空即過」近乎建構保證;係數橋在 K3 前近空未誠實列明 | 驗收升級為分佈門檻;「誠實里程碑」段明文豐度=K3 後 |
| M9 | 完整誠實 | e5-small 對財經 CJK 檢索不可靠(codebase 自證);「檢索空=拒答」漏了「非空但離題→幻覺」失敗態 | 新拍板點 R6(檢索品質量測+rerank/拒答門檻) |
| m1-m3 | 各 | method_key/kind 混淆(FK 會直接失敗)、item_id 型別、advisor 呈現語意 | seed 4 列新 method_key;integer;免責語硬綁 |
