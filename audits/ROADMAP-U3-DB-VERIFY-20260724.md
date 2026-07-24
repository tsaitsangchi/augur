# Roadmap U3 DB 親驗 [I]（2026-07-24）

* **性質**：[I] 驗收留痕（非 RULING；不改 [N]）
* **對應帳本**：`reports/augur_roadmap_r3_gap_ledger_20260724.md` G-OUT-1／G-FT-1
* **環境**：WSL `/home/hugo/project/augur`；`./venv/bin/python`；`.env` 載入；PG `127.0.0.1:5432` accepting

## 總評

兩項皆 **PASS** → 帳本 G-OUT-1／G-FT-1 建議／已標 `gap_class=none`（親驗落地）。未 `git commit`／未 `archive_push`。

## Task 1 — direction product gate `--verify`

```bash
cd /home/hugo/project/augur
set -a && source .env && set +a
./venv/bin/python scripts/migrate_direction_product_gate_ddl.py --verify
```

| 項 | 結果 |
|---|---|
| exit | **0** |
| 判定 | **PASS**（`verify()` 兩負向皆拒寫） |
| stdout | `✓ evaluated_fail 門:trigger 拒寫`；`✓ 不存在門:trigger 拒寫`；`(正向路徑無 evaluated_pass 門可測——誠實留待首個 pass 門)` |
| 附證 `pg_trigger` | `trg_dirprob_gate_guard` on `direction_probability`；`trg_ddirprob_gate_guard` on `daily_direction_probability` |

註：agent sandbox 初跑曾 `Connection refused`（沙箱擋 localhost）；改 unrestricted／本機 PG online 後綠。

## Task 2 — `chk_itext_owned_local_private`

```sql
SELECT conname, conrelid::regclass::text, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conname = 'chk_itext_owned_local_private';
```

| 項 | 結果 |
|---|---|
| 存在 | **有**（1 列） |
| 表 | `knowledge_item_text` |
| 定義原文 | `CHECK ((((license)::text <> 'owned_local'::text) OR ((access_scope)::text = 'local_private'::text)))` |

## 對帳本建議

| ID | 親驗前 | 親驗後建議 |
|---|---|---|
| G-OUT-1 | partial（未親驗） | **none** |
| G-FT-1 | partial（live 待確認） | **none** |
