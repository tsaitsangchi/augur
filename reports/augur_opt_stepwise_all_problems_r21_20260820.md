---
title: augur 優化——全專案逐步執行最佳下一步（可先／可同步）計畫書 r21
status: proposed_exec_ssot
series: optimization_plan
round: r21
role: **後續優化執行計畫書（全專案開問題）**；Steward 貼 OPT-R21-ALL 後升為開工鎖
date: 2026-08-20
viewpoint: 2026-08-20T10:11+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r21_20260820.md
  - reports/augur_project_charter_plain_zh_r21_20260820.md
understanding: reports/augur_deep_understanding_and_opt_plan_r21_20260820.md
charter: reports/augur_project_charter_plain_zh_r21_20260820.md
supersedes_exec: reports/augur_opt_stepwise_all_problems_r19_20260819.md
inherits_board: reports/augur_opt_stepwise_all_problems_r19_20260819.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
detail_kh: reports/augur_kh_opt_stepwise_best_next_plan_20260813.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
path_opt_ops: reports/augur_path_timing_opt_ops_plan_r18_20260819.md
path_hit_lift: reports/augur_path_hit_lift_plan_r20_20260820.md
path_hit_tombstone: audits/PATH-HIT-LIFT-P5-STOPPED-20260820.md
slim_plan: reports/augur_repo_slim_opt_plan_r20_20260819.md
archive_tip: archive-20260820-r21-hist-wf-ridge-pb-close
self_reported: true
---

# augur 優化——全專案逐步執行最佳下一步 r21（2026-08-20 10:11）

> **一句**：r19 鎖寫於「08-19 還沒有價」。現在 **價／特徵／核心宇宙＝08-19**，**出門仍＝08-18**（僅 H20+H60）。日曆 08-20＝假 B3。路徑閘「加濾提高 30 日勝率」已 P5 判死。本檔＝後續優化執行地基（繼承 r19 全板硬門，刷新 LIVE 與兩把市場刀）。  
> **位階**：[I]；不創 [N]；不解凍；不假 B3＠08-20；不 sim-apply；不默升格；不重開 PATH-HIT-LIFT P2／P3／P4。  
> **分軌**：市場 ≠ 指揮 KH；KH ≠ 擋 B3；路徑 ≠ 改 standing。  
> **升鎖**：Steward 貼下方 `OPT-R21-ALL` 後，本檔取代 r19 成為開工鎖。未貼之前，仍以本檔 LIVE 為準（r19 LIVE 已過期，勿再當 08-19＝假 B3）。

本檔 **supersede** `reports/augur_opt_stepwise_all_problems_r19_20260819.md` 作為開工順序。理解＝r21。心跳契約仍＝r16。PATH-OPT 手冊仍管 θ／GO 文案。HIT-LIFT 河閉見墓碑。倉精化仍＝slim r20。

---

## §0 怎麼用

```text
每次要開工／問「下一步」：
  1) 先看 §1 決策卡
  2) 再看 §2 全板：狀態≠🟢／≠禁 的列
  3) 缺 GO → 停、問 Steward；有 GO → 做、寫 audit、改本檔狀態
  4) 細節指令 → r16 心跳／KH 板／PATH-OPT／WP 卡片／確立路徑 r17
```

| 標記 | 意思 |
|---|---|
| **最佳下一步** | 這一列若要動，下一槍具體做什麼 |
| **可先** | 市場主軸仍在 WAIT（08-20 無價，或 08-19 出門未授權）時，現在就可以做 |
| **可同步** | 可與另一軌或主軸 WAIT 並行；B3／L2 開火中則讓出 `augur_llm.lock` |
| **延後** | 主軸未閉合前不要排進工時 |
| **❄／禁** | 凍結或禁止；要動須另句明示 |

**Hard doors**：

