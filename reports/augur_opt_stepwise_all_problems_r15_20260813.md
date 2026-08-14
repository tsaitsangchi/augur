---
title: augur 優化——全專案逐步執行最佳下一步（可先／可同步）計畫書 r15
status: final
series: optimization_plan
round: r15
role: **後續優化執行 SSOT（全專案所有開問題）**
date: 2026-08-13
viewpoint: 2026-08-13T11:54+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r15_20260813.md
  - reports/augur_project_charter_plain_zh_r15_20260813.md
detail_market: reports/augur_opt_stepwise_best_next_plan_r15_20260813.md
detail_kh: reports/augur_kh_opt_stepwise_best_next_plan_20260813.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
s1_s5_parent: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
kh_split: audits/KH-SPLIT-FROM-MARKET-AXIS-ADOPTED-20260812.md
archive_tip: archive-20260814-h240-retrain-0813
prior_archive: archive-20260814-l0-retrain-r16-b3-0813
self_reported: true
---

# augur 優化——全專案逐步執行最佳下一步（2026-08-13）

> **一句**：本檔＝**後續優化唯一執行計畫書**。每個還開著的問題都標了：**最佳下一步**、**現在可先做？**、**可與主軸同步做？**。  
> **來源**：深化理解 r15 債表 R15-01…19；細節仍可回市場板／KH 板，**開工以本檔為準**。  
> **位階**：[I]；不創 [N]；不解凍；不假 B3；不 sim-apply；不默升格；**勿重掃假綠**。  
> **分軌保留**：市場與知識**互不等待**——知識「可先／可同步」**不**以 PriceAdj 為開工條件；市場主軸**不**因知識未完美而停。  
> **LIVE（親查 11:54+08）**：PriceAdj／tip＝**2026-08-12**；H20＝dead、H60＝thin；watcher **230370** 候 ≥08-13。

---

## §0 怎麼用（後續優化協議）

```text
每次要開工／問「下一步」：
  1) 先看 §1 決策卡（現在只做那幾件）
  2) 再看 §2 全板：狀態≠🟢／≠禁 的列
  3) 缺 GO → 停、問 Steward；有 GO／已授重用 → 做、寫 audit、改本檔狀態
  4) 細節指令 → 市場板或 KH 板／WP 卡片
```

| 標記 | 意思 |
|---|---|
| **最佳下一步** | 這一列若要動，**下一槍具體做什麼** |
| **可先** | 市場主軸仍在 **WAIT 無價** 時，**現在就可以做**（不假跑 B3、不搶即將開火的 LLM 重活） |
| **可同步** | 可與**另一軌或主軸 WAIT** 並行；B3／L2 **開火中**則讓出 `augur_llm.lock` |
| **延後** | 主軸未閉合前不要排進工時 |
| **❄／禁** | 凍結或禁止；要動須**另句**明示 |

**Hard doors**：

```text
FZ/GATE-keep | hold-#1 | no-fake-B3 | NF-pause | no-SIM-apply | no-promote
| 勿重掃假綠 | skip-sync-B | 誠實 econ
| PDF-C-no-ASR | ASR=owned_local+local_private | no-KH10 | stop-at-7 | no-relax-θ
| T0 | apply=opt-in | 有引文禁假「無此內容」 | 空包不進化
| 市場≠指揮 KH；KH≠擋 B3
```

---

## §1 決策卡｜現在該做什麼？

視點 **2026-08-13 12:00+08**（價頂仍 08-12；K17 已入倉）。

| 問 | 答 |
|---|---|
| **全專案最佳下一步** | **M1**：A2B3 watcher 候 `PriceAdj≥08-13` → B3 `20,60` → L2（**禁止假跑**）。閉環怎麼轉＝**r16** |
| **可先做（此刻、不等價）** | **已做**：K17 入倉；M2 披露；`--check` 綠；M10 監看；M9 對帳；M20 hold 卡。**剩下**：等價／23:50 TIMEOUT；push 另句 |
| **可同步做** | 上列已閉項本窗不再重做。B3 開火時讓出 LLM。**不要**再開 K9／P6 訓／NF |
| **不要做** | 假 B3；sim-apply；塗綠；換冠；默五窗；重掃 0812；K9 開訓；放寬 θ；假 depth8；ASR→PDF-C |

```text
paste（後續優化依本檔）:
  OPT-R15-ALL | hold-#1 WAIT≥08-13 | B3=20,60 then-L2
  | 可先=K17-commit ∥ M2-disclose ∥ kh-check ∥ NF-watch
  | no-fake-B3 | no-K9-train | E-keep | stop-at-7 | dual-ssot-keep
```

