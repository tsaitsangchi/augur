#!/usr/bin/env bash
# 🎯 DESKTOP→PC002 進化狀態增量拉取(乙案私有通道;hugo 2026-07-27「不用等週末、每二小時」)。
#
# 白話:本機=進化/arena 正典(乙案 audits §六);DESKTOP 留有 07-26 後增量(gold/RAWEVO ledger/
#   hints/coverage/eval runs)。本支經 tailscale ssh **唯讀讀取遠端、只寫本機**——
#   離線=優雅跳過(exit 0,週間常態);**偵測遠端 arena/evolution 排程仍活 → 拒絕拉取**
#   (防雙寫機械閘;停用遠端排程屬跨機破壞性變更、由人執行一次,見 --runbook)。
#   水位=本地 max PK,append-only 表 ON CONFLICT 略過=冪等。憑證不過線(遠端用遠端自己的 .env)。
# 守 #6(不代改他機設定;偵測到未停即拒)· #15(水位/計數誠實印、拒因明說)· #28(零 token)· #29。
#
# 執行指令矩陣:
#   bash scripts/pull_desktop_evolution_delta.sh              # 增量拉取(離線/未停排程=不拉)
#   bash scripts/pull_desktop_evolution_delta.sh --check      # 唯讀:連線+遠端計數 vs 本地水位(零寫入)
#   bash scripts/pull_desktop_evolution_delta.sh --runbook    # 印「在 DESKTOP 上手動執行一次」之指令
#   DESKTOP_HOST=100.x.y.z bash scripts/pull_desktop_evolution_delta.sh   # 覆寫目標(預設主機名)
set -u
HOST="${DESKTOP_HOST:-desktop-8mqpfs8}"
REMOTE_ROOT="${DESKTOP_ROOT:-/home/hugo/project/augur}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-}"
SSH="ssh -o ConnectTimeout=4 -o BatchMode=yes -o StrictHostKeyChecking=accept-new hugo@$HOST"

if [ "$MODE" = "--runbook" ]; then
  cat <<'RB'
── 一次性 runbook(在 DESKTOP 上執行;本機不代做——跨機破壞性變更 #6)──
 1) 授權本機拉取(把 PC002 公鑰加入 DESKTOP):
      mkdir -p ~/.ssh && chmod 700 ~/.ssh
      echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIM1O9qu5M/1v5okHNg1r7ySUy7PaLY137B4JEtYzF7Ue pc002-augur-pull' >> ~/.ssh/authorized_keys
      chmod 600 ~/.ssh/authorized_keys
 2) 停用其 arena/evolution 排程(乙案:本機為正典、防雙寫;備份後註解不刪):
      crontab -l > ~/crontab.backup.$(date +%Y%m%d)
      crontab -l | sed -E 's|^([^#].*(arena|evolve|evolution|deliberation).*)|#DISABLED-yian \1|' | crontab -
      for t in $(systemctl --user list-timers --all --no-pager | grep -oE 'augur-[a-z0-9-]+\.timer'); do
        systemctl --user disable --now "$t"; done
 3) 回本機驗證:bash scripts/pull_desktop_evolution_delta.sh --check
RB
  exit 0
fi

cd "$ROOT" || exit 1
set -a; . ./.env; set +a
export PGPASSWORD="${DB_SUPERUSER_PASSWORD}"
PSQL_L=(psql -h 127.0.0.1 -U "${DB_SUPERUSER_USER}" -d augur -tA)
RQ() { $SSH "cd $REMOTE_ROOT && set -a && . ./.env && set +a && PGPASSWORD=\$DB_SUPERUSER_PASSWORD psql -h 127.0.0.1 -U \$DB_SUPERUSER_USER -d augur -tA -c \"$1\""; }

if ! $SSH true 2>/dev/null; then
  echo "$(date '+%F %T') DESKTOP($HOST) 不可達——優雅跳過(週間常態;或未加 tailnet/未授權公鑰,見 --runbook)"
  exit 0
fi
echo "$(date '+%F %T') ✓ DESKTOP 可達"

# ── 防雙寫機械閘:遠端 arena/evolution 排程仍活即拒拉(不代停,#6) ──
LIVE=$($SSH 'crontab -l 2>/dev/null | grep -cvE "^#" | tr -d " "; crontab -l 2>/dev/null | grep -cE "^[^#].*(arena|evolve|evolution)" | tr -d " "' 2>/dev/null | tail -1)
if [ "${LIVE:-0}" -gt 0 ]; then
  echo "✗ 遠端仍有 ${LIVE} 條 arena/evolution 排程在跑——拒絕拉取(雙寫風險;請先跑 --runbook 第 2 步)"
  exit 1
fi
echo "  ✓ 遠端排程已停(防雙寫確立)"

pull_serial() {   # $1=表 $2=serial PK
  local t="$1" pk="$2" wm rmax n
  wm=$("${PSQL_L[@]}" -c "SELECT coalesce(max($pk),0) FROM $t" 2>/dev/null | tr -d ' ')
  rmax=$(RQ "SELECT coalesce(max($pk),0) FROM $t" 2>/dev/null | tr -d ' ')
  [ -z "${rmax:-}" ] && { printf "  %-32s (遠端無此表,略過)\n" "$t"; return; }
  if [ "$MODE" = "--check" ]; then
    printf "  %-32s 本地=%s 遠端=%s 待拉=%s\n" "$t" "${wm:-0}" "$rmax" "$((rmax-${wm:-0}))"; return
  fi
  [ "$rmax" -le "${wm:-0}" ] && { printf "  %-32s 無新列(水位 %s)\n" "$t" "${wm:-0}"; return; }
  n=$(RQ "COPY (SELECT * FROM $t WHERE $pk > ${wm:-0} ORDER BY $pk) TO STDOUT" \
      | "${PSQL_L[@]}" -c "COPY $t FROM STDIN" 2>&1 | grep -oE '[0-9]+' | tail -1)
  printf "  %-32s +%s 列(%s → %s)\n" "$t" "${n:-0}" "${wm:-0}" "$rmax"
}

echo "── 逐表水位($([ "$MODE" = "--check" ] && echo 唯讀比對 || echo 增量拉取)) ──"
pull_serial local_model_gold_sample sample_id
pull_serial raw_evolution_iteration_ledger iteration_id
pull_serial evolution_hypothesis_hint hint_id
pull_serial raw_table_coverage_snapshot snapshot_id
[ "$MODE" = "--check" ] && { echo "(--check:零寫入結束)"; exit 0; }

# eval_run:PK=文字雜湊 → 全量差集 + ON CONFLICT 略過(冪等)
TSV=$(mktemp); RQ "COPY (SELECT * FROM local_model_eval_run) TO STDOUT" > "$TSV" 2>/dev/null
n0=$("${PSQL_L[@]}" -c "SELECT count(*) FROM local_model_eval_run" | tr -d ' ')
"${PSQL_L[@]}" <<SQL >/dev/null 2>&1
BEGIN;
CREATE TEMP TABLE _er (LIKE local_model_eval_run INCLUDING DEFAULTS);
\copy _er FROM '$TSV'
INSERT INTO local_model_eval_run SELECT * FROM _er ON CONFLICT (run_id) DO NOTHING;
COMMIT;
SQL
n1=$("${PSQL_L[@]}" -c "SELECT count(*) FROM local_model_eval_run" | tr -d ' ')
rm -f "$TSV"
printf "  %-32s +%s 列(差集)\n" local_model_eval_run "$((n1-n0))"
echo "$(date '+%F %T') ✓ 完成(冪等;下輪 2h 自動再跑)"
