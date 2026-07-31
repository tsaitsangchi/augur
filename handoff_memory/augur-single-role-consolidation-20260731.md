---
name: augur-single-role-consolidation-20260731
description: "2026-07-31「augur ＝ 全部」整併終態：單一角色 augur(superuser)、augur_predict 退役使 #8 失去 DB 層、三庫已刪、ttai_import 併入 public、備份只剩 C 碟一份"
metadata: 
  node_type: memory
  type: project
  originSessionId: b877d307-e736-407a-aa6a-200f3758f684
  modified: 2026-07-31T07:59:59.847Z
---

**終態（2026-07-31 晚，全部實查）**：資料庫僅 `augur`＋`postgres`；**角色僅 `augur`（superuser）＋`postgres`**；
schema 僅 `public`（**322** 表）。`pytest` 256 passed／14 skipped／0 failed。
計畫書＝repo `reports/augur_single_role_consolidation_plan_20260731.md`（含逐步進度、教訓、驗收指令）。

**四項不可逆變更**（皆 Steward 拍板；OCV 對照留痕於 `reports/augur_db_role_architecture_submission_20260731.md` §6.2）：
1. `ALTER ROLE augur SUPERUSER`（hugo 親跑）；2. `DROP ROLE augur_predict`；
3. `DROP DATABASE ttai/rdai/stock` ＋ 三角色（`stock` 那個 superuser 隨之消失）；
4. `ttai_import` 16 表＋11 seq＋6 view＋2 enum `SET SCHEMA public` 後 DROP schema。

**⚠ 最重要的一句：`#8` 隔離之 DB 層已不存在，且原理上無法重建**——單一角色擁有全部表，
`REVOKE` 對 owner 無效（owner 可自我 GRANT）。現唯 `src/augur/audit/import_isolation.py` 之
**AST 字面稽核**（射程 7 package＋core；`execution`／`arena`／`identity`／`deliberation` **不在集合內**）。
**擋不到動態 SQL**——那原本是 DB 層 REVOKE 的職責，屬淨損失、非換法可補。
WM.35 消費閘之新證據即此（S22 定案，GROUNDING-MAP:176 有可重跑指令，實跑違規數 0）。

**改名**：`ttai_import.knowledge_source` → **`public.knowledge_unit_source`**（102,564 列，逐單元出處紀錄，
FK→`knowledge_unit`／`extraction_run`）。與 `public.knowledge_source`（**3,605 列，知識管線來源登錄簿，
帶 `chk_ks_active_needs_approval` 人簽閘**）是**完全不同的兩張表**——查詢前先確認要哪一張。

**備份現況（換機／災後必看）**：`~/db_dumps/` **已被清空**。唯一備份＝
**`/mnt/c/database/augur_pgdump_20260731_Fd`**（本日 09:20 建、11 GB、2,748 物件、`pg_restore -l` 可解析、
**含整併前之 `ttai_import` 151 物件與 `touch_updated_at()`＋2 trigger**）。HANDOFF §3 已改指向它。

**三個獨立證據證明 `GROUNDING-MAP` 07-17/18 基線與 `HANDOFF §0.5` 描述的不是本機**：
`/home/giga` 不存在且無此帳號／`/mnt/d` 不存在／「十新表」live 僅 `raw_supersede_log` 一張在。
已於 GROUNDING-MAP:8 加機器身分揭露、:3 加全域導讀。**日後見「本機 live 與 $S 不符」勿逕判為某次變更所致。**

**兩則遷移教訓（同一病犯兩次）**：
- **撞名檢查須含索引／約束層**——`ALTER TABLE RENAME` **不改索引與約束名**；首次交易因
  `knowledge_source_pkey already exists` 原子回滾（單一 transaction 的設計救了一次）。
- **清點須涵蓋五類**：`pg_class`(r/v/m/S/**i**)、`pg_constraint`、**`pg_proc`**、`pg_type`、`pg_trigger`。
  漏了 `pg_proc` ⇒ `touch_updated_at()` 未搬 ⇒ `DROP SCHEMA CASCADE` 連帶刪掉 2 個 trigger。

**另修一個既有缺陷**：`tests/test_release_lag_antileakage.py` 之 `_clean` 含 `feature_values`，
被 `fv_guard` 拒而拋例外 ⇒ `commit()` 到不了 ⇒ **前三張表已刪之列一併回滾**，清理看似執行實則零效果，
synthetic 列累積於生產表（實證殘留 313 列）。已改逐表獨立子交易＋帶通行證。**判斷句：清理程式碼跑完
不代表清乾淨了——要驗殘留數。**

**S9 的唯一機械紅燈已刪**：`test_db_tombstone_controlled_erasure` 斷言「應用角色被拒」，superuser 後恆 FAIL，
Steward 拍板刪除（原位留說明段）。⇒ **superuser 這件事在 repo 內已無自動紅燈，只剩文件留痕。**

**同日附帶完成**：D8 硬編版號全刪（README:30／原則精華:7 改為「以 `ls docs/` 現查為準」，
`check_treaty_refs` 首度 RC=0）；S21 KS.20-24 之 🔨 經 Steward 拍板閉合（依據與不利事實同格留存）；
qdrant 二進位遷入 `augur/.qdrant_server/`（r2 債 #40 結案）。
