# augur Issue 整合狀態總表 + 接續計畫 (2026-06-22)

> 🎯 **這份在做什麼**:整合 reports/ 下 8 個 issue 檔案 + **本機(WSL2)真實 DB 實證**之單一 issue tracker;
> 列每項根因/狀態/解法/護欄分類,供用戶逐項拍板。**取代**散落的 augur_fullsync_issues_*.md / issue_status / ingestion_issues。
>
> 守 #15(實證誠實、source-traceable)·#20(主動但實證、決策層人拍板)·#24/#25(放量需護欄/IP休養)。

---

## 0. 關鍵環境實況(2026-06-22、本機 WSL2 實查)

| 項目 | 值 | 來源 |
|---|---|---|
| FinMind 額度錶 | **5832 / 6000(餘 168)⚠️ 過熱** | `_user_quota()` |
| FinMind token 到期 | **2026-06-24(剩 ~2 天)** | sponsor info |
| FRED | 84,766 列 / 31 series(Tier A 22 + Tier B 9) | DB query |
| DB in-scope 完整度 | **39 / 84 有資料、45 缺、1 LOW** | `count(*)` 實證 |
| DB 總列數 | ~2.34 億 / 39 表 | `count(*)` 實證 |
| git HEAD | `9d97b11`(已 push) | `git log` |
| 進行中進程 | 無 | `ps aux` |

⚠️ **6/22 milestone「84 表 100% 完整」**:該 commit 在另一台機(疑 Mac)寫的、reflects 那台 DB;**本機(WSL2)實證 45 表缺、6/22 milestone 對本機不適用**。本機若要「84 表完整」需 (a) 從 Mac `pg_restore` 或 (b) 本機重抓 45 缺表(趕 6/24)。

⚠️ **額度過熱**:餘 168/小時、IP 在熱期;**任何 API 放量(heal/probe/全 sync)會立刻撞 403**。必須 cooldown 至 ≤2900 才安全放量。

---

## 1. Issue 已閉環(✅;code 已 commit、本機 git pull 即有)

| # | issue | 解法 commit | 驗證 |
|---|---|---|---|
| 1 | GovBank 寬 PK 數值假 EX (412,111 列假 false-neg) | `fadba1a`:`_key` → `tuple(_norm(...))` | 6/18 [1/83] PASS |
| 2 | FuturesDaily/OptionDaily numeric exception (`200710/200711`、`201211W4`) | `e95cec1`:schema 跨型別降級 NUMERIC→VARCHAR | [20/83]/[21/83] PASS |
| 3 | SecuritiesLending date sentinel `-1` exception | `e95cec1`:DATE→VARCHAR 降級 | 同 |
| 4 | ConvertibleBondDailyOverview 非法日 `1911-00-00` exception | `e95cec1`:`_is_date` 加 `date.fromisoformat` 合法性驗 | 同 |
| 5 | FuturesFinalSettlementPrice `202101W1` exception | `e95cec1` | 同 |
| 6 | USStockPrice `stock_id=null` exception (1997 指數彙總) | `6aa7d25`:market PK-null fallback → by-dim-id (Info roster) | 同 |
| 7 | FRED `fred_series` EX=1 假旗 (FRED 修訂日重對齊 `BAMLH0A0HYM2`) | `5ce3ad8`:`reconcile_fred` vintage 容忍 | 6/18 實證 PASS |
| 8 | Institutional VM 假 EX (per-stock vs by-date 端點差) | `e8ef8c4`:`reconcile_per_stock` 對齊端點 | sample 60: VM 73→0 |
| 9 | CrudeOilPrices/ExchangeRate EX 假 MIS (by-dim-id 走 by-date 對) | `7ff03f9`:`reconcile_by_dim_id` + catalog `reconcile_scope` 對齊 | 6/18 commit |
| 10 | UK/Europe/US/Japan 國際股漏抓 (誤判 per-stock) | `184cd7d`:`optimal_mode` 國際股 src=none → by-date | 6/15 commit |
| 11 | News 對帳 incomplete (秒級時戳新聞流) | `7650167`:News intraday→日級聚合 + `reconcile_coverage`(列數量級) | 6/18 commit |
| 12 | GoldPrice MIS=9997 (對帳 raw 5min vs DB 日級聚合) | `bfff28d`:`reconcile_by_date` 對 `_AGGREGATE_DAILY` 套聚合 | 6/22 commit |
| 13 | cooldown 漏抓無記錄 | `bfff28d`:`_per_stock_sync` 收集 `failed_ids`(rows is None) | 6/22 commit |
| 14 | catalog `_dedicated_probe_ids` from-scratch crash | `d5fc040`:加 TaiwanStockInfo table-exists 防護 | 6/22 commit |
| 15 | MIN_INTERVAL 0.7s ban 風險 | `2f5fa6e`:0.7→0.9 降 start rate(per-stock 32 並發平衡點 <5500) | 6/22 commit |
| 16 | FRED 12 series → 缺 vintage PIT | `52b2b2b`:FRED 擴 31 series + Tier B ALFRED vintage | 6/22 commit |

