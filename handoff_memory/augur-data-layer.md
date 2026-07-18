---
name: augur-data-layer
description: 資料層四層理解 SSOT(table/field/raw值/raw關係)— 94表772欄逐欄+恆等式實證;catalog db-only工具;關鍵raw真相+已知bug
metadata: 
  node_type: memory
  type: reference
  originSessionId: c3c40e0c-7154-4936-8937-6d9ce947808c
---

augur 資料層(⚠**2026-07-17 實查已成長:public relkind='r' 246 純表**〔+3 view〕、`column_catalog` 769 欄;原 94 表 772 欄為 06-29 建錨值)經 2026-06-29 **四層逐欄實證**(非 catalog 照抄、非「我以為」)。完整四層字典＝`reports/augur_full_column_walkthrough_20260629.md`(1306 行、commit 4b030d6);**理解結論報告(我的判斷、九節)＝`reports/augur_data_layer_understanding_20260629.md`(封存 tag `data-layer-understanding-20260629`、commit 559c47e)**。

**四層 + SSOT 位置**:
1. **table 定義**:`dataset_catalog`(95 列、抓法/tier/頻率/最早/排除)。
2. **field 定義**:`column_catalog`(751 欄、中文/型別/PK/anti-leakage/dirty_note)— **已回填對齊 DB**(fred 3 欄補、49 PK+型別偏差校正;型別/PK 權威是 **DB information_schema** #2、catalog 是可刷新快取)。
3. **raw 值定義**:逐欄實證 categorical 實際值域 + 範例(`scratchpad/deep_raw_profiler.py`)。
4. **raw 之間關係**:12 欄位間數值恆等式實證(`scratchpad/verify_identities.py`)。
另:3 份深驗報告(`augur_raw_data_definitions`/`_verification_ledger`/`_financial_typecodes_dictionary` 20260628);財報 224 type 全由 in-data `origin_name` 解碼。

**關鍵 raw 真相(catalog/報告之外、實證才知)**:
- 法人別實際 **6 值**(Dealer/Dealer_Hedging/Dealer_self/Foreign_Dealer_Self/Foreign_Investor/Investment_Trust;Total 表 7 含 total)、非概稱「5 玩家」。
- **HoldingSharesLevel 17 級含 `total` 彙總 + `差異數調整(說明4)`**＝percent 可負/>100 來源 → 用持股分級算 Pareto 須排除 total/差異數調整列。
- categorical 值域:BlockTrade 3(單一型/逐筆/配對)·SecuritiesLending 3(定價/競價/議借)·monitoring_color 6(-/B/G/R/YB/YR)·Info.type 3(emerging/tpex/twse)·GovBank 8 行庫。
- 財報語意:損益**單季**/現金流**累計YTD**/資產負債**snapshot**;`_per`=佔資產%;單位**元**;月營收單位**元**(catalog 原誤標千元已修)。
- anti-leakage 金礦欄:`Dividend.AnnouncementDate`✓·`Shareholding.RecentlyDeclareDate`✓·`MonthRevenue.create_time`**實證多空/ingestion時戳、不可用**→月營收用法定 lag(次月15)。

**欄位間恆等式(實證 99-100%、違反皆有解釋非錯)**:融資今餘=昨+買-賣-現償(100%)·**融券=昨+賣-買-現償(對稱;today>0 時 100%、全表 82% 因餘額下界截斷非公式錯)**·DailyShortSale 融券/借券餘額 100%·外資持股比率=持有/發行×100(100%)·財報三表勾稽 資產=負債+權益(99.5%)/毛利=營收-成本(99.6%)/營益=毛利-營業費用(96.8% 含其他項)·**跨表 市值≈收盤×發行股數(100%)**。

**已知資料 bug/陷阱**:① `TaiwanStockDividend` **PK=stock_id 單欄塌列**(同股多年互蓋僅存1筆;碼已修 require_keys=date、待 token 重建;現未入生產特徵不影響 alpha)② GovBank/衍生表 **PK 全欄塌陷**(detect_keys fallback;aggregate/out-of-scope 不影響)③ **BalanceSheet 系統性缺季**(2016-19/2022-24,影響 C3 庫存特徵)④ 停牌 OHLC=0 哨兵·PER=-1 虧損哨兵·國際股 Adj_Close overflow 不可用·CnnFearGreed 情緒格式混亂·Suspended time 8:00/09:00 不一致。

**catalog db-only 工具(commit 4b030d6)**:`build_catalog --db-only`＝landed 表純 DB 欄級 refresh(型別/PK from DB、**不打 API**、不動表級、**merge 保留策展 dirty/caveat/中文**)→ token 過期時對齊 column_catalog↔DB(#12 改 writer、非 hand-patch)。

**Why（五輪深化過程，用戶 2026-06-29 directive「記住」）**:用戶連**五輪**反覆要徹底確認資料層理解,每輪逼深一層、收斂到結論 — ① **完全理解確認**(我承認摘要級→親讀 3 深驗報告+catalog SSOT)② **逐欄走查** 94 表 772 欄結構(profiler+審視)③ **catalog 回填**對齊 DB(fred 3欄補+49 PK+型別校正、加 `db_only` 模式)④ **raw 值** categorical 實證(實際值域+範例)⑤ **raw 之間關係**恆等式驗證(16 勾稽/定義/三表/跨表)→ **理解結論報告**。資料誠實是 augur 命門(#1/#15)。
**核心教訓(五輪收穫)**:(a)「完全理解」是**逐層逼近、非一次到達** — 每輪都揭新東西(法人 6 值/HoldingSharesLevel total+差異數調整/PER≤0 28%/融券誤判);(b)**逐欄/逐列實證會推翻「看一個數字就下的結論」**(融券全表 82% 我曾誤判「公式錯」、逐列追查發現公式對、違反是餘額下界截斷)→ #20 見可疑追到底、防自欺③、靈魂「只信真兆」;(c) **連五輪「還問」本身是紀律**——不因問過就空稱「完全懂」,每輪都實證再答 + 誠實標漸近邊界(罕見碼準則級/衍生 out-of-scope),拒絕自欺。
**How to apply**:查任何欄定義→ `column_catalog`(對齊 DB);查 raw 值域/恆等式→ 走查報告 + scratchpad 工具。**誠實邊界(漸近、非絕對全知)**:罕見財報碼 IFRS 準則條文級、衍生品 out-of-scope 欄精確邊界未逐一。關聯 [[feature-execution-plan]] [[core-universe-and-f3-model]] [[rigor-completeness-discipline]] [[db-cross-machine-independent]]。
