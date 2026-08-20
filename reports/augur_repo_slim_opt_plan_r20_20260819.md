---
title: augur 倉精化——合併精要／逐步刪重複計畫書 r20
status: slim_exec_ssot
series: repo_slim
round: r20
role: **只**管倉精化（讀序／去重／刪未用）；不取代 r19 市場開工鎖
date: 2026-08-19
viewpoint: 2026-08-19T16:57+08:00
layer: "[I]"
depends_on:
  - reports/augur_deep_understanding_and_opt_plan_r20_20260819.md
  - reports/SSOT_READ_ORDER.md
  - reports/augur_opt_stepwise_all_problems_r19_20260819.md
implements: R19-09／M14／R20-01／R20-02／R20-11／R20-12／R20-13
self_reported: true
---

# augur 倉精化計畫書 r20（2026-08-19）

> **一句**：把專案「合併為精要」＝給讀者一條 **≤15 檔讀序**；「逐步刪」＝只刪**有證據**的重複／未用，預設 **搬進 `archive/`** 而不是 `rm`。  
> **位階**：[I]；不創 [N]。本檔＝M14 那份「#29 另計畫」。市場心跳仍跟 r19。  
> **覆蓋**：盤點指令見 §2；入鏈圖方法見 §3。非整庫逐行複讀。

---

## §0 協議（怎麼瘦才不算自我欺騙）

```text
精要 ≠ 把 524 份 md 貼成一份
精要 ＝ SSOT_READ_ORDER.md（現行入口）＋舊文留繼承鏈

刪除門檻（同時）：
  1) 重複：byte-identical 或明確被 supersede 且無人再當開工入口
  2) 未用：heartbeat／cron／tests／install_services／src import／紙本 GO 皆無引用
  3) Steward 點名（T1 起；T0 僅允許「無引用的 byte-identical」）

永遠不進刪除候選：
  constitution/  specs/  docs/三件套  CLAUDE.md
  src/augur/** 熱路徑
  日更殼 B3／L0／L2／RETRAIN-ALL／check_asof_ready／train_ranker／predict_asof
  install_cron.sh 所列、live crontab 所列
  audits/*-GO|FIRED|EXECUTED|ADOPTED|LOCKED 紙本

複審鐘 ≠ 刪除鐘：
  日曆滿 N 天 ≠ 未用 ≠ 授權 rm
  T5＝對已進 archive/ 且已在 annotated tag 的檔，滿 90 天列入可審清單
  清單預設 KEEP；下一步仍須 Steward 點名（T5b），不是 cron rm
```

**Hard doors（精化專用，疊在 r19 門上）**：

```text
no-mass-delete-reports | no-mass-delete-audits | no-delete-scripts-in-T0
| filename-miss ≠ unused | migrate_horizon_* = KEEP
| archive-first | no-calendar-ttl-delete | review-clock ≠ rm
| no-commit-unless-asked
| no-fake-B3@08-19 | 精化≠改產品行為
```

---

## §1 決策卡

| 問 | 答 |
|---|---|
| **精化最佳下一步** | T0–T4＋T6＋**T7 已做**。T5＝90 天複審鐘**候選**（未開火；最早≈**2026-11-17**） |
| **合併精要在哪** | `reports/SSOT_READ_ORDER.md` |
| **現在動了什麼** | T0：1 CSV。T1：五支腳本。T2：31。T3：14。T4：7。T5：只寫計畫。T6：1 leftover。T7：1 份 sim 專章草案 → `archive/slim-t7/` |
| **為什麼不刪 169 支「零入鏈」腳本** | 多數其實寫在 audits／reports；補紙本後只剩 16；16 裡含活窗 migrate |
| **可與市場 WAIT 同步？** | T0 已同步。T1／T6／T7 搬檔＝是（零碼）但**須點名**。T5 產清單＝是但**須點名且鐘到** |
| **不要做** | 把 superseded 理解長文一次打包刪掉；刪 `migrate_horizon_5.py`；刪 GO 紙本；當 08-19 為 as-of；**用滿 90 天當 rm 授權**；打包刪七月報告 |

---

## §2 盤點（2026-08-19 親查）

產生方式：`find`／`git ls-files`／`md5sum`；排除 `venv/`、`.git/`、`models_artifacts/`。

