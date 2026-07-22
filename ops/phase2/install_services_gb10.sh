#!/usr/bin/env bash
# GB10 安全啟用：只裝應用 UI 層，不覆寫已就緒的 infra。
#
# 沿用（勿動）：
#   augur-postgres.service  :5432
#   augur-qdrant.service    :6333   （~/qdrant + config.yaml）
#   ollama.service          :11434  （既有 user unit，非 augur-ollama）
#
# 本腳本啟用：
#   augur-advisor :8399  （模型預設 qwen3:30b-a3b）
#   augur-chat    :8090
#   augur-admin   :8500
#   augur-probability :8600
#
# 用法：
#   bash ops/phase2/install_services_gb10.sh           # 寫 unit + enable/start UI
#   bash ops/phase2/install_services_gb10.sh --status  # 只看現況
#   bash ops/phase2/install_services_gb10.sh --stop    # 停 UI（不動 infra）
set -euo pipefail

ROOT="${PROJECT_ROOT:-${AUGUR_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}}"
UD="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
VENV="$ROOT/venv/bin/python"
MODEL="${AUGUR_ADVISOR_MODEL:-qwen3:30b-a3b}"
TIMEOUT="${AUGUR_ADVISOR_TIMEOUT:-900}"
UC() { systemctl --user "$@"; }

if [ ! -x "$VENV" ]; then
  echo "✗ 缺少 $VENV —— 先在 $ROOT 做 pip install -e ."
  exit 1
fi
if [ ! -f "$ROOT/.env" ]; then
  echo "✗ 缺少 $ROOT/.env"
  exit 1
fi

status_only() {
  echo "── infra（應已常駐）──"
  for u in augur-postgres augur-qdrant ollama; do
    printf '  %-18s %s\n' "$u" "$(UC is-active "$u" 2>/dev/null || echo absent)"
  done
  echo "── UI ──"
  for u in augur-advisor augur-chat augur-admin augur-probability; do
    printf '  %-18s %s\n' "$u" "$(UC is-active "$u" 2>/dev/null || echo absent)"
  done
  echo "── 端口 ──"
  ss -tln 2>/dev/null | grep -E ':(5432|6333|11434|8399|8090|8500|8600)\b' || echo "(無匹配)"
}

if [ "${1:-}" = "--status" ]; then status_only; exit 0; fi

if [ "${1:-}" = "--stop" ]; then
  for u in augur-chat augur-advisor augur-admin augur-probability; do
    UC disable --now "$u.service" 2>/dev/null || true
  done
  echo "✓ UI 已停（infra 未動）"
  status_only
  exit 0
fi

mkdir -p "$UD"
loginctl enable-linger "$USER" 2>/dev/null || true

# advisor：依既有 ollama；不建立 augur-ollama
cat > "$UD/augur-advisor.service" <<EOF
[Unit]
Description=augur advisor shell (:8399, model=${MODEL})
After=network-online.target ollama.service augur-postgres.service
Wants=ollama.service augur-postgres.service

[Service]
Type=simple
WorkingDirectory=$ROOT
Environment=OLLAMA_BASE_URL=http://127.0.0.1:11434
Environment=OLLAMA_MODEL=${MODEL}
EnvironmentFile=$ROOT/.env
ExecStart=$VENV $ROOT/scripts/serve_advisor_openai.py --serve --model ${MODEL} --timeout ${TIMEOUT} --port 8399
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

cat > "$UD/augur-chat.service" <<EOF
[Unit]
Description=augur chat UI (:8090)
After=augur-advisor.service
Wants=augur-advisor.service

[Service]
Type=simple
WorkingDirectory=$ROOT
EnvironmentFile=$ROOT/.env
ExecStart=$VENV $ROOT/scripts/serve_chat_ui.py --port 8090 --advisor http://127.0.0.1:8399
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

cat > "$UD/augur-admin.service" <<EOF
[Unit]
Description=augur admin console (:8500)
After=network-online.target augur-postgres.service
Wants=augur-postgres.service

[Service]
Type=simple
WorkingDirectory=$ROOT
EnvironmentFile=$ROOT/.env
ExecStart=$VENV $ROOT/scripts/serve_admin_console.py --serve
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

cat > "$UD/augur-probability.service" <<EOF
[Unit]
Description=augur probability UI (:8600)
After=network-online.target augur-postgres.service
Wants=augur-postgres.service

[Service]
Type=simple
WorkingDirectory=$ROOT
EnvironmentFile=$ROOT/.env
ExecStart=$VENV $ROOT/scripts/serve_probability_ui.py --serve
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# 範本入庫（與本機 ~/.config 同步）
TPL="$ROOT/ops/phase2/systemd"
mkdir -p "$TPL"
cp -f "$UD"/augur-{advisor,chat,admin,probability}.service "$TPL/"

UC daemon-reload

echo "啟用 UI（模型=$MODEL timeout=${TIMEOUT}s）…"
for u in augur-advisor augur-chat augur-admin augur-probability; do
  UC enable "$u.service"
  UC restart "$u.service"
done

echo "等待埠就緒…"
sleep 8
ok=0
for p in 8399:advisor 8090:chat 8500:admin 8600:probability; do
  port=${p%%:*}; nm=${p##*:}
  if ss -tln 2>/dev/null | grep -q ":$port "; then
    echo "  ✓ $nm :$port"
    ok=$((ok + 1))
  else
    echo "  ✗ $nm :$port 尚未 — journalctl --user -u augur-$nm -n 40 --no-pager"
  fi
done

# 輕量 advisor 探活（不跑完整 LLM）
if curl -sf --max-time 3 http://127.0.0.1:8399/v1/models >/dev/null 2>&1; then
  echo "  ✓ advisor /v1/models OK"
else
  echo "  ⋯ advisor /v1/models 尚未（30b 冷啟可能較慢；看 journal）"
fi

echo "── 完成（$ok/4 UI 埠）──"
echo "狀態: bash ops/phase2/install_services_gb10.sh --status"
echo "對話: http://127.0.0.1:8090  （SSH 隧道或本機瀏覽）"
echo "⚠ 勿跑舊版 install_services.sh（會覆寫 qdrant／另建 augur-ollama）"
