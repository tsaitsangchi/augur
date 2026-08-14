---
status: adopted
series: market_ops
track: RETRAIN-ALL
kind: standing_adopted
date: 2026-08-14
viewpoint: 2026-08-14T10:00+08:00
decision: RETRAIN-ALL-ASOF 包每日自動跑（鎖價頂；8×H{20,40,60,82,120}＋Daily*＋Mkt*＋DirStackM）
shell: scripts/run_retrain_all_asof_daily.sh
inner: scripts/run_retrain_all_asof.sh
cron_ssot: install_cron.sh
paste: "RETRAIN-ALL-ASOF-DAILY-CRON-ADOPTED | lock=價頂 | 8x5+Daily+Mkt+DirStackM | 21:40+09:20 | no-promote | no-emit-B3 | no-fake-B3 | skip-complete"
self_reported: true
layer: "[I]"
---

# ADOPTED｜RETRAIN-ALL-ASOF 日更 cron · 2026-08-14

Steward：「要這包每天自動跑」。

## 決策

1. **這包**＝方向臂鎖在可更新最新日（PriceAdj TAIEX 價頂）＋重訓截面 8 族 × H{20,40,60,82,120}＋Daily*／MktLogit／DirStackM。  
2. **上鐘**：平日 **21:40**（L0／結算後搶同日價）＋平日 **09:20**（隔晨補；FinMind 常次日才有收盤列）。  
3. D **不是**日曆今天、**不是** 2026-05-31。無價／假 B3／包已齊＠D → **SKIP exit 0**。  
4. 有價無 `feature_values` → 本驅動先 collect feat／core，再訓。  
5. **不** emit B3、**不** promote、**不** sim `--apply`、**不**開 NF。23:00 後拒開工（讓 TWEVO）。

## 落地

| 檔 | 變更 |
|---|---|
| `scripts/run_retrain_all_asof_daily.sh` | 日更驅動 |
| `install_cron.sh` | 兩條平日 cron＋告警標籤 |
| live crontab | `--apply` 與 SSOT 對齊 |

## 不做

- 不改 LIVE 冠軍／SERVE-SWAP  
- 不把 Daily* 塞進 L2 殼（L2 仍人／無 cron）  
- 不自動五窗 B3 出單（B3 standing 仍 H20／H60、禁默設 cron）
