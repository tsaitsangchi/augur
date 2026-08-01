#!/usr/bin/env bash
# 🎯 systemd OnFailure sink——單元失敗時追記一行到 ~/logs/alerts.log。
#
# 守 #28(本地零依賴:純 bash+coreutils;DB/venv 全掛照樣可寫——sink 不得依賴失敗棧,
# 登錄冊 C4′ 裁定即因此否決 DB 表案)、#15(失敗必須留下可見痕跡,不靜默)。
#
# 執行指令矩陣
# ------------
#   bash scripts/notify_failure.sh <unit名>     # 追記一行(由 augur-alert@.service 以 %i 呼叫)
#   bash scripts/notify_failure.sh --selftest   # 紅綠自測(寫進暫存檔驗真行為)
set -u
LOG="${AUGUR_ALERT_LOG:-$HOME/logs/alerts.log}"

append_alert() {  # $1=unit $2=logfile。純函式化:輸出行格式固定,selftest 餵真輸入驗
  mkdir -p "$(dirname "$2")"
  printf '%s FAIL %s\n' "$(date '+%F %T%z')" "$1" >> "$2"
}

case "${1:-}" in
  --selftest)
    ok=0; t=$(mktemp)
    append_alert "augur-test.service" "$t"
    grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} .+ FAIL augur-test\.service$' "$t" && echo "  ✓ 追記行格式正確(真寫真讀)" || { echo "  ✗ 追記行格式"; ok=1; }
    append_alert "u2" "$t"
    [ "$(wc -l < "$t")" = 2 ] && echo "  ✓ append 不覆寫(兩行都在)" || { echo "  ✗ append 覆寫了"; ok=1; }
    rm -f "$t"
    echo "自測:$([ $ok = 0 ] && echo '全通過 ✓' || echo '有失敗 ✗')"; exit $ok ;;
  "") echo "用法: notify_failure.sh <unit名>|--selftest"; exit 2 ;;
  *) append_alert "$1" "$LOG" ;;
esac
