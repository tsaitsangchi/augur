# augur 知識層 權限與內容分類軸 規劃報告（PostgreSQL Schema 整合版）

🎯 **白話**：後台那兩個下拉選單「授權」和「範圍」讓人混淆——`public_domain` 和 `public` 名字都有 public，但**是兩個完全不同的軸**。本報告據實(全部欄位/型別/CHECK/FK/索引皆由 PG 17.9 實庫直查)把知識層**所有管「誰能看什麼內容」的分類軸**攤開講清楚、兩兩區分，讓**真實 DDL 貫穿全文**，說明如何組合成存取決策，並把未來 RBAC(群組×domain)以**可落地、冪等、預設 deny、server-side 強制**的具體 DDL 疊加——且逐條吸收 schema 紅隊發現(critical/high 必修進 DDL；修不了者明列為已知風險)。

守原則 #1(逐字可溯源/零 AI 入庫/授權硬擋) #5(存取控制/不越權) #19(決策層拍板前先攤清、跨檔一致)。**Schema 整合版**，日期：2026-07-05。

> 本報告為**基礎定義層 + schema 綁定層**，與同日《RBAC 設計計畫》(`augur_rbac_design_plan_20260705.md`)互補——RBAC 談「使用者↔domain 授權」，本報告談「內容自身的分類軸」與其**真實欄位落點**，RBAC 建在這些軸之上。
>
> **事實來源(#1)**：全部 schema 事實由 `venv/bin/python` + `augur.core.db` 直查 `information_schema.columns` / `pg_constraint`(`pg_get_constraintdef`) / `pg_indexes` / `pg_extension` / `pg_roles`(PG 17.9，DB=`augur`，`current_user=augur`，`rolsuper=false`)。既有述詞 SSOT 讀 `src/augur/knowledge/corpus.py` 與 `src/augur/philosophy/retrieval.py` 真實 code。**RBAC DDL 尚未在 DB 執行**——屬決策層拍板前之設計交付(#19)，非執行層落地。

---

## 0. 開宗明義：`public` ≠ `public_domain`（最常見的混淆）

| | `public_domain` | `public` |
|---|---|---|
| **屬於哪個軸** | **license**(著作權/法律軸) | **access_scope**(系統可見範圍軸) |
| **回答的問題** | 這份文本「法律上能不能被逐字儲存/散布」 | 這份文本「在 augur 內部誰看得到」 |
| **真實欄位** | `knowledge_item_text.license varchar(64)` | `knowledge_item_text.access_scope varchar(16)` |
| **值域(據實查得)** | `{public_domain, cc-by, cc-by-sa, cc0}`(哲學側 `philosophy_work_text.license` **僅** `public_domain`) | `{public, local_private}` |
| **在哪強制** | DB CHECK 硬牆(入庫時擋) | DB CHECK + 檢索 SQL 過濾 |
| **設錯的後果** | 侵權/法律風險 | 越權洩漏/私有內容外流 |

**一句話**：`public_domain` 管「**合不合法收進來**」；`public` 管「**收進來之後給誰看**」。兩者正交、可自由組合——公版著作也可以只給自己看(`public_domain` + `local_private`)；CC 授權的論文也可以對外可引(`cc-by` + `public`)。

---

## 1. 六個正交分類軸 × 真實 schema 對照表（逐一，皆據實查證）

每一則知識內容同時被下列**六個獨立軸**標記；它們各管一件事、各在不同 DB 欄位/CHECK 強制。

### 1.0 軸 ↔ 真實 schema 總表（型別/CHECK/強制點）

| 權限軸 | 真實表.欄位 | 確切型別 | 強制約束(CHECK 名) | 值域 | 強制點 | 現庫值 |
|---|---|---|---|---|---|---|
| **license** | `knowledge_item_text.license` | `varchar(64)` NOT NULL | `knowledge_item_text_license_check` | `{public_domain,cc-by,cc-by-sa,cc0}` | DB CHECK(物理硬牆) | 全 `cc-by`(13) |
| **license**(哲學側) | `philosophy_work_text.license` | `varchar(32)` NOT NULL DEFAULT `'public_domain'` | `philosophy_work_text_license_check` | **僅** `{public_domain}` | DB CHECK(單值、更嚴) | — |
| **access_scope** | `knowledge_item_text.access_scope` | `varchar(16)` NOT NULL DEFAULT `'public'` | `chk_itext_access_scope` | `{public,local_private}` | DB CHECK + 檢索 SQL | 全 `public`(13) |
| **source_type** | `knowledge_item_text.source_type` | `varchar(24)` NULL | `chk_itext_source_type` | `≠ 'ai_generated'`(NULL 放行) | DB CHECK | 全 `NULL`(13) |
| **source_type**(哲學對偶) | `philosophy_work.work_type` | `varchar(32)` NOT NULL | `philosophy_work_work_type_check` | `≠ 'ai_generated'` | DB CHECK | — |
| **corpus_class** | `philosophy_work.corpus_class` | `varchar(16)` NOT NULL DEFAULT `'literary'` | `philosophy_work_corpus_class_check` | `{literary,reference}` | DB CHECK | literary 1528 / reference 7 |
| **review_flag** | `philosophy_work.review_flag` | **`boolean`** NULL(三態靠 NULL) | 無 CHECK(型別本身即約束) | `{false,NULL,true}` | 檢索 SQL(`clean_work_sql`) | false 1166 / NULL 218 / true 151 |
| **domain** | `knowledge_item.domain` | `varchar(64)` NOT NULL | **無 CHECK / 無 FK**(缺口) | 自由字串，現值 40 種 | 索引 `idx_item_domain`，**無值域強制** | medicine 12262… rd_mgmt 2697… |

**FK 拓撲(權限鏈骨架，據實查得)**：
```
knowledge_source(source_key)  ──< knowledge_item(source_key)
knowledge_taxonomy(tax_id)    ──< knowledge_item(taxonomy_id)
knowledge_item(item_id)       ──< knowledge_item_text(item_id)   [全文掛 item → domain 經此傳遞]
knowledge_item_text(itext_id) ──< knowledge_sentence(itext_id)   (XOR: chk num_nonnulls=1)
philosophy_thinker(thinker_id)──< philosophy_work(thinker_id) ON DELETE CASCADE
philosophy_work(work_id)      ──< philosophy_work_text(work_id) ON DELETE CASCADE
philosophy_school(school_id)  ──< philosophy_principle / philosophy_source   (注意:NOT philosophy_work)
```
**RBAC 關鍵推論**：`domain` 只住 `knowledge_item`——全文/句層**無 domain 欄**。故 domain 過濾必須 **JOIN 回 `knowledge_item`**(既有 `retrieve_items` 已 `JOIN knowledge_item i ON i.item_id = x.item_id`，無需新增 JOIN，命中既有 `idx_item_domain`)。

### 1.1 `license` — 著作權/法律軸
- **真實欄位**：`knowledge_item_text.license varchar(64) NOT NULL`。**強制 DDL**：
  ```sql
  CONSTRAINT knowledge_item_text_license_check CHECK (
    license::text = ANY (ARRAY['public_domain','cc-by','cc-by-sa','cc0']::text[]) )
  ```
- **哲學側更嚴(關鍵不對稱)**：`philosophy_work_text.license varchar(32) NOT NULL DEFAULT 'public_domain'`，`CHECK ( license::text = 'public_domain' )` ——**只准公版**(憲章：哲學原典限公版；知識層 item_text 才放寬到公版＋CC 白名單)。兩表 license 軸型別(64 vs 32)與值域皆不同，是刻意的。
- **管什麼**：這份文本能不能**合法逐字進入全文表**。版權他人著作進不了(只能走「principle→factor_map→#14」抽象路，見憲章)。
- **責任**：DB CHECK 是物理硬牆(非白名單值 INSERT 直接被 DB 拒)，但**擋不了誤標**(把版權檔謊稱 public_domain)——仍是人的誠信責任。

### 1.2 `access_scope` — 系統可見範圍軸
- **真實欄位**：`knowledge_item_text.access_scope varchar(16) NOT NULL DEFAULT 'public'`。**強制 DDL**：
  ```sql
  CONSTRAINT chk_itext_access_scope CHECK (
    access_scope::text = ANY (ARRAY['public','local_private']::text[]) )
  ```
- **強制點**：DB CHECK + **檢索層 SQL**(`corpus.clean_item_sql(..., access_scope)`；`retrieve_items(access_scope='public')` 預設)。
- **管什麼**：進不進**對外對話檢索池**。`public`＝對外可檢索引用；`local_private`＝只本機/私有模式可見、不入對外池。
- **現庫全 `public`**：既有 13 列維持不動即正確——`public` 語意本就該被對外看到；RBAC 只在 `public` 之上再加 domain 閘。

### 1.3 `corpus_class` — 語料性質軸
- **真實欄位**：`philosophy_work.corpus_class varchar(16) NOT NULL DEFAULT 'literary'`。**強制 DDL**：
  ```sql
  CONSTRAINT philosophy_work_corpus_class_check CHECK (
    corpus_class::text = ANY (ARRAY['literary','reference']::text[]) )
  ```
- **強制點**：單一語意閘(W2.5；切句/嵌入/檢索一律 `corpus.clean_work_sql`，產 `w.review_flag = false AND w.corpus_class = 'literary'`)。
- **管什麼**：`literary`(1528)→ 進切句/嵌入/語意檢索；`reference`(7)→ **只走 lexicon 定義路**，不進切句/嵌入(否則辭典全文污染語意檢索)。

### 1.4 `domain` — 領域軸（未來 RBAC 授權邊界；也是最大缺口）
- **真實欄位**：`knowledge_item.domain varchar(64) NOT NULL`。**無 CHECK、無 FK**——現值 40 種全靠 writer 端自律。索引 `idx_item_domain btree(domain, entity_type)` **已存在**。
- **現值(據實)**：OpenAlex 域(`medicine` 12262、`social_sciences` 12252、`engineering` 9569、`chemistry` 8721…) + 管理域(`business_mgmt` 2822、`production_mgmt` 2759、`organization_mgmt` 2720、**`rd_mgmt` 2697**、`accounting_mgmt` 2616、`finance_mgmt` 2591、`investment_mgmt` 2587、`mgmt_philosophy` 2094…) + `general` 15。**庫中無 `local` 域實列**(舊版報告稱 domain 含 `local` 屬預留/本機檔，現庫尚無)。
- **管什麼**：這則內容屬哪個知識域。**「研發人員只看研發」正靠此軸**——現成已有 `rd_mgmt`(2697 筆)，群組授權綁到它即可(見 §3)。
- **⚠ 缺口(紅隊 high，已修入 §3.3a 字典表方案)**：這是六軸中**唯一無 DB 級值域強制**的軸，卻正是 RBAC 要當邊界的軸。方向不對稱——拼錯 grant 側是 **fail-closed**(該群組讀不到，偏安全)；誤標 item 側是 **fail-open**(內容落入錯授權集＝越權)。故 RBAC 上線前須建 `knowledge_domain` 字典表 + FK 升級此軸為受控邊界(§3.3a)。

### 1.5 `review_flag` — 歸屬驗證軸（三級誠實）
- **真實欄位**：`philosophy_work.review_flag boolean NULL`(**boolean 三態靠 NULL，非 varchar**)。**無 CHECK、無索引**。provenance 佐證：`reviewed_by varchar(16)` `CHECK (reviewed_by = ANY(ARRAY['audit','provenance','human']))`。
- **值域(據實)**：`false`(1166=已驗 clean) / `NULL`(218=未稽核) / `true`(151=庫存但歸屬未驗)。
- **強制**：檢索閘顯式 `review_flag = false`(NULL/true 天然排除，fail-closed)。`false`→可引用；`true`→回第二誠實句「知識庫存有此著作但歸屬未驗證,不予引用」；`NULL`→亦排除(verify_text_integrity 要求補稽核至 0)。
- **⚠ 防迴歸(紅隊 low)**：禁改寫成 `review_flag != true` / `IS DISTINCT FROM true`(會把 218 個 NULL 放進池＝fail-open)；須加單測釘死「NULL 與 true 皆排除」語意。

### 1.6 `source_type` — 來源/provenance 軸
- **真實欄位**：`knowledge_item_text.source_type varchar(24) NULL`。**強制 DDL**：
  ```sql
  CONSTRAINT chk_itext_source_type CHECK (
    source_type IS NULL OR source_type::text <> 'ai_generated' )
  ```
- **哲學對偶**：`philosophy_work.work_type varchar(32) NOT NULL`，`CHECK ( work_type::text <> 'ai_generated' )`。
- **管什麼**：**禁 AI 生成內容入庫**(#1 三敵之首「假資料」的機器防線)。NULL 放行(現庫全 NULL)。

---

## 2. 組合決策流：一則內容「能不能被某人引用」（過濾條件寫成真實欄名 SQL）

六軸不是各自獨立生效，而是**串成一條決策鏈**(任一關 fail 即止)，各關對應真實欄名述詞：

```
(a) 入庫閘   x.license IN ('public_domain','cc-by','cc-by-sa','cc0')            ── 否 → 進不了全文表(#1 法律)
            AND (x.source_type IS NULL OR x.source_type <> 'ai_generated')      ── 否 → 進不了全文表(#1 假資料)
(b) 語意閘   w.corpus_class = 'literary'  (哲學側;items 側 i.entity_type ∈ 准入集) ── reference → 只走 lexicon(W2.5)
(c) 可見閘   x.access_scope = 'public'                                          ── local_private → 不入對外池
(d) 歸屬閘   w.review_flag = false                                             ── true/NULL → 排除(誠實句)
(e) RBAC 閘  i.domain ∈ v_user_allowed_domain(uid)  OR  u.is_superuser         ── 否 → 該使用者看不到(§3)
                                                                                 檢索全空 → 「知識庫中無此內容」
```

- (a) 是**法律/真實性**；(b) 是**語意正確**；(c)(e) 是**存取控制**；(d) 是**誠實歸屬**。
- 目前 (a)–(d) 已實作(住 `corpus.clean_item_sql` / `clean_work_sql` SSOT)；**(e) RBAC 閘尚未建**(見 §3)。
- **SSOT 紀律(#12)**：述詞一律 import `corpus.py` 產出片段，**RBAC 只 append (e) 一段**，絕不手抄 (a)–(d)。

---

## 3. RBAC schema：完整 CREATE TABLE DDL（整合真實型別；預設 deny、server-side）

前六軸皆為**內容自身屬性**(住既有表)。RBAC 加的是**使用者 ↔ domain 授權關係**新維度——不改任何內容軸、不動既有 CHECK/FK、不觸 #1 命門。所有型別對齊真實欄(`knowledge_item.domain = varchar(64)`)。

### 3.0 設計不變式（紅線）
- **預設 deny**：`group_domain_grant` 無列即無權；superuser 為唯一略過閘。
- **server-side 強制**：閘寫在檢索 SQL WHERE，絕不靠 UI 藏(見 §5)。
- **domain 型別逐字對齊**：`group_domain_grant.domain` 必 `varchar(64)`，否則隱式轉型埋越權盲點。
- **不碰 #1**：RBAC 全表與 `feature_values`/預測管線**零 FK 連結**(已驗)；RBAC 只決定「人讀哪些 domain」，**不新增任何知識→預測旁路**。

### 3.1 `app_user` — 使用者
```sql
CREATE TABLE IF NOT EXISTS app_user (
    user_id       integer     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username      varchar(64) NOT NULL,
    display_name  varchar(128),
    password_hash text        NOT NULL,               -- 見 §3.6 存法約定(argon2id/bcrypt 編碼字串)
    is_superuser  boolean     NOT NULL DEFAULT false,  -- administrator:略過 domain 閘
    is_active     boolean     NOT NULL DEFAULT true,   -- 停用即全域 deny(不刪列、保稽核)
    created_at    timestamptz NOT NULL DEFAULT now()
    -- password_hash 之 CHECK 見 §3.6:改為擋裸 hex/明文(非長度魔數),或誠實不加、由寫入路徑守門
);
-- 大小寫不敏感唯一:防 Admin/admin 雙帳號繞授權(紅隊 low)
CREATE UNIQUE INDEX IF NOT EXISTS uq_app_user_username_ci ON app_user (lower(username));
```

### 3.2 `permission_group` — 群組（命名避開 SQL 保留字 `ROLE`）
> `role` 是 SQL 保留字，裸建須永遠 `"role"`、易錯；依 CLAUDE #18「一看就懂」取 `permission_group`，與 `app_user`/`app_session` 同前綴內聚。
```sql
CREATE TABLE IF NOT EXISTS permission_group (
    group_id   integer     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    group_key  varchar(32) NOT NULL,   -- 'rnd' / 'finance' / 'administrator'
    label     varchar(64) NOT NULL,   -- 繁中顯示名
    note      text,
    CONSTRAINT uq_permission_group_key UNIQUE (group_key)
);
CREATE TABLE IF NOT EXISTS user_group (
    user_id integer NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    group_id integer NOT NULL REFERENCES permission_group(group_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, group_id)
);
```

### 3.3 `knowledge_domain` 字典 + `group_domain_grant`（domain 升級為受控邊界）
**決策(統一紅隊矛盾)**：**建 `knowledge_domain` 字典表**，`group_domain_grant.domain` **FK 到它**——把「domain 標註」從自律升級為受控安全邊界。理由：現況 `knowledge_item.domain` 無 CHECK/無 FK、自由 40 值，一旦當授權邊界，打錯字＝靜默越權/漏權。**本節取代舊報告 §3.1-R4「不加 FK:domain 非獨立實體表」之矛盾表述——建了字典它就是實體表，兩側皆可 FK。**

```sql
-- 3.3a domain 字典(合法域 SSOT;型別逐字對齊 knowledge_item.domain = varchar(64))
CREATE TABLE IF NOT EXISTS knowledge_domain (
    domain    varchar(64) PRIMARY KEY,
    label     varchar(64),
    is_active boolean NOT NULL DEFAULT true,
    note      text
);
-- 冪等回填:只從 knowledge_item.domain 取(授權邊界 SSOT=內容實際所在;紅隊 medium:
-- 不混入 source/staging/query 側詞彙,避免死授權/污染)
INSERT INTO knowledge_domain (domain)
SELECT DISTINCT domain FROM knowledge_item
ON CONFLICT (domain) DO NOTHING;
INSERT INTO knowledge_domain (domain) VALUES ('philosophy')   -- 哲學層固定域(見 §7 缺口 G2/G4)
ON CONFLICT (domain) DO NOTHING;

-- 3.3b 群組→可讀 domain(授權矩陣;無列＝無權＝預設 deny)
CREATE TABLE IF NOT EXISTS group_domain_grant (
    group_id integer     NOT NULL REFERENCES permission_group(group_id)        ON DELETE CASCADE,
    domain  varchar(64) NOT NULL REFERENCES knowledge_domain(domain) ON DELETE RESTRICT,
    PRIMARY KEY (group_id, domain)
);
CREATE INDEX IF NOT EXISTS idx_gdg_domain ON group_domain_grant (domain);
```
> **hygiene 效益**：grant.domain FK 到字典 → 不可能授權到不存在的域(打錯字被 FK 擋，非靜默漏權)。`ON DELETE RESTRICT` 防誤刪仍被授權的域。**選配硬化(決策層 gate，見 §7 G1)**：把 `knowledge_item.domain` 也 FK 到字典——因 3.3a 已冪等回填全部現值，加 FK **安全不失敗**；但屬「升級判準」動作，不在冪等段自動執行、須拍板。

### 3.4 `app_session` — 伺服器端會話（uuid 用 PG17 核心版，不依賴 pgcrypto）
> **紅隊 critical 修正**：實庫 `pg_extension = {plpgsql, vector}`，**無 pgcrypto**，且 `current_user=augur`、`rolsuper=false`→ **無權 CREATE EXTENSION**。`gen_random_uuid()` 在 PG13+ **核心即內建**，不需 pgcrypto。token 明文由**應用層 CSPRNG**(`secrets.token_urlsafe`)產生、DB 只存其 sha256——雜湊也在應用層算，DB 完全不需 pgcrypto。故**移除** `CREATE EXTENSION pgcrypto`。
```sql
CREATE TABLE IF NOT EXISTS app_session (
    session_id   uuid        PRIMARY KEY DEFAULT gen_random_uuid(),  -- PG17 核心內建
    user_id      integer     NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    token_hash   text        NOT NULL,      -- 存 cookie token 之 sha256,非明文
    issued_at    timestamptz NOT NULL DEFAULT now(),
    expires_at   timestamptz NOT NULL,      -- 逾時即失效(server-side 檢查)
    revoked_at   timestamptz,               -- 登出/強制下線;非 NULL 即作廢(append-only,不刪列)
    last_seen_at timestamptz,
    ip_addr      inet,
    user_agent   text,
    CONSTRAINT uq_app_session_token UNIQUE (token_hash),
    CONSTRAINT chk_app_session_expiry CHECK (expires_at > issued_at),
    CONSTRAINT chk_app_session_token_len CHECK (char_length(token_hash) >= 32)  -- 堵空/短 token 冒用
);
CREATE INDEX IF NOT EXISTS idx_session_user ON app_session (user_id);
CREATE INDEX IF NOT EXISTS idx_session_live ON app_session (expires_at) WHERE revoked_at IS NULL;
```
> **會話有效性(紅隊 high，強制入閘)**＝`revoked_at IS NULL AND expires_at > now()` **且** JOIN `app_user.is_active = true`。**登出＝寫 `revoked_at`**(append-only 保稽核，不 DELETE)。

### 3.5 `knowledge_item_text.owner_user_id` — local_private 擁有者
唯一觸及既有內容表之改動。**nullable、無 default**：既有 13 列 itext 全 NULL 相容；PG17 下 `ADD COLUMN ... NULL` 無 default ＝ metadata-only、不重寫表。
```sql
ALTER TABLE knowledge_item_text
    ADD COLUMN IF NOT EXISTS owner_user_id integer NULL
        REFERENCES app_user(user_id) ON DELETE RESTRICT;   -- 紅隊 medium:不用 SET NULL(免製造無主 private 孤兒)
```
> **owner 一致性硬牆(紅隊 medium，統一採加 CHECK 版)**：見 §4 遷移之 `chk_itext_private_owner`——`private ⇒ owner NOT NULL`、`public ⇒ owner NULL`，堵「無主 private」與「public 誤掛 owner」兩越權/漏判。`ON DELETE RESTRICT`：有 private 內容的 user 不可直接刪(須先轉移/降級)，杜絕 SET NULL 持續製造孤兒。

### 3.6 `password_hash` / `token_hash` 存法（約定，DB 無法強制——誠實標註）
- **`password_hash`**：存 **Argon2id**(首選)或 **bcrypt** 編碼字串(含演算法 id+salt+參數)。**禁明文、禁無 salt 之裸 SHA/MD5**。真雜湊強度由**應用層寫入路徑**負責，DB 無法驗。
- **CHECK(誠實版，取代長度魔數)**：紅隊 medium 指出 `char_length >= 20` 是安全劇場(20 字元明文照過、無 salt MD5=32 hex 反被放行)。改為擋裸 hex/明文：
  ```sql
  CONSTRAINT chk_app_user_pwd_encoded CHECK (
    password_hash LIKE '$argon2%' OR password_hash LIKE '$2b$%' OR password_hash LIKE '$2a$%' )
  ```
  此僅擋「明顯非 argon2/bcrypt 編碼」，**非密碼學保證**；文件誠實標註 DB 不強制雜湊強度。
- **`token_hash`**：cookie 給客戶端隨機不透明 token；DB 只存其 sha256(§3.4 `chk_app_session_token_len ≥ 32`)——DB 外洩不等於可冒用會話。

### 3.7 授權解析 view（含 is_active，紅隊 high 修入）
```sql
-- 某 user 之 allowed_domains = 其所有「有效群組」grant 之 domain 聯集;停用帳號無列
CREATE OR REPLACE VIEW v_user_allowed_domain AS
SELECT ur.user_id, rdg.domain
FROM   user_group ur
JOIN   app_user u          ON u.user_id = ur.user_id AND u.is_active   -- 停用即無授權(紅隊 high)
JOIN   group_domain_grant rdg ON rdg.group_id = ur.group_id;
```

---

## 4. 遷移 ALTER（冪等安全、既有資料相容、index、bootstrap）

RBAC 為**純新增**：不改任何六軸欄、不動既有 CHECK/FK；既有 **111,259** item / 13 itext / 1,535 work **不受影響**。

> **紅隊 critical 修正(冪等造假)**：PostgreSQL 的 `ALTER TABLE ... ADD CONSTRAINT` **不支援 `IF NOT EXISTS`**——裸寫第二次跑即 `constraint already exists`、整交易 abort。本專案既有遷移器 `scripts/migrate_text_understanding_ddl.py:ensure_constraint()` 早已用 `pg_constraint` guard 解此題。本節**沿用該慣例**：`CREATE TABLE`/`ADD COLUMN`/`CREATE INDEX` 用 `IF NOT EXISTS`(合法)；`ADD CONSTRAINT` 一律先查 `pg_constraint`。

```sql
BEGIN;

-- (1) 四張 RBAC 表 + 字典(§3.1–3.3、3.4;全 CREATE TABLE IF NOT EXISTS)
-- (2) 冪等回填 knowledge_domain(§3.3a;ON CONFLICT DO NOTHING)
-- (3) owner 欄(§3.5;ADD COLUMN IF NOT EXISTS,metadata-only、13 列瞬時)
ALTER TABLE knowledge_item_text
    ADD COLUMN IF NOT EXISTS owner_user_id integer NULL
        REFERENCES app_user(user_id) ON DELETE RESTRICT;

-- (4) 授權解析 view(§3.7;CREATE OR REPLACE 天然冪等)

COMMIT;
```

**`ADD CONSTRAINT` 走 pg_constraint guard（沿用 `ensure_constraint` 模式，逐條冪等）**：
```sql
-- 對每條 CHECK/FK:不存在才加。(psql 版用 DO block;Python 遷移器用 ensure_constraint())
DO $$
BEGIN
  -- owner 一致性硬牆(itext 僅 13 列全 public、owner 全 NULL → 現庫全成立,可安全加)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint
                 WHERE conname='chk_itext_private_owner' AND conrelid='knowledge_item_text'::regclass) THEN
    ALTER TABLE knowledge_item_text ADD CONSTRAINT chk_itext_private_owner CHECK (
        (access_scope = 'local_private' AND owner_user_id IS NOT NULL)
     OR (access_scope = 'public'        AND owner_user_id IS NULL) );
  END IF;
END $$;
```

**選配 item.domain FK（兩段式免全表鎖，紅隊 medium；屬 §7 G1 決策層 gate、預設不執行）**：
> `knowledge_item` 有 111,259 列，直接 `ADD CONSTRAINT ... FOREIGN KEY` 會取 ACCESS EXCLUSIVE 鎖並**掃全表驗證**。用兩段式：
```sql
-- 先短鎖不掃表:
ALTER TABLE knowledge_item ADD CONSTRAINT fk_item_domain
    FOREIGN KEY (domain) REFERENCES knowledge_domain(domain) NOT VALID;
-- 再 SHARE UPDATE EXCLUSIVE(不阻讀寫)驗證既有列:
ALTER TABLE knowledge_item VALIDATE CONSTRAINT fk_item_domain;
```

**bootstrap admin（冪等 upsert，可重跑不重複）**：
```sql
INSERT INTO permission_group (group_key, label) VALUES
    ('administrator','系統管理員'), ('rnd','研發')
ON CONFLICT (group_key) DO NOTHING;
-- password_hash 由應用層 --set-password 產生後帶入(此處佔位示意,禁明文)
INSERT INTO app_user (username, display_name, password_hash, is_superuser)
VALUES ('admin','系統管理員', :argon2_hash, true)
ON CONFLICT (username) DO UPDATE SET is_superuser = true, is_active = true;
```

**遷移安全(CLAUDE #30)**：`ADD COLUMN`/`ADD CONSTRAINT` 需 ACCESS EXCLUSIVE 鎖→**務必避開 pg_dump 進行中**(否則鎖佇列風暴、全庫 hang)。遷移前跑 extension/函式 smoke test(#23)確認 `gen_random_uuid()` 可用(PG17 核心已有)。

---

## 5. 逐檢索路徑強制 SQL 片段（真實欄名、預設 deny、server-side）

> **紅隊 critical 修正(exact 路徑 fail-open)**：真實 `retrieve_items`(`src/augur/philosophy/retrieval.py`)的 exact 分支，打分查詢帶 `{clean}{extra}`，但隨後 `_item_citations(cur, f"s.sent_id = ANY(%s) AND {clean}", ...)` **只帶 `{clean}`、不帶 `{extra}`**(retrieval.py `_item_citations` 之 `WHERE {where}` 僅 `clean`)。若把 RBAC 閘塞進 `extra` 字串，會在此第二段 citation-fetch **靜默丟棄＝洩漏全域**。安全邊界不可寄生在「各分支各自拼 `extra`」的非 SSOT 機制上。

**修法(必做，非選配)**：把 RBAC domain 述詞收進 `corpus.py` 成 **SSOT 函式** `rbac_domain_sql(item_alias, uid_param_ordinal)`，與 `clean_item_sql`/`clean_work_sql` 並列；**打分查詢、`_item_citations`、ANN 分支三處都 import 同一片段**(對齊 corpus.py #12「三端同一閘、禁 inline 複本」)。並修 `_item_citations` 使其 `where` 也納入 RBAC(不能只信任呼叫端傳入的 where)。加 CI lint/單測：**每個對 `knowledge_item_text` 的檢索 SELECT 必含 `v_user_allowed_domain` 或 `is_superuser` 述詞，否則 fail**。

RBAC SSOT 片段(位置參數 `%s`，對齊真實 code 風格)：
```sql
-- rbac_domain_sql('i'):預設 deny + superuser 旁路(且 superuser 須 is_active)
( EXISTS (SELECT 1 FROM app_user u WHERE u.user_id = %s AND u.is_superuser AND u.is_active)
  OR i.domain IN (SELECT domain FROM v_user_allowed_domain WHERE user_id = %s) )
```

**知識 items 側完整檢索 WHERE(exact 打分分支＋citation 分支＋ANN 分支三處一致)**：
```sql
-- i = knowledge_item, x = knowledge_item_text(既有別名);i.domain 已在 JOIN 範圍,命中 idx_item_domain
WHERE c.term = ANY(%s)
  AND (x.license IN ('public_domain','cc-by','cc-by-sa','cc0')      -- (a) clean_item_sql SSOT,不重述
       AND i.entity_type IN ('paper','report','document')
       AND x.access_scope = 'public')
  AND ( EXISTS (SELECT 1 FROM app_user u WHERE u.user_id = %s AND u.is_superuser AND u.is_active)  -- (e) RBAC
        OR i.domain IN (SELECT domain FROM v_user_allowed_domain WHERE user_id = %s) )
```

**private owner 旁路(若開放 local_private 檢索)**——把 access_scope 硬 `public` 改為「public ∪ 自己的 local_private」，**永遠寫 `owner_user_id = %s`，絕不 `OR IS NULL`**(紅隊 medium)：
```sql
  AND ( x.access_scope = 'public'
        OR (x.access_scope = 'local_private' AND x.owner_user_id = %s) )
```

**哲學語料側(`retrieve()`)**——用 `clean_work_sql` 既有述詞；哲學層 domain 見 §7 G2/G4(採固定 `'philosophy'` 域，且該值須先在 `knowledge_domain` 字典)：
```sql
WHERE w.review_flag = false AND w.corpus_class = 'literary'   -- (b)(d) clean_work_sql SSOT
  AND wt.license = 'public_domain'                            -- (a) 哲學側單值 CHECK(比知識側嚴)
  AND ( EXISTS (SELECT 1 FROM app_user u WHERE u.user_id = %s AND u.is_superuser AND u.is_active)
        OR 'philosophy' IN (SELECT domain FROM v_user_allowed_domain WHERE user_id = %s) )
```

**uid 來源(紅隊 high，會話與授權原子化)**：`uid` **絕不由前端傳入**，由 server-side 查 `app_session`(`WHERE token_hash = sha256(cookie) AND revoked_at IS NULL AND expires_at > now()`)JOIN `app_user`(`WHERE is_active`)得出 effective `uid`/`is_superuser`；只有此受驗 uid 才進 domain 閘——杜絕「握著舊 uid 就越權」。

**授權設定範例(「研發只看研發」「admin 看全部」)**：
```sql
INSERT INTO group_domain_grant (group_id, domain)
SELECT r.group_id, d.domain
FROM   permission_group r, (VALUES ('rd_mgmt'),('production_mgmt'),('engineering')) AS d(domain)
WHERE  r.group_key = 'rnd'
ON CONFLICT DO NOTHING;
-- administrator = is_superuser=true(bootstrap 已設),EXISTS 分支直接放行全 domain
```

---

## 6. 權限型態情境矩陣（補真實 domain 值）

| 情境 | license(真實欄) | access_scope | domain(真實值) | 誰能看(RBAC) |
|---|---|---|---|---|
| 公版經典逐字全文，人人可查 | `public_domain`(哲學側單值) | (哲學層 work) | `philosophy`(固定域) | 全部 |
| **自有研發報告，只研發+admin** | `cc-by`/自釋 | `local_private`→(RBAC)域內 | **`rd_mgmt`**(2697 筆現存) | rnd 群組 + administrator |
| CC-BY 財經論文，對外可引 | `cc-by` | `public` | `business_mgmt`/`finance_mgmt`(現存) | 全部(或財經群組) |
| 生產管理知識，只產線+admin | `cc-by`/自釋 | `public`→域內 | `production_mgmt`(2759 筆) | 產線群組 + administrator |
| 本機私人筆記，只自己 | `public_domain`/自有 | `local_private`(owner=自己) | (待標;無 `local` 域實列) | owner + administrator |
| 版權他人著作 | ✗ 進不了全文表 | — | — | 只能走 principle→factor_map(#14) |

---

## 7. Schema 紅隊結論（critical/high 逐條：已修入哪節 / 或已知風險）

| 級別 | 發現(摘) | 處置 |
|---|---|---|
| **critical** | exact 檢索路徑 fail-open：RBAC 閘塞 `extra` 會在 `_item_citations`(只帶 `{clean}`)被丟棄→洩漏全域 | **已修入 §5**：RBAC 收進 `corpus.rbac_domain_sql()` SSOT、三端 import、修 `_item_citations` where 納 RBAC、加 CI lint 單測 |
| **critical** | pgcrypto 未裝(`pg_extension={plpgsql,vector}`)、`augur` 非 superuser 無權 CREATE EXTENSION；token 隨機源寄望 pgcrypto→遷移爆或空 token 冒用 | **已修入 §3.4/§3.6**：移除 `CREATE EXTENSION pgcrypto`；`gen_random_uuid()` 用 PG17 核心；token 由應用層 CSPRNG、DB 存 sha256、`token_hash` 加 `NOT NULL`+`len≥32` CHECK |
| **critical** | 冪等造假：`ADD CONSTRAINT` 無 `IF NOT EXISTS`，二跑即 abort | **已修入 §4**：沿用既有 `migrate_text_understanding_ddl.py` 之 `pg_constraint` guard(`DO $$`/`ensure_constraint`) |
| **critical** | 與現行 admin console 脫節：`serve_admin_console.py` 是 env 單密碼 + 記憶體 `_SESSIONS` dict、無 user/role/uid；RBAC 閘取不到 uid＝形同虛設 | **已知風險(§8 待拍板 #6)**：DDL 無消費端。**RBAC 落地前置依賴＝改造 admin console 認證層**(登入改查 `app_user`+寫 `app_session`、記憶體 session 換 DB)。屬決策層拍板，本報告停下問、不暗示可直接落地 |
| **high** | domain 無 CHECK/無 FK 當授權邊界，誤標即越權 | **已修入 §3.3a**：建 `knowledge_domain` 字典 + grant.domain FK；item.domain FK 屬 §8 G1 決策 gate(兩段式 NOT VALID) |
| **high** | 事實錯誤:哲學層其實**有** `philosophy_school.domain varchar(32)`，舊版誤稱「哲學無 domain」 | **已修正(見下 G2/G4)**：`philosophy_school` 確有 `domain`(varchar **32**，與 item 的 64 型別/詞彙皆異)，**但** `philosophy_work` 經 `thinker_id→philosophy_thinker` **無 `school_id`**——`school_id` 只在 `philosophy_principle`/`philosophy_source`。故**哲學全文(`philosophy_work_text`)無可遍歷 FK 路徑到 `philosophy_school.domain`**；逐域授權須加欄或建映射。現採固定 `'philosophy'` 域(§5)，並誠實標為「未落到全文可 JOIN 之實欄」 |
| **high** | 有效性 fail-open：授權子查詢不含 `is_active`/`revoked_at`/`expires_at`；停用/登出仍越權；停用 superuser 仍全放行 | **已修入 §3.4/§3.7/§5**：`v_user_allowed_domain` JOIN `app_user AND u.is_active`；superuser 分支加 `AND u.is_active`；uid 由受驗 session 解析(revoked_at/expires_at gate) |
| medium | grant.domain 是否 FK 自相矛盾 | **已統一(§3.3)**：建字典、兩側皆可 FK、刪除「不加 FK」錯誤前提 |
| medium | 重寫六軸述詞違反 SSOT #12 | **已修入 §2/§5**：一律 import `corpus.py` 片段，RBAC 只 append (e) |
| medium | 111k 列加 FK 未用 NOT VALID | **已修入 §4**：兩段式 `NOT VALID`+`VALIDATE` |
| medium | pgcrypto 臆造依賴 | 同上 critical，**已修** |
| medium | password_hash 長度 CHECK 是安全劇場 | **已修入 §3.6**：改擋裸 hex/明文(`LIKE '$argon2%'/'$2b$%'`)、誠實標 DB 不保證強度 |
| medium | owner `ON DELETE SET NULL` 製造無主 private 孤兒；一致性 CHECK 版本間消失 | **已修入 §3.5/§4**：改 `ON DELETE RESTRICT`、統一加 `chk_itext_private_owner` 硬牆 |
| medium | domain 詞彙跨表分裂→授權綁錯來源 | **已修入 §3.3a**：字典只從 `knowledge_item.domain` 回填，不混 source/staging/query 側 |
| low | username 大小寫繞授權 | **已修入 §3.1**：`lower(username)` 唯一索引 |
| low | review_flag NULL 陷阱 | **已修入 §1.5**：維持 `= false`、加單測釘死、放量前補 partial index |
| low | 數字不一致(108k vs 111,259) | **已修**：全報告統一 **111,259**(實測) |

---

## 8. 待決策層拍板

1. **G1｜domain 升級為安全邊界**：`knowledge_item.domain` 現無 FK；是否加 `fk_item_domain`(§4 兩段式，字典已回填全值故安全)。屬「升級判準」——RBAC 上線前必須完成，否則邊界不可信。
2. **G2/G4｜哲學層 domain 落點**：`philosophy_school.domain`(varchar 32)存在但 `philosophy_work` 無可遍歷 FK 到它。二擇一：(a) 永久定哲學層為單一 `'philosophy'` 域(現採)，或 (b) 對 `philosophy_work` 加 `domain varchar(64)` 欄使軸真正落實欄。現狀「字面量常量」須明標未落實欄。
3. **是否重命名 access_scope 值**：把 `public` 改名 `shared`/`org` 徹底消歧義——但改值域要動 DB CHECK + 既有資料遷移，須拍板。
4. **研發群組涵蓋哪些 domain**：`rd_mgmt` 之外是否含 `production_mgmt`/`engineering`…；群組清單全集。
5. **private owner 模型 + owner 刪除策略**：`ON DELETE RESTRICT`(現採) vs CASCADE；是否開放 local_private 檢索路徑(前置＝owner 落地回填)。
6. **認證層調和(承 §7 critical#4)**：RBAC 落地前置＝改造 `serve_admin_console.py` 登入/會話層接上 DB `app_user`/`app_session`。無此則 RBAC DDL 無消費端。

---

## 附錄：真實 schema dump 摘要（事實來源 #1）

**環境**：PG 17.9，DB=`augur`，`current_user=augur`，`rolsuper=false`，`pg_extension = {plpgsql, vector}`(**無 pgcrypto**)。**無**任何 user/role/session/auth/acl/permission/grant/account 表(ILIKE 全 0 命中)。`knowledge_item` = **111,259** 列。

**六軸 CHECK(逐字，`pg_get_constraintdef`)**：
- `knowledge_item_text_license_check` = `license = ANY (ARRAY['public_domain','cc-by','cc-by-sa','cc0'])`
- `chk_itext_access_scope` = `access_scope = ANY (ARRAY['public','local_private'])`
- `chk_itext_source_type` = `source_type IS NULL OR source_type <> 'ai_generated'`
- `philosophy_work_corpus_class_check` = `corpus_class = ANY (ARRAY['literary','reference'])`
- `philosophy_work_text_license_check` = `license = 'public_domain'`(單值、比知識側嚴)
- `philosophy_work_work_type_check` = `work_type <> 'ai_generated'`
- `philosophy_work_reviewed_by_check` = `reviewed_by = ANY (ARRAY['audit','provenance','human'])`
- `knowledge_sentence_check` = `num_nonnulls(text_id, itext_id) = 1`(XOR)

**關鍵型別**：`knowledge_item.domain varchar(64) NOT NULL`(無 CHECK/無 FK)；`knowledge_item_text`{`license varchar(64)`, `access_scope varchar(16) DEFAULT 'public'`, `source_type varchar(24)`}；`philosophy_work`{`corpus_class varchar(16) DEFAULT 'literary'`, `review_flag boolean`(三態)}；`philosophy_work_text.license varchar(32) DEFAULT 'public_domain'`；`philosophy_school.domain varchar(32)`(型別≠item)。

**索引**：`idx_item_domain btree(domain, entity_type)` 存在(RBAC domain 過濾受惠)；`knowledge_item_text` 僅 PK/UNIQUE(`item_id,seq`)/`idx_itext_item`——六軸述詞(license/access_scope)無索引、放量前補 partial index。

**FK 關鍵**：`philosophy_school(school_id)` ←`philosophy_principle`/`philosophy_source`(**非** `philosophy_work`)；`philosophy_work → philosophy_thinker`(無 `school_id`)→ 哲學全文無路徑到 `school.domain`。

**現庫分布**：access_scope 全 `public`(13)、license 全 `cc-by`(13)、source_type 全 `NULL`(13)、corpus_class literary 1528/reference 7、review_flag false 1166/NULL 218/true 151、domain 40 種(medicine 12262…rd_mgmt 2697…business_mgmt 2822…+general 15，**無 `local` 域實列**)。

**述詞 SSOT(真實 code)**：`corpus.LICENSE_WHITELIST=('public_domain','cc-by','cc-by-sa','cc0')`；`SEMANTIC_ENTITY_TYPES=('paper','report','document')`；`clean_item_sql`/`clean_work_sql` 產出述詞、`retrieve_items` 三分支 import(exact citation 分支 `_item_citations` 目前只帶 `{clean}` 未帶 `{extra}`——見 §5 修法)。既有冪等 guard 慣例＝`scripts/migrate_text_understanding_ddl.py:ensure_constraint()`(`pg_constraint` 查表)。
