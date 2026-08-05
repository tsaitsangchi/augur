---
status: adopted
series: s5_daily_ops
depends_on:
  - reports/augur_post_close_daily_asof_ops_design_20260805.md
  - reports/augur_daily_asof_predict_emit_runbook_20260805.md
---

# ADOPTED｜POST-CLOSE-DAILY-ASOF standing GO

> **授權**：Steward AskQuestion `ops_cut` → **`adopt_standing`**（2026-08-05）  
> paste（可重用，不需每日再 Ask）：

```
POST-CLOSE-DAILY-ASOF-standing-go | FZ/GATE-keep | API-THAW-bounded-A | skip-sync-B | no-SIM-apply
# 範圍: 交易日 D=庫內 TAIEX max(date)
# 每日 B: feat(D) → core B1 incremental@D → predict H20+H60 → emit H20+H60
# 編排: bash scripts/run_daily_asof_predict.sh --date D   （B3；非 cron）
# 不含: P6 --fit／OOS 全量、NF-pause 解凍、β5 resume、Dividend／dim-sync
# 失敗: PriceAdj < D → 跳過 B 並告警；任一 RC≠0 → 停後續步
```

## 生效範圍

| 允 | 禁（另句） |
|---|---|
| 交易日收盤後、庫內 `PriceAdj≥D` 時執行 **B 車道**（見 runbook） | 掛 systemd timer／改 `install_cron.sh` |
| A 車道 THAW-bounded（可復用 arena 約 20:00 sync） | FinMind／Dividend／dim-sync 放量 |
| H20＋H60 predict＋emit | 默認日跑 P6 `--fit`／OOS 全量 |
| 手觸發或半自動編排（顯式 `D`） | 撤 NF-pause／β5；sim `--apply` |

## 驗收（每跑一輪）

- `build_single_ticker_rel_payload("2330", 20).as_of == D`
- EXEC／日誌記 `D`、RC、calibrator id；失敗即停

*self-reported（#32a）。未授權自動 cron。*
