---
status: draft
series: s4_models
depends_on:
  - reports/augur_s4_market_model_families_opt_plan_20260804.md
  - audits/S4-WAVE-B-ADAPTER-PHASE0B-EXECUTED-20260805.md
  - audits/S3-WAVE-D-EXECUTED-20260804.md
---

# S4 下一族 adapter plan-first（2026-08-05）

> **性質**：[I] plan-first（波次 A · 項 8）。**本檔不開訓、不寫 adapter 業務碼。**  
> **背景**：taxonomy Wave A–G **普查／誠實 SKIP** 已收官；真評測已試 RankEnsemble／SeqLSTM／sklearn 族／ARIMA Phase 0b。  
> **self-reported（#32a）**。

---

## 0. 一句話

**「下一族」＝在已 SKIP／partial 中挑一條有新前提可解鎖者做 plan→Phase 0；不是重跑已判死族。**

---

## 1. 已結案（不重做）

| 族 | 結果 |
|---|---|
| RankRidge／RankGBDT | 現任經濟尺冠軍側 |
| RankEnsemble | 未過門 |
| SeqLSTM Phase 0b | 未過門 |
| Wave-A sklearn | 僅 RankSVM@H20 真贏；DIRFAMILY P1 未改善 DirStack |
| ARIMA Phase 0b | mean hit > naive（有證據）→ **Phase 1 另項（清單 #4）、本檔不默授** |

---

## 2. 候選下一族（擇一）

| 代號 | 族 | 為何現在可談 | 主要缺口 |
|---|---|---|---|
| **NF-E** | Wave E GNN（GCN／GAT） | `stock_graph_edge` **已落地**（S3-WAVE-D；13,021 邊）——原 SKIP「無圖邊」前提已變 | 仍無 GNN 套件／薄 adapter；需 GPU 或 CPU smoke 誠實 |
| **NF-B-VAR** | Wave B VAR／VECM | classical 薄殼路線已有 ARIMA 先例 | 多序列面板契約；截面彙總尺另書 |
| **NF-B-P1** | ARIMA Phase 1（另書量尺） | 0b 有證據 | **＝清單項 4**；本檔僅交叉引用，不併授權 |
| **NF-pause** | 停新族 | 專心 β／閉環／顧問 | — |

**推薦預設**：若要新族文件推進 → **NF-E**（前提真變）；若要計量延續 → **NF-B-VAR**；CPU／聊天優先 → **NF-pause**。

---

## 3. (a)(b) schema／程式（NF-E 示意）

| 層 | 內容 |
|---|---|
| schema | **無新表**（讀 `stock_graph_edge`／既有 price as-of）；失敗則誠實 SKIP |
| python | 新 `src/augur/models/…` 薄殼＋`scripts/probe_*_phase0.py`；`--selftest` 零 DB 不變式；Phase 0b 另 GO |
| 硬禁 | 假綠；live FinMind；SIM-apply；把 KH `knowledge_edge` 當股圖 |

NF-B-VAR：同 ARIMA 模式——單／多股序列契約＋naive／常數地板臂（#32b）。

---

## 4. 分階段

| 階段 | 產出 | 另授權？ |
|---|---|---|
| Phase 0（本檔） | Steward 選 NF-* | 本檔呈裁 |
| Phase 0a | 套件／import smoke | 選後小 GO |
| Phase 0b | 有界評測 vs 地板 | 是 |
| Phase 1 | 僅 0b「有證據」後 | 是 |

---

## 5. 請 Steward 裁示

1. **NF-E-go-plan** — 核准以 GNN 為下一族詳細設計（仍不開訓）  
2. **NF-B-VAR-go-plan** — 核准 VAR 詳細設計  
3. **NF-pause** — 暫停新族  
4. **defer_to_item4** — 下一手改走 ARIMA Phase 1（清單 #4 另句）  

*定版草稿（2026-08-05 波次 A）。*
