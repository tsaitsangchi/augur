---
status: final
series: optimization_plan
round: r6
depends_on:
  - reports/augur_deep_understanding_r6_20260804.md
  - reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
---

# augur 專案優化計畫書 r6（2026-08-04）——地基＝深化理解報告 r6

> **性質**：[I] 優化排序建議，供 Steward 選擇下一手 GO；**不創設治權判準**、**不含任何 `--apply`／`--allow-apply`／自動執行**。
> **地基**：`reports/augur_deep_understanding_r6_20260804.md` §7（36 項綜合債表）。本檔只做「歸軌＋排序＋落點」，不重複展開債之描述。
> **與既有 SSOT 之關係**：predict 閉環相關項（S3 Wave C/D/E、S5 寫庫／sim 等）之計畫本體**已存在**於 `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`——本檔**不重造**，只標其優先序位置；本檔新增值＝**治理收斂／程式結構／scripts 體積**三軌（本輪首次全量結構盤點才浮現）之排序建議。
> **判準（CLAUDE #26 裁決句沿用）**：「搞錯會不會沉默污染下游？會→歸理解軸／須 Steward GO；僅慢／純機械修正（改錯字／補一欄／刪自認過時檔）→執行層 AI 可主動，但**逐項仍先呈過目**（#19），不批次動手。

---

## §0 四軌總覽

| 軌 | 範圍 | 項數 | 已有 SSOT？ |
|---|---|---:|---|
| **A. 治理收斂軌** | RULING 043 簽核、CS 漂移、10-14 日曆項、V2-SUNSET 矛盾 | 6 | 部分（`reports/augur_1014_review_evidence_prep_20260801.md`） |
| **B. Predict 閉環深化軌** | S3 Wave C/D/E、S5 寫庫/sim、序列窗契約、模型 backlog | 16 | **有**（`augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md`＋各 Wave 帳） |
| **C. 程式結構健檢軌** | action_log 接線、循環依賴、命名邊界、lint 債 | 5 | 無（本輪新提） |
| **D. scripts／ops 體積收斂軌** | 死碼、外來殘片、同型合併、暫存檔歸位 | 9 | 無（本輪新提） |

**排序原則**：①治理矛盾／簽核缺口（影響效力认定）優先於一般品質債；②「牴觸現行 [N]/[I] 規則」（如 D 軌 #21 `sync_memory.sh` 違 #14）優先於「單純冗餘」；③新能力（B 軌）之排序沿用既有 SSOT 之波次序，本檔不重排；④C／D 軌屬「改正確／補完整」執行層，可批次但仍逐項呈目。

---

## §1 A 軌：治理收斂（對映 r6 §7.1/#1-4、§7.2/#14-16）

