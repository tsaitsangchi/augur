# 「augur ＝ 全部」單一化整併執行計畫書（2026-07-31）

> **性質**：[I] 執行計畫。涉治權變更（OCV 弱化）之部分已於 `reports/augur_db_role_architecture_submission_20260731.md` §6.2 留痕。
> **依 CLAUDE #20 計畫先行**；依憲章 v1.39.0 附 **(a) table schema**（§4）與 **(b) python 程式規畫**（§5）。
> **產製基準**：HEAD `77e28bd`；現況取樣 2026-07-31 14:0x–14:5x（ttai 目錄刪除後）。**引用前重跑附註指令。**

---

## §0 決定記錄（Steward 逐次拍板；本節為留痕，非建議）

| # | 決定 | 時點 |
|---|---|---|
| D-1 | 終局只有 `augur` 一個 DB 角色，**含 `augur_predict` 一併移除** | 07-31 下午 |
| D-2 | `augur` 升為 **superuser**（連維運也用 augur） | 同上 |
| D-3 | `ttai`／`rdai`／`stock` 三庫與角色清理 | 同上 |
| D-4 | `~/project/ttai/` 目錄**已刪**（Steward 親為，14:0x） | 已發生 |
| D-5 | qdrant「在 augur 專案會再重建」 | 同上 |
| D-6 | **`ttai_import` 16 表合併進 `public` 保留**（schema 併後刪除） | 07-31 晚 |
| D-7 | **DROP 前不 dump** | 同上 |

**OCV 四項對照**已於 D13 呈案 §6.2 載明（人類介入點 −1、揭露比例下降、否決可達性不變、自動鏈長不變）。

**⚠ D-6＋D-7 之交互**：因 16 表併入 public，ttai 庫之內容於併後即存在於 augur，故 D-7（不 dump）之風險由「資料永久消失」降為「**併失敗才會消失**」。
**⇒ 順序成為唯一保護：必須先併、驗過，才能刪。** 本計畫據此排序。

---

## §0.5 執行進度（2026-07-31 晚更新；本節為事實記錄）

| 步 | 狀態 | 備註 |
|---|---|---|
| S1 改名 | ✅ | `knowledge_source`→`knowledge_unit_source`；**含主鍵／2 FK／sequence 同步正名**（見下 L-1） |
| S2 SET SCHEMA | ✅ | 16 表＋11 seq＋6 view＋2 enum 於**單一 transaction** 完成 |
| S3 驗收 | ✅ **全綠** | 16/16 與搬動前 ttai 基線精確相符 |
| S4 DROP SCHEMA | ✅ | Steward 執行；連帶效應見 L-2 |
| S5 程式側 | ✅ **17/17** | 詳 §5.2；含刪除 `setup_predict_role.py` 與 `tests/test_predict_role_isolation.py`（`git rm`，歷史留存） |
| S6 服務重啟實測 | ✅ | qdrant 已重啟並以 `ps` 實測跑新路徑；餘服務未受改動 |
| S7 qdrant 路徑 | ✅ | unit `ExecStart`＋`install_services.sh:26` 改指 `augur/.qdrant_server/`；**r2 債 #40 結案** |
| S8 文件同步 | ✅ | GROUNDING-MAP 五處補註（含全域＋機器身分揭露）、HANDOFF 五處（§0.5／§3 dump SSOT／.env 兩列／重開機節） |
| **S9** 🔒 | ✅ | Steward 親跑，實查 `augur superuser=true` |
| **S10** 🔒 | ✅ | Steward 親跑 `DROP OWNED BY`＋`DROP ROLE augur_predict` |
| **S11** 🔒 | ✅ | `DROP DATABASE ttai/rdai/stock` ＋ `DROP ROLE` ×3 |

**全套驗收（2026-07-31 晚）**：`pytest tests/` → **256 passed／14 skipped／0 failed／0 errors**；
行為級檢查 `not hasattr(db,'connect_predict')` 等三項全過；全 repo 零功能殘留；
`check_cmd_matrix` 439/439（刪一支）；`check_treaty_refs` 僅餘 README:30 兩則（屬 D8 待裁）。

