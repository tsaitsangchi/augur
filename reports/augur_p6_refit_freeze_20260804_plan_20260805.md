---
status: plan_first
series: s4_probability
depends_on:
  - audits/S4-P6-ASOF-CD-EXECUTED-20260805.md
  - reports/augur_daily_asof_predict_emit_runbook_20260805.md
---

# P6 重 fit／FREEZE→2026-08-04 plan-first（2026-08-05）

> **性質**：[I] plan-first。**本檔零灌庫**。  
> **裁示意向**：Steward 選 `freeze_0804`＝錨 2026-08-04，H20＋H60 必要 oos → fit → emit。  
> **self-reported（#32a）**。

## 0. 一句話

**滾 FREEZE≠只改 `--emit --asof`**：emit 只套校準器到新分位；要把校準器本身改成「看見 05-31→08-04 之間已實現標籤」須先 **重建 OOS 對樣本** 再 **`--fit --asof 2026-08-04`**，最後再 emit。

## 1. 現況債

| 表 | 現況 |
|---|---|
| `probability_oos_sample` H20 | max exit≈**2026-05-04**（panel 頂≈03-31） |
| 同 H60 | max exit≈**2026-05-28**（panel 頂≈02-28） |
| calibrator | 多支仍 `…asof2026-05-31…`；H60 最新含 `platt_RankRidge_h60_asof2026-05-31_g5a96c09` |
| `prediction_probability`＠08-04 | 已有 H20／H60 emit，但 **Platt 仍為舊 FREEZE 訓練** |

A+B 邊界已守：`exit_date > FREEZE` 不進 fit。

## 2. 建議執行序（需另 GO）

```text
P6-REFIT-FREEZE-2026-08-04-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# horizons=20,60  family=RankRidge
```

1. `build_probability_oos_sample.py --run --horizon 20 --asof 2026-08-04`  
2. 同上 `--horizon 60`  
3. `calibrate_relative_probability.py --fit --horizon 20 --asof 2026-08-04`  
4. 同上 `--fit --horizon 60`  
5. `--emit --horizon 20 --asof 2026-08-04`  
6. `--emit --horizon 60 --asof 2026-08-04`  

可選最小驗證：先 `--limit-folds 2` 煙測再開全量。

## 3. 風險／誠實界

| 風險 | 說明 |
|---|---|
| CPU | 全量 OOS＝逐折 refit Ridge；H20／H60 可能數十分～數小時 |
| 標籤未齊 | H60 近窗折不足「60 交易日已實現」→折數少於直覺（正常、禁灌未來） |
| live 覆蓋 | emit 後顧問即讀新 calibrator（`ORDER BY created_at DESC`）；舊 05-31 列保留可溯 |
| 非確立級 | 不改 dgate；econ_verdict 規則表照舊 |

## 4. 不做（本 GO 外）

重訓 RankRidge；撤 NF-pause／β5；sim-apply；`--all` horizons（40/82/120）；改 DEFAULT_FREEZE 常數（CLI `--asof` 即可）。

## 5. 驗收

- 新 `calibrator_id` 含 `asof2026-08-04` 且 `purge_verified=True`  
- emit＠08-04 指向新 id  
- `--report` 印 Brier／ECE（允許貼近 0.5 窄帶＝誠實薄 edge）

*候 GO。*
