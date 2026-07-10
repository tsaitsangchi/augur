#!/usr/bin/env bash
# 🎯 一鍵 DB import — 從 dump 還原/取代 augur database(換機接續前置)。
# 破壞性:取代既有 augur 庫須 --force 明示(先終止連線+drop);新機(庫不存在)則直接建+還原(#6)。
# 全本地、零 Claude usage。dump 不在 git、須先實體搬到本機(見下方偵測路徑)。
#
# 支援三種 dump 格式(自動判別):
#   (a) tar 內含 pg_dump -Fd 目錄(augur #30 慣例 augur_pg17_*.tar)→ 先解 tar 再 -Fd -j4 平行還原
#   (b) pg_dump -Fd 目錄(未打包)                                → 直接 -Fd -j4
#   (c) pg_dump -Fc 單檔(augur_*.dump)                          → 直接 -j4
#
# 執行指令矩陣:
#   bash import_database.sh                 # 自動偵測最新 dump;augur 不存在→建+還原;已存在→拒(要 --force)
#   bash import_database.sh <dump 路徑>      # 指定 dump(.tar / -Fd 目錄 / -Fc .dump)
#   bash import_database.sh --dry-run        # 只偵測格式 + 輕量驗證 + 印計畫,不解 tar、不動 DB
#   bash import_database.sh --force          # 取代既有 augur 庫(破壞性:終止連線→dropdb→重建還原)
#   bash import_database.sh --migrate        # 還原後補跑 13 支 migrate_*_ddl.py(dump 較舊時對齊 git,冪等)
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1
VENV_PY="$ROOT/venv/bin/python"
STAGE=""
cleanup() { [ -n "$STAGE" ] && [ -d "$STAGE" ] && rm -rf "$STAGE"; }
trap cleanup EXIT

# ---- .env(DB 憑證,不在 git)----
if [ ! -f "$ROOT/.env" ]; then
  echo "✗ 找不到 .env(含 DB 憑證、不在 git)——請先重建 .env 再匯入。"; exit 1
fi
set -a; source "$ROOT/.env"; set +a
DB_NAME="${DB_NAME:-augur}"; DB_USER="${DB_USER:-augur}"
DB_HOST="${DB_HOST:-127.0.0.1}"; DB_PORT="${DB_PORT:-5432}"
SU="${DB_SUPERUSER_USER:-postgres}"
export PGPASSWORD="${DB_SUPERUSER_PASSWORD:-}"
psu() { psql -h "$DB_HOST" -p "$DB_PORT" -U "$SU" "$@"; }

# ---- 參數 ----
DUMP=""; FORCE=0; DRYRUN=0; MIGRATE=0
for a in "$@"; do
  case "$a" in
    --force) FORCE=1 ;;
    --dry-run) DRYRUN=1 ;;
    --migrate) MIGRATE=1 ;;
    -*) echo "✗ 未知參數 $a"; exit 1 ;;
    *) DUMP="$a" ;;
  esac
done

# ---- 偵測 dump(未指定則找最新;優先本地 ext4 快)----
if [ -z "$DUMP" ]; then
  for d in "$HOME/db_dumps" /mnt/d/database /mnt/c/AI; do
    [ -d "$d" ] || continue
    cand=$(ls -t "$d"/augur_pg17_*.tar "$d"/augur_*.dump 2>/dev/null | head -1)
    [ -n "$cand" ] && { DUMP="$cand"; break; }
  done
fi
if [ -z "$DUMP" ] || [ ! -e "$DUMP" ]; then
  echo "✗ 找不到 dump。dump 不在 git、須先實體搬到本機(6.6GB)。"
  echo "  預設搜尋:~/db_dumps/  /mnt/d/database/  /mnt/c/AI/(檔名 augur_pg17_*.tar / augur_*.dump)"
  echo "  或直接指定:bash import_database.sh /path/to/dump"
  exit 1
fi
echo "dump = $DUMP  ($(du -h "$DUMP" | cut -f1))"

# ---- 判格式(不解 tar,只偵測)----
NEED_EXTRACT=0; TOPDIR=""
if [ -d "$DUMP" ]; then
  FMT="pg_dump -Fd 目錄"; JOBS="-j 4"
elif file "$DUMP" 2>/dev/null | grep -q 'tar archive'; then
  inner=$(tar -tf "$DUMP" 2>/dev/null | grep -m1 'toc\.dat$')
  if [ -n "$inner" ]; then
    TOPDIR="${inner%%/*}"; FMT="tar 內含 -Fd 目錄($TOPDIR)"; JOBS="-j 4"; NEED_EXTRACT=1
  else
    FMT="tar(-Ft,不支援平行)"; JOBS=""
  fi
else
  FMT="pg_dump -Fc 單檔"; JOBS="-j 4"
fi
echo "格式 = $FMT   還原平行度 = ${JOBS:-無(sequential)}"

