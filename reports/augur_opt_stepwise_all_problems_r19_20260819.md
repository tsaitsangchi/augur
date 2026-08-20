---
title: augur 優化——全專案逐步執行最佳下一步（可先／可同步）計畫書 r19
status: locked_exec_ssot
series: optimization_plan
round: r19
role: **後續優化執行 SSOT（全專案所有開問題）**
date: 2026-08-19
viewpoint: 2026-08-19T14:13+08:00
layer: "[I]"
depends_on:
  - archive/slim-t2/augur_deep_understanding_and_opt_plan_r19_20260819.md
  - reports/augur_project_charter_plain_zh_r19_20260819.md
understanding_adopted: audits/DEEP-UNDERSTANDING-R19-OPT-PLAN-ADOPTED-20260819.md
exec_adopted: audits/OPT-R19-ALL-PROBLEMS-ADOPTED-20260819.md
exec_locked: audits/OPT-R19-ALL-LOCKED-20260819.md
supersedes_exec: archive/slim-t2/augur_opt_stepwise_all_problems_r18_20260817.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
s1_s5_parent: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
detail_kh: reports/augur_kh_opt_stepwise_best_next_plan_20260813.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
path_opt_ops: reports/augur_path_timing_opt_ops_plan_r18_20260819.md
archive_tip: archive-20260819-b3-hist-slim-r20
prior_archive: archive-20260819-path-opt-charge-t5-ridge
self_reported: true
---

# augur 優化——全專案逐步執行最佳下一步 r19（2026-08-19 14:13）

> **LIVE 過期（2026-08-20）**：本檔寫於「08-19 還沒有價」。價／fv／core 現已到 **08-19**，出門仍 **08-18**，日曆 08-20＝假 B3。後續優化開工順序改跟 [`reports/augur_opt_stepwise_all_problems_r21_20260820.md`](augur_opt_stepwise_all_problems_r21_20260820.md)。硬門繼承仍有效；**不要**再把 08-19 當假 B3。

> **一句**：本檔＝**後續優化唯一執行計畫書**（Steward 14:13 依理解報告收成開工鎖）。每個還開著的問題都標了：**最佳下一步**、**現在可先做？**、**可與主軸同步做？**。  
> **來源**：深化理解 r19 債表 R19-01…27；吸收 r18 全板＋08-19 PATH-OPT／CHARGE-T5／封存。  
> **位階**：[I]；不創 [N]；不解凍；不假 B3；不 sim-apply；不默升格；**勿重掃假綠**。  
> **分軌保留**：市場與知識**互不等待**。路徑研究**不指揮**日更。  
> **LIVE（親查 15:22+08）**：價頂／fv／包／**出門**＝**2026-08-18** H20+H60。**08-19＝假 B3**（rc=3）。HIST＠**08-12／08-11 截面 64／64 已閉**（方向臂仍＠08-18）。下一未齊＝**08-10 缺 52**（已有 H5 窗）。P6 freeze 仍＠08-14。KH `--check`：S0 FIRE **63**；**未** `--apply`。V0／V1＠08-18 **已閉**。

本檔 **supersede** `archive/slim-t2/augur_opt_stepwise_all_problems_r18_20260817.md` 作為開工順序。理解地基＝深化理解 **r20**（r19 理解已 supersede；**本檔仍是市場開工鎖**）。r16 心跳契約仍有效。PATH-OPT 手冊仍管 M29–M35 的 θ／GO 文案。倉精化＝`reports/augur_repo_slim_opt_plan_r20_20260819.md`。

---

## §0 怎麼用（後續優化協議）

```text
每次要開工／問「下一步」：
  1) 先看 §1 決策卡（現在只做那幾件）
  2) 再看 §2 全板：狀態≠🟢／≠禁 的列
  3) 缺 GO → 停、問 Steward；有 GO／已授重用 → 做、寫 audit、改本檔狀態
  4) 細節指令 → r16 心跳／KH 板／PATH-OPT／WP 卡片／確立路徑 r17
```

