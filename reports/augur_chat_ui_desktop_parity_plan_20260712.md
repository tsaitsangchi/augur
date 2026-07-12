# 前台 Claude-Desktop 級改造計畫(草案・待拍板)

> **性質**:計畫先行文件(憲章第六部 v1.39.0)。用戶指示(2026-07-12):「本地 AI 前台改成像 Claude
> Desktop——模型選擇、user settings,功能介面 UI 都一樣」。本計畫盤點現有資產後給出**誠實對照表**
> (哪些做得到同款、哪些是 Claude 專屬不復刻)+ schema/程式規畫/分階段。

## §0 三十秒+誠實邊界

**好消息**:後端資產已有七成——登入/RBAC、對話持久化(`chat_session` 10 列+`chat_message` 含
guard_pass 欄)、歷史 API(`/api/sessions`/`/api/messages`,owner 收窄)、附件(`/attach`)、
串流回覆、F1 檔位選單(`/api/tiers`,6 檔位 live)。**缺的是「殼」**:側欄、設定面板、渲染與操作、
主題——純前端工程+一張新表。

**誠實邊界(拍板前先講死)**:
1. 「模型選擇像 Fable 5/Opus 4.8」=**同款 UI 體驗**(下拉選單+模型名+描述+速度標);模型本體
   永遠是本地 qwen 家族(憲章 v1.37.0 advisor 本機限定)——選單會像,選項不會是 Claude;
2. Claude 專屬功能**不復刻**:Artifacts、Projects、MCP connectors、網頁瀏覽、Claude 帳號體系
   (§2 對照表逐項標明);
3. **誠實層零退化(紅線)**:guard footer、方向拒答句、ultra 審議裁決區塊、「review 級」字樣在新 UI
   一律顯著呈現,不得摺疊隱藏(棘輪:UI 改版只能加強誠實呈現)。

## §1 功能對照表(Claude Desktop → 本地;=驗收清單)

