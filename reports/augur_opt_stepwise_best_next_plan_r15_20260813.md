---
title: augur 優化——逐步執行最佳下一步計畫書 r15（市場主軸）
status: final
series: optimization_plan
round: r15
role: 市場／預測／凍結／結構**長板**（開工順序以全專案逐步執行 SSOT 為準）
parent_exec: reports/augur_opt_stepwise_all_problems_r15_20260813.md
date: 2026-08-13
viewpoint: 2026-08-13T11:49+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r15_20260813.md
  - reports/augur_project_charter_plain_zh_r15_20260813.md
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
supersedes_as_exec_nav:
  - reports/augur_opt_stepwise_best_next_plan_r14_20260811.md
archive_tip: archive-20260813-b3-0812-kh-a2l3-nf0812
kh_nav_external: reports/augur_kh_opt_stepwise_best_next_plan_20260813.md
kh_split: audits/KH-SPLIT-FROM-MARKET-AXIS-ADOPTED-20260812.md
self_reported: true
---

# augur 優化——逐步執行最佳下一步計畫書 r15（2026-08-13 · 市場主軸）

> **一句**：本檔＝市場長板（殼指令／Phase 細節）。  
> **後續優化開工**＝`reports/augur_opt_stepwise_all_problems_r15_20260813.md`。  
> **KH 外置長板**：`reports/augur_kh_opt_stepwise_best_next_plan_20260813.md`——**不**因 tip WAIT 決定 KH 開工。  
> **位階**：[I]；不創 [N]；不解凍；不 sim-apply；不默升格；**勿重掃假綠**。  
> **LIVE（親查 2026-08-13 11:49）**：tip／fv／PriceAdj＝**08-12**；H20＝**dead**、H60＝**thin**；A2B3 ARMED 候 **≥08-13**。

---

## §0 怎麼用這份計畫書（市場協議）

```text
每次要開工／回答「市場下一步」：
  1) 打開本檔 §1 → 找狀態≠🟢 的市場列
  2) 取最佳下一步；缺 GO → AskQuestion
  3) 做完 → audit → 改本檔狀態
  4) KH 問題 → 轉 KH 選刀專檔（本檔不編排）
```

**Hard doors（市場）**：

```text
FZ/GATE-keep | hold-#1 | skip-sync-B | no-fake-B3 | NF-pause
| no-SIM-apply | no-cron-B3 | 誠實 econ | 勿重掃假綠 | no-promote 默認
```

| 已授重用（勿重問） | 來源 |
|---|---|
| 日更 B3＠D · `20,60` | standing＋`run_daily_asof_predict.sh` |
| B3＠08-12 EXECUTED | `OPS-B3-20260812-EXECUTED` |
| L2 ALL-RANK＠08-12 no-promote | `RETRAIN-ASOF-0812-ALL-RANK-EXECUTED` |
| A→B3 候 **D=08-13** | `OPS-B3-A2B3-ARMED-20260813`（watcher 230370） |
| NF＠0812 旁刀收口 | `NF-0812-CLOSEOUT-ACK`；殘格須點名 |
| KH 分軌 | `KH-SPLIT-FROM-MARKET-AXIS-ADOPTED` |

---

## §1 開問題板（市場 · 結構 · 凍結）