| 標記 | 意思 |
|---|---|
| **最佳下一步** | 這一列若要動，**下一槍具體做什麼** |
| **可先** | 市場主軸仍在 **WAIT 無今日價** 時，**現在就可以做**（不假跑 B3＠08-19） |
| **可同步** | 可與**另一軌或主軸 WAIT** 並行；B3／L2 **開火中**則讓出 `augur_llm.lock` |
| **延後** | 主軸未閉合前不要排進工時 |
| **❄／禁** | 凍結或禁止；要動須**另句**明示 |

**Hard doors**：

```text
FZ/GATE-keep | no-fake-B3@08-19 | NF-pause | no-SIM-apply | no-promote
| 勿重掃假綠 | skip-sync-B | 誠實 econ | standing=20,60 除非雙明示
| PDF-C-no-ASR | ASR=owned_local+local_private | no-KH10 | stop-at-7 | no-relax-θ
| T0 | apply=opt-in | 有引文禁假「無此內容」 | 空包不進化
| score／p_beat／p_mkt／p_up／路徑％ ≠ 報酬％
| 市場≠指揮 KH；KH≠擋 B3；路徑≠改 standing
| 觀察≠進場 | 條件≠可交易 | 兩檔≠宇宙 | 做空≠可空
| 禁 evaluate／approve dgate_H_5/10/60/90/240（無新 GO）
| 禁塗 established（無 E5-verdict-go）；不救 H20；不放寬 DSR 95%
| 禁再送 E4 就緒 5；禁倒 canonical 31 進 prodset
| CHARGE-T5 ≠ 可交易 ≠ #14；T20／T40 不當冠
```

---

## §1 決策卡｜現在該做什麼？

視點 **2026-08-19 15:22+08** LIVE：價頂／fv／pack／**emit**＝**08-18** H20+H60；**08-19＝假 B3**。M36 刀 A **已閉**。HIST＠08-12／08-11 **已閉**。S4 其他模型 V0／V1 **已閉**。開工鎖仍＝r19。**不是** KH `--apply`。

| 問 | 答 |
|---|---|
| **全專案最佳下一步** | **等下一句 GO**。市場主軸候下一真收盤（刀 B）。08-19 不准當 as-of |
| **此刻絕對不要** | 把 as-of 設成 **08-19**（價未進）；promote；把 CHARGE-T5／兩檔％當可交易；KH `--apply` |
| **可先做（不等今日價）** | KH `--check` **已跑**（S0 FIRE 63）；V0／V1 **已跑**；E4b 鐘；P6 對帳文件；`--scan`。PATH-OPT 未閉槍**另句**才跑 |
| **可同步做** | 上列。**不要** K9／再 P6 無 GO／NF／dgate evaluate／KH `--apply` |
| **不要做** | 假 B3＠08-19；sim-apply；塗綠；換冠；默八窗出門；重掃 0812；K9 開訓；放寬 θ；`E5-evaluate-go`；倒 canonical 31；`--track other --apply`；無 GO 補 08-10；W4／W5／RS-CHARGE P1 無句混入；本鎖順便 drain S0 |

```text
paste（後續優化依本檔）:
  OPT-R19-ALL | no-fake-B3@08-19
  | knife-A=出門＠08-18 已閉；knife-B=WAIT PriceAdj≥08-19-close
  | standing=20,60 | H_TRACK=8 | no-promote | NF-pause
  | kh=check-green | E-keep | stop-at-7 | no-K9-train
  | M28=clock-WAIT | no-E5 | no-canonical-3plus1
  | archive=archive-20260819-b3-hist-slim-r20
  | emit＠08-18 H20+H60 | pack@08-18 COMPLETE | P6 freeze@08-14
  | PATH-OPT-OPS P0 adopted；觀察≠進場；兩檔≠宇宙
  | CHARGE-T5 P1 已閉；成本後 IS −64.8%；≠可交易
  | RS-CHARGE P1／TREND-PB W4 皆另句
  | slim-T5=90d-review-clock-candidate（≠rm；最早≈2026-11-17）
  | slim-T6=PME-0724-local-backup→archive
  | slim-T7=sim-chapter-draft→archive
```

