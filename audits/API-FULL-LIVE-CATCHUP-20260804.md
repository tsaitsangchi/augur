# API FULL LIVE CATCHUP [I]（2026-08-04）

> **位階**：[I] 工具／接續記憶  
> **授權**：Steward「全線資料補抓」— live 增量宇宙日維 + FRED `--no-catalog`  
> **前置佇列**：等 MC asof 重算、日頻 API-CATCHUP、Dividend→dim-sync→缺口窄窗 清場後執行（**未插隊**）

## 0. 閘門清場

```
[2026-08-04T09:05:14+08:00] pulse elapsed=241s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:07:14+08:00] pulse elapsed=361s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:09:14+08:00] pulse elapsed=481s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:11:14+08:00] pulse elapsed=601s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:13:14+08:00] pulse elapsed=721s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:15:14+08:00] pulse elapsed=841s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:17:14+08:00] pulse elapsed=961s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=3
[2026-08-04T09:19:14+08:00] pulse elapsed=1081s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:21:14+08:00] pulse elapsed=1201s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:23:14+08:00] pulse elapsed=1321s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:25:14+08:00] pulse elapsed=1441s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=4
[2026-08-04T09:27:14+08:00] pulse elapsed=1561s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=7
[2026-08-04T09:29:14+08:00] pulse elapsed=1681s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:31:14+08:00] pulse elapsed=1801s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:33:14+08:00] pulse elapsed=1921s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:35:15+08:00] pulse elapsed=2041s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:37:15+08:00] pulse elapsed=2162s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:39:15+08:00] pulse elapsed=2282s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:41:15+08:00] pulse elapsed=2402s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:43:15+08:00] pulse elapsed=2522s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:45:15+08:00] pulse elapsed=2642s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:47:15+08:00] pulse elapsed=2762s MC=1 CATCH=1 DIV=0 orch=1 heavy_procs=9
[2026-08-04T09:49:15+08:00] pulse elapsed=2882s MC=1 CATCH=1 DIV=1 orch=0
0 heavy_procs=5
[2026-08-04T09:49:15+08:00] GATES_CLEAR
[2026-08-04T09:49:15+08:00] LAUNCH_FULL_LIVE
[2026-08-04T09:49:45+08:00] DM_START --end 2026-08-03 (default all daily / live by-date; NO --full-universe)
[2026-08-04T13:15:18+08:00] DM_END rc=0
[2026-08-04T13:15:18+08:00] MACRO_START sync_macro --no-catalog
[2026-08-04T13:15:54+08:00] MACRO_END rc=0
```

- wait log: `/tmp/augur_logs/api_full_live_wait_20260804.log`

## 1. 指令與 rc

| 步 | 指令 | rc | log |
|---|---|---|---|
| FinMind 日維 | `daily_maintenance.py --end 2026-08-03`（預設全日頻 by-date；**無** `--full-universe`；**無** Dividend rebuild） | 0 | `/tmp/augur_logs/api_full_live_dm_20260804.log` |
| FRED | `sync_macro.py --no-catalog` | 0 | `/tmp/augur_logs/api_full_live_macro_20260804.log` |

## 2. 前後 max(date)

### BEFORE
```
BEFORE max(date) @ 2026-08-04T09:49:15.491276+08:00
TaiwanStockPriceAdj: 2026-08-03
TaiwanStockPrice: 2026-08-03
TaiwanStockMarginPurchaseShortSale: 2026-08-03
TaiwanStockInstitutionalInvestorsBuySell: 2026-08-03
TaiwanStockPER: 2026-08-03
TaiwanStockDayTrading: 2026-08-03
TaiwanStockTotalReturnIndex: 2026-07-31
TaiwanStockDividend: 2026-10-12
fred_series overall max(date): 2026-08-03

```

### AFTER
```
AFTER max(date) @ 2026-08-04T13:15:54.855721+08:00
TaiwanStockPriceAdj: 2026-08-03
TaiwanStockPrice: 2026-08-03
TaiwanStockMarginPurchaseShortSale: 2026-08-03
TaiwanStockInstitutionalInvestorsBuySell: 2026-08-03
TaiwanStockPER: 2026-08-03
TaiwanStockDayTrading: 2026-08-04
TaiwanStockTotalReturnIndex: 2026-07-31
TaiwanStockDividend: 2026-10-12
fred_series overall max(date): 2026-08-03

```

