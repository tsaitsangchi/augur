---
title: augur 優化——逐步執行最佳下一步計畫書 r14（刷新加強）
status: final
series: optimization_plan
round: r14
role: **後續優化執行 SSOT**（全域開問題＋最佳下一步＋可先／∥；依 r14 深化理解）
date: 2026-08-11
viewpoint: 2026-08-12T08:42+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r14_20260811.md
  - reports/augur_project_charter_plain_zh_r14_20260811.md
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
supersedes_as_exec_nav:
  - reports/augur_opt_stepwise_best_next_plan_r13_20260808.md
archive_tip: archive-20260811-b3-kh8-ppt-aap-hold
board_refresh: 2026-08-12T08:42+08:00
refresh_note: B3＠08-11 catch-up EXECUTED；下一主軸候 PriceAdj≥08-12
self_reported: true
---

# augur 優化——逐步執行最佳下一步計畫書 r14（2026-08-11 · 刷新加強）

> **一句**：依 **r14 深化理解報告**，把專案**目前全部開問題**編成「**最佳下一步**／**可先做**／**可同步做**／**延後／禁**」執行板；**後續優化一律先對本檔選刀，再開 CODE／VERIFY**。  
> **位階**：[I]；不創 [N]；不解凍；不 sim-apply；不默升格；**勿重掃假綠**。  
> **讀序**：人話 r14 → 理解 r14 → **本檔選刀** → S1→S5 SSOT → 最近 audit／standing → watcher。  
> **LIVE（親查 2026-08-12）**：tip／fv＝**08-11**（B3 catch-up **EXECUTED** · 20,60）；H20＝**dead**、H60＝**thin**；PriceAdj＝**08-11** → 下一主軸候 **≥08-12**。

---

## §0 怎麼用這份計畫書（後續優化協議）

```text
每次要開工／回答「下一步」：
  1) 打開本檔 §1 開問題板 → 找狀態≠🟢 的列
  2) 取「最佳下一步」；看「可先／∥」欄決定是否搶主軸
  3) 缺 GO／雙明示 → AskQuestion；禁默跑升格／解凍／假 B3
  4) 做完 → 寫 audit（GO／EXECUTED／TIMEOUT）→ 改本檔該列狀態
  5) 觸發 §8 → 再生 r15（勿原地無限貼）
```

| 標記 | 意思 |
|---|---|
| **主軸** | 唯一優先；其他不得搶資源假開工 |
| **∥** | 可與主軸**同步**（不改 tip／不升格／不假 B3） |
| **可先** | 主軸 WAIT 時的閒時刀（仍須 GO 若寫庫／訓模） |
| **延後** | 本輪不開 |
| **❄／禁** | 凍結或硬禁；要動＝另句授權 |

**Hard doors（每次開工複誦）**：

```text
FZ/GATE-keep | hold-#1 | skip-sync-B | no-fake-B3 | NF-pause
| no-SIM-apply | no-cron-B3 | 誠實 econ | 勿重掃假綠 | no-promote 默認
| PDF-C-no-ASR | ASR=owned_local+local_private only
```

| 已授重用（勿重問） | 來源 |
|---|---|
| 日更 B3＠D · `20,60` | standing＋`run_daily_asof_predict.sh` |
| VERIFY-B3＠08-10 | `VERIFY-B3-20260810-EXECUTED` |
| A→B3 候 **D=08-11** | `OPS-B3-A2B3-ARMED-20260811` · `/tmp/asof-ping-0811/` |
| tip 五窗一槍＠08-10 | VERIFY（**≠**改 standing 預設殼） |
| PPT／PDF-C／AVI-ASR | 各 `*-EXECUTED-20260811`（知識≠模型升格） |

---

## §1 全域開問題板（全部問題 · 最佳下一步 · 可先／∥）

> 對齊理解 r14 債表 R14-01…14；列號穩定，後續只改「狀態／下一步」。

