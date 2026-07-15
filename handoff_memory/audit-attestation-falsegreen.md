---
name: audit-attestation-falsegreen
description: "audit「✅ PASS」曾是假綠(死表空視窗靜默 PASS);blocker 已修 coverage_gap;#29 audit-of-audit findings;v1.28 library 自測入憲"
metadata: 
  node_type: memory
  type: project
  originSessionId: 778040ca-21b5-4b60-ad2d-0fad302930ca
---

2026-07-14 對抗審查(#29 audit-of-audit,21 agents)證實 daily_maintenance 的「✅ PASS（DB byte-equal API，無幻像）」**曾是假綠**——**開賽 gate 差點建在假地基上**。

**核心 blocker(已修)**:by-date 死表(max(date) 跌破滾動下界 since=today−14)→ reconcile_by_date 查 0 列 → matched=0/incomplete=False → verdict 當「比過且乾淨」PASS。**閘分不清「沒比對」與「比過乾淨」**。實錘死表:USStockPrice(死25天)、TaiwanStockParValueChange(~11月)、TaiwanBusinessIndicator/SecuritiesTraderInfo/StockDelisting。
- **修**:reconcile_by_date 空視窗標 `coverage_gap`+assert since≤until;verdict passed 納入 not coverage_gap;daily_maintenance headline 列「未對帳 N 表」+ exit **rc=2 終態**(重試不會綠、須人 re-sync/exempt)。回歸鎖入 `python -m augur.audit.reconcile --selftest`。
- **死表定性(#25 探測)**:上游 FinMind 仍有料(AAPL 07-10 有)→**本機漏 sync、非死 feed**→ sync_by_date 可補([[cross-machine-handoff]] 未涵蓋)。補救待額度恢復+處置拍板(Task 追蹤)。

**#29 全 6 findings 已處置(2026-07-14 hugo 逐項拍板)**:(b)旗艦抽樣框 warrant 污染→改真名冊∩表(2→32 真股/40);#29-1 by-date 交叉驗證加值比對(PK 存在但值不符=真 VM、不當乾淨扣抵,回歸鎖入 reconcile --selftest);#29-2 roster 部分覆蓋傳 verdict.sampled+headline「⚠部分覆蓋 N 表」誠實揭露(不擋綠、FinMind throttle 揭露債);死/空表全分類:**USStockPrice→dim_only 豁免**(by-date 回 PK-null 髒列不可 sync〔sync.py:501 pk-null-needs-dim〕+零預測用途、per-ticker 放量不划算)、**BusinessIndicator/ParValueChange/SecuritiesTraderInfo/StockDelisting→cadence 豁免**(低頻/事件表,滾動窗常空非死)。catalog attestation_mode 值域擴 cadence+dim_only(migrate codified)。

**--audit-all sync 浪費 → (c) --audit-only 修(2026-07-14)**:--audit-all 先 sync_all_by_date 全 88 表會回填停更多年之 snapshot 表(JapanStockInfo 自 2019 逐月)——sync 了會豁免的表、燒光額度。修=`daily_maintenance --audit-only`(跳 pre-sync、audit_set 由 catalog reconcile_scope IS NOT NULL **且 to_regclass 表實存** 取、直接對帳現況)。另加 audit 迴圈 **per-dataset try/except 韌性**(一表 schema/DB 錯記 incomplete 續跑不崩全部+conn.rollback 清錯態)——--audit-only 暴露 --audit-all 一直用 sync 預篩掩蓋的 catalog 錯配。

**誠實生產判決(2026-07-14 --audit-only 首跑):❌ FAIL**(VM33/EX4999/MIS5127)——**不再假綠、audit 說真話**。三類待辦**已全治本**:①11 張 tick/intraday catalog-有-DB-無表→**table-exists 過濾排除**;②2 空視窗表→FutOptTickInfo(合約 info)snapshot、CapitalReductionReferencePrice(事件)cadence;③9 真差異表根因全查明:
- **EX4999=TaiwanFuturesSpreadTick tick 串流假象**(全欄 PK+API 回不同 tick 子集,零預測用途)→**intraday 豁免新模式**;
- **VM33/MIS14=3 張 roster 表(DayTrading/PriceLimit/StockInfo)邊緣日 staleness**——實證 DayTrading VM32 全是 07-14(lag=1 邊緣)DB Volume=0(過早 sync 拿到 0、resume 看 max(date) 不回抓),API 有真值;re-sync 該日即補(非修訂、真舊)。
**治本=(a) roster-heal**(hugo 拍板):compare 回 fix_keys(VM+MIS 鍵)→reconcile_per_stock 聚合 fix_dates→daily_maintenance roster 分支對 diff 日 sync_by_date 重抓再驗(與 by-date heal 對稱);實證 PriceLimit VM1→heal 07-14→VM0 PASS。**根治「roster 表邊緣過早 sync 舊值卡住(--heal 原只補 by-date)」**。catalog 錯配 2 表(FutOptDailyInfo/ConvertibleBondInfo 無 date 卻 by-date)已歸 snapshot。attestation_mode 值域:byte/snapshot/restating/coverage/cadence/dim_only/intraday。

**v1.28 入憲(2026-07-14 hugo 拍板)**:CLAUDE #18 原「library 不需指令矩陣」**廢止**→ library 模組須執行指令矩陣=自測 CLI(`python -m augur.<pkg>.<mod> --selftest`,零 DB/API 純紅綠)。**全 74 支已補齊+實跑 71/71 全綠**(把不變式固化成回歸鎖)。先例=reconcile/admission。

**Why**:靈魂「寧誠實紅、不假綠」;假綠燒 hugo 親簽 gate=不可逆。**看到 audit「PASS」先問:是真比對過,還是空視窗/抽樣掃到地毯下?**

**--audit-only --heal 收斂至 VM0/EX0(2026-07-14)**:多輪 --audit-only 生產跑逐一揪隱形 blocker——③ tick/roster staleness 治本後,VM=0/EX=0(FinMind 資料全乾淨)。殘留靠**incomplete 表名診斷**(verdict 加 incomplete_tables 列名+headline「未完整 N 表(...)」,#8 不藏錯)才揪出:2 by-dim-id 表 fetch 失敗擋綠——(1)**TaiwanStockTotalReturnIndex** datalist=0(FinMind 無此 dataset 維度端點)→ reconcile_by_dim_id 加**退回表內 distinct dim**(TAIEX/TPEx)→PASS;(2)**fred_series** 是 FRED 資料被 by-dim-id 誤路由打 FinMind→daily_maintenance 加 **fred 分支走 reconcile_fred**(macro.vintage_map()、31 series、FRED 額度不佔 FinMind);路由修後 fred_series 顯 FRED 資料真差異 EX3/MIS66(sync 落後+微 restatement,FRED 域殘留)。**教訓:coverage_ok 計算但 verdict 不消費(news coverage FAIL 印出卻不 gate);verdict.passed=VM0∧EX0∧¬incomplete∧¬coverage_gap,MIS 不 gate**。

**How to apply**:全量誠實 attest=`daily_maintenance --audit-only --audit-days 14 --heal`(--audit-only 跳 pre-sync 浪費、table-exists 過濾、韌性 try/except)。日常查 `verify_knowledge_admission_health.py`。攸關開賽=E1_raw_reconcile_exit;真綠須 FinMind VM0/EX0(已達)+ fred_series FRED 域收尾。見 [[jian-a-admission-hardening]]、[[augur-validation-master-plan]]、[[quota-error-discipline]]。


**fred_series 收尾→綠(2026-07-14 hugo (a) 拍板)**:catch-up(sync_fred 補 MIS 66→0)+ reconcile_fred Tier A restatement 容忍**擴 (a)**:DB 有、API 現無、且 date ≤ API max 之列=FRED 修訂/aged(把觀測 NaN 化,BAMLH0A0HYM2 2023-07-04~14 落 API min 2023-07-17 前 實證;FRED sync 決定性→DB 只有 FRED 曾回列→必合法 restatement)→ 不計 EX。守衛:僅 ≤API max(晚於=未來可疑仍留 EX 紅旗 #15)。fred_series EX3→0 PASS。**至此全資料(FinMind+FRED)VM0/EX0=誠實真綠達成**。