---
status: draft
series: s3_features
depends_on:
  - reports/augur_s3_features_for_market_model_families_20260804.md
  - audits/S3-WAVE-B-EXECUTED-20260804.md
  - audits/S3-WAVE-D-EXECUTED-20260804.md
  - audits/S3-WAVE-C-EXECUTED-20260804.md
---

# S3-Wave-E／A–D 殘帳 — gated 組＋已落地未晉升 plan-first（2026-08-05）

> **性質**：[I] plan-first（憲章第六部；CLAUDE #20）。**預設不 build** 組 14–16；先把「下一特徵波」定錨為**殘帳治理＋gated 紀律**，避免空 GO 假推進。
> **觸發**：S3-A／B／C／D 皆已 GO＋EXECUTED；master list 下一波名＝**S3-E（組 14–16）**，同時 A–D 留下可操作殘帳（候選未晉升、股級 macro SKIP、GNN 無消費端等）。
> **self-reported（#32a）**。

---

## 0. 一句話

**S3-E 字面＝組 14–16（Alt-NLP gated／LOB N/A／RL state missing）——多數應維持 gated／N/A，不是下一波放量 build；真正高槓桿的「特徵下一手」多半是 A–D 殘帳（Wave-B 0/4 未提拔、圖邊無 GNN 消費、估值 winsorize 等），須與 E 分開授權。**

---

## 1. 波次現況地圖

| 波 | 組 | 狀態 |
|---|---|---|
| S3-A | 1–7 | EXECUTED（覆蓋／契約） |
| S3-B | 8–9 | EXECUTED；**4 候選多 seed 0 提拔**；股級 macro **SKIP** |
| S3-C | 10–11 | EXECUTED（查核：既有 oracle 已對齊） |
| S3-D | 12–13 | EXECUTED（序列窗 library＋`stock_graph_edge` 13,021） |
| **S3-E** | **14–16** | **未 GO**；master list 預設 gated／N/A／missing |

---

## 2. 兩條正交軌（勿綁成一 GO）

### 軌 α — S3-E 字面（組 14–16）

| 組 | 預設裁決 | 若要動所需 |
|---|---|---|
| 14 Alt／NLP／LLM-derived | **gated** | Steward 明示＋license＋提拔閘；禁 AI 摘要入庫 |
| 15 LOB L2 | **N/A** | 真來源基建（現無） |
| 16 RL state／portfolio context | **missing** | 專用契約＋另尺（≠ alpha 特徵） |

**本軌 Phase 0 建議交付物**：書面「維持 gated／N/A」確認帳（零 build），或 Steward 點名解鎖其中一組後再另 plan。

### 軌 β — A–D 殘帳（更高槓桿候選）

| 殘帳 | 現況 | 建議下一手 |
|---|---|---|
| Wave-B 截面候選 | 材料化＋IC；**0/4 提拔** | 強化假說／換變換／誠實維持 staged——**不**因「有波名」強晉升 |
| 股級 macro | SKIP | 維持；解鎖＝另契約（leakage／PIT） |
| `stock_graph_edge` | 資料 have | 等 S4 graph adapter；S3 側可停 |
| 序列窗 | library have | 等 DL 族真過門再擴通道 |
| 估值 winsorize 等已知債 | 文件已知 | 機械債另案，非 E |

---

## 3. (a)(b) schema／程式（僅在解鎖時）

| 軌 | schema | python |
|---|---|---|
| α 維持 gated | 無新表 | 無新 builder；可寫 `audits/S3-WAVE-E-GATED-KEEP-YYYYMMDD.md` |
| α 解鎖 14 | staging／knowledge 既有管線 | 走 acquire→promote→license gate；**不**直寫 `feature_values` |
| β 候選強化 | 既有 `feature_candidate_values` | 既有 `validate_*`／`verify_candidate_promotion`；新特徵另 plan |

---

## 4. 分階段建議

| 階段 | 內容 | 另授權？ |
|---|---|---|
| **Phase 0（本檔）** | 裁示：E＝gated-keep，或解鎖子集；β 殘帳是否另開 | 本檔呈裁 |
| **Phase E-keep** | 只寫 KEEP 帳＋更新 master list 狀態句 | 低 |
| **Phase β-opt** | 針對 Wave-B 未過門候選之「下一假說」plan（非自動重跑重算） | 是 |
| **Phase E-unlock** | 僅當 Steward 點名組 14 或 16 | 是（高） |

---

## 5. 建議 GO 句（裁示後擇一）

```text
S3-WAVE-E-GATED-KEEP | FZ/GATE-keep | skip-sync | no-SIM-apply
```

或（殘帳，另名避免與 E 混淆）：

```text
S3-RESIDUAL-B-CANDIDATES-plan-first | FZ/GATE-keep | skip-sync | no-SIM-apply
```

---

## 6. 硬邊界

- 禁 LOB 幻造；禁未授權 Alt／LLM 特徵進預測管線；禁把 knowledge embedding 當因子。
- skip-sync／no-SIM-apply／FZ/GATE-keep。
- Wave-B 0 提拔**不是**失敗需重做同一四候選；是誠實門檻結果。

---

## 7. 請 Steward 裁示

1. **E-gated-keep** — 組 14–16 維持；只留 KEEP 帳（推薦預設）
2. **beta-residual-plan** — 另開 Wave-B 候選後續假說 plan（不重跑同一 verify）
3. **unlock-14** — 明示解鎖 Alt／NLP 一條窄路徑（須附 license 範圍）
4. **defer** — 特徵面暫停，專心 DIRFAMILY／S4 薄殼

---

*定版（2026-08-05）。S3-A–D 不重開；本檔定「E 字面 vs 殘帳」分軌，避免空波次。*
