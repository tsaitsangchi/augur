# API 重量序：Dividend → dim-sync → 缺口窄窗（2026-08-04）

> **位階**：[I] 執行留痕（非 [N]）  
> **授權**：Steward 裁 — 順序 Dividend → dim-sync → 只補庫內缺口窄窗；等 MC asof 08-03 重算與日頻 catchup 告一段落再開；見 403 即停。  
> **狀態**：**DONE**（閘已過）（啟動時 MC／catchup 未完；背景編排輪詢，禁前景阻塞）

## 0. 閘條件

| 閘 | 啟動時（~08:56+08） | 通過判準 |
|---|---|---|
| MC asof 2026-08-03 | `mc_simulation_run` max asof 仍 **2026-05-31**（540 列）；無 `MC-ASOF-20260803-RERUN-20260804.md` | audit 出現 **或** cone／run 列 `asof_date=2026-08-03` 齊（≥1 列起算放行，寫入實數） |
| 日頻 catchup | `daily_maintenance --end 2026-08-03` PID 跑中；`sync_macro --no-catalog` 跑中；無 `API-CATCHUP-20260804.md` | catchup audit 出現 **或** dm+macro 兩 PID 皆結束 |
| 超時 | — | 等閘 **6h** → 寫 TIMEOUT 段、停、問 Steward |

## 1. Dividend 現況（庫內親查，開跑前）

| 項 | 值 |
|---|---|
| PK | `(stock_id)` 單欄 — **塌列復現** |
| 列／distinct stock | 2411／2411；2330＝1 |
| bak_20260724 | **不存在**（庫可能換過／未還原 partial） |
| 續跑策略 | 依 `reports/augur_dividend_rebuild_20260724.md` §8：RENAME live＋rename 舊 PK 索引名 → `sync.sync_finmind_dataset`／`_per_stock_sync` resume；見 403 即停 |

## 2. 進度（由背景編排追加）

| 步 | 狀態 | rc | 時刻 | 註 |
|---|---|---|---|---|
| A 等閘 | done | 0 | 2026-08-04T09:00:26+08:00 | 閘清 |
| B1 Dividend | done | 0 | | | |
| B2 dim-sync | done | 0 | | | |
| B3 缺口窄窗 | done | 0 | | | |

## 3. 禁則

- 禁無界全史／亂寬窗／`--full-universe`
- 不搶 `heavy_slot`（佔用則該步延後或 SKIP 問 Steward）
- 不 commit

---
*起草：WAITING_GATE。後續段落由編排腳本追加。*

## A 閘通過 2026-08-04T09:00:26+08:00

- MC：audit=yes；asof08-03 count=
- catchup：audit=yes；dm/macro 進程已結束

## Steward 放行（STEWARD-FULL-ROSTER-20260804）

- **裁**：照跑 **全 roster** Dividend resume；見 **403／額度即停、不重試風暴** → dim-sync → 缺口窄窗。
- **時刻**：2026-08-04T09:01+08（口頭確認時編排已閘清並開 B1）

## A 閘通過 2026-08-04T09:00:26+08:00（編排寫入）

- MC／catchup 雙閘已清；狀態改 **DONE**

## B1 起步親查（2026-08-04T09:00:26+08 起）

| 項 | 值 |
|---|---|
| 起步 | **2026-08-04T09:00:26+08:00**（`B1 Dividend start`） |
| #25 probe | `PROBE_OK rows=1`（2330／2026-06-17） |
| PK_BEFORE | `['stock_id']` → RENAME `TaiwanStockDividend_collapsed_bak_20260804`＋PK 索引更名 |
| roster_n | **3132**（全 roster） |
| log | `/tmp/augur_logs/dividend_resume_20260804.log` |
| orch PID | 827735 |


### B1-PULSE-50-3132 (2026-08-04T09:02:11+08:00)

`TaiwanStockDividend: 50/3132 股、累計 247 列（32 並發)` — PID 830767 under orch 827735。

### B1-PULSE (2026-08-04T09:05:11+08:00)

`  TaiwanStockDividend: 300/3132 股、累計 3628 列（32 並發）`

### B1-PULSE (2026-08-04T09:08:11+08:00)

`  TaiwanStockDividend: 500/3132 股、累計 4967 列（32 並發）`

### B1-PULSE (2026-08-04T09:11:11+08:00)

`  TaiwanStockDividend: 700/3132 股、累計 7783 列（32 並發）`

### B1-PULSE (2026-08-04T09:14:11+08:00)

