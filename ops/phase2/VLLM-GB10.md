# vLLM on GB10（可選後端）

* **性質**：[I] 運維 runbook（不創設 [N] 義務）。
* **主機**：`aitopatom-b96e`（NVIDIA GB10 / aarch64）
* **目的**：`local-llm` MCP 可經 `LLM_BACKEND=openai` 打 vLLM；**倉庫 mcp 預設仍 Ollama**（改預設見窄案計畫）。
* **最佳化**：[`reports/local_llm_vllm_optimization_plan_20260722.md`](../../reports/local_llm_vllm_optimization_plan_20260722.md)
* **不變**：`project-memory` 嵌入維持 Ollama `:11434`。

## 架構與並存紀律

| 埠 | 服務 | 用途 |
|---|---|---|
| `11434` | Ollama | embed（`nomic-embed-text`）＋ MCP 現行預設／回退；產品 UI `qwen3:30b-a3b` |
| `8000` | vLLM（可選） | `local-llm` 當 `LLM_BACKEND=openai` |

**並存（P0）**

1. 起 vLLM 前若 Ollama 已載 **UI 大模**，先：`ollama stop qwen3:30b-a3b`（可保留 embed）。
2. unit 使用 `--gpu-memory-utilization 0.35`，刻意留空間給 embed。
3. **禁止**為圖方便改 `0.0.0.0` 公網暴露。
4. 產品 UI／advisor **不**改打 vLLM（本 runbook 範圍外）。

## 獨立 venv

```bash
mkdir -p ~/augur-venvs
python3 -m venv ~/augur-venvs/vllm
source ~/augur-venvs/vllm/bin/activate
python -m pip install -U pip wheel ninja
pip install vllm   # GB10 2026-07-22：0.25.1 OK；4B 編譯路徑需要 ninja
```

## 模型

| 階 | HF／served-name | 狀態 |
|---|---|---|
| L0 | `Qwen/Qwen3-0.6B`／`qwen3-0.6b` | 煙霧基線 |
| **L1（建議）** | `Qwen/Qwen3-4B`／`qwen3-4b` | P1 選定（見 `VLLM-OPT-20260722.md`） |
| L2 | `Qwen/Qwen3-30B-A3B-Instruct` | 本波未驗 |

`LLM_MODEL` 必須與 `--served-model-name` 同一字串。

## 手動／systemd 啟動

```bash
source ~/augur-venvs/vllm/bin/activate
vllm serve Qwen/Qwen3-4B \
  --host 127.0.0.1 --port 8000 \
  --served-model-name qwen3-4b \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.35
```

```bash
cp ops/phase2/systemd/augur-vllm.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user start augur-vllm.service   # 不 enable，除非另拍板
```

預檢（含 latency_ms）：

```bash
VLLM_MODEL=qwen3-4b bash ops/phase2/vllm_preflight.sh --chat
```

## 臨時 MCP 覆寫（未改倉庫預設）

```bash
export LLM_BACKEND=openai
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY=EMPTY
export LLM_MODEL=qwen3-4b
# 可選：OPENAI_MAX_TOKENS_ASK=256 等（見 tools/local_llm_mcp/README.md）
```

## 驗收

| 項 | 標準 |
|---|---|
| selftest | `python3 -m tools.local_llm_mcp selftest` OK |
| preflight | PASS＋`latency_ms` |
| embed 並存 | vLLM active 時 Ollama embed 仍通 |
| 倉庫 mcp | 仍 Ollama，除非窄案拍板 |

證據：`VLLM-SPIKE-*.md`、`VLLM-OPT-*.md`。
