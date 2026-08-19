---
status: executed
series: s1s5_loop
track: HIST-ASOF
date: 2026-08-19
viewpoint: 2026-08-19T15:22+08:00
asof: "2026-08-11"
go: audits/HIST-ASOF-0811-GO-20260819.md
fired: audits/HIST-ASOF-0811-FIRED-20260819.md
log: /tmp/hist-asof-0811-apply/run.log
elapsed_ms: 537475
rc: 0
paste: "HIST-ASOF-apply | date=2026-08-11 | track=all | no-force-direction"
self_reported: true
layer: "[I]"
---

# EXECUTED｜歷史 as-of＠2026-08-11 · track=all

`bash scripts/run_asof_collect_train_verify.sh --date 2026-08-11 --apply --track all`  
**RC=0** · **~9.0 min**（15:13:37→15:22:35）· **force_dir=0** · **no-promote** · 未 emit B3 · 未 SERVE-SWAP。

## 截面

| 項 | 結果 |
|---|---|
| collect | SKIP（panel+core＠08-11 已在） |
| Rank 8×8 | **64／64**（resume **12**；新訓 **52**） |
| 方向臂 | SKIP Daily／Mkt／DirStackM |
| `pack_complete` | **True**（歷史 D 不要求方向臂） |
| 方向臂活鎖 | 仍＝價頂 **2026-08-18** |
| 已實現窗 | 無（08-11 之後僅 5 個交易日＜H5 的 6）→ **不跑** `--ic` |
| #14 | H20=`dead`；其餘 thin（未塗綠） |
| 庫內 pv＠08-11 | H20／H60 各 568＝舊出門列；**本殼未新寫** |

已齊近：07-31、08-07、**08-11**、08-12、08-13、08-14、08-17、08-18。

下一未齊（有 panel）：**08-10 缺 52**（**已有 H5 實現窗**）。補齊另貼 HIST-ASOF-apply。

*v1 重訓；誠實形；IC ≠ 報酬％ ≠ 升格。*
