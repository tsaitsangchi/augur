# [DRAFT 呈案] B4｜P0 四表升級 honesty_ledger_guard（UPDATE-GUC）——翻 C5 裁決一部

> **[DRAFT 呈案] 未經拍板不得施作。**
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草；所涉之閘約束的表正是記錄 AI 引擎產出與判決之表（含引擎自身為寫入者之表），且通行證補丁將由 AI 寫入引擎程式——故本案建議一律附機械可判驗收與證偽條件，不以「相信起草者」為據。
> 日期：2026-08-01（親驗均為本日執行時現查）。設計 SSOT＝`reports/augur_problem_solution_register_20260801.md` §3 B4＋`reports/augur_steward_adjudication_sheet_20260801.md` B4 條。

---

## §1 問題與授權鏈

**問題**：r2 深化理解（`reports/augur_deep_understanding_r2_20260731.md:88` 債 #4，判定「惡化」）——`honesty_delete_only_guard` 覆蓋 23 表 46 trigger，但 `tgtype&16` 命中 0＝**UPDATE 面 100% 全裸**；一句裸 psql UPDATE 即可默改晉升鏈判準欄（方向、verdict、set_status、status），零留痕（#15 默改面）。07-31 單一角色整併後 **DB 層 role 隔離已不存在**（唯 `augur` superuser 一角；`src/augur/core/db.py:18-19` 自陳），trigger＋GUC 係 DB 層僅存的機械屏障。

**解法登錄**（登錄冊 §3 B4）：P0 四表升級 `honesty_ledger_guard`（UPDATE 須 GUC 通行證）；DDL 帶 `SET lock_timeout='5s'` 絕不排隊；其餘表列 P2 分批。統一 DDL 窗（3c）執行。

**建議案**（裁決呈案單 B4 條）：P0 先四表——`principle_factor_map`（符號尺方向基準）、`philosophy_principle`、`evolution_production_feature_set`、`feature_sign_check`。
**證偽條件**（原文）：若 GUC 閘使正常晉升路徑報錯（漏帶通行證的合法寫入者），縮射程。

**授權鏈**：
- 本呈案＝W2 呈案批之一路（範圍：唯讀親驗＋寫 scratchpad 呈案；結束條件：文件交付；所繫任務＝登錄冊 B4，波次 W2「呈案（翻 C5 一部）→裁」）。
- **翻 C5 裁決一部＝治權判準變更＝Steward 專屬**（`AUGUR-MC v1.6 §8.1`／`AUGUR-L6 v1.2` L6.18(a)）；AI 於此僅得草擬、比對與呈案。
- 拍板後之 DDL 施作與寫入者補丁＝執行層，於統一 DDL 窗（登錄冊 3c）進行；施作後驗收報告回呈。

### 翻 C5 一部之治權說明

**C5 原裁決**（SSOT＝`reports/augur_self_evolution_master_plan_v2_20260726.md:268-271`「C5 誠實閘：只做 DELETE/TRUNCATE 拒，不做 UPDATE-GUC」；2026-07-26 hugo 拍板 V2-HONESTY-go；工具層落地註記＝`scripts/migrate_honesty_guards_ddl.py:6-10` 與 selftest `:117-125`）。三條理由與本案逐條回應：

