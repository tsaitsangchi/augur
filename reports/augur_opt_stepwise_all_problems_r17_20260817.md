---
title: augur 優化——全專案逐步執行最佳下一步（可先／可同步）計畫書 r17
status: superseded_by_r18
series: optimization_plan
round: r17
role: 歷史執行板（開工順序改跟 r18）
superseded_by: reports/augur_opt_stepwise_all_problems_r18_20260817.md
date: 2026-08-17
viewpoint: 2026-08-17T08:16+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r17_20260817.md
  - reports/augur_project_charter_plain_zh_r17_20260817.md
understanding_adopted: audits/DEEP-UNDERSTANDING-R17-OPT-PLAN-ADOPTED-20260817.md
exec_adopted: audits/OPT-R17-ALL-PROBLEMS-ADOPTED-20260817.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
s1_s5_parent: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
detail_kh: reports/augur_kh_opt_stepwise_best_next_plan_20260813.md
archive_tip: archive-20260814-weekly-fd-tar
self_reported: true
---

# augur 優化——全專案逐步執行最佳下一步（2026-08-17）

> **已 supersede**：開工順序改跟 `reports/augur_opt_stepwise_all_problems_r18_20260817.md`。本檔保留為 08:16 歷史板（emit 仍寫 08-13，已過期）。

> **一句**：本檔＝**後續優化唯一執行計畫書**。每個還開著的問題都標了：**最佳下一步**、**現在可先做？**、**可與主軸同步做？**。  
> **來源**：深化理解 r17 債表 R17-01…23。  
> **位階**：[I]；不創 [N]；不解凍；不假 B3；不 sim-apply；不默升格；**勿重掃假綠**。  
> **分軌保留**：市場與知識**互不等待**。  
> **LIVE（親查 08:16+08）**：價頂／fv＝**2026-08-14**；emit＝**2026-08-13** 僅 H20＋H60；08-17 無價。  
> **KH `--check`（08:16，唯讀）**：S0 FIRE kh0_breach=**213**；S1 FIRE delta=**68**；S3 FIRE zh lag_est=**2**。**未** `--apply`。

本檔 **supersede** `reports/augur_opt_stepwise_all_problems_r15_20260813.md` 作為開工順序；r15 長板指令仍可當細節。

---

## §0 怎麼用（後續優化協議）

```text
每次要開工／問「下一步」：
  1) 先看 §1 決策卡（現在只做那幾件）
  2) 再看 §2 全板：狀態≠🟢／≠禁 的列
  3) 缺 GO → 停、問 Steward；有 GO／已授重用 → 做、寫 audit、改本檔狀態
  4) 細節指令 → r16 心跳／KH 板／WP 卡片
```

| 標記 | 意思 |
|---|---|
| **最佳下一步** | 這一列若要動，**下一槍具體做什麼** |
| **可先** | 市場主軸仍在 **WAIT 無今日價** 時，**現在就可以做**（不假跑 B3＠08-17、不搶即將開火的 LLM 重活） |
| **可同步** | 可與**另一軌或主軸 WAIT** 並行；B3／L2 **開火中**則讓出 `augur_llm.lock` |
| **延後** | 主軸未閉合前不要排進工時 |
| **❄／禁** | 凍結或禁止；要動須**另句**明示 |

**Hard doors**：

```text
FZ/GATE-keep | no-fake-B3@08-15/16/17 | NF-pause | no-SIM-apply | no-promote
| 勿重掃假綠 | skip-sync-B | 誠實 econ | standing=20,60 除非雙明示
| PDF-C-no-ASR | ASR=owned_local+local_private | no-KH10 | stop-at-7 | no-relax-θ
| T0 | apply=opt-in | 有引文禁假「無此內容」 | 空包不進化
| score／p_beat／p_mkt／p_up ≠ 報酬％
| 市場≠指揮 KH；KH≠擋 B3
| 禁 evaluate／approve dgate_H_5/10/60/90/240（無新 GO）
| 禁塗 established（無 E5-verdict-go）；不救 H20；不放寬 DSR 95%
```

---

## §1 決策卡｜現在該做什麼？

