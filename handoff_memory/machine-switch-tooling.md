---
name: machine-switch-tooling
description: 換機工具已改版 — 本機 scripts/ 五件組已被遠端根目錄工具組取代（CLAUDE v1.25 #31），舊版封存於 backup 分支
metadata:
  node_type: memory
  type: project
  originSessionId: c3c40e0c-7154-4936-8937-6d9ce947808c
---

# 換機工具套件（已被取代，2026-07-13 更新）

**現行正典（SSOT＝repo `HANDOFF.md` §2 + `CLAUDE.md` v1.25 #31）**：換機接續用**根目錄工具組**——
`resume_project.sh`（一鍵編排）/ `sync_from_github.sh`（fast-forward-only 源碼同步）/ `sync_memory.py`（memory ⇄ repo `handoff_memory/`）/ `import_database.sh`（DB 匯入自動判格式）/ `read_handoff.py`（讀接續狀態）——皆零 Claude usage。

**史料**：本機 2026-07-09 曾建 `scripts/` 五件組（export_db / import_db / sync_memory / setup_new_machine / archive_snapshot + generate_session_context），另一台機器 07-10 起以根目錄工具組重新實作並入憲 #31，功能性取代。2026-07-13 本機 main 重設對齊 origin/main 時，五件組連同本機審議引擎 W1+W2 舊版（6 個未推 commit）完整封存於本機分支 **`backup/local-wsl2-20260713`**（856ab86；僅本機、未推遠端）。

**Why**：兩機並行各自造輪，遠端版已入憲為正典；舊版不刪、留分支可考。
**How to apply**：換機/接續一律照 HANDOFF §2 與 #31 跑根目錄工具，勿再引用 `scripts/` 五件組路徑；需考古 → `git checkout backup/local-wsl2-20260713`。
