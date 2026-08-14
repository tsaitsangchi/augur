---
status: executed
series: market_ops
track: L0-HOTPATH
phase: P2
date: 2026-08-14
viewpoint: 2026-08-14T09:36+08:00
D: "2026-08-14"
go: audits/L0-HOTPATH-APPLY-GO-20260814.md
fired: audits/L0-HOTPATH-APPLY-FIRED-20260814.md
plan: reports/augur_l0_hotpath_daily_plan_20260814.md
shell: scripts/run_l0_hotpath_daily.sh
log: /tmp/l0-hotpath-2026-08-14
paste: "L0-HOTPATH-APPLY-EXECUTED | D=2026-08-14 | RC=0 | PriceAdj=08-13 | no-fake-B3 | no-extended | no-cron | ≠B3 ≠L2"
self_reported: true
layer: "[I]"
---

# EXECUTED｜L0-HOTPATH · P2 真抓＠2026-08-14

`bash scripts/run_l0_hotpath_daily.sh --date 2026-08-14 --apply` · **RC=0** · 約 15 min  
黃帳 0（stale-guard 全 ok）。**未** `--extended` · **未** B3／L2 · **未** cron。

## 步

| 步 | RC | 結果 |
|---|---|---|
| bydate 核 A×14 | 0 | 183,401 列／各 2 筆（resume 08-13→end 08-14） |
| TRI dim-sync | 0 | 2 id（TAIEX／TPEx）；2 列 |
| macro | 0 | FRED 31 檔 |

## tip（誠實）

| 表 | max(date) | n＠08-14 |
|---|---|---|
| TaiwanStockPrice | **2026-08-13** | 0 |
| TaiwanStockPriceAdj TAIEX | **2026-08-13** | 0 |
| TaiwanStockInfo | 2026-08-14 | 3309 |
| TaiwanStockPER | 2026-08-13 | 0 |
| TaiwanStock10Year | 2026-08-13 | 0 |
| InstitutionalInvestorsBuySell | 2026-08-13 | 0 |
| MarginPurchaseShortSale | 2026-08-13 | 0 |
| Shareholding | 2026-08-13 | 0 |
| DailyShortSaleBalances | 2026-08-13 | 0 |
| SecuritiesLending | 2026-08-13 | 0 |
| GovernmentBankBuySell | 2026-08-13 | 0 |
| DayTrading | 2026-08-14 | 2059 |
| TotalInstitutionalInvestors | 2026-08-13 | 0 |
| TotalMarginPurchaseShortSale | 2026-08-13 | 0 |
| TRI TAIEX | **2026-08-13** | — |
| fred_series | 2026-08-13 | — |

**PriceAdj(TAIEX) 08-13 < D 08-14**：盤中／FinMind 尚無收盤價。殼已黃帳。**不開 B3**（假 B3）。

L1 綠燈仍是 `PriceAdj ≥ D`。本窗未亮。