```text
FZ/GATE-keep | no-fake-B3@08-20 | NF-pause | no-SIM-apply | no-promote
| 勿重掃假綠 | skip-sync-B | 誠實 econ | standing=20,60 除非雙明示
| PDF-C-no-ASR | ASR=owned_local+local_private | no-KH10 | stop-at-7 | no-relax-θ
| T0 | apply=opt-in | 有引文禁假「無此內容」 | 空包不進化
| score／p_beat／p_mkt／p_up／路徑％／勝率 ≠ 報酬％
| 市場≠指揮 KH；KH≠擋 B3；路徑≠改 standing
| 觀察≠進場 | 條件≠可交易 | 兩檔≠宇宙 | 做空≠可融券
| 禁 evaluate／approve dgate_H_5/10/60/90/240（無新 GO）
| 禁塗 established（無 E5-verdict-go）；不救 H20；不放寬 DSR 95%
| 禁再送 E4 就緒 5；禁倒 canonical 31 進 prodset
| CHARGE-T5 ≠ 可交易 ≠ #14；T20／T40 不當冠
| PATH-HIT-LIFT 河閉；禁再開 P2／P3／P4
| 四閘過 ≠ 可交易；群光條件標 ≠ 可融券
```

---

## §1 決策卡｜現在該做什麼？

視點 **2026-08-20 週四 10:11+08** LIVE（盤中）：

| 錨 | 值 |
|---|---|
| PriceAdj TAIEX max | **2026-08-19** |
| fv／core＠08-19 | 37 欄／27 955 列／**285** 檔；`asof_ready` **ready** |
| emit pv／pp | 仍 **2026-08-18** RankRidge **H20+H60** 各 286 |
| 日曆 08-20 | **假 B3** rc=3 |
| 冠軍 | RankRidge；standing 仍兩窗 |
| P6 freeze | H20／H60＠**08-14** vs 價／包 **08-19** |
| E4b | WAIT k=0；next≈**2026-11-13** |
| PATH-HIT-LIFT | **P5 墓碑** |
| RIDGE-THEN-PB＠08-19 | 做多進場 **0／10**；做空 **1／10＝2385 群光**（≠可融券） |

| 問 | 答 |
|---|---|
| **全專案最佳下一步** | **等下一句 GO**。市場有兩把合法刀，預設不代裁：**(A) 補出門＠08-19**（世界已算）；**(B) 等 08-20 真收盤再整鏈**。08-20 **不准**當 as-of。 |
| **此刻絕對不要** | 把 as-of 設成 **08-20**；promote；把四閘勝率／群光／兩檔％當可交易；KH `--apply`；重開 HIT-LIFT P2–P4 |
| **可先做（不等今日價）** | E4b 鐘重讀；P6 對帳文件；`--scan`；路徑條件探針 **dry-run 另句**；KH `--check`（本鎖不 apply） |
| **可同步做** | 上列。**不要** K9／再 P6 無 GO／NF／dgate evaluate／KH `--apply` |
| **不要做** | 假 B3＠08-20；sim-apply；塗綠；換冠；默八窗出門；重掃 0812；K9 開訓；放寬 θ；`E5-evaluate-go`；倒 canonical 31；`--track other --apply`；無 GO 補 08-10；W4／W5／RS-CHARGE P1 無句混入；本鎖順便 drain S0；HIT-LIFT 加濾 |

```text
paste（後續優化依本檔）:
  OPT-R21-ALL | no-fake-B3@08-20
  | knife-A=補出門＠08-19 WAIT-GO（世界已算、pv 仍 08-18）
  | knife-B=WAIT PriceAdj≥08-20-close
  | standing=20,60 | H_TRACK=8 | no-promote | NF-pause
  | kh=check-ok-apply-no | E-keep | stop-at-7 | no-K9-train
  | M28=clock-WAIT | no-E5 | no-canonical-3plus1
  | archive=archive-20260820-r21-hist-wf-ridge-pb-close
  | emit＠08-18 H20+H60 | fv/core＠08-19 ready | P6 freeze@08-14
  | PATH-HIT-LIFT P5 墓碑；觀察≠進場；兩檔≠宇宙；做空≠可融券
  | RIDGE-THEN-PB＠08-19 多 0／10、空 1／10 群光≠可融券
  | CHARGE-T5 P1 已閉；成本後 IS −64.8%；≠可交易
  | RS-CHARGE P1／TREND-PB W4 皆另句
  | slim-T5=90d-review-clock-candidate（≠rm；最早≈2026-11-17）
```

