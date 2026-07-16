# arena 前置 = G1-G5 實質驗證機制｜計畫書 v1（呈 hugo 拍板）

> **定位**：承 2026-07-16 hugo 拍板——(1) 解凍已由 07-12 v1.9.0 入憲完成；(2) `unfreeze_06dcb178267d` gate（live 實查 status=`superseded`、criteria_sha=`990ddea219ad24e0`、approved_by=hugo@2026-07-11 12:08）退為 superseded 史料；(3) arena 開賽前置改以 master plan §4 的 **G1-G5 實質驗證機制**為準。
> **本版變更（納入三面對抗審查）**：v0 骨架經一輪 live code + live DB 覆核 + 三面對抗審查（機制正確性 / 治權一致性 / 完整性），**修正一個 blocker（G3/G4 軸別誤植）與 12 處 major/minor**，並補齊憲章 v1.39.0「計畫完整性」所需之 (a) 表 schema + (b) python 程式規畫。逐條處置見 §10 附表。
> **核心前提（實證、不美化）**：G1-G5 的機械判定碼在 `scripts/preregister_unfreeze_gate.py::evaluate()` **從未實作**——L169-171 明寫「守門 1-4 過；**守門5(先凍後跑時序)與 G1-G5 逐項機械評估=解凍後路徑(本計畫內不可達)**」，evaluate() 只機械測守門 1-4、從不改 status。master plan §7 債 5（F7）已誠實記載此為結構性限制。**故本計畫不是「改指向」，而是「新建 G1-G5 實質驗證的執行機制」。**

---

## 決策紀錄（Phase 0，2026-07-16 hugo 逐項拍板；滾動更新）

| 裁決 | 決定 | 影響 |
|---|---|---|
| **D-2 軸別** | **Reading A** | 方向 arena 確立走它自己門二 `evaluate_direction_gate`（≥60 clusters）；相對強度 G3/G4 歸相對強度部署、**不 gate 方向 arena**。→ G3/G4/D-7/D-8/D-9/consecutive_k **移出 arena 開賽關鍵路徑**（相對強度部署事、日後） |
| **D-5 對帳範圍** | **全真名冊 3,114 真股**（排除權證污染）→ **同日午後被 G1-PIN 部分 supersede（見下）** | `reconcile_per_stock(roster_only=True)` + `daily_maintenance --full-universe` + `full_universe_attest.py` 已實作；滾動窗放量**中止於 32/84**（hugo 拍板 A）——工具保留（支援 `--audit-until`，pinned 窗驗證可復用） |
| **G1-PIN as-of 釘選**（2026-07-16 午後 hugo 拍板；supersede G1 滾動框架） | **arena 資料地基 as-of 釘死 2026-06-30、不再追滾動資料完整**（hugo 原話「資料就定在 2026-06-30 即可，不要再去追資料完整」） | **概念修正**：live 世界 byte 對帳=移動標靶（每日新資料+歷史修訂），滾動「真綠」明天即過期=「凍一條河」；且追 byte-equal-to-current-API 與 as-of vintage（#8）有張力。**G1 重定義**：≤2026-05-31 由凍結期快照認證（既有、不動）；**06-01~06-30 段對帳到綠一次→凍成 G1 參照，之後不再滾動追**；與 feature_values 凍結後 panel（2026-06-30）對齊。系統 live 增量 sync 照常（服務 advisor 等），僅 arena G1 用固定 as-of。06 月段驗證方式（全真名冊 vs 抽樣+揭露 vs 接受日常 sync 證據）＝gate criteria 組裝時之小裁決（待 hugo）。原「audit_until≥CURRENT_DATE−3d」freshness 斷言**作廢**（滾動框架產物） |
| **D-1 G2 方向覆蓋** | **補做** | G2 須含方向特徵 `daily_direction_feature_values` anti-leakage 迴歸鎖（實證現無）；實作首步＝查 `build_daily_direction_features.py` as-of 紀律，有 lookahead＝真 bug 要修 |
| **D-4 MIS 揭露** | **補明確揭露** | 全宇宙+heal 跑完 MIS＝真實數（非抽樣吸收之 5369）；result_snapshot 明列真殘留及性質、驗收 SQL 註明界定，根治「audit 假綠」前科疑慮 |
| **D-3 gate 表** | **新專表 `arena_admission_gate`** | superseded unfreeze gate 純留史料；新表帶 `axis` 消歧 + `supersedes_gate_id` 鏈（**subsumes D-10**）+ 白名單 trigger（鏡射 `trg_unfreeze_no_goalpost`） |
| **D-6 hash 正規化** | **復用 `reconcile._norm` 口徑** | G2 hash 與 byte-reconcile 同正規化（數字等價 `'1.0'==1`、`NaN`/`''`→None）+ 定點小數舍入 + 確定性排序（panel_date,id,feature）+ NULL sentinel；`normalization_ref` 版本化存 baseline 表（#12 單一住所） |
| **D-11 U6 放鬆語意** | **白名單枚舉 + fail-closed** | 每 frozen 門檻列放鬆方向（floor↓ / ceiling↑ / required-count↓ / alpha↑＝放鬆）；未列/新鍵 **fail-closed**（當疑放鬆、要求簽核），避免漏枚舉之門檻被偷放鬆漏網 |

**arena 開賽關卡 Phase 0 決策：全 7 顆已拍板**（D-1~D-6、D-11；D-10 由 D-3 subsumed）。
**已降級（相對強度部署、非 arena 開賽關卡）**：D-7（RankRidge feats_hash 家族）、D-8（非重疊期定義/rebalance 頻率）、D-9（G4 established 落表）、consecutive_k 凍結。
**開賽前查核（非決策）**：`validation_evidence` 19 列全綠須確認每列有債清留痕（本會話 E 債已解、非漏 seed）。

**執行邊界（hugo directive 2026-07-16）**：以上皆**計畫層方向決策**；實作（建表/evaluator/hash baseline/接線）與治權修訂一律**待 hugo 後續拍板才動工**（#26），不因決了方向就動手。

**Phase 1 實作完成（同日 hugo 拍板「啟動 Phase 1」→「接著寫到完成」；全 7 元件落地+實測）**：
①gate 表+挪門柱 trigger（selftest 4/4）②preregister（繼承 990ddea sha 斷言；draft `arena_adm_3f1cfdc9aded`）③兩軸 panel hash 洩漏鎖（36+2,830 panel/19.2M 列 verify PASS 0 mismatch；防改 trigger）④核心裁判（守門鏈+fail-closed+原子終態；--check 唯讀預演）⑤score repro（**§6.5 校正：oos_sample=逐折 refit 產物非 artifact 輸出；正解=artifact 重打分決定性**，112 組 100% 復現至 5 位；正典家族=990ddea scope.model_ids=ce62866，D-7 免議）⑥U5 人裁佇列（evaluator 聯動實證）⑦雙閘接線（兩 chokepoint fail-closed 實證 rc=1）。
**最終預演：G2 整關綠；剩餘 blocker 100%=hugo 決策項**（06 月段方式→freeze→check→evaluate）。

---

## 一、背景與決策

### 1.1 gate 退史料之由來

2026-07-11 hugo 親簽凍結 `unfreeze_06dcb178267d`，原設計意圖：`evaluate()` 過即解凍 → 開賽。2026-07-16 實測發現 `evaluate()` 是**純唯讀診斷**：只機械測守門 1-4（status=frozen / criteria_sha 覆算 / judgestop 快照一致 / FREEZE 生效中），G1-G5 的實質評估在 L171 明標「本計畫內不可達」（未實作）。

hugo 拍板：
1. **解凍已完成**——由 07-12 入憲（原則精華 v1.9.0 / 憲章 v1.43.0）承接，不再依賴 gate 的 evaluate。
2. **gate 退 superseded 史料**——live DB 已是 `status=superseded`（實查）。
3. **arena 開賽前置改以 master plan §4 G1-G5 實質驗證機制為準**。

### 1.2 這是「新建機制」不是「改文字」

master plan §4.3 的判準**值**（G1-G5 各關的閾值口徑）是 SSOT，但——

