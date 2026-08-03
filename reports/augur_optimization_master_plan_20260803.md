# Augur 統一優化執行總計畫（2026-08-03）——後續優化之唯一執行依據

> **性質**：[I] 執行 SSOT（CLAUDE #16／#20）。**不創設治權判準**；不解凍 API；不降閘；不代簽。
> **產出者**：AI 合成（四路補齊 × 三份素材 × 現查覆核）。**self-reported（#32a）**：本檔一切「這是債／這是假綠／這會安靜地讓錯的東西通過」之判讀均為 AI 自陳，**不得作為「世界如此」之權威確認**；凡附覆核指令者，指令輸出才是證據。
> **資料時點**：全部數字為 **2026-08-03 10:13–10:20 CST 現查**（psql／實跑腳本／systemctl／crontab／git／檔案系統），零抄舊值。repo HEAD＝`f7c7c68`。
> **本輪唯讀**：零 DDL、零 DB 寫入、零 commit、零 systemctl、未改任何既有檔（唯一寫入＝本檔）。

---

## §0 三問直答 ＋ 一頁總圖

### 0.0 本檔與前三份的關係（生效力宣告）

| 檔 | 原地位 | 自本檔起 | 殘餘價值（仍應讀） |
|---|---|---|---|
| `reports/augur_deep_understanding_r4_20260803.md` | 問題與槓桿 SSOT | **素材（問題發現層）** | §3 對抗三表之**證據與覆核指令**、§5 踩雷 20 則（T1–T20 全部仍有效，本檔不複述）、§8 誠實邊界 |
| `reports/augur_optimization_plan_20260803.md` | 優化排序計畫（35 項 P0–P3） | **素材（內容層）** | §1 五條排序原則之**說理**（本檔 §0.4 承接）、各項之 schema／程式規畫細節（本檔只引不複製）、附錄 B 覆核指令 |
| `reports/augur_optimization_execution_plan_20260803.md` | 執行編排（拍板碼 `OPT-EXEC-20260803-go`） | **素材（框架層）＋部分前提已失效** | §2 資源與互斥表之**框架設計**、拍板碼分句設計（`W0-go`／`FZ-keep`／`GATE-keep`／`NHC-keep`）。⚠ 其 W0 全波前提（I5B 待施作）**已於寫成前 12 小時不成立**，見 X2 |

**本檔取代前三份之「執行指引」地位**。三份降為素材／史料，**其個別優先級與波次編號不再具執行效力**——凡與本檔 §2 序列衝突者以本檔為準。三份之**證據、覆核指令、schema 規畫、踩雷紀錄**全部保留有效，本檔以引用方式承接、不複製。

⚠ **前三份不得被讀為「已結」**：r4 §8 自陳未讀全 repo；優化計畫書 §0.4 自陳射程限 Z1–Z6；執行計畫未自陳射程。本檔補齊了 Z7–Z10 與三份對抗審查，但**仍不是全專案優化的完整集合**（見 §8）。

---

### 0.1 【問一】最佳下一步是什麼？

> # **M-G1：修 worktree 雙失效——pre-commit 改 fail-closed ＋ 治權檔同步稽核器**
> **執行者＝AI（S1–S3）／hugo（S4 文字裁決，不阻塞前三步）｜【可先做】｜半日｜零 DB 零 API 可逆**

**現查證據（2026-08-03 10:14，三項獨立）**：

```
三 worktree venv：can-use-ca1439=NO／project-analysis-report-fc3448=NO／zai-ma-9f972d=NO
ops/githooks/pre-commit:16　[ -x "$PY" ] || { echo "...略過..."; exit 0; }
CLAUDE.md 首行：main=v1.35 ／ 三 worktree=v1.31 · v1.32 · v1.31
```

**為何是它，而不是別的（四條，逐條可機械覆核）**：

**(i) 它是元問題，不是並列的一項。** 現在有三個 worktree 活著，本輪四路補齊的產出全部在 worktree 內完成。每一筆 commit 完全不過五閘（治權引用／指令矩陣／假斷言／vendor 直綁／#8 AST），併回 main 後閘從未看過那些內容；而失效**完全靜默**，只印一行「略過」、rc=0。零 CI（`.github/workflows` 不存在）⇒ pre-commit 是全專案**唯一**的自動觸發點。**不先修它，其後每一項修復的驗證通道本身都不可信**——這正是優化計畫書自己的原則四「先讓紅燈會亮 ＞ 把紅燈修綠」之定義情形。

**(ii) 治權檔漂移使並行 agent 讀到已被廢止的法。** worktree 注入的 `CLAUDE.md` 是 v1.31／v1.32，**缺 #33／#34／#35**，且仍把 **#28(c)「非必要不 fan-out」載為生效條文**——而該條已被 #34 明示反向廢止。⇒ 一個在 worktree 裡工作的 agent 會依舊法自我限縮並行度，且不會知道自己讀的是舊法。本檔本身即在此環境產出（見 §8）。

**(iii) 無 Steward 前置。** S1（hook 改 fail-closed，`--git-common-dir` 解析共用 venv）／S2（新增 `check_worktree_treaty_sync.py`）／S3（順修 hook 檔頭把安裝者由 `install_services.sh` 更正為 `resume_project.sh` → `scripts/install_git_hooks.py`）皆屬 #26 執行層「改正確」。**只有 S4（#13 是否增列 worktree 條款＝M-P3）需裁，且它不阻塞 S1–S3。**

**(iv) 三個競爭者現查已不成立或可逆。**
- 優化計畫書之第一名 **P0-1 sim q_grid**：**已於 09:40:56 commit `36c69cc` 修復**（本輪親驗 `normalize_q_grid(_q_grid(...))` → `list` len=**99**）。
- 執行計畫之第一名 **W0-1/W0-2 I5B 施作**：**已於 08-02 21:04 commit `2b6350d` 落地**（live CHECK 含 `superseded`）——其「今日最緊、須回 `I5B-diff-施作`」是對已完成事項再要一次授權。
- 唯一今日真不可逆者 **M-T1（sim ledger 開列）**：現查 `sim_run_link`＝0 列、`sim_evolution_iteration_ledger`＝0 列，而首格落地後 `simlink_no_delete` 使孤兒 uid 永久化。**但**現查 `crontab -l | grep -i sim` 零命中、`systemctl --user list-unit-files | grep -i sim` 零命中、`run_arena_daily_pipeline._steps()` 六步不含 sim ⇒ **首格由人工按 `--apply`，窗是我們自己控制的，不是時鐘逼的**（見 M-T7）。故它是「今日內要做完」而非「必須第一個做」。

**證偽條件（本判斷何時失效）**：若 hugo 決定今晚就按 `--apply`，則 M-T1 升為第一（因其不可逆性此時被啟動）；若三個 worktree 今日全部收掉且不再並行，M-G1 降為 P1。

---

### 0.2 【問二】哪些可先做？（不需任何裁決／前置，即刻可動）

**共 55 項。** 全部標【可先做】，皆為 #26 執行層「改正確／補完整／接上既有判準」，零判準變更、零外部副作用、零不可逆。逐項見 §1 表之「就緒」欄；此處按車道列出：

| 車道（互斥資源） | 可先做項目 | 數 |
|---|---|---|
| **PG-HOOK**（`ops/githooks/pre-commit`） | M-G1（S1–S3，含檔頭更正） | 1 |
| **PG-AUDIT**（`scripts/reconcile_audit.py`） | M-G3 | 1 |
| **PG-EVO**（進化 driver 檔群） | M-T2 → M-G7 → M-E3（組內序列） | 3 |
| **PG-SIMEVAL**（`scripts/evaluate_sim_calibration.py`） | M-M1 → M-M2（組內序列） | 2 |
| **PG-SIMDDL**（sim 表＋ledger） | M-T1 | 1 |
| **PG-LINT**（`tools/constitution_lint/`＋`check_treaty_refs.py`） | M-L1＋M-L2 合單、M-L3（lint 部分）、M-N14 | 4 |
| **PG-KNOW**（`src/augur/knowledge/`） | M-K2 → M-G15（正名）→ M-N9（正名）（組內序列） | 3 |
| **PG-KNOW2**（`retrieval.py`／回填，與上組不同檔） | M-K1、M-K3、M-K6 | 3 |
| **PG-DOC**（文件／報告，逐檔互斥、彼此並行） | M-N4、M-N13、M-N16、M-N17、M-N18、M-L6 | 6 |
| **PG-NEWFILE**（新檔，全並行） | M-G2、M-G9、M-G11、M-G12、M-G13(探針)、M-G16(探針)、M-N1、M-N2、M-N8、M-N10、M-N11、M-N12(探針)、M-N15、M-M4、M-M5(killed/undecidable)、M-O3、M-O4、M-O5、M-O7、M-O9、M-P12(正名)、M-P13、M-W2、M-W6、M-E7、M-R3(剖析) | 26 |
| **唯讀盤點**（不改檔） | M-E2、M-T6、M-T7、M-G10(改碼部分)、M-G8(S1)、M-E1(甲)、M-T5(紀律) | 7 |

**⚠ 三個「可先做但有時間形狀」的例外**（仍不需裁決，但排序有意義）：
1. **M-T1** 應在今晚按 `--apply` 之前完成（否則成本由「開一列」變成「回填遷就已寫死的 uid」）。
2. **M-T2** 應在今晚 23:00 run 22 之前完成（否則又多一輪恆亮假告警；錯過**可逆**）。
3. **M-N1／M-N2** 建議同批（共用 schema，邊際成本近零），且**越早建基線，能觀察到的 diff 越多**。

---

### 0.3 【問三】哪些可同步做？（並行組與互斥資源）

**結論：十一個車道組間全部可並行；最大同時線數受 RAM 而非 CPU 綁定。**

**現查容量（2026-08-03 10:14，與 09:55 之量測已漂）**：

```
nproc=12 ｜ loadavg 7.55 7.47 7.56
free -m: total 11,961 / used 5,000 / available 6,960 / shared 2,085 / swap 已用(略)
llama-server RSS = 647 MB（09:55 曾量到 5,507 MB —— qwen3:8b 已退駐）
```

⚠ **口徑警告**：FILL-PARALLEL 於 09:55 量得 `available=1,509 MB` 並據此結論「重活同時最多 1 條」。**19 分鐘後現查為 6,960 MB**（llama-server 由 5,507→647 MB）。⇒ **容量是隨 Ollama 駐留狀態擺盪的量，不是常數**；任何排班前必須現查，不得引用本段數字。

**可並行上限（依現查 6,960 MB available）**：

| 層 | 定義 | 現況上限 | 若 qwen3:8b 回駐（−5.5 GB） |
|---|---|---|---|
| **重活 (i)** | 載 LLM／建 panel／pandas 掃 8.54M 列／pg_dump／全量 upsert | **2 條** | **1 條** |
| **中量 (ii)** | 單表 SQL 聚合、小批 CPU、DDL、selftest（各 ≤300 MB） | **3–4 條** | 2–3 條 |
| **輕量 (iii)** | 讀檔／lint／文字編輯／grep／git（<200 MB） | **6–8 條**（回到 12 核與 Claude 端） | 同 |

**#34「平行度預設拉滿」應拉在 (iii) 層**——PG-NEWFILE 的 26 項與 PG-DOC 的 6 項是最佳標的。硬邊界（記憶體）不因 #34 鬆動。

**七類互斥資源（現查狀態）**：

| # | 資源 | 現查 | 誰搶 | 規則 |
|---|---|---|---|---|
| R1 | **heavy_slot**（PG advisory lock） | **持有者＝無**（另有 2 筆 07-31 SIGKILL 殘帳，鎖已隨連線釋放、無實害） | 僅 `run_evolution_iteration.py:377`／`eval_local_model.py:426` 兩處 | 全機唯一。**今晚 23:00 前必須淨空** |
| R2 | **Ollama 車道**（`-np 1`） | llama-server 在（RSS 647 MB） | 取 `/tmp/augur_llm.lock`：01:30 鏈／evolve_cycle／self_seek／l2-deliberation／admission-assist；**不取鎖卻實際佔用**：`tools.project_memory_mcp index`（M-O7） | 引擎層單槽；鎖的帳與真實佔用分家 |
| R3 | **FinMind IP ＋ 限速** | 未現查配額（唯讀輪禁 API，#24／#25） | arena 20:00 日班／audit_selfheal／TRI 補抓／對帳 | ⚠ `finmind.py:59` 之 `_pace()` 用 `threading.Lock()` ＋ module-global ⇒ **限速是 in-process 的，兩進程並行則對外速率相加** |
| R4 | **DB DDL 窗** | `pg_locks WHERE NOT granted`＝0；**但 pid 217629 已 active 2 天 17:11**，持 AccessShareLock 於 4 張 knowledge 表 | M-T1／M-M3／M-N1 建表／M-P11 相關 | #30：dump 期間禁 DDL（週六 07:30，實測 dump 僅 **352 秒**）。**knowledge 四表之 DDL 須等 M-O1** |
| R5 | **hugo 的 TTY** | `steward_question_ledger` awaiting_hugo=**159**、`resolved_by='hugo'`=**0**；L2 積壓 180 件 | 全部裁決 | **定義上不可並行**；湊窗批次（§4 三窗） |
| R6 | **RAM** | available **6,960 MB**（擺盪） | 見上表 | 排班前現查，不引用本檔數字 |
| R7 | **檔案集** | #34 三項硬邊界**不含撞檔**；唯一護欄在記憶檔 `no-concurrent-agents-same-files` | 三組已識別之撞檔面 | **本檔已用工單分組規避**（見 §3.1），不必等 M-P1 裁決 |

**三組必須綁成單一工單的撞檔面**（依 #34 字面拉滿即會各拆多 agent）：
1. `scripts/evaluate_sim_calibration.py` ← M-M1 · M-M2（＋已關閉之 X1 同檔）
2. `scripts/check_treaty_refs.py` ← M-L1 · M-L2
3. `scripts/run_evolution_iteration.py` ← M-T2 · M-E4（M-E4 待裁，故今日只有 M-T2）

---

### 0.4 排序主尺（本檔選定；解決三份文件的三個「第一名」）

三份素材各用一把尺，各自產生一個第一名且無一份宣告與其他兩份的關係。**本檔選定一把主尺並明文寫出降級規則**，以免第五份文件再生第五個第一名：

```
主序（r4 §4）：  能安靜地讓錯的東西通過 ＞ 能讓對的東西被誤讀 ＞ 效能與體積
  ↑ 升級修正（優化計畫書 原則三）：位於不可壓縮鏈上者，即使主序中等亦升 P0
  ↑ 升級修正（本檔新增 原則六）：今日成本≈0、明日成本高之不可逆項，升當日
  ↓ 排程層（執行計畫 §2/§3）：「今日窗口」是排程約束，不是優先級——
     它決定「今天幾點做」，不決定「先做哪個」
```

**對三份原有第一名的重新定位**：

| 原第一名 | 出處 | 新尺下的位置 | 理由 |
|---|---|---|---|
| P0-1 sim q_grid | 優化計畫書（原則三） | **X1 已關閉** | 09:40:56 `36c69cc` 已修（親驗 list/99）。原則三本身仍有效，改由 M-T1 承接 |
| W0-1/2 I5B 施作 | 執行計畫（今日窗口） | **X2 已關閉** | 08-02 21:04 `2b6350d` 已落地。剩餘＝M-T6 觀察帳 |
| D1 worktree | r4（主序第一） | **M-G1＝最佳下一步** | 主序第一名，且現查三項證據全部成立 |

---

### 0.5 一頁總圖

```
                        ┌───────────────────────────────────────────┐
  最佳下一步 ────────►   │ M-G1  worktree 雙失效（fail-closed＋同步）  │  半日・AI・零裁決
                        └───────────────────┬───────────────────────┘
                                            │ 它使其他一切修復的驗證通道可信
   ┌────────────────────────────────────────┴───────────────────────────────────┐
   │                            四條可同時開的線（今日）                            │
   ├──────────────┬──────────────┬──────────────────┬───────────────────────────┤
   │ 線1 PG-HOOK  │ 線2 PG-EVO   │ 線3 PG-SIMDDL     │ 線4 PG-STEWARD（hugo 車道） │
   │ M-G1         │ M-T2(23:00前)│ M-T1(--apply 前)  │ M-T4(19:00前)・M-T3(23:00前)│
   └──────────────┴──────────────┴──────────────────┴───────────────────────────┘
   ＋ 線5–11 PG-NEWFILE／PG-DOC／PG-LINT／PG-AUDIT／PG-SIMEVAL／PG-KNOW／PG-OPS 全並行

   ── 今晚時窗（序列，見 §3.2）──
   19:13:56 watchdog 態三發車點 ──► 20:00 arena 全鏈 ──► 21:30 結算
        └─ M-T4 裁決點            └─ 禁 heavy／禁 API／禁重活
   ──► 22:15 evolve_cycle ──► 22:5x run22 前置快照 ──► 23:00 run 22（持 slot ≈9.5h）

   ── 三個硬期限（§5）──
   2026-10-14 併審（72 日・7 框全 [ ]・88 處/32 檔）
   2026-10-15 WM.36 無條件適用（現存量 56 檔·172 處・登錄完成 0/6・欄位級 0/98）
   ≈2026-11-04 sim K=3 齊（三格 × 21 交易日，不可壓縮）
```

**五個最貴的洞（現查覆核，全部仍成立）**：

| # | 一句話 | 現查（10:14） | 對應項 |
|---|---|---|---|
| **A** | 三 worktree 的 commit 完全不過五閘，且靜默 | venv 全 NO；hook `exit 0`；治權檔 v1.31/v1.32 vs main v1.35 | M-G1 |
| **B** | 對帳鏈**目前沒有任何活著的觸發器** | `attestation_result` 最新＝**08-01 18:43**（39h 前）；日班不帶 `--audit`；watchdog 08-02 發車後零產出 | M-G3 · M-G4 · M-G5 |
| **C** | 116 支 trigger 一句 GUC 全靜音且無痕 | `tgenabled='A'`＝**0**／全 116 支為 `'O'`；唯一角色 `augur` 為 superuser | M-G16（需裁） |
| **D** | WM.36 距硬期限 72 日、登錄完成 **0/6** | `world_concept_version` 6/6 `authoritative_binding_id` NULL；`world_channel_binding` `source_column` **0/98** | M-N1 · M-W2 · M-W3 · M-W5 |
| **E** | 異地備份層為零，而備份日誌印 ✓ | `/mnt/c/database/` **空**（total 0）；兩份 11G dump 與 DB、repo 同碟 | M-O2（部分需裁） |

---

## §1 統一編號對照表（三份文件 × 四路補齊之項目歸一）

**編號規則**：`M-<族><序>`。族＝ X 已關閉／T 今晚窗口／G 讓紅燈會亮／N 數字與口徑／L 治權 lint／W WM.36 弧／M sim 軸／E 進化引擎／K 知識層／O 維運基建／R 軸與架構／P 規則與人裁。
**就緒欄**：🟢【可先做】｜🟡【需前置：…】｜🔴【需裁：…】
**來源欄**：`P`＝優化計畫書｜`X`＝執行計畫｜`r4`＝深化理解 r4｜`F1..F4`＝四路補齊（Z／FC／U／LANE）

### 1.1 已關閉（3 項——請自後續執行集移除，勿再派工）

| 統一 ID | 標題 | 來源 | 現查裁決 |
|---|---|---|---|
| **X1** | sim evaluator q_grid 契約 | P0-1／r4 D7·C5·G4／F3 U-X1 | ✅ commit `36c69cc`（08-03 09:40:56）。親驗 `normalize_q_grid(_q_grid(...))`→`list` len=**99**。⚠ **殘餘 X1-r**：#35「退回舊版確認變紅」未由任何一輪執行 → 併入 M-G2 驗收 |
| **X2** | I5B 世代 supersede 施作 | X W0-0/1/2·Q01／r4 §7.1 | ✅ commit `2b6350d`（08-02 21:04）＋live CHECK 含 `superseded`。**執行計畫整個 W0 關鍵路徑前提不成立**；剩餘＝M-T6 |
| **X3** | RULING-2026-043 本體 | P S-2／r4 D3·C3·Q1 | 🟡 本體已建（`c9575f3`，AL-2026-047）；**簽核欄仍 `[ ]`** → 簽核＝M-P16；射程對帳＋回歸鎖＝M-L6 |

### 1.2 今晚窗口（7 項）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-T1** | sim `iteration_uid` 孤兒——首格落地前開 ledger 列＋FK | P1-12／r4 D23／F3 U08／F4 SIM-新 | 🟢【可先做】**建議升 P0**（計畫書排 09-30） | AI |
| **M-T2** | 進化引擎 `cleared_at` 謂詞（driver:433 ＋ A8:239） | P0-4／r4 D18／F3 U01 | 🟢【可先做】23:00 前 | AI |
| **M-T3** | pending 17 列人裁 vs run 22 自動 supersede 之定序 | X Q18·W1-5／r4 Q10／F3 U10 | 🔴【需裁：晉升單位＝feature 還是 (principle,feature)】23:00 前 | hugo |
| **M-T4** | 今晚 ≈19:13:56 watchdog 發車 FinMind 放量，撞 20:00 arena | F4 LANE-1（**三份素材皆無**） | 🔴【需裁：三案擇一】19:00 前 | hugo |
| **M-T5** | heavy_slot 今晚淨空紀律 | F4 LANE-2 | 🟢【可先做】（不做事即達成） | AI＋hugo |
| **M-T6** | run 22 觀察帳（I5B 首次生效點） | X W0-3/4/5·Q02／F3 U07 | 🟢【可先做】唯讀 | AI 監看＋【自動】cron |
| **M-T7** | **事實更正**：「20:00 sim 首格自動落地」不成立 | F4 SIM-事實更正 | 🟢（更正，非工項） | AI |

### 1.3 先讓紅燈會亮（16 項——本檔主序最高族）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-G1** | **worktree 雙失效**：hook fail-closed ＋ 治權檔同步 ＋ 檔頭安裝者更正 | P0-2／r4 D1·D2·C6／F2 FC-G1·FC-C6／F3 U02 | 🟢 S1–S3；🔴 S4＝M-P3 | AI／hugo |
| **M-G2** | 三支掃描器加「掃到對象數地板」（空集合＝綠燈之家族根因） | P2-4／r4 §7.4-3／F2 FC-G0 | 🟢【可先做】**單項投報最高** | AI |
| **M-G3** | `reconcile_audit.py:158` 接上 library 正解 `reconcile.verdict()` | P0-3／r4 D4·G2·G3／F2 FC-G2／F3 U03 | 🟢【可先做】 | AI |
| **M-G4** | audit watchdog **送車即死**（08-02 18:45 發車後零產出） | F1 Z9-1（**三份素材皆無**） | 🔴【需授權：改 systemd user unit】 | AI＋hugo |
| **M-G5** | 日班只跑 sync 不跑對帳——attestation 唯一觸發器已壞 | F1 Z9-3／X Q06 | 🟡【需前置：M-G3 → M-G4】＋🔴【需授權：API 面】 | AI＋hugo |
| **M-G6** | 15 條 crontab 零失敗告警（systemd 側 13 unit 全有 OnFailure） | F1 Z9-4（**三份素材皆無**） | 🟢 改期望表；🔴【需授權：`--apply`】 | AI／hugo |
| **M-G7** | 週報 R6 digest `gate_ref` 過濾使人閘路 APPLY 失明 | P0-6／r4 D15／F3 U04 | 🟢【可先做】週日 09:00 前 | AI |
| **M-G8** | `augur-knowhow-refresh --domain finance` 空轉 | P0-7／r4 D11·G5／F2 FC-G5／F3 U05 | 🟢 S1 fail-loud；🔴【需授權：改 unit】 | AI／hugo |
| **M-G9** | 92 個 dataset 零 per-dataset 新鮮度哨兵 | F1 Z8-2（**三份素材皆無**） | 🟢【可先做】 | AI |
| **M-G10** | `TaiwanStockTotalReturnIndex` 停更 **17 個交易日**，三個下游靜默失效 | F1 Z8-1（**三份素材皆無**） | 🟢 改碼＋哨兵；🔴【需授權：補抓 API】 | AI／hugo |
| **M-G11** | `test_l716_conflict_registered.py` 只鎖「檔在」不鎖「已簽」 | r4 G6／F2 FC-G6 | 🟢【可先做】 | AI |
| **M-G12** | `execute_sunset_consequence --check` 綠燈量的是它自己 | r4 G10／F2 FC-G10／X Q16 | 🟢【可先做】 | AI |
| **M-G13** | `steward_question_ledger`「待裁」名實不符＋否決可達性零量測 | r4 D25·G9／F2 FC-G9 | 🟢 探針；🔴【需裁：Q22 機器可否改 awaiting→superseded】 | AI／hugo |
| **M-G14** | `knowhow_evidence_weight` 100% high——閘已補、消費側未補 | r4 G11／F2 FC-G11 | 🟢【可先做】 | AI |
| **M-G15** | KH1「既有原文＝視同通過」旁路（100% 通過率之結構根因） | r4 G12／F2 FC-G12 | 🟢 正名＋分流探針；🔴【需裁：旁路存廢】 | AI／hugo |
| **M-G16** | 116 支 trigger 全 origin-mode——一句 GUC 全靜音且事後無痕 | P3-4／r4 D6·G8·T9·Q7／F2 FC-G8 | 🟢 探針；🔴【需裁：`ENABLE ALWAYS` 算不算升嚴】 | AI／hugo |

