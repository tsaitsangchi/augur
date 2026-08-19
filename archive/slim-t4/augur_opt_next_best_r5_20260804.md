# Augur 優化｜最佳下一步 r5（LIVE 刷新 · 2026-08-04 ≈11:25+08）

> **性質**：[I] Steward 接續便利條。**非**新計畫 SSOT；執行序仍讀 step／foundation。  
> **取代／升級**：`reports/augur_opt_next_best_r4_20260804.md`——結論同向（#1 仍＝C），但親查錨與「C／37／A1」LIVE 狀態重戳。  
> **audit**：`audits/OPT-R3-NEXT-BEST-R5-20260804.md`  
> **self-reported**：優先序＝呈案；A1／額度僅引 `pgrep`／log。

| SSOT | 路徑 |
|---|---|
| step／runbook | `archive/slim-t3/augur_optimization_step_plan_r3_20260804.md` |
| 地基 | `archive/slim-t3/augur_optimization_foundation_unified_20260803.md`／`archive/slim-t3/augur_project_optimization_plan_20260804.md` |
| P1 呈案 | `reports/augur_p1_feature_drift_plan_20260804.md`（§6：A 綠；C 未授權） |
| P1 A 已綠 | `audits/P1-DRIFT-A-EXECUTED-20260804.md` |
| SIGN active3 | `audits/OPT-R3-SIGN-ACTIVE3-H20-RECORD-EXECUTED-20260804.md` |
| G13／G16 臂＋殘本 | `OPT-R3-G13-G16-ARMS-EXECUTED` → `OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED` |
| U0-STRUCT | `audits/U0-STRUCT-378097-20260804.md` · 37 prep＝`reports/augur_u0_37_jp_ok_checklist_20260804.md` |
| 平行軌（等 C） | `audits/OPT-R3-PARALLEL-A1-STRUCT-C-20260804.md` |
| A1 監看 | `audits/OPT-R3-W2PREP-A1-WATCH-20260804.md` |
| HANDOFF 片段 | 檔頭「2026-08-04 上午 · 優化 step r3」——便利條仍指舊 `augur_opt_next_best_20260804.md`（**可先做**改指本檔／r4） |

---

## 1. LIVE 核對（勿用陳舊 r3／r4 敘事）

| 項 | LIVE | 證據 |
|---|---|---|
| P1-DRIFT **A** | ✅ **EXECUTED** | `audits/P1-DRIFT-A-EXECUTED-20260804.md`（H60 dry 綠） |
| P1-DRIFT **C** | ❌ **無** `P1-DRIFT-C-EXECUTED*`；平行軌＝**awaiting** `C-go` | `ls` 無 C 檔；`OPT-R3-PARALLEL…` §3 |
| G13／G16 臂 | ✅ ARMS-EXECUTED | `OPT-R3-G13-G16-ARMS-EXECUTED-20260804.md` |
| G13 年齡門＋G16 ALWAYS | ✅ **DONE** | write 逾齡 **54**／keep **106**；ALWAYS **116**；`OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED` |
| G13 殘 | 106 ≤30d awaiting triage（另本；**非**再擇臂） | backlog 探針綠；`resolved_by='hugo'=0` |
| SIGN active3 | ✅ DONE（go 已消費） | `OPT-R3-SIGN-ACTIVE3-H20-RECORD-EXECUTED` |
| Binding **37** | STRUCT **俟｜jp-ok**；**無** `U0-37-DRY-SQL`／`U0-37-JP-OK`／`U0-37-REGISTRY-EXECUTED`／`*-BLOCKED-DB*` | prep only＝`augur_u0_37_jp_ok_checklist`；尚未 FAIL→unblock 落地檔 |
| STRUCT **80／97** | 仍開（俟拆／俟偵測器｜不登） | `U0-STRUCT-378097` |
| A1 | 🟡 **仍 partial** | pid **877801**＋父 **877790**；另 **861734**（`--end 2026-08-03`）；log mtime **10:50** 停額度閘 |

**不是**下一步：再圈 G13／G16；重跑 SIGN／P1-A；新 UNBIND；第二支 A1；假關確立級；在無 `C-go` 下開 C-train。

---

## 2. 單一「最佳下一步」

**Steward 貼 `P1-DRIFT: C-go`（多 horizon／經濟終關／庫內 as-of 重訓）——C 仍未 EXECUTED，預測車道唯一仍缺的新人句主槓桿。**

**為何仍是這把（相對 r4）**

| 候選 | 裁決 |
|---|---|
| **P1-DRIFT C** | ✅ **#1**：r4 已定 C＝post-arms 主刀；LIVE **確認 C 未落地**→ 不換槓桿 |
| A1 終態 | 額度閘暫停＝預期；**無人句可催**；只監看 |
| STRUCT 37／80／97 | 出口句可同步；屬 Registry 車道；**37 尚無 DRY-SQL／JP-OK／REGISTRY 帳** |
| G13 106 triage | 可另本；不擋預測 C；**勿**當「再擇臂」 |
| predict 寫庫／sim `--apply` | 比 C 更外一層；**另授** |

