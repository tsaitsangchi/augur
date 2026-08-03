#!/usr/bin/env bash
# 🎯 audit 監看看門狗 — 每 30 分判態;判態改讀 DB 帳本 attestation_result(三態機),log 只作進行中觀察。
#    無 1 日內 PASS 且非進行中/冷卻中 → relaunch selfheal(6h 牆鐘)。DB 讀不到=誠實記錄退出(不宣綠、不盲發車)。
# 由 systemd timer augur-audit-watchdog.timer 每 30 分觸發。全本地零 usage(1 次 psql+pgrep)。
# 設計(C2 2026-08-01):log 末行閂鎖假綠實證——末行 PASS 凍於 07-15、DB 最新 07-25 FAIL,watchdog 宣綠 17 天。
# 設計(M-G4 2026-08-03):**發車閉環**——舊版發車後不回頭看,08-02 18:45 那班車一個位元組都沒寫出來,
#   其後 29 行照印「冷卻中」,與正常冷卻在 grep 上不可區分 ⇒ 靜默 39 小時。今加兩道閉環:
#   (a) 發車後 60s 內 audit_retry.log mtime 未前進 → 立刻大聲;(b) 跨輪:dispatch 過寬限期後
#   selfheal 不在且 attestation 零新列 → 每輪大聲並 exit 1(經 OnFailure→alerts.log)。
# 執行指令矩陣:
#   bash audit_watchdog.sh                     # 跑一次檢查(timer 每 30 分自動呼叫;手動亦可)
#   DB_PORT=59999 bash audit_watchdog.sh       # 壞連線演練(fail-safe:不判態、不發車;本機 postgres 綁 0.0.0.0 故 127.0.0.99 非壞位址,以壞埠演練)
#   AUGUR_WATCHDOG_NO_DISPATCH=1 bash audit_watchdog.sh  # 判態演練:照走三態機、到發車就停(零 FinMind API #24)
#   bash audit_watchdog.sh --selftest          # 紅綠自測(零 DB 零 API;閉環判式+字樣互斥+wiring)
cd "$(dirname "$0")" || exit 1
LOG="$HOME/audit_retry.log"
WLOG="$HOME/audit_watchdog.log"
TS_FILE="/tmp/augur_audit_dispatch.ts"
DEAD_FLAG="/tmp/augur_audit_dispatch.dead"   # 夭折已吵過旗標(每次發車只 exit 1 一次,不灌爆 alerts.log)
COOLOFF_H=24        # 發車冷卻(小時;Steward 拍板值——見呈案 §4,403 證偽時第一調整旋鈕:加大至 48)
FIRSTWRITE_WAIT_SEC=60      # 發車後閉環(a):等首筆寫入之上限秒數
DISPATCH_GRACE_SEC=600      # 發車後閉環(b):跨輪判夭折前之寬限秒數(timer 間隔 30 分,故此值只是安全帶)
ts=$(date '+%m-%d %H:%M')

# ── 閉環判式(M-G4)。純函式、零 IO ⇒ --selftest 可紅綠驗;production 與自測同一支。 ──
# dispatch_is_dead:發車後那台車是不是根本沒開出去?
#   $1=selfheal 是否活著(1/0)  $2=dispatch 之後 attestation_result 新列數
#   $3=距 dispatch 秒數        $4=寬限秒數
#   rc=0 ⇒ 夭折(須大聲);rc=1 ⇒ 健康或仍在寬限期內。
#   判準:既沒有行程還在跑、也沒有留下任何 verdict ⇒ 那班車沒開出去(08-02 18:45 即此形)。
dispatch_is_dead() {
  [ "$3" -ge "$4" ] || return 1        # 寬限期內不判(剛發車、還來不及有動靜)
  [ "$1" -eq 0 ] || return 1           # 行程還在跑 = 正常進行中
  [ "$2" -eq 0 ] || return 1           # 已留下 verdict = 有跑到終點
  return 0
}

