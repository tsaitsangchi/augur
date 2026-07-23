# AUD-02 `raw_supersede_log` 驗證清單

* **性質**：[I] 執行層驗證 checklist；供人類／agent 在有／無 PostgreSQL 環境照跑
* **依據**：`docs/remediation/AUD-02-raw-supersede-log.md`（設計卷宗 §四）、`tests/test_raw_supersede_log.py`、`scripts/migrate_raw_supersede_ddl.py`
* **repo 狀態（2026-07-23）**：**main 已落地程式**（`generic_schema` 快照 seam、`schema.INFRA_DDL`、migration 硬化、`setup_predict_role` REVOKE 明列、pytest 回歸）；**生產 DB apply 仍待人類 P5 拍板**（本清單只驗「環境內可證明之行為」，不假關治理日曆）
* **本機實測基線（無 PG）**：venv `migrate --selftest` 全綠；`pytest tests/test_raw_supersede_log.py` → **8 passed, 7 skipped**；`--check` → `connection refused`（預期，非 repo 缺陷）

---

## 一、repo 已落地 vs 需 PostgreSQL

| 類別 | 內容 | 本清單項 |
|---|---|---|
| **repo 已落地**（無 PG 可驗） | 設計卷宗、DDL 常數、migration 腳本、`--selftest` 純邏輯六不變式、pytest (A) 純函式＋gate、`schema`／`generic_schema` module selftest | §三（5 項） |
| **需 PostgreSQL** | migration `--check`／apply、VERIFY 清單、pytest (B) DB 六不變式、append-only trigger、tombstone、同交易回滾、`setup_predict_role` 禁讀驗證 | §四（7 項＋選配） |

**項數摘要**：無 PG 必跑 **5** 項（§三）；有 PG 必跑 **7** 項（§四）；選配 **2** 項（§四末）。

---

## 二、前置（兩類環境共通）

在專案根目錄 `/home/hugo/project/augur` 執行。

| # | 步驟 | 指令 | 預期 | 失敗時看什麼 |
|---|---|---|---|---|
| P1 | 進 venv | `source venv/bin/activate`（或 `.venv/bin/activate`） | prompt 前綴 `(venv)` | 無 venv → `pip install -e .` 建環境 |
| P2 | 套件就緒 | `pip install -e .` | 無 error | `ModuleNotFoundError: augur`／`psycopg2` → 重裝 editable |
| P3 | `.env` 存在 | `test -f .env && echo OK` | 印 `OK` | 複製範本、填 `DB_HOST`／`DB_PORT`／`DB_NAME`／`DB_USER`／`DB_PASSWORD` |
| P4 | **（僅 PG 項）** PG 可連 | `venv/bin/python -c "from augur.core import config, db; db.connect().close(); print('PG OK')"` | 印 `PG OK` | `Connection refused` → 起 postgres；認證失敗 → 查 `.env` 與 `pg_hba.conf` |
| P5 | **（僅 PG 項）** 目標庫 | 同上；`DB_NAME` 應為 `augur`（或你方約定庫名） | 連線成功 | 庫不存在 → `createdb augur` 或還原 dump |
| P6 | **（tombstone 正向路徑）** superuser | `.env` 設 `DB_SUPERUSER`（預設 `postgres`）＋`DB_SUPERUSER_PASSWORD` | tombstone 測不 skip | 缺則 `test_db_tombstone_controlled_erasure` 只驗「應用角色被拒」、owner 正向路徑 **skip**（非 FAIL） |

---

## 三、無 PostgreSQL 可跑項（預期綠／可勾）

> 下列項在 **無 PG 監聽** 時仍應全 PASS。DB 測試 **skip ＝ 誠實略過，非假 PASS**（CLAUDE #15）。

### 3.1 migration 純邏輯 selftest

```bash
venv/bin/python scripts/migrate_raw_supersede_ddl.py --selftest
```

| 預期 | 失敗時 |
|---|---|
| 結尾 `自測:全通過 ✓(①②③④＋純 insert 零 IO 綠;⑤⑥需 PG)`；exit 0 | 任一 `✗FAIL` → 查 `src/augur/core/generic_schema.py` 之 `_supersessions`／`provision_and_upsert` gate |

### 3.2 pytest — 純函式層 (A) ＋ gate

```bash
venv/bin/python -m pytest tests/test_raw_supersede_log.py -v --tb=short
```

| 預期 | 失敗時 |
|---|---|
| **8 passed, 7 skipped**（skip 原因含 `DB 不可用`） | passed＜8 → 看失敗 test 名；不應為 import error |

### 3.3 schema 模組 selftest（INFRA_DDL 含 `raw_supersede_log`）

```bash
venv/bin/python -m augur.core.schema --selftest
```

| 預期 | 失敗時 |
|---|---|
| `INFRA_DDL 含 … raw_supersede_log` ✓；exit 0 | 缺表名 → `src/augur/core/schema.py` INFRA_DDL 未同步 |

### 3.4 generic_schema 模組 selftest（AUD-02 邏輯鎖）

```bash
venv/bin/python -m augur.core.generic_schema --selftest
```

