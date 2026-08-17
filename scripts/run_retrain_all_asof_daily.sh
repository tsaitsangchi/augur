#!/usr/bin/env bash
# 🎯 RETRAIN-ALL-ASOF 日更驅動 — 鎖可更新最新日，重訓截面 8×H{5,10,20,40,60,90,120,240}＋方向臂。
#
# D＝PriceAdj TAIEX 價頂（≠ 日曆今天、≠ 完整性錨 2026-05-31）
# 價未進／假 B3 → 誠實 SKIP exit 0（cron 不當失敗）
# 有價無特徵 → collect feat／core 再訓（本驅動補齊；內殼仍不 sync）
# 該 D 包已齊 → SKIP（--force 才重跑）
# 守: FZ/GATE-keep · skip-sync · no-SIM-apply · **no-promote** · NF-pause · **no-fake-B3**
#     · 不 emit B3 · 不 SERVE-SWAP · 23:00 後不開工（讓 TWEVO）
# 契約: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
# 採納: audits/RETRAIN-ALL-ASOF-DAILY-CRON-ADOPTED-20260814.md
# 內殼: scripts/run_retrain_all_asof.sh
#
# 執行指令矩陣:
#   bash scripts/run_retrain_all_asof_daily.sh --selftest
#   bash scripts/run_retrain_all_asof_daily.sh --dry-plan
#   bash scripts/run_retrain_all_asof_daily.sh --apply
#   bash scripts/run_retrain_all_asof_daily.sh --date 2026-08-13 --dry-plan
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
FORCE=0
INNER="scripts/run_retrain_all_asof.sh"

usage() {
  sed -n '2,18p' "$0" | sed 's/^# \?//'
  echo ""
  echo "選項: --date YYYY-MM-DD（省略＝可更新最新日）  --dry-plan  --apply  --selftest  --force"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE="${2:-}"; shift 2 ;;
    --dry-plan) DRY_PLAN=1; shift ;;
    --apply) DO_APPLY=1; shift ;;
    --selftest) SELFTEST=1; shift ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知參數: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ ! -x "$PY" ]]; then
  echo "✗ 找不到 $PY" >&2
  exit 1
fi

_has() { grep -E -q -- "$1" "$2"; }

coverage_probe() {
  local d="$1"
  "$PY" - "$d" <<'PY'
import sys
from augur.core import asof_ready, db
from augur.core.closed_horizons import H_TRACK
d = sys.argv[1]
fams = list(asof_ready.A_FAMILIES)
hs = H_TRACK
daily_ids = ("DailyLogit", "DailyGBDT", "DailyGBDT_cal")
mkt_ids = ("MktLogit", "MktLogit_v2")
stack_ids = ("DirStackM",)
with db.connect() as conn, db.transaction(conn) as cur:
    cur.execute(
        """
        SELECT count(DISTINCT family || ':' || horizon::text)
          FROM model_registry
         WHERE family = ANY(%s)
           AND horizon = ANY(%s)
           AND asof_snapshot::text = %s
        """,
        (fams, list(hs), d),
    )
    rank_n = int(cur.fetchone()[0] or 0)
    cur.execute(
        """
        SELECT count(DISTINCT model_id) FROM model_registry
         WHERE model_id = ANY(%s) AND asof_snapshot::text = %s
        """,
        (list(daily_ids), d),
    )
    daily_n = int(cur.fetchone()[0] or 0)
    cur.execute(
        """
        SELECT count(DISTINCT model_id) FROM model_registry
         WHERE model_id = ANY(%s) AND asof_snapshot::text = %s
        """,
        (list(mkt_ids), d),
    )
    mkt_n = int(cur.fetchone()[0] or 0)
    cur.execute(
        """
        SELECT count(DISTINCT model_id) FROM model_registry
         WHERE model_id = ANY(%s) AND asof_snapshot::text = %s
        """,
        (list(stack_ids), d),
    )
    stack_n = int(cur.fetchone()[0] or 0)
need_rank = len(fams) * len(hs)
need_daily, need_mkt, need_stack = 3, 2, 1
ok = rank_n >= need_rank and daily_n >= need_daily and mkt_n >= need_mkt and stack_n >= need_stack
print(
    f"{'COMPLETE' if ok else 'INCOMPLETE'} rank={rank_n}/{need_rank} "
    f"daily={daily_n}/{need_daily} mkt={mkt_n}/{need_mkt} stack={stack_n}/{need_stack}"
)
sys.exit(0 if ok else 1)
PY
}