# cooldown_line:態二之輸出字樣產生器。**與 dispatch_is_dead 同一組輸入**,
# 故字樣與判式不會分岔。驗收②:「發車後夭折」與「冷卻中」兩字樣互斥,grep 可分。
cooldown_line() {   # $1=alive01 $2=attest_after $3=age秒 $4=grace秒 $5=last_verdict $6=cooloff_h
  if dispatch_is_dead "$1" "$2" "$3" "$4"; then
    printf '⛔ 發車後夭折(dispatch 後 %ss:selfheal 不在且 attestation 零新列 ⇒ 車沒開出去;疑 systemd cgroup 連坐,見 M-G4)' "$3"
  else
    printf '冷卻中(最新 %s;%sh 窗內已試,不重複發車)' "$5" "$6"
  fi
}

# await_first_write:發車後 N 秒內 $LOG mtime 是否前進。rc0=有、rc1=逾時未前進。
# ⚠ 射程誠實(假綠自檢):本判式在 watchdog 自己還活著時量,而 Type=oneshot 的 cgroup 於此期間
#   尚未拆 ⇒ 「cgroup 連坐殺」型死法在這 60s 內會看起來是活的。故 (a) 只抓「立刻就死」
#   (flock 搶不到、腳本不存在、權限錯);連坐型必須靠跨輪的 dispatch_is_dead 才抓得到。
await_first_write() {   # $1=檔 $2=發車前 mtime $3=最長等待秒 $4=輪詢間隔秒(預設 2)
  f="$1"; before="$2"; deadline="$3"; step="${4:-2}"; waited=0
  while :; do
    now_m=$(stat -c %Y "$f" 2>/dev/null || echo 0)
    [ "$now_m" -gt "$before" ] && return 0
    [ "$waited" -ge "$deadline" ] && return 1
    sleep "$step"; waited=$((waited+step))
  done
}

