#!/usr/bin/env bash
# 🎯 audit 監看看門狗 — 每 30 分判態;判態改讀 DB 帳本 attestation_result(三態機),log 只作進行中觀察。
#    無 1 日內 PASS 且非進行中/冷卻中 → relaunch selfheal(6h 牆鐘)。DB 讀不到=誠實記錄退出(不宣綠、不盲發車)。
# 由 systemd timer augur-audit-watchdog.timer 每 30 分觸發。全本地零 usage(1 次 psql+pgrep)。
# 設計(C2 2026-08-01):log 末行閂鎖假綠實證——末行 PASS 凍於 07-15、DB 最新 07-25 FAIL,watchdog 宣綠 17 天。
# 執行指令矩陣:
#   bash audit_watchdog.sh                     # 跑一次檢查(timer 每 30 分自動呼叫;手動亦可)
#   DB_PORT=59999 bash audit_watchdog.sh       # 壞連線演練(fail-safe:不判態、不發車;本機 postgres 綁 0.0.0.0 故 127.0.0.99 非壞位址,以壞埠演練)
cd "$(dirname "$0")" || exit 1
LOG="$HOME/audit_retry.log"
WLOG="$HOME/audit_watchdog.log"
TS_FILE="/tmp/augur_audit_dispatch.ts"
COOLOFF_H=24        # 發車冷卻(小時;Steward 拍板值——見呈案 §4,403 證偽時第一調整旋鈕:加大至 48)
ts=$(date '+%m-%d %H:%M')

# ① DB 判態:1 日內 PASS?/冷卻窗內已試?/最新 verdict?(driver 過濾=E1 gate 同口徑)
#   外部已設 DB_HOST/DB_PORT 時保留之(.env 不覆寫)——使壞連線演練(驗收 §6.2)可執行
_ext_db_host="${DB_HOST:-}"; _ext_db_port="${DB_PORT:-}"
set -a; . ./.env 2>/dev/null; set +a
[ -n "$_ext_db_host" ] && DB_HOST="$_ext_db_host"
[ -n "$_ext_db_port" ] && DB_PORT="$_ext_db_port"
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
