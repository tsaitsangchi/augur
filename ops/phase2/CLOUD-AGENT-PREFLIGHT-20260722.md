# Cloud agent MCP preflight — 證據 — 2026-07-22

* **性質**：[I] 證據；非「雲端實地採用已完成」。
* **主機**：`aitopatom-b96e`
* **更新**：同日 Tailscale／Ollama bind 診斷（agent 本機探測）

## 交付

| 產物 | 路徑 |
|---|---|
| Runbook | `ops/phase2/CLOUD-AGENT-MCP-PREFLIGHT.md` |
| 預檢腳本 | `ops/phase2/cloud_mcp_preflight.sh` |
| Pack 掛勾 | `ops/machines/packs/aitopatom-b96e/CHECKLIST.md` |

## GB10 loopback 預檢（PASS）

```
OLLAMA_URL=http://127.0.0.1:11434
✅ api/tags 可達
✅ 模型在列：qwen3-coder-next
✅ 模型在列：nomic-embed-text
✅ api/generate 有回應（煙霧）
```

複核（2026-07-22）：`curl 127.0.0.1:11434/api/tags` — 3 models；`qwen3-coder-next`／`nomic-embed-text` 在列。

## Tailscale（FAIL — 未安裝）

| 檢查 | 結果 |
|---|---|
| `command -v tailscale` | **FAIL** — not found（系統提示可用 `sudo snap install tailscale`；`dpkg`／`snap list` 亦無套件） |
| `tailscale status` | **未跑**（binary 不存在，exit 127） |
| `tailscale ip -4` | **未跑**（同上） |
| 對端 `OLLAMA_URL=http://<ts-ip>:11434` 預檢 | **PENDING** — 無 ts-ip，**未執行**（避免假綠） |

### 你側下一步（需瀏覽器登入；agent 不代跑互動 `tailscale up`）

依 runbook §一（官方腳本優先於 snap）：

```bash
# 在 GB10 (aitopatom-b96e)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up          # 瀏覽器登入
tailscale status
tailscale ip -4            # 記下 <gb10-ts-ip>
```

入網後，**對端**（同 tailnet 跳板／模擬雲端）再跑：

```bash
OLLAMA_URL=http://<gb10-ts-ip>:11434 bash ops/phase2/cloud_mcp_preflight.sh
```

## Ollama bind（診斷）

```
ss -ltn | grep 11434
LISTEN ... 127.0.0.1:11434
```

**現況**：Ollama **僅**聽 `127.0.0.1:11434`。即使 Tailscale 入網，對端直連 `<ts-ip>:11434` **會失敗**，除非另開通道。

**建議（勿公網裸開；未改系統）**：

1. **優先**：Tailscale **serve／proxy**（或僅對 tailnet IP bind）把本機 11434 暴露給 tailnet。
2. 或：`OLLAMA_HOST=<gb10-ts-ip>:11434` + Tailscale ACL 僅受信 tag——**需你核准**；**禁止**未經核准改 `0.0.0.0`／公網。

本波 **未** 變更 `OLLAMA_HOST`。

## 待你側勾選

- [ ] Tailscale 安裝＋`tailscale up` 登入；取得 `<gb10-ts-ip>`
- [ ] 解決 127.0.0.1-only bind（serve／proxy 或核准之 tailnet bind）後，對端 `OLLAMA_URL=http://<gb10-ts-ip>:11434` 重跑預檢綠
- [ ] Cursor Cloud session 依下方 §四 checklist 觀察工具採用

不宣稱雲端實地採用完成；不公網裸開 11434。

---

## Cursor Cloud session checklist（可貼／可勾）

來源：`CLOUD-AGENT-MCP-PREFLIGHT.md` §四。前置：Tailscale 通 + `OLLAMA_URL` 已設進 Cloud secrets／MCP env。

**Env（勿寫進 git）**

```text
OLLAMA_URL=http://<gb10-ts-ip>:11434
OLLAMA_MODEL=qwen3-coder-next
OLLAMA_NUM_CTX=32768
EMBED_MODEL=nomic-embed-text
```

`cwd` = 雲端 checkout 的 monorepo 根。

**勾選**

- [ ] 通道：`curl $OLLAMA_URL/api/tags` 含 `qwen3-coder-next`、`nomic-embed-text`
- [ ] `local_ask` 來源標記含 **coder-next**
- [ ] 跨檔問句是否**自然**呼叫 `local_research`（對照 `.cursor/rules/local-mcp-routing.mdc`）
- [ ] 治理問句走 `constitution`，非 local-llm 濃縮生效規格
- [ ] 無索引時 `recall`／`local_research` **isError**（不靜默空答）