case "${1:-}" in
  --selftest)
    ok=0
    chk() { if [ "$2" = "1" ]; then echo "  ✓ $1"; else echo "  ✗ $1"; ok=1; fi; }
    # ── A. dispatch_is_dead 真值表(alive attest_after age grace) ──
    dispatch_is_dead 1 0 1800 600; rc=$?; chk "行程還活著 ⇒ 不判夭折" "$([ $rc -eq 1 ] && echo 1 || echo 0)"
    dispatch_is_dead 0 1 1800 600; rc=$?; chk "已有 attestation 新列 ⇒ 不判夭折" "$([ $rc -eq 1 ] && echo 1 || echo 0)"
    dispatch_is_dead 0 0  60  600; rc=$?; chk "寬限期內(60s<600s) ⇒ 不判夭折" "$([ $rc -eq 1 ] && echo 1 || echo 0)"
    dispatch_is_dead 0 0 1800 600; rc=$?; chk "行程不在+零新列+過寬限 ⇒ **判夭折**(=08-02 18:45 實況)" "$([ $rc -eq 0 ] && echo 1 || echo 0)"
    # ── B. 字樣互斥(驗收②:發車失敗與正常冷卻在 grep 上可區分) ──
    l_dead=$(cooldown_line 0 0 1800 600 "PASS@08-01 18:43" 24)
    l_cool=$(cooldown_line 1 0 1800 600 "PASS@08-01 18:43" 24)
    chk "夭折字樣含『發車後夭折』且不含『冷卻中』" \
        "$(printf '%s' "$l_dead" | grep -q '發車後夭折' && ! printf '%s' "$l_dead" | grep -q '冷卻中' && echo 1 || echo 0)"
    chk "冷卻字樣含『冷卻中』且不含『發車後夭折』" \
        "$(printf '%s' "$l_cool" | grep -q '冷卻中' && ! printf '%s' "$l_cool" | grep -q '發車後夭折' && echo 1 || echo 0)"
    # 判式與字樣不得分岔:同一組輸入,rc=0 必配夭折字樣、rc=1 必配冷卻字樣
    sync_ok=1
    for c in "1 0 1800 600" "0 1 1800 600" "0 0 60 600" "0 0 1800 600"; do
      # shellcheck disable=SC2086
      dispatch_is_dead $c; rc=$?
      # shellcheck disable=SC2086
      line=$(cooldown_line $c "V" 24)
      if [ "$rc" -eq 0 ]; then printf '%s' "$line" | grep -q '發車後夭折' || sync_ok=0
      else printf '%s' "$line" | grep -q '冷卻中' || sync_ok=0; fi
    done
    chk "判式 rc 與輸出字樣全表一致(不分岔)" "$sync_ok"
    # ── C. await_first_write 真檔行為(非合成 fixture:真 stat、真 mtime) ──
    t=$(mktemp); touch -d '@1000000000' "$t"; before=$(stat -c %Y "$t")
    await_first_write "$t" "$before" 2 1; rc=$?; chk "無人寫入 ⇒ 逾時報紅(rc1)" "$([ $rc -eq 1 ] && echo 1 || echo 0)"
    ( sleep 1; touch "$t" ) &
    await_first_write "$t" "$before" 10 1; rc=$?; chk "有人寫入 ⇒ 偵測到前進(rc0)" "$([ $rc -eq 0 ] && echo 1 || echo 0)"
    wait; rm -f "$t"
    # ── D. wiring(防假綠:確認 production 真的呼叫這三支,而非只有自測在跑) ──
    #   pattern 用字串併接切開,否則 grep 會掃到本斷言自己這一行(install_cron.sh 2026-07-31 實犯之型)
    src="${BASH_SOURCE[0]}"
    chk "production 態二呼叫 cooldown_line" \
        "$(grep -c 'cooldown''_line "\$alive01"' "$src" | grep -q '^1$' && echo 1 || echo 0)"
    chk "production 態二呼叫 dispatch_is_dead 取 rc" \
        "$(grep -c 'dispatch''_is_dead "\$alive01"' "$src" | grep -q '^1$' && echo 1 || echo 0)"
    chk "production 態三呼叫 await_first_write" \
        "$(grep -c 'await''_first_write "\$LOG"' "$src" | grep -q '^1$' && echo 1 || echo 0)"
    chk "SQL 帶 dispatch 後 attestation 計數(閉環(b)之輸入來源)" \
        "$(grep -q 'run_at > to_timestamp(\${disp_epoch})' "$src" && echo 1 || echo 0)"
    # 假綠鎖:該計數必須鎖 selfheal 自己的 driver。放寬成 daily_maintenance% 會把別人跑的
    # --audit-only 算進來 ⇒ 真死掉的發車被判健康(2026-08-03 12:07 live 實例)。
    chk "該計數之 driver 鎖 --heal(不得放寬成 daily_maintenance%)" \
        "$(awk "/run_at > to_timestamp/{print prev} {prev=\$0}" "$src" | grep -q "driver LIKE '%--heal%'" && echo 1 || echo 0)"
    echo "自測:$([ $ok -eq 0 ] && echo '全通過 ✓' || echo '有失敗 ✗')"
    exit $ok ;;
  "") : ;;
  *) awk '/^cd "\$\(dirname/{exit} NR>1' "${BASH_SOURCE[0]}"; exit 2 ;;
esac

# ① DB 判態:1 日內 PASS?/冷卻窗內已試?/最新 verdict?/dispatch 後有無新 verdict?(driver 過濾=E1 gate 同口徑)
#   外部已設 DB_HOST/DB_PORT 時保留之(.env 不覆寫)——使壞連線演練(驗收 §6.2)可執行
disp_epoch=$(stat -c %Y "$TS_FILE" 2>/dev/null || echo 0)   # 發車時戳(無檔=0 ⇒ to_timestamp(0)=1970,計數必 >0 ⇒ 不誤判夭折)
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
       ORDER BY run_at DESC LIMIT 1),'無紀錄'),
    (SELECT count(*) FROM attestation_result WHERE driver LIKE '%--heal%'
       AND run_at > to_timestamp(${disp_epoch}))" 2>/dev/null)
if [ -z "$row" ]; then
  echo "$ts watchdog: ⚠ DB 不可讀——不判態、不發車(fail-safe 雙向:不宣綠、不盲放量)" >> "$WLOG"; exit 0
fi
fresh_pass=$(echo "$row" | cut -d'|' -f1)
recent_try=$(echo "$row" | cut -d'|' -f2)
last_verdict=$(echo "$row" | cut -d'|' -f3)
# dispatch 之後、**由被發車的那支**留下的 verdict 列數(閉環(b) 之核心輸入)。
# ⚠ driver 必須鎖 '--heal'(audit_selfheal.sh 跑的是 daily_maintenance --audit-days 14 --audit-all --heal):
#   用寬鬆的 'daily_maintenance%' 會把**別人跑的** --audit-only 也算成「這班車到站了」——
#   2026-08-03 12:07 live 即有一筆 --audit-only,足以讓 08-02 那班真死掉的車被判成健康(假綠)。
attest_after=$(echo "$row" | cut -d'|' -f4)

