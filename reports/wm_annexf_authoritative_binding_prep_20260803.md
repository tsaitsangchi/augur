# Annex F 六概念｜權威表徵採認備料（Steward 圈選單）——2026-08-03

> **性質**：WM.36 合規弧 M3 之**採認備料**（`AUGUR-MC v1.6 §8.1`：AI 僅**草擬、比對、呈案**；**本報告零條文解釋**——凡條文歧義一律列 §7 問題待 Steward）。
> **全程唯讀**：本輪零 DDL、零 DB 寫入、零 commit、零 systemctl；`decided_by`／`decided_at` 一欄未填（never-type-human-signature）。SQL 範本僅以 `EXPLAIN`（無 `ANALYZE`）於 `BEGIN…ROLLBACK` 內**乾解析**，未執行任何 DML——唯讀證明見 §6。
> **目的**：把 Annex F 六條之採認從「研究」壓成「圈選」。六概念之 `authoritative_binding_id` 現全 NULL ⇒ `resolve()` **0/6 全 fail-closed**（§1.3 實跑）＝M3 絞殺的物理起點在 Steward 附卷採認。
> **上游 SSOT**：`reports/wm3536_vendor_registry_plan_20260802.md`（設計＋§11 逐檔清單）／`reports/w2_20260801/WM_M1_pk_vs_appendonly_20260802.md`（丙案裁決）／`specs/WORLD-MODEL-SPECIFICATION.md`（WM.14／WM.15／WM.32／WM.35／WM.36／WM.37／Annex A／Annex F）。
> **數字時點**：全部為 **2026-08-03 執行時 live 唯讀現查**（psql／`data_audit_log`／模組 `--check`），非抄自既有報告；指令附於各節，可獨立重跑。

---

## §0 判準原文（逐字，供圈選時對照；本節只引不釋）

> **WM.14**（`specs/WORLD-MODEL-SPECIFICATION.md:183-186`）：「每一世界事實在系統內**必須**有且僅有一個權威 Representation。……**可判定判準**：Registry（WM.36）中該世界概念之權威表徵欄**恰解析至一個**表徵載體者為合規；**解析至零個或多個者違反本條**。」
> **WM.15**（:188-191）：「凡兩個以上 Observation Channel 描述同一世界事實——含原始觀測與其**衍生調整觀測**……其**同一性宣告**與**擇用規則**必須**一次性作成為單一宣告**……消費端必須引用世界概念，**不得**各自內嵌擇用規則。」
> **WM.35**（:336-340）：「unmapped 或未登錄映射之通道，其資料**僅具 Observation 地位**——得保存、對帳、追溯，**不得**被消費為 Representation 或 Knowledge 之依據。」
> **WM.36**（:344-358）：登錄七欄＝「世界概念／歸類（閉集）／**通道映射（粒度至欄位級、一對多**）／**權威表徵指定（WM.14）**／通道時間屬性雙宣告／provenance／定案性述語」；「任何消費世界模型之模組……**不得**以來源位置字面（**供應商表名、欄名、series 識別碼**）直接繫結」；「**可判定判準（登錄完成）**：登錄項七欄俱全且各欄可解析者為登錄完成；**unmapped 為顯式合法過渡態**。」
> **WM.32／A.37**（:294／:601）：定案性述語形式為「**相對截止日之可判定述語**」；未登錄者「依 WM.32 缺省規則推定 non-final」。
> **Annex F 地位聲明**（:939）：「本附件……屬系統狀態之初始化素材，**非規範條文**；其**採認與登錄由 Steward 附卷裁定**。」

---

## §1 現況親驗（2026-08-03）

### 1.1 Registry 三表列況

```bash
set -a && . ./.env && set +a && PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
SELECT (SELECT count(*) FROM world_concept) ident,
       (SELECT count(*) FROM world_concept_version) ver,
       (SELECT count(*) FROM world_concept_version WHERE superseded_at IS NULL) cur,
       (SELECT count(decided_by) FROM world_concept_version) signed,
       (SELECT count(authoritative_binding_id) FROM world_concept_version) auth,
       (SELECT count(*) FROM world_channel_binding) bind,
       (SELECT count(*) FROM world_channel_binding WHERE superseded_at IS NOT NULL) bind_sup;"
```

| 身分列 | 版本列 | 現行列 | **已親簽（decided_by 非空）** | **已指定權威表徵** | 通道列 | 已 supersede 之通道列 |
|---|---|---|---|---|---|---|
| 6 | 6 | 6 | **0** | **0** | 98（mapped 10／unmapped 88） | **0** |

⇒ 版本化機制自建表以來**從未被使用過**（`superseded_at` 全 NULL）；本次採認即**第一次修訂**（形制影響見 §3.2）。

### 1.2 十列 mapped 通道（即六概念之全部候選；`source_column` 全為 NULL＝表級暫登）

| binding_id | 概念 | source_table | role | map_note（provenance） |
|---|---|---|---|---|
| 75 | tw.daily_bar | `TaiwanStockPrice` | observation | Annex F-1 原始成交價通道 |
| 81 | tw.daily_bar | `TaiwanStockPriceAdj` | **derived** | Annex F-1 含 CorporateAction 調整之衍生通道（WM.15） |
| 25 | tw.corporate_action.ex_dividend | `TaiwanStockDividend` | observation | Annex F-2 股利通道 |
| 48 | tw.corporate_action.ex_dividend | `TaiwanStockDividendResult` | observation | Annex F-2 除權息結果通道 |
| 12 | tw.fx.twd_usd | `fred_series` | observation | Annex F-3 外國經濟資料庫對應 series（**註記內容經本輪實證為誤，見 §3.3**） |
| 32 | tw.fx.twd_usd | `TaiwanExchangeRate` | observation | Annex F-3 本國供應商匯率資料集 |
| 4 | tw.trading_calendar | `TaiwanStockTradingDate` | observation | Annex F-4 交易日通道 |
| 28 | tw.roster_membership | `TaiwanStockInfo` | observation | Annex F-5 基本資訊快照通道 |
| 2 | tw.roster_membership | `TaiwanStockDelisting` | observation | Annex F-5 下市通道（成員資格時間函數輸入；A.2） |
| 3 | tw.delisting | `TaiwanStockDelisting` | observation | Annex F-6 下市通道（A.25） |