| 優先 | 項 | 建議動作 | 需 Steward GO？ |
|---|---|---|---|
| **P0（2026-08-04 復查降級）** | `direction_gate`「≥60」vs 凍結值「250」判準級矛盾 | **live 復查**（`SELECT criteria->>'min_clusters',status...`）：250 之 11 門（9 approved／2 evaluated_fail）——250≥60 非違憲（07-31 r2 對抗核驗已指正「抓錯方向」，本輪重驗證實）；**原真違規**（36 之 6 門 approved，低於 60）**現況皆已 `superseded`**、非 `approved`——**現況無任一 approved 門使用 <60 之值**。殘餘僅「條文字面『≥60』是否要明文對齊 250」之**文字/文檔層**問題，非安全違規 | **否**（降為 P2 文字層；不再是阻斷級）——如需仍可請 Steward 一句定調 |
| **P0（2026-08-04 已簽核）** | ~~RULING-2026-043 待簽核~~ | 內容三批施作皆已機械驗證（15 表掛 `honesty_ledger_guard`），僅缺簽核欄——Steward 經 `AskQuestion` 選 `sign_now`，已於 `constitution/RULING-2026-043-B4-UPDATE-GUC-EXPANSION.md` 簽核欄填入 hugo＋2026-08-04＋留痕本次對話指示 | 否（已簽核生效） |
| **P0（2026-08-04 已解決）** | ~~WM.36 registry 缺口——`tw.daily_bar` 概念同掛 raw／adjusted 兩表，`resolve()` 只給權威（現指 raw），無法指名 adjusted；`build_stock_graph_edges.py` 因此撞閘~~ | **已執行選項 A**：新概念卡 `tw.daily_bar_adjusted`（binding_id=100）登錄＋接線，行為不變性驗證通過（13,021 邊零差異）；`check_vendor_binding --gate` 該檔之 `TaiwanStockPriceAdj` 一項已消除。詳見 `audits/WM36-GAP-OPTION-A-EXECUTED-20260804.md` | 否（已裁已執行）——**新殘留**：`TaiwanStockInfo`（產業分類）語意錯配為獨立缺口，另案呈裁 |
| **P1（2026-08-04 已解決）** | ~~`TaiwanStockInfo`（`build_stock_graph_edges.py` 產業分類來源）掛靠 registry 之唯一概念為 `tw.roster_membership`（binding 28，語意＝上市名冊成員），與「產業分類查詢」語意不符~~ | **已執行**：新概念卡 `tw.stock_industry_category`（binding_id=102）登錄＋接線＋行為不變性驗證通過；`check_vendor_binding --gate` 該檔零殘留直綁。詳見 `audits/WM36-GAP-TAIWANSTOCKINFO-EXECUTED-20260804.md` | 否（已裁已執行） |
| P1 | V2-SUNSET 續命三條全未達成 | 監看 08-02 prodset active=3 之後續增長；不主動觸發 SUNSET consequence | 否（監看，碰護欄停） |
| P1 | 2026-10-14 六筆日曆項並列 | 沿用既有備料報告；建議 10 月初集中複核一次 | 否（排程提醒） |
| ~~P2~~ | ~~CS 版號漂移（v1.53.0 vs v1.54.0）~~ | **2026-08-04 已修正**——標題與 frontmatter `spec-version` 皆改 v1.54.0 | 否，已完成 |
| P2 | `HANDOFF-governance.md` 65 處 lint 標記脫離 `bound_docs` | 需先確認是否重新掛回 `bound_docs`（可能改變凍結語意）——偏保守先問 | 建議先問 |

---

## §2 B 軌：Predict 閉環深化（沿用既有 SSOT 波次序，本檔僅列位置）

> 完整清單見 `reports/augur_deep_understanding_r6_20260804.md` §3.5「待 GO」與 `augur_s3_features_for_market_model_families_20260804.md`／`augur_s4_market_model_families_opt_plan_20260804.md`。本檔不重列細節，只給下一手候選：

| 候選 GO 句 | 對映債（r6 §7 編號） | 備註 |
|---|---|---|
| ~~`S3-WAVE-C-go \| FZ/GATE-keep \| skip-sync \| no-SIM-apply`~~ | 組 10-11 | **已 GO＋EXECUTED（2026-08-04，查核性質）**——`audits/S3-WAVE-C-EXECUTED-20260804.md`：組 10（`market_direction_feature`／`daily_direction_feature_values`）與組 11（`cross_section.py` 交互）之契約**確認已由既有 oracle 主線／Wave-B 期間程式對齊**（非新建）；查核中新發現一項超字面範圍缺口（`probability_oos_sample`/`calibrate_relative_probability`/`train_direction_stack` 三支硬編碼 `RankRidge`，新 Wave-A 6 族尚不能餵 DirStack）已誠實記錄、未擅自執行，另呈候選句 `S4-DIRFAMILY-GENERALIZE-plan-first`（見下新增第 14 項） |
| ~~`S3-WAVE-D-go`~~ | #6（序列窗/圖邊契約缺口） | **已 GO＋EXECUTED（2026-08-04，Phase 1+2a+2b）**——`audits/S3-WAVE-D-EXECUTED-20260804.md`；殘餘＝Phase 2c（圖邊首次寫庫）待另授＋adapter 訓練碼另計（見§2.1） |
| `predict-asof-write-go` | #13（prediction_values 未寫） | 寫既有表 `prediction_values`（已建，非新表） |
| ~~`SIM-FIRST-CELL-go`~~ | #13 | **已 GO＋EXECUTED**（2026-08-04）——格點 `2026-08-03`／52 檔已產／時鐘 K=1/3；`audits/SIM-FIRST-CELL-EXECUTED-20260804.md`；下一格待 label 日（≈21 交易日後）或人工補產 |
| `LOOP-S2-TO-S1-EXPAND-go`／`LOOP-CYCLE-1-go` | C1 Arc B/C | 需 API-THAW-bounded |
| missing adapter 實作（8 族） | #12 | 每族另立 plan-first（不可批次一次做完，各族輸入契約不同）——**S4-Wave-C SeqLSTM**（序列 DL，首族）已 plan-first＋Phase 0a 可行；**S4-Wave-A 剩 6+2 族**（XGB/Cat/RF/SVM/KNN/MLP 同構＋NB/LTR 架構不同,誠實分列)plan-first 已完稿,見 §2.2 |

