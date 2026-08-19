---
title: augur 優化——逐步執行最佳下一步計畫書 r13
status: final
series: optimization_plan
round: r13
role: 後續優化執行導覽 SSOT（全域開問題＋可先／∥；依 r13 地基）
date: 2026-08-08
viewpoint: 2026-08-08T19:50+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r13_20260808.md
  - reports/augur_project_charter_plain_zh_r13_20260808.md
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
supersedes_as_exec_nav:
  - reports/augur_opt_stepwise_best_next_plan_r12_20260807.md
archive_tip: archive-20260807-r11-nfa-verify-charter
board_refresh: 2026-08-08T19:50+08:00
self_reported: true
---

# augur 優化——逐步執行最佳下一步計畫書 r13（2026-08-08）

> **一句**：在 **r13 深化理解**上，把**目前全部開問題**收成可逐步執行的「最佳下一步／可先／可同步」板。  
> **Hard doors**：`FZ/GATE-keep` · `hold-#1` · `NF-pause` · `no-SIM-apply` · `no-fake-B3` · 誠實 econ · **勿重掃假綠** · no-promote 默認。  
> **LIVE**：tip＝**2026-08-07**（五 H 已掛）；價頂＝**08-07**；A2B3 **ARMED＠08-10** horizons=**20,60**；serve＝RankRidge＠**07-31**；H20 **dead**。

---

## §0 護欄與讀序

```text
讀序: 人話 r13 → 理解 r13 → 本檔 r13 選刀 → S1→S5 SSOT → 最近 audit/standing → #1 watcher
硬邊界: FZ/GATE-keep | skip-sync-B | no-SIM-apply | NF-pause | hold-#1
         | no-cron-B3 | 誠實 econ | 勿重掃假綠 | no-promote 默認
```

| 已授重用 | 來源 |
|---|---|
| 日更 B3＠D | standing＋`run_daily_asof_predict.sh` |
| A→B3＠**08-10** ARMED | `OPS-B3-A2B3-ARMED-20260810` · `/tmp/asof-ping-0810/` |
| tip 五窗一槍 | `B3-HORIZONS-FIVE`＋`SERVE-FIVE-H`＠08-07（**≠**改 standing 預設） |

---

## §1 全域開問題板（最佳下一步 · 可先／∥）

| # | 問題 | 最佳下一步 | 可先／∥？ | 狀態 |
|---|---|---|---|---|
| **1** | 日更＠**2026-08-10** | 候價→自動 B3 `20,60` | **主軸**；∥ #2／#10 | 🟡 ARMED／WAIT |
| **2** | econ／dgate 誠實形 | 不修綠；日更照常 | **∥** | 🟡 H20 dead |
| **3** | graph asof／tip 邊 | — | — | 🟢 rebuild＠08-07 |
| **4** | H82 ghost | — | — | 🟢 |
| **5** | r11–r13 文檔地盤 | — | — | 🟢 本輪刷新 |
| **6** | 08-07 封存基線 | — | — | 🟢 |
| **7** | 圖消費／提拔 | 熱路徑／VERIFY 另高門檻 GO | 延後 | 🟢 旁路；提拔🔴 |
| **8** | C1 CYCLE | — | — | 🟢 CYCLE-3 |
| **9** | P6＠08-07 | —／擴長窗另刀 | 閒時可先擴 | 🟢 H20／60；長窗🟡 |
| **10** | M／β5／NF | 輕監；禁默開新族 | **∥** | ❄ |
| **11** | Dividend／dim | 另 auth | 旁車道 | ❄ |
| **12** | sim apply | **禁** | — | ❄ |
| **13** | 循環依賴 | explore-only | 低優先∥ | 🔴 |
| **14** | scripts 冗餘 | #29 另計畫 | 延後 | 🔴 |
| **15** | 10–14 治權日曆 | 10 月初複核 | 排程 | 🟡 |
| **16** | standing 五窗 | 不改殼；要改須雙明示＋改預設另句 | 延後 | ❄／tip 已五窗一槍 |
| **17** | dgate evaluate | 另明示 GO | 延後 | 🟡 |
| **18** | 其他模型 | **勿重掃**；新族另契約 | ∥文件 | 🟢 多族 STOP |
| **19** | `model_family_chk` | — | — | 🟢 可登錄層關閉 |
| **20** | 升格另軌 | 僅文件／明示 promote GO | 文件∥ | ❄ |
| **21** | Wave-A 收官 | — | — | 🟢 |
| **22** | RankRidge＠0731 | — | — | 🟢 |
| **23** | tip＋N 日實現報酬研究 | 等價蓋過 tip | 延後 | 🔴 |

