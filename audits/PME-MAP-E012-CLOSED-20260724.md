# PME MAP-E012 CLOSED [I]（2026-07-24）

* Steward：「**開 MAP-E012**」＝S0＋S1＋S2（庫內可建）
* 拍板：`MAP-P-yes`＋`MAP-E012`＋`FZ-keep`＋`GATE-keep` → `audits/PME-MAP-EXPAND-PLAN-APPROVED-20260724.md`
* 計畫：`reports/augur_pme_expand_hypothesis_map_coverage_plan_20260724.md`
* 性質：[I]；**不**創設 [N]；**未**跑 S3／S4／U；**≠**可交易／≠確立級；**≠**解凍

## 做了什麼

| 階段 | 狀態 | 摘要 |
|---|---|---|
| **S0** | ✅ | `scripts/report_pme_gate_diagnosis.py`（矩陣＋`--selftest`）；報告 `reports/augur_pme_gate_diagnosis_20260724.md`／`.json` |
| **S1** | ✅ | `scripts/curate_pme_map_expand.py --apply`；**新 map 16 列**（16 特徵）；新學派 2（`short_term_reversal`／`short_interest`）；新 source paper×3；**deferred**＝`margin_usage_ratio`（無足夠可核文獻本輪零寫） |
| **S2** | ✅ | `roe`／`debt_ratio` 寫入 `feature_values`（asof 宇宙、panel≥2021-01-01）；`scripts/build_pme_fundamental_features.py`＋`augur.features.fundamentals`；panel 熱路徑已掛接 |
| **S3** | ❌ 未跑 | local-gates／APPLY 另令「開 MAP-S3」 |
| **S4／U** | ❌ 未跑 | 另令 |

## 數字（DB 親驗 2026-07-24）

| 項 | 前（計畫／run6） | 後（MAP-E012） |
|---|---|---|
| coverage distinct | mapped=17／missing=5／blocked_div=1 | **mapped=35**／**missing=3**／blocked_div=1 |
| `principle_factor_map` 列 | 42 | **58**（+16） |
| unmapped-in-fv | 17 | **1**（`margin_usage_ratio` deferred） |
| `roe` cells | 0 | **16182**（21 panels × ≤776 stocks；#1 缺列保留） |
| `debt_ratio` cells | 0 | **16140** |
| G-ISO | — | **0** violations |
| gate_cross run6 | PASS×PASS=2 等 | **未重跑**（GATE-keep；舊 run_id=6 仍為閘證據 SSOT） |

### S2 誠實缺口

* **未建**：`peg_ratio`（deferred_growth）、`piotroski_fscore`（deferred_complex）、`macro_regime`（blocked_fz／FZ-keep）
* **panel `2024-09-30`**：本輪 fundamentals batch=0（財報 as-of／釋出後無可算列）→ 該日無 roe／debt 寫入；其餘 ≥2021 面板有值
* **不**宣稱雙綠／active／n_feats 成長（未 S3／S4）

### S1 來源（禁 ai_generated）

* 既有校延伸：Wyckoff／Marks／Gompers–Metrick／Jegadeesh–Titman／Lefèvre／Ang et al.／Amihud＋Fama–French
* 新校：Jegadeesh 1990（短窗反轉）；Asquith–Pathak–Ritter 2005（融券）

## 硬邊界核對

| 碼 | 本輪 |
|---|---|
| FZ-keep | ✅ 零 FinMind／FRED；Dividend 未開 |
| GATE-keep | ✅ 未跑閘、未降閾、未手改 validated_* |
| ≠可交易／確立級 | ✅ |
| SKIP≠PASS | ✅ 未改寫舊 SKIP |

## 下一步（人）

回「**開 MAP-S3**」（仍 GATE-keep／FZ-keep）→ local-gates＋APPLY 僅真雙綠。  
S4 僅當 active 集合變更後另令。
