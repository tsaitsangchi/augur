---
name: machine-pc002-s1800-hardware
description: 本機 PC002-S1800 硬體要點：SSOT 在 repo 機器文件；非顯而易見發現＝兩支 DIMM 同插 Channel B → 單通道、頻寬砍半（CPU-only LLM 直接受害）
metadata: 
  node_type: memory
  type: project
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-27T02:44:45.419Z
---

**本機 hostname＝`PC002-S1800`**（ASUS ExpertCenter D700TA、i5-10500 6C/12T、實體 16GB、Intel UHD 630 內顯無獨顯、WD Blue SN550 1TB NVMe、Win11 Pro 26200；WSL2 Ubuntu 24.04 `memory=12GB`／`processors=12`／`swap=64GB`）。

**硬體 SSOT＝repo `ops/machines/PC002-S1800.md`**（由 `ops/collect_machine_info.sh` 自動產生、勿手改；手動註記寫檔尾 NOTES 區塊）——規格細節查該檔，**不要在記憶裡複製一份**（會過時）。此處只留 repo 沒記、且會影響決策的兩點：

**① 記憶體是單通道（2026-07-27 WMI 實測發現，repo 文件未記）**：16GB＝2×8GB DDR4，但 `Win32_PhysicalMemory.DeviceLocator` 顯示兩支都插在 **`ChannelB-DIMM0` + `ChannelB-DIMM1`（BANK 2/3）、Channel A 兩槽全空** → 單通道模式、記憶體頻寬約砍半。且混插（Kingston 2667 + SK Hynix 3200）實跑 `ConfiguredClockSpeed=2400`。
**Why 重要**：本機無獨顯、本地 LLM（MCP `local-llm` 的 qwen3:4b、embedding nomic-embed-text）全在 CPU 跑，**token 生成速度是記憶體頻寬綁定**——理論上換槽可接近倍增本地推論吞吐。
**⛔ 但 hugo 2026-07-27 已拍板「不修」——不要再提案換槽**。本機是公司配發、Trend Micro Apex One 企業管理之機器，開機殼涉 IT 政策而非單純技術權衡。此條保留為**已知硬體特性**（效能異常時的判讀依據），不是待辦。實績參照：`qwen3:4b` 17.1 tok/s；STREAM Triad 6.85 GB/s（load≈6.3 下量測＝下限，非乾淨基線）。

**② 別套用 `DESKTOP-8MQPFS8` 的調優值**：那台是 Ryzen 5 3600＋GTX 1650＋WSL 25.4GiB；其 2026-07-25「極限調優」commit `e5414de`（WSL 26GB／swap 128GB／zram／PG `shared_buffers=6GB`／Ollama KEEP_ALIVE=1h＋flash-attn＋KV q8_0）**是那台的口徑**，本機 WSL 只有 12GB、照抄會 OOM。本機 MCP 走 `tools/local_llm_mcp` 的 per-host 邏輯（`PC002-S1800` → `qwen3:4b`／`num_ctx=4096`／`keep_alive=30s`），已是為本機挑的值。相關：[[machines-two-concurrent]]、[[db-import-tuning-hnsw-oom]]、[[qdrant-serving-hnsw-overfilter]]。
