# Augur 優化｜最佳下一步 r4（刷新 · 2026-08-04 ≈11:16+08）

> **性質**：[I] Steward 接續便利條。**非**新計畫 SSOT；執行序仍讀 step／foundation。  
> **取代／升級**：`reports/augur_opt_next_best_r3_20260804.md`——該檔「#1＝G13／G16 **擇臂**」**已過期**（臂已 EXECUTED）。  
> **audit**：`audits/OPT-R3-NEXT-BEST-R4-20260804.md`  
> **self-reported**：優先序＝呈案；A1／額度僅引 `pgrep`／log。

| SSOT | 路徑 |
|---|---|
| step／runbook | `archive/slim-t3/augur_optimization_step_plan_r3_20260804.md` |
| 地基 | `archive/slim-t3/augur_optimization_foundation_unified_20260803.md`／`archive/slim-t3/augur_project_optimization_plan_20260804.md` |
| P1 A／C | A＝`audits/P1-DRIFT-A-EXECUTED-20260804.md` · C＝`audits/P1-DRIFT-C-EXECUTED-20260804.md` · 呈案＝`reports/augur_p1_feature_drift_plan_20260804.md` |
| SIGN active3 | `audits/OPT-R3-SIGN-ACTIVE3-H20-RECORD-EXECUTED-20260804.md` |
| **G13／G16 臂** | `audits/OPT-R3-G13-G16-ARMS-EXECUTED-20260804.md` → 殘本 `OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED`（年齡門＋`enable-always-go`） |
| U0-STRUCT | `audits/U0-STRUCT-378097-20260804.md` · prep＝`reports/augur_u0_struct_next_paths_20260804.md` |
| A1 監看 | `audits/OPT-R3-W2PREP-A1-WATCH-20260804.md`（須再刷時以本檔 §5 為準） |

---

## 1. 一句現況（相對 r3）

| 已關／已定 | 證據 |
|---|---|
| Wave unbind | 39、35／70 全刀 EXECUTED |
| Registry | mapped **20**；U0 **7／65** COMMIT |
| U0-STRUCT | 37／80／97＝俟＋出口；prep ✅；**零 Registry**（出口 go 仍開） |
| P1-DRIFT **A** | **EXECUTED／dry-run GREEN**（H60） |
| P1-DRIFT **C** | **EXECUTED** — H20＋H60＋econ prodset；`audits/P1-DRIFT-C-EXECUTED-20260804.md`；≠可交易／寫庫 |
| SIGN active3 h20／60 | **PASS 3／0**；go **已消費** |
| **G13／G16** | 臂＋殘本 **已關**：年齡門 write **54**／keep **106**；ALWAYS **116**；見 `OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED`（**勿重貼擇臂**） |
| G13／G16 殘 | ✅ 年齡門／`enable-always-go` 已落地；殘＝≤30 日 awaiting triage／M-G15／GATE-raise 入憲（另本） |
| A2 | ✅ |
| A1 | 🟡 **仍跑** pid **877801**（≈56m @11:16；STAT=S）；log 停 `[4/92]`／額度閘 **5972/6000≥5800**（mtime **10:50**）；**403=0**；另 `--end 2026-08-03`≈**861734**——**勿殺勿疊** |

**不是**下一步：再圈 G13／G16 臂選單；重跑 SIGN／P1-A／**P1-C**；再開 UNBIND；重跑 U0 prep；第二支 A1；假關確立級。

---

## 2. 單一「最佳下一步」（post C）

**`P1-DRIFT: C-go` 已消費／EXECUTED**（H20＋H60＋econ prodset）。預測下一 lev＝寫庫／SIM／direction_gate——**另句**；勿重貼 C-go。

| 候選 | 狀態 |
|---|---|
| **P1-DRIFT C** | ✅ **已落地** — `audits/P1-DRIFT-C-EXECUTED-20260804.md` |
| G13／G16 再擇臂／殘本 | ❌／✅ 已關；選單勿重貼 |
| A1 終態 | 額度閘暫停＝預期；只監看 |
| STRUCT 出口 | prep 齊；`Q-R8`／`U0-97` 等 **可同步**，另句 |
| predict 寫庫／sim `--apply` | **另授**（非 C 默認） |

