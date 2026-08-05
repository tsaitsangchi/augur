#!/usr/bin/env bash
# 🎯 B3 日更 as-of 編排薄殼 — feat → core(B1 incr) → predict H20/H60 → emit → 驗收。
#
# 守: FZ/GATE-keep · skip-sync（本殼永不 sync）· no-SIM-apply · **非 cron**（禁 systemd／install_cron）。
# 契約: reports/augur_daily_asof_b3_orchestrator_plan_20260805.md
#       reports/augur_daily_asof_predict_emit_runbook_20260805.md
# GO:   audits/DAILY-ASOF-B3-SHELL-GO-20260805.md
#
# 執行指令矩陣:
#   bash scripts/run_daily_asof_predict.sh --dry-plan
#   bash scripts/run_daily_asof_predict.sh --date 2026-08-04 --dry-plan
#   bash scripts/run_daily_asof_predict.sh --date 2026-08-04
#   bash scripts/run_daily_asof_predict.sh --date 2026-08-04 --skip-feat --force-core
#   bash scripts/run_daily_asof_predict.sh --date 2026-08-04 --force-core --skip-predict --skip-emit
#   bash scripts/run_daily_asof_predict.sh --date 2026-08-04 --core-full
#   bash scripts/run_daily_asof_predict.sh --selftest   # 旗標／路徑（輕；可連 DB 讀 max）
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || { echo "✗ 找不到專案目錄 $ROOT" >&2; exit 1; }

PY="${ROOT}/venv/bin/python"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"

DATE=""
HORIZONS="20,60"
DRY_PLAN=0
SKIP_FEAT=0
SKIP_CORE=0
FORCE_FEAT=0
FORCE_CORE=0
CORE_FULL=0
SKIP_PREDICT=0
SKIP_EMIT=0
SELFTEST=0
LOG=""

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \?//'
  echo ""
  echo "選項: --date YYYY-MM-DD  --horizons 20,60  --dry-plan"
  echo "      --skip-feat  --skip-core  --force-feat  --force-core  --core-full"
  echo "      --skip-predict  --skip-emit  --selftest"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE="${2:-}"; shift 2 ;;
    --horizons) HORIZONS="${2:-}"; shift 2 ;;
    --dry-plan) DRY_PLAN=1; shift ;;
    --skip-feat) SKIP_FEAT=1; shift ;;
    --skip-core) SKIP_CORE=1; shift ;;
    --force-feat) FORCE_FEAT=1; shift ;;
    --force-core) FORCE_CORE=1; shift ;;
    --core-full) CORE_FULL=1; shift ;;
    --skip-predict) SKIP_PREDICT=1; shift ;;
    --skip-emit) SKIP_EMIT=1; shift ;;
    --selftest) SELFTEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知參數: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ ! -x "$PY" ]]; then
  echo "✗ 找不到 $PY" >&2
  exit 1
fi

# --- 唯讀錨（stdout: key=value）-----------------------------------------------
probe_anchors() {
  "$PY" - <<'PY'
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute('SELECT max(date)::text FROM "TaiwanStockPriceAdj" WHERE stock_id=%s', ("TAIEX",))
    print("price_max", cur.fetchone()[0] or "")
    cur.execute("SELECT max(panel_date)::text FROM feature_values")
    print("fv_max", cur.fetchone()[0] or "")
    cur.execute("SELECT max(as_of_date)::text FROM core_universe_asof")
    print("core_max", cur.fetchone()[0] or "")
    cur.execute(
        "SELECT count(*) FROM feature_values WHERE panel_date = "
        "(SELECT max(panel_date) FROM feature_values)")
    # per-D presence filled later
PY
}

has_fv_d() {
  local d="$1"
  "$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute('SELECT 1 FROM feature_values WHERE panel_date=%s LIMIT 1', ('$d',))
    print('1' if cur.fetchone() else '0')
"
}