| 區 | 數量 | 註 |
|---|---|---|
| `src/augur` `*.py` | **151** | 17 領域 package（+ `__pycache__` 目錄勿算） |
| `scripts/` py+sh | **414** | CLAUDE #29 要矩陣；不是「都可以刪」 |
| `reports/*.md` | **524** | git 追蹤 reports **525**（含非 md） |
| `reports/` 全檔 | **551** | 另有 gitignore 的 json dump |
| `audits/` | **1106** | 紙本；禁默刪 |
| `constitution/` | **59** | [N] |
| `specs/` | **14** | [N] |
| `tests/*.py` | **30** | |
| `docs/` | **18** | |
| `tools/` git | **51** | 工作樹 tools 檔數可更高 |
| `handoff_memory/` | **82** | 不拼進精要 |
| `ops/` git | **67** | `find ops` 曾見 **1077**＝其中 gpu-test-venv **1010**（gitignore） |
| `reports/*.json` git | **1** | 其餘 json 已 ignore |
| 追蹤 `*.pyc`／`logs/` | **0** | 已乾淨 |
| `status: superseded` 報告 | **9** 檔（另有 superseded_exec 等） | **留歷史**；T2 才考慮搬 archive |
| 理解系列 `augur_deep_understanding*` | **15** | 現行＝r20 |
| 執行板系列 `augur_opt_stepwise*` | **10** | 現行開工＝r19 |
| 人話憲章 | **6** | 現行＝r19 |
| byte-identical reports 組 | **1 組**＝3 份 identity CSV | T0 處理 1 份 |

封存 tip＝`archive-20260819-b3-hist-slim-r20`（commit `63752bb`；回填 `3bd1a37`）。T5 複審鐘 **epoch＝2026-08-19**（此 tag 日；T0–T4 檔當日入 `archive/`）。

---

## §3 入鏈圖（scripts）—方法與誠實上限

**方法**：對 `scripts/*.py|*.sh` 搜檔名於 `src/` `tests/` `scripts/`（除自身）`tools/` `docs/` `constitution/` `ops/` `CLAUDE.md` `HANDOFF.md` `install_cron.sh` `install_services.sh`。再把「零命中」拿到 `reports/`+`audits/` 複核。

**結果**：

| 桶 | 支數 | 含義 |
|---|---|---|
| heartbeat／cron 保底 | 32 | **永不刪** |
| 碼側入鏈 ≥3 | 74 | 留 |
| 碼側入鏈 1–2 | 139 | 多半是被一支殼或一篇 md 點名 |
| 碼側入鏈 0 | **169** | **不是**刪除清單 |
| 上列 169 在 reports／audits 仍被點名 | 153 | 探針／migrate 的紙本活著 |
| 碼＋紙本皆 0 | **16** | T1 **最高審視**，仍預設 KEEP |

**16 支（檔名在碼＋紙本皆未出現）**：

```text
KEEP（活系統／窗／閘，即使沒人寫檔名）：
  migrate_horizon_5.py
  migrate_horizon_10.py
  migrate_horizon_240.py
  migrate_direction_ruling_ddl.py
  migrate_assist_run_guard_ddl.py
  migrate_revalidation_baseline_ddl.py
  migrate_trial_ledger_recipe_ddl.py
  check_kh1_bypass.py
  check_kh8_band_consumption.py
  seed_authorization_grants.py
  seed_sim_arena_validation_evidence.py

T1 才准 Steward 點名審視（仍不是現在刪）：
  build_item_text_from_payload.py
  check_isolation_outer_pkgs.py
  enrich_re3data_sources.py
  report_principle_candidates.py
  report_term_coverage.py
```

上限：動態 `importlib`、crontab 變數、Steward 口頭指令、只存在於對話 transcript 的用法，入鏈圖**看不見**。所以 T0 刪腳本＝自我欺騙。

cron 現用（live `crontab -l`，刪之即斷心跳）：

`run_evolution_chain.sh` · `evolve_cycle.py` · `evolve_self_seek.py` · `notify_failure.sh` · `gpu_verify.sh` · `check_selftest_coverage.py` · `check_finmind_quota.py` · `run_arena_daily_pipeline.py` · `settle_arena_labels.py` · `run_retrain_all_asof_daily.sh` · `mine_steward_questions.py` · `triage_questions.py` · `pull_desktop_evolution_delta.sh` · `report_triple_evolution_week.py` · `verify_validation_evidence.py` · `backfill_fulltext_unattempted.py` · `backup_database.sh` · `run_evolution_iteration.py` · `run_raw_evolution_iteration.py`

