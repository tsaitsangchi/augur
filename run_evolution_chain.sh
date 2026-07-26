#!/usr/bin/env bash
# 🎯 演化標準作業鏈一鍵編排(hugo 2026-07-25 常備指令;全本地零 Claude token)。
# 鏈序(七段、齒輪同輪咬合):首遍收割 → 自我求知 → **第二遍收割(消費本輪新 query)** → 演化迴圈
#      → 第二次求知(為明日備料) → 現況摘要。2026-07-26 由五段改七段:原設計求知在收割之後,
#      新 query 得等 24h 才被消費=每跳一步慢一天;第二遍收割使「發現缺口→抓回文獻→變教材」在單輪內閉合。flock 防重疊;各步失敗不斷鏈(獨立 log 誠實記錄);晉升永遠人閘。
# 執行指令矩陣:
#   bash run_evolution_chain.sh              # 跑完整鏈(cron 與手動同路)
#   bash run_evolution_chain.sh --no-harvest # 跳過收割段(只教材+pack;離線/省 API)
# 用法:cron 每晚 01:30 自動;hugo 隨時可手動跑;待簽=python3 scripts/evolve_cycle.py(無參數)看 candidate。
set -u
cd /home/hugo/project/augur || exit 1
LOG=/home/hugo/logs/evolution_chain.log
LOCK=/tmp/evolution_chain.lock
exec 9>"$LOCK"
flock -n 9 || { echo "$(date '+%F %T') 另一條鏈在跑,略過" >> "$LOG"; exit 0; }
{
  echo "═══ $(date '+%F %T') 演化鏈開始 ═══"
  if [[ "${1:-}" != "--no-harvest" ]]; then
    if pgrep -f "harvest_knowledge.py" > /dev/null; then
      echo "── 收割段:偵測到收割進程已在跑,本輪跳過收割、直接消化 ──"
    else
      echo "── 1/5 通用收割批 ──"
      venv/bin/python scripts/harvest_knowledge.py --batch 200 --rounds 2 --max-minutes 60
      echo "── 2/5 quant_finance 圈域 ──"
      venv/bin/python scripts/harvest_knowledge.py --domain quant_finance --batch 100 --max-minutes 20
      echo "── 3/5 software_engineering 圈域 ──"
      venv/bin/python scripts/harvest_knowledge.py --domain software_engineering --batch 100 --max-minutes 20
    fi
  fi
  echo "── 4/7 自我求知(缺口→query) ──"
  venv/bin/python scripts/evolve_self_seek.py --seek
  # 齒輪咬合(2026-07-26 hugo:「求知的齒輪轉了,收割的齒輪沒跟上」)——求知產出之 query 必須在
  # **同一輪內**被收割消費,否則要等 24h 下一輪=每跳一步慢一天。第二遍收割即為此。
  if [[ "${1:-}" != "--no-harvest" ]] && ! pgrep -f "[h]arvest_knowledge.py" > /dev/null; then
    echo "── 5/7 第二遍收割(消費本輪自我求知之新 query) ──"
    venv/bin/python scripts/harvest_knowledge.py --domain quant_finance --batch 120 --max-minutes 25
    venv/bin/python scripts/harvest_knowledge.py --domain software_engineering --batch 120 --max-minutes 25
  else
    echo "── 5/7 第二遍收割:跳過(--no-harvest 或收割進程在跑) ──"
  fi
  echo "── 6/7 演化迴圈(三源教材→pack→eval;含第二遍收割之新文獻) ──"
  venv/bin/python scripts/evolve_cycle.py --cycle
  echo "── 7/7 第二次求知(用最新文獻找下一輪缺口,供明日首遍收割) ──"
  venv/bin/python scripts/evolve_self_seek.py --seek
  echo "── 待簽現況(晉升唯 hugo 人簽) ──"
  venv/bin/python scripts/evolve_cycle.py 2>/dev/null | grep -E "version|gold\[" | head -8
  echo "═══ $(date '+%F %T') 演化鏈結束 ═══"
} >> "$LOG" 2>&1
