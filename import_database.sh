#!/usr/bin/env bash
# 🎯 一鍵 DB import — 從 dump 還原/取代 augur database(換機接續前置)。
# 破壞性:取代既有 augur 庫須 --force 明示(先終止連線+drop);新機(庫不存在)則直接建+還原(#6)。
# 全本地、零 Claude usage。dump 不在 git、須先實體搬到本機(見下方偵測路徑)。
#
# 支援三種 dump 格式(自動判別):
#   (a) tar 內含 pg_dump -Fd 目錄（#30 慣例 augur_YYYYMMDD_weekly_Fd.tar；舊名 augur_pg17_*.tar）
#       → 先解 tar 再 -Fd -j4 平行還原。內層已 -Z1,外層 tar 不再 gzip。
#       ⚠ pg_restore 不能直接吃「tar-of-Fd」(不是 -Ft / 不是 -Fc)——必須先解出目錄。
#   (b) pg_dump -Fd 目錄(未打包,augur_YYYYMMDD_weekly_Fd) → 直接 -Fd -j4（同資料夾有目錄則優先於 .tar）
#   (c) pg_dump -Fc 單檔(augur_*.dump)                    → 直接 -j4
#
# 執行指令矩陣:
#   bash import_database.sh                 # 自動偵測最新 dump;augur 不存在→建+還原;已存在→拒(要 --force)
#   bash import_database.sh <dump 路徑>      # 指定 dump(.tar / -Fd 目錄 / -Fc .dump)
#   bash import_database.sh --dry-run        # 只偵測格式 + 輕量驗證 + 印計畫,不解 tar、不動 DB
#   bash import_database.sh --force          # 取代既有 augur 庫(破壞性:終止連線→dropdb→重建還原)
#   bash import_database.sh --migrate        # 還原後補跑全部 migrate_*_ddl.py+source_governance(glob 全量、不寫死支數;dump 較舊時對齊 git,冪等)
#   bash import_database.sh --selftest       # 偵測/格式判別自測(免 .env、不動 DB)
#   IDX_MEM=3GB bash import_database.sh …     # 覆蓋索引段 maintenance_work_mem(預設 2GB;大表 HNSW 可調高,須 IDX_MEM×2 < RAM−shared_buffers 避免 OOM)
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1
VENV_PY="$ROOT/venv/bin/python"
STAGE=""
cleanup() { [ -n "$STAGE" ] && [ -d "$STAGE" ] && rm -rf "$STAGE"; }
trap cleanup EXIT

SEARCH_DIRS=("$HOME/db_dumps" /mnt/c/database /mnt/d/database /mnt/c/AI)

pick_from_dir() {  # $1=目錄 → stdout 一條路徑。同資料夾優先 weekly 目錄,其次 weekly .tar,再舊名。
  local d="$1" cand
  [ -d "$d" ] || return 1
  cand=$(ls -td "$d"/augur_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_weekly_Fd 2>/dev/null | head -1)
  [ -n "${cand:-}" ] && [ -d "$cand" ] && { printf '%s\n' "$cand"; return 0; }
  cand=$(ls -td "$d"/augur_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_weekly_Fd.tar 2>/dev/null | head -1)
  [ -n "${cand:-}" ] && [ -f "$cand" ] && { printf '%s\n' "$cand"; return 0; }
  cand=$(ls -td "$d"/augur_pg17_*.tar "$d"/augur_pgdump_*.tar "$d"/augur_pgdump_*_Fd "$d"/augur_*.dump 2>/dev/null | head -1)
  [ -n "${cand:-}" ] && { printf '%s\n' "$cand"; return 0; }
  return 1
}

