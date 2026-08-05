---
status: executed
series: s4_models
depends_on:
  - audits/S4-WAVE-B-ADAPTER-PHASE0-EXECUTED-20260805.md
  - reports/augur_s4_wave_b_classical_ts_adapter_plan_20260805.md
---

# S4-Wave-B-ADAPTER Phase 0b EXECUTED（2026-08-05）

> **性質**：[I] audit。**self-reported（#32a）**；數字出自 (a) stdout。  
> **邊界**：另書量尺（方向 hit vs naive）；**≠** #14 可交易；**不進 Phase 1 自動**。

---

## 1. 預凍門檻（跑前寫定）

`mean(ARIMA hit) > mean(naive hit)`（每股 hit 先平均，再比整體 mean）。  
宇宙＝core_universe_asof `as_of_date=2026-05-31` 前 15 檔；`h=20`；月步 `step=21`；近端 `max_folds=36`；訓練窗 `train_window=504`（滾動、非全史 expanding——全史 MLE 不可完成級慢，探針改近端窗並留本句誠實標註）。

CLI：`scripts/probe_classical_ts_phase0b.py --run --n-stocks 15 --horizon 20 --asof 2026-05-31 --max-folds 36`

---

## 2. 結果（stdout 彙總）

| 尺 | 值 |
|---|---|
| 有效股 | **15**/15 |
| ARIMA mean hit | **0.5370**（min/med/max＝0.278／0.556／0.694） |
| naive mean hit | **0.5185**（min/med/max＝0.306／0.528／0.639） |
| 每股贏地板 | **9**/15 |
| 判定 | **✓ 有證據**（嚴格 > naive） |

逐股：`1102/1104/1109/1210/1229/1231` 未贏地板；其餘 9 檔贏。log＝`/tmp/classical-ts-phase0b.log`（本機）。

---

## 3. 結論與下一步

- **有證據勝過 naive 地板**——仍 **≠ 可交易**、不得與 RankRidge #14 混稱。  
- **不自動進 Phase 1**（全宇宙／registry／熱路徑接線須另 GO）。  
- 探針加速口徑（504 窗／36 折）已寫入本帳；若 Steward 要求「全史 expanding」須另授長跑窗。

---

*EXECUTED 2026-08-05。*
