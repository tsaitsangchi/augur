---
status: executed_option_A
series: advisor_integration
depends_on:
  - reports/augur_advisor_predict_as_knowledge_plan_20260805.md
  - audits/ADVISOR-PRED-KH-AUTOREL-TOPN-EXECUTED-20260805.md
  - audits/ADVISOR-PICKS-SKIP-A-EXECUTED-20260805.md
---

# 顧問：有 picks 時少載重檢索（減 8b↔embed 互擠）plan-first（2026-08-05）

> **性質**：[I] plan-first（波次 A · 項 10）。  
> **✅ Phase 1 EXECUTED**：Steward `picks_skip_A-go`＋`skip_evo_too` → `audits/ADVISOR-PICKS-SKIP-A-EXECUTED-20260805.md`。  
> **觸發**：11GB 機上 `advise()` 對 PRED-KH／選股題仍先 `retrieve_all`（SentenceTransformer／pgvector／或 Qdrant）→ 與已載 `qwen3:8b`（~6GB）互擠 → `llama-server process no longer running`／「(無回覆)」。  
> **self-reported（#32a）**。

---

## 0. 一句話

**真兆 picks／prob_note 已自足時，檢索降為可選輕量或跳過，避免為「哲學引文」把聊天模型擠死——不鬆 guard、不略過數字白名單。**

---

## 1. 現況碼路徑（理解錨）

`advise()`（有 `PredictionPayload.picks` 時）：

1. **不**再短路方向拒答（PRED-KH 已做）  
2. **仍**呼叫 `retrieve_all` → encode query（本機 embed 模型）→ 再 `llm_fn`（8b）  
3. guard 仍要求數字 ∈ `payload.numbers()`  

故瓶頸＝步驟 2 的 **雙模型同駐**，非 payload 建構。

---

## 2. 選項

| 代號 | 行為 | 利 | 險 |
|---|---|---|---|
| **A skip_retrieve_on_picks** | `has_picks` → `citations=[]`，直組 prompt＋LLM | 記憶體最省；PRED-KH 主路徑穩 | 少哲學／KH 旁證（題本即預測知識） |
| **B light_lex_only** | 跳向量檢索；僅 lexicon／定義詞若有 | 保留定義閘 | 仍可能觸輕量 DB |
| **C retrieve_after_llm** | 先 LLM 再可選補引文 | 複雜；不推 | 雙次往返 |
| **D status_quo** | 不改 | — | 11GB 續撞 |

**推薦**：**A**（預測通道題＝picks 即 context；KH 空引文仍走主路徑——與既有 `has_picks` 豁免 empty-decline 一致）。

---

## 3. (a)(b) schema／程式

| 層 | 內容 |
|---|---|
| schema | **無新表** |
| python | `advise.py`：若 `has_picks` 且非 Mode B／非 lex 強制 → 跳過 `src_fn(query)`／translate；`citations=[]`；其餘 guard／prompt／evolution 塊策略另裁（建議 evolution_md 對 picks 題 **可關** 以再省 IO——可選開關） |
| 測試 | `relevance`／`advise` selftest：餵假 payload picks → mock retrieve **不得被呼叫**（#35 下游絆線） |
| 服務 | 改後 `systemctl --user restart augur-advisor`（#7） |

---

## 4. 硬邊界

- **不**因省記憶體放寬 guard 數字／出處閘  
- **不**让 empty retrieval decline 蓋掉 picks（既有不變式）  
- 知識／哲學純題（無 picks）→ **仍**全速檢索  
- FZ／API／SIM 無關  

---

## 5. 分階段

| 階段 | 產出 | 另授權？ |
|---|---|---|
| Phase 0（本檔） | Steward 選 A／B／D | 呈裁 |
| Phase 1 | 最小 diff＋selftest 驗紅＋重啟＋PREP-KH smoke | **明示 GO** |
| 驗收 | UI「2330…」不再因 embed 換死 8b（誠實：仍可能因別因 OOM） | — |

---

## 6. 請 Steward 裁示

1. **picks_skip_A-go** — 核准選項 A 實作（另句開工）  
2. **picks_light_B-go** — 選 B  
3. **keep_D** — 維持現況  

*定版草稿（2026-08-05 波次 A）。*
