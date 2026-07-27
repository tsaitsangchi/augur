#!/usr/bin/env bash
# 🎯 一鍵重建 augur crontab 條目（換機後恢復排程;根治「cron 不隨 git 遷移」缺口）。
# 對稱工具:systemd 側＝install_services.sh;本腳本只管 cron 側。全本地、免 sudo、零 Claude usage。
#
# **設計要點:合併而非覆蓋**——本機 crontab 可能含非 augur 條目(如 stock_backend 舊專案),
# 一律**保留原樣**;只以標記行 `# >>> augur` / `# <<< augur` 圍出 augur 區塊並整段替換。
# 沒有標記時視為首次安裝、附加於末尾。故重複執行冪等、且不會吃掉別人的排程。
#
# 條目來源＝本檔 AUGUR_BLOCK（單一 SSOT;改排程改這裡、跑一次本腳本即生效、隨 git 走）。
# ⚠ LLM 單槽鎖:凡呼叫 ollama 之條目一律經 `flock -n /tmp/augur_llm.lock`
#   （與 install_services.sh 之 l2-deliberation drop-in 同一把鎖;ollama -np 1 全域序列化,
#     不鎖則多支互搶、全部變慢且結果不可比。-n＝搶不到即跳過本輪,不排隊不堆積。）
#
# 執行指令矩陣:
#   bash install_cron.sh              # 無參數:唯讀比對(現行 vs 本檔期望,印 diff、不動)
#   bash install_cron.sh --apply      # 安裝/更新 augur 區塊（先自動備份;偵測到標記外舊條目會拒絕）
#   bash install_cron.sh --migrate    # 首次遷移:吸收標記外之舊 augur 條目（明示取代、先備份）
#   bash install_cron.sh --dry-run    # 印出將寫入之完整 crontab、不動
#   bash install_cron.sh --uninstall  # 移除 augur 區塊（保留他人條目）
#   bash install_cron.sh --selftest   # 零 DB／零副作用紅綠
set -u
ROOT="${PROJECT_ROOT:-${AUGUR_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}}"
BEGIN="# >>> augur (install_cron.sh 管理;勿手改此區塊,改本腳本 AUGUR_BLOCK)"
END="# <<< augur"
BAK_DIR="$HOME/backups/cron"

AUGUR_BLOCK=$(cat <<EOF
$BEGIN
# 演化標準作業鏈(每日 01:30;七段:收割→求知→二遍收割→演化→備料;LLM 單槽鎖)
30 1 * * * flock -n /tmp/augur_llm.lock bash $ROOT/run_evolution_chain.sh
# 連續演化(6h;錯開 01:30 鏈——*/6 會落在 01:15 撞鏈;LLM 單槽鎖)
15 4,10,16,22 * * * flock -n /tmp/augur_llm.lock bash -c 'cd $ROOT && venv/bin/python scripts/evolve_cycle.py --cycle' >> \$HOME/logs/evolve_cycle.log 2>&1
# 自我求知(6h;純 SQL/文字,不碰 ollama,故不入鎖)
45 */6 * * * cd $ROOT && venv/bin/python scripts/evolve_self_seek.py --seek >> \$HOME/logs/self_seek.log 2>&1
# 週一 08:00 維運健檢(VACUUM/磁碟/zram)
0 8 * * 1 { date; cd $ROOT && set -a && . ./.env && set +a && PGPASSWORD=\$DB_PASSWORD psql -h \$DB_HOST -p \$DB_PORT -U \$DB_USER -d \$DB_NAME -c "VACUUM ANALYZE"; free -h; df -h /; /usr/local/bin/ollama list; pg_lsclusters; zramctl; echo ----; } >> \$HOME/logs/ops_weekly.log 2>&1
# 週一 08:40 工具自測(錯開 08:00 維運;原 08:10 過近)
40 8 * * 1 cd $ROOT && { date; bash ops/gpu-verify/gpu_verify.sh; python3 -m tools.constitution_mcp --selftest; python3 -m tools.local_llm_mcp --selftest; python3 -m tools.project_memory_mcp --selftest; echo ----; } >> \$HOME/logs/verify_weekly.log 2>&1
# arena 每交易日出單(hugo 2026-07-26「讓 arena 的鐘重新走起來」;全鏈=sync〔freeze mdc 有界豁免 V2-FZ-scope〕
# →特徵→對局;雙機械閘+休市誠實缺席 exit 0;取代已完成使命之 oneshot)
0 20 * * 1-5 cd $ROOT && venv/bin/python scripts/run_arena_daily_pipeline.py --run >> \$HOME/logs/arena_pipeline.log 2>&1
# arena 每日結算+官方計分板(冪等;標籤到期才結;三基準並排+洩漏稽核)
30 21 * * 1-5 cd $ROOT && venv/bin/python scripts/settle_arena_labels.py --run >> \$HOME/logs/arena_settle.log 2>&1; cd $ROOT && venv/bin/python scripts/settle_arena_labels.py --scoreboard >> \$HOME/logs/arena_settle.log 2>&1
# Steward 提問帳本 2h 增量(hugo 2026-07-27「每二個小時做一次」;純本地零 Claude token)
17 */2 * * * cd $ROOT && venv/bin/python scripts/mine_steward_questions.py --run >> \$HOME/logs/qledger.log 2>&1 && venv/bin/python scripts/triage_questions.py --run >> \$HOME/logs/qledger.log 2>&1
# DESKTOP→本機 進化增量拉取 2h(乙案私有通道;離線=優雅跳過、遠端排程未停即拒拉)
37 */2 * * * cd $ROOT && bash scripts/pull_desktop_evolution_delta.sh >> \$HOME/logs/desktop_pull.log 2>&1
$END
EOF
)