### 1.4 數字與口徑（18 項）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-N1** | **「條文 ↔ live 探針」綁定表**（含 10-14 全 13 項機械覆蓋） | P0-5 S1／r4 §7.4-2·§6.4／F1 Z7-4／F2 FC-T0 | 🟢【可先做】**過期族唯一槓桿** | AI |
| **M-N2** | 度量登錄表 `measure_registry`（「引用數字必附口徑」之機械載體） | r4 §3.4·§7.4-1／F2 FC-N1 | 🟢【可先做】**建議與 M-N1 同批**（共用 schema） | AI／hugo(authoritative) |
| **M-N3** | `CLAUDE.md:127`「137/137」→ 探針綁定（live **467/467**） | r4 D40·§3.2／F2 FC-T1 | 🔴【需裁：改治權檔文字，依 #19 逐段呈】 | AI 草擬／hugo |
| **M-N4** | `HANDOFF.md` 三處硬編數字（12 條 cron → live **15**） | r4 D40／F1 Z10-2／F2 FC-T2 | 🟢【可先做】 | AI |
| **M-N5** | `GROUNDING-MAP.md:45-47` 三列綁定（Registry「零跡象」／直綁 37 檔） | P2-10／r4 D40·§3.2／F2 FC-T3 | 🟡【需前置：M-N7 定尺】 | AI |
| **M-N6** | `RULING-2026-042 §二2` 閘位數字已反向——正文不得改，改附滾動快照 | r4 Q9·§3.2／F2 FC-T4 | 🔴【需裁：以哪份為 L7.16 認定基礎】 | AI 備卷／hugo |
| **M-N7** | vendor 直綁**四把尺** → 定權威尺（唯一綁硬期限者） | r4 §3.4·Q25／P3-5／F2 FC-N2 | 🔴【需裁：權威尺選定＝清償配額之輸入】 | AI 呈案／hugo |
| **M-N8** | script 支數（**327**／**467**）與 public 表數（**334**／335）正名 | r4 §3.4／F2 FC-N3 | 🟢【可先做】 | AI |
| **M-N9** | KH0 破口兩把尺（未評 138,875 ／ 無原文 138,826，差 49） | r4 §3.4·D10·Q6／P3-2／F2 FC-N4 | 🟢 雙報正名；🔴【需裁：Q6 KH0 對無原文之通過條件】 | AI／hugo |
| **M-N10** | 閘表分層**四把尺**不可相減＋12 張裸 UPDATE 之設計性例外 | r4 §3.4·T8·Q8／F2 FC-N5 | 🟢 登錄；🔴【需裁：例外確認】 | AI／hugo |
| **M-N11** | `sent_no_emb` 多把尺 → 定 embed-catchup 之可判收斂條件 | r4 §3.4／F2 FC-N6 | 🟢【可先做】 | AI |
| **M-N12** | `dual_green_n` 名實不符——今晚 run 22 起有實質倒數 | r4 §3.4·T11·T12·Q12／F2 FC-N7 | 🟢 雙報探針；🔴【需裁：Q12 什麼算進步】 | AI／hugo |
| **M-N13** | F2 備料報告「Registry NONE／直綁 47 檔」加時戳與現值對照 | r4 §3.2／F2 FC-T5 | 🟢【可先做】追加式，不改正文 | AI |
| **M-N14** | `tools/constitution_lint/github-workflow.yml` 檔頭阻斷理由已過期 | r4 §3.2／P §5／F2 FC-T6 | 🟢【可先做】 | AI |
| **M-N15** | `MEMORY.md` 索引稽核器（1 孤兒／3 截短名／3 則自稱⭐權威）＋PG 設定漂移 | P2-2／r4 D32／F2 FC-T7／F4 DRIFT-1 | 🟢 稽核器＋數字修正；🔴【需裁：「同時點只能一則現況權威」＝新判準】 | AI／hugo |
| **M-N16** | r0–r3 報告加機讀 `superseded_by` 標頭（九則已被 live 推翻） | r4 §3.2／F2 FC-T8 | 🟢【可先做】 | AI |
| **M-N17** | `reports/` **301** ＋ `audits/` **200** 檔無狀態欄、無索引、無取代鏈 | F1 Z10-1（**三份素材皆無**） | 🟢 慣例＋稽核器＋索引；存量補標見 §8 | AI |
| **M-N18** | `verify_code_reports.py:16` ROOT 硬編絕對路徑（worktree 掃到 main） | F1 Z10-3 | 🟢【可先做】**應先於 M-N17**（它是 M-N17 的設計約束） | AI |

### 1.5 治權層 lint 與自我一致性（8 項）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-L1** | CS 版本自我一致性 lint ＋ `constitution_lint` corpus 擴射程 | P1-3／r4 D13·D14·G7／F2 FC-G7 | 🟢 (a)CS 三方比對＋(b)corpus；🔴 (c)掛第六閘＝M-L7 | AI／hugo |
| **M-L2** | 大憲章修訂表**雙現行**（`**ACTIVE**` 1 列＋`**現行**` 1 列） | P1-4／r4 C2／F2 FC-C2 | 🟢 lint＋降級腳本；🔴【需裁：改正文，依 #19】 | AI／hugo |
| **M-L3** | 條號前綴 lint ＋清償 14 例 | P2-1 | 🟢 lint；🔴【需裁：逐處補前綴＝改治權檔文字】 | AI／hugo |
| **M-L4** | CS-系統核心思想同檔對「有無待裁事項」給兩個相反答案 | r4 C1·Q5／F2 FC-C1 | 🔴【需裁：Q5 該 open-tension 仍未裁還是已吸收】 | AI 呈案／hugo |
| **M-L5** | MC §0.5 Layer 4 規格名不符（Knowledge **Graph** vs 生效本 **System**）＋specs draft 並存 | r4 C4／F2 FC-C4 | 🔴【需裁：改元憲章文字，§8.1 專屬 Steward】 | AI 呈案／hugo |
| **M-L6** | RULING-2026-043 射程對帳（17 處／6 檔）＋「碼內裁決號 ⊆ 實存裁決檔」回歸鎖 | r4 D3 殘餘／F2 FC-C3 | 🟢【可先做】 | AI |
| **M-L7** | `constitution_lint --selftest` 之 G10 界線 FAIL（291 條斷言零自動觸發） | P S-1／r4 D12·Q4·T2 | 🔴【需裁：DRAFT 標記之效力界線】 | hugo |
| **M-L8** | `evolution_iteration_ledger` 並存兩條互相包含的 axis CHECK | r4 C7／F2 FC-C7 | 🔴【需裁：DROP CONSTRAINT 屬破壞性＋三軸共用表之架構判準】 | AI 呈案／hugo |

### 1.6 WM.36 合規弧（6 項——唯一綁外部硬期限）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-W1** | 探針表建立與 10-14 全 13 項登錄 | P0-5 S1／F1 Z7-4 | 🟢（**已併入 M-N1**，不另計） | AI |
| **M-W2** | 欄位級映射（`source_column` **0/98**）之單位成本抽樣 | P0-5 S3 之前置／F1 Z7-3 | 🟢【可先做】**唯讀抽樣，把唯一未估項變可排程** | AI |
| **M-W3** | M3 絞殺驗收判準**結構上不可達**——新路 SQL 解析後仍是 vendor 表名 | F1 Z7-1（**三份素材皆無**） | 🔴【需裁：權威表徵本身即 vendor 表時，解除直綁之判準】 | AI 呈案／hugo |
| **M-W4** | 7 張多值表：登錄後消費端仍須內嵌列篩選字面（`stock_id='TAIEX'`／`'TXO'`） | F1 Z7-2（**三份素材皆無**） | 🔴【需裁：WM.36「series 識別碼」是否含表內列鍵】 | AI 盤點／hugo |
| **M-W5** | 98 通道欄位展開 ＋ 權威採認（`authoritative_binding_id`／`decided_by` 落值） | P0-5 S3/S4 | 🟡【需前置：M-W2 抽樣 → M-W3·M-W4 裁定粒度】＋🔴【hugo 親跑，AI 不代打】 | AI 備料／hugo |
| **M-W6** | vendor／矩陣閘擴口徑（`tests/`／`tools/`／`ops/`／`augur_proxy/`／repo 根） | P2-5 | 🟢【可先做】 | AI |

### 1.7 sim 軸（5 項；另見 M-T1）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-M1** | sim `--apply` 只擋 K、不擋 `n_valid`（既有 `is_invalid` 欄零使用） | P1-8 | 🟢【可先做】 | AI |
| **M-M2** | evaluator 之 kill switch 未吃 `env_halt`（唯一 fail-open 的一支） | P1-6／r4 D34（**已更正**）／F3 U09 | 🟢【可先做】 | AI |
| **M-M3** | sim 三張證據表無 UPDATE 閘（0 列表、零 code 改動、次秒級 DDL） | P1-7／r4 D16／F4 SIM-並行 | 🔴【需裁：M-P11 帳本表射程】 | AI 實作／hugo 圈選 |
| **M-M4** | sim 時鐘無提醒機制（settle／evaluate 未入 runbook） | P1-10 | 🟢【可先做】掛既有週日 09:00 | AI |
| **M-M5** | W4 判決工具不存在＝證據鏈終點懸空 | P1-11／r4 D24 | 🟢 killed／undecidable 兩路徑；🔴 promoted 路徑 | AI／hugo |

### 1.8 進化引擎（7 項；另見 M-T2·M-T3·M-T6）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-E1** | `gate_cache` 方向鍵：用**反方向**證據判 validated（現查 run21 仍 **4 列**） | P1-9／r4 D8·Q11／F3 U13 | 🟢 (甲)加方向鍵；🔴 (乙)不符即 FAIL_SIGN＝新判準 | AI／hugo |
| **M-E2** | prodset 可溯源鏈斷點（`apply_log_id=24` 指向 queue 311） | r4 D17（**兩份計畫皆漏**）／F3 U14 | 🟢 唯讀全量對帳可先做；改指見 §8 未估 | AI |
| **M-E3** | evolution ledger 11 欄全零寫入；**`apply_allowed` 恆 false** | P2-9／r4 D36 | 🟢【可先做】 | AI |
| **M-E4** | `gate_scale` 指紋只認 `min_abs_hac_t`（靜默換尺） | P3-1／r4 D30·Q16 | 🔴【需裁：「什麼算可比」＝判準】 | AI 呈案／hugo |
| **M-E5** | 整批路完全不受武裝閘約束（`queue_id=None` → 直接 return True） | r4 D9·Q18／P S-8(a) | 🔴【需裁：授權邊界；現查該路徑一句即 `applied=17`】 | hugo |
| **M-E6** | RAWEVO gain 恆為真且以 `basis='new_gap'` 繞過對照臂 | r4 D31·Q13（**兩份計畫皆漏行動項**） | 🔴【需裁：gain 語意是否為原意】 | AI 呈案／hugo |
| **M-E7** | `eval_code_hash` ＝整檔位元組 sha（兩個方向都失真） | r4 D38（**兩份計畫皆漏**） | 🟢【可先做】誠實正名 | AI |

### 1.9 知識層（8 項）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-K1** | `retrieval.py:408` 死碼＋advisor 每檢索 ≈1.3s 浪費 | P1-1／r4 T20 | 🟢【可先做】⚠ 改後須 `systemctl restart augur-advisor augur-chat`（#7） | AI |
| **M-K2** | `prior_depth` 是自我背書的 pass（142,441 件） | P1-2／r4 D19 | 🟢【可先做】零行為變更 | AI |
| **M-K3** | D1 回填自動化（每日漏 21 件、零排程） | P2-11／r4 D20 部分 | 🟢【可先做】 | AI |
| **M-K4** | `knowhow_auto_admit_run` **508,926 列／556 MB** 帳本止血 | P2-8／r4 D28·Q28／P S-7 | 🔴【需裁：留痕義務範圍】＋🟡【需前置：M-O1】 | AI／hugo |
| **M-K5** | KH7 仍是庫級放行（6 列 probe 撐 145,952 件 depth 7） | r4 D29·Q14（**兩份計畫皆漏**） | 🔴【需裁：逐 item 還是庫級前提】 | AI 呈案／hugo |
| **M-K6** | `knowledge_access_audit` 名不副實（66 列、最後 07-06、檢索路徑零寫入） | r4 D37（**兩份計畫皆漏**） | 🟢 誠實正名；🔴【需裁：是否補真軌跡】 | AI／hugo |
| **M-K7** | 全文管線只完成誠實標記、未完成推進（121,389 unattempted、零排程） | r4 D20·Q24／X W2-5 | 🔴【需裁：外部 API 放量節奏】 | hugo |
| **M-K8** | `knowledge_domain_map` 是否納 `erp_tiptop`（唯一 100% 可答語料恆 pending） | P S-9／r4 Q15 | 🔴【需裁：納新域＝人拍板，AI 不得自行 INSERT】 | hugo |

### 1.10 維運與基建（11 項）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-O1** | runaway psql backend **pid 217629**（active **2 天 17:11**，持 4 張 knowledge 表 AccessShareLock） | F4 LANE-0（**三份素材皆無**） | 🔴【需裁：`pg_terminate_backend` 屬 #6 破壞性】**knowledge 車道之上游阻斷器** | hugo |
| **M-O2** | 異地備份層為零 ＋ 鏡像步驟印「✓ 完成」卻無事後驗證 | X Q08／r4 D27·Q26／F1 Z9-2／F3 U11／F4 OPS | 🟢 鏡像驗證＋哨兵；🔴【需裁：異裝置選型】 | AI／hugo |
| **M-O3** | `sync_memory.py export` 無密碼掃描（79 檔全量推 public repo） | P2-3／r4 D33 | 🟢【可先做】**不可逆風險** | AI |
| **M-O4** | **288** 支含 selftest 之檔僅 3 支在排程；**26** 支 pytest 零排程 | P2-6／r4 D35 | 🟢【可先做】掛既有週一 08:40 | AI |
| **M-O5** | 隔離閘字面面補三包（`augur.arena`／`execution`／`deliberation`） | P2-7 | 🟢【可先做】 | AI |
| **M-O6** | 01:30 演化鏈與 TWEVO I3 用**兩把不同的鎖**，每個週間夜必然同時跑 | F4 LANE-3（**三份素材皆無**） | 🔴【需裁：改自動鏈編排觸 #26 OCV 四項對照聲明】 | AI 量化／hugo |
| **M-O7** | `project_memory index` 用 Ollama 但不入 LLM 單槽鎖 | F4 LANE-5 | 🟢【可先做】wrapper 一行 | AI |
| **M-O8** | 週一 08:00 維運 cron 呼叫的 `/usr/local/bin/ollama` 不存在，每週靜默失敗 | F4 DRIFT-2 | 🟢 改期望表；🔴【需授權：`--apply`】 | AI／hugo |
| **M-O9** | 並行容量哨兵（nproc／loadavg／available／llama RSS／heavy_slot 持有者） | F4 LANE-4 | 🟢【可先做】掛既有週日 09:00 | AI |
| **M-O10** | DESKTOP 並行機／跨庫 drift | X Q20 | 🔴【需裁：週末機會窗】 | hugo |
| **M-O11** | `augur_sandbox` 庫之治權定位未定（34 MB／14 表／17 處引用） | r4 D39·Q27（**兩份計畫皆漏**） | 🔴【需裁：是否受表級不變式約束／是否納備份】 | hugo |

### 1.11 軸與架構（8 項）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-R1** | `direction_gate` 無 pass（現查 **0/29**）；cluster 60 vs 250；own_stack h 錯配 | X Q04（**優化計畫書＋r4 §4 皆無**） | 🔴【需裁：降門／supersede own_stack／維持 250】 | hugo |
| **M-R2** | LAIEVO **0 輪**（`local_ai_iteration_ledger`＝0 列）＋robot 過地板 | X Q05（**同上**） | 🔴【需裁：新凍結集＋換尺】 | hugo |
| **M-R3** | heavy_slot／I3 過慢（645–720 s/feature，一輪 ≈9.5h） | X Q13 | 🟢 剖析可先做；改法另案 | AI |
| **M-R4** | I6 未接 `train_ranker`（晉升不進熱路徑） | X Q14 | 🔴【需裁：明示授權】 | hugo |
| **M-R5** | `path_gate`「一條路」未收斂（六門平行債） | X Q15／記憶 `augur-path-six-parallel-gap` | 🔴【需 #20 另立計畫書：觸 ≥3 package】 | hugo→AI |
| **M-R6** | SUNSET consequence 封存腳本缺 | X Q16 | 🟢（**已併入 M-G12**） | AI |
| **M-R7** | PME-XDOM-SOLAR 等 APPLY（無雙綠＋無碼硬促） | X Q17 | 🔴【需裁：另句 `PME-APPLY-go`∧雙綠】 | hugo |
| **M-R8** | TWEVO close 判準（重試成功仍記 failed，產能帳失真） | X Q09 | 🔴【需裁：雙欄 vs 洗敗】 | AI 呈案／hugo |

### 1.12 規則層與人裁（16 項）

| ID | 標題 | 來源 | 就緒 | 執行者 |
|---|---|---|---|---|
| **M-P1** | #34 是否增列第 (iv) 項硬邊界「並行以檔案集不重疊為前提」 | P S-4／r4 D22·Q19／F4 PARALLEL-護欄 | 🔴【需裁：涉 AI 自身監督機制，AI 不得為核准主體】 | hugo |
| **M-P2** | 三則記憶級規則升格入 CLAUDE.md（人簽不代打／git add 逐檔／pgrep 正法） | P3-3／r4 D21·Q20 | 🔴【需裁：同上】 | hugo |
| **M-P3** | worktree 是否為 #13 允許之工作場所 | P S-3 | 🔴【需裁：三項減損屬 OCV 單向棘輪】 | hugo |
| **M-P4** | `guard-mechanisms` 型 6／型 7 是否入憲 | r4 Q21 | 🔴【需裁】 | hugo |
| **M-P5** | 領域治權檔升版是否須登錄 `constitution/AMENDMENT-LOG.md` | r4 Q2 | 🔴【需裁：現為分裂雙帳簿】 | hugo |
| **M-P6** | 模擬方法自進化專章 v1.0 是否為 MC §0.5 意義下之「規格」 | r4 Q3 | 🔴【需裁】 | hugo |
| **M-P7** | 機器規則可否把 `awaiting_hugo` 改成 `superseded` | r4 Q22 | 🔴【需裁：直落 P5.W2／OCV C 分量】 | hugo |
| **M-P8** | 單一角色整併是否為「閘的強度」局部回退 | r4 Q23 | 🔴【需裁：不可逆、跨治權檔；AI 不得提案回退已結案架構決定】 | hugo |
| **M-P9** | 2026-07-25 `promoted_by='hugo'` 代打是否構成 GOV-3 B 之新 Evidence | r4 Q30 | 🔴【需裁：10-14 checklist 第 7 項即問此事】 | hugo |
| **M-P10** | 5 條 manual `validation_evidence` 於 10-09／10-10 到期後之處置 | P S-5／r4 Q29 | 🔴【需裁：到期距併審僅 4 日，宜先裁】 | hugo |
| **M-P11** | 「帳本表不掛 honesty trigger」之射程（30 張零 trigger 治權味表） | P S-6／r4 Q8 | 🔴【需裁：一裁解鎖 M-M3＋M-P12＋M-N1 新表三項】 | hugo |
| **M-P12** | `validation_evidence` 三條 red 無處置時鐘；**2 條 manual 從未被檢驗**卻計入 green | F1 Z8-3／P S-5 | 🟢 (a)正名 (b)時鐘；🔴 (c)E2/E4 處置＝M-P10 | AI／hugo |
| **M-P13** | sim／arena 兩軸在綠燈帳本上**零覆蓋** | F1 Z8-4 | 🟢【可先做】 | AI |
| **M-P14** | 是否接上 I1/I2 讓 `dual_green_n` 有成長來源 | P S-8(b) | 🔴【需裁：新特徵入生產須走提拔關卡＋經濟終關】 | hugo |
| **M-P15** | 「同一時點只能有一則現況權威」是否入規則 | F1 Z10-1／P2-2 | 🔴【需裁：新判準】 | hugo |
| **M-P16** | RULING-2026-043 簽核欄仍 `[ ]` | X3 殘餘 | 🔴【需裁：hugo 親簽，AI 不得代簽】 | hugo |

---

**統計（現查 `grep -oE 'M-[TGNLWMEKORP][0-9]+' | sort -u | wc -l`）**：**110** 個 `M-*` 統一編號 ＋ **3** 個已關閉 `X*` ＝ **113**。
族別分布：N **18**｜G **16**｜P **16**｜O **11**｜K **8**｜L **8**｜R **8**｜E **7**｜T **7**｜W **6**｜M **5**。
就緒分布（**分階段項目按其 AI 可為之首階段計入 🟢，其後續裁決另計入 🔴，故兩欄有重疊、不可相加**）：🟢【可先做】**55**｜🟡【需前置】**5**｜🔴【需裁／需授權】**36 個獨立裁決節點**（§4 去重後）。
其中 M-W1（併入 M-N1）與 M-R6（併入 M-G12）為交叉引用之併入項，不另派工。

**四路補齊之新發現（三份素材皆無，共 15 項）**：M-G4 · M-G6 · M-G9 · M-G10 · M-N17 · M-N18 · M-O1 · M-O6 · M-O7 · M-O9 · M-W3 · M-W4 · M-T4 · M-P12 · M-P13。
**兩份計畫皆漏而 r4 有（7 項）**：M-E2 · M-E6 · M-E7 · M-G13 · M-K5 · M-K6 · M-O11。
**執行計畫獨有而優化計畫書漏（9 項）**：M-O2（最重要）· M-R1 · M-R2 · M-R3 · M-R4 · M-R5 · M-R7 · M-R8 · M-O10。
**結構性成因**：優化計畫書 §0.4 自陳射程限 Z1–Z6（漏維運／軸／吞吐／架構）；執行計畫血緣為 07-31 五軸夜計畫（漏閘體系／治權層自我一致性／知識層假綠）。**兩份是互補的兩個半圓，任一單獨採用都有系統性盲區。**

---

## §2 逐步執行序（第 1 步 … 第 33 步）

> **讀法**：步序＝建議執行順序，**不等於必須序列**——「可並行」欄明列哪些步可同時開。凡步與步之間有硬依賴者，於「前置」欄逐字寫出。
> **驗收欄一律機械可判**（SQL／指令＋期望值）。凡新增檢查一律要求 **先驗紅**（CLAUDE #35：退回壞版必須變紅才算有鑑別力）——**全綠即視為未通過**。
> **今日基線值**已在各步驗收欄內以粗體標出，供改動後對照。

### 階段 0 — 今日（2026-08-03）：不可逆窗口與元問題

---

