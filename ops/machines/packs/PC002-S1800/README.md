# 設定包：`PC002-S1800`

* **主機**：僅適用 **`PC002-S1800`**（WSL2 · x86_64 · Intel UHD 630 · **無 NVIDIA**）。
* **角色**：開發／驗證 + 資料層（PostgreSQL + qdrant + 全棧 UI）；本地小／中模型（CPU）。
* **≠** [`../DESKTOP-8MQPFS8/`](../DESKTOP-8MQPFS8/)（另一台 WSL2：Ryzen + GTX 1650）。
* **對立大模型機**：[`../aitopatom-b96e/`](../aitopatom-b96e/)（GB10 · 122GiB）。
* **正典 remote**：public monorepo [`tsaitsangchi/augur`](https://github.com/tsaitsangchi/augur)（`main`）。

## 本機路徑（2026-07-23 實測）

| 項目 | 值 |
|---|---|
| 正典 clone | **`/home/hugo/project/augur`** |
| Windows 使用者 | `C:\Users\S114013.GSMCTW` |
| `.wslconfig` | `memory=12GB` · `processors=12` · `swap=64GB` |
| Ollama binary | `/home/hugo/ollama/bin/ollama`（0.31.1） |

## 硬體對齊的 MCP／模型

| 項目 | 此機 | 勿用 |
|---|---|---|
| 主路徑（chat／advisor） | **`qwen3:8b`**（程式預設） | 勿把 8b 寫進 MCP `LLM_MODEL` |
| MCP `LLM_MODEL` | **`qwen3:4b`**（已釘於 `.mcp.json`） | GB10 大模型／`qwen3-coder-next` |
| `OLLAMA_NUM_CTX`（MCP） | **`4096`** | `32768`（GB10） |
| `OLLAMA_KEEP_ALIVE`（MCP） | **`30s`**（短卸載，讓 8b 可換載） | 長駐雙模型 |
| `OLLAMA_TEMPERATURE`（MCP） | **`0`** | — |
| `EMBED_MODEL` | `nomic-embed-text`（若未裝需另 pull） | — |
| CUDA／NVIDIA | **無** | 勿假設 `nvidia-smi` |
| PostgreSQL | **17.9** online @5432 | — |
| Qdrant | **1.18.2** @6333 | — |

硬體快照 SSOT：[`../../PC002-S1800.md`](../../PC002-S1800.md)。  
改 mcp 後於 Cursor **Reload MCP**。

## 驗收速查

```bash
hostname   # 必須 PC002-S1800
cd /home/hugo/project/augur
git remote -v   # origin → tsaitsangchi/augur.git
free -h         # Mem≈11GiB、Swap=64GiB
pg_lsclusters   # 17/main online
curl -s http://127.0.0.1:11434/api/version
curl -s http://127.0.0.1:6333/ | head -c 120
systemctl --user is-active augur-chat augur-advisor augur-admin augur-probability augur-ollama augur-qdrant
```
