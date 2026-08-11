---
title: NF-B-VAR · B-1c VAR／VECM go-plan（asof=2026-07-31 · 零默訓）
status: plan_first
series: s4_models
track: NF-B-VAR
date: 2026-08-07
viewpoint: 2026-08-07T14:48+08:00
paste: "NF-B-VAR-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31"
prior_arima: audits/S4-ARIMA-P1-EXECUTED-0731-20260807.md
v2: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
layer: "[I]"
role: ARIMA P1 後「下一族」＝VAR／VECM 計畫；誠實缺 adapter；零碼／零開訓
self_reported: true
---

# NF-B-VAR-go-plan｜B-1c VAR／VECM · asof=2026-07-31 · 2026-08-07

> **Steward**：ARIMA P1＠07-31 全 core **有證據** → 佇列下一族＝**B-1c VAR**；本檔＝**go-plan only**。  
> **一句**：用庫內歷史多序列（asof 釘 **2026-07-31**）做有界 classical 下一刀——**先契約＋薄殼計畫**；碼現況＝**無** `Var*` class（≠ ARIMA 已有 `ArimaUnivariate`）。  
> **本檔 ≠** `NF-B-VAR-go`／≠ Phase 0b 探針執行／≠ registry／≠ 混 #14。

---

## §0 護欄

```text
NF-B-VAR-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | hold-#1
# ≠ NF-B-VAR-go；≠ 撤全域 NF；≠ GARCH 假綠；≠ 塞 ranker serve
```

| 可 | 不可 |
|---|---|
| 寫多序列契約／階段／預凍地板／paste | 本句寫 `VarUnivariate` 業務碼或 fit 全宇宙 |
| 對齊 ARIMA 另書 hit 尺經驗 | 把 ARIMA 有證據複製成 VAR 已通過 |
| 排 0a／0b／P1 執行句 | 連帶解凍 GNN／RL；改 dgate；sim-apply |

---

## §1 為什麼是 VAR（佇列）

| 項 | 值 |
|---|---|
| 前族 | B-1a ARIMA P1＠**07-31**：mean hit 0.5139 > naive 0.4850（204／204） |
| V2 | 優先 **3** · B-1c（原 defer；ARIMA 先例已開） |
| Wave-B 普查 | SKIP（缺多序列面板契約／adapter）——**仍成立至本 plan 解鎖碼** |
| 碼盤點（2026-08-07） | `src/augur/models/`：**無** VAR／VECM；僅 `ArimaUnivariate` |
| 歷史資料 | PriceAdj≤**07-31** 多股對數報酬；可選 prodset 外生（P1 默認**純價 panel**） |
| 套件 | `statsmodels` 在場 ≠ adapter |

---

## §2 多序列契約（文件釘；執行前必滿）

| 契約項 | 草案 |
|---|---|
| asof | **2026-07-31**（凍結；禁讀 >asof） |
| panel | 選定 stock 集合 S（|S| 小起步：產業子集或 core 隨機／前 k）× 對齊交易日 |
| 變數 | 各股近端 log-return；缺日＝該折 SKIP（不填假） |
| 維度上限 | Phase 0：**k≤5** 股／系（防維度災）；0b 可 k=2～3 |
| horizon | **H20**（對齊 ARIMA P1；H60 另授） |
| 模型 | `VAR(p)` 固定小 p（例 p=1 或 2）；禁自動大搜參當完成 |
| 失敗 | 不收斂／奇異／樣本不足 → 該折／該系 **誠實 SKIP** |

**VECM**：本 plan **延後**（協整檢定＋誤差修正＝另子句）；先 VAR levels-on-returns。

---

## §3 階段（另句才跑）

| 階段 | 產出 | 授權句 |
|---|---|---|
| **本窗** | 本 plan＋ADOPT | `NF-B-VAR-go-plan` ✅ |
| **0a** | `VarSmall` 薄殼＋`--selftest`（零 DB） | `NF-B-VAR-0a-go` |
| **0b** | 有界探針 vs naive／ARIMA 單股地板；asof=**07-31** | `NF-B-VAR-0b-go` |
| **P1** | 擴大宇宙／系；仍另書 hit 尺 | `NF-B-VAR-P1-go` |
| registry | 僅 0b／P1 有證據後；CHK 加字面；**no-serve-swap** | 再另句 |

### 預凍門（0b 跑前寫死 · #32b）

| 尺 | 門檻 |
|---|---|
| 主 | 系／股彙總 mean(VAR 方向 hit) **嚴格 >** mean(naive) |
| 對照 | 可並列同窗 ARIMA 單股 hit（**資訊**；非必須贏 ARIMA） |
| 禁 | 用 #14 RankRidge 門當 VAR 通過；sim GARCH 冒充 |

---

## §4 Paste-ready

採納（零開訓）：

```text
NF-B-VAR-plan-adopt | FZ/GATE-keep | NF-pause-others | no-train | asof=2026-07-31 | hold-#1
```

薄殼碼（另決策）：

```text
NF-B-VAR-0a-go | FZ/GATE-keep | no-train-prod | hold-#1
```

有界探針（碼齊後）：

```text
NF-B-VAR-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | no-promote | no-serve-swap | hold-#1
```

---

## §5 驗收（本窗）

- [x] 下一族點名＝**B-1c VAR**；asof 釘 **2026-07-31**  
- [x] 誠實：**adapter missing**；契約 k≤5／H20／naive 地板  
- [x] 與 ARIMA P1 交叉；**≠** 本窗開訓／寫庫  
- [ ] 0a／0b → 須各別 GO  

*完。[I] plan-first · self-reported。*
