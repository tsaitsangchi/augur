---
title: NF-B-GARCH · B-1b GARCH 預測臂 go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-B-GARCH
date: 2026-08-07
viewpoint: 2026-08-07T16:20+08:00
paste: "NF-B-GARCH-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31"
prior_gnn: audits/NF-E-GNN-0B-EXECUTED-20260807.md
wave_b: audits/S4-WAVE-B-EXECUTED-20260804.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
layer: "[I]"
role: GNN STOP 後下一族＝GARCH 預測臂；硬分尺≠sim 風險；零碼／零開訓
self_reported: true
---

# NF-B-GARCH-go-plan｜B-1b GARCH **預測臂** · asof=2026-07-31

> **Steward**：NF-E GNN 0b **STOP** → 下一族＝Wave B 殘格 **B-1b GARCH 預測臂**；本檔＝**go-plan only**。  
> **一句**：單股報酬上 fit 小 GARCH（＋常數均值）→ 有界**方向**尺（asof 釘 **2026-07-31**）；**嚴禁**把 `simulate_*`／組合風險 GARCH 綠冒充本臂通過。  
> **本檔 ≠** 0a／0b 執行 · ≠ sim-apply · ≠ registry · ≠ 混 #14。

---

## §0 護欄

```text
NF-B-GARCH-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1
# ≠ 開碼／探針；≠ 撤全域 NF；≠ 引用 simulate_portfolio_risk／MC 當預測 PASS
```

| 可 | 不可 |
|---|---|
| 寫預測臂契約／階段／naive 地板 | 本句寫 `GarchMean` 業務碼或全宇宙 fit |
| 明訂 **預測尺 ⊥ sim 風險尺** | 把 arch 已用於 sim 稱「預測已存在」 |
| 排 0a→0b | 改 dgate；SERVE-SWAP；sim `--apply` |

---

## §1 為什麼是 GARCH（佇列）

| 項 | 值 |
|---|---|
| Wave B | ARIMA／VAR／Kalman／協整 探針已做；**殘＝B-1b 預測** |
| 普查 | 預測 **missing**；sim＝**n/a-sim**（分尺已釘） |
| 套件 | `arch` **有**（sim 路徑已用）≠ 預測熱路徑 adapter |
| 碼盤點 | `classical_ts`／models：**無** 預測用 GARCH 薄殼 |
| 歷史資料 | PriceAdj 單股報酬 ≤**07-31** |

---

## §2 雙尺誠實（寫死）

| 尺 | 用途 | 本 plan |
|---|---|---|
| **預測臂** | 未來 h 日報酬**方向 hit** vs naive | **本族主尺** |
| **sim／風險臂** | 波動／尾部／組合壓力 | **禁止**當 S4 預測通過證據 |

`scripts/simulate_*` 內 GARCH＝風險基礎設施——**零交叉綠燈**。

---

## §3 契約草案（預測臂）

| 契約項 | 草案 |
|---|---|
| asof | **2026-07-31** |
| 模型 | `ConstantMean`＋`GARCH(1,1)`（固定；禁大搜參當完成） |
| 輸入 | 近端 log-return（`train_window` 釘死，對齊 classical） |
| 方向信號 | 均值預測累積（或殘差均值）；**不以 σ 漲當漲跌預測**（σ 可另報、不入主門） |
| horizon | 建議 **H20**（與 ARIMA 對齊）；若價窗不夠另降階並帳註 |
| 失敗 | 不收斂／樣本短 → 該股該折 **SKIP** |

---

## §4 階段（另句）

| 階段 | 產出 | 句 |
|---|---|---|
| **本窗** | 本 plan＋ADOPT | `NF-B-GARCH-go-plan` ✅ |
| **0a** | `GarchMeanDir`（名可微調）＋`--selftest` | `NF-B-GARCH-0a-go` |
| **0b** | 有界宇宙 vs naive；asof=**07-31** | `NF-B-GARCH-0b-go` |
| registry | 有證據後另授；**no-serve-swap** | 再另句 |

### 預凍門（0b · #32b）

mean(GARCH 方向 hit) **嚴格 >** mean(naive)；**且**帳面聲明未引用任何 sim GARCH 指標。

---

## §5 Paste-ready

```text
NF-B-GARCH-plan-adopt | FZ/GATE-keep | NF-pause-others | no-train | asof=2026-07-31 | hold-#1 | pred-arm-only
```

```text
NF-B-GARCH-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | no-SIM-apply
```

```text
NF-B-GARCH-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | no-promote | no-serve-swap | hold-#1
```

---

## §6 驗收（本窗）

- [x] 下一族＝**B-1b GARCH 預測臂**；asof **2026-07-31**  
- [x] 與 sim 風險 **硬分尺**  
- [x] adapter **missing** 誠實  
- [x] **≠** 本窗開訓  
- [ ] 0a／0b → 各別 GO  

*完。[I] plan-first · self-reported。*
