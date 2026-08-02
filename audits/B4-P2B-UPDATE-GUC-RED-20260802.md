# B4-P2b 突變驗紅紀錄（六表升級 UPDATE-GUC；2026-08-02 施作）

依 CLAUDE.md #35「凡新回歸鎖必先驗紅」——`scripts/migrate_honesty_guards_ddl.py` P2b 新斷言群、
兩原住所檔（`src/augur/audit/evolution_ledger_ddl.py`／`scripts/migrate_sim_evolution_ddl.py`）同步斷言、
與寫入者通行證 V9-P2b census 之紅證。呈案＝`reports/w2_20260801/B4P2_remaining_tables_proposal.md`
（Steward 圈選「P2b-同意、run 21 結輪後開窗」＋編號併 RULING-2026-043）。
**時機約束已實證**：run 21 於 2026-08-02 04:11:19 `succeeded` 結輪（evolution_run 親查）、
引擎行程零存活（ps 親查）——P2b 窗成立；原禁改二檔（run_evolution_iteration／run_philosophy_evolution）
已解禁後才動。DDL 本批**未執行**（歸主 session DDL 窗）；驗紅全在 scratch 副本，repo 檔全程綠。

## live 現況親驗（2026-08-02 pg_trigger 現查；閘前基線）

六表全數僅掛 `honesty_delete_only_guard`（DEL＋TRUNC 面）、UPDATE 面全裸、`honesty_ledger_guard` 零掛
——呈案六表集合與 live 一致，**無「已閘表誤算入集合」筆誤**（⚠07-25「兩帳本 honesty 上閘」係
trial_ledger／revalidation_baseline，非本批 evolution_iteration_ledger／raw_…——已查證不衝突）。
legacy trigger 實名（live 親查，非抄呈案猜名）：
tw_iter_no_delete_row／tw_iter_no_truncate・raw_iter_no_delete_row／raw_iter_no_truncate・
lai_iter_no_delete_row／lai_iter_no_truncate・**mcsim_no_delete／mcsim_no_truncate（無 `_row` 後綴）**；
evolution_run／evolution_coverage_snapshot＝標準 `trg_<t>_delonly_*` 名、免入 legacy 映射。

## 突變矩陣（scratch 副本退壞版 → 對應 case 紅）

| 突變 | 退壞內容 | 紅之斷言 | 結果 |
|---|---|---|---|
| M-A1 | `LEGACY_TRIGGERS` 拔一名（tw_iter_no_truncate） | 「evolution_iteration_ledger:卸 legacy 實名 tw_iter_no_delete_row+tw_iter_no_truncate」 | ✗ rc=1 |
| M-A2 | `LEGACY_TRIGGERS` 拔整條 mcsim 映射 | 「mc_simulation_run:卸 legacy 實名 mcsim_no_delete+mcsim_no_truncate」 | ✗ rc=1 |
| M-B | `simulate_portfolio_risk.py` 拔一個通行證點 | V9-P2b census（10 點凍結）→ 1≠2 | ✗ 可偵測 |
| M-C | `evolution_ledger_ddl.ledger_ddl()` 退回 delete-only | 「三 ledger 已升 UPDATE-GUC…雙 trigger+卸 legacy 名不掛回」 | ✗ rc=1 |
| M-D | `migrate_sim_evolution_ddl.M3_SQL` 退回 delonly | 「M3 已升 UPDATE-GUC…+卸 mcsim_no_* 不掛回」 | ✗ rc=1 |
| M-E | `PME_TABLES` 誤把 evolution_run 掛回（遷出後回流） | 「PME 僅餘 kill_switch」＋「五表集互斥（_registry_problems）」 | ✗ rc=1 |

M-A/C/D/E＝`--selftest` 純函式斷言（餵 `_upgrade_sql()`／`ledger_ddl()`／`M3_SQL` 實輸出，
非整檔字面——#35(1)(3)）；壞變體另有 in-selftest 驗紅（`_registry_problems`：PME∩P2B 重疊、
legacy 鍵懸空〔不在 P2A/P2B〕）。
M-B＝V9-P2b 通行證 census（`grep -c "SET LOCAL augur.honesty_write = 'on'"`〔execute 形帶空格；
排除 run_raw 教學印字之無空格形〕逐檔對凍結值：run_philosophy_evolution 2、run_evolution_iteration 2、
run_raw_evolution_iteration 1、audit_philosophy_feature_coverage 1、backfill_evolution_run_zombies 1、
simulate_mc_paths 1、simulate_portfolio_risk 2＝**10 點**）。

## 綠證（修復版；2026-08-02）

- `migrate_honesty_guards_ddl.py --selftest` 69/69 ✓ rc=0。
- `python -m augur.audit.evolution_ledger_ddl --selftest` rc=0；pytest
  `test_evolution_ledger_ddl.py`＋`test_evolution_contract_ledger.py` 12 passed。
- `migrate_sim_evolution_ddl.py --selftest` 15/15 GREEN rc=0（含新增「M3 已升」＋「sim 七表維持
  delete-only（P2c 緩議）」二鎖）。
- 寫入者 selftest 全 rc=0：run_evolution_iteration 55 ✓／run_philosophy_evolution 18 ✓／
  run_raw_evolution_iteration 25 ✓／audit_philosophy_feature_coverage 4 ✓／
  backfill_evolution_run_zombies 8 ✓／simulate_portfolio_risk 24 ✓（simulate_mc_paths 無 selftest
  ＝既有現況，py_compile ✓）。
- V9-P2b census＝10/10；`check_false_assertions.py --gate` rc=0（無新增）；`check_cmd_matrix.py` rc=0
  （456 支缺漏 0）。

## 射程誠實

selftest 斷言驗的是「產出之 DDL 字串結構」（純函式輸出），**非** live trigger 行為——行為面
（裸 UPDATE 拒／帶證過／DELETE 恆拒／mc upsert 衝突分支重跑）唯 DDL 窗後之呈案 §7 探針可證。
半閘非硬閘：C5「GUC 對引擎豁免」警告全數保留（引擎自帶通行證＝閘只擋裸手，不防引擎默改）。
kill_switch 依 §5 乙案**續留 delete-only**（緊急煞車零摩擦；`PME_TABLES` 明文僅此一表、絕不遷）。
local_ai_iteration_ledger 現零寫入者——未來 H1 R-CELL′ 寫入者出生即須帶通行證（約束已記呈案 §3#11）。
