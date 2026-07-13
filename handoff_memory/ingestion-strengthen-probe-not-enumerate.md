---
name: ingestion-strengthen-probe-not-enumerate
description: "抓取唯一資料本質排除=日(#4)；需特殊維度id不排除→補通用多維度抓取；OUT_OF_UNIT規模物理不可行2026-06-16證偽→BACKFILL_DEFERRED(分點/權證/鉅額皆實證可抓、僅backfill scope待決)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 535524f8-f10a-43be-8ee8-7e88ab8d3ccf
---

augur 抓取範圍判準（**入憲 v1.4.0**，原則 #3/#4/#18 重大判準修正，2026-06-11）：

**唯一資料本質排除＝#4 日為最小單位**（intraday）。凡 API 有的**日級**真實資料皆應抓入——總經 / 衍生品(期/權) / 外股 / 商品 / 匯率 / 可轉債 / 籌碼皆有價值之情境或特徵輸入。**不以抓取維度/方式（需特殊 id）或「非個股標的」為排除理由**。資料價值決定抓不抓，抓取實作應配合（想辦法抓），不能用單一抓取條件反噬資料完整度。

**需特殊維度 id（`futures_id`/`option_id`/`cb_id`/ticker/`name`/`currency`…）→ 補通用多維度抓取**（探測 dataset 主 id 維度 + 由對應 Info/metadata 表通用列舉 id；仍無 hardcoded 白名單——「通用多維度」≠「窮舉硬編每個 dataset 特殊抓法」）。canonical-probe 對「per-stock 但僅近期有資料」者套 backward-probe 起點，修 `full_start=1990` 死點誤判（News/DividendResult 其實能 per-stock 抓）。

**`ingest.OUT_OF_UNIT`→`BACKFILL_DEFERRED`（2026-06-16「物理不可行」證偽、改名）**：3 張（券商分點/權證/鉅額）**實證皆可抓**——分點/權證走 **dedicated endpoint**（`finmind.fetch_dedicated(path, date=, data_id=)`；分點 2330 單日回 4838 列、權證 endpoint 確認 200-success）、鉅額走普通 `/data`（13 列）。退役「規模物理不可行」假分類，實為「**可抓但暫緩自動全市場 backfill**」（規模/scope[抓哪些股×哪段窗]待決＝放量決策，**非物理不可行**、非治權排除）。capability 已補（finmind.py `fetch_dedicated`/`_protected_get` 共用三層防護）；catalog 記 dedicated_url + notes；未接 sync auto-backfill（option 2 待授權）。

**Why**：用戶 2026-06-11 directive——這些都是總經/情境的真實資料，應想辦法抓，不該用「引擎只會 market/per-stock/by-date 三種」去砍資料。先前 AI 誤把「抓取實作的限制」當「資料排除理由」（曾建議排除 30 表衍生品/外股/商品），被糾正並入憲。

**How to apply**：遇 dataset 抓不到，先窮舉抓法（per-stock/by-date/by-dim-id/**dedicated endpoint**/parquet）——**幾乎都抓得到**（2026-06-16 連分點/權證/鉅額都實證可抓，曾誤判「物理不可行」被證偽）；真抓不到只有 intraday(<日，#4 資料本質排除)。規模大者（分點 per-(股,日)/權證宇宙 126K）非「不可抓」而是「**backfill scope 待決**」（`BACKFILL_DEFERRED`、放量決策）。連結 [[augur_project_overview]] [[finmind-fetch-methods]]。
