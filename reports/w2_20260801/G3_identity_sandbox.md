# [DRAFT 呈案] G3｜identity 六表：沙盒演練→建表＋最小接線（P5 一次拍板）

> **[DRAFT 呈案] 未經拍板不得施作。**
> **自我利益揭露（`AUGUR-L6 v1.2` L6.18(c)）**：本呈案由 AI（W2 呈案批 agent）起草；identity 六表之 append-only 閘所約束的寫入者包含 AI 自身，本案親驗數字全附指令可獨立重放、建議附證偽條件；裁決專屬 Constitution Steward（§8.1／L6.18(a)），本文僅呈案不代決。
> 起草日：2026-08-01（六）｜設計 SSOT：登錄冊 §3-G3＋裁決單 §七 G3｜制度前例：`constitution/RULING-2026-015-PHASE2-MERGE.md`（P5 一次拍板制）＋`ops/phase2/P5-SUBMISSION-2026-07-18.md`。

---

## §1 問題與授權鏈

**問題一句話**：Layer 3 identity 六表在本機生產庫**從未建立**（碼在、DDL 在、表不在）——元憲章 §1.3「沒有 Identity 不允許 Knowledge」在本機**反向成立**（`knowledge_item` 現 285,204 列、零 identity 表）。

**歷史鏈（為何「曾做完」而「現在沒有」）**：
1. RULING-2026-014：型別判準採認（T.1 Security／T.2 Index／FredSeries／Automobile 守衛）。
2. RULING-2026-015（2026-07-18）：Phase 2 分支准併＋裁①（advisory lock 並發防護）＋裁③（生產順序＝retire 先行）＋**主文 4「P5 一次拍板制」**（生產施作以單一 P5 核准涵蓋全順序）。
3. `ops/phase2/P5-SUBMISSION-2026-07-18.md`：Steward 簽核（數字錨＝2026-07-16 態）。
4. `ops/phase2/ENTITY-BACKFILL-20260722.md`：**於 GB10（主機 `aitopatom-b96e`、userspace PG）實跑落地**——registry 3,491／alias 3,491／retire 342／attr 9,258／人裁佇列 37。
5. hugo 2026-07-25 宣告：**沒有 GB10**（記憶「GB10 不可用」）——該批 augur_id 隨機器消滅；07-31 單一角色整併後之本機庫（及其 postmerge dump）**均不含六表**（§2.2 親驗）。

**授權鏈（L6.5-L6.8 四要件留痕）**：(a) 範圍＝W2 呈案批之唯讀親驗＋文件產出，零施作；(b) 結束條件＝本文件交付；(c) 可撤銷；(d) 參照＝登錄冊 §1 `G3`（W2、☐）＋裁決單 §七 G3。
**關鍵主張（誠實）**：舊 P5 簽核繫於「GB10 環境＋2026-07-16 數字錨」，環境已消滅、名冊已漂移（§2.4）——**不得沿用舊簽核施作本機**；本呈案即依 RULING-2026-015 主文 4 之制度，呈**新的一次 P5 拍板**（沙盒演練→生產 apply＋最小接線一次涵蓋）。

---

## §2 現況親驗（2026-08-01 執行時現查）

### 2.1 生產庫：六表零存在；單一角色

```
$ SELECT … FROM information_schema.tables WHERE table_name IN (六表)  → identity_tables=(none)
$ SELECT to_regclass('entity_registry')                                → (null)
$ SELECT current_user, rolsuper                                        → augur / rolsuper=true
$ SELECT EXISTS(… pg_database WHERE datname='augur_sandbox')           → false（沙盒亦不存在）
$ 資料庫清單：postgres, augur（僅此二庫）
```

### 2.2 兩份 dump 亦零六表（「表不在」非本機漏 sync，而是從未建）

```
$ pg_restore -l ~/db_dumps/augur_20260801_weekly_Fd  | grep -icE "entity_registry|identity_claim|identity_lifecycle" → 0
$ pg_restore -l ~/db_dumps/augur_20260731_postmerge_Fd | 同上 → 0
```

### 2.3 Code 資產完整且全綠（10/10 selftest 親跑）

