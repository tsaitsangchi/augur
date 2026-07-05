# augur 前後台介面「Claude Desktop 化」完整計劃書 v2

🎯 **白話**：把 augur 的**前台**（誠實博學的我 · 投資哲學顧問對話 app，`scripts/serve_chat_ui.py`）與**後台**（知識控制台 admin，`scripts/serve_admin_console.py`）打磨到**與 claude.ai 網頁版高度一致**——同一套暖色設計系統、serif/sans 二分、標準聊天版面（**composer 永遠釘底、只有訊息區捲動**）、側欄時間分組 recents + hover 選單、串流逐字、訊息 hover 工具列、程式碼複製、Cmd+K、空態 prompt chips、responsive 抽屜。本檔＝**實作前的完整設計計劃**，30 分鐘可讀、逐項可落地。

守 #5（上傳/路徑/XSS 防護）· #1（顧問誠實鏈不被 UI 繞過）· #18（命名）· #28（本地零 usage、純前端 localStorage）· 憲章 v1.30.0（顧問呈現層）· v1.29.0（RBAC）。日期：2026-07-05。

> **範圍界定（誠實）**：本計劃是**介面層**（HTML/CSS/JS + 薄後端端點）。**不新增預測/知識演算法、不改 RBAC enforcement、不繞 guard**。cowork/code 兩情境之專屬後端 agent 尚不存在（§8 誠實缺口明列）。復刻對象是 **claude.ai 網頁版**（頁面內 DOM），**不是** Electron/Tauri 桌面殼（標題列/系統匣/全域喚起明確不在範圍，§8）。

---

## 0. 目標與非目標

**目標**（依「一模一樣」的用戶心智拆解，由骨架到細節）：
1. **版面骨架保真**：app 外殼鎖捲，唯一捲軸落在訊息區；**composer 永遠停底、側欄不動**（修用戶明列的核心 BUG）。
2. **視覺系統保真**：暖色 token、**assistant 正文 serif / UI chrome sans 的二分**（claude.ai 最強識別，目前最大落差）、圓角/邊框/陰影節奏。
3. **側欄保真**：New chat / 搜尋 / Recents **時間分組**（今天/昨天/過去 7 天/過去 30 天/更早）/ 每列 hover 選單（重新命名/刪除/加星）/ 左下帳號區 / 收合鈕。
4. **互動狀態保真**：**串流逐字**（qwen3 SSE）、`<think>` 折疊區塊、訊息 hover 工具列（複製/重試）、程式碼複製鈕、空態 prompt chips、錯誤卡片、Cmd+K 命令面板、responsive 抽屜、sticky-bottom 黏底 + 回到底部鈕、toast 通知。
5. **composer 保真**：卡上模型 pill、送出/停止狀態機、`/` 斜線指令選單（揭露既有隱藏指令）。

**非目標**（明確不做，避免用戶期待落空）：
- **不做桌面殼**（Electron/Tauri、frameless 標題列、traffic-light 內距、系統匣、全域快捷喚起）——augur 走「瀏覽器內高擬真 claude.ai 網頁版」路線（§8）。
- **不做深色模式**（用戶已拍板永遠淺色，鎖 `color-scheme:light`）。
- **不做 Artifacts/Canvas 右側面板**（qwen3 顧問輸出是純文字逐字引文語料、無 tool-use 產物，硬做空面板＝造假；架構上保留 `.main` 未來可容雙欄的意識即可，§8）。
- **不做對話公開分享連結**（違反 local_private 隔離不變式；降級為「匯出 .md / 複製到剪貼簿」，§8）。
- **不做多模態圖片附件縮圖預覽**（qwen3:8b 是文字模型、非視覺，顯示縮圖＝假象，§8）。
- **不做編輯分叉 + 對話樹版本切換**（需把 `s.msgs` 從線性陣列改樹結構，資料模型級改動、對單機本地價值低，§8）。
- **不做讚/踩回饋送出**（本地無回饋收集後端，做 UI 卻無去向＝造假「已送出」，§8）。
- **不做多使用者雲端 / 對話雲端永久儲存**（本機單機為主）。

---

## 1. 設計系統（Design System，兩台共用 SSOT）

### 1.1 色彩 token（暖色 Claude 風，light 主題，鎖 `:root{color-scheme:light}`）

| Token | 值 | 用途 |
|---|---|---|
| `--bg` | `#faf9f5` | 主背景（暖米白，非純白、R>G>B 暖調） |
| `--sidebar` | `#f0eee6` | 側欄背景（比主區深一階暖米灰） |
| `--surface` | `#ffffff` | 卡片／composer／作用中項 |
| `--bubble` | `#f0eee6` | 使用者訊息氣泡 |
| `--text` | `#1f1e1d` | 主文字 |
| `--muted` | `#73726c` | 次要文字（sidebar 項/note/免責） |
| `--border` | `#e9e6dc` | 細分隔線（弱） |
| `--border-strong` | `#dcd8cc` | composer/強調邊 |
| `--accent` | `#d97757` | **Claude 珊瑚**：✻ 星標、送出鈕、focus 邊框、連結、頭像底、作用中 |
| `--accent-hover` | `#c15f3f` | 珊瑚 hover（小字連結亦用此深階確保 AA） |
| `--accent-soft` | `#f5e5dd` | 珊瑚淡底（avatar/chip/modenote） |
| `--hover` | `#e7e4d8` | 側欄項 hover |
| `--codebg` | `#2b2a27` | 程式碼區塊深底（全站淺色，唯 code 深色以利可讀） |
| 狀態綠 | `#5f8a5a` | 健康燈 on／完成徽章 |
| 狀態紅 | `#c15f3f` | 健康燈 off |
| 錯誤淡紅底 | `#fbeaea` | 錯誤卡片背景 |

### 1.2 字體（**serif/sans 二分是本次最關鍵視覺改動**）

| 用途 | font stack |
|---|---|
| **UI chrome**（sidebar/鈕/composer/user 氣泡） | `ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif` |
| **assistant 回覆正文**（含其內標題/清單） | `"Tiempos Text",Georgia,"Songti TC","Noto Serif TC",serif` |
| **空態問候大標** | 同 serif（呼應「serif 是 Claude 的聲音」） |
| **程式碼**（inline / block，即使正文 serif 亦保 mono） | `ui-monospace,SFMono-Regular,Menlo,monospace` |