**工時切法（人話）**：

1. **此刻**：M1b 出門＠08-17 **已閉**。M36 出門＠08-18 **已閉**。08-19 **無價**。  
2. **若等新價**：**不**當 08-19 為 as-of，直到 PriceAdj 真的 ≥ 那天。  
3. **路徑槍**：一次一句；不要跟下一槍 B3 搶鎖。

---

## §2 全專案開問題板

> 🟢＝本窗不當工單；❄／禁＝不要排進「可先」。

### 2.1 市場／預測／凍結／結構／路徑

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **M1a** | — | 08-14 已訓未出門 | — | — | — | 🟢 出門＠08-14 H20+H60 |
| **M1b** | — | 08-17 心跳 | — | — | — | 🟢 出門＠08-17 H20+H60 |
| **M36** | R19-01 | **08-18 已訓未出門** | — | — | — | 🟢 出門＠08-18 H20+H60 |
| **M2** | R19-03 | econ／dgate | **不修綠**；H20=dead、H60=thin；draft 閘不 evaluate | **是** | **是** | 🟢 形已誠實 |
| **M3** | — | graph tip 邊 | — | — | — | 🟢 |
| **M4** | — | H82 庫列 | 已刪；禁再插入 | — | — | 🟢 |
| **M5** | — | r19 文檔 | 開工跟**本檔** | — | — | 🟢 本輪 |
| **M6** | — | ARCHIVE | — | — | — | 🟢 `archive-20260819-b3-hist-slim-r20` |
| **M7** | R19-06 | 圖提拔熱路徑 | 另 `VERIFY-graph-cand-go` | **否** | **否** | 🔴 |
| **M8** | — | C1／CYCLE | 不編；見 K10 | **否** | — | 🟢 隔離 |
| **M9** | R19-05 | P6／長窗 | freeze 仍＠08-14；Ridge 包＠**08-18** → **缺口再開**；refit **另 GO** | 文件＝是 | 訓＝否 | 🟡 缺口 08-14 vs 08-18 |
| **M10** | R19-08 | M／β5／NF | 輕監；0812 六族**勿重掃**；殘格須點名卡 | **監看＝是**；開訓＝否 | 監看＝是 | 🟢 監看；開訓❄ |
| **M11** | R19-10 | Dividend | 另 auth | **否** | **否** | ❄ |
| **M12** | R19-10 | sim apply | **禁** | **否** | **否** | 禁 |
| **M13** | R19-09 | 循環依賴文件 | explore-only | 低優先可先讀 | 是（零碼） | 🔴 |
| **M14** | R19-09／R20-01／R20-11／R20-12／R20-13 | 倉精化（scripts／重複檔／讀序） | 依 slim r20；T0–T4＋T6＋T7 已做；T5＝90 天複審鐘**候選**（最早≈2026-11-17；產清單≠rm） | T5 開火＝否（鐘未到） | 是（零產品碼） | 🟢 T7 閉；T5 候選 |
| **M15** | R19-11 | 10–14 治權日曆 | 10 月初清單；**不假關** | 排程備忘＝是 | 是 | 🟡 |
| **M16** | R19-04 | standing 八窗殼 | **雙明示**＋改 `run_daily_asof_predict.sh` 預設 | **否** | **否** | ❄ |
| **M17** | R19-21 | dgate evaluate | 另 GO；禁塗綠草稿閘 | **否** | **否** | 禁（無 GO） |
| **M18** | R19-08／27 | 其他模型族／HIST 未齊 | 已齊近：08-18／17／14／13／12／**11**／07／07-31；下一未齊 **08-10 缺 52**（已有 H5 窗）；HIST＠08-12／08-11 **已閉**；方向臂仍＠08-18；H5 OOS ≠升格；H10 仍日曆閘；**禁**重掃 0812 | 掃描／walk＝已做；補 08-10 **另句** | 讓 B3 | 🟢 V0＠08-18；HIST＠08-11／12 64／64；H10 閘；NF❄ |
| **M19** | — | family_chk | — | — | — | 🟢 |
| **M20** | R19-07 | 升格另軌 | 可寫門檻文件；禁 SERVE-SWAP | **文件＝是** | 文件＝是 | 🟢 hold；swap❄ |
| **M21** | — | Wave-A 收官 | — | — | — | 🟢 |
| **M22** | — | RankRidge＠08-18 | 八窗 COMPLETE；B3 已寫 `prediction_values`／pp＠08-18 僅 20,60 | — | — | 🟢 訓＋出門 |
| **M23** | R19-15 | tip＋N 實現報酬 | 等價蓋過 tip＋N。E4b 鐘已掛；H60 第 1 期出場＝2026-11-13 | **否**（價未蓋） | **否** | 🔴；鐘🟢 WAIT |
| **M24** | — | 相對機率／分數看板 | 守 score／p_beat≠報酬％ | — | — | 🟢 |
| **M25** | R19-20 | 工作樹未入倉 | — | — | — | 🟢 已封存 20260819 |
| **M26** | R19-22 | HANDOFF 過期 | 不重寫 300 行 STATE；接續讀本檔 LIVE | 備忘＝是 | 是 | 🟡 |
| **M27** | R19-23 | PME 缺 map | 維持診斷；禁降閾／禁 APPLY | 文件＝是 | 是 | 🟡 |
| **M28** | R19-24 | #14 確立 | E0–E3 已閉；E4 就緒 5 耗盡；E4b **WAIT k=0** next＝2026-11-13。新角度特徵須另句點名 | E5＝禁；鐘可重讀 | 文件＝是 | 🟡 **鐘 WAIT** |
| **M29** | R19-25 | UP-PULL／RIDGE-THEN-PB | P0＋P1＠08-18 已閉（5／2）；回撤序進場 0／10；P2／emit 另句 | P2／emit＝否 | 讓 B3 | 🟡 P1 閉；emit 未開 |
| **M30** | R19-25 | TREND-PB 目錄 | P0＋W1–W3＠08-18 已閉；**W4／W5 另句** | W4＝否（須 GO） | 讓 B3 | 🟡 W3 閉 |
| **M31** | — | WATCH-PB | P0＋P1＠08-18 EXECUTED（13／6）；觀察≠進場；P2 另句 | P2＝否 | 讓 B3 | 🟡 P1 閉 |
| **M32** | — | BULL5 | P0＋P1＠08-18 已閉；9／1；∩進場＝0；P2 另句 | P2＝否 | 讓 B3 | 🟡 P1 閉 |
| **M33** | R19-25 | RS-CHARGE | **P0 已採納**；預診 7／1；**P1 探針未寫／未跑** | P1＝否（須 GO） | 讓 B3 | 🟡 P0 閉；P1 開 |
| **M34** | — | TWIN-EX | P0＋P1＠08-18 已閉；冠軍 E-charge×T5（僅兩檔）；≠可交易 | — | 讓 B3 | 🟡 P1 閉 |
| **M35** | R19-26 | CHARGE-T5 | P0＋P1＠08-18 已閉；k=10 等權；成本後 IS **−64.8%**；T20／T40 不當冠；**≠可交易、≠#14** | 探針／emit＝否 | 讓 B3 | 🟡 P1 閉；產品失敗已量出 |

