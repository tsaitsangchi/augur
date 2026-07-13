---
name: git-fetch-before-treaty-commit
description: 改治權檔/重要 commit 前先 git fetch 確認 remote 最新，避免跨機並行演進分叉
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c3c40e0c-7154-4936-8937-6d9ce947808c
---

改治權檔或做重要 commit 前，**先 `git fetch origin` 確認 `origin/main` 是否領先本地**；若領先，先 pull/rebase 到最新再改。

**Why**：augur 多機器並行開發（Mac + WSL2）、DB 跨機獨立但 git 共用 remote。2026-06-24 本地基於舊 commit e54574a 做「資料完整性判準入憲」（升 v1.6.1/v1.8.1），未先 fetch；而另一機器（Mac）已於 2026-06-23 push 治權升版（OUT_OF_UNIT → 原則精華 v1.7.0/憲章 v1.9.0）。結果：push 被拒（remote 領先 4 commit）、治權檔檔名 rename 衝突（同檔被 rename 成不同名）、需 `reset --hard` 撤分叉 → pull → 重 apply 判準至最新治權檔 → 重升版 v1.7.1/v1.9.1 → 重建 tag。一次可避免的返工。

**How to apply**：(1) 動 `docs/原則精華_*` / `docs/系統架構大憲章_*` / CLAUDE / README 等治權檔前，或任何要 push 的 commit 前 → 先 `git fetch origin && git log --oneline main..origin/main`（看 remote 領先什麼）。(2) remote 領先 → 先 `git pull --ff-only` 拉到最新，基於最新版改、升版號接續（非基於舊版分叉）。(3) 治權檔升版時版本號要疊在 remote 最新之上（remote v1.7.0 → 本地新判準應升 v1.7.1，非 v1.6.1）。關聯 [[bounded-autonomy-mode]] 碰護欄（push/治權）停手、[[rigor-completeness-discipline]] 實證不憑「我以為 remote 沒變」。
