# SIM-S0-RESIDUAL：`tw.daily_bar` authoritative-binding（2026-08-04）[I]

> **位階**：[I] 執行／診斷留痕（非 META-CONSTITUTION [N]）。  
> **授權（exact）**：`SIM-S0-RESIDUAL: tw.daily_bar authoritative-binding | GATE-keep | no-SIM-apply`  
> **REGISTRY-GO（exact）**：`REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo` → ✅ **EXECUTED**  
> **計畫**：`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`  
> **上游 Discovery**：`audits/SIM-SELF-EVOLVE-S0-DISCOVERY-20260804.md`（D-CELL）  
> **self-reported（#32a）**：數字出 (a) stdout／(b) DB。  
> **硬守**：GATE-keep · no-SIM-apply · 零 FinMind 放量 · 不殺 A1 · 零 git commit

---

## 1. 診斷（殘差窗；COMMIT 前）

| 層 | 機制 | COMMIT 前實證 |
|---|---|---|
| 消費端 | `check_sim_clock._snapshot` → `resolve_sql("tw.daily_bar")` → TAIEX 日曆錨 | 權威 NULL → `UnmappedConcept`（WM.35 fail-closed） |
| Registry | `world_concept_registry_current.authoritative_binding_id` | **NULL**；`decided_by` NULL；category=`event` |
| 通道候選 | binding **75** `TaiwanStockPrice`（observation, mapped）／**81** Adj（derived, mapped） | 與 Annex F §1.2 一致 |
| 權威建議 | Annex F §2.1＝**75**（raw）；不採 81 | 備料 SSOT，非本窗發明 |

---

## 2. 本窗／後續落地

| 動作 | 結果 |
|---|---|
| DRY SQL 備料 | ✅ `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-DRY-SQL-20260804.md` |
| honesty／REGISTRY-GO 呈請 | ✅ `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-HONESTY-REQUEST-20260804.md` |
| honesty 發證 | ✅ `audits/U0-75-HONESTY-ISSUED-20260804.md`（COMMIT 後**已消費**） |
| Registry COMMIT `authoritative_binding_id=75` | ✅ `audits/U0-75-REGISTRY-EXECUTED-20260804.md`（`decided_at=2026-08-04 13:37:44+08`） |
| `check_sim_clock` 誠實降級碼 | ✅ 仍保留（Unmapped 時不 traceback）；權威採認後路徑不再觸發 |

---

## 3. COMMIT 後驗收（live 重跑）

**指令**：`venv/bin/python -m augur.catalog.world_concept --resolve tw.daily_bar`  
→ `Binding(..., binding_id=75, table='TaiwanStockPrice', column=None, role='observation')`

**指令**：`venv/bin/python scripts/check_sim_clock.py --check`

| 項 | 值 |
|---|---|
| **rc** | **0** |
| week_line | `sim 時鐘：K=0/3，下一格 2026-08-03，待結算 0 列` |
| `calendar_unmapped` | **未置 true**（權威 75 已解析；鍵僅 Unmapped 時設） |
| gate | `SIM-CAL-R1`／`approved` |
| mapped／sc | **21／98**／**11／98**（75 本批前已 mapped；權威指定不改 sc） |
| `sim_run_link` | **0**（首格仍未落地——**no-SIM-apply**） |

---

## 4. REGISTRY-GO？

**已履行。** 通行證 one-shot 已消費；不得複用於 81／80／97。

---

## 5. 護欄複核

| 項 | |
|---|---|
| GATE-keep（resolve 不靜默回退） | ✅ |
| no-SIM-apply | ✅ |
| 零 FinMind 放量／不殺 A1 | ✅ |
| 零 git commit | ✅ |
| 未改 binding 81 | ✅ |
| 不發明 metrics／binding | ✅（75＝Annex F 既有建議） |

---

## Trace

| 產物 | 路徑 |
|---|---|
| honesty | `audits/U0-75-HONESTY-ISSUED-20260804.md` |
| EXECUTED | `audits/U0-75-REGISTRY-EXECUTED-20260804.md` |
| DRY | `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-DRY-SQL-20260804.md` |
| 呈請 | `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-HONESTY-REQUEST-20260804.md` |
| 備料 SSOT | `reports/wm_annexf_authoritative_binding_prep_20260803.md` §2.1 |

---

*完。[I] SIM-S0-RESIDUAL — Registry COMMIT 已閉。*  
