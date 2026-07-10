#!/usr/bin/env bash
# 🎯 一鍵換機接續 — 在新電腦上串起「本地優先」前置動作,零 Claude usage。
# 冪等、可重跑;碰缺前置或破壞性即停手交人(#6/#26)。不自動摧毀既有 DB。
#
# 執行指令矩陣:
#   bash resume_project.sh              # 跑全部可自動化前置(source 同步→套件→memory→DB→smoke)
#   bash resume_project.sh --with-db    # 連 DB import 也做(augur 缺才建;已存在仍不動,要重匯用 import_database.sh --force)
#
# 無法自動化的兩個人工前置(本腳本會檢查並提示,不代勞):
#   (1) .env 重建(含密鑰、不在 git)   (2) dump 實體搬到本機(6.6GB、不在 git)
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1
VENV_PY="$ROOT/venv/bin/python"
WITH_DB=0; [ "${1:-}" = "--with-db" ] && WITH_DB=1

step() { echo ""; echo "▶ $1"; }
echo "═══ augur 換機接續(本地優先) ═══"

# ---- 0) 硬前置:.env ----
step "0/5 檢查 .env(含 DB 憑證/密鑰,不在 git、須手動重建)"
if [ ! -f "$ROOT/.env" ]; then
  echo "  ✗ 無 .env——這是無法自動化的人工前置。請先重建 .env(鍵見 HANDOFF.md §3)再重跑。"
  exit 1
fi
echo "  ✓ .env 存在"

# ---- 1) 套件(venv 缺則自建)----
step "1/5 venv + pip install -e .(scripts 個別可執行)"
if [ ! -x "$VENV_PY" ]; then
  echo "  venv 不存在 → 建立(python -m venv venv)…"
  python3 -m venv "$ROOT/venv" || { echo "  ✗ 建 venv 失敗(python3 是否安裝?)"; exit 1; }
fi
"$ROOT/venv/bin/pip" install -e . -q && echo "  ✓ 套件就緒" || { echo "  ✗ pip install 失敗(OS 依賴?lightgbm 需 OpenMP libgomp)"; exit 1; }

# ---- 2) 源碼同步 ----
step "2/5 sync_from_github.sh(安全 fast-forward)"
bash "$ROOT/sync_from_github.sh" || echo "  ⚠ 同步未完成(分岔/髒樹?依其訊息處理);接續其餘步驟"

# ---- 3) memory 還原 ----
step "3/5 sync_memory.py restore(還原 Claude memory)"
"$VENV_PY" "$ROOT/sync_memory.py" restore || echo "  ⚠ memory 還原未完成"

# ---- 4) DB ----
step "4/5 資料庫"
set -a; source "$ROOT/.env"; set +a
export PGPASSWORD="${DB_SUPERUSER_PASSWORD:-}"
DBN="${DB_NAME:-augur}"
tbl=$(psql -h "${DB_HOST:-127.0.0.1}" -p "${DB_PORT:-5432}" -U "${DB_SUPERUSER_USER:-postgres}" -d "$DBN" \
      -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "NODB")
if [ "$tbl" = "NODB" ] || [ "${tbl:-0}" = "0" ]; then
  if [ "$WITH_DB" = 1 ]; then
    echo "  augur 庫缺/空 → 跑 import_database.sh"
    bash "$ROOT/import_database.sh" || echo "  ⚠ DB import 未完成(dump 是否已搬到本機?見其訊息)"
  else
    echo "  augur 庫缺/空。DB import 未做——加 --with-db 讓本腳本一併匯入(需 dump 已搬到本機),"
    echo "  或手動 bash import_database.sh。"
  fi
else
  echo "  ✓ augur 庫已存在($tbl 個 public 表)——不動(要重匯用 import_database.sh --force)"
fi

# ---- 5) smoke test ----
step "5/5 import smoke test"
"$VENV_PY" -c "import augur; from augur.core import db; print('  ✓ import augur OK')" 2>&1 | grep -v dotenv || true

echo ""
echo "═══ 接續前置完成 ═══"
echo "後續(依需要):systemd 常駐服務(chat:8090/advisor:8399/admin:8500/ollama:11434)、讀 HANDOFF.md §4 進度、reports/augur_construction_understanding_20260710.md 建構全貌。"
