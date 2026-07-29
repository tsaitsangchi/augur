# IMPORT-QUAL-GATE S2 CLOSED（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`audits/SIX-TRACK-WAVE-APPROVED-20260729.md`（`IMPORT-QUAL-S2`＋`FZ-keep`）  
> **前提**：S1 CLOSED＝`audits/IMPORT-QUAL-GATE-S1-CLOSED-20260728.md`  
> **不含**：approve／activate 動作、長計畫書、FinMind／FRED、破壞 license／admission gate

## 一、做了什麼

| 項 | 狀態 | 摘要 |
|---|---|---|
| **`/gov` 匯入合格面板** | ✅ | 擴 `serve_admin_console._gov_data`／`gov_dashboard_html`：列 `knowledge_import_job`（近 30）＋檔案級 `knowledge_import_qualification` |
| **可選篩選／重新整理** | ✅ | `?job=N` 篩該 job 之 qualification（上限 200）；無篩選列近 80 筆跨 job；頁首「⟳ 重新整理」 |
| **JSON 同形** | ✅ | `/api/gov`（可選 `?job=`）回同一 `_gov_data` |
| **硬禁** | ✅ | 匯入區塊**無** approve／activate 按鈕／form；不改 admission／license gate |
| **FZ-keep** | ✅ | 零市場 API |

## 二、如何查看

1. 起／重啟 admin：`systemctl --user restart augur-admin`（`127.0.0.1:8500`）
2. 瀏覽器登入後台 → 側欄「🔐 來源治權 · 匯入合格」→ `http://127.0.0.1:8500/gov`
3. 錨點：`#import-qual`；單 job：`/gov?job=<id>`
4. 函式路徑煙測（免 login）：`python` 載入 `scripts/serve_admin_console.py` → `_gov_data()`／`gov_dashboard_html(d)`

## 三、驗證真兆（本輪）

| 檢查 | 結果 |
|---|---|
| 表存在 | `knowledge_import_job`／`knowledge_import_qualification` |
| DB 現況（煙測當下） | jobs≥1、quals≥1（庫內已有 S1 寫入列） |
| `_gov_data()` | `import_table=True`；jobs／quals／by_verdict／by_ingest 有值 |
| `?job=2` | 回傳 qualification 全為 `job_id=2` |
| HTML | 含 `IMPORT-QUAL-S2`；import 區塊無 `<button>`；無 `/api/approve`／`/api/activate` |
| `import_qualification --selftest` | 全通過 |
| admin 無參數矩陣 | 可印；port=8500 |

## 四、變更檔

| 檔 | 角色 |
|---|---|
| `scripts/serve_admin_console.py` | `/gov`＋`/api/gov` 唯讀加匯入帳本；側欄文案 |
| `audits/IMPORT-QUAL-GATE-S2-CLOSED-20260729.md` | 本收官 |
| `audits/SIX-TRACK-WAVE-APPROVED-20260729.md` | §三 IMPORT-QUAL-S2 列 CLOSED |

## 五、誠實註記

- 本輪為最小可用面板，**不做** writer 行為變更、**不做**卡住 `status=running` job 的自動 finalize。
- 升級／活化仍唯人、走既有 TTY CLI；web 零寫升級路徑不變。