視點 **2026-08-17 08:10+08**（開盤前；價頂 08-14；emit 08-13）。

| 問 | 答 |
|---|---|
| **全專案最佳下一步** | **M1b**：候 `PriceAdj≥2026-08-17` → 另貼 B3-go 再心跳。M1a 出門＠08-14 **已 EXECUTED** |
| **此刻絕對不要** | 把 as-of 設成 08-15／08-16／08-17 |
| **可先做（不等今日價）** | KH `--check` **已跑**（S0／S1／S3 FIRE，未 apply）；誠實披露 #14；M25 未提交清單；P6 對帳文件；**M28 E4 就緒 5 耗盡**；**E4b 鐘已掛（WAIT、k=0、next=2026-11-13）**。S0 drain **須另句**才 `--apply` |
| **可同步做** | 上列。B3 開火時讓出 LLM。**不要**再開 K9／P6 訓／NF／dgate evaluate／KH `--apply` |
| **不要做** | 假 B3；sim-apply；塗綠；換冠；默八窗出門；重掃 0812；K9 開訓；放寬 θ；假 depth8；ASR→PDF-C |

```text
paste（後續優化依本檔）:
  OPT-R17-ALL | no-fake-B3@08-15/16/17
  | knife-A=B3-emit@08-14 horizons=20,60
  | knife-B=WAIT PriceAdj≥08-17 then L0→L1→L2
  | standing=20,60 | H_TRACK=8 | no-promote | NF-pause
  | kh=check-green | E-keep | stop-at-7 | no-K9-train
```

**工時切法（人話）**：

1. **此刻（無 08-17 價）**：Steward 若選刀 A → 只做 08-14 出門；若選刀 B → 巡檢／文件／等價。  
2. **08-17 價到**：只做 L0（需要時）→ B3 20,60 → 包未齊才 L2／RETRAIN-ALL；做完寫 EXECUTED＋誠實 #14。  
3. **當日 23:50 仍無價**：TIMEOUT 帳；**仍不假跑**。

---

## §2 全專案開問題板

> 🟢＝本窗不當工單；❄／禁＝不要排進「可先」。

