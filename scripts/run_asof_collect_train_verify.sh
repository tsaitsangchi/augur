#!/usr/bin/env bash
# 🎯 歷史 as-of 閉環薄殼 — collect 特徵 → 邊界 A 訓練 → predict/emit 驗証。
#
# 守: FZ/GATE-keep · skip-sync · no-SIM-apply · **no-promote** · NF-pause · **非 cron**
#     · no-fake-B3（價 < D 整鏈 SKIP）· 勿重掃 0812 NF · 禮讓即將開火的 B3
# 契約: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md §3
#       reports/augur_s1s5_asof_verify_best_next_20260813.md WP-H
#
# 執行指令矩陣:
#   bash scripts/run_asof_collect_train_verify.sh --selftest
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-07 --dry-plan
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-07 --apply
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-07 --apply --ridge-only
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-13 --dry-plan   # 價未到 → rc=3
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || { echo "✗ 找不到專案目錄 $ROOT" >&2; exit 1; }

PY="${ROOT}/venv/bin/python"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"

DATE=""
DRY_PLAN=0
DO_APPLY=0
SKIP_COLLECT=0
SKIP_TRAIN=0
SKIP_VERIFY=0
RIDGE_ONLY=0
SELFTEST=0
LOCK="/tmp/augur_hist_asof.lock"

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \?//'
  echo ""
  echo "選項: --date YYYY-MM-DD  --dry-plan  --apply  --selftest"
  echo "      --skip-collect  --skip-train  --skip-verify  --ridge-only"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE="${2:-}"; shift 2 ;;
    --dry-plan) DRY_PLAN=1; shift ;;
    --apply) DO_APPLY=1; shift ;;
    --skip-collect) SKIP_COLLECT=1; shift ;;
    --skip-train) SKIP_TRAIN=1; shift ;;
    --skip-verify) SKIP_VERIFY=1; shift ;;
    --ridge-only) RIDGE_ONLY=1; shift ;;
    --selftest) SELFTEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知參數: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ ! -x "$PY" ]]; then
  echo "✗ 找不到 $PY" >&2
  exit 1
fi

if [[ "$SELFTEST" -eq 1 ]]; then
  ok=1
  chk() { if [[ "$2" == "1" ]]; then echo "  ✓ $1"; else echo "  ✗FAIL $1"; ok=0; fi; }
  echo "[HIST-ASOF selftest]"
  chk "check_asof_ready.py" "$([[ -f scripts/check_asof_ready.py ]] && echo 1 || echo 0)"
  chk "L2 殼" "$([[ -f scripts/run_daily_retrain_l2_all_rank.sh ]] && echo 1 || echo 0)"
  chk "build_feature_panel.py" "$([[ -f scripts/build_feature_panel.py ]] && echo 1 || echo 0)"
  chk "doc no-fake-B3" "$(grep -q 'no-fake-B3' "$0" && echo 1 || echo 0)"
  chk "doc no-promote" "$(grep -q 'no-promote' "$0" && echo 1 || echo 0)"
  if "$PY" -m augur.core.asof_ready --selftest >/tmp/hist-asof-lib-selftest.out 2>&1; then
    chk "asof_ready --selftest" 1
  else
    chk "asof_ready --selftest" 0
  fi
  if bash "$0" --date 2026-08-07 --dry-plan >/tmp/hist-asof-dry.out 2>&1; then
    chk "dry-plan 08-07 RC=0" 1
  else
    rc=$?
    if [[ "$rc" -eq 3 ]]; then
      echo "  ⚠ dry-plan rc=3（價閘；LIVE 若價頂<08-07 才合理）"
      chk "dry-plan 08-07 可執行" 1
    else
      chk "dry-plan 08-07 RC=0" 0
    fi
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
  echo "✗ 安全預設：請顯式 --dry-plan 或 --apply" >&2
  exit 2
fi

echo "══════════════════════════════════════════════════════"
echo "HIST-ASOF collect/train/verify  D=$DATE  dry=$DRY_PLAN apply=$DO_APPLY"
echo "  skip_collect=$SKIP_COLLECT skip_train=$SKIP_TRAIN skip_verify=$SKIP_VERIFY ridge_only=$RIDGE_ONLY"
echo "  本殼不 sync／不 promote／不 sim-apply／不開 NF／不改 LIVE 冠軍"
echo "══════════════════════════════════════════════════════"

