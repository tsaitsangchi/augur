# Roadmap R1 環境親驗 [I]（2026-07-24）

* **性質**：[I] 驗收留痕（非 RULING）
* **拍板**：Steward「**開 R1**」（R0／R2 已 DONE；〔A〕〔U-defer〕〔S1〕）
* **路線圖**：`reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.2

## 總評

**PARTIAL／BLOCKED on PG** — 非「環境全綠」。repo／venv／import／selftest 親驗通過；**`db.ping()` = False**（`127.0.0.1:5432` connection refused；`pg_isready` = down）。本 WSL 環境無法以 sudo 啟動 postgresql（sudoers 權限異常）。**不宣稱 R1 全綠 DONE。**

## 驗收表

| # | 驗收項 | 結果 | 證據 |
|---|---|---|---|
| 1 | `.env` 存在（人前置） | ✅ PASS | 檔案存在（內容不入本留痕） |
| 2 | `venv` 存在 | ✅ PASS | `./venv` |
| 3 | 核心 import smoke | ✅ PASS | `augur`／`schema`／`generic_schema`／`sync`／`reconcile` |
| 4 | `db.ping()` | ❌ FAIL | `ping: False`；5432 no response |
| 5 | scripts 指令矩陣（#29） | ✅ PASS | `check_cmd_matrix.py` → NEED=0（321 支） |
| 6 | schema／AUD-02 `--selftest` | ✅ PASS | `augur.core.schema --selftest`；`migrate_raw_supersede_ddl.py --selftest` |
| 7 | AUD-02 migration `--check`（需 PG） | ⏭ SKIP／blocked | `psycopg2.OperationalError: Connection refused` |
| 8 | ollama（可選） | ⏭ n/a | `127.0.0.1:11434` 無回應 |

## 親跑指令摘要

```bash
./venv/bin/python -c "from augur.core import db; print(db.ping())"   # False
./venv/bin/python -c "import augur; …"                                 # OK
./venv/bin/python -m augur.core.schema --selftest                      # 全通過
./venv/bin/python scripts/migrate_raw_supersede_ddl.py --selftest      # 全通過（⑤⑥需 PG）
./venv/bin/python scripts/check_cmd_matrix.py                          # NEED=0
pg_isready -h 127.0.0.1 -p 5432                                        # down
```

HEAD（親驗時）：`3d8f2f9`

## 殘留（解阻後重跑）

用戶於本機／WSL **啟動 PostgreSQL** 後：

1. `./venv/bin/python -c "from augur.core import db; assert db.ping()"`
2. `./venv/bin/python scripts/migrate_raw_supersede_ddl.py --check`（必要時 apply）
3. `./venv/bin/pytest -q tests/test_raw_supersede_log.py`（目標含 DB 層；見 `audits/AUD-02-VERIFY-CHECKLIST-20260724.md` §四）

以上綠 → 可另指令「**閉合 R1**」升級為 DONE。

## 刻意不做

* 假稱 `db.ping()` 通過
* 假關 10-14／039 項
* 未跑 `import_database.sh`（DB 未起；且破壞性需 `--force`）
* 未改 MC／specs [N]
