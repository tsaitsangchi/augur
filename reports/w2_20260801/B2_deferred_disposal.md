# [DRAFT 呈案] B2｜evolution_deferred_work 積壓 7 筆逐筆處置 SQL（未經拍板不得施作）

> **狀態**：DRAFT 呈案——W2 批（登錄冊 2026-08-01 §3 B2）；**未經 Steward 拍板不得施作**。
> **L6.18(c) 自我利益揭露**：本案處置對象含 AI 自身回歸鎖測試所造成之 4 筆探針污染（#7–#10），AI 既是污染製造者亦是本呈案草擬者；處置方式、標記字串與施作時點全由 Steward 拍板，AI 僅備料呈案。
> **撰寫**：2026-08-01 15:21（六）；現況數字全為當刻親驗，施作前請依 §6 重驗。

---

## §1 問題與授權鏈

**問題**：`evolution_deferred_work`（heavy-slot 積壓帳本）現有 **7 筆未清**（cleared_at IS NULL）。其中 4 筆為 07-31 21:01:37 同秒之回歸鎖測試探針污染（非真積壓）、3 筆為真夜輪 defer 但其標的輪已閉帳（defer 目的已消滅）。**drain 補跑器對這 7 筆的機械判定全部是 rerun**（§2.4 親驗）——若 B3 重啟 timer 而不先清帳，每 30 分即嘗試 spawn 一整輪 TWEVO（單輪實證燒道 13.3 小時，§2.3），且 4 筆探針也會被當真積壓補跑。

**授權鏈**：
- 呈案本身＝解法登錄冊 `reports/augur_problem_solution_register_20260801.md` §3 B2（「Steward 拍板後執行」，分派 W2）＋裁決建議單 `reports/augur_steward_adjudication_sheet_20260801.md` B2 條（建議：探針 4 筆標 `test-artifact-20260731`；#4/#5/#11 標 superseded 各附理由；**全標不刪**）。
- 施作授權＝Steward 於裁決單圈選「**B2-同意**」（或改採他案）後方可執行；建議由 **hugo 親跑** §3 SQL（單一交易、UPDATE-only）；若指定 AI 執行，屬 #6/#26 之一次性明示授權（範圍＝§3 全文 SQL 一次、不含其他寫入）。
- 波次固定序（登錄冊 CR4）：**B2 → B1-apply → B3**；本案為第一步。

---

## §2 現況親驗（2026-08-01 15:21；全部唯讀）

### 2.1 帳本全貌（9 列、7 筆未清）

```sql
SELECT defer_id, axis, step_key, requested_at, cleared_at, cleared_by
  FROM evolution_deferred_work ORDER BY defer_id;
```
```
 defer_id | axis |        step_key         |         requested_at          |          cleared_at           |    cleared_by
----------+------+-------------------------+-------------------------------+-------------------------------+------------------
        2 | tw   | run_evolution_iteration | 2026-07-27 17:13:49.539666+08 | 2026-07-31 09:43:44.662868+08 | drain:superseded
        3 | lai  | eval_local_model        | 2026-07-27 20:47:22.323879+08 | 2026-07-31 09:43:44.696619+08 | drain:superseded
        4 | tw   | run_evolution_iteration | 2026-07-28 23:00:02.412108+08 |                               |
        5 | tw   | run_evolution_iteration | 2026-07-29 23:00:02.704935+08 |                               |
        7 | tw   | run_evolution_iteration | 2026-07-31 21:01:37.705825+08 |                               |
        8 | tw   | run_evolution_iteration | 2026-07-31 21:01:37.763654+08 |                               |
        9 | tw   | run_evolution_iteration | 2026-07-31 21:01:37.91065+08  |                               |
       10 | tw   | run_evolution_iteration | 2026-07-31 21:01:37.960502+08 |                               |
       11 | tw   | run_evolution_iteration | 2026-08-01 02:00:01.570468+08 |                               |
```
- 與登錄冊相符：#2/#3 已於 07-31 09:43 由 drain 憑機械佐證清訖；未清＝#4/#5/#7/#8/#9/#10/#11 共 7 筆；`max(defer_id)=11, total=9, open=7`。
- **#6 缺號**＝`heavy_slot` selftest 之 `selftest_probe` 探針「真插一列再刪」自刪所致（`src/augur/core/heavy_slot.py:275` DELETE WHERE step_key='selftest_probe'）；非帳本被竄。
- 本表**無任何 trigger**（`pg_trigger` 親查 0 列）→ 平 UPDATE 可行、無需 GUC 通行證；但也代表本帳本尚無 DELETE 防護（B4 射程之外之觀察，非本案處置）。