| C5 理由（07-26） | 本案回應（08-01） |
|---|---|
| ① GUC 對唯一自動寫入者豁免（apply 引擎自行 `SET LOCAL`）＝閘只擋人不擋引擎，對真正威脅豁免 | **承認且不推翻其真值**：升級後對引擎仍非安全邊界（引擎自帶通行證）。但前提已變——07-26 時 DB 尚有 role 層縱深（`augur_predict` 受限角色）；07-31 整併後唯 superuser 一角，**「擋裸手」本身成為僅存的 DB 層價值**：默改需顯式咒語＝意圖留痕、repo/psql history 可稽；且防手滑（漏 WHERE 之全表 UPDATE）。誠實分類：此為**半閘非硬閘**（三層強度語彙），本案不得被引為「P4.E3 已對 PME 機械落地」之完整宣稱——C5 對此的警告全數保留。 |
| ② prodset 走 `ON CONFLICT (feature) DO UPDATE`，guard 僅在衝突分支觸發→首次 APPLY 過（INSERT）、再次 APPLY 死（UPDATE），單次測試驗不出 | 以**次序**消滅：寫入者通行證補丁**先合入**（無 trigger 時 `SET LOCAL` 任意 GUC 無害），DDL 才上；驗收含**對既有列之 UPDATE 探針**（直接打衝突分支等價路徑，非只測首插）。且現況 I5 於 cron 為 dormant（`run_evolution_iteration.py:235-237`：無 `--allow-apply` 即 skip），APPLY-go 未開前無自動寫入者會踩空窗。 |
| ③ 要管 UPDATE 走「追加修訂列＋superseded_by」，不走 GUC | **對 append-only 帳本群仍為正解、本案不翻**：iteration ledgers 等 P2 群維持 C5 原則。本案四表為 **current-state registry**（PK＝feature／map_id／principle_id，8+ 既有寫入者皆 in-place 更新語意）；改追加修訂列＝schema 重構＋全部寫入者與讀者改寫，與風險不成比例。**C5 對其餘 delete-only 表（升級後餘 20 表）之效力不變。** |

**判死留檔（CLAUDE #32(c)）**：C5 裁決文字**不刪不改**；`migrate_honesty_guards_ddl.py` 之 C5 註記改為「C5（07-26）＋B4 部分翻案（RULING 編號＝Steward 定）」並存，總控計畫 v2 §C5 原文不動（史料）。

---

## §2 現況親驗（2026-08-01 執行時現查；配方＝`.env` 唯讀 psql）

### 2.1 四表 trigger 現況

```sql
SELECT c.relname, t.tgname, p.proname,
       (t.tgtype::int & 16)>0 AS upd, (t.tgtype::int & 8)>0 AS del,
       (t.tgtype::int & 4)>0 AS ins, (t.tgtype::int & 32)>0 AS trunc
FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_proc p ON p.oid=t.tgfoid
WHERE NOT t.tgisinternal AND c.relname IN ('principle_factor_map','philosophy_principle',
  'evolution_production_feature_set','feature_sign_check') ORDER BY 1,2;
```

```
evolution_production_feature_set | trg_..._delonly_row   | honesty_delete_only_guard | upd=f del=t
evolution_production_feature_set | trg_..._delonly_trunc | honesty_delete_only_guard | trunc=t
philosophy_principle             | trg_..._delonly_row   | honesty_delete_only_guard | upd=f del=t
philosophy_principle             | trg_..._delonly_trunc | honesty_delete_only_guard | trunc=t
principle_factor_map             | trg_..._delonly_row   | honesty_delete_only_guard | upd=f del=t
principle_factor_map             | trg_..._delonly_trunc | honesty_delete_only_guard | trunc=t
(6 rows)
```

**⚠ 與登錄冊不符（明標一）**：`feature_sign_check` **零 trigger**（連 delete-only 都沒有——07-31 A1 前才建表，未入任何 guard 名單）。故本案實為「**3 表升級＋1 表新掛**」，非「四表升級」。

### 2.2 guard 函式與 GUC 名（live prosrc 親讀）

```sql
SELECT prosrc FROM pg_proc WHERE proname='honesty_ledger_guard';
```
live 函式體：DELETE/TRUNCATE 無條件 RAISE；`IF TG_OP='UPDATE' AND coalesce(current_setting('augur.honesty_write', true),'') <> 'on'` 則 RAISE。
**GUC 名確認＝`augur.honesty_write`**，通行證＝`SET LOCAL augur.honesty_write='on'`（與 repo `scripts/migrate_honesty_guards_ddl.py:30,38` 一致，零漂移）。函式已存在於庫內、本案 DDL **不建不改函式**。

### 2.3 兩 guard 全庫覆蓋面

