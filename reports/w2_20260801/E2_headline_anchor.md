# [DRAFT 呈案] E2｜headline 錨落帳——新表 `alpha_headline_anchor` DDL＋migrate 規畫＋hugo 親簽 INSERT 範本——未經拍板不得施作

> **登錄冊**：`reports/augur_problem_solution_register_20260801.md` §1 E2（W2；DDL AI／簽錨=hugo TTY）＋§3-E「兩時欄分開、不補造時戳」；DDL 排 **3c 統一 DDL 窗**（與 D4/B4 同窗）。
> **建議案底稿**：`reports/augur_steward_adjudication_sheet_20260801.md`「五、E2」。
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草；新表將成為「確立級數字」之機器可查載體，AI 之數字宣稱亦受其約束——起草者不得為核准主體，簽錨列一律 hugo TTY 親簽（never-type-human-signature 紀律），全部出處附 file:line 可獨立覆驗。

---

## §1 問題與授權鏈

**問題一句話**（r3 `augur_deep_understanding_r3_20260801.md:32,112`）：headline 錨「治權認定 1.1321（hugo 簽）與本機快照 1.1302 **皆無 DB 帳**」；機器可查之 `trial_ledger` 停在 07-13（值=1.1972 舊錨、已不可再現）、本機 `revalidation_baseline` 凍在 07-09（1.1972 世代）——「確立級數字」與帳本分家，任何下游（週報、A2/A4 證偽條件之 headline 鏈量測）都無機器可查的錨。

**授權鏈**：Steward 指示（登錄冊性質段）→ E2 標「DDL AI／簽錨=hugo TTY」→ 本檔＝DDL 與程式規畫之呈案；**簽錨 INSERT 之執行與其中數值之認定專屬 hugo**（promoted_by/approved_by/signed_by 類欄位一律 hugo 親跑寫入；AI 僅備範本）。**不得事後補造時戳**：表以「登錄時刻」與「宣稱所指時點」兩欄分開落實。

---

## §2 現況親驗（2026-08-01 執行，全部現查）

### 2.1 DB 三查（分家事實成立）

```sql
SELECT to_regclass('public.alpha_headline_anchor') IS NULL;   -- t（表不存在）
SELECT max(run_at)::date, count(*) FROM trial_ledger;          -- 2026-07-13 | 32
SELECT cell, universe, frozen_at::date, net_sharpe, n_periods
FROM revalidation_baseline WHERE cell='ridge_H60_LO';
-- ridge_H60_LO | asof_incumbent | 2026-07-09 | 1.197184709380887 | 25
-- ridge_H60_LO | pit_broad      | 2026-07-09 | 1.0022458998152453 | 25
```
即：本機 DB 最新的 headline 機算帳＝**1.1972 世代（07-09 凍結）**；07-17 重定錨（發生於簽核機）從未落入本機任何表——r3「皆無 DB 帳」成立，且比 r3 措辭更完整：**本機 DB 現值還停在被取代的 1.1972**。兩表皆已掛 `honesty_ledger_guard`（UPDATE-GUC＋禁刪，現查 trigger 在）。

### 2.2 兩數之出處現查（file:line；含歧異揭露）

**1.1321**：
- `reports/alpha_p0_diagnostics_20260718.md:24`「headline 錨 1.1972 今日不可再現（同配方重跑=**1.1321**，Δ−0.065）」；`:44`「34 特徵=1.1321」（feats_hash `canonical34_stageB_20260706`）；`:194` DSR 段（N=32 池→**34.5%**）。
- 簽核事實（hugo 拍 A「修復重定錨」、簽核錨=1.1321、於另一台機器）之載體＝專案記憶 `alpha-phase1-anchor-repair`；**repo 內無「1.1321 簽核」之獨立文件**（`taiwan_alpha_improvement_plan_20260717.md` grep 零命中）。

