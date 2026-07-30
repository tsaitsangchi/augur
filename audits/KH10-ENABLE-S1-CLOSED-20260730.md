# KH10-ENABLE-S1 CLOSED（2026-07-30）

> **拍板**：`audits/EVO-S4-KH10-S1-APPROVED-20260730.md`（`KH10-ENABLE-S1`＋`FZ-keep`）  
> **計畫**：`reports/augur_kh10_enable_plan_20260729.md` §6-S1

## 交付

| 檔 | 角色 |
|---|---|
| `src/augur/knowledge/evolution.py` | insert／governance；`decided_by` 硬鎖 HUMAN |
| `scripts/collect_evolution_candidates.py` | KH7 pass／KH6 probe／KH9 高分 → candidate |
| `scripts/review_evolution_candidates.py` | `--list`／`--submit`／`--approve|reject|defer|kill`；mutate **須 TTY** |

## 實測

- 三支 `--selftest` 全綠  
- `--apply --pending`：inserted **kh7=14／kh6=9／kh9=20**（skip=0）→ `governance_pending=43`  
- `--list` 可見佇列；ledger 仍空（等人裁）  
- 無 `--auto-approve`；管道非 TTY 裁決會拒  

## 明確未做（S2／紅線）

- `apply_evolution_feedback.py`（S2）  
- 自動寫 philosophy／prodset APPLY  
- AI 代裁  

## 人裁用法

```bash
venv/bin/python scripts/review_evolution_candidates.py --list
venv/bin/python scripts/review_evolution_candidates.py --approve ID --rationale '...'
venv/bin/python scripts/review_evolution_candidates.py --reject ID --rationale '...'
```
