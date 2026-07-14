#!/usr/bin/env bash
# 🎯 audit 監看看門狗 — 每 30 分驗證 audit 執行狀況;selfheal 死或 log 靜默>45min 且未綠→relaunch
#    (flock 防重複:selfheal 還活著持鎖時 relaunch 立即失敗 no-op);已綠→只記錄不動作。
# 由 systemd timer augur-audit-watchdog.timer 每 30 分觸發(session-independent、撐過 Claude session)。
# 全本地零 usage。log=~/audit_watchdog.log(監看軌)、audit 本體 log=~/audit_retry.log。
#
# 設計選擇:驗證優先、異常才 relaunch(非無條件重啟——無條件會打斷正在健康跑的對帳);冪等靠 flock。
# 執行指令矩陣:
#   bash audit_watchdog.sh          # 跑一次檢查(timer 每 30 分自動呼叫;手動亦可)
cd "$(dirname "$0")" || exit 1
LOG="$HOME/audit_retry.log"
WLOG="$HOME/audit_watchdog.log"
ts=$(date '+%m-%d %H:%M')

# ① 以「最後一條 attestation」判態(rc=0≠PASS 假綠教訓 2026-07-14;log 累積故取最後一條為現況)
last_att=$(grep -E 'attestation：' "$LOG" 2>/dev/null | tail -1)
case "$last_att" in
  *"✅ PASS"*)
    echo "$ts watchdog: audit 已綠 ✓(attestation PASS)、無需動作" >> "$WLOG"
    exit 0 ;;
  *"❌ FAIL"*)
    # 對帳紅=終態:relaunch 重跑不會變綠、只重打一輪 API(#24/#28)→ 只記錄、待根因/判準拍板(#26)
    echo "$ts watchdog: ✗ attestation FAIL 終態——不 relaunch,待根因" >> "$WLOG"
    exit 0 ;;
esac

# ② 未綠 → 檢查 selfheal 存活 + log 進展
alive=$(pgrep -f 'audit_selfheal\.sh' | head -1)
logage=$(( $(date +%s) - $(stat -c %Y "$LOG" 2>/dev/null || echo 0) ))
if [ -n "$alive" ] && [ "$logage" -lt 2700 ]; then
  pos=$(grep -oE '\[[0-9]+/88\]' "$LOG" 2>/dev/null | tail -1)
  echo "$ts watchdog: 健康(selfheal pid $alive、log ${logage}s 前更新、進度 ${pos:-?})" >> "$WLOG"
  exit 0
fi

# ③ selfheal 死 或 log 靜默>45min → relaunch(flock 防重複:還持鎖=立即失敗 no-op)
echo "$ts watchdog: ⚠ 異常(selfheal alive='${alive:-無}'、log ${logage}s 靜默)→ relaunch" >> "$WLOG"
setsid nohup flock -n /tmp/augur_audit.lock bash "$PWD/audit_selfheal.sh" >/dev/null 2>&1 < /dev/null &
disown 2>/dev/null || true
echo "$ts watchdog: relaunch 已送(flock 守單例)" >> "$WLOG"
