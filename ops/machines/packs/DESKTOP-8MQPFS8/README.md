# 設定包：`DESKTOP-8MQPFS8`（精簡 stub）

* **主機**：僅適用 **`DESKTOP-8MQPFS8`**（WSL2 · x86_64 · GTX 1650）。
* **角色**：開發／驗證 + 資料層。
* **對立機／完整包**：[`../aitopatom-b96e/`](../aitopatom-b96e/)（GB10 全執行 T1 目標）。
* **正典 remote（2026-07-22）**：public monorepo [`tsaitsangchi/augur`](https://github.com/tsaitsangchi/augur)（`main`）。**勿**再追蹤 `augur-constitution`。

## 建議差異（相對 GB10）

| 項目 | 此機 |
|---|---|
| `OLLAMA_MODEL` 預設 | `qwen3:4b`（VRAM 4GB；由 `tools.py` 依 hostname） |
| PostgreSQL | 預期 **有**（17.x） |
| ollama | 2026-07-21 快照：**未安裝** |
| repo 路徑 | **勿寫死**；以該機 clone 為準；`PROJECT_ROOT`＝此機路徑 |

## 觀察期：改指 public augur

在此機執行：[`RETARGET-TO-PUBLIC-AUGUR.md`](RETARGET-TO-PUBLIC-AUGUR.md)（改 `origin` 或重 clone；通過驗收後 GB10 方可步 6 刪 archived 倉）。

完整一鍵檢查腳本可依 `aitopatom-b96e/setup_check.sh` 為此機複製並改 `EXPECTED_HOST`／服務斷言後補齊。