---

## 3. 可先做／可同步／勿做

### 可先做（不擋 #1）

| # | 項 | 狀態 |
|---|---|---|
| 1 | **A1 監看→終態記帳**（不殺不疊） | partial；兩支 end 仍在 |
| 2 | HANDOFF 便利條改指 r4／**本 r5**（commit **另授**） | 文件 |
| 3 | U0-37 prep 維持（checklist／STRUCT；零寫庫） | done；勿當已 jp-ok |
| 4 | G13 106 ≤30d triage **文件呈案**（另本；不機械清庫） | 可先做、非 #1 |

### 可同步

```
P1-DRIFT: C-go（人）  ‖  A1 監看收尾
                      ‖  STRUCT 出口 go（Q-R8／U0-97／80 拆）
                      ‖  G13-106 triage 呈案（另本）
```

- 不互搶 Registry COMMIT；不與 A1 疊第二支 `daily_maintenance --end 2026-08-04`。  
- C：`--skip-sync`；不綁 A1 完成；**禁**順便 `SIM --apply`／假可交易。  
- STRUCT 寫庫仍要 `REGISTRY-GO`＋honesty（STRUCT **未**預發）。

### 勿做

| 禁 | 理由 |
|---|---|
| 稱「C 已跑／in-flight train」 | **無** C-EXECUTED；平行軌明示等 C |
| 重貼 G13／G16 **選單**／稱仍待擇臂 | ARMS＋年齡門／ALWAYS 已 EXECUTED |
| 重貼／重跑 SIGN／`P1-DRIFT: A` | 已 EXECUTED |
| 第二支 A1 | pid 877801 仍在 |
| U0 37／80／97 強登 Registry | 俟＋出口；無 REGISTRY-GO |
| 新 UNBIND 刀 | Wave DONE |
| Dividend／寬窗／放量 | THAW-bounded |
| `SIM --apply`／predict 寫庫當 C 默認 | 須另句 |
| 假關確立級／可交易 | 未過經濟終關等 |

---

## 4. Steward go 句（僅仍開閘）

### 主裁（本波 #1）

```text
P1-DRIFT: C-go
```

建議護欄（可併）：

```text
P1-DRIFT: C-go | FZ/GATE-keep | no-SIM-apply | skip-sync
```

### 加料（平行、非擋主裁）

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

- `G13-Q22: machine-supersede-ok` · `G16-ALWAYS: enable-always-go`
- `G13 年齡門／批次 supersede；enable-always-go。`
- `SIGN-ACTIVE3-h20-record-go`
- `P1-DRIFT-PLAN-go`／`P1-DRIFT: A`
- `U0-STRUCT: 37=俟|jp-ok ; 80=俟拆|登事件欄 ; 97=俟偵測器|不登`
- （平行授權）`可同步：A1 監看（勿疊）‖ STRUCT 出口另句 ‖ 等 C。`——**等 C ≠ 已授 C-go**

---

## 5. 誠實探針筆記（A1／37／C）

### C

| | |
|---|---|
| `P1-DRIFT-C-EXECUTED*` | **不存在** |
| in-flight C-train | **無**（PARALLEL 明示本輪未 train） |
| 呈案殘列 | §6 `[ ] C 完整 retrain-asof` |
| 結論 | #1 仍＝等人貼 `C-go`；落地後才換下一槓桿 |

### Binding 37

| | |
|---|---|
| STRUCT | `37=俟\|jp-ok`（主狀態仍俟） |
| `U0-37-DRY-SQL`／`U0-37-JP-OK`／`U0-37-REGISTRY-EXECUTED`／`BLOCKED-DB` | **皆無檔** |
| prep | checklist §1–3 ✅；§4–5 待人 `Q-R8`＋另句 REGISTRY-GO |
| 結論 | **尚未**進入「FAIL→unblock→REGISTRY」執行鏈；勿報 37 已解鎖或已 BLOCKED |

### A1（≈11:25+08）

```text
pgrep: daily_maintenance --end 2026-08-04 → 877801 (+ bash 877790)
       daily_maintenance --end 2026-08-03 → 861734
log:   /home/hugo/logs/daily_maintenance_2026-08-04_a1a2.log
       mtime 10:50; 7446B; 停在 [4/92] EuropeStockPrice→ExchangeRate
       額度 5972/6000 ≥ 5800 → 主動暫停(每 150s 檢錶)
403:   0（log 可見段）
exit:  尚未（非終態）— 勿殺勿疊第二支 --end 2026-08-04
```

---

*完。LIVE：C 未 EXECUTED → #1 仍＝`P1-DRIFT: C-go`；零 Registry；不疊 A1；37 僅 STRUCT＋prep。*
