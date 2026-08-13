#!/usr/bin/env bash
# 🎯 L2 日更 ALL-RANK 薄殼 — RankRidge×5H＋challenger×8 → repredict/emit H20,60。
#
# 守: FZ/GATE-keep · skip-sync · no-SIM-apply · **no-promote** · NF-pause · **非 cron**
# 契約: reports/augur_daily_retrain_l2_all_rank_plan_20260812.md（邊界＝A）
# GO:   audits/DAILY-RETRAIN-L2-SHELL-GO-20260812.md
#
# 執行指令矩陣:
#   bash scripts/run_daily_retrain_l2_all_rank.sh --selftest
#   bash scripts/run_daily_retrain_l2_all_rank.sh --date 2026-08-11 --dry-plan
#   bash scripts/run_daily_retrain_l2_all_rank.sh --date 2026-08-11 --apply
#   bash scripts/run_daily_retrain_l2_all_rank.sh --date 2026-08-11 --apply --skip-challenger
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || { echo "✗ 找不到專案目錄 $ROOT" >&2; exit 1; }

PY="${ROOT}/venv/bin/python"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"

DATE=""
SEED=42
DRY_PLAN=0
DO_APPLY=0
SKIP_CHAL=0
FAIL_HARD_CHAL=0
SKIP_REPREDICT=0
SELFTEST=0
RESUME=1
LOGDIR=""

RIDGE_HS=(20 40 60 82 120)
# family:horizon pairs（邊界 A／鏡 0810·0811）
CHAL_SPECS=(
  "RankGBDT:20"
  "RankGBDT:60"
  "RankXGB:60"
  "RankCat:60"
  "RankRF:60"
  "RankKNN:60"
  "RankMLP:60"
  "RankSVM:20"
)
REPRED_HS=(20 60)

usage() {
  sed -n '2,14p' "$0" | sed 's/^# \?//'
  echo ""
  echo "選項: --date YYYY-MM-DD  --dry-plan  --apply  --selftest"
  echo "      --skip-challenger  --fail-hard-challenger  --skip-repredict"
  echo "      --seed N  --no-resume  --logdir DIR"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE="${2:-}"; shift 2 ;;
    --seed) SEED="${2:-}"; shift 2 ;;
    --dry-plan) DRY_PLAN=1; shift ;;
    --apply) DO_APPLY=1; shift ;;
    --skip-challenger) SKIP_CHAL=1; shift ;;
    --fail-hard-challenger) FAIL_HARD_CHAL=1; shift ;;
    --skip-repredict) SKIP_REPREDICT=1; shift ;;
    --no-resume) RESUME=0; shift ;;
    --logdir) LOGDIR="${2:-}"; shift 2 ;;
    --selftest) SELFTEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知參數: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ ! -x "$PY" ]]; then
  echo "✗ 找不到 $PY" >&2
  exit 1
fi

run_step() {
  local name="$1"; shift
  echo ""
  echo "── step: $name ──"
  if [[ "$DRY_PLAN" -eq 1 ]]; then
    echo "+ $*"
    echo "  (dry-plan: 未執行)"
    return 0
  fi
  echo "+ $*"
  "$@"
}

train_one() {
  local fam="$1" h="$2"
  local args=(scripts/train_ranker.py --run --family "$fam" --horizon "$h" --asof "$DATE" --seed "$SEED")
  if [[ "$RESUME" -eq 1 ]]; then
    args+=(--resume)
  fi
  run_step "train-${fam}-H${h}" "$PY" "${args[@]}"
}

