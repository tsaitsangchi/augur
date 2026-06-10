# augur 全市場全量 sync 問題記錄 (2026-06-10)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `TaiwanStockGovernmentBankBuySell` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=412111 MIS=412111 |
| `TaiwanStockInstitutionalInvestorsBuySell` | 對帳 FAIL（疑幻像/不一致） | VM=3 EX=0 MIS=2627750 |
