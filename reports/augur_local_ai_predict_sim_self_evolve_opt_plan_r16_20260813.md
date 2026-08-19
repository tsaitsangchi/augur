---
title: 本地 AI 股市預測模擬——S1→S5 閉環自我進化計畫書 r16
subtitle: 日更心跳＋歷史 as-of 重覆驗＋知識分軌；非全族普查 checklist
status: final
series: s1s5_loop
round: r16
date: 2026-08-13
viewpoint: 2026-08-13T13:20+08:00
layer: "[I]"
role: S1→S5 閉環自我進化**運轉 SSOT**（繼承 08-04 GO；本檔＝08-13 重新優化）
essence: 本質仍是 S1→S5 連續閉環；優化＝怎麼轉、轉什麼、什麼算進化
ssot_code: SIM-SELF-EVOLVE-OPT-PLAN-R16-20260813
parent_go: SIM-SELF-EVOLVE-OPT-PLAN-20260804-go
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
exec_nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
asof_knife: reports/augur_s1s5_asof_verify_best_next_r18_20260817.md
asof_knife_prior: reports/augur_s1s5_asof_verify_best_next_20260813.md
kh_evolve: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
kh_split: audits/KH-SPLIT-FROM-MARKET-AXIS-ADOPTED-20260812.md
l2_plan: reports/augur_daily_retrain_l2_all_rank_plan_20260812.md
l0_hotpath: reports/augur_l0_hotpath_daily_plan_20260814.md
l0_adopted: audits/L0-HOTPATH-PREDICT-DAILY-ADOPTED-20260814.md
archive_tip: archive-20260819-path-opt-charge-t5-ridge
prior_archive: archive-20260818-b3-retrain-force-hist-oos
other_verify: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
residual: audits/NF-0812-RESIDUAL-NAME-CARD-20260813.md
sole_steward: true
self_reported: true
does_not_withdraw: SIM-SELF-EVOLVE-OPT-PLAN-20260804-go
supersedes_as_operating_loop:
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
inherits_boundaries:
  - FZ/GATE-keep · skip-sync-B · no-SIM-apply · no-promote · NF-pause
  - no-fake-B3 · 勿重掃假綠 · 誠實 econ · predict ⊥ live API
  - 市場≠指揮 KH；KH≠擋 B3
---

# 本地 AI 股市預測模擬——閉環自我進化計畫書 r16（2026-08-13）

> **一句**：本質不變——這仍是 **S1→S5 自我進化閉環**，不是一次勾完的清單。  
> **重新優化**：進化改走 **日更心跳（L1→L2）＋庫內歷史 as-of 重覆驗＋知識獨立閉環**；不再把「taxonomy 全族再掃一遍變綠」當成進化。  
> **位階**：[I] 運轉 SSOT。**不創 [N]**；**不撤** 08-04 GO；衝突時 **本檔管怎麼轉**，08-04 管本質／括號驗收／已拍 GO 史料。  
> **LIVE（親查 13:20+08；過期）**：當時價頂 08-12。**2026-08-17 視點**＝價頂／包＝08-14；開工＝r18；as-of 刀＝`reports/augur_s1s5_asof_verify_best_next_r18_20260817.md`。08-15／16／17＝假 B3。

---

## 0. 本質（不改）與優化（改運轉）

### 0.1 Steward 管線（08-04 逐字；仍是北極星）

```
本地AI股市預測模擬自進化計畫
→抓取finmind及fred資料(資料完整)
→raw data交互產生KH
→產生股票特徵值(最佳化特徵完整，最佳化多種特徵值重覆驗証)
→產生模型(最佳化多種模型重覆驗証)
→產生預測股價(最佳化準確率的漲跌比率重覆驗証)
```

本質一句：**連續運轉**的閉環——前向 S1→S5，加上回饋（特徵↔知識↔raw；模型↔漲跌比尺）。成功定義仍是 **#14 經濟價值**，不是裸 IC、不是 sim 綠、不是假關確立級。

### 0.2 08-04→08-13：為什麼要重新優化

08-04 計畫在「從零鋪閉環地圖」時是對的。九天執行後，若仍按原文把「全 12 大類／≈35 族普查」當近期完成態，會把閉環轉成**假進化**（重掃、塗綠、搶日更槽）。

