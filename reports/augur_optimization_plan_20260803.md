# Augur 專案優化計畫書（2026-08-03）

> **性質**：#20 計畫先行之計畫報告（規劃類，非執行紀錄）。本檔為「後續優化此專案」之基礎排序與落地規畫。
> **產出者**：AI（合成十區深讀之 `optimization_candidates` 與對抗發現）。**self-reported（#32a）**：本檔一切判讀為 AI 自陳，不得作為「世界如此」之權威確認；凡可機械覆核者已附覆核指令，未附者標【推論】。
> **授權狀態**：本檔僅為呈案。**任何標【Steward】之項目，AI 不得代裁、不得逕自實作**。
> **資料時點**：所有數字為 2026-08-03 09:2x 現查（非抄報告）。與既有報告不符處已逐條標「報告說 X／live 實為 Y」。

---

## §0 優化總圖（一頁）

### 0.1 本專案現在站在哪裡

近 72 小時完成的量能是真的：登錄冊 24 項全清、23 項裁決批、A3 八閘（G-SIGN 入閘）、首兩顆引擎自掙晉升、SIM-CAL-R1 門親簽生效＋四件套落地、B4 三批 UPDATE-GUC、pre-commit 五閘上崗、WM.36 弧 M1/M2/PK 丙案落地。**這些不是待辦，是地基。**

但同一批深讀在地基上找到一個共同形狀，它值得成為本計畫的組織原則：

> **本專案現階段的主要風險，已經不是「還沒做」，而是「做了、看起來綠了、但量的不是它宣稱在量的東西」。**

十區中六區各自獨立撞到同一型（記憶檔 `guard-mechanisms-that-silently-fail` 的第二問法）。本計畫的 P0 幾乎全部是這一型，而非新功能。

### 0.2 五個最貴的洞（全部已機械覆核）

| # | 一句話 | 現況覆核 | 不修會怎樣 |
|---|---|---|---|
| **A** | sim evaluator 讀不到 runner 產的 q_grid | `normalize_q_grid(_q_grid(...))` → **None**（實跑） | 三個月校準時鐘跑完，11 月才發現一列都算不出＝**白等一季** |
| **B** | 三個 worktree 的 commit 完全不過五閘 | 三 worktree 皆無 `venv/`，hook `exit 0` | 並行 session（含本次三個）現在提交的每一筆都零閘，之後併回 main |
| **C** | 116 支 trigger 可被一句 session GUC 全部靜音 | `tgenabled` 全 `O`；兩角色皆 superuser | 全部「硬閘」實為紀律提示，而文件一律稱其為硬閘 |
| **D** | 進化引擎積壓告警恆為 9、A8 驗收結構上不可能 FAIL | 現查 `cleared_at IS NULL` = **0**／total 9 | heavy slot 餓死（本軸最貴失效）永遠分辨不出來 |
| **E** | WM.36 距 10-14 硬期限 72 日，登錄完成數 **0/6** | 6/6 `authoritative_binding_id` NULL、98 通道 `source_column` 全空 | 唯一有外部硬期限的義務，目前進度容易被「表已建」誤讀為已達標 |

### 0.3 本計畫的形狀

```
P0（7 項｜本週）    先讓紅燈會亮 + 保住 sim 時鐘 + 10-14 倒推起跑
P1（12 項｜2 週）   把 Steward 看得見的面補齊 + 治權層自我一致性機械化
P2（11 項｜1 個月） 存量清償、覆蓋率、成本止血
P3（5 項｜待裁）    全部觸治權判準，AI 只呈案不動手
```

**總計 35 項，全部來自十區之 `optimization_candidates` 與對抗發現，零自創需求。**

### 0.4 本計畫的射程限制（誠實揭露）

我收到的素材為**十區中的 Z1–Z6**（治權層／工具規則與記憶／進化引擎／閘體系／知識層／sim 軸）。**Z7–Z10 與三份對抗審查在傳入時被截斷**，其 `optimization_candidates` 不在本計畫內。

⇒ **本計畫不是全專案優化的完整集合**，而是「已收到的六區之完整合成」。補齊 Z7–Z10 後應以增補章方式併入，**不得因本檔存在而推定其餘四區無待辦**（此即 RULING-2026-039「禁止假關」之同型戒律）。

---

## §1 排序原則（本專案已證有效者，逐條說理）

以下四條不是通用專案管理教條，是**本專案過去兩個月用實例證明過的**排序依據。每條附本專案的證據來源。

### 原則一：「不修會怎樣」＞「修了有多好」

**說理**：本專案的主要資產是「誠實的證據鏈」。一個假綠造成的損害是**沉默污染下游**（CLAUDE.md #28 之裁決句：「搞錯會不會沉默污染下游？會→歸理解軸窮盡」），而一個未做的優化只是慢。二者成本不對稱。

**本專案證據**：`promoted_by='hugo'` 代打（07-25）、綠燈帳本 19/19 假綠（07-31 已修）、promote 傳空 args 靜默成功 16,072 筆（07-31 已修）、`augur-knowhow-refresh --domain finance` 空轉（本輪新發現，同族第二次發作）。**每一次的損害都是「相信了一個不成立的綠燈並在其上繼續建造」，而非「少做了一件事」。**

**操作化**：每項優化必須寫出「不修會怎樣」，且該句必須描述**一個具體的錯誤決策**，不能只寫「不夠好」。寫不出來的項目降級。

### 原則二：硬期限倒推 ＞ 主觀急迫

**說理**：本專案唯一的外部硬期限是 **2026-10-14**（距今 **72 日**）。所有其他「急」都是可協商的。

**本專案證據**：`ULTRACODE-SCHEDULE.md` 之併結 checklist 七項**本日親讀仍全 `[ ]`**；另有六項同綁該日（F2 §8）。全 repo `2026-10-14` 於 `constitution/`＋`specs/`＋`docs/compliance/` 共 74 處命中。

**操作化**：綁 10-14 者一律進 P0/P1 並在 §3 倒推排程；未綁者不得因「感覺重要」插隊。**且倒推須留審查緩衝**——不是排到 10-13。

### 原則三：關鍵路徑（會卡住別人的先做）

**說理**：本專案有兩條**時間不可壓縮**的鏈：sim 校準時鐘（三格 × 21 交易日 ≈ 11 月上旬）與 TWEVO 週輪（每週一至五 23:00）。這兩條上的缺陷有一個特性——**修復成本不隨時間變，但發現越晚，已浪費的等待越不可回收**。

**本專案證據**：sim q_grid 契約破裂（P0-1）若今日修，成本是一行；若 11 月 K=3 齊了才發現，成本是**重跑一整季的時鐘**（而 `run_id` 因 `ON CONFLICT DO NOTHING` 且不含 code 版本，已產列還改不了形狀）。

**操作化**：位於不可壓縮鏈上的缺陷，即使「不修會怎樣」的嚴重度中等，也升 P0。

### 原則四：收益成本比 ＋「先讓紅燈會亮」優先於「把紅燈修綠」

**說理**：這是本專案記憶檔 `augur-three-gate-strengths` 的第一原則。一個**會誤報綠**的檢查器比沒有檢查器更糟，因為它消耗了信任預算。

**本專案證據**：`reconcile_audit.py:158` 漏 `coverage_gap`（正確判式住在沒人呼叫的 `reconcile.py:587`，且該處有回歸鎖）；`verify_evolution_acceptance.py` A8 因漏 `cleared_at` 而結構上不可能 FAIL；`check_cmd_matrix` 467/467 全綠但不含 repo 根。

**操作化**：同等成本下，**先做「讓既有檢查器誠實」，再做「新增檢查器」**。本計畫 P0 中有 4 項屬前者，P1 才開始新增。

### 原則五（判準補充）：AI 可為 vs Steward 保留

沿用 `AUGUR-MC v1.6 §8.1`／`AUGUR-L6 v1.2` L6.18(a)：

- **AI 可為**：改正確／補完整／接上既有判準／純機械一致性檢查（CLAUDE.md #26 執行層自我糾錯）。
- **【Steward】**：新增或變更判準、條文解釋、**涉及 AI 自身監督機制之變更**、外部副作用、不可逆。

⚠ **本計畫中所有「加嚴閘」的項目都要過這一關**——加嚴不因方向為善而免除授權（型 7「凍結了判準文字沒凍結判準的實作」之戒律）。

---

## §2 優先級逐項

### ── P0：本週（7 項）──

---

#### P0-1　sim evaluator q_grid 契約修復【執行者＝AI】

**問題**
runner 寫入 `summ["terminal_q_grid"] = {"unit": "...", "p": <list[99]>}`（`scripts/run_sim_calibration_cell.py:260-261`，`_q_grid()` 回 `list`）；evaluator `normalize_q_grid`（`scripts/evaluate_sim_calibration.py:124-130`）只認 `p` 為 **dict**，對 list 走 `g[f"p{i}"]` → KeyError → 回 `None`。

**機械覆核**（本日實跑，非抄報告）：
```bash
cd /home/hugo/project/augur && venv/bin/python -c "
import sys;sys.path.insert(0,'scripts');sys.path.insert(0,'src')
import _bootstrap, numpy as np
from evaluate_sim_calibration import normalize_q_grid
from run_sim_calibration_cell import _q_grid
print(normalize_q_grid({'terminal_q_grid':{'unit':'x','p':_q_grid(np.linspace(-.5,.5,20000))}}))"
# 現輸出：None
```

**最毒的部分**：`evaluate_sim_calibration.py:742-744` 的自測項字面寫著「q_grid 巢狀形（**runner 實形** unit+p 子鍵）可解」，`:126` 註解寫「runner 實形=…（2026-08-02 契約**親驗**）」——**兩處都宣稱已對齊真實 runner，但 fixture 是手寫的、錯的**，於是自測永遠綠。此為 CLAUDE.md #35(1)（純函式餵真輸入）要防的型態，且該規則 08-01 入憲、本檔 08-02 新寫，**屬向前生效射程內**。

**為何現在**
今晚 20:00 cron（`run_arena_daily_pipeline.py --run`）把 08-03 收盤入庫後，anchor 實現；**首格 52 列須人工按 `--apply` 才落地，非自動**（M-T7 三處親驗：crontab／unit-files／`_steps()` 皆無 sim）。**現查 `max(date) FROM "TaiwanStockPriceAdj" WHERE stock_id='TAIEX'` = 2026-07-31、`sim_run_link` = 0 列** ⇒ 時鐘尚未起跑，現在修是零遷移成本。

一旦首格落地就修不動了：runner 用 `INSERT … ON CONFLICT (run_id) DO NOTHING`，`run_id` 由 `(gate,candidate,stock,asof,h,spec_sha)` 決定、**不含 code 版本**；重跑是 DO NOTHING、UPDATE 被 `honesty_ledger_guard` 擋、換 run_id 等於換候選。⇒ **正解必須是改 evaluator（數字本身是對的，只是形狀），不是改 runner。**

**Schema（不產表）**
所讀既有表：
```
sim_run_link        （現 0 列）── runner 寫入，含 iteration_uid
mc_simulation_run   （現 540 列，全 asof=2026-05-31）── summary jsonb 內含 terminal_q_grid
sim_realized_outcome（現 0 列）── settle 寫入
sim_calibration_eval（20 欄；eval_id, gate_id, candidate_id, arm, eval_set_id, eval_code_hash,
                      n_runs, n_valid, n_excluded, is_invalid, cov_p50/p80/p90,
                      pinball_mean, crps_mean, pit_ks_stat, pit_ks_p, detail jsonb,
                      created_at, git_sha）
```
**結果落哪張表**：不變——修復後 `sim_calibration_eval` 才會從「0 列可評」變成有列。本項零 DDL。

**程式規畫**

| 檔 | 函式 | 角色 | 改動 |
|---|---|---|---|
| `scripts/evaluate_sim_calibration.py` | `normalize_q_grid`（:121-136） | 消費 | 取 `g["p"]` 後若為 `list`／`tuple` 直接採用（一行：`if isinstance(g, dict) and "p" in g: g = g["p"]`；其後 list 分支已存在則沿用，否則補 `if isinstance(g, (list, tuple)) and len(g)==99: return list(g)`） |
| 同上 | `_selftest`（:742-744） | 回歸鎖 | fixture **改為直接 import `run_sim_calibration_cell._q_grid` 的真輸出**（#35(1)），移除手寫 dict |
| 同上 | `_evaluate`（:473 附近） | 誠實訊息 | `n_no_qgrid > 0` 時訊息與「等 settle 波」分離（見下） |