---

## §4 分階段

### T0（本窗 · 已執行）

**目標**：合併精要可見；只動「無引用 × byte-identical」。

| 動作 | 結果 |
|---|---|
| 寫精要讀序 | `reports/SSOT_READ_ORDER.md` |
| 寫理解 r20 | `reports/augur_deep_understanding_and_opt_plan_r20_20260819.md` |
| 寫本計畫 | 本檔 |
| README 加運轉讀序鏈 | 治權讀序之下、不雙寫義務 |
| r19 M14 從「另計畫／否」改指向本檔 | 市場鎖仍＝r19 |
| 搬 duplicate CSV | `reports/identity_retire_name_mismatch_20260718.csv` → `archive/slim-t0/`（md5＝0801；全倉零引用） |
| **不**刪 | 任何 script（T0）、任何 audit 紙本、`20260722_gb10.csv`（有引用）；RIDGE 雙 JSON 改到 T1 |

驗收：讀序 ≤15；刪除數＝**1 檔搬遷**；heartbeat 檔一字未動。

### T1（Steward「執行 T1」· **已執行** 2026-08-19 15:57）

| 動作 | 結果 |
|---|---|
| JSON 去別名 | `audits/RIDGE-THEN-PB-0818.json`＝指針；內容 SSOT＝`audits/RIDGE-THEN-PB-LS-0818.json`（md5 `a88ce3ae…`）。**未改** LONG EXECUTED 正文路徑 |
| 五支腳本 | `git mv` → `archive/slim-t1/`（見該目錄 README） |
| 稽核 | `check_cmd_matrix.py` rc=0（受檢 570／缺漏 0）；`--selftest` 過；`check_selftest_coverage.py --selftest` 過；`OUTER_PKGS` 仍在 `src` |
| 禁止項 | 未動 migrate_horizon_*、cron、probe_* |

證據帳：`audits/SLIM-T1-EXECUTED-20260819.md`。

### T2（Steward「下一槍精化＝T2」· **已執行** 2026-08-19 16:02）

31 份 superseded 舊輪報告 `git mv`／`mv` → `archive/slim-t2/`（清單見該目錄 README）。`SSOT_READ_ORDER` 留鏈。`handoff_memory/`、`GROUNDING-MAP.md`、audits 紙本**未**動。

現行仍在 `reports/`：理解 r20、執行板 r19、憲章 r19、as-of 刀 r19、KH readout、r16、PATH-OPT 手冊、slim r20。

證據帳：`audits/SLIM-T2-EXECUTED-20260819.md`。

### T3（Steward「要執行 T3」· **已執行** 2026-08-19 16:27）

14 份祖先計畫 `git mv` → `archive/slim-t3/`（清單見該目錄 README）。**未搬** 08-04 閉環 GO。`SSOT_READ_ORDER` 留鏈。

證據帳：`audits/SLIM-T3-EXECUTED-20260819.md`。

### T4（Steward「要執行 T4」· **已執行** 2026-08-19 16:33）

7 份 `augur_opt_next_best*.md` `git mv` → `archive/slim-t4/`。**未搬** KH 20260812 選刀檔。08-04 GO `based_on` 已改指 archive。

證據帳：`audits/SLIM-T4-EXECUTED-20260819.md`。

### T5（Steward「把 90 天複審鐘寫進 slim」· **候選 · 未開火** 2026-08-19 16:43）

**性質**：複審鐘，**不是**刪除鐘。寫進本計畫 ≠ GO ≠ 授權 `rm`／`git rm`。

