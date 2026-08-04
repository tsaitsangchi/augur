# EXECUTED｜LOOP-S4-TO-S5 · 2026-08-04

> **位階**：[I] 執行帳  
> **GO**：`audits/LOOP-S4-S5-FULL-GO-20260804.md`  
> **計畫**：`reports/augur_s4_s5_closed_loop_plan_20260804.md` §3  
> **WAVE-A**：train-matrix **DONE** 13:30+08（`/tmp/s4-wave-a-20260804/train-matrix.log`）；**無** `S4-WAVE-A-EXECUTED*`——本帳消費 P1-C＋Wave A **已落地** artifact，**未重啟** Wave A

---

## 1. 做了什麼

| 步 | 結果 |
|---|---|
| `predict_asof --dry-run` H20／40／60／120 asof=2026-06-30 | **全 RC=0**；未寫庫 |
| OOS 漲跌比／勝率（B2_ridge top20% + H60 GBDT×3 seed） | **完** → `audits/S5-OOS-20260804.md` |
| `direction_gate` 唯讀 | evaluated_pass=**0** |
| predict 寫／sim apply／sync | **未做** |

---

## 2. 引用 artifact

| 來源 | model_id／artifact |
|---|---|
| P1-C | RankRidge H20／H60 · seed42 · `56d03625463b3eba` |
| Wave A（train DONE） | RankRidge H40／H120 · seed42；RankGBDT H20／H60 × seed1/2/42 |

---

## 3. S5 metrics 摘要（詳表見 S5-OOS）

| H | net hit | vs bench hit | net Sharpe | note |
|---|---|---|---|---|
| 20 | 0.639 | ＞0.623 | 1.17 | folds 穩定偏正 |
| 60 | 0.632 | ＞0.579 | **1.30** | 主尺最佳 |
| 40 | 0.567 | **＜**0.633 | 1.14 | 方向尺警示 |
| 120 | 0.875 | ＞0.750 | 1.22 | **n=8** 樣本不足 |
| GBDT H60 | 0.579×3 | ＝bench | med≈1.09 | 不升格挑戰者 |

---

## 4. 旗標守則

skip-sync · no-SIM-apply · GATE-keep · NHC-keep · API-THAW-bounded · 不殺 A1 · 不假確立級 · #9 真 stdout

## 5. 路徑

- GO：`audits/LOOP-S4-S5-FULL-GO-20260804.md`  
- OOS：`audits/S5-OOS-20260804.md`  
- logs：`/tmp/loop-s5-20260804/`  
- Wave A logs：`/tmp/s4-wave-a-20260804/`

*完。self-reported（#32a）。*
