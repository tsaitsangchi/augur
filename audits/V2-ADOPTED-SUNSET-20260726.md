# V2-P-yes ＋ V2-SUNSET 拍板登錄（2026-07-26）

> **性質**：拍板登錄（比照 `TRI-SELF-EVO-PLANS-APPROVED-NO-EXEC-20260726.md` 先例）。
> **hugo 對話拍板原文（逐字）**：
>
> 「V2-P-yes；V2-SUNSET：期限 2026-10-31，條件＝§2.1 之 (a)(b)(c) 三選一達成即續命，全未達成則三軸整體停止、帳本封存、不得換 trigger_code 重開」
>
> **簽名誠實註記**（§8.1／[[never-type-human-signature]] 紀律）：本檔由 claude 依 hugo 對話拍板繕寫登錄；
> 決策者＝hugo、繕寫者＝claude，二者分立如實記載，不冒充親簽欄位。

## 一、V2-P-yes（採納）

- `reports/augur_self_evolution_master_plan_v2_20260726.md` 自即刻起為**三軸自進化總控／介面契約 SSOT v2**。
- `augur_triple_self_evolution_master_plan_20260726.md`（TRI-v1）降為前身史料；`TRI-P-yes`／`TRI-IFACE-yes` 由 `V2-P-yes` 承接；未被 v2 修訂之 TRI-v1 條文續行。
- 隨拍執行授權（承 hugo 拍板前一則訊息之明示包裹——「我收到後…立即開 Phase 2 焊死六件」，hugo 以本拍板回覆）：**`V2-ISO-go` ＋ `V2-HONESTY-go`**（Phase 2；其 §12.2 前置僅 `V2-P-yes`，已成立）。

## 二、V2-SUNSET（program-level 落日，凍結）

**期限**：2026-10-31
**續命條件（三選一達成即續命；引 v2 §2.1 原文）**：
(a) arena 至少結算一批且方向門有可讀數；或
(b) `evolution_production_feature_set` active 由 2 成長，且每一新成員通過符號一致性檢查；或
(c) LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched，且該結論可被獨立重跑複現。
**全未達成之後果**：三軸計畫整體停止、三本帳本封存為史料、**不得以更換 trigger_code 重開**；重啟須新開一份計畫並重新拍板。

**criteria_sha（凍結雜湊；標的＝上方「期限＋三條件＋後果」四行之 UTF-8 全文）**：見本檔尾行機器附記。
**挪門柱紀律**：升嚴須走 `GATE-raise`、放寬一律不許；本檔一經 commit，修訂唯增列、不回改（P4.E3）。
**遷移**：Phase 5 `evolution_prereg_gate` 建表後，本列轉入該表凍結（axis='program'），本檔留為原始憑據。

## 三、拍板時點現況快照（誠實基線，防事後美化起跑線）

- 條件 (a)：**半達成**——arena 首批 4,128 列已結算（07-26）；「方向門有可讀數」未達（cluster=2／需 60；每日出單 cron 已掛、07-27 起走）。
- 條件 (b)：**未達成**——active=2，其一（volume_gini_60d）符號反向待人裁（H5）。
- 條件 (c)：**半達成**——behavior 臂 F@L1=0.933 勝 floor(0)與 mismatched(0)；「獨立重跑複現」未跑。

---
機器附記：criteria_sha256 = `65eda89328adc75d95e6e03dcf0f31571d5cbb5131efefa45ce9c856d7d8cd01`（標的全文如 §二；驗算：對該五行 UTF-8 取 sha256）
標的原文冗餘備份（驗算用）：
```
期限：2026-10-31
(a) arena 至少結算一批且方向門有可讀數；或
(b) evolution_production_feature_set active 由 2 成長，且每一新成員通過符號一致性檢查；或
(c) LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched，且該結論可被獨立重跑複現。
全未達成：三軸整體停止、帳本封存、不得換 trigger_code 重開。
```
