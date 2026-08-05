---
status: waiting
date: 2026-08-05
layer: "[I]"
step: "ops_B3_new_D"
self_reported: true
---

# WAIT｜步驟 2 新 D B3 完整鏈 · 2026-08-05

> Steward：`probe_wait` —— 價未到位，**不跑 B**。

| 錨 | LIVE |
|---|---|
| DB calendar | **2026-08-05** |
| TAIEX／2330 PriceAdj max | **2026-08-04** |
| fv／core／pp H20 | **2026-08-04** |
| `--date 2026-08-05 --dry-plan` | **RC=3**（價閘整鏈 SKIP）｜符合設計 |

## 就緒條件

`PriceAdj TAIEX max(date) ≥ D`（`D`＝目標交易日，通常＝當日已收盤價）。

本殼 **不** sync；A 車道（arena／THAW／手跑 maintenance）另做。

## 到位後（手貼）

```bash
bash scripts/run_daily_asof_predict.sh --dry-plan
# 確認 D 與 need_feat／need_core 後：
bash scripts/run_daily_asof_predict.sh --date YYYY-MM-DD
```

*完。等候中。*