**工時切法（人話）**：

1. **此刻**：08-18 出門已閉。08-19 **有價、有世界、沒有出門**。08-20 **無價**。  
2. **若要名單跟上世界**：另句 `B3-go | D=2026-08-19 | horizons=20,60`。不是把日曆改成 08-20。  
3. **若等新價**：PriceAdj ≥ 08-20-close 後才整鏈。  
4. **路徑槍**：HIT-LIFT 停。其餘一次一句；不要跟 B3 搶鎖。

---

## §2 全專案開問題板

> 🟢＝本窗不當工單；❄／禁＝不要排進「可先」。

### 2.1 市場／預測／凍結／結構／路徑

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **M1a** | — | 08-14 已訓未出門 | — | — | — | 🟢 出門＠08-14 H20+H60 |
| **M1b** | — | 08-17 心跳 | — | — | — | 🟢 出門＠08-17 H20+H60 |
| **M36** | — | 08-18 已訓未出門 | — | — | — | 🟢 出門＠08-18 H20+H60 |
| **M37** | R21-01 | **08-19 世界已算、名單未出門** | Steward 貼 `B3-go \| D=2026-08-19 \| horizons=20,60` 才跑 WP-M37 | **否**（須 GO） | 讓其他長 LLM | 🟡 **刀 A**；禁假 B3＠08-20 |
| **M38** | R21-02 | 08-20 收盤未進庫 | WAIT PriceAdj≥08-20-close 後整鏈 | **否** | — | 🟡 **刀 B** |
| **M39** | R21-03 | PATH-HIT-LIFT 勝率優化 | **停**；見墓碑 | **否** | **否** | 🟢 P5 河閉；禁 P2／P3／P4 |
| **M2** | R19-03 | econ／dgate | **不修綠**；H20=dead、H60=thin；draft 閘不 evaluate | **是** | **是** | 🟢 形已誠實 |
| **M3** | — | graph tip 邊 | — | — | — | 🟢 |
| **M4** | — | H82 庫列 | 已刪；禁再插入 | — | — | 🟢 |
| **M5** | — | r21 文檔 | 開工跟**本檔**（貼 OPT-R21-ALL 後鎖） | — | — | 🟢 本輪 |
| **M6** | — | ARCHIVE | — | — | — | 🟢 `archive-20260820-r21-hist-wf-ridge-pb-close` |
| **M7** | R19-06 | 圖提拔熱路徑 | 另 `VERIFY-graph-cand-go` | **否** | **否** | 🔴 |
| **M8** | — | C1／CYCLE | 不編；見 K10 | **否** | — | 🟢 隔離 |
| **M9** | R19-05 | P6／長窗 | freeze 仍＠08-14；價／包現＠**08-19** → **缺口再開**；refit **另 GO** | 文件＝是 | 訓＝否 | 🟡 缺口 08-14 vs 08-19 |
| **M10** | R19-08 | M／β5／NF | 輕監；0812 六族**勿重掃**；殘格須點名卡 | **監看＝是**；開訓＝否 | 監看＝是 | 🟢 監看；開訓❄ |
| **M11** | R19-10 | Dividend | 另 auth | **否** | **否** | ❄ |
| **M12** | R19-10 | sim apply | **禁** | **否** | **否** | 禁 |
| **M13** | R19-09 | 循環依賴文件 | explore-only | 低優先可先讀 | 是（零碼） | 🔴 |
| **M14** | R20-11…13 | 倉精化 | 依 slim r20；T0–T4＋T6＋T7 已做；T5＝90 天複審鐘**候選**（最早≈2026-11-17；產清單≠rm） | T5 開火＝否 | 是（零產品碼） | 🟢 T7 閉；T5 候選 |
| **M15** | R19-11 | 10–14 治權日曆 | 10 月初清單；**不假關** | 排程備忘＝是 | 是 | 🟡 |
| **M16** | R19-04 | standing 八窗殼 | **雙明示**＋改 `run_daily_asof_predict.sh` 預設 | **否** | **否** | ❄ |
| **M17** | R19-21 | dgate evaluate | 另 GO；禁塗綠草稿閘 | **否** | **否** | 禁（無 GO） |
| **M18** | R19-08／27 | 其他模型族／HIST 未齊 | 已齊近：08-18／17／14／13／12／11／07／07-31；下一未齊 **08-10 缺 52**；方向臂仍＠08-18；H5 OOS ≠升格；H10 仍日曆閘；**禁**重掃 0812 | 掃描／walk＝已做；補 08-10 **另句** | 讓 B3 | 🟢 V0＠08-18；HIST＠08-11／12 64／64；H10 閘；NF❄ |
| **M19** | — | family_chk | — | — | — | 🟢 |
| **M20** | R19-07 | 升格另軌 | 可寫門檻文件；禁 SERVE-SWAP | **文件＝是** | 文件＝是 | 🟢 hold；swap❄ |
| **M21** | — | Wave-A 收官 | — | — | — | 🟢 |
| **M22** | — | RankRidge＠08-18 | 八窗 COMPLETE；B3 已寫 pv／pp＠08-18 僅 20,60 | — | — | 🟢 訓＋出門＠08-18 |
| **M22b** | R21-01 | RankRidge＠08-19 | fv／core 已算；**pv 無 08-19 列** | 見 M37 | 讓 B3 | 🟡 世界齊、出門未寫 |
| **M23** | R19-15 | tip＋N 實現報酬 | 等價蓋過 tip＋N。E4b 鐘已掛；H60 第 1 期出場＝2026-11-13 | **否**（價未蓋） | **否** | 🔴；鐘🟢 WAIT |
| **M24** | — | 相對機率／分數看板 | 守 score／p_beat≠報酬％ | — | — | 🟢 |
| **M25** | R19-20 | 工作樹未入倉 | 20260820 封存 `archive-20260820-r21-hist-wf-ridge-pb-close` | 本輪入倉 | 是 | 🟢 本封存 |
| **M26** | R19-22 | HANDOFF 過期 | 不重寫 300 行 STATE；接續讀本檔 LIVE | 備忘＝是 | 是 | 🟡 |
| **M27** | R19-23 | PME 缺 map | 維持診斷；禁降閾／禁 APPLY | 文件＝是 | 是 | 🟡 |
| **M28** | R19-24 | #14 確立 | E0–E3 已閉；E4 就緒 5 耗盡；E4b **WAIT k=0** next＝2026-11-13。新角度特徵須另句點名 | E5＝禁；鐘可重讀 | 文件＝是 | 🟡 **鐘 WAIT** |
| **M29** | R19-25 | UP-PULL／RIDGE-THEN-PB | P0＋P1＠08-18 已閉；**＠08-19 重跑**：做多進場 **0／10**、做空 **1／10＝群光**（條件標，≠可融券）；emit 另句 | P2／emit＝否 | 讓 B3 | 🟡 P1 閉＠08-19 帳；emit 未開 |
| **M30** | R19-25 | TREND-PB 目錄 | P0＋W1–W3＠08-18 已閉；**W4／W5 另句** | W4＝否（須 GO） | 讓 B3 | 🟡 W3 閉 |
| **M31** | — | WATCH-PB | P0＋P1＠08-18 EXECUTED（13／6）；觀察≠進場；P2 另句 | P2＝否 | 讓 B3 | 🟡 P1 閉 |
| **M32** | — | BULL5 | P0＋P1＠08-18 已閉；9／1；∩進場＝0；P2 另句 | P2＝否 | 讓 B3 | 🟡 P1 閉 |
| **M33** | R19-25 | RS-CHARGE | **P0 已採納**；預診 7／1；**P1 探針未寫／未跑** | P1＝否（須 GO） | 讓 B3 | 🟡 P0 閉；P1 開 |
| **M34** | — | TWIN-EX | P0＋P1＠08-18 已閉；冠軍 E-charge×T5（僅兩檔）；≠可交易 | — | 讓 B3 | 🟡 P1 閉 |
| **M35** | R19-26 | CHARGE-T5 | P0＋P1＠08-18 已閉；k=10 等權；成本後 IS **−64.8%**；T20／T40 不當冠；**≠可交易、≠#14** | 探針／emit＝否 | 讓 B3 | 🟡 P1 閉；產品失敗已量出 |
| **M40** | — | 全宇宙四閘＠08-19 | 做多 5／做空 5（H20 不擋）；cap 10 不湊滿；≠ Ridge 池、≠可交易 | 探針可另句 | 讓 B3 | 🟢 帳已算；不當日更 |

