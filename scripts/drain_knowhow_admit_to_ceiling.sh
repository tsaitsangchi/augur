#!/usr/bin/env bash
# ⚠ **已過時（2026-07-30）＝請改用 scripts/run_kh_chain.py**
#   本檔原註「ceiling=7（KH8/9 未 LAND）」已不實：KH8／KH9 早已 LAND（三表皆在、
#   evaluate_layer(8)/(9) 有實評估器），且硬夾 --apply-up-to 7 會使推進永遠停在 7。
#   新入口：python3 scripts/run_kh_chain.py --check   （前置檢查＋各段待辦量）
#            python3 scripts/run_kh_chain.py --run --phase advance --limit 5000
#   本檔保留為史料；如仍要用，下方 ceiling 已改為 9（受 gate.max_auto_depth 夾）。
# 單進程清到 depth 上限（KH10 不納入：depth-10 評估器僅查 gate.enabled＝自我背書）。
# 用法（主機 net／能連 DB 的終端）:
#   bash scripts/drain_knowhow_admit_to_ceiling.sh
# 守: FZ-keep · predict⊥API · 不假推 8–10 · HUMAN-APPROVE-keep
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-./venv/bin/python}"
LOG="${LOG:-/tmp/knowhow_admit_until_empty_$(date +%Y%m%d_%H%M%S).log}"
echo "log=$LOG"
echo "ceiling=9 (KH8/KH9 已 LAND; 實際受 gate.max_auto_depth 夾; KH10 不納入)"
# 避免並發：若已有 runner 則退出
if pgrep -f 'scripts/run_knowhow_auto_admit.py' >/dev/null 2>&1; then
  echo "ABORT: another run_knowhow_auto_admit.py already running:" >&2
  pgrep -af 'scripts/run_knowhow_auto_admit.py' >&2 || true
  exit 3
fi
exec "$PY" scripts/run_knowhow_auto_admit.py \
  --until-empty --apply-up-to 9 --limit 5000 --max-rounds 200 \
  2>&1 | tee "$LOG"