### 2.1 S3-WAVE-D——plan-first 完稿＋Phase 1+2a+2b 已 EXECUTED（2026-08-04 追記）

> **更正**（原草擬修正紀錄，保留供對照）：本節原草擬「新表 `feature_sequence_window`（讀 `feature_values` 展開滑動窗）」——經 DB 親查，`feature_values.panel_date` 實為**月頻**（113 個 distinct 日期，非日頻），不適合直接展開日頻序列窗；已修正為**組 12 不建新表**（複用既有 `audit.field_correlation.build_stock_panel` 之日頻對齊面板），**組 13（圖邊）才建新表** `stock_graph_edge`。

完整 table schema＋python 程式規畫＋分階段＋驗收，見 `reports/augur_s3_wave_d_sequence_graph_plan_20260804.md`。**執行結果（Phase 1-2c 全數完成）**：`features/sequence.py`／`build_sequence_panel.py`（225/225 核心股 3 窗長皆足窗）；`stock_graph_edge` **已寫入 13,021 邊**（產業共群 1,831＋報酬相關性 5,089/6,101）＠2026-06-30（Phase 2c 經 `AskQuestion` 明示授權）——見 `audits/S3-WAVE-D-EXECUTED-20260804.md`。S4 Wave C/D/E 之 SKIP 理由自此由「缺特徵契約」轉為「缺 adapter 訓練碼」（後者另計，見 §2 表末「missing adapter 實作」列）。

### 2.2 missing adapter 8 族——兩條並行進度（2026-08-04 追記）

| 族線 | 狀態 | 文件 |
|---|---|---|
| **S4-Wave-C SeqLSTM**（序列 DL） | plan-first 完稿→Phase 0a 煙測**可行**（單折 59.5s／全量估 64.4 分）→**Phase 0b 全量評測已完成、誠實未過門**（19 折×3 seed,net Sharpe min 1.1311<冠軍 1.3016;≈42.2 分鐘） | `reports/augur_s4_wave_c_lstm_adapter_plan_20260804.md`／`audits/S4-SEQLSTM-EVAL-20260804.md` |
| **S4-Wave-A 剩 6+2 族**（分類 ML） | plan-first 完稿→6 族 class＋dispatch 寫入生產碼→**Phase 0 評測已完成**（36 次 backtest≈43.2 分鐘）——**12 組合中 `RankSVM`@H20 一項真贏**,其餘 11 未過門 | `reports/augur_s4_wave_a_sklearn_adapters_plan_20260804.md`／`audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md`——6 族（XGB/Cat/RF/SVM/KNN/MLP)同構、零架構風險；NB／LTR 誠實列為架構不同,本輪不做 |

---

## §3 C 軌：程式結構健檢（本輪新提，對映 r6 §7.3/#17-20）