**S5 之三種處置分類（供日後同型工作參照）**：
① **整格刪除**——標的完全消失、留著只會誤導（`verify_roadmap_r6_s12` 之 A5；Steward 拍板）。
② **移除子判準**——主判準仍有效，但該子項移除後會**假綠**故不得留（`verify_evolution_acceptance` A9、
   `migrate_probability_ddl` A-28；根因＝`role_table_grants WHERE grantee='<不存在角色>'` 回 0 列而恆真）。
③ **改射程註記**——檢查本身仍有用，僅涵蓋範圍縮小（`verify_prodset_hotpath`）。

**另修一項既有缺陷（非本輪造成）**：`tests/test_release_lag_antileakage.py` 之 `_clean` 迴圈含
`feature_values`，遭 `fv_guard` 拒而拋例外 ⇒ `commit()` 到不了 ⇒ **前三張表已刪之列一併回滾**，
清理看似執行實則零效果，synthetic 列逐次累積於生產表（實證殘留 313 列）。已改為逐表獨立子交易
＋帶通行證＋失敗印警告；修後實測四張表零殘留。此為 r2 債 #27 之具體傷害實例。

**S9 之唯一機械紅燈及其處置**：`test_db_tombstone_controlled_erasure` 斷言
「應用角色被拒＝抹除不可自應用路徑達成」，`augur` 升 superuser 後恆 FAIL（DID NOT RAISE）。
Steward 拍板**丙案（刪除）**；已於原位留說明段記載刪除理由與「抹除函式仍為 SECURITY DEFINER、
但已無 DB 層角色阻擋」之事實，原內容見 git history。

**⚠ 順序偏離（誠實記錄）**：本計畫 §2 原排 S5→S11，實際依 Steward 指示**先執行 S11**。
未造成問題（三外部庫與 `augur_predict` 無關），惟本文件之順序敘述與實際不符，於此標明。

**S11 完成後之終態**：資料庫僅 `augur`＋`postgres`；角色僅 `augur`／`augur_predict`／`postgres`
（`stock` 之 superuser 隨角色刪除消失）。public **322** 表、`knowledge_unit` 142,040、
`feature_values` 8,540,331、五埠全通。

### 兩則執行教訓（同一病犯兩次，記錄以免再犯）

**L-1｜撞名檢查漏了索引／約束層。** 首次 S1+S2 交易因
`ERROR: relation "knowledge_source_pkey" already exists in schema "public"` 而**原子回滾**——
`ALTER TABLE … RENAME` **不改索引與約束名**。原檢查只掃 `pg_class`（表／view／seq）與 `pg_type`，
未掃 `relkind='i'` 與 `pg_constraint`。補上約束改名後成功。
**（單一 transaction 之設計在此發揮實效：16 表原封回滾、零損。）**

**L-2｜清點漏了 `pg_proc`，致 CASCADE 連帶刪除 2 個 trigger。**
`ttai_import.touch_updated_at()` 未隨表搬移（清點時未查函式），`DROP SCHEMA … CASCADE` 刪函式時
連帶刪除依賴它的 `trg_ku_touch@knowledge_unit`／`trg_vf_touch@value_flow`。
**損失**：1 函式＋2 trigger，作用僅 `NEW.updated_at = now()`；`GROUNDING-MAP:140` 原即載明其
**非憲章護欄**。Steward 裁示「可建可不建」。**定義留存如下**（`ttai` 庫刪除前擷取）：
```sql
CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS trigger LANGUAGE plpgsql
AS $$ BEGIN NEW.updated_at = now(); RETURN NEW; END $$;
CREATE TRIGGER trg_ku_touch BEFORE UPDATE ON public.knowledge_unit
  FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
CREATE TRIGGER trg_vf_touch BEFORE UPDATE ON public.value_flow
  FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
```

**共同根因**：遷移前之物件清點**憑印象列型別**，未使用明確之型別全集。
**改正**：schema 遷移之清點清單一律涵蓋 `pg_class`（r／v／m／S／**i**）、`pg_constraint`、
`pg_proc`、`pg_type`、`pg_trigger` 五類，缺一不可。

