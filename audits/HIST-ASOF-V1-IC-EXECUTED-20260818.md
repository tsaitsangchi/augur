---
status: executed
series: s1s5_loop
track: V1
date: 2026-08-18
viewpoint: 2026-08-18T08:40+08:00
plan: reports/augur_s1s5_asof_verify_best_next_r18_20260817.md
nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
paste: "HIST-ASOF-V1-IC | D=07-31 H5+H10 / D=08-07 H5 | dry-run | no-write | no-promote | NF-pause"
self_reported: true
layer: "[I]"
---

# EXECUTED｜其他模型歷史 as-of V1 rank IC（唯讀）

Steward：全問題下一步＋用過去 as-of 收特徵／訓／驗＋改程式。

## 答

- **可以**用過去 as-of：D ≤ PriceAdj 價頂（現 **2026-08-17**）；截面 8 族共用當時 `feature_values`。08-18＝假 B3。
- **本窗未訓**：07-31／08-14／08-17 截面已 64／64。08-07／08-10 僅 12／64——補齊須另貼 `HIST-ASOF-apply | track=all`（方向臂不覆寫）。
- **V2／V4 未開**：VECM／TCN／NB／RL 登錄＝0；0812 NF 禁重掃。`--track other --apply` 仍 **rc=6**。

## 程式

| 檔 | 改什麼 |
|---|---|
| `src/augur/core/asof_ready.py` | `label_is_realized`／族矩陣／其他車道盤點 |
| `scripts/verify_asof_families.py` | **新**：V0 盤點＋已實現窗 rank IC（dry-run predict） |
| `scripts/check_asof_ready.py` | `--family-matrix`；假 B3 例改 08-18 |
| `scripts/run_asof_collect_train_verify.sh` | `--track other --dry-plan`＝V0（rc=0）；`--apply` 仍 rc=6 |
| `scripts/predict_asof.py` | `quiet=`（批次驗証不印投組） |

自測：`python -m augur.core.asof_ready --selftest`；`bash scripts/run_asof_collect_train_verify.sh --selftest` 全過。

## V1（單 panel；≠確立；IC ≠ 報酬％）

價頂 08-17 ⇒ H5 最晚已實現 panel＝**08-07**；H10＝**07-31**。模型＝`registry.latest ≤ D`。未寫 `prediction_values`。

**H5＠08-07**（OOS：模型 stamp 07-31；n=284）

| 族 | IC | spread |
|---|---|---|
| RankXGB | 0.0086 | 0.0203 |
| RankGBDT | 0.0078 | 0.0071 |
| RankKNN | 0.0184 | −0.0021 |
| RankRF | −0.0241 | 0.0179 |
| RankCat | −0.0322 | 0.0181 |
| RankMLP | −0.0636 | 0.0107 |
| RankSVM | −0.0798 | 0.0066 |
| RankRidge | −0.0848 | 0.0055 |

**H10＠07-31**（n=204）：八族 IC 皆負（Ridge −0.1505 … KNN −0.0661）。

**H5＠07-31**：RankKNN IC＝**1.0**（同日 stamp）——**不可信、不升格**；下一 panel 08-07 掉到 0.018。其餘族多數負。

JSON：`/tmp/v1-asof-2026-07-31.json`、`/tmp/v1-asof-2026-08-07.json`。

未 promote、未 sim-apply、未假 B3＠08-18、未開 NF。
