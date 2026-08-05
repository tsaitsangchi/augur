---
status: monitor
date: 2026-08-05
layer: "[I]"
bundle: "open_step_1_light_parallel"
self_reported: true
---

# MONITOR｜開問題步驟 1（輕∥）· 2026-08-05

> Steward 選執行序 **「1」**：#4／#8／#10／Adv 抽測；Ops 等下交易日。

| 探針 | LIVE |
|---|---|
| Ops 熱路徑 | TAIEX／fv／core／pp(H20,60) 皆 **2026-08-04**；core n=**283** |
| DB calendar | **2026-08-05**（價尚未新 D → **等收盤／A 車道**） |
| #4 sequence | selftest **全通過** |
| #4 graph | 13,021＠**2026-06-30**（與日更錯位＝仍開、非本日修） |
| #8 | `identity_claim` n=0；未 `repair_priceadj` |
| #10 dgate | fail 12／approved 11／superseded 6 |
| Adv | Top5 改寫 OK；2330 as_of＝08-04；`:8399`/`:8090`=200 |

## 下交易日（步驟 2，本日不做）

```bash
bash scripts/run_daily_asof_predict.sh --dry-plan
bash scripts/run_daily_asof_predict.sh --date YYYY-MM-DD
```

（須 `PriceAdj TAIEX max ≥ D`；本殼不 sync。）

*完。self-reported（#32a）。*
