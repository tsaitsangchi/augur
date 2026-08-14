#!/usr/bin/env bash
# 🎯 所有生產 AI 預測模型重訓到指定 as-of（方向臂鎖＝可更新最新日／價頂）。
#
# 範圍: 截面 8 族 × H{20,40,60,82,120,240}（--resume 已有則跳過）
#       + 方向臂 DailyLogit/DailyGBDT/DailyGBDT_cal + MktLogit/MktLogit_v2 + DirStack/DirStackM
# 方向 H 軌封閉集＝H{20,40,60,82,120,240}（H240＝2026-08-14 另開；≠ v2/arena/threelens 家族）
# 方向臂 --asof／--until 未指定 → PriceAdj TAIEX 價頂（≠ 完整性錨 2026-05-31）
# 日更驅動（cron）＝ scripts/run_retrain_all_asof_daily.sh
# 誠實 SKIP: SeqLSTM（評測不寫庫）／classical TS 煙測／threelens 冒煙／0812 NF 六族
# 守: FZ/GATE-keep · skip-sync · no-SIM-apply · **no-promote** · NF-pause · **no-fake-B3**
# 契約: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
#
# 執行指令矩陣:
#   bash scripts/run_retrain_all_asof.sh --selftest
#   bash scripts/run_retrain_all_asof.sh --dry-plan          # D＝可更新最新日
#   bash scripts/run_retrain_all_asof.sh --date 2026-08-12 --dry-plan
#   bash scripts/run_retrain_all_asof.sh --date 2026-08-12 --apply --no-resume
#   bash scripts/run_retrain_all_asof.sh --date 2026-08-13 --dry-plan   # 價未到 → rc=3
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || { echo "✗ 找不到專案目錄 $ROOT" >&2; exit 1; }

PY="${ROOT}/venv/bin/python"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

DATE=""
DRY_PLAN=0
DO_APPLY=0
SELFTEST=0
SKIP_RANK=0
SKIP_DAILY=0
SKIP_MKT=0
SKIP_STACK=0
RESUME=1
SEED=42
LOCK="/tmp/augur_retrain_all_asof.lock"
LOGDIR=""

FAMILIES=(RankRidge RankGBDT RankXGB RankCat RankRF RankSVM RankKNN RankMLP)
HORIZONS=(20 40 60 82 120 240)

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \?//'
  echo ""
  echo "選項: --date YYYY-MM-DD（省略＝可更新最新日）  --dry-plan  --apply  --selftest"
  echo "      --skip-rank  --skip-daily  --skip-mkt  --skip-stack"
  echo "      --no-resume  --seed N  --logdir DIR"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE="${2:-}"; shift 2 ;;
    --dry-plan) DRY_PLAN=1; shift ;;
    --apply) DO_APPLY=1; shift ;;
    --selftest) SELFTEST=1; shift ;;
    --skip-rank) SKIP_RANK=1; shift ;;
    --skip-daily) SKIP_DAILY=1; shift ;;
    --skip-mkt) SKIP_MKT=1; shift ;;
    --skip-stack) SKIP_STACK=1; shift ;;
    --no-resume) RESUME=0; shift ;;
    --seed) SEED="${2:-}"; shift 2 ;;
    --logdir) LOGDIR="${2:-}"; shift 2 ;;
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