---

## §1 現況（全部唯讀親驗）

| 項 | 值 | 取得方式 |
|---|---|---|
| 角色 | `postgres`(super)／`stock`(**super**)／`augur`／`augur_predict`／`rdai`／`ttai` | `pg_roles` |
| 資料庫 | `augur` 60 GB／`ttai` 214 MB／`stock` 10 MB／`rdai` 7.6 MB | `pg_database_size` |
| **rdai 物件數** | **0** | `pg_class` 非系統 schema |
| **stock 物件數** | **0** | 同上 |
| ttai 內容 | `buffer` schema 16 表 | 同上 |
| **augur.ttai_import** | **16 表全在**，多數列數 ≥ ttai 側 | 逐表 `reltuples` |
| public → ttai_import | **零跨 schema FK、零 view 引用** | `pg_constraint`／`pg_views` |
| ERP 產物 | `owned_local` item_text **150,772**／`ttai_erp_pilot` items **141,873** | `knowledge_item_text`／`knowledge_item` |
| augur 缺 DELETE 之表 | **0**（無 ACL 型 append-only） | `has_table_privilege` |
| `augur_owner`／`augur_app` | **不存在**（HANDOFF §0.5 宣稱屬他機） | `pg_roles` |

---

## §2 分步行程

> **不可逆點以 🔒 標示。🔒 之前的每一步都可回退。**

| 步 | 動作 | 性質 | 執行主體 |
|---|---|---|---|
| **S1** | `ttai_import.knowledge_source` 改名（唯一撞名） | 可逆（改回即可） | AI |
| **S2** | 16 表＋11 seq＋6 view＋2 enum `SET SCHEMA public` | 可逆（再 SET 回去） | AI |
| **S3** | 併後驗收（§6.1）：逐表 `count(*)` 與 ttai 側精確比對 | 唯讀 | AI |
| **S4** | `DROP SCHEMA ttai_import`（此時應為空） | 可逆性：空 schema，無損 | AI |
| **S5** | 程式側移除 `augur_predict`（29 檔，已完成 1 檔） | 可逆（git revert） | AI |
| **S6** | 服務重啟＋五埠實測（#7） | 可逆 | AI |
| **S7** | qdrant unit 改指 `augur/.qdrant_server/qdrant`＋`install_services.sh:26` | 可逆 | AI |
| **S8** | 文件同步（§8） | 可逆 | AI 草擬／治權檔部分呈 Steward |
| **S9** 🔒 | `ALTER ROLE augur SUPERUSER` | 屬性可改回，**期間所生事實不可逆** | **Steward 親跑**（`L6.18(a)` 涉自身監督機制） |
| **S10** 🔒 | `DROP ROLE augur_predict` | **不可逆** | Steward 確認後 |
| **S11** 🔒 | `DROP DATABASE ttai / rdai / stock` ＋ `DROP ROLE` ×3 | **不可逆**（D-7：不 dump） | Steward 確認後 |

**S11 之前置條件（硬）**：S3 驗收全綠。**未過即不得進 S11**——這是 D-7（不 dump）下唯一的保護。

---

## §3 §4 對應 table schema（憲章 v1.39.0 強制節 a）

### 4.1 遷移標的（`ttai_import` → `public`）

**16 表**（列數為 `reltuples` 估計，S3 須改用精確 `count(*)`）：

| 表 | 列數(est) | 大小 | 撞名 |
|---|---|---|---|
| `knowledge_unit` | 142,040 | 122 MB | — |
| `knowledge_source` | 102,564 | 14 MB | **⚠ 撞** |
| `knowledge_relation` | 67,914 | 13 MB | — |
| `column_meta` | 39,563 | 6.0 MB | — |
| `knowledge_unit_lang` | 13,934 | 2.4 MB | — |
| `function_meta` | 5,348 | 1.2 MB | — |
| `buffer_embedding` | 3,482 | 1.0 MB | — |
| `sql_predicate` | 1,984 | 560 kB | — |
| `form_field` | 1,962 | 584 kB | — |
| `program_meta` | 874 | 296 kB | — |
| `code_value` | 390 | 192 kB | — |
| `field_reference` | 121 | 96 kB | — |
| `extraction_run` | 74 | 64 kB | — |
| `value_flow` | 41 | 168 kB | — |
| `relation_type` | 17 | 32 kB | — |
| `erp_system` | 1 | 48 kB | — |

