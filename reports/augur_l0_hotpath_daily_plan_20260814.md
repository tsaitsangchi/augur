---
title: L0-HOTPATH-DAILY｜台灣熱路徑日班計畫書
status: predict_daily_adopted
viewpoint: 2026-08-14T09:50+08:00
register: audits/L0-HOTPATH-DAILY-PLAN-REGISTER-20260814.md
adopted: audits/L0-HOTPATH-PREDICT-DAILY-ADOPTED-20260814.md
layer: "[I]"
series: market_ops
track: L0-HOTPATH
role: L0＝預測日更 API 門（核 A＋TRI＋FRED；既有 20:00 arena ①＝本殼；**不新增** crontab）
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
l2_plan: reports/augur_daily_retrain_l2_all_rank_plan_20260812.md
b3_plan: reports/augur_daily_asof_b3_orchestrator_plan_20260805.md
ops_design: reports/augur_post_close_daily_asof_ops_design_20260805.md
empirical: audits/OPS-DAILY-0813-EXECUTED-20260814.md
self_reported: true
---

# L0-HOTPATH-DAILY｜台灣熱路徑日班（2026-08-14）

> **一句**：每天只把 **B3／L2 要用的台灣日頻＋TRI＋FRED** 增量到「FinMind 已有的最新交易日」；**不是** 93 表全日頻、**不是** 339 表、**不是** B3／L2。  
> **性質**：[I] 預測日更 L0 契約。Steward 2026-08-14「預測日更請走核 A＋TRI」＝**改既有 20:00 的取數內容**，不是新 timer。  
> **閉環位階**：r16 心跳的 **L0（API 門）**。L1／L2 仍人／watcher；本檔不授 no-cron-B3 的例外。

---

## §0 為何現在（08-14 實證）

| 事實 | 含義 |
|---|---|
| 採納前：平日 20:00 arena 跑 `daily_maintenance --end 當天`（無 `--datasets`） | L0 **有**排程，但是 **93 日頻全表** |
| 08-14 開 93 表 → `EuropeStockInfo` 自 **2019-01-14** 逐日回填 | 預設日班＝多年國際名冊 backfill，不是日更 |
| 改 47 張台灣日頻 `--end 2026-08-13` | **433,809** 列／約 29 min／RC=0 |
| TRI `--with-dim-sync`（TAIEX／TPEx） | **10** 列；TAIEX 08-07→**08-13** |
| `sync_macro --no-catalog` | FRED 31 檔／RC=0 |
| 08-13 價在 **08-14 早上**才進庫 | 20:00 鐘點≠價已到；Sponsor 斷過一晚 |

r16 S1 已釘：**資料完整＝THAW 熱路徑 as-of，≠ 339 表**。本檔把這句收成可執行的封閉集。

---

## §1 邊界（釘死）

| 在邊界內（日班可規畫） | 在邊界外（本計畫永不默納） |
|---|---|
| **核 A**：B3／特徵／籌碼依賴之台灣日頻（§3.1） | 預設 `daily_datasets()` 93 表 |
| **擴 B**（可選 `--extended`）：其餘台灣日頻（期貨／選擇權／新聞…） | Europe／US／UK／Japan／中國股 Info／Price 回填 |
| **維 C**：`TaiwanStockTotalReturnIndex` **只** TAIEX／TPEx | 全 `--with-dim-sync`（ExchangeRate 自 2020 等） |
| **經 D**：`sync_macro --no-catalog` | `--full-universe`／Dividend 全史／intraday／tick |
| stale-guard：resume 過舊 → **SKIP＋記帳**，不回填 | 把 SKIP 當「表已齊」塗綠 |
| 人／`--apply`／arena 20:00 ①＝本殼（2026-08-14 採納） | 新增 crontab 條／`install_cron.sh --apply`／`AUGUR_DIM_SYNC=1` |

```text
paste（邊界）:
  L0-HOTPATH | A+C+D 預設 | B=--extended
  | TRI-only-dim | stale-guard | no-93 | no-339
  | 既有20:00①=本殼 | 不新增cron | ≠B3 ≠L2 | no-promote
```

