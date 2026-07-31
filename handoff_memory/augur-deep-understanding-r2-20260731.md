---
name: augur-deep-understanding-r2-20260731
description: 07-31 午第二輪深化理解（獨立核驗＋重開機後重測）：基線報告 commit 前已過期之元教訓、sim 專章生效鏈、KH0 真破口 48.68%、靈魂 v1.10.0 最終目標、人閘偵測級實證邊界
metadata: 
  node_type: memory
  type: project
  originSessionId: b877d307-e736-407a-aa6a-200f3758f684
  modified: 2026-07-31T03:46:33.761Z
---

**指針**：全文＝repo `reports/augur_deep_understanding_r2_20260731.md`（12 路 workflow `wf_cdbaf172-737` 唯讀探查＋繕打者親讀治權檔合成；對今晨基線 `augur_deep_understanding_20260731.md` 42 債逐項核驗）。本檔只存記憶級結論。

**元教訓（最值錢）**：**基線報告在 commit 前就已過期**——債 #15（12 死鏈）在報告落檔前 83 分鐘已被 `ceac40c` 修綠、債 #31 在 28 分鐘前已被 `847f65a` 修、B1 根因在產製前 1 小時已被 `f143aa6` 修；A10/B4「池子在掉＝有人在推進」係 **log 行 vs live SQL 時序錯配、方向整個抓反**（池子實為上升，08:06 harvest 進料 14,361）。⇒ 07-31 上午治權與現實以分鐘互相超車；**可信的不是報告數字，是附的驗證指令**（承 [[cross-claim-contradiction-check]]）。

**07-31 治權三件大事**（基線零覆蓋）：
1. **靈魂 v1.10.0 新增「最終目標」章（hugo 拍板入憲）**：「讓本地 AI 具備與人一樣的判斷力」——能力≠權威（P5.W2/W5 不可豁免）、「量不出差別≠沒有差別」明文禁止、六項可判定判準（分域／同題盲測／過地板／含不知道題／≥2 輪複現／後果回流）、本地化為要件。**後續優化對準此終點**。
2. **sim 專章 v1.0 生效**（gp_86c8063fc688、hugo TTY 親簽 10:25、唯一經新閘的治權簽名）＋憲章 v1.54.0 登錄；八表落地**全 0 列**；`evolution_axis` registry 5 軸（含 sim）、兩表 CHECK→FK。⚠**候選物理死鎖**：`simulation_method_registry` 0 列而候選表 FK 指向它＝候選寫不進去；20 個既有 method 註冊各需人簽＋gate_ref（治權提案），路徑未定；kill_switch 無 sim scope（KILL_SCOPES 寫死四值＋自測鎖封閉集）。**P3 未起、prereg 無 sim 列＝節點二未成立**。
3. **憲章 v1.53.0 入口底線**：入 staging 不得因欄位缺漏判死；KH0 分母改**全部** knowledge_item——**真普遍破口 138,829/285,177＝48.68%**（v1.52.0「破口 0」係窄口徑假綠、已明文撤回）；46,775 筆 rejected 溯及回收（staging_rejection_recovery）。此為現行 [N] 義務、量級最大的地基工程。

**人閘現況（偵測級實證邊界）**：governance_queue TTY 閘是真閘（--approve 無 TTY rc=1、先於 DB），但三條殘道全開——pty 十行可產 'hugo' 簽名（唯讀探針實證）、TTY 內按 Enter 回退 `getpass.getuser()`（docstring 與專章「親手打簽名」宣稱**強於 code**）、DB 層 UPDATE 完全繞過 CLI。**INSERT 路徑零人簽**（local_model_version 可直接 INSERT serving）。direction_gate 18 列裸 hugo vs 8 列「claude 繕打」註記＝機械不可區分。專章 §4.4 已明文承認偵測級——**其他通道宜向此對齊（誠實降級或真上機械），勿再讓外觀強於實質**（承 [[never-type-human-signature]]）。

**其餘記憶級更新**：
- `honesty_delete_only_guard` 已 **23 表 46 trigger、UPDATE 仍 100% 全裸**（sim 八表複製同病）；`evolution_run` 堆 6 列 running 殭屍（timeout/SIGTERM 不回填）。
- KH8 降級**不可持久**：upsert 用 GREATEST，bulk 降 admit_depth 會被下次 auto_admit 自動還原——降級必須同時動 layer_scores 或 GREATEST 邏輯。
- fulltext 出料端**根本沒排程**（ATA 只跑 sentences+embed；fetch 無任何 cron/timer）——修 timer 不會抓全文，要加排程。
- `lending_fee_rate_mean_20d`（active 特徵）**全 repo 零產生器**＝clean-room 不可重建破口（候選側 lending_fee_vw_mean_20d 同病、列數同 17,072）。
- Qdrant ANN 漏 eligible 過濾是 **live**（sentence_items 後端＝qdrant_server）；retrieval :408 死碼、**:373 非死碼**（基線半錯）。
- V2-SUNSET 0/3（92 天）；(c) 的正確判準表＝`local_model_eval_run`（非 local_ai_iteration_ledger）；sim 軸不在三軸內、不構成續命路徑反分食 slot。
- A3 三鏡頭門已 superseded 且「2026-08 deadline」查無出處（[[augur-construction-v4]] 該句勿再引）。
- src/augur ＝ **16 package**（索引「18」為誤）；scripts 301 支；public 306 base 表（11:26 快照、日內 +10）。
- 重開機（11:09）翻頁但未修根因：孤兒佔埠消失（再手動 `./venv` 起即複發）、ata-advance 連三日 failed 的 systemd 證據被抹除（只剩 log/ledger）。
