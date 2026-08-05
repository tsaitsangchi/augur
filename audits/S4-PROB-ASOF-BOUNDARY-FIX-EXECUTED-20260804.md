---
status: executed
series: s4_model_families
depends_on:
  - reports/augur_s4_probability_asof_boundary_fix_plan_20260804.md
---

# P6 機率校準 AS_OF/exit_date 邊界修補 — 執行紀錄（2026-08-04）

> **性質**：[I] 執行紀錄（計畫＝`reports/augur_s4_probability_asof_boundary_fix_plan_20260804.md`；Steward 授權「選項 A+B 現在執行」）。
> **急迫性**：`augur-probability.service`(:8600)／`augur-advisor.service`(:8399)皆 live running 且直接消費受影響表；修補完成前,live 服務 serve 之 H60 機率源自含 445 列邊界違規之校準器。

---

## 1. 執行內容

### 選項 A——寫入端修補(`scripts/build_probability_oos_sample.py`)

`emit_horizon` 之 `_exit_date` 檢查由「只檢查算不算得出」擴為「算得出**且**未外溢 FREEZE」：

```python
exit_d = _exit_date(cal, test_pd, h)
if exit_d is None or exit_d > AS_OF_DATE:
    continue
```

新增 `AS_OF_DATE = date.fromisoformat(AS_OF)` 常數供比較。

### 選項 B——消費端防禦性雙保險(`scripts/calibrate_relative_probability.py`)

`fit_horizon` 於 `_load` 之後、進入 expanding-purge 迴圈前,新增：

```python
rows = [r for r in rows if r[3] <= FREEZE_DATE]
```

不論寫入端未來是否再有疏漏,serve fit 自身亦守住邊界；過濾列數非 0 會誠實印出警訊(供人工追查上游),非靜默丟棄。

---

## 2. 修補驗證(先證後動,非改完就信)

| 步驟 | 結果 |
|---|---|
| 邏輯抽驗(4 個已知案例,修補前獨立跑) | `2026-03-31`／`2026-04-30`(已知違規)→ `skip=True`；`2026-02-28`／`2025-01-31`(已知乾淨)→ `skip=False`——修補條件精準命中,無誤傷 |
| 清理既有違規列 | `DELETE FROM probability_oos_sample WHERE horizon=60 AND exit_date>'2026-05-31'` → 445 列(非 hand-patch 數值,是刪除「修正後寫入端本就不會產出」之列,對應 CLAUDE #12「改 writer code + 重建」) |
| `--verify`(既有機械斷言) | ✓ 全綠(purge 斷言+方向契約) |
| 目標重跑確認(`--limit-folds 3`,取最後 3 折) | `emit 0 折`——確認修補後之寫入端對最近 3 個測試 panel(`2026-03-31`／`2026-04-30`／`2026-05-31`)**皆正確跳過**(前二者因 exit_date 外溢,後者因 exit_date 算不出),非漏未執行 |
| 重跑 `--fit --horizon 60` | `purge_verified=True`(較修補前之 `False` 已回復)、折數 99/100(較污染前之 101 折減少,因 2 個晚期 panel 已不再產出) |
| 重跑 `--emit --horizon 60 --asof 2026-05-31` | 339 檔,`prediction_probability` H60 列確認指向新(乾淨)校準器 `platt_RankRidge_h60_asof2026-05-31_g5a96c09`(同 id,`ON CONFLICT DO UPDATE` 原地更新為乾淨值,非新增列) |
| 全 horizon 複查(H20/H40/H60/H82/H120) | 五者 `exit_date>FREEZE` 違規列數皆為 **0** |

**修補前後校準器數值對照**(供留痕,非隱藏差異)：

| | 折數 | Brier | ECE | purge_verified |
|---|---|---|---|---|
| 修補前(受污染,101 折) | 101 | 0.2452 | 0.0075 | False |
| 修補後(乾淨,99 折) | 99 | 0.2453 | 0.0078 | **True** |

數值差異極小(Brier Δ=0.0001,ECE Δ=0.0003)——與計畫書 §2 之預期(1.3% 訓練列擾動,數值影響應小)相符；但修補之意義不在數值大小,而在恢復「serve 校準器僅 fit 於 FREEZE 內已實現標籤」之快照一致性承諾(A-29)。

---

## 3. Live 服務影響確認

- `serve_probability_ui.py`(`_calibrators`/`_stock_rows`/`_leaderboard`/`_stock_ids`)與 `src/augur/advisor/payload.py`(prediction_probability 讀取段)皆為**逐請求即時 `SELECT`**,無啟動時快取——**修補後之乾淨資料立即生效,無需重啟服務**(已讀碼確認,非假設;呼應 CLAUDE #7 之反面情境——本次修補屬純資料修正、非服務程式碼變更,不落入「服務常駐記憶體吃到舊碼」之陷阱)。
- `augur-probability.service`／`augur-advisor.service` 現況皆 `active running`,下一次任何使用者請求 H60 機率,即讀到修補後之乾淨值。

---

## 4. 硬邊界遵守確認

- ✓ 未 hand-patch 任何數值(#12)——刪除之 445 列是「移除不該存在的列」,校準器 `a,b` 參數由 `_platt_fit` 重新計算得出,非手改。
- ✓ 未觸碰 `TaiwanStockPriceAdj` 等真實價格資料——本修補純屬「校準器訓練集之列篩選範圍」。
- ✓ 零 FinMind／FRED、零 sim `--apply`、零 `direction_gate`/`arena_admission_gate` 觸碰。
- ✓ H20/H40/H82/H120 未受影響(修補前即 0 違規,修補後亦驗證仍 0)——本次動作範圍精準限於 H60 之既有污染。
- ✓ 選項 C(AS_OF 是否該隨 live 增量滾動)、選項 D(P6 是否為一次性快照)**均未動**——依計畫書建議另案處理,本次僅執行 A+B。

---

## 5. 結論

`build_probability_oos_sample.py`(選項 A)與 `calibrate_relative_probability.py`(選項 B)之 AS_OF/exit_date 邊界缺口已修補並驗證；H60 之 445 列既有污染已清理；`probability_calibrator`／`prediction_probability` 已回復乾淨狀態(`purge_verified=True`);live 服務已即時受益,無需重啟。選項 C／D 之架構層問題留待另裁(計畫書§5 待決問題 5)。
