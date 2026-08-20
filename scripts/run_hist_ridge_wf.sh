#!/usr/bin/env bash
# 🎯 HIST-RIDGE-WF-v1 — 歷史日：特徵 → 核心宇宙 → RankRidge 八窗訓 → 八窗分數。
#
# 守: no-fake-B3 · no-promote · no-SIM-apply · NF-pause · standing 不改
#     · 只 RankRidge × H_TRACK · 不覆寫方向臂 · 不重建既有 tip 核心
# 契約: reports/augur_hist_ridge_wf_plan_r21_20260820.md
#
# 執行指令矩陣:
#   bash scripts/run_hist_ridge_wf.sh --selftest
#   bash scripts/run_hist_ridge_wf.sh --date 2026-07-07 --dry-plan
#   bash scripts/run_hist_ridge_wf.sh --date 2026-07-07 --apply
#   bash scripts/run_hist_ridge_wf.sh --date 2026-08-20 --apply   # rc=3
# 批次（月尾河／月中河）:
#   python scripts/run_hist_ridge_wf_batch.py --month-ends --collect-only --apply
#   python scripts/run_hist_ridge_wf_batch.py --month-ends --train-predict --apply --from 2015-01-30
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
SKIP_COLLECT=0
SKIP_TRAIN=0
SKIP_PREDICT=0
SELFTEST=0
LOCK="/tmp/augur_hist_ridge_wf.lock"
HORIZONS=(5 10 20 40 60 90 120 240)

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \?//'
  echo ""
  echo "選項: --date YYYY-MM-DD  --dry-plan  --apply  --selftest"
  echo "      --skip-collect  --skip-train  --skip-predict"
  echo "月尾批次見 scripts/run_hist_ridge_wf_batch.py"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE="${2:-}"; shift 2 ;;
    --dry-plan) DRY_PLAN=1; shift ;;
    --apply) DO_APPLY=1; shift ;;
    --skip-collect) SKIP_COLLECT=1; shift ;;
    --skip-train) SKIP_TRAIN=1; shift ;;
    --skip-predict) SKIP_PREDICT=1; shift ;;
    --selftest) SELFTEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知參數: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ ! -x "$PY" ]]; then
  echo "✗ 找不到 $PY" >&2
  exit 2
fi

if [[ "$SELFTEST" -eq 1 ]]; then
  ok=1
  chk() { if [[ "$2" == "1" ]]; then echo "  ✓ $1"; else echo "  ✗FAIL $1"; ok=0; fi; }
  echo "[HIST-RIDGE-WF selftest]"
  chk "plan" "$([[ -f reports/augur_hist_ridge_wf_plan_r21_20260820.md ]] && echo 1 || echo 0)"
  chk "train_ranker" "$([[ -f scripts/train_ranker.py ]] && echo 1 || echo 0)"
  chk "predict_asof" "$([[ -f scripts/predict_asof.py ]] && echo 1 || echo 0)"
  chk "build_feature_panel" "$([[ -f scripts/build_feature_panel.py ]] && echo 1 || echo 0)"
  chk "build_core" "$([[ -f scripts/build_core_universe.py ]] && echo 1 || echo 0)"
  chk "八窗" "$([[ ${#HORIZONS[@]} -eq 8 ]] && echo 1 || echo 0)"
  set +e
  bash "$0" --date D --dry-plan >/tmp/hist-ridge-wf-ph.out 2>&1
  rc=$?
  set -e
  chk "佔位符 D rc=2" "$([[ "$rc" -eq 2 ]] && echo 1 || echo 0)"
  set +e
  FAKE="$("$PY" scripts/check_asof_ready.py --fake-b3-date)"
  bash "$0" --date "$FAKE" --dry-plan >/tmp/hist-ridge-wf-fake.out 2>&1
  rc=$?
  set -e
  chk "假 B3 dry rc=3" "$([[ "$rc" -eq 3 ]] && echo 1 || echo 0)"
  if [[ "$ok" -eq 1 ]]; then
    echo "自測:全通過 ✓"
    exit 0
  fi
  echo "自測:有 FAIL ✗"
  exit 1
fi

if [[ -z "$DATE" ]]; then
  echo "✗ 須 --date YYYY-MM-DD" >&2
  usage
  exit 2