**1.1302**：
- `reports/alpha_phase1_tail_verdict_20260717.md:6,111`「headline 維持 ridge_H60_LO **1.1302** 不動（canonical34/since2014/cost0.585%/T=25）」；
- `reports/alpha_p1_buffer_verdict_20260717.md:4`「asof 基準=1.1302（**P2 新量尺現值**）」；`reports/alpha_p4_voltarget_verdict_20260717.md:6-8`（基準=1.1302 錨）；
- `HANDOFF.md:207`（1-2 P2 turnover 半和量尺 ✅「headline→1.1302」）、`HANDOFF.md:209`「→**新錨 net 1.1302**／超額+0.372／HAC-t 6.70／DSR 47.9%…→revalidation_baseline re-freeze」；
- 記憶 `alpha-phase1-anchor-repair`：本機 07-16 快照 `revalidate_baseline.py --dry-run` 實算=net 1.1302／DSR 34.3%（與簽核 1.1321 差 0.0019=PriceAdj 快照漂）。

**⚠ 歧異揭露（與登錄冊不符者，明標）**：登錄冊／呈案單將兩值定名為「1.1321=治權錨、1.1302=本機快照」；但 repo 文件鏈同時支持另一個系譜——**1.1321=07-17/18 P0 量尺之重定錨值，1.1302=其後 P2 turnover 半和量尺之最終 headline（HANDOFF.md:209 明文稱之「新錨」）**，且本機 07-16 快照 dry-run 亦得 1.1302（兩種解釋數值巧合同落 1.1302，超額/HAC-t 小數不同：0.372/6.70 vs 0.3772/6.945）。**兩值各自為錨的量尺口徑不同這件事本身，正是必須落帳的內容**——表設計以 `scale_note` 欄強制記錄量尺、由 hugo 簽核時定奪各列定名。另：**DSR「47.9%」（HANDOFF.md:209）已被記憶判「查無來源、疑誤植」**（P0 §5 實跑=34.5%@N=32、本機 dry-run 34.3% 吻合）——範本 `n_basis` 欄預填 34.5%@N=32 並註記 47.9% 不採。

### 2.3 復用件現查

`pg_proc` 現查：`honesty_ledger_guard`（UPDATE-GUC＋禁 DELETE/TRUNCATE）與 `honesty_delete_only_guard` 皆在（`scripts/migrate_honesty_guards_ddl.py:33-52` 為 SSOT）——新表直接復用前者（#12 單一閘住所），滿足登錄冊「honesty guard 上閘後不可刪」。

---

## §3 方案

### 3.1 設計要點（為何新表、而非動既有表）

- `revalidation_baseline`＝**本機機算帳**（PK=(cell,universe) 冪等覆寫、無沿革）；`trial_ledger`＝試驗帳。兩者都不該承載「治權宣稱」——簽核值 1.1321 在本機**不可再現**，寫進機算帳＝把不可再現數字混進可再現帳（#15）。新表＝**append-only 宣稱帳**：誰、何時、宣稱哪個時點的哪個數、量尺為何、出處何在；沿革以 `supersedes_id` 鏈成家譜，永不覆寫。
- 「兩錨兩時欄」：`claim_asof`（宣稱所指時點）＋`recorded_at`（登錄時刻，DB now()）分開；原始宣稱行為時點另設 `claimed_at`（**可考才填、不可考=NULL 誠實留白——不補造時戳**）。

### 3.2 DDL 全文（3c 統一 DDL 窗執行；秒級、僅建新表零鎖既有表）

