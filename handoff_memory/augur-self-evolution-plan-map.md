---
name: augur-self-evolution-plan-map
description: 自我迭代進化計畫 SSOT＝v2 總控(20260726);三軸 RAWEVO×TWEVO×LAIEVO;Phase 0/1 已完、Phase 2 焊死待 V2-P-yes;V2-SUNSET 落日須 hugo 親填;拍板碼與隔離不變式全錄
metadata: 
  node_type: memory
  type: project
  originSessionId: b6cddf62-b16d-44ba-af86-bbdb2cb161c8
  modified: 2026-07-26T13:03:00.356Z
---

**自我迭代進化的 SSOT＝`reports/augur_self_evolution_master_plan_v2_20260726.md`（891 行 13 節，14-agent workflow 產出＋親驗）。TRI-v1（`augur_triple_self_evolution_master_plan_20260726.md`）降為前身；`V2-P-yes` 承接 `TRI-P-yes`。三軸主檔：RAWEVO＝raw_data、TWEVO＝tw_prediction、LAIEVO＝local_ai_route_b（各 loop_plan_20260726.md）。**

**核心結構**：
- **§2 V2-SUNSET（v2 最重要新增）**：program-level 落日條款，**hugo 親填指標與期限、AI 不得代選**；三選一達成才續命：(a) arena 結算一批＋方向門可讀數（結算半已達成 07-26）(b) prodset active 由 2 成長且新成員過符號檢查 (c) LAIEVO 任一臂 F@L1 同時勝 floor 與 mismatched **且可獨立複現**——(c) 首半已達成（behavior F@L1=0.933），複現待跑。建議期限 2026-10-31。既有停損全停「輪」、換 trigger_code 即重開＝v1 致命缺口。
- **§3.1 正交矩陣**：只有 TW 寫 `feature_values`/`prodset`/`promotion_queue`；只有 LAI 寫 `local_model_*`；只有 RAW 寫 `raw_table_coverage_snapshot`；`evolution_hypothesis_hint`＝唯一跨軸表（UNIQUE dedup_key＋decision 單向前進＋無 FK 故障隔離）。
- **§3.2 六條邊**：RAW→TW（hint→人閘 H3→curate_pme_map_expand 只吃 approved）；RAW→LAI（**唯一已真接上**：build_eval_set 直讀三 SSOT 表；但產物落 L3/L4＝無內容鑑別力層 → `V2-RUBRIC-go` 前**不可量測**）；TW→LAI（brief/1，Phase 6 後、前置=arena 有 settled 列——已達成）；LAI→TW（行為類 hint）；TW/LAI→RAW（唯讀回饋）。
- **§3.3 共用零件裁決**：C2 三 ledger **不合表**（同構 DDL 常數模組＋pytest 斷言）；C3 heavy_slot 兩階段（flock 已上；第二版 pg advisory 須**自持長生連線**——`db.connect` finally 關連線會靜默放鎖）；C4 證據協定 `evidence_protocol.py`（live 臂須同時勝 floor+mismatched 寫成程式）；C5 誠實閘**只擋 DELETE/TRUNCATE、不做 UPDATE-GUC**（GUC 對唯一自動寫入者豁免＋ON CONFLICT 首過再死）；C6 停機＝`evolution_kill_switch.scope`（tw/lai/raw/global），TRI-HALT 表已撤回。
- **§3.4 方法移植**：M-1 對照臂→TWEVO（**最高價值**：G-PROM 零對照臂、54 測 3 過≈雜訊期望 2.7；`volume_gini_60d` direction=+1 但 mean_ic=-0.054/hit 0.25 仍過閘佔 prodset n=2 之半＝符號盲，`evolution.py` 零處讀 direction）；M-2 deflation→LAI（n_trials 入帳；LAI 搜尋**不得**寫 trial_ledger）；M-3 5-oracle 單一住所（gold verdict 983 全 'oracle_pass' 是字串常數非裁決）。
- **§3.5 隔離不變式 I1-I9**：I3＝`src/augur/evolution/` 目前三重盲區（PIPELINE/FORBIDDEN/LITERALS 皆不含）；I8＝principle_domain_map 禁 join principle_factor_map（且實查 0 列、35 principle 全 investment、無他域原理可映射——第一步是人撰非 code）；I9＝FZ 豁免已於 07-26 落 mdc（V2-FZ-scope：日頻增量 daily_maintenance＋FRED；arena 每日出單 cron 已掛）。
- **§6 分階段**：Phase 0 止血 **✅07-26 完**（LLM 單槽鎖/去重/降頻/fail-closed 舊評分/arena fail-loud）；Phase 1 EXP1 **✅完**（behavior F@L1 0.933>0.167=判準 A PASS；grammar 亦 0.933→行為守則在 F 軸零貢獻；L2 兩臂 P=0.000＝真缺口；判準 B＝RAW→LAI 邊「不可量測」照預註冊寫）→分叉＝**進 Phase 2＋V2-RUBRIC-go 排下一人裁**；Phase 2 焊死（V2-ISO-go+V2-HONESTY-go：isolation 三處擴充+4 pytest／predict role unregistered 桶 fail-loud／PME 六表 DELETE 拒閘／kill_switch scope／題庫漂移哨兵／check_plan_consistency）；Phase 3 RAW 唯讀先行；Phase 4 TWEVO 對照臂+GATE-raise；Phase 5 五表 DDL（前置=跨軸邊有實料——arena settled 已達成）；Phase 6 三軸開輪。
- **§8 人閘 H1-H10**：H1 V2-P-yes+SUNSET；H2 serving 晉升（pp_3ab2 晉升依據已作廢待處置）；H3 hint approve；H4 GATE-raise；H5 volume_gini_60d 回溯；H6 V2-RUBRIC-go；H7 S0 audit 補登錄；H8 P5.W5；H9 V2-FZ-scope（✅已落 mdc）；H10 principle_domain_map 人撰。§8.1 誠實條文：單帳號機無法機械區分 AI/hugo 簽名＝榮譽制+事後偵測；augur_human 角色已裁不做。
- **§10 明確不做**：LoRA 全鏈（復活條件之一「behavior 與 grammar 有可複現差距」首批**不成立**——兩臂同 0.933；唯 L2 P=0.000 缺口是未來重議入口）；cross_notify 表；三 ledger 合表；30 條驗收接審議引擎（82 件積壓 0 解決）；RAW 缺口寫 gold（永不）。
- **§11 誠實天花板**：不能證「答得更準」（P/A 只證行為類別）；RUBRIC 前 RAW→LAI 不可量測；prodset 成長瓶頸=訊號強度非覆蓋（17→35 已證偽擴覆蓋路）。

**計畫落後於事實的地方（讀 v2 時須帶著的更正，07-26 晚）**：§1 錨的「arena settled 全 NULL」已過期（4,128 全結、首批覆盤完成、每日出單 cron 20:00+結算 21:30 已掛、oneshot 退場）；「0.5087」已改平手口徑 0.5080；計分板已有三基準並排+常數隊自動標示；observation prereg＝`audits/ARENA-WATCHLIST-PREREG-20260726.md`。評測尺教訓見 [[eval-boilerplate-floor]]；硬體與 LoRA 裁決見 [[gb10-unavailable]]。