> **落地要點**：對 `.msg.a .bubble` 套 serif；user 氣泡與所有 UI 維持 sans；code/inline code 維持 mono。這一步最能立刻拉近 editorial 質感。

### 1.3 字級 / 字重 / 行高

- 內文 `15px`；assistant 回覆 `line-height:1.65`；段落 `margin:0 0 12px`。
- 標題階梯：h2 `1.3em` / h3 `1.14em` / h4 `1.02em`，全 `font-weight:600; line-height:1.3`。
- 空態大標 `29px; font-weight:500`（不 bold）。
- sidebar 項 `13-14px`；note/免責 `11-12px`（`--muted`）。字重只用 `400/500/600`（不用 700+）。`-webkit-font-smoothing:antialiased`。

### 1.4 間距 / 圓角 / 邊框 / 陰影 / 圖示

- **圓角**：小控制項 `8-10px`、鈕 pill `50%`、卡片/彈窗 `16-18px`、composer `24px`、頭像 `50%`（帳號）或 `8px`（✻ 星章）、徽章 pill `16-20px`。
- **邊框**：`1px solid var(--border)`（弱）/ `var(--border-strong)`（強）；絕不用冷灰。
- **陰影**：極淡（`0 1-2px … rgba(0,0,0,.05)`）、主要靠 border 分層；composer focus-within 才略增。
- **內容欄寬**：訊息 wrapper `max-width:740px; margin:0 auto`（65-72 字元/行；claude.ai 約 768，740 在合理區間，保留）。捲動容器滿寬、內層置中。
- **共用元件**：✻ 星標（珊瑚）、圓形 `＋`（附加）、圓形珊瑚 `↑`（送出）、pill 徽章、健康燈（8px 圓點）、side-nav 作用中（白底+微陰影+粗體）。

> **落地形式**：`:root{--…}` CSS 變數（單一 SSOT）；兩台各自 inline `<style>`（stdlib server、無打包）。本表為兩台對齊 SSOT；漂移風險升高再抽 `src/augur/…/ui_theme.py` 常數。

---

## 2. 前台版面 — composer 釘底 + 訊息區獨立捲動（**核心，含明確 DOM/CSS**）

### 2.1 版面契約（三層固定高度 → 唯一捲軸落在訊息區）

用戶明列 BUG：「composer 未釘底、整頁一起捲」。**根因**：`#log`（flex:1 子項）缺 `min-height:0`——flex item 預設 `min-height:auto` 拒絕縮小，長內容撐破容器把 `#bar`（composer）頂出 100vh 之外，視覺上就是整頁被推著捲。修復＝三行 CSS。

**DOM 結構（現況 DOM 巢狀已正確，不需搬節點，只補 CSS）**：

```
<div class=app>                    ← flex row, height:100vh, overflow:hidden（外殼鎖捲）
  <aside class=sidebar>…</aside>   ← width:260px, flex-shrink:0（固定寬、不捲）
  <main class=main>                ← flex column, flex:1, min-height:0, position:relative
    <div id=log>…</div>            ← flex:1, min-height:0, overflow-y:auto（唯一捲區）
    <button id=jump>↓</button>     ← 回到底部浮動鈕（absolute 相對 .main）
    <div id=bar>…composer…</div>   ← flex-shrink:0（釘底、不縮不捲）
  </main>
</div>
```

### 2.2 明確 CSS（三行修復 + 完整規則）

```css
html,body{height:100%}
.app{display:flex;height:100vh;overflow:hidden}          /* 外殼鎖 body 級捲動（現況已對）*/
.sidebar{width:260px;flex-shrink:0;display:flex;flex-direction:column;height:100%}
.main{flex:1;display:flex;flex-direction:column;min-width:0;min-height:0;position:relative}
                                                          /* ↑ 補 min-height:0 + position:relative（給 #jump 定位）*/
#log{flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:26px 20px 8px}
                                                          /* ↑↑↑ 補 min-height:0 = 本次最關鍵一行 */
                                                          /*     overscroll-behavior:contain 防捲動穿透到 body */
#bar{flex-shrink:0;padding:8px 20px 18px;                /* ↑ 補 flex-shrink:0 = composer 恆定釘底 */
     background:linear-gradient(180deg,rgba(250,249,245,0),var(--bg) 32%)}
```

**驗證**：訊息很多時，只有 `#log` 出現 scrollbar 且可向上看歷史，`#bar` 恆停視窗底、`.sidebar` 不動。底部漸層讓最後一則訊息漸隱到 composer 底色（漸層是 `#bar` 的 background、不擋點擊）。

### 2.3 auto-scroll 黏底邏輯（sticky/pinned bottom 契約）

現況 `add()` 內 `d.scrollIntoView()` 無條件強拉、會連帶捲最近可捲祖先、行為不可控。改為條件式黏底：

```js
var pinned=true;                                          // 全域黏底狀態
function atBottom(){return log.scrollHeight-log.scrollTop-log.clientHeight<100}
                                                          // 100px 容差（對齊 claude.ai/setproduct 設計指南）
log.addEventListener('scroll',function(){pinned=atBottom();toggleJump()});
// 送出使用者訊息：一律捲到底
//   add('u',text) 後 → log.scrollTop=log.scrollHeight; pinned=true
// 回覆 append（串流每 token 後）：只有 pinned 才續捲
//   if(pinned) log.scrollTop=log.scrollHeight
// 移除對訊息 div 的 scrollIntoView()
```

- **使用者上捲**超過 100px → `scroll` 事件令 `pinned=false`，之後回覆/串流不再強拉回底；捲回底部 → `pinned` 自動恢復 true。這是 GitHub issue #18404 明列的行為契約。
- **串流時**（§4.1）：每次 append token 後 `if(pinned) log.scrollTop=log.scrollHeight`。若日後 jitter 明顯，用 `wheel` 事件（真人滾輪/觸控板才觸發、layout 位移不觸發）偵測使用者主動上捲設 `pinned=false`，並用 `requestAnimationFrame` 節流分批校正。