| # | 問題（對應債） | 最佳下一步 | 可先／∥？ | 狀態 |
|---|---|---|---|---|
| **1** | 日更 tip≥**08-13**（R15-01） | 候 `PriceAdj≥08-13` → B3 `--date 2026-08-13 --horizons 20,60` → L2 `--apply`；**08-12 已 EXECUTED** | **市場主軸**；∥ #2 | 🟡 **WAIT 08-13**（08-12🟢） |
| **2** | econ／dgate（R15-02） | **不修綠**；披露＠08-12：H20=dead／H60=thin | **∥** | 🟡 |
| **3** | graph tip 邊 | — | — | 🟢 |
| **4** | H82 ghost | — | — | 🟢 |
| **5** | r15 文檔地盤 | 本輪落地 | — | 🟢 本檔 |
| **6** | 08-13 ARCHIVE | tag 已 push；假 decline 閘尚未入倉 | ∥文件 | 🟡 閘未 commit |
| **7** | 圖提拔熱路徑（R15-05） | 另高門檻 `VERIFY-graph-cand-go` | 延後 | 🔴 提拔；旁路🟢 |
| **8** | C1／CYCLE（市場側） | 不因 K10 開工；市場板不編 KH 特徵 | — | 🟢 隔離見 KH |
| **9** | P6／長窗（R15-04） | 對帳 08-12 artifact；擴長窗另 plan＋GO | **可先**（市場 WAIT） | 🟡 |
| **10** | M／β5／NF（R15-07／09） | 輕監；**禁默開新族**；0812 六族已 EVIDENCE 勿重掃 | **∥監看** | ❄ |
| **11** | Dividend／dim | 另 auth | 旁車道 | ❄ |
| **12** | sim apply | **禁** | — | ❄／禁 |
| **13** | 循環依賴 | explore-only 文件 | 低優先∥ | 🔴 |
| **14** | scripts 冗餘 | #29 另計畫 | 延後 | 🔴 |
| **15** | 10–14 治權日曆（R15-10） | 10 月初複核清單；**不假關** | 排程 | 🟡 |
| **16** | standing 五窗永久化（R15-03） | 雙明示＋改殼 | 延後 | ❄ |
| **17** | dgate evaluate | 另明示 GO；禁塗綠 | 延後 | 🟡 |
| **18** | 其他模型族 | **勿重掃假綠**；殘格見 NF residual card | ∥文件 | 🟢 STOP／EVIDENCE 多 |
| **19** | model_family_chk | — | — | 🟢 |
| **20** | 升格另軌（R15-06） | 文件／`PROMOTE-TRACK`；禁默 SERVE-SWAP | 文件∥ | ❄ |
| **21** | Wave-A／挑戰收官 | — | — | 🟢 |
| **22** | RankRidge tip 鏈 | 08-12 ALL-RANK 已重訓＋repredict；換殼敘事另句 | — | 🟢 |
| **23** | tip＋N 實現報酬（R15-14） | 等價蓋過 tip＋N 日 | 延後 | 🔴 |
| **24** | 相對機率看板 | 雙窗已修；守「數字≠報酬％」 | — | 🟢 |
| **K** | KH 全線 | **外置**→ KH 20260813 專檔 | **非本檔** | 📦 遷出 |

---

## §2 決策速查：現在該做什麼？

| 若你問 | 答案（本視點 **2026-08-13 11:49**） |
|---|---|
| **最佳下一步（本檔＝市場）** | **#1**：讓 ARMED watcher 跑；`PriceAdj≥2026-08-13` → B3 `20,60` → L2 |
| **KH 下一步** | **本檔不答** → KH 20260813 專檔 |
| **現在可同步（市場）** | **#2** 披露；**#10** 凍結輕監；**#9** 文件對帳 |
| **不要做** | 假 B3、sim-apply、換冠、默改五窗殼、重掃 STOP／0812 EVIDENCE；**勿**用 tip 擋 KH |

```text
paste（市場主軸）:
  hold-#1 | WAIT PriceAdj≥2026-08-13 | B3 horizons=20,60 | then-L2
  | prior B3@08-12 EXECUTED | A2B3-ARMED | FZ/GATE-keep | no-fake-B3 | no-SIM-apply
  | NF-pause | KH=external-ssot
```

---

## §3 逐步執行序列（Phase）

### Phase 0｜✅ DONE

| 項 | 結果 |
|---|---|
| 人話／理解 r14；KH 分軌 | 落地 |
| B3＠08-11／08-12 | EXECUTED；#14 誠實 |
| L2 ALL-RANK＠08-12 | EXECUTED；no-promote |
| NF＠0812 六族有界 | EVIDENCE＋closeout-ack |
| ARCHIVE 08-13 | tag 在遠端 |
| A2B3 arm＠08-13 | **ARMED**（本 Phase 1） |

### Phase 1｜🟡 IN FLIGHT（主軸｜市場）

| 步 | 觸發 | 動作 | 驗收 |
|---|---|---|---|
| **1a** | `PriceAdj ≥ 2026-08-12` | B3＠08-12 `20,60` | ✅ EXECUTED |
| **1b** | L1 RC=0＠08-12 | L2 ALL-RANK `--apply` | ✅ EXECUTED；no-promote |
| **1c** | `PriceAdj ≥ 2026-08-13` | B3＠08-13 `20,60` → L2 | 🟡 WAIT（價頂仍 08-12；watcher 在） |
| **1d** | 08-13 23:50 仍無價 | TIMEOUT；不假跑 | 🟡 未到點 |
| **1e** | 之後每新 D | standing A→B3→L2 | tip=D；誠實 #14 |

**∥ Phase 1（僅市場列）**：

| 步 | 對齊 # | 動作摘要 | 驗收 |
|---|---|---|---|
| 1p | #2 | 日更後披露 dead／thin；禁塗 dgate | 帳或對話無「已綠」 |
| 1q | #10 | 不開 NF／M／β；僅文件監看 | 無新族 train 默啟 |

### Phase 2｜Steward 選一（市場／結構；不搶 #1）

