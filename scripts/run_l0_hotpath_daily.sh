#!/usr/bin/env bash
# 🎯 L0 熱路徑日班薄殼 — 核 A 台灣日頻 → TRI 窄窗 dim-sync → FRED。
#
# 守: FZ/GATE-keep · stale-guard · TRI-only-dim · 不新增 cron · ≠B3 ≠L2 · no-93 · no-339
# 契約: reports/augur_l0_hotpath_daily_plan_20260814.md
#       reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md（L0＝API 門）
# GO:   audits/L0-HOTPATH-SHELL-GO-20260814.md
# 採納: audits/L0-HOTPATH-PREDICT-DAILY-ADOPTED-20260814.md
#       既有 20:00 arena ① 呼叫本殼（--date D --apply）；人跑同一入口。
#
# 執行指令矩陣:
#   bash scripts/run_l0_hotpath_daily.sh --selftest
#   bash scripts/run_l0_hotpath_daily.sh --date 2026-08-13 --dry-plan
#   bash scripts/run_l0_hotpath_daily.sh --date 2026-08-13 --apply          # 須另 APPLY-go
#   bash scripts/run_l0_hotpath_daily.sh --date 2026-08-13 --apply --extended
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || { echo "✗ 找不到專案目錄 $ROOT" >&2; exit 1; }

PY="${ROOT}/venv/bin/python"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
unset AUGUR_DIM_SYNC   # 禁全 dim-sync 捷徑；TRI 只走下方顯式 --datasets

# 核 A＝B3／籌碼日頻（計畫 §3.1）
CORE_A=(
  TaiwanStockPrice
  TaiwanStockPriceAdj
  TaiwanStockInfo
  TaiwanStockPER
  TaiwanStock10Year
  TaiwanStockInstitutionalInvestorsBuySell
  TaiwanStockMarginPurchaseShortSale
  TaiwanStockShareholding
  TaiwanDailyShortSaleBalances
  TaiwanStockSecuritiesLending
  TaiwanStockGovernmentBankBuySell
  TaiwanStockDayTrading
  TaiwanStockTotalInstitutionalInvestors
  TaiwanStockTotalMarginPurchaseShortSale
)

# 擴 B＝其餘台灣日頻（計畫 §3.2；預設關）
EXT_B=(
  TaiwanStockInfoWithWarrant
  TaiwanStockInstitutionalInvestorsBuySellWide
  TaiwanStockDayTradingBorrowingFeeRate
  TaiwanStockMarketValue
  TaiwanStockMarketValueWeight
  TaiwanStockPriceLimit
  TaiwanStockNews
  TaiwanStockBlockTrade
  TaiwanStockConvertibleBondDaily
  TaiwanStockConvertibleBondDailyOverview
  TaiwanStockConvertibleBondInstitutionalInvestors
  TaiwanStockLoanCollateralBalance
  TaiwanStockSuspended
  TaiwanStockDividendResult
  TaiwanStockIndustryChain
  TaiwanFuturesDaily
  TaiwanOptionDaily
  TaiwanFuturesInstitutionalInvestors
  TaiwanOptionInstitutionalInvestors
  TaiwanFuturesDealerTradingVolumeDaily
  TaiwanOptionDealerTradingVolumeDaily
  TaiwanFuturesFinalSettlementPrice
  TaiwanOptionFinalSettlementPrice
  TaiwanFuturesInstitutionalInvestorsAfterHours
  TaiwanOptionInstitutionalInvestorsAfterHours
  TaiwanFuturesOpenInterestLargeTraders
  TaiwanOptionOpenInterestLargeTraders
  TaiwanFuturesSpreadTrading
  TaiwanFutOptInstitutionalInvestors
  TaiwanTotalExchangeMarginMaintenance
  TaiwanSecuritiesTraderInfo
  TaiwanStockMarginShortSaleSuspension
  TaiwanStockDayTradingSuspension
)

STALE_DAYS=21
LOCK="/tmp/augur_l0_hotpath.lock"
DATE=""
EXTENDED=0
DRY_PLAN=0
DO_APPLY=0
SELFTEST=0
LOGDIR=""

usage() {
  sed -n '2,14p' "$0" | sed 's/^# \?//'
  echo ""
  echo "選項: --date YYYY-MM-DD  --dry-plan  --apply  --extended  --selftest  --logdir DIR"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE="${2:-}"; shift 2 ;;
    --extended) EXTENDED=1; shift ;;
    --dry-plan) DRY_PLAN=1; shift ;;
    --apply) DO_APPLY=1; shift ;;
    --selftest) SELFTEST=1; shift ;;
    --logdir) LOGDIR="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知參數: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ ! -x "$PY" ]]; then
  echo "✗ 找不到 $PY" >&2
  exit 1
