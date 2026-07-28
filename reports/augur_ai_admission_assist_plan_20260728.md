# 本地 AI 入庫預審協助（ADM-AI-ASSIST）— 建議／打分／排隊，approve／activate 唯人

> **性質**：[I] 短計畫（#20 計畫先行；本輪**零實作**）  
> **日期**：2026-07-28  
> **觸發**：Steward「如何由本地 AI 最佳化自我判定入庫」＋定錨「approve／activate 仍應唯人」  
> **位階**：執行層／工具記憶；**不改** [N]；零 FinMind／FRED  
> **建議拍板碼**：`ADM-AI-ASSIST-PLAN`（拍板＝可開 S0 設計＋DDL 草案；**≠**授權 AI 改審批態）

---

## 0. 一句定錨

**自我判定＝對 proposed 來源／staging 候選寫 `recommend_score`＋`reason`＋audit 軌跡，供人一鍵採納或駁回——本地 AI 永不把 `approve`／`activate` 寫成終態通過。**

---

## 1. 現況診斷（code 親查；本輪 DB 連線拒收，量級另日補）

| 層 | 現況 | AI 建議欄？ |
|---|---|---|
| **L1 機械閘** | `admission.admission_gate` 四件 fail-closed（source=`active`、license 白名單、`owned_local⇒local_private`、`source_type≠ai_generated`）；staging BEFORE INSERT 非 active 拒寫；promote JOIN 非 active 不晉升 | 無（正確＝純機械） |
| **來源審批** | `curation.HUMAN_ONLY={approve,activate,resume,reopen}`；TTY＋superuser；`system=True` 觸升級必紅 | **無**獨立 AI 欄；`review_log.reason` 可寫字但無結構化 score |
| **SRC-AUTO** | `auto_review_sources.py`＝人簽六／七謂詞內機械 auto-approve（`actor=auto_rules_v1`）；計畫 §L-A／L-V 本地 AI 諮詢／只嚴不鬆＝**P4 未接線** | 諮詢層**未落地** |
| **staging／promote** | `knowledge_staging`：`status∈{pending,promoted,rejected}`＋payload／provenance；哲學域 work 等人審，七類 item 可機械 promote | **無** `recommend_*`／`ai_assist` 欄 |
| **admin `/gov`** | 唯讀分佈＋FT-COV 終態桶＋近期 review_log；升級＝copy-ready **CLI**，web 零寫 | **無**建議分／一鍵採納 UI |
| **ATA（KH-XDOM）** | `advance_knowledge_terminal.py`：已入庫後 pending→answerable｜terminal_blocked；禁 HUMAN_ONLY | 正交（見 §4） |
| **deliberate** | 本地 qwen 提可驗宣稱→oracle；**LLM 意見零證據力** | 精神對齊：AI 只產輔助軌跡 |

**結論**：機械閘與「唯人升級」已硬；缺的是**入庫前／來源審**的結構化本地 AI 預審層＋人裁隊列 UI——不是再做一條自動 activate。

---

## 2. 三層架構（可執行）

```
候選（proposed 源／staging pending／哲學待審）
  │
  ├─ L1 機械閘（既有，零 LLM）
  │     license／格式／admission_gate／probe 前置／SRC-AUTO 謂詞（若適用）
  │     不過 → 誠實拒／留桶；AI 不得覆寫通過
  │
  ├─ L2 本地 LLM 建議（新；零裁決權）
  │     qwen3:4b（MCP／批次）或 8b（advisor 人讀摘要）
  │     輸出：recommend_score∈[0,1] ＋ reason≤N 字 ＋ flags
  │           （相關性／疑重複／license 風險詞／建議 domain／hold_for_human）
  │     寫入：audit 表或 staging JSONB／review_log action='assist'（見 §3）
  │     方向鎖：可標 hold（只嚴不鬆）；**不可**放行 approve／activate
  │
  └─ L3 人裁（Sole Steward）
        TTY `review_knowledge_source.py --approve/--activate`
        或未來 admin「採納建議」＝仍呼叫同一 HUMAN_ONLY 路徑（身分閘不變）
```

| 層 | 做什麼 | 不做什麼 |
|---|---|---|
| **L1** | license／格式／active 源／謂詞可驗項 | 不把 LLM 分數當閘通過條件 |
| **L2** | 打分＋理由＋風險旗＋建議 domain；排隊供掃 | 不改 `approval_status`；不冒充人簽 |
| **L3** | 唯人 `approve`／`activate`（及 resume／reopen） | 不委派給 timer／AI／非 TTY |

**與「自我判定」語意對齊**：最佳化＝**預審品質與吞吐**（人看建議比裸掃 3k＋pending 快），不是模型自封入庫官。利益衝突（模型選自己教材）→ 分數**永不**進 L1／永不觸發升級；抽核＋熔斷同 SRC-AUTO 精神。

