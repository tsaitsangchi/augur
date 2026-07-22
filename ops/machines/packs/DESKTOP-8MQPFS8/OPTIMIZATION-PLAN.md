# DESKTOP-8MQPFS8 系統最佳化計畫

* **性質**：[I] 營運計畫（依本機鎖定基準，非 GB10）
* **基準時間**：2026-07-22 19:34 CST
* **基準檔**：[`ENV-BASELINE-20260722.md`](ENV-BASELINE-20260722.md)、[`../../DESKTOP-8MQPFS8.md`](../../DESKTOP-8MQPFS8.md)
* **對立機**：`aitopatom-b96e`（GB10 · 大模型／高記憶體）— **分工，不互相取代**

---

## 0. 鎖定現況（記住）

| 軸 | 現值 |
|---|---|
| 角色 | **資料層 + 開發／驗證 + 小模型 MCP** |
| WSL | Mem **24GB** · Swap **32GB** @ `D:\wsl\swap.vhdx` · CPU **12** |
| GPU | GTX 1650 **4GB**（可用 ~3GB） |
| 資料 | PostgreSQL **17.10** @5432 online |
| 推論 | Ollama **0.32.1** · **`qwen3:4b`** + `nomic-embed-text` |
| 正典碼 | `/home/giga/augur/augur-code` ↔ public `augur` monorepo |
| MCP | `PYTHONPATH`→augur-code · 模型 4b · ctx 8192 |
| 風險 | **C: 僅 ~108GB**；VRAM 小；勿跑 coder-next／30b |

**一句話策略**：本機專精「真資料 + 真 PG + 輕量本地 AI」；重推論／大 ctx 交給 GB10。

---

## 1. 目標架構（最佳化後的分工）

```
┌──────────── DESKTOP-8MQPFS8 ────────────┐     GitHub monorepo      ┌──────── GB10 ────────┐
│  ✅ PostgreSQL + pgvector（權威資料）     │◄───────────────────────►│  ✅ 大模型 / 高 ctx   │
│  ✅ 開發、遷移、驗證、報表               │                         │  ✅ MCP 重推論        │
│  ✅ MCP：4b 機械性輔助 + embed           │                         │  ❌ 無 PG（現況）     │
│  ⚠ 僅小 VRAM                             │                         │                      │
└─────────────────────────────────────────┘                         └─────────────────────┘
```

---

## 2. 分階段計畫

### Phase A — 穩定基線（本週 · 必做）

| # | 動作 | 完成標準 | 狀態（2026-07-22） |
|---|---|---|---|
| A1 | 凍結 WSL 資源 | 維持 `memory=24GB` / `swap=32GB@D:` / `processors=12`；**不再盲目加 swap** | ✅ 已核對生效 |
| A2 | MCP 穩定 | Reload 後三支 connected；設定維持 `PYTHONPATH`+`/usr/bin/python3`+`qwen3:4b` | ✅ 設定+import/embed 煙霧通過；Cursor 需 Reload 驗三綠燈 |
| A3 | 提交本機營運文件 | `ops/machines/*`、本計畫、MCP 可攜設定 push 到 public `augur` | ✅ 見 git |
| A4 | C: 騰空間 | 清 Windows 暫存／舊 WSL 備份／移大型檔到 D:；目標 C: 可用 **>150GB** | ✅ 2026-07-22：**FreeC≈169GB**（Temp + Overwolf→D: junction + Downloads 安裝包外置）；**WSL `ext4.vhdx` ~543GB 仍在 C:**（遷碟見 Phase D） |
| A5 | Ollama 單一實例 | 確認僅 giga 系統服務佔 11434；勿與他使用者雙開搶 4GB VRAM | ✅ 僅 `ollama.service` PID 佔 11434 |

### Phase B — 資料層最佳化（1–2 週）

| # | 動作 | 完成標準 |
|---|---|---|
| B1 | PG 健康 | `pg_lsclusters` online；必要時 `ALTER EXTENSION vector UPDATE`（0.8.5） |
| B2 | 連線與角色 | `.env` 的 `PROJECT_ROOT=/home/giga/augur/augur-code`；角色／庫名與 HANDOFF 一致 |
| B3 | 備份策略 | 定期 dump **寫到 D:**（勿堆在 C:）；保留最近 N 份 |
| B4 | 沙盒庫 | 維持／啟用 `augur_sandbox` 做危險遷移演練，勿直接動生產庫 |
| B5 | 資源配額 | PG `shared_buffers`／work_mem 依 **24GB RAM** 溫和設定（避免吃光給 Ollama／Cursor） |

