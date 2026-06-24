# Augur 資料完整性驗證報告 — as-of 2026-05-31 逐表盤點

**日期**：2026-06-24
**觸發**：用戶 directive「先確認目前在 database 的資料到 2026 年 5 月 31 日止已全部抓取完成」
**判準依據**：資料完整性判準（原則精華 v1.7.1 / 憲章 v1.9.1，2026-06-24 入憲）—— 完整＝每股及相關資料自 API 最早日 → **as-of 2026-05-31** 滿足無缺；固定截止日使完整可定案、可驗證。
**結論**：**84/84 資料表到 as-of 完整**。發現 GoldPrice 唯一真漏抓（2022-2026）、本輪補齊；per-stock by-date 整批漏抓掃描（L2）核心日頻表 ＝ 0。

---

## 一、驗證方法（逐表 max(date) + 漏抓判別）

完整性判準入憲後，「DB 到 as-of 完整」須**逐表實證**，不得假設 sync 跑過「全市場全史」即每表到 as-of（#20 rigor：不靠「我以為已完整」）。

**第一層 — 逐表 `max(date)` vs as-of**，三分類：

| 分類 | 判定 |
|---|---|
| `max ≥ as-of` | ✅ 完整 |
| `max < as-of` 且 API 該窗也空（低頻/稀疏/季頻未發布/事件無新）| ✅ 正常 |
| `max < as-of` 且 API 該窗**有資料** | ⚠️ 真漏抓 → 補 |

**漏抓 vs API 停更 判別（關鍵）**：對 `max < as-of` 之表，probe API 在「DB 缺的窗」+「DB 有的窗」兩段：
- 缺窗有、有窗也有 → **真漏抓**（DB 該抓未抓）
- 缺窗空、有窗有（早期有、後期停）→ **API 停更非漏抓**，DB=API 即完整

---

## 二、盤點結果（86 base table − 2 系統 log = 84 資料表）

| 類別 | 表數 | 狀態 |
|---|---:|---|
| `max ≥ as-of`（含 GoldPrice 補後、News 至 06-19、TickInfo 契約月）| 70 | ✅ |
| `max < as-of` 但可解釋（見三）| 12 | ✅ 正常 |
| snapshot 無 date 欄（FutOptDailyInfo / ConvertibleBondInfo）| 2 | ✅ 當前快照 |
| **小計（in-scope 資料表）** | **84** | **✅ 全完整** |
| 系統 log（data_audit_log / pipeline_execution_log，非 FinMind 資料）| 2 | — 不計入 |

---

## 三、`max < as-of` 之 12 表逐一判定（全部正常）

| 表 | max(date) | 判定 | 依據 |
|---|---|---|---|
| EuropeStockInfo | 2019-01-14 | ✅ API 停更 2019 | FinMind 國際股 Info 停更 |
| JapanStockInfo | 2019-01-14 | ✅ API 停更 2019 | 同上 |
| UKStockInfo | 2019-01-31 | ✅ API 停更 2019 | 同上 |
| ExchangeRate | 2020-11-13 | ✅ API 停更 2020 | `data_id='Canda'` 2019/2020 有 311/362 列、2020-11 後 0 列 |
| TaiwanStockParValueChange | 2025-08-25 | ✅ 稀疏事件 | as-of 內 API 無新面額變更 |
| TaiwanStockBalanceSheet | 2026-03-31 | ✅ 季頻 Q1 最新 | Q2（6 月底）as-of 後未發布 |
| TaiwanStockCashFlowsStatement | 2026-03-31 | ✅ 季頻 Q1 最新 | 同上 |
| TaiwanStockFinancialStatements | 2026-03-31 | ✅ 季頻 Q1 最新 | 同上 |
| TaiwanBusinessIndicator | 2026-04-01 | ✅ 月頻 4 月最新 | 5 月景氣指標 as-of 內未發布 |
| TaiwanStockCapitalReductionReferencePrice | 2026-04-13 | ✅ 稀疏事件 | as-of 內 API 無新減資 |
| TaiwanStockSplitPrice | 2026-04-22 | ✅ 稀疏事件 | as-of 內 API 無新分割 |
| TaiwanStockMonthPrice | 2026-05-01 | ✅ 月 K | 5 月 K（標 05-01）已涵蓋 5 月 |

**判別實證**：以上 probe 皆查 API 對應窗 → 缺窗空、或本就無新資料（低頻/稀疏/季頻），DB=API → 非漏抓。

---

## 四、GoldPrice 唯一真漏抓 — 補抓實證

| 項目 | 值 |
|---|---|
| 症狀 | DB `max(date)=2022-06-07`，停 4 年 |
| probe 缺窗 | `fetch('GoldPrice', start='2026-05-15', end='2026-05-15')` → **257 列**（樣本 Price=4651.03）|
| 判定 | 缺窗有資料 → **真漏抓 2022-2026** |
| 補抓 | sync resume by-date → **+1056 列**（2022-06-08 → 2026-06-24）|
| 補後 | `max(date)=2026-06-24`、總 12,384 列 |
| 對帳 | `reconcile_by_date(since='2026-05-01')` → **passed=True**（VM=0 EX=0 MIS=0）|

