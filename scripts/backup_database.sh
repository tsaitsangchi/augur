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
# 鏡像哨兵（M-O2,2026-08-03）:原 [3/4] 為 `mkdir -p && cp -r … && echo "✓ 鏡像完成"`——**綠燈量的是
# cp 當下的 rc,不是「鏡像現在還在、且還原得回來」**。實測:08-01 那輪之 ~/logs/backup.log 逐字寫
# 「✓ 鏡像完成」,而 /mnt/c/database 為 total 0(空)。現改為鏡像後一律過 scripts/verify_backup_mirror.py
# （pg_restore -l 驗 toc＋資料檔數比對＋與本地逐項比對＋新鮮度 ≤ 8 日）,並附一列備份帳本;
# **唯讀狀態模式亦跑同一哨兵,紅則離開碼非 0**（單一住所 #12:判準只有一份,住 verify_backup_mirror.py）。
#
# 執行指令矩陣
# ------------
#   bash scripts/backup_database.sh              # 無參數=印現況+跑鏡像哨兵(唯讀;哨兵紅則 exit≠0)
#   bash scripts/backup_database.sh --run        # 跑一輪:dump→驗 toc→打 tar→鏡像 dir+tar→驗鏡像+記帳→輪替
#   bash scripts/backup_database.sh --selftest   # 紅綠自測(免 DB:輪替白名單/路徑判定/哨兵紅路徑)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DUMP_DIR="${AUGUR_DUMP_DIR:-$HOME/db_dumps}"
MIRROR_DIR="${AUGUR_DUMP_MIRROR:-/mnt/c/database}"
KEEP_WEEKLY="${AUGUR_DUMP_KEEP:-3}"          # 本地保留週數
KEEP_MIRROR="${AUGUR_DUMP_KEEP_MIRROR:-2}"   # 鏡像保留週數
LOCK=/tmp/augur_pgdump.lock
NAME_RE='^augur_[0-9]{8}_weekly_Fd$'         # 輪替白名單:僅本支產物可被刪(#6 誤刪界)
TAR_RE='^augur_[0-9]{8}_weekly_Fd\.tar$'     # 同日單檔(內層已 -Z1,不再 gzip)

is_rotatable() {  # $1=目錄或 .tar → 0/1。純函式(僅字串判定),selftest 餵真輸入驗
  local b
  b="$(basename "$1")"
  [[ "$b" =~ $NAME_RE ]] || [[ "$b" =~ $TAR_RE ]]
}

pack_tar() {  # $1=-Fd 目錄 → 同路徑旁 .tar(內含 <basename>/toc.dat)。失敗非 0
  local dest="$1" parent base tarf part inner
  parent="$(dirname "$dest")"
  base="$(basename "$dest")"
  tarf="${dest}.tar"
  part="${tarf}.part"
  rm -f "$part"
  tar -C "$parent" -cf "$part" "$base" || { rm -f "$part"; return 1; }
  inner="$(tar -tf "$part" | grep -m1 'toc\.dat$' || true)"
  [ -n "$inner" ] || { echo "✗ tar 內無 toc.dat——不轉正" >&2; rm -f "$part"; return 1; }
  mv "$part" "$tarf"
  echo "  ✓ tar $(du -sh "$tarf" | cut -f1) 內含 $inner"
}

rotate_kind() {  # $1=目錄 $2=留幾份 $3=dir|tar —— 兩種產物分開輪替,不可混成一列
  local root="$1" keep="$2" kind="$3"
  local -a items=()
  shopt -s nullglob
  if [ "$kind" = tar ]; then
    items=( "$root"/augur_*_weekly_Fd.tar )
  else
    items=( "$root"/augur_*_weekly_Fd )
  fi
  shopt -u nullglob
  [ "${#items[@]}" -eq 0 ] && return 0
  printf '%s\n' "${items[@]}" | sort | head -n -"$keep" | while read -r old; do
    [ -n "$old" ] || continue
    is_rotatable "$old" && { echo "  輪替刪除 $(basename "$old")"; rm -rf "$old"; } \
      || echo "  跳過白名單外 $(basename "$old")"
  done
}

mirror_sentinel() {  # → rc 0=綠 / 非 0=紅。判準單一住所=scripts/verify_backup_mirror.py
  local py="$ROOT/venv/bin/python" rc=0
  # 找不到直譯器一律**判紅**(不是略過):哨兵存在的理由就是不確定時擋下(同 ops/githooks/pre-commit)
  [ -x "$py" ] || { echo "  ✗ 找不到 $py——哨兵跑不了,fail-closed 判紅(非略過)" >&2; return 1; }
  "$py" "$ROOT/scripts/verify_backup_mirror.py" --check "$@" | sed 's/^/  /' || rc=$?
  return $rc
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
  local rc=0
  mirror_sentinel || rc=$?
  return $rc
}

