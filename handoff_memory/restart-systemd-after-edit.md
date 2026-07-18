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

**換機/unit 遺失一鍵重建（2026-07-13 入 repo）**：unit 檔**不隨 git**——換機後 `~/.config/systemd/user/` 為空、服務全不在線。根治＝**`bash install_services.sh`**（repo 根、零 usage）：生成 5 常駐服務（ollama:11434←advisor:8399←chat:8090·admin:8500·probability:8600）+2 timer（embed-catchup 03:30、l2-deliberation 預設 disabled 待 hugo 開閘 `--with-l2`）+`enable-linger`+enable/restart+端口實測。⚠**2026-07-17 更正:`augur-qdrant.service` 已 active running**(07-14 hugo 拍板上線、`install_services.sh` 已含 qdrant),原「休眠不設 unit」過時;另 `augur-green.service/.timer` **不在** install_services.sh(該 timer 仍會跑)→換機一鍵重建對 green 不成立、須另掛。`--status`/`--uninstall`。啟動規格與 start_chat.sh 對齊（單一 SSOT）。
**2026-07-13 兩陷阱（重建時必避）**：① systemd unit 的 `Environment=` **必在 `[Service]` 段**、放 `[Unit]` 靜默無效（誤放致 ollama 讀錯模型庫）；② **兩個 ollama 模型庫**——`~/ollama/models`（start_chat.sh + systemd `OLLAMA_MODELS` 用）vs 預設 `~/.ollama/models`（裸 `ollama list`/`pull` 無 env 時用）；systemd ollama 須 `Environment=OLLAMA_MODELS=%h/ollama/models` 才讀對庫（否則 advisor qwen3:8b 靠庫2 舊版僥倖能跑、但 L2 的 qwen3:4b 缺）。pull 模型務必確認落在 systemd 用的庫。③ install 用 `enable`+`restart`（非 `enable --now`——後者對已 active 服務不 restart、更新 unit 不生效）。embed-catchup 命令用主語料 `--layer sentence --language zh`；完整多 lang/scope 組合原機 wrapper 未遷移、待補。
