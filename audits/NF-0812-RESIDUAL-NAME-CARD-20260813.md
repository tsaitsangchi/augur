---
status: residual_name_card
series: s4_models
track: NF-0812-CLOSEOUT
date: 2026-08-13
viewpoint: 2026-08-13T09:58+08:00
asof: "2026-08-12"
paste: "NF-0812-residual-card | FZ/GATE-keep | no-re-scan-STOP | NF-pause | no-promote | hold-#1"
self_reported: true
layer: "[I]"
---

# 殘格點名卡｜asof＝2026-08-12 · 勿重掃假綠

> Steward 引句：「再下一族須另點名殘格」。本檔＝**點名卡**；**≠** go、**≠** 開訓。

## 已閉＠0812（禁同尺重掃刷綠）

| 族 | 帳 | 門 |
|---|---|---|
| ARIMA P1 | `S4-ARIMA-P1-0812-EXECUTED` | EVIDENCE · no-promote |
| VAR | `NF-B-VAR-0812-0B-EXECUTED` | EVIDENCE · no-promote |
| Kalman | `NF-B-KALMAN-0812-0B-EXECUTED` | EVIDENCE · no-promote |
| COINT | `NF-B-COINT-0812-0B-EXECUTED` | EVIDENCE · no-promote |
| GARCH 預測臂 | `NF-B-GARCH-0812-0B-EXECUTED` | EVIDENCE · no-promote |
| GNN | `NF-E-GNN-0812-0B-EXECUTED` | EVIDENCE（異網格）· no-promote |

亦禁：TimesFM／Chronos／Moirai／TFM／LSTM／PatchTST／FTTR 等同族「再刷一次假綠」。

## 誠實殘格（須明示 paste 才開）

| 代號 | 為何算殘 | 現況 | 風險 |
|---|---|---|---|
| **NF-B-VECM** | VAR plan 明示延後 | **無** `Vecm*`／probe | 須 0a→0b；≠塗綠 VAR |
| **NF-C-TCN** | Wave C 殘（≠ LSTM／TFM） | 無 0812 帳；須 plan／0a | 易混序列已 STOP 族 |
| **NF-A-NB** | Wave A 樸素貝氏表格 | 無 adapter 熱路徑 | 另尺；≠ sklearn 重掃 |
| **Daily*** | 方向臂；⊥ ALL-RANK A | registry 有字面；日更未納 | **另軸**；勿當市場 L2 |
| **Wave F RL** | taxonomy defer | 高門檻／無熱路徑 | 默認 **延後** |
| **收口停** | — | 維持 NF-pause | **推薦預設**（市場 hold-#1） |

## 推薦

```text
NF-0812-旁刀收口 | NF-pause | hold-#1 | A2B3-ARMED@08-13
# 下一族＝（空白）直至 Steward 點名上一表殘格
```

若要開刀，貼其中一句（示例）：

```text
NF-B-VECM-go-plan | asof=2026-08-12 | FZ/GATE-keep | no-train
NF-C-TCN-go-plan | asof=2026-08-12 | FZ/GATE-keep | no-train
NF-A-NB-go-plan | asof=2026-08-12 | FZ/GATE-keep | no-train
Daily-arm-0812-go-plan | asof=2026-08-12 | FZ/GATE-keep | ≠ALL-RANK-A
NF-0812-closeout-ack | NF-pause | hold-#1
```

*完。*
