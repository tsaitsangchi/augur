---
title: augur 優化——逐步執行最佳下一步計畫書 r14（刷新加強）
status: final
series: optimization_plan
round: r14
role: **後續優化執行 SSOT**（全域開問題＋最佳下一步＋可先／∥；依 r14 深化理解）
date: 2026-08-11
viewpoint: 2026-08-12T11:00+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r14_20260811.md
  - reports/augur_project_charter_plain_zh_r14_20260811.md
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
supersedes_as_exec_nav:
  - reports/augur_opt_stepwise_best_next_plan_r13_20260808.md
archive_tip: archive-20260812-b3-0811-asr-doc-r14
board_refresh: 2026-08-12T11:00+08:00
refresh_note: KH 已全部退出本檔市場主軸編排→見 kh_opt_stepwise_20260812；本檔只答 tip／B3／凍結／結構
kh_nav_external: reports/augur_kh_opt_stepwise_best_next_plan_20260812.md
kh_split: audits/KH-SPLIT-FROM-MARKET-AXIS-ADOPTED-20260812.md
self_reported: true
---

# augur 優化——逐步執行最佳下一步計畫書 r14（2026-08-11 · 市場主軸）

> **一句**：本檔＝**市場／預測／凍結／結構**選刀 SSOT。  
> **KH 全部外置**：知識閉環選刀改讀 `reports/augur_kh_opt_stepwise_best_next_plan_20260812.md`（`KH-SPLIT-FROM-MARKET-AXIS-ADOPTED`）——**不**再當本檔主軸附屬、**不**因 tip WAIT／「讓 B3」決定 KH 開工。  
> **位階**：[I]；不創 [N]；不解凍；不 sim-apply；不默升格；**勿重掃假綠**。  
> **讀序（市場）**：人話 r14 → 理解 r14 → **本檔** → S1→S5 → standing／audit。  
> **讀序（KH）**：KH readout → **KH 選刀專檔** → ingest-B／S*（**勿**回本檔找 KH 刀）。  
> **LIVE（親查 2026-08-12）**：tip／fv＝**08-11**；H20＝**dead**、H60＝**thin**；PriceAdj＝**08-11** → **市場**下一刀候 **≥08-12**。

---

## §0 怎麼用這份計畫書（市場協議）

```text
每次要開工／回答「市場下一步」：
  1) 打開本檔 §1 → 找狀態≠🟢 的市場列
  2) 取最佳下一步；缺 GO → AskQuestion
  3) 做完 → audit → 改本檔狀態
  4) KH 問題 → 轉 KH 選刀專檔（本檔不編排）
```

| 標記 | 意思 |
|---|---|
| **市場主軸** | tip／B3 本檔唯一主軸 |
| **∥** | 可與**市場其他列**同步（不改 tip／不升格／不假 B3） |
| **可先** | 市場主軸 WAIT 時的市場閒時刀 |
| **延後／❄／禁** | 同前 |
| **外置 KH** | 不在本板開工；見 `kh_nav_external` |

**Hard doors（市場）**：

```text
FZ/GATE-keep | hold-#1 | skip-sync-B | no-fake-B3 | NF-pause
| no-SIM-apply | no-cron-B3 | 誠實 econ | 勿重掃假綠 | no-promote 默認
```

| 已授重用（勿重問） | 來源 |
|---|---|
| 日更 B3＠D · `20,60` | standing＋`run_daily_asof_predict.sh` |
| VERIFY-B3＠08-10 | `VERIFY-B3-20260810-EXECUTED` |
| A→B3 候 **D=08-11** | `OPS-B3-A2B3-ARMED-20260811` |
| tip 五窗一槍＠08-10 | VERIFY（**≠**改 standing 預設殼） |
| KH 分軌（不在本檔編排） | `KH-SPLIT-FROM-MARKET-AXIS-ADOPTED` · `kh_opt_stepwise_20260812` |

---

## §1 開問題板（市場 · 結構 · 凍結）

> 對齊理解 r14 債表之**市場／結構**項。原 #24–29 KH 列**遷出**→ KH 選刀專檔。

