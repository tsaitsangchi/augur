# 策展映射禁 hardcode → PostgreSQL SSOT ＋ 入憲計畫

**日期**：2026-07-28（同日補強：**know-how 產生**覆蓋＋A0 探針）  
**性質**：[I] 執行層計畫（plan-first；CLAUDE #16／#20）  
**Steward 拍板（2026-07-28）**：✅ **`NHC-PLAN`＋`NHC-S12`＋`FZ-keep`**（登錄＝`audits/NHC-PLAN-APPROVED-20260728.md`；收官＝`audits/NHC-S12-CLOSED-20260728.md`）
**Steward 開跑（2026-07-29）**：✅ **`NHC-S3`＋`FZ-keep`**（「所有 working 開始跑」；收官＝`audits/NHC-S3-CLOSED-20260729.md`）
**未拍**：`NHC-CONSTITUTE`（**禁止改 [N]**）
**觸發**：Steward——(1) `_GLOSSARY` 類 CJK→EN 檢索詞硬編碼；(2)「此專案所有程式都不能 hard code，都需進 PostgreSQL 17 table」；(3) **請入憲**；(4) 優化已 hardcode 程式（遷 DB＋改讀表）；(5) **同日補充**：know-how **產生**不要 hard code——例「第一性原理在太陽能材料研發如何應用？」應由**一般機制＋DB 策展／檢索**作答，禁寫死詞表／領域模板／Q&A  
**姊妹互鏈**：
- `reports/augur_knowhow_cross_domain_advisor_plan_20260728.md`（KH-XDOM；S01 **CLOSED**——跨域檢索／去作答閘；本計畫落地其「query 擴展＝DB、禁硬編碼大表」＋**組答不得再 hardcode 領域分支**）
- `reports/augur_pme_cross_domain_evolution_enable_plan_20260728.md`（PME-XDOM；已拍 YES＋**僅** `SUNZI-MGMT` 文獻橋——**異域進化灌因子**與顧問產生正交；太陽能材料題**不**因此開 `PME-XDOM-SOLAR`）
- `reports/augur_knowledge_fulltext_coverage_plan_20260728.md`（FT-COV——終態覆蓋；產生 consumable 語料）  
**實證時點**：2026-07-28 code 親查＋S12 apply（`retrieve_glossary` active=13）

---

## 0. 一句結論＋本輪邊界

| | |
|---|---|
| **結論** | Steward 定錨＝**策展的、會增減、決定行為的資料性映射／詞表／別名 → 住 PostgreSQL；禁 Python／JSON 當 SSOT**。首要標的＝`query_translation._GLOSSARY`→`retrieve_glossary`。**擴充定錨（同日）**：know-how **產生**＝一般管線（跨域檢索＋LLM 組答＋DB 原則／map／別名／glossary）——**禁止**為單一領域（太陽能／第一性原理…）寫死 Q&A、prompt 分支、詞表專用 if。 |
| **S12 已做** | DDL＋13 種子＋`query_translation` 讀表；A0 四探針驗收尺；predict FORBIDDEN；advisor 重啟 |
| **仍不做（本輪）** | 改憲章 [N]（無 `NHC-CONSTITUTE`）；為探針加領域 hardcode |
| **非目標** | 解凍 FinMind／FRED；預測熱路徑吃 glossary；把「所有字面量」解讀成禁常數／禁 regex／禁演算法閾值；把顧問產生題誤開成 PME 太陽能灌因子 |

**建議原則表述（入憲草案要旨）**：  
> 凡策展的、會增減、決定行為的資料性映射／詞表／別名／分類對照 → 住 PostgreSQL；runtime 只讀表；新增＝admin INSERT、零改碼。Python／repo JSON 僅得作一次性 bootstrap 種子，不得為 runtime SSOT。know-how **產生**（顧問組答）不得以領域專用 hardcode 模板／Q&A 取代「DB 策展＋統一檢索＋LLM」。邏輯／安全閘詞表若憲章已裁「執行層、安全繫於機械閘」→ 明示豁免清單（見 §2）。

---

## 0.5 A0 探針診斷（短；2026-07-28）

**A0／S12 驗收探針清單**（與漿料組句回歸並存；**禁**為任一題加 code 專支）：

| ID | 探針句 |
|---|---|
| **A0-app** | 第一性原理在太陽能材料研發如何應用？ |
| **A0-core** | 依第一性原理列出在太陽能材料研發技術核心？ |
| **A0-phys** | 依第一性原理列出在太陽能材料研發物理學技術核心？ |
| **A0-chem** | 依第一性原理列出在太陽能材料研發在化學上技術核心？ |

