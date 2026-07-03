# 全球 know-how 落地計畫 v1.3(harvest:registry → PostgreSQL 正式表)

**日期**:2026-07-02(v1.1 同日補完美:修 7 缺陷,見 §八)　**執行體**:`scripts/harvest_knowledge.py`(本地 Python、背景、零 LLM)
**上游**:`knowledge_query`(4,706 詞)× `knowledge_source`(73+ 列)× `knowledge_taxonomy`(4,798 節點,皆已實建)
**治權**:憲章 v1.19.0 知識層多域擴充準則 · CLAUDE #28/#29 · #17 限速 · #15 誠實

---

## 一、落地資料流(五層,鏡射 augur raw 管線)

```
① registry 層   knowledge_query × knowledge_source × knowledge_taxonomy + knowledge_domain_map(排程空間)
② harvest 層    harvest_knowledge.py 批次驅動器(排程矩陣+限速+熔斷+resume)
③ staging 層    knowledge_staging(payload JSONB + provenance + query_id,③′ 補欄)
④ promote 層    promote_knowledge.py(mapper 正規化、冪等去重、lineage)
⑤ 正式表        人物→philosophy_thinker | 著作→philosophy_work(公版全文→work_text)
                | 論文/報告/資料集/化合物/蛋白/物種→ knowledge_item(新建)
```

## 二、接收 schema(PostgreSQL 17 DDL)

### 1. `knowledge_item` — 通用知識條目正式表
```sql
CREATE TABLE knowledge_item (
  item_id      serial PRIMARY KEY,
  domain       varchar(64) NOT NULL,
  entity_type  varchar(32) NOT NULL,          -- paper/report/dataset/compound/material/protein/species…
  title        text NOT NULL,
  title_zh     text,
  year         int,
  authors      text,                          -- 分號串(顯示);正規化人物住 thinker
  external_id  text,                          -- 跨源去重鍵(優先序見 §二4)
  venue        text,
  url          text,                          -- 可溯源(#1)
  taxonomy_id  int REFERENCES knowledge_taxonomy(tax_id),
  source_key   varchar(64) REFERENCES knowledge_source(source_key),
  staging_id   int,                           -- 回溯原始 payload
  ingested_at  timestamptz DEFAULT now()
);
CREATE UNIQUE INDEX uq_item_extid ON knowledge_item (entity_type, external_id) WHERE external_id IS NOT NULL;
CREATE UNIQUE INDEX uq_item_title ON knowledge_item (entity_type, md5(title), COALESCE(year,0)) WHERE external_id IS NULL;  -- v1.2:僅無 external_id 者用 title+year 去重(否則同名同年不同 DOI〔Editorial/Erratum 常見〕相撞靜默丟件,五鏡實測重現)
CREATE INDEX idx_item_domain ON knowledge_item (domain, entity_type);
CREATE INDEX idx_item_tax    ON knowledge_item (taxonomy_id);
```

### 2. `knowledge_harvest_log` — 排程進度帳本(resume 心臟)
```sql
CREATE TABLE knowledge_harvest_log (
  query_id    int NOT NULL DEFAULT 0,         -- 0=單跑型 sentinel;**故意不設 FK**(0 無對應列;>0 完整性由 harvest 寫入時保證+驗收抽驗)
  source_key  varchar(64) REFERENCES knowledge_source(source_key),
  last_run    timestamptz,
  rows_staged int,
  attempts    int DEFAULT 1,                  -- error 重試上限 2,防無限重跑(§八缺陷5)
  status      varchar(16) CHECK (status IN ('ok','empty','error')),
  note        text,
  PRIMARY KEY (query_id, source_key)
);
```

