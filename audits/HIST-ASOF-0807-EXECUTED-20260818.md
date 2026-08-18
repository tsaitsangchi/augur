---
status: executed
series: s1s5_loop
track: HIST-ASOF
date: 2026-08-18
viewpoint: 2026-08-18T10:49+08:00
asof: "2026-08-07"
go: audits/HIST-ASOF-0807-GO-20260818.md
fired: audits/HIST-ASOF-0807-FIRED-20260818.md
log: /tmp/hist-asof-0807-apply/run.log
elapsed_ms: 567739
rc: 0
paste: "HIST-ASOF-apply | date=2026-08-07 | track=all | no-force-direction | no-promote"
self_reported: true
layer: "[I]"
---

# EXECUTED｜歷史 as-of＠2026-08-07 · track=all

`bash scripts/run_asof_collect_train_verify.sh --date 2026-08-07 --apply --track all`  
**RC=0** · **~9.5 min** · **force_dir=0** · **no-promote** · 未 emit B3 · 未 SERVE-SWAP。

## 截面（這才是本槍要的）

| 項 | 結果 |
|---|---|
| collect | SKIP（panel＠08-07 已在） |
| Rank 8×8 | **64／64**（resume 既有 12 格；新訓 52） |
| 方向臂 | SKIP Daily／Mkt／DirStackM（歷史 D≠價頂） |
| `pack_complete` | **True**（歷史 D 只看截面） |
| 方向臂活鎖 | 仍＝價頂 **2026-08-17**（未往回搬） |
| `prediction_values`＠08-07 | H20／H40／H60／H120 舊列；本殼未 emit 今日 B3 |
| #14 | H20=`dead`；其餘 H_TRACK=`thin_unestablished`（未塗綠） |

已齊日： **07-31、08-07、08-14、08-17**。

## 同日 stamp IC（不採、不升格）

`--ic`＠08-07 吃到剛訓的 `*_2026-08-07_*`＝**同日 stamp**。RankKNN H5 IC＝**0.9992**＝07-31 那支 1.0 同一陷阱。GBDT／XGB／RF 0.29–0.34 亦同日，**不是** OOS。

誠實 OOS 仍＝先前 V1：07-31 模型 × 08-07 H5 panel，八族 IC 近 0（最高 KNN 0.0184）。

JSON：`/tmp/v1-asof-2026-08-07-post-apply.json`（覆蓋前的 OOS JSON 已在 `audits/HIST-ASOF-V1-IC-EXECUTED-20260818.md`）。

## 誠實 SKIP

SeqLSTM／classical TS／threelens／0812 NF 六族／P6 重 fit／promote。未 `--force-direction`。未 evaluate dgate。

下一未齊（有 panel）：**08-13 缺 8**（無已實現窗）。補齊另貼 HIST-ASOF-apply。

*v1 重訓；誠實形。*
