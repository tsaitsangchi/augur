# KH-NAV-DECOUPLE-A-ADOPTED · 2026-08-12

date: 2026-08-12  
kind: nav_adopted  
phase: **A**（導航解耦 only）  
status: ADOPTED  
ladder: A → B → C（每階收口再開下一階）

## 決策（Steward）
KH 閉環自我進化**不候**市場 tip／`PriceAdj`／日曆日更；與市場 **雙主軸並立**。  
市場軌仍 FZ-keep（B3＠D）。共 LLM／重 CPU 時收盤窗讓 B3。

## 本階範圍（A）
- 改導航文件 only；**不開碼／timer**
- 觸發改 ingest-driven＝**B**（未開）
- 碼／timer＝**C**（須 B 收口＋明示 GO）

## 落地檔
- `reports/augur_opt_stepwise_best_next_plan_r14_20260811.md`（#29、雙主軸、WP-K）
- `reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md`（§1.1 階梯、§4）

## 驗收
- [x] 選刀敘事：KH 不因 tip WAIT 停刀  
- [x] 市場 #1 仍候 PriceAdj≥08-12  
- [x] 明文禁：未開 B／C 上 cron／timer  
- [x] 下一可開：**B** ingest-driven 觸發計畫（另回合）

## paste
```text
KH-NAV-DECOUPLE-A-ADOPTED | dual-axis | KH≠tip-calendar
| next=B-ingest-plan | no-C-without-GO | yield-lock-to-B3
```
