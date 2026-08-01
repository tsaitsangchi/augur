# [DRAFT 呈案] C2——attestation 掛回 watchdog：DB 三態機＋FinMind 放量節奏（未經拍板不得施作）

> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，所修對象（watchdog 假綠）正是監督 AI/自動鏈產出之機制；本檔一切現況數字附現查指令可獨立複驗，FinMind 放量節奏之裁決專屬 Steward。
> 呈案日 2026-08-01（W2 批）；設計 SSOT＝`reports/augur_problem_solution_register_20260801.md` §3-C2＋`reports/augur_steward_adjudication_sheet_20260801.md` 三-C2。

## §1 問題與授權鏈

**問題**：raw 資料真實性唯一機械證據鏈（attestation）已斷 16 天而看門狗渾然不覺——`audit_watchdog.sh` 以「log 末行閂鎖」判態（`~/audit_retry.log` 最後一條 `attestation：` 行），該行凍結於 **2026-07-15 15:46 的 PASS**；此後 07-16/07-24/07-25 共 6 次 attest 走 session 手動路徑只寫 DB 不寫該 log，其中**最新一次（07-25 18:14）FAIL**。watchdog 每 30 分讀舊 log 宣「已綠 ✓」至今（今日 14:52 仍然），**永不再發車**。後果鏈：`validation_evidence` E1（gate sql＝「attestation_result 最近一列 PASS 且 ≤2 日」）恆紅、E1 紅燈永遠修不好（r3 §八 佇列 #3）。

**授權鏈**：登錄冊 C2（W2 呈案項）「呈案→裁（API 放量節奏）」；裁決呈案單建議案＝「watchdog 改 DB 三態機（無 1 日內 PASS 才發車）、6h 牆鐘、FinMind 沿用既有 0.7s throttle＋探測閘」，證偽條件「掛回後一週內撞 403 ⇒ 節奏過密，改 12h」。本檔＝親讀現行實作後之逐檔 diff 計畫＋節奏選項。施作＝拍板後 AI 改碼、hugo 過目；**零 systemd 單元變更**（timer/service 檔不動，見 §3.3）。

## §2 現況親驗（2026-08-01 15:0x 現查）

### 2.1 現行閂鎖實作（親讀）

- `~/.config/systemd/user/augur-audit-watchdog.timer`：`OnBootSec=5min / OnUnitActiveSec=30min / Persistent=true`；service `ExecStart=/usr/bin/bash /home/hugo/project/augur/audit_watchdog.sh`（oneshot、WorkingDirectory=repo 根）。timer 存活證據：`~/audit_watchdog.log` 每 ~30 分一條、最新 `08-01 14:52`（不經 systemctl 查詢即可證）。
- `audit_watchdog.sh:16-25`：`grep -E 'attestation：' "$LOG" | tail -1` → `*"✅ PASS"*` 即宣綠 exit；`*"❌ FAIL"*` 終態不 relaunch。**判態來源＝log 末行，且 FAIL 為永久閂鎖**。
- `audit_watchdog.sh:28-38`：未綠時查 `pgrep audit_selfheal` ＋ log 靜默 >45min 才 relaunch（`setsid nohup flock -n /tmp/augur_audit.lock ...`，**無牆鐘上限**）。
- `audit_selfheal.sh`：最小探測（#25 單股單日）→ 通了才 `FINMIND_MIN_INTERVAL=0.7 ... daily_maintenance.py --audit-days 14 --audit-all --heal`（:28）；rc=0 綠收工／rc=2 對帳紅終態 exit／rc=3 未完整休 30 分重試，至多 48 輪（=24h）。

### 2.2 假綠實證（log vs DB 分家）

```
ls -la ~/audit_retry.log     → mtime Jul 15 15:46（log 末條 attestation＝✅ PASS，即 DB id=2 那次）
tail -1 ~/audit_watchdog.log → 「08-01 14:52 watchdog: audit 已綠 ✓(attestation PASS)、無需動作」
```

