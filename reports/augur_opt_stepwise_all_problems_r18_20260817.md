---
title: augur 優化——全專案逐步執行最佳下一步（可先／可同步）計畫書 r18
status: adopted_exec_ssot
series: optimization_plan
round: r18
role: **後續優化執行 SSOT（全專案所有開問題）**
date: 2026-08-17
viewpoint: 2026-08-18T14:55+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r17_20260817.md
  - reports/augur_project_charter_plain_zh_r17_20260817.md
understanding_adopted: audits/DEEP-UNDERSTANDING-R17-OPT-PLAN-ADOPTED-20260817.md
exec_adopted: audits/OPT-R18-ALL-PROBLEMS-ADOPTED-20260817.md
supersedes_exec: reports/augur_opt_stepwise_all_problems_r17_20260817.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
s1_s5_parent: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
detail_kh: reports/augur_kh_opt_stepwise_best_next_plan_20260813.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
archive_tip: archive-20260819-path-opt-charge-t5-ridge
prior_archive: archive-20260818-b3-retrain-force-hist-oos
self_reported: true
---

# augur 優化——全專案逐步執行最佳下一步 r18（2026-08-18 14:55）

> **一句**：本檔＝**後續優化唯一執行計畫書**。每個還開著的問題都標了：**最佳下一步**、**現在可先做？**、**可與主軸同步做？**。  
> **來源**：深化理解 r17 債表 R17-01…23；吸收本日 M1a 出門、E0–E4b。  
> **位階**：[I]；不創 [N]；不解凍；不假 B3；不 sim-apply；不默升格；**勿重掃假綠**。  
> **分軌保留**：市場與知識**互不等待**。  
> **LIVE（親查 14:55+08）**：價頂／fv／包＝**2026-08-17**。08-18＝假 B3。RETRAIN-ALL **force** 已閉。方向臂活鎖＝08-17。出門仍＝本晨 B3 H20+H60。P6 freeze 仍＠08-14。KH S0–S3 ok。下一未齊＝08-12 缺 32（無已實現窗）。V1 H5 OOS 已跑；**H10 OOS walk 全 no_model**（日曆閘：08-07 後僅 6 日，H10 須 11）。

本檔 **supersede** `reports/augur_opt_stepwise_all_problems_r17_20260817.md` 作為開工順序。理解地基仍＝深化理解 r17（不必重寫長文）。r16 心跳契約仍有效。

---

## §0 怎麼用（後續優化協議）

```text
每次要開工／問「下一步」：
  1) 先看 §1 決策卡（現在只做那幾件）
  2) 再看 §2 全板：狀態≠🟢／≠禁 的列
  3) 缺 GO → 停、問 Steward；有 GO／已授重用 → 做、寫 audit、改本檔狀態
  4) 細節指令 → r16 心跳／KH 板／WP 卡片／確立路徑 r17
```

| 標記 | 意思 |
|---|---|
| **最佳下一步** | 這一列若要動，**下一槍具體做什麼** |
| **可先** | 市場主軸仍在 **WAIT 無今日價** 時，**現在就可以做**（不假跑 B3＠08-17） |
| **可同步** | 可與**另一軌或主軸 WAIT** 並行；B3／L2 **開火中**則讓出 `augur_llm.lock` |
| **延後** | 主軸未閉合前不要排進工時 |
| **❄／禁** | 凍結或禁止；要動須**另句**明示 |

**Hard doors**：

```text
FZ/GATE-keep | no-fake-B3@08-19 | NF-pause | no-SIM-apply | no-promote
| 勿重掃假綠 | skip-sync-B | 誠實 econ | standing=20,60 除非雙明示
| PDF-C-no-ASR | ASR=owned_local+local_private | no-KH10 | stop-at-7 | no-relax-θ
| T0 | apply=opt-in | 有引文禁假「無此內容」 | 空包不進化
| score／p_beat／p_mkt／p_up ≠ 報酬％
| 市場≠指揮 KH；KH≠擋 B3
| 禁 evaluate／approve dgate_H_5/10/60/90/240（無新 GO）
| 禁塗 established（無 E5-verdict-go）；不救 H20；不放寬 DSR 95%
| 禁再送 E4 就緒 5；禁倒 canonical 31 進 prodset
```