**附帶必修（同一改動窗）**：解析失敗時 evaluator 走 `n_no_qgrid += 1; continue` → `n_valid==0` → 印「零格可評: 有 run 但無已結算有效觀測（**等 settle 波**）」。**真因是解析失敗，訊息卻指向 settle 未跑**，人會以為時鐘正常而繼續等。須改為當 `n_no_qgrid > 0` 時印明「N 列 q_grid 無法解析（契約不符）」。

**分階段**
1. **S1（今日，首格落地前）**：改 `normalize_q_grid` ＋ 自測 fixture 改真輸入。
2. **S2**：依 #35 唯一有效驗法——**退回舊版確認自測變紅**（不是「新版綠了」就算數）。
3. **S3**：改誠實訊息，跑 `--selftest` 全綠。
4. **S4（今晚首格落地後）**：以真實 1 列 `mc_simulation_run` 跑 `evaluate_sim_calibration.py --dry-run`，確認不再計入 `n_no_qgrid`。

**驗收判準（機械可判）**
- `venv/bin/python -c "...normalize_q_grid(...真輸出...)"` 回**非 None 且長度 99**。
- `git stash` 舊版 → 跑 `--selftest` → **rc≠0**；還原 → rc=0。（退回驗紅）
- 首格落地後 `evaluate_sim_calibration.py --dry-run` 輸出中 `n_no_qgrid == 0`。

**風險**
低。改的是消費端解析，不動任何已落地資料、不動門、不動 thresholds。唯一風險是「list 順序是否即 p1..p99」——須在 S1 一併確認 `_q_grid()` 之輸出順序（現查回 list 長度 99，順序須讀該函式確認）。

**是否觸治權判準**：**否**。屬 #26 執行層「改正確」；不改門文、不改 thresholds、不改 `criteria_sha`。

---

#### P0-2　worktree 治權檔與 pre-commit 雙重失效【執行者＝AI（hook）／【Steward】（#13 文字）】

**問題（兩個失效疊在同一個原因上）**

(a) **五閘靜默略過**：`ops/githooks/pre-commit:14-16`
```
ROOT="$(git rev-parse --show-toplevel)"
PY="$ROOT/venv/bin/python"
[ -x "$PY" ] || { echo "pre-commit: 無 $PY，略過（請先 pip install -e .）"; exit 0; }
```
worktree 內 `--show-toplevel` 回 worktree 根；**現查三個 worktree 皆無 `venv/`**（`can-use-ca1439`／`project-analysis-report-fc3448`／`zai-ma-9f972d`）。而 hooks 由 common dir 解析（`git rev-parse --git-path hooks` → 主 repo `.git/hooks`）⇒ **hook 確實被觸發，但走 `exit 0`**。

(b) **注入過期治權檔**：harness 注入的 project instructions 來自 worktree 的 base commit。本 session 讀到的是 **CLAUDE.md v1.32**，主 repo 為 **v1.35**（`git worktree list` 現查：本 worktree 停在 `0d2b2b9`／2026-07-31，main 在 `45ea88d`）。缺 #33（禁阻塞等待迴圈）、#34（平行度拉滿）、#35（回歸鎖三規則）；且 worktree 版仍以**生效文字**載已被 #34 反向廢止的「非必要不 fan-out」。

**為何現在**
不是假設——**本次深讀本身就跑在受影響的 worktree 裡**，且現有三個並行 session。這是「監督機制自己靜默失效」的當期實例，不是歷史教訓。

**Schema**：不產表、不讀表（純檔案層）。

**程式規畫**

| 檔 | 函式／段 | 角色 | 改動 |
|---|---|---|---|
| `ops/githooks/pre-commit` | 開場 :14-16 | 強制 | `ROOT` 改由 `git rev-parse --git-common-dir` 推主 repo 根；venv 仍缺則 **`exit 1`＋印補救指令**（fail-closed），不再 exit 0 |
| `scripts/check_worktree_treaty_sync.py`（**新增**） | `main()` / `--check` / `--selftest` | 稽核 | 比對每個 `git worktree list` 之治權檔 blob 是否等於 main；不一致即 rc≠0 |
| `.git/hooks/pre-commit` | :13 註記 | 誠實 | 現寫「須由 **install_services.sh** 或本檔複製安裝」，但 `grep -n hook install_services.sh` **零命中**；真安裝者是 `resume_project.sh` → `scripts/install_git_hooks.py`。逐字改正 |

新增 script 依 #18／#29(d) **首次提交即須含執行指令矩陣**＋`--selftest`（零 DB 零 API）。

治權檔清單（`check_worktree_treaty_sync.py` 之射程）：
`CLAUDE.md`、`docs/系統核心思想_*.md`、`docs/原則精華_*.md`、`docs/系統架構大憲章_*.md`、`constitution/**`、`specs/**`。

**分階段**
1. **S1**：hook 之 `ROOT` 改 `--git-common-dir`；於 worktree 內實跑確認五閘**真的執行**（現況印「略過」）。
2. **S2**：venv 缺失改 `exit 1`；同步在 `resume_project.sh` 3b 步前加提示。
3. **S3**：新增 `check_worktree_treaty_sync.py`＋矩陣＋selftest。
4. **S4**【Steward】：#13 增列「凡於 worktree 執行者，動工前先以 `head -1 <repo根>/CLAUDE.md` 核對版本，不一致即以主 repo 為準」——**此步為治權檔文字增修，AI 僅草擬**。

**驗收判準（機械可判）**
- `cd <任一 worktree> && bash ops/githooks/pre-commit` → **不再印「略過」，且五閘逐支有輸出**。
- 移除主 repo venv 之可執行位（模擬）→ hook **rc=1**（fail-closed 驗紅）；還原 → rc=0。
- `venv/bin/python scripts/check_worktree_treaty_sync.py --check` → 現況應 **rc≠0**（三 worktree 皆落後），修正同步後 rc=0。

**風險**
中。改 `exit 0` → `exit 1` 後，**venv 未裝的環境會暫時無法 commit**——這正是想要的行為，但須確認 `resume_project.sh` 的順序（3b 裝 hook 在 `pip install -e .` 之後），否則新機首次 commit 會卡。S2 前須實測換機流程。

**是否觸治權判準**：**分裂**。S1–S3（hook 與稽核器）屬執行層，AI 可為；**S4（#13 文字）觸，屬 Steward**。另：「worktree 是否為 #13 允許之工作場所」本身是條文解釋——三項實測（過期治權檔、失去 recall、五閘略過）皆為**監督強度之實質減損**，依 #26 OCV 單向棘輪屬「任一分量弱化即須 Steward 書面裁決」，見 §7 S-3。

---

#### P0-3　`reconcile_audit.py` coverage_gap 假綠【執行者＝AI】

**問題**
`scripts/reconcile_audit.py:158`：
```python
passed = vm == 0 and ex == 0 and not inc
```
**未納入 `coverage_gap`**。而正確判式在 library：`src/augur/audit/reconcile.py:587`
```python
"passed": tvm == 0 and tex == 0 and not incomplete and not coverage_gap}
```
且該處 `:615-618` **已有回歸鎖自測**（含 2026-07-14 假綠 blocker）。⇒ **修好的判式住在沒人呼叫的函式裡**——現查 `grep -n "verdict" scripts/reconcile_audit.py` 只命中註解與變數名，CLI 全檔不呼叫 `reconcile.verdict()`。

**誠實修正（本輪新發現，與素材不同）**
素材將此列為「三層假綠鏈已成立」。**實查 `attestation_result` 全 10 列：`coverage_gap_n > 0` 僅 id=3 一列，且該列 `passed=False`（因 `extra_in_db=6826` 另有原因）。`passed=true AND coverage_gap_n>0` 之列數＝0。**

⇒ **此為 latent bug（潛伏），尚未實際產生過一次假綠。** 仍列 P0，理由是原則四（先讓紅燈會亮）＋修復成本近零＋它位於 `daily_maintenance` → `attestation_result` → watchdog 三層信任鏈的最上游。但**不得宣稱「已經騙過我們」**。

**Schema（不產表）**
所讀既有表 `attestation_result`（14 欄）：
```
id bigint NN; run_at timestamptz NN; driver varchar NN; passed boolean NN;
matched bigint; value_mismatch int; extra_in_db int; missing_in_db bigint;
exempt_n int; sampled_n int; coverage_gap_n int; incomplete_n int;
audit_since varchar; note text
```
**關鍵**：`coverage_gap_n` 欄**已存在且已在收集資料**——資料早就在，只是判式沒讀它。結果仍落 `attestation_result`，零 DDL。

**程式規畫**

| 檔 | 函式 | 角色 | 改動 |
|---|---|---|---|
| `scripts/reconcile_audit.py` | `_summary()`（:137-162） | 消費 | 改呼叫 `augur.audit.reconcile.verdict()`（#12 單一住所）；退而求其次：`passed = vm==0 and ex==0 and not inc and not agg.get("coverage_gap")` |
| `src/augur/audit/reconcile.py` | `verdict()`（:583-588） | 判準 SSOT | **不動**（已正確且已有回歸鎖） |

**分階段**
1. **S1**：先跑一次**唯讀**全表對帳，列出「改判式後會由 PASS 轉 FAIL 的表清單」（不改碼，先算影響面）。
2. **S2**：改 `_summary()` 接上 `verdict()`。
3. **S3**：退回舊版確認變紅（#35）——以 S1 清單中任一表為 fixture。
4. **S4**：依 S1 清單決定每張轉紅表是「補資料」還是「誠實掛紅」。**死表＝本機漏 sync 可補**（記憶 `audit-attestation-falsegreen` 已記此射程）。

**驗收判準（機械可判）**
- `grep -n "coverage_gap" scripts/reconcile_audit.py` → 判式行命中。
- 合成一組 `matched=0, vm=0, ex=0, coverage_gap=True` 之輸入 → `_summary()` 回 `passed=False`（現況回 True）。
- 退回舊碼跑同 fixture → 回 True（驗紅成立）。

**風險**
中。S2 之後 `daily_maintenance` 可能開始寫 `passed=false`，進而觸發 watchdog 發車。**必須先做 S1 算影響面**，不可直接改了就上（否則今晚 cron 可能連鎖）。

**是否觸治權判準**：**否**。是把既有判準（library 側已定稿並有鎖）真正接上，不是改判準。

---

#### P0-4　進化引擎 `cleared_at` 謂詞（driver ＋ A8 驗收器）【執行者＝AI】

**問題**
`scripts/run_evolution_iteration.py:433`：`SELECT count(*) FROM evolution_deferred_work` **未加 `WHERE cleared_at IS NULL`**。
`scripts/verify_evolution_acceptance.py:238-241`：同樣漏，且判式為「0 → N/A，否則 PASS」。

**機械覆核**（本日現查）：
```sql
SELECT count(*) FILTER (WHERE cleared_at IS NULL) uncleared, count(*) total FROM evolution_deferred_work;
-- 現值：uncleared = 0 ／ total = 9
```
⇒ driver 現在印「積壓(搶不到重活鎖):9 列」，而**真實積壓為 0**。且 A8「重活互斥」驗收因 `n_def=9 ≠ 0` 恆走 PASS 分支——**結構上不可能 FAIL**。

**為何現在**
今日為週一，**今晚 23:00 即 run 22**（亦即 I5B supersede 機制之首次生效點）。這是本軸最貴失效模式（heavy slot 餓死，07-27~29 曾連三日 rc=75）的告警通道，而該通道現在是**恆亮＝等於沒有**。

**Schema（不產表）**
所讀既有表 `evolution_deferred_work`（8 欄）：
```
defer_id bigint NN; axis text NN; step_key text NN; requested_at timestamptz NN;
reason text NN; cleared_at timestamptz; cleared_by text; detail jsonb NN
```
**結果落哪張表**：driver 側落 stdout 與 `evolution_iteration_ledger.steps_json`；驗收側落 `verify_evolution_acceptance` 之 stdout／rc。零 DDL。

