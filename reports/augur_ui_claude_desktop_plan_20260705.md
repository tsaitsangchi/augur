# augur 前後台介面 Claude Desktop 化 — 完美計劃報告

🎯 **白話**：把 augur 的**前台（誠實博學的我 · 對話 app）**與**後台（知識控制台 · admin）**改成**儘可能一模一樣的 Claude Desktop app 介面**——同一套暖色設計系統、同款功能鈕、chat/cowork/code 三情境、各可開 new session、看得到 running 狀態、背景工作、`.md` 文件內容。本報告＝**實作前的完整設計計劃**（憲章 v1.31.0「計畫先行」首例），供決策層拍板後分階段落地。
守 #5（上傳/路徑/XSS 防護）· #1（顧問誠實鏈不被 UI 繞過）· #18（命名）· #28（本地零 usage）· 憲章 v1.31.0（計畫先行、計畫完整性）· v1.30.0（顧問呈現層）· v1.29.0（RBAC）。日期：2026-07-05。

> **範圍界定（誠實）**：本計劃是**介面層**（HTML/CSS/JS + 薄後端端點）。**不新增預測/知識演算法、不改 RBAC enforcement、不繞 guard**。cowork/code 兩情境之**專屬後端 agent 尚不存在**——本計劃明列其為「UI 就緒、後端待建」，不佯裝已具備（見 §7 誠實缺口）。

---

## 0. 為何要這份計劃（目標與非目標）

**目標**：兩台 app **視覺與互動儘可能等同 Claude Desktop**——(a) 暖色設計系統一致；(b) 左側欄 + 情境切換 + New session + 底部帳號/狀態；(c) running 狀態、背景工作、`.md` 檢視三種可觀測性；(d) chat/cowork/code 三情境各可開 session。
**非目標**：不做多使用者雲端、不做對話歷史永久雲儲存（本機單機為主）、不改顧問誠實機制、不建 cowork/code 的真實 agent 後端（本計劃只出 UI 殼 + 標示待建）。

---

## 1. 設計系統（Design System，兩台共用 SSOT）

**單一調色盤（暖色 Claude 風，light 主題）**：

| Token | 值 | 用途 |
|---|---|---|
| `--bg` | `#faf9f5` | 主背景（暖米白） |
| `--sidebar` | `#f0eee6` | 側欄背景（暖米灰） |
| `--surface` | `#ffffff` | 卡片／輸入盒／作用中項 |
| `--bubble` | `#f0eee6` | 使用者訊息氣泡 |
| `--text` | `#1f1e1d` | 主文字 |
| `--muted` | `#73726c` | 次要文字 |
| `--border` | `#e9e6dc` | 細分隔線 |
| `--border-strong` | `#dcd8cc` | 輸入框/強調邊 |
| `--accent` | `#d97757` | **Claude 珊瑚**：主按鈕、送出、連結、星標、作用中 |
| `--accent-hover` | `#c15f3f` | 珊瑚 hover |
| `--accent-soft` | `#f5e5dd` | 珊瑚淡底（avatar、chip、note） |
| `--hover` | `#e7e4d8` | 側欄項 hover |
| 狀態綠 | `#5f8a5a` | 健康燈 on／完成徽章 |
| 狀態紅 | `#c15f3f` | 健康燈 off |

**字體**：介面 `ui-sans-serif, -apple-system, "Segoe UI", "Noto Sans TC", sans-serif`；問候語 serif `Georgia, "Noto Serif TC", serif`（呼應 Claude「serif 是 Claude 的聲音」）；碼 `ui-mono`。
**字級**：h1 問候 29px / 標題 20–22px / 內文 15px / 說明 12–13px。兩級字重（400/600）。**圓角**：卡片 12–14px、輸入盒 24px、控制項 8–10px、頭像 7–8px、徽章 20px（pill）。**陰影**：極淡（`0 1–2px…rgba(0,0,0,.05)`），無漸層無發光。
**共用元件**：星標 `✻`（珊瑚）、圓形 `＋`（附加/新增）、圓形珊瑚 `↑`（送出）、pill 徽章（狀態）、健康燈（8px 圓點）、side-nav 項（作用中＝白底+陰影+粗體）。

