---
title: S4｜序列／圖消費端草稿（NF-pause 下｜不訓）
status: draft_acked
acked: audits/LIGHT-PARALLEL-PLANS-ACK-20260805.md
date: 2026-08-05
layer: "[I]"
series: s4_models
open_problem: "#4"
depends_on:
  - audits/S3-WAVE-D-EXECUTED-20260804.md
  - audits/S4-NF-PAUSE-ACCEPTED-20260805.md
  - reports/augur_s4_next_family_adapter_plan_20260805.md
  - reports/augur_s4_wave_c_lstm_adapter_plan_20260804.md
self_reported: true
---

# S4 序列／圖消費端草稿 · 2026-08-05

> **性質**：[I] plan-first **consume-side only**。  
> **硬前提**：**NF-pause 已接受**——本檔**不**開新族 Phase 0b／不訓／不撤 pause。  
> **開項**：#4（S3-D 資料已落地 ↔ S4 仍 SKIP／未過門）。

## 0. 一句話

**缺的不是「再挖一輪 S3」；缺的是「誰讀序列窗／圖邊、讀成什麼張量、失敗怎麼 SKIP」的消費契約——在 pause 下只允許把契約寫清楚並做零 DB／import smoke。**

## 1. 供给侧（已有｜勿重做）

| 資產 | 狀態 | 證據 |
|---|---|---|
| 組 12 序列窗 library | **have**（不建新表） | `S3-WAVE-D-EXECUTED` Phase 1；window∈{20,60,120} |
| `stock_graph_edge` | **13,021** 列；`as_of_date=2026-06-30` **單一快照** | Phase 2c；型＝industry_same／corr_60／corr_120 |
| S4 Wave C 普查 | 族 SKIP「無 adapter」 | `S4-WAVE-C-EXECUTED` |
| SeqLSTM adapter plan | 契約解除後曾開；**Phase 0b 未過門** | `augur_s4_wave_c_lstm_adapter_plan` 後記 |
| Wave D Transformer 普查 | SKIP | `S4-WAVE-D-EXECUTED` |
| NF 下一族 | **pause** | `S4-NF-PAUSE-ACCEPTED`；NF-E＝GNN 候選但擱置 |

## 2. 消費缺口（精確）

| 讀者 | 現狀 | 缺口 |
|---|---|---|
| RankRidge／prodset 熱路徑 | 讀 `feature_values` 扁平 | **不**消費序列窗／圖邊（誠實；非 bug） |
| SeqLSTM／Transformer | 無穩定 panel cache／adapter 或未過門 | 再訓＝撤 pause＋新 GO |
| GNN（NF-E） | 邊表有、套件／adapter 無 | 同上；且圖 **as_of 僅 06-30**≠日更 D |
| 顧問／S5 | 相對機率 | **不得**把圖邊當方向確立 |

## 3. 本草稿允許做的事（pause 下）

| ID | 交付 | CPU |
|---|---|---|
| **C0** | 本檔（契約圖＋禁區） | 零 |
| **C1** | 唯讀探針腳本大綱：`count/as_of` 圖邊；序列窗 `build_*` import＋`--selftest` | 秒級 |
| **C2** | 「消費契約卡」：輸入鍵（stock_id, as_of, window／edge_type）→張量／COO 形狀→缺資料 FAIL 字句 | 文件 |
| **C3** | 日更錯位清單：圖邊快照落後 PriceAdj／fv 時，adapter **必須 SKIP** 而非靜默用舊圖 | 文件 |

## 4. 明示禁止（本檔效力內）

- 撤 `NF-pause`／開 `NF-E-go`／`S4-ARIMA-P1`／重跑 SeqLSTM 0b  
- 寫訓練 loop、改 prodset、sim `--apply`  
- FinMind／放量 sync；把 `knowledge_edge` 當股圖  
- 為「看起來有消費」而 median-fill 圖／窗  

## 5. 契約卡草案（供將來 adapter）

### 5.1 序列窗

| 項 | 草案 |
|---|---|
| 來源 | S3-D sequence library（既有函式；不新表） |
| 鍵 | `(stock_id, as_of, window∈{20,60,120}, channels…)` |
| 失敗 | 窗不滿／缺價 → 該股該折 **剔除或 SKIP 族**（族級策略預註冊） |
| 效能 | 必須面板快取（Wave-C plan §3.1）；禁逐 as-of 重打 31 SQL/股 無快取 |

### 5.2 圖邊

| 項 | 草案 |
|---|---|
| 來源 | `stock_graph_edge` |
| 鍵 | `(as_of_date, src, dst, edge_type)` |
| 新鮮度 | `as_of_date` 須 ∈ 允許落後窗或 **重建邊**（重建＝另 GO，非本草稿） |
| 失敗 | 無邊／過期 → GNN **SKIP**（理由＝資料契約，非假綠） |

## 6. 分階段（含 pause 牆）

| 階段 | 內容 | 要撤 pause？ |
|---|---|---|
| 本檔 C0–C3 | 文件＋可選 selftest 探針 | **否** |
| 解凍後 Phase 0a | import／形狀 smoke | 要 `NF-*-go-plan` |
| 解凍後 Phase 0b | 有界評測 vs 地板 | 要；未過門＝誠實停 |
| 日更圖重建 | `build_stock_graph_edges --asof D --commit` | **另句**（與 NF 正交） |

## 7. Paste-ready

```text
S4-SEQ-GRAPH-CONSUME-DRAFT-ack
# pause 下僅文件／selftest；不訓
```

解凍（**勿**與本 ack 混貼）：

```text
NF-E-go-plan
# 或延續
# （SeqLSTM 重開須新句；承認 0b 未過門史料）
```

## 8. 驗收（草稿本身）

1. Steward 能復述：資料 have ≠ 可訓。  
2. 圖邊 as_of 落後被寫成 **強制 SKIP 條件**。  
3. 無任何默授訓練／prodset。

*完。[I] self-reported（#32a）。*