```sql
-- ========== E2 alpha_headline_anchor DDL（冪等；統一 DDL 窗;dump 期間禁跑 #30） ==========
SET lock_timeout = '5s';

CREATE TABLE IF NOT EXISTS alpha_headline_anchor (
  anchor_id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  anchor_label  text        NOT NULL,                    -- 人讀標籤(如 'headline_govern_20260717')
  claim_kind    text        NOT NULL CHECK (claim_kind IN
                  ('governance_signed','local_snapshot','historical_reference')),
  metric_name   text        NOT NULL DEFAULT 'net_sharpe',
  metric_value  double precision NOT NULL,
  recipe        text        NOT NULL,                    -- 'ridge_H60_LO/asof_incumbent/canonical34/since2014/cost0.585%'
  scale_note    text        NOT NULL,                    -- 量尺口徑(P0 vs P2 turnover 半和)——兩錨歧異之關鍵欄
  n_basis       text        NOT NULL,                    -- 口徑戳記(P0 紀律:DSR 引用必帶 @N=、T=)
  claim_asof    date        NOT NULL,                    -- 宣稱所指時點(資料 as-of / 簽核基準日)
  claimed_at    timestamptz,                             -- 原始宣稱行為時點;不可考=NULL(不補造)
  recorded_at   timestamptz NOT NULL DEFAULT now(),      -- 登錄時刻(落帳當下;與 claim_asof/claimed_at 分開)
  source_ref    text        NOT NULL,                    -- 出處 file:line(#10 可溯源;多出處分號串)
  signed_by     text,                                    -- hugo(親簽列必填;唯 hugo TTY 寫入)
  machine       text,                                    -- 產生該數字之機器(如 'DESKTOP(簽核機)'/'PC002-S1800')
  supersedes_id bigint REFERENCES alpha_headline_anchor(anchor_id),
  note          text,
  CONSTRAINT chk_aha_signed CHECK (claim_kind <> 'governance_signed' OR signed_by IS NOT NULL)
);

-- honesty guard 復用(#12;函式 SSOT=migrate_honesty_guards_ddl.py:33——DELETE/TRUNCATE 一律拒、
-- UPDATE 須 SET LOCAL augur.honesty_write='on';本表常態零 UPDATE,修訂=追加新列+supersedes_id)
DROP TRIGGER IF EXISTS trg_alpha_headline_anchor_honesty_row ON alpha_headline_anchor;
CREATE TRIGGER trg_alpha_headline_anchor_honesty_row
  BEFORE UPDATE OR DELETE ON alpha_headline_anchor
  FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS trg_alpha_headline_anchor_honesty_trunc ON alpha_headline_anchor;
CREATE TRIGGER trg_alpha_headline_anchor_honesty_trunc
  BEFORE TRUNCATE ON alpha_headline_anchor
  FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();

COMMENT ON TABLE alpha_headline_anchor IS
  'headline 宣稱帳(append-only 家譜;登錄冊 E2 2026-08-01):治權簽核錨與本機快照分 claim_kind 落帳;claim_asof(宣稱所指)/claimed_at(原始宣稱,不可考=NULL 不補造)/recorded_at(登錄)三時點分立;修訂=新列+supersedes_id,不覆寫;governance_signed 列唯 hugo TTY 親簽';
```

### 3.3 migrate 腳本規畫（新增 `scripts/migrate_alpha_headline_anchor_ddl.py`；首次提交即含矩陣 #18/#29d）

| 函式 | 職責 | 輸入/輸出 |
|---|---|---|
| `check(conn)` | 唯讀：`to_regclass` ＋列 `pg_trigger`（表上兩 trigger）＋現有列數/claim_kind 分佈 | stdout；exit 0 |
| `apply(conn)` | **先斷言 `honesty_ledger_guard` 函式存在（`pg_proc` 查無即 fail-loud exit 1，不自造第二住所 #12）** → 執行 §3.2 DDL（冪等） → 自動接 `check` | exit 0/1 |
| `selftest()` | 零 DB 紅綠：DDL 字串斷言（IDENTITY PK／CHECK 三值／`chk_aha_signed`／兩 trigger 各 DROP IF EXISTS／`SET lock_timeout`／`claimed_at` 可 NULL 而 `recorded_at` NOT NULL）；**驗紅**：以壞 DDL 變體（拿掉 CHECK）餵斷言函式須 FAIL（回歸鎖先驗紅三規則） | exit 0/1 |
| `main` | 無參數=印矩陣＋`--check`（安全預設）；`--check`／`--apply`／`--selftest` | — |