**程式規畫**

| 檔 | 位置 | 角色 | 改動 |
|---|---|---|---|
| `scripts/run_evolution_iteration.py` | :433 | 消費 | 加 `WHERE cleared_at IS NULL`（抄 `scripts/drain_deferred_work.py:113` 之既有正確寫法，#12 同一住所） |
| `scripts/verify_evolution_acceptance.py` | :238-241 | 驗收 | 同上；**且判式改為對照「rc=75 事件數 vs deferred 未清列數」**，不一致才 FAIL——否則仍是橡皮圖章 |

**分階段**
1. **S1**：兩處加謂詞。
2. **S2**：回歸鎖——fixture 塞一列 `cleared_at` 非空，斷言計數不含它；退回舊碼須變紅。
3. **S3**：A8 判式升級（rc=75 事件數對照）——此步較大，可與 S1/S2 分離。

**驗收判準（機械可判）**
- 改後 driver 印「積壓 … **0** 列」（現印 9）。
- fixture：`INSERT` 一列 cleared 之 deferred → 計數不變；退回舊碼 → 計數 +1（驗紅）。
- A8：構造「有 rc=75 事件但 deferred 無列」之 fixture → **FAIL**（現況必 PASS）。

**風險**
低（S1/S2）。S3 需定義「rc=75 事件數」之取得口徑（從 `steps_json` 掃），屬新增邏輯，可延至 P1。

**是否觸治權判準**：**否**（#26 執行層自我糾錯）。

---

#### P0-5　WM.36 登錄完成度：10-14 倒推起跑【執行者＝兩者（AI 備料／hugo 決定採認）】

**問題**
World Concept Registry **已落地**（08-02 21:23）——這推翻了 F2 08-01 備料所記之「Registry 表本體＝**NONE**」。現查五物件皆在：`world_concept`(6)／`world_concept_version`(6)／`world_concept_registry_current`(view)／`world_concept_registry_legacy`(6)／`world_channel_binding`(98)。

**但「表已建」≠「WM.36 已履行」**。WM.36 可判定判準為「登錄項七欄俱全且各欄可解析」（`specs/WORLD-MODEL-SPECIFICATION.md:344-`）。現查：
```sql
SELECT count(*) n, count(*) FILTER (WHERE authoritative_binding_id IS NULL) no_auth,
       count(*) FILTER (WHERE decided_by IS NULL) no_dec FROM world_concept_registry_current;
-- 現值：(6, 6, 6)   ⇒ 欄4 權威表徵指定 6/6 空、decided_by 6/6 空
SELECT mapping_status, count(*), count(source_column) FROM world_channel_binding GROUP BY 1;
-- 現值：unmapped 88 / 0 ｜ mapped 10 / 0   ⇒ source_column 非空者 0/98
```
⇒ **今日「登錄完成」數＝0/6**（self-reported 判讀，覆核指令如上）。且通道映射 WM.36 欄3 要求「粒度至**欄位級**」，現況 provenance 自陳 `table_level(§9 Q5 表級暫登;欄位級=column_catalog 待後批)`。

**vendor 直綁：四把尺同時流通**（引用必連口徑）
| 尺 | 值 | 出處 |
|---|---|---|
| GROUNDING-MAP 07-17 快照 | 37 檔 | `GROUNDING-MAP.md:46` |
| F2 報告 08-01 | 47 檔 | F2 §1 |
| 同一 grep 本日 | 50 檔 | `grep -rlE 'FROM\s+"Taiwan' src scripts --include='*.py'` |
| **止血閘本日實跑** | **56 檔／172 處** | `scripts/check_vendor_binding.py --scan`（rc=1） |

⚠ **素材記 170 處，本日實為 172 處**——今日 commit `45ea88d`（「止血閘補數字表名漏洞」）擴了口徑，`quoted_table` 140→142。**同日之內已再漂一次**，正說明手抄數字不可用。止血閘口徑有 `caliber_sha256=0e0e608f75122bf5` 可自證。

**為何現在**
距 10-14 **72 日**。checklist 七項本日親讀仍全 `[ ]`：
```
- [ ] WM.35／36 直綁消費禁令生效盤點
- [ ] 025 (iii)(iv)(vi) ②③ 觸發／達成或明示續延
- [ ] 029 L5 PRV／ASF 日曆復審
- [ ] L7.16 全棧 owner≠app 矩陣進度
- [ ] KDO.4／LDO.4 量測落地狀態
- [ ] 020 M2 仍 deferred 或另案承接
- [ ] GOV-3 B 有無新越權 Evidence
```
欄位級映射（98 列 × 欄位展開）不是一天的工作量；72 日看似寬裕，但須扣除審查緩衝與 hugo 的決定時間（§4）。

**Schema（產表——新增探針綁定表）**

本項的核心優化不是「趕工填欄」，而是**把 10-14 的進度量測從手抄變機械**。現況散在三處（F2 報告／GROUNDING-MAP／ULTRACODE-SCHEDULE）各自手抄，本輪已抓到三處過期。

```sql
-- 新表：條文 ↔ live 探針綁定（唯讀量測，不代 Steward 勾任何一項）
CREATE TABLE IF NOT EXISTS treaty_probe_binding (
    probe_id         text PRIMARY KEY,              -- 如 'WM36-AUTH-BINDING'
    obligation_ref   text NOT NULL,                 -- 'specs/WORLD-MODEL-SPECIFICATION.md:344'
    deadline         date,                          -- 2026-10-14（無期限者 NULL）
    probe_kind       text NOT NULL
        CHECK (probe_kind IN ('sql','cmd')),
    probe_sql        text,                          -- 唯讀 SQL（probe_kind='sql'）
    probe_cmd        text,                          -- 可重跑指令（probe_kind='cmd'）
    expect_expr      text NOT NULL,                 -- 機械判定式，如 'value = 0'
    caliber_note     text NOT NULL,                 -- 口徑聲明（哪把尺）
    created_at       timestamptz NOT NULL DEFAULT now(),
    CHECK ((probe_kind='sql' AND probe_sql IS NOT NULL)
        OR (probe_kind='cmd' AND probe_cmd IS NOT NULL))
);

-- 新表：探針量測歷程（append-only）
CREATE TABLE IF NOT EXISTS treaty_probe_reading (
    reading_id   bigserial PRIMARY KEY,
    probe_id     text NOT NULL REFERENCES treaty_probe_binding(probe_id),
    read_at      timestamptz NOT NULL DEFAULT now(),
    value_text   text NOT NULL,                     -- 量測值（原樣，不解釋）
    verdict      text NOT NULL
        CHECK (verdict IN ('meets','not_meets','undecidable')),
    git_sha      text NOT NULL,
    detail       jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_tpr_probe_time ON treaty_probe_reading(probe_id, read_at DESC);
```

**設計約束（引 L7.26(a)）**：探針**不得由被量測構件自身支配**——`probe_sql` 一律直查 live DB，不呼叫被量測模組的函式。

**閘**：`treaty_probe_reading` 為帳本 ⇒ 依 §7 S-6 之射程裁決決定是否掛 `honesty_delete_only_guard`（**不預設**，見 §7）。

**程式規畫**

| 檔 | 職責 | 簽名 | 輸入表 | 輸出表 |
|---|---|---|---|---|
| `scripts/migrate_treaty_probe_ddl.py`（新） | 建表／冪等遷移 | `main(argv)`；`--check`／`--apply` | — | 上二表 |
| `scripts/read_treaty_probes.py`（新） | 逐探針量測、寫 reading | `main(argv)`；`--check`（唯讀不寫）／`--apply`／`--probe-id X`／`--selftest` | `treaty_probe_binding` ＋各被量測表 | `treaty_probe_reading` |
| `scripts/report_1014_progress.py`（新，可併入既有週報） | 產 10-14 進度表（本次值／上次值／diff） | `main(argv)`；`--check` | 上二表 | stdout |

三支皆須含**執行指令矩陣**＋`--selftest`（#18／#29(d)，新增即須具矩陣）。

**首批探針（7 條，對應 checklist 七項）**
| probe_id | 量什麼 | expect |
|---|---|---|
| `WM36-AUTH-BINDING` | `count(*) FILTER (WHERE authoritative_binding_id IS NULL)` on registry_current | `= 0`（現 6） |
| `WM36-COL-GRAIN` | `count(source_column)` on `world_channel_binding` | `= count(*)`（現 0/98） |
| `WM36-DECIDED-BY` | `count(*) FILTER (WHERE decided_by IS NULL)` | `= 0`（現 6） |
| `WM35-VENDOR-DIRECT` | `check_vendor_binding.py --scan` 之檔數／處數 | 附 `caliber_sha256`；趨勢須單調下降 |
| `L716-COMPENSATING` | trigger 家族現況（`honesty_ledger_guard` 表數／`delete_only` 表數） | 記錄值，不設 expect（042 §二2 為 08-01 快照，見下） |
| `KDO4-MEASURE` | KDO.4 量測落地狀態 | 待 KDO.4 agent 報告後定 |
| `GOV3B-EVIDENCE` | 是否有新登錄之越權 Evidence | 人裁欄，探針只列候選 |

**⚠ 042 之數字必須加限定詞**：`RULING-2026-042` §二2 記「30 種 guard 函式；`honesty_delete_only_guard` 23 表＋`honesty_ledger_guard` 5 表」。**本日現查為 34 種／delete_only 9 表／ledger_guard 25 表——方向完全反轉**（B4-P2a/P2b 所致）。依大憲章 v1.51.0 通則一「史述凍結」，**042 正文不得改**；正解是另立滾動快照並在 10-14 議程明列「042 §二2 為 08-01 快照，現況見探針」。

**分階段**
1. **S1（本週）**：建表＋首批 7 探針＋`--check` 唯讀跑通，產出**今日基線值**。
2. **S2（8 月中）**：接入週報（週日 09:00 既有班次），每週一行 diff。
3. **S3（8 月下～9 月）**：欄位級映射補齊（98 列 × 欄位展開）——**此步是真工作量**，見 §4 車道。
4. **S4（9 月下）**：`authoritative_binding_id` 指定＋`decided_by` 落人簽——**decided_by 一律 hugo 親跑寫入**（記憶 `never-type-human-signature`；AI 絕不代打）。
5. **S5（10 月上，緩衝）**：併審備料定稿，**不代勾任何 checklist 項**。

**驗收判準（機械可判）**
- `read_treaty_probes.py --check` rc=0 且 7 條探針皆有 reading。
- 週報含「10-14 進度：N/7 探針 meets」一行。
- S3 完成之判準：`SELECT count(source_column) FROM world_channel_binding` **= 98**（現 0）。
- S4 完成之判準：`SELECT count(*) FILTER (WHERE authoritative_binding_id IS NULL OR decided_by IS NULL) FROM world_concept_registry_current` **= 0**（現 6）。

**風險**
中高。S3/S4 是本計畫**唯一有外部硬期限且工作量大**的項目；若 8 月底前 S3 未起跑，10-14 前完成的機率顯著下降【推論】。S4 依賴 hugo 親簽，須排進 §4 之人力車道。

**是否觸治權判準**：
- 建探針表與量測＝**否**（純備料，F2 已立「不代 Steward 勾」之紀律）。
- **「哪些 concept 該登錄、authoritative_binding 指向誰」＝觸，屬 Steward**（採認決定）。
- **`decided_by` 落值＝hugo 親跑，AI 不得代打。**

---

#### P0-6　週報對人閘路 APPLY 失明【執行者＝AI】

**問題**
`scripts/report_triple_evolution_week.py:347` 之 digest 查詢：
```sql
WHERE a.evidence_json->>'gate_ref' = 'V2-AUTOADVANCE'
```
**機械覆核**（本日現查，近 7 日）：
```
V2-AUTOADVANCE   20
TWEVO-APPLY-go    2      ← 08-02 兩顆引擎自掙晉升
HUMAN-PROMOTION   1      ← 07-29 人工晉升
```
⇒ 實跑週儀表確認 digest **只列出 20 筆**；**08-02 兩顆自掙晉升與 07-29 人工晉升完全不出現**。