- §4.3 自承「下列為 AI 建議 + 論證，**非裁決**；判準值本身=拍板點 U1-U6 人凍才生效」；真正**權威凍結值**是 DB 內 `prediction_unfreeze_gate.criteria`（criteria_sha=`990ddea219ad24e0`）的快照，**現孤懸於已 superseded 的死列**，無任何 live frozen gate 承接。
- G1-G5 的**機械判定 code 從未實作**（F7）。

因此「arena 前置改 G1-G5」**必須新建**：(a) 承接 990ddea 凍結判準的新 gate 物件、(b) G1-G5 逐關的機械評估 code、(c) fail-closed 接線。**不能只改治權文字就當 arena 前置已備妥。**

### 1.3 對抗審查揭出的 blocker：軸別（本版最重要的修正）

v0 草案把 master plan §4 的 **G3/G4** 當作 arena 的「開賽後持續 verdict」，但 live code 實證：

| 事實 | 實證來源 |
|---|---|
| 今日唯一有 approved gate + daily pipeline 的「arena」是**方向/預言機軸** | `run_arena_daily_pipeline.py::_gate_approved` 查 `direction_gate WHERE gate_id LIKE 'dgate_arena%'`；6 列 approved（own_daily_5 / chronos_5 / timesfm_5 / own_stack_20/40/82，實查） |
| 方向 arena 的資料/結算/econ/榜全是方向軸機器 | features=`daily_direction_feature_values`（19.2M 列、live 至 2026-07-09）；結算=`settle_arena_labels.py`；econ=`run_direction_econ_eval.py`；榜=`arena_scoreboard.py`；ledger=`direction_arena_prediction`（表存在、**0 列**） |
| master plan §4 G2/G3/G4 全是**相對強度軸**產物 | G2=`feature_values` 35 panel + `RankRidge_H{20,40,60,120}`；G3=相對強度 `probability_oos_sample` 校準；G4=相對強度組合 `econ_verdict_rule` |
| 方向軸已有**自己的確立機制** | `evaluate_direction_gate.py` 三關（HAC 命中率 / Brier / ECE+單調）；門二裁決待 `direction_arena_policy.futility_min_clusters=60`（frozen）樣本後 evaluate |

把相對強度軸的 G3/G4（新建 `probability_live_reading`、`revalidate_verdict --upgrade`）接到方向 arena 當持續 verdict，會 (a) 以相對強度校準去 gate 方向 arena 的「確立級升格」——該相對強度 live 視窗對方向 arena **永遠不會成熟**（H120≈2.9 年、跨軸誤植）；(b) 與方向軸既有 `settle_arena_labels`/`run_direction_econ_eval` 形成**兩套並行 live 校準棧**，違 CLAUDE #12（單一住所）。

**本版裁決（升為 §3 前置架構決策，須 hugo 拍板）**：見 §3.1。

---

## 二、G1-G5 機制化現狀總表

（逐關 done/partial/gap + 現況一句 + 須等新資料？；一切引自本輪 live code + live DB）

| Gate | master plan §4.3 判準（值 SSOT） | status | 一句話現況（實證） | 須等新資料？ |
|---|---|---|---|---|
| **G1** 資料供應鏈 | (a) in-scope 表 byte 對帳全綠至 as-of'；(b) as-of' 更新已入憲（commit 時間 > approved_at） | **partial** | (a) 機械化且此刻 `passed=True`（`attestation_result` id=2、run_at 2026-07-15、VM=0/EX=0/coverage_gap_n=0/incomplete_n=0）——**但 `missing_in_db=5369`**（由 exempt_n=19/部分覆蓋 27/端點扣抵 3 吸收）、`audit_since='2026-07-01'`（滾動窗、非全史）、`sampled_n=27`（roster-scoped 34 表抽 40 股）、**無 `audit_until` 欄**；(b) 零機械化、僅治理事實 | 否 |
| **G2** 舊區段復現（anti-leakage 迴歸） | (a) panel≤FREEZE `feature_values` 逐 panel 值 hash 不變；(b) 4 模型分數復現至 5 位小數；U5 restatement 人裁 | **gap** | 三判準**只有文字被凍進 990ddea 快照、零評估碼**。現有 `feats_hash` 只鎖特徵「名集合」抓不到值被改；score 5 位靠一次性人工觀測、無可重跑斷言；U5 連 diff 工具都不存在。**且方向 arena 自身特徵（`daily_direction_feature_values`）完全未被 G2 覆蓋** | 否（作用於凍結區段） |
| **G3** 校準存活（live 視窗） | ≥6 非重疊期；live Brier−0.25 三分；live ECE≤0.05 | **gap** | 判準值凍結入 990ddea 快照，**但無任何 code 在跑 live 視窗**；相對強度 `probability_oos_sample` 全 ≤FREEZE（25 panel、2016-2025）、零 live 樣本；方向 arena `direction_arena_prediction` 0 列 | **是** |
| **G4** econ 升級（thin→established） | live 同時 net_excess>0 ∧ HAC-t≥2.0 ∧ DSR≥0.95 ∧（建議加）deflated_ann>0；連續 2 輪 | **partial** | 四指標計算基座已實作（`revalidation_verdict.metric_snapshot` 2 列，DSR≈0.756<0.95）；但**升級判定器整支未實作**（既有 `revalidate_verdict.py` 是衰減方向、DSR 只當標註）；`revalidation_ledger` 僅 1 輪（as_of=2026-05-31）；`consecutive_k` 未凍 | **是** |
| **G5** 回退/治理 | 原子 fail、軌B 照常、retry=新 gate 留痕、U6 放鬆須簽核 | **partial** | 狀態白名單 trigger（`trg_unfreeze_no_goalpost`）+ track-B 解耦已機械化且 live 實測；但**原子 evaluator 只在 direction gate 有、unfreeze 側是 stub**；無 `supersedes_gate_id` 鏈欄；superseded 死列**無後繼 gate**（違其自身 §4.3 G5 語義）；U6 放鬆簽核零機械強制 | 否 |

**一句話總結**：G1(reconcile)、G5(骨架) 已有可靠機械基座；G2 全缺（且方向軸未覆蓋）、G4 缺升級判定器、G3 缺整條 live 讀數鏈。方向 arena 兩 chokepoint（`run_arena_daily_pipeline.py:37-44`、`run_arena_round.py:66-72`）只檢 `dgate_arena% approved`（6 列），**完全不碰 G1-G5**——這正是要補的斷鏈。

---

## 三、目標：arena 前置 G1-G5 gate 機制

### 3.1 前置架構裁決（blocker，須 hugo 拍板）——兩層切分 + 軸別歸屬

G3/G4 是 **live 視窗判準**，需 ≥6 非重疊期才有檢定力，而 live 資料只在**開賽之後**累積 → 「開賽前必過 G1-G5 全部」＝永遠開不了賽。故 gate 必須**兩層切分**，且**軸別必須釐清**：

**(A) 開賽硬前置（open-time hard precondition，今日即可判）= G1 + G2（+ G5 治理骨架）**
- **G1（reconcile）＝軸無關的共享資料地基**：byte 對帳全綠至 as-of'，任何 arena 開賽前皆須。
- **G2（anti-leakage 迴歸）＝共享地基 + 被 gate 那條軸的自身特徵**：現況 G2 只 hash `feature_values`（相對強度軸）。**若被 gate 的是方向 arena**，G2 必須**加一條方向軸自身 anti-leakage 迴歸**（`daily_direction_feature_values`），否則等於對「方向 arena 自身特徵無洩漏」發了根本沒驗過的綠燈（假兆）。→ **裁決題 D-1**：方向軸特徵迴歸「補做」還是「明文標為誠實債、G2 scope 僅共享地基」。

**(B) 開賽後持續 verdict（post-open continuous verdict）= G3 + G4，綁「實際產出 live 輸出的軸」**
- **關鍵裁決 D-2**：方向 arena 的**確立級升格**走**誰**？
  - **本計畫建議（Reading A，#12 尊重）**：走方向軸**自己的門二** `evaluate_direction_gate.py`（三關 + ≥60 clusters），**不**用相對強度 G3/G4。相對強度 G3/G4 是**相對強度部署自身的生命週期**（`revalidation_verdict` upgrade 軌），**不 gate 方向 arena**。→ 不新建 `probability_live_reading` + 鏡射 settle（避免與方向軸既有 `settle_arena_labels`/`run_direction_econ_eval` 雙棧、違 #12）。
  - Reading B（若 hugo 要跨軸耦合）：須明列耦合理由；否則不採。