## 3. 停手訊號（#24）

### DM tail
```
  UKStockInfo by-date 2019-09-11: 1 交易日 / 24339 列 / 160 筆
  UKStockInfo by-date 2019-10-09: 1 交易日 / 24339 列 / 180 筆
  UKStockInfo by-date 2019-11-06: 1 交易日 / 24339 列 / 200 筆
  UKStockInfo by-date 2019-12-04: 1 交易日 / 24339 列 / 220 筆
  UKStockInfo by-date 2020-01-01: 1 交易日 / 24339 列 / 240 筆
  UKStockInfo by-date 2020-01-29: 1 交易日 / 24339 列 / 260 筆
  UKStockInfo by-date 2020-02-26: 1 交易日 / 24339 列 / 280 筆
  UKStockInfo by-date 2020-03-25: 1 交易日 / 24339 列 / 300 筆
  UKStockInfo by-date 2020-04-22: 1 交易日 / 24339 列 / 320 筆
  UKStockInfo by-date 2020-05-20: 1 交易日 / 24339 列 / 340 筆
  UKStockInfo by-date 2020-06-17: 1 交易日 / 24339 列 / 360 筆
  UKStockInfo by-date 2020-07-15: 1 交易日 / 24339 列 / 380 筆
  UKStockInfo by-date 2020-08-12: 1 交易日 / 24339 列 / 400 筆
  UKStockInfo by-date 2020-09-09: 1 交易日 / 24339 列 / 420 筆
  UKStockInfo by-date 2020-10-07: 1 交易日 / 24339 列 / 440 筆
  UKStockInfo by-date 2020-11-04: 1 交易日 / 24339 列 / 460 筆
  UKStockInfo by-date 2020-12-02: 1 交易日 / 24339 列 / 480 筆
  UKStockInfo by-date 2020-12-30: 1 交易日 / 24339 列 / 500 筆
  UKStockInfo by-date 2021-01-27: 1 交易日 / 24339 列 / 520 筆
  UKStockInfo by-date 2021-02-24: 1 交易日 / 24339 列 / 540 筆
  UKStockInfo by-date 2021-03-24: 1 交易日 / 24339 列 / 560 筆
  UKStockInfo by-date 2021-04-21: 1 交易日 / 24339 列 / 580 筆
  UKStockInfo by-date 2021-05-19: 1 交易日 / 24339 列 / 600 筆
  UKStockInfo by-date 2021-06-16: 1 交易日 / 24339 列 / 620 筆
  UKStockInfo by-date 2021-07-14: 1 交易日 / 24339 列 / 640 筆
  UKStockInfo by-date 2021-08-11: 1 交易日 / 24339 列 / 660 筆
  UKStockInfo by-date 2021-09-08: 1 交易日 / 24339 列 / 680 筆
  UKStockInfo by-date 2021-10-06: 1 交易日 / 24339 列 / 700 筆
  UKStockInfo by-date 2021-11-03: 1 交易日 / 24339 列 / 720 筆
  UKStockInfo by-date 2021-12-01: 1 交易日 / 24339 列 / 740 筆
  UKStockInfo by-date 2021-12-29: 1 交易日 / 24339 列 / 760 筆
[finmind] 額度 5972/6000 ≥ 5800 → 主動暫停(每 150s 檢錶,≤2900 續)
[finmind] 額度退到 2685 → 續抓
  UKStockInfo by-date 2022-01-26: 1 交易日 / 24339 列 / 780 筆
  UKStockInfo by-date 2022-02-23: 1 交易日 / 24339 列 / 800 筆
  UKStockInfo by-date 2022-03-23: 1 交易日 / 24339 列 / 820 筆
  UKStockInfo by-date 2022-04-20: 1 交易日 / 24339 列 / 840 筆
  UKStockInfo by-date 2022-05-18: 1 交易日 / 24339 列 / 860 筆
  UKStockInfo by-date 2022-06-15: 1 交易日 / 24339 列 / 880 筆
  UKStockInfo by-date 2022-07-13: 1 交易日 / 24339 列 / 900 筆
  UKStockInfo by-date 2022-08-10: 1 交易日 / 24339 列 / 920 筆
  UKStockInfo by-date 2022-09-07: 1 交易日 / 24339 列 / 940 筆
  UKStockInfo by-date 2022-10-05: 1 交易日 / 24339 列 / 960 筆
  UKStockInfo by-date 2022-11-02: 1 交易日 / 24339 列 / 980 筆
  UKStockInfo by-date 2022-11-30: 1 交易日 / 24339 列 / 1000 筆
  UKStockInfo by-date 2022-12-28: 1 交易日 / 24339 列 / 1020 筆
  UKStockInfo by-date 2023-01-25: 1 交易日 / 24339 列 / 1040 筆
  UKStockInfo by-date 2023-02-22: 1 交易日 / 24339 列 / 1060 筆
  UKStockInfo by-date 2023-03-22: 1 交易日 / 24339 列 / 1080 筆
  UKStockInfo by-date 2023-04-19: 1 交易日 / 24339 列 / 1100 筆
  UKStockInfo by-date 2023-05-17: 1 交易日 / 24339 列 / 1120 筆
  UKStockInfo by-date 2023-06-14: 1 交易日 / 24339 列 / 1140 筆
  UKStockInfo by-date 2023-07-12: 1 交易日 / 24339 列 / 1160 筆
  UKStockInfo by-date 2023-08-09: 1 交易日 / 24339 列 / 1180 筆
  UKStockInfo by-date 2023-09-06: 1 交易日 / 24339 列 / 1200 筆
  UKStockInfo by-date 2023-10-04: 1 交易日 / 24339 列 / 1220 筆
  UKStockInfo by-date 2023-11-01: 1 交易日 / 24339 列 / 1240 筆
  UKStockInfo by-date 2023-11-29: 1 交易日 / 24339 列 / 1260 筆
  UKStockInfo by-date 2023-12-27: 1 交易日 / 24339 列 / 1280 筆
  UKStockInfo by-date 2024-01-24: 1 交易日 / 24339 列 / 1300 筆
  UKStockInfo by-date 2024-02-21: 1 交易日 / 24339 列 / 1320 筆
  UKStockInfo by-date 2024-03-20: 1 交易日 / 24339 列 / 1340 筆
  UKStockInfo by-date 2024-04-17: 1 交易日 / 24339 列 / 1360 筆
  UKStockInfo by-date 2024-05-15: 1 交易日 / 24339 列 / 1380 筆
  UKStockInfo by-date 2024-06-12: 1 交易日 / 24339 列 / 1400 筆
  UKStockInfo by-date 2024-07-10: 1 交易日 / 24339 列 / 1420 筆
  UKStockInfo by-date 2024-08-07: 1 交易日 / 24339 列 / 1440 筆
  UKStockInfo by-date 2024-09-04: 1 交易日 / 24339 列 / 1460 筆
  UKStockInfo by-date 2024-10-02: 1 交易日 / 24339 列 / 1480 筆
  UKStockInfo by-date 2024-10-30: 1 交易日 / 24339 列 / 1500 筆
  UKStockInfo by-date 2024-11-27: 1 交易日 / 24339 列 / 1520 筆
  UKStockInfo by-date 2024-12-25: 1 交易日 / 24339 列 / 1540 筆
  UKStockInfo by-date 2025-01-22: 1 交易日 / 24339 列 / 1560 筆
  UKStockInfo by-date 2025-02-19: 1 交易日 / 24339 列 / 1580 筆
  UKStockInfo by-date 2025-03-19: 1 交易日 / 24339 列 / 1600 筆
  UKStockInfo by-date 2025-04-16: 1 交易日 / 24339 列 / 1620 筆
  UKStockInfo by-date 2025-05-14: 1 交易日 / 24339 列 / 1640 筆
  UKStockInfo by-date 2025-06-11: 1 交易日 / 24339 列 / 1660 筆
  UKStockInfo by-date 2025-07-09: 1 交易日 / 24339 列 / 1680 筆
  UKStockInfo by-date 2025-08-06: 1 交易日 / 24339 列 / 1700 筆
  UKStockInfo by-date 2025-09-03: 1 交易日 / 24339 列 / 1720 筆
  UKStockInfo by-date 2025-10-01: 1 交易日 / 24339 列 / 1740 筆
  UKStockInfo by-date 2025-10-29: 1 交易日 / 24339 列 / 1760 筆
  UKStockInfo by-date 2025-11-26: 1 交易日 / 24339 列 / 1780 筆
  UKStockInfo by-date 2025-12-24: 1 交易日 / 24339 列 / 1800 筆
  UKStockInfo by-date 2026-01-21: 1 交易日 / 24339 列 / 1820 筆
  UKStockInfo by-date 2026-02-18: 1 交易日 / 24339 列 / 1840 筆
  UKStockInfo by-date 2026-03-18: 1 交易日 / 24339 列 / 1860 筆
  UKStockInfo by-date 2026-04-15: 1 交易日 / 24339 列 / 1880 筆
  UKStockInfo by-date 2026-05-13: 1 交易日 / 24339 列 / 1900 筆
  UKStockInfo by-date 2026-06-10: 1 交易日 / 24339 列 / 1920 筆
  UKStockInfo by-date 2026-07-08: 1 交易日 / 24339 列 / 1940 筆
[89/92] UKStockInfo: by-date 24339 列 / 1958 筆
[90/92] UKStockPrice: by-date 7732 列 / 2 筆
[91/92] USStockInfo: by-date 78 列 / 1 筆
[92/92] USStockPrice: pk-null-needs-dim 0 列 / - 筆

增量完成：74 dataset 有更新、共 454,497 列；14 dataset 略過（no-baseline / not-by-date-capable / intraday）
⚠ 2 dataset 之 catalog plan 為 by-dim-id 且本輪 by-date 0 列 ＝ **這條路推不動它**（M-G10）：['GovernmentBondsYield', 'TaiwanStockTotalReturnIndex']
  修法＝以 --with-dim-sync 走 _dimension_sync（FinMind 放量、須授權）；先看量請跑 --dim-sync-dry-run。
```