fi

_has() { grep -E -q -- "$1" "$2"; }

taipei_today() {
  TZ=Asia/Taipei date +%F
}

is_weekend() {
  local d="$1"
  local wd
  wd="$(TZ=Asia/Taipei date -d "$d" +%u)"
  [[ "$wd" -ge 6 ]]
}

# --- selftest（零寫庫；內嵌 dry-plan 煙測）------------------------------------
if [[ "$SELFTEST" -eq 1 ]]; then
  ok=1
  chk() { if [[ "$2" == "1" ]]; then echo "  ✓ $1"; else echo "  ✗FAIL $1"; ok=0; fi; }
  echo "[L0-HOTPATH selftest]"
  chk "daily_maintenance.py 存在" "$([[ -f scripts/daily_maintenance.py ]] && echo 1 || echo 0)"
  chk "sync_macro.py 存在" "$([[ -f scripts/sync_macro.py ]] && echo 1 || echo 0)"
  chk "venv python" "$([[ -x $PY ]] && echo 1 || echo 0)"
  chk "核 A 14 張" "$([[ ${#CORE_A[@]} -eq 14 ]] && echo 1 || echo 0)"
  chk "擴 B 非空" "$([[ ${#EXT_B[@]} -gt 0 ]] && echo 1 || echo 0)"
  chk "doc 禁 cron" "$(_has '非 cron|no-cron|禁 cron' "$0" && echo 1 || echo 0)"
  chk "doc no-93" "$(_has 'no-93' "$0" && echo 1 || echo 0)"
  chk "doc TRI-only" "$(_has 'TRI-only|TRI 窄窗' "$0" && echo 1 || echo 0)"
  chk "doc ≠B3" "$(_has '≠B3|不呼叫 B3' "$0" && echo 1 || echo 0)"
  if bash "$0" --date 2026-08-13 --dry-plan >/tmp/l0-hotpath-selftest-dry.out 2>&1; then
    chk "dry-plan RC=0" 1
    chk "dry 含核 A Price" "$(_has 'TaiwanStockPrice' /tmp/l0-hotpath-selftest-dry.out && echo 1 || echo 0)"
    chk "dry 含 TRI dim-sync" "$(_has 'TaiwanStockTotalReturnIndex' /tmp/l0-hotpath-selftest-dry.out && echo 1 || echo 0)"
    chk "dry 含 --with-dim-sync" "$(_has '--with-dim-sync' /tmp/l0-hotpath-selftest-dry.out && echo 1 || echo 0)"
    chk "dry 含 sync_macro" "$(_has 'sync_macro.py --no-catalog' /tmp/l0-hotpath-selftest-dry.out && echo 1 || echo 0)"
    chk "dry 無 EuropeStockInfo" "$(_has 'EuropeStockInfo' /tmp/l0-hotpath-selftest-dry.out && echo 0 || echo 1)"
    chk "dry 無 AUGUR_DIM_SYNC=1" "$(_has 'AUGUR_DIM_SYNC=1' /tmp/l0-hotpath-selftest-dry.out && echo 0 || echo 1)"
    chk "dry 無 B3 殼" "$(_has 'run_daily_asof_predict' /tmp/l0-hotpath-selftest-dry.out && echo 0 || echo 1)"
    chk "dry 無 L2 殼" "$(_has 'run_daily_retrain_l2' /tmp/l0-hotpath-selftest-dry.out && echo 0 || echo 1)"
    chk "dry 零寫庫標" "$(_has 'dry-plan: 未執行' /tmp/l0-hotpath-selftest-dry.out && echo 1 || echo 0)"
  else
    chk "dry-plan RC=0" 0
  fi
  if bash "$0" --date 2026-08-16 --dry-plan >/tmp/l0-hotpath-selftest-weekend.out 2>&1; then
    chk "週末 SKIP RC=0" 1
    chk "週末印非交易日" "$(_has '非交易日|SKIP' /tmp/l0-hotpath-selftest-weekend.out && echo 1 || echo 0)"
  else
    chk "週末 SKIP RC=0" 0
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
  echo "✗ 安全預設：請顯式 --dry-plan 或 --apply（P1 殼禁默抓）" >&2
  exit 2
fi

if [[ -z "$DATE" ]]; then
  DATE="$(taipei_today)"
  echo "未指定 --date → 台北日曆 $DATE"
fi