### 2.4 回到底部浮動鈕（jump to latest）

```css
#jump{position:absolute;left:50%;bottom:96px;transform:translateX(-50%);
      width:34px;height:34px;border-radius:50%;background:var(--surface);
      border:1px solid var(--border-strong);color:var(--muted);
      box-shadow:0 2px 10px rgba(0,0,0,.1);cursor:pointer;
      opacity:0;pointer-events:none;transition:opacity .18s;
      display:flex;align-items:center;justify-content:center;z-index:6}
```

```js
function toggleJump(){var on=!atBottom();
  jump.style.opacity=on?'1':'0';jump.style.pointerEvents=on?'auto':'none'}
jump.onclick=function(){log.scrollTo({top:log.scrollHeight,behavior:'smooth'});pinned=true};
```

- 顯示條件：`pinned=false`（離底 >100px）淡入；回底淡出。位置：訊息區右下、composer 正上方置中偏下。

### 2.5 切換對話 / 空態的捲位

- `loadSession()` 重建 `log.innerHTML` 後，末尾補 `log.scrollTop=log.scrollHeight; pinned=true`（開既有對話直接定位到底部最新訊息，對齊 claude.ai、避免誤捲到頂）。
- 空對話：`#greet` 置中（`margin:13vh auto`），無捲動需求；首則訊息送出即 `_g.remove()`，訊息從捲動區頂部 padding 之下起堆疊。greeting 用 margin auto 置中、不干擾 `#log` 的 `flex:1` 高度計算。

---

## 3. 側欄（Sidebar）

### 3.1 側欄自身三段式捲動

```css
.sidebar{width:260px;flex-shrink:0;background:var(--sidebar);
         border-right:1px solid var(--border);
         display:flex;flex-direction:column;height:100%;padding:12px;overflow:hidden}
/* 頂部（brand/new chat/搜尋/情境）flex-shrink:0 固定 */
.recents{flex:1;min-height:0;overflow-y:auto}   /* 只有 recents 捲（min-height:0 關鍵）*/
.foot{flex-shrink:0}                              /* 底部帳號/健康燈固定 */
```

自頂而下：`✻ augur` 品牌（+ 收合鈕）→ `＋ 新對話` → 搜尋 → 三情境切換 → Recents（時間分組 + hover 選單）→ 底部（健康燈 + 知識控制台外連 + 帳號區）。

> **參照範本**：後台 `serve_admin_console.py` 的 `.side`（`display:flex;flex-direction:column`）+ `.acct-box{margin-top:auto}` 已正確做到分段捲動 + 帳號貼底，前台照套。

### 3.2 New chat（現況 done）

品牌下第一個顯著項：左 `＋`（珊瑚）+「新對話」，整列可點、hover 淺底、圓角 8-10px。`onclick=newSession()`：清 log 回該情境問候、解除附加、重置輸入、`q.focus()`。可綁 `Cmd/Ctrl+Shift+O`（§4.6）。

### 3.3 搜尋（Search chats）— gap，medium

New chat 下加一列 `.search`（放大鏡 + 「搜尋對話」）。純前端：

```js
// 點擊在 sidebar 頂部展開一個 input；oninput 即時 filter：
//   SESSIONS.filter(s => s.title.includes(q) || s.msgs.some(m=>m.content.includes(q)))
// 命中結果重繪 Recents（平列、不分組）；清空還原時間分組。可綁 Cmd/Ctrl+K focus（§4.6 命令面板）。
```

### 3.4 Recents 時間分組 — gap，high

現況 `renderRecents()` 只 push 一個寫死「近期」header。改為依 `s.ts` 分桶（本地時區日界）：

```js
var t0=new Date();t0.setHours(0,0,0,0);var d=t0.getTime();
// 桶判定（由新到舊，固定順序）：
//   今天       ts >= d
//   昨天       ts >= d-86400000
//   過去 7 天   ts >= d-7*86400000
//   過去 30 天  ts >= d-30*86400000
//   更早       再按月份 label（如 '2026 年 6 月'）
// 每個非空桶輸出一個 .rec-h（沿用現有 class）+ 該桶列（依 ts 倒序）
```

分組順序固定：**今天 → 昨天 → 過去 7 天 → 過去 30 天 → 更早（按月）**。Starred 分區（§3.6）排在所有時間桶之上。

### 3.5 每列 hover 選單（重新命名 / 刪除 / 加星 / 分享）— gap，high

`.rec` 列改 `position:relative` flex 容器，右端加預設 `opacity:0`、`.rec:hover` 時 `opacity:1` 的 kebab（⋯）真 button（tabbable）。點開小 popover：

- **重新命名**：inline 換 input 或 `prompt()`，提交後改 `s.title` → `saveSessions()` → `renderRecents()`。
- **刪除**：`confirm()` 後 `SESSIONS` 陣列移除該 id；若刪的是 `CURid` 則 `newSession()`；`saveSessions()` → `renderRecents()`。
- **加星/取消星**：切 `s.starred` → 即時移入/移出 Starred 區（§3.6）。
- **分享**：**不做公開連結**（違反隔離不變式，§8）；改為「複製對話為 Markdown 到剪貼簿」或「下載此對話 .md」——保留把內容帶出去的實用內核。

kebab `Esc` 關、點外部關；全純前端 localStorage、零後端零 usage。

### 3.6 Starred（加星置頂）— gap，medium

`session` 物件加 `s.starred` 布林；hover 選單加加星動作。`renderRecents()` 先渲染 Starred 分區（`.rec-h`「已加星」+ 所有 `s.starred` 列，不受時間分組），再渲染時間桶。空時該區隱藏。狀態存 localStorage。

### 3.7 對話標題自動生成 — gap（省 usage 折衷）

現況 `recordMsg` 只 `s.title=content.slice(0,24)`（硬截 24 字，sidebar 一排難看半句）。折衷：

- **(a) 零成本改良（先做）**：取首則訊息「第一句」（到 `。`/`?`/`？`止）或首行，明顯改善。
- **(b) 真 AI 命名（可選、標記）**：首次回覆完成後背景發一個「用 8 字命名這段對話」的輕量本地請求更新 `s.title`——需權衡 qwen3 額外一次生成延遲（#28）。建議先 (a)。