（88 列 unmapped 為顯式合法過渡態（WM.36 可判定判準原文）。本輪逐列檢視 88 個表名後，**未發現**任何一列可直接改列為上開六概念之候選；最接近而**經判讀為不同世界事實／不同粒度**者六張，一併列出供覆核：`ExchangeRate`（binding 66；Taiwan `InterbankRate` 止於 2020-11-12，見 §2.3）、`TaiwanStockSuspended`（暫停買賣＋復牌 `resumption_date`，非下市；2,285 列／2025-03-07 起）、`TaiwanStockKBar`（分鐘 K，粒度非日級，A.34）、`TaiwanStockMonthPrice`／`TaiwanStockWeekPrice`（月／週聚合，粒度非日級）、`TaiwanStockCapitalReductionReferencePrice`／`TaiwanStockSplitPrice`／`TaiwanStockParValueChange`（減資／分割／面額變更＝**CorporateAction 家族之其他事件**，非 Annex F-2 之「除權息」；若 Steward 認其與除權息為同一世界事實 ⇒ WM.15 待決同一性存量，見 §2.2 證偽條件 (iii)）。此判讀為 AI self-reported，未經 Steward 採認。）

### 1.3 解析現況（唯讀實跑）

```
$ venv/bin/python -m augur.catalog.world_concept --check
── Registry 現況：概念 6 現行列／通道 98 現行列（mapped 10）──
  ✗ tw.corporate_action.ex_dividend：…未指定權威表徵（authoritative_binding_id IS NULL）
  ✗ tw.daily_bar / ✗ tw.delisting / ✗ tw.fx.twd_usd / ✗ tw.roster_membership / ✗ tw.trading_calendar（同上）
  ⚠ 6/6 概念尚不可消費——消費端呼叫 resolve() 會 fail-closed 拋例外（這是正確行為，非 bug）。
```

### 1.4 候選通道之資料現況（本輪 psql 現查；**非抄既有報告**）

| 供應商表 | 列數 | 期間（min→max date） | 維度基數 | 最近落地（`data_audit_log`） | `dataset_catalog.attestation_mode` |
|---|---|---|---|---|---|
| `TaiwanStockPrice` | **12,350,335** | 1994-09-13 → 2026-07-31 | 55,674 stock_id | 2026-08-01 17:54 upsert **41,876 列** | `byte` |
| `TaiwanStockPriceAdj` | **11,190,394** | 1992-01-04 → 2026-07-31 | 3,127 stock_id | 2026-08-01 17:54 upsert **2,803 列** | **`restating`** |
| `TaiwanStockDividend` | **2,411** | 2005-09-03 → **2026-08-23**（13 列未來日） | 2,411 stock_id（**每股恰 1 列：max=min=avg=1**） | **2026-06-19**（44 日未更） | **`restating`** |
| `TaiwanStockDividendResult` | **31,097** | 2003-07-07 → 2026-07-31 | 2,376 stock_id | 2026-08-01 17:48 | `byte` |
| `TaiwanStockDelisting` | **344** | 2001-01-20 → 2026-07-28 | 344 stock_id | 2026-08-01 17:47 upsert 1 列 | `cadence` |
| `TaiwanStockInfo` | **4,296** | 2020-06-03 → 2026-07-31 | 3,128 stock_id／**僅 254 個相異日**（2026-07-31 一日即 3,305 列） | 2026-08-01 17:48 | `snapshot` |
| `TaiwanStockTradingDate` | **6,937** | 1999-01-05 → **2026-12-31**（**103 個未來日**、2026 年 243 日） | — | 2026-06-21 | `byte` |
| `TaiwanExchangeRate` | **96,402** | 2006-01-02 → 2026-07-31 | **19 幣別**（USD 5,118 列） | 2026-08-01 17:45 upsert 19 列 | `byte` |
| `fred_series` | **344,876** | 1919-01-01 → 2026-07-30 | **31 series** | 2026-07-31 22:24 | `byte` |
| `ExchangeRate`（unmapped 66） | 54,730 | 1990-01-02 → **2020-11-13** | 6 country（Taiwan 8,972 列、止於 2020-11-12） | 2026-08-01 17:03 upsert **3 列**（但表內 max(date) 五年餘未前進） | `byte` |

---

## §2 逐概念備料

> 每節格式：**(a) 概念原文＋七欄現值** → **(b) 候選 binding 逐個依據（WM.14 逐字＋資料現況）** → **(c) 建議案一個＋理由一句＋證偽條件** →（如適用）**(d) 無合格候選之誠實宣告**。

---

### §2.1 `tw.daily_bar`（Annex F 第 1 條）

**(a) 概念原文與七欄現值**

> Annex F-1 原文：「**MarketTrade/DailyBar**｜事件／狀態（日級成交）｜兩通道：原始成交價通道＋含 CorporateAction 調整之衍生通道（WM.15 衍生觀測；供應商資料集名於登錄時 [I] 註記）｜同一世界事實之同一性宣告與擇用規則**單一登錄**（規範效力來源：A.58；AUD-14-R 落地）｜時間戳語義：交易日；可知規則：收盤後當日可得、次一交易日定案述語適用。」

| WM.36 欄 | 現值 |
|---|---|
| 1 世界概念 | `tw.daily_bar` |
| 2 歸類 | `event`（provenance 註：「原文雙寫『事件／狀態』，閉集單值暫置 event，**採認時校正**」） |
| 3 通道映射 | binding 75（`TaiwanStockPrice`, observation）＋ binding 81（`TaiwanStockPriceAdj`, **derived**）；二者 `source_column` 皆 NULL |
| **4 權威表徵指定** | **NULL** ⇒ WM.14 判準「解析至零個……違反本條」 |
| 5 時間屬性雙宣告 | ts=`交易日`／knowability=`收盤後當日可得`；`cross_market_axis`=NULL |
| 6 provenance | 來源＝所列通道之當次回應；作成依據＝AUD-01-R4 隨卷；**採認狀態＝pending** |
| 7 定案性述語 | **`次一交易日定案述語適用`**（六概念中唯一非「未宣告」者） |

