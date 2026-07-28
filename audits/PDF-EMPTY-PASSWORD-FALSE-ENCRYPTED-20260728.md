# PDF `encrypted` 誤判補正（空密碼 owner 限制）

> **日期**：2026-07-28 · **位階**：[I] · **觸發**：admin 本機匯入 9 PDF → `encrypted=9`、入庫 0

## 根因（實證）

| 判準 | 結果 |
|---|---|
| 副檔名／magic | 9／9 真 PDF（BCL easyPDF 6.03） |
| `/Encrypt` 標記 | 皆有 |
| 真需密碼？ | **否**——`pypdf.PdfReader.decrypt("")` 回 `1`（USER），可抽正文（約 2k–9k 字／檔） |
| 舊碼行為 | `_read_pdf` 見 `is_encrypted` 即 `return None, "encrypted"` → **誤判** |

上傳暫存：`~/.augur_uploads/dece4a78f2dd5a24/管理辦法/*.pdf`（job `0abf42c494aa2d7e`）。

## 改動

| 檔 | 內容 |
|---|---|
| `src/augur/knowledge/fileparse.py` | 加密旗標先試空密碼；失敗才 `encrypted`；`SKIP_LABEL_ZH`（含「加密 PDF，需密碼／請先解密」） |
| `scripts/acquire_local_files.py` | 誠實跳過分類附中文標籤 |

**未改**：license DB CHECK／admission／FinMind・FRED。

## 驗收

- `python -m augur.knowledge.fileparse --selftest`：全過（含 owner 限制≠encrypted、真 user 密碼→encrypted）
- dry-run 同 9 檔：`ok×9`
- live ingest：`入庫 7(seg 8)、重複跳 2`（內容相同複本 sha1 冪等）
- `systemctl --user restart augur-admin`：:8500 回 200

## 用戶下一步

- 之後同類「有 Encrypt、無開啟密碼」的 PDF 會自動抽文入庫。
- **真需密碼**的 PDF 仍會誠實 skip；請先本機解密或另案做「使用者提供密碼」UI。
- 公司內部辦法若非公版，匯入時宜選 `owned_local` + `local_private`（本次複測沿用原 job 的 `public_domain`／`public`，未改 license 閘）。
