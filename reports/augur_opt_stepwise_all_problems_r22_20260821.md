---
title: augur 優化——全專案逐步執行最佳下一步（可先／可同步）計畫書 r22
status: adopted_exec_ssot
series: optimization_plan
round: r22
role: **後續優化執行計畫書（全專案開問題）**；Steward「後續依此進行」＝OPT-R22-ALL 開工鎖
date: 2026-08-21
viewpoint: 2026-08-21T14:45+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r22_20260821.md
  - reports/augur_project_charter_plain_zh_r22_20260821.md
understanding: reports/augur_deep_understanding_and_opt_plan_r22_20260821.md
charter: reports/augur_project_charter_plain_zh_r22_20260821.md
supersedes_exec: reports/augur_opt_stepwise_all_problems_r21_20260820.md
inherits_board: reports/augur_opt_stepwise_all_problems_r21_20260820.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
path_opt_ops: reports/augur_path_timing_opt_ops_plan_r18_20260819.md
path_hit_tombstone: audits/PATH-HIT-LIFT-P5-STOPPED-20260820.md
finmind_free: reports/augur_finmind_free_rankridge_plan_r21_20260821.md
hist_wf: reports/augur_hist_ridge_wf_plan_r21_20260820.md
slim_plan: reports/augur_repo_slim_opt_plan_r20_20260819.md
archive_tip: archive-20260821-r21-w10-ma-finmind-p0
self_reported: true
---

# augur 優化——全專案逐步執行最佳下一步 r22（2026-08-21 14:45）

> **一句**：後續優化**只跟本檔**。價／世界／八窗模型／兩窗出門 tip＝**08-20**（237）。**08-19 補帳已寫**（285）。日曆 08-21＝假 B3。  
> **位階**：[I]；不創 [N]。本檔＝開工鎖（Steward：依此進行）。**不是** B3-go、不是改 L0、不是第二支 WF `--apply`、不是重開 PATH-HIT-LIFT。  
> **分軌**：市場 ≠ 指揮 KH；KH ≠ 擋 B3；路徑 ≠ 改 standing；取數計畫 ≠ 今天改 cron。

理解＝r22。心跳仍＝r16。PATH-OPT 管 θ。HIT-LIFT＝墓碑。slim＝r20。FinMind＝free 計畫（P1 另 GO）。

---

## §0 怎麼用（每次開工）

```text
1) 看 §1 決策卡 → 現在只做這些
2) 看 §1b 四欄：須 GO／可先／可同步／禁
3) 看 §2 全板：狀態≠🟢／≠禁 的列
4) 缺 GO → 停；有 GO → 做、寫 audit、改本檔狀態
5) 細節指令 → 長板（r16／KH／PATH-OPT／FinMind／HIST-WF）
```

| 標記 | 意思 |
|---|---|
| **最佳下一步** | 這一列若要動，下一槍具體做什麼 |
| **可先** | 市場主軸仍在 WAIT（無 08-21 價，或 08-19／08-20 出門未授權）時，**現在就可以做** |
| **可同步** | 可與其他可先並行；**B3／L2 開火則讓出** `augur_llm.lock` |
| **延後** | 主軸未閉合前不要排進工時 |
| **❄／禁** | 凍結或禁止；要動須**另句**明示，本鎖不夠 |

**Hard doors**

```text
FZ/GATE-keep | no-fake-B3@08-21 | NF-pause | no-SIM-apply | no-promote
| skip-sync-B | standing=20,60 除非雙明示
| PDF-C-no-ASR | stop-at-7 | no-relax-θ | apply=opt-in
| score／p_beat／p_mkt／p_up／路徑％／勝率／均線閘 ≠ 報酬％
| 觀察≠進場 | 條件≠可交易 | 兩檔≠宇宙 | 做空≠可融券
| PATH-HIT-LIFT 河閉；禁 P2／P3／P4
| 禁 E5／倒 canonical 31／再送 E4 就緒 5
| 禁 evaluate 草稿 dgate；禁 --track other --apply
| 不改 L0 直到 P0′（錶≠6000）
| 不第二支 HIST-WF --apply
| 平行條件帳不互覆寫
```