detect_fmt() {  # 讀 DUMP;設 FMT / JOBS / NEED_EXTRACT / TOPDIR(不解全包)
  NEED_EXTRACT=0; TOPDIR=""; JOBS="-j 4"
  if [ -d "$DUMP" ]; then
    FMT="pg_dump -Fd 目錄"
    return 0
  fi
  local kind
  kind=$(file -b "$DUMP" 2>/dev/null || true)
  if [[ "$DUMP" == *.tar ]] || echo "$kind" | grep -qiE 'tar archive|posix tar'; then
    local inner
    inner=$(tar -tf "$DUMP" 2>/dev/null | grep -m1 'toc\.dat$' || true)
    if [ -n "$inner" ]; then
      TOPDIR="${inner%%/*}"; FMT="tar 內含 -Fd 目錄($TOPDIR)"; NEED_EXTRACT=1
    else
      FMT="tar(-Ft,不支援平行)"; JOBS=""
    fi
    return 0
  fi
  FMT="pg_dump -Fc 單檔"
}

# ---- 參數 ----
DUMP=""; FORCE=0; DRYRUN=0; MIGRATE=0
for a in "$@"; do
  case "$a" in
    --force) FORCE=1 ;;
    --dry-run) DRYRUN=1 ;;
    --migrate) MIGRATE=1 ;;
    --selftest)
      _ok=0
      _chk() { if [ "$2" = 1 ]; then echo "  ✓ $1"; else echo "  ✗ $1"; _ok=1; fi; }
      _td=$(mktemp -d)
      mkdir -p "$_td/a/augur_20260801_weekly_Fd" "$_td/b"
      : > "$_td/a/augur_20260801_weekly_Fd/toc.dat"
      tar -C "$_td/a" -cf "$_td/a/augur_20260801_weekly_Fd.tar" augur_20260801_weekly_Fd
      _p=$(pick_from_dir "$_td/a")
      _chk "同資料夾有目錄與 tar ⇒ 優先目錄" "$( [ "$_p" = "$_td/a/augur_20260801_weekly_Fd" ] && echo 1 || echo 0 )"
      _p=$(pick_from_dir "$_td/b")
      _chk "空目錄 ⇒ 偵測失敗" "$( [ -z "${_p:-}" ] && echo 1 || echo 0 )"
      tar -C "$_td/a" -cf "$_td/b/augur_20260814_weekly_Fd.tar" augur_20260801_weekly_Fd
      _p=$(pick_from_dir "$_td/b")
      _chk "僅有 weekly .tar ⇒ 選 tar" "$( [ "$_p" = "$_td/b/augur_20260814_weekly_Fd.tar" ] && echo 1 || echo 0 )"
      DUMP="$_td/b/augur_20260814_weekly_Fd.tar"
      detect_fmt
      _chk "weekly_Fd.tar ⇒ 判為 tar 內含 -Fd" "$( [ "$NEED_EXTRACT" = 1 ] && [ "$TOPDIR" = "augur_20260801_weekly_Fd" ] && echo 1 || echo 0 )"
      DUMP="$_td/a/augur_20260801_weekly_Fd"
      detect_fmt
      _chk "-Fd 目錄 ⇒ 不解 tar" "$( [ "$NEED_EXTRACT" = 0 ] && [ "$FMT" = "pg_dump -Fd 目錄" ] && echo 1 || echo 0 )"
      rm -rf "$_td"
      echo "自測:$([ $_ok -eq 0 ] && echo '全通過 ✓' || echo '有失敗 ✗')"
      exit $_ok
      ;;
    -*) echo "✗ 未知參數 $a"; exit 1 ;;
    *) DUMP="$a" ;;
  esac
done

# ---- .env(DB 憑證,不在 git;selftest 已先行退出)----
if [ ! -f "$ROOT/.env" ]; then
  echo "✗ 找不到 .env(含 DB 憑證、不在 git)——請先重建 .env 再匯入。"; exit 1
fi
set -a; source "$ROOT/.env"; set +a
DB_NAME="${DB_NAME:-augur}"; DB_USER="${DB_USER:-augur}"
DB_HOST="${DB_HOST:-127.0.0.1}"; DB_PORT="${DB_PORT:-5432}"
SU="${DB_SUPERUSER_USER:-postgres}"
export PGPASSWORD="${DB_SUPERUSER_PASSWORD:-}"
psu() { psql -h "$DB_HOST" -p "$DB_PORT" -U "$SU" "$@"; }

