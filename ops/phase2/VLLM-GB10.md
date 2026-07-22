# vLLM on GB10（可選後端）

* **性質**：[I] 運維 runbook（不創設 [N] 義務）。
* **主機**：`aitopatom-b96e`（NVIDIA GB10 / aarch64）
* **目的**：讓 `local-llm` MCP 可經 `LLM_BACKEND=openai` 打 vLLM OpenAI 相容 API；**預設仍 Ollama**。
* **不改**：`.cursor/mcp.json` 預設、`project-memory` 嵌入（維持 Ollama `:11434`）。

## 架構

| 埠 | 服務 | 用途 |
|---|---|---|
| `11434` | Ollama | embed（project-memory）＋ MCP 預設後端 |
| `8000` | vLLM（可選） | `local-llm` 當 `LLM_BACKEND=openai` |

## 獨立 venv（勿污染主 `venv`）

```bash
mkdir -p ~/augur-venvs
python3 -m venv ~/augur-venvs/vllm
source ~/augur-venvs/vllm/bin/activate
python -m pip install -U pip wheel
# 官方 wheel／CUDA 對 aarch64 可能不可用——失敗則見 VLLM-SPIKE-*.md，適配碼仍保留
pip install vllm
```

失敗時常見原因：無 aarch64 CUDA wheel、PyTorch/CUDA 與 GB10 驅動不符。回退＝繼續用 Ollama，不切 mcp.json。

## 首發模型（煙霧用）

選**小一檔可載入**之 Qwen3 Instruct／MoE（HF id），遠低於與 Ollama 搶滿 ~120G：

| 建議 | 說明 |
|---|---|
| HF | 例：`Qwen/Qwen3-30B-A3B-Instruct`（以實機可載為準；過大則換更小 Instruct） |
| `--served-model-name` | 與 MCP `LLM_MODEL` **同一字串**（例 `qwen3-30b-a3b-instruct`） |

煙霧前若 Ollama 已載大模，先 `ollama stop qwen3:30b-a3b`（保留 `nomic-embed-text`）。

## 手動啟動

```bash
source ~/augur-venvs/vllm/bin/activate
vllm serve Qwen/Qwen3-30B-A3B-Instruct \
  --host 127.0.0.1 \
  --port 8000 \
  --served-model-name qwen3-30b-a3b-instruct \
  --max-model-len 32768
```

參數以實機可跑為準（OOM 則降 `--max-model-len` 或換更小模型）。

## systemd user unit（預設不 enable）

範本：`ops/phase2/systemd/augur-vllm.service`

```bash
mkdir -p ~/.config/systemd/user
cp /home/giga/augur/ops/phase2/systemd/augur-vllm.service ~/.config/systemd/user/
systemctl --user daemon-reload
# 預設不 enable；僅手動起停：
systemctl --user start augur-vllm.service
systemctl --user status augur-vllm.service
systemctl --user stop augur-vllm.service
```

**不要** `systemctl --user enable augur-vllm`，除非煙霧穩定且你明示要開機自啟。

## 預檢

```bash
bash ops/phase2/vllm_preflight.sh
# 可選一發 chat：
bash ops/phase2/vllm_preflight.sh --chat
```

## 切 MCP 到 vLLM（煙霧通過後）

在 shell 或臨時覆寫（**勿改** repo 內 mcp.json 預設，除非另案拍板）：

```bash
export LLM_BACKEND=openai
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY=EMPTY
export LLM_MODEL=qwen3-30b-a3b-instruct
```

`recommended.env` 已附註解區塊。一秒回退：`unset LLM_BACKEND` 或 `LLM_BACKEND=ollama`。

## 驗收對照

| 項 | 標準 |
|---|---|
| MCP selftest | `python3 -m tools.local_llm_mcp selftest` → OK |
| 預設 mcp.json | 仍 Ollama／coder-next |
| 煙霧 | `vllm_preflight.sh` 綠；可選 `local_ask` provenance 含 `@ openai:` |
| 安裝失敗 | 證據記 FAIL；適配碼仍可用於他機／日後 |

證據檔：`ops/phase2/VLLM-SPIKE-YYYYMMDD.md`。
