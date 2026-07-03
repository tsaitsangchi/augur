# 全球 know-how 來源/查詢自我窮舉計畫(knowledge registry expansion)

**日期**:2026-07-02　**執行體**:`scripts/expand_knowledge_registry.py`(本地 Python、背景、零 LLM)
**治權依據**:憲章 v1.19.0「知識層多域擴充準則」+ CLAUDE #28(執行層省 usage)/#29(資料驅動零 hardcode)

---

## 一、目標與核心思路

補齊 `knowledge_query`(查詢分類)與 `knowledge_source`(來源 registry)為**全球 know-how 目錄**。
關鍵:「全球知識分類」**不由人/AI hardcode 列舉**——世界已有機器可讀的權威分類體系與來源註冊表,直接抓取(零 token、零幻像、可溯源):

| 權威來源(真實免費 API) | 內容 | 寫入 |
|---|---|---|
| OpenAlex Topics API | 全球研究知識官方分類樹:4 domains → 26 fields → 252 subfields → ~4,500 topics | `knowledge_taxonomy`(全樹 SSOT)→ 衍生 `knowledge_query` |
| re3data API | 全球研究資料庫註冊表 ~3,200 repos(學科/API 資訊) | `knowledge_source` 目錄列(enabled=false 待驗) |
| DBpedia 獎項類別 | 諾獎×6/圖靈/菲爾茲/沃爾夫/拉斯克/科普利/普立茲克/IEEE 等得主類別 | `knowledge_source` 人物來源(沿用已實測 SPARQL 模板) |

## 二、四階段