- **若另要開「相對強度 live arena」**：須**明列為獨立軸、獨立排程、獨立 gate**，不共用「arena」一詞含混；此時才建 `probability_live_reading` + 鏡射 settle（§5 條件式表）。

**(C) G5（橫切）**：原子 fail 語義、retry 留痕、U6 放鬆簽核，作用於 admission gate 物件本身。

> **切法直接回應**：開賽 = **G1+G2 硬綠**；方向 arena 開賽即入 `review_observation_only` tier、**永不宣稱確立級**；確立級升格 = 門二 evaluate（≥60 clusters）成熟後翻牌。相對強度 G3/G4 各自服務相對強度部署，不阻擋方向 arena 開賽。

### 3.2 這關住哪（新建）

- **裁判 script**：`scripts/evaluate_arena_admission.py`，鏡射已實證的 `evaluate_direction_gate.py::_evaluate_one()`（三關 AND → 單筆 UPDATE status + result_snapshot 的原子樣板）。機械覆算 G1+G2（+守門5 先凍後跑）、逐關回 pass/fail、AND 收斂、fail-closed。
- **verdict 落表（新建專表）**：`arena_admission_gate`（詳 §5.1），配狀態白名單 trigger（鏡射 `trg_unfreeze_no_goalpost`）+ `supersedes_gate_id` 鏈欄 + `axis` 消歧欄。
  - **為何新建而非復用 `prediction_unfreeze_gate`**：hugo 07-16 已裁 unfreeze gate 退 superseded 史料；復用需在已封存列旁另立新 gate_id 並回頭實作 stub，語義糾纏。專表讓 superseded gate 純留史料。**（此為建議，最終 hugo 拍板 D-3。）**
  - **凍結判準託管**：新 gate 建立時，把 superseded 死列（990ddea）的 G1+G2 子判準（`g1_data` / `g2_repro`）**逐鍵複製**進新 gate criteria，並對複製部分做 **sha 等值斷言**，以機械證明「機制置換未挪門柱」，再由 hugo 重簽 frozen；同時把 990ddea 的後繼 gate_id 顯式回填（`supersedes` 鏈）。

### 3.3 如何被開賽流程強制（fail-closed）

chokepoint 已現成，在今日查 `dgate_arena% approved` 的**同兩點**加 AND 前置：

1. `run_arena_daily_pipeline.py::_gate_approved()`（L37-44，管線頂部）——**最佳落點**：G1+G2 未過即在任何 sync/特徵/ledger 寫入**之前**中止整鏈。
2. `run_arena_round.py::live_round()`（L66-72，寫 ledger 前）——縱深防禦。

前置 SQL（fail-closed：表缺/列缺/status≠pass → 拒開賽）與現有 `dgate_arena approved` 檢查 **AND 串接**（門一 ∧ 門二 才放行）：
```sql
SELECT 1 FROM arena_admission_gate
WHERE gate_id = %(g1g2_gate_id)s AND status = 'evaluated_pass' AND axis = 'shared_foundation';
```

**同批修正 in-code 前置字串**（執行層、非治權）：`run_arena_daily_pipeline.py:90-91`、`run_arena_round.py:8`（docstring）與 `:71`（拒跑訊息）現硬寫「unfreeze GATE evaluate pass」前置鏈——已退役，須改述為新 `arena_admission_gate` G1-G2 硬前置，否則 code 自述與新機制矛盾。

### 3.4 逐關機械檢查（摘要，細節見 §4/§6）

- **G1（硬前置）**：斷言最新 `attestation_result` `passed AND value_mismatch=0 AND extra_in_db=0 AND coverage_gap_n=0 AND incomplete_n=0`（**`missing_in_db` 不斷言為 0**，其被 exempt/端點扣抵吸收之機制明列於 result_snapshot，見 §9）；補 `audit_until` 欄斷言「覆蓋達 as-of'」（欄就位前以核心表 `max(date)` 近似）；記錄 `sampled_n`/`audit_since` 揭露旗標；asof_charter(b) 記 governance-satisfied（時序見 §4-G1）。
- **G2（硬前置）**：35/35 panel `value_hash+row_count` 比對 baseline（0 mismatch）；4 artifact 重打分逐 (h,panel,stock) `round(·,5)` 100% 復現；U5 diff 空=pass、非空=review；**方向軸特徵迴歸**依 D-1 裁決。
- **守門5（原子 evaluator 內）**：`approved_at < min(live 工件最早 created_at)`（先凍後跑時序錨，鏡射 B2 `preregistered_at < min(run_at)`）。
- **G3/G4（持續、分軸）**：依 D-2 裁決——方向 arena 走門二；相對強度部署走 `revalidation_verdict` upgrade 軌 + `evaluate_direction_gate` 對應軸。
- **G5（橫切）**：evaluator 內 AND 收斂單筆落地（無 per-component 覆寫面）；retry=新 gate_id + `supersedes_gate_id` 鏈；U6 放鬆偵測 + 簽核閘。
- **evidence_ledger_gate（§4.2 併列前置，v0 漏列）**：`verify_validation_evidence.py --strict` 綠 或已知債紅列如實在帳（見 §4-G1 附加）。

---

## 四、缺口與工作項

每 gap → 一個具體工作項。標「〔now〕」可 clean-room 立即做、「〔live〕」須等新資料、「〔治權〕」須 hugo 拍板。

### G1

| # | gap | 工作項 |
|---|---|---|
| G1-W1〔now〕 | `attestation_result` 缺 `audit_until`，且 `audit_since='2026-07-01'`＝滾動窗、非全史 | `schema`/`daily_maintenance.py` INSERT 加 `audit_until DATE`（寫對帳窗上限）；gate 斷言 `audit_until >= CURRENT_DATE − 3d`（欄就位前以 `TaiwanStockPrice`/`TaiwanStockPER` `max(date)` 近似）。**G1 明述為 windowed 宣稱**：≤FREEZE(2026-05-31) 歷史完整性由凍結期快照另行認證，此關只保證 as-of' 滾動窗綠 |
| G1-W2〔now/治權〕 | `missing_in_db=5369` 被 `passed=True` 吸收（exempt 19/部分覆蓋 27/端點扣抵 3），但 v0 驗收靜默略過 | gate result_snapshot **明列** `missing_in_db` 與吸收機制；驗收 SQL 註明「`missing_in_db` 不斷言為 0，其受 `exempt_n`/端點扣抵界定」（避免重演 MEMORY「audit 假綠」前科）。**裁決 D-4**：是否以 `passed=True` 為權威單一斷言（吸收邏輯已收斂於此），或補「missing_in_db 在容忍內」明確斷言 |
| G1-W3〔now/治權〕 | roster-scoped 34 表僅抽 40 股 byte 對帳（latest `sampled_n=27`），非全宇宙 | **裁決 D-5**：arena 級改全宇宙 run（`sample_n=None`）跑一次寫 attestation，或明確接受 sampled 揭露。工作項＝`daily_maintenance.py` 加全宇宙路徑 + gate result_snapshot 帶 `sampled_n` 旗標（不讓「真綠」字面與 27 表 40 股抽樣脫節） |
| G1-W4〔now〕 | asof_charter(b) 無機械檢查，且原 990ddea 判準「commit > approved_at」對**新 gate** 恆為 FALSE（新 gate approved_at 在未來） | 修正不等式方向：新 gate 之 G1(b)＝「as-of' 政策已先入憲（charter 解凍 commit `7d337ec`@2026-07-12 存在）且 **commit_time ≤ 新 gate approved_at**（治理在先）」；記為 governance-satisfied。若要機械化＝新增 as-of' 政策變更偵測（低優先，交 hugo） |
| G1-W5〔now〕 | §4.2 併列前置 `evidence_ledger_gate` + `baseline_refs` v0 未納入；且 `validation_evidence` live 實查 **19 列全 green、0 red/amber**，與 master plan §1.4「已知債紅列須存在（不許全綠假象）」矛盾 | gate 加 `evidence_ledger_gate` 斷言（`--strict` 綠 或債紅列如實在帳）+ `baseline_refs`（`revalidation_baseline`/calibrators/`econ_verdict_rule` 快照存在且未變）；**先查清 19 列為何全綠**（債列是否被人裁除名/修復留痕、或漏 seed）——未釐清前不得當「真綠」採信 |