| # | 問題（對應債） | 最佳下一步 | 可先／∥？ | 狀態 |
|---|---|---|---|---|
| **1** | 日更 tip≥**08-12**（R14-01） | 候 `PriceAdj≥08-12` → B3 `--date 2026-08-12 --horizons 20,60`；**08-11 已 EXECUTED** | **市場主軸**；∥ #2 | 🟡 **WAIT 08-12**（08-11🟢） |
| **2** | econ／dgate（R14-02） | **不修綠**；披露＠08-11：H20=dead／H60=thin | **∥** | 🟡 |
| **3** | graph tip 邊 | — | — | 🟢 |
| **4** | H82 ghost | — | — | 🟢 |
| **5** | r14 文檔地盤 | — | — | 🟢 |
| **6** | 08-11 ARCHIVE | — | — | 🟢 |
| **7** | 圖提拔熱路徑（R14-05） | 另高門檻 `VERIFY-graph-cand-go` | 延後 | 🔴 提拔；旁路🟢 |
| **8** | C1／CYCLE（市場側） | — | — | 🟢 |
| **9** | P6／長窗（R14-04） | 對帳 08-10 artifact；擴長窗另 plan＋GO | **可先**（市場 WAIT） | 🟡 |
| **10** | M／β5／NF（R14-07／09） | 輕監；**禁默開新族** | **∥監看** | ❄ |
| **11** | Dividend／dim | 另 auth | 旁車道 | ❄ |
| **12** | sim apply | **禁** | — | ❄／禁 |
| **13** | 循環依賴 | explore-only 文件 | 低優先∥ | 🔴 |
| **14** | scripts 冗餘 | #29 另計畫 | 延後 | 🔴 |
| **15** | 10–14 治權日曆（R14-10） | 10 月初複核清單 | 排程 | 🟡 |
| **16** | standing 五窗永久化（R14-03） | 雙明示＋改殼 | 延後 | ❄ |
| **17** | dgate evaluate | 另明示 GO；禁塗綠 | 延後 | 🟡 |
| **18** | 其他模型族 | **勿重掃假綠**；新族另契約 | ∥文件 | 🟢 STOP 多 |
| **19** | model_family_chk | — | — | 🟢 |
| **20** | 升格另軌（R14-06） | 文件／`PROMOTE-TRACK`；禁默 SERVE-SWAP | 文件∥ | ❄ |
| **21** | Wave-A／挑戰收官 | — | — | 🟢 |
| **22** | RankRidge tip 鏈 | 08-11 ALL-RANK 已重訓＋repredict；換殼敘事另句 | — | 🟢 |
| **23** | tip＋N 實現報酬（R14-14） | 等價蓋過 tip＋N 日 | 延後 | 🔴 |
| **K** | （原 #24–29 等）KH 全線 | **外置**→ `reports/augur_kh_opt_stepwise_best_next_plan_20260812.md` | **非本檔** | 📦 遷出 |

---

## §2 決策速查：現在該做什麼？

| 若你問 | 答案（本視點 **2026-08-12**） |
|---|---|
| **最佳下一步（本檔＝市場）** | **#1**：候 `PriceAdj≥2026-08-12` → B3 `20,60` |
| **KH 下一步** | **本檔不答** → 開 KH 選刀專檔／`kh_ingest_trigger --check` |
| **現在可同步（市場）** | **#2** 披露；**#10** 凍結輕監；**#9** 文件對帳 |
| **不要做** | 假 B3、sim-apply、換冠、默改五窗殼、重掃 STOP；**勿**用 tip 擋 KH、**勿**把 KH 進度當 B3 前提 |

```text
paste（市場主軸）:
  hold-#1 | WAIT PriceAdj≥2026-08-12 | B3 horizons=20,60
  | prior B3@08-11 EXECUTED | FZ/GATE-keep | no-fake-B3 | no-SIM-apply
  | KH=external-ssot
```

---

## §3 逐步執行序列（Phase）

### Phase 0｜✅ DONE

| 項 | 結果 |
|---|---|
| 人話／理解／本導航 r14 | 落地並本輪刷新加強 |
| B3＠08-10 VERIFY | PASS；#14 誠實 |
| PPT／PDF-C／AVI-ASR＋readout 私有 | CODE／EXECUTED |
| ARCHIVE 08-11 | tag 在 |
| A2B3 arm＠08-11 | ARMED → TIMEOUT → **08-12 catch-up EXECUTED**（`OPS-B3-20260811-EXECUTED`） |

### Phase 1｜🟡 IN FLIGHT（主軸｜市場）

