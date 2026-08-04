# FinMind AI Agent Skill 要點對照 [I]（2026-08-04）

> **性質**：[I] 讀文件／對照筆記（CLAUDE.md #16）；**不**改限速、**不**放量、**不**改 `finmind.py`  
> **觸發**：用戶給 SPA `https://finmindtrade.com/analysis/#/data/ai_agent_skill`（「此頁面有如何使用 FinMind 請參考」）  
> **本輪 API**：用戶已解凍（`audits/API-THAW-20260804.md`）；本任務仍以讀文件為主，**未**為對照另開狂打 API  
> **Steward 裁（同日）**：A＝接官方 Skill → `.cursor/rules/finmind.mdc`（含 augur §0 硬閘）；B＝不掛 MCP；C 暫緩

---

## 1. 來源與取證方式

| URL | 角色 | 取證結果 |
|---|---|---|
| `https://finmindtrade.com/analysis/#/data/ai_agent_skill` | 用戶給的 SPA 入口 | WebFetch 僅得 JS 殼（ArchitectUI「無 JS 無法用」）；瀏覽器 MCP 本輪無法建 tab → **未在 SPA 本體抽取** |
| `https://finmind.github.io/tutor/ai/AgentSkill/` | 官方同題中文文件（SPA 導航「AI Agent Skill」之靜態對應） | ✅ 全文抽出 |
| `https://finmind.github.io/en/tutor/ai/AgentSkill/` | 英文對照 | ✅ |
| `https://raw.githubusercontent.com/FinMind/FinMind/master/.claude/commands/finmind.md` | Cursor／Claude Code skill 本體 | ✅（官方安裝指令指向此檔） |
| `https://finmind.github.io/llms.txt` | API／SDK／限速濃縮索引 | ✅ |
| `https://pypi.org/project/finmind-mcp/`（v0.0.7） | 官方 MCP | ✅ |

**判讀**：SPA 與 github docs／skill 檔為同一產品線內容；下列摘要以 skill 頁＋skill 檔＋`llms.txt` 為準，並標 URL。

---

## 2. 頁面摘要：如何使用 FinMind（要點）

### 2.1 三條連接路徑（官方分流）

1. **llms.txt**（網頁 ChatGPT／Claude）：貼連結讓 AI 懂 API／dataset，**不**直接代打 API。  
   - `https://finmind.github.io/llms.txt`／`llms-full.txt`
2. **Agent Skill**（Claude Code／Codex／Cursor／Windsurf／Gemini）：下載 skill，用 `/finmind …` 或規則檔驅動，**實際抓資料**。  
   - 文件：`https://finmind.github.io/tutor/ai/AgentSkill/`  
   - Cursor 安裝例：`mkdir -p .cursor/rules && curl -o .cursor/rules/finmind.mdc <skill raw URL>`
3. **MCP Server `finmind-mcp`**：MCP host 自動呼叫，自然語言即可。  
   - Cursor／Desktop 等：`uvx finmind-mcp`＋`env.FINMIND_TOKEN`  
   - PyPI：`https://pypi.org/project/finmind-mcp/`

### 2.2 Auth

- 註冊＋驗證信箱 → Token（帳號頁：`https://finmindtrade.com/analysis/#/account/user`）。
- 環境變數：`FINMIND_TOKEN`（skill／MCP 共用）。
- 請求慣例（skill／`llms.txt`）：`Authorization: Bearer {token}`；傳統 query 亦可帶 `token=`（Quick Start／既有腳本仍常見）。
- 額度表：`GET https://api.web.finmindtrade.com/v2/user_info`（Bearer）→ `user_count`／`api_request_limit`；超額常回 **HTTP 402**。

### 2.3 Endpoint

| 用途 | 路徑 |
|---|---|
| 主資料 | `GET https://api.finmindtrade.com/api/v4/data`（`dataset`／`data_id`／`start_date`／`end_date`） |
| data_id 清單 | `/v4/datalist` |
| 欄位中英對照 | `/v4/translation` |
| 專屬（勿硬塞 `/data`，否則 422） | 分點／權證報導、tick snapshot、期選 snapshot 等（skill 表列） |
| Sponsor Pro 整日 parquet | `/v4/storage_objects?dataset=&date=`（免 `data_id`） |
| 登入／換 token | `/login`、帳號頁自助換票（舊票即失效） |

### 2.4 限速（官方文件面）

| 來源 | 數字／行為 |
|---|---|
| `llms.txt`（簡） | 有 token **600／hr**；無 token 300／hr |
| skill 檔（分級） | Free 600 · Backer 1,600 · Sponsor **6,000** · SponsorPro 20,000／hr |
| 超額 | HTTP **402**（msg 含 upper limit）；讀錶不自計 usage |

官方**未**在 skill 頁教「IP sustained throttle／禁止重試風暴」——那是操作層經驗值。

### 2.5 SDK 與最佳實務（官方）

- Python SDK：`from FinMind.data import DataLoader` → `login_by_token` → `taiwan_stock_daily(...)`；批次可用 `stock_id_list`＋`use_async=True`。
- skill 建議：`requests`＋`pandas` 標準樣板；錯誤先辨 402／`status!=200`／空 data／缺 token。
- 意圖→dataset 對照表（股價／籌碼／財報／期選／總經）；複雜題多步 query。
- 圖表標題／軸標預設繁中；裝 CJK 字型。
- 裝套件偏好 `uv`。

### 2.6 本頁「五點」濃縮（給 Steward 一眼）