**工時切法（人話）**：

1. **此刻（無 08-13 價）**：入倉假 decline 閘 → 跑一次 `kh_ingest_trigger --check` → 其餘等 watcher。  
2. **價到**：只做 B3→L2；做完寫 EXECUTED＋誠實 #14。  
3. **23:50 仍無價**：TIMEOUT 帳；**仍不假跑**；可先項可繼續。

---

## §2 全專案開問題板

> 列齊 r15 債。🟢＝本窗不當工單；❄／禁＝不要排進「可先」。  
> **可先／可同步** 欄：`是`＝現在允許；`WAIT 時是`＝僅無價／主軸未開火；`否`＝不要先做。

### 2.1 市場／預測／凍結／結構

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **M1** | R15-01 | 日更 tip≥08-13 | 候價 → `run_daily_asof_predict.sh --date 2026-08-13 --horizons 20,60` → L2 `--apply`（L1 RC=0；no-promote）。Watcher 已 ARMED | **否**（無價不能做） | 開火時**獨佔**日更槽 | 🟡 **主軸 WAIT** |
| **M2** | R15-02 | econ／dgate | **不修綠**；披露 H20=dead／H60=thin | **是** | **是** | 🟢 `M2-ECON-DISCLOSE-0812` |
| **M3** | — | graph tip 邊 | — | — | — | 🟢 |
| **M4** | — | H82 ghost | — | — | — | 🟢 |
| **M5** | — | r15 文檔 | 本計畫落地後跟本檔 | — | — | 🟢 |
| **M6** | R15-18 半 | ARCHIVE 後未入倉 | 與 **K17** 同槍：閘＋r15 文檔可另 commit | **是** | **是**（≠B3） | 🟢 同 K17 |
| **M7** | R15-05 | 圖提拔熱路徑 | 另 `VERIFY-graph-cand-go` | **否** | **否**（延後） | 🔴 |
| **M8** | R15-17 市場側 | C1／CYCLE | 不編；見 K10 | **否** | — | 🟢 隔離 |
| **M9** | R15-04 | P6／長窗 | 對帳 08-12 artifact；擴窗**另 plan＋GO** 才訓 | **文件＝是**；訓練＝否 | 文件＝是 | 🟢 對帳；訓❄ |
| **M10** | R15-07／09 | M／β5／NF | 輕監；0812 六族**勿重掃**；殘格須點名卡 | **監看＝是**；開訓＝否 | 監看＝是 | 🟢 本窗監看；開訓❄ |
| **M11** | R15-09 | Dividend | 另 auth | **否** | **否** | ❄ |
| **M12** | R15-09 | sim apply | **禁** | **否** | **否** | 禁 |
| **M13** | R15-08 | 循環依賴文件 | explore-only | 低優先可先讀 | 是（零碼） | 🔴 |
| **M14** | R15-08 | scripts 冗餘 | #29 另計畫 | **否**（延後） | **否** | 🔴 |
| **M15** | R15-10 | 10–14 治權日曆 | 10 月初清單；**不假關** | 排程備忘＝是 | 是 | 🟡 |
| **M16** | R15-03 | standing 五窗殼 | **雙明示**＋改殼 | **否** | **否** | ❄ |
| **M17** | R15-02 | dgate evaluate | 另 GO；禁塗綠 | **否** | **否** | 🟡 延後 |
| **M18** | R15-07 | 其他模型族 | V1 hist＠08-07 **EXECUTED**（A-pack 13）；殘格仍點名；**禁**重掃 0812 | 閘／hist 殼＝是 | 讓 B3 | 🟢 V0＋V1＠08-07；NF❄ |
| **M19** | — | family_chk | — | — | — | 🟢 |
| **M20** | R15-06 | 升格另軌 | 可寫 `PROMOTE-TRACK` 文件；禁 SERVE-SWAP | **文件＝是** | 文件＝是 | 🟢 hold 卡；swap❄ |
| **M21** | — | Wave-A 收官 | — | — | — | 🟢 |
| **M22** | — | RankRidge＠08-12 | 已重訓；換殼另句 | — | — | 🟢 |
| **M23** | R15-14 | tip＋N 實現報酬 | **等價蓋過 tip＋N 日** 才研究 | **否** | **否** | 🔴 |
| **M24** | — | 相對機率看板 | 已修；守 p_beat≠報酬％ | — | — | 🟢 |

### 2.2 知識／顧問

