---
status: executed
series: s1s5_loop
track: HIST-ASOF
date: 2026-08-18
viewpoint: 2026-08-18T11:20+08:00
asof: "2026-08-13"
go: audits/HIST-ASOF-0813-GO-20260818.md
fired: audits/HIST-ASOF-0813-FIRED-20260818.md
log: /tmp/hist-asof-0813-apply/run.log
elapsed_ms: 201269
rc: 0
paste: "HIST-ASOF-apply | date=2026-08-13 | track=all | no-force-direction | no-promote"
self_reported: true
layer: "[I]"
---

# EXECUTED｜歷史 as-of＠2026-08-13 · track=all

`bash scripts/run_asof_collect_train_verify.sh --date 2026-08-13 --apply --track all`  
**RC=0** · **~3.4 min** · **force_dir=0** · **no-promote** · 未 emit B3 · 未 SERVE-SWAP。

## 截面

| 項 | 結果 |
|---|---|
| collect | SKIP（panel＠08-13 已在） |
| Rank 8×8 | **64／64**（resume 56；新訓 **8×H10**） |
| 方向臂 | SKIP Daily／Mkt／DirStackM |
| `pack_complete` | **True** |
| 方向臂活鎖 | 仍＝價頂 **2026-08-17** |
| 已實現窗 | 無（價頂 08-17 不夠 H5）→ 不跑 `--ic` |
| #14 | H20=`dead`；其餘 thin（未塗綠） |

已齊日：07-31、08-07、**08-13**、08-14、08-17。

下一未齊（有 panel）：**08-12 缺 32**（無已實現窗）。

*v1 重訓；誠實形。*