| 軸 | 現況（S12 後） | 判讀 |
|---|---|---|
| **glossary 命中** | 四探針 `_glossary_en_query` → **None**（表無「第一性原理／太陽能材料」列） | 不走詞表路徑；**不得**靠加死詞「修」產生；可選日後 **INSERT** 擴詞零改碼 |
| **產生路徑** | 統一 `advise`：CJK 檢索 →（可）LLM `translate_for_retrieval` → EN 檢索 → relevance → prompt＋guard | 化學／物理／材料／應用變體**同一路徑**；差在 DB 語料命中，不靠 if-domain |
| **S12 驗收** | 翻譯／組答路徑**不崩**；模組無 `_GLOSSARY`；repo **無**太陽能／第一性／物理／化學專用組答分支 | 答案深度＝語料／原則策展（FT-COV／harvest），缺料→誠實 decline |
---

## 1. What／Why／非目標

### 1.1 What

1. **覆蓋範圍釐清**（避免「所有字面量」過度解釋）——§2。  
2. **硬編碼清冊**（檔:行＋類型＋處置）——§3。  
3. **PG17 表設計**（首推新表 `retrieve_glossary`；不擴 `knowledge_topic_alias` 混職責）——§4。  
4. **改碼範圍**（S2：`query_translation` 讀表；S3：其餘必遷項）——§5–6。  
5. **入憲草案落點**（第一部 PG 系統記錄＋知識層表 roster；CLAUDE #29b／原則精華交叉對齊在 S4）——§7。  
6. **分階＋驗收＋拍板碼**（入憲採納 ≠ 開 S1–S2）——§8–10。  
7. **know-how 產生軸（同日補強）**——覆蓋三入口，皆走「一般機制＋DB」，禁領域 hardcode：  
   | 入口 | 一般機制 | DB 策展（SSOT） | 禁 |
   |---|---|---|---|
   | **query 擴展** | `translate_for_retrieval`（詞表∨LLM） | `retrieve_glossary`；可選 `knowledge_topic_alias` | 寫死漿料／太陽能／第一性原理大表於 `.py` |
   | **顧問組答** | `advise`：跨域 hybrid／RRF → relevance → prompt → guard（KH-XDOM） | 可答語料＝item／sentence／embed／`philosophy_principle`／`principle_domain_map`（人撰注記） | `if "太陽能" in q` 專用模板／寫死 Q&A／領域 prompt 分支 |
   | **原則／map 策展** | admin／腳本 INSERT；PME 另鏈 | `philosophy_principle`＋`principle_factor_map`＋`principle_domain_map` | AI 造原則；顧問產生題順便灌預測因子 |

### 1.2 Why

- **實證痛點**：`advise()` CJK 問句（如「太陽能電池導電漿料」）靠 `_GLOSSARY` 組英文檢索；詞表寫死在 code → 增漿料／半導體術語須改碼＋重部署，違 #29b「策展映射住 DB」。  
- **產生痛點（同日）**：跨域／方法論題（第一性原理×太陽能材料）若靠寫死詞表或領域模板「補洞」，會把 know-how 產生鎖死在 code——與「一般機制＋DB 策展」對立；正確槓桿＝INSERT glossary／harvest query／終態覆蓋＋統一 `advise`。  
- **現行註解過期**：`query_translation.py:40` 自稱「執行層品質工程、非 #29b 資料鎖」——與 Steward 本輪定錨**衝突**；應改歸 **資料側**（安全仍繫於 relevance＋guard，詞表本身＝策展映射）。  
- **既有先例已證路徑**：`knowledge_topic_alias`（TOPIC_ALIAS 遷庫）、`knowledge_domain_map`（DOMAIN_MAP_OVERRIDES 種子）、`judgestop_threshold`、`principle_domain_map`——同一 #29b 模式。  
- **跨域計畫依賴**：KH-XDOM §3.1「query 擴展：DB 別名、禁硬編碼大表」——無 `retrieve_glossary` 則跨域漿料×材料題仍卡死在 code 詞表；產生軸與 KH-XDOM 組答**同一出口**（`advise`），NHC 不另造編排器。

### 1.3 非目標（硬紅線）

| 不做 | 理由 |
|---|---|
| 解凍 FinMind／FRED／市場 sync | API 凍結；本計畫零市場 API |
| 預測熱路徑 import glossary／knowledge | `import_isolation`；素養↔預測正交 |
| 把 `safe_general`／`relevance._EN_GENERIC`／guard 正則遷 DB | 憲章 v1.35.0 已裁「詞表不鎖＝執行層、安全繫於 guard」 |
| 把演算法常數／超時／模型 tag／prompt 全文當「資料」遷庫 | 邏輯／設定，非策展映射 |
| 本輪改 [N] 或 apply DDL | 須分離拍板碼 |
| 為 A0 探針新增太陽能／第一性原理 **code 分支／死 Q&A** | 違產生軸定錨；改 INSERT／harvest／FT-COV |
| 因顧問產生題開通 `PME-XDOM-SOLAR` | PME 近程僅已拍 `SUNZI-MGMT`；產生≠進化灌因子 |

