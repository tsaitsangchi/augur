#!/usr/bin/env bash
# 🎯 歷史 as-of 閉環薄殼 — collect 特徵 → 訓練 → 驗証（截面共用 panel；方向臂另軸）。
#
# 守: FZ/GATE-keep · skip-sync · no-SIM-apply · **no-promote** · NF-pause · **非 cron**
#     · no-fake-B3（價 < D 整鏈 SKIP）· 勿重掃 0812 NF · 禮讓即將開火的 B3
# 契約: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md §3
#       reports/augur_s1s5_asof_verify_best_next_20260813.md WP-H
#
# 執行指令矩陣:
#   bash scripts/run_asof_collect_train_verify.sh --selftest
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-14 --dry-plan
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-14 --dry-plan --track all
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-07-31 --apply --track all   # 截面；方向臂不覆寫價頂
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-14 --dry-plan --track other  # V0 盤點 rc=0
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-18 --dry-plan   # 價未到 → rc=3
#   bash scripts/run_asof_collect_train_verify.sh --date 2026-07-31 --apply --track other  # rc=6 不開訓
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
TRACK="A"
SKIP_REPRED=0
FORCE=0
FORCE_DIR=0
SELFTEST=0
LOCK="/tmp/augur_hist_asof.lock"

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \?//'
  echo ""
  echo "選項: --date YYYY-MM-DD  --dry-plan  --apply  --selftest"
  echo "      --track A|all|other（A＝L2 邊界 A；all＝8×8；other dry-plan＝V0 盤點；other --apply＝rc=6 不開訓）"
  echo "      --skip-collect  --skip-train  --skip-verify  --ridge-only  --skip-repredict  --force"
  echo "      --force-direction（歷史 D 才覆寫方向臂活鎖；預設禁）"
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
    --skip-repredict) SKIP_REPRED=1; shift ;;
    --force) FORCE=1; shift ;;
    --force-direction) FORCE_DIR=1; shift ;;
    --track)
      TRACK="${2:-}"
      shift 2
      ;;
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
  chk "verify 有 --oos" "$(grep -q -- '--oos' scripts/verify_asof_families.py && echo 1 || echo 0)"
  chk "verify 有 --walk" "$(grep -q -- '--walk' scripts/verify_asof_families.py && echo 1 || echo 0)"
  chk "verify 有 --horizon" "$(grep -q -- '--horizon' scripts/verify_asof_families.py && echo 1 || echo 0)"
  chk "L2 殼" "$([[ -f scripts/run_daily_retrain_l2_all_rank.sh ]] && echo 1 || echo 0)"
  chk "RETRAIN-ALL 內殼" "$([[ -f scripts/run_retrain_all_asof.sh ]] && echo 1 || echo 0)"
  chk "build_feature_panel.py" "$([[ -f scripts/build_feature_panel.py ]] && echo 1 || echo 0)"
  chk "doc no-fake-B3" "$(grep -q 'no-fake-B3' "$0" && echo 1 || echo 0)"
  chk "doc no-promote" "$(grep -q 'no-promote' "$0" && echo 1 || echo 0)"
  if "$PY" -m augur.core.asof_ready --selftest >/tmp/hist-asof-lib-selftest.out 2>&1; then
    chk "asof_ready --selftest" 1
  else
    chk "asof_ready --selftest" 0
  fi
  if bash "$0" --date 2026-08-14 --dry-plan >/tmp/hist-asof-dry.out 2>&1; then
    chk "dry-plan 08-14 RC=0" 1
  else
    rc=$?
    if [[ "$rc" -eq 3 ]]; then
      echo "  ⚠ dry-plan rc=3（價閘；LIVE 若價頂<08-14 才合理）"
      chk "dry-plan 08-14 可執行" 1
    else
      chk "dry-plan 08-14 RC=0" 0
    fi
  fi
  if bash "$0" --date 2026-08-14 --dry-plan --track all >/tmp/hist-asof-dry-all.out 2>&1; then
    chk "dry-plan --track all RC=0" 1
  else
    chk "dry-plan --track all RC=0" 0
  fi
  if bash "$0" --date 2026-07-31 --dry-plan --track all >/tmp/hist-asof-dry-0731.out 2>&1; then
    chk "dry 07-31 截面已齊跳過訓" "$(grep -q 'SKIP（包已齊' /tmp/hist-asof-dry-0731.out && echo 1 || echo 0)"
    chk "dry 07-31 無建議覆寫方向臂" "$(grep -q 'train_daily_direction.py' /tmp/hist-asof-dry-0731.out && echo 0 || echo 1)"
  else
    chk "dry 07-31 截面已齊跳過訓" 0
  fi
  LATEST_TIP="$("$PY" scripts/check_asof_ready.py --latest-date)"
  if bash "$0" --date "$LATEST_TIP" --dry-plan --track all --force >/tmp/hist-asof-dry-force.out 2>&1; then
    chk "dry --force RC=0" 1
    chk "dry force 含 Daily" "$(grep -q 'train_daily_direction.py' /tmp/hist-asof-dry-force.out && echo 1 || echo 0)"
    chk "dry force 無 predict_asof" "$(grep -q 'predict_asof.py' /tmp/hist-asof-dry-force.out && echo 0 || echo 1)"
    chk "dry force 傳 --no-resume" "$(grep -q -- '--no-resume' /tmp/hist-asof-dry-force.out && echo 1 || echo 0)"
  else
    chk "dry --force RC=0" 0
  fi
  if bash "$0" --date 2026-07-31 --dry-plan --track all --force >/tmp/hist-asof-dry-0731-force.out 2>&1; then
    chk "force hist RC=0" 1
    chk "force hist 跳過 Daily" "$(grep -q 'step: daily ── SKIP' /tmp/hist-asof-dry-0731-force.out && echo 1 || echo 0)"
    chk "force hist 跳過 market" "$(grep -q 'step: market ── SKIP' /tmp/hist-asof-dry-0731-force.out && echo 1 || echo 0)"
    chk "force hist 跳過 stack" "$(grep -q 'step: stack ── SKIP' /tmp/hist-asof-dry-0731-force.out && echo 1 || echo 0)"
    chk "force hist 仍含 Rank" "$(grep -q 'train_ranker.py' /tmp/hist-asof-dry-0731-force.out && echo 1 || echo 0)"
    chk "force hist 宣告不覆寫" "$(grep -q '不覆寫 Daily/Mkt/DirStackM' /tmp/hist-asof-dry-0731-force.out && echo 1 || echo 0)"
  else
    chk "force hist RC=0" 0
  fi
  set +e
  bash "$0" --date 2026-08-18 --dry-plan >/tmp/hist-asof-fake.out 2>&1
  rc=$?
  set -e
  chk "dry 08-18 假 B3 rc=3" "$([[ "$rc" -eq 3 ]] && echo 1 || echo 0)"
  set +e
  bash "$0" --date 2026-08-14 --dry-plan --track other >/tmp/hist-asof-other.out 2>&1
  rc=$?
  set -e
  chk "dry other rc=0" "$([[ "$rc" -eq 0 ]] && echo 1 || echo 0)"
  chk "dry other 含 VECM" "$(grep -q 'VECM' /tmp/hist-asof-other.out && echo 1 || echo 0)"
  chk "dry other 禁 0812 NF" "$(grep -q 'GarchMeanDir' /tmp/hist-asof-other.out && echo 1 || echo 0)"
  chk "dry other 無 train_ranker" "$(grep -q 'train_ranker.py' /tmp/hist-asof-other.out && echo 0 || echo 1)"
  chk "dry other 含族矩陣" "$(grep -q 'RankRidge' /tmp/hist-asof-other.out && echo 1 || echo 0)"
  set +e
  bash "$0" --date 2026-08-18 --dry-plan --track other >/tmp/hist-asof-other-fake.out 2>&1
  rc=$?
  set -e
  chk "other+假 B3 仍 rc=3" "$([[ "$rc" -eq 3 ]] && echo 1 || echo 0)"
  set +e
  bash "$0" --date 2026-08-14 --apply --track other >/tmp/hist-asof-other-apply.out 2>&1
  rc=$?
  set -e
  chk "apply other rc=6" "$([[ "$rc" -eq 6 ]] && echo 1 || echo 0)"
  set +e
  bash "$0" --date D --dry-plan >/tmp/hist-asof-placeholder.out 2>&1
  rc=$?
  set -e
  chk "dry 佔位符 D rc=2" "$([[ "$rc" -eq 2 ]] && echo 1 || echo 0)"
  chk "dry 佔位符說明" "$(grep -q '佔位符' /tmp/hist-asof-placeholder.out && echo 1 || echo 0)"
  if "$PY" scripts/check_asof_ready.py --scan >/tmp/hist-asof-scan.out 2>&1; then
    chk "scan RC=0" 1
    chk "scan 含未齊日" "$(grep -qE '2026-08-12|2026-08-11|2026-08-10' /tmp/hist-asof-scan.out && echo 1 || echo 0)"
  else
    chk "scan RC=0" 0
  fi
  set +e
  "$PY" scripts/verify_asof_families.py --walk --horizon 82 >/tmp/hist-h82.out 2>&1
  rc=$?
  set -e
  chk "horizon 82 拒 rc=2" "$([[ "$rc" -eq 2 ]] && echo 1 || echo 0)"
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
if [[ ! "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "✗ --date 須 YYYY-MM-DD（D 是佔位符，例如 2026-08-07）" >&2
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

TRACK="$(echo "$TRACK" | tr '[:lower:]' '[:upper:]')"
if [[ "$TRACK" != "A" && "$TRACK" != "ALL" && "$TRACK" != "OTHER" ]]; then
  echo "✗ --track 只准 A、all 或 other" >&2
  exit 2
fi

echo "══════════════════════════════════════════════════════"
echo "HIST-ASOF collect/train/verify  D=$DATE  dry=$DRY_PLAN apply=$DO_APPLY track=$TRACK force=$FORCE force_dir=$FORCE_DIR"
echo "  skip_collect=$SKIP_COLLECT skip_train=$SKIP_TRAIN skip_verify=$SKIP_VERIFY ridge_only=$RIDGE_ONLY skip_repredict=$SKIP_REPRED"
echo "  本殼不 sync／不 promote／不 sim-apply／不開 NF／不改 LIVE 冠軍"
echo "  歷史 D≠價頂：track=all 預設不覆寫 Daily*/Mkt/DirStackM"
echo "══════════════════════════════════════════════════════"

set +e
"$PY" scripts/check_asof_ready.py --date "$DATE"
READY_RC=$?
set -e

if [[ "$READY_RC" -eq 3 || "$READY_RC" -eq 4 ]]; then
  echo "✗ 假 B3／無價 —— 整鏈 SKIP（歷史 as-of ≠ 假裝今天）" >&2
  exit "$READY_RC"
fi

if [[ "$TRACK" == "OTHER" ]]; then
  echo ""
  "$PY" - <<'PY'
from augur.core import asof_ready
print(asof_ready.other_lane_refuse_msg(), end="")
PY
  if [[ "$DO_APPLY" -eq 1 ]]; then
    echo "✗ --track other --apply 不開訓（殘格須點名 GO；0812 NF 禁重掃；盤點請 --dry-plan）" >&2
    exit 6
  fi
  echo ""
  echo "── step: other-verify（V0 盤點；不訓）──"
  echo "+ $PY scripts/verify_asof_families.py --date $DATE"
  "$PY" scripts/verify_asof_families.py --date "$DATE"
  echo ""
  echo "══════════════════════════════════════════════════════"
  echo "other dry-plan 完成。OOS IC：python scripts/verify_asof_families.py --date $DATE --ic --oos"
  echo "walk：python scripts/verify_asof_families.py --walk --oos --horizon 5"
  echo "開訓截面 8 族請 --track all；--apply --track other 仍 rc=6"
  echo "══════════════════════════════════════════════════════"
  exit 0
fi

PACK_COMPLETE="$("$PY" - "$DATE" <<'PY'
import sys
from augur.core import asof_ready, db
d = sys.argv[1]
with db.connect() as conn, conn.cursor() as cur:
    snap = asof_ready.snapshot(cur, d)
print("1" if snap.get("pack_complete") else "0")
PY
)"

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

# --- train（A＝L2 邊界 A；all＝RETRAIN-ALL 內殼，不 emit B3）----------------
if [[ "$SKIP_TRAIN" -eq 1 ]]; then
  echo ""
  echo "── step: train ── SKIP（--skip-train）"
elif [[ "$PACK_COMPLETE" == "1" && "$FORCE" -eq 0 ]]; then
  echo ""
  echo "── step: train ── SKIP（包已齊＠$DATE；同尺再訓須 --force）"
  echo "  pack_complete=True  A格已齊＠$DATE（方向臂只在價頂列入包）"
  echo "  下一槍：未齊的歷史 D 或候新價 B3；不要對同一天 apply（同尺）"
elif [[ "$TRACK" == "ALL" ]]; then
  ALL=(bash scripts/run_retrain_all_asof.sh --date "$DATE")
  if [[ "$DRY_PLAN" -eq 1 ]]; then
    ALL+=(--dry-plan)
  else
    ALL+=(--apply)
  fi
  if [[ "$FORCE" -eq 1 ]]; then
    ALL+=(--no-resume)
    echo ""
    echo "同尺重訓：--force → 內殼 --no-resume（已登錄格也重 fit；不 promote）"
  fi
  LATEST="$("$PY" scripts/check_asof_ready.py --latest-date)"
  if [[ "$DATE" != "$LATEST" && "$FORCE_DIR" -eq 0 ]]; then
    ALL+=(--skip-daily --skip-mkt --skip-stack)
    echo ""
    echo "方向臂鎖＝價頂 $LATEST；歷史 D=$DATE 不覆寫 Daily/Mkt/DirStackM（--force-direction 才動）"
  elif [[ "$DATE" != "$LATEST" && "$FORCE_DIR" -eq 1 ]]; then
    echo ""
    echo "⚠ --force-direction：將把活鎖 Daily/Mkt/DirStackM 從 $LATEST 覆寫成 $DATE"
  fi
  echo ""
  echo "── step: train-RETRAIN-ALL ──"
  echo "+ ${ALL[*]}"
  "${ALL[@]}"
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
  if [[ "$SKIP_REPRED" -eq 1 ]]; then
    L2+=(--skip-repredict)
  fi
  echo ""
  echo "── step: train-L2-A ──"
  echo "+ ${L2[*]}"
  "${L2[@]}"
fi

# --- verify（唯讀；dry-plan 也跑，不算訓）-----------------------------------
if [[ "$SKIP_VERIFY" -eq 1 ]]; then
  echo ""
  echo "── step: verify ── SKIP"
else
  echo ""
  echo "── step: verify ──"
  "$PY" - "$DATE" <<'PY'
import sys
from augur.core import asof_ready, db
d = sys.argv[1]
with db.connect() as conn, conn.cursor() as cur:
    snap = asof_ready.snapshot(cur, d)
    cur.execute("SELECT family, count(*) FROM model_registry WHERE asof_snapshot::text=%s GROUP BY 1 ORDER BY 1", (d,))
    fams = cur.fetchall()
    cur.execute("SELECT horizon, verdict FROM econ_verdict_rule ORDER BY 1")
    verd = cur.fetchall()
    cur.execute(
        "SELECT horizon, count(*) FROM prediction_values pv "
        "JOIN model_registry mr USING (model_id) "
        "WHERE pv.panel_date=%s GROUP BY 1 ORDER BY 1",
        (d,),
    )
    emit = cur.fetchall()
print("snapshot@" + d)
for k in (
    "status", "price_max", "fv_nfeat", "has_core",
    "registry_a_cells", "registry_daily", "registry_mkt",     "registry_stack",
    "at_tip",
    "pack_complete",
):
    print(f"  {k}={snap[k]}")
print("registry family@%s" % d)
for f, n in fams:
    print(" ", f, n)
print("econ_verdict_rule")
for h, v in verd:
    print(" ", "H"+str(h), v)
print("prediction_values emit@%s" % d)
if not emit:
    print("  (無出門列；track=all 本來不 emit B3)")
for h, n in emit:
    print(" ", "H"+str(h), n)
print("護欄: 誠實形；dead/thin ≠ 可交易；本殼未 SERVE-SWAP；分數 ≠ 報酬％")
PY
fi

echo ""
echo "══════════════════════════════════════════════════════"
if [[ "$PACK_COMPLETE" == "1" && "$FORCE" -eq 0 ]]; then
  echo "包已齊＠$DATE：不要 --apply 同一天（同尺重複）。未齊 D 或 --force 才真跑。"
elif [[ "$DRY_PLAN" -eq 1 ]]; then
  echo "dry-plan 完成。真跑: --apply --date $DATE --track $TRACK"
else
  echo "HIST-ASOF apply 完成 D=$DATE  no-promote"
fi
echo "══════════════════════════════════════════════════════"
