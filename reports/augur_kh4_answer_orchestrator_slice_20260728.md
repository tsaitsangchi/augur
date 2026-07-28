# KH4 最小 Answer Orchestrator Slice（2026-07-28）

**性質**：[I] 實作報告／接續說明  
**對應拍板**：`KH4-PLAN + KH4-ANSWER-ORCH + KH4-INGEST-ALL + FZ-keep + NHC-keep`  
**正交**：依附 `KH-XDOM` / `KH-ATA-SCHED` / `IMPORT-QUAL-GATE` / `RKI` / `KNI`；本檔只記本輪最小可落地 slice

## 一句話

本輪把 KH4 落成一個最小閉環：**有狀態表、有刷新器、有 local/topic/SFTP 寫入點、也有 retrieval 端的最小 answer gate**；但 KH-axis / interaction projection 仍先用保守機械衍生，不宣稱完成全量語意編排。

## 本輪交付

### 新表

- `knowledge_kh4_state`
  - `qualification_state`
  - `kh_axis_state`
  - `interaction_state`
  - `answer_state`
  - `answer_status`
  - `status_reason`
  - `evidence`

### 新模組 / 腳本

- `src/augur/knowledge/kh4.py`
- `scripts/migrate_kh4_state_ddl.py`
- `scripts/refresh_kh4_state.py`

### 接入路徑

- `local upload`：`scripts/acquire_local_files.py`
- `SFTP`：經 `scripts/acquire_remote_files.py` 復用 `ingest_file`
- `topic harvest`：`scripts/promote_knowledge.py` + `scripts/refresh_knowledge_pipeline.py`
- `ATA`：`scripts/advance_knowledge_terminal.py`

## 最小狀態語意

### 1. qualification

- `passed`：已有 item/text 或 promoted 證據
- `blocked`：qualification reject/error，或已進 `knowledge_fulltext_status`
- `pending`：其餘

### 2. KH-axis expansion

- `ready`：source active 且 item 已有 domain/source 歸屬
- `blocked`：source 非 active / 缺治理前提
- `pending`：其餘

### 3. interaction projection

- `ready`：已有 sentence embedding
- `blocked`：terminal blocked
- `pending`：有 text/sentence 但尚未到 embed

### 4. answer eligibility

- `eligible`：語意層准入型別 + license 白名單 + 已 embedded
- `blocked`：任一前層 blocked
- `ineligible`：非語意層准入型別
- `provisional`：其餘未達最低層材料

## 最小 answer gate

`src/augur/philosophy/retrieval.py` 的 items 側檢索現在要求：

- `knowledge_kh4_state` 存在
- `knowledge_kh4_state.answer_status = 'eligible'`

效果：`provisional` / `blocked` / `ineligible` 的 items 不會直接進一般回答材料池。

## 誠實邊界

1. 這不是最終 KH4 全量 orchestrator，只是最小 slice。
2. 非 item 級材料（如 local dry-run / reject 檔）目前仍以 `knowledge_import_qualification` 為主。
3. 本輪未碰 `approve/activate`，也未放寬任何人裁邊界。
4. 本輪零 FinMind/FRED，且無 hardcode 專題答案樹。