```sql
SELECT p.proname, count(DISTINCT c.relname) AS n_tables, count(*) AS n_triggers, string_agg(...)
FROM pg_trigger t JOIN pg_class c ... WHERE p.proname IN ('honesty_delete_only_guard','honesty_ledger_guard') GROUP BY 1;
```

- `honesty_delete_only_guard`：**23 表 46 trigger**（evolution_apply_log, evolution_coverage_snapshot, evolution_evidence_run, evolution_hypothesis_hint, evolution_iteration_ledger, evolution_kill_switch, **evolution_production_feature_set**, evolution_run, local_ai_iteration_ledger, mc_simulation_run, **philosophy_principle**, **principle_factor_map**, promotion_queue, raw_evolution_iteration_ledger, sim_calibration_eval, sim_evolution_candidate, sim_evolution_iteration_ledger, sim_evolution_verdict, sim_llm_proposal, sim_realized_outcome, sim_run_link, simulation_method_registry, steward_question_ledger）——與 r2 債 #4 數字相符。
- `honesty_ledger_guard`（UPDATE-GUC 正解）：**5 表 9 trigger**——local_model_eval_item、local_model_eval_run、revalidation_baseline、trial_ledger（各 row+trunc 雙 trigger）＋ **sim_evolution_verdict**（`sev_no_update` 單 UPDATE trigger，與其 delonly 雙 trigger 並掛）。

**明標二**：r2「23 表 UPDATE 100% 全裸」對 `sim_evolution_verdict` 不成立——其 delonly 雙 trigger 確無 UPDATE 位元，但另有第三支 `sev_no_update`（honesty_ledger_guard）補上 UPDATE 閘。**真裸＝22 表**。
**明標三**：升級 3 表後 delete-only 殘餘＝**20 表**（23−3），非登錄冊「其餘 19 表列 P2」——差 1 係因 `feature_sign_check` 本就不在 23 表內。P2 待辦清單應以 20 表計（其中 sim_evolution_verdict 實質已閉，真待辦 19 表——登錄冊數字歪打正著但推導錯誤，留此更正）。

### 2.4 四表內容量（升級標的之份量）

```
principle_factor_map             111 列   ← 符號尺方向基準（見 2.5）
philosophy_principle              54 列   （untested 46／sign_refuted 7／validated 1）
evolution_production_feature_set   9 列   （active 2／removed 7）＝生產熱路徑 prodset_contract 之 SSOT
feature_sign_check                 4 列   （見 2.5）
```

### 2.5 A1 落帳現況（今日新事實之親驗）

```sql
SELECT check_id, feature, h, verdict, direction_source FROM feature_sign_check ORDER BY check_id;
```
```
1 | inst_cumflow_position_120d | 20 | PASS | principle_factor_map
2 | inst_cumflow_position_120d | 60 | PASS | principle_factor_map
3 | lending_fee_rate_mean_20d  | 20 | PASS | principle_factor_map
4 | lending_fee_rate_mean_20d  | 60 | PASS | principle_factor_map
```
恰 4 列、兩現役符號全 PASS（mean_20d 亦 PASS）——與任務簡報一致。`direction_source='principle_factor_map'` 機械證實：**pfm 的 direction 欄就是符號尺的方向基準**，pfm 裸 UPDATE＝符號證據鏈上游可默改；fsc 裸 UPDATE＝verdict 本身可默改。此即 P0 選表依據。

### 2.6 既有通行證先例（repo 親查）

`SET LOCAL augur.honesty_write = 'on'` 現役用點：`scripts/revalidate.py:289`、`scripts/revalidate_baseline.py:108`、`scripts/migrate_trial_ledger_ddl.py:130`、`src/augur/features/panel.py:175`（fv_guard 同 GUC）。**模式已確立**：交易起點一行 `SET LOCAL`，本案寫入者補丁照抄同款。

---

## §3 方案

### 3.1 DDL 全文（每表獨立交易＋`SET LOCAL lock_timeout='5s'`；冪等可重跑）