**(b) 候選清單與依據**

| 候選 | 支持其為權威表徵之事實 | 不支持之事實 |
|---|---|---|
| **binding 75 `TaiwanStockPrice`**（observation） | ① WM.15 稱另一通道為「**衍生**調整觀測」，本通道即該條之「原始觀測」；② 鍵集合較廣：2026-07 共 **911,570 列／50,334 個 stock_id**，且與 Adj 之共同鍵 **61,554 列＝Adj 該窗全部列**（Adj 鍵集合 ⊆ 本表）；③ `attestation_mode=byte`（逐 byte 對帳口徑）＝與欄 7 現值「次一交易日定案」相容；④ 每日 live（08-01 upsert 41,876 列） | 含權證／ETF 等非普通股標的（55,674 stock_id），消費端若需「上市普通股日 K」仍須自行過濾（此為**宇宙選擇**問題，非通道問題） |
| **binding 81 `TaiwanStockPriceAdj`**（derived） | ① 生產鏈實際消費較重：repo 內字面出現 **45 處／29 檔**（vs raw 40 處／21 檔）；② 報酬計算通常需還原價 | ① 角色欄自書 `derived`（WM.15 衍生觀測）；② `attestation_mode=**restating**`＝回溯重算，與**已登錄之欄 7「次一交易日定案」相斥**（採 adj 為權威者，欄 7 須同時改為 A.37 例示之「還原價於無後續除權息事件之區間內定案」）；③ 2026-07 與 raw 之共同鍵中 **3,085／61,554 列（5.01%）close 不同**⇒ 兩通道**不可互換** |

> 共同鍵 close 歧異之查法（可重跑）：`SELECT count(*), count(*) FILTER (WHERE p.close IS DISTINCT FROM a.close) FROM "TaiwanStockPrice" p JOIN "TaiwanStockPriceAdj" a USING (stock_id,date) WHERE p.date>=DATE '2026-07-01';` → `61554 / 3085`。

**(c) 建議案**：**binding 75**（`TaiwanStockPrice`）。
**理由（一句）**：兩通道之**已登錄欄 5／欄 7 現值**（收盤後當日可得、次一交易日定案）只與 raw 相容，且 raw 之鍵集合涵蓋 adj 全部鍵——選 raw 是**不需同時改動其他欄**的唯一選項。
**證偽條件**：(i) Steward 認定 A.58／WM.15 之「擇用規則」以**還原價**為預設消費值 ⇒ 改指 **81** 並**同步**修欄 7 為還原價定案述語；(ii) 絞殺時任一 adj 消費者改繫 `resolve('tw.daily_bar')` 後影子比對 **diff≠0**（依上表 5.01% 之歧異率，**此事必然發生**）⇒ 該檔熔斷、停手問，並依 §7 Q1 之裁示決定「adj 消費者的合法載體」；(iii) 若欄 2 由 `event` 校正為 `state` 而影響歸類—權威組合之判定 ⇒ 重審。

---

### §2.2 `tw.corporate_action.ex_dividend`（Annex F 第 2 條）

**(a) 概念原文與七欄現值**

> Annex F-2 原文：「**CorporateAction.除權息**｜世界事件｜股利與除權息結果通道｜權威表徵指定於事件概念｜時間戳語義：除權息交易日；可知規則：**公告時點欄為可知規則錨**（WM.31(b)）。」

| 欄 | 現值 |
|---|---|
| 1／2 | `tw.corporate_action.ex_dividend`／`event` |
| 3 | binding 25（`TaiwanStockDividend`）＋ binding 48（`TaiwanStockDividendResult`），皆表級暫登 |
| **4** | **NULL** |
| 5 | ts=`除權息交易日`／knowability=**`公告時點欄為可知規則錨(WM.31(b))`** |
| 6／7 | pending／**`未宣告`**（⇒ WM.32 缺省推定 non-final） |

**(b) 候選清單與依據**

| 候選 | 支持 | 不支持 |
|---|---|---|
| **binding 25 `TaiwanStockDividend`** | **唯一持有欄 5 所指之「公告時點欄」**：`AnnouncementDate`／`AnnouncementTime` 存在且 **2,295／2,411 列非空**；另持 `StockExDividendTradingDate`／`CashExDividendTradingDate` | **表已塌列**：2,411 列／2,411 個 stock_id，**每股恰 1 列（max=min=avg=1.000）**——一檔股票數十年只剩一筆除權息紀錄；`year` 欄髒（相異值 50，含「100年」「年度及　　年第　　季/不適用」）；**最近落地 2026-06-19**（44 日未更）；`attestation_mode=restating` |
| **binding 48 `TaiwanStockDividendResult`** | 資料完整且 live：**31,097 列／2,376 stock_id／2003-07-07→2026-07-31**，2026-08-01 仍在 upsert；`attestation_mode=byte`；持除權息前後價（`before_price`／`after_price`／`reference_price`） | **無任何公告時點欄**（全欄：date, stock_id, before_price, after_price, stock_and_cache_dividend, stock_or_cache_dividend, max_price, min_price, open_price, reference_price）⇒ 指定其為權威表徵者，**欄 5 已登錄之可知規則錨在該通道上不可解析** |

**(c) 建議案**：**不採認、維持 `authoritative_binding_id` NULL（WM.35 顯式過渡態）**。
**理由（一句）**：兩候選各缺一半——25 有可知規則錨但**表本身已塌列**（每股 1 列），48 資料健全但**錨欄不存在**，任一指定都會使「七欄俱全且各欄可解析」在**同一列上不成立**。
**(d) 無合格候選之誠實宣告**：本概念**現無單一合格候選**；解閘前置二擇一——**前置甲**：修 `TaiwanStockDividend` writer 之塌列（#12「改 writer + 重建」，不 hand-patch）後採認 25；**前置乙**：Steward 裁示「欄 5 之可知規則錨得由**同概念他通道**承載」，則採認 **48**（本備料之備選）。
**證偽條件**：(i) 若重查 `TaiwanStockDividend` 之每股列數 >1（即塌列已修）⇒ 主案改為採認 25；(ii) 若 Steward 裁錨可跨通道 ⇒ 改採 48；(iii) 若發現第三通道（如 `TaiwanStockCapitalReductionReferencePrice`、`TaiwanStockSplitPrice`）描述**同一**世界事實 ⇒ 依 WM.15 登錄為待決同一性存量後再議。