| # | 問題（對應債） | 最佳下一步 | 可先／∥？ | 狀態 |
|---|---|---|---|---|
| **1** | 日更 tip≥**08-12**（R14-01） | 候 `PriceAdj≥08-12` → B3 `--date 2026-08-12 --horizons 20,60`；**08-11 已 EXECUTED** | **主軸**；∥ #2／#26 | 🟡 **WAIT 08-12**（08-11🟢） |
| **2** | econ／dgate（R14-02） | **不修綠**；披露＠08-11：H20=dead／H60=thin | **∥** | 🟡 |
| **3** | graph tip 邊 | — | — | 🟢 |
| **4** | H82 ghost | — | — | 🟢 |
| **5** | r14 文檔地盤 | — | — | 🟢 |
| **6** | 08-11 ARCHIVE | — | — | 🟢 |
| **7** | 圖提拔熱路徑（R14-05） | 另高門檻 `VERIFY-graph-cand-go` | 延後 | 🔴 提拔；旁路🟢 |
| **8** | C1／CYCLE | — | — | 🟢 |
| **9** | P6／長窗（R14-04） | 對帳 08-10 artifact；擴長窗另 plan＋GO | **可先**（主軸 WAIT） | 🟡 |
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
| **22** | RankRidge tip 鏈 | 08-11 ALL-RANK 已重訓＋repredict；換殼敘事另句 | — | 🟢 `RETRAIN-ASOF-0811-ALL-RANK-EXECUTED` |
| **23** | tip＋N 實現報酬（R14-14） | 等價蓋過 tip＋N 日 | 延後 | 🔴 |
| **24** | Writer／`.doc`（R14-11） | —／剩餘自掃圖 no_text | — | 🟢 `DOC-WRITER-REINGEST-EXECUTED` ok=48 |
| **25** | ASR 品質／via UX（R14-12） | 可選對聽；via 抽樣已見 | **∥／可先** | 🟢 抽樣 via |
| **26** | 私有 readout／ANN（R14-13） | 固化腳本另 GO；矩陣已 PASS | **∥／可先** | 🟢 抽樣；🟡 固化 |
| **27** | `.msg`／rar | 明示跳過或另 plan | 延後 | 🔴 |
| **28** | KH8 discrim＞7 | 生產 **stop-at-7**；升格另 GO | 延後 | ❄ |

---

## §2 決策速查：現在該做什麼？

| 若你問 | 答案（本視點 **2026-08-12**） |
|---|---|
| **最佳下一步（唯一）** | **#1**：候 `PriceAdj≥2026-08-12` → B3 `20,60`；**08-11 已 EXECUTED**（catch-up） |
| **現在可同步做** | **#2** 披露 dead／thin；**#10** 凍結輕監；**#26** 固化私有 smoke（可選） |
| **主軸 WAIT 可先做** | **#9** P6 文件對帳；**#25** 可選對聽 |
| **不要做** | 假 B3、sim-apply、換冠、默改五窗殼、重掃 STOP 族、ASR→PDF-C |

