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
| **P0** | `direction_gate`「≥60」vs 凍結值「250」判準級矛盾已呈裁未裁 | 提醒仍待裁；不自行選一方 | **是**——裁決權專屬 Steward |
| **P0** | RULING-2026-043 待簽核 | 提醒仍待簽；HANDOFF「043＝B」不可誤讀為已簽 | **是** |
| P1 | V2-SUNSET 續命三條全未達成 | 監看 08-02 prodset active=3 之後續增長；不主動觸發 SUNSET consequence | 否（監看，碰護欄停） |
| P1 | 2026-10-14 六筆日曆項並列 | 沿用既有備料報告；建議 10 月初集中複核一次 | 否（排程提醒） |
| P2 | CS 版號漂移（v1.53.0 vs v1.54.0） | **純文字更正**——標題數字改對即可，屬「改正確」執行層 | 否，可執行後呈目 |
| P2 | `HANDOFF-governance.md` 65 處 lint 標記脫離 `bound_docs` | 需先確認是否重新掛回 `bound_docs`（可能改變凍結語意）——偏保守先問 | 建議先問 |

---

## §2 B 軌：Predict 閉環深化（沿用既有 SSOT 波次序，本檔僅列位置）

> 完整清單見 `reports/augur_deep_understanding_r6_20260804.md` §3.5「待 GO」與 `augur_s3_features_for_market_model_families_20260804.md`／`augur_s4_market_model_families_opt_plan_20260804.md`。本檔不重列細節，只給下一手候選：

| 候選 GO 句 | 對映債（r6 §7 編號） | 備註 |
|---|---|---|
| `S3-WAVE-C-go \| FZ/GATE-keep \| skip-sync \| no-SIM-apply` | 組 10-11 | 方向表↔ranker 契約／meta，無新表需求（消費既有 `market_direction_feature`） |
| ~~`S3-WAVE-D-go`~~ | #6（序列窗/圖邊契約缺口） | **已 GO＋EXECUTED（2026-08-04，Phase 1+2a+2b）**——`audits/S3-WAVE-D-EXECUTED-20260804.md`；殘餘＝Phase 2c（圖邊首次寫庫）待另授＋adapter 訓練碼另計（見§2.1） |
| `predict-asof-write-go` | #13（prediction_values 未寫） | 寫既有表 `prediction_values`（已建，非新表） |
| `SIM-FIRST-CELL-go` | #13 | sim 首格 cell→settle→eval→verdict，消費既有 sim 表族 |
| `LOOP-S2-TO-S1-EXPAND-go`／`LOOP-CYCLE-1-go` | C1 Arc B/C | 需 API-THAW-bounded |
| missing adapter 實作（8 族） | #12 | 每族另立 plan-first（不可批次一次做完，各族輸入契約不同） |

### 2.1 S3-WAVE-D——plan-first 完稿＋Phase 1+2a+2b 已 EXECUTED（2026-08-04 追記）

> **更正**（原草擬修正紀錄，保留供對照）：本節原草擬「新表 `feature_sequence_window`（讀 `feature_values` 展開滑動窗）」——經 DB 親查，`feature_values.panel_date` 實為**月頻**（113 個 distinct 日期，非日頻），不適合直接展開日頻序列窗；已修正為**組 12 不建新表**（複用既有 `audit.field_correlation.build_stock_panel` 之日頻對齊面板），**組 13（圖邊）才建新表** `stock_graph_edge`。

完整 table schema＋python 程式規畫＋分階段＋驗收，見 `reports/augur_s3_wave_d_sequence_graph_plan_20260804.md`。**執行結果（Phase 1-2c 全數完成）**：`features/sequence.py`／`build_sequence_panel.py`（225/225 核心股 3 窗長皆足窗）；`stock_graph_edge` **已寫入 13,021 邊**（產業共群 1,831＋報酬相關性 5,089/6,101）＠2026-06-30（Phase 2c 經 `AskQuestion` 明示授權）——見 `audits/S3-WAVE-D-EXECUTED-20260804.md`。S4 Wave C/D/E 之 SKIP 理由自此由「缺特徵契約」轉為「缺 adapter 訓練碼」（後者另計，見 §2 表末「missing adapter 實作」列）。

---

## §3 C 軌：程式結構健檢（本輪新提，對映 r6 §7.3/#17-20）

| 優先 | 項 | 建議動作 | Table／程式規畫 |
|---|---|---|---|
| P1 | `execution/action_log.py` 零消費端 | 在 3 個既有決策點接線：`run_evolution_iteration.py`（APPLY 時）、`predict_asof.py`（出單時）、`decide_sim_verdict.py`（promoted/killed 時）呼叫 `action_log.append(...)` | **無新表**（DDL 已遷、既有）；程式規畫＝三個呼叫點各加 1 行 import＋1 行 append 呼叫，函式簽名沿用 `action_log.py` 既有介面 |
| P2 | `advisor↔deliberation`、`core↔audit` 循環依賴 | 分析哪個方向是「真依賴」哪個是「可倒轉」，抽公用介面打斷循環 | 需先讀兩處 import 明細才能定案，不可倉促動刀——建議列入下次 explore 而非本輪直接改 |
| P2 | `models/registry.py` 命名邊界 | 語境可接受，暫不改名（改名影響 import 面廣，效益低於風險） | 不動作 |
| P2 | `evaluation/portfolio.py` SyntaxWarning | docstring 字串加 `r` prefix，1 行修正 | 無新表，1 行 diff |

