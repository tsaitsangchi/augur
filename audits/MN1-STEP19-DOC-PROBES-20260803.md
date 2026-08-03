# M-N1 第 19 步落地帳：文件硬編數字→探針 diff（2026-08-03）

> 位階：[I] · 對應 `reports/augur_optimization_master_plan_20260803.md` 第 19 步驗收②（7 處 live 文件）
> 前帳：`audits/MN1-MN2-LANDING-20260803.md`（骨架）· 紀律：M-T5 守（零 heavy_slot／零 evolution driver／零 `--allow-apply`）、FZ-keep（零 FinMind／FRED）、未 commit／push

## 機制（本輪新增）

1. **`sync_treaty_probes.py --seed-doc`**：新增 `SEED_DOC` 11 條 doc 族綁定（owner=AI、無 deadline、每列攜 `measure_key/ruler_key` FK——驗收③）。
2. **`register_measure.py --register-defaults`**：DEFAULTS 3→11 把尺（crontab_entries／deferred_work_uncleared／validation_evidence_status／lint_total_errors／lint_selftest_status／wm36_registry_tables／vendor_direct_bind／pg_memory_settings；全 `authoritative=false`，標權威仍 Steward）。
3. **`read_treaty_probes.py --check` 加「文件標記 diff」**：凡 clause_ref 檔內含 `<!--probe:ID-->值<!--/probe-->` 標記者，當場重跑 `check_cmd`、文件值≠live 值即 **rc≠0**。純函式 `_marker_mismatches` 餵真輸入紅綠雙向自測（#35 規則 1；無字面斷言）。

## 7 處覆蓋（master 第 19 步驗收② 指名清單）

| # | 指名處 | 處置 | probe_id |
|---|---|---|---|
| 1 | `HANDOFF.md:26`（crontab 15；另 M-N4 之 :50 deferred、:51 VE） | ✅ 三處皆改標記引 probe | `doc_handoff_cron_lines`／`doc_handoff_deferred_uncleared`／`doc_handoff_ve_status` |
| 2 | `CLAUDE.md:127`「137/137」 | ⛔ **殘（M-N3 需裁，治權檔）**——綁定已立、擬改前後見下節，未動文字 | `doc_claude_scripts_matrix`（已綁、待裁後落標記） |
| 3 | `GROUNDING-MAP.md:45-47` 三列 | ⛔ **殘（M-N5 需前置 M-N7 權威尺）**——未綁、未改 | — |
| 4 | F2 備料兩處（`reports/augur_1014_review_evidence_prep_20260801.md:43`／`:49`） | ✅ 追加式「追記」節（正文不改），標記引 probe | `doc_f2_registry_tables`／`doc_f2_vendor_bind_grep` |
| 5 | `tools/constitution_lint/github-workflow.yml` 檔頭 | ✅ 加探針同綁行（total_errors＋selftest 現況）；不動並行工單（M-L7 敘）之文字 | `doc_workflow_lint_errors`／`doc_workflow_selftest_status` |
| 6 | 記憶 2 檔（`augur-three-gate-strengths`／`db-import-tuning-hnsw-oom`） | ✅ handoff 副本＋活 memory 同步（07-31 史述數字加限定詞、不改正文；live 現值走標記） | `doc_mem_tgs_matrix`／`doc_mem_tgs_ve`／`doc_mem_pg_tuning` |

## 先驗紅（#35：凡新回歸鎖必先驗紅）

- 手改 `HANDOFF.md` 標記 15→**14** → `--check` 印 `✗ 文件漂移 doc_handoff_cron_lines: 文件='14' live='15'`、**rc=1**；復原後綠。
- **驗紅過程順手抓到一條真漂移**：並行工單同時段新增 script，`check_cmd_matrix` 受檢數 494→**495**，`doc_mem_tgs_matrix` 標記即紅；以 check_cmd 現值機械回填後綠——機制上線首日即攔到真手抄腐爛。

## 驗收 rc（2026-08-03 現查）

| 條件 | 結果 |
|---|---|
| `read_treaty_probes.py --check` | **rc=0**（綁定 24｜缺 reading 0｜Steward 非 undecidable 0｜文件標記 diff 0） |
| 先驗紅（手改一位數） | **rc=1** ✅（紅證見上） |
| 每列攜 `ruler_key` FK（驗收③） | DB FK `treaty_probe_binding_ruler_fk` 強制；11 條 doc 族全過 |
| `check_cmd_matrix` | **rc=0**（受檢 495／缺漏 0） |
| 三支改動腳本 `--selftest` | 全綠（sync／read／register） |
| M-N4 三處與現查一致＋旁附可重跑指令（驗收④） | ✅（crontab 15、deferred 0、VE total=25 green=14 red=9 unverified=2——master 抄「19／red 3」本身已過期，正證本步必要性） |

## 擬改前後（M-N3，候 Steward 裁；依 #19 逐段呈、AI 不動治權檔文字）

`CLAUDE.md:127`（#28 本地審議引擎段末句）：

- **改前**：`**地基＝scripts/ 全量守 #29(a)(d)**（2026-07-11 稽核 137/137：個別可執行＋執行指令矩陣＋graceful 無參數）。`
- **擬改後**：`**地基＝scripts/ 全量守 #29(a)(d)**（2026-07-11 稽核當日 137/137：個別可執行＋執行指令矩陣＋graceful 無參數；現值＝probe \`doc_claude_scripts_matrix\`——<!--probe:doc_claude_scripts_matrix-->495<!--/probe--> 支受檢、\`python3 scripts/check_cmd_matrix.py\` 現查，\`read_treaty_probes.py --check\` 驗 diff，歷史數字不作現況引用）。`
- 性質：保留史述、加限定詞＋探針標記；惟 CLAUDE.md 為 L6 治權檔（M-N3 在 master 明標 🔴 需裁），**未落文，候裁**。

## 殘項（誠實）

1. **M-N3**（CLAUDE.md:127）——需裁；綁定與擬改稿已備。
2. **M-N5**（GROUNDING-MAP.md:45-47 三列）——需前置 **M-N7**（vendor 權威尺選定，Steward）；本輪僅登錄 `vendor_direct_bind/grep_from_taiwan_src_scripts` 一把尺（authoritative=false）供比對，未代裁。
3. `measure_registry` 11 把尺全 `authoritative=false`——批次標權威＝第 20 步驗收①（Steward）。
4. 記憶檔 `three-gate-strengths` 之「零 CI 零 git hook」等**非數字現況句**僅加「07-31 當日值」限定詞；全面稽核屬 M-N15（第 24 步）。
5. 漂移速率警示：本工作 3 小時窗內 `check_cmd_matrix` 受檢數 482→494→495——doc 標記將隨並行批持續變紅，**紅＝機制在工作**，以 `--check` 輸出回填即可（勿手抄）。