**為何現在**
本專案 08-02 的核心里程碑（首兩顆引擎自掙晉升，hugo `--queue-id` 逐顆親簽）**在 Steward 的週掃視清單上是不存在的**。掃視認領機制（P5.W5）對最重大、最新的決策路徑失明 ⇒ 等於義務只履行在舊路徑上。下次週報是**本週日 09:00**。

**Schema（不產表）**
所讀既有表 `evolution_apply_log`（含 `queue_id`、`applied_at`、`evidence_json jsonb`）。結果落 stdout／週報。零 DDL。

**程式規畫**

| 檔 | 位置 | 改動 |
|---|---|---|
| `scripts/report_triple_evolution_week.py` | :347 | 去掉 `gate_ref` 過濾；改為全撈並**以 gate_ref 分欄標示**（`V2-AUTOADVANCE`／`TWEVO-APPLY-go`／`HUMAN-PROMOTION`／其他） |
| 同上 | digest 標題 | 同步改字（現標題暗示只含自動路） |

**分階段**：單步（一句 WHERE 改分組）。

**驗收判準（機械可判）**
- 週報 digest 之 7 日筆數 = `SELECT count(*) FROM evolution_apply_log WHERE applied_at >= now()-interval '7 days'`（現 23，digest 現顯 20）。
- digest 中出現 `TWEVO-APPLY-go` 與 `HUMAN-PROMOTION` 分組。

**風險**：極低（唯讀報表，A12 已鎖零寫入）。

**是否觸治權判準**：**否**。

---

#### P0-7　`augur-knowhow-refresh` 週更空轉【執行者＝AI（改碼）／hugo（改 unit 授權）】

**問題**
`~/.config/systemd/user/augur-knowhow-refresh.service` 之 ExecStart 帶 `--domain finance`，但 **`domain='finance'` 在 `knowledge_query`／`knowledge_item`／`knowledge_source`／`knowledge_staging` 四表皆 0 列**。

2026-08-02 04:30 該 unit 之 journal 逐字：
```
▶ S2 promote | 待辦(前):staging pending 0
  S7 kip … 無 item_ids
  KH4 refresh(domain=finance) → 0 item
```
最後 systemd 標 **Finished（成功）**。同時刻全域真實 `knowledge_staging` pending = **102,039**（最舊 `fetched_at` = 2026-07-02，已滿一個月且每日仍在增）。

**這是同族假綠的第二次發作**——07-31 已修的「promote 傳空 args 走印用法分支、16,072 筆假綠」是第一次。分子與分母同時歸零，unit 每週準時綠燈，journal 自洽得無懈可擊。

**為何現在**
每週日 02:00 跑一次，每跑一次就多累積一週的積壓。且 S3 fulltext 亦被同一 domain 濾成 0 ⇒ 90,426 件 `pending_oa_queue` 永遠不抓。

**Schema（不產表）**
所讀既有表：`knowledge_staging`（395,471 列＝promoted 291,252／pending 102,039／rejected 2,180）、`knowledge_item`、`knowledge_query`、`knowledge_source`。結果仍落 `knowledge_item`／`knowledge_item_text`（promote 之既有落點）。零 DDL。

**程式規畫**

| 檔 | 函式 | 角色 | 改動 |
|---|---|---|---|
| `scripts/refresh_knowledge_pipeline.py` | domain 解析段 | **強制** | `--domain` 於 `knowledge_item ∪ knowledge_query` 皆 0 列時 **exit≠0（fail-loud）**，不得 0 待辦靜默成功 |
| `~/.config/systemd/user/augur-knowhow-refresh.service` | ExecStart | 組態 | 換真 domain 或拿掉 `--domain` 走全域；依 #24/#25 加 `--stage-limit` 節流 |

**分階段**
1. **S1（AI 可為）**：加 fail-loud——**先做這個**。即使 unit 未改，下週日就會紅，而不是綠。
2. **S2（須 hugo 授權）**：改 unit 檔（drop-in）＋`systemctl --user daemon-reload`。**改 systemd 屬環境副作用，AI 不自行動**（#6／#26 護欄）。**不得跑 `install_services.sh`**（CR2 已否決）。
3. **S3**：promote 放量（純本地 DB 操作、不觸外部 API，安全）；分批觀察 102,039 之收斂。

**驗收判準（機械可判）**
- S1：`refresh_knowledge_pipeline.py --domain finance` → **rc≠0**（現 rc=0 且印 0 待辦）。
- S2 後：`journalctl --user -u augur-knowhow-refresh.service --since <次週>` 之「待辦(前)」**≠ 0**。
- S3：`SELECT count(*) FROM knowledge_staging WHERE status='pending'` 逐週下降。

**風險**
低—中。S1 會讓下週日 unit 變紅（**這是想要的**）。S3 之 promote 為本地操作，但 102,039 筆一次跑完可能佔用 DB；須分批（#25 最小單位精神）。

**是否觸治權判準**：**否**（執行層修正）。**但 S2 改 systemd 須用戶明示授權。**

---

### ── P1：兩週（12 項）──

以下逐項採精簡格式（問題／為何現在／schema／程式／驗收／治權），完整欄位同 P0 規格。

---

**P1-1　`retrieval.py` 死碼 ＋ advisor 每檢索 1.3s 浪費【AI】**
- **問題**：`src/augur/philosophy/retrieval.py:408` 之 `set_kh_evidence_validity(cur)` 中 `cur` 是**未定義的全域名**（`co_varnames` 無 `cur`）→ NameError 被同段 `except Exception: pass` 吞掉。runtime 實證呼叫成功次數＝**0**。而 `:373`（`_finalize_items_kh_first`）中 `cur` 是形參、真的會執行，但 `set_kh_evidence_validity`（`auto_admit.py:133-140`）清空快取後**不寫 `_at` 鍵**，而 `kh_evidence_valid`（`:163-166`）以 `_at is not None` 為快取有效條件 ⇒ 每次檢索 ≈ **1.3s**（0.89s 全表掃＋0.44s 重掃），`_OK_TTL_SEC=900` 的記憶化被自己打掉。
- **為何現在**：advisor 為常駐服務、每答都付這個成本；且這是 07-30 第四次核驗要修掉的病之**殘留第二現場**。
- **Schema**：不產表；讀 `knowhow_evidence_weight`。零 DDL。
- **程式**：刪 `retrieval.py:371-375` 與 `:405-409` 兩段 try/except（`kh_evidence_valid()` 已零配合自足＋fail-closed）。**改後須 `systemctl restart augur-advisor augur-chat`**（CLAUDE.md #7，http.server 不熱更新）。
- **驗收**：連續兩次 `kh_evidence_valid()` 第二次 **<0.05s**；`ok=False` 時 `rank_item_citations` 回傳序與輸入**逐項相同**。
- **治權**：否。

---

**P1-2　`prior_depth` 假 pass 誠實改【AI】**
- **問題**：`auto_admit.py:599-604` 之 `d < before` 捷徑把未重評的層記成 `{"verdict":"pass","note":"prior_depth"}`。現查：142,441 件 depth≥5 之 item 今日 `kh_axis_state='pending'`（D3 新判準下 KH5 應 fail），但 `layer_scores` 寫著 pass。**這是自我背書的 pass**，與 KH10 被排除的理由同型。
- **為何現在**：D3 這次收緊對存量 14 萬件零效果，而帳面說 pass；**下一位讀 layer_scores 的人會相信 KH5 過了**。改成誠實標記是零行為變更，可立即做。
- **Schema**：不產表；改寫 `knowhow_auto_admit_state.layer_scores` jsonb 內容語意。落點不變。
- **程式**：`verdict` 改為 `"not_reevaluated"`；迴圈判斷改看 `in ("pass","not_reevaluated")` 以**保行為不變**。現查下游 grep `"verdict":"pass"` 僅本模組自用。
- **驗收**：一次全量 upsert 後，`SELECT count(*) FROM knowhow_auto_admit_state WHERE layer_scores::text LIKE '%prior_depth%' AND layer_scores::text LIKE '%"pass"%'` → **0**；且 depth 分布不變（行為不變之證）。
- **治權**：否（#26 改正確）。**建議優先於 P3-2 做**——它讓 P3-2 的收益可被看見。

---

**P1-3　CS 版本自我一致性 lint【AI】**
- **問題**：三檔 CS front-matter 漂移——`CS-系統架構大憲章_v1.54.0.md`（檔名 v1.54.0／標題 v1.53.0／`spec-version: v1.53.0`／增量敘述 v1.49.0／date+author 沿用 v1.48.0）、`CS-系統核心思想_v1.10.0.md`（檔名 v1.10.0／標題與 spec-version 皆 v1.9.0）、`CS-CLAUDE.md`（`spec-version: v1.35` 但 `date: 2026-07-23`）。
- **為何現在**：`spec-version` 是 WM.39–45 之機器可解析欄；欄值指向舊版 ⇒ **該版正文之合規聲明在形式上不存在**。RULING-2026-002 主文二補正期到 **10-14**，屆時若以 front-matter 為證，三檔皆不成立。
- **Schema**：不產表（純檔案）。
- **程式**：`scripts/check_treaty_refs.py` 增第五類 finding `cs_selfversion_mismatch`——檢「檔名 stem 版號 ＝ H1 標題版號 ＝ `spec-version` ＝ `archive-path`」四值一致。約 30–50 行純字串比對，零 DB 零 API。該支已在 pre-commit 第一閘 ⇒ **零新觸發成本**。
- **驗收**：**先驗紅**——現況三檔應各報一 finding；修正後 rc=0；退回文字再變紅。
- **治權**：否（純機械一致性，不解釋條文）。

---

**P1-4　大憲章修訂表「雙現行」lint【AI】**
- **問題**：`docs/系統架構大憲章_v1.54.0.md` 修訂表 56 列中，狀態欄 SUPERSEDED 54／`**ACTIVE**` 1（:446 v1.49.0）／`**現行**` 1（:451 v1.54.0）——**兩列同時宣稱現行**。根因是降級步驟按字串 `**現行**` 比對，漏掉寫成 `**ACTIVE**` 的那列。
- **為何現在**：這是升版流程的**結構性副產物**，會反覆再犯；且任何 grep「現行版」的人或工具會得到兩個答案。
- **Schema**：不產表。
- **程式**：同 `check_treaty_refs.py` 加「修訂表狀態欄非 SUPERSEDED 者恰為 1 列」斷言。**正則須同時認 `**現行**`／`**ACTIVE**`／`現行`／`ACTIVE` 四種寫法**（本輪就是因為只認一種而漏）。
- **驗收**：現況 rc≠0；把 v1.49.0 列改 SUPERSEDED 後 rc=0。
- **治權**：否（lint）；**改修訂表文字**屬 #26「文字改正確」，但依 #19 宜呈 Steward 過目。

---

**P1-5　`validation_evidence` 與 `attestation_result` 掛誠實閘【AI 實作／【Steward】圈選】**
- **問題**：兩表**皆零 trigger**。`validation_evidence`（19 列＝green 16／red 3）是專案對外宣稱「證據鏈綠」的載體；`attestation_result`（10 列）是 watchdog 判「audit 已綠」的唯一真相源。一句裸 `UPDATE validation_evidence SET status='green'` 即可讓整個誠實性宣稱體系變綠，**無 pre-image、無留痕**。
- **為何現在**：這是「量綠燈的尺自己可被改」的最短路徑。B4 三批已把裸 UPDATE 面 20→9，這兩張是漏網且最要害。
- **Schema（不產表，掛閘）**：
```sql
-- validation_evidence（13 欄：evidence_id, chain_link, claim, check_type, check_sql,
--   check_cmd, source_ref, status, status_note, last_verified_at, created_at,
--   machine_note, valid_until）
CREATE TRIGGER trg_validation_evidence_honesty_row
  BEFORE DELETE OR UPDATE ON validation_evidence
  FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
CREATE TRIGGER trg_validation_evidence_honesty_trunc
  BEFORE TRUNCATE ON validation_evidence
  FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();
-- attestation_result 同型（14 欄，見 P0-3）
```
- **程式**：`scripts/verify_validation_evidence.py`／`ops/audit_selfheal.sh` 之寫入交易內各加 `SET LOCAL augur.honesty_write='on'`。漏補者首次執行即 fail-loud（**這是想要的訊號**）。
- **分階段**：S1 呈案圈選 → S2 DDL 窗（**#30：dump 期間禁 DDL**）→ S3 補通行證 → S4 負測（`BEGIN … ROLLBACK` 確認裸 UPDATE 被拒）。
- **驗收**：`UPDATE validation_evidence SET status='green' WHERE evidence_id='<red 之一>'` **被拒**；加 GUC 後成功；`SELECT count(*) FROM pg_trigger WHERE tgrelid='validation_evidence'::regclass AND NOT tgisinternal` = 2。
- **治權**：**邊界**——上閘屬執行層硬化，但 DDL 落治權表，建議循 B4 三批之呈案格式走一次 Steward 圈選（見 §7 S-6 之射程問題）。

