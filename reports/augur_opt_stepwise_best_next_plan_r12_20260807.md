---
title: augur 優化——逐步執行最佳下一步計畫書 r12
status: final
series: optimization_plan
round: r12
role: 後續優化執行導覽 SSOT（全域開問題＋可先／∥；依 r11 地基）
date: 2026-08-07
viewpoint: 2026-08-07T14:04+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r11_20260807.md
  - reports/augur_project_charter_plain_zh_r11_20260807.md
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
supersedes_as_exec_nav:
  - reports/augur_opt_stepwise_best_next_plan_r10_20260806.md
  - reports/augur_deep_understanding_and_opt_plan_r11_20260807.md  # 選刀部：改以本檔為準；理解仍讀 r11 第一部
archive_tip: archive-20260807-r11-nfa-verify-charter
board_refresh: 2026-08-07T14:04+08:00
self_reported: true
---

# augur 優化——逐步執行最佳下一步計畫書 r12（2026-08-07）

> **一句**：在 **r11 深化理解**上，把**目前全部開問題**收成可逐步執行的「最佳下一步／可先做／可同步」板——**後續優化選刀以此檔為準**。  
> **性質**：[I]；不創 [N]；不解凍；不掛 cron；不 sim-apply；不假關確立級；**勿重掃假綠**。  
> **疊用**：  
> - 人話對齊 → `charter_plain_zh_r11`  
> - **現況理解** → r11 第一部  
> - **選刀** → **本檔 r12**  
> - **准否／驗收** → S1→S5 SSOT ＋ 最近 ARCHIVE／standing  
> **日更**：`skip-sync-B` · `no-SIM-apply` · 誠實 econ · **主軸 #1 候 A→B3**。  
> **板刷新（14:04）**：Wave-A 收官 ✅；RankRidge RETRAIN＋SERVE-SWAP＠0731 ✅；NF-A 含 KNN 全 STOP。

---

## §0 護欄與讀序

```text
讀序: 人話 r11 → 理解 r11 第一部 → 本檔 r12 → S1→S5 SSOT → 最近 ARCHIVE/standing → #1 watcher
硬邊界: FZ/GATE-keep | skip-sync-B | no-SIM-apply | no-M-resume | no-β5
         | NF-pause | no-cron-B3 | 誠實 econ | 勿重掃假綠 | no-promote 默認
```

| 已授重用 | 來源 |
|---|---|
| 日更 B3＠D | standing GO＋`run_daily_asof_predict.sh` |
| A→B3＠08-07 ARMED | watcher＋`OPS-B3-A2B3-ARMED-20260807` |
| 封存 tip | `archive-20260807-r11-nfa-verify-charter` @ `c2edc1b` |

**LIVE**（≈14:04+08 **2026-08-07**）：PriceAdj／fv 頂＝**2026-08-06**；B3＠06＝DONE（serve＝**RankRidge asof 2026-07-31** 五 H＠tip）；A＠08-07＝**WAIT**；`evaluated_pass=0`；H20 econ=**dead**。

---

## §1 全域開問題板（最佳下一步 · 可先／∥）

| # | 問題 | 最佳下一步 | 可先／∥？ | 狀態 |
|---|---|---|---|---|
| **1** | 日更＠**2026-08-07** | 候 A 價→自動 B3（已 armed） | **主軸**；∥ #2／#10 | 🟡 ARMED／WAIT |
| **2** | econ／dgate 誠實形 | 不修綠；日更照常 | **∥** | 🟡 pass=0；H20 dead |
| **3** | graph asof 錯位 | — | — | 🟢 |
| **4** | H82 ghost | — | — | 🟢 |
| **5** | r7–r11 文檔地盤 | — | — | 🟢（r11＋本檔） |
| **6** | 08-07 封存 | — | — | 🟢 tip push 完 |
| **7** | 圖消費端 | G3／rebuild 另 GO；熱路徑仍不讀圖 | ∥文件 | 🟢 G1＋**G2 stub＠08-07**／G3🔴 |
| **8** | C1 EXPAND／CYCLE | CYCLE／殘 gap **閒時** | ∥日更後 | 🟡 EXPAND✅／CYCLE🔴 |
| **9** | P6 週 fit | 下一 asof **閒時另 GO** | 閒時·⊥日更 | 🟡 |
| **10** | M／β5／NF | 只輕監；禁默開新族 | **∥** | ❄ |
| **11** | Dividend／dim-sync | 另 auth | 旁車道 | ❄ |
| **12** | sim apply | **禁** | — | ❄ |
| **13** | 循環依賴 | explore-only（零改碼） | 低優先∥ | 🔴 |
| **14** | scripts 冗餘 | #29 另計畫 | 延後 | 🔴 |
| **15** | 10-14 治權日曆 | 10 月初複核 | 排程 | 🟡 |
| **16** | H40／120 納每日 B | 不改 standing | 延後 | ❄ |
| **17** | dgate evaluate | 另明示 GO | 延後 | 🟡 |
| **18** | 其他模型驗証 | **勿重掃**；V4／新特徵另契約 | ∥文件 | 🟢 V*＋NF-A 收官 |
| **19** | `model_family_chk` | `SCHEMA-FAMILY-CHK-go-plan`（挑戰字面；≠升格） | 閒時⊥#1 | 🟡 |
| **20** | 08-07 文件落地 | — | — | 🟢 封存完 |
| **21** | Wave-A 收官 | — | — | 🟢 `WAVE-A-BOUNDED-CLOSE-EXECUTED` |
| **22** | RankRidge asof 前進 | — | — | 🟢 RETRAIN＋SERVE-SWAP‑0731 |

