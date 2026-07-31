# 呈案 D13：DB 角色架構與他專案清理（2026-07-31）

> **性質**：[I] **呈案**——依 `AUGUR-MC v1.6 §8.1`「Agent 不得參與修憲與解釋」與 `RULING-2026-028`（繕打非參與），
> 本檔為**繕打者草擬之事實與選項並列**，**不含建議採用何案、不代為認定位階**。決定權專屬 Steward。
> **觸發**：Steward 2026-07-31 下午提問「此專案的 database user 是否應把所有 user 為 stock 修改為 augur」
> → 續問「我可以把 augur 先改為 super user 嗎」→ 續告「未來只會存在 augur 專案與 augur user 與 database」。
> **關聯**：行程計畫 `reports/augur_execution_roadmap_20260731.md`（本案為新增拍板點 **D13**，
> 與其 **D7**〔guard 統一模式〕、**W2-1**〔UPDATE 通行證〕同屬「誰能繞過誠實閘」主題）。
> **全部事實為 2026-07-31 13:2x–13:4x 本機唯讀親驗**；引用前重跑附註指令。

---

## §0 繕打者之更正（先行揭露）

對話中繕打者曾稱「現在 `augur` 非 superuser，（跨庫）這條路是斷的」——**此語不精確，於此更正**：

- `pg_database.datacl` 四庫皆為**空**＝ `CONNECT` 依 PostgreSQL 預設授予 `PUBLIC`
  ⇒ **`augur` 可以連進 `ttai`／`stock`／`rdai` 庫**（實測 `psql -d ttai -c "SELECT 1"` 回 `1`）。
- 但**讀不到任何資料**：`ttai` 之 16 張表全在 `buffer` schema，`augur` 對其可 SELECT 者＝**0**。

**正確表述**：牆不在「連線」，在「表級授權」。此更正不改變本案之選項結構，但改變其中一項代價之描述
（見 §3 D13-1 乙案之「跨庫暴露」欄）。

---

## §1 現況事實（唯讀親驗）

### 1.1 角色與資料庫

| 角色 | superuser | createdb | createrole | login | 擁有之庫 |
|---|---|---|---|---|---|
| `postgres` | **是** | 是 | 是 | 是 | `postgres` |
| `stock` | **是** | 是 | 否 | 是 | `stock`（10 MB） |
| `augur` | 否 | 否 | 否 | 是 | `augur`（**60 GB**） |
| `augur_predict` | 否 | 否 | 否 | 是 | — |
| `rdai` | 否 | 否 | 否 | 是 | `rdai`（7.6 MB） |
| `ttai` | 否 | 否 | 否 | 是 | `ttai`（214 MB） |

`pg_auth_members` **零列**（無角色繼承）。取得指令：
`SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolcanlogin FROM pg_roles WHERE rolname NOT LIKE 'pg\_%'`

### 1.2 `stock` 在 augur 庫之落點＝零

| 項 | 值 |
|---|---|
| 擁有之 table／view／sequence／function／schema | **0／0／0／0／0** |
| `information_schema.role_table_grants` 之 grantee | 僅 `augur`(2,163)／`augur_predict`(192)，**無 stock** |
| repo 內以 stock 為 DB 角色之引用 | **0**（`.env` `DB_USER=augur`） |
| 目前連線 | `augur`×10、`postgres`×1，**無 stock** |

⇒ **「把 stock 改為 augur」在 augur 側無標的**。`stock` 是他專案角色（伺服器採一專案一 role＋一 db）。

### 1.3 augur 庫內部之權限現況

- `public` 之 306 張表**全部 owner＝`augur`**（單一擁有者）。
- **`augur` 缺 DELETE 之表數＝0** ⇒ **無任何 ACL 型 append-only 保護**。
- `augur_owner`／`augur_app` 角色**不存在**（`SELECT count(*) … rolname='augur_owner'` → 0）。
- 誠實閘（`honesty_delete_only_guard` 等）所掛之表，其 owner 亦為 `augur`。
- 無 `postgres_fdw`／`dblink` extension（跨庫連結＝0）。
- 無 RLS（`relrowsecurity` 為真者＝0）。

**推論（PostgreSQL 語義，非本機實測——實測即為破壞性）**：表之 owner 得
`ALTER TABLE … DISABLE TRIGGER`。故現況下**所有服務所用之角色 `augur` 得卸除任一誠實閘**。
此即記憶 `kh-verify-fail-three` 所列「V-5 DISABLE TRIGGER 可卸閘」六則未修之一。

### 1.4 與 HANDOFF §0.5 之不一致

