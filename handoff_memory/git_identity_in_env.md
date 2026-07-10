---
name: git-identity-in-env
description: "git 身分(user.name/email)與授權的 git config 指令放在專案 .env;commit 前先查那裡,不要問用戶、也不要自行臆測設定"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7fcd646b-99c3-43c3-a5cc-d9b4810f3887
---

git 提交身分(`user.name` / `user.email`)以**明確的 `git config --global` 指令**形式存放在專案根目錄的 `.env` 檔。

**Why:** CLAUDE.md #14 + git 安全協議要求「NEVER update the git config」——不可自行臆測或設定身分。但用戶把要執行的 `git config --global user.email/user.name` 指令**明寫在 .env**,即為對「這些特定值」的預先授權。值本身(email/name)在每個 commit 都公開,非機密;但 .env 同檔含真正機密(FINMIND_TOKEN / FRED_API_KEY / DB_PASSWORD / GITHUB_TOKEN / GEMINI_API_KEY...)——**只取身分、絕不外洩或 commit 其餘 keys**。

**How to apply:** 提交時若遇 "Author identity unknown",先 `grep` .env 找 `git config --global` 兩行並照跑,**不問用戶**;但仍**不主動 `git push`**(需另外明確授權)。實證 2026-06-21:首次 commit 因身分未設失敗 → 我停下沒自設 → 用戶說「設定在.env檔案內,你查一下」→ 查到明寫指令照跑成功。
