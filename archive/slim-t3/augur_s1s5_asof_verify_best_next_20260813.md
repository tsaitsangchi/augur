---
title: 本地 AI 股市預測模擬閉環——最佳下一步／可先／可同步＋歷史 as-of 驗証
status: final
series: s1s5_loop
date: 2026-08-13
viewpoint: 2026-08-13T13:10+08:00
layer: "[I]"
role: S1→S5 閉環在 r15 視點的選刀＋「過去 as-of 能否訓／驗」答覆；其他模型驗証＝V0 刷新＋協議
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
parent_go_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
exec_nav: reports/augur_opt_stepwise_all_problems_r15_20260813.md
other_verify: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
residual: audits/NF-0812-RESIDUAL-NAME-CARD-20260813.md
self_reported: true
---

# 本地 AI 股市預測模擬閉環 · 選刀＋歷史 as-of（2026-08-13）

> **一句**：閉環**怎麼轉**＝r16；本質／GO＝08-04。本檔＝**今天怎麼走**＋**能不能用過去 as-of 收特徵／訓練／驗証**。  
> **LIVE（親查 13:10+08）**：PriceAdj／特徵／tip＝**2026-08-12**（尚無 08-13）；watcher 候 **≥08-13**；H20＝dead、H60＝thin；校準器仍掛 **08-07**。  
> **不創 [N]**；不假 B3；不 sim-apply；不默升格；**勿重掃** 0812 已 EVIDENCE 族。

---

## §1 歷史 as-of：可以，而且這是唯一合法做法

**可以。** 用「當時看得到的世界」收特徵、訓練、樣本外驗証——這就是閉環 S3／S4／S5 的正門，不是偷看未來。

| 可以 | 不可以 |
|---|---|
| as-of＝**已有** `feature_values.panel_date` 的交易日 D（現 tip＝08-12） | 用還沒進庫的「今天價」假裝 D 已到（假 B3） |
| 特徵只切 **D 當下可見**（anti-leakage） | 拿 D+1 的價／財報回填 D 的特徵 |
| 在 D 上 `train_ranker --asof D`／L2 `--date D`（skip-sync） | 一次把 taxonomy 全族訓完當「已確立」 |
| 多 D 走 walk-forward 當**重覆驗証** | 同一族、同一尺把 0812 EVIDENCE 再刷成假綠 |
| 驗完寫 #11／#14／SKIP；**no-promote** | sim `--apply`；改冠軍；塗綠 dgate |

**特徵不用重抓一遍市場 API。** 庫內 `feature_values` 已鋪到 **08-12**（tip **37** 種）。各截面模型（RankRidge／GBDT／XGB…）**共用這張 panel**，不是每族各採一套價。缺的是序列／圖等**額外張量**（所以 Wave C–E 曾 SKIP），不是「沒有歷史價」。

**曆法（親查）**：`feature_values` 不是每個交易日都有。2018–2025＝月頻；2026＝月頻 **01-31…07-31** ＋日頻 **08-04…08-12**。`train_ranker --asof D` 讀 **所有 `panel_date≤D`**（anti-leakage）；在 D **出單／emit** 才需要 **剛好 D** 那一張 panel。因此「過去 as-of 訓練」合法；「把整段歷史補成全日頻 panel」是另一張 S3 GO，本窗不做。

**殼已通（本窗 dry-plan，零寫庫）**：

```text
bash scripts/run_daily_retrain_l2_all_rank.sh --date 2026-08-12 --dry-plan   # 通
bash scripts/run_daily_retrain_l2_all_rank.sh --date 2026-08-07 --dry-plan   # 通（歷史 D）
bash scripts/run_daily_retrain_l2_all_rank.sh --date 2026-06-30 --dry-plan   # 通
# 真訓（另句 --apply；禁與 B3 開火搶槽；仍 no-promote）
```

`train_ranker.py --asof D`＝只讀 DB as-of，**⊥ live FinMind**。

---

## §2 閉環各段：最佳下一步／可先／可同步