HANDOFF §0.5（2026-07-18）逐字載：「**owner 分離生產生效**——十張憲章表＋2 抹除函式隸
`augur_owner`（NOLOGIN），應用角色 `augur_app` 僅 SELECT/INSERT」。**本機實況**：兩角色皆不存在、
零 ACL append-only、全表 owner＝`augur`、服務連線角色＝`augur`。

該節另提及 `/home/giga/augur/backups/`（`giga` 帳號路徑）⇒ 該宣稱**可能為另一載體之狀態**。
惟 HANDOFF 為**跨機接續文件**且其自身別處載明「DB 不隨 git」，該節**未標注為機器局部**
⇒ 於本機閱讀者會相信存在一層實際不存在之保護。**「是否為不實宣稱、應如何處置」屬 Steward 認定。**

### 1.5 `augur_predict` 之性質（關乎「只剩 augur user」之射程）

- 非他專案角色，**係 augur 自身元件**：repo **25 支**程式引用；`src/augur/core/db.py` 內建連線通道；
  `scripts/setup_predict_role.py` 為換機必跑步驟。
- 作用：可 SELECT 之表由 `augur` 之 **309** 收窄至 **162**。
- r2 核驗記載其為「全系統唯一一處經三路獨立檢查、無任何假綠」之機制，
  且為靈魂層「素養層零量化價值、不進預測管線」之 DB 層保證。

### 1.6 跨專案依賴（決定「刪什麼」之邊界）

**DB 層：零耦合。** 無 FDW／dblink；`augur` 對他庫可連線但可讀表數＝0。
⇒ **刪除 `ttai`／`stock`／`rdai` 三個資料庫與角色，對 augur 之 DB 層無影響。**

**檔案系統層：有耦合，且不在 DB。**

| 依賴 | 證據 | 影響 |
|---|---|---|
| Qdrant 二進位在 ttai **專案目錄** | `augur-qdrant.service:12` `ExecStart=/home/hugo/project/ttai/.qdrant_server/qdrant`（85 MB）；`install_services.sh:26` `QDRANT_BIN` 同 | 刪 `~/project/ttai/` ⇒ `augur-qdrant.service` 起不來（＝r2 債 #40） |
| ERP 語料之重抓能力 | `.env` 有 `ORACLE_HOST/PORT/SERVICE_NAME/USER/PASSWORD`；repo 內 **無** Oracle 連接器（`cx_Oracle`／`oracledb` 零命中）；HANDOFF 載抽取屬「外部 TTAI 工具」 | 刪 ttai 專案 ⇒ `owned_local` **150,772 列** item_text 之唯一載具僅剩 DB dump |
| `~/project/` 目錄現況 | 只有 `augur`／`ttai` 兩個目錄（**無** `rdai`／`stock` 專案目錄） | rdai／stock 僅剩 DB，無專案側牽連 |

**⇒ 本案之關鍵區分：刪「資料庫」與刪「專案目錄」是兩件事。前者對 augur 無影響；後者會斷 qdrant 與 ERP 重抓。**

---

## §2 治權面之落點（逐字引，不代解釋）

- `AUGUR-MC v1.6 §P5.W5`：不得降低人類監督與否決能力——屬 **§8.4 不可豁免核心**（連履行時程亦不得豁免）。
- `AUGUR-L6 v1.2 L6.18(a)`：AI **不得為涉及自身監督機制之變更之核准主體**。
- CLAUDE.md `#26`（OCV 單向棘輪）：凡弱化「人類介入點數／否決可達性／揭露比例／最大自動鏈長」
  任一項者，**即屬治權變更、停下問**。
- CLAUDE.md `#6`：破壞性操作（刪庫／刪角色）**必先確認**；授權某次 ≠ 授權所有同類。

**須 Steward 認定之點（繕打者不代判）**：
1. 「將 `augur` 升為 superuser」**是否**構成上述「弱化監督機制」？（AI 於本專案即以 `augur` 身分操作 DB。）
2. 「未來只存在 augur user」**是否包含** `augur_predict`？（見 §1.5——其存廢影響靈魂層保證。）
3. HANDOFF §0.5 之不一致應如何處置（更正為機器局部／補做 owner 分離／其他）？
4. 上列各項之修訂位階（patch／major）——依 `GOVERNANCE-ANNEX` 為 Steward 保留事項。

---

## §3 選項並列（不排序、不含偏好）

### D13-1｜`augur` 之權限層級