# 態一:綠(1 日內 PASS)→ 無需動作
if [ "$fresh_pass" -ge 1 ]; then
  echo "$ts watchdog: audit 已綠 ✓(DB:1 日內 PASS;最新 $last_verdict)" >> "$WLOG"; exit 0
fi

# 態二:進行中或冷卻中 → 觀察不動作(FAIL 不再是永久閂鎖;冷卻窗防 rc=2 終態重試風暴 #24)
alive=$(pgrep -f 'audit_selfheal\.sh' | head -1)
alive01=$([ -n "$alive" ] && echo 1 || echo 0)
if [ -n "$alive" ]; then
  logage=$(( $(date +%s) - $(stat -c %Y "$LOG" 2>/dev/null || echo 0) ))
  echo "$ts watchdog: 進行中(selfheal pid $alive、log ${logage}s 前更新;最新 $last_verdict)" >> "$WLOG"; exit 0
fi
tsage=$(( $(date +%s) - disp_epoch ))
if [ "$recent_try" -ge 1 ] || { [ -f "$TS_FILE" ] && [ "$tsage" -lt $((COOLOFF_H*3600)) ]; }; then
  # 閉環(b):冷卻與夭折用同一組輸入判、同一支產生字樣 ⇒ 不會再出現「兩者都印冷卻中」(M-G4)
  echo "$ts watchdog: $(cooldown_line "$alive01" "$attest_after" "$tsage" "$DISPATCH_GRACE_SEC" "$last_verdict" "$COOLOFF_H")" >> "$WLOG"
  if dispatch_is_dead "$alive01" "$attest_after" "$tsage" "$DISPATCH_GRACE_SEC"; then
    # 每次發車只 exit 1 一次(→ OnFailure=augur-alert@%n → ~/logs/alerts.log),旗標於下次發車清除
    [ -f "$DEAD_FLAG" ] && exit 0
    : > "$DEAD_FLAG"; exit 1
  fi
  exit 0
fi

# 態三:過期(無 1 日內 PASS、無進行中、冷卻已過)→ 發車(flock 守單例;6h 牆鐘)
echo "$ts watchdog: ⚠ 過期(最新 $last_verdict、無 1 日內 PASS)→ relaunch(timeout 6h)" >> "$WLOG"
before_m=$(stat -c %Y "$LOG" 2>/dev/null || echo 0)
touch "$TS_FILE"; rm -f "$DEAD_FLAG"
if [ -n "${AUGUR_WATCHDOG_NO_DISPATCH:-}" ]; then
  echo "$ts watchdog: (演練 AUGUR_WATCHDOG_NO_DISPATCH=1:到發車即止,不真發車、不驗閉環)" >> "$WLOG"; exit 0
fi
setsid nohup timeout -k 60 21600 flock -n /tmp/augur_audit.lock bash "$PWD/audit_selfheal.sh" >/dev/null 2>&1 < /dev/null &
disown 2>/dev/null || true
echo "$ts watchdog: relaunch 已送(flock 守單例、dispatch 時戳=$TS_FILE)" >> "$WLOG"
# 閉環(a):發車後 60s 內 $LOG 必須有寫入,否則那班車立刻就死了(flock 搶不到/腳本不在/權限錯)
if await_first_write "$LOG" "$before_m" "$FIRSTWRITE_WAIT_SEC"; then
  echo "$(date '+%m-%d %H:%M') watchdog: 閉環 ✓ 發車後 ${FIRSTWRITE_WAIT_SEC}s 內 $LOG 已有寫入" >> "$WLOG"
else
  echo "$(date '+%m-%d %H:%M') watchdog: ⛔ 發車後夭折(${FIRSTWRITE_WAIT_SEC}s 內 $LOG mtime 未前進 ⇒ 車沒開出去)" >> "$WLOG"
  : > "$DEAD_FLAG"; exit 1
fi