**11 sequence**：`buffer_embedding_id_seq`／`code_value_id_seq`／`erp_system_id_seq`／`extraction_run_id_seq`／
`field_reference_id_seq`／`form_field_id_seq`／`knowledge_relation_id_seq`／`knowledge_source_id_seq`／
`knowledge_unit_id_seq`／`sql_predicate_id_seq`／`value_flow_id_seq`
（owned sequence 隨 `ALTER TABLE … SET SCHEMA` 自動移動，**S2 仍須逐一驗證**）

**6 view**：`v_coverage`／`v_detail_coverage`／`v_embeddings_stale`／`v_qdrant_export`／
`v_units_without_source`／`v_value_flow_unsourced`（**零撞名**）

**2 enum type**：`src_kind`／`unit_state`（**零撞名**）

**2 trigger**：`trg_ku_touch@knowledge_unit`／`trg_vf_touch@value_flow`（僅 touch `updated_at`，
`GROUNDING-MAP:140` 已誠實揭露其**非憲章護欄**；隨表移動）

### 4.2 唯一撞名之處置

| | augur.public.knowledge_source | ttai_import.knowledge_source |
|---|---|---|
| 列數 | 3,605（active 97） | 102,564 |
| 角色 | **知識管線承重表**（`knowledge_item.source_key` FK 指向它；`chk_ks_active_needs_approval` 人簽閘在其上） | ERP buffer 之來源表 |

**⇒ 必須改名的是 ttai_import 側**（public 側動不得）。

**該表之實際語意（親驗，非推測）**：欄位＝`id`／`knowledge_unit_id`(FK→`knowledge_unit`)／
`source_kind`／`source_ref`／`excerpt`／`run_id`(FK→`extraction_run`)／`created_at`；
樣本 `source_ref` 形如 `ds.gap_file × ds.gbd_file(gbd02=standard): make_menu`。
⇒ 它**不是來源登錄簿**（那是 public 側那張），而是**逐單元之出處紀錄**——
每列＝某個 `knowledge_unit` 的一個出處。

**新名：`knowledge_unit_source`**（S15 定案依據）
- 精確描述關係（單元 ↔ 其出處），符合 `#18`「`package.module` 讀起來＝做什麼」「一看就懂」；
- **與同批既有之 `knowledge_unit_lang` 同構**——不引入新慣例、不新增前綴，沿用該組兄弟表之既有命名先例；
- 與 public 側 `knowledge_source`（來源登錄簿）語意上明確可分，日後不致再混淆。

**連帶**：`pg_type` 之 `knowledge_source`（隱含 row type）與 `_knowledge_source`（陣列 type）
隨 `ALTER TABLE … RENAME` **自動更名**，無須另行處理。
其 FK 約束名（`knowledge_source_run_id_fkey`／`knowledge_source_knowledge_unit_id_fkey`）
**不隨表名自動更名**——是否一併更名為 `knowledge_unit_source_*_fkey` 屬美觀非功能，列為 S2 之可選項。

### 4.3 命名慣例（**S16 已定案：不加前綴**）

**Steward 拍板（2026-07-31 晚）**：「不要另外再 erp，因為都是此專案的通用資料」
⇒ **16 表除撞名者外一律保留原名**，不加 `erp_`／`ttai_` 等任何前綴。

**併此記錄之事實（供日後參照，非異議）**：下列名稱在 `CLAUDE #18` 之字面判準下屬「通用角色名」
——`column_meta`／`function_meta`／`program_meta`／`form_field`／`field_reference`／`value_flow`／
`code_value`／`relation_type`／`extraction_run`／`buffer_embedding`。
Steward 已認定此批為「本專案之通用資料」，故 `#18` 之「別的領域會搶這名」該當性不成立。
**未來若新增同名需求，須以本節為先例查核。**（repo 現對這些表名**零引用**，故本次無同步成本。）

