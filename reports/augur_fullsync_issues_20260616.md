⚠️ **SUPERSEDED** by [`augur_issue_consolidated_20260622.md`](augur_issue_consolidated_20260622.md)。本檔保留為**歷史**(2026-06-16 sync ShortSale EX=68 之原始 log;root cause 已修 commit `e8ef8c4` per-stock 對帳)。

---

# augur 全市場全量 sync 問題記錄 (2026-06-13)

實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。

| dataset | 類型 | 細節 |
|---|---|---|
| `TaiwanDailyShortSaleBalances` | 對帳 FAIL（疑幻像/不一致） | VM=0 EX=68 MIS=0 |
