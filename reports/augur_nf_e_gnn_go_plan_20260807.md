---
title: NF-E-GNN · Wave E GCN／GAT go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-E
date: 2026-08-07
viewpoint: 2026-08-07T15:50+08:00
paste: "NF-E-GNN-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31"
prior_coint: audits/NF-B-COINT-0B-EXECUTED-20260807.md
graph_consume: src/augur/features/graph_consume.py
v2: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
layer: "[I]"
role: Wave B 收尾後「下一族」＝圖 GNN；誠實缺 GNN adapter＋缺 graph＠07-31；零碼／零開訓
self_reported: true
---

# NF-E-GNN-go-plan｜E-7a GCN／GAT · asof=2026-07-31

> **Steward**：Wave B classical（ARIMA／VAR／Kalman／協整）探針鏈收尾 → 下一族＝**Wave E 圖 GNN**；本檔＝**go-plan only**。  
> **一句**：用 **S-EQ** 股圖＋prodset 節點特徵，在 asof 釘 **2026-07-31** 做有界圖學習——**前提先補齊**；碼／套件／圖快照現況皆有洞。  
> **本檔 ≠** 0a 碼／0b 訓／塞 B3／換 LIVE serve／升格。

---

## §0 護欄

```text
NF-E-GNN-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1
# ≠ NF-E-*-go 執行；≠ 撤全域 NF；≠ 把 knowledge_edge 當股圖；≠ sim-apply
```

| 可 | 不可 |
|---|---|
| 寫契約／缺口／階段／paste | 本句安裝套件、寫 GCN、全宇宙訓 |
| 釘 S-EQ＋已聲明邊型 | 硬編碼 06-30／默用 MAX(asof)／讀 asof>D |
| 排 rebuild／0a／0b | 連帶解凍 RL／GARCH 假綠；改 dgate |

---

## §1 為什麼是 GNN（佇列）

| 項 | 值 |
|---|---|
| V2 | 優先 **5**（classical 已走完可談） |
| 圖邊 | `stock_graph_edge` **有**（08-05／08-06）；consume stub **G2** 已在 |
| 普查 | E-7a GCN／GAT＝**SKIP**（無預測 adapter）——仍成立 |
| LIVE／#1 | hold；**不**塞 B3 standing |

---

## §2 現況探針（2026-08-07 · 誠實）

| 錨 | 結果 |
|---|---|
| `stock_graph_edge` @ **2026-07-31** | **無列**（max＝**2026-08-06**；另有 08-05） |
| S-EQ `load_edges(…, 2026-07-31)` | 預期 **`graph_asof_missing`** |
| `torch` | **有** |
| `torch_geometric`／`dgl` | **無** |
| GNN train／predict class | **無**（僅 `graph_consume` 讀邊 stub） |
| 節點特徵 | prodset active3 可沿用（與 RankRidge 同尺另書時須標） |

→ **0b 不可直接開**：須先 `GRAPH-REBUILD`＠**07-31**（或 Steward 改釘圖／標的 asof）；0a 須決「純 torch 手工消息傳遞」vs「另授裝 torch_geometric」。

---

## §3 契約草案

| 契約項 | 草案 |
|---|---|
| 標的 asof | **2026-07-31**（特徵／label／圖 **同一 D**；S-EQ） |
| 邊 | 僅 `industry_same`／`return_corr_60d`／`return_corr_120d`（已聲明） |
| 節點 x | prodset 特徵 panel＠D（缺＝SKIP 節點，不 fill 假） |
| 任務 | 截面相對排序或方向（0a 選定後寫死；**另書尺**，禁直接冒充 #14 冠軍門） |
| 失敗 | 無圖／無套件／不收斂 → **誠實 SKIP** |

**禁**：KH `knowledge_edge` 當股圖；lookahead 邊；默換 RankRidge serve。

---

## §4 階段（另句才跑）

| 階段 | 產出 | 句 |
|---|---|---|
| **本窗** | 本 plan＋ADOPT | `NF-E-GNN-go-plan` ✅ |
| **圖前提** | `stock_graph_edge`＠**07-31** 寫入 | `GRAPH-REBUILD-2026-07-31-go` |
| **0a** | 最小 GNN／消息傳遞薄殼＋`--selftest`（零 DB 或合成圖） | `NF-E-GNN-0a-go` |
| **0b** | 有界探針＠07-31 vs 地板（naive／RankRidge 資訊對照） | `NF-E-GNN-0b-go` |
| registry／serve | 預設不；有證據＋CHK 另授；**no-serve-swap** | 再另句 |

### 預凍門（0b · #32b）

寫死後再跑：至少嚴格勝 **naive**（或明文寫死的常數地板）；**不得**僅因 IC 綠稱可交易。

---

## §5 Paste-ready

```text
NF-E-GNN-plan-adopt | FZ/GATE-keep | NF-pause-others | no-train | asof=2026-07-31 | hold-#1
```

圖前提（建議先於 0b）：

```text
GRAPH-REBUILD-2026-07-31-go | FZ/GATE-keep | skip-sync | no-SIM-apply | --commit | hold-#1
```

```text
NF-E-GNN-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31
```

```text
NF-E-GNN-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | no-promote | no-serve-swap | hold-#1
```

---

## §6 驗收（本窗）

- [x] 下一族＝**E-7a GNN**；asof 釘 **2026-07-31**  
- [x] 誠實：圖＠07-31 **缺**、`torch_geometric` **缺**、adapter **缺**  
- [x] **≠** 本窗開訓／rebuild／裝包  
- [ ] rebuild／0a／0b → 各別 GO  

*完。[I] plan-first · self-reported。*
