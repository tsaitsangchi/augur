# augur 自我迭代進化總控計畫 v2（RAWEVO／TWEVO／LAIEVO 三軸）

- **檔案**：`reports/augur_self_evolution_master_plan_v2_20260726.md`
- **日期**：2026-07-26（本檔所有「實查」數字皆為當日親驗，時戳見附錄 A）
- **性質**：三軸自進化之**交互契約與執行序** SSOT v2。對 `reports/augur_triple_self_evolution_master_plan_20260726.md`（下稱 TRI-v1）作**增量修訂**：本檔明列「保留／修訂／撤回」三類處置，未被本檔提及之 TRI-v1 條文續行。
- **拍板狀態**：本檔為**計畫書**，尚未採納。採納碼 `V2-P-yes`。採納 ≠ 執行；所有執行仍需各自 `*-go`。
- **既有命名一律逐字沿用**：`RAWEVO`／`TWEVO`／`LAIEVO`、三軸 `*-P-yes`／`*-Sx-go`／`*-Bx-go`、`FZ-keep`／`GATE-keep`／`PME-AUTO-B`／`APPROVED-NO-EXEC`。新增者一律以 `V2-` 或 `GATE-raise` 前綴，不覆用舊碼。

**閱讀導引（30 分鐘）**：趕時間只讀 §0（三分鐘判斷要不要重拍板）＋ §2（成敗定義）＋ §6.0/§6.1（今天要做什麼）＋ §8（人閘）＋ §11（誠實天花板）。§3 是本次修訂的主體（交互優化），§4／§5 是 v1.39.0 要求的表與程式落實，§10 是被砍掉的條目。

---

## §0 本次修訂之地基級更正（三分鐘判讀）

### 0.1 一句話

**LAIEVO 過去所有「能力數字」的量尺，今日經親驗證明失效；而同型的病（沒有地板臂、沒有對照、判準與證據方向可以相反）在 TWEVO 與 RAWEVO 也存在，只是還沒被人問過。** 三軸計畫的骨架大致成立，但「怎麼知道它有沒有變好」這一層地基必須重做，而重做之前不應該再蓋任何帳本。

### 0.2 舊尺如何失效（親驗、可複現）

| 事實 | 證據 |
|---|---|
| 舊 `_score` ＝金標之 CJK 雙字元組覆蓋率；gold 全出自三個固定模板 | `scripts/evolve_cycle.py:135` |
| 一條**完全不看題目**的常數樣板：集A 0.654／集B 0.722；現役 serving `pp_3ab2efebb04e` 帳本記 **0.492** | 現役冠軍**低於零知識地板** |
| 把 gold 內所有數字換成 9 當答案，仍得 1.000 | 事實敏感度 **0%** |
| `think:false` 對 qwen3:4b **無效**；`num_predict=400` 下 100% `done_reason='length'` | 被打分的是**截斷的思考鏈**，不是答案 |
| 「固定集」按 `md5(prompt)` 排序 LIMIT 12，gold 每日成長即換題（帳本 `44893a73fbfc` vs 現行 `a8b466844fe5`）；gold 今日 983→**1103**（今日新增 824 列） | 0.256→0.325→0.383→0.492 **跨的不是同一把尺** |
| `local_model_version` 五版之 `anchor_hash`／`eval_code_hash`／`gate_id` **全 NULL** | 母計畫設計的三 hash 挪門柱鎖**自落地起空轉** |
| `local_model_gold_sample.verdict` 1103/1103 全為 `'oracle_pass'` | 常數而非篩選；系統中**不存在**該 oracle（真 oracle 有 5 個，住 `src/augur/deliberation/verifiers.py`，gold 一個都沒用到） |

**推論**：今日之前所有 LAIEVO 能力數字（0.492／0.567／0.521／0.511／0.533…）**全部無證據力**；不是「樣本太小」，是**量測無效**。

### 0.3 新尺已建成（S0，2026-07-26 落地）

- 凍結題庫 `local_model_eval_item`（`set_id=4183475c5089`，L1_RETRIEVED／L2_NO_RETRIEVAL／L3_ABSENT／L4_AMBIG 各 30 題，共 120）；帳本 `local_model_eval_run`；兩表皆掛誠實閘（DELETE/TRUNCATE 拒、UPDATE 綁 `SET LOCAL augur.honesty_write='on'`），負向測試已實證會擋。
- 判準 `src/augur/evolution/behavior_rubric.py`：F（事實逐字）／P（指名正確 SSOT 表）／A（該拒答或消歧義）三軸 **0/1 確定性、永不平均**；評測器 `eval_code_hash=f3075238eb55`，跨尺比較 **fail-loud**（已實戰觸發）。
- 四個離線控制臂（零 LLM、確定性，實查 12 列帳本）：

| 臂 | F | P | A | 意義 |
|---|---|---|---|---|
| ceiling | 1.000 | 1.000 | 1.000 | 尺可被滿足，非假嚴格 |
| floor | 0.000 | 0.000 | 0.000 | 舊尺給它 0.654 的樣板，新尺全滅 |
| shuffled（同層答錯內容） | 0.167 | 0.900 | 0.967 | **P/A 測的是行為類別選對，不測內容** |
| mismatched（跨層選錯行為） | 0.000 | 0.267 | 0.000 | 行為選錯即全滅 |

- **判讀鐵則（事前預註冊）**：任何臂須**同時勝過 floor 與 mismatched** 才有證據力。
- **誠實限制**：A 軸進步只能宣稱「更會選對行為」，**不得**宣稱「答得更準」；唯 F 軸對內容敏感。

### 0.4 新尺的**新發現**（本檔首次記載，五份計畫與 TRI audit 皆未載）

把已存的四臂按 layer × axis 拆開後：

| 格 | ceiling | shuffled | mismatched | floor | 是否有內容鑑別力 |
|---|---|---|---|---|---|
| **F @ L1** | 1.000 | **0.167** | 0.000 | 0.000 | **有（唯一）** |
| P @ L1 | 1.000 | 0.900 | 0.533 | 0.000 | 弱 |
| P @ L2 | 1.000 | 0.900 | 0.000 | 0.000 | 弱 |
| A @ L3 | 1.000 | **0.967** | 0.000 | 0.000 | **無** |
| A @ L4 | 1.000 | **0.967** | 0.000 | 0.000 | **無** |

**這件事直接決定三軸交互能不能被量測**：三軸中**唯一真正已接上的邊是 RAW→LAI**（`scripts/build_eval_set.py` 直接讀 `column_catalog`／`field_correlation`／`knowledge_item` 產題），而它的產物正好落在 L3／L4 —— 那兩格由建構本身決定**無法與「同層答錯內容」區分**。

> 結論措辭必須誠實：三軸交互目前不是「不成立」，而是**用現有量尺不可量測**。

### 0.5 `base` 臂在現行組態下結構性無效（本輪親驗）

- 兩支 `eval_local_model.py --arm base`（16:23、17:42 各一支）合計約 **2.2 小時**機器時間；`~/logs/eval_arms_20260726.log` 中 `── base ──` 段落**零輸出**，`local_model_eval_run` **零 base 列**（18:33 實查仍為 12 列）。
- 機制：`think:false` 無效 → 每題撞 `num_predict` 上限 → `eval_local_model.py:152` 判 INVALID → 整輪無有效題。
- 對照：同一題走 `format=FORMAT_SCHEMA`（grammar 臂路徑）實測 `done_reason=stop`、108 token、生成約 6 秒。
- **推論**：三臂成本不是「約 6 小時」而是「grammar ≈12 分＋behavior ≈12 分＋一個結構性無效的 base 臂」。18:28 起 grammar 臂已自動接手，預期約 18:40 出第一個有效 LLM 臂數字。

### 0.6 波及範圍：哪些段落作廢

| 檔案／段落 | 處置 | 理由 |
|---|---|---|
| `augur_local_ai_evolution_loop_plan_20260725.md` §六「部署工作域金標分數逐版單調升、通用能力錨集零退步」 | **作廢** | 兩個判準對象在 DB 與 repo **皆無載體**（無部署域金標表；「171 錨集」＝`data/distill/sft.jsonl` 是訓練檔、無任何評測端引用，拿來當錨即 train-on-test） |
| 同上 §三(3) 四補丁之 (b)(c)「錨集 byte hash／評分程式 hash 釘入 gate」 | **作廢（自落地即空轉）** | 三 hash 全 NULL |
| 同上 §四程式表（`evolve_capture.py`／`evolve_train_lora.py --machine gb10`／`evolve_gate_eval.py`）與 §五 `evolution_sample` 表 | **作廢** | 三支腳本 repo 全無；GB10 已由 hugo 2026-07-25 宣告不存在；`evolution_sample` 表不存在（實際落點是 `local_model_gold_sample`） |
| `augur_local_ai_route_b_no_gpu_plan_20260726.md` §一/§六.1/§六 B1 驗收/§4.4 gain 語意/L-V3/L-V8 | **全段重寫**（本檔 §3.4 M-2、§6.1） | 全部建築在已失效的 `_score` 上 |
| 同上 §5.2(2) `export_evolution_sft.py --min-verdict`、§4.1「僅前三 verdict 入訓練視圖」 | **作廢** | verdict 為常數，過濾器先天無效 |
| 同上 §5.2(6) 部署域評測器列為「可選、P1.5 再補、不阻塞 B1」 | **順序反轉**：尺是前提不是補丁；且實際實作名為 `scripts/eval_local_model.py` | 尺壞則 B1 全部輸出無意義 |
| 同上 §5.2(3)(5)、§七 依賴（LoRA 六支＋`lora_training_run`＋llama.cpp「須 spike」） | **降級為條件性**（§10 明確不做＋復活條件） | 4B QLoRA no-go（GTX 1650 4GB sm_75 無 bf16）；唯一權重鏈已親驗定案為 PEFT→`convert_lora_to_gguf.py`→Modelfile ADAPTER；語料 87% 為文獻 metadata，背進權重＝訓練幻覺 |
| `augur_tw_prediction_self_evolution_loop_plan_20260726.md` §0 現況錨「run_id=5／run_id=6」 | **修訂為 `run_id=1`** | 本機 `evolution_run` 僅 run_id=1（序列 last_value=1，非刪除）；整數 run_id 跨機不可攜 |
| 同上 §8 對偶介面（`consumed_briefs`／`lora_*`／「讀對方 ledger status」錯峰） | **撤回並改寫**（本檔 §3.2／§3.3 C3） | 所引零件多數無實體；錯峰改為單槽鎖 |
| 同上 §8.2「brief 進 LAIEVO gold 題庫」 | **撤回** | gold 是死渠道；敘事型 brief 亦無法成為機械可判之凍結題 |
| `augur_raw_data_self_evolution_loop_plan_20260726.md` §7.2「覆蓋結論句作 gold 情境註記」 | **撤回並改指**（本檔 §3.2 邊 2） | 同上 |
| 同上 §3.2 attestation 引用（07-24／豁免 18） | **修訂**：最新為 id=9 @2026-07-25 18:14、`passed=false`、`missing_in_db=7,839` | 基線本身是失敗態，須誠實標註 |
| 同上 §6「快照表可整輪 DELETE 回滾」 | **改為** `status=halted` ＋失效標記 | 與 P4.E3「只失效不刪除」直接衝突 |
| 同上 §5.1「每輪算 field_correlation 差分」 | **降級**：現行 schema 為 upsert-in-place、無 iteration 維度，差分**機械不可實現**（見 §3.2 邊 1 之處置） | PK=(stock_id,field_a,field_b,method,basis)、無 run 維度 |
| TRI-v1 §4.3 `evolution_cross_notify` 新表與 `TRI-HALT` 效力 | **撤回**（改由 `evolution_kill_switch.scope` 承載，§3.3 C6） | 一張自陳「無效力」的佈告欄同時是唯一全域停機閘，設計自相矛盾；且該表由 M1 才建，最需要急停的期間恰好沒有急停 |
| TRI-v1 §4.4 統一 view | **延後＋修欄**（RAW 分支誤把 `approved_by` 放進 `trigger_code` 槽；引用 RAWEVO 不存在的 `consecutive_no_gain`） | 三 ledger 皆未建，先對齊 DDL 再談 view |
| TRI-v1 §3.5「增補欄為**建議**」 | **改為硬要求**（§3.3 C2） | §4.4 view 與 T-V1/T-V4/T-V9 全部硬引這些欄，「建議」使 TRI 對自己的驗收條件無拘束力 |
| TRI-v1 §3.3 週節拍表 | **撤回**，改為「單槽鎖為主、時刻表為輔」（§9） | 實機三條 LAI cron 全部不取任何共用鎖；Ollama `-np 1` 全域序列化 |
| 三份子計畫共 6 處 `report_dual_evolution_week.py`、四處「可選 `DUAL-IFACE-yes`」 | **一律以腳本斷言取代人工數字**（§3.3 C8） | 同一條「最機械」的驗收條件，原文寫 3 處、兩面獨立審查各數出 6 與 7 —— 手數的驗收本身就是假綠來源 |

