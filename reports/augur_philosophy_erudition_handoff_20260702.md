# augur 哲學素養庫擴充階段 — 執行記錄與交接報告

**日期**：2026-07-02　**封存 tag**：`philosophy-erudition-expand-20260702`　**HEAD**：`4854aba`（remote 同步 0/0）
**性質**：本階段（續哲學素養框架）之完整執行記錄，供**重開機／換機接續**。DB 跨機獨立不進 git，換機須以本報告 + 實查為準重建認知。

---

## 一、階段目標與一句話總結

延續哲學素養框架（`philosophy-erudition-20260701` / `philosophy-advisor-20260701`），本階段將**哲學素養庫從「哲學家」擴到「管理各領域思想家」、從「書目」補到「多語言公版全文」，並把「現代版權著作核心精神合規路」入憲（v1.18.0）**。核心貫穿一條線：**凡入庫內容必為真兆（公版逐字／書目事實 metadata），AI 生成內容一律擋在門外（#1 命門）**。

---

## 二、本階段用戶指令序列（時序）

1. 續抓中文古典諸子（公版全文）
2. `philosophy_thinker` 增加管理各領域（組織/企業/財務/會計/生產/投資/研發管理）全世界 thinker，窮舉補齊
3. 依 thinker 窮舉補齊對應 `philosophy_work`
4. 依 work 窮舉補齊對應 `philosophy_work_text` → **有原文抓原文** → **有原文及譯本就全部都抓**
5. `philosophy_work_text` 逐字逐句理解定義與意涵、設計 schema 入庫、為 qdrant 準備 →（**我停在命門前，AskUserQuestion 被 dismiss，擱置**）
6. 更新全部檔案上傳 GitHub 並做封存點（commit + push + tag）
7. 產生本交接報告

---

## 三、完成事項

### 1. 治權入憲 v1.18.0（commit `5cd760f`）
- **憲章 v1.17.0 → v1.18.0**（git rename + philosophy 段補「版權著作核心精神入庫準則」）
- **CLAUDE v1.12 → v1.13**（#17 補現代版權著作合規路）
- README / 原則精華 同步 v1.18.0 引用（跨檔一致）
- **合規路內容**：現代版權著作全文法律不可抓、**禁 AI 整理／摘要入庫（#1）**；其核心精神須經**真實文獻出處** `philosophy_principle`（引書名/篇章/頁碼）→ `principle_factor_map` 因子假說 → **#14 經濟價值驗證**入庫；**採用由 #14 裁決、非大師權威**。`work_type` / `license` / `source_type` DB CHECK 硬擋 `ai_generated`。

### 2. 素養庫擴充（commit `4854aba`）
| 工具 | 成果 |
|---|---|
| `seed_management_thinkers.py` + `seed_management_thinkers2.py` | 管理各領域 major 思想家 90 位（組織/財務/會計/生產/投資/研發/策略/行銷/HR）|
| `seed_thinker_bibliography.py` | 105 部 major 代表著作**書目**（書名/年份事實 metadata）|
| `seed_master_citations.py` | 現代大師補入學派 proponents + `philosophy_source` citation（合規路顯性化）|
| `seed_thinker_works_dbpedia.py` | DBpedia notableWork 書目（**實證覆蓋極差：701 位僅 1 筆** → 改我知識窮舉）|
| `verify_philosophy_factors.py` | `principle_factor_map` #14 經濟價值回填 37 筆 |

### 3. `philosophy_work_text` 多語言（schema 變更）
- **加 `language` 欄**（VARCHAR(8)），現有 25569 段回填：`en` 25017 / `zh` 552，0 NULL。
- 支援**同一著作並存多語言全文**（原文 + 公版譯本），fetcher 去重鍵 `(work_id, language)`。

### 4. 全文抓取 triage workflow（`philosophy-fulltext-triage`）
- **理解層**（Workflow）：逐部窮盡判別 129 部無全文 work 之**合法公版可得性** + 對抗驗證防幻覺 URL。判準演進：`有原文抓原文` → `原文及譯本全抓`（逐版本依**作者/譯者**卒年獨立判、英譯版權陷阱）。
- **執行層**（`fetch_confirmed_fulltext.py`，本地零 usage）：只抓對抗驗證通過者，Gutenberg / 維基文庫各語言 strip、填 `language`。
- **結果**：129 部 → 107 版權硬邊界 / 10 有公版 / 2 不確定；**confirmed 入庫**：鶡冠子（zh 原文 6 段/18,990 字）、泰勒《The Principles of Scientific Management》（Gutenberg 6435, en 3 段/211,052 字）。

---

## 四、當前 DB 實證狀態（2026-07-02，實查）

| 表 | 列數 |
|---|---|
| `philosophy_thinker` | **861** |
| `philosophy_school` | 23 |
| `philosophy_source` | 44 |
| `philosophy_principle` | 26 |
| `principle_factor_map` | 42 |
| `philosophy_work` | **699**（有全文 572 / 僅書目版權 124）|
| `philosophy_work_text` | **25,578 段**（en 25,020 / zh 558；license 非公版 = **0** ✓）|
| `philosophy_chunk` | 76,795 |
| `philosophy_chunk_embedding` | 76,795（e5-small 384 維）|