### 2.1 市場／預測／凍結／結構

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **M1a** | R17-01 | 08-14 已訓未出門 | — | — | — | 🟢 `OPS-B3-20260814-EXECUTED` |
| **M1b** | R17-02 | 08-17 心跳 | 候 `PriceAdj≥08-17` → 另貼 B3-go 再 L0／B3 20,60 | **否**（無價不能做） | 開火獨佔 | 🟡 **KEEP WAIT** |
| **M2** | R17-03 | econ／dgate | **不修綠**；披露 H20=dead、其餘 thin；draft 閘不 evaluate | **是** | **是** | 🟢 形已誠實；持續 |
| **M3** | — | graph tip 邊 | — | — | — | 🟢 |
| **M4** | — | H82 庫列 | 已刪；代碼配方史料；禁再插入 | — | — | 🟢 |
| **M5** | — | r17 文檔 | 本計畫落地後跟本檔 | — | — | 🟢 本輪 |
| **M6** | — | ARCHIVE 後入倉 | 焦點改 **M25**（H 軌／r17 文檔） | 清單＝是 | 是（≠B3） | 🟢 併 M25 |
| **M7** | R17-06 | 圖提拔熱路徑 | 另 `VERIFY-graph-cand-go` | **否** | **否** | 🔴 |
| **M8** | R17-18 市場側 | C1／CYCLE | 不編；見 K10 | **否** | — | 🟢 隔離 |
| **M9** | R17-05 | P6／長窗 | 對帳 08-14 artifact vs 08-04／08-07 校準器；擴窗**另 plan＋GO** 才訓 | **文件＝是**；訓練＝否 | 文件＝是 | 🟡 文件；訓❄ |
| **M10** | R17-08／10 | M／β5／NF | 輕監；0812 六族**勿重掃**；殘格須點名卡 | **監看＝是**；開訓＝否 | 監看＝是 | 🟢 監看；開訓❄ |
| **M11** | R17-10 | Dividend | 另 auth | **否** | **否** | ❄ |
| **M12** | R17-10 | sim apply | **禁** | **否** | **否** | 禁 |
| **M13** | R17-09 | 循環依賴文件 | explore-only | 低優先可先讀 | 是（零碼） | 🔴 |
| **M14** | R17-09 | scripts 冗餘 | #29 另計畫 | **否** | **否** | 🔴 |
| **M15** | R17-11 | 10–14 治權日曆 | 10 月初清單；**不假關** | 排程備忘＝是 | 是 | 🟡 |
| **M16** | R17-04 | standing 八窗殼 | **雙明示**＋改 `run_daily_asof_predict.sh` 預設 | **否** | **否** | ❄ |
| **M17** | R17-21 | dgate evaluate | 另 GO；禁塗綠草稿閘 | **否** | **否** | 禁（無 GO） |
| **M18** | R17-08 | 其他模型族 | 殘格仍點名；**禁**重掃 0812 | 閘／hist 殼＝是 | 讓 B3 | 🟢 V0；NF❄ |
| **M19** | — | family_chk | — | — | — | 🟢 |
| **M20** | R17-07 | 升格另軌 | 可寫門檻文件；禁 SERVE-SWAP | **文件＝是** | 文件＝是 | 🟢 hold；swap❄ |
| **M21** | — | Wave-A 收官 | — | — | — | 🟢 |
| **M22** | — | RankRidge＠08-14 | 已重訓 8 窗；換殼另句 | — | — | 🟢 訓；出門見 M1a |
| **M23** | R17-15 | tip＋N 實現報酬 | **等價蓋過 tip＋N 交易日** 才研究（08-14 起算）。E4b 鐘已掛；第一筆 H60 出場＝2026-11-13 | **否**（價未蓋） | **否** | 🔴；鐘🟢 WAIT |
| **M24** | — | 相對機率／分數看板 | 守 score／p_beat≠報酬％ | — | — | 🟢 |
| **M25** | R17-20 | H 軌開窗碼未入倉 | 列 diff；**Steward 明示才 commit／push** | **清單＝是** | 是（≠B3 開火） | 🟡 |
| **M26** | R17-22 | HANDOFF 過期 | 不在本窗重寫 300 行 STATE；接續讀 r17 LIVE | 備忘＝是 | 是 | 🟡 |
| **M27** | R17-23 | PME 缺 map | 維持診斷；禁降閾／禁 APPLY | 文件＝是 | 是 | 🟡 |
| **M28** | #14 確立 | 往「證明能賺錢」 | E4 就緒 5 耗盡。E4b 鐘 **WAIT**：已實現非重疊＝0；next＝2026-11-13。未付 N、未提拔、未 evaluate | E5＝禁（AND 未過且 K=0） | 文件＝是；鐘可重讀 | 🟡 **鐘 WAIT k=0** |

### 2.2 知識／顧問

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **K0** | — | S0 KH0 breach | `--check` 已 FIRE **213**；drain 須另句 `--apply`（limit=213） | 巡檢＝**已做**；apply＝**否**（缺 GO） | apply 避開 B3 | 🟡 **FIRE** |
| **K1** | — | S1 新件／S3 lag | S1 delta=**68**；S3 zh lag=**2**。S3 concordance 須另句 | 巡檢＝已做；apply＝否 | apply 避開 B3 | 🟡 **FIRE** |
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
| **K17** | — | 閘入倉 | r15 已入倉；本輪焦點改 M25 | — | — | 🟢 |

---

## §3 逐步執行序列（Phase）

### Phase 0｜✅ 已閉（本檔不當工單）

B3＠08-13、L2／RETRAIN-ALL＠08-13 與＠08-14（8×8）、H90 取代 H82、H5／H10／H240 開窗、L0 熱路徑採納、RETRAIN-ALL cron 採納、KH 分軌、假 decline 閘、KH8 A2-L3 未過 θ、NF＠0812 六族 EVIDENCE no-promote。

### Phase 1｜🟡 現在（開盤前 WAIT＋可先）