| 資產 | 檔 | selftest |
|---|---|---|
| DDL 單一權威（42 個 DDL 項：6 表＋6 index＋6 comment＋6 REVOKE＋5 function＋11 trigger＋identity_criteria 欄＋seed） | `scripts/migrate_identity_ddl.py` | ✓ 全通過（DDL 結構不變式；DB 語義需 PG＝沙盒演練標的） |
| 型別種子（4 列：Security／Index／FredSeries／Automobile 守衛） | `scripts/seed_entity_type_catalog.py` | ✓ |
| retire backfill（裁③ 先行；單實例 advisory lock；`--rehearse-clean` 一律 ROLLBACK） | `scripts/backfill_lifecycle_retire.py` | ✓ |
| 存量鑄造（三名冊；冪等分批；紅旗 provisional 不縫合） | `scripts/backfill_entity_registry.py` | ✓ |
| 屬性 SCD-2 同步 | `scripts/sync_attribute_versions.py` | ✓ |
| library 五模組 `augur.identity.{identifier,claim,lifecycle,attribute_version,resolve}` | `src/augur/identity/` | ✓×5 |

`mint` 簽名（親讀 `src/augur/identity/identifier.py:47`）：`mint(cur, entity_type, evidence_ref, actor, augur_id=None) -> str`——catalog 校驗（未登錄型別拒）＋`binding_kind_default='instance'` 校驗（分類節點拒鑄）＋actor 必填（P4.E6）＋命名空間隔離校驗（`augur:{namespace_key}/…`）後 INSERT `entity_registry`。單一入口＝`resolve.resolve_or_mint(cur, code_system, external_code, entity_type, evidence_ref, actor, valid_from=None, code_lock=True)`（`resolve.py:96`；per-code advisory lock 裁①）。

### 2.4 名冊活錨 vs 舊 P5 錨（漂移明標；#9 不轉抄）

| 項 | 舊 P5 錨（07-16 態） | **本日親驗（08-01）** | 漂移 |
|---|---|---|---|
| Security 名冊 | 3,086 | **3,096** | +10 |
| Index 名冊 | 32 | **32** | 0 |
| FredSeries 名冊 | 31 | **31** | 0 |
| 名冊殘差（非數字∧非 Index/大盤） | 0 | **0** | 0 |
| 下市紀錄（=預鑄 retired 身估） | 342 | **344**（distinct (stock_id,date) 亦 344，零塌列） | +2 |
| 名實不符人裁佇列 | 37 | **37**（MISMATCH_SQL 親跑） | 0 |
| 終態 registry 估 | 3,491 | **≈3,503**（344＋3,159；估算，以沙盒實跑為準） | — |

⚠ 腳本 docstring 內之 342／3,149／235 為舊錨敘述（僅註解、無 hardcode 斷言，code 全讀活名冊）；本呈案一律以沙盒實跑數為新錨。

### 2.5 零消費者盤點（誠實條款之事實基礎）

```
$ grep -rl "entity_registry|entity_alias|identity_lifecycle_event|entity_attribute_version" src/ scripts/
  → src/augur/identity/（5 模組）＋src/augur/audit/import_isolation.py（稽核唯讀）
    ＋上表 4 支 backfill/migrate 腳本。攝取路徑（ingestion/ingest.py、sync.py）零引用；
    mint/resolve_or_mint 之 runtime 呼叫端＝0。
```

`identifier.py:15-19` 自陳（現行、將續留）：「**ID.11 義務結案狀態：機制就位、義務未結**——攝取路徑現仍以外部碼直充身份……不得計為 ID.11 已落實」。

### 2.6 單一角色下 append-only 縱深之誠實（與 F1／L7.16 登錄一致）

`migrate_identity_ddl.py:29-30` 原設計自陳：「表 owner ≠ 應用角色，方為完整機器保證」。**本機現況＝單一 augur superuser 角色**（07-31 整併；記憶「#8 隔離之 DB 層已不存在」）——六表建立後，append-only 之 `REVOKE … FROM PUBLIC` 縱深**對唯一角色無效力**，實際強度＝trigger＋紀律（superuser 可 `DISABLE TRIGGER`，同 V-5 已知殘道；F1／RULING-2026-042 之 L7.16 適用性註記為其治權承接）。本呈案不粉飾：**建表後之不可刪保證屬「半硬」層級**，與 `honesty_ledger_guard` 諸表同級。