---

## 2. 覆蓋範圍（資料 vs 邏輯／豁免）——必讀

**判準（對齊 CLAUDE #29b 既有句）**：  
「這是資料（策展、會增減、可外部產生／admin INSERT）還是邏輯（演算法／型別／流程／安全閘）？」

| 類 | 定義 | 例子 | 處置 |
|---|---|---|---|
| **A. 資料性映射（本原則覆蓋）** | 策展詞對／別名／domain 對照／主題清單；增減改變檢索或管線行為；非安全閘本體 | `_GLOSSARY`、`knowledge_topic_alias`、`knowledge_domain_map`、distill 策展題表；**未來**為 A0 探針可 INSERT 之「第一性原理→first principles」「太陽能材料→solar materials」等列（**表內策展，非 code**） | **住 PG**；runtime 讀表 |
| **A′. know-how 產生行為（本原則覆蓋·禁 hardcode 形態）** | 組答／擴展／策展入口的**行為資料**須 DB 或統一管線；領域差異只反映在列與語料 | 跨域題靠 `advise`＋語料；原則注記靠 `principle_domain_map` | **禁**領域專用 Q&A／模板／if-domain 分支當「產生」 |
| **B. Bootstrap 種子（允許在 code／migrate）** | 一次性 INSERT；之後 SSOT＝DB | `migrate_topic_alias_ddl.SEED`、`DOMAIN_MAP_OVERRIDES` | 維持；禁 runtime 再讀 code dict 當權威 |
| **C. 邏輯／安全閘詞表（明示豁免）** | 安全繫於機械閘、非資料鎖；憲章已裁執行層 | `safe_general` B/A 詞表、`relevance._EN_GENERIC`／`_STOP`、`guard` 正則、`LICENSE_WHITELIST`／`SOURCE_TYPE_WHITELIST`（封閉枚舉＋DB CHECK 同步） | **留 code**；擴充＝改碼＋（若有）CHECK 同步，**不**假稱 #29b 違規 |
| **D. 演算法／運維常數（豁免）** | 閾值、超時、視窗、型別 FORCE 集、物理分類後備 | `RELEVANCE_FLOOR`、`_MAX_LEN`、`FORCE_STR`、`INTRADAY` fail-safe 後備 | 留 code；**operational 閾值**若已走 #29b（如 `judgestop_threshold`／`risk_policy`）則維持 DB |
| **E. 設定／機密** | `.env`、Ollama URL／model tag | `OLLAMA_TRANSLATE_MODEL` | 非資料；不入本原則 |

**Steward「所有程式都不能 hard code」之正式解讀（建議入憲消歧）**：  
＝**禁止以 Python／JSON 作為策展映射之 runtime SSOT**；**≠**禁止程式內出現任何字串／數字字面量。過度解釋會迫遷安全閘詞表、破壞 v1.35.0 豁免與離線自測零 IO 契約。

---

## 3. 硬編碼清冊（S0）

### 3.1 本輪首要（A 類 · retrieve）

| ID | 檔:行 | 符號 | 類型 | 現況 | 處置 |
|---|---|---|---|---|---|
| **G1** | `src/augur/advisor/query_translation.py:41-55` | `_GLOSSARY` | CJK→EN 檢索詞表（長詞優先；`漿料` 過寬須共現） | **runtime hardcode**；docstring 誤標非 #29b | **S1 種子 → S2 改讀 `retrieve_glossary`** |
| G1-call | `src/augur/advisor/advise.py:~181` | `translate_for_retrieval` | 消費端 | 間接 | S2 後自動受益；可選接 DB 別名擴展（互鏈 KH-XDOM） |
| **G-A0** | （行為·非單檔） | A0 探針組答 | 產生軸 | 見 §0.5：詞表未命中；無領域分支 | **S2／U 驗收**：機制可答或誠實 decline；**禁止**為探針加 code 專支；缺口用 INSERT glossary／harvest／FT-COV |

**G1 現行詞對（種子來源＝code 親查；S1 bootstrap＝此 13 列）**：

> **A0 可選後續 INSERT（非 S1 必種、禁預寫進 `.py` 常數）**：`第一性原理→first principles`、`第一性原理思考→first principles thinking`、`太陽能材料→solar materials`、`太陽能→solar`（若採納須設 `require_cooccur` 或夠長片語，避免過寬）——僅 admin／migrate 補列於 `retrieve_glossary`，證明「零改碼加詞」。