| 步 | 何時 | 做 | 不做 | 驗收 |
|---|---|---|---|---|
| **1A** | Steward 選刀 A | B3 20,60＠08-14 | 假 08-17、默八窗、promote、dgate evaluate | ✅ tip emit=08-14 H20+H60；#14 誠實 |
| **1B** | Steward 選刀 B 或 1A 已閉且新價到 | 08-17 整鏈心跳 | 無價假跑 | tip=D；#14 誠實；no-promote |
| **1C** | 23:50 無 08-17 價 | TIMEOUT 帳 | 仍不假跑 | TIMEOUT audit |
| **1D** | **此刻可先** | KH `--check`（已跑、FIRE 未 apply）；M2 披露；M25 清單 | 不開 K9／K8；不擅自 commit；不 KH `--apply` | check 帳在；清單在 |
| **1E** | **可先文件** | M9 P6 對帳；M20 升格 hold；**M28 就緒 5 耗盡** | evaluate／改 established／付 N／無 GO 提拔／放寬 ρ／再送就緒殘餘 | 文件；swap❄；feat 另角度才開 |

**並行規則**：1D／1E 在 **1A／1B 未開火** 時可同時做。1A 或 1B 開始 → 長 LLM／apply **讓路**。

### Phase 2｜主軸閉合後（Steward 選一，不預設全開）

1. 下一交易日重複 1B（standing）  
2. P6／長窗（有 plan＋GO）  
3. 升格門檻文件定稿（仍 no-promote）  
4. K9 **僅**在 `K9-DOMAIN-FT-plan-adopt` 之後  
5. 圖提拔 VERIFY  
6. NF 殘格——**點名卡才 plan**  
7. standing 八窗——**僅雙明示**

### Phase 3｜本檔不開

解凍 M／β5；無點名撤 NF-pause；cron B3；sim `--apply`；八窗改 standing；SERVE-SWAP；放寬 θ；depth≥8；KH10；K10 默灌預測；對話 approve 來源；整庫回填當進化；evaluate 草稿 `dgate_H_*`；假 B3。

---

## §4 工作包（開跑複製）

### WP-M1a｜補出門＠08-14（刀 A；須 GO）

```text
WHEN: Steward 明示 M1a-go
DO:   bash scripts/run_daily_asof_predict.sh --date 2026-08-14 --horizons 20,60
DONT: --date 2026-08-15/16/17; 默改 8 窗; promote; evaluate dgate; sim-apply
DONE: RC=0 + EXECUTED + prediction_probability@08-14 僅披露 H20 dead / H60 thin
NOTE: RETRAIN-ALL 已 COMPLETE；本包＝S5 出門，不是再訓一遍
```

### WP-M1b｜新價心跳＠≥08-17（刀 B）

```text
WHEN: PriceAdj(TAIEX) ≥ 2026-08-17
DO:   （需要時）bash scripts/run_l0_hotpath_daily.sh --date 2026-08-17 --apply
      bash scripts/run_daily_asof_predict.sh --date 2026-08-17 --horizons 20,60
      （L1 RC=0 且包未齊才）L2 / run_retrain_all_asof_daily.sh
DONT: 無價假跑; sync-B; sim-apply; 默八窗; promote
DONE: RC=0 + EXECUTED + #14 誠實
```

### WP-M25｜未入倉清單（可先；commit 另句）

工作樹（2026-08-17 08:16，**不 commit**）：H 軌 DDL／`closed_horizons`／日更與方向殼、H5／H10／H90／RETRAIN-ALL＠0813–0814 audits、r17 三份報告、PME 診斷 0814、`ollama.py`。

```text
WHEN: 現在（不等價）
DO:   上列 diff；Steward 明示才 git add／commit／push
DONT: 無明示卻入倉
DONE: Steward 明示才入倉
```

### WP-KD｜KH 巡檢（可同步；本窗已跑）

```text
WHEN: 任意；避開 B3 開火
DO:   python scripts/kh_ingest_trigger.py --check
DONT: 無 GO 卻 --apply; 日曆假進化
DONE: 本窗已跑：S0 FIRE 213／S1 FIRE 68／S3 FIRE zh lag 2
```

### WP-K0｜S0 drain（須另句 GO；本窗未開）

