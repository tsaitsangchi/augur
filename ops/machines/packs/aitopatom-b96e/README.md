# 設定包：`aitopatom-b96e`（此機專用）

* **性質**：[I] 營運設定包，不創設 [N] 義務。
* **主機**：僅適用 **`aitopatom-b96e`**（NVIDIA GB10 · aarch64 · 122GiB）。
* **對立機**：`DESKTOP-8MQPFS8`（WSL2 · x86_64 · 有 PG）——**勿在此機套用對立機假設**。
* **硬體快照**：[`../../aitopatom-b96e.md`](../../aitopatom-b96e.md)（`collect_machine_info.sh` 產生）。

## 此機角色

**全執行節點（T1，2026-07-22 Steward 選定）**：治理 + 本地推論／語意記憶 + **目標**本機 PostgreSQL／qdrant／應用真跑。

| 已就緒 | T1 待補 |
|---|---|
| ollama、GB10 GPU、三支 MCP、monorepo、**PG :5432**＋**DB 54 GB**、**qdrant :6333**、**UI 開機自啟**（`install_services_gb10.sh`：advisor `:8399`／chat `:8090`／admin `:8500`／probability `:8600`，模型 **`qwen3:30b-a3b`**）、`venv`、advisor 結構煙霧 PASS | LLM picks 段缺、`entity_registry` 空（可本機 backfill） |

**執行手冊**：[`../../phase2/T1-GB10-FULLSTACK-RUNBOOK.md`](../../phase2/T1-GB10-FULLSTACK-RUNBOOK.md)（從第 0 步取證開始）。

## 開機常駐

- **Infra**：`augur-postgres`、`augur-qdrant`、`ollama`（linger 已開）。範本：[`../../phase2/systemd/`](../../phase2/systemd/)。
- **UI（GB10 安全腳本）**：`bash ops/phase2/install_services_gb10.sh` —— 只裝 advisor／chat／admin／probability，模型 **`qwen3:30b-a3b`**，**不**覆寫 qdrant／ollama。狀態：`--status`；停 UI：`--stop`。
- **勿**跑根目錄 `install_services.sh`（舊路徑／會衝突）。

## 檔案

| 檔 | 用途 |
|---|---|
| [`recommended.env`](recommended.env) | 建議環境變數（無密鑰；可 `set -a; source …; set +a`） |
| [`setup_check.sh`](setup_check.sh) | **一鍵檢查**（錯誤 hostname 拒絕；查 ollama／模型／repo／索引） |
| [`CHECKLIST.md`](CHECKLIST.md) | 開機／換 session／換機接續檢查清單 |

## 使用

```bash
# 終態根＝/home/giga/augur；過渡期若在 migrate 分支工作樹亦可
cd "${AUGUR_ROOT:-/home/giga/augur}"
./ops/machines/packs/aitopatom-b96e/setup_check.sh
set -a && source ops/machines/packs/aitopatom-b96e/recommended.env && set +a
```

MCP：共享 `.cursor/mcp.json` 已可攜；模型由 `tools/local_llm_mcp/tools.py` **依 hostname 預設 `qwen3:30b-a3b`**（可被 `OLLAMA_MODEL` 覆寫）。
