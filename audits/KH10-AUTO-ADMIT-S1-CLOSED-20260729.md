# KH10-AUTO-ADMIT-S1 CLOSED（2026-07-29）

> **性質**：[I] 收官；憲章 v1.48.0 一律准入下之漸進編排落地。  
> **計畫**：[`reports/augur_kh10_auto_admit_plan_20260729.md`](../reports/augur_kh10_auto_admit_plan_20260729.md)

## 做了什麼

| 項 | 結果 |
|---|---|
| S0.1 DDL | `knowhow_auto_admit_state`；run 加 `admit_depth_*`；gate `enabled=true`／`progressive_enabled`／`max_auto_depth=7` |
| `src/augur/knowledge/auto_admit.py` | 逐層 evaluate 0…10；8／9=skipped；單調水印；`--selftest` 綠 |
| `scripts/run_knowhow_auto_admit.py` | `--check`／`--dry-run`／`--apply-raw`／`--apply-up-to N` |
| live 煙測 | `items_with_text=157969`；`--apply-up-to 4 --limit 5` → 5 item **depth 0→4**；state buckets `{4:5}` |

## 驗收

- 庫內原文已准入；編排只抬 `admit_depth`（精準）  
- KH4 fail 會停在較淺 depth（本輪 5 件皆達 4＝eligible 路徑通）  
- 未跑 bulk activate（煙測加 `--no-activate-source`）  
- 零 FinMind／FRED；未灌 PME  

## 指令

```text
python scripts/migrate_knowhow_auto_admit_ddl.py --apply
python scripts/run_knowhow_auto_admit.py --check
python scripts/run_knowhow_auto_admit.py --dry-run --apply-up-to 4 --limit 20
python scripts/run_knowhow_auto_admit.py --apply-up-to 4 --limit 50
python scripts/run_knowhow_auto_admit.py --apply-up-to 7 --limit 20   # 至現況 max
```

## 下一步

- 有界放量 `--apply-up-to 4`／`7`（可開來源 activate）  
- S2：KH8／KH9 最小片 → 提高 `max_auto_depth`  
