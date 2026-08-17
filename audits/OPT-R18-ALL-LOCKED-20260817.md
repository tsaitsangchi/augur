---
status: locked
series: optimization_plan
round: r18
date: 2026-08-17
viewpoint: 2026-08-17T10:17+08:00
plan: reports/augur_opt_stepwise_all_problems_r18_20260817.md
adopted: audits/OPT-R18-ALL-PROBLEMS-ADOPTED-20260817.md
paste: "OPT-R18-ALL | no-fake-B3@08-15/16/17 | knife-B=WAIT PriceAdj≥08-17 then L0→L1→L2 | standing=20,60 | H_TRACK=8 | no-promote | NF-pause | kh=check-green | E-keep | stop-at-7 | no-K9-train | M28=clock-WAIT | no-E5 | no-canonical-3plus1"
price_tip: "2026-08-14"
emit_tip: "2026-08-14"
self_reported: true
layer: "[I]"
---

# LOCKED｜OPT-R18-ALL · 開工鎖（nav-only）

Steward 於 10:17+08 貼上 r18 §1 完整 paste。本句＝**鎖門＋確認刀 B 仍 WAIT**，**不是** B3-go、**不是** KH-S0-apply-go、**不是** E5。

## 本窗 LIVE（親查）

| 項 | 值 |
|---|---|
| PriceAdj TAIEX／max | **2026-08-14** |
| `prediction_values` max | **2026-08-14**（H20 286＋H60 286，RankRidge＠08-14） |
| 08-15／16／17 | **無價** → 當 as-of＝假 B3 |
| KH `--check` | S0 FIRE **213**；S1 ok；S3 FIRE zh lag **2**；**未** `--apply` |

## 鎖住的意思

| 子句 | 做 | 不做 |
|---|---|---|
| `no-fake-B3@08-15/16/17` | 守 | `--date 2026-08-15/16/17` |
| `knife-B=WAIT … then L0→L1→L2` | 候價；價到後路徑＝L0（需要時）→ B3 20,60 → 包未齊才 L2 | **現在**不開火；**不**掛自動 watcher；開火仍須另貼 `B3-go` |
| `standing=20,60` `H_TRACK=8` | 日常出門兩窗；軌仍八窗 | 默改八窗 standing |
| `no-promote` `NF-pause` | 守 | SERVE-SWAP；解凍 NF |
| `kh=check-green` | `--check` 已重跑 | `--apply`／抬 >KH2 |
| `E-keep` `stop-at-7` `no-K9-train` | 守 | 放寬 θ；depth≥8；K9 開訓 |
| `M28=clock-WAIT` | 鐘可重讀 | 當已實現 PnL |
| `no-E5` | 守 | `E5-evaluate-go`；塗 established |
| `no-canonical-3plus1` | 守 | 再送就緒 5；倒 31 欄進 prodset |

## 下一槍仍須另貼

```text
B3-go | D=2026-08-17 | horizons=20,60 | no-promote | no-8H-standing
```

```text
KH-S0-apply-go | drain up_to=0 limit=213 | no-lift-gt-KH2
```

本窗 **未** L0／B3／L2；**未** commit。
