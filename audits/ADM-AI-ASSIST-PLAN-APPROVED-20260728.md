# ADM-AI-ASSIST-PLAN＋FZ-keep 拍板登錄（2026-07-28）

> **性質**：拍板登錄（[I]；不創設 [N]）。  
> **計畫**：`reports/augur_ai_admission_assist_plan_20260728.md`  
> **hugo／Steward 對話拍板原文（逐字）**：`ADM-AI-ASSIST-PLAN`  
> **簽名誠實註記**：本檔由 agent 依 Steward 拍板繕寫登錄；決策者＝hugo、繕寫者＝agent，二者分立。

## 一、效力

| 碼／項 | 含義 | 本輪 |
|---|---|---|
| **`ADM-AI-ASSIST-PLAN`** | 採納三層：L1 機械 → L2 本地 LLM 建議（score＋reason＋audit）→ L3 唯人 approve／activate | ✅ |
| **近程執行** | 開 **S0–S1**（DDL＋預審 script；**預設 dry-run**） | ✅ 核准並執行 |
| **硬禁** | AI／timer **不得**執行 approve／activate | ✅ |
| **`FZ-keep`**（預設同掛） | 零市場 API；Ollama 用本地 4b／既有慣例 | ✅ |

## 二、S0 定案（schema）

**選項 C**：新表 `knowledge_admission_assist`（`target_kind∈{source,staging}`、score／reason／flags、`actor=local_ai_v1`）——多輪冪等、不污染 `approval_status`／staging `status`；SRC-AUTO L-A／L-V 合併同一 writer。

| 不做（本拍） | 理由 |
|---|---|
| S2 有界 `--apply` 抽核／gov 唯讀建議列 | 未拍 → **待另令** |
| S3 timer＋人裁工作流 | 未拍 → **待另令** |
| AI／timer 觸發 approve／activate | **硬禁** |
| 解凍 FinMind／FRED | `FZ-keep` |
| 入憲 [N]／把 assist_score 寫進 admission_gate | 明示非目標 |

## 三、執行落點

- migrate：`scripts/migrate_admission_assist_ddl.py`
- 預審：`scripts/assist_admission_review.py`（預設零寫；`--selftest`／`--dry-run`）
- 收官：`audits/ADM-AI-ASSIST-S01-CLOSED-20260728.md`
- 封存：`bash scripts/archive_push.sh --slug adm-ai-assist-s01`