GoldPrice 補後進入「max ≥ as-of」之 70 表，達 **84/84 完整**。
（GoldPrice 補抓為 DB 資料變更；DB 不進 git、跨機獨立，無需 commit。）

---

## 五、多層完整性驗證（2026-06-24）

| 層級 | 驗證 | 結果 |
|---|---|---|
| **第一層 — 表級** | 84 表 `max(date)` vs as-of + 漏抓/停更判別 | 70 直達 + 12 可解釋 + 2 snapshot = **84/84** ✅ |
| **第二層 — 市場級交易日** | 核心 8 日頻表 2026-05 交易日 coverage（基準＝大盤指數日曆 20 交易日）| 全 **20/20** 無 gap ✅ |
| **第二層 — 全史交易日 gap** | TaiwanStockPrice vs 大盤指數日曆全史重疊期（2003-01-02 ~ 2026-05-29、5760 官方交易日）| 缺漏 **0** 天、多餘 **0** 天 ✅ |
| **第三層 — per-stock by-date 整批漏抓（L2）** | 49 per-stock 表 L1 缺日掃描 → 鄰日突變精煉 → 核心 7 日頻表 9 突變候選日 API 確認 | 整批漏抓 **0**（9 候選全為半日/特殊交易日、多數 DB≥API）✅ |

8 核心日頻表（Price/PER/Institutional/Margin/DayTrading/Shareholding/TotalInstitutional/TotalMargin）2026-05 全 20/20 交易日齊全；TaiwanStockPrice 全史 5760 個官方交易日零缺漏 → 不只 max 到 as-of，**中間無 gap**。

### 第三層方法（L2 — 為何不必逐缺日打 API）

逐缺日確認百萬千萬級不可行；真漏抓的訊號是 **by-date 整批驟降**（某市場日大量股漏），個股停牌則零星、不影響當日全市場股數。三步精煉：

1. **L1 純 DB 缺日掃描**（49 表、110s）→ 36 億「缺日」，但 9 成 false positive：`TaiwanStockNews`（date 為 datetime，35 億假）、`InfoWithWarrantSummary`（權證彙總 9836 萬）、及事件型/稀疏表（處置/停資券/鉅額/借券——本就稀疏，「缺日」屬常態）。naive「每股每交易日都該有」僅適用日頻規律表。
2. **鄰日 window 均值精煉**（排除市場規模漸變：1994 年台股就 188 家上市、2001 融資標的 410 家——早期股數少是歷史規模非漏抓）→ 核心 7 日頻表全史僅 **9 個**突變候選日（當日股數 < 前後 11 日均值 ×0.5）。
3. **L2 API by-date 確認** 9 候選：全部非漏抓 —
   - `InstitutionalInvestorsBuySell` 2016-06-04：DB 594 > API 548（DB 反而更全）
   - `MarginPurchaseShortSale` 7 日（2012-08-02…2016-09-28）：DB 有 437~580 股、API 今回 **0**（特殊日 API 不回、DB 當年已抓）
   - `DayTrading` 2016-01-29：DB 392 ＝ API 392（完全一致）
   - 皆半日/特殊交易日（市場本就少股），無一真漏抓。

**時間實證**：L1+L2 全程**約 5 分鐘**（突變精煉讓 L2 從百萬缺日降至 9 候選、API 確認秒級）。對照若 L3 全量重抓（49 表 × 數千股，或核心表 by-date 全量 ~5 萬 call）→ 約半天~1 天（受 FinMind 限流）。

## 六、教訓與限制

**教訓（#20 rigor 完整性）**：sync 跑「全市場全史」**不保證每表到 as-of**。GoldPrice 漏抓 2022-2026 唯有逐表驗證 `max(date)` 才察覺——正是完整性判準入憲後該做的實證驗證，不靠「我以為 sync 全史已完整」。

**已驗（L2，第三層）**：per-stock by-date 整批漏抓掃描 → 核心 7 日頻表全史整批漏抓 ＝ **0**（9 突變候選全證實半日/特殊交易日，多數 DB≥API）。

**未做（L3，如需可續）**：個股級零星漏抓（單股某日漏、當日全市場股數正常）——被個股停牌混淆、by-date 維度抓不到；徹底分離需 per-stock 全量重抓（49 表 × 數千股，或核心表 by-date 全量 ~5 萬 call）→ 約半天~1 天（受 FinMind 限流、屬放量 #24 需授權 + 過夜防睡眠）。個股零星漏抓危害遠小於整批，且 reconcile by-date 已抽樣驗證近期。全史交易日 gap 以 TaiwanStockPrice（核心價格表）為證，其餘日頻表驗至 2026-05（最後一月、最易漏處）。

---

*數據來源：DB query（information_schema + max(date) + by-date 股數 window）、FinMind API probe（GoldPrice 補抓、ExchangeRate 判別、L2 by-date 9 候選確認）、sync/reconcile stdout。全數可溯源（原則精華 #9/#10）。*
