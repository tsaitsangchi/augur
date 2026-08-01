# [DRAFT 呈案] C1——validation_evidence manual 5 條有效期方案（未經拍板不得施作）

> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，所提機制會限制「AI 標綠後永久免驗」之路徑，屬對 AI 自身產出之監督強化；一切數字附現查指令可獨立複驗，不以「相信起草者」為依據。
> 呈案日 2026-08-01（W2 批）；設計 SSOT＝`reports/augur_problem_solution_register_20260801.md` §3-C1＋`reports/augur_steward_adjudication_sheet_20260801.md` 三-C1。

## §1 問題與授權鏈

**問題**：`validation_evidence`（19 列證據帳本）之 5 條 `check_type='manual'` 列由人裁定級後**永久免疫於紅燈**——`verify_validation_evidence.py --run` 對 manual 一律跳過（`scripts/verify_validation_evidence.py:76-79`），故 2026-07-11/07-12 的人裁 green **無論世界怎麼變都恆綠**。r3 深化報告（`reports/augur_deep_understanding_r3_20260801.md` §二）列為「仍未修之四假綠」之一。5 條中 E2/E5 之 status_note 明載「解凍後重估／清償」為 live 維運工作項——裁定已 20 天、無任何機制逼它回頭。

**授權鏈**：登錄冊 C1（W2 呈案項）「排程 AI／有效期 Steward」；裁決呈案單建議案＝「manual 列加 `valid_until`（預設簽核日＋90 天），過期自動轉 `unverified` 紅；重簽由 hugo；排程兩行入 cron 合批」。本檔＝有效期部分之完整呈案；**排程部分已於 W1 cron 合批完成並 live**（見 §2.4，與登錄冊「C1 ☐」狀態欄之偏差，明標）。拍板權專屬 Steward（§8.1）；DDL 施作與重簽＝hugo。

## §2 現況親驗（2026-08-01 15:0x 現查；配方＝repo `.env` + psql 唯讀）

### 2.1 帳本總況（與登錄冊「19 列＝green 14/red 5/manual 5」相符）

```sql
SELECT status, count(*) FROM validation_evidence GROUP BY status ORDER BY 1;
-- green | 14
-- red   |  5
```

### 2.2 manual 5 列逐列（**全部 green**；2 列 `last_verified_at` 為 NULL——有效期起算須 COALESCE）

```sql
SELECT evidence_id, chain_link, status, last_verified_at, created_at
FROM validation_evidence WHERE check_type='manual' ORDER BY evidence_id;
```

| evidence_id | chain_link | status | last_verified_at | created_at | status_note 摘要（人裁提供者） |
|---|---|---|---|---|---|
| E2_macro_latent_debt | feature | green | 2026-07-12 02:01:03+08 | 2026-07-11 11:49:37+08 | 人裁除名(hugo 2026-07-12 E 債裁定)…重 sync 已隨解凍成為常態維運 |
| E3_promotion_funnel | promotion | green | **NULL** | 2026-07-11 11:49:37+08 | 人審 2026-07-11:依既有方法論 SSOT+B 提拔裁決報告 |
| E4_gm_promotion_gap | gate | green | **NULL** | 2026-07-11 11:49:37+08 | (a) 裁決落地:gm 入 canonical 29、全鏈重訓完成 |
| E5_survivorship_debt | train | green | 2026-07-12 02:01:03+08 | 2026-07-11 11:49:37+08 | 人裁除名(hugo 2026-07-12)…解凍後以真 PIT 名單重估=live 維運工作項 |
| E7_h60_ece_outlier | calibration | green | 2026-07-12 02:01:03+08 | 2026-07-11 11:49:37+08 | 人裁定級(hugo 2026-07-12)…V1 判讀前不背書之緩解措施留存 |

種子原值對照（`scripts/migrate_validation_evidence_ddl.py` SEEDS）：E4_gm 種子＝**red**（已知債）、E5 種子＝**red**、E2/E7 種子＝amber——現值 green 皆出自 hugo 07-11/07-12 人裁（status_note 留痕），**非機器覆寫**；惟裁後即無任何到期機制。

### 2.3 結構現況

```sql
-- 欄位:12 欄(machine_note 已在;**無 valid_until**)
SELECT column_name FROM information_schema.columns WHERE table_name='validation_evidence';
-- ... status_note / last_verified_at / created_at / machine_note

-- trigger:0(人裁欄無 DB 層防護——本呈案不擴射程,B4 另案)
SELECT count(*) FROM pg_trigger WHERE tgrelid='validation_evidence'::regclass AND NOT tgisinternal;  -- 0
```

### 2.4 排程現況（**偏差明標**：登錄冊 C1 狀態 ☐，但 cron 兩行已 live）