### 4.4 併入後 public 之變化

| 項 | 併前 | 併後 |
|---|---|---|
| public 基表數 | **306** | **322** |
| public view 數 | 3 | 9 |
| public enum 型別 | — | ＋2 |
| public 非內部 trigger | 95 | ＋2（97） |
| **含 `confidence` 欄之 public 表** | **0** | **2 表＋1 view**（`knowledge_unit.confidence`／`value_flow.confidence`／`v_units_without_source.confidence`） |

**⚠ 治權後果（§8.1 詳述）**：末列使 `GROUNDING-MAP.md:86` 之 KS.20-24 宣稱逐字不實。

### 4.5 本計畫不新建任何表

（D5 告警帳本、KH0 進度帳、殭屍回填帳等新表屬他案；Steward 已授權「計畫書可建新表」，
但本計畫射程不含之，避免與整併混同。）

---

## §5 對應 python 程式規畫（憲章 v1.39.0 強制節 b）

### 5.1 已完成（本 session，可 revert）

| 檔:行 | 改動 | 驗收 |
|---|---|---|
| `scripts/predict_asof.py:154` | `db.connect_predict()` → `db.connect()`＋三行說明註解 | 無參數 rc=0、零殘留 ✓ |
| `.gitignore` | 新增 `/.qdrant_server/`（根限定） | `git check-ignore` ✓ |

### 5.2 待改（S5；29 檔扣除已完成 1 檔）

**A. src（2 檔）**
| 檔:行 | 現況 | 改法 |
|---|---|---|
| `src/augur/core/db.py:43-46` | `connect_predict()` | 移除 |
| `:73-79` | `ping_predict()` | 移除 |
| `:4／:7／:10／:11` | docstring 述 predict 通道 | 改寫為單一角色 |
| `:91／:94／:97-98／:103-104` | 四條自測 `chk` | 移除 |
| `src/augur/core/config.py:49-57` | `DB_PARAMS_PREDICT` | 移除 |
| `:88-94` | 四條自測 `chk` | 移除 |

**B. scripts（功能依賴）**
| 檔:行 | 現況 | 改法 |
|---|---|---|
| `scripts/verify_roadmap_r6_s12.py:155-175` | `_a5()` 整段以 `augur_predict` 為判準（`role_ok`／`sess_ok`／素養表 SELECT 抽樣） | **【待 Steward·S17】** 該檢查失去標的：(i) 移除 A5 項並於報表誠實標「DB 層隔離已退役」／(ii) 改為驗 AST 稽核 |
| `scripts/setup_predict_role.py` 全檔 | 建 role＋GRANT／REVOKE（含 :205-208 對 `ttai_import` 之 REVOKE） | **【待 Steward·S18】** (i) 整支退役／(ii) 改 graceful 說明並保留矩陣（#29(d)） |

**C. `migrate_*.py` 之 GRANT（9 檔）**
`migrate_prediction_ddl`／`migrate_probability_ddl`／`migrate_raw_supersede_ddl`／
`migrate_revalidation_baseline_ddl`／`migrate_revalidation_ledger_ddl`／`migrate_risk_policy_ddl`／
`migrate_trial_ledger_ddl`／`migrate_unfreeze_gate_ddl`／`migrate_validation_evidence_ddl`
——移除對 `augur_predict` 之 GRANT 語句。
**⚠ 回退風險**：此步移除後，**重建 `augur_predict` 之能力隨之消失**（`setup_predict_role.py` 若依賴這些 GRANT 定義）。
**⇒ 若欲保留回退可能，C 應排在 S10 之後而非之前。** 本計畫排在 S5 內，Steward 得指示調整。