| 步 | 觸發 | 動作 | 驗收 |
|---|---|---|---|
| **1a** | `PriceAdj ≥ 2026-08-11` | B3＠08-11 `20,60` | ✅ **EXECUTED 2026-08-12** |
| **1b** | 08-11 23:50 仍無價 | TIMEOUT；不假跑 | ✅ TIMEOUT 帳在 |
| **1c** | `PriceAdj ≥ 2026-08-12` | B3＠08-12 `20,60` | 🟡 WAIT（價頂仍 08-11） |
| **1d** | 之後每新 D | standing A→B3 | tip=D；誠實 #14 |

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

> KH 刀（Writer／smoke／ingest／AUTO-LIFT／KH8）→ **KH 選刀專檔**，不在本 Phase。

### Phase 3｜延後／禁（本檔不開刀）

解凍 M／β5；撤 NF-pause；cron B3；sim `--apply`；Dividend 全量；假關 dgate；同尺重掃 STOP；無證據 SERVE-SWAP；无價假跑 tip。

---

## §4 軌快照

| 軌 | 狀態 | 本輪動作 |
|---|---|---|
| A 日頻 | 🟡 WAIT tip≥08-12 | Phase 1c（市場主軸） |
| B 閉環／圖 | 旁路🟢／提拔🔴 | 延後 2.4 |
| C 結構 | 🔴 | 延後 2.5 |
| D 日曆 | 🟡 10–14 | #15 |
| E 凍結 | ❄ | #10–12 |
| F 模型 | 冠軍穩／STOP 多 | 勿重掃；慎 swap |
| G 文件 | 🟢 r14＝**市場**選刀 | KH 外置專檔 |
| H 知識 | 📦 **已遷出** | `augur_kh_opt_stepwise_best_next_plan_20260812.md` |

---

## §5 工作包卡片（開跑複製）

### WP-A｜市場主軸日更（#1）

```text
WHEN: PriceAdj≥2026-08-12
DO:   bash scripts/run_daily_asof_predict.sh --date 2026-08-12 --horizons 20,60
DONT: sync-B 偷跑; 假 B3; sim-apply; 默五窗; SERVE-SWAP
DONE: RC=0 + tip=D + EXECUTED/FIRED audit + #14 誠實
```

### WP-F｜凍結輕監（#10 · ∥）

```text
WHEN: 任意
DO:   確認無默訓新族; 文件列 STOP
DONT: NF-*-go 無 Steward; 重掃假綠
DONE: 無違規 commit/job
```

> ~~WP-K~~ 已廢於本檔 → 見 KH 選刀專檔。

---

## §6 與深化理解債表對照

| 理解 R14-* | 本板 # | 處置 |
|---|---|---|
| R14-01 日更 | #1 | 市場主軸 WAIT |
| R14-02 econ | #2 | ∥ 不修綠 |
| R14-03 五窗殼 | #16 | ❄ |
| R14-04 P6 | #9 | 可先／另 GO |
| R14-05 圖提拔 | #7 | 延後 |
| R14-06 升格 | #20 | ❄ |
| R14-07 NF | #10 | ❄ |
| R14-08 scripts | #14 | 延後 |
| R14-09 M／sim… | #10–12 | ❄ |
| R14-10 日曆 | #15 | 排程 |
| R14-11…13 知識 | **K 外置** | KH 選刀專檔 |
| R14-14 tip+N | #23 | 延後 |

---

## §7 驗收（本計畫書本身）

- [x] 市場／凍結／結構開問題入板  
- [x] KH **遷出**本檔主編排（`KH-SPLIT-FROM-MARKET-AXIS-ADOPTED`）  
- [x] Phase＋WP-A／F 可執行  
- [x] 聲明：本檔＝**市場**選刀 SSOT；KH＝外置專檔  

---

## §8 何時寫 r15（刷新觸發）

1. tip≥**08-12** 日更閉合（FIRED／EXECUTED 或 TIMEOUT）；或  
2. Steward 雙明示改 standing／升格／解凍。

（KH 收口改寫 **KH 選刀專檔**／其 audit，不強制觸發本 r15。）

---

## §9 結語

> **市場：先對 r14 → 不假跑 tip。KH：先對 kh_opt_stepwise → 與本檔無關。**

配套：

- 理解：`reports/augur_deep_understanding_and_opt_plan_r14_20260811.md`  
- 人話：`reports/augur_project_charter_plain_zh_r14_20260811.md`  
- **KH 選刀**：`reports/augur_kh_opt_stepwise_best_next_plan_20260812.md`  
- 分軌帳：`audits/KH-SPLIT-FROM-MARKET-AXIS-ADOPTED-20260812.md`  

*完。[I] · r14＝市場選刀 SSOT（KH 已外置）。*
