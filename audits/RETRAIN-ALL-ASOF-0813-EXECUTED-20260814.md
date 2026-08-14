---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-14
viewpoint: 2026-08-14T11:15+08:00
asof: "2026-08-13"
go: audits/RETRAIN-ALL-ASOF-0813-GO-20260814.md
fired: audits/RETRAIN-ALL-ASOF-0813-FIRED-20260814.md
shell: scripts/run_retrain_all_asof_daily.sh
log: /tmp/retrain-all-asof-2026-08-13/driver.log
paste: "RETRAIN-ALL-0813-EXECUTED | D=2026-08-13 | 40/40 | Daily+Mkt+DirStackM | resume=13 | no-promote | no-emit | no-fake-B3@08-14"
self_reported: true
layer: "[I]"
---

# EXECUTED｜全模型重訓到可更新最新日＠2026-08-13

`bash scripts/run_retrain_all_asof_daily.sh --apply` · **RC=0**  
鎖＝PriceAdj TAIEX 價頂 **2026-08-13**（08-14 仍無收盤列＝假 B3，未跑）。  
resume＝1 · **no-promote** · **未 emit**。

開火前覆蓋：rank 13/40、daily 0/3、mkt 0/2、stack 0/1。  
完成後覆蓋：**COMPLETE rank=40/40 daily=3/3 mkt=2/2 stack=1/1**。

## 截面 8×5

13 格 `--resume` 跳過（L2＠08-13 已有）。新訓 27 格。缺 0。

## 方向臂 asof＝08-13

| model_id | 結果 |
|---|---|
| DailyLogit／DailyGBDT | v1 champion＝Logit（k=1 hit 0.5509；k=5 hit 0.5194） |
| DailyGBDT_cal | v2 寫 3 674 238 列 |
| MktLogit／MktLogit_v2 | H{20,40,60,82,120} P_mkt 全寫 |
| DirStack | 五窗合成完成（v1 仍不入 registry） |
| DirStackM | asof＝08-13；月頻至 08-13 |

## 誠實 SKIP

SeqLSTM／classical TS／threelens／0812 NF 六族／P6 重 fit／promote／emit B3／`--asof 2026-08-14`。  
未 evaluate／approve `dgate_H_60`。

今晚 21:40 cron 見包已齊＠08-13 會 SKIP，直到價頂前進。