`  TaiwanStockDividend: 900/3132 股、累計 10525 列（32 並發）`

### B1-PULSE (2026-08-04T09:17:11+08:00)

`  TaiwanStockDividend: 1100/3132 股、累計 13195 列（32 並發）`

### MONITOR-PULSE (2026-08-04T09:18:57+08:00)

`  TaiwanStockDividend: 1200/3132 股、累計 14602 列（32 並發）`

### MONITOR-PULSE (2026-08-04T09:23:57+08:00)

`  TaiwanStockDividend: 1550/3132 股、累計 19174 列（32 並發）`

### MONITOR-PULSE (2026-08-04T09:28:57+08:00)

`  TaiwanStockDividend: 1850/3132 股、累計 22448 列（32 並發）`

### MONITOR-PULSE (2026-08-04T09:33:57+08:00)

`  TaiwanStockDividend: 2200/3132 股、累計 27181 列（32 並發）`

### MONITOR-PULSE (2026-08-04T09:38:57+08:00)

`  TaiwanStockDividend: 2550/3132 股、累計 29189 列（32 並發）`

### MONITOR-PULSE (2026-08-04T09:43:57+08:00)

`  TaiwanStockDividend: 2850/3132 股、累計 29958 列（32 並發）`

## B1 Dividend rc=0 2026-08-04T09:47:31+08:00

```
  TaiwanStockDividend: 1450/3132 股、累計 18006 列（32 並發）
  TaiwanStockDividend: 1500/3132 股、累計 18587 列（32 並發）
  TaiwanStockDividend: 1550/3132 股、累計 19174 列（32 並發）
  TaiwanStockDividend: 1600/3132 股、累計 19634 列（32 並發）
  TaiwanStockDividend: 1650/3132 股、累計 20214 列（32 並發）
  TaiwanStockDividend: 1700/3132 股、累計 20645 列（32 並發）
  TaiwanStockDividend: 1750/3132 股、累計 21254 列（32 並發）
  TaiwanStockDividend: 1800/3132 股、累計 21907 列（32 並發）
  TaiwanStockDividend: 1850/3132 股、累計 22448 列（32 並發）
  TaiwanStockDividend: 1900/3132 股、累計 23065 列（32 並發）
  TaiwanStockDividend: 1950/3132 股、累計 23843 列（32 並發）
  TaiwanStockDividend: 2000/3132 股、累計 24486 列（32 並發）
  TaiwanStockDividend: 2050/3132 股、累計 25281 列（32 並發）
  TaiwanStockDividend: 2100/3132 股、累計 26005 列（32 並發）
  TaiwanStockDividend: 2150/3132 股、累計 26662 列（32 並發）
  TaiwanStockDividend: 2200/3132 股、累計 27181 列（32 並發）
  TaiwanStockDividend: 2250/3132 股、累計 27621 列（32 並發）
  TaiwanStockDividend: 2300/3132 股、累計 28014 列（32 並發）
  TaiwanStockDividend: 2350/3132 股、累計 28343 列（32 並發）
  TaiwanStockDividend: 2400/3132 股、累計 28653 列（32 並發）
  TaiwanStockDividend: 2450/3132 股、累計 28891 列（32 並發）
  TaiwanStockDividend: 2500/3132 股、累計 29067 列（32 並發）
  TaiwanStockDividend: 2550/3132 股、累計 29189 列（32 並發）
  TaiwanStockDividend: 2600/3132 股、累計 29226 列（32 並發）
  TaiwanStockDividend: 2650/3132 股、累計 29385 列（32 並發）
  TaiwanStockDividend: 2700/3132 股、累計 29472 列（32 並發）
  TaiwanStockDividend: 2750/3132 股、累計 29534 列（32 並發）
  TaiwanStockDividend: 2800/3132 股、累計 29572 列（32 並發）
  TaiwanStockDividend: 2850/3132 股、累計 29958 列（32 並發）
  TaiwanStockDividend: 2900/3132 股、累計 30599 列（32 並發）
  TaiwanStockDividend: 2950/3132 股、累計 31298 列（32 並發）
  TaiwanStockDividend: 3000/3132 股、累計 31917 列（32 並發）
  TaiwanStockDividend: 3050/3132 股、累計 32140 列（32 並發）
  TaiwanStockDividend: 3100/3132 股、累計 32933 列（32 並發）
  → TaiwanStockDividend：catalog 驅動 per-stock → 32933 列
SYNC_RESULT={'dataset': 'TaiwanStockDividend', 'mode': 'per-stock', 'rows': 32933, 'stocks_with_data': 2573, 'failed_ids': []}
AFTER (32933, 2573)
2330 42
PK_AFTER ['stock_id', 'date']
B1_DONE
```

