---
name: venv-finetune-stack-absent
description: 07-30 親驗本機 venv 無 peft/trl/bitsandbytes/gguf(僅 accelerate+datasets);LoRA 路線須先補環境再談訓練
metadata: 
  node_type: memory
  type: project
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-30T03:55:13.209Z
---

2026-07-30 親驗 `pip list`（本機 PC002-S1800 venv）：**有** torch 2.4.1／transformers 5.12.1／accelerate 1.14.0／datasets 2.17.1／sentence-transformers 5.6.0／lightgbm／xgboost／sklearn／statsmodels／arch（GARCH）；**無** peft、trl、bitsandbytes、gguf、dspy。

**Why**：MEMORY.md 索引第 15 行（07-25 晚）記「venv 新增 peft/trl/dspy/gguf」——與本機實況不符（DB 於 07-18 重匯、venv 可能重建，或該記錄屬另一台機器）。若照該記憶規劃 1.7b QLoRA 訓練，會在「環境已備」的假前提上排程，動工即撞 ImportError。

**⚠ 載具歸屬（2026-07-30 親驗，比套件更硬的阻塞）**：**GTX 1650 4GB 屬 DESKTOP-8MQPFS8，不是當家機**。當家機 PC002-S1800 之 SSOT 明寫 `GPU: 無 nvidia-smi`／`nvcc: 未安裝`／「本地小中模型 CPU-only，無獨顯」，實測 `torch.cuda.is_available()=False`。而 hugo 已拍板本機當家、DESKTOP 僅週末開 ⇒ **QLoRA 在當家機物理不可行**，訓練只能週末在 DESKTOP、平日僅評測。我 2026-07-30 曾把 DESKTOP 的 GPU 當成本機能力寫進計畫書（假兆③：憑記憶未實證該硬體屬哪台機），已更正。

**How to apply**：AI 自進化線（LoRA／QLoRA）任何計畫必須把 **環境前置列為 P0 且附 import smoke，並強制輸出 hostname**（CLAUDE #23）：`pip install peft trl bitsandbytes` → 4-bit 載入 smoke **於 DESKTOP** → 才進訓練；**於當家機跑出的 smoke 一律不算通過**；`llama.cpp` 仍未裝且**絕不可跑其 requirements.txt**（會拖壞 venv，見 [[gb10-unavailable]]）。相關：[[guard-mechanisms-that-silently-fail]]（記憶亦會靜默過期）。
