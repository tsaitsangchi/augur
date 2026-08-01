# [DRAFT 呈案] E1｜dgate own_stack 三門處置（supersede vs 讓 08-03 首發）——未經拍板不得施作

> **登錄冊**：`reports/augur_problem_solution_register_20260801.md` §1 E1（W2）＋§3-E。
> **建議案底稿**：`reports/augur_steward_adjudication_sheet_20260801.md`「五、E1」。
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，涉及對預註冊監督門之廢止裁量；起草者不得為核准主體，全部主張附 SQL／file:line 可獨立覆驗，建議附證偽條件。
> **時效**：**2026-08-03（一）20:00**——arena cron（`crontab` `0 20 * * 1-5`）將於當日自動觸發 own_stack 之 H 軌**首次出單**（機制見 §2.3）。兩案皆宜在此前拍板：A 須在此前施作才「零孤兒列」；B′ 則是「此前什麼都不做」。

---

## §1 問題與授權鏈

**問題一句話**：`dgate_arena_own_stack_20/40/82` 三門（status=approved，hugo TTY 2026-07-12 親核）自開賽以來零證據列——r3 深化理解（`augur_deep_understanding_r3_20260801.md:111`）稱「horizon 與 h=5 出單結構性錯配＝現行結構下永無證據」，登錄冊裁定 W2 呈案二擇一：A supersede（判死留檔）／B′ 補多 h 出單。

**授權鏈**：Steward 指示「記錄所有問題的解決方式，之後依記錄逐項展開解決」→ 登錄冊 E1 標【呈案→Steward】→ 本檔＝呈案與證據整備（§8.1／L6.18(a)：裁決專屬 Steward，本檔不代決）。本輪作業全程唯讀（零 DDL、零寫入、零探針寫）。

**⚠ 親驗推翻登錄冊前提（本呈案最重要的一句）**：**「錯配＝永無證據」不成立、「B′ 須補出單」也不成立**——`direction_arena_candidate` 中 `own_stack_rolling` 之 spec **早已是 `horizons=[20,40,82]`、track='H'**（凍結於 2026-07-11，凍結協定 trigger 保護）。它至今零出單，唯一原因是 **H 軌=每月首個交易日出手**（`run_arena_round.py:100`），而 arena 07-15 才開賽、七月首個交易日（07-01）已過——**下一個觸發點＝2026-08-03（八月首個交易日）20:00 cron，屆時將自動首發，零 code 缺口**。E1 的真裁決題不是「要不要補出單」，而是「**要不要讓 08-03 首發發生、要不要花約三年養這三門**」（時程數學見 §2.5）。

---

## §2 現況親驗（2026-08-01 執行，全部現查）

### 2.1 三門現況（approved、未評、min_clusters=36）

```sql
SELECT gate_id, track, horizon, status, evaluated_at, approved_at::date
FROM direction_gate WHERE gate_id LIKE 'dgate_arena_own_stack%';
```
```
dgate_arena_own_stack_20 | H | 20 | approved | (null) | 2026-07-12
dgate_arena_own_stack_40 | H | 40 | approved | (null) | 2026-07-12
dgate_arena_own_stack_82 | H | 82 | approved | (null) | 2026-07-12
```
criteria（jsonb 現查）三門共同：`estimand={table: direction_arena_prediction, hcol: horizon_td, key_col: model_key, model_id: own_stack_rolling, settled_only: true}`、`min_clusters: 36`、`alpha=0.05/6`（Bonferroni）、`hac_min_lag` 2/2/4、`auto_trigger=「第一個滿足已結算 cluster ≥36 之月末自動觸發 evaluate」`、approved_by=hugo。

### 2.2 候選與帳本（spec 已含三 horizon；帳本零列）

```sql
SELECT model_key, track, status, spec->'horizons' FROM direction_arena_candidate
WHERE model_key IN ('own_stack_rolling','own_threelens_interact');
```
```
own_stack_rolling      | H | active  | [20, 40, 82]     （frozen_at 2026-07-11）
own_threelens_interact | H | retired | [20, 40, 82]     （07-25 拆彈先例，見 §3.1）
```
```sql
SELECT model_key, horizon_td, count(*) FROM direction_arena_prediction GROUP BY 1,2;
-- 8 隊全部 horizon_td=5；own_stack_rolling 零列。
-- 總量:15,344 列/已結算 4,128/已結算 cluster=2(07-15、07-16)/max(pred_date)=2026-07-31。
```

### 2.3 出單機制親讀（B′「補出單」實不存在缺口）