> **落地形式**：`:root{--…}` CSS 變數（單一 SSOT）；兩台各自 inline `<style>`（stdlib server、無打包）。**若日後抽為共用 `ui_theme.py` 常數字串則兩台 import**（#12；目前各持一份、以本表為對齊 SSOT）。

---

## 2. 前台（誠實博學的我 · 對話 app）

### 2.1 版面（Claude Desktop 三區）
```
┌─ sidebar(260px) ─┬──────────── main ────────────┐
│ ✻ augur          │                               │
│ [＋ 新對話]       │      ✻                        │
│ ─ 情境 ─          │   今天想聊什麼?  (serif)       │
│ · 對話 (active)   │   問我投資哲學…                 │
│ · 協作            │                               │
│ · 程式            │   [使用者氣泡 ›右]            │
│                   │   ✻ 顧問回覆(白話解讀)         │
│ (spacer)          │                               │
│ ● PostgreSQL      │ ┌ composer(圓角) ───────────┐ │
│ ● 顧問殼          │ │ ＋  輸入訊息…          ↑  │ │
│ ● Ollama          │ └───────────────────────────┘ │
│ 知識控制台 ↗      │  本地 qwen3:8b · 逐字引文閘   │
│ 登出              │                               │
└───────────────────┴───────────────────────────────┘
```

### 2.2 三情境（chat / cowork / code）
| 情境 | 問候語 | 後端 | 狀態 |
|---|---|---|---|
| **對話** | 今天想聊什麼? | advisor（投資哲學顧問，已運作） | ✅ 完整 |
| **協作** | 一起完成什麼任務? | 暫共用 advisor（專屬協作 agent 待建） | 🟡 UI 就緒、後端待建 |
| **程式** | 要處理哪段程式? | 暫共用 advisor（專屬 code agent 待建） | 🟡 UI 就緒、後端待建 |

- **切換**：側欄點情境 → `setMode(m)` 換問候語 + 作用中樣式 + **開新 session**（清空對話）。情境以 `MODE` 前端狀態承載；`/chat` payload 可帶 `augur_mode`（目前後端忽略、未來分派用）。
- **New session**：`＋ 新對話` → `newSession()`：清 log 回該情境問候、解除附加檔、重置輸入。**每情境獨立可開**。
- 協作/程式頂端顯示 `modenote`（珊瑚淡底）：「此情境沿用顧問後端，專屬 agent 建置中」（#誠實，不佯裝）。

### 2.3 訊息與輸入
- 使用者訊息＝右對齊暖灰氣泡；顧問訊息＝全寬、左側珊瑚 `✻` 頭像、白話解讀（**引經據典逐字區塊不顯示**，憲章 v1.30.0；Mode B 附加檔區塊保留）。
- Composer：圓角卡片、左 `＋`（附加）、中 textarea（自動長高 ≤180px）、右珊瑚 `↑`；**Enter 送出、Shift+Enter 換行**；送出中 `↑` 轉灰。
- `＋` 選單：A 入知識庫（license 白名單、local_private owner=登入者）／B 只問這次（不入庫）。承既有 Mode A/B。

### 2.4 running 狀態
- 側欄底部三顆健康燈（PostgreSQL／顧問殼 :8399／Ollama :11434），`GET /health` 每 15 秒輪詢，綠=可達紅=不可達。

### 2.5 端點（前台後端，薄 proxy）
| 端點 | 方法 | 作用 | 狀態 |
|---|---|---|---|
| `/` | GET | 登入頁 or 主頁（RBAC gate） | ✅ |
| `/login` `/logout` | POST/GET | identity session | ✅ |
| `/chat` | POST | proxy → advisor 殼（帶 X-Augur-Session/Internal） | ✅ |
| `/ingest` `/attach` | POST | Mode A 入庫／Mode B 附檔 | ✅ |
| `/health` | GET | DB/advisor/ollama 可達性 | ✅ |

---

## 3. 後台（知識控制台 · admin）

### 3.1 版面（同設計系統的 sidebar dashboard）
左側欄：`✻ augur 控制台` + nav（**總覽 / 背景工作 / 文件** ─ 主題抓取 / 本機匯入 / 遠端 SFTP ─ 誠實博學的我↗ / 登出）；右側 section 切換（`.sec.active`）。

