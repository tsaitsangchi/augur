# Augur 優化｜最佳下一步 r3（刷新 · 2026-08-04 ≈11:06+08）

> **性質**：[I] Steward 接續便利條。**非**新計畫 SSOT；執行序仍讀 step／foundation。  
> **取代／升級**：`reports/augur_opt_next_best_r2_20260804.md`——該檔仍把 SIGN 當待命、主刀仍散；**本 r3 以親查檔為準重排**。  
> **audit**：`audits/OPT-R3-NEXT-BEST-R3-20260804.md`  
> **self-reported**：優先序＝呈案；A1／額度僅引 `pgrep`／log。

| SSOT | 路徑 |
|---|---|
| step／runbook | `reports/augur_optimization_step_plan_r3_20260804.md` |
| 地基 | `reports/augur_optimization_foundation_unified_20260803.md`／`reports/augur_project_optimization_plan_20260804.md` |
| P1 A 已綠 | `audits/P1-DRIFT-A-EXECUTED-20260804.md` |
| SIGN active3 | `audits/OPT-R3-SIGN-ACTIVE3-H20-RECORD-EXECUTED-20260804.md` |
| G13／G16 臂 | **EXECUTED**＝`audits/OPT-R3-G13-G16-ARMS-EXECUTED-20260804.md`（`machine-supersede-ok`／`enable-probe-only`） |
| U0-STRUCT | `audits/U0-STRUCT-378097-20260804.md` · prep＝`reports/augur_u0_struct_next_paths_20260804.md` |
| A1 監看 | `audits/OPT-R3-W2PREP-A1-WATCH-20260804.md` |

---

## 1. 一句現況（相對 r2）

| 已關／已定 | 證據 |
|---|---|
| Wave unbind | 39、35／70 全刀 EXECUTED |
| Registry | mapped **20**／sc **10**；U0 **7／65** COMMIT |
| U0-STRUCT | 37／80／97＝俟＋出口；prep reports 已勾；**零 Registry** |
| P1-DRIFT **A** | **EXECUTED／dry-run GREEN**（H60 prodset 重產）；殘餘＝其他 horizon／經濟終關＝完整 **C** |
| SIGN active3 h20／60 `--record` | **EXECUTED · PASS 3／0**（6 列 FSC）；`SIGN-ACTIVE3-h20-record-go` **已消費** |
| G13／G16 | ✅ **已圈臂並落地**：`machine-supersede-ok`／`enable-probe-only`（live 探針仍紅＝誠實） |
| A2 | ✅ |
| A1 | 🟡 **仍跑** pid **877801**（≈49m @11:06；STAT=S）；log 停 `[4/92]`／額度閘 **5972/6000≥5800**（mtime 10:50）；**無 403**；另 `--end 2026-08-03`≈861734——**勿殺勿疊** |

**不是**下一步：再裁 STRUCT；再寫／重跑 P1-DRIFT A；重貼 `SIGN-ACTIVE3-h20-record-go`；重貼 G13／G16 臂；再開 UNBIND；重跑 U0 prep；第二支 A1；`ENABLE ALWAYS`（須另裁 `enable-always-go`）。

---

## 2. 單一「最佳下一步」

~~**Steward 對 G13／G16 完成擇臂**~~ → **已圈並 EXECUTED**（`machine-supersede-ok`／`enable-probe-only`）。

**現行主刀（建議）**：A1 終態記帳（監看、不疊）‖ 或 Steward 另句開 P1-DRIFT **C**／STRUCT 出口（`Q-R8`…）／G13 年齡門另本——**非**再圈 G13／G16 臂。

| 候選 | 為何不當「再當 #1 擇臂」 |
|---|---|
| G13／G16 擇臂 | ✅ **已消費** → ARMS-EXECUTED |
| A1 終態 | 額度閘暫停＝預期；只宜監看記帳 |
| predict 非 dry／經濟終關 | 屬 P1 **C**；須**新授權** |
| STRUCT 出口執行 | prep 已齊；須另句；STRUCT 本身已結 |
| G13 年齡門批次 | 卡「細節另跑本」；dry-run 噪音／片段＝0 |