### 2.2 知識／顧問

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **K0** | — | S0 KH0 breach | 記帳 63；drain 另貼 `KH-S0-apply-go` | check＝可重跑；apply＝否 | 避開 B3 | 🟡 FIRE 63；本鎖不 apply |
| **K1** | — | S3 zh lag | — | — | — | 🟢 |
| **K2** | — | ingest 階梯 | 守 apply 選開 | — | — | 🟢 |
| **K3** | R19-19 | AUTO-LIFT | 常駐即可；**禁抬 >KH2** | **否** | — | 🟢／禁抬層 |
| **K4** | R19-14 | 私有 smoke | 回歸可重跑 | 抽樣＝是 | 是 | 🟢 |
| **K5** | R19-12 | Doc1 純圖 | **hold**；不 OCR 硬開 | **否** | — | 🟢 hold |
| **K6** | R19-14 | ASR 對聽 | 可選抽樣 | 是 | 是（輕） | 🟢 |
| **K7** | — | 8b 產品口吻 | 守 8b＋960 | — | — | 🟢 |
| **K8** | R19-16 | KH8 discrim | **E-keep／stop-at-7** | **否** | **否** | ❄ |
| **K9** | R19-17 | 他域 FT | 另 `adopt` 才訓；現 **plan-only** | **否** | **否** | 🔴 |
| **K10** | R19-18 | C1→feat | 另 GO；禁默加權 predict | **否** | **否** | 🔴 隔離 |
| **K11** | R19-13 | `.msg`／rar | skip-hold 或另 plan | **否** | **否** | 🔴 |
| **K12** | — | KH10 | — | **否** | **否** | 禁（≠ H10 交易日） |
| **K16** | — | 假 decline 閘 | 產品行為已修 | — | — | 🟢 |
| **K17** | — | 閘入倉 | — | — | — | 🟢 |