### 2.2 知識／顧問

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **K0** | — | S0 KH0 breach | 記帳 63；drain 另貼 `KH-S0-apply-go` | check＝已做；apply＝否 | 避開 B3 | 🟡 FIRE 63；本鎖不 apply |
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

B3＋L2／RETRAIN-ALL＠08-13／08-14／08-17；H90 取代 H82；H5／H10／H240 開窗；L0 熱路徑；RETRAIN-ALL cron；KH 分軌；假 decline 閘；KH8 未過 θ；NF＠0812 六族 no-promote；E0–E4b；HIST-ASOF＠07-31／08-07／08-13；ARCHIVE 20260819；PATH-OPT 多數 P1＠08-18。

### Phase 1｜🟡 現在（盤中 WAIT＋可先）

| 步 | 何時 | 做 | 不做 | 驗收 |
|---|---|---|---|---|
| **1A** | — | 08-18 出門 | — | ✅ 已閉 H20+H60；#14 誠實 |
| **1B** | Steward 貼下一交易日 B3-go 且價到 | 整鏈心跳 | 無價假跑＠08-19 | tip=D；#14 誠實 |
| **1C** | **此刻可先（本窗已跑）** | KH `--check`；M2 披露 | 不開 K9／K8；不 KH `--apply` | 14:13：S0 FIRE 63／S1 FIRE／S2–S3 ok；未 apply |
| **1D** | **可先** | M9 P6 缺口文件；E4b 鐘 | evaluate／付 N／再送就緒 5 | 鐘 WAIT；P6 refit **另 GO** |
| **1G** | **本窗已閉** | V0／V1 other-verify＠08-18 | `--track other --apply`；0812 重掃；promote | V0 64／64；H5 walk 6 panel；H10 全 no_model；假 B3＠08-19 rc=3 |
| **1H** | **本窗已閉** | HIST-ASOF-apply＠08-12 `--track all` | `--force-direction`／promote／無實現窗卻 `--ic` | 截面 64／64；方向臂仍＠08-18；新訓 32（H5／H10／H90／H240） |
| **1I** | **本窗已閉** | HIST-ASOF-apply＠08-11 `--track all` | `--force-direction`／promote／無實現窗卻 `--ic` | 截面 64／64；resume 12 新訓 52；方向臂仍＠08-18 |
| **1E** | **另句** | RS-CHARGE P1＠08-18 dry-run | 當可交易；改 standing | n 與預診對上；08-19 rc=3 |
| **1F** | **另句** | TREND-PB W4＠08-18 | 倒 31；開 NF；當可交易 | T09／T10／C05 帳 |