**D. 其餘引用（11 檔）**：`bridge_deliberation_distill`／`preregister_unfreeze_gate`／`revalidate`／
`revalidate_baseline`／`run_model_robustness`／`survivorship_economic_verdict`／
`verify_evolution_acceptance`／`verify_prodset_hotpath`／`verify_roadmap_r7_gate`／
`verify_validation_evidence`／`import_database.sh`（`setup_predict_role` 呼叫）
——逐檔判別「功能依賴」vs「字串／註解」，前者改、後者更新描述。

**E. 測試**
| 檔 | 現況 | 處置 |
|---|---|---|
| `tests/test_predict_role_isolation.py` | 5 測全 passed；`:43` role 未建即 `pytest.skip` | **【待 Steward·S19】** **不得只留著讓它 skip**（會由 5 passed 變 5 skipped、RC=0 綠燈，掩蓋「這層防線已不存在」）。(i) 刪除並於 `tests/` 留說明／(ii) 改寫為驗「AST 稽核為唯一防線」 |

**F. qdrant（S7）**
| 檔:行 | 改法 |
|---|---|
| `~/.config/systemd/user/augur-qdrant.service:12` | `ExecStart=/home/hugo/project/augur/.qdrant_server/qdrant` |
| `install_services.sh:26` | `QDRANT_BIN="${QDRANT_BIN:-$ROOT/.qdrant_server/qdrant}"` |

**G. `.env`（人工，AI 不動）**：`DB_PREDICT_PASSWORD`（:80）移除；
`ORACLE_*` 五鍵（:60-66）——其工具已隨 ttai 目錄消失，**【待 Steward·S20】** 保留或移除。

---

## §6 驗收（唯讀、可重跑；每條須能回答「壞了會不會安靜變綠」）

### 6.1 S3 合併驗收（**S11 之硬前置**）

```bash
# 逐表精確比對（非 reltuples）——16 表逐一，任一不符即中止
cd /home/hugo/project/augur && set -a && . ./.env && set +a
for t in knowledge_unit knowledge_source knowledge_relation column_meta knowledge_unit_lang \
         function_meta buffer_embedding sql_predicate form_field program_meta code_value \
         field_reference extraction_run value_flow relation_type erp_system; do
  a=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc \
      "SELECT count(*) FROM public.$t" 2>/dev/null)
  b=$(PGPASSWORD="$DB_SUPERUSER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER_USER" -d ttai -tAc \
      "SELECT count(*) FROM buffer.$t" 2>/dev/null)
  printf '%-24s augur=%-8s ttai=%-8s %s\n' "$t" "$a" "$b" "$([ "$a" -ge "$b" ] 2>/dev/null && echo OK || echo '⚠ CHECK')"
done
```
**通過條件**：16 表 `augur ≥ ttai`（augur 側為較新副本，允許多）。任一 `⚠` 即**不得進 S11**。
（`knowledge_source` 比對時用改名後之新名。）

```sql
-- ttai_import 應已清空
SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='ttai_import';
-- 期望 0
-- public 物件數
SELECT relkind, count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND relkind IN ('r','v','S') GROUP BY 1;
-- 期望 r=322, v=9
```

### 6.2 S5 程式側驗收

```bash
# 行為級：模組載入後不得再有 predict 通道（非 grep，驗真實屬性）
venv/bin/python -c "
from augur.core import db, config
assert not hasattr(db,'connect_predict'), 'connect_predict 殘留'
assert not hasattr(db,'ping_predict'), 'ping_predict 殘留'
assert not hasattr(config,'DB_PARAMS_PREDICT'), 'DB_PARAMS_PREDICT 殘留'
print('✓ predict 通道已完全退役')"
venv/bin/python -m augur.core.db --selftest; echo "rc=$?"      # 期望 0
venv/bin/python -m augur.core.config --selftest; echo "rc=$?"  # 期望 0
venv/bin/python scripts/check_cmd_matrix.py; echo "rc=$?"      # 期望 0
venv/bin/python -m pytest tests/ -q 2>&1 | tail -3             # 注意 skip 數（見 S19）
```

### 6.3 S6 服務驗收（#7；防孤兒佔埠假綠）