標頭：🎯 白話＋「守 #6 #10 #12 #15 #29a/d」＋執行指令矩陣四行。**不做**：INSERT（簽錨非腳本職權）、任何對 `revalidation_baseline`/`trial_ledger` 的觸碰。執行窗：3c 統一 DDL 窗（與 D4/B4 合批），**避開週六 07:30 backup cron 之 pg_dump 時段（#30 dump 期間禁 DDL）**。

### 3.4 hugo TTY 親簽 INSERT 範本（拍板後由 hugo 親跑；數值定名權在 hugo）

```sql
-- ========== E2 簽錨(hugo TTY 親跑;AI 不代打) ==========
-- 執行前請逐欄核對;metric_value/claim_kind 之定名若與 §2.2 歧異揭露之認定不同,以你簽的為準。
BEGIN;
SET LOCAL lock_timeout = '5s';

-- 列 1:治權簽核錨(登錄冊定名 1.1321;量尺=P0;簽核行為在簽核機、行為時點不可考=claimed_at NULL)
INSERT INTO alpha_headline_anchor
  (anchor_label, claim_kind, metric_name, metric_value, recipe, scale_note, n_basis,
   claim_asof, claimed_at, source_ref, signed_by, machine, note)
VALUES
  ('headline_govern_20260717', 'governance_signed', 'net_sharpe', 1.1321,
   'ridge_H60_LO/asof_incumbent/canonical34/since2014/cost0.585%',
   'P0 量尺(2026-07-17 PriceAdj 修復後重定錨當日)',
   'T=25 periods;DSR=34.5%@N=32(alpha_p0_diagnostics §5 實跑;HANDOFF 之 47.9% 查無來源、不採)',
   DATE '2026-07-17', NULL,
   'reports/alpha_p0_diagnostics_20260718.md:24,44;memory:alpha-phase1-anchor-repair(簽核=另一機器,repo 無獨立簽核文件——誠實揭露)',
   'hugo', 'DESKTOP(簽核機;本機 DB 無此帳)',
   '本機不可再現(07-16 快照 dry-run=1.1302,Δ0.0019=PriceAdj live sync 漂移);歧異見呈案 §2.2');

-- 列 2:本機快照(登錄冊定名 1.1302;⚠ repo 文件鏈亦稱此值為 P2 量尺後之 headline/HANDOFF「新錨」)
INSERT INTO alpha_headline_anchor
  (anchor_label, claim_kind, metric_name, metric_value, recipe, scale_note, n_basis,
   claim_asof, claimed_at, source_ref, signed_by, machine, note)
VALUES
  ('headline_local_20260717', 'local_snapshot', 'net_sharpe', 1.1302,
   'ridge_H60_LO/asof_incumbent/canonical34/since2014/cost0.585%',
   '雙出處並存:P2 turnover 半和量尺 headline(維持不動)/本機 07-16 快照 dry-run——由簽核者於 note 定奪或並記',
   'T=25 periods;本機 dry-run DSR=34.3%(N=32 口徑)',
   DATE '2026-07-17', TIMESTAMPTZ '2026-07-17 00:00+08',  -- dry-run 執行日可考;精確時刻不可考則改 NULL
   'reports/alpha_phase1_tail_verdict_20260717.md:111;reports/alpha_p1_buffer_verdict_20260717.md:4;HANDOFF.md:207,209;memory:alpha-phase1-anchor-repair',
   'hugo', 'PC002-S1800',
   'HANDOFF.md:209 稱本值「新錨」——與登錄冊「1.1321=治權錨」定名歧異,簽核時裁定;本機 revalidation_baseline 現值仍為 1.1972 世代(07-09 凍結)');

COMMIT;

-- 【後驗＋負向探針(選跑;證明閘武裝)】
SELECT anchor_id, anchor_label, claim_kind, metric_value, claim_asof, recorded_at FROM alpha_headline_anchor;
BEGIN; DELETE FROM alpha_headline_anchor WHERE anchor_id=1; ROLLBACK;  -- 期望 RAISE「誠實帳本閘拒絕」
```