# ---- 輕量驗證 + dry-run ----
if [ "$NEED_EXTRACT" = 1 ]; then
  echo "驗證:tar 內含 toc.dat ✓($(tar -tf "$DUMP" 2>/dev/null | wc -l) 個 data 檔;還原時才解出)"
else
  toc=$(pg_restore --list "$DUMP" 2>&1 | grep -c ';') || true
  echo "驗證:pg_restore --list TOC 物件 ≈ $toc"
fi
if [ "$DRYRUN" = 1 ]; then
  echo "── DRY-RUN:以上為計畫,未解 tar、未動 DB。移除 --dry-run 才實際匯入。"; exit 0
fi

# ---- 破壞性安全閘:庫已存在 ----
exists=$(psu -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null)
if [ "$exists" = "1" ]; then
  size=$(psu -d postgres -tAc "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null)
  if [ "$FORCE" != 1 ]; then
    echo "✗ 資料庫 '$DB_NAME' 已存在($size)。取代為破壞性操作。"
    echo "  新機不該撞到此情況;若確要取代,加 --force(會先終止連線並 dropdb)。"
    exit 1
  fi
  echo "⚠ --force:取代既有 '$DB_NAME'($size)。終止連線 → dropdb…"
  psu -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$DB_NAME' AND pid<>pg_backend_pid();" >/dev/null 2>&1
  psu -d postgres -c "DROP DATABASE $DB_NAME;" || { echo "✗ dropdb 失敗"; exit 1; }
fi

# ---- 需要時解 tar ----
RESTORE_SRC="$DUMP"
if [ "$NEED_EXTRACT" = 1 ]; then
  STAGE="$(dirname "$DUMP")/.augur_restore_stage_$$"
  mkdir -p "$STAGE"
  echo "解 tar → $STAGE(數十秒)…"
  tar -xf "$DUMP" -C "$STAGE" || { echo "✗ 解 tar 失敗"; exit 1; }
  RESTORE_SRC="$STAGE/$TOPDIR"
  [ -f "$RESTORE_SRC/toc.dat" ] || { echo "✗ 解出目錄無 toc.dat($RESTORE_SRC)"; exit 1; }
fi

# ---- 確保角色存在(新機只有 postgres)----
for pair in "$DB_USER:${DB_PASSWORD:-}" "augur_predict:${DB_PREDICT_PASSWORD:-}"; do
  role="${pair%%:*}"; pw="${pair#*:}"
  has=$(psu -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$role';" 2>/dev/null)
  if [ "$has" != 1 ] && [ -n "$pw" ]; then
    psu -d postgres -c "CREATE ROLE $role LOGIN PASSWORD '$pw';" >/dev/null 2>&1 \
      && echo "  建立角色 $role" || echo "  (角色 $role 建立略過)"
  fi
done

# ---- 建庫 + 還原 ----
echo "建立資料庫 $DB_NAME(owner=$DB_USER)…"
psu -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || { echo "✗ createdb 失敗"; exit 1; }
echo "pg_restore 還原中(-Fd 平行約 15-20 分)…"
pg_restore $JOBS -h "$DB_HOST" -p "$DB_PORT" -U "$SU" -d "$DB_NAME" "$RESTORE_SRC" 2>&1 | tail -5
echo "  pg_restore 結束(GRANT 到尚未建角色之非致命錯誤可忽略)"

# ---- 預測隔離角色(#8 動態 GRANT 閘)----
echo "setup_predict_role(#8 隔離角色)…"
if [ -x "$VENV_PY" ]; then
  "$VENV_PY" "$ROOT/scripts/setup_predict_role.py" --apply --confirm 2>&1 | tail -3 || echo "  (setup_predict_role 未完成,可事後手動跑)"
else
  echo "  ✗ 無 $VENV_PY;請先 pip install -e . 後手動跑 scripts/setup_predict_role.py --apply --confirm"
fi

# ---- 選配:補 migrations(冪等)----
if [ "$MIGRATE" = 1 ] && [ -x "$VENV_PY" ]; then
  echo "補跑 migrate_*_ddl.py(對齊 git DDL,冪等)…"
  for m in "$ROOT"/scripts/migrate_*_ddl.py; do
    "$VENV_PY" "$m" >/dev/null 2>&1 && echo "  ✓ $(basename "$m")" || echo "  ⚠ $(basename "$m") 未完成(查 dump 是否已含)"
  done
fi

# ---- smoke test(#7 實測)----
echo "── smoke test ──"
pub=$(psu -d "$DB_NAME" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null)
tt=$(psu -d "$DB_NAME" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='ttai_import';" 2>/dev/null)
sz=$(psu -d postgres -tAc "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null)
echo "  public $pub 表 · ttai_import $tt 表 · 庫大小 $sz"
echo "════════════════════════════════════════════"
echo "  ✓ DB import 完成:$DB_NAME($sz)"
echo "════════════════════════════════════════════"
