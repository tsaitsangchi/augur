---
name: restart-systemd-after-edit
description: "改 augur 常駐服務(systemd chat/advisor/admin)腳本後須重啟該服務再實測,否則跑舊碼"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9009c955-58bc-46c5-904b-ed515e2be723
---

改動 augur 常駐服務(`systemctl --user`：`augur-chat` :8090 / `augur-advisor` :8399 / `augur-admin` :8500 / `augur-ollama`)所屬的 `scripts/serve_*.py`（或其 import 的 `src/augur/**`）後，**必須 `systemctl --user restart <service>` 重啟該服務、再對重啟後的服務實測**。

**Why:** Python `http.server` 等在**啟動時載入腳本、不熱更新**；只改檔+commit 而不重啟，運行中的服務仍跑舊記憶體版 → live 實測跑舊碼＝假通過。2026-07-05 實證：`oai_compat._reply_text` 移除「引經據典」區塊已 commit（v1.30.0），但只重啟了 chat/admin、**漏重啟 advisor**，用戶 live 仍看到引經據典（`_reply_text` 跑在 advisor :8399）。

**How to apply:** 判斷改的檔屬哪個服務（`_reply_text`/oai_compat/retrieval/advise/guard → advisor；serve_chat_ui/前台 PAGE → chat；serve_admin_console → admin），改完 commit 後**重啟對應服務**（治權/顯示/邏輯層改動尤其）；跨服務改動一併重啟。已入 CLAUDE #7（v1.18）。相關：[[augur-project-map]]。
