---
status: executed
series: daily_asof_ops
go: audits/DAILY-ASOF-B3-SHELL-GO-20260805.md
shell: audits/DAILY-ASOF-B3-SHELL-EXECUTED-20260805.md
phase: P2_live
self_reported: true
---

# EXECUTED｜B3 P2 LIVE · D=2026-08-04 · 2026-08-05

> **來源**：Steward 本機手跑 log（貼回對話）  
> **殼**：`scripts/run_daily_asof_predict.sh`  
> **self-reported（#32a）**

## 1. 跑次

| # | 指令 | 結果 |
|---|---|---|
| A | `--date 2026-08-04` | **B3 鏈完成**；accept OK |
| B | （無 `--date`，等同 TAIEX max＝08-04） | 再跑一輪相同；完成（連貼雙指令所致） |
| C | `--date 2026-08-04 --force-core` | core-incr 對照∅ PASS → 全鏈再完成 |

## 2. 共同錨

| 項 | 值 |
|---|---|
| D | **2026-08-04** |
| feat／core（A/B） | SKIP（已有） |
| core（C） | incremental 寫入 **283**；公式＝表＝283 |
| predict H20／H60 | 各 **283** 列；RC=0 |
| emit H20 | p∈[0.413,0.585]；econ=**dead** |
| emit H60 | p∈[0.373,0.626]；econ=**thin_unestablished** |
| accept | `2330` as_of＝**2026-08-04** |

## 3. 判讀

- B3 薄殼 **P2 真跑通過**（非 dry-plan）。  
- `--force-core` 路徑可用；本 D 上 core 已與公式一致（重刷為冪等）。  
- H20 `dead`／H60 `thin_unestablished`＝既有經濟標籤，**≠** 鏈失敗。

## 4. 操作提醒

勿把說明註解與第二條指令連貼；`<D>` 為佔位符。下交易日：

```bash
bash scripts/run_daily_asof_predict.sh --dry-plan
bash scripts/run_daily_asof_predict.sh --date YYYY-MM-DD
```

*完。*