### 3.8 左下帳號區（現況 done）

貼底（`margin-top:auto` 或 `.foot` 固定）、上方 1px 分隔線。圓形頭像 30px（monogram initial、珊瑚底白字）+ 兩行：主行使用者名、次行「模型版本 · 角色」（session 真實查 `app_user`、非寫死）+ 登出 ⏻。

- **點擊彈出小選單（gap，low）**：整列可點開向上 popover：登出、知識控制台外連（:8500）、快捷鍵小抄、關於 augur 版本。**資料控制（對齊 Claude data control 精神、零後端）**：加「匯出全部對話 JSON / 清空本機對話」兩個純前端動作。不做主題切換（永遠淺色）、不做方案/訓練資料開關（本地不外送、不適用）。

### 3.9 收合鈕（collapse）— gap，low

brand 列右端加收合 button（`<<`）。點擊 toggle `.app` 上 `.collapsed` class：`.sidebar` `width:0` 或縮成 icon rail（64px）、主區佔滿；`transition:width .2s ease`；狀態記 `localStorage('augur_sidebar_collapsed')`。收合後左緣留展開把手。

### 3.10 情境切換 / 模型位置（現況設計，保留）

- 三情境（對話/協作/程式）佔 claude.ai 中 Projects/Starred 的視覺位置，是 augur 刻意設計（三情境共用顧問後端、誠實標註），**非 BUG**，保留。若要更貼 claude.ai 可改頂部 segmented control，屬產品取捨、不需改。
- 模型選單 claude.ai 放主區/composer（per-conversation 決策）。augur 目前單一本地模型，帳號次行唯讀顯示合理；卡上模型 pill 見 §5.2。

---

## 4. 互動與狀態（Interaction States）

### 4.1 訊息串流（逐字/分塊繪製）— gap，high

現況一次性 `fetch` 後整段塞入、無串流。後端 advisor 殼 `/v1/chat/completions` 是 OpenAI 相容格式，可請求 `stream=true` 讓 Ollama/qwen3 走 SSE。前端改法：

```js
// send() 的 await r.json() 改為 fetch + response.body.getReader() 讀 SSE：
//   逐塊解析 choices[0].delta.content → append 進累積字串 acc
//   每塊後對 acc 整段重跑 mdToHtml() 寫回 wait._bubble.innerHTML（增量 re-parse，code/清單邊串流邊成形）
//   尾端顯示閃爍游標 <span class=caret>；if(pinned) log.scrollTop=log.scrollHeight
// 串流完成（SSE done）後才附 guard verdict（guard 需完整答案才判，收全文後顯示 [guard] 行）
```

```css
.caret{display:inline-block;width:7px;height:1.1em;background:var(--accent);
       vertical-align:text-bottom;animation:blink 1s step-end infinite}
@keyframes blink{50%{opacity:0}}
```

若殼暫不支援串流，至少把假「思考中…」文字改為脈動骨架（§4.4）。串流中送出鈕切停止方鈕（§5.3）、用 `AbortController.abort()` 中斷、partial 保留。

### 4.2 `<think>` 折疊區塊（extended thinking）— gap，high（augur 特別契合）

qwen3:8b 原生輸出 `<think>…</think>` 推理段。現況 `mdToHtml` 未處理、推理內容裸露或被殼剝掉。改法：串流/渲染時偵測 `<think>…</think>`，渲染成 Claude 式**可折疊淡色區塊**（預設收合、點「顯示思考過程」展開），與正文分離。串流時 `<think>` 段先逐字進思考區、`</think>` 後切正文。完成後收合成一行摘要（「思考了 N 秒」，N 為串流計時）。這是把 qwen3 既有能力包裝成 Claude 質感的高 CP 值一項。

```css
.think{margin:0 0 12px;border:1px solid var(--border);border-radius:10px;
       background:var(--sidebar);font-size:13.5px;color:var(--muted)}
.think summary{cursor:pointer;padding:8px 12px;list-style:none;user-select:none}
.think .body{padding:0 12px 10px;font-family:inherit;white-space:pre-wrap}
```
用 `<details class=think><summary>顯示思考過程</summary><div class=body>…</div></details>`。

### 4.3 訊息 hover 工具列 — gap，high

`.msg` 內附 `.actions` 容器（`opacity:0;transition:opacity .15s`；`.msg:hover .actions{opacity:1}`；`@media(hover:none){.actions{opacity:1}}` 觸控常駐）：

- **assistant 訊息**：複製整則（`navigator.clipboard.writeText(該則純文字)`，點後 icon 換 ✓ 1.5s + 'Copied' tooltip）、重試（重送該輪 user 訊息、覆寫本則回覆）。**不做讚/踩**（本地無回饋去向，§8）。
- **user 訊息**：複製 + 編輯（把氣泡換 textarea 預填原文、Save 重送）。**編輯不做分叉/多版本樹**（§8）——編輯即覆寫重生、不建 `< n/m >` 版本切換器。

所有按鈕 `aria-label`、可 Tab、Enter/Space 觸發。串流完成前工具列不出現。按鈕 `32x32px`、圓角、透明底、hover 淡灰底。

### 4.4 載入骨架 / 脈動等待態 — gap，medium

現況等待態是純文字假訊息「思考中…」。改為脈動：`add('a','')` 後在氣泡放三點 `<span class=dots>` + CSS keyframes `opacity:.35→1`（約 1.2s 循環）或 ✻ 星芒 pulse。串流首 token 到達即移除脈動改逐字。骨架約 300-500ms 內出現以免看似當機。

### 4.5 程式碼區塊複製鈕 + 語言標籤 — gap，medium

`mdToHtml` 的 code fence 正則改捕語言標識（`` /```(\w+)?\n?([\s\S]*?)```/ ``），包一層：

