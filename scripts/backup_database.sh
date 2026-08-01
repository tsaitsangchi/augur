#!/usr/bin/env bash
# 🎯 定期 DB 備份——每週平行 pg_dump ＋ /mnt/c 鏡像 ＋ 白名單輪替。
#
# 守 CLAUDE #30（平行 dump 為預設:-Fd -j4 -Z1;先寫本地 ext4、後搬 drvfs;dump 期間禁 DDL）、
# #28（本地零 usage）、#6（輪替刪除受白名單 regex 限制,最壞誤刪界=舊 weekly dump）。
#
# 起因（登錄冊 G1,2026-08-01）:12 條 cron 零 pg_dump——唯一 dump 為 07-31 手動一次性產物,
# 且 dump＋DB＋repo 同一顆實體 C: 碟。本支解「檔案級誤刪/壞遷移」與「vhdx 損毀」兩層
# （/mnt/c 鏡像跨 vhdx 邊界）;「碟亡」層唯異裝置可解=登錄冊 G2 呈案,本支不假裝解決。
#
# 鎖檔 /tmp/augur_pgdump.lock 兼作「dump 進行中」公示——手動 DDL 前 SOP:
#   flock -n /tmp/augur_pgdump.lock true || echo "dump 進行中,DDL 等它完(#30 鎖風暴)"
#
# 執行指令矩陣
# ------------
#   bash scripts/backup_database.sh              # 無參數=印現況(唯讀:既有備份清單+空間)
#   bash scripts/backup_database.sh --run        # 跑一輪:dump→驗 toc→鏡像→輪替
#   bash scripts/backup_database.sh --selftest   # 紅綠自測(免 DB:輪替白名單/路徑判定)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DUMP_DIR="${AUGUR_DUMP_DIR:-$HOME/db_dumps}"
MIRROR_DIR="${AUGUR_DUMP_MIRROR:-/mnt/c/database}"
KEEP_WEEKLY="${AUGUR_DUMP_KEEP:-3}"          # 本地保留週數
KEEP_MIRROR="${AUGUR_DUMP_KEEP_MIRROR:-2}"   # 鏡像保留週數
LOCK=/tmp/augur_pgdump.lock
NAME_RE='^augur_[0-9]{8}_weekly_Fd$'         # 輪替白名單:僅本支產物可被刪(#6 誤刪界)

is_rotatable() {  # $1=目錄名 → 0/1。純函式(僅字串判定),selftest 餵真輸入驗
  [[ "$(basename "$1")" =~ $NAME_RE ]]
}

status() {
  echo "── 備份現況(唯讀) ──"
  echo "本地 $DUMP_DIR:"
  ls -d "$DUMP_DIR"/augur_* 2>/dev/null | while read -r d; do
    printf '  %s  %s  %s\n' "$(basename "$d")" "$(du -sh "$d" 2>/dev/null | cut -f1)" \
      "$(is_rotatable "$d" && echo '[輪替內]' || echo '[白名單外,不動]')"
  done || echo "  (無)"
  echo "鏡像 $MIRROR_DIR:"
  ls -d "$MIRROR_DIR"/augur_* 2>/dev/null | sed 's/^/  /' || echo "  (無)"
  df -h "$DUMP_DIR" "$MIRROR_DIR" 2>/dev/null | tail -2 | sed 's/^/  /'
  echo "⚠ 本支解檔案級/vhdx 級;碟亡層須異裝置(G2 呈案)——不假裝解決。"
}

