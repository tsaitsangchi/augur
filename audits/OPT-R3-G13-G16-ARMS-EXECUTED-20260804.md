# G13／G16 Steward 臂落地 · EXECUTED（2026-08-04）

> **位階**：[I]。  
> **Steward 原文（精確）**：
> ```
> G13-Q22: machine-supersede-ok
> G16-ALWAYS: enable-probe-only
> ```
> **呈裁卡**：`audits/OPT-R3-G13-G16-CIRCLE-CARDS-20260804.md`  
> **前態**：`audits/OPT-R3-G13-G16-AWAIT-ARM-20260804.md`（未圈臂 → 本檔關閉）  
> **探針基線**：`audits/OPT-R3-W1B-G3-PROBE-EXECUTED-20260804.md`

---

## 1. 臂意涵（依卡）

| 閘 | Steward 臂 | 機械效力（本輪） |
|---|---|---|
| **G13-Q22** | `machine-supersede-ok` | 准機器路徑將**可機械判定**之 `awaiting_hugo`→`superseded`（既有 `resolve_questions --sweep-awaiting`）；年齡門／批次細節＝**另本** |
| **G16-ALWAYS** | `enable-probe-only` | **維持** `check_trigger_always_mode` 探針；**不** `ENABLE ALWAYS`／不 DDL |

---

## 2. 觸檔

| 路徑 | 角色 |
|---|---|
| `ops/steward_opt_arms.json` | 臂位 SSOT（[I]；fail-closed 讀取） |
| `scripts/_steward_opt_arms.py` | 純函式讀臂／授權判準（無 `__main__`） |
| `scripts/resolve_questions.py` | `--sweep-awaiting` 寫入須 Q22 准；selftest 含先驗紅 |
| `scripts/check_steward_question_backlog.py` | 報臂；仍唯讀；selftest 臂閘 |
| `scripts/check_trigger_always_mode.py` | 報臂＝probe-only；明示不准 DDL；selftest |
| 本檔 | 執行留痕 |
| `audits/OPT-R3-G13-G16-CIRCLE-CARDS-20260804.md` | 輕量勾選已裁 |
| `audits/OPT-R3-G13-G16-AWAIT-ARM-20260804.md` | 指向本 EXECUTED |
| `reports/augur_opt_next_best_r3_20260804.md` | #1 擇臂已消費 |
| `audits/OPT-R3-NEXT-BEST-R3-20260804.md` | 指針同步 |

**未觸**：constitution／[N]；trigger DDL；Registry COMMIT；FinMind／FRED 寬窗；git commit；M-G15 `auto_admit`。

---

## 3. 驗證（親跑）

| 指令 | 結果 |
|---|---|
| `check_steward_question_backlog.py --selftest` | ✓（含 keep-awaiting→拒／live 臂准） |
| `check_trigger_always_mode.py --selftest` | ✓（probe-only→不准 DDL；live 臂對） |
| `resolve_questions.py --selftest` | ✓（Q22／G16 臂閘先驗紅） |
| `check_false_assertions.py --gate` | ✓ 無新增（基線未增列） |
| `check_steward_question_backlog.py --check` | **rc=1 紅**：awaiting=**160**；最舊 2026-06-22（**43** 日）；臂＝machine-supersede-ok／准寫；本支未改列 |
| `check_trigger_always_mode.py --check` | **rc=1 紅**：ALWAYS=**0**／origin=116；臂＝enable-probe-only；ENABLE ALWAYS 准=否 |
| `resolve_questions.py --sweep-awaiting --dry-run` | 臂准；噪音 **0**／片段 **0** → 真決策題 **160** 保留（未寫庫） |

**誠實判讀**：兩探針 live **紅＝驗收**（臂≠自動刷綠）。G13 准寫後 dry-run 顯示既有噪音／片段規則**零命中**——160 列清積壓須年齡門／triage **另本**，非本輪範圍。

---

## 4. #35

新回歸鎖（純函式餵真臂＋壞臂必拒）掛在三支 `--selftest`；未增 `false_assertion_baseline` 列。

---

## 5. 殘餘／下一步

| 項 | 狀態 |
|---|---|
| awaiting 年齡門／批次 supersede 規則 | ✅ **已關**→ `audits/OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED-20260804.md`（逾齡 54 write／keep 106） |
| `ENABLE ALWAYS`／`enable-always-go` | ✅ **已關**→ 同檔（ALWAYS 0→116） |
| ≤30 日 awaiting triage／人結案 | 仍開（106 列；`resolved_by='hugo'=0`） |
| M-G15 `auto_admit` 旁路 | 仍須另裁 |
| GATE-raise／[N] 入憲 | 另本（本輪未改憲章） |

*EXECUTED 時點：2026-08-04 ≈11:10+08；殘本落地見 AGE-G16-ALWAYS。*