```html
<div class=codewrap>
  <div class=codebar><span class=lang>python</span><button class=codecopy>複製</button></div>
  <pre class=cb><code>…</code></pre>
</div>
```
```css
.codebar{display:flex;justify-content:space-between;align-items:center;
         background:#1f1e1d;color:#8a8a8a;padding:5px 12px;font-size:12px;
         border-radius:10px 10px 0 0}
.codecopy{background:transparent;border:0;color:#b8b3a8;font-size:12px;cursor:pointer}
.codewrap pre.cb{border-radius:0 0 10px 10px;margin:0}
```
事件委派：`log.addEventListener('click', e=>{if(e.target.matches('.codecopy')) …clipboard.writeText(同 codewrap 內 pre code textContent)…})`，按鈕文字換「已複製 ✓」1.5s。code block 維持深底 `--codebg`（全站淺色唯 code 深色）。

### 4.6 鍵盤快捷 — gap，medium

全域 `document.addEventListener('keydown')`（游標在 `#q` 外才觸發大多數）：

| 快捷 | 動作 |
|---|---|
| `Cmd/Ctrl+K` | 開命令面板 overlay（`role=dialog aria-modal`），對 `SESSIONS` 標題 fuzzy 過濾（上下鍵選、Enter `loadSession`、Esc 關）+ 快捷動作 |
| `Cmd/Ctrl+Shift+O` | `newSession()` |
| `Enter` / `Shift+Enter` | 送出 / 換行（現況 done） |
| `Esc` | 分層退場：先關 plusmenu/命令面板/斜線選單 → 再停止串流 → 再取消編輯 |
| `Cmd/Ctrl+Shift+;` | 聚焦 `#q` |
| `/`（在 `#q` 內首字元） | 彈斜線指令選單（§5.5） |

plusmenu 現況點外部不關，順帶補 `Esc`/點遮罩關。

### 4.7 空態 prompt chips — gap，medium

`#greet` 問候句下加一排 3-4 顆建議 chip（依 MODE 給不同起手式；`GREET` 物件已按 mode 分，擴充加 chips 陣列）。如 chat：「價值投資的核心是什麼?」「葛拉漢的安全邊際」「巴菲特護城河」。

```css
.chip{display:inline-block;padding:8px 14px;margin:6px;
      border:1px solid var(--border-strong);border-radius:16px;
      background:var(--surface);font-size:13px;cursor:pointer;color:var(--text)}
.chip:hover{background:var(--bubble)}
```
`onclick` 填入 `#q`（可自動 `send()` 或僅填待用戶按送出）。

### 4.8 錯誤態卡片 + Retry — gap，medium

現況 catch 只 `wait._bubble.textContent='錯誤:'+err`。改渲染錯誤卡片：

```css
.errcard{background:var(--errbg,#fbeaea);border:1px solid #e5c4c0;border-radius:10px;
         padding:12px 14px;color:#8a3a2f;display:flex;align-items:center;gap:10px}
```
內容：警示 icon + 說明（區分網路錯誤/殼 500/逾時文案）+ 行內「重試」按鈕（重呼 send 同一輪 user text）。加 `role=alert` 供螢幕報讀。429/limit 不自動重試（承 #24/#28 見訊號即停），由使用者手動 Retry。guard 攔下（`g.pass=false`）沿用 fail 樣式並可再強化。

### 4.9 responsive 窄螢幕側欄抽屜 — gap，medium

現況 `.sidebar{width:260px}` 固定、無漢堡。加：

```css
@media(max-width:768px){
  .sidebar{position:fixed;left:0;top:0;height:100vh;transform:translateX(-100%);
           transition:transform .22s ease;z-index:20}
  .sidebar.open{transform:none}
  .main{width:100%}
}
.scrim{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;z-index:15}
.scrim.show{display:block}
```
`.main` 頂部加精簡 app bar 含漢堡（☰，`onclick` 切 `.sidebar.open` + `.scrim.show`）。抽屜 `transform:translateX(-100%)→0`；點遮罩/選 recents 一項/`Esc` 關；開啟時 focus trap、關後焦點還漢堡鈕。composer/訊息維持全寬、左右 padding 縮小。觸控無 hover → hover 工具列改常駐（§4.3）。

### 4.10 toast 通知系統 — gap（並修一個資料語意 BUG）

現況所有系統回饋（解除附加 `add('a','已解除附加。')`、入庫結果、附加成功、複製）都塞進對話流，**污染 `#log` 且被 `recordMsg` 存進 localStorage 變永久對話內容**（語意錯誤——「已解除附加」不該是一則對話）。改：加輕量 toast（右下角淡入淡出、2-3s 自動消失），把上述系統回饋全改走 toast，不再污染對話記錄。

```css
.toast{position:fixed;right:20px;bottom:20px;background:var(--surface);
       border:1px solid var(--border-strong);border-radius:10px;padding:10px 16px;
       font-size:13px;box-shadow:0 4px 18px rgba(0,0,0,.1);
       opacity:0;transform:translateY(8px);transition:.2s;z-index:30}
.toast.show{opacity:1;transform:none}
```
桌面系統推播（Notification API）需權限，標可選（low）。**這項同時提升擬真度並修正「系統訊息被當對話存檔」的資料語意錯誤**。

### 4.11 focus 可及性 — gap，low

現況 `:focus-visible` 珊瑚外框基礎良好（保留）。補：icon 按鈕（複製/重試/停止/kebab）全加 `aria-label`；`#log` 加 `aria-live='polite'`（串流中可暫 off、完成後朗讀最終訊息以免逐字轟炸）；命令面板/抽屜加 `role=dialog aria-modal=true` + focus trap + 關後焦點還原觸發元素；珊瑚小字用 `--accent-hover #c15f3f` 確保 WCAG AA。

---

## 5. composer（輸入區）細節

### 5.1 圓角卡片容器（現況 done）

`max-width:740px; border-radius:24px; background:var(--surface); border:1px solid var(--border-strong); box-shadow:0 2px 14px rgba(0,0,0,.05); display:flex; align-items:flex-end; gap:8px`；`focus-within` 邊框深化 + 陰影加強。左 `＋` 附加、中 textarea、右 `↑` 送出，與訊息氣泡同寬置中。

> **陰影微調（low）**：claude.ai composer 幾乎純靠 border 分層，可把 `box-shadow` 降到 `0 1px 3px` 或移除、focus-within 才給極淡陰影。保留現狀亦無傷。

### 5.2 卡上模型 pill — gap，medium

