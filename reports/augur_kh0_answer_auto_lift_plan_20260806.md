---
title: KH0-ANSWER-AUTO-LIFT｜答對自動抬層至 KH1／KH2 計畫
status: plan_first
series: kh_loop_evolve
open_problem: "#1c"
date: 2026-08-06
viewpoint: 2026-08-06T10:14+08:00
layer: "[I]"
role: 本地 AI KH 自進化現主軸（答對→自動抬 admit）；≠來源放行
axis_adopted: audits/KH-AXIS-1c-AUTO-LIFT-ADOPTED-20260806.md
doctrine: audits/KH0-ANSWER-AUTO-LIFT-DOCTRINE-20260806.md
parent: archive/slim-t2/augur_local_ai_kh_loop_evolve_opt_plan_20260806.md
ruler_intent: R-hybrid
ruler_status: adopted
ruler_adopted: audits/KH0-ANSWER-AUTO-LIFT-RULER-ADOPTED-20260806.md
go: audits/KH0-ANSWER-AUTO-LIFT-GO-20260806.md
inherits_boundaries:
  - no web／對話裸 approve knowledge_source（T2：機械 system 可；見 AI-SOURCE-APPROVE-T2）
  - FZ/GATE-keep · no-SIM-apply · hold 市場 #1
  - 錯料可錯答；可修正可見
t2_source: audits/AI-SOURCE-APPROVE-T2-EXECUTED-20260806.md
self_reported: true
---

# KH0-ANSWER-AUTO-LIFT plan-first · 2026-08-06

> **一句**：顧問作答在 **核可尺判定「答對」** 後，對所據 `item_id` **自動**跑 `progressive_item`／層評估，把 admit_depth 推向 **KH1→KH2**；來源升級走 T2 機械路徑（非 web／對話）。  
> **性質**：[I] plan-first；開碼須 go；**T2** 已放寬來源機械 activate。  
> **主軸位**：evolve 計畫 §4 **#1c**（已 ADOPTED 為現主軸）。

---

## §0 護欄

```text
KH0-ANSWER-AUTO-LIFT-plan | FZ/GATE-keep | no-web-dialog-approve | hold-#1
# admit_depth 自動抬；來源：T2 機械 system 可（每批≤1、has_text）
```
---

## §1 觸發與客體

| 項 | 草案 |
|---|---|
| **何時** | `advise()`（或等價）完成一輪且 `verdict.pass`，且存在 item 級引文 |
| **客體** | 本回答所用 **ItemCitation.item_id**（去重）；不含純 works |
| **答錯／decline** | **不抬**；留下可對照引文供人修正資料 |
| **重複答對** | 幂等：已 ≥2 則 no-op；1→2 可再推 |

---

## §2 核可尺（候確認；意向＝R-hybrid）

| ID | 規則 | 自動抬？ |
|---|---|---|
| **R-cite** | 答中抽樣之數字／拉丁專詞／關鍵 CJK 片語 ⊆ 引文連合文本 | 是（主路徑） |
| **R-human** | 人點「此答可抬」 | 是（邊界／R-cite 失敗但人認） |
| **R-judge** | 本地 LLM yes/no（可選臂；本 v1 可不開） | 可選 |
| **R-hybrid（意向）** | 先 R-cite；不通過不抬；可選掛 R-human 旁路 | **計畫預設推薦** |

**未確認前不得開碼。** Steward 貼一句 `ruler=R-hybrid`（或其它）即鎖定。

---

## §3 自動抬層行為（碼開後）

1. 核可 pass → 對每個 item：`progressive_item(..., up_to=2, apply=True)`；**T2**：預設可 `activate_source`（每批最多 1 `source_key`、須 `has_text`；`--no-activate-source` 關）  
2. 預期：標題件經 **global_title_kh1** 可過 KH1；KH2 仍視來源 active／assist；有原文＋qual 者可到 1／2  
3. 寫 `knowhow_auto_admit_run`／state；另帳 `knowhow_answer_lift_log` 記：query_hash、item_ids、ruler、pass/fail（activate 交鏈 note）  
4. **禁** web／對話裸 `transition(approve/activate)`；機械路徑僅經 `maybe_activate_source`（system actor）

### Errata · T2（2026-08-06）

初版硬碼 `activate_source=False`。Steward 確認 v1.48 機械可並裁 **T2-go** 後，以 `AI-SOURCE-APPROVE-T2-EXECUTED` 為準：預設 **on**。
### KH1／KH2 語意提醒（evaluate · 2026-08-06 更新）

| 層 | 無原文標題件 | 有原文＋條件 |
|---|---|---|
| KH0 | A.1 pass | pass |
| KH1 | **title → pass**（`global_title_kh1`） | qual pass 或原文旁路 |
| KH2 | 視來源 active／assist 旗 | 可 pass |

→ 「自動抬向 1／2」＝**盡力前進到 cap=2**；標題件現可穩過 KH1；KH2 非保證。誠實留 note。

---

## §4 分階段

| 階 | 交付 | GO |
|---|---|---|
| P0 | 本 plan＋主軸 ADOPTED | 本輪文件 |
| P1 | Steward 確認 `ruler=` | 一句 |
| P2 | 最小碼：R-cite＋lift log（初版 `activate_source=False`） | `KH0-ANSWER-AUTO-LIFT-go` ✅ |
| P2b | T2：機械 activate 預設 on／max 1 | `AI-SOURCE-APPROVE-T2-go` ✅ |
| P3 | 掛 advise 熱路徑（feature-flag 預設 off） | `KH0-ANSWER-AUTO-LIFT-wire-advise-go` ✅ |
| P4 | R-human 旁路 UI／CLI | 另句 |

---

## §5 Paste-ready

確認尺（例）：

```text
KH0-ANSWER-AUTO-LIFT-ruler = R-hybrid
```

開碼：

```text
KH0-ANSWER-AUTO-LIFT-go | FZ/GATE-keep | no-activate-source | ruler=R-hybrid
```

---

## §6 驗收（計畫本身）

1. 主軸＝#1c 自動抬層已書面。  
2. 明分：admit 自動 ≠ 來源放行。  
3. 尺未確認前無業務碼。  

*完。[I] self-reported。*
