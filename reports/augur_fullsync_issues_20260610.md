# augur 全市場全量 sync 問題記錄 (2026-06-10)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `TaiwanStockMonthRevenue` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=7 MIS=0 |
| `TaiwanFuturesDaily` | exception | syntax for type numeric: "200710/200711" LINE 1: ...0,1.13,3,9750.0,44,'position'),('2007-10-08','TX','200710/20...                                                              ^   |
| `TaiwanOptionDaily` | exception | nput syntax for type numeric: "201211W4" LINE 1: ....1,0.1,1,0.0,1093,'position'),('2012-11-21','TXO','201211W4'...                                                              ^   |
| `TaiwanStockNews` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=0 MIS=0 |
| `USStockPrice` | exception | _id" of relation "USStockPrice" violates not-null constraint DETAIL:  Failing row contains (1997-09-30, null, 1.000000, 18.340000, 18.340000, 17.610000, 17.610000, 22998.000000).   |
| `TaiwanStockSecuritiesLending` | exception | : invalid input syntax for type date: "-1" LINE 1: ...,NULL,0),('2003-12-13','2323','定價',200,4.0,25.4,'-1',0),('...                                                              ^   |
| `GoldPrice` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=0 MIS=0 |
| `USStockInfo` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=2 MIS=0 |
| `TaiwanFuturesDealerTradingVolumeDaily` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=154449 MIS=154449 |
| `TaiwanOptionDealerTradingVolumeDaily` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=25858 MIS=25858 |
| `GovernmentBondsYield` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=364 MIS=0 |
| `TaiwanStockTotalReturnIndex` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=0 MIS=0 |
| `TaiwanStockConvertibleBondDailyOverview` | exception | 9-04-12','2009-06-10',0.0,NULL,NULL,NULL,0.0,'1911-00-0...                                                              ^ HINT:  Perhaps you need a different "datestyle" setting.   |
| `TaiwanStockMarginShortSaleSuspension` | 對帳 FAIL（疑幻像/不一致） | VM=1 EX=0 MIS=0 |
| `TaiwanFuturesFinalSettlementPrice` | exception | nput syntax for type numeric: "202101W1" LINE 1: ...ing_code", "notional_value") VALUES ('2021-01-06','202101W1'...                                                              ^   |