送出鈕左邊加 model pill，顯示當前模型（`OLLAMA_MODEL`/`__MODEL__` 已可取），點開列可用本地模型（`ollama /api/tags` 已在 `_health` 探測、可重用列清單）。即便只有 `qwen3:8b`，顯示「qwen3:8b ▾」也對齊 claude.ai「首鍵前先看到 tier」的資訊揭露。與 `＋` 分置左右符合 Claude 語意分離（左＝附加什麼、右＝哪個模型答）。

### 5.3 送出 / 停止狀態機 — gap，medium

三態：(a) 空輸入 = disabled/淡；(b) 有內容 = 實心珊瑚可送；(c) 生成中 = 停止方鈕（■）。實作：`send()` 內用 `AbortController` 包 fetch，生成中 `#b` 切 stop 樣式綁 `controller.abort()`；完成/中斷復原為 `↑`。對長本地生成（qwen3:8b 可能數十秒）體驗提升明顯。

### 5.4 多行自動成長 + Enter 送出（現況 done）

textarea 單行起，`input` 事件 `height:auto→min(scrollHeight,180)`，封頂 180px 後 `overflow-y:auto` 內部捲。`Enter` 送出、`Shift+Enter` 換行（`keydown` 攔 `Enter && !shiftKey → preventDefault + send`）。**補**：IME 組字（中日韓）中的 Enter 不誤送——`compositionstart/compositionend` 期間不送。

### 5.5 `/` 斜線指令選單 — gap（揭露既有隱藏能力）

augur 已實作 `/移除`、`/remove`（解除附加）、`+路徑`（資料夾 dry-run 掃描）三指令但**零 UI**、用戶無從得知。改：`#q` 打 `/`（首字元）時彈小選單列出：

- `/移除` — 解除附加
- `/remove` — 同上（英文別名）
- `+資料夾路徑` — 掃描預覽（dry-run，不入庫）

這不是新功能、是把已寫好卻埋著的能力顯露。`Esc`/選擇/點外部關。

### 5.6 附件（對齊 augur 文字語料語意）

- **拖放檔案/資料夾到視窗（gap，low）**：觸發現有 `doAttach/doIngest`，加一層 drop overlay 提示（「放開以附加」半透明遮罩）。
- **`#chip` 升多附件卡列（gap，low）**：從單一標籤升為每卡「檔名 ellipsis + 檔型 icon + × 個別移除」，對齊 Claude chip 樣式（小圓角）。
- **不做圖片縮圖預覽**（qwen3 文字模型、非多模態，§8）。

### 5.7 placeholder / 免責（現況 done）

placeholder「輸入訊息…」（等同 claude.ai「Message Claude…」）。免責小字**照抄 claude.ai 風格**〔用戶 2026-07-05 拍板「照抄 claude.ai」，**覆蓋本計劃原「維持 augur 特有版」之建議**〕：「誠實博學的我可能會出錯，請查證重要資訊。」（對齊 claude.ai「Claude can make mistakes. Check important info.」；**已落地** commit 2a4c2c4）。三情境位置（§3.10）claude.ai 無對應等價物、維持側欄 nav（Claude 式位置）。

---

## 6. 後台（知識控制台）對應

後台 `serve_admin_console.py` 的 `.side`（`display:flex;flex-direction:column`）+ `.acct-box{margin-top:auto}` **已正確做到分段捲動 + 帳號貼底**，是前台 §2/§3 修正的參照範本。後台對應調整：

| 項 | 現況 | 動作 |
|---|---|---|
| 設計 token | 同一套暖色 | 對齊 §1 SSOT（若前台改 serif 二分，後台 `.mdbody` 文件正文亦可套 serif、標題/UI 維持 sans） |
| 側欄捲動 | 已對（`.side` flex column + `.acct-box` margin-top:auto） | 保留、作前台範本 |
| 文件渲染 `_md_to_html` | 已支援標題/表格/碼/清單/引言 | 補齊與前台 `mdToHtml` 一致（blockquote/table 兩台同款；後台已有可作前台補課參照） |
| 帳號區點擊選單 | 僅登出 | 可與前台 §3.8 同步（登出/外連/關於），low |
| 收合鈕 / responsive | 無 | 與前台 §3.9/§4.9 同款套用（後台 nav 較短、優先序 low） |
| 程式碼複製鈕 | 文件 `.mdbody pre.cb` 無複製鈕 | 可套 §4.5（medium，文件常含指令碼） |

後台**安全（#5）不變**：`.md` 檢視 `_read_doc` realpath 圍欄（僅 `reports/`＋`docs/`、副檔 `.md`、拒 traversal）；`_md_to_html` 先 `html.escape` 全文再結構化（防 XSS）；job log `_safe_log` 圍欄（僅 `harvest_<hex>.log`）。**新增前端互動（toast/hover/搜尋）不觸後端授權路徑**。

---

## 7. 分階段（標 augur 現況 done / gap / 優先序）

> **執行進度（2026-07-05 UI 全部落地）**：**Phase 1-4 全數完成**（結構驗證＋mock 殼串流端到端＋134 測試通過；互動待瀏覽器確認）——
> ✅ **Phase 1** 捲動釘底（`#log min-height:0`＋pinned 黏底＋回到底部鈕）· ✅ **Phase 2 側欄**（recents 時間分組／hover 選單重新命名·加星·複製·刪除／搜尋／starred／toast）· ✅ **Phase 3** serif/sans 二分・串流 SSE・訊息複製・程式碼複製・chips・錯誤卡・骨架脈動・**retry**・**Cmd+K 命令面板**・**responsive 抽屜** · ✅ **Phase 4** 模型 pill・停止鈕（AbortController）・斜線指令選單 · ✅ 帳號區・永遠淺色・免責照抄・後台背景工作 log 選取複製。
> **明確不做（§8 誠實缺口／§0 非目標）**：~~think 折疊（殼 think=False、moot）~~・桌面殼・Artifacts・公開分享・圖片縮圖・編輯分叉・讚踩；§5.6 附件拖放/多卡列（low、未做）。

