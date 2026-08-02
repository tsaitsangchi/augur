-- ============================================================================
-- ops/d2s/sim_cal_r1_insert.sql — SIM-CAL-R1 預註冊門 INSERT（D2S §7 步 3 骨架填實）
-- ----------------------------------------------------------------------------
-- 執行前提＝hugo 親跑（psql 親簽載體;先例=E2/H2;AI 不代跑、不代簽）。親簽前門不生效。
-- 圈選依據：reports/w2_20260801/D2S_sim_prereg_gate_proposal.md §9 D2S-同意
--   （①甲 house-sha 二級錨定＋②T-A 嚴案＋③甲 逐輪一列＋④甲 零新碼 psql 親簽;2026-08-02）
-- 預覽 criteria_sha   = 9e0abe040c7dc1e515c25dc40b546fce6238afede81fe30bc0ad48cbf882c23b
-- 預覽 thresholds_sha = cd1e623a5a173c2a9e9823856fd76474defe82cccf41dbbeeba7bb47baf5e9d4
-- 覆算式（呈案 §6-2 兩級）：
--   criteria_sha   = encode(sha256(convert_to(criteria->>'criteria_text','UTF8')),'hex')
--   thresholds_sha = encode(sha256(convert_to((criteria->'thresholds')::text,'UTF8')),'hex')
-- 執行方式（於 repo 根目錄;git_sha 由 \set backtick 於執行時代入）：
--   set -a && . ./.env && set +a
--   PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
--     -f ops/d2s/sim_cal_r1_insert.sql
-- ============================================================================
\set ON_ERROR_STOP on
\set git_sha `git rev-parse --short HEAD`

WITH c(t) AS (VALUES ($CT$門：SIM-CAL-R1（sim 軸首輪校準評估之預註冊門；專章 §3.1；D-2）
評估對象：sim_evolution_candidate 之 method 於 simulation_method_registry status='registered'、
  且本輪繫 gate_ref='SIM-CAL-R1' 之候選（首輪即 iid_bootstrap 之 spec 變體；origin 依專章 §2.2-2.3）。
樣本外窗（§3.3）：live 臂唯計 mc_simulation_run.asof_date ≥ 本門 approved_at 次一交易日之新 run；
  首輪 horizon 唯 h=21（交易日）；asof 取樣＝每 21 個交易日一格（窗不重疊）、至少 K=3 格；
  target 集＝史料 52 檔個股（凍結清單 SQL：SELECT DISTINCT target_id FROM mc_simulation_run
  WHERE target_id ~ '^[0-9]+$'；其排序串接 sha256=649221f491e67048b23ee19f36b85274b588d0896e86447a42203b4125982ce4）；
  PORT_* 不入首輪（結算口徑未定＝impl plan U-3）。
結算：sim_realized_outcome settle_mode∈{normal,last_trade}；unsettleable 除外並計入 n_excluded。
臂組成（§3.4 五臂地板；定義凍結）：
  live＝候選 spec 於真實資料之分位錐；
  ceiling＝同窗實現值之事後經驗分位錐（oracle 參照；僅作上界、不參賽）；
  floor＝無條件常數錐：全史 pooled 日報酬 σ 之常態錐、全 target 全 asof 同一 σ（樣板地板）；
  shuffled＝同 asof×h 內 target 間實現值重排（seed=42）；
  mismatched＝target i 之錐配 target j≠i 之實現值（固定 derangement；seed=42）；
  robot＝選配第六臂（加嚴參照、非地板要件）。
判準門檻（T-A；數值見 thresholds 鏡射，thresholds_sha 錨定於本文末行）。
判死（§3.2 可證偽；任一成立即 killed）：
  k1 |cov_p80−0.80|＞tol 或 |cov_p90−0.90|＞tol（tol 依 T-案）；
  k2 live 之 crps_mean 未依 T-案判法勝過 floor、shuffled、mismatched 三臂之每一臂；
  k3（唯 T-A）PIT KS 依日期簇 bootstrap 臨界值 p＜0.05。
undecidable（§5.4）：n_valid＜下限、或日期簇＜K、或任一臂缺 ⇒ undecidable（不得作 pass 用；誠實無能為合法產出）。
promoted 前提：k1-k3 全數反向成立＋arms_covered ⊇ 五臂（chk_sev_five_arm_floor）＋人簽三欄
  （chk_sev_promote_signed；gate_proposal_ref 指向 enacted governance_proposal）。本門非晉升唯一鎖。
評估紀律：評估前覆算 sha256(criteria->>'criteria_text')＝criteria_sha、
  且覆算 sha256((criteria->'thresholds')::text)＝本文末行 thresholds_sha，任一不符即拒評（§3.1）；
  eval_code_hash 落 sim_calibration_eval；同 (gate,candidate,arm,eval_set,code_hash) 唯一（uq_sce_cell）；
  史料（asof≤2026-05-31）之任何數字不得入本門證據列。
換尺＝換身分（§5.3）：判準、臂定義、評估碼實質變更 ⇒ 開新 gate_id、本列轉 superseded；分數不跨尺比較。
thresholds_sha=cd1e623a5a173c2a9e9823856fd76474defe82cccf41dbbeeba7bb47baf5e9d4$CT$))
INSERT INTO evolution_prereg_gate
  (gate_id, axis, purpose, criteria, criteria_sha, status, approved_by, approved_at, git_sha, note)
SELECT 'SIM-CAL-R1', 'sim',
       'sim 軸首輪合法評估之預註冊門（專章 §3.1;判準先於資料;D-2）',
       jsonb_build_object('criteria_text', t, 'thresholds', $TH${"horizon_td": [21], "n_windows_min": 3, "n_valid_min": 100, "date_clusters_min": 3,
 "cov_tol": {"p80": 0.05, "p90": 0.05},
 "skill_metric": "crps_mean", "skill_arms": ["floor", "shuffled", "mismatched"],
 "skill_test": {"kind": "date_cluster_block_bootstrap", "B": 1000, "seed": 42, "one_sided_lcb": 0.95},
 "pit": {"test": "ks", "p_min": 0.05, "critical_values": "date_cluster_bootstrap"},
 "settle_modes": ["normal", "last_trade"],
 "targets_sha": "649221f491e67048b23ee19f36b85274b588d0896e86447a42203b4125982ce4",
 "promoted_allowed": true,
 "calendar": "twse"}$TH$::jsonb, 'round', 'R1'),
       encode(sha256(convert_to(t, 'UTF8')), 'hex'),
       'approved', 'hugo', now(), :'git_sha',
       'D2S 呈案;T-A 圈選;criteria_text 唯一 binding、thresholds 鏡射由文末 thresholds_sha 錨定'
FROM c;
