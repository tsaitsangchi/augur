# 全文落地與逐字理解計畫 v2.0(重生版:text corpus → verbatim understanding →「誠實博學的我」)

**日期**:2026-07-03(v2.0 重生;v1.x 歷程見 §九)　**系列**:知識三部曲之三
**重生依據**:五鏡對抗審查 27 案(9 pass/17 pass_with_guard/1 kill)+ 向量層專鏡(pass_with_guard)+ **執行實測定錨**(T3 156.8 萬句 50.6s/T4 44k 列/s/lexicon 154,875 條上線/「道」5,026 處)
**治權**:靈魂 v1.4.0 · 憲章 v1.20.0(全文准入雙軌)· CLAUDE #28/#29

---

## 〇、命門定錨(v1 四條不變 + v2.0 新增三條)

1. 逐字逐句定義不由 AI 生成入庫;合法載體=公版辭書/註疏(**已實現:lexicon 154,875 條**)+ concordance(**已實現:「道」5,026 處**)+ 純計算統計 + 真實文獻。AI 只在回答時刻組織真兆。
2. 「全能全知」=漸近北極星;**字面全知不得鑄入 schema/表名/措辭**(v2.0:omniscience 一律改稱 coverage);系統必答「不知道」且分三級(§七)。
3. 多域知識素養層零量化價值、不進預測管線、不產因子(隔離不變式擴及 `augur.knowledge`,機器強制)。
4. 確定性優先:結構/統計/對齊/圖譜各層一律計數、閉式公式、字串規則;禁 LLM 判斷入庫。
5. **〔新〕AI 記憶物理隔離籠**:AI 產出(回答快取/對話記憶)若落庫,唯一住所=獨立 schema、`is_ai_generated` 恆真 CHECK、不回饋檢索排序——堵死「AI 舊回答兩跳洗白入庫」。
6. **〔新〕宣稱誠實化**:各層能力邊界入庫可查(charter 小表);guard 措辭閘——統計陳述不得升格為知識斷言。
7. **〔新〕嵌入=索引非內容**:向量化的都是真兆原文(定義/句/段),向量命中後 guard 仍逐字引用原文。

## 一、八層金字塔(v2.0)

```
L6 治理橫切  歸屬治理常備化(寫入蓋章+fail-closed 述詞+人審 CLI)· verify_text_integrity 常備稽核器
             · derivation_method 憲欄 · AI 記憶隔離籠 · charter 宣稱表
L5 角色層    「誠實博學的我」:answer.py 四段管線 · 三級誠實 · 自我知識視圖 · coverage 四指標時序
L4 語意層    三粒度分表嵌入:chunk(63,601 既有)+ lexicon_embedding(新)+ sentence_embedding(新)
L3.5 衍生層  經-注-疏對齊 · 跨語平行(章節錨定)· 詞義歷時 · 引文網(n-gram)· knowledge_edge 圖譜
L3 定義層    knowledge_lexicon ✅ 154,875 條(說文/康熙 p0/Webster/Roget/王弼/論語孟子注疏)
L2.5 統計層  knowledge_term_stats 聚合(物化)+ 共現 PMI/keyness(按需 SQL,不預算表)
L2 結構層    sentence ✅ 1,567,854 句 · concordance ✅(zh 全量+en 物化中,總 ~5,000 萬列)
L1 全文層    work_text(公版)+ item_text(公版+CC 白名單,憲章 v1.20.0)+ corpus_class 語料角色欄(新)
L0 來源層    registry 三表 ✅(query 4,706/source 3,592/taxonomy 4,798)
```

## 二、schema 增補(全部併入 T0 `migrate_text_understanding_ddl.py` 同一冪等住所,#12)

