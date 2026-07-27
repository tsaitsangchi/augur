---
name: augur-self-evolution-plan-map
description: 自我迭代進化計畫 SSOT＝v2 總控(20260726);三軸 RAWEVO×TWEVO×LAIEVO;Phase 0/1 已完、Phase 2 焊死待 V2-P-yes;V2-SUNSET 落日須 hugo 親填;拍板碼與隔離不變式全錄
metadata: 
  node_type: memory
  type: project
  originSessionId: b6cddf62-b16d-44ba-af86-bbdb2cb161c8
  modified: 2026-07-27T06:28:42.092Z
---

**自我迭代進化的 SSOT＝`reports/augur_self_evolution_master_plan_v2_20260726.md`（891 行 13 節，14-agent workflow 產出＋親驗）。TRI-v1（`augur_triple_self_evolution_master_plan_20260726.md`）降為前身；`V2-P-yes` 承接 `TRI-P-yes`。三軸主檔：RAWEVO＝raw_data、TWEVO＝tw_prediction、LAIEVO＝local_ai_route_b（各 loop_plan_20260726.md）。**

**核心結構**：
- **§2 V2-SUNSET（v2 最重要新增）**：program-level 落日條款，**hugo 親填指標與期限、AI 不得代選**；三選一達成才續命：(a) arena 結算一批＋方向門可讀數（結算半已達成 07-26）(b) prodset active 由 2 成長且新成員過符號檢查 (c) LAIEVO 任一臂 F@L1 同時勝 floor 與 mismatched **且可獨立複現**——(c) 首半已達成（behavior F@L1=0.933），複現待跑。建議期限 2026-10-31。既有停損全停「輪」、換 trigger_code 即重開＝v1 致命缺口。
- **§3.1 正交矩陣**：只有 TW 寫 `feature_values`/`prodset`/`promotion_queue`；只有 LAI 寫 `local_model_*`；只有 RAW 寫 `raw_table_coverage_snapshot`；`evolution_hypothesis_hint`＝唯一跨軸表（UNIQUE dedup_key＋decision 單向前進＋無 FK 故障隔離）。
- **§3.2 六條邊**：RAW→TW（hint→人閘 H3→curate_pme_map_expand 只吃 approved）；RAW→LAI（**唯一已真接上**：build_eval_set 直讀三 SSOT 表；但產物落 L3/L4＝無內容鑑別力層 → `V2-RUBRIC-go` 前**不可量測**）；TW→LAI（brief/1，Phase 6 後、前置=arena 有 settled 列——已達成）；LAI→TW（行為類 hint）；TW/LAI→RAW（唯讀回饋）。
- **§3.3 共用零件裁決**：C2 三 ledger **不合表**（同構 DDL 常數模組＋pytest 斷言）；C3 heavy_slot 兩階段（flock 已上；第二版 pg advisory 須**自持長生連線**——`db.connect` finally 關連線會靜默放鎖）；C4 證據協定 `evidence_protocol.py`（live 臂須同時勝 floor+mismatched 寫成程式）；C5 誠實閘**只擋 DELETE/TRUNCATE、不做 UPDATE-GUC**（GUC 對唯一自動寫入者豁免＋ON CONFLICT 首過再死）；C6 停機＝`evolution_kill_switch.scope`（tw/lai/raw/global），TRI-HALT 表已撤回。
- **§3.4 方法移植**：M-1 對照臂→TWEVO（**最高價值**：G-PROM 零對照臂、54 測 3 過≈雜訊期望 2.7；`volume_gini_60d` direction=+1 但 mean_ic=-0.054/hit 0.25 仍過閘佔 prodset n=2 之半＝符號盲，`evolution.py` 零處讀 direction）；M-2 deflation→LAI（n_trials 入帳；LAI 搜尋**不得**寫 trial_ledger）；M-3 5-oracle 單一住所（gold verdict 983 全 'oracle_pass' 是字串常數非裁決）。
- **§3.5 隔離不變式 I1-I9**：I3＝`src/augur/evolution/` 目前三重盲區（PIPELINE/FORBIDDEN/LITERALS 皆不含）；I8＝principle_domain_map 禁 join principle_factor_map（且實查 0 列、35 principle 全 investment、無他域原理可映射——第一步是人撰非 code）；I9＝FZ 豁免已於 07-26 落 mdc（V2-FZ-scope：日頻增量 daily_maintenance＋FRED；arena 每日出單 cron 已掛）。
> ⚠ **2026-07-27 對抗驗證更正（讀本檔 §6/§10 前必看）**：下文「behavior F@L1 0.933＞0.167＝判準 A PASS」**在能力語意上已被證偽**。親驗：13 行零知識格式規則機（不看內容、只認題幹開頭）於 L1.F/L1.P/L3.A/L4.A **全拿 1.000**、與 ceiling 打平且勝過每一個 LLM 臂；echo 臂 F@L1=1.000 勝 behavior；常數字串 `VARCHAR` 得 0.2333 亦越過 0.167 門檻。且 floor 與 mismatched 在 F@L1 **結構性恆為 0**＝空門檻。「可複現」則因 `run_id` 去重＋`ON CONFLICT DO NOTHING` **結構上不可記錄**（DESKTOP 0.933 vs 本機 0.967 同尺同模型不一致）。SUNSET (c) 之週報假綠已停（改記 ⚠ 未判定）。詳見 `audits/V2-SUNSET-C-DISPUTED-20260727.md`，判準器修補全部待 hugo。