### 0.7 hugo 之前拍的板，哪些需要重拍

| 拍板碼 | 原狀態 | 建議 | 理由 |
|---|---|---|---|
| `LAIEVO-P-yes`（＝`ROUTEB-P-yes`） | 已拍（APPROVED-NO-EXEC） | **需重新確認** | 該檔 mtime 15:53，早於新尺實測（16:12 建表、16:21–16:22 控制臂）；其增益／停損／驗收整套建立在已作廢的尺上 |
| `TWEVO-P-yes` | 已拍 | **不重開，但須知悉兩項更正** | (a) 現況錨 run_id 錯；(b) `volume_gini_60d` 之證據與假說方向相反卻通過 G-PROM（§3.4 M-1） |
| `RAWEVO-P-yes` | 已拍 | **不重開，但出口須改指**（§3.2 邊 2） | 其 LAI 出口指向死渠道 |
| `TRI-P-yes`／`TRI-IFACE-yes` | 已拍 | **以 `V2-P-yes` 承接**；TRI-v1 降為前身，未被本檔修訂之條文續行 | TRI-v1 §1 現況錨完整繼承壞尺前提；§3.3／§4.3 已被實機事實推翻 |
| `TRI-M0-go`／`TRI-M1-go` | 未開 | **維持未開**；本檔以 Phase 2–5 取代其內容 | M1 的五張表在跨軸邊有實料之前建起來，只會得到三本空帳（且 append-only 只能失效不能刪） |
| `TRI-CADENCE-yes` | 未拍 | **維持未拍**，且須先過 P5.W5（§8） | 把節奏變成預設自動＝自動化升級 |
| `FZ-keep` | 生效中 | **需補豁免條文**（§3.5 I9） | 已實證未守住：2026-07-26 09:18 對 `TaiwanStockPriceAdj` upsert 2,799＋2,800 列；三軸 V0／L-V0／T-V0 以「零市場 API 放量」為前提，出生即紅 |
| `GATE-keep` | 生效中 | **維持，並補「升嚴程序」`GATE-raise`** | GATE-keep 只禁降、未定升嚴程序；G-PROM 符號一致性屬升嚴，目前無落地路徑 |
| `APPROVED-NO-EXEC` audit 之「本輪零 DDL、零新腳本」 | 已登錄 | **需補一份 S0 登錄**（§8 人閘 H7） | 同日 16:12 已建兩表、新增四檔（含新開 package `src/augur/evolution/`），全部 git untracked、無 audit 登錄 → 治權帳面與事實分叉（P4.E3 留痕） |

---

## §1 現況錨（實查 2026-07-26，含時戳）

### 1.1 三軸現況

| 軸 | 帳本 | 現況錨 | 可信度 |
|---|---|---|---|
| **RAWEVO** | 無（`raw_evolution_iteration_ledger` 不存在） | `dataset_catalog` 97 列（86 有實表）／`column_catalog` 769／`field_correlation` 657,164／`field_return_leadlag` 135,192／`field_lens_map` 342；`attestation_result` 最新 id=9 @07-25 18:14 **passed=false**、missing_in_db=7,839；public 表 **250** 張（TRI-v1 寫 248，已過期） | 素材齊備、可唯讀先行 |
| **TWEVO** | `evolution_run`(1)／`promotion_queue`(59)／`evolution_apply_log`(2)／`evolution_production_feature_set` active=**2** | 本機唯一 run_id=1（07-24 21:46 succeeded）；`principle_factor_map` 58 列／39 distinct feature／35 principle；`philosophy_principle` 35 列（33 untested／2 validated）；`direction_gate` **無 evaluated_pass**；`arena` 4,128 列 **settled_at 全 NULL**、pred_date 僅 07-15/16 | 閘鏈可跑，**gain 來源尚無貨** |
| **LAIEVO** | `local_model_version`(5)／`local_model_gold_sample`(1103)／`local_model_eval_item`(120)／`local_model_eval_run`(12) | serving=`pp_3ab2efebb04e`（promoted_by=hugo，**晉升依據已作廢**）；`anchor_hash`/`eval_code_hash`/`gate_id` 五版全 NULL；新尺 `set_id=4183475c5089`＋`eval_code_hash=f3075238eb55` 已建、四臂已測；**S1 grammar 臂 18:28 起實跑中** | 尺已重建，**能力數字尚未產生** |

### 1.2 單機硬體（三軸互斥之物理前提）

一台 WSL2、Ryzen 5 3600（12 執行緒）、23GB RAM（本輪實查 available **3GB**、zram 已用 2.6GB、load 5.72）、**GTX 1650 4GB sm_75**（已用 3350MiB，`nomic-embed-text` 常駐＋qwen3:4b 部分卸載）、**單一 Ollama 實例且 `-np 1`（全域序列化）**、同一 PostgreSQL（shared_buffers 6GB／work_mem 256MB）。

> 任何假設「有空閒 GPU（LoRA）／空閒 Ollama slot（多臂並行）／空閒 PG 記憶體」之計畫，在現況下皆為超賣。

### 1.3 已 live 的排程（五份計畫全文零提及 —— 這是節奏設計與地面脫節的根）

| 時間 | 作業 | 實測 | 是否取共用鎖 |
|---|---|---|---|
| `30 1 * * *` | `run_evolution_chain.sh`（收割×3→self_seek→收割×2→evolve_cycle→self_seek） | 01:30:01→02:31:51＝**62 分** | 只有 `flock` 防自身重入 |
| `15 */2` | `evolve_cycle.py --cycle` | 打 LLM 槽 | 否 |
| `45 */6` | `evolve_self_seek.py --seek` | PG／網路 | 否 |
| `15 6` cron **＋** `augur-l2-deliberation.timer` | `run_daily_deliberation.py --run` | **同一支跑兩次**（今日 cron 記積壓 81／新增 15；journal 記 82／新增 16） | 否 |
| `0 8 * * 1` VACUUM ANALYZE ／ `10 8 * * 1` verify_weekly | 相隔 10 分 | 否 |
| 週日 `02:00` knowhow-refresh | 與 01:30 鏈重疊 | 否 |
| `0 20 27 7 *` | `arena_settle_oneshot.sh`（自拆） | 尚未觸發 | — |

### 1.4 帳本閘現況（標準不一致）

- **有**誠實閘：`local_model_gold_sample`／`local_model_version`／`local_model_eval_item`／`local_model_eval_run`／`trial_ledger`／`revalidation_baseline`／`raw_supersede_log`／`governance_proposal`／四張 gate 表／arena 三表（共 25 個非內部 trigger）。
- **無**任何 trigger：`evolution_run`／`evolution_coverage_snapshot`／`promotion_queue`／`evolution_apply_log`／`evolution_production_feature_set`／`principle_factor_map`／`philosophy_principle`。

> 標準是顛倒的：**唯一由引擎自動寫入、`decided_by` 全為 `'evolution_engine'`、無人簽的 PME 帳本，沒有閘**。

---

## §2 本計畫的成敗定義（program-level 落日條款）

> 這是 v2 相對 v1 最重要的新增。既有全部停損（`RAWEVO-STOP-N=2`／`TWEVO-N=3`／`LAIEVO-STOP-N=2`）停的是**輪**，換一個 `trigger_code` 即可重開；週儀表量的全是吞吐（iteration 數、hint 數、覆蓋率、gain 旗標）。沒有 program-level 落日，一年後最可能的畫面是：三本帳本各 50+ 輪、hugo 簽了兩百次人閘，而 `prodset` 仍 n=2（其一還與假說反向）、arena 仍未結算、headline 未動 —— 每一輪都「照計畫執行」，整體卻從未被問過是否值得繼續。

### 2.1 `V2-SUNSET`（須 hugo 親自填寫指標與期限，AI 不得代選）

於 `evolution_prereg_gate`（§4.2.8）凍結**一列**，內容形如：

> 至 `<期限>`，若下列全部未達成，則三軸計畫**整體停止**、三本帳本封存為史料，不得以更換 `trigger_code` 重開；重啟須新開一份計畫並重新拍板。
> (a) arena 至少結算一批且方向門有可讀數；或
> (b) `evolution_production_feature_set` active 由 2 成長，且每一新成員通過符號一致性檢查；或
> (c) LAIEVO 有任一臂在 **F@L1** 上同時勝過 floor 與 mismatched，且該結論可被獨立重跑複現。

建議期限：**2026-10-31**（三個月，涵蓋 arena 首批結算後兩個月的觀察窗）。指標與期限一經 hugo 簽入即 `criteria_sha` 凍結，**升嚴須走 `GATE-raise`、放寬一律不許**。

### 2.2 週儀表第一行

`scripts/report_triple_evolution_week.py` 的**第一行**固定印 `V2-SUNSET` 之三項條件現況與剩餘天數；iteration／hint／coverage 計數一律排在其後，且標為「吞吐指標，非成功指標」。

---

## §3 交互優化（主體）

### 3.1 三軸正交矩陣（誰能寫哪張表）

| 目標表 | RAWEVO | TWEVO | LAIEVO |
|---|---|---|---|
| `feature_values`／`feature_candidate_values` | 唯讀 | **寫** | **禁** |
| `evolution_production_feature_set`／`promotion_queue`／`evolution_apply_log` | **禁** | **寫**（PME-AUTO-B） | **禁** |
| `principle_factor_map` | 經人閘→`curate_pme_map_expand` | **寫** | 經人閘→同上 |
| `local_model_version`／`local_model_gold_sample`／`local_model_eval_*` | **禁** | **禁** | **寫** |
| `raw_table_coverage_snapshot` | **寫** | 唯讀 | 唯讀 |
| `evolution_hypothesis_hint` | **寫**（hints_out） | 寫／讀 | 寫／讀 |
| 各自 `*_iteration_ledger` | 各寫各的 | 各寫各的 | 各寫各的 |
| `knowledge_*`／`philosophy_*` | 唯讀 | 唯讀（philosophy 為其自身） | 唯讀 |

> 這張矩陣在 TRI-v1 是文字，本檔以 §3.5 I3 的機械閘落地。

### 3.2 燃料鏈：六條邊，逐條給機械落點

#### 邊 1：RAW → TW（缺口帳／交互假說 → 市場假說）

- **現況**：TRI-v1 寫入口為 TWEVO `hints_in`；RAWEVO 原文寫 `consumed_briefs`（那是 LAIEVO 的欄名）；而 TWEVO ledger 兩欄皆無，`principle_factor_map` 只有 6 欄、無任何 provenance 欄。**兩份文件指向兩個都不存在的欄。**
- **機械落點（本檔）**：
  1. RAWEVO R3 產出 → 寫 `evolution_hypothesis_hint`（`from_axis='raw'`，`dedup_key` UNIQUE）。
  2. hugo 以 `RAWEVO-HINT-approve <ids>` 將 `decision` 改為 `approved`（**單向前進**，trigger 擋回改）。
  3. `scripts/curate_pme_map_expand.py` 改為**只吃** `decision='approved'` 之列（且該腳本由硬編 `MAP_E012_SEED` list 改為讀 DB，守 #29b）。
  4. 寫入 `principle_factor_map` 時同批填新欄 `hint_id`／`provenance`／`created_at`。
  5. TWEVO ledger `hints_in` 存 `hint_id` 陣列（**無 FK**，見 §3.3 C1 故障隔離）。
- **觸發**：人閘（H3）。**禁自動連鎖**。
- **驗收**：`A6`（§7）—— `hints_in` 之每個 `hint_id` 在 `evolution_hypothesis_hint` 中皆 `decision='approved'` ∧ `decided_by` 非空 ∧ `decision_code` 非空。
- **RAWEVO R3 差分之處置**：`field_correlation` 為 upsert-in-place、無 run 維度，「第 N 輪新發現什麼」機械不可實現。**本檔不新增 history 表**（65.7 萬列×每輪之體積不划算）；改為：R3 每輪只把**本輪被提為 hint 的那幾條**（通常 <50 條）連同其 `corr`／`n_obs`／`computed_at` 快照進 `evolution_hypothesis_hint.provenance`。差分因此定義為「hint 層級的差分」而非「全表差分」，並在 RAWEVO 計畫中明文修正 §5.1 的承諾。

#### 邊 2：RAW → LAI（唯一**已經真的接上**的邊）