---

**P1-6　sim evaluator 之 kill switch 未吃 env_halt【AI】**
- **⚠ 本項已對素材作誠實修正**：素材列「`apply_evolution_promotions.py:304` 只讀 `scope IN ('tw','global')`＝煞車射程缺口」。**親讀該處後判定此非缺口**——`:303` 之註解逐字：「V2 Phase 2.4(C6):逐 scope 口徑——**本引擎屬 tw 軸**;自軸或 global 任一 halt 即停(OR、fail-safe)」。該引擎**就是** TW 軸的 apply，讀 tw+global 是設計正確。且該處**已傳** `env_halt=_env_halt()`。⇒ **原項目撤回，不列為待修。**
- **真正的缺口在另一支**：`scripts/evaluate_sim_calibration.py:370-373` 之 `_kill_state` 呼叫 `effective_kill_state(states)` **未傳 `env_halt`**，而 runner／settle／propose 三支都有讀 `AUGUR_EVOLUTION_KILL_SWITCH`。
- **為何現在**：緊急以環境變數全域煞車時，**evaluator 是唯一照跑照寫的一支**，且方向為 **fail-open**。sim 軸剛上膛（SIM-CAL-R1 approved），煞車面不一致的成本正在上升。
- **Schema**：不產表；讀 `evolution_kill_switch`（5 列：tw/lai/raw/global/sim，現全 clear）。
- **程式**：`_kill_state` 補 `env_halt=os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH")=="halt"`（抄 runner 之既有寫法，#12 同一住所）。
- **驗收**：`AUGUR_EVOLUTION_KILL_SWITCH=halt venv/bin/python scripts/evaluate_sim_calibration.py --dry-run` → **拒跑**（現照跑）；set `sim` scope=halt 亦拒；selftest 加對應紅測。
- **治權**：否（把煞車接到它宣稱要煞的地方）。
- **教訓留檔**：素材之原判斷是「看到 `IN ('tw','global')` 就推定射程不足」而未讀上一行註解。**凡指控某處射程不足，須先讀該處自陳的射程聲明**——本專案多數關鍵處都有誠實的射程註記。

---

**P1-7　sim 三張證據表無 UPDATE 閘【AI 實作／【Steward】圈選】**
- **問題**：`sim_calibration_eval`／`sim_realized_outcome`／`sim_run_link` 現僅有 `*_no_delete`＋`*_no_truncate`，**無 UPDATE trigger**（對照 `mc_simulation_run` 已有 `honesty_ledger_guard`）。這三張恰好是「用來證明能力宣稱」的表（#32b 軸）。
- **Schema**：三表各補 `honesty_ledger_guard`（DDL 同 P1-5 形）。
- **程式**：**現行四件套全為 insert-only ⇒ 一行 code 都不用改**（低成本、高收益）。
- **驗收**：裸 `UPDATE sim_calibration_eval SET crps_mean=0` 被拒；四件套 `--selftest` 仍全綠。
- **治權**：邊界（同 P1-5，併入同一圈選案）。

---

**P1-8　sim `--apply` 只擋 K、不擋 `n_valid`【AI】**
- **問題**：`_evaluate` 於 apply 模式僅檢 `k_clusters < th["date_clusters_min"]`（:546-548），**未檢 `n_valid < th["n_valid_min"]`（100）**；`undecidable_reasons` 只印在 stdout 與 detail。
- **為何現在**：K=3 但 n_valid=60 時仍會寫 5 列帶指標的 eval 列，而門文明訂 undecidable「不得作 pass 用」；**由於 W4 判決工具不存在，沒有任何下游會讀 `detail.undecidable_reasons`**，這 5 列就是裸露的可被誤引數字。
- **Schema**：`sim_calibration_eval` 已有 `is_invalid boolean NOT NULL DEFAULT false` 欄——**現行 INSERT 完全沒用到它**。
- **程式**：apply 前把 `undecidable_reasons` 非空納入拒寫條件，或改為寫入時強制 `is_invalid=true`（用起既有欄）。
- **驗收**：構造 K=3／n_valid=60 之 fixture → 拒寫或 `is_invalid=true`（現況：寫入且 `is_invalid=false`）。
- **治權**：否（門文已定 undecidable 語意，本項是接上）。

---

**P1-9　`gate_cache` 方向鍵：用反方向證據判 validated【AI（加鍵）／【Steward】（FAIL_SIGN 新判準）】**
- **問題**：`run_philosophy_evolution.py:759/810/830` 之 `gate_cache[feature]` 以 **feature** 為鍵，而 `direction` 取自該 feature 的**第一個 principle**（`:818`，`ORDER BY feature, principle_id` ⇒ 最小 principle_id 勝）。
- **機械覆核**（本日現查，4 列）：
```
queue_id | principle_id | map.direction | G-PROM.evidence.expected_direction
   562   |     116      |      1        |   -1
   563   |     123      |      1        |   -1
   643   |     116      |     -1        |    1
   644   |     123      |     -1        |    1
```
其中 562/563 拿到的是以 dir=−1 算出的 **G-PROM=PASS ＋ G-SIGN=PASS**。目前四列因 G-ECON=FAIL 而 rejected_gate，**但只要 G-ECON 轉 PASS，即判 promote → 八閘全綠 → pending_auto → 可 APPLY** ⇒ 用反方向證據把假說判 validated（M-1 volume_gini_60d 病灶從另一入口復發）。
- **Schema**：不產表；讀 `principle_factor_map`（零 CHECK、零業務 trigger）、`promotion_queue`。
- **程式**：(甲) `gate_cache` 鍵改為 `(feature, direction)`——現僅 2 個 feature 方向衝突，額外算力 +11–12 分鐘/feature【依 07-31 實測 645–720 s/feature 推算】；(乙) `map.direction ≠ canonical ⇒ 該列直接 FAIL_SIGN`——零額外算力。
- **驗收**：上述 SQL 回**零列**（現 4 列）。
- **治權**：**部分**——(甲) 加方向鍵是純錯誤修正（不觸）；**(乙) 是新增判準（觸）**。建議先做 (甲)。

---

**P1-10　sim 時鐘無提醒機制【AI】**
- **問題**：S-4 裁定 R1 全程人工逐次觸發（不接 cron），但 settle 需在 ≈2026-09-02／10-02／11-04 各跑一次、evaluate 需在 K=3 齊後跑；而 `ops/RUNBOOK-20260803-night.md` **只寫到今晚的 runner `--apply`**，settle／evaluate 完全未入檔。
- **為何現在**：catch-up 冪等只保證「晚跑不掉格」，**不保證「有人會跑」**。時鐘會因為沒人記得而停在第一格。
- **Schema**：不產表；讀 `sim_run_link`／`sim_realized_outcome`。
- **程式**：既有週日 09:00 週報加一行 sim 時鐘哨（下一格 asof／待結算列數／K 進度）——**零新排程零新成本**；並把 settle／evaluate 兩步補進 runbook 並標日期。
- **驗收**：週報含「sim 時鐘：K=n/3，下一格 <date>，待結算 <n> 列」。
- **治權**：否（唯讀報表；不接 cron ⇒ 不違 S-4 之人工觸發裁定）。

---

**P1-11　W4 判決工具不存在＝證據鏈終點懸空【AI 實作 killed／undecidable；promoted 路徑【Steward】】**
- **問題**：`scripts/decide_sim_verdict.py` **不存在**；`sim_evolution_verdict` 0 列且**全 repo 零 writer**。⇒ 11 月 K=3 齊、evaluator 寫出 5 列後，**沒有任何載體把 k1/k2/k3 素材轉成 verdict**；專章 §5.1「判死留檔・永不靜默消失」與 §5.4「誠實無能宣告為合法產出」在 DB 層無落點。
- **為何現在**：距首次需要它約 3 個月，但**它是 sim 軸唯一的終點**；且 §2 之 k1/k2/k3 史料實測顯示 7/7 序列全判死【推論，史料非門之證據】⇒ **判死留檔的路徑極可能是首先被走到的那條**。
- **Schema（不產表）**：`sim_evolution_verdict` 三鎖已在——`chk_sev_promote_signed`（promoted ⇒ decided_by／decided_at／gate_proposal_ref 皆非空）、`chk_sev_five_arm_floor`（promoted ⇒ arms_covered ⊇ live/ceiling/floor/shuffled/mismatched）、`chk_sev_evidence_nonempty`；trigger `sev_no_delete`／`sev_no_truncate`／`sev_no_update`(GUC)。
- **程式**：新增 `scripts/decide_sim_verdict.py`（含矩陣＋selftest）。**先實作 killed／undecidable 兩條**（DB 層唯 promoted 綁三鎖，此二者腳本可寫）；`basis` 存 thresholds 逐條判式、`evidence_eval_ids` 指向 5 列 eval。**promoted 路徑一律不設人名旗標**（專章 §4.2）。
- **驗收**：以合成 eval 列跑 → 寫出 killed 列且三 CHECK 未被違反；promoted 路徑在缺 `decided_by` 時**被 DB 拒**（驗鎖真的在）。
- **治權**：killed／undecidable ＝否；**promoted 之人簽路徑＝Steward**（且 `decided_by` 由 hugo 親跑）。

---

**P1-12　`sim_evolution_iteration_ledger` 孤兒表【AI】**
- **問題**：runner 寫 `sim_run_link.iteration_uid='sim-<anchor>-r01'`，但該 uid 在 ledger 表**無對應列、亦無 FK**；ledger 0 列且零 writer。⇒ 專章 §3.6「合法目標函數唯校準品質」之 DB 層載體（`gain_basis CHECK`，限 `calibration_delta/none/incomparable`）**掛在一張永遠不會被寫的表上**——硬 CHECK 存在但守不到任何東西。
- **Schema**：對 `sim_run_link.iteration_uid` 加 FK 指向 ledger，使兩者不可能漂移。
- **程式**：runner 或 W4 開列 `iteration_uid` planned→running→終態＋`gain_basis`。
- **驗收**：`SELECT count(*) FROM sim_run_link l LEFT JOIN sim_evolution_iteration_ledger g USING(iteration_uid) WHERE g.iteration_uid IS NULL` → **0**。
- **治權**：否（補完既有 schema 之意圖）。

---

### ── P2：一個月（11 項，精簡列示）──