| src_cjk | tgt_en | require_cooccur | 備註 |
|---|---|---|---|
| 導電漿料 | conductive paste | false | |
| 正面銀漿 | front silver paste | false | |
| 背面鋁漿 | rear aluminum paste | false | |
| 銀漿 | silver paste | false | |
| 鋁漿 | aluminum paste | false | |
| 金屬化 | metallization | false | |
| 太陽能電池 | solar cell | false | |
| 多主柵 | multi busbar | false | |
| 鈣鈦礦 | perovskite | false | |
| 光伏 | photovoltaic | false | |
| 半導體 | semiconductor | false | |
| 矽晶 | silicon wafer | false | |
| 漿料 | paste | **true** | 裸命中且僅此詞 → 不開英文檢索（現行 `ens == ["paste"]`） |

### 3.2 已符 #29b（B 類 · 維持／複驗）

| ID | 檔:行 | 符號／表 | 類型 | 判讀 |
|---|---|---|---|---|
| T1 | `scripts/migrate_topic_alias_ddl.py`＋`acquire_topic.py:31+` | `knowledge_topic_alias` | 主題→domain ILIKE | **已遷**；SEED 僅 bootstrap |
| D1 | `scripts/harvest_knowledge.py:41`＋`knowledge_domain_map` | `DOMAIN_MAP_OVERRIDES` | OpenAlex field→augur domain | **bootstrap-seed 豁免**（runtime SSOT＝DB；07-13 裁定維持） |
| P1 | `scripts/migrate_principle_domain_map_ddl.py` | `principle_domain_map` | 原理×應用域 | 已 DDL；列為人撰 |
| J1 | `judgestop_threshold` 等 | operational 閾值 | 已 #29b 先例 | 維持 |

### 3.3 待裁／次優先遷徙（A 或 borderline · S3）

| ID | 檔:行 | 符號 | 類型 | 建議 |
|---|---|---|---|---|
| Q1 | `scripts/advisor_distill_generate_questions.py:36-66` | `_OOC_TOPICS` | 策展 OOC 主題清單 | 可建 `advisor_distill_seed_topic`（07-13 附錄 B 待裁；綁蒸餾重啟） |
| Q2 | 同檔 `:70+` | `_IMPOSSIBLE_TOPICS` | 拒答誘導題 | 同上或測資豁免（偏測試金標） |
| A1 | `scripts/expand_knowledge_registry.py:107` | `AWARDS` | 獎項清單種子 | 低優先；可維持 bootstrap |
| C1 | `src/augur/catalog/__init__.py:199+` | `_DEDICATED_URL` 等 | catalog build 策展註記 | 07-13 裁定 3 維持結案；非本輪 |
| I1 | `src/augur/ingestion/ingest.py:65` | `_AGGREGATE_DAILY` | 聚合映射種子 | DB-first 過渡已做；欄 migrate 另帳 |
| L1 | `scripts/fetch_oa_fulltext.py:43-46` | `LICENSE_MAP` | Unpaywall→三軌 license 別名 | **偏邏輯／封閉枚舉對映**；建議豁免或極小靜態表（與 LICENSE_WHITELIST 同命運） |

### 3.4 明示豁免（C／D 類 · 不遷）

| ID | 檔:行 | 符號 | 理由 |
|---|---|---|---|
| X1 | `src/augur/advisor/safe_general.py:25-76` | `_B_CONCEPTS`／A 類正則 | 憲章 v1.35.0「詞表不鎖＝執行層」 |
| X2 | `src/augur/advisor/relevance.py:49-73` | `_STOP`／`_EN_GENERIC` | 同；機械相關度閘 |
| X3 | `src/augur/advisor/guard.py` | 五閘正則／閉集句 | 安全閘本體 |
| X4 | `src/augur/knowledge/corpus.py:21` | `LICENSE_WHITELIST` | 封閉枚舉＋DB CHECK；#19 三側同步 |
| X5 | `src/augur/knowledge/admission.py:31` | `SOURCE_TYPE_WHITELIST` | 同上 |
| X6 | 型別／物理分類後備 | `FORCE_*`、`INTRADAY` seed | 邏輯／fail-safe；非策展別名 |

### 3.5 清冊摘要（給拍板）

- **Clear 違規（須遷）**：**1 件**——`_GLOSSARY`（G1）。  
- **已 DB-SSOT**：**≥4 件**（topic_alias／domain_map／principle_domain_map／多個 threshold）。  
- **Borderline／S3**：**~6 件**（distill 題表、AWARDS、catalog 註記殘、aggregate 過渡、LICENSE_MAP）。  
- **豁免**：**≥6 件**（safe_general／relevance／guard／license／source_type／型別常數）。

---

## 4. Schema（PG17）— `retrieve_glossary`

### 4.1 為何新表、不擴 `knowledge_topic_alias`

