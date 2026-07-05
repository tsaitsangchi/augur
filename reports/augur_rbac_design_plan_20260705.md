🎯 **這份是什麼**：把 augur 從「單人本地工具」升為「一位主使用者(superuser)＋受控多使用者群組」的知識讀取存取控制(RBAC)完整設計計畫。核心命題只有一句——**讓「誰能讀哪些知識 domain」變成 server-side SQL 強制、預設 deny、fail-closed 的機器邊界**，而**絕不**因此鬆動知識↔預測的命門隔離。本計畫已逐條吸收三輪紅隊(privesc / leak / complete)發現，critical/high 全數處理(修進設計或明列已知風險＋緩解)。

**守原則 #1(source-pure 命門零妥協) #5(不引入安全漏洞) #19(治權升版逐檔一致)**
日期：2026-07-05

---

## 0. 目標與三條紅線

### 0.1 目標

augur 現況是**單人本地工具**：後台 :8500 靠單一 env `AUGUR_ADMIN_PASSWORD`、前台 :8090 與 advisor 殼 :8399 **零鑑權**、對話檢索 `retrieve_all` 寫死 `access_scope='public'` 且從不傳 domain。目標是升為：

- **一位主使用者(superuser)** 得見全部知識 domain；
- **受控多使用者群組**：每個群組經 `group_domain_grant` 授予若干 domain，使用者的可見範圍＝所屬群組 grant 之**聯集**；
- **預設 deny**：無 grant ＝ 看不到任何 domain；
- **server-side 強制**：enforcement 一律在檢索層 SQL，UI 隱藏不算數；
- **資料驅動零改碼**：加使用者/加群組/授權皆 INSERT(對映 CLAUDE #29(b))。

### 0.2 三條紅線(不可逾越，每章 gate 逐一釘死)

**紅線 1 — 不碰 #1 命門隔離。**
RBAC 只作用於「素養/顧問層內部：人能讀哪些 domain」。知識↔預測之三道機器防線**原封不動、絕不弱化/繞過/找理由變更**：
- (a) AST import-lint(`tests/test_philosophy_isolation.py`)：預測 7 package(`features/models/universe/evaluation/ingestion/audit/catalog`)零 import `augur.philosophy`/`augur.advisor`/`augur.knowledge`；
- (b) 唯讀單向依賴、對話單閘(`advise()`+`guard`)；
- (c) #1 source-pure + CLEAN 述詞 fail-closed(`corpus.clean_item_sql`/`clean_work_sql`)。
RBAC 的 domain 過濾**只能是在 CLEAN 述詞之上再 AND 收窄的加法**，絕不改寫 CLEAN 本身(license/review_flag/entity_type/fail-closed)。superuser 也**不得**讀未過 CLEAN 的內容、不得觸預測表。

**紅線 2 — domain 標註即安全邊界。**
domain 現行職責＝因子鏈純度隔離(`domain='investment'` 唯一因子路)。RBAC 讓它兼任授權邊界後，**入庫時 domain 標錯＝越權洩漏**。現況 `knowledge_item.domain` 是 `varchar(64) NOT NULL` **無 FK 自由字串**，無字典表擋錯拼/幽靈 domain。本計畫以 `knowledge_domain` 字典表 + FK + fail-closed 補 referential integrity，並誠實標明「入庫標註正確性」是 enforcement 之外的獨立命門(P2 hygiene + 常備稽核器)。**domain 的因子鏈隔離語意不因 RBAC 而改變。**

**紅線 3 — 系統定位擴張須升治權。**
「單人本地(就是你)」是靈魂 `docs/系統核心思想_v1.4.0.md`「為誰」節的明文根定義。擴為「多使用者群組」＝**動靈魂 v1.4.0→v1.5.0 ＋ 憲章 v1.25.0→v1.26.0**，屬**決策層拍板**(CLAUDE #19/#26)。AI 只呈 DDL/resolver/憲章 diff、在 clean-room 非生產庫建置實測，**絕不自行 migrate 生產庫**、絕不先於治權升版拍板動生產身分表。

---

## 1. 現狀 → 目標(grounding 檢索路徑清單表)

### 1.1 現況三層零鑑權(即時越權面)

| 服務 | 檔案 | 現況 | 即時風險 |
|---|---|---|---|
| 後台 :8500 | `scripts/serve_admin_console.py` | 單一 env `AUGUR_ADMIN_PASSWORD`(L449)；session＝記憶體 `_SESSIONS`(L130)；`hash_password`(L49)/`verify_password`(L55) 雜湊穩健 | 無帳號/角色/群組；cookie 缺 `Secure`；`/login` 無節流(L455 只記不擋) |
| 前台 :8090 | `scripts/serve_chat_ui.py` | **完全無登入、無 session**(`do_GET` L171、`do_POST` L256 零 auth)；`/chat` 原樣 proxy 到殼(L285)不夾身分 | **最大即時越權面**：任何可達者無條件取全庫檢索 |
| advisor 殼 :8399 | `scripts/serve_advisor_openai.py` + `src/augur/advisor/oai_compat.py` | 明文零 auth(`oai_compat.py:153` 收任意 API key、`do_POST` L174 零鑑權)；L62-63 綁 `retrieve_all` 寫死 `access_scope='public'`、無 per-request 身分注入 | 同機任一進程可直打提權；請求無身分攜帶通道 |

**現況即是「預設 allow」而非 deny**——RBAC 諸表(`app_user`/`permission_group`/`user_group`/`group_domain_grant`/`knowledge_domain`/resolver)全庫 grep 零命中，確為待建。**在 RBAC 落地前，:8090/:8399 須視為「對外即失守」。**

### 1.2 檢索/查詢路徑清單表(每條標 RBAC 接法)

**判準**：凡「回傳知識內容給使用者」的路徑逐條列管。**未接線 ≠ 可豁免**——接線即洩漏者一律列入強制範圍。

| # | 函式 / 檔案:行 | 回什麼 | 現況吃 domain? | RBAC 接法 |
|---|---|---|---|---|
| 1 | `retrieve_all` `retrieval.py:299` | works+items 合併(對話端唯一組合檢索器，殼綁此) | 否(寫死 public、不傳 domain) | 新增 `scope`(**無預設，缺即 raise**)，透傳給 `retrieve_items`；works 側依 #3 裁決 |
| 2 | `retrieve_items` `retrieval.py:244` | items 側逐字句(`ItemCitation` 含 `.domain`) | 半有(單值 `domain=None`＝不濾，且 `retrieve_all` 不傳) | **語意反轉**：domain 述詞併入 `clean_item_sql`，非 super 且空集→`AND false`；exact 候選(L269)+exact 取原文(L274)+ann(L288) **三段皆帶** |
| 3 | `retrieve` `retrieval.py:64` | works 側逐字 chunk；`philosophy_work`(`framework.py:74`)**無 domain 欄、且未過 `clean_work_sql`** | **否**(結構性缺口) | **P3 硬前提二選一**：(A) 加 domain 欄+FK 走同閘；(B) 憲章明訂公版哲學/文學為保留 domain `philosophy_public` 納入預設 grant。**裁決前對非 super 程式預設 deny**；並須先補 `clean_work_sql` |
| 4 | `retrieve_attached` `retrieval.py:339` | 本次上傳附檔逐字段落(Mode B) | 否(不觸 DB) | **domain 豁免**(內容屬上傳者)，但**上傳/檢索須登入**；lambda 顯式 `scope=None` 忽略、禁 `**kw` 靜默吞 |
| 5 | `lexicon_lookup` `retrieval.py:147` | 公版辭書/註疏逐字定義 | **否**(無 domain、**無 clean_work_sql**) | 現況未接線(advise 不傳 lex_terms)但**接線即洩漏**；接線 PR 必帶 works 側 CLEAN + 公開裁決 |
| 6 | `concordance_lookup` `retrieval.py:172` | items 側逐字用例原句 | **否**(**連整個 CLEAN 閘都沒過**——無 license/entity_type/domain) | 現況未接線但接線洩漏的是**繞過 #1 命門**的內容(非只跨 domain)；接線 PR 必帶 `clean_item_sql`(含 domain)+ works 側 `clean_work_sql` |
| 7 | `verify_verbatim`/`_item`(`:92`/`:310`) | 不新增內容，只 bool 驗逐字性 | — | 非洩漏面；但 domain 過濾須在 **citation 產生之前**(SQL WHERE)，否則驗過的仍是越權列 |

**橫切鐵則**：`clean_item_sql`(`corpus.py:36`)是 items 側唯一 CLEAN 閘、已支援 `access_scope` server-side 強制(封閉集字面內插、fail-closed)。RBAC 的 domain 強制**最自然落點＝把 domain 收進 `clean_item_sql`**(單一住所 #12)。works 側(#3/#5/#6 的 works 部分)**目前無此類閘**，是 RBAC 的結構性缺口，必須正面裁決。

---

## 2. 資料模型(DDL，真實欄型、多對多、資料驅動)

全部住 `augur.knowledge` 對應之新 migration `scripts/migrate_rbac_ddl.py`(仿 `migrate_text_understanding_ddl.py` 之 idempotent `CREATE TABLE IF NOT EXISTS`；`import _bootstrap` 個別可執行、指令矩陣、無參 graceful — CLAUDE #29)。**不混入** `migrate_text_understanding_ddl.py`(職責隔離)。

> **命名 SSOT(定稿收斂，消除六視角漂移)**：resolver 模組＝`src/augur/knowledge/access.py`；user/授權 CLI＝單一 `scripts/manage_rbac_user.py`；前台+後台共用 session 表＝`app_session`；共用密碼/session 模組＝`src/augur/knowledge/identity.py`；主鍵一律 `bigint GENERATED ALWAYS AS IDENTITY`(PG10+ 標準)。各章一律引用此表，禁再造別名。

### Step 0 — `knowledge_domain` 字典表(紅線 2 的 referential-integrity 地基)

```sql
CREATE TABLE IF NOT EXISTS knowledge_domain (
    domain            varchar(64) PRIMARY KEY,        -- 對齊 knowledge_item.domain 欄型
    label_zh          varchar(128) NOT NULL,
    is_authz_boundary boolean NOT NULL DEFAULT false, -- 未拍板=不可被 grant 引用、不可預設可見
    is_investment     boolean NOT NULL DEFAULT false, -- domain='investment' 唯一因子路;與 RBAC 正交
    enabled           boolean NOT NULL DEFAULT true,
    note              text,
    created_at        timestamptz NOT NULL DEFAULT now()
);
```
種子＝**先實查** `SELECT DISTINCT domain FROM knowledge_item` 拉現存真值 + `knowledge_domain_map` 的 `augur_domain` 值域，**逐一人工拍板** label 與 `is_authz_boundary` 後 INSERT。**禁 `INSERT ... SELECT DISTINCT` 批量吸納**(會把入庫時標錯的域合法化)。

### Step 1 — `app_user`(身分主體，無 role 欄)

```sql
CREATE TABLE IF NOT EXISTS app_user (
    user_id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username       varchar(64)  NOT NULL,
    pw_hash        text         NOT NULL,          -- 'pbkdf2$<iter>$<salt>$<hash>',復用 identity.hash_password
    is_superuser   boolean      NOT NULL DEFAULT false,  -- resolver 短路旗標,非 role
    is_active      boolean      NOT NULL DEFAULT true,
    failed_logins  integer      NOT NULL DEFAULT 0,
    locked_until   timestamptz  NULL,
    last_login_at  timestamptz  NULL,
    created_at     timestamptz  NOT NULL DEFAULT now(),
    updated_at     timestamptz  NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_app_user_username ON app_user (lower(username));  -- 大小寫不敏感,防分身
```
**刻意不設 `role` 欄**：權限一律經 `user_group` grant 聯集外掛，`is_superuser` 只是 resolver 的明確分支(→ALL)，避免 role 成隱性權限來源。

### Step 2 — 群組 + 兩張多對多連結表

```sql
CREATE TABLE IF NOT EXISTS permission_group (
    group_id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    group_name varchar(64) NOT NULL UNIQUE,       -- 研發組 / 財經組 / 管理員
    note       text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_group (           -- 多對多①: 一人可多群組
    user_id    bigint NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    group_id   bigint NOT NULL REFERENCES permission_group(group_id) ON DELETE CASCADE,
    granted_at timestamptz NOT NULL DEFAULT now(),
    granted_by varchar(64),                        -- 稽核:誰把此人加進此群組(#10 可溯源)
    PRIMARY KEY (user_id, group_id)
);

CREATE TABLE IF NOT EXISTS group_domain_grant (   -- 多對多②: 一群組可授多 domain
    group_id   bigint      NOT NULL REFERENCES permission_group(group_id) ON DELETE CASCADE,
    domain     varchar(64) NOT NULL REFERENCES knowledge_domain(domain),  -- FK 硬擋幽靈/拼錯 domain
    granted_at timestamptz NOT NULL DEFAULT now(),
    granted_by varchar(64),
    note       text,
    PRIMARY KEY (group_id, domain)
);
```
**加第四個領域群組(如化學研究組)＝`INSERT permission_group` + 若干 `INSERT group_domain_grant`，零 code 變動**(對映 #29(b))。

### Step 3 — `app_session`(持久化，前後台共用)

```sql
CREATE TABLE IF NOT EXISTS app_session (
    token_hash   text        PRIMARY KEY,          -- sha256(token);DB 不存明文 token(見 §6 H8 緩解)
    user_id      bigint      NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    issued_at    timestamptz NOT NULL DEFAULT now(),
    expires_at   timestamptz NOT NULL,
    last_seen_at timestamptz NOT NULL DEFAULT now(),
    revoked_at   timestamptz NULL,                 -- 主動登出/停用;非 NULL 即失效
    client_note  varchar(128) NULL,                -- admin/chat/emergency;非授權欄
    client_ip    inet        NULL
);
CREATE INDEX IF NOT EXISTS idx_session_user   ON app_session(user_id);
CREATE INDEX IF NOT EXISTS idx_session_expiry ON app_session(expires_at);
```
取代後台記憶體 `_SESSIONS`。**cookie 存明文 token，DB 只存 `sha256(token)`**——DB 外洩不直接得可用 token。有效判定(fail-closed，全 AND)：`revoked_at IS NULL AND expires_at > now() AND app_user.is_active`。

### Step 4 — `knowledge_access_audit`(稽核落 DB)

```sql
CREATE TABLE IF NOT EXISTS knowledge_access_audit (
    audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id  bigint,                               -- NULL=匿名/未登入嘗試
    action   varchar(32) NOT NULL,                 -- login/login_fail/retrieve/grant/revoke/set_super/emergency
    domains  text,                                 -- 本次 scoped 之 allowed_domains(#10 可溯源)
    is_super boolean,
    outcome  varchar(16) NOT NULL,                 -- ok/deny/empty/fail
    detail   text,
    at       timestamptz NOT NULL DEFAULT now()
);
```

### Step 5 — `local_private` 擁有者欄(多使用者歸屬，紅線 2 衍生)

多使用者下 `access_scope='local_private'` 的「本機那個人」語意斷裂。`knowledge_item_text`(`migrate_text_understanding_ddl.py:110`)只有 `access_scope`、**無 owner**。

```sql
ALTER TABLE knowledge_item_text ADD COLUMN IF NOT EXISTS owner_user_id bigint REFERENCES app_user(user_id);
```
**在 owner 欄回填前，程式層強制 `local_private` 內容僅 superuser 可見**(不靠文件承諾，見 §4 / §6 H7)。

---

## 3. 認證流程(後台+前台、bootstrap、env 後門、密碼雜湊)

### 3.1 密碼雜湊(維持 pbkdf2 240k，前向相容)

沿用 `serve_admin_console.py:hash_password`(L49，pbkdf2_hmac sha256 / 240000 iter / 16-byte salt)/`verify_password`(L55，`hmac.compare_digest`)。**理由**：零新依賴(標準庫)、威脅模型匹配(綁 127.0.0.1、小使用者數)、已 ≥ OWASP 210k 門檻。**抽為共用** `src/augur/knowledge/identity.py`(三端 import 同一份，禁 inline 複本 #12)。演算法前綴(`pbkdf2$...`)保升級路；`verify_password` 對**未知前綴一律回 False**(fail-closed，不 raise)。透明 rehash 僅在登入成功、明文在手時於記憶體重算，**算完即棄、永不 log/落盤明文**。

### 3.2 後台 + 前台共用 identity 模組

`identity.py` 內容：`hash_password`/`verify_password`、`issue_session(user_id)→token`、`verify_session(token)→user_id|None`(持久化版，每請求查 `app_session` gate)、`revoke_session`/`revoke_user_sessions`。後台 L49/L55/L130/L173/L179 遷出改 import；前台 `do_POST`(L256)新增 auth gate 呼叫同一 `verify_session`。**驗證函式自身 fail-closed**(token 無效/過期/帳號停用一律回 None)，呼叫端無從放寬。

### 3.3 後台認證(app_user-first、env-fallback 相容期)

`/login`(L445)改為：先查 `app_user`(username + `verify_password`) → 查無再 fallback env `AUGUR_ADMIN_PASSWORD`(相容期)。env 命中授**臨時 superuser-等效 session**、`client_note='emergency'`、強制 `knowledge_access_audit(action='emergency')` + warning log。

### 3.4 前台登入(整套新增，預設 deny)

```
POST /login (form: username, password)
 1. row = SELECT user_id, pw_hash, is_active, is_superuser FROM app_user WHERE lower(username)=lower(%s)  -- 參數化
 2. 常數時間:row 不存在也對 dummy hash 跑一次 verify_password(抹平 username 列舉時間側信道)
 3. 通過且 is_active → issue_session;登入成功一律發【新】token(防 session fixation)
 4. Set-Cookie: sid=<token>; HttpOnly; SameSite=Strict; Path=/  [; Secure 對外強制]
 5. 失敗 → 泛化訊息「帳號或密碼錯誤」(不區分無帳號/密碼錯);failed_logins++、達閾值設 locked_until(指數退避)
```
每請求 `_current_user()`(前置於 `/chat`/`/ingest`/`/attach`)：`verify_session` → `user_id`；**None → 401，絕無 fallback 到 public 檢索**。

### 3.5 Bootstrap 首 admin(CLI，唯一建帳號路徑)

`scripts/manage_rbac_user.py`(單一參數化工具 #29(c))：
```
python scripts/manage_rbac_user.py --create-user --username hugo --superuser   # 密碼走 getpass,禁 argv
python scripts/manage_rbac_user.py --set-password --username hugo
python scripts/manage_rbac_user.py --add-to-group --username bob --group 研發組
python scripts/manage_rbac_user.py --grant-domain --group 研發組 --domain investment --confirm
python scripts/manage_rbac_user.py --set-super --username alice --confirm
python scripts/manage_rbac_user.py --deactivate --username bob
python scripts/manage_rbac_user.py --list
python scripts/manage_rbac_user.py --explain-access --username bob   # 列哪些群組貢獻哪些 domain
```
- **bootstrap 順序鐵律**：首 user 必為 `--superuser`(空表 `count(*)=0` 才允許無授權建)；表非空且未帶 `--superuser` → **拒絕並提示**(fail-closed，不默默建無權孤兒或臨時全開)。
- **`--grant-domain`/`--set-super` 須 `--confirm`**(授權某次 ≠ 授權所有同類 #6)且 audit 落 DB；密碼走 `getpass`(禁 `--password` argv 入 shell history)。
- **復原路徑**：所有 superuser 皆 inactive/鎖定時，CLI 本機信任邊界可 `--reactivate`/`--set-super` 重建，不依賴 env。

### 3.6 env 緊急後門(預設【硬】關閉)

**修正六視角「建議關閉」為硬預設 deny**：`AUGUR_EMERGENCY_BACKDOOR` 未設 ＝ 後門**完全停用**。啟用時：僅後台 127.0.0.1、僅 superuser-等效、**短 TTL**、每次強制 audit + warning、`client_note='emergency'`、**該 session 不可被前台通道複用**(前台只認 `app_user`)。`.env` 保護(#5)不因後門放寬。長期以 break-glass 一次性 token(用後失效)取代常駐 env 密碼。

### 3.7 帳號停用 / 密碼更換(即時失效)

停用：`UPDATE app_user SET is_active=false` **同交易** `revoke_user_sessions(user_id)`；且 `verify_session` gate 每請求查 `is_active` 為第二道保險(**下一請求即失效**，不等 TTL)。改密：`hash_password(新)` + `revoke_user_sessions`(強制重登)。**後台 session 一併遷 `app_session`**(消除紅隊指出的「記憶體 session 撤不到」矛盾)。

---

## 4. 授權與強制(allowed_domains resolver + 逐路徑 server-side SQL，預設 deny)

### 4.1 resolver — `resolve_allowed_domains(user_id) → (is_super: bool, allowed: frozenset[str])`

住 `src/augur/knowledge/access.py`。**嚴格三態、型別分離**(吸收紅隊「空集 vs NULL 混淆 fail-open」)：

```python
def resolve_allowed_domains(user_id):
    """回 (is_super, allowed)。
    superuser         → (True,  frozenset())     # is_super=True 時 allowed 忽略
    非 super 有 grant → (False, frozenset(域聯集))
    其餘一切(user 不存在/inactive/無 grant/DB 拋錯) → (False, frozenset())  # fail-closed,絕不當 super、絕不 raise 到吐全庫
    """
    # is_super 只能來自【單列、無 JOIN、無聚合】:
    #   SELECT is_superuser FROM app_user WHERE user_id=%s AND is_active
    #   查無/多列 → 視為 (False, frozenset())
    # 非 super 的 allowed:
    #   SELECT COALESCE(array_agg(DISTINCT g.domain) FILTER (WHERE g.domain IS NOT NULL), '{}')
    #   FROM user_group ug JOIN group_domain_grant g USING(group_id) WHERE ug.user_id=%s
```

**關鍵安全語意**：
- **不用「None＝ALL」的隱式哨兵**——`is_super` 與 `allowed` 各自獨立判斷。superuser 走 `is_super=True` 明確分支；非 super 一律走 `allowed`(空集也是集合、不是「不濾」)。
- `array_agg(...) FILTER (WHERE g.domain IS NOT NULL)` + `COALESCE('{}')`：杜絕 `{NULL}`(`= ANY(ARRAY[NULL])` 恆 UNKNOWN 但陣列非空的誤判)。
- resolver **只讀** `app_user`/`user_group`/`group_domain_grant`/`knowledge_domain` 四表，零觸預測表、零觸 `philosophy_work`。
- **`general` 與任何 `is_authz_boundary=false` 的 domain**：對非 super **一律 deny**(不因「字典裡有這列」就可 grant 或預設可見)——關掉紅隊指出的 general backdoor。

### 4.2 enforcement — `clean_item_sql` 改回 `(fragment, params)` 二元組(吸收 high 級「位置參數地雷」)

紅隊三輪一致指出：`clean_item_sql` 現回**純字串**、呼叫端手工按位置拼 params，且 exact 第二段 `_item_citations`(L274)只帶 `{clean}` **不帶 `{extra}`**——domain 若走 `extra` 則此段靜默 fail-open；若把新 `%s` 塞進字串則三處 params 位置全錯位。**修法(必做)**：

```python
def clean_item_sql(item_alias="i", itext_alias="x", access_scope=None,
                   is_super=False, allowed_domains=None):
    """回 (sql_fragment, params:list)。domain 走【參數化】(開放值,非封閉集,不可內插)。
    ⚠ 與舊 domain 參數語意【相反】:非 super 且 allowed_domains 空 → AND false(deny),不是【不濾】。"""
    p = (f"{itext_alias}.license IN ({_quoted(LICENSE_WHITELIST)}) "
         f"AND {item_alias}.entity_type IN ({_quoted(SEMANTIC_ENTITY_TYPES)})")
    params = []
    if access_scope is not None:                      # 封閉集,維持安全字面內插
        assert access_scope in ("public", "local_private")
        p += f" AND {itext_alias}.access_scope = '{access_scope}'"
    if not is_super:
        if not allowed_domains:                       # None 或 [] 皆 fail-closed
            p += " AND false"                          # 預設 deny:無授權域=零可見
        else:
            p += f" AND {item_alias}.domain = ANY(%s::text[])"
            params.append(list(allowed_domains))
    return f"({p})", params
```

呼叫端一律 `frag, fp = clean_item_sql(...); sql += frag; params += fp`——**消除手工位置對齊**。`access_scope` 維持封閉集內插(安全)，domain 走參數化。**exact 候選(L269)、exact 取原文 `_item_citations`(L274)、ann(L288) 三段共用同一 `frag`+`fp`**——一改三處自動同帶，關掉 L274 與 ANN 補位兩個洩漏面。

### 4.3 身分傳遞鏈(前台 → 殼 → SQL；不可偽造 token，吸收 critical IDOR)

**身分不由 client/中間層明文攜帶 domain**(client 可竄改；user_id 是可枚舉小整數＝IDOR)。**每一跳從自己的可信來源解析**：

1. **前台 :8090**：`_current_user()` 由 server 端 session 反查 user_id → **只把 `session_token` 經內部通道傳殼**(不傳 user_id、不傳 allowed_domains)；proxy 前 `body.pop('augur_identity', None)` 剝除前端任何偽造欄。
2. **前台↔殼共享機密 header**：`X-Augur-Internal: <env secret>`(住 `.env`，非 commit #5)。**列為 P4 硬阻斷條件、非「待議」**；header 缺/不符 → 殼 fail-closed 當 `allowed_domains=[]`、`is_super=False`。
3. **advisor 殼 :8399**：**絕不信** body/header 帶入的 `user_id`/`allowed_domains`/`is_super`(一律 pop 忽略)。殼收 `session_token` → **自查** `app_session` 驗有效性 → 取 user_id → **殼自跑** `resolve_allowed_domains`。這是單一權威來源收斂。
4. **殼綁 127.0.0.1**(現況)列為對外開放前 P4 阻斷 gate；loopback 綁定**不當授權**，token 驗證才是。

### 4.4 契約改造(吸收 critical「advise() (query,k) 寫死 + Mode B lambda TypeError」)

`advise.py:33` 現為 `src_fn(query, k=k)` 寫死兩參。**P3 第一步必做**：
- `advise()` 新增 `scope` 參數；L33 改 `src_fn(query, k=k, scope=scope)`；
- `retrieve_fn` 抽象界面統一簽名 `(query, k, scope=None)`；
- **Mode B lambda 顯式** `lambda q, k=k, scope=None: retrieve_attached(...)`(明確忽略，**禁 `**kw` 靜默吞**——靜默吞會讓一般模式 scope 也被丟成 fail-open)；
- `retrieve_all` 簽名 `scope` **無預設，缺即 raise**(消除「忘了傳＝全開」)。
- **fail-closed 保險**：若 scope 因簽名不符被丟，下游 `clean_item_sql` 收 `allowed_domains=None` → `AND false`(deny)，非不濾。

### 4.5 逐路徑接法(§1.2 表 checklist，一條不漏)

- **items 側**(#2/#6-items 來源)：`clean_item_sql`(含 domain)，exact+ann 三段同帶。
- **works 側**(#3/#5/#6-work 來源)：先補 `clean_work_sql`(現況 `retrieve` 連 CLEAN 都沒過)，再依 P3 裁決(A 加 domain 欄 / B 定 `philosophy_public` 保留 domain)；**裁決前對非 super 程式預設 deny**。
- **`local_private`**：`AND (owner_user_id = %s OR is_super)`；owner 欄回填前程式強制僅 super 可見。
- **Milvus/ANN 未來接線**(`retrieval.py:247` 待 N3)：契約寫死——Milvus **只存向量+sent_id(最多 domain scalar)、絕不存原文**；kNN 只回候選 sent_id，**一律回 PG 經 `clean_item_sql`(含 domain)二次授權過濾取原文**(PG 為唯一權威閘)；Milvus filter 僅減候選；不可達→fallback pgvector(有過濾)，**絕不 fallback 無過濾直取**。此不變式接線前入憲章。

### 4.6 誠實閉集不變(空集不洩「你無權」)

RBAC 收窄致主檢索空集 → **走既有三級誠實固定句閉集**(憲章 v1.25.0 line 137，「知識庫中無此內容」)，**不新造「你無權查」回應**。`_verdict_note` 的 `citations` 計數在 RBAC 收窄致空時須與真空一致(都 0)，不洩「過濾前有 N 筆」。空集與「庫中確無」對外**位元級不可區分**；timing 側信道(空集不經 LLM vs 命中經 LLM)列為 low、記錄並在測試斷言回應與延遲不可區分(緩解見 §6 L11)。

---

## 5. 分階段路線圖 P1–P5

> **貫穿**：每階段 resume-safe、可獨立退場(rollback 不損既有資料)、失敗語意 fail-closed。**治權升版拍板(紅線 3)是 P1 對【生產庫】migrate 的前置 gate**(修正六視角「錯綁在 P5」)——P1 前可 clean-room 非生產庫建置實測(執行層)，但任何在生產庫建 `app_user` 並開放第二使用者登入的動作，前置＝靈魂 v1.5.0 + 憲章 v1.26.0 已拍板。

| 階段 | 目標 | 里程碑 | 退場 | 依賴 |
|---|---|---|---|---|
| **P0(前置)** | 止血現況預設 allow | :8090/:8399 視為「對外即失守」；文件警示；殼綁 127.0.0.1 確認；env 後門硬關 | — | 無(立即) |
| **P1** | 身分基礎設施上線(不碰檢索) | `migrate_rbac_ddl.py` 建 6 表(§2)；`identity.py` 抽共用；`manage_rbac_user.py`；後台 `/login` app_user-first+env fallback；後台 session 遷 `app_session` | drop 6 表、還原 import | **治權升版拍板**、`hash_password` 復用 |
| **P2** | domain 標註 hygiene + FK(檢索仍未 scoped) | 孤兒查詢回 0 列；`knowledge_domain` 種子人工拍板；`knowledge_item.domain` **兩階段 FK**；`general`/`local_private` 歸屬拍板；`audit_domain_hygiene.py` 常備稽核器 | drop FK/字典表 | P1 字典表 |
| **P3** | 檢索層 server-side domain 強制(核心，預設 deny) | `access.py` resolver；`clean_item_sql` 改 `(frag,params)`+domain；**advise 簽名改造+Mode B lambda 相容(第一步)**；exact+ann 三段同帶；**works 側正面裁決**；concordance/lexicon 補 CLEAN；越權迴歸測試綠 | 還原 `retrieve_*` 簽名 | P2 FK、契約改造 |
| **P4** | 前台登入 + 身分一路傳到檢索 | 前台整套 auth；`app_session` 共用；殼收 `session_token` 自查+自 resolve；`X-Augur-Internal` 共享機密(硬阻斷)；登入節流；`/attach` 須登入 | 前台回唯讀展示或關閉 | P3 resolver、殼改造 |
| **P5** | env 單密碼退場(相容期收束) | 核對 `is_super AND is_active ≥1`；稽核 log 近 N 日無 env 命中；移除 `/login` env fallback | 保留 env 旁路 | P1-P4 完成 + 治權升版已生效 |

**兩階段 FK(吸收 high 級「ALTER ADD CONSTRAINT 全表鎖」)**：
```sql
-- 前提:孤兒查詢回 0 列;字典表 domain 為 PK(FK 目標須唯一索引,已滿足)
ALTER TABLE knowledge_item ADD CONSTRAINT fk_item_domain
    FOREIGN KEY (domain) REFERENCES knowledge_domain(domain) NOT VALID;   -- 短鎖、不掃全表、即時對新寫入生效
ALTER TABLE knowledge_item VALIDATE CONSTRAINT fk_item_domain;            -- SHARE UPDATE EXCLUSIVE、可與讀寫並行
```
**DDL 時機鐵律(#30)**：排在 `pg_dump` 完成後、執行前查 `pg_stat_activity` 確認無 active dump(否則撞鎖佇列 hang 全庫)。

**P5 gate(紅線 3)**：`is_super AND is_active ≥1` 未過**不移除**(防不可逆鎖死)；治權升版未生效**不移 code**(CLAUDE #26 碰護欄即停)。

---

## 6. 安全對抗審結論(紅隊 critical/high 逐條 — 本計畫核心)

三輪紅隊(**privesc / leak / complete**)。**統計：critical 10、high 9，全數處理**(修進設計節，無「修不了」項；殘留者明列已知風險+緩解)。medium/low 一併處置。

### 6.1 Critical(10 / 10 全數修入設計)

| # | 紅隊發現 | 處置 | 修入節 |
|---|---|---|---|
| C1 | **現況預設 allow**：:8090/:8399 零鑑權 + `retrieve_all` 寫死 public + `domain=None`＝不濾，RBAC 未落地前任何可達者取全庫 | **P0 止血**(視為對外即失守)；domain 語意在 `clean_item_sql` 反轉為 fail-closed；任一跳缺身分＝`allowed_domains=[]`/`is_super=False` | §0.1、§1.1、§4.2、§5-P0 |
| C2 | **身分未端到端 + 殼零 auth = 前台繞過 + user_id IDOR 提權**(直打 :8399 改 user_id=1 冒充首 superuser) | 前台只傳**不可偽造 session_token**、殼自查 DB 自 resolve；`X-Augur-Internal` 共享機密**硬阻斷**；殼 pop 忽略 body 任何身分欄；缺身分預設 deny | §4.3 |
| C3 | **resolver 空集 vs NULL 混淆 fail-open**(None＝ALL 隱式哨兵、`{NULL}` 陣列誤判、is_super 聚合誤真) | resolver **嚴格三態、型別分離**：`(is_super:bool, allowed:frozenset)`；is_super 單列無 JOIN；`FILTER(WHERE domain IS NOT NULL)`+`COALESCE('{}')`；禁「None 當 ALL」 | §4.1 |
| C4 | **works/lexicon/concordance 結構性繞過 domain**(`philosophy_work` 無 domain 欄；`retrieve_all` 每次取一半 works) | **works 側 P3 硬前提二選一(A/B)、裁決前對非 super 程式預設 deny**；不得 items 先接 works 後裁決 | §1.2#3、§4.5、§5-P3 |
| C5 | **concordance_lookup 連整個 CLEAN 閘都沒過**(缺 license/entity_type/review_flag，非只缺 domain)＝接線即繞 #1 命門 | 從「缺 domain」**升級標記為「缺整個 CLEAN 閘、屬 #1 命門洩漏面」**；接線 PR 必帶 `clean_item_sql`+works 側 `clean_work_sql`；lexicon 同補 | §1.2#5#6、§4.5 |
| C6 | **advise() `(query,k)` 寫死 + Mode B lambda `(q,k)`**：透傳 scope 屬臆造契約，落地即 TypeError | **P3 第一步**改 `advise` 簽名 + L33 + 統一 `retrieve_fn(query,k,scope=None)` + Mode B lambda 顯式 `scope=None`(禁 `**kw` 吞) | §4.4 |
| C7 | **預設 deny 未真正貫穿**：works 側不經 `clean_item_sql`、殼綁定寫死 public，works 半邊事實上預設 allow | works 側**程式預設 deny**(非文件承諾)；`retrieve_all` scope **無預設缺即 raise** | §4.4、§4.5、§5-P3 |
| C8 | **隔離測試不掃 `scripts/` + `augur.core` 不在 FORBIDDEN**：resolver 便宜行事收進 `augur.core` 即開知識→預測旁路破 #1 | **必建三測**(見 6.4)：測試掃描面涵蓋 `scripts/` + **正向 assert resolver 模組路徑 ∈ FORBIDDEN 三前綴**；明文禁 RBAC 查詢置於 `augur.core`；grep-lint 掃 `augur.core` 亦納入 | §6.4、§8 |
| C9(=C4 leak 版) | works 側照 P3「items 先接、works 待裁決」落地即刻對所有群組吐哲學/文學逐字語料 | 同 C4：兩側同一 PR 決斷 | §4.5 |
| C10(=C2 leak/complete 版) | 殼身分契約三段漂移(傳 token/user_id/domains 未收斂) | **收斂為單一 token 契約**(§4.3)；命名 SSOT 表(§2) | §4.3、§2 |

### 6.2 High(9 / 9 全數修入設計)

| # | 紅隊發現 | 處置 | 修入節 |
|---|---|---|---|
| H1 | **`clean_item_sql` 字串片段 + 位置參數手動穿線**：加 `%s` 三處錯位、L274 只帶 clean 不帶 extra | **改回 `(fragment, params)` 二元組**；domain 進 clean(非 extra)；三段共用同一 frag+params | §4.2 |
| H2 | **ANN 補位漏帶 domain**：exact 濾掉的越權列從 pgvector kNN 補回 | domain 進 clean → exact+ann 三段自動同帶；ann 分支專屬越權迴歸測試 | §4.2、§6.4 |
| H3 | **user_group/is_superuser 純 INSERT 零改碼提權**：任何 DB 寫路徑可自加 admin 群組 | `--grant-domain`/`--set-super` 須 `--confirm`+audit；**寫入以獨立 PG role 收束**(檢索連線唯讀、只 manage CLI 寫角色可改)；`granted_by` + 授權者權限 ≥ 被授範圍檢查 | §3.5、§6.5 |
| H4 | **general backdoor + local 無 owner**：萬用配對 + 本機上傳硬編 `domain=local` + `local_private` 無 owner | general/`is_authz_boundary=false` 域**顯式 deny**；`local_private` 加 `owner_user_id`、回填前僅 super 可見(程式強制) | §4.1、§2-Step5、§4.5 |
| H5 | **session 記憶體/缺 Secure/無節流**：劫持、暴力、無法即時撤銷 | session 遷 DB + 每請求查 `is_active`/`revoked_at`；`token_hash` 存 sha256；對外強制 Secure；`(username,ip)` 失敗計數+`locked_until`；登入發新 token | §2-Step3、§3.4、§3.7 |
| H6 | **`knowledge_item.domain` 無 FK 自由字串**：入庫標註端標錯/未標即越權(enforcement 正確≠安全) | 兩階段 FK；writer pre-INSERT 校驗 domain∈字典且非未拍板域；常備稽核器(仿 `verify_text_integrity.py`) | §5-P2、§8(紅線 2) |
| H7 | **殼內部信任邊界偽冒**：X-Augur-* header/body 可偽造 | 收斂單一 token 契約；共享機密只確認「來源是前台」不取代 token 驗證；殼綁 127.0.0.1 對外前阻斷 | §4.3 |
| H8 | **隔離測試無法斷言 resolver 前綴 + 無越權迴歸測試** | **必建**：resolver 前綴正向 assert + grep-lint + 越權迴歸測試檔(§7)升為交付物 checklist、憲章升版 PR 前置 gate | §6.4、§7、§8 |
| H9 | **access_scope 封閉集內插 vs domain 開放值**：混在同一 SSOT 造參數錯位 | `(fragment,params)` 綁定交付；access_scope 維持封閉集內插、domain 走參數化並隨片段返回其 params | §4.2 |

### 6.3 Medium / Low(處置摘要)

| 級 | 發現 | 處置 |
|---|---|---|
| M | env 後門成永久並行 admin 通道 | 硬預設關閉(`AUGUR_EMERGENCY_BACKDOOR` 未設＝停用)、短 TTL、強制 audit、不可前台複用、break-glass 一次性 token(§3.6) |
| M | rehash 明文誤落盤 + 未知 hash 前綴 fail-open | rehash 僅記憶體算完即棄、禁 log/audit 明文；未知前綴一律 False；pw_hash 僅經 `hash_password` 產、DB role 收束直寫(§3.1) |
| M | Milvus 接線繞過 pgvector domain 過濾 | 接線契約:只回 sent_id、PG 二次授權過濾為唯一權威、fallback pgvector 非無過濾直取；接線前入憲章(§4.5) |
| M | Mode B lambda 不吃 scope 靜默 fail-open | 顯式簽名禁 `**kw` 吞;scope 被丟則下游 `AND false` deny(§4.4) |
| M | 治權升版拍板點錯綁 P5 | **移為 P1 生產庫 migrate 前置 gate**(§5) |
| M | bootstrap 雙 CLl 命名/職責漂移、superuser 全鎖無復原 | 命名 SSOT 收斂單一 `manage_rbac_user.py`;CLI 本機復原路徑不依賴 env(§2、§3.5) |
| M | 兩服務 session 不共享、後台記憶體殘留撤不到 | 後台 session 一併遷 `app_session`(§3.7) |
| M | 後台 `_status_text` 聚合 count 洩全庫規模 | 後台多使用者化時按 allowed_domains 收窄或僅 super 可見(§4.6 延伸) |
| L | 回筆數/citations/延遲存在性側信道 | 空集走既有閉集、citations 收窄致空計 0、timing 遮罩;測試斷言「授權空 vs 庫中無」位元級+時間不可區分(§4.6) |
| L | 命名/DDL identity 慣例漂移 | 命名 SSOT 表 + 主鍵一律 `GENERATED ALWAYS AS IDENTITY`(§2) |

### 6.4 必建機器測試(從紅隊「建議」升為交付物，吸收 C8/H2/H8)

1. **擴 `test_philosophy_isolation.py` 掃描面**涵蓋 `scripts/`；新增正向 assert：RBAC resolver 模組路徑必 ∈ `FORBIDDEN` 三前綴(fail-closed 防誤放 `augur.core`)。
2. **grep-lint**：掃 `features/models/universe/evaluation/ingestion/audit/catalog` **與 `augur.core`** 對 `app_user`/`group_domain_grant`/`allowed_domains` 之字面字串引用 = 0(擋「不 import 但字串拼 SQL」旁路)。
3. **越權迴歸測試檔**(§7 案例落地為 CI；接線 PR 未帶 domain 閘 → CI 拒)。

### 6.5 DB role 收束(縱深防禦，吸收 H3)

檢索連線角色**唯讀**(SELECT 素養表)；`app_user`/`user_group`/`group_domain_grant`/`is_superuser` 之寫入僅 `manage_rbac_user.py` 用的寫角色可改。考慮 `is_superuser` 由可 UPDATE 欄改為需既有 superuser 簽核的 append-only 授權事件表推導(長期)。

### 6.6 誠實 — 殘留已知風險(修不了/待決策，明列不藏)

- **入庫端 domain 標註正確性**：FK 只擋授權端幽靈域，**擋不住 writer 把敏感列標成低敏 domain**。緩解：P2 hygiene + writer pre-INSERT 校驗 + 常備稽核器；**根治須決策層把「domain 標註正確性＝安全命門」評估是否升原則精華**(獨立拍板，非隨 RBAC 自動生效)。
- **works 側 domain 裁決(A/B)**、**`general`/`local_private` 歸屬**、**Milvus 接線契約入憲**：屬**決策層拍板**點，本計畫給出 fail-closed 安全預設(裁決前對非 super deny)，但最終判準須用戶明示。
- **相容期 env 雙軌**：`.env` 洩漏＝直取 superuser。緩解：限最短、audit `login/env-legacy`、P5 log 稽核近 N 日無命中才移除。
- **timing 側信道**：low，位元級一致靠遮罩近似，非數學保證。

---

## 7. 越權測試案例清單(情境 → 期望 deny → 驗法)

| # | 情境 | 期望 | 驗法 |
|---|---|---|---|
| T1 | 新建 user 無任何群組，`retrieve_items` 檢索 | 空集(預設 deny) | 單元：resolver 回 `(False, ∅)` → SQL 含 `AND false` → 0 列 |
| T2 | superuser 檢索 | 不濾 domain(仍過 CLEAN+access_scope) | 單元：`is_super=True` → clean 不含 domain 條款；越權列仍被 license/entity_type 擋 |
| T3 | 研發組(只授 investment)查 philosophy domain 內容 | items 側 deny；works 側裁決前亦 deny | 單元：`allowed={investment}` → philosophy 列不現；works `retrieve` 對非 super 空 |
| T4 | **ANN 補位越權**：exact 撈不到、語意近的他域敏感內容 | ann 段同收窄、不補回 | 單元：造跨域列，exact 空、ann 應補但被 domain 擋 → 0 |
| T5 | **exact 第二段(L274)越權**：候選含他域 sent_id | 最終 citation 不含他域 | 單元：候選跨域，驗 `_item_citations` 用同一含 domain 的 clean |
| T6 | **直打 :8399** body 夾 `augur_identity:{user_id:1,is_super:true,allowed_domains:['*']}` | 殼忽略、fail-closed 空 scope | 整合：無有效 `X-Augur-Internal` + 無有效 token → `(False,∅)` → 空檢索 |
| T7 | **偽造 X-Augur-User-Id header** 直打殼 | 不生效(殼不信 header user_id) | 整合：殼只認 session_token 自查 DB |
| T8 | 前端 body 塞 `augur_identity` 偽造 | 被 `pop` 剝除、以 session 重寫 | 整合：前台 proxy 前 pop |
| T9 | 未登入打 `/chat`/`/ingest`/`/attach` | 401，無 public fallback | 整合：`_current_user()` None → 401 |
| T10 | 停用帳號後既有活 session 續打 | 下一請求即 deny | 整合：`UPDATE is_active=false` → 次請求 `verify_session` 查 is_active 失敗 |
| T11 | RBAC 收窄致主檢索空 | 走既有誠實閉集、**不洩「你無權」** | 單元：空集回應與「庫中確無」位元級一致；citations=0；延遲不可區分 |
| T12 | resolver DB 拋錯/user inactive | `(False,∅)` 空集，**不當 super、不吐全庫** | 單元:catch → `(False,∅)`;新建 inactive user → 空 |
| T13 | `general`/未拍板 domain 內容 | 對非 super deny | 單元：`is_authz_boundary=false` → 不可 grant、不預設可見 |
| T14 | `local_private` 內容(owner 欄回填前) | 僅 super 可見 | 單元：非 super → `AND (owner_user_id=%s OR is_super)` 擋 |
| T15 | Mode B 附檔帶 scope | 不 TypeError、附檔正常、不影響一般模式 scope | 單元：lambda 顯式 `scope=None`；一般模式 scope 仍達 SQL |
| T16 | **隔離**：預測 package import `augur.knowledge` 或 resolver 誤置 `augur.core` | 測試 fail | `test_philosophy_isolation.py` 擴掃 scripts/ + resolver 前綴 assert + grep-lint |
| T17 | 直接對 `knowledge_sentence_embedding` 裸 kNN(繞 `clean_item_sql`) | 無此路徑 | 稽核：確認無 script 對 embedding 表裸查繞 clean |
| T18 | `manage_rbac_user.py --grant-domain` 無 `--confirm` | 拒絕、不 silent INSERT | CLI：預設印警告要求 `--confirm` + audit |

---

## 8. 憲章升版點與禁項紅線

### 8.1 須改治權條文(逐檔一致 #19)

- **靈魂 `docs/系統核心思想_v1.4.0.md` → v1.5.0**：「為誰」節「一個…就是你」→「**一位主使用者(superuser)＋受控多使用者群組(RBAC 讀取控制)**；群組使用者只增/收窄知識 domain 讀取範圍，不改『一個對自己誠實的實踐者』之單一決策主體假設」。
- **憲章 v1.25.0 → v1.26.0 · 第三部橫切 philosophy 層**：新增「**知識存取控制準則(RBAC)**」段——(i) **隔離不受影響條款**(line 138/142/共同不變式①② 不因 RBAC 增刪一字；RBAC 一切表/resolver 住 `augur.knowledge`/`philosophy`/`advisor`/`scripts`、預測 7 package 零 import、**禁置於 `augur.core`**)；(ii) enforcement 一律 server-side SQL、在 `clean_item_sql` 之上 AND 收窄、不改寫 CLEAN；(iii) resolver 語意(superuser→ALL、否則群組 grant 聯集、**空集＝deny**)；(iv) scoped 檢索仍經 `advise()`+`guard` 單閘、不改三級誠實固定句閉集。
- **憲章 line 138**：擴文明載 RBAC 表/resolver 同受零 import 約束；`test_philosophy_isolation.py` 加 resolver 前綴正向 assert + 掃 `scripts/`。
- **憲章 line 142**：明載前台傳身分後 scoped 檢索不繞閘、身分只收窄。
- **憲章第六部修訂歷史**：新增一列「系統定位擴張(單人→多使用者群組讀取控制)」，標**新能力**非新增不可違反原則。
- **`docs/原則精華_v1.7.1.md`**：20 條**預期不動**(RBAC 不觸三敵)。唯一例外＝若決策層把「domain 標註正確性＝安全命門」升為原則層強制(獨立拍板)。
- **CLAUDE.md #29(b)**：RBAC 全資料驅動與 #29 一致、無須改條文，可交叉引用 `knowledge_source` registry 同構。#5 已合規。
- **Milvus 接線不變式**(§4.5)接線前寫入憲章。

### 8.2 禁項紅線(永遠人決策、AI 不自主)

以下屬**決策層**，AI 一律停下問(#19/#26)：
1. 建/改群組、授予/撤銷 `group_domain_grant`(「授權範圍」是決策，非執行，即使零改碼)；
2. 任何 user `is_superuser` 置真；
3. 新 domain 成授權邊界(INSERT `knowledge_domain` + `is_authz_boundary=true` 拍板)；
4. `local_private` 跨使用者可見性歸屬；
5. works 側(哲學/文學)是否納入 domain 邊界(A/B 裁決)；
6. 升靈魂/憲章 RBAC 判準本身。

**RBAC 不得成為知識→預測旁路**(憲章禁項)：(i) `domain='investment'` 因子鏈純度隔離不因 RBAC 增減；(ii) RBAC 表任何欄**禁被預測 7 package 讀取或當特徵**(授權資料不是因子)；(iii) 不得新增「按群組給不同預測」「按 domain 授權觸發特徵計算」路徑——**預測對所有人相同，RBAC 只作用於知識讀取可見性**。三敵(假資料/偷看未來/自我欺騙)零容忍不因 RBAC 鬆動(#27 凌駕邊界)。

---

**收束**：機器隔離(import-lint + 唯讀單向 + CLEAN fail-closed + #1 命門)是不可觸碰地基；RBAC 只在「已 CLEAN 通過的素養內容」之上以 server-side SQL 對「人」加收窄閘、預設 deny、fail-closed。`domain` 由「因子鏈純度隔離」兼任「授權邊界」是最大結構張力，須以 `knowledge_domain` 字典表 FK + 兩階段驗證 + 入庫稽核補 referential integrity。系統定位由單人擴為多使用者群組＝動靈魂 v1.5.0 + 憲章 v1.26.0，屬決策層拍板；AI 只呈 diff、在 clean-room 實測，**絕不自行 migrate 生產庫、絕不先於治權升版動生產身分表**。三輪紅隊 critical 10 / high 9 全數處理，殘留已知風險(§6.6)明列不藏。

**誠實聲明(未測試)**：本文所有 DDL/簽名為**設計稿**，尚未在 repo 實跑或建表。引用之檔案/行號/函式簽名為本 session 真讀所得；`app_user`/`permission_group`/`user_group`/`group_domain_grant`/`knowledge_domain`/`app_session`/`knowledge_access_audit` 諸表與 `access.py`/`identity.py`/`manage_rbac_user.py`/`migrate_rbac_ddl.py`/`audit_domain_hygiene.py` 全數**未見於 repo、為本計畫新提**。