fi
if [[ ! "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "✗ --date 須 YYYY-MM-DD（D 是佔位符）" >&2
  exit 2
fi
if [[ "$DO_APPLY" -eq 1 && "$DRY_PLAN" -eq 1 ]]; then
  echo "✗ 勿同時 --apply 與 --dry-plan" >&2
  exit 2
fi
if [[ "$DO_APPLY" -eq 0 && "$DRY_PLAN" -eq 0 ]]; then
  echo "✗ 請顯式 --dry-plan 或 --apply" >&2
  exit 2
fi

echo "══════════════════════════════════════════════════════"
echo "HIST-RIDGE-WF-v1  D=$DATE  dry=$DRY_PLAN apply=$DO_APPLY"
echo "  RankRidge × ${HORIZONS[*]}  不改 standing 不 promote 不覆寫方向臂"
echo "══════════════════════════════════════════════════════"

set +e
"$PY" scripts/check_asof_ready.py --date "$DATE"
READY_RC=$?
set -e

if [[ "$READY_RC" -eq 3 || "$READY_RC" -eq 4 ]]; then
  echo "✗ 假 B3／無價 —— 整鏈 SKIP" >&2
  exit "$READY_RC"
fi

if [[ "$DO_APPLY" -eq 1 ]]; then
  exec 9>"$LOCK"
  if ! flock -n 9; then
    echo "✗ 另一輪 HIST-RIDGE-WF 在跑（$LOCK）" >&2
    exit 5
  fi
  if [[ -f /tmp/augur_hist_asof.lock ]]; then
    exec 8</tmp/augur_hist_asof.lock
    if ! flock -n 8; then
      echo "✗ HIST-ASOF 持鎖中，本槍讓路" >&2
      exit 5
    fi
  fi
fi

run_step() {
  local name="$1"; shift
  echo ""
  echo "── step: $name ──"
  echo "+ $*"
  if [[ "$DRY_PLAN" -eq 1 ]]; then
    echo "  (dry-plan: 未執行)"
    return 0
  fi
  "$@"
}

run_step_soft() {
  local name="$1"; shift
  echo ""
  echo "── step: $name ──"
  echo "+ $*"
  if [[ "$DRY_PLAN" -eq 1 ]]; then
    echo "  (dry-plan: 未執行)"
    return 0
  fi
  set +e
  "$@"
  local rc=$?
  set -e
  if [[ "$rc" -ne 0 ]]; then
    echo "⚠ $name rc=$rc（不中止其餘窗）" >&2
    return "$rc"
  fi
  return 0
}

HAS_CORE="$("$PY" - "$DATE" <<'PY'
import sys
from augur.core import asof_ready, db
d = sys.argv[1]
with db.connect() as conn, conn.cursor() as cur:
    snap = asof_ready.snapshot(cur, d)
print("1" if snap.get("has_core") else "0")
PY
)"

if [[ "$SKIP_COLLECT" -eq 1 ]]; then
  echo ""
  echo "── step: collect ── SKIP"
elif [[ "$READY_RC" -eq 2 ]]; then
  run_step "feat" "$PY" scripts/build_feature_panel.py --panels "$DATE" --asof
  run_step "core" "$PY" scripts/build_core_universe.py \
    --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial \
    --asof --incremental --asof-date "$DATE" --skip-pan-hist
elif [[ "$READY_RC" -eq 0 && "$HAS_CORE" != "1" ]]; then
  run_step "core" "$PY" scripts/build_core_universe.py \
    --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial \
    --asof --incremental --asof-date "$DATE" --skip-pan-hist
elif [[ "$READY_RC" -eq 0 ]]; then
  echo ""
  echo "── step: collect ── SKIP（panel+core@$DATE 已在）"
else
  echo ""
  echo "── step: collect ── SKIP（status rc=$READY_RC）"
fi

if [[ "$SKIP_TRAIN" -eq 1 ]]; then
  echo ""
  echo "── step: train RankRidge 8H ── SKIP"
else
  for h in "${HORIZONS[@]}"; do
    run_step_soft "train H$h" "$PY" scripts/train_ranker.py --run --family RankRidge \
      --horizon "$h" --asof "$DATE" --resume || true
  done
fi

if [[ "$SKIP_PREDICT" -eq 1 ]]; then
  echo ""
  echo "── step: predict RankRidge 8H ── SKIP"
else
  for h in "${HORIZONS[@]}"; do
    run_step_soft "predict H$h" "$PY" scripts/predict_asof.py --run --family RankRidge \
      --horizon "$h" --asof "$DATE" --top-n 3 || true
  done
fi

echo ""
echo "── verify ──"
"$PY" - "$DATE" "$DO_APPLY" "$SKIP_PREDICT" <<'PY'
import sys
from augur.core import asof_ready, db
from augur.core.closed_horizons import H_TRACK
d = sys.argv[1]
apply = int(sys.argv[2])
skip_pred = int(sys.argv[3])
with db.connect() as conn, conn.cursor() as cur:
    snap = asof_ready.snapshot(cur, d)
    cur.execute("SELECT count(*) FROM core_universe_asof WHERE as_of_date=%s", (d,))
    n_core = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM core_universe_asof WHERE as_of_date=%s", (snap["price_max"],))
    n_tip = cur.fetchone()[0]
    cur.execute(
        """
        SELECT m.horizon, count(*)
          FROM prediction_values pv
          JOIN model_registry m ON m.model_id=pv.model_id
         WHERE pv.panel_date=%s AND m.family='RankRidge'
         GROUP BY 1 ORDER BY 1
        """,
        (d,),
    )
    emit = cur.fetchall()
    cur.execute(
        """
        SELECT horizon FROM model_registry
         WHERE family='RankRidge' AND asof_snapshot=%s
         ORDER BY 1
        """,
        (d,),
    )
    hs = [r[0] for r in cur.fetchall()]
print("snapshot status=%s price_max=%s fv_nfeat=%s has_core=%s" % (
    snap.get("status"), snap.get("price_max"), snap.get("fv_nfeat"), snap.get("has_core")))
print("core@%s=%s  core@tip(%s)=%s" % (d, n_core, snap.get("price_max"), n_tip))
print("RankRidge registry@%s horizons=%s" % (d, hs))
print("prediction_values RankRidge@%s" % d)
if not emit:
    print("  (無列)")
for h, n in emit:
    print("  H%s n=%s" % (h, n))
need = list(H_TRACK)
have = [int(h) for h, _n in emit]
missing = [h for h in need if h not in have]
print("八窗分數缺=%s" % (missing or "無"))
print("護欄: standing 未改；分數≠報酬％；本殼未 SERVE-SWAP")
if apply and not skip_pred and missing:
    raise SystemExit(1)
PY

echo ""
echo "HIST-RIDGE-WF D=$DATE 結束 dry=$DRY_PLAN apply=$DO_APPLY"
