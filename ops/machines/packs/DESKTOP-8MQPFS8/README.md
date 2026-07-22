# 設定包：`DESKTOP-8MQPFS8`

* **主機**：僅適用 **`DESKTOP-8MQPFS8`**（WSL2 · x86_64 · GTX 1650 4GB）。
* **角色**：開發／驗證 + 資料層（PostgreSQL）；本地小模型 MCP。
* **對立機**：[`../aitopatom-b96e/`](../aitopatom-b96e/)（GB10 · 大模型／122GiB）。
* **正典 remote**：public monorepo [`tsaitsangchi/augur`](https://github.com/tsaitsangchi/augur)（`main`）。**勿**再追蹤 `augur-constitution`。

## 本機路徑（2026-07-22 實測）

| 項目 | 值 |
|---|---|
| 正典 clone | **`/home/giga/augur/augur-code`** |
| 歷史 constitution 樹 | `/home/giga/augur/augur-constitution`（⛔ superseded；見該樹 `DEPRECATED.md`） |
| Cursor workspace 根 | `/home/giga/augur` → MCP 用上層 `.cursor/mcp.json`，**cwd 釘死 augur-code** |

## 硬體對齊的 MCP／模型

| 項目 | 此機 | 勿用（GB10） |
|---|---|---|
| `OLLAMA_MODEL` | **`qwen3:4b`**（~2.5GB；VRAM 4GB 上限） | `qwen3-coder-next`、`qwen3:30b-a3b` |
| `OLLAMA_NUM_CTX` | **`8192`**（hostname 預設） | `32768`（GB10） |
| `EMBED_MODEL` | `nomic-embed-text` | — |
| ollama | **0.32.1** active（2026-07-22） | — |
| PostgreSQL | **17.10** online | GB10 未裝 |

共享 repo 設定不寫死模型：`tools.local_llm_mcp` 依 hostname=`DESKTOP-8MQPFS8` 自動選 `qwen3:4b`。工作區 MCP 額外顯式覆寫，避免誤載 GB10 預設。

## 環境基準與最佳化計畫

| 文件 | 用途 |
|---|---|
| [`ENV-BASELINE-20260722.md`](ENV-BASELINE-20260722.md) | 硬體／服務鎖定快照 |
| [`OPTIMIZATION-PLAN.md`](OPTIMIZATION-PLAN.md) | 分階段系統最佳化計畫（現行） |

## 觀察期：改指 public augur

若尚未改 remote：[`RETARGET-TO-PUBLIC-AUGUR.md`](RETARGET-TO-PUBLIC-AUGUR.md)。

## 驗收速查

```bash
hostname   # DESKTOP-8MQPFS8
cd /home/giga/augur/augur-code
git remote -v   # 僅 origin → tsaitsangchi/augur.git
test -d src/augur && test -d constitution && test -d tools/constitution_mcp && echo MONOREPO_OK
ollama list     # 應有 qwen3:4b；建議另有 nomic-embed-text
curl -s http://127.0.0.1:11434/api/version
```
