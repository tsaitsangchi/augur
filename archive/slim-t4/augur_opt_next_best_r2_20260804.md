# Augur 優化｜最佳下一步 r2（刷新 · 2026-08-04 ≈11:00+08）

> **性質**：[I] Steward 接續便利條。**非**新計畫 SSOT；執行序仍讀 r3。  
> **取代／升級**：`reports/augur_opt_next_best_20260804.md` 上午版——呈案已寫；**P1-DRIFT: A 已執行**（dry-run 綠）。  
> **audit**：`audits/OPT-R3-NEXT-BEST-R2-20260804.md` · P1 A＝`audits/P1-DRIFT-A-EXECUTED-20260804.md`  
> **can-do2**：`audits/OPT-R3-CANDO2-BATCH-20260804.md`（本波「可先做」bundle 落地）  
> **self-reported**：優先序＝呈案；進程／額度僅引 `pgrep`／log。

| SSOT | 路徑 |
|---|---|
| step／runbook | `archive/slim-t3/augur_optimization_step_plan_r3_20260804.md` |
| 地基 | `archive/slim-t3/augur_project_optimization_plan_20260804.md` |
| P1 呈案（已落地） | `reports/augur_p1_feature_drift_plan_20260804.md` |
| U0-STRUCT（已結） | `audits/U0-STRUCT-378097-20260804.md` |
| can-do 批次帳 | `audits/OPT-R3-CANDO-BATCH-20260804.md` |
| can-do2 批次帳 | `audits/OPT-R3-CANDO2-BATCH-20260804.md` |
| A1 監看 | `audits/OPT-R3-W2PREP-A1-WATCH-20260804.md` |

---

## 1. 一句現況（相對上午 next-best）

| 已關／已定 | 證據 |
|---|---|
| Wave unbind | 39、3570 field_corr、35 dirfeat、70 valuation、35 research（各 EXECUTED） |
| Registry | mapped **20**／sc **10**；U0 **7／65** COMMIT |
| OUT8／N7／043 | 裁切已登錄（見 HANDOFF／can-do） |
| **U0-STRUCT** | 37＝俟\|jp-ok；80＝俟拆\|登事件欄；97＝俟偵測器\|不登——**零 Registry** |
| P1 drift **plan** | `P1-DRIFT-PLAN-go` 產物已寫 |
| P1-DRIFT **A** | **已執行** — dry-run 綠；`audits/P1-DRIFT-A-EXECUTED-20260804.md` |
| G3 探針 | EXECUTED（G13／G16 live 紅＝探針有效） |
| HANDOFF／MC cone | 已刷新／庫內 as-of 已齊；sign h=20 **defer** |
| A2 | ✅ `sync_macro` |
| A1 | 🟡 **仍跑** pid **877801**（≈40m @11:00）；log 停 `[4/92]`／額度閘 **5972/6000≥5800**（mtime 10:50）；**無 403**；**勿疊第二支** |
| can-do2 | ✅ U0 prep／G13·G16 卡／SIGN 待命帳已寫；A1 **非終態** |

**不是**下一步：再裁 U0-STRUCT；再寫 P1 呈案；再圈／重跑 P1-DRIFT A（已綠）；再開 UNBIND 刀（已 DONE）；重跑 U0 prep。

---

## 2. 單一「最佳下一步」

~~**Steward 對已寫呈案圈選：`P1-DRIFT: A|B|C|defer`**~~ → **已圈 A 並執行**（rename-align／H60 重產；dry-run 綠）。見 `audits/P1-DRIFT-A-EXECUTED-20260804.md`。

**現行主刀**：A1 收尾記帳／G13·G16 呈裁／U0 STRUCT prep（仍禁 REGISTRY）——**非**再裁 P1 臂；完整 C（多 horizon／經濟終關）另句才開。

---

## 3. 可先做（依賴已滿足；不需等 P1 圈選）

