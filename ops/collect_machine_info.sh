#!/usr/bin/env bash
# 自動蒐集「本機」軟硬體基礎資訊，產生 ops/machines/<hostname>.md
#
# 設計原則：
#   - 以 hostname 為識別鍵，各機各自一檔，互不覆蓋（同一 repo、多台機器）。
#   - 只寫「實測事實」；跨機共享的說明（專案相依、治理差異）放 ops/machines/README.md。
#   - 產出檔可安全重跑覆蓋自己那份；請勿手改（手動註記寫在檔尾 NOTES，重跑會保留該區塊）。
#
# 用法：
#   ops/collect_machine_info.sh            # 產生/更新本機檔
#   ops/collect_machine_info.sh --print    # 只印到 stdout，不寫檔
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MACHINES_DIR="$SCRIPT_DIR/machines"
HOST="$(hostname)"
OUT="$MACHINES_DIR/${HOST}.md"
NOW="$(date '+%Y-%m-%d %H:%M %Z')"
PRINT_ONLY=0
[[ "${1:-}" == "--print" ]] && PRINT_ONLY=1

ver() { command -v "$1" >/dev/null 2>&1 && { "$@" 2>&1 | head -1; } || echo "(未安裝)"; }
val() { local v; v="$(eval "$1" 2>/dev/null)"; [[ -n "$v" ]] && echo "$v" || echo "n/a"; }

# ---- 蒐集 ----
OS_PRETTY="$(val 'grep ^PRETTY_NAME= /etc/os-release | cut -d= -f2- | tr -d \"')"
KERNEL="$(uname -r)"; ARCH="$(uname -m)"
IS_WSL="no"; grep -qi microsoft /proc/version 2>/dev/null && IS_WSL="yes (WSL2)"
SYSTEMD="$(systemctl is-system-running 2>/dev/null || echo offline)"
CPU_MODEL="$(val "lscpu | sed -n 's/^Model name:\\s*//p'")"
CPU_CORES="$(val "lscpu | sed -n 's/^Core(s) per socket:\\s*//p'")"
CPU_THREADS="$(val "nproc")"
MEM_KB="$(val 'grep MemTotal /proc/meminfo | awk "{print \$2}"')"
MEM_GIB="$(awk "BEGIN{if($MEM_KB+0>0)printf \"%.1f\", $MEM_KB/1024/1024; else print \"n/a\"}")"
SWAP_KB="$(val 'grep SwapTotal /proc/meminfo | awk "{print \$2}"')"
SWAP_GIB="$(awk "BEGIN{if($SWAP_KB+0>0)printf \"%.1f\", $SWAP_KB/1024/1024; else print \"0\"}")"
DISK_ROOT="$(val "df -h / | tail -1 | awk '{print \$2\" total, \"\$4\" avail (\"\$5\" used)\"}'")"

# GPU
if command -v nvidia-smi >/dev/null 2>&1; then
  GPU_LINE="$(nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader 2>/dev/null)"
  [[ -z "$GPU_LINE" ]] && GPU_LINE="偵測失敗（可能被 sandbox / 權限阻擋）"
else
  GPU_LINE="無 nvidia-smi"
fi
DXG="$( [[ -e /dev/dxg ]] && echo '存在 (WSL2 直通)' || echo '不存在' )"
NVCC_VER="$(command -v nvcc >/dev/null 2>&1 && nvcc --version 2>/dev/null | sed -n 's/.*release //p' | head -1 || echo '(未安裝)')"

# 工具鏈
declare -A TOOLS
for t in git gh python3 node npm gcc make cmake nvcc psql docker ollama; do
  if command -v "$t" >/dev/null 2>&1; then
    if [[ "$t" == "nvcc" ]]; then
      TOOLS[$t]="$(nvcc --version 2>/dev/null | sed -n 's/.*release //p' | head -1)"
    else
      TOOLS[$t]="$($t --version 2>&1 | head -1 | sed 's/^[^0-9]*//' | cut -c1-40)"
    fi
  else
    TOOLS[$t]="(未安裝)"
  fi
done

# PostgreSQL 叢集
PG_VER="$(command -v psql >/dev/null 2>&1 && psql --version 2>/dev/null | awk '{print $3}' || echo '(未安裝)')"
if command -v pg_lsclusters >/dev/null 2>&1; then
  PG_CLUSTER="$(pg_lsclusters 2>/dev/null | awk 'NR>1{print $1"/"$2" port "$3" ("$4")"}' | paste -sd'; ' -)"
  [[ -z "$PG_CLUSTER" ]] && PG_CLUSTER="無叢集"
else
  PG_CLUSTER="n/a"
fi

# 保留既有檔尾 NOTES 區塊
NOTES_BLOCK=""
if [[ -f "$OUT" ]] && grep -q '<!-- NOTES:START -->' "$OUT"; then
  NOTES_BLOCK="$(sed -n '/<!-- NOTES:START -->/,/<!-- NOTES:END -->/p' "$OUT")"
fi
if [[ -z "$NOTES_BLOCK" ]]; then
  NOTES_BLOCK=$'<!-- NOTES:START -->\n（本區塊供手動註記，重跑腳本會保留。例如：此機專責之角色、特殊設定、已知問題。）\n<!-- NOTES:END -->'
fi

# ---- 產生 Markdown ----
gen() {
cat <<EOF
# 機器基礎資訊：\`${HOST}\`

> **性質**：本機實測快照 **[I]**（自動產生，勿手改；手動註記請寫檔尾 NOTES 區塊）。
> **產生工具**：\`ops/collect_machine_info.sh\` ｜ **產生時間**：${NOW}
> 跨機共享說明（專案相依、治理差異）見 [README.md](README.md)。

## 摘要

| 面向 | 值 |
|---|---|
| 主機名 | \`${HOST}\` |
| 平台 | WSL：${IS_WSL} ｜ 架構：${ARCH} |
| OS / 核心 | ${OS_PRETTY} ／ \`${KERNEL}\` |
| systemd | ${SYSTEMD} |
| CPU | ${CPU_MODEL}（${CPU_CORES} 核 / ${CPU_THREADS} 緒） |
| 記憶體 | ${MEM_GIB} GiB（swap ${SWAP_GIB} GiB） |
| 系統碟 \`/\` | ${DISK_ROOT} |
| GPU | ${GPU_LINE} |
| GPU 直通 \`/dev/dxg\` | ${DXG} |
| CUDA \`nvcc\` | ${NVCC_VER} |
| PostgreSQL | ${PG_VER}（${PG_CLUSTER}） |

## 工具鏈

| 工具 | 版本 |
|---|---|
| git | ${TOOLS[git]} |
| gh | ${TOOLS[gh]} |
| python3 | ${TOOLS[python3]} |
| node | ${TOOLS[node]} |
| npm | ${TOOLS[npm]} |
| gcc | ${TOOLS[gcc]} |
| make | ${TOOLS[make]} |
| cmake | ${TOOLS[cmake]} |
| nvcc | ${TOOLS[nvcc]} |
| psql | ${TOOLS[psql]} |
| docker | ${TOOLS[docker]} |
| ollama | ${TOOLS[ollama]} |

## 手動註記

${NOTES_BLOCK}
EOF
}

if [[ "$PRINT_ONLY" == "1" ]]; then
  gen
else
  mkdir -p "$MACHINES_DIR"
  gen > "$OUT"
  echo "已寫入：$OUT"
fi
