---
title: S4／S5 其他模型驗証矩陣｜plan-first（∥ #1 候 A）
status: adopted
series: s4_s5_verify
open_problem: "其他模型驗証"
date: 2026-08-06
viewpoint: 2026-08-06T16:37+08:00
adopted: audits/S4-OTHER-VERIFY-MATRIX-ADOPTED-20260806.md
layer: "[I]"
role: 把「再進行其他模型驗証」收成可選刀矩陣；零新訓·零解 NF·不搶 B3
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
s4_families: reports/augur_s4_market_model_families_opt_plan_20260804.md
tried_list: audits/S4-MODELS-TRIED-LIST-20260804.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
nav: reports/augur_opt_stepwise_best_next_plan_r10_20260806.md
live_asof_board: reports/augur_s1s5_asof_verify_best_next_r19_20260819.md
inherits_boundaries:
  - FZ/GATE-keep · skip-sync-B · no-SIM-apply · no-cron-B3
  - NF-pause（不開新族 adapter／train）
  - hold #1 A→B3＠08-06（價未到不假跑）
  - 禁假確立級；#14 ≠ 裸 IC；sim ≠ 預測尺
self_reported: true
---

# S4／S5 其他模型驗証矩陣 · plan-first · 2026-08-06

> **一句**：taxonomy **Wave A–G 普查已收官**；「其他模型驗証」≠再掃一輪假綠，而是依矩陣選 **V1 重覆驗既有族／V3 S5↔S4 回饋／V2 缺 adapter 排隊**——**開新族須先撤 NF-pause**。  
> **性質**：[I] plan-first；本檔 **零新訓、零寫庫、零解凍**。  
> **LIVE**：PriceAdj 頂 **08-05**；#1 watcher 候 **08-06**；`evaluated_pass=0`。

---

## §0 護欄

```text
S4-OTHER-VERIFY-matrix-plan | FZ/GATE-keep | NF-pause | hold-#1 | skip-sync-B | no-SIM-apply
# ≠ S4-WAVE-*-reopen 默授 train；≠ 撤 NF；≠ 假 SKIP=pass
```

| 可（本檔） | 不可 |
|---|---|
| 寫矩陣／優先序／paste-ready | 開 XGB／LSTM／GNN／RL 新訓 |
| 點名既有 5 架構臂如何重覆驗 | 把 Wave B–G SKIP 改稱已驗証通過 |
| 排 V3 OOS 回饋刀（另 GO） | 與 B3 同 slot 搶 CPU／API |

---

## §1 一句現況（相對「還要驗其他模型」）

| 已完成 | 誠實缺口 |
|---|---|
| Wave **A–G EXECUTED**（普查＋大量誠實 SKIP） | 生產熱路徑仍≈ **Wave A 三臂**（RankRidge 主） |
| 已試架構 **5**（見 TRIED-LIST） | SKIP 等待 adapter：**A8＋B5＋C5＋D3＋E2＋F3＋G8…** |
| C2 迴路已授（S4↔S5） | 回饋弧重跑／新 asof **另句**；非一鍵 |
| NF-pause＠08-05 | **禁**默開下一新族 |

→ 「其他模型」若指 **尚未有 adapter 的族**：先做 **V2 排隊＋解 pause GO**，不是假訓。  
→ 若指 **已有產物的多模型重覆驗**：走 **V1／V3**（#11／#14／OOS）。

---

## §2 驗証矩陣（選刀）

| 軌 | 名稱 | 客體 | 驗收尺 | ∥ #1？ | 須 GO |
|---|---|---|---|---|---|
| **V0** | 盤點刷新 | TRIED-LIST↔庫內 artifact／prodset | 表一致；無幻造 id | ✅ 唯讀 | 本檔即 V0 敘事；可另 probe |
| **V1** | 既有族重覆驗 | RankRidge／RankGBDT／M1／Direction 三臂 | #11 ≥3 seed（隨機臂）；#14 分布；禁單 seed 勝 | ⚠️ CPU 重→**A 後或閒時** | H60＋**H20 EXECUTED**（`S4-V1-REVERIFY-EXECUTED-20260806`／`…-H20-EXECUTED-20260807`） |
| **V2** | 缺 adapter 排隊 | Wave A SKIP 八族→B→C… | 誠實 missing 清單＋優先 1～3 族 | ✅ 文件 | **ADOPTED** `audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md`（零開訓） |
| **V3** | S5↔S4 回饋驗 | 既有 predict／OOS → 重選 horizon／族 | OOS 漲跌比 folds；回寫優先帳；禁假 pass | ⚠️ 讓 B3 | `LOOP-S5-TO-S4-OPT-run` → **EXECUTED** `audits/LOOP-S5-TO-S4-OPT-EXECUTED-20260807.md`／`S4-REOPT-BACKLOG-20260807.md` |
| **V4** | 新族解凍 | ARIMA／VAR／Seq／Graph 股邊 | adapter＋多 seed＋#14／SKIP | ❌ 與 pause 衝突 | `NF-E-go-plan`／`S4-ARIMA-P1-go` 等 |
| **V5** | S5-only 尺 | 不新訓；既有 pp／econ | direction／漲跌比 OOS；dgate 唯讀 | ✅ 輕量可∥ | `S5-OOS-VERIFY-go` → **EXECUTED** `audits/S5-OOS-VERIFY-EXECUTED-20260806.md` |

