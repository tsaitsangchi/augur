# augur 全市場全量 sync 問題記錄 (2026-06-10)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `TaiwanStockGovernmentBankBuySell` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanStockBlockTradingDailyReport` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanStockTradingDailyReport` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
| `TaiwanStockWarrantTradingDailyReport` | date-based/需特定id | per-stock-non-canonical（需 by-date 或 data_id 專路徑） |