if [[ "$SELFTEST" -eq 1 ]]; then
  ok=1
  chk() { if [[ "$2" == "1" ]]; then echo "  ✓ $1"; else echo "  ✗FAIL $1"; ok=0; fi; }
  echo "[RETRAIN-ALL-ASOF-DAILY selftest]"
  chk "內殼" "$([[ -f $INNER ]] && echo 1 || echo 0)"
  chk "build_feature_panel" "$([[ -f scripts/build_feature_panel.py ]] && echo 1 || echo 0)"
  chk "build_core_universe" "$([[ -f scripts/build_core_universe.py ]] && echo 1 || echo 0)"
  chk "doc no-promote" "$(_has 'no-promote' "$0" && echo 1 || echo 0)"
  chk "doc no-fake-B3" "$(_has 'no-fake-B3' "$0" && echo 1 || echo 0)"
  chk "doc 不 emit" "$(_has '不 emit' "$0" && echo 1 || echo 0)"
  chk "doc 價頂鎖" "$(_has '價頂' "$0" && echo 1 || echo 0)"
  if bash "$0" --date 2026-08-12 --dry-plan >/tmp/retrain-all-asof-daily-dry.out 2>&1; then
    chk "dry-plan 08-12 RC=0" 1
    chk "dry 無 predict_asof" "$(_has 'predict_asof.py' /tmp/retrain-all-asof-daily-dry.out && echo 0 || echo 1)"
    chk "dry 無 SERVE-SWAP" "$(_has 'SERVE-SWAP' /tmp/retrain-all-asof-daily-dry.out && echo 0 || echo 1)"
  else
    chk "dry-plan 08-12 RC=0" 0
  fi
  if bash "$0" --dry-plan >/tmp/retrain-all-asof-daily-latest.out 2>&1; then
    chk "dry-plan 無 --date RC=0" 1
  else
    chk "dry-plan 無 --date RC=0" 0
  fi
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

hhmm="$(TZ=Asia/Taipei date +%H%M)"
if [[ "$DO_APPLY" -eq 1 && "$hhmm" > "2259" ]]; then
  echo "SKIP: 台北 $hhmm ≥ 23:00，不開工以免撞 TWEVO"
  exit 0
fi

if [[ -z "$DATE" ]]; then
  DATE="$("$PY" scripts/check_asof_ready.py --latest-date)"
  if [[ -z "$DATE" ]]; then
    echo "SKIP: 無可否更新最新日（價頂空）"
    exit 0
  fi
  echo "方向臂鎖／as-of＝可更新最新日 $DATE"
fi

echo "══════════════════════════════════════════════════════"
echo "RETRAIN-ALL-ASOF-DAILY  D=$DATE  dry=$DRY_PLAN apply=$DO_APPLY force=$FORCE"
echo "  不 sync／不 promote／不 sim-apply／不 emit B3／不開 NF"
echo "══════════════════════════════════════════════════════"

set +e
"$PY" scripts/check_asof_ready.py --date "$DATE"
READY_RC=$?
set -e

if [[ "$READY_RC" -eq 3 || "$READY_RC" -eq 4 ]]; then
  echo "SKIP: 假 B3／無價（D=$DATE rc=$READY_RC）——不把日曆今天當成已有價"
  exit 0
fi

cov_out=""
set +e
cov_out="$(coverage_probe "$DATE")"
COV_RC=$?
set -e
echo "覆蓋: $cov_out"

if [[ "$FORCE" -eq 0 && "$COV_RC" -eq 0 ]]; then
  nH="$("$PY" -c 'from augur.core.closed_horizons import H_TRACK; print(len(H_TRACK))')"
  echo "SKIP: 包已齊＠$DATE（8×${nH}＋Daily*＋Mkt*＋DirStackM）。--force 才重跑"
  exit 0
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

if [[ "$READY_RC" -eq 2 ]]; then
  run_step "feat" "$PY" scripts/build_feature_panel.py --panels "$DATE" --asof
  run_step "core" "$PY" scripts/build_core_universe.py \
    --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial \
    --asof --incremental --asof-date "$DATE" --skip-pan-hist
  if [[ "$DRY_PLAN" -eq 0 ]]; then
    set +e
    "$PY" scripts/check_asof_ready.py --date "$DATE"
    READY_RC=$?
    set -e
    if [[ "$READY_RC" -ne 0 ]]; then
      echo "✗ collect 後仍未 ready rc=$READY_RC" >&2
      exit 1
    fi
  fi
fi

inner=(bash "$INNER" --date "$DATE")
if [[ "$DRY_PLAN" -eq 1 ]]; then
  inner+=(--dry-plan)
else
  inner+=(--apply)
fi

echo ""
echo "── step: retrain-all ──"
echo "+ ${inner[*]}"
set +e
"${inner[@]}"
INNER_RC=$?
set -e
if [[ "$INNER_RC" -eq 5 ]]; then
  echo "SKIP: 已有重訓在跑（鎖）"
  exit 0
fi
if [[ "$INNER_RC" -eq 3 || "$INNER_RC" -eq 4 ]]; then
  echo "SKIP: 內殼假 B3／無價 rc=$INNER_RC"
  exit 0
fi
if [[ "$INNER_RC" -ne 0 ]]; then
  echo "✗ 內殼 rc=$INNER_RC" >&2
  exit "$INNER_RC"
fi
echo "RETRAIN-ALL-ASOF-DAILY D=$DATE 完成（no-promote；未 emit）"
exit 0