---

## 3. 可先做／可同步／勿做

### 可先做（不擋 #1）

| # | 項 | 狀態 |
|---|---|---|
| 1 | **A1 監看→終態記帳**（不殺不疊） | partial；pid 仍在 |
| 2 | HANDOFF／r3 指針一句（commit 另授） | 本檔＋ audit |
| 3 | U0 prep 文件維持（零寫庫） | done；勿重跑當開工 |

### 可同步

```
A1 監看收尾  ‖  （人裁後）C＝多 horizon／經濟終關（另句）
             ‖  （人裁後）STRUCT 出口 go（Q-R8／U0-97…）
             ‖  （另本）G13 年齡門／批次 supersede
```

- 不互搶 Registry COMMIT；不與 A1 疊第二支 `daily_maintenance --end 2026-08-04`。  
- predict C／寫庫／經濟終關：**另句**；`--skip-sync`；不綁 A1 完成。  
- STRUCT 寫庫仍要 `REGISTRY-GO`＋honesty（STRUCT **未**預發）。

### 勿做

| 禁 | 理由 |
|---|---|
| 重貼 `SIGN-ACTIVE3-h20-record-go`／重跑 SIGN | 已 EXECUTED PASS |
| 重貼／重跑 `P1-DRIFT: A` | dry-run 已綠 |
| 重貼／重裁 G13／G16 臂 | 已 EXECUTED；勿當開工 |
| 第二支 A1 | pid 877801 仍在 |
| U0 37／80／97 REGISTRY／COMMIT | 俟＋出口；未授 |
| 新 UNBIND 刀 | Wave DONE |
| Dividend／寬窗／放量 | THAW-bounded |
| `SIM --apply` | 須另句 |
| 假關確立級／可交易 | 未過經濟終關等 |

---

## 4. Steward go 句（僅仍開閘）

### 主裁（仍開者）

```text
P1-DRIFT: C-go
```

（或多 horizon／經濟終關之等價句；護欄可併 `FZ/GATE-keep` · `no-SIM-apply` · `skip-sync`。）

```text
Q-R8=jp-ok
U0-97: 不登
```

（37／80 寫庫另要 `REGISTRY-GO`＋honesty。）

可選另本（G13 積壓細節）：年齡門／批次 supersede 規則——**非**重貼已選臂。

### 已消費／勿重貼當開工

- `U0-STRUCT: 37=俟|jp-ok ; 80=俟拆|登事件欄 ; 97=俟偵測器|不登`
- `P1-DRIFT-PLAN-go`／`P1-DRIFT: A`
- `SIGN-ACTIVE3-h20-record-go`
- `G13-Q22: machine-supersede-ok`／`G16-ALWAYS: enable-probe-only` → ARMS-EXECUTED

---

## 5. 親查錨（A1／SIGN · ≈11:06+08）

### SIGN

| 項 | 值 |
|---|---|
| 檔 | `audits/OPT-R3-SIGN-ACTIVE3-H20-RECORD-EXECUTED-20260804.md`（mtime ≈11:05） |
| 結果 | PASS 3／FAIL 0；`feature_sign_check`＋6 列 |
| G13／G16 臂 | **CLOSED** → `audits/OPT-R3-G13-G16-ARMS-EXECUTED-20260804.md` |

### A1

```text
pgrep: daily_maintenance --end 2026-08-04 → 877801 (S, ~49m)
log:   /home/hugo/logs/daily_maintenance_2026-08-04_a1a2.log (mtime 10:50; 7446B)
       … [4/92] … 額度 5972/6000 ≥ 5800 → 主動暫停
403:   0
also:  --end 2026-08-03 → 861734 (~1h19m) — 不殺
exit:  尚未（非終態）
```

---

*完。G13／G16 臂已落地；零 Registry；不疊 A1；不 ENABLE ALWAYS。*
