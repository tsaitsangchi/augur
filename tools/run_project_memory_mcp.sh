#!/usr/bin/env bash
# 啟動 project-memory-mcp（可攜：PYTHONPATH=repo 根，不寫死絕對路徑）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-$ROOT}"
export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
export EMBED_MODEL="${EMBED_MODEL:-nomic-embed-text}"
exec python3 -m tools.project_memory_mcp "$@"
