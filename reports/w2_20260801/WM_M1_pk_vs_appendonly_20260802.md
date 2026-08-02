# [DRAFT 呈案] WM.36 M1 殘項｜`world_concept_registry` 之 PK × append-only 互斥——三案與定案時點

> **[DRAFT 呈案] 未經拍板不得施作。本文零 DDL、零 DB 寫入、零 commit；全部親驗為 2026-08-02 執行時唯讀現查。**
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，所涉之表正是「AI 生成之解析 API 賴以運作」之表；且三案中有一案（乙）等於承認現行實作無誤、對起草者最省事。故各案一律附**機械可驗之驗收與證偽條件**，不以「相信起草者」為據；反面證據（house precedent 全數不站在乙這邊）亦一併列出。
> **來源**：M1 誠實殘項（commit `84a2da3` 訊息原文：「誠實殘項：**PK vs append-only 張力**／Annex F-1 雙類暫置 event／無 DEXTWUS 不虛構——全列待裁」）。
> **設計 SSOT**＝`reports/wm3536_vendor_registry_plan_20260802.md` §4；條文錨＝`specs/WORLD-MODEL-SPECIFICATION.md` WM.36:344-358（含「Registry 內容為世界模型之一部分，其變更為表徵狀態變更（WM.25），受版本化與可追溯義務（WM.13）約束」）。
> **授權鏈**：本次授權＝WM.36 M3 地基三件（範圍：新檔實作＋唯讀親驗＋呈案；結束條件：三件交付；不碰 A 類 29 檔、零 DDL 執行、零 DB 寫入）。**表結構變更＝Steward 專屬**（`AUGUR-MC v1.6 §8.1`），AI 僅草擬、比對、呈案。

---

## §1 為什麼「現在」必須定案（不是可以拖的技術債）

M1 種子已 live：概念 6 列、通道 98 列（mapped 10／unmapped 88），且**六列之 `authoritative_binding_id`、`decided_by`、`decided_at` 全為 NULL**。

> **下一個合法動作就是第一次修訂。** Annex F 六條之採認（G0 格 4「簽核即附卷」）＝hugo 親簽寫入 `decided_by`／`decided_at`＋指定 `authoritative_binding_id`。在現行 schema 下，這個動作**只能以 `UPDATE` 完成**（同 `concept_key` 再 INSERT 一列會撞 PK）——而 UPDATE 又必須帶 `SET LOCAL augur.honesty_write='on'` 通行證，也就是**誠實閘專門用來讓人起疑的那句咒語**。
>
> 結果：**治權鏈上第一筆人類簽核，會以與表註記（「append-only：變更＝新列、舊列標時戳」）正相反的方式寫入。** 定案若晚於採認，第一筆就先自證註記為假。

第二個時點理由：**成本現在最低、且單調上升**。全 repo 提及此二表者僅 3 檔（`scripts/migrate_world_concept_registry_ddl.py`、`src/augur/catalog/world_concept.py`、`scripts/migrate_strangler_ledger_ddl.py` 之說明），**消費端 0 檔**；M3 絞殺一旦開跑，A 類 29 檔會全部改繫 `resolve()`。6 列 × 0 消費者的搬遷，與 6 列 × 29 消費者的搬遷不是同一件事。

---

## §2 現況親驗（指令可獨立重跑；配方＝`set -a && . ./.env && set +a` 後 psql 唯讀）

### 2.1 二表現形與閘

```
world_concept_registry   PRIMARY KEY btree (concept_key)          -- 自然鍵即主鍵
  triggers: trg_..._honesty_row   BEFORE UPDATE OR DELETE  FOR EACH ROW  → honesty_ledger_guard()
            trg_..._honesty_trunc BEFORE TRUNCATE          FOR EACH STATEMENT → honesty_ledger_guard()
world_channel_binding    PRIMARY KEY btree (binding_id)  -- surrogate（GENERATED ALWAYS AS IDENTITY）
  同二 trigger
```

`honesty_ledger_guard()` 現行語意（`pg_get_functiondef` 全文親驗）：`DELETE`／`TRUNCATE` **一律拒**；`UPDATE` 於 `current_setting('augur.honesty_write')<>'on'` 時拒 ⇒ **帶通行證即可原地改任何欄**（含 `decided_by`）。

### 2.2 列況（唯讀）

