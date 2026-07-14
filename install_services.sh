#!/usr/bin/env bash
# 🎯 一鍵重建 augur systemd user 服務棧 + timers（換機/重開機後恢復開機自起;根治「unit 檔不隨 git 遷移」缺口)。
# 全本地、免 sudo（user 級 systemd）、零 Claude usage。啟動規格與 start_chat.sh 對齊（單一 SSOT）。
#
# 服務(6 常駐):qdrant:6333 · ollama:11434 ← advisor:8399 ← chat:8090 · admin:8500 · probability:8600
# timers(2):embed-catchup(03:30 補嵌入積壓,冪等) · l2-deliberation(每日自審,預設 disabled 待 hugo 開閘)
# 註:qdrant:6333=sentence_items serving 索引(hugo 2026-07-14 拍板上線;pgvector 仍 SSOT、Qdrant 可拋棄從 PG 重建)。
#
# ⚠ ollama 排序循環陷阱(2026-07-11 實證):user unit **不得**寫 After=default.target(與 WantedBy 成環→開機被丟棄)。
#    本腳本一律只用 WantedBy=default.target + 服務間 After=<具體服務>,不觸 default.target 依賴。
#
# 執行指令矩陣:
#   bash install_services.sh              # 生成 unit + enable-linger + enable/start 5 服務 + embed timer;實測端口
#   bash install_services.sh --with-l2    # 另 enable l2-deliberation timer(僅 hugo 開閘後)
#   bash install_services.sh --status     # 只印現況,不動
#   bash install_services.sh --uninstall  # 停用+移除所有 augur-* unit(保留 .env/資料)
set -u
ROOT="$HOME/project/augur"
UD="$HOME/.config/systemd/user"
VENV="$ROOT/venv/bin/python"
OLLAMA_BIN="$HOME/ollama/bin/ollama"
UC() { systemctl --user "$@"; }

if [ "${1:-}" = "--status" ]; then
  UC list-units 'augur-*' --all --no-pager 2>/dev/null
  UC list-timers 'augur-*' --all --no-pager 2>/dev/null
  echo "--- 端口 ---"; ss -tlnp 2>/dev/null | grep -E ':(8090|8399|8500|8600|11434)\b' || echo "(無 augur 端口在聽)"
  exit 0
fi

if [ "${1:-}" = "--uninstall" ]; then
  for u in augur-chat augur-advisor augur-admin augur-probability augur-ollama augur-qdrant augur-embed-catchup.timer augur-l2-deliberation.timer augur-audit-watchdog.timer; do
    UC disable --now "$u" 2>/dev/null; UC stop "$u" 2>/dev/null
  done
  rm -f "$UD"/augur-*.service "$UD"/augur-*.timer
  UC daemon-reload 2>/dev/null
  echo "✓ 已移除所有 augur-* unit(資料/.env 未動)"; exit 0
fi

[ -x "$VENV" ] || { echo "✗ 無 $VENV——先 pip install -e . 建 venv"; exit 1; }
[ -x "$OLLAMA_BIN" ] || echo "⚠ 無 $OLLAMA_BIN(ollama 服務會失敗;裝 ollama 至 ~/ollama/bin 後再跑)"
mkdir -p "$UD"

svc() { # $1=name $2=desc $3=unit_extra(After/Wants,進[Unit]) $4=svc_extra(Environment,進[Service]) $5...=ExecStart
  local name=$1 desc=$2 uextra=$3 sextra=$4; shift 4
  cat > "$UD/$name.service" <<EOF
[Unit]
Description=$desc
$uextra

[Service]
Type=simple
WorkingDirectory=$ROOT
$sextra
ExecStart=$*
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
}

# 0) qdrant serving 索引(sentence_items;hugo 2026-07-14 拍板上線;pgvector 仍 SSOT、此可拋棄從 PG 重建)
#    storage=augur 專屬 ~/qdrant_augur(不共用 ttai);二進位暫用 ttai native 檔;retrieval.py 對故障自動降級 pgvector
svc augur-qdrant "augur Qdrant serving 索引 (:6333)" \
  "" "Environment=QDRANT__STORAGE__STORAGE_PATH=%h/qdrant_augur
Environment=QDRANT__SERVICE__HTTP_PORT=6333
Environment=QDRANT__SERVICE__GRPC_PORT=6334
Environment=QDRANT__TELEMETRY_DISABLED=true" \
  "$HOME/project/ttai/.qdrant_server/qdrant"
# 1) ollama(最底層,無服務依賴;OLLAMA_MODELS 與 start_chat.sh 一致=~/ollama/models,非預設 ~/.ollama)
svc augur-ollama "augur Ollama 模型後端 (:11434)" \
  "" "Environment=OLLAMA_MODELS=%h/ollama/models" \
  "$OLLAMA_BIN" serve