**第 1 步｜M-G1　worktree 雙失效 → fail-closed**　🟢【可先做】
- **做什麼**：(a) `ops/githooks/pre-commit` 之 `ROOT` 改由 `git rev-parse --git-common-dir` 推導（親驗 worktree 內回 `/home/hugo/project/augur/.git`，其 dirname/venv/bin/python 存在）；(b) `[ -x "$PY" ] || exit 0` 改為 `exit 1`（fail-closed）；(c) 檔頭 `:13` 之安裝者由 `install_services.sh` 更正為 `resume_project.sh:53-54` → `scripts/install_git_hooks.py --apply`；(d) 新增 `scripts/check_worktree_treaty_sync.py`（含指令矩陣＋`--selftest`，#18／#29(d)）。
- **誰**：AI
- **前置**：無
- **驗收**：① 在 worktree 內放一支缺指令矩陣之新 script，`bash ops/githooks/pre-commit` 須 **rc≠0**（現況 rc=0＋印「略過」）；② 移除主 repo venv 可執行位 → rc=1 而非 0（**先驗紅**）；③ 正常情形 worktree 內 stdout 逐一印出五閘名稱；④ `check_worktree_treaty_sync.py --check` 現況 **rc≠0**（三 worktree 皆落後：v1.31／v1.32／v1.31 vs main **v1.35**），同步後 rc=0；⑤ 回歸鎖斷言「hook 檔頭提到的安裝者腳本中須真的出現 `install_git_hooks` 呼叫」——改前必 FAIL（`grep -c hook install_services.sh`＝**0**）。
- **⚠ 取 rc 一律重導向到檔或用 `${PIPESTATUS[0]}`**（r4 T1：rc 會被 pipe 吃掉）。
- **可並行**：與第 2–9 步全部並行（檔案集＝`ops/githooks/`＋一支新 script，與任何其他步不重疊）。

---

**第 2 步｜M-T1　sim ledger 開列 ＋ FK**　🟢【可先做】｜**今晚 `--apply` 之前**
- **做什麼**：於 `sim_evolution_iteration_ledger` 開一列 `iteration_uid='sim-<anchor>-r01'`（planned 狀態）＋`gain_basis`（CHECK 限 `calibration_delta`／`none`／`incomparable`）；把 writer 端 planned→running→終態接上；對 `sim_run_link.iteration_uid` 加 FK 指向 ledger。
- **誰**：AI（**凡欄位為 `decided_by`／`approved_by` 者留空待 hugo 親跑，不代打**）
- **前置**：無。⚠ **但 FK 之 DDL 須避開 #30 dump 窗**（週六 07:30，實測 dump 僅 352 秒）；建議與第 12 步之 DDL 批次同窗。
- **為何今日**：現查 `sim_run_link`＝**0 列**、`sim_evolution_iteration_ledger`＝**0 列**；`run_sim_calibration_cell.py:222` 產 `iteration_uid` 並於 `:247/:273` 寫入 `sim_run_link`，而該表有 `simlink_no_delete` trigger ⇒ **首格 52 列一落地，孤兒 uid 永久不可刪**，事後只能補寫回填式 ledger（形同追溯粉飾）或永遠加不上 FK。今日開列成本≈0。
- **驗收**：`SELECT count(*) FROM sim_run_link l LEFT JOIN sim_evolution_iteration_ledger g USING(iteration_uid) WHERE g.iteration_uid IS NULL` → **0**。⚠ **現況兩表皆 0 列故 trivially 0——此判準須在首格落地後重跑才有鑑別力**；另加負測：刻意 INSERT 一列 uid 不存在之 `sim_run_link` 須被 FK 拒。
- **可並行**：與第 1、3–9 步全部並行（PG-SIMDDL，獨立檔案集與表）。

---

**第 3 步｜M-T2 → M-G7 → M-E3　進化 driver 檔群（組內序列）**　🟢【可先做】｜**今晚 23:00 之前**
- **做什麼**：
  - **M-T2**：`run_evolution_iteration.py:433` 之裸 `SELECT count(*) FROM evolution_deferred_work` 加 `WHERE cleared_at IS NULL`；`verify_evolution_acceptance.py:239` 同補，且 A8 判式由「0→N/A，否則 PASS」改為對照 rc=75 事件數。正確寫法可抄 `scripts/drain_deferred_work.py:113`（#12 同一住所）。
  - **M-G7**：`report_triple_evolution_week.py:347` 之 `WHERE a.evidence_json->>'gate_ref'='V2-AUTOADVANCE'` 去除，改為以 `gate_ref` 分欄。
  - **M-E3**：ledger 11 個全零寫入欄補寫，尤其 `apply_allowed`（driver `:282` 硬寫 false 且全檔無處改 true）。
- **誰**：AI（單一執行者，三項同批做完——**M-T2 與 M-E4 撞同一支檔，但 M-E4 待裁故今日不衝突**）
- **前置**：無
- **驗收**：① driver 印「積壓 **0** 列」（現印 **9**；live `uncleared/total`＝**0/9**）；② fixture 塞一列 `cleared_at` 非空 → 計數不變，退回舊碼 → 計數 +1（**先驗紅**）；③ A8 對「有 rc=75 事件但 deferred 無未清列」之 fixture → **FAIL**（現況結構上必 PASS）；④ digest 之 7 日筆數 == `SELECT count(*) FROM evolution_apply_log WHERE applied_at>now()-interval '7 days'`（**現查 23**，digest 現顯 20），且出現 `TWEVO-APPLY-go` 與 `HUMAN-PROMOTION` 分組。
- **⚠ M-T2 之 S3（A8 判式改對照 rc=75 事件數）未估**——須先定「rc=75 事件數」自 `steps_json` 之取得口徑；可延至第 14 步。
- **可並行**：與第 1、2、4–9 步全部並行。**組內三項須序列**（同一檔群）。

---

**第 4 步｜M-T4　今晚 ≈19:13:56 watchdog 發車撞 20:00 arena**　🔴【需裁】｜**19:00 前**
- **做什麼**：呈三案，由 hugo 選一。**現查三個判定值（10:14）**：`/tmp/augur_audit_dispatch.ts` mtime＝**2026-08-02 18:45:56**（`COOLOFF_H=24` ⇒ 08-03 18:45:56 到期）；`attestation_result` 最新 PASS＝**2026-08-01 18:43**（39 小時前，`fresh_pass=0`）；`augur-audit-watchdog.timer` 現查 LAST＝**10:13:56**、NEXT＝**10:43:56** ⇒ 打點落在每小時 `:13:56`／`:43:56`，**第一個 tsage≥24h 的打點＝19:13:56**。
- **機制**：屆時執行 `audit_selfheal.sh`，以 `FINMIND_MIN_INTERVAL=0.7`（**低於已驗證安全值 0.9**）跑 `daily_maintenance --audit-days 14 --audit-all --heal`，牆鐘 6 小時 ⇒ 19:13→最晚 01:13，與 20:00 arena 之 `daily_maintenance --end <date>` 重疊。`finmind.py:59` 之 `_pace_lock` 為 `threading.Lock()`＋module-global ⇒ **限速 in-process，兩進程對外速率相加**（≈2.5 req/s vs 單流安全值 ≈1.1）。同檔 `:42` 已記「2026-06-20 單流 0.7s 就把時錶衝到 5850–5998」。
- **三案**：(甲) 19:00 前手動跑一次 audit 讓 `fresh_pass≥1`，watchdog 走態一不發車——但這本身即 API 放量，只是挪到白天且不重疊；(乙) 19:00 前 `touch /tmp/augur_audit_dispatch.ts` 延後冷卻 24h——零 API、最小干預，但屬繞過看門狗設計；(丙) 不干預，20:00 後緊盯 arena log，見 403 即停（#24）。
- **誰**：hugo（裁決）／AI（19:00 前重跑三個判定值供裁）
- **前置**：無
- **驗收（觀測）**：20:00–22:30 之 `~/logs/arena_pipeline.log` 無 403／無 FinMindError；`SELECT max(date) FROM "TaiwanStockPriceAdj"` 於 22:30 前 ≥ 2026-08-03（**現查 max＝2026-07-31**）。若採乙案：19:00 後 `stat -c %Y /tmp/augur_audit_dispatch.ts` 大於今日 18:45 之 epoch。
- **連鎖後果（若撞車）**：arena sync 掛 → 08-03 收盤不入庫 → sim anchor 不實現 → 首格滑到週二 → **21 交易日時鐘整體平移一天（不可回收）**。
- **可並行**：屬 hugo 車道，與全部 AI 車道並行。**AI 不代選**——(乙) 觸碰監督機制之計時器，(甲)(丙) 觸 API 放量。

---

**第 5 步｜M-T3　pending 17 列人裁 vs run 22 自動 supersede 之定序**　🔴【需裁】｜**23:00 前**
- **做什麼**：`_supersede_stale_pending` 之謂詞為 `queue_status='pending_auto' AND feature=%s AND run_id < %s`——**不分 action**。⇒ 今晚 run 22 只要重新產出同 feature 之列，現查 **17 列 pending_auto**（16 筆 FAIL_SIGN demote 涵蓋 10 feature ＋ 1 筆孤兒 promote q555，合計 **11 個相異 feature**）**會在人裁窗開啟前先被標 superseded、queue_id 全部換號**。
- **裁點**：r4 Q10「晉升單位是 feature 還是 (principle, feature)」；且「今晚是否先開人裁窗消化 17 列」須在 23:00 前定。
- **誰**：hugo（裁決＋TTY 親跑，`decided_by` 不代打）／AI（17 列逐列 `gate_json` 摘要備料，≤1h）
- **前置**：無
- **驗收**：任一為真即算收斂——(a) 23:00 前 17 列已由 hugo 逐顆處置；或 (b) Steward 明示接受「run 22 自動 supersede 後於新世代重新產列」並留痕於 `audits/`。**驗收後**：`SELECT count(*) FROM promotion_queue WHERE queue_status='superseded'`（**現查 0**）於 run 22 後 > 0。
- **可並行**：hugo 車道，與全部 AI 車道並行。**三份素材無一完整寫出此衝突**：exec W1-5 把人裁排在 W0 之後、r4 Q10 只抓到 q555 一顆、優化計畫書完全未列。

---

**第 6 步｜M-T5　heavy_slot 今晚淨空紀律**　🟢【可先做】（不做事即達成）
- **做什麼**：今日 20:00 起**不跑** `run_evolution_iteration.py`、**不跑** `eval_local_model.py`（全 repo 僅此二處取 `augur_evolution_heavy_slot`）。現查持有者＝**無**（另有 2 筆 07-31 SIGKILL 殘帳，鎖已隨連線釋放、無實害）。
- **實證**：run 20 持鎖 09:52:14、run 21 持鎖 09:30:34 ⇒ 一輪 ≈**9.5 小時**；cron 給 TWEVO `--slot-wait 10800`（3 小時有界等待）。`~/logs/twevo.log` 記錄 07-31 23:00 那次等滿 10800s 後於 08-01 02:00:01 印「⚠ 重活單槽被佔用 → 已寫 evolution_deferred_work；rc=75」，因 run 20 於 18:19 手動起跑持鎖到 04:11。
- **⚠ 潛在索求者**：`augur-drain-deferred.timer` 每 30 分（現查 NEXT 10:16:56）跑 `drain_deferred_work.py --apply --limit 1`，rerun 白名單含 `(tw, run_evolution_iteration)`；現查積壓 **0 列**故今晚起跑前無風險，但 run 22 若 rc=75 就會啟動這條。
- **誰**：AI（自我約束）＋hugo（不手動起 TWEVO／lai 臂）
- **前置**：無
- **驗收**：23:05 時 `venv/bin/python -m augur.core.heavy_slot` 印「持有中 = tw_iteration」；隔晨 `SELECT status FROM evolution_run ORDER BY run_id DESC LIMIT 1` = `succeeded`（非 failed／無 rc=75 defer 新列）。
- **可並行**：純紀律，與所有輕量步並行；**與任何重活互斥**。

---

**第 7 步｜M-T7　事實更正：首格不是 20:00 自動落地**　🟢
- **做什麼**：把「今晚 20:00 cron … 首格 52 列落地」自後續文件與心智模型移除。**三處親驗**：`crontab -l | grep -i sim` 零命中；`systemctl --user list-unit-files | grep -i sim` 零命中；`run_arena_daily_pipeline._steps()` 六步（daily_maintenance／sync_macro／derive_market_iv／build_market_direction_features／build_daily_direction_features／run_arena_round）**不含** `run_sim_calibration_cell`；`ops/RUNBOOK-20260803-night.md` 逐字寫「sim 首格產 run（S-4 人工逐次觸發；**勿排程**）」。
- **實務結論**：20:00 讀為「anchor 檢查點」、`--apply` 讀為「窗關閉動作」。`run_sim_calibration_cell.py --dry-run` 在 anchor 未到時 **0.79 秒**即誠實印「anchor 未實現……無事可產」⇒ **輪詢成本近零、可安全反覆確認**（單次人工呼叫，非阻塞迴圈，不違 #33）。
- **誰**：AI（更正）／hugo（按 `--apply`）
- **驗收**：`--apply` 之後 `SELECT count(*) FROM sim_run_link`＝52 且 `SELECT count(*) FROM mc_simulation_run`＝**592**（現查 **540** + 52）；再跑一次 `--apply` 為 0 新增（冪等證明）。
- **`--apply` 之前置**：第 2 步（M-T1 ledger 列已開）＋ 第 11 步（M-M1／M-M2 驗收綠）。

---

**第 8 步｜M-T6　run 22 觀察帳**　🟢【可先做】唯讀
- **做什麼**：22:5x 產前置快照（`\copy` 到 `audits/prerun22_pending_snapshot_20260803.csv`，現查基線＝pending_auto **17 列全屬 run 21**、superseded **0 列**、max run_id **21**）；23:00 起監看；隔晨收尾唯讀 SQL 落 `audits/OPT-W0-RUN22-20260803.md`。**勿手動搶 heavy slot、勿帶 `--allow-apply`。**
- **誰**：AI（監看）＋【自動】cron
- **前置**：第 6 步（slot 淨空）
- **驗收（隔晨四項，runbook 原文）**：① `SELECT status FROM evolution_run ORDER BY run_id DESC LIMIT 1`＝`succeeded`；② `SELECT count(*) FROM promotion_queue WHERE queue_status='superseded'` > 0（**現查 0**，I5B 首次生效）；③ `pending_auto` 全屬 run 22（現查 17 列全屬 run 21）；④ 最新 `evolution_iteration_ledger` 之 `gain_evidence->>'basis'` 不再是 `incomparable`；⑤ `evolution_apply_log` 無新增（未帶 `--allow-apply`）。
- **可並行**：唯讀，與所有步並行（23:00 後與重活互斥）。

---

**第 9 步｜輕量並行批（今日可同時開的 26 項 PG-NEWFILE ＋ 6 項 PG-DOC）**　🟢【可先做】
- **做什麼**：依 §0.2 車道表，於今日剩餘時間內同時推進輕量層（<200 MB RSS，現查 available **6,960 MB**，上限 6–8 條）。**建議今日優先四項**：
  - **M-G2**（三支掃描器地板）——本批**單項投報最高**，一次堵住 G1／G5／G7 三個獨立假綠的**共同再生產路徑**。同時吸收 **X1-r**（sim selftest 之退回舊版驗紅）。
  - **M-N18**（`verify_code_reports.py:16` ROOT 硬編）——**必須先於 M-N17**，它是後者的設計約束來源；正解寫法可抄 `check_vendor_binding.py:47`。
  - **M-N1 ＋ M-N2**（探針綁定表 ＋ 度量登錄表）——共用 schema，同批邊際成本近零；**越早建基線，能觀察到的 diff 越多**。
  - **M-O3**（`sync_memory.py export` 密碼掃描）——不可逆風險，成本近零。
- **誰**：AI（可 fan-out 多線，**但須由編排者明示檔案集不重疊**——#34 三項硬邊界不含撞檔，M-P1 未裁前不可依賴規則保護）
- **前置**：無
- **驗收**：見 §1 各項；共通要求＝新增 script 須含執行指令矩陣、`--selftest` rc=0，且 `check_cmd_matrix.py` 受檢數由 **467** 前進而缺漏仍 **0**（現查 467/467、rc=0）。
- **可並行**：組內 26+6 項互不重疊，可開 6–8 線。

---

### 階段 1 — 本週（08-04 至 08-09）：讓紅燈會亮

---

**第 10 步｜M-G3　`reconcile_audit.py` 接上 library 正解**　🟢【可先做】
- **做什麼**：`scripts/reconcile_audit.py:158` 之 `passed = vm == 0 and ex == 0 and not inc` 未納 `coverage_gap`；正解住 `src/augur/audit/reconcile.py:587`（含 `and not coverage_gap`）且已有回歸鎖。改為呼叫 `reconcile.verdict()`。
  - **⚠ 2026-08-03 更正（本檔原文事實錯誤）**：原文稱正解「**全 repo 零真實呼叫者**」——**不實**。實查（`git grep 'reconcile\.verdict(' d69452b^`，即 M-G3 落地前）已有 **4 支生產呼叫者**：`daily_maintenance.py:131`、`full_market_sync.py:93,146`、`full_universe_attest.py:105`、`refetch_fixed_tables.py:42`。**寫 `attestation_result` 的那條路早就在用正解**；M-G3 修的是另一支不寫帳本的 driver。原文若被讀成「這條判準從未生效過」，會高估 M-G3 的效力。
- **⚠ S1 不可略**：先跑唯讀影響面掃描（全表對帳算出「改判式後由 PASS 轉 FAIL 的表清單」），否則直接改上去可能連鎖觸發 watchdog。
- **誰**：AI
- **前置**：無
- **現況為 latent**：`SELECT count(*) FROM attestation_result WHERE passed AND coverage_gap_n>0` = **0**；全表 **9 列**（⚠ 優化計畫書兩處寫「10 列」，與 live 及 r4 D5 不符，**以 9 為準**）。但最新列 id=10 之 `passed=t` 而 `missing_in_db=11,145`。
- **驗收**：① 合成 `matched=0, vm=0, ex=0, coverage_gap=True` → `_summary()` 回 `passed=False`（現回 True）；② 退回舊碼跑同 fixture → 回 True（**先驗紅**）；③ 回歸鎖 fixture 取自 `reconcile.py` 真輸出、**非手寫 dict**（#35(1)）；④ `grep -n coverage_gap scripts/reconcile_audit.py` 於判式行命中。
- **可並行**：PG-AUDIT 單檔，與第 11–18 步全部並行。

---

**第 11 步｜M-M1 → M-M2　sim evaluator 單線（組內序列）**　🟢【可先做】
- **做什麼**：三項落在**同一支** `scripts/evaluate_sim_calibration.py`（X1 已修為第一項），**必須綁成一個工單交給一個執行者**，不可分派多 agent。順序：
  - **M-M1**：`_evaluate` 於 apply 模式僅檢 `k_clusters < th["date_clusters_min"]`（`:546-548`），未檢 `n_valid < th["n_valid_min"]`（100）。改為把 `undecidable_reasons` 非空納入拒寫，或用起既有 `is_invalid boolean NOT NULL DEFAULT false` 欄（現行 INSERT 完全沒用到）。
  - **M-M2**：`:370-373` 之 `_kill_state` 呼叫 `effective_kill_state(states)` **未傳 `env_halt`**，而 runner／settle／propose 三支都讀 `AUGUR_EVOLUTION_KILL_SWITCH` ⇒ evaluator 是唯一 **fail-open** 的一支。補 `env_halt=`（抄 runner 既有寫法，#12 同一住所）。
- **⚠ 已更正之素材**：r4 **D34**（`apply_evolution_promotions.py:304` kill scope 只有 tw+global＝射程缺口）**經親讀撤回**——`:303` 註解逐字「本引擎屬 tw 軸;自軸或 global 任一 halt 即停(OR、fail-safe)」且 `:305` 已傳 `env_halt=_env_halt()`，是**設計正確**。合成路應據此更正 D34 文字，**不得兩說並存**。
- **誰**：AI（單一執行者）
- **前置**：無
- **驗收**：① 構造 K=3／n_valid=60 之 fixture → 拒寫或 `is_invalid=true`（現況寫入且 `is_invalid=false`）；② `AUGUR_EVOLUTION_KILL_SWITCH=halt venv/bin/python scripts/evaluate_sim_calibration.py --dry-run` → **rc≠0**（現照跑）；③ `sim` scope 設 halt 亦拒；④ selftest 加對應紅測，**且退回舊版須變紅**。
- **可並行**：PG-SIMEVAL 單檔，與第 10、12–18 步全部並行。**組內必序列。**

---

**第 12 步｜M-L1 ＋ M-L2　治權 lint 合單**　🟢【可先做】（(c) 掛閘除外）
- **做什麼**：二者**同改 `scripts/check_treaty_refs.py`／`tools/constitution_lint/`，須合為一個工單**：
  - **M-L1(a)**：新增 `cs_selfversion_mismatch` finding——檢「檔名 stem 版號＝H1 標題版號＝`spec-version`＝`archive-path`」四值一致。現查漂移：`CS-系統架構大憲章_v1.54.0.md`（檔名 v1.54.0／標題 v1.53.0／`spec-version: v1.53.0`）、`CS-系統核心思想_v1.10.0.md`（檔名 v1.10.0／標題與 spec-version 皆 v1.9.0）；`CS-CLAUDE.md` 之 `spec-version: v1.35` **正確**。
  - **M-L1(b)**：`tools/constitution_lint/report.py:51-61` 之 `corpus_files()` 只 glob `specs/*.md`（現查 **14** 檔），而 `constitution/` **51** 檔、`docs/compliance/` **7** 檔全在射程外。
  - **M-L2**：加「修訂表狀態欄非 SUPERSEDED 者恰為 1 列」斷言。**正則須同時認 `**現行**`／`**ACTIVE**`／`現行`／`ACTIVE` 四種寫法**——本輪之所以漏正是因為只認一種。
- **誰**：AI（規則）／hugo（改正文，依 #19 逐段呈）
- **前置**：無（(c) 掛第六閘＝M-L7，需裁）
- **驗收**：① M-L1(a) 跑在現況須**恰報 2 筆**（大憲章、核心思想各一），`CS-CLAUDE.md` 不報（**先驗紅**）；② M-L2 跑在現況須報「2 列」（`:446` v1.49.0 標 `**ACTIVE**` ＋ `:451` v1.54.0 標 `**現行**`），修正後恰 1 列；③ M-L1(b) 之 corpus 擴充後，`constitution/` 51 檔進入射程——**(b) 未估、須先抽樣**（51 檔之不變式尚未定義，建議先抽 5 檔量單位成本）。
- **可並行**：PG-LINT，與第 10、11、13–18 步全部並行。

---

**第 13 步｜M-G8　knowhow-refresh 空轉 fail-loud**　🟢 S1／🔴 S2 需授權
- **做什麼**：(S1) 在 `refresh_knowledge_pipeline.py` 之 domain 解析段加 fail-loud 分支＋候選數地板；(S2) 改 `augur-knowhow-refresh.service` 之 ExecStart（現含 `--from-stage promote --domain finance`）。
- **現查**：`SELECT count(*) FROM knowledge_item WHERE domain='finance'` = **0**；同時刻全域 `knowledge_staging status='pending'` = **102,039**。⚠ **兩份計畫的排程時點都寫錯**——優化計畫書 §4.2 記「02:00 週日」，live `systemctl --user list-timers` 現查 `augur-knowhow-refresh.timer` **NEXT＝Sun 2026-08-09 04:30**、LAST＝Sun 2026-08-02 04:30（該計畫自己 P0-7 所引 journal 亦為 04:30，**檔內自相矛盾**）。⇒ 下一次假綠窗口是 **08-09 04:30**（還有 6 天）。
- **誰**：AI（S1）／hugo（S2 授權動 systemd，#6／#7）
- **前置**：無
- **驗收**：① `refresh_knowledge_pipeline.py --domain <不存在>` → **rc≠0** 並印可用域清單（現況 rc=0 且印 0 待辦）。⚠ 本輪**只驗了 DB 側**（domain='finance' 為 0、pending 102,039），**未實跑該腳本**（非唯讀、避免副作用）——rc 現值為引用素材，執行時須自行實跑定論。② S2 後 `journalctl --user -u augur-knowhow-refresh` 出現非零處理量，或明確以 rc≠0 表達「本域 0 件」。
- **可並行**：與第 10–12、14–18 步並行。

---

**第 14 步｜M-G9 ＋ M-G10　資料新鮮度：哨兵先建、再修 TRI**　🟢 哨兵／🔴 補抓需授權
- **做什麼**：
  - **M-G9（先）**：新增 `scripts/check_dataset_freshness.py`（catalog 驅動、per-table `ORDER BY date DESC LIMIT 1`）。⚠ **設計約束非可選**：本輪對 92 個 daily dataset 逐表裸 `max(date)` 全掃在 2 分鐘內未跑完（被 timeout 中斷）⇒ **不可用裸 `max(date)` 全掃**。
  - **M-G10（後）**：`TaiwanStockTotalReturnIndex` 之 `dataset_catalog.data_id_required='t'`、`reconcile_scope='by-dim-id'`，本應走 `_dimension_sync`，而 `run_arena_daily_pipeline.py:79` 只呼叫 `daily_maintenance.py --end d`（by-date 驅動）⇒ **該路徑永遠不會推進 TRI**。接線 `_dimension_sync` 分支。