| # | 項目 | 一句話 | 執行者 | 治權 |
|---|---|---|---|---|
| P2-1 | 條號前綴 lint ＋清償 14 例 | `CLAUDE.md:12` 自承「殘餘待辦」但零機械載體；最尖銳者 `:62`「回歸鎖 #15」——本檔 #15＝PR/遠端，真住所是新設 **#35**；`:126`「三敵人零容忍（#1／#8／#15）」在本檔對映為「Read before Edit／報告誠實／PR 遠端」**語意全毀**。且 `:151`（#34 內，07-31 新增）**在紀律訂立後仍犯** | AI（lint）／【Steward】（逐處補前綴＝改治權檔文字，依 #19 宜逐段呈） | 部分 |
| P2-2 | `check_memory_index.py` | `MEMORY.md` 是新 session **唯一自動載入**的接續入口（#31），卻純人工維護、零稽核器。現有 1 孤兒（`machine-switch-tooling.md`）＋3 截短名＋**3 則同時自稱 ⭐權威**，而 `HANDOFF.md` 已改指 r4（untracked） | AI（稽核器）／【Steward】（「同時點只能一則現況權威」＝新判準） | 部分 |
| P2-3 | `sync_memory.py export` secret 掃描 | export 把 79 檔全量推 **public** monorepo，路徑零掃描（僅一行人讀提醒）；2026-07-13 已有一次差點洩漏 ttai admin 密碼。**不可逆**（push 後不可 force 主分支） | AI | 否 |
| P2-4 | 三支掃描器加「掃到對象數地板」 | `check_treaty_refs._iter_files`（glob 無命中＝無 finding）／`import_isolation._string_ref_violations:159`（`if not d.exists(): continue`）／`_ast_import_scan`（`except SyntaxError: continue`）——**空集合＝綠燈**橫跨三支 | AI | 否 |
| P2-5 | vendor／矩陣閘擴口徑 | `check_vendor_binding.SCAN_DIRS=("src","scripts")` ⇒ `tests/`（已知 2 處直綁）／`tools/`／`ops/`／`augur_proxy/` 全在射程外；`check_cmd_matrix.SCAN_TOP_DIRS` 不含 repo 根。**10-14 前須量準真實出血面** | AI | 否（基線重寫須 commit 訊息記口徑變更） |
| P2-6 | 夜間 selftest sweep | **292 支 `--selftest` 中僅 3 支在排程**（週一 08:40 三支 MCP）；`crontab -l \| grep -c pytest` = **0**，26 支 pytest 零排程。#18／#29(d) 之「每支可個別驗證」事實上只是「可被驗證」 | AI | 否（#28 本地優先） |
| P2-7 | 隔離閘字面面補三包 | `augur.arena`／`augur.execution`／`augur.deliberation` **不在任何字面掃描集合**；而 07-31 單一角色整併後 `augur_predict` REVOKE 對偶已消失 ⇒ **AST/字面閘為唯一閘**。現況乾淨純屬巧合（檔內註解已自陳） | AI | 否 |
| P2-8 | `knowhow_auto_admit_run` 帳本止血 | 556 MB／509,551 列，每輪 `--until-empty` 再加 ≈14.6 萬列（+160 MB），而絕大多數列 `layer_scores` 逐字相同 | AI | **邊界**（減少留痕可能被讀為削弱，見 §7 S-7） |
| P2-9 | evolution ledger 空欄補寫 | 11 個欄位全庫零寫入；**`apply_allowed` 全 false**——driver 開輪硬寫 false（`:282`）且全檔無處改為 true，即使跑 `--allow-apply` 也不寫。⇒ #26 授權四要件之留痕在正規欄位上是空的 | AI | 否 |
| P2-10 | GROUNDING-MAP 數字改 lint 綁定 | `:45-47` 三列仍記 registry「零跡象」、直綁 37 檔（07-17 口徑），而 live 已有 registry 五物件＋直綁 50/56。沿用既有 `<!--lint:KEY-->…<!--/lint-->` ＋ `--sync` 機制 | AI | 否 |
| P2-11 | D1 回填自動化 | `backfill_fulltext_unattempted.py` 是一次性、無排程；**每日漏 21 件**（現查隱形 21 件，與 `ata_advance.log` 之 `pending 121389→121410` 獨立互證）。零 API、分批冪等、成本近零 | AI | 否 |

---

### ── P3：待裁（5 項，全部觸治權判準，AI 只呈案）──

| # | 項目 | 為何 AI 不動手 |
|---|---|---|
| **P3-1** | **`gate_scale` 指紋升級** | `_gate_scale`（`run_evolution_iteration.py:131-153`）只指紋 `min_abs_hac_t` ＋「有無 G-SIGN 鍵」，**未涵蓋** min_seeds／min_panels／min_delta_ic／G-ECON cost·top_frac·max_dd_floor／G-SIGN n_boot_seeds·min_series／since／horizon_h／panel 數。碼內註解（:56-58）**已自陳**「縮 `--since` 換 panel 口徑而 `_gate_scale` 看不出來」卻未修——**靜默換尺**，2026-07-26 量尺失效之同型病。但 `gate_scale` 是「什麼算可比」之判準輸入，**改它即改判準** |
| **P3-2** | **KH0 結構性破口修復** | 現查破口 **138,875/285,227（48.7%）**，其中無原文 138,826。兩個唯一的 state 列產生者都硬性要求有全文（`auto_admit.py:719` INNER JOIN／`ingress_kip.py:92` EXISTS）⇒ `--run --phase advance` 只能關 49 件（0.035%），事後驗證**必然印「✗ KH0 底線不變式未回復」並 return 4**＝**一個永遠紅、且紅得不會變綠的閘**（一個月內必被當「已知紅燈」忽略）。修 SQL 屬執行層，**但 `evaluate_layer(0)` 對無原文者該判 pass 還是 fail 是 v1.53.0「標題即有語意」之條文解釋** |
| **P3-3** | **三則記憶級規則升格入 CLAUDE.md** | 人簽不代打／git add 逐檔明列／pgrep 正法。其中 `CS-CLAUDE.md:50` 已把 `§P5.E1／§P5.W2` 之落點指向記憶檔 `never-type-human-signature`，而 **CLAUDE.md 全文對此零字**；DB 層又已證 `decided_by` 零 CHECK、`augur` 為 superuser ⇒ **此規則是該義務唯一實質防線，卻掛在最易蒸發的一層**。但「人簽不代打」正是 AI 自身監督機制 ⇒ `AUGUR-L6 v1.2` L6.18(a)：**AI 不得為核准主體** |
| **P3-4** | **trigger 改 `ENABLE ALWAYS`** | 現查 116 支全為 `'O'`；親驗 `SET LOCAL session_replication_role='replica'` 成功 ⇒ **無 DDL、無鎖、schema 無差異、事後鑑識查不到痕跡**地靜音全部誠實閘。`ENABLE ALWAYS` 是不動角色架構下**唯一**能實質提升強度的手段。但「加嚴」在本專案有明文程序（GATE-raise），其對象是判準文字；本項不動判準文字只讓判準更難繞——**屬執行層硬化還是判準變更，須 §8.1 解釋** |
| **P3-5** | **兩本存量基線之清償期限與配額** | 假斷言 20 條 ERROR（基線 22 行）／vendor **56 檔 172 處**（基線 128 指紋）。棘輪**只擋新增、不設縮減義務**；WM.36 於 2026-10-15 起無條件適用，屆時未清償即為違規存量。**清償節奏屬治理排程決定，AI 不得自訂期限**（v1.31 亦禁 AI 自訂生效要件） |

---

## §3 依賴圖與排程建議

### 3.1 依賴圖

```
                       ┌─────────────────────────────────────────┐
  【今日 20:00 前】     │ P0-1 sim q_grid 契約  ◄── 最硬的時間點   │
                       └───────────────┬─────────────────────────┘
                                       │ 首格落地後不可改形狀
                                       ▼
                        P1-8 n_valid 閘 ─► P1-11 W4 判決工具 ─► P1-12 ledger FK
                                       ▲
                        P1-10 時鐘哨 ───┘（提醒 settle／evaluate 要跑）

  【今日 23:00 前】     P0-4 cleared_at ──► P0-6 週報 gate_ref
                        （run 22 前修完，否則又一輪假告警）

  【本週】              P0-2 worktree ──► 一切後續 commit 的前提
                        P0-3 reconcile ──► S1 影響面 ──► S2 接 verdict
                        P0-7 refresh fail-loud ──► (hugo 授權) unit 修正

  【10-14 倒推】        P0-5 探針表 ──► P1-3 CS lint ──► P1-4 雙現行 lint
                              │              └──► P2-10 GROUNDING-MAP 綁定
                              └──► S3 欄位級映射（8月下起跑）──► S4 hugo 親簽
                                                                    │
                                                                    ▼
                                                          10-14 併審備料
  【並行、無依賴】      P1-1 死碼／P1-2 prior_depth／P1-5,7 掛閘／P1-6 kill scope
```

### 3.2　10-14 硬期限倒推（距今 72 日）

| 時點 | 里程碑 | 為何是這個時點 |
|---|---|---|
| **08-03（今日）** | P0-1 修完（首格前）；P0-4 修完（run 22 前） | 兩個當日不可逆窗口 |
| **08-09（本週末）** | P0-2/3/6/7 完成；P0-5 探針表 S1 產出**今日基線值** | 基線越晚建，能觀察到的 diff 越少 |
| **08-23** | P1 全 12 項完成；探針入週報（S2） | 留 7 週給欄位級映射 |
| **08-31** | **P0-5 S3 起跑**（98 列通道 × 欄位級展開） | 【推論】若此日未起跑，10-14 前完成機率顯著下降 |
| **09-30** | S3 完成：`count(source_column) = 98` | 留 2 週給 S4 人簽 |
| **10-05** | **S4 hugo 親簽窗**：`authoritative_binding_id` ＋ `decided_by` 落值 | **AI 絕不代打**；須排 hugo 的時間 |
| **10-09／10-10** | 5 條 manual `validation_evidence` **valid_until 到期** | `chk_ve_manual_expiry` 已上線；到期自動降 unverified |
| **10-10** | 併審備料定稿；**不代勾任何 checklist 項** | 留 4 日緩衝 |
| **2026-10-14** | Steward 併審 | — |
| **2026-10-15** | WM.36 起**無條件適用** | vendor 存量（現 172 處）須在此前清償或取得豁免【Steward，P3-5】 |

⚠ **10-09/10-10 的 manual 證據到期與 10-14 併審只差 4 日**——其中 `E3_promotion_funnel`／`E4_gm_promotion_gap` **連 `last_verified_at` 都是 NULL**（從未被任何機械斷言檢驗過）。到期時是「重簽」還是「轉為 sql 型」須 Steward 先裁（§7 S-5），**不宜留到 10-09 當天才問**。

### 3.3　不可壓縮鏈（純等待，無法趕工）

```
sim 校準時鐘：anchor(08-03 收盤後) ─21td─► 格1(≈09-02) ─21td─► 格2(≈10-02) ─21td─► 格3(≈11-04)
                                                                              └─► K=3 齊，可 evaluate
TWEVO 週輪：每週一至五 23:00（今晚 run 22 ＝ I5B supersede 首次生效點）
```
**這兩條上的任何缺陷，發現越晚，已浪費的等待越不可回收。**（原則三）

---

## §4 資源與車道

### 4.1　四條車道與其真實瓶頸

| 車道 | 容量 | 本計畫佔用 | 瓶頸 |
|---|---|---|---|
| **AI（Claude）** | 依 #28 檔位分派：理解層 Fable 5／重執行 Opus 4.8／輕執行 Sonnet 5 | P0/P1 之絕大多數 | **不是瓶頸**。#34 已反向廢止「非必要不 fan-out」，平行度可拉滿——**但須加檔案集不重疊之前提**（見 §7 S-4） |
| **hugo 的時間** | 稀缺、不可替代 | P0-5 S4 親簽／P0-7 S2 授權／P3 全部／§7 八項裁決 | **真正的瓶頸**。所有 `decided_by`／`approved_by`／`promoted_by` 一律 hugo 親跑（記憶 `never-type-human-signature`） |
| **DB（augur 61 GB）** | 單機 PostgreSQL | P1-5/7 之 DDL 窗；P2-8 帳本止血 | **#30：dump 期間禁 DDL**（ACCESS EXCLUSIVE 被擋 → 鎖風暴 → 全庫查詢 hang）。DDL 一律排在 dump 完成後 |
| **heavy slot** | 序列化、一次一個重活 | TWEVO I3（現需 7–10 小時）／KH 全量重評（P3-2） | **P3-2 若獲准，需一次處理 13.8 萬件**——須先實測單件成本再排 |
| **Ollama／本地 LLM** | 三模型 | 本計畫幾乎不用 | 非瓶頸（本計畫以機械檢查為主，#28 本地優先） |

### 4.2　排程既有佔用（現查 `crontab -l` 15 行／7 個 user timer）

