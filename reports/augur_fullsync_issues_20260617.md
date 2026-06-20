# augur 全市場全量 sync 問題記錄 (2026-06-13)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `fred_series` | 對帳 FAIL | VM=0 EX=1 |
| `TaiwanStockInstitutionalInvestorsBuySell` | 對帳 FAIL（疑幻像/不一致） | VM=1 EX=0 MIS=0 |
| `TaiwanStockNews` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=0 MIS=0 |
| `USStockPrice` | 對帳 FAIL（疑幻像/不一致） | VM=12765 EX=0 MIS=12102 |
| `GoldPrice` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=36 MIS=9997 |
| `USStockInfo` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=3 MIS=6 |
| `TaiwanFuturesDealerTradingVolumeDaily` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=170796 MIS=170796 |
| `TaiwanOptionDealerTradingVolumeDaily` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=29365 MIS=29365 |
| `GovernmentBondsYield` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=442 MIS=0 |
| `TaiwanStockTotalReturnIndex` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=0 MIS=0 |
