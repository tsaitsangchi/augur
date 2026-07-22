#!/usr/bin/env bash
# 依 hostname 選本機 OLLAMA_MODEL 後啟動 local-llm-mcp。
# 兩機硬體不同，不可共用同一模型預設（見 ops/machines/README.md）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-$ROOT}"
case "$(hostname)" in
  aitopatom-b96e)
    export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3:30b-a3b}"
    ;;
  DESKTOP-8MQPFS8)
    export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3:4b}"
    ;;
  *)
    export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3:4b}"
    ;;
esac
export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
exec python3 -m tools.local_llm_mcp "$@"