---

## §1 決策卡｜現在該做什麼？

視點 **2026-08-19 09:15+08** LIVE：價頂／fv／pack＝**08-18**；**08-19＝假 B3**。Steward 鎖已含 W3 閉。B3 emit＠08-18、W4、W5、P2、P6 refit 皆另句。

| 問 | 答 |
|---|---|
| **全專案最佳下一步** | **等下一句 GO**。本鎖不開工。P6 freeze 缺口（08-14 vs 包 08-17）須另 GO |
| **此刻絕對不要** | 把 as-of 設成 **08-19**（價未進）；開 W4／W5；promote |
| **可先做（不等今日價）** | KH `--check`；E4b 鐘；P6 對帳；`--scan`。`--walk --oos` H5 **已閉**；H10 全 no_model（候價或另 HIST 更早 D）。KH apply／P6 refit／HIST apply **另句** |
| **可同步做** | 上列。B3 開火時讓出 LLM。**不要** K9／再 P6 無 GO／NF／dgate evaluate／KH `--apply` |
| **不要做** | 假 B3＠08-19；sim-apply；塗綠；換冠；默八窗出門；重掃 0812；K9 開訓；放寬 θ；`E5-evaluate-go`；再送就緒 5；`--track other --apply`（殼會 rc=6）；無 GO 補 08-12；W4／W5 無句混入 |

```text
paste（後續優化依本檔）:
  OPT-R18-ALL | no-fake-B3@08-19
  | knife-B=出門＠08-17 已閉；08-18 價已在；B3 emit＠08-18 另句
  | standing=20,60 | H_TRACK=8 | no-promote | NF-pause
  | kh=check-green | E-keep | stop-at-7 | no-K9-train
  | M28=clock-WAIT | no-E5 | no-canonical-3plus1
  | RETRAIN-ALL-force＠08-17 已閉
  | archive=archive-20260819-path-opt-charge-t5-ridge
  | UP-PULL P0 adopted policy=strict k=10
  | P1 probe＠08-18 EXECUTED n_long=5 n_short=2
  | Ridge 八窗均分 Top10 標等回撤 copy-only＠08-18（∩進場＝0；未接 live）
  | TREND-PB P0 adopted；W1＋W2＋W3＠08-18 EXECUTED；W4／W5 另句
  | WATCH-PB P0 adopted；P1 probe＠08-18 EXECUTED n=13／6；觀察≠進場
  | RS-CHARGE P0 adopted；無L-C；觀察≠進場；P1 另句
  | TWIN-EX P0＋P1＠08-18 EXECUTED；charge×T5 仍冠（僅兩檔）；≠可交易
  | PATH-OPT-OPS P0 adopted；觀察≠進場；兩檔≠宇宙；未閉槍另句
  | BULL5 P0＋P1＠08-18 EXECUTED n=9／1；∩進場＝0；不用累積遞減
  | CHARGE-T5 P0＋P1＠08-18 EXECUTED；k=10 等權；無成本兩窗正；成本後 IS −64.8%；≠可交易
```

**工時切法（人話）**：

1. **此刻**：M1b 出門＠08-17 **已閉**。RETRAIN-ALL force＠08-17 **已閉**。S0／S3 **已閉**。HIST-ASOF＠08-07／08-13 **已閉**。P6＠08-17 **另句**。下一未齊 08-12 **另句 HIST-ASOF-apply**。  
2. **08-18 價已在**：B3 emit H20+H60 **另貼 B3-go**；#14 誠實；no-promote。  
3. **08-19 價未進**：**不**當 as-of。W4／W5 **另句**。