## B2 dim-sync rc=0 2026-08-04T09:47:34+08:00

```
每日維護 by-date：1 日頻 dataset（--with-dim-sync：by-dim-id 者改走逐維度 id＝FinMind 放量）
  → TaiwanStockTotalReturnIndex：by 維度 id（2 個、來源 文檔種子：['TAIEX', 'TPEx']…）
[1/1] TaiwanStockTotalReturnIndex: by-dimension-id 32 列 / - 筆

增量完成：0 dataset 有更新、共 0 列；1 dataset 略過（no-baseline / not-by-date-capable / intraday）
```

## B3 缺口 probe 2026-08-04T09:48:26+08:00

```
TaiwanStockPriceAdj: max=2026-08-03
TaiwanStockPrice: max=2026-08-03
TaiwanStockMarginPurchaseShortSale: max=2026-08-03
TaiwanStockInstitutionalInvestorsBuySell: max=2026-08-03
TaiwanStockPER: max=2026-08-03
TaiwanStockDayTrading: max=2026-08-03
TaiwanStockTradingDailyReport: MISSING
TaiwanStockTotalReturnIndex: max=2026-07-31
GAPS= [('TaiwanStockTotalReturnIndex', '2026-07-31', '2026-08-03')]
```

### B3 fill rc=0
```
TaiwanStockPriceAdj: max=2026-08-03
TaiwanStockPrice: max=2026-08-03
TaiwanStockMarginPurchaseShortSale: max=2026-08-03
TaiwanStockInstitutionalInvestorsBuySell: max=2026-08-03
TaiwanStockPER: max=2026-08-03
TaiwanStockDayTrading: max=2026-08-03
TaiwanStockTradingDailyReport: MISSING
TaiwanStockTotalReturnIndex: max=2026-07-31
GAPS= [('TaiwanStockTotalReturnIndex', '2026-07-31', '2026-08-03')]
每日維護 by-date：1 日頻 dataset
[1/1] TaiwanStockTotalReturnIndex: not-by-date-capable 0 列 / - 筆 / ⚠ 需逐維度 id 抓取（by-date 推不動;M-G10、須 --with-dim-sync 且經授權）

增量完成：0 dataset 有更新、共 0 列；1 dataset 略過（no-baseline / not-by-date-capable / intraday）
⚠ 1 dataset 之 catalog plan 為 by-dim-id 且本輪 by-date 0 列 ＝ **這條路推不動它**（M-G10）：['TaiwanStockTotalReturnIndex']
  修法＝以 --with-dim-sync 走 _dimension_sync（FinMind 放量、須授權）；先看量請跑 --dim-sync-dry-run。
```

## 總結 2026-08-04T09:48:27+08:00

| 步 | rc |
|---|---|
| B1 Dividend | 0 |
| B2 dim-sync | 0 |
| B3 gap | 0 |
| 403 停手 | no |

*編排結束。不 commit。*

## Monitor 觀測：orch 已退出 (2026-08-04T09:48:57+08:00)

orch log tail:

```
[2026-08-04T08:58:26+08:00] ORCH start; timeout=21600s
[2026-08-04T08:58:26+08:00] A WAITING for MC + catchup
[2026-08-04T08:58:26+08:00] pulse elapsed=1s mc_ok=1 catchup_ok=0 dm=1 macro=1
[2026-08-04T09:00:26+08:00] pulse elapsed=121s mc_ok=1 catchup_ok=1 dm=0 macro=0
[2026-08-04T09:00:26+08:00] GATES CLEAR
[2026-08-04T09:00:26+08:00] B1 Dividend start
[2026-08-04T09:47:31+08:00] B1 Dividend rc=0
[2026-08-04T09:47:31+08:00] B2 dim-sync start
[2026-08-04T09:47:34+08:00] B2 dim-sync rc=0
[2026-08-04T09:47:34+08:00] B3 gap probe
[2026-08-04T09:48:26+08:00] B3 narrow fill datasets: TaiwanStockTotalReturnIndex
[2026-08-04T09:48:27+08:00] B3 rc=0
[2026-08-04T09:48:27+08:00] ORCH DONE DRC=0 DIM=0 GAP=0
```

### DB 終態親查


| 表 | 指標 |
|---|---|
| TaiwanStockDividend | n=32933 stocks=2573 max(date)=2026-10-12 |