- `scripts/run_arena_round.py:100`：`h_fires = month_days and month_days[0] == as_of`——H 軌唯每月首個交易日出手。08-01/08-02 為週末 ⇒ **08-03 為八月首個交易日**（假設非臨時休市），`month_days=[08-03]` ⇒ `h_fires=True`。
- `run_arena_round.py:126-140`：`horizons = (spec or {}).get("horizons", [5])`，逐 h 呼叫 `adapter.predict(series, h)` 寫 ledger——**horizon 由候選 spec 資料驅動（#29b），own_stack 將以 20/40/82 各出一輪**。
- `src/augur/arena/adapters.py:160-236`：`OwnStackRolling.predict(series, horizon_td, ...)` 對任意 h 皆滾動重訓——**adapter 端 horizon-generic，零改碼**。
- `scripts/settle_arena_labels.py:122-131`：結算以 ledger 之 `horizon_td` 動態數交易日——**結算端 horizon-generic，零改碼**。
- `scripts/evaluate_direction_gate.py:88-124`：三門 estimand 直讀 `horizon_td=20/40/82` 之已結算列——**裁判端已接好**。
- cron 現查：`0 20 * * 1-5 … run_arena_daily_pipeline.py --run`（雙機械閘開:閘一 approved dgate_arena% 現=8 列、閘二 admission evaluated_pass=1 列）。

### 2.4 supersede 白名單（trigger 機械保護現況）

- `pg_trigger` 現查：`trg_direction_no_goalpost` 掛於 direction_gate、`tgenabled='O'`。
- 函式白名單（`scripts/migrate_direction_gate_ddl.py:63-69`，與 live `pg_proc.prosrc` 一致）：`approved → evaluated_pass|evaluated_fail|superseded` 合法；**superseded 為終態無出邊**；criteria 任何變更一律 RAISE。
- **approved→superseded 臂之實測先例**：`reports/augur_refreeze_0630_plan_20260725.md:16`「全部狀態轉移 ROLLBACK 實測合法（…**approved→superseded 亦在白名單**）」。

### 2.5 時程數學（B′ 之真實代價；誠實計算）

月頻出手 × `min_clusters=36`（已結算 pred_date 數）⇒ 需 **36 個月度出手全結算**。自 2026-08-03 起每月一發，第 36 發 ≈ **2029-07**；h=82 之標籤再需 82 個交易日（≈4 個日曆月）⇒ 三門全可判 ≈ **2029 年 Q4**。期間每月寫入 ≈ 3×(344 宇宙+1 TAIEX) ≈ **1,035 列/月**（帳本反回填＋不可篡改 trigger 保護，永久留存）。運算成本＝每月 3 次 OwnStackRolling 滾動重訓（本機分鐘級）；**零新 API 面**（同一班 20:00 sync，H 軌不另抓數）。

---

## §3 方案

### 3.1 A 案：supersede 三門＋retire 候選（完整拆彈；先例同構）

先例＝07-25 A3 拆彈（hugo 拍板甲′）：`own_threelens_interact` retired ＋ `dgate_a3_threelens_20/40/82` superseded；其 retire_note（DB 現查）：「…防 2026-08 首交易日自動首手早於 approve（先凍後跑紀律）;餘隊不動」——**同一個 08-03 首發機制，先例已處理過一次**。差異須誠實揭露：a3 三門當時 **preregistered 未簽核**（先凍後跑有違規之虞，拆彈=防違規）；own_stack 三門**已 approved**（08-03 首發程序上完全合法）——本案拆的不是違規風險，是 §2.5 的三年養門成本。

**操作指令全文**（拍板後執行；建議 hugo TTY 親跑，AI 依先例代跑亦合規——本操作無人簽欄位、全程受 trigger 白名單機械保護；執行前後全套驗證含於指令）：