```bash
systemctl --user restart augur-advisor augur-chat augur-admin augur-probability
for p in 8090 8500 8399 8600 11434 6333; do
  curl -s -o /dev/null -w "$p:%{http_code}\n" --max-time 8 http://127.0.0.1:$p/; done
# 8399 對 / 回 404 屬正常，驗 /v1/models 應 200
ss -tlnp | grep -E ':(8090|8500|8399|8600|6333)'   # 取 pid
# → ps -o lstart,cmd -p <pid>：啟動路徑須為絕對路徑、時刻須晚於改動
```

### 6.4 整體健康（每日可跑）

```bash
cd /home/hugo/project/augur && venv/bin/python scripts/check_treaty_refs.py; \
venv/bin/python scripts/check_cmd_matrix.py; \
psql -tAc "SELECT 'roles', string_agg(rolname,',') FROM pg_roles WHERE rolname NOT LIKE 'pg\_%'
           UNION ALL SELECT 'dbs', string_agg(datname,',') FROM pg_database WHERE NOT datistemplate"
```

---

## §7 不可逆點與中止設計

| 步 | 若失敗，系統停在什麼狀態 | 是否一致 |
|---|---|---|
| S1–S2 | 部分表已 `SET SCHEMA`、部分仍在 ttai_import | **不一致**——須在**單一 transaction** 內完成全部 `SET SCHEMA`（PostgreSQL 之 DDL 可交易） |
| S3 | 唯讀，無狀態 | — |
| S4 | schema 未刪，無害 | 一致 |
| S5 | 部分檔改、部分未改 | **不一致**——但 `augur_predict` 仍在，功能不斷；可 git revert |
| S9 🔒 | superuser 已授予 | 一致（可 `NOSUPERUSER` 改回） |
| S10 🔒 | role 已刪 | **若 S5 之 C 組已移除 GRANT，重建能力已失** |
| S11 🔒 | 庫已刪、無 dump | **無回退**——故 6.1 為硬前置 |

**建議之保護**：S2 全部 `SET SCHEMA` 包在一個 transaction；S11 前人工複讀 6.1 輸出。

---

## §8 文件與治權同步

### 8.1 ⚠ `GROUNDING-MAP.md:86` 之 KS.20-24 宣稱將逐字不實

現行逐字：「public schema（236 表）**零** confidence 欄；僅 `ttai_import` 遺留二欄（$S L11850/L12014）＋一 view（L12149）」，
狀態標 🔨（未閉）。**併入 public 後，那三處 confidence 欄將位於 public**
⇒ 該句由「僅 ttai_import 遺留」變為「public 內有」，**宣稱不實且 🔨 之描述須重寫**。

**【待 Steward·S21】** 此為 MC §P4.E1／KS.20-24（**不可豁免核心**）之合規陳述。處置選項（並列，不推薦）：
(i) 更新 `GROUNDING-MAP` 陳述並說明該三欄屬 ERP staging、非 Knowledge 五元組之 confidence；
(ii) 併入時同步移除／改名該三欄；
(iii) 維持 ttai_import 為獨立 schema（與 D-6 相反）。

### 8.2 `GROUNDING-MAP.md:140`

「12 條中 2 條（`trg_ku_touch`／`trg_vf_touch`@ttai_import）僅 touch updated_at，非憲章護欄」
——併入後位置改為 `@public`，句子須更新（**非護欄之事實不變**）。

### 8.3 `HANDOFF.md` 須改處

§0.5 owner 分離段（宣稱與本機不符，且隨 D-2 失去意義）／§2 新機 setup 序（`setup_predict_role` 步驟）／
§3 `.env` 表之 `DB_PREDICT_PASSWORD`／`ORACLE_*` 列／§3 dump 位置（三庫刪除後）／
重開機檢查節第 3 點「qdrant 二進位在 `~/project/ttai/`（跨專案依賴）」——**已不成立，須改**。

### 8.4 WM.35 消費閘之證據

`GROUNDING-MAP:176` 以「十新表對 `augur_predict` SELECT 全拒」為 WM.35 已達之證據。
角色移除後該證據消失。**【待 Steward·S22】** 新架構下 WM.35 以何為證。
（WM.35／36 屬 2026-10-14 到期義務；`RULING-2026-030` 第五(b)：自 10-15 起消費禁令無條件適用。）

