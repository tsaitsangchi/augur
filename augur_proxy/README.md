# Augur Proxy — Multi-Channel Proxy (非 Model Context Protocol)

Multi-Channel Proxy (P0): cache-first routing with automatic backend selection.

## Quick start

```bash
pip install -r requirements-mcp.txt
python -m augur_proxy.selftest
python -m augur_proxy --port 8000
```

## Invoke

```bash
curl -s http://127.0.0.1:8000/invoke \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"explain L0 human authorization gate","type":"quick"}'
```

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `MCP_URL` | `http://127.0.0.1:8000/invoke` | Client endpoint |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Local LLM backend |
| `OLLAMA_MODEL` | `qwen3:4b` | Ollama model name |
| `REDIS_URL` | _(empty)_ | Optional Redis cache |
| `MCP_CLAUDE_STUB` | `0` | Force Claude stub when `1` |
| `MCP_AUDIT_LOG` | `logs/mcp_audit.log` | Audit log path |

## Routing

| Type | Backend | Use case |
|---|---|---|
| `quick` | Ollama (local) | Explain, summary |
| `static` | Cache only | Repeat lookups |
| `compliance` | Claude | Lint, WM/L7 checks |
| `audit` | Claude | Rulings, §8.x |

Classifier auto-detects type when `type` is omitted.

## Python client

```python
from tools.constitution_lint.mcp_client import invoke_mcp

result = invoke_mcp("explain L2", type="quick")
print(result["backend"], result["tokens"])
```
