---
name: augur-path-six-parallel-gap
description: 2026-07-30 親驗:「一條路」在實作層實為六條並行——3 門表同骨架重複+6 裁決表異質(2 空表);統一 path_* 三表設計已入計畫書
metadata: 
  node_type: memory
  type: project
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-30T04:03:29.120Z
---

**實測（2026-07-30 `information_schema` 親查）**：報告書核心宣稱「八行走者走同一條路、無特權通道」，但實作層是**每條線各自實作自己的門與裁決**：

- **三個預註冊門表為同一 13 欄骨架重複三次**，只差作用域欄：`arena_admission_gate`（3 列，scope 欄＝`axis`）／`direction_gate`（29 列，`track`＋`horizon`）／`evolution_prereg_gate`（1 列，`axis`）。共同核心欄＝gate_id・purpose・criteria・criteria_sha・status・preregistered_at・approved_by・approved_at・git_sha・evaluated_at・result_snapshot・evaluation_ref。
- **六個 verdict 表異質，其中兩個從未被寫過**：`deliberation_verdict`(768)・`revalidation_verdict`(2)・`direction_arena_verdict`(**0**)・`direction_econ_verdict`(**0**)・`econ_verdict_rule`(規則非事實)・`knowledge_import_verdict_dict`(詞典非事實)。方向軸判決實際寫在 `direction_gate.status/result_snapshot`，那兩張空表是殘留。
- **`knowhow_auto_admit_gate` 名字撞概念**：欄位是 enabled／require_kh8／require_kh9／channels／max_auto_depth——它是**組態開關表，不是「先凍結判準再看資料」的證據門**。
- **生產認知集無 `prodset*` 表**：真名為 `evolution_production_feature_set`（查 `prodset%` 回 0 筆）。

**Why**：後果有四——新增第九種行走者＝再抄一份 13 欄表＋一支評估器（成本線性）；「這個世界目前對什麼有把握」沒有單一可查處（要 union 六表還得知道哪兩張是空的）；判死留檔散在 status 欄與 JSONB、跨線不可比；「回流」無共同落點。

**How to apply**：設計已寫入 `reports/augur_future_development_plan_20260730.md` §四／§五——**新增 `path_gate`／`path_candidate`／`path_verdict` 三表＋`src/augur/path/` 五模組（registry・candidate・verdict・adapters・status）**，紀律是**只增不改既有**（既有門與裁決之列為已定案證據，改之違不朽律）：以 adapter 把既有六條登錄上來（帶 `adapter_source`／`adapter_key`）、新事實走唯一寫入器、P3 雙寫觀察一週才議單寫。兩個關鍵 DB 級不變式：`path_gate_eval_needs_approval_ck`（**未經人簽之門不得評估**）與 `path_no_ai_human_sig`（`decided_by='human:*'` 須人類會話通行證，把 [[never-type-human-signature]] 從紀律升格為機械閘）。相關：[[augur-world-construction-core]]。