### G2

| # | gap | 工作項 |
|---|---|---|
| G2-W1〔now/治權〕 | 無 feature_values「值」逐 panel hash；且 live 已有 post-FREEZE panel（`2026-06-30`、91385 列，總 36 panel）——「35/35 靜態集」敘述過時 | 新表 `feature_panel_hash_baseline`（§5.2）；新工具 `freeze_feature_panel_hash.py`（凍結期算 baseline、gate 期重算比對）。**先拍板 value 正規化規則 D-6**（小數位/去尾零/NULL 表示）否則 hash 假紅。**baseline 須釘死凍結 as-of 快照點（≤FREEZE 的 35 panel）**，並定義「新 ≤as-of panel 出現時」行為（不把持續增生集當靜態） |
| G2-W2〔now/治權〕 | 無 score 5 位小數復現斷言工具；且 `RankRidge` 有**兩個 feats_hash 家族**（`ce62866bb62de38b`、`3a4e66fae8cfa2fa`，H82 僅在 3a4e66），`probability_oos_sample.model_family` 只記 `'RankRidge'` 無法消歧 | 新工具 `verify_score_repro.py`（§6）；先凍 score baseline（新 `score_repro_baseline` 表）。**先釘死正典家族 D-7**：查 25-panel score 之來源家族（ce62866 vs 3a4e66）與部署路徑，明列並排除另一家族與 H82；**並校正原 990ddea scope 內部不一致**（`model_ids` LIKE 涵蓋 H82+兩家族，`horizons=[20,40,60,120]` 卻排除 82） |
| G2-W3〔now〕 | U5 無 diff 工具、無 review 佇列 | 新工具 `report_restatement_diff.py`（§6）；新表 `restatement_review_queue`（§5.4）；diff 空=pass、非空=review 非自動 fail（鏡射 judgestop 人裁） |
| G2-W4〔now/治權〕 | 方向 arena 自身特徵（`daily_direction_feature_values`）無 anti-leakage 迴歸——G2 只覆蓋相對強度 `feature_values` | 依 **D-1**：補方向軸特徵 hash baseline（同 `feature_panel_hash_baseline`，`axis='direction'`，釘死方向候選訓練所用之凍結 as-of 段），或明文標「G2 scope 僅共享地基、方向特徵未覆蓋＝誠實債」。不得讓 G2 綠燈冒充方向 arena 全綠 |

### G3（依 D-2；本計畫建議方向 arena 走門二、以下為「相對強度部署」軌或「另開相對強度 live arena」時才建）

| # | gap | 工作項 |
|---|---|---|
| G3-W1〔now/live，條件式〕 | 相對強度軸無 live 逐期 Brier/ECE 帳 | **僅當 D-2 選「另開相對強度 live arena」**：新表 `probability_live_reading`（§5.5）〔now 建表〕；資料〔live〕。**方向 arena 不建此表**（複用 `direction_arena_prediction`+`settle_arena_labels`） |
| G3-W2〔now，條件式〕 | 無 live 結算腳本 | **方向軸複用** `settle_arena_labels.py`（勿另造）；相對強度軸若開＝新鏡射 settle |
| G3-W3〔now/治權〕 | 無非重疊期計數器 + tier 分派 | evaluator 寫「非重疊＝panel 間距≥H 交易日」計數 + n<6→review / n≥6→可確立 分派。**非重疊定義 + live rebalance 頻率（月/季頻）須入憲 D-8**——直接決定 6 期累積速度與「開賽後多久可升確立」 |
| G3-W4〔live〕 | 無 U1/U2/U3 閾值套用 + 裁決 | evaluator G3 分支：Brier−0.25 三分、ECE 對 0.05、期數對 6，閾值讀 frozen criteria（#12 不複製常數） |

### G4（相對強度部署生命週期；**不 gate 方向 arena**，除非 D-2 選 Reading B）

| # | gap | 工作項 |
|---|---|---|
| G4-W1〔now〕 | 升級方向判定器整支未實作 | 新 `scripts/upgrade_econ_verdict.py`：net_excess>0 ∧ HAC-t≥2.0 ∧ **DSR≥0.95（硬條件，非衰減軌純標註）** ∧ deflated_ann>0；純函式鏡射既有 `revalidate_verdict.py` decay evaluate + `--selftest` fixture |
| G4-W2〔now〕 | v0 指示「讀 `revalidation_ledger` 追 streak」＝**讀錯表** | **校正**：streak 讀 `revalidation_verdict.state`（現有 `_prior_streak` 即讀此，track 換 `A_upgrade`）；四指標經 `_m()` 讀 `revalidation_ledger`（現碼即此）或 `revalidation_verdict.metric_snapshot`（兩處皆有值，實查）。附「判準→正確來源表」對照（§6.9） |
| G4-W3〔now/治權〕 | 無 `established` 寫入器；`econ_verdict_rule` schema=(horizon,verdict,source_report,note,created_at) **無 as_of/streak 欄**、無法原地記連續輪證據 | **裁決 D-9**：established 持久化落 `revalidation_verdict` upgrade 軌（有 as_of_date/state/metric_snapshot 可記連續輪證據），`econ_verdict_rule` 之 UPDATE 僅為衍生視圖（升級成立後）。Phase 0 定案，不可 Phase 1「established 寫入器就緒」與現表結構矛盾 |
| G4-W4〔治權〕 | `consecutive_k` 未凍（frozen=FALSE） | 人拍板凍結（U4 定 2 或 3），否則「先凍後跑」無機械時序力 |
| G4-W5〔now〕 | h20_dead_no_shortcut 無機械閘 | 升級迴圈明確排除 `econ_verdict='dead'` 之 horizon（H20，實查=dead） |
| G4-W6〔live〕 | 僅 1 輪（as_of=2026-05-31）、DSR≈0.756<0.95 | 等 ≥2 非重疊 live 輪累積（資料層，非 code） |

### G5

| # | gap | 工作項 |
|---|---|---|
| G5-W1〔now〕 | 無可達的 G1-G2（+守門5）原子 evaluator | `evaluate_arena_admission.py`（§6.3）讀各源表 → AND 收斂 → 單筆 evaluated_pass/fail（複用 direction gate `all()`+單 UPDATE 樣板）；含守門5 時序錨 |
| G5-W2〔now/治權〕 | retry 鏈無顯式連結欄；superseded 死列（990ddea）無後繼 gate | `arena_admission_gate` 加 `supersedes_gate_id text REFERENCES ...` + trigger 斷言（**DDL/schema 變更 → hugo 拍板 D-10**）；建新 gate 時**回填** 990ddea 的後繼；澄清語義瑕疵（真 fail 後 retry＝保留 evaluated_fail 列 + 開新 gate_id，superseded 專指「未評估即棄」，見 §10-#8） |
| G5-W3〔now/治權〕 | U6 放鬆簽核零機械強制 | 新 `verify_gate_relaxation_signoff.py`（§6.7）：解新 gate vs 被 supersede 舊 gate 的 criteria 門檻，偵測放鬆（alpha↑/min_clusters↓/ece_ceiling↑/nonoverlap_n↓…），放鬆則要求 note 含人簽核理由。**須先白名單化「放鬆語意」定義 D-11** |
| G5-W4〔now〕 | 新專表無狀態白名單 trigger | `migrate_arena_admission_gate_ddl.py`（§6.1）：表 DDL + `trg_arena_admission_no_goalpost` 白名單 trigger + selftest 固化紅綠鎖 |
| G5-W5〔now〕 | `preregister_unfreeze_gate.py` 仍被 a2 launch §1 當「G1-G5 原子」依賴、實為 stub | 於該支 evaluate() docstring 加 deprecate 註記（指向新 `evaluate_arena_admission.py`），防下游再誤依賴（執行層、非治權） |

---

