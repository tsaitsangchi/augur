---
status: executed_partial
series: s3_features
depends_on:
  - audits/S3-BETA-BETA2-GO-20260805.md
  - reports/augur_s3_residual_wave_b_candidates_plan_20260805.md
---

# S3-BETA-beta2 EXECUTED（部分；2026-08-05）

> **裁示**：`S3-BETA-beta2 | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **self-reported（#32a）**；數字 (a) stdout。  
> **誠實**：封存時 `#11` `verify_candidate_promotion --features pb_pctile_x_dvlog --h 60 --seeds 3 --keep` **仍 in-flight**——**不**假稱多 seed Δ 終表已入帳。

---

## 1. 定義（落地）

| 項 | 值 |
|---|---|
| 新候選名 | `pb_pctile_x_dvlog` |
| 公式 | 同 panel `z(pb_self_pctile_252d) × z(dollar_volume_log_20d)` |
| code | `src/augur/audit/feature_candidate.py`（`_interact_z`／`CANDIDATES`＋1） |
| CLI | `scripts/run_s3_beta2_interaction.py --run` |

## 2. 材料化

| 項 | 值 |
|---|---|
| panel × core | 106 × 225 |
| 寫入列 | **23,850**（2014-12-31..2026-06-30） |
| 舊四名 | **未**重跑 verify |

## 3. IC 預篩（已完）

as-of H60：IC **−0.0435**／iid-t **−4.26**／HAC-t **−2.81**／勝率 0.36／n=104  
→ `|t|≥2` **過**（方向為**負**——訊號有、符號與裸 pctile 相反）。  
pan-hist／H20 同向負、|HAC|亦 ≥2。對照母因子 `pb_self_pctile_252d` as-of H60 仍為正。

## 4. #11 多 seed（封存時）

**in-flight**（PID 見當日 `/tmp/s3-beta2-verify.log`）。跑完後另開 EXECUTED 補表或 append 本檔——**本封存點不以記憶補 Δ**。

## 5. 邊界

- 不 promote／不 SIM-apply／不 sync  
- 候選表 `--keep` 保留  

*部分 EXECUTED 2026-08-05（封存前切片）。*
