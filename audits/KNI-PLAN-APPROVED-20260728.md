# KNI-PLAN＋KNI-S01＋RKI-keep＋NHC-keep＋FZ-keep 拍板登錄（2026-07-28）

> **性質**：拍板登錄（[I]；不創設 [N]）。  
> **計畫**：`reports/augur_knowhow_nary_interaction_plan_20260728.md`  
> **hugo／Steward 對話拍板原文（逐字）**：`KNI-PLAN`＋`KNI-S01`＋`RKI-keep`＋`NHC-keep`＋`FZ-keep`  
> **簽名誠實註記**：本檔由 agent 依 Steward 拍板繕寫登錄；決策者＝hugo、繕寫者＝agent，二者分立。

## 一、五碼效力

| 碼 | 含義 | 本輪 |
|---|---|---|
| **`KNI-PLAN`** | 採納 KHⁿ（n≥3）逐步實現藍圖；相容擴充 RKI、不另造答案 SSOT | ✅ |
| **`KNI-S01`** | 開工 **S0＋S1**（schema `arity`／`axes[]`＋種子三元升格）；**不含** S2 runner／S3 評測／S4 PME 策展 | ✅ 核准並執行 |
| **`RKI-keep`** | 不推翻 RKI S01；既有二元探針／probe 繼續有效 | ✅ |
| **`NHC-keep`** | 禁三元專支／寫死答案樹；新探針＝INSERT；產生走 advise／glossary | ✅ |
| **`FZ-keep`** | FinMind／FRED 維持凍結；本輪不放量 harvest | ✅ |

## 二、S01 範圍

| 階段 | 做 | 驗收錨 |
|---|---|---|
| **S0** | 同表冪等加 `arity`／`axes`；既有列回填 `arity=2`；放寬 `interaction_kind` 含 `kh_x_kh_x_kh` | `\d`；active≥14；selftest |
| **S1** | 升格 `RKI-FP-AI-SOLAR`→正式 **arity=3**／`axes[3]`／`kh_x_kh_x_kh`（不另造平行答案列） | `--show` 可見 n=3；二元列仍在 |

## 三、非目標（明示）

| 不做 | 理由 |
|---|---|
| **`KNI-S2`** runner 多軸檢索／組答 | 未拍 → **待另令** |
| **`KNI-S3`**／**`KNI-S4`** 評測／人策展 PME 候選 | 未拍 → **待另令** |
| 自動開 **`PME-XDOM-SOLAR`** | ≠本拍；研發作答 ≠ 灌台股因子 |
| 解凍 FinMind／FRED／放量 harvest | `FZ-keep` |
| 入憲 [N] | 無 constitute 碼 |
| 刪／廢 RKI 二元種子當「升級」 | `RKI-keep` |
| hardcode 三元專答樹 | `NHC-keep` |

## 四、執行落點

- migrate：`scripts/migrate_knowhow_interaction_probe_ddl.py`（`--apply`／`--selftest`／`--show`）
- 收官：`audits/KNI-S01-CLOSED-20260728.md`
- 計畫 Steward 欄更新；HANDOFF 一句
- 封存：`bash scripts/archive_push.sh --slug kni-s01`
