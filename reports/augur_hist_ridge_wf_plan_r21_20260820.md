---
title: 歷史逐日特徵＋宇宙＋RankRidge 八窗 walk-forward（HIST-RIDGE-WF-v1）
status: adopted_by_paste
series: s1s5_loop
round: r21
date: 2026-08-20
viewpoint: 2026-08-20T10:40+08:00
layer: "[I]"
product_id: HIST-RIDGE-WF-v1
role: Steward 點名開這一槍；目的＝讓 RIDGE-THEN-PB 能用 as-of 分數驗 30 日，不是改日常出門
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r21_20260820.md
shell: scripts/run_hist_ridge_wf.sh
batch: scripts/run_hist_ridge_wf_batch.py
self_reported: true
---

# HIST-RIDGE-WF-v1｜歷史逐日特徵＋宇宙＋八窗 RankRidge

> **一句**：要驗證「相對強／弱 Top10 再過閘」是否比全宇宙路徑閘準，必須先有**當時世界**的日頻特徵、核心宇宙、walk-forward RankRidge 八窗分數。本槍只做這件事。  
> **不是**：假 B3＠08-20、換冠、改 standing H20+H60、開 NF、`--track other --apply`、重掃 0812、把 2000–2013 硬灌進核心（核心閘地板仍＝**2014-01-01**）。

Steward 點名：`開一槍歷史逐日特徵＋宇宙＋walk-forward 八窗訓練與分數`

---

## §0 護欄

```text
HIST-RIDGE-WF-v1 | no-fake-B3@08-20 | D≤PriceAdj | family=RankRidge | H_TRACK=8
| standing=20,60 不改 | no-promote | no-SIM-apply | NF-pause
| 不覆寫方向臂 | 不重建既有 core＠08-19 | 不做 8 族 64 格
| 2000–2013＝本槍範圍外（須另改 core since）
| 分數 ≠ 報酬％ | 條件 ≠ 可交易
```

## §1 為什麼不能一次灌到 2000

| 需要 | 庫裡（親查） |
|---|---|
| 2014-01-01…2026-08-19 交易日 | **3,081** |
| 已結束月份的月尾（2014-01…2026-07） | **151**（08-19＝8 月月中／價頂，不列入月尾訓） |
| 月尾已有 `feature_values`／核心 | **63**／同日（另 08-19 有核心但不算已結束月尾） |
| 月尾還缺特徵 | **88** |
| 2000–2013 | 另約 2,500 日；**核心閘 `--since 2014-01-01`**，本槍不改地板 |
| 最後可驗 30 日的 as-of | **2026-07-06**（t+1 進、再抱 30 個交易日；07-07 出口超出價頂，不算完整樣本） |

一月一日訓八族 × 八窗約 **9 分鐘／日**。三千日＝幾週機器時間。本槍只訓 **RankRidge 八窗**。  
**定錨**：每個交易日 D 的模型 `asof=D`，特徵／宇宙／訓練標皆不得用 D 之後的資料（`label_realized_by`：出場日 ≤ D）。不是拿 08-19 的模型套回 2014。  
月尾仍先 collect——那是 PIT 核心樣本河，不是「只在月末訓、月中借模型」。

## §2 怎麼走（對齊現有殼，不另發明世界）

對每個目標日 D（D ≤ 價頂 **2026-08-19**）：

1. **特徵**：`build_feature_panel.py --panels D --asof`（HIST 缺 panel 時同一刀；roster＝曾進核心的股）  
2. **宇宙**：`build_core_universe.py --asof --incremental --asof-date D --skip-pan-hist`（**不**全表 DELETE、**不**重灌 08-19）  
3. **訓練**（as-of 定錨）：`train_ranker.py --run --family RankRidge --horizon {H_TRACK} --asof D --resume`  
   - 該日模型 stamp＝**D**；panels ≤ D；**標出場日必須 ≤ D**（價表已長到 2026，不能靠「日曆不夠」擋洩漏）  
   - PIT 核心：舊 panel 沒有 `core_universe_asof` 列就不進樣本  
   - 樣本不足 → 該日該窗不誠實訓。**H240＠D 是往回推**：最後可用訓練面板＝D 往前第 241 個交易日（t+1 再抱 240，出場日≤D）。例如 D=2014-08-19 → 最後面板 **2013-08-27**。不是等到 2015。2014 以前不寫 `core_universe_asof`（`--since` 地板仍 2014）；舊 panel 無核心列時訓練回退該日 `feature_values` 的股。  
4. **分數**：`predict_asof.py --run --family RankRidge --asof D --horizon H` × 八窗（載 ≤D 最新可載；逐日訓齊後即同日模型）

之後才做 RIDGE-THEN-PB 探針 × 已實現 30 日報酬（P4；本窗第一日先把鏈跑通）。

## §3 分期（Steward 2026-08-20；同日訂正：逐日 asof=D）

```text
asof=D 定錨：該日模型只准用 ≤D 的特徵／宇宙／價／已實現標。禁止參考 D 之後任何資料。
特徵＋核心：**每個交易日**（有還原價即可），不是只有月尾。2014-08-19 這種月中日同樣灌。
1. 月尾河可繼續當 PIT 樣本（不擋月中日）
2. 每個交易日特徵＋核心，可訓日起 asof=D 重訓八窗＋打分
3. 分數夠、且 30 日已實現，才拿 RIDGE-THEN-PB 對路徑閘
```

「月中只用上月末模型打分」＝省算捷徑，**不是** as-of 定義。Steward 訂正後：每個交易日產生 stamp＝該日的模型。

| 階 | 做 | 何時 |
|---|---|---|
| **P0** | 盤點 | LIVE：月尾特徵河仍在灌 |
| **P1-collect** | 月尾：特徵＋增量核心 | **正在跑**；`--skip-train --skip-predict` |
| **P2-collect** | **每個交易日**特徵＋核心（月中＝交易日即可） | 與月尾河並行可灌單日；全量 `--all-days --collect-only` |
| **P2-train** | 每個交易日 `asof=D` 八窗訓＋打分 | **正在跑** `--all-days --train-predict --from 2014-01-02` →價頂 |
| **P4** | RIDGE-THEN-PB vs 路徑閘 | 許多 as-of ≤**2026-07-06** 已有該日模型＋八窗分且 30 日已實現 |
| **禁** | 2000–2013、改 standing、promote、假 B3＠08-20、用未來標、用 tip 模型套歷史日 | 另 GO |

**為什麼還是先月尾 collect**：`train_ranker` `asof=True`，舊 panel 必須自己有核心快照。2014-01 以前沒有。標出場日 ≤ 訓練日（`label_realized_by`）。

殼：`scripts/run_hist_ridge_wf.sh`（單日）· `scripts/run_hist_ridge_wf_batch.py`（月尾／月中河）

## §4 驗收（第一日）

- [x] 08-20 仍假 B3；鏈通第一日 D＝**2026-07-07**（**不是**完整 30 日樣本）  
- [x] `feature_values`＠07-07 有列；`core_universe_asof`＠07-07＝284；**08-19 核心＝285 未變**  
- [x] RankRidge 八窗＠07-07 可載（當時未濾未來標；月尾河改走 `label_realized_by`）  
- [ ] **P1-collect**：88 個月尾特徵＋核心  
- [ ] **P1-train**：月尾八窗模型＋分數（最早全八窗約 2015-01-30）  
- [ ] **P2**：月中日只打分  
- [ ] **P4**：對照路徑閘（asof ≤2026-07-06、樣本要多）  
- [x] standing 未改；未 promote；未寫 08-20  

*完。[I] · self-reported · HIST-RIDGE-WF-v1。*
