#!/usr/bin/env bash
# KH ingest-trigger 訊號輪詢（階 C 可選）— 只跑 --check；無日曆「進化」。
# 不經 install_cron／install_services 默裝。Steward 若要用 systemd，自行 unit＋本腳。
# 與 B3／LLM：本腳預設不搶 augur_llm.lock（check 無 LLM）。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec flock -n /tmp/augur_kh_ingest_trigger.lock \
  "$ROOT/venv/bin/python" scripts/kh_ingest_trigger.py --check "$@"
