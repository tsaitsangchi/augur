# (b) 線候選庫存盤點——SUNSET 條件 (b) 之可推進料件全查（2026-07-28）

> [I] A1 交付（hugo 2026-07-28「照這個序自動往下走」；唯讀盤點、零執行）。SUNSET (b)＝`prodset active 由 2 成長＋新成員符號一致`，現況 **active=1**——本檔盤點「還有什麼料能走四道漏斗」。

## 一、prodset 現況（`evolution_production_feature_set`）

- **active＝1**：`inst_cumflow_position_120d`（07-24 註冊）。
- **removed＝7**（07-27 誠實清理）：debt_ratio／gov_bank_net_buy_60d／top_holders_pct／volume_gini_20d／volume_gini_60d／volume_max_share_20d／volume_max_share_60d——基線 2 因清理降 1；(b) 要 **>2** 即至少再添 2 個過全漏斗成員。

## 二、候選庫存（`feature_candidate_values`，已具值可直接進漏斗）

| 候選 | 列數 | panel | 出處與現況 |
|---|---|---|---|
| `lending_fee_rate_mean_20d` | 17,072 | 2021-03-31→2026-06-30、776 檔 | **G-PROM-D2 真窗候選，已過第 1 關**（hac_t=2.63；`augur_gprom_d2_probe_20260724.md`）；multi-seed／G-ECON **SKIP 未跑** |
| `lending_fee_vw_mean_20d` | 17,072 | 同上 | **同上已過第 1 關**（hac_t=2.94）；後三關未跑 |
| `days_since_high_126d` | 17,072 | 同上 | 高點距離族；漏斗全未跑 |
| `days_since_high_252d_raw` | 17,072 | 同上 | 同族（與既有 mapped `days_since_high_252d` 語意近似——增量門檻須嚴防同族冗餘） |
| `log1p_days_since_high_252d` | 17,072 | 同上 | 同族單調變換——**與 raw 版本質同訊號**，增量測試預期擇一 |

## 三、燃料線（下一批候選之源）

- **hint 待批 10 則**（`evolution_hypothesis_hint` decision='pending'）——在 digest 頁等你批覆；approved 後走 curation stanzas（三空格人填）→ `principle_factor_map`（現 77 列）→ 才能派生新候選值。**此段人閘、AI 不代**。
- **名實不符債**（07-26 計畫 §已記）：`lending_fee_rate_mean_30d` 非真 30d——回饋 map 時窗口語意須標明，防假對齊。

## 四、A2 執行計畫（夜間、臂後；已在核可序內）

1. **對 5 候選跑後三關**：`verify_candidate_promotion.py`（as-of 口徑＋去相關 Eff-t＋multi-seed 多因子增量——對 active=1 之現 prodset 測增量）→ 存活者進 `run_economic_eval.py` 經濟終關（IC 撐住 ≠ 可交易）。
2. **車道紀律**：CPU 重、待 v2 臂批（bsprow7jz）收槍後 `nice` 起跑（批次臂先跑之 directive 不破）。
3. **終點人閘不變**：四關全過者呈報告；**提拔入 prodset＝你簽**（符號一致性＋方向掛 principle 之 fuel-line 憲政），屆時 (b) 條件 active 1→2→3 才有真路徑。
4. 誠實預期管理：同族 3 候選大概率增量互斥擇一；借券 2 候選第 1 關 t 值健康但 multi-seed 與經濟關歷史上是主墳場（7 候選全滅前例）——**(b) 不保證今晚有進度，只保證漏斗誠實跑完**。
