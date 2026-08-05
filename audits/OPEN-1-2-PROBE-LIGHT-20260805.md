---
status: waiting
date: 2026-08-05
layer: "[I]"
bundle: "full_board_1_2_probe_light"
self_reported: true
---

# MONITOR｜全開項 1∥＋2 探針等 A · 2026-08-05

> Steward：`1,2` → AskQuestion **`probe_light`**（輕監看；再探針價；**不 sync**）。

## 1. 輕∥（#4／#8／#10／Adv）

| 探針 | LIVE |
|---|---|
| #4 sequence | selftest **全通過** |
| #4 graph | 13,021＠**2026-06-30** |
| #8 identity_claim | n=**0**；未 repair |
| #10 dgate | fail 12／approved 11／superseded 6 |
| Adv | Top5 改寫 OK；2330＠08-04；殼 **200** |

## 2. Ops-B 阻塞（等 A）

| 錨 | LIVE |
|---|---|
| calendar | **2026-08-05** |
| TAIEX／2330 | **2026-08-04** |
| fv／core／pp | **2026-08-04**（core n=283） |
| `ready_new_D` | **False** |
| `--date 2026-08-05 --dry-plan` | **RC=3** 價閘 SKIP |

**不跑**：FinMind／THAW sync、B3 真跑新 D、cron。

## 3. A 到位後（另觸）

確認 `PriceAdj TAIEX max ≥ D` 後：

```bash
bash scripts/run_daily_asof_predict.sh --dry-plan
bash scripts/run_daily_asof_predict.sh --date 2026-08-05
```

（日期以實際進庫日為準。）

交叉：`audits/OPS-B3-NEW-D-WAITING-20260805.md`。

*完。self-reported（#32a）。*

## re-probe 2026-08-05T20:03:10+08:00

TAIEX max 仍 **2026-08-04**；`D=08-05` dry-plan RC=3；輕監看穩定。