```sql
-- ========== E1-A supersede 操作（單一交易、原子；須於 2026-08-03 20:00 前完成） ==========
-- 【前驗 1】trigger 掛載且啟用（期望 1 列、tgenabled='O'）
SELECT tgname, tgenabled FROM pg_trigger
WHERE tgrelid='public.direction_gate'::regclass AND NOT tgisinternal;

-- 【前驗 2】白名單函式源含 approved→superseded 臂（期望 t）
SELECT position('superseded' IN prosrc) > 0 AND position('approved' IN prosrc) > 0
FROM pg_proc WHERE proname='direction_gate_no_goalpost';

-- 【前驗 3】三門仍為 approved（期望 3）
SELECT count(*) FROM direction_gate
WHERE gate_id IN ('dgate_arena_own_stack_20','dgate_arena_own_stack_40','dgate_arena_own_stack_82')
  AND status='approved';

-- 【預演】同一批 UPDATE 以 ROLLBACK 乾跑（實測轉移合法、零殘留；07-25 先例手法）
BEGIN;
SET LOCAL lock_timeout = '5s';
UPDATE direction_gate
   SET status='superseded',
       note = note || ';superseded 2026-08-0X Steward 裁決(登錄冊 E1-A):月頻×min_clusters=36=判決時程約至 2029、資源不養;非證偽、非 evaluated_fail;日後真需 H 軌證據=另立新門新預註冊(supersede 不封路)'
 WHERE gate_id IN ('dgate_arena_own_stack_20','dgate_arena_own_stack_40','dgate_arena_own_stack_82')
   AND status='approved';
-- 期望 UPDATE 3
ROLLBACK;

-- 【正式施作】預演通過後，同語句改 COMMIT 收尾：
BEGIN;
SET LOCAL lock_timeout = '5s';
UPDATE direction_gate
   SET status='superseded',
       note = note || ';superseded 2026-08-0X Steward 裁決(登錄冊 E1-A):月頻×min_clusters=36=判決時程約至 2029、資源不養;非證偽、非 evaluated_fail;日後真需 H 軌證據=另立新門新預註冊(supersede 不封路)'
 WHERE gate_id IN ('dgate_arena_own_stack_20','dgate_arena_own_stack_40','dgate_arena_own_stack_82')
   AND status='approved';
-- 斷言:恰 3 列;非 3 即 ROLLBACK 停手判源

UPDATE direction_arena_candidate
   SET status='retired',
       retire_note='2026-08-0X Steward 裁決(登錄冊 E1-A):三門 supersede 連動退役——月頻 H 軌自 08-03 起之出單無對應門、不留無門觀察流;spec/門檻零變更(凍結協定);先例=own_threelens_interact 07-25'
 WHERE model_key='own_stack_rolling' AND status='active';
-- 斷言:恰 1 列（retire_note 單次寫入、trigger 保護）
COMMIT;

-- 【後驗】
SELECT gate_id, status FROM direction_gate WHERE gate_id LIKE 'dgate_arena_own_stack%';
-- 期望:3×superseded
SELECT status, retire_note IS NOT NULL FROM direction_arena_candidate WHERE model_key='own_stack_rolling';
-- 期望:retired | t
-- 【負向探針（選跑）】驗 trigger 仍武裝:BEGIN; UPDATE direction_gate SET criteria=criteria||'{}'::jsonb
--   WHERE gate_id='dgate_arena_own_stack_20'; ROLLBACK;  -- 期望 RAISE「criteria 不得變更(挪門柱)」
```

註：note 之「2026-08-0X」由執行日代入；supersede 理由句可依 Steward 措辭調整（note 欄不在 trigger 凍結集，同一 UPDATE 內寫入）。

**A-lite 子選項（列而不薦）**：只 supersede 三門、候選續 active——08-03 起每月產無門觀察列。不薦：日後若另立新門，預註冊前累積之資料屬事後選窗（先凍後跑紀律不可用），觀察流無證據價值、徒增帳本與運算。

### 3.2 B′ 案：讓 08-03 首發（零施作；真名=「不拆彈」）

**工作量親估（依 §2.3 出單處親讀）**：
| 項 | 工作量 |
|---|---|
| 出單 | **0**——spec 已 [20,40,82]、adapter/結算/裁判全 horizon-generic，08-03 20:00 cron 自動首發 |
| 必要盯場 | 08-03 21:00 後查 ledger 落列＋洩漏稽核（`train_data_max_date==pred_date`）——一次唯讀確認 |
| 選配：scoreboard 分 horizon | `settle_arena_labels.py:263-299` 現 `GROUP BY model_key` 會把 own_stack 三個 h 混進同一列命中率（僅展示層；門判據 per-horizon 不受影響）。修法＝`GROUP BY model_key, horizon_td`＋表頭加 h 欄＋`_selftest` fixture 一則，估 **10-20 行 diff、0.5-1h**；屬「計分口徑變更、變更即留痕」（該檔頭 2026-07-26 紀律），建議與首批 h>5 結算（最早 ≈08-31，h=20 結算日）前完成即可，非 08-03 前置 |
| 持續成本 | §2.5：~1,035 列/月、每月 3 次重訓分鐘級、**判決時程 ≈ 2029 Q4** |

---

## §4 選項與建議案

| 案 | 一句話 | 成本 | 判決可得性 |
|---|---|---|---|
| **A（建議）** | 三門 supersede＋候選 retire，08-03 前施作 | 一次交易、不可逆（門） | 即刻收斂；日後另立新門不封路 |
| A-lite | 只 supersede 門 | 同上＋每月無門觀察流 | 不薦（觀察流無證據價值） |
| B′ | 不動，08-03 自動首發 | ≈零工作；三年養門 | 最早 ≈2029 Q4 才可判 |

