# 跨學說統計層 schema(v2.0 (d)(e)(f) 族擴充;合成 A/B/C 三案、fatal/major 全修)

**全表通則(紅線①機器強制)**:每個衍生層表每列 `method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key)`;method_kind 四值 CHECK(counting/closed_form_stat/string_rule/sql_join)= embedding 相似度與 LLM 判斷之 DB 硬擋(A 案 nullable 漏洞已修=全表 NOT NULL)。term 欄值域=`augur.knowledge.textnorm` 輸出形(紅線④)。命名僅 stats/vocab/seed/affinity/co_occurrence/alignment/edge/metric/charter,零 truth/omniscien* 字面(charter forbidden_pat 補中文 `全知|真理`)。DDL 正式住所=`scripts/migrate_text_understanding_ddl.py`(§二 L34),builder 內嵌同文自舉、兩處同步。

## (d) 合規骨架
### knowledge_derivation_method(v2.0 原文)
方法白名單。種子 17 列(cnt_term_work/cnt_term_corpus/gate_stat_vocab/rule_proponents_parse/join_prior_school_thinker/rule_confirmed_school_edge/join_work_of_thinker/agg_group_rollup/cnt_cooc_sentence/stat_npmi/stat_jaccard/stat_llr_dunning/stat_keyness_llr/stat_log_odds_dirichlet/stat_tf_share/stat_tfidf_cosine/stat_keyness_topk_jaccard),kind 全在四值集內、零判準變更;definition 逐欄列公式與分母(C 案寬列溯源斷鏈之修法)。
| 欄 | 型別 | 語意 |
|---|---|---|
| method_key | varchar(64) PK | 方法鍵 |
| method_kind | varchar(24) CHECK 四值 | 合法方法集(封閉=判準,擴值=決策層) |
| definition | text NOT NULL | 公式逐字(含每欄公式與分母來源) |

## (e) 計數基層(物化=完整事實,concordance 為 SSOT 永存 → 任何截斷可按需 SQL 精確重算)
### knowledge_term_stats(v2.0 原文+NOT NULL 補強)— term×work 計數
| 欄 | 型別 | 語意 | method |
|---|---|---|---|
| term/language | text/varchar(8) | textnorm 形 | — |
| work_id | int FK philosophy_work | 出處 work(CLEAN=review_flag=false AND corpus_class='literary',fail-closed) | — |
| tf | int | 該 work 內 postings 數 | cnt_term_work(counting) |
| df_works | int | 語料級 df 反正規化副本(SSOT=corpus_stats;同 phase 同掃描寫入=防雙源漂移,A-minor 修) | cnt_term_work |
PK(term,language,work_id)。實測外推 ≈275 萬列(C 案 p0×16),免分區。

### knowledge_term_corpus_stats(新)— 語言層分母 SSOT
| 欄 | 型別 | 語意 | method |
|---|---|---|---|
| term/language | text/varchar(8) | PK | — |
| tf_total | bigint | 全語料詞頻 | cnt_term_corpus(counting) |
| df_works | int | 出現 work 數 | cnt_term_corpus |
| df_sents | bigint | 出現句數(NPMI/Jaccard/LLR 邊際分母) | cnt_term_corpus |
≈44.8 萬列。不含 idf/rank 欄(閉式值按需導出,避 C 案寬列混 kind)。