---

## 3. 可先做／可同步／勿做

### 可先做（不擋 #1）

| # | 項 | 狀態 |
|---|---|---|
| 1 | **A1 監看→終態記帳**（不殺不疊） | partial；pid 仍在 |
| 2 | ~~G13 年齡門／G16 ALWAYS 殘本~~ | ✅ `OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED` |
| 3 | HANDOFF 一句指針（commit **另授**） | 文件 |
| 4 | U0 prep 維持（零寫庫） | done；勿重跑當開工 |

### 可同步

```
A1 監看收尾  ‖  STRUCT 出口 go（Q-R8／U0-97／80 拆）
             ‖  （若另授）predict-asof-write-go／SIM-FIRST-CELL-go
```

- 不互搶 Registry COMMIT；不與 A1 疊第二支 `daily_maintenance --end 2026-08-04`。  
- **勿重跑** `P1-DRIFT: C-go`／重訓 H20／H60 當開工。  
- STRUCT 寫庫仍要 `REGISTRY-GO`＋honesty（STRUCT **未**預發）。

### 勿做

| 禁 | 理由 |
|---|---|
| 重貼 G13／G16 **選單**／稱「仍待擇臂」 | `ARMS-EXECUTED` 已在 |
| 重貼／重跑 SIGN／`P1-DRIFT: A`／`C-go` | 已 EXECUTED PASS／綠 |
| 第二支 A1 | pid 877801 仍在 |
| U0 37／80／97 強登 Registry | 俟＋出口；未授 REGISTRY-GO |
| 新 UNBIND 刀 | Wave DONE |
| Dividend／寬窗／放量 | THAW-bounded |
| `SIM --apply`／predict 寫庫 | 須另句（C 未授寫庫） |
| 假關確立級／可交易 | econ 尺≠確立級；direction_gate 另層 |

---

## 4. Steward go 句（僅仍開閘）

### 主裁（已消費）

```text
P1-DRIFT: C-go
```

→ **已 EXECUTED**（`audits/P1-DRIFT-C-EXECUTED-20260804.md`）。勿重貼當開工。

### 加料（平行）

```text
Q-R8=jp-ok
U0-97: 不登
```

```text
U0-80-SPLIT-BOUND: second_binding=<id> + role=price_limit_ref
```

（37／80 寫庫另要 `REGISTRY-GO`＋honesty＝該 binding＋`decided_by=hugo`。）

若要預測寫庫／sim（**另層、非 C 默認**）：

```text
predict-asof-write-go
SIM-FIRST-CELL-go
```

### 已消費／勿重貼當開工

- `G13-Q22: machine-supersede-ok` · `G16-ALWAYS: enable-always-go`（→ `OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED`）
- `G13 年齡門／批次 supersede；enable-always-go。`（殘本 GO；已消費）
- `SIGN-ACTIVE3-h20-record-go`
- `P1-DRIFT-PLAN-go`／`P1-DRIFT: A`／`P1-DRIFT: C-go`
- `U0-STRUCT: 37=俟|jp-ok ; 80=俟拆|登事件欄 ; 97=俟偵測器|不登`

---

## 5. 親查錨（≈11:16+08；G13／G16 殘本另刷）

### G13／G16（殘本已關）

| 項 | 值 |
|---|---|
| 檔 | `audits/OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED-20260804.md` |
| 臂 | `machine-supersede-ok`／`enable-always-go` |
| G13 write | 逾齡 **54**／keep **106**（dry＝write）；awaiting 160→106 |
| G16 apply | ALWAYS **0→116** |
| 探針 | backlog **rc=0**（最舊 29 日）；ALWAYS **rc=0** |

### A1

```text
pgrep: daily_maintenance --end 2026-08-04 → 877801 (S, ~56m)
log:   /home/hugo/logs/daily_maintenance_2026-08-04_a1a2.log (mtime 10:50; 7446B)
       … [4/92] … 額度 5972/6000 ≥ 5800 → 主動暫停
403:   0
also:  --end 2026-08-03 → 861734 (~1h26m) — 不殺
exit:  尚未（非終態）
```

---

*完。C 已 EXECUTED；零 Registry；不疊 A1；不重貼擇臂／C-go。*