**16 項 code-level issue 已閉環**。其餘屬「data 層完整性/驗證」未做。

---

## 2. Issue 待處理(分 5 大類、按依賴排序)

### Class A — **本機資料完整性缺口**(45 缺表、最大障礙)

本機 39/84 完整、缺 45 表。**用戶須先決策 DB 來源**:

| 選項 | 描述 | 時間 | 額度需求 | 風險 |
|---|---|---|---|---|
| A1 從 Mac `pg_restore` 搬 | Mac 84 表完整(6/22 milestone)→ dump → 本機 restore | 數小時 | 無 | 須用戶在 Mac 操作 |
| A2 本機從零重抓 45 缺表 | catalog-driven sync (--new-only 跳已有) | **預估 1.5-2 天 @0.9s/32w** | ~128k calls (估) | 趕 6/24、IP 須先休養 |
| A3 放棄完整性、用既有 39 表 | 純大表已抓完;但 67 個籌碼/事件/衍生表缺、影響特徵 | 0 | 0 | 不可解凍 F2/F3 |

**強烈建議 A1**(token 剩 2 天、A2 風險高;A3 阻塞下游)。但需用戶在 Mac 操作 pg_dump → 傳輸 → 本機 pg_restore。

**45 缺表清單**(catalog excluded=f 但本機 DB 無):
EuropeStockPrice、GovernmentBondsYield、InterestRate、JapanStockPrice、TaiwanBusinessIndicator、TaiwanFutOptInstitutionalInvestors、TaiwanFutures(Dealer/FinalSettlement/Institutional×2/OpenInterest/Spread)、TaiwanOption(同類×6)、TaiwanStock10Year、TaiwanStockBlockTrade、TaiwanStockCapitalReduction、TaiwanStockConvertibleBond×4、TaiwanStockDayTrading(×3)、TaiwanStockDelisting、TaiwanStockDispositionSecurities、TaiwanStockIndustryChain、TaiwanStockInfoWithWarrantSummary、TaiwanStockLoanCollateralBalance、TaiwanStockMarginShortSaleSuspension、TaiwanStockMarketValue(×2)、TaiwanStockMonthPrice、TaiwanStockParValueChange、TaiwanStockPriceLimit、TaiwanStockSplitPrice、TaiwanStockSuspended、TaiwanStockTotalReturnIndex、TaiwanStockTradingDate、TaiwanStockWeekPrice、TaiwanTotalExchangeMarginMaintenance、UKStockInfo。

**1 LOW 表**(< 1000 列、疑不完整):`TaiwanSecuritiesTraderInfo` 63 列。

### Class B — **既有 39 表 reconcile re-verify**(用 catalog-driven scope 路由)

對帳 code 已完整 commit、本機 sync 進程用啟動時舊 code → 已落地表的歷史 reconcile FAIL 須當前 code re-verify。

| dataset | 原 issue | 預期 |
|---|---|---|
| `TaiwanStockInstitutionalInvestorsBuySell` | 6/13 VM=33 / 6/18 VM=1 | 走 `reconcile_per_stock` + heal_by_date 重抓覆蓋為 API 當前 → 殘 VM 為近日修訂真差異 |
| `TaiwanFuturesSpreadTick` | 6/13 EX=390 | 待當前 code 對 by-dim-id 重對帳 |
| `TaiwanStockNews` | 6/13 incomplete | 走 `reconcile_coverage`(已落、待執行) |
| `fred_series` | 6/13/17/18 EX=1 | 走 `reconcile_fred` vintage 容忍 → 預 PASS |
| `TaiwanDailyShortSaleBalances` | 6/16 EX=68 | per-stock 對帳已修 → 預 PASS |
| `TaiwanFutures/OptionDealerTradingVolumeDaily` | 6/10 EX≡MIS=154k/25k(PK key 錯位) | sync 完 probe 1 天定論哪欄(疑 volume 數值/dealer_name 全半形/is_after_hour 型別)→ 修 `_norm`/收窄 PK |

**動作**:跑 `PYTHONPATH=src venv/bin/python scripts/reconcile_audit.py`(catalog 驅動全 39 有資料表 scope 路由)、約 30-60 分;**走 FinMind+FRED API、額度敏感**(須先 IP cooldown)。

### Class C — **catalog 元資料 probe**(可選、不阻塞)

| dataset | 問題 | 解法 |
|---|---|---|
| 鉅額(BlockTradingDailyReport)| catalog earliest 標 2026-05(可疑、似只近窗) | dedicated endpoint probe 真起點 |
| 權證(WarrantTradingDailyReport)| catalog earliest 空 | dedicated endpoint probe |
| 分點(TradingDailyReport)| catalog earliest 已實證 ~4838 列/股/日 | scope 待決(per-(股,日)規模) |

3 表屬 `BACKFILL_DEFERRED`(可抓但 scope 待決、非排除)。**動作**:sync 完 probe + 抓全市場(趕 6/24);scope 屬放量決策、須用戶授權。