---

## 3. (a) Schema／(b) 程式規畫（拍板後才動）

### 3.1 建議資料落點（二擇一或並存；S0 定案）

| 選項 | 表／欄 | 用途 |
|---|---|---|
| **A（偏來源）** | `knowledge_source_review_log` 擴 `action` CHECK 加 `'assist'`（或 `'ai_pre_review'`）；`reason`＝JSON 字串含 score／flags／model／prompt_hash | 與既有審批軌同址；gov 近期 log 可顯示 |
| **B（偏 staging）** | `knowledge_staging` 加可空欄：`assist_score real`、`assist_reason text`、`assist_flags jsonb`、`assist_at`、`assist_model text` | pending 隊列排序／篩選 |
| **C（帳本）** | 新表 `knowledge_admission_assist`（target_kind∈{source,staging}、target_id、score、reason、flags、actor=`local_ai_v1`、created_at） | 多輪重跑冪等、不污染 status |

**硬約束**：任一選項的 writer **禁止** `UPDATE … approval_status`／呼叫 `curation.transition(..., approve|activate)`。selftest 鎖同 ATA。

### 3.2 Python（建議名；拍板後建）

| 檔 | 職責 |
|---|---|
| `scripts/assist_admission_review.py`（新） | 批次預審：讀 proposed／pending 池 → L1 快篩 → 本地 Ollama 產 score／reason → 寫 assist 軌；`--dry-run`／`--limit`／`--selftest`；預設零寫 |
| `scripts/migrate_admission_assist_ddl.py`（新） | DDL 冪等＋誠實閘 |
| 擴 `serve_admin_console.py` `/gov` 或 `/assist` | **唯讀**建議分桶＋copy-ready「依建議 approve」CLI；可選「標記已讀／駁回建議」（不觸升級） |
| 複用 | `admission_gate`、`probe_knowledge_source`、`local_summarize`／Ollama；**不**複寫 SRC-AUTO 謂詞引擎 |

### 3.3 排程

- systemd user timer（如每日低峰）：`assist_admission_review.py --limit N`  
- 共用 `/tmp/augur_llm.lock`（與既有 LLM 單槽）  
- **禁** timer 呼叫 `review_knowledge_source.py --approve/--activate`

---

## 4. 與鄰案分工（防撞名）

| 案 | 邊界 |
|---|---|
| **本計畫 ADM-AI-ASSIST** | **入庫前／來源審**：建議與排隊 |
| **SRC-AUTO** | 人簽**機械**謂詞可 auto-approve；其 L-A／L-V＝本計畫可**承接／合併**為同一 assist writer（避免兩套摘要） |
| **ATA／KH-XDOM** | **已入庫後**終態覆蓋（promote／全文／句／embed）；永不 approve／activate |
| **FT-COV／全文三軌** | license 可答終態；本計畫不鬆 CHECK、不洗 blocked |
| **NHC-keep** | 提示／域別名不 hardcode；flags 詞表若策展→住 DB |
| **deliberate** | 高爭議單件可 escalate 人裁佇列；assist 批次不冒充 oracle 裁決 |

---

## 5. 分階段・驗收・停損

| 階段 | 內容 | 驗收 | 停損 |
|---|---|---|---|
| **S0** | 拍板本檔＋定 schema 選項 A/B/C；live 池量補測（proposed／pending） | 拍板碼＋選項一字 | 未拍零 DDL |
| **S1** | DDL＋`assist_admission_review.py` dry-run／selftest（禁 HUMAN_ONLY 紅） | selftest 綠；dry 產出分數樣本 | — |
| **S2** | 有界 `--apply --limit`＋gov 唯讀建議列 | 抽核 20：人與建議方向一致≥閾值（另定） | 兩輪不過→關 timer、分數降級展示 |
| **S3** | timer＋人裁工作流（copy-ready／可選一鍵仍走 TTY 身分） | 零次 AI 觸發 approve／activate（audit 掃描） | 任一違規→全域暫停 assist |

**明確不做**：LLM 放行權；AI 改 license／新域自動 active；繞 probe；解凍市場 API；改憲章 [N]；把 assist_score 寫進 admission_gate。

---

## 6. 建議拍板句

> 拍 **`ADM-AI-ASSIST-PLAN`**：採納本檔三層設計（L1 機械 → L2 本地 AI 僅建議／打分／audit → L3 唯人 approve／activate）；允許 S0–S1 開 DDL＋預審 script（預設 dry-run）；**禁止**任何路徑讓本地 AI／timer 執行 approve／activate。SRC-AUTO 之 L-A／L-V 與本 assist **合併單一 writer**，避免雙軌。

（若只要「先寫進 SRC-AUTO P4、不另立案」→ 回 **`SRC-AUTO-LAV-go`**，範圍收窄為來源 review_log 諮詢層，不含 staging 隊列。）
