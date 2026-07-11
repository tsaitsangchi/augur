# augur 反洩漏審計報告 — feature_values 全生產面板兩輪審計與修復

**日期**:2026-07-11
**檔名(定稿)**:`reports/augur_antileakage_audit_20260711.md`

**查證基準(誠實聲明)**:
- **DB 數字**:除明標「修正前快照」者外,所有數字於 **2026-07-11** 以 psql 對本地 `augur` 庫(`table_schema='public'`)直查實證;`top_holders_pct` 重建於本日 09:27 啟動、~50 分完成,重建前/後數字**分別標示**,不混用。
- **程式行號**:已 commit 之檔釘 HEAD `7fd3426`;**三檔工作樹未 commit 修正**(`src/augur/features/chip.py`、`src/augur/features/release_lag.py`、`scripts/rebuild_feature.py`,2026-07-11 審計 1A 落地)之行號**釘工作樹現行內容**(`git status` M;工作樹另 4 檔 M 屬 advisor 蒸餾工作流、與本審計無關)。
- 相關 commit:`cd8b35e`(2026-07-11 08:10:07 +0800,第一輪修復,`git show` 實查)。

**目錄**:§0 三十秒摘要|§1 審計方法|§2 已修復(cd8b35e)|§3 chip 大戶比(active 洩漏→已修復+重建完成)|§4 潛在債|§5 全模組健康度總表|§6 schema 與程式規畫|§7 分階段與驗收|§8 殘留決策清單|附:數字溯源

---

## §0 三十秒摘要

對 augur 生產特徵面板 `feature_values`(重建後現況:**2,418,655 列 / 35 特徵 / 35 panel,2007-12-31 → 2026-05-31**;重建前快照 2,419,048 列)完成兩輪反洩漏審計,**全部已確認洩漏均已修復**:

