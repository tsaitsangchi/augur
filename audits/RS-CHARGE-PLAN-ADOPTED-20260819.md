---
status: adopted
series: s4_s5_verify
round: r18
date: 2026-08-19
viewpoint: 2026-08-19T11:05+08:00
plan: reports/augur_rs_charge_qihong_yanhua_plan_r18_20260819.md
product_id: RS-CHARGE-v1
layer: "[I]"
self_reported: true
paste: "RS-CHARGE-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19 | pool=Ridge八窗均分Top10 | L-A∧L-D∧H5>0∧H10>0 | 無L-C | 觀察≠進場 | 做空≠可空"
---

# ADOPTED｜RS-CHARGE 相對強×短窗仍衝（P0）

Steward 貼：

```text
RS-CHARGE-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| pool=Ridge八窗均分Top10 | L-A∧L-D∧H5>0∧H10>0 | 無L-C | 觀察≠進場 | 做空≠可空
```

## 生效

| 角色 | 路徑 |
|---|---|
| 本軌定義 SSOT | `reports/augur_rs_charge_qihong_yanhua_plan_r18_20260819.md` |
| 執行板掛點 | r18 **M33**（已採納；探針未開工） |
| 日常出單 | 仍 standing **H20+H60 RankRidge**；本軌不覆蓋 |
| 進場閘 | 仍 **UP-PULL-v1**；本軌不放寬 L-B、不盜用「可當進場條件」 |

`adopt`＝凍結池＝Ridge 八窗均分 Top10、閘＝L-A∧L-D∧H5>0∧H10>0、**無 L-C**、排序＝均分降序、護欄。**不是**探針閉包、不是可交易、不是把 §4 預診 7／1 當買點、不是 #14、不是改 `prediction_values`。

## 本 paste 鎖定

| 條 | 意思 |
|---|---|
| no-promote | 不換冠、不 SERVE-SWAP、不取代 RankRidge 出門 |
| standing=20,60 | 日常出門窗不變 |
| no-fake-B3@08-19 | 08-19 價未進不當 as-of；最近合法日＝**2026-08-18** |
| pool=Ridge八窗均分Top10 | 相對強池；分數≠％；dry-run |
| L-A∧L-D∧H5>0∧H10>0 | 長窗全正、結構未破、短窗仍雙正 |
| 無L-C | 不要求距 20 日高 −15%～−3%（研華才進得來） |
| 觀察≠進場 | 一律「等回撤／等反彈，不是進場」 |
| 做空≠可空 | 空方＝條件排序；非融券、非下單 |

不用奇鋐／研華單檔％套樣。改池為全宇宙＝`RS-CHARGE-UNI-v1` 另句。不改 WATCH-PB／BULL5／UP-PULL θ。

## 本窗未做（刻意）

`scripts/probe_rs_charge.py`／P1＠08-18／寫庫／OOS／commit／假 B3＠08-19。

下一槍（另貼，不預設連發）：

```text
RS-CHARGE-probe-go | date=2026-08-18 | k=10 | dry-run | 觀察≠進場
```
