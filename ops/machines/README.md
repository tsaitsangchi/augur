# 機器基礎資訊（ops/machines/）

同一 Augur 專案在**多台不同軟硬體機器**上運行時，各機的環境資訊在此按機器分檔記錄。

## 運作原理

- **識別鍵＝主機名（hostname）**：每台一個檔 `ops/machines/<hostname>.md`，互不覆蓋。
- **同一 repo 共享**：專案本體（憲章、規格、程式、工具）經 GitHub 同步；機器基礎資訊各機獨立。
- **機器本地、不進 git**：`.env`、各機 venv（含 `gpu-verify/.gpu-test-venv`）、編譯產物等仍留本機（見 `.gitignore`）。
- **自動產生**：實測欄位由 `ops/collect_machine_info.sh` 產生，勿手改；手動註記寫在各檔尾 `<!-- NOTES -->` 區塊（重跑會保留）。

### 新增 / 更新一台機器

```bash
cd <repo 根>
git pull                          # 取得最新共享內容
./ops/collect_machine_info.sh     # 產生/更新本機 ops/machines/<hostname>.md
git add ops/machines/*.md && git commit -m "ops(machines): 更新 <hostname> 基礎資訊" && git push
```

> 在**一般終端機**執行（非 Cursor sandbox）；sandbox 內量測會出現 GPU 被擋、systemd/PostgreSQL 誤判為 offline/down 等假象（獨立 namespace 所致）。

## 機器清單

| 主機名 | 角色 | 平台 / 架構 | GPU | 檔案 |
|---|---|---|---|---|
| `DESKTOP-8MQPFS8` | 開發 / 本機驗證 | WSL2 · x86_64 | GTX 1650 4GB | [DESKTOP-8MQPFS8.md](DESKTOP-8MQPFS8.md) |
| _（另一台）_ | _待填_ | _待填_ | _待填_ | _在該機執行腳本後產生_ |

## 跨機比較（重點軸；各機詳情見其檔）

| 軸 | DESKTOP-8MQPFS8 | （另一台） |
|---|---|---|
| OS / 核心 | Ubuntu 24.04.4 · 6.18-WSL2 | — |
| CPU | Ryzen 5 3600 (6C/12T) | — |
| 記憶體 | ~15.6 GiB | — |
| GPU / CUDA | GTX 1650 · driver 12.6 · nvcc 12.0 | — |
| PostgreSQL / pgvector | 17.10 / 0.8.5 | — |

> 兩機若架構不同（如 x86_64 vs ARM64/aarch64），需注意：Python wheel（torch cu 版本）、`nvcc -arch`、二進位相依、PostgreSQL 擴充編譯等**不可直接共用**，各機依自身架構安裝。

---

## 跨機共享：專案相依與運行要點

以下為**與機器無關**的專案需求（各機皆適用）。

### augur-code（`augur-code/`）
- 套件：`pyproject.toml`（`name=augur`，requires-python ≥ 3.10）
- 核心相依：`psycopg2-binary`、`pandas`、`polars`、`numpy`、`scikit-learn`、`xgboost`、`lightgbm`、`catboost`、`jieba`、`shap`
- 選用群組：`deep`（`torch`、`sentence-transformers`）、`admin`（pdf/docx/pptx/xlsx/paramiko）、`dev`（pytest）
- 各機需備：本機 `venv` + `.env`（連線/密鑰，**已 gitignore，勿提交**）

### augur-constitution（本 repo）
- MCP 相依：`requirements-mcp.txt`（`fastapi`、`uvicorn[standard]`、`pydantic>=2`、`httpx`）
- MCP server：`.mcp.json` → `constitution`（`python3 -m tools.constitution_mcp`，`PYTHONPATH` 指向 repo 上層 `augur/`）
- 憲章 lint gate：`python3 -m tools.constitution_lint report`（repo 根執行；純 stdlib）
- 資料層：PostgreSQL + pgvector（生產庫 `augur`、沙盒庫 `augur_sandbox`；詳見 `infrastructure/ENVIRONMENT-SPEC.md`）

---

## 與治理規格之關係

規範性環境登錄以受治理之 [`../../infrastructure/ENVIRONMENT-SPEC.md`](../infrastructure/ENVIRONMENT-SPEC.md)（綁定 AUGUR-L7 L7.50）為準。本目錄為 **[I] 資訊性營運快照，不具規範力、不取代該規格**。

**2026-07-21 已知差異**（本機升級/安裝所致，是否走正式程序更新由 Steward 裁定）：

| 項目 | ENVIRONMENT-SPEC（2026-07-18） | DESKTOP-8MQPFS8 現況（2026-07-21） |
|---|---|---|
| PostgreSQL | 17.9 | **17.10** |
| pgvector | 0.8.4 | **0.8.5** |
| CUDA Toolkit (`nvcc`) | （未載，當時未裝） | **12.0.140 已裝** |
