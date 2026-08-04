# G13／G16 仍待圈選臂（2026-08-04）— **已關閉**

> **位階**：[I]。  
> **狀態**：**CLOSED** — Steward 已親打臂；執行＝`audits/OPT-R3-G13-G16-ARMS-EXECUTED-20260804.md`  
> **同句上下文（歷史）**：Steward `G13-Q22／G16-ALWAYS／SIGN-ACTIVE3-h20-record-go`（僅點閘 ID → 本 AWAIT）  
> **SIGN**：已執行 → `audits/OPT-R3-SIGN-ACTIVE3-H20-RECORD-EXECUTED-20260804.md`（PASS 3／0）  
> **呈裁卡**：`audits/OPT-R3-G13-G16-CIRCLE-CARDS-20260804.md`

---

## 關閉登錄

| 閘 | Steward 臂（精確） | 產物 |
|---|---|---|
| **G13-Q22** | `machine-supersede-ok` | `ops/steward_opt_arms.json`＋`--sweep-awaiting` 寫入閘 |
| **G16-ALWAYS** | `enable-probe-only` | 同上；探針維持、**無** trigger DDL |

---

## 史料：未圈臂時處分（≈11:01–11:06）

| 閘 | 當時 | 本輪動作 |
|---|---|---|
| G13-Q22 | 僅點名閘 ID | **不改**（已由後續親打臂取代） |
| G16-ALWAYS | 僅點名閘 ID | **不改**（同上） |

---

## 探針現況（ARMS-EXECUTED 複核）

| 閘 | 探針 | live |
|---|---|---|
| G13 | `check_steward_question_backlog.py --check` | rc=1 紅：awaiting=160；臂准；未改列 |
| G16 | `check_trigger_always_mode.py --check` | rc=1 紅：ALWAYS=0；probe-only |

*完（關閉）。*
