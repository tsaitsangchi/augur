---
title: augur 優化——逐步執行最佳下一步計畫書 r9
status: final
series: optimization_plan
round: r9
role: 後續優化執行導覽 SSOT（開問題全域板＋可∥／可先做）
date: 2026-08-06
viewpoint: 2026-08-06T08:28+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_r8_20260806.md
  - reports/augur_project_optimization_plan_r8_20260806.md
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
supersedes_as_exec_nav:
  - reports/augur_project_optimization_plan_r8_20260806.md
inherits_nav:
  - 理解 r8 →（本檔選刀）→ S1→S5 SSOT ＋ ARCHIVE／standing
self_reported: true
---

# augur 優化——逐步執行最佳下一步計畫書 r9（2026-08-06）

> **一句**：在**深化理解 r8** 地基上，把**目前全部開問題**收成可逐步執行的「最佳下一步／可先做／可同步」板——**後續優化以此檔為選刀 SSOT**。  
> **性質**：[I]；不創 [N]；不解凍 M／β5／NF；不掛 B3 cron；不 sim `--apply`；不假關確立級。  
> **准否／驗收**：仍讀 `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` ＋最近 `ARCHIVE-CHECKPOINT-*`／standing。  
> **疊用**：現況→理解 r8；**選刀→本檔 r9**；准否→S1→S5 SSOT。日更＝A 軌已授路徑。  
> **LIVE 錨**（(b) ≈08:28+08）：價／fv／core／pp／graph 頂＝**2026-08-05**；A＠08-06＝WAIT；H82 artifact✅；dgate 無 evaluated_pass。

---

## §0 讀序與護欄（每次開刀前）

```text
讀序: 理解 r8 → 本檔 r9 → S1→S5 SSOT → 最近 ARCHIVE / standing
硬邊界: FZ/GATE-keep | skip-sync-B | no-SIM-apply | no-M-resume | no-β5 | NF-pause | no-cron-B3 | 誠實 econ
```

| 已授可重用 | 來源 |
|---|---|
| 日更 B3（feat→B1→predict H20+60→emit） | `POST-CLOSE-DAILY-ASOF-standing-go-ADOPTED` |
| A 價 READY→B3＠D | arm_auto_b3（08-06 監看中） |

---

## §1 全域開問題板（最佳下一步 · 可先／∥）

狀態：🟢已關｜🟡進行／監看｜🔴開｜❄凍結｜📄帳未入版

| # | 問題 | 最佳下一步 | 可先／∥？ | 狀態 |
|---|---|---|---|---|
| **1** | 下一交易日 asof 出單 | A 價 READY→**B3＠08-06**（監看已 armed） | **主軸**；∥凍結輕監 | 🟡 WAIT |
| **2** | 確立級／econ 誠實 | **不修綠**；日更照常、標籤保留 | ∥ 產品誠實 | 🟡（非 bug） |
| **3** | graph asof 錯位 | （已 rebuild＠08-04／08-05） | — | 🟢 |
| **4** | H82 ghost | （已 train＋emit＠08-05） | — | 🟢 |
| **5** | r7／r8 文檔未入版 | （F 軌已 push） | — | 🟢 |
| **6** | H82／graph 執行帳未 push | `commit`＋`push` 六檔 audit | **可先∥**（與候 A 並行） | 📄 |
| **7** | 圖消費端是否讀新 asof | draft／plan-first：`s4_seq_graph_consume` | 可∥文件；**寫碼另 GO** | 🔴 |
| **8** | C1 S2→S1 EXPAND／CYCLE | 另 `LOOP-*-go`（⊥日更搶槽時先講） | 與 #1 互斥重活時讓 #1 | 🔴 |
| **9** | P6 週滾 H20／H60 fit | 累積實現後另 GO（非每日） | 閒時；⊥日更 | 🔴 |
| **10** | M-stop／β5／NF | **只輕監**；解凍＝另裁決句 | **∥ #1** | ❄ |
| **11** | Dividend／寬 dim-sync | 另 auth | 不同車道 | ❄ |
| **12** | sim `--apply`／時鐘格 | 禁 apply；時鐘驅動 | 旁軸 | 🟡／❄ |
| **13** | 循環依賴 advisor↔delib／core↔audit | **explore-only** 先出圖 | 可∥低優先 | 🔴 |
| **14** | scripts 同型冗餘 | #29 另小計畫 | 延後 | 🔴 |
| **15** | 10-14 治權日曆 | 備料複核（10 月初） | 排程 | 🟡 |
| **16** | H40／H120 納每日 B | **不建議**改 standing | 延後／另句 | ❄敘事 |
| **17** | dgate pass=0 | 禁假确立；另 evaluate 須明示 | 延後 | 🟡 |