前置檢查（施作窗開始時跑；任一不符即不動）：

```sql
-- P0：函式必須已在（本 DDL 不建函式）
SELECT count(*)=1 AS fn_ok FROM pg_proc WHERE proname='honesty_ledger_guard';
-- P1：無長交易在跑（#30 鎖風暴教訓：等待中的 EXCLUSIVE 會擋住全庫）；pg_dump 進行中一律不施作
SELECT pid, state, wait_event_type, now()-xact_start AS xact_age, left(query,80) AS q
FROM pg_stat_activity WHERE datname='augur' AND state<>'idle' ORDER BY xact_age DESC NULLS LAST;
```

```sql
-- ============ 表 1/4：principle_factor_map（獨立交易） ============
BEGIN;
SET LOCAL lock_timeout = '5s';
DROP TRIGGER IF EXISTS trg_principle_factor_map_delonly_row   ON principle_factor_map;
DROP TRIGGER IF EXISTS trg_principle_factor_map_delonly_trunc ON principle_factor_map;
DROP TRIGGER IF EXISTS trg_principle_factor_map_honesty_row   ON principle_factor_map;   -- 冪等重跑保護
DROP TRIGGER IF EXISTS trg_principle_factor_map_honesty_trunc ON principle_factor_map;
CREATE TRIGGER trg_principle_factor_map_honesty_row
    BEFORE UPDATE OR DELETE ON principle_factor_map
    FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
CREATE TRIGGER trg_principle_factor_map_honesty_trunc
    BEFORE TRUNCATE ON principle_factor_map
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();
COMMIT;

-- ============ 表 2/4：philosophy_principle（獨立交易） ============
BEGIN;
SET LOCAL lock_timeout = '5s';
DROP TRIGGER IF EXISTS trg_philosophy_principle_delonly_row   ON philosophy_principle;
DROP TRIGGER IF EXISTS trg_philosophy_principle_delonly_trunc ON philosophy_principle;
DROP TRIGGER IF EXISTS trg_philosophy_principle_honesty_row   ON philosophy_principle;
DROP TRIGGER IF EXISTS trg_philosophy_principle_honesty_trunc ON philosophy_principle;
CREATE TRIGGER trg_philosophy_principle_honesty_row
    BEFORE UPDATE OR DELETE ON philosophy_principle
    FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
CREATE TRIGGER trg_philosophy_principle_honesty_trunc
    BEFORE TRUNCATE ON philosophy_principle
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();
COMMIT;

-- ============ 表 3/4：evolution_production_feature_set（獨立交易） ============
BEGIN;
SET LOCAL lock_timeout = '5s';
DROP TRIGGER IF EXISTS trg_evolution_production_feature_set_delonly_row   ON evolution_production_feature_set;
DROP TRIGGER IF EXISTS trg_evolution_production_feature_set_delonly_trunc ON evolution_production_feature_set;
DROP TRIGGER IF EXISTS trg_evolution_production_feature_set_honesty_row   ON evolution_production_feature_set;
DROP TRIGGER IF EXISTS trg_evolution_production_feature_set_honesty_trunc ON evolution_production_feature_set;
CREATE TRIGGER trg_evolution_production_feature_set_honesty_row
    BEFORE UPDATE OR DELETE ON evolution_production_feature_set
    FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
CREATE TRIGGER trg_evolution_production_feature_set_honesty_trunc
    BEFORE TRUNCATE ON evolution_production_feature_set
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();
COMMIT;

-- ============ 表 4/4：feature_sign_check（新掛，非升級；獨立交易） ============
BEGIN;
SET LOCAL lock_timeout = '5s';
DROP TRIGGER IF EXISTS trg_feature_sign_check_honesty_row   ON feature_sign_check;
DROP TRIGGER IF EXISTS trg_feature_sign_check_honesty_trunc ON feature_sign_check;
CREATE TRIGGER trg_feature_sign_check_honesty_row
    BEFORE UPDATE OR DELETE ON feature_sign_check
    FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
CREATE TRIGGER trg_feature_sign_check_honesty_trunc
    BEFORE TRUNCATE ON feature_sign_check
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();
COMMIT;
```

