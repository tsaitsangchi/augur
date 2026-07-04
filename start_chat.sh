#!/usr/bin/env bash
# 誠實博學的我 — 一鍵啟動 Ollama + advisor 殼 + 對話 UI(冪等:已起則跳過)。
# 用法: bash ~/project/augur/start_chat.sh   |   停止: bash ~/project/augur/start_chat.sh stop
# 全本地、免 sudo、零 Claude usage。瀏覽器開 http://localhost:8090
set -u
ROOT="$HOME/project/augur"
VENV="$ROOT/venv/bin/python"
OLLAMA_BIN="$HOME/ollama/bin/ollama"
LOGDIR="$HOME/augur_chat_logs"; mkdir -p "$LOGDIR"

up() { ss -ltn 2>/dev/null | grep -q ":$1 "; }           # 埠是否監聽
start() {  # $1=名稱 $2=埠 $3=log $4...=指令
  local name=$1 port=$2 log=$3; shift 3
  if up "$port"; then echo "  ✓ $name(:$port)已在運行、跳過"; return; fi
  ( setsid nohup "$@" > "$LOGDIR/$log" 2>&1 < /dev/null & ) ; disown 2>/dev/null || true
  for i in $(seq 1 30); do sleep 2; up "$port" && { echo "  ✓ $name(:$port)已起 ~$((i*2))s"; return; }; done
  echo "  ✗ $name(:$port)逾時未開埠 → 看 $LOGDIR/$log"
}

if [ "${1:-start}" = "stop" ]; then
  echo "停止三服務…"
  pkill -f serve_chat_ui;        pkill -f serve_advisor_openai
  echo "  (Ollama serve 保留;要停: pkill -f 'ollama serve')"
  exit 0
fi

echo "啟動『誠實博學的我』服務棧…"
# 1) Ollama(GPU 模型後端)
if up 11434; then echo "  ✓ Ollama(:11434)已在運行、跳過"
else ( OLLAMA_MODELS="$HOME/ollama/models" setsid nohup "$OLLAMA_BIN" serve > "$LOGDIR/ollama.log" 2>&1 < /dev/null & ); disown 2>/dev/null || true
  for i in $(seq 1 20); do sleep 2; up 11434 && { echo "  ✓ Ollama(:11434)已起"; break; }; done; fi
# 2) advisor 殼(advise()+guard 唯一編排出口)
OLLAMA_BASE_URL="http://127.0.0.1:11434" \
  start "advisor 殼" 8399 advisor.log \
  "$VENV" "$ROOT/scripts/serve_advisor_openai.py" --serve --model qwen3:8b --timeout 400 --port 8399
# 3) 對話 UI(瀏覽器前端、proxy 到 advisor)
start "對話 UI" 8090 chat_ui.log \
  "$VENV" "$ROOT/scripts/serve_chat_ui.py" --port 8090

echo
echo "════════════════════════════════════════════"
echo "  誠實博學的我 → 瀏覽器開  http://localhost:8090"
echo "  (回覆較慢:本地 qwen3:8b 約 3-6 分鐘;guard 攔非逐字引用)"
echo "  log 目錄: $LOGDIR   停止: bash $0 stop"
echo "════════════════════════════════════════════"