- **現況**：`scripts/build_eval_set.py` 已直接讀 `column_catalog`(4 處)／`field_correlation`(1)／`knowledge_item`(4) 產生 L1–L4 凍結題 —— RAWEVO 的資產**已是** LAIEVO 新尺的地基。而三份計畫描述的落點是「gold 情境註記」，那條渠道已死（verdict 常數、舊尺失效、gold 每日成長會挪動任何以它為選集的固定集）。
- **機械落點（本檔）**：出口改指 `local_model_eval_item` 之**產題流程**，並加三條硬約束：
  1. **禁寫入既有 `set_id`**（`4183475c5089` 已凍結）；新題只能開新 `set_id`。
  2. 跨 `eval_code_hash` 或跨 `set_id` 之比較一律 **fail-loud 拒比**（已實作，維持）。
  3. eval item 須記錄來源表當時的 `attestation_result` 狀態（最新 id=9 為 `passed=false`，不得被讀成「已對帳的乾淨基線」）。
- **禁**：RAW 的任何產出寫進 `local_model_gold_sample`（§3.5 I5）。
- **已知限制（必須寫在契約裡）**：RAW 的機械缺口證據天生適合產 L3_ABSENT、catalog 同名多實體適合產 L4_AMBIG，**而那兩層目前無內容鑑別力**（§0.4）。故在 A 軸補上內容敏感子判準（`V2-RUBRIC-go`）之前，這條邊的貢獻**不可量測**，任何「RAW 讓模型更誠實」的宣稱一律不得成立。

#### 邊 3：TW → LAI（`prediction_brief`）

- **現況**：`scripts/export_evolution_advisor_brief.py` **不存在**；且 TWEVO 唯一可出口的結算證據（arena）settled=0。**這條邊既無管線也無貨。**
- **處置**：**排在 Phase 6 之後**，前置條件為「arena 首批結算完成且有 settled 列」。
- **落點（屆時）**：`brief/1` JSON 檔 → LAIEVO ledger `briefs_in`（存 path＋hash，**禁 panel 陣列、禁數值陣列**）→ 僅允許作 **pack 情境註記**。
- **明禁**：brief 進 `local_model_eval_item`（加題即改 `set_id`，炸掉整個凍結集的可比性）或 `local_model_gold_sample`。

#### 邊 4：LAI → TW（行為軸假說）

- 與邊 1 共用 `evolution_hypothesis_hint`（`from_axis='lai'`），人閘同 H3。
- **語料裁決**：LAI 側可產出的 hint 限於「行為與流程」類（例：某類問題在無檢索時模型系統性斷言），**不得**把文獻 metadata 當作市場假說來源。

#### 邊 5／6：TW → RAW、LAI → RAW（唯讀回饋）

- 落點：RAWEVO ledger `briefs_in`（僅存 path＋hash）。用途限於「下一輪 R0/R1 優先掃哪些表」。
- **禁**：RAW 因此改寫任何 raw 表（RAWEVO 全程唯讀，這是它零風險的來源）。

#### 跨軸通知

- **撤回** `evolution_cross_notify` 新表。改為：
  - 佈告：各軸 ledger 之 `cross_notify_json`（純記錄，零效力）。
  - 停機：`evolution_kill_switch` 加 `scope`（§3.3 C6）。

### 3.3 共用零件（收斂清單）

#### C1 `evolution_hypothesis_hint`（唯一新增的「跨軸表」）

- **為何是表而非 JSONB**：`dedup_key` 跨軸唯一（TRI-v1 宣稱的唯一 Goodhart 防線）與「只有 approved 可進 curate」這兩條規則，**只有 UNIQUE ＋ CHECK 能機械保證**；若照三份子計畫存在各自 ledger 的 JSONB 陣列裡，兩條規則都只能靠自律。
- **故障隔離（必要）**：三軸 ledger 對此表**不設 FK**（只存 `hint_id` 陣列，允許懸空、由驗收 `A6` 查出）；`decision` **單向前進不 UPDATE 回頭**；各軸讀取路徑在「表不可用／查無」時**降級為零 hints 繼續結輪**，不得拋錯。理由：RAW 的結輪寫入 TW 開輪要讀的列，若加 FK／鎖，一條壞 CHECK 就能讓與之無關的軸結不了輪 —— 那正是 TRI-v1 §2.3.6「禁跨軸自動連鎖」要防的東西。

#### C2 三本 ledger：**不合表**，改「同一份 DDL 常數模組 ＋ 三張同構表 ＋ 一條 pytest 斷言」

- **裁決理由**：合表的五項宣稱效益（uid 唯一、guard、停損查詢、週報、validator 各做一次）在三表＋常數模組下**全部成立**；合表額外付出的代價是各軸專屬欄退化成無 CHECK 的 `payload JSONB`（丟掉設計中唯一的機械部分），且一個 trigger/CHECK 落在三個 driver 的共同路徑上 —— 為 RAW 收緊一條 CHECK 就會擋掉 TW 的結輪。三表皆未建，兩案成本相同，沒有理由選劣化版。
- **硬要求（把 TRI-v1 §3.5 的「建議」升為契約必要欄）**：`iteration_uid`／`briefs_in`／`briefs_out`／`hints_in`／`hints_out`／`consecutive_no_gain`／`steps_json JSONB '[]'`／`opened_at`/`closed_at`／`gain`／`gain_basis`／`gate_ref` 為 `V2-P-yes` 之契約必要欄，**非建議**；任一軸拒絕即等同拒絕本檔介面章全案，須另案書面留痕，不得部分採納。
- **機械驗收**：pytest 斷言「三張 `CREATE TABLE` 由 `src/augur/audit/evolution_ledger_ddl.py` 之同一常數清單生成」。

#### C3 `heavy_slot`：單槽鎖（**兩階段**）

- **第一版（今天可做，零 code）**：所有打 Ollama 的入口在**呼叫端**包 `flock -n /tmp/augur_llm.lock`：crontab 的 `15 */2 evolve_cycle`、`30 1 run_evolution_chain.sh`、`15 6` 審議，以及所有手動 `eval_local_model.py`。取不到即 graceful skip 並寫一行 log。
- **第二版（Phase 5，`V2-SLOT-go`）**：`src/augur/core/heavy_slot.py`，`pg_try_advisory_lock(hashtext('augur_evolution_heavy_slot'))`。
  - **關鍵陷阱（必寫進實作）**：**不得**使用 `augur.core.db.connect`（`src/augur/core/db.py:32-38` 在 `finally` 關連線，session 級 advisory lock 隨連線釋放 → 鎖在第一個 `with connect()` 區塊結束時就沒了，且**靜默**放行）。模組須自持長生 `psycopg2` 連線，每個 heavy step 邊界**重驗**鎖仍在自己手上，掉鎖即 fail-loud 不續跑。
  - `--selftest` 必含一條：巢狀 `with connect()` 進出後鎖仍在。
  - 搶不到鎖時**不 silent skip**：寫一列 `evolution_deferred_work` 並由週報印出積壓筆數。理由：在這台機器上搶不到鎖是常態，silent skip 會變成穩態 —— 82 件無人理的 escalation 就是同一種結局的既有證據。

#### C4 證據協定（跨軸方法移植的載體）

- `src/augur/audit/evidence_protocol.py`（純函式、零 DB、含 `--selftest`）：
  - `ARMS = ('ceiling','floor','shuffled','mismatched','live')`
  - `same_scale(suite_id, code_hash)` → 跨尺 fail-loud
  - `evidence_level(metric_by_arm) -> {'none','incomparable','weak','scoped_established'}`，鐵則「live 臂須**同時**勝過 floor 與 mismatched 才有證據力」**寫成程式而非註解**。
- **落表**：TW／RAW 用**新表** `evolution_evidence_run`；**LAI 繼續用 `local_model_eval_run`**（不對一天大的 append-only 表做長格式改造，只加兩欄，見 §4.3）。兩者共用同一份純函式判讀 —— 這是本檔對兩面鏡的裁決：拿到方法移植的全部價值，不付 schema churn 的代價。

#### C5 誠實閘：**只做 DELETE/TRUNCATE 拒，不做 UPDATE-GUC**

- **裁決理由**：`honesty_ledger_guard()` 的 UPDATE 分支條件是 `current_setting('augur.honesty_write',true) <> 'on'`，而 PME 唯一的自動寫入者 `apply_evolution_promotions.py` 依提案須自行 `SET LOCAL` → **閘只擋人手修正、不擋引擎**，對真正的威脅豁免。更糟：`prodset` 走 `ON CONFLICT (feature) DO UPDATE`，guard 僅在衝突分支觸發 → 同一特徵**首次 APPLY 過（INSERT）、再次 APPLY 死（UPDATE）**，任何單次測試都驗不出來。落地後還會被寫成「P4.E3 已對 PME 機械落地」（#15）。
- **做法**：PME 六表＋三軸新表一律掛「只擋 DELETE/TRUNCATE」的 guard；要管 UPDATE 就走**追加修訂列＋`superseded_by`**，不走 GUC。RAWEVO §6 的「整輪 DELETE 回滾」改為 `status='halted'` ＋失效標記。

#### C6 停機：擴 `evolution_kill_switch.scope`，撤回 `TRI-HALT` 專用表

- `scope ∈ ('tw','lai','raw','global')`；`TRI-HALT` ＝ 寫入 `scope='global'` 的 halt 列，沿用既有 `scripts/set_evolution_kill_switch.py`（加 `--scope`）。
- 三軸 driver 開輪前一律查 `scope IN (自軸,'global')`。
- 好處：與既有 `G-KILL` 讀取路徑**同一套語意**，不分叉；且**今天就有效**，不必等 M1 建表。

#### C7 契約 validator

- `src/augur/audit/evolution_contract.py`（dataclass＋validator＋uid regex＋status 映射純函式）＋ `scripts/validate_evolution_contract.py`。
- 三契約：`brief/1`（`claim_level ∈ {ledger_fact, paper, gap_debt}`、`claims ≤ 20`、禁數值陣列）、`hint/1`、`xnotify/1`；首欄帶 schema 版本、**未知欄位 fail-closed**、產生端消費端共用同一 validator。
- **措辭黑名單擴充**：既有「可交易／確立級／已解凍」外，**新增 LAI 側假兆詞**「更準／更聰明／答得更好」—— 因 P/A 只證行為類別（shuffled 在 A@L3/L4 拿 0.967）。
- **落地端硬要求**：LAIEVO `L-V6` 之判準改為「每筆 brief 檔經 `validate_evolution_contract.py --file <path> --kind brief` rc=0」，不得只驗「無 panel 陣列」。

#### C8 計畫一致性斷言（取代人工數字）

- `scripts/check_plan_consistency.py`（rg 全量掃 `reports/`，缺漏 exit≠0，零 usage，納入 `check_cmd_matrix` 射程）。斷言項：別名標註全覆蓋、`DUAL-IFACE-yes` 死碼零殘留、`--defer-heavy` 同名（LAIEVO 現寫 `--defer`）、契約必要欄在三份 DDL 段皆出現、SSOT 指針行皆指向本檔。
- **理由**：同一條「最機械」的 M0 驗收，原文寫「三處」、兩面獨立審查各數出 6 與 7 —— 手數的驗收條件本身就是假綠來源。

### 3.4 跨軸方法移植（三條，附機械落點）

#### M-1 對照臂 ＋ 符號一致性 → TWEVO（**價值最高的一條**）

- **現況真空**：`grep permutation|shuffle|placebo|null_model` 於 `src/augur/philosophy/evolution.py` 與 `scripts/run_philosophy_evolution.py` **零命中** —— TWEVO 的 local-gates 從未有任何對照臂跑過。
- **同型病已在生產**：`volume_gini_60d` 假說 `direction=+1`，實測 `mean_ic=-0.0539`／`hac_t=-3.966`／`hit_rate=0.25`（即**在假說方向上穩定答錯**），仍通過 G-PROM、APPLY 進 prodset、其 principle 被翻成 `validated`，且它是 **active n=2 的其中一支**。成因：`run_philosophy_evolution.py:241` 已先把 preds 乘上 direction，然後只判 `|hac_t| ≥ 2` —— `evolution.py` **全檔零處讀 `direction`**。這正是新尺 `mismatched` 臂（量級對、類別選錯）要抓的失效模式。
- **多重比較**：54 個假說評過、3 個過 `|t|≥2`；純雜訊下期望假陽性 ≈ 54×0.05 = **2.7** → 目前雙綠與「全是雜訊」在統計上不可區分。
- **落點**：
  1. `scripts/run_philosophy_evolution.py --control-arms`：標籤置換臂＋隨機特徵臂，走**完全相同**的 local-gates 路徑，≥200 draws，結果寫 `evolution_evidence_run`（arm='shuffled'／'mismatched'，metric_name='hac_t_abs_ge2_rate'）。
  2. **事前預註冊決策規則**（`GATE-raise` 拍板時一併簽）：經驗偽陽率 > 10% ⇒ 將 `min_abs_hac_t` 調至經驗 95 分位。
  3. **符號一致性**：`sign(mean_ic)` 須與 `principle_factor_map.direction` 一致，不一致 → verdict `FAIL_SIGN`（**非 SKIP**），並禁止 I8 把該列回填為 `validated`；`gate_json` 多記 `expected_direction`／`observed_sign`。
  4. **既有 `volume_gini_60d` 之處置**（demote／標註／保留但註記）＝獨立人裁議題（H5）。