if [[ ! "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "✗ --date 須 YYYY-MM-DD" >&2
  exit 2
fi

# 週末／國定假 → SKIP（exit 0）。交易日曆缺表時只守週末。
if is_weekend "$DATE"; then
  echo "SKIP｜$DATE 週末＝非交易日（L0 熱路徑不抓）"
  exit 0
fi
TRADE_N="$("$PY" -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute(\"SELECT to_regclass('public.\\\"TaiwanStockTradingDate\\\"')\")
    if cur.fetchone()[0] is None:
        print('NA')
    else:
        cur.execute('SELECT count(*) FROM \"TaiwanStockTradingDate\" WHERE date=%s', ('$DATE',))
        print(int(cur.fetchone()[0] or 0))
" 2>/dev/null || echo NA)"
if [[ "$TRADE_N" == "0" ]]; then
  echo "SKIP｜$DATE 不在 TaiwanStockTradingDate（國定假／非交易日）"
  exit 0
fi

if [[ -z "$LOGDIR" ]]; then
  LOGDIR="/tmp/l0-hotpath-${DATE}"
fi
mkdir -p "$LOGDIR"

CAND=("${CORE_A[@]}")
if [[ "$EXTENDED" -eq 1 ]]; then
  CAND+=("${EXT_B[@]}")
fi

# stale-guard：stdout 每行 status<TAB>dataset<TAB>resume
GUARD="$("$PY" -c "
from datetime import date, timedelta
from augur.core import db, schema
D = date.fromisoformat('$DATE')
cut = D - timedelta(days=$STALE_DAYS)
names = '''$(printf '%s\n' "${CAND[@]}")'''.strip().splitlines()
with db.connect() as conn, conn.cursor() as cur:
    for ds in names:
        cur.execute('SELECT to_regclass(%s)', (f'public.\"{ds}\"',))
        if cur.fetchone()[0] is None:
            print(f'no-table\t{ds}\t')
            continue
        cols = schema.get_dataset_columns(cur, ds)
        if 'date' not in cols:
            print(f'no-date\t{ds}\t')
            continue
        cur.execute(f'SELECT max(date)::text FROM \"{ds}\"')
        mx = cur.fetchone()[0]
        if not mx:
            print(f'no-baseline\t{ds}\t')
            continue
        resume = date.fromisoformat(str(mx)[:10])
        if resume < cut:
            print(f'skip-stale\t{ds}\t{resume.isoformat()}')
        else:
            print(f'ok\t{ds}\t{resume.isoformat()}')
")"

OK_DS=()
YELLOW=()
FATAL=""
while IFS=$'\t' read -r st ds resume; do
  [[ -n "${st:-}" ]] || continue
  case "$st" in
    ok)
      OK_DS+=("$ds")
      echo "  guard ok     $ds  resume=$resume"
      ;;
    skip-stale)
      YELLOW+=("$ds resume=$resume < D-${STALE_DAYS}d")
      echo "  ⚠ SKIP stale $ds  resume=$resume"
      ;;
    no-baseline|no-table|no-date)
      YELLOW+=("$ds $st（拒全史）")
      echo "  ⚠ 拒全史     $ds  ($st)"
      if [[ "$ds" == "TaiwanStockPrice" || "$ds" == "TaiwanStockPriceAdj" ]]; then
        FATAL="$ds $st"
      fi
      ;;
    *)
      YELLOW+=("$ds $st")
      echo "  ⚠ $st        $ds"
      ;;
  esac
done <<< "$GUARD"

if [[ -n "$FATAL" ]]; then
  echo "✗ 核價表無基線：$FATAL —— 不啟動全史" >&2
  exit 3
fi

echo "══════════════════════════════════════════════════════"
echo "L0 HOTPATH  D=$DATE  dry_plan=$DRY_PLAN  apply=$DO_APPLY  extended=$EXTENDED"
echo "  核 A=${#CORE_A[@]}  擴 B=$EXTENDED  stale>${STALE_DAYS}d=SKIP"
echo "  by-date 將跑 ${#OK_DS[@]} 張；黃帳 ${#YELLOW[@]}"
echo "  logdir=$LOGDIR"
echo "  本殼不呼叫 B3／L2／cron／promote／93 表／AUGUR_DIM_SYNC"
echo "══════════════════════════════════════════════════════"

