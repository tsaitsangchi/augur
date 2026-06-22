⚠️ **SUPERSEDED** by [`augur_issue_consolidated_20260622.md`](augur_issue_consolidated_20260622.md)。本檔保留為**歷史**(2026-06-17 sync cooldown 漏抓 3 表之原始 log;PriceLimit/LoanCollateralBalance heal 已 ✅、BlockTrade 待全 roster heal)。

---

# augur 全市場全量 sync 問題記錄 (2026-06-13)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `TaiwanStockPriceLimit` | cooldown漏抓 | 20 股 rows=None: ['2493', '2494', '2545', '2546', '2547', '2548', '2882B', '2947', '3018', '3019', '3020', '3021', '3022', '3027', '3028', '3029', '3030', '3031', '3036', '3071'] |
| `TaiwanStockLoanCollateralBalance` | cooldown漏抓 | 11 股 rows=None: ['1459', '1523', '1540', '1541', '1558', '1603', '2341', '2364', '2384', '2385', '2644'] |
| `TaiwanStockBlockTrade` | cooldown漏抓 | 190 股 rows=None: ['2392', '2393', '2395', '2396', '2397', '2399', '2401', '2402', '2403', '2404', '2405', '2406', '2408', '2409', '2411', '2412', '2413', '2414', '2415', '2417', '2 |