## 五、表 schema（憲章 v1.39.0 強制）

### 5.1 新表 `arena_admission_gate`（G5-W2/W4；住所＝`migrate_arena_admission_gate_ddl.py`）

```sql
CREATE TABLE IF NOT EXISTS arena_admission_gate (
  gate_id           text PRIMARY KEY,
  axis              text NOT NULL
                      CHECK (axis IN ('shared_foundation','direction','relative_strength')),
  purpose           text,
  criteria          jsonb NOT NULL,            -- G1+G2(+守門5) 判準快照(值+口徑+溯源;G1/G2 子塊逐鍵複製自 990ddea)
  criteria_sha      text  NOT NULL,            -- 覆算錨(挪門柱=RAISE)
  status            text  NOT NULL DEFAULT 'draft'
                      CHECK (status IN ('draft','frozen','evaluated_pass','evaluated_fail','superseded')),
  preregistered_at  timestamptz NOT NULL DEFAULT now(),
  approved_by       text,
  approved_at       timestamptz,
  git_sha           text,
  evaluated_at      timestamptz,
  result_snapshot   jsonb,                     -- G1/G2 逐關 pass/fail + missing_in_db/sampled_n 揭露旗標
  evaluation_ref    text,
  supersedes_gate_id text REFERENCES arena_admission_gate(gate_id),   -- G5 retry 鏈
  note              text,
  CONSTRAINT chk_aag_frozen_signed CHECK
    (status <> 'frozen' OR (approved_by IS NOT NULL AND approved_at IS NOT NULL)),
  CONSTRAINT chk_aag_evaluated_stamped CHECK
    (status NOT IN ('evaluated_pass','evaluated_fail')
     OR (approved_at IS NOT NULL AND evaluated_at IS NOT NULL))
);
-- trigger trg_arena_admission_no_goalpost：鏡射 trg_unfreeze_no_goalpost
--   ① 非 draft 不得刪(廢止=superseded)  ② 非 draft criteria 不可變  ③ 凍後簽核欄鎖定
--   ④ 狀態白名單:draft→frozen|superseded；frozen→evaluated_pass|evaluated_fail|superseded；終態不可回改
```

### 5.2 新表 `feature_panel_hash_baseline`（G2-W1/W4）

```sql
CREATE TABLE IF NOT EXISTS feature_panel_hash_baseline (
  axis            text NOT NULL CHECK (axis IN ('relative_strength','direction')),
  source_table    text NOT NULL,          -- 'feature_values' | 'daily_direction_feature_values'
  panel_date      date NOT NULL,
  row_count       bigint NOT NULL,
  value_hash      text NOT NULL,          -- 依 normalization_ref 正規化後之逐列聚合 hash
  normalization_ref text NOT NULL,        -- value 正規化規則版本(D-6);hash 口徑可溯
  frozen_as_of    date NOT NULL,          -- 凍結快照 as-of 點(釘死,非 live 增生集)
  frozen_at       timestamptz NOT NULL DEFAULT now(),
  git_sha         text,
  PRIMARY KEY (axis, source_table, panel_date)
);
```

### 5.3 新表 `score_repro_baseline`（G2-W2）

```sql
CREATE TABLE IF NOT EXISTS score_repro_baseline (
  horizon      int  NOT NULL,
  panel_date   date NOT NULL,
  model_id     text NOT NULL,             -- 正典 feats_hash 家族全名(D-7 釘死;排除另一家族與 H82)
  row_count    bigint NOT NULL,
  score_hash   text NOT NULL,             -- 逐 stock round(score,5) 排序後聚合 hash
  frozen_at    timestamptz NOT NULL DEFAULT now(),
  git_sha      text,
  PRIMARY KEY (horizon, panel_date, model_id)
);
```

### 5.4 新表 `restatement_review_queue`（G2-W3 / U5）

```sql
CREATE TABLE IF NOT EXISTS restatement_review_queue (
  id            bigserial PRIMARY KEY,
  source_table  text NOT NULL,
  vintage_from  date, vintage_to date,
  diff_summary  jsonb NOT NULL,           -- 修訂列/欄/幅度摘要(#1 可溯源)
  status        text NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','signed_off_benign','signed_off_action')),
  signed_by     text, signed_at timestamptz, note text,
  created_at    timestamptz NOT NULL DEFAULT now()
);
```

### 5.5 新表 `probability_live_reading`（G3-W1，**條件式**——僅「另開相對強度 live arena」時建；方向 arena 不建）

```sql
CREATE TABLE IF NOT EXISTS probability_live_reading (
  horizon       int  NOT NULL,
  panel_date    date NOT NULL,
  model_family  text NOT NULL,
  stock_id      text NOT NULL,
  p             double precision NOT NULL,
  realized_label int,                     -- t+H 結算後回填
  brier_period  double precision,         -- per-period(結算後)
  ece_period    double precision,
  settled_at    timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (horizon, panel_date, model_family, stock_id)
);
```

### 5.6 既有表（讀取/寫入；結果落哪張表）

| 表 | 角色 | 本計畫讀/寫 | 關鍵欄（實查） |
|---|---|---|---|
| `attestation_result` | G1 對帳 verdict | **讀**（G1 斷言）；G1-W1 **加欄** `audit_until` | passed / value_mismatch / extra_in_db / missing_in_db / exempt_n / sampled_n / coverage_gap_n / incomplete_n / audit_since / note |
| `prediction_unfreeze_gate` | superseded 史料 + 990ddea 凍結判準來源 | **讀**（複製 criteria + sha 錨） | gate_id / criteria(jsonb) / criteria_sha / status / approved_by / approved_at |
| `validation_evidence` | evidence_ledger_gate | **讀**（G1-W5 斷言；先查 19 全綠） | status(green/amber/red) |
| `revalidation_baseline` / `probability_calibrator` / `econ_verdict_rule` | baseline_refs | **讀**（存在且未變斷言） | — |
| `feature_values` | G2 相對強度特徵 | **讀**（hash baseline） | panel_date / 35 特徵；36 panel（含 post-FREEZE 2026-06-30） |
| `daily_direction_feature_values` | G2 方向特徵（D-1） | **讀**（hash baseline，若補） | panel_date；19.2M 列、至 2026-07-09 |
| `model_registry` | G2 score 復現 artifact | **讀**（正典家族 D-7） | model_id / feats_hash（ce62866 / 3a4e66 兩家族） |
| `probability_oos_sample` | G2 score baseline 來源 | **讀**（消歧家族） | horizon / panel_date(25) / model_family('RankRidge') / stock_id / score |
| `revalidation_verdict` | G4 升級 streak + 指標 | **讀+寫**（upgrade 軌，D-9） | as_of_date / cell / track / state / metric_snapshot(jsonb: dsr/hac_t/net_excess/deflated_ann) |
| `revalidation_ledger` | G4 四指標原料 | **讀**（`_m()`） | as_of_date / stage / horizon / model / metric_name / metric_value / hac_t / n_periods |
| `direction_gate` | 門一/門二（方向軸確立） | **讀**（開賽 AND 前置；D-2 走門二） | gate_id / status（6 dgate_arena approved；dgate_H/D 全 evaluated_fail） |
| `direction_arena_prediction` | 方向 arena live ledger | **讀**（守門5 min created_at；0 列） | created_at |
| `direction_arena_policy` | 門二 futility | **讀** | futility_min_clusters=60 / futility_z=1.645（frozen） |

---

## 六、python 程式規畫（憲章 v1.39.0 強制）

每支守 CLAUDE #29(a)(d)：個別可執行（`import _bootstrap`）、執行指令矩陣、無參數 graceful、`--selftest` 純紅綠。

### 6.1 `scripts/migrate_arena_admission_gate_ddl.py`（新；G5-W4）
- `run(dry:bool)->int`：冪等建 `arena_admission_gate` + `trg_arena_admission_no_goalpost` + `supersedes_gate_id` FK。
- `check()->int`：表/trigger/CHECK 存在性斷言。
- `selftest()->int`：adhoc draft 假列實測非法狀態轉移（frozen→draft、非 draft 刪、凍後改 criteria）必 RAISE；測畢刪 draft。
- 讀/寫：DDL only。