**「全系統日更」在本檔＝A＋C＋D**（核＋TRI＋FRED）。擴 B＝加長、不是預設。方向臂 Daily* **⊥** 本班（arena 20:00 已自建方向特徵；不塞進本殼）。

---

## §2 與既有 20:00 的關係

| 鏈 | 現況（2026-08-14 採納後） | 本檔做什麼 |
|---|---|---|
| arena 20:00 ① | `run_l0_hotpath_daily.sh --date D --apply`（核 A＋TRI＋FRED） | **已取代** 無 `--datasets` 的 93 表 |
| crontab 字面 | 仍 `run_arena_daily_pipeline.py --run` | **不**新增條、**不** `install_cron --apply` |
| `AUGUR_DIM_SYNC=1` | arena **忽略**並警告 | **禁**當其餘 5 張 dim 表捷徑 |
| 人跑本班 | 同一殼；與 20:00 可能同日重疊（冪等） | 可；勿再開 93 表 |

P4 拆成兩截：改 arena ①＝本句已授；**新 timer**仍❄。

---

## §3 封閉集

### 3.1 核 A（預設必跑）

B3 `feature_values`／籌碼 E 類真零／core 宇宙實際讀到的日頻：

```text
TaiwanStockPrice
TaiwanStockPriceAdj
TaiwanStockInfo
TaiwanStockPER
TaiwanStock10Year
TaiwanStockInstitutionalInvestorsBuySell
TaiwanStockMarginPurchaseShortSale
TaiwanStockShareholding
TaiwanDailyShortSaleBalances
TaiwanStockSecuritiesLending
TaiwanStockGovernmentBankBuySell
TaiwanStockDayTrading
TaiwanStockTotalInstitutionalInvestors
TaiwanStockTotalMarginPurchaseShortSale
```

08-14 親跑：上列在 `--end 2026-08-13` 後 tip 皆 **08-13**。

**不進核 A**（節奏不是「每個交易日一列」）：

| 表 | 理由 |
|---|---|
| `TaiwanStockMonthRevenue`／`TaiwanStockMonthPrice` | 月頻；07-01 不是洞 |
| `TaiwanStockFinancialStatements`／BalanceSheet／CashFlows | 季報 |
| `TaiwanStockHoldingSharesPer` | 集保週快照＋發布日 lag |
| `TaiwanStockDividend*` 未來除權日 | 事件／未來日，不當日更尺 |

### 3.2 擴 B（`--extended`）

08-14 已增量、非 B3 硬依賴：InfoWithWarrant、InstWide、當沖借券費、市值／權重、漲跌幅、News、鉅額、可轉債三表、擔保餘額、停牌、除權結果、產業鏈、期貨／選擇權日頻與法人（不含 tick）、整戶維持率、券商名冊、融資券／當沖暫停。

預設關。要「台灣日頻盡量齊」才開。仍受 stale-guard。

### 3.3 維 C（TRI 窄窗 dim-sync）

```text
daily_maintenance --datasets TaiwanStockTotalReturnIndex --with-dim-sync --end D
```

只 2 個文檔種子 id。**這是本班唯一准開的 dim-sync**。  
其餘 by-dim-id（CrudeOilPrices／ExchangeRate／GovernmentBondsYield／InterestRate／TaiwanExchangeRate）**不進本班**。

### 3.4 經 D

```text
python scripts/sync_macro.py --no-catalog
```

FRED 31 檔；不重探 catalog。

---

## §4 契約（殼必須守）

### 4.1 `D` 怎麼定

1. 顯式 `--date YYYY-MM-DD` 優先。  
2. 未指定 → 台北日曆日；週末／國定假 → **SKIP**（exit 0，記「非交易日」）。  
3. `--end D` 交給 FinMind；當天 API 尚無列＝該日 0 列，**不是**假成功。  
4. 成功尺看庫內 tip，不看日曆「今天」字面。

