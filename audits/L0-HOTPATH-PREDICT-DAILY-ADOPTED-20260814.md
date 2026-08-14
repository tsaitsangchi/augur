---
status: adopted
series: market_ops
track: L0-HOTPATH
kind: standing_adopted
date: 2026-08-14
viewpoint: 2026-08-14T09:50+08:00
decision: 預測日更 L0＝核 A＋TRI（既有 20:00 arena 第①步改呼叫熱路徑殼）
plan: reports/augur_l0_hotpath_daily_plan_20260814.md
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
shell: scripts/run_l0_hotpath_daily.sh
arena: scripts/run_arena_daily_pipeline.py
paste: "L0-HOTPATH-PREDICT-DAILY-ADOPTED | 核A+TRI | arena①=hotpath | no-93 | no-AUGUR_DIM_SYNC | no-new-cron | ≠B3 ≠L2 | no-fake-B3@08-14"
self_reported: true
layer: "[I]"
---

# ADOPTED｜預測日更走核 A＋TRI · 2026-08-14

Steward：「預測日更請走核 A＋TRI」。

## 決策

1. **預測心跳的 L0**＝核 A 14 張台灣日頻 ＋ TRI 窄窗 dim-sync（只 TAIEX／TPEx）＋熱路徑內既有 FRED（`sync_macro --no-catalog`）。  
2. **不是** `daily_datasets()` 93 表；**不是** `--extended`；**不是** `AUGUR_DIM_SYNC=1`（其餘 5 張 dim 表仍關）。  
3. 落地＝改**既有**平日 20:00 `run_arena_daily_pipeline.py --run` 的第①步：改呼叫 `bash scripts/run_l0_hotpath_daily.sh --date D --apply`。  
4. **不**新增 crontab 條；**不** `install_cron.sh --apply`（時鐘仍是同一條 20:00）。  
5. **不**因此開 B3＠08-14（PriceAdj TAIEX 仍 08-13；FinMind 當日收盤列未到）。L1／L2 仍人／watcher。

## 落地（本輪）

| 檔 | 變更 |
|---|---|
| `scripts/run_arena_daily_pipeline.py` | `_steps` ①＝熱路徑殼；`AUGUR_DIM_SYNC=1` 改警告並忽略 |
| `install_cron.sh` | 只改 arena 行註解；**cron 字面不變** |
| r16 L0 列／L0 計畫 §2／§6 | 預測日更 standing＝核 A＋TRI |
| 本檔 | 採納帳 |

## 驗收

- [x] `--dry-run --date 2026-08-14` 第①步含 `run_l0_hotpath_daily.sh --date 2026-08-14 --apply`
- [x] 同 dry-run **不含** 無 `--datasets` 的 `daily_maintenance.py --end D`
- [x] `AUGUR_DIM_SYNC=1` dry-run 印忽略警告，步驟仍是熱路徑
- [x] `--skip-sync` 仍跳過①
- [ ] 今晚 20:00 實跑帳（另 EXECUTED；本採納不預塗綠）

## 不做

- 不開 93 表／EuropeStockInfo 2019 回填  
- 不裝新 timer、不 P3 watcher  
- 不 `--extended`、不假 B3、不 promote、不 sim `--apply`
