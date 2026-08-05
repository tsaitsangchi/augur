---
status: draft
series: s4_probability
depends_on:
  - reports/augur_s4_probability_asof_boundary_fix_plan_20260804.md
  - audits/S4-PROB-ASOF-BOUNDARY-FIX-EXECUTED-20260804.md
---

# P6 AS_OF 選項 C／D — 架構／使用紀律 plan-first（2026-08-05）

> **性質**：[I] plan-first（憲章第六部；CLAUDE #20）。**不含**任何 `--run`／live 重灌／gate 改判準。
> **觸發**：`audits/S4-PROB-ASOF-BOUNDARY-FIX-EXECUTED-20260804.md`／邊界修補計畫執行後記——選項 A+B 已落地；**選項 C／D 明示留待另案**。
> **self-reported（#32a）**：本文為 AI 呈案；裁示權屬 Steward。

---

## 0. 一句話

**A+B 已保證「無論 AS_OF 取何值，exit_date 不得越界」；C／D 回答的是另一個問題——這個寫死的 `AS_OF="2026-05-31"` 本身該不該隨 live 滾動（C），還是把整條 P6 管線當歷史一次性快照（D）。二者正交、可並存，但預設行為只能擇一。**

---

## 1. 現況（讀碼＋既有 EXECUTED，非猜測）

| 錨 | 現況 |
|---|---|
| `build_probability_oos_sample.AS_OF` | 常數 `"2026-05-31"` |
| `calibrate_relative_probability.FREEZE` | 同常數 |
| 選項 A | 寫入端跳過 `exit_date > AS_OF` |
| 選項 B | serve fit 再過濾 `exit_date ≤ FREEZE` |
| live 消費 | `augur-probability`／`augur-advisor` 逐請求查表（無快取） |
| `feature_values`／價 | 已 live 增量（遠超 2026-05-31） |

**不變式（A+B 已守）**：校準訓練集不得含「標籤窗超出快照錨」之列。  
**未決（本檔）**：快照錨要不要動、以及「是否鼓勵重跑」。

---

## 2. 選項對照

| | **C — AS_OF 參數化／可滾動** | **D — 一次性歷史快照紀律** |
|---|---|---|
| **是什麼** | `AS_OF`／`FREEZE` → CLI `--asof`（預設可仍＝2026-05-31）；重跑時明示新錨 | 文件＋腳本標頭標「歷史一次性；無 `--limit-folds` 之全量 `--run` 不建議」；既有輸出當定案封存 |
| **要改碼？** | 是（兩支腳本常數→參數；文件／`FAMILY_NOTE`／A-29 誠實標記可能連動） | 否（或僅 docstring／HANDOFF 紀律句） |
| **要重灌？** | 若滾到新錨＝**是**（全 horizon materialize＋fit＋emit；觸 live serving） | 否 |
| **與 A+B** | 相容（滾動後 A+B 仍守 exit 邊界） | 相容（紀律層；A+B 當安全網） |
| **風險** | 連動 `econ_verdict_rule`／呈現偏差／歷史可比性；誤滾＝污染 live 機率 UI | 管線與「live 增量維運」敘事張力；DIRFAMILY 等仍可能重跑相對分量 |

**可並存讀法（推薦預設）**：
- **短期採 D 精神**：不主動滾 AS_OF；全量重跑需 Steward 明示 as-of。
- **中期若採 C**：先參數化、預設仍釘 2026-05-31；**滾動＝另句授權＋另次重灌**，非改常數即自動滾。

---

## 3. (a) table schema

| 表 | 本計畫是否改 schema |
|---|---|
| `probability_oos_sample`／`probability_calibrator`／`prediction_probability` | **否**（C 若執行＝重寫列值／新 calibrator_id，非改 DDL） |
| 新表 | **無** |

## 4. (b) python 規畫（僅在授權 C 或「C 參數化、預設釘死」時）

| 檔 | C（參數化） | D（紀律） |
|---|---|---|
| `scripts/build_probability_oos_sample.py` | `AS_OF` → `--asof`（default 現值） | docstring／矩陣加「歷史快照；全量重跑須明示」 |
| `scripts/calibrate_relative_probability.py` | `FREEZE` 與 `--asof` 對齊語意 | 同上 |
| live 服務 | 不改；仍讀最新 calibrator／emit 列 | 不改 |
| HANDOFF／r6 | 記裁示句 | 記「不建議無授權全量重跑」 |

**不在範圍**：FinMind／FRED；`direction_gate`；DIRFAMILY Phase 1；自動每日滾 AS_OF cron。

---

## 5. 分階段與驗收

| 階段 | 內容 | Gate | 另授權？ |
|---|---|---|---|
| **Phase 0（本檔）** | 裁示 C／D／「C 參數化＋預設釘死＋D 紀律」 | Steward 一句書面 | 本檔即呈裁 |
| **Phase 1a**（若裁 C 參數化） | 兩支腳本 `--asof`；預設＝2026-05-31；行為不變性 | 預設路徑 bit／數字不變 | 是 |
| **Phase 1b**（若裁滾到新錨） | 明示新 as-of＋全量重灌＋live 驗 `purge_verified` | 新錨下 A+B 全綠；UI 抽驗 | **是（高風險）** |
| **Phase D-only** | 僅文件／標頭紀律 | 零碼或僅 docstring | 低；仍建議明示 |

---

## 6. 硬邊界

- FZ/GATE-keep；skip-sync；no-SIM-apply。
- **禁止** AI 自行把 AS_OF 改成「今天」或掛 cron 滾動。
- 滾動重灌＝觸 live serving → 須 #26 授權四要件留痕。

---

## 7. 請 Steward 裁示（擇一或組合）

1. **D-only**：維持釘死 2026-05-31＋使用紀律（零／近零碼）
2. **C-param-default-pin**：參數化、預設仍 2026-05-31、滾動另句（推薦若預期未來要跟 live）
3. **C-roll-now**：參數化＋立即滾到指定 as-of 並重灌（須同時給目標日）
4. **defer**：本輪不裁，P6 維持 A+B 現況

---

*定版（2026-08-05）。下一手＝Steward 裁示上表；未裁前不改碼、不重灌。*