| 預期 | 失敗時 |
|---|---|
| `_supersessions`／`provision_and_upsert 預設 snapshot_reason=None` 全 ✓ | 比對 `reconcile._norm` 是否仍共用 |

### 3.5 指令矩陣稽核（選配、零 DB）

```bash
venv/bin/python scripts/check_cmd_matrix.py
```

| 預期 | 失敗時 |
|---|---|
| exit 0；`migrate_raw_supersede_ddl.py` 不在缺漏清單 | 補 docstring「執行指令矩陣」區塊 |

**§三 勾選判定**：3.1–3.4 全 exit 0 且 pytest **8 passed** → 可宣稱 **「repo 層 AUD-02 驗證 PASS（無 PG 範圍）」**。

---

## 四、有 PostgreSQL 必跑項

> 在 §二 P4–P5 通過後執行。建議順序：check →（必要時）apply → pytest 全綠 → predict role。

### 4.1 migration 唯讀 `--check`（VERIFY 清單）

```bash
venv/bin/python scripts/migrate_raw_supersede_ddl.py --check
```

| 預期 | 失敗時 |
|---|---|
| 印 `── 驗證清單 ──`；各列有值（非 `(查詢失敗:…)`）；exit 0 | 表不存在 → 跑 4.2 apply；連線錯 → §二 P4 |

**VERIFY 應含（摘要）**：

| 標籤 | 應見 |
|---|---|
| raw_supersede_log 欄 | `id, table, pk, old_row, new_row, superseded_at, valid_time, reason, attestation_run_id, note, actor`（順序以 DB 為準） |
| FK→attestation_result | 外鍵定義字串 |
| 索引 | `ix_supersede_pk_gin`, `ix_supersede_run`, `ix_supersede_table_time`, `raw_supersede_log_pkey` |
| triggers | `trg_raw_supersede_append_only`, `trg_raw_supersede_no_truncate` |
| tombstone 受控函式 | `raw_supersede_tombstone(SECURITY DEFINER✓)` |
| PUBLIC mutate 權 | `(無)` 或不含 UPDATE/DELETE/TRUNCATE |

### 4.2 migration apply（表／硬化尚未存在時）

```bash
venv/bin/python scripts/migrate_raw_supersede_ddl.py
```

| 預期 | 失敗時 |
|---|---|
| 逐行 `✓ table raw_supersede_log` … `✓ revoke tombstone execute from public`；再印 VERIFY；exit 0 | 權限不足 → 用 owner／superuser 連線；重跑應冪等（IF NOT EXISTS） |

**注意**：破壞性僅限「新表＋硬化」；**生產 apply 仍須人類 P5 拍板**——本項用於沙盒／備援／本機驗證庫。

### 4.3 pytest — DB 行為層 (B) 全綠

```bash
venv/bin/python -m pytest tests/test_raw_supersede_log.py -v --tb=short
```

| 測試 | 驗什麼 |
|---|---|
| `test_db_gate_non_heal_no_snapshot` | 非 heal 主路徑不留痕 |
| `test_db_heal_byte_differ_logged` | heal 值異 → 入帳 old/new |
| `test_db_heal_noop_not_logged` | heal no-op 不入帳 |
| `test_db_append_only_blocks_update_delete` | UPDATE/DELETE → RAISE |
| `test_db_truncate_blocked` | TRUNCATE → RAISE |
| `test_db_tombstone_controlled_erasure` | 應用角色 EXECUTE 被拒；owner＋事由 tombstone |
| `test_db_same_transaction_rollback` | 同交易 SAVEPOINT 回滾 → 快照與 upsert 皆撤 |

| 預期 | 失敗時 |
|---|---|
| **15 passed, 0 failed**（tombstone owner 路徑：有 `DB_SUPERUSER_PASSWORD` 則全跑；無則 1 skip 可接受） | trigger 缺 → 4.2；權限 → Phase 1 owner 分離見 `ops/phase1/` |

### 4.4 append-only／TRUNCATE 手動 spot-check（選配）

在 psql 或 `python -c` 對**測試庫**、已有一筆 log 後：

```sql
-- 應 RAISE（用 SAVEPOINT 包）
UPDATE raw_supersede_log SET note='x' WHERE id=(SELECT min(id) FROM raw_supersede_log);
DELETE FROM raw_supersede_log WHERE id=(SELECT min(id) FROM raw_supersede_log);
TRUNCATE raw_supersede_log;
```

| 預期 | 失敗時 |
|---|---|
| 三句皆 exception；列數不變 | 查 `pg_trigger`／`migrate_raw_supersede_ddl.py` DDL 段 |

### 4.5 tombstone 受控函式（選配、需 superuser）

```sql
-- 以 superuser：取一筆 id 後
SELECT raw_supersede_tombstone(<id>, 'GDPR erasure req #42');
-- 應 old_row/new_row 含 "_tombstoned": true；列仍在
```

| 預期 | 失敗時 |
|---|---|
| 空事由 RAISE；合法事由 → tombstone 骨架＋note 含 reason | `REVOKE EXECUTE FROM PUBLIC` 是否 apply |

