---
status: executed
series: s4_s5_verify
track: incident-restore
date: 2026-08-17
viewpoint: 2026-08-17T16:15+08:00
asof: "2026-08-14"
go: audits/HIST-ASOF-0814-DIR-RESTORE-GO-20260817.md
fired: audits/HIST-ASOF-0814-DIR-RESTORE-FIRED-20260817.md
logdir: /tmp/dir-restore-0814-20260817
elapsed_ms: 8327112
rc: 0
parent: audits/HIST-ASOF-0731-EXECUTED-20260817.md
paste: "HIST-ASOF-apply | date=2026-07-31 | track=all | skip-sync | no-promote | yield-to-B3"
self_reported: true
layer: "[I]"
---

# EXECUTED｜方向臂鎖拉回價頂 2026-08-14

`bash scripts/run_retrain_all_asof.sh --date 2026-08-14 --apply --skip-rank --logdir /tmp/dir-restore-0814-20260817`  
**RC=0** · **~139 min** · skip-sync · **no-promote** · 截面 8×8 **SKIP**（未刷）。

## 親查

| D | A 格 | Daily | Mkt | stack | pack_complete |
|---|---|---|---|---|---|
| 07-31 | 64 | 0 | 0 | 0 | True（歷史 D 只看截面） |
| 08-14 | 64 | 3 | 2 | 1 | True（價頂全包） |

DailyLogit／DailyGBDT／DailyGBDT_cal／MktLogit／MktLogit_v2／DirStackM 的 `asof_snapshot` 全＝**2026-08-14**。

mkt-feat：`--since 2026-08-01 --until 2026-08-14` → **191 列**（非倒區間）。

## 誠實 SKIP

Rank 8×8／SeqLSTM／classical TS／threelens／0812 NF／P6／promote。未 emit B3。未 evaluate dgate。