| 優先 | 項 | 建議動作 | Table／程式規畫 |
|---|---|---|---|
| P1 | `execution/action_log.py` 零消費端 | 在 3 個既有決策點接線：`run_evolution_iteration.py`（APPLY 時）、`predict_asof.py`（出單時）、`decide_sim_verdict.py`（promoted/killed 時）呼叫 `action_log.append(...)` | **無新表**（DDL 已遷、既有）；程式規畫＝三個呼叫點各加 1 行 import＋1 行 append 呼叫，函式簽名沿用 `action_log.py` 既有介面 |
| P2 | `advisor↔deliberation`、`core↔audit` 循環依賴 | 分析哪個方向是「真依賴」哪個是「可倒轉」，抽公用介面打斷循環 | 需先讀兩處 import 明細才能定案，不可倉促動刀——建議列入下次 explore 而非本輪直接改 |
| P2 | `models/registry.py` 命名邊界 | 語境可接受，暫不改名（改名影響 import 面廣，效益低於風險） | 不動作 |
| P2 | ~~`evaluation/portfolio.py` SyntaxWarning~~ | **2026-08-04 復驗證偽**——`-W error::SyntaxWarning` 全乾淨匯入、檔內無 `\w` 字面；原判讀誤，**無需修正** | 不動作 |

**本輪已做（2026-08-04／05）**：CS 版號漂移已修正（A 軌 P2）；`portfolio.py` 經復驗證偽、無需動作；**`action_log` 三點接線已 EXECUTED（2026-08-05，見 §5 第 21 項）**。餘循環依賴仍建議先呈報範圍再動手（#19 逐檔紀律）。

---

## §4 D 軌：scripts／ops 體積收斂（本輪新提，對映 r6 §7.3/#21-31）

| 優先 | 項 | 建議動作 |
|---|---|---|
| **P0** | ~~`sync_memory.sh` 自動 `git commit`＋`push origin main`，且寫死他人他機路徑~~ | **2026-08-04 已刪除**——確認零引用（僅本檔＋r6 理解報告提及）後刪除；`sync_memory.py`（Python 版）功能已覆蓋且不越權 |
| ~~P1~~ | ~~`drain_knowhow_admit_to_ceiling.sh`／`arena_settle_oneshot.sh` 自標過時~~ | **2026-08-04 已移至 `archive/`**（確認零功能性消費端後移動，可逆保守處置） |
| ~~P1~~ | ~~`export_milvus_index.py` 疑似死碼~~ | **2026-08-04 已確認零引用並移至 `archive/`** |
| P2 | 全文抓取族八代同堂、`curate_pme_xdom_*` 三胞胎 | 依 #29(c)/(b) 收斂為參數化工具——工程量中等，建議另立小計畫 |
| P2 | run 綁定腳本（`observe_twevo_run22.py` 等） | run 22 結束後移入 `archive/` 或刪除 |
| P2 | 暫存檔（`tmp_runners/`、`scratchpad/`）未歸 `audits/` | 盤點後移正 |
| P2 | `migrate_*_ddl.py` 83 支體積 | **不建議收斂**——換機還原依賴，體積是刻意维护成本非債務，本檔僅記錄不建議動作 |

**建議本輪立即可做**：`sync_memory.sh` 因牴觸 #14 屬**規則層問題**而非單純體積債，建議優先處理；其餘建議先盤點消費端確認零引用後才刪（避免誤刪）。**本輪已做**：三支自標過時／疑似死碼腳本（`export_milvus_index.py`／`drain_knowhow_admit_to_ceiling.sh`／`arena_settle_oneshot.sh`）皆已確認零功能性消費端並移至 `archive/`（D 軌 P1 兩列全清）。

---

## §5 建議序列（回應「可先做或同步做」之慣性提問）

### 可立即平行做（風險低、範圍小、機械修正，各自獨立）——**2026-08-04 已全數處理**

1. ~~`evaluation/portfolio.py` raw-string 修正~~（C 軌 P2）——**復驗證偽，無需修正**（見上）
2. ~~`sync_memory.sh` 停用／刪除確認~~（D 軌 P0）——**已刪除**（確認零引用）
3. ~~CS 版號漂移文字更正~~（A 軌 P2）——**已修正**（`CS-系統架構大憲章_v1.54.0.md` 標題＋frontmatter `spec-version` 由 v1.53.0 改 v1.54.0，對齊檔名與正文 SSOT 指針）