```sql
-- (a) 歸屬治理常備化(L6)
ALTER TABLE philosophy_work
  ADD COLUMN IF NOT EXISTS review_reason text,
  ADD COLUMN IF NOT EXISTS reviewed_by varchar(16) CHECK (reviewed_by IN ('audit','provenance','human')),
  ADD COLUMN IF NOT EXISTS reviewed_at timestamptz;
-- 述詞 SSOT:src/augur/knowledge/corpus.py 之 CLEAN_WORK = "w.review_flag = false"(fail-closed,NULL 不放行)
-- 全部 builder(T2-T5/embed/L5 檢索)引用;guard:reviewed_by='provenance' 僅限「策展來源+身分可驗」,自動遍歷型不得用

-- (b) 語料角色(L1;值由 knowledge_source 來源定義決定、promote 時寫入,防 DEFAULT fail-open)
ALTER TABLE philosophy_work ADD COLUMN IF NOT EXISTS corpus_class varchar(16) NOT NULL DEFAULT 'literary'
  CHECK (corpus_class IN ('literary','reference'));
-- 六源辭書/類語→'reference'(只走 lexicon 解析,不進 T3/T4/T5);註疏歸屬=單欄可逆拍板(預設 reference)

-- (c) 三粒度嵌入(L4;與既有 philosophy_chunk_embedding 同構、分表〔HNSW post-filter 陷阱實測 0 列坑〕)
CREATE TABLE IF NOT EXISTS knowledge_lexicon_embedding (
  lex_id INT PRIMARY KEY REFERENCES knowledge_lexicon(lex_id) ON DELETE CASCADE,
  embedding vector(384) NOT NULL, model_tag VARCHAR(64) NOT NULL);
CREATE TABLE IF NOT EXISTS knowledge_sentence_embedding (
  sent_id INT PRIMARY KEY REFERENCES knowledge_sentence(sent_id) ON DELETE CASCADE,
  embedding vector(384) NOT NULL, model_tag VARCHAR(64) NOT NULL);
-- HNSW:灌完才建;1.5M 級前置 SET maintenance_work_mem='2GB';帶過濾 kNN 一律 SET hnsw.iterative_scan=relaxed_order

-- (d) 衍生層合規骨架(L6,treaty 鏡憲欄)
CREATE TABLE IF NOT EXISTS knowledge_derivation_method (
  method_key varchar(64) PRIMARY KEY,
  method_kind varchar(24) NOT NULL CHECK (method_kind IN ('counting','closed_form_stat','string_rule','sql_join')),
  definition text NOT NULL);          -- 每個衍生層列一律 FK 本表;LLM/embedding 相似度不在合法 kind 集=DB 硬擋
-- (e) 統計/對齊/圖譜(L2.5/L3.5;各帶 derivation_method FK 與 provenance)
CREATE TABLE IF NOT EXISTS knowledge_term_stats ( -- 聚合統計(取代 5.6 億 pair 預算表,千倍槓桿)
  term text, language varchar(8), work_id int, tf int, df_works int, method_key varchar(64) REFERENCES knowledge_derivation_method,
  PRIMARY KEY (term, language, work_id));
CREATE TABLE IF NOT EXISTS knowledge_alignment (  -- 對齊統一單表(grain CHECK 封閉;句級開放=另拍板)
  align_id serial PRIMARY KEY, grain varchar(16) CHECK (grain IN ('chapter','quote')),
  src_sent_id int, dst_sent_id int, src_work_id int, dst_work_id int,
  anchor text NOT NULL, matched_text text, method_key varchar(64) REFERENCES knowledge_derivation_method);
CREATE TABLE IF NOT EXISTS knowledge_edge (       -- 圖譜 JOIN 物化(零新事實;predicate 封閉集)
  edge_id serial PRIMARY KEY, predicate varchar(32) NOT NULL CHECK (predicate IN
    ('term_in_work','term_defined_by','work_of_thinker','thinker_of_school','work_in_taxonomy','work_quotes_work')),
  src_id int NOT NULL, dst_id int NOT NULL, provenance varchar(16) CHECK (provenance IN ('join','string_rule','counting')),
  method_key varchar(64) REFERENCES knowledge_derivation_method, UNIQUE (predicate, src_id, dst_id));
-- (f) 指標與宣稱(L5/L6)
CREATE TABLE IF NOT EXISTS knowledge_coverage_metric (  -- 命門2:不得名 omniscience
  metric_date date, metric_key varchar(32), numerator bigint, denominator bigint, note text,
  PRIMARY KEY (metric_date, metric_key));               -- append-only 不重寫歷史
CREATE TABLE IF NOT EXISTS knowledge_capability_charter (
  layer varchar(32) PRIMARY KEY, can_answer text NOT NULL, cannot_answer text NOT NULL,
  forbidden_pat text);                                   -- 確定性 regex;初始列與新增=用戶過目
```