---

## §2 全專案開問題板

> 🟢＝本窗不當工單；❄／禁＝不要排進「可先」。

### 2.1 市場／預測／凍結／結構

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **M1a** | R17-01 | 08-14 已訓未出門 | — | — | — | 🟢 出門＠08-14 H20+H60 |
| **M1b** | R17-02 | 08-17 心跳 | — | — | — | 🟢 出門＠08-17 H20+H60 |
| **M2** | R17-03 | econ／dgate | **不修綠**；H20=dead、H60=thin；draft 閘不 evaluate | **是** | **是** | 🟢 形已誠實 |
| **M3** | — | graph tip 邊 | — | — | — | 🟢 |
| **M4** | — | H82 庫列 | 已刪；禁再插入 | — | — | 🟢 |
| **M5** | — | r17／r18 文檔 | 開工跟**本檔** | — | — | 🟢 本輪 |
| **M6** | — | ARCHIVE 後入倉 | — | — | — | 🟢 `archive-20260819-path-opt-charge-t5-ridge` |
| **M7** | R17-06 | 圖提拔熱路徑 | 另 `VERIFY-graph-cand-go` | **否** | **否** | 🔴 |
| **M8** | R17-18 市場側 | C1／CYCLE | 不編；見 K10 | **否** | — | 🟢 隔離 |
| **M9** | R17-05 | P6／長窗 | freeze 仍＠08-14；Ridge 包＠08-17 → **缺口再開**；refit **另 GO** | 文件＝是 | 訓＝否 | 🟡 缺口 08-14 vs 08-17 |
| **M10** | R17-08／10 | M／β5／NF | 輕監；0812 六族**勿重掃**；殘格須點名卡 | **監看＝是**；開訓＝否 | 監看＝是 | 🟢 監看；開訓❄ |
| **M11** | R17-10 | Dividend | 另 auth | **否** | **否** | ❄ |
| **M12** | R17-10 | sim apply | **禁** | **否** | **否** | 禁 |
| **M13** | R17-09 | 循環依賴文件 | explore-only | 低優先可先讀 | 是（零碼） | 🔴 |
| **M14** | R17-09 | scripts 冗餘 | #29 另計畫 | **否** | **否** | 🔴 |
| **M15** | R17-11 | 10–14 治權日曆 | 10 月初清單；**不假關** | 排程備忘＝是 | 是 | 🟡 |
| **M16** | R17-04 | standing 八窗殼 | **雙明示**＋改 `run_daily_asof_predict.sh` 預設 | **否** | **否** | ❄ |
| **M17** | R17-21 | dgate evaluate | 另 GO；禁塗綠草稿閘 | **否** | **否** | 禁（無 GO） |
| **M18** | R17-08 | 其他模型族 | 已齊＝07-31／08-07／08-13／08-14／08-17；價頂 8×8 **force 重 fit** 13:44；下一未齊 08-12 缺 32；V1 H5 OOS 近 0；**H10 OOS 全 no_model**（08-07 後僅 6 日）；**禁**重掃 0812 | 掃描／IC／08-07＋08-13 apply／H5 walk／force／H10 walk＝**已做**；開新族＝否；補 08-12／06-30 **另句** | 讓 B3 | 🟢 V0＋V1 H5；H10 日曆閘；NF❄ |
| **M19** | — | family_chk | — | — | — | 🟢 |
| **M20** | R17-07 | 升格另軌 | 可寫門檻文件；禁 SERVE-SWAP | **文件＝是** | 文件＝是 | 🟢 hold；swap❄ |
| **M21** | — | Wave-A 收官 | — | — | — | 🟢 |
| **M22** | — | RankRidge＠08-17 | 八窗 **force 重 fit** 13:44；出門仍本晨 B3 20,60（未重 emit） | — | — | 🟢 |
| **M23** | R17-15 | tip＋N 實現報酬 | 等價蓋過 tip＋N。E4b 鐘已掛；H60 第 1 期出場＝2026-11-13 | **否**（價未蓋） | **否** | 🔴；鐘🟢 WAIT |
| **M24** | — | 相對機率／分數看板 | 守 score／p_beat≠報酬％ | — | — | 🟢 |
| **M25** | R17-20 | 工作樹未入倉 | — | — | — | 🟢 已封存 20260818 |
| **M26** | R17-22 | HANDOFF 過期 | 不重寫 300 行 STATE；接續讀本檔 LIVE | 備忘＝是 | 是 | 🟡 |
| **M27** | R17-23 | PME 缺 map | 維持診斷；禁降閾／禁 APPLY | 文件＝是 | 是 | 🟡 |
| **M28** | #14 確立 | 往「證明能賺錢」 | E0–E3 已閉；E4 就緒 5 耗盡（3＋1 canonical 停）；E4b **WAIT k=0** next＝2026-11-13。新角度特徵須另句點名 | E5＝禁；鐘可重讀 | 文件＝是 | 🟡 **鐘 WAIT** |
| **M29** | UP-PULL | 長線結構×短線進出做多／做空 Top10 | P0＋P1＠08-18 已閉（5／2）；標註 Ridge copy-only 已閉；**RIDGE-THEN-PB＠08-18 已閉**（強／弱池各10；進場 0／0）；P2／P1b／P3／P4 另句 | P2／emit＝否 | 讓 B3 | 🟡 P1＋標註＋RIDGE-THEN-PB 閉；emit 未開 |
| **M30** | TREND-PB 目錄 | 市場同類規則閉集驗証（T01–T12＋C01–C07） | P0 已採納；**W1＋W2＋W3＠08-18 已閉**（C04∩T01＝0；T07∩T01＝0；T04 做多＝0）；W4／W5 另句 | W4＝否 | 讓 B3 | 🟡 W3 閉；W4／W5 未開 |
| **M31** | WATCH-PB | 已離高、短窗仍衝——全宇宙觀察篩 | P0 已採納；**P1＠08-18 EXECUTED**（觀察多 13／空 6；∩進場＝0）；P2 另句 | P2＝否 | 讓 B3 | 🟡 P1 閉；觀察≠進場 |
| **M32** | BULL5 | 長線多頭 × 5 日回跌 | **P0＋P1＠08-18 已閉**；閘＝H10…H240 全＞0 ∧ H5＜0；做多 9／空 1；∩進場＝0；奇鋐不在；**P2 另句** | P2＝否 | 讓 B3 | 🟡 P1 閉 |
| **M33** | RS-CHARGE | 相對強×長窗多×短窗仍衝（奇鋐／研華交集） | **P0 已採納**；Ridge Top10∩L-A∩L-D∩H5>0∩H10>0；無 L-C；預診 7／1（含 3017＋2395）；**P1 另句** | P1＝否 | 讓 B3 | 🟡 P0 閉；觀察≠進場 |
| **M34** | TWIN-EX | 奇鋐／研華進出最佳化（不要抱牢） | **P0＋P1＠08-18 已閉**；冠軍 E-charge×T5；**≠可交易、≠宇宙**；宇宙外推＝CHARGE-T5 P1 **已閉** | — | 讓 B3 | 🟡 P1 閉 |
| **M35** | CHARGE-T5 | 衝勢 5 日進出（新規則模型） | **P0＋P1＠08-18 已閉**；E-charge×T5、k=10 等權；IS 籃 240／+43.8%（成本後 **−64.8%**）；OOS +2181%（成本後 +210%；不當預期）；T20／T40 不當冠；兩檔無 k 對上舊帳；**≠可交易、≠#14** | 探針／emit＝否 | 讓 B3 | 🟡 P1 閉 |