---

### §2.3 `tw.fx.twd_usd`（Annex F 第 3 條）

**(a) 概念原文與七欄現值**

> Annex F-3 原文：「**EconomicIndicator.新台幣對美元匯率**｜世界量｜兩供應商通道（本國供應商匯率資料集＋外國經濟資料庫對應 series）｜**一權威表徵指定＋衝突保存落點**（AUD-06-R1/R2 落地）｜時間戳語義：觀測日；可知規則：依通道各自宣告（vintage 通道逐版）。」
> 另 A.11 原文：「每一指標為**世界量，非任何供應商之 series 識別**。」

| 欄 | 現值 |
|---|---|
| 1／2 | `tw.fx.twd_usd`／`quantity` |
| 3 | binding 12（`fred_series`）＋ binding 32（`TaiwanExchangeRate`），**皆 `source_column` NULL** |
| **4** | **NULL**（provenance 註：「多通道衝突保存落點＝`conflict_set_ref`，值待採認」；`conflict_set_ref` 現亦 NULL） |
| 5 | ts=`觀測日`／knowability=`依通道各自宣告(vintage 通道逐版)` |
| 6／7 | pending／`未宣告` |

**(b) 候選清單與依據**

| 候選 | 支持 | 不支持 |
|---|---|---|
| **binding 32 `TaiwanExchangeRate`** | 本國供應商匯率資料集，**96,402 列／2006-01-02→2026-07-31**，USD 幣別 **5,118 列**、每日 live（08-01 upsert 19 列）；`attestation_mode=byte` | **一表含 19 幣別**——`source_column` NULL 之表級登錄**無法表達「哪一列才是 TWD/USD」**；且 USD 列有四個價欄（`cash_buy`／`cash_sell`／`spot_buy`／`spot_sell`），**哪一欄是「該世界量」亦未登錄**（2026-07-31：spot_buy 32.26／spot_sell 32.36／cash_buy 31.91／cash_sell 32.58） |
| **binding 12 `fred_series`** | **本庫確有新台幣對美元 series：`DEXTAUS`——11,170 列／1983-10-03→2026-07-24**，2026-07-24 值 **32.39**（與同日本國通道 spot 32.26/32.36 同尺度）；每列自帶 `realtime_start`（vintage，對應欄 5「逐版」）；07-31 仍在 upsert | **一表含 31 個 series**——表級登錄同樣無法表達 `series_id='DEXTAUS'`；而 WM.36 禁令原文明文列舉之字面即含「**series 識別碼**」 |
| （非候選）`ExchangeRate`（unmapped binding 66） | 另有 country='Taiwan' 之 `InterbankRate`（8,972 列） | **止於 2020-11-12**（表級 max 2020-11-13）；每日 sync 仍 upsert 3 列但資料五年餘未前進 ⇒ 不具 live 地位、未登錄為本概念通道 |

**(c) 建議案**：**不採認、維持 NULL（顯式過渡態）**，前置＝**先補「列篩選表達力」**（讓通道列能承載 `currency='USD'`／`series_id='DEXTAUS'`），補畢後採認 **binding 32**（本國通道為權威、`fred_series`(DEXTAUS) 為衝突保存之第二通道並填 `conflict_set_ref`）。
**理由（一句）**：兩候選皆**多值表**，在現行「表級暫登（`source_column` IS NULL）」下 `resolve()` 只會回傳表名，消費端**仍須自行內嵌 `currency='USD'`／`series_id='DEXTAUS'` 字面**——那正是 WM.36 禁令逐字列舉之物，採認即產生「解析到表、字面仍在消費端」的半套。
**證偽條件**：(i) Steward 裁示表級暫登於本概念可接受（欄位級待後批）⇒ 立即採認 32、不待補欄；(ii) 若補欄後查得 `TaiwanExchangeRate` USD 與 `fred_series` DEXTAUS 同日值差超出可容忍門檻 ⇒ 依 WM.16 登錄衝突、`conflict_set_ref` 不得留 NULL；(iii) 若本國通道停更（max(date) 落後 >5 交易日）⇒ 權威改指 fred 通道。
**(d) 附帶必須修訂之事實錯誤**：binding 12 之 `map_note` 現載「2026-08-02 親驗本庫**無**新台幣對美元直接 series，僅 DTWEXBGS」——**經本輪實證為誤**：`DEXTAUS` 在庫、11,170 列、且 repo 內 `src/augur/features/macro.py:52` 早已逐字標註 `_a("DEXTAUS", "新台幣對美元匯率")`。此註記若隨採認附卷，等於把一個可一行證偽的錯誤寫進治權記錄 ⇒ **建議在採認同一交易內先修訂該通道列**（範本 B，§5.2）。

---

### §2.4 `tw.trading_calendar`（Annex F 第 4 條）

**(a) 概念原文與七欄現值**

> Annex F-4 原文：「**TradingCalendar**｜世界關係（日曆日↔交易日）｜交易日通道｜**單通道權威**｜時間戳語義：交易日；可知規則：事前公告之市場日曆。」

| 欄 | 現值 |
|---|---|
| 1／2 | `tw.trading_calendar`／`relation` |
| 3 | binding 4（`TaiwanStockTradingDate`, observation），表級 |
| **4** | **NULL** |
| 5 | ts=`交易日`／knowability=`事前公告之市場日曆` |
| 6／7 | pending／`未宣告` |

**(b) 候選清單與依據**

| 候選 | 支持 | 不支持 |
|---|---|---|
| **binding 4 `TaiwanStockTradingDate`** | ① **唯一候選**（Annex F 自書單通道權威；98 列通道中無第二個日曆通道）；② 表結構即概念本身（單欄 `date`，無需列篩選、無多值歧義）⇒ **表級登錄不產生 §2.3 之半套問題**；③ **6,937 列／1999-01-05→2026-12-31**，其中 **103 個未來日**——與欄 5「事前公告之市場日曆」逐字相符（可知規則之機械證據）；④ `attestation_mode=byte` | 最近落地 **2026-06-21**（非每日）——惟日曆為事前公告、已覆蓋至 2026-12-31，故非資料缺口 |

