# Augur 架構總覽（2 層 × 8 層 × 2 Repo 對映）[I]

* **性質**：**[I] 資訊性文件（Informative，非規範性）** —— 給人閱讀的架構總覽／導覽圖，**不創設任何義務、不改動憲章**。凡與本文件牴觸者，一律以《Augur Meta-Constitution》及各層生效規格之 [N] 條款為準（`AUGUR-MC v1.3 §0.6`）。
* **建立日**：2026-07-17
* **維護**：隨各層生效狀態更新；屬 patch 級編輯。

---

## 一、一句話

Augur 的完整架構是**憲章定義的 8 層（Layer 0–7）**；本文件在其上疊一個**給人看的 2 層視角（概念層／實作層）**，並對映到**2 個 GitHub repo**。**8 層是治理的權威結構，2 層是理解的摘要透鏡** —— 後者不取代前者。

## 二、2 層視角（概念 vs 實作）

這個二分並非新創，而是憲章 `§0.6(b)`（概念層獨立性）與 Prime Axiom（**Representation Before Intelligence**：表徵先於智慧）之直接體現：

| 層 | 是什麼 | 對映 8 層 | 對映 repo |
|---|---|---|---|
| **概念層**（Reality／Representation） | 精神、思想、憲章；世界「是什麼、如何表徵/分類/識別/知道」 | Layer 0–4 | `augur-constitution`（私有） |
| **實作層**（Intelligence／Action） | 軟體、模型、程式、資料庫；世界如何被「推理/行動/承載」 | Layer 5–7 | `augur`（公開）＋基建 |

> **概念層獨立性（`§0.6(b)`）**：概念層（L1–4）規格**不得**引用執行層（L5–7）之構件（特定資料庫、向量庫、Agent 框架、LLM）作為定義依據 —— 這正是「概念先於實作」在憲章中的機器可判落實。

## 三、8 層權威結構（憲章定義）× 對映

```
┌─ 概念層 ── augur-constitution repo ───────────────────────────┐
│ Layer 0  Meta-Constitution   精神/憲章/Prime Axiom+五原則      │
│ Layer 1  World Model         世界有何物（存在宣告）            │
│ Layer 2  Ontology            是什麼類、如何分類、同一性判準      │
│ Layer 3  Identity            identifier 鑄造、生命週期          │
│ Layer 4  Knowledge System    Knowledge 五元組、Confidence 語義  │
├─ 交界（L5/L6 雙面）───────────────────────────────────────────┤
│ Layer 5  Cognitive Kernel    規格→概念層 ／ 推理引擎→實作層     │
│ Layer 6  Agent Runtime       規格→概念層 ／ Agent 引擎→實作層   │
├─ 實作層 ── augur code repo ＋ 基建 ───────────────────────────┤
│ Layer 7  Infrastructure      python · git · docker ·          │
│                              postgresql(System of Record) ·   │
│                              qdrant(Semantic Memory) · 圖DB ·  │
│                              LLM/模型 · ML 運算底座            │
└──────────────────────────────────────────────────────────────┘
        ▲ constrains（§0.6 lex superior：上層約束下層）
```

**技術棧落點**：你列的 `python`／`git`／`docker`／`postgresql`／`qdrant` 全部屬 **Layer 7**。其中 `postgresql`＝§5 之 System of Record、`qdrant`＝§5 之 Semantic Memory（向量庫）。

## 四、L5/L6 是雙面的（重要）

Layer 5（Cognitive Kernel）、Layer 6（Agent Runtime）**橫跨兩層**：
- 它們的**規格**（推理不變式、人類權威、風險分級）＝**概念層**（[N] 規範，住 `augur-constitution`）。
- 它們的**引擎實作**（實際的 reasoning engine、Agent runtime、排程器、LLM）＝**實作層**（住 `augur`/基建）。

因此**不可**把 L5/L6 整個歸入實作層 —— 那會弄丟其規範性。L5 規格自稱「概念層與執行層之交界」即此故。

## 五、現況快照（概念層遙遙領先、實作層幾乎空白）

| Layer | 規格狀態 | 實體到位 |
|---|---|---|
| L0 Meta-Constitution | ✅ v1.3 生效 | — |
| L1 World Model | ✅ AUGUR-WM v1.0 生效 | — |
| L2 Ontology | ✅ AUGUR-ONT v1.0 生效 | — |
| L3 Identity | ✅ AUGUR-ID v1.0 生效 | — |
| L4 Knowledge System | ✅ AUGUR-KS v1.0 生效 | — |
| L5 Cognitive Kernel | ✅ AUGUR-L5 v1.0 生效（provisional，§8.2 延後） | ❌ 引擎未建 |
| L6 Agent Runtime | ✅ AUGUR-L6 v1.0 生效（**含 §8.2 實質人類審查**；裁決 2026-007／AL-2026-011） | ❌ 引擎未建 |
| L7 Infrastructure | 🔄 AUGUR-L7 v0.1-draft 草擬完成、充任受阻（待 §8.2 實質審查；規格自訂 L7.90(d) 必審清單 (i)–(vii) **共七項**〔產生指令：`sed -n '566,600p' specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md \| grep -cE '^>\s+\((i\|ii\|iii\|iv\|v\|vi\|vii)\)'` → 7；第 (vii) 項 T-L7-13 自身即為依 §8.1 之書面裁決聲請。該規格第 942／1134 行仍作「六項」，為 L7 草案之內部不一致，另案〕） | ⚠️ 僅測試 PostgreSQL；qdrant/圖DB/ML 皆無 |

```
概念層  ████████████████████  L0–L6 生效、L7 草擬待充任  ← 遙遙領先
實作層  █░░░░░░░░░░░░░░░░░░░  僅 1 個測試 PostgreSQL   ← 幾乎空白
```

**治權主導混合式**（見 `CONSTITUTIONAL-ROLLOUT-PLAN.md`）之下一步，正是補**實作層/基建**（總綱階段 4/7）：在 GB10（見 `infrastructure/ENVIRONMENT-SPEC.md`）上起 System of Record / Semantic Memory / 圖DB / ML 底座。

## 六、治權注意（本文件之地位）

- 本 2 層視角為**組織/呈現透鏡**，可自由使用、不需修憲。
- **憲章之權威結構仍為 8 層**（`§0.5` Layer 對照表、`§0.6` lex superior）。若欲將 8 層改為 2 層之**規範性結構**，屬原則級變更，須 `§8.5` 修憲程序 + Steward 裁決 —— 且不建議（將失去逐層合憲 gate 與依賴序之治理粒度）。
- §8.3 linter（`tools/constitution_lint/`）以 8 層之逐層合規聲明為 gate；2 層無此機制。

---

*本文件為 [I] 導覽圖，權威悉依憲章與各層生效規格 [N] 條款。*