- **現查（四項獨立證據）**：`TRI max(date) WHERE stock_id='TAIEX'` = **2026-07-09**；`TaiwanStockPriceAdj max` = **2026-07-31**；其間 `TaiwanStockTradingDate` 有 **17** 個交易日；`market_direction_feature max(panel_date)` = **2026-07-09**（凍結）。下游二：`run_arena_round.py:96-100` 以 TRI 當月日期集合算 `h_fires` ⇒ 8 月起 `month_days` 為空 ⇒ **H 軌永不出手**；且 `series["TAIEX"]` 末點停在 07-09 卻與 07-31 的個股序列同批餵給 market 型模型。
- **誰**：AI（哨兵＋改碼）／hugo（補抓放量授權；**依 #25 先最小單位探測**）
- **前置**：哨兵無前置；補抓須 §4 之授權，且**與 M-G5 對帳共用 FinMind 額度與同一 IP，須錯開日子**。
- **驗收**：① 新哨兵無參數 graceful、含指令矩陣、`--selftest` rc=0，全量跑 **<60 秒**（對照本輪裸全掃 >120 秒被 timeout 之基線）；② **以今日 live 跑，TRI 必須報紅**（落後 17 個交易日）——**全綠即視為未通過**；③ 至少一列寫入 `validation_evidence`；④ 修復後 `TRI max ≥ PriceAdj max`（現 07-09 vs 07-31）且 `market_direction_feature max(panel_date)` 前進；⑤ **先驗紅**：把 TRI 退回 07-09 之快照要能讓哨兵變紅。
- **⚠ 補抓 API 面未估、須先抽樣**——`_dimension_sync` 之實際 request 數取決於 resume 粒度，須先跑 `--dry-run` 量測，不編數字。**污染期之 arena 預測是否需標記／重跑屬 Steward**（涉已入帳本之預測列）。
- **可並行**：哨兵屬 PG-NEWFILE，與第 10–13、15–18 步並行；**補抓屬 PG-OPS，與 M-G5 互斥**。

---

**第 15 步｜M-G4 → M-G5 → M-G6　維運告警鏈（硬依賴串行）**　🔴 需授權
- **⚠ 這是全案唯一的三層硬依賴鏈，任一跳過後者的驗收都會是假綠：**
  ```
  第 10 步 M-G3（修 reconcile 判式）→ M-G4（修 watchdog 發車）→ M-G5（掛對帳排程）
  ```
- **M-G4（watchdog 送車即死）**：現查證據鏈——`~/audit_watchdog.log:552-553`「08-02 18:45 ⚠ 過期→relaunch」；其後 **29 行**連續「冷卻中(最新 PASS@08-01 18:43)」；但 `~/audit_retry.log` mtime 停在 **2026-08-01 18:45:26**、`attestation_result` 最新仍是 **08-01 18:43** ⇒ 08-02 那次發車**一個位元組都沒寫出來**。機制：`augur-audit-watchdog.service` 為 `Type=oneshot`＋`KillMode=control-group`，而 `audit_watchdog.sh:57` 以 `setsid nohup … &` 送車——`setsid` 脫離 session、**不脫離 systemd cgroup**【此為根因推論；觀察事實 (1)–(3) 已足以立項】。兩案：(甲) unit 加 `KillMode=process`；(乙) 改用 `systemd-run --user --scope`。**閉環驗證是必要條件**。
- **M-G5（對帳無排程）**：`run_arena_daily_pipeline.py:77-80` 日班第①步為 `daily_maintenance.py --end <d>`，**不帶 `--audit` 也不帶 `--heal`** ⇒ 每日只同步、從不對帳。`attestation_result` 唯一來源是 watchdog relaunch，而該路徑自 08-02 起送車即死 ⇒ **對帳鏈目前沒有任何活著的觸發器**。
- **M-G6（cron 零告警）**：systemd 側 **13 個 user unit 全部**有 `OnFailure=augur-alert@%n`；cron 側 `crontab -l` **15 行**，`grep -c 'notify_failure\|alerts.log'` = **0**。sink（`scripts/notify_failure.sh` → `~/logs/alerts.log`）已於 08-01 上崗但全檔只有一行測試紀錄，**生產中從未觸發過**。改法＝改 `install_cron.sh` 期望表（現查 `--check` rc=0「✓ 一致」），**不手改 crontab**。
- **誰**：AI（改 unit／期望表／閉環判式）／hugo（授權動 systemd、跑 `--apply`、授權 M-G5 之 API 面）
- **前置**：M-G5 硬依賴 M-G3 → M-G4。M-G6 無前置（但 `--apply` 需授權）。
- **驗收**：
  - M-G4：① 觸發一次真發車後 60 秒內 `~/audit_retry.log` mtime 前進（**現凍在 08-01 18:45:26**）；② `SELECT max(run_at) FROM attestation_result WHERE driver LIKE 'daily_maintenance%'` 前進（**現查 2026-08-01 18:43:57**）；③ **先驗紅**：以舊組態重跑，新加的閉環判式須報「發車後無產出」；④ 發車失敗與「正常冷卻」之輸出字樣**在 grep 上可區分**（現況二者皆為『冷卻中』）。
  - M-G5：① 掛班次後連續 3 日 `SELECT count(*) FROM attestation_result WHERE run_at > now()-interval '3 days'` ≥ **3**（現 **0**）；② **接縫驗收**——其中至少一列之 `passed` 與 `coverage_gap` 一致。**M-G3 與 M-G5 分開驗會各自看起來都對。**
  - **⚠ 2026-08-03 更正（本檔原文期待錯誤，已刪）**：原文要求「`missing_in_db=11,145` 這類情形**必須寫 `passed=false`**」——**這個期待與 attestation 的宣稱不符，照做會壞事**。
    `src/augur/audit/reconcile.py` 檔頭第 4–10 行逐字定錨三類差異：`value_mismatch`＝同鍵值不同、`extra_in_db`＝**幻像/PK 碰撞紅旗**、`missing_in_db`＝**覆蓋缺口；重跑 sync 即補**；並明寫「attestation 通過 ＝ `value_mismatch=0 ∧ extra_in_db=0`」。
    ⇒ attestation 宣稱的是「**DB 裡的東西沒有假的**」（無幻像），**不是**「DB 有 API 的全部」（完整）。把 `missing_in_db` 納入 `passed` 等於**改變該機制宣稱在量什麼**，屬判準變更；且實測後果為災難：`attestation_result` 全 **10** 列之 `missing_in_db` 依序 5369／5700／5700／5754／6138／7839／7839／7839／11145／**13342**，**無一為 0** ⇒ 納入後 10 列全轉 FAIL
    〔⚠ 本行自身的小史：初稿寫「9 列」——那是 M-G3 執行線數小時前查的值；本檔付印前現查已增至 10 列（12:09 那輪 audit 寫入）。**引用他人查得的數字而未自行現查，正是本檔各處數字漂移的成因**；凡本檔數字皆附覆核指令，讀者應以現查為準〕 ⇒ watchdog 之 `fresh_pass` 恆 0 ⇒ 每 24h 冷卻窗到期即發車跑 6h selfheal、**永不收斂**。
    **正解**：覆蓋缺口該有**獨立的可見載體**，不是塞進 attestation 的 `passed` 欄——落點＝第 17 步 M-P13 之 `validation_evidence` 新列（斷言「`missing_in_db` 之趨勢／絕對量」），該列今日必為紅。
    ⇒ 本項**不需 Steward 裁定 `missing_in_db` 語意**（語意已定錨於 code 檔頭），只需本檔更正期待。
  - M-G6：① `crontab -l | grep -c 'notify_failure'` = **15**（現 **0**）；② `bash install_cron.sh --check` rc=0「✓ 一致」；③ **先驗紅**：刻意讓一條 cron 失敗，`~/logs/alerts.log` 必須增一行。
- **⚠ M-G5 日班對帳時長未估、須先抽樣**——`~/audit_retry.log` 之 08-01 那輪由 16:40 發車到 18:45 完成（≈2 小時）但那是 `--heal` 全量；日班該用什麼 `--audit-days` 與抽樣股數（現 `AUDIT_SAMPLE_STOCKS=40`）須先量一次再定，不編數字。
- **可並行**：**組內三項嚴格序列**；改 unit／期望表本身（不觸 API）可與第 10–14、16–18 步並行。**M-G5 與 M-G10 補抓共用 FinMind，須錯開日子。**

---

**第 16 步｜M-K1 · M-K2 · M-K3　知識層執行層修正**　🟢【可先做】
- **做什麼**：
  - **M-K1**：刪 `retrieval.py:371-375` 與 `:405-409` 兩段 try/except。`:408` 之 `set_kh_evidence_validity(cur)` 中 `cur` 是**未定義全域名**（`co_varnames` 無 `cur`）→ NameError 被同段 `except Exception: pass` 吞掉；而 `:373` 中 `cur` 是形參、真的會執行，但清空快取後不寫 `_at` 鍵，使 `_OK_TTL_SEC=900` 的記憶化被自己打掉 ⇒ 每次檢索 ≈**1.3s**。**⚠ 改後須 `systemctl restart augur-advisor augur-chat`**（#7，http.server 不熱更新）。
  - **M-K2**：`auto_admit.py:599-604` 之 `d < before` 捷徑把未重評的層記成 `{"verdict":"pass","note":"prior_depth"}`。`verdict` 改為 `"not_reevaluated"`，迴圈判斷改看 `in ("pass","not_reevaluated")` 以**保行為不變**。
  - **M-K3**：`backfill_fulltext_unattempted.py` 加分批冪等＋掛既有班次（現為一次性、無排程，每日漏 21 件）。
- **誰**：AI
- **前置**：無（**DDL 部分須等 M-O1**——現查 pid 217629 持 `knowledge_item`／`knowledge_item_text`／`knowledge_sentence`／`knowledge_sentence_embedding` 及 9 個 index 之 AccessShareLock；**純 DML 走 ROW EXCLUSIVE、與 ACCESS SHARE 相容，可以跑**）
- **建議時窗**：**週間 10:00–18:00**（現查唯一無本專案排程之時段；02:00–06:00 有 embed-catchup 03:30／ata-advance 04:00 兩個**不入任何鎖**的 CPU 消費者）
- **驗收**：① M-K1：連續兩次 `kh_evidence_valid()` 第二次 **<0.05s**；`ok=False` 時 `rank_item_citations` 回傳序與輸入**逐項相同**；② M-K2：`SELECT count(*) FROM knowhow_auto_admit_state WHERE layer_scores::text LIKE '%prior_depth%' AND layer_scores::text LIKE '%"pass"%'` → **0**，且 depth 分布不變（行為不變之證）。**⚠ 全量 upsert 機時未估**（142,441 件 depth≥5 之 item），須先抽 1,000 列量單位成本。
- **可並行**：M-K1（`retrieval.py`）與 M-K2（`auto_admit.py`）不同檔可並行；**M-K2 與 M-G15、M-N9 同檔區須序列**。

---

**第 17 步｜M-P12 ＋ M-P13　綠燈帳本誠實化**　🟢 (a)(b)／🔴 (c) 需裁
- **做什麼**：
  - **M-P12(a)**：`last_verified_at IS NULL` 者不得計入 green（改為 `unverified`）——現查 `SELECT count(*) FROM validation_evidence WHERE status='green' AND last_verified_at IS NULL` = **2**（`E3_promotion_funnel`／`E4_gm_promotion_gap`，`valid_until=2026-10-09`，**從未被任何檢驗碰過卻以 green 身分計入**）。
  - **M-P12(b)**：紅燈加 `red_since` 欄與週報一行——現查 19 列＝green **16**／red **3**（`E2_feature_frozen_panel`、`E4_exclusion_set_contract`、`E10_daily_green`），每日 07:10 班次忠實重驗成紅、寫回 DB、無人處置。
  - **M-P13**：新增 sim／arena 之 `sql` 型 VE 列——現查 `SELECT count(*) FROM validation_evidence WHERE evidence_id ILIKE '%sim%' OR claim ILIKE '%sim%'` = **0**；`direction_gate` 現查 **0/29 evaluated_pass**；`sim_run_link` 0 列。
- **誰**：AI（(a)(b)＋M-P13）／hugo（(c) E2/E4 處置＝M-P10）
- **前置**：(b) 之加欄 DDL 與 M-P11（帳本表射程）之圈選重疊 ⇒ **建議併入同一 DDL 窗**（#30 避開週六 07:30）
- **驗收**：① `SELECT count(*) FROM validation_evidence WHERE status='green' AND last_verified_at IS NULL` = **0**（**改動前跑必須回 2 ＝ 先驗紅**）；② green 總數由 **16** 誠實降為 **14**（分母不變 19），且該降幅在報告中具名記錄為**口徑更正、非退步**；③ 每日 07:10 log 增印「red N 條，最久者 red_since=YYYY-MM-DD」；④ M-P13 新增 ≥3 條且**至少一條在今日 live 是紅的**（TRI 落差 17 交易日、`sim_run_link` 0 列）——**全綠即證明斷言沒有鑑別力，視為未通過**；⑤ 每條新列建立當日 `last_verified_at` 非 NULL（不得重蹈 (a) 之未驗列）。
- **可並行**：與第 10–16、18 步並行；**DDL 部分與第 2 步、第 21 步同窗批次**。

---

**第 18 步｜M-O2　備份鏡像驗證（AI 部分）**　🟢【可先做】
- **做什麼**：`scripts/backup_database.sh:63-65` 為 `mkdir -p && cp -r … && echo "✓ 鏡像完成"` ⇒ **綠燈量的是 `cp` 當下的 rc，不是「鏡像現在還在、且可還原」**。本地 dump 有走 `pg_restore -l` 驗 toc（`:62` 印「11G / 2696 物件 / 352s」），**鏡像那一份完全沒驗**。加：鏡像後 `pg_restore -l` 驗證＋物件數比對＋一列備份帳本＋一條 `validation_evidence`（備份新鮮度 ≤ 8 日）。
- **現查**：`ls -la /mnt/c/database/` → **total 0（空）**，mtime 2026-08-03 08:21；而 `~/logs/backup.log` 之 08-01 那輪逐字寫「[3/4] 鏡像 → /mnt/c/database … ✓ 鏡像完成」。兩份 11G dump 與 61 GB live DB、repo 同在 `/dev/sdd`。
- **誰**：AI（驗證加固）／hugo（異裝置選型＝M-O2 之 Steward 部分，見 §4）
- **前置**：無
- **驗收**：① 跑 `bash scripts/backup_database.sh --run` 後鏡像側亦印出物件數且與本地一致（現本地 **2696** 物件、鏡像 **0** 驗證）；② **先驗紅**——在 `/mnt/c/database` 為空之現況下跑唯讀狀態模式，新加的哨兵**必須報紅**（現況只印「鏡像 /mnt/c/database: (無)」而 rc 仍 0）；③ 新增一列 `validation_evidence` 量「最新可還原鏡像之年齡 ≤ 8 日」，**今日必為紅**；④ 異裝置決定前，該紅燈**不得**被改判或加豁免——它就是待裁事項的可見載體。
- **可並行**：PG-OPS，與所有步並行。**唯一時間約束＝驗證動作不要撞週六 07:30 之 dump 窗**（實測僅 ≈6 分鐘 ＋ drvfs 鏡像時間，遠短於記憶檔之「15-20 分」估計）。

---

### 階段 2 — 兩週（08-10 至 08-23）：口徑機械化與治權層自我一致性

---

**第 19 步｜M-N1 完成 ＋ M-N4 · M-N5 · M-N13 · M-N14 · M-N16　過期族一次收斂**　🟢（M-N5 需 M-N7）
- **做什麼**：把散在 F2 報告／GROUNDING-MAP／ULTRACODE-SCHEDULE／CLAUDE.md／HANDOFF／記憶檔六處的手抄數字，全部改為由 M-N1 綁定表自動 diff。**這是過期族的唯一槓桿**——17 則之個別修正若不接探針，只是把一個手抄值換成另一個手抄值。
- **現查漂移速率（證明必要性）**：同一日內 vendor 基線 128/170→**130/172**；`2026-10-14` 在治權檔命中 74 處→**88 處**；`reports/` 之治權版號引用中，指向現行大憲章 v1.54.0 者僅 14/120 次、指向現行原則精華 v1.12.0 者僅 7/87 次 ⇒ **一個新 agent 讀到隨機一份報告，約有 88% 機率讀到指向舊版治權檔的引用**。
- **誰**：AI
- **前置**：M-N5 需 M-N7（vendor 權威尺）先裁；其餘無前置
- **驗收**：① 把任一綁定值手改一位數，`--check` 必 **rc≠0**（**先驗紅**）；② 覆蓋數 ≥ §3.2 中屬 live 文件者（**7 處**：`CLAUDE.md:127`／`HANDOFF.md:26`／`GROUNDING-MAP.md:45-47` 三列／F2 備料兩處／`github-workflow.yml` 檔頭／記憶 2 檔）；③ 每列必須攜帶 `ruler_key`（FK 指向 M-N2 之度量登錄表）——**只綁值不綁尺者視為未完成**；④ M-N4：`HANDOFF.md` 三處與現查一致（crontab **15**、deferred 未清 **0**、VE「19 列／red 3（含 1 條僅週日跑）」），每處旁附可重跑之一行指令；⑤ M-N16：r0–r3 各檔頭有 `superseded_by`。
- **可並行**：PG-DOC 逐檔互斥、彼此並行（6 條線）；與第 20–25 步全部並行。

---

**第 20 步｜M-N2 完成 ＋ M-N8 · M-N9 · M-N10 · M-N11 · M-N12　七組一名多義正名**　🟢（authoritative 標定需裁）
- **做什麼**：七組全部登錄 `measure_registry`，欄含 `measure_key`／`ruler_key`／定義／可重跑指令／`authoritative` 旗標。**現查各組值**：
  | 組 | 並存口徑 | 現查值 |
  |---|---|---|
  | public 表數 | `relkind='r'` ／ `pg_tables`（含分區父表） | **334** ／ 335 |
  | script 支數 | `ls scripts/*.py` ／ `check_cmd_matrix` 射程 | **327** ／ **467** |
  | KH0 破口 | 未評 ／ 無原文 | 138,875 ／ 138,826（差 **49**） |
  | vendor 直綁 | GROUNDING-MAP ／ F2 ／ 今日 grep ／ 止血閘 | 37 ／ 47 ／ 50 ／ **56 檔·172 處** |
  | 閘表分層 | 有 trigger 63 ／ 含 UPDATE 51 ／ 裸 UPDATE 12 ／ `ledger_guard` **25 表** ／ `delete_only` **9 表** | 四尺不可相減 |
  | `sent_no_emb` | 全庫未嵌句 ／ 有未嵌句之 itext ／（r4 另兩把） | 67,080 ／ 1,410 ／ 14,208 ／ 396 |
  | `dual_green_n` | G-PROM∧G-ECON 相異 feature ／ 八閘全綠**列** | run21＝**2** ／ **3** |
- **誰**：AI（登錄）／hugo（`authoritative` 標定，低爭議者可批次）
- **前置**：無（vendor 那組之 authoritative＝M-N7，需裁）
- **驗收**：① 一句 SQL 可判「每個 `measure_key` 之 `count(*) FILTER (WHERE authoritative)` **恰為 1**」；② M-N1 之每列探針必須 FK 指向已登錄之 `(measure_key, ruler_key)`——**先驗紅**：插入無 ruler 之探針列須被 FK 拒；③ M-N12 探針以 run 21 資料跑須得 **(2, 3)** 而非 (2, 2)；④ M-N9：`run_kh_chain --check` 輸出須**同時印兩數並各標尺名**（現況只印一數）。
- **⚠ M-N11 之完整集合**：本輪只重跑兩把尺（67,080／1,410），r4 所載另兩把（14,208／396）之定義未還原 ⇒ 驗收要求把**全部**尺登錄，不以其中兩把為完整集合。
- **可並行**：PG-DOC／PG-NEWFILE，與第 19、21–25 步並行；**M-N9 若同改 `run_kh_chain.py` 則與第 16 步 M-K2 同檔區須序列**。

---

**第 21 步｜M-M3 ＋ M-P12(b) ＋ M-N1 新表　DDL 批次窗（一次做完）**　🔴【需裁：M-P11】
- **做什麼**：M-P11 一裁即解鎖三項——`sim_calibration_eval`／`sim_realized_outcome`／`sim_run_link` 補 `honesty_ledger_guard`（M-M3）、`validation_evidence`＋`attestation_result` 補閘（M-P12(b) 相關）、M-N1 之 `treaty_probe_binding`／`treaty_probe_reading` 是否掛閘。
- **為何併批**：現查三張 sim 表 **0 列**（56 kB／24 kB）、`validation_evidence` **19 列**（96 kB）、`attestation_result` **9 列**（64 kB）⇒ **CREATE TRIGGER 之 ACCESS EXCLUSIVE 是次秒級**；且 pid 217629 持有的 18 個鎖物件**不含這些表** ⇒ 無排隊、無 #30 鎖風暴。**併批可省下多次獨佔鎖。**
- **為何在首格前**：三張 sim 表正是要拿來證明能力宣稱的表（#32b）。在首格 52 列落地**之前**掛閘，宣稱強度是「本表所有列自始受 UPDATE 閘保護」；落地之後才掛，強度降為「自某時點起」。**成本差＝0，證據強度差是實的。**
- **誰**：AI（實作）／hugo（M-P11 射程圈選）
- **前置**：M-P11 裁決。⚠ **若 Steward 採乙案（「帳本表不掛閘」延伸為通則），本項反而不該做。**
- **驗收**：① 裸 `UPDATE sim_calibration_eval SET crps_mean=0` 被拒（現況允許）；② 裸 `UPDATE validation_evidence SET status='green' WHERE evidence_id='<red 之一>'` 被拒；加 GUC 後成功；③ `SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal` 由 **116** 增加且與新增數相符；④ sim 四件套 `--selftest` 仍全綠；⑤ 寫入端（`verify_validation_evidence.py`／`ops/audit_selfheal.sh`）之交易內補 `SET LOCAL augur.honesty_write='on'`，漏補者首次執行即 fail-loud（**這是想要的訊號**）。
- **可並行**：**DDL 窗獨佔**——與第 2 步 M-T1 之 FK 同窗批次；避開週六 07:30。其餘步照常並行。

---

**第 22 步｜M-E1(甲) · M-E2 · M-E7　進化引擎溯源與方向**　🟢（M-E1 乙案需裁）
- **做什麼**：
  - **M-E1(甲)**：`gate_cache[feature]` 改為 `(feature, direction)` 鍵。現查 run 21 仍有 **4 列**方向衝突（q562/p116、q563/p123 之 `map.direction=1` vs gate `expected_direction=-1`；q643/p116、q644/p123 反向）。其中 562/563 拿到的是以 dir=−1 算出的 G-PROM=PASS＋G-SIGN=PASS。**目前四列因 G-ECON=FAIL 而 rejected_gate，但只要 G-ECON 轉 PASS 即八閘全綠→pending_auto→可 APPLY。**
  - **M-E2**：對每一列 `evolution_production_feature_set` 唯讀對帳 `apply_log_id` → `evolution_apply_log.queue_id` → `promotion_queue.action` 與該列 `last_action` 是否一致。已知斷點：`lending_fee_rate_mean_20d` 之 `apply_log_id=24` 指向 queue 311（07-29 promote 證據被當 08-01 demote 依據）。
  - **M-E7**：`eval_code_hash` 為整檔位元組 sha——改一個註解即產生新 cell，把邏輯抽到別檔則實質改了演算法而 hash 不動。誠實正名。
- **誰**：AI
- **前置**：**M-E1 甲案之改碼須避開 TWEVO 執行窗**（`run_philosophy_evolution.py` 由 cron 於 23:00 執行；跑到一半換碼＝結果不可歸因）
- **⚠ 運算成本**：M-E1 甲案 **+11–12 分鐘/feature**（優化計畫書依 07-31 實測 645–720 s/feature 推算，**本輪未重測**）；若今晚生效，I3 時長增加，須確認不撞 `--slot-wait 10800` 上限。
- **驗收**：① 方向衝突 SQL 回**零列**（現 **4 列**）；② M-E2：不一致列數 = 0（**現查 3 列 active，逐列指向未親查——本輪只確認兩份計畫皆缺此項**，見 §8）。
- **可並行**：PG-EVO，與第 19–21、23–25 步並行。

---