### 需先盤點才能動（不可倉促）

4. ~~D 軌死碼清除（`export_milvus_index.py` 等）~~——**已盤點＋執行**：3 支皆確認零功能性消費端，已移至 `archive/`
5. ~~`action_log` 接線（C 軌 P1）~~——**已 EXECUTED（2026-08-05）**，見第 21 項／`audits/C-TRACK-ACTION-LOG-WIRED-20260805.md`

### 需 Steward 裁決（AI 不可代行）——**2026-08-04 稍晚全數處理**

6. ~~`direction_gate` 判準矛盾~~（A 軌 P0）——**live 復查降級**：現無 approved 門低於 60，非阻斷級，見 §1
7. ~~RULING-043 簽核~~（A 軌 P0）——**已簽核**（hugo，2026-08-04；`constitution/RULING-2026-043-B4-UPDATE-GUC-EXPANSION.md`）
8. ~~WM.36 registry raw／adjusted 概念缺口三選項~~（A 軌 P0）——**已執行選項 A**（新概念卡 `tw.daily_bar_adjusted`，見 §1／`audits/WM36-GAP-OPTION-A-EXECUTED-20260804.md`）；**新殘留**：`TaiwanStockInfo`／`tw.roster_membership` 語意錯配，待另裁（見 §1 新增 P1 列）

### 沿用既有 SSOT、下一手候選 GO 句（B 軌）