### 2.2 知識／顧問

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **K0** | — | S0 KH0 breach | — | — | — | 🟢 drain＠09:07 218→0 |
| **K1** | — | S3 zh lag | — | — | — | 🟢 concordance＠09:08 zh 2→0 |
| **K2** | — | ingest 階梯 | 守 apply 選開 | — | — | 🟢 |
| **K3** | R17-19 | AUTO-LIFT | 常駐即可；**禁抬 >KH2** | **否** | — | 🟢／禁抬層 |
| **K4** | R17-14 | 私有 smoke | 回歸可重跑 | 抽樣＝是 | 是 | 🟢 |
| **K5** | R17-12 | Doc1 純圖 | **hold**；不 OCR 硬開 | **否** | — | 🟢 hold |
| **K6** | R17-14 | ASR 對聽 | 可選抽樣 | 是 | 是（輕） | 🟢 |
| **K7** | — | 8b 產品口吻 | 守 8b＋960 | — | — | 🟢 |
| **K8** | R17-16 | KH8 discrim | **E-keep／stop-at-7** | **否** | **否** | ❄ |
| **K9** | R17-17 | 他域 FT | 另 `adopt` 才訓；現 **plan-only** | **否** | **否** | 🔴 |
| **K10** | R17-18 | C1→feat | 另 GO；禁默加權 predict | **否** | **否** | 🔴 隔離 |
| **K11** | R17-13 | `.msg`／rar | skip-hold 或另 plan | **否** | **否** | 🔴 |
| **K12** | — | KH10 | — | **否** | **否** | 禁（≠ H10 交易日） |
| **K16** | — | 假 decline 閘 | 產品行為已修 | — | — | 🟢 |
| **K17** | — | 閘入倉 | 焦點改 M25 | — | — | 🟢 |