if [[ "$SELFTEST" -eq 1 ]]; then
  ok=1
  chk() { if [[ "$2" == "1" ]]; then echo "  ✓ $1"; else echo "  ✗FAIL $1"; ok=0; fi; }
  echo "[RETRAIN-ALL-ASOF selftest]"
  chk "train_ranker.py" "$([[ -f scripts/train_ranker.py ]] && echo 1 || echo 0)"
  chk "train_daily_direction.py" "$([[ -f scripts/train_daily_direction.py ]] && echo 1 || echo 0)"
  chk "train_market_direction.py" "$([[ -f scripts/train_market_direction.py ]] && echo 1 || echo 0)"
  chk "train_direction_stack.py" "$([[ -f scripts/train_direction_stack.py ]] && echo 1 || echo 0)"
  chk "8 族" "$([[ ${#FAMILIES[@]} -eq 8 ]] && echo 1 || echo 0)"
  chk "6 H" "$([[ ${#HORIZONS[@]} -eq 6 ]] && echo 1 || echo 0)"
  chk "doc no-promote" "$(grep -q 'no-promote' "$0" && echo 1 || echo 0)"
  chk "doc no-fake-B3" "$(grep -q 'no-fake-B3' "$0" && echo 1 || echo 0)"
  if "$PY" -m augur.core.asof_ready --selftest >/tmp/retrain-all-asof-lib.out 2>&1; then
    chk "asof_ready --selftest" 1
  else
    chk "asof_ready --selftest" 0
  fi
  latest="$("$PY" scripts/check_asof_ready.py --latest-date 2>/dev/null || true)"
  chk "latest-date ISO" "$([[ "$latest" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] && echo 1 || echo 0)"
  if bash "$0" --date 2026-08-12 --dry-plan >/tmp/retrain-all-asof-dry.out 2>&1; then
    chk "dry-plan 08-12 RC=0" 1
    chk "dry 含 RankCat H20" "$(grep -q 'family RankCat --horizon 20' /tmp/retrain-all-asof-dry.out && echo 1 || echo 0)"
    chk "dry 含 Daily --asof" "$(grep -q 'train_daily_direction.py --run --asof 2026-08-12' /tmp/retrain-all-asof-dry.out && echo 1 || echo 0)"
    chk "dry 含 DirStackM" "$(grep -q 'train_direction_stack.py --run-v2 --asof 2026-08-12' /tmp/retrain-all-asof-dry.out && echo 1 || echo 0)"
    chk "dry 含 RankCat H240" "$(grep -q 'family RankCat --horizon 240' /tmp/retrain-all-asof-dry.out && echo 1 || echo 0)"
    chk "方向 H 含 240" "$(grep -q 'H_HORIZONS = (20, 40, 60, 82, 120, 240)' scripts/train_market_direction.py && echo 1 || echo 0)"
    chk "月頻 rank 含 240" "$(grep -q 'H_RANKS = (20, 40, 60, 82, 240)' scripts/build_direction_stack_monthly.py && echo 1 || echo 0)"
    chk "DirStackM 預設含 240" "$(grep -q 'M_HORIZONS = (20, 40, 60, 82, 240)' scripts/train_direction_stack.py && echo 1 || echo 0)"
  else
    chk "dry-plan 08-12 RC=0" 0
  fi
  if bash "$0" --dry-plan >/tmp/retrain-all-asof-dry-latest.out 2>&1; then
    chk "dry-plan 無 --date RC=0" 1
    chk "dry 無 date 鎖最新" "$(grep -q "D=$latest" /tmp/retrain-all-asof-dry-latest.out && echo 1 || echo 0)"
  else
    chk "dry-plan 無 --date RC=0" 0
  fi
  set +e
  "$PY" scripts/train_daily_direction.py --run --asof 2026-08-14 --ks 5 >/tmp/retrain-all-fakeb3.out 2>&1
  rc=$?
  set -e
  chk "Daily 08-14 假 B3 rc=3" "$([[ "$rc" -eq 3 ]] && echo 1 || echo 0)"
  if [[ "$ok" -eq 1 ]]; then
    echo "自測:全通過 ✓"
    exit 0
  fi
  echo "自測:有 FAIL ✗"
  exit 1
fi

if [[ "$DO_APPLY" -eq 1 && "$DRY_PLAN" -eq 1 ]]; then
  echo "✗ 勿同時 --apply 與 --dry-plan" >&2
  exit 2
fi

if [[ "$DO_APPLY" -eq 0 && "$DRY_PLAN" -eq 0 ]]; then
  echo "✗ 安全預設：請顯式 --dry-plan 或 --apply" >&2
  exit 2
fi

if [[ -z "$DATE" ]]; then
  DATE="$("$PY" scripts/check_asof_ready.py --latest-date)"
  if [[ -z "$DATE" ]]; then
    echo "✗ 無可否更新最新日（價頂空）" >&2
    exit 4
  fi
  echo "方向臂鎖／as-of＝可更新最新日 $DATE"
fi

if [[ -z "$LOGDIR" ]]; then
  LOGDIR="/tmp/retrain-all-asof-${DATE}"
fi
mkdir -p "$LOGDIR"

echo "══════════════════════════════════════════════════════"
echo "RETRAIN-ALL-ASOF  D=$DATE  dry=$DRY_PLAN apply=$DO_APPLY seed=$SEED resume=$RESUME"
echo "  skip_rank=$SKIP_RANK skip_daily=$SKIP_DAILY skip_mkt=$SKIP_MKT skip_stack=$SKIP_STACK"
echo "  logdir=$LOGDIR"
echo "  本殼不 sync／不 promote／不 sim-apply／不開 NF／不改 LIVE 冠軍／不重 fit P6"
echo "══════════════════════════════════════════════════════"

set +e
"$PY" scripts/check_asof_ready.py --date "$DATE"
READY_RC=$?
set -e

if [[ "$READY_RC" -eq 3 ]]; then
  echo "✗ 假 B3：整鏈 SKIP" >&2
  exit 3
fi
if [[ "$READY_RC" -eq 4 ]]; then
  echo "✗ 無價：整鏈 SKIP" >&2
  exit 4
fi
if [[ "$READY_RC" -eq 2 ]]; then
  echo "✗ 需先 collect feature_values＠$DATE（本殼不 collect）" >&2
  exit 2
fi
if [[ "$READY_RC" -ne 0 ]]; then
  echo "✗ check_asof_ready rc=$READY_RC" >&2
  exit "$READY_RC"
fi

if [[ "$DO_APPLY" -eq 1 ]]; then
  exec 9>"$LOCK"
  if ! flock -n 9; then
    echo "✗ 已有重訓在跑（$LOCK）" >&2
    exit 5
  fi
fi

fail=0
mark_fail() {
  echo "✗ step FAIL: $1" >&2
  fail=1
}

