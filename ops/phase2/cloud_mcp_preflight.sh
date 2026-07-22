#!/usr/bin/env bash
# Cloud／遠端 MCP 前置預檢——只讀探測，不改系統、不開埠。
# 用法：
#   bash ops/phase2/cloud_mcp_preflight.sh
#   OLLAMA_URL=http://100.x.y.z:11434 bash ops/phase2/cloud_mcp_preflight.sh
set -euo pipefail

OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
OLLAMA_URL="${OLLAMA_URL%/}"
NEED_MODELS=(qwen3-coder-next nomic-embed-text)

ok() { echo "✅ $*"; }
fail() { echo "❌ $*" >&2; exit 1; }
warn() { echo "⚠ $*"; }

echo "=== cloud_mcp_preflight ==="
echo "OLLAMA_URL=$OLLAMA_URL"
echo "hostname=$(hostname)"

if ! curl -sf --max-time 5 "${OLLAMA_URL}/api/tags" -o /tmp/augur_ollama_tags_$$.json; then
  fail "無法 GET ${OLLAMA_URL}/api/tags（通道未通或 ollama 未起）"
fi
ok "api/tags 可達"

TAGS="$(cat /tmp/augur_ollama_tags_$$.json)"
rm -f /tmp/augur_ollama_tags_$$.json

for m in "${NEED_MODELS[@]}"; do
  if echo "$TAGS" | grep -q "$m"; then
    ok "模型在列：$m"
  else
    fail "模型未見：$m（請在 GB10 ollama pull）"
  fi
done

# 可選：極短 generate（不強制成功於高負載；失敗只 warn）
GEN_PAYLOAD="$(printf '%s' '{"model":"qwen3-coder-next","prompt":"Reply with exactly: OK","stream":false,"options":{"num_predict":8}}')"
if curl -sf --max-time 60 "${OLLAMA_URL}/api/generate" \
    -H 'Content-Type: application/json' \
    -d "$GEN_PAYLOAD" -o /tmp/augur_ollama_gen_$$.json; then
  if grep -q '"response"' /tmp/augur_ollama_gen_$$.json; then
    ok "api/generate 有回應（煙霧）"
  else
    warn "api/generate HTTP 200 但無 response 欄"
  fi
  rm -f /tmp/augur_ollama_gen_$$.json
else
  warn "api/generate 超時或失敗（可稍後重試；tags 已通過）"
fi

echo "=== 預檢結束（tags 通過）==="
echo "下一步：Tailscale 對端設 OLLAMA_URL 後重跑；Cloud session 依 ops/phase2/CLOUD-AGENT-MCP-PREFLIGHT.md §四勾選。"