## 三、程式增補(全 #29:矩陣/冪等/resume/graceful)

| 支 | 職責 | 關鍵紀律 |
|---|---|---|
| `embed_knowledge.py`(新) | `--layer {lexicon\|sentence\|chunk} [--language] [--limit]`;e5-small+"passage: "+批 64;build_meta 游標(embed_* scope) | **硬閘:一律 `CLEAN_WORK` 述詞**(向量鏡實查 lexicon 全數來源 work 未蓋章=先 W1);passage=`COALESCE(term_display,term)`;junk 過濾分語言(zh <10 字=真訓詁句不得剔,改全符號規則);每期首 1,000 列實測重投影吞吐 |
| `verify_text_integrity.py`(新) | C1/C2/C6/歸屬不變式全量 SQL 稽核、exit 1 擋管線;`--sample/--full` | 逐字承諾的常備機器證明(取代抽樣手驗) |
| `review_flagged_works.py`(新) | 151+ 部 flag 人審 CLI:`--list`(佇列+證據)/`--accept id --thinker-id`/`--reject id` | 人審=決策層;AI 只呈證據 |
| `refresh_text_understanding.py`(新) | T-1→T3→T4→T4b→T5→embed 增量統一驅動器;harvest 輪末可掛 | 順序閘為輔、fail-closed 述詞為主(雙保險) |
| `audit_work_attribution.py` 擴 | `--incremental`(只稽核 NULL)+ 蓋 reviewed_by/reviewed_at/review_reason | fetch/harvest 輪末自動補跑 |
| `src/augur/knowledge/answer.py`(新,L5) | 四段:問題→規則檢索計畫(exact 優先 semantic 補)→多層真兆 JOIN→引用作答+全閘 | 跨語:query 擴展(先 exact 取定義併入 query)+雙語雙查 UNION re-rank(向量鏡實測法) |
| `src/augur/knowledge/profile.py`(新,L5) | 自我知識視圖族:「我學過什麼」=harvest_log/build_meta/coverage 可查詢化 | — |
| `report_knowledge_coverage.py`(新) | 四指標算入 coverage_metric;誠實率=**固定測例重放**(動態實證非靜態宣稱) | — |
| builder 述詞統一(改) | T2-T5/檢索全引 `corpus.py CLEAN_WORK` + `corpus_class='literary'`(T3/T4/T5)| 切換前先跑 W1 蓋章,無資料損失 |

## 四、實測定錨(v2.0 以程式輸出取代一切估算,#15)

| 項 | 實測 |
|---|---|
| T3 全量 | 21,682 段→1,567,773 句,50.6s(428.8 段/s) |
| T4 吞吐 | 44k 列/s;zh 全量 27.2s;en 全量物化 ~50M 列/5.4GB=分鐘-小時級(進行中) |
| 嵌入吞吐 | lexicon 10.2 條/s(→p0 全量 5-6h/0.65GB)、句 77.1 句/s(→zh 12 分/0.24GB;en 全量 8-11h/6.3GB=拍板) |
| 跨語實測 | en 長 query→zh chunk rank3-4 可用;zh 單字→junk 0.84 污染 → 修法=query 擴展+雙語雙查+relaxed_order;驗收 rank@10 記真值不預設過 |

