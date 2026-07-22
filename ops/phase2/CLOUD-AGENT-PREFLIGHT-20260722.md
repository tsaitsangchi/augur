# Cloud agent MCP preflight — 證據 — 2026-07-22

* **性質**：[I] 證據；非「雲端實地採用已完成」。
* **主機**：`aitopatom-b96e`

## 交付

| 產物 | 路徑 |
|---|---|
| Runbook | `ops/phase2/CLOUD-AGENT-MCP-PREFLIGHT.md` |
| 預檢腳本 | `ops/phase2/cloud_mcp_preflight.sh` |
| Pack 掛勾 | `ops/machines/packs/aitopatom-b96e/CHECKLIST.md` |

## GB10 loopback 預檢（已跑）

```
OLLAMA_URL=http://127.0.0.1:11434
✅ api/tags 可達
✅ 模型在列：qwen3-coder-next
✅ 模型在列：nomic-embed-text
✅ api/generate 有回應（煙霧）
```

## 待你側勾選

- [ ] Tailscale 入網；對端 `OLLAMA_URL=http://<gb10-ts-ip>:11434` 重跑預檢
- [ ] Cursor Cloud session 依 runbook §四觀察工具採用

不宣稱雲端實地採用完成；不公網裸開 11434。
