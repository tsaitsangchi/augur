#!/usr/bin/env bash
# 🎯 arena 首批結算作業(hugo 拍板 SOP 2026-07-25;首發 2026-07-27 週一收盤後)。
# SOP:sync(audit+heal 推進至目標日) → 複驗 PriceAdj max(date) → settle --run → 成績單 → 自拆 cron。
# 全本地零 Claude usage;settle 自帶 fail-closed 雙閘(資料未到=零寫入)。守 #7(實測)· #29a/d · #6(破壞性須明示 --run)。
#
# ⚠ 兩個必須知道的事實(2026-07-26 親驗更正):
#   (1) cron 規格 `0 20 27 7 *` ＝**每年 7/27 20:00 觸發一次**,沒有次日重試(下次是 2027-07-27)。
#       原版資料未到時 exit 0 ＝靜默無事發生、無人知曉;現改 rc≠0 + sentinel 檔使失敗可見。
#   (2) 本檔原住 ~/logs/(不在 git)、換機即失;2026-07-26 移入 repo scripts/ 並補指令矩陣。
#
# 執行指令矩陣:
#   bash scripts/arena_settle_oneshot.sh              # 無參數:唯讀現況(PriceAdj max(date)/是否就緒/sentinel)
#   bash scripts/arena_settle_oneshot.sh --run        # 實跑結算(破壞性:寫 arena 標籤、成功後自拆 cron)
#   bash scripts/arena_settle_oneshot.sh --dry-run    # 跑到複驗為止,不 sync 不 settle 不自拆
#   bash scripts/arena_settle_oneshot.sh --target-date 2026-07-28   # 覆寫目標交易日(預設 2026-07-27)
#   bash scripts/arena_settle_oneshot.sh --selftest   # 零 DB 紅綠(參數解析/守衛存在)
set -u
ROOT="${PROJECT_ROOT:-${AUGUR_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}}"
SENTINEL="$HOME/logs/ARENA_SETTLE_BLOCKED.sentinel"
TARGET="2026-07-27"
MODE="status"

while [ $# -gt 0 ]; do
  case "$1" in
    --run) MODE="run" ;;
    --dry-run) MODE="dry" ;;
    --selftest) MODE="selftest" ;;
    --target-date) TARGET="${2:-$TARGET}"; shift ;;
    -h|--help) awk "/^set -u/{exit} NR>1"  "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "✗ 未知參數:$1（--help 看指令矩陣）"; exit 2 ;;
  esac
  shift
done

if [ "$MODE" = "selftest" ]; then
  ok=0
  chk() { if [ "$2" = "1" ]; then echo "  ✓ $1"; else echo "  ✗ $1"; ok=1; fi; }
  chk "無參數不執行破壞性動作(預設 MODE=status)" "$([ "$(grep -c '^MODE="status"' "${BASH_SOURCE[0]}")" -ge 1 ] && echo 1 || echo 0)"
  chk "資料未到 → rc≠0(非 exit 0 靜默)" "$(grep -q 'exit 1' "${BASH_SOURCE[0]}" && echo 1 || echo 0)"
  chk "資料未到 → 產 sentinel 使失敗可見" "$(grep -q 'ARENA_SETTLE_BLOCKED' "${BASH_SOURCE[0]}" && echo 1 || echo 0)"
  chk "自拆 cron 僅在 settle rc=0 時" "$(grep -q 'RC -eq 0' "${BASH_SOURCE[0]}" && echo 1 || echo 0)"
  chk "ROOT 不寫死 hugo 路徑(換機可攜)" "$(grep -q 'PROJECT_ROOT:-' "${BASH_SOURCE[0]}" && echo 1 || echo 0)"
  chk "dry-run 不觸 settle" "$(grep -q '\[ "\$MODE" = "dry" \]' "${BASH_SOURCE[0]}" && echo 1 || echo 0)"
  echo "自測:$([ $ok -eq 0 ] && echo '全通過 ✓' || echo '有失敗 ✗')"
  exit $ok
fi

cd "$ROOT" || { echo "✗ 找不到專案根 $ROOT"; exit 1; }
set -a; . ./.env; set +a
MAXD=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
       -tAc 'SELECT max(date) FROM "TaiwanStockPriceAdj"' 2>/dev/null)

if [ "$MODE" = "status" ]; then
  awk "/^set -u/{exit} NR>1"  "${BASH_SOURCE[0]}"
  echo "現況:"
  echo "  PriceAdj max(date) = ${MAXD:-(psql 無回應)}   目標日 = $TARGET"
  if [ -z "$MAXD" ] || [ "$MAXD" \< "$TARGET" ]; then
    echo "  → 尚未就緒(資料未到目標日);--run 會拒跑並產 sentinel"
  else
    echo "  → 已就緒;--run 即可結算"
  fi
  [ -f "$SENTINEL" ] && echo "  ⚠ 存在阻塞 sentinel:$(cat "$SENTINEL")"
  exit 0
fi

LOG="$HOME/logs/arena_settle_${TARGET//-/}.log"
mkdir -p "$HOME/logs"
{
  echo "═══ $(date '+%F %T') arena 結算作業開始(mode=$MODE, target=$TARGET) ═══"
  if [ "$MODE" = "run" ]; then
    echo "── 1/4 sync(daily_maintenance audit+heal,綠鏈同款) ──"
    venv/bin/python scripts/daily_maintenance.py --audit-days 14 --audit-all --heal
    MAXD=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
           -tAc 'SELECT max(date) FROM "TaiwanStockPriceAdj"' 2>/dev/null)
  else
    echo "── 1/4 sync:跳過(--dry-run) ──"
  fi
  echo "── 2/4 複驗 PriceAdj max(date) ──"
  echo "PriceAdj max(date)=${MAXD:-(psql 無回應)} / 目標 $TARGET"
  if [ -z "$MAXD" ] || [ "$MAXD" \< "$TARGET" ]; then
    echo "✗ 資料未到 $TARGET(或 psql 失敗),不跑 settle、零寫入"
    echo "  ⚠ 本 cron 為一次性(每年 7/27),**不會自動重試**——需人工重跑本腳本或另掛 cron"
    date "+%F %T PriceAdj max=${MAXD:-none} < $TARGET;結算未執行、需人工介入" > "$SENTINEL"
    exit 1
  fi
  rm -f "$SENTINEL"
  if [ "$MODE" = "dry" ]; then
    echo "── 3/4 settle:跳過(--dry-run);資料已就緒,--run 即可實跑 ──"
    echo "═══ $(date '+%F %T') dry-run 結束 ═══"
    exit 0
  fi
  echo "── 3/4 settle --run ──"
  venv/bin/python scripts/settle_arena_labels.py --run
  RC=$?
  echo "settle exit=$RC"
  echo "── 4/4 成績單摘要 ──"
  venv/bin/python scripts/settle_arena_labels.py
  if [ $RC -eq 0 ]; then
    (crontab -l | grep -v arena_settle_oneshot) | crontab -
    echo "✓ 結算完成,cron 已自拆;成績單詳情待 hugo/Claude 陪跑覆盤"
  fi
  echo "═══ $(date '+%F %T') 作業結束 ═══"
} >> "$LOG" 2>&1
