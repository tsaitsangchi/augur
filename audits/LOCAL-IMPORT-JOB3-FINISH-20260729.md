# LOCAL-IMPORT-JOB3-FINISH-20260729

> **日期**：2026-07-29 · **位階**：[I] 操作記錄 · **FZ-keep**：無 FinMind/FRED 操作

## 背景

`knowledge_import_job #3`（`source_key=local_files_smoke_test`，root=`/home/hugo/.augur_uploads/af9db9d2497f24cb`，541 檔）處於 zombie `running` 狀態，489/541 已 qualify，52 檔從未掃描。

## 處置

### 步驟一：終結 Job 3（zombie → completed）

直接 UPDATE `knowledge_import_job` SET status='completed'，寫入實際統計與 zombie 記錄 summary。

**Job 3 最終統計（489/541 scanned）**：

| ingest_status | count |
|---|---|
| inserted | 8 |
| duplicate | 285 |
| short | 54 |
| skipped | 142 |
| **未掃描（zombie）** | **52** |

### 步驟二：重新匯入全目錄（Job 4）

```bash
./venv/bin/python scripts/acquire_local_files.py \
  --dir /home/hugo/.augur_uploads/af9db9d2497f24cb \
  --source-key local_files_smoke_test \
  --license public_domain --access-scope public --domain smoke_test
```

- 自動建立 **job_id=4**
- 耗時約 56 分鐘（16:28 → 17:24）
- Log：`/tmp/augur_logs/local_import_job3_finish.log`
- 結束標記：`[local_import_done]`

**Job 4 統計（541/541 scanned，status=completed）**：

| ingest_status | count |
|---|---|
| inserted | 67 |
| duplicate | 332 |
| short | 57 |
| skipped | 85 |

**skip 細分**：

| reason_code | count |
|---|---|
| skip_no_text | 33 |
| skip_unknown_ext | 26 |
| skip_empty | 13 |
| skip_parse_error | 13 |

### 原 52 未掃描檔的歸宿

Job 4 全量重掃 541 檔。Job 3 的 8 inserted 在 Job 4 呈 duplicate（已存在），Job 4 的 67 inserted 為**淨新增**——涵蓋原 52 未掃描檔中可解析者＋Job 3 曾 skip 但 Job 4 重新判定可入庫者。

### 累計入庫

- Job 3 inserted: 8
- Job 4 inserted: 67（淨新增，不重複 Job 3）
- **合計 unique items: 75**

## 後續

- `build_sentences --scope items` → `embed_knowledge` → advisor 可檢索
- Job 5（4 檔 inserted）為同期另一小批次，非本次範圍

## 合規

- 未觸 FinMind/FRED API（FZ-keep）
- license=public_domain、access_scope=public 維持不變
- 未觸 admit drain、PME
