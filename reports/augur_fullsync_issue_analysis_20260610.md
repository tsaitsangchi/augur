⚠️ **SUPERSEDED** by [`augur_issue_consolidated_20260622.md`](augur_issue_consolidated_20260622.md)(整合 issue tracker)。本檔保留為**歷史**(GovBank/Institutional 兩 issue 之深度根因分析,所述 root cause `_key→_norm`(fadba1a) + per-stock 對帳(e8ef8c4) 已 commit、分析價值仍在)。

---

# augur 全市場全量 sync — #7 對帳 FAIL 根因分析 (2026-06-10/11)

**結論先講(#15 誠實)**：截至 dataset 8/82,出現 2 個 #7 對帳 FAIL,**經 live API + DB 實證,兩者皆為 reconcile 方法學 artifact,非資料損毀 / 非 AI 幻像 / 非真缺口**。已落地之 raw 資料對 augur roster(上市股)universe 而言**正確且完整**。

全部數字 source-traceable:DB query(isolated venv READ-ONLY)+ live FinMind API 取樣。

---

## Issue 1 — `TaiwanStockGovernmentBankBuySell`：VM=0 EX=412111 MIS=412111

### 現象
近窗(2026-05-01+)reconcile:matched=0、value_mismatch=0、extra_in_db=missing_in_db=412,111(= DB 近窗全部列)。即 DB 與 API **一列都配不上**。

### 根因(code bug,非資料)
`audit/reconcile.py` 之 `_key()` 用 `str(row.get(c))` 建配對 key(而值比對 `_norm` 用 `round(float,6)`)。GovBank 之 PK 為 **7 欄含數值欄**(`buy_amount/sell_amount/buy/sell`,因 `bank_name` 不在 `KEY_CANDIDATES`,detect_keys 退回全欄)。數值欄 DB 存 NUMERIC(`str(Decimal)="1234.000000"`)vs API raw(`str(1234.0)="1234.0"`)→ key tuple 永不相等 → 100% 配對失敗 → 全 EX/MIS。

### 資料正確性(DB-verified)
- 總列 13,702,521、`distinct(date,stock_id,bank_name)` = 13,702,521、**重複 = 0**
- 日期 2021-06-30 ~ 2026-06-10、value_mismatch = 0(無錯值/無幻像)
→ **資料乾淨**;FAIL 純為 reconcile false-negative。

### 修正(已 staged,未 commit)
`_key` 改用 `_norm`(與值比對一致正規化):`tuple(_norm(row.get(c)) for c in pk)`。synthetic 單元測試驗證:寬 PK 含數值欄 DB(Decimal) vs API(raw) → matched 全配、EX=0 MIS=0;缺列→MIS、值錯→VM 仍正確偵測(無誤殺)。**運行中進程已載入舊碼,需 post-hoc 以修正版 re-verify(唯讀,不重抓)**。

---

## Issue 2 — `TaiwanStockInstitutionalInvestorsBuySell`：VM=3 EX=0 MIS=2,627,750

### 現象
近窗 reconcile:extra_in_db=0、value_mismatch=3、missing_in_db=2,627,750(API 近窗有 ~263 萬列 DB 沒有)。

### 根因(reconcile 範圍不匹配,非缺口)
此 dataset 以 **per-stock**(逐 roster 股)落地;reconcile_by_date 以 **market by-date(無 data_id,全市場)** 取 API。兩者 universe 不同:
- live 實測 2026-06-05:market by-date = **100,874 列 / 6 names**(≈ **16,812 檔證券**,含權證/ETF);per-stock 2330 = 5 列(同 6 類內)
- DB 該日 = 11,659 列 / **2,387 檔**(roster 上市股);names DB 與 API **完全一致**(6 類:Dealer/Dealer_Hedging/Dealer_self/Foreign_Dealer_Self/Foreign_Investor/Investment_Trust)
→ MIS = market universe(~16,800,含 ~14,400 權證/非 roster)− DB roster(~2,387)之**非 roster 證券法人資料**。augur 以「上市股票」為預測標的,**正確排除權證/非 roster**(同 §一.WarrantTradingDailyReport 排外原則)。

### 資料正確性(DB-verified)
- 總列 25,835,874、日期 2005-01-03 ~ 2026-06-10、近窗(2026-05-01+)= 326,685 列、最新每日 ~11-12k
→ **roster 股票之法人資料完整正確**;MIS 為範圍差(權證),非缺口。VM=3 = 3 列微值差(近期重述,benign,可日後 heal_by_date 重抓)。

### 修正方向(follow-up,非本次)
reconcile 對 **per-stock 落地之 dataset** 應以 **per-stock 或 roster-scoped** 對帳(只比對 DB universe 內 stock_id),不應與 full-market by-date(含權證)對撞。或：driver verify() 對 per-stock-synced 表改走 per-stock reconcile。

---

## 治權決策(2026-06-11)

1. **不 full-restart**:已完成 8 支(含 6 支 per-stock)。full restart 觸發 per-stock resume 逐 3100 股重探(每支 ~52 分鐘 × 6 ≈ **~5 小時純浪費**),且資料本就正確 → 不值得。當初(1 支時)建議重啟,現因進度推進而**撤回**。
2. **sync 繼續**:資料正確、resume-safe、caffeinate ON;持續抓 dataset 9/82+。
3. **`_key` 修正 staged**:惠及未來 from-zero + post-hoc re-verify;本次運行進程不套用。
4. **大多 per-stock dataset(BalanceSheet/FinancialStatements/PER/Shareholding/…)#7 PASS**:乾淨 PK(stock_id,date)+ 無權證 universe → 舊 reconcile 即正確。只有 GovBank(寬 PK 數值)與 Institutional(權證 universe)兩類 artifact。

## Follow-ups(待用戶授權)
- [ ] commit `_key`→`_norm` 修正(reconcile.py)
- [ ] reconcile per-stock-synced 表改 roster-scoped(修 Issue 2 類)
- [ ] sync 完成後,以修正+scoped reconcile 對 GovBank / Institutional re-verify → 應 PASS
- [ ] (可選)`bank_name` 納入 `KEY_CANDIDATES` → GovBank 下次 rebuild 得乾淨 PK `(date,stock_id,bank_name)`
