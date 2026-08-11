---
title: NF-B-KALMAN · B-1d 狀態空間／Kalman go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-B-KALMAN
date: 2026-08-07
viewpoint: 2026-08-07T15:05+08:00
paste: "NF-B-KALMAN-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31"
prior_var: audits/NF-B-VAR-0B-EXECUTED-20260807.md
prior_arima: audits/S4-ARIMA-P1-EXECUTED-0731-20260807.md
v2: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
layer: "[I]"
role: VAR 0b 後「下一族」＝Kalman／狀態空間計畫；誠實缺 adapter；零碼／零開訓
self_reported: true
---

# NF-B-KALMAN-go-plan｜B-1d Kalman／狀態空間 · asof=2026-07-31

> **Steward**：VAR 0b＠07-31 **有證據** → 佇列下一族＝**B-1d Kalman**；本檔＝**go-plan only**。  
> **一句**：單股庫內價／報酬（asof 釘 **2026-07-31**）上做有界狀態空間薄殼——**先契約**；碼現況＝**無** Kalman class（`classical_ts` 僅 Arima／VarSmall）。  
> **本檔 ≠** `NF-B-KALMAN-go`／≠ 0a 碼／≠ 0b 探針／≠ registry／≠ 混 #14。

---

## §0 護欄

```text
NF-B-KALMAN-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1
# ≠ 0a／0b／P1 執行；≠ 撤全域 NF；≠ sim GARCH 冒充；≠ 塞 ranker serve
```

| 可 | 不可 |
|---|---|
| 寫狀態空間契約／階段／naive 地板／paste | 本句寫 `KalmanLocalLevel` 業務碼或全宇宙 fit |
| 對齊 ARIMA／VAR 另書 hit 尺 | 把前族有證據複製成本族已通過 |
| 排 0a→0b→P1 | 連帶解凍協整／GNN／RL；改 dgate；sim-apply |

---

## §1 為什麼是 Kalman（佇列）

| 項 | 值 |
|---|---|
| 前族 | ARIMA P1＋VAR 0b＠**07-31** 皆 mean hit > naive |
| Wave-B | B-1d 普查 **SKIP**（無 adapter）——仍成立至 0a |
| 碼盤點 | `src/augur/models/`：**無** Kalman／UnobservedComponents 薄殼 |
| 歷史資料 | PriceAdj≤**07-31** 單股序列（與 ARIMA 同消費面） |
| 套件 | `statsmodels` 可能有 `UnobservedComponents`／`statespace`——**≠**已接熱路徑 |
| 與 GARCH | **分尺**：本族＝預測方向 hit；禁用 `simulate_*` GARCH 綠冒充 |

---

## §2 契約草案（執行前釘）

| 契約項 | 草案 |
|---|---|
| asof | **2026-07-31** |
| 單元 | **單股**（非 VAR 多系；先 Local Level／local linear trend 一類） |
| 輸入 | log-price 或 log-return（0a 選定後寫死；建議 **level＝log close** 做 Local Level） |
| horizon | **H20**（對齊前兩族；H60 另授） |
| 模型 | 固定小規格（例 `local level`）；禁大搜參當完成 |
| 預測 | 未來 h 步點預測 → 累積方向 vs 實現 |
| 失敗 | 不收斂／樣本不足 → 該股該折 **誠實 SKIP** |

**不做（本 plan）**：多因子狀態空間、即接 `predict_asof`、VECM／協整（B-1e 另族）。

---

## §3 階段（另句才跑）

| 階段 | 產出 | 授權句 |
|---|---|---|
| **本窗** | 本 plan＋ADOPT | `NF-B-KALMAN-go-plan` ✅ |
| **0a** | `KalmanLocalLevel`（名可微調）＋`--selftest` | `NF-B-KALMAN-0a-go` |
| **0b** | 有界探針 vs naive；asof=**07-31**；可 n=50→全 core | `NF-B-KALMAN-0b-go` |
| **P1** | 擴大／穩定性 | `NF-B-KALMAN-P1-go` |
| registry | 有證據後＋CHK 字面；**no-serve-swap** | 再另句 |

### 預凍門（0b 跑前 · #32b）

| 尺 | 門檻 |
|---|---|
| 主 | mean(Kalman 方向 hit) **嚴格 >** mean(naive) |
| 對照 | 可並列同窗 ARIMA（資訊；非必須贏） |
| 禁 | #14 RankRidge 門；sim 風險綠 |

---

## §4 Paste-ready

```text
NF-B-KALMAN-plan-adopt | FZ/GATE-keep | NF-pause-others | no-train | asof=2026-07-31 | hold-#1
```

```text
NF-B-KALMAN-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31
```

```text
NF-B-KALMAN-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | no-promote | no-serve-swap | hold-#1
```

---

## §5 驗收（本窗）

- [x] 下一族＝**B-1d Kalman**；asof 釘 **2026-07-31**  
- [x] 誠實 **adapter missing**  
- [x] 與 ARIMA／VAR 交叉；**≠** 本窗開訓  
- [ ] 0a／0b → 各別 GO  

*完。[I] plan-first · self-reported。*