| 項 | 值 |
|---|---|
| 概念列／其中已親簽（`count(decided_by)`） | **6 / 0** |
| 概念列已指定權威表徵（`count(authoritative_binding_id)`） | **0**（⇒ 六概念皆不可被消費，WM.35:338） |
| 通道列（mapped／unmapped） | **98（10／88）** |
| 已 supersede 之列（任一表） | **0**（`superseded_at` 全 NULL——**版本化機制從未被使用過**） |

### 2.3 相依：PK 不是孤立的

```
world_channel_binding_concept_key_fkey : world_channel_binding.concept_key
                                          → world_concept_registry(concept_key)   ← 依賴本 PK
fk_auth_binding                        : world_concept_registry.authoritative_binding_id
                                          → world_channel_binding(binding_id)     ← 反向、現全 NULL
```

⇒ 改 `world_concept_registry` 之 PK，**必須同時處理 98 列之外鍵**（見 §4 甲案之致命點）。

### 2.4 全庫「版本化表」之 PK 對照（本案最有力的一份外部證據）

```sql
SELECT c.relname, string_agg(a.attname,',') AS version_cols, <pk>
FROM pg_class c JOIN pg_attribute a ON a.attrelid=c.oid
WHERE c.relkind='r' AND c.relnamespace='public'::regnamespace
  AND a.attname IN ('superseded_at','superseded_by','valid_from','valid_to','version') GROUP BY 1;
```

| 表 | 版本欄 | PRIMARY KEY |
|---|---|---|
| entity_alias | valid_from, valid_to | (alias_id) ← surrogate |
| **entity_attribute_version** | valid_from, valid_to | **(augur_id, attribute_name, valid_from, transaction_time)** ← 雙時間複合 |
| evolution_iteration_ledger／local_ai_／raw_／sim_ | superseded_by | (iteration_id) ← surrogate |
| raw_supersede_log | superseded_at | (id) ← surrogate |
| world_channel_binding | superseded_at | (binding_id) ← surrogate |
| **world_concept_registry** | superseded_at | **(concept_key) ← 自然鍵** |

**全庫九張帶版本欄之表，只有 `world_concept_registry` 一張把自然鍵當主鍵。** 其餘八張一律 surrogate 或含時間維之複合鍵——即「同一實體可有多列」的形狀。本表是唯一的例外，而例外的代價正是本案張力。

### 2.5 house precedent：identity／version 拆表已在生產

`entity_attribute_version`（**9,288 列**在跑）：

```
PRIMARY KEY (augur_id, attribute_name, valid_from, transaction_time)   -- 雙時間 append-only
FOREIGN KEY (augur_id) REFERENCES entity_registry(augur_id)            -- 指向 identity 表（PK=augur_id）
trg_attr_append_only  BEFORE DELETE OR UPDATE ... identity_append_only()
trg_attr_no_truncate  BEFORE TRUNCATE ...
```

`identity_append_only()` 比 honesty guard 更嚴：**DELETE 即使帶通行證也拒**（只許 UPDATE 成 redacted 骨架）。
⇒ 「身分表持自然鍵、版本表持時間維複合鍵、外鍵指身分表」這個形狀，本專案**已有 9,288 列的生產先例**。

---

## §3 張力之精確陳述（四點，非一點）

1. **註記與 schema 互斥**：M1 腳本 `:25-26` 與表 COMMENT 皆寫「append-only：變更＝新列、舊列標 `superseded_at`，不 UPDATE 內容欄」，但 `concept_key` 為 PK ⇒ 同鍵第二列 **在 DB 層物理不可能**。註記描述的是一個 schema 拒絕實現的協定。
2. **現行修訂路徑實為 UPDATE**：唯一存在的修訂通道是 honesty guard 的 GUC 通行證（B4 呈案已自陳其為**半閘非硬閘**）。故本表實際語意是 **current-state registry**，不是 append-only ledger。
3. **傳染到通道表**：`world_channel_binding` 雖有 surrogate PK、可以真的 append 新列，但**改指權威通道**必須改 `world_concept_registry.authoritative_binding_id` ⇒ 仍落回同一個 UPDATE。故「binding 表設計正確」救不了整體。
4. **條文面**：WM.36 明文「Registry 內容……其變更為表徵狀態變更（WM.25），受**版本化**與**可追溯**義務（WM.13）約束」。現行 schema 下，一次 UPDATE 之後**舊值不存在於任何地方**（無側記表、無觸發器留痕、`superseded_at` 永遠用不到）⇒ 版本化義務目前**無任何機械載體**。此為事實陳述；「是否構成違反」屬解釋，落 Steward（§7 Q1）。

---