| 欄 | 內容 |
|---|---|
| **對象** | 已 `git mv` 進 `archive/slim-t0`…`t7/` **且**已在 annotated tag 的檔 |
| **epoch** | `archive-20260819-b3-hist-slim-r20` 之日＝**2026-08-19** |
| **滿 90 天** | 最早可審日≈**2026-11-17**（08-19＋90） |
| **開火句** | Steward 點名「執行 T5」**且**日曆 ≥ 最早可審日 |
| **開火做什麼** | 產出 `audits/SLIM-T5-REVIEW-LIST-YYYYMMDD.md`：路徑、入 archive 日、所在 tag、建議＝**KEEP** |
| **開火不做** | `rm`；`git rm`；改讀序鏈；搬現行 SSOT；動 heartbeat／[N]／GO 紙本；cron 自動掃刪 |
| **鐘未到** | 即使點名「執行 T5」→ 寫「未到期／清單空」帳；仍不刪 |
| **清單之後** | 個別檔若要再瘦＝**T5b 另句點名**（仍預設 archive-first，不是默 rm） |
| **不在 T5** | `reports/` 現行入口；`scripts/` 未搬檔；`audits/*-GO\|FIRED\|EXECUTED`；生成物 dump／`models_artifacts`（磁碟 TTL 另軌，非 M14） |

```text
WHEN: Steward「執行 T5」AND today >= 2026-11-17
DO:   列 archive/slim-t{0,1,2,3,4,6,7}/ 滿 90 天檔 → REVIEW-LIST（預設 KEEP）
DONT: rm; git rm; cron 刪; 改 SSOT 鏈; 當日曆＝未用
DONE: REVIEW-LIST 入 audits/ + 本節標 EXECUTED（清單≠刪除）
```

候選帳：`audits/SLIM-T5-REVIEW-CLOCK-CANDIDATE-20260819.md`。

### T6（Steward「點名 T6」· **已執行** 2026-08-19 16:50）

1 份無引用 leftover：`augur_pme_gate_diagnosis_20260724.local-backup.md` `git mv` → `archive/slim-t6/`。正式 `20260724.md` **未搬**。

**未搬**：`identity_retire_name_mismatch_20260722_gb10.csv`（ops 仍點檔名）；七月單題打包；PME 日更長河；任何 `.py`。

證據帳：`audits/SLIM-T6-EXECUTED-20260819.md`。

### T7（Steward「點名 T7」· **已執行** 2026-08-19 16:57）

1 份無引用專章草案：`augur_sim_evolution_chapter_draft_20260731.md` `git mv` → `archive/slim-t7/`。**必留** `…_final_20260731.md`。

**未搬**：`0722_gb10.csv`；七月打包；PME 日更；任何 `.py`；08-04 GO。

證據帳：`audits/SLIM-T7-EXECUTED-20260819.md`。

---

## §5 與 r19 板的關係

| 項 | 誰說了算 |
|---|---|
| 現在市場做哪槍 | **r19**（刀 B WAIT 價） |
| 現在怎麼瘦倉 | **本檔** |
| S1→S5 怎麼轉 | r16 |
| 路徑 θ／GO 文案 | PATH-OPT r18 |
| 理解 LIVE | **r20**（r19 14:05 段過期） |

r19 **M14** 本窗改為：T0–T4＋T6＋T7 已閉；T5＝90 天複審鐘**候選**（未開火；≠rm）。

---

## §6 驗收

- [x] 精要＝索引，不是拼接全書  
- [x] T0 只搬 1 個有 md5＋零引用證據的 CSV  
- [x] 公布 16 支「雙零入鏈」並標 KEEP／審視，避免把 migrate 當垃圾  
- [x] T1：RIDGE 指針＋五支腳本進 `archive/slim-t1/`；`check_cmd_matrix` 570／0  
- [x] T2：31 份舊輪報告進 `archive/slim-t2/`；讀序留鏈  
- [x] T3：14 份祖先計畫進 `archive/slim-t3/`；08-04 GO 未搬  
- [x] T4：7 份 opt_next_best 進 `archive/slim-t4/`；KH 0812 未搬  
- [x] 不刪 heartbeat、不刪 [N]、不刪 GO 紙本  
- [x] 不假 B3、不 promote、不代 commit  
- [x] T5 寫成 90 天**複審鐘**候選；**未**開火；**未**當刪除 TTL  
- [x] T6：1 份 PME local-backup 進 `archive/slim-t6/`；正式 0724 未搬  
- [x] T7：1 份 sim 專章草案進 `archive/slim-t7/`；final 未搬  
- [ ] T5 開火（須點名且 ≥2026-11-17）→ REVIEW-LIST；預設 KEEP  

*完。[I] · slim exec SSOT · T0–T4＋T6＋T7 EXECUTED · T5 CANDIDATE（review-clock ≠ rm）。*