```text
paste（主軸）:
  hold-#1 | WAIT PriceAdj≥2026-08-12 | B3 horizons=20,60
  | prior B3@08-11 EXECUTED | FZ/GATE-keep | no-fake-B3 | no-SIM-apply
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

**∥ Phase 1（允許並行，禁搶 tip）**：

| 步 | 對齊 # | 動作摘要 | 驗收 |
|---|---|---|---|
| 1p | #2 | 日更後披露 dead／thin；禁塗 dgate | 帳或對話無「已綠」 |
| 1q | #10 | 不開 NF／M／β；僅文件監看 | 無新族 train 默啟 |
| 1r | #24 | Writer 安裝＋`.doc` 抽字＋擇批 reingest | skip:missing_parser↓；audit |
| 1s | #26 | 私有／ASR smoke（未登入 0／登入命中） | 通過表 |
| 1t | #25 | via 可見＋可選對聽抽樣 | 引文或 UI 可見 via |

### Phase 2｜Steward 選一（不搶 #1）

| 順位 | 刀 | 開法 | 驗收 |
|---|---|---|---|
| 2.1 | Writer／doc 大批 | `DOC-WRITER-REINGEST-go` | EXECUTED＋抽樣 readout |
| 2.2 | 私有回歸套件固化 | `KH-PRIVATE-SMOKE-go` | 腳本可重跑 |
| 2.3 | P6／長窗 | 另 plan＋GO | artifact 對齊 tip |
| 2.4 | 升格門檻文件 | `PROMOTE-TRACK-doc` | 文件 [I]；仍 no-promote |
| 2.5 | standing 五窗殼 | **雙明示**＋改預設 | standing≠口頭五窗 |
| 2.6 | 圖提拔 | `VERIFY-graph-cand-go` | 高門檻 evidence |
| 2.7 | STRUCT／scripts | explore／#29 | 報告；慢改碼 |

### Phase 3｜延後／禁（本檔不開刀）

解凍 M／β5；撤 NF-pause；cron B3；sim `--apply`；Dividend 全量；假關 dgate；同尺重掃 STOP；無證據 SERVE-SWAP；ASR 進 PDF-C；LLM 潤飾回寫庫；KH8 discrim 默升＞7；无價假跑 08-11。

---

## §4 軌快照

| 軌 | 狀態 | 本輪動作 |
|---|---|---|
| A 日頻 | 🟡 WAIT tip≥08-11 | Phase 1a–1c |
| B 閉環／圖 | 旁路🟢／提拔🔴 | 延後 2.6 |
| C 結構 | 🔴 | 延後 2.7 |
| D 日曆 | 🟡 10–14 | #15 |
| E 凍結 | ❄ | #10–12／#28 |
| F 模型 | 冠軍穩／STOP 多 | 勿重掃；慎 swap |
| G 文件 | 🟢 r14 | 本檔＝選刀 SSOT |
| H 知識 | 🟢 窄切／🟡 棧與回歸 | ∥ #24–26 |

---

## §5 工作包卡片（開跑複製）

### WP-A｜主軸日更（#1）

```text
WHEN: PriceAdj≥2026-08-11
DO:   bash scripts/run_daily_asof_predict.sh --date 2026-08-11 --horizons 20,60
DONT: sync-B 偷跑; 假 B3; sim-apply; 默五窗; SERVE-SWAP
DONE: RC=0 + tip=D + EXECUTED/FIRED audit + #14 誠實
```

### WP-K｜知識有界（#24–26 · ∥）

```text
WHEN: 主軸 WAIT 或日更後閒時
DO:   Writer→doc 自測→選批; 私有 smoke; via 檢查
DONT: 潤飾回寫; 公網 ASR; 未登入洩私有
DONE: audit 或固定題通過表
```

### WP-F｜凍結輕監（#10 · ∥）

```text
WHEN: 任意
DO:   確認無默訓新族; 文件列 STOP
DONT: NF-*-go 無 Steward; 重掃假綠
DONE: 無違規 commit/job
```

---

## §6 與深化理解債表對照

| 理解 R14-* | 本板 # | 處置 |
|---|---|---|
| R14-01 日更 | #1 | 主軸 WAIT |
| R14-02 econ | #2 | ∥ 不修綠 |
| R14-03 五窗殼 | #16 | ❄ |
| R14-04 P6 | #9 | 可先／另 GO |
| R14-05 圖提拔 | #7 | 延後 |
| R14-06 升格 | #20 | ❄ |
| R14-07 NF | #10 | ❄ |
| R14-08 scripts | #14 | 延後 |
| R14-09 M／sim… | #10–12 | ❄ |
| R14-10 日曆 | #15 | 排程 |
| R14-11 Writer | #24 | ∥／可先 |
| R14-12 ASR UX | #25 | ∥／可先 |
| R14-13 私有回歸 | #26 | ∥／可先 |
| R14-14 tip+N | #23 | 延後 |

---

## §7 驗收（本計畫書本身）

- [x] 全部開問題入板（市場＋知識＋凍結＋結構）  
- [x] 每列有「最佳下一步」＋「可先／∥」  
- [x] Phase 0–3＋WP 卡片可執行  
- [x] 對齊人話 r14／理解 r14／LIVE 親查  
- [x] 聲明：**後續優化以此檔為選刀 SSOT**  

---

## §8 何時寫 r15（刷新觸發）

任一生效即刷新導航（勿只改對話記憶）：

1. tip≥**08-11** 日更閉合（FIRED／EXECUTED 或 TIMEOUT）；或  
2. Steward 雙明示改 standing／升格／解凍；或  
3. 知識 #24+#26 整段收口並入 ARCHIVE。

---

## §9 結語

後續優化口令：

> **先對 r14 選刀板 → 主軸不假跑 → 可∥知識與誠實披露 → 其餘要 GO。**

配套：

- 理解：`reports/augur_deep_understanding_and_opt_plan_r14_20260811.md`  
- 人話：`reports/augur_project_charter_plain_zh_r14_20260811.md`  

*完。[I] · self-reported · r14 選刀 SSOT（刷新加強）。*
