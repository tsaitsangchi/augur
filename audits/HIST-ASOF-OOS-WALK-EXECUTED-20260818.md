---
status: executed
series: s1s5_loop
track: V1-oos
date: 2026-08-18
viewpoint: 2026-08-18T11:08+08:00
plan: reports/augur_s1s5_asof_verify_best_next_r18_20260817.md
nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
paste: "再進行其他模型驗証＋過去 as-of 收特徵／訓／驗＋改程式"
self_reported: true
layer: "[I]"
---

# EXECUTED｜V1 OOS 刀（同日 stamp 切開）＋ walk H5

Steward：全問題下一步＋其他模型驗証＋過去 as-of 能否收特徵／訓／驗＋改程式。

## 答

- **可以**用過去 as-of：D ≤ PriceAdj 價頂（現 **2026-08-17**）。08-18＝假 B3。
- 截面 8 族共用當時 `feature_values`。方向臂只在價頂。VECM／TCN／NB／RL 須點名。0812 NF 禁重掃。
- `--ic` 默認 latest≤D **可能同日 stamp**。誠實 OOS＝`--ic --oos`（stamp < panel）。

## 程式

| 檔 | 改什麼 |
|---|---|
| `src/augur/models/registry.py` | `latest_before`（asof_snapshot < D）；回 `asof_snapshot` |
| `src/augur/core/asof_ready.py` | `stamp_kind`／`n_trading_days_after`／`scan_realized_panels` |
| `scripts/predict_asof.py` | `strict_before=` 載更早 stamp |
| `scripts/verify_asof_families.py` | `--oos`／`--walk`；同日 stamp 標旗 |
| `scripts/run_asof_collect_train_verify.sh` | scan 自測跟 08-07 已齊；IC 指引改 `--oos` |
| `scripts/check_asof_ready.py` | scan 末行 OOS IC |

自測：`asof_ready`／`registry`／HIST 殼 **全過**。未寫庫、未 promote。

## Walk H5 OOS（stamp＝07-31；n≈282–284）

| panel | Ridge | GBDT | XGB | KNN |
|---|---|---|---|---|
| 08-07 | −0.0848 | 0.0078 | 0.0086 | 0.0184 |
| 08-06 | −0.1552 | −0.0985 | −0.1074 | 0.0521 |
| 08-05 | −0.0917 | −0.0197 | −0.0706 | −0.0618 |
| 08-04 | −0.0804 | −0.0935 | −0.0663 | 0.0658 |
| 07-31 | no_model（無更早 H5 stamp） | — | — | — |

四 panel 均值：KNN ≈ **0.019**；其餘負；冠軍 Ridge ≈ **−0.10**。IC ≠ 報酬％；單 panel ≠確立；不升格。

JSON：`/tmp/v1-oos-walk.json`。
