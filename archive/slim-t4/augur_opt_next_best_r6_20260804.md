# Augur 優化｜最佳下一步 r6（self-evolve 主軸 · LIVE · 2026-08-04 ≈12:06+08）

> **性質**：[I] Steward 接續便利條。**非**新計畫 SSOT；執行序以已拍 self-evolve 計畫為準。  
> **取代／升級**：`reports/augur_opt_next_best_r5_20260804.md`——r5 #1＝裸等 `C-go`；本檔改為 **S0 DONE 後之 P1-C 對帳叉**（證據有並行 econ、無正式 C-EXECUTED）。  
> **audit**：`audits/OPT-R3-NEXT-BEST-R6-20260804.md`  
> **self-reported（#32a）**：優先序＝呈案；LIVE 數字引 `pgrep`／log／既有 audit。

| SSOT | 路徑 |
|---|---|
| **approved 主軸** | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`（§7.1 GO；§0.5 重覆驗証；§2.7 S0 DONE） |
| GO／登錄 | `audits/SIM-SELF-EVOLVE-OPT-PLAN-GO-20260804.md` · `audits/SIM-SELF-EVOLVE-OPT-PLAN-20260804.md` |
| S0 Discovery | `audits/SIM-SELF-EVOLVE-S0-DISCOVERY-20260804.md` — **DONE** |
| S0 殘差 `tw.daily_bar` | `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-20260804.md`（診斷＋哨降級 DONE；COMMIT 仍待） |
| P1 A | `audits/P1-DRIFT-A-EXECUTED-20260804.md` |
| P1 C | **無** `P1-DRIFT-C-EXECUTED*`（`ls` ≈12:06） |
| U0-37 | `audits/U0-37-REGISTRY-EXECUTED-20260804.md`（mapped **21**；`Q-R8=jp-ok` **已消費**） |
| STRUCT 80／97 | `audits/U0-STRUCT-378097-20260804.md` · paste＝`audits/U0-80-97-EXIT-PASTE-20260804.md` |
| G13-106 | `reports/augur_g13_awaiting106_triage_ask_20260804.md`（呈案；非再擇臂） |
| A1／DATA-FILL | `audits/DATA-FILL-DUAL-WATCH-20260804.md` · `audits/DATA-FILL-TO-20260803-PROGRESS-20260804.md` |
| 地基／r3／r5 | foundation＋step r3＋`augur_opt_next_best_r5_20260804.md`（context；**本檔升級便利條**） |

---

## 1. LIVE 核對（勿用陳舊 r5 敘事）

| 項 | LIVE（≈12:06+08） | 證據 |
|---|---|---|
| 計畫 GO | ✅ EXECUTED | `SIM-SELF-EVOLVE-OPT-PLAN-GO-20260804.md` |
| **S0 Discovery** | ✅ **DONE**（勿稱仍開） | `SIM-SELF-EVOLVE-S0-DISCOVERY-20260804.md` 五項勾完 |
| S0 殘差 `tw.daily_bar` | 🟡 診斷／DRY／哨降級 ✅；權威仍 NULL | `SIM-S0-RESIDUAL-*`；待 `REGISTRY-GO:75` |
| P1-DRIFT **A** | ✅ EXECUTED | `P1-DRIFT-A-EXECUTED-20260804.md` |
| P1-DRIFT **C** | ❌ **無** `P1-DRIFT-C-EXECUTED*` | `ls` 零檔；**≠**「已 auth／已 EXECUTED」 |
| 並行經濟尺 | H60 ✅ 完；H20 🟡 **仍跑**（pid **930006**） | `/tmp/p1-drift-c-econ-h60.log`／`…-h20.log`；`train_ranker` **現無** |
| U0-37 | ✅ REGISTRY EXECUTED；mapped **21／98** | `U0-37-REGISTRY-EXECUTED`；**勿**再貼 `Q-R8=jp-ok` |
| STRUCT **80／97** | 仍開（俟拆／俟偵測器｜不登）—**僅 paste** | `U0-STRUCT-378097` |
| G13-106 | ask 已備；非再擇臂 | `augur_g13_awaiting106_triage_ask_20260804.md` |
| A1 雙看 | 🟡 仍跑（Steward `(a) 雙看`） | 861734（`--end 08-03`）＋877801（`--end 08-04`）；log mtime **12:06**→**JapanStockInfo** by-date；403＝0（既有帳） |
| DATA-FILL→08-03 | **未完成**（無完成帳） | `DATA-FILL-TO-20260803-20260804.md` missing；樣本短表未齊 |

**不是**下一步：重開 S0；稱 C 已 EXECUTED；重貼 37／`Q-R8`；重貼 G13／G16 選單；第二／第三支 A1；sim `--apply`；放量；假關確立級。

---

## 2. 單一「最佳下一步」

**S0 已 DONE；依 approved 計畫下一刀＝預測車道 P1-C 對帳（無 `P1-DRIFT-C-EXECUTED*`）——Steward 擇：正式授 `P1-DRIFT: C-go | FZ/GATE-keep | no-SIM-apply | skip-sync`（錯峰 A1／H20 後多 horizon 重訓），或認定並行 H60＋進行中 H20 已屬 C 效力 → H20 完即走 P2e 歸檔、勿無對帳重疊重訓。**

### 為何是這把（相對 r5／主軸）

| 候選 | 裁決 |
|---|---|
| **P1-C 對帳（S4→S5／P1 波次）** | ✅ **#1**：計畫 §5／§4／文末＝預測車道主刀；LIVE **確認無 C-EXECUTED**；但存在 `p1-drift-c-econ-*` 並行產物 → **對帳叉**，非陳舊「假裝無事再貼 C-go」單敘事 |
| S1 資料完整（THAW） | 雙看已授、A1 在推進 JapanStockInfo；**無人新句可催**；且 ⊥ 預測熱路徑 |
| 殘差 `REGISTRY-GO:75` | 解 `calendar_unmapped`／時鐘週報——**可同步**；計畫標為殘差、**不擋** P1-C |
| P2e 單獨當 #1 | 僅當 Steward **已認**並行＝C；否則缺正式對帳 |
| STRUCT 80／97／G13-106 | Registry 橫切；計畫明示 **不擋** P1-C |
| sim 首格／predict 寫庫 | §7.3 另層；**另授** |

---

## 3. 可先做／可同步／勿做

### 可先做（不擋 #1）

| # | 項 | 狀態 |
|---|---|---|
| 1 | **A1／DATA-FILL 雙看**（不殺不疊第三支） | 進行中；S1 THAW-bounded |
| 2 | **H20 終態監看→備 P2e 材料**（stdout 歸檔；禁假確立級） | pid 930006 仍跑 |
| 3 | `tw.daily_bar` DRY／honesty 呈請維持（等 75） | 備料 ✅ |
| 4 | G13-106 triage ask **審閱**（另本；不機械清庫） | 報告已在 |
| 5 | HANDOFF 便利條改指 **本 r6**（commit **另授**） | 文件 |

### 可同步

```
P1-C 對帳／C-go（人）  ‖  A1＋861734 雙看收尾（S1）
                        ‖  REGISTRY-GO:75（tw.daily_bar 權威）
                        ‖  STRUCT 80／97 出口句
                        ‖  G13-106 triage（另本）
                        ‖  H20→P2e 歸檔準備（若認＝C）