# ---- 偵測 dump(未指定則找最新;優先本地 ext4 快;同資料夾目錄優先於 tar)----
if [ -z "$DUMP" ]; then
  for d in "${SEARCH_DIRS[@]}"; do
    cand=$(pick_from_dir "$d") || continue
    DUMP="$cand"; break
  done
fi
if [ -z "$DUMP" ] || [ ! -e "$DUMP" ]; then
  echo "✗ 找不到 dump。dump 不在 git、須先實體搬到本機。"
  echo "  預設搜尋:~/db_dumps/  /mnt/c/database/  /mnt/d/database/  /mnt/c/AI/"
  echo "  檔名優先:augur_YYYYMMDD_weekly_Fd 目錄 > 同名 .tar > 舊名 augur_pg17_*.tar / augur_pgdump_* / augur_*.dump"
  echo "  或直接指定:bash import_database.sh /mnt/c/database/augur_YYYYMMDD_weekly_Fd.tar"
  exit 1
fi
echo "dump = $DUMP  ($(du -h "$DUMP" | cut -f1))"

# ---- 判格式(不解 tar,只偵測)----
detect_fmt
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
  # 解到本地 ext4(勿解到 drvfs 上的 dump 旁——11G 在 /mnt/c 極慢)
  STAGE="$HOME/db_dumps/.augur_restore_stage_$$"
  mkdir -p "$STAGE"
  echo "解 tar → $STAGE(11G 級;解完才 pg_restore -Fd)…"
  tar -xf "$DUMP" -C "$STAGE" || { echo "✗ 解 tar 失敗"; exit 1; }
  RESTORE_SRC="$STAGE/$TOPDIR"
  [ -f "$RESTORE_SRC/toc.dat" ] || { echo "✗ 解出目錄無 toc.dat($RESTORE_SRC)"; exit 1; }
fi

