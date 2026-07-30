---
name: augur-tech-baseline-20260730
description: 2026-07-30 親驗技術底座:294 表/8.54M feature_values/18 package/63 migrate DDL/11 systemd unit/ollama 三模型/套件實況——取代舊地圖之過期數字
metadata: 
  node_type: memory
  type: project
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-30T04:03:52.895Z
---

**全部本日 `psql`／`pip list`／ollama API／`ls` 親驗**（不是記憶）：

- **DB**：`augur` 庫 **294 張 public 表**；角色僅二：`augur`（應用）／`augur_predict`（隔離讀）。DDL SSOT＝`scripts/migrate_*.py` **63 支**。
- **規模**：`feature_values` **8,540,331**／`knowledge_item` **270,736**／`knowledge_sentence` **1,811,477**／`governance_proposal` 3／`trial_ledger` 32／`principle_domain_map` 8。
- **程式**：`src/augur/` **16 package**——advisor・arena・audit・catalog・core・deliberation・evaluation・evolution・execution・features・identity・ingestion・knowledge・models・philosophy・universe（舊記憶寫「15 package／193 scripts」已過期；`scripts/` 受指令矩陣稽核者 **425 支**）。⚠ 數 package 要 `ls -d src/augur/*/ | grep -v __pycache__`——直接 `ls` 會把 `__init__.py` 與 `__pycache__` 算進去（我 2026-07-30 即因此誤記 18）。
- **本機模型（ollama `localhost:11434`）**：`qwen3:8b`（教師／oracle）・`qwen3:4b`（顧問引擎／受評）・`nomic-embed-text`（嵌入）。
- **套件**：torch 2.4.1・transformers 5.12.1・accelerate 1.14.0・datasets 2.17.1・sentence-transformers 5.6.0・lightgbm 4.6.0・xgboost 3.3.0・scikit-learn 1.9.0・statsmodels 0.14.6・**arch 8.0.0**（GARCH-FHS）・scipy 1.18.0・pandas 3.0.5・numpy 2.4.6。**無 peft／trl／bitsandbytes／gguf／dspy**（見 [[venv-finetune-stack-absent]]）。
- **服務（user-level systemd，`~/.config/systemd/user/`，非 `/etc`）**：11 unit＋5 timer——`augur-{chat,advisor,admin,probability,qdrant,ollama}.service`（ollama 另有 `max-loaded.conf` drop-in）＋`augur-{admission-assist,ata-advance,audit-watchdog,embed-catchup,l2-deliberation}.service` 各配 `.timer`。

**Why**：舊 [[augur-project-map]] 之數字（15 package／193 scripts／原則精華 v1.9.1／憲章 v1.46.0）已被多層補丁疊成矛盾文本；在錯的底座上規劃會排出跑不動的行程（例：以為 peft 已裝而排 LoRA 訓練）。

**How to apply**：`systemctl --user`（**不是** `sudo systemctl`）操作服務；改 `serve_*.py`／`src` 後必 restart 對應 unit（`http.server` 啟動載入不熱更新，見 [[restart-systemd-after-edit]]）。查表名前先 `information_schema` 實查、勿憑印象（本日即因憑印象猜 `prodset_state`／`arena_bet`／`meta_replay_run` 三個表名全錯，真名見 [[augur-path-six-parallel-gap]]）。治權現行版：靈魂 v1.8.0・**原則精華 v1.11.0**・大憲章 v1.49.0・CLAUDE.md v1.31・AUGUR-MC v1.6。
