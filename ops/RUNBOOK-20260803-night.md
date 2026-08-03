# Runbook — 2026-08-03（週一）夜：sim 首格 ＋ run 22 全裝備首驗

> **⚠ 2026-08-03 午後更新（五項變更，覆蓋原文對應段）**
> 1. **甲案成功，今晚 watchdog 不發車**（13:10 三輸入現查 ＋ 六視角對抗驗證獨立同證）。
>    ⚠ **本節前一版寫「甲案失效、19:14 會發車」——那是錯的，已作廢。** 錯因見下方 1-c。
>    白天 audit 12:07 寫入 `attestation_result` id=11（`--audit-only`，**`passed=false`**：
>    `value_mismatch=1979`／`missing_in_db=13,342`）。今晚 19:14 之判態逐條：
>    　① `fresh_pass`（`passed` 且 1 日內）＝ **0** ⇒ 非態一
>    　② `audit_selfheal.sh` 不在跑 ⇒ 非「進行中」
>    　③ `recent_try`（24h 內任一 `daily_maintenance%` 列，**不論 passed**）＝ **1** ⇒ **態二成立**
>    `audit_watchdog.sh:159` 之條件是 `recent_try >= 1` **OR** 冷卻窗內——`recent_try` 才是主判準，
>    `TS_FILE` mtime 只是 OR 的第二支。⇒ **12:07 那筆 FAIL 本身就足以擋住發車**，
>    要到 **08-04 12:07 之後** `recent_try` 才歸零。
>    19:30 驗證：`tail -3 ~/logs/audit_watchdog.log` 應見「**冷卻中**」或「**⛔ 發車後夭折**」字樣
>    （二者 grep 可分，M-G4 已使其互斥），**不得**出現「relaunch 已送」。
>
>    **1-c. 我為什麼連錯三次（留給下次讀這份 runbook 的人）**：
>    ① 中午抄 `audit_selfheal.sh` 的參數 `--audit-all`（沒讀完旗標說明）；
>    ② 12:12 只讀了「態一＝`passed` 且 1 日內」就宣告會發車（**沒往下讀態二的完整條件**）；
>    ③ 13:10 用 `grep audit_selfheal` 檢測進程，**命令列自己含該字串**而誤報「進行中」。
>    三次的共同形狀：**看了判準的一部分就下結論**。今晚任何一步若與預期不符，
>    先把該步的判準**整段**讀完再行動。
>    〔附帶發現：`audit_watchdog.sh:152` 用 `pgrep -f 'audit_selfheal\.sh'`，
>    任何命令列含該字串的進程都會讓它誤判「進行中」。方向是 fail-safe（誤判只會不發車），
>    但診斷時要知道這件事。〕
>
>    **1-b. audit 的真正產出（比甲案重要）**：`value_mismatch=1979` 中 **1,958 筆（99%）集中在
>    `UKStockPrice` 一張表**，且其中 1,870 筆集中在**單一天**（窗 10 日，前 9 日累積 88 筆）。
>    對照：`USStockPrice` 之 `attestation_mode='dim_only'`（豁免）而 `UKStockPrice='byte'`（不豁免）
>    ——**同型兩張外國個股價格表口徑不一致**。
>    台股側 VM 僅 **6 筆**：`TaiwanStockMarketValue` 4／`TaiwanStockSecuritiesLending` 1／
>    `TaiwanStockDispositionSecuritiesPeriod` 1。**MarketValue 那 4 筆才是可能污染因子鏈的**
>    （`market_cap_log` 由它來），UK 那 1,958 筆對台股預測零貢獻。
>    ⇒ **數量大的不等於重要；看它在不在因子鏈上。**
>    處置屬 Steward（是修資料還是改口徑；**AI 不擅自把 UKStockPrice 改成豁免——那是把紅燈關掉**）。
> 2. **sim 首格不需要先開 ledger 列**——M-T1 已把 FK 焊死（`sim_run_link.iteration_uid → sim_evolution_iteration_ledger`）
>    且 runner `--apply` 會自動 `ensure_iteration_row(planned)→running`。孤兒 uid 現在是 **DB 層物理不可能**，不再靠人記得。
> 3. **`--apply` 之前置**：M-T1 ✅（今日完成）＋ M-M1／M-M2 驗收綠（`evaluate_sim_calibration.py`，午後施作中——按之前先確認其 `--selftest` rc=0）。
> 4. **17 列 pending 不用開人裁窗**——經查標的皆已不存在（q555 之 feature 已由 q556 晉升；16 列 demote 之 feature 有 7 個已 removed、3 個從未進 prodset）。
>    讓 run 22 自動標 superseded 即可，證據見 `reports/mt3_pending_disposition_evidence_20260803.md`。
> 5. **20:00 不會自動產首格**（三處親驗：crontab／unit-files／`run_arena_daily_pipeline._steps()` 皆無 sim）。20:00 讀為「anchor 檢查點」。