## §4 三案（各附 DDL 草案、遷移影響、對已寫成之解析 API 之衝擊）

> 共同前提：現有 6 概念列／98 通道列；`superseded_at` 全 NULL；**零消費者**。

### 甲 改 PK：surrogate／複合鍵＋部分唯一索引保「現行列唯一」

```sql
-- 甲1（複合）
ALTER TABLE world_concept_registry DROP CONSTRAINT world_concept_registry_pkey;
ALTER TABLE world_concept_registry ADD COLUMN transaction_time timestamptz NOT NULL DEFAULT clock_timestamp();
ALTER TABLE world_concept_registry ADD PRIMARY KEY (concept_key, transaction_time);
CREATE UNIQUE INDEX uq_world_concept_current ON world_concept_registry (concept_key)
    WHERE superseded_at IS NULL;          -- 「現行列恰一」
```

**致命點（親驗導出，非推測）**：`world_channel_binding.concept_key` 之外鍵**要求被參照欄具備非部分之 unique 約束**（PostgreSQL 規則）。
- 保留該 FK ⇒ 必須保留 `concept_key` 之**全表** unique ⇒ 同鍵多列仍不可能 ⇒ **甲案自我否定**。
- 放棄該 FK ⇒ 98 列通道對概念之參照完整性由 DB 層退為程式層 ⇒ 以「加強版本化」為名，換掉一個真的在擋事的機械閘（**負向交換**）。
- 改 FK 指向 surrogate `concept_row_id` ⇒ 每次概念修訂都要改 98 列通道之外鍵值 ⇒ 更多 UPDATE，方向相反。

⇒ **甲案在保留 §2.3 外鍵的前提下不可行**；若硬要走，其唯一自洽形式就是把身分與版本拆開——那就是丙案。
> ⚠ **[待沙盒實證]**「部分唯一索引不得作為 FK 之被參照約束」為 PostgreSQL 文件規則，本輪**未實跑驗證**（鐵律零 DDL 執行）。主 session 於沙盒庫一行可證：對測試表建 partial unique 後嘗試建 FK，應收 `there is no unique constraint matching given keys`。**此為本案唯一未親驗之技術前提，若被推翻則甲案復活。**

### 乙 維持 PK；承認是 current-state registry，修訂走 UPDATE＋審計側記，並把註記誠實化

```sql
-- schema 不動；新增側記表（append-only，掛同一 honesty guard）
CREATE TABLE world_concept_revision_log (
    revision_id  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    concept_key  text NOT NULL,
    changed_at   timestamptz NOT NULL DEFAULT now(),
    changed_by   text,                    -- 人簽欄：hugo 親跑寫入，AI 不代填
    before_row   jsonb NOT NULL,          -- 改前整列（觸發器 OLD）
    after_row    jsonb NOT NULL,
    basis        text                     -- 裁決/報告錨
);
-- 並將 world_concept_registry 之 BEFORE UPDATE 觸發器改為「記側記後放行」（現為單純 GUC 閘）
```
同時**必須**修正文字：M1 腳本 `:25-26`、二表 COMMENT 之「append-only：變更＝新列」改為「current-state registry：修訂＝原地 UPDATE（GUC 通行證）＋側記留舊值」。

- 優點：零遷移、零 API 改動；與 B4 對「current-state registry」之處置一致。
- 代價：**(i)** 版本化義務由側記承擔（是否滿足 WM.13/WM.25＝解釋落點）；**(ii)** 人類簽核（`decided_by`）永遠必須帶「默改咒語」才寫得進去——把治權簽核與默改動作寫成同一個形狀；**(iii)** `superseded_at` 二欄成為永久死欄（誠實作法是一併移除，否則下一位讀者又會以為有版本化）。
- **B4 之類比不成立處（誠實揭露）**：B4 為四表選 UPDATE-GUC 的理由原文是「8+ 既有寫入者皆 in-place 更新語意；改追加修訂列＝schema 重構＋**全部寫入者與讀者改寫**，與風險不成比例」。本表**寫入者 1（只 INSERT）、讀者 1（本輪剛寫的解析 API）、消費者 0**——「不成比例」之事實前提在此**不存在**。

### 丙 identity／version 拆表（house precedent＝`entity_registry` ＋ `entity_attribute_version`）＋相容 view