## 五、拍板點(僅剩 3 + 2 執行工單)

1. **en 句嵌入範圍**:A 全量(8-11h/6.3GB)/B 去重濾後(~4.5GB)/**C 子集(高頻 term 命中句/投資域 work,推薦)**——「能嵌≠該嵌」,L5 實需驗證後可升級
2. **註疏 corpus_class**:預設 reference(只走 lexicon);要讓注疏可語意檢索則改 literary(單欄 UPDATE 可逆)
3. **句級對齊 grain**:v2.0 先 chapter/quote 封閉集;句級開放=判準變更另拍板
- 工單 A:chunk junk 塊清理(「_」「----」0.84 高分污染,**須先於跨語驗收**)
- 工單 B:review_flag NULL 新生 125+ 部(含 T2 六源)→ W1 `--incremental` 蓋章收斂

## 六、執行序(W1-W9)

```
W1 治理常備化(--incremental 蓋章+述詞切 fail-closed+人審 CLI 佇列)   ← 一切嵌入/衍生層的硬先決
W2 verify_text_integrity 上線(C2/C6 全量必 0)
W3 corpus_class 落欄+六源標 reference
W4 T4 en 物化收尾(進行中)+ 計數=grep 驗收
W5 embed p0 lexicon(5-6h)→ p1 zh 句(12 分)→ 跨語驗收 rank@10(先做工單 A)
W6 L2.5 term_stats 物化 + 共現按需 SQL 定案
W7 L3.5 衍生層(合規骨架先行:derivation_method+charter → 對齊/引文網/圖譜)
W8 L5:answer.py+profile.py+三級誠實+coverage report
W9 en 句嵌入(拍板點 1 裁決後)
```

## 七、「誠實博學的我」(L5 定義,取代字面全知)

- **能力形**:任一字/句 → 出現處(concordance 5,000 萬列)× 定義(lexicon 154,875)× 解經(註疏)× 語意近鄰(三粒度向量)× 知識圖譜(term↔thinker↔school↔taxonomy)七維 JOIN,逐字引用+locator。
- **誠實形**:三級誠實(全無/部分有/有但未驗〔review_flag/unverified 源〕)機器分級;coverage 四指標(topic 覆蓋率/lineage 可溯源率/高頻詞可解率/誠實率=固定測例重放)append-only 時序;charter 表明文「我能答什麼/不能答什麼」。
- **記憶形**:知識庫=長期記憶;harvest_log/build_meta=學習履歷;AI 對話產出只進隔離籠(命門 5)。

## 八、驗收判準(v2.0)

1. W1 後:`SELECT count(*) FROM philosophy_work WHERE review_flag IS NULL AND EXISTS(全文)` = **0**(常備不變式)
2. verify_text_integrity `--full`:C2 句/C6 定義逐字子串驗 = 全量 0 違反
3. concordance 計數=grep 數(數學相等,已實證「道」);reference 語料句數=0
4. 嵌入計數=來源計數(排除項逐類誠實印);跨語 rank@10 記真值
5. L5:七維 JOIN 一問通;三級誠實各觸發一例;coverage 首期四指標入庫可溯源

## 九、修訂歷程

v1.0→v1.3(三輪 solo:7→5→8 缺口)→ v1.4(五鏡 confirmed 11 項)→ v1.5(憲章 v1.20.0 CC 雙軌)→ v1.6(雙重驗證 7 縫:T-1 稽核閘)→ **v2.0(重生:五鏡 27 案〔9 pass/17 guard/1 kill〕+向量專鏡+T3/T4/lexicon 執行實測定錨;新增 L2.5/L3.5/L6、三粒度嵌入、治理常備化、誠實化條款群)**。
