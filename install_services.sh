#!/usr/bin/env bash
# 🎯 一鍵重建 augur systemd user 服務棧 + timers（換機/重開機後恢復開機自起;根治「unit 檔不隨 git 遷移」缺口)。
# 全本地、免 sudo（user 級 systemd）、零 Claude usage。啟動規格與 start_chat.sh 對齊（單一 SSOT）。
#
# 服務(6 常駐):qdrant:6333 · ollama:11434 ← advisor:8399 ← chat:8090 · admin:8500 · probability:8600
# timers:embed-catchup(03:30) · ata-advance(04:00 庫內 ATA sentences+embed,limit=200) · admission-assist(05:00 dry-run 預設;ADM-AI-ASSIST S3) · l2-deliberation(06:15,預設 disabled) · knowhow-refresh(週日,預設 disabled) · audit-watchdog(30m) · drain-deferred(30m,清 heavy-slot 積壓)
# 註:qdrant:6333=sentence_items serving 索引(hugo 2026-07-14 拍板上線;pgvector 仍 SSOT、Qdrant 可拋棄從 PG 重建)。
#
# ⚠ ollama 排序循環陷阱(2026-07-11 實證):user unit **不得**寫 After=default.target(與 WantedBy 成環→開機被丟棄)。
#    本腳本一律只用 WantedBy=default.target + 服務間 After=<具體服務>,不觸 default.target 依賴。
#
# 執行指令矩陣:
#   bash install_services.sh              # 生成 unit + enable-linger + enable/start 5 服務 + embed timer;實測端口
#   bash install_services.sh --with-l2    # 另 enable l2-deliberation timer(僅 hugo 開閘後)
#   bash install_services.sh --with-refresh  # 另 enable know-how 週更 timer(件 A/G;R-A-R3 開閘後;保守純下游)
#   bash install_services.sh --with-assist-apply  # admission-assist 改 --apply（仍禁 approve/activate；預設 dry-run）
#   bash install_services.sh --status     # 只印現況,不動
#   bash install_services.sh --uninstall  # 停用+移除所有 augur-* unit(保留 .env/資料)
set -u
# 路徑契約：PROJECT_ROOT／AUGUR_ROOT 優先；否則＝本腳本所在 repo 根（勿寫死 hugo 路徑）
ROOT="${PROJECT_ROOT:-${AUGUR_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}}"
UD="$HOME/.config/systemd/user"
VENV="$ROOT/venv/bin/python"
OLLAMA_BIN="${OLLAMA_BIN:-$HOME/ollama/bin/ollama}"
# qdrant 二進位：可覆寫；預設仍嘗試舊 ttai 路徑（各機可改用 docker／自備 binary）
QDRANT_BIN="${QDRANT_BIN:-$HOME/project/ttai/.qdrant_server/qdrant}"
UC() { systemctl --user "$@"; }

if [ "${1:-}" = "--status" ]; then
  UC list-units 'augur-*' --all --no-pager 2>/dev/null
  UC list-timers 'augur-*' --all --no-pager 2>/dev/null
  echo "--- 端口 ---"; ss -tlnp 2>/dev/null | grep -E ':(8090|8399|8500|8600|11434)\b' || echo "(無 augur 端口在聽)"
  exit 0
fi

if [ "${1:-}" = "--uninstall" ]; then
  for u in augur-chat augur-advisor augur-admin augur-probability augur-ollama augur-qdrant augur-embed-catchup.timer augur-ata-advance.timer augur-admission-assist.timer augur-l2-deliberation.timer augur-knowhow-refresh.timer augur-audit-watchdog.timer augur-drain-deferred.timer; do
    UC disable --now "$u" 2>/dev/null; UC stop "$u" 2>/dev/null
  done
  rm -f "$UD"/augur-*.service "$UD"/augur-*.timer
  rm -rf "$UD"/augur-*.service.d "$UD"/augur-*.timer.d   # drop-in 目錄同清(2026-07-26 加 drop-in 後之必要;否則重裝殘留舊 override)
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
  "$QDRANT_BIN"
# 1) ollama(最底層,無服務依賴;OLLAMA_MODELS 與 start_chat.sh 一致=~/ollama/models,非預設 ~/.ollama)
svc augur-ollama "augur Ollama 模型後端 (:11434)" \
  "" "Environment=OLLAMA_MODELS=%h/ollama/models" \
  "$OLLAMA_BIN" serve
# 2) advisor 殼(依 ollama;advise+guard 唯一出口)
svc augur-advisor "augur 顧問殼 advise+guard (:8399)" \
  "After=augur-ollama.service
Wants=augur-ollama.service" \
  "Environment=OLLAMA_BASE_URL=http://127.0.0.1:11434 OLLAMA_TIMEOUT=2400
EnvironmentFile=$ROOT/.env" \
  "$VENV" "$ROOT/scripts/serve_advisor_openai.py" --serve --model qwen3:8b --timeout 2400 --port 8399
# ↑ EnvironmentFile:RBAC secret(AUGUR_INTERNAL_SECRET)顯式注入——先前只靠 import philosophy.retrieval
#   副作用觸發 load_dotenv 才有 secret,import 順序一動即靜默轉 fail-closed deny-all(答段脆弱點,07-14 硬化)
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