```sql
SELECT id, run_at, driver, passed FROM attestation_result ORDER BY run_at;
--  2 | 2026-07-15 15:46 | daily_maintenance --audit-only --heal | t   ← log 知道的最後一次
--  3 | 2026-07-16 15:04 | 同上                                  | f
--  4 | 2026-07-16 15:43 | 同上                                  | t   ← 全帳本最後一次 PASS(16 天前)
--  5 | 2026-07-24 10:34 | daily_maintenance --heal              | f
--  6 | 2026-07-24 13:15 | daily_maintenance --heal              | f
--  7 | 2026-07-25 17:07 | daily_maintenance --audit-only --heal | f
--  8 | 2026-07-25 18:14 之前後三次 07-25 皆 f                    ← 最新現況=FAIL、其後 7 天零 attest
SELECT max(run_at) FROM attestation_result WHERE passed;  -- 2026-07-16 15:43:14+08
```

E1 現況：`status='red'`、`last_verified_at=2026-08-01 13:14`、`machine_note='斷言為假'`（今日 --run 如實紅）。旁證：`attestation_result` trigger＝0（無 honesty 閘，B4 相鄰債，本案不擴）；`automation_action_log`／`authorization_grant` 表**不存在於 live DB**（`to_regclass` 雙 f）——發車留痕暫仍走文字 log，結構化留痕待該遷移另案。

### 2.3 執行環境現況

- selfheal 未在跑（pgrep 無）、`/tmp/augur_audit.lock` 不存在——發車道路是空的。
- crontab 無任何 attest 排程行（親讀全量 crontab；attest 的唯一自動入口就是本 watchdog timer）。
- FinMind throttle 現值（親讀 `src/augur/ingestion/finmind.py`）：`MIN_INTERVAL` 預設 **0.9**（:42，env `FINMIND_MIN_INTERVAL` 可覆寫；selfheal :28 用 **0.7**＝hugo 2026-07-14 拍板實驗值）；`QUOTA_COOLDOWN=1800`（:45，403 固定冷卻）；`QUOTA_HEADROOM=200`／`QUOTA_METER_EVERY=120`／`QUOTA_POLL=150`（:51-53，主動額度閘讀錶暫停機制）。探測閘＝selfheal 之 #25 最小探測，本案不動。

## §3 方案

### 3.1 `audit_watchdog.sh` 三態機改寫（逐檔 diff 計畫）

**保留**：檔頭矩陣形制、`cd "$(dirname "$0")"`（:10）、WLOG/LOG 變數（:11-12）、selfheal 存活觀察（:28-34 之 pgrep＋logage，降為狀態②之一部）、flock 單例（:38）。
**替換**：:15-25（log 末行判態）→ DB 三態機；:36-40（發車）→ 加 `timeout -k 60 21600` 牆鐘＋dispatch 時戳檔。完整提案全文（拍板後整檔覆寫，行號對映如上）：

