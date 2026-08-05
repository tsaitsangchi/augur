---
status: draft
series: s3_features
depends_on:
  - audits/S3-WAVE-B-EXECUTED-20260804.md
  - reports/augur_s3_wave_e_gated_residual_plan_20260805.md
---

# S3 殘帳 β — Wave-B 截面候選後續假說 plan-first（2026-08-05）

> **性質**：[I] plan-first（憲章第六部；CLAUDE #20）。**禁止**重跑同一四候選、同一 verify 口徑假裝「再試一次就過」。  
> **觸發**：Wave-B 0/4 提拔（`pb_self_pctile_252d` 過 HAC 但多 seed Δ≤0；其餘 IC／Δ 皆負）。  
> **self-reported（#32a）**。

---

## 0. 一句話

**四候選已誠實判死於「當前定義＋當前生產集增量」；下一手只能是換假說／換變換／換對照臂，不是重跑同一把尺。**

---

## 1. 已結案事實（不重做）

| 候選 | HAC 篩 | 多 seed Δ | 狀態 |
|---|---|---|---|
| `pb_xsec_rank` | 未過 | ≈−0.04 | staged 保留 |
| `pb_industry_demean` | 未過 | ≈−0.04 | staged 保留 |
| `pb_self_pctile_252d` | **過** | ≈0 微負 | staged（訊號有、增量無） |
| `inst_govbank_divergence` | 未過 | ≈0 微負 | staged；覆蓋較短 |

SSOT＝`audits/S3-WAVE-B-EXECUTED-20260804.md` §3。

---

## 2. 可選假說軌（擇一授權，勿一次全開）

| 軌 | 假說 | 要做什麼 | 不做什麼 |
|---|---|---|---|
| **β1 符號翻轉／空頭邊** | PB 類因子在台股為反轉 | 對 `pb_*` 取負向再跑 IC＋提拔尺 | 不改門檻遷就正號 |
| **β2 交互合成** | `pb_self_pctile`×流動性／規模 | 新候選名（新列）；先 IC 再 #11 | 不把舊四名「改參數」當新特徵 |
| **β3 換 horizon 臂** | H20／H120 與 H60 異質 | 僅對**已過 HAC 者**（現僅 self_pctile）加臂 | 不對已劣化兩名浪費 CPU |
| **β4 退役 staged** | 四名已無研究價值 | `DELETE`／標記 retired＋帳 | 須明示；非預設 |
| **β5 停** | 特徵面暫停 | 只留 KEEP／staged | — |

**推薦預設**：**β5 停**或 **β2 窄做一顆交互**（若要動碼）；**禁 β＝重跑四名 verify**。

> **執行追記（2026-08-05）**：Steward `S3-BETA-beta2 | FZ/GATE-keep | skip-sync | no-SIM-apply` → 材料化＋IC 見 `audits/S3-BETA-BETA2-EXECUTED-20260805.md`（partial；#11 in-flight at archive）。

---

## 3. (a)(b) schema／程式

| 軌 | schema | python |
|---|---|---|
| β1–β3 | 既有 `feature_candidate_values`（新 feature 名） | 既有 `validate_feature_candidates`／`verify_candidate_promotion`；新變換函式若有則進既有 builder |
| β4 | 候選表列處置 | 一次性 script＋audit |
| 新表 | **無**（除非交互要獨立表——不建議） |

---

## 4. 分階段

| 階段 | Gate | 另授權？ |
|---|---|---|
| **Phase 0（本檔）** | Steward 選 β1–β5 | 本檔呈裁 |
| **Phase 1** | 若選 β1–β3：單一假說 materialize＋IC；過才 #11 | 是 |
| **晉升** | 仍走既有提拔閘；禁自動 prodset | 是 |

---

## 5. 硬邊界

- FZ/GATE-keep · skip-sync · no-SIM-apply  
- 不因「只差一點」放寬 HAC／Δ 門檻  
- 與 S3-E gated-keep 正交（本檔＝組 8 殘帳，非組 14–16）

---

## 6. 請 Steward 裁示

1. **beta5_stop** — 特徵殘帳暫停（推薦若要專心 S4-B 0b／他題）  
2. **beta2_one_interaction** — 只做一顆 `pb_self_pctile`×控制變數交互 plan→build  
3. **beta1_sign_flip** — PB 族負向再測  
4. **beta3_h20_arm** — 僅 self_pctile 加 H20 臂  
5. **beta4_retire** — 退役四 staged 名  

---

*定版（2026-08-05）。*