| 階段 | 動作 | 量/估時 |
|---|---|---|
| P1 分類樹 | 抓 OpenAlex domains/fields/subfields/topics(分頁 per-page=200)→ `knowledge_taxonomy`(openalex_id/level/parent_id/name/works_count)→ 衍生 INSERT `knowledge_query`(query=topic 名、domain=field 名 slug、標 `origin='openalex_taxonomy'`) | ~25 calls / ~2 分 |
| P2 來源目錄 | re3data `/api/v1/repositories` 清單 + 逐 repo 明細(XML,解析 name/subject/apiType)→ `knowledge_source`(key=`re3data_<id>`、adapter='generic_json'、**enabled=false**、note 含學科+API 型別) | ~3,200 calls × 0.5s ≈ 30-40 分 |
| P3 人物來源 | ~20 大獎項類別 INSERT `dbpedia_award_<slug>` 來源列(SPARQL 模板同已驗) | 本地 INSERT / 秒級 |
| P4 抽測+統計 | 每類最小抽測(#25:taxonomy 詞 1 個跑 openalex_works、獎項源 1 個跑 acquire limit 3)+ 終態統計 print | ~5 calls |

## 三、schema 變更

- 新表 `knowledge_taxonomy (tax_id, openalex_id UNIQUE, level, parent_openalex_id, name, works_count)`
- `knowledge_query` 加欄 `origin varchar(32) DEFAULT 'manual'`(區分手動策展 vs taxonomy 衍生)

## 四、紀律(#29/#17/#25/#15)

- **冪等可續**:全部 `ON CONFLICT DO NOTHING`;中斷重跑安全;re3data 逐 repo 以 DB 已有 key skip(resume)
- **限速**:OpenAlex 0.3s、re3data 0.5s 步調;honor 錯誤即停該段續下段
- **不自動放量**:本計畫只擴**目錄**;不對 ~4,500 詞自動跑擷取(另需授權;pipeline 以 `--domain`/enabled 圈範圍)
- **誠實邊界**:①OpenAlex 分類=**學術知識**之窮舉,非人類全部知識(工藝/隱性 know-how 無 API 可窮舉)②re3data 目錄列**未驗 adapter 不啟用**(enabled=false,啟用需逐源實測)③獎項類別覆蓋 major 人物、非全體從業者

## 五、預期產出

| 表 | 前 | 後(估) |
|---|---|---|
| `knowledge_taxonomy` | — | ~4,800 節點(4+26+252+4,500) |
| `knowledge_query` | 190 詞/14 域 | **~4,700 詞**(手動 190 保留並存) |
| `knowledge_source` | 73 列 | **~3,300 列**(re3data 目錄 + 獎項源;enabled 維持已驗集) |

## 六、驗收判準

P4 統計:taxonomy 4 levels 皆非空、query origin 分布、source enabled/disabled 分布;抽測各 1 通過;背景完成通知後主迴圈一次讀取驗收(單次、省 token)。

## 七、風險

- re3data 為 XML API:解析失敗率>10% → 記 log 續跑、誠實報缺
- OpenAlex 503 瞬斷(今日已遇):段內重試 1 次、仍敗則跳頁記錄
- 4,700 詞使 pipeline 全量跑不再可行 → 明文:pipeline 必以 domain/enabled 圈範圍(已支援)

---

## 八、與 harvest 落地計畫之配合(v1.1 補,2026-07-02 交叉檢視)

1. **taxonomy_id 直寫(修縫隙 A)**:P1 衍生 `knowledge_query` 時,openalex_id 不再僅暫存 `note`——`knowledge_query.taxonomy_id` 欄建立後(harvest §二4),expansion script 衍生 SQL **直接帶 taxonomy_id**;harvest 之遷移 SQL 降級為冪等補漏(每次 expansion 重跑後可安全重放)。
2. **domain slug 公式=兩計畫共同契約(修縫隙 B)**:query.domain 之 field slug 公式 `lower(replace(replace(f.name,' ','_'),',',''))` 為 SSOT(住 expansion script);harvest 的 `knowledge_domain_map` 種子**一律 `SELECT DISTINCT domain FROM knowledge_query` 資料驅動生成**(恆等列預設、含手動 14 域),再人工 UPDATE 特定對映(materials_science→energy_materials 等)——不手打 26 slug、公式改動自動跟隨。
3. **harvest 先決=僅 P1**(分類樹,已完成);P2 re3data 目錄列 enabled=false 不在 harvest 排程,非先決。

## 九、執行狀態與計畫↔程式待同步清單(v1.1,2026-07-02)

- **執行狀態**:P1 已完成(taxonomy 4,798、query 4,706)、P2 re3data 背景執行中、P3/P4 已完成;本計畫角色轉為**記錄+重跑依據**(script 冪等可重跑)。
- **待同步(執行層 TODO,harvest 建 taxonomy_id 欄後做)**:
  1. `expand_knowledge_registry.py` P1 衍生 SQL 改直寫 `taxonomy_id`(§八契約 1;現行寫 note,harvest 遷移 SQL 補漏中)
  2. 同 script 補 `--skip-taxonomy` 選項(P2 單獨重跑用,免重打 OpenAlex)

## 十、v1.2 修訂(五鏡對抗審查 confirmed 修復,2026-07-02)

1. **P3 宣稱失實更正(#15)**:計畫原列「~20 大獎項類別」,實作 `AWARDS` 僅 **12 類**、DB 亦 12 列——§九「P3 已完成」更正為「P3 完成 12/目標 20;差集 8 類(諾獎化學/物理/生醫已由域源覆蓋,其餘如 Lasker/Copley 已列程式)待補跑」。
2. **P2 文件補正**:實程式寫入欄含 `entity_type='work'`/`domain='general'`(文件原漏列);**已知侷限誠實記**:repo 明細 HTTP 抓取失敗時仍 INSERT 空 metadata 目錄列(key/name 有效、subject/api 空),fail 計數僅含 XML ParseError 不含 HTTP-None——修正列入待同步 TODO。
3. **未拍板域治理(重要)**:P1 衍生之 4,516 詞含**未經決策層拍板之域**(medicine/nursing/dentistry/arts 等 16 field)——治理閘=harvest `knowledge_domain_map` **僅拍板域建列**(未拍板 field 無對映列 → INNER JOIN 天然排除出排程並印統計);**未拍板域之啟用=決策層 INSERT**(呼應憲章 v1.19.0「新領域入庫=人拍板」)。taxonomy/query 表保留全集(目錄無害、排程有閘)。
4. 待同步 TODO 增:③ re3data HTTP-None 列處置(補抓或標 note)④ 獎項差集 8 類補跑。
