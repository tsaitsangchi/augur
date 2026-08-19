---
status: adopted
series: s4_s5_verify
round: r18
date: 2026-08-19
viewpoint: 2026-08-19T13:03+08:00
plan: reports/augur_bull5_hstack_pullback_plan_r18_20260819.md
product_id: BULL5-v1
layer: "[I]"
self_reported: true
paste: "BULL5-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19 | 全正窗＝H10…H240 | H5<0 | 不用累積遞減當多頭 | 條件≠可交易 | 做空≠可空"
n_long_prediag: 9
n_casc_prediag: 2
asof_prediag: "2026-08-18"
---

# ADOPTED｜BULL5 長線多頭 × 5 日回跌（P0）

Steward 貼：

```text
BULL5-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| 全正窗＝H10…H240 | H5<0 | 不用累積遞減當多頭 | 條件≠可交易 | 做空≠可空
```

## 生效

| 角色 | 路徑 |
|---|---|
| 本軌定義 SSOT | `reports/augur_bull5_hstack_pullback_plan_r18_20260819.md` |
| 執行板掛點 | r18 **M32**（已採納；探針未開工） |
| 日常出單 | 仍 standing **H20+H60 RankRidge** |
| 進場閘 | 仍 **UP-PULL-v1**；本軌不放寬 L-B、不盜用「可當進場條件」 |

`adopt`＝凍結 **BULL5-v1**＝H10／20／40／60／90／120／240 log 報酬全＞0 且 H5＜0。**不是**探針閉包、不是把預診 9 檔當買點、不是 #14、不是改 standing。累積％遞減＝`BULL5-CASC-v1`；均線排列＝`BULL5-SMA-v1`；本採納**不開**。

## 本 paste 鎖定

| 條 | 意思 |
|---|---|
| no-promote | 不換冠、不取代 RankRidge 出門 |
| standing=20,60 | 日常出門窗不變 |
| no-fake-B3@08-19 | 最近合法日＝**2026-08-18** |
| 全正窗＝H10…H240 | 現價高於各窗前收＝長線多頭 |
| H5<0 | 只讓近 5 個交易日回跌；不要求 H10 也負 |
| 不用累積遞減當多頭 | H10>H20>…>H240 預診為空頭結構（08-18＝2 檔） |
| 條件≠可交易 | 過閘 ≠ 下單 |
| 做空≠可空 | 空方鏡像＝條件排序，不是可融券可成交 |

不套樣單檔％。不改 UP-PULL／WATCH-PB／RS-CHARGE／TWIN-EX θ。

## 本窗未做（刻意）

`scripts/probe_bull5.py`／P1＠08-18／寫庫／OOS／commit／假 B3＠08-19／CASC／SMA。

下一槍（另貼）：

```text
BULL5-probe-go | date=2026-08-18 | k=10 | dry-run | 條件≠可交易
```