**並行規則**：1C／1D（與已閉的 1G）在 **1A／1B 未開火** 時可同時做。1A 開始 → 長 LLM／apply／探針 **讓路**。

### Phase 2｜主軸閉合後（Steward 選一，不預設全開）

1. 下一交易日重複 1B（standing 20,60）  
2. P6 擴其餘 H_TRACK（有 plan＋GO；H20+H60 freeze＠08-14 已閉）  
3. 升格門檻文件定稿（仍 no-promote）  
4. K9 **僅**在 `K9-DOMAIN-FT-plan-adopt` 之後  
5. 圖提拔 VERIFY  
6. NF 殘格——**點名卡才 plan**  
7. standing 八窗——**僅雙明示**  
8. 新角度特徵漏斗——**另句點名**（不是 canonical 31 族內重編碼）  
9. PATH-OPT OOS walk／emit——**各一槍、各一 ID**  
10. 降週轉新產品（若要接 CHARGE-T5 教訓）——**新 ID**，不是改 k 偷渡

### Phase 3｜本檔不開

解凍 M／β5；無點名撤 NF-pause；cron B3；sim `--apply`；八窗改 standing；SERVE-SWAP；放寬 θ；depth≥8；KH10；K10 默灌預測；對話 approve 來源；整庫回填當進化；evaluate 草稿 `dgate_H_*`；假 B3；`E5-evaluate-go`；倒 31 欄進 prodset；再送 range／股利／sbl／pe／margin；把 CHARGE-T5 接顧問；把兩檔％寫進 #14。

---

## §4 工作包（開跑複製）

### WP-M36｜補出門＠08-18（刀 A；已閉）

```text
WHEN: Steward 貼 B3-go | D=2026-08-18 | horizons=20,60
DO:   bash scripts/run_daily_asof_predict.sh --date 2026-08-18 --horizons 20,60
DONT: 無價假跑@08-19; sync-B; sim-apply; 默八窗; promote
DONE: 14:17 RC=0；pv/pp＠08-18 僅 20,60；H20=dead；H60=thin；2330@H20 as_of=08-18
```

