---
name: git-add-scoped-only
description: 禁 git add -A/目錄級 add——並行 session 未提交工作會被掃進自己的 commit(2026-07-28 實犯)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-28T06:00:51.888Z
---

2026-07-28 實犯:封存時 `git add -A reports/ scripts/` 把並行 Cursor session(PME-XDOM 線)兩個**未提交中的檔**掃進我的 commit `a214ce0` 推上 main——內容無損但推早了對方半成品、commit 歸屬錯誤;已推不 amend 不 force,向 hugo 自陳。

**Why**:兩台/多 session 並行是本專案常態([[machines-two-concurrent]]、[[no-concurrent-agents-same-files]]),working tree 是共享的——目錄級 add=把別人手上的畫一起裱框。

**How to apply**:commit 一律**逐檔明列** `git add <file1> <file2>`(只加自己本步編輯過的檔);commit 前看 `git status --short` 有無非本步之 M 檔;`--allow-empty` 純標記 commit 時**零 add**。