# --- 1 截面 8×6 --------------------------------------------------------------
if [[ "$SKIP_RANK" -eq 1 ]]; then
  echo ""
  echo "── step: rank 8×6 ── SKIP"
else
  echo ""
  echo "計畫: ${#FAMILIES[@]} 族 × ${#HORIZONS[@]} H ＝ $(( ${#FAMILIES[@]} * ${#HORIZONS[@]} )) 格（resume=$RESUME）"
  for fam in "${FAMILIES[@]}"; do
    for h in "${HORIZONS[@]}"; do
      args=(scripts/train_ranker.py --run --family "$fam" --horizon "$h" --asof "$DATE" --seed "$SEED")
      if [[ "$RESUME" -eq 1 ]]; then
        args+=(--resume)
      fi
      if [[ "$DRY_PLAN" -eq 1 ]]; then
        run_step "train-${fam}-H${h}" "$PY" "${args[@]}"
      else
        if ! run_step "train-${fam}-H${h}" "$PY" "${args[@]}" 2>&1 | tee -a "$LOGDIR/rank.log"; then
          mark_fail "train-${fam}-H${h}"
        fi
      fi
    done
  done
fi

# --- 2 市場特徵 + MktLogit(/v2) ---------------------------------------------
if [[ "$SKIP_MKT" -eq 1 ]]; then
  echo ""
  echo "── step: market ── SKIP"
else
  if ! run_step "mkt-feat" "$PY" scripts/build_market_direction_features.py --run \
      --since 2026-08-01 --until "$DATE" 2>&1 | tee -a "$LOGDIR/mkt.log"; then
    mark_fail "mkt-feat"
  fi
  if ! run_step "MktLogit" "$PY" scripts/train_market_direction.py --run --asof "$DATE" \
      2>&1 | tee -a "$LOGDIR/mkt.log"; then
    mark_fail "MktLogit"
  fi
  if ! run_step "MktLogit_v2" "$PY" scripts/train_market_direction.py --run-v2 --asof "$DATE" \
      2>&1 | tee -a "$LOGDIR/mkt.log"; then
    mark_fail "MktLogit_v2"
  fi
fi

# --- 3 Daily* ----------------------------------------------------------------
if [[ "$SKIP_DAILY" -eq 1 ]]; then
  echo ""
  echo "── step: daily ── SKIP"
else
  if ! run_step "Daily-v1" "$PY" scripts/train_daily_direction.py --run --asof "$DATE" \
      2>&1 | tee -a "$LOGDIR/daily.log"; then
    mark_fail "Daily-v1"
  fi
  if ! run_step "Daily-v2" "$PY" scripts/train_daily_direction.py --run-v2 --ks 5 --seeds 3 --asof "$DATE" \
      2>&1 | tee -a "$LOGDIR/daily.log"; then
    mark_fail "Daily-v2"
  fi
fi

# --- 4 H240 OOS（DirStack 前置；不 P6 fit／emit）------------------------------
if [[ "$SKIP_STACK" -eq 1 ]]; then
  echo ""
  echo "── step: oos-h240 ── SKIP（隨 stack）"
else
  if ! run_step "oos-h240" "$PY" scripts/build_probability_oos_sample.py --run --horizon 240 \
      --asof "$DATE" 2>&1 | tee -a "$LOGDIR/oos-h240.log"; then
    mark_fail "oos-h240"
  fi
  if ! run_step "dgate-h240" "$PY" scripts/preregister_direction_gate.py --preregister-all \
      2>&1 | tee -a "$LOGDIR/stack.log"; then
    mark_fail "dgate-h240"
  fi
fi

# --- 5 月頻 stack + DirStack(/M) --------------------------------------------
if [[ "$SKIP_STACK" -eq 1 ]]; then
  echo ""
  echo "── step: stack ── SKIP"
else
  if ! run_step "stack-monthly" "$PY" scripts/build_direction_stack_monthly.py --run \
      --since 2017-01-01 --until "$DATE" 2>&1 | tee -a "$LOGDIR/stack.log"; then
    mark_fail "stack-monthly"
  fi
  if ! run_step "DirStack" "$PY" scripts/train_direction_stack.py --run --asof "$DATE" \
      2>&1 | tee -a "$LOGDIR/stack.log"; then
    mark_fail "DirStack"
  fi
  if ! run_step "DirStackM" "$PY" scripts/train_direction_stack.py --run-v2 --asof "$DATE" \
      2>&1 | tee -a "$LOGDIR/stack.log"; then
    mark_fail "DirStackM"
  fi
fi

echo ""
echo "SKIP（誠實、非失敗）: SeqLSTM／classical TS／threelens／0812 NF 六族／P6 重 fit／promote"
echo "══════════════════════════════════════════════════════"
if [[ "$fail" -ne 0 ]]; then
  echo "RETRAIN-ALL-ASOF D=$DATE 有失敗（見 $LOGDIR）"
  exit 1
fi
echo "RETRAIN-ALL-ASOF D=$DATE 完成（no-promote）"
exit 0
