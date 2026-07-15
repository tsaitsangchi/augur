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

**⚠ --audit-all sync 浪費(2026-07-14 發現,未修)**:daily_maintenance --audit-all 先 sync_all_by_date 全 88 表,會**回填停更多年之 snapshot 表**(JapanStockInfo 自 2019 逐月)——而 audit 階段又豁免它們=sync 了會豁免的表、燒光額度(3→3940/6000)audit 前就耗盡。被審表(TW 價量/UK/JP/EU Price)其實都當前。修法待拍:(b)sync 前跳過 audit-豁免表 / (c)audit 只跑當前 DB。生產 audit 尚未取得真綠、待此優化後另跑。

**v1.28 入憲(2026-07-14 hugo 拍板)**:CLAUDE #18 原「library 不需指令矩陣」**廢止**→ library 模組須執行指令矩陣=自測 CLI(`python -m augur.<pkg>.<mod> --selftest`,零 DB/API 純紅綠)。**全 74 支已補齊+實跑 71/71 全綠**(把不變式固化成回歸鎖)。先例=reconcile/admission。

**Why**:靈魂「寧誠實紅、不假綠」;假綠燒 hugo 親簽 gate=不可逆。**看到 audit「PASS」先問:是真比對過,還是空視窗/抽樣掃到地毯下?**

**How to apply**:日常查 `python scripts/verify_knowledge_admission_health.py`(admission 側)+ audit rc 三態(0綠/2終態紅含 coverage_gap/3可重試)。攸關開賽=E1_raw_reconcile_exit 唯一紅、attest 真綠才翻;真綠須 dead-table 補回或誠實豁免。見 [[jian-a-admission-hardening]]、[[augur-validation-master-plan]]、[[quota-error-discipline]]。