| 順位 | 刀 | 開法 | 驗收 |
|---|---|---|---|
| 2.1 | P6／長窗 | 另 plan＋GO | artifact 對齊 tip |
| 2.2 | 升格門檻文件 | `PROMOTE-TRACK-doc` | 文件 [I]；仍 no-promote |
| 2.3 | standing 五窗殼 | **雙明示**＋改預設 | standing≠口頭五窗 |
| 2.4 | 圖提拔 | `VERIFY-graph-cand-go` | 高門檻 evidence |
| 2.5 | STRUCT／scripts | explore | 報告；慢改碼 |
| 2.6 | NF 殘格 | **點名卡**才 plan | 禁同尺重掃 0812 |

### Phase 3｜延後／禁（本檔不開刀）

解凍 M／β5；撤 NF-pause（無點名）；cron B3；sim `--apply`；Dividend 全量；假關 dgate；同尺重掃 STOP／EVIDENCE；無證據 SERVE-SWAP；无價假跑 tip。

---

## §4 軌快照

| 軌 | 狀態 | 本輪動作 |
|---|---|---|
| A 日頻 | 🟡 WAIT tip≥08-13 | Phase 1c |
| B 閉環／圖 | 旁路🟢／提拔🔴 | 延後 2.4 |
| C 結構 | 🔴 | 延後 2.5 |
| D 日曆 | 🟡 10–14 | #15 |
| E 凍結 | ❄ | #10–12 |
| F 模型 | 冠軍穩／STOP＋EVIDENCE 多 | 勿重掃；慎 swap |
| G 文件 | 🟢 r15＝**市場**選刀 | KH 外置專檔 |
| H 知識 | 📦 **已遷出** | `augur_kh_opt_stepwise_best_next_plan_20260813.md` |

---

## §5 工作包卡片（開跑複製）

### WP-A｜市場主軸日更（#1）

```text
WHEN: PriceAdj≥2026-08-13
DO:   bash scripts/run_daily_asof_predict.sh --date 2026-08-13 --horizons 20,60
      # L1 RC=0 後：
      bash scripts/run_daily_retrain_l2_all_rank.sh --date 2026-08-13 --apply
DONT: sync-B 偷跑; 假 B3; sim-apply; 默五窗; SERVE-SWAP; promote
DONE: RC=0 + tip=D + EXECUTED/FIRED + #14 誠實 + L2 no-promote
```

（ARMED watcher 已按上列順序；人工只在 TIMEOUT 或 watcher 死後介入。）

### WP-F｜凍結輕監（#10 · ∥）

```text
WHEN: 任意
DO:   確認無默訓新族; 0812 六族不重掃
DONT: NF-*-go 無 Steward 點名; 重掃假綠
DONE: 無違規 commit/job
```

---

## §6 與深化理解債表對照

| 理解 R15-* | 本板 # | 處置 |
|---|---|---|
| R15-01 日更 | #1 | 市場主軸 WAIT |
| R15-02 econ | #2 | ∥ 不修綠 |
| R15-03 五窗殼 | #16 | ❄ |
| R15-04 P6 | #9 | 可先／另 GO |
| R15-05 圖提拔 | #7 | 延後 |
| R15-06 升格 | #20 | ❄ |
| R15-07 NF | #10／2.6 | ❄＋點名卡 |
| R15-08 scripts | #14 | 延後 |
| R15-09 M／sim… | #10–12 | ❄ |
| R15-10 日曆 | #15 | 排程 |
| R15-11…13／15…19 知識 | **K 外置** | KH 專檔 |
| R15-14 tip+N | #23 | 延後 |
| R15-18 假 decline 入倉 | #6 | ∥ 不擋 #1 |

---

## §7 驗收（本計畫書本身）

- [x] 市場／凍結／結構開問題入板  
- [x] KH **遷出**本檔主編排  
- [x] Phase＋WP-A／F 可執行  
- [x] 聲明：本檔＝**市場**選刀 SSOT；KH＝外置專檔  

---

## §8 何時寫 r16（刷新觸發）

1. tip≥**08-13** 日更閉合（FIRED／EXECUTED 或 TIMEOUT）；或  
2. Steward 雙明示改 standing／升格／解凍。

（KH 收口改寫 **KH 選刀專檔**，不強制觸發本 r16。）

---

## §9 結語

> **市場：先對 r15 → 不假跑 tip。KH：先對 kh_opt_stepwise_20260813 → 與本檔無關。**

配套：理解 r15 · 人話 r15 · KH 選刀 20260813 · 分軌帳 `KH-SPLIT-FROM-MARKET-AXIS-ADOPTED`。

*完。[I] · r15＝市場選刀 SSOT（KH 已外置）。*