### WP-M1b｜新價心跳＠≥08-19 收盤（刀 B；須 GO）

```text
WHEN: PriceAdj(TAIEX) ≥ 該日 且 Steward 貼 B3-go
DO:   （需要時）bash scripts/run_l0_hotpath_daily.sh --date <D> --apply
      bash scripts/run_daily_asof_predict.sh --date <D> --horizons 20,60
      （L1 RC=0 且包未齊才）L2 / run_retrain_all_asof_daily.sh
DONT: 無價假跑; sync-B; sim-apply; 默八窗; promote
DONE: RC=0 + EXECUTED + #14 誠實
```

### WP-M25｜未入倉清單（已閉）

`archive-20260819-b3-hist-slim-r20` 為現行 tip（上一點＝`archive-20260819-path-opt-charge-t5-ridge`）。本 WP 不當工單。

### WP-KD｜KH 巡檢（可同步；本窗已跑）

```text
WHEN: 任意；避開 B3 開火
DO:   python scripts/kh_ingest_trigger.py --check
DONT: 無 GO 卻 --apply; 日曆假進化
DONE: 14:13 S0 FIRE kh0_breach=63；S1 FIRE delta=63；S2 eligible 146338；S3 zh/en lag=0；未 --apply
```

### WP-M18｜其他模型 V0／V1（可先；本窗已閉）

```text
WHEN: 主軸 WAIT；避開 B3 開火
DO:   check_asof_ready --scan
      verify_asof_families.py --date 2026-08-18
      run_asof_collect_train_verify.sh --date 2026-08-18 --dry-plan --track other
      verify_asof_families.py --walk --oos --horizon 5 --limit 6
      verify_asof_families.py --walk --oos --horizon 10 --limit 4
DONT: --track other --apply; 重掃 0812; promote; 假 B3@08-19
DONE: 14:40 V0 64/64；H5 新 panel 08-10 正 IC ≠升格；H10 全 no_model
      audits/S1S5-OTHER-VERIFY-0818-EXECUTED-20260819.md
      reports/augur_s1s5_asof_verify_best_next_r19_20260819.md
```

### WP-HIST-0812｜歷史 as-of＠08-12（本窗已閉）

```text
WHEN: Steward 貼 HIST-ASOF-apply | date=2026-08-12 | track=all | no-force-direction
DO:   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-12 --apply --track all
DONT: --force-direction; promote; 假 B3@08-19; 無實現窗卻 --ic
DONE: 15:03 RC=0；64/64；resume 32 新訓 32；方向臂仍＠08-18
      audits/HIST-ASOF-0812-EXECUTED-20260819.md
```

### WP-HIST-0811｜歷史 as-of＠08-11（本窗已閉）

```text
WHEN: Steward 貼 HIST-ASOF-apply | date=2026-08-11 | track=all | no-force-direction
DO:   bash scripts/run_asof_collect_train_verify.sh --date 2026-08-11 --apply --track all
DONT: --force-direction; promote; 假 B3@08-19; 無實現窗卻 --ic
DONE: 15:22 RC=0；64/64；resume 12 新訓 52；方向臂仍＠08-18
      audits/HIST-ASOF-0811-EXECUTED-20260819.md
```

### WP-K0｜S0 drain（須另句；本鎖不開）

```text
WHEN: Steward 明示 KH-S0-apply-go（且非 B3 開火）
DO:   python scripts/kh_ingest_trigger.py --apply
DONT: 把 OPT-R19-ALL 當授權去 apply；抬 >KH2
DONE: kh0_breach 63→0（尚未跑）
```

### WP-M28｜經濟確立路徑（就緒 5 耗盡；鐘 WAIT）

```text
WHEN: 任意重讀；新角度另句
DO:   python scripts/report_live_oos_clock.py --origin 2026-08-14 --h 60
DONT: 算未實現 PnL；E5-evaluate-go；再送就緒 5；倒 31 欄進 prodset；放寬 0.6
DONE: 鐘已掛；k=0；next_due=2026-11-13
```