```bash
#!/usr/bin/env bash
# 🎯 audit 監看看門狗 — 每 30 分判態;判態改讀 DB 帳本 attestation_result(三態機),log 只作進行中觀察。
#    無 1 日內 PASS 且非進行中/冷卻中 → relaunch selfheal(6h 牆鐘)。DB 讀不到=誠實記錄退出(不宣綠、不盲發車)。
# 由 systemd timer augur-audit-watchdog.timer 每 30 分觸發。全本地零 usage(1 次 psql+pgrep)。
# 設計(C2 2026-08-01):log 末行閂鎖假綠實證——末行 PASS 凍於 07-15、DB 最新 07-25 FAIL,watchdog 宣綠 17 天。
# 執行指令矩陣:
#   bash audit_watchdog.sh          # 跑一次檢查(timer 每 30 分自動呼叫;手動亦可)
cd "$(dirname "$0")" || exit 1
LOG="$HOME/audit_retry.log"
WLOG="$HOME/audit_watchdog.log"
TS_FILE="/tmp/augur_audit_dispatch.ts"
COOLOFF_H=24        # 發車冷卻(小時;Steward 拍板值——見呈案 §4,403 證偽時第一調整旋鈕)
ts=$(date '+%m-%d %H:%M')

# ① DB 判態:1 日內 PASS?/冷卻窗內已試?/最新 verdict?(driver 過濾=E1 gate 同口徑)
set -a; . ./.env 2>/dev/null; set +a
row=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "
  SELECT
    (SELECT count(*) FROM attestation_result WHERE driver LIKE 'daily_maintenance%'
       AND passed AND run_at > now() - interval '1 day'),
    (SELECT count(*) FROM attestation_result WHERE driver LIKE 'daily_maintenance%'
       AND run_at > now() - interval '${COOLOFF_H} hours'),
    COALESCE((SELECT (CASE WHEN passed THEN 'PASS' ELSE 'FAIL' END)||'@'||to_char(run_at,'MM-DD HH24:MI')
       FROM attestation_result WHERE driver LIKE 'daily_maintenance%'
       ORDER BY run_at DESC LIMIT 1),'無紀錄')" 2>/dev/null)
if [ -z "$row" ]; then
  echo "$ts watchdog: ⚠ DB 不可讀——不判態、不發車(fail-safe 雙向:不宣綠、不盲放量)" >> "$WLOG"; exit 0
fi
fresh_pass=$(echo "$row" | cut -d'|' -f1)
recent_try=$(echo "$row" | cut -d'|' -f2)
last_verdict=$(echo "$row" | cut -d'|' -f3)

# 態一:綠(1 日內 PASS)→ 無需動作
if [ "$fresh_pass" -ge 1 ]; then
  echo "$ts watchdog: audit 已綠 ✓(DB:1 日內 PASS;最新 $last_verdict)" >> "$WLOG"; exit 0
fi

# 態二:進行中或冷卻中 → 觀察不動作(FAIL 不再是永久閂鎖;冷卻窗防 rc=2 終態重試風暴 #24)
alive=$(pgrep -f 'audit_selfheal\.sh' | head -1)
if [ -n "$alive" ]; then
  logage=$(( $(date +%s) - $(stat -c %Y "$LOG" 2>/dev/null || echo 0) ))
  echo "$ts watchdog: 進行中(selfheal pid $alive、log ${logage}s 前更新;最新 $last_verdict)" >> "$WLOG"; exit 0
fi
tsage=$(( $(date +%s) - $(stat -c %Y "$TS_FILE" 2>/dev/null || echo 0) ))
if [ "$recent_try" -ge 1 ] || { [ -f "$TS_FILE" ] && [ "$tsage" -lt $((COOLOFF_H*3600)) ]; }; then
  echo "$ts watchdog: 冷卻中(最新 $last_verdict;${COOLOFF_H}h 窗內已試,不重複發車)" >> "$WLOG"; exit 0
fi

# 態三:過期(無 1 日內 PASS、無進行中、冷卻已過)→ 發車(flock 守單例;6h 牆鐘)
echo "$ts watchdog: ⚠ 過期(最新 $last_verdict、無 1 日內 PASS)→ relaunch(timeout 6h)" >> "$WLOG"
touch "$TS_FILE"
setsid nohup timeout -k 60 21600 flock -n /tmp/augur_audit.lock bash "$PWD/audit_selfheal.sh" >/dev/null 2>&1 < /dev/null &
disown 2>/dev/null || true
echo "$ts watchdog: relaunch 已送(flock 守單例、dispatch 時戳=$TS_FILE)" >> "$WLOG"
```

設計要點：
- **雙冷卻來源**：DB `recent_try`（涵蓋 hugo 手動 attest——手動跑過就不重複燒 API）OR 時戳檔（涵蓋「探測一直失敗、6h 牆鐘殺掉、attestation_result 零新列」情境——否則下一 tick 會立即再發車＝探測風暴）。
- **FAIL 語意變更（明標）**：現行「FAIL 終態永不 relaunch」→「FAIL 後冷卻 `COOLOFF_H` 再自動試一輪」。理由：對帳窗每日滾動（--audit-days 14），昨日之紅今日可能自癒（07-16 當日 f→t 實證）；永久閂鎖則重演本次 16 天斷鏈。連敗斷路器見 §4 選配。
- **1 日 PASS 窗 × E1 之 2 日 gate 窗**：發車判準比 gate 過期判準早 1 天——正常運作下 E1 永不掉紅（PASS 每日刷新、gate 看 2 日）。
- `timeout -k 60 21600`：先 SIGTERM、60s 後 SIGKILL；selfheal 內層 daily_maintenance 有自己的 45min 靜默看門狗，此為外層總量閘（bound 探測迴圈：現行 48×30min=24h → 上限 6h/輪）。