run() {
  exec 9>"$LOCK"
  flock -n 9 || { echo "✗ 另一輪 dump 進行中($LOCK)——不並發" >&2; exit 3; }
  cd "$ROOT"; set -a; . ./.env; set +a
  local day dest tmp t0
  day=$(date +%Y%m%d); dest="$DUMP_DIR/augur_${day}_weekly_Fd"; tmp="${dest}.part"; t0=$(date +%s)
  [ -d "$dest" ] && { echo "✓ 今日已備份($dest)——冪等跳過"; exit 0; }
  mkdir -p "$DUMP_DIR"; rm -rf "$tmp"
  echo "[1/4] pg_dump -Fd -j4 -Z1 → $tmp(#30 口徑;期間禁 DDL)"
  PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
    -Fd -j 4 -Z 1 -d "$DB_NAME" -f "$tmp"
  echo "[2/4] 驗 toc(pg_restore -l 可解析才算備份,否則只是位元組)"
  local n_obj
  n_obj=$(pg_restore -l "$tmp" 2>/dev/null | grep -vc '^;') || { echo "✗ toc 不可解析——保留 $tmp 供鑑識,不轉正" >&2; exit 4; }
  [ "$n_obj" -gt 100 ] || { echo "✗ 物件數異常($n_obj)——不轉正" >&2; exit 4; }
  mv "$tmp" "$dest"
  echo "  ✓ $(du -sh "$dest" | cut -f1) / $n_obj 物件 / $(( $(date +%s)-t0 ))s"
  echo "[3/4] 鏡像 → $MIRROR_DIR(跨 vhdx 邊界;drvfs 慢屬預期)"
  mkdir -p "$MIRROR_DIR" && cp -r "$dest" "$MIRROR_DIR/" \
    && echo "  ✓ 鏡像完成" || echo "  ⚠ 鏡像失敗(本地 dump 已成,僅少一層)"
  echo "[4/4] 輪替(白名單 $NAME_RE;本地留 $KEEP_WEEKLY、鏡像留 $KEEP_MIRROR)"
  for pair in "$DUMP_DIR:$KEEP_WEEKLY" "$MIRROR_DIR:$KEEP_MIRROR"; do
    local dir="${pair%%:*}" keep="${pair##*:}"
    ls -d "$dir"/augur_*_weekly_Fd 2>/dev/null | sort | head -n -"$keep" | while read -r old; do
      is_rotatable "$old" && { echo "  輪替刪除 $(basename "$old")"; rm -rf "$old"; } \
        || echo "  跳過白名單外 $(basename "$old")"
    done
  done
  echo "✓ 備份輪完成"
}

selftest() {
  local ok=0
  chk() { if [ "$2" = 1 ]; then echo "  ✓ $1"; else echo "  ✗ $1"; ok=1; fi; }
  # 純函式餵真輸入,紅綠雙向(禁字面斷言)
  chk "本支產物名 ⇒ 可輪替" "$(is_rotatable "/x/augur_20260801_weekly_Fd" && echo 1 || echo 0)"
  chk "手動 dump(postmerge)⇒ 白名單外不動" "$(is_rotatable "/x/augur_20260731_postmerge_Fd" && echo 0 || echo 1)"
  chk "前綴仿冒(evil_augur_..._weekly_Fd)⇒ 不動" "$(is_rotatable "/x/evil_augur_20260801_weekly_Fd" && echo 0 || echo 1)"
  chk "部分名(augur_weekly)⇒ 不動" "$(is_rotatable "/x/augur_weekly" && echo 0 || echo 1)"
  chk "dump 先寫 .part 再轉正(中斷不留假完整品)" "$(grep -c 'tmp}.part\|\.part' "${BASH_SOURCE[0]}" | awk '{print ($1>=2)?1:0}')"
  # 取**首個**匹配:取末個會掃到本斷言自己這行(2026-08-01 實犯=該型第四犯,詳 guard 記憶)
  chk "toc 驗證在轉正之前(不可解析=不算備份)" "$(awk '/pg_restore -l/{if(!a)a=NR} /mv "\$tmp" "\$dest"/{if(!b)b=NR} END{print (a&&b&&a<b)?1:0}' "${BASH_SOURCE[0]}")"
  echo "自測:$([ $ok -eq 0 ] && echo '全通過 ✓' || echo '有失敗 ✗')"
  return $ok
}

case "${1:-}" in
  --run)      run ;;
  --selftest) selftest ;;
  "")         status ;;
  *) sed -n '2,22p' "${BASH_SOURCE[0]}"; exit 2 ;;
esac
