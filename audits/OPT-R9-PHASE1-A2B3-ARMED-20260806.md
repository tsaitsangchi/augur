---
status: armed
series: opt_r9
phase: "1"
date: 2026-08-06
D: "2026-08-06"
viewpoint: 2026-08-06T08:30+08:00
self_reported: true
---

# ARMED｜計畫 r9 Phase 1 · A→自動 B3＠2026-08-06

> Steward 確認：「下一事件：Phase 1＝價到 08-06 → 自動 B3」。  
> 沿用既有 `arm_auto_b3`（非新掛第二支）。

## 閘

| 項 | 值 |
|---|---|
| 觸發 | `PriceAdj 2330 max ≥ 2026-08-06` |
| 動作 | `bash scripts/run_daily_asof_predict.sh --date 2026-08-06` |
| 截止 | **23:50+08** → TIMEOUT 帳、**不**假跑 B3 |
| 輪詢 | 20 min |
| log | `/tmp/asof-ping-0806/watch.log` |
| watcher | bash ≈**2298526**（LIVE 首查／08:14 皆 WAIT） |
| 現價頂 | **2026-08-05** |

## 護欄

`FZ/GATE-keep | skip-sync-B | no-SIM-apply | no-cron` · standing 日更 H20＋H60。

## 驗收（就緒後）

RC=0；fv／core／pp 頂＝08-06；Adv as_of＝08-06；寫 `DAILY-ASOF-B3-*-EXECUTED`（或 FAIL）。

*候 WAKE。*
