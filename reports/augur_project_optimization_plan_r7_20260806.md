---
status: final
series: optimization_plan
round: r7
date: 2026-08-06
viewpoint: 2026-08-06T08:15+08:00
depends_on:
  - reports/augur_deep_understanding_r7_20260806.md
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
  - reports/augur_project_optimization_plan_r6_20260804.md
supersedes_as_nav:
  - reports/augur_project_optimization_plan_r6_20260804.md
self_reported: true
---

# augur 專案優化計畫書 r7（2026-08-06）——地基＝深化理解報告 r7

> **性質**：[I] 優化排序建議，供 Steward 選下一手 GO；**不創設治權判準**；**不含**自動 `--apply`／默認掛 cron／解凍 M／β5／NF。  
> **地基**：`reports/augur_deep_understanding_r7_20260806.md`。  
> **與 S1→S5 SSOT**：閉環執行本體仍＝`augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`（已拍）；本檔＝**全專案導覽＋r7 優先序**，不重造閉環細節。  
> **相對 r6**：r6 多數 B／C／D 衝刺項已 EXECUTED；r7 **改以「日頻穩態＋凍結紀律＋剩餘開債」** 排序。

---

## §0 五軌總覽

| 軌 | 範圍 | r7 定位 |
|---|---|---|
| **A. 日頻運維穩態** | A→B3、standing、監看、失敗誠實 | **主軸**（已半自動化；勿掛 cron） |
| **B. Predict 閉環深化** | 凍結下可做的小刀：graph／H82／P6 節奏／C1 | **精選 GO**；大批普查已過峰 |
| **C. 結構／體積** | 循環依賴、scripts 收斂 | **低頻**；先盤點 |
| **D. 治權日曆** | 10-14、SUNSET 監看 | **排程提醒** |
| **E. 凍結護欄** | M／β5／NF／SIM-apply | **只監看；解凍＝另裁決** |

---

## §1 A 軌：日頻運維穩態（對映 r7 R7-01／R7-02／R7-15／R7-16）

| 優先 | 項 | 建議動作 | 需新 GO？ |
|---|---|---|---|
| **P0** | A 價→B3＠新 D | 維持 standing；現 **08-06 ping→auto B3** 已 armed | 否（standing＋已核准 arm） |
| P1 | 失敗告警／RC≠0 停後續 | 沿殼行為；可選：失敗寫 `audits/DAILY-ASOF-*-FAIL-*` 模板 | 可選擇性 |
| P1 | 日更後顧問抽驗 | `build_single_ticker_rel_payload(2330,20).as_of==D` | 否（runbook §5） |
| P2 | 是否把 H40／H120 納入每日 B | **不建議**入 standing（成本／敘事）；閒時另句 | 是（若要改 standing） |
| ❄ | 掛 systemd timer／改 cron | **禁止**直至另句 | 是（明示 timer GO） |

**可∥**：凍結輕監（E 軌）＋A 車道進程監看（不重跑 maintenance）。

---

## §2 B 軌：Predict 閉環深化（對映 R7-03…07／13）

> 細節契約仍讀 S1→S5 SSOT／既有 Wave 帳；本表只排刀。

| 優先 | 候選 | 對映 | 備註 |
|---|---|---|---|
| P1 | **graph_edge rebuild＠新 D** plan-first＋GO | R7-03 | asof 仍 06-30；消費端錯位 |
| P1 | **H82 train_ranker**（修 ghost）→predict＋emit＠D | R7-04 | 校準器已有 asof08-04；缺 artifact |
| P2 | P6 週節奏（H20／H60 再 fit） | R7-06 | 累積實現 exit 後；非日更 |
| P2 | C1 `LOOP-S2-TO-S1-EXPAND`／`LOOP-CYCLE-1` | R7-07 | **⊥日更**；需 API-THAW-bounded |
| ❄ | 撤 M-stop／β5／NF-pause | R7-05／13 | 須 CONTRACT／另裁決；預設不變 |
| ❄ | P1-DRIFT C 大重訓 | （r5 史料） | 非本輪主槓桿；日更已用既有 RankRidge |