---

## §4 選項與建議案

| 案 | 內容 | 評 |
|---|---|---|
| **主案（建議）** | §3.2 表＋§3.3 腳本＋§3.4 兩列親簽 | 呈案單建議案原文；純落帳零反向風險 |
| 變體 a | 兩列外加第三列 `historical_reference`（1.1972 舊錨家譜首節點） | 可選：1.1972 已有 DB 帳（trial_ledger/revalidation_baseline），不加亦可溯；加了家譜完整。**建議加**（claim_kind 已預留） |
| 變體 b | 不建新表，改在本機重跑 `revalidate_baseline.py` re-freeze | **否**——本機重算≠簽核值（1.1321 不可再現），且覆寫機算帳治不了「宣稱無帳」病 |

**建議：主案＋變體 a（三列）**。證偽條件（沿呈案單）：純落帳無反向風險；若表建後三個月零查詢（週報/驗證端無人讀），降為附錄表。**另一證偽**：若日後簽核機 dump 抵達、其 `revalidation_baseline` 實值與簽核列不符，則簽核列之 note 追加新列修正（supersedes_id 鏈），不改寫原列。

## §5 風險與回滾

- **DDL 風險 ≈ 零**：僅 CREATE 新表＋自表 trigger，不觸既有表；`SET lock_timeout='5s'` 絕不排隊；窗=3c 統一窗、避 dump 時段。回滾：表零列時 `DROP TABLE`（**須先 `DROP TRIGGER` 兩支？不必——trigger 隨表刪**；但 guard 禁 TRUNCATE/DELETE 不禁 DROP——superuser 單一角色現實之殘餘風險，與 trial_ledger 同級，誠實記載不粉飾）；已簽列後不回滾、只 supersede。
- **定名歧異風險**：§2.2 之 1.1321/1.1302 定名歧異若未在簽核時裁定，表會固化錯誤定名——已以 `scale_note` 強制欄＋範本 note 預寫歧異、簽核時裁定來緩解。
- **時戳誠實**：`claimed_at` 預設 NULL 不補造；`recorded_at` 由 DB now() 生成不可指定（範本不含該欄）。
- **AI 代打風險**：`signed_by='hugo'` 列若由 AI 執行即違 never-type-human-signature——範本明文「hugo TTY 親跑」，且 `chk_aha_signed` 只驗非空、程序約束靠紀律＋（既有）人閘慣例，誠實承認此欄無機械人證。

## §6 驗收判準（機械可判）

1. `SELECT to_regclass('public.alpha_headline_anchor') IS NOT NULL` ＝ t。
2. `SELECT count(*) FROM pg_trigger WHERE tgrelid='alpha_headline_anchor'::regclass AND NOT tgisinternal` ＝ **2**。
3. `python scripts/migrate_alpha_headline_anchor_ddl.py --selftest` exit 0（含驗紅分支）；`--check` exit 0。
4. 簽錨後：`SELECT count(*) FILTER (WHERE claim_kind='governance_signed'), count(*) FILTER (WHERE claim_kind='local_snapshot') FROM alpha_headline_anchor` ＝ (1,1)（採變體 a 再加 historical_reference=1）；每列 `source_ref` 非空、`recorded_at` 落於簽核當日。
5. 負向探針：`DELETE`/`TRUNCATE`/裸 `UPDATE` 三者於 ROLLBACK 交易內皆 RAISE。
6. r3 口徑句「1.1321/1.1302 皆無 DB 帳」自此不再為真（下輪深化理解可機械覆核）。

## §7 Steward 決定欄

- [ ] E2 主案同意（表＋腳本＋兩列親簽；DDL 入 3c 統一窗）
- [ ] 變體 a（加第三列 1.1972 historical_reference）：要／不要
- [ ] 列 1/列 2 之 metric_value 與定名維持範本；或改：＿＿＿＿＿＿
- [ ] 其他：＿＿＿＿＿＿
- 簽：＿＿＿＿（hugo）　日期：＿＿＿＿