**建議本輪立即可做（風險最低、影響面最小）**：P2 的 `portfolio.py` raw-string 修正——純字面 lint 修正，符合 #26「改正確」執行層，可直接做後呈目。其餘 3 項建議先呈報給您逐項確認範圍後再動手（#19 逐檔紀律）。

---

## §4 D 軌：scripts／ops 體積收斂（本輪新提，對映 r6 §7.3/#21-31）

| 優先 | 項 | 建議動作 |
|---|---|---|
| **P0** | `sync_memory.sh` 自動 `git commit`＋`push origin main`，且寫死他人他機路徑 | **建議直接停用或刪除**——已牴觸 CLAUDE #14（commit/push 須明示授權），非單純冗餘而是規則牴觸；`sync_memory.py`（Python 版）功能已覆蓋且不越權 |
| P1 | `drain_knowhow_admit_to_ceiling.sh`／`arena_settle_oneshot.sh` 自標過時 | 建議移至 `archive/` 或刪除（各自檔頭已聲明被取代） |
| P1 | `export_milvus_index.py` 疑似死碼 | 建議先確認零引用（grep 消費端）才刪，避免誤刪備援路徑 |
| P2 | 全文抓取族八代同堂、`curate_pme_xdom_*` 三胞胎 | 依 #29(c)/(b) 收斂為參數化工具——工程量中等，建議另立小計畫 |
| P2 | run 綁定腳本（`observe_twevo_run22.py` 等） | run 22 結束後移入 `archive/` 或刪除 |
| P2 | 暫存檔（`tmp_runners/`、`scratchpad/`）未歸 `audits/` | 盤點後移正 |
| P2 | `migrate_*_ddl.py` 83 支體積 | **不建議收斂**——換機還原依賴，體積是刻意维护成本非債務，本檔僅記錄不建議動作 |

**建議本輪立即可做**：`sync_memory.sh` 因牴觸 #14 屬**規則層問題**而非單純體積債，建議優先處理；其餘建議先盤點消費端確認零引用後才刪（避免誤刪）。

---

## §5 建議序列（回應「可先做或同步做」之慣性提問）

### 可立即平行做（風險低、範圍小、機械修正，各自獨立）

1. `evaluation/portfolio.py` raw-string 修正（C 軌 P2）
2. `sync_memory.sh` 停用／刪除確認（D 軌 P0）
3. CS 版號漂移文字更正（A 軌 P2）

以上三項互不相依、皆為 1 檔內小範圍修正，可同批次呈目後一次性做完。

### 需先盤點才能動（不可倉促）

4. D 軌死碼清除（`export_milvus_index.py` 等）——先 grep 消費端
5. `action_log` 接線（C 軌 P1）——先讀三個決策點現有程式碼再插入呼叫

### 需 Steward 裁決（AI 不可代行）

6. `direction_gate` 判準矛盾（A 軌 P0）
7. RULING-043 簽核（A 軌 P0）

### 沿用既有 SSOT、下一手候選 GO 句（B 軌）

8. ~~`S3-WAVE-D-go`~~ **已全數執行**（Phase 1-2c，2026-08-04，見 §2.1）；`S3-WAVE-C-go`（組 10-11，方向表↔ranker 契約，無新表需求）仍待授
9. `predict-asof-write-go`／`SIM-FIRST-CELL-go`
10. 8 族 missing adapter 之首族 plan-first（契約與資料皆已備妥；建議先選 sequence DL 一族如 LSTM 或圖模型 GCN，因序列窗／圖邊皆已落地）

**本檔原建議之單一最高槓桿下一手 `S3-WAVE-D-go` 已於 2026-08-04 完成 Phase 1-2c 全數**（`audits/S3-WAVE-D-EXECUTED-20260804.md`；`stock_graph_edge` 13,021 邊已寫入）。**新單一最高槓桿候選**：選一族 adapter 訓練碼開工（契約與資料已備妥，是真正把「契約」轉成「可訓練模型」的下一步；序列 DL／GNN adapter 需另立 plan-first，因涉及訓練框架選型與計算資源評估）。若目標是「清理治理層乾淨度」→ 仍可並行做 §5 第 1-3 項機械修正＋提醒 Steward 兩項待裁（第 6-7 項）。

---

## §6 驗收方式

- A 軌治理項：以裁決/簽核文件（`constitution/RULING-*`／HANDOFF 更新）為驗收證據。
- B 軌：沿用既有波次模式——GO audit→EXECUTED audit（見歷史 `audits/S{3,4,5}-WAVE-*` 範式）。
- C／D 軌機械修正：`git diff` 對照＋（若涉 script）`python -m` 直跑一次確認無 traceback；ReadLints 確認無新增 lint。

---

*定版（2026-08-04）——依 `augur_deep_understanding_r6_20260804.md` §7 全量債表歸軌排序；不含任何自動執行，等候 Steward 選定下一手。*
