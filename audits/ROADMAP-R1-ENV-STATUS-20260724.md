# Roadmap R1 環境親驗 [I]（2026-07-24）

* **性質**：[I] 驗收留痕（非 RULING）
* **拍板**：Steward「**開 R1**」→ 本機 PG 啟動後親驗 → **閉合 R1＝DONE**
* **路線圖**：`reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.2

## 總評

✅ **DONE**（2026-07-24）。證據來源＝Steward 本機 WSL 終端（`hugo@PC002-S1800`）；Cursor 代理命名空間仍可能看不到 5432，**不以代理連線失敗否決本機綠燈**。

## 驗收表

| # | 驗收項 | 結果 | 證據 |
|---|---|---|---|
| 1 | `.env` 存在 | ✅ PASS | `DB_HOST`／`DB_USER=augur`（密不入留痕） |
| 2 | `venv` 存在 | ✅ PASS | `./venv` |
| 3 | 核心 import smoke | ✅ PASS | 先前代理親驗 |
| 4 | `db.ping()` | ✅ PASS | Steward：`True`（PG 17 main online） |
| 5 | cmd matrix（#29） | ✅ PASS | NEED=0（321） |
| 6 | schema／AUD-02 `--selftest` | ✅ PASS | 先前代理親驗 |
| 7 | AUD-02 `--check`＋pytest DB | ✅ PASS（行為）／⚠ 硬化殘留 | pytest **15 passed**；`--check` 見下 |
| 8 | ollama（可選） | ✅ PASS | Steward：11434 LISTEN；`qwen3:4b`／`8b`／`nomic-embed-text` |

## Steward 本機親跑（閉合依據）

```text
pg_lsclusters → 17 main 5432 online postgres
pg_isready → accepting connections
db.ping() → True
migrate_raw_supersede_ddl.py --check → 表／欄／FK／pkey 在；列數 0
pytest tests/test_raw_supersede_log.py → 15 passed in 0.79s
```

## AUD-02 硬化殘留（不擋 R1 DONE）

`--check` 報告：

* triggers(append-only + no-truncate)：**(無)**
* tombstone SECURITY DEFINER：**(無)**
* 表 COMMENT：**(無)**

表本體已在、pytest 行為層全綠；append-only／tombstone DDL 可能尚未 apply。建議另指令：

```bash
./venv/bin/python scripts/migrate_raw_supersede_ddl.py   # 無 --check＝執行硬化 DDL
./venv/bin/python scripts/migrate_raw_supersede_ddl.py --check
```

## 刻意不做

* 假關 10-14／039
* 未改 MC／specs [N]
* 本輪未代跑 hardening apply（待 Steward「套用 AUD-02 硬化」）
