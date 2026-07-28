# Admin 本機匯入進度可見 — 實作留痕

> **日期**：2026-07-28 · **位階**：[I] · **slug**：admin-local-import-progress

## 改動

| 檔 | 內容 |
|---|---|
| `scripts/serve_admin_console.py` | 本機匯入 UI 進度條；API `begin`／`file`／`commit`／`status`；舊 `/api/upload` 保留相容 |
| `src/augur/knowledge/webupload.py` | `new_upload_dir`／`append_upload`／`safe_updir`（分批落暫存） |
| `scripts/acquire_local_files.py` | 逐檔 `[progress] k/N file=… status=…` + `[local_import_done]` |

## 進度呈現

1. **上傳階段**：每批最多 6 檔；UI「上傳中 k／N」＋％進度條＋目前檔名
2. **解析階段**：背景 `acquire_local_files -u`；輪詢 `/api/upload/status` →「解析入庫 k／N」＋成功／略過／失敗計數

## 實測

- `python -m augur.knowledge.webupload --selftest` 全過
- 登入後 begin→2 檔 file→commit→status：`done=true`、入庫 2、無 license 鬆動
- `systemctl --user restart augur-admin` 後生效

## 限制

- job 狀態在 admin 進程記憶體；重啟中途 job 失效
- 瀏覽器 `webkitdirectory` 仍受瀏覽器選夾能力限制（隱藏檔／權限）
- 硬重新整理後才載入新 HTML／JS（服務已重啟）