| 08-04 寫法（當時合理） | r16 運轉（現在該這樣轉） |
|---|---|
| 文件先行、零訓練 | 日更已在轉：B3＋L2＠08-12 **已 EXECUTED** |
| S2 掛在市場前向鏈上 | **知識分軌**；與 tip／B3 **互不等待** |
| S4＝Wave A–G 全覆蓋才算「多種」 | 「多種」＝**邊界 A 日更包**＋V0 盤點＋**點名殘格**＋誠實 SKIP／EVIDENCE |
| 缺最新價 → 用舊 as-of 續跑（對） | 再釘：**歷史 as-of＝合法重覆驗**；**假今天價＝非法** |
| C1 在 S3 收口後必須觸發 | C1 仍存在，但 **不擋** 市場心跳 |
| P0 Discovery 五項 | Discovery 已收斂；改看 **心跳＋誠實 #14** |
| 已試 2 族 | 截面 8 族＠08-12；NF 六族＠0812＝EVIDENCE **no-promote** |

**進化現在長這樣**：價到 → 用當時世界出單／重訓 → 用 #14 說實話 → 證據回饋下一刀（族／窗／特徵）→ 知識自己轉、不挡市場。

### 0.3 兩條閉環（同一本質，分軌運轉）

```text
市場閉環 M（本檔主軸）
  L0 sync（API 門）→ S1 價完整
    → S3 特徵 as-of → S4 邊界 A 重訓 → S5 出單＋#14
      ↺ C2：OOS／econ 重選族／horizon（人閘；no-promote）
      ↺ 歷史 as-of：對已有 panel 的 D 做 walk-forward（≠假今天）

知識閉環 K（外置 SSOT）
  入庫／檢索／compact 作答／假 decline 閘／KH8 stop-at-7
    ↺ C1 Arc A：特徵缺口→KH 優化（文件／ingest）
    ↺ C1 Arc B：raw 缺口→擴大 S1（另句 THAW）
  與 M 共享最多是 augur_llm.lock；無指揮關係
```

KH 細節＝`reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md`。本檔 **不編排** KH 開工順序。

---

## 1. 硬邊界（繼承＋08-13 加釘）

```text
FZ/GATE-keep | skip-sync-B | no-SIM-apply | no-promote 默認 | NF-pause
| no-fake-B3 | 勿重掃假綠 | 誠實 econ | predict ⊥ live API
| #8 anti-leakage | #11 隨機臂 ≥3 seed | #14 終關
| 禁假 evaluated_pass | p_beat ≠ 報酬％
| 市場≠指揮 KH；KH≠擋 B3
```

| 釘 | 含義 |
|---|---|
| **假 B3** | 還沒有 `PriceAdj≥D` 卻跑 D 的日更心跳 |
| **合法歷史 as-of** | D ≤ 已有 fv／PriceAdj；`train_ranker --asof D` 只讀 `panel_date≤D` |
| **邊界 A** | 日更「所有模型」＝RankRidge×5H＋challenger×8；**≠** taxonomy 全文 |
| **重掃假綠** | 0812 已 EVIDENCE／STOP 族，同尺再刷當通過 |
| **升格** | 有證據仍預設 **no-promote**；SERVE-SWAP 另軌雙明示 |
| **sim** | 風險形狀旁軸；**禁 `--apply`** 直至另句 |

---

## 2. 市場心跳（閉環怎麼每天轉）

這是 r16 相對 08-04 最大的運轉優化：**把前向鏈收成可重複的日更節奏**，而不是每次重開 Wave。

| 層 | 殼 | 做什麼 | 不做 |
|---|---|---|---|
| **L0** | `run_l0_hotpath_daily.sh`（核 A＋TRI＋FRED）。**預測日更 standing**＝既有 20:00 arena ① 呼叫本殼（`L0-HOTPATH-PREDICT-DAILY-ADOPTED`）。**不是** 93 表、**不是** `AUGUR_DIM_SYNC=1`、**不新增** cron | 價／TRI／FRED 進庫 | tip、重訓；93 表回填 |
| **L1** | `run_daily_asof_predict.sh`（B3） | feat／core／既有 serve 出單＋emit＠**今天 D** | 無價假跑；sync 進預測 |
| **L2** | `run_daily_retrain_l2_all_rank.sh` | 邊界 A as-of＝D 重訓 → H20/60 再出單 | promote；NF；Daily*；無 L1 成功 |
| **RETRAIN-ALL** | `run_retrain_all_asof_daily.sh`（平日 21:40＋09:20） | 價頂鎖；8×8＋Daily*＋Mkt*＋DirStackM | promote；emit B3；假 B3 |