---

## §2 逐步執行序列（建議路徑）

### Phase 0｜此刻（可全部∥）

| 步 | 動作 | 驗收 |
|---|---|---|
| 0a | **hold_a**：維持 A 監看＋E 凍結輕監 | watcher 活；無解凍 |
| 0b | **#6** push H82＋graph audits（可選薄 tag） | `origin/main` 含帳；clean |
| 0c | 理解錨不重寫；開刀後用本檔刷新板 | — |

### Phase 1｜主軸日更（等事件）

| 步 | 觸發 | 動作 | 驗收 |
|---|---|---|---|
| 1a | PriceAdj≥**2026-08-06** | B3 `--date 2026-08-06` | RC=0；Adv as_of=D；EXECUTED 帳 |
| 1b | TIMEOUT 23:50 | 寫 WAIT 帳；**不**假跑 B3 | WAIT audit |
| 1c | 其後每個新交易日 D | standing：A READY→B3 | 同 1a |

### Phase 2｜精選下一刀（Steward 三選一；#1 優先）

| 順位 | 刀 | GO 草案 |
|---|---|---|
| 2.1 | 圖消費接線 plan-first | `GRAPH-CONSUME-plan-first \| FZ/GATE-keep` |
| 2.2 | C1 EXPAND | `LOOP-S2-TO-S1-EXPAND-go \| … \| API-THAW-bounded` |
| 2.3 | 循環依賴 explore | `STRUCT-CYCLE-EXPLORE-go`（零改碼） |
| 2.4 | P6 週 fit H20／H60 | `P6-REFIT-…-go`（非日更） |

### Phase 3｜明確延後（本檔不排刀）

解凍 M／β5／NF；sim apply；Dividend 全量；B3 cron／timer；假關 dgate；每日強制 H40／120。

---

## §3 軌映射（承 r8；狀態刷新）

| 軌 | r9 狀態 |
|---|---|
| **A 日頻** | 🟡 08-06 WAIT；standing 有效 |
| **B 閉環** | H82／graph 重建 🟢；消費／C1／P6 週 🔴 |
| **C 結構** | 🔴 explore 未開 |
| **D 日曆** | 🟡 10-14 |
| **E 凍結** | ❄ |
| **F 文件** | r7／r8 🟢；H82／graph 帳 📄 |

---

## §4 單次對話操作協議

1. Steward 貼「選刀」或選本檔 #／Phase 步。  
2. Agent 對照 §0 護欄＋S1→S5；缺 GO 則 AskQuestion。  
3. 執行→EXECUTED audit；必要時刷新本檔 §1 狀態列（或出 r10）。  
4. **默認不**解凍、不 cron、不 apply。

---

## §5 驗收本計畫「可當後續地基」

| 項 | 準則 |
|---|---|
| 覆蓋 | §1 覆蓋現知開問題（含已關標 🟢） |
| 可執行 | 每 🔴 有下一步句或延後理由 |
| 正交 | 日更 A≠研究 B≠解凍 E |
| 採納 | Steward `adopt_r9` 後讀序改為：理解 r8→**本檔**→SSOT |

---

## §6 指針

| 角色 | 路徑 |
|---|---|
| **本檔（選刀 SSOT）** | `reports/augur_opt_stepwise_best_next_plan_r9_20260806.md` |
| 現況 | `reports/augur_deep_understanding_r8_20260806.md` |
| 前導航 | `reports/augur_project_optimization_plan_r8_20260806.md`（史料） |
| 閉環 | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` |
| 日更 | standing＋`scripts/run_daily_asof_predict.sh`＋runbook |

*定版 r9（2026-08-06）——候 Steward 採納為後續優化執行地基。*