> **為什麼落成檔案**：三個時點各有不可補性（anchor 錯過走 catch-up 帳／run 22 是所有新機制的第一次無人看顧運轉），
> 而 AI session 可能不在場或已斷。本檔讓 hugo 可獨立完成全程；每步附「預期輸出」與「不對就停」。
> 全程零 Claude usage（#28 本地優先）。前置環境一律：`cd /home/hugo/project/augur && set -a && . ./.env && set +a`

---

## T-20:00｜anchor 實現（等 sync，不需人動作）

日常 sync 於 20:00 由 cron 觸發。**確認 anchor 到位**（08-03 收盤資料入庫）：

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && venv/bin/python scripts/run_sim_calibration_cell.py --dry-run
```

- **預期（anchor 已到）**：印出防衛鏈全綠（雙 sha → 52 檔清單 sha → kill switch）＋首格 52 檔對帳清單。
- **預期（anchor 未到）**：印「anchor 未實現（…尚未入庫；等 T+1 sync）——無事可產」＝**正常，等即可**，不是錯誤。
- **不對就停**：任一 sha 防衛紅（門判準文與指紋分家）＝治權級，停手回報，勿 --apply。

## T-21:xx｜sim 首格產 run（S-4 人工逐次觸發；勿排程）

**前置自檢**（一條，全綠才往下）：

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && venv/bin/python scripts/evaluate_sim_calibration.py --selftest >/dev/null 2>&1 && echo "M-M1/M-M2 前置 ✓" || echo "✗ 前置未綠——先問 AI，勿 --apply"
```

乾跑無誤後：

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && venv/bin/python scripts/run_sim_calibration_cell.py --apply
```

- **預期**：`mc_simulation_run` +52 列、`sim_run_link` +52 列（arm='live'）。
- **冪等證明（建議隨即跑一次）**：再跑一次 `--apply` 應為 **0 新增**。
- **不對就停**：52 檔清單 sha 不合＝凍結清單漂移，停手（勿改 sha 遷就資料）。
- 首格落地後，證據時鐘正式起算：第二格 ≈09-01、第三格 ≈10-01；K=3 齊 ≈11-03 ⇒ **T-A 首判 ≈11 月上旬**。

## T-22:5x｜run 22 前置快照（I5B 驗收基線）

run 22 會首次觸發「世代 supersede」（開新世代列前自動把同 feature 舊 pending_auto 標 superseded）。**驗收要有前基線**：

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\copy (SELECT queue_id, run_id, feature, action, queue_status FROM promotion_queue WHERE queue_status='pending_auto' ORDER BY queue_id) TO 'audits/prerun22_pending_snapshot_20260803.csv' CSV HEADER"
```

- **預期**：現有 pending_auto 全集入檔（run 21 世代）。

## T-23:00｜run 22 全自動輪（cron 自動；不需人動作）

`0 23 * * 1-5` 觸發 `run_evolution_iteration.py --run --slot-wait 10800`。本輪是**全裝備首驗**：八閘 G-SIGN／P2b 通行證（引擎寫帳本須帶證）／I5B 世代 supersede／版本鍵可比（run 21 已立 snapshot_ver=2 基準⇒本輪 gain 首次真可比）／stale-hold drain／3 特徵 prodset（含 08-02 親簽的兩顆）。

**隔日晨驗收**（或當晚結輪後）：

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && tail -20 ~/logs/twevo.log && venv/bin/python scripts/report_applygo_readiness.py | head -30
```

四項機械檢查：

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tA -c "SELECT 'run22 status='||status FROM evolution_run ORDER BY run_id DESC LIMIT 1; SELECT 'superseded 列='||count(*) FROM promotion_queue WHERE queue_status='superseded'; SELECT '本輪 pending='||count(*) FROM promotion_queue WHERE queue_status='pending_auto'; SELECT 'gain 可比='||COALESCE((SELECT gain_evidence->>'basis' FROM evolution_iteration_ledger ORDER BY opened_at DESC LIMIT 1),'(無)')"
```

- **預期**：status=succeeded／superseded 列 >0（I5B 首次生效）／pending 全屬 run 22／gain basis **不再是 incomparable**（版本鍵同版 ⇒ 首次真比較）。
- **不對就停**：出現 P2b 通行證相關的 UPDATE 遭拒（引擎寫帳本被誠實閘擋）＝補丁有漏，停手回報，勿手動繞閘。

---

## 護欄（三條，任一觸即停手待人）

1. **kill switch**：`venv/bin/python scripts/set_evolution_kill_switch.py --status`——任一 scope=halt 時引擎不跑，屬設計非故障。
2. **不繞閘**：任何「加通行證讓它過」的臨場動作一律不做（那是把閘關掉）。
3. **人簽欄**：`promoted_by`／`approved_by`／`decided_by`／`signed_by` 一律 hugo 親打，AI 不代填、不代貼。

## 若要停止今晚一切自動作業

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && venv/bin/python scripts/set_evolution_kill_switch.py --set halt --scope global --by hugo --reason "<理由>"
```

（halt 後引擎照跑但不採用結果；解除＝同指令 `--set clear`。）
