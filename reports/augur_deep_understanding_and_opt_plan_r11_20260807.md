---
title: augur 深化理解＋專案優化計畫書（合併）r11
status: final
series: deep_understanding_and_opt
round: r11
date: 2026-08-07
viewpoint: 2026-08-07T13:12+08:00
layer: "[I]"
role: 後續優化地基（理解＋選刀同一檔）；刷新理解 r8／導航 r10
supersedes_as_exec_nav:
  - reports/augur_opt_stepwise_best_next_plan_r10_20260806.md
inherits_understanding:
  - reports/augur_deep_understanding_r8_20260806.md
  - reports/augur_deep_understanding_r6_20260804.md
companion_plain_charter: reports/augur_project_charter_plain_zh_r11_20260807.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
self_reported: true
---

# augur 深化理解＋專案優化計畫書 r11（2026-08-07）

> **性質**：[I]；**不創** [N]；不解凍；不掛 cron；不 sim `--apply`；不假關確立級。  
> **一句**：把「專案是什麼／現在卡在哪／下一步怎麼排」收成**同一份後續優化地基**——之後選刀以本檔為導航 SSOT（刷新 r10）。  
> **疊用**：准否／閉環 enrichment → 仍以 S1→S5 SSOT（`augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`）＋ ARCHIVE／standing 為準。  
> **人話憲章對閱**：[I] `reports/augur_project_charter_plain_zh_r11_20260807.md`（**不**取代元憲章／領域大憲章）。  
> **覆蓋誠實**：非整庫逐檔複讀（reports≈429／audits≈536／scripts≈723）；本輪＝**結構地圖＋LIVE 親查＋08-06→08-07 增量收斂**；細節長表回 r6／r8／INVENTORY。

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
  ↺ S5 證據回饋 S4／S3／S2（回饋弧；非 checklist 一次做完）
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
| `docs/` | 靈魂／原則精華／領域大憲章（領域 doctrine） |
| `src/augur/` | 實作：`features`／`models`／`evaluation`／`advisor`／`ingestion`／`knowledge`／`evolution`… |
| `scripts/` | CLI 動詞（sync／train／predict／econ／KH…）≈723 |
| `reports/` | 計畫／理解 [I] |
| `audits/` | GO／EXECUTED／ADOPTED 留痕 [I] |
| `models_artifacts/` | joblib；**不一定**進 `model_registry` |
| `tests/` · `ops/` · `tools/` | 回歸／運維／MCP |
| PostgreSQL `augur` | System of Record（本機約 **62GB**／registry 27 列） |

治權透鏡：概念層 L0–4；實作層 L5–7（詳 `ARCHITECTURE-OVERVIEW.md`）。  
工具規則：`CLAUDE.md`（plan-first、#9 真兆、#11／#14、#32 預凍對照）。

### §3 S1→S5 × 硬邊界（運轉真相）

| 階 | 現況一句 |
|---|---|
| **S1** | 日更靠價到 D；**禁假 B3** |
| **S2** | KH／PDF／advice 旁軌；EXPAND／CYCLE 另 GO |
| **S3** | 熱路徑 **prodset active3**；M／β5 ❄ |
| **S4** | 冠軍 **RankRidge**；**NF-pause** 禁默開新族 |
| **S5** | B3 出 pp／顧問；H20 **econ=dead**；sim **禁 apply** |

硬邊界（導航釘）：

```text
FZ/GATE-keep | skip-sync-B | no-SIM-apply | NF-pause
| no-cron-B3 | 誠實 econ | no-promote 默認 | 勿重掃假綠
```

慣例（08-07 Steward 對話釘）：

1. 其他模型＝凍結歷史窗上**一次一族**誠實重驗／有界 `NF-*-go`。  
2. **勿重掃假綠**（同尺未過門族不再刷報表當進度）。  
3. **主軸＝#1 候 A→B3**。

### §4 LIVE 錨（2026-08-07 ≈13:12+08 · 親查）

| 錨 | 值 | 來源 |
|---|---|---|
| `TaiwanStockPriceAdj` max | **2026-08-06** | psql |
| `feature_values` max panel | **2026-08-06** | psql |
| `prediction_probability` 頂 | **2026-08-06**（watcher／既有帳） | 連動 |
| `direction_gate` `evaluated_pass` | **0** | psql |
| `direction_gate` approved | **11** | psql |
| `model_registry` | **27** | psql／INVENTORY |
| DB size | **62 GB** | psql |
| 日更主掛 | RankRidge **H20**（dead）＋**H60**（thin_unestablished） | INVENTORY |
| #1 watcher | pid 候 **08-07**；最近 ping max=**08-06** WAIT | `/tmp/asof-ping-0807/watch.log` |
| DB dump | `C:\database\augur_20260807_115516.dump`（~11GB · -Fc） | 運維旁註 |