has_core_d() {
  local d="$1"
  "$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute('SELECT 1 FROM core_universe_asof WHERE as_of_date=%s LIMIT 1', ('$d',))
    print('1' if cur.fetchone() else '0')
"
}

resolve_date() {
  if [[ -n "$DATE" ]]; then
    echo "$DATE"
    return
  fi
  "$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute('SELECT max(date)::text FROM \"TaiwanStockPriceAdj\" WHERE stock_id=%s', ('TAIEX',))
    d=cur.fetchone()[0]
    assert d, 'TAIEX max(date) 空'
    print(d)
"
}

verify_accept() {
  local d="$1"
  "$PY" -c "
from augur.advisor.payload import build_single_ticker_rel_payload
p = build_single_ticker_rel_payload('2330', horizon=20)
print(p.as_of)
raise SystemExit(0 if str(p.as_of) == '$d' else 1)
"
}

run_step() {
  local name="$1"; shift
  echo ""
  echo "── step: $name ──"
  echo "+ $*"
  if [[ "$DRY_PLAN" -eq 1 ]]; then
    echo "  (dry-plan: 未執行)"
    return 0
  fi
  local rc=0
  "$@" || rc=$?
  echo "RC[$name]=$rc"
  if [[ "$rc" -ne 0 ]]; then
    echo "✗ 停鏈 @ $name (RC=$rc)" >&2
    exit "$rc"
  fi
}

selftest() {
  local ok=1
  [[ -f "$ROOT/scripts/build_feature_panel.py" ]] || { echo "FAIL missing build_feature_panel"; ok=0; }
  [[ -f "$ROOT/scripts/build_core_universe.py" ]] || { echo "FAIL missing build_core_universe"; ok=0; }
  [[ -f "$ROOT/scripts/predict_asof.py" ]] || { echo "FAIL missing predict_asof"; ok=0; }
  [[ -f "$ROOT/scripts/calibrate_relative_probability.py" ]] || { echo "FAIL missing calibrate"; ok=0; }
  # 互斥語意：skip+force 允許（force 勝）；core-full 與 incremental 二選一在組命令時處理
  local d
  d="$(resolve_date)"
  echo "selftest resolve_date → $d"
  local pm
  pm="$("$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute('SELECT max(date)::text FROM \"TaiwanStockPriceAdj\" WHERE stock_id=%s', ('TAIEX',))
    print(cur.fetchone()[0] or '')
")"
  echo "selftest price_max → $pm"
  if [[ "$ok" -eq 1 ]]; then
    echo "自測:路徑＋錨 OK ✓"
    exit 0
  fi
  echo "自測:FAIL ✗"
  exit 1
}

if [[ "$SELFTEST" -eq 1 ]]; then
  selftest
fi

D="$(resolve_date)"
IFS=',' read -r -a HZ_ARR <<< "$HORIZONS"

echo "══════════════════════════════════════════════════════"
echo "B3 run_daily_asof_predict  D=$D  dry_plan=$DRY_PLAN  horizons=$HORIZONS"
echo "  skip_feat=$SKIP_FEAT force_feat=$FORCE_FEAT  skip_core=$SKIP_CORE force_core=$FORCE_CORE core_full=$CORE_FULL"
echo "  skip_predict=$SKIP_PREDICT skip_emit=$SKIP_EMIT"
echo "  本殼不呼叫 sync／FinMind／cron／sim-apply"
echo "══════════════════════════════════════════════════════"

# 錨
PRICE_MAX="$("$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute('SELECT max(date)::text FROM \"TaiwanStockPriceAdj\" WHERE stock_id=%s', ('TAIEX',))
    print(cur.fetchone()[0] or '')
")"
FV_MAX="$("$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute('SELECT max(panel_date)::text FROM feature_values'); print(cur.fetchone()[0] or '')
")"
CORE_MAX="$("$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute('SELECT max(as_of_date)::text FROM core_universe_asof'); print(cur.fetchone()[0] or '')
")"
echo "錨: price_max=$PRICE_MAX fv_max=$FV_MAX core_max=$CORE_MAX"