設計註記：(a) DROP＋CREATE 同交易＝原子換閘、無無閘空窗；(b) `lock_timeout` 用 `SET LOCAL`（交易域、不外洩）——5 秒拿不到鎖即 abort 不排隊（07-03 鎖風暴教訓：排隊中的 ACCESS EXCLUSIVE 請求會擋住全庫後續查詢）；(c) trigger 命名循 trial_ledger 現役慣例 `trg_<tbl>_honesty_row/_trunc`；(d) INSERT 面刻意不設事件——append＝合法路（與五表現役 honesty_ledger_guard 一致；「簽核 gate trigger 不含 INSERT」之 r2 已知殘留不在本案射程）。

### 3.2 閘住所收斂（#12）——`scripts/migrate_honesty_guards_ddl.py` diff 計畫

上述 psql 全文為施作窗用；**閘的長期住所仍收斂回 migrate script**（同 commit 落地，防 live-vs-repo drift——件A 教訓）：

| 位置 | 現文 | 改為 |
|---|---|---|
| `:6-10` docstring | C5 裁決註記 | 保留 C5 原文＋追加一段：「B4 部分翻案（2026-08-0X RULING-＿＿）：pfm／pp／prodset／feature_sign_check 四表升 UPDATE-GUC；C5 對其餘 delete-only 表效力不變」 |
| `:24` `TABLES` | `("trial_ledger","revalidation_baseline")` | 不動；新增 `GUC_TABLES_P0 = ("principle_factor_map","philosophy_principle","evolution_production_feature_set","feature_sign_check")` |
| `:27-29` `PME_TABLES` | 8 表含 pfm/pp/prodset | 移除三表（餘 5：evolution_run, evolution_coverage_snapshot, promotion_queue, evolution_apply_log, evolution_kill_switch）＋註記遷出依據 |
| `_trigger_sql()`（:55-63） | 只 DROP honesty 名 | 新增 `_upgrade_sql(tbl)`：先 DROP delonly 雙名再 DROP/CREATE honesty 雙名（=§3.1 每表內容） |
| `apply()`（:90-99） | 單一大交易 | GUC_TABLES_P0 改**逐表獨立交易**且交易內先 `SET LOCAL lock_timeout='5s'`；TABLES/PME_TABLES 沿用原路 |
| `selftest()`（:117-125） | 「PME 八表全覆蓋」`len(PME_TABLES)==8`；C5 斷言 | 改 `==5`；C5 斷言保留並加 B4 註記；新增 GUC_TABLES_P0 四表斷言：upgrade SQL 含 delonly DROP＋`BEFORE UPDATE OR DELETE`＋`honesty_ledger_guard`＋`lock_timeout`（新斷言先驗紅：暫時改壞常數確認會 FAIL 再復原——F5 三規則） |

### 3.3 寫入者盤點與逐檔 diff 計畫（apply 後須帶通行證者）

全 repo 掃描（scripts/ src/ tools/ *.sh augur_proxy/ ops/）四表之 UPDATE 寫入者**共 9 檔 10 個交易點**；補丁一律為交易起點加一行：
`cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4)`