---

## §3 逐步執行序列（Phase）

### Phase 0｜✅ 已閉（本檔不當工單）

B3＋L2／RETRAIN-ALL＠08-13／08-14／08-17／**08-18 出門**；H90 取代 H82；H5／H10／H240 開窗；L0 熱路徑；RETRAIN-ALL cron；KH 分軌；假 decline 閘；KH8 未過 θ；NF＠0812 六族 no-promote；E0–E4b；HIST-ASOF＠07-31／08-07／08-13／08-12／08-11；ARCHIVE 20260819；PATH-OPT 多數 P1＠08-18；RIDGE-THEN-PB 探針＠08-18／08-19；**PATH-HIT-LIFT P5**；slim T0–T4＋T6＋T7。

### Phase 1｜🟡 現在（盤中 WAIT＋可先）

| 步 | 何時 | 做 | 不做 | 驗收 |
|---|---|---|---|---|
| **1A** | — | 08-18 出門 | — | ✅ 已閉 H20+H60 |
| **1J** | Steward 貼 B3-go＠08-19 | 兩窗出門（必要時先確認包／L2） | 把日曆當 08-20；默八窗；promote | pv／pp＠08-19 僅 20,60；#14 誠實 |
| **1B** | Steward 貼下一交易日 B3-go 且 **08-20 價到** | 整鏈心跳 | 無價假跑＠08-20 | tip=D；#14 誠實 |
| **1C** | 可先 | KH `--check`；M2 披露 | 不開 K9／K8；不 KH `--apply` | 上次：S0 FIRE 63；未 apply |
| **1D** | 可先 | M9 P6 缺口文件；E4b 鐘 | evaluate／付 N／再送就緒 5 | 鐘 WAIT；P6 refit **另 GO** |
| **1G–1I** | 已閉 | V0／V1＠08-18；HIST＠08-12／08-11 | `--track other --apply`；0812 重掃 | 見 r19 帳 |
| **1E** | 另句 | RS-CHARGE P1 dry-run | 當可交易；改 standing | n 與預診對上 |
| **1F** | 另句 | TREND-PB W4＠最近有價日 | 倒 31；開 NF；當可交易 | T09／T10／C05 帳 |
| **1K** | **禁** | PATH-HIT-LIFT P2／P3／P4 | 任何「加濾提高勝率」 | 墓碑已寫 |