### knowledge_stat_vocab(新)— 統計詞彙閘(en 未去 stopword 之顯式對策)
| 欄 | 型別 | 語意 | method |
|---|---|---|---|
| term/language | PK | 凡進共現/親和計算必在本表 | — |
| gate_reason | varchar(24) CHECK('freq_gate','lexicon_hit') | 入閘依據 | gate_stat_vocab(closed_form_stat) |
只存成員資格,不存計數(A 案 df 雙源漂移修法=分母只居 corpus_stats)。閘參數(頻帶 R、df_floor F、cap K)=操作值印 log,不鑄 schema(#27)。重跑 vocab=同 tx 重置下游 staging/cooc/affinity(不留舊口徑幽靈列,B 案陳舊化缺口修法)。

### knowledge_school_thinker_seed(新)— 歸屬鏈缺口修補(紅線⑤)
| 欄 | 型別 | 語意 | method |
|---|---|---|---|
| school_id/thinker_id | int FK 雙表 | PK | — |
| matched_text | text NOT NULL | proponents 原文片段/既存表重述(逐字 provenance) | — |
| match_rule | varchar(24) CHECK('exact_name','normalized_name','name_zh','prior_table') | **無 'manual'**(A-minor 修:列一律 string_rule/sql_join 產生,人工僅得改 review_status) | rule_proponents_parse(string_rule)/join_prior_school_thinker(sql_join) |
| review_status | varchar(12) CHECK('seed','confirmed','rejected') DEFAULT 'seed' | 人拍板閘,confirmed 才投影 edge=fail-closed | — |
本次實查新事實:**`school_thinker` 表已存在(19 列、17 校 17 思想家,無 provenance/review 欄,框架 build 非冪等所產)**——經 seed 匯入(match_rule='prior_table')走同一確認流,不直接採信。

### knowledge_term_group_stats(新)— 跨群組聚合基表
| 欄 | 型別 | 語意 | method |
|---|---|---|---|
| group_kind | varchar(12) CHECK('school','thinker') | **fatal 修法**:school 鏈現況近空(seed 匹配 53+19 中僅孫武/Livermore 有全文;en 591 部古典文本×現代 proponents=0 交集)→ thinker 軌(173 位有 CLEAN 全文)=當下非空之跨語料統計交付;school 軌 fail-closed 建好等鏈;學說語料補救三選一(補現代文本/古典 re-seed/其他分群)=**決策層拍板項,本設計不越權** | — |
| group_id | int | school_id 或 thinker_id | — |
| term/language | | textnorm 形;term 域=stat_vocab(有界) | — |
| tf/df_works | bigint/int | 群內計數(school=僅 confirmed edge 鏈上卷) | agg_group_rollup(sql_join) |
PK(group_kind,group_id,term,language)。domain 不冗餘落欄(44 校 JOIN 零成本,拒 C 案反正規化)。

### knowledge_term_cooccurrence(新)— 唯一 pair 級物化(紅線③)
| 欄 | 型別 | 語意 | method |
|---|---|---|---|
| term_a/term_b | text,CHECK(term_a<term_b) | 存序無向 pair,**只存計數不存 rank**(C-major a<b vs rank 矛盾修法) | — |
| language | varchar(8) | 不跨語 | — |
| cooc_sents/cooc_works | bigint/int | 共句數/共 work 數 | cnt_cooc_sentence(counting) |
PK(language,term_a,term_b)。有界三閘:兩端∈vocab+cooc_sents≥min_cooc(操作值)+zh 排除子字串 pair(**共通 major 修:textnorm 雙軌 詞↔構成字 P=1 artifact,string_rule 濾層入 method definition**)。en 43.7 萬²=1.9e11 全物化禁令→上界 ≈vocab²有界後百萬-千萬級,build 前 SQL 實算。計數 upsert=DO UPDATE(語料增長重跑=刷新,B-major 凍結修法)。

### knowledge_term_affinity(新)— term 親和(長格式=一列一公式一 method_key,A 案溯源純度)
| 欄 | 型別 | 語意 | method |
|---|---|---|---|
| term_a | text | **anchor(有向)**,每 anchor 每 stat top-K 雙向物化(C-major 修:base 表無向、本表有向,回查 cooc 用 LEAST/GREATEST) | — |
| term_b/language | | 鄰居 | — |
| stat_key | varchar(16) CHECK('npmi','jaccard','llr') | log_odds 移出(pair 語意不合,歸群組層) | — |
| stat_value | double precision | 閉式值 | stat_npmi/stat_jaccard/stat_llr_dunning |
| basis_n | bigint | N=CLEAN 句數(語言內,實測 en 1,505,700/zh 33,319) | — |
| rank_in_a | smallint(**無 BETWEEN CHECK**,K=操作值,A-minor 修) | COMMENT 明載口徑:僅已物化 pair 中名次,非全域 top-K | — |
PK(term_a,term_b,language,stat_key)。重算=語言 scope DELETE+INSERT(確定性冪等)。

### knowledge_term_group_affinity(新)— 群組 keyness(哪些詞定義了這個群)
欄:group_kind/group_id/term/language/stat_key CHECK('keyness_llr','log_odds_dirichlet','tf_share')/stat_value/basis_n(=語言內 vocab token 總量)/rank_in_group(無上限 CHECK)/method_key。PK(group_kind,group_id,term,language,stat_key)。method=stat_keyness_llr/stat_log_odds_dirichlet/stat_tf_share(全 closed_form_stat)。

### knowledge_group_affinity(新)— 群×群統計關聯(「學說互相理解」的誠實承載)
欄:group_kind/group_a/group_b CHECK(a<b)/language/stat_key CHECK('tfidf_cosine_counts','keyness_topk_jaccard')/stat_value/basis_n(cosine=共享詞數;jaccard=聯集基數,COMMENT 入庫)/method_key。PK 全欄含 language(**B-major 修:分語言分母歸一,zh 不被 102:1 淹沒**)。shared_thinker_n **移除**(無語言語意=A 案 PK hack;=edge 上一句 SQL,歸按需家族)。school=C(44,2)=946 上界全量;thinker=anchor top-K 有界。method=stat_tfidf_cosine/stat_keyness_topk_jaccard。

### knowledge_alignment(v2.0 原文,本次不建管線)
grain CHECK('chapter','quote') 封閉、anchor NOT NULL;句級=另拍板。**跨語 chapter 對齊=blocked(共通 major:實測 0 個 work 同時有 en/zh 文本,譯本配對 method 未定義=決策層)**;引文網(quote)後續 builder 之綁定契約:hashtextextended(非 hashtext int4,C-major 碰撞修)+hash 命中後 ngram_text 逐字等值回驗+zh 只用單字軌 n-gram(C-major 雙軌破碎修)。

### knowledge_edge(v2.0 原文+族內擴欄 evidence_n)
6 述詞封閉集、provenance 三值照舊(拒 B 案 12 述詞/edge 併吞統計之重寫);`evidence_n int NOT NULL DEFAULT 1`=支撐列數(counting,零新事實保持)。本次 populate:work_of_thinker(sql_join,1,374)+thinker_of_school(僅 confirmed seed 投影,**非 confirmed 既存邊同步刪除=fail-closed 同步**);term_in_work/term_defined_by 不批量物化(與 term_stats 全冗餘)。

## (f) 宣稱層(v2.0 原文)
### knowledge_coverage_metric — append-only;本 builder 寫入:clean_sents_{lang}、stat_vocab_{lang}、cooc_pairs_{lang}、rows_*、school_seed_confirmed、**schools_with_clean_text(分子/44=fatal 之誠實錶)**、xlang_parallel_works(實測 0)。同日重跑=ON CONFLICT re-measure,不改往日列。
### knowledge_capability_charter — 初始列 layer='affinity_stats'(can/cannot/forbidden_pat=`(?i)(truth|omniscien)|全知|真理` 含中文,A-minor 修);**charter phase 不含於 --phase all,先印全文=用戶過目才 --run 入庫**。

## 快取(非知識宣稱)
### knowledge_sent_terms_stage — UNLOGGED,(language,term,sent_id,work_id),concordance⋈vocab⋈CLEAN 之 DISTINCT 投影(零新事實,可 TRUNCATE 重建;崩潰截斷有偵測+--rebuild-staging)。存在理由=**A-major 修:concordance 分區鍵實查=HASH(term),同句 terms 散在 16 分區,逐分區自交=系統性漏計假計數;正解=staging+anchor-block 全域自交**。

## 有界物化判準(統一)與按需 SQL 家族
物化 iff:上界閉合≤10⁴ 全量(school pair 946)∨ 聚合 grain O(詞彙×works/群)且 build 前 SQL 實算≤10⁷ ∨ top-K/閾值截斷後有界且 rank 落欄可稽核;估>10⁸ 回頭重設計(5.6 億 pair 教訓)。按需家族(文件化不物化):任意低頻 pair NPMI 精確重算(concordance term 索引)、work×work 相似、shared_thinker_n、edge 列回鑽 evidence、thinker×thinker 全對。C 案 T7 digest(統計句渲染嵌入)**不建**=與紅線②「AI 只在回答時刻組織」緊張,未拍板前禁建(對抗判決)。

---

## DDL 全文
```sql
-- knowledge_derivation_method
CREATE TABLE IF NOT EXISTS knowledge_derivation_method (
  method_key  varchar(64) PRIMARY KEY,
  method_kind varchar(24) NOT NULL CHECK (method_kind IN ('counting','closed_form_stat','string_rule','sql_join')),
  definition  text NOT NULL
);

-- knowledge_term_stats
CREATE TABLE IF NOT EXISTS knowledge_term_stats (
  term       text        NOT NULL,
  language   varchar(8)  NOT NULL,
  work_id    int         NOT NULL REFERENCES philosophy_work(work_id),
  tf         int         NOT NULL,
  df_works   int         NOT NULL,
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (term, language, work_id)
);

-- knowledge_term_corpus_stats
CREATE TABLE IF NOT EXISTS knowledge_term_corpus_stats (
  term       text        NOT NULL,
  language   varchar(8)  NOT NULL,
  tf_total   bigint      NOT NULL,
  df_works   int         NOT NULL,
  df_sents   bigint      NOT NULL,
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (term, language)
);

-- knowledge_stat_vocab
CREATE TABLE IF NOT EXISTS knowledge_stat_vocab (
  term        text        NOT NULL,
  language    varchar(8)  NOT NULL,
  gate_reason varchar(24) NOT NULL CHECK (gate_reason IN ('freq_gate','lexicon_hit')),
  method_key  varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (term, language)
);

-- knowledge_school_thinker_seed
CREATE TABLE IF NOT EXISTS knowledge_school_thinker_seed (
  school_id     int         NOT NULL REFERENCES philosophy_school(school_id),
  thinker_id    int         NOT NULL REFERENCES philosophy_thinker(thinker_id),
  matched_text  text        NOT NULL,
  match_rule    varchar(24) NOT NULL CHECK (match_rule IN ('exact_name','normalized_name','name_zh','prior_table')),
  review_status varchar(12) NOT NULL DEFAULT 'seed' CHECK (review_status IN ('seed','confirmed','rejected')),
  method_key    varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (school_id, thinker_id)
);

-- knowledge_term_group_stats
CREATE TABLE IF NOT EXISTS knowledge_term_group_stats (
  group_kind varchar(12) NOT NULL CHECK (group_kind IN ('school','thinker')),
  group_id   int         NOT NULL,
  term       text        NOT NULL,
  language   varchar(8)  NOT NULL,
  tf         bigint      NOT NULL,
  df_works   int         NOT NULL,
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (group_kind, group_id, term, language)
);

-- knowledge_term_cooccurrence
CREATE TABLE IF NOT EXISTS knowledge_term_cooccurrence (
  term_a     text        NOT NULL,
  term_b     text        NOT NULL,
  language   varchar(8)  NOT NULL,
  cooc_sents bigint      NOT NULL,
  cooc_works int         NOT NULL,
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (language, term_a, term_b),
  CHECK (term_a < term_b)
);

-- knowledge_term_affinity
CREATE TABLE IF NOT EXISTS knowledge_term_affinity (
  term_a     text             NOT NULL,
  term_b     text             NOT NULL,
  language   varchar(8)       NOT NULL,
  stat_key   varchar(16)      NOT NULL CHECK (stat_key IN ('npmi','jaccard','llr')),
  stat_value double precision NOT NULL,
  basis_n    bigint           NOT NULL,
  rank_in_a  smallint         NOT NULL,
  method_key varchar(64)      NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (term_a, term_b, language, stat_key)
);

-- knowledge_term_group_affinity
CREATE TABLE IF NOT EXISTS knowledge_term_group_affinity (
  group_kind    varchar(12)      NOT NULL CHECK (group_kind IN ('school','thinker')),
  group_id      int              NOT NULL,
  term          text             NOT NULL,
  language      varchar(8)       NOT NULL,
  stat_key      varchar(24)      NOT NULL CHECK (stat_key IN ('keyness_llr','log_odds_dirichlet','tf_share')),
  stat_value    double precision NOT NULL,
  basis_n       bigint           NOT NULL,
  rank_in_group smallint         NOT NULL,
  method_key    varchar(64)      NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (group_kind, group_id, term, language, stat_key)
);

-- knowledge_group_affinity
CREATE TABLE IF NOT EXISTS knowledge_group_affinity (
  group_kind varchar(12)      NOT NULL CHECK (group_kind IN ('school','thinker')),
  group_a    int              NOT NULL,
  group_b    int              NOT NULL,
  language   varchar(8)       NOT NULL,
  stat_key   varchar(24)      NOT NULL CHECK (stat_key IN ('tfidf_cosine_counts','keyness_topk_jaccard')),
  stat_value double precision NOT NULL,
  basis_n    bigint           NOT NULL,
  method_key varchar(64)      NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (group_kind, group_a, group_b, language, stat_key),
  CHECK (group_a < group_b)
);

-- knowledge_alignment
CREATE TABLE IF NOT EXISTS knowledge_alignment (
  align_id     serial PRIMARY KEY,
  grain        varchar(16) CHECK (grain IN ('chapter','quote')),
  src_sent_id  int,
  dst_sent_id  int,
  src_work_id  int,
  dst_work_id  int,
  anchor       text NOT NULL,
  matched_text text,
  method_key   varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key)
);

-- knowledge_edge
CREATE TABLE IF NOT EXISTS knowledge_edge (
  edge_id    serial PRIMARY KEY,
  predicate  varchar(32) NOT NULL CHECK (predicate IN
    ('term_in_work','term_defined_by','work_of_thinker','thinker_of_school','work_in_taxonomy','work_quotes_work')),
  src_id     int NOT NULL,
  dst_id     int NOT NULL,
  provenance varchar(16) CHECK (provenance IN ('join','string_rule','counting')),
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  UNIQUE (predicate, src_id, dst_id)
);

-- knowledge_edge.evidence_n(族內擴欄)
ALTER TABLE knowledge_edge ADD COLUMN IF NOT EXISTS evidence_n int NOT NULL DEFAULT 1;

-- knowledge_coverage_metric
CREATE TABLE IF NOT EXISTS knowledge_coverage_metric (
  metric_date date,
  metric_key  varchar(32),
  numerator   bigint,
  denominator bigint,
  note        text,
  PRIMARY KEY (metric_date, metric_key)
);

-- knowledge_capability_charter
CREATE TABLE IF NOT EXISTS knowledge_capability_charter (
  layer         varchar(32) PRIMARY KEY,
  can_answer    text NOT NULL,
  cannot_answer text NOT NULL,
  forbidden_pat text
);

-- knowledge_sent_terms_stage(推導快取,零新事實,可 TRUNCATE 重建)
CREATE UNLOGGED TABLE IF NOT EXISTS knowledge_sent_terms_stage (
  language varchar(8) NOT NULL,
  term     text       NOT NULL,
  sent_id  int        NOT NULL,
  work_id  int        NOT NULL,
  PRIMARY KEY (language, term, sent_id)
);

-- comments(口徑入庫)
COMMENT ON COLUMN knowledge_term_affinity.rank_in_a IS
  '口徑:僅「通過 vocab 閘+min-cooc 門檻之已物化 pair」中的名次,非全域 top-K(低頻 pair 可按需 SQL 對 concordance 精確重算)';
COMMENT ON TABLE knowledge_term_cooccurrence IS
  '唯一 pair 級物化:兩端∈knowledge_stat_vocab+cooc_sents≥min_cooc;zh 排除子字串 pair(詞↔構成字 P=1 artifact);其餘 pair=按需 SQL 精確重算';
COMMENT ON COLUMN knowledge_term_stats.df_works IS
  '語料級 df 之反正規化副本(SSOT=knowledge_term_corpus_stats.df_works);同一 phase 同一掃描寫入,重建必同步';
COMMENT ON COLUMN knowledge_group_affinity.basis_n IS
  'tfidf_cosine_counts=兩向量共享 vocab 詞數;keyness_topk_jaccard=top-M keyness 詞集聯集基數';

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('cnt_term_work','counting','tf(t,l,w)=COUNT(*) postings FROM knowledge_concordance c JOIN knowledge_sentence s ON s.sent_id=c.sent_id JOIN philosophy_work_text wt ON wt.text_id=s.text_id JOIN philosophy_work w ON w.work_id=wt.work_id WHERE review_flag=false AND corpus_class=''literary'' GROUP BY term,language,work_id;df_works(t,l)=COUNT(*) OVER (PARTITION BY term,language)(=corpus_stats.df_works 同掃描反正規化副本)') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('cnt_term_corpus','counting','同 cnt_term_work 之 CLEAN 掃描聚合到 (term,language):tf_total=SUM(tf);df_works=COUNT(DISTINCT work_id);df_sents=COUNT(DISTINCT sent_id)(NPMI/Jaccard/LLR 句級邊際分母之 SSOT)') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('gate_stat_vocab','closed_form_stat','入閘=tf_rank(語言內,ORDER BY tf_total DESC)>R AND df_works>=F,取前 K;R/F/K=操作值(#27),每次 build 印於 log,不鑄入 schema。en 未去 stopword(the 3.2M/of 2.1M postings 實測在庫)故必須顯式閘') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('rule_proponents_parse','string_rule','philosophy_school.proponents 以 [;,、/]+'' and '' 切分→trim→與 philosophy_thinker.name/name_zh 精確或 lower(trim()) 正規化等值匹配;人工不得手建列,僅得改 review_status(confirm/reject)') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('join_prior_school_thinker','sql_join','既存 school_thinker 表(19 列,無 provenance/review 欄,框架 build 非冪等所產)之列重述為 seed(review_status=''seed'');matched_text=school.name||'' <- ''||thinker.name;不直接採信=fail-closed') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('rule_confirmed_school_edge','string_rule','knowledge_edge(thinker_of_school) = seed 表 WHERE review_status=''confirmed'' 之投影;非 confirmed 之既存邊同步刪除(fail-closed 投影,人拍板才進圖)') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('join_work_of_thinker','sql_join','knowledge_edge(work_of_thinker) = philosophy_work(work_id,thinker_id) 重述,零新事實') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('agg_group_rollup','sql_join','tf(t,l,g)=SUM(term_stats.tf) over 群組 works;thinker 群=work.thinker_id;school 群=confirmed thinker_of_school edge∘work_of_thinker 鏈;term 域=knowledge_stat_vocab(有界)') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('cnt_cooc_sentence','counting','cooc_sents(a,b,l)=COUNT(DISTINCT sent_id) 同句含 a,b;cooc_works 同理;域=兩端∈stat_vocab 且 a<b;zh 排除 a 為 b 子字串(或反之)之 pair(textnorm 雙軌 詞↔構成字 P=1 之確定性 artifact);留存門檻 cooc_sents>=min_cooc(操作值印 log);句集=CLEAN works 句') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('stat_npmi','closed_form_stat','pmi=ln(c_ab*N/(c_a*c_b));npmi=pmi/(-ln(c_ab/N));c_x=corpus_stats.df_sents,c_ab=cooc_sents,N=CLEAN 句數(語言內,basis_n 落欄)') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('stat_jaccard','closed_form_stat','J=c_ab/(c_a+c_b-c_ab),句級,分母來源同 stat_npmi') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('stat_llr_dunning','closed_form_stat','Dunning 1993 G2 over 2x2 句計數表(k11=c_ab,k12=c_a-c_ab,k21=c_b-c_ab,k22=N-c_a-c_b+c_ab);符號=sign(c_ab*N-c_a*c_b)') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('stat_keyness_llr','closed_form_stat','G2 over 2x2 token 表(群內 tf vs 同語言其餘語料 tf;域=vocab terms;符號=群內相對頻率高為正);basis_n=語言內 vocab token 總量') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('stat_log_odds_dirichlet','closed_form_stat','Monroe et al. 2008 informative Dirichlet prior log-odds z-score;prior α_t=a0*tf_total(t)/T,a0=操作值印 log;群 vs 同語言其餘語料') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('stat_tf_share','closed_form_stat','tf(t,g)/tf_total(t)(群佔比,0..1)') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('stat_tfidf_cosine','closed_form_stat','cosine over 群組詞頻向量;權重=tf*ln(G/df_groups),G=同 kind 同語言有語料之群數,df_groups=含該 term 之群數;全由 counts 導出,零 embedding') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;

INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) VALUES ('stat_keyness_topk_jaccard','closed_form_stat','J=|A∩B|/|A∪B|,A/B=兩群 keyness_llr>0 之 top-M term 集(M=操作值印 log);basis_n=|A∪B|') ON CONFLICT (method_key) DO UPDATE SET method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition;
```

## Milvus 銜接
## Milvus 寫入前準備(嵌入=索引非內容;紅線①②之讀路徑落地)

**哪些欄餵向量(僅原文,統計永不餵)**:
1. `knowledge_sentence.sentence`(主鍵 sent_id)——zh 已嵌 33,314 列、en 全量 8-11h/6.3GB=既拍板批次(pgvector `knowledge_sentence_embedding` vector(384)+model_tag,實查既存)。
2. `knowledge_lexicon.term + definition`(主鍵 lex_id)——154,875 列已全量嵌(`knowledge_lexicon_embedding`)。
3. `philosophy_chunk`(主鍵 chunk pk)——63,601 列已嵌(`philosophy_chunk_embedding`)。
本次交付之全部統計表(term_stats/corpus_stats/stat_vocab/cooccurrence/affinity/group_stats/group_affinity/edge/seed)**任何欄位皆不餵向量**;C 案 digest(統計結論句渲染再嵌)因與紅線②「AI 只在回答時刻組織」正面緊張,**未經決策層拍板不建**(對抗判決採納)。

**Collection 對映(pgvector=庫內 SSOT,Milvus=可拋棄外部加速索引)**:
- `kx_sent_{model_tag}_{textnorm_ver}`:向量+pg_pk(sent_id)+窄 scalar payload {language, work_id, thinker_id, school_ids int[](僅 confirmed thinker_of_school 鏈,現況空=誠實), corpus_class}——payload 由 PG JOIN(sentence→work_text→work→edge)匯出,partition key=language。
- `kx_lexicon_{model_tag}`:lex_id+{language, lex_type}。
- `kx_chunk_{model_tag}`:chunk pk+{language, work_id}。
換 embedding model 或 textnorm/jieba 版本=新 collection 重建,不原地混版(對齊 textnorm「換版本須重建」條款);正文與數字永不進 Milvus。

**同步協議**:批次 export 游標記 `knowledge_build_meta`(scope=`mv_{collection}`,≤32 字元,與資料同 tx 推進);Milvus upsert by pg_pk 冪等;synced_rows vs source_rows 對帳差值以 COUNT 實查 append `knowledge_coverage_metric`(如 `milvus_sent_en`:分子=已索引、分母=CLEAN 句 1,505,700 實測);school 鏈重校(review_status 變動)→只重刷 payload 不重算向量。

**讀路徑鐵則(嵌入=索引非內容的機器強制)**:query → textnorm 正規化 → (a) 精確路徑:直接 SQL 打 corpus_stats/term_affinity/group_affinity(零向量);(b) 語意路徑:query 先取 `knowledge_term_affinity` top-K npmi 鄰居做**確定性 query 擴展**+雙語雙查(=§四實測修法,對治 zh 單字→junk 0.84)→ Milvus ANN 回 **id+distance 而已** → 一律回 PG JOIN(sentence/concordance char offset/affinity/edge)取內容與統計 → AI 於回答時刻組織。ANN distance 僅「檢索索引分數」——**永不寫入任何 knowledge_* 表**(method_kind 四值 CHECK=無合法 kind 可載=DB 硬擋);rerank 若用,只准 counts 類分數(keyness/npmi),嵌入分數不落庫不排序回流。

**寫前完成定義**:phases ddl→metrics 全跑+charter 列用戶過目後,Milvus 側只消費上列三鏡像;本設計不為 Milvus 新增任何 PG 表,嵌入層與統計層零交叉;任何時點可 DROP collection 從 PG 全量重建。

## 啟動指令
`cd /home/hugo/project/augur && .venv/bin/python scripts/build_cross_school_stats.py            # 無參數=唯讀資訊矩陣(已實測通過);微測: --phase all --run --smoke ;放量: --phase all --run ;配額護欄分段: --phase cooc --run --limit 4(游標自動續)。註:檔案已落地 /home/hugo/project/augur/scripts/build_cross_school_stats.py,唯讀模式+py_compile 實測通過;--run 寫入路徑未實測(未經授權不動 DB,誠實聲明)。`
