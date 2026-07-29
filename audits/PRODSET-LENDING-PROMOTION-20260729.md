# lending_fee_rate_mean_20d 促升事件記錄（2026-07-29）

- **寫入行為**：hugo 親跑 staging(`feature_candidate_values`)→生產(`feature_values`)整批複製 17,072 列（含 staging 獨有 2026-06-30 panel）；當時零治理帳（prodset／apply_log 皆無列）——claude 鑑識上報後 hugo 對話定性「**我搬的**」。
- **治理補齊**：prodset 登記 `set_status='active', principle_id=107, last_action='human_promoted'`（claude 繕打，不冒充親簽 §8.1）；**TWEVO queue 外促升＝無 apply_log 屬誠實留白**（不偽造 queue 史）。
- **四關證據鏈**：G1 HAC t=2.63（G-PROM-D2 20260724）→ G2 增量四格全正（A2 20260729，3 seeds×2h×2 模型）→ 符號尺 5/5 PASS（dir=−1 掛 p107、5 bootstrap 全同號）→ 經濟終關（口徑改「canonical vs canonical−lending」重跑，結果另補）。
- **SUNSET (b)**：prodset active 1→2（門檻 >2、還差 1；新成員符號一致 ✓）。
- **連帶修復**：孤 panel 2026-06-30（生產僅此特徵有值）→ 以 build_feature_panel 補全該月面板（毒化風險除）；經濟終關重名炸空已定位（canonical 已含之特徵不得再 --add）。
- **殘餘債**：`feature_values` 無誠實閘（本次事件之所以無帳可查的根因）——上閘提案待 hugo 一字。

## 補記（同日）

全鏈入帳完成：`evolution_run=10`（human_promotion 事件列）→ `promotion_queue=311`（decided_by='hugo(對話拍板)〔claude 繕打 §8.1〕'）→ `evolution_apply_log=24`（gate_ref='HUMAN-PROMOTION'）→ prodset `last_action='promote'`。**四次 NOT NULL／CHECK 拒絕全記錄在案**——schema 誠實機械逼完整記帳，如設計。孤 panel 2026-06-30 補全建置已放；經濟終關改雙跑「canonical−lending vs canonical 全集」（`--drop-features` 新參數＋重名防呆）。prodset active=2。

## 補記二（同日）：經濟終關順序與首雙跑作廢

- 首次 econ 雙跑**作廢**：GRID-A 月頻加密於兩跑之間持續灌入 ≥2021-04 panel → 期數 17 vs 14、基準淨 12.6% vs 19.0%＝不同尺（claude 自查發現、未採信任何一側數字）。重跑排 GRID-A 收槍後之凍定網格。
- **順序誠實註記**：lending 已先promoted（人搬）→ econ 屬**事後補證**而非前置閘；若重跑判負，誠實路徑＝demote 提案呈 hugo（不迴避）。