### §5 08-06→08-07 理解增量（相對 r8／r10）

| # | 增量 | 證據 |
|---|---|---|
| 1 | B3＠08-06 DONE；A 滾到候 **08-07** | standing／watcher |
| 2 | V0／V5／V1·H60／V1·H20／V3 **EXECUTED** | audits 08-06–07 |
| 3 | V2 歷史排隊 **ADOPTED**（零默訓） | `S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807` |
| 4 | NF-A 有界重驗：**RF／XGB／Cat／SVM·H20／MLP** 皆 **STOP promote** | `NF-A-*-EXECUTED-20260807` |
| 5 | SVM·H20：Sharpe 仍＞冠軍，**hit 未清**→不宣稱複現 08-04 真贏 | SVM EXECUTED |
| 6 | Wave-A adapter 可評；**`model_family_chk` 擋 registry**（orphan joblib） | RF／XGB… train log |
| 7 | 慣例釘：勿重掃假綠；主軸回 #1 | Steward 對話 |
| 8 | graph／H82 在 r10 已標 🟢（本輪未重打假債） | r10 §1 |

**未變**：確立級假不了；sim 禁 apply；NF／M／β5 凍結；H60＞H20 敘事；Sole Steward。

### §6 模型／特徵誠實結論

| 結論 | 含義 |
|---|---|
| 冠軍護城河深 | prodset3 上挑戰樹／SVM／MLP 難穩升格 |
| 歷史窗可訓可驗 | `until=2026-06-30`＋as-of／purged WF＝合法徑 |
| SKIP≠pass | taxonomy Wave B–G 多數仍缺 adapter 或誠實 SKIP |
| 下一「進化」常不是新族 | 特徵增量／圖消費／日更穩態／誠實尺，優於假掃族表 |

詳：`audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md` · `audits/S4-REOPT-BACKLOG-20260807.md`。

### §7 綜合債表（r11）

| ID | 債 | 狀態 |
|---|---|---|
| R11-01 | A→B3＠**08-07** | 🟡 **主軸** WAIT |
| R11-02 | econ／dgate 誠實形（pass=0；H20 dead） | 🟡 不修綠 |
| R11-03 | GRAPH 消費 G2 stub | 🟡 ∥文件 |
| R11-04 | C1 CYCLE／殘 gap | 🟡 閒時 |
| R11-05 | P6 週 fit | 🟡 閒時⊥日更 |
| R11-06 | 循環依賴／scripts 冗餘 | 🔴 低優先 |
| R11-07 | `model_family_chk` 挑戰族 | 🟡 另 schema GO |
| R11-08 | Wave-A 收官文件（KNN 可略） | 🟡 可選 |
| R11-09 | M／β5／NF／sim／Dividend | ❄ |
| R11-10 | 10-14 治權日曆復審 | 🟡 排程 |
| R11-11 | 08-07 後大量 audits 未入版控 | 🟡 文件債（另 commit 授） |

---

## 第二部｜優化計畫（選刀板）

### §8 讀序與操作協議

```text
現況理解 → 本檔第一部
選刀     → 本檔第二部 §9–§11
准否／驗收 → S1→S5 SSOT ＋ 最近 ARCHIVE／standing
人話對齊 → charter_plain_zh_r11（[I]）
日更     → skip-sync-B · no-SIM-apply · 誠實 econ · 不假 B3
```

1. 選刀＝§9 編號或 Phase 步。  
2. 缺 GO → AskQuestion；禁默訓／默升格。  
3. 重大收斂 → r12 刷新本檔或拆回「理解／導航」雙檔。  
4. **勿重掃假綠**；Wave-A 同尺已 STOP 者不重刷。

### §9 全域開問題（最佳下一步 · 可先／∥）

