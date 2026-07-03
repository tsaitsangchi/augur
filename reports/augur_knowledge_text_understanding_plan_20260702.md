# 全文落地與逐字理解計畫 v1.4(text corpus → verbatim understanding →「博學的我」)

**日期**:2026-07-02(v1.1 同日完備化:schema 全約束 + 逐支程式設計,修訂見 §九)
**系列**:知識三部曲之三(① expansion 目錄 → ② harvest metadata → ③ 本計畫全文與理解)
**治權**:靈魂 v1.4.0(博學≠占卜)· 憲章 v1.19.0 · v1.18.0(禁 AI 整理入庫)· CLAUDE #28/#29

---

## 〇、命門定錨(不因任何目標鬆動)

1. **逐字逐句定義不由 AI 生成入庫**(#1)。合規載體:公版辭書(說文/康熙/Webster 1913/Roget 1911)+ 公版註疏(王弼注/十三經注疏)+ concordance 逐字索引(純計算)。
2. **「全能全知」=漸近北極星**,操作化為 §六四指標;系統對庫外問題**必答「不知道」**。
3. AI 合法角色在**回答時刻**(RAG 引用真兆),不在入庫時刻。
4. **確定性優先**:L2 結構層一律規則演算法(regex 句切、jieba 精確模式 HMM=False、Porter stemmer)——不用 ML 黑箱切分,理解層每列可重現(#15 半年重跑一致)。

## 一、六層落地金字塔

```
L5 角色層   「博學的我」RAG 顧問(advisor 泛化 + guard 擴充)
L4 語意層    chunk + embedding 泛化(text_id | itext_id 二擇一)
L3 定義層    knowledge_lexicon(公版辭書詞條 + 註疏,解析=規則)
L2 結構層    knowledge_sentence(逐句)+ knowledge_concordance(逐字,分區表)
L1 全文層    work_text(公版,既有)+ knowledge_item_text(OA CC,新)
L0 來源層    registry 三表(①②計畫)
```

## 二、接收 schema(PostgreSQL 17,完備 DDL;統一住 `scripts/migrate_text_understanding_ddl.py` 冪等遷移)

### 1. `knowledge_item_text`(L1)
```sql
CREATE TABLE IF NOT EXISTS knowledge_item_text (
  itext_id   serial PRIMARY KEY,
  item_id    int NOT NULL REFERENCES knowledge_item(item_id),
  seq        int NOT NULL,
  content    text NOT NULL,
  language   varchar(8),
  source_url text NOT NULL,
  license    varchar(64) NOT NULL CHECK (license = 'public_domain'),   -- v1.4:憲章 v1.19.0 明文「公版全文才逐字入」;CC 白名單納入=治權升版待決策層拍板,屆時 ALTER CHECK
  fetched_at timestamptz DEFAULT now(),
  UNIQUE (item_id, seq)                          -- 冪等鍵(重跑不重複)
);
CREATE INDEX IF NOT EXISTS idx_itext_item ON knowledge_item_text (item_id);
```

### 2. `knowledge_sentence`(L2)
```sql
CREATE TABLE IF NOT EXISTS knowledge_sentence (
  sent_id    serial PRIMARY KEY,
  text_id    int REFERENCES philosophy_work_text(text_id),
  itext_id   int REFERENCES knowledge_item_text(itext_id),
  seq        int NOT NULL,
  sentence   text NOT NULL,
  language   varchar(8) NOT NULL,                -- 自上游帶入;上游 NULL 由 T3 前置確定性 backfill(v1.4,見 T3)
  char_start int NOT NULL, char_end int NOT NULL,
  CHECK (num_nonnulls(text_id, itext_id) = 1)    -- 二擇一強制
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_sent_text  ON knowledge_sentence (text_id, seq)  WHERE text_id  IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_sent_itext ON knowledge_sentence (itext_id, seq) WHERE itext_id IS NOT NULL;
```

### 3. `knowledge_concordance`(L2,分區)
```sql
CREATE TABLE IF NOT EXISTS knowledge_concordance (
  term     text NOT NULL,                        -- 正規化形(契約見 §二6)
  language varchar(8) NOT NULL,
  sent_id  int NOT NULL,                         -- 不設 FK(分區表效能;完整性由 builder 保證+抽驗)
  position int NOT NULL,
  PRIMARY KEY (term, sent_id, position)
) PARTITION BY HASH (term);
-- 16 個 hash 分區:migrate script 迴圈建 knowledge_concordance_p0..p15
CREATE INDEX IF NOT EXISTS idx_conc_lang_term ON knowledge_concordance (language, term);
```

### 4. `knowledge_lexicon`(L3)
```sql
CREATE TABLE IF NOT EXISTS knowledge_lexicon (
  lex_id         serial PRIMARY KEY,
  term           text NOT NULL,                  -- 正規化形(同 §二6 契約,與 concordance 可 JOIN)
  term_display   text,                           -- 原詞條形(繁簡/大小寫原貌)
  language       varchar(8) NOT NULL,
  definition     text NOT NULL,                  -- 逐字自公版來源
  source_work_id int NOT NULL REFERENCES philosophy_work(work_id),
  source_locator text,                           -- 卷/部首/頁碼
  lex_type       varchar(16) CHECK (lex_type IN ('dictionary','commentary','thesaurus')),
  license        varchar(64) NOT NULL DEFAULT 'public_domain' CHECK (license='public_domain'),
  UNIQUE NULLS NOT DISTINCT (term, language, source_work_id, source_locator)   -- 冪等鍵(PG15+;防 NULL locator 重複,v1.4)
);
CREATE INDEX IF NOT EXISTS idx_lex_term ON knowledge_lexicon (language, term);
```

### 5. L4 泛化(chunk 補欄,明文 DDL)
```sql
ALTER TABLE philosophy_chunk ADD COLUMN IF NOT EXISTS itext_id int REFERENCES knowledge_item_text(itext_id);
ALTER TABLE philosophy_chunk ALTER COLUMN text_id DROP NOT NULL;
ALTER TABLE philosophy_chunk ALTER COLUMN work_id DROP NOT NULL;   -- v1.4:work_id 亦 NOT NULL+FK philosophy_work,item 側無值可填(五鏡實測必炸)
ALTER TABLE philosophy_chunk ADD CONSTRAINT chk_chunk_src CHECK (num_nonnulls(text_id, itext_id) = 1);
ALTER TABLE philosophy_chunk ADD CONSTRAINT chk_chunk_work CHECK ((text_id IS NULL) = (work_id IS NULL));  -- text 側必有 work、item 側必無
CREATE UNIQUE INDEX IF NOT EXISTS uq_chunk_itext ON philosophy_chunk (itext_id, chunk_seq) WHERE itext_id IS NOT NULL;  -- v1.4:itext 側冪等鍵(NULLS DISTINCT 使既有 UNIQUE 失效)
```
`philosophy_chunk_embedding` 不變(chunk_id 域擴大即可)。

### 5b. `knowledge_build_meta` — L2 進度游標(v1.4:原引用之 build_meta 不存在,正式建表)
```sql
CREATE TABLE IF NOT EXISTS knowledge_build_meta (
  scope          varchar(32) PRIMARY KEY,   -- 'concordance_philosophy_zh' 等
  cursor_sent_id bigint NOT NULL DEFAULT 0,
  updated_at     timestamptz DEFAULT now()
);
```

### 6. term 正規化契約(T2/T4/L5 三方 JOIN 鍵,SSOT=`src/augur/knowledge/textnorm.py` 新 library 模組)
- 中文:NFC 正規化;**單字**=一-鿿 逐字;**詞**=jieba `cut(HMM=False)`(確定性、詞典驅動);繁簡不互轉(原貌,查詢層可雙查)
- 西文:lowercase + Porter stemmer(純規則);原形回 sentence 可見
- lexicon 詞條頭字同規則正規化入 `term`,原貌入 `term_display`
- 新 package `src/augur/knowledge/`(領域名詞,#18)住 textnorm + lexicon parsers(scripts 保持薄 CLI)
- **依賴(v1.4,五鏡實查 venv 皆未裝)**:`jieba` 補入 pyproject dependencies 並安裝;Porter stemmer **不引 nltk**——textnorm 內建純 Python Porter 實作(~40 行規則,零外依賴);T0 驗證 `import jieba` 過才續

## 三、程式碼設計(逐支:職責/指令矩陣/冪等/resume/錯誤/驗證)

### T0 `migrate_text_understanding_ddl.py`
§二全部 DDL 冪等執行(IF NOT EXISTS + 16 分區迴圈;ADD CONSTRAINT 先查 pg_constraint 才 ADD,v1.3 修)。**先決(v1.4):`knowledge_item` 須已由計畫② 建成**(item_text FK 依賴)——啟動先查 to_regclass,缺則 exit 並指引先跑 ② 建表。矩陣:`python scripts/migrate_text_understanding_ddl.py`。驗證:**11 物件**存在(+build_meta+chunk 新索引)+ 負向(重跑無錯)+ `import jieba` 過。

### T1 `fetch_oa_fulltext.py`(L1)
- 職責:knowledge_item(有 DOI、無 item_text)→ Unpaywall 查 `best_oa_location` → **v1 僅收 license=public_domain/US-Gov PD**(如 OSTI 報告;**CC 白名單超出憲章 v1.19.0「公版才入全文」判準,納入須治權升版另拍板**——v1 誠實少收,不越權)且 content-type ∈ {text/html, text/plain} → HTML 剝標籤(規則)→ item_text。**PDF 一律跳過記 log**。
- 矩陣:`python scripts/fetch_oa_fulltext.py [--domain X] [--limit N]`(無參數=印矩陣+待抓統計)
- 冪等/resume:`WHERE NOT EXISTS item_text`;錯誤:per-DOI 記 log 續下筆、連 5 錯熔斷;限速 0.5s(Unpaywall 要求 email env)。
- 驗證(#25):`--limit 3` 一 CC 命中落地 + 一版權未明被硬擋(負向)。

### T2 `build_lexicon.py`(L3)
- 前置:5 部辭書/註疏全文先經既有 fetch 工具入 work+work_text(來源:維基文庫〔說文/康熙/王弼注/十三經注疏〕、Gutenberg Webster 1913 / Roget——**確切 ebook ID 執行時經 gutendex 實測確認(#25),計畫不寫死記憶值**;康熙字典維基文庫完整性同樣執行時實測)。
- 職責:讀該 work 全文 → **per-source 規則 parser**(住 `src/augur/knowledge/lexicon_parsers.py`):
  - 說文:wikitext 逐字條「【字】…也」段切;locator=卷+部首
  - 康熙:部首頁結構切;Webster:行首全大寫 headword 塊切;Roget:編號段切;王弼注/注疏:經文句→注文對(lex_type='commentary',term=經文句首詞)
- 矩陣:`python scripts/build_lexicon.py --source {shuowen|kangxi|webster1913|roget1911|wangbi|shisanjing}`(v1.4 補十三經注疏,與 §〇 宣示一致;無參數=列 source+進度)
- 冪等:UNIQUE ON CONFLICT DO NOTHING;解析失敗詞條**計數誠實印出**(寧缺);驗證:每源抽 3 詞條逐字對回原文。

### T3 `build_sentences.py`(L2)
- 切分規則(確定性 regex,不用 ML):中文 `(?<=[。!?;])`(引號閉合後切);西文 `(?<=[.!?])\s+(?=[A-Z"'])`;縮寫誤切=已知侷限誠實記(v1 不追完美句界,concordance 不受影響)。
- 矩陣:`python scripts/build_sentences.py [--scope philosophy|items|all] [--limit N]`
- **前置 backfill(v1.4)**:上游 `language IS NULL` 列(實查 1,265+ 列且增長中)以**確定性規則**回填上游表——CJK 字元占比 >30% → 'zh',否則 'en'(規則明文、可重現 #15);backfill 數誠實印出。item_text 之 language 由 T1 以同規則必填。
- 冪等/resume:`WHERE NOT EXISTS sentence`(per text_id);批次 500 段/commit;char_start/end 必填(逐字回溯)。
- 驗證:抽 5 句 char_range 切回原文 byte-equal。

### T4 `build_concordance.py`(L2)
- 職責:sentence → textnorm(§二6)→ executemany 批次 1 萬列/commit 入分區表。
- 矩陣:`python scripts/build_concordance.py [--scope philosophy|items] [--language zh|en] [--limit N]`
- 冪等/resume:進度游標記於 `knowledge_build_meta`(§二5b,v1.4 正式建表);PK 衝突 DO NOTHING 兜底。
- **分期紀律(v1.4 修:原「哲學 scope」實即全 corpus 3.6 億字/26,843 段,分期虛設)**:p0=**zh 語料**(~600 段,量小先驗中文路徑)→ p1=en 抽樣 1,000 段實測吞吐 → 以 p0/p1 實測外推全量(en 3.42 億字為大頭)分批;**各期數字執行時以 SQL 實算印出,計畫值為快照非承諾**。
- 驗證:「道」in《道德經》出現數 = grep 原文數(數學相等)。

### T5 chunk/embed 泛化(既有工具改)
- `build_philosophy_chunks.py`:SELECT 加 item_text UNION(帶 itext_id);`embed_philosophy_chunks.py` 不改(吃新 chunk 增量)。
- 驗證:新 chunk 之 char_range 回原文;embedding 計數=chunk 計數。

### L5 advisor 擴充(介面明文)
- `retrieval.py` 加:`lexicon_lookup(term) -> [LexEntry(定義,出處,locator)]`、`concordance_lookup(term, limit) -> [句+work+char_range]`
- `guard.py` 新規則:定義引用必附 source_locator;檢索空 → 固定誠實句「知識庫中無此內容」(§六誠實率=100% 的機制保證)。

### 執行相依圖
```
T0 → T2(辭書先行,量小價值高) → T3(--scope philosophy) → T4(同 scope,實測效能)
   → T1(隨 harvest 增量) → T3/T4/T5 增量 → L5(T2-T4 首批驗收後)
```

## 四、L5「博學的我」(同 v1.0,誠實版全知)
RAG(L1-L4 檢索)+ 逐字引用 + guard;不進預測管線、不產因子、不宣稱全知;「學習履歷」=harvest_log/build_meta。

## 五、量估
T2 ~1-2 天背景(5 部辭書);T3+T4 哲學期 ~數小時;全 corpus concordance 數億列=分區+分期(p0 實測後定節奏);T1 隨 harvest;嵌入 e5-small 6.7 塊/s。

## 六、「全知」四指標(#15)
topic 覆蓋率 / lineage 可溯源率 / 高頻詞 lexicon 可解率 / **誠實率 100%**(guard 機制保證,非自律)。

## 七、紀律與風險
三敵不鬆(lexicon license CHECK 硬擋/AI 生成零入庫/版權未明不落全文);concordance 量級=最大風險→分區+分期+p0 實測;Webster 解析失敗率誠實記;PDF 不做(v1);「全知我」入靈魂/憲章=另請決策層拍板。

## 八、驗收判準
1. lexicon:「道」→ 說文+康熙+王弼注、"value"→ Webster,逐字可溯 locator
2. concordance:「道」全出現處秒查、char_range 回原文 byte-equal、計數=grep 數
3. item_text:CC 落地一例 + 版權未明硬擋一例(負向)
4. L5 原型:引用作答一例 + 庫外問題誠實「不知道」一例
5. 重跑冪等:**T1-T5** 全部重跑零重複(UNIQUE 實證;含 chunk itext 側 uq_chunk_itext)

## 八之一、層間介面契約(v1.2 補;每條:契約內容/SSOT 住所/驗收 SQL)

| # | 介面 | 契約 | SSOT | 驗收 |
|---|---|---|---|---|
| C1 | L2↔L3↔L5 | **term 正規化**(中文 NFC+逐字+jieba HMM=False;西文 lower+Porter)三方同一函式 | `src/augur/knowledge/textnorm.py` | `SELECT count(*) FROM knowledge_lexicon l JOIN knowledge_concordance c USING (term,language)` > 0 且抽樣詞雙表可 JOIN |
| C2 | L1↔L2↔L4 | **char_range 逐字回溯**:sentence 與 chunk 之 char_start/end 皆相對同一 content 欄 | 各 builder 寫入時計算 | 抽 5 列 `content[char_start:char_end] = sentence/chunk` byte-equal |
| C3 | L1↔L2/L4 | **text_id \| itext_id 二擇一**:sentence 與 chunk 同一取捨規則 | DDL CHECK num_nonnulls=1(兩表同式) | 負向 insert 雙空/雙填必失敗 |
| C4 | L0↔L1 | **license 硬擋**:work_text=public_domain;item_text ∈ {public_domain,cc-by,cc-by-sa,cc0} | DDL CHECK | 負向 insert 'unknown' 必失敗 |
| C5a | L0↔L1↔L5(item 側) | lineage 七層:sent→itext→item→staging(query_id)→query(taxonomy_id)→taxonomy+source | 各層 FK/欄 | 一條 JOIN SQL 走通 |
| C5b | L0↔L1↔L5(philosophy 側,v1.4 誠實拆分) | work/work_text **無 staging/query 鍵**(五鏡實查),lineage=work_text.source_url + thinker.source + work.note | 既有欄 | 抽樣列三欄非空+URL 可達 |
| C6 | L3↔L1 | 辭書/註疏**本身先為 work+work_text**(全文入庫)再解析 lexicon(定義可回原書) | T2 前置步驟 | lexicon.source_work_id 100% 非空且 work 有全文 |
| C7 | L4↔L5 | 檢索回傳=Citation(逐字+source_url+locator),guard 驗引文 ⊂ 原文 | retrieval.py/guard.py 既有機制擴充 | L5 驗收 4(誠實「不知道」)+引文回查 |

執行細計畫觸發點(僅風險層,執行時才產):L2=p0 實測報告後、L3=per-source 解析細計畫、L5=角色定位設計(涉決策層)。L1/L4 不另立篇(既有管線小擴充)。

## 九、v1.1 完備化修訂記錄
| # | v1.0 缺陷 | v1.1 修法 |
|---|---|---|
| 1 | item_text 無冪等鍵 | UNIQUE(item_id,seq) |
| 2 | sentence 二擇一無強制、無 FK/UNIQUE | CHECK num_nonnulls + 雙部分 UNIQUE + FK |
| 3 | concordance 分區「備選」未定 | PARTITION BY HASH(term)×16 明文;FK 取捨明文 |
| 4 | lexicon 無去重鍵、詞條正規化未定 | UNIQUE 四鍵;term/term_display 分欄 |
| 5 | L4 chunk 泛化 DDL 缺 | ALTER + CHECK 明文 |
| 6 | term 正規化=T2/T4/L5 隱性耦合 | §二6 契約 SSOT=`src/augur/knowledge/textnorm.py` |
| 7 | T1-T5 無逐支設計 | §三逐支:矩陣/冪等/resume/錯誤/驗證/確定性選型(regex 句切、jieba HMM=False、Porter;PDF 誠實不做) |
| 8 | 執行相依未圖示 | §三相依圖 |

## 十、v1.4 修訂(五鏡對抗審查 confirmed 修復,2026-07-02)
[high] chunk work_id NOT NULL 漏處置(實測必炸)→ DROP NOT NULL + 一致性 CHECK|[high] sentence.language 上游 1,265+ NULL → T3 確定性 backfill(CJK 比例規則)|[med] itext chunk 冪等鍵 uq_chunk_itext|[med] build_meta 不存在 → §二5b 正式建表|[med] C5 拆 C5a/C5b(philosophy 側誠實無七層鏈)|[med] jieba/nltk 未裝 → pyproject+內建 Porter|[med] 分期「哲學 scope=全 corpus」矛盾 → zh p0/en p1 實測外推|[med] lexicon NULLS NOT DISTINCT|[med] T0 先決=② item 表|[med] CC 白名單越憲章判準 → v1 僅公版、CC=治權待拍板|[low] 十三經注疏入 T2 CLI