### Phase 0 — 已實作（現況 done，本次不動）
暖色設計系統 + token、260px sidebar（brand/新對話/三情境/recents localStorage/健康燈/左下帳號區真實查 `app_user`）、composer（圓角 24px/＋附加/textarea Enter 送出/自動長高 180px）、訊息樣式（user 右氣泡/assistant ✻ 星章）、`mdToHtml`（標題/清單/inline code/深色 code block/粗體/連結）、`:focus-visible` 珊瑚 ring、`/health` 15s 輪詢三燈、鎖 `color-scheme:light`、後台 `.side` 分段捲動 + `.acct-box` 貼底 + 文件 md 渲染。

### Phase 1 — 版面骨架修復（**high，最優先，一次做完**）
| 項 | 優先 | §參照 |
|---|---|---|
| `#log` 補 `min-height:0`（**核心 BUG 一行修復**） | high | §2.2 |
| `#bar` 補 `flex-shrink:0`、`.main` 補 `min-height:0`+`position:relative` | high | §2.2 |
| auto-scroll 黏底（`pinned` 狀態機 + `atBottom()` 100px 容差） | high | §2.3 |
| 移除無條件 `scrollIntoView()`、`loadSession` 後定位到底 | high | §2.3, §2.5 |
| 回到底部浮動鈕 `#jump` | medium | §2.4 |

### Phase 2 — 視覺 + 側欄保真（high/medium）
| 項 | 優先 | §參照 |
|---|---|---|
| **assistant 正文 serif（serif/sans 二分）** | high | §1.2 |
| Recents 時間分組 | high | §3.4 |
| 每列 hover 選單（重新命名/刪除/加星/複製匯出） | high | §3.5 |
| 搜尋入口 | medium | §3.3 |
| Starred 分區 | medium | §3.6 |
| 標題自動生成（零成本首句版） | medium | §3.7 |
| blockquote / table markdown 渲染 | medium | §4.5 延伸（前台補後台已有款） |
| 收合鈕 / 帳號區彈出選單 | low | §3.8, §3.9 |

### Phase 3 — 互動與狀態（high/medium）
| 項 | 優先 | §參照 |
|---|---|---|
| 串流逐字（SSE，殼 `stream=true`） | high | §4.1 |
| `<think>` 折疊區塊 | high | §4.2 |
| 訊息 hover 工具列（複製/重試/編輯覆寫） | high | §4.3 |
| toast 系統（修對話污染 BUG） | high | §4.10 |
| 程式碼複製鈕 + 語言標籤 | medium | §4.5 |
| 空態 prompt chips | medium | §4.7 |
| 錯誤卡片 + Retry | medium | §4.8 |
| Cmd+K 命令面板 + 快捷 | medium | §4.6 |
| responsive 抽屜 | medium | §4.9 |
| 載入脈動骨架 | medium | §4.4 |
| focus 可及性補強 | low | §4.11 |

### Phase 4 — composer 細節（medium/low）
| 項 | 優先 | §參照 |
|---|---|---|
| 送出/停止狀態機（AbortController） | medium | §5.3 |
| 卡上模型 pill | medium | §5.2 |
| `/` 斜線指令選單（揭露隱藏能力） | medium | §5.5 |
| IME 組字防誤送 | medium | §5.4 |
| 拖放 overlay / 多附件卡列 | low | §5.6 |
| 陰影微調 border-only | low | §5.1 |

### Phase 5 — 後台對應 + 對話歷史入 DB（待拍板）
後台套 §6；對話歷史若拍板入 PostgreSQL 見 §7.1（否則維持 localStorage、零 schema）。

### 7.1 對話歷史入 DB（計畫完整性預留 schema，僅拍板後建）

```sql
CREATE TABLE IF NOT EXISTS chat_session (
  session_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id    bigint NOT NULL REFERENCES app_user,
  mode       varchar(16) NOT NULL DEFAULT 'chat',   -- chat|cowork|code
  title      text, starred boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS chat_message (
  message_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  session_id bigint NOT NULL REFERENCES chat_session ON DELETE CASCADE,
  role       varchar(12) NOT NULL,                   -- user|assistant
  content    text NOT NULL, guard_pass boolean,
  created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS ix_chat_message_session ON chat_message(session_id, message_id);
```
Python：遷移 `scripts/migrate_chat_history_ddl.py`（冪等 guard）；讀寫 `src/augur/advisor/chat_history.py`（`create_session`/`append_message`/`list_sessions`/`load_messages`，**只讀寫這兩表、隔離不變式不觸預測/知識表**）；前台加 `/api/sessions`、`/api/session/<id>` 端點。RBAC：session 綁 `user_id`、他人不可讀（承 v1.29.0 owner 收窄）。

---

## 8. 誠實缺口（三敵/#15，明列不含糊）

1. **cowork/code 無專屬後端**：三情境共用投資顧問 advisor；協作/程式問非投資主題時，顧問依 guard 誠實回「知識庫中無此內容」而非佯裝會做。頂端 `modenote`（珊瑚淡底）標「此情境沿用顧問後端、專屬 agent 建置中」，composer 附近可延續一行 muted 誠實標註。**不得**為「看起來完整」讓 cowork/code 假裝有專屬能力。
2. **不做桌面殼（架構性不適用）**：augur 前台是 stdlib `http.server` 跑瀏覽器分頁、非打包原生 app，無標題列/系統匣/全域喚起可言，**不引入 Electron**（違極簡取向、徒增依賴、重蹈 Open WebUI HF crash-loop）。明說走「瀏覽器內高擬真 claude.ai 網頁版」路線。**這是最該誠實標記、避免用戶期待落空的一項。**
3. **不做 Artifacts/Canvas 右側面板**：qwen3 顧問輸出是純文字逐字引文語料、無 tool-use/code-execution 產物，硬做空面板＝造假。架構上保留 `.main` 未來可容 `.artifact-pane` 的雙欄意識（現單欄 flex column 合理）；未來顧問能產結構化文件（如估值報表）再引入。**現在誠實優於擬真。**
4. **不做對話公開分享連結**：公開 URL 需可公開存取的快照後端 + 唯讀路由，違反 augur 單機本地私有（RBAC P4、`access_scope=local_private`）的存取隔離不變式。hover 選單「分享」降級為「複製對話為 Markdown / 下載 .md」，保留把內容帶出去的內核。
5. **不做多模態圖片附件縮圖**：後端是本地逐字文字語料、qwen3:8b 非視覺模型，顯示圖片縮圖是假象。附件走「入庫/只問這次」文字語意（可升多附件卡列 §5.6），不做圖片預覽。
6. **不做編輯分叉 + 對話樹版本切換**：需把 `s.msgs` 從線性陣列改樹結構（多子分支 + 當前路徑指標），資料模型級改動、對單機本地顧問價值不高、複雜度高。編輯即覆寫重生（§4.3），不建 `< n/m >` 版本器。
7. **不做讚/踩回饋送出**：本地無回饋收集後端，做 UI 卻無實際去向會造假「你的回饋已送出」。故 hover 工具列只做複製/重試。
8. **永遠淺色**（用戶拍板）：鎖 `color-scheme:light`、移除任何 `prefers-color-scheme:dark`，不半套深色以免與 claude.ai 淺色招牌不符。程式碼區塊深底是刻意（利可讀）、非深色模式。
9. **對話歷史未持久化（現況）**：localStorage 版（每情境獨立、最近 100 則、重整不失但換裝置失）；DB 兩表版 §7.1 待拍板。
10. **健康燈為可達性、非深度健康**：`/health` 只探端口可達（advisor `/v1/models`、ollama `/api/tags`、DB `SELECT 1`），不驗模型能否推理。

