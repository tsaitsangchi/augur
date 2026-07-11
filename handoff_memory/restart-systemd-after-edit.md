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

**停電/重開機後災後檢查（2026-07-11 實證）**：全部 6 服務+2 timer 掛 `systemctl --user`（unit 檔在 `~/.config/systemd/user/`）。檢查序：`pg_isready` → `systemctl --user list-units 'augur-*' --all` → 死掉的 start → 逐端口 curl 實測（chat:8090/advisor:8399〔`/` 404 正常、打 `/v1/models`〕/admin:8500/probability:8600/ollama:11434/qdrant:6333）→ DB 查殘留鎖（CLAUDE #30）。曾有 boot 排序循環（augur-ollama 誤寫 `After=default.target` 與 `WantedBy=default.target` 成環 → advisor/chat/admin 開機被 systemd 丟棄），2026-07-11 已刪該行修復；若重開機後三服務又死，先 `journalctl --user | grep -i cycle`。
