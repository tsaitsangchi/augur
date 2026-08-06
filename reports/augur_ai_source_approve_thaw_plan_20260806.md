---
title: AI／機械路徑 · 來源 approve／activate 解凍探討計畫
subtitle: 高風險治權；對齊憲章 v1.48 與 ops「唯人／禁 AI」敘事落差
status: t2_executed
choice: T0+T2
adopted: audits/AI-SOURCE-APPROVE-THAW-T0-ADOPTED-20260806.md
t2_go: audits/AI-SOURCE-APPROVE-T2-GO-20260806.md
t2_executed: audits/AI-SOURCE-APPROVE-T2-EXECUTED-20260806.md
date: 2026-08-06
viewpoint: 2026-08-06T10:40+08:00
layer: "[I]"
role: 探討「AI 來源 approve」落差；T0 敘事＋T2 AUTO-LIFT 機械 activate 已落地（見 t2_executed）
ssot_code: AI-SOURCE-APPROVE-THAW-PLAN-20260806
self_reported: true
depends_on:
  - docs/系統架構大憲章_v1.54.0.md
  - src/augur/knowledge/curation.py
  - reports/augur_kh10_auto_admit_plan_20260729.md
  - reports/augur_ai_admission_assist_plan_20260728.md
  - reports/augur_kh0_answer_auto_lift_plan_20260806.md
  - audits/KH0-ANSWER-AUTO-LIFT-EXECUTED-20260806.md
inherits_boundaries:
  - 不改 HUMAN_ONLY／不改 web 寫路徑
  - license／負面清單／#1 禁幻造全文仍守
  - web／對話 Agent 仍不可裸 approve
---

# AI／機械路徑 · 來源 approve／activate 解凍探討計畫（2026-08-06）

> **一句**：釐清「AI 來源 approve」在**憲章已半開**與**操作仍常關**之間的落差；Steward 已裁 **T0**（敘事）＋ **T2**（AUTO-LIFT 機械 activate，見 `AI-SOURCE-APPROVE-T2-EXECUTED`）。  
> **觸發**：Steward 選 `thaw_plan`（「要開 AI 可否 approve 計畫書」）。  
> **性質**：[I] 高風險治權；**加嚴／改判準須人裁**（通則二）。

---

## §0 現況真相（勿混三層）

| 層 | 誰 | 現況 |
|---|---|---|
| **憲章 v1.48+** | 法理 | **廢止**「approve／activate 唯人」；機械路徑（`system=True`，如 `system:kh10_auto_admit`）**得**跑狀態機升級並留 `knowledge_source_review_log` |
| **碼 `curation.py`** | 實作 | `HUMAN_ONLY = set()`；`maybe_activate_source`／`progressive_item(activate_source=True)` 可機械 approve→activate |
| **gov／web** | UI | **零寫**；頁面明示 approve 走 CLI＋TTY＋`is_superuser`——**瀏覽器／聊天 AI 結構上不能按按鈕放行** |
| **本回合 KH ops** | 操作契約 | T0：web／對話仍禁。**T2（已 EXECUTED）**：AUTO-LIFT 預設可機械 activate（每批 ≤1 源、需 has_text）。敘事「禁 AI 來源 approve」＝禁**對話代理／無審計擴權**，非否認真憲章／T2 機械路徑 |

```text
「AI 來源 approve」≠ 單一開關
  A. 憲章機械 system 路徑（已存在）
  B. 對話式 Agent／Cursor 代跑 CLI（人環境·超權風險）
  C. Web 按鈕（結構上禁止，應維持）
```

**結論先行**：若問題是「憲法上可不可以機械 approve」→ **已經可以（v1.48）**。  
若問題是「聊天 AI／AUTO-LIFT 要不要打開 activate」→ **這才是本計畫要裁的解凍幅度**。

---

## §1 為何 ops 常寫「禁 AI approve」

| 理由 | 說明 |
|---|---|
| **責信** | 來源 active＝營運可見／可答池擴大；誤放行成本高於誤擋 |
| **通道分離** | assist＝建議；approve＝終態；混用＝gov 假綠 |
| **代理範圍** | Cursor／對話未持 `app_user.is_superuser` TTY 時，不應經旁路寫來源 |
| **本輪 KH 主軸** | D-Data／答對抬 **admit_depth**，刻意**不**綁來源狀態機，避免「答對一篇就 activate 整源」 |