| 案 | 內容 | 代價 | 不可逆性 | 依據／備註 |
|---|---|---|---|---|
| **甲** | 維持非 superuser（現狀） | 維運需切 `DB_SUPERUSER_*` 通道（已實測可用，回 `postgres\|t`） | 無（現狀） | 與 §1.4 owner 分離方向相容 |
| **乙** | 升為 superuser | ①**跨庫暴露**：可讀寫 `ttai`(16 表)／`stock`／`rdai` 全部——惟若採 D13-2 甲全刪，此項代價**歸零**；②`COPY … FROM PROGRAM` ＝以 postgres OS 身分執行命令，而 `augur` 正是三個對外開埠服務（8090／8500／8399）之連線角色；③**使 D13-3 甲失去意義**（superuser 可瞬間撤銷任何 owner 分離） | 角色屬性可再 `NOSUPERUSER` 復原；**但期間所生之事實不可逆** | 須先答 §2 認定點 1 |
| **丙** | 只給特定能力（如 `CREATEROLE`）不給 superuser | 僅解「建角色」一項需求；其餘維運仍走 `postgres` | 低 | 若目的僅為執行 D13-3 甲 |

**事實補充（供權衡）**：`postgres` 為 PostgreSQL 內建 superuser、不隨他專案消失。故縱使終局只剩 augur 一個專案，
**superuser 通道仍然存在**（`DB_SUPERUSER_*` 已在 `.env`）。乙案所增者為「應用角色同時具 superuser」，
非「取得原本沒有的能力」。

### D13-2｜`stock`／`rdai`／`ttai` 之清理

| 案 | 內容 | 代價 | 不可逆性 | 備註 |
|---|---|---|---|---|
| **甲** | 三庫＋三角色全刪 | 三專案資料永久消失（stock 10 MB／rdai 7.6 MB／ttai 214 MB） | **高·不可逆**（除非先 dump） | 一併解除「`stock` 是 superuser」（角色不存在即無此洞），較 `NOSUPERUSER` 徹底 |
| **乙** | 只刪庫、保留角色 | 同上減資料 | 高 | 角色留著仍佔 superuser（stock） |
| **丙** | 分階段：先 `stock`（已休眠：其 4 條 cron 經 hugo 2026-07-13 裁定全部取消）→ 觀察 → 再 rdai／ttai | 時程較長 | 可分段回退 | 每段前 dump 即可回復 |
| **丁** | 不刪，僅 `ALTER ROLE stock NOSUPERUSER` | 保留全部資料 | 低·可逆 | 只收緊權限、不清理 |

**三案共同之硬邊界（無論選何案）**：
- **`~/project/ttai/` 目錄不得隨之刪除**——否則 `augur-qdrant.service` 起不來（r2 債 #40）、
  且 ERP 語料重抓能力歸零。若欲解此耦合，須先將 qdrant 二進位遷入 augur 自有路徑並改
  `install_services.sh:26` 與該 unit；此為獨立工項。
- 刪任何庫前，`pg_dump` 留檔屬 `#6`／`#30` 之常規要求。

### D13-3｜owner 分離（`augur_owner`／`augur_app`）

| 案 | 內容 | 代價 | 不可逆性 | 備註 |
|---|---|---|---|---|
| **甲** | 本機補做（比照 HANDOFF §0.5 所載之另一載體） | 需建角色（須 `postgres` 或 D13-1 丙）＋改 306 表 owner ＋改服務連線角色 ＋全服務重啟實測（#7） | 中·可回退（owner 可改回） | 修 V-5「DISABLE TRIGGER 可卸閘」；與 W2-1 同主題宜同批設計 |
| **乙** | 明文放棄該設計，並將 HANDOFF §0.5 更正為機器局部 | 誠實閘之可卸性成為**已知並接受**之限制 | 低（純文件） | 須同時更新 r2 債 #4／#24 之描述 |
| **丙** | 維持現狀、不決定 | 文件宣稱與實況持續背離；新讀者持續誤信 | — | 腐爛型，時間不站在這邊 |

---

## §4 選項間之相依（繕打者僅列關係，不排序）

- **D13-1 乙 ⊗ D13-3 甲**：互斥於實質——superuser 之應用角色可撤銷任何 owner 分離。
- **D13-2 甲 → D13-1 乙之代價①歸零**：他庫若已刪，「跨庫暴露」不復存在。
  （惟代價②`COPY FROM PROGRAM` 與代價③不受影響。）
- **D13-2 甲／丁 → 解除「stock superuser」**：甲為徹底、丁為收緊。
- **D13-3 甲 ← D13-1 丙**：若僅為建角色而需權限，丙案足夠、不必乙案。
- **D13-3 與行程計畫 W2-1／D7 同主題**：宜合併考量，避免兩次動同一批表之 trigger／ACL。

---