- **注意**：以上兩項皆為**升嚴**，`GATE-keep` 只禁降未定升嚴程序 → 須先立 `GATE-raise` 程序（§8 H4）。

#### M-2 試驗計數／deflation 精神 → LAIEVO（**資料不混帳**）

- `evolve_cycle.py:208` 已自陳「套 deflation 精神：搜尋會膨脹、須外部確認」，但只做了集A搜／集B確認的分割，`n_variants` 僅埋在 JSON。
- **落點**：`local_model_eval_run` 加 `n_trials INTEGER`／`selection_scope TEXT`；`--compare` 常駐輸出加一句「本 set 已比較 N 個候選，最佳臂之領先須大於選擇偏差」。
- **明禁**：LAI 的選材試驗**不得**寫進 `trial_ledger`（那是市場宣稱的多重試驗帳，混入會污染 `deflated_floor` 的 `n_trials` 輸入）。若判定 LAI/RAW 搜尋不入 N，`revalidate_baseline` 輸出須加一句誠實限制「N 未含 LAI/RAW 搜尋」。

#### M-3 5-oracle 確定性裁決 → gold verdict 與產題謂詞（**單一住所**）

- 同一件事在系統裡有三份互不相識的實作：`verifiers.py` 的 5 個真 oracle（`information_schema`／`import_isolation`／`file_grep`／`db_query`／`pytest`，且 `confirmed` 唯一寫點是 `verify_claim`）；`evolve_cycle.py:290` 把 `'oracle_pass'` 當字串常數無條件寫入 gold；`build_eval_set.py` 又自己寫 `NOT EXISTS`／catalog 查核。
- **落點**：
  1. `build_eval_set.py` 的 `_l3`／`_l4` 謂詞抽成單一住所（`src/augur/audit/db_oracle.py` 或直接 import `verifiers`），供產題與漂移哨兵共用（#12）。
  2. gold 的 verdict 改由確定性 oracle 產生（至少讓 `rejected` 會出現）—— **但 gold 表為 append-only、既有 1103 列只能新增更正列不可 UPDATE**，故此項須先定更正機制，排在 Phase 6（低優先）。
- **隔離注意**：新依賴 `augur.evolution → augur.deliberation` 須**同批**寫進 `import_isolation` 的允許清單並附理由，不得默默相依。

### 3.5 **不該連的地方**（隔離不變式，逐條理由）

| 代號 | 不變式 | 理由 | 機械落點 |
|---|---|---|---|
| **I1** | 判準本體不共用 | F/P/A 是文本行為 0/1 判準、G-PROM/G-ECON 是重疊窗統計；合併＝類型錯誤 | 三軸 `gain_basis` CHECK 各表不同 |
| **I2** | 寫入目標表單向 | 只有 TW 能寫 `feature_values`／`prodset`／`promotion_queue` | §3.1 矩陣＋`import_isolation` 反向掃描 |
| **I3** | import 方向與角色授權 | 新開 package `src/augur/evolution/` 目前是三重盲區：`PIPELINE` 七值不含 evolution、`FORBIDDEN` 三值不含 `augur.evolution`、十組 `*_LITERALS` 無任何 `local_model_` 字面 → `check_isolation()` 回 0 違規是「沒在看」而非「乾淨」 | §5.2 之 `import_isolation` 三處擴充＋4 條 pytest |
| **I4** | 三種人簽不合併 | `TWEVO-APPLY-go` ≠ serving `promoted_by` ≠ `RAWEVO-HINT-approve`；合併會反過來降低人類監督（觸 P5.W5） | 三處各自 `gate_ref` |
| **I5** | 語料與面板不互灌 | RAW brief 不得成為 gold／題庫；LAI 評測集不得吃 panel | contract validator 之 `claim_level` 白名單＋`build_eval_set` set_id 保護斷言 |
| **I6** | `trial_ledger` 不混帳 | 見 M-2 | 表層不變，條文明禁 |
| **I7** | 佈告欄零效力 | 除停機外，任何 driver 不得依 `cross_notify_json` 分支，否則「禁跨軸自動連鎖」形同虛設 | 驗收 `A7` |
| **I8** | `principle_domain_map` 為**應用注記軸非量化資格** | 憲章 v1.47.0 明定；他域原理欲入量化須另走 investment school 全鏈 | `import_isolation` 字面守衛：**禁任何 SQL join `principle_domain_map` → `principle_factor_map`** |
| **I9** | `FZ-keep` 之豁免須明列，不得靠默契 | 07-26 09:18 已有 `TaiwanStockPriceAdj` 2,799+2,800 列 upsert；不寫下來，三軸第一條驗收出生即紅、然後被忽略 | 見下 |

**I8 之前置事實（誠實記載）**：`principle_domain_map` 實查 **0 列**、除 DDL migration 外零 code 消費端；且 35 條 principle **100% 掛在 investment 學派下**（management 學派 21 個、principle 零條）—— **沒有他域原理可映射**。故第一步是人撰 principle（決策層），不是寫 code。另 RAW 側已有功能重疊的跨域註記層 `field_lens_map`（342 列），兩者關係須由 hugo 裁定分層或二擇一，不並存兩套而不定義。

**I9 之處置（`V2-FZ-scope`，條文層，不加表級 trigger）**：
- 允許路徑：arena 結算 SOP 之前置 sync、`daily_maintenance --heal` 之對帳補洞。
- 禁止路徑：探索性 backfill、寬窗放量、新 dataset 首抓。
- 三軸 V0／L-V0／T-V0 之措辭由「零市場 API 放量」改為「**無豁免清單外之放量**」。
- **硬排序：任何 ingest 機械閘不得早於 2026-07-27 20:00 arena 結算完成**。理由：`arena_settle_oneshot.sh` 在資料未到時走 `exit 0`、cron **不自拆**、log 只寫「明晚重試」→ 閘一旦落地即為**永久靜默重試**，而 arena 是 TWEVO 在整份計畫集裡唯一可測的產出。同批修正該 SOP 為 fail-loud（資料未到時 rc≠0 並寫通知）。
- 機械閘若日後要做，維度是**驅動者與量級**（預註冊 driver 白名單＋單輪列數上限），**不是表名**。

---

## §4 表 schema（v1.39.0 (a) 硬要求）

### 4.1 所讀既有表（唯讀清單 → 結果落哪張表）

| 既有表 | 關鍵欄（讀） | 讀者 | 結果落點 |
|---|---|---|---|
| `dataset_catalog`(97) | `dataset, attestation_mode, exempt_*` | RAWEVO R0/R1 | `raw_table_coverage_snapshot` |
| `column_catalog`(769) | `dataset, column_name, anti_leakage_flag, dirty_value_note` | RAWEVO R0；`build_eval_set` L4 | 同上；`local_model_eval_item` |
| `attestation_result`(9)／`full_attest_progress`(32) | `run_at, passed, missing_in_db, driver` | RAWEVO R1 | `raw_table_coverage_snapshot.last_attest_ref`（**須同時記 `passed` 狀態**） |
| `field_correlation`(657,164)／`field_return_leadlag`(135,192)／`field_lens_map`(342) | `stock_id, field_a, field_b, corr, n_obs, computed_at` | RAWEVO R3 | `evolution_hypothesis_hint.provenance` |
| `knowledge_item`(270,117) | `title, domain, item_text` | `build_eval_set` L1/L3 | `local_model_eval_item` |
| `principle_factor_map`(58)／`philosophy_principle`(35) | `map_id, feature, direction, validated_ic, status` | TWEVO I0/I5/I8 | `promotion_queue`／`evolution_apply_log` |
| `feature_values`／`feature_candidate_values`(85,360／5 特徵) | as-of 面板 | TWEVO I1–I3 | `evolution_run`／`promotion_queue` |
| `evolution_production_feature_set`(active=2)／`promotion_queue`(59)／`evolution_apply_log`(2)／`evolution_kill_switch` | 全欄 | TWEVO I5/I6 | 同名表 |
| `direction_arena_*`(4,128／11／2／0) | `pred_date, settled_at` | TWEVO I7 | `evolution_evidence_run`（arm='live'） |
| `trial_ledger`(32)／`revalidation_*`(560) | `feats_hash, metric_*, n_trials` | TWEVO I7c | 不變 |
| `local_model_version`(5)／`local_model_gold_sample`(1103) | `status, promoted_by, verdict` | LAIEVO | `local_ai_iteration_ledger` |
| `local_model_eval_item`(120)／`local_model_eval_run`(12) | 全欄 | LAIEVO 全軸 | 同名表 |
| `deliberation_claim`(604)／`deliberation_escalation`(176) | `status, anchor, assigned_verifier` | 驗收（Phase 6 條件性） | `deliberation_verdict` |
| `governance_proposal`(3) | `proposal_id, status, decided_by` | 三軸 `gate_ref` | 同名表 |

### 4.2 新表 DDL（完整）

> 全部由 `src/augur/audit/evolution_ledger_ddl.py` 之常數產生，落地腳本 `scripts/migrate_evolution_v2_ddl.py`（冪等、`--check`／`--dry-run`／`--apply`／`--selftest`）。

#### 4.2.1 三本 ledger 之**共同骨架**（逐字同構，`{axis}` ∈ raw｜tw｜lai）

```sql
CREATE TABLE IF NOT EXISTS {axis}_evolution_iteration_ledger (   -- 實名見 4.2.2
    iteration_id        BIGSERIAL PRIMARY KEY,
    iteration_uid       TEXT NOT NULL UNIQUE
                        CHECK (iteration_uid ~ '^(tw|lai|raw)-[0-9]{8}-r[0-9]{2}$'),
    axis                TEXT NOT NULL CHECK (axis IN ('tw','lai','raw')),
    opened_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at           TIMESTAMPTZ,
    status              TEXT NOT NULL DEFAULT 'planned'
                        CHECK (status IN ('planned','running','succeeded','failed',
                                          'halted','stopped_no_gain')),
    trigger_code        VARCHAR(64) NOT NULL,           -- 開輪拍板碼（不是人名）
    steps_json          JSONB NOT NULL DEFAULT '[]'::jsonb,
        -- 元素最小集：{step, script, argv, rc, started, finished, artifacts, notes}
    gain                BOOLEAN,                        -- NULL = incomparable（不計停損）
    gain_basis          VARCHAR(32),                    -- 各軸 CHECK 不同，見 4.2.2
    gain_evidence       JSONB NOT NULL DEFAULT '{}'::jsonb,
        -- {suite_id, code_hash, arm_metrics:{...}, evidence_run_ids:[...]}
    consecutive_no_gain INTEGER NOT NULL DEFAULT 0,
    stop_reason         TEXT,
    briefs_in           JSONB NOT NULL DEFAULT '[]'::jsonb,   -- [{path, sha256, source_iteration_uid, kind}]
    briefs_out          JSONB NOT NULL DEFAULT '[]'::jsonb,
    hints_in            JSONB NOT NULL DEFAULT '[]'::jsonb,   -- hint_id 陣列（無 FK）
    hints_out           JSONB NOT NULL DEFAULT '[]'::jsonb,
    cross_notify_json   JSONB NOT NULL DEFAULT '[]'::jsonb,   -- 佈告，零效力
    gate_ref            TEXT,                           -- governance_proposal.proposal_id
    closed_by           TEXT,
    notes               TEXT,
    superseded_by       TEXT
);
CREATE INDEX IF NOT EXISTS ix_{axis}_iter_status ON {axis}_..._ledger (status, opened_at DESC);
-- 誠實閘（只擋刪除，見 C5）
CREATE TRIGGER {axis}_iter_no_delete_row  BEFORE DELETE ON ...
    FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard_delete_only();
CREATE TRIGGER {axis}_iter_no_truncate    BEFORE TRUNCATE ON ...
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard_delete_only();
```

#### 4.2.2 各軸專屬欄（三表**實名**與差異）

