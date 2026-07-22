#!/usr/bin/env bash
# vLLM 預檢：curl /v1/models；可選 --chat 一發 completions（含延遲）。
# 用法：
#   bash ops/phase2/vllm_preflight.sh
#   bash ops/phase2/vllm_preflight.sh --chat
#   VLLM_BASE=http://127.0.0.1:8000/v1 VLLM_MODEL=qwen3-0.6b bash ops/phase2/vllm_preflight.sh --chat
set -euo pipefail

BASE="${VLLM_BASE:-http://127.0.0.1:8000/v1}"
BASE="${BASE%/}"
MODEL="${VLLM_MODEL:-qwen3-4b}"
DO_CHAT=0
for a in "$@"; do
  case "$a" in
    --chat) DO_CHAT=1 ;;
    -h|--help)
      echo "Usage: $0 [--chat]"
      exit 0
      ;;
  esac
done

echo "== vLLM preflight =="
echo "BASE=$BASE MODEL=$MODEL"

echo "-- GET $BASE/models"
t0=$(date +%s%3N)
if ! curl -sS -m 5 "$BASE/models" | tee /tmp/augur-vllm-models.json | head -c 2000; then
  echo
  echo "FAIL: /v1/models 不可達（vLLM 未起？見 ops/phase2/VLLM-GB10.md）"
  exit 1
fi
t1=$(date +%s%3N)
echo
echo "OK: /v1/models latency_ms=$((t1 - t0))"

if [[ "$DO_CHAT" -eq 1 ]]; then
  echo "-- POST $BASE/chat/completions (max_tokens=64)"
  body=$(python3 - <<PY
import json
print(json.dumps({
    "model": "$MODEL",
    "messages": [{"role": "user", "content": "Reply with exactly: pong"}],
    "max_tokens": 64,
    "stream": False,
    "chat_template_kwargs": {"enable_thinking": False},
}))
PY
)
  t0=$(date +%s%3N)
  if ! curl -sS -m 120 "$BASE/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer EMPTY" \
    -d "$body" | tee /tmp/augur-vllm-chat.json | head -c 2000; then
    echo
    echo "FAIL: chat/completions"
    exit 1
  fi
  t1=$(date +%s%3N)
  echo
  echo "OK: chat/completions latency_ms=$((t1 - t0))"
fi

echo "preflight: PASS"
