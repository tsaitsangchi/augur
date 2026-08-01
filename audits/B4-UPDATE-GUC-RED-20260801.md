# B4 突變驗紅紀錄（UPDATE-GUC 升級；2026-08-01 波2 施作）

依 CLAUDE.md #35「凡新回歸鎖必先驗紅」——`scripts/migrate_honesty_guards_ddl.py` B4 新斷言群
與寫入者通行證 V9 census 之紅證。呈案＝`reports/w2_20260801/B4_update_guc_upgrade.md`（Steward 圈選甲案）。
DDL 本波**未執行**（歸波3統一窗）；驗紅全在 scratch 副本，repo 檔全程綠。

## 突變矩陣（scratch 副本退壞版 → 對應 case 紅）

| 突變 | 退壞內容 | 紅之斷言 | 結果 |
|---|---|---|---|
| M1 | `_upgrade_sql` 抽掉 `SET LOCAL lock_timeout = '5s';` | 「交易首句 SET LOCAL lock_timeout」×4 表 | ✗ rc=1 |
| M2 | row 閘退化 `BEFORE UPDATE OR DELETE` → `BEFORE DELETE` | 「row 閘=BEFORE UPDATE OR DELETE→honesty_ledger_guard」×4 | ✗ rc=1 |
| M3 | `PME_TABLES` 誤把 principle_factor_map 加回（重疊+數目6） | 「PME 五表覆蓋」＋「B4 四表與 PME 組互斥」 | ✗ rc=1 |
| M4 | 升級誤用 `honesty_delete_only_guard()` 為 row 閘函式 | 「row 閘=…→honesty_ledger_guard」×4 | ✗ rc=1 |
| M5 | `verify_philosophy_factors.py` 抽掉一個通行證點 | V9 census（10 點命中）→ 9 ≠ 10 | ✗ 可偵測 |

M1–M4＝`--selftest` 純函式斷言（餵 `_upgrade_sql()`／常數組實輸出，非整檔字面——#35(1)(3)）；
M5＝V9 通行證 census（`grep -c "SET LOCAL augur.honesty_write"` 於 9 檔，期望計數 2+2+1+1+1+1+1+1=10）。

## 綠證（修復版）

- `migrate_honesty_guards_ddl.py --selftest` 36/36 ✓ rc=0；`--check`（唯讀）rc=0。
- V9 census＝10/10；9 檔寫入者 selftest 全 rc=0（verify_philosophy_factors 無 selftest＝py_compile）；
  `apply_evolution_promotions --dry-run`／`--backfill-prodset --dry-run` rc=0。
- GUC 探針（寫入者同款 `db.connect()` 路徑）：`SET LOCAL augur.honesty_write='on'` 可設、rollback 零殘留。
- `check_false_assertions.py --gate` rc=0（無新增）；`check_cmd_matrix.py` rc=0。

## 射程誠實

selftest 斷言驗的是「產出之 DDL 字串結構」（純函式輸出），**非** live trigger 行為——
行為面（裸 UPDATE 拒／帶證過／DELETE 恆拒）唯波3 DDL 窗後之 V3–V6 探針可證（呈案 §6）。
半閘非硬閘：C5「GUC 對引擎豁免」警告全數保留。