### 3.2 各區
| 區 | 內容 | 狀態 |
|---|---|---|
| **總覽** | 服務 running 狀態（DB/顧問/Ollama 健康燈）＋ 知識層數字（item/本機檔/staging） | ✅ |
| **背景工作** | 掃 `harvest_*.log` 列表 + **● 執行中／✓ 完成** pill + 行數 + 「檢視 ↗」進度頁 | ✅ |
| **文件** | `reports/`＋`docs/` 之 `.md` 清單（左）＋ **伺服器端渲染**內容（右：標題/表格/碼區塊/清單/引言） | ✅ |
| 主題抓取 | 觸發 harvest（確認頁/放量背景+即時進度頁） | ✅ 既有 |
| 本機匯入 | 原生上傳選檔/夾入庫（webupload→acquire_local_files） | ✅ 既有 |
| 遠端 SFTP | 金鑰連線瀏覽入庫 | ✅ 既有 |

### 3.3 端點（後台）
| 端點 | 作用 | 狀態 |
|---|---|---|
| `/api/health` | DB/advisor/ollama 健康 | ✅ |
| `/api/jobs` | `harvest_*.log` 清單+狀態 | ✅ |
| `/api/docs` | `reports/`＋`docs/` .md 清單 | ✅ |
| `/api/doc?path=` | 守衛讀 .md → `_md_to_html` 渲染 HTML | ✅ |
| `/api/status` `/api/browse` `/api/topic/log` `/api/sftp/*` | 既有 | ✅ |

**安全（#5）**：`.md` 檢視 `_read_doc` realpath 圍欄（僅 `reports/`＋`docs/`、副檔 `.md`、拒 traversal）；`_md_to_html` 先 `html.escape` 全文再結構化（防 XSS）；job log `_safe_log` 圍欄（僅 `harvest_<hex>.log`）。

---

## 4. 對應檔案（元件 → 檔·函式）

| 元件 | 檔 | 關鍵函式/常數 |
|---|---|---|
| 前台 shell + 三情境 + 健康 | `scripts/serve_chat_ui.py` | `PAGE`（CSS/HTML/JS）·`LOGIN_PAGE`·`H._health`·`H.do_GET/do_POST` |
| 前台入庫擁有者接線 | `scripts/acquire_local_files.py` | `--owner-user-id` |
| 後台 shell + 三區 + 渲染 | `scripts/serve_admin_console.py` | `ADMIN_CSS`·`dashboard_html`·`NAV_SCRIPT`·`_list_jobs`·`_list_docs`·`_read_doc`·`_md_to_html`·`_health` |
| 顧問呈現（引文隱藏） | `src/augur/advisor/oai_compat.py` | `_reply_text` |
| 設計系統 SSOT | 本報告 §1（未抽共用檔；抽則 `src/augur/…/ui_theme.py`） | — |

---

## 5. 分階段（Phase）與現況

- **Phase 0 — 已實作（2026-07-05 本 session，先做後補計畫；本報告即為之補立 SSOT 並定義後續）**：兩台換 Claude 暖色設計系統 + 功能鈕；前台 sidebar/三情境/new session/composer(Enter 送出)/健康燈；後台 總覽健康 + 背景工作 + 文件(md 渲染)。**已起 server + admin/admin 登入實測（HTTP 200、三情境、/health 全綠、/api/docs 90 檔、/api/doc 渲染含表格）、134 測試通過。**
- **Phase 1 — Claude 保真度精修（拍板後部分已落地 2026-07-05）**：✅ 前台**深色模式**（`prefers-color-scheme` 對偶調色盤、CSS 變數 + 修字面色）、✅ 兩台**過場 + focus-visible ring**。🟡 **後台深色模式暫緩**（後台 inline 字面色多、需先 inline→CSS 變數重構才不半套；列 Phase 1 追蹤，避免半套深色）。待拍板：字體微調、空狀態插圖、行動 responsive（側欄收合）、Esc 關選單。
- **Phase 2 — 會話歷史（✅ 已落地 2026-07-05，localStorage 版）**：前台側欄 **recents 近期列表**（每情境獨立、自動標題＝首則、點選重載、新對話開新 session、localStorage 存最近 100 則）。DB 兩表版（跨裝置/可搜，§6 schema 已備）待拍板再升。待補：重新命名/刪除 session。
- **Phase 3 — cowork/code 真實後端（待拍板、跨越介面層）**：協作/程式專屬 agent 之後端（非本計劃介面範圍、屬另立計劃；在此標記依賴）。
- **Phase 4 — 觀測性增強（待拍板）**：背景工作即時 tail（SSE）、工作可停止（terminate）、`.md` 全文搜尋、文件樹（子目錄）。

