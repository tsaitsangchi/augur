# Entity registry backfill — GB10 — 2026-07-22

* **性質**：[I] 證據紀錄。順序依 `ops/phase2/P5-SUBMISSION-2026-07-18.md`（retire→mint→attrs）。
* **主機**：`aitopatom-b96e`；庫 `augur`（userspace PG）。
* **腳本來源**：`origin/remediation/phase2-retire-backfill`（本機 main 原先缺 `backfill_lifecycle_retire.py`／`acquire_code_lock`；已 checkout 相關檔至工作樹，**尚未另開 PR 併入 main**）。

## 終態（實查）

| 項 | P5 核准錨 | GB10 實跑 |
|---|---|---|
| entity_registry | 3,491 | **3,491** |
| entity_alias | 3,491 | **3,491** |
| provisional alias | 235 | **235** |
| lifecycle retire 事件 | 342 | **342** |
| entity_attribute_version | 9,258 | **9,258** |
| 名實不符佇列 | 37 | **37**（CSV：`reports/identity_retire_name_mismatch_20260722_gb10.csv`） |

## 步驟

0. `seed_entity_type_catalog.py` → catalog 4 列  
1. `backfill_lifecycle_retire.py --apply` → retire 342  
2. `backfill_entity_registry.py --apply` → registry 3491（含紅旗 provisional 235）  
3. `sync_attribute_versions.py --apply` → attrs 9258  

詳細 stdout：本機 `ops/phase2/ENTITY-BACKFILL-APPLY-20260722.log`（`*.log` gitignore）。

## 注意

- 此批 `augur_id` 為 **GB10 新鑄**，與 DESKTOP 若曾 backfill 之 ID **不保證相同**。  
- 併入 main 前請 Steward 決定是否把 remediation 分支 identity 補件合倉。