```
23:00 週一至五   TWEVO run_evolution_iteration --run --slot-wait 10800（刻意不帶 --allow-apply）
09:00 週六        RAWEVO
09:00 週日        三軸週儀表 ◄── P0-6／P1-10 掛這裡（零新排程）
07:10 每日        證據帳本重驗（sql 型）
07:40 週日        證據帳本重驗（含 script_exit 型）
08:40 週一        三支 MCP --selftest ◄── P2-6 selftest sweep 可掛這裡
02:00 週日        augur-knowhow-refresh（現空轉，P0-7）
04:00 每日        ata-advance（現近空轉：切句 0／實插 0／新嵌 0）
20:00 每日        run_arena_daily_pipeline --run ◄── 今晚讓 sim anchor 實現
```
**本計畫新增排程數＝0**（P0-6／P1-10／P2-6 全部掛既有班次）。這是刻意的：新排程是新的失效面。

### 4.3　工作量估計（附依據）

| 群組 | 估計 | 依據 |
|---|---|---|
| P0-1／P0-4／P0-6 | 各 ≤1h | 單行至數行改動＋回歸鎖；比照 B4 三批之單表改動節奏 |
| P0-2 | 半日 | hook 改 ≤10 行；新 script ≈100 行（比照 `check_worktree_treaty_sync` 同型之 `check_cmd_matrix`） |
| P0-3 | 半日 | S1 唯讀影響面掃描為主要成本（全表對帳） |
| P0-5 S1 | 1 日 | 二表 DDL＋三 script（含矩陣＋selftest），比照 `migrate_sim_evolution_ddl` ＋四件套之落地量（四件套由 commit `92647f0` 一次落地） |
| **P0-5 S3（欄位級映射）** | **未估，須先抽樣** | 98 通道 × 欄位展開；`column_catalog` 已在，但展開比例未量。**這是本計畫最大的未知數**，建議 08 月中先抽 10 列量單位成本 |
| P1 全 12 項 | 3–5 日 | 多為單檔小改＋回歸鎖；P1-11（W4 工具）約占 1.5 日 |
| P2 全 11 項 | 5–8 日 | P2-1（14 例逐處補＋lint）與 P2-6（首輪基線）為大宗 |

⚠ **P0-5 S3 未估**——誠實標示，不編造數字。

---

## §5 明確不做（防後人重提）

| 不做 | 為何 |
|---|---|
| **改 `RULING-2026-042` 正文之閘位數字** | 該裁決已簽生效，依大憲章 v1.51.0 通則一**史述凍結**。其 §二2 記「delete_only 23 表／ledger_guard 5 表」，本日實為 **9／25**（方向反轉）——**這是正確的、不該改**。正解是另立滾動快照（`audits/L716-COMPENSATING-CONTROLS-<date>.md`）並在 10-14 議程標明「042 §二2 為 08-01 快照」 |
| **把 `constitution_lint --selftest` 現在就掛 pre-commit** | 現跑 rc=1，唯一 FAIL＝G10 界線（`### TR.Z …（DRAFT）` 殘留是否構成 status error）。**掛了會使 repo 立即不可 commit**。且該 FAIL 是條文解釋、專屬 Steward（§7 S-1）。在裁定前不掛——hook 標頭之誠實註記已記此為刻意 |
| **安裝 `tools/constitution_lint/github-workflow.yml` 為 CI** | 同上（selftest 未綠）。但**須更正該檔頭之過期阻斷理由**：檔頭載「接線前置：WM.44-LABEL 尚有未結之 error」，而 **live report 實為 WM.44-LABEL error＝0（L1–L7 全 0）**——照檔頭去排障會排錯東西 |
| **恢復非 superuser 寫入角色（回退單一角色整併）** | 這是唯一能根治 P3-4 的手段，但屬**不可逆、跨治權檔**之架構決定，會重啟已結案的整併。hugo 07-31 曾主動問過此題且該題仍在 `awaiting_hugo`。**AI 不得提案回退已結案之架構決定**，只得如實揭露強度上限 |
| **接上 I1/I2（`feature_candidate_values` → 漏斗 → `feature_values`）** | 現有 390,274 列候選（11 feature）躺著，且這 11 個正是 coverage_class='missing' 而八閘全 SKIP 者。**這是 `dual_green_n` 唯一可能成長的來源**，但新特徵入生產須走原則精華 #11 第 4 道提拔關卡＋#14 經濟終關，**不得由 driver 逕自擴權**（`run_evolution_iteration.py:75-79` 之射程聲明已明示此界）。列入 §7 S-8 供 Steward 決定是否另立計畫 |
| **自行 INSERT `knowledge_domain_map`（納 erp_tiptop）** | 唯一 100% 可答的 erp_tiptop（141,873 件）因不在映射工件而 `kh_axis_state=pending`；而 mapped 的 quant_finance 12,414 件反而不可答。**但該表語意是「決策層拍板域的機械名冊、納新域＝人 INSERT 一列」（#29b），AI 不得自行 INSERT**（§7 S-9） |
| **開啟 cron 的 `--allow-apply`** | 現行刻意不帶（`install_cron.sh:71-77` 記明理由）。**且在 P1-x 未修前開啟＝啟用無武裝閘的整批路**——driver 不把 `--allow-apply`／`--gate-ref` 傳給子行程（`:251-256`），子行程走 `queue_id=None` 分支（`apply_evolution_promotions.py:73` **直接 return True**）；現查該路徑一句即 `applied=17`（含 16 筆 FAIL_SIGN demote＋1 筆 promote）。屬授權層（§7 S-8） |
| **為 KH8 調鬆 `MIN_MINORITY_MASS`** | 現查 `population_discriminates` → ok=**False**（band_minority_mass=0.0027 ≪ 0.05）。**改 0.02 仍 fail**（雙重冗餘）。調閾值以求綠燈＝挪門柱，正是本專案零容忍者 |
| **在本計畫代勾任何 10-14 checklist 項** | F2 已立此紀律；RULING-2026-039 禁止假關。探針只產生**值**，勾選是 Steward 的動作 |
| **新增排程** | 本計畫新增排程數＝0，全部掛既有班次。新排程＝新失效面 |

---

## §6 驗收與里程碑總表

| # | 項目 | 機械驗收判準（一行可跑） | 期限 | 執行者 | 治權 |
|---|---|---|---|---|---|
| P0-1 | sim q_grid | `normalize_q_grid(真 _q_grid 輸出)` 非 None 且 len=99；退回舊版 selftest **rc≠0** | **今日 20:00 前** | AI | 否 |
| P0-2 | worktree 雙失效 | `cd <worktree> && bash ops/githooks/pre-commit` 不印「略過」；venv 缺 → **rc=1** | 本週 | AI／【S】 | 分裂 |
| P0-3 | reconcile 假綠 | fixture `coverage_gap=True` → `_summary()` 回 `passed=False` | 本週 | AI | 否 |
| P0-4 | cleared_at | driver 印「積壓 **0** 列」（現 9）；A8 對 rc=75 fixture **FAIL** | **今晚 23:00 前** | AI | 否 |
| P0-5 | 10-14 探針 | `read_treaty_probes.py --check` rc=0，7 探針皆有 reading | S1 本週／S3 09-30／S4 10-05 | 兩者 | 部分 |
| P0-6 | 週報 gate_ref | digest 筆數 = `count(*) FROM evolution_apply_log WHERE applied_at >= now()-'7d'`（現 23 vs 顯示 20） | 週日前 | AI | 否 |
| P0-7 | refresh 空轉 | `--domain finance` → **rc≠0** | 本週（S2 待授權） | AI／hugo | 否 |
| P1-1 | retrieval 死碼 | 第二次 `kh_evidence_valid()` **<0.05s**；ok=False 時排序逐項不變 | 08-23 | AI | 否 |
| P1-2 | prior_depth | `layer_scores` 含 `prior_depth` 且 `"pass"` 之列 → **0**；depth 分布不變 | 08-23 | AI | 否 |
| P1-3 | CS 版本 lint | 現況三檔各報 finding（**先驗紅**）；修正後 rc=0 | 08-23 | AI | 否 |
| P1-4 | 雙現行 lint | 修訂表非 SUPERSEDED 者**恰 1 列** | 08-23 | AI | 否 |
| P1-5 | 綠燈帳本掛閘 | 裸 `UPDATE validation_evidence SET status='green'` **被拒** | 08-23 | AI／【S】 | 邊界 |
| P1-6 | evaluator env_halt | `AUGUR_EVOLUTION_KILL_SWITCH=halt` → evaluator **拒跑**（現照跑）。**註：素材所列之 apply 射程缺口已撤回**（親讀為設計正確） | 08-23 | AI | 否 |
| P1-7 | sim 三表 UPDATE 閘 | 裸 `UPDATE sim_calibration_eval` 被拒；四件套 selftest 全綠 | 08-23 | AI／【S】 | 邊界 |
| P1-8 | n_valid 閘 | K=3／n_valid=60 fixture → 拒寫或 `is_invalid=true` | 08-23 | AI | 否 |
| P1-9 | 方向鍵 | 方向不符 SQL 回**零列**（現 4 列） | 08-23 | AI／【S】 | 部分 |
| P1-10 | sim 時鐘哨 | 週報含「K=n/3、下一格、待結算 n 列」 | 週日前 | AI | 否 |
| P1-11 | W4 判決工具 | 合成 eval → 寫 killed 列；promoted 缺 `decided_by` **被 DB 拒** | 09-30 | AI／【S】 | 部分 |
| P1-12 | ledger FK | `sim_run_link` LEFT JOIN ledger 之 NULL 列 → **0** | 09-30 | AI | 否 |
| P2-1…11 | （見 §2 P2 表） | 各項見該表 | 09-30 | 多數 AI | 多數否 |
| P3-1…5 | （見 §2 P3 表） | **待裁後定** | — | 【Steward】 | 全觸 |

**里程碑三點**：
- **M1（今日）**：sim 時鐘保住 ＋ run 22 告警恢復真訊號。
- **M2（08-23）**：P0＋P1 全清；治權層自我一致性首次有機械載體；Steward 週掃視不再對新路徑失明。
- **M3（10-10）**：10-14 併審備料定稿，**七項 checklist 各有一個現查值**（不代勾）。

---

## §7 Steward 決定欄（本計畫本身需拍板者）

> 以下九項為**本計畫無法自行推進**之節點。AI 已備妥證據與選項，**不代裁**。
> 每項標明：卡住誰／選項／若不裁的後果。

