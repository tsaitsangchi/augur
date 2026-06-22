⚠️ **SUPERSEDED** by [`augur_issue_consolidated_20260622.md`](augur_issue_consolidated_20260622.md)。本檔為 sync milestone(疑 Mac 機 84 表完整);**本機 WSL2 實證 45 表缺**(見 consolidated §0、§2.A)。接續事項已併入 consolidated §2-§4。

---

# augur 全市場全量 sync 完成 + 接續記錄 (2026-06-22)

> 🎯 **這份在做什麼**：記錄 from-zero/`--new-only` 全 83 dataset sync 達成里程碑（in-scope 84 表 100% 完整）+ sync 完接續（heal / re-verify / deferred）狀態與本次發現的 #8 記錄缺陷。
> 守原則 #7(對帳)·#8(漏抓 heal)·#15(完整性實證)·#24(限速)。

## 一、sync 完成里程碑（2026-06-21 23:16、總 1518min ≈ 25hr）

- **全 83 dataset sync DONE**：log `DONE 19 sync / 19 對帳 PASS / 64 已有跳過`。
- **excluded=f 全 84 表 100% 完整**（待補 0、psql 實證 `count(*) FILTER (n_live_tup=0) = 0 / 84`）。
- **3 sponsor 趕上 6/24 token 到期**：

| sponsor 表 | 列數 | 抓法 |
|---|---|---|
| TaiwanStockBlockTrade | 56,653 | per-stock（最後一表收尾） |
| TaiwanStockLoanCollateralBalance | 5,255,371 | per-stock |
| TaiwanStockInfoWithWarrantSummary | 215,923 | roster-scoped |

## 二、cooldown 漏抓（#8 機制實戰首次捕獲）

per-stock 大表貼頂撞 403 → `QUOTA_COOLDOWN` → `max_retries` 用盡漏股，`_per_stock_sync` 收集 `failed_ids` 記 ISSUES_MD：

| 表 | 漏股 | heal 狀態 |
|---|---|---|
| TaiwanStockPriceLimit | 20 | ✅ heal 補回（107,694 列、殘 failed 0） |
| TaiwanStockLoanCollateralBalance | 11 | ✅ heal 補回（8 股有資料、殘 failed 0） |
| TaiwanStockBlockTrade | 190 | ⚠️ 清單截斷 → 改全 roster resume heal（批 A 補） |

## 三、⚠️ #8 failed_ids 記錄缺陷（本次發現、#15 自我糾錯）

- **現象**：`full_market_sync.issue()` 記 `failed_ids[:30]` 且 markdown 寫入截斷 → BlockTrade 190 股行止於 `'2`（無閉合 `]`）→ heal 腳本 `\[[^\]]*\]` regex parse 不到、且清單本就殘缺（只前 ~20 個）。
- **正解**：**per-stock 漏抓表 heal 一律走全 roster resume**（`_per_stock_sync` 有資料股 resume from max、漏股從 floor 補），不依賴 `failed_ids` 清單。清單只作參考、不作 heal 依據。
- **TODO（待修 code）**：`issue()` 不截斷 list；或 per-stock 漏抓改記「需全 roster heal」旗標而非逐股清單。

## 四、sync 完接續（2026-06-22 啟動、用戶授權「自主全跑」）

- **批 A heal**（`/tmp/augur_heal_all.py`、`caffeinate` 背景、resume-safe）：cooldown 漏股 + 重啟 `--new-only` 跳過致不完整 3 表（[59] ConvertibleBondDailyOverview by-date 補後段[DB 僅到 2010-03-02]、[63] MonthPrice、[64] WeekPrice per-stock 全 roster）。
- **批 B**：全 84 表 `scripts/reconcile_audit.py` re-verify → 核 9 對帳 FAIL 閉環（GoldPrice 聚合 / News coverage / Institutional per-stock / GovBonds by-dim-id / fred vintage / Dealer EX≡MIS PK probe / USStock heal / [62] MarginMaintenance unsettled）。
- **批 C**：deferred 3 表（分點 TradingDailyReport / 權證 WarrantTradingDailyReport / 券商別鉅額 BlockTradingDailyReport）probe（單股單日 #25：fetch_dedicated 吃不吃 start_date 範圍 → 決定可行性）+ 抓（趕 6/24）→ 移出 BACKFILL_DEFERRED + catalog excluded=false + doctrine。

接續完成判據：全 84 表對帳乾淨 + deferred 3 表落地 → 解凍 F2/F3（下一主階段：models + evaluation）。