**第 23 步｜M-G11 · M-G12 · M-G13 · M-G14 · M-G15 · M-G16　假綠族探針批**　🟢 探針部分
- **做什麼**（六項皆為新檔或加斷言，可再拆多線並行）：
  - **M-G11**：`tests/test_l716_conflict_registered.py` 現 assert 僅四條（`RULING.exists()`／`"L7.16" in text`／`"AL-2026-046" in text`／`"## AL-2026-046" in AMENDMENT_LOG`）——把 `RULING-2026-042` 之簽核欄 `[x]` 改回 `[ ]` 測試仍全綠。加簽核欄斷言。
  - **M-G12**：`execute_sunset_consequence --check` 之綠燈原文為「本行印得出來＝未鏽」。現查 `SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'trg_sunset_seal_%'` = **0**。改為 SQL 查詢＋rc 回傳。
  - **M-G13**：現查 `steward_question_ledger` status 分布 awaiting_hugo=**159**、`resolved_by='hugo'`=**0**（六個 resolved_by 值中無 'hugo'）；最舊 `asked_at`=2026-06-22（懸置 **42 日**）。探針門檻「最舊 awaiting_hugo 懸置 > 30 日即紅」。
  - **M-G14**：`confidence_band` 現查 high **145,958**／absent 380／low 16。**閘已補**（`MIN_DISCRIMINATING_BANDS=2` 之 `discrimination_verdict` 已真接線於 `run_kh_chain.py:83`／`reevaluate_kh_depths.py:83`，現跑 ok=False、`band_minority_mass` 0.0027 < 0.05）；**殘餘缺口＝消費側**——任何直讀 `confidence_band` 而不經 gate 者仍取到假訊號。建 honest view。
  - **M-G15**：`auto_admit.py:335-360` 逐字 `if snap["has_text"]: return {"verdict":"pass","note":"既有原文＝KH1 視同通過"}`，且 `qualification` 為 reject/error 時只要有原文仍回 `pass`。`knowledge_item_text` 現查 **158,532** 列全部走旁路 ⇒ KH1 通過率結構上不可能不是 100%。**這與 KH8 被判死的理由完全同構**（零變異指標不得充當證據，`AUGUR-MC v1.6 §P4.E7`），但 KH1 未受同樣處置。正名＋分流探針。
  - **M-G16**：現查 `pg_trigger` 非內部 trigger 之 `tgenabled` 分布＝`'O'` **116**、`'A'` **0**。探針以「ALWAYS 支數 ≥1 才綠」為門檻。
- **誰**：AI（探針／正名）／hugo（M-G13 之 Q22、M-G15 之旁路存廢、M-G16 之 `ENABLE ALWAYS`，見 §4）
- **前置**：無
- **驗收（六項共通）**：**今日 live 跑必須報紅**——M-G11 之複本簽核欄改 `[ ]` 須 FAIL、M-G12 現況（0 支 seal trigger）須 rc≠0、M-G13 現況（42 日）必紅、M-G14 之 grep 直讀路徑數現況應 >0、M-G15 之旁路占比 >90% 必紅、M-G16 現況（ALWAYS 0 支）必 rc≠0。**全綠即視為未通過。**
- **另**：M-G16 附帶要求——全 repo 凡以「硬閘」描述 trigger 之處皆加「origin-mode、superuser 可靜音」限定詞（可 grep 判）。
- **可並行**：PG-NEWFILE，六項可再拆 4–6 線；**M-G15 與 M-K2、M-N9 同檔區須序列**。

---

**第 24 步｜M-O4 · M-O5 · M-O7 · M-O9 · M-N15 · M-N17 · M-W6　覆蓋率與存量批**　🟢【可先做】
- **做什麼**：
  - **M-O4**：現查 **288** 支含 selftest 之檔僅 3 支在排程（週一 08:40 三支 MCP）；`crontab -l | grep -c pytest` = **0**，**26** 支 pytest 零排程。掛既有週一 08:40，**零新排程**。
  - **M-O5**：`augur.arena`／`augur.execution`／`augur.deliberation` 不在任何字面掃描集合；07-31 單一角色整併後 `augur_predict` REVOKE 對偶已消失 ⇒ AST/字面閘為唯一閘。
  - **M-O7**：`tools/project_memory_mcp/embed.py:31-36` 走 Ollama `/api/embed`，而 `fuser -v /tmp/augur_llm.lock` 顯示無持有者 ⇒ 不入 LLM 單槽鎖。包 flock（只改呼叫點，不動 MCP server 生命週期）。
  - **M-O9**：容量哨兵（印 nproc／loadavg／available／llama-server RSS／heavy_slot 持有者），掛既有週日 09:00。
  - **M-N15**：`MEMORY.md` 稽核器（四類：孤兒檔／截短名／多重 ⭐權威／檔內數字對 M-N1 綁定值之 diff）。現查 memory 目錄 **80** 個 md；已知漂移：`three-gate-strengths:17` 寫「19/19 green」（live green **16**／red **3**）、`:23` 寫「437/437」（live **467/467**）；`db-import-tuning-hnsw-oom` 記「sb=6GB／wm=256MB／mwm=2GB」而 live 為 **2 GB／16 MB／1 GB**（三個數字全部不符）。
  - **M-N17**：`reports/` **301** ＋ `audits/` **200** 檔零 front-matter `status:`、零索引檔。慣例現成——`docs/系統架構大憲章_v1.47.0.md:3` 逐字寫「**SUPERSEDED**：已被 v1.48.0 取代…本檔僅留史料」，reports/ 只是沒把它延伸過來。
  - **M-W6**：`check_vendor_binding.SCAN_DIRS=("src","scripts")` ⇒ `tests/`（已知 2 處直綁）／`tools/`／`ops/`／`augur_proxy/` 全在射程外；`check_cmd_matrix.SCAN_TOP_DIRS` 不含 repo 根。**10-14 前須量準真實出血面。**
- **誰**：AI（M-N15 之「唯一現況權威」規則＝M-P15，需裁；M-N17 同）
- **前置**：M-N17 需 M-N18（第 9 步）先完成；M-N15 之 diff 須以 M-N1 綁定值為基準（**而非另抄一份數字，否則只是新增第三把尺**）
- **驗收**：① M-N15 稽核器跑在現況須報 ≥2 筆數字 diff（19/19、437/437）＋孤兒檔（**先驗紅**）；② M-N17 稽核器現況須報「301+200 份中 **501** 份缺 `status` 欄」，全綠即未通過；③ M-W6 擴口徑後基線重寫須於 commit 訊息記口徑變更；④ 新增 script 使 `check_cmd_matrix` 受檢數由 **467** 前進而缺漏仍 0。
- **⚠ M-N17 之 501 檔存量補標未估、須先抽樣**——建議先對 08 月 18 份＋`HANDOFF.md` 讀序引用之 6 份共 **24 份**試做，量單位成本後再外推。**不得回頭改既有報告正文**（只加 front-matter 與索引）。
- **可並行**：PG-NEWFILE／PG-DOC，可開 5–7 線。

---

**第 25 步｜M-W2　WM.36 欄位級映射單位成本抽樣**　🟢【可先做】唯讀
- **做什麼**：現查 `SELECT count(*) FILTER (WHERE source_column IS NOT NULL AND source_column<>'') FROM world_channel_binding` = **0／98**；`world_concept_version` 六列之 `authoritative_binding_id` **6/6 NULL**、`decided_by` 6/6 NULL ⇒ **WM.36 登錄完成數 0/6**。優化計畫書 P0-5 自己把 S3 標為「未估，須先抽樣，**這是本計畫最大的未知數**」——但**沒有把該抽樣本身立為可排程的項**，於是它會停在「建議」。
- **本步只做抽樣與成本外推，不做填欄**（填欄粒度須等 M-W3／M-W4 裁定，否則可能展錯粒度）。
- **誰**：AI
- **前置**：無（純唯讀）
- **驗收**：產出抽樣報告含——(a) 10 列之逐列展開結果與各自實際耗時（分鐘）；(b) 由 `column_catalog` 可自動配對之比例（機械數字，附 SQL）；(c) 外推 98 列之總時數區間與其推導式；(d) **一句「以此速率，S3 於 YYYY-MM-DD 完成／不可能於 10-14 前完成」之機械結論**；(e) 零 DB 寫入（`source_column` 非空數在本步前後皆為 **0**）。
- **為何現在**：距 10-14 為 **72 日**；若 8 月底前仍無單位成本，「來不來得及」就只能靠感覺。**抽樣成本近零（唯讀），而它是唯一能把該判斷從主觀變機械的動作。**
- **可並行**：唯讀，與所有步並行。

---

### 階段 3 — 一個月（08-24 至 09-30）：存量清償與 sim 終點

---

**第 26 步｜M-M4 ＋ M-M5　sim 時鐘哨與 W4 判決工具**　🟢（promoted 路徑需裁）
- **做什麼**：M-M4＝既有週日 09:00 週報加一行 sim 時鐘哨（下一格 asof／待結算列數／K 進度），並把 settle／evaluate 兩步補進 runbook 並標日期（現 `ops/RUNBOOK-20260803-night.md` 只寫到今晚的 runner `--apply`）。M-M5＝新增 `scripts/decide_sim_verdict.py`（含矩陣＋selftest），**先實作 killed／undecidable 兩條**。
- **現查**：`sim_evolution_verdict` 0 列且全 repo 零 writer；三鎖已在（`chk_sev_promote_signed`／`chk_sev_five_arm_floor`／`chk_sev_evidence_nonempty`）＋`sev_no_delete`／`sev_no_truncate`／`sev_no_update`(GUC)。
- **誰**：AI（killed／undecidable）／hugo（promoted 之人簽路徑，`decided_by` 親跑）
- **前置**：M-M5 建議在 K=1 落地後（≈09-02）再做，以便用真 eval 列測
- **驗收**：① 週報含「sim 時鐘：K=n/3，下一格 <date>，待結算 <n> 列」；② 以合成 eval 列跑 → 寫出 killed 列且三 CHECK 未被違反；③ promoted 路徑在缺 `decided_by` 時**被 DB 拒**（驗鎖真的在）；④ **promoted 路徑一律不設人名旗標**（專章 §4.2）。
- **為何重要**：catch-up 冪等只保證「晚跑不掉格」，**不保證「有人會跑」**；且 `sim_evolution_verdict` 是 sim 軸唯一的終點，而 §2 之 k1/k2/k3 史料實測顯示 7/7 序列全判死【推論，史料非門之證據】⇒ **判死留檔的路徑極可能是首先被走到的那條**。
- **可並行**：PG-NEWFILE，與第 27–30 步並行。

---

**第 27 步｜M-L6 ＋ M-L3　治權對帳與條號前綴**　🟢 lint／🔴 清償需裁
- **做什麼**：
  - **M-L6**：`constitution/RULING-2026-043-B4-UPDATE-GUC-EXPANSION.md` 已存在（`c9575f3`）、`AL-2026-047` 已登錄（裁決檔現 **41** 份／AL 現 47 條），**但生產碼仍有 17 處引用／6 檔**（`migrate_honesty_guards_ddl.py`／`migrate_sim_evolution_ddl.py`／`migrate_steward_qledger_ddl.py`／`src/augur/audit/evolution_ledger_ddl.py`／兩份 `audits/B4-P2*`）。逐處核對「碼內引用之射程主張」與「補建正文之明文射程」是否一致——否則等於用事後補的文字追認事前的施作。**並加回歸鎖防止「先施作、後補號」再犯。**
  - **M-L3**：條號前綴 lint。最尖銳者 `CLAUDE.md:62`「回歸鎖 #15」——本檔 #15＝PR/遠端，真住所是新設 **#35**；`:126`「三敵人零容忍（#1／#8／#15）」在本檔對映為「Read before Edit／報告誠實／PR 遠端」**語意全毀**；且 `:151`（#34 內，07-31 新增）**在紀律訂立後仍犯**。
- **誰**：AI（對帳＋鎖＋lint）／hugo（M-L3 之逐處補前綴＝改治權檔文字，依 #19；M-P16 之 043 簽核）
- **前置**：無
- **驗收**：① **先驗紅為唯一有效驗法**——回歸鎖斷言「`grep -oE 'RULING-2026-[0-9]{3}' scripts src audits | sort -u` ⊆ `ls constitution/RULING-*` 之編號集合」跑在 `c9575f3` 之父 commit（`36c69cc`）須 **FAIL**、跑在 HEAD 須 **PASS**；② 對帳產出差異表（每處引用之射程主張 vs 正文射程，逐行標一致／擴張／收窄）。
- **⚠ M-L3 之 14 例逐處清償未估**——須先逐例判定該補哪個前綴（**屬理解層，錯了會沉默污染下游**，#28 二分之理解軸）。
- **可並行**：PG-LINT／PG-DOC，與第 26、28–30 步並行。

---

**第 28 步｜M-K4 · M-N9(實作) · M-K3(全量)　知識層存量批**　🔴 需裁／🟡 需前置 M-O1
- **做什麼**：M-K4＝`knowhow_auto_admit_run` 帳本止血（現查 **508,926 列**／556 MB；⚠ 優化計畫書 P2-8 與 r4 D28 皆記 **509,551**，**與 live 不符**，方向為減少，成因本檔不臆測——**以 live 為準並現查再定論**）。
- **⚠ 一條兩份計畫都沒寫的硬依賴**：大量 DELETE 會產生大量 dead tuple；若 M-O1 未解、xmin horizon 仍凍在 07-31（pid 217629 已 active **2 天 17:11**），**刪掉的空間根本回收不了**（vacuum 拿不到 horizon）⇒ **M-K4 的收益完全依賴 M-O1 先完成**。
- **誰**：AI（實作）／hugo（M-P11-類之留痕義務範圍＝§4 之 S-7／Q28；M-O1 之 terminate）
- **前置**：**M-O1 → M-K4**（硬依賴）；M-K4 本身需裁
- **建議時窗**：**週間 10:00–18:00**（依 §0.3，重活層現況上限 2 條；且須避開 TWEVO 23:00–08:30、01:30 演化鏈、週六 07:30 dump、週六 09:00 RAWEVO）
- **驗收**：① 表大小由 556 MB 降至目標值，且 `SELECT count(DISTINCT layer_scores) FROM knowhow_auto_admit_run` 前後不變（**證明只刪重複、未刪掉任何不同的評估結果**）；② M-N9 實作後 `run_kh_chain --check` 同時印兩尺。
- **⚠ 未估、須先抽樣**——須先跑唯讀 `SELECT count(DISTINCT (target_kind, target_id, layer_scores))` 取縮減比（該查詢在 50 萬列上是中量作業，≈分鐘級）；**且一旦刪過不可逆**。
- **可並行**：**G-HEAVY 獨佔線**，與 heavy_slot 家族、pg_dump、RAWEVO 全部互斥（雖不共用鎖，但共用 RAM/IO 上限）。

---

**第 29 步｜M-R3　heavy_slot／I3 效能剖析（先量再改）**　🟢 剖析可先做
- **做什麼**：I3 local-gates 現需 **7–10 小時**（`install_cron.sh` 註記：645–720 s/feature × 37 feature，因 panels 36→66、`feature_values` 2.51M→8.54M）。**先量再改，GATE-keep。**
- **⚠ 一個必須先分離的變數**：現有 645–720 s/feature 是**混合條件下的觀測**——01:30 演化鏈與 TWEVO I3 用兩把不同的鎖（M-O6），每個週間夜必然同時跑，而 `evolution_deferred_work` 有一列 2026-07-27 實錄，reason 逐字寫「重活車道實質被 LLM 臂佔用:llama-server 5.8/12 核、可用記憶體 2GB;I1/I2/I3/I6/I7 延後至臂收尾再跑(避免 OOM)」。⇒ **須在「有／無 LLM 鏈並行」兩種條件下各量一次**，否則剖析結論不可歸因。
- **誰**：AI（剖析）／hugo（M-O6 之編排裁決）
- **前置**：量測須佔 heavy_slot ⇒ **只能排在非 TWEVO 夜**
- **驗收**：兩條件各得一組 s/feature 數字＋其差；改法另立小計畫（#20）。
- **⚠ 未估**：單次量測 ≈1 個 feature ≈12 分鐘，兩條件共 ≈0.5 小時機時；但**四案（M-O6 甲乙丙丁）之量化對照未估**。
- **可並行**：**佔 heavy_slot ⇒ 與 M-T6、TWEVO、M-K4 互斥**。

---

**第 30 步｜M-N17 存量補標（24 份試點 → 外推）＋ M-N3 · M-N5 · M-N6 收束**　🟡／🔴
- **做什麼**：完成 24 份試點 front-matter（其中被 r4 §3.2 具名為過期者標 `superseded_by:`），量出單位成本後決定 501 檔之外推排程；M-N3（`CLAUDE.md:127` 137/137 → 467/467）與 M-N5（GROUNDING-MAP 三列）依裁決落地；M-N6（RULING-042 滾動快照附卷）備卷。
- **誰**：AI（試點與備卷）／hugo（M-N3 依 #19 逐段呈；M-N6 之認定基礎；M-N7 之權威尺）
- **前置**：M-N5 需 M-N7；M-N3 需 #19 呈報；M-N6 需裁
- **驗收**：① M-N3 改為 `<!--lint:CMD_MATRIX-->467/467<!--/lint-->`（機制沿用 GROUNDING-MAP 既有標記）——**禁直接手改為 467**（那只是把一個手抄值換成另一個手抄值）；② M-N6：全 repo 凡引用 042 閘位數字之處皆帶「2026-08-01 快照」限定詞（可 grep 判，現況應命中 ≥1 處無限定詞），且**不得修改 `RULING-2026-042` 正文**（改了即違史述凍結，屬驗收失敗）；③ 全程零既有報告內文變更（`git diff --stat` 中該 24 檔僅前幾行增行）。
- **可並行**：PG-DOC，與第 26–29 步並行。

---

### 階段 4 — 10 月倒推（10-01 至 10-14）：併審備料

---

**第 31 步｜M-W5　98 通道欄位展開 ＋ 權威採認**　🟡🔴
- **做什麼**：`world_channel_binding.source_column` 由 0 填至 98；`world_concept_version` 之 `authoritative_binding_id`＋`decided_by` 落值。
- **誰**：AI（備料）／**hugo 親跑 `decided_by`（AI 絕不代打）**
- **前置**：**M-W2 抽樣 → M-W3／M-W4 裁定粒度 → 本步**。⚠ M-W3 未裁前，`compare_shadow_binding.py:301` 對新路 SQL 一律 `residual_vendor(new_sql)` 回掃 M2 口徑、`:117` 對 `identical_sql` 記 pending ⇒ **即使欄位展開做完，仍只能落 red 或 pending，永遠拿不到 green**（現查 `vendor_binding_strangler_ledger` = **0 列**）。
- **驗收**：① `SELECT count(source_column) FROM world_channel_binding` = **98**（現 **0**）；② `SELECT count(*) FILTER (WHERE authoritative_binding_id IS NULL OR decided_by IS NULL) FROM world_concept_version` = **0**（現 **6**）；③ `SELECT count(*) FROM vendor_binding_strangler_ledger WHERE verdict='green'` ≥ 1（現 0）。
- **時點**：S3 起跑 **08-31**（若此日未起跑，10-14 前完成機率顯著下降【推論】）；S3 完成 **09-30**；S4 親簽窗 **10-05**。
- **可並行**：與第 32、33 步並行。

---

**第 32 步｜M-P10 收束（5 條 manual VE 到期）**　🔴【需裁】
- **做什麼**：5 條 manual `validation_evidence` 之 `valid_until` 為 **2026-10-09／10-10**，距 10-14 併審僅 **4 日**；其中 `E3_promotion_funnel`／`E4_gm_promotion_gap` 連 `last_verified_at` 都是 **NULL**。`chk_ve_manual_expiry` 已上線，到期自動降 unverified。
- **⚠ 不宜留到 10-09 當天才問**——當天處理會在併審前夕製造 5 條 unverified。
- **誰**：hugo（裁）／AI（三案備料）
- **前置**：無（**建議排進 §4 之窗二，本週即裁**）
- **驗收**：`SELECT count(*) FROM validation_evidence WHERE check_type='manual' AND last_verified_at IS NULL` 之處置有書面裁決；到期後無新增 unverified。

---

**第 33 步｜10-10 併審備料定稿**　🟡
- **做什麼**：七項 checklist **各有一個現查值**（**不代勾**，RULING-2026-039 禁假關）。現查 `ULTRACODE-SCHEDULE.md` 七個勾選框**本日仍全 `[ ]`**（WM.35/36 直綁消費禁令生效盤點・025 (iii)(iv)(vi)②③・029 L5 PRV／ASF 日曆復審・L7.16 全棧 owner≠app 矩陣・KDO.4/LDO.4 量測落地・020 M2・GOV-3 B 有無新越權 Evidence），該節自標「到期前不得勾『結清』」。
- **⚠ 覆蓋面**：M-N1 須涵蓋 **13 項**（七框 ＋ 六項同綁該日：RULING-002 主文二／主文五・LDI.7・D-PRIN-2・C1 manual 有效期 10-09/10-10・RULING-012 Phase 7）。現查 `2026-10-14` 於 `constitution/`＋`specs/`＋`docs/compliance/` 命中 **88 處／32 檔**（r4 於同日稍早量到 74 處／27 檔 ⇒ **同一日內漂了 14 處**，手抄必然過期）。
- **誰**：AI（值）／hugo（勾選）
- **前置**：M-N1（第 9/19 步）＋M-W5（第 31 步）
- **驗收**：① `SELECT count(*) FROM treaty_probe_binding WHERE deadline='2026-10-14'` ≥ **13**；② `read_treaty_probes.py --check` rc=0 且每條皆有一列 reading；③ **全部 reading 之 `verdict` 中零筆由 AI 寫入 'meets' 於人裁類框**（可用 `SELECT probe_id,verdict FROM treaty_probe_reading` 核）；④ 留 4 日緩衝。

---

## §3 並行組與車道

### 3.1 十一個車道組（組間全部可並行；組內規則逐條列出）

| 車道 | 互斥資源（單一） | 組內項目與規則 | 可同時開幾線 |
|---|---|---|---|
| **PG-HOOK** | `ops/githooks/pre-commit` | M-G1（S1–S3 含檔頭更正）——**四項同檔，必須同批** | 1 |
| **PG-AUDIT** | `scripts/reconcile_audit.py` | M-G3 | 1 |
| **PG-EVO** | `run_evolution_iteration.py`／`verify_evolution_acceptance.py`／`report_triple_evolution_week.py`／`run_philosophy_evolution.py` | M-T2 → M-G7 → M-E3 →〔待裁〕M-E4；M-E1(甲) 改 `run_philosophy_evolution.py`——**該檔今晚 23:00 由 cron 執行，改動須在 23:00 前完成或推遲到明日** | 1（組內序列） |
| **PG-SIMEVAL** | `scripts/evaluate_sim_calibration.py` | M-M1 → M-M2（＋已關閉之 X1 同檔）——**三項同檔，綁成單一工單** | 1（組內序列） |
| **PG-SIMDDL** | sim 四件套之表／ledger | M-T1（ledger 列＋FK）、M-M3（UPDATE 閘，待裁）——**不同表可並行** | 2 |
| **PG-LINT** | `tools/constitution_lint/`＋`scripts/check_treaty_refs.py` | M-L1＋M-L2 **合單**（同檔）；M-N14（`github-workflow.yml` 檔頭）與 M-L3（`CLAUDE.md` lint）可分線 | 3 |
| **PG-KNOW** | `src/augur/knowledge/auto_admit.py` | M-K2 → M-G15(正名) → M-N9(正名) → 〔待裁〕KH0 JOIN 修法——**四項同檔區，嚴格序列** | 1 |
| **PG-KNOW2** | `retrieval.py`／`backfill_*`／`evidence.py` view | M-K1、M-K3、M-G14、M-K6——**不同檔，可並行**；⚠ 批量 upsert 屬中量層 ⇒ 實際同時最多 2 條 | 2 |
| **PG-DOC** | 各報告／治權相鄰文件（**逐檔互斥，異檔可並行**） | M-N4(`HANDOFF.md`)、M-N13(F2 備料)、M-N16(r0–r3 標頭)、M-N17(`reports/`)、M-L6(對帳)、M-N3(`CLAUDE.md`，待裁) | 6 |
| **PG-NEWFILE** | 無（各自新檔） | M-G2、M-G9、M-G11、M-G12、M-G13、M-G16、M-N1、M-N2、M-N8、M-N10、M-N11、M-N12、M-N15、M-N18、M-M4、M-M5、M-O3、M-O4、M-O5、M-O7、M-O9、M-P13、M-W2、M-W6、M-E7、M-R3 | **6–8**（受 §0.3 輕量層上限） |
| **PG-OPS** | systemd unit／crontab／備份 | M-G4 → M-G5（**硬序列**）、M-G6、M-O2、M-O8——`install_cron.sh` 與 crontab 為**單一資源**，M-G6 與 M-O8 須同批或串行 | 2 |
| **PG-STEWARD** | **hugo 的 TTY** | §4 全部裁決 | **1（定義上不可並行，不可假多人）** |