## §6 Steward 決定記錄（2026-07-31 下午・對話拍板）

> 本節為**決定之留痕**，非繕打者之建議。決定內容依 Steward 逐次答覆記錄如下。

### 6.1 決定內容

| 項 | 決定 | 對應選項 |
|---|---|---|
| 終局角色數 | **只有 `augur` 一個** | — |
| `augur_predict` | **包含在內、一併移除** | （§1.5 所述之機制取消） |
| `augur` 權限 | **升為 superuser**（讀法二：連維運也用 augur） | **D13-1 乙** |
| `stock`／`rdai`／`ttai` | 清理（庫與角色） | **D13-2**（甲／丙之別待定，見 6.5） |
| owner 分離 | 隨 D13-1 乙**失去意義**（superuser 可撤銷任何分離） | **D13-3 乙**（放棄設計、更正文件） |

### 6.2 OCV 四項對照（CLAUDE `#26` 強制要求；前→後）

| 分量 | 變更前 | 變更後 | 判定 |
|---|---|---|---|
| 人類介入點數 | 4 支 CLI 之 TTY 閘 ＋ **app／維運雙憑證分離**（`DB_USER` vs `DB_SUPERUSER_*`） | TTY 閘 4 支不變；**憑證分離消失** | **減少 1** |
| 否決可達性 | hugo 可 `ALTER ROLE`／停服務／改 `.env` | 同左（不受影響） | 不變 |
| 揭露比例 | `tests/test_predict_role_isolation.py` **5 passed**（`has_table_privilege` 逐表實證） | role 不存在 → 該檔 :43 走 `pytest.skip` ⇒ **5 skipped**、RC=0、**綠燈但零實證** | **下降** |
| 最大自動鏈長 | 一波（本計畫 §0） | 同左 | 不變 |

⇒ 依 `#26`「任一弱化即屬治權變更、停下問」，本案**確屬治權變更**；已由 Steward 拍板，本節即其留痕。
**繕打者未參與該認定**（`AUGUR-MC v1.6 §8.1`）。

### 6.3 隨之消失的保證（誠實列示）

1. **`#8` 隔離之 DB 層將不存在，且原理上無法重建**——單一角色擁有全部 306 表，`REVOKE` 對 owner 無效
   （owner 得隨時自我 `GRANT`）。此後 `#8` 完全依賴 **code 層 AST import 稽核**
   （`src/augur/audit/import_isolation.py`，射程 7 個 package；`execution`／`arena`／`identity`／`deliberation`
   不在掃描範圍——r2 §4 B10 記載其「現況恰好乾淨」而非「由構造保證」）。
2. **紅燈不會亮、只會變成 skip**：`test_predict_role_isolation.py` 之設計為 role 未建即 skip
   （其 docstring 逐字：「誠實標『DB 閘未 apply』、非假 pass」）。設計誠實，**但在綠色摘要中不可見**。
3. **`WM.35` 消費閘之證據失效**：`GROUNDING-MAP.md:176` 逐字載「十新表對 `augur_predict` SELECT 全拒
   （`has_table_privilege` 逐表查證——**WM.35 消費閘已達**）」。角色移除後該證據不復存在，
   而 **WM.35／36 屬 2026-10-14 到期義務**（`RULING-2026-030` 第五(b)：自 10-15 起消費禁令無條件適用）。
   **⇒ 須 Steward 另行認定：WM.35「已達」之宣稱在新架構下以何為證。**
4. **`COPY … FROM PROGRAM`**：`augur` 為三個對外開埠服務（8090／8500／8399）之連線角色，
   升 superuser 後該路徑可執行 OS 命令（以 postgres OS 身分）。

### 6.4 治權檔影響（好消息：核心四檔未指名）

- **靈魂／原則精華／大憲章／CLAUDE：零命中 `augur_predict`** ⇒ 移除角色**不直接使治權條文失真**。
- `docs/模擬方法自進化專章_v1.0.md:99` 之提及係 **2026-07-31 之 `pg_roles` 實查快照**（附一「實查事實一」）
  ⇒ 屬**史述**，依大憲章 v1.51.0 通則一（史述凍結）**不得改**。
- `GROUNDING-MAP.md:176` 屬現況宣稱 ⇒ 須更正（見 6.3 第 3 點）。**屬 D8 類，繕打者只草擬。**

### 6.5 遷移清單（29 檔；執行前逐項確認）

**A. 程式（src，2 檔）**
- `src/augur/core/db.py`：移除 `connect_predict()`／`ping_predict()`（:43／:73）及其 docstring 描述（:4／:7／:10／:16）；`_selftest` :91 之 `chk("connect_predict 可呼叫")` 一併移除。
- `src/augur/core/config.py:56`：移除 `DB_PARAMS_PREDICT`。

