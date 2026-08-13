---
title: 本地 AI·KH——逐步執行最佳下一步（獨立選刀 SSOT）
status: final
series: kh_optimization_plan
date: 2026-08-13
viewpoint: 2026-08-13T11:49+08:00
layer: "[I]"
role: KH **長板**（與市場 tip／B3 **分軌**；開工順序以全專案逐步執行 SSOT 為準）
parent_exec: reports/augur_opt_stepwise_all_problems_r15_20260813.md
ssot_code: KH-OPT-STEPWISE-20260813
parent_evolve: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
trigger_plan: reports/augur_kh_ingest_driven_trigger_plan_b_20260812.md
split_from_market: audits/KH-SPLIT-FROM-MARKET-AXIS-ADOPTED-20260812.md
market_nav_orthogonal: reports/augur_opt_stepwise_best_next_plan_r15_20260813.md
supersedes_as_exec_nav:
  - reports/augur_kh_opt_stepwise_best_next_plan_20260812.md
prior_ack: audits/KH-OPT-STEPWISE-ACK-20260813.md
self_reported: true
---

# 本地 AI·KH——逐步執行最佳下一步（2026-08-13）

> **一句**：KH 閉環長板。  
> **後續優化開工**＝`reports/augur_opt_stepwise_all_problems_r15_20260813.md`。  
> **不是**：等 PriceAdj、讓收盤 B3 才准開 KH。  
> **基礎設施**：`augur_llm.lock` 為共用互斥——**不構成**市場指揮 KH。

---

## §0 協議

```text
問「KH 下一步」→ 只開本檔 §1（或 evolve readout／ingest S*）
問「市場下一步」→ 只開 r15 市場板（本檔不答 tip／B3）
禁：用 hold-#1／PriceAdj 擋 KH；用 KH 進度擋／催 B3
```

**Hard doors（KH only）**：

```text
FZ/GATE-keep(知識) | T0 no-web-dialog-approve | T2-system-ok
| PDF-C-no-ASR | ASR=owned_local+local_private only
| no-KH10 | KH8-prod-stop-at-7 | E-keep-until-θ
| no-relax-θ | no-fake-depth8 | ingest S0-S9 | apply=opt-in
| no-calendar-fake-evolve | AUTO-LIFT-ops-resident（碼預設仍 off；禁抬>KH2）
| 有 item 引文禁假「無此內容」 | 空包不進化
```

---

## §1 開問題板

| # | 問題 | 最佳下一步 | 狀態 |
|---|---|---|---|
| **K0** | D-Data／S0 breach | `kh_ingest_trigger --check`；FIRE→選開 `--apply` | 🟢 LIVE 0（0813 apply 後） |
| **K1** | S3 concordance lag | 同上 | 🟢 LIVE 0 |
| **K2** | ingest 階梯 A→B→C | 已收口；守 apply 選開 | 🟢 |
| **K3** | AUTO-LIFT 試點→常駐 | systemd 常駐；碼預設 off；**未**授 >KH2 | 🟢 |
| **K4** | 私有／ASR smoke | `kh_private_smoke.py` | 🟢 |
| **K5** | Writer／doc 殘渣 | Doc1 純圖 hold；鎖檔忽略 | 🟢 hold |
| **K6** | ASR via／對聽 | 可選抽樣 | 🟢 |
| **K7** | 錨題 live／逐步口吻 | 產品：8b＋960；步驟題 4b→8b | 🟢 |
| **K13** | 檔名.ext＋問句／(無回覆) | evolve v3 已硬化 | 🟢 |
| **K14** | 問法回歸矩陣 | `kh_query_form_matrix.py` | 🟢 |
| **K15** | D-FillAuto | 欄位=值機器閘 | 🟢 |
| **K16** | 假 decline（有引文仍「無此內容」） | `ensure_cite_backed_response`；Genero TP3x `1818824` 補答 | 🟢 碼已跑／**未 commit** |
| **K8** | KH8 discrim | A2-L3 已寫；ok=False → **E-keep／stop-at-7** | ❄／🔴 禁放寬 θ、禁假 depth8 |
| **K9** | 他域 FT | plan-first 已登記；**另 adopt 才訓**；首隊建議 C=`quant_finance` | 🔴 plan-only |
| **K10** | C1 EXPAND→特徵 | **另 GO**；禁默加權 predict；非市場日更義務 | 🔴 隔離 |
| **K11** | `.msg`／rar | 明示跳過或另 plan | 🔴 skip-hold |
| **K12** | KH10 | — | 禁 |
| **K17** | 假 decline 閘入倉＋8399 回歸套 | commit／push 另句；持續盯同類標題題 | 🟡 |

---

## §2 現在該做什麼？（KH）

| 問 | 答（2026-08-13 11:49） |
|---|---|
| **KH 最佳下一步** | **守穩態**：`--check` → `priority_hit: ∅`；K16 閘保持載入；**不**開 K9／K8／K10 |
| **有人貼檔名卻「無此內容」** | 先查 item／readout／是否登入；有 cite 則走摘錄閘（已修 TP3x）——**禁**當缺件整庫回填 |
| **不要做** | 因 tip 停 KH；默開抬層；日曆假進化；ASR→PDF-C；無尺抬 KH8；放寬 θ；對話 approve 來源 |

```text
paste（KH only）:
  KH-OPT-STEPWISE-20260813 | S0=0 | S3=0 | A2-L3-done | E-keep | stop-at-7
  | no-fake-depth8 | no-relax-θ | T0-keep | AUTO-LIFT=resident-only
  | false-decline-gate | no-K9-train | no-market-axis
```

---

## §3 配套

- Evolve SSOT：`reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md`  
- 觸發：`reports/augur_kh_ingest_driven_trigger_plan_b_20260812.md`  
- 分軌帳：`audits/KH-SPLIT-FROM-MARKET-AXIS-ADOPTED-20260812.md`  
- 理解／人話：r15 成對檔  
- 硬門卡：`audits/KH-HARD-GATE-CARD-20260813.md`  

*完。[I] · KH 獨立選刀 · 20260813。*
