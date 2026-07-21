#!/usr/bin/env bash
# 啟動 constitution-mcp（可攜：PYTHONPATH=repo 根）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-$ROOT}"
exec python3 -m tools.constitution_mcp "$@"