---

## §3 逐步執行序列（Phase）

### Phase 0｜✅ 已閉（本檔不當工單）

B3＋L2／RETRAIN-ALL＠08-13 與＠08-14（8×8）；H90 取代 H82；H5／H10／H240 開窗；L0 熱路徑；RETRAIN-ALL cron；KH 分軌；假 decline 閘；KH8 A2-L3 未過 θ；NF＠0812 六族 no-promote。  
**本日閉**：M1a 出門＠08-14；M1b 出門＠08-17 H20+H60；E0–E4b；HIST-ASOF＠07-31；HIST-ASOF＠08-07；HIST-ASOF＠08-13；ARCHIVE；P6 freeze→08-14；RETRAIN-ALL 包＠08-17；**RETRAIN-ALL force**＠08-17（8×8＋方向臂；`--no-resume`）。

### Phase 1｜🟡 現在（盤中 WAIT＋可先）

| 步 | 何時 | 做 | 不做 | 驗收 |
|---|---|---|---|---|
| **1A** | — | 08-14 出門 | — | ✅ 已閉 |
| **1B** | — | 08-17 出門 | — | ✅ 已閉 |
| **1C** | Steward 貼下一交易日 B3-go 且價到 | 08-18 整鏈心跳 | 無價假跑 | tip=D；#14 誠實 |
| **1D** | **此刻可先** | KH `--check`；M2 披露 | 不開 K9／K8；不 KH `--apply`（無新 GO） | ✅ 09:08：S0–S3 ok；priority_hit=∅ |
| **1E** | **可先** | M9 P6 缺口 08-14 vs 包 08-17；E4b 鐘 | evaluate／付 N／再送就緒 5／放寬 ρ | 鐘 WAIT；P6 refit **另 GO** |
| **1F** | **本窗已跑** | V1 `--ic --oos`／`--walk --oos` H5＠08-04…08-07（stamp 07-31）；`--walk --horizon 10` | 開 NF／promote／把同日 IC 當確立／把 H10 全 no_model 當失敗 | H5 四 panel 近 0／偏負；H10 四 panel 全 no_model（日曆閘，不是假綠） |
| **1G** | **本窗已閉** | HIST-ASOF-apply＠08-07 `--track all`；同日 IC 不採 | `--force-direction`／promote | 截面 64／64；方向臂仍＠08-17 |
| **1H** | **本窗已閉** | HIST-ASOF-apply＠08-13 `--track all`（補 8×H10） | `--force-direction`／promote／無實現窗卻 `--ic` | 截面 64／64；無已實現窗 |
| **1I** | **本窗已閉** | RETRAIN-ALL force＠08-17 `--track all --force`（方向臂鎖價頂＋八窗重 fit） | 假 B3＠08-18／promote／重 emit／P6／evaluate dgate | RC=0；pack_complete；standing 仍 20,60 |
| **1J** | **P1 已閉** | UP-PULL 探針＠08-18 strict both k=10 | 當可交易／可空；soft-fill 混入 v1；改 standing | n_long=5／n_short=2；假 B3＠08-19 rc=3 |
| **1K** | **W1＋W2 已閉** | TREND-PB 路徑＋指標族＠08-18 | 當可交易；倒 31；開 NF；W3 混入 | W2：T04 做多＝0；C04∩T01＝0；T12＝1 |
| **1L** | **W3 已閉** | TREND-PB T07＠08-18（Elder 兩屏近似） | 宣稱＝三屏原作；倒 MACD；W4 混入 | T07∩T01 做多＝0；pass 67／19 |

