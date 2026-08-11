---
title: NF-B-COINT · B-1e 協整 go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-B-COINT
date: 2026-08-07
viewpoint: 2026-08-07T15:25+08:00
paste: "NF-B-COINT-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31"
prior_kalman: audits/NF-B-KALMAN-0B-EXECUTED-20260807.md
prior_var: audits/NF-B-VAR-0B-EXECUTED-20260807.md
v2: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
layer: "[I]"
role: Kalman 0b 後「下一族」＝協整；Wave B classical 收尾格；誠實缺 adapter；零碼／零開訓
self_reported: true
---

# NF-B-COINT-go-plan｜B-1e 協整 · asof=2026-07-31

> **Steward**：Kalman 0b＠07-31 **有證據** → 下一族＝**B-1e 協整**（Wave B classical **收尾**）；本檔＝**go-plan only**。  
> **一句**：成對／小籃 log-price 協整殘差 → 有界方向尺（asof 釘 **2026-07-31**）；碼現況＝**無** coint 薄殼。  
> **本檔 ≠** 0a／0b 執行 · ≠ registry · ≠ 混 #14 · ≠ 當配對交易可下單授權。

---

## §0 護欄

```text
NF-B-COINT-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1
# ≠ 開碼／探針；≠ 撤全域 NF；≠ sim GARCH；≠ 塞 ranker serve
```

| 可 | 不可 |
|---|---|
| 寫對／系契約、階段、naive 地板、paste | 本句實作 Engle–Granger／Johansen 業務碼 |
| 對齊 ARIMA／VAR／Kalman 另書 hit | 宣稱「協整＝可套利／可交易」 |
| 標 Wave B classical 收尾 | 連帶解凍 GARCH 預測綠／GNN／RL |

---

## §1 為什麼是協整（佇列）

| 項 | 值 |
|---|---|
| Wave B 已開 | ARIMA · VAR · Kalman（皆＠07-31 有證據探針） |
| 殘格 classical | **B-1e**（B-1b GARCH 預測另分尺／易混 sim → **不**本窗搶） |
| 普查 | SKIP（無 adapter）——至 0a 仍成立 |
| 碼盤點 | `classical_ts`：**無** coint／Johansen／EG 薄殼 |
| 資料 | PriceAdj≤**07-31** 多股 log close（對齊 VAR 消費面） |
| 套件 | statsmodels `coint`／`Johansen` **可能**在場 ≠ 熱路徑 |

---

## §2 契約草案

| 契約項 | 草案 |
|---|---|
| asof | **2026-07-31** |
| 單元 | **對（k=2）** 優先；Johansen k=3 另子步 |
| 組對 | 非重疊 core 序對（同 VAR）或同產業邊（可選；0b 釘死一種） |
| 方法 0a | **Engle–Granger** 兩步（殘差 ADF／簡易 OLS β）固定小規格 |
| 信號 | 殘差 z-score／均值回復方向 → 對未來 h 日**相對／單邊**方向（0b 寫死一種主尺） |
| horizon | **H20** |
| 失敗 | 不協整／奇異／樣本短 → 該對該折 **SKIP**（不填假） |

**誠實**：協整探針「有證據」≠ 配對交易系統、≠ #14、≠ LIVE serve。

---

## §3 階段（另句）

| 階段 | 產出 | 句 |
|---|---|---|
| **本窗** | 本 plan＋ADOPT | `NF-B-COINT-go-plan` ✅ |
| **0a** | `CointPairEG`（名可微調）＋`--selftest` | `NF-B-COINT-0a-go` |
| **0b** | 有界對宇宙 vs naive；asof=**07-31** | `NF-B-COINT-0b-go` |
| **P1／registry** | 有證據後另授；**no-serve-swap** | 再另句 |

### 預凍門（0b · #32b）

mean(主尺 hit) **嚴格 >** mean(naive)；（可並列 VAR／單股 ARIMA 作資訊對照）。

---

## §4 Paste-ready

```text
NF-B-COINT-plan-adopt | FZ/GATE-keep | NF-pause-others | no-train | asof=2026-07-31 | hold-#1
```

```text
NF-B-COINT-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31
```

```text
NF-B-COINT-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | no-promote | no-serve-swap | hold-#1
```

---

## §5 驗收（本窗）

- [x] 下一族＝**B-1e 協整**；asof **2026-07-31**；Wave B classical 收尾意向  
- [x] adapter **missing** 誠實  
- [x] **≠** 本窗開訓／寫庫  
- [ ] 0a／0b → 各別 GO  

*完。[I] plan-first · self-reported。*
