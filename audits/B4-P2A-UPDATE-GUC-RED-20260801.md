# B4-P2a 突變驗紅紀錄（五表升級 UPDATE-GUC；2026-08-01 施作）

依 CLAUDE.md #35「凡新回歸鎖必先驗紅」——`scripts/migrate_honesty_guards_ddl.py` P2a 新斷言群、
兩原住所檔（`migrate_steward_qledger_ddl.py`／`src/augur/audit/evolution_ledger_ddl.py`）同步斷言、
與寫入者通行證 V9 census 之紅證。呈案＝`reports/w2_20260801/B4P2_remaining_tables_proposal.md`
（Steward 圈選「P2a-同意＋§5-乙（kill_switch 排除）＋編號併 RULING-2026-043」）。
DDL 本批**未執行**（歸主 session DDL 窗）；驗紅全在 scratch 副本，repo 檔全程綠。

## 突變矩陣（scratch 副本退壞版 → 對應 case 紅）

| 突變 | 退壞內容 | 紅之斷言 | 結果 |
|---|---|---|---|
| M-A1 | `LEGACY_TRIGGERS` 拔一名（hint_no_truncate） | 「hint:卸 legacy 名 hint_no_delete+hint_no_truncate」 | ✗ rc=1 |
| M-A2 | `LEGACY_TRIGGERS` 拔整條 evidence 映射 | 「evidence:卸 legacy 名 evidence_no_delete+evidence_no_truncate」 | ✗ rc=1 |
| M-B | `resolve_questions.py` 拔一個通行證點（第 5 點） | V9 census（10 點凍結）→ 4≠5 | ✗ rc=1 |
| M-C | qledger TRIGGERS 退回 delonly（BEFORE DELETE＋delete_only_guard） | 「guard=honesty_ledger_guard」＋「row 閘=BEFORE UPDATE OR DELETE」 | ✗ rc=1 |
| M-D | HINT_DDL row 閘函式退回 `honesty_delete_only_guard` | 「hint/evidence 已升 UPDATE-GUC…雙 trigger+卸 legacy 名不掛回」 | ✗ rc=1 |

M-A/C/D＝`--selftest` 純函式斷言（餵 `_upgrade_sql()`／`TRIGGERS`／`HINT_DDL` 實輸出，
非整檔字面——#35(1)(3)）；壞變體另有 in-selftest 驗紅（`_registry_problems`：PME 重疊、legacy 鍵懸空）。
M-B＝V9 通行證 census（`grep -c "SET LOCAL augur.honesty_write"` 逐檔對凍結值：
apply_evolution_promotions 4〔2 B4-P0＋2 P2a〕、resolve_questions 5、triage_questions 1、
serve_admin_console 1、ops/a3_gsign/rollback_pending_auto_gsign.sql 1＝10 點）。

## 綠證（修復版；2026-08-01）

- `migrate_honesty_guards_ddl.py --selftest` 53/53 ✓ rc=0。
- `migrate_steward_qledger_ddl.py --selftest` rc=0；`python -m augur.audit.evolution_ledger_ddl --selftest` rc=0。
- pytest `test_evolution_ledger_ddl.py`＋`test_evolution_contract_ledger.py` 12 passed。
- V9 census＝10/10；`apply_evolution_promotions --selftest/--dry-run/--backfill-prodset --dry-run`、
  `triage_questions --selftest/--dry-run`、`resolve_questions --selftest/--classify --dry-run`、
  `run_raw_evolution_iteration --selftest` 全 rc=0；`serve_admin_console.py` py_compile ✓。
- GUC 探針：triage/classify dry 路徑實跑新 `SET LOCAL augur.honesty_write='on'`（交易起點）——可設、
  rollback/commit 零殘留。
- `check_false_assertions.py --gate` rc=0（無新增）；`check_cmd_matrix.py` rc=0。
- `migrate_pending_auto_gsign.sql` 已執行（77 列 `decided_by='gate_set_migration_gsign'` 在庫）＝史料；
  其冪等重跑謂詞命中 0 列、trigger 不觸發，免補丁（rollback SQL 已補通行證）。

## 射程誠實

selftest 斷言驗的是「產出之 DDL 字串結構」（純函式輸出），**非** live trigger 行為——行為面
（裸 UPDATE 拒／帶證過／DELETE 恆拒／forward-only 並存）唯 DDL 窗後之呈案 §7 探針可證。
半閘非硬閘：C5「GUC 對引擎豁免」警告全數保留。kill_switch 依 §5 乙案**未上閘**（緊急煞車零摩擦），
其 clear 默改面保留＝已知殘險（緩解＝watchdog／n_tup_upd 事後稽）。