| 表名 | 專屬欄 | `gain_basis` CHECK |
|---|---|---|
| `raw_evolution_iteration_ledger` | `tier TEXT CHECK (tier IN ('P1','P2','P3'))`、`gap_summary_json JSONB NOT NULL DEFAULT '{}'`、`coverage_snapshot_ref BIGINT` | `IN ('new_gap','hint_approved','none','incomparable')` |
| `evolution_iteration_ledger`（TW） | `apply_allowed BOOLEAN NOT NULL DEFAULT false`、`dual_green_names TEXT[]`、`near_miss_json JSONB`、`source_run_id BIGINT`、`evidence_hash TEXT`（內容定址：`code_sha`+`config_json` hash+map 版本 hash+`as_of`） | `IN ('dual_green_delta','prodset_delta','arena_prereg','none','incomparable')` |
| `local_ai_iteration_ledger` | `eval_set_id TEXT`、`eval_code_hash TEXT`、`n_trials INTEGER`、`selection_scope TEXT` | `IN ('eval_delta','none','incomparable')` |

> `evidence_hash` 是對「run_id=5/6 在本機不存在」這個 blocker 的結構性修正：**閘證據 SSOT 由整數 serial 改為內容定址**。

#### 4.2.3 `evolution_hypothesis_hint`

```sql
CREATE TABLE IF NOT EXISTS evolution_hypothesis_hint (
    hint_id             TEXT PRIMARY KEY,             -- '<axis>-h-<8hex>'
    from_axis           TEXT NOT NULL CHECK (from_axis IN ('tw','lai','raw')),
    from_iteration_uid  TEXT NOT NULL,                -- 無 FK（故障隔離）
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    hint_text           TEXT NOT NULL,
    suggested_map       JSONB NOT NULL DEFAULT '{}'::jsonb,  -- {principle_hint, feature_hint, direction}
    provenance          JSONB NOT NULL,                      -- {kind, refs:[], n_obs}
    dedup_key           TEXT NOT NULL UNIQUE,
    duplicate_of        TEXT,
    decision            TEXT NOT NULL DEFAULT 'pending'
                        CHECK (decision IN ('pending','approved','data_debt_only','rejected')),
    decided_by          TEXT,
    decided_at          TIMESTAMPTZ,
    decision_code       TEXT,                          -- 'RAWEVO-HINT-approve <ids>' 等
    gate_ref            TEXT,
    CHECK (decision = 'pending'
           OR (decided_by IS NOT NULL AND decided_at IS NOT NULL AND decision_code IS NOT NULL))
);
-- 單向前進：非 pending 者不可再改 decision（P4.E3 只失效不刪除）
CREATE TRIGGER hint_decision_forward_only BEFORE UPDATE ON evolution_hypothesis_hint
    FOR EACH ROW EXECUTE FUNCTION hint_decision_forward_only();
CREATE TRIGGER hint_no_delete BEFORE DELETE OR TRUNCATE ON evolution_hypothesis_hint ...;
```

#### 4.2.4 `evolution_evidence_run`（TW／RAW 之證據協定落點）

```sql
CREATE TABLE IF NOT EXISTS evolution_evidence_run (
    evidence_id     BIGSERIAL PRIMARY KEY,
    axis            TEXT NOT NULL CHECK (axis IN ('tw','raw')),
    suite_id        TEXT NOT NULL,     -- 凍結測試集/組態之內容雜湊
    code_hash       TEXT NOT NULL,     -- 判準程式版本
    arm             TEXT NOT NULL CHECK (arm IN ('ceiling','floor','shuffled','mismatched','live')),
    metric_name     TEXT NOT NULL,
    metric_value    DOUBLE PRECISION,
    n_items         INTEGER NOT NULL,
    n_valid         INTEGER NOT NULL,
    n_excluded      INTEGER NOT NULL DEFAULT 0,
    is_invalid      BOOLEAN NOT NULL DEFAULT false,
    n_trials        INTEGER,
    selection_scope TEXT,
    detail          JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (axis, suite_id, code_hash, arm, metric_name)
);
CREATE TRIGGER evidence_no_delete BEFORE DELETE OR TRUNCATE ON evolution_evidence_run ...;
```

#### 4.2.5 `raw_table_coverage_snapshot`

```sql
CREATE TABLE IF NOT EXISTS raw_table_coverage_snapshot (
    snapshot_id       BIGSERIAL PRIMARY KEY,
    iteration_uid     TEXT NOT NULL,                 -- 無 FK
    dataset           TEXT NOT NULL,
    est_rows          BIGINT,                        -- pg_class.reltuples（估計，實測誤差約 -1.9%）
    exact_rows        BIGINT,                        -- 僅 P1 表計算
    min_date          DATE, max_date DATE,
    date_semantics    TEXT CHECK (date_semantics IN
                        ('observation','event_future_ok','calendar','snapshot','no_date')),
    staleness_days    INTEGER,
    freq_class        TEXT,
    gap_years_json    JSONB NOT NULL DEFAULT '{}'::jsonb,
    catalog_registered BOOLEAN NOT NULL,
    last_attest_ref   BIGINT,
    last_attest_passed BOOLEAN,                      -- 必填：基線本身可能是失敗態
    gap_class         TEXT,                          -- 四分類
    detail            JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (iteration_uid, dataset)
);
```

#### 4.2.6 `evolution_deferred_work`（heavy slot 積壓，取代 silent skip）

