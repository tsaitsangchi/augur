---
name: background-tasks-visible
description: 用戶要求：每個背景作業都須用 TaskCreate 登記進可見任務清單並更新狀態，不得只用背景 shell 靜默跑
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 778040ca-21b5-4b60-ad2d-0fad302930ca
---

用戶 directive 2026-07-13：背景 shell（Bash run_in_background）對用戶介面不可見，用戶看不到「有東西在跑」。

**Why**：用戶要隨時看得到每一個進行中的背景作業；只靠 harness 完成通知＝過程黑箱（也呼應 CLAUDE #21 長跑不靜默）。

**How to apply**：凡啟動背景作業（DB 匯入/長跑 sync/build/watchdog…）：
1. 啟動同時 `TaskCreate`（subject＝作業名、description 含背景 shell ID＋log 路徑、activeForm＝進行中描述）並立即 `TaskUpdate` 設 in_progress；
2. 有階段性進展可更新 description；完成/失敗即改 completed（失敗則保持 in_progress 並開新 task 描述阻塞）；
3. 一個背景作業一個 task，不合併。

**⚠ 啟動方式陷阱（2026-07-13 實證失誤）**：長跑進程**一律用 Bash `run_in_background: true`**，**不要用 `nohup … & disown` 包在同步 Bash 呼叫裡**。差別：
- `run_in_background: true`→ harness 追蹤該背景 shell、顯示在用戶「背景任務」監看區、**完成時自動 <task-notification> 通知**我；
- `nohup … & disown`→ 同步 Bash 呼叫立即返回、harness 以為已完成、**脫離追蹤**：用戶背景區看不到、我也不會被自動通知完成 → 只能手動輪詢（違 #28 且用戶「看不到」）。
兩者都要配 TaskCreate；但唯有 `run_in_background: true` 能讓 harness 背景區真正可見+自動通知。若進程已用 nohup 啟動且不宜重啟，用 `Monitor` 工具設 until 條件（等 pgrep 消失）等完成，補回「完成即報」。
