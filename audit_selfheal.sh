#!/bin/bash
# augur audit 自癒跑者 v2(2026-07-13:增 log 停滯看門狗)。
# 迴圈:最小探測(#25 單股單日)→ IP 健康才放量跑 audit → 中斷/卡死 → 休 30 分回探測,至綠或 48 次。
# 看門狗:audit log 靜默 >45 分=卡死(實證 2026-07-13:對帳段 API 讀無效 timeout 掛 9h,poll_schedule_timeout)
#        → 殺進程記中斷、走自癒循環(DB-driven resume 冪等快轉已對帳段)。
# 用法:nohup flock -n /tmp/augur_audit.lock bash audit_selfheal.sh >/dev/null 2>&1 &
#      log=~/audit_retry.log;隨 repo 走、任何 clone 直跑(cd 到腳本所在 repo 根)。
cd "$(dirname "$0")" || exit 1
LOG="$HOME/audit_retry.log"
for i in $(seq 1 48); do
  if PYTHONPATH=src venv/bin/python - <<'EOF' >> "$LOG" 2>&1
from augur.ingestion.finmind import fetch
import sys
try:
    fetch("TaiwanStockPrice", data_id="2330", start_date="2026-07-09", end_date="2026-07-09", max_retries=0)
    sys.exit(0)
except Exception as e:
    print(f"probe: {type(e).__name__}: {e}", flush=True)
    sys.exit(1)
EOF
  then
    echo "$(date '+%m-%d %H:%M') 探測 $i/48:IP 健康 → 放量跑 audit(interval=0.7 實驗、滾動窗 today−14)" >> "$LOG"
    # throttle:FINMIND_MIN_INTERVAL=0.7(hugo 2026-07-14 拍板實驗值 #27;>0.9 已驗證值、IP 剛 sustained ban 後屬激進——
    #   放量後緊盯,撞 403 即退回 0.9;縮窗後總量小、sustained 短,風險由範圍縮緩解)。
    # 對帳窗:--audit-days 14=滾動 since=today−14(hugo 2026-07-14 拍板取代寫死 2026-07-01——寫死窗隨時間膨脹
    #   重演 IP throttle;滾出窗之日以最後一次 attest 定案,同 05-31 凍結先例;留痕 HANDOFF §4)。
    # --audit-all(全量 attest 非只本次更新)+--heal(差異日自動 sync 重抓再驗);窗上限=catalog 滾動安全邊緣(hugo 07-14 拍板 (a)+(b))
    FINMIND_MIN_INTERVAL=0.7 PYTHONUNBUFFERED=1 venv/bin/python scripts/daily_maintenance.py --audit-days 14 --audit-all --heal >> "$LOG" 2>&1 &
    py=$!
    while kill -0 "$py" 2>/dev/null; do
      sleep 300
      age=$(( $(date +%s) - $(stat -c %Y "$LOG") ))
      if [ "$age" -gt 2700 ]; then
        echo "$(date '+%m-%d %H:%M') 看門狗:log 靜默 ${age}s>45min=卡死 → 殺進程記中斷" >> "$LOG"
        kill "$py" 2>/dev/null; sleep 5; kill -9 "$py" 2>/dev/null
        break
      fi
    done
    wait "$py"; rc=$?
    if [ "$rc" -eq 0 ]; then
      echo "$(date '+%m-%d %H:%M') ✓ audit 完成且對帳綠(rc=0 attestation PASS)" >> "$LOG"
      exit 0
    fi
    if [ "$rc" -eq 2 ]; then
      # rc=2=機制跑完但 attestation FAIL(資料判準紅)——重試不會變綠、只重打一輪 API(#24/#28),
      # 終態停手待根因/判準拍板(#26);watchdog 見 FAIL 終態亦不 relaunch。
      echo "$(date '+%m-%d %H:%M') ✗ audit 對帳 FAIL(rc=2)——不重試,待根因;見 log 內 attestation 行" >> "$LOG"
      exit 1
    fi
    # rc=3=僅未完整(過程抓取錯、VM/EX=0)→ 與其他中斷同路:休 30 分回探測重試(暫時性錯誤可自癒)
    echo "$(date '+%m-%d %H:%M') audit 中斷(rc=$rc$([ "$rc" -eq 3 ] && echo '=未完整可重試')),休 30 分回探測" >> "$LOG"
  else
    echo "$(date '+%m-%d %H:%M') 探測 $i/48:仍拒,休 30 分" >> "$LOG"
  fi
  sleep 1800
done
echo "$(date '+%m-%d %H:%M') 48 次未完成,停止;人工介入" >> "$LOG"
exit 1