| # | 問題 | 最佳下一步 | 可先／∥ | 狀態 |
|---|---|---|---|---|
| **1** | 日更＠08-07 | 候價→自動 B3 | **主軸** | 🟡 ARMED／WAIT |
| **2** | econ／dgate | 不修綠；日更照常 | ∥ | 🟡 |
| **3** | graph asof | — | — | 🟢（沿 r10） |
| **4** | H82 ghost | — | — | 🟢 |
| **5–6** | 舊文檔／Phase1 帳 | 可略 | — | 🟢 |
| **7** | 圖消費 | `GRAPH-CONSUME-plan-first` G2 | ∥文件 | 🟡 |
| **8** | C1 | CYCLE 閒時另 GO | ⊥日更後 | 🟡 |
| **9** | P6 | 閒時另 GO | ⊥日更 | 🟡 |
| **10** | M／β5／NF | 輕監 | ∥ | ❄ |
| **11** | Dividend／dim-sync | 另 auth | 旁 | ❄ |
| **12** | sim apply | **禁** | — | ❄ |
| **13** | 循環依賴 | explore-only | 低∥ | 🔴 |
| **14** | scripts 冗餘 | #29 另計畫 | 延後 | 🔴 |
| **15** | 10-14 日曆 | 排程複核 | — | 🟡 |
| **16** | H40／120 納每日 B | 不改 standing | 延後 | ❄ |
| **17** | dgate evaluate | 另明示 GO | 延後 | 🟡 |
| **18** | 其他模型 | **勿重掃**；可選 Wave-A 收官／V4·特徵另契約 | ∥ | V*✅／NF-A STOP |
| **19** | registry CHK | 另 `SCHEMA-FAMILY-CHK-plan` | 閒時 | 🟡 新 |
| **20** | 文件落地債 | 明示 commit／archive 另授 | ∥ | 🟡 |

### §10 分階段序列

#### Phase 0｜文件地基（本檔）✅

寫出 r11 合併地基＋人話憲章對閱。

#### Phase 1｜日更主軸 🟡 IN FLIGHT

| 步 | 觸發 | 動作 | 驗收 |
|---|---|---|---|
| 1a | PriceAdj≥08-07 | 自動 B3 `--date 2026-08-07` | RC=0；Adv as_of=D |
| 1b | 逾時仍無價 | TIMEOUT WAIT 帳；**不**假跑 | WAIT audit |
| 1c | 之後每新 D | standing A→B3 | 同 1a |

#### Phase 2｜Steward 選一（不搶 #1 CPU）

| 順位 | 刀 | 草案 |
|---|---|---|
| 2.1 | Wave-A 有界收官文件 | `Wave-A-bounded-close` |
| 2.2 | GRAPH G2 stub | `GRAPH-CONSUME-plan-first \| FZ/GATE-keep` |
| 2.3 | schema family_chk | `SCHEMA-FAMILY-CHK-go-plan`（僅挑戰族字面；≠升格） |
| 2.4 | C1 CYCLE／P6／結構 explore | 各既有 paste |

#### Phase 3｜延後（本檔不開刀）

解凍；cron B3；sim-apply；Dividend 全量；假關 dgate；V4 廣解凍默訓；同尺重掃 NF-A 已 STOP 族。

### §11 其他模型徑（答「可否用過去資料」）

| 問 | 答 |
|---|---|
| 可否用過去資料收集特徵／訓練／驗證？ | **可**——庫內 as-of 歷史＋凍結 `until`（例 2026-06-30）＋prodset |
| 怎麼排？ | V1 既有族重驗 → V2 排隊 → 有界 `NF-*-go` → 仍 STOP 則勿假綠 |
| 現在還要開訓嗎？ | **預設否**；主軸 #1；再開須另 paste |
| 升格？ | 三 seed 過預凍冠軍門檻＋hit 不劣＋**另句 promote GO** |

### §12 採納後讀序

1. **本檔**（理解＋選刀）  
2. `reports/augur_project_charter_plain_zh_r11_20260807.md`（人話）  
3. `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`（閉環 SSOT）  
4. `audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md`  
5. 最近 ARCHIVE／standing／#1 watcher  

r8／r10＝史料；數字衝突以**更新 LIVE 親查／EXECUTED audit** 為準。

---

## §13 本檔驗收

- [x] 產品／閉環／硬邊界可復述  
- [x] LIVE 錨親查（PriceAdj／fv／dgate／registry／size）  
- [x] 08-07 模型軌 STOP 與「勿重掃／主軸 #1」入板  
- [x] 開問題板含可先／∥與 Phase  
- [x] 明示不創 [N]、不假 B3、不 sim-apply  
- [x] 人話憲章另檔 [I]  

*完。[I] r11 地基 · self-reported。*
