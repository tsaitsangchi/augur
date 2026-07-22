# 設定包：`DESKTOP-8MQPFS8`（精簡 stub）

* **主機**：僅適用 **`DESKTOP-8MQPFS8`**（WSL2 · x86_64 · GTX 1650）。
* **角色**：開發／驗證 + 資料層。
* **對立機／完整包**：[`../aitopatom-b96e/`](../aitopatom-b96e/)（GB10 治理+推論）。

## 建議差異（相對 GB10）

| 項目 | 此機 |
|---|---|
| `OLLAMA_MODEL` 預設 | `qwen3:4b`（VRAM 4GB；由 `tools.py` 依 hostname） |
| PostgreSQL | 預期 **有**（17.x） |
| ollama | 2026-07-21 快照：**未安裝** |
| repo 路徑 | **勿寫死**；以該機 clone 為準 |

完整一鍵檢查腳本可依 `aitopatom-b96e/setup_check.sh` 為此機複製並改 `EXPECTED_HOST`／服務斷言後補齊。
