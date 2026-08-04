# SIM-S0-RESIDUAL：`tw.daily_bar` authoritative-binding（2026-08-04）[I]

> **位階**：[I] 執行／診斷留痕（非 META-CONSTITUTION [N]）。  
> **授權（exact）**：`SIM-S0-RESIDUAL: tw.daily_bar authoritative-binding | GATE-keep | no-SIM-apply`  
> **計畫**：`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`  
> **上游 Discovery**：`audits/SIM-SELF-EVOLVE-S0-DISCOVERY-20260804.md`（D-CELL 阻斷）  
> **self-reported（#32a）**：數字出 (a) stdout／(b) DB。  
> **硬守**：GATE-keep · no-SIM-apply · 零 FinMind 放量 · 不殺 A1 · **零 Registry COMMIT**（缺 `REGISTRY-GO` 形）

---

## 1. 診斷：`tw.daily_bar` 如何被解析

| 層 | 機制 | 本窗實證 |
|---|---|---|
| 消費端 | `check_sim_clock._snapshot` → `resolve_sql("tw.daily_bar")` → 查 TAIEX `date` 作交易日曆錨 | 權威 NULL → `UnmappedConcept`（WM.35 fail-closed） |
| Registry | `world_concept_registry_current.authoritative_binding_id` → `world_channel_binding` | `tw.daily_bar` 權威 **NULL**；`decided_by` NULL |
| 通道候選 | binding **75** `TaiwanStockPrice`（observation, mapped）／**81** `TaiwanStockPriceAdj`（derived, mapped） | 與 Annex F §1.2 一致 |
| 權威建議 | Annex F §2.1 建議案＝**75**（raw）；不採 81（derived＋restating 與欄 7「次一交易日定案」相斥） | **採認 SSOT＝備料報告，非本窗發明** |

**一句**：時鐘哨不缺表／不缺 TAIEX 列——缺的是 Steward 對 binding **75** 的權威採認（＋ `REGISTRY-GO`／honesty／`decided_by`）。

---

## 2. 本窗實作（最小、GATE-keep）

| 動作 | 結果 |
|---|---|
| Registry COMMIT `authoritative_binding_id=75` | **未做**——殘差句 **≠** `REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo` |
| DRY SQL 備料 | ✅ `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-DRY-SQL-20260804.md`（ROLLBACK 形；佔位親簽） |
| honesty／REGISTRY-GO 呈請 | ✅ `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-HONESTY-REQUEST-20260804.md` |
| `check_sim_clock` 誠實降級 | ✅ 捕 `UnmappedConcept` → 週報仍印、`calendar_unmapped=true`、**不**回退 vendor 表名字面 |

**不弱化**：`augur.catalog.world_concept.resolve*` 仍 fail-closed；僅告知哨在日曆不可解析時改印「下一格 未實現」而非 traceback。

---

## 3. `check_sim_clock --check`（本窗重跑）

**指令**：`venv/bin/python scripts/check_sim_clock.py --check`

| 項 | 值 |
|---|---|
| **rc** | **0**（告知哨；自測亦 0） |
| week_line（預期形） | `sim 時鐘：K=0/3，下一格 未實現，待結算 0 列` |
| `calendar_unmapped` | **true**（權威仍 NULL——誠實） |
| gate | `SIM-CAL-R1`／`approved`（與 Discovery 一致） |
| `sim_run_link` | **0**（首格仍未落地——本窗 **no-SIM-apply**） |

**誠實界**：rc=0 **≠** 權威已採認；**≠** 首格已落地。解除 `calendar_unmapped` 仍待下節 REGISTRY-GO＋COMMIT。

---

## 4. 是否仍需 REGISTRY-GO？

**要。** 殘差授權足以：診斷＋DRY＋時鐘哨誠實降級；**不足以**寫 `world_concept_version`／消費 honesty GUC 做 COMMIT。

請 Steward 另貼：

```text
REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo
```

後依 DRY 改 `COMMIT`、親填 `decided_by`／`decided_at`，再驗 `--resolve tw.daily_bar` → `TaiwanStockPrice`（75）。

---

## 5. 護欄複核

| 項 | |
|---|---|
| GATE-keep（resolve 不靜默回退） | ✅ |
| no-SIM-apply | ✅ |
| 零 FinMind 放量／不殺 A1 | ✅ |
| 零 git commit | ✅ |
| 零 Registry COMMIT | ✅ |
| 不發明 metrics／binding | ✅（75＝Annex F 既有建議） |

---

## Trace

| 產物 | 路徑 |
|---|---|
| DRY | `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-DRY-SQL-20260804.md` |
| 呈請 | `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-HONESTY-REQUEST-20260804.md` |
| 碼改 | `scripts/check_sim_clock.py`（Unmapped 誠實降級） |
| 備料 SSOT | `reports/wm_annexf_authoritative_binding_prep_20260803.md` §2.1 |

---

*完。[I] SIM-S0-RESIDUAL。*  