```sql
CREATE TABLE IF NOT EXISTS evolution_deferred_work (
    defer_id      BIGSERIAL PRIMARY KEY,
    axis          TEXT NOT NULL,
    step_key      TEXT NOT NULL,
    requested_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason        TEXT NOT NULL,        -- 'heavy_slot_busy' | 'kill_switch' | ...
    cleared_at    TIMESTAMPTZ,
    cleared_by    TEXT,
    detail        JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

#### 4.2.7 `local_model_eval_set_check`（題庫漂移哨兵；Phase 2 可先只印不落表）

```sql
CREATE TABLE IF NOT EXISTS local_model_eval_set_check (
    check_id    BIGSERIAL PRIMARY KEY,
    set_id      TEXT NOT NULL,
    checked_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    n_items     INTEGER NOT NULL,
    n_drifted   INTEGER NOT NULL,
    detail      JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

#### 4.2.8 `evolution_prereg_gate`（三軸判準與 `V2-SUNSET` 之凍結落點）

沿用 `arena_admission_gate` 之欄位形狀，加 `axis`：

```sql
CREATE TABLE IF NOT EXISTS evolution_prereg_gate (
    gate_id         TEXT PRIMARY KEY,
    axis            TEXT NOT NULL CHECK (axis IN ('tw','lai','raw','program')),
    purpose         TEXT NOT NULL,
    criteria        JSONB NOT NULL,
    criteria_sha    TEXT NOT NULL,
    status          TEXT NOT NULL CHECK (status IN
                      ('preregistered','approved','evaluated_pass','evaluated_fail','superseded')),
    preregistered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    approved_by     TEXT, approved_at TIMESTAMPTZ,
    git_sha         TEXT,
    evaluated_at    TIMESTAMPTZ, result_snapshot JSONB, evaluation_ref TEXT,
    note            TEXT
);
CREATE TRIGGER prereg_gate_no_goalpost BEFORE UPDATE OR DELETE ON evolution_prereg_gate ...;
```

> **注意（對抗意見已採納）**：LAI 之判讀鐵則**暫不入此表凍結**——尺才一天大、S1 未出，而 `no_goalpost` 擋的是任何終態改動**包含升嚴**，凍早了會從「不能放鬆」變成「不能修」。先以計畫書＋audit 留痕，待新尺經 ≥1 次完整分叉後再凍結（Phase 6）。首批只凍 `V2-SUNSET`（program 軸）。

### 4.3 既有表之增補（ALTER，冪等）

| 表 | 動作 | 理由 |
|---|---|---|
| `local_model_eval_run` | `ADD COLUMN n_trials INTEGER`、`selection_scope TEXT`、`n_excluded INTEGER DEFAULT 0` | M-2；謂詞重算後之排除計數 |
| `principle_factor_map` | `ADD COLUMN hint_id TEXT`、`provenance JSONB`、`created_at TIMESTAMPTZ DEFAULT now()` | 邊 1 之 provenance；目前該表 6 欄無任何來源可溯 |
| `evolution_kill_switch` | `ADD COLUMN scope TEXT NOT NULL DEFAULT 'global' CHECK (scope IN ('tw','lai','raw','global'))` ＋唯一索引 | C6 |
| PME 六表 | 掛「只擋 DELETE/TRUNCATE」guard | C5 |

**不做**：`local_model_eval_run` 的長格式改造（對一天大的 append-only 表動刀，收益低）；改為 `evolution_evidence_run` 只服務 TW/RAW。
**不做**：加 `UNIQUE(set_id, eval_code_hash, arm)`。實查 `run_id` 已是 `(set_id, code_hash, arm, model, n_items)` 之決定性雜湊配 `ON CONFLICT DO NOTHING` → 不會產生重複列；**真正的病是靜默丟棄**（第二支跑完、你以為有結果、其實沒寫）。修法是 `DO NOTHING` 時 **fail-loud**：印出「該 run 已存在、本次結果未入帳」並 rc≠0。

### 4.4 統一 view（延後至 Phase 6；三表逐字同構後為 trivial）

```sql
CREATE OR REPLACE VIEW v_evolution_iteration_unified AS
SELECT axis, iteration_uid, opened_at, closed_at, status, trigger_code,
       gain, gain_basis, consecutive_no_gain, gate_ref, closed_by
FROM raw_evolution_iteration_ledger
UNION ALL SELECT ... FROM evolution_iteration_ledger
UNION ALL SELECT ... FROM local_ai_iteration_ledger;
```
（TRI-v1 版之 RAW 分支把 `approved_by` 放進 `trigger_code` 槽、且讀 RAWEVO 不存在的 `consecutive_no_gain` —— 兩處錯誤已在 §4.2 一併消除：RAWEVO 之 `approved_by` **改名為 `trigger_code`**，「誰核可」一律只由 `evolution_hypothesis_hint.decided_by` 與 `gate_ref` 承載。理由：live DB 全部 14 個 `*_by` 欄語意皆為「人」。）

---

## §5 python 程式規畫（v1.39.0 (b) 硬要求）

> 全部遵 #18／#29：白話 docstring（標頭首行帶 #18 標記）＋「守原則 #X #Y」一行＋**執行指令矩陣**＋`--selftest`（零 DB 零 API）；`scripts/` 一律 `import _bootstrap`、無參數 graceful。新增者於**首次提交當下**即須含矩陣，否則不得宣稱已個別驗證。

### 5.1 既有程式之角色（唯讀引用；不重寫）

| 檔 | 角色 | 本檔要求之改動 |
|---|---|---|
| `src/augur/philosophy/evolution.py` | PME 狀態機、`DEFAULT_GATE_CONFIG` SSOT | 加符號一致性判準；`--selftest` 由 2 條擴為**全部 8 個閘值**；`config_sha256` 與人簽 baseline 比對，不符拒開 run |
| `scripts/run_philosophy_evolution.py` | I3 local-gates 主引擎（25–35 分） | 加 `--control-arms`（置換臂／隨機特徵臂 ≥200 draws）；multi-seed 之取樣改名或改為真獨立變異來源（現為固定 `rng=42` 對同 20 panels 取 80%，重疊 ≥64%，非獨立） |
| `scripts/apply_evolution_promotions.py` | I5（PME-AUTO-B） | 不改語意；因 C5 只擋 DELETE，其 `ON CONFLICT DO UPDATE` 路徑不受影響 |
| `scripts/curate_pme_map_expand.py` | 邊 1／邊 4 唯一入口 | `MAP_E012_SEED` 硬編 list 改為讀 DB（#29b）；只吃 `decision='approved'` |
| `scripts/eval_local_model.py` | LAI 評測 harness | per-layer 常駐輸出；`DO NOTHING` fail-loud；謂詞重算與 `n_valid/n_excluded`；`--arm base` 標記為現行組態下無效 |
| `scripts/build_eval_set.py` | 邊 2 產題器 | 抽 `_l3`/`_l4` 謂詞為可重用函式；記 `attestation` 狀態；`set_id` 保護斷言 |
| `src/augur/audit/import_isolation.py` | 隔離 AST／字面雙閘 | 三處擴充（I3） |
| `scripts/setup_predict_role.py` | predict 角色授權 | 加第三桶 `unregistered` → `--apply` **拒跑**（見 §6.2） |
| `scripts/set_evolution_kill_switch.py` | 停機 CLI | 加 `--scope` |
| `scripts/migrate_honesty_guards_ddl.py` | 誠實閘 DDL | 擴至 PME 六表（只擋刪除） |
| `scripts/check_cmd_matrix.py` | #29(d) 稽核（實跑 0.46s／350 支／缺 0） | 納入 `check_plan_consistency.py` |
| `src/augur/deliberation/verifiers.py` | 5 oracle、`confirmed` 唯一寫點 | 不改；僅被 M-3 引用 |

### 5.2 新增模組／腳本（逐檔：職責・簽名・輸入表・輸出表・角色）

| 檔 | 角色 | 主要簽名 | 輸入表 | 輸出表 |
|---|---|---|---|---|
| `src/augur/audit/evolution_ledger_ddl.py` | 三 ledger＋hint＋evidence＋deferred 之 **DDL 常數單一住所**（#12） | `LEDGER_COMMON: tuple[Column,...]`；`ledger_ddl(axis) -> str` | — | — |
| `src/augur/audit/evolution_contract.py` | `brief/1`/`hint/1`/`xnotify/1` dataclass＋validator＋uid regex | `validate(obj, kind) -> list[str]`；`iteration_uid_ok(s) -> bool` | — | — |
| `src/augur/audit/evidence_protocol.py` | 證據等級純函式（C4） | `same_scale(a,b) -> bool`；`evidence_level(metrics: dict[str,dict]) -> str` | — | — |
| `src/augur/core/heavy_slot.py` | 單槽鎖（自持長生連線） | `@contextmanager heavy_slot(name, wait_s=0) -> Lock` | — | `evolution_deferred_work` |
| `src/augur/philosophy/iteration.py` | TWEVO step 圖／停損／gain 比較純函式 | `next_step(steps_json) -> str`；`should_stop(n) -> bool` | — | — |
| `scripts/migrate_evolution_v2_ddl.py` | 全部新表＋ALTER 之冪等 DDL | `--check/--dry-run/--apply/--selftest` | — | §4.2/§4.3 全部 |
| `scripts/run_raw_evolution_iteration.py` | RAWEVO R0–R5 driver（唯讀） | `--open/--step/--close/--tier/--dry-run/--selftest` | `dataset_catalog`,`column_catalog`,`attestation_result`,`field_correlation` | `raw_evolution_iteration_ledger`,`raw_table_coverage_snapshot`,`evolution_hypothesis_hint` |
| `scripts/run_evolution_iteration.py` | TWEVO I0–I9 driver（subprocess 編排既有 script） | `--open/--step/--close/--allow-apply/--dry-run/--selftest` | 同 §4.1 TW 列 | `evolution_iteration_ledger`,`evolution_evidence_run` |
| `scripts/close_local_ai_iteration.py` | LAIEVO 開／結輪（**無** `--promoted-by` 旗標） | `--open/--close/--gate-ref/--selftest` | `local_model_eval_run`,`local_model_version` | `local_ai_iteration_ledger` |
| `scripts/verify_evolution_acceptance.py` | **統一三軸驗收** A0–A12（舊碼 T-V/V/L-V 對照表內建） | `--axis/--check/--selftest` | 全部 | stdout＋rc |
| `scripts/validate_evolution_contract.py` | 三契約 validator CLI | `--file/--kind/--scan-ledgers/--selftest` | 三 ledger JSONB | rc |
| `scripts/report_triple_evolution_week.py` | 三軸並列週儀表（**第一行為 `V2-SUNSET` 現況**） | `--week/--check/--selftest`；缺表 graceful rc=0 | 三 ledger＋evidence＋deferred＋hint | stdout／md |
| `scripts/verify_eval_set_validity.py` | 題庫漂移哨兵（唯讀） | `--set-id/--selftest` | `local_model_eval_item`＋來源表 | （第一版只印；第二版落 `local_model_eval_set_check`） |
| `scripts/check_plan_consistency.py` | 計畫文件機械斷言（C8） | `--selftest` | `reports/*.md` | rc |
| `scripts/report_ocv_snapshot.py` | OCV 機械擷取（**判斷欄留白**） | `--selftest` | crontab／pg_roles／grants／grep | md（供 hugo 填裁決欄） |
| `scripts/export_evolution_advisor_brief.py` | 邊 3（**Phase 6 之後**） | `--iteration-uid/--out/--selftest` | TW ledger＋apply_log | brief JSON 檔 |

**不建之檔（§10）**：`export_evolution_sft.py`／`train_qlora_small.py`／`train_lora_cpu.py`／`publish_lora_ollama.py`／`eval_local_model_deploy.py`（已由 `eval_local_model.py` 取代，名稱歧異就此消除）／`migrate_lora_training_ddl.py`／`migrate_evolution_cross_notify_ddl.py`／`report_dual_evolution_week.py`（作廢，別名由 C8 斷言確保全 repo 零殘留）。

---

## §6 分階段（每階段附：前置拍板碼・動作・中止條件・驗收・回滾）

### Phase 0（`V2-S0-go`）今日止血：零 GPU、零 DDL、可即刻回滾

| # | 動作 | 中止條件 | 驗收（機械） |
|---|---|---|---|
| 0.1 | 停掉殘餘 `--arm base`（`think:false` 無效導致結構性無效；本輪已耗 2.2h／零列） | 若 grammar 臂已在跑則讓其跑完 | `ps` 無 `--arm base`；log 有停手註記 |
| 0.2 | LLM 入口一律 `flock -n /tmp/augur_llm.lock`（C3 第一版） | 任一 cron 因鎖而連續 3 日全 skip → 回滾並改排時刻 | crontab 每條 LLM 條目皆含 flock |
| 0.3 | 刪 06:15 重複排程（cron 與 systemd timer 二擇一，建議留 timer） | — | 同日只有一份 `run_daily_deliberation` 輸出 |
| 0.4 | `evolve_cycle` 由 `15 */2` 降為 `15 */6`；且其舊 `_score` 路徑改 fail-closed（不再寫分數與 candidate） | 若 hugo 判定仍需連續模式，改為僅停 `_eval_pack` 寫入 | `local_model_version` 不再新增 candidate |
| 0.5 | `eval_local_model.py --compare` 常駐印 layer×axis 對照矩陣，並在 A@L3/L4 旁常駐印「shuffled=0.967 ⇒ 本格無內容鑑別力」 | — | 輸出含該行 |
| 0.6 | 週日 knowhow-refresh 02:00 → 04:30；週一 verify_weekly 08:10 → 08:40 | — | timer/crontab 已改 |
| 0.7 | 修 `arena_settle_oneshot.sh`：資料未到時 rc≠0＋通知（現為 `exit 0` 靜默無限重試） | — | dry-run 觸發時 rc≠0 |

**回滾**：全部為 crontab／timer／輸出層，逐項可還原；無資料變更。
**須明示**：0.1–0.4、0.6 屬常駐排程／背景作業變更（#6）。

### Phase 1（`V2-EXP1`，**進行中**）最小可驗證實驗：35 分鐘

- **動作**：`--arm grammar`（18:28 起實跑中，≈12 分）→ `--arm behavior`（≈12 分）→ 跑 per-layer 拆解，與已存四臂並列。
- **事前預註冊判讀規則（先寫下，不得事後改）**：
  - **判準 A（LAI 軸是否存在）**：behavior 之 **F@L1 > 0.167**（shuffled 實測值）且 > 0（floor）→ 才算 LAIEVO 首次有非空、可複現的能力數字。
  - **判準 B（RAW→LAI 這條唯一活邊是否成立）**：看 A@L3／A@L4 —— **已知 shuffled 在該格＝0.967**，故無論 behavior 拿多少都**證不了事**；結論必須寫成「三軸交互目前**不可量測**」，不得寫成「成立」或「不成立」。
- **分叉**：
  - F@L1 過 → 進 Phase 2，並把 `V2-RUBRIC-go`（A 軸內容敏感子判準）排為下一個人裁項；**不開任何 ledger／DDL**。
  - F@L1 不過 → LAIEVO 退回 S0，三軸總控延後；RAWEVO 仍可獨立唯讀先行（Phase 3）。
- **中止條件**：grammar 臂亦出現 100% `done_reason='length'` → 停手，改查 harness 而非改判準。
- **驗收**：`local_model_eval_run` 新增 ≥1 列 `is_invalid=false` 且 `n_valid ≥ 100`。

### Phase 2（`V2-ISO-go` ＋ `V2-HONESTY-go`）焊死：隔離、閘、漂移可見

| # | 動作 | 中止條件 | 驗收 |
|---|---|---|---|
| 2.1 | `import_isolation` 三處擴充＋4 條 pytest（I3） | 若擴充後既有測試紅且非真違規 → 先修清單再上 | `check_isolation()` rc=0 且**負向測試**（故意 import）會紅 |
| 2.2 | `setup_predict_role` 加 `unregistered` 桶 → `--apply` 拒跑；同批把 `local_model_*`／`raw_evolution_*` 加入 FORBIDDEN_EXPLICIT | 若換機流程因此卡住 → 補登該表而非改回 fail-open | `--apply` 對未登錄表 rc≠0；`augur_predict` 對四張 `local_model_*` 零授權 |
| 2.3 | PME 六表掛「只擋刪除」guard（C5） | 若 `apply_evolution_promotions` 因此紅 → 立即回滾（**不應該紅，這是本設計的重點**） | 負向測試：DELETE 被擋；一次完整 `--dry-run` APPLY 路徑仍綠 |
| 2.4 | `evolution_kill_switch` 加 `scope`；`set_evolution_kill_switch.py --scope` | — | 寫入 `scope='global'` halt 後，三軸 driver（含 dry-run）皆拒開新輪 |
| 2.5 | `verify_eval_set_validity.py`（唯讀、第一版只印），掛在 01:30 鏈收割段之後 | `n_drifted` 連續 3 日 >20 且無人處置 → 升為 fail-loud 阻斷 evolve_cycle | 該腳本 rc=0 且輸出 `n_drifted` |
| 2.6 | `check_plan_consistency.py` ＋ 修正三子計畫之 SSOT 指針、死碼、`--defer`→`--defer-heavy` | — | rc=0 |

**為何 2.1 現在做成本為零**：`behavior_rubric.py` 目前只 import `json/re/sys`，`src/augur/evolution/` 確實乾淨 —— **趁還是真乾淨時焊死**；等三軸開跑再補就是事後追捕。

### Phase 3（`RAWEVO-S0-go` → `RAWEVO-S2-go`）RAW 唯讀先行

- **為何先跑 RAW**：全程唯讀、零 API、零 GPU、素材齊備，是三軸中唯一今天就能零風險推進的一軸。
- **誠實修正 TRI-v1 的開工序理由**：TRI-v1 稱「RAWEVO 先行＝其產出是 TWEVO I0 的燃料」，但 hints 出自 RAWEVO **S2/S3** —— 首批序列若照 v1，TWEVO 頭幾輪必然零 RAW hints。本檔改寫為：**RAWEVO 先行＝零風險先跑；首輪 TWEVO 零 RAW hints 屬預期**。
- **中止條件**：任一步觸 API 呼叫（import 級檢查）→ 立即 halt＋報告；`est_rows` 與 `exact_rows` 對 P1 表偏差 >5% → 停手改用 exact。
- **驗收**：`raw_table_coverage_snapshot` 有 ≥86 列（有實表者）；`feature_values`／`prodset`／`promotion_queue` 零寫入（機械斷言）；每則 hint 含出處＋`n_obs`；`last_attest_passed` 欄非空。

### Phase 4（`V2-CTRL-go` ＋ `GATE-raise`）TWEVO 對照臂與符號一致性

- **動作**：M-1 之四項（置換臂／隨機特徵臂／事前決策規則／符號一致性）。
- **中止條件**：置換臂 ≥200 draws 之壁鐘超過 2 小時 → 降 draws 並標註統計力；經驗偽陽率無法收斂（跨兩次執行差 >5pp）→ 停手，先查取樣是否真獨立。
- **驗收**：`evolution_evidence_run` 有 `axis='tw'` 之 shuffled／mismatched 列；`gate_json` 出現 `expected_direction`／`observed_sign`；重跑既有 58 列閘評，`volume_gini_60d` 判 `FAIL_SIGN`。
- **人裁項**：`GATE-raise` 程序本身、閾值調整、`volume_gini_60d` 之回溯處置。

### Phase 5（`V2-HINT-go` ＋ `V2-LEDGER-go` ＋ `V2-SLOT-go`）介面契約落地

- **前置硬條件（採納對抗意見）**：**至少一條跨軸邊有實料** —— arena 首批結算完成（有 settled 列）**或** RAWEVO S2 已產出 ≥1 則 approved hint。未達成則本階段不開。
  - 理由：五張表在跨軸邊有實料之前建起來，只會得到三本空帳；而 append-only 之下**只能失效不能刪**，欄名歧異將永久固化。
- **動作**：`migrate_evolution_v2_ddl.py --apply`（三 ledger＋hint＋evidence＋deferred＋prereg gate）；`curate_pme_map_expand` 改資料驅動；`heavy_slot.py` 第二版。
- **中止條件**：三軸子計畫任一拒絕契約必要欄且未提出書面理由 → 停手（不得部分採納）。
- **驗收**：pytest「三表由同一常數清單生成」；`validate_evolution_contract.py --scan-ledgers` rc=0；`heavy_slot --selftest` 之巢狀連線斷言綠。

### Phase 6（`RAWEVO-S3/S4`／`TWEVO-S2`／`LAIEVO-B1`）三軸開輪

- **動作**：各軸開第一輪；週儀表上線；停損計數開始。
- **拍板紀律**：`TWEVO-S2-go`（含 I3 25–35 分重活）與 `LAIEVO-B1-go`（含 embed）**拍板可同批、執行須經 heavy slot 鎖錯開**（修正 TRI-v1 §7.2 對同一「單機重活互斥」判準的兩種結論）。
- **中止條件**：`V2-SUNSET` 之期限到達且三條件皆未達成 → 整體停止；或任一軸連續 N 輪無增益且 `gain` 皆為 NULL（不可比）→ 先查量尺再談停損（**不可比不計入停損**）。
- **驗收**：§7 全表。

---

## §7 驗收總表（統一編號 A0–A12；含舊碼對照）

| 新碼 | 判準（機械） | 舊碼對照 |
|---|---|---|
| **A0** | 三軸全程無**豁免清單外**之 FinMind/FRED 放量（掃 `data_audit_log` 之 driver 白名單） | T-V0／V0／L-V0 |
| **A1** | `iteration_uid` 格式合法且跨三表唯一；跨軸引用一律用 uid，`rg` 無裸 PK 引用 | T-V1 |
| **A2** | `DEFAULT_GATE_CONFIG` 八個閘值與人簽 baseline `config_sha256` 相符；SKIP≠PASS；ECON-only 禁晉升 | GATE-keep／V1 |
| **A3** | 三 ledger 之 `steps_json` 每步有 `rc`＋`started`＋`finished`；`closed_at`／`closed_by` 非空才算結輪 | V2／L-V2 |
| **A4** | `gain=true` ⇒ `gain_evidence` 指向存在的 `evolution_evidence_run` 或 `local_model_eval_run` 列，且該列**同時勝過 floor 與 mismatched**；`gain=NULL` 不計停損亦不晉升 | V3／L-V3 |
| **A5** | APPLY 紀律：`apply_allowed=true` ⇒ `gate_ref` 非空且指向 `governance_proposal` 之 enacted 列 | V4 |
| **A6** | 人閘完整：`hints_in` 每個 `hint_id` 在 hint 表皆 `decision='approved'` ∧ `decided_by`／`decision_code` 非空；`local_model_version` 無「serving 而 `promoted_by` 為空」之列 | T-V4／L-V1 |
| **A7** | 通知不連鎖：`rg` 三軸 driver 無任何依 `cross_notify_json` 之分支（停機除外，且停機讀的是 `evolution_kill_switch`） | T-V3 |
| **A8** | 重活互斥：同一時間窗內 `steps_json` 標 heavy 之 step 重疊 ≤1；搶不到鎖者於 `evolution_deferred_work` 有對應列 | T-V5／L-V9 |
| **A9** | 三軸隔離：`check_isolation()` rc=0 且**負向測試會紅**；`augur_predict` 對 `local_model_*`／`raw_evolution_*` 零授權；RAW/LAI 對 `feature_values`／`prodset`／`promotion_queue` 零寫入 | T-V6／L-V5 |
| **A10** | 措辭掃描：所有 brief／hint／週報零命中黑名單（可交易／確立級／已解凍／更準／更聰明）；`brief.claim_level` 僅三值 | T-V8／L-V6 |
| **A11** | 停損各自：達 N ⇒ `status='stopped_no_gain'` ∧ `stop_reason` 非空 ∧ 不改 serving／prodset | T-V9／L-V8 |
| **A12** | 儀表唯讀：`report_triple_evolution_week.py` 對 DB 零寫入；第一行為 `V2-SUNSET` 現況 | T-V7 |

> **凡驗收涉及「分數提升」，一律要求附 ceiling／floor／mismatched 對照臂**（A4）—— 這是今日教訓的制度化。

**驗收落點**：`scripts/verify_evolution_acceptance.py --check`（SQL＋rg，零 usage，納入 `check_cmd_matrix`）。
**不接審議引擎（本輪）**：前置二條 —— (1) 現存 82 件未解 escalation（2026-07-12 起零解決）結清；(2) 取 10 條驗收做端到端試點，**≥80% 須由 5 oracle 真正裁出 confirmed/refuted**（非 escalated）。未達成則驗收就是腳本，並在計畫中誠實標明「本條為腳本驗收，非引擎裁決」。理由：把 30 條倒進一個 14 天零解決的佇列，是把機械驗收轉成人工積壓 —— 那是 D 分量下降包裝成上升。

---

## §8 人閘清單（哪幾點須 hugo 親簽，為何機器不能代）

| # | 閘點 | 為何機器不能代 | 落點 |
|---|---|---|---|
| **H1** | `V2-P-yes`（採納本檔）／`V2-SUNSET`（成敗指標與期限） | 定義「什麼算成功」是價值判斷，不是執行 | `evolution_prereg_gate`(axis='program') |
| **H2** | LAIEVO serving 晉升（`promoted_by`） | P5.W2；且現役 `pp_3ab2efebb04e` 之晉升依據已作廢，重評／retire 之處置須人裁 | `local_model_version` |
| **H3** | `RAWEVO-HINT-approve <ids>`（hint 升級） | 決定哪條假說進入量化鏈＝判準層 | `evolution_hypothesis_hint.decision` |
| **H4** | `GATE-raise`（升嚴程序本身）＋ G-PROM 符號一致性與多重比較閾值 | GATE-keep 只禁降未定升嚴；改閘＝治權層 | `evolution_prereg_gate`(axis='tw') |
| **H5** | `volume_gini_60d` 之回溯處置（demote／標註／保留但註記） | 涉及已 APPLY 之生產狀態與 P4.E3 | `evolution_apply_log` 追加註記列 |
| **H6** | `V2-RUBRIC-go`（A 軸內容敏感子判準） | 判準變更，且會換 `eval_code_hash`、使既有 12 列 run 退出可比範圍 | `behavior_rubric.py` |
| **H7** | 補一份 S0 audit 登錄（今日 DDL＋四新檔＋新 package） | P4.E3 留痕；TRI audit 之「本輪零 DDL、零新腳本」須修正射程 | `audits/` |
| **H8** | `TRI-CADENCE-yes` 或任何 cron 新增／自動化升級 | **P5.W5**：須 Steward 書面裁決「未實質降低人類監督」 | `audits/`＋OCV 快照 |
| **H9** | `V2-FZ-scope`（FZ-keep 豁免清單） | 凍結範圍屬治權判準 | `.cursor/rules/finmind-fred-api-freeze.mdc`＋計畫條文 |
| **H10** | `principle_domain_map` 與 `field_lens_map` 之分層裁定；他域 principle 之人工撰寫 | 憲章 v1.47.0 明定 AI 生成詮釋 DB CHECK 硬擋 | `principle_domain_map` |

### 8.1 關於「機器能不能區分 AI 與 hugo」—— 誠實條文（必須逐字寫進計畫）

> 本機為單帳號單機環境：`pg_roles` 僅 `augur`/`augur_app`/`augur_owner`/`augur_predict`/`postgres`/`stock`，**無任何代表自然人 hugo 的角色**；AI 與 hugo 皆以 `DB_USER=augur` 連線，`getpass.getuser()` 兩者同為 `hugo`。因此 **`promoted_by`／`decided_by`／`approved_by` 之類欄位在機器上無法區分 AI 與人**。本機制為**榮譽制 ＋ 事後偵測**，任何文件不得將其描述為機械保證。

**採取的做法（偵測而非預防）**：
1. 每一列人閘須帶 `gate_ref` 指向一列 `governance_proposal`；
2. 週報固定一段「本週所有宣稱人簽之列（表、列、時戳、`trigger_code`、由哪支程式路徑寫入）」供 hugo 掃視認領；
3. 三軸 CLI **一律不設** `--promoted-by`／`--approved-by` 之類可由執行者填人名的旗標。

**砍掉的做法**：建立 `augur_human` DB 角色。理由：(a) 其穩態必然是密碼進 `.pgpass`／`.env`（hugo 不會為每次簽名手打密碼），屆時 AI 可無聲取得，防護回到原點但**檔面已宣稱機械化** —— 比今天更危險，因為今天大家知道它是榮譽制；(b) role 屬 cluster 層、不在 `pg_dump`，會在 #31 換機時成為新的人工前置；(c) trigger 驗的是憑證不是人。

---

## §9 排程與節奏（單槽鎖為主、時刻表為輔）

| 時間 | 作業 | 變更 |
|---|---|---|
| 01:30–02:35 | `run_evolution_chain.sh`（實測 62 分） | 加 flock；鏈尾加 `verify_eval_set_validity` |
| 02:35–03:30 | — | RAWEVO 週輪候補窗（唯讀，可與 embed 並存） |
| 03:30 | embed-catchup | 維持 |
| **04:30** | knowhow-refresh（週日） | 由 02:00 移入（原與鏈重疊） |
| **04:45–05:45** | **LAI 評測窗**（新增） | 唯一塞得下一次 grammar+behavior 雙臂的時段 |
| 06:15 | 審議（**去重後單跑**） | 刪除重複排程 |
| 07:30 | daily_green | 維持 |
| `15 */6` | `evolve_cycle`（**由 */2 降頻**） | 每 2 小時打一次 LLM 槽必然撞掉任何評測臂；且其 held-out n=6 分數實測在 0.0–0.571 間亂跳、無證據力，降頻零損失 |
| `45 */6` | `evolve_self_seek` | 維持（純 PG／網路） |
| 週一 08:00／**08:40** | VACUUM ANALYZE／verify_weekly | verify 由 08:10 後移（避免與 VACUUM 及常駐 embed 搶 4GB VRAM） |
| 07-27 20:00 | arena 一次性結算 | 維持，且修為 fail-loud |

> **原則**：錯開的真正約束不是「三軸」，而是**一個 Ollama 槽 ＋ 3GB 可用記憶體 ＋ 4GB VRAM（已用 3.35GB）**。任何以 driver 為單位的節奏表在這台機器上都是空談，因為每隔幾小時就有 cron 進同一個槽。先降頻＋上鎖，時刻表才有意義。

---

## §10 明確不做（砍掉的條目、理由、復活條件）

| 條目 | 為何砍 | 復活條件 |
|---|---|---|
| **Tier 2 LoRA 全鏈**（6 支腳本＋`lora_training_run`） | 4B QLoRA no-go（sm_75 無 bf16、4GB，超量在 WSL2 不 OOM 只慢 3.7×）；語料 87% 為文獻 metadata，背進權重＝訓練幻覺且違 #9/#10；唯一站得住的窄塊只剩「該拒答／消歧義」行為，其餘 82% 是格式、grammar 零訓練即得 | Phase 1 之 behavior 臂 **F@L1 > 0.167** 且與 grammar 臂有可複現差距；**且** A 軸補上內容敏感判準後仍留明確缺口；**且** GPU 可用 VRAM > 3.5GB 或改 CPU LoRA、RAM available > 8GB |
| **`evolution_cross_notify` 表與 `TRI-HALT` 專用效力** | 一張自陳無效力的佈告欄同時是唯一停機閘＝設計自相矛盾；且與既有 `evolution_kill_switch` 分叉成兩套停機語意 | 不復活（已由 `kill_switch.scope` 取代） |
| **三本 ledger 合併為單表** | 合表的五項效益在「三表＋常數模組」下全部成立；合表額外代價是各軸專屬欄退化為無 CHECK 的 JSONB，並製造跨軸單點故障 | 不復活 |
| **`augur_human` DB 角色** | 見 §8.1 | 出現真正的第二個人類使用者或第二台機器 |
| **PME 誠實閘之 UPDATE-GUC 分支** | 對唯一自動寫入者豁免；且 `ON CONFLICT DO UPDATE` 會使同一特徵首次過、再次死（單次測試驗不出） | 不復活（改追加修訂列） |
| **把 30 條驗收接進審議引擎** | 82 件 escalation 自 07-12 零解決；倚重的 `file_grep`(n=11)／`pytest`(n=4) 是最少被行使的 oracle | §7 之兩條前置達成 |
| **FZ-keep 表級寫入 trigger** | 會殺掉 07-27 arena 結算，而該 SOP 資料未到時 `exit 0`、cron 不自拆 → 永久靜默重試 | arena 首批結算完成後，且改以 driver 白名單＋列數上限為維度 |
| **predict role 改 fail-closed 白名單** | 把「無聲放寬」換成「無聲收緊」，爆點落在換機當下（hugo 上下文最少時） | 不復活（改 fail-loud on unknown，效果相同、失敗形態安全） |
| **凍結 LAI 判讀鐵則進 no_goalpost gate** | 尺才一天大、S1 未出；`no_goalpost` 擋任何終態改動**包含升嚴** | 新尺經 ≥1 次完整分叉後 |
| **`local_model_eval_run` 長格式改造 ＋ 加 UNIQUE** | 對一天大的 append-only 表動刀；且重複列問題不存在（`run_id` 已是決定性雜湊），真正的病是 `DO NOTHING` 靜默 | 不復活（改 fail-loud＋兩欄） |
| **`field_correlation` 全表 history 快照** | 65.7 萬列×每輪的體積不划算 | 不復活（改 hint 層級差分） |
| **RAW 缺口寫進 gold** | gold verdict 1103/1103 常數、舊尺失效、每日成長 —— 死渠道 | 永不 |
| **合併 arena／direction／unfreeze 三張 gate 表** | 動 live 閘、收益低 | 無限期不做 |
| **擴 5-oracle 閉集** | 封閉集變更屬治權 | 累積 ≥3 個真實無法以現有 oracle 表達的 anchor |
| **`report_dual_evolution_week.py`** | 已由 `report_triple_evolution_week.py` 取代 | 不復活（由 C8 斷言確保零殘留） |

---

## §11 誠實天花板

### 11.1 這份計畫**能**達成什麼

- 讓「有沒有變好」這個問題在三軸上**都有一把可被否證的尺**（LAI 已有；TW 經 Phase 4 補對照臂與符號一致性後有；RAW 經 Phase 3 有覆蓋帳但**尺仍最弱**）。
- 讓三軸的**燃料鏈有機械落點**：hint 走一張有 UNIQUE 與人閘 CHECK 的表，而不是三份 JSONB 裡的約定。
- 讓**隔離從文字變成閘**：`augur.evolution` 進入 AST 與字面雙掃描、predict 角色對未登錄表拒跑。
- 讓**帳本不可刪**（P4.E3 在 PME 側第一次有機械落點）。
- 讓**整個計畫可以失敗**（`V2-SUNSET`）—— 這是 v1 最缺的一件。

### 11.2 這份計畫**不能**達成什麼（誠實限制）

1. **不能證明模型「答得更準」**：P 與 A 只測行為類別（shuffled 在 A@L3/L4 拿 0.967）；唯 F 軸對內容敏感，而 F 僅在 L1 有鑑別力。任何跨軸 brief 引用 A 軸進步一律受措辭閘擋。
2. **不能量測 RAW→LAI 這條唯一活邊的貢獻**（在 `V2-RUBRIC-go` 落地之前）。這是本檔最誠實也最不好看的一句。
3. **不能在機器上區分 AI 與 hugo 的簽名**（§8.1）。
4. **不能保證 `prodset` 會成長**：實證顯示擴大 map 覆蓋（17→35）之後雙綠仍 2、active 仍 2；瓶頸是**訊號強度**而非覆蓋數量。本檔不重走已被本機證偽的路。
5. **不能解凍、不開 API、不降閘**：`FZ-keep`／`GATE-keep` 全程維持；缺口帳、假說燃料、預測需求**均不得**作為解凍論據（`INV2` 須 Steward 明示）。
6. **不能替代 arena**：TWEVO 的 `gain_basis='arena_prereg'` 在 07-27 結算之前一律不成立，前幾輪 `gain` 只能是 `incomparable`（**不計停損**，否則 `TWEVO-N=3` 會誤觸發）。

### 11.3 賭注與收場

| 賭注 | 賭錯的樣子 | 怎麼收 |
|---|---|---|
| **B1**：零訓練（grammar＋行為守則）就能拿到大部分行為能力 | Phase 1 之 behavior 臂 F@L1 ≤ 0.167 | LAIEVO 退回 S0；不進 LoRA；誠實記「本地小模型在此任務上零訓練無增益」 |
| **B2**：TWEVO 的 3/54 雙綠不全是雜訊 | 置換臂顯示經驗偽陽率 > 10% 且 95 分位 >> 2.0 | 走 `GATE-raise` 升閾；prodset 可能歸零 —— **這是誠實的結果，不是失敗** |
| **B3**：RAW 的機械缺口能產出對市場有意義的假說 | 連續 N 輪 hints 全被 H3 拒或 `data_debt_only` | `RAWEVO-STOP-N` 觸發、降頻月輪 |
| **B4**：三軸互惠 | 一年後三本帳本各 50+ 輪而 §2.1 三條件皆未達成 | `V2-SUNSET` 觸發，整體停止、封存為史料 |
| **B5**：LAIEVO 變強會惠及全系統 | 實測其唯一受益面是 `local-llm` MCP 的 `ask` profile（審議引擎用裸 4b、不讀 pack；advisor 用 8b 而 pack 在 4b 上評） | 二選一（Phase 6 人裁）：(A) 把 serving pack 接進審議引擎，讓其 5 oracle 反向驗證；(B) 誠實寫明射程僅及一個 MCP profile。**在 Phase 1 結果出來前兩者皆不動** |

---

## §12 拍板碼總表

### 12.1 逐字沿用（不重新發明）

`RAWEVO-P-yes`／`RAWEVO-S0-go`…`S5-go`／`RAWEVO-HINT-approve <ids>`／`RAWEVO-STOP-N=k`／`RAWEVO-P-no`／`RAWEVO-Sx-hold`
`TWEVO-P-yes`／`TWEVO-S0-go`…`S5-go`／`TWEVO-APPLY-go`／`TWEVO-U-go`／`TWEVO-N=3`
`LAIEVO-P-yes`／`LAIEVO-B0-go`／`B1-go`／`B4-go`／`B2-spike-go`／`B2-train-go`／`B3-go`／`LAIEVO-STOP-N=k`／`LAIEVO-Bx-hold`
`TRI-P-yes`／`TRI-IFACE-yes`／`TRI-M0-go`／`TRI-M1-go`／`TRI-CADENCE-yes`／`TRI-HALT`／`TRI-RESUME`
`FZ-keep`／`GATE-keep`／`APPROVED-NO-EXEC`／`PME-AUTO-B`／`DUAL-IFACE-yes`（已由 `TRI-IFACE-yes` 涵蓋，**死碼、勿再單獨下**）

### 12.2 本檔新增

| 碼 | 意義 | 前置 |
|---|---|---|
| `V2-P-yes` | 採納本檔為三軸總控 SSOT v2（TRI-v1 降為前身） | — |
| `V2-P-no`／`V2-Px-hold` | 否決／暫緩 | — |
| `V2-SUNSET` | 凍結 program-level 成敗指標與期限（hugo 填內容） | `V2-P-yes` |
| `V2-S0-go` | Phase 0 止血批（含改 cron，屬 #6 破壞性） | `V2-P-yes` |
| `V2-EXP1` | Phase 1 實驗（已在跑；判讀規則已預註冊） | — |
| `V2-RUBRIC-go` | A 軸內容敏感子判準（判準變更、換 `eval_code_hash`） | Phase 1 結果 |
| `V2-ISO-go` | 隔離守衛＋predict role fail-loud | `V2-P-yes` |
| `V2-HONESTY-go` | PME 六表 DELETE 拒閘 | `V2-P-yes` |
| `V2-CTRL-go` | TWEVO 對照臂 | `V2-P-yes` |
| `GATE-raise` | **升嚴程序**（GATE-keep 之對偶；含符號一致性、閾值上調、回溯處置） | Steward |
| `V2-HINT-go` | hint 表落地＋curate 資料驅動化 | 跨軸邊有實料 |
| `V2-LEDGER-go` | 三 ledger＋evidence＋deferred 落地 | 同上 |
| `V2-SLOT-go` | heavy_slot advisory lock 第二版 | `V2-LEDGER-go` |
| `V2-FZ-scope` | FZ-keep 豁免清單條文 | Steward |
| `V2-OCV` | OCV 快照產出＋P5.W5 書面裁決 | Steward |

---

## 附錄 A：本輪親驗數字索引（2026-07-26）

| 項目 | 數字 | 來源／時戳 |
|---|---|---|
| `local_model_eval_run` | 12 列（含 `probe` 測試殘留 1 列） | psql 18:33 |
| 四臂（`f3075238eb55`） | ceiling 1/1/1；floor 0/0/0；shuffled .1667/.9/.9667；mismatched 0/.2667/0 | 16:22:53 三列＋16:21:56 |
| per-layer 拆解 | F@L1：1.000／0.167／0.000／0.000；A@L3、A@L4：1.000／**0.967**／0.000／0.000 | detail JSONB 聚合（唯讀） |
| base 臂 | 兩支共約 2.2h、log 段落零輸出、**零入帳** | `~/logs/eval_arms_20260726.log`（649B, 18:28）；ps |
| grammar 臂 | pid 2607965，18:28 起實跑中 | ps 18:33 |
| gold | 1103 列（今日新增 824）、verdict 1103/1103 `oracle_pass` | psql |
| `local_model_version` | 5 列；`anchor_hash`/`eval_code_hash`/`gate_id` 全 NULL | psql |
| `prodset` active | 2（`inst_cumflow_position_120d`、`volume_gini_60d`） | psql |
| `volume_gini_60d` | direction=+1、`validated_ic=-0.0389`、apply_log `hac_t=-3.966`／`mean_ic=-0.0539`／`hit_rate=0.25` | psql |
| `evolution_run` | 僅 run_id=1（序列 last_value=1） | psql |
| arena | 4,128 列、settled_at 全 NULL、pred_date 07-15/16 | psql |
| `attestation_result` | 最新 id=9 @07-25 18:14、`passed=false`、`missing_in_db=7,839` | psql |
| FZ 後寫入 | 07-26 09:18 `TaiwanStockPriceAdj` upsert 2,799＋2,800 列 | `data_audit_log` id 260539/260540 |
| escalation | resolved=t 94（皆 07-10/11）；resolved=f **82**（07-12 起零解決） | psql |
| 硬體 | RAM available 3GB／zram 2.6GB／load 5.72；GPU 4096MiB 已用 3350MiB；llama-server RSS 9.5GB | free/nvidia-smi/ps 18:33 |
| crontab | 見 §1.3（06:15 cron 與 systemd timer 重複；`15 */2` evolve_cycle；`30 1` chain；`0 20 27 7` arena） | `crontab -l` 18:33 |
| 稽核 | `check_cmd_matrix` 0.46s／350 支／缺 0；`check_isolation()` 0.85s／violations 0（**「沒在看」而非乾淨**） | 實跑 |
| 未建之表 | `evolution_iteration_ledger`／`local_ai_iteration_ledger`／`raw_evolution_iteration_ledger`／`raw_table_coverage_snapshot`／`evolution_cross_notify`／`lora_training_run` 全部 `to_regclass=NULL` | psql |

## 附錄 B：與 TRI-v1 之處置對照（保留／修訂／撤回）

| TRI-v1 條 | 處置 | 本檔落點 |
|---|---|---|
| §1 現況錨 | 修訂（248→250 表；LAI 錨全面更新；run_id 更正） | §1 |
| §2.1 正交矩陣 | 保留＋機械化 | §3.1／§3.5 I3 |
| §2.2 燃料鏈 | 修訂（RAW→LAI 改指題庫；RAW→TW 落點統一為 hint 表） | §3.2 |
| §2.3 禁項清單 | 保留＋擴措辭黑名單＋補 P5.W5 句 | §3.3 C7／§8 |
| §2.3.3「不改三 hash 錨」 | 修訂（現行有效錨＝`set_id`＋`eval_code_hash`；`local_model_version` 三欄回填另案） | §0.2／§8 H2 |
| §3.3 週節拍 | 撤回 → 單槽鎖為主 | §3.3 C3／§9 |
| §3.4 TRI-HALT | 撤回 → `kill_switch.scope` | §3.3 C6 |
| §3.5 增補欄「建議」 | 修訂為硬要求 | §3.3 C2 |
| §4.3 cross_notify 表 | 撤回 | §10 |
| §4.4 統一 view | 修訂＋延後 | §4.4 |
| §5.2 腳本總表 | 修訂（新增今日 S0 四檔；砍 LoRA 六支＋dual 週報＋cross_notify migrate；`eval_local_model_deploy.py` 更名統一） | §5.2／§10 |
| §6.1 M0/M1 | 以 Phase 2–5 取代；M1 加「跨軸邊有實料」前置 | §6 |
| §6.1 M2 開工序理由 | 修訂（首輪 TWEVO 零 RAW hints 屬預期） | §6 Phase 3 |
| §7.2 可同批／必須分開 | 修訂（拍板可同批、執行須經鎖錯開；新增 P5.W5 列） | §6 Phase 6／§8 H8 |
| T-V0–T-V9 | 併入 A0–A12（舊碼對照保留） | §7 |

---

**本檔到此為止之全部主張，均可回溯至附錄 A 之實查來源或計畫原文引用；凡未實查者一律標為「計畫中」或「須人裁」。本檔不含任何未經來源支撐的量化數字。**