# FRED 資料源完整研究 (2026-06-11)

augur 第二資料源（FRED — Federal Reserve Economic Data，St. Louis Fed）全貌——總經因子來源（殖利率曲線/利率/通膨/失業/油/匯率…）。
**source-traceable（#15）**：fred.stlouisfed.org WebSearch + `api.stlouisfed.org` live probe（augur key 實證）+ augur `fred.py`。

---

## 一、API Endpoints（base：`https://api.stlouisfed.org/fred`）

| endpoint | 用途 | 關鍵參數 |
|---|---|---|
| `/series` | series metadata（標題/頻率/單位/季調/起訖）| `series_id` |
| `/series/observations` | **觀測值（augur 抓取用）** | `series_id`, `observation_start/end`, **`realtime_start/end`（#8 point-in-time、取當時可見值/vintage）**, `units`, `frequency`, `aggregation_method`, `limit`(上限 100000) |
| `/series/search` | **依關鍵字搜尋 series（series-id 來源）** | `search_text`, `limit`, `order_by` |
| `/series/updates` | 近期更新的 series | — |
| `/series/vintagedates` | 歷史修訂日（vintage）| `series_id` |
| `/category` `/category/children` `/category/series` | **類別階層瀏覽 + 列該類 series（series-id 來源）** | `category_id`（root=0）|
| `/releases` `/release/series` | 發布（328 個）+ 該發布之 series | — |
| `/sources` `/source/releases` | 資料來源（120 個）| — |
| `/tags` `/series/search/tags` | 非階層 metadata 標籤 | — |

- 回應格式：`file_type=json`（或 xml）。所有 endpoint 共用 `api_key`。
- 完整約 **31 endpoints / 5 大類**：**Category**(category/children/related/series/tags)、**Release**(releases/release/series/dates/tables)、**Series**(series/observations/search/categories/release/tags/updates/**vintagedates**)、**Source**(sources/source/releases)、**Tag**(tags/related_tags/series) + GeoFRED(地圖、另一 API)。augur 用 `/series/observations`；#18 列舉用 `/series/search`+`/category/series`。

## 二、認證與限速

- **api_key**：32 字元小寫英數，**免費註冊**（fred.stlouisfed.org/docs/api/api_key.html）。augur 用 `config.FRED_API_KEY`（live probe 確認存在、有效）。
- **限速**：**120 req/min**（=7200/hr）；超限 **HTTP 429**（augur `fred.py` 已 429 退避重試）。
- **無 tier 分級、無訂閱到期**（與 FinMind 不同）——公開政府資料、全免費全可取。

## 三、涵蓋（live probe 實證）

- **844,000 經濟時間序列**、**120 sources**、**328 releases**、**8 大類 / 80 子類**。
- 8 大類（`category/children?category_id=0`）：Money/Banking/Finance(32991)、Population/Employment/Labor(10)、National Accounts(32992)、Production/Business(1)、Prices(32455)、International(32263)、U.S. Regional(3008)、Academic(33060)。
- 長歷史：DGS10 自 **1962-01-02**（60+ 年）。

## 四、series 結構

- **metadata**（`/series`）：`id, title, frequency`(Daily/Weekly/Monthly…), `units`(Percent…), `seasonal_adjustment`, `observation_start/end`。
- **observations**（`/series/observations`）：每列 `realtime_start, realtime_end, date, value`；缺值 `value="."`。
- **augur `fred.py` 落地**：只取 `(series_id, date, value)`——**補 series_id**（FRED 回應不含、補後才成 `(series_id,date)` 複合 PK #2）；**丟 realtime_start/end**（vintage metadata、隨查詢日變、存了破壞冪等對帳）；**`"."`→NULL**（無值非真實值、不違 #1）。

## 五、series-id 來源（#18，對映 FinMind `/datalist`）

FRED series-id（如 `DGS10`/`T10Y2Y`/`UNRATE`）全集來源——**動態 API，非臆測白名單**：
- **`/series/search?search_text=`**：關鍵字搜尋（實證「10-year treasury constant maturity」→ 79 個 series）。
- **`/category/series?category_id=`**：列某類別下全部 series（配 `/category/children` 階層展開）。
- **`/tags` / `/series/search/tags`**：標籤交集篩選。
- augur 現況：`FRED_SERIES`（12 個人選標準總經因子：T10Y2Y/T10Y3M/DGS10/DGS2/FEDFUNDS/UNRATE/CPIAUCSL/INDPRO/VIXCLS/DTWEXBGS/DCOILWTICO/BAMLH0A0HYM2）——**由 feature 設計決定、非窮舉全 844K**（YAGNI）；要擴充時用 search/category 動態列舉。

## 六、augur 現有用法（`src/augur/ingestion/fred.py`）

- 薄 client：`fetch(series_id, start_date, end_date)` → `series/observations`。
- 429 退避重試；api_key/series_id 錯 → 立即 `FredError`。
- **無主動節流**（不同 FinMind `_pace`）——因 120/min 寬鬆 + augur 只抓 12 series（量小）；若未來放量列舉須補節流。
- resume：`sync_fred` 每 series 從 DB `max(date)` 續（同 #6）。

## 七、對 augur 的關鍵啟示

1. **series-id 來源（#18）**：FRED 走 `/series/search` + `/category/series`（對映 FinMind `/datalist`）——維度 id 全集有動態權威來源、非臆測。
2. **限速**：120/min 寬鬆、無 tier、無到期——FRED 抓取**無 FinMind 的 6-24 到期壓力**；總經因子可從容全史。
3. **vintage/realtime（#8 原生解法、非無解）**：FRED 總經數據事後修訂（vintage）；augur 現只存最新值（去 realtime）守冪等——但 **FRED API 原生支援 point-in-time**：`/series/vintagedates?series_id=` 取某 series 全部修訂日、`/series/observations?realtime_start=YYYY-MM-DD&realtime_end=` 取「**該日當時可見值**」（或 ALFRED）。**留意**：用「最新修訂值」做歷史回測 = look-ahead（反 #8）；augur 建模若要嚴格 PIT，**已有 API 解法**（vintagedates + realtime_start）、須評估改抓 vintage。
4. **長歷史**：多數 series 數十年（DGS10 自 1962）；`full_start=1990` 為下界、FRED 回實際範圍（同 #18 辨明）。
5. **observations 參數**：FRED 原生支援 `units`(差分/變化率)、`frequency`+`aggregation_method`(降頻)——augur 目前抓原始、未來特徵可善用（但對映關係須記錄、防 #8 洩漏）。

> ⚠️ **#8 警示**（最重要）：FRED 總經數據**事後修訂**頻繁，用最新值回測 = look-ahead bias。嚴格 point-in-time 須走 vintage（ALFRED）。此為 augur 建模階段必須正視之 anti-leakage 課題。