**(c) 建議案**：**binding 4**。
**理由（一句）**：單通道、單欄、涵蓋至年底且含 103 個未來日——WM.14「恰解析至一個」在本概念上**無須任何裁量**即成立。
**證偽條件**：(i) 查得任何其他通道（如自 `TaiwanStockPrice` 之相異日期）被消費為交易日曆 ⇒ 依 WM.15 為待決同一性存量、須先作同一性宣告；(ii) `max(date)` 未覆蓋次一年度（例：跨年後仍止於 2026-12-31）⇒ 可知規則宣告與事實脫節、須補 sync 後再議。

---

### §2.5 `tw.roster_membership`（Annex F 第 5 條）

**(a) 概念原文與七欄現值**

> Annex F-5 原文：「**Roster 成員資格**｜世界狀態（point-in-time）｜基本資訊快照＋下市通道｜**權威表徵為時間函數之成員資格概念**（A.2 survivorship 禁令適用）｜時間戳語義：快照日；可知規則：快照當日。」

| 欄 | 現值 |
|---|---|
| 1／2 | `tw.roster_membership`／`state` |
| 3 | binding 28（`TaiwanStockInfo`）＋ binding 2（`TaiwanStockDelisting`），皆表級 |
| **4** | **NULL** |
| 5 | ts=`快照日`／knowability=`快照當日` |
| 6／7 | pending／`未宣告` |

**(b) 候選清單與依據**

| 候選 | 支持 | 不支持 |
|---|---|---|
| **binding 28 `TaiwanStockInfo`** | live（08-01 落地）；3,128 stock_id；`attestation_mode=snapshot` 與欄 5「快照日」相符 | **不足以構成 point-in-time 成員資格函數**：全表 4,296 列僅 **254 個相異日**，且 **2026-07-31 一日即佔 3,305 列**（＝最新全量快照），其餘 253 日多為零星增量（次高 2024-12-04 僅 179 列）；起點 **2020-06-03**——2020 年前無任何快照 ⇒ 以其為權威即以「現存名單」代表歷史成員資格（Annex F 自引之 **A.2 survivorship 禁令**正是針對此） |
| **binding 2 `TaiwanStockDelisting`** | 344 列、2001-01-20→2026-07-28、live | 只承載「離開」事件，**不含成員資格狀態本身**；且同表已作為 `tw.delisting` 之候選（一表服務兩概念合法，WM.36 欄 3 一對多） |
| （**未登錄**之內部候選）`core_universe_asof` | 真正的 point-in-time 表徵：**42,782 列／2018-01-31→2026-06-30／895 stock_id**（欄：`as_of_date, stock_id, panels, features, committed_at`） | **不在 `world_channel_binding` 98 列之內**——未登錄之載體不得被指定為權威表徵；且其為系統內部衍生物而非 Observation Channel，是否得登錄＝**條文問題（§7 Q3）**；覆蓋亦止於 2026-06-30、起點 2018 |

**(c) 建議案**：**不採認、維持 NULL（顯式過渡態）**，前置＝先解決「時間函數之成員資格」由何載體承載。
**理由（一句）**：Annex F 自書「權威表徵為**時間函數**之成員資格概念」，而登錄在案的兩個候選都不是時間函數（一為稀疏快照、一為離場事件），真正是時間函數的 `core_universe_asof` **未登錄為通道**。
**(d) 無合格候選之誠實宣告**：本概念**現無合格候選**；不硬湊。
**證偽條件**：(i) Steward 裁示成員資格得以「最新快照＋下市事件之組合」為權威 ⇒ 採認 **28** 並將擇用規則登錄於 registry（不得散在消費端，WM.15）；(ii) Steward 裁示內部衍生表得登錄為通道 ⇒ 先補登 `core_universe_asof` 通道列，再指定其為權威；(iii) 若查得 `TaiwanStockInfo` 之相異日已補為逐日 ⇒ 主案改為採認 28。

---

### §2.6 `tw.delisting`（Annex F 第 6 條）

**(a) 概念原文與七欄現值**

> Annex F-6 原文：「**Delisting**｜世界事件｜下市通道｜**單通道權威**（A.25 可見性語義適用）｜時間戳語義：下市日；可知規則：主管機關公告。」

| 欄 | 現值 |
|---|---|
| 1／2 | `tw.delisting`／`event` |
| 3 | binding 3（`TaiwanStockDelisting`, observation），表級 |
| **4** | **NULL** |
| 5 | ts=`下市日`／knowability=`主管機關公告` |
| 6／7 | pending／`未宣告` |

**(b) 候選清單與依據**

| 候選 | 支持 | 不支持 |
|---|---|---|
| **binding 3 `TaiwanStockDelisting`** | ① **唯一候選**（Annex F 自書單通道權威）；② 表結構即概念（`date, stock_id, stock_name`，一列＝一次下市事件，無多值歧義 ⇒ 表級登錄不產生 §2.3 之半套問題）；③ **344 列／2001-01-20→2026-07-28**，08-01 仍 upsert 1 列＝live；④ 內部 `identity_lifecycle_event` 精確 344 列且 `event_type` 單一值 `retire`（與本表列數相同，供交叉核對；`count(*)` 實查非估計值） | `attestation_mode=cadence`（非逐 byte）；欄 5 之「主管機關公告」在本表**無對應公告時點欄**（僅 `date`）——與 §2.2 同型之錨欄問題，惟本概念之錨規則未指名欄位（§7 Q4） |

