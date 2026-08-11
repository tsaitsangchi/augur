---
title: Phase2 閒時五刀 · plan-first／explore 合集（2026-08-07）
status: plan_first
series: optimization_plan
date: 2026-08-07
viewpoint: 2026-08-07T16:55+08:00
paste: "PHASE2-IDLE-1TO5-plan | FZ/GATE-keep | no-train | hold-#1"
nav: reports/augur_opt_stepwise_best_next_plan_r12_20260807.md
layer: "[I]"
role: Steward 選 1–5 全開 plan／explore；零開訓；零改 B3／serve／dgate
self_reported: true
---

# Phase2 閒時五刀｜plan-first／explore · 2026-08-07

> **Steward**：看板順位 **1–5** 全要 · 深度＝**plan_all**。  
> **主軸**：**hold-#1**（A→B3＠08-07）；PriceAdj 頂仍 **08-06**。  
> **本合集 ≠** 任一執行訓／P6 fit／CYCLE 寫庫／G3 接熱路徑／序列重訓。

```text
PHASE2-IDLE-1TO5-plan-adopt | FZ/GATE-keep | no-train | hold-#1 | skip-sync | no-SIM-apply
# 1=C1 CYCLE · 2=P6 · 3=G3 · 4=STRUCT explore · 5=Seq DL
```

---

## 1｜C1 CYCLE（#8）

| 項 | 內容 |
|---|---|
| 前序 | `LOOP-S2-TO-S1-EXPAND` ✅；`LOOP-CYCLE-1`＠08-05＝accept／gap 文件 |
| 本 plan | 下一 CYCLE＝**對齊 tip（目標 D＝08-07 就緒後或 08-06 閘）** 的 gap 重寫＋驗收表；**不含** S3 rebuild／NF 解凍 |
| 執行句（另授） | `LOOP-CYCLE-2-go \| FZ/GATE-keep \| API-THAW-bounded \| no-SIM-apply \| re-accept-only` |
| 禁 | 與 live B3 搶 slot；假關 dgate |

---

## 2｜P6 週 fit（#9）

| 項 | 內容 |
|---|---|
| 前序 | FREEZE＠**08-04** H20／H60 已 fit／emit |
| 本 plan | **下一 FREEZE 候選＝2026-08-06**（價／fv／B3 tip 已達；校準器未自動跟） |
| 序（另 GO） | build oos H20／H60＠08-06 → fit → emit；⊥日更 CPU |
| 執行句 | `P6-REFIT-FREEZE-2026-08-06-go \| FZ/GATE-keep \| skip-sync \| no-SIM-apply \| horizons=20,60 \| RankRidge` |
| 禁 | 把 emit-only 當 refit；假升確立級 |

---

## 3｜G3 圖→熱路徑（#7）

| 項 | 內容 |
|---|---|
| 前序 | G1／G2 stub ✅；圖＠07-31／08-06；**NF-E 0b STOP** |
| 本 plan | G3＝**消費接線設計**（非翻案升格 GNN）：RankRidge 熱路徑如何 **可選** 讀圖特徵／旁路；預設 **仍不讀** |
| 誠實 | GNN 0b 未勝 naive → G3 **不得**默認開訓；先契約／feature 旁路 plan |
| 執行句（更遠） | `GRAPH-G3-HOTPATH-go-plan` → 另 `…-go`；與 #1 互斥時讓日更 |
| 禁 | 塞進 B3 standing；SERVE-SWAP 到 GcnSmall |

---

## 4｜結構循環 explore（#13）

| 項 | 內容 |
|---|---|
| 性質 | **零改碼** 唯讀盤點 import／腳本環／文件互指 |
| 產出 | explore 帳（見 `STRUCT-CYCLE-EXPLORE-EXECUTED`） |
| 執行句 | 本窗即 explore（無 GO 寫庫） |
| 禁 | 大清理重構；誤傷熱路徑 |

---

## 5｜C／D 序列 DL（模型下一族）

| 項 | 內容 |
|---|---|
| 前序 | SeqLSTM Phase 0b **未過門**（min Sharpe≪1.3016）；adapter／`sequence_ranker` 已在 |
| 本 plan | asof 釘 **2026-07-31**；**勿重掃假綠**＝若同尺重跑須寫明「驗證漂移」非賭升格 |
| 建議 | `NF-C-SEQLSTM-go-plan`＝有界再驗或 Transformer 另族；預設 **STOP promote** 期望 |
| 執行句 | `NF-C-SEQLSTM-go-plan \| FZ/GATE-keep \| asof=2026-07-31 \| no-train`（本窗僅 plan） |
| 禁 | 撤全域 NF；默換 LIVE |

---

## Paste 總表（採納後各刀另貼）

```text
LOOP-CYCLE-2-go | …          # 1 執行
P6-REFIT-FREEZE-2026-08-06-go | …   # 2 執行
GRAPH-G3-HOTPATH-go-plan | … # 3 深化
STRUCT-CYCLE-EXPLORE-go | …  # 4（本窗可已 explor）
NF-C-SEQLSTM-go-plan | asof=2026-07-31 | no-train  # 5
```

*完。[I] · self-reported。*