---

## §2 解凍選項（Steward 擇一；本檔不代選生效）

| ID | 內容 | 風險 | 要否改憲 |
|---|---|---|---|
| **T0 敘事對齊** | 改計畫／gov 文案：寫明「機械 system 可；web／對話代理不可」 | 低 | 否 |
| **T1 ASSIST-only 加強** | 只加強 ADM-AI-ASSIST 排隊／真模型；**仍不**由對話路徑 approve | 低 | 否 |
| **T2 AUTO-LIFT 可选 activate** | 答對抬層時，對**單一 source_key** 允許 `activate_source=True`（仍 system actor、有 lift_log） | 中：一篇答→整源 active | 否（已合 v1.48）；須**操作 GO** |
| **T3 代理 CLI 授辭** | 明示何種 Agent 可代跑 `review_knowledge_source.py --approve`（仍要 superuser＋TTY 或改認證） | 高 | 可能要安全章 |
| **T4 Web 放行鈕** | gov 頁加 approve——**逆結構** | 極高 | 要＋強烈不薦 |
| **T5 收斂回唯人** | 恢復 HUMAN_ONLY⊇{approve,activate} | 與 v1.48 衝突 | **要入憲撤回** |

**建議討論預設（非自動生效）**：**T0＋T1** 先做；T2 僅當 Steward 要「答對自進化含來源可見」時另 GO；**不薦 T4**；T5 僅當要撤回一律准入哲學。

---

## §3 若裁 T2（AUTO-LIFT 連動來源）——契約草案

僅在未來 `…-go` 生效；本檔無權執行。

1. **觸發**：R-hybrid 答對且 lift 成功；`activate_source` 旗標明示 on  
2. **範圍**：僅 citations 出現之 `source_key`；**一批最多 N 源**（建議 N=1）  
3. **硬閘**：license／負面清單／non-AI-fulltext 既有 CHECK；失敗→不抬來源、admit 仍可寫  
4. **帳**：`knowledge_source_review_log`＋`knowhow_answer_lift_log.note` 交鏈  
5. **禁**：web；對話 Agent 直接 SQL；無 lift_id 的裸 approve  

Paste（**未來**，勿與本 plan 混貼）：

```text
AI-SOURCE-APPROVE-T2-go | FZ/GATE-keep | system-actor-only | max-sources-1 | tie-lift-log
# 讀本檔 §3；≠ web；≠ 對話無審計放行
```

---

## §4 與 KH 自進化主軸關係

| 主軸 | 與來源 approve |
|---|---|
| D-Data／KH0–2 admit | **正交**；可不碰來源 |
| AUTO-LIFT R-hybrid | **T2**：預設 `activate_source=True`（`--no-activate-source` 可關） |
| global_title_kh1 | 只改 evaluate KH1；**不** approve |

解凍來源 ≠ 完成 KH 抬層；兩者可永久分離（`--no-activate-source` 即分離）。

---

## §5 分階段

| 階 | 交付 | 狀態 |
|---|---|---|
| P0 | 本探討計畫＋REGISTER | ✅ |
| P1 | Steward 選 T0…T5 | ✅ T0＋後續 T2 |
| P2 | 若 T0：改 gov／計畫措辭 | ✅ |
| P3 | 若 T2：§3 開碼 | ✅ `AI-SOURCE-APPROVE-T2-EXECUTED` |
| P4 | 若 T5：入憲案 | 未選 |

---

## §6 Paste-ready

採納探討（文件）：

```text
AI-SOURCE-APPROVE-THAW-PLAN-adopt | docs-only | no-approve-exec
# 讀: reports/augur_ai_source_approve_thaw_plan_20260806.md
```

裁示例：

```text
AI-SOURCE-APPROVE-CHOICE = T0
# 或 T1 / T2 / T3 / T4 / T5
```

---

## §7 驗收（本計畫書）

1. Steward 能區分：憲章機械可 ≠ web／對話可。  
2. 五選項利弊表存在。  
3. 無任何本檔觸發的 approve／activate。  

*完。[I] self-reported（#32a）。*