### 3. `knowledge_domain_map` — OpenAlex field → augur 域對映(§八缺陷3)
taxonomy 衍生詞的 domain=OpenAlex field slug(26 個),與手動域/來源域不同名 → 資料驅動對映表:
```sql
CREATE TABLE knowledge_domain_map (
  openalex_field varchar(64) PRIMARY KEY,     -- 'materials_science' 等 26 field slugs
  augur_domain   varchar(64) NOT NULL         -- 'energy_materials'/'chemistry'/'physics'/…或保留原 slug
);
```
種子(v1.2 治理修正:**僅決策層已拍板之域建列**——未拍板 field〔medicine/nursing/arts 等〕不建恆等列,INNER JOIN 天然排除出排程並於啟動印排除統計;納入新域=決策層 INSERT):已拍板域覆寫對映(明文列舉):
`materials_science→energy_materials`·`energy→energy_materials`·`economics_econometrics_and_finance→finance_mgmt`·`business_management_and_accounting→business_mgmt`·`decision_sciences→organization_mgmt`·`chemistry→chemistry`·`chemical_engineering→chemistry`·`physics_and_astronomy→physics`·`biochemistry_genetics_and_molecular_biology→biology`·`engineering→electronics`(電子相近域)——**其餘 16 未拍板 field(medicine/nursing/arts 等)不建列**(v1.3 刪 v1.1 殘句「保留原 slug 為新域名」——與治理閘互斥;啟用=決策層 INSERT)。**新對映=INSERT/UPDATE,零 code**。實際 slug 以 `SELECT DISTINCT` 結果為準(公式 SSOT 在 expansion script,#25 執行時核)。

### 4. 既有表補欄(③′/①′)
```sql
ALTER TABLE knowledge_staging ADD COLUMN IF NOT EXISTS query_id int;        -- v1.2:IF NOT EXISTS 使「可重放」宣稱成立
ALTER TABLE knowledge_query   ADD COLUMN IF NOT EXISTS taxonomy_id int REFERENCES knowledge_taxonomy(tax_id);
UPDATE knowledge_query q SET taxonomy_id = t.tax_id           -- 遷移:P1 暫存於 note 的 openalex_id 轉正
  FROM knowledge_taxonomy t WHERE q.origin='openalex_taxonomy' AND t.openalex_id = q.note;
```

### 5. promote mapper 擴充(code 層)
`promote_item`:staging(entity_type ∈ paper/report/dataset/compound/material/protein/species)→ `knowledge_item`。
**external_id 優先序(明文)**:`doi > arxiv_id > chembl_id/cid > uniprot_id > gbif_id > osti_id > openalex_id > ia_identifier > openlibrary_key`;無任一 → title+year 去重鍵。
`taxonomy_id` 回填:staging.query_id → knowledge_query.taxonomy_id(lineage 全鏈:item→staging→query→taxonomy→source)。
`staging_id` **故意不設 FK**(staging 可歸檔清理,回溯為 best-effort;v1.2 註記)。

## 三、落地過程作法(harvest_knowledge.py 逐步;**§二全部 DDL 之冪等 migrate 住所=本 script 啟動時自建**〔CREATE TABLE/INDEX 全帶 IF NOT EXISTS,v1.3 補住所〕)

1. **載排程(兩型,§八缺陷4)**:
   - **(a) 查詢型**(template 含 `{query}`):
     ```sql
     SELECT q.query_id, q.query, m.augur_domain, s.source_key
     FROM knowledge_query q
     JOIN knowledge_domain_map m ON m.openalex_field = q.domain   -- 手動域=恆等列
     JOIN knowledge_source s ON s.enabled AND (s.query_template LIKE '%{query}%' OR s.query_template LIKE '%{query_raw}%')
       AND s.adapter <> 'manual_file'
       AND s.entity_type IN ('work','compound','material','protein','species')   -- v1.3:排除 thinker 即可(v1.2 誤寫 ='work' 白名單,靜默剔除 chembl/pubchem/cod/gbif/uniprot 5 合法源 393 組合,與 §一⑤承諾自相矛盾)
       AND (s.domain='general' OR s.domain = m.augur_domain)
     LEFT JOIN knowledge_harvest_log l USING (query_id, source_key)
     WHERE q.enabled AND (l.status IS NULL OR (l.status='error' AND l.attempts < 2))
     ORDER BY (q.origin='manual') DESC,
              (SELECT works_count FROM knowledge_taxonomy t WHERE t.tax_id=q.taxonomy_id) DESC NULLS LAST
     LIMIT {batch}
     ```
   - **(b) 單跑型**(enabled 且 template 非空且同時不含 `{query}`/`{query_raw}`):每源獨立跑一次;**limit 依 #18 探測**——首跑 500,若回滿 500 → 記 log 並翻頁/提高再跑(500=初值非寫死上限,v1.2);log 以 `query_id=0` 記錄。
   - **(c) ID 驅動型(v1.3 新分類)**:template 含 `{query_raw}` 且無 `{query}`(unpaywall_doi=DOI、wikidata_people=職業 QID)——**本質收 ID 非詞彙**,不入詞彙排程(否則 4,706 詞代入 DOI-lookup 必 404=垃圾組合)、不入單跑;僅**手動 acquire 或上游 ID feed 驅動**(如 crossref 結果之 DOI 餵 unpaywall)。DB 實算單跑型=**26 源**(v1.2 誤計 28 含此 2 源,更正)。
2. **批次執行**:每組合 `acquire --source S --query Q --domain D --query-id QID --limit 25` → upsert harvest_log(status+rows+attempts);**限速矩陣** per-source sleep(openalex 0.5s/crossref 1s/dbpedia 3s/其餘 1.5s);**熔斷**:同源本輪連續 5 錯 → 跳過該源其餘組合。
3. **輪末 promote(v1.2 治理)**:`work`/`item` 自動;**thinker 僅單跑型來源(獎項/策展類)自動晉升**,查詢型來源之 thinker payload 一律留 staging pending 人審(守「審核後晉升」、防概念實體污染策展表)。
4. **多輪自停(§八缺陷6,省 token)**:`--rounds N`(預設 1)與 `--max-minutes M`(預設 120)——單次背景啟動連跑多輪,任一觸頂即收尾統計自停;**一次啟動=一次通知**。
5. **統計 print**:每輪組合/staged/promoted/error/熔斷源;resume 由 log 驅動。
6. **實作註記(v1.2)**:排程 SQL 一律 psycopg **參數化執行**(`%s`),`{batch}`/`{query}` 為文件示意——不得用 `.format()`;**LIKE 字面 `%` 在 psycopg 參數化下須寫 `%%`**(v1.3 半句補,已實測);harvest 啟動時印 **domain_map 未配對域統計** + **零排程來源清單**(enabled 查詢型源中配不到任何 query 者=source 側鏡像剔除偵測,v1.3);已知歸屬:`ctext_books`/`gutendex_search`(domain='philosophy',哲學全文走既有 fetch 工具鏈,**明文故意不入 harvest 排程**)。
7. **指令矩陣**:
   ```
   python scripts/harvest_knowledge.py                          # 無參數:排程統計+用法
   python scripts/harvest_knowledge.py --batch 10 --rounds 1    # 首輪最小驗證(#25)
   python scripts/harvest_knowledge.py --batch 300 --rounds 4 --max-minutes 120   # 常規背景批
   python scripts/harvest_knowledge.py --domain solar_materials --batch 100       # 圈域跑
   python scripts/harvest_knowledge.py --singles-only           # 只跑單跑型來源
   ```

## 四、量估與節奏(v1.1 修正)

- 排程空間(v1.3):**治理閘後實際排程 ≈ 1,700 詞**(手動 190 + 已拍板 field ~1,500;未拍板 16 field 詞不入)× 相容源 ≈ 萬級組合(原 28-30k 低估近 3 倍;**執行時以排程 SQL count 實算印出,計畫值=快照非承諾**)+ 單跑型(實算 28 源)
- 每組合 ~3-4s → `--batch 300` ≈ 20-25 分/輪
- `--rounds 4 --max-minutes 120` = 一次背景 ~1,200 組合 → 全量約 **50-70 次背景啟動**(nightly 一至兩月;誠實成本)
- 優先序:手動 190 詞 → 高 works_count topic → 長尾;隨時停、永遠續;AI 不自掛喚醒鏈(#28)

## 五、紀律

- **#25 首輪驗證**:`--batch 10 --rounds 1` 全鏈通(staging→item、lineage 四鏈)才放常規批
- **#17(v1.2 補)**:限速矩陣+熔斷;**acquire 層 honor `Retry-After` header**;429/503=**暫時性錯誤**——熔斷該源本輪、log note='temp'、**不 attempts++**(否則暫時限流被永久除役);僅永久性錯誤(4xx 非 429/解析錯)attempts++、≥2 除役(手動 reset 可復)
- **版權**:一律 metadata+URL/DOI;全文只走既有公版/OA 判準,本計畫不自動抓全文
- **#15**:harvest_log=誠實帳本;empty=正常結果非錯誤
- **domain 隔離**:item 不進預測管線、不產因子(憲章 v1.19.0)
- **全文歸屬稽核(v1.2 補,五鏡實證 Gutenberg 同名誤配已存在)**:`fetch_all_thinker_works` 續用前補**歸屬稽核**——作者姓名全等比對+著作年代 vs 作者生卒粗檢,不符者標 review 不入 chunk;既有 work_text 掛錯者清理(另列執行工單)
- **工具收斂(#29c,§八缺陷7)**:harvest 為 `backfill_knowhow_pipeline` 之一般化——harvest 驗收後 backfill **退役**(其 D 段 Gutenberg 掃描獨立保留=`fetch_all_thinker_works.py`,由 harvest 輪末選配呼叫或單獨排程)

## 六、驗收判準

1. 首輪 `--batch 10`(manual 詞優先):**三鏈實證** `item → staging(query_id) → query` + `source_key` 非空;`taxonomy_id` 對 `origin='manual'` **明文容 NULL**(manual 詞無 taxonomy 對映,v1.3 修——四鏈完整實證移至驗收 5 之 taxonomy 詞獨立圈跑)
2. 中斷重跑 resume 實證(已跑組合 skip;error attempts 上限生效)
3. 去重實證(同 DOI 重抓不重複)
4. 單跑型來源(dbpedia 獎項)獨立執行+log(query_id=0)實證
5. domain_map 對映生效:**獨立以 `--domain energy_materials --batch 5` 圈跑實證**(v1.2 修:主排程 manual 優先,首輪 batch 10 取不到 taxonomy 詞,故驗收 5 獨立小跑)

## 七、風險

- OpenAlex 503/S2 429(已實證)→ 熔斷+attempts 除役;re3data 3,200 目錄列 enabled=false **不在排程**(逐源驗證啟用是另一工作)
- 長尾 topic empty 正常;subprocess 啟動開銷 ~1s×28k≈8h 累計 → 若成瓶頸,後續優化為 in-process 呼叫(不改架構)
- knowledge_item 全量估數十萬列,一般索引足
- **external_id 跨 id 體系侷限(v1.3 誠實註明)**:同一論文 A 源給 doi、B 源僅 arxiv_id → 成兩條 item;v1 明文接受、無 crosswalk(後續可以 openalex_id 映射合併)

## 八之一、與 expansion 計畫之配合契約(2026-07-02 交叉檢視,修縫隙 A-E)

1. `taxonomy_id` 寫入責任移交 expansion P1 直寫(本計畫遷移 SQL 降級為冪等補漏,每輪 harvest 前可安全重放)。
2. `knowledge_domain_map` 種子=**僅拍板域建列**(手動 14 域恆等 + 已拍板 field 覆寫;v1.3 同步 §二3 治理閘,廢「SELECT DISTINCT 全恆等」舊契約)——slug 公式 SSOT 在 expansion script。
3. 單跑型來源 limit=#18 探測(首跑 500、回滿翻頁/提高至不滿額;v1.3 同步 §三1b 重定性,廢「明示 500」舊理據)。
4. 先決條件=expansion P1(分類樹)已完成即可啟動;P2 re3data 非先決(enabled=false 不在排程)。
5. 手動詞與 taxonomy 詞跨域重複(同詞不同 domain)→ 允許重抓、由 staging `ON CONFLICT` 與 item `external_id` 去重兜底(明文接受,不做排程層 dedupe 以保域歸屬)。

## 八、v1.1 修正記錄(重讀後補完美的 7 缺陷)

| # | 缺陷 | 修法 |
|---|---|---|
| 1 | query→taxonomy 連結濫用 `note` 欄(脆、不可 FK) | `knowledge_query.taxonomy_id` 正式欄+遷移 |
| 2 | staging 無 query_id → item 掛不到 taxonomy、lineage 斷鏈 | staging 加 `query_id`、acquire 加 `--query-id` 蓋章 |
| 3 | taxonomy 詞 domain(OpenAlex field slug)與來源域不相容 → 域專源配不到詞 | `knowledge_domain_map` 對映表(26 列資料驅動) |
| 4 | 無 `{query}` 來源(dbpedia 獎項)被配 4,700 詞=荒謬 | 排程分查詢型/單跑型;log query_id=0 sentinel |
| 5 | error 組合無限重入排程 | `attempts` 欄、上限 2 次除役 |
| 6 | 一輪一啟動 token 不經濟、量估過鬆 | `--rounds`/`--max-minutes` 多輪自停;量估修正 20-25 分/輪 |
| 7 | 與 backfill_knowhow_pipeline 職責重疊(#29c 違和) | harvest 驗收後 backfill 退役,明文 |

## 十、v1.2 修訂(五鏡對抗審查 confirmed 修復,2026-07-02)
[high] uq_item_title 改 partial(WHERE external_id IS NULL,同名同年不同 DOI 實測相撞)|[med] 排程 entity 閘(s.entity_type='work',防 9,412 組合灌概念實體入 thinker)|[med] promote 治理(thinker 僅單跑型自動、查詢型留審)|[med] {query_raw} 誤歸單跑修正|[med] 429/503 暫時錯誤不 attempts++、honor Retry-After|[med] ALTER IF NOT EXISTS|[med] 量估更正(實算為準、全量 50-70 次背景誠實成本)|[med] domain_map 僅拍板域(未拍板 field 天然排除=治理閘)|[med] 歸屬稽核(Gutenberg 同名誤配)|[low] 驗收5 獨立圈跑|staging_id 註記|參數化執行註記|未配對偵測

## 十一、v1.3 修訂(15 項雙重驗證 fix_gaps 補修,2026-07-02)
[med] {query_raw} 第三類 ID 驅動型(不入詞彙排程、僅 ID feed;單跑 28→26 更正)|[med] entity 閘改允許集(修 v1.2 白名單靜默剔除 compound/material 5 源)|[med] 驗收1 改三鏈+manual 容 NULL(修與驗收5 互斥)|[med] 未拍板域三處矛盾句同步(§二3 殘句刪/§八之一2 改僅拍板/量估補閘後 ~1,700 詞)|[low] source 側鏡像偵測+philosophy 兩源排除歸屬明文|[low] external_id 跨體系侷限註明|[low] §八之一3 同步/`%%` 半句/DDL migrate 住所
