---
status: executed
series: s4_s5_verify
track: V1
horizon: 20
date: 2026-08-07
viewpoint: 2026-08-07T09:25+08:00
go: audits/S4-V1-REVERIFY-H20-GO-20260807.md
in_progress: audits/S4-V1-REVERIFY-H20-INPROGRESS-20260807.md
prior_h60: audits/S4-V1-REVERIFY-EXECUTED-20260806.md
prior_oos: audits/S5-OOS-20260804.md
scope: "H20 · B2_ridge + M1_gbdt×{42,1,2} · ENS 對照 · prodset · until=2026-06-30"
logs: /tmp/s4-v1-reverify-h20-20260807/
panel_hash: 26e4c2daaa
layer: "[I]"
self_reported: true
---

# EXECUTED｜S4-V1-REVERIFY · H20 · 2026-08-07

> **一句**：H20 prodset×三 seed 重跑完；hash **26e4c2daaa**（＝S5-OOS H20）；M1 **全 seed Sharpe＜bench** → 不升格；`evaluated_pass=0`。

---

## 0. 護欄

| 項 | 結果 |
|---|---|
| 範圍 | Steward＝**h20**（H60 不重跑） |
| until | **2026-06-30** |
| 三 seed | 42→1→2 全 rc=0（≈07:58–09:24+08） |
| NF／sim／dgate 寫 | **未動** |

---

## 1. 尺

```text
prodset · active3 · h=20 · cost=0.00585 · 66 非重疊 panel
panel hash=26e4c2daaa · 主讀 top20%/equal net
```

---

## 2. #14（top20%/equal net）

### B2_ridge（確定性）

| seed | net Sharpe | 勝率 | CAGR | bench Sharpe |
|---|---|---|---|---|
| 1／2／42 | **1.21** | **64%** | +20.0% | 0.86／62% |

對照 S5-OOS：1.1684／0.639。本窗 **1.21／64%**——同 hash 軟差；**#14 方向仍：淨 Sharpe≫bench**。

### M1_gbdt · #11

| seed | net Sharpe | 勝率 |
|---|---|---|
| 1 | **0.75** | 62% |
| 2 | **0.78** | 57% |
| 42 | **0.81** | 62% |

| 統計 | Sharpe |
|---|---|
| **min／med／max／mean** | **0.75／0.78／0.81／0.78** |

→ **三 seed 全＜bench 0.86** → **禁升格**；禁單 seed 勝謊。

### ENS（對照）

seed 42／1／2 net Sharpe：**1.14／1.12／1.13**（皆＜B2 1.21）→ **不改冠軍**。

---

## 3. direction_gate

**evaluated_pass=0**（不變）。

---

## 4. 與 H60 V1／backlog

| | H60（08-06） | H20（本窗） |
|---|---|---|
| B2 vs bench | 優 | 優 |
| M1 | 含 seed＜bench | **全 seed＜bench** |
| 升格 | 否 | **否** |

→ `S4-REOPT-BACKLOG-20260807` 項1–3 **維持**（H60＞H20 主尺；M1／ENS 不升格）。H20 仍服務掛、**econ=dead 敘事不變**（本尺≠econ_verdict）。

---

## 5. 路徑

- GO／本帳／log：`audits/S4-V1-REVERIFY-H20-*` · `/tmp/s4-v1-reverify-h20-20260807/`

*完。[I]；self-reported。*
