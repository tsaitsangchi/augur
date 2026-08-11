---
title: augur 深化理解＋專案優化地基（合併）r13
status: final
series: deep_understanding_and_opt
round: r13
date: 2026-08-08
viewpoint: 2026-08-08T19:50+08:00
layer: "[I]"
role: 後續優化地基（理解＋與選刀板對齊）；刷新 r11；選刀以 r13 導航為準
supersedes_as_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r11_20260807.md
inherits_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r11_20260807.md
  - reports/augur_deep_understanding_r8_20260806.md
  - reports/augur_deep_understanding_r6_20260804.md
companion_plain_charter: reports/augur_project_charter_plain_zh_r13_20260808.md
exec_nav: reports/augur_opt_stepwise_best_next_plan_r13_20260808.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
self_reported: true
---

# augur 深化理解＋專案優化地基 r13（2026-08-08）

> **性質**：[I]；**不創** [N]；不解凍；不 sim `--apply`；不假關確立級；**勿重掃假綠**。  
> **一句**：在 r11 理解上吸收 **08-07→08-08** 增量（tip／五窗／圖／帳務／模型挑戰鏈／hold-#1），收成**下一段優化地基**。  
> **疊用**：人話憲章 r13 → **本檔理解** → **`reports/augur_opt_stepwise_best_next_plan_r13_20260808.md` 選刀** → 准否／驗收＝S1→S5 SSOT＋ARCHIVE／standing／audit。  
> **覆蓋誠實**：非整庫逐檔複讀（reports／audits／scripts 體量大）；本輪＝**結構地圖＋LIVE 親查＋08-07→08-08 收斂**；細節長表仍回 r6／r8／r11／INVENTORY。

---

## 第一部｜深化理解

### §1 專案是什麼（產品真相）

Augur＝**只用真實資料、誠實預測台股相對強弱**的系統（觀兆→機率；非明牌）。

```text
真實價／基本面／資金流（S1）
  → 知識／KH（S2）
    → 特徵／prodset（S3）
      → 模型族 train／serve（S4）
        → 日更預測／方向／經濟尺／顧問／模擬（S5）
  ↺ S5 證據回饋 S4／S3／S2（回饋弧；非 checklist 一次勾完）
```

| 它是 | 它不是 |
|---|---|
| as-of 凍結、walk-forward、多 seed、#14 經濟終關 | 保證獲利／價格點位神算 |
| 相對排序為生產熱路徑；方向機率屬可證偽實驗 | `evaluated_pass` 可默認綠燈 |
| Sole Steward；plan-first；AI self-reported | AI 代簽升格／假兆補表 |

成功定義＝**經濟價值**（淨 Sharpe／hit vs bench），不是裸 IC。

### §2 倉庫地圖（讀檔導航）

| 區 | 作用 |
|---|---|
| `constitution/` · `specs/` | Layer 0–7 **[N]** 治權與規格 |
| `docs/` | 靈魂／原則精華／領域大憲章（doctrine） |
| `src/augur/` | 實作：`features`／`models`／`evaluation`／`advisor`／`ingestion`／`knowledge`／`evolution`／`philosophy`／`arena`／`catalog`／`core`／`universe`／`llm`／`execution`／`deliberation`／`identity`／`audit`… |
| `scripts/` | CLI 動詞（sync／train／predict／B3／econ／探針…）≈**380+** |
| `reports/` | 計畫／理解 [I] |
| `audits/` | GO／EXECUTED／ADOPTED／ARMED 留痕 [I] ≈**690+** |
| `models_artifacts/` | joblib；挑戰族可不進／已進 registry 仍 **STOP** |
| `tests/` · `ops/` · `tools/` | 回歸／運維／MCP |
| PostgreSQL `augur` | System of Record（本機約 **62GB**） |

工具規則：`CLAUDE.md`（plan-first、#9 真兆、#11／#14、#32 預凍、#35 回歸鎖）。  
接續入口：`HANDOFF.md`（史深；**現況以本檔＋r13 導航＋最近 audit 為準**）。

