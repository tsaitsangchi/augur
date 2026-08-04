# Augur 優化｜最佳下一步 r7（self-evolve 主軸 · LIVE · 2026-08-04 ≈13:32+08）

> **性質**：[I] Steward 接續便利條。**非**新計畫 SSOT；執行序以已拍 self-evolve 計畫為準。  
> **取代／升級**：`reports/augur_opt_next_best_r6_20260804.md`——r6 #1＝P1-C 對帳叉（當時無 C-EXECUTED）；**C 已 EXECUTED**＋**LOOP 三連已授** → 本檔 #1＝**執行已授權之 LOOP-S4-TO-S5**（勿再貼 C-go／勿重開 S0）。  
> **audit**：`audits/OPT-NEXT-BEST-R7-20260804.md`  
> **self-reported（#32a）**：優先序＝呈案；LIVE 數字引 `pgrep`／log／既有 audit。

| SSOT | 路徑 |
|---|---|
| **approved 主軸** | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`（essence＝S1→S5 閉環） |
| C2／C0 閉環 | `reports/augur_s4_s5_closed_loop_plan_20260804.md` · GO＝`audits/LOOP-S4-S5-FULL-GO-20260804.md` |
| S4 families | **approved** · `audits/S4-FAMILIES-PLAN-GO-20260804.md` |
| S3 features（待採納） | `reports/augur_s3_features_for_market_model_families_20260804.md` · `audits/S3-FEATURES-MARKET-FAMILIES-20260804.md` |
| P1-C | `audits/P1-DRIFT-C-EXECUTED-20260804.md` ✅ |
| Wave A | `/tmp/s4-wave-a-20260804/` · **無** `S4-WAVE-A-EXECUTED*` |
| 管線進度 | `audits/SIM-SELF-EVOLVE-PIPELINE-PROGRESS-20260804.md`（≈13:06；本 r7 升級其「下一刀」） |

---

## 1. LIVE 核對（勿用陳舊 r6 敘事）

| 項 | LIVE（≈13:32+08） | 證據 |
|---|---|---|
| 計畫 GO／S0 Discovery | ✅ DONE | 勿稱仍開／勿重 Discovery |
| **P1-DRIFT C** | ✅ **EXECUTED** | `P1-DRIFT-C-EXECUTED-20260804.md` |
| **LOOP 三連** | ✅ **已授權**；❌ **無 EXECUTED** | `LOOP-S4-S5-FULL-GO` 有；`LOOP-S4-TO-S5-EXECUTED*`／`LOOP-S5-TO-S4-OPT-EXECUTED*` **缺** |
| S4-FAMILIES-PLAN | ✅ GO-EXECUTED | ≠ Wave 收口帳 |
| **S4-WAVE-A** | 🟡 train-matrix **DONE**（13:30）；方向臂／正式 EXECUTED **另帳** | `/tmp/s4-wave-a-20260804/train-matrix.log` 末行 DONE；**無** `S4-WAVE-A-EXECUTED*`；**不重啟** |
| A1 雙看 | 🟡 A1 **仍跑**（877790／877801）；861734 **本窗 pgrep 未見** | 不殺、不疊第三支 |
| U0-75 | honesty ✅；**REGISTRY COMMIT ❌** | `U0-75-HONESTY-ISSUED`；**無** `U0-75-REGISTRY-EXECUTED*` |
| S3-FEATURES-PLAN | 🟡 報告已寫；**待** `S3-FEATURES-PLAN-go` | 採納≠放量 build |
| S5 階段 | **NOT_STARTED**（無 OOS 終局帳） | pipeline sticky；C 附帶 dry／econ ≠ S5 閉環完成 |

**不是**下一步：重開 S0；再貼 `P1-DRIFT: C-go`；再貼已消費之 LOOP 三連當「新開工」；重啟／kill Wave A；假關確立級；sim `--apply`；放量 API。

---

## 2. 單一「最佳下一步」

**LOOP 三連已授、EXECUTED 未寫——立刻對可引用 S4 artifact（P1-C RankRidge＋Wave A 已落地 RankGBDT／H40·H120 等子集）跑 S5 dry＋OOS 漲跌比／勝率，落 `LOOP-S4-TO-S5-EXECUTED`／`S5-OOS`；Wave A 正式收口帳與方向臂另平行，不擋本刀、不重跑訓練矩陣。**

### 為何是這把（相對 r6／主軸）

| 候選 | 裁決 |
|---|---|
| **執行 LOOP-S4-TO-S5** | ✅ **#1**：FULL-GO §4 步驟 3；授權在、EXECUTED 缺；本質＝S4→S5 正向閉環；S5 仍 NOT_STARTED |
| P2e 歸檔 | 可先做／可併；C 已 EXECUTED；**不替代** S5 OOS 閉環尺 |
| S4-WAVE-A-EXECUTED 收口 | 可同步簿記；矩陣已 DONE；≠再貼 `S4-WAVE-A-go` |
| `REGISTRY-GO:75` COMMIT | 可同步（授權已發）；解 `calendar_unmapped`；**不擋** S5 dry |
| `S3-FEATURES-PLAN-go` | 可同步採納（人貼）；**不含** build；觸發後才進 C1 |
| 再貼 C-go／對帳叉 | ❌ **stale**（C 已有正式帳） |
| 重 S0／Discovery | ❌ DONE |

---

## 3. 可先做／可同步／勿做

### 可先做（不擋 #1）

| # | 項 | 註 |
|---|---|---|
| 1 | **P2e 歸檔** H60／H20 econ stdout（(a)(b)(c)；禁假確立級） | C 已 EXECUTED |
| 2 | **A1 雙看續監**至終態 | 不殺不疊；S1 ⊥ 預測熱路徑 |
| 3 | **U0-75 COMMIT**（既有 honesty／REGISTRY-GO；寫 `U0-75-REGISTRY-EXECUTED*`） | 勿再當「未授權」 |
| 4 | **S4-WAVE-A-EXECUTED** 薄帳（矩陣 DONE＋artifact 清單；方向臂 partial 誠實） | 不重跑矩陣 |
| 5 | 更新 `S4-MODELS-TRIED-LIST`（納 Wave A RankGBDT／H40·H120） | 與 S5 帳交叉 |

### 可同步

```
LOOP-S4-TO-S5 執行（S5 dry＋OOS）  ‖  A1 終態監看（S1）
                                   ‖  U0-75 Registry COMMIT（殘差）
                                   ‖  S4-WAVE-A-EXECUTED 收口簿記
                                   ‖  P2e 歸檔
                                   ‖  Steward 貼 S3-FEATURES-PLAN-go（採納）
                                   ‖  STRUCT 80／97 出口句（Registry 橫切）