> ⚠️ **chunk / embedding 尚未涵蓋本階段新抓 2 部**（鶡冠子 + 泰勒）—— `philosophy_work_text` 已 +9 段但 `philosophy_chunk` 仍 76,795。**新全文需重切塊 + 嵌入才能被檢索**（見待辦）。

---

## 五、命門守護記錄（三個關鍵決策 — 重開機須延續同一判準）

1. **AI 生成「逐字逐句定義與意涵」入庫 → 拒絕（違 #1 命門）**。用戶要對 work_text 逐字逐句生成定義入庫做 qdrant。我 **AskUserQuestion 停下**（未執行任何生成）。關鍵洞察：**真實公版註疏（王弼《老子注》/十三經注疏/《說文解字》字義）才是「逐字逐句定義與意涵」的真兆載體**，非 AI 生成；且**向量化不需中間定義層**（原文 76,795 塊已嵌入即可語意檢索）；向量庫我薦 **pgvector（已在用）** 非另建 qdrant。**此岔路待用戶拍板，未決。**
2. **熊彼得《Capitalism, Socialism and Democracy》archive.org → 排除不抓（#17）**。verify agent 誠實揭露：1942 帶版權聲明、archive.org `possible-copyright-status=None` 未認定 PD。依 CLAUDE #17「license 限 public_domain」+ 命門「公版存疑寧缺勿抓」**排除**。
3. **git add rename 陷阱 → reset 修正**。`git add` 舊檔名（已 rename）報 fatal 會**中斷整個 add 命令**、致其他檔漏 staged（首次 commit 只含憲章純 rename、漏治權內容）。用 `reset --mixed`（不丟工作）重做，`git diff <base> HEAD --stat` 驗證 13 檔全含無遺漏。

---

## 六、待辦 / 接續指引（重開機後）

### 優先待用戶決策
- **逐字逐句定義任務岔路**（第五節第 1 點）：定義來源（真實公版註疏 / 不設定義層直接向量化 / AI 生成〔違憲不可〕）+ 向量庫（qdrant / pgvector）。這是**決策層**，須用戶拍板方向才續。

### 執行層可續（護欄內、本地零 usage）
- **新全文重切塊 + 嵌入**：鶡冠子 + 泰勒（work_id 564 / 663）已入 `philosophy_work_text` 但未進 `philosophy_chunk`；跑既有切塊 + e5-small 嵌入補上，檢索才涵蓋。
- **剩餘 triage verify**：session limit 18:00（Asia/Taipei）觸頂致 2 部 uncertain + 少數 verify 未完成（多屬版權硬邊界）；重置後可用 `Workflow({scriptPath, resumeFromRunId: "wf_eb713121-32e"})` 續跑（完成 agent 走快取）。
- **fetcher confirmed 清單**：`triage` 產出的 confirmed 版本若日後擴充，用 `fetch_confirmed_fulltext.py <confirmed.json>` 抓（已支援多語言 + wikitext）。

### 已知邊界（非缺陷、勿當漏做）
- **124 部僅書目**：現代版權著作（塔雷伯/蒙格/達利歐/波特/杜拉克…），全文法律不可抓，停在書目 metadata 為正確終點。
- **619 位 thinker 無著作**：DBpedia 匯入的冷僻/次要哲學家，多無公版全文且無可靠 major 書目；**不 AI 編造補**（#1）。

---

## 七、環境 / resume 資訊

- **工作目錄**：`/home/hugo/project/augur/`（WSL2）
- **Python**：`PYTHONPATH=src venv/bin/python3 <script>`
- **DB**：PostgreSQL（**跨機獨立、不進 git**；換機須各自建/實查，勿照抄本報告列數為既成）
- **治權 SSOT**：靈魂 v1.4.0 / 原則精華 v1.7.1 / 憲章 **v1.18.0** / CLAUDE **v1.13** / README
- **封存**：tag `philosophy-erudition-expand-20260702`；commit `4854aba`（main，remote 同步）
- **workflow script**：`.../workflows/scripts/philosophy-fulltext-triage-wf_eb713121-32e.js`（run id `wf_eb713121-32e`，可 resume）
- **本階段 scripts**（9 支，`scripts/`）：`fetch_all_thinker_works` / `fetch_chinese_classics` / `fetch_confirmed_fulltext` / `seed_management_thinkers[2]` / `seed_master_citations` / `seed_thinker_bibliography` / `seed_thinker_works_dbpedia` / `verify_philosophy_factors`
- **記憶**：`memory/investment-philosophy-framework.md` + `MEMORY.md` 索引已同步本階段（含三條命門教訓）

---

*守則不變：三敵零容忍（#1 零 AI 幻像 / #8 anti-leakage / #15 誠實）不因任何要求或入憲鬆動；哲學素養層量化零價值、不進預測管線、不取代真實資料預測。*
