---
name: gb10-unavailable
description: hugo 2026-07-25 宣告：沒有 GB10 機器、AI 進化只能在本機（DESKTOP-8MQPFS8）——凡記憶/文件稱「GB10=大模型機/訓練機」皆以此為準修正
metadata: 
  node_type: memory
  type: project
  originSessionId: b6cddf62-b16d-44ba-af86-bbdb2cb161c8
  modified: 2026-07-25T10:08:13.562Z
---

**hugo 2026-07-25 對話宣告：「沒有GB10機器。我目前只能在本機設備進行進化」。**

**Why**：repo 文件（ops/machines/packs/aitopatom-b96e、tools.py hostname 分支、07-22 runbook）與多則記憶把 GB10（aitopatom-b96e、122GB 統一記憶體）當「對立機＝大模型/訓練機」，演化閉環計畫 P2 原指定 GB10 訓練。此宣告後**該機不可用**（原因未細究、不重要）——一切「丟給 GB10」的規畫路徑失效。

**How to apply**：
- 演化/訓練規畫一律以**本機硬體**為界：GTX 1650 4GB（idle free ~2.7GB，Windows 顯示驅動吃 1.2GB 拿不回）＋25GB RAM（PG shared_buffers 6GB 常駐）＋6 核 Zen2。
- 本機可行進化階梯（2026-07-25 評估）：Tier1=prompt-pack/few-shot 演化（零訓練、gate 可測、最高 ROI）；Tier2=CPU LoRA on 4b（週級 cadence、須停 PG 或 bf16 實測）或 GPU LoRA on qwen3:1.7b 特化生（1.1GB NF4 塞得進 2.7GB）；硬體路=二手 12GB GPU 即解鎖 4b QLoRA。
- repo 的 GB10 機器包/文件＝史料保留、勿當現況引用。
- 見 [[augur-project-map]]（兩機敘述過時）、演化計畫 reports/augur_local_ai_evolution_loop_plan_20260725.md（P2 已依此改寫）。