### 3.2 `audit_selfheal.sh` diff（僅節奏旋鈕，依 §4 拍板結果二擇一）

- 甲（沿用拍板實驗值）：**:28 不動**（`FINMIND_MIN_INTERVAL=0.7`）。
- 乙（退保守）：:28 `FINMIND_MIN_INTERVAL=0.7` → `0.9`（=finmind.py 已驗證預設；:23-24 註解同步改）。
- 兩案皆不動：最小探測閘（:11-20）、rc 三態（:40-51）、48 輪上限（外層另有 6h 牆鐘）。

### 3.3 systemd／cron：**零變更**

timer/service 檔不改（ExecStart 指向同一腳本路徑）、不需 daemon-reload、不新增 cron 行——自動鏈長、人類介入點數、否決可達性、揭露比例四項**皆不弱化**（發車頻率上限反而從「log 靜默即可再發」收緊為「冷卻窗一輪」）。

## §4 選項與建議案（FinMind 放量節奏＝Steward 專屬裁決）

| 旋鈕 | 甲 | 乙 | 丙 | 建議 |
|---|---|---|---|---|
| 發車冷卻 COOLOFF_H | **24h**（每日至多一輪 attest API 負載；與「無 1 日內 PASS」自然對齊） | 12h（收斂快一倍、API 面加倍） | 0（嚴格照裁決單字面「無 1 日內 PASS 才發車」；rc=2 終態後 30 分即再試＝#24 重試風暴反例） | **甲 24h**。證偽（裁決單原文改寫）：掛回後一週內撞 403 → 節奏過密，COOLOFF_H 調 12→48…即「加大」；若一週內 E1 連續紅且每輪 FAIL 原因相同 → 冷卻自動試無意義，改採連敗斷路器 |
| throttle | **0.7s**（selfheal 現值、hugo 07-14 拍板實驗值；audit 為低併發負載，非 06-20 調 0.9 之 32 併發情境） | 0.9s（finmind.py 已驗證預設；每輪耗時 +~29%） | — | **甲 0.7s**（=裁決單建議「沿用既有 0.7s throttle＋探測閘」）。證偽：一週內 403 → 改 0.9＋冷卻加倍 |
| 連敗斷路器（選配） | 不加（首版簡單；靠 403 證偽條件事後調） | 加：`最近 3 筆 attestation_result 皆 FAIL → 不發車、WLOG 記「連敗斷路、待人裁」`（見訊號即停 #24；代價＝重演人不看就永停之閂鎖，需搭 C4′ alerts sink 才有人看見） | — | **首版甲不加**；C4′ alerts.log sink 落地後補乙（斷路訊息進 alerts 才不是靜默閂鎖）。證偽：若首週出現 ≥3 輪同因 FAIL 連跑，證明不加錯了，立即補乙 |

**每輪 API 負載（設計估算、非實測，僅供節奏裁決參考）**：14 日窗 by-date 表 ~840 call＋roster 抽樣 27 表×40 股 ~1,080 call＋heal 補抓若干 → 約 2,000-3,000 call/輪；0.7s 步調約 25-40 分鐘/輪，額度錶 6,000/h rolling、閘頭寸 200——單輪遠低於上限；與 arena 20:00 出單共用同一 `_quota_gate`（同進程外無互鎖，但兩者皆讀錶退避，見 §5 風險 2）。

**建議案彙整**：三態機照 §3.1＋COOLOFF_H=24＋throttle 0.7 沿用＋首版不加斷路器；C4′ sink 落地後補斷路器乙案。

## §5 風險與回滾