**並行規則**：1C／1D 在 **1J／1B 未開火** 時可同時做。1J 或 1B 開始 → 長 LLM／apply／探針 **讓路**。

### Phase 2｜主軸閉合後（Steward 選一，不預設全開）

1. 下一交易日重複 1B（standing 20,60）  
2. P6 擴其餘 H_TRACK（有 plan＋GO；freeze＠08-14 已舊）  
3. 升格門檻文件定稿（仍 no-promote）  
4. K9 **僅**在 `K9-DOMAIN-FT-plan-adopt` 之後  
5. 圖提拔 VERIFY  
6. NF 殘格——**點名卡才 plan**  
7. standing 八窗——**僅雙明示**  
8. 新角度特徵漏斗——**另句點名**（不是 canonical 31 族內重編碼）  
9. PATH-OPT 其餘未閉槍——**各一槍、各一 ID**；**不含** HIT-LIFT  
10. 降週轉新產品（若要接 CHARGE-T5 教訓）——**新 ID**，不是改 k 偷渡

### Phase 3｜本檔不開

解凍 M／β5；無點名撤 NF-pause；cron B3；sim `--apply`；八窗改 standing；SERVE-SWAP；放寬 θ；depth≥8；KH10；K10 默灌預測；對話 approve 來源；整庫回填當進化；evaluate 草稿 `dgate_H_*`；假 B3＠08-20；`E5-evaluate-go`；倒 31 欄進 prodset；再送 range／股利／sbl／pe／margin；把 CHARGE-T5 接顧問；把兩檔％寫進 #14；把四閘勝率寫成可交易；重開 HIT-LIFT；把群光當可融券。

---

## §4 工作包（開跑複製）

### WP-M36｜補出門＠08-18（已閉）

```text
WHEN: Steward 貼 B3-go | D=2026-08-18 | horizons=20,60
DO:   bash scripts/run_daily_asof_predict.sh --date 2026-08-18 --horizons 20,60
DONT: 無價假跑; sync-B; sim-apply; 默八窗; promote
DONE: 2026-08-19 14:17 RC=0；pv/pp＠08-18 僅 20,60；H20=dead；H60=thin
```

### WP-M37｜補出門＠08-19（刀 A；須 GO）

```text
WHEN: Steward 貼 B3-go | D=2026-08-19 | horizons=20,60
      （check_asof_ready --date 2026-08-19 已 ready；fv/core 已在）
DO:   （需要時）bash scripts/run_l0_hotpath_daily.sh --date 2026-08-19 --apply
      bash scripts/run_daily_asof_predict.sh --date 2026-08-19 --horizons 20,60
      （L1 RC=0 且包未齊才）L2 / run_retrain_all_asof_daily.sh
DONT: --date 2026-08-20; sync-B; sim-apply; 默八窗; promote
DONE: RC=0 + EXECUTED + pv/pp＠08-19 僅 20,60 + #14 誠實
```

### WP-M1b｜新價心跳＠≥08-20 收盤（刀 B；須 GO）

