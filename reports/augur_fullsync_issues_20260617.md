# augur 全市場全量 sync 問題記錄 (2026-06-13)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `fred_series` | 對帳 FAIL | VM=0 EX=1 |
| `TaiwanStockInstitutionalInvestorsBuySell` | 對帳 FAIL（疑幻像/不一致） | VM=1 EX=0 MIS=0 |
| `TaiwanStockNews` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=0 MIS=0 |