# --- selftest（免 DB 寫；可連 DB 讀 max）------------------------------------
if [[ "$SELFTEST" -eq 1 ]]; then
  ok=1
  chk() { if [[ "$2" == "1" ]]; then echo "  ✓ $1"; else echo "  ✗FAIL $1"; ok=0; fi; }
  echo "[L2-ALL-RANK selftest]"
  chk "train_ranker.py 存在" "$([[ -f scripts/train_ranker.py ]] && echo 1 || echo 0)"
  chk "predict_asof.py 存在" "$([[ -f scripts/predict_asof.py ]] && echo 1 || echo 0)"
  chk "calibrate emit 存在" "$([[ -f scripts/calibrate_relative_probability.py ]] && echo 1 || echo 0)"
  chk "venv python" "$([[ -x $PY ]] && echo 1 || echo 0)"
  chk "Ridge 五 H" "$([[ ${#RIDGE_HS[@]} -eq 5 ]] && echo 1 || echo 0)"
  chk "challenger 八臂" "$([[ ${#CHAL_SPECS[@]} -eq 8 ]] && echo 1 || echo 0)"
  # 自測字串檢查：用 grep -E（勿依賴 rg；使用者 PATH 常無 ripgrep）
  _has() { grep -E -q -- "$1" "$2"; }
  chk "doc 禁 cron" "$(_has '非 cron|no-cron|禁 cron' "$0" && echo 1 || echo 0)"
  chk "doc no-promote" "$(_has 'no-promote' "$0" && echo 1 || echo 0)"
  # dry-plan 路徑煙測（不 --apply）
  if bash "$0" --date 2026-08-11 --dry-plan >/tmp/l2-allrank-selftest-dry.out 2>&1; then
    chk "dry-plan RC=0" 1
    chk "dry 含 RankRidge H20" "$(_has 'family RankRidge --horizon 20' /tmp/l2-allrank-selftest-dry.out && echo 1 || echo 0)"
    chk "dry 含 RankSVM" "$(_has 'RankSVM' /tmp/l2-allrank-selftest-dry.out && echo 1 || echo 0)"
    chk "dry 含 predict H60" "$(_has 'predict_asof.py --run --family RankRidge --horizon 60' /tmp/l2-allrank-selftest-dry.out && echo 1 || echo 0)"
    chk "dry 含 emit" "$(_has 'calibrate_relative_probability.py --emit' /tmp/l2-allrank-selftest-dry.out && echo 1 || echo 0)"
  else
    chk "dry-plan RC=0" 0
  fi
  if [[ "$ok" -eq 1 ]]; then
    echo "自測:全通過 ✓"
    exit 0
  fi
  echo "自測:有 FAIL ✗"
  exit 1
fi

if [[ -z "$DATE" ]]; then
  echo "✗ 須 --date YYYY-MM-DD（或 --selftest）" >&2
  usage
  exit 2
fi

if [[ "$DO_APPLY" -eq 1 && "$DRY_PLAN" -eq 1 ]]; then
  echo "✗ 勿同時 --apply 與 --dry-plan" >&2
  exit 2
fi

if [[ "$DO_APPLY" -eq 0 && "$DRY_PLAN" -eq 0 ]]; then
  echo "✗ 安全預設：請顯式 --dry-plan 或 --apply（P1 殼禁默訓）" >&2
  exit 2
fi

if [[ -z "$LOGDIR" ]]; then
  LOGDIR="/tmp/daily-retrain-l2-${DATE}"
fi
mkdir -p "$LOGDIR"

