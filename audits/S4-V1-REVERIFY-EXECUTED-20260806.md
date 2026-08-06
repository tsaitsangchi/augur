---
status: executed
series: s4_s5_verify
track: V1
date: 2026-08-06
viewpoint: 2026-08-06T17:00+08:00
go: audits/S4-V1-REVERIFY-GO-20260806.md
in_progress: audits/S4-V1-REVERIFY-INPROGRESS-20260806.md
plan: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
prior_oos: audits/S5-OOS-20260804.md
scope: "H60 core · B2_ridge + M1_gbdt×{1,2,42} · ENS 對照 · prodset · until=2026-06-30"
logs: /tmp/s4-v1-reverify-20260806/
panel_hash: ca1b6ff379
layer: "[I]"
self_reported: true
---

# EXECUTED｜S4-V1-REVERIFY · H60 核心 · 2026-08-06

> **一句**：同尺重跑 H60 prodset×三 seed；panel hash **ca1b6ff379**（＝S5-OOS）；**禁**單 seed 升格、**禁**確立級。  
> **#1**：PriceAdj 仍 **08-05**；未搶 B3；`evaluated_pass=0`。

---

## 0. 護欄

| 項 | 結果 |
|---|---|
| GO 範圍 | Steward＝**h60_core**（H20/40/120 本窗不做） |
| asof／until | 價 LIVE=08-05；OOS **until=2026-06-30**（未假 08-06） |
| skip-sync／no-SIM-apply／NF-pause | **守** |
| 三 seed | **42→1→2** 全 rc=0（≈16:45–16:59+08） |

---

## 1. 尺與特徵

```text
feature_source=prodset
feats=['cycle_position_252d','inst_cumflow_position_120d','lending_fee_rate_mean_30d']
h=60 · cost=0.00585 · since=2021-01-01 · until=2026-06-30
panel hash=ca1b6ff379 · 22 非重疊 panel · 19 期回測
主讀：top20%/equal net
```

---

## 2. #14 結果（top20%/equal net）

### 2a B2_ridge（確定性；三 seed 同位）

| seed | net Sharpe | 勝率 | CAGR | vs bench Sharpe 1.10／勝率 58% |
|---|---|---|---|---|
| 1／2／42 | **1.25** | **58%** | +26.6% | Sharpe **優於** bench；勝率＝bench |

對照 `S5-OOS-20260804`：net Sharpe **1.3016**／net hit **0.6316**。  
本窗 stdout 2 位＝**1.25／58%**——**同 hash／同 feats，數字非 byte 復現**（軟漂移／印出粒度／資料修訂風險）；**#14 方向仍成立**（淨 Sharpe＞基準），**不作**「完全重現 1.30」宣稱。

### 2b M1_gbdt · #11 三 seed

| seed | net Sharpe | 勝率 | CAGR | vs bench |
|---|---|---|---|---|
| 1 | 1.18 | 68% | +21.4% | Sharpe＞bench |
| 2 | **0.97** | 68% | +17.3% | Sharpe **＜**bench |
| 42 | 1.09 | 68% | +20.0% | ≈／微劣於 1.10 門檻帶 |

| 統計 | Sharpe |
|---|---|
| **min／med／max／mean** | **0.97／1.09／1.18／1.08** |

對照 S5-OOS：1.031／1.090／1.153／hit 全＝0.5789。  
本窗 med 近；**seed2＜bench** → **禁升格挑戰者**；禁單 seed（seed1）勝出謊。勝率 68%≠Sharpe 優勝（幅度／成本結構）。

### 2c ENS_ridge_gbdt（對照·非升格）

| seed | net Sharpe top20%/equal |
|---|---|
| 42 | 1.25 |
| 1 | 1.16 |
| 2 | 1.26 |

仍處 Ridge／GBDT 之間或貼近 Ridge；**不**因單 seed ENS＞B2 改冠軍（與既有 ensemble 未過門敘事一致）。

---

## 3. direction_gate（唯讀）

| status | |
|---|---|
| **evaluated_pass** | **0** |

→ 本重覆驗 **≠** 確立級／可交易核准。

---

## 4. 結論

1. V1 H60 核心 **EXECUTED**；三 seed 齊。  
2. **冠軍敘事不變**：B2_ridge 淨 Sharpe 穩優於 bench；M1 **不得**升格。  
3. 與 08-04 檔有 **軟數字差**（尤其 B2 hit／Sharpe）——已誠實記；後續若要硬對帳另開 reproprobe。  
4. H20／全表／Direction 重訓 **未授權本窗**。  
5. NF-pause／#1 hold **仍在**。

---

## 5. 路徑

- GO：`audits/S4-V1-REVERIFY-GO-20260806.md`  
- 本帳：`audits/S4-V1-REVERIFY-EXECUTED-20260806.md`  
- log：`/tmp/s4-v1-reverify-20260806/econ-h60-seed{42,1,2}.log`

## 6. 建議下一句

| 若… | 貼 |
|---|---|
| S5→S4 回饋 | `LOOP-S5-TO-S4-OPT-run` |
| 擴 H20 V1 | 另 `S4-V1-REVERIFY-go`＋明示 horizon |
| A 到後 B3 | （watcher 自動；勿假跑） |

*完。[I] executed；self-reported。*