```
crontab -l ｜ 節錄（註記「登錄冊 C1 2026-08-01」）:
10 7 * * * cd /home/hugo/project/augur && venv/bin/python scripts/verify_validation_evidence.py --run >> $HOME/logs/validation_evidence.log 2>&1
40 7 * * 0 cd /home/hugo/project/augur && venv/bin/python scripts/verify_validation_evidence.py --run --with-scripts >> $HOME/logs/validation_evidence.log 2>&1
```

`~/logs/validation_evidence.log` 尚不存在（今日 07:10 前 cron 未掛；首次觸發＝08-02 07:10）。今日 13:14-13:15 有一次 `--run`（red 列之 `last_verified_at` 為證；session 手動）。**故本呈案僅餘「有效期」一件事**；過期檢查搭既有每日 07:10 便車、**零新增 cron、零新增自動鏈長**（OCV 四項不弱化）。

## §3 方案

### 3.1 DDL（完整全文；19 列小表、鎖秒級；統一 DDL 窗 3c 或即時皆可）

```sql
-- C1-DDL-1:加欄(冪等)
BEGIN;
SET lock_timeout = '5s';
ALTER TABLE validation_evidence ADD COLUMN IF NOT EXISTS valid_until timestamptz;
COMMENT ON COLUMN validation_evidence.valid_until IS
  'manual 型有效期(C1 2026-08-01):過期由 verify_validation_evidence --run 自動轉 unverified'
  '(green/amber→unverified;red 不動——紅比未驗更誠實);重簽=hugo 更新 status+last_verified_at+valid_until;'
  'sql/script_exit 型恆 NULL(每跑重驗、無效期概念)';
COMMIT;

-- C1-DDL-2:存量初始化(Steward 圈選 90/180 後由 hugo 執行;90 天示例)
-- 基準=COALESCE(last_verified_at, created_at)——E3/E4_gm 之 last_verified_at 為 NULL(§2.2)
BEGIN;
SET lock_timeout = '5s';
UPDATE validation_evidence
   SET valid_until = COALESCE(last_verified_at, created_at) + interval '90 days'
 WHERE check_type='manual' AND valid_until IS NULL;
COMMIT;

-- C1-DDL-3(選配乙,機械閉合;須在 DDL-2 之後):讓「manual green/amber 而無有效期」結構性不可能
BEGIN;
SET lock_timeout = '5s';
ALTER TABLE validation_evidence ADD CONSTRAINT chk_ve_manual_expiry
  CHECK (check_type <> 'manual' OR status NOT IN ('green','amber') OR valid_until IS NOT NULL);
COMMIT;
```

90 天初始化之實際到期日（§2.2 現值代入，已現算）：E2＝2026-10-10、E3＝2026-10-09、E4_gm＝2026-10-09、E5＝2026-10-10、E7＝2026-10-10——**全部落在 10-14 日曆復審之前**，重簽可併該次復審一次做完（180 天則為 2027-01-07/08）。

### 3.2 verify 端 diff 計畫（`scripts/verify_validation_evidence.py`；行號＝現行檔）

1. **:72-74**（run() 之 SELECT）：欄位清單加 `valid_until` → `SELECT evidence_id, check_type, check_sql, check_cmd, status, valid_until FROM ...`；迴圈解包 `for eid, ctype, csql, ccmd, st, vu in rows:`。
2. **:76-79**（manual 分支）改為過期自動降轉（比較在 SQL 內用 DB 之 now()；只寫 `machine_note`、**永不碰 `status_note`**〔07-31 抹痕教訓〕、**不動 `last_verified_at`**〔它是有效期起算基準與重簽稽核痕〕）：

```python
if ctype == "manual":
    if vu is not None and st in ("green", "amber"):
        cur.execute(
            "UPDATE validation_evidence SET status='unverified', machine_note=%s "
            "WHERE evidence_id=%s AND check_type='manual' "
            "AND valid_until < now() AND status IN ('green','amber')",
            (f"manual 有效期已過(valid_until={vu:%Y-%m-%d});自動轉 unverified,待 hugo 重簽", eid))
        if cur.rowcount:
            conn.commit()
            n_exp += 1
            print(f"  ✗ {eid}: manual 有效期已過({vu:%Y-%m-%d}) → unverified(待 hugo 重簽)")
            continue
    n_skip += 1
    print(f"  — {eid}: manual(人審;現況 {st}"
          + (f";有效至 {vu:%Y-%m-%d}" if vu else ";無有效期") + ")")
    continue
```

3. **:75** 計數器加 `n_exp = 0`；**:98** 總結行加 `過期轉 unverified {n_exp}`。
4. **:102-109**（`_list()`）：SELECT 加 `valid_until` 顯示欄（`-` 表無），一眼可見各 manual 列剩餘效期。
5. **:2-10**（docstring）：「manual 型跳過(人審更新)」改「manual 型:未過期跳過、過期自動轉 unverified(人重簽)」。
6. `strict()` **零改動**——`unverified` 本已 ≠ green，自動擋 GATE `--strict`。
7. **選配乙之種子相容**（若採 C1-DDL-3 才需要）：`scripts/migrate_validation_evidence_ddl.py:122-124` 之 INSERT 加 `valid_until` 欄，manual 種子帶 `now() + interval '90 days'`（全新 DB bootstrap 時歷史人裁自帶 90 天重簽期，否則 CHECK 會使 `--run` 種子在新機炸掉）。

