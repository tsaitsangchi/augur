# 預測正交 — 追溯拍板總表 [I]（2026-07-24）

* **依據**：Steward `PREDICT-ORTHOGONAL`（`audits/PREDICT-ORTHOGONAL-API-RULING-20260724.md`）  
* **效力**：屬預測／庫內切分範圍 → 追溯 **yes**；真需 API 補洞 → **仍 API 門**（不假 yes）  
* **yes 邊界**：允許依庫內資料 plan／實作／驗收  
* **仍否（全體共用）**：放量 sync、解凍取數、假稱資料洞已補、Dividend 缺股已滿、可交易／確立級（除非原計畫另有閘且已過）  
* **凍結**：FinMind／FRED **仍凍**（`.cursor/rules/finmind-fred-api-freeze.mdc`）

---

## A. 追溯 yes（預測／庫內切分範圍）

| # | path | 原先卡關理由（摘要） | 屬預測／庫內切分？ | 追溯拍板 | 效力邊界註 |
|---|---|---|---|---|---|
| 1 | `reports/augur_prodset_predict_hotpath_plan_20260724.md` | 計畫已出／執行未開；近程敘事常與「資料地基等解凍」並列 | **是**（prodset→train／predict；零 API／庫內 as-of） | ✅ **正式拍板** `P2H-P-yes`＋`P2H-E123`＋`FC-empty`＋`FZ-keep`（`audits/P2H-PLAN-APPROVED-20260724.md`） | 計畫已拍板＋近程執行**授權**；**執行未開**（須「開 prodset 熱路徑」）。≠可交易／≠確立級／≠解凍 |
| 2 | `reports/augur_prediction_sop_plan_20260705.md` | 文首「待拍板」；曾與放量／資料完整敘事綁讀 | **是**（端到端預測 SOP；可庫內） | ✅ **yes** | 庫內 train／predict／eval 可依案 plan／實作／驗收；仍否放量 sync |
| 3 | `reports/augur_stock_prediction_sop_20260705.md` | 端到端 SOP；增量／cron／as-of 前推曾混 API | **是**（預測骨幹） | ✅ **yes** | 同上；tradability 等閘值仍須原案決策層，但不因 API 凍否決庫內路徑 |
| 4 | `reports/augur_prediction_sop_master_20260706.md` | plan-first 主計劃；歷史與資料地基敘事交織 | **是** | ✅ **yes** | 庫內階段可拍／可做；需新 raw 之節點 → 見 B |
| 5 | `reports/augur_prediction_deployment_plan_20260707.md` | 部署／再驗證；role／DDL／harness | **是**（predict runtime／部署） | ✅ **yes** | R5 近程已落地者維持；殘留庫內項可續；≠解凍 |
| 6 | `reports/augur_prediction_model_improvement_plan_20260707.md` | 決策層「要不要更強模型」 | **是**（庫內重訓／經濟終關） | ✅ **yes** | 僅庫內挑戰者／deflation／#14；禁「最精準」假兆框 |
| 7 | `reports/augur_prediction_revalidation_harness_plan_20260708.md` | 再驗證 harness／判停 | **是** | ✅ **yes** | 凍結快照／庫內 ledger 即可 |
| 8 | `reports/augur_prediction_validation_master_plan_20260711.md` | 驗證總綱；明文 FREEZE／零新資料 | **是** | ✅ **yes** | 與正交定義同構；仍否挪門柱／假確立 |
| 9 | `reports/augur_prediction_short_horizon_model_plan_20260709.md` | HANDOFF 曾標待拍板；FREEZE 綁快照 | **是** | ✅ **yes**（史料） | 結案釐清已建議結案（`augur_short_horizon_plan_closure_20260711.md`）；追溯肯定「本可不因 API 擋」 |
| 10 | `reports/taiwan_alpha_improvement_plan_20260717.md` | 資料維度最高；部分工項需 FinMind 補季 | **部分是** | ✅ **yes（預測／組合／方法軸之庫內段）** | **拆分**：相對強度訓練／econ／recipe 等庫內＝yes；**D1 BS 缺季補抓等＝仍 API 門**（見 B） |
| 11 | `reports/augur_direction_live_arena_plan_20260711.md` | 文首待拍板（後已開賽） | **是**（真未來預測帳本） | ✅ **yes**（肯定庫內／真未來預測側） | 開賽後續 settle／scoreboard 不需 FinMind 解凍；確立級仍唯門二；≠解凍取數 |
| 12 | `reports/augur_arena_threelens_candidate_plan_20260712.md` | 待拍板後動工 | **是**（arena 候選預測） | ✅ **yes** | 庫內特徵＋真未來出手；仍否在凍結史上重開 v3 調參 |
| 13 | `reports/augur_oracle_direction_v2_revival_plan_20260711.md` | 待拍板；敘事「解凍後樣本長大」 | **是**（方向軸庫內二次實驗） | ✅ **yes（庫內可跑段）** | 可用庫內 raw／features 做預註冊實驗；**仍否**：假稱需 FinMind 才能拍板；**仍否**違反既有 no-v3／門柱；經濟不可交易邊界不變 |
| 14 | `reports/augur_philosophy_market_evolution_loop_plan_20260724.md` | 已 `PME-P-yes`…＋`FZ-keep`；S2「新 raw→等解凍」 | **是**（強化預測閉環） | ✅ **再確認 yes**（已拍） | 零 API／既有 `feature_values` 重算＝yes；**新 raw／新 panel 需 API＝仍 API 門** |
| 15 | R5 預測隔離／predict ping（`audits/ROADMAP-R5-*`、`reports/augur_roadmap_r5_plan_20260724.md`） | 近程已 DONE；曾與 API 凍結並敘 | **是** | ✅ **再確認 yes**（已執行） | 凍結維持；≠確立級 |
| 16 | `reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.8／近程句「拍板／開 prodset→熱路徑」 | 活躍產品計畫待拍板敘事 | **預測熱路徑列＝是** | ✅ **熱路徑列追溯 yes**（見 #1） | 路線圖其餘 API／10-14／HAR-ext **不**因本檔假關 |

---

## B. 仍 API 門（不屬預測／真需外部取數 — **不**假追溯 yes）

| # | path／標的 | 原先卡關理由 | 屬預測／庫內切分？ | 登錄 | 說明 |
|---|---|---|---|---|---|
| 1 | `reports/augur_dividend_rebuild_20260724.md` · G-DIV-1 | Dividend roster／窄窗 audit 需 FinMind | **否**（取數補洞） | **仍 API 門** | PAUSED；解凍＋明示後 resume；不得假稱缺股已滿 |
| 2 | `reports/augur_roadmap_r4_data_foundation_20260724.md` · 資料地基 API 段 | 全量 catalog／attestation e2e | **否**（地基取數） | **仍 API 門** | 庫內 `db_only` 段已另閉；API 洞另帳 |
| 3 | `audits/ROADMAP-DATA-FOUNDATION-DB-ONLY-20260724.md` 所列 API 洞 | Dividend resume／正典 audit·heal／全量 catalog | **否** | **仍 API 門** | 與預測正交；不解凍 |
| 4 | FRED 新 series／`macro` 未接特徵之**新抓** | 需 FRED API | **否**（取數） | **仍 API 門** | 既有庫內 FRED 列之本地特徵實驗＝可走 A；**新拉 series＝門** |
| 5 | Alpha 計畫 **D1 BS 缺季／放量補財報** 等 | 需 FinMind 放量 | **否**（取數） | **仍 API 門** | 見 A#10 拆分 |
| 6 | 任何 `sync`／`probe`／`daily_maintenance` audit·heal／放量 | 凍結禁止 | **否** | **仍 API 門** | `finmind-fred-api-freeze.mdc` |

---

## C. 特別登錄：P2H（prodset→預測熱路徑）

| 項 | 內容 |
|---|---|
| 計畫 | `reports/augur_prodset_predict_hotpath_plan_20260724.md` |
| 正式拍板 | Steward「**回拍板碼**」→ `audits/P2H-PLAN-APPROVED-20260724.md`（2026-07-24） |
| 追溯碼 | **`P2H-P-yes`＋`P2H-E123`＋`FC-empty`＋`FZ-keep`** |
| 意義 | 採納藍圖；近程 S1–S3（含 predict）**授權**；空 active→fail-closed；凍結維持、接 prodset≠解凍 |
| Gap | `G-PME-HOTPATH` 仍 **open**（執行未開工前不假 none）；帳本見 `reports/augur_pme_gap_ledger_20260724.md` |
| 本輪 | **計畫已拍板／執行未開**；實作須另句「**開 prodset 熱路徑**」 |

---

## D. 交叉一句

**凍結仍凍取數；預測拍板／庫內執行不因凍結否決；追溯 yes ≠ 解凍 ≠ 確立級／可交易。**