**組間全部可並行。** 最大可並行度受 PG-NEWFILE 內部與記憶體上限（§0.3）綁定，不受 CPU 綁定。

### 3.2 今晚時窗序列鏈與各時段禁動窗

> **這條鏈本身完全序列；其外的 PG-HOOK／PG-AUDIT／PG-LINT／PG-NEWFILE／PG-DOC／PG-KNOW 可全程並行**，只要遵守下列各時段「禁做」欄。

| 時點 | 事件 | **禁做** | 可做 |
|---|---|---|---|
| **至 19:00** | M-T4 裁決窗（watchdog 尚在冷卻，`dispatch.ts` mtime＝08-02 18:45:56，24h 到期＝18:45:56） | — | 全部車道自由 |
| **19:13:56** | watchdog 態三判定點；若未干預，`audit_selfheal.sh` 起跑（`FINMIND_MIN_INTERVAL=0.7`、6h 牆鐘 → 最晚 01:13） | **此後禁任何額外 FinMind 呼叫**（含「只是探測一下」——#25 說最小單位，但此刻連最小單位都是往已被雙流壓的 IP 上加） | 非 API 之全部車道 |
| **20:00–≈22:30** | arena 全鏈六步（daily_maintenance→sync_macro→derive_market_iv→兩支 builder→run_arena_round）。⚠ 現查 crontab 為 `0 20 * * 1-5`＝**僅平日**（今日週一會跑） | ① 任何 FinMind／FRED 呼叫；② **任何重活**（§0.3 之 (i) 層：M-K4、KH 全量 upsert、pg_dump、panel rebuild）——會與 builder 搶 RAM；③ **任何取 heavy_slot 之作業** | PG-LINT／PG-DOC／PG-NEWFILE 之檔案編輯與 lint（輕量層） |
| **21:30** | arena 結算（實測秒級） | — | 同上 |
| **anchor 到位後、23:00 前** | `run_sim_calibration_cell.py --dry-run`（0.79s，零成本可反覆確認）；確認 §2 第 11 步全綠 ＋ 第 2 步 ledger 列已開後，才按 `--apply` | 在 M-M1／M-M2 未驗收綠、M-T1 ledger 列未開之前按 `--apply` | dry-run 反覆確認 |
| **22:15** | evolve_cycle 起跑（flock LLM 鎖） | ⚠ 若它到 23:00 仍持有 qwen3:8b（RSS 可達 5.5 GB），TWEVO 的 I3 會在低 available 下開跑 ⇒ swap thrash | — |
| **22:5x** | run 22 前置快照（`\copy` 到 `audits/prerun22_pending_snapshot_20260803.csv`）。基線＝pending_auto **17**（全 run 21）、superseded **0** | — | 唯讀 |
| **23:00–≈08:30 隔日** | TWEVO run 22 持 heavy_slot（實測一輪 ≈9.5h） | ① 一切重活；② 一切對 `evolution_*` 表之寫入；③ **改 `run_evolution_iteration.py`／`verify_evolution_acceptance.py`／`run_philosophy_evolution.py`**（跑到一半換碼＝結果不可歸因） | PG-LINT 治權 lint（純文字、不碰 DB）、PG-DOC |
| **01:30–≈03:21** | 演化鏈（harvest ×4 ＋ evolve_self_seek ×2 ＋ evolve_cycle）與 I3 並行——**結構性，今晚不修**（M-O6） | — | — |
| **03:30／04:00** | embed-catchup／ata-advance（`sentence_transformers` e5-small on CPU，**不入 Ollama 鎖、不入 heavy_slot**，是獨立的第三條 CPU 消費者） | knowledge 車道之批量作業不宜排此段 | — |
| **隔晨** | runbook 四項機械檢查（見 §2 第 8 步驗收） | — | 全部恢復 |

### 3.3 排程既有佔用全表（供後續排班直接引用，避免重查）

**crontab（現查 15 行，`crontab -l | grep -c '^[0-9*]'`＝15；`install_cron.sh --check` rc=0「✓ 一致」）**：

```
01:30 每日      演化鏈 run_evolution_chain.sh          〔flock -n LLM 鎖；不取 heavy_slot〕
04:15,10:15,16:15,22:15  evolve_cycle                 〔flock -n LLM 鎖〕
45 */6         evolve_self_seek                        〔flock -w 3600 LLM 鎖〕
08:00 週一      維運健檢                                〔⚠ 呼叫 /usr/local/bin/ollama 不存在，M-O8〕
08:40 週一      三支 MCP --selftest ＋ gpu_verify        ◄── M-O4 掛此
20:00 週間      FinMind 讀錶 ＋ arena 全鏈               〔實測 07-31 跑到 22:27，≈2h27m〕
21:30 週間      arena 結算                              〔秒級〕
:17 每 2h      Steward 提問帳本
:37 每 2h      DESKTOP 增量拉取
09:00 週日      三軸週儀表                              ◄── M-G7／M-M4／M-O9 掛此
07:10 每日      證據帳本重驗（sql 型）
07:40 週日      證據帳本重驗（含 script_exit 型）
07:30 週六      pg_dump -Fd -j4                         〔實測 352 秒；#30 DDL 禁窗僅約 6 分鐘＋鏡像〕
09:00 週六      RAWEVO                                  〔現查不取 heavy_slot〕
23:00 週間      TWEVO --slot-wait 10800                 〔取 heavy_slot，實測 9.5h〕
```

**systemd user timers（現查 8 個）**：

```
augur-drain-deferred      每 30 分   〔潛在 heavy_slot 索求者；現查積壓 0 列〕
augur-audit-watchdog      每 30 分   〔現查 LAST 10:13:56／NEXT 10:43:56 ⇒ 打點 :13:56/:43:56〕
augur-embed-catchup       03:30      〔e5-small CPU，不入任何鎖〕
augur-ata-advance         04:00      〔同上〕
augur-admission-assist    05:00      〔flock -n LLM 鎖〕
augur-l2-deliberation     06:15      〔flock -n LLM 鎖〕
augur-knowhow-refresh     週日 04:30 〔現空轉，M-G8；NEXT=2026-08-09 04:30〕
launchpadlib-cache-clean  （非本專案）
```

> **空窗結論：週間 10:00–18:00 是全天唯一沒有任何本專案排程的時段** ⇒ 一切重活（M-K4、M-K2 全量 upsert、M-R3 剖析）與 DDL（M-T1 FK、第 21 步批次）應排在此。

**本計畫新增排程數＝0**（M-G7／M-M4／M-O4／M-O9 全部掛既有班次）。**這是刻意的：新排程是新的失效面，且會擠壓上述唯一空窗。**

### 3.4 撞檔護欄（M-P1 未裁前之規避）

#34「平行度預設拉滿」之三項硬邊界（配額護欄／OCV 棘輪／#33）**不含撞檔**；唯一撞檔護欄活在記憶檔 `no-concurrent-agents-same-files`。**本檔已用工單分組規避，成本為零、不需等 M-P1 裁決**：

| 撞檔面 | 涉及項 | 規避方式 |
|---|---|---|
| `scripts/evaluate_sim_calibration.py` | M-M1 · M-M2（＋X1） | 綁成 §2 第 11 步單一工單 |
| `scripts/check_treaty_refs.py` | M-L1 · M-L2 | 綁成 §2 第 12 步合單 |
| `scripts/run_evolution_iteration.py` | M-T2 · M-E4 | M-E4 待裁 ⇒ 今日僅 M-T2；日後恢復時須串行 |
| `src/augur/knowledge/auto_admit.py` | M-K2 · M-G15 · M-N9 · KH0 JOIN | PG-KNOW 組內嚴格序列 |
| `install_cron.sh`／crontab | M-G6 · M-O8 | PG-OPS 同批或串行 |

**⚠ 若本計畫 fan-out 執行，編排者必須明示每條線的檔案集，不可依賴規則保護。**

---

## §4 待 Steward 裁決總表（依阻塞程度排序）

> **AI 於此類事項僅得草擬、比對與呈案**（`AUGUR-MC v1.6 §8.1`／`AUGUR-L6 v1.2` L6.18(a)）。**本檔未代裁任何一項、未預設任何答案、未代簽任何 `decided_by`／`approved_by`／`promoted_by`、未代勾任何 10-14 日曆項**（RULING-2026-039 禁假關）。
> **「證偽條件」欄**＝什麼樣的事實會推翻本檔對該項急迫性的判斷（供 Steward 檢驗 AI 的呈案，而非相信它）。
> **阻塞度**：🔴🔴🔴＝卡住 ≥3 項且有硬時窗｜🔴🔴＝卡住 ≥2 項｜🔴＝卡住 1 項或無下游

### 4.1 窗一（今日 19:00 前，≈5 分鐘）

| ID | 待裁 | 阻塞 | 建議案（AI 呈案，不預裁） | 證偽條件 |
|---|---|---|---|---|
| **M-T4** | 今晚 ≈19:13:56 watchdog 發車 FinMind 放量，與 20:00 arena 對撞 | 🔴🔴🔴 卡 arena 入庫 → sim anchor → 21 交易日時鐘（不可回收） | 三案並陳：(甲) 19:00 前手動跑一次 audit 使 `fresh_pass≥1`（挪到白天、不重疊，但仍是放量）；(乙) `touch /tmp/augur_audit_dispatch.ts` 延後 24h（零 API、最小干預，但繞過看門狗設計）；(丙) 不干預，20:00 後見 403 即停。**AI 不代選**——(乙) 觸碰監督機制之計時器 | 若 19:00 前實查 FinMind 時錶餘裕充足（本輪**未查**，唯讀輪禁 API），則雙流風險大幅下降、(丙) 成本可接受；若 watchdog 之 `COOLOFF_H` 實為其他值，則發車時點推算失效 |

### 4.2 窗二（今日 23:00 前 ＋ 本週內，≈35 分鐘）

| ID | 待裁 | 阻塞 | 建議案 | 證偽條件 |
|---|---|---|---|---|
| **M-T3** | 晉升單位＝feature 還是 (principle, feature)？今晚 23:00 前是否先開人裁窗消化 17 列 | 🔴🔴🔴 卡 §2 第 5 步、第 8 步、M-E1、M-E2 | 呈 17 列逐列 `gate_json` 摘要；兩路：(a) 23:00 前逐顆處置；(b) 明示接受 run 22 自動 supersede 後重新產列並留痕 | 若 `_supersede_stale_pending` 之謂詞實際有 action 條件（本輪讀為「不分 action」），則 16 筆 demote 不受影響、僅 q555 一顆有爭議 |
| **M-P11** | 「帳本表不掛 honesty trigger」之射程（08-03 已就 `vendor_binding_strangler_ledger` 併裁不掛，是否延伸至其他 **30 張**零 trigger 治權味表？） | 🔴🔴🔴 **一裁解鎖三項**：M-M3（sim 三表）＋M-P12(b)（VE/attestation）＋M-N1 新表 | 要害四張：`attestation_result`(**9** 列)／`validation_evidence`(**19** 列)／`model_registry`(16 列)／`knowhow_auto_admit_gate_change`(**0** 列)。(甲) 不延伸 → 四張補閘；(乙) 延伸 → 成為可引用通則 | 若這四張表另有非 trigger 之寫入保護（本輪查為零 trigger、`augur` 為 superuser、`decided_by` 零 CHECK），則急迫性下降 |
| **M-O1** | runaway psql backend **pid 217629**（active **2 天 17:11**）是否 terminate | 🔴🔴🔴 **knowledge 車道整條之上游阻斷器**：卡 M-K4 收益、卡四張 knowledge 表之任何 DDL | 三案：(甲) 立即 `pg_terminate_backend(217629)`；(乙) 先找出持有者（tty/session）再收；(丙) 保留並接受 knowledge 車道本週不做 DDL。⚠ 屬 #6 破壞性，AI 不代殺 | 若該 backend 是 hugo 正在跑的長查詢且結果有用，甲案即為破壞；若 `statement_timeout`／`idle_in_transaction_session_timeout` 實非 0（本輪查為 0），則它會自己收 |
| **M-P3** | worktree 是否為 #13 允許之工作場所 | 🔴🔴 卡 M-G1 之 S4；三項減損屬 OCV 單向棘輪 | (甲) 禁止在 worktree 起實作型 session；(乙) 允許但強制先同步治權檔＋hook fail-closed；(丙) 其他。**實測三項減損**：過期治權檔（本檔即在 v1.32 環境產出）、失去 project-memory recall、五閘靜默跳過 | 若 M-G1 之 S1–S3 完成後三項減損全部消失，則本項降為文字補正、不再是棘輪議題 |
| **M-N7** | vendor 直綁**四把尺**之權威尺選定 | 🔴🔴 卡 M-N5、M-W6 基線、M-P（清償配額）；**唯一綁硬期限者** | 建議 `check_vendor_binding --scan` 為權威尺（唯一涵蓋 `quoted_table_esc` 承載形者，而該類正是 08-03 補洞所揭露的盲點；現查 **56 檔·172 處**，rc=1，`caliber_sha256=0e0e608f75122bf5`），其餘三處（37／47／50）標史料加時戳 | 若 WM.36 之義務對象經解釋為僅限「表名字面」而不含 esc 承載形，則 142 之 quoted_table 為真分母、26 之 esc 不計 |
| **M-P10** | 5 條 manual VE 於 10-09／10-10 到期後之處置 | 🔴🔴 到期距併審僅 **4 日**；其中 2 條 `last_verified_at` 為 NULL | (甲) 重簽（人審）；(乙) 轉為可機械化之 `sql` 型；(丙) 逐條分流。**宜先裁，不宜留到 10-09 當天** | 若 `chk_ve_manual_expiry` 之到期行為實為「自動降 unverified 且不阻塞任何下游」，則可留到 10-09；本輪未驗其下游效應 |
| **M-P16** | `RULING-2026-043` 簽核欄（現 `[ ]`） | 🔴🔴 卡 M-L6 之射程對帳；11+ 張表之閘架構法源 | 本體已建（`c9575f3`，79 行，AL-2026-047 已入 `AMENDMENT-LOG:487`）；檔內 `:69` 自陳「簽核前，引用應讀為『編號已指配、本體待簽』」。**hugo 親簽，AI 不得代簽** | 若 Steward 採「圈選留痕即為完整裁決、不編號」（原 S-2 乙案），則應清除碼內 17 處字樣、改引呈案檔路徑，本項轉為清理工項 |

### 4.3 窗三（08 月中，≈60–90 分鐘）——判準與解釋族

| ID | 待裁 | 阻塞 | 建議案 | 證偽條件 |
|---|---|---|---|---|
| **M-W3** | 當「權威表徵」本身就是 vendor 表時，「不得以來源位置字面直接繫結」之解除判準為何 | 🔴🔴🔴 **WM.36 弧之關鍵路徑瓶頸**：卡 M-W5、M-N5；不裁則 M3 絞殺**結構上永遠拿不到 green** | 現查 `world_channel_binding` 10 條 mapped 通道之 `source_table` **全部是 vendor 表名**（tw.trading_calendar→TaiwanStockTradingDate、tw.delisting→TaiwanStockDelisting）；`compare_shadow_binding.py:301` 對新路 SQL 一律 `residual_vendor()`、`:117` 對 `identical_sql` 記 pending。三案：(甲) 引入 schema view／別名層；(乙) 認定「經 registry 解析取得表名」即已合規、改 residual 判式；(丙) 其他。屬 `specs/WORLD-MODEL-SPECIFICATION.md:344-358` 之條文解釋 | 若 registry 之設計原意即為「解析層存在即合規」，則乙案為原意還原而非判準變更；若 M2 口徑另有未被本輪讀到的例外條款，則瓶頸不成立 |
| **M-W4** | WM.36「series 識別碼」之射程是否含表內列鍵（`stock_id='TAIEX'`／`option_id='TXO'`） | 🔴🔴 卡 M-W5 之展開粒度（做錯順序會返工）；且現行止血閘**根本不量列篩選字面** ⇒ 基線 172 處是**低估、幅度未知** | 現查消費點：`run_arena_round.py:96,112`／`build_market_direction_features.py:53`／`train_daily_direction.py:82`／`build_daily_direction_features.py:49`／`verify_arena_watchlist.py:131` 全帶 `WHERE stock_id='TAIEX'`；同型見 OptionDaily 之 `'TXO'`＋`trading_session`、法人表之 `name`、HoldingSharesPer 之 `HoldingSharesLevel`。若含，則 registry 需第八欄（列選擇述語）或概念鍵須細到 `tw.index.taiex`；若不含，**須明文記載以免下一輪重新爭論**。與 M-W3 **宜併案** | 若禁令原文之「series 識別碼」有既存定義明確排除表內列鍵，則本項不成立、僅需備註 |
| **M-N12／Q12** | TWEVO 之「什麼算進步」（`compare_gain` 要求 `dual_green_n` 逐輪嚴格遞增） | 🔴🔴 **今晚 run 22 起有實質倒數**：現查 run21 `dual_green_n`＝**2**、八閘全綠列＝**3**；`prodset_delta` 在人閘模式下**結構恆 0** ⇒ 若停在 2，**三輪後即 `stopped_no_gain`** | 先建雙報探針（M-N12，AI 可為）使裁決有資料。此變更會改自動鏈的停手時點 ⇒ 觸 #26 自動鏈上限之**單向棘輪四項對照聲明** | 若 run 22 之 `dual_green_n` 自然升到 3+，倒數解除、可從容裁；若 I1/I2 接線（M-P14）獲准，則成長來源恢復 |
| **M-E5／Q18** | 是否開啟 cron `--allow-apply`；整批路是否也經武裝閘 | 🔴🔴 **在 M-E5 未修前開啟＝啟用無武裝閘的整批路**——現查該路徑一句即 `applied=17` | driver 不把 `--allow-apply`／`--gate-ref` 傳給子行程（`:251-256`），子行程走 `queue_id=None` 分支（`apply_evolution_promotions.py:73` **直接 return True**）。現行刻意不帶（`install_cron.sh:71-77` 記明理由） | 若 `single_apply_gate` 在 `queue_id=None` 時實另有其他檢查（本輪讀為直接 return True），則整批路並非無閘 |
| **M-G16／Q7** | trigger 改 `ENABLE ALWAYS` 算不算「升嚴」而須走 GATE-raise | 🔴🔴 卡全部「硬閘」宣稱之強度上限；10-14 併審會據此認定 L7.16 現行承載 | 現查 116 支全 `'O'`、`'A'`＝**0**；`session_replication_role='replica'` 無 DDL、無鎖、schema 無差異、**事後 `tgenabled` 仍是 `'O'`、鑑識查不到痕跡**（≠`DISABLE TRIGGER`）。`ENABLE ALWAYS` 是不動角色架構下**唯一**能實質提升強度的手段；但它不動判準文字、只讓判準更難繞 ⇒ 屬執行層硬化還是判準變更須 §8.1 解釋 | 若專案另有非 superuser 之寫入路徑（本輪查為單一 superuser `augur`），則現行強度並非全靠紀律 |
| **M-L7／S-1** | `constitution_lint --selftest` 之 G10 界線 FAIL 如何處置 | 🔴🔴 **291 條治權斷言零自動觸發點**；連帶 CI 全面接線 | 現跑 `--selftest` rc=**1**，FAIL **恰 1 條**＝「G10 界線：`### TR.Z …（DRAFT）` 之殘留不由本檢查代 Steward 認定」。三案：(甲) 認定 linter 不應報紅 → 修斷言；(乙) 認定應報紅 → 先更正各規格 TR.Z 殘留或依 §8.4 核發有到期日豁免；(丙) 標 known-issue（`--allow-known-fail`＋audits 留痕）後掛閘。⚠ **掛了會使 repo 立即不可 commit** | 若 TR.Z 之 DRAFT 標記在規格內另有明訂效力（本輪未逐條讀 51 份裁決正文），則甲乙其一為原意還原 |
| **M-N9／Q6** | KH0 對無原文 item 之通過條件（v1.53.0「標題即有語意」之條文解釋） | 🔴🔴 卡 KH0 之**永遠紅、且紅得不會變綠**——現查破口 138,875／285,227（**48.7%**），兩個唯一 state 產生者都硬性要求有全文（`auto_admit.py:719` INNER JOIN／`ingress_kip.py:92` EXISTS）⇒ `--phase advance` 只能關 **49** 件（0.035%） | (甲) 進得來、判 fail 亦可，破口即關；(乙) 有標題即 pass（會讓 13.8 萬件一次進入推進池）。**恆紅閘會在一個月內喪失訊號價值**（r4 D10 之明文預測） | 若 `evaluate_layer(0)` 之 `has_text` 有其他資料來源（本輪查為只看 `knowledge_item_text`），則破口可由第三路徑收斂 |
| **M-N6／Q9** | 10-14 併審以何為 L7.16 現行承載之依據 | 🔴 卡 M-N6、10-14 第四項 | `RULING-2026-042 §二2` 記「delete_only **23** 表／ledger_guard **5** 表」，現查為 **9 表／25 表**（**方向完全反轉**，B4-P2a/P2b 所致）。依大憲章 v1.51.0 通則一**史述凍結，正文不得改** ⇒ 唯一合法解是另附滾動快照。(甲) 以 08-01 快照為基礎；(乙) 以滾動快照為基礎 | 若 v1.51.0 通則一之「史述凍結」不及於附表數字（本輪讀為及於正文全部），則可直接更正 |
| **M-L4／Q5** | CS-系統核心思想之 open-tension 是仍未裁還是已被吸收 | 🔴 卡 10-14 前之合規盤點 | 同一檔正文載「幅度級 E[r] 於 A.38 閉集之模態定性……**列 open-tension 呈 Steward 裁**」，而 front-matter `open-tensions: []`、CS.2 逐字「`none`」。**以 front-matter 為準即靜默吞掉一項待裁事項**，RULING-2026-039 明文禁假關。AI 不得代為認定其已閉 | 若 P11-high① 之修訂確已吸收該 tension 且有留痕（本輪未查該修訂內容），則 front-matter 為正確、正文為殘留 |
| **M-L5／C4** | MC §0.5 Layer 4 規格名不符（Knowledge **Graph** vs 生效本 **System**） | 🔴 卡治權層機械比對 | `constitution/META-CONSTITUTION.md:59` 逐字「Knowledge **Graph** Specification（AUGUR-KS…）」，生效本標題為《Knowledge **System** Specification》；同節 `:52` 逐字「新增規格必須先在本表登錄所屬 Layer **方生效力**」⇒ 照字面比對會誤得「KS 未登錄」。另 `specs/` 同時存在 `KNOWLEDGE-SYSTEM-SPECIFICATION.md` 與 `-v0.1-draft.md` 兩份同標題檔。**改 §0.5＝改元憲章，§8.1 專屬 Steward** | 若 §0.5 之登錄以 Layer 編號而非規格名為識別（本輪讀為以名），則名不符僅為勘誤、不影響生效力 |
| **M-L8／C7** | `evolution_iteration_ledger` 並存兩條互相包含的 axis CHECK | 🔴 | 現查 `_axis_check`＝`ANY(ARRAY['tw','lai','raw'])`、`_axis_check1`＝`axis='tw'`；同表 `iteration_uid` CHECK＝`^(tw\|lai\|raw)-\d{8}-r\d{2}$`（語意相反）。該表全部 **5 列 axis 皆 'tw'**、無 FK、無資料遷移需求。(甲) DROP `_axis_check1` 恢復三軸；(乙) 保留單軸並同步收窄 uid 正則、**明文承認本表只服務 tw**。屬 #6 破壞性 DDL ＋ 架構判準 | 若三軸實際將共用此表（現況 lai／raw／sim 各有自己的 ledger 表），則甲案為原意 |
| **M-E4／Q16** | `gate_scale` 指紋是否升級（「什麼算可比」之判準輸入） | 🔴🔴 靜默換尺；`compare_gain` 仍宣稱兩輪可比 | `_gate_scale`（`run_evolution_iteration.py:131-153`）只指紋 `min_abs_hac_t` ＋「有無 G-SIGN 鍵」，**未涵蓋** min_seeds／min_panels／min_delta_ic／G-ECON cost·top_frac·max_dd_floor／G-SIGN n_boot_seeds·min_series／since／horizon_h／panel 數。**碼內註解 `:56-58` 已自陳**「縮 `--since` 換 panel 口徑而 `_gate_scale` 看不出來」卻未修 | 若 `compare_gain` 另有 panel 口徑之獨立比對（本輪未查），則指紋窄不必然造成誤比 |
| **M-K5／Q14** | KH7 是逐 item 判準還是庫級前提 | 🔴 6 列 probe 撐 145,952 件 depth 7；**與 KH8 被判死的理由同構** | (甲) 逐 item 化並接受 depth 掉檔；(乙) 明文認定為庫級前提、要求 `layer_scores` 顯式標 `evidence_scope`；(丙) 維持現狀 | 若 KH7 之設計原意即為庫級前提且已有明文（本輪未查得），則僅需正名 |
| **M-E6／Q13** | RAWEVO 的 gain 語意是否為原意（恆為真、永不停損、以 `basis='new_gap'` 繞過對照臂） | 🔴 raw 軸永遠自稱有進步 | `gain = bool(made or true_gap or freeze_gap)`；`basis='new_gap'` 不在驗收器 `METRIC_BASES` ⇒ **用一個自訂名稱繞過對照臂要求**（與 #32(b) 三臂鐵律相衝） | 若 raw 軸之產出本質不適用對照臂（如純結構性補洞），則需明文豁免而非沉默繞過 |
| **M-G13／Q22** | 機器規則可否把 `awaiting_hugo` 改成 `superseded` | 🔴🔴 直落 P5.W2／OCV C 分量（#26 自動鏈上限） | 現查 status 分布 superseded 845／queued_for_claude 270／**awaiting_hugo 159**／pending 151；`resolved_by` 六個值中**無 'hugo'**；`triage='decision' AND status='awaiting_hugo'`＝**159**（即全部 awaiting 皆標 decision）；最舊 `asked_at`＝**2026-06-22**（懸置 **42 日**）；已有 `rules_v3_sweep_awaiting` **2 列**走此路徑 | 若那 159 件主要是會話中的一般提問而非真待裁（r4 G9 之判讀），則名實不符是主要問題、OCV 弱化是次要 |
| **M-G15** | KH1「既有原文＝視同通過」旁路之存廢 | 🔴 100% 通過率之結構根因 | `auto_admit.py:335-360` 逐字 `if snap["has_text"]: return {"verdict":"pass","note":"既有原文＝KH1 視同通過"}`，且 `qualification` 為 reject/error 時只要有原文仍回 `pass`。`knowledge_item_text` **158,532** 列全走旁路。同族於 Q6／Q14 | 若 KH1 之判準原意即為「有原文即通過」（本輪未查得明文），則僅需正名為零變異指標、不得充當獨立證據 |