### 2.2 未清 7 筆之 detail（探針指紋）

```
 #4  {"at":"2026-07-28T23:00:02","owner":"tw_iteration","steps":["I0".."I9"]}
 #5  {"at":"2026-07-29T23:00:02","owner":"tw_iteration","steps":["I0".."I9"]}
 #7  {"at":"2026-07-31T21:01:37","owner":"tw_iteration","steps":["I0".."I9"],"waited_seconds":0}
 #8  {"at":"2026-07-31T21:01:37","owner":"tw_iteration","steps":["I3"],"waited_seconds":0}
 #9  {"at":"2026-07-31T21:01:37","owner":"tw_iteration","steps":["I0".."I9"],"waited_seconds":0}
 #10 {"at":"2026-07-31T21:01:37","owner":"tw_iteration","steps":["I3"],"waited_seconds":0}
 #11 {"at":"2026-08-01T02:00:01","owner":"tw_iteration","steps":["I0".."I9"],"waited_seconds":10800.0}
```
探針 4 筆（#7–#10）之機械指紋：**同一秒內四筆（跨距 255ms）、`waited_seconds=0`、其中兩筆僅 `steps:["I3"]`**。真 cron defer 恆為週間 23:00 起跑、全步序 I0–I9、`--slot-wait 10800`（#11 之 `waited_seconds:10800` 即是；cron 親驗：`0 23 * * 1-5 … run_evolution_iteration.py --run --slot-wait 10800`）。21:01 非任何排程時點＝07-31 晚回歸鎖測試污染（r3 報告同判）。

### 2.3 「補跑」選項已無標的：r01 已閉帳（**新事實，登錄冊寫作時未有**）

```sql
SELECT iteration_uid, axis, status, opened_at, closed_at
  FROM evolution_iteration_ledger WHERE axis='tw' AND opened_at >= '2026-07-28';
```
```
 tw-20260728-r01 | tw | failed | 2026-07-28 23:00:02.330539+08 | 2026-08-01 06:47:10.221009+08
```
- **07-28 之後全表無任何 tw `succeeded` 輪** → drain 之 (a) superseded 機械佐證對 #4/#5/#11 **不存在**，機械路只剩 rerun。
- `tw-20260728-r01`：與 #4 同一 cron tick 開帳（23:00:02.33 開帳、23:00:02.41 落 defer）；累積 **33 個 step attempt**；**已於 2026-08-01 06:47:10 閉帳**，`status='failed'`、`closed_by='run_evolution_iteration(執行層)'`、`stop_reason='步驟失敗:I3,I3(fail-closed,不前進)'`。
- **末段 attempt（07-31 17:21 起）I0–I9 全部 rc=0**（I3 於 07-31 18:19→08-01 04:11 跑 10 小時、rc=0；I4–I9 於 08-01 06:46–06:47 全 rc=0）——閉帳 failed 係計入歷史 I3 敗次；**末次判準（A5）之重裁屬另案、動已結 r01 列＝Steward**，本案不碰 ledger。
- 07-31 17:21 之補跑正是 drain timer 最後一次發車（stamp 檔 `~/.local/share/systemd/timers/stamp-augur-drain-deferred.timer` mtime = Jul 31 17:21）撿起 #4 所 spawn：**單筆舊積壓補跑燒道 13.3 小時（17:21→06:47），並把 07-31 23:00 夜輪餓死 3 小時而產生 #11**（`~/logs/twevo.log` 尾段親驗：「已有進行中之輪 tw-20260728-r01(26 步已跑)…heavy slot 有界等待中(上限 10800s)…⚠ 已寫 evolution_deferred_work;rc=75」）——「舊積壓補跑餓死當夜新輪」之白燒樣態實證。

### 2.4 drain 現行機械判定：7 筆**全 rerun**（危險所在）

```
$ venv/bin/python scripts/drain_deferred_work.py --check        # 2026-08-01 15:2x
heavy slot 現況：持有中=(空閒)｜死亡未釋放殘帳 2 筆
未清積壓：7 筆
  #4 … → **rerun**｜無涵蓋佐證 → 補跑（rc=0 才清）
  #5 … → **rerun**｜…
  #7 … → **rerun**｜…    #8 … → **rerun**｜…    #9 … → **rerun**｜…    #10 … → **rerun**｜…
  #11 … → **rerun**｜…
```
（另觀察：heavy slot「死亡未釋放殘帳 2 筆」＝slot ledger 孤兒紀錄，非本案射程，留紀錄。）