---

## §1 決策卡｜現在該做什麼？

LIVE **2026-08-21 週五 14:45+08**（親查）：

| 錨 | 值 |
|---|---|
| PriceAdj TAIEX max | **2026-08-20** |
| 08-20 | `asof_ready` **ready**；fv 37／27 956；core **237**；價頂包 8×8＋Daily3＋Mkt2＋DirStackM |
| 08-19 | 截面 8×8 **ready**；core **285** |
| emit pv／pp | tip **2026-08-20** H20+H60 各 **237**；補帳＠08-19 各 **285**；校準仍 08-14 |
| 日曆 08-21 | **假 B3** rc=3 |
| 八窗模型 asof | 已到 **08-20**（≠出門）；ge2014 RankRidge **4372** |
| HIST-WF | ok **532**、last_ok **2016-03-09**、正在 **2016-03-10**、fail 0；鎖在握 |
| KH `--check` | S0 FIRE **63**；S1–S3 ok；未 apply → **其後 `KH-S0-apply-go` 已閉 0** |
| E4b | WAIT；k 已實現非重疊＝0；next＝**2026-11-13** |
| FinMind | 到期 **2026-09-14**；L0 未改 |
| PATH-HIT-LIFT | P5 墓碑 |
| 本窗可先 | `audits/OPT-R22-CAN-DO-FIRST-EXECUTED-20260821.md` |

| 問 | 答 |
|---|---|
| **全專案最佳下一步** | **刀 B**：等 08-21 真收盤再整鏈。刀 A／A2 **已閉**。08-21 **不准**當 as-of。 |
| **可先（此刻就做、不等價）** | §1b 可先欄。預設：**讓歷史河跑、讓條件帳 watch、KH `--check`、E4b 鐘重讀、P6／PME 只寫文件。** |
| **可同步** | 可先各項彼此可並行；B3 一開火全部讓路。 |
| **絕對不要** | 假 B3＠08-21；promote；sim-apply；改 L0；第二支 WF apply；HIT-LIFT 加濾；KH `--apply`；把均線／四閘／2459 當可交易 |

```text
OPT-R22-ALL | no-fake-B3@08-21
| knife-A  = B3-go | D=2026-08-19 | horizons=20,60
| knife-A2 = B3-go | D=2026-08-20 | horizons=20,60
| knife-B  = WAIT PriceAdj≥08-21-close 再整鏈
| standing=20,60 | no-promote | NF-pause
| no-second-WF-apply | no-L0-until-P0-prime
| emit@08-20 H20+H60 n=237 | world@08-20 core=237
| archive=archive-20260821-r21-w10-ma-finmind-p0
```

---

## §1b 四欄清單（本窗工時）

### 須 GO（本鎖不夠）

| 槍 | 要貼的句 | 做完長什麼樣 |
|---|---|---|
| **刀 B** 08-21 心跳 | 價進庫 **且** `B3-go \| D=2026-08-21 \| horizons=20,60` | tip＝D；#14 誠實 |
| P6 refit | 點名 H 與 asof 的 GO | freeze 日對齊價頂（另帳） |
| FinMind P1 L0 | 先 P0′（錶≠6000）再 `FINMIND-FREE-L0-go` | 閉集瘦、register SKIP |
| RS-CHARGE P1／TREND-PB W4／路徑 emit | 各產品自己的 `*-go` | dry-run；≠可交易 |
| 補 HIST＠08-10 | 點名缺 52 | 另句；無 GO 不跑 |
| standing 八窗／promote／K9／K10 | 雙明示或 adopt | 本鎖永不順便 |

### 可先（現在就能做；市場 WAIT 時）