# --- timer: ata-advance(KH-ATA-SCHED;04:00 庫內 sentences+embed;禁 fulltext／approve;FZ-keep) ---
# limit=200 勿過猛;僅 --stages sentences embed(不含 fulltext＝KH-ATA-EXEC;promote 無 --entity-type＝僅印統計)
ATA_ADVANCE_LIMIT="${ATA_ADVANCE_LIMIT:-200}"
cat > "$UD/augur-ata-advance.service" <<EOF
[Unit]
Description=augur ATA in-DB advance (sentences+embed only; KH-ATA-SCHED; no HUMAN_ONLY)

[Service]
Type=oneshot
WorkingDirectory=$ROOT
EnvironmentFile=$ROOT/.env
StandardOutput=append:$HOME/ata_advance.log
StandardError=append:$HOME/ata_advance.log
ExecStart=$VENV $ROOT/scripts/advance_knowledge_terminal.py --apply --limit $ATA_ADVANCE_LIMIT --stages sentences embed
EOF
cat > "$UD/augur-ata-advance.timer" <<EOF
[Unit]
Description=augur ATA 庫內推進 04:00 每日(KH-ATA-SCHED)

[Timer]
OnCalendar=*-*-* 04:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# --- timer: admission-assist(ADM-AI-ASSIST S3;05:00;預設 --dry-run 安全;apply 須顯式) ---
# 禁 timer 呼叫 review_knowledge_source.py --approve/--activate；只跑 assist_admission_review。
# flock -n /tmp/augur_llm.lock：與 L2／演化鏈共用 LLM 單槽；搶不到即跳過本輪。
ADM_ASSIST_LIMIT="${ADM_ASSIST_LIMIT:-20}"
# 額外參數直通（Steward 2026-07-31 以此掛總時限；空值＝不加，維持原行為）
# 例：ADM_ASSIST_EXTRA_ARGS="--max-wall-sec 3600" bash install_services.sh
ADM_ASSIST_EXTRA_ARGS="${ADM_ASSIST_EXTRA_ARGS:-}"
if [ "${ADM_ASSIST_APPLY:-0}" = "1" ] || [ "${1:-}" = "--with-assist-apply" ]; then
  ADM_ASSIST_ARGS="--apply --limit ${ADM_ASSIST_LIMIT} --kind both${ADM_ASSIST_EXTRA_ARGS:+ ${ADM_ASSIST_EXTRA_ARGS}}"
  ADM_ASSIST_MODE_NOTE="apply(有界寫帳本;仍禁升級)"
else
  ADM_ASSIST_ARGS="--dry-run --limit ${ADM_ASSIST_LIMIT} --kind both${ADM_ASSIST_EXTRA_ARGS:+ ${ADM_ASSIST_EXTRA_ARGS}}"
  ADM_ASSIST_MODE_NOTE="dry-run(零寫審批;留執行事實 admission_assist_run)"
fi
cat > "$UD/augur-admission-assist.service" <<EOF
[Unit]
Description=augur ADM-AI-ASSIST L2 預審 (${ADM_ASSIST_MODE_NOTE}; no HUMAN_ONLY)

[Service]
Type=oneshot
WorkingDirectory=$ROOT
EnvironmentFile=$ROOT/.env
StandardOutput=append:$HOME/admission_assist.log
StandardError=append:$HOME/admission_assist.log
# flock -n：鎖忙→軟跳過 exit 0（不標 failed）；真腳本失敗仍非 0
ExecStart=/bin/bash -c 'if /usr/bin/flock -n /tmp/augur_llm.lock $VENV $ROOT/scripts/assist_admission_review.py $ADM_ASSIST_ARGS; then exit 0; fi; if ! /usr/bin/flock -n /tmp/augur_llm.lock -c true; then echo "[admission-assist] skip: /tmp/augur_llm.lock busy"; exit 0; fi; exit 1'
EOF
cat > "$UD/augur-admission-assist.timer" <<EOF
[Unit]
Description=augur ADM-AI-ASSIST 預審 05:00 每日(預設 dry-run;S3)

