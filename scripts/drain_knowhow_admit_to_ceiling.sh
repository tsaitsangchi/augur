#!/usr/bin/env bash
# 單進程清到實務天花板 depth=6（非真 KH10）。
# 用法（主機 net／能連 DB 的終端）:
#   bash scripts/drain_knowhow_admit_to_ceiling.sh
# 守: FZ-keep · predict⊥API · 不假推 7–10
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-./venv/bin/python}"
LOG="${LOG:-/tmp/knowhow_admit_until_empty_$(date +%Y%m%d_%H%M%S).log}"
echo "log=$LOG"
echo "ceiling=6 (KH7 fail / KH8-9 UNBUILT; max_auto_depth=7 but evaluate_layer 7 fails)"
# 避免並發：若已有 runner 則退出
if pgrep -f 'scripts/run_knowhow_auto_admit.py' >/dev/null 2>&1; then
  echo "ABORT: another run_knowhow_auto_admit.py already running:" >&2
  pgrep -af 'scripts/run_knowhow_auto_admit.py' >&2 || true
  exit 3
fi
exec "$PY" scripts/run_knowhow_auto_admit.py \
  --until-empty --apply-up-to 6 --limit 5000 --max-rounds 200 \
  2>&1 | tee "$LOG"