| # | 做 | 不做 | 本窗 |
|---|---|---|---|
| **1W** | 讓 HIST-WF `--apply` 繼續；條件帳 watch **已在跑就不要再開** | 第二支 WF apply；搶 `/tmp/augur_hist_ridge_wf.lock` | **已監看**（532／2016-03-09；watch 五支都在） |
| **1C** | `python scripts/kh_ingest_trigger.py --check` | `--apply`（本鎖） | **S0 已 drain 63→0**（`KH-S0-APPLY-EXECUTED-20260821`） |
| **1D** | `python scripts/report_live_oos_clock.py --origin 2026-08-14 --h 60`（E4b 重讀） | 算未實現 PnL；E5 | **已跑** WAIT |
| **1D2** | P6 缺口文件：freeze＠08-14 vs 價＠08-20（只寫、不訓） | refit | **已寫** `M9-P6-RECON-0820` |
| **1D3** | PME 診斷維持 | 降閾／APPLY | **已寫** 20260821；PASS×PASS＝5 ≠升格 |
| **M26** | 接續讀本檔 LIVE，不重寫 300 行 HANDOFF | 當第二套義務 | 跟本檔 |
| **M20** | 升格門檻**文件**可寫 | SERVE-SWAP | **備忘** `M20-PROMOTE-HOLD-MEMO` |
| **M15** | 10–14 治權日曆備忘 | 假關 039 殘留 | **備忘** `M15-GOVERNANCE-CALENDAR-MEMO` |

### 可同步（與可先並行；B3 開火則停）

1C ∥ 1D ∥ 1D2 ∥ 1D3 ∥ 1W 監看 ∥ M20 文件 ∥ M15 備忘 ∥ K4／K6 輕抽樣。  
**不可同步**：任何 `--apply` 訓模、L0 放量、第二 WF、KH `--apply`、路徑探針搶 LLM。

### 禁（本窗不當工單）

假 B3＠08-21；sim `--apply`；promote；默八窗出門；HIT-LIFT P2–P4；改 L0／93 表／到期前猜 free；`--track other --apply`；重掃 0812 NF；evaluate 草稿 dgate；倒 canonical 31；再送 E4 就緒 5；把條件帳／2459 當可交易；做空當可融券。

---

## §2 全專案開問題板

> 🟢＝本窗不當工單。❄／禁＝不要排進「可先」。

