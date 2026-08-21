---
status: executed
series: s1s5_loop
track: FINMIND-FREE-RIDGE
product_id: FINMIND-FREE-RIDGE-v1
phase: P0-probe
date: 2026-08-21
layer: "[I]"
self_reported: true
go: audits/FINMIND-FREE-PROBE-GO-20260821.md
fired: audits/FINMIND-FREE-PROBE-FIRED-20260821.md
json: audits/FINMIND-FREE-PROBE-20260821.json
---

# EXECUTED｜P0 RankRidge-min 探針（Sponsor 基線）

- 額度錶：**0/6000**（仍 Sponsor；**不是** free 600）
- 探針日＝價頂 **2026-08-20**
- data call＝**3**（每表 by-date 一次即過，未打 data_id=2330）
- `TaiwanStockPriceAdj`：by-date n=2802
- `TaiwanStockInstitutionalInvestorsBuySell`：by-date n=102023
- `TaiwanStockSecuritiesLending`：by-date n=1171
- scenario=**A**
- 不寫 raw、不改 L0、≠解凍

**到期（Steward 帳號頁 2026-08-21）**：Sponsor **2026-09-14**。秒級以 `/user_info` 為準。

**下一步（仍屬計畫，未開工）**：第一次讀到 `api_request_limit≠6000` 時重跑同一探針（P0′）；到期前不改 L0、不 93 表囤貨。