[Timer]
OnCalendar=*-*-* 05:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# --- timer: knowhow-refresh(件 A/G;每週日 02:00;預設 disabled,待 R-A-R3 hugo 開閘;保守 --from-stage promote 純下游不觸外部 API) ---
KNOWHOW_REFRESH_ARGS="${KNOWHOW_REFRESH_ARGS:---from-stage promote --domain finance}"
cat > "$UD/augur-knowhow-refresh.service" <<EOF
[Unit]
Description=augur know-how 管線週更(件 A/G;#26 護欄:預設保守 --from-stage promote 純下游、不觸外部 API 放量)

[Service]
Type=oneshot
WorkingDirectory=$ROOT
EnvironmentFile=$ROOT/.env
ExecStart=$VENV $ROOT/scripts/refresh_knowledge_pipeline.py $KNOWHOW_REFRESH_ARGS
EOF
cat > "$UD/augur-knowhow-refresh.timer" <<EOF
[Unit]
Description=augur know-how 管線週更 週日 02:00

[Timer]
OnCalendar=Sun *-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# --- drop-in: knowhow-refresh 時間平移(V2 Phase 0.6,2026-07-26) ---
# 週日 02:00 與 01:30 演化鏈重疊(鏈含 60 分鐘收割段)→ 後移至 04:30。
# Persistent=false 為必要:實測 Persistent=true 下改 OnCalendar,systemd 視「新排程之上一次發生」
# 為錯過而**立刻補觸發一次**(2026-07-26 誤觸紀錄)。時間平移類改動一律同時關 Persistent。
mkdir -p "$UD/augur-knowhow-refresh.timer.d"
cat > "$UD/augur-knowhow-refresh.timer.d/shift.conf" <<EOF
[Timer]
OnCalendar=
OnCalendar=Sun *-*-* 04:30:00
Persistent=false
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

# --- drop-in: l2-deliberation 納入 LLM 單槽鎖(V2 Phase 0.2,2026-07-26) ---
# deliberation engine.py:32 經 make_structured_llm_fn 走 ollama,與 evolve_cycle／演化鏈搶同一個
# LLM 槽(ollama -np 1 全域序列化)。-n＝非阻塞:搶不到即跳過本輪(不排隊、不堆積);
# 連續 3 日全 skip 須回滾並改排時刻(V2 Phase 0.2 中止條件)。鎖檔與 crontab 條目同一把:/tmp/augur_llm.lock。
mkdir -p "$UD/augur-l2-deliberation.service.d"
cat > "$UD/augur-l2-deliberation.service.d/llm-lock.conf" <<EOF
[Service]
ExecStart=
ExecStart=/usr/bin/flock -n /tmp/augur_llm.lock $VENV $ROOT/scripts/run_daily_deliberation.py --run
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

# --- timer: drain-deferred(每 30 分清 evolution_deferred_work 積壓;2026-07-31 hugo 拍板) ---
# 餓死三日之修:TWEVO 23:00 秒退 rc=75 後從無補跑。本 timer 每輪只處理最舊一筆(--limit 1):
# superseded(有成功輪佐證)=廉價清帳;rerun 白名單僅 tw、rc=0 才清;slot 忙即空轉非錯誤。
# 併行安全:script 內 flock /tmp/augur_drain.lock 防雙 drain;子行程自取 heavy slot(父不持)。
cat > "$UD/augur-drain-deferred.service" <<EOF
[Unit]
Description=augur heavy-slot 積壓補跑器(superseded 清帳/白名單補跑;每輪最舊一筆)

[Service]
Type=oneshot
WorkingDirectory=$ROOT
ExecStart=$VENV $ROOT/scripts/drain_deferred_work.py --apply --limit 1
EOF
cat > "$UD/augur-drain-deferred.timer" <<EOF
[Unit]
Description=augur 積壓補跑 每 30 分

[Timer]
OnBootSec=10min
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
UC enable --now augur-ata-advance.timer 2>/dev/null; UC restart augur-ata-advance.timer 2>/dev/null  # KH-ATA-SCHED 庫內 ATA
UC enable --now augur-admission-assist.timer 2>/dev/null; UC restart augur-admission-assist.timer 2>/dev/null  # ADM-AI-ASSIST S3（預設 dry-run）
UC enable augur-audit-watchdog.timer 2>/dev/null; UC restart augur-audit-watchdog.timer 2>/dev/null   # audit 未綠期間監看;綠後 no-op
UC enable --now augur-drain-deferred.timer 2>/dev/null; UC restart augur-drain-deferred.timer 2>/dev/null  # heavy-slot 積壓補跑(2026-07-31)
UC enable augur-l2-deliberation.timer 2>/dev/null   # timer 檔就緒但不啟(--now),待開閘
UC enable augur-knowhow-refresh.timer 2>/dev/null   # 件 A/G:timer 檔就緒不啟,待 R-A-R3 hugo 開閘(--with-refresh)
[ "${1:-}" = "--with-l2" ] && { UC start augur-l2-deliberation.timer; echo "✓ L2 timer 已啟(--with-l2)"; }
[ "${1:-}" = "--with-refresh" ] && { UC start augur-knowhow-refresh.timer; echo "✓ know-how refresh timer 已啟(--with-refresh;保守 --from-stage promote)"; }
[ "${1:-}" = "--with-assist-apply" ] && echo "✓ admission-assist unit 已寫為 --apply（limit=${ADM_ASSIST_LIMIT};仍禁 approve/activate）"

echo "── 端口實測(各服務啟動需數秒;advisor 待 ollama+模型) ──"
sleep 6
for p in 11434:ollama 8399:advisor 8090:chat 8500:admin 8600:probability; do
  port=${p%%:*}; nm=${p##*:}
  ss -tlnp 2>/dev/null | grep -q ":$port " && echo "  ✓ $nm :$port 監聽中" || echo "  ⋯ $nm :$port 尚未(看 journalctl --user -u augur-$nm)"
done
echo "完成。狀態:bash install_services.sh --status｜L2 開閘:bash install_services.sh --with-l2"
