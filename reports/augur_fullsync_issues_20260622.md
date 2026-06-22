# augur 全市場全量 sync 問題記錄 (2026-06-13)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `TaiwanFuturesDealerTradingVolumeDaily` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=172173 MIS=172173 |
| `TaiwanOptionDealerTradingVolumeDaily` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=29623 MIS=29623 |