```text
WHEN: Steward 明示 KH-S0-apply-go（且非 B3 開火）
DO:   python scripts/kh_ingest_trigger.py --apply
      # recommend：KH0 breach drain up_to=0 limit=213；可順帶 S3 zh concordance
DONT: 無 GO 卻 apply；抬 >KH2
DONE: --check S0 不再 FIRE
```

### WP-M28｜經濟確立路徑（E4 就緒 5 耗盡；E4b 鐘 WAIT）

```text
WHEN: E4b-clock EXECUTED 2026-08-17
DO:   讀 reports/augur_econ_e4b_clock_r17_20260817.md
      重讀：python scripts/report_live_oos_clock.py --origin 2026-08-14 --h 60
DONT: 算未實現 PnL；每日重疊當 T；E5-evaluate-go；再送就緒 5
DONE: audits/ECON-E4B-CLOCK-EXECUTED-20260817.md
NOTE: already_realized_nonoverlap=0；next_due=2026-11-13；K=4≈2027 年中
```

---

## §5 與深化理解債表（R17-* → 本板）

| R17 | 本板 | 本窗處置 |
|---|---|---|
| 01 08-14 出門 | M1a | 🟢 EXECUTED |
| 02 08-17 心跳 | M1b | WAIT |
| 03 econ | M2／M17 | 披露；evaluate 禁 |
| 04 八窗殼 | M16 | ❄ |
| 05 P6 | M9 | 可先文件 |
| 06 圖提拔 | M7 | 延後 |
| 07 升格 | M20 | 可先文件；禁 swap |
| 08 NF | M10／M18 | 監看∥；禁重掃 |
| 09 scripts | M13／M14 | 延後 |
| 10 M／sim／Dividend | M10–12 | ❄／禁 |
| 11 日曆 | M15 | 排程 |
| 12 Doc1 | K5 | hold |
| 13 msg／rar | K11 | skip-hold |
| 14 私有／ASR | K4／K6 | 可選抽樣∥ |
| 15 tip+N | M23 | 延後 |
| 16 KH8 | K8 | ❄ E-keep |
| 17 K9 | K9 | 延後／另 adopt |
| 18 K10 | K10 | 隔離 |
| 19 AUTO-LIFT>KH2 | K3 | 禁 |
| 20 未入倉 | M25 | 清單可先；commit 另句 |
| 21 dgate draft | M17 | 禁 |
| 22 HANDOFF | M26 | 備忘 |
| 23 PME | M27 | 診斷；禁 APPLY |
| — #14 確立路徑 | M28 | E4 就緒 5 耗盡；E4b 鐘 WAIT k=0 next=2026-11-13 |

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
| E3 量產讀數 | `reports/augur_econ_e3_measure_r17_20260817.md` |
| E4 短名單 | `reports/augur_econ_e4_shortlist_r17_20260817.md` |
| E4 漏斗墓碑 | `reports/augur_econ_e4_feat_range_mean_20d_r17_20260817.md` |
| E4 漏斗墓碑（股利） | `reports/augur_econ_e4_feat_dividend_yield_r17_20260817.md` |
| E4 漏斗墓碑（借券） | `reports/augur_econ_e4_feat_sbl_short_balance_log_r17_20260817.md` |
| E4b live OOS 鐘 | `reports/augur_econ_e4b_clock_r17_20260817.md` |

衝突：開工順序與「可先／可同步」**以本檔為準**；殼指令與 GO 文案以長板／audit 為準。r16 LIVE 段（候 08-13）已過期，**心跳契約仍有效**。

---

## §7 何時刷新（r18／改本檔）

1. M1a 或 M1b 閉合（EXECUTED 或 TIMEOUT）；或  
2. Steward 雙明示改 standing／升格／解凍／K9 adopt；或  
3. 價頂滾過 08-17 且 emit 跟上。

---

## §8 驗收（本計畫書）

- [x] 全專案開問題入板（市場＋知識＋凍結＋結構）  
- [x] 每列有最佳下一步＋可先＋可同步  
- [x] §1 決策卡可當「現在只做這些」  
- [x] 分軌：知識可先**不等價**；市場主軸不因 KH 停  
- [x] 聲明：後續優化**依本檔**；長板＝細節  

*完。[I] · r17 全專案逐步執行 SSOT。*
