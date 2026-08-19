---
status: adopted
series: s4_s5_verify
round: r18
date: 2026-08-19
viewpoint: 2026-08-19T08:30+08:00
plan: reports/augur_uptrend_pullback_ls_top10_plan_r18_20260819.md
layer: "[I]"
self_reported: true
paste: "UP-PULL-plan-adopt | policy=strict | k=10 | no-promote | standing=20,60 | no-fake-B3 | 做空≠可空 | 路徑％≠未來％"
---

# ADOPTED｜長線結構 × 短線進出 Top10（P0）

Steward 貼：

```text
UP-PULL-plan-adopt | policy=strict | k=10 | no-promote | standing=20,60
| no-fake-B3 | 做空≠可空 | 路徑％≠未來％
```

## 生效

| 角色 | 路徑 |
|---|---|
| 本軌定義 SSOT | `reports/augur_uptrend_pullback_ls_top10_plan_r18_20260819.md` |
| 執行板掛點 | r18 **M29**（已採納；探針未開工） |
| 日常出單 | 仍 standing **H20+H60 RankRidge**；本軌不覆蓋 |

`adopt`＝凍結兩段硬閘、排序鍵、填滿政策 **strict**、k=10、護欄。**不是**探針腳本、不是輸出名單、不是可交易、不是 #14、不是改 `prediction_values`。

## 本 paste 鎖定

| 條 | 意思 |
|---|---|
| policy=strict | 過閘幾檔列幾檔；不足 10 **不補**、不暗改 θ |
| k=10 | 上限 10；08-18 預診做多 5／做空 2 → 就列那麼多 |
| no-promote | 不換冠、不 SERVE-SWAP、不取代 RankRidge |
| standing=20,60 | 日常出門窗不變 |
| no-fake-B3 | 08-19 價未進不當 as-of；最近合法日＝**2026-08-18** |
| 做空≠可空 | 空方表＝條件排序；非融券、非下單 |
| 路徑％≠未來％ | 閘用已發生路徑；表頭必須寫明 |

θ 變體（soft-fill／relax-A／改回撤帶）須**另句**，不得沿用 v1 名稱。

## 本窗未做（刻意）

`probe_uptrend_pullback.py`／跑 08-18 名單／寫庫／OOS walk／模型／commit／假 B3＠08-19。

下一槍（另貼，不預設連發）：

```text
UP-PULL-probe-go | date=2026-08-18 | side=both | k=10 | policy=strict
```
