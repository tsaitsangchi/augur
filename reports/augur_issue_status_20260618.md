⚠️ **SUPERSEDED** by [`augur_issue_consolidated_20260622.md`](augur_issue_consolidated_20260622.md)(更新版 issue tracker、含本機 WSL2 真實 DB 實證)。本檔為 2026-06-18 階段性狀態(過時)。

---

# augur 全市場 sync 問題處理狀態總表 (2026-06-18)

> 🎯 **這份在做什麼**：把 `reports/` 下 5 個 issue 檔記錄之 ~19 個 dataset 問題,逐一核出**目前處理狀態**(已閉環 / 待 re-verify / 待重抓),供 mac-resume from-zero sync 跑完後以當前 code(`scripts/reconcile_audit.py`)全表 re-verify 時**逐項核對閉環**用。
> 守原則 #15(實證誠實)·#10(可溯源)·#9(零幻像)。所有狀態 source-traceable：DB query｜log 行號｜git commit。
>
> 來源 issue 檔：`augur_fullsync_issues_20260610.md`(16 筆)·`_20260613.md`(3 筆)·`_20260616.md`(1 筆)·`_20260617.md`(3 筆)·`_issue_analysis_20260610.md`(GovBank/Institutional 深析)。

## 0. 關鍵前提(影響所有判定)