**B. 唯一 runtime 呼叫端（1 檔）**
- `scripts/predict_asof.py:154`：`db.connect_predict()` → `db.connect()`；同行註解「G-ISO-2：預測寫入走 augur_predict」須改為誠實描述新架構。

**C. `migrate_*.py` 中之 GRANT 語句（9 檔）**
`migrate_prediction_ddl` / `migrate_probability_ddl` / `migrate_raw_supersede_ddl` / `migrate_revalidation_baseline_ddl` / `migrate_revalidation_ledger_ddl` / `migrate_risk_policy_ddl` / `migrate_trial_ledger_ddl` / `migrate_unfreeze_gate_ddl` / `migrate_validation_evidence_ddl`
——各含對 `augur_predict` 之 GRANT；移除後須確認其 `--selftest`（多為字串比對，見 r2 債 #25）不因此假綠。

**D. `verify_*` 與其他 scripts（11 檔）**
`bridge_deliberation_distill` / `preregister_unfreeze_gate` / `revalidate` / `revalidate_baseline` / `run_model_robustness` / `survivorship_economic_verdict` / `verify_evolution_acceptance` / `verify_prodset_hotpath` / `verify_roadmap_r6_s12` / `verify_roadmap_r7_gate` / `verify_validation_evidence`

**E. 建置與測試（2 檔）**
- `scripts/setup_predict_role.py`：整支退役（或改為「本架構已不使用」之 graceful 說明，保留矩陣以合 #29(d)）。
- `tests/test_predict_role_isolation.py`：**不得只留著讓它 skip**——否則綠燈永遠掩蓋 6.3 第 2 點。處置選項：(i) 刪除並於 `tests/` 留一則說明；(ii) 改寫為驗證「AST 稽核為唯一防線」之測試。**屬 Steward 選擇。**

**F. 文件（4 檔＋1）**
`GROUNDING-MAP.md`（含 :176 之 WM.35 證據句）／`HANDOFF.md`（§3 `.env` 表之 `DB_PREDICT_PASSWORD` 列、§0.5 owner 分離段）／`docs/remediation/AUD-02-raw-supersede-log.md`／`docs/remediation/HANDOFF-2026-07-17.md`；
`import_database.sh`（`setup_predict_role` 之呼叫）。

**G. `.env`**：`DB_PREDICT_PASSWORD` 移除（**人工**，不在 git）。

### 6.6 執行順序與閘（繕打者建議之順序，非決定）

| 步 | 動作 | 性質 | 閘 |
|---|---|---|---|
| 0 | `pg_dump` 留檔：`stock`／`rdai`／`ttai` 三庫 ＋ augur 全庫 | 唯讀 | — |
| 1 | 程式側改動（A–F），逐檔改、跑各自 `--selftest`、跑 pytest | 可逆 | 一支一支檢視（#19） |
| 2 | 重啟受影響常駐服務並實測（#7） | 可逆 | 五埠實測 |
| 3 | `ALTER ROLE augur SUPERUSER` | **治權變更** | Steward 親跑（6.2 已留痕） |
| 4 | `DROP ROLE augur_predict` | **不可逆** | 須 1–2 完成且驗收綠 |
| 5 | `DROP DATABASE stock/rdai/ttai` ＋ `DROP ROLE` | **不可逆** | 須步 0 之 dump 存在且驗過 |
| — | **`~/project/ttai/` 目錄不刪** | 硬邊界 | 見 §1.6（qdrant 二進位＋ERP 重抓） |

**繕打者將於獲授權後執行步 1–2，並於步 3–5 僅備妥指令、由 Steward 親跑**
（步 3 涉自身監督機制之變更，`L6.18(a)`；步 4–5 為 §0.1 第 2 類破壞性）。

---

## §5 繕打者未做之事（誠實界定）

- **未執行任何變更**：未 `ALTER ROLE`、未 `DROP DATABASE`、未建角色、未改 owner、未投遞 `governance_queue`。
- **未實測 owner 卸 trigger**（§1.3 之推論係 PostgreSQL 語義，實測即為破壞性寫入）。
- **未認定** §2 四個認定點之任一項，**未建議採用任何案**。
- **未查**：`ttai`／`rdai` 兩專案是否尚有他人／他機在用（本機無其專案目錄，但不排除他處）；
  `stock` 庫內容之保存價值；ERP 重抓工具之實際所在與可用性。
- 本呈案未經獨立核驗（`RULING-2026-028` 第 3 點）。