| | `knowledge_topic_alias` | `retrieve_glossary` |
|---|---|---|
| 用途 | 使用者主題詞 → `knowledge_query.domain` ILIKE（**harvest／acquire 圈選**） | CJK 片語 → 英文檢索 token（**retrieve query 擴展**） |
| 消費端 | `acquire_topic.py` | `query_translation._glossary_en_query` → `advise` |
| 值語意 | domain 樣式 | 英文詞組 |
| 共現規則 | 無 | 有（過寬詞 `require_cooccur`） |

混表會污染 FK 語意與 admin UI；**兩表並存、同屬 #29b**。

### 4.2 DDL（計畫完整性；未 apply）

```sql
-- PostgreSQL 17；冪等建表建議住 scripts/migrate_retrieve_glossary_ddl.py（拍板後新增）
CREATE TABLE IF NOT EXISTS retrieve_glossary (
    glossary_id      BIGSERIAL PRIMARY KEY,
    src_cjk          TEXT NOT NULL,              -- 源中文／CJK 片語（檢索匹配用）
    tgt_en           TEXT NOT NULL,              -- 目標英文檢索片段
    priority         INT  NOT NULL DEFAULT 0,    -- 越大越先；亦可由 length(src_cjk) 衍生，兩者取 max
    require_cooccur  BOOLEAN NOT NULL DEFAULT FALSE,
      -- TRUE：僅當同 query 另有其他 active 命中時才採用本列
      -- （對齊現行「裸漿料 → None」）
    active           BOOLEAN NOT NULL DEFAULT TRUE,
    provenance       TEXT,                       -- 來源註記（steward_seed_20260728／admin／…）
    note             TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (src_cjk, tgt_en)
);

CREATE INDEX IF NOT EXISTS idx_retrieve_glossary_active_prio
  ON retrieve_glossary (active, priority DESC, char_length(src_cjk) DESC)
  WHERE active;

COMMENT ON TABLE retrieve_glossary IS
  'CJK→EN 檢索詞表(#29b；runtime query_translation 讀表；只服務 retrieve query；非 citation／非答案／非 guard 輸入)';
```

**演算法不變式（遷庫後仍由 code 執行，規則非資料）**：

1. 只載 `active=true`。  
2. 排序：`ORDER BY priority DESC, char_length(src_cjk) DESC`（長詞優先；與現行 `sorted(..., -len)` 等價並可人工抬 priority）。  
3. 子字串覆蓋：較短 `src_cjk` 若已被較長命中包含 → skip（現行 `漿料⊂導電漿料`）。  
4. `require_cooccur=true` 之列：若本輪唯一命中集合 ⊆ 該類列 → 回 `None`（現行裸「漿料」）。  
5. 組句：命中之 `tgt_en` 以空白 join；失敗 fail-closed → 走 qwen3:4b 或 `None`。

### 4.3 種子列（G1 全量＋provenance）

遷移腳本 `SEED`＝上表 13 列；`漿料` 列 `require_cooccur=TRUE`；其餘 `FALSE`；`provenance='steward_seed_20260728'`；`priority=0`（依賴字長排序即可）。

### 4.4 可選後續欄（本輪不建）

- `domain_hint`：跨域評測標籤（非 filter）——等 KH-XDOM S2 需要再加。  
- `locale`：若將來非 zh→en。

---

## 5. Python／遷移／改碼範圍

| 階段 | 檔 | 角色 |
|---|---|---|
| S1 | **新** `scripts/migrate_retrieve_glossary_ddl.py` | `--check`／`--apply`／`--show`／`--selftest`；冪等 DDL＋SEED；無參數印矩陣（#29） |
| S2 | `src/augur/advisor/query_translation.py` | 刪 runtime `_GLOSSARY`；`_load_glossary(conn|cache)` 讀表；lru_cache 進程快取＋可選 TTL／`reload`；**零 IO selftest**：注入假列 fixture，不強制 live DB |
| S2 | `scripts/setup_predict_role.py`（若有 knowledge 只讀白名單） | 確認 predict role **不**需此表；advisor／app role SELECT |
| S2 | 測試 | 既有詞表自測綠；加「表空→全走 LLM／None」「漿料共現」 |
| S3 | distill／其餘 A 類 | 各建表或結案豁免；逐件拍板 |
| S4 | `docs/系統架構大憲章_*.md`、CLAUDE #29b、原則精華交叉引用、GOVERNANCE-MAP／CS | **僅在「入憲採納」碼後** |

**本輪可選工件**：計畫內 DDL 已足夠；**不**預建 `migrate_*` 於 repo（避免未拍板半套）。若 Steward 要「草稿腳本未 apply」——開 S1 時一次落地即可。

---

## 6. 分階段