1. **當前 mac-resume ＝一輪 from-zero 全新 sync**(log 開頭 `PHASE 1 bootstrap → PHASE 2 seed roster → PHASE 2b FRED → PHASE 4+5 [1/83]…`),非 OptionDaily 卡死點 resume。現跑到 **[24/83] USStockPrice**;driver `/tmp/augur_mac_resume.py`、log `/tmp/augur_mac_resume.log`、PID 40071。
2. **進程用啟動時載入的舊 code**;磁碟 code 已 `git pull` 至 **73908b1**(含 vintage / per-stock / by-dim-id / 跨型別降級 / PK-null fallback)。→ **進程 log 裡的對帳 FAIL,須用當前 code re-verify 才算數**(fred EX=1 已實證即此情況、見 §2)。
3. **對帳 PASS 判據**(`reconcile.verdict`,reconcile.py:336)：`value_mismatch==0 ∧ extra_in_db==0 ∧ not incomplete`。`incomplete`＝對帳時 API 抓取未完成、未比對 →「沒比到 ≠ 比過且髒」(#15),保守判 FAIL。

---

## 1. ✅ 已處理完成(root cause 已修 + 重抓 PASS,實證閉環)

| dataset | 原 issue(來源) | root cause / 修正 | 現況實證 |
|---|---|---|---|
| `TaiwanStockGovernmentBankBuySell` | EX=412111(analysis) | `_key` 用 `str()` vs 值比對 `_norm()` 不一致(寬 PK 含數值欄)→ 改 `tuple(_norm(...))` (reconcile.py:50) | log [1/83] ✅ PASS、DB 13,749,650 列 |
| `TaiwanFuturesDaily` | exception `numeric "200710/200711"`(0610) | schema 跨型別降級 `e95cec1`(混合值域 ALTER 為字串) | log [20/83] ✅ PASS、DB 5,782,918 列 |
| `TaiwanOptionDaily` | exception `numeric "201211W4"`(0610) | 同上 `e95cec1` | log [21/83] ✅ PASS、DB 33,734,019 列 |
| `TaiwanStockMonthRevenue` | EX=7(0610) | per-stock 對帳 `e8ef8c4`(對齊抓取端點) | log [13/83] ✅ PASS、DB 474,246 列 |
| `TaiwanDailyShortSaleBalances` | EX=68(0616) | 同上 `e8ef8c4` | log [3/83] ✅ PASS、DB 7,690,325 列 |
| `fred_series` | EX=1(0613/0617 + log PHASE 2b) | FRED vintage 容忍 `5ce3ad8`(`BAMLH0A0HYM2` 修訂日重對齊、同值 4.15) | **當前 code re-verify ✅ PASS**：matched 84,755 / VM=0 / EX=0 / vintage 容忍=1、DB 84,756 列 |

---

## 2. 🔄 root cause 已修、進程舊 code 誤報 FAIL、待統一 re-verify

| dataset | log(舊 code) | 真相 / 待驗 |
|---|---|---|
| `TaiwanStockInstitutionalInvestorsBuySell` | [5/83] FAIL VM=1 EX=0 | per-stock 對帳已修 `e8ef8c4`;殘 VM=1 疑近日修訂**真差異**(非幻像)、待 heal_by_date 重抓覆蓋為 API 當前(非 hand-patch #12)。DB 24,944,833 列 |
| `TaiwanStockNews` | [22/83] FAIL VM=0 EX=0 | =`incomplete`(對帳時 News API 抓取未完成、沒比到);News 不適合 by-date 近窗對帳 → 待確認 catalog `reconcile_scope` 或標 N/A。DB 2,482,426 列 |
| `fred_series`(同 §1) | PHASE 2b FAIL VM=0 EX=1 | **已實證**：當前 code re-verify PASS(vintage 容忍)。log FAIL 為進程舊 code、非真問題 |

> **fred 的實證即「進程舊 code 誤報」之鐵證**：同一 DB、同一 fred API,舊 code FAIL / 當前 code PASS。Institutional/News 同理需當前 code re-verify。

---

## 3. ⏳ root cause 已修、mac-resume 尚未重抓到(後段 [24/83]+,DB 多未建)

| dataset | 原 issue(來源) | 已修方式 | 待驗 |
|---|---|---|---|
| `USStockPrice` | exception `stock_id null`(0610) | market PK-null 髒列 fallback `6aa7d25`(sync.py:327) | **[24/83] 正在抓、無 exception**、DB 增長中(215+ 列) |
| `TaiwanStockSecuritiesLending` | exception `date "-1"`(0610) | schema 跨型別降級 `e95cec1` | 未建、待推進 |
| `TaiwanStockConvertibleBondDailyOverview` | exception datestyle `1911-00-0`(0610) | 同上 `e95cec1` | 未建、待推進 |
| `TaiwanFuturesFinalSettlementPrice` | exception `numeric "202101W1"`(0610) | 同上 `e95cec1` | 未建、待推進 |
| `USStockInfo` | EX=2(0610) | 待 by-date/scope re-verify | DB 16,971 列、待 re-verify |
| `GoldPrice` | VM=0 EX=0(0610) | 疑 incomplete、待 scope re-verify | 未建、待推進 |
| `TaiwanStockTotalReturnIndex` | VM=0 EX=0(0610) | 同上 | 未建、待推進 |
| `TaiwanFuturesDealerTradingVolumeDaily` | EX=154449 MIS=154449(0610) | 疑 reconcile_scope 範圍差(by-date 含非 roster)、待 scope 對齊 | 未建、待推進 |
| `TaiwanOptionDealerTradingVolumeDaily` | EX=25858 MIS=25858(0610) | 同上 | 未建、待推進 |
| `GovernmentBondsYield` | EX=364(0610) | 待 by-dim-id/scope re-verify | 未建、待推進 |
| `TaiwanStockMarginShortSaleSuspension` | VM=1(0610) | 待 re-verify | 未建、待推進 |

---

## 4. root cause 修正 commit 索引(可溯源 #10)

| commit | 修什麼 | 對應 issue 類 |
|---|---|---|
| `e95cec1` | schema `ensure_table` 跨型別降級(混合值域自動 ALTER 為字串) | 全部 numeric/date exception(FuturesDaily/OptionDaily/SecuritiesLending/ConvertibleBond/FinalSettlement) |
| `6aa7d25` | market PK-null 髒列 fallback + Info-roster 維度 id | USStockPrice stock_id null |
| `5ce3ad8` | FRED vintage 容忍 | fred_series EX=1 |
| `e8ef8c4` | per-stock 對帳對齊抓取端點 | roster-scoped 表假 VM(MonthRevenue/ShortSaleBalances/Institutional) |
| `7ff03f9` | by-dim-id 對帳 + catalog `reconcile_scope` 對齊 fetch_mode | by-dim-id 表(CrudeOil/ExchangeRate)+ scope 範圍差類 |
| `184cd7d` | optimal_mode 國際股 src=none 走 by-date | 國際股漏抓(UK/Europe/US/Japan) |
| reconcile.py:50 | `_key` 改 `tuple(_norm(...))` | GovBank 寬 PK 數值假 EX |

---

## 5. 誠實結論 + 下一步

**結論**：早期 exception / 對帳 FAIL 的 **root cause 已幾乎全數修正並 commit**;已重抓的全 PASS;fred EX=1 當場實證已 PASS。**但「全部 issue 閉環」尚不能宣稱**——① mac-resume 才 [24/83]、§3 約 10 個 issue 表還沒重抓到;② 進程用舊 code、§2 的 Institutional/News 等需用當前 code re-verify 才能定論。

**下一步(待 mac-resume from-zero 跑完、勿與正在跑的 sync 並發打 FinMind #24)**：
1. `scripts/reconcile_audit.py` 全表 re-verify(含 vintage / per-stock / by-dim-id 新對帳)→ §2 §3 逐項核對。
2. Institutional 殘 VM heal_by_date 重抓覆蓋為 API 當前(非 hand-patch #12);News 確認 `reconcile_scope`(by-date 近窗不適用 → 標 N/A 或改 scope)。
3. 全表 PASS → 解凍 F2/F3 → F3 models + evaluation(下一主階段)。

> 放量 / commit / push 一律須用戶明示授權。clean-room #16：零參考 stock_backend。