**並行規則**：1D／1E／1F 在 **1B 未開火** 時可同時做。1B 開始 → 長 LLM／apply **讓路**。

### Phase 2｜主軸閉合後（Steward 選一，不預設全開）

1. 下一交易日重複 1B（standing 20,60）  
2. P6 擴其餘 H_TRACK（有 plan＋GO；H20+H60 freeze＠08-14 已閉）  
3. 升格門檻文件定稿（仍 no-promote）  
4. K9 **僅**在 `K9-DOMAIN-FT-plan-adopt` 之後  
5. 圖提拔 VERIFY  
6. NF 殘格——**點名卡才 plan**  
7. standing 八窗——**僅雙明示**  
8. 新角度特徵漏斗——**另句點名**（不是 canonical 31 族內重編碼）

### Phase 3｜本檔不開

解凍 M／β5；無點名撤 NF-pause；cron B3；sim `--apply`；八窗改 standing；SERVE-SWAP；放寬 θ；depth≥8；KH10；K10 默灌預測；對話 approve 來源；整庫回填當進化；evaluate 草稿 `dgate_H_*`；假 B3；`E5-evaluate-go`；倒 31 欄進 prodset；再送 range／股利／sbl／pe／margin。

---

## §4 工作包（開跑複製）

### WP-M1b｜新價心跳＠≥08-17（刀 B；須 GO）

```text
WHEN: PriceAdj(TAIEX) ≥ 2026-08-17 且 Steward 貼 B3-go
DO:   （需要時）bash scripts/run_l0_hotpath_daily.sh --date 2026-08-17 --apply
      bash scripts/run_daily_asof_predict.sh --date 2026-08-17 --horizons 20,60
      （L1 RC=0 且包未齊才）L2 / run_retrain_all_asof_daily.sh
DONT: 無價假跑; sync-B; sim-apply; 默八窗; promote
DONE: RC=0 + EXECUTED + #14 誠實
```

### WP-M25｜未入倉清單（已閉）

`archive-20260819-path-opt-charge-t5-ridge` 已 push（上一點＝`archive-20260818-b3-retrain-force-hist-oos`）。本 WP 不當工單。

### WP-KD｜KH 巡檢（可同步；本窗已跑）

```text
WHEN: 任意；避開 B3 開火
DO:   python scripts/kh_ingest_trigger.py --check
DONT: 無 GO 卻 --apply; 日曆假進化
DONE: 09:08 終檢：S0–S3 ok；priority_hit=∅
```

### WP-K0｜S0 drain（已閉）