### 2.1 市場／預測／凍結／結構／路徑／取數

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **M1a** | — | 08-14 出門 | — | — | — | 🟢 |
| **M1b** | — | 08-17 出門 | — | — | — | 🟢 |
| **M36** | — | 08-18 出門 | — | — | — | 🟢 H20+H60 |
| **M37** | R22-01 | **08-19 世界齊、名單未寫** | — | — | — | 🟢 補帳＠08-19 H20+H60 n=285；tip 仍 08-20 |
| **M37b** | R22-01 | **08-20 世界齊、名單未寫** | — | — | — | 🟢 出門＠08-20 H20+H60 n=237 |
| **M38** | — | 08-20 價 | 已進庫 | — | — | 🟢 價閉 |
| **M38b** | R22-02 | 08-21 收盤未進庫 | WAIT PriceAdj≥08-21-close | **否** | — | 🟡 **刀 B** |
| **M39** | R21-03 | PATH-HIT-LIFT | **停** | **否** | **否** | 🟢 墓碑 |
| **M2** | R19-03 | econ／dgate | 不修綠；H20=dead、H60=thin | 披露＝是 | 是 | 🟢 形已誠實 |
| **M3** | — | graph tip | — | — | — | 🟢 |
| **M4** | — | H82 | 禁再插入 | — | — | 🟢 |
| **M5** | — | r22 文檔 | 開工跟**本檔** | — | — | 🟢 本鎖 |
| **M6** | — | ARCHIVE | `archive-20260821-r21-w10-ma-finmind-p0` | — | — | 🟢 |
| **M7** | R19-06 | 圖提拔 | `VERIFY-graph-cand-go` | **否** | **否** | 🔴 延後 |
| **M8** | — | C1／CYCLE | 見 K10 | **否** | — | 🟢 隔離 |
| **M9** | R19-05 | P6 freeze＠08-14 vs 價＠**08-20** | **文件可先**；refit 另 GO | 文件＝是 | 訓＝否 | 🟡 缺口再開；本窗已寫 recon |
| **M10** | R19-08 | M／β5／NF | 輕監；0812 **勿重掃** | 監看＝是 | 監看＝是 | 🟢 監看；開訓❄ |
| **M11** | R19-10 | Dividend | 另 auth | **否** | **否** | ❄ |
| **M12** | R19-10 | sim apply | **禁** | **否** | **否** | 禁 |
| **M13** | R19-09 | 循環依賴文件 | explore-only | 低優先可讀 | 是（零碼） | 🔴 |
| **M14** | R20-11 | 倉精化 | slim r20；T5 鐘最早≈11-17；≠rm | T5＝否 | 是（零產品碼） | 🟢 T7 閉；T5 候選 |
| **M15** | R19-11 | 10–14 治權日曆 | 備忘；不假關 | 備忘＝是 | 是 | 🟡 本窗已寫備忘 |
| **M16** | R19-04 | standing 八窗 | **雙明示** | **否** | **否** | ❄ |
| **M17** | R19-21 | dgate evaluate | 另 GO；禁塗綠 | **否** | **否** | 禁 |
| **M18** | R19-27 | 其他族／HIST 未齊 | 近端 8H 已到 08-20；下一未齊 **08-10 缺 52** 另句；禁重掃 0812 | 補 08-10＝否 | 讓 B3 | 🟢 近端齊；08-10 另句 |
| **M19** | — | family_chk | — | — | — | 🟢 |
| **M20** | R19-07 | 升格 | 可寫門檻文件；禁 swap | 文件＝是 | 文件＝是 | 🟢 hold；swap❄；本窗備忘 |
| **M21** | — | Wave-A | — | — | — | 🟢 |
| **M22** | — | RankRidge＠08-18 | 訓＋出門已閉 | — | — | 🟢 |
| **M22b** | R22-01 | RankRidge＠08-19／08-20 | pv 兩日皆寫；tip＝08-20 | — | — | 🟢 |
| **M23** | R19-15 | tip＋N 實現 | E4b 鐘；H60 第 1 期≈11-13 | 鐘重讀＝是 | 文件＝是 | 🔴 實現；鐘🟢 |
| **M24** | — | 分數看板 | score≠％ | — | — | 🟢 |
| **M25** | — | 入倉 | 20260821 封存已推 | — | — | 🟢 |
| **M26** | R19-22 | HANDOFF | 讀本檔 LIVE | 備忘＝是 | 是 | 🟡 |
| **M27** | R19-23 | PME | 診斷；禁降閾／APPLY | 文件＝是 | 是 | 🟡 本窗 run_id=35；PASS×PASS＝5 ≠升格 |
| **M28** | R19-24 | #14 | E4 耗盡；E4b WAIT k=0 | 鐘＝是；E5＝禁 | 文件＝是 | 🟡 本窗已重讀 WAIT |
| **M29** | R19-25 | RIDGE-THEN-PB v1 | 表在；做多買進 tip **08-14**；≠可交易 | 再開 watch＝否（已有則維持） | 讓 B3 | 🟡 產品在 |
| **M30** | R19-25 | TREND-PB | W4／W5 **另句** | **否** | 讓 B3 | 🟡 W3 閉 |
| **M31** | — | WATCH-PB | P2 另句；觀察≠進場 | **否** | 讓 B3 | 🟡 |
| **M32** | — | BULL5 | P2 另句 | **否** | 讓 B3 | 🟡 |
| **M33** | R19-25 | RS-CHARGE | P1 探針**未跑** | **否**（須 GO） | 讓 B3 | 🟡 P0 閉 |
| **M34** | — | TWIN-EX | ≠可交易 | — | 讓 B3 | 🟡 P1 閉 |
| **M35** | R19-26 | CHARGE-T5 | 成本後 IS −64.8%；≠可交易、≠#14 | **否** | — | 🟡 失敗邊界已量 |
| **M40** | — | 全宇宙四閘 | ≠ Ridge 池、≠可交易 | 探針另句 | 讓 B3 | 🟢 帳；不當日更 |
| **M41** | R22-03 | HIST-RIDGE-WF 河 | **讓跑**；禁第二 apply；不聲稱灌完 | 監看＝是 | 監看＝是 | 🟡 河＠2016-03-09／532 |
| **M42** | — | W10／MA10／MA20 | 不覆寫 v1；W10＝0 列＝誠實空；MA10／MA20 有 08-20 | 再開 watch＝否 | 讓 B3 | 🟢 入倉；≠可交易 |
| **M43** | R22-04 | FinMind → free | P0 基線已做；P0′＝錶≠6000；P1 另 GO | **改 L0＝否** | — | 🟡 日曆 09-14 |
| **M44** | R22-05 | core＠08-20＝237 | 記實；不編造；P3 宇宙閘另 GO | 文件＝是 | 是 | 🟡 |
| **M45** | — | 單檔研報（2459） | 另帳 [I]；不滑進日更 | — | — | 🟢 |

