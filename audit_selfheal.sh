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
    echo "$(date '+%m-%d %H:%M') 探測 $i/48:IP 健康 → 放量跑 audit(interval=0.7 實驗、對帳窗近14日)" >> "$LOG"
    # throttle:FINMIND_MIN_INTERVAL=0.7(hugo 2026-07-14 拍板實驗值 #27;>0.9 已驗證值、IP 剛 sustained ban 後屬激進——
    #   放量後緊盯,撞 403 即退回 0.9;縮窗後總量小、sustained 短,風險由範圍縮緩解)。
    # 對帳窗:--audit-since 2026-07-01(近~14 日;hugo 拍板 A 縮 #7 attestation 範圍——6/1 起全量 sustained throttle IP、
    #   歷史凍結期已對帳定案、近 14 日足以 attestation 最近增量;完整性判準變更留痕見 HANDOFF §4)。
    FINMIND_MIN_INTERVAL=0.7 PYTHONUNBUFFERED=1 venv/bin/python scripts/daily_maintenance.py --audit-since 2026-07-01 >> "$LOG" 2>&1 &
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
      echo "$(date '+%m-%d %H:%M') ✓ audit 完成(rc=0)" >> "$LOG"
      exit 0
    fi
    echo "$(date '+%m-%d %H:%M') audit 中斷(rc=$rc),休 30 分回探測" >> "$LOG"
  else
    echo "$(date '+%m-%d %H:%M') 探測 $i/48:仍拒,休 30 分" >> "$LOG"
  fi
  sleep 1800
done
echo "$(date '+%m-%d %H:%M') 48 次未完成,停止;人工介入" >> "$LOG"
exit 1
