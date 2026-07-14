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

**#29 其餘 findings(待判準,未修)**:①roster-scoped 抽樣 40/3114=1.3% 覆蓋卻過綠(verdict 不讀 sampled)——HANDOFF 記為 FinMind throttle 揭露債;②by-date 交叉驗證(A案)只比 PK 不比值→值損壞列可逃 EX+VM。已修者=旗艦抽樣框 warrant 污染((b):抽樣框改真名冊∩表,旗艦 2→32 真股/40)。

**v1.28 入憲(2026-07-14 hugo 拍板)**:CLAUDE #18 原「library 不需指令矩陣」**廢止**→ library 模組須執行指令矩陣=自測 CLI(`python -m augur.<pkg>.<mod> --selftest`,零 DB/API 純紅綠)。**全 74 支已補齊+實跑 71/71 全綠**(把不變式固化成回歸鎖)。先例=reconcile/admission。

**Why**:靈魂「寧誠實紅、不假綠」;假綠燒 hugo 親簽 gate=不可逆。**看到 audit「PASS」先問:是真比對過,還是空視窗/抽樣掃到地毯下?**

**How to apply**:日常查 `python scripts/verify_knowledge_admission_health.py`(admission 側)+ audit rc 三態(0綠/2終態紅含 coverage_gap/3可重試)。攸關開賽=E1_raw_reconcile_exit 唯一紅、attest 真綠才翻;真綠須 dead-table 補回或誠實豁免。見 [[jian-a-admission-hardening]]、[[augur-validation-master-plan]]、[[quota-error-discipline]]。