**(c) 建議案**：**binding 3**。
**理由（一句）**：單通道、單一事件粒度、live 且列數與內部 lifecycle 帳本一致——WM.14「恰解析至一個」成立且無替代品可爭。
**證偽條件**：(i) Steward 認定欄 5「主管機關公告」須有**表內可解析之錨欄**（本表無）⇒ 退回過渡態、先補通道或改寫欄 5；(ii) 查得 `TaiwanStockSuspended`（2,285 列／2025-03-07 起，含 `resumption_date`）被任何模組當作下市判定 ⇒ WM.15 待決同一性存量；(iii) 本表與 `identity_lifecycle_event` 列數脫鉤且無法解釋 ⇒ 先對帳。

---

## §3 三個跨概念之結構性阻塞（圈選前需知）

### 3.1 表級暫登 vs「粒度至欄位級」（WM.36 欄 3 原文）
十列 mapped 通道之 `source_column` **全為 NULL**。對**表即概念**之通道（`TaiwanStockTradingDate`、`TaiwanStockDelisting`）無實害；對**多值表**（`fred_series` 31 series、`TaiwanExchangeRate` 19 幣別）則使 `resolve()` 只能回表名，**消費端仍須內嵌 series 識別碼／幣別字面**。`world_channel_binding` 現行 schema **無任何欄可承載列篩選**（`provenance` jsonb 雖可放，但 `resolve()` 只回 `(table, column, role)`，放進去也解析不出來）。⇒ §7 Q2。

### 3.2 「採認＝INSERT、免通行證」在現行索引下**不成立**
設計註記（`scripts/migrate_world_concept_identity_split_ddl.py:41-43`）載：「honesty guard 只擋 UPDATE/DELETE/TRUNCATE，INSERT 自由 ⇒ Annex F 六條採認親簽變成 **INSERT 一列新版本**，不再需要 `SET LOCAL augur.honesty_write='on'`」。
但版本表上有 `uq_world_concept_current UNIQUE (concept_key) WHERE superseded_at IS NULL`（本輪 `\d` 親驗），而六列 seed **皆為現行列**（`superseded_at` 全 NULL）。⇒ 直接 INSERT 第二筆現行列**必撞唯一違反（23505）**；欲插入新版本，**必須先把 seed 列標 `superseded_at`（UPDATE）**，而該 UPDATE **正是 honesty guard 要通行證的那一種**。
**誠實限定**：此為依索引定義之推導；**未以實測證實**（實測＝寫入，本輪禁止）。可唯讀複核之依據：`\d world_concept_version`（索引定義）＋ `SELECT count(*) FROM world_concept_version WHERE superseded_at IS NULL` ＝ 6。⇒ §5 範本照實寫入 `SET LOCAL` 一行；§7 Q5 請 Steward 裁「治權簽核與默改共用通行證」是否可接受，或改為由工具腳本封裝。

### 3.3 binding 12 之 `map_note` 事實錯誤（見 §2.3(d)）
現載「本庫無新台幣對美元直接 series」；實證 `DEXTAUS` 在庫 11,170 列、2026-07-24 值 32.39，且 `src/augur/features/macro.py:52` 已逐字標為「新台幣對美元匯率」。⇒ 建議採認前以範本 B 修訂該通道列（修訂＝標舊列 superseded〔需通行證〕＋INSERT 更正列）。

---

## §4 hugo 圈選單

> 圈選方式：在「圈選」欄打勾或直接寫下你要的 binding_id／「不採認」。**decided_by／decided_at 一律由你親打**，本備料未填、亦不代填。

| # | 世界概念 | 候選（binding_id → 表） | **AI 建議** | 一句理由 | 圈選 |
|---|---|---|---|---|---|
| 1 | `tw.daily_bar` | **75**→`TaiwanStockPrice`(obs)／81→`TaiwanStockPriceAdj`(derived) | **75** | 已登錄之欄 5／欄 7 只與 raw 相容，且 raw 鍵集合涵蓋 adj 全部鍵 | ☐ 75　☐ 81　☐ 不採認　☐ 其他：____ |
| 2 | `tw.corporate_action.ex_dividend` | 25→`TaiwanStockDividend`（有公告錨、**已塌列**）／48→`TaiwanStockDividendResult`（健全、**無錨欄**） | **不採認（過渡）** | 兩候選各缺一半，任一指定都使「七欄各欄可解析」在同一列上不成立 | ☐ 不採認　☐ 48（裁錨可跨通道）　☐ 25（俟塌列修復）　☐ 其他：____ |
| 3 | `tw.fx.twd_usd` | 32→`TaiwanExchangeRate`(19 幣別)／12→`fred_series`(31 series，含 **DEXTAUS**) | **不採認（過渡）＋先修 binding 12 註記** | 兩者皆多值表，表級登錄下消費端仍須內嵌幣別／series 字面＝WM.36 禁令原文所列 | ☐ 不採認　☐ 32（接受表級暫登）　☐ 12　☐ 其他：____ |
| 4 | `tw.trading_calendar` | **4**→`TaiwanStockTradingDate` | **4** | 單通道單欄、覆蓋至 2026-12-31 含 103 未來日，WM.14 恰一無裁量空間 | ☐ 4　☐ 不採認　☐ 其他：____ |
| 5 | `tw.roster_membership` | 28→`TaiwanStockInfo`(254 相異日)／2→`TaiwanStockDelisting`；（未登錄）`core_universe_asof` | **不採認（過渡）** | Annex F 要求「時間函數」，登錄在案兩候選都不是時間函數 | ☐ 不採認　☐ 28＋擇用規則　☐ 先補登 `core_universe_asof` 通道　☐ 其他：____ |
| 6 | `tw.delisting` | **3**→`TaiwanStockDelisting` | **3** | 單通道單事件粒度、live，且列數與內部 lifecycle 帳本一致 | ☐ 3　☐ 不採認　☐ 其他：____ |

**附帶待圈（非 Annex F 七欄，但同一交易內須決定）**
| 項 | 建議 | 圈選 |
|---|---|---|
| binding 12 `map_note` 事實更正（§3.3） | 採認前先修訂 | ☐ 先修訂　☐ 併後批　☐ 不修 |
| `tw.daily_bar` 欄 2 由 `event` 校正為（`event`／`state`）（provenance 自書「採認時校正」） | 依 Steward 裁 | ☐ 維持 event　☐ 改 state　☐ 後批 |
| 採認交易是否得用 `SET LOCAL augur.honesty_write='on'`（§3.2 之物理必要） | 需明示同意，否則採認無合法路徑 | ☐ 同意　☐ 改由腳本封裝　☐ 其他：____ |