---

## §2 逐步執行序列

### Phase 0｜✅ DONE

r13 理解＋人話憲章＋本導航；08-08 增量收口（五窗 tip／圖／#19／hold arm）。

### Phase 1｜🟡 IN FLIGHT（主軸）

| 步 | 觸發 | 動作 | 驗收 |
|---|---|---|---|
| 1a | PriceAdj≥**08-10** | 自動 B3 `--date 2026-08-10 --horizons 20,60` | RC=0；Adv as_of=D；FIRED／EXECUTED |
| 1b | 08-10 23:50 仍無價 | TIMEOUT WAIT 帳；**不**假跑 | TIMEOUT audit |
| 1c | 之後每新 D | standing A→B3 | 同 1a |

**∥ Phase 1**：#2 誠實敘事；#10 凍結輕監。

### Phase 2｜Steward 選一（不搶 #1）

| 順位 | 刀 | paste／草案 |
|---|---|---|
| 2.1 | P6 擴 H40／82／120 | `P6-REFIT-…-longH-go`（另寫 plan） |
| 2.2 | 升格門檻文件 | `PROMOTE-TRACK-doc \| no-promote` |
| 2.3 | standing 五窗永久化 | 雙明示＋改殼（高門檻） |
| 2.4 | 圖提拔 VERIFY | `VERIFY-graph-cand-go` |
| 2.5 | STRUCT／scripts | explore／#29 |

### Phase 3｜延後（本檔不開刀）

解凍 M／β5；撤全域 NF；cron B3；sim `--apply`；Dividend 全量；假關 dgate；同尺重掃 STOP 族；無證據 SERVE 挑戰族。

---

## §3 軌快照

| 軌 | 狀態 |
|---|---|
| A 日頻 | 🟡 Phase1 armed＠08-10 |
| B 閉環／圖 | 寫庫＋G3 旁路 🟢；提拔／熱路徑 🔴 |
| C 結構 | 🔴 循環／scripts |
| D 日曆 | 🟡 10–14 |
| E 凍結 | ❄ M／β／NF／sim |
| F 模型 | RankRidge 冠；挑戰 STOP；勿重掃 |
| G 文件 | r13 🟢 |

---

## §4 Paste-ready

```text
OPT-R13-adopt | FZ/GATE-keep | skip-sync-B | no-SIM-apply | hold-#1 | nav=r13
hold-#1 | A→B3@2026-08-10 | horizons=20,60 | no-fake-B3 | NF-pause
```

閒時例：

```text
P6-LONGH-go-plan | FZ/GATE-keep | H=40,82,120 | no-serve-swap
PROMOTE-TRACK-doc | no-promote | hold-#1
```

---

## §5 採納後讀序

1. `reports/augur_project_charter_plain_zh_r13_20260808.md`  
2. `reports/augur_deep_understanding_and_opt_plan_r13_20260808.md`  
3. **本檔 r13（選刀）**  
4. S1→S5 SSOT · 最近 ARCHIVE／standing · `#1` watcher log  

r12＝史料選刀；理解細節可回 r11／INVENTORY。

---

## §6 本檔驗收

- [x] 全部開問題含最佳下一步＋可先／∥  
- [x] Phase 0–3  
- [x] 主軸 #1／勿重掃／雙明示五窗界線寫死  
- [x] paste-ready  
- [x] 不創 [N]、不開訓  

*完。[I] · self-reported。*