### 4.4 窗四（穩定後／機會窗）——不阻塞當前任何步

| ID | 待裁 | 阻塞 | 一句話 |
|---|---|---|---|
| **M-R1／Q04** | `direction_gate` 開門條件（降 cluster 門／supersede own_stack／補 h 出單／維持 250） | 🔴 確立級永紅 | 現查 **0/29 evaluated_pass**；arena 自陳 cluster=2/60；`direction_arena_verdict` 0 列 |
| **M-R2／Q05** | LAIEVO 新凍結集＋換尺後首輪 | 🔴 能力宣稱無證據力 | 現查 `local_ai_iteration_ledger` = **0 列**（零輪）；呼應記憶 `eval-boilerplate-floor` 之三臂鐵律 |
| **M-O2(異裝置)／Q26** | 異地備份之目標裝置／路徑 | 🔴🔴 **唯一「一次事故即全專案歸零」之風險** | 現查 `/mnt/c/database/` 空；兩份 11G dump 與 61 GB DB、repo 同碟。屬採購／實體，AI 不自行選定 |
| **M-K7／Q24** | 外部全文抓取之放量節奏 | 🔴 | 90,426＋9,477 件佇列零排程；#29(b) 要求端到端至 license 終態，但 #24/#25 要求受控。建議比照 ata-advance 之 200/日先跑一週 |
| **M-K8／Q15／S-9** | `knowledge_domain_map` 是否納 `erp_tiptop` | 🔴 | 唯一 100% 可答語料（141,873 件）因不在名冊而恆 pending，而 mapped 的 quant_finance 12,414 件反而不可答。**AI 不得自行 INSERT**（#29b） |
| **M-K4／S-7／Q28** | `knowhow_auto_admit_run` 留痕義務範圍 | 🔴 | (甲)「每次評估都留一列」＝誠實要件 → 不可做，改分區/歸檔；(乙)「每個**不同**結果留一列」→ 去重合規。**一旦刪過不可逆** |
| **M-P1／S-4／Q19** | #34 是否增列第 (iv) 項硬邊界「並行以檔案集不重疊為前提」 | 🔴 | 本檔已以工單分組規避（§3.4），不阻塞。**涉 AI 自身監督機制，AI 不得為核准主體** |
| **M-P2／P3-3／Q20** | 三則記憶級規則升格入 CLAUDE.md | 🔴 | `CS-CLAUDE.md:50` 已把 §P5.E1／§P5.W2 落點指向記憶檔，而 **CLAUDE.md 全文對此零字**；DB 層 `decided_by` 零 CHECK、`augur` 為 superuser ⇒ **這是該義務唯一實質防線，卻掛在最易蒸發的一層** |
| **M-P4／Q21** | `guard-mechanisms` 型 6（機器覆寫人裁且無痕）／型 7（凍結判準文字沒凍結實作）是否入憲 | 🔴 | #35 目前只吸收型 3／4；型 6 已實犯 |
| **M-P5／Q2** | 領域治權檔升版是否須登錄 `AMENDMENT-LOG` | 🔴 | 現為分裂雙帳簿（AL 47 條全屬 MC/specs 軸；領域軸八版 0 列入 AL、2 版入 DB）；⚠ **DB 不隨 git 跨機** |
| **M-P6／Q3** | 模擬方法自進化專章 v1.0 是否為 MC §0.5 意義下之「規格」 | 🔴 | 它載實質 [N] 義務句、自稱條文 SSOT，但形制是大憲章第三部之下位專章；無 CS、無 AL、未入 §0.5 |
| **M-P7／Q22** | （同 M-G13） | — | — |
| **M-P8／Q23** | 單一角色整併是否為閘強度之局部回退 | 🔴 | 不可逆、跨治權檔，會重啟已結案的整併。hugo 07-31 曾主動問過，該題現仍在 `awaiting_hugo`。**AI 不得提案回退已結案之架構決定**，只得如實揭露強度上限 |
| **M-P9／Q30** | 07-25 `promoted_by='hugo'` 代打是否構成 GOV-3 B 之新 Evidence | 🔴 | 10-14 checklist 第 7 項即問此事；07-24 盤點結論為「無新 Evidence」，但該事件發生於 07-25 |
| **M-P14／S-8(b)** | 是否接上 I1/I2 讓 `dual_green_n` 有成長來源 | 🔴 | 現有 390,274 列候選（11 feature），且這 11 個正是 `coverage_class='missing'` 而八閘全 SKIP 者。新特徵入生產須走原則精華 #11 第 4 道提拔關卡＋#14 經濟終關 |
| **M-P15** | 「同一時點只能有一則現況權威」是否入規則 | 🔴 | 現查 `reports/` 217/301 份內文含「SSOT／權威／現況」字樣、其中 14 份明文自稱 SSOT。不裁則 M-N17 之稽核器只報不擋 |
| **M-O6／LANE-3** | 01:30 演化鏈與 TWEVO 兩把鎖是否合一 | 🔴 卡 M-R3 之可歸因性 | (甲) 01:30 鏈改取 heavy_slot（TWEVO 夜必然餓死該鏈＝停掉每日知識收割）；(乙) 挪到 TWEVO 結束後（≈09:00）；(丙) 維持現狀、明示接受 I3 夜間降速為設計；(丁) 兩鎖合一為單一「本機重活」鎖。**改自動鏈編排 ⇒ 觸 #26 OCV 四項對照聲明** |
| **M-O10／Q20(exec)** | DESKTOP 並行機／跨庫 drift | 🔴 | 數字雙真相；週末機會窗 |
| **M-O11／Q27** | `augur_sandbox` 之治權定位（34 MB／14 表／17 處引用） | 🔴 | 記憶「終態＝只剩一個庫」已不成立（現查 **3 個庫**）；該庫不在 HANDOFF／README／備份範圍，隔離靠什麼保證不明 |
| **M-R4／Q14(exec)** | I6 是否接 `train_ranker` | 🔴 | 晉升不進熱路徑；**≠可交易** |
| **M-R5／Q15(exec)** | `path_gate` 三表收斂 | 🔴 | 觸 ≥3 package ⇒ **須 #20 另立計畫書**，不在本檔射程 |
| **M-R7／Q17(exec)** | PME-XDOM-SOLAR 等 APPLY | 🔴 | 僅 `PME-APPLY-go`∧雙綠；閘外 |
| **M-R8／Q09(exec)** | TWEVO close 判準（重試成功仍記 failed） | 🔴 | 產能帳失真；(甲) 雙欄 (乙) 洗敗 |
| **M-E1(乙)／Q11** | `map.direction ≠ canonical ⇒ 直接 FAIL_SIGN`；及 07-29 新增之 p123 兩列方向與 07-28 裁決相反如何處置 | 🔴 | (甲) 依裁決改方向；(乙) 撤下 map 列；(丙) 承認同一 feature 可承載多方向假說、改為逐 (principle, feature) 裁方向 |
| **M-N15／M-N17 之權威規則** | （同 M-P15） | — | — |
| **M-K6** | `knowledge_access_audit` 是否補真軌跡 | 🔴 | 66 列、最後 07-06、檢索路徑零寫入 |
| **M-N10 例外確認** | 12 張裸 UPDATE 表中哪些屬設計性例外 | 🔴 | `entity_registry`／`entity_alias` 之 UPDATE 全裸是**設計如此**（`identity_no_delete` 例外訊息逐字寫「下市/去識別化以 UPDATE status=tombstoned 標記」）。**把 12 張一律當缺口會做出錯誤的補閘提案**（r4 T8） |
| **M-N3** | `CLAUDE.md:127` 之 137/137 修正（依 #19 逐段呈） | 🔴 | live **467/467**。⚠ **禁直接手改為 467**，須改為 lint 綁定 |
| **M-L2 正文／M-L3 清償** | 大憲章修訂表雙現行之正文修正；條號前綴 14 例逐處補 | 🔴 | 皆屬「文字改正確」但依 #19 宜逐段呈 Steward 過目 |

**統計**：窗一 **1** 項｜窗二 **7** 項｜窗三 **16** 項｜窗四 **26** 項（含 2 項與前重複之交叉引用）＝**共 36 個獨立待裁節點**（去重後）。

**hugo 車道之總量誠實揭露**：另有 `steward_question_ledger` **awaiting_hugo 159 件**（最舊懸置 **42 日**、`resolved_by='hugo'` 恆 **0**）與 L2 人裁積壓 **180 件**，**不含在上述 36 項內**——那是另一條獨立節奏（M-G13 之射程）。

---

## §5 硬期限倒推表

> **本專案只有三條真正的硬期限**：一條外部（10-14／10-15），兩條物理不可壓縮（sim 三格 × 21 交易日、TWEVO 週輪）。其餘一切「急」都是可協商的（排序原則二）。
> **「為何是這個時點」欄**＝該時點的機械依據，不是感覺。

### 5.1 今日至本週（2026-08-03 至 08-09）

| 時點 | 里程碑 | 為何是這個時點 | 對應步 | 錯過的後果 |
|---|---|---|---|---|
| **08-03 19:00** | M-T4 裁決 | `dispatch.ts` mtime＝08-02 18:45:56 ＋ `COOLOFF_H=24` ⇒ 18:45:56 到期；watchdog 打點 `:13:56`／`:43:56` ⇒ **第一個 tsage≥24h 的打點＝19:13:56** | 第 4 步 | 雙流 FinMind（≈2.5 vs 安全值 1.1 req/s）→ 403 → arena sync 掛 → **sim anchor 不實現 → 21 交易日時鐘平移一天（不可回收）** |
| **08-03 20:00** | arena 全鏈起跑（`0 20 * * 1-5`，僅平日） | 收盤資料入庫、sim anchor 實現之唯一路徑 | 第 3.2 節 | 同上 |
| **08-03 `--apply` 前** | M-T1 ledger 列已開 ＋ M-M1／M-M2 驗收綠 | `sim_run_link` 有 `simlink_no_delete` trigger ⇒ **首格 52 列一落地，孤兒 uid 永久不可刪** | 第 2、11 步 | 成本由「開一列」變成「回填遷就已寫死的 uid」（形同追溯粉飾）或永遠加不上 FK |
| **08-03 23:00** | M-T2 修完 ＋ M-T3 定序 ＋ heavy_slot 淨空 | TWEVO cron `0 23 * * 1-5`；I5B supersede **首次生效點**；一輪持鎖 ≈9.5h | 第 3、5、6 步 | M-T2：又一輪恆亮假告警（**可逆**）；M-T3：17 列 queue_id 全換號、人裁窗找不到目標（**不可逆**） |
| **08-09 04:30** | `augur-knowhow-refresh` 下次空轉窗 | 現查 timer NEXT＝Sun 2026-08-09 04:30（⚠ **兩份計畫皆記「02:00 週日」，與 live 不符**） | 第 13 步 | 102,039 筆 pending 再累積一週，而 unit 準時 Finished、journal 自陳「待辦(前) 0」 |
| **08-09（本週末）** | M-G1／M-G3／M-G7／M-G8 完成；**M-N1 產出今日基線值** | **基線越晚建，能觀察到的 diff 越少**——同一日內已量到三處漂移（vendor 128→130／10-14 命中 74→88／memory 索引） | 第 1、9、10、13 步 | 過期族每輪重新長出（r0→r4 已重做五次全量現查） |

### 5.2 每週固定窗（排班時必須避開）

| 週期 | 事件 | 禁動 | 實測時長 |
|---|---|---|---|
| 週一至五 23:00 → ≈08:30 | TWEVO run（持 heavy_slot） | 一切重活；改進化 driver 檔群 | **9.5h**（run20 09:52:14／run21 09:30:34） |
| 每日 01:30 → ≈03:21 | 演化鏈（不取 heavy_slot，M-O6） | knowledge 車道批量 | 1h51m |
| 每日 03:30／04:00 | embed-catchup／ata-advance（e5-small CPU，不入任何鎖） | 同上 | — |
| 週六 07:30 | `pg_dump -Fd -j4 -Z1` | **DDL（#30 鎖風暴）** | **352 秒**（11 GB／2696 物件）——遠短於記憶檔「15-20 分」之估計 |
| 週六 09:00 | RAWEVO（現查不取 heavy_slot） | 重活 | — |
| 週日 09:00 | 三軸週儀表 ◄ M-G7／M-M4／M-O9 掛此 | — | — |
| **週間 10:00–18:00** | **全天唯一空窗** | — | ⇒ 重活與 DDL 一律排此 |

### 5.3 10-14／10-15 倒推（距今 **72 日**，現查 `python3 -c` 實算）

| 時點 | 里程碑 | 為何是這個時點 | 現查基線 |
|---|---|---|---|
| **08-23** | M-N1／M-N2 探針入週報；治權 lint 族（M-L1／M-L2／M-L6）完成 | 留 7 週給欄位級映射 | `treaty_probe_*` 表不存在；`measure_registry` 不存在 |
| **08-31** | **M-W5 S3 起跑**（98 通道 × 欄位級展開） | 【推論】若此日未起跑，10-14 前完成機率顯著下降。**M-W2 抽樣（第 25 步）之產出即是把此推論變成機械結論** | `source_column` **0/98** |
| **≈09-02** | sim 格 1 落地（anchor + 21 交易日） | 物理不可壓縮 | `sim_run_link` **0 列** |
| **09-30** | M-W5 S3 完成 | 留 2 週給 S4 人簽 | 同上 |
| **≈10-02** | sim 格 2 | 不可壓縮 | — |
| **10-05** | **M-W5 S4 hugo 親簽窗**：`authoritative_binding_id` ＋ `decided_by` 落值 | **AI 絕不代打**；須排 hugo 的時間 | `world_concept_version` **6/6 皆 NULL** |
| **10-09／10-10** | 5 條 manual `validation_evidence` `valid_until` 到期 | `chk_ve_manual_expiry` 已上線；**距併審僅 4 日** | 其中 2 條 `last_verified_at` 為 **NULL**（從未被檢驗）|
| **10-10** | 併審備料定稿；**不代勾任何 checklist 項** | 留 4 日緩衝 | 七框全 `[ ]`；`2026-10-14` 命中 **88 處／32 檔** |
| **2026-10-14** | **Steward 併審**（七框 ＋ 六項同綁項＝13 項） | 外部硬期限 | RULING-2026-039 禁假關 ⇒ **任何漏項不能事後補勾** |
| **2026-10-15** | **WM.36 起無條件適用** | 該日起直綁消費禁令自動生效 | 現存量 **56 檔·172 處**（權威尺待 M-N7 裁）；`vendor_binding_strangler_ledger` **0 列** |

⚠ **關鍵路徑警告**：M-W3（M3 絞殺判準結構不可達）**在 M-W5 之前**。現查 `world_channel_binding` 之 10 條 mapped 通道 `source_table` **全部是 vendor 表名** ⇒ 即使 S3 欄位展開做完、S4 親簽完成，`compare_shadow_binding` 仍只能落 red 或 pending。**M-W3 不裁，10-14 那一格解不開。**

### 5.4 sim 校準時鐘（不可壓縮鏈）

```
anchor(08-03 收盤後) ─21td─► 格1(≈09-02) ─21td─► 格2(≈10-02) ─21td─► 格3(≈11-04)
                                                                        └─► K=3 齊 → evaluate → M-M5 verdict
```

| 時點 | 動作 | 現況 |
|---|---|---|
| 今晚 | runner `--apply`（**人工，非 cron**——M-T7） | 前置＝第 2 步＋第 11 步 |
| ≈09-02 | settle 第一波 | **⚠ `settle`／`evaluate` 兩步完全未入 runbook**（`ops/RUNBOOK-20260803-night.md` 只寫到今晚的 runner）⇒ M-M4 補 |
| ≈10-02／≈11-04 | settle 二、三波 | catch-up 冪等只保證「晚跑不掉格」，**不保證「有人會跑」** |
| ≈11-04 後 | evaluate → M-M5 verdict | `sim_evolution_verdict` **0 列**、全 repo **零 writer** |

**「發現越晚，已浪費的等待越不可回收」**——這正是 X1（q_grid 契約）今日修的價值：若 11 月 K=3 齊了才發現，成本是**重跑一整季的時鐘**，而 `run_id` 因 `ON CONFLICT DO NOTHING` 且不含 code 版本，已產列還改不了形狀（r4 T7）。

---

## §6 明確不做（防後人重提）

| 不做 | 為何（機械依據） |
|---|---|
| **改 `RULING-2026-042` 正文之閘位數字** | 該裁決已簽生效，依大憲章 v1.51.0 通則一**史述凍結**。其 §二2 記「delete_only 23 表／ledger_guard 5 表」，現查為 **9／25**（方向反轉）——**這是正確的、不該改**。正解是另立滾動快照並在 10-14 議程標明「042 §二2 為 08-01 快照」（M-N6） |
| **把 `constitution_lint --selftest` 現在就掛 pre-commit** | 現跑 rc=1，唯一 FAIL＝G10 界線。**掛了會使 repo 立即不可 commit**。且該 FAIL 是條文解釋、專屬 Steward（M-L7）。hook 標頭之誠實註記已記此為刻意 |
| **安裝 `tools/constitution_lint/github-workflow.yml` 為 CI** | 同上（selftest 未綠）。但**須更正該檔頭之過期阻斷理由**——檔頭載「WM.44-LABEL 尚有未結之 error」，而 live 實為 **WM.44-LABEL error＝0**、真阻斷是 G10（M-N14） |
| **恢復非 superuser 寫入角色（回退單一角色整併）** | 唯一能根治 M-G16 的手段，但屬**不可逆、跨治權檔**之架構決定，會重啟已結案的整併。**AI 不得提案回退已結案之架構決定**，只得如實揭露強度上限（M-P8 由 hugo 自決） |
| **接上 I1/I2（`feature_candidate_values` → 漏斗 → `feature_values`）** | 現有 390,274 列候選（11 feature）躺著，且這 11 個正是 `coverage_class='missing'` 而八閘全 SKIP 者。**這是 `dual_green_n` 唯一可能成長的來源**，但新特徵入生產須走原則精華 #11 第 4 道提拔關卡＋#14 經濟終關，**不得由 driver 逕自擴權**（`run_evolution_iteration.py:75-79` 射程聲明已明示此界）⇒ M-P14 |
| **自行 INSERT `knowledge_domain_map`（納 erp_tiptop）** | 該表語意是「決策層拍板域的機械名冊、納新域＝人 INSERT 一列」（#29b）⇒ M-K8 |
| **開啟 cron 的 `--allow-apply`** | 現行刻意不帶（`install_cron.sh:71-77` 記明理由）。**且在 M-E5 未修前開啟＝啟用無武裝閘的整批路**——現查該路徑一句即 `applied=17`（含 16 筆 FAIL_SIGN demote ＋ 1 筆 promote） |
| **為 KH8 調鬆 `MIN_MINORITY_MASS`** | 現查 `population_discriminates` → ok=**False**（`band_minority_mass`＝0.0027 ≪ 0.05）。**改 0.02 仍 fail**（雙重冗餘）。調閾值以求綠燈＝挪門柱，正是本專案零容忍者 |
| **代勾任何 10-14 checklist 項** | RULING-2026-039 禁止假關。探針只產生**值**，勾選是 Steward 的動作（第 33 步驗收 ③ 即機械檢查此事） |
| **新增排程** | 本計畫新增排程數＝**0**，全部掛既有班次。新排程＝新失效面，且會擠壓週間 10:00–18:00 這個唯一空窗 |
| **代打任何人簽欄位** | `promoted_by`／`approved_by`／`decided_by`／`signed_by` 一律 hugo 親跑（記憶 `never-type-human-signature`）。DB 層已證 `decided_by` **零 CHECK**、`augur` 為 **superuser** ⇒ **這條規則是該義務唯一實質防線** |
| **回頭改既有報告／裁決之正文** | M-N16／M-N17 只加 front-matter 與索引，不動內文（史述凍結之延伸慣行；r4 §3.2 已立「引用時加限定詞、不改正文」） |
| **把本 [I] 計畫貼進憲章** | 本檔為 L6 以下之執行文件，不創設判準 |
| **自訂任何「須公示 N 日方生效」之要件** | 本專案為 Sole Steward 專案；CLAUDE v1.31 已明文禁止 AI 新訂此類要件，且強制公示條款已於 2026-07-23 經 `RULING-2026-031` 廢止 |
| **依 #34 字面把三組同檔項拆給多 agent** | §3.4 已識別五個撞檔面並以工單分組規避。#34 三項硬邊界不含撞檔，M-P1 未裁前**不可依賴規則保護** |
| **在 M-O1 未解前對四張 knowledge 表做 DDL** | pid 217629 持 AccessShareLock 已 2 天 17:11；ACCESS EXCLUSIVE 會排隊並依 #30 引發鎖風暴（症狀＝全庫查詢突然 hang） |
| **把 M-K4 排在 M-O1 之前** | xmin horizon 凍在 07-31 ⇒ **刪掉的空間根本回收不了**（vacuum 拿不到 horizon）。這條依賴兩份計畫都沒寫 |

---

## §7 驗收與里程碑

### 7.1 五個里程碑