| # | 檔 | 交易起點（插入處） | 受閘 UPDATE 語句 | 性質 |
|---|---|---|---|---|
| 1 | `scripts/apply_evolution_promotions.py` | `:332`（主 APPLY 交易） | `:335` UPDATE philosophy_principle SET status；`:360` `_upsert_prodset`（`:49-76` ON CONFLICT DO UPDATE 衝突分支） | 引擎自動路（I5；現 dormant——`run_evolution_iteration.py:235-237` 無 `--allow-apply` 即 skip） |
| 2 | 同上 | `:185`（backfill 交易） | `:186` `_upsert_prodset` | 手動補登錄路 |
| 3 | `scripts/verify_philosophy_factors.py` | `:35` | `:36` UPDATE pfm SET validated_ic=NULL… | 手動驗證回填 |
| 4 | 同上 | `:60` | `:61` UPDATE pfm SET validated_ic,validated_econ | 手動驗證回填 |
| 5 | `scripts/curate_pme_map_expand.py` | `:210` | `:271` UPDATE pp SET hypothesis；`:300` UPDATE pfm SET direction | 策展（hugo 決策後執行） |
| 6 | `scripts/curate_pme_xdom_map.py` | `:221` | `:262` UPDATE pp；`:294` UPDATE pfm | 策展 |
| 7 | `scripts/curate_pme_xdom_ai_predict_map.py` | `:260` | `:347` UPDATE pp；`:385` UPDATE pfm | 策展 |
| 8 | `scripts/curate_pme_xdom_solar_map.py` | `:228` | `:321` UPDATE pp；`:361` UPDATE pfm | 策展 |
| 9 | `scripts/sync_philosophy_principle_status.py` | `:223` | `:225` UPDATE pp SET status | 手動 heal |
| 10 | `src/augur/philosophy/framework.py` | `:270` | `:291` UPDATE pp SET hypothesis；`:302` UPDATE pfm SET direction | library 建置路（seed 重建） |

**不需補丁者（誠實列示）**：
- `scripts/verify_sign_consistency.py:98-100`（feature_sign_check 唯一寫入者）——**純 INSERT append-only**，INSERT 不設閘、零影響；其 selftest `:214-216` 已斷言「寫入僅限 feature_sign_check、不碰 prodset」。
- 各 curate/framework 之 **純 INSERT** 落點（`curate_pme_map_expand.py:308`、`framework.py:304` 等）——無 ON CONFLICT DO UPDATE，不受閘。
- `promotion_queue`／`evolution_apply_log` 之 UPDATE（`apply_evolution_promotions.py:269,303,371,199`）——此二表不在本案射程（維持 delete-only，P2 再議）；同交易帶上通行證亦無害。
- cron 現況：**零自動寫入者實際在跑**（I5 dormant；curate/sync/verify 皆手動）——施作窗風險面極小，但 **APPLY-go 開閘前本補丁必須已合入**（否則首輪自動 APPLY 的 demote/promote 撞閘）。

**hugo 手動 UPDATE 咒語**（apply 後生效；一次性告知）：
```sql
BEGIN; SET LOCAL augur.honesty_write='on'; UPDATE <四表之一> ... ; COMMIT;
```

### 3.4 施作次序（一次窗內完成）

1. **寫入者補丁先合入**（10 點＋migrate script 改版同 commit；無 trigger 時 `SET LOCAL` 無害＝零行為變化）→ 各 `--selftest`／`--dry-run` 過。
2. **DDL 四交易**（§3.1；或跑改版後 `migrate_honesty_guards_ddl.py --apply`，二擇一、以後者為準—住所收斂）。
3. **行為探針**（§6 驗收；全 BEGIN…ROLLBACK 零殘留）。
4. 驗收報告回呈＋登錄冊 B4 勾狀態。

---

## §4 選項與建議案

| 案 | 內容 | 評估 |
|---|---|---|
| **甲（建議）** | 四表升級（3 升級＋1 新掛）＋9 檔 10 點通行證補丁＋migrate script 住所收斂；寫入者先行、DDL 後行；統一 DDL 窗（3c）執行 | 覆蓋晉升鏈判準四要害（方向基準／原則 status／prodset SSOT／符號 verdict）；寫入者盤點已完成（§3.3）＝證偽條件之「漏帶通行證」風險已窮舉到 repo 全量 |
| 乙 | 僅 3 表（延後 feature_sign_check） | 不建議：fsc 恰是 verdict 帳本、唯一寫入者 append-only（**零 UPDATE 合法路**）＝上 GUC 閘零誤傷、受益最大（PASS/FAIL 遭默改即 (b) 綠燈失真） |
| 丙 | 全 23（真裸 22）表一次升級 | 不建議：iteration ledgers 等表 UPDATE 寫入者眾且未逐一盤點，違證偽條件之精神；且其中多屬 append-only 帳本、C5 理由 ③（追加修訂列）於彼仍為正解。維持 P2 分批 |
| 丁 | 不上 GUC、四表改追加修訂列重構 | 不建議：current-state registry 改 append 語意＝schema＋全寫入者＋全讀者重構，比例失衡（§1 治權說明理由 ③） |