| 階段 | 名稱 | 內容 | 依賴 | 驗收摘要 |
|---|---|---|---|---|
| **S0** | 清冊 | 本報告 §3；可複驗 Grep | 無 | 清冊與 code 一致 |
| **S1** | DDL＋種子 | `retrieve_glossary` 建表＋13 列漿料／光伏種子 | S0；**開碼** | `\d`＋`SELECT count(*)=13`；`--show` 列齊 |
| **S2** | retrieve 讀表 | `query_translation` 改讀 DB；刪 runtime hardcode；自測綠 | S1 | 「太陽能電池導電漿料」→ 同現行英文組句；裸漿料→None；無改碼可 INSERT 新詞；**A0**：repo diff **無**太陽能／第一性原理專用分支 |
| **S3** | 其餘 hardcode | §3.3 逐件遷或結案豁免 | S2；逐件碼 | 無殘留 A 類 clear 違規 |
| **S4** | 入憲＋工具層對齊 | [N] 草案寫入＋CLAUDE #29b 明示 glossary＋**產生禁領域 hardcode**＋豁免清單；原則精華交叉 | **入憲採納碼** | 憲章升版＋CS；lint／合規聲明 |
| **U** | 凍結回歸＋產生探針 | 與 KH-XDOM 聯測（漿料題＋**A0 第一性×太陽能材料**）；isolation 綠；FZ-keep；PME 仍僅 SUNZI-MGMT | S2+；KH-XDOM S01 已 CLOSED | 跨域題可擴詞不改碼；A0 走統一 `advise`（可答或誠實 decline，皆可接受若無幻造） |

**建議近程一次開實作**：`NHC-S12`＝S1＋S2（極小、對齊 Steward「優化 hardcode」最強痛點）。S3／S4 分離。A0 探針屬 **S2／U 驗收尺**，非另開實作階段。

---

## 7. 憲章修訂草案（待拍 · 未寫入 [N]）

### 7.1 建議落點

| 落點 | 動作 | 理由 |
|---|---|---|
| **第一部「資料本質：PostgreSQL＝唯一系統記錄」**（現行 v1.26.0 總綱） | **補子條**「策展映射 SSOT」 | 與「設定與程式碼不承載資料」同節收斂；升版非新原則編號 |
| **第三部 philosophy／知識層「知識層多域擴充準則」** | **表 roster 加** `retrieve_glossary`；一句職責 | 與 `knowledge_topic_alias`／`knowledge_domain_map` 並列 |
| **第二部防幻覺／safe_general（v1.35.0）** | **不改判準**；交叉一句「retrieve glossary ≠ safe_general 豁免類」 | 防誤把 G1 繼續當品質工程豁免 |
| **CLAUDE #29b**（L6／[I]） | S4 同步：明示 retrieve_glossary；修正「僅 topic_alias」舉例；列豁免清單 | 工具層與 [N] 對齊 |
| **原則精華** | 第 5 行交叉引用憲章升版即可（非新可違反原則） | 同 v1.26／v1.47 前例 |

### 7.2 草案條文（可貼入憲章之候選正文）

> **策展映射住 PostgreSQL（curated-mapping SSOT）〔草案 · 待 Steward `NHC-CONSTITUTE`〕**  
> 凡**策展的、會增減、決定 runtime 行為**之資料性映射／詞表／別名／分類對照（含但不限：主題→domain 別名、OpenAlex field→augur domain、**CJK→EN 檢索詞表 `retrieve_glossary`**、原理×應用域注記），其 **runtime SSOT＝本地 PostgreSQL**；新增或調整＝決策層／admin **INSERT／UPDATE 表列**、**零改碼**。Python dict／tuple／repo JSON **不得**作為上述映射之 runtime 權威；僅允許遷移腳本內之**一次性 bootstrap 種子**（種子寫入後以 DB 為準）。  
> **know-how 產生**：顧問／素養組答須經**統一檢索＋組答管線**消費上列 DB 策展與可答語料；**禁止**以領域專用 hardcode 詞表、Q&A、或 prompt／控制流分支代替策展列與一般機制（例：不得為「第一性原理×太陽能材料」另寫死答案路徑）。  
> **明示豁免（執行層／邏輯側）**：安全繫於機械閘、憲章已裁「詞表不鎖」者——含 `advisor.safe_general` 通識白名單、`relevance` 泛用停詞、`guard` 正則與誠實閉集、全文／來源 **封閉枚舉白名單**（`LICENSE_WHITELIST`／`SOURCE_TYPE_WHITELIST` 與 DB CHECK 同步）、以及純演算法常數／型別 FORCE 集／運維超時。豁免項之擴充仍受既有治權（三敵、§8.2）約束，**不得**藉豁免回寫策展大表於 code。  
> **邊界**：本條從屬第一部 PostgreSQL 系統記錄與 CLAUDE #29b；**不解凍**市場 API；**不**使 know-how／glossary 進入預測熱路徑；顧問產生 **≠** 異域 PME 灌因子（後者另受 PME-XDOM 拍板範圍約束）。

