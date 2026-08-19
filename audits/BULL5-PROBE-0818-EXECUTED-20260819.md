---
status: executed
series: s4_s5_verify
track: BULL5
date: 2026-08-19
viewpoint: 2026-08-19T13:06+08:00
asof: "2026-08-18"
shell: scripts/probe_bull5.py
lib: src/augur/evaluation/bull5.py
json: /tmp/bull5-2026-08-18.json
audit_json: audits/BULL5-0818.json
paste: "BULL5-probe-go | date=2026-08-18 | k=10 | dry-run | 條件≠可交易"
selftest: green
fake_b3_0819: rc=3
n_bull5_long: 9
n_bull5_short: 1
n_shown_long: 9
n_shown_short: 1
intersect_entry_long: 0
intersect_entry_short: 0
intersect_watch_long: 5
wrote_prediction_values: false
version: BULL5-v1
self_reported: true
layer: "[I]"
---

# EXECUTED｜BULL5 探針＠2026-08-18

Steward 貼 `BULL5-probe-go | date=2026-08-18 | k=10 | dry-run | 條件≠可交易`。零寫庫。未 promote。未改 standing。未開 CASC／SMA。`--date 2026-08-19` → rc=3。

閘＝H10…H240 全＞0 ∧ H5＜0。排序＝mean(H60,H120,H240) 降序、H5 升序。標籤禁止「可當進場條件」。

## 答

| | 做多 | 做空 |
|---|---|---|
| 過閘（全列） | **9**（n＜k 不補） | **1** |
| ∩ UP-PULL 進場 | **0** | **0** |
| ∩ WATCH 觀察 | **5**（茂訊、技嘉、藍天、南帝、桂盟） | 0 |

做多第 1＝**2484 希華**（H5 −1.9%、H240 +235.9%）。**3017 奇鋐不在**（H5 仍正）。做空第 1＝**5519 隆大**（條件排序，≠可空）。

與計畫書 §3.4 預診 9 檔、同一順序。路徑％＝已發生，不是未來漲跌幅。
