# G-PROM-D2 probe [I]（20260724）

* since=`2021-01-01` h=`60` panels=`22`
* GATE-keep `min_abs_hac_t=2`；multi-seed／G-ECON＝SKIP（候選表）
* JSON：`reports/augur_gprom_d2_probe_20260724.json`

| feature | table | mean_ic | |hac_t| | n | G-PROM | G-ECON |
|---|---|---:|---:|---:|---|---|
| `lending_fee_rate_mean_30d` | feature_values | 0.04180123339040098 | 1.8755820335693179 | 20 | SKIP | SKIP |
| `days_since_high_252d` | feature_values | 0.05049727653585314 | 1.673003623053691 | 20 | SKIP | SKIP |
| `lending_fee_rate_mean_20d` | feature_candidate_values | 0.08330142004986081 | 2.631940471598567 | 20 | SKIP | SKIP |
| `lending_fee_vw_mean_20d` | feature_candidate_values | 0.07994638404761033 | 2.9364388050503014 | 20 | SKIP | SKIP |
| `log1p_days_since_high_252d` | feature_candidate_values | 0.05049727653585314 | 1.673003623053691 | 20 | SKIP | SKIP |
| `days_since_high_126d` | feature_candidate_values | 0.04853571965873959 | 2.070140172212189 | 20 | SKIP | SKIP |
| `days_since_high_252d_raw` | feature_candidate_values | 0.05049727653585314 | 1.673003623053691 | 20 | SKIP | SKIP |

## 判讀

* 新名 G-PROM＝PASS 且 |hac|≥2 → 可另令 map＋開 MAP-S3；**本腳本不 APPLY**。
* 仍 FAIL → 留下對照＝實驗成功（定義噪音假說被否／未解）。
* ≠可交易／確立級。