### 7.3 修訂歷程列（升版時）

| 版本 | 日期 | 摘要 | 狀態 |
|---|---|---|---|
| v1.48.0（建議） | （拍板日） | 第一部補策展映射 SSOT＋know-how 產生禁領域 hardcode；知識層表加 `retrieve_glossary`；消歧 ≠ safe_general 豁免 | **DRAFT** |

---

## 8. 與 KH-XDOM／PME-XDOM 之關係（產生軸）

**產生等式（定錨）**：  
**know-how 產生** ＝ **跨域檢索（KH-XDOM）** ＋ **LLM 組答（統一 `advise`）** ＋ **DB 原則／map／glossary／語料策展**  
**≠** 再 hardcode 太陽能（或任一領域）專用分支  
**≠** 異域進化灌因子（PME；近程僅已拍 **SUNZI-MGMT**）

| | 本計畫（NHC） | KH-XDOM（20260728） | PME-XDOM（20260728） |
|---|---|---|---|
| 職責 | 策展映射 SSOT（glossary 等）入 DB／入憲；**禁產生 hardcode** | 跨域**讀與答**；去作答 `domain=` 閘；ATA 終態 | 異域概念→**investment** 假說→map→閘 |
| 共同痛點 | 漿料／光伏 CJK 詞仍 code；產生易被誤修成死模板 | 孫子×企管、漿料×材料、**第一性×太陽能材料（A0）** | 孫子×企管文獻橋（首條） |
| 接線 | `retrieve_glossary`→`translate_for_retrieval`；A0＝S2／U 尺 | §3.1 query 擴展「DB、禁硬編碼大表」；S01 **CLOSED** | `philosophy_principle`／map；**不含**顧問 Q&A |
| 依賴 | NHC S2 → 加詞不改碼 | 組答消費 NHC 詞表＋FT-COV 終態 | **不**依賴 NHC glossary；不因 A0 開 SOLAR |
| 正交 | 不碰 approve 唯人；不開 PME-SOLAR | 同；產生≠進化 | 灌因子僅 `SUNZI-MGMT`；太陽能材料＝次條候選另碼 |
| 拍板 | ✅ `NHC-PLAN`＋`NHC-S12`＋`NHC-S3`＋`FZ-keep`；**待** `NHC-CONSTITUTE` | 已拍 PLAN＋S01 | 已拍 YES＋SUNZI-MGMT |

**一句**：跨域要「答得出」＝終態＋去閘＋**可擴檢索詞**＋統一組答；NHC 專責詞表／映射入 DB 與「產生不 hardcode」入憲草案；KH-XDOM 專責檢索空間；PME 專責已拍範圍之假說鏈——三軸勿混。

---

## 9. 驗收

| ID | 條件 | 否證 |
|---|---|---|
| V-S0 | 清冊 G1／豁免／已 DB 與 repo 一致 | 漏列 clear `_GLOSSARY` |
| V-S1 | 表存在；種子 13 列；`漿料.require_cooccur=true` | 只建空表 |
| V-S2 | runtime 無 `_GLOSSARY` 常數；讀表結果與遷前組句等價；INSERT 新詞免改碼 | 仍 `from _GLOSSARY` |
| V-S2b | `--selftest` 零外部可綠（fixture）；live 路徑可另測 | selftest 強制連 DB 且無 fixture |
| **V-A0** | 探針「第一性原理在太陽能材料研發如何應用？」走統一 `advise`；S2 diff **無**該題／該域專用 hardcode；可選 INSERT glossary 後擴詞**零改碼**；可答或誠實 decline 皆可（禁幻造） | 為探針新增 `if`／Q&A／領域 prompt 分支；或把 `reports/` 研究檔當 citation 權威灌進答案 |
| **V-GEN** | 文件與實作維持產生等式（§8）；無太陽能專用組答模組 | 「產生」＝新 hardcode 模板宣稱完成 |
| V-SCOPE | 文件明示豁免清單；未誤遷 safe_general | 把 B 概念表搬進 PG 當本原則「完成」 |
| V-CONST | 僅在 `NHC-CONSTITUTE` 後改 [N] | 未拍板改憲章 |
| V-FZ | 零 FinMind／FRED | 借機 sync |
| V-ISO | predict 不 import glossary | isolation 紅 |
| V-PME | A0／NHC 實作**不**觸發 `PME-XDOM-SOLAR` 或未拍異域 map | 顧問題順便灌預測因子 |

---

