# W2 呈案批索引（2026-08-01）——17 份，圈選即施作

> 產出＝10 路平行草擬（`wf_d0161d65-a01`，10/10 零失敗），每份含：現況親驗（現查非抄舊數）／
> 完整 DDL·diff／選項與建議案＋證偽條件／風險回滾／機械驗收／**Steward 決定欄（留白）**。
> 圈選格式同呈案單：`A3-同意`、`B2/B3-同意`、`E1-改採B′` 皆可，批次可。
> 建議裁決順序＝`augur_steward_adjudication_sheet_20260801.md` 尾節（殭屍批→本週→可批次）。

| 檔 | 內容 | 建議案 |
|---|---|---|
| A3_gsign_gate_proposal | G-SIGN 四件套逐檔 diff＋77 筆三案＋十驗收十回歸鎖 | 通過；UNJUDGEABLE⇒FAIL；乙案 |
| B2_deferred_disposal | 7 筆逐筆 SQL（BEGIN/COMMIT＋DO 斷言整包回滾） | 探針 test-artifact／#4·#5·#11 superseded |
| B3_drain_stale_hold | decide() stale-hold 8-hunk diff＋重啟程序 | 修好再重啟（前置 B2＋B1-apply） |
| B4_update_guc_upgrade | 3 表升級＋1 表新掛 GUC 閘 DDL＋寫入者 9 檔 10 點盤點 | 甲案（先合通行證補丁後上 DDL） |
| C1_manual_validity | valid_until 三段 DDL＋verify 端 diff | 90 天（到期恰在 10-14 復審前） |
| C2_attestation_watchdog | watchdog DB 三態機 diff＋假綠實證 | 照案；FinMind 沿用既有 throttle |
| D2_kh8_discrimination | discrimination_verdict 全文＋三門檻後果表 | 0.05 |
| D3_kh5_axis_evidence | kh4.py 逐 item 軸覆蓋 diff＋ready 率預估 | 照案 |
| D4_repromotion_lock | 再晉升鎖 DDL＋通行證 GUC | 證據繫結案 |
| E1_dgate_disposition | 三門兩案（A supersede 指令全文／B′ 工作量估） | A 案 |
| E2_headline_anchor | alpha_headline_anchor DDL＋親簽 INSERT 範本 | 建表＋hugo 簽兩錨 |
| F1_ruling_042_draft | RULING-2026-042 六節草稿＋同 commit 施作清單 | 照案 |
| F5_three_rules_clause | CLAUDE.md 三規則條文草案（向前生效） | 通過 |
| G2_offsite_backup_options | 三案比較（威脅分層＋敏感性盤點） | A 外接碟主＋C 第二機輔 |
| G3_identity_sandbox | 沙盒演練逐條指令＋最小接線＋零消費者誠實條款 | 照案 |
| H1_laievo_rcell | R-CELL′ 預凍全文＋13 run 快照＋S-8 條款 | 照案（不換尺） |
| H2_sim_first_method | derive schema 規畫＋mc_baseline 入冊逐步 | 照案（親簽點明標） |

## 呈案批對登錄冊之修正（agents 親驗抓到的過期數字，已各自明標）

- A3：「波及 7 呼叫端」實為 **6 呼叫端＋1 手寫七閘 dict**（apply:89-91）；blast radius **67→77**（run 20 灌入）；「running=0」時機約束改**三查**（pgrep 空∧slot 空∧ledger 零 running——殭屍 9 列使原句不可用）。
- B2：「#4/#5 補跑 vs superseded 二擇一」實際只剩 superseded 一路（補跑已真實發生過並燒道 13.3h）；**timer enabled+Persistent ⇒ 重開機自動復活並對 7 筆全 rerun**——B2 宜速裁（或先臨時 disable）。
- B4：「四表升級」實為 **3 升級＋1 新掛**（feature_sign_check 原零 trigger）；「23 表全裸」實為 **22**（sim_evolution_verdict 另有 sev_no_update 已閘）。
- A3 附帶發現（另案）：週報 (b) 讀 sign 表採 `DISTINCT ON (feature)` 最新列——引擎雙寫單 h 列後可能遮住 h20 列，宜改 per-(feature,h) 全 PASS 口徑。

## 待裁之外的既備件

`backfill_evolution_run_zombies.py --apply`（B1，9 列）與 `execute_sunset_consequence.py`（F3，落地不啟用）為執行件非呈案，裁決同批圈選即可。

## 預製波追加（2026-08-01 夜；圈選點）

- **D2S_sim_prereg_gate_proposal**：SIM-CAL-R1 判準＋T-A 嚴/T-B 寬兩組門檻＋四圈選點（sim 門立前一切 sim 數字屬 self-reported）。
- **B4P2_remaining_tables_proposal**：19 表三批（P2a 治權 6 表先／P2b 引擎 6 表 run 21 後／P2c sim 七表緩議）；⚠13 表 legacy trigger 名分居 3 檔、照抄 P0 卸不掉舊閘（已載修法）。
- 另 `reports/augur_identity_mismatch_triage_20260801.md`：37 例預裁包（A=34/B=1/C=2；建議 MM-A+MM-B 全收、MM-C 留人裁）。
- **I5B_engine_supersede_diff_20260802**：I5B-甲 引擎 diff 呈文（待 hugo 逐字過目；窗至 08-03 23:00）。