1. **Token＝`FINMIND_TOKEN`**，Bearer（或 query `token`）通 API／讀錶。  
2. **主入口 `/api/v4/data`**；重資料走專屬 path 或 `storage_objects`。  
3. **額度看 `/v2/user_info`**；階梯上限 skill 寫到 Sponsor 6k／Pro 20k。  
4. **AI 三路**：llms.txt（懂）／skill（編輯器代抓）／`finmind-mcp`（MCP 代抓）。  
5. **SDK 或 requests 均可**；官方鼓勵 async 批次、意圖對表、402 優雅處理。

---

## 3. 與 augur 對照

對照物：`src/augur/ingestion/finmind.py`、日維／#24／#25、今日解凍後補抓（`audits/API-CATCHUP-20260804.md`）。

### 3.1 已對齊（不必為「對齊官方」而改）

| 官方概念 | augur 現況 |
|---|---|
| v4 `/data` + token | `API_URL`＋`config.FINMIND_TOKEN`（query `token=`） |
| `/datalist`・`/translation` | 同檔公開入口；422 enum 動態列 dataset（#3） |
| 專屬 endpoint | `fetch_dedicated`；sync 路由 `dedicated` |
| 讀額度錶 `user_info` | `_user_quota`；Bearer（與官方一致） |
| 額度／重試意識 | `_quota_gate`＋`_pace`＋`_RETRY_STATUS`（402／429／403／5xx）；403 固定 `QUOTA_COOLDOWN=1800`（#24） |
| #25 最小單位 | 探測／健康檢查文化已入 CLAUDE／日維／selfheal |
| 日頻增量 | `daily_maintenance`；解凍後 catch-up 已冪等補到 `--end 2026-08-03`（有界 datasets；禁 Dividend／`--with-dim-sync`） |
| 取數與預測正交 | 預測熱路徑不依賴 live FinMind（predict-vs-market-api） |

**一句**：augur 的 production ingestion **比官方 skill 更深**（IP sustained、主動閘、見 403 長冷卻）——skill 是「怎麼問 API」；augur 是「怎麼在 Sponsor 額度下活過長跑」。

### 3.2 差距／可改進（**只建議**；大改需計畫＋拍板）

| 項 | 官方／skill | augur | 建議等級 |
|---|---|---|---|
| Auth header | 強調 Bearer | `/data` 等仍 **query `token=`**；僅 user_info 用 Bearer | **低**：註解聲明雙軌皆合法即可；改 header 屬相容回歸，須計畫＋最小探測 |
| 限速敘事 | 文件寫 600（簡）／階梯至 6k–20k | 實戰按 Sponsor ~6k＋`MIN_INTERVAL=0.9`＋HEADROOM | **低**：模組 docstring 加一行「官方階梯 vs 本機操作值」；**勿**自動改 `MIN_INTERVAL` |
| SDK `DataLoader`／`use_async` | 官方推薦 | 自研 `requests` client（clean-room／單一收口 `_protected_get`） | **不建議換 SDK**；async 若採會繞過 `_pace` 單一 start-rate → 高風險，須計畫 |
| `storage_objects`／Sponsor Pro | skill 明文 | 本 client **未**實作 | **中／另案**：僅當真要整日 tick／KBar 時再開計畫 |
| Agent Skill／MCP | Cursor 一 curl／`uvx finmind-mcp` | `.cursor/mcp.json` **無** finmind；**無** `.cursor/rules/finmind.mdc` | **決策項**（見 §5）：探索友善 vs 誤放量風險 |
| 補抓佇列仍缺口 | — | `TotalReturnIndex` 等需 `--with-dim-sync`；Dividend rebuild 另授；08-04 當日未納 | **操作**：維持 CATCHUP 另帳；非本筆記範圍 |

### 3.3 與剛解凍補抓的交叉（FZ 誠實）

- 解凍＝`API-THAW-20260804.md`（INV1∧INV2）。  
- 補抓＝`API-CATCHUP-20260804.md`：日維有界成功、**無** 403；仍禁放量／Dividend／dim-sync。  
- 官方 skill／MCP 若在 Cursor 直接開通，**可能繞過** augur `_pace`／`_quota_gate` 另開請求 → 與 #24 精神衝突；接 skill 須另訂「探索 path ≠ ingestion path」護欄。

---

## 4. 可選下一步（不自動執行）

1. **只寫註解**：`finmind.py` 標頭補「官方三路／Bearer 雙軌／階梯額度參考 URL」——機械小改，仍建議口頭 yes。  
2. **Cursor rule skill**：下載 `finmind.mdc` 進 `.cursor/rules/`——方便 ad-hoc 查詢；須明示「禁止與 sync 並跑、見 403 停」。  
3. **MCP `finmind-mcp`**：寫入 MCP 設定——與現有 constitution／local-llm／memory 並列；同樣額度護欄，大改須計畫。  
4. **Bearer 遷移／SDK／storage_objects／改 `MIN_INTERVAL`**：一律 **plan-first**，本報告不授權。

---

## 5. AskQuestion（Steward 裁・部分關閉）

- **A**：是否把官方 Agent Skill 接到 Cursor（`.cursor/rules/finmind.mdc`）？→ **yes**（已落地，含解凍／ingestion 收口／403 停）
- **B**：是否裝／掛 `finmind-mcp`？→ **本輪否**；仍開放 Steward 覆裁
- **C**：是否只改 `ingestion/finmind.py` 註解對齊官方文件面（不改行為）？→ **暫緩**
- **D**：以上皆暫緩？→ 不適用（A 已執行）

建議預設（self-reported）：ingestion 生產路徑維持現狀；MCP 若日後要掛，另開計畫＋同樣旁路禁令。

---

*寫於 2026-08-04。位階 [I]。Skill 接線同日 commit。*
