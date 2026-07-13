---
name: memory-export-secret-scan
description: sync_memory export 全量推活 memory 到 public repo — commit/push 前必掃密碼，記憶不得存明碼憑證
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 778040ca-21b5-4b60-ad2d-0fad302930ca
---

`sync_memory.py export` 把**全部活 memory 檔**推到 repo `handoff_memory/`，而 **repo 是 public**（HANDOFF 明載）。2026-07-13 實證：export 夾帶 `ttai-integration-and-platform.md` 內的明碼服務密碼（admin 登入密碼），差點 push 到 GitHub。

**Why**：記憶是給 AI 的工作參考，會被無差別同步到公開 repo；任何寫進活 memory 的明碼憑證都會外洩。幸好該次 push 前逐檔掃到、amend 移除，密碼從未上 GitHub。

**How to apply**：
1. **記憶絕不存明碼憑證**——密碼/token/secret 一律寫「⟨見 .env XXX⟩」引用，不寫實際值（已修 ttai 檔兩處 → `AUGUR_ADMIN_PASSWORD`）。
2. **export→commit→push 前必掃密碼**：`git diff --cached` 的 handoff_memory 逐檔掃 `password|token|secret|登入:.*/ \`...\``；抓到明碼即從 commit 移除或改引用，再 push。
3. `.env` 已 gitignore（守）；但 memory 是另一條可能繞過的洩漏路徑，須獨立防。

相關：[[git_identity_in_env]]（.env 是憑證 SSOT）、[[cross-machine-handoff]]（memory 隨 repo 遷移機制）。