### 2.5 環境現況

- heavy slot 空閒（`pg_locks` advisory 0 列）；無 drain / run_evolution_iteration 行程在跑（ps 親驗）。
- drain timer：runtime 已停（stamp 07-31 17:21 後未再前進；同目錄其他 timer 08-01 均有新 stamp），**但 enable symlink 仍在**（`~/.config/systemd/user/timers.target.wants/augur-drain-deferred.timer` 存在）＋`Persistent=true` → **⚠ 重開機即自動復活**。詳見 B3 呈案 §2；此為 B2 應盡速施作之理由之一。
- TWEVO cron 僅週間（`0 23 * * 1-5`）：今（六）明（日）晚**無**新 tick；下一 tick＝**08-03（一）23:00**。B2 施作窗（本週末）內不會有新 defer 干擾；若拖過 08-03 23:00，可能出現 defer_id>11 之新列（§3 斷言已防呆——新列不在處置範圍、亦不會被誤標）。

---

## §3 方案：逐筆處置 SQL 全文（UPDATE-only、單一交易、全標不刪）

處置依裁決建議單 B2 條：探針 4 筆標 `cleared_by='test-artifact-20260731'`；#4/#5/#11 標 superseded（`cleared_by='ruling:superseded'`，非人名；理由逐筆入 detail）。每筆 WHERE 同時釘 `defer_id`＋`requested_at` 精確微秒值＋`cleared_at IS NULL`（跨機防漂移、冪等防重跑）。