## 10. Steward 拍板碼（分離）

| 碼 | 含義 | 建議 |
|---|---|---|
| **`NHC-PLAN`** | 採納本計畫 what／§0.5 A0／§2 覆蓋（含產生軸）／清冊／分階／非目標／§8 互鏈 | **必拍** |
| **`NHC-S12`** | 開工 S1＋S2（DDL＋種子＋`query_translation` 讀表；A0＝驗收尺非另開支） | **近程建議**（對齊「優化 hardcode」＋產生不 hardcode） |
| **`NHC-S3`** | 開工其餘 A 類遷徙（逐件或整包） | 次拍 |
| **`NHC-CONSTITUTE`** | **入憲採納**：將 §7.2（含產生句）寫入憲章正文並升版＋S4 工具層對齊 | **與 S12 分離**；可晚於實作驗收 |
| **`FZ-keep`** | 市場 API 維持凍結 | 預設附帶 |
| **（PME 範圍）** | 異域灌因子仍僅已拍 `PME-XDOM-SUNZI-MGMT`；A0 **不**暗示 `PME-XDOM-SOLAR` | 附帶確認即可（無需重拍 YES） |

**建議合併拍板句（示意）**：  
`NHC-PLAN`＋`NHC-S12`＋`FZ-keep`（實作先跑；A0＝S2／U 驗收探針）。  
入憲另句（可同日或驗收後）：`NHC-CONSTITUTE`（**碼面分離**；含 §7.2 產生禁 hardcode）。  

**一行可複製**：  
`NHC-PLAN`＋`NHC-S12`＋`FZ-keep`（±另句 `NHC-CONSTITUTE`）

**禁止解讀**：單獨說「入憲」≠授權改 [N] 檔案——須見 **`NHC-CONSTITUTE`** 或等價明示「採納並寫入憲章」。  
**本輪狀態**：已拍／開跑 `NHC-PLAN`＋`NHC-S12`＋`NHC-S3`＋`FZ-keep`；**未拍** `NHC-CONSTITUTE`。

---

## 11. 風險

| 風險 | 緩解 |
|---|---|
| 過度解釋「禁一切 hardcode」 | §2 覆蓋範圍入憲消歧；豁免清單 |
| S2 讀表破壞零 IO selftest | fixture 注入；DB 路徑與純函式分離 |
| 表空／連線失敗拖垮顧問 | fail-closed：空表→跳過詞表走 LLM／None（同現行未命中） |
| 與 topic_alias 混淆 | 兩表職責表 §4.1；admin 文件分開 |
| 未拍板改 [N] | 無 `NHC-CONSTITUTE` 則機械上不碰 `docs/系統架構大憲章_*.md` |
| 用 hardcode「修好」A0 探針 | V-A0／V-GEN；缺口走 INSERT／FT-COV／harvest |
| 顧問產生與 PME 灌因子混談 | §8 等式；V-PME；近程僅 SUNZI-MGMT |

---

## 12. 本輪交付物清單

| 交付 | 路徑／狀態 |
|---|---|
| 本計畫（含產生軸＋A0×4） | `reports/augur_no_hardcode_db_ssot_constitution_plan_20260728.md`（**本檔**） |
| 拍板／CLOSED | `audits/NHC-PLAN-APPROVED-20260728.md`／`audits/NHC-S12-CLOSED-20260728.md` |
| DDL／種子 | `scripts/migrate_retrieve_glossary_ddl.py`（**已 apply**；active=13） |
| 改碼 | `query_translation` 讀表；`setup_predict_role` FORBIDDEN |
| 憲章草案 | §7.2（**未寫入 [N]**；待 `NHC-CONSTITUTE`） |
| S3 | ✅ CLOSED（2026-07-29；`audits/NHC-S3-CLOSED-20260729.md`） |

---

## 13. 修訂紀要（本檔 [I]）

| 日 | 摘要 |
|---|---|
| 2026-07-28 | 初版：G1→`retrieve_glossary`；清冊；入憲草案；拍板碼 |
| 2026-07-28（同日） | 補強 know-how **產生**覆蓋；A0 探針診斷；互鏈 KH-XDOM／PME |
| 2026-07-28（S12） | 拍板執行 CLOSED；A0 擴為 app／core／phys／chem 四探針；標待 NHC-S3／NHC-CONSTITUTE |
| 2026-07-29（S3） | 「所有 working 開始跑」＝開 NHC-S3＋FZ-keep；Q1/Q2 遷 DB；A1/C1/L1 豁免；I1 欄交棒；**待** NHC-CONSTITUTE |

---

*位階：[I] 計畫。S12 已執行；入憲仍待 `NHC-CONSTITUTE`。治理原文仍以憲章 [N] 與 constitution-mcp 為準。*
