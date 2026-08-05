---
status: price_ready
series: daily_asof_ops
go: audits/A-THAW-PRICE-ONLY-GO-20260805.md
date: 2026-08-05
viewpoint: "2026-08-05T23:31+08:00"
self_reported: true
---

# READY｜A 價到位（監看帳）· 2026-08-05

> **監看** `watch_exit`：≈23:31 偵測 **READY**（maint 仍可能續跑其他表）。

| 錨 | LIVE |
|---|---|
| TAIEX Price／PriceAdj max | **2026-08-05** |
| Price＠08-05／PriceAdj＠08-05 | **42074**／**2807** 列 |
| fv／core max | 仍 **2026-08-04**（B 尚未跑） |
| B3 `--date 2026-08-05 --dry-plan` | **GATE_RC=0**；need_feat=1 need_core=1 |
| arena maint | 仍可能在跑（全日頻掃；不阻 B） |

## 下一步

```bash
bash scripts/run_daily_asof_predict.sh --date 2026-08-05 --dry-plan
bash scripts/run_daily_asof_predict.sh --date 2026-08-05
```

*價門已開；出單鏈另觸。*