### 2.2 知識／顧問

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **K0** | — | S0 kh0_breach | `--check` 可重跑；`--apply` 須 `KH-S0-apply-go` | check＝是 | 避開 B3 | 🟢 本窗 drain 63→0 |
| **K1** | — | S3 zh lag | — | — | — | 🟢 |
| **K2** | — | ingest 階梯 | 守 apply 選開 | — | — | 🟢 |
| **K3** | R19-19 | AUTO-LIFT | **禁抬 >KH2** | **否** | — | 🟢／禁抬層 |
| **K4** | R19-14 | 私有 smoke | 可選抽樣 | 是 | 是 | 🟢 |
| **K5** | R19-12 | Doc1 純圖 | hold；不 OCR 硬開 | **否** | — | 🟢 hold |
| **K6** | R19-14 | ASR 對聽 | 可選抽樣 | 是 | 是（輕） | 🟢 |
| **K7** | — | 8b 口吻 | 守 8b＋960 | — | — | 🟢 |
| **K8** | R19-16 | KH8 | **E-keep／stop-at-7** | **否** | **否** | ❄ |
| **K9** | R19-17 | 他域 FT | 另 adopt 才訓 | **否** | **否** | 🔴 |
| **K10** | R19-18 | C1→feat | 另 GO；禁默加權 predict | **否** | **否** | 🔴 隔離 |
| **K11** | R19-13 | `.msg`／rar | skip-hold | **否** | **否** | 🔴 |
| **K12** | — | KH10 | — | **否** | **否** | 禁（≠ H10） |
| **K16** | — | 假 decline 閘 | 已修 | — | — | 🟢 |
| **K17** | — | 閘入倉 | — | — | — | 🟢 |

---

## §3 逐步執行序列

### Phase 0｜✅ 已閉（不當工單）

08-13／14／17／**18 兩窗出門**；08-20 **價**＋價頂 RETRAIN 包；H_TRACK 八窗可訓；L0 熱路徑（Sponsor）；W10／MA 入倉；FinMind P0 基線；PATH-HIT-LIFT P5；slim T0–T4＋T6＋T7；archive 20260821。**不含** 08-19／08-20 兩窗 pv。

### Phase 1｜🟡 現在（本鎖）