run() {
  exec 9>"$LOCK"
  flock -n 9 || { echo "✗ 另一輪 dump 進行中($LOCK)——不並發" >&2; exit 3; }
  cd "$ROOT"; set -a; . ./.env; set +a
  local day dest tmp t0
  day=$(date +%Y%m%d); dest="$DUMP_DIR/augur_${day}_weekly_Fd"; tmp="${dest}.part"; t0=$(date +%s)
  if [ -d "$dest" ]; then
    echo "✓ 今日已備份($dest)——dump 冪等跳過;仍確保 tar＋鏡像（冪等≠免驗）"
  else
    mkdir -p "$DUMP_DIR"; rm -rf "$tmp"
    echo "[1/5] pg_dump -Fd -j4 -Z1 → $tmp(#30 口徑;期間禁 DDL)"
    PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
      -Fd -j 4 -Z 1 -d "$DB_NAME" -f "$tmp"
    echo "[2/5] 驗 toc(pg_restore -l 可解析才算備份,否則只是位元組)"
    local n_obj
    n_obj=$(pg_restore -l "$tmp" 2>/dev/null | grep -vc '^;') || { echo "✗ toc 不可解析——保留 $tmp 供鑑識,不轉正" >&2; exit 4; }
    [ "$n_obj" -gt 100 ] || { echo "✗ 物件數異常($n_obj)——不轉正" >&2; exit 4; }
    mv "$tmp" "$dest"
    echo "  ✓ $(du -sh "$dest" | cut -f1) / $n_obj 物件 / $(( $(date +%s)-t0 ))s"
  fi
  echo "[3/5] 打 tar（單檔搬運;內層已 -Z1,不再 gzip）→ ${dest}.tar"
  if [ -f "${dest}.tar" ]; then
    echo "  ✓ tar 已在——打包冪等跳過"
  else
    pack_tar "$dest" || { echo "✗ 打包 tar 失敗" >&2; exit 4; }
  fi
  echo "[4/5] 鏡像 dir+tar → $MIRROR_DIR(跨 vhdx 邊界;drvfs 慢屬預期)"
  local mirror_rc=0 mdir mtar
  mkdir -p "$MIRROR_DIR"
  mdir="$MIRROR_DIR/$(basename "$dest")"
  if [ -d "$mdir" ] && [ -f "$mdir/toc.dat" ] \
     && [ "$(du -sb "$dest" | cut -f1)" = "$(du -sb "$mdir" | cut -f1)" ]; then
    echo "  鏡像目錄已齊（位元組相符）——跳過 cp"
  else
    cp -r "$dest" "$MIRROR_DIR/" \
      || echo "  ⚠ 目錄 cp 回報失敗(本地 dump 已成,僅少一層)"
  fi
  if [ -f "${dest}.tar" ]; then
    mtar="$MIRROR_DIR/$(basename "${dest}.tar")"
    if [ -f "$mtar" ] && [ "$(stat -c%s "${dest}.tar")" = "$(stat -c%s "$mtar")" ]; then
      echo "  鏡像 tar 已齊（位元組相符）——跳過 cp"
    else
      cp -f "${dest}.tar" "$MIRROR_DIR/" \
        || echo "  ⚠ tar cp 回報失敗(本地 tar 已成,僅少一層)"
    fi
  fi
  # **cp 的 rc 不是證據**:驗的是鏡像現在還在、toc 可解析、資料檔齊、與本地逐項相符(M-O2)
  mirror_sentinel --record || mirror_rc=$?
  echo "[5/5] 輪替(白名單 目錄 $NAME_RE／tar $TAR_RE;本地留 $KEEP_WEEKLY、鏡像留 $KEEP_MIRROR)"
  for pair in "$DUMP_DIR:$KEEP_WEEKLY" "$MIRROR_DIR:$KEEP_MIRROR"; do
    local dir="${pair%%:*}" keep="${pair##*:}"
    rotate_kind "$dir" "$keep" dir
    rotate_kind "$dir" "$keep" tar
  done
  [ "$mirror_rc" -eq 0 ] || {
    echo "✗ 備份輪:本地 dump 完好且已驗 toc,但**鏡像未通過可還原驗證**——異地層形同不存在" >&2
    exit 5
  }
  echo "✓ 備份輪完成(本地已驗 toc;鏡像已驗可還原+記帳)"
}