**觸發（AND）**：`PriceAdj(TAIEX) ≥ D` ∧ L1 RC=0 ∧ 人／standing 授 L2 ∧ 未與 B3 搶鎖。  
**失敗**：價不足 → **整鏈 SKIP**（這就是 hold-#1）。23:50 仍無價 → TIMEOUT 帳，**仍不假跑**。

Standing 預設窗仍 **H20＋H60**。五窗永久化須 **雙明示** 改殼（❄）。

---

## 3. 歷史 as-of：重覆驗証的正門

「最佳化多種…重覆驗証」**不是**把今天的模型再訓一次，而是：

1. 在 **已有** `feature_values.panel_date＝D` 的日子上，只用當時可見資料訓練／出單／#14。  
2. 多個 D 走 walk-forward，看分布（#11），不是單日極值。  
3. 截面族 **共用** panel，不必每族重抓 FinMind。

**曆法（親查）**：2018–2025 月頻；2026 月頻至 07-31；日頻 **08-04…08-12**。出單需要剛好那天的 panel；訓練讀所有 `≤D`。把歷史補成全日頻＝另張 **S3 GO**。

殼已通（本窗 dry-plan，零寫庫）：

```text
bash scripts/run_daily_retrain_l2_all_rank.sh --date 2026-08-07 --dry-plan
# 真跑須另貼 WP-H-L2-hist-go；禁與即將開火的 B3 搶槽
```

| D | 重跑價值 |
|---|---|
| 08-12 | **不要**（L2 已 EXECUTED） |
| 08-10／08-11 | 低（A-pack 已有） |
| **08-07** | **本窗 V1 EXECUTED**（A-pack 13；原 registry 空） |
| 07-31 | 月頻；僅 Ridge×5 |
| 06-30 | 低（舊 prodset 錨已齊） |

---

## 4. 各段現況 × 驗收 × 最佳下一步

括號驗收仍對齊 08-04 §0.5；下表＝**現在怎麼過、下一槍做什麼**。

| 段 | Steward 括號 | 08-13 現況 | 階段仍算過？ | 最佳下一步 | 可先 | 可同步 |
|---|---|---|---|---|---|---|
| **S0** | 計畫可運轉 | 08-04 GO 仍在；本檔＝運轉優化 | 是 | 依本檔轉；不另修憲 | — | — |
| **S1** | 資料完整＝THAW 熱路徑 as-of，**≠** 339 表 | 價頂 **08-12**；候 08-13 | 日更心跳 **WAIT** | 價到 → B3 `20,60` | 否 | 開火獨佔 |
| **S2** | raw↔KH 交互可核；非整庫入靈魂 | 分軌；ingest S0/S3 綠；假 decline 已閘 | 知識閉環自過 | 見 KH SSOT；**不等 S1** | 巡檢 | 避開 B3 |
| **S3** | 多特徵＋提拔＋#11＋誠實覆蓋 | tip **37** 種＠08-17；P6 校準仍＠**08-14** | 生產 panel **可用**；P6 對齊＝缺口 | 沿用 panel；P6 另 GO | 文件 | 再 P6 無 GO＝否 |
| **S4 日更** | 多模型重覆驗 | 邊界 A＠08-12：Ridge×5＋chal×8 | **日更包過** | 新 D 才 L2；**禁**同尺 08-12 | 否 | 歷史 D 須 GO |
| **S4 普查** | taxonomy 全族 | V0 已刷新；NF＠0812 EVIDENCE no-promote | 普查＝**有界證據＋pause**，不是完成交易 | 殘格**點名**；禁重掃 | V0 已做 | 開新族＝否 |
| **S5** | 漲跌比重覆驗；禁假確立 | H20 dead／H60 thin；dgate 不塗綠 | **誠實形過**（過的是「說實話」） | 披露；不修綠 | 已披露 | evaluate＝否 |
| **S5 sim** | 分尺；人節奏 | 禁 apply | 旁軸凍結 | 不動 | 否 | 否 |

