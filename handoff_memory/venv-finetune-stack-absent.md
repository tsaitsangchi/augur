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

**How to apply**：AI 自進化線（LoRA／QLoRA）任何計畫必須把 **環境前置列為 P0 且附 import smoke**（CLAUDE #23）：`pip install peft trl bitsandbytes` → 驗 4-bit 載入 smoke（GTX 1650 4GB）→ 才進訓練；`llama.cpp` 仍未裝且**絕不可跑其 requirements.txt**（會拖壞 venv，見 [[gb10-unavailable]]）。相關：[[guard-mechanisms-that-silently-fail]]（記憶亦會靜默過期）。
