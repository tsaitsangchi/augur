# Augur 優化｜最佳下一步（sticky · 2026-08-04）

> **性質**：[I] Steward 接續便利條。**非**新計畫 SSOT；執行序仍讀 r3。  
> **⚠️ 刷新 10:55+08**：下文 §1–§2 上午敘事（「開 P1-DRIFT **呈案**」）**已過期**——呈案已寫完。  
> **現行 SSOT 接續條**＝[`reports/augur_opt_next_best_r2_20260804.md`](augur_opt_next_best_r2_20260804.md) · audit `audits/OPT-R3-NEXT-BEST-R2-20260804.md`。  
> **self-reported**：優先序＝呈案；數字僅引 audit／pgrep。

| SSOT | 路徑 |
|---|---|
| step／runbook | `archive/slim-t3/augur_optimization_step_plan_r3_20260804.md`（§0／§3–§5／§8–§9） |
| 地基 | `archive/slim-t3/augur_project_optimization_plan_20260804.md`（§1／§5–§7 P0–P3） |
| **現行 next-best** | `reports/augur_opt_next_best_r2_20260804.md` |
| 本條 audit（舊） | `audits/OPT-R3-NEXT-BEST-20260804.md` → 升 `OPT-R3-NEXT-BEST-R2-20260804.md` |
| U0-STRUCT | `audits/U0-STRUCT-378097-20260804.md`（已結） |
| P1 呈案 | `reports/augur_p1_feature_drift_plan_20260804.md`（已落地） |

---

## 刷新 10:55｜單一最佳下一步（現行）

**Steward 圈選：`P1-DRIFT: A|B|C|defer`**（呈案已在；非再寫 plan；非再裁 STRUCT）。

- A1 🟡 pid **877801** 仍跑（額度閘暫停、無 403）→ 只監看收尾、**勿第二支**。  
- 可平行：A1 記帳 ‖ U0 37／80／97 prep（零寫庫） ‖ G13/G16 呈裁卡 ‖ SIGN h=20（另句）。  
- 全文表＋go 句 → **r2 檔**。

---

## 1. 一句現況（史料 · ≈10:52）

P0／Wave-1 備料／多項 Wave-2 **已關**；U0 **7／65** COMMIT → mapped 20／98。  
**U0-STRUCT 已結**：37＝俟｜jp-ok；80＝俟拆｜登事件欄；97＝俟偵測器｜不登——**主狀態仍俟、今日零 Registry**。A1 🟡仍跑。P1 predict dry＝特徵漂移誠實拒。  
**其後 can-do**：P1 **plan 已寫** → 下一步改 circle（見上「刷新 10:55」）。

---

## 2. 單一「最佳下一步」（史料 · 已升 r2）

~~**開 P1 特徵漂移對齊呈案**~~ → **已完成**（`P1-DRIFT-PLAN-go` → `augur_p1_feature_drift_plan_20260804.md`）。  
**現行**＝圈選 `P1-DRIFT: A|B|C|defer`（見 r2）。

已採 STRUCT 原文（已結，勿重當 #1）：

```text
U0-STRUCT: 37=俟|jp-ok ; 80=俟拆|登事件欄 ; 97=俟偵測器|不登
```

---

## 3. 可先做（依賴已滿足）

| # | 項 | 建議授權句（若需） |
|---|---|---|
| 1 | A1 收尾記帳（`pgrep`／log／`data_audit_log`；**不殺不疊**） | 既有 `A1A2-run-today-go` 夠用 |
| 2 | P1 特徵漂移對齊**呈案** | `P1-DRIFT-PLAN-go` |
| 3 | Wave-1b **G3** 假綠探針增量（#35 先驗紅） | `G3-probe-go` 或併 W1 殘 |
| 4 | HANDOFF 08-04 段刷新（mapped 20／STRUCT 指針） | 文件；commit 另授 |
| 5 | U0 37／80／97 **prep only**（偵測器／拆設計／jp Adj_Close 註） | STRUCT 已允；**禁** REGISTRY |
| 6 | 符號尺有界 `--record`（環境允） | 可併 `S1P1-light-go` 延伸 |
| 7 | MC cone 庫內 as-of（A4；零 API） | 既有 THAW-bounded／庫內路徑 |

---

## 4. 可同步／平行（互不阻塞）

```
A1 監看  ‖  P1-DRIFT 呈案  ‖  G3 探針  ‖  HANDOFF 刷新  ‖  U0 STRUCT prep（零寫庫）
```

- 不互搶 Registry COMMIT；不搶 `heavy_slot`；不與 A1 疊第二支 `daily_maintenance`。  
- sim `--selftest` 已綠 → **勿**並行 `--apply`。

---

## 5. 仍擋／勿做

| 禁 | 理由 |
|---|---|
| U0 37／80／97 COMMIT | STRUCT＝俟＋出口；**未**授 REGISTRY-GO／honesty |
| 新 UNBIND SQL 刀（35／70／39） | 已 DONE；勿重開 |
| `SIM-FIRST-CELL`／`--apply` | 須另句 |
| Dividend／寬窗／放量／`--with-dim-sync` | THAW-bounded 仍否（另帳豁免不擴） |
| 假關確立級／G-*／10-14 | 另帳 |
| 第二支 A1 | 進程仍在 |
| 宣稱 predict 可交易 | drift 拒載＝誠實 |

---

## 6. 出處錨點

- r3 §0 一句現況；§3 可先／同步；§5 Wave-2；§8 護欄  
- STRUCT：`U0-STRUCT-378097`；CIRCLE EXECUTED：`U0-CIRCLE-765-EXECUTED`  
- 落地：`OPT-STEP-R3-W1-LANDING`；`OPT-R3-W2PREP-*`；`BATCH-UNBIND-OUT8-N7-A1A2`

---

*完。零業務碼改動。*
