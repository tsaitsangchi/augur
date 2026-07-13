# augur 建構作法完整理解報告 v4（code-verified）

**日期**：2026-07-13 ｜ **取代**：`augur_construction_understanding_20260710.md`（v3）
**方法**：58-agent 多視角深讀（16 子系統讀者＋10 critic 補讀＋4 橫切鏡頭）× 逐宣稱對抗驗證（12 條承重宣稱被 REFUTED、正文一律採更正版）× 完整性 critic 二輪迭代；全宣稱附 `path:line` 或 live DB SELECT 證據。
**如何讀**：§0 三十秒框架 → 有疑再進對應章；§12 列 v3 過時宣稱與本輪 REFUTED 表。
**目錄**：§0 三十秒框架＋術語 ｜ §1 治權脊椎 ｜ §2 系統全景（三塊/double-gate/中途態）｜ **半-1 預測** §3.1 ingestion+raw品質 · §3.2 core/catalog/DDL遷移 · §3.3 features+發現工具鏈 · §3.4 universe/models/execution/登錄 · §3.5 evaluation · §3.6 audit · §3.7 驗證harness+出單SOP · §3.8 方向軸 · §3.9 擂台+三鏡頭 ｜ **半-2 素養/顧問** §4.1 knowledge+語意橋 · §4.2 philosophy · §4.3 嵌入/檢索 · §4.4 advisor/前台/蒸餾/RBAC ｜ **第三塊＋跨系統** §5 審議引擎 · §6 跨機維運 · §7 房規 · §8 端到端 · §9 wiring表 · §10 常數速查 · §11 債/斷線/埋雷 · §12 對 v3 差異

---

## §0 三十秒核心框架

augur 是「**台股相對強弱預測 × 投資素養顧問**」雙半系統，由**治權文件**（靈魂 v1.8.0／原則精華 v1.9.0／憲章 v1.45.0／CLAUDE v1.27／README）自上而下長出，再以**第三塊系統——本地審議引擎**（零 Claude token 的對抗驗證引擎）治理開發過程本身。三塊的建構總綱是同一句話：**凡承重判準先凍後跑（preregister-then-run）、凡強制下沉機械閘（DB trigger/CHECK/AST）、凡做不到誠實留終態帳（fulltext_blocked/never_shown）、凡長跑帳本冪等可續（resume-safe）、凡拍板權綁人（hugo 親簽、AI fail-closed）**。

當前狀態一句話（2026-07-13）：FREEZE 已解凍轉 live 增量維運（原則精華 v1.9.0）、方向軸十門二次證偽全判死＋no-v3 入憲、擂台九選手六門簽核待 audit 綠開賽、知識層全文解析器 CODE 已 commit（491 件公版全文/47 萬句於**原機**落地——本機 DB 為 07-12 dump、尚無此資料，詳 §4.1 陷阱）、活體增量推進到特徵層（feature_values 至 2026-06-30）但 universe→prediction 仍錨 2026-05-31（中途態、unfreeze gate 未 evaluate）。

### §0.1 三塊系統與依賴方向

```
┌────────── 治權文件（法律）──────────┐
│ 靈魂 → 原則精華(20條) → 憲章(六部) → CLAUDE → README │
└──────────────┬──────────────┘
     機械閘下沉(trigger/CHECK/AST/GRANT/測試)
                 ↓
┌─ 半-1 預測系統 ─┐        ┌─ 半-2 素養/顧問系統 ─┐
│ ingestion→catalog→ │ ←唯讀── │ knowledge/philosophy   │
│ features→universe→ │ frozen  │ →embed→retrieve→      │
│ models→prediction→ │ payload │ advisor→chat UI        │
│ validation→arena   │ (單向)  │                        │
└──────────────┘        └──────────────┘
                 ↑ 兩塊之外
┌─ 第三塊:本地審議引擎(開發治理) ─────────┐
│ deliberate.py 十模式+5 oracle 機械鎖+人裁佇列    │
│ 裁「開發宣稱」真偽,零 Claude token,GATE 證成    │
└────────────────────────────┘
```

單向依賴鐵律：預測 7 package **零 import** philosophy/advisor/knowledge（AST 閘八道掃描、親跑 0 violations）；顧問對預測**只經一個 frozen dataclass 唯讀**（`build_prediction_payload`，payload.py:154-260）。
**縮寫速查**：PIT=point-in-time（決策當下可見）· OOS=out-of-sample · EAV=entity-attribute-value 窄長表 · IC=information coefficient · HAC=heteroskedasticity-and-autocorrelation-consistent（Newey-West）· DSR=deflated Sharpe ratio · ECE=expected calibration error · MDE=minimum detectable effect · RBAC=role-based access control · HNSW=hierarchical navigable small world（向量索引）· SSOT=single source of truth

---

---

## §1 治權脊椎：doctrine 如何組織與防漂移

augur 的最上層不是 code，是一組**治權文件**——所有 code／架構／決策都從中長出的 SSOT（single source of truth，單一權威來源）。這層回答四個問題：法律怎麼**組織**、怎麼**分家**、怎麼**升版**、怎麼**防彼此漂移**。它把「只信真兆、防三敵人（① 假資料 · ② 偷看未來 · ③ 自我欺騙）」的抽象精神，逐級降解為可執行紀律；並對最承重的判準（輸出契約 fail-closed、隔離命門、挪門柱禁止），把 prose **編譯成 DB trigger + AST 測試的機械閘**。防漂移靠兩層力量：**文件紀律**（一概念一權威家，靠人工同步清單）＋**機械閘**（DB／AST 硬鎖，寫入前不合格即 `RAISE EXCEPTION`）。

### 1.1 五檔分層 + HANDOFF：各司一職、互引不複述

治權其實是**五檔**、非四檔。clean-room #16 的 WHAT 明列「只依 augur 自身 **5 治權檔**（靈魂 / 原則精華 / 憲章 / CLAUDE.md / README）＋ 自身 schema ＋ live API」（`docs/原則精華_v1.9.0.md:143`）——**README 是第五治權檔**，v3 報告 §1 的治權表只列 4 檔（漏 README，`reports/augur_construction_understanding_20260710.md:60-65`）為低估。另加 HANDOFF 共 6 份接續文件，但 HANDOFF 性質不同：非法律檔，是「跨機接續 SSOT」（新機 clone 後第一份讀，`HANDOFF.md:1-11`）——doctrine 未正式把它編為「第六治權檔」，此序數為理解框架、非 doctrine 明文。

| 層 | 檔案（版本） | 職責 |
|---|---|---|
| 靈魂（WHAT/WHY） | `docs/系統核心思想_v1.8.0.md`（162 行） | 一句話定義＋三敵人表＋北極星 3 問＋世界觀＋管線圖，讀完懂 80% |
| 原則精華（法律全文唯一 SSOT） | `docs/原則精華_v1.9.0.md`（173 行） | 20 條「不可違反法律」，每條 WHAT｜WHY｜ENFORCE；三基石 #1/#8/#15 |
| 憲章（HOW 框架） | `docs/系統架構大憲章_v1.45.0.md`（380 行） | 把 20 法律 map 到「三敵 × 管線」＋12-PHASE 維運＋升版規則；六部＋3 附錄 |
| CLAUDE（AI 工具規則） | `CLAUDE.md`（v1.27） | 「如何用 AI 工具編輯本專案」的短半衰期協作規則（半衰期 6-12 月） |
| README（門面指針） | `README.md`（59 行） | 對外門面＋「先讀這幾份」治權檔導引 |
| ＋ HANDOFF（跨機接續 SSOT，非法律檔） | `HANDOFF.md`（137 行） | §1 治權路由、§4 取代式現況 STATE、§5 誠實紅線 |

### 1.2 SSOT 三分與升版連動：文件紀律防漂移

防漂移的第一層是**「一概念一權威家」**：憲章第六部立「SSOT 鐵律：靈魂只住核心思想、法律全文只住原則精華、架構/維運只住本憲章；任一概念只有一個權威家（#12）」（`docs/系統架構大憲章_v1.45.0.md:274`）。刻意的設計是**憲章第四部把 20 條做成純索引表、不改寫法律全文**：「法律全文以原則精華為 SSOT……本憲章不另行改寫（避免漂移，呼應 #12）」（`:188`）——杜絕兩處法律不一致；**不能拿憲章第四部當法律 SSOT**。

**升版連動有嚴格判準**（憲章第六部 `:269-270`）：僅「新增一條不可違反原則」或「既有原則之重大判準修正」才連動升原則精華；純架構/維運/方法承載變更**只升憲章、原則精華不動**（治權檔本就各自獨立版本）。

> **更正（v3 之數字誤述）**：連動升原則精華**並非「迄今僅兩次」**。逐列查憲章修訂歷程，原則精華迄今被**連動約十次**：v1.1.0（#16）/ v1.2.0（#17）/ v1.3.0（#18）/ v1.4.0（重大判準修正）/ v1.5.0（#19）/ v1.6.0（#20）各連動一次（`docs/系統架構大憲章_v1.45.0.md:335-340`），加憲章 v1.9.0（→ 精華 v1.7.0，#3/#4/#18 判準修正 `:343`）、v1.9.1（→ v1.7.1，as-of 新增判準 `:344`）、v1.38.0（→ v1.8.0，FREEZE `:373`）、v1.43.0（→ v1.9.0，解凍 `:378`）。**v1.38.0 / v1.43.0 只是「既有判準內容實質擴展」子型的最近兩次**——v1.38.0 修訂文字自稱「首次連動原則精華升版……因判準內容實質擴展、非僅憲章承載」，該「首次」僅指此子型之首次，非史上僅兩次。誤讀此「首次」會低估連動頻率。

升版哲學同時**反膨脹**：v1.22.0 立「修訂歷程 3 行封頂」體例（`:273`）、永守「30 分鐘讀懂全系統法律」（憲章全文出現 **12 次**「30 分鐘」，`grep -c`＝12）；這是拒絕舊 stock_backend「255-treaty 累積病」的機制（原則精華升版哲學段，`docs/原則精華_v1.9.0.md` ≈`:158-173`）。

### 1.3 條號非連續 × 12-PHASE：拒累積病＋從零重建脊椎

**20 條條號非連續是刻意設計**：按「新增順序編、分類歸區」故跳號——A 資料 `#1-7,17,18` · B 建模 `#8-12` · C 風險治理 `#13-15,19` · D 開發協作 `#16,20`（`docs/系統架構大憲章_v1.45.0.md:188`）。新增法律只 append、條號永久穩定；讀者若期待連續會誤判「缺條」。

**12-PHASE 維運矩陣（憲章第五部 `:231`）＝從零重建脊椎**：規定從零重建一律照 PHASE 0-11 序、不可跳/不可改 order，每 PHASE 過 audit gate 才進下一（0 環境 → 1 infra bootstrap → 2 名冊 → 2b FRED → 3 宇宙引導 → 4 全史 sync → 5 raw 對帳 → 6 raw 完整候選 → 7 feature store → 8 最終核心 → 9 五鏡 audit → 10 訓練 → 11 驗證）。並澄清**「三種建法」**：generic auto-schema（API 表、無白名單）、explicit DDL bootstrap（infra log，PHASE 1）、builder 自建（計算型內部表，各自 PHASE）——#3「無白名單全 generic」只管 API dataset，內部表用自己的 explicit DDL。

### 1.4 機械閘：doctrine 下沉為 DB trigger + AST 測試

防漂移的第二層是**把最承重的判準編譯成機械閘、不靠 prose**：

- **輸出契約 fail-closed**（憲章 v1.45.0）：`direction_probability` / `daily_direction_probability` 寫入前，對應 `direction_gate` 狀態須＝`evaluated_pass`，否則 `RAISE EXCEPTION`——強制於 DB trigger `trg_dirprob_gate_guard` / `trg_ddirprob_gate_guard`（BEFORE INSERT/UPDATE），共用函式 `direction_product_gate_guard`，錯誤訊息**字面引「fail-closed(憲章 v1.45.0 輸出契約)」**。現無任一 gate＝`evaluated_pass`，故產物表**零列**（DB：`count(*) direction_gate WHERE status='evaluated_pass'`＝0、`count(*) direction_probability`＝0）＝誠實拒答。
- **挪門柱禁止**：`direction_gate` 判準不得事後挪動——`trg_direction_no_goalpost`（BEFORE UPDATE/DELETE）。
- **擂台 anti-snooping**：`direction_arena_prediction` 不可改/不可回填——`trg_arena_pred_immutable` + `trg_arena_pred_no_backfill`；候選凍結 `trg_arena_candidate_frozen`。
- **來源治理審批 fail-closed**（憲章 v1.41.0）：非 active 之知識來源擋於庫外——`staging_source_gate`（`knowledge_staging` BEFORE INSERT）。
- **隔離命門（#1 命門，AST 靜態閘）**：`tests/test_philosophy_isolation.py` 斷言**預測 7 package**（`import_isolation.py:31` PIPELINE＝features/models/universe/evaluation/ingestion/audit/catalog）**零 import** FORBIDDEN＝{philosophy, advisor, knowledge}（`:33`）；RBAC resolver 須住 `augur.knowledge`、`augur.core` 禁 resolve；scripts/ 預測腳本禁字面觸 chat/RBAC 表。

> **措辭精確**：`staging_source_gate`（DB）與 AST 隔離測試守的是**兩個不同不變式**——前者守「語料准入的來源純度」（knowledge_staging 入庫），後者守「預測管線零 import 素養層」；二者是**互補純度機制、非守同一標的之雙閘**，不宜混稱為「同一隔離命門的 AST+DB 雙閘」。

### 1.5 輸出契約立法（v1.42 → v1.45）：自 v3 以來最大治權變化

v3 報告 §1 完全未涵蓋此段——它是 07-10 之後治權層最大的變化，四步連續入憲：

- **v1.42.0（07-11）預言機軸立法**：validate 新增「預言機誠實判準」，H/D 兩軌唯 `direction_gate` **預註冊可證偽實驗過 GATE** 才展示；五項誠實硬綁、禁單股準確率、逐日點位/路徑永久除外（`:377`）。
- **v1.43.0（07-12）no-v3 ＋ FREEZE 解凍**：方向軸**十門二次證偽**（結案報告 hugo 親簽），對凍結快照不得另立同假說新 gate；同步 FREEZE 解除（原則精華 v1.8.0→v1.9.0）（`:378`）。DB 佐證：`direction_gate` 恰 10 列 `evaluated_fail | hugo`——`dgate_H_20/H_40/H_82/H_120`、`dgate_D_1/D_5`，加 4 個 v2 變體 `H_20_v2/H_40_v2/H_82_v2/D_5_v2`（**v2 變體僅 4 個、非 6 個**，無 `H_120_v2`/`D_1_v2`）。
- **v1.44.0（07-12）輸出契約三產物閉集**：① 方向機率 % ② horizon 級準確率 %（「非單股保證」硬綁）③ 期望報酬率；fail-closed 升格 DB 機械閘（`:379`、`docs/系統架構大憲章_v1.45.0.md:129`）。
- **v1.45.0（07-12，ACTIVE）E[r] 幅度級升格 ＋ 刪靈魂不可違反句**：③ 由「經濟翻譯非幅度預測」升格「**幅度級期望報酬產物、得逐股呈現**」；原不可違反句「不是預測絕對漲跌幅」經用戶**三度堅持刪除**（`docs/系統核心思想_v1.8.0.md:28`），AI 勸阻全文與用戶堅持**雙留痕**（SSOT＝`reports/augur_oracle_output_contract_plan_20260712.md` §9-§12）（`docs/系統架構大憲章_v1.45.0.md:380`）。

**機械落地**：`direction_probability` 表新增七欄承載輸出契約——`expected_ret` / `hit_rate` / `p_up` / `econ_verdict` / `base_rate` / `calibrator_id` / `gate_id`（DB `information_schema.columns` 確認七欄全存）；fail-closed 從 prose 變 trigger 級強制。憲章並**明列「不受本次修訂影響之鎖」**：逐日價格點位/路徑永久除外（P1-4）、no-v3、GATE 唯一產生路、三敵零容忍、guard 單向棘輪、五項誠實硬綁（`:129`）——**修法只改「敢不敢說」、不動誠實地基**。

### 1.6 陷阱

- **治權檔版本交叉引用【無機械閘】、純人工同步、已實測漂移**：`README.md:14` 狀態句仍寫「靈魂 v1.5.0・憲章 v1.43.0・CLAUDE v1.25」，但實檔為 v1.8.0 / v1.45.0 / v1.27——而 `README.md:22-24` 連結表卻正確指 `_v1.8.0`/`_v1.9.0`/`_v1.45.0`（README **內部即不一致**）；`HANDOFF.md:20,120` 亦引「CLAUDE.md（v1.25）」。`tests/` 無任何 doctrine-version 一致性測試。**版本 SSOT＝憲章修訂歷程 ACTIVE 列＋原則精華全文（#12），勿信 README/HANDOFF 狀態句的版本數字**。
- **CLAUDE.md 版本天然領先其被引用值**：依其 §六，CLAUDE 可獨立升版而不動憲章（半衰期 6-12 月工具規則），故 CLAUDE 實檔 v1.27 領先其他治權檔對它的引用 v1.25——**by-design、非 bug**，但引用數字會持續落後。
- **as-of `2026-05-31` hardcode 只活在 demo 路徑**：全庫僅三處、皆在 `src/augur/advisor/payload.py:67`（example）、`:82`（empty payload）、`:86`（註解）；**生產選股路徑** `build_prediction_payload():154` 的 `as_of=None` 取 DB `max(panel_date)`（`:168`）、非 hardcode。解凍後部署主模型 panel 仍為 2026-05-31（DB `max(panel_date) FROM prediction_values`＝2026-05-31）——因 unfreeze gate 尚未 evaluate 通過、live 數字未升格，**非資料過期缺陷**。
- **修訂歷程只 append、既有列不回改**：47 條列裡除 v1.45.0＝ACTIVE，其餘 46 全 SUPERSEDED。查某判準演化史看歷程，但「現行法律」只認 ACTIVE 版＋原則精華全文。

### 1.7 07-10（v3）之後的變化

- **版本全面前進**：靈魂 v1.5.0→v1.8.0、原則精華 v1.8.0→v1.9.0、憲章 v1.39.0→v1.45.0（**360→380 行、41→47 版**修訂歷程）、CLAUDE v1.22→v1.27。v3 §1 表格所列版本全部過期，但**六部結構 / SSOT 三分 / 12-PHASE / 附錄 A 留空 / 條號非連續**等結構性宣稱仍全成立。
- **FREEZE→解凍（v1.43.0）**：v3 §1.3「全系統以 2026-05-31 為凍結基準」已 superseded——as-of 凍結解除、轉 **live 增量維運**、as-of'＝滾動；歷史完整性判準至 2026-05-31 定案不變。live 准入依 `prediction_unfreeze_gate`（gate_id＝`unfreeze_06dcb178267d`，`docs/原則精華_v1.9.0.md:77`）之 evaluate 紀律；DB 現況 `status=frozen | approved_by=hugo`（**未 evaluate**）——**pass 前 live 數字不得入任何「確立級」宣稱**。
- **輸出契約立法（v1.42→v1.45）**：見 §1.5，是自 v3 以來最大治權變化，v3 §1 完全未涵蓋。
- **升版連動運作證實**：v3 稱 v1.38.0 為「首次連動原則精華升版」；此後 v1.43.0 成為此子型第二次連動（原則精華 v1.8.0→v1.9.0），連動判準本身穩定運作（惟總連動次數約十次、見 §1.2 更正）。
- **CLAUDE #28 新增模型檔位分派（v1.27）**：執行/理解二分之上新增 Fable5（理解/裁決）、Opus4.8（重執行）、Sonnet5（輕執行/看顧）三檔位分派表，沿用同一裁決句「搞錯會沉默污染下游 → 高檔位；僅慢 → 低檔位」。
- **漂移點的移轉**：v3 §1.4 記的漂移是「system-reminder 注入舊 CLAUDE vs on-disk 較新」——本次該問題已消失（reminder 與 disk 皆 v1.27）；但**出現新漂移**：README/HANDOFF 對治權檔的狀態句版本引用落後於實檔（見 §1.6）。

---

## §2 系統全景（v4 更新版）

### §2.1 兩半＋第三塊、單向依賴與唯一耦合點

v3 的「兩半架構」在 07-10 之後演化為**三塊**：審議引擎既非預測也非顧問，是「**用機械 oracle 裁決開發宣稱**」的治理層（詳 §5）。兩半之間**唯一耦合點**不變＝advisor 經 `build_prediction_payload()` 唯讀 `prediction_values`/`model_registry`/`revalidation_ledger`/`prediction_probability`/`probability_calibrator`/`TaiwanStockInfo` 六表，回傳 **frozen** `PredictionPayload`（payload.py:19-42；`numbers()` 同時當 guard 數字白名單——LLM 造出白名單外的數字被機械攔）。反向零依賴（AST＋字面雙掃描 0 命中）。

07-10 後新增**最貼近特徵表的耦合旁路面「語意橋」**：advise.py:80-122 `_bridge_links` 讀 `field_term_map`（5,972 列）/`field_knowhow_lexical_affinity`（59,706 列），把問句命中的欄位名對映 know-how 詞——語意為「欄位**名稱詞**×know-how 詞的語料句共現」、**非**「欄資料值與報酬的相關」（免責硬綁 advise.py:120-122）。同步新增機械圍欄：`import_isolation` BRIDGE_LITERALS 納入禁字面掃描（import_isolation.py:46-48,175），預測 package 零觸及——**新耦合面與新防線同時落地**，單向性維持。

### §2.2 縱深防禦 double-gate 現況（v4 修正版）

- **AST 靜態閘**：`check_isolation()` 現串**八道**（1 AST import＋5 字面旁路〔rbac/chat/distill/deliberation/bridge〕＋1 對位＋1 scripts 洩漏面；v3 時代少於此），空列表即通過、薄殼 test 委派消費、附紅測證明掃描器抓得到植入違規。
- **DB 動態閘**：`augur_predict` role 已從 v3 的「provisioned-but-unwired」升為「**applied but connection-unwired**」——role 已建、153 張預測表 SELECT、素養表 0 授權（`import_database.sh:150` 換機時自動 `--apply`）；但 `core/config.py` 尚無 `DB_PARAMS_PREDICT`、`db.py connect()` 仍單一 superuser 參數——**沒有任何生產 code 真的用這個 role 連線**，動態閘仍未載入（setup_predict_role.py:19 自陳「另一步」）。
- **輸出契約閘（07-10 後最重要新落地）**：`direction_probability`/`daily_direction_probability` 掛 BEFORE INSERT/UPDATE trigger（`trg_dirprob_gate_guard`/`trg_ddirprob_gate_guard`），gate 非 `evaluated_pass` 一律 RAISE EXCEPTION（訊息字面引「憲章 v1.45.0 輸出契約」；migrate_direction_product_gate_ddl.py:27-43）。現況 direction_gate 無任一 pass → 兩張方向產物表**物理零列**＝fail-closed armed-and-dormant 實證。
- **不對稱（記錄在案）**：幅度軸 `prediction_probability` 無 trigger、判死列照存（econ_verdict dead 339/thin_unestablished 1,356），靠 advisor 展示層貼標（advise.py:40、payload.py:220-226）。方向軸=DB 物理零列、幅度軸=庫存全 verdict＋展示層把關——輸出契約 v1.45.0 明文只約束方向輸出，此為設計而非漏洞，但強度不對稱值得知情。

### §2.3 活體增量中途態（2026-07-13 快照）

解凍（07-12）後端到端鏈**推進不同步**（皆 live DB 親驗）：`feature_values` 36 panel、max=**2026-06-30**（新 panel 91,385 列/2,846 股/35 特徵）；但 `core_universe_asof` max=**2026-05-31**、`prediction_values` max=**2026-05-31**（RankRidge 5 horizon 各 339 picks）。顧問 payload 的 as-of 錨取 `max(panel_date) FROM prediction_values`（payload.py:167-170）＝**2026-05-31**——不會誤用更新但未走完下游的特徵面板，PIT 邊界自洽。live 數字升格為「確立級」前須過 `prediction_unfreeze_gate` evaluate（現況 frozen 未 evaluate）。

---

# 半-1 預測系統：逐子系統 HOW-built

## §3.1 ingestion+raw 資料品質：FinMind/FRED→DB 與語意驗證層

這層是 augur 最上游取數層與資料真實性的實證支柱，一體兩面。**(A) fetch 側**把兩個外部真實來源（FinMind v4 台股全 dataset、FRED/ALFRED 總經）忠實落地成 PostgreSQL 表——葉端 client 只回 API 原值、不算特徵不選股；靠單一限速門 + catalog/adaptive 驅動抓法 + DB-state resume 做到全史可續傳、零 hardcode 清單，並以獨立的 #7 byte-level 對帳證明 DB 與 API 逐值相等（無 AI 幻像）。**(B) raw 品質側**回答「抓進來之後，怎麼證明每一欄/每一 type 的語意是對的、髒值在哪、單位是什麼」——一批唯讀 profiler/verifier 逐表逐 type 據實驗出語意判準（不靠「我以為」）、回填進 `column_catalog` 當 DB SSOT，再用 writer-code 修補器（重抓非 hand-patch，#12）矯正壞資料。存在理由：所有下游 feature/model 的真兆假兆判準（#15）都繫於這批 raw 是 API 忠實原值、時點正確（anti-leakage #8）、語意正確、且可被機械重驗。

### 3.1.1 fetch 側怎麼建的（機制為主，含為什麼）

**分層薄化**：`finmind.py`/`fred.py` client 只做「一 dataset/series → 韌性化 GET → `list[dict]`」，欄名逐字照 API、FRED `"."`→None、每列補 `series_id`，建表/upsert 外包給 `generic_schema`；葉端零 DB 依賴故可 `ThreadPoolExecutor` 並發（fetch 並發、DB 寫序列）。

**三層防護收斂到單一 `_protected_get`**（`finmind.py:120`），六個公開 endpoint（fetch/fetch_dedicated/list_datasets/translation_datasets/translation/datalist）共用，確保「驗證與全史同門同限速」。每次 attempt 迴圈開頭固定 `_quota_gate()` 再 `_pace()`（`finmind.py:126-128`）：① **`_pace`** 鎖內預約下一發送時槽（`_next_slot`）、鎖外 sleep，thread-safe 維持 start 間隔 ≥ `MIN_INTERVAL`；② **`_quota_gate`** 每 `QUOTA_METER_EVERY=120` call 問權威錶 `/user_info`，`count ≥ limit − QUOTA_HEADROOM(200)` 時持 `_quota_lock` 全員暫停、退到一半以下續；③ **403 固定冷卻**保險網。設計哲學「見 403 前先停」——因額度是 rolling 視窗、本地計數含未知成分（實證 probe 403 時錶讀 5507<6000），故不本地推算、閉環問錶。**退避處置**（`finmind.py:145-149`，親驗）：`403` → `sleep(max(QUOTA_COOLDOWN=1800, retry_after))` 固定冷卻不短退避；**`402/429/5xx` 皆走指數退避** `backoff*=2`（非僅 429/5xx——402 亦在 `_RETRY_STATUS` 且 `!=403`）；且此「一律」有邊界：僅在 `attempt<max_retries` 時 sleep，最後一次改 raise（`finmind.py:151`）。`422` 刻意不在 `_RETRY_STATUS`（`:53`），`list_datasets` 送無效名才拿得到 422 的 dataset enum（列入重試則永遠拿不到）。

**adaptive 而非 hardcoded 分類**：`sync_finmind_dataset` 先由 `catalog._catalog_plan` 讀原料欄即時算 `optimal_mode` 走正解，失敗才回落 `_adaptive_sync` 五段探測（市場別寬窗→canonical 2330→by-date→維度 id→逐股）；dataset 全集靠送無效名觸 422 解 enum，抓取起點靠對 API 逐年逐月探測（`_bydate_data_start`/`_data_era_start`），全程零 hardcode 清單（#3）。**by-date 增量**把每日維護 request 從逐股 ~3100 筆降到「範圍內交易日數」（個位數）：交易型跳週末，事件型（News、date 帶時間戳）不跳（由 `_date_has_time` 依資料事實判、不假設，刻意避免漏抓週末新聞）。

**resume 純 DB-state-driven**：逐股一次 `GROUP BY stock_id, max(date)` 取全 roster 起點（取代 N+1 查詢，`sync.py:186`），by-date 用 `max(date)`，本 ingestion 路徑**無獨立 ledger 表**（範圍限縮：知識/驗證等其他子系統另有 `knowledge_embed_ledger`/`revalidation_ledger` 等 ledger/checkpoint，不在此範疇）。冪等 `ON CONFLICT` upsert 保重跑安全；抓取失敗（`rows is None`）記入 `failed_ids`/`failed_days`（`sync.py:201-202`）、真無資料（`[]`）不記——不記則 resume 只看 `max(date)` 會把漏抓當真空洞、永不回補。

### 3.1.2 FRED PIT 雙 tier 與 #7 byte 對帳

**FRED PIT 雙 tier**：Tier B（月/季/週會被回溯修訂）走 ALFRED 全 vintage（`realtime_start=1776-07-04`→`realtime_end=9999-12-31`、`output_type=1`，`fred.py:57-60`）保各版真 `realtime_start`，feature 層才能取 panel 當下可見版；Tier A（每日市場）`realtime_start=`觀測日本身（`fred.py:106`，當日即知＝正確 PIT）。兩 tier 強制共表 PK `(series_id,date,realtime_start)`，否則 Tier A 先落地窄 PK 會使 Tier B 多版於 `ON CONFLICT` 互蓋＝資料流失；落地前 `_fred_pk_ok` 程式守門（`ingest.py:103-127`），舊表 PK 缺 `realtime_start` 即 raise 拒落地（把 vintage 靜默塌版變程式強制錯誤，根治＝DROP 重建）。DB 實測 `fred_series` 343,967 列 / 31 series，其中 9 個為多 vintage（Tier B，精確 = {CPIAUCSL,GDPC1,INDPRO,M2SL,PAYEMS,UMCSENT,UNRATE,WALCL,WRESBAL}），與 `macro.py` 22 Tier A + 9 Tier B 逐一吻合、無 Tier A 誤帶多版。

**#7 對帳＝DB↔API byte attestation**，獨立於寫入路徑：`reconcile` 純唯讀算四類（matched/value_mismatch/missing_in_db/extra_in_db），attestation pass ⟺ `VM=0 ∧ EX=0 ∧ 非 incomplete`（`reconcile.py:404-413`）；任何日/股/維度抓取失敗即 `incomplete`→verdict 不給 pass（「沒比到 ≠ 比過且乾淨」，#15）。對帳法由 catalog `reconcile_scope` 路由到「與抓取同端點」的比對法——per-stock 表用 per-stock 端點重抓（避免 by-date/per-stock 兩端點微差造成假 VM，2026-06-17 三大法人 VM=73 實證）；唯一寫入者 `heal_by_date` 仍走 `sync_by_date` 的 upsert（非 hand-patch，守 #12）。比對前 `_norm` 對齊 `generic_schema` 防型別假 mismatch（數字 round 6 位、null/placeholder→None、bool 先於 float 判、前導零識別碼保 str）。

### 3.1.3 raw 資料品質/語意正確性驗證層（profile/verify/repair/annotate 七腳本）

> **v3 缺口界定（親驗，範圍收窄）**：v3 報告（20260710）對這 7 支腳本名（`profile_raw_data`/`verify_financial_type_semantics`/`verify_cashflow_cumulative`/`verify_units`/`repair_priceadj_basis`/`refetch_fixed_tables`/`annotate_schema_comments`）**零提及**（grep=0），且「raw-data 語意字典」之特定產物確缺（財報單季/累計/snapshot 判定、`type_caveat`/`dirty_value_note`、`origin_name` 解碼、PER 估值哨兵、PriceAdj-除息修復、單位交叉驗——相關 term 全 0）。**但**承重缺口範圍遠小於「整層無人擁有」：anti-leakage 偵測（v3 §3.2 `_anti_leakage_flag`）、snapshot 語意（`_refine_earliest_below`）、停牌哨兵 close≤0、塌列/reconcile 三類差異（v3 §3.7）已被既有 bucket 擁有。本節補的是**「這些判準怎麼被 profile/verify 實證出來」的產生側**。

**三段式管線，職責嚴格分離**：(1) 唯讀診斷產判準——`profile_raw_data`（逐表逐欄/逐 type 事實 profile）、`verify_units`（跨源單位）、`verify_financial_type_semantics`/`verify_cashflow_cumulative`（財報語意）；(2) 判準落地——報告 synthesis + 回填 `column_catalog.type_caveat`/`dirty_value_note` + `dataset_catalog.anti_leakage_note`；(3) writer-code 修補——`repair_priceadj_basis`（重抓）、`refetch_fixed_tables`（re-sync）、`annotate_schema_comments`（鏡射 catalog 進 PG COMMENT）。診斷側全唯讀 `db.transaction`，只有修補側才寫。

**財報語意用「演化式方法糾錯」而非一次定案**（每代 docstring 明寫修前代缺陷）：第一代 `profile_raw_data._is_cumulative`（`:34` `type=(SELECT type ... LIMIT 1)` + `stock_id='2330'`）只抽單股+任意單 type、naive；第二代 `verify_financial_type_semantics` 跨多股（tested≥5）同年四季 `|value|` 單調比≥0.8＝累計、≤0.4＝單季，並揭測試股數（#15 不抽樣推斷、tested<5 回「?樣本不足」）；第三代 `verify_cashflow_cumulative` 發現 `|value|`-單調對「會變號的現金流」失準，改用抗變號的 `median(|Q4|/|Q1|)≥2＝累計`（`verify_cashflow_cumulative.py:2-6`）。DB 實證三判定：**income=單季**（2330 Revenue 2023 四季 508B/480B/546B/625B，Q2<Q1 非單調）、**cashflow=累計 YTD**（CFO 385B/552B/847B/1242B 嚴格遞增）、**balance=snapshot**（TotalAssets ~5 兆時點水位）；三判定回填 `type_caveat`（「財報單季；發布日季底+45/90 日（release_lag gate #8）」/「現金流累計 YTD（需去累計得單季）」/「資產負債時點 snapshot」）。

**224 財報 type 碼由資料自身 `origin_name` 欄解碼**（source-pure，證實原以為需 FinMind 外部文件是錯的）：三表皆有 `origin_name`，distinct type 合計 = income 62 + cashflow 34 + balance 128 = 224；同一 type 碼跨期對多個中文變體（如 EPS→{基本每股盈餘, 基本每股盈餘(元), 每股稅後盈餘(元)…}，舊期混語編碼）。**惟需注意**（親驗）：`origin_name` 解碼屬資料屬性觀察，無 augur 腳本以它程式化建 type→中文映射（`annotate_schema_comments` 取 `column_catalog` 而非 `origin_name`）。

**單位靠跨源一致性交叉定錨**（`verify_units` 五道 A1-A5，比≈1 才定否則標待究）：A1 `Trading_money≈close×volume`、A2 財報季 Rev≈月營收×3（同時定兩源、揭出 catalog 月營收誤標千元→實為元）、A3 融資餘額比例、A4 持股 unit、A5 台積電 TotalAssets>1e12 驗元級。**單位結論屬「交叉驗定錨」強度、非官方文件鐵證**。

**writer-code 修補（重抓非 hand-patch，#12）**：`repair_priceadj_basis` 以 `factor=adj.close/raw.close` 單調回落掃描（`factor<prev*FACTOR_TOL(0.995)`）找損傷股——回溯調整序列每逢除息全史重算，增量 append 會把「舊基準史+新基準增量」拼接成損傷序列；對受損股整檔重抓單一現行基準（per-stock 一 request、走 `finmind.fetch` 三層防護）、同交易 `DELETE+INSERT`、逐股 commit（resume-safe），API 回 0 列則跳過留損傷不誤刪（`repair_priceadj_basis.py:63-66`）。**現況 175 檔 core_universe 股正損傷**（SCAN_SQL 實跑 `count(DISTINCT stock_id)=175`），為 live 除息復發之新鮮狀態、repair 器已備但殘留未清。`refetch_fixed_tables` 是「修 code→重抓補完整性」（#19）：修 `generic_schema` 型別邊界 + sync PK-null fallback 後，對截斷表 resume 續抓或 DROP 全史重抓——已使 FinalSettle 從「僅 1 列」→2799、FuturesDaily 5,818,071（1998-）、USStockPrice 35,052,889（1928-）、OptionDaily 33,928,645（2002-）。`annotate_schema_comments` 把 catalog 表/欄中文 + `zh_source` provenance 鏡射進 PG COMMENT，無中文來源不瞎補（`:70` skipped/`:80` warn，#15），刻意避開 FinMind `/translation` API（只支援 12 dataset 且翻 row-value 非欄名）。

### 3.1.4 機械閘與不變式（enforced_where）

- 所有 FinMind 請求無一例外先 `_quota_gate()` 再 `_pace()`（`finmind.py:126-128`），六個公開 endpoint 一律經 `_protected_get`（親驗恰 6 個實呼叫點）；start rate 唯一受 `MIN_INTERVAL` 約束、與並發數無關（**降並發無效**——`_pace` 鎖內預約時槽，語見 `finmind.py:38` 註解）。
- `403` → `sleep(max(1800, retry_after))` 固定冷卻；`402/429/5xx` → 指數退避 `backoff*=2`；`422` 不在 `_RETRY_STATUS`（`finmind.py:53`）故可拿 dataset enum。
- intraday 8 表（`INTRADAY` frozenset）一律不落地：`ingest.py:97-98` raise `IntradayRejected` + `sync.py:324/439` 三入口前置閘。
- `fred_series` 恆為 `(series_id,date,realtime_start)` 複合 PK；`_fred_pk_ok` 落地前守門，舊表缺 `realtime_start` 即 raise（`ingest.py:103-127`）。超單頁寧可 raise 不靜默截斷（`fred.py:97-98`，#15）。
- `#7` attestation pass ⟺ `VM=0 ∧ EX=0 ∧ 非 incomplete`（`reconcile.py:404-413`）；抓取失敗即 incomplete、verdict 不 pass。
- store 落地與 `data_audit_log`（dataset,data_id,action,rows）在同一 `db.transaction` 原子提交（`ingest.py:145-151`）；該表現 ≈25.8 萬列（live 增長、精確快照值不可重現，親驗已漂至 258,634+）。
- `require_keys=('date',)` 於逐股（`sync.py:199`）與 by-date（`:474`）強制 date 入 PK，防窄樣本 `detect_keys` 鎖 PK=stock_id 單欄致多日/多股 `ON CONFLICT` 互蓋塌列（2026-06-28 TaiwanStockDividend 2330 史失實證）；store 另對「值＝data_id 之維度欄」強制入 PK（`ingest.py:143-144`）。
- 診斷側唯讀不變式：`profile_raw_data`/`verify_*` 全程只 SELECT；`repair` 無參數路徑走唯讀掃描、只有 `--repair` 才進寫入。判準機械落地＝DB catalog 而非 code hardcode（`type_caveat=45` 欄、`dirty_value_note=23` 欄、`anti_leakage_note=3` 表，#29）。

### 3.1.5 陷阱（gotchas）

- **「兩型 403」是 docstring 概念、非 code 分支**：`finmind.py:145-146` 對所有 403 都同一固定冷卻，不會偵測 IP-sustained 型另行處理。
- **`FULL_START=1990`（`sync.py:36`）只是 backward-search 查詢下界、非資料起點保證**：實測 GoldPrice DB `min(date)=1979-01-01`——已由 catalog earliest 探測回填，v3「GoldPrice 被截成 1990」對現行 DB 已不成立。`sync_fred` **刻意不 resume**（每次 `start_date=None` 全抓），因 resume 用 `max(date)` 起點會漏掉首抓被 1990 截掉的 pre-1990 史。
- **`reconcile_scope` 程式支援 7 路由但 DB 現只有 3 值**：by-date（46 非排除）/roster-scoped（31）/by-dim-id（7）= 84；full-history/market/coverage 分支現無 dataset 觸發；且 by-date 實際經 `_has_date` fallback 命中、非具名 scope 分支（結果等價）。
- **`raw_data_profile` 是幽靈 forward-reference**：該表從未建立（`to_regclass` 空），只出現在 `profile_raw_data.py:18` 自身 SKIP frozenset；profiler 純 stdout 診斷、不寫任何表，catalog 的 caveat 回填是報告+人工 synthesis 驅動、非腳本自動寫入。`profile_raw_data._is_cumulative` 的「語意=」欄不可當定論、須看兩支 verify 腳本。
- **記憶索引「PER=-1＝虧損哨兵」與 DB 矛盾**：PER=-1 僅 2 列、PER=0 有 1,785,980 列（/總 7,593,287）才是主導非正值；判準需重新定錨（且 PER=0 究竟是虧損哨兵 vs 缺值/預設編碼、尚未獨立證明，勿照舊字典硬濾）。
- **TaiwanStockDividend 至今（07-13）仍塌列**：PK 仍 stock_id 單欄、2411 股各僅 1 列（2330 僅 1 列）；writer code 雖已修 `require date`（`sync.py:196-199`），但 DROP+re-sync 未執行，DB 現況壞資料——用 Dividend 全史的特徵會踩空。
- **PriceAdj 損傷是 live 結構性復發問題**（每逢除息增量拼接舊/新基準），repair 器是過渡期工具、非根治；長期正解＝庫內以 raw+除權息事件自建調整序列（arena plan §5）。BalanceSheet 有系統性覆蓋缺季（2018 僅 1 季、2016=3、2023/2024=2），是表級缺口非個股缺列。
- **`fetch_dedicated` 在自動 sync 路徑未被啟用**（dedicated 參數無上游傳非空值）；`BACKFILL_DEFERRED=frozenset()` 空集、相關分支現 dead（`ingest.py:42`）。`_data_era_start` fallback 探測種子股號硬編（'2317','2454','1101','2002'，`sync.py:143`）——屬探測啟發種子、不入庫，與 #3 邊界相容。

### 3.1.6 07-10（v3）之後的變化（delta）

- **`finmind.py MIN_INTERVAL` 由硬編 0.9 改為 env 可覆蓋**（`float(os.environ.get('FINMIND_MIN_INTERVAL','0.9'))`，commit 80dd1f3，2026-07-12）：新增退級開關供背景 audit 跑者以 2.0s 重掛（97 分鐘 0.9s 再觸 IP ban 實證）；預設 0.9 不變、三層機制本身未動。audit 看門狗 v2（log 停滯 45min 自動殺，commit c7656ac，07-13）+ `scripts/reconcile_audit.py` 背景對帳總驗 driver 現正背景執行——本子系統的 by-date audit 對帳在 live 增量維運（v1.9.0 解凍後）已是常態背景跑者、非一次性。
- **新增 `features/macro_vintage.py` PIT 消費讀取器 + `tests/test_macro_vintage.py`**（commit abf5da8，2026-07-11）：ingestion 端 vintage 落地的 consumer 側對照測試——證 Tier B 取 panel 當下現行版、拿不到未來修訂（GDPC1 2020Q1 於 2020-05 見 advance 初值、2025 見後修版且不同）、發布滯後→None、Tier A cutoff=panel−1（T+1 保守）、未知 series fail-loud。v3 未涵蓋此讀取器。
- **`sync.py`/`reconcile.py`/`ingest.py`/`fred.py` 自 2026-07-04（commit 4010382）起無實質變動**（git 確認）；v3 對這些檔的描述現仍成立，僅少數行號微調。
- **raw 品質層整層是 v3 空白**（7 支腳本 grep=0），但範圍收窄如 §3.1.3 界定。`repair_priceadj_basis.py` 為 post-v3 新增（commit e47e453，2026-07-12，E1/arena F2 修復鏈）；PriceAdj 現有 175 檔待修為 live 除息新鮮狀態。
- **catalog 語意/髒值標註持續累積**：`column_catalog` 較 2026-06-28 記憶（dirty 22 / type_caveat 32）成長至 `dirty_value_note 23` / `type_caveat 45`。`verify_units.py` A2「千元」標籤 bug 已修（commit 436b57a/b0216f5，現碼印「月營收=元」）、記憶索引「待修標籤」一條已 stale。停牌哨兵 `close=0` 列數由記憶「~28 萬（06-28）」增至現 611,822 列（live 增量累積、memory count 需刷新）。

## §3.2 core+catalog+generic_schema+DDL 遷移：建表/DB/元資料/schema 演化

橫切地基層，管「每一張表如何存在、如何演化」。四件事＋一條橫切機制：`config.py`（密鑰/路徑單一住所）、`db.py`（PostgreSQL 連線與交易邊界 context manager，刻意不建表）、`generic_schema.py`（看 API 資料**自動推型別建表冪等 upsert**、無 dataset 白名單、API 即權威）、`catalog`（對每個 dataset 探測「怎麼抓」持久化成 `dataset_catalog`+`column_catalog` 兩張登錄表）；再加 raw 之外**下游百餘張表**（登錄/閘門/帳本/機率/方向/審議…）由 **26 支 `migrate_*.py` 冪等 DDL 遷移**建立與逐步演化。核心設計是「三種建表模式各司其職」＋「治權紀律以 CHECK 閉集＋plpgsql trigger 寫死進 schema，讓紀律變成資料庫物理上無法違反的機械閘、而非靠 code 自律」。

### 三種建表模式各司其職（全子系統核心）

1. **generic auto-schema → API 原始表**：唯一生產 wiring 點是 `ingest.store`（`ingest.py:146` 呼叫 `provision_and_upsert`；全 repo grep 僅 def+此一呼叫，無任何 script/test 直呼——CONFIRMED）。無 dataset 白名單，任意 API dataset 都能落地（`generic_schema.py:17` docstring，#3）。
2. **explicit DDL → 運維/登錄表**：刻意用運維型別、**不套 API 表的 VARCHAR/NUMERIC 規則**——`schema.py:25-47 INFRA_DDL` 兩張 log 表（`id BIGSERIAL PRIMARY KEY` / `TIMESTAMP DEFAULT now()` / `TEXT`）、`catalog.bootstrap_catalog_tables:222` 兩張登錄表。`schema.py:14-16` docstring 明述「#5 的 VARCHAR(255)/NUMERIC(20,6) 是給 API 資料表、內部運維表自訂明確型別」。（精確化：`BIGSERIAL` 僅 infra log 表用；登錄表 PK 是 `VARCHAR(255)`/複合 VARCHAR，非序列。）
3. **builder / migrate 自寫 DDL → 下游計算/治權表**：core 只給連線與交易邊界。feature/universe 計算型走 builder-owns-DDL；登錄/gate/ledger/機率/方向/審議型走下述 26 支 `migrate_*`。

### core：密鑰單一住所與乾淨的交易邊界

`config.py` 由本檔實體位置 `parents[3]` 推得 `PROJECT_ROOT`（`config.py:20`），`python-dotenv` 載 `.env`，集中 `DB_PARAMS`＋`FINMIND_TOKEN`/`FRED_API_KEY`（`config.py:37-47`）。它是**唯一密鑰 reader**（grep 密鑰名於 `src/augur` 排除 config.py → 其餘皆用 `config.FINMIND_TOKEN`/`config.FRED_API_KEY`，無模組自 env 讀密鑰）；但**非唯一 env reader**——operational flag 多處直讀：`advisor/ollama.py:34,67,74…`、`query_translation.py:69`、`prompt.py:70`（`AUGUR_SIM_URL`）、`finmind.py:38`（`FINMIND_MIN_INTERVAL`）/`:90`（`FINMIND_QUOTA_GATE`）皆屬 URL/timeout/model/閘旗標（CONFIRMED）。`db.py` 的 `transaction(conn)` 區塊正常 commit、例外 rollback（`db.py:36-47`），使任一批失敗只回滾該批、重跑安全（#6）；docstring 明寫「不建表——infra 表由 schema.py、API 原始表由 generic_schema 各自負責」（`db.py:12-13`）。這 26 支 migrate 全共用 `db.transaction()` 這唯一交易入口。

### generic_schema：auto-schema 引擎與型別紀律

`provision_and_upsert:271` 一站式串 `infer_schema`→`detect_keys`→`ensure_table`→`upsert`。推型別看值：`YYYY-MM-DD`→DATE、純數字→`NUMERIC(20,6)` 超出自動加大、`FORCE_STR={stock_id,securities_trader_id,year,cb_id}` 識別碼強制字串免掉前導零、字串 >255→TEXT（`generic_schema.py:33-54`）。`detect_keys` 從 `KEY_CANDIDATES`（順序即偵測優先序 id→date→維度）貪婪挑最小唯一組合（`:45-53`）；其中 `realtime_start` 緊接 `date`，把 FRED ALFRED vintage 同 `(series_id,date)` 多版塌成一列的問題化解成 `(series_id,date,realtime_start)` 的 point-in-time 取版鍵（#8）；`is_after_hour/trading_session` 納入避免 Dealer 日盤/夜盤 2 筆退回全欄 fallback 把 volume 測量值塞進 PK。型別紀律「**只擴不縮**」：`ensure_table` 對已存在表補缺欄＋auto-widen（VARCHAR→TEXT/加長、NUMERIC 加大），首批窄樣本後續遇更寬值自動 ALTER；跨型別降級（NUMERIC/DATE 欄後續出現不相容值如契約月 `'200710'`、sentinel `'-1'`）用 `trim_scale(c)::text`/`c::text` 去尾零，使與 API 原字串 **byte-equal**（`generic_schema.py:232-241`，守 #7；CONFIRMED）。

### catalog：存原料、即時重算

`optimal_mode(c)` 是**純函式**（無 DB/API I/O），依原料算最少呼叫抓取模式與預估 call 數，不凍結會變的 `n_dates`（`catalog:273-291`）；其**國際股防呆**只讓 `data_id_source=='roster'`（台股名冊）走 per-stock，國際股 `src='none'` 改 by-date，刻意避免用台股 id 漏抓 UK/US/Japan（`catalog:287`，2026-06-16 實證 bug；DB 查 Europe/Japan/UK/USStockPrice 皆 `by-date`——CONFIRMED）。`probe_dataset` 對已落地表全讀 DB 真值、未落地走 finmind 分類 cascade；tier/intraday/single-day 由解析官方 `docs/finmind-references/datasets.md` 驅動，失敗才退硬編/probe 備援。中文名**不由 API 推**（FinMind `/translation` 翻科目值非欄名、實測 0 逐欄清單）→ 由 curated `docs/datasets_zh.md`（1345 行）seed（`catalog:143-163`）；DB `zh_source` 分布 金融=666/金融通用=53/FM=32/FRED=2/派生=1（DB 查——CONFIRMED，其中 `FM` 是策展者對來源的標註、非 code 動態取欄名）。`_anti_leakage_flag` 由欄名偵測 API 自帶公告/as-of 時點欄（`_ASOF_HINTS`，`catalog:371-378`，#8）；`earliest` 用 1955 哨兵窗偵測 snapshot date-insensitive 表→標 None（`catalog:760-763`）。

### DDL 遷移機制：26 支 migrate_* 把治權紀律寫死進 schema（gap 整合）

這 26 支（`ls scripts/migrate_*.py` 實測 26；其中 25 支符 `migrate_*_ddl.py` glob）是 raw 表以外**每張下游持久表**的存在與演化機制，橫跨 15+ 子系統、無任一 bucket 單獨擁有。統一骨架：白話 docstring＋執行指令矩陣＋DDL 常數（多為 `(label, sql)` tuple 清單）＋run/verify/status 三函式＋argparse，`import _bootstrap` 使個別可執行（#29a），走 `db.transaction()`（#6）。

**冪等三件套＋約束冪等的三種 idiom**：表用 `CREATE TABLE IF NOT EXISTS`、欄用 `ADD COLUMN IF NOT EXISTS`、seed 用 `ON CONFLICT DO NOTHING`；但 PG「`ADD CONSTRAINT` 無 `IF NOT EXISTS`」是隱性非冪等點，26 支用**三種不統一 idiom** 繞過：(a) `DROP CONSTRAINT IF EXISTS`+`ADD`（`migrate_prediction_ddl.py:41-45`）、(b) `DO $$ IF NOT EXISTS(SELECT FROM pg_constraint)`（`migrate_source_governance.py:57-75`）、(c) Python `ensure_constraint()` 先查 `pg_constraint`（`migrate_text_understanding_ddl.py:171-176`）——漏用任一直接 `ADD CONSTRAINT` 會在二次執行報 duplicate。

**機械閘寫進 schema**：大量 CHECK 閉集鎖 vocabulary（status/verdict/family/license/method/`horizon∈{20,40,60,82,120}`），加值域（`p_up BETWEEN 0 AND 1`）、XOR（`num_nonnulls(text_id,itext_id)=1`）、恆真 CHECK 讓欄永遠 true。超出 CHECK 表達力的紀律改用 **plpgsql BEFORE-trigger** 承載（07-11~07-12 才成形的新家族）：

- **挪門柱不可挪**：`direction_gate_no_goalpost`/`unfreeze_gate_no_goalpost`（`migrate_direction_gate_ddl.py:42-77`/`migrate_unfreeze_gate_ddl.py:47-80`）——凍結後 criteria 不可變、狀態轉移白名單、終態快照凍結、非草稿（direction 為 `preregistered`、unfreeze 為 `draft`）不得刪。兩支近同構、live 兩 trigger 皆在（DB 查 pg_trigger）。
- **真未來不可回填**：`arena_pred_no_backfill`（`migrate_direction_arena_ddl.py:97-99`）`pred_date` 早於台北今日−1 即 `RAISE`；`arena_pred_immutable`（`:110-126`）預測欄凍結、結算欄唯 `NULL→值`一次、DELETE 禁。機械上無法把預測補插進已過 horizon 偷看。
- **模擬永非預測**：`mc_simulation_run.is_simulation boolean NOT NULL DEFAULT true CHECK (is_simulation)`（`migrate_direction_ddl.py:92`）——欄物理上永遠無法寫 false。
- **fail-closed staging gate**：trigger `staging_source_gate`（plpgsql 函式名 `trg_staging_source_gate`；`migrate_source_governance.py:187-204`）非 active 源（含未知 source_key）BEFORE INSERT 即 `RAISE`，`manual_file` 豁免。
- **人拍板才 active**：`chk_ks_active_needs_approval`（`source_governance:67-70`，approved/active⇒approved_by NOT NULL）、`chk_ug_frozen_signed`（`unfreeze_gate:40-41`，frozen⇒簽核）；RBAC 刻意**不 seed** `knowledge_domain`（授權邊界須決策層逐列人拍板，`migrate_rbac_ddl.py:125`）。
- **confirmed 必帶證據**：`deliberation_verdict CHECK(verdict='undecidable' OR evidence IS NOT NULL)`（`migrate_deliberation_ddl.py:75`）。

**verify() 自帶驗收關（兩級）**：唯讀斷言（表/約束/trigger 用 information_schema/pg_constraint/pg_trigger 計數）＋**負向活體實測**（交易內插一列違規資料、預期 `RAISE`、無條件 ROLLBACK 零落地）——`knowhow_bridge --verify` 插 `cooc_sents=5`、`source_governance --verify` 插 proposed 源、`arena --verify` 三個 `_expect_raise`，都是「機械非自律」的證明。`migrate_probability_ddl.py:168-173` 另加**真隔離斷言**：查 `information_schema.table_privileges WHERE grantee='augur_predict'`，機率三表若有任何權限即判失敗。

**#29b「決定行為的資料住 DB」的具體落地**：`econ_verdict_rule` 把原硬編 dict 一次性 seed 成 5 列（`migrate_probability_ddl.py:97-108`；DB 查 `20|dead,40/60/82/120|thin_unestablished`），此後校準讀表非讀碼；`prediction_probability.econ_verdict` 與此逐 horizon 同列硬綁（D2，同列 NOT NULL 不可分離，非 DB FK）。`deliberation_lens`/`daily_topic`/`engine_config` 亦同——增列＝INSERT 零改碼；「新增類型」（新 model family/新 verdict 值）仍是 DDL/CHECK 變動（邏輯側），資料/邏輯二分清楚。

### 機械閘與不變式（速查）

- **主鍵首建固定**：`ensure_table` 對既存表末行 `return db_primary_key(cur,table) or list(keys)`（`generic_schema.py:242`），`require_keys` 只在首建生效——防後續小樣本推更窄鍵覆蓋資料。
- **fred_series 靠程式守門**：因「PK 首建固定」使 require 對舊表無效，`_fred_pk_ok` 讀 `pg_index`，PK 不含 `realtime_start` 即 `raise` 拒落地（`ingest.py:103-113,123-127`；DB 查 PK=`(series_id,date,realtime_start)`——CONFIRMED）。
- **併發首建安全**：`SAVEPOINT _ct` 隔離 CREATE，撞 `DuplicateTable/DuplicateObject/UniqueViolation`→`ROLLBACK TO SAVEPOINT`→重讀 columns 走補欄路徑、不丟該批（`generic_schema.py:196-210`，親驗）。
- **NULL 語意三處統一**：`_NULL=('','none','null','nan','nat')` 同時用於取樣/主鍵判定/寫入 `_coerce`（`generic_schema.py:58`），否則「判為有值進主鍵但寫入轉 None → NOT NULL 違反」。
- **store() 動態擴充 require_keys 防塌列**：by data_id 落地時把「值等於 data_id 的維度欄」（currency/name）強制入 PK，防不同 id 同 date 互相覆蓋（`ingest.py:143-144`）。
- **登錄表冪等寫入**：`_upsert_dataset` 用 `ON CONFLICT(dataset) DO UPDATE`、`last_verified` 用 SQL `now()`；`_upsert_columns` 先 DELETE 該 dataset 再 INSERT（重探即全換，`catalog:303-316`）。
- **knowhow 橋以 schema 為 SSOT**：build 端 `MIN_COOC_BRIDGE=30`（`build_field_knowledge_bridge.py:24`，註「與 DDL CHECK 同值(schema 為 SSOT)」）對齊 DDL `CHECK (cooc_sents >= 30)`（`migrate_knowhow_bridge_ddl.py:50`，live 實有）。
- **換模不靜默假成功**：嵌入表就地遷移為 `(id, model_tag)` 複合 PK（`migrate_text_understanding_ddl.py:186-193`），防換模重嵌 `ON CONFLICT DO NOTHING` 靜默假成功。
- **純函數回歸測試守核心**：`tests/test_generic_schema.py` 16 個測試鎖型別推導/主鍵偵測（含 by-date require 防塌、Dealer `is_after_hour` 須入 PK 而非 volume）/NULL/sentinel 邊界，皆 clean-room 不打 API/DB。

### 陷阱

- **「數字落地永不經 Python float」不成立（v3 沿用需更正）**：`_coerce` 本身確實不呼叫 `float()`（`generic_schema.py:245-249`，此窄述為真），但它是 pass-through 保留輸入型別——FinMind 以 JSON 數字回傳的欄位在 `resp.json()` 階段即成 Python `float/int`，經 `_coerce` 走 `else v` 原樣落地並由 psycopg2 float 轉接。故此不變式**僅對「以字串抵達之值」成立**，非普遍保證；程式並未 `str(v)` stringify 以強制之。（`_digits:87` 的 `float()` 只用於推 NUMERIC 寬度、不碰落地值。）
- **catalog 元資料相對現況 STALE**：`last_verified` max=2026-06-29；84 個已落地 dataset 中 82 個 `source_provenance` 仍標 `probe`（僅 TaiwanStockInfo/fred_series 2 個標 DB）；表級 n_stocks 嚴重低估——`TaiwanStockPrice` catalog `n_stocks=3102` vs DB `count(distinct stock_id)=54309`（含權證，DB 查）。欄級 `column_catalog` 仍準。要對齊須重跑 `build` 或 `build(db_only=True)`（後者只更 column、不動表級 provenance）。
- **stale docstring**：`catalog/__init__.py:14` 與 `build_catalog.py` 皆稱 `build()/refresh()` 打 API，但**檔內無 `def refresh`**（grep 0 命中）；真正 refresh-like 路徑是 `build(db_only=True)`。`migrate_deliberation_ddl.py:2` 仍稱「5 表」但 live 已 16 表（DB 查）——docstring 精確描述本遷移固化的 5 表、其餘 11 表另有出處，惟「deliberation_* 5 表」一語已不反映表族現規模。`import_database.sh:16` 仍稱「13 支」但 25 支符 glob。
- **中央 runner 旗標慣例 footgun（更正版）**：26 支存在兩種相反旗標慣例並存——`build-on-default`（無參數即建表、僅 `--check/--dry-run/--show` 唯讀）者共 **11 支**（如 prediction/text_understanding/revalidation_ledger/risk_policy/topic_alias…），須 `--run/--migrate` 才建者 **15 支**（deliberation/direction*/probability/rbac/source_governance/unfreeze_gate/validation_evidence/knowhow_bridge…）。而 `import_database.sh:158` 的 `for m in scripts/migrate_*_ddl.py` 對每支以**無參數**呼叫並 `&& echo ✓`，故那批 gated `_ddl` 腳本被靜默 no-op（`return 0`）卻仍印 ✓——**真 footgun**：新增 `--run-gated` 遷移後、舊 dump 的 `--migrate` 補跑會假成功、實際沒補表。另 `migrate_source_governance.py` **無 `_ddl` 尾、根本不被 glob 匹配**（25 支入迴圈、非 26），且它本就需 `--run --snapshot`（無快照 `sys.exit`），命名慣例例外要人記得。
- **反向 SSOT 漂移（違 #12）**：live DB 有 `chk_itext_owned_local_private`（`license=owned_local ⇒ access_scope=local_private`，DB 查 pg_constraint 實有），但 **26 支遷移無任一支 `ADD CONSTRAINT` 建它**——全 repo grep 唯一命中是 `acquire_local_files.py:63-65` 的 `sys.exit` 護欄（非 DDL）。故 clean-room 依遷移重建**不會重現此 CHECK**，可攜的強制其實只是 Python 護欄。
- **BACKFILL_DEFERRED 空集致 dead code**：`ingest.py:42 BACKFILL_DEFERRED = frozenset()`（鉅額已移入 OUT_OF_UNIT），`catalog:853-858` 對應分支恆不可達，屬刻意保留的框架佔位。
- **硬編軟白名單與 QUOTA 過期**：`_DIRTY_VALUE_NOTES/_SPONSOR_ONLY/_SINGLE_DAY` 等硬編 dict 是需人維護的 code 資料，與 #29 有張力；`QUOTA_EXPIRY='2026-06-24'` 硬編且已過期（今 2026-07-13，DB `quota_expiry` 亦全為此值）。
- **prediction_values 隔離僅 COMMENT、非機械（v3 REFUTED、未修）**：`migrate_prediction_ddl.py:61-63` 只 `COMMENT`（自稱「AST+GRANT 雙閘」但無實際閘 code），`setup_predict_role` 把該表 GRANT 給 predict role 可讀寫，無閘阻 pipeline 回讀當特徵；對比機率層已加真 GRANT 斷言（僅覆蓋機率三表、未回頭補 prediction_values）。

### 07-10（v3）之後的變化

- **core+catalog code 零變更**：`git log --since=2026-07-10` 對 core/、`catalog/__init__.py`、`build_catalog.py`、`datasets_zh.md`、test 皆 0 commit；v3 §3.2 機制描述仍逐字有效。實質變化在 **DB 狀態**：v3 稱「已落地表全讀 DB 真值 vs 未落地走 probe」是 build 當下語義，現況因 wave1/full_market_sync 大量落地、82/84 個 landed dataset 的 provenance 卡在 `probe`、n_stocks 嚴重低估——v3 未凸顯的新張力。全庫 base table 現達 231 張，但 `dataset_catalog` 僅登錄 95 個 API dataset registry 行、`column_catalog` 754 欄（DB 查）——登錄表只涵蓋 raw 取數層。
- **DDL 遷移涵蓋面倍增**：v3 時代 `import_database.sh` 註解稱「13 支」，現 26 支（25 符 glob）；v3 主要逐檔談 prediction/rbac/text_understanding/probability（部分），對 gate/arena/ledger 群著墨少。**全新機制類別**：plpgsql「挪門柱/反回填/不可篡改/fail-closed staging」trigger 家族在 **07-11~07-12** 才成形（`direction_gate_no_goalpost`/`unfreeze_gate_no_goalpost`/`arena_pred_no_backfill`/`arena_pred_immutable`/`staging_source_gate`〔函式名 trg_staging_source_gate〕，live 皆在）——治權紀律入 schema 的手法從「閉集 CHECK」升級為「狀態機 trigger」。
- **owned_local 漂移「部分收斂＋反向再開」**：v3 說 live 之 `knowledge_item_text` license CHECK 尚未含 `owned_local`；現 license CHECK 含 `owned_local`（遷移 DDL 已補並跑到、SSOT 一致），但 `chk_itext_owned_local_private` 反而 live 存在卻無任何 committed 遷移建它（07-10 後被人工加入 live 卻未入遷移，正好構成上述反向漂移）。
- **#29b 新落地**：`econ_verdict_rule`（硬編 dict→5 seed 列）、`deliberation_engine_config/lens/daily_topic` seed、`deliberation_bench_batch`（GATE 預註冊）——把裁決閾值/題庫/校準規則從 code 外置到表。v3 標記之 gotchas（refresh 不存在、QUOTA_EXPIRY 過期、require 只首建生效）本次逐一親驗確認仍成立、無修復。

## §3.3 features+特徵發現工具鏈:35特徵EAV+四道提拔漏斗

**▶ 一句話**：features 子系統把「raw 真實 API 值 → 可被模型排序的乾淨特徵」這層數學轉換集中在一處，每股從 source-pure raw 算 **35 個生產特徵**、以長窄 EAV（`(panel_date, stock_id, feature, value)` 一列一特徵）寫入 `feature_values`；在此層機械強制三敵人零容忍——source-pure（算不出即缺列不捏造）、anti-leakage（面板日只用 ≤t 已公開資料）、思想≠特定值（八二/康波當假說鏡頭、特定數字不入公式）。**這 35 特徵怎麼被找出來的**，答案在另一層「特徵發現研究工具鏈」（§四提拔漏斗，見本節下方子節）：發散撒網掃描 → 建構 as-of 候選 → 過四道漏斗+經濟終關才晉為生產。DB 實查現況：`feature_values` 恰 **35 distinct 特徵、2,510,040 列、36 個 panel（2007-12-31 ~ 2026-06-30）、3093 檔**，由 6 支產生器貢獻——`panel.py` 14（13 價量 + `monthly_revenue_yoy`）、`chip.py` 7、`valuation.py` 5、`concentration.py` 4、`phase.py` 4、`margin_cycle.py` 1（DB 逐特徵 GROUP BY 全數歸位；`panel.py:30` 只 import chip/concentration/margin_cycle/phase/release_lag/valuation，其中 release_lag 是 gate 非生成器）。

### 怎麼建的：組合根 fan-out 與兩種缺列 regime

`build_panel`（`panel.py:124`）是**組合根 fan-out** 也是**唯一「常態生產」寫入者**：對每股跑「兩段 DB transaction + 一段 insert」——第一段查還原價/月營收 + 呼叫 chip/valuation（`:130-136`），第二段呼叫 phase/margin_cycle（`:155-157`），concentration 不需 cursor（`:154` 吃第一段已抓的 price df），最後 `execute_values` 批次 upsert。逐股獨立 transaction 讓長跑可續、單股失敗不連坐。**刻意的非統一 per-module 契約**：`compute_features(df)` / `concentration(price_df)` 只吃純還原價 df；chip/valuation/margin 簽章是 `(cur, sid, panel_date)` 需查 DB；phase 混合——反映「純價格數學轉換 vs 跨表 join」的本質差異，不強行統一介面。

35 特徵按產生器歸位（DB GROUP BY 逐一核對）：
- **panel.py 14**（`compute_features` 產 13 純還原價 df 特徵 + `_compute_revenue_yoy`）：`return_1d`、`momentum_{5,20,60,120,252}`、`volatility_60d`、`dollar_volume_log_20d`、`turnover_mean_20d`、`range_mean_20d`、`price_to_252d_high`、`cycle_position_252d`、`volume_surge_5_60` + `monthly_revenue_yoy`。
- **chip.py 7**（籌碼；含 f4 `top_holders_pct` 集保 + f5-f7 借券/融資/官股 E 類真零）。
- **valuation.py 5**（估值；含 `price_to_10yr`）｜ **concentration.py 4**（八二 P3）｜ **phase.py 4**（康波 C2×2 + C4×2）｜ **margin_cycle.py 1**（康波 C3 `gross_margin_pctile`）。

**價格基準統一用還原價 `TaiwanStockPriceAdj`**（2026-06-27 審查 R1/R5 修）：(a) 除權息跳空非真報酬、原始價污染動能/區間位置；(b) 還原價表無停牌 `close=0` 哨兵列 → 改還原價即自動剔停牌、免 252 窗 min 被 lo=0 污染致 cycle 退化。另加 `close>0` 防衛 + **還原價 master gate**：無 ≤t 價量列 或 最近價距 panel > 45 日（`MAX_STALE_CALENDAR_DAYS`，`panel.py:35`）→ **整股完全不寫任何特徵**（連已算好的 chip/valuation 也丟棄，`panel.py:137-144` `rows=[]` → `continue`），不輸出 stale 偽 as-of。

**EAV 長窄表刻意選型**：PK `(panel_date, stock_id, feature)` + `value NUMERIC(20,6) NOT NULL`、`ON CONFLICT DO UPDATE` 冪等（DDL `panel.py:36-43`；information_schema 確認 value 為 numeric 精度 20 標度 6、三主鍵欄與 value 皆 `is_nullable=NO`——**型別由 DB 強制、非僅 code 約定**）。用 upsert 換取「特徵維度可增量演進」：新增特徵後重跑 `build_feature_panel` 即把新特徵補進既有面板，不需改 schema、不需 migration。

**兩種缺列 regime 刻意非對稱**（此為 pilot v3 教訓修正——原把 E 類誤當 P 類入完整度 gate → 跨多 panel 交集塌成 0 核心股）：
- **P 類（連續、活躍股每期有值）**：算不出即 dict 不含該 key（缺列）；各產生器末尾 `{k: float(v) for ... if v is not None and np.isfinite(v)}` 純函式濾網（`compute_features` 收尾、`concentration.py:56`、`phase.py:43/76`）。
- **E 類（chip f5-f7 借券/官股事件型稀疏）**：真零語意——無事件填中性 0，**但只在 `_table_covers` 雙側機械 gate 通過時**才填 0（`chip.py:163/170/176` 三個 if），否則仍缺列（防把「源表未 sync」誤當「真無事件」捏造零）。`_table_covers`（`chip.py:48`）= `min<=panel AND (panel−max).days<=14`（`_MAX_STALENESS_DAYS=14`，`chip.py:45`，源自實測 3 表相鄰事件日 gap max=13、含 CNY 長假）。此 gate **實證生效**：`gov_bank_net_buy_60d` 最早 panel=2021-09-30（DB 查），因源表 `TaiwanStockGovernmentBankBuySell` 始於 2021-07-01，2021Q3 前 panel 因 `min≤panel` 為 False 被主動排除；決定性反證＝panel 2021-06-30 確實存在（71,892 列）但該特徵於此 panel 為 0 列。DB 零占比：sbl 35.4% / lending 37.1% / gov_bank 10.4%（真零、非缺列）。

**八二/康波兩鏡頭以「思想可入、數字不回流」建**（#9/#16）：不用 0.8/0.2 或 40-60 年，`concentration.py:22-39` 用 cutoff-free `_gini`/`_max_share` 泛函量「分布多不均」、`phase.py:24-30` `_range_position` 用資料自身歷史 min/max 定「現在在循環哪裡」。六軸只留過第 4 道漏斗的存活軸：八二僅 **P3 量能集中 4 特徵**（`volume_gini`/`volume_max_share` × {20,60}）、康波 **C2 價格相位 2**（`range_position_120d`/`days_since_high_252d`）+ **C4 法人累計流相位 2**（`inst_cumflow_position_{60,120}d`）+ **C3 毛利循環 1**（`gross_margin_pctile`）；淘汰者如八二 P1 持股集中（與 `top_holders_pct` 共線 +0.97，`concentration.py:8-11` 提拔結論註）退回 git 史。

### 機械閘與不變式

- **feature_values 型別/PK/冪等**：`NUMERIC(20,6) NOT NULL` + PK 三欄，DB 強制（`panel.py:36-43`）；`ON CONFLICT DO UPDATE` 保證冪等重跑。
- **source-pure #1**：算不出（歷史不足/除零/NaN/inf）→ 不寫該列（各產生器 isfinite 純函式濾網）。
- **anti-leakage #8（命門）**：全 SQL `date <= %s` 純後向；期間型資料額外套**發布日 gate**（抽成獨立 `release_lag` 模組）——月營收套 `revenue_released`（`panel.py:147-148`）、財報套 `financial_released`（`margin_cycle.py:47`）、集保大戶比套 `holdings_visible_cutoff`（`chip.py:145`）。三組常數定位：**`REVENUE_DAY=15`/`FIN_LAG_QUARTER=45`/`FIN_LAG_ANNUAL=90` 是台灣法定公告期限（法律事實），故不違 #9**；但 **`HOLDINGS_LAG_DAYS=7`（`release_lag.py:31`）性質不同——TDCC 集保無發布日欄可查，這是「週五快照、寧晚勿早」的保守審計近似（2026-07-11 審計 1A 拍板），非嚴格法定值、待 probe 精修**，不宜與前三者一概稱「法定」。
- **E 類真零前提由機械 gate 強制**（非僅註記）：`_table_covers` 雙側任一不覆蓋即缺列不填 0（見上）。
- **候選污染隔離為機制性**：`feature_candidate.py:28-29` `PROD_TABLE=feature_values`（唯讀來源）/ `FEATURE_TABLE=feature_candidate_values`（audit 自建 staging、schema 同構）；生產 `baseline.canonical_features`（`baseline.py:37-44`）只 `SELECT FROM feature_values` **完全不觸候選表** → 官方候選流程結構上不可能污染核心。**但此隔離不是全域絕對**（見陷阱「雙層隔離不對稱」）。
- **canonical 模型特徵集 = 交集 = 29 非 35**：`baseline.canonical_features` 用 `HAVING count(DISTINCT panel_date)=len(pds)`（`baseline.py:41-44`）取「`CANONICAL_START='2008-12-31'` 起每個 panel 都出現」之特徵交集，實測 **29**；6 個因源表起始日致早期 panel 部分覆蓋的特徵被交集 gate 排除（DB 實列：`gov_bank_net_buy_60d`/`inst_cumflow_position_60d`/`120d`/`institutional_net_buy_ratio_20d`/`price_to_10yr`/`top_holders_pct`），確保跨 panel 維度一致。
- **提拔關卡機械閘**：IC 顯著性**禁裸用 iid `effective_t`**（審查 G8，重疊 label 窗高估），須 Newey-West Bartlett-kernel HAC Eff-t（`metrics.py:89` `effective_t_hac`，lag=floor(4·(n/100)^(2/9))、n<3 或 LRV≤0 → None）；判準一律 **|HAC-t|≥2**，iid 只作對照。

### 特徵發現研究工具鏈（§四提拔漏斗）——「發現→提拔」的研發流程層

這是相對於 features/「成品層」的**研發流程層**，回答「35 個生產特徵是怎麼被找出來的」。核心精神：「**生成發散、篩選收斂**」，且「**是市場、不是我，決定哪個特徵有用**」——絕大多數候選在漏斗被淘汰、飽和是常態。方法論 SSOT ＝ `reports/augur_feature_discovery_methodology_20260626.md` §四（憲章入憲引用）、SOP ＝ `reports/augur_core_feature_sop_20260629.md`；全鏈本地零 Claude usage（#28）。

**三段式管線「寬網→緊閘」**：發現層撒網找方向 → 建構層（`verify_*_candidates` 把浮現訊號做成 as-of 安全的 `x_` 前綴實驗特徵）→ 提拔層（同一批 `verify_*` 對候選跑漏斗判生死）。發現層六支各司一職：
- `run_raw_interaction_ic`：raw 欄橫斷面 rank IC + 78 對 z-乘積交互（crude iid t 前身、07-11 改 as-of PIT）。
- `run_deep_interaction_scan`：18 正規化訊號（逐法人別籌碼/借券/當沖 × 多 horizon）× 全對交互、直算 HAC-t（`money×inst_net`、`foreign_pct×turnover` 由此浮現）。
- `run_cross_table_interaction_scan`：跨表跨群兩兩交互（GROUP 只配不同群）、z 乘積(協同)/z 差(分歧) 兩 transform、含 release_lag gate 的財報/月營收腿。
- `run_field_correlation`：raw 欄兩兩相關 + lead-lag（predictive、#8 安全）→ 底料候選來源。
- `run_feature_audit`：接 `feature_diagnostics.five_mirror` 五鏡合判（單因子有號 IC/共線/LOO/SHAP/purged）、裁定供人合判非自動刪。
- `run_horizon_universe_scan`：換 horizon（5/20/60/120/252）× 換宇宙（core vs 擴大 ~3080）掃描，測 alpha 是否推廣到更多名（飽和後的逃脫方向）。

**發現層刻意用寬鬆 pan-hist `core_universe`**（含 look-ahead、放大 IC 只為找方向，`run_field_correlation.py:26`/`run_feature_audit.py:33`/`validate_feature_candidates.py:33`）；**所有特徵候選提拔層一律收緊到 as-of `core_universe_asof`**（逐 panel PIT、消 survivorship，`run_deep`/`run_cross`/`verify_matthew`/`verify_fundamental` 等）——看發現層數字不能當結論、只是候選方向。（提拔層宇宙口徑之精確表述限「特徵候選 verify_*」；哲學/知識層 `verify_philosophy_factors.py:29` 等仍用 `core_universe`，不在此特徵漏斗內。）

**掃描工具經三次方法論自我糾錯逐步強化、演變史寫進 docstring**：(a) t-stat 從 crude iid（`run_raw_interaction_ic.py:169` `mean/std*sqrt(n)`、重疊窗高估）升級為 HAC（`run_deep`/`run_cross` 改用 `metrics.effective_t_hac`）——同一訊號 iid vs HAC 可能一個顯著一個不顯著，crude 高 t（如 money×inst_net）**不可採信、必須送提拔複核用 HAC 重測**；(b) 宇宙從固定名單回填升級為 `core_universe_asof` 逐 panel PIT + 全期成員聯集含已下市股，消存活者偏誤（commit cd8b35e，2026-07-11；聯集之具體下市檔數未於 code/docstring 載明，**未親驗**）；(c) 交互從「群內兩兩」擴到「跨群兩兩」（`run_cross_table` GROUP 只配對不同群、`run_deep` 逐法人別 × 多 horizon）。

建構/提拔層候選 verify_* 按鏡頭分軌：
- `verify_fundamental_candidates`：P5 八二（營收產業 share/馬太）+ C3 康波（庫存 Kitchin/毛利循環相位），發布日 gate；被 reexam/stability 以模組載入復用其 `_compute`/`CANDS`。
- `verify_interaction_candidates`（Track A 跨鏡交互 3 候選：gini 剔 size 殘差/流相位背離/價流相位背離）｜ `verify_matthew_candidates`（Track B 八二 P6 馬太 rank-pct ~1yr 變化）｜ `verify_daytrade_candidates`（當沖比/買賣不均）——皆寫 staging 表過漏斗。
- `verify_signal_promotion`/`verify_interaction_promotion`：對 `run_deep` 浮現訊號（`dealer_net_r`/`foreign_pct×turnover`/`money×inst_net`）跑完整漏斗、iid-t vs HAC-t 雙口徑（**直接注入 feature_values 再 DELETE**）。
- `validate_feature_candidates`：接 `audit.feature_candidate.compute_candidates`（PBR 三層相對化 + govbank×inst 背離 4 候選）+ five_mirror，寫 staging。

**候選建構嚴守 #9 cutoff-free 與母原則③相對化**：全部是 data-driven 泛函——OLS 殘差剔 size（`x_gini_resid_size`，`verify_interaction_candidates.py:52`）、橫斷面 z 差背離（`x_flow_phase_divergence`）、rank-pct 的 ~1yr 變化（馬太 `verify_matthew_candidates.py:36-63`，`rank(pct=True)` 差分）、自身歷史百分位、TTM 營收產業 share / 庫存÷4 季營收 Kitchin 比（`verify_fundamental_candidates.py`）——grep 候選 builder 之硬編預測閾值（PER<15/top-20%/N 年循環）為空，僅結構性回看窗與顯著檢定。

**漏斗是三段 AND（鏡射方法論 §四漏斗4）**：① as-of 逐 panel 單因子 rank IC + iid-t 對照 HAC-t（**|HAC|≥2 才算顯著**）② 共線（vs 既有生產特徵、剔冗餘）③ 多 seed（≥3）多因子增量 Δ（候選加入生產集後 Ridge/GBDT mean IC 是否穩定正增量、Δ≤0 = 已被涵蓋）。**須誠實界定機械 vs 人裁**：程式**唯 ①HAC≥2 段是自動 short-circuit gate**（`verify_fundamental_candidates.py:164` `abs(hac)>=2 → passed=True`、`:173 if passed:` 才跑昂貴的多因子 ladder、`:181` else 印「單因子 HAC 全 <2 → 不續多因子；不提拔（省算 #28）」，`verify_daytrade_candidates.py:114/121/132/137` 同構）；②共線與 ③Δ>0 是**判讀行（人裁）**（`verify_fundamental:182`「HAC|≥2| + 低共線 + 多因子增量正 → 提拔」），非硬 code gate。第 4 道漏斗的獨立工具是 `verify_candidate_promotion.py`（iid-t vs HAC-t 雙口徑欄 `:103-113`、多 seed 增量、驗後不入生產）。

**收尾是經濟終關 + 穩定性關（#14/#15）**：`verify_economic_candidate.py` 把候選加入後跑 `portfolio.run_backtest`、扣台股來回成本 **`COST=0.00585`**（`:26`），比 net Sharpe/Calmar/MaxDD 對等權基準（因「IC 撐住 ≠ 可交易 alpha、靈魂成功定義是經濟價值非 IC」）；`verify_stability.py` 進一步防單期僥倖——逐期 Δnet 正期比例 + t（`:80`）、Leave-one-period-out ΔCalmar 最壞值（`:88-94`）、前後子期各自成立、top 10/20/30% 分位一致（`:106-115`），四項全過才 productionize。

**發現的方法瑕疵「覆蓋假象」並就地修正**：`baseline._panel_matrix` 剔除缺任一特徵之股（`:66-69` `if len(fv)==len(feats)`），故加一個稀疏候選（覆蓋 ~63%）會讓宇宙掉 ~37% → **ΔIC 假跌純屬宇宙縮小、非候選有害**，會冤殺真訊號。修法＝`verify_incremental_fair.py`/`reexam_sparse_candidates.py` 把候選缺值以「該 panel 橫斷面中位數」補滿（中性、rank 居中）→ base 與 +候選跑同一宇宙，Δ 才真反映增量（此 impute 限「公平同宇宙 Δ」診斷用、非入生產）。

**口徑全 reuse evaluation SSOT helper**（`label.labels`/`metrics.rank_ic`/`baseline.run_ladder`/`walkforward.splits` embargo=h+62td/`release_lag.*` 發布日 gate/`portfolio.run_backtest`）——scan/verify 腳本本身只是薄編排 + 候選計算邏輯，不自造指標數學。每支守 #29(a)(d)：`import _bootstrap`、標頭指令矩陣、無參數 graceful、驗後 `--clear`/DELETE 復原。

**全鏈淨結論＝飽和**：跑遍群內/跨群/多 horizon/換宇宙，**唯一過四道漏斗 + 經濟價值的候選是 `inter_fh_x_p10yr`**（外資持股 × 10 年線位置 z 乘積），且 opt-in、限 374 核心宇宙、換寬宇宙 ΔIC 轉負（−0.0005）、**不設生產預設**（`cross_section.py:17-24`）；**`feature_candidate_values` 現 0 列**（DB 查）＝至今無任何候選由這些工具晉為生產特徵。這正是方法論的誠實勝利。

### 陷阱

- **「panel 唯一寫 feature_values」須限定為「唯一常態生產寫入者」**：另有 **7 支**離線腳本直接 `INSERT INTO feature_values`（注入候選 → 驗 → DELETE 復原）——`reexam_sparse_candidates`/`verify_economic_candidate`/`verify_economic_reexam`/`verify_incremental_fair`/`verify_interaction_promotion`/`verify_signal_promotion`/`verify_stability`（DB grep 精確 7）。**v3 報告記為 8 支已過時**：較新的 candidate 家族（`verify_fundamental`/`interaction`/`matthew`/`daytrade`/`validate`）已改寫入獨立 `feature_candidate_values` 表、不再直寫生產表。
- **雙層隔離不對稱（最大陷阱）**：官方 staging 候選（`feature_candidate.py`）是**機制性隔離、安全**；但上述 7 支 verify 腳本圖方便直寫生產表，其隔離**退化為紀律性**——base 須手動排除候選名（`verify_stability.py:66` `[f for f in canonical_features(...) if f not in fu.CANDS+[IMP]]`），`verify_stability.py:65` 明白警告「base 須排除全部實驗候選…否則 base 汙染」。故「候選數學上不可能進核心」是**過度宣稱**：若 INSERT 與 DELETE 之間崩潰，全覆蓋候選列會殘留於 `canonical_features` 所讀之表、被 base 吃進去、Δ 失真。正確版：官方候選流程機制性隔離；7 支 legacy verify 為紀律性 INSERT→DELETE、非「數學上不可能」。
- **名實不符特徵未改名（rename 漣漪成本）**：`lending_fee_rate_mean_30d` 名「30d」實＝最近 100 筆借券成交（`_LEND_SQL LIMIT 100` 無日期下界、窗跨中位 ~1.5 年）；`gov_bank_net_buy_60d` 名「60d」實＝最近 ≤60 個官股**事件日**（非交易日/日曆日）；語意以 `chip.py:94-104` 註 + catalog 明標，因漣漪 4 檔/77k+48k 列故保留舊名。
- **`volatility_20d` 已因與 `range_mean_20d` 共線 +0.94 經五鏡剪枝、code 不產**（`panel.py:105` `for w in (60,):` 同行註）；DB 確認只有 `volatility_60d`（78,957 列）、`volatility_20d` 不在 35 特徵。
- **off-by-one 視窗需求不一**：`momentum_252d` 需 253 列（`n>w`，`panel.py:102`）、`price_to_252d_high`/`cycle_position_252d` 只需 252 列（`n>=252`）。
- **chip 日頻籌碼 T+1 精確公布時刻 gate 未做**（`chip.py:19` 承認）：法人/融資券/借券現採保守 `date<=panel` 同日含，「上線後待 probe」——集保 f4 已於 07-11 補發布日 gate、其餘未補，已知未修的 anti-leakage 邊角。
- **財報 lag 產業別缺口（休眠債）**：`release_lag` 一律 45/90 日無產業分支，金融保險/證券/期貨業法定 Q1/Q3 為 60 日（`release_lag.py:16-22` 揭露）；現況唯一消費者 `gross_margin_pctile` 已因 #15 陳舊守衛排除金融股故不觸發，但未來若讓 panel 季中/月頻消費金融股財報會顯現此漏。
- **crude iid t-stat 是刻意保留的高估版**：`run_raw_interaction_ic.py:169` 的 iid t 會高估顯著性，其高 t 不可採信、必送 HAC 重測（同一訊號兩口徑可能結論相反）。
- **docstring 特徵數字 stale**：候選腳本 docstring 提「對 34 特徵增量」「base 33 特徵」是 2026-07-02 寫入時的常數；runtime canonical 現為 **29**（`CANONICAL_START` 交集 gate 於 07-11 才拍板）——看數字要以 SELECT/runtime 為準、不信 docstring 字面。
- **context/regime 類訊號橫斷面 IC 恆 0**：breadth、大盤 regime 每 panel 全股同值 → 橫斷面 rank IC 恆 0、無法用單因子橫斷面 IC 驗（`verify_matthew.py:9` 明述、故不含 P6 regime 軸）。
- **方向軸特徵是另一套 EAV、不在此 35 範圍**：`build_daily_direction_features` → `daily_direction_feature_values`、`build_market_direction_features` → `market_direction_feature`，寫獨立表（且方向軸家族已二次證偽判死，見記憶 augur-oracle-v2-plan）。

### 07-10（v3）之後的變化

v3 報告（2026-07-10）僅覆蓋 features 生產產生器 + 單支 `verify_candidate_promotion.py`；本節補齊「發現→提拔」研發流程層（13+ 支 scan/candidate 工具與方法論 SSOT）。commit **cd8b35e（2026-07-11 08:10，晚 v3 一天）** 三處洩漏修正實質改動本子系統：
- **`price_to_10yr` 的 #8 洩漏已修（v3 開放點閉環）**：分子從 `TaiwanStockPriceAdj`（前向還原＝把未來股利/分割因子回溯注入歷史價、偷看未來）改讀原始 `TaiwanStockPrice`（`valuation.py:35-39` `_RAW_CLOSE_SQL`），與分母 `TaiwanStock10Year` 同 raw point-in-time 口徑——v3 gotcha「price_to_10yr 基礎不一致（開放點）」不再是開放點。
- **`margin_cycle.py` 新增 #15 陳舊守衛 `MAX_STALE_DAYS=400`**（`:26`）：最新已公告毛利季離 panel > 400 日即缺列，排除保險/金融業 IFRS 後停報 GrossProfit（停於 2010）冒充當季——v3 版無此守衛。
- **`chip.py` `top_holders_pct`（f4）新增集保發布日 gate**（commit abf5da8，2026-07-11 11:07，審計 1A）：從 `date≤panel` 改傳 `holdings_visible_cutoff`（panel−7），因集保為週五快照且延後公布、`date≤panel` 會偷看未公開當週快照——v3 gotcha「chip 承認 T+1 gate 未做」就集保這塊已補。
- **`release_lag.py` 新增 `HOLDINGS_LAG_DAYS=7` + `holdings_visible_cutoff`**（abf5da8），docstring 新增財報產業別 lag 缺口揭露（現況休眠、唯一消費者已排除金融股故不觸發）。
- **`macro_vintage.py` 為 07-11 新建檔**（v3 未提）：`fred_series` 之唯一合法 PIT 消費門——Tier B `date≤panel AND realtime_start≤panel`（取當下現行版、拿不到未來修訂）、Tier A 因美時區 + T+1 發布用 `panel−1` 保守、未知 series fail-loud；定位「接線前先建好門」，`macro_vintage.py:13` docstring 誠實載明「尚無任何生產特徵消費總經」。
- **`rebuild_feature.py` registry 驅動單特徵重建器**（體現 #12「改 writer 碼 + 重建、不手 UPDATE 補值」）：`_REBUILDERS` 恰註冊本波修正的 3 個特徵（`price_to_10yr`/`gross_margin_pctile`/`top_holders_pct`），修正後算不出者誠實 DELETE 缺列。
- **`baseline.CANONICAL_START='2008-12-31'` 交集起點常數（2026-07-11 用戶拍板(a)）**：**須辨明——交集 gate 本身非 07-11 新增**（d797392 於 07-06 已用 `HAVING count(DISTINCT panel_date)=len(pds)` 交集，只是 pds=全 panel），07-11 僅**加上起點濾**，使 `gross_margin_pctile`（2007-12-31 全市場 0 檔有 ≥8 季 GP/Rev、結構性不可能存在）得以進入交集，base 由 28（全 36 panel 交集）→ **29**（≥2008-12-31 之 35 panel），改變每支提拔測試的 base 特徵集。
- **解凍後 live 增量**：`feature_values` 現含 panel 2026-06-30（超過 FREEZE 2026-05-31），對應解凍後 live 增量維運（as-of 滾動）、v3 報告時點尚在凍結期。
- **總經因子仍未接 per-stock 特徵層（未閉環）**：`macro.py` 宣告 31 檔 FRED series、`macro_vintage.py` 建 PIT 門，但 `feature_values` 內零 macro 特徵、`build_panel` 只 import 6 支 per-stock 模組——門建好但無生產消費者。

## §3.4 universe+models+execution+模型登錄：核心股PIT/薄殼ranker/artifact生命週期

**▶ 一句話**：這是預測管線 raw→feature→**universe→model→execution** 的後段脊椎——universe/core_gate 用「純完整度+真台股候選空間」選出乾淨可交易股集（不評分/不排名/不設上限）；models 是把 as-of 特徵矩陣 fit 成橫斷面相對強弱分數的最薄一層（fit/predict 契約+registry+artifact）；execution 疊一層唯讀 advisory 風控（DD 熔斷/cap/換手，閾值全住 DB、只出建議不下單）。三者共享 `model_registry`/`artifact`/`prediction_values` 一條 **train-once-serve-same-artifact** 的 provenance 脊椎（#15 可重現、#6 冪等、#12 離線≡上線零雙軌漂移）。**07-10 後這三個 package 的 code 零變動，所有 delta 純屬 DB live state 與 migrate CHECK 層。**

### 3.4.1 universe / core_gate（核心股完整度閘）

**做什麼**：core universe＝「值得被模型排序的乾淨可交易股集合」的選拔閘。輸出兩份名單：`core_universe`（pan-historical 單名單、含 look-ahead、供探索）與 `core_universe_asof`（逐 as-of 日 PIT 名單、消完整度 survivorship、供誠實 walk-forward）。**唯一判準是「資料完整（source-pure）+真台股個股空間」，不評分、不排名、不設 top-N 上限**（#10 質>量、可少不評分）。

**怎麼建的（機制為主）**：整個選拔是「一條資料驅動 SQL + 一個 PIT 迴圈」，零硬編零評分。四道閘全組進 `_select_core` 的**單一查詢**（`core_gate.py:162-171`）——真股碼 regex `_REAL_STOCK_PREDICATE`（`stock_id ~ '^[0-9]'`，`:165`）+ `NOT EXISTS TaiwanStockInfo ∈ ETF_INDUSTRY`（`:166-168`）+ 流動性 EXISTS（`:139-142`）放 WHERE 列級；universal 完整度 `HAVING count(*)=required`（`:170`）+ conditional 豁免子句放 HAVING 聚合後；結尾只有 `ORDER BY stock_id`（字母序、非分數序）、**無 score、無 LIMIT**（`claim1` CONFIRMED）。**完整度分母是關鍵設計**：`required` 不是 `len(panel)×len(feat)`，而是「市場上實際可算出的 `(panel,feature)` distinct 組合數」（`SELECT count(*) FROM (SELECT DISTINCT panel_date,feature …)`，`:120-123`）；某特徵在某 panel 全市場 0 覆蓋（結構性不存在，如 gov_bank 早於源表）就不計入 required，差額存 `absent_combos` 揭露（`:124-125`，#15 不靜默）避免誤殺核心或靜默 0-core。流動性閾值＝latest panel 的 `dollar_volume_log_20d` 之 `percentile_cont(pct)`（`:131-135`，動態相對分位、不寫死金額）。build provenance 帳本：每次 build append 一列 `core_universe_build_meta`（`:91-99`），記 scope/panel 範圍/liquidity_pct+算出 threshold/conditional/feat_list/core_count，解「dump 成品之 build 參數不可考」痛點。

**機械閘與不變式**：
- 完整度分母 `required`＝市場實際可算組合數（`:120-125`），core 股須 `HAVING count(*)=required`（`:170`，靠 PK `(panel_date,stock_id,feature)` 保 `count(*)≤required`）——SQL 聚合閘、非事後過濾。
- 候選空間＝真股碼 ∧ 非 ETF：`_REAL_STOCK_PREDICATE`（`:75`）排 roster 污染（產業名/指數名）+ `NOT EXISTS ETF_INDUSTRY`（`:72`，505 檔）——WHERE 列級硬閘。
- as-of PIT：`build_universe_asof` 每個 t 只用 `sub=pds[:i+1]`（≤t 面板，`:217-219`）算完整度、寫 `core_universe_asof`——#8 消完整度 look-ahead，只用 t 當時已知、不以「未來才知完整」回填歷史。canonical 特徵集固定取全期（與 M-1 可比），完整度逐 t 用子集判定。

**陷阱**：
- **完整度與流動性時點口徑不對稱**：完整度是 pan-historical（≤t 所有面板都要齊）、流動性只檢查 latest panel（`:130-142`）——core 股須「歷史一路完整」但「只需在 t 這天夠流動」。刻意設計、易誤解。
- **`canonical_features` 兩個同名相反實作**：`core_gate.py:102` 用寬 union（面板內全部 distinct 特徵）、`baseline.py:37-44` 用嚴 intersection（`HAVING count(DISTINCT panel_date)=len`）——命名撞、語意相反，讀 code 易混。
- **「core⊇baseline 特徵集」在豁免配置下無機制保證**：金融業 core 對 `monthly_revenue_yoy` 被豁免，而該特徵落在 baseline intersection 內，機制上不保證 core 齊 baseline 特徵集，當前僅經驗成立（prior art 親驗）。
- **PIT 名單序列非單調（v3 claim 更正）**：v3 稱「核心隨窗延長單調收縮 714→…→344」，實測 `SELECT as_of_date,count(*) FROM core_universe_asof GROUP BY 1` 顯示**整體下降但至少 5 次窗間上升**（2020-12→2021-03→2021-06=460→462→464；2021-12→2022-03=435→440；2023-12→2024-03=392→397；2025-12→2026-05=337→344）。純完整度 gate 在數學上**必**單調非增（窗 ≤t+1 之 required⊇required(t)），故「單調」與「只用完整度即單調收縮」之描述**錯誤**；打破單調的是部署 asof 建置另套的 **point-in-time 流動性 gate（build_meta liquidity_pct=25、於各窗最新 panel 之 P25 重算，股隨流動性穿越門檻進出）+ conditional gate**，非純完整度。端點值 714（2014-12-31）→344（2026-05-31）正確。
- **universe 零單元測試**：完整度閘/PIT 迴圈/required 計算皆無回歸鎖，只靠整合驗收腳本。

### 3.4.2 models（薄殼 ranker + registry + artifact）

**做什麼**：契約只有 `fit(X,y_rank)→self` / `predict(X)→ndarray`。三支各司一職：`ranker`（RankRidge 默認/RankGBDT 挑戰者）、`registry`（`model_registry` CRUD + PIT 載回 + resume）、`artifact`（joblib 序列化+凍結特徵集/as-of）。刻意不放 SHAP（留 audit，防膨脹侵入預測 SSOT）。

**怎麼建的**：核心是「複用鐵律（#12）+ 薄殼」。估計器組態**不是共享 code，而是把 `evaluation/baseline.py` 的 `B2_ridge`/`M1_gbdt` 超參字面複製**到 `ranker.py`——RankRidge=StandardScaler+Ridge(alpha=1.0)（`ranker.py:16-38`）、RankGBDT=LGBMRegressor 固定 7 超參（`:41-56`）——兩份是靠人工慣例同步的孿生字面複本，**無任何 assert/test 綁它們**（唯一機械綁定是一條 `np.allclose` 測試 `test_models_ranker.py:6-16`，且該測試手搭 StandardScaler+Ridge 為 ref、甚至未 import baseline、只在 baseline `robust=False` 分支成立）。`train_ranker` 全複用 baseline helper（`_fold_xy(asof=True)` 疊 (X,y)、`canonical_features`）。sklearn/lightgbm 採 fit 內 lazy import（package 輕、隔離乾淨，代價是相依錯誤延到 fit 才爆）。

**機械閘與不變式**：
- registry PIT 選模：`latest` 用 `WHERE family=%s AND horizon=%s AND asof_snapshot<=%s ORDER BY asof_snapshot DESC, created_at DESC LIMIT 1`（`registry.py:47-48`）——**絕不載 as-of 後訓練的模型**（walk-forward 命門）。
- register 冪等 upsert：`ON CONFLICT (model_id) DO UPDATE SET metrics/artifact_path/git_sha/created_at`（`registry.py:34-36`）供 resume。**親驗更正**：`git_sha` **非凍結**——每次 ON CONFLICT 用 `EXCLUDED.git_sha` 覆寫、`created_at=now()`；真正凍結的是 feats_hash/seed/family/horizon/train_span/asof_snapshot（不在 SET 清單）。
- feats_hash 順序無關：`sha256("\n".join(sorted(feats)))[:16]`（`artifact.py:18-20`），有 `test_feats_hash_order_invariant` 機械守。
- family 雙閘不對稱：DB `model_family_chk` 允 9 族（`migrate_prediction_ddl.py:37-45`）、但 `train_ranker.py:94` argparse choices 只允 RankRidge/RankGBDT——方向軸族靠別的 script 寫 registry。
- H=252 禁入：`train_ranker.py:99` `args.horizon==252` 即中止（結構洩漏 embargo=4）。
- 隔離不變式：models package 零 import knowledge/philosophy/advisor（`models/__init__.py:5`、audit.import_isolation AST 稽核強制）。

**陷阱**：
- **`predict_asof.py:122 cur_feats` 是死變數**：算出當下 canonical 後**再也沒被讀**。緊接的 `:123` 檢查是 `artifact.feats_hash(feats) != reg["feats_hash"]`，兩邊皆源自 artifact 自身＝**artifact↔registry 自檢（偵測損壞）**，非偵測「當下 canonical vs 凍結」漂移——三處 docstring 宣稱的「防漂移拒載」**未實作**。實效：canonical 新增特徵會**靜默用舊集出單**、漂移未被偵測。
- **RankRidge seed 是無效裝飾**：`RankRidge.__init__(self, alpha=1.0)`（`ranker.py:21`）無 seed 參數、`train_ranker.py:78` 對 RankRidge 呼叫 `est_cls()`（else 分支）不傳 seed；但 model_id/registry 仍記 seed=42（Ridge 解確定性、seed 純裝飾）。
- **RankRidge≡B2 只在 robust=False 成立**：baseline B2 是 `RobustScaler if robust else StandardScaler`、RankRidge 永遠 StandardScaler；robust=True 時離線估計器≠上線 RankRidge、無綁定不自動同步。

### 3.4.3 模型登錄／artifact 生命週期（train-once-serve-same-artifact 的 provenance 脊椎）

**做什麼**：這條脊椎回答「每一筆預測怎麼被凍結、版本化、as-of 解析、並在 serve 端零重算複用同一模型」。三個物件協作：`model_registry`（每個 fit 好模型的身分證：family/horizon/train_span/as-of/feats_hash/seed/metrics/artifact_path/git_sha）、`artifact.py`（把 estimator+凍結特徵集+as-of 打包成單一 joblib，離線訓練＝上線 serve 同一物件）、`prediction_values`（as-of 出單產物、靈魂產品輸出口）。train_ranker `fit→save→register`，predict_asof `latest→load→predict→寫產物`，兩端全複用 evaluation.baseline 同一 helper（#12）。

**怎麼建的**：
- **版本化靠把 feats_hash 編進 model_id 字串**：`train_ranker.py:70` `model_id=f"{family}_H{horizon}_{asof}_seed{seed}_{fh}"`。特徵集一變、fh 變、model_id 變→INSERT 新列而非覆寫舊模型（版本脊椎核心：模型不可變、換代即新身分）。實測 registry 同存 28 特徵 `ce62866` 與 29 特徵 `3a4e66fae` 兩代 RankRidge（共 9 列）。
- **artifact.save**（`artifact.py:23-33`）把 estimator+凍結 feats list+as-of+family/seed+feats_hash 一起 `joblib.dump` 成單一 .joblib；load（`:36-39`）純反序列化→serve 端拿回同一 estimator 物件、零重算（#6 冪等的 ML 具現）。檔名＝身分字串，人眼可辨版本。`MODELS_DIR=PROJECT_ROOT/models_artifacts`（`:15`，注意與 `config.MODELS_DIR`＝models 命名易混）。
- **PIT 部署解析＝隱式 recency**：live 指標＝`latest` 的「≤as-of 之最新登錄」（`registry.py:41-52`）；registry **無 active/is_current 旗標欄**（實測欄位僅 11 個、無部署狀態欄），故「誰是 live」是隱式 recency（`asof_snapshot DESC, created_at DESC`）而非顯式 promotion flag。
- **serve 端口徑保真來自 `feats=art["feats"]`**（`predict_asof.py:120`）直接驅動 `baseline._panel_matrix`（`:128`，只收全 feats 齊之股，`baseline.py:67`）——凍結特徵 list 隨 artifact 走、serve 用它建矩陣、不看當下 canonical；**feats_hash 只是 belt-and-suspenders，移除它也不改變 serve 用哪組特徵**。
- **provenance 記帳**：`git_sha()`（`registry.py:16`，記 HEAD sha）+ metrics.note 誠實 caveat（`train_ranker.py:33-40`，記 survivorship 債未閉環、H120 小樣本）。

**機械閘與不變式**：
- FK：`prediction_values.model_id REFERENCES model_registry(model_id)`（`migrate_prediction_ddl.py:49`）——每筆預測必綁一個已登錄的具體模型版本，孤兒預測寫不進去。
- family CHECK 白名單鎖 9 族（`migrate:37-45`），非白名單族 INSERT 被 DB 拒；DROP+ADD CONSTRAINT 冪等對齊擴充。
- model_id PK 唯一 + feats_hash 內嵌（命名協定、非 DB 約束）→ 特徵集換代產生新列、舊模型不可變共存。
- **無 DB 層 artifact 檔存在性約束**：`artifact_path` 僅 `text NOT NULL`，指向缺檔/方法論字串（方向軸族）DB 都收——存在性只在 runtime `artifact.load` 才驗（脆弱面）。

**陷阱（本機 provenance 斷裂——v3 未觸及的新層）**：
- **部署模型 5 個 joblib 全缺**：實際部署的 `3a4e66fae`（29 特徵）5 個 joblib 在 disk 全 MISSING（逐檔 `-f` 驗證），故 `predict_asof --run --horizon 20/40/60/82/120` 會在 `artifact.load`（`:119`，先於 `:123` feats_hash 檢查）拋 `FileNotFoundError`；單 horizon 路徑無 try/except 直接 traceback，只有 `--rewrite-all` 會逐 horizon 吞例外印「✗ H失敗」續跑（`:204-211`）。
- **disk 僅存 4 檔（`ce62866`、28 特徵）是舊 canonical**：`latest()`（asof/created DESC）從不選中、也非任何 live prediction 之源（於 07-11 14:11 被 29 特徵代取代），極易誤把它們當「解凍前凍結快照」。
- **`cur_feats` 口徑陷阱（若天真接線做漂移檢查會破壞所有預測）**：其口徑＝`canonical_features([asof])` **單 panel 交集＝35 特徵**，而 train 凍結的是**全史交集＝29 特徵**；35≠29→hash 恆不符→每次誤拒所有正確 artifact。防漂移正解須以「同 train 的全 ≤as-of panel 集合」重算 canonical，非單 panel。
- **recency 部署可被重登翻轉**：`register` 的 ON CONFLICT DO UPDATE bump `created_at=now()`（`registry.py:36`），重登任一舊 model_id 即可在 `created_at DESC` 平手中翻轉「誰是 live」，**無 active flag/A-B/rollback 指標可鎖定或審核**。
- **方向軸/市場族 artifact_path 存方法論字串**：MktLogit/DailyGBDT/DailyLogit/DirStackM 的 artifact_path＝`'walk_forward_refit_per_fold(…)'` 等字串（非真路徑、無單一 artifact），且 `predict_asof --family` 無 choices 限制（`:187`）。**更正**：此四族在 registry 皆 `horizon=0`，predict 預設 `--horizon 60`→`latest(…,60,…)` 回 None→graceful 退出**不崩**；須**同時 `--horizon 0`**（命中既有列）才會走到 `artifact.load`（方法論字串）→FileNotFoundError。故為需搭配 horizon 的潛在誤用面，非預設調用即無條件崩。
- **雙軌漂移根因**：`models_artifacts/` 被 `.gitignore:18` 排除、joblib 未入 git（`git ls-files` 空）+ DB 跨機獨立（走 pg_dump 搬運、不隨 git）→ joblib 永不隨 repo 遷移、僅 DB 列隨 dump 遷移→registry 有 `3a4e66fae` 列而本機無其檔。
- **但可重現性作為性質仍存活**：registry 列（DB 持久）+ RankRidge 確定性 + 凍結鍵（feats_hash/train_span/as-of）使 artifact 可經 retrain **位元重建**（今日 canonical 全史交集仍 hash 到 `3a4e66fae` 即證；29 減 28 之差＝新增 `gross_margin_pctile`）——joblib 實為「可重建快取」而非唯一真相源。

### 3.4.4 execution（部署後風控 overlay）

**做什麼**：在 long 投組上疊唯讀 advisory 風控三件事：DD 熔斷（權益回檔觸閾值→建議降倉）、單標的部位上限 cap（削頂並按比例重分配）、換手預算（超預算告警）。三類閾值全讀 DB `risk_policy` 表、**零 hardcode**（#29b）。**機械落地靈魂「系統建議、人決策；有紀律的顧問不是自動駕駛」**——只出降倉建議與旗標、不自動下單。

**怎麼建的**：「三層委派 + 唯讀 advisory + 資料驅動閾值」。零重造：DD 算法複用 `portfolio.drawdown_series`、換手率複用 `portfolio._turnover`、選股複用 `build_long_portfolio`（#12 單一住所）。程式碼**無硬編業務閾值**（執行碼唯一小數是 1e-12 收斂容差），閾值全走 `load_policies`（`risk_control.py:31-36`，唯一 SELECT、全檔零寫）。cap 用迭代收斂（每輪夾頂+按比例重分配，上界 `len(sids)+1` 保證停，`:87-100`），且刻意在 `N×cap<1` 退化投組回權重和 <1 而非硬塞回 1（硬塞會反推回集中、違 cap 本意 #15）。DD 熔斷/換手只出建議旗標，**唯 position_cap 機械改寫落庫權重**（可逆正規化）。

**機械閘與不變式**：
- 風控唯讀 advisory 不下單（全檔零 INSERT/UPDATE/DELETE）；`apply_overlay:142-146` controlled_port 僅含 cap 後權重，dd/turnover 回旗標 dict。
- `risk_policy.policy_key` DB CHECK ∈ {dd_circuit,max_position,turnover_budget}；load_policies 缺鍵 graceful（該風控不套、印告警，#15 不假裝有）。
- DD 熔斷 anti-leakage（#8）：`_deployed_dd_returns` 只納 forward 窗已關閉（`future[h]≤asof`）之已實現報酬（`predict_asof.py:69`）；熔斷用**當前**回檔 `dd[-1]` 非最深 max_dd（`risk_control.py:56-59`，已從深谷回升即使歷史 max_dd 深也不觸發、正確語意易誤讀）。
- 全 repo 只有兩支 output-stage 腳本 import `augur.execution`（`predict_asof.py:34`、`verify_risk_overlay.py:31`），無 feature/universe/model 反向依賴——execution 是純下游 overlay 的機械證據。

**陷阱**：
- **DD 熔斷 live dormant**：`_deployed_dd_returns` 需 forward 窗已關閉，現況 prediction_values 全庫僅 1 個 distinct panel_date（2026-05-31），每 model_id 恰 1 panel→任一 asof 之 `panel_date<asof` 查詢回空→rets=[]→「DD 熔斷未評估」；即使 risk_policy 已 seed 6 列也不觸發。
- **cap 退化投組合法回權重和 <1**：`N×cap<1`（如 5 檔×0.10=0.5）時全夾頂後和 <1、誠實不硬塞（`risk_control.py:96-98`）——**下游不可假設 controlled_port 權重和為 1**。
- **doctrine 機制落差**：靈魂/原則 #13 指定規則地板＝「vol-target × trend」，實作是 DD+cap+換手——是規則型防守但非 doctrine 明言機制，屬部分落地。
- **execution 零單元測試**：cap 收斂/DD/換手皆無單測，只靠整合驗收 `verify_risk_overlay.py`。

### 3.4.5 07-10（v3）之後的變化

**核心程式碼零變動**：`git diff --stat 76cce6c..HEAD` 對 `src/augur/universe/`、`src/augur/models/`、`src/augur/execution/`、`scripts/train_ranker.py` 全空——core_gate/ranker/registry/artifact/risk_control/train_ranker 自 v3 未改一行。所有 delta 純屬 DB live state + scripts（migrate CHECK）層。

- **risk_policy 表從 dormant→live**：v3 親驗 `to_regclass('risk_policy')=None`、風控 dormant；現已 seed 6 列（H60/H120 × dd_circuit/max_position/turnover_budget，source_ref=stageD verdict）。DDL/SEED 腳本 commit 00795f5（07-07，早於 v3），本機 DB 07-10 後才實跑 migrate。惟 **DD 熔斷仍 live dormant**（forward 窗未關→回 []）。
- **model_family_chk 從 2 族擴至 9 族**：現 CHECK 允 RankRidge/RankGBDT/MktLogit/DirStack/DailyLogit/DailyGBDT/DailyGBDT_cal/MktGBDT/DirStackM（`migrate_prediction_ddl.py:37-45`，commits 163caf0/2430b15 均 07-11、晚於 v3）——`model_registry`/`artifact`/`prediction_values` 共享 infra 已被 arena 方向軸子系統消費。
- **model_registry/prediction_values 從骨幹→已 live 落地**：model_registry 現 15 列（RankRidge H20/40/60/82/120 seed42 + 方向軸族），prediction_values 1695 列＝5 個 RankRidge model_id × 339 股 × horizon{20,40,60,82,120}（含罕見 H82，對應方向軸六門之一）。
- **07-11 14:11 canonical 特徵集 28→29**（+`gross_margin_pctile`、hash `ce62866`→`3a4e66fae`），產生新一代 RankRidge 並成為實際部署模型：5 個 horizon 各 1 panel×339 列全由 `3a4e66fae` 產生，`latest()` 對五 horizon 全解析到 `3a4e66fae`。**新增本機層 provenance 斷裂結論（v3 未含）**：這 5 個部署列的 joblib 在本機 disk 缺席（懸空指標），「serve 端載回同一物理 artifact 零重算」對部署模型不可滿足——但可重現性作為性質仍存活（見 3.4.3）。
- **core_universe/asof/build_meta 已落地生產快照**：core_universe=344、core_universe_asof=28 個 as_of × 共 12394 列（2014-12-31→2026-05-31）、build_meta 記 panel_count=28/feat_count=35/liquidity_pct=25/threshold=14.929/conditional=monthly_revenue_yoy 豁免金融保險|金融業/core_count=344——與 v3 config-scoped 數字一致。

## §3.5 evaluation：誠實驗證的數學 SSOT

**▶ 一句話**：所有「驗證數學」的唯一住所——每支 validator / harness / predict / audit 腳本都 import 這裡的 helper，讓 rank IC、purged 折切分、label 構造、Deflated Sharpe、投組經濟指標跨模型/跨 horizon **口徑一致才可比**（#12）；核心指標全 clean-room 手刻、零黑箱統計庫，每條公式 trace 回論文。它把靈魂的成功定義「經濟價值非 IC」機械化（`portfolio` 算 CAGR/Sharpe/MaxDD/Calmar、net=gross−換手成本），並對抗敵③自我欺騙：IC 序列用 HAC(Newey-West) 去相關 t 校正重疊窗高估、多重比較用 DSR 扣血、gross/net 雙報。

**做什麼（白話）**：模型吐出「每股 score/rank」，這層負責把它跟「實際 forward 報酬 label」比出可信度——**全是橫斷面相對強弱口徑、非絕對漲跌準確率**（`metrics.py:4`）。排序力（rank IC）撐住只是入場券，真正的裁決在 `portfolio` 層的經濟指標；兩者中間夾著 anti-leakage 的折切分（`walkforward`）與多重比較扣血（DSR）。樣本選哪些 panel（raw 全折 vs purged embargo 後折）由呼叫端決定，本層只算數學、不選樣本。

### 怎麼建的（機制與為什麼）

**五層職責硬切分、各做一件事**——`metrics` 只算指標不選樣本；`walkforward` 只產 train/test 索引切分、不碰資料不訓練不算 label（`walkforward.py:8`）；`label` 只造 label 不切分；`baseline`+`portfolio` 是組裝層（train→predict→組投組）；`deflation` 是「per-period 正確口徑」的共用住所。切分乾淨的好處是：raw vs purged 的口徑差異全推給呼叫端傳「哪些 panel 的 IC」，本層永遠只做一件確定性的事。

**clean-room 手刻、核心指標零外部統計庫依賴**——`metrics.py`（179 行）只用 numpy + `scipy.stats.norm`：Spearman rank IC 自刻（`_spearman:22` / `_ranks:37`，tie 取平均序位）、Newey-West HAC t 自刻（`effective_t_hac:89`，Bartlett 核 `LRV=γ0+2·Σ(1−l/(L+1))·γ_l`、經驗滯後 `lag=floor(4·(n/100)^(2/9))`，`metrics.py:103-107`）、DSR 兩式自刻（`expected_max_sharpe:122` 為 Bailey-LdP 2014 式(5)、`deflated_sharpe:140` 為式(9)）。檔內第 115-119 行直接附論文出處（Bailey & López de Prado 2014, JPM 40(5)）讓公式可 trace。手刻的理由是每條公式要能逐字對回論文、不受黑箱庫版本漂移污染（#12）。

**anti-leakage 寫進結構而非靠紀律**——兩道洩漏防線都是**執行期硬閘**：①`walkforward.py:48-49` `if h_days >= _H_FORBIDDEN(252): raise ValueError`，是 `train_ranker` CLI gate 外的第二道、擋「直呼 evaluation 旁路 CLI」（H≥252 經 purge 後獨立觀測太少、結構性洩漏）；②embargo 保證下界＝`h_days + 62` 交易日（label 窗＋特徵最大滯後 `_FEATURE_LAG_TD=62`，`walkforward.py:17,51`），有真實日曆時 `walkforward.py:53-64` 逐折用 `bisect` 在交易日索引上回推——每折自 train 尾往回加 panel、直到「train 尾 panel 距 test 之**實際交易日** ≥ 目標」才收（`guaranteed=True`），這是唯一非估算路；無日曆時退回 `embargo_panels_for` 單一估算並誠實標 `guaranteed=False`（`walkforward.py:65-70`、`:22` docstring 明寫「非保證、僅開發近似」）。

**label t+1 進場口徑**——`entry=calendar[0]`（panel 之後的次一交易日）、`exit=calendar[h]`（`label.py:48`）；forward return 用還原價 `TaiwanStockPriceAdj` 的 log return；`close≤0`（停牌哨兵）或缺進/出場價的股票**該股缺列、不外推**（`label.py:80-84`、#1），日曆不足回 `(None,None)`。這確保「今天的 panel 只用得到明天以後的價格」，時點欄不洩漏。

**#12 單一住所靠委派落地、backtest≡live 零漂移**——`build_long_portfolio`（`portfolio.py:58`）是 `run_backtest`（離線）與 `predict_asof`（線上出單）共用的**唯一選股邏輯**；`drawdown_series`（`portfolio.py:21`）是唯一 DD 算法、被 `execution.risk_control` 複用；`deflation.deflated_floor`（`deflation.py:44`）是唯一 per-period DSR 口徑、被 4 支 script 複用。誠實補一句：這些綁定是**人工委派慣例、無 assert 機械綁死**——選對函式靠命名與 review，不是靠型別鎖。

**一個貫穿的效能決策**——`label.full_calendar(conn)` 開頭一次性取全市場交易日曆、逐折傳入 `forward_returns` 做記憶體 filter，取代對 11M 列 `TaiwanStockPriceAdj` 的逐 panel N² 全表掃描（`baseline.py`/`portfolio.py:95` 皆先取 `cal` 再逐折餵）。

**cross_section 交互特徵刻意不入 `feature_values`**——`inter_fh_x_p10yr`（`cross_section.py:22` 註冊表目前唯一一個）是**宇宙相依量**（z 用當前 panel 橫斷面 mean/std），故由 eval 層 `augment()`（`cross_section.py:32`）在組好矩陣後尾端動態 append、**opt-in、限 374 核心宇宙**——換寬宇宙 ΔIC 轉負（−0.0005）故不設生產預設。誤用到擴展宇宙會製造假增量，口徑須與 `verify_interaction_promotion` 同源。

### 機械閘與不變式（enforced_where）

- **H≥252 禁入 walk-forward**（結構性洩漏硬閘）：`walkforward.py:48-49` 執行期 `raise ValueError`（非 assert），在 walkforward 層強制、擋 CLI gate 旁路。
- **embargo 保證下界＝h+62 交易日**：`walkforward.py:57-63` 逐折 `bisect` 真實交易日回推（`guaranteed=True`）；`tests/test_evaluation_core.py:85-101` 以 in-memory panel 斷言 test∉train、train 全早於 test、embargo gap 恰=emb、逐折嚴格 expanding。
- **`canonical_features` 只對 panel≥`CANONICAL_START` 取「每 panel 都出現」之交集、且只 `SELECT FROM feature_values`**（`baseline.py:41-45`）；SQL 實證交集＝29 特徵。
- **候選污染機械隔離（非紀律）**：`_panel_matrix` 只在 `feats` 明點名時才 `to_regclass` 檢查併讀 `feature_candidate_values`（`baseline.py:55-59`），而 `canonical_features` 從不讀該表 → 核心特徵集不受候選污染，在 evaluation/audit 邊界強制。
- **label t+1 + 還原價 + 缺列**：`entry=calendar[0]/exit=calendar[h]`（`label.py:48`）、`close≤0` 或缺價 continue（`label.py:80-84`）；test 斷言非交易日 panel 進場不漂移為 t+2。
- **drawdown_series 單一住所**：`portfolio.py:21` 被 `execution.risk_control:51` 複用，DD 算法零重造（#12）；`build_long_portfolio` 3 個直接 caller（`run_backtest` `portfolio.py:132` / `predict_asof.py:134` / `survivorship_economic_verdict.py:156`），選股層零雙軌。
- **DSR per-period 口徑靠 `deflation.deflated_floor` 包裝強制**：`deflation.py:57` 恆餵 `sr_pp`（per-period）——但 `metrics.deflated_sharpe` 本身**口徑無關**，餵年化 SR 會靜默算出灌水 DSR，無機械閘攔直呼（見陷阱）。
- **HAC t 為顯著性唯一標準靠慣例**：`run_ladder`（`baseline.py:158`）與 `feature_diagnostics` 一律尾端併陳 `effective_t_hac`；但 `metrics.summarize:83` 仍回 iid `effective_t`、無機械閘禁裸用（#11/G8 屬**紀律面**防線）。

### 陷阱（gotchas，本輪逐一 CONFIRMED）

- **`run_backtest` 預設 `cost=0.0`（`portfolio.py:81`）**：caller 忘傳 cost 則 `net==gross`（`portfolio.py:143` `net=g−turn*cost−sb`，全預設下逐項等於 gross），#14「扣成本」失效。`COST_TW=0.00585`（台股來回≈0.585%）**不是 evaluation 模組常數**，散落在 >10 支 script 各自定義（`verify_stability.py:25` / `revalidate_baseline.py:31` / `verify_economic_reexam.py:24` / `deflate_cost_sensitivity.py:37`…），無單一 SSOT、改成本值須逐檔改。
- **`metrics.deflated_sharpe` 口徑無關、餵年化 SR 靜默灌水**：`metrics.py:167` `z=(sr_obs−sr0)·√(t−1)/√denom` 不檢查單位，餵年化 `sr_ann` 配 per-period `T` 使 z 灌水 `√ppy` 倍。唯一防線是 `deflation.deflated_floor` 包裝＋docstring「禁平行重寫」命名慣例；`deflation.py:6` 自陳「DSR 高估~14pp」**（此~14pp 為 docstring 自陳、本輪唯讀未獨立複現）**，其活體對照住 `scripts/deflate_headline_verdict.py:120` 刻意保留的 `bug=M.deflated_sharpe(sr_ann,...)`、`:126` 印「buggy 年化版 DSR ← 作廢、勿引」——證明錯口徑呼叫可正常執行、防線純慣例。
- **`run_backtest(asof=False)` 是 latent dead code（TypeError）**：`portfolio.py:101` `stocks=None` → `baseline._panel_matrix:49` `fset=set(None)` → `TypeError`；grep 全庫 `run_backtest` caller 無一傳 `asof=False`（預設 True），故此路從未走到。
- **long-short 短腿永遠等權**：`portfolio.py:137` `simple[order[-nt:]].mean()` 算術平均，即使 `weight='pred'` 長腿 rank 加權（`:134` `Σ(w·ret)`），短腿仍等權（非對稱設計、非 bug 但易誤解）。
- **`metrics.summarize` 仍回 iid `effective_t`（`:83`）**而 #11/G8 明令禁裸用——防線僅靠 `run_ladder`/`feature_diagnostics` 併陳 HAC 之慣例，有心人可直接讀 `summarize['effective_t']` 繞過。
- **常數未對齊的 stale-advertise 張力**：`label.HORIZONS=(5,20,60,252)`（`label.py:22`）仍列 252，但 `walkforward.splits` 對 h≥252 raise——以 `HORIZONS[3]` 餵 `splits()` 會炸；另 `baseline.py:12` docstring 稱「seeds 參數預留」但 `run_ladder` 簽名只有 `seed=42`（多 seed 統計實由呼叫端跑），亦屬 stale 描述。
- **HAC「必嚴格小於 iid」是實證非通用證明**：`tests/test_evaluation_core.py:25-34` 於 φ=0.6 AR(1) 斷言 `hac_t < iid_t`、`:37-43` 白噪音 assert 近等（rel=0.15）；但 iid `effective_t` 用 `std(ddof=1)`、HAC γ0 用 `e@e/n`（ddof=0）口徑本就不同，對趨近 0 之極小正 φ 理論上可反轉——於有意義正自相關成立且有測，但非普適定理。
- **`test_evaluation_core.py` 僅涵蓋 3/7 模組**（`effective_t_hac`、`_entry_exit`、`splits`，`:14` 只 import label/metrics/walkforward）；DSR（`expected_max_sharpe`/`deflated_sharpe`）、portfolio 經濟指標、baseline canonical gate、`cross_section.augment` 全無單測——覆蓋缺口。

### 07-10（v3）之後的變化

**唯一 code 改動＝`baseline.py` 新增 `CANONICAL_START='2008-12-31'`**（commit `d973b81`、2026-07-11 hugo 親簽、屬 V0-V2 驗證總綱落地）。`git log --since=2026-07-10 -- src/augur/evaluation/` 只回此一 commit，其餘 6 檔（metrics/portfolio/label/walkforward/deflation/cross_section）逐檔 last-commit 全早於 07-10（metrics 07-07、portfolio 07-08、label 07-04、walkforward 07-06、deflation 07-08、cross_section 06-29）；改動 15 行、全在 baseline.py（常數定義 `:30-34` ＋ `canonical_features` 加 filter `pds=[p for p in panel_dates if str(p)>=CANONICAL_START]` `:41` ＋ docstring）。

**效果 SQL 實證**：`canonical_features` 從「對全 panel 取交集」（含 2007-12-31 → 28 特徵）改為「先濾 panel≥2008-12-31 再取交集」→ **29 特徵**（兩者 `EXCEPT` 唯一差＝`gross_margin_pctile`）。理據是資料事實——`gross_margin_pctile` 於 2007-12-31 結構性不可能存在（全市場 0 檔有 ≥8 季 GP/Rev 成對、該 panel `count(*)=0`），其最早可存在 panel 恰＝2008-12-31；gate 要求排除「數學上不可能的特徵」，起點＝特徵可存在之最早 panel 而非任意值。對應 commit 訊息「29 特徵 hash `3a4e66fa`」（V0-V2 驗證總綱 `d973b81` 親簽定案）。

**v3 §3.5 未列舉、v4 補記（非 07-10 後新增、但 v3 漏點）**：`run_backtest` 現支援三模型——`B2_ridge`（`portfolio.py:116`）、`M1_gbdt`（`:127` LightGBM）、`ENS_ridge_gbdt`（`:119`，Ridge+GBDT 等權 rank-average、零調權抗 regime）；long_short 短腿另計年化借券成本 `sb=short_borrow·h/252`（`portfolio.py:141`）。這兩者 v3 時（fe8b4cb 07-08、e67211e 07-07）已存在，非 07-10 後新增。

**本輪新發現（v3 未點）**：`scripts/deflate_headline_verdict.py:120` 內建 `bug=` 年化版 DSR 側錄，把 `deflation.py` docstring 的「高估~14pp」從純 lore 升為 in-code 可複現對照（本輪唯讀未跑），且證明 `metrics.deflated_sharpe` 錯口徑呼叫可正常執行、防線純慣例——這是 v3 未列舉的活體反例。

## §3.6 audit：隔離命門 + DB↔API 對帳 + 衍生研究寫入者

### ▶ 這層在做什麼（白話）

`src/augur/audit/` 是預測管線的橫切支柱，把三條 doctrine 鐵則從口號變成「可自動跑的架構不變式」：(1) **隔離命門** `import_isolation`——「素養層（哲學/知識/顧問）零量化價值、絕不進預測管線」（#8／憲章 philosophy 邊界 v1.17.0/v1.19.0）靠 AST 靜態稽核 + 字面掃描機械強制，配 `setup_predict_role.py` 的 DB GRANT/REVOKE 成雙閘；(2) **DB↔API 對帳** `reconcile`——「#7 證明 DB 無 AI 幻像」靠逐列重抓 API 真值、正規化後值相等比對、fail-closed attestation；(3) **衍生研究**——`feature_diagnostics` 訓練前五鏡合判特徵去留（#11）、`feature_candidate` 把浮現候選做成 as-of 安全特徵寫獨立 staging、`field_correlation` 探索 raw 欄位相關與 lead-lag。**注意 v3「全層唯讀」是過度概括**：唯讀僅指 `reconcile` 的對帳路徑，同層的 `field_correlation` 與 `feature_candidate` 是**專職 writer**（見「audit 層的真實寫入邊界」）。

### 隔離命門：八道靜態掃描 + DB 動態閘（雙閘）

`import_isolation.check_isolation()`（`import_isolation.py:167-178`）是唯一總入口，回違規清單、空 `list`＝通過。它用**純檔案系統 + AST，絕不 import 被檢查的 code**（`:79 ast.parse(py.read_text)`、`:82 ast.walk`、`:90` 比對 FORBIDDEN 前綴，全程 read_text 零 import）。**串接的是八道掃描（v3 記「七道」為誤，實為八道）**（`:169-178`）：

1. `_import_violations`（`:170`）——7 個預測 package（`PIPELINE=features/models/universe/evaluation/ingestion/audit/catalog`，`:31`）rglob `*.py`、AST-walk 任一 import 命中 `FORBIDDEN=(augur.philosophy/advisor/knowledge)`（`:33`）即違規。
2-6. **五道字面旁路掃描** `_string_ref_violations`（`:95-108`，純 substring，擋「字串拼 SQL 繞過 import」，因 AST 看不到執行期組的 raw SQL）：`rbac`（`:171`）、`chat`（`:172`）、`distill`（`:173`，界線-A 蒸餾 staging）、`deliberation`（`:174`，審議引擎工作帳）、`bridge`（`:175`，K 計畫 R5 語意橋表）。
7. `_placement_violations`（`:176`）——resolver 必住 `augur.knowledge/access.py`、chat_history 必住 `augur.advisor`，`core` 不得含 `resolve_allowed_domains`/`append_message`（否則 pipeline 經 core 可達，`:111-133`）。
8. `_scripts_predict_leak_violations`（`:177`）——`scripts/` 中 import 預測 package 者禁字面觸及 RBAC/chat 表（`:136-164`）。

稽核器自身合法持有偵測常數（RBAC/chat/distill 字串），故字面掃描用 `_SELF`（`:59`）排除本檔避免自我誤報（`:102`）。掃描範圍分兩檔：`SCAN_STR=PIPELINE+("core",)`（rbac/chat/bridge，`:50`）、`SCAN_DISTILL=PIPELINE+("core","knowledge","philosophy")`（distill/deliberation，`:52`，界線-A 連素養層寫入者一併禁觸及、防蒸餾產物回流真兆庫）。

**縱深防禦雙閘**：靜態閘擋 compile-time；DB 動態閘（`setup_predict_role.py`）擋 runtime 動態 SQL 旁路——建受限 role `augur_predict`，`classify()`（`:45-56`）依 `FORBIDDEN_PREFIXES=(philosophy_/knowledge_/advisor_distill_)`（`:32`）+ `FORBIDDEN_EXPLICIT`（`:33-37`，chat/RBAC/映射表）分流，`apply()` 對素養層 REVOKE ALL（`:99-100`）、對預測表 GRANT SELECT（`:103`）、`WRITABLE` 加 INSERT/UPDATE（`:104-105`）、`ALTER DEFAULT PRIVILEGES REVOKE`（`:107`）讓未來素養表自動關。本機 live 實測 role 已存在（`role_exists=true`），素養層 `philosophy_work/knowledge_item/chat_message/app_user/advisor_distill_context` 對 `augur_predict` `SELECT` 皆 `false`（DB 查詢），FORBIDDEN 實際覆蓋 **78 表**（DB 查詢，v3 記 62、隨表增長）。

### DB↔API 對帳：純 kernel + 四類非對稱處置

心臟是無 I/O 純函式 `compare(db_rows, api_rows, pk, valcols)`（`reconcile.py:61-82`）→ 四類計數 `matched/value_mismatch/missing_in_db/extra_in_db` + 範例。比對地基 `_norm`（`:37-52`）是血淚 bugfix 累積：**bool 須在 float 前判**（`:41-42`，否則 `float(True)=1.0` 把 DB varchar `'true'` 誤轉數值 → PK 永不匹配 → 100% 假 EX≡MIS，Dealer is_after_hour 2026-06-24）；**前導零識別碼保留 str**（`:47-48`，否則 `float('009802')=9802.0` 與 `'9802'` 碰撞，DayTrading 2026-06-24）；數值 PK Decimal↔raw str 正規化為同值（`_key:55-58`，GovBank 2026-06-11）。

外層各 `reconcile_*` 刻意**對齊寫入端點重抓**消端點差假 VM：per-stock 表逐股用 per-stock 端點（`reconcile_per_stock:204-217`，2026-06-17 三大法人假 VM=73 教訓）、by-dim-id 表逐維度 id 累積（`reconcile_by_dim_id:270-276`，2026-06-18 by-date 回空假 MIS）。四類差異**非對稱處置**：VM/MIS（可補的覆蓋缺口）→ `fixable_dates`（`:171-178`）→ `heal_by_date`（`:186-201`）對 fixable 日期回灌 `sync.sync_by_date`（`:196`）的 upsert 路徑（**非 hand-patch，守 #12**）；EX（DB 有 API 無＝幻像/塌列/PK 碰撞紅旗）→ `flagged_dates`（`:181-183`）→ **絕不自動補也不自動刪、須人查根因**（誤刪 = 可能刪掉合法已下市歷史真值）。頂層 `verdict()`（`:404-413`）三-clause fail-closed：`passed = value_mismatch==0 ∧ extra_in_db==0 ∧ not incomplete`（`:413`），任一表 `errors`/`incomplete` 即不 pass（`:408`，「沒比到 ≠ 比過且乾淨」）。

### audit 層的真實寫入邊界（更正 v3「全層唯讀」）

「全 audit 層唯讀、唯一寫入例外是 heal_by_date」**經對抗判決 REFUTED**。正確版分兩軌：

- **對帳/attestation 軌唯讀**：`reconcile.compare/verdict/*` 皆唯讀，`heal_by_date` 是其**唯一寫入**（且走 `sync_by_date` upsert 非 hand-patch），EX 紅旗不自動補刪——此部分成立。
- **衍生研究軌是專職 writer**：`field_correlation.py` 對自建 `field_correlation`（`analyze_stock:144` → `execute_values INSERT … ON CONFLICT`，`:155-158`）與 `field_return_leadlag`（`analyze_stock_leadlag:203` → `:214-217`）行 INSERT/UPDATE + DDL（`cur.execute(DDL):86`、`DDL_LEADLAG:213`）；`feature_candidate.py` 對 `feature_candidate_values` 行 INSERT（`compute_candidates` → `:113-115`）、DELETE（`clear_candidates:122-127`）、DDL（`ensure_candidate_table:36-39`）。各模組 docstring 的「audit 唯讀」僅指**不改 raw/生產/被對帳資料**，不等於零寫入（`field_correlation.py:10-11` 自陳「不改 raw、不選股、不入模」）。

`feature_candidate` 靠**機制性（非紀律性）隔離**防污染核心特徵集：`canonical_features()`（`baseline.py:37-45`）只 `SELECT feature FROM feature_values` 算交集、**結構上永不返回候選欄名**；`_panel_matrix`（`:48-59`）先 `to_regclass` 判候選表存在、**僅對 `feats` 明點名的候選欄併讀**（`:55-59`）——生產路徑 `feats=canonical`（不含候選專名）→ 機械上碰不到候選污染。

### 五鏡合判 five_mirror

`feature_diagnostics.five_mirror`（`:98-131`）合判五鏡——① 單因子有號 IC（`single_factor_ic:26`，附 **HAC Eff-t 不裸用 iid t**，#11 重疊窗高估）、② 共線矩陣（`collinearity:48`）、③ leave-one-out ablation（`leave_one_out:66`）、④ TreeSHAP（`shap_importance:82`）、⑤ 增量/穩健（併於 ①③）。合判規則刻意設計成**無單一指標可判生死**：`'drop?'` 需 `weak_shap ∧ weak_ic ∧ ablation_safe` 三條件同時成立（`:125`）；即使 `loo=False` 時 `ablation_safe` 恆 True（`:124`），`drop?` 仍需兩指標同弱。全部 reuse evaluation helper（`label/metrics/baseline`，守 #12 口徑一致）。

### 機械閘與不變式

- **預測 7 package 零 import 素養層**：`_import_violations`（`:70-92`）AST 強制、`check_isolation()` 現行 code 必回 `[]`，由 `test_philosophy_isolation.py` 薄殼委派 + 各子測分別釘 import/rbac/chat/distill/deliberation/bridge/對位/scripts，**含紅測**（`:114-120`：植入 `SELECT stat_value FROM field_knowhow_lexical_affinity` 暫存檔、反斷言掃描器必抓到）——證閘非假閘。
- **預測 role 對素養層 SELECT 一律拒**：`setup_predict_role.apply` REVOKE ALL 強制、`test_predict_role_isolation.py` 斷任一 forbidden 表 `SELECT=true` 即 FAIL 且須覆蓋 ≥3 表；live 實測素養層 5 表全 `false`（DB 查詢）。
- **attestation fail-closed**：`verdict.passed = VM==0 ∧ EX==0 ∧ not incomplete`（`reconcile.py:413`；`test_reconcile.py` 覆蓋 incomplete/errors→不 pass）。
- **`_norm` 三血淚不變式**：bool→字串、前導零→保留 str、Decimal↔raw str→同值（`reconcile.py:41-48`，違之則 100% 假 EX≡MIS/假 VM）。
- **候選機制性隔離**：`canonical_features` 只讀 `feature_values`、`_panel_matrix` 僅於 feats 明點名時併讀候選（`baseline.py:37-59`）——生產模型路徑機械上碰不到候選。
- **對位釘死**：resolver 必住 `augur.knowledge`、chat_history 必住 `augur.advisor`（FORBIDDEN 前綴、預測零 import），`_placement_violations` + test 雙重釘（`import_isolation.py:111-133`）。

### 陷阱

- **對帳模式必須對齊寫入端點重抓**（反直覺）：per-stock 表誤用 by-date 端點、by-dim-id 表誤用 by-date、intraday-source 未套日聚合 → 全會產生假 VM/假 MIS；殘餘 VM 才是真差異（`reconcile.py:204-217/270-276`）。
- **EX 是最嚴重訊號但 heal 絕不自動碰**：EX 可能塌列/AI 幻像/PK 碰撞，只回報須人查；誤把 EX 自動刪 = 可能刪掉合法已下市歷史真值（違 #12/#15）。
- **`heal_by_date` 的 `passed` 只有 2-clause**（`reconcile.py:201`：`VM==0 ∧ EX==0`），缺 `not incomplete`，與正典 `verdict()` 三-clause 不一致——heal 後若 after 仍有抓取失敗，heal 仍可能回 `passed=True`（違 #15 精神）。
- **`_scripts_predict_leak_violations` 偵測面不對稱**（`import_isolation.py:161`）：只掃 `RBAC_LITERALS + CHAT_LITERALS`，**未掃 DISTILL/DELIB/BRIDGE**——import 預測 package 的腳本若字面觸及 `advisor_distill_*`/`deliberation_*`/`field_term_map` 不會被此面抓到（其餘七面仍掃 pipeline+core）。
- **候選表為空（0 列）證機制在運作、但因果不可反推**：`feature_candidate_values` 現 0 列（DB 查詢），證生產路徑現況無候選污染；但「空 = 五鏡曾裁掉候選」**無法由 count=0 確立**（可能從未填充、或經 `clear_candidates` 清）。`CANDIDATES` 為硬編 4 個實驗候選（`feature_candidate.py:30`）。
- **`field_correlation`/`field_return_leadlag` 非生產特徵**：`field_correlation.py:10-11` docstring 自陳探索性、非 as-of、若日後用於特徵須另過 #8/#11；已落地 656,570 列/374 股與 135,124 列（DB 查詢）。（微註：`field_return_leadlag` 自身 docstring 宣稱 predictor≤t/報酬 t+1 的 anti-leakage 建構，故「非 as-of」對 leadlag 略寬，但「非生產、須另過漏斗」對兩表皆成立。）

### 07-10（v3）之後的變化

- **`augur_predict` role 已 APPLIED（v3＝provisioned-but-unbuilt）**：v3 報告與 `setup_predict_role.py:82` 自陳「role 尚未建、暫緩實建」，今 live `pg_roles` 已有此 role 且 GRANT/REVOKE 生效（DB 查詢 `role_exists=true`、素養層 5 表 SELECT 皆 `false`）。**然 runtime 仍未接線**：`db.connect()` 用單一 `config.DB_PARAMS`（owner role，`db.py:29`），`config.py` 查無 `DB_PARAMS_PREDICT` 變數（僅 `setup_predict_role.py:19/127` docstring 提及為「下一步」），`predict_asof.py:112` 走 `db.connect()`——**DB 閘 role 真實存在但預測進程尚未以此 role 連線、閘未被實際行使**。
- **靜態閘兩次擴充界線-A**：07-10 後 `import_isolation.py` 新增 `DELIB_LITERALS`（`deliberation_*` 審議引擎工作帳，commit e2f257a，`:44-45`）與 `BRIDGE_LITERALS`（`field_term_map/field_knowhow_lexical_affinity/knowledge_item_term_stats`，K 計畫 R5 語意橋表「每欄一係數」＝最貼近特徵表旁路面，commit 80dd1f3，`:48`），對應 `check_isolation()` 的 deliberation/bridge 兩道掃描（`:174-175`）。
- **【新發現・雙閘背向】DB 動態閘出現覆蓋缺口（divergence）**：`setup_predict_role.py` 的 `FORBIDDEN_PREFIXES/EXPLICIT`（`:32-37`）**未同步上述兩擴充**，這些表在 `classify()` 落入 allowed 分支（`:52-55`）→ 被 `apply()` GRANT SELECT（`:103`）。live 實測 `augur_predict` 可 `SELECT` `deliberation_claim/session/verdict`、`field_term_map`、`field_knowhow_lexical_affinity`（皆 `true`，DB 查詢）；僅 `knowledge_item_term_stats` 因 `knowledge_` 前綴被擋（`false`）。故 **deliberation 全表 + 2/3 bridge 表的「雙閘」實為單閘（只有靜態）、DB 動態旁路防禦缺席**——非現行主動洩漏（靜態閘已擋 pipeline code 觸及），但 v3 稱頌的縱深對稱已被新增項侵蝕。
- **紅測強化**：`test_philosophy_isolation.py:108-120` 新增 bridge-table 紅測（fail-closed 反斷言），對植入 `field_knowhow_lexical_affinity` 字面的暫存檔斷言掃描器必抓到。
- **分析表落地現況（DB 查詢）**：`field_correlation` 656,570 列/374 股、`field_return_leadlag` 135,124 列（均已 populate）；`feature_candidate_values` 0 列（候選已清、未提拔）。

## §3.7 預測驗證 harness+出單 SOP:證據帳本/unfreeze GATE/deflation/as-of 出單

**這層在做什麼(白話)**：這層一半是「靈魂產品的實際輸出口」、一半是「憑什麼相信這條輸出鏈」的自我審計。出單 SOP（`predict_asof`）對某 as-of 日把橫斷面相對強弱 rank 變成 top-decile long 投組建議、再校準成「勝過同儕中位數」的相對機率、由唯讀 UI 誠實呈現——只建議、不下單、不動錢（靈魂：有紀律的顧問不是自動駕駛）。驗證 harness 則回答「edge 已誠實判 thin/dead，那每一環到底驗了什麼」：把散落於報告/commit 的斷言變成可機械重驗的 DB 帳本（`validation_evidence`）、把「將來接新資料怎樣才算過」的判準先凍結入 DB（`prediction_unfreeze_gate`）、並用 Deflated Sharpe / survivorship 拆解 / R 軌把 headline 淨 Sharpe~1.2 這種薄 edge 誠實坐實而非藏。全部本地零 usage（#28）。

### 3.7.1 出單 SOP：as-of → top-decile 投組（靈魂輸出口）

`predict_asof.predict`（`scripts/predict_asof.py:104-158`）是 SOP 的核心，鏈為：as-of 日 → `registry.latest` 載「≤as-of 之最新同 family/horizon」artifact（`:116`；`registry.py:47` 以 `asof_snapshot<=asof ORDER BY DESC` 坐實 PIT≤as-of）→ 取當日 `core_universe_asof` 名單經 `baseline._panel_matrix` 組特徵矩陣（`:128`）→ `estimator.predict` 出每股分數 → 分數降序 rank（`:132`）→ `portfolio.build_long_portfolio(top_frac=0.1)` 建 top-decile 等權 long 投組（`:134`）→ 先 `DELETE` 同 `(panel_date,model_id)` 再 `executemany INSERT` 寫 `prediction_values`（`:146-151`，冪等）。live DB 現況：五 horizon 各 339 股、每 horizon 33 檔 `in_portfolio`（=`int(339×0.1)`）、全 `panel_date=2026-05-31`、全 RankRidge，共 1,695 列。

**為什麼這樣建**：出單（live）與離線回測（`run_backtest`）**共用同一支** `portfolio.build_long_portfolio`（`portfolio.py:58`，兩端皆呼叫）做選股與加權——刻意避免「驗證用一套選股邏輯、上線用另一套」的漂移型自欺（#12 命門）。收尾可選 `--risk-control` 套 `execution.risk_control` overlay（`:136-141`）：單標的 cap 是唯一機械改寫落庫權重者、DD 熔斷/換手只出建議旗標不下單，閾值全讀 `risk_policy` 表（#29b）。DD 熔斷的 anti-leakage 由 `_deployed_dd_returns` 保證只納 forward 窗已關閉（`future[h]<=asof`、報酬全實現）之過去 panel（`predict_asof.py:66-70`，#8）。

### 3.7.2 相對機率誠實輸出口：三表校準 + 誠實 UI

薄 edge 要誠實坐實而非讓數字好看，機率鏈是三表管線：`build_probability_oos_sample`（walk-forward 逐折 refit 同族 Ridge，把〔分位, 已實現相對標籤, exit_date〕落 `probability_oos_sample`，校準器唯一合法 fit 對樣本）→ `calibrate --fit`（expanding-purge 逐折評估 Brier/ECE + 對全 FREEZE 樣本做 **Platt**（2 參 logistic，折內 n 小故不用 isotonic 免過擬合）→ `probability_calibrator`）→ `calibrate --emit`（套校準器於 `prediction_values` 分位 → `prediction_probability`）。把「橫斷面分位」校成「P(勝過同儕中位數|as-of,H)」。方向契約統一：fit 側 `cross_sectional_rank` 與 emit 側 `pctl=1-(rk-1)/(n-1)` 同為 [0,1]、1=最強，`build_probability_oos_sample.py:148-159` 逐折抽驗 top-1 分位==top-1 分數（`by_pctl<>by_score` 計數須為 0）。

**誠實化雙軌**：(a) `deflate_headline_verdict` 用 Deflated Sharpe 把 headline 淨 Sharpe 釘成真兆地板（見 §3.7.5）；(b) `econ_verdict`（dead/thin_unestablished/established）讀自 `econ_verdict_rule` DB 表、與每筆機率同列硬綁不可分離（`calibrate_relative_probability.py:147-158`，缺列 fail-loud）。emit 後機率誠實地擠在窄帶：live DB 全局 `p_beat_median∈[0.3825,0.6165]`≈[0.38,0.62]、H60 `brier≈0.2475` 僅微幅勝 base-rate 基線 0.25、全 horizon `purge_verified=t`；econ_verdict 現況 H20=dead、其餘=thin_unestablished。

`serve_probability_ui`（`scripts/serve_probability_ui.py`）是 100% 伺服端確定性渲染（零 LLM）的唯讀誠實殼：route 僅 GET 讀 + POST /login、綁 127.0.0.1、fail-closed；四誠實標記（橫斷面口徑+as-of+逐折 n／日曆日↔交易日偏差／econ_verdict／family_note 同族近似）逐值硬綁同一 DOM 節點（單獨截圖仍自帶）；四 horizon 呈四張獨立模型卡（不連成機率曲線、免讀出未主張的期限結構）；`_check()` 機械斷言「上漲機率」等禁語不出現（`:387-389`）。另掛 /simulate（MC 模擬情境、四鎖）與 /direction（方向 GATE 死亡證明誠實頁）兩分頁。

### 3.7.3 證據帳本 `validation_evidence`：讓紅列無處可藏

雙層落點裁決（#29b「這是資料還是文件？」）：敘事層「為何可信/caveat/判讀法」＝論證不增減 → 住 `reports/`（master plan §1.1 逐環矩陣）；機械層「斷言→重驗方式→狀態」＝策展的+會增減+可外部產生 → 住 DB 表 `validation_evidence`。帳本種子一次性 bootstrap（`migrate_validation_evidence_ddl.py`，`ON CONFLICT DO NOTHING` 冪等），此後 SSOT=DB、增列=INSERT 零改碼。重驗三型：`sql`（自動 SELECT）/`script_exit`（白名單命令、`--with-scripts` 才跑）/`manual`（方法論判讀只能人審）。**green 只代表「該斷言此刻對 DB 重驗為真」，明文不代表方法論正確**（那住裁決報告、由人審）——帳本存在的意義就是讓紅列無處可藏。

`verify_validation_evidence.py` 逐列重驗，`sql` 型嚴格唯讀：單條 SELECT 前綴白名單+禁分號（`:36`）+`BEGIN TRANSACTION READ ONLY`+`SET LOCAL statement_timeout='60s'`+`ROLLBACK`（`:39-43`），結果須單列單欄 boolean 否則標 red（`:50`）；斷言寫壞標 red+note、不 crash 整批（`:85-88`，#15）；`--strict` 任一非 green→exit 1（`:108-116`），設計為解凍 GATE 的機械前置。現況 DB：18 green / 1 red、10 chain_link / 19 列（gate=3 含新增 `E4_exclusion_set_contract`），唯一殘紅=`E1_raw_reconcile_exit`（`reconcile_audit.py` 現 exit=1）→故 `--strict` 現會 exit 1。

### 3.7.4 解凍 GATE `prediction_unfreeze_gate`：先凍後跑 + 挪門柱 trigger

GATE 明文鏡射 deliberation B2「先凍後跑」：`criteria` jsonb 快照 + `criteria_sha`（sha256 sort_keys[:16]，`preregister_unfreeze_gate.py:44-46`）+ `preregistered_at`，開跑前 sha 漂移即拒跑。criteria 由 `_criteria_draft`（`:49-74`）組「DB 現值快照」（judgestop/calibrator/econ/model_registry 現值，零 hardcode 已在 DB 之值）+ U1-U6 建議值（標 `proposal:true`）；`--freeze` 須 `--approved-by`（人拍板留痕、AI 不代拍），凍結前斷言 status=draft 且 judgestop 快照==現值。

因解凍在數月後、可能異機異 session，B2「只靠 CLI 斷言」升級為 **DB trigger** `unfreeze_gate_no_goalpost`（`migrate_unfreeze_gate_ddl.py:47-80`，live 已在）做機械閘：(1) 非 draft 後 `criteria/criteria_sha` DISTINCT 即 RAISE（`:56-59`）；(2) 凍後簽核欄改即 RAISE（`:61-64`）；(3) 狀態轉移白名單 `draft→frozen|superseded`、`frozen→evaluated_*|superseded`（`:66-72`），`evaluated_*`/`superseded` 為終態無合法出邊；非 draft 列禁 DELETE（廢止=superseded 留痕，`:50-54`）。「g5 fail=燒 gate」由此落地：`evaluated_fail` 無出邊（連轉 superseded 都不行）→任一 gate fail 該 gate_id 永久留痕、retry 必須另立新 gate_id。`selftest()`（`:175-217`）以 adhoc 假列實測四個非法轉移全被拒。

`evaluate` 守門斷言鏈（`:151-172`，任一敗 exit 1）：status=frozen → criteria_sha 覆算相符 → judgestop 現值==快照（只比對 track∈`A_annotate,B_decay`，`:164`，故新增 R_robust 5 列不誤觸分叉）→ `new_asof>FREEZE` 且 feature_values 實有 >FREEZE panel → 先凍後跑時序。

### 3.7.5 deflation / survivorship / R 軌：把薄 edge 誠實坐實

**deflation** 是編排層+SSOT helper：DSR per-period 正確口徑抽成單一住所 `deflation.py`（`:1-11` docstring 禁平行重寫，因年化 SR 配 sqrt(T-1) 會使 z 灌水 √ppy 倍、DSR 高估~14pp【未親驗，程式文件自陳、本輪未重跑】，本 session 已踩）；`sr_pp=mean/sd ddof=1`（`:28-29`，非年化），`metrics.deflated_sharpe`（`metrics.py:140`）用 `sqrt(T-1)` + 非常態 skew/kurt 分母。N 一律由 `trial_ledger` DB query 機械得出（`deflate_headline_verdict.py:84-86`，禁人手，SOP §6 G7；DB 現 32 列/4 horizon 各 8）。**裁決取較保守**：`dsr_lo=min(家族 N,混頻 N)`（`:129`），因混頻全試驗 N 較大→SR_0↑→DSR↓=保守下界，`passed=dsr_lo>=0.95`（`:135`）；code inline 註記 H120 since2014「N=8 樂觀 95.8% 過 vs N=16 保守 93.6% 未過→判未確立」【未親驗，inline 自陳】，方向與敵③防灌水一致。

**survivorship** 把「倖存樂觀」拆兩獨立效應：①經典下市偏誤≈0（下市邊際 +0.0023 Sharpe，清算 label 取 [entry,exit] 內最後可得還原價、`forward_returns_pit` 限 `date<=exit_` 無 look-ahead）、②完整度閘 incumbency=宇宙定義決策 −16.5%（1.20→1.00）——把整段 −16% 標 survivorship 是誤歸（`survivorship_economic_verdict.py:9-10`；【±數字未親驗，docstring 自陳】）。

**R 軌**（缺口②）復用既有 `revalidation_ledger`（stage='R'）不建新表（#29c）。因 Ridge 決定性→seed 軸零資訊，誠實軸是資料切法：era 校準/相鄰季頻 rank Spearman/真 LOFO 全 walk-forward 重訓/特徵擾動 seeds{41,42,43}/宇宙隨機半切 IC 同號率。先凍後跑靠 judgestop `track='R_robust'` 5 列 frozen + `_assert_prereg_frozen`（`run_model_robustness.py:52-57`，不足 5 即 exit 1）。R 軌性質是 annotate/review 非自動判停（econ 已判 thin）：觸紅→人裁。

### 3.7.6 機械閘與不變式

- **挪門柱 trigger**（`migrate_unfreeze_gate_ddl.py:47-80`，pg_trigger 查得）：非 draft 後 criteria/sha 不可變、凍後簽核欄鎖定、狀態轉移白名單、非 draft 禁 DELETE；selftest 四負向測試實證全被拒。
- **簽核 CHECK**：`chk_ug_frozen_signed`（frozen 必有 approved_by+at）、`chk_ug_eval_signed`（evaluated_* 必有 approved_at+evaluated_at）——DB 實查二 constraint 皆在，強制「凍結=人簽核在先」。
- **evidence CHECK**：`chain_link` 10 值封閉集、`check_type∈(sql,script_exit,manual)`、`chk_ve_sql_presence`/`chk_ve_cmd_presence`；`--strict` 任一非 green exit 1。
- **DSR 保守取大**：`passed=dsr_lo>=0.95=min(家族 N,混頻 N)`（`deflate_headline_verdict.py:135`），方法論鎖禁用樂觀較小 N 灌水過門檻。
- **相對機率唯一口徑**（致命紅線）：`prediction_probability.p_beat_median>0 AND <1` 開區間 DB CHECK（`migrate_probability_ddl.py:79`）、horizon IN(20,40,60,82,120)、econ_verdict IN 三態、rank_pctile∈[0,1]；serve `_check()` 禁語斷言；DB COMMENT 載「絕對漲跌唯經預言機軸 GATE、GATE 前禁」。
- **purge 機械斷言**：`exit_date=t+1` 後第 h 交易日落表；serve 校準器 fit 前 `SELECT count(exit_date>FREEZE)==0` 才標 `purge_verified`（`calibrate_relative_probability.py:112-113`，#8）。
- **as-of 凍結**：`registry.latest` 以 `asof_snapshot<=asof`（`registry.py:47`）；DD 熔斷只用 forward 窗已關閉之過去 panel（`predict_asof.py:69`）。
- **#12 單一住所**：選股唯一住 `build_long_portfolio`（backtest≡live）、DD 唯一住 `drawdown_series`、DSR per-period 唯一住 `deflation.py`。
- **N 機械來源**：deflate 之 N 一律 `trial_ledger` DB query，禁人手；`revalidation_stage_chk` 擴 (B,C,D,R)、`chk_js_track` 擴 (A_annotate,B_decay,R_robust)，DB 實查皆在。

### 3.7.7 陷阱

- **evaluate G1-G5 是 stub、FREEZE 常數硬寫**（承重）：`preregister_unfreeze_gate.py:33` `FREEZE='2026-05-31'` 未隨 07-12 解凍更新，而 `evaluate()` 守門 1-4 過後直接 `return 0`（`:171`）、G1-G5 評分未實作。後果：今日對 asof 2026-06-30 跑 evaluate，守門 1-4 全過會墜落 stub `return 0`——FREEZE 內讓此 stub 安全的「拒跑分支」（設計為本計畫內唯一可實測主路徑）已不再觸發。這是設計時未預期「解凍改為 rolling live 增量」的縫。
- **frozen gate 守著已被取代的基線**：`unfreeze_06dcb178267d`（hugo，07-11 12:08）其 `scope.model_ids` 仍指 4 個 `*_ce62866` 舊模型（H20/40/60/120，無 H82）；07-11 午後 gm 提拔觸發全鏈重訓後生產已換 `3a4e66` 家族（含 H82，共 9 列，`model_registry` 無 deployed 旗標故「生產」係依 created_at 較新+含 H82 推斷）。trigger 禁改 criteria→正解是 superseded+另立新 gate，但目前無新 gate。gate scope 明文排除 H82（`h82_excluded`）但 `econ_verdict_rule` 已有 82=thin——涵蓋面已窄於現行生產面。
- **green≠方法論正確**：07-12「E 債裁定」（hugo）把 E5 survivorship/E2 macro/E7 h60 ece 三列由人裁翻綠；E4 gm 則是 07-11 裁決（選項 a：gm 入 canonical+全鏈重訓）——survivorship 樂觀偏誤本質未消（as-of IC 仍帶 caveat），是人裁除名而非解決。
- **--strict 前置帳面存在、機械未接線**：`--strict` 現因 E1 red 會 exit 1，但 G1-G5 是 stub、無任何機械路徑真消費 `criteria.evidence_ledger_gate`，故現階段不阻擋任何事。
- **E8_econ_verdict_bound 完整性氣味**：現為 green 但 `status_note` 殘留「未回單列單欄 boolean:(None,)」（join 無列→None，依 verify 邏輯應 red），其 green 疑來自人工覆寫/早期狀態，重跑 `verify --run` 可能翻 red，值得解凍前複核。
- **feats_hash 防漂移未實作**（v3 已標 CONFIRMED）：`predict_asof.py:122` `cur_feats` 算出後從未被讀（死變數），`:123` 檢查用的是 `feats`（=artifact 自身凍結集）比對 registry，實為 artifact↔registry 損壞自檢；canonical 若「新增」特徵→靜默用舊 feats 集出單、漂移未被偵測，三處 docstring 宣稱「當下 canonical 不符即拒」是 over-claim。
- **prediction_values self-loop 雙閘是 over-claim**（v3 §11 #2 REFUTED）：`import_isolation` FORBIDDEN/literal 集不含 `prediction_values`、`setup_predict_role.py:39` 把其列入 WRITABLE 且 GRANT SELECT/INSERT/UPDATE 給 `augur_predict`；「禁被回讀當特徵」僅由 DDL COMMENT 約定承載、非機械閘。
- **migrate_probability_ddl `--verify` 與 live DB 矛盾**：其 A-28 斷言（`:168-173`「augur_predict 對四表無任何權限」）在 live DB 會 FAIL——實查四表皆有 SELECT。兩支 migration 腳本 embody 互相矛盾的隔離模型，DB 依 setup_predict_role 那套。
- **風控 overlay 對 H20/40/82 dormant**：`risk_policy` 只 seed H60/H120（各三列），其餘 horizon `predict_asof --risk-control` 印警告、不套任何風控。`COST_TW=0.00585` 散落多支各自定義、非 evaluation 常數；`run_backtest` cost 預設 0.0，caller 忘傳則 net==gross。
- **校準是「同族近似」非同一模型**：校準器 fit 於 walk-forward 逐折 refit 的 Ridge，serve 卻套於 train_ranker 全樣本 artifact 之分位——同 family、非同一模型，`family_note`（A-36）硬揭露此近似性。stale docstring：82 啟用後多支仍寫舊封閉集 {20,40,60,120}（`build_probability_oos_sample.py:18`、`predict_asof.py:198`）。

### 3.7.8 07-10（v3）之後的變化

- **整個驗證 harness 是 v3 之後淨新增**（CONFIRMED）：v3 §3.9 已涵蓋 `deflation.py`/survivorship/revalidate（B/C/D），但「證據帳本 `validation_evidence` + 解凍 GATE `prediction_unfreeze_gate` + R 軌 `run_model_robustness`」完全不在 v3。五支核心 script 全於 2026-07-11 commit `d973b81`（「驗證總綱 V0-V2 落地，hugo 親簽」）一次落地，對應 master plan（`reports/augur_prediction_validation_master_plan_20260711.md`）。
- **R 軌已實跑非僅規劃**：`revalidation_ledger` stage='R' 有 356 列（calib_era 64/lofo 236/perturb 16/rank_autocorr 32/subset 8），judgestop 由 6→11 列（新增 R_robust 5 policies，全 frozen created 2026-07-11 11:56，早於 ledger 寫入 min 11:59）。
- **FREEZE 於 07-12 解凍入憲**（原則精華 v1.9.0/憲章 v1.43.0）轉 live 增量維運：`feature_values` 現到 2026-06-30、有 91,385 列 >FREEZE（v3 時代 FREEZE=2026-05-31）；此舉反轉 evaluate 拒跑分支條件（見 §3.7.7），但 GATE 的 FREEZE 常數與 G1-G5 主體尚未隨解凍更新。
- **07-11 全鏈重訓**：gm 提拔入 canonical（交集 gate 起點 2007-12-31→2008-12-31、28→29 特徵、feats_hash 變），觸發重訓；`model_registry` RankRidge 由 4→9 列（ce62866 4 + 3a4e66 5 含 H82，新舊並存）；`probability_oos_sample` 42,456→41,860 列；`prediction_probability` 1,376/4h→1,695/5h。
- **H82 啟用**（commit `ea3e1f9`, 07-11）：封閉集 {20,40,60,120}→{20,40,60,82,120}，live 現有 H82 calibrator + 339 列 emit。
- **econ_verdict 由 Python dict 遷為 DB 表**（`abf5da8`, 07-11，#29b）：`calibrate` 改讀 `econ_verdict_rule`、缺列 fail-loud。
- **serve 新增兩誠實分頁**（`163caf0`, 07-11）：/simulate（蒙地卡羅逐日情境錐、四鎖）與 /direction（方向軸六門死亡證明誠實頁）。
- **augur_predict role 現況已建帶 grants**（v3 為 provisioned-but-unwired）；但 predict runtime 是否真連此 role（`DB_PARAMS_PREDICT` wiring）本輪未再驗、沿用 v3 「走預設 role」未閉環標記。`risk_policy` 現已 seed H60/H120（v3 那台為空/dormant，差異可能是機器狀態非純 code 演進）。

## §3.8 方向軸/預言機：GATE/probability/二次證偽判死/輸出契約

**▶ 一句話**：把「某股未來 H 天漲/跌的機率」這個危險假兆需求，關進「先凍判準→人核准→機械覆算→過關才展示、不過就判死留檔永不出 UI」的可證偽閉環；實證結局是 v1 六門＋v2 四門在凍結快照上全數 `evaluated_fail`（二次證偽），方向軸凍結至真未來新資料、不開 v3。

### 這層在做什麼

這是絕對方向機率軸，與既有「相對機率」軸並立、疊加不拆——相對軸問「P 是否勝過同儕中位數」（靈魂產品），絕對軸問「N 天漲的機率是多少」（危險假兆）。它存在的理由不是「答得出」，而是「寧可誠實判死，也不讓未經 GATE 的絕對方向數字污染系統」。核心產物三件：`direction_gate`（可證偽賭注載體）、`direction_probability`/`daily_direction_probability`（過門後才有列的產物表）、以及判死後憲法唯一允許回應「未來逐日股價路徑」的形式——MC 模擬情境。此軸唯記錄面、不進預測管線。

### 怎麼建的（機制為主）

**立法先行、鏡射前例**：2026-07-11 先立憲（憲章 v1.42.0「預言機誠實判準」、靈魂 v1.6.0）再建 code。`direction_gate` 刻意鏡射既有 `prediction_unfreeze_gate` 的狀態機（preregister→approve→evaluate、status 封閉枚舉），讓「先凍後跑、approve 唯人」的紀律沿用同一機械骨架（`migrate_direction_gate_ddl.py`）。母法住 `docs/系統架構大憲章_v1.45.0.md:127-136`。

**挪門柱＝DB trigger 機械閘（非腳本自律）**：每 (track,horizon) 一列 gate，`criteria`(JSONB)＋`criteria_sha`（sha256 前 16 碼）在跑任何 OOS 數字前寫死。函式 `direction_gate_no_goalpost()`（`migrate_direction_gate_ddl.py:42-72`）四件事：① DELETE 且 `OLD.status<>'preregistered'` → RAISE（敗退留檔、廢止只能走 superseded，`:45-49`）；② approved 後 `criteria`/`criteria_sha` 任一變 → RAISE（`:51-54`）；③ 終態列（`evaluated_pass`/`evaluated_fail`）的 `result_snapshot`/`evaluated_at`/`evaluation_ref`/`git_sha` 變 → RAISE（判決快照凍結不可回改，`:56-62`）；④ 狀態轉移限白名單 `preregistered→approved|superseded`、`approved→evaluated_*|superseded`（`:63-69`）。安全繫於 trigger `trg_direction_no_goalpost`（live DB 已掛）而非腳本自律。

**三關機械裁判**（`evaluate_direction_gate.py:133-214`）：(i) hit-rate 顯著優於「同窗全局多數類固定方向基線 max(p̄,1−p̄)」——逐 panel 算 (hit−naive) 序列→HAC 去相關 Eff-t（`effective_t_hac`，lag 由 `criteria.hac_min_lag` 覆蓋月頻重疊窗）→單尾 p<alpha；**禁裸 iid t**（重疊窗高估，`:168-172`）；(ii) OOS Brier < 基線 p̄(1−p̄)；(iii) ECE ≤ DB 凍結上限＋p_up 十分位 vs 實現上漲頻率 Spearman 單調。三關全過＝`evaluated_pass`，任一不過＝`evaluated_fail`，全裁決落 `result_snapshot` 可溯。

**estimand 引擎（封死挪門柱後門，v1→v2 關鍵修）**：`criteria.estimand` 機械凍結 model_id/窗/seed 聚合，`_fetch_samples` 依此參數化取樣（`evaluate_direction_gate.py:88-124`）；若某 gate 無 estimand 而目標表含多個 model_id → `SELECT count(DISTINCT model_id)>1` 直接印「拒判」回 `REFUSE`（`:125-128`），堵死「事後挑贏面模型貼別人準確率」的自由度；`min_clusters` 未達也 REFUSE（`:112-117`）。另有判前 `_assert_clean_tree()`（`:79-85`）：工作樹不 clean 即 `sys.exit`，確保 `evaluation_ref` 真釘得住腳本內容（補 v1「判時 evaluate 腳本未入 git」教訓）。

**approve 是人類 TTY 專屬決策閘**：`approve()` 首行 `if not sys.stdin.isatty(): sys.exit(...)`，AI/腳本一律 fail-closed 拒（`preregister_direction_gate.py:322-324`）；`criteria` 由腳本產生（判準值＝計畫建議），但「這門算不算數」唯人在自己終端逐門簽。DB 另有 CHECK `chk_dg_approved_signed` 強制 approved/evaluated 狀態須有 approved_by+approved_at（`migrate_direction_gate_ddl.py:37-39`）。決策層 vs 機械層二分落到 code。

**v2 復活攻堅＝上膛全部未試彈藥後仍證偽**：v2 修好 v1 全部程序缺陷（真 purge、正確基線去千里眼、estimand 凍結、purged isotonic 校準），並餵入籌碼五族/六市場特徵/月頻 panel/特徵直餵，四門仍 eff-t≈0、Brier 全敗、ECE 全過＝「乾淨的死亡、無訊號」（`preregister_direction_gate.py:74-127` `_criteria_v2`）。結論寫進 `criteria.fail_path`：v2 家族全 fail＝凍結至解凍＋新資料、不開 v3。結案報告 `reports/augur_oracle_direction_v2_verdict_20260711.md`（hugo 親簽 2026-07-12）。

**MC 模擬四鎖＝判死後唯一合法路徑回答**：對 as-of≤FREEZE 歷史日報酬做純歷史重抽（iid＋block bootstrap 雙法、BLOCK_LEN=21td），**零模型 tilt**（中位走向純由該股自身歷史分布決定，非已判死的方向模型，`simulate_mc_paths.py:4-10,60-72`）。四鎖（`:9-10`）：①摘要硬綁 disclaimer「模擬非預測」（`:36`）；②只存 summary 分位錐、絕不存逐路徑；③數字不入 chat payload；④憲章明文。外加 DB CHECK `mc_simulation_run_is_simulation_check = CHECK(is_simulation)` 讓該布林永遠只能 true。live DB 已有 520 筆模擬 run。

**輸出契約＋產物表 fail-closed DB 化（O1，2026-07-12）**：三產物（方向機率／horizon 級準確率／E[r]）落既有兩表，補 `expected_ret`/`hit_rate` 欄；掛 BEFORE INSERT/UPDATE trigger `direction_product_gate_guard` 對非 `evaluated_pass` 門一律 RAISE（把 fail-closed 從腳本 if 下沉為 DB 不變式，修對抗審查 H1 blocker，`migrate_direction_product_gate_ddl.py:30-43`）。`produce_direction_probability.py` 改「呈現 gate 所驗證的 arena artifact 本身」不重訓（修 F1）；E[r] 用閉式 `(2·hit−1)·vol−cost`（`:104`）；`econ_verdict` 唯讀自 `direction_econ_verdict`，缺列即拒產（H3，`:84-88`）；market 候選無 registry model_id 者路由到 ledger 呈現、不入產物表（F2，`:89-93`）。

**真未來 live 擂台＝唯一復活路的帳本層**：`direction_arena_candidate`（參賽者凍結協定，insert-only）＋`direction_arena_prediction`（反回填 trigger 強制 `pred_date` 貼緊台北今日）＋policy＋verdict（futility 三態），共 3 個防篡改 trigger。arena 判準以 prereg-now-evaluate-later 預註冊、Bonferroni α=0.05/K、MDE/檢定力機械凍入 criteria（`migrate_direction_arena_ddl.py`、`preregister_direction_gate.py:175-232`）。

### 機械閘與不變式

| 不變式 | 機制 | 出處 |
|---|---|---|
| 挪門柱鎖 | approved 後 criteria/sha 不可變、終態快照凍結、狀態轉移白名單、非 preregistered 不得刪 | `migrate_direction_gate_ddl.py:42-72`（trigger live 已掛） |
| approve 唯人 | `sys.stdin.isatty()` 硬擋＋CHECK `chk_dg_approved_signed` | `preregister_direction_gate.py:323`、`migrate_direction_gate_ddl.py:37-39` |
| 產物表 fail-closed | 寫入時 gate 須 `evaluated_pass` 否則 RAISE；live 兩表 0 列坐實 | `migrate_direction_product_gate_ddl.py:30-43` |
| estimand 拒判閘 | 無 estimand 而多 model_id → REFUSE；min_clusters 未達也 REFUSE | `evaluate_direction_gate.py:125-128`、`:112-117` |
| 判前 clean-tree | 工作樹不 clean 即 `sys.exit` | `evaluate_direction_gate.py:79-85` |
| 模擬非預測硬綁 | `CHECK(is_simulation)` 使布林永只能 true；method 限 iid/block | `simulate_mc_paths.py`＋pg_constraint |
| 擂台反回填 | `pred_date < 台北今日−1` 即 RAISE；結算欄唯 NULL→值一次；預測欄凍結；對局列不得刪 | `migrate_direction_arena_ddl.py:97-132`（3 trigger 全掛） |
| 候選凍結協定 | spec/身分欄不得變、參賽列不得刪（退役＝status）、retire_note 單次寫 | `migrate_direction_arena_ddl.py:91-94` |
| ECE 門檻 DB 讀值 | `ece_ceiling` 讀 `judgestop_threshold.calib_late_ece_ceiling` frozen 列，缺列即 exit | `preregister_direction_gate.py:134-137`、`evaluate_direction_gate.py:184` |

### 陷阱（gotchas）

- **v1 H 軌「千里眼基線」程序 bug**：v1 用逐 panel 實現值挑贏面當 naive 基線（偷看），使模型 eff-t 巨負（H_20 −3.35／H_40 −4.98／H_82 −5.79、p≈1.0），看似 hit .548-.604 卻遠輸偷看基線；v2 改「全局多數類固定方向」後 eff-t 回到 ≈0（`preregister_direction_gate.py:80-82`）。
- **D5「近失」是程序灌水非訊號**：v1 `dgate_D_5` hit p=**.03813** 過關，但那是 best-of-2 champion 選擇＋零 purge 的名義值；v2 修 champion 選擇＋purged isotonic 後 `dgate_D_5_v2` 退到 p=**.07193**（不過關，DB 實測坐實）。
- **Brier 天花板就在基率附近**：`dgate_D_5_v2` purged isotonic 也翻不正 Brier（.25389 vs 基線 p̄(1−p̄)≈.25），ECE 全過＝模型誠實地不知道——校準沒問題、就是沒超越基率的資訊，不是壞掉是無訊號。
- **market 候選寫不進產物表**：`direction_probability.model_id` FK→`model_registry`，但 gate-eligible 擂台候選（own_daily_rolling/chronos/timesfm/own_stack/own_threelens）刻意不在 registry（`registry_model_id=NULL`），produce 只能路由到 ledger 呈現、不入產物表（`produce_direction_probability.py:89-93`）。
- **`direction_econ_verdict` 表為空（0 列）**：produce 無 econ_verdict 列即 fail-closed 拒產（H3），故即便未來有 pass 門，也須先把經濟裁決落 `direction_econ_verdict` 才能出 E[r]（`:84-88`）。
- **擂台 armed 但未開賽**：6 個 `dgate_arena_*` 已 approved、9 候選已註冊，但 `direction_arena_prediction`＝0 列——真未來對局尚未產生任何預測，故 arena 六門都還沒 evaluate。
- **本機 DB 落後於 repo 程式（A3 家族分歧）**：code 的 `A3_GATES` 已是 `_r2` 版（`preregister_direction_gate.py:166-172`，註解稱原三門 approved→superseded），但此機 live DB 只有非-`_r2` 的 `dgate_a3_threelens_20/40/82` 停在 `preregistered`（approved_by=NULL）、全庫無 `_r2` 亦無 `superseded` 列——此機 pgdump_20260712 早於 A3 `_r2` 重註冊工作（與 memory「A3 `_r2` 三門已簽」分歧，此處以 DB 觀測為準）。
- **相對軸 vs 絕對軸別混**：`serve_probability_ui` 的相對機率頁（P 勝過同儕中位數）是靈魂產品、方向軸判死零影響；方向 GATE 判死只封絕對方向機率，兩者永不混排（致命紅線口徑）。
- **econ 相對揀選是假兆軸**：`run_direction_econ_eval` 的相對揀選 Sharpe alive 屬既有相對邊際、不歸功方向模型（panel 內 P_mkt 全股同值→p_up 排序≡rank_pctile 排序）；唯「市場擇時 overlay 勝 buy&hold」才是方向模型獨特 claim，實測 dead（`run_direction_econ_eval.py:33-38`）。
- **H120 review 級天花板**：即便三關全過，n=35 非重疊樣本使 H120 被 `review_tier_cap` 鎖在「觀察名單」（review_observation_only）、不得完整展示——criteria 預先寫死、展示端據以降級（`preregister_direction_gate.py:61-62`）。

### 07-10(v3)之後的變化

整個子系統為 v3（2026-07-10）之後全新建置——v3 報告全文零提及 oracle/預言機/direction_gate（親驗 `grep -cE` 回 0），首批 direction 程式 commit 皆為 2026-07-11（`ea3e1f9` 憲章 v1.42.0 立法＋基建、`163caf0` 全建置鏈＋經濟終關六門判決＋MC 四鎖）。時間軸：

- **2026-07-11**：v1 六門（H20/40/82/120＋D1/D5）機械裁決全 `evaluated_fail`＝第一次證偽。
- **2026-07-11**：v2 復活攻堅（`5d59300` 擂台 A0 骨架、`b3b709e` v2 四門全 fail）＝第二次證偽，結案 `augur_oracle_direction_v2_verdict_20260711.md`。
- **2026-07-12**：no-v3 入憲（`7d337ec` 憲章 v1.43.0，`docs/系統架構大憲章_v1.45.0.md:136`「對凍結快照不得另立同假說新 gate、確證唯真未來 live 擂台」）＋ FREEZE 解凍拍板。
- **2026-07-12**：輸出契約入憲三段式——`18afc31` 計畫草案＋對抗審查（Opus 4.8，4 blocker/停下問）→ `a57d1da` v1.44.0 和解式增修（二度堅持）→ `1cdee99` v1.45.0 刪靈魂原句「不是預測絕對漲跌幅」＋E[r] 升格為得逐股呈現的幅度級產物（三度堅持，AI 勸阻與三度堅持雙留痕，`docs/系統架構大憲章_v1.45.0.md:129`）；守住的界＝econ_verdict 同源（判死不顯數字）、單股準確率宣稱仍禁、逐日路徑永久除外（P1-4）。
- **2026-07-12**：O1 fail-closed DB 機械閘落地（`395e107` 產物表 gate guard trigger）＋ O1 三產物生產器（`3ec0d12`，fail-closed 實證 0 列）。

**live DB 現況**（此機 pgdump_20260712）：`direction_gate` v1 六門＋v2 四門（10 門全 `evaluated_fail`/`never_shown`/approved_by=hugo）、arena 六門 approved 待開賽、a3 三門 preregistered；產物表兩表 0 列、`mc_simulation_run` 520 筆、`direction_arena_prediction` 0 筆。

## §3.9 直播擂台+三鏡頭候選:A0-A3／預註冊／九選手

### ▶ 這層在做什麼

直播擂台（direction live arena）是方向軸「先凍後跑」的**真未來競技場**：九個方向預測候選（自家配方 own／市場基礎模型 market／樸素基線 baseline）在真實未來台股價格上同場出手，預測落一張**不可篡改帳本** `direction_arena_prediction`，效力唯由「跑任何 OOS 數字之前就凍死的判準」`direction_gate` 裁決。它存在的理由，是給二度證偽（v1／v2 皆判死）的方向軸一條 **no-v3 合規復活路**：凍配方 → 真未來出預測 → 凍判準裁決，絕不回頭在凍結歷史資料上重試調參。三鏡頭候選 `own_threelens_interact` 是新參賽者，賭「DirStackM 只餵 7 壓縮特徵、把方向訊號壓沒了」——把瓶頸拆掉，35 基礎特徵 + 9 對跨鏡頭交互直餵方向軸。

### 怎麼建的（機制與為什麼）

**四表三 trigger 帳本層**（`scripts/migrate_direction_arena_ddl.py`，DDL 單一住所）：`candidate`（參賽者凍結協定，insert-only）／`prediction`（對局帳本）／`policy`（futility 閾值）／`verdict`（futility 三態閉集）。三個 trigger 把真未來機械化為 code 而非自律，`verify()` 內含 3 個負向單測（`_expect_raise`），全在單一交易內 `conn.rollback()`（`:170`）零落地——「機械化而非自律」是這整層的設計基調。

**統一 adapter 介面**（`src/augur/arena/adapters.py`）：`predict(series, horizon_td, context=None) -> dict[str,float]`，REGISTRY 8 個 adapter（3 baseline + own_daily／own_stack + chronos／timesfm + own_threelens）。市場模型「樣本路徑→p_up」的轉換口徑寫死於 code、隨 `code_sha` 凍結（`:300-306` 分位插值：`last<=qe[0]→p=0.95`、`last>=qe[-1]→p=0.05`，非校準機率、是分位插值近似）。adapter 原則上零 DB 零網路，`OwnThreelensInteract` 為唯一例外（讀自己的特徵表 + 價格；`SYNTH_*` 冒煙走中性 0.5、任何缺料 except→全 0.5 不編造）。

**prereg-now-evaluate-later 的 gate**（`scripts/preregister_direction_gate.py`）：判準＝三關（hit-rate 顯著優於同窗多數類基線，HAC／date-cluster 禁 iid；Brier<p̄(1−p̄)；ECE≤DB 讀值+分位單調）。MDE／檢定力由 `_power_ref` 在**預註冊當下機械算一次凍入** criteria jsonb、`criteria_sha` 綁死（per-cluster hit-rate sd + AR(1) LRV 膨脹 → effective_n → 各檢定力可偵測邊際）。approve 唯 hugo TTY：非 isatty 即 `sys.exit` fail-closed（`:323-324`）。

**兩個獨立家族**：A2 arena K=6（own_daily／chronos／timesfm×D5 + own_stack×H20/40/82），α=0.05/6=0.00833（`:195`）；A3 threelens K=3（own_threelens_interact×H20/40/82），α=0.05/3=0.01667（`:252`）。跨家族多重性**全序列揭露**＝v1 六門 + v2 四門 + A2 六門 + A3 三門＝19 門一律全列（`:254`，憲章 v1.45.0），不得單挑活門講故事。

**三鏡頭月頻鏈**（`scripts/build_threelens_monthly.py`）：execution 期把模組全域常數 `panel.FEATURE_TABLE` 換成新表（`:67`），**直接複用 `feature_values` 的同一支 generator**（`panel.build_panel`）——零複製、零口徑漂移、同碼同值。再以 SQL 補 9 對跨鏡頭交互（每 panel 橫斷面 z-score 後乘積，`WINDOW w AS (PARTITION BY panel_date, feature)` `:45`、`a.zv*b.zv` `:48`，`interact__` 前綴），`INTERACT_PAIRS` 9 對先驗凍結（`:27-37`，拍板後不得增刪改）。113 月 panel 完全鏡射 `direction_stack_feature_monthly` 窗（2017-01-24→2026-05-29）。

**市場隊 adapter**（Chronos-Bolt／TimesFM）：lazy import 本地權重，分位頭預測終點分位 → 以現價在分位曲線的線性插值位置得 P(終值>現價)；無套件／OOM → RuntimeError＝operational 除名事由誠實留痕、不阻其他隊。register 時強制 license 白名單（apache-2.0/mit）+ `offline_only:true` + provenance repo/revision（`scripts/register_arena_candidate.py:77-81` 四道 assert）。

**結算**（`scripts/settle_arena_labels.py`）：以已實現 TAIEX 交易日曆**動態數 label 日**（`bisect_right` `:53`，不猜未來日曆）；停牌分支 last_trade/unsettleable；PriceAdj factor 不連續檢核——唯 `f1 < f0*(1-FACTOR_TOL) and f0 < 1.0` 才判違規（`:142`），拼接損傷（f<1 回落）標 unsettleable 排除、減資／公司行動（f≥1 收斂）豁免不攔（`:125` 註解「175 檔誤標教訓」）。

**futility 判停 + 計分板**（`scripts/arena_scoreboard.py`）：讀凍結 policy（60,1.645），excess（hit−基線）單邊 95% 信賴上界<0→suspected、連續 2 輪→confirmed_stop_entries＝**只建議停出新預測**，ledger 全數留家族入 gate 不除名（`:8-9`「除名＝倖存者 K、FWER 失效」）。全部 review 級：固定字串 `FIXED = "review 級・觀察中・非裁決・非交易訊號"`（`:31`）機械斷言，裁決效力＝零、gate 判決唯 `direction_gate` evaluate。

### 三鏡頭候選的隔離：宣稱 vs 落地（更正版）

計畫書意圖是「own_threelens_interact 相對 own_stack_rolling 的 delta **只有特徵寬度**（個股側 7→44 直餵）、市場 context 與 DirStackM 同款不變」，藉此把 A3 gate 結果單因子歸因於特徵寬度。**此隔離並未落實於 adapter，正文採更正版**：`own_threelens_interact` 相對 `own_stack_rolling` 至少**三處同時變動**——

1. **特徵集**：44 純個股特徵 vs `own_stack` 的 6 維含市場分量 `[logit(p_mkt), rank−0.5, 交互, vol, mom, beta(對 TAIEX)]`（`adapters.py:157,207` vs `:311,354`）。
2. **模型架構**：HistGBM 3-seed（SEEDS=(7,42,2026) `:318`）+ isotonic vs L2 Logistic Regression（`OwnStackRolling` make_pipeline）。
3. **市場 context**：由「用（lg+beta）」變為「**完全不用**」——`adapters.py:315` 白紙黑字「市場 context 不用——與 own_stack 之 delta=特徵寬度」、`register_arena_candidate.py:65` spec 亦「市場 context 不用（delta=特徵寬度）」，該註解正面否定了自己「與 DirStackM 同款不變」的宣稱。

結論：「delta 只有特徵寬度」與「市場 context 同款不變」**皆不成立**；若 A3 gate 未來 pass/fail，**無法歸因於特徵寬度單一因子**（三處混淆）。成立的兩點是：工程冒煙非 gate 宣稱（`train_direction_threelens.py:93`）、效力 100% 讓給 A3 真未來家族（防偷跑 v3）。

### 機械閘與不變式

- **candidate 凍結協定**：trigger `arena_candidate_frozen`（函式 `migrate_direction_arena_ddl.py:73-94`）拒 DELETE、拒改 spec/team/track/gate_eligible/code_sha/weights_hash/frozen_at，retire_note 僅單次寫；換版＝新候選新列。
- **反回填鎖**：trigger `arena_pred_no_backfill`（`:97-107`）拒 `pred_date < 台北今日−1`＝真未來機械保證，斷檔＝無列不補跑。
- **對局列不可篡改**：trigger `arena_pred_immutable`（`:110-132`）凍結 p_up/pred_date/created_at/身分欄，結算欄唯 NULL→值一次。
- **criteria sha-lock**：`check()` 重算 `_sha` 不符＝挪門柱（`preregister_direction_gate.py:345-347`）；DB CHECK `chk_dg_approved_signed` 強制 approved/evaluated_* 類須 approved_by/approved_at 非空。
- **MDE／檢定力機械凍入**：`_power_ref` 於預註冊時算 sd/rho1/inflation/effective_n/mde_power80_pp 入 criteria jsonb 隨 sha 凍結，預註冊後不可事後改（#9 可溯源）。*（措辭精確化：criteria 中的 `sd` 實為「每 panel 原始 hit-rate 之 std」，非計畫用語「excess-hit sd」；凍結機制與數字成立，唯一詞不精確。）*
- **9 交互對先驗凍結**於 `INTERACT_PAIRS` + candidate spec jsonb（insert-only trigger 保凍）。
- **結算 fail-closed**：逐列斷言 created_at（台北日）<label 日，違者整批禁結算 exit 1（`settle_arena_labels.py:9`）。
- **futility 非裁決**：計分板固定字串 review 級、confirmed_stop 只建議停新預測、ledger 不除名（FWER 保全）。

### 陷阱

- **panel.FEATURE_TABLE 隱性全域副作用**：`build_threelens` 執行期 mutate 模組全域常數換目的表（`:67`）；分開跑 script 無虞，但若同進程內與一次 `feature_values` build 並跑會**污染目的表**。
- **A3 gate 未核准仍會出手**：`run_arena_round.live_round()` 的機械閘只查 `dgate_arena%` approved（`:68`，A2 家族全域開關），`:100` 取全體 `status='active'` 候選逐列 INSERT ledger，**無 per-candidate A3 gate 核准檢查**。故 A2 一經核准、H 軌出手日到，`own_threelens_interact`（active、track=H）即落 ledger，縱其 A3 三門僅 preregistered——A3 的「approve 前零預測」是**程序約束、非機械強制**（現值 ledger=0 故尚無實害，但 code path 如述）。
- **futility 閾值 D 軌校準用在 H 軌**：`futility_min_clusters=60` 照 D 軌日頻校準（≈3 個月日 cluster）；H 軌月頻下 60 clusters=5 年 → 實務上 H 軌 futility 幾乎不觸發（已知、屬保守 review-only、可接受）。
- **adapter docstring 概括不準**：模組 docstring 稱「adapter 自己零 DB」，但 `OwnThreelensInteract` 是例外（讀 `direction_threelens_feature_monthly` + `TaiwanStockPriceAdj`）。
- **19 門揭露只落在 A3 criteria**：A2/arena 門凍結時 A3 尚未存在，其 family_disclosure 停在「16 門」；19 門全序列揭露僅落在最新 A3 門的 criteria——這是**正確的逐新家族累積揭露**行為、非缺陷。
- **擂台實際尚未開賽**：ledger 現況 0 列、無 cron（A2 提案＝首日手動陪跑）；結算 UPDATE 路徑是 A0 合成冒煙時無法測的最後一塊，仍待首批真列驗證。

### DB 與 code／memory 三方不一致（最重要，須以 DB 為準）

現行 live DB 的 A3 三門是 **pre-`_r2` 原始列** `dgate_a3_threelens_{20,40,82}`：`status=preregistered`（未 approve、approved_by=NULL）、`criteria_sha` 為 **12 碼（手刻配方 bug、無 separators）**，且 DB 中**完全無任何 `_r2` 列**。但 git HEAD 的 `A3_GATES` 皆帶 `_r2`（`preregister_direction_gate.py:169-171`、`_sha()[:16]` 產 16 碼），memory 索引亦宣稱「A3 `_r2` 三門已簽」。更強的矛盾：code 註解 `:167-168` 稱「原列 approved→superseded 留檔」，但 DB 原列 status 從未 approved、從未 superseded。判讀：`_r2` 重簽 + 核准**從未對此還原 dump 所屬的 DB 執行**——換機還原後 A3 家族實際處於「原始 buggy-sha 預註冊、未核准」，與交接記憶「已簽」落差。**本報告以 DB 現況為準**：A3 尚未 approved，own_threelens_interact 之 gate 效力尚未凍定生效。

### 07-10（v3）之後的變化

整個 arena 子系統是 v3 報告之後才建（v3 僅在方法論層提三鏡頭為假說鏡頭 + 方向軸判決，無任何 arena 內容）。建置序：A0 骨架（5d59300）→ A1 全套 script（a7a2c0c）→ A2 ready + MDE 機械凍入 + PriceAdj 修復（e47e453）→ chronos adapter API 對齊（0e59a70）→ 三鏡頭 T1 月頻鏈啟建（5edc549）→ T2-T4 冒煙 trainer/adapter/凍結註冊/A3 預註冊（8959055）→ A3 `_r2` 重簽 + 開賽前置全簽封存（5a93cdc）。

落地成果（親驗 CONFIRMED）：`direction_threelens_feature_monthly` 已建 **113 panel × 44 特徵＝2,229,083 值**（其中 461,882 交互值），窗完全鏡射 stack 表；**A2 六門已 hugo TTY approved**、futility（60,1.645）已凍入 `direction_arena_policy`（frozen=t）；候選定版 **9 列註冊（5 gate_eligible**；own_v2_frozen 對照列 + baseline×3 不立門）；timesfm 條件款（權重下載停滯即依凍結協定除名留痕）；no-v3 + FREEZE 解凍（07-12，v1.9.0/v1.43.0）入憲＝擂台「真未來新實驗、不構成對凍結資料重試」的合法性基礎。**唯一未生效的 delta**：A3 `_r2` sha bug 修復在現行還原 DB 未套用（見上一子節）。

---

# 半-2 素養／顧問系統：逐子系統 HOW-built

## §4.1 knowledge 管線+語意橋:source→staging→promote→全文三軌→句→統計軌

### 這層在做什麼

把「全球公開知識 + 用戶自有私有檔」忠實落地成 PostgreSQL,供顧問層(advisor)檢索作答的「誠實博學的我」引用——但**素養層對量化預測管線零貢獻、機械隔離**。管線五段:①`knowledge_source`(DB registry:adapter+查詢模板)→acquire→②`knowledge_staging`(pending 待審,帶 provenance)→promote(冪等去重晉升七類條目/哲學實體)→③`knowledge_item`(metadata)→fetch 全文(**license 三軌 gate**:公版/CC/owned_local 才抓)→④`knowledge_item_text`(逐字全文)→build_sentences(確定性 regex 切句)→⑤`knowledge_sentence`→embed(e5-small)→可檢索。三條設計哲學:**「擴新領域=INSERT 一列 DB、零改碼」**(#29b)、**「harvest 完成=到達該內容 license 允許之可答終態、非止於標題」**、**「license 阻擋是誠實終態(`fulltext_blocked`)、非漏做」**。

### 怎麼建的(五段管線 + 為什麼)

**1｜三層引擎取代九支批次(#29c)**：`acquire_knowledge.py`(通用擷取)+ `promote_knowledge.py`(晉升)兩支參數化引擎。acquire 從 registry 讀 adapter/query_template/adapter_config/approval_status/pace_seconds(`acquire_knowledge.py:330-332`),依 adapter 名分派(`:342` `ADAPTERS[src[1]](...)`);**14 個 adapter** 註冊於 `ADAPTERS` dict(`:298-305`),各約 15 行、只回 API 原值寫 `knowledge_staging`。擴新領域=INSERT 一列或 `--domain` 覆寫(`:341`)零 code;新「來源協定」才寫新 adapter(如 oai_pmh 為 OAPEN 新增),通用 JSON API 甚至用 `adapter_generic_json` 靠 adapter_config 的 results_path/fields 對映(`:246-269`)零 code。key 走 header 不落 provenance(`:61-65`)。

**2｜promote 晉升去重**：`MAPPERS` dict 把 `staging.entity_type` 分派到 mapper(thinker→philosophy_thinker、work→philosophy_work、citation/school→philosophy_source、七類 paper/report/dataset/compound/material/protein/species→knowledge_item);`EXTID_PRIORITY` 11 鍵跨源去重(`promote_knowledge.py:127`),無 external_id 者退回 title+year 去重(對齊 partial unique index `uq_item_title`);work 無 thinker 歸屬且非哲學域者後援轉 knowledge_item(`:219-223`)。冪等:已存在標 dup、成功標 promoted。

**3｜harvest 批次驅動器**：`harvest_knowledge.py` 讀 `knowledge_query × knowledge_source × knowledge_taxonomy` 組排程矩陣(`_Q_CORE:98-108`),其 `JOIN knowledge_domain_map`(`:100`)過濾未拍板域=**治理閘**;逐組合 subprocess 呼叫 acquire、輪末呼叫 promote。`knowledge_harvest_log` 是 resume 心臟(`status` CHECK ∈{ok,empty,error};`error AND attempts<2` 才重跑,`_Q_CORE:108`;429/503/timeout=temp 不累加 attempts;永久錯上限 2 除役,`:84`)。DDL migrate 唯一住所=本 script(`:55-95` 全冪等 `CREATE IF NOT EXISTS`),啟動時自建 knowledge_item/harvest_log/domain_map。

**4｜全文抓取兩條路 + license 三軌 gate**：
- **OA 路**(`fetch_oa_fulltext.py`):拿 DOI 問 Unpaywall best_oa_location,四值 license 白名單(cc-by/cc-by-sa/cc0/pd)才入庫;NC/ND/null/PDF/非 html-plain/過短一律 skip 並寫 `knowledge_fulltext_status` 誠實終態帳。`PENDING_WHERE`(`:93-99`)以 `NOT EXISTS` 排除已落帳者→下輪不重問 Unpaywall=收斂省 API。
- **公版路**(`fetch_pd_fulltext.py`,07-13 新):是「源專屬解析器 dispatcher」——`resolve_target`(`:53-89`)依 `adapter_config.fulltext.strategy` 分派 `url_template`(IA `_djvu.txt`)/`edgar_archive`(從 staging payload cik 組 SEC 檔案 URL)/`fraser_api`(title API 取 location.textUrl);**無策略=直鏈 text/plain 向後相容**(`:56-57` `return url,"text",...`);html_strip 模式 `import fetch_oa_fulltext.strip_html` 單一實作(#12,`:29`)。

**5｜切句=零 ML 確定性 regex**(`build_sentences.py`):zh 走全形句末標點+引號閉合(`ZH_END_RE:35`)、en 走句末標點+空白+大寫起頭(`EN_CUT_RE:36`),`split_sentences`(`:56-75`)帶 `char_start/char_end` 使 `content[s:e]==sentence` 可精確切回原文(逐字零 AI #1、半年重跑一致 #15),`_trim_span` 保證首尾非空白。讀 CLEAN 述詞 SSOT `corpus.clean_work_sql`(`review_flag=false AND corpus_class='literary'`,NULL fail-closed,`corpus.py:29,35`)排除未稽核/reference 語料;批 500 段/commit、`WHERE NOT EXISTS` resume。嵌入分離存 `knowledge_sentence_embedding`(e5-small multilingual),由 `refresh_knowledge_pipeline.py` 的 Stage 鏈(fetch_oa_fulltext→build_sentences→embed_knowledge)自動接——**注意此 timer 鏈只走 OA 路、不含 pd 解析器**。

**規模落地(DB 實查)**：`knowledge_sentence` 1,756,817 句(哲學側 text_id 1,542,146 + items 側 itext_id 214,671);`knowledge_sentence_embedding` 1,696,984 列(單一 model_tag `intfloat/multilingual-e5-small`,≈96.6% 已嵌)。

### 機械閘與不變式(enforced_where)

- **license 三軌 DB CHECK**:`knowledge_item_text_license_check` 限 5 值 `{public_domain,cc-by,cc-by-sa,cc0,owned_local}`;`chk_itext_owned_local_private` = `CHECK((license<>'owned_local') OR (access_scope='local_private'))` 把 owned_local **物理綁死** local_private(自有私有軌永不公開);另 `chk_itext_source_type`(禁 `ai_generated`)、`chk_itext_access_scope`(public/local_private)兩道互補閘(DB 實查)。`corpus.py:17` `LICENSE_WHITELIST` 是 Python 複本、須與 DB CHECK 同步(`:13-14` 明文警語)。
- **source-pure fail-closed 源閘**:acquire 對非 active 源 `sys.exit`(`acquire_knowledge.py:336`);promote 用 `NOT EXISTS` 排除 registry 中 `approval_status<>'active'` 之 staging(`:200-202`)——憲章 v1.41.0。
- **審批升級唯人 TTY**:`curation.TRANSITIONS` 升級動作(approve/activate/resume/reopen)∈ `HUMAN_ONLY`(`curation.py:30`),`cli_identity` 要求 `sys.stdin.isatty()`(`:44`),AI/管道呼叫被拒;`system=True` 僅得降級(`:62-63`)。
- **fulltext 誠實終態帳**:`knowledge_fulltext_status.status` CHECK 限 6 值(skip_no_oa/skip_license/skip_pdf/skip_ctype/skip_short/skip_fetch_error);live 已有 16,550 件 blocked 終態(skip_no_oa 11,184 + skip_license 3,274 + skip_pdf 976 + skip_fetch_error 913 + skip_short 186 + skip_ctype 17,DB 實查)。
- **跨源去重**:partial unique index `uq_item_extid(entity_type,external_id) WHERE external_id NOT NULL` + `uq_item_title(entity_type,md5(title),COALESCE(year,0)) WHERE external_id NULL`(`harvest_knowledge.py:73-76`)。
- **切句可切回原文 + 三端同閘**:`char_start/char_end` 使 `content[s:e]==sentence`;`corpus.clean_work_sql` 由 builder/embed/retrieval 三端共用同一 SQL 片段、禁 inline 複本(#12)。
- **隔離不變式(AST 靜態閘)**:`augur.knowledge` ∈ `FORBIDDEN` 前綴(`import_isolation.py:33`),預測 7 package AST-walk 零 import(`:90`);RBAC resolver 對位須住 knowledge 不得置 core(`:112`)。實跑 `python3 -m augur.audit.import_isolation` exit 0、零違規。
- **治理規模(DB 實查)**:`knowledge_source` = 3,528 proposed / 69 active / 3 approved / 1 suspended;審批唯人 TTY 閘落地。

### 陷阱(真兆/假兆判讀)

- **最大陷阱——「491 件公版全文/47 萬句」對本機 DB 是假兆**:計畫報告 §4 與 commit c008b5c 宣稱「491 件公版全文/47 萬句落地(IA 488+FRASER 2+SEC 1)」**在本機 live DB 無法復現**:`source_type='pd_fetch'` = 0 件、無任何 `knowledge_source.adapter_config` 含 `fulltext` 鍵(IA/SEC 之 adapter_config 為 NULL、FRASER 僅有 auth_header)、`item_text` 之 source_url 分桶 archive.org/fraser/sec.gov 皆 0(DB 實查;對比 `reports/knowledge_fulltext_source_resolvers_plan_20260712.md:65`)。成因=**DB 跨機獨立不隨 git**(記憶 db-cross-machine-independent):解析器 CODE 已 commit 進 repo,但 `adapter_config.fulltext` 的 UPDATE 資料列+491 件落地資料是在別台機器執行,本 WSL2 DB 是不含該資料的 restore。此三者(全文段、49 萬句、fulltext 策略設定)於現庫完全不存在,**不可引為本機事實**。
- **承上——本機解析器實際無法落地任何 IA 全文**:因 `adapter_config.fulltext` 缺,`fetch_pd_fulltext` 對 IA 走無策略回退=直鏈 `knowledge_item.url`(=`archive.org/details/` 詳情頁 HTML)→ mode='text' 但 ctype=text/html → skip_ctype。要生效須先把 `adapter_config.fulltext` 策略 UPDATE 進 DB。
- **本機 DB 真正主體是 owned_local ERP 私有語料**:`knowledge_item_text` 中 owned_local/local_private = 150,685 段 / 141,825 件(=entity_type `document` 全部、佔 item_text 99.75%),遠大於公開全文(OA cc-by 330 + cc-by-sa 18 + public_domain 4 ≈ 352 distinct item,DB 實查)。注意 `erp_extract` 這個 source_type **非** `acquire_local_files.py` 產出(該支寫 `local_upload`、owned_local 硬配 local_private 於 `:63-65`),來自另一支未在本範圍檔中的批次載入。此大型私有部署在 07-10 v3 報告完全未見。
- **PDF 抽取僅 P0 拍板、P1-P3 未實作**:`src/augur/knowledge/pdf_text.py` 不存在、`knowledge_fulltext_status` CHECK 未擴 skip_pdf_no_textlayer/skip_pdf_quality;`skip_pdf` 積壓 976 件仍卡誠實停(OAPEN 61 本亦然)。pypdf 雖已在 pyproject[admin],抽取模組未建。
- **timer 鏈不抓公版全文**:`refresh_knowledge_pipeline.py` 自動鏈只用 `fetch_oa_fulltext`(OA 路),完全不呼叫 `fetch_pd_fulltext`(grep 0 次);公版解析器是獨立手動/批次跑,易誤以為 timer 會自動抓公版全文。
- **知識 API 無內建 rate limit**:acquire 整個 run 是單一交易且對這些知識 API 無 FinMind 式三層防護;限速靠 `pace_seconds` 住 DB + harvest 層 `pace()`;adapter 中途例外→整批 rollback。
- **promote 對未註冊源 fail-open**:fail-closed 源閘只擋「在 registry 且非 active」者;若 staging 的 source_key 根本不在 `knowledge_source`(如 local_upload source_key=NULL),`NOT EXISTS` 通過=放行——屬設計預期(本機檔非外部源)但語意上是對未註冊源 fail-open,須知悉。
- **切句准入閘僅作用 philosophy 側**:`clean_work_sql` 的 review_flag/非 literary 排除只作用於哲學側;items 側 214,671 句無此過濾(item_text 無 work 歸屬),受 `clean_item_sql` 的 access_scope=local_private + owner 收窄擋外流。`corpus.py` docstring 仍寫「四值白名單」但 `LICENSE_WHITELIST` 已 5 值(含 owned_local),屬 in-code docstring stale。

### 語意橋:欄位↔know-how + 語料統計軌(K 計畫 K1/K2)

這條「語意橋」回答一個治權難題:知識層(哲學原典+投資 know-how 語料)如何在「零量化污染」前提下與資料層(dataset_catalog 登錄 95 表/已落地 84 表、754 欄 raw data)對話。做法是把 raw 欄位的**名稱文字**(column_name/中文名/髒值註/表註/特徵名)經 textnorm 斷詞成詞,再去 know-how 語料的詞共現統計軌查「這個欄位名稱詞,跟哪些 know-how 詞在語料句子中常一起出現」,物化成 `field_knowhow_lexical_affinity`。**經對抗審查逼出的誠實定義**:橋上係數是「欄位名稱詞」與 know-how 詞的**詞面共現(lexical affinity)**——絕不是「該欄實際數值與投資報酬的統計相關」,**raw 數值從不進入計算**。它不屬 knowledge/philosophy/embedding 任一支,是把「量化欄位定義」與「投資智慧語料」用純確定性 SQL 統計接起的承重接縫,供 advisor 當「解讀素材」用、**永不當特徵**。

**三層資料流**:① 上游逐字層——`build_concordance.py`(T4:knowledge_sentence→textnorm→`knowledge_concordance` 16-hash-分區 postings)+ `build_lexicon.py`(T2:六源公版辭書逐字→`knowledge_lexicon` 定義);② 統計軌——哲學側 `build_cross_school_stats.py`(全鏈,帶 corpus='philosophy')+ items 側 `build_items_knowhow_stats.py`(獨立算 npmi/jaccard);③ 橋層——`build_field_knowledge_bridge.py` 把欄位詞 JOIN 統計軌**只做 JOIN、零新事實**(method='join_field_lexical_affinity' 屬 sql_join)。

- **field_term_map 建法**(`build_field_knowledge_bridge.py:36-62`):對 `column_catalog` 三欄(column_name→en、column_name_zh/dirty_value_note→zh)、`dataset_catalog`(table_name_zh/notes→偽欄 `_dataset_`)、`feature_values`(distinct feature 名 `_`→空白→en)各 textnorm.tokenize 斷詞,一詞一列標 source_field;DELETE 全表後重灌(冪等),PK=(dataset,column_name,term,source_field)。實測 5,972 列覆蓋 884 對象=754 欄 + 35 特徵 + 95 表(zh 5,108 / en 864,五種 source_field,DB 實查)。
- **橋上係數物化**(`:65-83`):field_term_map JOIN `knowledge_term_affinity`(a.term_a=f.term OR a.term_b=f.term)取對端當 knowhow_term,JOIN `knowledge_term_cooccurrence` 取 pair 的 cooc_sents,`DISTINCT ON(dataset,column,knowhow_term,stat_key,corpus) ORDER BY stat_value DESC` 每組留最高;`WHERE c.cooc_sents>=30` 擋稀疏假係數;philosophy+items 雙語料同時物化。實測 `field_knowhow_lexical_affinity` 59,706 列(philosophy 746 欄有 npmi/jaccard/llr;items 36 欄只有 npmi/jaccard,DB 實查)。
- **items 側獨立分母**(`build_items_knowhow_stats.py:34-108`,#15 anti-leakage 靈魂):對 items CLEAN 語料(domain∈三投資域 AND access_scope∈public/local_private)∩concordance∩stat_vocab 得 postings,算 corpus_stats/term×item tf/句級共現/npmi/jaccard;`basis_n=N=items CLEAN 句數(10,848)`,**絕不沿用哲學分母**(en 1,505,700 / zh 33,319,三值互異,DB 實查)。
- **corpus 判別欄 + PK 重建**(`migrate_knowhow_bridge_ddl.py:66-75`):三統計表 ALTER ADD COLUMN corpus DEFAULT 'philosophy' 後 DROP/ADD PRIMARY KEY 把 corpus 併入 PK(philosophy/items 分治、互不覆寫),`_pk_has_corpus()` 冪等。此步動 6.5M 列 ACCESS EXCLUSIVE,計畫規定 #30 dump 後執行。實測 `knowledge_term_affinity` = items/en 119,764 + philosophy/en 2,804,226 + philosophy/zh 152,928。
- **兩道最小分母閘**:統計軌內部 `min_cooc=5`(操作值,`build_items_knowhow_stats.py:23`);橋層 `cooc_sents>=30` 硬 CHECK(`build_field_knowledge_bridge.py:24` MIN_COOC_BRIDGE、DDL `migrate_knowhow_bridge_ddl.py:50`,schema 為 SSOT)——橋層遠嚴於內部。`method_kind` CHECK 四值封閉(counting/closed_form_stat/string_rule/sql_join,`build_cross_school_stats.py:68`)DB 硬擋 embedding/LLM 冒充係數,四新 method_key 已 seed 使橋表 FK 不失敗。
- **隔離機械鎖=字面掃描**(`import_isolation.py:48,175`):因橋表恰是「每欄一係數」形狀=最貼近特徵表的旁路面、AST import 稽核看不到 raw SQL,故 `BRIDGE_LITERALS=('field_term_map','field_knowhow_lexical_affinity','knowledge_item_term_stats')` 納入字面掃描,禁預測 7 package + core 以字串拼 SQL「SELECT stat_value 當特徵」;`tests/test_philosophy_isolation.py:118` 紅測反斷言。
- **advisor 消費端 + 免責硬綁**(`advise.py:80-122`):問句命中欄位/特徵名→`_bridge_links` 查橋(唯讀、例外沉默略過)→`_bridge_block`(`:120-122`)把數值包在硬綁免責塊「詞面共現、非該欄資料數值與報酬之相關;不得複述本段數值、不得當交易依據」,items 優先(ORDER BY corpus='items' DESC)。生產語意層唯一消費端(`verify_knowledge_e2e_smoke.py` 亦 SELECT 但僅健檢、非語意輸出)。

**橋層獨有陷阱**:
- **跨語料互刪隱患(活)**:`build_cross_school_stats.py:633` phase_affinity DELETE `WHERE language=%s` 只帶 language 未帶 corpus,而同檔 phase_vocab(`:404`)DELETE 有帶 `AND corpus='philosophy'`。重跑哲學 `--phase affinity`(或 all)會連 items affinity(現況 items/en 119,764 列)一起刪除、只重灌 philosophy;items 須再跑 `build_items_knowhow_stats.py` 復原。計畫 §7 M3 承諾「builder DELETE 全帶 corpus」,line 633 是漏網未落實——屬活隱患(現況「可被誤刪」非已刪)。
- **物化快照 stale**:items `basis_n=10,848` 是建置當時句數,但 live CLEAN items 已 10,855(背景 harvest 又進 7 句);橋是物化非 view,須重跑兩支 builder 才反映。textnorm 是 stem 級比對(Porter),items 頂詞出現 `manag`(management 詞幹)、`10`、`2`(數字)。items 側僅 en 語料(zh CLEAN=0)、只算 npmi/jaccard 無 llr、只覆蓋 36 欄,屬計畫誠實里程碑之語料限制非 bug。
- **易混淆同名件**:`build_field_lens_map.py` 是完全不同的舊橋(doctrine 硬編規則把 NUMERIC 欄映射三鏡頭量/形/位、無 know-how 詞無語料係數),勿與 field_term_map 混淆;`backfill_knowhow_pipeline.py` 是退役墓碑 stub(exit 2 錯得大聲)、`backfill_semantic_bound.py` 屬 deliberation 引擎(回填 deliberation_claim),二者皆非 K 計畫語意橋(因命名誤入)。

### 07-10(v3)之後的變化

- **fetch_pd_fulltext.py 重寫**:從「只抓直鏈 text/plain」升為「源專屬解析器 dispatcher」(3 策略住 adapter_config、code 只加 dispatcher)——commit c008b5c(07-13);v3 無此。**但落地資料(491 件/49 萬句/adapter_config.fulltext 策略)不在本機 DB**(見上陷阱)。
- **兩份新計畫書**:`knowledge_fulltext_source_resolvers_plan`(07-12,已執行 CODE)與 `knowledge_pdf_extraction_plan`(07-12,P0 拍板未實作)填補全文最後一塊缺口(PDF/OAPEN 976+61 件)規劃。
- **FRASER key plumbing**:acquire `fill()` 增 `{fraser_api_key}` env 代換(key 不落 DB)、auth_header 走 header(commit f8e47aa)。
- **本機 live DB 主體位移**:從 v3 的哲學+論文 metadata,擴為以 141,825 件 owned_local ERP 私有 document 為主的大型語料(150,685 段 item_text);此私有部署 v3 未見。
- **句/嵌入規模落地**:`knowledge_sentence` 1,756,817 句、`knowledge_sentence_embedding` 1,696,984 列(e5-small);v3 時切句/嵌入鏈剛接通、規模未達此。
- **整個 K1/K2 語意橋子系統 v3 之後全新建**(v3 對 field_knowhow/lexical_affinity/K 計畫零命中;計畫定稿 07-12 5005f10 / code 落地 07-13 80dd1f3):新增 `field_term_map` 5,972 + `field_knowhow_lexical_affinity` 59,706 + `knowledge_item_term_stats` 30,443;三統計表加 corpus 判別欄+PK 重建;items 統計軌首次落地(corpus_stats 5,146 / cooccurrence 29,941 / affinity 119,764);隔離擴 BRIDGE_LITERALS + advisor 橋接線與免責硬綁。
- **來源治理狀態機**(`curation.py`,憲章 v1.41.0)+ `knowledge_source` 膨脹到 3,528 proposed / 69 active,審批唯人 TTY 閘落地。

## §4.2 philosophy 素養層：原典/思想家/版權合規路/隔離

**這層在做什麼（白話）**：把人類投資大師與哲學家的智慧——**限真實權威文獻、非 AI 生成**——結構化為兩種東西：(1)「**可證偽的因子假說**」：投資學派 → 原則 → augur 特徵 → 預期 IC 方向（direction），供 feature 層當理論來源、validate 後當顧問可解釋性素材；(2)「**逐字可溯源的原典全文語料庫**」（公版古典）＋思想家/著作 metadata，供顧問「引經據典」的語義檢索。最高 WHY 一句話：**哲學是「假說、非真兆」——大師說了不算，要 augur 自己過四道漏斗＋經濟價值 #14 實證活下來才算數**；且此層對量化「零加權」，以機械閘（AST＋DB CHECK）硬綁「絕不進預測管線」。

### 怎麼建的（機制為主）

**假說 vs 實證刻進資料型別本身**。`principle_factor_map` 的 `direction SMALLINT NOT NULL` 是**文獻預期 IC 方向（假說）**、`validated_ic DOUBLE PRECISION` / `validated_econ TEXT` 可 NULL、由 augur 自身回填（`framework.py:37-42`）；`philosophy_principle.status` 預設 `'untested'`（`framework.py:33`）。哲學不加權、經濟價值 #14 是唯一裁決——這把「驗證活下來、非大師說了算」寫進了欄位定義，不靠註解宣示。

**策展資料以 in-code literals 承載，走 #29b「傳輸工件」特例路**。23 個投資學派（`SEED`, `framework.py:93`）、17 位核心思想家＋著作（`THINKERS`, `framework.py:311`）寫死在 Python，明文自陳為「principle→factor 映射本質是 code」的哲學層特例（與 #29「repo 檔＝另一種 hardcode」有張力，docstring 承認）。`build()`（`framework.py:259`）/ `build_people()`（`framework.py:372`）全用**冪等 upsert（ON CONFLICT DO UPDATE / SELECT-then-INSERT），刻意 NEVER blanket DELETE**——理由寫死在 docstring（`framework.py:262-263, :376-377`）：下游 FK 已掛他管線列（`stock_philosophy_tag` / `school_thinker` / promote_knowledge 寫的 `philosophy_source`、factor_map 的 `validated_ic` 回填），blanket DELETE 會誤清或撞 NO ACTION FK 中止。**關鍵設計**：既有 principle 只 `UPDATE ... SET hypothesis`（`framework.py:287`）不動 status、既有 factor_map 只 `UPDATE ... SET direction`（`framework.py:299`）不動 `validated_ic/econ`——所以 seed 重放時 augur 的實證回填**存活**。

**版權雙軌合規路**（憲章「全文准入三軌」的落地）：
- **Track-1 公版全文**：`fetch_public_domain_classics.py`（維基文庫中文戰略/哲學古典，道德經/武經七書/三十六計等 8 部）＋ `fetch_gutenberg_classics.py`（Gutenberg 英文哲學/投資經典 50 書）以**本地 urllib 下載 raw ＋純 regex 解析**（`fetch_public_domain_classics.py:66-124` fetch_raw/clean/parse_body、`fetch_gutenberg_classics.py:137-174` strip_gutenberg/split_chapters），**零 LLM、逐字無摘要改寫**，落 `philosophy_work_text`（`license` 硬寫 `'public_domain'`，`fetch_gutenberg_classics.py:227-228`），再切句/嵌入/檢索。
- **Track-2 版權現代著作**：`seed_thinker_works_dbpedia.py` 只抓「**書目 metadata**」（title/year，`note` 明標「書目 metadata、DBpedia notableWork、全文版權/未抓」，`seed_thinker_works_dbpedia.py:73-74`），**絕不抓全文**（全檔無 `philosophy_work_text` 寫入）；其「核心精神」僅經 `principle→factor_map→#14` 抽象成可量化因子假說由 augur 獨立驗證入庫（`framework.py:171-194` 的 quality_qmj/piotroski/peg/macro_cycle SEED），不複製任何受版權文字。

**檢索層 `retrieval.py` 走「零向量優先、逐字可溯源、fail-closed RBAC」**。`retrieve()`（`retrieval.py:64`）works 側 e5-small pgvector cosine kNN，未登入 `scope=None` 直接回 `[]`（`retrieval.py:68-69`），一律過 `corpus.clean_work_sql` 閘；`retrieve_items()` items 側**先 exact concordance 計數、只在不足且真有嵌入時才載模型跑 ANN 補位**（#28 本地零 usage）；`retrieve_all()` 三路徑（登入者公開 works / domain 收窄 public items / 擁有者收窄 local_private items）交錯合併、cap k、None→全 deny。

**思想家骨架靠實證來源擴充、非 AI 窮舉**：`seed_wikidata_philosophers.py`（按 sitelinks 知名度抓 occupation=philosopher）、`seed_dbpedia_philosophers.py`（WDQS outage 替代）、`seed_thinker_works_dbpedia.py`（補書目）；in-code 硬編清單（`seed_world_philosophers.py` 141 位）明文標為 #29b 傳輸工件——一次性 seed 載體、**預設無參數只印指令矩陣不執行**（`seed_world_philosophers.py:145-147`），內容已落庫、SSOT 是 DB。

### 機械閘與不變式

| 不變式 | 機械閘（enforced_where） | 親驗結果 |
|---|---|---|
| **禁 AI 生成入庫** | DB 層雙 CHECK：`philosophy_source.source_type<>'ai_generated'`（`framework.py:48`）＋`philosophy_work.work_type<>'ai_generated'`（`framework.py:82`） | live `pg_constraint` 兩條皆存在（CONFIRMED） |
| **原典全文限公版** | DB 等值 CHECK：`philosophy_work_text.license='public_domain'` | live 全庫 work_text 唯一值 public_domain、31782 列、count(DISTINCT license)=1（CONFIRMED） |
| **素養層絕不進預測管線** | AST 靜態閘 `import_isolation._import_violations()`：預測 7 package 任一 import `augur.philosophy/advisor/knowledge`＝違規 | `python3 -m augur.audit.import_isolation` EXIT 0（CONFIRMED） |
| **檢索逐字他證** | 型別分派 `verify_verbatim`（`retrieval.py:110-124`）：work Citation→`text in row[0]` 子字串；ItemCitation→`verify_verbatim_item`（`retrieval.py:377-383`）`substring(content FROM char_start+1)==text` 位置+內容雙驗；AttachedCitation→附檔全文子字串 | 三側分派齊備（CONFIRMED） |
| **檢索 RBAC fail-closed** | `retrieve` scope=None→`[]`（`retrieval.py:68-69`）；`retrieve_all` `not scope`→`(False,frozenset(),None)` 全 deny（`retrieval.py:357-358`）；`clean_work_sql`＝`review_flag=false AND corpus_class='literary'`（`corpus.py:35`，NULL 不放行） | 三路徑全 deny（CONFIRMED） |
| **冪等 NEVER blanket DELETE** | `build()`（`framework.py:266-306`）無 DELETE 語句、只 upsert；隔離對位由 `test_philosophy_isolation.py` 常備測試守 | resolver 住 knowledge、chat_history 住 advisor（CONFIRMED） |

`PIPELINE` 恰 7 package（`import_isolation.py:31`）、`FORBIDDEN` 3 前綴（`import_isolation.py:33`）。隔離不變式的**邏輯 SSOT 住 `augur.audit.import_isolation`**（`test_philosophy_isolation.py` 只是薄殼委派）；`check_isolation()` 涵蓋 (a) AST-walk import 違規、(b) 字面旁路掃描（RBAC/chat/distill/bridge 被字串拼 SQL 觸及）、(c) 對位檢查（resolver/chat_history 誤置 core）、(d) scripts 洩漏面。philosophy 層只**單向讀**預測輸出（`verify_philosophy_factors.py` 讀 feature_values 做驗證），反向零依賴。

**corpus 治理三態（evolved beyond framework DDL）**：`philosophy_work` 後續加了 `review_flag/review_reason/reviewed_by/reviewed_at/corpus_class`（原 `framework.py` DDL 無此欄），`corpus_class IN(literary,reference)`——**reference 語料只走 lexicon 路、不進切句/嵌入/檢索**（`corpus.py:32-34`）。對比知識層 item 走 `corpus.LICENSE_WHITELIST` 五軌（`public_domain/cc-by/cc-by-sa/cc0/owned_local`，`corpus.py:17`），原典全文只允許 `public_domain` 單軌，更嚴。

**bridge 表紅測 fail-closed 自檢**：`test_philosophy_isolation.py:114-120` 植入含 `SELECT stat_value FROM field_knowhow_lexical_affinity` 的暫存檔，斷言掃描器**必抓到**，否則判「閘是假的」——把「閘有沒有真的在守」也做成可跑測試。

### 陷阱

- **`framework.py:254` bootstrap docstring 稱「建 6 表」但 DDL 實為 9 表**（stale，v3 已標，至今未修）。
- **live `philosophy_school` 有 44 學派，但 `SEED` 只定義 23 投資學派**：額外 21 為無 principles 的組織/管理理論學派（Carnegie School / Institutional Theory / Disruptive Innovation / Resource-Based View…），grep 遍 `scripts/ src/ data/` 零命中程式字面——係經 knowledge 資料管線（`promote_knowledge.py:111` INSERT INTO philosophy_school）入庫（data-in-DB、非 code），把 philosophy_school 從「投資」擴成一般管理學說語料骨架。
- **`principle_factor_map.feature` 是裸 `VARCHAR(255)` 無 FK**：待建特徵（roe/debt_ratio/piotroski_fscore/peg_ratio/macro_regime）照樣 INSERT 假說，但無可算特徵 → `validated_ic` 恆 NULL；**假說可先於實作登錄**（`framework.py:175-192` SEED 標「待建」）。
- **`concordance_lookup`（`retrieval.py:190`）回 knowledge_item 逐字內容但不過 `clean_item_sql` 的 domain/擁有者收窄**：目前未接進 `advise()`/`retrieve_all` 故非現行洩漏面，但 docstring 警告若未來接顧問讀取路徑而未先補 RBAC 閘，會繞過收窄洩漏 `local_private`。
- **禁 AI 生成的 DB CHECK 只擋 type 欄字面 `='ai_generated'`、不做語義偵測**：思想家 `bio` 欄在 `seed_world_philosophers.py`/`fetch_*` 明文自陳源自「AI 記憶整理、待 DBpedia/Wikidata 覆核」（source_type 設 book 即過 CHECK）——故 **bio metadata 是較軟的誠實邊界**（傳輸工件、預設不執行、待覆核），與原典全文「逐字無改寫」的硬保證不同層級；live 4135 thinker 中多數 bio 為空、birth_year NULL（harvest 稀疏、誠實留空不杜撰）。
- **`assert access_scope in (...)` 作安全驗證**（`corpus.py:55`）：`python -O` 下 assert 被剝除，但呼叫端皆傳封閉集內值、風險低（詳見 knowledge 層）。

### 07-10（v3）之後的變化

- **【最大實質修正】v3「validated_ic/econ 全 NULL、status 全 untested」半錯**。v3 該判斷係讀 `framework.py`（build 不寫 validated_ic）推論、**未查 DB**。live 實測 `principle_factor_map` 42 筆有 **37 筆 `validated_ic` NOT NULL**（由 `verify_philosophy_factors.py` 回填真實 as-of rank IC ＋ portfolio Sharpe），5 筆 NULL 恰為尚未建的特徵（debt_ratio/macro_regime/peg_ratio/piotroski_fscore/roe，`SELECT DISTINCT feature FROM feature_values WHERE feature IN(這5個)` 回空集，CONFIRMED）。**v3 的「全 NULL」應更正為「可算的真實特徵已全數回填，只剩 5 個未建特徵 NULL」**——回填機制 `verify_philosophy_factors.py:35-38`「若 feature not in augur_feats → UPDATE validated_ic=NULL」。
- **但 `philosophy_principle.status` 未同步**：validated_ic 已回填、principle.status **live 仍 26/26 全 `'untested'`**（map 層實證與 principle 層狀態不一致；回填只動 factor_map、沒翻 principle.status，`build()` 從不寫 status）——顧問若讀 status 會**低估已驗證程度**。
- **thinker/work 規模成長**：任務原假設「861 thinker」（源自 07-02 commit 訊息），live 已達 **4135 thinker / 1536 work**（wikidata/dbpedia harvest 續跑），其中 695 位有 work、618 部有全文。（未親驗逐值，取材料 harvest 帳）
- **`retrieval.py` 於 commit 9b32a8b（07-10）大改**：`retrieve_items` 加 Qdrant 外部索引 factory 路（v1.40.0 接縫 DB 化）＋ pgvector 自動降級（D6 fallback）；`retrieve_all` 落地三路徑 RBAC（登入者公開 works / domain 收窄 public items / 擁有者收窄 local_private items）。
- **`import_isolation.py` 隔離面擴充**：新增 `DELIB_LITERALS`（審議引擎工作帳＝行為樣本非真兆，`import_isolation.py:44`）與 `BRIDGE_LITERALS`（K 計畫 R5 語意橋表 `field_knowhow_lexical_affinity` 等「每欄一係數」＝最貼近特徵表的旁路面，`import_isolation.py:48`）掃描；`test_philosophy_isolation.py` 於 commit 80dd1f3（07-12）新增 `test_pipeline_and_core_have_no_bridge_table_reference` 附 fail-closed 紅測。
- **corpus 治理欄位落地**：`philosophy_work` 已加 `review_flag/corpus_class` 等（原 DDL 無），`clean_work_sql` 閘升級為 `review_flag=false AND corpus_class='literary'`（fail-closed）；live 1536 work 中約 1160 過 CLEAN 閘可檢索、151 被 review_flag=true 擋、少數 reference 只走 lexicon。（count 取材料 harvest 帳，未逐值親驗）
- **`stock_philosophy_tag` 至今未變**：DDL 建好（`framework.py:50-56`，含 as_of #8 欄）但 live count=0、全 repo 零 writer（`grep INSERT INTO stock_philosophy_tag` 零命中，CONFIRMED）——橫斷面哲學標籤仍未實作。

## §4.3 嵌入/向量/檢索：e5-small 口徑 / pgvector 生產 / HNSW

**▶ 一句話**：把知識語料（逐字定義 lexicon、原典/文獻句 sentence、段落 chunk）用**單一** CPU 嵌入模型 `intfloat/multilingual-e5-small`（384 維、cosine）投影成向量，**pgvector 是唯一真相（SSOT）**、HNSW 供顧問層 L2 檢索「引經據典」；外部向量庫（Qdrant/Milvus）是可隨時 DROP 從 pgvector 重建的影子索引。核心紅線：**嵌入＝索引不是內容**（命門7/紅線③）——search 只回 `(pk, distance)`，內容永遠回 PG JOIN 取逐字原文。此子系統為哲學/知識素養層基建，與預測管線物理隔離、零量化價值、絕不進 feature（憲章 v1.17.0）。

### 這層在做什麼

三粒度分工、各一張 pgvector 表：`knowledge_lexicon_embedding`（定義級，154,875 筆全嵌）、`knowledge_sentence_embedding`（句級，works|items × zh|en 四側共 1,696,984 筆）、`philosophy_chunk_embedding`（段落級，126,609 筆），全用單一 `model_tag=intfloat/multilingual-e5-small`、無雜世代（2026-07-13 GROUP BY model_tag 三表各僅回單一 tag）。句級四側現量：works_en 1,455,960 / works_zh 33,314 / items_zh 147,196 / items_en 60,514（和＝1,696,984）。嵌入完的向量供顧問層 `advise()` 做語義 kNN，回逐字可溯源引文。

### 怎麼建的（機制與為什麼）

**(1) e5 非對稱前綴口徑＝全系統釘死的機械契約**。e5 系模型要求問答不對稱前綴：嵌庫端一律加 `passage: `（`embed_knowledge.py:34` `PASSAGE_PREFIX`；lexicon 於 `fetch_batch:111` 先組成 `passage: 詞: 定義`、sentence 於主迴圈 `:198` 未帶前綴則補；`embed_philosophy_chunks.py:57`），查詢端一律加 `query: `（`retrieval.py:60` `_query_vec` 唯一入口，`retrieve`/`retrieve_items` 皆走它）；兩端都 `normalize_embeddings=True`（單位向量→cosine，`embed_knowledge.py:200`）。pgvector HNSW 用 `vector_cosine_ops`（`embed_knowledge.py:167-168` lex/sent、`embed_philosophy_chunks.py:68-69` chunk）。**這是本子系統最易被誤植的口徑**——忘了任一端檢索品質就崩。

**(2) 嵌入世代命名收斂單一 SSOT `embedspec.py`**。三元組 `(MODEL_TAG, dim, TEXTNORM_VER=1)` 加全部衍生命名（確定性 slug、collection 名、同步鍵）只住這裡；S5 嵌入/S6 serving/S7 檢索三端 import 同一份，換模＝只改這裡（SOP-A）、collection 名自動換世代不覆蓋舊世代。`model_slug`（`embedspec.py:35-42`）是純函數（token 首字縮寫≤5 + sha1 前 6 碼），`intfloat/multilingual-e5-small` 算出 `ime5s30b1cd`，由 `test_knowledge_embedspec.py:17` pin 成字面常數逼有意識同步（slug 非字面常數而是確定性計算值、由 test pin，語意上等同釘死）；sentence_items collection 組出 `kn_sent_it_ime5s30b1cd_tn1`。命名長度預算貼地零餘裕：collection≤26、sync_scope≤32，超長/非封閉集 `ValueError` fail-loud（`embedspec.py:45-64`）——英文題名或多字元語言碼（如 `zh-hant`）即 fail，是設計硬邊界不是 bug。

**(3) 增量游標 + 冪等 resume + 排除帳落庫**。`embed_knowledge.py` 主迴圈：讀 `knowledge_build_meta.cursor_sent_id`（`:189`）→ encode + `INSERT ... ON CONFLICT DO NOTHING`（`:200-206`）→ 再推游標（`:207-209`）＝**先寫向量再推游標，永不超前資料**。works 側游標繼承 legacy `embed_sentence_{lang}`（機器遷移非手撥，`ensure_scope:96-99`；DB 實證 `embed_sentence_zh`=1,514,500 與 `embed_sentence_works_zh`=1,514,500 一致）。排除/處理帳寫 `knowledge_embed_ledger` 而非 stdout。junk 過濾分語言：zh 只剔純符號（短句「翕,盛貌。」是真訓詁不得剔）、en 剔長度<10 或>1000。

**(4) 外部索引封成五方法抽象、後端 DB 化 factory**（v1.40.0）。`vectorindex.py` 的 `VectorIndex` 基類→`MilvusLiteIndex`/`QdrantIndex`，`search` 只回 `(pk, distance)`（`:42-49`）；payload 只帶窄 scalar（domain/entity_type/taxonomy_id/language）、partition/filter key=language。後端選擇 DB 化：`make_index` 讀 `knowledge_vectorstore_config` 選 backend，並機械斷言 `config.embed_model/dims == embedspec 現行世代`，不一致 `raise RuntimeError` 拒服務（`vectorindex.py:332-334`，防混世代索引污染檢索）。切後端＝admin `UPDATE` 一列、零改碼（CLAUDE #29b）。

**(5) cutover 走影子評測機械門檻**。`export_qdrant_index.py` 把 CLEAN 過閘句匯到 Qdrant（雙向 anti-join 對帳：missing→補、orphan→刪、orphan/source>0.5 要求 `--rebuild`、斷言 synced==clean_source 差=0）；`verify_qdrant_shadow.py` 用 50 題確定性題集同打 pgvector 與 Qdrant，量 top-10 重疊、`mean≥0.90` 才允許切 config 一列（`:74` `passed=mean_ov>=threshold`），落 `vectorstore_shadow_eval`。

### CLEAN 准入閘與私有隔離（三端共用 SSOT）

CLEAN 准入閘是切句 S3 / 嵌入 S5 / 檢索 S7 三端**共用**的 `corpus.py` SSOT、禁 inline 複本，全 fail-closed（NULL/未知不放行）。works 側＝`review_flag=false ∧ corpus_class='literary'`（`corpus.py:35`）；items 側 base＝`license∈白名單(5值:public_domain/cc-by/cc-by-sa/cc0/owned_local, corpus.py:17) ∧ entity_type∈{paper,report,document}(corpus.py:22)`。

**⚠ 對 v3-reader 原稱「access_scope 三端共用」的重要修正**：真正三端恆一之閘＝`license ∧ entity_type`；`access_scope` **不是嵌入端閘**——嵌入端（S5）`embed_knowledge.py:113` 傳 `is_super=True` 且不傳 access_scope＝**不濾**，故私有內容照嵌進 pgvector。`access_scope` 只在**讀取/匯出**端收窄（retrieval public/local_private、export public）。實證：items_en 中通過 `license∧entity_type` 者按 access_scope 拆為 public 55,861 + local_private 4,653＝60,514——即 **4,653 筆私有嵌入確實住在 pgvector**，但 `export_qdrant_index.py:67` 匯出前以 `clean_item_sql(access_scope='public')` 擋掉、**私有永不外流至外部影子索引**（憲章 v1.36.0 owned_local⇒local_private）。`qdrant_sync_state` 快照 `kn_sent_it..._en`：`n_source_total=60,507 / n_source_clean=55,854 / n_synced=55,854`、note withheld=4,653。

### 機械閘與不變式

- **未登記模型 `dim_for` → KeyError fail-closed**（不猜維度、不建錯維 collection）：`embedspec.py:28-32`，`test_knowledge_embedspec.py:46-50`。
- **換模但表仍單欄 PK 且既有 tag≠新 tag → `sys.exit`**（防 DO NOTHING 靜默零寫入假成功，SOP-A/P6）：`embed_knowledge.py:resolve_write_target`。
- **表維度 atttypmod≠模型維度 → `sys.exit`**（異維＝新表世代）：`embed_knowledge.py:check_dim`；adapter 端 `_assert_dim` 亦 raise（`vectorindex.py`）。
- **ZERO_INSERT_SUSPECT**：`done>0 ∧ kept_total>0 ∧ inserted==0` → 落帳 note 後 `sys.exit`（SOP-A③ 防換模未遷 PK 的靜默假成功）：`embed_knowledge.py:214-224`。
- **`make_index` 世代機械斷言**：config.embed_model/dims 必須==embedspec 現行世代，否則 `raise RuntimeError` fail-loud：`vectorindex.py:332-334`。
- **search 只回 `(pg_pk, distance)` 永不回內容**（紅線③）；內容一律回 PG JOIN 且過 CLEAN+RBAC（外部 id 過不了 cfrag 即被丟＝零洩漏面）：`vectorindex.py:42-49`、`retrieval.py:308-334`。
- **filter 欄名封閉集 + 值型別把關 + 禁引號/反斜線**（fail loud 不注入）：`vectorindex.py`。
- **export 對帳 `synced−clean_source` 差≠0 → `sys.exit`**（不得宣稱竣工）；orphan/source>0.5 → 要求 `--rebuild`：`export_qdrant_index.py`。
- **影子 cutover 門檻 `mean_overlap≥0.90`（threshold 可調）才 passed**：`verify_qdrant_shadow.py:74`。

**sentence/lexicon 嵌入表已走 P6 複合主鍵** `(sent_id/lex_id, model_tag)`（同一句可並存多模型世代、換模重嵌不被 `ON CONFLICT DO NOTHING` 靜默吞掉）；`philosophy_chunk_embedding` 是較早世代仍單欄 `chunk_id`。三表 embedding 皆 `vector(384)`（DB atttypmod=384 實查）。

### 陷阱（gotchas，親驗 CONFIRMED）

- **⚠ make_index 的「fail-loud 拒服務」實際被檢索端吞成「靜默降級」**：`make_index` 世代不一致的 `RuntimeError`（`vectorindex.py:332-334`）在 serve 端被 `retrieval.py:311-315` 的 `except` 捕捉→ print 一行、降級 pgvector 直查、`_idx=None`，**不 raise 不拒服務**。兩子句各自為真，但「fail-loud」僅止於 make_index 內部、不會傳播至檢索回應；外部索引默默失效時檢索悄悄改走 pgvector 而使用者無感，只能靠 log 察覺（`retrieval.py:333-334` qdrant 故障降級同理）。
- **影子 cutover 門檻只閘 mean 不閘 min**：`verify_qdrant_shadow.py:74` `passed=mean_ov>=threshold`；DB 最近通過列（2026-07-12）`mean=0.912 min=0.2 threshold=0.9 passed=t`——單題 pgvector↔Qdrant top-10 可只重疊 2/10 仍算 PASS（HNSW 近似 + `hnsw_ef=256`（`vectorindex.py:217`）固有特性，min 僅記錄不 gate）。
- **`embed_philosophy_chunks.py` docstring stale**：標頭題名寫 `bge-m3 CPU、1024 維`（`:2,:4`），但實際 `MODEL='intfloat/multilingual-e5-small'`、`DIM=384`（`:17-18`，行末註解說明 bge-m3 CPU 53.7h 太久故換 e5-small）；DB 實查 `philosophy_chunk_embedding` model_tag=e5-small、atttypmod=384——**碼與 DB 為準、docstring 為過時殘留**。
- **Qdrant host 的 G3 allowlist 只是文件意圖、未在向量路徑機械強制**：`QdrantIndex.__init__`/`make_index` 只吃 `config.endpoint` 直連（預設 `127.0.0.1:6333`）無 host 斷言；真正 G3 host 焊點只在 `advisor/ollama.py:30` 對 LLM 端點。endpoint 由 admin 控 config 列，本機部署風險低但非 fail-loud。
- **`coverage_metric`（Milvus export 軌）凍結於 2026-07-04 只 2 列**，`qdrant_sync_state`（Qdrant export 軌）才是活帳本（07-12）；Milvus Lite 已降為 eval/S6 軌，別把 `coverage_metric` 當現況。
- **`concordance_lookup` 回逐字內容但不過 `clean_item_sql` 的 domain/擁有者收窄**（`retrieval.py` docstring 明載）；目前未接進 `advise()`/`retrieve_all` 故非現行洩漏面，但若未來接入顧問讀路徑必先加收窄否則繞過 RBAC。
- **R6 量測釘死「絕對分數門檻不可行」**：`measure_finance_retrieval.py` 把「e5-small cosine 0.80-0.88 窄帶與相關性幾乎無關」量成數字，故域精度為唯一有效軸、對策＝域過濾/rerank 或評估換模（SOP-A）。註：「0.80-0.88 窄帶」「52/126,609≈0.04% junk chunk」為 docstring 內既有實證陳述（分母 126,609 本次 DB 驗＝現量，惟 0.80-0.88 與 52 junk 之量測本次未重跑獨立複核，**未親驗**）。

### 07-10（v3）之後的變化

- **Qdrant cutover 已上線**（v3 於 07-10 11:43 撰寫，早於 07-10 20:46 的 cutover commit `9b32a8b`）：v3 仍記「讀取路徑現走 pgvector、遷移未 cutover」；現況 `knowledge_vectorstore_config.sentence_items=qdrant_server`（`http://127.0.0.1:6333`），其餘 scope（`sentence_works`/`lexicon`/`philosophy_chunk`）仍 pgvector。Qdrant 反成 items 側 ANN 生產後端、Milvus 降為 eval 軌。
- **新增 `make_index` config-driven factory + 世代 fail-loud 斷言**（v1.40.0 接縫 DB 化）：`vectorindex.py:325-339`，兩張新表 `knowledge_vectorstore_config` / `vectorstore_shadow_eval` 種子四 scope。
- **新增 `verify_qdrant_shadow.py`（D6 機械守門）與 `export_qdrant_index.py` CLEAN 匯出引擎 + `qdrant_sync_state` 帳本**；`retrieve_items` 加入「外部索引→PG JOIN 取原文、故障降級 pgvector」雙庫路徑。
- **嵌入積壓大幅消化**：HANDOFF 記全文源解析器落地時切 469,551 句待嵌，現 DB 實查未嵌 backlog 僅約 59,833（works_en 52,867 + items_en 6,935 + 零星），句級嵌入總量達 1,696,984。
- **shadow eval 帳累積多次通過**：最近 2026-07-12 `mean=0.912 passed=true`——D6 門檻實跑落地（v3 時尚無此表/評測）。
- **⚠ 影子索引落後 SSOT 7 筆**：`qdrant_sync_state` 快照 items_en `n_synced=55,854`，但 live pgvector 通過 `license∧entity_type∧public` 者為 55,861（多 7 筆公開列）——sentence_items 已 cutover 至 qdrant_server，故現行 serving 較 SSOT 短少此 7 筆，重跑 export 可補齊；withheld(local_private)=4,653 live 與快照相符。

## §4.4 advisor+serving+前台+蒸餾+RBAC+檔位：誠實顧問全鏈

### 這層在做什麼

量化本體算好的真實預測數字（唯讀 payload）＋素養庫逐字公版引文，經**本機** LLM（qwen3）翻成引經據典的白話，交付到瀏覽器對話前台。命題不是「答得多」而是「不說謊」：數字 100% 唯讀轉述 payload、引文 100% 公版逐字、庫外主題與絕對方向題一律**機械拒答**，而非讓弱本機模型自信講錯。三敵防護（假資料／偷看未來／自欺）靠生成後機械 guard 閘落地、不靠 prompt 自律。v1.37.0 後全鏈本機限定，`owned_local` 私有內容永不離機。它是量化半的**唯讀對外門面**：對預測／知識／哲學表全 SELECT 零寫，唯一寫入例外＝自家 `chat_*`（owner 綁）與 `deliberation_*` 審議帳本。

### 怎麼建的（機制為主）

**唯一編排出口 `advise()`（`advise.py:125`）**：全鏈唯一動筆處，漏斗順序寫死於函式體——方向短路 → `retrieve_fn` → `_clean`（`verify_verbatim`＋`is_low_content` 濾 junk）→ `relevant_citations` 相關度過濾 → 英文 fallback 再檢索 → honesty/whitelist gate → `build_prompt` → `llm_fn` → 依 payload 型別分派 guard → picks 確定性注入。`oai_compat`／`serve_advisor_openai` 只翻 OpenAI 協定與起 server，零第二編排器（`oai_compat.py:114` chat_completion 只呼 advise，守 #12）。

**三敵防護＝ 5 條 guard 閘（`guard.py:45-79`）**：①引號內 ≥8 字須逐字 ⊂ 某 citation（`:50-53`）②顯著小數/IC 鄰接數字須 ∈ `payload.numbers()` 白名單（`:56-60`）③無未來/保證語 `_FUTURE_LEAK`（`:62-64`）④逆向不翻轉模型結論 `_REVERSE`（`:66-68`）⑤股名須與 payload 相符（`:72-77`）；另有 `guard_attribution`（`:147-166`，古典出處斷言須 citation 佐證）、`guard_definition`（lexicon 須附 source_locator）。`advise.py:219-224` 依型別分派：`KnowledgePayload → guard_knowledge`（數字雙源＝`payload.numbers() ∪ citation_numbers`、已驗引文段豁免②③），其餘 → `guard()`。`guard.py:4` 自述此為 #1/#8/#15 在對話層唯一可靠落地。

**弱模型能力天花板的結構性繞道（D4b）**：qwen3:8b 實證會幻覺「選哪些股＋股名＋迴圈重複」，故把 picks 從 LLM 手中拿走——`_render_picks_table`（`advise.py:20-49`）純 f-string 從 payload ground truth 排版，於 guard 之後 prepend（`:233-234`，免 guard 因數字皆出 payload），LLM 只負責它做得到的 caveat 白話（`prompt.py:180` 明示「清單已呈現、你不必也不要重列或點名個股」）。同源設計 `strip_quote_marks`（`ollama.py:44`）剝除模型引號框：模型不從事逐字引用（它做不到照抄公版），逐字原文改由系統 citations 提供。

**相關度閘取代 cosine 分數門檻（`relevance.py`）**：e5-small 對 out-of-corpus 硬回 0.80~0.88 窄帶離題高分令 LLM confabulate；改以零 usage 純正則「夠強辨識性專詞共現」判定——`_strong_distinctive`（`:93-95`）剔泛用字與單 CJK 字、只留多字專詞（perovskite/知行合一），全數不相關 → 視同空檢索 → 誠實 decline。`RELEVANCE_FLOOR=0.30`（`:41`）已退為簽章相容、非現行判準（`:139` docstring 自陳；主路徑 `advise.py:171/178` 直呼 `relevant_citations` 不讀 floor）——注意它仍活用於遙測記錄，是「非閘判準」而非嚴格死碼。

**方向題硬拒答且拒答句 DB 驅動（`prompt.py`＋`advise.py`）**：`advise.py:148-150` 對 `_asks_direction_or_path(query)` 短路弱 LLM、直回 `build_direction_refusal()`；句子即時查 `direction_gate` 表組出（門數/判死數不寫死，#29b），DB 例外退回 hardcode 常數 fail-closed（`prompt.py:104-122`）。實測 `direction_gate` 19 門＝10 evaluated_fail＋6 approved＋3 preregistered＋0 evaluated_pass，走「其餘無一評估通過」誠實分支。

**三個 stdlib-only 常駐 server 手刻**（明文避開 Open WebUI 的 HuggingFace crash-loop、無 node/Docker）：`serve_chat_ui`（:8090 同源 proxy＋RBAC 登入前台）→ `serve_advisor_openai`（:8399 OpenAI 相容薄殼）→ 本機 Ollama（:11434）；`serve_admin_console`（:8500 知識控制台）。全綁 `127.0.0.1`、偽 SSE（先 role keepalive chunk、全文過閘後才分塊 emit）以相容 `stream:true` × guard 全文後置閘。

**本機 LLM 限定焊點 G3（`ollama.py:29-38` `_assert_local_host`，v1.37.0）**：建構 `llm_fn` 時斷言「最終組出的 url」（非只 base_url）host ∈ 本機 allowlist（localhost/127.0.0.1/::1＋`OLLAMA_HOST_ALLOWLIST`），違者 fail-loud `RuntimeError` 拒起——env 誤設外部端點＝把 `owned_local` 送出本機，寧拒起不默默外送。三個 `llm_fn` 工廠（`make_llm_fn:157`／`make_structured_llm_fn:105`／`chat_with_stats:76`）皆過此焊點。

### 蒸餾 S2-S5 師生管線（Claude-as-teacher，DP1 usage 護欄）

離線為「誠實顧問」產 SFT 語料的師生蒸餾。核心賭注：Claude 當**行為示範老師**只教「該怎麼誠實地回答」（decline/hedge/據真兆答），**不供事實**；老師答案裡任何事實斷言一律由 S5 用生產 guard 硬驗「⊂ 真實檢索 context」不過即丟——把 guard 從對話送出期**前置到訓練資料生成期**。四步各一支資料驅動 script、逐題 commit 游標 resume：S2 `generate_questions`（三情境＋標籤）→ S3 `build_context`（實跑真兆檢索注入、`target_response` 留空）→ S4 teacher 生 gold → S5 `validate` 過 guard 硬驗、通過寫 jsonl。

- **界線-B「Claude 只教行為、不供事實」做成 DB schema 分欄**：`advisor_distill_context` 把 `context`（jsonb 真實檢索、trace 回 chunk/sent）與 `target_response`（teacher 示範）拆兩欄（`migrate_advisor_distill_ddl.py:49-64`）；S5 再機械驗 target 事實 ⊂ context——**機械保證而非相信 Claude 不編**。實測攔掉 pilot 37.6%（274 gold → 171 pass、103 drop），drop 主因含 `guard_attribution` 捏造出處（teacher 名點莊子/墨子/判斷力批判等卻無 citation 佐證）、未來語、grounding<0.30。
- **S3 刻意用 super scope `_SCOPE=(True,frozenset(),1)`（`build_context.py:33`）復現生產失敗路徑**：不做 domain 收窄，讓情境2（out-of-corpus）題也撈到「離題但 cosine 高分」的假 context，訓模型「拿到不相關 context 仍誠實 decline」（136/150 情境2 relevant=false）。context 全為 `retrieve_all` 真實輸出、零 LLM。
- **S5 直接 import 生產 guard byte-identical**（`validate.py:83`，guard.py 一字未動）＋一道 S5 專屬 grounding backstop（覆蓋 ≥0.30 或 ≥8 字逐字片段 ∈ citation，`:98-101`）；設計原則「只更嚴不更鬆」。**S5 GATE 由 pooled 改 per-batch**（`:123-125`）：異質批（不同 teacher/題型）不混池、各 `batch_tag` 獨立過 40% drop，防量測污染（delib 批 100% drop 曾把 pilot2 拖成假象）。
- **S2 三情境資料驅動＋DP7 GATE**：情境1（in-corpus, ANSWER，源 `_embedded_works` 實查＋curated concept/chem）、情境2（out-of-corpus, DECLINE，curated 明確零覆蓋域主題名 × 問法模板）、情境3（離題/未來, REFUSE）；DP7 生成期硬強制 out-of-corpus 佔比 ≥55% 否則 `sys.exit(1)`（`generate_questions.py:255-258`）。答案（gold）不在此生。
- **S4 usage 護欄硬編（#28/DP1）**：`teacher.py:98-101` `--run` 須 `--confirm` 且 `detect_teacher_mechanism` 偵測到憑證才跑，否則 exit 不自燒 usage；無參數印指令矩陣＋現況（安全預設）。
- **審議 → 蒸餾 back-flow（`bridge_deliberation_distill.py`）**：每條 oracle 裁決過（confirmed/refuted 且有 `is_deterministic` verdict）的工程宣稱 → 一題「此宣稱是否成立」QA、`expected=DECLINE`（因知識語料對 augur schema 零內容、誠實答法＝轉查 DB/oracle）、`topic_ref=claim_id` 溯源（`bridge.py:60-66`）；下游全複用 S2-S4 零重造，界線-A 零回流預測。現 29 題已橋、已建 context、尚未生 gold。
- **界線-A「蒸餾產物零回流預測管線」三重機械閘**：命名前綴 `advisor_distill_*`＋AST/字面掃描（`import_isolation.py:41` `DISTILL_LITERALS`、`:173`）＋DB REVOKE（`setup_predict_role.py:32` `FORBIDDEN_PREFIXES`）。`migrate_advisor_distill_ddl.py` 內**沒有** REVOKE——DB 層隔離真正住 `setup_predict_role`。`augur_predict` role 現存且對 `advisor_distill%` 零 grant。

### RBAC／身分認證／知識域授權（多租戶安全治理）

一條與資料/預測管線正交的讀取存取控制支柱，把 augur 從「單人本地工具」升為「一位 superuser＋受控多群組」，讓「誰能讀哪個知識 domain」成為 **server-side SQL 強制、預設 deny、fail-closed** 的機器邊界，同時絕不鬆動知識↔預測的 #1 隔離。承重設計只有一句：`knowledge_item.domain` 被**同時當作**(a) 因子鏈純度隔離欄與 (b) 授權邊界。

- **domain 雙用＝加法不改寫**：`corpus.clean_item_sql`（`corpus.py:51-70`）先組既有 license/entity_type CLEAN 述詞，再 **AND 收窄** domain；superuser 完全不加 domain 條款但**仍過 CLEAN**（`corpus.py:44`，讀不到未稽核/AI 生成/非白名單 license）——確保 RBAC 只作用於已 CLEAN 內容、不成知識→預測旁路（憲章 line 165-166 準則 i/ii）。
- **resolver 嚴格三態、型別分離、fail-closed**（`access.py:17-37`）：回 `(is_super:bool, allowed:frozenset)`，super→`(True,∅)`、非 super 有 grant→群組 grant 聯集、其餘一切（不存在/inactive/無 grant/Exception 兜底）→`(False,∅)`。刻意**不用 None=ALL 隱式哨兵**；SQL 用 `array_agg FILTER(WHERE domain IS NOT NULL)+COALESCE('{}')` 杜 `{NULL}` 誤判——吸收紅隊「空集 vs NULL 混淆 fail-open」。
- **`clean_item_sql` 安全字面內插 vs 參數化二分＋`(frag,params)` 二元組**（`corpus.py:51-70`）：封閉集常數（LICENSE 5 值、entity_type、access_scope）直接內插（值域受控），使用者資料（allowed_domains、owner_user_id）一律走 `%s` 參數化。回二元組讓呼叫端 `sql+=frag; params+=fp`，消除舊版手工位置對齊的三處錯位/fail-open（吸收紅隊 H1/H9）。非 super 且授權域空 → `AND false`（預設 deny 非不濾）。
- **access_scope 雙軸收窄**：`public → domain` 收窄（群組 grant）；`local_private → 擁有者收窄`（`owner_user_id=%s`，私有無部門語意故不 domain 收窄，跨使用者 fail-closed），super 見全部私有（`corpus.py:54-69`）。`retrieve_all`（`retrieval.py:363-369`）三路徑各取半交錯：works 對登入者公開、public items 走 domain、private items 走 owner。
- **identity 單一實作、三端＋殼共用**（`identity.py`）：pbkdf2_hmac sha256 240000 迭代（`_ITER=240000`，≥OWASP 210k）、DB 只存 `sha256(token)`（cookie 存明文、外洩不直接得可用 token）、`authenticate` 常數時間（無帳號也對 `_DUMMY_HASH` 跑一次 verify、抹平帳號列舉側信道）、`verify_session` 全 AND fail-closed（`revoked_at IS NULL AND expires_at>now() AND is_active`，`:81-84`）。chat:8090／probability:8600／admin:8500＋advisor 殼皆 import 同一份（禁 inline 複本 #12）。
- **身分絕不信 client 帶入**（`oai_compat._resolve_scope:198-219`）：前台由 server session 反查、只把 `X-Augur-Session` 經內部通道傳殼；殼先驗 `X-Augur-Internal` 共享機密 → `verify_session` 自查 DB → `resolve_allowed_domains` 自 resolve，body/header 帶入的 `user_id/allowed_domains/is_super` 一律忽略（防 IDOR 提權）。無 internal header **預設 fail-closed deny**（v1.30.0 紅隊 HIGH 修：舊 stopgap 預設 super、忘設 `AUGUR_INTERNAL_SECRET` 即 RBAC 靜默全失效）；`serve_chat_ui.py:864` 無機密直接 `sys.exit` 拒啟動，不靜默降級。
- **referential integrity 三重＋FK 故意延後**：`knowledge_domain` 字典為地基、`group_domain_grant.domain FK REFERENCES knowledge_domain`（phantom/拼錯 domain 授不出去）、`--grant-domain` 前檢 `is_authz_boundary=true`（`manage_rbac_user.py:142-147`）。但 `knowledge_item.domain` 的兩階段 FK **故意未套用**（#30 DDL 時機鐵律＋升邊界是政策決定）——入庫端「writer 把敏感列標成低敏 domain＝靜默越權」仍可能，是計畫誠實明列的殘留風險。
- **DB 層機械閘硬綁 owned_local 三軌**：`chk_itext_owned_local_private`（`license='owned_local'` 蘊含 `access_scope='local_private'`、DB 綁死永不公開）、`chk_itext_source_type`（禁 `source_type='ai_generated'` 入庫，#1）。`erp_tiptop` ERP 私有語料 150,685 段全 owned_local/local_private，其讀取實由「擁有者收窄」而非 domain 治理。
- **資料驅動零改碼**：加使用者/群組/授權皆純 INSERT（`manage_rbac_user.py`），`build_rbac_enterprise_groups.py` 冪等落地 7 職能群組 × 授權邊界域矩陣。系統定位由單人擴多群組＝動靈魂 v1.4.0→v1.5.0＋憲章 v1.28.0（決策層拍板）；三輪資安紅隊 critical 10/high 9 全處理入設計。`sync_admin_user.py`（07-11 新增）把 `.env` 帳密 upsert 成 `app_user` superuser 列，認證仍唯 identity 一家。

### 前台檔位（fast/think/ultracode）↔ 本地審議引擎接縫（F1）

兩個各自「名義上被覆蓋」子系統之間、任一端框架都不含的承重接縫：把「仿 Claude 前台」的 model×effort 選擇路由到本地零-token 審議引擎，再把 5-oracle 機械裁決以誠實模板端回用戶。它讓 #28「模型檔位分派」doctrine（fast/think/ultracode ↔ 輕/重/裁決）在前台真正落地。

- **model 欄承載 tier（OpenAI-compat 原生載體）**：`chat_completion` 現不讀 `body["model"]` 作邏輯 → 啟用它零相容破壞。`do_POST` 先 `effort.load_tiers()→resolve_tier(body.get("model"))`（`oai_compat.py:248-253`），tier id 閉集住 DB `frontend_tiers.tiers`，新增/停用檔位＝UPDATE 一列零改碼（#29b）。任何 OpenAI client 的模型下拉即自動成為檔位選單。
- **三檔位語意分流＋per-request llm 工廠**：fast＝R2 單發參數凍結（think=False/temp0.15/num_predict900）；think＝`make_llm_fn(think=True)`＋num_predict4096（對齊 GATE 預註冊 think_spec）；ultracode＝審議引擎轉接。`make_tier_llm_fn` per-request 注入（`oai_compat.py:261`），不動 `make_server` 簽名（#3）。
- **ultracode 路由＝機械規則零 LLM**：`route_ultracode`（`effort.py:86-107`）先過 eligibility 詞表（表/欄位/schema/列數/檔案/隔離/import），再機械組 target_block 三型（檔案路徑經 pathlib 存在性驗、表名對 `information_schema.tables` 比對），首行沿用 `engine._target_from_block` 既有契約 → 零 engine 解析改動。
- **結果併入不繞 guard（三路硬隔）**：`run_ultracode` 取單飛鎖 → `engine.deliberate`（全帳落 `deliberation_*`）→ 回讀 claim/verdict/escalation（`effort.py:143-152`）→ `verdict_block` 機械模板；narrative 另走既有 `advise()` 完整 guard 閘鏈（且用 fast 參數）；oai_compat 機械合成＝guarded narrative ＋ 分隔線 ＋ 裁決區塊。
- **雙標示誠實框架（`effort.py:155-175`）**：裁決區塊標題明載「宣稱原文＝LLM 提出、非系統背書；系統背書僅及 oracle 證據行」（`:159`）；四終態各有圖標（✓confirmed·bound / ◐ anchor-only 降格 / ✗refuted / ⚠已進人裁佇列），背書數字唯出 `deliberation_verdict.evidence` 行；固定尾註「兩者不一致以上方 oracle 裁決為準」（`:173-174`）。三態在真實資料上完整行使：frontend claim confirmed·bound 8／anchor-only 7／refuted 5／escalated 10。
- **單飛鎖＋config 熱翻旗（4GB 現實＋免重啟）**：`threading.Semaphore(max_concurrent=1)` 模組級（`effort.py:110-113`），非阻塞 acquire 失敗 → 即時機械忙碌句、不排隊不啟 engine（`:131-132`）；`load_tiers` 用 `load_rules(...,fresh=True)`（`effort.py:37-38`／`engine_config.py:22-24`）每 request 短連線繞 `_CACHE` 讀 config——正是 http.server「啟動載入不熱更新」教訓 #7 的**反面設計**，翻 enabled 旗標免重啟。任何讀 config 例外 → fail-safe `{"enabled":False}` 走 legacy 逐位元同現行。
- **`verify_claim` 是全系統唯一 confirmed 寫點**（`verifiers.py:148`），seam 零新增寫點、只呼叫既有管線、LLM 意見零證據力。`effort.py` 對諮詢資料面**零寫 SQL**（全檔僅 5 個 SELECT，grep INSERT|UPDATE|DELETE exit=1）。
- **8b-ultra 名實已明示**：選 `augur-8b-ultra` 時審議引擎本體跑 qwen3:4b（`ultra.engine_model` 固定），只白話 narrative 用 8b；UI label 明寫「審議引擎＝4b；白話＝8b」（`oai_compat.py:42`／`effort.py:135`）。

### 機械閘與不變式

- 顯著小數/IC/Sharpe/score 鄰接數字須 ∈ `payload.numbers()` 白名單，否則 guard fail（`guard.py:56-60`；`test_advisor_guard.py:61` stray 小數 pass=False）。
- 回覆引號內 ≥8 字須逐字 ⊂ 某 citation（`guard.py:50-53`）；檢索全空時回覆必為 `HONESTY_CLOSED_SET` 二句之一，否則 `guard_empty_retrieval` fail（`guard.py:137-144`，憲章 v1.25.0）。
- 方向/逐日價格/準確率排名題強制短路弱 LLM、直回 DB 驅動拒答句（`advise.py:148-150`＋`prompt.py:104`）。
- RBAC 預設 fail-closed deny：無 `X-Augur-Internal` 機密即非 super、絕不信 client 帶入身分（`oai_compat.py:198-219`；`test_rbac_enforcement.py` clean_item_sql 非 super 空域 → `AND false`）；`clean_item_sql` 契約回 `(fragment, params)` 二元組。
- `llm_fn` 端點 host 須 ∈ 本機 allowlist、否則建構時 fail-loud 拒起（`ollama.py:29-38`，三工廠皆施；憲章 v1.37.0）。
- S5 蒸餾複用生產 guard byte-identical，訓練集只收過閘者、機械保證只更嚴不更鬆（`advisor_distill_validate.py:83`）。
- `advise()` 是唯一諮詢編排出口、seam/oai_compat/effort 只翻協定/選檔位/起 server 不繞 guard；`effort.py` 諮詢面零寫 SQL。
- resolver 物理住 `augur.knowledge`（∈ FORBIDDEN 前綴）非 core，測試正向釘死（`test_philosophy_isolation.py:53-64`），預測 7 package＋core 禁 import 且禁字面引用 RBAC 表/resolver（憲章 line 163 機器強制）。
- `chat_history` 所有讀寫 `WHERE user_id=%s` owner 收窄，他人 session fail-closed（`chat_history.py` 全函式；IDOR/OWASP A01）；`user_settings` POST 過白名單鍵（theme/font_size/default_tier/enter_to_send）ON CONFLICT upsert（`serve_chat_ui.py:795-808`）。
- ultracode 單飛：`Semaphore(1)` 忙碌 → 機械忙碌句、`deliberation_session` 僅新增 1 筆；未知 tier fail-closed（HTTP 400 於任何 200 之前）；治權觸線 → escalation 人裁，不因前台鬆動（#19/#26）。

### 陷阱

- **選股題 guard fail 連確定性 picks 表一起丟失**：`_render_picks_table` 於 guard 後 prepend，但 `oai_compat._reply_text:99-106` 於 guard fail 時 `body=NO_KNOWLEDGE_RESPONSE` → picks 表被丟棄 → 對有真實 payload 的選股題回「知識庫中無此內容」語意矛盾（非對稱 fail-closed 代價，v3 已記、仍在）。
- **guard 與 guard_knowledge 負號正則不對稱**：`guard.py:57` 用 `-?\d+\.\d{2,}`（捕負號），`guard.py:121`（函式 `guard_knowledge`）用 `\d+\.\d{2,}`（無負號）→ 知識域對負值 sign-blind，可放行符號相反的編造值（citation 有 0.9987、輸出 -0.9987）。
- **蒸餾 274 gold 的 teacher 是 Claude、不是本機零-token**：DB `teacher_model` 全 `claude-teacher-workflow`（寫入窗 07-06 17:09-17:19、≈2.2s/題），由 out-of-band Claude-as-teacher 工作流直寫 DB、**耗 Claude usage、須人拍板**（機制 B）。committed `advisor_distill_teacher.py` 是真骨架、**從未產出過任何 gold**：其 `_call_teacher` 只接本地 ollama（`teacher.py:70-71` 對 claude 前綴會 raise），若真跑本機路徑 `teacher_model` 會記 `qwen3:8b`（`:107`）。**本機 qwen3:8b 只是 script 預設 fallback 機制 D**（`:58-60`），非實際產 gold 的 teacher；讀 teacher.py 會誤以為它是 S4 執行者。
- **S5 誠實 decline gold 過閘機制不是「閉集句觸發」**：`validate.py:89` `grounding_exempt = (expected in ("DECLINE","REFUSE") or any(閉集句 in target))`——第一 disjunct 對所有情境2（全 DECLINE）已成立，與是否含閉集句無關；實查 118 個通過的情境2 gold 僅 22/118 以「知識庫中無此內容」起手、46/118 完全不含任何閉集句仍通過。故真正過閘＝(a) `expected=DECLINE` 被 grounding 豁免 ＋ (b) 內容不觸發 `guard_knowledge/guard_attribution`（不裸捏出處）；閉集句只是行為誠實的常見措辭、非機械過閘之因。
- **32 題 situation-1 的 expected 被外帶覆寫 ANSWER→DECLINE**：`generate_questions.py:173/176/179` 硬編 `expected='ANSWER'`，但 DB 內 situation-1 relevant=false 者 expected 全＝DECLINE（32 列），無任何 committed UPDATE script（同 gold 之 out-of-band 直寫模式）——staging 側 #12「不 hand-patch」張力。
- **`RELEVANCE_FLOOR=0.30` 與 `best_overlap` 讀值會誤判為現行閘**：相關判定 100% 走 `_strong_distinctive` 專詞集，floor 只保留為簽章相容＋遙測；`advise.py:9/:131` docstring STALE（仍寫「llm_fn 可接 Claude API」，v1.37.0 已禁外部、本機限定僅由 wiring＋G3 焊點落地，advise() 本身不機械強制本機）。
- **知識↔RBAC 兩個誠實殘留**：`knowledge_access_audit` 目前只是「管理動作帳本」（66 列全 grant_domain/add_domain/create_group/create_user，零 login/retrieve/deny）——runtime enforcement 是靜默的；`knowledge_item.domain` 兩階段 FK 未套用（入庫端標錯無 FK 攔）。另 `concordance_lookup/lexicon_lookup` 歷史上連 CLEAN 閘都沒過、現況零呼叫點，`retrieval.py:193-195` 明文警告「接線即洩漏、必先加 clean_item_sql 收窄」。
- **admin console env 後門是第二登入路徑**：帳號留空或＝`AUGUR_ADMIN_USER` 即比對 .env 明文/pbkdf2 → 臨時 superuser 記憶體 session（`serve_admin_console.py:800-808`，明文分支走 `hmac.compare_digest`、不經 `identity.authenticate`），標「相容期」、為本機綁 127.0.0.1 之刻意取捨；治權升級走 CLI 需互動 TTY＋is_superuser（`review_knowledge_source.py:66-67`），web/AI 結構上不能觸發。

### 07-10（v3）之後的變化

- **整個「前台檔位 ↔ 審議引擎」seam 在 v3 報告零命中**（grep effort/ultracode/檔位/verdict_block 與 deliberation 於 763 行 v3 全 exit=0，連審議子系統本身都不在）：`effort.py`＋`engine_config` fresh 參數＋`engine.deliberate` progress_cb＋oai_compat F1 tier 解析同一 commit `d86444b`（07-11 15:11）落地，enabled 旗標同日 21:43 翻 ON（v3 後 1 天內從無到 LIVE），已跑 5 場真實 `[frontend]` 前綴審議（07-12）。**只讀 plan 會誤判尚未上線、須查 DB 才知現況**。
- **蒸餾 S1-S5 pilot 早已完成、v3 稱「斷在 S4／target 全 NULL／無訓練資料」為 stale**：實際 07-06/07 已產 274 gold＋171 行 SFT（`data/distill/sft_pilot2.jsonl`，early 於 v3 報告 3 天）；`bridge_deliberation_distill.py`（v3 後新增，07-11 由 ANSWER 改判 DECLINE）29 題已橋；S5 GATE 由 pooled 改 per-batch；`augur_predict` role v3 稱「尚未建」現已建且對 distill 零 grant。
- **方向軸誠實全鏈上線（07-11）**：新增 `DIRECTION_SIM_HONESTY`/`DIRECTION_PATH_FIXED_RESPONSE`＋`advise.py:148` 短路；拒答句改 DB 驅動即時查 `direction_gate`（v2 四門 → 現 19 門）；07-12 修方向分類器短路誤傷——`_DIR_PAT` 移除裸「未來 N 天」、改 `_HORIZON_PAT × _DIR_WORD_PAT` 共現才算方向題，使「未來 60 天看好哪些台股」正確走 picks（`77cee4b`）。
- **chat UI Claude-Desktop parity 收尾（07-12）**：設定面板＋`user_settings` DB 持久化＋暗色主題＋Claude 式檔位下拉＋側欄收合＋訊息編輯/複製＋cmd-k 搜尋＋ultracode 審議裁決專屬卡（誠實紅線永遠展開、`serve_chat_ui.py:253` CSS「永遠展開、不得摺疊」）。
- **RBAC 部署狀態精確化**：v3 稱「provisioning 待拍板」欠精確——群組**結構**（7 群組/31 grant/27 授權邊界域/1 superuser）已於 07-05 落地 DB，僅**人事指派**（`user_group=0`）待用戶補，實質仍等同單一 superuser；`erp_tiptop`（第 27 個授權邊界域、~15 萬段 owned_local）為 v3 後可見部署狀態。`sync_admin_user.py` 為 07-11 新增（.env → app_user 單一帳密源）。核心 RBAC 程式 07-05 定稿、v3 後無實質改動。
- **K 計畫橋接進 advisor（07-12）**：`advise.py` 新增 `_bridge_links/_bridge_block`——問句命中 raw 欄位名 → 查 `field_knowhow_lexical_affinity`（唯讀、免責硬綁「lexical 非資料值與報酬相關」）。相對機率附欄（P6，v1.40.0）：`payload.py` 新增 probs/prob_note，picks 表渲染 P30/P60/P120＋四誠實標記（判死 horizon 帶 dead 標籤，標記與機率硬綁不可分離）。v3 未完成債「`example_payload` 為預設 payload_fn」已修（現預設 `empty_payload`，不再有注入假 score 風險）。

---

# 第三塊系統與跨系統維運

## §5 本地審議引擎:第三塊系統(開發治理)——12模組/oracle機械鎖/GATE證成/L2F1

### 5.1 這層在做什麼

前兩塊系統(量化本體、顧問層)產「給人的答案」;第三塊系統管的是「AI 自己說的話能不能信」——把「Claude ultracode 的多視角對抗驗證」搬到本地零-token 運作。核心設計:讓弱模型(qwen3:4b/8b)只做它做得到的事——**提出「帶錨點、指定確定性 verifier」的可機械驗證宣稱(claim)**;而「判對判錯」一律交給確定性 oracle(查 DB / 掃檔 / 跑隔離稽核 / 跑 pytest)。哲學=CLAUDE.md #15「LLM 意見零證據力、工具輸出才是證據」+ 靈魂「系統建議、人決策」。存在理由=#28 2026-07-11 用戶 directive:機械可驗宣稱之驗證/審查/裁決一律**優先本地審議引擎、Claude 為後備**,全程不燒 Claude usage;undecidable 或觸治權紅線則誠實升級人裁,引擎永不自判 confirmed。子系統住 `src/augur/deliberation/` 12 模組 + `scripts/` 5 支 CLI + `advisor/effort.py`(F1 前台),DDL 單一住所在 `scripts/migrate_deliberation_ddl.py`(16 張 `deliberation_*` 表)。

### 5.2 怎麼建的——機械鎖是單一真理來源

**confirmed 的唯一寫點=verify_claim。** 全系統只有 `verifiers.py:191` 這一句 `UPDATE deliberation_claim SET status=...` 能把 status 寫成 `'confirmed'`,且只在跑完 assigned_verifier 得 `confirmed` verdict(`is_deterministic=true`,`verifiers.py:181-183`)後才寫。propose(qwen 葉端)、consensus、iterate、panel、甚至人裁,全都**寫不到 confirmed**。這個設計把「造真」的權力整個從模型手裡拔掉——弱模型只需會提問。強制層是**代碼單一寫點紀律 + 測試**,不是 DB trigger:`deliberation_claim` 上零 trigger(`information_schema.triggers` 查無),表層 CHECK 只約束枚舉閉集(status/assigned_verifier/category),「confirmed ⟺ deterministic verdict」的等價關係僅靠 `verify_claim` 單一寫點守護(`__init__.py:4-5` 明言「engine 層強制,表層 CHECK 承載閉集」)。實查佐證:`SELECT count(*) FROM deliberation_claim WHERE status='confirmed' AND NOT EXISTS(is_deterministic confirmed verdict)=0`。人裁路徑也不鬆:`resolve_escalation.py:6` 明文「人裁只寫 escalation 三欄、絕不改 claim.status 為 confirmed」——連 `human_confirmed` outcome 也不翻(正道=補可機驗 anchor 重裁)。

**5-oracle 封閉集 + 唯讀沙箱。** `verifiers.py:30` `ORACLES=(information_schema, import_isolation, file_grep, db_query, pytest)`,與 `deliberation_claim` 的 `assigned_verifier` CHECK 閉集同錨(pg_constraint 含 `human_claude`/`none`)。`run_verifier`(`verifiers.py:143-145`)對非閉集 verifier 一律回 `undecidable`;各 `_v_*` 對不合契約的 anchor 也回 `undecidable`(fail-closed,寧 escalate 不硬猜)。安全契約逐 oracle:
- **db_query**(`verifiers.py:86-109`):`BEGIN TRANSACTION READ ONLY`(:96)+ `SET LOCAL statement_timeout='30s'`(:98)+ `ROLLBACK`(:107);SQL 須單條 SELECT、不含 `;`、不命中 `_DB_FORBIDDEN`(`:31-32` insert|update|delete|drop|alter|grant|set…);只認單一標量。
- **file_grep**(`verifiers.py:64-83`):realpath 圍欄拒逃逸(:69-70 須 startswith `REPO_ROOT`)+ `_SECRET_DENY`(`:33-34` `.env`/`.key`/`.pem`/credential…)拒讀機密檔(圍欄內仍擋)。
- **pytest**(`verifiers.py:112-134`):node 限 `tests/` 下 realpath、`-x -q --no-header -p no:cacheprovider`、120s timeout;exit0=confirmed / exit1=refuted / 其餘=undecidable。

**anchor 正規化層——把 LLM 從可機械化處移除。** qwen 常把 anchor 寫歪,`anchors.py` 用確定性規則修正:L1 `schema_grounding`(:42,題目詞→information_schema LIKE 實查→注入真表清單,防臆造表名)、L2 `verifier_lint`(:141,查無表但形似程式符號→改派 file_grep,防假 refuted)、L3 路徑誤蓋修(`normalize_anchor:31`)、L4/L5/L6 具名快路(`fast_anchor:64-110`,可機械解析的中文宣稱如「表 X 至少 N 列」→零 LLM 直接構 db_query 錨)。快路參數經嚴格 regex 白名單抽取(表名 `[a-z_][a-z0-9_]*`、值 `[a-z0-9_.-]`),整段 SQL/節點原樣**進不了錨**——`test_fast_anchor_injection_counterexample`(`tests:139-145`)守著 UPDATE/引號/分號注入反例。實測 28/340 claim 走過快路(DB `provenance ? 'fast_path'`)。

### 5.3 怎麼建的——共識、迭代、十模式編排

**三級殺權共識(`consensus.py:33-51`)。** 同題跑 N 個 lens(各成 session),依去重鍵 `(verifier, 正規化 anchor)`(`:18`)聚合:① 任一 `refuted`=**單票即殺**(`:34`,工具說假就是假,不投票,排在 confirmed 判斷之前)② 需底層已有 `confirmed` 才聚合為 confirmed(`:37`,不製造)③ 全 escalated/undecidable/pending→`escalated`(`:40`,絕不因多數升 confirmed),混合→`contested`。整支 `consensus.py` 為純函式、**零 DB 寫語句**——多數決不鬆機械鎖。停機由 `critic.py` 的 loop-until-dry 判:`is_dry`(`:23-25`)連續 `dry_k=2` 輪無新確定性發現(只認 confirmed/refuted、escalated 不湊數)才停;`uncovered_tables`(`:28`)機械枚舉題目命中之真實表尚未被覆蓋者,注入下一輪 lens 提示(完整性 critic)。編排在 `engine.deliberate_panel`(`engine.py:86-114`,max_rounds=3)。

**十模式共用同一裁決管線、皆不鬆機械鎖。** `scripts/deliberate.py` 薄殼把 `--run/--panel/--iterate/--judge/--run-plan/--resume/--report/--list-runs` 對映十模式。模式 9 自我迭代(`iterate.py`,DRAFT→ATTACK→REFINE→VERIFY):refined 宣稱走 `_verify_claims`(`:39-44`)= `ledger.insert_claim`→`verify_claim(cur=cur)`(同交易,唯一 confirmed 寫點不變);`llm_fn` 注入式(測試可假 LLM 零 GPU)。模式 4 judge panel(`panel_judge.py:25-47`):多判官 soft 評分只 INSERT `deliberation_panel_score`、**零 claim 寫入、零 confirmed 權**。模式 10 run/task(`ledger.py`)= 帳本承載長跑(create_run 冪等/resume_reset/next_task/finish_run),resume-safe。全程 LLM 只在 propose 葉端且用本機 qwen(`engine.py:12` `from augur.advisor.ollama import make_structured_llm_fn`,ollama 端點鎖 localhost:11434 + host allowlist 拒公網);裁決/共識/停機/GATE 全零模型智力、零 Claude token。

### 5.4 怎麼建的——治權紅線、GATE 證成、F1/L2 前後台

**D6 治權紅線強制人裁(`redlines.py` + `ledger.py:38-41`)。** `insert_claim` 在快路**之前**(`ledger.py:38`,早於 `fast_anchor:44`)consult redline:claim/anchor 命中 anti-leakage 時點欄(如 `AnnouncementDate`)或治權檔→`assigned_verifier` 強制改 `human_claude` + `provenance.redline` 留痕→`verify_claim`(`verifiers.py:172-173`)走 escalation `reason='red_line_category'`。語意:治權判準/anti-leakage 相關宣稱不得由弱模型+oracle 逕行機裁,決策層人拍板(#19/#26)——紅線豁免不了快路。已 live 落帳 6 筆 `red_line_category`(AnnouncementDate 健檢宣稱全被轉人裁),機制從「9 列死設定零 consumer」變成真接電。

**可證偽的「習得」GATE(`benchmark_deliberation.py`)。** 這是引擎「效力」的唯一證成路徑:`--preregister` 凍結門檻/口徑/seeds/題庫版本/`rules_config_sha` 快照→三臂(single_fast/single_think/engine)×3 題集 seed(經模式 10 帳本、跨真實停電 resume)→`--report-gate` 讀快照斷言。三判準=median acc 增量≥+15pp、engine 假確認≤各臂 min、McNemar 合併 p<0.05;門檻讀自凍結快照的 `cfg['thresholds']`(`report_gate:406,418`)**非 code 常數**。「事後不得挪門柱」機械強制:快照缺失(`:388`)、rules sha 漂移(`:392`)、`preregistered_at ≥ min(run_at)`(`:396-397`)任一違反即 `exit 1`,重跑=新 batch 新預註冊。實績:`gate_43044a574c0d` **PASS**——engine median acc 100.0% vs 最佳非引擎 53.3%=+46.7pp、假確認 engine=0 vs 各臂 min=7、McNemar 合併 p=3.64e-12(逐 seed 41/42/43 全顯著;`reports/augur_deliberation_a5_remeasure_20260711.md:14`)。DB 獨立實查該 batch:engine 90/90 fc=0、single_fast 50/90 fc=20、single_think 47/90 fc=7。

**F1 前台轉接(`advisor/effort.py`)。** chat UI 選「ultra 檔」→`resolve_tier`(`:45-54`)→`run_ultracode`(`:121`)→`route_ultracode`(`:86-107`)機械 eligibility(關鍵詞命中「表/欄位/schema/列數/檔案/隔離/import」才進引擎,`:89`)→單飛鎖(Semaphore max_concurrent=1,`:110-113,130-132`,4GB VRAM 現實,忙碌回機械誠實句)→`engine.deliberate`→`verdict_block`(`:155-175`)零-LLM 機械模板附回覆尾。**雙標示是刻意設計**:宣稱原文永遠標「LLM 提出、非系統背書」(`:159,161`),系統只背書 oracle 證據行;`confirmed·anchor-only`(語意未綁)會降格顯示「僅錨點查證通過,不背書宣稱全文」(`:166`)。config `fresh=True` 讀(`load_tiers:34-42`)=翻旗標免重啟;不合格題誠實 fallback 走一般 advise()。**eligibility 詞表是雙面刃**:誤放行頂多 undecidable→escalated(誠實不損);但機械可驗題若不含關鍵詞會被判不 eligible、走 fallback 根本不觸審議——「該審而未審」的漏放行由詞表覆蓋面決定。

**L2 每日自審(`run_daily_deliberation.py`)。** 零-token cron 入口,讀 `deliberation_daily_topic`(enabled)常備題庫逐題跑 panel→confirmed/refuted 落帳、escalated 進人裁佇列,收尾印積壓。人裁佇列由 `resolve_escalation.py` 消化(`--list/--resolve/--watch`),`--watch` 的殭屍 session 偵測與積壓警示皆 warn-only(exit 0)、屬可見性非硬閘。

### 5.5 機械閘與不變式(速查)

| 不變式 | 強制點(path:line) | 佐證 |
|---|---|---|
| confirmed 唯一寫點=verify_claim(非 DB trigger) | `verifiers.py:181-191`;`__init__.py:4-5` | DB:0 confirmed 缺 deterministic verdict;`triggers` 查無 |
| 5-oracle 封閉集;非閉集/不合契約→undecidable→escalate | `verifiers.py:30,143-145,185-188` | pg_constraint 含 pytest;undecidable escalation=102 筆 |
| consensus 三級殺權、refuted 單票即殺、零 confirmed 寫權 | `consensus.py:34,37,40`(純函式無 DB 寫) | `tests:18-39` |
| 治權紅線先於快路、命中強制 human_claude | `ledger.py:38-41` + `redlines.py:22-37` | `red_line_category` escalation=6(AnnouncementDate) |
| db_query 唯讀沙箱(READ ONLY+30s timeout+禁寫詞+拒多語句) | `verifiers.py:92,96-109` | `tests:105-121` |
| file_grep realpath 圍欄 + 秘密檔 denylist | `verifiers.py:69-73` | `tests` secret denylist |
| GATE 門檻讀快照、rules 漂移/挪門柱/事後預註冊→exit 1 | `benchmark_deliberation.py:388,392,396-397` | gate_43044a574c0d PASS |
| 人裁只寫 escalation 三欄、不改 claim.status | `resolve_escalation.py:6,51-53` | 機械鎖連人不鬆 |
| semantic_bound 二級制:confirmed 分 bound / anchor-only 降格 | `anchors.py:113-138`;`effort.py:162-167` | DB confirmed true:164 / false:38(合計 202) |

裁決效力域邊界(A5 §1):GATE PASS 效力止於 5-oracle 可裁域(schema 存在/量比較/檔內容/隔離不變式);undecidable 誠實 escalate、LLM 意見零證據力、治權觸線強制人裁——三者不因「效力成立/為主」鬆動。

### 5.6 陷阱(gotchas,親驗)

- **redline `doctrine_file` 觸線樣式已 STALE/部分失效**:`deliberation_redline_trigger` 現存 pattern 為 `docs/原則精華_v1.8.0.md`、`docs/系統核心思想_v1.5.0.md`、`docs/系統架構大憲章_v%`,但現行檔名已是 `原則精華_v1.9.0.md`/`系統核心思想_v1.8.0.md`/`系統架構大憲章_v1.45.0.md`(親驗 `docs/` ls)。`redlines.consult` 用 Python 子串 `in`(非 SQL LIKE,`redlines.py:30,33,35`),故 ① 舊版本 pin 不 match 現行檔名 ② 憲章樣式的 `%` 是字面字元、真實 anchor 路徑不含它→憲章 doctrine_file 觸線經 file_grep 幾乎永不觸發。目前只有 CLAUDE.md/README.md 兩條 doctrine_file 觸線是活的;anti-leakage 欄觸線 4 條正常(6 筆演練皆走它)。潛在防護缺口,尚未致害但值得修 pattern。
- **`verifiers.py:1` 標頭 docstring 仍寫「四真 oracle」**,但 code(`ORACLES` 5-tuple `:30`)、CHECK 閉集、`_v_pytest` 皆已含 pytest=5 oracle(P3 新增)——標頭字數低估。
- **seed 在 temperature=0 貪婪解碼下為 no-op**(`engine.py:21-23,25` 誠實註記):真正可重現量測軸=題集抽樣 seed(`benchmark build_tasks` 的 `random.Random(seed)`),非模型解碼 seed;誤把 seed 當模型隨機源會誤解重複性。
- **L6_pytest 生產預設關**(`anchors.py:59` 註明、DB config `fast_anchor_rules.L6_pytest=false`):執行任意測試節點=最大攻擊面,故快路預設不自動路由 pytest;仍可經 LLM 顯式提 pytest verifier + tests/ 沙箱驗。改開=UPDATE config 一列。
- **GATE 三批誠實留檔、不消音**:`gate_663fecd41783` FAIL(假確認逐輪 engine=1、依「不挪門柱」判死)、`gate_97ece3e`(core_universe 素材 bug)作廢、`gate_43044a574c0d` PASS——判死留檔=「不挪門柱」紀律的實證,不是把失敗批刪掉重跑。
- **D3/D4 GATE 驗收句原本寫錯載體**(≥1800s session vs run/task):單場審議 by design 數十秒,長跑實由 run/task 帳本承載(GATE run 跨停電 resume 完跑);hugo 2026-07-12 裁定採措辭修正案。
- **verdict_block 雙標示不可誤讀**:`confirmed·anchor-only`(語意未綁)僅代表錨點查證通過、不背書宣稱全文,呈現時已降格——不可把 anchor-only 當全文背書。

### 5.7 07-10(v3)之後的變化

v3 建構理解報告(`augur_construction_understanding_20260710.md`)**完全沒有審議引擎章節**(grep 全文無「審議/deliberation/ultracode」段落標題;其提到的 GATE 是 DP7 蒸餾 out-of-corpus 關卡、與本子系統無關)。整個本地審議引擎子系統對 v3=空白 prior art——MVP 於同日 commit 24e87a3 落地,P0-P3 補完 + F1 + L2 皆在 07-10 之後(或與報告並行),故本 §5 是此子系統的**首份深度理解**。07-10 後的具體變化:
- **P3 模組化**(commit e2f257a):單體 `deliberate.py` 拆成 `src/augur/deliberation/` 12 個內聚模組 + lens prompt DB 化(#29b);P3 完整版(a1e98c3)加 panel/consensus/critic/pytest oracle/L6 + 引擎回歸測試 315 行(`tests/test_deliberation_engine.py`)。
- **oracle 從 4→5**:P3 新增 pytest 沙箱 oracle(限 tests/、-x 120s、exit0/1/其餘=confirmed/refuted/undecidable);CHECK 閉集同步擴。
- **GATE 機制成立**(commit 455e009 + `gate_43044a574c0d` PASS,07-11):preregister→gate_run(三臂×3seed 跨真實停電 resume)→report_gate 三判準;engine 效力「預註冊成立」。
- **F1 前台旗標翻開**(DB config `frontend_tiers.enabled` 現=true;A5 報告 07-11 時=false):code 鏈 commit d86444b 已接(旗標關),之後經 UPDATE fresh 讀免重啟翻開;實查 5 個 `[frontend]` 前綴 session=F1 已被路由使用(唯 `effort.route_ultracode:90` 注入此前綴)。這是純 DB config 變更、不在 git。
- **L2 每日自審就緒未掛 cron**:題庫 `deliberation_daily_topic` 3 題(core_invariants/ledgers/probability_layer)全 enabled 且經 `--run` 手動跑過(07-12 session 與題庫逐字相符者各 6 場),但**本換機環境 crontab 無 delib 條目**、session 止於 07-12(無 07-13)——#31 cron 機器本地不隨 git,origin 機 07-12 曾跑首個全自動日。
- **D6 治權紅線 live 演練落帳**:6 筆 `red_line_category` escalation,機制從「9 列死設定零 consumer」變成真接電(commit 455e009)。
- **引擎規模成長**(A5 07-11→現查):claim→340(confirmed 202=bound 164+anchor-only 38;fast_path 28);escalation reason 分布 undecidable 102 / red_line_category 6 / no_oracle 1(15 undecidable 未決人裁積壓)。

---

## §6 跨機/維運/自癒:#29-31 落地/零usage工具組/看門狗/常綠e2e

這層管兩件 v3 完全沒寫到的事:一是「augur 怎麼搬到另一台電腦還能接續開發」(#31 換機接續本地優先),二是「搬完之後每天怎麼證明系統還暢通、斷了怎麼自己爬起來」(常綠 e2e + 自療看門狗)。它落地 CLAUDE.md #28-31,核心精神=**本地優先零 Claude usage**(能用本地 DB/script 算的絕不繞道 model)、**AI 不代勞人工前置**(.env 重建、dump 實體搬只檢查提示)、**破壞性須明示授權**(#6)。全部是根目錄的 bash/python 腳本 + `scripts/` 下四支驗證器,底座是 `scripts/_bootstrap.py` 讓每支 script 任何 cwd 直接可跑。

要先分清三軸,別把它們混為一談:**一次性搬機 setup**(五件組)vs **每天證明還活著**(daily_green 本地零 API 綠檢)vs **市場攝取續命**(audit_selfheal 吃 FinMind、易 IP ban)。後兩者常被並列為「持續存活迴路」,實質分屬本地管線健康與市場資料自療兩層,嚴格分離(`daily_green.py:7-8`)——一條零外部 API、一條專打 FinMind,兩者互斥於同一 IP。

### 零 usage 五件組:換機接續前置的本地編排(#31)

`resume_project.sh` 是一鍵入口,把「一串人工 fetch/merge/pip/restore」收斂成一條可重跑的本地零-usage 鏈,依序 5 步:0) 檢 `.env`(缺即 exit 1,人工前置不代勞)→ 1) venv(缺則 `python3 -m venv` 自建)+ `pip install -e .`→ 2) `sync_from_github.sh`→ 3) `sync_memory.py restore`→ 4) DB 偵測(`--with-db` 才連 `import_database.sh`,已存在庫**不動**、要重匯得 `--force`,`resume_project.sh:53-60`)→ 5) smoke。設計刻意**容錯續行**:步 2/3 失敗以 `⚠` 印訊息續跑(`resume_project.sh:38,42`)而非硬中止,且各子步皆可獨立單跑;ROOT 由 `BASH_SOURCE` dirname 推導(`resume_project.sh:12`)故可搬任何 clone 路徑。**兩個無法自動化的人工前置由腳本檢查提示、明確不代勞**:(1) `.env` 重建(含 DB 憑證/密鑰、不在 git,鍵見 HANDOFF §3);(2) 6.6GB dump 實體搬到本機(不在 git,`import_database.sh:51` 預設搜 `~/db_dumps`、`/mnt/d/database`、`/mnt/c/AI`,檔名 `augur_pg17_*.tar` / `augur_pgdump_*_Fd` 目錄 / `augur_*.dump`)。

- **`sync_from_github.sh`(只走安全 fast-forward)**:刻意只走最安全更新路徑——先驗「在 main 分支 + working tree 乾淨」兩道前置閘(`sync_from_github.sh:18-20`、`:21-25`,任一不過 exit 1),再用 `git merge-base --is-ancestor HEAD origin/main`(`:41`)判分岔;**一旦雙方各有對方沒有的 commit 就完全停手**(不 merge/rebase/reset),只印雙方各領先幾個 commit 交人判斷,唯 HEAD 是遠端祖先才 `git merge --ff-only`(`:50`)。且只有偵測到 `src/` 或 `pyproject/setup` 變動才重跑 pip(`:57`,省 usage)。why=接續腳本絕不能自作主張改寫 git 歷史。
- **`sync_memory.py`(memory 隨 repo 遷移)**:Claude memory 原機器本地(`~/.claude/projects/<mangled>/memory/`)不隨 git。做法是用路徑 mangle 由「當前 repo 實際位置」反推活 memory 目錄(`sync_memory.py:32-33` `mangled=str(REPO_ROOT).replace("/","-")`)。`export` 把活 memory 忠實鏡射進 repo `handoff_memory/`(活端已刪的檔也 `unlink` 抹掉,`:87`);`restore` 還原回活 memory,且覆蓋前對「兩邊都有且內容不同」的檔做 timestamped 備份(`:103` `at_risk=u`、`:105-111`),活端獨有(快照沒有)的檔一律**保留不刪、只印警告**(`:120`)——守 #6 不毀資料。含明碼服務密碼的 `ttai-integration-and-platform.md` 蓄意不入快照(#5),故 `handoff_memory/` 為 40 檔而本機活 memory 較多。
- **`read_handoff.py`(誠實不代勞的接續閱讀器)**:把 `HANDOFF.md` + memory 索引 + 全 memory 內文組成 digest 印到 stdout,可 pipe 給本地 qwen3:8b 問答。標頭誠實聲明兩件事:(a) 它**不會**減少 Claude 自己讀 memory 的量(Claude 由 harness 自動注入索引),省的是「人/本地 AI 不開 Claude 就讀到全狀態」那條路徑;(b) 剛換機找不到 memory 不報錯、只印 HANDOFF + 提示(`read_handoff.py:8-13`)。同精神:`resume_project.sh`/`import_database.sh` 對兩個無法自動化的人工前置(`.env` 重建、6.6GB dump 實體搬)只檢查提示、明確不代勞。
- **底座 `scripts/_bootstrap.py`(11 行 path 墊片)**:每支 script 於 `import augur` 前 `import _bootstrap`,即把 `src/` 插入 `sys.path`(`_bootstrap.py:9-11`),達成「任何 cwd 直接 `python scripts/X.py` 即跑、不需 `PYTHONPATH=src` 前置」且與 `pip install -e .` 並存(已裝則 no-op);路徑邏輯單一住此(#12)。實測 **172/174** 支採用,僅 `backfill_knowhow_pipeline.py`、`verify_code_reports.py` 未 import。

另有 `start_chat.sh`(本地「誠實博學的我」服務棧一鍵起:Ollama:11434 + advisor + chat UI:8090,`up()` 埠偵測冪等)——與五件組同組,但 ROOT 硬寫 `$HOME/project/augur`(`start_chat.sh:6`),見〈陷阱〉。

### import_database.sh:大檔還原 + HNSW 記憶體最佳化(07-13 收官)

這是 #30 平行 `pg_dump -Fd -j4` 慣例的**還原端對偶**,`--dry-run` 只偵測格式 + 輕量驗證 + 印計畫、不解 tar 不動 DB(#29d graceful 安全預設)。

- **三格式自動判 + stage**:tar 內含 `-Fd` 目錄 / 裸 `-Fd` 目錄 / `-Fc` 單檔,需要時先解 tar 到本地 stage(`trap EXIT` 清理,`:23`)。
- **分階段還原(核心)**:拆 pre-data / data / post-data 三段,前二段 `-j4` 並行快載,**post-data 索引/約束段獨立降並發 `-j2`**(`:135`)並用 `PGOPTIONS` 提高 `maintenance_work_mem=$IDX_MEM`(預設 2GB,`:136,143`)。why 已寫進 code 註解(`:131-134`):augur dump 含 **3 個 pgvector HNSW 向量索引**,同時建置各吃一份 `maintenance_work_mem`——全域預設 64MB 會龜速 spill 磁碟(實證卡 70 分),盲目全域調高又讓並發建索引 OOM,故用「高記憶體 × 低並發」單獨伺候索引段(建議式護欄:`IDX_MEM×2` 須 < RAM−shared_buffers)。
- **收尾 + #8 隔離**:確保 `augur`/`augur_predict` 角色存在、還原後跑 `setup_predict_role.py --apply --confirm` 補 #8 隔離 GRANT(`:148-150`);`--migrate` 選配補跑 `migrate_*_ddl.py`(glob 冪等,`:158`)對齊較舊 dump。
- **破壞性安全閘**:對已存在 augur 庫拒絕覆蓋、須 `--force` 明示(先 `pg_terminate_backend` 終止連線再 `DROP DATABASE`,`:93/102-103`),新機庫不存在則直接建。
- **斷言式 smoke test(07-13 教訓)**:不只信 exit 0 與表數,額外查 `USING hnsw` 索引數並斷言 ≥3(`:168/172`),缺就警告「索引段可能未完成、查完整 log、可 `--force` 重跑」;同時保留完整 `pg_restore` log 不再 `tail -5` 吞錯(#7)。

### daily_green.py:無 CI 下事實上唯一的每日健康閘(常綠 e2e)

**這 repo 完全沒有 CI**——無 `.github/workflows`、無 `.pre-commit-config.yaml`、`.git/hooks/` 全是 `.sample`(親驗)。因此 `daily_green.py` 這條每日綠檢是這個系統事實上唯一的持續健康閘(對應 e2e 主計畫 P7、憲章 v1.40.0「暢通不變式」);audit_selfheal 屬資料同步自療、非 pass/fail 閘,不算健康閘。

它是**薄殼 subprocess 序列器**,本體不含任何驗證邏輯:把四支既有可執行驗證器當積木,以 `sys.executable` 逐支 shell 呼叫並彙總 exit code,`STEPS` 是資料驅動的 `(name, argv)` 清單(`daily_green.py:29-34`)、`--skip`/`--with-benchmark` 只是參數化它,任一子驗證器 `returncode≠0` → 整體 `return 1`(`:53-57`)。此設計刻意複用而非新寫,呼應 #29a「每支個別可執行」。四驗證器各守一層:

- **`verify_knowledge_e2e_smoke.py`(暢通不變式判定器,fail-closed)**:用 sentinel 走真實管線做端到端斷言——底文=真實公版句(Adam Smith《國富論》1776,`:38-40`,#1 禁 AI 生成 sentinel)+ 唯一 nonce、`domain='smoke_test'` 隔離,經既有 CLI 逐支驅動(#12 複用 builder),再機械斷言、最後 `--clean` 冪等拆除。修 A-16「只驗正向可檢索=假綠燈」後為 **fail-closed**:除正向(nonce byte-equal 命中,`:116-122`),還斷言反向——private 對照列(`access_scope=local_private` 無 owner)不得被域授權檢索到(`:126`)、無授權檢索須回 0 hits(`:128`);再加語料隔離斷言(smoke 前後 `term_affinity/corpus_stats` 列數不變,`:145`),07-12 又加 K1 橋斷言(欄位問句命中 + 免責硬綁 + 低支持 pair 物化 CHECK≥30,`:134-139`)。`--clean` 依 FK 順序 DELETE(embedding→concordance→sentence→fulltext_status→item_text→item→staging,`:56-77`)冪等拆除;正式庫當前 `domain='smoke_test'` 殘留 0 列,證明隔離 + 拆除有效。**nonce 必須造成純字母才進 exact 索引**(`:81`,#債1 修),否則正向斷言會靜默落空。
- **`verify_advisor_regression.py`(顧問回歸釘)**:把「顧問輸出每個數字都對得上 DB ground truth」變成可重跑機械驗收——`--no-llm` 結構模式用 mock `llm_fn` 回固定字串達 CI 可重現(A-30),斷言 picks 渲染 = `prediction_values` round-4 byte-equal + rank 整數等同(`:51`)、guard 五閘、髒數字反斷言(mock 編造 1234.56 必被攔,`:121-124`)。機率附欄斷言會在 `prediction_probability` 由空轉非空時**自動 SKIP→HARD**(`:64-67`),含逐值等同 + 四誠實標記 regex + P30 判死硬綁(`:75-93`)。
- **`verify_qdrant_shadow.py`(cutover 後守門)**:確定性 50 題(seed=42 + 題集 sha 入 detail,A-32 可重現)同打兩端,pgvector 參照端謂詞完全鏡射 export 的 CLEAN 口徑(`corpus.clean_item_sql`,否則假對帳),量 top-10 `sent_id` 重疊率,門檻卡 `mean_overlap ≥ 0.90`(`:74,94`),passed 落 `vectorstore_shadow_eval` 一列才允許 UPDATE config 切後端。pgvector 永遠是 SSOT(雙庫鐵則),影子只驗「可拋棄外部索引忠實鏡射」。
- **`resolve_escalation.py --watch`(delib-watch,07-11 加入)**:殭屍 session + 人裁積壓警示,設計為 **warn-only 恆回 0**(`resolve_escalation.py:69`),機械保證即使殭屍/積壓也不把 daily_green 判紅——警示不擋綠(#21)。

選配 `--with-benchmark` 再追加 deliberation 基準快檢(`benchmark_deliberation.py`,qwen3:4b、每類 2 題,`daily_green.py:44-45`)。四驗證器全走本地零 Claude token(`--no-llm`/純 SQL/mock),呼應 #28。影子端另有世代一致不變式:讀端須斷言 `config.embed_model == embedspec` 世代,不一致 fail-loud 拒服務(憲章 v1.40.0、`migrate_vectorstore_config_ddl --verify`)。

`daily_green` 標榜全程零外部 API、零市場資料,與 `daily_maintenance`(吃 FinMind)嚴格分離。排程 `augur-green.timer`(每日 07:30)**只寫在 docstring**(`daily_green.py:16`)、從未入 git;當前換機後機器上未安裝任何 augur systemd unit、qdrant(6333)/ollama(11434)兩埠皆未 listen——green 迴路目前**休眠**(shadow 步驟需 6333、`--with-benchmark` 需 11434,現在會直接 FAIL),見〈陷阱〉。

### audit_selfheal.sh v2:市場對帳自療迴路 + 45 分看門狗

這是市場資料對帳/增量的自療背景循環(07-13 入 repo,舊機只在本機、不隨遷移),`cd $(dirname $0)` 使其隨 repo 走、任何 clone 直跑。三段機制:

- **外圈=最小 IP 探測放量**:#25 單股 2330、單日 2026-07-09、`max_retries=0`(`audit_selfheal.sh:11-20`)→ IP 健康才背景啟 `daily_maintenance.py --audit-since 2026-06-01`(先 `sync_all_by_date` 市場增量再 reconcile,吃 FinMind、易 IP ban、須與其他 FinMind 作業互斥)→ 中斷/卡死或探測仍拒就休 30 分回探測(`sleep 1800`,`:45`),至綠(哨兵句「✓ audit 完成(rc=0)」`:38`)或 **48 輪**封頂後停止交人工介入(`:47`)。DB-driven resume 讓重跑冪等快轉已對帳段。
- **內圈=log 停滯看門狗(v2 核心新增)**:放量期間每 300s 檢查 `~/audit_retry.log` 的 mtime,靜默 `>2700s`(45 分)判卡死 → SIGTERM → `sleep 5` → SIGKILL(`:27-35`)。動因是 07-13 實證:audit 對帳段 API 讀無效 timeout 掛 **9h**(`poll_schedule_timeout`、`/proc rchar=0`,進程活著但 log 靜默 ≠ 在跑,HANDOFF.md:115)。看門狗以「共享 log mtime 靜默」當存活 proxy,只對「完全無輸出的 hang」有效。
- **throttle**:用 `finmind.py` SSOT `MIN_INTERVAL=0.9`(`:23-24`、`finmind.py:38`),已移除 committed 的換機保守 2.0 覆蓋(#27 爬坡,換機後實證額度 204/6000 充裕 + `quota_gate` 第二層保護、≈2.2x 加速)——此改動**尚未 commit**,工作樹目前 `M audit_selfheal.sh`;當前背景 PID 6804 正跑此 0.9 版。

注意 v1 未入 git(舊機本地未 commit),「v1→v2」僅 docstring/commit 訊息自述、無法 git-diff(未親驗)。此循環 `nohup flock -n /tmp/augur_audit.lock` 起,對用戶介面不可見,故須 TaskCreate 登記(#21 背景作業可見)。

### 機械閘與不變式速覽

| 不變式 | 機制 / 出處 | 種類 |
|---|---|---|
| fast-forward-only:非 main / 髒樹 / 分岔皆 exit 1,絕不 merge/rebase/reset | `sync_from_github.sh:18-25,41-52` | bash 機械閘 |
| DB 覆蓋須明示授權:已存在庫無 `--force` exit 1;`--force` 才 terminate+DROP | `import_database.sh:93,102-103` | bash 機械閘 #6 |
| HNSW 完整性斷言:`USING hnsw` 索引 <3 印警告;live DB 實測=3(chunk/lex/sent) | `import_database.sh:168,172` | 執行後驗證閘 |
| restore 不毀資料:只對「兩邊都有且內容不同」先 timestamped 備份再覆蓋,活端獨有檔保留不刪 | `sync_memory.py:103-120` | Python 機械閘 #6 |
| audit log 停滯看門狗:mtime age>2700s(45min)即 kill+kill -9;外圈 48 輪封頂 | `audit_selfheal.sh:10,27-35` | bash watchdog |
| 索引段記憶體護欄:`IDX_MEM×2 < RAM−shared_buffers`(靠 `-j2` 低並發落實) | `import_database.sh:134` | 文件護欄(建議式) |
| 個別可執行:`import _bootstrap` 插 `src/` 進 path,172/174 採用 | `_bootstrap.py:9-11` | Python path 墊片 #29a |
| 任一子驗證器 exit≠0 → daily_green exit 1;delib-watch warn-only 恆回 0(不擋綠) | `daily_green.py:53-57`、`resolve_escalation.py:69` | exit code 契約 A-31 |
| 暢通不變式:煙測綠=暢通、破=管線債修復優先於擴容(強制點=smoke `all(ok)`) | 憲章 v1.40.0;`verify_knowledge_e2e_smoke.py` | 每日機械綠檢 |

### 陷阱

- **五件組 ROOT 推導兩軌矛盾**:`resume_project.sh:12`/`import_database.sh:19` 用 `dirname BASH_SOURCE`(可搬)、`audit_selfheal.sh:8` 用 `cd $(dirname $0)`(可搬),但 `sync_from_github.sh:6` 與 `start_chat.sh:6` **硬寫 `ROOT=$HOME/project/augur`**。故 clone 到非標準路徑時,`resume_project.sh` 一鍵鏈會在它呼叫的 `sync_from_github.sh` 這支斷掉(`resume_project.sh:38` 以 `$ROOT/sync_from_github.sh` 呼叫、後者內部又 cd 回硬寫路徑)。
- **memory 路徑 mangle 非「任何 clone 路徑皆對」**(更正 reader 過度宣稱):機制對「當前無 `.` 的路徑」正確,但 `sync_memory.py:32` 只 `.replace("/","-")`,而 Claude Code 的目錄命名把 `.`(及可能其他非字母數字)也一併換成 `-`(同機 `~/.claude/projects/` 內 `…-stock-backend--claude-worktrees-…` 即證:`/.claude` 段被 mangle 成 `--claude`)。故 clone 到含 `.` 的路徑(如 worktree `.claude-worktrees/…`)時,推導出的 memory 目錄會與 Claude 實際目錄**分岔、指向不存在的錯目錄**,restore/export 失效。
- **「補跑 13 支 migrate」文件數字過時**(更正):過時的「13 支」**只存在於 `import_database.sh:16`**(由 commit 76cce6c 引入);`ls scripts/migrate_*_ddl.py` 實測 **25 支**,但 loop 是 glob 驅動(`:158` `for m in .../migrate_*_ddl.py`)故功能無誤(跑全部),純屬文件數字過時。a59423b 收官 commit 訊息**從未提及** migrate 支數(reader 把「13 支」歸給 a59423b 訊息屬誤植)。
- **`augur-green.timer` 不隨 repo 遷移**:全 git 歷史查無任何 `*.service`/`*.timer`,timer 純為 docstring 建議、當前機器未安裝(`systemctl --user list-unit-files | grep augur` 空、`~/.config/systemd/user` 不存在)。無 CI 意味**換機後若忘了重裝 timer,健康閘會靜默不跑而無人知**。目前機器上唯一活著的 augur 迴路是 audit_selfheal(pgrep 確認無 green-loop 進程)。
- **`daily_green.py:55` 潛在 IndexError**:若某失敗步驟 stdout+stderr 全空,`(r.stdout+r.stderr).strip().splitlines()[-1]` 會拋 IndexError → daily_green 自身崩潰而非乾淨回報 FAIL。實務上子腳本恆有輸出故未觸發,但屬真實脆弱點。
- **影子門檻 MEAN-only**:`passed = mean_ov >= threshold`(`verify_qdrant_shadow.py:74`)只看 mean、`min_overlap` 只記錄不設閘。實測 `vectorstore_shadow_eval` 2026-07-12 15:46 `mean=0.912` 但 `min_overlap=0.2`、`passed=t`——極端退化的單題不會擋 cutover。
- **看門狗 liveness proxy 的盲區**:以 log mtime 靜默判卡死,只對「完全無輸出的 hang」有效;若卡死狀態仍偶爾吐字就不觸發,且某合法長步驟(>45min)不吐 log 但實際在進展會被誤殺——這是針對 9h I/O 卡死調校的啟發式權衡、非通用 hang 偵測(audit 逐日對帳高頻 log + `PYTHONUNBUFFERED=1` 讓誤殺風險低但非零)。
- **HANDOFF.md 標頭版號略舊**:`HANDOFF.md:20,120` 仍寫 `CLAUDE.md（v1.25）`、快照時點 07-12,而現況已 v1.27、已有 07-13 commit(c7656ac/a59423b);`read_handoff.py` 直吐 HANDOFF 全文,新機讀到的版本號會偏舊(HANDOFF 自帶「HEAD 之後會前進、以 git log 為準」caveat 緩解)。

### 07-10(v3)之後的變化

- **整個子系統對 v3 是空白區**:v3 報告 grep `resume_project`/`sync_memory`/`import_database`/`audit_selfheal`/`_bootstrap`/`daily_green`/常綠/看門狗/systemd 全數 0 命中。五件組雖於 07-10(76cce6c/b011099)同期落地,但 v3 報告本身未把它們寫進去。
- **常綠三支核心其實晚於 v3 凍結時刻**:e2e 主計畫報告狀態行(commit 24e87a3,07-10 18:40)寫「P7 未動」,但 `daily_green.py` + `verify_knowledge_e2e_smoke.py` + `verify_qdrant_shadow.py` 於同晚更後的 9b32a8b(07-10 20:46「P1-P7 全竣工」)才首次加入(`verify_advisor_regression.py` 已在 24e87a3 交付)。
- **07-11(455e009)**:daily_green 新增 delib-watch 步驟(本地審議引擎整合進常綠)。**07-12(5edc549)**:smoke 新增 K1 橋斷言。
- **cutover 已實際發生**:`knowledge_vectorstore_config` 的 `sentence_items` 已切 `qdrant_server`(其餘 lexicon/philosophy_chunk/sentence_works 仍 pgvector),shadow eval 07-11/07-12 多次 `passed=t`——`verify_qdrant_shadow` 已從「cutover 前門檻」轉為「cutover 後守門」。**`prediction_probability` 已由空轉非空**(實測 1695 列)→ regression 機率斷言已自動 SKIP→HARD,逐值等同 + 四標記 + 判死硬綁現已生效強制(不等同當前通過)。
- **07-13 兩件實質收官**:(1) `import_database.sh` 分階段還原強化(a59423b)——data 段 `-j4`/索引段 `-j2`+`IDX_MEM` 2GB、完整 log 不再 `tail -5` 吞錯、smoke 加 HNSW≥3 斷言,修 07-13 匯入 HNSW `maintenance_work_mem` 不足卡 70 分實證;(2) `audit_selfheal.sh` v2 看門狗**首次入 repo**(c7656ac),補上舊機 runner「不隨機器遷移」的缺口,45 分 log 停滯自動殺,修同日 9h 無聲卡死實證。同期治權升版 CLAUDE.md v1.25→v1.27:#21 升「背景作業一律 TaskCreate 登記進可見清單」、#28 加模型檔位分派表(Fable5/Opus4.8/Sonnet5)。
- **換機現實(07-13 WSL2 新機)**:systemd 可用(PID1 systemd 255)但無任何 augur unit 安裝、qdrant/ollama 未啟——green 迴路休眠,唯 audit_selfheal 正在跑(nohup+flock 手動起,ps 確認 `daily_maintenance --audit-since 2026-06-01` 活著、log 持續增長)。

---

## §7 跨系統 meta-patterns（建構房規，v4 增補版）

v3 §6 列 10 條房規；本輪 4 鏡頭實證後**新增/擴張 7 條**（每條 ≥2 跨子系統實例、皆 code/DB 親驗）：

1. **preregister-then-run（先凍後跑）——最跨子系統的最高階房規**：跑任何 OOS 數字前把「怎樣才算過」寫死＋`criteria_sha` 覆算偵測挪門柱。三處同構：解凍 gate（preregister_unfreeze_gate.py:1-12）、方向 gate（preregister_direction_gate.py:2-9，挪門柱=trigger 機械拒）、擂台（MDE/檢定力機械凍入 criteria、候選 `code_sha/weights_hash/frozen_at`）。
2. **誠實終態（fulltext_blocked/never_shown）**：做不到＝落終態帳「被擋非漏做」＋下輪排除收斂。知識層 `knowledge_fulltext_status`（skip_no_oa 11,184/skip_license 3,274/skip_pdf 976/skip_fetch_error 913/skip_short 186/skip_ctype 17）；方向 GATE `never_shown` 判死留檔（evaluate_direction_gate.py:202、serve_probability_ui.py:251,283）。
3. **resume-safe 冪等（帳本＋冪等鍵＋FOR UPDATE 取工）**：審議 ledger.py:115-175（同 idempotency_key 回既有 run、kill 殘留 reset、單機單工）；知識 `knowledge_harvest_log`/`knowledge_embed_ledger`；audit DB-driven resume；預測 `revalidation_ledger`/`trial_ledger`。
4. **零 usage 本地工具**：接續五工具（CLAUDE #31）＋本地審議引擎（deliberate.py:3-6「弱模型只需會提可驗證問題、判對判錯交給誠實工具」）——#28「本地為主、Claude 為輔」的機械落地。
5. **人裁 gate（hugo 親簽、AI fail-closed）**：GATE approve 唯人（TTY 閘）、DB 親驗 direction_gate 全 approved 列 approved_by=hugo；審議 undecidable/治權觸線→`escalated` 人裁佇列（verifiers.py:150-178、redlines.py:1-7）。
6. **取代式 STATE（07-13 新）**：現況每封存點整段重寫、歷史交給 git（HANDOFF §4、commit ddd4821）；同哲學＝治權檔「憲法只記現行法律」、程式標頭不寫修訂史（CLAUDE #18）。
7. **plan-first＋對抗審查（結晶為房規）**：規劃類工作先產計畫書（reports/ 45+ 份 `*_plan_*.md`）＋用戶拍板才實作；高風險門檻才多 agent 對抗審查（實例：輸出契約 18afc31 Opus 4.8 4-blocker、K 計畫 5005f10 三視角）——SSOT＝憲章第六部/CLAUDE #20。
8. **watchdog 自癒（07-13 新運維房規）**：長跑配「log 停滯偵測」而非只有存活偵測——「進程活著＋log 靜默≠在跑」（audit 掛 9h 實證）；audit_selfheal.sh v2 內建 45 分靜默自動殺＋續跑。

v3 已列且本輪再驗成立的：fail-closed 機械閘（新實例：審議 engine_config「表缺列→全關快路」、O1 生產器、PDF 五道品質閘）、DB-driven config #29b（大幅擴張：knowledge_source 3,601/knowledge_query 4,709/topic_alias 36/risk_policy 6 列、全文解析三策略住 adapter_config〔策略位址已定；本機 07-12 dump 該欄 NULL、資料在原機，見 §4.1〕、審議快路開關、advisor 拒答句全 DB 驅動）、single-writer 機械鎖（新實例：verifiers.verify_claim=全系統唯一能寫 confirmed 的地方）、EAV 窄長表（feature_values 四欄 250 萬列；knowledge_staging payload jsonb）、命名慣例 screaming/DDD（全 package 一致抽查成立）。

## §8 端到端兩個故事（v4 更新版）

### §8.1 預測流：raw → arena（時點鏈逐跳）

`FinMind/FRED →(三層限速+by-date 對帳)→ raw 84 表 →(generic_schema 建表+catalog 登錄)→ panel.build_panel(全 SQL date<=panel_date 純後向;月營收 revenue_released 15 日 gate、財報 financial_released 45/90 日、集保 holdings_visible_cutoff=panel−7、recency>45 日整股丟棄) → feature_values(EAV) → build_universe_asof(逐 t 只看 ≤t,sub=pds[:i+1],core_gate.py:217-219,消 survivorship) → train_ranker(walkforward embargo 下界 h+62td,H≥252 禁入) → prediction_values(panel_date 為 as-of 錨) → 驗證 harness(E 帳本/deflation/R 軌) → arena(預註冊對局)`。
**#8 是多跳縱深**、每跳有獨立時點欄，非單一 gate。release_lag 四常數（15/45/90/7 日）皆法定公告期限＝法律事實非知識閾值（release_lag.py:28-32）；審計 1A（集保週五快照洩漏）修復已 commit 進 HEAD（release_lag.py:57-66）。

### §8.2 顧問流：來源 → 誠實回答（license 鏈逐跳）

`knowledge_source(3,601 列 registry,approval_status 閘) →(acquire)→ knowledge_staging(302,650 列,pending;staging_source_gate trigger 擋非 active 來源)→(promote 人審)→ knowledge_item(254,176 metadata) →(fetch_fulltext,憲章全文准入三軌 license-gate)→ knowledge_item_text(151,811)/philosophy_work_text(31,782) →(build_sentences)→ knowledge_sentence(1,756,817)/philosophy_chunk(126,609) →(embed,e5-small)→ sentence_embedding(1,696,984≈96.6%)/chunk_embedding(126,609=1:1) →(retrieve+guard)→ advisor →(oai_compat,scope fail-closed)→ chat UI`。
顧問流時點欄＝payload.as_of 快照凍結；拒答句/方向誠實句 DB 驅動（direction_gate 為 SSOT、DB 例外退 hardcode 句不消失）。

### §8.3 兩流交界的 latent 埋雷（本輪確認仍在）

macro：`fred_series` PK 含 realtime_start（vintage PIT 結構就緒），但**無 PIT reader**（repo 無 macro_vintage.py）、Tier B「realtime_start<=panel 濾版」只活在 docstring 零程式強制；因 feature_values 35 特徵**零 macro 消費者**故不爆。觸發條件＝任何 macro 特徵接入前**必須先落 PIT reader**（順序不可反，否則沉默洩漏）。

## §9 治權 → code enforcement wiring 表（v4 更新版）

| 治權強制宣稱 | 機械落點 | 現況（07-13 親驗）|
|---|---|---|
| #1 零 AI 幻像入庫 | DB CHECK `<>'ai_generated'` ×3（item_text/philosophy source/work）＋guard 數字白名單（guard.py:56）＋引文逐字閘（:50）| ✓ live |
| #8 素養→預測單向 | AST 八道掃描（import_isolation）＋predict role GRANT | AST ✓ 0 violations；role **applied-but-connection-unwired** |
| #11 提拔關卡 | `metrics.effective_t_hac`（Newey-West HAC，metrics.py:89）| ✓ |
| #15 誠實固定句閉集 | guard.HONESTY_CLOSED_SET 僅二句、與憲章:159 逐字一致（guard.py:15-20）＋空檢索閘（:137/142）| ✓ |
| 輸出契約 v1.45.0 fail-closed | `trg_dirprob_gate_guard`/`trg_ddirprob_gate_guard` BEFORE trigger、非 evaluated_pass 一律 RAISE | ✓ **armed-and-dormant**（方向產物表物理 0 列）——07-10 後從 COMMENT 升級為真 trigger |
| 挪門柱禁止 | `trg_direction_no_goalpost`/`trg_unfreeze_no_goalpost`（狀態機白名單+終態凍結）| ✓ |
| 擂台凍結/不可改/不回填 | `trg_arena_candidate_frozen`/`trg_arena_pred_immutable`/`trg_arena_pred_no_backfill` | ✓ |
| 知識來源人審准入 | `staging_source_gate` BEFORE INSERT | ✓ |
| owned_local 私有軌 | **`chk_itext_owned_local_private` 跨欄 CHECK 已存在**＋license 白名單含 owned_local | ✓ 但 ⚠ 反向 SSOT 漂移：CHECK 只活在 live DB、無任何遷移建它＝clean-room 重建不重現（違 #12，見 §3.2/§11）|
| 治權宣稱強制人裁 | redlines.consult（ledger.py:38 已接線）| ⚠ **斷線**：`deliberation_redline_trigger` 的 3 個 pattern 釘死舊版檔名（v1.5.0/v1.8.0/`_v%`），Python 子字串比對對現行三大治權檔全 MISS——僅 CLAUDE.md/README 命中。修法＝UPDATE 3 列為版本無關前綴 |
| prediction_values 禁回讀當特徵 | 僅 DDL COMMENT（migrate_prediction_ddl.py:61-62）| ⚠ v3 REFUTED#2 **今日仍成立**（無機械閘）|

## §10 關鍵常數／魔數／不變式速查（起草者逐節回報彙整）

### §10·1 治權層（10 條）
- 治權檔數=5 — clean-room #16 明列靈魂/原則精華/憲章/CLAUDE.md/README(docs/原則精華_v1.9.0.md:143);另加HANDOFF共6份接續文件、HANDOFF為跨機接續SSOT非法律檔
- 憲章規模=380行·47版修訂歷程·僅v1.45.0為ACTIVE其餘46 SUPERSEDED — grep-cE '^| v[0-9]'=47、grep-c ACTIVE=1(docs/系統架構大憲章_v1.45.0.md:380)
- 反膨脹紀律=永守「30分鐘讀懂全系統法律」 — 憲章全文出現12次「30分鐘」(grep-c=12);v1.22.0立修訂歷程3行封頂體例(:273)
- 原則精華連動升版≈10次 — v1.1.0~v1.6.0(#16-#20+v1.4.0)+憲章v1.9.0/v1.9.1+v1.38.0+v1.43.0(修訂歷程:335-378);v1.38.0/v1.43.0僅「既有判準實質擴展」子型最近兩次、非史上僅兩次
- as-of freeze基準=2026-05-31 — 現已解凍轉live增量維運、as-of'=滾動(docs/原則精華_v1.9.0.md:77);hardcode僅活payload.py:67/:82 demo路徑、生產取DB max(panel_date)
- unfreeze gate_id=unfreeze_06dcb178267d — 現況status=frozen|hugo未evaluate;pass前live數字不得入確立級宣稱(docs/原則精華_v1.9.0.md:77 + DB)
- 輸出契約fail-closed=gate須evaluated_pass否則RAISE EXCEPTION — trg_dirprob_gate_guard/trg_ddirprob_gate_guard(函式direction_product_gate_guard字面引憲章v1.45.0);現0門pass→direction_probability零列
- direction_probability七承載欄=expected_ret/hit_rate/p_up/econ_verdict/base_rate/calibrator_id/gate_id — 對映輸出契約三產物+誠實硬綁(DB information_schema.columns)
- 方向軸十門全evaluated_fail|hugo親簽 — dgate_H_20/40/82/120+D_1/D_5+4個v2變體(H_20/40/82_v2,D_5_v2;無H_120_v2/D_1_v2)(DB direction_gate)
- 預測隔離不變式=7 pkg(features/models/universe/evaluation/ingestion/audit/catalog)零import FORBIDDEN 3 pkg(philosophy/advisor/knowledge) — import_isolation.py:31/:33 + tests/test_philosophy_isolation.py AST斷言

### §10·3.1 ingestion+raw（10 條）
- MIN_INTERVAL=0.9 — FinMind start rate 唯一 SSOT，2026-07-12 起 env FINMIND_MIN_INTERVAL 可覆蓋、預設不變；降並發無效（start rate 受 _pace 約束、非並發數）(finmind.py:38)
- QUOTA_COOLDOWN=1800 — 403 額度耗盡/IP 限流之固定冷卻秒數，不短退避反覆撞防惡化成 sustained ban(finmind.py:41)
- QUOTA_HEADROOM=200 / QUOTA_METER_EVERY=120 — 額度閘暫停閾值(limit−200)與讀權威錶 /user_info 頻率(每120 call)(finmind.py:47-48)
- PER_STOCK_WORKERS=32 — 逐股 fetch 並發數，只改並發不改 start rate(sync.py:38)
- _RETRY_STATUS=(402,429,403,500,502,503,504) — 可重試碼集；422 刻意排除以便 list_datasets 拿 dataset enum(finmind.py:53)
- fred_series PK=(series_id,date,realtime_start) — vintage 多版 PIT 防 ON CONFLICT 塌版；_fred_pk_ok 落地前守門(ingest.py:103-127)；DB 343,967 列/31 series/9 Tier B
- FACTOR_TOL=0.995 — PriceAdj factor=adj/raw 回落 >0.5% 即判除息拼接損傷；既是偵測閘也是修後驗證閘(repair_priceadj_basis.py:25)
- INTRADAY=8 表 / OUT_OF_UNIT=3 表 / BACKFILL_DEFERRED=frozenset()(空集、分支 dead) — 落地排除集(ingest.py:22-42)
- type_caveat=45 欄 / dirty_value_note=23 欄 / anti_leakage_note=3 表 — 語意/髒值/as-of 判準落地的 DB SSOT(column_catalog + dataset_catalog)
- #7 attestation pass ⟺ value_mismatch=0 ∧ extra_in_db=0 ∧ 非 incomplete；抓取失敗即 incomplete、verdict 不 pass(reconcile.py:404-413)

### §10·3.2 core/catalog/DDL（10 條）
- VARCHAR_LEN=255 — 字串下限 VARCHAR(255)、maxlen>255→TEXT（generic_schema.py:33）
- NUMERIC(20,6)=NUMERIC_PRECISION=20 / NUMERIC_SCALE=6 — API 數字下限、超出自動加大只擴不縮（generic_schema.py:34-35）
- connect_timeout=10 — psycopg2 連線逾時秒數（db.py:29）
- page_size=1000 — execute_values upsert 批次頁大小（generic_schema.py:267）
- _NULL=('','none','null','nan','nat') — 取樣/主鍵判定/寫入三處共用的 NULL 語意集合（generic_schema.py:58）
- MIN_COOC_BRIDGE=30 ⇔ cooc_sents>=30 — knowhow 橋最小共現分母閘、schema 為 SSOT 同值雙寫（build_field_knowledge_bridge.py:24 / migrate_knowhow_bridge_ddl.py:50）
- horizon∈{20,40,60,82,120} — 機率/方向層 CHECK 閉集鎖 horizon vocabulary（migrate_probability_ddl.py:81 econ_verdict_rule seed）
- N_PARTITIONS=16 — knowledge_concordance HASH 分區數、以迴圈建（migrate_text_understanding_ddl.py:36,266-268）
- QUOTA_EXPIRY='2026-06-24' — sponsor-only 抓法配額到期硬編值、今 07-13 已過期（catalog；DB quota_expiry 全為此值）
- arena pred_date >= 台北今日−1 — 擂台反回填鎖、早於即 RAISE 保證真未來（migrate_direction_arena_ddl.py:97-99）

### §10·3.3 features+工具鏈（9 條）
- feature_values 規模 = 35 distinct 特徵 / 2,510,040 列 / 36 panel(2007-12-31~2026-06-30) / 3093 檔 — 生產特徵層現況(DB 實查)
- value NUMERIC(20,6) NOT NULL + PK(panel_date,stock_id,feature) — EAV 型別/唯一性由 DB 強制、ON CONFLICT DO UPDATE 冪等(panel.py:36-43)
- CANONICAL_START='2008-12-31' → canonical 交集 = 29(非 feature_values 的 35 distinct) — 模型實際特徵集起點(baseline.py:30-44)
- _MAX_STALENESS_DAYS=14 — E 類真零 _table_covers 近端容忍(源自實測 3 表相鄰事件日 gap max=13;chip.py:45)
- MAX_STALE_CALENDAR_DAYS=45 — 還原價 master recency gate,最近價距 panel>45 日整股缺列(panel.py:35)
- REVENUE_DAY=15 / FIN_LAG_QUARTER=45 / FIN_LAG_ANNUAL=90 為法定公告期限;HOLDINGS_LAG_DAYS=7 為 TDCC 無發布日欄之保守審計近似 — #8 發布日 gate(release_lag.py:28-31)
- MIN_QUARTERS=8 / MAX_STALE_DAYS=400 — 毛利循環自身百分位窗 + #15 陳舊守衛(margin_cycle.py:25-26)
- |HAC-t|≥2(Newey-West Bartlett,metrics.py:89) + COST=0.00585(台股來回成本,verify_economic_candidate.py:26) — 提拔顯著性機械閘 + 經濟終關成本
- feature_candidate_values 現 0 列;生產交互唯一 inter_fh_x_p10yr(opt-in、限 374 宇宙、換寬宇宙 ΔIC −0.0005) — 全鏈飽和實證(cross_section.py:17-24 + DB 查)

### §10·3.4 universe/models/登錄（9 條）
- required = 完整度分母 = 市場實際可算之 (panel,feature) distinct 組合數，非 len(panel)×len(feat)；結構性缺格不計、差額存 absent_combos（core_gate.py:120-125）
- liquidity_pct=25 → threshold=14.929 — 部署 asof 宇宙的 P25 流動性下界，取 latest panel 之 dollar_volume_log_20d percentile_cont（core_universe_build_meta，core_gate.py:131-135）
- ETF_INDUSTRY=505 檔 / FINANCIAL_INDUSTRIES=('金融保險','金融業') — 候選空間排 ETF + monthly_revenue_yoy 之豁免產業（core_gate.py:72）
- feats_hash = sha256("\n".join(sorted(feats)))[:16] — 順序無關的特徵集口徑鎖，內嵌進 model_id（artifact.py:18-20、train_ranker.py:70）
- model_family_chk = 9 族白名單 {RankRidge,RankGBDT,MktLogit,DirStack,DailyLogit,DailyGBDT,DailyGBDT_cal,MktGBDT,DirStackM} — 非白名單族 INSERT 被 DB 拒（migrate_prediction_ddl.py:37-45）
- risk_policy = H60/H120 × {dd_circuit=-0.20/-0.25, max_position=0.10, turnover_budget=0.75}，共 seed 6 列；policy_key DB CHECK 鎖三鍵（migrate_risk_policy_ddl.py）
- H_FORBIDDEN=252 禁入訓練 — train_ranker.py:99 horizon==252 即中止（結構洩漏 embargo=4）
- core_count=344（asof 2026-05-31）；PIT 序列端點 714(2014-12-31)→344(2026-05-31)，整體下降但非單調（core_universe_asof=28 as_of × 12394 列）
- 部署兩代 feats_hash：ce62866(28 特徵，disk 僅存 4 檔) vs 3a4e66fae(29 特徵，+gross_margin_pctile，實際部署但 5 個 joblib 在本機缺席)

### §10·3.5 evaluation（8 條）
- _FEATURE_LAG_TD=62 交易日 — 特徵最大滯後(年報法定90日≈62td);embargo 保證下界=h+62(src/augur/evaluation/walkforward.py:17)
- _H_FORBIDDEN=252 — H≥252 禁入 walk-forward 之執行期硬閘 raise ValueError(src/augur/evaluation/walkforward.py:18,48-49)
- CANONICAL_START='2008-12-31' — 交集 gate 覆蓋起點,07-11 hugo 親簽新增;使 canonical 特徵集 28→29(src/augur/evaluation/baseline.py:30)
- canonical 交集=29 特徵(hash 3a4e66fa) — SQL:交集(panel≥2008-12-31)=29 vs 全panel=28,差=gross_margin_pctile(baseline.py:37-45,commit d973b81)
- COST_TW=0.00585 — 台股來回成本≈0.585%,但非 evaluation 模組常數、散落>10 script各自定義;run_backtest 預設 cost=0.0(portfolio.py:81)
- HORIZONS=(5,20,60,252) — label 4 個 forward horizon,但 252 與 walkforward h≥252 raise 未對齊(src/augur/evaluation/label.py:22)
- _EULER_GAMMA=0.5772156649 — DSR SR_0 期望最大值(式5)近似需之 Euler-Mascheroni γ(src/augur/evaluation/metrics.py:19)
- HAC lag=floor(4·(n/100)^(2/9)) — Newey-West Bartlett 核經驗滯後(lag=None 時);LRV=γ0+2·Σ(1−l/(L+1))·γ_l(metrics.py:103-107)

### §10·3.6 audit（10 條）
- PIPELINE = ('features','models','universe','evaluation','ingestion','audit','catalog') — 受隔離約束的預測 7 package(import_isolation.py:31)
- FORBIDDEN = ('augur.philosophy','augur.advisor','augur.knowledge') — 預測管線 AST 禁 import 的素養層前綴(import_isolation.py:33)
- check_isolation() 掃描道數 = 8 — import + rbac/chat/distill/deliberation/bridge 五道字面 + 對位 + scripts 洩漏面(import_isolation.py:169-178;更正 v3「七道」)
- FORBIDDEN_PREFIXES = ('philosophy_','knowledge_','advisor_distill_') — DB 動態閘 REVOKE 素養層前綴;未含 deliberation_/field_ 故 divergence(setup_predict_role.py:32)
- augur_predict FORBIDDEN 覆蓋表數 = 78 — live REVOKE 素養層表數(DB 查詢;v3 記 62、隨表增長)
- verdict.passed = value_mismatch==0 ∧ extra_in_db==0 ∧ not incomplete — 三-clause fail-closed attestation(reconcile.py:413)
- COVERAGE_MISS_TOL = 0.2 — coverage 對帳用列數量級比、容忍去重/時序差(reconcile.py:34)
- MIN_OBS = 60 — 一對欄位至少 60 共同非空 obs 才寫相關(field_correlation.py:24)
- CANDIDATES = 4 個硬編實驗候選(pb_xsec_rank/pb_industry_demean/pb_self_pctile_252d/inst_govbank_divergence) — feature_candidate.py:30
- five_mirror drop? 門檻 = weak_shap ∧ weak_ic ∧ ablation_safe(ic_floor=0.02, shap_quantile=0.1) — 三條件 AND、無單一指標判生死(feature_diagnostics.py:98-125)

### §10·3.7 驗證harness+出單（9 條）
- FREEZE='2026-05-31' — 解凍 GATE/evaluate 硬寫凍結日,07-12 解凍後未更新致守門4 拒跑分支失效 (preregister_unfreeze_gate.py:33)
- top_frac=0.1 — 出單 top-decile long 選股比例,339 股取 33 檔 in_portfolio (predict_asof.py:104,190)
- COST_TW=0.00585 — 台股單邊成本,散落多支非 evaluation 常數;run_backtest cost 預設 0.0 忘傳則 net==gross (predict_asof.py:37)
- dsr_lo>=0.95 — DSR 保守下界(混頻大 N)過門才判統計確立,禁樂觀小 N 灌水 (deflate_headline_verdict.py:135)
- criteria_sha=sha256(sort_keys)[:16] — 解凍 GATE 判準凍結指紋,非 draft 後漂移即 trigger RAISE (preregister_unfreeze_gate.py:44-46)
- p_beat_median∈(0,1) 開區間 — 相對機率 DB CHECK,越界值進不了庫;horizon IN(20,40,60,82,120) (migrate_probability_ddl.py:79)
- statement_timeout='60s' — verify sql check 唯讀交易上限,結果須單列單欄 boolean 否則標 red (verify_validation_evidence.py:40,50)
- R_robust 5 policies — calib_late_skill_floor=0/ece_ceiling=0.05/rank_autocorr_annotate=0.3/lofo_signflip=0/subset_sign_agree=0.75,全 frozen (judgestop_threshold)
- trial_ledger=32 列/4 horizon 各 8 — deflate 之試驗數 N 機械來源,禁人手填 (deflate_headline_verdict.py:84-86)

### §10·3.8 方向軸（10 條）
- criteria_sha = sha256 前 16 碼 — 挪門柱凍結指紋,approved 後任一改即 RAISE(migrate_direction_gate_ddl.py:52-54)
- 10 門結局 = v1 六門+v2 四門全 evaluated_fail/never_shown/approved_by=hugo — 二次證偽,無一過關(live DB direction_gate)
- dgate_D_5 v1 p=.03813 → v2 修 champion+purge 後 dgate_D_5_v2 p=.07193 — 唯一近失退回不過關(result_snapshot 覆算)
- dgate_D_5_v2 Brier=.25389 vs 基線≈.25 — Brier 天花板在基率附近,ECE 全過=誠實無訊號
- FREEZE=2026-05-31 — MC 模擬 as-of 上界,純歷史重抽僅用 ≤as-of(simulate_mc_paths.py:31)
- MC 模擬 = n_paths 10000 / BLOCK_LEN 21td / HIST_WINDOW_TD 756 / 雙法 iid+block bootstrap / 零 tilt(simulate_mc_paths.py:33-35)
- 反回填鎖閾值 = 台北今日−1,pred_date 早於即 RAISE(migrate_direction_arena_ddl.py:99-100)
- arena α = Bonferroni 0.05/K 跨家族多重性凍入 criteria;H120 n=35→review_observation_only cap(preregister_direction_gate.py:60-62)
- ECE ceiling 讀 judgestop_threshold.calib_late_ece_ceiling frozen 列,不寫死(evaluate_direction_gate.py:184)
- E[r] 閉式 = (2·hit−1)·vol − cost(produce_direction_probability.py:104)

### §10·3.9 擂台+三鏡頭（10 條）
- futility_min_clusters=60 / futility_z=1.645 — futility 判停閾值(frozen=t;direction_arena_policy;照 D 軌日頻校準)
- A2 α=0.05/6=0.00833 · A3 α=0.05/3=0.01667 — 各家族 Bonferroni(preregister_direction_gate.py:195/252)
- 19 門 = v1 六門+v2 四門+A2 六門+A3 三門 — 跨家族全序列揭露總數(preregister_direction_gate.py:254;憲章 v1.45.0)
- OwnThreelensInteract SEEDS=(7,42,2026) — HistGBM 3-seed+isotonic(adapters.py:318)
- FACTOR_TOL=0.005 / UNSETTLE_GAP_DAYS=30 — 結算 factor 回落容忍與停牌上限日(settle_arena_labels.py:34-35)
- 市場模型轉換極值 p=0.95(last<=qe[0]) / p=0.05(last>=qe[-1]) — Chronos/TimesFM 同口徑分位插值近似(adapters.py:302-305)
- 44 特徵 = 35 基礎 + 9 交互(INTERACT_PAIRS) — 113 panel×44=2,229,083 值(含 461,882 交互值);窗 2017-01-24→2026-05-29
- 反回填閾 pred_date >= 台北今日−1 — arena_pred_no_backfill trigger 真未來機械保證(migrate_direction_arena_ddl.py:97-107)
- MDE own_stack_20:effective_n=36 / mde_power80_pp=8.41 — 預註冊機械凍入 criteria(DB power_disclosure)
- license 白名單 apache-2.0/mit + offline_only:true — 市場隊註冊四道 assert(register_arena_candidate.py:77-81)

### §10·4.1 knowledge+語意橋（9 條）
- LICENSE 三軌白名單 = {public_domain,cc-by,cc-by-sa,cc0,owned_local}(5值) — knowledge_item_text 全文准入,DB CHECK knowledge_item_text_license_check 硬擋+owned_local⟹local_private(corpus.py:17 為須同步之 Python 複本)
- fulltext_status CHECK = 6 值(skip_no_oa/skip_license/skip_pdf/skip_ctype/skip_short/skip_fetch_error) — 誠實 fulltext_blocked 終態帳,live 16,550 件 blocked(fetch_oa_fulltext.py:93-99)
- SEMANTIC_ENTITY_TYPES = (paper,report,document) — 語意層切句/嵌入/檢索 entity_type 准入集,fail-closed(corpus.py:22)
- ADAPTERS 數 = 14 — acquire 擷取引擎註冊之 adapter 數,擴來源協定才加、擴領域零 code(acquire_knowledge.py:298-305)
- MODEL_TAG = intfloat/multilingual-e5-small — 句嵌入模型,knowledge_sentence_embedding 1,696,984 列(≈96.6% 覆蓋)
- MIN_COOC_BRIDGE = 30 — 橋層最小 pair 支持度硬 CHECK,遠嚴於統計軌內部 min_cooc=5,擋稀疏假係數(build_field_knowledge_bridge.py:24 / migrate_knowhow_bridge_ddl.py:50)
- items basis_n = 10,848 — items 統計軌獨立分母(建置當時 CLEAN 句數),絕不沿用哲學 1,505,700(en)/33,319(zh)(build_items_knowhow_stats.py:78-106,#15 anti-leakage)
- harvest 重試上限 = 2 — knowledge_harvest_log 永久錯除役閘(error AND attempts<2 才重跑;429/503/timeout=temp 不累加)(harvest_knowledge.py:84,108)
- method_kind CHECK = {counting,closed_form_stat,string_rule,sql_join}(4值) — 係數種類封閉集,DB 硬擋 embedding/LLM 冒充係數(build_cross_school_stats.py:68)

### §10·4.2 philosophy（10 條）
- PIPELINE=7 package(features/models/universe/evaluation/ingestion/audit/catalog) — 預測管線集合，AST 隔離閘掃描面(import_isolation.py:31)
- FORBIDDEN=3 前綴(augur.philosophy/advisor/knowledge) — 預測管線禁 import 的素養層前綴(import_isolation.py:33)
- SEED=23 投資學派 — in-code 策展、principle→factor 假說來源(framework.py:93)；THINKERS=17 in-code 思想家(framework.py:311)
- DDL=9 表(bootstrap docstring 誤稱 6，stale) — philosophy_* 表 CREATE TABLE IF NOT EXISTS 清單(framework.py:20起)
- LICENSE_WHITELIST=5 值(public_domain/cc-by/cc-by-sa/cc0/owned_local) — 知識層 item 准入白名單(corpus.py:17)；原典全文更嚴、僅 public_domain 單軌
- clean_work_sql 閘=review_flag=false AND corpus_class='literary' — works 側 fail-closed 檢索准入，NULL 不放行(corpus.py:35)
- philosophy_work_text license 唯一值=public_domain(31782 列，DISTINCT=1) — DB 等值 CHECK 強制原典全文限公版(live 查詢 CONFIRMED)
- factor_map=42 筆／validated_ic NOT NULL=37／NULL=5(=roe/debt_ratio/piotroski_fscore/peg_ratio/macro_regime 尚未建特徵) — 假說 vs 實證分欄回填現況(live 查詢 CONFIRMED)
- philosophy_school live=44(23 investment SEED + 21 management 經 promote_knowledge 資料管線入庫) — 學派骨架已擴成一般管理學說語料(live 查詢 CONFIRMED)
- philosophy_principle status=26/26 全 untested — validated_ic 已回填但 principle 層狀態未同步(live 查詢 CONFIRMED)

### §10·4.3 嵌入/檢索（10 條）
- MODEL_TAG=intfloat/multilingual-e5-small — 全系統唯一嵌入模型（embedspec.py:15）
- MODEL_DIMS[e5-small]=384 — 向量維度，三表 embedding 皆 vector(384)（embedspec.py:16 + DB atttypmod=384）
- TEXTNORM_VER=1 — textnorm 世代版本，入 collection 名（embedspec.py）
- slug=ime5s30b1cd / sentence_items collection=kn_sent_it_ime5s30b1cd_tn1 — e5-small 確定性 slug（純函數 sha1[:6]，test_knowledge_embedspec.py:17 pin）
- PASSAGE_PREFIX='passage: '（嵌庫端 embed_knowledge.py:34）／查詢端 'query: '（retrieval.py:60）— e5 非對稱前綴機械契約
- collection 名長度預算=26、sync_scope=32 — 貼地零餘裕，超長 fail-loud（embedspec.py:45-64）
- HNSW opclass=vector_cosine_ops — pgvector 索引（embed_knowledge.py:167-168）；Qdrant hnsw_ef=256（vectorindex.py:217）
- 影子 cutover 門檻 mean_overlap≥0.90 — 只閘 mean 不閘 min（verify_qdrant_shadow.py:74）
- LICENSE_WHITELIST 5 值（public_domain/cc-by/cc-by-sa/cc0/owned_local）+ SEMANTIC_ENTITY_TYPES{paper,report,document} — items 側 CLEAN base 閘（corpus.py:17,22）
- 三粒度現量：lexicon 154,875 / sentence 1,696,984 / philosophy_chunk 126,609（2026-07-13 實查，全 e5-small）

### §10·4.4 advisor/前台/RBAC（11 條）
- pbkdf2 _ITER=240000 — identity 密碼雜湊迭代次數（≥OWASP 210k），DB 只存 sha256(token)（identity.py:20）
- 引文逐字門檻=8字 — guard 閘①：引號內 ≥8 字須逐字 ⊂ citation（guard.py:50-53）
- DP7 GATE=0.55 / S5 drop=0.40 — 蒸餾 S2 out-of-corpus 佔比下界（generate_questions.py:255-258）＋S5 per-batch 掉件率上界（validate.py:123-125）
- direction_gate=19門 — 10 evaluated_fail＋6 approved＋3 preregistered＋0 evaluated_pass，拒答句 DB 驅動即時查（prompt.py:104-122）
- RELEVANCE_FLOOR=0.30 — 已退為簽章相容/遙測、非現行相關度閘（判準改 _strong_distinctive 專詞共現，relevance.py:41/139）
- fast 參數=qwen3:8b temp0.15/num_predict900/think=False — advisor 現行單發參數凍結（R2）；think 檔 num_predict4096
- ports=8090/8399/8500/11434（＋機率 8600） — chat_ui/OpenAI 殼/admin console/Ollama，全綁 127.0.0.1
- frontend_tiers：default=augur-8b-fast、ultra.engine_model=qwen3:4b、max_concurrent=1、config_sha=950b9ab7e16b19c3 — 前台檔位操作值整列住 deliberation_engine_config（#29b）
- probe tok/s：4b=17.1 / 8b=6.7（各 n=9） — /v1/models 與 UI 唯一速度來源，effort.probe_speed 現算不硬編
- 蒸餾 pilot：303 ctx / 274 gold（teacher_model=claude-teacher-workflow）/ 171 validated，drop 37.6% — data/distill/sft_pilot2.jsonl（171 行）
- RBAC live：app_user=1 / permission_group=7 / group_domain_grant=31 / user_group=0 / knowledge_domain=41（is_authz_boundary=27；is_investment 欄 0/41 全空＝預留旗標零 code 消費，因子鏈純度實繫於 knowledge_item.domain 值本身）；erp_tiptop=150,685 段 owned_local

### §10·5 審議引擎（9 條）
- ORACLES 5-tuple = (information_schema, import_isolation, file_grep, db_query, pytest) — oracle 封閉集單一住所 (verifiers.py:30;與 assigned_verifier CHECK 閉集同錨)
- db_query statement_timeout = '30s' + BEGIN TRANSACTION READ ONLY + ROLLBACK — db_query 唯讀沙箱三件套 (verifiers.py:96-107)
- pytest oracle timeout = 120s、旗 -x -q --no-header -p no:cacheprovider、限 tests/ 沙箱 — (verifiers.py:124-126)
- GATE 三判準門檻:median acc 增量 ≥ +15pp、engine 假確認 ≤ 各臂 min、McNemar 合併 p < 0.05 — 讀自凍結快照 cfg['thresholds'] 非 code 常數 (benchmark_deliberation.py:406,418)
- GATE PASS batch = gate_43044a574c0d:engine median 100.0% vs 最佳非引擎 53.3% = +46.7pp、假確認 engine=0、McNemar p=3.64e-12 — (augur_deliberation_a5_remeasure_20260711.md:14)
- F1 單飛鎖 max_concurrent = 1(4GB VRAM 現實)— Semaphore (effort.py:110-113,130-132)
- loop-until-dry dry_k = 2(連續 2 輪無新 confirmed/refuted 才停)、panel max_rounds = 3 — (engine.py:86;critic.is_dry k=2)
- 引擎現況規模:claim 340(confirmed 202 = bound 164 + anchor-only 38;fast_path 28);escalation undecidable 102 / red_line_category 6 / no_oracle 1 — DB 實查
- deliberation_* DDL 表數 = 16(單一住所)— scripts/migrate_deliberation_ddl.py

### §10·6 跨機維運（8 條）
- IDX_MEM=2GB — import_database.sh post-data 索引段 maintenance_work_mem 預設,護欄 IDX_MEM×2 < RAM−shared_buffers 避 3 個 HNSW 並發建索引 OOM(import_database.sh:136,17,131-134)
- HNSW≥3 — DB 匯入 smoke 完整性斷言標準(sent/lex/chunk),live 實測=3;<3 印警告索引段未完成(import_database.sh:118,168-172)
- 看門狗閾值=2700s(45min) — audit log mtime 停滯超過即判卡死並 kill+kill -9(audit_selfheal.sh:30-32)
- audit 外圈 48 輪 / 休養 sleep 1800(30min) — 自癒重試上限 + IP 休養間隔,封頂後停止交人工介入(audit_selfheal.sh:10,45,47)
- FinMind MIN_INTERVAL=0.9 — 節流 SSOT 預設(換機爬坡已移除保守 2.0 覆蓋,≈2.2x 加速,#27;finmind.py:38 / audit_selfheal.sh:23-25)
- shadow mean_overlap≥0.90 — Qdrant 影子守門門檻,passed 才允許 cutover;min_overlap 只記錄不設閘(verify_qdrant_shadow.py:74,94)
- pg_restore 並發 pre/data -j4 · post-data -j2 — 分階段還原,索引/約束段獨立降並發(import_database.sh:135,139,141,143)
- _bootstrap 採用 172/174 — scripts 個別可執行覆蓋率,僅 backfill_knowhow_pipeline.py/verify_code_reports.py 未 import(#29a;_bootstrap.py:9-11)

## §11 未完成債／斷線／埋雷（v4 彙整）

**斷線（doctrine 說有、code 缺）**
1. **redline 治權檔 pattern 失聯**（§9）——對靈魂/原則精華/憲章的宣稱不會強制人裁；修法一行 UPDATE×3。
2. **predict role connection-unwired**——`DB_PARAMS_PREDICT` 未實作、無生產 code 用該 role 連線；動態閘空轉。
3. **prediction_values 禁回讀**僅 COMMENT 約定。

**埋雷（latent，觸發即沉默污染）**
4. **macro PIT reader 缺位**（§8.3）——接 macro 特徵前必須先落 reader。
5. **migrate 旗標二慣例並存**：`--migrate` 無參數呼叫 25 支 glob 內腳本，其中 **14 支 gated**（須 `--run/--migrate` 旗標）被**靜默 no-op 卻印 ✓**；第 15 支 gated＝`migrate_source_governance.py` 無 `_ddl` 尾不入 glob、完全不被呼叫。
6. **sync_memory 路徑推導**只 `replace('/','-')`——clone 到含 `.` 路徑（如 `.claude-worktrees/`）時 memory 目錄分岔指錯。

**狀態出入（以 DB 為準）**
7. **A3 三鏡頭三門 DB=preregistered、approved_by 空**（2026-07-12 17:39 重新預註冊）——與 commit/記憶「_r2 三門已簽」不符且 DB 無任何 `_r2` gate_id；開賽鏈若含 A3 須先向 hugo 確認簽核狀態。
8. **README line14 狀態句版本漂移**（寫 v1.5.0/v1.43.0/v1.25，實 v1.8.0/v1.45.0/v1.27；README 自身連結表卻正確）＋HANDOFF 引 CLAUDE v1.25——版本 SSOT=憲章修訂歷程，勿信狀態句。
9. **蒸餾 gold 的 teacher 事實**：274 筆全部 `teacher_model='claude-teacher-workflow'`（耗 Claude usage、人拍板），「本機 ollama 零 token」僅是 script fallback 機制 D 的能力、非已發生事實。

**各節起草者回報之債（彙整）**
- 【§1】治權檔版本交叉引用無機械閘、已實測漂移:README.md:14狀態句(靈魂v1.5.0/憲章v1.43.0/CLAUDE v1.25)與HANDOFF.md:20,120(CLAUDE v1.25)落後實檔(v1.8.0/v1.45.0/v1.27),而README.md:22-24連結表正確→README內部即不一致;tests/無任何doctrine-version一致性測試(缺一個版本一致性guard)
- 【§1】FREEZE已解凍入憲(v1.43.0)但live數字尚未升格:prediction_unfreeze_gate(unfreeze_06dcb178267d)現status=frozen未evaluate,部署主模型panel仍2026-05-31(payload.py:86 + DB max(panel_date));unfreeze evaluate為下一棒
- 【§1】憲章附錄A經驗結論刻意留空(#15):舊stock_backend數字不直接搬,須在Augur重跑後附source+口徑才補(by-design open debt,docs/系統架構大憲章_v1.45.0.md)
- 【§3.1】BACKFILL_DEFERRED=frozenset() 空集為 provisioned-but-unwired 框架、相關分支 dead(ingest.py:42)；fetch_dedicated 在自動 sync 路徑未被啟用（dedicated 參數無上游傳非空值）
- 【§3.1】MIN_INTERVAL/PER_STOCK_WORKERS 為「實驗中」操作值(#27 逐級試錯逼近奇異點、不寫死數字)；binding 是 sustained-throttle 非 pace，過度試探會深化 throttle
- 【§3.1】PriceAdj 175 檔 core_universe 股正處損傷態(factor 回落 >0.5%，SCAN_SQL 實測)，repair 器已備但殘留未清；且 live 除息必復發，長期正解=庫內自建調整序列(arena plan §5)、repair 僅過渡期工具
- 【§3.1】TaiwanStockDividend 塌列壞資料至今(2026-07-13)仍存：PK 仍 stock_id 單欄、2411 股各僅 1 列(2330 僅 1 列)，writer code 已修 require date 但 DROP+re-sync 未執行
- 【§3.1】PER 估值哨兵判準需重新定錨：記憶「PER=-1=虧損哨兵」錯(僅 2 列)，主導非正值是 PER=0(1,785,980 列)，且 PER=0 語意(虧損 vs 缺值)尚未獨立證明
- 【§3.1】raw_data_profile 為幽靈表(從未建立)、profiler 純 stdout；語意判準回填 catalog 為報告+人工 synthesis 驅動、非腳本自動化——語意判準落地未自動化，重跑須人再 synthesis
- 【§3.2】catalog 元資料 STALE：84 landed dataset 中 82 個 source_provenance 仍卡 probe、last_verified max=2026-06-29、TaiwanStockPrice n_stocks=3102 vs DB 54309；須重跑 build 對齊（DB 查）
- 【§3.2】chk_itext_owned_local_private 反向 SSOT 漂移：live DB 存在但 26 支遷移無任一 ADD CONSTRAINT 建它，唯一引用是 acquire_local_files.py:63-65 的 sys.exit 護欄，clean-room 依遷移重建不重現此 CHECK（違 #12）
- 【§3.2】import_database.sh:158 --migrate footgun：無參數呼叫致 15 支中的 gated _ddl 遷移被靜默 no-op（return 0）卻印 ✓，舊 dump 補跑會假成功實際沒補表
- 【§3.2】migrate_source_governance.py 無 _ddl 尾、不被 migrate_*_ddl.py glob 匹配（25/26 入迴圈），中央 runner 完全漏跑，靠人記得手動 --run --snapshot
- 【§3.2】prediction_values 隔離僅 migrate_prediction_ddl.py:61-63 的 COMMENT 承載、非機械閘（v3 已 REFUTED、未修）；GRANT 給 predict role 可讀寫，無閘阻 pipeline 回讀當特徵
- 【§3.2】硬編軟白名單（_DIRTY_VALUE_NOTES/_SPONSOR_ONLY/_SINGLE_DAY 等 dict）與 QUOTA_EXPIRY='2026-06-24'（已過期）是需人維護的 code 資料，與 #29『repo 內資料＝另一種 hardcode』有張力
- 【§3.3】總經因子未接 per-stock 特徵層:macro.py 宣告 31 FRED series、macro_vintage.py 建 PIT 消費門,但 feature_values 零 macro 特徵、build_panel 只 import 6 支 per-stock 模組——門建好但無生產消費者(panel.py:30 / macro_vintage.py:13)
- 【§3.3】雙層隔離不對稱:7 支 verify 腳本直寫 feature_values 靠結尾 DELETE 復原(紀律性非機制性),INSERT↔DELETE 間崩潰候選列會殘留於 canonical_features 所讀之表、base 須手動排除否則污染(verify_stability.py:65)
- 【§3.3】chip 日頻籌碼(法人/融資券/借券)T+1 精確公布時刻 gate 未做,現採保守 date≤panel 同日含,集保 f4 已補、其餘『上線後待 probe』(chip.py:19)
- 【§3.3】財報 lag 產業別缺口(休眠):release_lag 一律 45/90 無產業分支,金融保險/證期業法定 Q1/Q3 為 60 日;現況唯一消費者 gross_margin_pctile 已排金融股不觸發,未來月頻/季中消費金融股會顯現(release_lag.py:16-22)
- 【§3.3】HOLDINGS_LAG_DAYS=7 為 TDCC 集保無發布日欄之保守近似(2026-07-11 審計 1A 拍板),非嚴格法定值、待 probe 精修(release_lag.py:31)
- 【§3.3】名實不符特徵未改名(rename 漣漪 4 檔/77k+48k 列):lending_fee_rate_mean_30d 實=最近 100 筆借券成交、gov_bank_net_buy_60d 實=最近 ≤60 官股事件日(chip.py:94-104)
- 【§3.4】survivorship 債 b 未閉環（train_ranker.py:35-37 明標）：core_universe_asof PIT 只消完整度 look-ahead，但 feature_values 建自當前存活 roster、now 前下市股從未進 raw→從未入任何 as-of 名單→as-of IC 帶樂觀(存活)偏誤，呈現須明標。
- 【§3.4】本機 provenance 斷裂：實際部署的 3a4e66fae（29 特徵）5 個 joblib 在 disk 全 MISSING（models_artifacts/ 僅存 4 個舊 ce62866），predict_asof --run 會在 artifact.load(:119) 拋 FileNotFoundError；僅 --rewrite-all 吞例外續跑。
- 【§3.4】feats_hash『防漂移拒載』三處 docstring 宣稱但未實作（artifact.py:5、predict_asof.py:10/121）：cur_feats(:122) 死變數，:123 實際只做 artifact↔registry 自檢；正解須以 train 全 ≤asof panel 集重算 canonical（單 panel=35≠train 全史交集=29 會誤拒）。
- 【§3.4】DD 熔斷 live dormant：_deployed_dd_returns 需 forward 窗已關閉，現況 prediction_values 全庫僅 1 個 panel_date(2026-05-31)、每 model_id 恰 1 panel→回 []，即使 risk_policy 已 seed 也不觸發。
- 【§3.4】recency 部署無審核閘：registry 無 active/is_current flag（欄位僅 11 個），part=隱式 recency（asof/created DESC），且 register ON CONFLICT bump created_at=now()→重登舊 model_id 即可翻轉『誰是 live』，無 A-B/rollback 可鎖定。
- 【§3.4】universe/execution 零單元測試：完整度閘/PIT 迴圈/required 計算/cap 收斂/DD 皆無回歸鎖，只靠整合驗收腳本 verify_risk_overlay.py。
- 【§3.5】metrics.deflated_sharpe 口徑無關,餵年化 SR 靜默灌水~√ppy 倍(docstring 自陳 DSR 高估~14pp、本輪未複現);唯一防線=deflation.deflated_floor 包裝+命名慣例,無機械閘攔直呼(metrics.py:140,167;deflation.py:6;deflate_headline_verdict.py:120 存活體反例)
- 【§3.5】metrics.summarize 仍回 iid effective_t(metrics.py:83),#11/G8 明令禁裸用但無機械攔阻,防線僅靠 run_ladder/feature_diagnostics 併陳 HAC 之慣例、可被直讀繞過
- 【§3.5】COST_TW=0.00585 散落>10 script 各自定義、無單一 SSOT,且 run_backtest 預設 cost=0.0 使 caller 忘傳時 net==gross(portfolio.py:81,143)
- 【§3.5】tests/test_evaluation_core.py 僅覆蓋 3/7 模組(effective_t_hac/_entry_exit/splits);DSR/portfolio 經濟指標/baseline canonical gate/cross_section.augment 全無單測(:14)
- 【§3.5】常數未對齊:label.HORIZONS 列 252(label.py:22)但 walkforward 對 h≥252 raise(walkforward.py:48);baseline.py:12 docstring 稱 seeds 參數預留但 run_ladder 簽名僅 seed=42——stale advertise
- 【§3.5】run_backtest(asof=False) 為 latent dead code:portfolio.py:101 stocks=None → baseline._panel_matrix fset=set(None) TypeError,全庫無 caller 走此路
- 【§3.6】DB 動態閘 role 存在且 GRANT/REVOKE 生效,但預測 runtime 未接線——db.connect() 走單一 owner role config.DB_PARAMS(db.py:29),無 DB_PARAMS_PREDICT 變數(僅 setup_predict_role.py:19/127 docstring 提為下一步),predict_asof.py:112 走 db.connect();閘就位但未被行使
- 【§3.6】雙閘背向 divergence:setup_predict_role.py FORBIDDEN(:32-37) 未同步 import_isolation 07-10 後新增的 DELIB_LITERALS/BRIDGE_LITERALS → deliberation_claim/session/verdict + field_term_map + field_knowhow_lexical_affinity 對 augur_predict 仍 GRANTed SELECT(live=true),界線-A 新增項僅靜態單閘、DB 動態旁路防禦缺席
- 【§3.6】heal_by_date 的 passed 只 2-clause(reconcile.py:201:VM==0 ∧ EX==0),缺 not incomplete,與正典 verdict() 三-clause 不一致——heal 後 after 仍有抓取失敗時 heal 仍可能回 passed=True(違 #15)
- 【§3.6】_scripts_predict_leak_violations 偵測面不對稱(import_isolation.py:161):只掃 RBAC+CHAT literals,未掃 DISTILL/DELIB/BRIDGE——import 預測 package 的腳本若字面觸及 advisor_distill_*/deliberation_*/field_term_map 不會被此面抓到
- 【§3.6】reconcile_per_stock(sample_n)/reconcile_coverage(sample_days) 抽樣=部分覆蓋非全股 attest,agg['sampled'] 旗標須呼叫端誠實知會否則給全庫乾淨的假信心;reconcile_coverage 的 since 參數 provisioned-but-unused(docstring 自陳)
- 【§3.7】evaluate G1-G5 評分邏輯是 stub:守門1-4 過後直接 return 0、無 SET evaluated_pass/fail,解凍後主路徑未實作 (preregister_unfreeze_gate.py:171;master plan §7 債5)
- 【§3.7】FREEZE 常數硬寫 '2026-05-31' 未隨 07-12 解凍更新→今日對 asof>FREEZE 跑 evaluate 墜落 stub 而非拒跑分支,保護性拒絕失效 (preregister_unfreeze_gate.py:33,167-172)
- 【§3.7】frozen gate unfreeze_06dcb178267d 之 scope.model_ids 仍指 4 個已取代 ce62866,無新 gate 對齊 3a4e66/H82 生產基線(trigger 禁改,正解=superseded+另立)
- 【§3.7】E1_raw_reconcile_exit 殘紅(reconcile_audit exit=1)→--strict 現 exit 1,但 G1-G5 stub 無機械路徑消費此前置(帳面前置存在、機械未接線)
- 【§3.7】E8_econ_verdict_bound 為 green 但 status_note 殘留『未回單列單欄 boolean:(None,)』,疑人工覆寫/早期狀態,重跑 verify --run 恐翻 red,解凍前須複核
- 【§3.7】feats_hash 防漂移拒載未實作(cur_feats 死變數,predict_asof.py:122-123);prediction_values 回讀 self-loop 僅 DDL COMMENT 約定、無機械閘(v3 REFUTED 至今未修)
- 【§3.8】產物表 direction_probability/daily_direction_probability 現 0 列(fail-closed 現況,無 pass 門)——非缺陷,是判死的正確狀態,DB trigger 機械強制
- 【§3.8】擂台 armed 但未開賽:6 門 dgate_arena_* approved、9 候選註冊,但 direction_arena_prediction=0 列,arena 六門尚無真未來對局可 evaluate
- 【§3.8】direction_econ_verdict 表為空(0 列):即便未來有 pass 門,也須先把經濟裁決落此表才能出 E[r](produce_direction_probability.py:84-88 H3 fail-closed)
- 【§3.8】本機 DB 與 repo 程式 A3 家族分歧:code A3_GATES 用 _r2 版且註解稱原三門 superseded,但此機 DB 只有非-_r2 preregistered(approved_by NULL)、全庫無 _r2/superseded——pgdump_20260712 早於 A3 _r2 重註冊(以 DB 為準)
- 【§3.8】market 候選(own_daily_rolling/chronos/timesfm/own_stack/own_threelens)registry_model_id=NULL 刻意不入 model_registry,produce 只能路由 ledger 呈現、寫不進產物表(F2 已知路由,非 bug)
- 【§3.9】A3 三門 DB 現況=preregistered/未 approve/criteria_sha 12 碼(pre-_r2 buggy)、DB 無任何 _r2 列;與 git HEAD(A3_GATES=_r2 16碼)及 memory「A3 _r2 已簽」矛盾——_r2 重簽+核准從未對此還原 DB 執行,A3 效力尚未凍定生效(gotcha 最重要項;以 DB 為準)
- 【§3.9】run_arena_round.live_round() 機械閘只查 dgate_arena%(A2 家族)approved(:68),不驗 per-candidate A3 gate 核准,:100 取全體 active 逐列 INSERT;A3 僅 preregistered 時 own_threelens_interact(active/track=H)仍會落 ledger——「approve 前零預測」為程序約束、非機械強制(現 ledger=0 尚無實害)
- 【§3.9】own_threelens_interact 隔離不乾淨:相對 own_stack_rolling 三處同動(44 純個股 vs 6 含市場分量 / HistGBM 3-seed vs L2 LR / 市場 context 由用變不用,adapters.py:315 註解「不用」)——A3 gate 若 pass/fail 無法單因子歸因於特徵寬度
- 【§3.9】擂台尚未真正開賽:ledger 0 列、無 cron(A2 提案=首日手動陪跑);結算 UPDATE 路徑是 A0 合成冒煙無法測的最後一塊,待首批真列驗證
- 【§3.9】panel.FEATURE_TABLE 是模組全域常數,build_threelens 執行期 mutate 換目的表(:67);同進程內與 feature_values build 並跑會污染目的表(隱性全域副作用)
- 【§3.9】futility_min_clusters=60 照 D 軌日頻校準,H 軌月頻下 60 clusters=5 年→H 軌 futility 幾乎不觸發(保守 review-only,已知可接受)
- 【§4.1】計畫宣稱『491 件公版全文/47 萬句落地』(commit c008b5c / knowledge_fulltext_source_resolvers_plan_20260712.md:65)在本機 live DB 不存在——source_type='pd_fetch'=0、knowledge_source.adapter_config.fulltext 全 NULL;要生效須先把 fulltext 策略 UPDATE 進 DB(DB 跨機獨立、code 已 commit 但資料在別機落地)
- 【§4.1】PDF 抽取 P1-P3 未實作——src/augur/knowledge/pdf_text.py 不存在、fulltext_status CHECK 未擴 skip_pdf_no_textlayer/skip_pdf_quality;skip_pdf 積壓 976 件 + OAPEN 61 本仍卡誠實停(knowledge_pdf_extraction_plan_20260712.md 僅 P0 拍板)
- 【§4.1】phase_affinity DELETE 漏帶 corpus(build_cross_school_stats.py:633 `WHERE language=%s`,對比 :404 phase_vocab 有帶 corpus)——重跑哲學 affinity 會靜默刪除 items/en 119,764 列且不還原;計畫 §7 M3『DELETE 全帶 corpus』修補未落實於此行
- 【§4.1】refresh_knowledge_pipeline.py timer 鏈只走 OA 路、不含 fetch_pd_fulltext,亦未掛 bridge/stats_items 段——公版全文與 K 橋須手動/批次跑、非常綠自動鏈(K 計畫 §4 兩段 refresh 掛載未落地)
- 【§4.1】promote fail-closed 對未註冊源 fail-open——source_key 不在 knowledge_source(如 local_upload NULL)之 staging 經 NOT EXISTS 放行(promote_knowledge.py:200-202);屬設計預期(本機檔非外部源)但語意上須知悉
- 【§4.1】K 橋為物化快照非 view、會 stale——items basis_n=10,848 vs live CLEAN 10,855(背景 harvest +7 句);新料進不自動反映,須重跑 build_items_knowhow_stats.py + build_field_knowledge_bridge.py
- 【§4.2】stock_philosophy_tag DDL 建好(framework.py:50-56，含 as_of #8 欄)但 live count=0、全 repo 零 writer(grep INSERT 零命中) — 橫斷面哲學標籤仍未實作，v3 至今未變
- 【§4.2】validated_ic 已回填 37/42 但 philosophy_principle.status live 仍 26/26 全 untested(build() 從不寫 status、回填器只動 factor_map) — 兩層狀態不一致，顧問讀 status 會低估已驗證程度
- 【§4.2】principle_factor_map.feature 裸 VARCHAR(255) 無 FK — 5 個待建特徵(roe/debt_ratio/piotroski_fscore/peg_ratio/macro_regime)可先登錄假說但無可算特徵、validated_ic 恆 NULL
- 【§4.2】concordance_lookup(retrieval.py:190)回 knowledge_item 逐字內容但不過 clean_item_sql 的 domain/擁有者收窄 — 目前零呼叫非現行洩漏面，但未來接顧問讀取路徑須先補 RBAC 閘否則洩漏 local_private
- 【§4.2】禁 AI 生成 DB CHECK 只擋 type 欄字面='ai_generated'、不做語義偵測 — thinker bio 欄自陳源自『AI 記憶整理待覆核』(source_type=book 即過 CHECK)，是較軟誠實邊界、與原典全文逐字硬保證不同層級
- 【§4.2】philosophy_build_meta 只記 schools/principles/factor_map/sources 4 個 count，不記 build_people 維護的 thinkers/works/links — 低估實際維護範圍(v3 已標)
- 【§4.3】Qdrant 影子索引落後 pgvector SSOT 7 筆公開列（items_en n_synced=55,854 vs live public 55,861），sentence_items 已 cutover 故現行 serving 短少此 7 筆，需重跑 export_qdrant_index 補齊（qdrant_sync_state 快照 vs 2026-07-13 live）
- 【§4.3】make_index 世代 fail-loud raise（vectorindex.py:332-334）被 retrieval.py:311-315 except 吞成靜默降級 pgvector、非拒服務——世代不一致時檢索悄改走 SSOT 而使用者無感，只能靠 log 察覺
- 【§4.3】embed_philosophy_chunks.py 標頭 docstring 宣稱 bge-m3/1024 維但實際碼與 DB 皆 e5-small/384（:2,:4 stale vs :17-18 為準）
- 【§4.3】G3 host allowlist 對 Qdrant 未機械強制：QdrantIndex/make_index 只吃 config.endpoint 直連（預設 127.0.0.1:6333）無 host 斷言（migrate_vectorstore_config_ddl.py:45 註解稱另管，實碼未焊）
- 【§4.3】影子 cutover 門檻只閘 mean_overlap 不閘 min，最近通過列 min=0.2（單題 top-10 只重疊 2/10 仍 PASS，HNSW 近似+hnsw_ef=256 固有，min 僅記錄）
- 【§4.3】concordance_lookup 回逐字內容不過 clean_item_sql 的 domain/擁有者收窄（retrieval.py docstring 明載），現未接入 advise()/retrieve_all 故非現行洩漏面，未來接顧問讀路徑須先補 RBAC 閘
- 【§4.4】選股題 guard fail 連確定性 picks 表一起丟失：oai_compat._reply_text:99-106 於 guard fail 覆寫 body=NO_KNOWLEDGE_RESPONSE，對有真實 payload 的選股題回「知識庫中無此內容」語意矛盾（非對稱 fail-closed，v3 已記、仍在）
- 【§4.4】guard 與 guard_knowledge 負號正則不對稱（guard.py:57 捕負號、guard.py:121 函式 guard_knowledge 無）→ 知識域對負值 sign-blind，可放行符號相反的編造值
- 【§4.4】蒸餾 S4 teacher.py 是真骨架、從未產出過 gold（274 gold 全由 out-of-band claude-teacher-workflow 直寫、code 不在 repo）；32 題 situation-1 expected 被 ANSWER→DECLINE 外帶覆寫、無 committed UPDATE script（staging 側 #12 張力）
- 【§4.4】knowledge_item.domain 兩階段 FK 故意未套用（#30 DDL 時機＋政策決定）→ 入庫端 writer 標錯 domain＝靜默越權洩漏無 FK 攔（audit_domain_hygiene 只稽核不強制）
- 【§4.4】knowledge_access_audit 只記管理動作（66 列 grant/add/create），零 login/retrieve/deny → runtime enforcement 靜默、無存取日誌
- 【§4.4】RBAC live 人事未派（user_group=0）實質單 superuser、群組結構已建；concordance_lookup/lexicon_lookup 歷史未過 CLEAN 閘、現零呼叫點——未來接顧問讀取路徑而未先補 clean_item_sql 收窄＝繞 #1 命門（retrieval.py:193-195 明文警告）
- 【§5】redline doctrine_file 觸線 pattern STALE:pin 舊版檔名(原則精華_v1.8.0/核心思想_v1.5.0)+ 憲章樣式含字面 `%`,經 Python 子串 `in`(redlines.py:30-35)幾乎永不觸發;現僅 CLAUDE.md/README.md 兩條活。潛在治權防護缺口、尚未致害,值得修 pattern 對齊現行檔名(v1.9.0/v1.8.0/v1.45.0)
- 【§5】L2 每日自審 cron 在本換機環境未掛(crontab 無 delib 條目、session 止於 07-12);#31 cron 機器本地不隨 git,新機須重掛 run_daily_deliberation.py --run 才恢復全自動日
- 【§5】15 筆 undecidable escalation 未決,人裁佇列積壓;resolve_escalation.py --watch 積壓警示為 warn-only(exit 0)非硬閘,不擋 daily_green
- 【§5】verifiers.py:1 標頭 docstring 仍寫「四真 oracle」,實為 5 oracle(含 pytest);標頭與 code(ORACLES:30)不一致待更新
- 【§5】L6_pytest 快路生產預設關(anchors.py:59;DB config false)——執行任意測試節點=最大攻擊面;若要走 pytest 快路須 UPDATE config 一列並評估攻擊面
- 【§6】ROOT 推導兩軌矛盾:sync_from_github.sh:6 與 start_chat.sh:6 硬寫 ROOT=$HOME/project/augur,而 resume_project.sh 一鍵鏈以 dirname 推導 → clone 到非標準路徑時 resume 鏈會在 sync_from_github 這支斷掉
- 【§6】sync_memory.py:32 路徑 mangle 只 replace('/','-'),但 Claude Code 目錄命名把 '.'(及其他非字母數字)也換成 '-' → clone 到含 '.' 路徑(如 .claude-worktrees/…)時推導出的 memory 目錄與 Claude 實際目錄分岔、指向不存在的錯目錄,restore/export 失效
- 【§6】daily_green.py:55 (r.stdout+r.stderr).strip().splitlines()[-1] 在某失敗步驟輸出全空時拋 IndexError → daily_green 自身崩潰而非乾淨回報 FAIL(已實測確認的真實脆弱點)
- 【§6】augur-green.timer(每日 07:30)只在 daily_green.py:16 docstring、從未入 git,換機後機器未安裝任何 augur systemd unit;無 CI 下若忘了重裝 timer,唯一持續健康閘會靜默不跑而無人知
- 【§6】verify_qdrant_shadow.py:74 影子門檻 MEAN-only,min_overlap 只落庫不設閘 → 單題重疊退化到 0.2 仍 passed=t(實測 2026-07-12 mean=0.912/min=0.2/passed=t),極端退化不擋 cutover
- 【§6】文件/版號漂移未清:import_database.sh:16 「補跑 13 支 migrate」實為 25 支;HANDOFF.md:20,120 仍寫 CLAUDE.md v1.25(實 v1.27);audit_selfheal.sh 的 0.9 爬坡改動尚未 commit(工作樹 M audit_selfheal.sh)

## §12 對 v3（20260710）之承重差異

**v3 已過時的宣稱**（正文一律採本表）：
- §1 治權版本表（v1.5.0/v1.8.0/v1.39.0）→ 現 v1.8.0/v1.9.0/v1.45.0/CLAUDE v1.27；且治權檔正式為**五檔**（clean-room #16 含 README）非四檔。
- §10「資料凍結是明文延後技術債、不追新資料」→ **07-12 解凍入憲整段推翻**（live 增量維運、as-of' 滾動、unfreeze gate 紀律）。
- §8 owned_local「無跨欄 CHECK、license 白名單未含」→ 已補上（drift-toward-alignment）。
- §10「predict role 尚未 apply」→ 已 apply（但 connection-unwired，見 §11）。
- v3 完全未涵蓋（07-10 後從零出生）：方向軸建置與十門判死＋no-v3、輸出契約三度增修入憲、擂台 A0-A3、審議引擎補完＋GATE PASS＋F1/L2、三鏡頭鏈、全文解析器 T1-T3、chat UI parity、取代式 STATE、換機工具強化。
- **v3 仍有效**：§1-§9 的架構/HOW-built/wiring 主體（本輪逐列再驗，個別修正如上）；「當前狀態快照」職能已移交 HANDOFF §4 取代式 STATE。

**本輪對抗驗證 REFUTED 12 條**（正文皆已採更正版）：升版連動次數（≈10 次非 2 次）、_coerce float pass-through 語意、PIT 名單非單調（5 次窗間上升）、隔離掃描八道非七道、audit 層含兩支專職 writer、三鏡頭 adapter 隔離不乾淨（三處同動、無法單因子歸因）、蒸餾 teacher 實為 Claude workflow、memory 路徑推導限制、「13 支 migrate」歸屬、DDL 旗標慣例成員數、raw profiling 缺口範圍收窄、S5 decline gold 過閘機制（grounding 豁免非閉集句觸發）。
