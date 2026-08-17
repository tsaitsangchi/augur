---
status: executed
series: s4_s5_verify
track: V1-hist
date: 2026-08-17
viewpoint: 2026-08-17T13:50+08:00
asof: "2026-07-31"
go: audits/HIST-ASOF-0731-GO-20260817.md
fired: audits/HIST-ASOF-0731-FIRED-20260817.md
log: /home/hugo/.cursor/projects/home-hugo-project/terminals/947178.txt
elapsed_ms: 7728551
rc: 0
paste: "HIST-ASOF-apply | date=2026-07-31 | track=all | skip-sync | no-promote | yield-to-B3"
self_reported: true
layer: "[I]"
---

# EXECUTED｜歷史 as-of＠2026-07-31 · track=all

`bash scripts/run_asof_collect_train_verify.sh --date 2026-07-31 --apply --track all`  
**RC=0** · **~129 min** · skip-sync · **no-promote** · 未 emit 今日 B3 · 未 SERVE-SWAP。

## 截面（這才是本槍要的）

| 項 | 結果 |
|---|---|
| collect | SKIP（panel＠07-31 已在） |
| Rank 8×8 | **64／64**（4 Ridge 格 resume） |
| `prediction_values`＠07-31 | 僅 **H20 204** 列（track=all 本來不 emit standing B3） |
| #14 | H20=`dead`；其餘 H_TRACK=`thin_unestablished`（未塗綠） |

08-14 截面 64 格仍在（Rank `model_id` 含 as-of，兩天並存）。

## 副作用（方向臂單一 model_id）

Daily／Mkt／DirStackM 的 `ON CONFLICT` **會改 `asof_snapshot`**。本槍把活鎖從 **2026-08-14 → 2026-07-31**。

親查（訓後、復原前）：

| D | A 格 | Daily | Mkt | stack | 舊 pack 語意 |
|---|---|---|---|---|---|
| 07-31 | 64 | 3 | 2 | 1 | 齊 |
| 08-14 | 64 | 0 | 0 | 0 | 不齊 |

**不是** promote／SERVE-SWAP。Standing RankRidge emit＠08-14 仍吃 dated artifact。但任何走 `DailyLogit`／`MktLogit`／`DirStackM` 的路徑會吃到 07-31。

內殼 quirk：`build_market_direction_features --since 2026-08-01 --until 2026-07-31` 倒區間 → **0 列**；MktLogit 仍用庫內既有市場特徵訓到 07-31。

## 誠實 SKIP

SeqLSTM／classical TS／threelens／0812 NF 六族／P6 重 fit／promote。dgate preregister-all＝0 新 draft。未 evaluate dgate。

## 復原＋程式

- 復原：**EXECUTED** `audits/HIST-ASOF-0814-DIR-RESTORE-EXECUTED-20260817.md`（skip-rank＠08-14，RC=0，~139 min）。活鎖已回價頂。
- 殼：歷史 D≠價頂時 `--track all` 預設 `--skip-daily --skip-mkt --skip-stack`；`pack_complete` 在歷史 D 只看截面 8×8；mkt-feat 拒倒區間。

*v1 重訓；誠實形。*