```

- 不互搶 Registry COMMIT；不與 A1 疊第二支 `--end 2026-08-04`。  
- 若選正式 C-go：`--skip-sync`；錯峰 H20／A1 重活；**禁**順便 `SIM --apply`／假可交易。  
- `REGISTRY-GO:75` ≠ 殘差診斷句（診斷句已消費）；寫庫須 honesty＋`decided_by=hugo`。

### 勿做

| 禁 | 理由 |
|---|---|
| 稱「S0 仍開／Discovery 未收」 | S0 **DONE** |
| 稱「C 已 EXECUTED／已正式 auth」 | **無** `P1-DRIFT-C-EXECUTED*` |
| 無對帳即重疊再開多 horizon 重訓 | Discovery／計畫：並行待 Steward 對帳；H20／A1 仍佔機 |
| 重貼 `Q-R8=jp-ok`／37 REGISTRY | **已 EXECUTED**（mapped 21） |
| 重貼 G13／G16 **選單**／稱仍待擇臂 | ARMS＋年齡門／ALWAYS 已 EXECUTED |
| 重貼／重跑 SIGN／`P1-DRIFT: A` | 已 EXECUTED |
| 重貼 `SIM-S0-RESIDUAL: tw.daily_bar…` 當開工 | 殘差窗已接；下一刀＝**75 REGISTRY-GO** |
| 第二／第三支 A1；kill 雙看 | Steward `(a) 雙看` |
| Dividend／寬窗／放量 | THAW-bounded |
| `SIM --apply`／predict 寫庫當 C 默認 | 須另句 |
| 假關確立級／可交易 | dgate pass=0；econ≠確立級 |

---

## 4. Steward go 句（僅仍開閘）

### 主裁叉（本波 #1——擇一）

**叉 A｜正式開 P1-C（多 horizon／經濟終關路徑）**

```text
P1-DRIFT: C-go | FZ/GATE-keep | no-SIM-apply | skip-sync
```

（錯峰：A1 雙看／H20 淨後再疊重訓為宜。）

**叉 B｜認定並行已屬 C → P2e（勿重跑重訓）**

Steward 明示等價一句即可（示例，人可改寫）：

```text
P1-C-RECONCILE: parallel-econ=counts-as-C → P2e-archive | no-retrain | no-SIM-apply
```

然後等 H20 終態，歸檔 H60＋H20 stdout（(a)(b)(c)），**不**宣稱確立級。

### 加料（平行、非擋主裁）

```text
REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo
```

（`tw.daily_bar`→`TaiwanStockPrice`／Annex F §2.1；解 `calendar_unmapped`。）

```text
U0-97: 不登
```

```text
U0-80-SPLIT-BOUND: second_binding=<id> + role=price_limit_ref
```

（80／97 寫庫另要對應 `REGISTRY-GO`＋honesty；STRUCT **未**預發。）

若要預測寫庫／sim 首格（**另層、非 C 默認**）：

```text
predict-asof-write-go
SIM-FIRST-CELL-go
```

### 已消費／勿重貼當開工

- `SIM-SELF-EVOLVE-OPT-PLAN-20260804-go + GATE-keep + NHC-keep + API-THAW-bounded`
- S0 Discovery／`SIM-S0-RESIDUAL: tw.daily_bar authoritative-binding…`（殘差**診斷**窗）
- `Q-R8=jp-ok` · `REGISTRY-GO: binding=37 + honesty=37 + decided_by=hugo`
- `G13-Q22: machine-supersede-ok` · `G16-ALWAYS: enable-always-go` · 年齡門批次
- `SIGN-ACTIVE3-h20-record-go`
- `P1-DRIFT-PLAN-go`／`P1-DRIFT: A`
- `U0-STRUCT: 37=俟|jp-ok ; 80=俟拆|登事件欄 ; 97=俟偵測器|不登`（STRUCT 本身；37 出口已走完）
- `(a) 雙看`（DATA-FILL／A1——已落地監看，勿當新開工碼重貼）

---

## 5. 誠實探針筆記

### C（對帳核心）

| | |
|---|---|
| `P1-DRIFT-C-EXECUTED*` | **不存在**（≈12:06） |
| 正式 `C-go` 帳 | **無**（計畫 GO **不含** C） |
| 並行產物 | H60 econ **完**；H20 econ **進行中**（log 名 `p1-drift-c-econ-*`）；`train_ranker` **現無** |
| 結論 | #1＝**對帳叉**（正式 C-go **或** P2e）；**不是**「已 EXECUTED 故勿再提 C」；也**不是**無視並行的陳舊單句 |

### `tw.daily_bar` 殘差

| | |
|---|---|
| 殘差授權窗 | ✅ 已接（診斷＋DRY＋哨 `calendar_unmapped=true`） |
| Registry COMMIT 75 | ❌ 仍待 `REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo` |
| sim 首格 | 仍 `sim_run_link=0`；另待 `SIM-FIRST-CELL-go` |

### Binding 37／80／97

| | |
|---|---|
| **37** | ✅ EXECUTED；mapped **21**；`Q-R8` 已消費 |
| **80／97** | STRUCT 仍俟；出口 paste 仍開 |

### A1／DATA-FILL（≈12:06+08）

```text
pgrep: daily_maintenance --end 2026-08-03 → 861734
       daily_maintenance --end 2026-08-04 → 877801 (+ bash 877790)