if [[ -z "$PRICE_MAX" || "$PRICE_MAX" < "$D" ]]; then
  echo "✗ 告警: PriceAdj TAIEX max($PRICE_MAX) < D($D) —— 整鏈 SKIP（不做 B）" >&2
  exit 3
fi

NEED_FEAT=0
NEED_CORE=0
if [[ "$SKIP_FEAT" -eq 0 ]]; then
  if [[ "$FORCE_FEAT" -eq 1 || "$(has_fv_d "$D")" != "1" ]]; then
    NEED_FEAT=1
  fi
fi
if [[ "$SKIP_CORE" -eq 0 ]]; then
  if [[ "$FORCE_CORE" -eq 1 || "$(has_core_d "$D")" != "1" ]]; then
    NEED_CORE=1
  fi
fi

echo "計畫: need_feat=$NEED_FEAT need_core=$NEED_CORE predict+emit horizons=${HZ_ARR[*]} accept=2330@H20"

# --- 1 feat -----------------------------------------------------------------
if [[ "$NEED_FEAT" -eq 1 ]]; then
  run_step "feat" "$PY" scripts/build_feature_panel.py --panels "$D" --asof
else
  echo ""
  echo "── step: feat ── SKIP（已有 panel@$D 或 --skip-feat）"
fi

# --- 2 core -----------------------------------------------------------------
if [[ "$NEED_CORE" -eq 1 ]]; then
  if [[ "$CORE_FULL" -eq 1 ]]; then
    run_step "core-full" "$PY" scripts/build_core_universe.py \
      --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof --full-rebuild
  else
    run_step "core-incr" "$PY" scripts/build_core_universe.py \
      --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial \
      --asof --incremental --asof-date "$D" --skip-pan-hist
  fi
else
  echo ""
  echo "── step: core ── SKIP（已有 asof@$D 或 --skip-core）"
fi

# --- 3–4 predict ------------------------------------------------------------
if [[ "$SKIP_PREDICT" -eq 1 ]]; then
  echo ""
  echo "── step: predict ── SKIP（--skip-predict）"
else
  for h in "${HZ_ARR[@]}"; do
    h="$(echo "$h" | tr -d ' ')"
    [[ -n "$h" ]] || continue
    run_step "predict-H${h}" "$PY" scripts/predict_asof.py --run --horizon "$h" --asof "$D"
  done
fi

# --- 5–6 emit ---------------------------------------------------------------
if [[ "$SKIP_EMIT" -eq 1 ]]; then
  echo ""
  echo "── step: emit ── SKIP（--skip-emit）"
else
  for h in "${HZ_ARR[@]}"; do
    h="$(echo "$h" | tr -d ' ')"
    [[ -n "$h" ]] || continue
    run_step "emit-H${h}" "$PY" scripts/calibrate_relative_probability.py --emit --horizon "$h" --asof "$D"
  done
fi

# --- 7 accept ---------------------------------------------------------------
echo ""
echo "── step: accept ──"
if [[ "$DRY_PLAN" -eq 1 ]]; then
  echo "+ verify build_single_ticker_rel_payload('2330',20).as_of == $D"
  echo "  (dry-plan: 未執行)"
else
  GOT="$(verify_accept "$D")" || {
    echo "✗ 驗收失敗: payload.as_of=$GOT 期望 $D" >&2
    exit 4
  }
  echo "✓ accept as_of=$GOT == $D"
fi

echo ""
echo "══════════════════════════════════════════════════════"
if [[ "$DRY_PLAN" -eq 1 ]]; then
  echo "dry-plan 完成（零寫庫）。真跑去掉 --dry-plan。"
else
  echo "B3 鏈完成 D=$D"
fi
echo "══════════════════════════════════════════════════════"
