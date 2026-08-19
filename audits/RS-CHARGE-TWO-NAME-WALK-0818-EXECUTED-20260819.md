---
status: executed
series: s4_s5_verify
track: RS-CHARGE
date: 2026-08-19
viewpoint: 2026-08-19T11:10+08:00
asof_tip: "2026-08-18"
origin: "2024-01-02"
kind: two_name_path_gate_walk
not: RS-CHARGE-P2
json: /tmp/rs-charge-two-name-walk-20260818.json
sids: ["3017", "2395"]
entry: t+1
hold: 20
costs: none
ridge_pool: unavailable_daily
self_reported: true
layer: "[I]"
---

# EXECUTED｜奇鋐／研華路徑交集 · 歷史 t+1 報酬（研究、非 P2）

Steward 問能否依 RS-CHARGE 交集對這兩檔回測並列出報酬。能跑路徑閘；**不能**當成完整 RS-CHARGE（缺每日 Ridge 八窗 Top10）。零寫庫。未扣成本。≠可交易。08-18 過閘但無未來窗。

## 口徑

- 閘：L-A ∧ 現算 L-D（近 252 交易日還原高低）∧ H5＞0 ∧ H10＞0。無 L-C。
- 進場＝訊號日次一交易日；持有 20 交易日。只在條件由否→是時開一筆（出場前不重疊加倉）。
- 區間：2024-01-02～價頂 2026-08-18。

## 答

| | 奇鋐 3017 | 研華 2395 |
|---|---|---|
| 可評日／過閘日 | 635／213 | 635／103 |
| 轉折交易（20日） | 16 筆、9 勝 | 9 筆、6 勝 |
| 20日報酬複利 | **+137%** | **+61%** |
| 同期抱牢 | **+840%** | **+93%** |

重疊日（每天過閘都算一筆 H20，窗重疊）平均約 +8.7%，**不是**獨立交易。這兩檔是先選再回看，有倖存者偏差；不能外推到全宇宙。