**建議：甲案。**
**證偽條件**（承裁決呈案單＋本呈案加嚴）：
1. 若 apply 後任一正常晉升／策展路徑因漏帶通行證報錯（`UPDATE on <tbl> 遭拒`）⇒ 縮射程（回滾該表）＋補寫入者再上。
2. 若 APPLY-go 開閘後首輪 I5 出現 honesty 拒絕例外 ⇒ 同上，且記為本呈案盤點之漏（驗屍留檔）。
3. 若 DDL 交易因 lock_timeout 連續 3 次 abort ⇒ 不硬衝，改窗再試（#30）。

---

## §5 風險與回滾

| 風險 | 面 | 緩解 |
|---|---|---|
| 漏盤點的寫入者撞閘 | repo 掃描以 `grep -rn "UPDATE <tbl>\|INSERT INTO <tbl>"` 窮舉 scripts/src/tools/sh/augur_proxy/ops；但**單一角色下無法從 DB 側枚舉 ad-hoc psql 寫入者** | 施作後首週任何 `遭拒` 例外＝即時可見（fail-loud 即設計目的）；hugo 咒語已附（§3.3） |
| ON CONFLICT 衝突分支不對稱（C5 理由②） | 首插過、再插死 | 寫入者先行＋§6 探針直接 UPDATE 既有列（衝突分支等價路徑） |
| DDL 鎖排隊擋庫 | DROP TRIGGER 取 ACCESS EXCLUSIVE | 每表獨立交易＋`SET LOCAL lock_timeout='5s'`＋前置查 `pg_stat_activity`＋禁與 pg_dump 同窗（#30） |
| 閘強度誤讀 | 被引為「已機械防引擎默改」 | §1 治權說明明文：半閘（意圖留痕＋防手滑），非硬閘；C5 警告留檔 |
| selftest 假綠 | migrate script 舊斷言（PME==8）改後恆真 | 新斷言先驗紅（F5 三規則）；`--check` 輸出逐表列 trigger 名供人眼複核 |

**回滾 DDL 全文**（每表獨立交易；恢復 2026-08-01 親驗現狀）：

```sql
-- 表 1-3（恢復 delete-only）：以 principle_factor_map 為例，另二表同型替換表名
BEGIN;
SET LOCAL lock_timeout = '5s';
DROP TRIGGER IF EXISTS trg_principle_factor_map_honesty_row   ON principle_factor_map;
DROP TRIGGER IF EXISTS trg_principle_factor_map_honesty_trunc ON principle_factor_map;
CREATE TRIGGER trg_principle_factor_map_delonly_row
    BEFORE DELETE ON principle_factor_map
    FOR EACH ROW EXECUTE FUNCTION honesty_delete_only_guard();
CREATE TRIGGER trg_principle_factor_map_delonly_trunc
    BEFORE TRUNCATE ON principle_factor_map
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
COMMIT;

-- 表 4（feature_sign_check 恢復零閘現狀）
BEGIN;
SET LOCAL lock_timeout = '5s';
DROP TRIGGER IF EXISTS trg_feature_sign_check_honesty_row   ON feature_sign_check;
DROP TRIGGER IF EXISTS trg_feature_sign_check_honesty_trunc ON feature_sign_check;
COMMIT;
```

寫入者補丁**不需回滾**（無 trigger 時 `SET LOCAL` 無害），但若 Steward 裁回滾整案則同 commit revert。資料零觸碰（本案只動 trigger，不動任何列）。

---

