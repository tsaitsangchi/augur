# ADM-AI-ASSIST S2 CLOSED（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward「所有 working 開始跑」＝S2→S3；**硬禁** AI／timer approve／activate  
> **拍板基線**：`audits/ADM-AI-ASSIST-PLAN-APPROVED-20260728.md`＋`FZ-keep`  
> **計畫**：`reports/augur_ai_admission_assist_plan_20260728.md` §5 S2  
> **不含**：人裁抽核閾值入憲；S3 timer（見 `ADM-AI-ASSIST-S3-CLOSED-20260729.md`）；FinMind／FRED

## 一、先前回溯（有界 apply 曾失敗）

| 根因 | 處置 |
|---|---|
| `knowledge_source_review_log.action` CHECK **未含** `'assist'` → INSERT audit 撞約束 | S1 migrate DDL 已擴 CHECK（含 `assist`／`ratify`）；本輪 `--check`＝`review_log_action_check_has_assist=True` |

## 二、做了什麼

| 項 | 狀態 | 摘要 |
|---|---|---|
| **有界 `--apply`** | ✅ | `--apply --limit 3 --no-llm` → 寫 **assist=6**、**source_audit=6**（source×3＋staging×3） |
| **審批態零變** | ✅ | apply 前後 `approval_status` diff＝**0**；`assist` 列 `old_status≡new_status` |
| **`/gov` 唯讀建議列** | ✅ | `serve_admin_console.py` 已渲染「AI 預審建議」表（最新 target／score／flags／reason）；web **零寫**升級 |
| **硬禁** | ✅ | `--selftest` 綠；`actor=local_ai_v1` 且 `action∈{approve,activate}`＝**0** |
| **FZ-keep** | ✅ | 零市場 API |

## 三、真兆數字（2026-07-29 本輪）

| 指標 | 值 |
|---|---|
| proposed／pending_staging | **3504**／**18722** |
| `knowledge_admission_assist` 列（累計） | **26** |
| `review_log` action=`assist`（累計） | **26** |
| assist 導致 status 突變 | **0** |
| approval 分佈 | active=96 · approved=3 · proposed=3504 · suspended=1（apply 後不變） |
| 本輪 apply 樣本 score／model | 0.450／`heuristic`（`--no-llm`） |

### 本輪 apply 樣本（限 3／池）

| kind | target_id | score | model |
|---|---|---|---|
| source | aozora_books | 0.450 | heuristic |
| source | base_bielefeld | 0.450 | heuristic |
| source | biorxiv_details | 0.450 | heuristic |
| staging | 342756 | 0.450 | heuristic |
| staging | 342757 | 0.450 | heuristic |
| staging | 342758 | 0.450 | heuristic |

## 四、如何重跑（仍禁升級）

```bash
./venv/bin/python scripts/assist_admission_review.py --apply --limit 5
./venv/bin/python scripts/assist_admission_review.py --apply --limit 5 --no-llm   # Ollama 離線
# 人裁仍走 TTY：
python scripts/review_knowledge_source.py --approve KEY --actor NAME
```

`/gov`：登入 admin 後開「來源治權」→「AI 預審建議（唯讀）」。

## 五、變更／相依

- `scripts/assist_admission_review.py` — `--apply` 寫 assist＋`action='assist'` audit（`old=new`）  
- `scripts/serve_admin_console.py` — `/gov` 唯讀建議列（既有）  
- `scripts/migrate_admission_assist_ddl.py` — review_log CHECK 含 `assist`（既有）  
- 本 CLOSED  

## 六、下一步

見 **S3 CLOSED**（timer；預設 dry-run）。