---

## §5 親簽 SQL 範本（丙案形制；**本輪未執行**，僅 `EXPLAIN` 乾解析）

> **紀律**：`decided_by`／`decided_at` 之佔位（`⟨…⟩`）**由 hugo 親打**；AI 不代填、不預填 `now()` 之外的任何身分值。
> **執行前**：先 `BEGIN`，逐句檢視回傳列數，確認無誤才 `COMMIT`；有疑即 `ROLLBACK`（全部範本皆可安全 rollback）。

### 5.1 範本 A｜概念採認（每概念一份；以 `tw.trading_calendar` → binding 4 為例）

```sql
BEGIN;
-- 通行證：僅為「把 seed 現行列標 superseded」之 UPDATE 所需（§3.2：partial unique 使 INSERT 無法單獨完成）
SET LOCAL augur.honesty_write = 'on';

-- ① 標舊列 superseded（append-only：內容欄一概不原地改）
UPDATE world_concept_version
   SET superseded_at = now()
 WHERE concept_key = 'tw.trading_calendar'
   AND superseded_at IS NULL;                       -- 期望回 UPDATE 1

-- ② INSERT 新版本列（採認內容＝指定權威表徵＋人簽欄；其餘六欄逐欄承襲）
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref, decided_by, decided_at)
SELECT concept_key,
       category,
       4,                                            -- ← 圈選之 binding_id
       ts_semantics, knowability_rule, cross_market_axis,
       provenance || jsonb_build_object(
           '採認狀態', 'adopted',
           'decision_ref', '⟨附卷裁定編號⟩',
           'adopted_basis', 'Annex F 第 4 條；備料 reports/wm_annexf_authoritative_binding_prep_20260803.md §2.4'),
       finality_predicate, conflict_set_ref,
       '⟨hugo 親打⟩',                                 -- decided_by：AI 不代填
       TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩'         -- decided_at：AI 不代填
  FROM world_concept_version
 WHERE concept_key = 'tw.trading_calendar'
 ORDER BY transaction_time DESC
 LIMIT 1;                                            -- 期望回 INSERT 0 1

-- ③ 驗（純 SELECT）：現行列恰一、權威已指定、人簽欄已填
SELECT concept_key, authoritative_binding_id, decided_by, decided_at, transaction_time
  FROM world_concept_registry_current
 WHERE concept_key = 'tw.trading_calendar';

COMMIT;   -- 或 ROLLBACK
```

**其餘概念只需改三處**：`concept_key`（兩處 WHERE ＋ 驗證）、`4`→圈選之 binding_id、`decision_ref`／`adopted_basis` 之節號。對應表：`tw.delisting`→**3**（§2.6）、`tw.daily_bar`→**75**（§2.1）。
**不採認之三概念（§2.2／2.3／2.5）不需要任何 SQL**——維持 NULL 即 WM.35 顯式過渡態；如需在案上留痕，可只走範本 A 之 ①②、把 `authoritative_binding_id` 留 `NULL` 並於 provenance 記 `'採認狀態','deferred'` ＋ 理由（**此為留痕，不是採認**）。

### 5.2 範本 B｜通道列修訂（以 binding 12 之 `map_note` 事實更正為例；§3.3）

```sql
BEGIN;
SET LOCAL augur.honesty_write = 'on';               -- 標舊列 superseded 之 UPDATE 所需

UPDATE world_channel_binding
   SET superseded_at = now()
 WHERE binding_id = 12 AND superseded_at IS NULL;    -- 期望回 UPDATE 1

INSERT INTO world_channel_binding
    (concept_key, source_table, source_column, channel_role, mapping_status, provenance)
SELECT concept_key, source_table, source_column, channel_role, mapping_status,
       provenance || jsonb_build_object(
           'map_note', 'Annex F-3 外國經濟資料庫對應 series；本庫之新台幣對美元 series = DEXTAUS（2026-08-03 親驗 11,170 列／1983-10-03→2026-07-24／2026-07-24 值 32.39）',
           'corrects_binding_id', 12,
           'correction_basis', '原註記「本庫無新台幣對美元直接 series，僅 DTWEXBGS」經 live 查證為誤；反證亦見 src/augur/features/macro.py:52')
  FROM world_channel_binding
 WHERE binding_id = 12;                              -- 期望回 INSERT 0 1（binding_id 由 IDENTITY 新給）

SELECT binding_id, concept_key, source_table, provenance->>'map_note'
  FROM world_channel_binding
 WHERE concept_key = 'tw.fx.twd_usd' AND superseded_at IS NULL;

COMMIT;   -- 或 ROLLBACK
```

> ⚠ 若被修訂之通道**已被某概念指定為權威**（現況：無），該概念之 `authoritative_binding_id` 須於**同一交易內**改指新 binding_id，否則 `resolve()` 會因「權威通道已 supersede」而 fail-closed。

### 5.3 唯讀語法檢查結果（本輪實跑；**零寫入**）

```bash
psql … -f scratchpad/dryparse.sql      # 內容＝BEGIN; EXPLAIN (COSTS OFF) <四句 DML>; <驗證 SELECT>; ROLLBACK;
```
四句 DML＋驗證 SELECT **全部通過解析與計畫**（`EXPLAIN` 無 `ANALYZE` ⇒ 不執行）：
`Update on world_concept_version`（Seq Scan, Filter: superseded_at IS NULL AND concept_key=…）／`Insert on world_concept_version`（Limit→Sort by transaction_time DESC）／`Update on world_channel_binding`（Index Scan `world_channel_binding_pkey`, binding_id=12）／`Insert on world_channel_binding`（同索引）／驗證 SELECT（Nested Loop over version+concept）。`RC=0`、`ROLLBACK`。
**未被此檢查涵蓋者（誠實）**：唯一索引違反、trigger 拒絕、jsonb 併值結果——皆屬執行期行為，`EXPLAIN` 一律不觸發；§3.2 之推導因此**仍是推導、非實測**。

---

## §6 本輪唯讀證明與邊界

