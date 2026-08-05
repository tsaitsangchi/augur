---
status: accepted_beta5_stop
series: s3_features
depends_on:
  - reports/augur_s3_residual_wave_b_candidates_plan_20260805.md
  - audits/S3-BETA-BETA2-EXECUTED-20260805.md
  - audits/S3-BETA5-STOP-ACCEPTED-20260805.md
---

# S3 殘帳：β5 停 × β2 #11 暫停狀態 plan-first（2026-08-05）

> **性質**：[I] plan-first（波次 A · 項 5）。**零**重跑 verify／零 materialize（本檔只定錨）。  
> **父**：`reports/augur_s3_residual_wave_b_candidates_plan_20260805.md`。  
> **✅ 2026-08-05**：Steward 選 `accept_beta5_stop`（`audits/S3-BETA5-STOP-ACCEPTED-20260805.md`）。  
> **self-reported（#32a）**。

---

## 0. 一句話

**β2 交互已材料化＋IC 過門；`#11` 多 seed 被為顧聊天手動中止——不得假稱終表。特徵面預設改 β5 停；續 `#11` 須另 GO 且勿∥ 8b 聊天。**

---

## 1. 現況（真兆）

| 項 | 狀態 |
|---|---|
| `pb_pctile_x_dvlog` | 23,850 列已寫；`--keep` |
| as-of H60 IC | −0.0435／HAC-t **−2.81**（過 \|t\|≥2、方向負） |
| `#11` `verify … --seeds 3 --keep` | **KeyboardInterrupt**＠`baseline._panel_matrix`（為 Ollama／聊天騰資源） |
| 舊四名 Wave-B | **禁**重跑同一 verify |

SSOT partial＝`audits/S3-BETA-BETA2-EXECUTED-20260805.md` §6。

---

## 2. 選項（擇一）

| 代號 | 做什麼 | 何時 |
|---|---|---|
| **β5_stop**（推薦預設） | 特徵殘帳暫停；staged／β2 列保留；專心 S4／閉環／顧問 | 立即書面接受即可 |
| **β2_resume_#11** | 重掛同一 CLI；跑完回填 Δ 終表 | **另 GO**；機器空閒、**停 8b 或接受擠死** |
| **β1／β3／β4** | 見父檔 §2 | 另選、勿與 β2_resume 同開 |

---

## 3. (a)(b) schema／程式

| 選項 | schema | python |
|---|---|---|
| β5_stop | 無新表 | 無新碼；audit／本檔留痕 |
| β2_resume | 既有 `feature_candidate_values` | `scripts/verify_candidate_promotion.py --features pb_pctile_x_dvlog --h 60 --seeds 3 --keep` |

---

## 4. 硬邊界

- FZ/GATE-keep · skip-sync · no-SIM-apply  
- 不 promote／不改 HAC／Δ 門檻遷就  
- β2_resume **≠** 解凍 API  

---

## 5. 請 Steward 裁示

1. **accept_beta5_stop** — 書面接受 β5（本檔生效）  
2. **schedule_beta2_resume** — 另排 `#11` GO 句與時間窗  
3. **other_beta** — 改選父檔 β1／β3／β4  

*定版草稿（2026-08-05 波次 A）。*