對齊 Steward 管線：抓數 → KH → 特徵 → 模型 → 預測（漲跌比）＋回饋。

| 段 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態（13:03） |
|---|---|---|---|---|---|
| **S0** | 定錨 | 讀本檔＋08-04 SSOT；不另修憲 | — | — | 🟢 GO 仍在 |
| **S1** | 資料完整／日更 | 候 `PriceAdj≥08-13` → B3 `20,60` | **否**（無價） | 開火獨佔 | 🟡 hold-#1 |
| **S2** | raw↔KH | 守 ingest `--check`；**不等 S1** | 巡檢＝是 | 是（避開 B3） | 🟢 S0/S3 lag=0 |
| **S3** | 特徵完整＋重覆驗 | 沿用 panel＠08-12；P6 校準仍＠**08-07**（已對帳） | 文件已做 | 訓 P6＝**否**（另 GO） | 🟢 特徵在；校準缺口❄ |
| **S4 冠軍／邊界 A** | 多模型重覆驗 | 08-12 L2 已訓 Ridge×5＋challenger×8 | 同 asof 再訓＝**否** | 歷史其他 D 的 L2＝**可先文件／另 GO 才 --apply** | 🟢＠08-12 |
| **S4 其他族** | taxonomy／NF | 見 §3：V0 本窗刷新；殘格**點名**才 0a | V0＝是 | 開新族＝否（NF-pause） | V0🟢；V4❄ |
| **S5** | 漲跌比／#14 | 披露 dead／thin；不塗綠 | 披露已做 | dgate evaluate＝否 | 🟡 誠實形 |
| **S5 sim** | 風險形狀 | **禁 apply** | 否 | 否 | 禁 |
| **回饋 S5→S4** | 重選族／H | 既有 backlog；不因 tip WAIT 假 sweep | 文件＝是 | 重訓＝讓 B3 | 🟡 |
| **回饋 S3→S2** | KH 缺口 | 與市場分軌；假 decline 已修 | 是 | 是 | 🟢 |

**現在（人話）**

1. **閉環最佳下一步**＝仍是 **S1／M1**：價到再日更。這是前向鏈的日頻心跳，不能用歷史 as-of 代替「今天的 B3」。  
2. **可先**＝歷史 as-of **協議＋盤點**（本檔／V0）；不是假跑今天。  
3. **可同步**＝KH 巡檢、誠實 #14、V0 唯讀。B3 開火則停重訓。  
4. **其他模型驗証**＝先 V0（本窗已做），**不要**把 0812 六族再刷一遍。

---

## §3 其他模型驗証（進行到哪、下一步）

矩陣仍是 V0–V5（`augur_s4_other_model_verify_matrix_plan_20260806.md`），疊加 0812 收口。

| 軌 | 本窗 | 下一步 |
|---|---|---|
| **V0 盤點** | **已做** LIVE registry（§3.1） | 當帳；不必重掃 taxonomy |
| **V1 既有截面** | L2＠08-12 已覆蓋 RankRidge＋GBDT／XGB／Cat／RF／KNN／MLP／SVM | **禁止**同尺再訓 08-12；要 walk-forward 另列歷史 D＋GO |
| **V2 缺 adapter** | 殘格卡：VECM／TCN／NB／Daily*／RL | **點名**才 `*-go-plan` |
| **V3 S5↔S4** | 08-07 已跑過一輪 | 新 asof 回饋另句；讓 B3 |
| **V4 新族** | ARIMA／VAR／Kalman／COINT／GARCH／GNN＠0812＝EVIDENCE **no-promote** | **禁同尺重掃**；解 pause 須另句 |
| **V5 S5-only** | tip 兩窗 econ 已披露 | 不修綠 |

### 3.1 V0 LIVE（親查 13:03）

`model_registry` **family**：

