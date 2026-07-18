---
name: db-cross-machine-independent
description: augur DB 不隨 git、每台機器各自獨立；判斷 DB 狀態一律實查、勿照抄 handoff
metadata: 
  node_type: memory
  type: project
  originSessionId: 535524f8-f10a-43be-8ee8-7e88ab8d3ccf
---

augur 的 PostgreSQL 資料**不隨 git**——git 只帶 code/reports/charter/CLAUDE + `.env` 範本；真正的 `.env`（含 token）與 DB 資料都在各機本地、不進 git。因此**每台機器的 augur DB 各自獨立、內容不同**：

- **本機 WSL2**（DB query 實查 **2026-06-18**）：**28 表 / 估 ~1.137 億列**（reltuples 估值；最大表 InstitutionalInvestorsBuySell 23.9M、GovBank 12.6M、Price 10.5M、PriceAdj 10.3M…；已涵蓋價量/籌碼/財報/衍生/國際/總經）。catalog 兩表已建（dataset_catalog 95、column_catalog 751、中文 100% 覆蓋）。〔更早 2026-06-11 曾 24 表 1.09 億；用戶常 drop 重測，數字僅快照。〕⚠**2026-07-17 實查（本則自己的「一律實查」精神）:public 246 純表、dataset_catalog 97、column_catalog 769**——印證「數字僅快照、勿照抄」。
- **原機 Mac `caizongyede-MacBook-Pro`**（handoff 20260611 記載）：另一套 13 表 ~78M 列，sync 背景跑中（8/82）。表組成兩機不同。

**Why**：跨機接力 handoff 會寫「換機後新電腦 Postgres 是空的」——那是對「全新機器」的假設，對已用過的機器不成立。本機實查發現 24 表上億列，與 handoff 假設相反；若照抄就等於寫了假資料（違 #15 誠實 / #1 零幻像）。

**How to apply**：要判斷 DB 狀態（表數/列數/某表有無資料/sync 進度）一律**實查**——`PYTHONPATH=src venv/bin/python` 經 `augur.core.db.connect()`（context manager）查 `pg_stat_user_tables`；**勿照抄 handoff 或 [[augur_project_overview]] 的快照數字**（會過時，用戶也常 drop 全表重測）。