# 2) advisor 殼(依 ollama;advise+guard 唯一出口)
svc augur-advisor "augur 顧問殼 advise+guard (:8399)" \
  "After=augur-ollama.service
Wants=augur-ollama.service" \
  "Environment=OLLAMA_BASE_URL=http://127.0.0.1:11434" \
  "$VENV" "$ROOT/scripts/serve_advisor_openai.py" --serve --model qwen3:8b --timeout 400 --port 8399
# 3) chat UI(依 advisor;瀏覽器前端)
svc augur-chat "augur 對話 UI 誠實博學的我 (:8090)" \
  "After=augur-advisor.service
Wants=augur-advisor.service" "" \
  "$VENV" "$ROOT/scripts/serve_chat_ui.py" --port 8090
# 4) admin console(獨立;連 DB)
svc augur-admin "augur 後台知識控制台 (:8500)" "" "" \
  "$VENV" "$ROOT/scripts/serve_admin_console.py" --serve
# 5) probability UI(獨立;連 DB)
svc augur-probability "augur 機率/預測展示 UI (:8600)" "" "" \
  "$VENV" "$ROOT/scripts/serve_probability_ui.py" --serve

# --- timer: embed-catchup(03:30 補嵌入積壓;主語料 sentence works zh;embed_knowledge 冪等只嵌未嵌) ---
cat > "$UD/augur-embed-catchup.service" <<EOF
[Unit]
Description=augur 嵌入積壓補跑(sentence works zh;冪等)

[Service]
Type=oneshot
WorkingDirectory=$ROOT
ExecStart=$VENV $ROOT/scripts/embed_knowledge.py --layer sentence --language zh
EOF
cat > "$UD/augur-embed-catchup.timer" <<EOF
[Unit]
Description=augur 嵌入積壓補跑 03:30 每日

[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# --- timer: l2-deliberation(每日自審;預設 disabled,待 hugo 開閘) ---
cat > "$UD/augur-l2-deliberation.service" <<EOF
[Unit]
Description=augur L2 每日自主審議(零 token;GATE+A5 過後)

[Service]
Type=oneshot
WorkingDirectory=$ROOT
ExecStart=$VENV $ROOT/scripts/run_daily_deliberation.py --run
EOF
cat > "$UD/augur-l2-deliberation.timer" <<EOF
[Unit]
Description=augur L2 每日自審 06:15

[Timer]
OnCalendar=*-*-* 06:15:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# --- timer: audit-watchdog(每 30 分驗證 audit 執行狀況;selfheal 死且未綠→relaunch,flock 防重複) ---
cat > "$UD/augur-audit-watchdog.service" <<EOF
[Unit]
Description=augur audit 監看看門狗(每 30 分驗證+異常 relaunch)

[Service]
Type=oneshot
WorkingDirectory=$ROOT
ExecStart=/usr/bin/bash $ROOT/audit_watchdog.sh
EOF
cat > "$UD/augur-audit-watchdog.timer" <<EOF
[Unit]
Description=augur audit 監看 每 30 分

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
EOF

UC daemon-reload
loginctl enable-linger "$USER" 2>/dev/null && echo "✓ enable-linger(無登入也自起)" || echo "⚠ enable-linger 失敗(需 root 或已設)"

echo "啟用 6 常駐服務 + embed timer…"
# enable(開機自起 link)+restart(套用新 unit;inactive→start、active→restart,故重跑冪等且更新 unit 會生效)
for u in augur-qdrant augur-ollama augur-advisor augur-chat augur-admin augur-probability; do
  UC enable "$u.service" 2>/dev/null; UC restart "$u.service"
done
UC enable augur-embed-catchup.timer 2>/dev/null; UC restart augur-embed-catchup.timer 2>/dev/null
UC enable augur-audit-watchdog.timer 2>/dev/null; UC restart augur-audit-watchdog.timer 2>/dev/null   # audit 未綠期間監看;綠後 no-op
UC enable augur-l2-deliberation.timer 2>/dev/null   # timer 檔就緒但不啟(--now),待開閘
[ "${1:-}" = "--with-l2" ] && { UC start augur-l2-deliberation.timer; echo "✓ L2 timer 已啟(--with-l2)"; }

echo "── 端口實測(各服務啟動需數秒;advisor 待 ollama+模型) ──"
sleep 6
for p in 11434:ollama 8399:advisor 8090:chat 8500:admin 8600:probability; do
  port=${p%%:*}; nm=${p##*:}
  ss -tlnp 2>/dev/null | grep -q ":$port " && echo "  ✓ $nm :$port 監聽中" || echo "  ⋯ $nm :$port 尚未(看 journalctl --user -u augur-$nm)"
done
echo "完成。狀態:bash install_services.sh --status｜L2 開閘:bash install_services.sh --with-l2"