### 3.3 重簽路徑（hugo TTY 親跑；AI 不代打人簽）

```sql
-- 逐列重簽模板(status_note 如需更新由 hugo 同句改寫)
UPDATE validation_evidence
   SET status='green', last_verified_at=now(), valid_until=now() + interval '90 days'
 WHERE evidence_id='<ID>' AND check_type='manual';
```

## §4 選項與建議案

| 項 | 甲 | 乙 | 建議 |
|---|---|---|---|
| 效期長度 | **90 天**（裁決單建議；到期日恰在 10-14 復審前，首輪重簽可併復審） | 180 天（半衰期較符「人裁理由以年計」、擾人低） | **甲 90 天**。證偽條件（裁決單原文）：90 天內同一 manual 列被重簽 ≥2 次且內容不變 → 放寬 180 |
| 過期降轉範圍 | **green/amber → unverified；red 不動**（紅是債之誠實記載，降成 unverified 反而弱化警示） | 全部 → unverified | **甲**。證偽：若出現「red 列世界已變好但無人重看」實例，改為 red 亦到期進人裁佇列 |
| 機械閉合 CHECK（C1-DDL-3） | **加**（「無有效期之 manual 綠」結構性不可能——先讓紅燈會亮的第一原則；含 §3.2-7 種子相容 diff） | 不加（僅靠 verify 端邏輯；未來新 manual 列可再度永久免疫） | **甲 加**。證偽：CHECK 若擋掉任何正當人裁路徑（如須先綠後補期），改為 verify 端警示 |

**建議案彙整**：90 天＋green/amber 降轉＋CHECK 閉合；DDL-1/2/3 由 hugo 依序執行（DDL-3 必在 DDL-2 後），verify diff 隨後入 repo；重簽節奏交 10-14 復審一併處理首輪。

## §5 風險與回滾

- **風險 1**：過期降轉使 `--strict`（解凍 GATE 前置）從此多 5 個潛在紅點 → 這正是設計目的（免疫消失）；現況 `--strict` 本已因 5 條 sql/script red 不通過，無新增阻塞面。
- **風險 2**：機器 UPDATE 誤傷人裁欄 → 寫入欄僅 `status`＋`machine_note`，謂詞含 `check_type='manual' AND valid_until < now()`；`status_note`／`last_verified_at` 不在 SET 清單（07-31 COALESCE 死碼抹痕之結構性防再犯）。
- **風險 3**：該表 trigger＝0（§2.3），理論上任何寫入者可改 `valid_until` 自延效期 → 誠實記載為殘餘風險；DB 層防護屬 B4（UPDATE-GUC 閘）射程，本案不擴。
- **回滾**：`ALTER TABLE validation_evidence DROP CONSTRAINT IF EXISTS chk_ve_manual_expiry; ALTER TABLE validation_evidence DROP COLUMN IF EXISTS valid_until;`＋verify 端 git revert。已被降轉之列由 hugo 依 status_note 重簽回原狀（人裁原文全程未被觸碰，可完整還原）。

## §6 驗收判準（機械可判）

1. `SELECT count(*) FROM information_schema.columns WHERE table_name='validation_evidence' AND column_name='valid_until'` ＝ 1。
2. `SELECT count(*) FROM validation_evidence WHERE check_type='manual' AND valid_until IS NULL` ＝ 0（DDL-2 後）。
3. （採乙閉合時）`SELECT count(*) FROM pg_constraint WHERE conname='chk_ve_manual_expiry'` ＝ 1。
4. `python scripts/verify_validation_evidence.py --list` 每 manual 列印出 `有效至 YYYY-MM-DD`。
5. 行為紅測（唯讀構造）：以單列 `UPDATE ... SET valid_until=now()-interval '1 day' WHERE evidence_id='E3_promotion_funnel'`（hugo 演練、演練後重簽還原）後跑 `--run --id E3_promotion_funnel` → stdout 含「有效期已過」且 `status='unverified'`、`status_note` 逐字不變、`last_verified_at` 不變。
6. `--strict` 於（5）狀態下 exit 1 且列出該列。
7. 明晨 07:10 cron 後 `~/logs/validation_evidence.log` 存在且含「跳過」或「有效至」字樣（排程與有效期閉環同框）。

## §7 Steward 決定欄

- [ ] 效期：90 ／ 180 ／ 其他＝＿＿＿
- [ ] 降轉範圍：甲（green/amber）／ 乙（全部）
- [ ] CHECK 閉合：加 ／ 不加
- [ ] DDL 執行窗：即時 ／ 併統一 DDL 窗（3c）
- 裁決：＿＿＿＿＿＿＿＿（日期／簽）