### §3 S1→S5 × 硬邊界（運轉真相）

| 階 | 08-08 一句 |
|---|---|
| **S1** | 價到 D 才日更；**禁假 B3**；週休候下一交易日 |
| **S2** | KH／顧問旁軌；CYCLE-3＠08-07 已 re-accept |
| **S3** | 熱路徑 **prodset active3**；圖候選旁路在；**不**默入熱路徑 |
| **S4** | 冠軍 **RankRidge＠2026-07-31**；**NF-pause**；挑戰多 **STOP promote** |
| **S5** | tip＝**2026-08-07**；曾五窗雙明示掛齊；standing 預設仍 **20,60**；H20 **econ=dead**；sim **禁 apply** |

硬邊界（導航釘）：

```text
FZ/GATE-keep | skip-sync-B | no-SIM-apply | NF-pause
| no-cron-B3 | 誠實 econ | no-promote 默認 | 勿重掃假綠 | hold-#1
```

Steward 慣例（延續＋08-08 釘）：

1. 其他模型＝凍結窗上**一次一族**有界 `NF-*-go`；證據／SKIP 皆誠實。  
2. **勿重掃假綠**。  
3. **主軸＝hold-#1：候下一 tip→站式 B3**。  
4. 五窗＝**雙明示**；升格＝**另軌**。

### §4 LIVE 錨（2026-08-08 ≈19:50+08 · 親查）

| 錨 | 值 |
|---|---|
| 日曆 | **2026-08-08 六**（休市假設） |
| `TaiwanStockPriceAdj` max | **2026-08-07** |
| `feature_values`／`core_universe_asof` | **2026-08-07** · core n=**285** |
| `prediction_probability` tip | **2026-08-07** · **五 H** 各 285 |
| serve 模型 | RankRidge **asof 2026-07-31**（五 H artifact 皆在） |
| `model_registry` | **50**（含 Wave-A 18 列 STOP 回填） |
| DB size | **≈62 GB** |
| #1 watcher | **ARMED** D=**2026-08-10** horizons=**20,60** · pid 見 `OPS-B3-A2B3-ARMED-20260810` |
| H20 econ | **dead**（五窗≠修綠） |
| 圖＠08-07 | `stock_graph_edge` **33,567**；G3 tip SKIP **已癒** |

### §5 08-07→08-08 理解增量

| # | 增量 | 證據帳（示例） |
|---|---|---|
| 1 | B3＠08-07 verified；tip 日更閉合 | `VERIFY-B3-20260807-EXECUTED` |
| 2 | CYCLE-3 re-accept；DIR＠tip 基本閉 | `SIM-LOOP-CYCLE-3` |
| 3 | P6 freeze→**08-07**（H20＋H60） | `P6-REFIT-FREEZE-20260807-EXECUTED` |
| 4 | FRED macro heal（部分系列仍延遲誠實） | `FRED-MACRO-HEAL-EXECUTED` |
| 5 | G3 path=A＋**GRAPH-REBUILD＠08-07** | G3／REBUILD／`GRAPH-0807-STATUS-CLOSED` |
| 6 | SCHEMA #19：CHK ALTER＋orphan 18＋reprobe **可登錄層關閉** | SCHEMA-*／`REPROBE` |
| 7 | 預訓練／序列／表格挑戰鏈大量觸完（Chronos／Moirai／TimesFM NaN-SKIP／FTTR／PatchTST…）多 **STOP** | `NF-*-0B-EXECUTED` |
| 8 | 五窗 **A＋B 雙明示**＠tip 08-07 執行；standing 預設**未**改 | `B3-HORIZONS-FIVE`／`SERVE-FIVE-H` |
| 9 | hold-#1 accepted；A2B3 arm＠**08-10** | `HOLD-1-ACCEPTED`／`OPS-B3-A2B3-ARMED-20260810` |
| 10 | 「tip 後 10 日實現漲幅」**誠實不可算**（價頂＝tip） | 對話／預測 Top10 僅 predict |

