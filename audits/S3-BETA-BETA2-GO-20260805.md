---
status: go
series: s3_features
depends_on:
  - reports/augur_s3_residual_wave_b_candidates_plan_20260805.md
---

# S3-BETA-beta2 GO（2026-08-05）

> **裁示**：`S3-BETA-beta2 | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **範圍**：單一新候選 `pb_pctile_x_dvlog`＝同 panel `z(pb_self_pctile_252d)×z(dollar_volume_log_20d)`；材料化＋IC；**僅當** as-of H60 HAC `|t|≥2` 才得另跑 `#11` `verify_candidate_promotion`（單名、`--keep`）。  
> **禁**：重跑舊四名 verify；自動 promote／SIM-apply；sync／解凍 API。

*登錄 2026-08-05。*
