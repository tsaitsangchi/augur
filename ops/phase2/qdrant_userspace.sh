#!/usr/bin/env bash
# Prefer systemd --user unit augur-qdrant.service for linger boot; this script is manual fallback.
# T1：userspace qdrant（native aarch64）啟動／停止——免 sudo docker。
set -euo pipefail
INSTALL="${QDRANT_HOME:-/home/giga/qdrant}"
BIN="$INSTALL/qdrant"
CFG="$INSTALL/config.yaml"
LOG="${QDRANT_LOG:-/home/giga/augur-data/qdrant.log}"
PIDFILE="${QDRANT_PID:-/home/giga/augur-data/qdrant.pid}"
STORAGE="${QDRANT_STORAGE:-/home/giga/augur-data/qdrant}"
CMD="${1:-status}"

mkdir -p "$(dirname "$LOG")" "$STORAGE"

is_up() {
  curl -sf --max-time 2 http://127.0.0.1:6333/ >/dev/null 2>&1
}

case "$CMD" in
  start)
    if is_up; then
      echo "qdrant already UP on :6333"
      curl -s http://127.0.0.1:6333/ | head -c 200; echo
      exit 0
    fi
    test -x "$BIN" || { echo "✗ missing $BIN"; exit 1; }
    test -f "$CFG" || { echo "✗ missing $CFG"; exit 1; }
    nohup "$BIN" --config-path "$CFG" >>"$LOG" 2>&1 &
    echo $! >"$PIDFILE"
    for i in 1 2 3 4 5 6 7 8 9 10; do
      if is_up; then
        echo "qdrant started pid=$(cat "$PIDFILE")"
        curl -s http://127.0.0.1:6333/ | head -c 200; echo
        exit 0
      fi
      sleep 0.5
    done
    echo "✗ qdrant failed to become ready; see $LOG"
    exit 1
    ;;
  stop)
    if [ -f "$PIDFILE" ]; then
      kill "$(cat "$PIDFILE")" 2>/dev/null || true
      rm -f "$PIDFILE"
    fi
    pkill -f "$BIN" 2>/dev/null || true
    echo "qdrant stop signaled"
    ;;
  status)
    if is_up; then
      echo "UP"
      curl -s http://127.0.0.1:6333/ | head -c 200; echo
    else
      echo "DOWN"
      exit 1
    fi
    ;;
  *)
    echo "usage: $0 {start|stop|status}"; exit 1
    ;;
esac
