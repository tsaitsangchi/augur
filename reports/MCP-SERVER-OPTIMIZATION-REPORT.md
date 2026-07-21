# Augur MCP Server 最佳化報告 [I]

* **性質**：[I] 資訊性報告（不創設義務；權威悉依憲章與各層生效規格之 [N] 條款）
* **報告日**：2026-07-21
* **範圍**：本專案（憲章 repo ＋ code repo）之 token 使用診斷、既有 MCP 相關工作之評估、與 MCP server 建置建議
* **診斷方法**：實測檔案尺寸、實測本 session 之 workflow token 用量、盤點既有 `mcp/` 原型與設計文件、比對 Claude Code 之 MCP 載入機制

---

## 〇、一句話結論

**本專案最大的 token 支出不是工具，是「整檔讀規格」與「workflow 扇出」**。最有效的 MCP 投資是一支**條款級查詢 server（constitution-mcp）**，讓模型以每次數百 token 的小工具呼叫取代數萬 token 的整檔讀取；「自動切換」則**不必自建** —— Claude Code 的專案級 `.mcp.json` 作用域＋工具 schema 延遲載入（ToolSearch）已原生提供。既有 `mcp/` 目錄是 **Multi-Channel Proxy（提示詞路由器）**，與 Model Context Protocol 同名異物，其自估效益（約 2k tokens／月）不足以構成優先投資，且其合規結果快取與本專案「綠燈假象」之治理教訓相衝。

---

## 一、名詞澄清：本 repo 現存兩種「MCP」

| | `mcp/` 目錄（現存原型） | Model Context Protocol（本報告建議） |
|---|---|---|
| 全名 | **M**ulti-**C**hannel **P**roxy | **M**odel **C**ontext **P**rotocol |
| 是什麼 | FastAPI 路由器：把 prompt 依分類分流至 Ollama 本地模型／Redis 快取／`claude` CLI | Anthropic 開放協定：向 Claude Code session 提供工具（tools）與資源（resources）的 server |
| 服務對象 | **腳本／CI** 中的 `claude -p` 呼叫 | **互動式 Claude Code session** 本身 |
| 省 token 機制 | 快取重複 prompt；廉價查詢改走本地小模型 | 模型改用小工具查詢，**不必將大檔讀入 context** |
| 現況 | `mcp/`（router/classifier/cache/local_llm/claude_cli/logger，未追蹤）＋ `tools/constitution_lint/mcp_client.py` ＋ `reports/mcp_design_overview.md` | 尚未建置；`.mcp.json` 不存在 |

兩者可並存，但解決的是不同問題。本報告聚焦後者；前者之評估見 §五。

---

## 二、token 支出診斷（實測）

### 2.1 支出排行

| 排名 | 支出項 | 實測量級 | MCP 可否解 |
|---|---|---|---|
| 1 | **Workflow 子代理扇出** | 每次 47 萬–115 萬 tokens（本 session 四次 workflow 實測：1,156k／540k／602k／475k） | ❌ 非 MCP 問題；解法為 effort 分級、縮小 scope、`resumeFromRunId` 快取 |
| 2 | **整檔讀取規格／憲章** | 見 2.2；單次讀 L7 規格估 6–9 萬 tokens | ✅ **本報告主標的** |
| 3 | **跨 session 重讀** | 每個新 session 重讀 HANDOFF／憲章／規格各一輪 | ✅ 同上（條款級查詢＋既有摘要報告） |
| 4 | 工具 schema 載入 | 本 session 掛 5 個 MCP server、50+ 工具 | ✅ **已由 harness 解決**（延遲載入，見 §四） |

### 2.2 大檔實測（token 估算以 CJK 約 3 bytes/字、約 1 字/token 概算）

