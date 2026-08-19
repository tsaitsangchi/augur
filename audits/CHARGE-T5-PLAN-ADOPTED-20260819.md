---
status: adopted
series: s4_s5_verify
round: r18
date: 2026-08-19
viewpoint: 2026-08-19T13:25+08:00
plan: reports/augur_charge_t5_model_plan_r18_20260819.md
product_id: CHARGE-T5-v1
layer: "[I]"
self_reported: true
paste: "CHARGE-T5-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19 | 規則＝E-charge×T5 | 宇宙≠兩檔 | k=10 | 條件≠可交易 | 禁OOS最長持有當冠"
parent: TWIN-EX E-charge×T5（僅兩檔）
exec: r18 M35
---

# ADOPTED｜CHARGE-T5 衝勢 5 日進出（P0）

Steward 貼：

```text
CHARGE-T5-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| 規則＝E-charge×T5 | 宇宙≠兩檔 | k=10 | 條件≠可交易 | 禁OOS最長持有當冠
```

## 生效

| 角色 | 路徑 |
|---|---|
| 本軌定義 SSOT | `reports/augur_charge_t5_model_plan_r18_20260819.md` |
| 執行板掛點 | r18 **M35**（P0 已採納；宇宙未開工） |
| 兩檔實驗室 | 仍 TWIN-EX-v1；39 筆％**不是**本模型績效 |
| 日常出單 | 仍 standing **H20+H60 RankRidge** |

`adopt`＝凍結 **CHARGE-T5-v1**＝E-charge×T5（L-A ∧ L-D ∧ H5＞0 ∧ H10＞0；轉折 t+1 進；進場後第 5 交易日出；同日 k=10 等權）。**不是**宇宙已驗證、不是可交易、不是 #14、不是改 standing。空方鏡像＝`CHARGE-T5-SHORT-v1`；可學習打分＝`CHARGE-T5-FIT-v1`；本採納**不開**。

## 本 paste 鎖定

| 條 | 意思 |
|---|---|
| no-promote | 不換冠、不取代 RankRidge 出門 |
| standing=20,60 | 日常出門窗不變 |
| no-fake-B3@08-19 | 最近合法日＝**2026-08-18** |
| 規則＝E-charge×T5 | 與 TWIN-EX 兩檔冠軍同閘、同持有；無 L-C、無 L-B、無 Ridge |
| 宇宙≠兩檔 | 兩檔最佳不必宇宙最佳；39 筆不當產品績效 |
| k=10 | 同日新訊號依 mean(H60,H120,H240) 取最多 10 檔，不足不補 |
| 條件≠可交易 | 過閘 ≠ 下單 |
| 禁OOS最長持有當冠 | 不把 T20／T40／抱牢在大多頭窗當最佳 |

切窗與 TWIN-EX 同：IS＝2024，OOS＝2025-01～2026-06，出場 ≤ 2026-08-18。不要抱牢尺沿用：主鍵 IS 複利；T40 不當冠。

## 本窗未做（刻意）

`CHARGE-T5-universe-go`／單日探針／寫庫／emit／FIT／SHORT／commit／假 B3＠08-19。

下一槍（另貼；與 `TWIN-EX-universe-go` 同一槍）：

```text
CHARGE-T5-universe-go | dry-run | IS=2024 OOS=2025-01..2026-06 | 不要抱牢
```