```sql
-- ============================================================================
-- B2：evolution_deferred_work 積壓 7 筆逐筆處置（呈案 2026-08-01）
-- 前提：Steward 已圈選「B2-同意」。建議 hugo 親跑：
--   psql -h 127.0.0.1 -p 5432 -U augur -d augur -f b2_disposal.sql
-- 性質：UPDATE-only、無 DDL、全標不刪（#12）；斷言失敗即整包 ROLLBACK。
-- ============================================================================
BEGIN;
SET LOCAL lock_timeout = '5s';

-- ── (i) 探針 4 筆：07-31 21:01:37 同秒（跨距 255ms）、waited_seconds=0、
--        #8/#10 僅 steps=["I3"]；真 cron 恆週間 23:00 全步序＋slot-wait 10800
--        ＝07-31 晚回歸鎖測試探針污染，非真積壓 ──────────────────────────────
UPDATE evolution_deferred_work SET cleared_at = now(), cleared_by = 'test-artifact-20260731',
       detail = detail || jsonb_build_object('disposition','test-artifact','ruling','B2-20260801',
         'why','07-31 21:01:37 同秒四筆之一(waited_seconds=0,全步序)=回歸鎖測試探針污染;真 cron 恆 23:00 起跑且帶 slot-wait 10800')
 WHERE defer_id = 7  AND requested_at = '2026-07-31 21:01:37.705825+08' AND cleared_at IS NULL;

UPDATE evolution_deferred_work SET cleared_at = now(), cleared_by = 'test-artifact-20260731',
       detail = detail || jsonb_build_object('disposition','test-artifact','ruling','B2-20260801',
         'why','07-31 21:01:37 同秒四筆之一(waited_seconds=0,僅 steps=[I3]=非真夜輪形狀)=回歸鎖測試探針污染')
 WHERE defer_id = 8  AND requested_at = '2026-07-31 21:01:37.763654+08' AND cleared_at IS NULL;

UPDATE evolution_deferred_work SET cleared_at = now(), cleared_by = 'test-artifact-20260731',
       detail = detail || jsonb_build_object('disposition','test-artifact','ruling','B2-20260801',
         'why','07-31 21:01:37 同秒四筆之一(waited_seconds=0,全步序)=回歸鎖測試探針污染')
 WHERE defer_id = 9  AND requested_at = '2026-07-31 21:01:37.91065+08'  AND cleared_at IS NULL;

UPDATE evolution_deferred_work SET cleared_at = now(), cleared_by = 'test-artifact-20260731',
       detail = detail || jsonb_build_object('disposition','test-artifact','ruling','B2-20260801',
         'why','07-31 21:01:37 同秒四筆之一(waited_seconds=0,僅 steps=[I3]=非真夜輪形狀)=回歸鎖測試探針污染')
 WHERE defer_id = 10 AND requested_at = '2026-07-31 21:01:37.960502+08' AND cleared_at IS NULL;

-- ── (ii) #4：07-28 夜輪 tick；同 tick 開帳之輪 tw-20260728-r01 已於 08-01 06:47:10
--         閉帳（status=failed;末段 attempt I0-I9 全 rc=0,末次判準另案 A5）。
--         輪已結：補跑不能補回 07-28 夜、只會另開新輪＝defer 目的已消滅 ──────
UPDATE evolution_deferred_work SET cleared_at = now(), cleared_by = 'ruling:superseded',
       detail = detail || jsonb_build_object('disposition','superseded','ruling','B2-20260801',
         'why','標的=推進 07-28 23:00 tick 所開之輪 tw-20260728-r01;該輪已於 2026-08-01 06:47:10 閉帳(status=failed,stop_reason=步驟失敗:I3,I3;末段 attempt I0-I9 全 rc=0,末次判準之重裁屬 A5 另案)。輪已結,補跑只會另開新輪,defer 目的已消滅',
         'evidence','evolution_iteration_ledger.iteration_uid=tw-20260728-r01 closed_at=2026-08-01 06:47:10.221009+08')
 WHERE defer_id = 4  AND requested_at = '2026-07-28 23:00:02.412108+08' AND cleared_at IS NULL;

-- ── (iii) #5：07-29 夜輪 tick＝續跑當時 open 之同一輪 r01 被 slot 擋；標的同上已閉帳 ──
UPDATE evolution_deferred_work SET cleared_at = now(), cleared_by = 'ruling:superseded',
       detail = detail || jsonb_build_object('disposition','superseded','ruling','B2-20260801',
         'why','標的=續跑當時 open 之輪 tw-20260728-r01(07-29 tick 到達時該輪仍 open,slot 被佔而 defer);該輪已於 2026-08-01 06:47:10 閉帳。輪已結,defer 目的已消滅',
         'evidence','evolution_iteration_ledger.iteration_uid=tw-20260728-r01 closed_at=2026-08-01 06:47:10.221009+08')
 WHERE defer_id = 5  AND requested_at = '2026-07-29 23:00:02.704935+08' AND cleared_at IS NULL;

-- ── (iv) #11：07-31(五) 23:00 夜輪 tick,有界等滿 10800s 後落帳(twevo.log 佐證);
--          佔道者=r01 之補跑 I3(07-31 18:19→08-01 04:11)。r01 已閉帳;
--          週間 cron 08-03(一) 23:00 自然接續開新輪＝defer 目的已消滅 ─────────
UPDATE evolution_deferred_work SET cleared_at = now(), cleared_by = 'ruling:superseded',
       detail = detail || jsonb_build_object('disposition','superseded','ruling','B2-20260801',
         'why','07-31 23:00 tick 等滿 10800s 落帳;佔道者=舊積壓 #4 補跑之 r01 I3(18:19→04:11)。r01 已於 08-01 06:47:10 閉帳;下一週間 tick 08-03(一) 23:00 自然開新輪,defer 目的已消滅(補跑反會與之搶道)',
         'evidence','evolution_iteration_ledger.iteration_uid=tw-20260728-r01 closed_at=2026-08-01 06:47:10.221009+08; cron=0 23 * * 1-5 run_evolution_iteration.py --run --slot-wait 10800')
 WHERE defer_id = 11 AND requested_at = '2026-08-01 02:00:01.570468+08' AND cleared_at IS NULL;

-- ── 斷言：任一不符 → EXCEPTION → 整包 ROLLBACK（射程釘 defer_id<=11,
--    不碰施作時點後可能新生的列） ─────────────────────────────────────────────
DO $$
BEGIN
  IF (SELECT count(*) FROM evolution_deferred_work WHERE defer_id <= 11) <> 9 THEN
    RAISE EXCEPTION 'B2 斷言失敗:defer_id<=11 應恰 9 列(全標不刪)——整包回滾';
  END IF;
  IF (SELECT count(*) FROM evolution_deferred_work WHERE defer_id <= 11 AND cleared_at IS NULL) <> 0 THEN
    RAISE EXCEPTION 'B2 斷言失敗:defer_id<=11 仍有未清列——整包回滾';
  END IF;
  IF (SELECT count(*) FROM evolution_deferred_work
       WHERE defer_id IN (7,8,9,10) AND cleared_by = 'test-artifact-20260731') <> 4 THEN
    RAISE EXCEPTION 'B2 斷言失敗:探針 4 筆標記不齊——整包回滾';
  END IF;
  IF (SELECT count(*) FROM evolution_deferred_work
       WHERE defer_id IN (4,5,11) AND cleared_by = 'ruling:superseded') <> 3 THEN
    RAISE EXCEPTION 'B2 斷言失敗:superseded 3 筆標記不齊——整包回滾';
  END IF;
END $$;

COMMIT;
```

