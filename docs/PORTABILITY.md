# augur-code 可攜性與換機器 Checklist

> 目的：把 Augur 部署到**另一台硬體不同的機器**時，需要調整什麼、不需要調整什麼。
> 立於 2026-07-19，依 `src/`（318 .py）＋ shell 腳本之硬編碼掃描結果。

## 設計原則：機器事實隔離在 env / DB config / 探測，核心碼中立

掃描結論：**核心 Python 無硬編碼絕對路徑、無硬編碼硬體型號**；機器特定性走三條隔離縫——
1. **`.env`**（環境變數）：DB 連線、服務端點。
2. **DB 內 config**（`engine_config`）：併發數、模型層級等調校值。
3. **開機探測**：硬體(GPU/VRAM)由 `refresh_knowledge_pipeline.py` 自動偵測落帳，**不假設**。

換機器＝設好上述三者，核心 Python **一行不用改**。

---

## ✅ 不用改（可攜）

| 面向 | 為何可攜 | 證據 |
|---|---|---|
| 憲章規格 L0–L7 | 技術中立（L7.4 刪名測試） | `augur-constitution/specs/*` |
| 核心 Python (`src/augur/`) | 零硬編碼絕對路徑 | 掃描 `src/` 命中 0 |
| DB 連線 | 全走 env + 預設 | `src/augur/core/config.py:42-46` |
| GPU/VRAM | **偵測**非假設，落 `orch/hw_vram_mb` | `scripts/refresh_knowledge_pipeline.py:106-118` |
| 模型選擇 | env 覆蓋，不寫死 | `src/augur/advisor/ollama.py:25,78` |
| 併發/單飛鎖 | 讀 DB config（`frontend_tiers`） | `src/augur/advisor/effort.py:39-45` |
| 上傳路徑 | `expanduser("~")/.augur_uploads` | `src/augur/knowledge/webupload.py:18` |
| nvidia-smi 探測 | 先 PATH、再 WSL fallback | `scripts/refresh_knowledge_pipeline.py:108` |

---

## 🔧 換機器要設定的（三條縫）

### 1. `.env`（環境變數）

```bash
# DB（psycopg2）——預設 localhost/5432/augur/augur
DB_HOST=localhost
DB_PORT=5432
DB_NAME=augur
DB_USER=augur
DB_PASSWORD=<新機器之密碼>

# Ollama LLM 端點與模型——預設 localhost:11434 / qwen3:8b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=<依新機器 GPU 選型，見下>
```
> 對應：`core/config.py:42-46`、`advisor/ollama.py:24-25`。

### 2. DB 內調校 config（依硬體重設）

| config | 現機值(4GB GPU) | 換機器時 | 位置 |
|---|---|---|---|
| `frontend_tiers.max_concurrent`（單飛鎖） | 1（4GB 現實：同時 1 場審議） | GPU 更大可調高 | `advisor/effort.py:8,42` |
| 模型層級/選型 | `qwen3:8b`（4GB 需部分 CPU offload） | 更強 GPU 換更大模型；無 GPU 走 CPU/雲端 | `advisor/ollama.py:8,25` |

> 這些**改設定、不改碼**。`effort.py` 走 `engine_config.load_rules(fresh=True)`——翻旗標免重啟。

### 3. 硬體探測（自動，確認即可）

換機器後跑一次 `refresh_knowledge_pipeline.py`，它會偵測 GPU 有無/VRAM 並落 `orch/hw_vram_mb`（CPU-only 誠實記 0）。**不需手設**，但要確認落帳值符合新機器。

---

## ⚠️ 硬編碼摩擦點（換機器要手動處理的 2 處）

1. **`import_database.sh:51`**：DB dump 搜尋路徑含 WSL 專屬 `/mnt/d/database`、`/mnt/c/AI`（另有可攜的 `$HOME/db_dumps`）。
   - **非 WSL 機器**：`/mnt/*` 不存在但**不會崩**（`$HOME/db_dumps` 那條仍命中）。
   - **建議**：把 `/mnt/*` 改為環境變數 `AUGUR_DUMP_DIRS`，徹底去 WSL 依賴。
2. **`serve_admin_console.py`**：頁內瀏覽 `/mnt/c`（Windows 磁碟）是 WSL 專屬 UI 功能。換原生 Linux 就沒 Windows 碟可瀏覽——功能降級，非崩潰。

其餘 `localhost:11434`(ollama)、`127.0.0.1:6333`(qdrant, `knowledge/vectorindex.py:340`) 皆 env/`--url` 可覆蓋，非硬摩擦。

---

## 換機器施工順序

```
1. 複製 repo（憲章 + augur-code），零改動
2. 建 venv、pip install（pyproject.toml）
3. 寫 .env（DB + Ollama 端點/模型）
4. 還原 DB dump（import_database.sh；注意 /mnt 路徑或用 $HOME/db_dumps）
5. 起服務（Ollama、Qdrant）於新機器
6. 跑 refresh_knowledge_pipeline.py → 確認 orch/hw_vram_mb 偵測正確
7. 依新硬體重設 DB config：frontend_tiers.max_concurrent、模型選型
8. 驗證：core_gate/advisor 短連線通、審議引擎跑通一輪
```

## 驗證（換機器後確認可攜性成立）

- `python -c "from augur.core.config import DB_PARAMS; print(DB_PARAMS)"` → 顯示新機器 env 值
- `python scripts/refresh_knowledge_pipeline.py` → GPU/VRAM 偵測落帳正確
- 審議引擎跑一輪（單飛鎖不卡、模型回應）
- gate/selftest（憲章側）於新機器 PASS

---

## 一句話

**憲章可攜 ✓、核心碼可攜 ✓（env/config/探測）。** 換機器＝設 `.env`＋重設 DB 調校 config＋處理 `import_database.sh` 的 `/mnt` 路徑，核心 Python 不動。唯一要盯的硬編碼是那 2 處 WSL 路徑（一處降級不崩、一處是 Windows 碟 UI 功能）。