- **§6 分階段**：Phase 0 止血 **✅07-26 完**（LLM 單槽鎖/去重/降頻/fail-closed 舊評分/arena fail-loud）；Phase 1 EXP1 **✅完**（behavior F@L1 0.933>0.167=判準 A PASS；grammar 亦 0.933→行為守則在 F 軸零貢獻；L2 兩臂 P=0.000＝真缺口；判準 B＝RAW→LAI 邊「不可量測」照預註冊寫）→分叉＝**進 Phase 2＋V2-RUBRIC-go 排下一人裁**；Phase 2 焊死（V2-ISO-go+V2-HONESTY-go：isolation 三處擴充+4 pytest／predict role unregistered 桶 fail-loud／PME 六表 DELETE 拒閘／kill_switch scope／題庫漂移哨兵／check_plan_consistency）；Phase 3 RAW 唯讀先行；Phase 4 TWEVO 對照臂+GATE-raise；Phase 5 五表 DDL（前置=跨軸邊有實料——arena settled 已達成）；Phase 6 三軸開輪。
- **§8 人閘 H1-H10**：H1 V2-P-yes+SUNSET；H2 serving 晉升（pp_3ab2 晉升依據已作廢待處置）；H3 hint approve；H4 GATE-raise；H5 volume_gini_60d 回溯；H6 V2-RUBRIC-go；H7 S0 audit 補登錄；H8 P5.W5；H9 V2-FZ-scope（✅已落 mdc）；H10 principle_domain_map 人撰。§8.1 誠實條文：單帳號機無法機械區分 AI/hugo 簽名＝榮譽制+事後偵測；augur_human 角色已裁不做。
- **§10 明確不做**：LoRA 全鏈（復活條件之一「behavior 與 grammar 有可複現差距」首批**不成立**——兩臂同 0.933；唯 L2 P=0.000 缺口是未來重議入口）；cross_notify 表；三 ledger 合表；30 條驗收接審議引擎（82 件積壓 0 解決）；RAW 缺口寫 gold（永不）。
- **§11 誠實天花板**：不能證「答得更準」（P/A 只證行為類別）；RUBRIC 前 RAW→LAI 不可量測；prodset 成長瓶頸=訊號強度非覆蓋（17→35 已證偽擴覆蓋路）。

---

## 2026-07-27 增補四：Phase 4 完整閉環（PC002 執行完畢）

