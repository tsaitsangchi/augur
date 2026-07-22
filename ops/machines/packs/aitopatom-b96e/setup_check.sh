#!/usr/bin/env bash
# aitopatom-b96e 此機專用檢查——錯誤主機一律拒絕。
set -euo pipefail

EXPECTED_HOST="aitopatom-b96e"
HOST="$(hostname)"
# setup_check.sh → aitopatom-b96e → packs → machines → ops → repo 根（上 4 層）
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"

fail() { echo "❌ $*" >&2; exit 1; }
ok() { echo "✅ $*"; }
warn() { echo "⚠ $*"; }

echo "=== 設定包檢查：aitopatom-b96e ==="
echo "repo=$REPO"

[[ "$HOST" == "$EXPECTED_HOST" ]] || fail "hostname=$HOST（期望 $EXPECTED_HOST）。此設定包不可在他機執行。"
ok "hostname=$HOST"

[[ -d "$REPO/tools/constitution_mcp" ]] || fail "非 monorepo 根（缺 tools/constitution_mcp）：$REPO"
[[ -d "$REPO/src/augur" ]] || fail "非 monorepo 根（缺 src/augur）：$REPO"
ok "monorepo 根含 tools/constitution_mcp + src/augur"

if [[ -e /home/giga/augur/augur-constitution ]]; then
  warn "意外存在 /home/giga/augur/augur-constitution（歷史錯誤 PYTHONPATH）；MCP 不應再依賴它"
fi

if [[ "$REPO" == "/home/giga/augur" ]]; then
  ok "終態路徑：repo 根＝/home/giga/augur"
elif [[ "$REPO" == "/home/giga/augur-code-work" ]]; then
  warn "過渡路徑：仍在 /home/giga/augur-code-work（步 4 應收斂到 /home/giga/augur）"
else
  warn "repo 根＝$REPO（終態期望 /home/giga/augur）"
fi

if curl -sf --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null; then
  ok "ollama 11434 UP"
else
  fail "ollama 11434 不可達（systemctl --user start ollama？）"
fi

TAGS="$(curl -sf http://127.0.0.1:11434/api/tags || true)"
for m in "qwen3-coder-next" "qwen3:30b-a3b" "nomic-embed-text"; do
  if echo "$TAGS" | grep -q "$m"; then
    ok "模型已 pull：$m"
  else
    warn "模型未見於 ollama list：$m（請 ollama pull $m）"
  fi
done

DEF="$(cd "$REPO" && python3 -c 'from tools.local_llm_mcp.tools import _ollama_model; print(_ollama_model())')"
[[ "$DEF" == "qwen3-coder-next" ]] || fail "本機預設模型應為 qwen3-coder-next，實際=$DEF"
ok "local_llm 預設模型=$DEF"

IDX="$REPO/.project_memory/index.db"
if [[ -f "$IDX" ]]; then
  ok "project-memory 索引存在：$IDX"
else
  warn "索引不存在——請執行：python3 -m tools.project_memory_mcp index"
fi

warn "T1 待補：PostgreSQL / qdrant / DB 還原／應用煙霧（見 ops/phase2/T1-GB10-FULLSTACK-RUNBOOK.md）"
echo "=== 檢查結束（hostname 核對通過）==="
exit 0