```

- S5 用 **skip-sync／dry／庫內 as-of**；與 A1 **不互搶**放量 sync。  
- Wave A **未**正式 EXECUTED 時：S5 標 **partial／可用子集**（FULL-GO §3 已釘）。  
- 分數齊後接 `LOOP-S5-TO-S4-OPT`（寫最小安全 backlog；**不**默授 APPLY／全 taxonomy 重訓）。  
- `S3-FEATURES-PLAN-go` ≠ `S3-WAVE-*-go` build。

### 勿做

| 禁 | 理由 |
|---|---|
| 再貼／重跑 `P1-DRIFT: C-go` | **已 EXECUTED** |
| 稱 S0／Discovery 仍開；重跑 S0 | **DONE** |
| 再貼 LOOP 三連當新開工碼 | **已消費**（`LOOP-S4-S5-FULL-GO`）——下一刀＝**執行**非再授權 |
| 重啟／kill Wave A 訓練矩陣 | FULL-GO：**do-not-restart**；矩陣已 DONE |
| 第二／第三支 A1；kill 雙看 | Steward `(a)` |
| 無 `predict-asof-write-go` 寫 `prediction_values` | 本 LOOP 允 dry |
| `SIM --apply`／假確立級／改 dgate | keep |
| Dividend／寬窗／放量 FinMind／FRED | THAW-bounded |
| 以 SIGN／econ 綠假關 S3／S5／可交易 | 階段未完 |
| 重貼 `Q-R8`／37 REGISTRY | 已 EXECUTED |

---

## 4. Steward go 句（**僅仍開閘**）

> 已授權待執行者（LOOP／75 COMMIT／Wave A 收口）**不**再列為「請貼」——列於「可先做」。

### 仍開｜建議優先貼（採納、零 train）

```text
S3-FEATURES-PLAN-go + GATE-keep + NHC-keep + API-THAW-bounded + no-SIM-apply
```

（採納 S3 特徵類別 SSOT；**不含** `S3-WAVE-*-go` 放量 build。）

### 仍開｜Registry 橫切（可同步、非擋 #1）

```text
U0-97: 不登
```

```text
U0-80-SPLIT-BOUND: second_binding=<id> + role=price_limit_ref
```

（80／97 寫庫另要對應 `REGISTRY-GO`＋honesty；STRUCT **未**預發完整 COMMIT 句。）

### 仍開｜另層（錯峰後；非本波 #1）

```text
predict-asof-write-go
SIM-FIRST-CELL-go
```

### 可選明示 ack（非必要；C 帳已在）

```text
P2e-archive-ack | P1-C-EXECUTED-counts | no-retrain | no-SIM-apply
```

### 已消費／勿重貼當開工

- `SIM-SELF-EVOLVE-OPT-PLAN-20260804-go + GATE-keep + NHC-keep + API-THAW-bounded`
- S0 Discovery／`SIM-S0-RESIDUAL: tw.daily_bar…`（診斷窗）
- `P1-DRIFT: A`／`P1-DRIFT: C-go | FZ/GATE-keep | no-SIM-apply | skip-sync`
- `S4-FAMILIES-PLAN-go + …`
- `LOOP-S4-TO-S5-go`／`LOOP-S5-TO-S4-OPT-go`／`LOOP-FULL-CHAIN-go`＋`S4-WAVE-A` ack（見 FULL-GO §5）
- `REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo`（honesty 已發——下一刀＝**COMMIT 執行**，非再貼）
- `Q-R8=jp-ok`／`REGISTRY-GO: binding=37 + …`
- G13／G16 選單與臂；`SIGN-ACTIVE3-h20-record-go`
- `(a) 雙看`（勿當新開工碼）

---

## 5. 誠實探針筆記

### C2／Wave A（本波核心）

| | |
|---|---|
| `LOOP-S4-S5-FULL-GO` | ✅ ≈13:30 登錄 |
| `LOOP-S4-TO-S5-EXECUTED*` | ❌ **缺** → #1 |
| `LOOP-S5-TO-S4-OPT-EXECUTED*` | ❌ 待 S5 分數後 |
| `S4-WAVE-A-EXECUTED*` | ❌；train-matrix.log **DONE** 13:30:30 |
| 可用 artifact（FULL-GO／log） | RankRidge H20／H40／H60／H120；RankGBDT H20×3seed＋H60×3seed；方向臂另帳 |
| A1 | 877801 仍跑——S5 **錯峰**、不殺 |

### `tw.daily_bar`／75

| | |
|---|---|
| honesty | ✅ ISSUED |
| `U0-75-REGISTRY-EXECUTED*` | ❌ |
| 下一步 | 依 DRY **COMMIT**（既有 GO）；勿重貼 GO 當未授權 |

### 階段對照

| 主軸 | 本波關係 |
|---|---|
| S0 | ✅；殘差 75＝COMMIT 加料 |
| S1 | A1 進行中＝可先監看；⊥ 預測 |
| S2 | 地板 DONE；C1 待 S3 採納後 |
| S3 | 報告待 `S3-FEATURES-PLAN-go` |
| S4 | P1-C＋Wave A 矩陣進階；正式 WAVE-A-EXECUTED 另帳 |
| **S5／C2** | **本波 #1 掛點**（LOOP-S4-TO-S5 執行） |

---

*完。LIVE：C ✅；LOOP 三連授權 ✅／EXECUTED ❌ → #1＝跑 S5 dry＋OOS 並落 EXECUTED；Wave A 矩陣 DONE・不重啟；75＝COMMIT 可同步；S3-FEATURES-PLAN-go 仍開可貼。零重貼 C-go；零重 S0；零 sim `--apply`。*