**TWEVO 的尺修好了、且第一輪就咬人**：①對照臂 200 draws/臂實測**經驗偽陽率 9.0%（shuffled）/10.5%（mismatched）＝名目 α 兩倍**→GATE-raise 預註冊規則觸發、APPLY 篩升嚴至 |hac_t|≥**2.643**（p95）。②驗收重跑 run_id=2（58 maps）：**FAIL_SIGN=7——volume 集中度全家族**（gini_20d/60d、max_share_20d/60d、top_holders_pct、debt_ratio、gov_bank_net_buy_60d）顯著反向，符號盲時代全體漏網。③APPLY（R2/R3 全自動）：7 demote（volume_gini_60d validated→**sign_refuted**、prodset removed）＋1 promote（inst_cumflow_position_120d **過升嚴門檻**）；**prodset active n=2→1**（B2 賭注的誠實收場：「prodset 可能歸零——這是誠實的結果不是失敗」）；apply_log 8 列 `gate_ref='V2-AUTOADVANCE'`＋auto_rule 落帳（R6 digest 素材）。工程教訓：demote 通道原不存在（晉升自動/除役無門）＝volume_gini 賴在 prodset 的機械原因；apply 實跑=無 `--dry-run` 旗標（無 `--apply` 旗標）。

## 2026-07-27 增補三：LAIEVO 教材跨域化（hugo 拍板）

**「know how 不需要分域，交互相關學習提高本地 AI 能力」**——RUBRIC v2 換尺**同批**把 eval 母體從兩域（quant_finance/software_engineering）擴為全知識層跨域（含 ttai owned_local＋raw catalog），單次破尺不二段跳；gold 收割/self_seek 選材同步撤域限。不變式：量化隔離/私有邊界/0/1 機械判準/舊集 4183475c5089 封存可比——全部不動。域欄降為 provenance 注記、不再是學習迴路的牆。登錄＝PHASE4 audits §七。

## 2026-07-27 增補二（治理演進；讀 v2 前必看）

**⓪ `V2-AUTOADVANCE` 已生效（hugo 對話拍板「回覆 V2-AUTOADVANCE-yes 即生效」）**：預註冊自動推進規則集 R1–R7＋H10 分層裁定，SSOT＝`audits/V2-AUTOADVANCE-PROPOSAL-20260727.md`（ENACTED）。要點：TWEVO 閘內 auto-APPLY（雙綠∧kill clear∧FAIL_SIGN 過∧偽陽率≤10%、單輪上限 1）；H5 預決＝FAIL_SIGN ⇒ demote＋追加註記；LAIEVO pack 未勝零訓練基線 auto-retire（晉升仍人簽 P5.W2）；hint 升級**不**自動（Goodhart 防線、週日 digest 批覆）；R6 連續 2 週 digest 無人認領⇒自動降回逐案人閘。同日其他拍板（Phase 4 開／RUBRIC／H2 重評方向／兩機乙案）＝`audits/V2-PHASE4-RUBRIC-H2-APPROVED-20260727.md`。
**① kill_switch scope 缺口已修**：C6 升級 DDL 正辦住所＝`evolution_ledger_ddl.KILL_SCOPE_STMTS`（原斷言稱住 migrate_philosophy_evolution_ddl 係**虛指**、該檔實查零 scope）；本機四 scope 種子已落、effective[tw/lai/raw] 可讀。
**② `evidence_protocol.py` 已落地**（C4 鐵則機械化；自測錨在兩機逐位元一致的實測值）；其 docstring 曾因寫出 LAI 表名字面被 laievo 隔離掃描抓到——**Phase 2 焊死對自己人也生效**之實證。

## 2026-07-27 增補（PC002-S1800 實查；讀 v2 前必看）

**① `V2-P-yes` 已正式拍板生效**（`audits/V2-ADOPTED-SUNSET-20260726.md`，hugo 對話拍板、claude 繕寫登錄、二者分立記載）。同批隨拍授權 **`V2-ISO-go` ＋ `V2-HONESTY-go`**（Phase 2）。`V2-SUNSET` 已凍結：**期限 2026-10-31**、三選一續命、全未達成則三軸整體停止＋帳本封存＋**不得換 trigger_code 重開**；`criteria_sha256=65eda89328adc75d95e6e03dcf0f31571d5cbb5131efefa45ce9c856d7d8cd01`。拍板時點誠實基線：(a) 半達成 (b) 未達成 (c) 半達成。

