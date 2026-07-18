---
name: fred-data-source
description: "FRED 資料源全貌——api_key 免費/120min/無 tier 無到期、series-id 來源=search+category、#8 vintage 修訂洩漏警示；完整研究見 report"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 535524f8-f10a-43be-8ee8-7e88ab8d3ccf
---

augur 第二資料源 FRED（總經因子：殖利率曲線/利率/通膨/失業/油/匯率…）全貌。**完整研究**：`reports/augur_fred_research_20260611.md`。

**API**（base `api.stlouisfed.org/fred`）：`/series/observations`（augur 抓取）、**`/series/search` + `/category/series`（series-id 來源 #18，對映 FinMind `/datalist`）**、`/series`（metadata）、`/releases`(328)/`/sources`(120)。**api_key 32 字免費**、**限速 120/min（429 退避）**、**無 tier 分級、無到期**（與 FinMind 不同、無 6-24 壓力）。涵蓋 **844K series**、8 大類/80 子類。

**augur `fred.py`**：observations only、補 series_id 成 `(series_id,date)` PK、**丟 realtime/vintage**、`"."`→NULL；`FRED_SERIES`=12 人選標準總經因子（非窮舉、YAGNI）；無主動節流（120/min 寬鬆、量小）。

⚠️ **#8 vintage 洩漏警示——2026-07-17 實查已解除**:原稱「fred.py 只存最新值」為**材料性錯誤**(會誤導重造已存在的 reader)。實況:`fred.py:42-64` 早已支援 `vintage=True`(ALFRED realtime_start)、`fred_series` PK **含 realtime_start**、**100,572 列真 vintage 已落地**、`ingest._fred_pk_ok` 加了硬閘。原理(修訂值=look-ahead)仍正確,但**已被實作解決、非待辦**。連結 [[augur_project_overview]] [[finmind-data-source]]。
