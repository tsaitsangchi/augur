# augur 全市場全量 sync — 進度快照 / handoff (2026-06-10)

**性質**：執行中之全市場全量 sync 的 source-traceable 進度封存（供 resume / 跨機接續 / 封存點）。
**誠實聲明（#15）**：數字皆實跑來源——dataset 進度自 `/tmp/augur_fullsync.log`（程式 stdout）、
列數自 augur DB `pg_stat_user_tables`（READ-ONLY query）；**sync 執行中（未完成）**，本檔為 ~5 小時時點之快照。

## 執行狀態（~5 小時時點）
- driver：`scripts/full_market_sync.py`（背景、resume-capable、finmind 內建主動限速）
- 進度：**7/85 dataset 已處理**（[1-4] date-based 跳過 + [5-7] per-stock 載入完成），
  進行中 **[8/85] `TaiwanStockInstitutionalInvestorsBuySell` ~40%**
- 穩定性：~5 小時 **0 錯誤、0 IP re-ban**

## DB 實際列數（DB-verified，~31M 列 / 8 表）
| 表 | 列數 | #7 對帳 |
|---|---|---|
| `TaiwanStockInstitutionalInvestorsBuySell`（法人買賣超，進行中）| 12,175,992 | 待完成後驗 |
| `TaiwanStockBalanceSheet`（資產負債表）| 8,373,868 | ✅ PASS |
| `TaiwanDailyShortSaleBalances`（借券餘額）| 7,685,054 | ✅ PASS |
| `TaiwanStockFinancialStatements`（財務報表）| 2,707,505 | ✅ PASS |
| `fred_series`（總經 12 series）| 64,901 | ✅ PASS |
| `TaiwanStockInfo`（全市場名冊）| 4,139 | ✅ PASS |
| `data_audit_log`（稽核留痕）| 8,537 | — |
| `pipeline_execution_log` | 0 | — |
| **合計** | **~31,019,996** | |

## #7 無幻像 attestation（已驗證者）
roster + FRED + 3 per-stock 大表（BalanceSheet / 借券 / 財報）= **5 個 dataset 已 byte-level DB↔API
對帳 PASS（value_mismatch=0 ∧ extra_in_db=0）**——證明「抓→落地→逐 API 對帳→無幻像」在真實全量資料成立。

## 待處理（問題記錄 `reports/augur_fullsync_issues_20260610.md`，4 筆）
4 個 **date-based** 表（`GovernmentBankBuySell` / `BlockTradingDailyReport` / `TradingDailyReport` /
`WarrantTradingDailyReport`）→ 非 per-stock，canonical-2330-probe 正確跳過 → **follow-up：需 by-date
路徑補抓**（非錯誤、非幻像）。

## resume / 接續
- 中斷後：`PYTHONPATH=src venv/bin/python scripts/full_market_sync.py`（DB-driven resume，已完成股跳過、`ON CONFLICT` 冪等）。
- ⚠️ **WSL2 須確保 Windows 主機不睡**（caffeinate 無效；主機睡 → 進程死 → 需手動 re-launch 續傳）。
- 監看：log `/tmp/augur_fullsync.log` + 問題報告；2 monitors（5-min 心跳 + 問題即時警示）。
- 剩餘估計：**~40-50h**（per-stock 大表每個 ~1.7h × ~25-30 個）。

## 已知優化點（非 bug）
roster 前 **461 檔為 0-prefix ETF/債/權證**（無財報）；每個 fundamental dataset（財報/股利…）先空抓這段
（~15min/表）才到真公司（#462=`1101`）。可優化 roster「公司優先」減少前綴空跑——列未來優化，不影響正確性。