### Class D — **#8 漏抓記錄缺陷修正**(code-level、護欄內可做)

6/22 milestone 發現:
- `full_market_sync.issue()` 寫 `failed_ids[:30]`、markdown 寫入截斷 → BlockTrade 190 股清單行止於 `'2`、無閉合 `]` → heal 腳本 regex parse 不到。
- **正解**:per-stock 漏抓表 heal 一律走全 roster resume(`_per_stock_sync` 有資料股 resume from max、漏股從 floor 補),不依賴 `failed_ids` 清單。
- **TODO**:`issue()` 不截斷 list;或 per-stock 漏抓改記「需全 roster heal」旗標而非逐股清單。

**動作**:改 `scripts/full_market_sync.py` `issue()` 函數 + 改 sync issue 寫入機制。**護欄內、不放量、可立即做**;但需 commit 授權。

### Class E — **issue 報告檔清理**(純文件、護欄內)

8 個 issue 報告檔分散且重複:

| 檔 | 狀態 | 建議 |
|---|---|---|
| `augur_fullsync_issues_20260610.md` | 16 筆 exception(已修)| 保留歷史 |
| `augur_fullsync_issues_20260613.md` | sync log(已修改未 commit)| 保留歷史(內容為最近一次 sync 寫入) |
| `augur_fullsync_issues_20260616.md` | 1 筆 ShortSale EX=68(已修)| 保留歷史 |
| `augur_fullsync_issues_20260617.md` | 3 筆 cooldown(已修)| 保留歷史 |
| `augur_fullsync_issue_analysis_20260610.md` | 根因分析(已落地)| 保留(分析價值) |
| `augur_issue_status_20260618.md` | 6/18 狀態(過時)| 標 SUPERSEDED |
| `augur_ingestion_issues_20260620.md` | 6/20 15 issues 盤點 | 標 SUPERSEDED |
| `augur_fullsync_complete_20260622.md` | sync milestone + 接續 | 標 SUPERSEDED |
| **`augur_issue_consolidated_20260622.md`** | **本檔(取代)** | ACTIVE |

**動作**:在舊檔頂部加 SUPERSEDED 標、指向本檔。純文件、護欄內、可立即做(commit 授權)。

---

## 3. 護欄分類 + 待用戶決策

### 立即可做(護欄內、不放量、不需 commit)
- E:整理舊 issue 檔(加 SUPERSEDED 標、本機修改、未 commit)。

### 需 commit 授權(護欄內、可逆)
- D:`full_market_sync` issue() 不截斷 + 改 per-stock heal 機制(code 改)。
- E:舊 issue 檔 SUPERSEDED 標 + commit。

### 需用戶決策(資料來源選擇、戰略)
- **A:DB 來源**(A1 pg_restore vs A2 本機重抓 vs A3 放棄完整性)。
- **趕 6/24 token 到期之優先順序**(若選 A2、A3,則 sponsor-only 表抓取窗 ~2 天)。

### 需放量授權(API + 護欄)
- B:`reconcile_audit.py` 對既有 39 表 re-verify(走 FinMind+FRED API、額度敏感、先 IP cooldown)。
- A2:本機重抓 45 缺表(if 選 A2)。
- C:deferred 3 表 probe + 抓(if 用戶授權 scope)。
- B 後段:heal_by_date 重抓殘 VM 表(Institutional 等)。

---

## 4. 建議執行順序(經您拍板後)

```
階段 1 (護欄內、立即):
  D code fix (full_market_sync issue 截斷) → 本機 edit、待 commit 授權
  E 舊 issue 檔加 SUPERSEDED 標 → 本機 edit、待 commit 授權

階段 2 (決策):
  用戶選 A1/A2/A3 → 訂 DB 完整度策略

階段 3 (放量,if A2/B):
  IP cooldown 至 ≤2900 (~30-60 分)
  A2: --new-only 補抓 45 缺表 (預估 1.5-2 天) ← if 選 A2
  B: reconcile_audit.py re-verify 39 既有表 (30-60 分) ← if 選 B
  C: deferred 3 表 probe + 抓 ← if 用戶授權

階段 4 (commit、用戶授權):
  commit code 修正 + 整合 report + 對帳結果
  push origin/main
```

---

## 5. 我的建議

**首選 A1 (Mac pg_restore 搬)** + **D + E (本機 code/文件整理)** + **B (re-verify)**:
- A1 最快、最安全、避開 6/24 token 風險
- D + E 護欄內可做、不阻塞
- B 在 A1 後跑、走少量 API 額度(對帳近窗、非全史)

若 Mac 不便取得 dump、退而求其次 **A2** + 上述 D/E/B。

**請您拍板**:
1. A1 / A2 / A3 哪個?
2. D + E 護欄內 code 修 + 文件整理 → 可現做 / 等決策後一起做?
3. B re-verify 39 既有表 → 等 A 結果再做 / 現做(走少量額度)?
