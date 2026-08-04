# Wave-1b G3 假綠探針殘 · EXECUTED（2026-08-04）

> **位階**：[I]。**授權**：`G3-probe-go`（批次可先做）。  
> **射程**：r3 §4.2 G3＝假綠探針增量（CLAUDE #35；先驗紅）；對照 r2 Step6／master M-G11–16。  
> **禁**：不改 trigger 升嚴、不機器改 `awaiting_hugo`→superseded、不增 `false_assertion_baseline` 列。

---

## 1. 既有探針（本輪實跑）

| ID | 入口 | `--selftest` | live `--check` | 判讀 |
|---|---|---|---|---|
| **M-G11** | `pytest tests/test_l716_conflict_registered.py` | 3 passed | （簽核欄純函式已含先驗紅） | ✅ 鎖在 |
| **M-G12** | `execute_sunset_consequence.py --selftest` | 全通過 ✓（含 seal_check_rc 0→紅） | — | ✅ 鎖在 |
| **M-G13** | `check_steward_question_backlog.py --check` | 全通過 ✓ | **rc=1 紅**：awaiting_hugo=160；最舊 2026-06-22（懸置 **43** 日）；`resolved_by='hugo'=0` | ✅ 探針有效（live 必紅＝驗收） |
| **M-G14** | 既有 honest view／消費側（非本輪新碼） | — | — | 先前已落地；本輪未重開 DDL |
| **M-G16** | `check_trigger_always_mode.py --check` | 全通過 ✓（0 ALWAYS→紅） | **rc=1 紅**：非內部 116 全 `'O'`；ALWAYS=0 | ✅ 探針有效（升嚴須另裁） |
| **#35 閘** | `check_false_assertions.py --gate` | — | ✓ 無新增（基線容忍存量） | ✅ 基線未增列 |

---

## 2. 驗收對照（r3 G3）

| 條件 | 結果 |
|---|---|
| 探針或 false-assertion 基線不動增列 | ✅ gate 綠（無新增） |
| 壞了會紅／先驗紅 | ✅ G13／G16 selftest 含紅臂；live 親證紅 |
| 本輪不代裁 Q22／ENABLE ALWAYS／KH1 旁路存廢 | ✅ 只報紅、不改列／不改 trigger |

---

## 3. Steward 仍須另句（非本 EXECUTED 範圍）

| 題 | 建議裁句形 |
|---|---|
| M-G13／Q22 | `G13-Q22: machine-supersede-ok | keep-awaiting | triage-first` |
| M-G16 | `G16-ALWAYS: enable-probe-only | enable-always-go | defer` |
| M-G15 旁路 | 仍需裁才動 `auto_admit` 行為 |

---

## 4. 未做

- 未新增探針腳本（殘項腳本已在；本輪＝跑＋留痕）  
- 未 git commit  

*EXECUTED 時點：2026-08-04 ≈10:50+08。*