echo "══════════════════════════════════════════════════════"
echo "L2 ALL-RANK  D=$DATE  dry_plan=$DRY_PLAN  apply=$DO_APPLY  seed=$SEED"
echo "  skip_chal=$SKIP_CHAL fail_hard_chal=$FAIL_HARD_CHAL skip_repredict=$SKIP_REPREDICT resume=$RESUME"
echo "  logdir=$LOGDIR"
echo "  本殼不呼叫 sync／FinMind／cron／promote／sim-apply／NF／Daily*"
echo "══════════════════════════════════════════════════════"

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
REG_N="$("$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute(\"\"\"
      SELECT count(*) FROM model_registry
      WHERE asof_snapshot::text = %s
        AND family IN ('RankRidge','RankGBDT','RankXGB','RankCat','RankRF','RankKNN','RankMLP','RankSVM')
    \"\"\", ('$DATE',))
    print(cur.fetchone()[0])
" 2>/dev/null || echo "?")"
echo "錨: price_max=$PRICE_MAX fv_max=$FV_MAX core_max=$CORE_MAX registry_A@$DATE=$REG_N"

if [[ -z "$PRICE_MAX" || "$PRICE_MAX" < "$DATE" ]]; then
  echo "✗ 告警: PriceAdj TAIEX max($PRICE_MAX) < D($DATE) —— 整鏈 SKIP" >&2
  exit 3
fi

# --- 1 Ridge×5 ----------------------------------------------------------------
echo ""
echo "計畫: Ridge H=${RIDGE_HS[*]} + chal=${#CHAL_SPECS[@]} + repredict H=${REPRED_HS[*]}"
for h in "${RIDGE_HS[@]}"; do
  if [[ "$DRY_PLAN" -eq 1 ]]; then
    train_one RankRidge "$h"
  else
    train_one RankRidge "$h" 2>&1 | tee -a "$LOGDIR/ridge.log"
  fi
done
echo "RIDGE_PLAN_OR_DONE"

# --- 2 Challenger×8 -----------------------------------------------------------
chal_fail=0
if [[ "$SKIP_CHAL" -eq 1 ]]; then
  echo ""
  echo "── step: challenger ── SKIP（--skip-challenger）"
else
  for spec in "${CHAL_SPECS[@]}"; do
    fam="${spec%%:*}"
    h="${spec##*:}"
    if [[ "$DRY_PLAN" -eq 1 ]]; then
      train_one "$fam" "$h" || true
    else
      if ! train_one "$fam" "$h" 2>&1 | tee -a "$LOGDIR/challenger.log"; then
        echo "⚠ challenger 失敗: $fam H$h" >&2
        chal_fail=1
        if [[ "$FAIL_HARD_CHAL" -eq 1 ]]; then
          exit 5
        fi
      fi
    fi
  done
  echo "CHAL_PLAN_OR_DONE chal_fail=$chal_fail"
fi

# --- 3–4 repredict + emit ----------------------------------------------------
if [[ "$SKIP_REPREDICT" -eq 1 ]]; then
  echo ""
  echo "── step: repredict/emit ── SKIP（--skip-repredict）"
else
  for h in "${REPRED_HS[@]}"; do
    run_step "predict-H${h}" "$PY" scripts/predict_asof.py --run --family RankRidge --horizon "$h" --asof "$DATE"
    run_step "emit-H${h}" "$PY" scripts/calibrate_relative_probability.py --emit --horizon "$h" --asof "$DATE"
  done
fi

# --- 5 registry 尺（唯讀；dry 也印）------------------------------------------
echo ""
echo "── step: registry-check ──"
if [[ "$DRY_PLAN" -eq 1 ]]; then
  echo "+ expect model_registry asof_snapshot=$DATE family∈A-pack ≥13"
  echo "  (dry-plan: 未執行計數寫入)"
else
  N="$("$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute(\"\"\"
      SELECT count(*) FROM model_registry
      WHERE asof_snapshot::text = %s
        AND family IN ('RankRidge','RankGBDT','RankXGB','RankCat','RankRF','RankKNN','RankMLP','RankSVM')
    \"\"\", ('$DATE',))
    print(int(cur.fetchone()[0]))
")"
  echo "registry_A@$DATE = $N (驗收尺 ≥13)"
  if [[ "$N" -lt 13 ]]; then
    echo "⚠ 低於 13（若 --resume 且先前已有部分列，請核對缺臂）" >&2
  fi
fi

echo ""
echo "══════════════════════════════════════════════════════"
if [[ "$DRY_PLAN" -eq 1 ]]; then
  echo "dry-plan 完成（零寫庫）。真跑: --apply --date $DATE"
else
  echo "L2 ALL-RANK apply 完成 D=$DATE  chal_fail=$chal_fail  logdir=$LOGDIR"
  echo "護欄: no-promote（本殼未做 SERVE-SWAP）"
fi
echo "══════════════════════════════════════════════════════"