## §6 驗收判準（機械可判；全部通過才勾登錄冊 B4）

```sql
-- V1 覆蓋 census：四表各恰 2 trigger、fn=honesty_ledger_guard、row 閘 upd=t del=t、trunc 閘在
SELECT c.relname, count(*) FILTER (WHERE (t.tgtype::int&16)>0 AND (t.tgtype::int&8)>0) AS row_ud,
       count(*) FILTER (WHERE (t.tgtype::int&32)>0) AS trunc_t, count(*) AS n
FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_proc p ON p.oid=t.tgfoid
WHERE NOT t.tgisinternal AND p.proname='honesty_ledger_guard'
  AND c.relname IN ('principle_factor_map','philosophy_principle',
                    'evolution_production_feature_set','feature_sign_check')
GROUP BY 1;                          -- 期望：4 列、每列 row_ud=1 trunc_t=1 n=2

-- V2 全庫面：delete-only 降為 20 表 40 trigger；ledger_guard 升為 9 表
SELECT p.proname, count(DISTINCT c.relname), count(*) FROM pg_trigger t
JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_proc p ON p.oid=t.tgfoid
WHERE NOT t.tgisinternal AND p.proname IN ('honesty_delete_only_guard','honesty_ledger_guard')
GROUP BY 1;                          -- 期望：delonly 20|40；ledger 9|17
```

行為探針（每表四式、全 BEGIN…ROLLBACK 零殘留；表 1 例，餘三表同型）：

```sql
-- V3 裸 UPDATE 必拒（期望：ERROR ... 遭拒:須經工具鏈）
BEGIN; UPDATE principle_factor_map SET direction=direction WHERE map_id=(SELECT min(map_id) FROM principle_factor_map); ROLLBACK;
-- V4 帶證 UPDATE 必過（期望：UPDATE 1）
BEGIN; SET LOCAL augur.honesty_write='on'; UPDATE principle_factor_map SET direction=direction WHERE map_id=(SELECT min(map_id) FROM principle_factor_map); ROLLBACK;
-- V5 DELETE 必拒、帶證亦拒（期望：ERROR ... 無合法路徑）
BEGIN; SET LOCAL augur.honesty_write='on'; DELETE FROM principle_factor_map WHERE map_id=(SELECT min(map_id) FROM principle_factor_map); ROLLBACK;
-- V6 feature_sign_check INSERT 仍自由（期望：INSERT 0 1）
BEGIN; INSERT INTO feature_sign_check (feature,h,direction_source,verdict) VALUES ('__b4_probe__',20,'probe','UNJUDGEABLE'); ROLLBACK;
```

程式面：
- V7 `python scripts/migrate_honesty_guards_ddl.py --selftest` rc=0（新斷言曾驗紅之紀錄附於 commit）；`--check` 輸出人眼複核四表 trigger 名。
- V8 `python scripts/apply_evolution_promotions.py --selftest` rc=0；`--dry-run` rc=0；`--backfill-prodset --dry-run` rc=0。
- V9 九檔寫入者各自 selftest／dry-run（有者）rc=0；`grep -c "SET LOCAL augur.honesty_write" ` 於 §3.3 十點逐一命中。
- V10（時間性）APPLY-go 開閘後首輪 I5：`evolution_apply_log` 新列正常落帳、`twevo.log` 零 `遭拒` 例外。

---

## §7 Steward 決定欄（留白）

| 決定 | 圈選／簽註 |
|---|---|
| B4 採案（甲／乙／丙／丁／退回） | ＿＿＿＿＿＿ |
| 翻 C5 一部之裁決（含 RULING 編號指配） | ＿＿＿＿＿＿ |
| DDL 窗指定（統一窗 3c 併 D4/E2？） | ＿＿＿＿＿＿ |
| P2 殘餘（20 表，實 19 待閉）分批授權 | ＿＿＿＿＿＿ |
| 簽署 | ＿＿＿＿＿＿（hugo TTY）＿＿＿＿ 日期 ＿＿＿＿ |