selftest() {
  local ok=0
  chk() { if [ "$2" = 1 ]; then echo "  ✓ $1"; else echo "  ✗ $1"; ok=1; fi; }
  # 純函式餵真輸入,紅綠雙向(禁字面斷言)
  chk "本支產物名 ⇒ 可輪替" "$(is_rotatable "/x/augur_20260801_weekly_Fd" && echo 1 || echo 0)"
  chk "本支單檔 tar ⇒ 可輪替" "$(is_rotatable "/x/augur_20260801_weekly_Fd.tar" && echo 1 || echo 0)"
  chk "手動 dump(postmerge)⇒ 白名單外不動" "$(is_rotatable "/x/augur_20260731_postmerge_Fd" && echo 0 || echo 1)"
  chk "仿冒 tar ⇒ 不動" "$(is_rotatable "/x/evil_augur_20260801_weekly_Fd.tar" && echo 0 || echo 1)"
  chk "前綴仿冒(evil_augur_..._weekly_Fd)⇒ 不動" "$(is_rotatable "/x/evil_augur_20260801_weekly_Fd" && echo 0 || echo 1)"
  chk "部分名(augur_weekly)⇒ 不動" "$(is_rotatable "/x/augur_weekly" && echo 0 || echo 1)"
  chk "dump 先寫 .part 再轉正(中斷不留假完整品)" "$(grep -c 'tmp}.part\|\.part' "${BASH_SOURCE[0]}" | awk '{print ($1>=2)?1:0}')"
  chk "tar 先寫 .part 再轉正" "$(grep -q 'part="${tarf}.part"' "${BASH_SOURCE[0]}" && grep -q 'mv "$part" "$tarf"' "${BASH_SOURCE[0]}" && echo 1 || echo 0)"
  chk "未轉正 .tar.part ⇒ 不輪替" "$(is_rotatable "/x/augur_20260801_weekly_Fd.tar.part" && echo 0 || echo 1)"
  # 取**首個**匹配:取末個會掃到本斷言自己這行(2026-08-01 實犯=該型第四犯,詳 guard 記憶)
  chk "toc 驗證在轉正之前(不可解析=不算備份)" "$(awk '/pg_restore -l/{if(!a)a=NR} /mv "\$tmp" "\$dest"/{if(!b)b=NR} END{print (a&&b&&a<b)?1:0}' "${BASH_SOURCE[0]}")"
  # ── 鏡像哨兵:驗**行為**不驗字面(#35)。判準本體之紅綠在 verify_backup_mirror.py --selftest;
  #    此處另跑一條真端到端紅路徑——空鏡像目錄必須使 mirror_sentinel 非 0。
  chk "鏡像哨兵判準自測(verify_backup_mirror --selftest)" \
    "$("$ROOT/venv/bin/python" "$ROOT/scripts/verify_backup_mirror.py" --selftest >/dev/null 2>&1 && echo 1 || echo 0)"
  local td; td=$(mktemp -d)
  chk "空鏡像目錄 ⇒ 哨兵判紅(今日 live 之形狀)" \
    "$( ( export AUGUR_DUMP_MIRROR="$td"; mirror_sentinel >/dev/null 2>&1 ) && echo 0 || echo 1 )"
  chk "唯讀狀態模式承接哨兵判定(哨兵紅 ⇒ status 非 0)" \
    "$( ( export AUGUR_DUMP_MIRROR="$td"; status >/dev/null 2>&1 ) && echo 0 || echo 1 )"
  chk "找不到直譯器 ⇒ fail-closed 判紅(非略過)" \
    "$( ( ROOT=/nonexistent-augur-root; mirror_sentinel >/dev/null 2>&1 ) && echo 0 || echo 1 )"
  local pd; pd=$(mktemp -d)
  mkdir -p "$pd/augur_20260801_weekly_Fd"
  : > "$pd/augur_20260801_weekly_Fd/toc.dat"
  chk "pack_tar 真打出含 toc.dat 之單檔" \
    "$( pack_tar "$pd/augur_20260801_weekly_Fd" >/dev/null && tar -tf "$pd/augur_20260801_weekly_Fd.tar" | grep -q 'toc\.dat$' && echo 1 || echo 0 )"
  rm -rf "$pd"
  rmdir "$td"
  echo "自測:$([ $ok -eq 0 ] && echo '全通過 ✓' || echo '有失敗 ✗')"
  return $ok
}

case "${1:-}" in
  --run)      run ;;
  --selftest) selftest ;;
  "")         status ;;
  *) sed -n '2,22p' "${BASH_SOURCE[0]}"; exit 2 ;;
esac
