---
status: executed
series: local_ai_kh
kind: kh8_a2_l3
date: 2026-08-13
viewpoint: 2026-08-13T10:20+08:00
go: audits/KH8-DISCRIM-A2-L3-GO-20260813.md
fired: audits/KH8-DISCRIM-A2-L3-FIRED-20260813.md
script: scripts/kh8_a2_l3_apply.py
log: /tmp/kh8-a2-l3/
apply_json: /tmp/kh8-a2-l3/apply.json
rollback_sql: /tmp/kh8-a2-l3/rollback.sql
run_id: "kh8:a2-l3:20260813"
paste: "KH8-DISCRIM-A2-L3-EXECUTED | wrote=146399 | latest=A2-v1 | disc.ok=False | E-keep | stop-at-7 | no-fake-depth8 | no-relax-θ"
self_reported: true
layer: "[I]"
---

# EXECUTED｜KH8-DISCRIM-A2-L3 · 主表寫入 A2-v1

> **雙明示**：Steward paste＋`A2-L3-GO`。  
> **寫入** 146,399 列（`run_id=kh8:a2-l3:20260813`）· **DEFAULT_FORMULA 仍 legacy** · **θ 未動** · **E-keep／stop-at-7** · **≠ depth≥8**。

## 結果

| 尺 | 值 |
|---|---|
| wrote | **146,399** · RC=0 |
| latest／item formula | **全 A2-v1** |
| latest bands | medium **143037** · high **2966** · absent 385 · low 11 |
| latest minority | **≈0.0230** ≪ 0.05 |
| `population_discriminates.ok` | **False**（判準 2′：分量質量仍不足；全表 n 含舊＋新列，band 質量不可當綠） |
| evidence `--selftest` | **PASS** |
| matrix `--offline` | **PASS** |
| A2B3 watcher | **仍 ALIVE**（未殺） |

## 回滾（已備）

```sql
DELETE FROM knowhow_evidence_weight WHERE run_id = 'kh8:a2-l3:20260813';
```

檔：`/tmp/kh8-a2-l3/rollback.sql` · 或 `python scripts/kh8_a2_l3_apply.py --rollback`

## 誠實結論

1. 主表**消費側最新列**已是 A2-v1（打破 high 牆 → 多落 medium）。  
2. **母體鑑別力仍不過門** → **禁止**撤 E、**禁止**宣稱 depth≥8／KH8 進化成功。  
3. 未放寬 θ；未切碼默認 `DEFAULT_FORMULA`；未 MERGE。

## 未做／下句

- 撤 E · depth8 · relax-θ · MERGE／M3 匯合 · L5  
- 若要回滾：上列 SQL／`--rollback`

*完。*