log:   /home/hugo/logs/daily_maintenance_2026-08-04_a1a2.log
       mtime 12:06; ~15.6KB; 進至 JapanStockInfo by-date（已過 EuropeStock 段）
econ:  run_economic_eval --h 20 … prodset → 930006（仍跑）
403:   既有帳 0；本輪未重 grep 全檔
exit:  A1／861734／H20 皆尚未終態 — 勿殺勿疊
fill:  「全表已到 08-03」未成立；完成帳缺檔
```

---

## 6. 與主軸階段對照（讀法）

| 主軸 | 本波關係 |
|---|---|
| **S0** | ✅ 關帳；殘差 75＝Registry 加料，非重開 Discovery |
| **S1** | 雙看／THAW 進行中＝可先做監看；**≠**預測硬閘 |
| **S2** | KH 可引用（Discovery D-KH）；不開新灌因子 |
| **S3** | 隨 C／後續特徵重覆驗；本便利條不單開 |
| **S4→S5** | **本波 #1 掛點**（P1-C 對帳／P2e） |
| r3 橫切 | 80／97／G13-106／75 ‖ 不擋 #1 |

---

*完。LIVE：S0 DONE；C 未 EXECUTED → #1＝P1-C 對帳叉（C-go **或** P2e）；37／Q-R8 已消費（mapped 21）；A1 雙看＋H20 仍跑；殘差下一刀＝`REGISTRY-GO:75`（可同步）。零新放量；零 sim `--apply`。*
