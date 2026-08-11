---
status: paste_ready
series: daily_b3
kind: dual_explicit_paste_card
date: 2026-08-08
viewpoint: 2026-08-08T19:28+08:00
tip: "2026-08-07"
plan: reports/augur_b3_horizons_five_go_plan_20260808.md
prior_serve: audits/SERVE-SWAP-0731-EXECUTED-20260807.md
prior_b3: audits/VERIFY-B3-20260807-EXECUTED-20260808.md
paste: "B3-FIVE-dual-paste-ready | FZ/GATE-keep | hold-#1 | no-exec"
self_reported: true
layer: "[I]"
---

# PASTE-READY｜五窗雙明示（零執行）

> Steward：備齊 paste only。**本檔 ≠ go、≠ 改 standing B3、≠ 換 serve。**  
> hold-#1 續。升格另軌不併。

## 現況錨（唯讀 · tip＝2026-08-07）

| 尺 | 值 |
|---|---|
| `prediction_probability`＠tip | **H20＋H60** 各 285（僅兩窗） |
| standing B3 預設 | `HORIZONS=20,60` |
| RankRidge＠**2026-07-31** registry | **五 H 皆在**（20／40／60／82／120 各 1） |
| SERVE-SWAP-0731 | tip 曾五窗＠**08-06**；之後日更回兩窗 |
| P6＠08-07 | **僅 H20＋H60** 新 calibrator → 擴五窗須誠實處理 H40／82／120 校準缺口 |

## 雙明示（須兩句都貼才算「全開」；可只貼其一）

### A｜只擴日更 B3 窗（不換 serve 釘）

```text
B3-HORIZONS-FIVE-go | FZ/GATE-keep | skip-sync | no-SIM-apply
| tip=2026-08-07 | horizons=20,40,60,82,120 | hold-#1
# CLI（示意）: bash scripts/run_daily_asof_predict.sh --date 2026-08-07 --horizons 20,40,60,82,120
# 先決: RankRidge@0731 五 H 在（✅）；P6 非五窗 → H40/82/120 校準策略須在 GO 內寫死
# ≠ 改 standing 預設；≠ 默 SERVE-FIVE；≠ 修 H20 dead
```

### B｜tip 掛回五 H serve（重 predict＋emit）

```text
SERVE-FIVE-H-go | FZ/GATE-keep | skip-sync | no-SIM-apply
| tip=2026-08-07 | asof=2026-07-31 | horizons=20,40,60,82,120 | hold-#1
# 形同 SERVE-SWAP-0731 縮規重掛＠新 tip；H20 econ=dead 誠實保留
# ≠ 默改 standing B3 預設；≠ promote 挑戰族；≠ 修 dgate
```

### C｜維持兩窗（預設 · 無須 paste）

```text
hold-#1 | B3-horizons=20,60 | no-five-H
```

## 組合裁決

| 貼法 | 效果 |
|---|---|
| 只 A | 該 D（或明示日）五窗 emit；standing 預設可仍 20／60 |
| 只 B | tip 五 H 掛齊；不等於永久改 B3 預設 |
| **A＋B** | 全開五窗路徑（高門檻；校準缺口須寫死） |
| 皆不貼 | **hold**（現況） |

## 禁

- 單句冒充雙明示  
- 默改 `run_daily_asof_predict.sh` 預設 `HORIZONS`  
- 與升格／NF／SIM-apply 綁死  
- 假稱五窗＝econ 轉綠  

*完。等候 Steward 貼 A／B／二者／皆不。*