### 6.2 `scripts/preregister_arena_admission_gate.py`（新；G5-W2 / §3.2 託管）
- `_build_criteria(cur)->dict`：組 G1+G2(+守門5) 判準；**逐鍵複製** 990ddea 的 `g1_data`/`g2_repro` 子塊。
- `_assert_inherited_sha(cur, crit)->None`：對複製子塊之 sha 做**等值斷言 == 990ddea 對應摘要**（機制置換未挪門柱）。
- `preregister(note)` / `freeze(gate_id, approved_by)` / `check(gate_id)` / `selftest()`。
- `--backfill-supersedes`：回填 990ddea 死列後繼 gate_id。
- 簽名：`main(argv=None)->int`；輸出 → `arena_admission_gate`（draft→frozen，hugo TTY 親核）。

### 6.3 `scripts/evaluate_arena_admission.py`（新；G5-W1，**核心裁判**）
- `_assert_clean_tree()->None`：鏡射 `evaluate_direction_gate._assert_clean_tree`（git 樹乾淨）。
- 守門鏈（依序，任一敗 exit 1）：`status='frozen'` → `criteria_sha` 覆算 == 存列 → **守門5** `approved_at < min(created_at)`（`direction_arena_prediction` / 相對強度 live 工件，先凍後跑）。
- `_check_g1(cur, crit)->(bool, dict)`：讀 `attestation_result` 最新列，斷言 `passed AND value_mismatch=0 AND extra_in_db=0 AND coverage_gap_n=0 AND incomplete_n=0 AND audit_until>=CURRENT_DATE−3d`；`missing_in_db`/`sampled_n`/`audit_since` 入 snapshot **揭露不斷言 0**；併 `evidence_ledger_gate`（validation_evidence 綠或債紅在帳）+ `baseline_refs` 存在。
- `_check_g2(cur, crit)->(bool, dict)`：呼 `freeze_feature_panel_hash.verify` + `verify_score_repro.verify` + `restatement_review_queue` 無 pending（或已簽核）；方向軸迴歸依 D-1。
- `_evaluate_one(cur, gate_id)->None`：`passed = g1_ok and g2_ok`（**原子 AND，無 per-component 覆寫**）→ 單筆 `UPDATE status=evaluated_pass|evaluated_fail, result_snapshot, evaluated_at, git_sha`。
- `selftest()->int`：合成 fixture 單測 `_check_g1`/`_check_g2` 純判定 + trigger 白名單。
- 簽名：`main(argv=None)->int`；指令矩陣 `--evaluate <gate_id>` / `--check` / `--selftest` / 無參數印矩陣。

### 6.4 `scripts/freeze_feature_panel_hash.py`（新；G2-W1/W4）
- `_panel_hash(cur, table, panel_date, norm_ref)->(int, str)`：依正規化規則（D-6）算 row_count + value_hash。
- `freeze(axis, source_table, frozen_as_of)->int` / `verify(axis, source_table)->int`（重算 35 panel 比對、0 mismatch=0 else 1）。
- 讀 `feature_values`/`daily_direction_feature_values`；寫/讀 `feature_panel_hash_baseline`。

### 6.5 `scripts/verify_score_repro.py`（新；G2-W2）
- `_rescore(horizon, panel_date, model_id)->rows`：`artifact.load`（正典家族 D-7）→ 凍結 panel 重打分 → `round(·,5)`。
- `freeze()->int` / `verify()->int`（逐 (h,panel) score_hash == baseline）。
- 讀 `model_registry`/`feature_values`/`probability_oos_sample`；寫/讀 `score_repro_baseline`。

### 6.6 `scripts/report_restatement_diff.py`（新；G2-W3 / U5）
- `_refetch_vintage(table, window)->frame` → `_diff(db_frame, fetched)->dict`。
- `run(tables)->int`：diff 空=pass、非空→寫 `restatement_review_queue`（status=pending）出人裁報告。
- 讀 in-scope 源表；寫 `restatement_review_queue`。

### 6.7 `scripts/verify_gate_relaxation_signoff.py`（新；G5-W3 / U6）
- `_extract_thresholds(criteria)->dict`（白名單化門檻鍵 D-11）。
- `_detect_relaxation(new, old)->list`（alpha↑/min_clusters↓/ece_ceiling↑/nonoverlap_n↓…）。
- `run()->int`：新 gate 若相對 `supersedes` 舊 gate 放鬆且 note 缺人簽核 → exit 1。
- 讀 `arena_admission_gate`（新列 vs supersedes 鏈）。

### 6.8 `scripts/upgrade_econ_verdict.py`（新；G4-W1/W2/W3/W5，**相對強度部署軌**）
- `_m(cur, ...)->dict`：四指標，讀 `revalidation_ledger`（鏡射 `revalidate_verdict._metrics`）。
- `_prior_upgrade_streak(cur, cell, as_of)->int`：讀 `revalidation_verdict.state`（track=`A_upgrade`），連續 pass 計數。
- `_evaluate_upgrade(m)->bool`：`net_excess>0 and hac_t>=2.0 and dsr>=0.95 and deflated_ann>0`（DSR 硬條件）。
- `run(as_of)->int`：排除 `econ_verdict='dead'`（H20）；連續 `consecutive_k` 輪 pass → 寫 `revalidation_verdict`（state=`established_upgrade`），established 持久化落此表（D-9）；`econ_verdict_rule` UPDATE 為衍生視圖（可選）。
- `selftest()->int`：合成 fixture（3 輪連 pass → established；中斷 → 不升）。

### 6.9 判準 → 正確來源表/欄位對照（v0 多處撞表名錯配，附此表消歧）

| 判準/量 | 正確來源表.欄 | 誤植（v0） |
|---|---|---|
| G4 升級 streak | `revalidation_verdict.state`（track='A_upgrade'） | ~~revalidation_ledger~~ |
| G4 四指標（net_excess/hac_t/dsr/deflated_ann） | `revalidation_ledger`（`_m()`）或 `revalidation_verdict.metric_snapshot` | — |
| G4 established 持久化 | `revalidation_verdict`（有 as_of/state/metric_snapshot） | ~~econ_verdict_rule（無 streak 欄）~~ |
| G1 對帳 | `attestation_result`（最新列 + 加 `audit_until`） | — |
| G2 score baseline 家族 | `model_registry.feats_hash`（正典 D-7）× `probability_oos_sample` | ~~model_family='RankRidge' 單值不消歧~~ |

### 6.10 既有 script 修改（執行層、同批落地）
- `run_arena_daily_pipeline.py`：`_gate_approved()` 加 `arena_admission_gate evaluated_pass` AND 前置；L90-91 拒跑字串「unfreeze GATE」→ 新 gate。
- `run_arena_round.py`：`live_round()` 加同 AND 前置；L8 docstring + L70-71 拒跑字串同步。
- `preregister_unfreeze_gate.py`：evaluate() docstring 加 deprecate 註記（G5-W5）。

---

## 七、分階段 + 元件/端點

### Phase 0｜治權/拍板（阻塞後續，須 hugo）
拍板 §8 治權修訂 + 下列裁決題（每項均標「須 hugo」）：

| 代號 | 裁決題 |
|---|---|
| D-1 | G2 方向軸特徵迴歸：補做 vs 明文標誠實債 |
| D-2 | 方向 arena 確立走門二（建議 Reading A）vs 相對強度 G3/G4（Reading B，須耦合理由）；是否另開相對強度 live arena（獨立軸/排程/gate） |
| D-3 | verdict 落新專表 `arena_admission_gate` vs 復用（建議前者） |
| D-4 | G1 以 `passed=True` 單一斷言 vs 補 `missing_in_db` 容忍斷言 |
| D-5 | G1 sampled(27 表 40 股) vs 全宇宙 run |
| D-6 | feature value 正規化規則（hash 口徑） |
| D-7 | 正典 feats_hash 家族（ce62866 vs 3a4e66）+ 校正 990ddea scope H82 不一致 |
| D-8 | 非重疊期定義 + live rebalance 頻率（月/季頻）入憲 |
| D-9 | G4 established 持久化落 `revalidation_verdict` upgrade 軌 |
| D-10 | `supersedes_gate_id` FK 補欄（DDL 變更） |
| D-11 | U6「放鬆語意」白名單定義 |
| — | 凍結 `consecutive_k`（U4：2 或 3，G4-W4） |
| — | 先查清 `validation_evidence` 19 列全綠是否應有債紅（G1-W5） |