```sql
-- ① 身分表（自然鍵；外鍵指這裡 ⇒ §2.3 之 FK 完好保留）
CREATE TABLE world_concept (
    concept_key text PRIMARY KEY,
    created_at  timestamptz NOT NULL DEFAULT now()
);
-- ② 版本表（真 append-only：修訂＝INSERT 新列、舊列標 superseded_at）
CREATE TABLE world_concept_version (
    concept_key      text NOT NULL REFERENCES world_concept(concept_key),
    transaction_time timestamptz NOT NULL DEFAULT clock_timestamp(),
    category text NOT NULL CHECK (category IN ('entity','event','state','relation','quantity')),
    authoritative_binding_id bigint REFERENCES world_channel_binding(binding_id),
    ts_semantics text NOT NULL, knowability_rule text NOT NULL, cross_market_axis text,
    provenance jsonb NOT NULL, finality_predicate text NOT NULL DEFAULT '未宣告',
    conflict_set_ref text, decided_by text, decided_at timestamptz,
    superseded_at timestamptz,
    PRIMARY KEY (concept_key, transaction_time)        -- 同 entity_attribute_version 形
);
CREATE UNIQUE INDEX uq_world_concept_current ON world_concept_version (concept_key)
    WHERE superseded_at IS NULL;                       -- 現行列恰一（此索引不被 FK 參照 ⇒ 合法）
-- ③ 相容 view：解析 API 只要把讀取對象指到它，resolve_rows 一行都不用改
CREATE VIEW world_concept_registry_current AS
    SELECT * FROM world_concept_version WHERE superseded_at IS NULL;
-- ④ 遷移：6 列
INSERT INTO world_concept SELECT concept_key, created_at FROM world_concept_registry;
INSERT INTO world_concept_version (concept_key, category, authoritative_binding_id, ts_semantics,
    knowability_rule, cross_market_axis, provenance, finality_predicate, conflict_set_ref,
    decided_by, decided_at)
  SELECT concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
         cross_market_axis, provenance, finality_predicate, conflict_set_ref, decided_by, decided_at
  FROM world_concept_registry;
-- ⑤ 外鍵改指 ①（binding.concept_key → world_concept.concept_key）；舊表更名保留為史料（不 DROP）
```

- **治權面之關鍵優點**：hugo 的採認簽核變成 **INSERT**（honesty guard 只擋 UPDATE/DELETE/TRUNCATE，INSERT 自由）⇒ **人類簽核不再需要默改通行證**；每次修訂天然留全歷史。
- 對已寫成之解析 API 之衝擊：**一個常數**——`src/augur/catalog/world_concept.py:CONCEPT_TABLE` 改指 view（或版本表）。`resolve_rows` 之「現行列須恰一」已是既有回歸鎖（selftest「同鍵兩筆現行列 → 拋 RegistryIntegrityError」），**丙案落地不需改任何解析邏輯**，且該鎖從「防禦性」升格為「真的會被踩到的守衛」。
- 代價：三張表（＋一 view）取代一張；`--check`／種子腳本需相應改寫（M1 腳本 1 支）；DDL 窗需一次遷移交易。

---

## §5 建議案（AI self-reported，非裁決）

**建議＝丙**，理由三條、皆繫於本文親驗：
1. **甲在保留 FK 下不可行**（§4 甲），故實質選項只有乙與丙。
2. **乙的成立條件在本表不存在**（§4 乙末段：B4 之「寫入者/讀者眾多、不成比例」前提，本表為 1/1/0）。
3. **丙有 9,288 列的 house precedent、且把人類簽核從 UPDATE 變成 INSERT**——治權簽核不該與默改共用同一個形狀（§1）。

**次選＝乙**，其成立要件是 Steward 認定「側記表足以承擔 WM.13/WM.25 之版本化與可追溯義務」（§7 Q1）；若採乙，**必須同批完成文字誠實化與死欄處置**，否則等於留下一份寫著 append-only 的 current-state 表（防呆機制自己靜默失效之典型）。

**時點建議**：**在 Annex F 六條採認（`decided_by` 親簽）之前定案**。採認一旦以 UPDATE 落地，之後改丙就多一段「歷史第一版無法還原」的缺口（改前值不在任何地方）。

---

## §6 驗收與遷移影響（機械可判；施作歸主 session／DDL 窗）

