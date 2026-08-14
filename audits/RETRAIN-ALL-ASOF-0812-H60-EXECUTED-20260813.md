---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-13
viewpoint: 2026-08-13T17:00+08:00
asof: "2026-08-12"
shell: scripts/run_retrain_all_asof.sh
paste: "DIRLOCK-latest | H60-open | RETRAIN-ALL-0812 --no-resume | monthly-RankRidge-fix | no-promote | no-evaluate | no-fake-B3"
self_reported: true
layer: "[I]"
---

# EXECUTED｜方向臂另開 H60＋強制重訓＠2026-08-12

`bash scripts/run_retrain_all_asof.sh --date 2026-08-12 --apply --no-resume`  
首輪 RC=1（`stack-monthly` 全史重建撞 H20 RankRidge+RankSVM 重鍵）→ 改月頻只取 **RankRidge** → 補跑月頻＋DirStackM。  
**no-promote** · **不 evaluate** · **不 approve** `dgate_H_60`。

## 鎖

未指定 `--asof`／`--until` → PriceAdj TAIEX 價頂。探針＝**2026-08-12**。08-13＝假 B3。

## 方向 H60（新開）

| 層 | 結果 |
|---|---|
| MktLogit／MktLogit_v2 | H60 各 **4114** 列 P_mkt（2009-08-04→2026-05-13）；基率 p̄=0.714 |
| DirStack | H60 OOS **27745** 列（2018-12-31→2026-04-30） |
| 月頻 `rank_pctile_h60` | **40858** 列（2017-01-24→2026-05-29） |
| DirStackM | H60 OOS **24498** 列（2019-07-31→2026-04-30）；p̄=0.548 |
| `dgate_H_60` | **preregistered** draft；未核准 |

**不**併入 v2 K=4／arena／threelens／combo。

## 截面＋其餘方向臂

| 臂 | 結果 |
|---|---|
| 截面 8×5 | **40／40** 全重訓（resume=0） |
| 其中 H20／H40／H60 | **24／24** |
| DailyLogit／DailyGBDT／DailyGBDT_cal | asof＝08-12；v1 champion＝Logit |
| Mkt／DirStack／DirStackM | asof＝08-12；H 軌現為 **20／40／60／82／120** |

LIVE tip 未 SERVE-SWAP。P6 未重 fit。

## 誠實 SKIP

SeqLSTM／classical TS／threelens／0812 NF 六族／P6 重 fit／promote／evaluate／approve。

*v1 另開 H60＋強制重訓；誠實形。*
