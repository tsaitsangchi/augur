# Augur 架構總覽（2 層 × 8 層 × 單一 monorepo 落點）[I]

* **性質**：**[I] 資訊性文件（Informative，非規範性）** —— 給人閱讀的架構總覽／導覽圖，**不創設任何義務、不改動憲章**。凡與本文件牴觸者，一律以《Augur Meta-Constitution》及各層生效規格之 [N] 條款為準（`AUGUR-MC v1.6 §0.6`）。
* **建立日**：2026-07-17
* **維護**：隨各層生效狀態更新；屬 patch 級編輯。最近更新 **2026-07-30**（機械軌：版本／倉別／基建現況事實對齊）。

---

## 一、一句話

Augur 的完整架構是**憲章定義的 8 層（Layer 0–7）**；本文件在其上疊一個**給人看的 2 層視角（概念層／實作層）**，並對映到**單一 monorepo 內之落點**（2026-07-22 前為 `augur`／`augur-constitution` 雙倉，已合倉；2026-07-30 機械軌：README:3 明載「本倉自 2026-07-22 起為 應用 + 治權 合一遠端」）。**8 層是治理的權威結構，2 層是理解的摘要透鏡** —— 後者不取代前者。

## 二、2 層視角（概念 vs 實作）

這個二分並非新創，而是憲章 `§0.6(b)`（概念層獨立性）與 Prime Axiom（**Representation Before Intelligence**：表徵先於智慧）之直接體現：

| 層 | 是什麼 | 對映 8 層 | 倉內落點 |
|---|---|---|---|
| **概念層**（Reality／Representation） | 精神、思想、憲章；世界「是什麼、如何表徵/分類/識別/知道」 | Layer 0–4 | `constitution/`＋`specs/`（原 `augur-constitution`，2026-07-22 併入本倉） |
| **實作層**（Intelligence／Action） | 軟體、模型、程式、資料庫；世界如何被「推理/行動/承載」 | Layer 5–7 | `src/`＋`scripts/`＋基建（原公開倉 `augur`，2026-07-22 起與治權同倉；2026-07-30 機械軌：README:3） |

> **概念層獨立性（`§0.6(b)`）**：概念層（L1–4）規格**不得**引用執行層（L5–7）之構件（特定資料庫、向量庫、Agent 框架、LLM）作為定義依據 —— 這正是「概念先於實作」在憲章中的機器可判落實。

## 三、8 層權威結構（憲章定義）× 對映