- **零寫入實證**：全部查詢後複查 → 身分 6／版本 6／現行 6／`decided_by` 非空 **0**／`authoritative_binding_id` 非空 **0**／通道 98／已 supersede 通道 **0**，與 §1.1 起始值**逐項相同**。
- **零 DDL、零 commit、零 systemctl**；未觸 FinMind／FRED 任何 API（#24／#25 不適用，本輪無外部抓取）。
- **未改任何既有檔**；`reports/w2_20260801/INDEX.md` 未動；本檔為新增（#16 命名）。
- **不解釋條文**（`AUGUR-MC v1.6 §8.1`）：§2 各節之「建議案」為 **AI self-reported 之證據整備**（CLAUDE #32(a)），非裁決；凡需解釋條文方能定案者一律進 §7。
- **人簽欄**：`decided_by`／`decided_at` 全程未填、範本亦留 `⟨…⟩` 佔位。

---

## §7 待 Steward 之問題（逐題可單獨圈選；AI 不代裁）

| # | 問題 | 為何非 AI 可決 | 卡住什麼 |
|---|---|---|---|
| **Q1** | `tw.daily_bar` 採 raw 為權威後，**還原價（adj）之消費者**（現 29 檔／45 處）的合法載體為何？(a) 另立世界概念（如 `tw.daily_bar.adjusted`）／(b) 於 registry 登錄擇用規則欄／(c) 逕採 adj 為權威並改欄 7 | WM.14「恰一」與 WM.15「擇用規則單一登錄」之交互適用＝條文解釋 | M3 絞殺 A 類最重的一批檔（features／train／predict） |
| **Q2** | 多值表（`fred_series` 31 series／`TaiwanExchangeRate` 19 幣別）之通道登錄，是否須具**列篩選表達力**才算「粒度至欄位級」？若須，是否同意在 `world_channel_binding` 增欄（表結構變更＝Steward 專屬） | WM.36 欄 3「粒度至欄位級」之適用範圍＋表結構變更權限 | `tw.fx.twd_usd` 採認；macro 特徵鏈之絞殺 |
| **Q3** | 內部衍生表（`core_universe_asof`）得否登錄為 Observation Channel 並被指定為權威表徵？ | WM.7／WM.35 之「通道」外延＝條文解釋 | `tw.roster_membership` 採認；A.2 survivorship |
| **Q4** | 欄 5 之「可知規則錨」是否**必須**存在於**該權威通道之表內**？（影響 `ex_dividend`〔錨欄只在塌列表〕與 `delisting`〔表內無公告欄〕） | WM.31(b)／A.35 之適用＝條文解釋 | 兩概念之採認 |
| **Q5** | 採認交易須用 `SET LOCAL augur.honesty_write='on'`（§3.2 之物理必要）——治權簽核與「默改通行證」共用同一咒語是否可接受？或改由專用腳本封裝（腳本＝新增可執行入口，須具指令矩陣＋自測，#18／#29） | 監督機制之組態變更，AI 不得為核准主體（`AUGUR-L6 v1.2` L6.18(a)） | 六概念全部採認之執行路徑 |
| **Q6** | `tw.daily_bar` 欄 2 之閉集單值（原文雙寫「事件／狀態」，現暫置 `event`，provenance 自書「採認時校正」） | WM.36 欄 2 閉集歸類＝條文適用 | 採認同一交易內須定 |

---

## §8 複核用一鍵指令（全唯讀、零 Claude usage）

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
venv/bin/python -m augur.catalog.world_concept --check                    # 六概念可解析否（現 0/6）
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -x -c \
  "SELECT * FROM world_concept_registry_current ORDER BY concept_key;"    # 七欄現值
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c \
  "SELECT binding_id, concept_key, source_table, channel_role, mapping_status,
          provenance->>'map_note' FROM world_channel_binding
    WHERE mapping_status='mapped' ORDER BY concept_key, binding_id;"      # 十列候選
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c \
  "SELECT series_id, count(*), min(date)::text, max(date)::text FROM fred_series
    WHERE series_id IN ('DEXTAUS','DTWEXBGS') GROUP BY series_id;"        # §3.3 之事實
```

---

## 附記：採認形制已沙盒實測（2026-08-03，主 session 補驗）

呈案 §3.2 之「單獨 INSERT 必撞唯一違反」原為**依索引定義之推導、未實測**（本輪禁寫入）。已於 `augur_sandbox`（含丙案結構之遷移後複本）實跑，兩向皆證：

**(1) 單獨 INSERT ⇒ 真撞唯一違反**
```
INSERT INTO world_concept_version (…) SELECT … WHERE superseded_at IS NULL LIMIT 1;
ERROR:  duplicate key value violates unique constraint "uq_world_concept_current"
DETAIL:  Key (concept_key)=(tw.corporate_action.ex_dividend) already exists.
```

**(2) 正解形制（標舊列 superseded 需通行證 → INSERT 新版本 → view 恰一列）⇒ 成立**
```
BEGIN; SET LOCAL augur.honesty_write='on';
UPDATE world_concept_version SET superseded_at=now() WHERE concept_key='tw.trading_calendar' AND superseded_at IS NULL;  -- UPDATE 1
INSERT INTO world_concept_version (…, authoritative_binding_id, decided_by, decided_at) SELECT …;                        -- INSERT 0 1
SELECT count(*) FROM world_concept_registry_current;  -- 6（view 總列不變、該概念仍恰一現行）
ROLLBACK;                                              -- 沙盒零殘留；生產 decided_by 非空仍 0
```

⇒ **採認交易之正確形制＝同一交易內「UPDATE 標舊列（帶 GUC 通行證）＋ INSERT 新版本列」**。
**更正**：先前「治權簽核自此為純 INSERT、免通行證」之表述（2026-08-03 凌晨 commit 訊息與對話）**不正確**——首次採認因六列 seed 皆為現行列，必經 UPDATE 標記。此更正不改變丙案之價值（版本列 append-only、修訂留痕、view 恰一現行），但**親簽範本須含 `SET LOCAL augur.honesty_write='on'`**（呈案圈選單附帶項三已預留此決定點）。
