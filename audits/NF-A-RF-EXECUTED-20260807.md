---
status: executed
series: s4_models
track: NF-A-RF
date: 2026-08-07
viewpoint: 2026-08-07T09:52+08:00
paste: "NF-A-RF-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default"
go: audits/NF-A-RF-GO-20260807.md
plan: reports/augur_nf_a_rf_go_plan_20260807.md
logdir: /tmp/nf-a-rf-20260807/
champion_freeze_H60: {sharpe: 1.3016, hit: 0.6316}
source_champ: audits/S5-OOS-20260804.md
prior: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
self_reported: true
promote: false
layer: "[I]"
---

# EXECUTED｜NF-A-RF-go · RankRF H60×{42,1,2} · until=2026-06-30

## 1. 護欄

| 項 | 實況 |
|---|---|
| FZ/GATE-keep | **守** — 冠軍門檻寫死後才跑；未改 LIVE serve；未改 dgate |
| skip-sync | **守** — 零 FinMind／FRED |
| no-SIM-apply | **守** |
| seeds≥3 · H60 · until=2026-06-30 | **守** |
| no-promote-default | **守** — `PROMOTE=False`／`STOP_PROMOTE` |
| 其他族 NF-pause | **keep**（本波僅 RankRF） |
| #1 B3＠08-07 | **未**假 B3；本窗無 LIVE B3 競合 |

## 2. #14（主驗收）

探針：`/tmp/nf-a-rf-20260807/probe_rf_h60.py` → `portfolio.run_backtest(..., model="RankRF")`  
口徑：prodset 3 特徵 · top20% · equal · cost=0.585% · nonoverlap · until=2026-06-30  
`panel_hash=ca1b6ff379` · `n_panels=22` · backtest `n_periods=19`

| seed | net Sharpe | hit |
|---|---|---|
| 42 | 1.0206 | 0.6316 |
| 1 | 1.1169 | 0.6316 |
| 2 | 1.1068 | 0.6316 |

**min / med / max Sharpe = 1.0206 / 1.1068 / 1.1169**；**min hit = 0.6316**

| 尺 | 預凍冠軍 | 實測 | 判定 |
|---|---|---|---|
| min Sharpe > 1.3016 | 1.3016 | 1.0206 | ✗ |
| min hit ≥ 0.6316 | 0.6316 | 0.6316 | ✓（持平） |

→ **STOP promote**（三 seed 皆遠低於冠軍 Sharpe；與 `S4-WAVE-A-SKLEARN-EVAL-20260804` H60 RankRF 數字**逐 seed 一致**）。

## 3. train_ranker（副產物）

三 seed 皆完成 **fit + joblib**：

- `models_artifacts/RankRF_H60_2026-06-30_seed{42,1,2}_56d03625463b3eba.joblib`

**registry 寫入失敗**（三次同因）：

```text
CheckViolation: model_family_chk
ALLOWED = RankRidge|RankGBDT|MktLogit|DirStack|DailyLogit|DailyGBDT|DailyGBDT_cal|MktGBDT|DirStackM
# RankRF 不在 CHECK 內 → 碼可訓、不可入 model_registry
```

解讀：Wave-A adapter **可評不可登**（與 08-04 Phase 0「零 registry」結果一致、機制更清楚）。修 CHK＝另句 schema GO，**本帳不自動 ALTER**。

## 4. 決策

- **不**升格／**不**換 LIVE serve／**不**撤全域 NF-pause  
- RankRF H60 再驗＝**仍未過門**；預設佇列可繼續 A-3c XGB 等 **僅在**另句 `NF-*-go`  
- 殘件：orphan joblib ×3（無 registry 列）— 可留作挑戰重載或之後 schema GO 回填

## 5. 日誌

- master：`/tmp/nf-a-rf-20260807/master.log`
- probe：`/tmp/nf-a-rf-20260807/probe-h60.log`
- train：`/tmp/nf-a-rf-20260807/train-h60-seed{42,1,2}.log`

*完。[I] executed · no promote.*