8. ~~`S3-WAVE-D-go`~~ **已全數執行**（Phase 1-2c，2026-08-04，見 §2.1）；~~`S3-WAVE-C-go`~~（組 10-11，方向表↔ranker 契約）**已 GO＋EXECUTED**（查核性質，見 §2 表／第 14 項）
9. ~~`predict-asof-write-go`~~／~~`SIM-FIRST-CELL-go`~~ **兩者皆已 GO＋EXECUTED**（2026-08-04）——`SIM-FIRST-CELL`：sim 子閉環 K=1/3；`predict-asof-write-go`：`prediction_values` 225 列（as-of 2026-06-30，RankRidge H60 registry 最新模型）。**S1→S5 主線 predict 側與 sim 子閉環側皆已首次落地**（`audits/PREDICT-ASOF-WRITE-GO-20260804.md`）
10. ~~8 族 missing adapter 之首族——**S4-Wave-C SeqLSTM**~~：plan-first＋Phase 0a 可行性煙測（可行）→**Phase 0b 全量評測已執行完成、誠實未過經濟門檻**（2026-08-04；`audits/S4-SEQLSTM-EVAL-20260804.md`）——19 折×3 seed,3-seed net Sharpe min=1.1311／median=1.1517／max=1.1649,**三者皆低於現任冠軍 `RankRidge_H60` 之 1.3016**（非邊緣未過）;耗時 ≈42.2 分鐘。**不進 Phase 1**;`SeqLSTM` class＋評測 CLI 保留供未來換超參/horizon 重探。8 族首族評測至此收尾（誠實 SKIP 升格，同日第二例，呼應第 11 項 RankEnsemble）。
11. ~~RankEnsemble（RankRidge×RankGBDT 等權融合）plan-first＋Phase 0 評測~~——**已執行、誠實未過門**（2026-08-04；`reports/augur_s4_rank_ensemble_blend_plan_20260804.md`／`audits/S4-RANKENSEMBLE-EVAL-20260804.md`）：H60／H20 3-seed net Sharpe 全數低於冠軍 RankRidge，未進 Phase 1、未新增 model family。`run_economic_eval.py` 之 `ENS_ridge_gbdt` 掛載保留供未來重探。
12. ~~**S4-Wave-A 剩 6+2 族 sklearn adapter**~~——**EXECUTED**：僅 `RankSVM`@H20 真贏＋跨期分半複驗穩健；其餘 11 組合未過。詳 `audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md`。
13. ~~**S3-Wave-B 多 seed 複核**~~——**EXECUTED**：4 候選 0 提拔（staged 保留）。詳 `audits/S3-WAVE-B-EXECUTED-20260804.md` §3。
14. ~~**S3-Wave-C**~~——**EXECUTED**（查核）。詳 `audits/S3-WAVE-C-EXECUTED-20260804.md`。
15. ~~**S4-DIRFAMILY Phase 0**~~——**EXECUTED**（R1/R2＋行為不變性）。詳 `audits/S4-DIRFAMILY-GENERALIZE-EXECUTED-20260804.md`。
16. ~~**P6 AS_OF/exit_date 邊界 A+B**~~——**EXECUTED**。詳 `audits/S4-PROB-ASOF-BOUNDARY-FIX-EXECUTED-20260804.md`。
17. ~~**DIRFAMILY Phase 1（RankSVM@H20→DirStack）**~~——**EXECUTED（2026-08-05）**：步驟 1–4 全完。對齊 16 panel／4,034 列：`DirStack_RankSVM` Brier/hit/AUC **皆未優於**既有 `DirStack`（ΔBrier=+0.0007、Δhit=−0.016、ΔAUC=−0.032）。**不掛 GATE、不升格**。帳＝`audits/S4-DIRFAMILY-PHASE1-EXECUTED-20260805.md`。教訓＝截面經濟尺真贏 ≠ 方向合成變好。
18. ~~**P6 選項 C/D**~~——**EXECUTED（2026-08-05）**：C＝`--asof` 參數化、預設釘 2026-05-31；D＝全量重跑紀律句；**未滾動重灌**。帳＝`audits/S4-P6-ASOF-CD-EXECUTED-20260805.md`。
19. ~~**S4-Wave-B-ADAPTER Phase 0＋0b**~~——**EXECUTED**：Phase 0＝薄殼＋CLI；Phase 0b＝15 股×H20×36 折×train_window=504，ARIMA mean hit **0.5370** > naive **0.5185**（9/15 股贏地板）→ **有證據、不自動 Phase 1**。帳＝`audits/S4-WAVE-B-ADAPTER-PHASE0B-EXECUTED-20260805.md`。
20. ~~**S3-Wave-E gated-keep**~~——**EXECUTED**：組 14–16 維持 gated／N/A／missing。帳＝`audits/S3-WAVE-E-GATED-KEEP-20260805.md`。
21. ~~**C 軌 action_log 三點接線**~~——**EXECUTED**：grant×3；I5 TEMP-RED 修掉（selftest 紅→綠）；`predict_asof`／`decide_sim_verdict` 留痕。帳＝`audits/C-TRACK-ACTION-LOG-WIRED-20260805.md`。
22. ~~**S3 殘帳 β2**~~——**GO＋材料化＋IC EXECUTED（partial）**：`pb_pctile_x_dvlog` 23,850 列；as-of H60 HAC-t≈**−2.81**（過 \|t\|≥2、方向負）；`#11` verify **封存時 in-flight**。帳＝`audits/S3-BETA-BETA2-EXECUTED-20260805.md`。**禁**重跑舊四名 verify。

**收口敘事（2026-08-05 封存切片）**：S1→S5 前向弧已有真實落地；DIRFAMILY P1 未贏、P6 C/D、S4-B 0b 微勝 naive、action_log、β2 IC 皆已入帳。**β2 #11 多 seed 未終表**——見 partial EXECUTED。次選＝等 verify 回填、或換題／β5 停。

---

## §6 驗收方式

- A 軌治理項：以裁決/簽核文件（`constitution/RULING-*`／HANDOFF 更新）為驗收證據。
- B 軌：沿用既有波次模式——GO audit→EXECUTED audit（見歷史 `audits/S{3,4,5}-WAVE-*` 範式）。
- C／D 軌機械修正：`git diff` 對照＋（若涉 script）`python -m` 直跑一次確認無 traceback；ReadLints 確認無新增 lint。

---

*定版（2026-08-04）——依 `augur_deep_understanding_r6_20260804.md` §7 全量債表歸軌排序；不含任何自動執行，等候 Steward 選定下一手。*
