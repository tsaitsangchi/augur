# RKI-PLAN＋RKI-SCOPE-ALL-KH＋RKI-S01 拍板登錄（2026-07-28）

> **性質**：拍板登錄（[I]；不創設 [N]）。  
> **計畫**：`reports/augur_raw_knowhow_interaction_probe_plan_20260728.md`  
> **hugo／Steward 對話拍板原文（逐字）**：`RKI-PLAN`＋`RKI-SCOPE-ALL-KH`＋`RKI-S01`＋`FZ-keep`＋`NHC-keep`  
> **同日追加（原文）**：  
> 1. 「AI模型進化 × 投資預測模型進化也加入此專案」  
> 2. 「例如依第一性原理來強化AI 模型自我迭代再進化」  
> 3. 「例如依第一性原理來強化投資模擬預測模型自我迭代再進化」  
> 4. 「AI模型進化來強化太陽能材料研發技術」  
> **簽名誠實註記**：本檔由 agent 依 Steward 拍板繕寫登錄；決策者＝hugo、繕寫者＝agent，二者分立。

## 一、五碼效力

| 碼 | 含義 | 本輪 |
|---|---|---|
| **`RKI-PLAN`** | 採納 raw↔know-how 交互核心探針藍圖 | ✅ |
| **`RKI-SCOPE-ALL-KH`** | 方法論＝所有 know-how×所有 know-how；實作＝DB 探針列＋種子 | ✅ |
| **`RKI-S01`** | 開工 **S0＋S1**（盤點＋DDL＋種子）；**不含** S2 runner／S3 PME 灌因子 | ✅ 核准並執行 |
| **`FZ-keep`** | FinMind／FRED 維持凍結 | ✅ |
| **`NHC-keep`** | 禁領域 hardcode；產生走統一 advise／glossary；擴題＝INSERT | ✅ |

## 二、同日追加效力（仍在 RKI 探針層）

| 追加 | 落點種子 | 效力邊界 |
|---|---|---|
| AI×投資預測模型進化 | `RKI-AI-PREDICT-EVO`／`RKI-AI-PREDICT-EVAL` | 探針帳＋S0 對照；**≠** `PME-XDOM-AI-PREDICT` |
| 第一性×AI 自我迭代 | `RKI-FP-AI-ITER`（＋optional `RKI-FP-AI-PREDICT`） | NHC-keep；禁專答樹 |
| 第一性×投資模擬／預測迭代 | `RKI-FP-PREDICT-ITER` | PME／arena 僅檢索軸；答案不寫死 |
| AI×太陽能材料研發 | `RKI-AI-SOLAR-RD`（＋optional `RKI-FP-AI-SOLAR`） | 顧問／研發交互；**≠** `PME-XDOM-SOLAR`；與 AI×預測正交 |

> **另需拍板**：若要獨立異域進化灌因子閉環，開 `PME-XDOM-AI-PREDICT`／`PME-XDOM-SOLAR`（或等價碼）——**本輪未拍＝不做**。

## 三、S01 範圍

| 階段 | 做 | 驗收錨 |
|---|---|---|
| **S0** | 庫內 consumable 盤點＋種子命中診斷（含 AI／PME 物件） | `reports/augur_rki_s0_inventory_20260728.md` |
| **S1** | `knowhow_interaction_probe` DDL＋種子（含同日追加→**14**）；migrate 矩陣／selftest | `\d`＋active≥14；無專支 |

## 四、非目標

| 不做 | 理由 |
|---|---|
| S2 runner 全量報告 | 未拍 `RKI-S2` |
| S3／PME 人候選灌因子 | 未拍 `RKI-S3`；近程 PME-XDOM 仍僅 `SUNZI-MGMT` |
| `PME-XDOM-AI-PREDICT`／`PME-XDOM-SOLAR` | 另碼 |
| 解凍 FinMind／FRED | `FZ-keep` |
| 入憲 [N] | 無 constitute 碼 |
| hardcode「第一性強化 AI／預測迭代」答案 | `NHC-keep` |

## 五、執行落點

- 收官：`audits/RKI-S01-CLOSED-20260728.md`
- HANDOFF 一句
- 封存：`bash scripts/archive_push.sh --slug rki-s01`
