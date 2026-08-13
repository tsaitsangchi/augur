---
title: 本地 AI·KH——逐步執行最佳下一步（獨立選刀 SSOT）
status: final
series: kh_optimization_plan
date: 2026-08-12
viewpoint: 2026-08-12T13:11+08:00
layer: "[I]"
role: **KH 專案唯一選刀 SSOT**——與市場 tip／B3／hold-#1 **完全分軌**；不互為主軸／不互等
ssot_code: KH-OPT-STEPWISE-20260812
parent_evolve: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
trigger_plan: reports/augur_kh_ingest_driven_trigger_plan_b_20260812.md
split_from_market: audits/KH-SPLIT-FROM-MARKET-AXIS-ADOPTED-20260812.md
market_nav_orthogonal: reports/augur_opt_stepwise_best_next_plan_r14_20260811.md
note: 市場板不再編排 KH；本檔不出現「候 tip／讓 B3／∥市場主軸」為開工條件
self_reported: true
---

# 本地 AI·KH——逐步執行最佳下一步（2026-08-12）

> **一句**：KH 閉環自我進化的**全部開問題／最佳下一步**只在本檔與 KH readout／ingest-B 選刀；**與市場主軸無關**。  
> **不是**：等 PriceAdj、讓收盤 B3 才准開 KH、把 KH 當市場 #1 的附屬 ∥。  
> **基礎設施**：`augur_llm.lock` 為共用互斥（誰先搶誰跑）——**不構成**市場對 KH 的指揮關係。

---

## §0 協議

```text
問「KH 下一步」→ 只開本檔 §1（或 readout §4／ingest S*）
問「市場下一步」→ 只開 r14 市場板（本檔不答 tip／B3）
禁：用 hold-#1／PriceAdj 擋 KH；用 KH 進度擋／催 B3
```

**Hard doors（KH only）**：

```text
FZ/GATE-keep(知識) | T0 no-web-dialog-approve | T2-system-ok
| PDF-C-no-ASR | ASR=owned_local+local_private only
| no-KH10 | KH8-prod-stop-at-7 | ingest S0-S9 | apply=opt-in
| no-calendar-fake-evolve | no-default-timer | AUTO-LIFT-ops-resident（碼預設仍 off）
```

---

## §1 開問題板

| # | 問題 | 最佳下一步 | 狀態 |
|---|---|---|---|
| **K0** | D-Data／S0 breach | `kh_ingest_trigger --check`；FIRE→選開 `--apply` | 🟢 LIVE 0 |
| **K1** | S3 concordance lag | 同上（limit=5000） | 🟢 LIVE 0 |
| **K2** | ingest 階梯 A→B→C | 已收口；守 apply 選開 | 🟢 |
| **K3** | AUTO-LIFT 試點→常駐 | systemd 常駐旗 ✅；碼預設仍 off | 🟢 `AUTO-LIFT-RESIDENT-EXECUTED` |
| **K4** | 私有／ASR smoke | `kh_private_smoke.py` | 🟢 |
| **K5** | Writer／doc 殘渣 | Doc1 純圖 hold；鎖檔忽略 | 🟢 `KH-K5-DOC-RESIDUAL-EXECUTED` |
| **K6** | ASR via／對聽 | 可選 | 🟢 抽樣 |
| **K7** | 錨題 live／逐步口吻 | 產品：8b＋960；步驟題 4b→8b | 🟢 `KH-K7-PRODUCT-8B-EXECUTED` |
| **K13** | 檔名.ext＋問句／(無回覆) | 通則已入 evolve v3；碼已硬化 | 🟢 `KH-EVOLVE-EXT-ASK-NO-EMPTY-ADOPTED` |
| **K14** | 問法回歸矩陣 | `scripts/kh_query_form_matrix.py` | 🟢 `KH-QUERY-FORM-MATRIX-EXECUTED` |
| **K15** | D-FillAuto（設定填值） | 直接問 wsj02／站台 IP → 自動範例 `欄位=值` | 🟢 `KH-D-FILLAUTO-ADOPTED` |
| **K8** | KH8 discrim | plan-first；生產 stop-at-7 | ❄／🔴 |
| **K9** | 他域 FT | 另 GO | 🔴 |
| **K10** | C1 EXPAND→特徵 | **另 GO**；**非**市場日更義務；禁默加權 predict | 🔴 隔離 |
| **K11** | `.msg`／rar | 明示跳過或另 plan | 🔴 |
| **K12** | KH10 | — | 禁 |

---

## §2 現在該做什麼？（KH）

| 問 | 答（2026-08-12） |
|---|---|
| **KH 最佳下一步** | **守穩態**：`--check` → `priority_hit: ∅`（S0／S3 綠）；無強制刀 |
| **不要做** | 因 tip 停 KH；默開 AUTO-LIFT systemd；日曆假進化；ASR→PDF-C；無尺抬 KH8 |

```text
paste（KH only）:
  KH-OPT-STEPWISE | S0-S9 | no-market-axis
  | kh_ingest_trigger --check | lift-ops-resident | ext-ask+no-empty
  | kh_query_form_matrix | D-FillAuto
```

---

## §3 配套

- Evolve SSOT：`reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md`  
- 觸發：`reports/augur_kh_ingest_driven_trigger_plan_b_20260812.md`  
- 分軌帳：`audits/KH-SPLIT-FROM-MARKET-AXIS-ADOPTED-20260812.md`  

*完。[I] · KH 獨立選刀。*
