# G13 年齡門批次 supersede ＋ G16 enable-always-go · EXECUTED（2026-08-04）

> **位階**：[I]。  
> **Steward 原文（精確）**：
> ```
> G13 年齡門／批次 supersede；enable-always-go。
> ```
> **前態**：`audits/OPT-R3-G13-G16-ARMS-EXECUTED-20260804.md`（臂＝`machine-supersede-ok`／`enable-probe-only`；dry-run 噪音／片段 0→160 keep；年齡門／ALWAYS＝另本）  
> **呈裁卡**：`audits/OPT-R3-G13-G16-CIRCLE-CARDS-20260804.md`（本輪升 G16 臂）

---

## 1. 臂／規則（本輪）

| 閘 | 臂／規則 | 機械效力 |
|---|---|---|
| **G13-Q22** | 維持 `machine-supersede-ok`＋**年齡門** | 懸置日數 **> 30**（＝`check_steward_question_backlog` 同口徑）之 `awaiting_hugo` → `superseded`；噪音／片段規則仍先判；**≤30 日真決策題保留** |
| **G16-ALWAYS** | **`enable-always-go`**（自 `enable-probe-only` 升） | 准 `enable_trigger_always_mode.py --apply`；探針仍量 ALWAYS≥1 |

**年齡門定錨（既有 Steward／探針，非新造）**：卡原文「逾齡／可機械判定項」＋ backlog 探針門檻「最舊懸置 >30 日即紅」→ 批次 supersede 用同一 `>` 比較。fail-closed：無此規則不得靜默清 160。

---

## 2. 觸檔

| 路徑 | 角色 |
|---|---|
| `ops/steward_opt_arms.json` | G16→`enable-always-go`；G13 meaning 補年齡門 |
| `scripts/resolve_questions.py` | `--sweep-awaiting`＋`awaiting_age_supersede_ok`；`--max-age-days`／`--as-of` |
| `scripts/enable_trigger_always_mode.py` | **新**：ALWAYS DDL 寫入（須臂；dry-run 預設） |
| `scripts/check_trigger_always_mode.py` | 探針仍唯讀；文案／live 臂對偶 |
| `scripts/check_steward_question_backlog.py` | docstring 對齊年齡門口徑 |
| 本檔 | 執行留痕 |
| `audits/OPT-R3-G13-G16-ARMS-EXECUTED-20260804.md` | 輕量指向本殘本 |
| `reports/augur_opt_next_best_r4_20260804.md`／`audits/OPT-R3-NEXT-BEST-R4-20260804.md` | 殘項關閉指針 |

**未觸**：constitution／[N]；M-G15 `auto_admit`；Registry；FinMind／FRED 寬窗；git commit；第二支 A1；P1-C。

---

## 3. 驗證（親跑數字）

### Selftest／#35

| 指令 | 結果 |
|---|---|
| `resolve_questions.py --selftest` | ✓（含年齡門邊拒／參數化） |
| `check_trigger_always_mode.py --selftest` | ✓（live＝always-go→准） |
| `enable_trigger_always_mode.py --selftest` | ✓（probe-only 先驗紅拒寫） |
| `check_steward_question_backlog.py --selftest` | ✓ |
| `check_false_assertions.py --gate` | ✓ 無新增 |
| #35 年齡門突變對偶（不改檔） | `>` 邊拒 vs 壞 `≥` 邊准 → **PASS**（壞比較子會安靜變綠＝已證） |

### G13 dry-run → write

| 階段 | 噪音 | 片段 | 逾齡 | keep | rc |
|---|---|---|---|---|---|
| **dry-run** | 0 | 0 | **54** | **106** | 0 |
| **write** | 0 | 0 | **54** | **106** | 0 |

- as_of＝2026-08-04；門檻 >30 日  
- 寫後 `resolution_ref LIKE 'age_gate:%'`＝**54**；`resolved_by='rules_v3_sweep_awaiting'`＝**56**（含先前噪音／片段 2）  
- `awaiting_hugo`：**160 → 106**

### G16 dry-run → apply

| 階段 | ALWAYS | origin 候選 | rc |
|---|---|---|---|
| **dry-run** | 0 | **116** | 0 |
| **apply** | **0 → 116** | 116 | 0 |

### 探針（寫後）

| 探針 | rc | 摘要 |
|---|---|---|
| `check_steward_question_backlog.py --check` | **0 綠** | awaiting=**106**；最舊 2026-07-06（懸置 **29** 日 ≤30）；`resolved_by='hugo'` 仍 0 |
| `check_trigger_always_mode.py --check` | **0 綠** | ALWAYS=**116**／origin=0；臂＝enable-always-go |

---

## 4. 誠實判讀／殘餘

| 項 | 狀態 |
|---|---|
| 年齡門批次 | ✅ 54 逾齡已 supersede；106 ≤30 日真決策題仍 awaiting（**非**靜默清庫） |
| G13 探針綠 | ✅ 對年齡門檻成立；**≠**「無人裁積壓」——106 列＋`resolved_by='hugo'=0` 仍在 |
| G16 ALWAYS | ✅ 116 支已 `'A'`；replica GUC 靜音路徑已堵 |
| M-G15 `auto_admit` | **未動**（卡禁） |
| GATE-raise／[N] | **未改憲章**——本輪＝[I] 臂＋DDL 執行層硬化（master Q7 之「不動判準文字」讀法）；若 Steward 另要正式 GATE-raise／§8.1 入憲＝另本 |
| 「硬閘」文件缺 caveat | 探針仍報 8 處（不定 rc） |
| git commit | 未做 |

*EXECUTED 時點：2026-08-04 ≈11:20+08。*
