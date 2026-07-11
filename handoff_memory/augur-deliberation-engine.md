---
name: augur-deliberation-engine
description: 本地審議引擎效力成立——GATE PASS(gate_4304;+46.7pp/假確認0/McNemar 3.6e-12);A5 複量報告已交;F1 旗標仍關待 hugo 拍板翻;L2 cron 待掛
metadata: 
  node_type: memory
  type: project
  originSessionId: b066145f-886c-4e08-a8ce-952b36c108ab
---

本地 ultracode 引擎 2026-07-11 態:P0 三 blocker 封(B1 語意綁定二級/B2 GATE-lite 預註冊 gate_663fecd41783/B3 快路規則化 L6_pytest dormant);P1 modes 10/9/4 建(run-task 帳本/iterate live 驗/panel 零 confirmed 權);P2 D1-D7 接電(4b=17.1 tok/s、8b=6.7 實測;redline 觸線強制人裁;resolve_escalation 人裁佇列)。前台檔位 F1 落地(effort.py+oai_compat+chat_ui 雙選單;frontend_tiers 旗標關=零行為變;418→翻旗標條件=GATE+A5 過+用戶一句)。L2 每日自審(deliberation_daily_topic+run_daily_deliberation)備妥,cron 待 GATE+A5。三服務登入統一 .env AUGUR_ADMIN_*(sync_admin_user.py)。

**Why**:GATE 三判準(+15pp/假確認/McNemar 合併 p)照實裁決,不過=engine 維持 experimental 不挪門柱。

**How to apply**:GATE 報告=benchmark_deliberation --report-gate gate_43044a574c0d;翻旗標=UPDATE deliberation_engine_config frontend_tiers enabled:true(用戶拍板)。CLAUDE v1.24「本地審議引擎為主、Claude 為輔」條款。

**2026-07-11 晚間終態**:GATE 663f 誠實 FAIL(假確認逐輪 ✗)→ 素材修正(core_universe bug)→ 新預註冊 **gate_43044a574c0d PASS**(engine 100% vs 53.3%、假確認 0、McNemar 逐輪全顯著;停電中斷後 run/task resume 完跑=真 kill-resume 實證)。七片複量:D1/D2/D5/D6/D7+模式 4(panel_score 12 首跑)/9/10 全有帳;D3/D4 字面未達實質已證(載體=run/task 非 session,措辭裁定交 hugo)。**A5 報告=reports/augur_deliberation_a5_remeasure_20260711.md**(F2 開閘前置文件;checklist:6 單 red-line 演練人裁待清+翻旗標 UPDATE+L2 cron 一行)。