**建議：A 案**——與呈案單結論相同，但**理由修正**（呈案單原理由「B′ 增加每日 API 面與複雜度」經親驗不成立：零新 API、月頻、零 code 缺口）。修正後的理由：(1) **判決時程**——月頻×min_clusters=36 ⇒ 約 2029 Q4 才有第一個可判時點，三年間三門只是「活著的未判賭注」，對現行「一條路」推進零資訊增益；(2) **判死留檔合憲**——supersede＝廢止留檔（非 evaluated_fail、非證偽），白名單明文臂＋雙先例（a3_threelens 三列、unfreeze gate）；(3) **不封路**——若日後出現非 h=5 之投資決策需求，屆時以對齊該需求之新門另行預註冊（先凍後跑），且屆時可設計日頻 D 軌 cadence 使 36 clusters 兩個月可達，比留著月頻舊門快得多。
**若 Steward 重視「讓賭注跑完」的立場**（門已合法 approved、預註冊完整、fail 亦設計預期），B′ 為零成本合規選項——唯須接受 2029 判決時程並於 8 月底前收 scoreboard 口徑。

**證偽條件**（沿呈案單、補精確化）：A 案錯誤之訊號＝三個月內出現「非 h=5 之投資決策需求」且新門預註冊因故不可行——屆時本案「supersede 不封路」之宣稱被證偽。B′ 案錯誤之訊號＝至 2027-02（6 個月）own_stack 月度出單之早期 Brier 相對恆 0.5 基線無任何改善跡象，續養即沉沒成本謬誤。

---

## §5 風險與回滾

- **A 不可逆性（門）**：superseded 無出邊（白名單無 `superseded→*`）——「回滾」＝另立新 gate_id 重走 preregister→hugo TTY approve。候選 retire 事實上可逆（**附帶發現**：`arena_candidate_frozen` trigger 只凍身分欄與 retire_note 單寫，**status 欄無狀態機白名單**——`retired→active` 之 UPDATE 不會被拒；是否補閘屬另案，本案不擴scope）。
- **A 逾時風險**：若 08-03 20:00 前未施作，own_stack 首發寫入 ≈1,035 列後才 supersede——列不可刪（`trg_arena_pred_immutable`/`trg_arena_pred_no_backfill` 現查在掛），成為永久無門觀察列。無違規、無資料污染（append-only 誠實預測），僅帳面噪音；scoreboard 自 8 月底起會混 horizon（§3.2 修正可解）。
- **B′ 風險**：三年時程內 arena 結構若再變（如 D 軌口徑修訂），三門之 estimand 凍結不可改 ⇒ 屆時仍可能走回 supersede，白養數月；scoreboard 口徑若未修，own_stack 列自首批 h=20 結算（≈08-31）起顯示混合命中率。
- **共同**：本呈案全程唯讀，預演/施作指令皆帶 `SET LOCAL lock_timeout='5s'`（絕不排隊擋庫，#30 精神）；操作為行級 UPDATE 非 DDL，不受 3c 統一 DDL 窗約束，但仍避開 pg_dump 時段（週六 07:30 backup cron）。

## §6 驗收判準（機械可判）

**A 案**：
1. `SELECT count(*) FROM direction_gate WHERE gate_id LIKE 'dgate_arena_own_stack%' AND status='superseded'` ＝ **3**；且 `criteria_sha` 三列與施作前逐一相同（挪門柱零觸碰）。
2. `SELECT status FROM direction_arena_candidate WHERE model_key='own_stack_rolling'` ＝ `retired` 且 retire_note 非空。
3. 08-03 21:00 後：`SELECT count(*) FROM direction_arena_prediction WHERE model_key='own_stack_rolling'` ＝ **0**（若在 20:00 前完成施作）。
4. 08-03 之 `arena_pipeline.log` 顯示管線照常跑（閘一仍開：其餘 approved dgate_arena% ≥5 列）、D 軌 8 隊照常出單。

**B′ 案**：
1. 08-03 21:00 後：own_stack_rolling 於 `horizon_td∈{20,40,82}` 各 ≈345 列、`pred_date=2026-08-03`、`train_data_max_date=pred_date`（洩漏稽核零違規）。
2. 09-01 前 scoreboard 口徑修正 diff 合入（若採選配）；`settle_arena_labels.py --selftest` 全綠。

## §7 Steward 決定欄

- [ ] E1-A 同意（supersede 三門＋retire 候選；08-03 20:00 前施作；執行者＝＿＿）
- [ ] E1-A-lite（只 supersede 門）
- [ ] E1-B′（不動，讓 08-03 首發；scoreboard 口徑修正＝要／不要）
- [ ] 其他：＿＿＿＿＿＿
- 簽：＿＿＿＿（hugo）　日期：＿＿＿＿