**未變**：確立級假不了；sim 禁 apply；NF／M／β5 凍結預設；Sole Steward；冠軍護城河深。

### §6 模型／特徵誠實結論（刷新）

| 結論 | 含義 |
|---|---|
| 冠軍仍深 | prodset3 上樹／SVM／MLP／序列 TFM／PatchTST／FTTR 難穩過 RankRidge H60 門 |
| 有證據≠可升格 | Moirai／Chronos／GARCH／classical 等可有方向 hit 證據；預凍 **STOP promote** |
| TimesFM | 本機 forecast NaN → 0b **誠實 SKIP**（≠ stub 塗綠） |
| 圖 | 邊與候選＠tip 可消費旁路；**≠** 熱路徑／GNN 翻案 |
| registry | Wave-A 可登錄且標 STOP；NF 新字面**勿默 ADD CHK** |
| 下一進化常不是新族 | 日更穩態／誠實尺／特徵增量／圖提拔證據；優於假掃族表 |

### §7 綜合債表（r13）

| ID | 債 | 狀態 |
|---|---|---|
| R13-01 | A→B3＠**下一 tip（釘 08-10）** | 🟡 **主軸** ARMED／WAIT |
| R13-02 | econ／dgate 誠實形（H20 dead） | 🟡 不修綠 · ∥ |
| R13-03 | standing 五窗永久化 | ❄ 須另雙明示改殼 |
| R13-04 | P6 擴 H40／82／120 | 🟡 閒時可先 |
| R13-05 | 圖提拔／熱路徑開 | 🔴 另 VERIFY／高門檻 |
| R13-06 | 升格挑戰族 | ❄ 另軌 · 禁默 |
| R13-07 | NF 新族 | ❄ pause · 勿重掃 |
| R13-08 | STRUCT／scripts 冗餘 | 🔴 低優先 |
| R13-09 | M／β5／sim／Dividend | ❄ |
| R13-10 | 10–14 治權日曆 | 🟡 排程 |
| R13-11 | 大量 audits 未入版控 | 🟡 文件債（另 commit 授） |
| R13-12 | tip 後實現報酬研究 | 🔴 等價蓋過 tip＋N 日 |

---

## 第二部｜優化計畫（選刀對齊）

> **執行選刀 SSOT**＝`reports/augur_opt_stepwise_best_next_plan_r13_20260808.md`（本檔不重複長板；冲突以導航為準）。

### §8 讀序與操作協議

```text
人話憲章 r13
  → 本檔理解（第一部）
    → r13 導航選刀
      → S1→S5 SSOT + 最近 ARCHIVE/standing/audit
日更: skip-sync-B · no-SIM-apply · 誠實 econ · hold-#1 · 不假 B3
```

1. 選刀＝導航板 `#` 或 Phase 步。  
2. 缺 GO → AskQuestion；禁默訓／默升格。  
3. 重大收斂 → r14 或刷新導航。  
4. **勿重掃假綠**；已 STOP 族同尺不刷。

### §9 最佳下一步（摘要）

| 角色 | 內容 |
|---|---|
| **主軸** | hold-#1 → 價≥**2026-08-10** → 站式 B3 `20,60` |
| **可∥** | #2 誠實披露；#10 NF／凍結輕監 |
| **可先（閒時）** | P6 擴三長窗；升格門檻文件；r13 版控 commit（另授） |
| **禁** | sim-apply；塗綠 dgate；默改五窗 standing；挑戰 SERVE-SWAP |

```text
hold-#1 | A→B3@2026-08-10 | horizons=20,60 | NF-pause | no-SIM-apply | no-fake-B3
```

### §10 驗收

- [x] 產品／地圖／S1–S5／LIVE／增量／模型結論／債表  
- [x] 選刀對齊 r13 導航；人話憲章成對  
- [x] 覆蓋誠實聲明  
- [x] 不創 [N]、不開訓、不解凍  

*完。[I] · self-reported。*
