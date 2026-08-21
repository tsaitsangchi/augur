---
status: go
series: s1s5_loop
track: FINMIND-FREE-RIDGE
product_id: FINMIND-FREE-RIDGE-v1
phase: P0-probe
date: 2026-08-21
layer: "[I]"
self_reported: true
paste: 完整計畫在 reports/augur_finmind_free_rankridge_plan_r21_20260821.md，依計畫進行最佳的下一步?
---

# GO｜P0 RankRidge-min FinMind 探針

Steward 依計畫走最佳下一步＝**P0**，不是解凍、不是改 L0／cron。

範圍：讀 `/user_info` 一次；`TaiwanStockPriceAdj`／`TaiwanStockInstitutionalInvestorsBuySell`／`TaiwanStockSecuritiesLending` 各先不帶 `data_id` 抓價頂單日，失敗再 `data_id=2330`。每表 ≤2、合計 data call ≤6。不寫 raw、不 heal、不開 93 表。見 403／額度滿即停。

有界豁免（≠ INV2 解凍）：僅本探針。arena 日更白名單不動。