```text
WHEN: Steward 明示 KH-S0-apply-go（且非 B3 開火）
DO:   python scripts/kh_ingest_trigger.py --apply
DONT: 無 GO 卻 apply；抬 >KH2；本槍順便 S3
DONE: 09:07 S0 kh0_breach 218→0；seeded=218 advanced=0
```

### WP-M28｜經濟確立路徑（就緒 5 耗盡；鐘 WAIT）

```text
WHEN: 任意重讀；新角度另句
DO:   python scripts/report_live_oos_clock.py --origin 2026-08-14 --h 60
DONT: 算未實現 PnL；E5-evaluate-go；再送就緒 5；倒 31 欄進 prodset；放寬 0.6
DONE: 鐘已掛；k=0；next_due=2026-11-13；K=4≈2027 年中
NOTE: 現役 2021 在位淨≤基準（E3）；34 欄是捆不是單欄
```

---

## §5 與深化理解債表（R17-* → 本板）

| R17 | 本板 | 本窗處置 |
|---|---|---|
| 01 08-14 出門 | M1a | 🟢 EXECUTED |
| 02 08-17 心跳 | M1b | 🟢 出門＠08-17 |
| 03 econ | M2／M17 | 披露；evaluate 禁 |
| 04 八窗殼 | M16 | ❄ |
| 05 P6 | M9 | 🟡 缺口 08-14 vs 包 08-17 |
| 06 圖提拔 | M7 | 延後 |
| 07 升格 | M20 | 可先文件；禁 swap |
| 08 NF | M10／M18 | 監看∥；禁重掃 |
| 09 scripts | M13／M14 | 延後 |
| 10 M／sim／Dividend | M10–12 | ❄／禁 |
| 11 日曆 | M15 | 排程 |
| 12 Doc1 | K5 | hold |
| 13 msg／rar | K11 | skip-hold |
| 14 私有／ASR | K4／K6 | 可選抽樣∥ |
| 15 tip+N | M23 | 延後；鐘已掛 |
| 16 KH8 | K8 | ❄ E-keep |
| 17 K9 | K9 | 延後／另 adopt |
| 18 K10 | K10 | 隔離 |
| 19 AUTO-LIFT>KH2 | K3 | 禁 |
| 20 未入倉 | M25 | 🟢 封存 20260818 |
| 21 dgate draft | M17 | 禁 |
| 22 HANDOFF | M26 | 備忘 |
| 23 PME | M27 | 診斷；禁 APPLY |
| — #14 確立路徑 | M28 | E4 耗盡；E4b WAIT k=0 |
| — UP-PULL 長短進出 | M29 | P0＋P1＠08-18 已閉；P2 另句 |
| — TREND-PB 同類目錄 | M30 | P0＋W1＋W2＋W3＠08-18 已閉；W4／W5 另句 |
| — WATCH-PB 觀察篩 | M31 | P0＋P1＠08-18 已閉（13／6）；P2 另句 |
| — BULL5 多頭×5日回 | M32 | P0＋P1＠08-18 已閉；9／1；∩進場＝0 |
| — RS-CHARGE 相對強仍衝 | M33 | P0 已採納；預診 7／1＠08-18；P1 另句 |
| — TWIN-EX 兩檔進出（不要抱牢） | M34 | P0＋P1＠08-18 已閉；charge×T5；≠可交易 |
| — CHARGE-T5 衝勢 5 日進出 | M35 | P0＋P1＠08-18 已閉；成本後 IS 負；≠可交易 |

---

## §6 細節板（本檔不取代長指令）

