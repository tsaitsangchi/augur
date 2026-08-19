---
status: final
series: optimization_plan
round: r8
date: 2026-08-06
viewpoint: 2026-08-06T08:16+08:00
depends_on:
  - reports/augur_deep_understanding_r8_20260806.md
  - reports/augur_project_optimization_plan_r7_20260806.md
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
supersedes_as_nav:
  - reports/augur_project_optimization_plan_r7_20260806.md
self_reported: true
---

# augur 專案優化計畫書 r8（2026-08-06）——地基＝深化理解報告 r8

> **性質**：[I] 排序導覽；不創 [N]；不解凍；不掛 cron；不 sim-apply。  
> **相對 r7**：軌結構不變；**新增「文件地盤入版控」P0**；A 軌維持 armed 監看。  
> **閉環 SSOT**：執行邊界仍讀 S1→S5 計畫（2026-08-04 已拍）。

---

## §0 五軌（同 r7；r8 註）

| 軌 | 註 |
|---|---|
| **A 日頻穩態** | 08-06 WAIT；watcher 續跑至 READY／23:50 |
| **B 閉環精選刀** | graph／H82／C1 —— 另 GO |
| **C 結構／體積** | 低頻；先 explore |
| **D 治權日曆** | 10-14 |
| **E 凍結** | M／β5／NF｜只監看 |
| **F 文件地盤**（r8 新顯式） | r7+r8 未 push＝地基漂移風險 |

---

## §1 A 軌

| 優先 | 項 | 動作 | 新 GO？ |
|---|---|---|---|
| P0 | A→B3＠08-06 | 維持 arm_auto_b3；WAKE 後寫 EXECUTED／FAIL | 否 |
| P1 | 顧問抽驗 as_of=D | runbook §5 | 否 |
| ❄ | cron／timer | 禁 | 需明示 |

---

## §2 B 軌（下一手候選）

| 優先 | 候選句 | 對映 |
|---|---|---|
| P1 | graph_edge rebuild plan-first／GO | R8-03 |
| P1 | `TRAIN-H82-go \| FZ/GATE-keep \| skip-sync \| no-SIM-apply` | R8-04 |
| P2 | C1 EXPAND／CYCLE-1 | R8-06 |
| P2 | P6 週 fit（H20／H60） | 非日更 |
| ❄ | 撤凍結／新族 | E 軌 |

---

## §3 F 軌：文件地盤（r8 強調）

| 優先 | 項 | 建議 |
|---|---|---|
| **P0** | r7／r8 reports＋ADOPTED／REGISTER 入 git | `commit`→`push`；可選薄 tag `archive-20260806-r8-nav` |
| P1 | 計畫導航句寫入 ADOPTED 交叉指針 | 已有 r7 ADOPTED；r8 再 ADOPT 後覆蓋讀序→r8 |

---

## §4 C／D／E

沿用 r7 §3–5（循環依賴 explore；10-14 備料；凍結心智檢查句）。

```text
FZ/GATE-keep | skip-sync-B | no-SIM-apply | no-M-resume | no-β5 | NF-pause | no-cron-B3
```

---

## §5 建議序列（可∥）

### 現在∥

1. **A 監看**（候價）  
2. **E 凍結輕監**  
3. **F：commit／push r7+r8 地基**（建議與 ADOPT 同批）

### Steward 選一（互搶 slot 時先講）

4. graph rebuild  
5. H82 train  
6. C1 EXPAND  
7. 結構循環依賴 explore-only  

### 延後

解凍；sim apply；Dividend；改 standing 納 H40／H120 每日。

---

## §6 驗收

| 軌 | 驗收 |
|---|---|
| A | B3 RC=0 且 Adv as_of=D；或 TIMEOUT 有 WAIT 帳 |
| B | GO→EXECUTED；誠實未過可結 |
| F | `origin/main` 含 r8 檔；status clean |
| E | 無未授權解凍 |

---

## §7 讀序（ADOPT 後）

1. `reports/augur_deep_understanding_r8_20260806.md`  
2. `reports/augur_project_optimization_plan_r8_20260806.md`  
3. `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`  
4. 最近 `ARCHIVE-CHECKPOINT-*`／standing  

*定版 r8——候 Steward ADOPT／是否 push。*