| 步 | 何時 | 做 | 不做 | 驗收 |
|---|---|---|---|---|
| **1W** | 可先∥ | WF 河＋既有 watch | 第二 apply | 鎖一隻 |
| **1C** | 可先∥ | KH `--check`；S0 已另句 drain | 再 `--apply` 除非新 FIRE | S0＝0 |
| **1D** | 可先∥ | E4b 鐘；P6／PME 文件 | evaluate；refit | 鐘 WAIT |
| **1J** | 刀 A 已執行 | WP-M37 | 把 tip 拉回 08-19 | 🟢 pv＠08-19 僅 20,60 n=285；tip 仍 08-20 |
| **1J2** | 刀 A2 已執行 | WP-M37b | 日曆 08-21；默八窗 | 🟢 pv＠08-20 僅 20,60 n=237 |
| **1B** | 刀 B：價到＋GO | 整鏈心跳＠08-21 | 無價假跑 | tip=D |
| **1E** | 另句 | RS-CHARGE P1 dry-run | 當可交易 | 對上預診 |
| **1F** | **禁至 P0′** | 改 L0 | 93 表 | — |
| **1K** | **禁** | HIT-LIFT P2–P4 | 加濾勝率 | 墓碑 |

**並行規則**：1W／1C／1D 在 1J／1J2／1B **未開火**時同時做。任一 B3 開始 → 長 LLM／apply／探針**讓路**。

### Phase 2｜主軸閉合後（Steward 選一，不預設全開）

1. 下一交易日重複 1B（standing 20,60）  
2. P6 擴窗（plan＋GO；freeze 已舊）  
3. FinMind P0′ → P1 L0  
4. 升格文件定稿（仍 no-promote）  
5. K9 僅 adopt 後  
6. 圖 VERIFY  
7. NF 殘格——點名卡才 plan  
8. standing 八窗——僅雙明示  
9. PATH-OPT 未閉槍——各一 ID；**不含** HIT-LIFT  
10. 降週轉接 CHARGE-T5 教訓——**新 ID**

### Phase 3｜本檔不開

解凍 M／β5；撤 NF-pause；cron 自動 B3；sim `--apply`；SERVE-SWAP；放寬 θ；depth≥8；KH10；K10 默灌預測；evaluate 草稿 dgate；假 B3＠08-21；E5；倒 31；把條件帳／群光／CHARGE-T5／2459 當可交易；重開 HIT-LIFT；到期前改 L0；第二支 WF apply。

---

## §4 工作包（開跑複製）

### WP-M37｜補出門＠08-19（刀 A；須 GO）

```text
WHEN: Steward 貼 B3-go | D=2026-08-19 | horizons=20,60
DO:   bash scripts/run_daily_asof_predict.sh --date 2026-08-19 --horizons 20,60
      （包未齊才）L2 / retrain_all_asof
DONT: --date 2026-08-21; sync-B; sim-apply; 默八窗; promote; 搶 WF 鎖去訓八窗河
DONE: 2026-08-21 predict+emit RC=0 n=285；殼 accept rc=4 預期（tip 仍 08-20）；audits/OPS-B3-20260819-EXECUTED-20260821.md
```

### WP-M37b｜補出門＠08-20（刀 A2；須 GO）

```text
WHEN: Steward 貼 B3-go | D=2026-08-20 | horizons=20,60
      （check_asof_ready --date 2026-08-20 已 ready、價頂包已齊）
DO:   bash scripts/run_daily_asof_predict.sh --date 2026-08-20 --horizons 20,60
DONT: --date 2026-08-21; 默八窗; promote
DONE: 2026-08-21 RC=0 + pv/pp＠08-20 僅 20,60 n=237；audits/OPS-B3-20260820-EXECUTED-20260821.md
```

### WP-M38b｜新價心跳＠≥08-21 收盤（刀 B；須 GO）

```text
WHEN: PriceAdj(TAIEX) ≥ 該日 且 Steward 貼 B3-go | D=<D> | horizons=20,60
DO:   （需要時）bash scripts/run_l0_hotpath_daily.sh --date <D> --apply
      bash scripts/run_daily_asof_predict.sh --date <D> --horizons 20,60
      （L1 RC=0 且包未齊才）L2 / retrain_all_asof
DONT: 無價假跑@08-21; sync-B; sim-apply; 默八窗; promote
DONE: RC=0 + EXECUTED + #14 誠實
```

### WP-M41｜HIST-WF 河（可先＝讓它跑）

