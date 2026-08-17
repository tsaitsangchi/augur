---
status: go
series: s4_s5_verify
track: incident-restore
date: 2026-08-17
viewpoint: 2026-08-17T13:50+08:00
asof: "2026-08-14"
parent: audits/HIST-ASOF-0731-EXECUTED-20260817.md
paste: "HIST-ASOF-apply | date=2026-07-31 | track=all | skip-sync | no-promote | yield-to-B3"
self_reported: true
layer: "[I]"
---

# GO｜方向臂鎖拉回價頂 2026-08-14（事故復原）

HIST-ASOF＠07-31 `track=all` 覆寫了 Daily／Mkt／DirStackM 活鎖。價頂仍 **08-14**（08-15／16／17 假 B3）。yield-to-B3＝活鎖必須在價頂，不是停在七月。

## 准

- `bash scripts/run_retrain_all_asof.sh --date 2026-08-14 --apply --skip-rank --logdir /tmp/dir-restore-0814-20260817`
- skip-sync · no-promote · 不 `--force` 刷截面 8×8

## 禁

- `--date 2026-08-15/16/17`
- SERVE-SWAP／sim-apply／開 NF／evaluate dgate
- 與進行中 B3 搶槽