```
┌─ 概念層 ── constitution/ + specs/（原獨立倉,已併入） ─────────┐
│ Layer 0  Meta-Constitution   精神/憲章/Prime Axiom+五原則      │
│ Layer 1  World Model         世界有何物（存在宣告）            │
│ Layer 2  Ontology            是什麼類、如何分類、同一性判準      │
│ Layer 3  Identity            identifier 鑄造、生命週期          │
│ Layer 4  Knowledge System    Knowledge 五元組、Confidence 語義  │
├─ 交界（L5/L6 雙面）───────────────────────────────────────────┤
│ Layer 5  Cognitive Kernel    規格→概念層 ／ 推理引擎→實作層     │
│ Layer 6  Agent Runtime       規格→概念層 ／ Agent 引擎→實作層   │
├─ 實作層 ── src/ + scripts/ ＋ 基建 ───────────────────────────┤
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
- 它們的**規格**（推理不變式、人類權威、風險分級）＝**概念層**（[N] 規範，住 `specs/`；原 `augur-constitution` 已併入本倉）。
- 它們的**引擎實作**（實際的 reasoning engine、Agent runtime、排程器、LLM）＝**實作層**（住 `src/`／`scripts/`／基建；2026-07-30 機械軌：合倉後同倉不同目錄）。

因此**不可**把 L5/L6 整個歸入實作層 —— 那會弄丟其規範性。L5 規格自稱「概念層與執行層之交界」即此故。

## 五、現況快照（2026-07-30 機械軌更新：版本與基建現況事實對齊）

| Layer | 規格狀態 | 實體到位 |
|---|---|---|
| L0 Meta-Constitution | ✅ **AUGUR-MC v1.6** 生效（v1.5→v1.6 minor，Steward 裁決第 2026-040 號／AL-2026-044，2026-07-23；**原記 v1.3**） | — |
| L1 World Model | ✅ AUGUR-WM v1.0 生效 | — |
| L2 Ontology | ✅ AUGUR-ONT v1.0 生效（充任 RULING-2026-003） | — |
| L3 Identity | ✅ AUGUR-ID v1.0 生效 | — |
| L4 Knowledge System | ✅ **AUGUR-KS v1.1** 生效（v1.0 首次充任 2026-07-17；minor 升 v1.1 依 RULING-2026-016／AL-2026-019；**原記 v1.0**） | — |
| L5 Cognitive Kernel | ✅ AUGUR-L5 v1.0 生效（**provisional 已解除**：§8.2 條件通過，RULING-2026-029，2026-07-23；復審日曆 2026-10-14；**原記「provisional、§8.2 延後」**） | 引擎未建（沿 2026-07-17 原記，見下註） |
| L6 Agent Runtime | ✅ **AUGUR-L6 v1.2** 生效（v1.0 充任 2026-07-17 裁決 2026-007／AL-2026-011；v1.1 RULING-2026-013；v1.2 RULING-2026-016；**原記 v1.0**） | 引擎未建（沿 2026-07-17 原記，見下註） |
| L7 Infrastructure | ✅ **AUGUR-L7 v1.0** 生效（充任 2026-07-18，裁決第 2026-011 號／AL-2026-014；§8.2 之 L7.90(d) 七項必審 2026-07-19 **條件通過**〔RULING-2026-025〕、**provisional 已解除**，residual 復審 2026-10-14；**原記「v0.1-draft 草擬完成、充任受阻」**） | ✅ 生產 PostgreSQL 17.10（§5 System of Record）＋pgvector 0.8.5、public schema 295 表、67 條非內部 trigger；Qdrant（§5 Semantic Memory）服務在；圖DB／ML 底座仍無 |

> **實體到位之產生指令**（2026-07-30 於當家機 `PC002-S1800` 實跑）：`select count(*) from information_schema.tables where table_schema='public'` → **295**；`select version()` → `PostgreSQL 17.10 (Ubuntu 17.10-1.pgdg24.04+1)`；`select extversion from pg_extension where extname='vector'` → **0.8.5**；`select count(*) from pg_trigger where not tgisinternal` → **67**；`curl -s http://127.0.0.1:6333/collections` → `{"result":{"collections":[{"name":"kn_sent_it_ime5s30b1cd_tn1"}]},"status":"ok"}`（**誠實揭露**：`systemctl is-active augur-qdrant` → `inactive`；實際監聽者為 `ss -ltnp` 所示 pid 306 之 `/home/hugo/project/ttai/.qdrant_server/qdrant`——服務在、但載體非 augur 自有 unit）。憲章十表 2026-07-18 apply 生產、18 條護欄 trigger 在位之逐項證據見 `GROUNDING-MAP.md` §一／§四步 5（快照日 2026-07-17／18）。
>
> **誠實揭露（本次未重驗者）**：L5／L6 之「引擎未建」沿 2026-07-17 原記，本次機械軌未重驗；其是否已由本地審議引擎（`scripts/deliberate.py`）與現行 Agent runtime 部分到位，涉判斷，留後續盤點／Steward 認定。
>
> **史料註（L7 草案「六項／七項」內部不一致已解消）**：前版於此列記 L7 規格第 942／1004／1134 行仍作「六項」而 L7.90(d) 必審清單實為七項。2026-07-30 複驗：`grep -c '六項' specs/INFRASTRUCTURE-SPECIFICATION.md` → **0**、`grep -c '六項' specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md` → **0**、`grep -c '七項' specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md` → **3**、`sed -n '566,600p' specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md | grep -cE '^>\s+\((i|ii|iii|iv|v|vi|vii)\)'` → **7**——生效本與歸檔 draft 現均作「七項」，該不一致不復存在（2026-07-30 機械軌：本地 grep 實跑）。