| family | n | 最新 asof |
|---|---|---|
| RankRidge | 35 | **2026-08-12** |
| RankGBDT | 12 | 08-12 |
| RankXGB／Cat／RF／KNN／MLP／SVM | 各 6 | 08-12 |
| DailyGBDT／DailyGBDT_cal／DailyLogit／MktLogit／DirStackM | 1–2 | **2026-05-31**（方向臂舊） |

08-12 列：H20×3、H40×1、H60×7、H82×1、H120×1（對齊 L2 邊界 A）。  
registry asof：**無 08-07**（fv 有；校準器仍掛 08-07）。LIVE 掛載仍是 RankRidge H20／H60；方向族**未**跟日更 L2。

**其他模型**若指「方向臂 Daily*」→ 殘格卡已點名，**另 GO**，⊥ ALL-RANK。  
若指「VECM／TCN／NB」→ 同樣另 paste。  
若指「再驗一遍 ARIMA…GNN」→ **拒**（假綠）。

---

## §4 若要真跑歷史 as-of（工作包，未授 --apply）

### WP-H｜邊界 A 多 D walk-forward（截面族）

```text
WHEN: Steward 明示日期清單 且 PriceAdj/fv 已蓋過該 D 且 B3 未開火
DO:   for D in <清單>:
        bash scripts/run_daily_retrain_l2_all_rank.sh --date $D --apply
DONT: D > fv_max; 假 B3@08-13; promote; NF 族混進 L2; sim-apply
DONE: registry asof=D family∈A ≥13; #14 誠實; 帳 EXECUTED
```

建議清單（fv 已在）：

| D | fv | registry A-pack | 重跑價值 |
|---|---|---|---|
| **2026-08-12** | 37／27946 | **已有** 13 列／8 族 | **不要重跑**（本窗 L2 已 EXECUTED） |
| **2026-08-11／08-10** | 有 | 已有 13／8 | 低；同尺重複 |
| **08-07** | 37／27930 | **本窗 V1 EXECUTED** 13／8 | 已補缺口 |
| **2026-07-31** | 有 | 僅 RankRidge×5 | 可當月頻 walk-forward |
| **2026-06-30** | 38／96856 | 已有 29 列／8 族 | 低（舊 prodset 錨） |

真跑 08-07 已 EXECUTED（`audits/WP-H-L2-HIST-0807-EXECUTED-20260813.md`）。其他 D 仍須另貼 `WP-H-L2-hist-go | dates=…`。

### WP-R｜殘格 0a（須點名一族）

```text
WHEN: 貼 NF-B-VECM-go-plan | asof=2026-08-12 | no-train   （或 TCN／NB／Daily*）
DO:   plan-first 0a 契約；通過才 0b 有界 EVIDENCE
DONT: 當 L2; 塗綠 0812 六族; 無尺 depth
```

---

## §5 決策卡（本視點）

| 問 | 答 |
|---|---|
| **閉環最佳下一步** | S1：候 08-13 真價 → B3→L2 |
| **可先** | 本檔協議；V0 盤點；dry-plan 歷史 D（已通）；KH `--check` |
| **可同步** | V0／披露／監看；**不要**與即將開火的 B3 搶 CPU 開 `--apply` |
| **過去 as-of 能否收特徵＋訓＋驗** | **能**；panel 已到 08-12；L2 `--date D` 即此路；**≠**假今天、**≠**全族、**≠**升格 |
| **其他模型驗証進行** | V0＋V1＠08-07 已做；下一槍＝點名殘格或另一歷史 D |
| **不要** | 假 B3；重掃 0812 NF；sim-apply；把 Daily* 塞進 L2；P6／五窗偷渡 |

```text
paste:
  S1S5-ASOF-VERIFY | hold-#1 | V0-done | hist-asof=legal | L2 --date D | no-fake-B3
  | no-re-scan-0812 | NF-pause | no-promote | residual=name-first
```

採納「對列出的歷史 D 真跑 L2」請另貼，例如：

```text
WP-H-L2-hist-go | dates=2026-08-07 | skip-sync | no-promote | yield-to-B3
```

*完。[I] · self-reported。*