| # | 項 | 狀態 | 註 |
|---|---|---|---|
| 1 | **A1 收尾記帳**（`pgrep`／log 尾／終態 exit；不殺不疊） | ☑ 監看已刷新；☐ **終態**未到 | pid 877801 仍跑；另 `--end 2026-08-03`≈861734——**不殺、不疊** |
| 2 | U0 37／80／97 **prep only** | ☑ **done** | 三份 reports；禁 REGISTRY |
| 3 | 符號尺 `SIGN-ACTIVE3-h20-record-go`（環境允） | ☑ 待命帳；☐ **未 `--record`** | 另句才跑；見 `OPT-R3-SIGN-H20-STANDBY` |
| 4 | G13／G16 紅燈後之**呈裁卡**（不代裁） | ☑ **卡已呈**；☐ 人裁 | `OPT-R3-G13-G16-CIRCLE-CARDS` |
| 5 | 文件指針：本 r2 → HANDOFF 一句（commit 另授） | ☐ | 零業務碼；commit 另授 |

---

## 4. 可同步／平行

```
A1 監看收尾  ‖  等 P1-DRIFT 圈選（人）  ‖  U0 STRUCT prep（零寫庫）
             ‖  G13/G16 呈裁卡（文件）  ‖  SIGN h=20（另句後）
```

- 不互搶 Registry COMMIT；不搶 `heavy_slot`；不與 A1 疊第二支 `daily_maintenance --end 2026-08-04`。  
- sim `--selftest` 已綠 → **勿**並行 `--apply`。  
- P1 一旦圈 **C**／完整 **A**：另排 train／artifact 窗，仍 `--skip-sync`、不綁 A1 完成。

---

## 5. 仍擋／勿做

| 禁 | 理由 |
|---|---|
| 再裁「先 STRUCT」當 #1 | STRUCT **已結**（audit 已登） |
| U0 37／80／97 COMMIT／REGISTRY | 俟＋出口；未授 `Q-R8`／拆登／偵後 map |
| 新 UNBIND SQL 刀（35／70／39 等） | Wave 已 DONE |
| 第二支 A1（同日 `--end 2026-08-04`） | pid 877801 仍在；額度閘暫停中 |
| Dividend／寬窗／放量／`--with-dim-sync` | THAW-bounded |
| `SIM-FIRST-CELL`／`--apply` | 須另句 |
| 假關確立級／G-*／10-14 | 另帳 |
| 宣稱 predict 可交易 | 未過 drift 對齊＋經濟終關 |

---

## 6. Steward go 句（可直接貼）

### 主裁（本波 #1）

```text
P1-DRIFT: A=rename-align | B=canonical-arm | C=retrain-asof | defer
```

單選示例：

```text
P1-DRIFT: B-first then C
P1-DRIFT: C-go
P1-DRIFT: A-go
P1-DRIFT: defer
```

護欄可併：`FZ/GATE-keep` · `no-SIM-apply` · `skip-sync`。

### 加料（平行、非擋主裁）

```text
SIGN-ACTIVE3-h20-record-go
G13-Q22: <裁> | G16-ALWAYS: <裁>
Q-R8=jp-ok
U0-97: 不登
```

（37／80 寫庫仍另要 `REGISTRY-GO`＋新 honesty——STRUCT **未**預發。）

### 已消費／勿重貼當開工

- `U0-STRUCT: 37=俟|jp-ok ; 80=俟拆|登事件欄 ; 97=俟偵測器|不登` → **已登錄**  
- `P1-DRIFT-PLAN-go` → **呈案已寫**  
- `P1-DRIFT: A` → **已執行**（`audits/P1-DRIFT-A-EXECUTED-20260804.md`）；勿重貼當開工  

---

## 7. 親查錨（本輪 ≈11:00+08）

```text
pgrep: daily_maintenance --end 2026-08-04 → 877801 (S, ~40m)
log:   /home/hugo/logs/daily_maintenance_2026-08-04_a1a2.log (mtime 10:50; 7446B)
       … [4/92] EuropeStockPrice … 額度 5972/6000 ≥ 5800 → 主動暫停
403:   未見
```

---

*完。P1-DRIFT A 已另帳執行（見上）；零 Registry；不疊 A1；SIGN 未 `--record`。*