set +e
"$PY" scripts/check_asof_ready.py --date "$DATE"
READY_RC=$?
set -e

if [[ "$READY_RC" -eq 3 || "$READY_RC" -eq 4 ]]; then
  echo "✗ 假 B3／無價 —— 整鏈 SKIP（歷史 as-of ≠ 假裝今天）" >&2
  exit "$READY_RC"
fi

# 禮讓：B3 日更心跳若已持 hist 鎖以外的進行中 apply，不搶；本殼用專鎖防自撞。
if [[ "$DO_APPLY" -eq 1 ]]; then
  exec 9>"$LOCK"
  if ! flock -n 9; then
    echo "✗ 另一輪 hist as-of 在跑（$LOCK）——不並發" >&2
    exit 5
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

# --- collect ----------------------------------------------------------------
if [[ "$SKIP_COLLECT" -eq 1 ]]; then
  echo ""
  echo "── step: collect ── SKIP（--skip-collect）"
elif [[ "$READY_RC" -eq 0 ]]; then
  echo ""
  echo "── step: collect ── SKIP（panel@$DATE 已在；截面族共用）"
else
  run_step "feat" "$PY" scripts/build_feature_panel.py --panels "$DATE" --asof
  run_step "core" "$PY" scripts/build_core_universe.py \
    --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial \
    --asof --incremental --asof-date "$DATE" --skip-pan-hist
fi

# --- train（邊界 A；各模型共用上一張 panel）--------------------------------
if [[ "$SKIP_TRAIN" -eq 1 ]]; then
  echo ""
  echo "── step: train ── SKIP（--skip-train）"
else
  L2=(bash scripts/run_daily_retrain_l2_all_rank.sh --date "$DATE")
  if [[ "$DRY_PLAN" -eq 1 ]]; then
    L2+=(--dry-plan)
  else
    L2+=(--apply)
  fi
  if [[ "$RIDGE_ONLY" -eq 1 ]]; then
    L2+=(--skip-challenger)
  fi
  echo ""
  echo "── step: train-L2-A ──"
  echo "+ ${L2[*]}"
  if [[ "$DRY_PLAN" -eq 1 ]]; then
    echo "  (dry-plan: 委派 L2 dry-plan)"
    "${L2[@]}"
  else
    "${L2[@]}"
  fi
fi

# --- verify（誠實 #14；不塗綠、不升格）--------------------------------------
if [[ "$SKIP_VERIFY" -eq 1 ]]; then
  echo ""
  echo "── step: verify ── SKIP"
elif [[ "$DRY_PLAN" -eq 1 ]]; then
  echo ""
  echo "── step: verify ──"
  echo "+ SELECT horizon,econ_verdict,count(*) FROM prediction_probability WHERE panel_date=$DATE"
  echo "  (dry-plan: 未執行)"
else
  echo ""
  echo "── step: verify ──"
  "$PY" -c "
from augur.core import db
d='$DATE'
with db.connect() as c, c.cursor() as cur:
    cur.execute('''
      SELECT family, count(*) FROM model_registry
      WHERE asof_snapshot::text=%s
      GROUP BY 1 ORDER BY 1
    ''', (d,))
    rows=cur.fetchall()
    print('registry@'+d)
    for r in rows:
        print(' ', r[0], r[1])
    cur.execute('''
      SELECT horizon, econ_verdict, count(*) FROM prediction_probability
      WHERE panel_date=%s GROUP BY 1,2 ORDER BY 1,2
    ''', (d,))
    ev=cur.fetchall()
    print('econ@'+d)
    if not ev:
        print('  (尚無 prediction_probability；L2 emit 後才有)')
    for r in ev:
        print(' ', 'H'+str(r[0]), r[1], r[2])
"
  echo "護欄: 上表＝誠實形；dead/thin ≠ 可交易；本殼未 SERVE-SWAP"
fi

echo ""
echo "══════════════════════════════════════════════════════"
if [[ "$DRY_PLAN" -eq 1 ]]; then
  echo "dry-plan 完成。真跑: --apply --date $DATE"
else
  echo "HIST-ASOF apply 完成 D=$DATE  no-promote"
fi
echo "══════════════════════════════════════════════════════"
