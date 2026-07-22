# vLLM spike — GB10 — 2026-07-22

* **性質**：[I] 證據紀錄（不創設 [N] 義務）。
* **主機**：`aitopatom-b96e`（aarch64 / NVIDIA GB10 / driver 580.159.03 / CUDA 13.0）
* **範圍**：獨立 venv 安裝 vLLM、最小 serve 煙霧、local-llm MCP `LLM_BACKEND=openai` 路徑；**不**改 mcp.json 預設。

## 結果總覽

| 項 | 結果 |
|---|---|
| `python3 -m tools.local_llm_mcp selftest` | **OK** |
| `pip install vllm` → `~/augur-venvs/vllm` | **PASS**（vllm **0.25.1**） |
| `vllm serve` 煙霧 | **PASS**（`Qwen/Qwen3-0.6B` → `:8000`） |
| `bash ops/phase2/vllm_preflight.sh --chat` | **PASS** |
| MCP `local_ask` via openai 後端 | **PASS**（provenance 含 `@ openai:http://127.0.0.1:8000/v1`） |
| `.cursor/mcp.json` 預設 | **未改**（仍 Ollama／`qwen3-coder-next`） |
| project-memory embed | **仍 Ollama**（`nomic-embed-text`） |

**Spike 裁決：PASS**（aarch64 wheel 可得；小模煙霧與 MCP 適配皆綠）。

## 安裝證據

```text
python3 -m venv ~/augur-venvs/vllm
source ~/augur-venvs/vllm/bin/activate
pip install -U pip wheel
pip install vllm   # → Successfully installed … vllm-0.25.1
python -c 'import vllm; print(vllm.__version__)'  # 0.25.1
```

## 煙霧證據

啟動（約 3 分至 Application startup complete）：

```bash
vllm serve Qwen/Qwen3-0.6B \
  --host 127.0.0.1 --port 8000 \
  --served-model-name qwen3-0.6b --max-model-len 4096
```

- `GET /v1/models` → 200；`id=qwen3-0.6b`
- `POST /v1/chat/completions` → 200（`vllm_preflight.sh --chat`）
- MCP：

```text
(local model: qwen3-0.6b @ openai:http://127.0.0.1:8000/v1)
⚠ 本輸出為本地小模型生成，屬 [I] 輔助，不得原文貼入任何 [N] 治理文書。
…
MCP_OPENAI_SMOKE: PASS
```

煙霧後已 `pkill` 停掉 vLLM（不常駐、未 enable user unit）。

## 觀察／風險

- 預設 KV 配置下，即使 0.6B 也會吃滿近整機 unified memory（log：`GPU KV cache size: ~1M tokens`）。上 30B-A3B 前須降 `--gpu-memory-utilization`／`max-model-len`，並先卸 Ollama 大模。
- 產線模型與 systemd 範本仍指向 MoE／Instruct 候選；以本機可載為準，見 `VLLM-GB10.md`。
- mcp.json **通過煙霧仍維持 Ollama 預設**（計畫定案）。

## 產物路徑

| 檔 | 角色 |
|---|---|
| `tools/local_llm_mcp/tools.py` | 雙後端 `_generate_ollama`／`_generate_openai` |
| `tools/local_llm_mcp/selftest.py` | stub 雙後端＋死埠 fail-loud |
| `tools/local_llm_mcp/README.md` | env 表 |
| `ops/phase2/VLLM-GB10.md` | runbook |
| `ops/phase2/systemd/augur-vllm.service` | user unit 範本（預設不 enable） |
| `ops/phase2/vllm_preflight.sh` | `/v1/models`＋可選 chat |
| `ops/machines/packs/aitopatom-b96e/recommended.env` | 註解掉的 LLM_BACKEND 區塊 |
| 本檔 | 煙霧證據 |
