# NHC-PLAN＋NHC-S12 拍板登錄（2026-07-28）

> **性質**：拍板登錄（[I]；不創設 [N]）。  
> **計畫**：`reports/augur_no_hardcode_db_ssot_constitution_plan_20260728.md`  
> **hugo／Steward 對話拍板原文（逐字）**：`NHC-PLAN`＋`NHC-S12`＋`FZ-keep`  
> **本輪無** `NHC-CONSTITUTE` → **禁止改憲章 [N] 正文**。  
> **簽名誠實註記**：本檔由 agent 依 Steward 拍板繕寫登錄；決策者＝hugo、繕寫者＝agent，二者分立。

## 一、三碼效力

| 碼 | 含義 | 本輪 |
|---|---|---|
| **`NHC-PLAN`** | 採納禁 hardcode／策展映射住 PG（含 know-how 產生軸、A0 探針） | ✅ |
| **`NHC-S12`** | 開工 **S1＋S2**（`retrieve_glossary` DDL＋種子＋`query_translation` 讀表） | ✅ 核准並執行 |
| **`FZ-keep`** | FinMind／FRED 維持凍結 | ✅ |
| **`NHC-CONSTITUTE`** | 入憲寫 [N] | ❌ **未拍** → 不改 META／大憲章義務條文 |
| **`NHC-S3`** | 其餘 A 類 hardcode 遷徙 | ✅ **已開跑／CLOSED**（2026-07-29；見 `audits/NHC-S3-CLOSED-20260729.md`） |

## 二、S12 範圍

| 階段 | 做 | 驗收錨 |
|---|---|---|
| **S1** | `retrieve_glossary` 建表＋13 列漿料／光伏種子（`漿料.require_cooccur=true`） | `\d`＋`count(*)=13` |
| **S2** | `query_translation` 改讀表；刪 runtime `_GLOSSARY` SSOT；selftest fixture 零 IO | 漿料組句等價；裸漿料→None；A0 無領域專支 |

## 三、A0 驗收探針（know-how 產生＝通用路徑；禁 hardcode）

| ID | 探針句 | 期望行為 |
|---|---|---|
| **A0-app** | 第一性原理在太陽能材料研發如何應用？ | 統一 `advise`／翻譯；不崩；可答或誠實缺料 |
| **A0-core** | 依第一性原理列出在太陽能材料研發技術核心？ | 同上；禁寫死技術核心清單 |
| **A0-phys** | 依第一性原理列出在太陽能材料研發物理學技術核心？ | 同上；禁物理學專支 |
| **A0-chem** | 依第一性原理列出在太陽能材料研發在化學上技術核心？ | 同上；禁化學專支 |

> **定錨**：化學／物理／材料／應用變體皆**同一通用產生路徑**（跨域檢索＋LLM 組答＋DB 語料／原則／glossary）；差在檢索命中的庫內列，**不靠** `if-domain`／寫死 Q&A。深度不足 → 誠實缺料；補洞＝`INSERT retrieve_glossary` 或知識管線／FT-COV，**零改碼專支**。  
> **≠** 開通 `PME-XDOM-SOLAR`（異域進化仍僅已拍 `SUNZI-MGMT`）。

## 四、非目標

| 不做 | 理由 |
|---|---|
| 改憲章 [N] | 無 `NHC-CONSTITUTE` |
| S3 其餘 hardcode | ✅ CLOSED（`audits/NHC-S3-CLOSED-20260729.md`） |
| 解凍 FinMind／FRED | `FZ-keep` |
| 為 A0 加領域 hardcode | V-A0／V-GEN |
| 開 `PME-XDOM-SOLAR` | 產生 ≠ 進化灌因子 |

## 五、執行落點

- 收官：`audits/NHC-S12-CLOSED-20260728.md`
- HANDOFF 一句
- 封存：`bash scripts/archive_push.sh --slug nhc-s12-retrieve-glossary`
