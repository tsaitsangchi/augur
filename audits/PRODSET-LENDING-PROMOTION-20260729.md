# lending_fee_rate_mean_20d 促升事件記錄（2026-07-29）

- **寫入行為**：hugo 親跑 staging(`feature_candidate_values`)→生產(`feature_values`)整批複製 17,072 列（含 staging 獨有 2026-06-30 panel）；當時零治理帳（prodset／apply_log 皆無列）——claude 鑑識上報後 hugo 對話定性「**我搬的**」。
- **治理補齊**：prodset 登記 `set_status='active', principle_id=107, last_action='human_promoted'`（claude 繕打，不冒充親簽 §8.1）；**TWEVO queue 外促升＝無 apply_log 屬誠實留白**（不偽造 queue 史）。
- **四關證據鏈**：G1 HAC t=2.63（G-PROM-D2 20260724）→ G2 增量四格全正（A2 20260729，3 seeds×2h×2 模型）→ 符號尺 5/5 PASS（dir=−1 掛 p107、5 bootstrap 全同號）→ 經濟終關（口徑改「canonical vs canonical−lending」重跑，結果另補）。
- **SUNSET (b)**：prodset active 1→2（門檻 >2、還差 1；新成員符號一致 ✓）。
- **連帶修復**：孤 panel 2026-06-30（生產僅此特徵有值）→ 以 build_feature_panel 補全該月面板（毒化風險除）；經濟終關重名炸空已定位（canonical 已含之特徵不得再 --add）。
- **殘餘債**：`feature_values` 無誠實閘（本次事件之所以無帳可查的根因）——上閘提案待 hugo 一字。