run_step() {
  local name="$1"; shift
  local log="${LOGDIR}/${name}.log"
  echo ""
  echo "── step: $name ──"
  echo "+ $*"
  if [[ "$DRY_PLAN" -eq 1 ]]; then
    echo "  (dry-plan: 未執行)"
    return 0
  fi
  local rc=0
  { "$@" 2>&1 | tee -a "$log" "$LOGDIR/driver.log"; } || rc=${PIPESTATUS[0]}
  echo "RC[$name]=$rc"
  if [[ "$rc" -ne 0 ]]; then
    echo "✗ 停鏈 @ $name (RC=$rc)" >&2
    return "$rc"
  fi
  return 0
}

if [[ "$DO_APPLY" -eq 1 ]]; then
  exec 9>"$LOCK"
  if ! flock -n 9; then
    echo "✗ 已有 L0 熱路徑在跑（$LOCK）" >&2
    exit 1
  fi
fi

APPLY_RC=0
if [[ ${#OK_DS[@]} -eq 0 ]]; then
  echo ""
  echo "── step: by-date ── SKIP（核 A／擴 B 全被 stale-guard 擋下）"
  if [[ "$DO_APPLY" -eq 1 ]]; then
    APPLY_RC=2
  fi
else
  if ! run_step "bydate" "$PY" scripts/daily_maintenance.py --end "$DATE" --datasets "${OK_DS[@]}"; then
    APPLY_RC=$?
  fi
fi

if [[ "$APPLY_RC" -eq 0 ]]; then
  if ! run_step "tri" "$PY" scripts/daily_maintenance.py \
      --datasets TaiwanStockTotalReturnIndex --with-dim-sync --end "$DATE"; then
    APPLY_RC=$?
  fi
fi

if [[ "$APPLY_RC" -eq 0 ]]; then
  if ! run_step "macro" "$PY" scripts/sync_macro.py --no-catalog; then
    APPLY_RC=$?
  fi
fi

# 黃帳（SKIP ≠ 塗綠）
if [[ ${#YELLOW[@]} -gt 0 ]]; then
  echo ""
  echo "黃帳 stale-guard／無基線（${#YELLOW[@]}）:"
  for y in "${YELLOW[@]}"; do
    echo "  - $y"
  done
fi

if [[ "$DRY_PLAN" -eq 1 ]]; then
  echo ""
  echo "══════════════════════════════════════════════════════"
  echo "dry-plan 完成（零寫庫）。真跑須另 L0-HOTPATH-APPLY-go ＋ --apply。"
  echo "══════════════════════════════════════════════════════"
  exit 0
fi

# apply 後誠實 tip（給 L1 的綠燈＝PriceAdj TAIEX ≥ D）
TIPS="$("$PY" -c "
from augur.core import db
with db.connect() as conn, conn.cursor() as cur:
    cur.execute('SELECT max(date)::text FROM \"TaiwanStockPriceAdj\" WHERE stock_id=%s', ('TAIEX',))
    print('price_adj_taiex', cur.fetchone()[0] or '')
    cur.execute('SELECT max(date)::text FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id=%s', ('TAIEX',))
    print('tri_taiex', cur.fetchone()[0] or '')
    cur.execute('SELECT max(date)::text FROM \"TaiwanStockPrice\"')
    print('price_max', cur.fetchone()[0] or '')
")"
echo ""
echo "$TIPS"
PRICE_TIP="$(echo "$TIPS" | awk '/^price_adj_taiex/{print $2}')"
TRI_TIP="$(echo "$TIPS" | awk '/^tri_taiex/{print $2}')"

if [[ -f "$LOGDIR/driver.log" ]] && grep -Eqi 'Your level is register|status.?403|FinMindError' "$LOGDIR/driver.log"; then
  echo "✗ FinMind 掉級／403 —— 停、不重試風暴" >&2
  exit 3
fi

if [[ -n "$PRICE_TIP" && "$PRICE_TIP" < "$DATE" ]]; then
  echo "⚠ PriceAdj TAIEX=$PRICE_TIP < D=$DATE（FinMind 該日可能尚未出；不假 B3）"
fi
if [[ -n "$TRI_TIP" && "$TRI_TIP" < "$DATE" ]]; then
  echo "⚠ TRI TAIEX=$TRI_TIP < D=$DATE（黃帳；不擋 B3）"
fi

echo ""
echo "══════════════════════════════════════════════════════"
if [[ "$APPLY_RC" -eq 0 ]]; then
  echo "L0 HOTPATH apply 完成 D=$DATE  PriceAdj=$PRICE_TIP  TRI=$TRI_TIP"
else
  echo "L0 HOTPATH apply 有失敗 D=$DATE  rc=$APPLY_RC"
fi
echo "護欄: 未改 crontab · 未開 B3／L2 · 未 AUGUR_DIM_SYNC"
echo "══════════════════════════════════════════════════════"
exit "$APPLY_RC"