### 8.5 治權四檔

靈魂／原則精華／大憲章／CLAUDE 對 `augur_predict` **零命中**，本計畫不使其失真。
`docs/模擬方法自進化專章_v1.0.md:99` 之 `pg_roles` 快照屬**史述**，依大憲章 v1.51.0 通則一**不改**。

### 8.6 r2 報告與行程計畫中將過期之條目

債 #40（qdrant 跨專案依賴）→ S7 後解除；P2-1（隔離不可動）→ 已由 D-1 取代；
D13 §6.5 之「29 檔」→ 已完成 1 檔；`GROUNDING-MAP:86` 之 🔨 → 見 8.1。

---

## §9 待 Steward 之點（S15–S22）

| # | 事項 | 阻塞 |
|---|---|---|
| ~~S15~~ | ~~`ttai_import.knowledge_source` 之新名~~ → **已定案：`knowledge_unit_source`**（§4.2；沿 `knowledge_unit_lang` 之既有先例） | — |
| ~~S16~~ | ~~16 表是否加前綴~~ → **已定案：不加**（Steward 2026-07-31 晚「都是此專案的通用資料」；§4.3） | — |
| **S17** | `verify_roadmap_r6_s12._a5()` 之處置 | S5 |
| **S18** | `setup_predict_role.py` 退役形式 | S5 |
| **S19** | `test_predict_role_isolation.py` 之處置（**不得留著讓它 skip**） | S5 |
| **S20** | `.env` 之 `ORACLE_*` 五鍵去留 | — |
| **S21** | `GROUNDING-MAP:86` KS.20-24 合規陳述之處置 | S2（併入即發生） |
| **S22** | WM.35 消費閘之新證據 | 2026-10-14 |

---

## §10 未知與風險

| # | 內容 |
|---|---|
| U1 | `buffer_embedding` 為唯一 ttai 側 est 較多者（3,804 vs 3,482）——S3 須以精確 `count(*)` 確認；若 ttai 側確實較多，該差額在 D-7（不 dump）下將消失 |
| U2 | `setup_predict_role.py` 之 GRANT 集合是否完全獨立於 9 支 `migrate_*`（決定 S10 後之回退可能性） |
| U3 | 6 個 view 之定義是否含跨 schema 硬編引用（`SET SCHEMA` 後應自動跟隨，S2 須驗） |
| U4 | superuser 相對 owner 新增之能力清單（`COPY FROM PROGRAM`／event trigger／`pg_read_server_files` 等）——D13 §6.3 已列部分，未窮盡 |

~~**最大風險**：D-7（不 dump）使 §6.1 成為唯一保護。**S3 未全綠而進 S11 ＝ 資料永久消失且無任何復原路徑。**~~

**【2026-07-31 晚更正——原判過度悲觀】** 事後查得本日 **09:20:38 已存在一份完整 dump**，當時無人（含 Steward 與繕打者）在決策 D-7 時提及、繕打者亦未查：
`/mnt/c/database/augur_pgdump_20260731_Fd`（11 GB、2,748 物件、`pg_restore -l` 可解析、含 `ttai_import` **151 物件**、`touch_updated_at()` 與 `trg_ku_touch`／`trg_vf_touch` 三者俱在）。
⇒ 本輪一切不可逆操作（S4／S10／S11）之**前狀態實際有備份**，D-7「不 dump」之風險遠低於原估。
**惟同日稍晚 Steward 清空 `~/db_dumps/`（原五份 dump 全刪）**，故 C 碟那一份現為**唯一備份**——HANDOFF §3 已同步更正為以其為 SSOT。
**教訓**：`#15` 之「以實證非我以為」對**風險陳述**同樣適用——繕打者寫「無任何復原路徑」時**未跑 `ls ~/db_dumps/` 與 `/mnt/c/database/`**，僅依 D-7 之字面推論。誇大風險與低估風險同為失準。