```text
WHEN: PriceAdj(TAIEX) ≥ 該日 且 Steward 貼 B3-go
DO:   （需要時）bash scripts/run_l0_hotpath_daily.sh --date <D> --apply
      bash scripts/run_daily_asof_predict.sh --date <D> --horizons 20,60
      （L1 RC=0 且包未齊才）L2 / run_retrain_all_asof_daily.sh
DONT: 無價假跑@08-20; sync-B; sim-apply; 默八窗; promote
DONE: RC=0 + EXECUTED + #14 誠實
```

### WP-KD｜KH 巡檢（可同步）

```text
WHEN: 任意；避開 B3 開火
DO:   python scripts/kh_ingest_trigger.py --check
DONT: 無 GO 卻 --apply; 日曆假進化
DONE: 上次 08-19 14:13 S0 FIRE kh0_breach=63；未 --apply
```

### WP-K0｜S0 drain（須另句；本鎖不開）

```text
WHEN: Steward 明示 KH-S0-apply-go（且非 B3 開火）
DO:   python scripts/kh_ingest_trigger.py --apply
DONT: 把 OPT-R21-ALL 當授權去 apply；抬 >KH2
DONE: kh0_breach 63→0（尚未跑）
```

### WP-M28｜經濟確立路徑（就緒 5 耗盡；鐘 WAIT）

```text
WHEN: 任意重讀；新角度另句
DO:   python scripts/report_live_oos_clock.py --origin 2026-08-14 --h 60
DONT: 算未實現 PnL；E5-evaluate-go；再送就緒 5；倒 31 欄進 prodset；放寬 0.6
DONE: 鐘已掛；k=0；next_due=2026-11-13
```

### WP-HIT-LIFT｜停（勿再開）

```text
WHEN: 永不（本產品 ID）
DO:   無
DONT: P2 SWEET / P3 LIQ / P4 EXIT；放寬四閘；把 51% 勝率當優勢
DONE: audits/PATH-HIT-LIFT-P5-STOPPED-20260820.md
RETRY: 須全新產品 ID，不是本河續集
```

### WP-PATH｜其餘未閉槍（各須自己的 GO）

詳 `reports/augur_path_timing_opt_ops_plan_r18_20260819.md`。本檔只鎖開工順序：**不要一次開兩槍**；優先建議若 Steward 要動路徑＝`RS-CHARGE-probe-go` 或等刀 A／B。HIT-LIFT 不在此列。

---

## §5 與深化理解債表（R21／R19 → 本板）

| 債 | 本板 | 本窗處置 |
|---|---|---|
| R21-01 08-19 出門缺口 | M37／M22b | 🟡 須 B3-go＠08-19 |
| R21-02 08-20 價 | M38 | 🟡 WAIT |
| R21-03 HIT-LIFT | M39 | 🟢 P5 墓碑 |
| R19-01 08-18 出門 | M36 | 🟢 EXECUTED |
| R19-02 ≥08-19 心跳 | 拆成 M37＋M38 | 價已到 08-19；心跳未完 |
| R19-03 econ | M2／M17 | 披露；evaluate 禁 |
| R19-04 八窗殼 | M16 | ❄ |
| R19-05 P6 | M9 | 🟡 缺口 08-14 vs 08-19 |
| R19-06 圖提拔 | M7 | 延後 |
| R19-07 升格 | M20 | 可先文件；禁 swap |
| R19-08 NF | M10／M18 | 監看∥；禁重掃 |
| R19-09 scripts／倉精化 | M13／M14 | T0–T4＋T6＋T7 已閉；T5 複審鐘候選 |
| R19-10 M／sim／Dividend | M10–12 | ❄／禁 |
| R19-11 日曆 | M15 | 排程 |
| R19-12 Doc1 | K5 | hold |
| R19-13 msg／rar | K11 | skip-hold |
| R19-14 私有／ASR | K4／K6 | 可選抽樣∥ |
| R19-15 tip+N | M23 | 延後；鐘已掛 |
| R19-16 KH8 | K8 | ❄ E-keep |
| R19-17 K9 | K9 | 延後／另 adopt |
| R19-18 K10 | K10 | 隔離 |
| R19-19 AUTO-LIFT>KH2 | K3 | 禁 |
| R19-20 未入倉 | M25 | 🟡 工作樹又髒 |
| R19-21 dgate draft | M17 | 禁 |
| R19-22 HANDOFF | M26 | 備忘 |
| R19-23 PME | M27 | 診斷；禁 APPLY |
| R19-24 #14 | M28 | E4 耗盡；E4b WAIT |
| R19-25 PATH 未閉 | M29–M33 | 另句；HIT-LIFT 除外已停 |
| R19-26 CHARGE-T5 成本 | M35 | 🟢 已量出失敗邊界 |
| R19-27 HIST 未齊 | M18 | 08-12／08-11 已閉；下一＝08-10 另句 |

