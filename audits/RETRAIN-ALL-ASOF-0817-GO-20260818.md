---
status: go
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-18
viewpoint: 2026-08-18T08:00+08:00
asof: "2026-08-17"
shell: scripts/run_retrain_all_asof.sh
prior: audits/RETRAIN-ALL-ASOF-0814-H10-GO-20260816.md
paste: "方向臂改鎖可更新最新日＋重訓 H{5,10,20,40,60,90,120,240} 到最近日期"
self_reported: true
layer: "[I]"
---

# GO｜方向臂鎖最新日＋全量重訓＠2026-08-17

Steward：「做所有AI預測模型的方向臂改鎖在可更新的最新日期並重新訓練所有模型5天,10天,20天,40天,60天,90天,120天,240天到最近日期」。

同 08-16 句：RETRAIN-ALL 包；**不是** B3 出門；**不是** 改 standing。

## 准

- D＝`check_asof_ready --latest-date`＝**2026-08-17**（PriceAdj TAIEX 價頂）
- 方向臂鎖＝價頂（`asof_ready.resolve_lock`；≠ 完整性錨 2026-05-31）
- H 軌＝**H{5,10,20,40,60,90,120,240}**（交易日；H5 ≠ D 軌 k=5；H10 ≠ KH10）
- 昨夜 cron `run_retrain_all_asof_daily.sh --apply`＠21:40 已 COMPLETE＠08-17
- 本窗＝驗收包已齊；**不**再 `--no-resume` 重燒同 asof（會撞 09:20 cron 鎖）

## 禁

- `--asof 2026-08-18`／假 B3（價頂仍 08-17）
- promote／SERVE-SWAP／sim `--apply`／emit B3／開 NF／evaluate dgate
- 把分數／`p_beat`／`p_mkt`／`p_up` 當漲跌幅％
- 重掃 0812 NF；`--track other --apply`
