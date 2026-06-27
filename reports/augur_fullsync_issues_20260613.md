⚠️ **SUPERSEDED** by [`augur_issue_consolidated_20260622.md`](augur_issue_consolidated_20260622.md)。本檔為 sync driver 持續寫入之最近 issue log(2026-06-13 起);內容隨下次 sync 跑會被覆寫(`full_market_sync.py` 首行 `open("w")`)。

---

# augur 全市場全量 sync 問題記錄 (2026-06-13)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `TaiwanStockInstitutionalInvestorsBuySell` | 對帳 FAIL（疑幻像/不一致） | VM=33 EX=0 MIS=0 |
| `TaiwanFuturesSpreadTick` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=390 MIS=0 |
| `TaiwanStockNews` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=0 MIS=0 |
| `TaiwanStockInfo` | 0 列 | by-date（tier 限制/空/需特定參數） |
| `TaiwanFuturesDealerTradingVolumeDaily` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=177018 MIS=177018 |
| `TaiwanOptionDealerTradingVolumeDaily` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=31085 MIS=31085 |
| `TaiwanStockDayTrading` | 對帳 FAIL（疑幻像/不一致） | VM=44 EX=0 MIS=0 |
| `TaiwanStockTotalReturnIndex` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=0 MIS=0 |
| `TaiwanStockMarketValue` | cooldown漏抓 | 6 股 rows=None: ['1515', '2066', '2067', '2543', '2545', '2856'] |
| `TaiwanStock10Year` | cooldown漏抓 | 2 股 rows=None: ['6879', '7922'] |
| `TaiwanTotalExchangeMarginMaintenance` | 對帳 FAIL（疑幻像/不一致） | VM=1 EX=0 MIS=0 |