---

## §3 方案：沙盒演練 → 生產 apply ＋ 最小接線（一次 P5 涵蓋）

### 3.1 DDL（#12 單一住所引用＋lock_timeout 補強 diff）

**DDL 全文＝`scripts/migrate_identity_ddl.py:42-352`（單一權威，42 項；本呈案不複述全文以免雙住所漂移）**。物件摘要：六表（`entity_type_catalog`／`entity_registry`／`entity_alias`／`identity_claim`／`identity_lifecycle_event`／`entity_attribute_version`，FK 依賴序 catalog→registry→其餘四表）＋6 index＋11 trigger（append-only×3、no_delete×2、no_truncate×5、catalog_immutable×1）＋5 function（含 `identity_de_identify` SECURITY DEFINER、search_path 釘死、REVOKE EXECUTE）＋REVOKE 縱深＋ONT.20 `identity_criteria` 欄與四列判準 seed。全部 `IF NOT EXISTS`／`CREATE OR REPLACE`，冪等新表型、零既有表觸動。

**涉 code diff（施作前唯一必要改動；帶 SET lock_timeout，呈案紀律）**——`scripts/migrate_identity_ddl.py:470-473` `main()`：

```python
# 現行
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
# 改為
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            cur.execute("SET lock_timeout = '5s'")  # 絕不排隊(#30 鎖風暴;與 B4 DDL 同紀律)
            for label, ddl in DDL:
```

（新表型 DDL 本不與既有表爭鎖，`lock_timeout` 為縱深：任何意外鎖等 5s 即 fail-loud 整交易回滾，不留佇列。）另依 #30：生產 apply 前先 `flock -n /tmp/augur_pgdump.lock true || 停`（dump 進行中禁 DDL）。

### 3.2 沙盒演練（Phase S；全程可逆；逐條指令）

沙盒＝`augur_sandbox` 新庫（現不存在，§2.1）；演練資料＝今日 weekly dump 之三張來源表（`TaiwanStockInfo` 960 kB／`TaiwanStockDelisting` 72 kB／`fred_series` 57 MB——分鐘級還原）。`DB_NAME=augur_sandbox` 環境變數優先於 `.env`（親驗 `config.py:44` `os.getenv` ＋ `load_dotenv` 不覆蓋既有 env）。

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
# S1 建沙盒（可逆：S11 dropdb）
PGPASSWORD="$DB_PASSWORD" createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -T template0 augur_sandbox
# S2 還原三來源表（僅此三表；--no-owner 單一角色下中性）
PGPASSWORD="$DB_PASSWORD" pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d augur_sandbox \
  --no-owner -t TaiwanStockInfo -t TaiwanStockDelisting -t fred_series ~/db_dumps/augur_20260801_weekly_Fd
