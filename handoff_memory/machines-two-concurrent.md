---
name: machines-two-concurrent
description: 用戶 directive 2026-07-27——augur 專案現在是「兩台電腦同時進行」，非過去的單機接力換機
metadata: 
  node_type: memory
  type: project
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-27T03:39:45.950Z
---

**2026-07-27 用戶 directive：「目前此專案的進行是這二台電腦同時進行」**——augur 已從過去的「換機接力」（[[cross-machine-handoff]] 的 07-06 單機交棒框架）轉為**兩台機器並行推進**。

**兩台＝**本機 **`PC002-S1800`**（Intel i5-10500／WSL 12GB／**無獨顯**／資料層＋全棧 UI，見 [[machine-pc002-s1800-hardware]]）＋ **`DESKTOP-8MQPFS8`**（Ryzen 5 3600＋GTX 1650 4GB／WSL 25.4GiB）——2026-07-25/26 的 20 個 commit（極限調優、演化鏈、arena 結算）皆出自 DESKTOP。機器文件 SSOT＝`ops/machines/<hostname>.md`。

**只有這兩台——`aitopatom-b96e`（GB10）不存在**（hugo 2026-07-27 再次確認，同 2026-07-25 宣告 [[gb10-unavailable]]）。repo 內大量提及 GB10 的文件、機器包 `ops/machines/packs/aitopatom-b96e/`、以及 `tools/local_llm_mcp/tools.py` 的 `aitopatom-b96e` hostname 分支**全是史料／死碼，勿當現況引用**，任何「丟給 GB10 跑大模型／訓練」的規畫路徑一律失效——算力上限就是這兩台。

**Why**：並行 ≠ 接力。接力假設「另一台是靜止的交接來源」；並行下另一台隨時在推 commit、在改治權檔。

**How to apply**：
- **動手前先 `git fetch`**（承 [[git-fetch-before-treaty-commit]]）——尤其改治權檔／commit 前；本機一次落後 20 commit 就是實例。
- **只做 fast-forward**（`sync_from_github.sh` 分岔即停手），分岔一律停下問，不自行 merge/rebase/reset。
- **DB 各機獨立、不隨 git**（[[db-cross-machine-independent]]）——本機 DB 狀態一律實查，勿照抄另一台的報告數字；跨機同步 DB 只能靠 dump 實體搬檔。
- **調優／硬體參數不可跨機照抄**（兩台 RAM 差一倍、一台有 GPU 一台沒有）。
- 本機 stash 裡若有未上游的本機成果（如 `stash@{1}` panel 優化），並行下更容易被遠端覆寫，須主動確認去留。
- **擂台／進化歸屬已拍板（2026-07-27 乙案）**：**PC002-S1800（本機）＝進化三軸＋arena 之正典帳本機**；DESKTOP＝**只在週六日開機**的 GPU 實驗機（此即決定性理由：週間 22:30 cron 它不在線）。本機 arena cron 保留＝正典擂台鐘；**週末待辦**（DESKTOP 下次開機）：停它的 arena/evolution cron＋timer、以私有通道（不入 git）搬 07-26 增量（gold sample_id≥281 之 824 列、RAWEVO ledger 3 輪、hints 含 H3 approved、coverage snapshot、LLM 臂 eval runs）至本機；此後 DESKTOP 只消費本機 dump。登錄＝`audits/V2-PHASE4-RUBRIC-H2-APPROVED-20260727.md` §六。相關：本機 kill_switch 缺 `scope` 欄（repo 級缺口、無 migration 承載，見 [[augur-self-evolution-plan-map]] 07-27 增補）。