_current() { crontab -l 2>/dev/null || true; }
_without_block() { _current | awk -v b="$BEGIN" -v e="$END" 'BEGIN{s=1} $0==b{s=0} s{print} $0==e{s=1}'; }
# 標記區塊**之外**、卻指向本 repo 的條目＝前標記時代的遺留(首次安裝必遇)。
# 不自動吃掉:直接合併會產生重複兩份排程,靜默刪除又可能誤殺人手加的條目 → 一律要 --migrate 明示。
_orphans() { _without_block | grep -vE '^\s*#' | grep -F "$ROOT" || true; }
_without_orphans() { _without_block | grep -vF "$ROOT" ; }
_desired() { printf '%s\n%s\n' "$(_without_orphans | sed '/^$/d')" "$AUGUR_BLOCK"; }

case "${1:-}" in
  --selftest)
    ok=0
    chk() { if [ "$2" = "1" ]; then echo "  ✓ $1"; else echo "  ✗ $1"; ok=1; fi; }
    chk "區塊標記成對" "$([ -n "$BEGIN" ] && [ -n "$END" ] && echo 1 || echo 0)"
    chk "碰 ollama 之條目皆入單槽鎖(演化鏈+evolve_cycle)" \
        "$([ "$(printf '%s' "$AUGUR_BLOCK" | grep -c 'flock -n /tmp/augur_llm.lock')" -ge 2 ] && echo 1 || echo 0)"
    chk "evolve_cycle 不落在 01:15(避免撞 01:30 鏈)" \
        "$(printf '%s' "$AUGUR_BLOCK" | grep -q '^15 4,10,16,22' && echo 1 || echo 0)"
    chk "arena 每日雙條目(出單 20:00 平日+結算 21:30 平日,皆明示 --run)" \
        "$(printf '%s' "$AUGUR_BLOCK" | grep -q 'run_arena_daily_pipeline.py --run' \
           && printf '%s' "$AUGUR_BLOCK" | grep -q 'settle_arena_labels.py --run' && echo 1 || echo 0)"
    chk "oneshot 已退場(由每日條目取代,不殘留)" \
        "$(printf '%s' "$AUGUR_BLOCK" | grep -q 'arena_settle_oneshot' && echo 0 || echo 1)"
    chk "路徑不寫死 hugo(換機可攜)" \
        "$(printf '%s' "$AUGUR_BLOCK" | grep -qv '/home/hugo/project' && echo 1 || echo 0)"
    chk "無 % 未跳脫(cron 會截斷)" \
        "$(printf '%s' "$AUGUR_BLOCK" | grep -q '[^\\]%' && echo 0 || echo 1)"
    chk "移除邏輯保留他人條目(只剝標記區間)" \
        "$(declare -f _without_block | grep -q 'BEGIN{s=1}' && echo 1 || echo 0)"
    echo "自測:$([ $ok -eq 0 ] && echo '全通過 ✓' || echo '有失敗 ✗')"
    exit $ok ;;
  --dry-run)
    echo "── 將寫入之完整 crontab ──"; _desired; exit 0 ;;
  --uninstall)
    mkdir -p "$BAK_DIR"; _current > "$BAK_DIR/crontab.$(date +%Y%m%d%H%M%S).bak"
    _without_block | crontab -
    echo "✓ augur 區塊已移除(他人條目保留;備份在 $BAK_DIR)"; exit 0 ;;
  --apply|--migrate)
    n_orph=$(_orphans | grep -c . || true)
    if [ "${1:-}" = "--apply" ] && [ "$n_orph" -gt 0 ]; then
      echo "✗ 拒絕安裝:偵測到 $n_orph 條**標記外**指向本 repo 之舊條目,直接合併會變成重複排程。"
      _orphans | sed 's/^/    /'
      echo "  → 確認上列可被本腳本之 AUGUR_BLOCK 取代後,改跑:bash install_cron.sh --migrate"
      exit 3
    fi
    mkdir -p "$BAK_DIR" "$HOME/logs"; _current > "$BAK_DIR/crontab.$(date +%Y%m%d%H%M%S).bak"
    [ "$n_orph" -gt 0 ] && { echo "── --migrate:以下 $n_orph 條舊條目將由 AUGUR_BLOCK 取代(已備份) ──"; _orphans | sed 's/^/    /'; }
    _desired | crontab -
    echo "✓ augur 區塊已安裝/更新(備份在 $BAK_DIR)"
    echo "── 現行 augur 區塊 ──"; crontab -l | awk -v b="$BEGIN" -v e="$END" '$0==b{s=1} s{print} $0==e{s=0}'
    exit 0 ;;
  "")
    echo "── 現行 vs 期望(diff;空＝一致) ──"
    diff <(_current) <(_desired) && echo "  ✓ 一致,無須 --apply"
    exit 0 ;;
  *) awk '/^set -u/{exit} NR>1' "${BASH_SOURCE[0]}"; exit 2 ;;
esac