**施作後若已過 08-03 23:00 而出現 defer_id>11 之新列**：新列不在本案射程、留給 drain 機械路（或 B3 之 stale-hold）處置；斷言不會誤傷。

---

## §4 選項與建議案

| 案 | 內容 | 評註 |
|---|---|---|
| **甲【建議】** | 全 7 筆本批處置：#7–#10 標 `test-artifact-20260731`；#4/#5/#11 標 `ruling:superseded` 各附理由（§3 全文） | 與裁決建議單 B2 條一致；帳本一次歸零、B3 重啟零風險 |
| 乙 | 僅清探針 4 筆；#4/#5/#11 留給 drain rerun | **不建議**：r01 已閉帳（§2.3 新事實），rerun 不能補回原夜、只會另開新輪且每筆潛在燒道 10h+；#11 之 rerun 會與 08-03 cron 搶道。登錄冊「#4/#5 依 drain 補跑或標 superseded」二擇一在 r01 閉帳後只剩 superseded 一路合理 |
| 丙 | 全 7 筆 DELETE | **否決**：違「全標不刪」（#12 帳本不可竄）；且 `verify_evolution_acceptance` A8 以 count(*) 驗 defer 機制曾落帳 |
| cleared_by 字串 | 建議 `ruling:superseded`（與機器之 `drain:superseded` 同構、可 grep 區分人裁批次；ruling 號在 detail）；備選 `ruling:B2-20260801` | 不用人名（登錄冊明文）；不冒用 `drain:*`（那是機器自動路之誠實標記） |

**證偽條件**（裁決建議單原文）：若 drain 重啟後仍撿起本批任何一筆重跑 ⇒ 標記謂詞沒生效，回頭檢討（機械檢法見 §6-5）。

---

## §5 風險與回滾

- **風險極小**：UPDATE-only、無 DDL、`SET LOCAL lock_timeout='5s'` 絕不排隊；表無 trigger、無消費端解析 cleared_by（週報不讀本表，grep 親驗；A8 只 count 全表列數，不受影響）；WHERE 釘微秒級 requested_at＋`cleared_at IS NULL`，重複執行為 no-op（0 列 → 斷言仍過）。
- **主要殘餘風險**：施作前若重開機，drain timer 自動復活（enabled＋Persistent）並開始 rerun ——**此為盡速施作本案之理由**；臨時保險＝hugo 可先 `systemctl --user disable augur-drain-deferred.timer`（B3 重啟時再 enable --now）。
- **回滾 SQL**（留檔備用；撤銷須另附理由）：
```sql
BEGIN; SET LOCAL lock_timeout = '5s';
UPDATE evolution_deferred_work
   SET cleared_at = NULL, cleared_by = NULL,
       detail = detail || jsonb_build_object('rollback','B2-20260801 撤銷(理由:____)','rolled_back_at', now()::text)
 WHERE defer_id IN (4,5,7,8,9,10,11)
   AND cleared_by IN ('test-artifact-20260731','ruling:superseded');
COMMIT;
```
（detail 之 disposition 痕跡不抹除——回滾本身也留痕，#12。）

---

## §6 驗收判準（機械可判；施作後即跑）

```sql
-- 1. 全標不刪：恰 9 列
SELECT count(*) = 9 AS ok FROM evolution_deferred_work WHERE defer_id <= 11;
-- 2. 歸零：defer_id<=11 未清 0 筆
SELECT count(*) = 0 AS ok FROM evolution_deferred_work WHERE defer_id <= 11 AND cleared_at IS NULL;
-- 3. 探針 4 筆
SELECT count(*) = 4 AS ok FROM evolution_deferred_work WHERE cleared_by = 'test-artifact-20260731';
-- 4. superseded 3 筆且各有 evidence
SELECT count(*) = 3 AS ok FROM evolution_deferred_work
 WHERE defer_id IN (4,5,11) AND cleared_by = 'ruling:superseded' AND detail ? 'evidence';
```
5. `venv/bin/python scripts/drain_deferred_work.py --check` 印「**未清積壓：0 筆**」（若已有 08-03 後新列則僅列新列、不含 #4–#11）。
6. （B3 重啟後一週）`journalctl --user -u augur-drain-deferred.service` 中不得出現任何「#4…#11 → 補跑」字樣（證偽條件之機械檢法）。

---

## §7 Steward 決定欄

（留白——圈選格式：`B2-同意` / `B2-改採____`；cleared_by 字串若改採他值請一併批註）