| 里程碑 | 時點 | 完成定義（**全部機械可判**） |
|---|---|---|
| **M0　今夜保住三件事** | 08-04 隔晨 | ① `sim_run_link` LEFT JOIN ledger 之 NULL 列＝0（**且首格已落地故非 trivially 0**）；② driver 印「積壓 **0** 列」（現 9）；③ `promotion_queue` 首次出現 `superseded` 列（現 **0**）且 `evolution_run` 最新列 status＝`succeeded`；④ `~/logs/arena_pipeline.log` 無 403 且 `TaiwanStockPriceAdj max ≥ 2026-08-03` |
| **M1　紅燈會亮** | 08-09 | ① worktree 內 `bash ops/githooks/pre-commit` rc≠0 且印五閘名（現 rc=0＋「略過」）；② `check_worktree_treaty_sync --check` 由紅轉綠（三 worktree 由 v1.31/v1.32/v1.31 同步至 **v1.35**）；③ `coverage_gap=True` fixture → `passed=False`（現 True）；④ 三支掃描器之根目錄指向不存在路徑時**各自 rc≠0**（現三支皆 rc=0）；⑤ 新哨兵對 TRI 報紅（現落後 **17 個交易日**）；⑥ 週報 digest 筆數＝**23**（現顯 20） |
| **M2　口徑機械化** | 08-23 | ① `measure_registry` 七組全登錄且每個 `measure_key` 恰 1 列 authoritative；② `treaty_probe_binding` 覆蓋 ≥ **13** 項綁 10-14 者 ＋ ≥ **7** 處 live 文件數字；③ 任一綁定值手改一位數 → `--check` rc≠0；④ CS lint 現況**恰報 2 筆**、修正後 0；⑤ 修訂表現行標記**恰 1 列**（現 2 列）；⑥ `validation_evidence` 之 `green AND last_verified_at IS NULL`＝**0**（現 **2**），green 由 16 誠實降為 **14** |
| **M3　存量與 sim 終點** | 09-30 | ① `source_column` 非空＝**98**（現 0）；② `sim_evolution_verdict` 具 killed／undecidable 之可執行 writer，且 promoted 缺 `decided_by` 時被 DB 拒；③ `reports/`＋`audits/` 之 24 份試點皆有 `status:` front-matter 且稽核器可擋新增缺欄者；④ `attestation_result` 連續 3 日各 ≥1 列且 `passed` 與 `coverage_gap` 一致 |
| **M4　併審備料** | 10-10 | ① 七框 ＋ 六同綁項**各有一個現查值**；② `read_treaty_probes --check` rc=0 且每條有 reading；③ **零筆由 AI 寫入 'meets' 於人裁類框**；④ 留 4 日緩衝 |

### 7.2 驗收設計三條鐵律（貫穿全部項目）

1. **先驗紅是唯一有效驗法**（CLAUDE #35）。凡新增檢查一律要求「退回壞版必須變紅」。本計畫共 **21 項**把「今日 live 必須報紅」寫成通過條件：M-G1 · M-G2 · M-G3 · M-G4 · M-G6 · M-G9 · M-G10 · M-G11 · M-G12 · M-G13 · M-G14 · M-G15 · M-G16 · M-L1 · M-L2 · M-L6 · M-N1 · M-N15 · M-N17 · M-N18 · M-O2 · M-P12 · M-P13。**全綠即視為未通過。**
2. **回歸鎖 fixture 必取自真產生器**（#35(1)），禁字面 dict。本專案第一次把此做對是 `evaluate_sim_calibration.py` 之「契約絆線」段（`importlib` 動態載入真 runner），該模式應推廣至其餘跨程式契約——**⚠ 契約對數尚未盤點，見 §8**。
3. **rc 取值一律重導向到檔或用 `${PIPESTATUS[0]}`**（r4 T1：`cmd | tail -4; echo rc=$?` 取到的是 `tail` 的 rc，恆 0）。本輪量 vendor 掃描即用此法。

### 7.3 每週回報格式（掛既有週日 09:00 週儀表，零新排程）

```
本週優化進度
  已完成步：<第 N 步清單>            未完成且逾期：<清單＋原因>
  M-N1 探針：N/13 綁 10-14 者 meets   （AI 不代勾人裁類框）
  sim 時鐘：K=n/3，下一格 <date>，待結算 <n> 列
  紅燈：validation_evidence red N 條，最久 red_since=<date>
  容量：nproc / loadavg / available MB / llama RSS / heavy_slot 持有者
  待裁積壓：窗二 N 項、窗三 N 項；awaiting_hugo N 件（最舊懸置 N 日）
```

---

## §8 誠實邊界（本計畫未涵蓋者）

### 8.1 本檔未做的事

- **全程唯讀**：零 DDL、零 DB 寫入、零 commit、零 systemctl、未改任何既有檔（唯一寫入＝本檔）。**未執行任何優化項。**
- **未代裁**任何 §4 之 36 項；**未代簽**任何 `decided_by`／`approved_by`／`promoted_by`；**未代勾**任何 10-14 日曆項（RULING-2026-039）。
- **未實跑**：`refresh_knowledge_pipeline.py --domain finance`（非唯讀）｜288 支 selftest 全量｜26 支 pytest 全量｜`run_kh_chain --check` 全鏈（以等價 SQL 代）｜`constitution_lint --selftest`（本輪引 r4 之 rc=1／FAIL 恰 1 條）｜FinMind 配額錶（唯讀輪禁 API，#24／#25）。
- **未親查**：`evolution_production_feature_set` 三列 active 之 `apply_log_id` 逐列指向（影響 M-E2 之可為性判定）｜sim 四件套是否真為 INSERT-only（影響 M-M3 之「零 code 改動」估計，該句為引用素材）｜51 份裁決正文｜`docs/系統架構大憲章_v1.54.0.md` 全文逐條。

### 8.2 「未估、須先抽樣」清單（**不編數字**）

| # | 項目 | 為何未估 | 抽樣方法 |
|---|---|---|---|
| 1 | **M-W5**（98 通道欄位級展開） | 展開比例未量——**這是全案最大的未知數** | 第 25 步 M-W2 即為此設：抽 10 列量單位成本並外推 |
| 2 | **M-W3／M-W4 裁後改碼** | 取決於甲乙丙案（甲＝建 view 層涉 DDL＋98 通道逐一決定 view 名；乙＝改 `compare_shadow_binding` 判式約 20–40 行但改的是驗收判準本身、須先驗紅） | 裁後各案先跑一次機械後果實測 |
| 3 | **M-G10 補抓 API 面** | `_dimension_sync` 之實際 request 數取決於 resume 粒度 | 先跑 `--dry-run` 量測 |
| 4 | **M-G10 污染期回填／重跑** | 屬 Steward 處置（涉已入帳本之 arena 預測列） | 待裁後定 |
| 5 | **M-G5 日班對帳時長** | 08-01 那輪 16:40→18:45（≈2h）是 `--heal` 全量；日班該用什麼 `--audit-days` 與抽樣股數（現 `AUDIT_SAMPLE_STOCKS=40`）未定 | 先量一次再定 |
| 6 | **M-K2 全量 upsert 機時** | 142,441 件 depth≥5 之 item | 先抽 1,000 列量單位成本 |
| 7 | **M-K4 帳本止血** | 去重後剩幾列未知；單批 DELETE 秒數未知 | 先跑唯讀 `SELECT count(DISTINCT (target_kind,target_id,layer_scores))`（50 萬列上為分鐘級） |
| 8 | **M-L1(b)** `constitution/` 51 檔之 corpus 擴充 | 該目錄之不變式尚未定義 | 先抽 5 檔量單位成本 |
| 9 | **M-L3** 條號前綴 14 例逐處清償 | 須逐例判定該補哪個前綴——**屬理解層，錯了會沉默污染下游**（#28 二分） | 逐例讀原文定錨 |
| 10 | **M-N17** 501 檔存量補標 | 單位成本未量 | 先做 24 份試點（08 月 18 份＋HANDOFF 讀序引用之 6 份） |
| 11 | **M-G13** 159 件 awaiting_hugo 之分流 | 題目內容分佈未讀 | 先抽 20 題量分類成本 |
| 12 | **M-G16(b)** 116 支 trigger 改 ALWAYS | 各支之 owner 與複寫路徑未查 | 先全量查 owner |
| 13 | **M-E2** prodset 溯源修復 | 只確認「兩份計畫皆缺」與 r4 之描述，未親查其他斷點 | 先跑唯讀全量對帳 |
| 14 | **M-E4** `gate_scale` 指紋升級 | 須先窮舉應涵蓋之 11 個參數並確認每個口徑——屬理解層 | 逐參數定錨 |
| 15 | **M-O6** 四案量化對照 | 現有 645–720 s/feature 是**混合條件觀測、未分離** | 在「有／無 LLM 鏈並行」兩條件各量一次（各 ≈12 分鐘機時，須非 TWEVO 夜） |
| 16 | **M-O2 異裝置** | 涉採購／實體，非工時 | hugo 車道 |
| 17 | **M-R1／M-R2／M-R4／M-R5／M-R7／M-R8** | 性質橫跨判準、效能、架構；執行計畫自己也只給波次不給工時 | 裁後逐則另估，**不合併估** |
| 18 | **推廣「契約絆線」模式** | 跨程式契約對數尚未盤點（僅知 sim W5→W3 一對已修） | 先花 1–2h 盤點 `gate_json`／`evidence_json`／`attestation` payload／sim 四件套之寫端讀端配對 |

### 8.3 引用而未親自重跑之估計（標示來源，非本檔量測）

- M-G1 半日、M-G3 半日、M-N1 S1 一日（皆優化計畫書 §4.3 自陳）。
- M-E1(甲) 之 **+11–12 分鐘/feature**（優化計畫書依 07-31 實測 645–720 s/feature 推算）。
- M-K1 之「每次檢索多付約 1.3s」計時（r4 標為【引用】，非其親測）。
- M-G8 之 `--domain finance` **rc=0**（本輪只驗 DB 側：`domain='finance'`＝0、pending 102,039，**未實跑腳本**）。
- sim k1/k2/k3 史料模擬「7/7 序列全判死」（self-reported 模擬，且門明文**史料不得入證據列**）。

### 8.4 本檔已知會過期的部分（讀者請現查）

| 內容 | 為何會過期 | 現查指令 |
|---|---|---|
| §0.3 之容量數字 | **19 分鐘內 available 由 1,509 → 6,960 MB**（llama-server RSS 5,507→647）——**容量是隨 Ollama 駐留狀態擺盪的量，不是常數** | `free -m; ps -eo pid,rss,comm --sort=-rss \| head -5` |
| 全部 live 計數 | 本專案同一日內已被證實漂移 ≥3 次（vendor 128→130／10-14 命中 74→88／memory 索引） | §8.6 之彙編 |
| repo HEAD `f7c7c68` | 三個 worktree 並行中；今日已有 6 個 commit | `git log --oneline -5` |
| §5 之時點推算 | 依賴 `COOLOFF_H=24`、timer 打點週期、cron 表；任一變動即失效 | `systemctl --user list-timers --all` |

### 8.5 三個本檔**未涵蓋**的射程

1. **全 repo 逐檔讀**：本檔承接 r4 之射程聲明——**沒有**字面讀完全 repo。規模：`scripts/*.py` **327**｜`reports/*.md` **301**｜`audits/*.md` **200**｜public 表 **334**｜`constitution/*.md` **51**｜`specs/*.md` **14**｜`docs/compliance/*.md` **7**｜`src/augur` 16 package。**本檔＝可執行的優化 SSOT，不是全文索引。**
2. **三份並行 agent 今日產出之新報告**（`wm_annexf_*`／`wm_channel_registration_*`／`wm_m3_batch1_*`／`gov3b_*`／`kdo4_*`）之**完整內容**：本檔僅透過四路補齊之摘要引用其結論（M-W3／M-W4 即源自 `wm_m3_batch1_*`／`wm_channel_registration_*`）。它們只新增不修改，但**其細節可能與本檔某些數字互補或衝突，讀者宜對照**。
3. **前三份素材各自的完整細節**：本檔以引用方式承接三份之 schema 規畫、程式規畫、覆核指令、踩雷紀錄（尤其 **r4 §5 之 T1–T20 二十則踩雷，本檔不複述但全部仍有效**）。**執行任一步之前應回讀對應素材段落。**

### 8.6 覆核指令彙編（全部唯讀，可重跑）

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
# ⚠ 連線經 .env 之 DB_USER（psql -U hugo 會 FATAL）
# ⚠ 取 rc 一律重導向到檔或用 ${PIPESTATUS[0]}（r4 T1）

# ── 本檔全部 live 數字（一次取齊）──
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -Atc "
SELECT 'deferred',count(*) FILTER(WHERE cleared_at IS NULL)||'/'||count(*) FROM evolution_deferred_work
UNION ALL SELECT 'pq_pending_auto',count(*)::text FROM promotion_queue WHERE queue_status='pending_auto'
UNION ALL SELECT 'pq_superseded',count(*)::text FROM promotion_queue WHERE queue_status='superseded'
UNION ALL SELECT 'pq_max_run',max(run_id)::text FROM promotion_queue
UNION ALL SELECT 'apply_log_7d',count(*)::text FROM evolution_apply_log WHERE applied_at>now()-interval '7 days'
UNION ALL SELECT 'attestation',count(*)::text FROM attestation_result
UNION ALL SELECT 'attestation_max',max(run_at)::text FROM attestation_result
UNION ALL SELECT 've',count(*) FILTER(WHERE status='green')||'/'||count(*) FROM validation_evidence
UNION ALL SELECT 've_green_neververified',count(*)::text FROM validation_evidence WHERE status='green' AND last_verified_at IS NULL
UNION ALL SELECT 'wcb_srccol',count(source_column)||'/'||count(*) FROM world_channel_binding
UNION ALL SELECT 'wcv_noauth',count(*) FILTER(WHERE authoritative_binding_id IS NULL)||'/'||count(*) FROM world_concept_version
UNION ALL SELECT 'dgate_pass',count(*)::text FROM direction_gate WHERE status='evaluated_pass'
UNION ALL SELECT 'laievo',count(*)::text FROM local_ai_iteration_ledger
UNION ALL SELECT 'awaiting_hugo',count(*)::text FROM steward_question_ledger WHERE status='awaiting_hugo'
UNION ALL SELECT 'resolved_by_hugo',count(*)::text FROM steward_question_ledger WHERE resolved_by='hugo'
UNION ALL SELECT 'sim_run_link',count(*)::text FROM sim_run_link
UNION ALL SELECT 'sim_evo_ledger',count(*)::text FROM sim_evolution_iteration_ledger
UNION ALL SELECT 'mc_sim_run',count(*)::text FROM mc_simulation_run
UNION ALL SELECT 'strangler_ledger',count(*)::text FROM vendor_binding_strangler_ledger
UNION ALL SELECT 'trg_always/total',count(*) FILTER(WHERE tgenabled='A')||'/'||count(*) FROM pg_trigger WHERE NOT tgisinternal
UNION ALL SELECT 'seal_trigger',count(*)::text FROM pg_trigger WHERE tgname LIKE 'trg_sunset_seal_%'
UNION ALL SELECT 'kh_run_rows',count(*)::text FROM knowhow_auto_admit_run
UNION ALL SELECT 'staging_pending',count(*)::text FROM knowledge_staging WHERE status='pending'
UNION ALL SELECT 'ki_finance',count(*)::text FROM knowledge_item WHERE domain='finance'
UNION ALL SELECT 'TRI_max',max(date)::text FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX'
UNION ALL SELECT 'PriceAdj_max',max(date)::text FROM \"TaiwanStockPriceAdj\"
UNION ALL SELECT 'mkt_dir_feat_max',max(panel_date)::text FROM market_direction_feature
UNION ALL SELECT 'ledger_guard_tbl',count(DISTINCT tgrelid)::text FROM pg_trigger t JOIN pg_proc p ON t.tgfoid=p.oid WHERE NOT t.tgisinternal AND p.proname='honesty_ledger_guard'
UNION ALL SELECT 'delete_only_tbl',count(DISTINCT tgrelid)::text FROM pg_trigger t JOIN pg_proc p ON t.tgfoid=p.oid WHERE NOT t.tgisinternal AND p.proname='honesty_delete_only_guard';"

# ── runaway backend（M-O1）──
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -Atc \
 "SELECT pid,state,application_name,now()-xact_start FROM pg_stat_activity WHERE state<>'idle' AND pid<>pg_backend_pid();"

# ── worktree 雙失效（M-G1）──
for w in $(git worktree list --porcelain|awk '/^worktree/{print $2}'); do printf "%s venv=" "$w"; [ -d "$w/venv" ] && echo YES || echo NO; done
head -1 CLAUDE.md; head -1 .claude/worktrees/*/CLAUDE.md
sed -n '13,17p' ops/githooks/pre-commit

# ── 判式與契約 ──
sed -n '155,160p' scripts/reconcile_audit.py; sed -n '585,590p' src/augur/audit/reconcile.py
sed -n '433p' scripts/run_evolution_iteration.py; sed -n '239p' scripts/verify_evolution_acceptance.py
sed -n '347p' scripts/report_triple_evolution_week.py
venv/bin/python -c "
import sys;sys.path.insert(0,'scripts');sys.path.insert(0,'src');import _bootstrap,numpy as np
from evaluate_sim_calibration import normalize_q_grid; from run_sim_calibration_cell import _q_grid
r=normalize_q_grid({'terminal_q_grid':{'unit':'x','p':_q_grid(np.linspace(-.5,.5,20000))}});print(type(r).__name__,len(r))"

# ── 基線與口徑 ──
venv/bin/python scripts/check_vendor_binding.py --scan > /tmp/vb.txt 2>&1; echo rc=$?; tail -3 /tmp/vb.txt
venv/bin/python scripts/check_cmd_matrix.py > /tmp/cm.txt 2>&1; echo rc=$?; tail -2 /tmp/cm.txt
ls scripts/*.py | wc -l; ls reports/*.md | wc -l; ls audits/*.md | wc -l
ls constitution/*.md | wc -l; ls specs/*.md | wc -l; ls docs/compliance/*.md | wc -l
grep -ro "2026-10-14" constitution/ specs/ docs/compliance/ | wc -l
python3 -c "import datetime;print((datetime.date(2026,10,14)-datetime.date.today()).days,'days to 10-14')"

# ── 排程與維運 ──
crontab -l | grep -c '^[0-9*]'; crontab -l | grep -c 'notify_failure'
bash install_cron.sh --check 2>&1 | tail -2
systemctl --user list-timers --all --no-pager | head -12
stat -c '%y %n' /tmp/augur_audit_dispatch.ts; stat -c '%y' ~/audit_retry.log
ls -la /mnt/c/database/
venv/bin/python -m augur.core.heavy_slot 2>&1 | tail -3
free -m | head -2; cat /proc/loadavg; nproc
```

---

## 附　本計畫之 (a) 表 schema 對映 ＋ (b) python 程式規畫（憲章 v1.39.0 要件）

### (a) 表 schema

| 動作 | 表 | 內容 |
|---|---|---|
| **新建** | `treaty_probe_binding` | M-N1。欄：`probe_id` PK／`clause_ref`（file:line）／`deadline` date／`measure_key` FK→`measure_registry`／`ruler_key`／`check_cmd`／`expect_expr`／`owner`（AI／Steward）／`created_at` |
| **新建** | `treaty_probe_reading` | M-N1。欄：`reading_id` PK／`probe_id` FK／`read_at`／`value_text`／`verdict`（meets／not_meets／**undecidable**）／`machine_note`。⚠ 凡涉「是否已達成／續延」者一律 `undecidable`，AI 只登錄量測值 |
| **新建** | `measure_registry` | M-N2。欄：`measure_key`／`ruler_key`／`definition`／`repro_cmd`／`authoritative` bool／`registered_at`。約束：每 `measure_key` 之 `count(*) FILTER (WHERE authoritative)` 恰 1 |
| **加欄** | `validation_evidence` | M-P12(b)：`red_since` timestamptz |
| **加 FK** | `sim_run_link.iteration_uid` → `sim_evolution_iteration_ledger.iteration_uid` | M-T1 |
| **加 trigger** | `sim_calibration_eval`／`sim_realized_outcome`／`sim_run_link`／`validation_evidence`／`attestation_result` | M-M3／M-P11 裁後；`honesty_ledger_guard`（BEFORE DELETE OR UPDATE FOR EACH ROW ＋ BEFORE TRUNCATE FOR EACH STATEMENT） |
| **只讀** | `world_concept(_version/_registry_current)`／`world_channel_binding`／`column_catalog`／`dataset_catalog`／`promotion_queue`／`evolution_*`／`knowhow_*`／`knowledge_*`／`pg_trigger`／`pg_constraint`／`pg_stat_activity` | 各步之驗收與探針 |
| **DML（不改結構）** | `knowhow_auto_admit_state.layer_scores`（M-K2）／`evolution_iteration_ledger` 空欄（M-E3）／`knowledge_fulltext_status`（M-K3） | — |

### (b) python 程式規畫

| 檔 | 角色 | 新／改 | 對應步 |
|---|---|---|---|
| `ops/githooks/pre-commit` | 五閘入口 | 改（ROOT 解析／fail-closed／檔頭） | 1 |
| `scripts/check_worktree_treaty_sync.py` | worktree 治權檔同步稽核 | **新**（矩陣＋selftest） | 1 |
| `scripts/check_dataset_freshness.py` | per-dataset 新鮮度哨兵 | **新**（catalog 驅動、非 heavy） | 14 |
| `scripts/check_report_index.py` | `reports/`／`audits/` front-matter 稽核＋索引產生 | **新** | 24 |
| `scripts/check_memory_index.py` | `MEMORY.md` 四類稽核 | **新** | 24 |
| `scripts/read_treaty_probes.py`／`sync_treaty_probes.py`／`migrate_treaty_probe_ddl.py` | 探針表建置／量測／`--check` | **新** ×3 | 9・19・33 |
| `scripts/migrate_measure_registry_ddl.py`／`register_measure.py` | 度量登錄 | **新** ×2 | 9・20 |
| `scripts/decide_sim_verdict.py` | W4 判決（killed／undecidable） | **新** | 26 |
| `scripts/reconcile_audit.py` | 對帳 CLI | 改（呼叫 `reconcile.verdict()`） | 10 |
| `scripts/run_evolution_iteration.py`／`verify_evolution_acceptance.py`／`report_triple_evolution_week.py` | 進化 driver 檔群 | 改（謂詞／A8／gate_ref） | 3 |
| `scripts/evaluate_sim_calibration.py` | sim 評估器 | 改（n_valid 閘／env_halt） | 11 |
| `scripts/run_sim_calibration_cell.py` | sim runner | 改（ledger 狀態接線） | 2 |
| `scripts/check_treaty_refs.py` | 治權引用 lint | 改（＋`cs_selfversion_mismatch`／雙現行／掃到對象數地板） | 12・9 |
| `tools/constitution_lint/report.py` | corpus | 改（`corpus_files()` 擴至 `constitution/`＋`docs/compliance/`） | 12 |
| `src/augur/audit/import_isolation.py` | 隔離閘 | 改（地板斷言＋補三包） | 9・24 |
| `src/augur/philosophy/retrieval.py` | 檢索 | 改（刪兩段死碼）**＋重啟 advisor/chat** | 16 |
| `src/augur/knowledge/auto_admit.py` | 准入 | 改（`prior_depth` 正名／KH1 旁路分流） | 16・23 |
| `scripts/backfill_fulltext_unattempted.py` | D1 回填 | 改（分批冪等＋掛班次） | 16 |
| `scripts/backup_database.sh` | 備份 | 改（鏡像事後驗證＋`--status` 報紅） | 18 |
| `ops/audit_watchdog.sh`／`augur-audit-watchdog.service` | 發車 | 改（KillMode／閉環判式） | 15 |
| `install_cron.sh` | 排程 SSOT | 改（15 行加 `\|\| notify_failure`；ollama 路徑） | 15・24 |
| `scripts/verify_code_reports.py` | 報告清點 | 改（ROOT 由 `__file__` 推＋兩尺並列） | 9 |
| `scripts/verify_validation_evidence.py` | VE 重驗 | 改（未驗列不計 green／`red_since`／GUC 通行證） | 17・21 |
| `tools/project_memory_mcp`（呼叫點） | index | 改（包 flock） | 24 |

**共通義務**：凡新增可執行 Python 入口，**首次提交當下**即須含執行指令矩陣（含無參數安全預設）＋`--selftest`（CLAUDE #18／#29(d)／v1.30 向前生效）；`check_cmd_matrix.py` 受檢數應由 **467** 前進而缺漏維持 **0**。

---

**本檔結束。** 全檔為執行 SSOT 呈案，**未執行任何優化項**；零 DDL、零 DB 寫入、零 commit、零 systemctl。
§4 之 36 項待裁未代裁、未預設答案；恆紅閘（KH0 48.7%／`direction_gate` 0/29）與三條硬期限已如實揭露；§8 之 18 項「未估、須先抽樣」未編造數字。