```
概念層  ████████████████████  L0–L7 全部生效（L5／L7 之 §8.2 為條件通過、復審 2026-10-14）
實作層  ████████░░░░░░░░░░░░  生產 PG 17.10＋pgvector＋Qdrant 在；圖DB／ML 底座、L5/L6 引擎未建
                              （示意圖，非量化指標；數據見上表產生指令）
```

**治權主導混合式**（見 `CONSTITUTIONAL-ROLLOUT-PLAN.md`）之下一步，正是補**實作層/基建**（總綱階段 4/7）：起 System of Record / Semantic Memory / 圖DB / ML 底座。

> ⚠️ **本段原文之硬體基線為已作廢之 GB10（hugo 2026-07-25 宣告、2026-07-27 再確認、2026-07-30 重申該機不存在）；本節規劃於現行載體不可照用。**
> 原文（2026-07-17，保留供史料）：「在 GB10（見 `infrastructure/ENVIRONMENT-SPEC.md`）上起 System of Record / Semantic Memory / 圖DB / ML 底座」。
> **現行載體（雙機並行，兩份 [I] 實測快照為 SSOT，詳值一律以該二檔為準）**：
> - `ops/machines/PC002-S1800.md`——**當家機**；Intel Core i5-10500（6 核／12 緒）、**CPU-only 無 GPU**（本檔作者 2026-07-30 於此機實跑：`hostname` → `PC002-S1800`、`lscpu` → `Intel(R) Core(TM) i5-10500 CPU @ 3.10GHz`、`command -v nvidia-smi` → 無命中）。
> - `ops/machines/DESKTOP-8MQPFS8.md`——**並行使用之第二載體**；AMD Ryzen 5 3600、NVIDIA GTX 1650 4GB、driver 560.94（該檔 2026-07-25 快照記 `nvcc` 12.0；`infrastructure/ENVIRONMENT-SPEC.md` 記 CUDA 12.6 runtime）。**此列數值引自該二文件與 hugo 2026-07-25 宣告、2026-07-27 再確認、2026-07-30 重申，非本檔作者親測**（該機不在當家機可量測範圍）。
>
> **交叉引用更正**：`infrastructure/ENVIRONMENT-SPEC.md` 已於 **2026-07-18 重寫**（其所載即 `DESKTOP-8MQPFS8`），GB10 版歸檔於 `infrastructure/ENVIRONMENT-SPEC-GB10-20260716-superseded.md`；故 `GROUNDING-MAP.md` §一警語／§六-5 所稱「現版整份描述 GB10、待重寫」已為過期記述。（2026-07-30 機械軌：Steward 宣告＋`ls infrastructure/` 實查＋`git log -- infrastructure/`〔c1a9571、8853c55〕）

## 六、治權注意（本文件之地位）

- 本 2 層視角為**組織/呈現透鏡**，可自由使用、不需修憲。
- **憲章之權威結構仍為 8 層**（`§0.5` Layer 對照表、`§0.6` lex superior）。若欲將 8 層改為 2 層之**規範性結構**，屬原則級變更，須 `§8.5` 修憲程序 + Steward 裁決 —— 且不建議（將失去逐層合憲 gate 與依賴序之治理粒度）。
- §8.3 linter（`tools/constitution_lint/`）以 8 層之逐層合規聲明為 gate；2 層無此機制。

---

*本文件為 [I] 導覽圖，權威悉依憲章與各層生效規格 [N] 條款。*
