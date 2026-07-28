# IMPORT-QUAL-GATE S1 CLOSED（2026-07-28）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`audits/IMPORT-QUAL-GATE-PLAN-APPROVED-20260728.md`  
> **不含**：S2 `/gov` 完整面板、approve／activate 動作、任何市場 API

## 一、做了什麼

| 階段 | 狀態 | 摘要 |
|---|---|---|
| **拍板登錄** | ✅ | `IMPORT-QUAL-GATE-PLAN-APPROVED-20260728.md` |
| **S1 DDL** | ✅ | `knowledge_import_job` / `knowledge_import_qualification` + verdict/reason 字典 SSOT |
| **S1 writer** | ✅ | `scripts/acquire_local_files.py` 接入 shared writer；admin 原生上傳/資料夾入口同路徑受益 |
| **S1 reader/check** | ✅ | `scripts/migrate_import_qualification_ddl.py --check` 可檢表與字典；SQL focused 查表驗證 |
| **語意保護** | ✅ | 未改 admission gate、未改 license gate、未改 progress log sentinel、未碰 approve/activate |

## 二、新表

| 表 | 作用 |
|---|---|
| `knowledge_import_job` | 一次本機匯入的 job 帳本：來源、scope、dry-run、統計、summary |
| `knowledge_import_qualification` | 檔案級 qualification：初值、preflight、ingest_status、reason_code、item_id |
| `knowledge_import_verdict_dict` | verdict 字典 SSOT |
| `knowledge_import_reason_code_dict` | reason code 字典 SSOT |

## 三、已接上的 writer 路徑

- `scripts/acquire_local_files.py`
  - 開 job 時先寫 `knowledge_import_job`
  - 每檔先寫 `knowledge_import_qualification` 初值 `queued`
  - 跑 `preflight` 後回填 `verdict` / `reason_code` / `preflight`
  - dry-run 寫 `ingest_status='dry_run'`
  - 真實匯入寫 `inserted` / `duplicate` / `short` / `skipped`
- `scripts/serve_admin_console.py` 無須改碼：既有資料夾匯入與原生上傳都呼叫 `acquire_local_files.py`，因此 S1 已自動接上 UI 主路徑

## 四、驗證結果

### DDL

```text
tables=['knowledge_import_job', 'knowledge_import_qualification',
'knowledge_import_reason_code_dict', 'knowledge_import_verdict_dict']
verdict_dict=4
reason_dict=17
```

### focused 最小匯入

1. `--dry-run` 跑 1 檔 `sample.txt`：CLI 正常印 `[local_import_done]`
2. 真實最小匯入同檔：CLI 正常入庫 1 segment
3. DB 查表：

```text
jobs= [(2, 'completed', False, 1, 1, 1, 0, 0, 0, {'source_type': 'local_upload'}),
       (1, 'completed', True, 1, 1, 1, 0, 0, 0, {'source_type': 'local_upload'})]
quals=[(2, 2, 'pass', 'write_ok', 'inserted', 'sample.txt'),
       (1, 1, 'pass', 'preflight_ok', 'dry_run', 'sample.txt')]
```

結論：**dry-run 與真實最小匯入都會落 qualification，無 silent drop。**

## 五、誠實註記

- 用戶所指 `reports/augur_import_admission_quality_gate_plan_20260728.md` 未在本工作樹出現；因此本輪未更新其拍板欄，只補 audit 與 HANDOFF 最小留痕。
- 本輪未封存：工作樹有未提交變更，且用戶未明示 commit / archive。
