---
name: augur-deliberation-engine
description: 本地審議引擎 P0-P2 補完(3 blocker 封/modes 10-9-4/D1-D7 量測);前台檔位 F1(旗標關);GATE 預註冊跑中;L2 每日自審備妥待 GATE+A5
metadata:
  type: project
---

本地 ultracode 引擎 2026-07-11 態:P0 三 blocker 封(B1 語意綁定二級/B2 GATE-lite 預註冊 gate_663fecd41783/B3 快路規則化 L6_pytest dormant);P1 modes 10/9/4 建(run-task 帳本/iterate live 驗/panel 零 confirmed 權);P2 D1-D7 接電(4b=17.1 tok/s、8b=6.7 實測;redline 觸線強制人裁;resolve_escalation 人裁佇列)。前台檔位 F1 落地(effort.py+oai_compat+chat_ui 雙選單;frontend_tiers 旗標關=零行為變;418→翻旗標條件=GATE+A5 過+用戶一句)。L2 每日自審(deliberation_daily_topic+run_daily_deliberation)備妥,cron 待 GATE+A5。三服務登入統一 .env AUGUR_ADMIN_*(sync_admin_user.py)。

**Why**:GATE 三判準(+15pp/假確認/McNemar 合併 p)照實裁決,不過=engine 維持 experimental 不挪門柱。

**How to apply**:GATE 報告=benchmark_deliberation --report-gate gate_663fecd41783;A5 復審材料=P0-P2+P3 驗收 SQL;翻旗標=UPDATE deliberation_engine_config frontend_tiers enabled:true(用戶拍板)。CLAUDE v1.24 新增「本地審議引擎為主、Claude 為輔」條款。
