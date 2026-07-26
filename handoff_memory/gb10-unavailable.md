---
name: gb10-unavailable
description: hugo 2026-07-25 宣告：沒有 GB10 機器、AI 進化只能在本機（DESKTOP-8MQPFS8）——凡記憶/文件稱「GB10=大模型機/訓練機」皆以此為準修正
metadata: 
  node_type: memory
  type: project
  originSessionId: b6cddf62-b16d-44ba-af86-bbdb2cb161c8
  modified: 2026-07-26T09:43:16.684Z
---

**hugo 2026-07-25 對話宣告：「沒有GB10機器。我目前只能在本機設備進行進化」。**

**Why**：repo 文件（ops/machines/packs/aitopatom-b96e、tools.py hostname 分支、07-22 runbook）與多則記憶把 GB10（aitopatom-b96e、122GB 統一記憶體）當「對立機＝大模型/訓練機」，演化閉環計畫 P2 原指定 GB10 訓練。此宣告後**該機不可用**（原因未細究、不重要）——一切「丟給 GB10」的規畫路徑失效。

**How to apply**：
- 演化/訓練規畫一律以**本機硬體**為界：GTX 1650 4GB（idle free ~2.7GB，Windows 顯示驅動吃 1.2GB 拿不回）＋25GB RAM（PG shared_buffers 6GB 常駐）＋6 核 Zen2。
- 本機可行進化階梯（2026-07-25 初評，**2026-07-26 對抗審查＋親驗後修正如下**）：
  - **Tier1 = prompt-pack／grammar 強制**（零訓練、最高 ROI）——仍成立，但其「有效」的舊證據已隨壞尺作廢，見 [[eval-boilerplate-floor]]。
  - **Tier2 GPU QLoRA on qwen3:1.7b = 硬體上可行**（實測外推：1.7B NF4 base 1288 MiB，方法先在自身驗證誤差 0.05%）；**4B 判 no-go**（NF4 2548 MiB，含 741.9 MiB 未被 bitsandbytes 量化的 embedding——只量 `nn.Linear`；WSL2 有 host-memory fallback，超量不 OOM 只慢 3.7×，故「跑起來了」不等於裝得下）。
  - **GTX 1650 = TU117，唯一沒有 tensor core 的 Turing**：實測 bf16(模擬) 2.147 s/step vs fp16 6.408 s/step（3.0×）——**別預設 fp16 較快**；dtype 須以 20-step bake-off 實測決定。
  - **CPU LoRA on 4b 實質退場**（原估 171 條 1-2 天／輪，語料已近千條 → 週級以上，不划算）。
  - 硬體路＝二手 12GB GPU 即解鎖 4b QLoRA（不變）。
- **但硬體可行 ≠ 該做**：2026-07-26 裁決＝教材 87% 是文獻 metadata，背進權重＝訓練幻覺＋違 #9／#10；LoRA 僅「該拒答時拒答／多實體消歧義」窄塊有剩餘價值。詳 [[augur-self-evolution-plan-map]]。
- 權重鏈實證：**ollama 的 safetensors ADAPTER 路對 qwen3 不支援**（只有 llama／gemma2 converter），唯一路線＝PEFT → `llama.cpp/convert_lora_to_gguf.py` → `.gguf` → Modelfile `ADAPTER`；llama.cpp 本機未裝，且**絕不可跑它的 requirements.txt**（會把 venv 的 torch/transformers/numpy 拖回舊版、連帶拖壞 peft/trl/dspy）。
- 騰 VRAM 只需 `ollama stop qwen3:4b`（或 API `keep_alive:0`）——實測四個 augur user 服務仍 active，**不必 `systemctl stop ollama`**、不需 root。
- repo 的 GB10 機器包/文件＝史料保留、勿當現況引用。
- 見 [[augur-project-map]]（兩機敘述過時）、[[augur-self-evolution-plan-map]]、設計書 `reports/augur_tier2_lora_spike_design_20260726.md`。
