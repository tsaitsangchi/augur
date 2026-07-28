# augur MCP 雙平台掛載 SOP（Claude Code ＋ Cursor）

> 2026-07-28 統一（hugo「處理此專案所有的 MCP 可以 mount claude 與 cursor AI 平台」）。
> **兩平台設定完全一致**：`.mcp.json`（Claude，專案級）＝ `.cursor/mcp.json`（Cursor）——改一邊請同步另一邊（機械檢查：`python3 -c "import json; assert json.load(open('.mcp.json'))==json.load(open('.cursor/mcp.json'))"`)。

## 三個 MCP 伺服器

| server | 用途 | 外部依賴 | 工具 |
|---|---|---|---|
| `constitution` | 憲章/治權條款檢索、layer_status、lint | **零**（純檔案） | search_clauses/get_clause/get_ruling/layer_status/lint_compliance… |
| `local-llm` | 本地 LLM（Ollama）ask/summarize/extract/research | Ollama :11434 | local_ask/local_summarize/local_extract/local_map_reduce/local_research |
| `project-memory` | repo 語意索引與 recall | Ollama :11434（nomic-embed） | recall/memory_status（索引另跑 `python3 -m tools.project_memory_mcp index`） |

## 掛載方式

- **Claude Code**：開專案即自動讀 `.mcp.json`（首次會問一次是否信任專案 MCP）。
- **Cursor**：讀 `.cursor/mcp.json`（Settings → MCP 可看到三台；同為 stdio）。
- 兩者皆經 **wrapper**（`tools/run_*_mcp.sh`）啟動：cwd 無關（wrapper 自 `cd` 至 repo 根＋設 PYTHONPATH），已實測自 `/tmp` 起亦可真呼叫。

## 設計裁定（#12 單一住所）

- **模型選擇唯一住所＝工具內 `_default_model_for_host()`**（PC002-S1800/DESKTOP→qwen3:4b、GB10→qwen3-coder-next；`LLM_MODEL`/`OLLAMA_MODEL` env 可覆寫）。config 與 wrapper **皆不寫死模型**——2026-07-28 前 Cursor config 寫死 `LLM_MODEL=qwen3:4b`、wrapper 另有一張與工具打架的 host 表（GB10 寫 30b-a3b），已一併移除。
- `OLLAMA_KEEP_ALIVE=30s`：RAM 緊的兩機上用完快卸載，減少與評測臂/advisor 8b 的擠壓。
- `EMBED_TIMEOUT_S=180`：Ollama 車道忙時（批跑/8b 對話）嵌入排隊常超 90s 預設——實錄 2026-07-28 index 逾時即此因。**車道極忙時 index 仍可能逾時：等批收再跑，或臨時 `EMBED_TIMEOUT_S=600`。**

## 驗證指令（零 Ollama 煙測）

```bash
for m in constitution_mcp local_llm_mcp project_memory_mcp; do
  printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}\n' \
   | LOCAL_LLM_MCP_STUB=1 PROJECT_MEMORY_MCP_STUB=1 timeout 15 python3 -m tools.$m | head -1 | grep -q '"result"' \
   && echo "OK $m" || echo "FAIL $m"
done
```

## 已知陷阱

- **worktree**：Claude Code 於 worktree 開工時，wrapper 以**自身位置**定根 → 用的是 worktree 那份 code（正確），但 `project-memory` 的索引 db（`.project_memory/`）各 checkout 各一份——worktree 內 recall 命中的是 worktree 索引；主 checkout 的索引請在主目錄跑 index（詳 `ops/machines/PC002-S1800.md` 註記）。
- 週一 08:40 cron 已含三工具 `--selftest`（`verify_weekly.log`）。