| 結論 | 項目 | 狀態 |
|---|---|---|
| **已確認洩漏、已修復並 commit**(§2) | `price_to_10yr` 前向還原分子(洩漏+混口徑)/ `gross_margin_pctile` 陳舊值冒充當季 / IC 工具存活者偏誤 | commit `cd8b35e`(2026-07-11 08:10 +0800);重建 UPDATE 109,520 列(50,283+59,237)、DELETE 1,041 列(673+368) |
| **已確認 active 洩漏、已拍板 1A、已修復+重建完成(待 commit)**(§3) | `chip.top_holders_pct`:集保週五快照無公布 gate,修正前 65,923 列 / 32 panel 全數保守視為暴險、含 live panel 2026-05-31 | 用戶拍板**選項 A(保守 +7 日 gate)**;writer+gate 三檔已落地(工作樹)、重建完成 **UPDATE 65,530 / DELETE 393**(2026-07-11 09:27 起 ~50 分);驗收全過(§7);**僅餘 commit 授權(#14)** |
| **潛伏債(latent)、零現行消費者**(§4) | macro 兩埋雷:FRED Tier A `realtime_start` 為碼構造非實測 / Tier B vintage 濾版 gate 只在註解零程式 | 35 特徵零 macro、`fred_series` 零 feature 消費者 → 無 active 漏;觸發條件與修法已定(§4.1/4.2、§6.2b) |
| **判 clean**(§4、§5) | `concentration` / `phase` / `panel` | 比值因子相消 / 法人盤後當晚公布 / 水位漏源在已修 valuation |
| **記錄在案、現況休眠**(§2.4、§4.3) | `release_lag` 金融業 Q1/Q3 法定 60 日 vs 碼一律 45 日 | 已明文入 docstring(`release_lag.py:16-22`),生產鏈三重防線中和;研究面二工具補記(§4.3) |

**北極星自檢(本審計之判準,#8 語境)**:每個特徵值問三題——有真實 API 來源嗎(①)?**決策當下真看得到嗎(② 不洩漏)**?out-of-sample 撐得住嗎(③)?本輪審計即是把全生產面板逐一過第②題。三敵人(假資料/偷看未來/自我欺騙)零容忍;資料期限凍結 as-of 2026-05-31(FREEZE),審計與全部修復均在凍結快照內完成、不引入新資料。

---

## §1 審計方法

### 1.1 範圍與輪次

- **第一輪(2026-07-10,逐靶深查)**:**4 個靶點**——估值 `valuation`、毛利週期 `margin_cycle`、IC 研究工具 `run_raw_interaction_ic`、財報 gate `release_lag`——逐一對真實表深查 → 3 項確認洩漏並修復、1 項缺口記錄在案(§2)。
- **第二輪(workflow `wf_947ad3eb`,13 agents 平行對抗)**:掃 5 個特徵模組 `chip` / `concentration` / `phase` / `panel` / `macro` → 1 項 active 洩漏(§3)、2 項 macro 潛伏債(§4)、3 模組判 clean(§5)。
- **修復收尾(2026-07-11)**:chip 洩漏經用戶拍板選項 A 後即日落地+重建+驗收(§3.4、§7)。

### 1.2 對真實表、不對碼面推測

一切判定以 psql 對 `public` schema 真實表複現(#9 三源之 (b) DB query),不以「讀碼推想」定案。本報告定稿時關鍵數字**再次複跑**(查證日 2026-07-11),與 commit 訊息交叉核對;重建前後數字分標、不以舊快照冒充現況。

### 1.3 對抗覆核紀律:每一發現獨立複現才認

每項候選發現須經**獨立第二路徑複現**(另一 agent 或另一查詢路徑)才升格為「確認」;複現失敗即降級或剔除。本紀律於草擬期實際觸發一例:先前工作摘要(及 commit `cd8b35e` 訊息)稱 IC 工具全期聯集「含 132 下市股」,本次以三種 proxy 複查(不在 `TaiwanStockInfo`=0 股;股價序列早收=1 股;`TaiwanStockDelisting` 可對=**12/13 股**,口徑見 §2.3)**皆無法複現 132** → 本文按 #9 改以可複現數字表述(§2.3),原數字作廢、以本報告為準。

### 1.4 審計對象 schema 與結果落點(#20 v1.39.0:純分析附所讀既有表)

本審計不產新表;主審計對象與全部修復落點均為既有表 `feature_values`(完整 schema 見 §6.1)。修復一律走 **writer code 修正 + `scripts/rebuild_feature.py` registry 驅動重建**(#12 不 hand-patch 已 committed 資料),結果冪等落回 `feature_values` 同表。旁及唯讀之 raw 表:`TaiwanStockPrice` / `TaiwanStockPriceAdj` / `TaiwanStock10Year` / `TaiwanStockFinancialStatements` / `TaiwanStockHoldingSharesPer`(6 欄、**無發布日欄**,§3 關鍵)/ `fred_series` / `core_universe` / `core_universe_asof`。

---

## §2 已確認並修復之洩漏(commit `cd8b35e`)

### 2.1 `price_to_10yr`:前向還原分子=未來資訊回溯注入 + 分子分母混口徑

**機轉**。原碼分子讀 `TaiwanStockPriceAdj`(前向還原價):還原因子以**最新資料日為錨點 1.0**,把未來的股利/分割資訊**回溯**乘進歷史價——歷史價因「之後才發生」的事件而改變,即偷看未來(#8)。分母 `TaiwanStock10Year` 卻是 raw 口徑,兩邊除出來既洩漏又混口徑。

**實證**(psql 2026-07-11 複跑):
- adj/raw 比值隨錨點漂移:2330 於 2015-12-31 =**0.7546**、2020-12-31 =**0.9058**,向錨點(`TaiwanStockPriceAdj` max date =**2026-06-17**)趨近 1.0——同一歷史日的「價格」隨 sync 日不同而變,PIT 不成立。
- 分母確為 raw 口徑:2317 之 `TaiwanStock10Year` 最新列存值 **116.01**,≈ raw 收盤 10 年曆法窗均 **117.00**(差 0.85%,窗口定義誤差),遠離 adj 10 年均 **105.35**(差 10.1%)。

**修法**。分子改讀原始 `TaiwanStockPrice`,與 raw-basis 分母同 PIT 口徑——`src/augur/features/valuation.py:35-39`(`_RAW_CLOSE_SQL`,修正註解明載機轉)。

**重建規模**。UPDATE **50,283** / DELETE **673**(raw 缺值列;commit `cd8b35e` 訊息)。現況複核:`feature_values` 中 `price_to_10yr` = **50,283 列 / 31 panel**,與 UPDATE 數一致(10Year 表 2011 起,故 31 panel)。

### 2.2 `gross_margin_pctile`:停報陳舊值冒充「當季」毛利

**機轉**。原碼取「最近一筆已公告 GrossProfit」當作當季毛利,無陳舊上限——對已停報該科目之公司,十幾年前的舊值持續冒充當季(不是偷看未來,而是**假的「現在」**,#15 自我欺騙型)。

**實證**(psql 2026-07-11 複跑):4 檔保險股 **2832 / 2850 / 2851 / 2852** 之 `TaiwanStockFinancialStatements` `type='GrossProfit'` 最末日期**全部= 2010-12-31**(IFRS 後無此科目)——2011 之後的每個 panel 都在用 2010 年的毛利算「當前」毛利率百分位。

**修法**。`src/augur/features/margin_cycle.py:26` 加 `MAX_STALE_DAYS = 400`(≈4 季+緩衝)、`margin_cycle.py:55` 逐 panel 時序判斷:最新已公告毛利季距 panel >400 日即缺列不冒充。**逐 panel 時序**是關鍵——2008–2011 的 panel 當時該值仍新鮮,正確保留,不因「後來停報」回溯抹除(那反而是另一種未來資訊)。

**重建規模**。UPDATE **59,237** / DELETE **368**(commit `cd8b35e`)。現況複核:`gross_margin_pctile` = **59,237 列 / 34 panel**,一致。

### 2.3 `run_raw_interaction_ic.py`:最終名單回填全歷史=存活者偏誤

**機轉**。IC 研究工具原 `SELECT core_universe`(**期末最終 344 股**;psql 複核 `core_universe` = 344 列)回填**所有歷史 panel**——「活到 2026-05-31 的股票」被當作 2011 年的成員,凡曾入選後跌出/下市者一律不見,IC 估計向存活者偏移(#8 的橫斷面版)。

**修法**。改讀 `core_universe_asof` 逐 panel PIT 成員(`scripts/run_raw_interaction_ic.py:74-76`)。

**實證**(psql 2026-07-11 複跑):`core_universe_asof` 全期聯集 **776 股**;期末成員 **344 股**;**432 股**曾為成員但非期末成員(含跌出流動性/規模門檻與下市者)——固定名單版本系統性排除了全歷史 432/776 = 55.7% 曾入選個體。下市對照口徑:**432 股中 12 股**可對到 `TaiwanStockDelisting` 紀錄;全 776 聯集∩delisting =**13 股**(含 1 檔期末成員亦有 delisting 紀錄)。
> 溯源更正:先前摘要與 commit `cd8b35e` 訊息之「含 132 下市」經三 proxy 覆核未能複現(§1.3),以本段可複現數字為準。

### 2.4 附帶記錄(非修復):`release_lag` 金融業 60 日缺口

金融保險/證券/期貨業 Q1/Q3 法定申報期限為 **60 日**(證交法 §36 但書),碼一律 45 日(`src/augur/features/release_lag.py:29` `FIN_LAG_QUARTER = 45`)→ 對該類股財報「偏早可見」之潛在 #8 缺口。**現況休眠**(詳 §4.3):陳舊守衛已中和生產鏈、panel 皆季末、無現行金融股財報消費者;已明文記錄於 `release_lag.py:16-22` docstring(「未實作前勿讓 panel 消費金融股財報」),留待引入產業別分支時修。

---

## §3 `chip.top_holders_pct`:active 洩漏 → 已拍板 1A、已修復並完成重建(待 commit)

### 3.1 機轉(修正前)

大戶比讀集保 `TaiwanStockHoldingSharesPer`(TDCC 股權分散表),修正前取 `date <= panel_date ORDER BY date DESC LIMIT 1`、**無任何公布 gate**。但該表是**延後公布的結算快照**:現行為週頻週五結算、TDCC 於**次週**才公布——快照「date=週五」當天乃至其後數日,市場上根本看不到這筆資料。`date <= panel` 會在快照日當天即選到它 → **決策當下看不到的資料進了面板 = active 洩漏**(北極星第②題不過)。

修正前碼內自認(HEAD `7fd3426` 版 `chip.py:16-17`):「籌碼盤後公布之 T+1 規則此版採保守 date<=panel_date 同日含、**上線後待 probe 公布時刻**」——此 placeholder 假設對「盤後當晚公布」的日頻法人資料成立(第二輪判 clean),對**延後一週公布**的集保表不成立。

### 3.2 影響面實證(修正前口徑;psql 2026-07-11)

| 證據 | 數字 |
|---|---|
| 暴險列數(修正前) | `top_holders_pct` = **65,923 列 / 32 panel(2010-12-31 → 2026-05-31)**,含 live panel(rebuild 前快照) |
| 快照頻率 | 638 個 distinct 快照日(2010-01-29 ~ 2026-06-18),其中 **532 個為週五**;**2010–2014 為月頻(每年 12 快照日)、2015 年中起轉週頻**(2015=39、2016=50)——月頻年代快照多落月底 |
| 無公布日欄 | 表僅 6 欄(date, stock_id, HoldingSharesLevel, people, percent, unit),**無 release/announcement 欄** → gate 只能外加 |
| gate 缺口全面性 | 全 32 panel 之表層最近快照距 panel 之 gap 分布:**0 日(8 panel)/ 1(4)/ 2(6)/ 3(5)/ 4(3)/ 5(3)/ 6(3)**——max gap 僅 6 日 |
| live 實例 | panel 2026-05-31(週日)舊碼實選 **2026-05-29(週五)**快照——該快照公開日落在 6 月初,panel 當下不可見 |

**誠實表述暴險程度**(TDCC 實際公布時刻**零來源**、待 probe,#9):gap=0 之 **8 個 panel**(panel 日=快照結算日)**幾乎確定**選到未公開資料;gap 1–6 之 24 個 panel,若 TDCC 實際公布 lag 小於該 gap 則所選快照**可能已公開**、無時戳無法排除——依 #8 寧殺勿縱,**保守視全 32 panel / 65,923 列為暴險**,此即修復採全量重建之依據(非斷言「每列必然洩漏」)。

### 3.3 為何屬「active」而 macro 屬「latent」

`top_holders_pct` 是 35 生產特徵之一、每期落 `feature_values` 且進下游消費;macro 兩埋雷(fred `realtime_start` 構造、vintage gate 零程式)則零現行 feature 消費者——`feature_values` 全 **35 特徵中 0 個是 macro**(psql `count(distinct feature)`=35、逐一檢視無 macro 名)。前者修正前每天都在污染,後者是引信未接的雷(§4)。

### 3.4 拍板與落地(2026-07-11 審計 1A)

用戶拍板**選項 A:保守 gate(+7 日下界)立即修**(原選項 B「先記錄待 probe」不採:期間下游持續染污、且 probe 需觸外部即時來源與 FREEZE 有張力)。已全數落地(工作樹、待 commit):

- **gate SSOT**:`src/augur/features/release_lag.py:31-32` `HOLDINGS_LAG_DAYS = 7`;`:57-59` `holdings_release_date(d)=d+7`;`:62-66` `holdings_visible_cutoff(panel)=panel−7`(供 SQL 直用)。7 日=「次週五必已公開」之保守下界,與既有財報/月營收 gate 同模式;待 probe 實測後可精修(#27,由保守往精確、方向單向安全)。
- **消費端**:`src/augur/features/chip.py:83-87` `_HOLD_SQL`(gate 註 `:80-82`);`:144-145` f4 改傳 `release_lag.holdings_visible_cutoff(panel_date)` 為 cutoff;docstring `:17-18` 明載「已套發布日 gate(2026-07-11 審計 1A)」。
- **重建**:`scripts/rebuild_feature.py:30` registry 加 `top_holders_pct` → `compute_chip_features`(簽名約定 `:9` 天然相容,零改工具邏輯 #29c);`--feature top_holders_pct --run` 於 2026-07-11 09:27 啟動、歷時 ~50 分完成(逐 panel 交易、冪等)。
- **重建結果**(psql 完成後實查):`top_holders_pct` = **65,530 列 / 32 panel(2010-12-31 → 2026-05-31)** = **UPDATE 65,530 / DELETE 393**(65,923−65,530;cutoff 收緊後無可見快照之列,誠實刪列 #1);`feature_values` 總列 **2,418,655** = 2,419,048 − 393,守恆吻合。
- **效果**:每 panel 改用「已公開」快照(晚一週視角),**只會晚看、不會偷看**;代價=訊號多約一週滯後(週頻資料本質)。驗收全過,見 §7。

---

## §4 潛在債(latent debt)——現況零 active 消費者,但埋雷明確、觸發條件可預告

> 本節三項均**非 active 洩漏**(現況無生產鏈路消費到錯誤值),但皆屬「一旦接上消費者即沉默污染」型缺陷。每項列:事實(實證)→ 為何現況不爆 → 修法 → 觸發條件。

### 4.1 macro Tier A:`realtime_start` 戳記為碼構造、非實測發布時刻

**事實(psql + code 實證)**:
- `fred_series` 共 **31** 個 series:**22 檔 Tier A**(全部列 `realtime_start = date`)+ **9 檔 Tier B**(含真 vintage)——以「該 series 是否存在 `realtime_start ≠ date` 之列」機械二分,與 `macro.py:36-70` `SERIES` 宣告的 22 `_a()` + 9 `_b()` 完全吻合。
- Tier A 例 DFF:**26,299 / 26,299 列全部 `realtime_start = date`**——此非 API 實測,而是 `src/augur/ingestion/fred.py:106` 的碼構造:`"realtime_start": o.get("realtime_start") if vintage else o.get("date")`(非 vintage 一律注入觀測日本身)。
- 問題:`macro.py:8-9` 斷言 Tier A「當日觀測值、當天即知……正確、非近似」,但 FRED 每日數列多為**美東時間盤後/次日發布**,台北時區之 panel 若當日引用=拿「台北當天尚看不到」的值(T+1 可見性斷言未經實測,#8/#15)。

**為何現況不爆**:`feature_values` 全 35 特徵**零 macro 特徵**;全 repo `fred_series` 引用僅 ingestion / audit / catalog **八檔**(`ingest.py`/`sync.py`/`fred.py`/`catalog/__init__.py`/`audit/reconcile.py`/`scripts/reconcile_audit.py`/`sync_macro.py`/`full_market_sync.py`;grep 實查),`src/augur/features/` 與 evaluation **零消費者**。洩漏鏈路根本不存在。

**修法**:(a) 消費端統一對 Tier A 施 **+1 日保守 lag**(台北視角 T+1 才可見),寫進 §4.2 的 `macro_vintage.py` reader 介面、不改存量資料(戳記=觀測日仍是真值,#12 不 hand-patch);或 (b) 上線階段 probe 各 series 實際發布時刻精準化。**觸發條件**:任何 Tier A series 首次進入 feature/回測且以「panel 當日可見」口徑消費之時——接入前必須先落 (a)。

### 4.2 macro Tier B:消費端「濾版 gate」只活在註解、零程式強制

**事實(psql + code 實證)**:
- Tier B 9 檔(CPIAUCSL / GDPC1 / INDPRO / M2SL / PAYEMS / UMCSENT / UNRATE / WALCL / WRESBAL)**vintage 存真**:UNRATE `2020-01-01` 三版(`realtime_start` 2020-02-07=3.6 → 2021-01-08=3.5 → 2024-01-05=3.6);GDPC1 單一觀測日最深 **21 版**(1993-01-01)。資料層合格。
- 但「feature 層才能取面板日當下真看得到那版」的 PIT 規則**只存在於 `macro.py:10-12` 的 docstring**——repo 內**不存在任何**以 `realtime_start <= panel_date` 濾版的 reader 程式。未來任何人 `SELECT value ... ORDER BY realtime_start DESC LIMIT 1`(拿最新修訂版)即無聲洩漏,且因 vintage 資料「看起來很 PIT」而更難察覺。

**為何現況不爆**:同 4.1——零消費者。

**修法**:建 `src/augur/features/macro_vintage.py` PIT reader(規畫見 §6.2b),把濾版從註解升級為**介面上唯一的取值通道**——feature 層只准 import 此 reader、不准裸 SQL 摸 `fred_series`。**觸發條件**:任何 macro 特徵設計拍板、接入 `feature_values` 之前;reader 先行、特徵後至(順序不可反)。

### 4.3 release_lag:金融保險業 Q1/Q3 法定 60 日 vs 碼一律 45 日

**事實(code 實證)**:`release_lag.py:43` 對 Q1/Q2/Q3 財報一律 `FIN_LAG_QUARTER = 45`(`release_lag.py:29`),無產業分支;金融保險/證券/期貨業法定 Q1/Q3 為 **60 日**(證交法 §36 但書)→ 對該類股財報**低估滯後 15 日**=偏早可見(#8)。缺口已於第一輪審計明文記錄在 `release_lag.py:16-22`。

**為何現況不爆(生產鏈三重防線)**:唯一消費 `financial_released` 的**生產特徵** `gross_margin_pctile`(`margin_cycle.py`)① 已被 `MAX_STALE_DAYS=400` 陳舊守衛(`margin_cycle.py:26,55`)排除金融股(IFRS 後無 GrossProfit、停於 2010-12-31);② 生產 panel 皆季末、45/60 差異落在季中窗;③ 現況無其他財報特徵生產消費者。

**研究面補記(防線不涵蓋處,誠實)**:三重防線只涵蓋**生產鏈**。研究工具 `scripts/verify_fundamental_candidates.py:46,106-107` 與 `scripts/run_cross_table_interaction_scan.py:112,137` 亦經 `release_lag` gate 消費財報/月營收——金融股 60 日缺口對此二工具之**研究結論**(候選驗證/交互掃描)同樣偏早可見 15 日;其產出未直接入生產,但未來若有金融股財報腿之候選經此鏈提拔,結論須重驗。

**修法**:令 `financial_release_date` 產業感知(收 `stock_id → industry_category`,金融類 Q1/Q3 用 60)並穿線全消費者逐檔驗口徑;或上線階段接 TWSE/MOPS 真實公告日精準 gate(超出 as-of FREEZE、屬未來階段)。**觸發條件**:panel 改為季中/月頻 **且** 出現消費金融股財報之特徵——二者同時成立前,此債休眠;成立前**不得**先開該消費(`release_lag.py:21-22` 已明文此禁)。

---

## §5 全模組健康度總表(8 特徵模組 + 1 宇宙/消費端)

`src/augur/features/` 實有 8 個特徵模組(chip / concentration / macro / margin_cycle / panel / phase / release_lag / valuation;ls 實查);universe gate 屬宇宙層、其修復落在消費端 script,單列不混計。

| # | 模組(檔) | verdict | 一句話 |
|---|---|---|---|
| 1 | valuation(`src/augur/features/valuation.py`) | **已修**(cd8b35e) | `price_to_10yr` 分子改讀 `TaiwanStockPrice`(`valuation.py:35-39`),消「前向還原把未來股利/分割因子回溯注入」之洩漏+raw-basis 10 年線混口徑;重建 UPDATE 50,283 / DELETE 673(現存 50,283 列 psql 複核吻合) |
| 2 | margin_cycle(`margin_cycle.py`) | **已修**(cd8b35e) | `MAX_STALE_DAYS=400` 陳舊守衛(`:26,:55`)擋 4 保險股 2010 停報毛利冒充當季(逐 panel 時序判定、2008-2011 panel 正確保留);重建 UPDATE 59,237 / DELETE 368(現存 59,237 列吻合) |
| 3 | chip(`chip.py`) | **已修+重建完成(工作樹、待 commit)** | 原為全系統唯一 active 洩漏:`top_holders_pct` 讀集保延後公布快照(638 快照日 / 532 週五 / 無發布日欄)僅 `date<=panel` 無 gate → 修正前 65,923 列 / 32 panel 保守視為全暴險(含 live 2026-05-31);審計 1A 拍板後套 `holdings_visible_cutoff = panel−7` gate(`chip.py:144-145`、`release_lag.py:31,62-66`),重建 UPDATE 65,530 / DELETE 393、驗收全過(§7) |
| 4 | concentration(`concentration.py`) | clean | 量能 Gini / max-share 純 ≤t 後向泛函、還原因子在比值構造中相消,無外源時點欄 |
| 5 | macro(`macro.py`) | **latent**(零 active) | `feature_values` 35 特徵零 macro、`fred_series` 零 feature 消費者;兩埋雷(Tier A 戳記 §4.1 / Tier B 消費 gate 缺席 §4.2)觸發條件明確 |
| 6 | phase(`phase.py`) | clean | 價格/法人流相位皆 ≤t 自身極值後向窗;法人買賣盤後當晚公布、panel 日可見性成立 |
| 7 | panel(`panel.py`) | clean | 還原價動能/波動/流動性皆相對量、還原因子比值相消(價格「水位」型洩漏落在 valuation、已修);recency gate 防 stale 偽 as-of |
| 8 | release_lag(`release_lag.py`) | 潛在債已明文 | 金融業 Q1/Q3 法定 60 日 vs 碼一律 45(§4.3);生產鏈三重防線下休眠(研究面二工具補記在案),觸發條件已寫入 `:16-22` |
| 9 | 宇宙/消費端(`src/augur/universe/core_gate.py` + `scripts/run_raw_interaction_ic.py`) | **已修**(cd8b35e,消費端) | `core_universe_asof`(`core_gate.py:40`、`build_universe_asof :202`)供逐 panel PIT 成員;IC 工具已由「最終 344 股回填全 panel」改用之(`run_raw_interaction_ic.py:74-76`;全期聯集 776 股、432 股非期末成員、其中 12 檔對得 delisting——消 survivorship) |

---

## §6 對應 table schema 與 python 程式規畫(#20 v1.39.0)

### 6.1 所讀關鍵表 schema(psql information_schema 實查;本審計**不產新表**,結果一律落既有 `feature_values`)

**`feature_values`(結果落表;三輪修復皆=UPDATE/DELETE 既有列,零 DDL)**
```
panel_date  date          NOT NULL ┐
stock_id    varchar       NOT NULL ├ PK (panel_date, stock_id, feature)
feature     varchar       NOT NULL ┘
value       numeric       NOT NULL
現況(重建後):2,418,655 列 / 35 特徵 / 35 panel(2007-12-31 → 2026-05-31)
```

**`TaiwanStockHoldingSharesPer`(chip f4 輸入;結算快照、無任何發布日欄 → gate 只能外加)**
```
date                date     ┐
stock_id            varchar  ├ PK (stock_id, date, HoldingSharesLevel)
HoldingSharesLevel  varchar  ┘
people / percent / unit  numeric
覆蓋 2010-01-29 ~ 2026-06-18;638 快照日(532 週五);2010-2014 月頻(12/年)、2015 年中起週頻
```

**`fred_series`(macro 輸入;PK 含 realtime_start=vintage 存真的結構基礎)**
```
series_id       varchar  ┐
date            date     ├ PK (series_id, date, realtime_start)
realtime_start  date     ┘
value           numeric
```

**元件/端點**:本審計無新服務端點(N/A);元件=修正之 writer 三檔+gate 模組+重建工具(下表)+一支未來 PIT reader(6.2b)。

### 6.2 python 程式規畫(檔 / 函式 / 職責 / 簽名 / 輸入輸出表)

**(a) chip 修復(審計 1A 已拍板、已落地——本表為完成式對帳,非待辦)**

| 檔 | 函式/常數(行號=工作樹) | 職責與簽名 | 輸入→輸出 |
|---|---|---|---|
| `src/augur/features/release_lag.py` | `HOLDINGS_LAG_DAYS = 7`(`:31`);`holdings_release_date(d: date) -> date`(`:57-59`,=d+7);`holdings_visible_cutoff(panel_date: date) -> date`(`:62-66`,=panel−7) | 集保快照「公開可得日」SSOT,與既有 `revenue_*` / `financial_*` 同型式;7 日為保守下界、probe 後回填實測值(#27) | 純日期算術、無表 |
| `src/augur/features/chip.py` | f4 段(`:144-145`)以 `release_lag.holdings_visible_cutoff(panel_date)` 為 `_HOLD_SQL`(`:83-87`)之 cutoff 參數 | `top_holders_pct` 只取「已公開」快照;gate 值不寫死於 chip、引 release_lag 常數 | `TaiwanStockHoldingSharesPer` → dict |
| `scripts/rebuild_feature.py` | `_REBUILDERS`(`:27-31`)含 `"top_holders_pct": ("augur.features.chip", "compute_chip_features")`(`:30`) | registry 驅動重建;compute 簽名 `(cur, sid, panel_date) -> {feature: value}` 與工具約定(`:9`)天然相容,零改工具邏輯(#29c);`--feature top_holders_pct --run` 逐 panel 交易(`:54-70`)、冪等、算不出誠實 DELETE | `feature_values` 65,923 列 → UPDATE 65,530 / DELETE 393(已執行,§7 驗收) |

**(b) macro PIT reader(觸發時建;§4.1/4.2 修法。時點見 §8-2)**

| 檔 | 函式 | 職責與簽名 | 輸入→輸出 |
|---|---|---|---|
| `src/augur/features/macro_vintage.py`(新) | `asof_value(cur, series_id: str, panel_date: date) -> float \| None` | **介面上強制**濾版:`WHERE series_id=%s AND date <= %s AND realtime_start <= %s ORDER BY date DESC, realtime_start DESC LIMIT 1`;無合格版→回 None(缺列 #1、不 fallback 最新版);feature 層禁裸 SQL 摸 `fred_series`、只准經此 reader | `fred_series` → 純函式回值(不落表;落表發生在未來 macro 特徵 writer) |
| 同檔 | `_tier(series_id) -> str`(讀 `macro.SERIES` 宣告,`macro.py:36-70` 為 SSOT) | 判 A/B:Tier A 於 `asof_value` 內另施保守 lag——比較基準改 `realtime_start <= panel_date − TIER_A_LAG_DAYS`(`TIER_A_LAG_DAYS = 1`,台北視角 T+1;是否併入由 §8-2 拍板) | `macro.SERIES` → 'A'/'B' |
| 同檔 | 驗收 pytest(觸發時同交):`UNRATE date=2020-01-01, panel=2020-06-30` 須回 **3.6**(realtime_start 2020-02-07 版)、**非** 2021-01-08 修訂版 3.5 | 以真 vintage 資料錨定濾版正確性(#9 oracle 錨定) | `fred_series` → assert |

**(c) 不動項**:`fred.py:106` 戳記構造**不改存量**(觀測日是真值;可見性修正歸消費端 reader,#12);`release_lag.py` 金融 60 日維持明文休眠(觸發條件到達才動,#3 最小邊界);`TaiwanStockHoldingSharesPer` 原表不加欄(無公布日可回填、gate 住 release_lag 純函式)。

---

## §7 分階段與驗收(#20 v1.39.0)

### 7.1 分階段(S1–S5;S1–S3 已完成)

| 階段 | 內容 | 狀態 |
|---|---|---|
| S1 | 第一輪逐靶審計+修復(valuation / margin_cycle / IC 工具)+ release_lag 缺口記錄 | **完成**,commit `cd8b35e`(2026-07-11 08:10) |
| S2 | 第二輪 13-agent 平行掃描(chip / concentration / phase / panel / macro) | **完成**(wf `wf_947ad3eb`) |
| S3 | chip 審計 1A:拍板選項 A → gate 落地(3 檔)→ 全量重建 → 驗收 | **完成**(2026-07-11;重建 09:27 起 ~50 分;驗收 7.2 全過) |
| S4 | S3 三檔 + 本報告 commit | **待用戶授權**(#14,AI 不自行 commit) |
| S5 | 觸發制未來項(FREEZE 後/上線階段):TDCC 公布時刻 probe → gate 7→實測值精修;macro `macro_vintage.py` reader(或依 §8-2 提早);FRED Tier A 台北可見時點 probe;金融 60 日產業分支 | 登記於 §8,不排程(FREEZE) |

### 7.2 S3 驗收(判準 → 實測結果;psql 2026-07-11 重建完成後實查,**全過**)

| # | 驗收判準 | 實測結果 |
|---|---|---|
| 1 | 列數守恆:重建後列數 = 修正前 − DELETE;UPDATE = 重建後列數 | ✓ 65,530 = 65,923 − 393;UPDATE 65,530 |
| 2 | panel 完整性:panel 數/範圍不變 | ✓ 32 panel、2010-12-31 → 2026-05-31 不變 |
| 3 | 全表守恆:`feature_values` 總列 = 前值 − DELETE;35 特徵 / 35 panel 不變 | ✓ 2,418,655 = 2,419,048 − 393;35 / 35 不變 |
| 4 | gate 性質:每 panel 於 cutoff=panel−7 下可選之表層最近快照距 panel ≥ 7 日 | ✓ 全 32 panel gap ∈ [7, 33](max 33 = 2014-12-31,月頻年代選上月月底快照、屬資料頻率本質非缺陷) |
| 5 | live 抽查(逐股層):2330 @ panel 2026-05-31 值須來自 ≤2026-05-24 快照 | ✓ 現值 85.39 = 2026-05-22 快照 percent;舊碼將選 2026-05-29(85.41,panel 當下未公開) |
| 6 | DELETE 語意:被刪列=cutoff 收緊後無可見快照者(誠實缺列 #1),非誤刪 | ✓ 393 列,佔 0.6%;與「首快照落於 (panel−7, panel] 之新上市/新入級距股」語意一致 |
| 7 | 冪等:逐 panel 交易、重跑同值 | ✓ 設計保證(`rebuild_feature.py:54-70` 逐 panel commit),同工具已於 S1 兩特徵實測 |

**未來項驗收(S5 觸發時)**:macro reader 之 UNRATE vintage pytest(§6.2b 表末列);TDCC probe 後 gate 精修須重過本表 #1–#6。

---

## §8 殘留決策清單(決策層、待用戶)

| # | 決策 | 選項/內容 | 影響 / 建議 |
|---|---|---|---|
| 1 | **S4 commit 授權**(#14) | chip 修復三檔(`chip.py` / `release_lag.py` / `rebuild_feature.py`)+ 本報告 | 洩漏本體已消、驗收已過;未 commit 前修正僅存於工作樹(有遺失風險)。建議儘速授權;commit 訊息應含 UPDATE 65,530 / DELETE 393 與「132 下市」更正(§2.3) |
| 2 | **macro PIT reader 建置時點**(含 Tier A +1 日 lag 是否併入介面) | **A**:現在即建 `macro_vintage.py`(雷區先圍欄、防未來裸 SQL)/**B**:待 macro 特徵設計拍板時一併建(#3 最小邊界:現況零消費者) | 二者皆守「reader 先於特徵」順序即可;差別僅在圍欄早晚。A 的成本是一支 ~30 行純函式+一條 pytest(§6.2b) |
| 3 | **probe 排程**(超出 as-of FREEZE、屬上線階段) | 集保 `TaiwanStockHoldingSharesPer` 實際公布時刻(→gate 7 日精修,#27)+ FRED Tier A 各 series 台北視角可見時點(→lag 分支精修) | FREEZE 期間不排程(CLAUDE.md 資料期限凍結),僅登記於本清單;probe 後精修方向均為「由保守往精確」、單向安全 |

---

## 附:數字溯源(#9/#10)

本報告所有計數之來源(psql 直查 `augur` 庫,2026-07-11;行號=本日 Read 實讀):

- **面板**:2,419,048(重建前快照)/ 2,418,655(重建後)/ 35 特徵 / 35 panel / 2007-12-31→2026-05-31。
- **chip**:65,923(修正前)→ 65,530 列 / 32 panel;UPDATE 65,530 / DELETE 393;638 快照日(2010-01-29~2026-06-18)/ 532 週五 / 2010-2014 每年 12 快照日;gap 分布 0:8/1:4/2:6/3:5/4:3/5:3/6:3;新 gate gap ∈[7,33];2330 抽查 85.39@2026-05-22 vs 85.41@2026-05-29。
- **§2**:50,283/31 panel、59,237/34 panel、673/368(cd8b35e 訊息+現況複核);2330 adj/raw 0.7546/0.9058、Adj max 2026-06-17;2317 10Year 116.01 vs raw 均 117.00 vs adj 均 105.35;4 保險股 GrossProfit max 皆 2010-12-31;core_universe 344 / asof 聯集 776 / 非期末 432 / delisting 對照 12(432 中)與 13(776 中)。
- **macro**:31 series = 22 Tier A + 9 Tier B(機械二分);DFF 26,299/26,299 全 `realtime_start=date`;UNRATE 2020-01-01 三版(3.6/3.5/3.6);GDPC1 1993-01-01 共 21 版;`fred_series` 消費者 8 檔(grep)、features/evaluation 零。
- **行號**:`chip.py:17-18,80-87,144-145`、`release_lag.py:16-22,29,31,43,57-66`、`rebuild_feature.py:9,27-31,54-70`(以上=工作樹未 commit 版);`valuation.py:35-39`、`margin_cycle.py:26,55`、`macro.py:8-9,10-12,36-70`、`fred.py:106`、`core_gate.py:40,202`、`run_raw_interaction_ic.py:74-76`、`verify_fundamental_candidates.py:46,106-107`、`run_cross_table_interaction_scan.py:112,137`(以上=HEAD `7fd3426`)。
- **git**:`cd8b35e` 2026-07-11 08:10:07 +0800(`git show -s`);HEAD `7fd3426`;工作樹 M 三檔屬本審計、另 4 檔屬他工作流。