**不做（除非另句）**：假關確立級；把 dead／thin 當 bug 强行「修綠」；`--all` horizon 灌進每日 B。

---

## §3 C 軌：結構／scripts（對映 R7-08／09）

| 優先 | 項 | 建議 |
|---|---|---|
| P2 | `advisor↔deliberation`／`core↔audit` 循環依賴 | **先 explore 圖**，再抽介面；不可倉促改 import |
| P2 | 全文抓取族／`curate_pme_xdom_*` 參數化 | 另小計畫；#29 |
| P3 | migrate_* 83 支 | **不收斂**（換機依賴） |
| — | action_log／sync_memory.sh | **已關**（見 r6 追記） |

---

## §4 D 軌：治權日曆（對映 R7-12／17）

| 項 | 動作 |
|---|---|
| 2026-10-14 多筆復審 | 沿用 `reports/augur_1014_review_evidence_prep_20260801.md`；10 月初集中 |
| V2-SUNSET consequence | **只監看**；無機械載體勿假裝已可自動停三軸 |
| HANDOFF lint 脫鉤 | 保守：先問再掛回 `bound_docs` |

---

## §5 E 軌：凍結護欄（操作清單）

每日／每次開刀前心智檢查：

```text
FZ/GATE-keep | skip-sync-B | no-SIM-apply | no-M-resume | no-β5 | NF-pause | no-cron-B3
```

解凍語意示例（須 Steward 親選，非本檔授權）：

- `S3-MACRO-STOCK-CONTRACT-v3-go`（重開軌 M）  
- `schedule_beta2_resume` / 撤 β5_stop  
- `NF-resume` + 族名 plan-first  
- `POST-CLOSE-DAILY-ASOF-timer-go`（若真要 timer）

---

## §6 建議序列（可先做／可同步）

### 現在∥（低風險）

1. **E 軌輕監**（確認無解凍／無第二支 B3）  
2. **A 監看**（等 08-06 價 → 自動 B3；或 WAKE 後寫 EXECUTED）  
3. 讀本檔＋r7 理解作後續對話地基（**本委託產出**）

### 下一手候選（需 Steward 選一）

4. `GRAPH-EDGE-REBUILD-plan-first`（或 GO 若契約已足）  
5. `TRAIN-H82-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
6. `LOOP-S2-TO-S1-EXPAND-go`（C1；與 4／5 互斥搶 slot 時優先說明）  
7. 結構循環依賴 **explore-only** GO  

### 明確延後

8. 新 S4 族／軌 M VERIFY／β5 假說  
9. sim `--allow-apply`／首格之後自動晉升  
10. Dividend 全量／寬 dim-sync  

---

## §7 驗收方式

| 軌 | 驗收 |
|---|---|
| A | `PriceAdj≥D` 且 B3 RC=0；Adv as_of=D；audit EXECUTED |
| B | 各 GO→EXECUTED；行為不變性或 #14 誠實未過皆可結（禁假綠） |
| C | explore 報告或 diff＋selftest；無掃描地板回退 |
| D | 日曆項有備料／複核帳 |
| E | 無未授權解凍 audit |

---

## §8 與「記住」之操作約定

後續優化預設讀序：

1. 本檔 r7 計畫（導覽）  
2. r7 深化理解（現況）  
3. S1→S5 閉環 SSOT（執行邊界）  
4. 最近 `ARCHIVE-CHECKPOINT-*`（已封增量）  

若與 r6 計畫衝突：**以 r7＋更新 audit 為準**（r6 作史料）。

---

*定版（2026-08-06）——候 Steward 選定下一手；日頻 A→B3 與凍結輕監可立即∥。*
