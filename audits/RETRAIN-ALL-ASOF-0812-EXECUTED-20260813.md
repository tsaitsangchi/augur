---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-13
viewpoint: 2026-08-13T14:35+08:00
asof: "2026-08-12"
shell: scripts/run_retrain_all_asof.sh
paste: "RETRAIN-ALL-0812 | 8x5 rank | Daily*/Mkt*/DirStackM | no-promote | no-fake-B3 | NF-pause"
self_reported: true
layer: "[I]"
---

# EXECUTED｜全部生產 AI 預測模型重訓到 as-of 2026-08-12

`bash scripts/run_retrain_all_asof.sh --date 2026-08-12 --apply`  
RC=0 · 約 59.6 min · skip-sync · **no-promote** · 08-13 假 B3 未跑。

## 截面 8×5

`model_registry`＠08-12：**40／40**（缺 0）。  
既有邊界 A 13 格 `--resume` 跳過；新訓 27 格（GBDT/XGB/Cat/RF/SVM/KNN/MLP 缺 H）。

## 方向臂（原停 05-31）

| model_id | asof_snapshot | 備註 |
|---|---|---|
| DailyLogit／DailyGBDT／DailyGBDT_cal | **2026-08-12** | v1 champion＝Logit（k=1 hit 0.5509；k=5 hit 0.5193）；v2 寫 3 673 389 列 |
| MktLogit／MktLogit_v2 | **2026-08-12** | 特徵面板頂仍 **08-07**（TRI TAIEX max＝08-07＜PriceAdj 08-12） |
| DirStackM | **2026-08-12** | 月頻特徵頂 08-07；H20 OOS 至 06-30（+20td 標籤未實現則略） |

DirStack v1 OOS 已重寫（H20 至 06-30）；**未**入 registry（舊契約）。

## 誠實 SKIP

SeqLSTM（評測不寫庫）／classical TS 煙測／threelens 冒煙／0812 NF 六族／P6 重 fit／SERVE-SWAP。

## 閘

- `check_asof_ready --date 2026-08-12` → ready  
- `--asof 2026-08-13` → rc=3 假 B3（Daily 自測已紅）  
- LIVE `prediction_probability` tip 仍 **08-12**（本輪未 emit）

程式：方向訓練／月頻 builder 改 `--asof`／`--until`；registry `ON CONFLICT` 改更新 asof；假 B3 共用 `asof_ready.refuse_if_fake_b3`。

*v1 重訓；誠實形。*