| # | 待裁事項 | 卡住 | 選項 | 不裁的後果 |
|---|---|---|---|---|
| **S-1** | **`constitution_lint --selftest` 之 G10 界線 FAIL 如何處置？**（`### TR.Z …（DRAFT）` 殘留是否構成 status error——屬條文解釋，DRAFT 標記之效力界線由誰認定） | P1 之「掛第六閘」；連帶 CI 全面接線 | (甲) 認定 linter 不應報紅 → 修斷言；(乙) 認定應報紅 → 先更正各規格 TR.Z 殘留，或依 §8.4 核發有到期日豁免；(丙) 標 known-issue（`--allow-known-fail`＋audits 留痕）後掛閘 | **291 條治權斷言永遠無自動觸發點**（WM.40 閉集擴欄鎖、WM.44-LABEL 上位原文鎖、`<!--lint:KEY-->` 數字綁定鎖、跨層逐字誤標鎖全部只在有人想到時才跑）＝防呆機制自己靜默失效之第八型 |
| **S-2** | **`RULING-2026-043` 之編號與形制如何收束？** 11+ 張表之誠實閘架構以「RULING-2026-043／B4-043」為法源施作，**但 `constitution/` 無該檔**（現查 `ls constitution/RULING-2026-043*` → 不存在），`AMENDMENT-LOG` 無對應 AL。**現查 17 處引用**散在 4 支生產碼＋2 份 audits | B4 架構之可稽核性；10-14 盤點 | (甲) 補作正式裁決檔＋AL-2026-047，追認 P0/P2a/P2b 為同案分批；(乙) 明示「圈選留痕即為完整裁決、不編號」並令 AI 清除碼內 17 處字樣、改引呈案檔路徑 | 依 `ls constitution/*RULING*` 盤點時**這批治權變更完全不可見**；且與 042 §四「`ls … \| tail -1` → 本檔」之驗證慣行直接衝突（043 號已被佔用而無檔） |
| **S-3** | **worktree 是否為 #13 允許之工作場所？** #13 現行文字只禁「寫」worktree，未規範「從 worktree 執行／讀治權檔」。實測三項減損：過期治權檔（本 session 讀到 v1.32 vs main v1.35）、失去 project-memory recall、五閘靜默跳過 | P0-2 S4 | (甲) 禁止在 worktree 起實作型 session；(乙) 允許但強制先同步治權檔＋hook fail-closed；(丙) 其他 | 三者皆為**監督強度之實質減損**，依 #26 OCV 單向棘輪屬「任一分量弱化即推定違反、須書面裁決」。不裁＝棘輪已被靜默鬆開 |
| **S-4** | **#34 是否增列第 (iv) 項硬邊界「並行以檔案集不重疊為前提」？** #34「平行度預設拉滿、不自行保留餘裕」之三項硬邊界（配額護欄／OCV 棘輪／#33）**未含撞檔**；唯一撞檔護欄活在記憶檔 `no-concurrent-agents-same-files` | §4 之 AI 車道；本次三 agent 並行 | (甲) 增列 (iv)；(乙) 不增，明示以任務編排層保證 | 本次三 agent 並行是靠父 agent**口頭約定**「只新增不修改」規避，**不是靠規則**。依 #34 字面把路數開滿即可重演 07-07 advise.py 混改 |
| **S-5** | **5 條 manual `validation_evidence` 於 10-09／10-10 到期後之處置** 其中 `E3_promotion_funnel`／`E4_gm_promotion_gap` **連 `last_verified_at` 都是 NULL**（從未被任何機械斷言檢驗過） | §3.2 之 10-09 節點 | (甲) 重簽（人審）；(乙) 轉為可機械化之 `sql` 型；(丙) 逐條分流 | 到期日距併審僅 4 日；若當天才處理，會在併審前夕製造 5 條 unverified。**宜先裁** |
| **S-6** | **「帳本表不掛 honesty trigger」之射程** Steward 已於 08-03 就 `vendor_binding_strangler_ledger` 併裁不掛。是否延伸至其他 **30 張零 trigger 之治權味表**？要害四張：`attestation_result`(10 列)／`validation_evidence`(19 列)／`model_registry`(16 列)／`knowhow_auto_admit_gate_change`(**0 列**) | P1-5／P1-7／P0-5 新表 | (甲) 不延伸 → 四張要害補閘；(乙) 延伸 → 「帳本不掛閘」成為可引用之通則（而非個案） | 不界定射程，則每張表都要重新爭論一次；且 P0-5 新增之 `treaty_probe_reading` 該不該掛也無依據 |
| **S-7** | **`knowhow_auto_admit_run` 之留痕義務範圍** P2-8 可省 556 MB 表之線性膨脹（每輪 +14.6 萬列／+160 MB），但該表是准入評估帳本 | P2-8 | (甲)「每次評估都必須留一列」＝誠實要件 → P2-8 不可做，改分區/歸檔；(乙)「每個**不同**評估結果留一列」→ 去重合規 | 涉及帳本語意，**且一旦刪過就不可逆** |
| **S-8** | **兩項授權邊界（建議併案裁）** (a) 是否開啟 cron `--allow-apply`？(b) 是否接上 I1/I2 讓 `dual_green_n` 有成長來源？ | §5 兩項「明確不做」之解禁條件 | (a) 現行不帶＝刻意（`install_cron.sh:71-77`）；**在整批路武裝閘未修前開啟＝一句即 `applied=17`**。(b) 接上須走提拔關卡＋經濟終關 | `compare_gain` 要求 `dual_green_n` **逐輪嚴格遞增**，而 prodset_delta 在人閘模式下**結構上恆為 0**（v2 口徑限縮 `source_run_id=本輪`，而 APPLY 一律發生在結輪之後）⇒ **平台期（哪怕停在健康的 2）一律記 gain=False，三輪即 `stopped_no_gain`**。不裁＝停損只是時間問題 |
| **S-9** | **`knowledge_domain_map` 是否納 erp_tiptop？** 唯一 100% 可答之語料（141,873 件）因不在映射工件而 `kh_axis_state=pending`；而 mapped 的 quant_finance 12,414 件反而不可答（`answer_status=provisional`） | P1-2 之後的 KH5 語意 | (甲) 登錄為已拍板域；(乙) 不登錄，並確認「KH5 對本系統最主要可答語料恆 pending」不算 D3 之證偽條件 | AI 不得自行 INSERT（#29b：納新域＝人拍板）。不裁＝D3 的軸判準與可答性**持續負相關**，而該指標會被誤讀為健康度 |

**另需 Steward 知悉（不需裁，但屬本計畫之前提）**：
- P3 五項（gate_scale 指紋／KH0 結構修復／三則記憶升格/ENABLE ALWAYS／基線清償期限）全部待裁，其中 **KH0 現為一個永遠紅的閘**（48.7% 破口，結構上補不起來），恆紅閘會在數週內喪失訊號價值。
- 本計畫**射程限於 Z1–Z6**（見 §0.4），Z7–Z10 與三份對抗審查未納入。

---

## 附錄 A　本輪推翻既有報告之處（報告說 X／live 實為 Y）

| # | 報告說 | live 實為（本日現查） | 出處 |
|---|---|---|---|
| 1 | F2 備料：World Concept Registry 表本體＝**NONE** | 五物件皆在（08-02 21:23 落地），但**登錄完成 0/6** | `reports/augur_1014_review_evidence_prep_20260801.md` §1(b) vs `world_concept_registry_current` |
| 2 | RULING-042 §二2：delete_only **23** 表／ledger_guard **5** 表 | **9** 表／**25** 表（方向反轉） | 042 為 08-01 快照；**史述凍結，不得改** |
| 3 | GROUNDING-MAP：直綁 **37** 檔 | 同 grep **50** 檔／止血閘 **56 檔 172 處** | `GROUNDING-MAP.md:46`（07-17 口徑） |
| 4 | 素材：vendor **170** 處 | **172** 處（今日 commit `45ea88d` 擴口徑） | `check_vendor_binding.py --scan` |
| 5 | 記憶 r3：`feature_sign_check` **0 列**／G-SIGN 未入閘（七閘） | 40 列 36 feature／**八閘**，run 21 全 111 列皆有 G-SIGN 鍵 | `augur-deep-understanding-r3-20260801.md:66,69` |
| 6 | 記憶 r3：prodset active **2** | **3**（inst_cumflow_position_120d／cycle_position_252d／lending_fee_rate_mean_30d） | 現查 `evolution_production_feature_set` |
| 7 | 記憶 r3：`evolution_run` 9 列 running／deferred 未清 7 筆 | running **0**／deferred 未清 **0**（total 9） | 現查 |
| 8 | 記憶：綠燈帳本 green14/red5 | **green 16／red 3** | 現查 `validation_evidence` |
| 9 | 記憶：`check_cmd_matrix` 437/437 | **467/467** | 本日實跑 |
| 10 | 記憶：「四個真有價值的閘全部不會自己跑」 | pre-commit **已於 08-02 21:20 上崗掛 5 閘**（後半句「無 CI」仍真） | `.git/hooks/pre-commit` mtime |
| 11 | 記憶「只剩一個庫」 | **3 個** DB（`postgres`／`augur` 61 GB／**`augur_sandbox` 34 MB／14 表**） | 現查 `pg_database` |
| 12 | 專章附一：`mc_simulation_run` trigger 數 **0**（可被無痕 DELETE） | **2 個** trigger，DELETE 已拒 | 專章附一為 07-31 快照 |
| 13 | 素材：`reconcile_audit` 假綠**已成鏈** | **latent**——`passed=true AND coverage_gap_n>0` 之列數 **= 0**（尚未實際騙過一次） | 本輪修正，現查 `attestation_result` 全 10 列 |
| 14 | `github-workflow.yml` 檔頭：接線受阻於 WM.44-LABEL 未結 error | live **WM.44-LABEL error = 0**（L1–L7 全 0）；真阻斷改為 selftest 之單一 G10 FAIL | 該檔頭理由已過期 |
| 15 | `CLAUDE.md:127`：scripts 稽核 **137/137** | **467/467**（README 已由 Steward 拍板刪同型硬編數，CLAUDE.md 未同步） | 本日實跑 |
| 16 | **素材**：`apply_evolution_promotions.py:304` 只讀 tw+global ＝射程缺口 | **非缺口**——`:303` 註解自陳「本引擎屬 tw 軸」且已傳 `env_halt`。**本輪撤回該項**（見 P1-6） | 親讀 `:300-308` |

> **方法論教訓**：15 項中有 9 項是**兩日內**產生的漂移。這印證了 P0-5（探針綁定表）與 P2-10（GROUNDING-MAP lint 綁定）的必要性——**在這個變動速率下，任何手抄的數字在寫下的當天就開始腐爛。**

---

## 附錄 B　覆核指令彙編（全部唯讀）

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a

# P0-1 sim q_grid 契約
venv/bin/python -c "
import sys;sys.path.insert(0,'scripts');sys.path.insert(0,'src')
import _bootstrap, numpy as np
from evaluate_sim_calibration import normalize_q_grid
from run_sim_calibration_cell import _q_grid
print(normalize_q_grid({'terminal_q_grid':{'unit':'x','p':_q_grid(np.linspace(-.5,.5,20000))}}))"

# P0-2 worktree 五閘略過
for w in $(git worktree list --porcelain | awk '/^worktree/{print $2}'); do
  echo "== $w"; [ -d "$w/venv" ] && echo "  venv YES" || echo "  venv NO -> hook exit 0"; done
head -1 CLAUDE.md; head -1 .claude/worktrees/*/CLAUDE.md

# P0-3 reconcile 判式 vs library
sed -n '155,160p' scripts/reconcile_audit.py; sed -n '585,588p' src/augur/audit/reconcile.py

# P0-4 deferred 謂詞
psql-> SELECT count(*) FILTER (WHERE cleared_at IS NULL) uncleared, count(*) total FROM evolution_deferred_work;

# P0-5 WM.36 登錄完成度
psql-> SELECT count(*) n, count(*) FILTER (WHERE authoritative_binding_id IS NULL) no_auth,
              count(*) FILTER (WHERE decided_by IS NULL) no_dec FROM world_concept_registry_current;
psql-> SELECT mapping_status, count(*), count(source_column) FROM world_channel_binding GROUP BY 1;
venv/bin/python scripts/check_vendor_binding.py --scan   # 口徑 caliber_sha256=0e0e608f75122bf5

# P0-6 週報失明
psql-> SELECT evidence_json->>'gate_ref', count(*) FROM evolution_apply_log
       WHERE applied_at >= now()-interval '7 days' GROUP BY 1;

# P1-9 方向衝突四列
psql-> SELECT q.queue_id, q.principle_id, m.direction,
              q.gate_json->'G-PROM'->'evidence'->>'expected_direction'
       FROM promotion_queue q JOIN principle_factor_map m USING(principle_id, feature)
       WHERE q.run_id=21 AND m.direction::text <> q.gate_json->'G-PROM'->'evidence'->>'expected_direction';

# P3-4 trigger 強度上限
psql-> SELECT tgenabled, count(*) FROM pg_trigger WHERE NOT tgisinternal GROUP BY 1;   -- 全 'O'
psql-> SELECT rolname, rolsuper FROM pg_roles WHERE rolname NOT LIKE 'pg\_%';          -- 兩者皆 super

# S-1 / S-2
venv/bin/python -m tools.constitution_lint --selftest > /tmp/l.txt 2>&1; echo rc=$?   # 1（勿接 pipe）
ls constitution/RULING-2026-043* ; grep -rln "RULING-2026-043" scripts src audits
```

---

**本檔結束。** 全檔為呈案，**未執行任何優化項**；零 DDL、零寫入、零 commit。
標【Steward】之九項待裁事項未代裁，恆紅閘與硬期限已如實揭露。