# ---- 確保角色存在(新機只有 postgres)----
# 2026-07-31 單一角色整併:僅 $DB_USER 一個角色(augur_predict 已退役)
for pair in "$DB_USER:${DB_PASSWORD:-}"; do
  role="${pair%%:*}"; pw="${pair#*:}"
  has=$(psu -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$role';" 2>/dev/null)
  if [ "$has" != 1 ] && [ -n "$pw" ]; then
    psu -d postgres -c "CREATE ROLE $role LOGIN PASSWORD '$pw';" >/dev/null 2>&1 \
      && echo "  建立角色 $role" || echo "  (角色 $role 建立略過)"
  fi
done

# ---- 建庫 + 分階段還原(大檔 + HNSW 向量索引最佳化;#7 完整 log 不吞)----
echo "建立資料庫 $DB_NAME(owner=$DB_USER)…"
psu -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || { echo "✗ createdb 失敗"; exit 1; }
RLOG="${AUGUR_IMPORT_LOG:-/tmp/augur_pg_restore_$$.log}"; : > "$RLOG"
# 分三段還原:資料段 -j4 並行快載;索引/約束段降並發 + 提高 maintenance_work_mem。
# why:augur dump 含 3 個 pgvector HNSW 向量索引,「同時建置」各吃一份 maintenance_work_mem——
# 全域預設(64MB)會龜速 spill 磁碟(實證卡 70 分),盲目全域調高又讓並發建索引 OOM;
# 故索引段獨立設 IDX_MEM(預設 2GB)× 低並發(-j2),兼顧速度與 RAM(IDX_MEM×2 須 < RAM−shared_buffers)。
if [ -n "$JOBS" ]; then POSTJOBS="-j 2"; else POSTJOBS=""; fi
IDX_MEM="${IDX_MEM:-2GB}"
rcommon=(-h "$DB_HOST" -p "$DB_PORT" -U "$SU" -d "$DB_NAME" "$RESTORE_SRC")
echo "還原 pre-data(schema)…"
pg_restore --section=pre-data $JOBS "${rcommon[@]}" >>"$RLOG" 2>&1
echo "還原 data(資料 COPY,${JOBS:-sequential})…"
pg_restore --section=data $JOBS "${rcommon[@]}" >>"$RLOG" 2>&1
echo "還原 post-data(索引/約束,maintenance_work_mem=$IDX_MEM ${POSTJOBS:-sequential};HNSW 最佳化)…"
PGOPTIONS="-c maintenance_work_mem=$IDX_MEM" pg_restore --section=post-data $POSTJOBS "${rcommon[@]}" >>"$RLOG" 2>&1
errs=$(grep -c '^pg_restore: error' "$RLOG" 2>/dev/null || echo 0)
echo "  三段還原完成(完整 log=$RLOG;pg_restore error 行=$errs——GRANT 到未建角色屬非致命)"

# ---- (2026-07-31 移除)預測隔離角色 setup_predict_role ----
# 單一角色整併後 augur_predict 退役 ⇒ #8 之 DB 層動態 GRANT 閘不復存在,
# 現唯 src/augur/audit/import_isolation.py 之 AST 稽核(射程 7 package)。
# 依據=reports/augur_single_role_consolidation_plan_20260731.md

# ---- 選配:補 migrations(冪等)----
if [ "$MIGRATE" = 1 ] && [ -x "$VENV_PY" ]; then
  echo "補跑 migrate_*_ddl.py(對齊 git DDL,冪等;glob 全量+source_governance)…"
  # why 三段嘗試:26 支存在兩種旗標慣例——gated 批(須 --migrate/--run 才建)無參數會「靜默 no-op 卻 exit 0」
  # 假 ✓(2026-07-13 v4 稽核);先試 --migrate 再 --run 再無參數,不吃旗標者 argparse exit 2 自然落到下一段。
  for m in "$ROOT"/scripts/migrate_*_ddl.py "$ROOT"/scripts/migrate_source_governance.py; do
    [ -f "$m" ] || continue
    if "$VENV_PY" "$m" --migrate >/dev/null 2>&1 || "$VENV_PY" "$m" --run >/dev/null 2>&1 || "$VENV_PY" "$m" >/dev/null 2>&1; then
      echo "  ✓ $(basename "$m")"
    else
      echo "  ⚠ $(basename "$m") 未完成(查 dump 是否已含)"
    fi
  done
fi

# ---- smoke test(#7 實測;含完整性驗證——防靜默缺失,2026-07-13 教訓)----
echo "── smoke test ──"
pub=$(psu -d "$DB_NAME" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null)
tt=$(psu -d "$DB_NAME" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='ttai_import';" 2>/dev/null)
idx=$(psu -d "$DB_NAME" -tAc "SELECT count(*) FROM pg_indexes WHERE schemaname NOT IN ('pg_catalog','information_schema');" 2>/dev/null)
hnsw=$(psu -d "$DB_NAME" -tAc "SELECT count(*) FROM pg_indexes WHERE indexdef ILIKE '%USING hnsw%';" 2>/dev/null)
sz=$(psu -d postgres -tAc "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null)
echo "  public $pub 表 · ttai_import $tt 表 · 索引 $idx · HNSW 向量索引 $hnsw · 庫大小 $sz"
# HNSW 完整性斷言:augur 標準含 3 個(sent/lex/chunk),缺則索引段未跑完——勿只信 exit 0/表數(2026-07-13 踩坑)
if [ "${hnsw:-0}" -lt 3 ]; then
  echo "  ⚠ HNSW 向量索引僅 ${hnsw:-0} 個(標準應 ≥3)——索引段可能未完成,查 $RLOG;可重跑 --force 或手動補 post-data 段。"
fi
echo "════════════════════════════════════════════"
echo "  ✓ DB import 完成:$DB_NAME($sz)"
echo "════════════════════════════════════════════"