| 檔案 | 大小 | 整檔讀取估算 |
|---|---|---|
| `specs/INFRASTRUCTURE-SPECIFICATION.md` | 267 KB／1,137 行 | ~60,000–90,000 tokens |
| `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` | 138 KB／1,059 行 | ~35,000–46,000 tokens |
| `specs/WORLD-MODEL-SPECIFICATION.md` | 117 KB／948 行 | ~30,000–39,000 tokens |
| `specs/AGENT-RUNTIME-SPECIFICATION.md` | 105 KB／542 行 | ~26,000–35,000 tokens |
| `specs/IDENTITY-SPECIFICATION.md` | 99 KB／797 行 | ~25,000–33,000 tokens |
| `specs/ONTOLOGY-SPECIFICATION.md` | 87 KB／634 行 | ~22,000–29,000 tokens |
| `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | 77 KB／540 行 | ~19,000–26,000 tokens |
| `constitution/META-CONSTITUTION.md` | 54 KB／690 行 | ~14,000–18,000 tokens |

**典型浪費場景**（本 session 及平行 session 歷史中反覆出現）：

* 為了核對**一條**條款的原文標籤（如 `P4.E8` 的括號名），讀入半份憲章（~8k tokens）——而答案只有一行（~30 tokens）。
* 對抗審查 agent 各自整檔讀同一份規格：一輪 3 個 judge × 讀 L7 全文 ≈ 20 萬+ tokens，其中大量是重複載入。
* 新 session 開場「摸清現況」讀 HANDOFF ＋ 憲章 ＋ 2–3 份規格 ≈ 10–15 萬 tokens。

---

## 三、建議方案：`constitution-mcp`（條款級查詢 server）

### 3.1 核心洞察：最難的部分已經寫完了

`tools/constitution_lint/mc_clauses.py` 經三輪硬化，已能：

* 枚舉憲章全部 **102 條 [N] 條款**（含 §2.1–§2.11 定義、§5.1–§5.6 架構角色之 list-item 體例）
* 抽出每條之**原文標籤資料**（`code → {paren_name, full_forms, text, line}`）
* 依 front-matter `upper-specs` 解析**上層規格條款標籤**（WM./ONT./ID./KS./L5./L6./L7.）

MCP server 只是給這套能力加一層薄薄的協定外殼（官方 `mcp` Python SDK，stdio transport，約 100–150 行）。

### 3.2 建議工具集（七支，全部唯讀）

| 工具 | 輸入 → 輸出 | 取代的讀取 | 單次節省估算 |
|---|---|---|---|
| `get_clause` | `"P4.E1"` → 該條原文＋標籤＋行號 | 讀半份憲章 | ~8k → ~0.2k |
| `search_clauses` | 關鍵詞 → 命中條款代號＋摘句清單 | grep＋人工翻找＋讀上下文 | ~5k → ~0.3k |
| `get_spec_clause` | `"KS.42"` → 該條規格原文 | 讀 1/3 份規格 | ~12k → ~0.3k |
| `lint_compliance` | 規格路徑 → 結構化結果（error/warning/info 逐筆） | Bash 執行＋模型解析原始輸出 | ~2k → ~0.5k |
| `layer_status` | （無）→ 八層生效狀態＋版本＋裁決號 | 讀 HANDOFF＋AMENDMENT-LOG | ~6k → ~0.3k |
| `get_ruling` | `"2026-025"` → 裁決主文摘要＋依據 | 讀整份裁決 | ~3k → ~0.4k |
| `list_amendments` | 範圍 → AL 條目清單 | 讀 AMENDMENT-LOG | ~4k → ~0.3k |

**設計紀律**（承接本專案治理教訓）：

1. **全部唯讀** —— server 不提供任何寫入／修改工具。修規格是 Steward §8.5／§8.6 之權，不給 Agent 一條經 MCP 的旁路。
2. **不快取合規結果** —— `lint_compliance` 每次實跑。本專案已三度實證「陳舊綠燈」之害（linter 三輪 error 0 而實質錯誤並存），在合規檢查前加 TTL 快取是自造第四輪。
3. **回傳附出處** —— 每筆回傳附 `file:line`，模型引用時可回溯，不製造「無 Source 之 Knowledge」（呼應 §P4.E1 精神，雖本工具屬 [I] 輔助非規範標的）。
4. **失敗發聲** —— 解析失敗回 error，不靜默退回近似答案（承接 B9「靜默降級」教訓）。

### 3.3 效益估算（誠實標註為估算）

以本 session 型態的治理工作日（2–3 輪審查＋若干條款核對）概算：

| 場景 | 現況 | 有 constitution-mcp | 節省 |
|---|---|---|---|
| 條款核對 ×20 次/日 | ~160k | ~4k | **~156k/日** |
| 新 session 開場摸底 | ~100–150k | ~10k（layer_status＋按需查詢） | **~90–140k/次** |
| 對抗審查 judge 引用條款 | 每 judge 整檔讀 | judge 亦可經 ToolSearch 用 MCP 工具 | 視 workflow 設計，潛在 50%+ |

**注意**：整檔讀取不會歸零 —— 需要「逐列重建整張矩陣」這類全文工作時，讀全檔仍是對的。MCP 省的是**點查詢被迫變成整檔讀**的那部分，而那部分是日常的大宗。

### 3.4 註冊與「自動切換」

專案根建 `.mcp.json`：

```json
{
  "mcpServers": {
    "constitution": {
      "command": "python3",
      "args": ["-m", "tools.constitution_mcp"],
      "cwd": "/home/giga/augur"
    }
  }
}
```

**「自動切換」不必自建**，Claude Code 原生兩層機制已覆蓋：

1. **專案作用域**：`.mcp.json` 只在進入本專案時載入；離開專案即卸載。憲章工具不會污染其他專案的 context。
2. **延遲載入（deferral）**：session 起始只載工具名，完整 schema 於首次需要時經 ToolSearch 取回。掛著不用 ≈ 零閒置成本。（本 session 實例：50+ 個 chrome／visualize 等工具即以此機制掛載。）

若日後 code repo 也要專屬工具（如 DB schema 查詢、AUD 審計狀態），在 `/home/giga/augur-code-work/.mcp.json` 另註冊一支 —— 兩個 repo 各自載各自的，這就是專案級「切換」的全部。

### 3.5 建置工作量

| 項 | 工時估 |
|---|---|
| server 骨架（官方 `mcp` SDK，stdio） | ~0.5 小時 |
| 七支工具（多為 `mc_clauses.py`／linter 之轉接） | ~1 小時 |
| selftest（含「失敗發聲」突變鎖，比照 linter 慣例） | ~0.5 小時 |
| `.mcp.json` ＋ README ＋ 實測 token 對比 | ~0.5 小時 |
| **合計** | **~2.5 小時** |

---

## 四、既有環境事實（為何不必自建切換層）

* 本 session 實測：5 個 MCP server（chrome／session／visualize／registry／scheduled-tasks）共 50+ 工具以**延遲載入**掛載 —— 未用到的工具只佔一行名稱，schema 不進 context。
* Workflow 子代理可經 ToolSearch 取用 session 之 MCP 工具 —— constitution-mcp 建好後，對抗審查 judge 亦可受益。
* 結論：**「減少 token」的正解不是做一個會切換 MCP 的 meta 層，而是把大檔讀取改造成小工具查詢** —— 切換與閒置成本問題，平台已解。

---

## 五、既有 `mcp/`（Multi-Channel Proxy）評估

| 面向 | 評估 |
|---|---|
| 效益 | 其設計文件自估**約 2k tokens／月（≈ $0.20）** —— 相對 §二之支出量級（單一 workflow 即 50 萬+），不構成優先投資 |
| 風險一：合規快取 | `compliance` 類回應設 24h TTL 快取 —— 與本專案「綠燈假象」教訓正面相衝。**若保留此原型，合規類應改為永不快取** |
| 風險二：本地小模型 | `quick` 類由 Ollama（qwen3:4b）回答憲章解釋 —— 4B 模型對 102 條條款之轉述風險，正是 WM.44-LABEL 所撲滅的「轉述冒充原文」病灶之新入口。若保留，其回答應強制附 `(local answer)` 標記且禁止進入任何治理文書 |
| 風險三：目錄撞名 | `mcp/` 撞名官方 Python SDK 套件 `mcp` —— 建置 constitution-mcp 需 `import mcp` 時，本地目錄優先於 site-packages，**必炸**。建議改名 `augur_proxy/` |
| 合理用途 | CI 中重複的報告生成類呼叫（非合規判定）可受益於快取；作為個人問答的本地分流亦無害 |

**建議處置**：目錄改名 `augur_proxy/`；合規類永不快取；不列入 token 最佳化主線。

---

## 六、附帶安全事件（已收口，記錄供稽核）

2026-07-21 檢查發現 commit `aecb515` 曾將工作目錄打包之 `augur-constitution.zip`（12MB）提交入 repo，**其內含 `.env`（存有 GITHUB_TOKEN）** —— `.gitignore` 擋得住 `.env`，擋不住裝著它的 zip。處置（同日完成）：

1. zip 自 HEAD 移除（`fab0bf6`）＋ `.gitignore` 增列 `*.zip`、`.venv-mcp/`
2. Steward 已於 GitHub 撤銷該 token（經 API 實測 401 確認失效；歷史中殘留即成廢字串，未改寫歷史 —— 多 session 並行下 force-push 風險大於收益）
3. `.env` 中死條目已清除；日常操作由 gh CLI OAuth 覆蓋，**無須重建 PAT**（如需推 `.github/workflows/` 再以 `gh auth refresh -s workflow` 補 scope）

**教訓**：凡「打包工作目錄」之產物一律視同含密（zip／tar 內之 gitignored 檔不受 .gitignore 保護）。

---

## 七、建議執行順序

| # | 動作 | 產出 |
|---|---|---|
| 1 | `mcp/` → `augur_proxy/` 改名（避 SDK 撞名） | 一次 `git mv` |
| 2 | 建 `tools/constitution_mcp/`（七工具＋selftest） | ~2.5 小時 |
| 3 | `.mcp.json` 註冊＋新 session 實測 token 對比 | 實測數據回填本報告 §3.3 |
| 4 | （可選）code repo 側 `.mcp.json` 規劃 | 另案 |
| 5 | （可選）workflow 模板改為 judge 優先用 MCP 工具查條款 | 扇出成本下降 |

---

*本報告為 [I] 資訊性文件。所引 token 數字除標明「實測」者外均為估算；建置後應以實測回填。*
