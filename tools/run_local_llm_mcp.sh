#!/usr/bin/env bash
# 啟動 local-llm-mcp（可攜：PYTHONPATH=repo 根、cwd 無關）。
# 模型選擇**單一住所＝工具內 _default_model_for_host()**（LLM_MODEL/OLLAMA_MODEL 可覆寫）；
# 本檔不再維護 hostname→模型表（2026-07-28 前曾與工具表打架：GB10 寫 30b-a3b vs 工具 qwen3-coder-next）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-$ROOT}"
export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
exec python3 -m tools.local_llm_mcp "$@"