| # | 債 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 狀態 |
|---|---|---|---|---|---|---|
| **K0** | — | S0 breach | `--check`；FIRE 才選開 `--apply` | 巡檢＝**是** | 是（apply 避開 B3 開火） | 🟢 LIVE 0 |
| **K1** | — | S3 lag | 同上 | 同上 | 同上 | 🟢 LIVE 0 |
| **K2** | — | ingest 階梯 | 守 apply 選開 | — | — | 🟢 |
| **K3** | R15-19 | AUTO-LIFT | 常駐即可；**禁抬 >KH2** | **否**（已常駐） | — | 🟢／禁抬層 |
| **K4** | R15-13 | 私有 smoke | 回歸可重跑 | 抽樣＝是 | 是 | 🟢 |
| **K5** | R15-11 | Doc1 純圖 | **hold**；不 OCR 硬開 | **否** | — | 🟢 hold |
| **K6** | R15-13 | ASR 對聽 | 可選抽樣 | 是 | 是（輕） | 🟢 |
| **K7** | — | 8b 產品口吻 | 守 8b＋960 | — | — | 🟢 |
| **K8** | R15-15 | KH8 discrim | **E-keep／stop-at-7** | **否** | **否** | ❄ |
| **K9** | R15-16 | 他域 FT | 另 `adopt` 才訓；現 **plan-only** | **否** | **否** | 🔴 |
| **K10** | R15-17 | C1→feat | 另 GO；禁默加權 predict | **否** | **否** | 🔴 隔離 |
| **K11** | R15-12 | `.msg`／rar | skip-hold 或另 plan | **否** | **否** | 🔴 |
| **K12** | — | KH10 | — | **否** | **否** | 禁 |
| **K13** | — | ext+ask／空包 | 已硬化 | — | — | 🟢 |
| **K14** | — | 問法矩陣 | 可重跑回歸 | 是 | 是 | 🟢 |
| **K15** | — | FillAuto | 守機器閘 | — | — | 🟢 |
| **K16** | — | 假 decline 閘 | 碼已在 8399；產品行為已修 | — | — | 🟢 碼 |
| **K17** | R15-18 | 閘＋帳 **入倉** | `git add` 三碼＋GENERO／r15 文檔；**另句才 commit／push** | **是（本窗可先第一槍）** | **是**（≠B3 開火） | 🟢 入倉（push 另句） |

---

## §3 逐步執行序列（Phase）

### Phase 0｜✅ 已閉（本檔不當工單）

B3＠08-12、L2＠08-12、NF＠0812 六族 EVIDENCE、KH ingest S0／S3、K0–K7／K13–K16 產品閘、KH 分軌、ARCHIVE tag、A2B3 **ARMED**、相對機率雙窗。

### Phase 1｜🟡 現在（主軸 WAIT＋可先／可同步）

| 步 | 何時 | 做 | 不做 | 驗收 |
|---|---|---|---|---|
| **1A** | 價≥08-13 | B3 `20,60` → L2 `--apply` | 假 B3、默五窗、promote | tip=D；#14 誠實；L2 no-promote |
| **1B** | 23:50 無價 | TIMEOUT 帳 | 仍不假跑 | TIMEOUT audit |
| **1C** | **此刻可先** | K17 入倉 | 不開 K9／K8 | ✅ `01e9f28` |
| **1D** | **可同步** | `--check`；M2 披露；M10 不開新族 | `--apply` 搶 B3；重掃 NF | ✅ check 綠；`M2-ECON-DISCLOSE`；`M10-NF-WATCH` |
| **1E** | **可先文件** | M9 長窗對帳；M20 升格 hold 卡 | 開訓／換殼 | ✅ `M9-P6-RECON`；`M20-PROMOTE-TRACK-HOLD` |

**並行規則**：1C／1D／1E 在 **1A 未開火** 時可同時做。1A 開始 → 1D 的 apply／長 LLM **讓路**。

### Phase 2｜主軸閉合後（Steward 選一，不預設全開）

順位建議（仍須各別 GO）：

1. 下一交易日重複 1A（standing）  
2. P6／長窗（有 plan＋GO）  
3. 升格門檻文件定稿（仍 no-promote）  
4. K9 **僅**在 `K9-DOMAIN-FT-plan-adopt` 之後  
5. 圖提拔 VERIFY  
6. NF 殘格（VECM／TCN／NB／Daily*）——**點名卡才 plan**

### Phase 3｜本檔不開

解凍 M／β5；無點名撤 NF-pause；cron B3；sim `--apply`；五窗改 standing；SERVE-SWAP；放寬 θ；depth≥8；KH10；K10 默灌預測；對話 approve 來源；整庫回填當進化。

---

## §4 工作包（開跑複製）

### WP-M1｜市場主軸（最佳下一步①）