---

## 6. 若 Phase 2 對話歷史入 DB（計畫完整性預留 schema）

> 僅在拍板「歷史入 PostgreSQL」時建；否則走 localStorage（零 schema）。此處預附以符憲章「計畫完整性」。

```sql
CREATE TABLE IF NOT EXISTS chat_session (
  session_id  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     bigint NOT NULL REFERENCES app_user,
  mode        varchar(16) NOT NULL DEFAULT 'chat',   -- chat|cowork|code
  title       text,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS chat_message (
  message_id  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  session_id  bigint NOT NULL REFERENCES chat_session ON DELETE CASCADE,
  role        varchar(12) NOT NULL,                   -- user|assistant
  content     text NOT NULL,
  guard_pass  boolean,
  created_at  timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS ix_chat_message_session ON chat_message(session_id, message_id);
```
對應 Python：遷移 `scripts/migrate_chat_history_ddl.py`（冪等 guard）；讀寫 `src/augur/advisor/chat_history.py`（`create_session`/`append_message`/`list_sessions`/`load_messages`，**只讀寫這兩表、隔離不變式不觸預測/知識表**）；前台 `serve_chat_ui.py` 新增 `/api/sessions` `/api/session/<id>` 端點。**RBAC**：session 綁 `user_id`、他人不可讀（承 v1.29.0 owner 收窄精神）。

---

## 7. 誠實缺口（三敵/#15，明列不含糊）

1. **cowork/code 無專屬後端**：目前三情境共用投資顧問 advisor；協作/程式問到非投資主題時，顧問會依 guard 誠實回「知識庫中無此內容」而非佯裝會做。UI 已標註「後端建置中」。**不得**為「看起來完整」而讓 cowork/code 假裝有專屬能力。
2. **對話歷史未持久化**：目前 new session＝前端清空、重整頁即失（無 recents）。Phase 2 才落地。
3. **健康燈為可達性、非深度健康**：`/health` 只探端口可達（advisor `/v1/models`、ollama `/api/tags`、DB `SELECT 1`），不驗模型能否推理。
4. **深色模式/行動版未做**：目前固定 light 暖色、桌面寬度為主。

---

## 8. 驗收準則（Definition of Done，每階段）

- **視覺**：與 Claude Desktop 並排，配色/圓角/字體/功能鈕位置「一眼認得是同一風格」；珊瑚僅用於主動作與品牌（不濫用）。
- **功能**：三情境可切、各可開 new session；`/health` 三燈正確反映服務起停；背景工作列表隨 harvest 更新、可開進度；`.md` 點選即渲染（含表格/碼/清單）。
- **安全**：`.md`/job log 路徑圍欄 + XSS escape 通過；RBAC/guard 不被 UI 繞過（顧問仍經 advise+guard 單閘）。
- **回歸**：`pytest` 全綠、隔離 AST 稽核過、兩台 `python -m py_compile` + 起 server 冒煙 200。

---

## 9. 待你拍板（決策層）

1. **Phase 1 保真精修**要做到哪（深色模式？行動版？插圖空狀態？）——預設：先補 hover/focus/過場 + 深色模式對偶。
2. **對話歷史**：localStorage（輕、零 schema）還是 DB 兩表（跨裝置、可搜）？——預設：先 localStorage，需求明確再入 DB（§6 已備 schema）。
3. **cowork/code 後端**：是否要另立計劃建真實 agent（Phase 3，跨介面層）？——預設：先維持 UI 殼 + 誠實標註。
4. **設計系統抽共用檔**：兩台各持一份 CSS vs 抽 `ui_theme.py` 單一 SSOT？——預設：先各持、以本報告 §1 為對齊 SSOT；漂移風險升高再抽。

> 拍板後我依選定階段實作（依憲章 v1.31.0：計畫已立、實作照此逐步落地、逐檔呈過目）。**Phase 0 已完成並實測**；其餘待你選。