**方向臂 Daily***：訓練鎖＝`asof_ready.resolve_lock`（未指定 → PriceAdj TAIEX **價頂**＝可更新最新日；≠ 完整性錨 2026-05-31）。H 軌封閉集＝**H{5,10,20,40,60,90,120,240}**（H5／H90＝2026-08-14；H10＝2026-08-16；H5 ≠ D 軌 k=5；H82 已刪、CHECK 不准 82；H60＝2026-08-13、H240＝2026-08-14 另開訓練／v1 draft gate；**不**併入 v2 K=4、不 evaluate、不 approve）。**⊥** L2 邊界 A。日更＝`run_retrain_all_asof_daily.sh` 平日 21:40＋09:20（`RETRAIN-ALL-ASOF-DAILY-CRON-ADOPTED`）；**不**塞進 ALL-RANK 殼。

---

## 5. 回饋弧（重新優化後怎麼轉）

### 5.1 C2｜模型 ↔ 漲跌比（市場閉環本體）

```text
S4 邊界 A（或點名族）as-of D
  → S5 predict／emit／#14／方向 OOS
    → 分數表（多 D／多 seed 分布）
      → 改進：重選 horizon／challenger 優先（人；no-promote）
      → 持平：記帳，日更繼續
      → 退化：書面 defer 或點名殘格／特徵缺口
      → 禁止：自動 SERVE-SWAP、塗綠 dead／thin、為補洞假 B3
```

既有 `LOOP-S4-TO-S5-go`／`LOOP-S5-TO-S4-OPT-go` **仍有效**；執行節奏改為：**日更每次都做正向 C2 的 #14 披露**；「重選族」必須另句，不得因單日 dead 就換冠。

### 5.2 C1｜特徵 ↔ KH ↔ raw（不再挡心跳）

| 弧 | r16 |
|---|---|
| **A** S3→S2 | KH 缺口可記、可 ingest；**不**當市場開工條件 |
| **B** S2→擴大 S1 | 仍須 `LOOP-S2-TO-S1-EXPAND-go`；THAW-bounded |
| **C** 重驗 | 知識側自驗；**不**用 tip WAIT 擋、**不**催 B3 |

K10「C1 概念當預測特徵」＝**隔離**；另 GO 才討論，禁默加權。

### 5.3 什麼算一次「自我進化」、什麼不算

| 算進化 | 不算（假進化） |
|---|---|
| 新 D 真價 → L1／L2 → 誠實 #14 | 無價跑 B3 |
| 歷史 D walk-forward，分布可引用 | 同尺重掃 0812 六族變綠 |
| 點名殘格 0a→有界 EVIDENCE、no-promote | 無 adapter 宣稱已確立 |
| 知識命中卻假「無此內容」→閘修 | 空 SSE／整庫回填當進化 |
| 書面 defer 換冠／換窗 | 默 SERVE-SWAP；sim-apply |

空轉（心跳 SKIP、TIMEOUT）要記帳，**不是**進化失敗，也**不是**授權假跑。

---

## 6. 其他模型驗証（掛在閉環上，不是第二套主軸）

矩陣仍是 V0–V5。r16 釘死：**驗証＝選軌，不是開全族。**

| 軌 | 閉環角色 | 現況 | 下一槍 |
|---|---|---|---|
| **V0** | 知道庫裡有誰 | **已刷新** 13:10 | 當帳 |
| **V1** | 邊界 A 重覆驗 | L2＠08-12 齊；**＠08-07 V1 EXECUTED** | 禁同尺 08-12；下一歷史 D 另句 |
| **V2** | 缺 adapter 排隊 | 殘格卡 | 點名 0a |
| **V3** | C2 回饋 | 08-07 已跑一輪 | 新 asof 讓 B3 |
| **V4** | 新族解凍 | 0812 六族 EVIDENCE | **禁重掃**；解 pause 另句 |
| **V5** | S5-only | dead／thin 已披露 | 不修綠 |