```text
WHEN: PriceAdj≥2026-08-13
DO:   bash scripts/run_daily_asof_predict.sh --date 2026-08-13 --horizons 20,60
      bash scripts/run_daily_retrain_l2_all_rank.sh --date 2026-08-13 --apply
DONT: 假 B3; sync-B; sim-apply; 默五窗; promote
DONE: RC=0 + EXECUTED + #14 誠實
NOTE: watcher pid 230370 已 ARMED；人工只在死／TIMEOUT 介入
```

### WP-K17｜假 decline 入倉（可先①）

```text
WHEN: 現在（不等價）
DO:   三碼 compact_answer / advise / oai_compat
      + audits/KH-GENERO-TP3X-FALSE-DECLINE-*
      +（可同批）r15 理解／人話／本檔／KH 選刀
DONT: --no-verify; 開 K9; 改 θ
DONE: Steward 明示才 git commit／push
```

### WP-KD｜KH 巡檢（可同步）

```text
WHEN: 任意；避開 B3 開火
DO:   python scripts/kh_ingest_trigger.py --check
DONT: 無 FIRE 卻 --apply; 日曆假進化
DONE: S0=0 S3=0 priority_hit∅
```

### WP-F｜凍結輕監（可同步）

```text
WHEN: 任意
DO:   確認無新族默訓; 不重掃 0812
DONT: NF-*-go 無點名
DONE: 無違規 job
```

---

## §5 與深化理解債表（R15-* → 本板）

| R15 | 本板 | 本窗處置 |
|---|---|---|
| 01 日更 | M1 | **最佳下一步①** WAIT |
| 02 econ | M2／M17 | 可先披露；evaluate 延後 |
| 03 五窗殼 | M16 | ❄ |
| 04 P6 | M9 | 可先**文件** |
| 05 圖提拔 | M7 | 延後 |
| 06 升格 | M20 | 可先**文件**；禁 swap |
| 07 NF | M10／M18 | 監看∥；禁重掃 |
| 08 scripts | M13／M14 | 延後 |
| 09 M／sim／Dividend | M10–12 | ❄／禁 |
| 10 日曆 | M15 | 排程 |
| 11 Doc1 | K5 | hold |
| 12 msg／rar | K11 | skip-hold |
| 13 私有／ASR | K4／K6 | 可選抽樣∥ |
| 14 tip+N | M23 | 延後等價 |
| 15 KH8 | K8 | ❄ E-keep |
| 16 K9 | K9 | 延後／另 adopt |
| 17 K10 | K10 | 隔離 |
| 18 假 decline 入倉 | K17／M6 | **可先第一槍** |
| 19 AUTO-LIFT>KH2 | K3 | 禁 |

---

## §6 細節板（本檔不取代長指令）

| 用途 | 路徑 |
|---|---|
| 理解地基 | `reports/augur_deep_understanding_and_opt_plan_r15_20260813.md` |
| 人話憲章 | `reports/augur_project_charter_plain_zh_r15_20260813.md` |
| 市場長板 | `reports/augur_opt_stepwise_best_next_plan_r15_20260813.md` |
| KH 長板 | `reports/augur_kh_opt_stepwise_best_next_plan_20260813.md` |
| NF 殘格 | `audits/NF-0812-RESIDUAL-NAME-CARD-20260813.md` |
| S1→S5 閉環運轉 SSOT r16 | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md` |
| S1→S5 本質／08-04 GO | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` |
| S1→S5 r16 本窗執行板 | `reports/augur_s1s5_r16_exec_board_20260813.md` |
| hist as-of 殼 | `scripts/run_asof_collect_train_verify.sh` |
| 其他模型 V0 | `audits/S4-V0-INVENTORY-20260813.md` |
| KH8 硬門 | `audits/KH-HARD-GATE-CARD-20260813.md` |

衝突：開工順序與「可先／可同步」**以本檔為準**；殼指令與 GO 文案以長板／audit 為準。

---

## §7 何時刷新（r16／改本檔）

1. M1 閉合（EXECUTED 或 TIMEOUT）；或  
2. K17 已 commit；或  
3. Steward 雙明示改 standing／升格／解凍／K9 adopt。

---

## §8 驗收（本計畫書）

- [x] 全專案開問題入板（市場＋知識＋凍結＋結構）  
- [x] 每列有最佳下一步＋可先＋可同步  
- [x] §1 決策卡可當「現在只做這些」  
- [x] 分軌：知識可先**不等價**；市場主軸不因 KH 停  
- [x] 聲明：後續優化**依本檔**；長板＝細節  

*完。[I] · r15 全專案逐步執行 SSOT。*