**候 A 期間建議**：V0＋**V5 ✅ 本窗已跑**；**V1／V3 重跑排 A 後**；**V2／V4 維持 pause**。

---

## §3 既有族（V1 客體·摘要）

| 族 | 角色 | 重覆驗重點 |
|---|---|---|
| RankRidge | 生產 train／熱路徑 | H20／60（＋可選 40／120）多 seed；#14 vs 基準 |
| RankGBDT | 已有 artifact | 三 seed 已有；重跑 #14 分布 |
| M1_gbdt | #14 對照 | 禁單 seed；報 min／med／max |
| DailyGBDT_cal／MktLogit／DirStackM | direction | hit／brier；≠確立級 |

as-of 錨：歷史窗多為 **2026-06-30** prodset；滾到新 D 須 **明示 asof**（勿默用 08-06 未 READY 價）。

---

## §4 SKIP 池（V2·勿假綠）

| Wave | 代表 | 狀態 |
|---|---|---|
| A | XGB／Cat／RF／LTR／SVM／KNN／NB／淺 MLP | missing adapter |
| B | ARIMA／GARCH／VAR／Kalman／協整 | SKIP／n/a-sim |
| C–D | RNN…／Transformer TS | 缺 seq panel／adapter |
| E | GCN／GAT 股圖 | 契約≠KH `knowledge_edge`；消費見 GRAPH-CONSUME |
| F | RL | defer；無下單 |
| G | 真 ensemble／NLP／GP… | SKIP／partial 文件化 |

---

## §5 與開問題板銜接（刷新）

| # | 最佳下一步 | ∥？ | 與本矩陣 |
|---|---|---|---|
| **1** | 候 A≥08-06 → B3 | 主軸 | **本檔不搶** |
| **2** | dgate 不修綠 | ∥ | V5 讀 status≠改門 |
| **7** | GRAPH G2 stub 另 GO | ∥文件 | 喂 V2／V4 圖族前置 |
| **8** | CYCLE 讓 #1 | 讓位 | C1≠S4 驗証 |
| **9** | P6 下一 FREEZE 閒時 | 閒時 | 校準≠新模型族 |
| **10** | M／β5／NF 輕監 | ∥ | NF-pause **疊加** |
| **本刀** | V0 矩陣 ✅；下一選 V5 或等 A 後 V1 | — | — |

```text
可∥:  #1 watcher  ∥  本矩陣文件  ∥  V5（輕·另 GO）  ∥  #7 文件  ∥  #10
串列:  V1/V3 重跑 → A 後或明示閒時 slot
       V4 新族 → 先撤 NF-pause
```

---

## §6 Paste-ready

採納本矩陣：

```text
S4-OTHER-VERIFY-matrix-adopt | FZ/GATE-keep | NF-pause | hold-#1
```

輕量 S5 尺（∥候 A）：

```text
S5-OOS-VERIFY-go | FZ/GATE-keep | read-mostly | no-new-train | hold-#1
```

A 後既有族重覆驗：

```text
S4-V1-REVERIFY-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | asof=<READY_D>
```

回饋弧重跑：

```text
LOOP-S5-TO-S4-OPT-run | FZ/GATE-keep | after-A | no-auto-APPLY
```

解 pause（另決策）：

```text
NF-E-go-plan
# 或 S4-ARIMA-P1-go | GATE-keep | skip-sync | no-SIM-apply
```

---

## §7 驗收（本計畫書）

1. 能復述：Wave A–G＝普查收官≠全族已訓通過。  
2. 「其他驗証」五軌 V0–V5 可指稱。  
3. NF-pause／#1 hold 仍在。  
4. 未開訓、未改 dgate、未假 B3。

*完。[I] plan_first。*