| 案 | 驗收（皆可零 AI 重跑） | 遷移影響 |
|---|---|---|
| 甲 | 先於沙盒證「partial unique 可否支撐 FK」；不可 ⇒ 本案作廢 | — |
| 乙 | 側記表存在＋觸發器實測：帶通行證 UPDATE 一列後，側記表恰增一列且 `before_row` 為改前值（**回歸鎖須先驗紅：拆掉側記觸發器 → 該驗收必失敗**）；M1 腳本與 COMMENT 文字掃描無「append-only」殘句 | 0 列搬遷；文字修訂 1 檔＋2 COMMENT |
| 丙 | `world_concept_version` 6 列、`world_concept` 6 列、view 6 列；`uq_world_concept_current` 存在；binding FK 指向 ①（`pg_constraint` 實查）；`world_concept.py --check` 輸出與遷移前逐字相同（**行為零變更之證據**）；補一條「同鍵 INSERT 第二版 → 舊列標 superseded_at 後 view 仍恰一」之實測 | 6＋6 列寫入、98 列 FK 重指；1 支腳本改寫、1 個常數改指 |

**共同**：DDL 一律帶 `SET lock_timeout='5s'`（#30）；`--apply` 須 hugo 明示（#6）；`decided_by`／`decided_at` 任何案皆 **hugo 親跑寫入**（AI 不代填）。

---

## §7 待 Steward 之解釋落點（AI 不解釋，僅列問題與兩造）

1. **WM.13/WM.25 之「版本化與可追溯」是否得由側記表承擔？** 兩造：條文說「其變更為表徵狀態變更……受版本化義務約束」，未指定載體形式（⇒ 側記可）vs `superseded_at` 之設計與 WM.25 語意指向「舊列留存、新列生效」（⇒ 須真 append-only）。
2. **Annex F 採認是否得先於本案落地？** 若是，第一筆治權簽核將以 UPDATE 寫入（§1）；若否，採認須等本案定案。
3. **`world_channel_binding` 是否同案處理？** 其 surrogate PK 已允許 append，但實務上「改指權威通道」仍落回概念表 UPDATE（§3.3）——是否要求 binding 之修訂亦一律 append（新列＋舊列標 `superseded_at`）並禁 in-place？

---

## §8 Steward 決定欄（留白待 hugo）

| # | 決定事項 | 選項 | 裁示 |
|---|---|---|---|
| 1 | PK × append-only 之處置 | 甲／**乙**／**丙**／其他 | |
| 2 | 若乙：文字誠實化＋`superseded_at` 死欄處置（移除／保留並註記） | 移除／保留＋註記 | |
| 3 | 若丙：舊表處置 | 更名保留為史料／DROP | |
| 4 | Annex F 六條採認之時點（§7 Q2） | 本案定案後／不受本案影響 | |
| 5 | `world_channel_binding` 是否同案（§7 Q3） | 同案／另案／不處理 | |
| 6 | 施作窗 | 統一 DDL 窗／即刻／M3 後 | |

---

## §9 誠實揭露與殘項

- 本文**零 DDL 執行、零 DB 寫入、零 commit**；全部數字為本日唯讀 psql 現查，指令逐條列於 §2，任何人可零 AI 獨立重跑。
- **唯一未親驗之技術前提**：§4 甲案之「部分唯一索引不得作為 FK 被參照約束」（PostgreSQL 規則，本輪未實跑；若被推翻，甲案復活並須重排 §5）。
- 未做：未估丙案 DDL 於 live 之鎖持有時間（6 列，預期毫秒級，但未實測）；未檢查是否有非 Python 之 registry 讀寫者（grep 射程＝`*.py`；SQL 檔／psql history 未掃）。
- 本文之分類、建議與「house precedent 不站在乙這邊」之判讀皆為 **AI self-reported**，不構成「世界如此」之權威確認（CLAUDE.md #32(a)）。

---

## 附記：甲案前提已沙盒實證（2026-08-02，主 session 補驗）

呈案自陳「甲案在保留現有外鍵下不可行（partial unique 不能支撐 FK）」為**唯一未親驗前提**。已於 `augur_sandbox` 實跑（探針表用畢即刪）：

```sql
CREATE TABLE _pk_probe_parent (concept_key text NOT NULL, version int NOT NULL,
  superseded_at timestamptz, PRIMARY KEY (concept_key, version));
CREATE UNIQUE INDEX ux_probe_current ON _pk_probe_parent (concept_key) WHERE superseded_at IS NULL;
CREATE TABLE _pk_probe_child (id serial PRIMARY KEY, concept_key text NOT NULL
  REFERENCES _pk_probe_parent(concept_key));
-- ERROR: there is no unique constraint matching given keys for referenced table "_pk_probe_parent"
```

⇒ **甲案不可行為實證事實**（PostgreSQL 不接受 partial unique index 作為 FK 參照鍵）。三案比較據此收斂為乙／丙之選。
