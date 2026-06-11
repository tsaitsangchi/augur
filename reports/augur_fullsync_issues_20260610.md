# augur 全市場全量 sync 問題記錄 (2026-06-10)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `TaiwanStockGovernmentBankBuySell` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=412111 MIS=412111 |
| `TaiwanStockInstitutionalInvestorsBuySell` | 對帳 FAIL（疑幻像/不一致） | VM=3 EX=0 MIS=2627750 |
| `TaiwanStockBlockTradingDailyReport` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanStockTradingDailyReport` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanStockWarrantTradingDailyReport` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanStockTotalInstitutionalInvestors` | 對帳 error | TaiwanStockTotalInstitutionalInvestors: 非 JSON 回應 (HTTP 502) |
| `TaiwanStockMonthRevenue` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=433 MIS=0 |
| `CrudeOilPrices` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanExchangeRate` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `ExchangeRate` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanFuturesSpreadTick` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanFuturesDaily` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanOptionDaily` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanStockNews` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `USStockPrice` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanStockDividendResult` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanStockSecuritiesLending` | exception | : invalid input syntax for type date: "-1" LINE 1: ...,NULL,0),('2003-12-13','2323','定價',200,4.0,25.4,'-1',0),('...                                                              ^   |
| `TaiwanFutOptTickInfo` | 對帳 error | 'str' object has no attribute 'isoformat' |