### 4.6 `setup_predict_role` — `raw_supersede_log` 禁讀

**唯讀盤點**（role 未建亦可）：

```bash
venv/bin/python scripts/setup_predict_role.py --dry-run
```

| 預期 | 失敗時 |
|---|---|
| forbidden 列表含 `raw_supersede_log`；若 `augur_predict` 已存在 → 對該表 SELECT=**拒** | 表不在 forbidden → `scripts/setup_predict_role.py` `FORBIDDEN_EXPLICIT` |

**role 已存在但新建表後 grants 未 refresh 時**：

```bash
venv/bin/python scripts/setup_predict_role.py --apply --confirm
```

| 預期 | 失敗時 |
|---|---|
| `REVOKE … 素養表` 含 `raw_supersede_log` | 需 `DB_PREDICT_PASSWORD`；無 CREATEROLE → superuser 代建 |

**明確 SQL 驗證**（role 已存在時）：

```sql
SELECT has_table_privilege('augur_predict', 'raw_supersede_log', 'SELECT');
-- 應 false
```

### 4.7 migration 冪等重跑

```bash
venv/bin/python scripts/migrate_raw_supersede_ddl.py
venv/bin/python scripts/migrate_raw_supersede_ddl.py --check
```

| 預期 | 失敗時 |
|---|---|
| 第二次 apply 無 error；VERIFY 與 4.1 一致 | 非冪等 DDL → 腳本 regression |

**§四 勾選判定**：4.1 VERIFY 全綠 ＋ 4.3 **15 passed（或 14 passed + 1 skip 僅 tombstone owner）** ＋ 4.6 forbidden／SELECT 拒 → 可宣稱 **「DB 環境 AUD-02 驗證 PASS」**。

---

## 五、結案判定（分級）

| 層級 | 條件 | 可宣稱 |
|---|---|---|
| **L1 — repo** | §三 3.1–3.4 全綠；pytest 8 passed / 7 skipped | repo 層 AUD-02 驗證 PASS；**不可**宣稱生產 DB 已合規 |
| **L2 — DB 沙盒／本機** | L1 ＋ §四 4.1–4.3（＋建議 4.6）全綠 | **DB 環境 AUD-02 驗證 PASS**（該庫實證） |
| **L3 — 生產** | L2 於**目標生產庫**重跑 ＋ Steward **P5 拍板** apply ＋ `#19` 逐檔檢視 | AUD-02 critical **生產解消**（仍不等於步 12／039／10-14 其他日曆結清） |

---

## 六、不假關聲明（治理邊界）

本清單 **僅** 驗證 AUD-02 程式與 DB 行為（P4.E5 矛盾保存／append-only／tombstone／predict 隔離）。**不得**因本清單全綠而：

* 宣稱 **RULING-2026-039** residual omnibus 或 **2026-10-14 併結 checklist** 已結清；
* 宣稱 **025 (iii)(iv)(vi)**、**029 日曆**、**WM.35／36** 過渡規則到期項已關；
* 宣稱 **AUD-02 生產 critical 已解消**（除非 L3 條件滿足）；
* 跳過 **人類 P5** 對生產 DB apply 之拍板。

原則精華 **#7**（新版本入庫、舊版標 superseded）已 **RULING-2026-041** 入憲；**code 施工／migration apply 仍另案**，不因 #7 入憲而假關 AUD-02 實作閘。

---

## 七、快速複製區（一頁跑完）

**無 PG：**

```bash
cd /home/hugo/project/augur && source venv/bin/activate
python scripts/migrate_raw_supersede_ddl.py --selftest
python -m augur.core.schema --selftest
python -m augur.core.generic_schema --selftest
python -m pytest tests/test_raw_supersede_log.py -v --tb=short
# 預期: 三 selftest exit 0；pytest 8 passed, 7 skipped
```

**有 PG：**

```bash
cd /home/hugo/project/augur && source venv/bin/activate
python -c "from augur.core import db; db.connect().close(); print('PG OK')"
python scripts/migrate_raw_supersede_ddl.py --check    # 失敗→下一行 apply
python scripts/migrate_raw_supersede_ddl.py            # 冪等；生產須 P5
python -m pytest tests/test_raw_supersede_log.py -v --tb=short   # 預期 15 passed
python scripts/setup_predict_role.py --dry-run       # raw_supersede_log ∈ forbidden
```

---

## 八、相關路徑

| 用途 | 路徑 |
|---|---|
| 設計 SSOT | `docs/remediation/AUD-02-raw-supersede-log.md` |
| Migration | `scripts/migrate_raw_supersede_ddl.py` |
| 回歸測試 | `tests/test_raw_supersede_log.py` |
| 快照 seam | `src/augur/core/generic_schema.py` |
| INFRA DDL | `src/augur/core/schema.py` |
| Predict 隔離 | `scripts/setup_predict_role.py` |
| 補正行程 | `audits/REMEDIATION-ROADMAP.md` 步 7 |

---

*建立：2026-07-23｜性質：[I] 執行驗證 checklist｜下一動作：有 PG 環境補跑 §四。*