- **風險 1（語意變更）**：FAIL 由永久閂鎖改冷卻重試——若某 FAIL 屬結構性（如判準紅），每日仍會白燒一輪 API 直到人裁。緩解：每日一輪為上限（甲案）；斷路器為既備後手；WLOG 逐日留 verdict 可稽核。
- **風險 2（額度競合）**：watchdog 發車時刻不定，可能與 arena 20:00/21:30 管線同時打 FinMind。兩者皆經 `finmind._pace`＋`_quota_gate`（各自進程讀同一權威錶），錶近滿即雙方暫停；最壞情況＝arena 出單延後數分鐘。若要硬錯開，可加「20:00-22:00 不發車」窗（本版未加，#3 最小邊界）。
- **風險 3（DB 依賴）**：判態改依 DB——postgres 掛掉時 watchdog 全程 no-op（fail-safe 誠實記錄）；attest 斷鏈會持續但不會假綠。與現況（log 假綠）相比嚴格改善。
- **風險 4（attestation_result 可竄）**：該表 trigger=0，superuser 可改寫歷史使 watchdog 誤判——既有 B4 相鄰債，本案誠實記載不擴射程。
- **回滾**：`git checkout -- audit_watchdog.sh audit_selfheal.sh`＋`rm -f /tmp/augur_audit_dispatch.ts`——兩檔皆 repo 追蹤、systemd 零變更故無單元回滾；進行中之 selfheal 由 flock/牆鐘自然收束，無資料側不可逆狀態（attest 本身唯讀對帳＋heal 冪等 re-sync）。

## §6 驗收判準（機械可判）

1. **假綠死亡測試（apply 後立即）**：`bash audit_watchdog.sh` 手動跑一次 → `tail -1 ~/audit_watchdog.log` **不得**含「已綠」（現況 DB：最後 PASS=07-16、>1 日）；必含「過期」＋「FAIL@07-25」與發車或冷卻之一。
2. **fail-safe 測試**：`DB_HOST=127.0.0.99 bash audit_watchdog.sh`（壞連線演練）→ WLOG 末行含「DB 不可讀」、且無新 selfheal 進程（`pgrep -f audit_selfheal` 空）。
3. **單例/冷卻**：發車後 5 分內再手動跑一次 → WLOG 末行為「進行中」或「冷卻中」，`pgrep -f audit_selfheal | wc -l` ≤ 1。
4. **閉環**：啟用後 48h 內 `SELECT count(*) FROM attestation_result WHERE run_at > '<apply 時刻>'` ≥ 1；一旦出現 PASS 列，`python scripts/verify_validation_evidence.py --run --id E1_raw_reconcile_exit` 印 `✓ E1_raw_reconcile_exit → green`。
5. **牆鐘**：發車輪之 selfheal 進程存活時間 ≤ 6h+90s（`ps -o etimes=` 抽查或 WLOG 前後時戳）。
6. **不弱化聲明（L6.16-17 對照）**：發車上限 由「log 靜默 45min 即可再發」→「COOLOFF_H 一輪」；人類介入點（hugo 手動 attest 計入冷卻、隨時 systemctl --user stop timer 可停）不減；WLOG 逐 tick 留態揭露比例不減；最大自動鏈長不增（timer→watchdog→selfheal 三段不變）。

## §7 Steward 決定欄

- [ ] 三態機改寫（§3.1）：准 ／ 修改＝＿＿＿
- [ ] COOLOFF_H：24 ／ 12 ／ 0 ／ 其他＝＿＿＿
- [ ] throttle：0.7 沿用 ／ 0.9
- [ ] 連敗斷路器：首版不加 ／ 加（搭 C4′）
- 裁決：＿＿＿＿＿＿＿＿（日期／簽）

---

## §8 施作後更正（2026-08-01，施作段親驗；史述不改、僅補正）

- **§6.2 演練位址假設錯誤**：`DB_HOST=127.0.0.99` 在本機**不是**壞位址——postgres 綁 `0.0.0.0`、
  127/8 loopback 全可達（`psql SELECT 1` 實測 rc=0）。fail-safe 演練改用**壞埠**（`DB_PORT=59999`）。
  首輪突變驗紅曾因此假紅、換壞埠重做才得真紅——**壞前提會讓驗紅本身變假**，留檔為戒。
- **§2.2 編號筆誤**：07-25 18:14 FAIL 列 live 實為 id **9**（非 8）；verdict 序不變。
- 施作記錄與突變驗紅全文＝commit 57eb275 之波 1 回報。