**② ⚠ 本機（PC002-S1800）DB 落後計畫整整一個工作天——接續前必讀**：本機 DB 還原自 `augur_pgdump_20260726_Fd`，而該 dump 之 `toc.dat` 產生於 **2026-07-26 08:49（早上）**，S0 新尺卻是**同日 16:12** 才建。故本機實查（07-27）：

| 項目 | v2 §1.1 錨（07-26 晚） | 本機實查 |
|---|---|---|
| `local_model_eval_item` | 120 題（`set_id=4183475c5089`） | **0** |
| `local_model_eval_run` | 12 列（四控制臂） | **0** |
| `local_model_gold_sample` | 1103 | **279** |
| `local_model_version` | 5 | 4（serving 仍 `pp_3ab2efebb04e`） |
| arena 首批結算 | 4,128 已結算 | 4,128 列但 **settled=0**、pred_date 僅 07-15/16 |

→ **LAIEVO Phase 1 在本機無法直接接續**：凍結題庫與四臂基準（floor=0.000／shuffled F@L1=0.167）都不在，而跨 `set_id`／`eval_code_hash` 比較一律 fail-loud 拒比，本機重跑 `build_eval_set.py` 會得到**不同 set_id**、接不上那 12 列。要接續須向 DESKTOP 取更新的 dump。`direction_gate` 三門（D_1／D_5／D_5_v2）本機皆 `evaluated_fail`。

**③ 程式落地現況（本機 git HEAD `dec05f2` 實查）**——已存在：`evolve_cycle`／`evolve_self_seek`／`eval_local_model`／`build_eval_set`／`run_raw_evolution_iteration`／`run_philosophy_evolution`／`apply_evolution_promotions`／`curate_pme_map_expand`／`set_evolution_kill_switch`／`verify_eval_set_validity`／`check_plan_consistency`／`src/augur/evolution/behavior_rubric.py`／`src/augur/audit/evolution_ledger_ddl.py`。**尚未寫**：`run_evolution_iteration.py`（TWEVO driver）／`report_triple_evolution_week.py`（§2.2 週儀表第一行印 SUNSET）／`verify_evolution_acceptance.py`（A0–A12 落點）／`validate_evolution_contract.py`／`export_evolution_advisor_brief.py`／`evidence_protocol.py`／`evolution_contract.py`／`heavy_slot.py`。

**④ 本機 DDL 狀態**：三本 ledger（`raw_evolution_iteration_ledger`／`evolution_iteration_ledger`／`local_ai_iteration_ledger`）與 `evolution_hypothesis_hint`／`evolution_evidence_run`／`evolution_prereg_gate`／`evolution_deferred_work`／`local_model_eval_set_check` 於 2026-07-27 由 `migrate_evolution_v2_ddl.py --apply` 建於本機（**全部 0 列空表**——dump 較 git 舊，此為補齊 DDL 對齊而非開 Phase 5）。誠實帳本 guard 已補至 **10/10 表全覆蓋**（原 dump 只有 `trial_ledger`／`revalidation_baseline` 有閘，8 張 PME 表全裸）。**但 `evolution_kill_switch` 本機仍無 `scope` 欄** → Phase 2.4（C6 停機語意）尚未落地於本機。

**計畫落後於事實的地方（讀 v2 時須帶著的更正，07-26 晚）**：§1 錨的「arena settled 全 NULL」已過期（4,128 全結、首批覆盤完成、每日出單 cron 20:00+結算 21:30 已掛、oneshot 退場）；「0.5087」已改平手口徑 0.5080；計分板已有三基準並排+常數隊自動標示；observation prereg＝`audits/ARENA-WATCHLIST-PREREG-20260726.md`。評測尺教訓見 [[eval-boilerplate-floor]]；硬體與 LoRA 裁決見 [[gb10-unavailable]]。