```text
WHEN: 已在跑則維持
DO:   監看 audits/HIST-RIDGE-WF-ALLDAYS-PROGRESS.json；不殺不疊
DONT: 第二支 --apply；口頭「已灌到價頂」
DONE: 河自己寫進度；本鎖不驗收灌完
```

### WP-M43｜FinMind（可先＝不改碼）

```text
WHEN: /user_info api_request_limit ≠ 6000
DO:   python scripts/probe_finmind_free_rankridge.py --apply
      然後另貼 FINMIND-FREE-L0-go 才改 L0
DONT: 到期前改閉集；93 表；到期日 hardcode 進程式
DONE: P0′ audit；P1 另檔
```

### WP-KD｜KH 巡檢（可先∥）

```text
WHEN: 任意；避開 B3 開火
DO:   python scripts/kh_ingest_trigger.py --check
DONT: 無 GO 卻 --apply
DONE: 記 FIRE；不當進化
```

### WP-M28｜E4b 鐘（可先∥）

```text
WHEN: 任意重讀
DO:   python scripts/report_live_oos_clock.py --origin 2026-08-14 --h 60
DONT: 未實現 PnL；E5；再送就緒 5
DONE: 鐘仍 WAIT；next≈2026-11-13
```

### WP-HIT-LIFT｜停

```text
WHEN: 永不（本產品 ID）
DONT: P2／P3／P4；放寬四閘
RETRY: 全新產品 ID
```

---

## §5 債表 → 本板

| 債 | 本板 | 本窗 |
|---|---|---|
| R22-01 兩日出門缺口 | M37／M37b／M22b | 🟢 08-19 補＋08-20 tip |
| R22-02 08-21 價 | M38b | 🟡 WAIT |
| R22-03 WF 河 | M41 | 🟡 讓跑 |
| R22-04 FinMind P0′ | M43 | 🟡 09-14；不改 L0 |
| R22-05 core 237 | M44 | 🟡 記實 |
| R21-03 HIT-LIFT | M39 | 🟢 |
| R19 其餘 | 見上表 | **不假關** |

---

## §6 細節板（本檔管順序，不管長指令全文）

| 用途 | 路徑 |
|---|---|
| 理解 | `reports/augur_deep_understanding_and_opt_plan_r22_20260821.md` |
| 人話憲章 | `reports/augur_project_charter_plain_zh_r22_20260821.md` |
| 精要讀序 | `reports/SSOT_READ_ORDER.md` |
| 前一執行板 LIVE 過期 | `reports/augur_opt_stepwise_all_problems_r21_20260820.md` |
| 心跳 | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md` |
| L0／L2 | 20260814／20260812 計畫 |
| FinMind | `reports/augur_finmind_free_rankridge_plan_r21_20260821.md` |
| HIST-WF | `reports/augur_hist_ridge_wf_plan_r21_20260820.md` |
| PATH-OPT／墓碑 | r18 ＋ `audits/PATH-HIT-LIFT-P5-STOPPED-20260820.md` |
| KH | 20260813 板 |
| slim | r20 |

衝突：開工順序與可先／可同步 **以本檔為準**。

---

## §7 何時刷新（r23）

B3＠08-19 或＠08-20 閉合；或 08-21 真心跳閉合；或錶≠6000；或 Steward 雙明示改 standing／L0／升格；或 WF 對帳宣稱灌到價頂。  
**不因** HIT-LIFT 再寫勝率續集。

---

## §8 驗收

- [x] 全專案開問題入板（市場＋路徑＋知識＋取數＋河）  
- [x] 每列有最佳下一步＋可先＋可同步  
- [x] §1b 四欄可當「現在只做這些」  
- [x] 分軌：知識可先不等價；河可先不搶出門；L0 不因本鎖改  
- [x] LIVE：價 08-20／emit 08-18／假 B3＠08-21／core 237  
- [x] 不創 [N]、不開訓、不假 B3、不代 commit  

*完。[I] · self-reported · r22 adopted_exec_ssot。*