---

## §6 細節板（本檔不取代長指令）

| 用途 | 路徑 |
|---|---|
| 精要讀序 | `reports/SSOT_READ_ORDER.md` |
| 現行理解 | `reports/augur_deep_understanding_and_opt_plan_r21_20260820.md` |
| 人話憲章 | `reports/augur_project_charter_plain_zh_r21_20260820.md` |
| 前一執行板（LIVE 過期） | `reports/augur_opt_stepwise_all_problems_r19_20260819.md` |
| 倉精化（M14） | `reports/augur_repo_slim_opt_plan_r20_20260819.md` |
| S1→S5 閉環運轉 | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md` |
| KH 長板 | `reports/augur_kh_opt_stepwise_best_next_plan_20260813.md` |
| L0 | `reports/augur_l0_hotpath_daily_plan_20260814.md` |
| L2 | `reports/augur_daily_retrain_l2_all_rank_plan_20260812.md` |
| NF 殘格 | `audits/NF-0812-RESIDUAL-NAME-CARD-20260813.md` |
| #14 確立路徑 | `reports/augur_econ_prove_edge_plan_r17_20260817.md` |
| E4b 鐘 | `reports/augur_econ_e4b_clock_r17_20260817.md` |
| as-of 刀 | `reports/augur_s1s5_asof_verify_best_next_r19_20260819.md` |
| 路徑／進出操作手冊 | `reports/augur_path_timing_opt_ops_plan_r18_20260819.md` |
| 衝勢 5 日 | `reports/augur_charge_t5_model_plan_r18_20260819.md` |
| PATH-HIT-LIFT（停） | `reports/augur_path_hit_lift_plan_r20_20260820.md` ＋墓碑 |
| 前前執行板 | `archive/slim-t2/augur_opt_stepwise_all_problems_r18_20260817.md` |

衝突：開工順序與「可先／可同步」**以本檔為準**；殼指令與 GO 文案以長板／audit 為準。r17／r18／r19 LIVE 段（價頂／emit）**過期**，以本檔 LIVE 為準。

---

## §7 何時刷新（r22／改本檔）

1. B3＠08-19 閉合，或 08-20 真心跳閉合；或  
2. Steward 雙明示改 standing／升格／解凍／K9 adopt／新角度 feat-go／路徑 emit；或  
3. P6 freeze 對齊 08-19。  
4. **不因** HIT-LIFT 墓碑再寫新勝率河——須全新產品 ID。

---

## §8 驗收（本計畫書）

- [x] 全專案開問題入板（市場＋路徑＋知識＋凍結＋結構）  
- [x] 每列有最佳下一步＋可先＋可同步  
- [x] §1 決策卡可當「現在只做這些」  
- [x] 分軌：知識可先**不等價**；市場主軸不因 KH 停；路徑不改 standing  
- [x] LIVE：價／fv／core＠08-19；emit＠08-18；假 B3＠08-20  
- [x] PATH-HIT-LIFT P5 入板為 🟢 河閉  
- [x] 不創 [N]、不開訓、不假 B3、不代 commit  

*完。[I] · self-reported · r21 proposed_exec_ssot。*