# S3 DDL＋驗證清單（VERIFY 12 項）
DB_NAME=augur_sandbox venv/bin/python scripts/migrate_identity_ddl.py
DB_NAME=augur_sandbox venv/bin/python scripts/migrate_identity_ddl.py --check
# S4 型別種子（catalog 4 列）
DB_NAME=augur_sandbox venv/bin/python scripts/seed_entity_type_catalog.py
# S5 trigger 行為探針（selftest 自陳「DB 語義需 PG」之補課；每句預期 RC≠0＝閘活）
PSQLS=(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d augur_sandbox -tAc)
PGPASSWORD="$DB_PASSWORD" "${PSQLS[@]}" "INSERT INTO entity_registry (augur_id,entity_type,minted_by) VALUES ('augur:security/probe_a','Security','sandbox-probe'),('augur:security/probe_b','Security','sandbox-probe')"
PGPASSWORD="$DB_PASSWORD" "${PSQLS[@]}" "INSERT INTO identity_claim (augur_id_a,augur_id_b,criterion_ref,evidence_ref,asserted_by) VALUES ('augur:security/probe_a','augur:security/probe_b','probe','probe','sandbox-probe')"
PGPASSWORD="$DB_PASSWORD" "${PSQLS[@]}" "UPDATE identity_claim SET note='x'"                       # 預期 RAISE:append-only
PGPASSWORD="$DB_PASSWORD" "${PSQLS[@]}" "DELETE FROM entity_registry WHERE minted_by='sandbox-probe'"  # 預期 RAISE:永久參照
PGPASSWORD="$DB_PASSWORD" "${PSQLS[@]}" "TRUNCATE entity_alias"                                    # 預期 RAISE:TRUNCATE 禁止
PGPASSWORD="$DB_PASSWORD" "${PSQLS[@]}" "UPDATE entity_type_catalog SET namespace_key='x' WHERE entity_type='Security'"  # 預期 RAISE:ID.12 回溯不變式(已有 registry 參照)
PGPASSWORD="$DB_PASSWORD" "${PSQLS[@]}" "SELECT identity_de_identify('augur:security/nope','probe')"    # 預期 RAISE:不存在不靜默成功
# S6 retire 先行（裁③；前置閘=registry 僅探針 2 列、零 retire 事件）
DB_NAME=augur_sandbox venv/bin/python scripts/backfill_lifecycle_retire.py --check    # 比對:下市 344/預鑄 344/名實不符 37
DB_NAME=augur_sandbox venv/bin/python scripts/backfill_lifecycle_retire.py --apply --mismatch-csv /tmp/identity_mismatch_sandbox.csv
# S7 存量鑄造（前置閘=retire 事件 344）
DB_NAME=augur_sandbox venv/bin/python scripts/backfill_entity_registry.py --check     # 比對:3,096/32/31、殘差 0
DB_NAME=augur_sandbox venv/bin/python scripts/backfill_entity_registry.py --apply
# S8 屬性同步＋冪等證
DB_NAME=augur_sandbox venv/bin/python scripts/sync_attribute_versions.py --check
DB_NAME=augur_sandbox venv/bin/python scripts/sync_attribute_versions.py --apply
DB_NAME=augur_sandbox venv/bin/python scripts/sync_attribute_versions.py --check      # 驗:append=0
DB_NAME=augur_sandbox venv/bin/python scripts/backfill_entity_registry.py --check     # 驗:未繫=0;重跑 minted=0
# S9（加值驗）乾淨順序重演：rehearsal 命名空間、單一交易一律 ROLLBACK 零殘留
DB_NAME=augur_sandbox venv/bin/python scripts/backfill_lifecycle_retire.py --rehearse-clean
# S10 沙盒終態數字錨落 stdout → 抄入本呈案 §6 表、回呈 Steward 圈選
# S11（P5 拍板、生產完成後）dropdb augur_sandbox —— 全程可逆閉環
```

**探針備註**：S5 之 probe 列（2 registry＋1 claim）因 no_delete／append-only 設計**留在沙盒中**（此即閘在工作之證明），沙盒整庫 S11 銷毀，零殘留於生產；S6 前置閘寫明「registry 僅探針 2 列」，S7 驗收數一併 +2 計入（或 S5 改於 S8 之後跑——執行者擇一並留痕，兩者皆機械可判）。

### 3.3 生產 runbook（Phase P；唯 P5 拍板後；順序＝裁③）

```bash
# P0 前置：flock 檢無 dump 進行中；備份錨=當週 weekly dump（已有 08-01 13:24 一份;若拍板日晚於下個 dump 以最新為錨）
flock -n /tmp/augur_pgdump.lock true || { echo "dump 進行中,DDL 等它完(#30)"; exit 1; }
# P1 DDL（含 3.1 之 lock_timeout diff 已入 repo）＋種子
venv/bin/python scripts/migrate_identity_ddl.py && venv/bin/python scripts/seed_entity_type_catalog.py
# P2-P4 ＝ S6-S8 之無 DB_NAME 版（生產 .env 即 augur 庫），每步先 --check 比對沙盒錨：
#   偏離=停、回報 Steward 重錨（承舊 P5 major② 漂移停止條件;例外:名冊自然增量型偏離
#   —— 生產 --check 數＝沙盒錨＋拍板日後名冊新增列，AI 呈差異表、Steward 輕量重錨後續行）
venv/bin/python scripts/backfill_lifecycle_retire.py --check   && venv/bin/python scripts/backfill_lifecycle_retire.py --apply --mismatch-csv reports/identity_retire_name_mismatch_$(date +%Y%m%d).csv
venv/bin/python scripts/backfill_entity_registry.py --check    && venv/bin/python scripts/backfill_entity_registry.py --apply
venv/bin/python scripts/sync_attribute_versions.py --check     && venv/bin/python scripts/sync_attribute_versions.py --apply
# P5 驗收（§6 表）＋ 名實不符 CSV（37 例）入 reports/ 為人裁佇列載體
```

### 3.4 最小接線（三個小選項，Steward 圈其一）

- **W-a【建議】唯讀哨兵、零 cron 變更**：接線＝每次殘差／drift 可被看見——`backfill_entity_registry.py --check` 與 `sync_attribute_versions.py --check` 為現成唯讀哨兵，**由 hugo 或有界授權之 AI 於每月首個工作日手跑一次**，未繫 >0 或殘差 >0 即呈報。零自動鏈延長、零 install_cron 觸動。
- W-b 掛入週一 verify_weekly cron 行（`crontab :15`）尾端加兩支 `--check`：紅燈自動化，但屬 `install_cron.sh` AUGUR_BLOCK 變更——須循 CR1 教訓整批 `--check`→hugo 一次 `--apply`，並附 L6.16 四項對照聲明（人類介入點數／否決可達性／揭露比例／最大自動鏈長——皆不弱化：新增者為唯讀哨兵）。
- W-c 增量寫入接線（每週 `sync_attribute_versions.py --apply`＋每月 `backfill_entity_registry.py --apply` 補鑄新上市）：閉環最完整，但把 append 寫權交給排程＝自動鏈延長之寫入型，建議**待 W-a/W-b 跑順一季後另呈**。
- **明確不在本案**：ingestion 准入點強制 resolve-or-mint（identifier.py 所稱 Phase 5）——動 `ingest.py` 屬攝取熱路徑變更，#3 最小邊界，另案設計。

### 3.5 零消費者誠實條款（本呈案之一部，拍板即生效）

1. 建表＋backfill 完成後，`mint`／`resolve_or_mint` 之 **runtime 消費端＝0** 之事實**照實記載**（`identifier.py:15-19` 現行自陳續留、不得因「表建好了」而刪改）；ID.11 之 runtime 義務維持「機制就位、義務未結」，**不得於任何合規聲明、週報或 10-14 checklist 中宣稱 ID.11 已落實**。
2. 本案交付之誠實表述上限＝「元憲章 §1.3 之**存量側**結清於本機（每一在冊世界個體有永久 augur_id＋lifecycle＋as-of 屬性）；**增量側與消費側未接線**」。
3. 60 天觀察窗（裁決單證偽條件之機械化）：建表日＋60 天時查 runtime 呼叫端（grep 清單同 §2.5）仍為 0 ⇒ 「碼在表在無人用」續命成立，屆時呈 Steward 裁廢或強制接線（Phase 5 提案），不得靜默展期。

---

## §4 選項與建議案

- **甲【建議，＝裁決單建議案】**：通過沙盒演練案（§3.2）→ 新 P5 一次拍板 → 生產 apply（§3.3）＋最小接線 W-a；零消費者誠實條款照 §3.5。
- 乙：僅沙盒演練、生產緩辦（等 Phase 5 攝取接線一起施作）——省一次拍板，但「反向成立」與 10-14 懸崖之 Identity 缺口繼續掛零。
- 丙：不建（維持現狀，於 10-14 checklist 誠實記載「§1.3 反向成立」）。
- 接線子選項：W-a／W-b／W-c（§3.4；甲案預設 W-a）。

**證偽條件（甲案）**：
1. 建表後 60 天 mint runtime 呼叫端仍為零（§3.5 第 3 款）⇒「碼在表在無人用」證實，裁廢或強制接線（裁決單原句）。
2. 沙盒演練中任一 S5 探針**未** RAISE（RC=0）⇒ append-only 設計在單一角色環境失效超出 §2.6 已知範圍，停案、先修 DDL 再呈。
3. 生產 --check 出現**非名冊增量型**偏離（如 mismatch≠37±新增可解釋量、殘差>0）⇒ 錨假設錯，停、重錨。

## §5 風險與回滾

- **DDL 風險低**：42 項全屬新物件（IF NOT EXISTS／CREATE OR REPLACE），不觸任何既有表；`SET lock_timeout='5s'`（§3.1 diff）保證絕不排隊，失敗即整交易回滾（psycopg2 單交易執行）。dump 互斥依 #30（P0 flock 檢查）。
- **沙盒全程可逆**：獨立庫、S11 `dropdb`；rehearse-clean 模式另有交易級 ROLLBACK 先例。
- **生產回退之誠實定義**（沿舊 P5 §三，append-only 體制無原地撤銷）：(a) **前向補償**＝`entity_registry.status→tombstoned`＋lifecycle `correct` 事件（EVIDENCE_REQUIRED）；或 (b) **整庫還原**至備份錨（影響全庫、非僅 identity 表）。簽核即知悉。
- **單一角色殘餘風險**（§2.6）：superuser 可 DISABLE TRIGGER——不粉飾；治權承接＝F1（RULING-2026-042 之 L7.16 註記）。
- **錯序防護**：裁③ 順序由前置閘硬鎖（鑄造先於 retire＝語義相反且 append-only 下不可重來之拓撲——舊 P5 major③ 原句）；每步前置閘不綠一律停。
- **並發防護**：retire --apply 單實例 advisory lock；resolve_or_mint 預設 per-code advisory xact lock（裁①）。

## §6 驗收判準（機械可判；「沙盒錨」欄由 S10 實跑數填入後回呈）

| # | 判準 | 指令 | 通過條件 |
|---|---|---|---|
| V1 | 六表＋11 trigger＋SECURITY DEFINER | `venv/bin/python scripts/migrate_identity_ddl.py --check`；另 `psql -tAc "SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal AND tgrelid='entity_type_catalog'::regclass"` | VERIFY 12 項全有值；VERIFY trigger 清單 10 列（五表：append_only×3＋no_delete×2＋no_truncate×5）；catalog trigger 另查＝1（`trg_type_catalog_immutable`，VERIFY 查詢不含 catalog 表）；`identity_de_identify(SECURITY DEFINER✓)`；PUBLIC 殘餘 mutate=(無) |
| V2 | 探針五紅 | §3.2 S5 五句 | 每句 RC≠0，錯誤訊息分別含「append-only」「永久參照」「TRUNCATE 一律禁止」「命名空間互斥」「不存在」 |
| V3 | retire | `psql -tAc "SELECT count(*) FROM identity_lifecycle_event WHERE event_type='retire'"` | ＝344（沙盒）；生產＝沙盒錨±重錨量 |
| V4 | registry 終態 | `psql -tAc "SELECT count(*) FROM entity_registry"` | ＝沙盒實跑錨（估 ≈3,503＋探針批註；#9 以實跑為準） |
| V5 | 人裁佇列 | mismatch CSV 列數 | ＝37（沙盒親驗）；CSV 入 reports/ |
| V6 | 冪等 | 重跑三支 `--check` | minted=0／append=0／未繫=0 |
| V7 | 誠實條款 | `grep -n "義務未結" src/augur/identity/identifier.py`；§2.5 grep 清單 | 自陳句仍在；runtime 呼叫端清單＝0（記載於完工報告） |
| V8 | 沙盒閉環 | `SELECT … pg_database WHERE datname='augur_sandbox'` | 生產完工後＝false（S11 已 drop） |

## §7 Steward 決定欄

- [x] 甲（沙盒→新 P5 一次拍板→生產＋W-a）　- [ ] 乙（僅沙盒）　- [ ] 丙（不建）
- 接線子選項：- [x] W-a　- [ ] W-b　- [ ] W-c　- [ ] 修改意見：＿＿＿
- 簽：hugo　日期：2026-08-01