### WP-PATH｜路徑未閉槍（各須自己的 GO）

詳 `reports/augur_path_timing_opt_ops_plan_r18_20260819.md` §5–§6。本檔只鎖開工順序：**不要一次開兩槍**；優先建議若 Steward 要動路徑＝`RS-CHARGE-probe-go` 或等刀 A／B。

---

## §5 與深化理解債表（R19-* → 本板）

| R19 | 本板 | 本窗處置 |
|---|---|---|
| 01 08-18 出門 | M36 | 🟢 EXECUTED |
| 02 ≥08-19 心跳 | 1B | 🟡 WAIT 價 |
| 03 econ | M2／M17 | 披露；evaluate 禁 |
| 04 八窗殼 | M16 | ❄ |
| 05 P6 | M9 | 🟡 缺口 08-14 vs 08-18 |
| 06 圖提拔 | M7 | 延後 |
| 07 升格 | M20 | 可先文件；禁 swap |
| 08 NF | M10／M18 | 監看∥；禁重掃 |
| 09 scripts／倉精化 | M13／M14 | T0–T4＋T6＋T7 已閉；T5 複審鐘候選 |
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
| 20 未入倉 | M25 | 🟢 封存 20260819 |
| 21 dgate draft | M17 | 禁 |
| 22 HANDOFF | M26 | 備忘 |
| 23 PME | M27 | 診斷；禁 APPLY |
| 24 #14 | M28 | E4 耗盡；E4b WAIT |
| 25 PATH 未閉 | M29–M33 | 另句；P1 多數已閉 |
| 26 CHARGE-T5 成本 | M35 | 🟢 已量出失敗邊界 |
| 27 HIST 未齊 | M18 | 08-12／08-11 已閉；下一＝08-10 另句 |

---

## §6 細節板（本檔不取代長指令）

| 用途 | 路徑 |
|---|---|
| 精要讀序 | `reports/SSOT_READ_ORDER.md` |
| 現行理解 | `reports/augur_deep_understanding_and_opt_plan_r20_20260819.md`（r19 理解已 supersede） |
| r19 理解（封存） | `archive/slim-t2/augur_deep_understanding_and_opt_plan_r19_20260819.md` |
| 倉精化（M14） | `reports/augur_repo_slim_opt_plan_r20_20260819.md` |
| 人話憲章 | `reports/augur_project_charter_plain_zh_r19_20260819.md` |
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
| 前一執行板 | `archive/slim-t2/augur_opt_stepwise_all_problems_r18_20260817.md`（已被本檔 supersede） |

衝突：開工順序與「可先／可同步」**以本檔為準**；殼指令與 GO 文案以長板／audit 為準。r17／r18 LIVE 段（價頂／emit）**過期**，以本檔 LIVE 為準。

---

## §7 何時刷新（r20／改本檔）

1. B3＠08-18 閉合，或下一真交易日心跳閉合；或  
2. Steward 雙明示改 standing／升格／解凍／K9 adopt／新角度 feat-go／路徑 emit；或  
3. P6 freeze 對齊 08-18。  
4. **不因** r20 理解／slim T0 而改本檔為非 LOCKED——精化有自己的計畫書，市場鎖仍這裡。

---

## §8 驗收（本計畫書）

- [x] 全專案開問題入板（市場＋路徑＋知識＋凍結＋結構）  
- [x] 每列有最佳下一步＋可先＋可同步  
- [x] §1 決策卡可當「現在只做這些」  
- [x] 分軌：知識可先**不等價**；市場主軸不因 KH 停；路徑不改 standing  
- [x] 吸收 PATH-OPT／CHARGE-T5／emit-gap＠08-18；聲明：後續優化**依本檔**  
- [x] Steward 14:13「後續依此優化」→ LOCKED（nav-only；KH `--check` 已跑；未 apply／未 B3）  

*完。[I] · r19 全專案逐步執行 SSOT · LOCKED。*