---

## 9. 驗收準則 + Claude Desktop 保真檢查表

### 9.1 驗收準則（Definition of Done）

- **版面**：訊息很多時只有 `#log` 出 scrollbar、可向上看歷史，composer 與側欄恆定不動；切既有對話定位到底部最新。
- **視覺**：與 claude.ai 並排「一眼認得是同一風格」；assistant 正文 serif、UI sans；珊瑚僅用於主動作與品牌（不濫用）。
- **互動**：串流逐字 + 游標；hover 工具列複製/重試可用；程式碼一鍵複製；空態 chips 可點；Cmd+K 可搜；錯誤有卡片可重試；窄屏側欄收抽屜；系統回饋走 toast 不污染對話。
- **安全**：`.md`/job log 路徑圍欄 + XSS escape 通過；RBAC/guard 不被 UI 繞過（顧問仍經 advise+guard 單閘）；新增前端互動不觸後端授權路徑。
- **回歸**：`pytest` 全綠、隔離 AST 稽核過、兩台 `python -m py_compile` + 起 server 冒煙 200。

### 9.2 Claude Desktop 保真檢查表（逐項可勾 ☐）

**版面骨架 / 捲動**
- ☐ app 外殼鎖 body 捲動（`.app height:100vh; overflow:hidden`）
- ☐ `#log` 有 `min-height:0`、唯一捲軸落此區
- ☐ `#bar` composer `flex-shrink:0`、訊息再多都恆定釘底
- ☐ 側欄捲動獨立、帳號區貼底不動
- ☐ 送出後在底部→自動黏底；已上捲→不強拉（`pinned` 100px 容差）
- ☐ 回到底部浮動鈕：離底淡入、點擊平滑回底、回底淡出
- ☐ 底部漸層遮罩（`pointer-events:none` 不擋點擊）
- ☐ 開既有對話定位到底部最新（非頂部）
- ☐ 空態問候置中、送出後讓位訊息流

**視覺系統**
- ☐ 暖米白 `#faf9f5` 主背景、側欄 `#f0eee6`、珊瑚 `#d97757` accent
- ☐ **assistant 正文 serif、UI chrome sans（二分）**
- ☐ 內文 15px / line-height 1.65 / 字重僅 400·500·600
- ☐ 圓角節奏（composer 24px、卡片 16-18px、小控制項 8-10px）
- ☐ 邊框暖灰非冷灰、陰影極淡（border 為主分層）
- ☐ user 右對齊米色氣泡（max-width 82%）、assistant 全寬無框 + ✻ 星章
- ☐ 鎖淺色（無深色模式）

**側欄**
- ☐ New chat（＋、珊瑚、可點清空開新）
- ☐ 搜尋入口（即時 filter 標題+內文）
- ☐ Recents 時間分組（今天/昨天/過去 7 天/過去 30 天/更早按月）
- ☐ 每列 hover kebab 選單（重新命名/刪除/加星/複製匯出）
- ☐ Starred 分區置頂
- ☐ 標題自動生成（首句版，非硬截 24 字）
- ☐ 左下帳號區（頭像 + 使用者名 + 模型·角色 + 點擊彈選單）
- ☐ 收合鈕（狀態記 localStorage）

**互動與狀態**
- ☐ 串流逐字 + 閃爍游標
- ☐ `<think>` 可折疊思考區塊
- ☐ 訊息 hover 工具列（assistant 複製/重試、user 複製/編輯）
- ☐ 程式碼區塊語言標籤 + 一鍵複製（✓ 回饋）
- ☐ 空態 prompt chips（依 mode）
- ☐ 錯誤卡片 + Retry（區分網路/500/逾時）
- ☐ Cmd+K 命令面板 + Cmd+Shift+O 新對話 + Esc 分層退場
- ☐ responsive 窄屏側欄抽屜（漢堡 + scrim + focus trap）
- ☐ 載入脈動骨架（非純文字「思考中」）
- ☐ toast 系統回饋（不污染對話 / localStorage）
- ☐ focus-visible ring + aria-label + aria-live

**composer**
- ☐ 圓角卡 + focus-within 深化
- ☐ 左 ＋ 附加 / 右 ↑ 送出 語意分離
- ☐ 送出/停止狀態機（生成中 ■ 可中斷）
- ☐ 卡上模型 pill（「qwen3:8b ▾」）
- ☐ textarea 自動長高封頂 180px + IME 防誤送
- ☐ `/` 斜線指令選單（揭露 /移除·/remove·+路徑）
- ☐ 免責小字（augur 具體版、不照抄）

**誠實缺口（確認明列、非默默省略）**
- ☐ cowork/code 無後端已標註
- ☐ 桌面殼 / Artifacts / 公開分享 / 圖片縮圖 / 編輯分叉 / 讚踩 明確標不做且說明理由
- ☐ 顧問誠實鏈（advise+guard）未被任何 UI 互動繞過