**建議量級（起點，實測再調）**：`shared_buffers≈2GB`、`effective_cache_size≈12GB`、並行重查詢時注意與 Ollama 錯峰。

### Phase C — 本地 AI／MCP（持續）

| # | 動作 | 完成標準 |
|---|---|---|
| C1 | 模型紀律 | **只** `qwen3:4b` + `nomic-embed-text`；禁止 pull 30b／coder-next |
| C2 | ctx | 維持 `OLLAMA_NUM_CTX=8192`（4GB VRAM） |
| C3 | project-memory 索引 | 在 `augur-code` 建 `.project_memory/`（gitignore）；錯峰、限並行 |
| C4 | 路由 | 遵循 `.cursor/rules/local-mcp-routing.mdc`：重判斷回 Cursor；4b 只做機械性子任務 |
| C5 | 驗證腳本 | 定期 `./ops/gpu-verify/gpu_verify.sh`；MCP selftest |

### Phase D — 工作區／磁碟（本月）

| # | 動作 | 完成標準 |
|---|---|---|
| D1 | 單一正典 | 只在 `augur-code` 開發；archived constitution **只讀／可刪前再確認** |
| D2 | 大檔外置 | 模型快取、dump、vhdx 相關大檔優先 **D:** |
| D3 | 可選收斂 | 長期可把 monorepo 工作樹遷到路徑更短處；短期維持 `augur-code` 即可 |
| D4 | 監控 | 週記：`free -h`、`df -h / /mnt/c /mnt/d`、`ollama list`、`pg_lsclusters` |

### Phase E — 不做／延後（明確排除）

| 項目 | 原因 |
|---|---|
| Swap 再加到 64／256GB | 收益低、易 thrash；32GB 已足夠保險 |
| WSL memory=28–32GB | Windows／Cursor 易不穩；維持 24GB |
| 本機 vLLM／大 ctx | VRAM／RAM 不適合；歸 GB10 |
| 雙 Ollama 實例 | 搶 4GB VRAM |
| Docker 全棧重疊 | 非必要前不裝；先用原生 PG＋Ollama |

---

## 3. 資源預算（24GB RAM 怎麼切）

| 用途 | 建議保留 |
|---|---|
| OS + Cursor/agent | ~4–6 GB |
| PostgreSQL | ~4–8 GB（尖峰） |
| Ollama 4b + embed | ~3–5 GB |
| 編譯／測試／餘量 | ~6–8 GB |
| Swap 32GB | 僅尖峰溢位，避免當主記憶體用 |

---

## 4. 驗收清單（最佳化「完成」定義）

- [ ] `free -h`：Mem≈23–24Gi、Swap=32Gi
- [ ] `nproc`=12；`nvidia-smi` 可見 GTX 1650
- [ ] PG online；Ollama `/api/version` OK；僅 4b + embed
- [ ] Cursor 三支 MCP connected（無 Connection closed）
- [ ] 開發只在 `augur-code`；C: 可用空間回升
- [ ] 本計畫與 ENV-BASELINE 已進 git（或本機 NOTES 已鎖）

---

## 5. 下一步（建議執行序）

1. **現在**：Commit／push 機器基準 + 本計畫（若要同步他機）
2. **今天**：Reload MCP 驗三綠燈；清 C:
3. **本週**：PG 參數溫和調校 + dump 到 D:
4. **其後**：建立 project-memory 索引；與 GB10 維持「資料在此、重模型在彼」

---

## 6. 變更紀錄

| 日期 | 內容 |
|---|---|
| 2026-07-22 | 初版：依 WSL 24/32/12、GTX1650、PG17.10、Ollama 4b、monorepo 路徑鎖定 |
| 2026-07-22 | Phase A 執行：WSL／MCP／Ollama 核對；C: 清至 ~169GB 可用；營運文件進 git |