| 用途 | 路徑 |
|---|---|
| 理解地基 | `reports/augur_deep_understanding_and_opt_plan_r17_20260817.md` |
| 人話憲章 | `reports/augur_project_charter_plain_zh_r17_20260817.md` |
| S1→S5 閉環運轉 | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md` |
| KH 長板 | `reports/augur_kh_opt_stepwise_best_next_plan_20260813.md` |
| L0 | `reports/augur_l0_hotpath_daily_plan_20260814.md` |
| L2 | `reports/augur_daily_retrain_l2_all_rank_plan_20260812.md` |
| NF 殘格 | `audits/NF-0812-RESIDUAL-NAME-CARD-20260813.md` |
| PME 診斷 | `reports/augur_pme_gate_diagnosis_20260814.md` |
| #14 確立路徑 | `reports/augur_econ_prove_edge_plan_r17_20260817.md` |
| E3 量產 | `reports/augur_econ_e3_measure_r17_20260817.md` |
| E4 短名單 | `reports/augur_econ_e4_shortlist_r17_20260817.md` |
| E4 三墓碑 | range／股利／sbl 三份 `reports/augur_econ_e4_feat_*_r17_20260817.md` |
| E4b 鐘 | `reports/augur_econ_e4b_clock_r17_20260817.md` |
| as-of 刀 | `reports/augur_s1s5_asof_verify_best_next_r18_20260817.md` |
| 路徑／進出最佳化操作手冊（M29–M35） | `reports/augur_path_timing_opt_ops_plan_r18_20260819.md`（P0 已採納；未閉槍另句） |
| 長線×短線進出 Top10 | `reports/augur_uptrend_pullback_ls_top10_plan_r18_20260819.md`（P0＋P1＠08-18 已閉） |
| 市場同類規則閉集 | `reports/augur_trend_pullback_model_catalog_verify_plan_r18_20260819.md`（P0＋W1–W3＠08-18 已閉；W4／W5 另句） |
| 已離高短窗仍衝觀察篩 | `reports/augur_watch_pullback_inband_plan_r18_20260819.md`（P0＋P1＠08-18 已閉） |
| 長線多頭×5日回跌 | `reports/augur_bull5_hstack_pullback_plan_r18_20260819.md`（P0＋P1＠08-18 已閉） |
| 相對強×短窗仍衝（奇鋐／研華交集） | `reports/augur_rs_charge_qihong_yanhua_plan_r18_20260819.md`（P0 已採納；探針另句） |
| 奇鋐／研華進出最佳化（不要抱牢） | `reports/augur_twin_ex_qihong_yanhua_plan_r18_20260819.md`（P0＋P1 已閉；宇宙＝CHARGE-T5 P1 已閉） |
| 奇鋐／研華符合條件與歷史進出 | `reports/augur_qihong_yanhua_conditions_ops_plan_r18_20260819.md`（E-charge×T5 逐筆報酬；≠可交易） |
| 衝勢 5 日進出（新規則模型） | `reports/augur_charge_t5_model_plan_r18_20260819.md`（CHARGE-T5-v1 **P0＋P1＠08-18 已閉**；成本後 IS 負；≠可交易） |
| 前一執行板 | `reports/augur_opt_stepwise_all_problems_r17_20260817.md`（已被本檔 supersede） |

衝突：開工順序與「可先／可同步」**以本檔為準**；殼指令與 GO 文案以長板／audit 為準。深化理解 r17 的 LIVE 段（emit 仍寫 08-13）**過期**，以本檔 LIVE 為準。

---

## §7 何時刷新（r19／改本檔）

1. 下一交易日 B3（PriceAdj≥08-18）閉合；或  
2. Steward 雙明示改 standing／升格／解凍／K9 adopt／新角度 feat-go；或  
3. P6 freeze 對齊 08-17。

---

## §8 驗收（本計畫書）

- [x] 全專案開問題入板（市場＋知識＋凍結＋結構）  
- [x] 每列有最佳下一步＋可先＋可同步  
- [x] §1 決策卡可當「現在只做這些」  
- [x] 分軌：知識可先**不等價**；市場主軸不因 KH 停  
- [x] 吸收本日 M1a／E0–E4b；聲明：後續優化**依本檔**  

*完。[I] · r18 全專案逐步執行 SSOT。*
