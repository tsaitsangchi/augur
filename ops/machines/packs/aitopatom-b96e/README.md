# 設定包：`aitopatom-b96e`（此機專用）

* **性質**：[I] 營運設定包，不創設 [N] 義務。
* **主機**：僅適用 **`aitopatom-b96e`**（NVIDIA GB10 · aarch64 · 122GiB）。
* **對立機**：`DESKTOP-8MQPFS8`（WSL2 · x86_64 · 有 PG）——**勿在此機套用對立機假設**。
* **硬體快照**：[`../../aitopatom-b96e.md`](../../aitopatom-b96e.md)（`collect_machine_info.sh` 產生）。

## 此機角色

**全執行節點（T1，2026-07-22 Steward 選定）**：治理 + 本地推論／語意記憶 + **目標**本機 PostgreSQL／qdrant／應用真跑。

| 已就緒 | T1 待補 |
|---|---|
| ollama、GB10 GPU、三支 MCP、應用碼（`augur-code-work`） | PostgreSQL、qdrant、augur DB 還原、應用接線煙霧 |

**執行手冊**：[`../../phase2/T1-GB10-FULLSTACK-RUNBOOK.md`](../../phase2/T1-GB10-FULLSTACK-RUNBOOK.md)（從第 0 步取證開始）。

## 檔案

| 檔 | 用途 |
|---|---|
| [`recommended.env`](recommended.env) | 建議環境變數（無密鑰；可 `set -a; source …; set +a`） |
| [`setup_check.sh`](setup_check.sh) | **一鍵檢查**（錯誤 hostname 拒絕；查 ollama／模型／repo／索引） |
| [`CHECKLIST.md`](CHECKLIST.md) | 開機／換 session／換機接續檢查清單 |

## 使用

```bash
cd /home/giga/augur          # 此機 repo 根（勿用他機路徑）
./ops/machines/packs/aitopatom-b96e/setup_check.sh
# 可選：載入建議 env
set -a && source ops/machines/packs/aitopatom-b96e/recommended.env && set +a
```

MCP：共享 `.cursor/mcp.json` 已可攜；模型由 `tools/local_llm_mcp/tools.py` **依 hostname 預設 `qwen3:30b-a3b`**（可被 `OLLAMA_MODEL` 覆寫）。