### MACRO tail
```
FRED 總經 sync：31 檔（Tier A 22 / Tier B vintage 9）
  FRED DGS10: +16849 列
  FRED DGS2: +13089 列
  FRED DGS3MO: +11719 列
  FRED DGS30: +12904 列
  FRED T10Y2Y: +13090 列
  FRED T10Y3M: +11631 列
  FRED DFF: +26329 列
  FRED T5YIE: +6153 列
  FRED T10YIE: +6153 列
  FRED DTWEXBGS: +5370 列
  FRED DEXTAUS: +11175 列
  FRED DEXKOUS: +11820 列
  FRED DEXCHUS: +11891 列
  FRED DEXJPUS: +14500 列
  FRED VIXCLS: +9544 列
  FRED BAMLH0A0HYM2: +795 列
  FRED BAMLC0A0CM: +795 列
  FRED DCOILWTICO: +10583 列
  FRED DCOILBRENTEU: +10224 列
  FRED NASDAQCOM: +14477 列
  FRED DPRIME: +18522 列
  FRED RRPONTSYD: +6127 列
  FRED UNRATE: +2196 列（vintage）
  FRED CPIAUCSL: +3360 列（vintage）
  FRED INDPRO: +39350 列（vintage）
  FRED PAYEMS: +13682 列（vintage）
  FRED GDPC1: +4402 列（vintage）
  FRED UMCSENT: +1081 列（vintage）
  FRED M2SL: +28533 列（vintage）
  FRED WALCL: +1772 列（vintage）
  FRED WRESBAL: +6771 列（vintage）
落地完成：344,887 列 / 31 series → fred_series
```

## 4. 08-04 日中增量

本輪主目標 `--end 2026-08-03`。若需 08-04 日中再增量，另開一小段（本 audit **未**自動含）。

## 5. 邊界

- **不是** catalog 無界全史
- Dividend rebuild／dim-sync／窄窗屬 `API-HEAVY-DIV-DIM-GAP-20260804.md` 三連（本輪不再 rebuild）
- **不 commit**

*寫於 2026-08-04T13:17:17.602726+08:00*