### Phase 1｜clean-room 可逆、現在即可做（不需 live 新資料）
> 完成即可讓方向 arena **以 review-only tier 開賽**（G1+G2 硬綠、確立走門二待 ≥60 clusters）。

- 建 `arena_admission_gate` + 白名單 trigger + `supersedes_gate_id`（G5-W2/W4）；複製 990ddea 判準 + sha 等值斷言 + 回填後繼。
- G1：加 `audit_until` 欄、（依 D-5）跑全宇宙 reconcile、gate 接線、evidence_ledger_gate/baseline_refs 斷言（G1-W1/W2/W3/W4/W5）。
- G2：`feature_panel_hash_baseline`（相對強度 + 依 D-1 方向軸）+ `freeze_feature_panel_hash.py`；`score_repro_baseline` + `verify_score_repro.py`；`report_restatement_diff.py` + `restatement_review_queue`（G2-W1/W2/W3/W4）——**全在凍結 as-of 快照段，今日即可 baseline 並跑**。
- G4：`upgrade_econ_verdict.py` + streak + established 寫入器 + h20 排除（G4-W1/W2/W3/W5，**碼就緒、資料 pending**）。
- G5：`evaluate_arena_admission.py` 原子 evaluator（含守門5）+ selftest；`verify_gate_relaxation_signoff.py`（G5-W1/W3）；`preregister_unfreeze_gate.py` deprecate 註記（G5-W5）。
- 接線：`_gate_approved()` + `live_round()` 加 G1+G2 AND 前置 + 修 in-code 前置字串（fail-closed）。
- **回退設計（每項附）**：新表 `DROP TABLE`；`audit_until` 反向 `ALTER TABLE ... DROP COLUMN`；接線 revert 為 git diff（可逆）。

### Phase 2｜須等 live 新資料（開賽後持續累積）
- **掛排程**：a2 launch §5 已有現成 crontab 三行（daily_pipeline / settle / scoreboard，`10 23 * * 1-5` 等）；擁有者由 hugo 指定。**排程屬開賽後常態運作、非開賽硬前置**（v0 §6.C 與 Phase 2 矛盾已修正）。
- 累積 live 非重疊期。
- **方向 arena 確立**：≥60 clusters → `evaluate_direction_gate` 三關 → review 翻確立-eligible。
- **G4 升級**（相對強度部署）：≥2 連續輪四條件皆 pass → `revalidation_verdict` established。

---

## 八、治權修訂提案（逐條，須 hugo 拍板）

> **共同精神**：原則不變（G1-G5 全數實質通過前 live 數字不得入確立級宣稱）、只換機制指向。靈魂（系統核心思想 v1.8.0）無 unfreeze gate/arena 前置/G1-G5 字面，**不動**（憲章「三不動」完整性已審視：僅涉解凍事件/資料凍結非 gate 機制，判定不需改——此留痕本身入本節）。

### 8.1 實質條文（升版）
| 檔 | 位置 | 改動 | 性質 |
|---|---|---|---|
| **原則精華**（SSOT） | L77「FREEZE→解凍」子條 | 「live 准入依 `prediction_unfreeze_gate` evaluate 紀律」→「依 master plan §4 G1-G5 實質驗證機制（判準值 SSOT=§4.3；權威凍結值=`arena_admission_gate.criteria` 承接 990ddea；實作 gate 另計畫）」+ 註原 gate 07-16 退 superseded | 升版 |
| **原則精華** | L173 修訂歷程 | 保留 v1.9.0 舊條（忠實記 07-12）；**新增 v1.9.1** 記 07-16 拍板 | 留痕 |
| **憲章** | L131 輸出契約硬綁④ | 「live 準確率唯解凍後依 unfreeze gate 紀律取得」→「**唯 G1-G5 硬前置通過後、經 arena live settle 依 direction_gate 紀律取得**」（精確化，前置≠準確率來源） | 升版 |
| **憲章** | L130 direction_gate「鏡射 unfreeze gate 狀態機」 | **定案加註**：「該 gate 物件已退史料、此處僅引狀態機模式非 G1-G5 評估邏輯」 | 升版（不再「可選」） |

### 8.2 檔名級聯 + 版本連動（#19 一處改全鏈對齊；v0 漏列，本版補齊）
原則精華 v1.9.0→**v1.9.1**、憲章 v1.45.0→**v1.46.0** 觸發之硬編檔名/自引全須同步：

| 同步點 | 內容 |
|---|---|
| 原則精華檔名 | `原則精華_v1.9.0.md`→`v1.9.1.md` + line1 標題 + line5 憲章指針 |
| 憲章檔名 | `大憲章_v1.45.0.md`→`v1.46.0.md` + line1/line4 自引 |
| 下游硬編引用 | README:14/23、HANDOFF:18/148、CLAUDE:4/26/46、憲章:4/188、原則精華 line5 |
| **HANDOFF.md** | L18 live 准入狀態（「FREEZE 已解凍→依 unfreeze gate 紀律」）→ 新機制；#31 HANDOFF=新機接續 SSOT，gate 退役須同步 |
| CLAUDE.md | L26 §2 blockquote 工具層引用同步指向 master plan §4 G1-G5 |
| README.md | L14 狀態段「依 unfreeze gate 紀律」→「依 master plan §4 G1-G5（unfreeze gate 已退史料）」 |

（檔名級聯屬純機械同步 #19，與治權文字改動**同批呈核**。）

### 8.3 報告可更新（同批呈核）
| 報告 | 改動 |
|---|---|
| master plan §4.4 / §4.0 | §4.3 判準值**不動**；註記綁定 `preregister_unfreeze_gate.evaluate()` 之路徑 07-16 退役、G1-G5 實作由本計畫承接 |
| arena plan §1 + a2 launch §1 | 門一「解凍 GATE `--evaluate`」重指向新 `arena_admission_gate` G1-G2；移除對 superseded unfreeze gate 依賴 |

### 8.4 排序紀律（治權文字不先於機制）
**治權升版須序列於或原子綁定於 `arena_admission_gate` 落地 + hugo 重凍之後**。落地前若須更新治權，誠實文字為「原 unfreeze gate 已退役、G1-G5 實作 gate 建置中、此期間 live 數字一律 fail-closed 不入確立級」，**而非**「live 准入依 G1-G5 實質驗證機制」如同已備妥。→ Phase 1 機制落地 → 再 ACTIVE 化治權文字。

**授權邊界**：以上全屬「判準機制指向變更」，依 CLAUDE #19/#26 屬決策層 → hugo 拍板；本計畫只提案、未動任何治權檔。

---

## 九、開賽驗收準則（可機械判定）

**開賽 = A + B + C 全成立**（fail-closed，任一缺即拒）：

### A. 開賽硬前置全綠（G1 + G2，今日即可判）
- **G1**：最新 `attestation_result` 列
  ```sql
  SELECT passed AND value_mismatch=0 AND extra_in_db=0
         AND coverage_gap_n=0 AND incomplete_n=0
         AND run_at > now() - interval '3 days'
  FROM attestation_result ORDER BY id DESC LIMIT 1;
  -- 註:missing_in_db 不斷言為 0(latest=5369,由 exempt_n=19/部分覆蓋 27/端點扣抵 3 吸收);
  --    其吸收機制明列 result_snapshot、sampled_n/audit_since 揭露旗標隨列(D-4/D-5 定案)
  ```
  + `audit_until >= CURRENT_DATE − 3d`（或核心表 `max(date)` 近似）；+ evidence_ledger_gate（`validation_evidence` 綠或債紅在帳）+ baseline_refs 存在；asof_charter(b) governance-satisfied（commit `7d337ec`@07-12 ≤ 新 gate approved_at）。
- **G2**：35/35 panel `value_hash+row_count == baseline`（0 mismatch，任一 mismatch＝舊時點洩入 #8 → FAIL）；4 artifact（正典家族）重打分 100% 列 `round(·,5)==baseline`；`restatement_review_queue` 無 pending（或已簽核）；方向軸迴歸依 D-1。