殘格（須 paste）：**VECM／TCN／NB／Daily*／RL**。TimesFM／Chronos／LSTM 等同族禁再刷假綠。

---

## 7. 節奏四層（工時怎麼切）

| 層 | 何時 | 做什麼 | 不要 |
|---|---|---|---|
| **① 日更** | 價 ≥ 今天 D | L1 B3 → L2 邊界 A | 假價；promote；NF |
| **② 閒時** | 無價／heartbeat WAIT | KH `--check`；V0；披露；dry-plan；文件 | 開 `--apply` 搶即將開火的槽 |
| **③ 點名 GO** | Steward 明示 | WP-H 歷史 D；P6 refit；殘格 0a；Daily 臂；升格軌 | 把 ③ 混進 ① |
| **④ 凍結** | 預設 | sim-apply；五窗 standing；KH10；放寬 θ；Dividend 放量 | 偷渡 |

**現在（13:23）落在 ① WAIT ＋ ②／③ 08-07 V1 已 EXECUTED。** 最佳下一步仍是候 08-13。

---

## 8. 決策卡（本視點）

| 問 | 答 |
|---|---|
| **閉環最佳下一步** | S1：`PriceAdj≥08-13` → B3 `20,60` → L2 `--apply` · no-promote |
| **可先** | 本檔；V0；dry-plan；KH 巡檢；誠實 #14（皆已做或可維持） |
| **可同步** | 知識閉環；文件；監看。B3 開火讓出鎖 |
| **重覆驗下一槍（點名）** | 08-07 V1 已做；下一歷史 D 或殘格須另貼 |
| **不要** | 假 B3；重掃 0812；sim-apply；Daily* 塞 L2；P6／五窗偷渡；用 KH 進度催／擋市場 |

```text
paste（採納 r16 為運轉 SSOT）:
  SIM-SELF-EVOLVE-OPT-PLAN-R16 | inherit-08-04-GO | dual-loop
  | heartbeat=L1→L2-A | hist-asof=legal | no-fake-B3
  | NF-pause | no-promote | no-re-scan-0812 | KH-split-keep
```

日常開工順序仍以 `reports/augur_opt_stepwise_all_problems_r18_20260817.md` 全板為準；**閉環怎麼轉**以本檔為準。

---

## 9. 讀序與檔案角色

| 角色 | 路徑 |
|---|---|
| **本檔（運轉 SSOT）** | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md` |
| 本質／括號／已拍 GO（史料＋不撤） | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` |
| 今日選刀＋as-of 刀 | `reports/augur_s1s5_asof_verify_best_next_r18_20260817.md` |
| 全專案開問題 | `reports/augur_opt_stepwise_all_problems_r18_20260817.md` |
| L2 邊界 A | `reports/augur_daily_retrain_l2_all_rank_plan_20260812.md` |
| RETRAIN-ALL 日更 cron | `audits/RETRAIN-ALL-ASOF-DAILY-CRON-ADOPTED-20260814.md` |
| L0 熱路徑日班（預測日更＝核 A＋TRI；P4a 已採納） | `reports/augur_l0_hotpath_daily_plan_20260814.md` |
| C2 細節（仍有效） | `reports/augur_s4_s5_closed_loop_plan_20260804.md` |
| KH 閉環 | `reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md` |
| 其他模型矩陣 | `reports/augur_s4_other_model_verify_matrix_plan_20260806.md` |
| V0 盤點 | `audits/S4-V0-INVENTORY-20260813.md` |
| 殘格點名 | `audits/NF-0812-RESIDUAL-NAME-CARD-20260813.md` |

---

## 10. 驗收（本重新優化）

- [x] 本質句與 08-04 管線逐字保留；**不撤 GO**
- [x] 運轉改為雙閉環＋L1/L2 心跳＋歷史 as-of 正門
- [x] 「多種模型重覆驗」改寫成邊界 A＋V0–V5＋點名殘格（禁假綠）
- [x] 各段現況／可先／可同步／不要
- [x] LIVE 親查；self-reported 優先序
- [x] 不創 [N]；不開訓；不假 B3；不 sim-apply

*完。[I] · r16 · self-reported。*
