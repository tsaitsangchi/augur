---
name: jian-a-admission-hardening
description: 件A admission code 對抗審查後 R1-R6 硬化+新健檢工具;live-vs-repo drift 教訓(chk 存 live 但曾無 migration)
metadata: 
  node_type: memory
  type: project
  originSessionId: 778040ca-21b5-4b60-ad2d-0fad302930ca
---

件 A 三通道公民化 code 經 15-agent 對抗審查(2026-07-14)+ by-oracle 裁決後之硬化狀態。

**新工具** `scripts/verify_knowledge_admission_health.py`(#29 日常哨兵,零 token):唯讀驗
① SCHEMA(必要 CHECK 在位:chk_itext_owned_local_private / source_type 黑名單 / access_scope 值域 / license 白名單)
② 資料(零 ai_generated、零 owned_local 非 local_private、全文 license 全白名單、provenance)。exit 1=命門/隔離破口。

**R1-R6 硬化**(commit 見 git log 2026-07-14 第二封存點):R1 `chk_itext_owned_local_private` codify 進
migrate_text_understanding_ddl.py CONSTRAINTS(冪等)· R4 admission_gate source_type=None 改 fail-closed ·
R5 acquire_local/remote_files 無參數 graceful(矩陣印出移出 db.connect)· R6 sftpsync/sftpbrowse walk 加深度上限 ·
R2/R3 pending item_source_gate trigger 改 BEFORE INSERT OR UPDATE + active 判準加 adapter 鍵(防 NULL-protocol SFTP 漏閘)。
附帶修既存 bug:原 TRIGGER_FN RAISE 用 %% 致佔位符/arg 數不符。⚠**2026-07-17 live 實查:函式 `trg_item_source_gate()` 確在 pg_proc(修正後單%版)、但 trigger 不在 pg_trigger(=半套)**;此組合(函式在+trigger 不在)無法由 migration 任一次執行產生(函式+CREATE TRIGGER 同一 transaction)→有一條不在 repo 裡的執行路徑碰過 live DB(成因未驗證)。現況零實害(admission.py 只有 Python belt、物理牆未掛),見 [[augur-mechanical-gate-gaps]]。

**Why**:admission 是知識庫准入安全邊界(命門 #1 鄰接、處理不可信 SFTP/apk 輸入),DDL/活化待 hugo=上線前抓漏窗。

**How to apply**:
- **live-vs-repo drift 教訓(最重要)**:對抗審查中「只 grep repo」的 skeptic 對 chk_itext_owned_local_private
  假 CONFIRMED「不存在」,而「查 live DB pg_constraint」的 skeptic 正確 REFUTED——**驗 DB 層宣稱一律查 live DB、
  非只 grep repo migration**;該 CHECK 存 live 但曾無 repo migration 重建=換機/重建 schema 漏命門牆(R1 已補)。
- 治權機械驗雙軌:deliberate.py 對治權檔宣稱走 doctrine_file redline→強制人裁(引擎不機裁治權判準);
  確定性事實(隔離/檔字串/CHECK 存在)用 verify_knowledge_admission_health.py 或 deterministic battery。
- 見 [[augur-knowledge-philosophy]](admission 四件 fail-closed)、[[background-tasks-visible]]、[[augur-project-map]]。