### B. 確立機制就位並鎖 tier（開賽當下必 pending，不阻擋開賽）
- 方向 arena 開賽即入 `review_observation_only` tier（**永不宣稱確立級**）——此鎖成立本身是 pass 條件；確立級升格待門二 `evaluate_direction_gate`（≥60 clusters）。
- G4 升級 evaluator + streak + established 寫入器（相對強度部署軌）就位；`consecutive_k` **已 frozen**。

### C. G5 治理骨架 + 機械強制到位
- `arena_admission_gate` + `trg_arena_admission_no_goalpost` 存在；`evaluate_arena_admission.py --selftest` exit 0。
- 原子裁決：G1-G2(+守門5) AND 收斂為單一 status，無 per-component 覆寫（無 cherry-pick）；守門5 `approved_at < min(live 工件 created_at)`（`direction_arena_prediction` 現 0 列）。
- retry 鏈：`supersedes_gate_id` 補欄；990ddea 死列後繼已回填。
- U6：`verify_gate_relaxation_signoff.py` 無「放鬆但簽核缺」之 gate。
- **強制**：`run_arena_daily_pipeline.py::_gate_approved()` + `run_arena_round.py::live_round()` 均 AND 檢查 `arena_admission_gate evaluated_pass`，fail-closed；in-code 前置字串已同步。
- 排程屬開賽後常態（非開賽前置）：a2 crontab 三行、擁有者由 hugo 指定。

### D.（非開賽前置，供對照——確立級升格門檻）
- **方向 arena 確立**：≥60 clusters → 門二三關（HAC 命中率 p<alpha ∧ Brier<base ∧ ECE≤ceiling ∧ 單調）。
- **G4 established**（相對強度部署）：連續 `consecutive_k` 輪四條件皆 pass → `revalidation_verdict` established（H20 dead 排除）。

---

## 十、風險與未決問題

### 10.1 對抗審查逐條處置（採納/不採 + 理由）

| # | 面向 | 發現 | 處置 |
|---|---|---|---|
| 1 | 機制 | G1「真綠」略去 `missing_in_db=5369`（假綠前科風險） | **採納**：§2/§3.4/§9 明列 5369 + 吸收機制、驗收 SQL 註明不斷言 0（G1-W2、D-4） |
| 2 | 機制 | G4-W2 讀錯表（應 `revalidation_verdict` 非 `revalidation_ledger`） | **採納**：streak→`revalidation_verdict.state`、指標→ledger/verdict，附 §6.9 對照表（G4-W2） |
| 3 | 機制 | arena code 內 unfreeze-gate 前置字串未列工作項 | **採納**：§3.3/§6.10 增列 `run_arena_daily_pipeline.py:90-91`、`run_arena_round.py:8,70-71` 同步 |
| 4 | 機制/完整性 | asof_charter 不等式方向對新 gate 失準 | **採納**：G1-W4 修為 `commit_time ≤ 新 gate approved_at`（治理在先） |
| 5 | 機制 | G2 雙 feats_hash 家族正典未釘（+990ddea scope H82 不一致） | **採納**：G2-W2/D-7 釘正典家族 + 校正 scope |
| 6 | 治權 | **blocker**：G3/G4 相對強度軸誤植方向 arena、#12 雙棧 | **採納（核心重構）**：§1.3/§3.1 升為前置架構裁決 D-2；方向 arena 走門二、不建 probability_live_reading 平行棧 |
| 7 | 治權 | G2 對方向 arena 假綠（只覆蓋 feature_values） | **採納**：G2-W4/D-1 補方向軸迴歸或標誠實債 |
| 8 | 治權 | 凍結判準託管孤兒（990ddea 未複製回權威 live 列） | **採納**：§3.2/G5-W2 複製 criteria + sha 等值斷言 + 回填後繼 |
| 9 | 治權 | §5 檔名級聯同步漏列 | **採納**：§8.2 補齊 README/HANDOFF/CLAUDE/憲章/原則精華 級聯 |
| 10 | 治權 | 治權文字先於機制落地 | **採納**：§8.4 排序紀律（Phase 1 落地 → 再 ACTIVE 化） |
| 11 | 治權 | 憲章 L130/L131④ 精度 | **採納**：§8.1 L130 定案加註、L131④ 精確化 |
| 12 | 完整性 | evidence_ledger_gate + baseline_refs 未納入；`validation_evidence` 19 全綠與 master plan 紅列預期矛盾 | **採納**：G1-W5 加斷言 + Phase 0 先查清 19 全綠 |
| 13 | 完整性 | 守門5 先凍後跑時序錨遺失 | **採納**：§3.4/§6.3 evaluator 加 `approved_at < min(created_at)` |
| 14 | 完整性 | 排程階段歸屬矛盾（開賽 blocker vs Phase 2） | **採納**：§7 定為開賽後常態、非硬前置；引 a2 crontab |
| 15 | 完整性 | 「門二今日已開」誇大 | **採納**：§2 改述「chokepoint 可放行(6 approved)，門二裁決待 ≥60 clusters evaluate」 |
| 16 | 完整性 | live 增量已恢復（36 panel、post-FREEZE 2026-06-30）未承認 | **採納**：G2-W1 baseline 釘凍結 as-of 快照 + 定義新 panel 行為 |
| 17 | 完整性 | 分階段缺回退欄 | **採納**：§7 Phase 1 附 DROP/反向 ALTER 回退 |
| 18 | 完整性 | `preregister_unfreeze_gate.py` deprecate 未處理 | **採納**：G5-W5 加 deprecate 註記 |
| 19 | 完整性/旁證 | A3 家族三方漂移（live `dgate_a3_threelens_{20,40,82}=preregistered` 無 `_r2`，repo 用 `_r2`，MEMORY 記「_r2 已簽」） | **採納為旁證**（非本 gate 阻塞）：實查確認 live 無 `_r2` 列；建議開賽前先對帳 A3 repo/DB/記憶三方一致（列入 §10.2 未決） |

### 10.2 仍待釐清（誠實標註）
1. **軸別（D-2）**：本計畫建議方向 arena 走門二、G3/G4 歸相對強度部署——須 hugo 確認；若要跨軸耦合須補理由；若另開相對強度 live arena 須獨立軸/排程/gate。
2. **G1 抽樣（D-5）**：全宇宙 run vs 接受 27 表 40 股 sampled 揭露。
3. **G2 正典家族（D-7）**：`probability_oos_sample.model_family='RankRidge'` 單值無法消歧 ce62866/3a4e66；須查部署路徑釘死並校正 990ddea scope。
4. **非重疊期 + rebalance 頻率（D-8）**：直接決定 6 期累積速度與升確立時程；DB 未定，須入憲。
5. **G4 DSR 雙用途**：`dsr_annotate=0.95` 衰減軌純標註、升級軌硬條件——是否拆 `dsr_upgrade_floor` 以免耦合。
6. **validation_evidence 19 全綠**：與 master plan §1.4 債紅列預期矛盾，開賽前須查清（漏 seed / 已修復留痕 / 人裁除名）。
7. **A3 三方漂移**：開賽前對帳 repo/DB/記憶一致（旁證）。
8. **retry 語義瑕疵**：判準字面「fail 後舊列 superseded」與 trigger「evaluated_fail 終態不可轉 superseded」有張力——真 fail 後 retry＝保留 evaluated_fail 列 + 開新 gate_id，superseded 專指「未評估即棄」；建議校正判準文字。

---

*本計畫書基於 2026-07-16 live code（Read/Grep）+ live DB（`augur` PostgreSQL）盤點合成，並納入三面對抗審查（機制正確性/治權一致性/完整性）。核心前提「G1-G5 評估碼＝`preregister_unfreeze_gate.py:171` 明標『本計畫內不可達』＝未實作、全部須新建」經實證。所有現況陳述可溯源至 §二/§五實查值；判準變更明確標「須 hugo 拍板」（D-1…D-11 + consecutive_k + validation_evidence）。靈魂＝寧誠實紅不假綠：missing_in_db=5369、validation_evidence 全綠疑點、軸別誤植、凍結判準託管孤兒——皆據實揭露，不美化。*