| Claude Desktop 功能 | 本地對映 | 判 |
|---|---|---|
| 側欄:對話清單/搜尋/新對話/改名/星標/刪除 | `chat_session` 已有 title/starred;補 UI+`/api/search`+rename/star/delete API(刪除=軟刪 archived 欄) | ✅ 做 |
| 模型選擇器(頂欄下拉+模型卡描述) | `/api/tiers` 升級呈現:qwen3-8b(深度)/4b(快速)× fast/think/ultracode,含 tok/s 與一句話描述 | ✅ 做 |
| User settings 面板(外觀/行為/帳號) | 新表 `user_settings`(§3);面板:主題 dark/light/system、字級、預設檔位、串流開關、Enter 送出行為 | ✅ 做 |
| Markdown+程式碼區塊(高亮/複製鈕) | 本地 vendor marked.js+highlight.js(**零 CDN**,static 目錄自帶;#28 本地) | ✅ 做 |
| 停止生成/重新生成/複製訊息 | stop=中斷 fetch stream;regenerate=末問重送;逐訊息複製鈕 | ✅ 做 |
| 附件上傳 | `/attach` 既有,接進輸入列(迴紋針鈕) | ✅ 接 |
| 鍵盤快捷鍵(⌘K 新對話/⌘/ 搜尋…) | 同款鍵位 | ✅ 做 |
| 暗/亮主題+響應式 | CSS 變數雙主題+行動版側欄摺疊 | ✅ 做 |
| Artifacts / Projects / MCP / 網頁瀏覽 / 語音 | Claude 專屬生態,本地無對應後端 | ❌ 不做(誠實列) |
| 帳號訂閱/用量頁 | 對映為:本地 tok/s 與審議引擎狀態小面板(誠實版「用量」) | 🔁 改造對映 |

## §2 UI 佈局規格(同款三欄式)

左側欄(可摺疊):新對話鈕/搜尋框/對話清單(星標置頂、相對時間、hover 操作選單)/底部用戶名+設定齒輪。
主區:頂欄=模型選擇器下拉(當前檔位名+▾)+對話標題;訊息流=Markdown 渲染、guard footer 樣式化
(pass=綠標、issue=黃標展開)、ultra 裁決區塊=等寬字卡片;輸入列=多行輸入+附件+送出/停止。
設定=齒輪彈出 modal(分頁:外觀/行為/關於——「關於」頁誠實陳列:本地模型清單、審議引擎 GATE 狀態、
方向軸十門判死聲明連結)。

## §3 Table Schema(v1.39.0 (a);DDL 住 `migrate_chat_ui_ddl.py`(新))

```sql
CREATE TABLE IF NOT EXISTS user_settings (
  user_id bigint PRIMARY KEY,          -- FK 對齊既有 RBAC 用戶表
  settings jsonb NOT NULL DEFAULT '{}',-- {theme, font_size, default_tier, stream, enter_to_send}
  updated_at timestamptz NOT NULL DEFAULT now());
ALTER TABLE chat_session ADD COLUMN IF NOT EXISTS archived boolean NOT NULL DEFAULT false;  -- 軟刪
```
所讀既有表:`chat_session`(+archived)、`chat_message`(不動)、`app_session`(auth 不動)、
`deliberation_engine_config`(tiers SSOT 不動)。

## §4 Python 程式規畫(v1.39.0 (b))

| 檔 | 職責 |
|---|---|
| `scripts/migrate_chat_ui_ddl.py`(新) | §3 DDL 冪等 |
| `scripts/serve_chat_ui.py`(改) | +API:`/api/search`(標題+內文 ILIKE,owner 收窄)、`/api/session/rename|star|archive`(POST)、`/api/settings`(GET/PUT,user_settings)、靜態資產路由 `/static/*`(僅白名單檔);既有 auth/串流/attach 不動 |
| `scripts/chat_static/`(新目錄) | `app.css`(雙主題 CSS 變數)、`app.js`(側欄/設定/渲染/快捷鍵)、`marked.min.js`+`highlight.min.js`+`github.css`(本地 vendor,一次性下載入 repo、版本註記) |
| 誠實層迴歸紅隊 | 新 UI 下實測:方向題拒答句全文顯示、guard footer 不被吞、ultra 裁決卡片完整、模擬頁連結可點 |

## §5 分階段・驗收・拍板點

| 階段 | 內容 | 驗收(#7 實測) |
|---|---|---|
| **U0** | 本計畫拍板 | — |
| **U1 殼** | 三欄佈局+側欄(清單/新對話/搜尋/改名/星標/軟刪)+DDL | 10 個既有 session 正確列出;owner 隔離實測(他人 session 不可見) |
| **U2 設定** | user_settings 表+面板(主題/字級/預設檔位/行為)+「關於」誠實頁 | 設定跨 session 持久;主題即時切換 |
| **U3 渲染與操作** | markdown/highlight(本地 vendor)+複製/停止/重生+快捷鍵 | 程式碼區塊高亮+複製;stop 真中斷 stream;⌘K 等鍵位 |
| **U4 模型選擇器+紅隊** | 檔位下拉 Claude 式呈現+誠實層迴歸全套 | §4 紅隊四項全過;guard 樣式化不減量 |

**拍板點**:①本計畫(現在);②本地 vendor 兩個 JS 庫入 repo(marked/highlight,MIT/BSD,一次性下載
——涉「引入外部前端依賴」故列拍板);③「關於」頁陳列內容過目。

**工程量誠實估計**:前端 ~600-900 行新碼(現 UI 內嵌 HTML 全重寫)+後端 ~150 行 API;U1-U4 約
2-3 個工作段;與解凍/擂台鏈**零衝突**(不碰資料層),可平行推進。

**時序建議**:擂台開賽(judgment 當下的事)優先佔用我;本計畫排開賽收尾後立即開工,或你說「先做 UI」
即調序。