---

## §2 逐步執行序列

### Phase 0｜✅ DONE

r11 理解＋人話憲章＋封存 `archive-20260807-r11-nfa-verify-charter`；本檔 r12 導航落地。

### Phase 1｜🟡 IN FLIGHT（主軸）

| 步 | 觸發 | 動作 | 驗收（SSOT＋封存／standing） |
|---|---|---|---|
| 1a | PriceAdj≥**08-07** | 自動 B3 `--date 2026-08-07` | RC=0；Adv as_of=D；EXECUTED 帳 |
| 1b | 23:50 仍無價 | TIMEOUT WAIT 帳；**不**假跑 | WAIT audit |
| 1c | 之後每新 D | standing A→B3 | 同 1a |

**∥ Phase 1（不搶 B3 CPU）**：#2 誠實敘事；#10 凍結輕監；#7 純文件（#18／#21／#22 本刷新已🟢）。

### Phase 2｜Steward 選一（#1 未完可不搶）

| 順位 | 刀 | paste／草案 |
|---|---|---|
| 2.1 | Wave-A 有界收官 | ~~`Wave-A-bounded-close`~~ ✅ EXECUTED |
| 2.2 | GRAPH G2 stub | `GRAPH-CONSUME-plan-first \| FZ/GATE-keep` |
| 2.3 | registry family_chk | `SCHEMA-FAMILY-CHK-go-plan \| FZ/GATE-keep \| no-promote` |
| 2.4 | C1 CYCLE | 既有 `LOOP-S2-TO-S1-…` 另 GO |
| 2.5 | P6 週 fit | `P6-REFIT-…-go`（閒時） |
| 2.6 | 結構循環 explore | `STRUCT-CYCLE-EXPLORE-go`（零改碼） |

### Phase 3｜延後（本檔不開刀）

解凍 M／β5；撤全域 NF；cron／timer B3；sim `--apply`；Dividend 全量；假關 dgate；H40／120 強迫入日更；同尺重掃 RF／XGB／Cat／SVM／MLP；V4 廣解凍默訓。

---

## §3 軌快照

| 軌 | 狀態 |
|---|---|
| A 日頻 | 🟡 Phase1 armed／WAIT＠08-07 |
| B 閉環／圖 | H82／graph 寫庫 🟢；消費 G2 🔴 |
| C 結構 | 🔴 循環／scripts |
| D 日曆 | 🟡 10-14 |
| E 凍結 | ❄ M／β／NF／sim |
| F 模型／驗証 | V*＋NF-A STOP；勿重掃；收官可選 |
| G 文件 | r11／r12／封存 🟢 |

---

## §4 其他模型（縮規；詳 r11／INVENTORY）

| 原則 | 操作 |
|---|---|
| 歷史資料可訓可驗 | as-of 凍結窗（例 `until=2026-06-30`）＋prodset |
| 一次一族 | 有界 `NF-*-go`；全域 pause keep |
| 已 STOP | **勿重掃假綠** |
| 升格 | 預凍門檻＋另句 promote GO；預設不升 |

---

## §5 操作協議

1. 選刀＝本檔 §1 `#` 或 §2 Phase 步。  
2. 對照 §0＋S1→S5 SSOT；缺 GO→AskQuestion。  
3. 驗收＝**SSOT＋最近封存／standing**（口頭進度不算）。  
4. EXECUTED audit；重大收斂→r13 刷新本板。  
5. 默認：不解凍／不 cron／不 apply／不假 B3／不升格。

---

## §6 Paste-ready

採納本導航（零開訓）：

```text
OPT-R12-adopt | FZ/GATE-keep | skip-sync-B | no-SIM-apply | hold-#1 | nav=r12
```

維持主軸、只候 A：

```text
hold-#1 | A→B3@2026-08-07 | no-fake-B3
```

文件旁刀（例）：

```text
Wave-A-bounded-close | FZ/GATE-keep | no-train
GRAPH-CONSUME-plan-first | FZ/GATE-keep
SCHEMA-FAMILY-CHK-go-plan | FZ/GATE-keep | no-promote
```

---

## §7 採納後讀序（後續優化）

1. `reports/augur_project_charter_plain_zh_r11_20260807.md`  
2. `reports/augur_deep_understanding_and_opt_plan_r11_20260807.md`（**理解**）  
3. **`reports/augur_opt_stepwise_best_next_plan_r12_20260807.md`（本檔·選刀）**  
4. `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`  
5. 最近 ARCHIVE（`archive-20260807-r11-nfa-verify-charter`）／standing／#1 watcher  

r10＝史料；r11 第二部選刀敘事以**本檔為準**。

---

## §8 本檔驗收

- [x] 全部開問題含最佳下一步＋可先／∥  
- [x] Phase 0–3 可執行  
- [x] 主軸 #1／勿重掃／驗收三層寫死  
- [x] paste-ready  
- [x] 不創 [N]、不開訓  

*完。[I] r12 執行導航 · self-reported。*
