# M-N1／M-N2 落地帳（2026-08-03）

> 位階：[I] · 對應 `reports/augur_optimization_master_plan_20260803.md` §1.4／第 9・19・20 步骨架  
> 授權：hugo 明示允許 `migrate_measure_registry_ddl.py --apply` → `migrate_treaty_probe_ddl.py --apply`

## 做了什麼

1. **DDL（live）**：`measure_registry`＋`treaty_probe_binding`＋`treaty_probe_reading`；兩支 `--verify-red` 皆綠、零殘留。
2. **消費腳本（新）**：`register_measure.py`／`sync_treaty_probes.py`／`read_treaty_probes.py`／`probe_ve_manual_1014_window.py`（矩陣＋`--selftest`）。
3. **資料面**：`--register-defaults`（3 尺，**authoritative=false**）＋`--seed-1014`（**13** 條 `deadline=2026-10-14`，全 `owner=Steward`）＋`read --apply`（每條 ≥1 reading，verdict 皆 `undecidable`）。

## 驗收（現查）

| 條件 | 結果 |
|---|---|
| `SELECT count(*) FROM treaty_probe_binding WHERE deadline='2026-10-14'` ≥ 13 | **13** |
| `read_treaty_probes.py --check` | **rc=0** |
| Steward reading 無 AI 寫入 `meets` | **0 筆非 undecidable** |
| `check_cmd_matrix` 缺漏 | **0**（受檢進至 **482**） |

## 未做（誠實殘項）

- **未代標**任一 `authoritative`（M-N2 第 20 步驗收①＝Steward 批次標定）。
- **未代勾**七框 `[ ]`（RULING-2026-039）。
- M-N1 過期族「文件數字→探針 diff」尚待第 19 步把 HANDOFF／CLAUDE 等 7 處改為引 `probe_id`。
- honesty trigger 掛否仍繫 **M-P11**。

## 同日已關閉環境項（本帳附記）

- 三 stale worktree **已 remove**；`check_worktree_treaty_sync.py --check` **rc=0**。
- M-G1／M-T2／M-G2／M-G3／M-M1／M-M2 碼側已綠（先前 SSOT 提交）；今晚仍守 **M-T5**（不搶 heavy_slot、不 `--allow-apply`）。