### 4.2 stale-guard（防 2019 回填）

對核 A／擴 B 每一張、且 catalog 頻率為 daily／single-day／single-series：

- `resume = max(date)`  
- 若 `resume` 空 → **拒跑該表**（no-baseline；不啟動全史）  
- 若 `resume < D − 21 日曆日` → **SKIP 該表**＋印黃帳（dataset、resume、D）  
- 其餘 → `sync_by_date --end D`（既有 resume＝重抓 tip 日補結算）

21 日＝涵蓋長假，擋不住的是「停更數年的國際名冊」。TRI／FRED 不套這條（TRI 走 2 id；FRED 本就全史冪等）。

### 4.3 成功／失敗尺

| RC | 含義 |
|---|---|
| **0** | 核 A 未 SKIP 者皆跑完；`PriceAdj(TAIEX) ≥ D` **或** FinMind 該日確實無價（probe 0 列＋level≠register） |
| **2** | 對帳／部分表 failed_days（可重試）；不假稱 tip＝D |
| **3** | FinMind level＝register／403／ban → **停、不重試風暴** |
| **0＋黃帳** | stale-guard SKIP 了某表；EXECUTED 必須列出 |

**硬成功（給 L1 的綠燈）**：`PriceAdj(TAIEX) ≥ D`。TRI 未到 D＝黃帳，**不擋** B3（B3 鎖的是 PriceAdj，不是 TRI）。方向臂若要 TRI＝另軸。

### 4.4 不做

- 不呼叫 B3／L2／predict／emit／promote  
- 不 `install_cron.sh --apply`（不新增 timer；既有 20:00 已改走本殼）  
- 不設 `AUGUR_DIM_SYNC=1`  
- 不把 p_beat／econ 寫進本班  
- 不在 Sponsor 掉級時改走逐股 3000 檔

---

## §5 建議產物（P1 才寫碼）

| 檔 | 職責 |
|---|---|
| `scripts/run_l0_hotpath_daily.sh` | `--date`／`--extended`／`--dry-plan`／`--selftest`／`--apply`；先 stale-guard 再 A→C→D |
| 日誌 | `/tmp/l0-hotpath-$D/`（`bydate.log`／`tri.log`／`macro.log`／`driver.log`） |
| 鎖 | `/tmp/augur_l0_hotpath.lock`（`flock -n`）；**不**占 `augur_llm.lock` |

```text
# P1 之後的指令矩陣（本檔日尚未存在）
bash scripts/run_l0_hotpath_daily.sh --selftest
bash scripts/run_l0_hotpath_daily.sh --date 2026-08-13 --dry-plan
bash scripts/run_l0_hotpath_daily.sh --date 2026-08-13 --apply
bash scripts/run_l0_hotpath_daily.sh --date 2026-08-13 --apply --extended
```

經驗錨（self-reported，08-14）：核 A＋擴 B＋TRI＋macro 約 **30–40 min**（Sponsor 6000／hr）。核 A＋C＋D 應更短。wall-clock 建議上限 **60 min**；超限停在當步、不開 93 表 fallback。

---

## §6 分階段授權

| 階段 | 產出 | 授權句（示意） | 狀態 |
|---|---|---|---|
| **P0** | **本計畫書**＋register | Steward 委託起草＝本檔 | ✅ |
| **P1** | 薄殼＋`--dry-plan`／`--selftest` | `L0-HOTPATH-SHELL-go` | ✅ `scripts/run_l0_hotpath_daily.sh` |
| **P2** | 真跑一日（建議新交易日或複跑已有 D）＋EXECUTED | `L0-HOTPATH-APPLY-go` | ✅ 08-14 RC=0；PriceAdj 仍 08-13 |
| **P3** | watcher：價未到則隔 15–30 min 重試至 23:50；仍無＝TIMEOUT 帳、**不假跑 B3** | `L0-HOTPATH-WATCH-go` | 🔴 |
| **P4a** | 改 arena ① 呼叫本殼（既有 20:00 取數內容） | Steward「預測日更請走核 A＋TRI」 | ✅ 2026-08-14 |
| **P4b** | 新增 crontab 條／`install_cron.sh --apply` | **雙明示**；本 plan **永不默授** | ❄ 禁默 |

