# augur 抓取資料問題總盤點 + 解決方案 (2026-06-20)

> 🎯 **這份在做什麼**：把 augur **ingestion（抓取）層**所有已知問題系統化——逐項記錄「根因 → 解決方案 → 狀態 → code 改動」，供逐一修正 + sync 完接續核閉環。整合本 session 發現 + `augur_fullsync_issues_20260617.md`(9 FAIL) + `augur_issue_status_20260618.md` + memory。
> 守原則 #1(零幻像)·#7(對帳)·#15(實證誠實、根因 source-traceable)·#24/#25(限速)·#3/#18(adaptive 抓取)。
> **護欄**：sync 在跑(PID 40071)、改 code 不影響正在跑進程(用啟動時 code);**驗證/放量/probe/heal 一律等 sync 完、不並發打 FinMind**。

## 問題分類總表

| # | 問題 | 類別 | 根因 | 解法 | 狀態 |
|---|---|---|---|---|---|
| 1 | `fred_series` EX=1 | 對帳 | FRED vintage 修訂日重對齊 | reconcile_fred 容忍 | ✅ 已閉環(5ce3ad8) |
| 2 | `GoldPrice` MIS=9997 | 對帳 | 對帳走 raw 5分鐘 vs DB 日級聚合 | reconcile_by_date 對 `_AGGREGATE_DAILY` 套聚合 | 🔧 本 session 已改 code、待 re-verify |
| 3 | `News` incomplete | 對帳 | by-date 逐 byte 不適事件流 | driver 路由→reconcile_coverage | 🔧 已改、待 re-verify |
| 4 | `Institutional` VM=1 | 對帳 | by-date vs per-stock 端點差(假 VM) | driver 路由→reconcile_per_stock | 🔧 已改、殘 VM 待 heal |
| 5 | `GovBondsYield` EX=442 | 對帳 | by-dim-id 表未走對函數 | driver 路由→reconcile_by_dim_id | 🔧 已改、待 re-verify |
| 6 | `Futures/OptionDealerVol` EX≡MIS | 對帳 | PK 含正規化對不上欄→key 系統性錯位 | probe 1 天定論哪欄 + 修 compare/PK | ⏳ 待 sync 完 probe |
| 7 | `USStockPrice` MIS=12102 | 完整性 | cooldown 漏抓(見 #8) | heal_by_date 補抓 | ⏳ 待 sync 完 heal |
| 8 | **cooldown 漏抓(通用)** | 完整性 | 撞 403→max_retries 用盡→跳過股、**無記錄** | 漏抓當下記錄(None≠[]) + sync 完精準 heal | 🔧 本 session 改 code |
| 9 | Deferred 3 表(分點/鉅額/權證) | 覆蓋 | sync 缺 dedicated 路徑 + 規模 + earliest 缺 | dedicated 抓取整合 + probe | 🔧 線 B 基礎已改、待續+probe |
| 10 | 額度逼近 6000(禁用閘下) | 運行 | per-stock 大表 32 並發淨增、無預防暫停 | 監控警示 + rolling 退出自然緩解 | 🔧 status script 已加警示 |
| 11 | Mac token user_count 黑箱失準 | 運行 | 服務端計數異常(零 call 不退反漲) | 禁用閘特例(讀錶不暫停) | ⚠️ 本地未 commit、待決(別機 git restore) |
| 12 | catalog earliest 缺/可疑 | 抓法 | 鉅額標 2026-05、權證空 | probe 補真起點 | ⏳ 待 sync 完 probe |

## 詳述 + 解決方案

### #8 cooldown 漏抓(本 session 重點解的完整性問題)
- **根因鏈**(source-traceable)：額度滿→`_protected_get`(finmind.py:101)撞 403→`sleep(QUOTA_COOLDOWN=1800s)`→重試;`max_retries`(4)用盡→`raise FinMindError`(finmind.py:132)→`_fetch_for_store`(sync.py)`return (sid, None)`→`_per_stock_sync._consume` `if rows:` 跳過→**該股漏抓**。實證 US `MIS=12102`(memory)。
- **關鍵**：`_fetch_for_store` 撞錯誤回 `None`、真無資料回 `[]`→**可區分漏抓 vs 真空**。
- **解法**(對齊用戶 2026-06-19「繼續並發、最後統一 heal」決策)：抓取**當下記錄漏抓 sids**(rows is None)→ sync 完對這清單**精準 heal**(不靠對帳近窗抽樣猜)。
  - code：`_per_stock_sync` 收集 `failed_ids`(rows is None)→ 回 summary;`_consume` 區分 `None`(漏抓記錄)vs `[]`(真空不記)。
  - 後續：full_market_sync 持久化 failed_ids + sync 完 heal(重抓 failed_ids)。

### #6 Dealer EX≡MIS（PK key 錯位）
- DealerVol PK=`date,dealer_code,dealer_name,futures_id,volume,is_after_hour`。`is_after_hour` 是 **API 真欄**(grep src 無、官方 datasets.md 漏列)。EX≡MIS 完全相等=某 PK 欄 DB/API 正規化系統性對不上→每筆同時 missing+extra。
- **解法**：sync 完 probe 1 天 API(最小單位 #25)→ 比對 DB row vs API row 逐 PK 欄→定論哪欄(疑 volume 數值 / dealer_name 全半形 / is_after_hour 型別)→ 修 `_norm`(加全半形正規化?)或收窄 PK(移數值/衍生欄)。

### #9 Deferred 抓取（線 B、用戶決策「合憲章就抓、依 catalog 逐筆硬抓」）
- 鉅額 per-stock 可行(~36min);分點/權證 dedicated;**關鍵未驗假說**：fetch_dedicated 若吃 start_date 範圍→分點~3105/權證~45035 calls 可行(非逐日天文)。
- code 已做：sync `_fetch_for_store`/`_per_stock_sync` 加 `dedicated` 參數。待續：`_sync_by_plan` dedicated 分支 + roster 來源 + 移出 BACKFILL_DEFERRED + catalog + doctrine。待 probe：範圍?權證 roster?earliest?

## code 改動清單

**本 session 已改(未 commit、import/dry 驗過)**：
- `reconcile.py`：GoldPrice 聚合對帳(#2)。
- `reconcile_audit.py`：catalog-driven 全 84 表 + scope 路由(#2-5 方法學)。
- `sync.py`：`_fetch_for_store`/`_per_stock_sync` 加 `dedicated` 參數(#9 基礎)。
- `/tmp/augur_status_report.sh`：現抓修正 + 額度/停滯警示(#10)。

**本 session 續改(護欄內、不打 API)**：
- `sync.py`：`_per_stock_sync` 收集 failed_ids(#8 cooldown 漏抓記錄)。

**待 sync 完(打 API)**：probe(#6/#9/#12)→ heal(#7/#8/#4)→ 全 84 表 re-verify(#2-6)→ deferred 放量(#9)。

## #13 [59] ConvertibleBondDailyOverview 不完整（2026-06-20 重啟副作用）
- 為上「主動閘」重啟 sync（--new-only）時，舊 run 已開始抓 [59] ConvertibleBondDailyOverview（抓到 2010-02 被 kill）→ --new-only 跳過（它有部分資料）→ **DB 僅 2010-01~02、缺 2010-02 之後到 2026**。
- ⚠️ **reconcile_audit 近窗對帳抓不到**：只對 DB 既有日期（2010 頭）近窗比對 → 會 PASS、不會發現缺後段（盲點）。
- **解法**：sync 完**明確** `sync.sync_by_date('TaiwanStockConvertibleBondDailyOverview', start=<earliest>, end=<today>)` 全史補抓（冪等覆蓋）；不靠對帳自動發現。或 truncate 後重抓。
- **同類 [63] TaiwanStockMonthPrice 不完整**（2026-06-20 第二次重啟[回禁用閘]副作用）：per-stock、--new-only 跳過時僅 1950/3105 股 → 缺 ~1155 股。解法：sync 完 per-stock heal（`_per_stock_sync` 對缺股重抓，或 truncate 後重抓全 roster）。reconcile_per_stock 抽樣對帳也可能漏（只抽 50 股）→ 須明確全 roster 補。
- **同類 [64] TaiwanStockWeekPrice 不完整**（2026-06-20 第三次重啟[MIN_INTERVAL 0.9]副作用）：per-stock、--new-only 跳過時僅 1300/3105 股 → 缺 ~1805 股。解法同 [63]（全 roster per-stock heal）。
- **heal 清單合計 3 表**（重啟 --new-only 跳過進行中表的代價）：[59]/[63]/[64]，全須 sync 完明確全史/全 roster 補（對帳盲點抓不到）。

## #14 [62] TaiwanTotalExchangeMarginMaintenance VM=1（2026-06-20 新 run 對帳 FAIL）
- 新 run [62] 對帳 FAIL VM=1 EX=0（market by-date、大盤融資維持率每日一值）。非 roster-scoped 假 VM。
- 最可能=**最新日維持率近日修訂/未定案**。full_market_sync verify() 無 unsettled buffer，但 `reconcile_audit`（本 session 改）有（排除最近 2 日）→ sync 完 re-verify 應被吸收 PASS。
- 解法：sync 完 `reconcile_audit.py --tables TaiwanTotalExchangeMarginMaintenance` re-verify 確認（已含在全 84 表 re-verify）。

## #15 新閘 HEADROOM 對 per-stock 32 並發 burst 偏薄（2026-06-20 實證）
- 新閘暫停閾值 limit−HEADROOM=5800，但 per-stock 32 並發在「每 120 call 讀錶」間隙 + in-flight call 衝過閾值 → 實證額度 rolling 計數衝到 **6013 > 6000**（[63] MonthPrice）。
- **未撞 403**：暫停後不發新 call、in-flight 是暫停前額度<6000 發出的（服務端已接受），6013 只是 rolling 計數、非 403。退續門檻 5000<6000 → 續抓安全。功能達標（防 403/漏抓）。
- **未來可選優化**：調 HEADROOM 200→800（閾值降到 5200、留 600 buffer 給 32 並發 burst），讓額度真停在 ~5400 不越 6000。但需重啟 sync（會讓當下進行中的 per-stock 表被 --new-only 跳過變不完整）→ 擇機（如 sync 自然結束後）再調。

## 執行時機
所有 code 改 = 現在(護欄內);所有 probe/heal/re-verify/放量 = **sync 完成後**(剩 ~28 表、勿並發 #24)。放量/commit/push 須用戶明示授權。