P3 可選次日 07:30 補一槍（08-13 這種「收盤後 API 未出、次晨才有」）。補槍仍是 watcher，不是新 cron。

```text
paste（開殼）:
  L0-HOTPATH-SHELL-go | A+C+D | TRI-only-dim | stale-guard
  | FZ/GATE-keep | no-93 | 既有20:00①=本殼 | 不新增cron | ≠B3 ≠L2
```

---

## §7 建議時刻（人／P3；非默認 cron）

| 窗（Asia/Taipei） | 用途 |
|---|---|
| 20:00 | 既有 arena；①＝本殼（P4a） |
| 價到或 20:30–21:30 | 人跑／P3 watcher 開本班 |
| 本班 RC=0 且 `PriceAdj≥D` | 才准另句 B3（L1） |
| 23:50 | TIMEOUT；不假 B3 |
| 休市 | SKIP |

錯開 TWEVO 23:00：本班應在 22:30 前收工（或次晨補）。

---

## §8 與選刀／閉環

| 文件 | 關係 |
|---|---|
| r16 L0 | 本檔＝L0 熱路徑的執行契約 |
| B3／L1 | **下游**；本班成功≠自動 B3 |
| L2 | 更下游；本班永不 `--apply` L2 |
| arena 20:00 | ①＝本殼（P4a 已採納）；P4b 新 timer 仍❄ |
| KH | 正交 |

---

## §9 硬禁

1. 無授權把本班**另**寫進 `install_cron.sh`／systemd timer（既有 20:00 ①＝本殼，不算新條）  
2. 預設 93 表／339 表／`AUGUR_DIM_SYNC=1`  
3. stale-guard 失敗改「乾脆全史」  
4. 本班內開 B3／L2／promote／sim-apply  
5. Sponsor 掉 Free 後改逐股放量  
6. 把 TRI 未到當成假 B3 或當成 B3 已可跑的唯一尺（B3 尺＝PriceAdj）

---

## §10 工作包卡片

### WP-P0｜本檔（已做）

```text
WHEN: Steward「起草 L0 熱路徑日班」
DO:   計畫＋register；r16 L0 加指針
DONT: 寫殼; install_cron --apply; 當時不改 arena
DONE: 封閉集＋stale-guard＋P0–P4 分階
```

### WP-SHELL｜P1

```text
WHEN: L0-HOTPATH-SHELL-go
DO:   run_l0_hotpath_daily.sh + dry-plan + selftest
DONT: --apply 寫庫（除非同 GO 含 APPLY）; 改 crontab
DONE: dry-plan 印滿 A→C→D；selftest 旗標／路徑綠
```

### WP-APPLY｜P2

```text
WHEN: L0-HOTPATH-APPLY-go AND 指定 D
DO:   --apply（預設 A+C+D）→ tip 帳 → EXECUTED
DONT: B3; L2; --extended 除非同句; cron
DONE: PriceAdj(TAIEX) 與核 A 未 SKIP 者之 tip 誠實列出
```

---

## §11 修訂

| 日 | 變更 |
|---|---|
| 2026-08-14 | P0 初稿：核 A／擴 B／TRI-only／stale-guard；不改 20:00；P4 才 cron |
| 2026-08-14 | P1：薄殼 `run_l0_hotpath_daily.sh`；selftest／dry-plan 綠；真抓須 `--apply` |
| 2026-08-14 | P2：`--apply` D=08-14 RC=0；價頂仍 08-13（盤中無收盤列）；未開 B3 |
| 2026-08-14 | P4a：Steward「預測日更請走核 A＋TRI」→ arena ①＝本殼；P3／P4b 仍未授 |

*predict_daily_adopted · P3 watcher／P4b 新 cron 未授。*
