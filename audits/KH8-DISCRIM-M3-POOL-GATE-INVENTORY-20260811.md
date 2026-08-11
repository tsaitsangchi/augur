---
status: inventory
series: local_ai_kh
kind: kh8_m3_pool_gate
date: 2026-08-11
viewpoint: 2026-08-11T08:22+08:00
paste: "KH8-DISCRIM-M3-pool-gate-inventory | FZ/GATE-keep | no-merge | E-keep | hold-#1"
adopt: audits/KH8-DISCRIM-M3-ADOPTED-20260808.md
plan: reports/augur_kh8_discrim_merge_adjudication_go_plan_20260808.md
hold: audits/HOLD-1-CONTINUING-KH-IDLE-20260811.md
self_reported: true
layer: "[I]"
---

# INVENTORY｜M3 答池闸（pool-gate）· 2026-08-11

> Steward：KH 閒時 → **m3_inv** → **code_now**。主軸 hold＠08-11 不讓。  
> **一句**：M3＝准併方向＋硬闸；本窗只造／鎖闸，**不 MERGE** 影表、不撤 E。

## §0 LIVE

| 錨 | 值 |
|---|---|
| 主 `knowhow_evidence_weight` n | **146,808** · disc **ok=False**（minority≈0.0027） |
| 影 `knowhow_evidence_weight_shadow_t2` n | **139,043**（實驗∪主曾 ok=True） |
| E | **stop-at-7** 直至生產 disc 真綠＋闸過 |
| A2 | 公式主軸已採納；**碼未落地** |

## §1 热路径现况（對 M3 §2.2）

| 路徑 | 现状 | 闸缺口 |
|---|---|---|
| `retrieve_items`／`retrieve_all` | JOIN `knowledge_item_text`＋sentence／emb＋`kh4=eligible`；**不**掃 weight 排序 | 有實作；缺 **明示契約／探針** |
| `readout` resolve／citations | 必 JOIN `item_text`；無權重命中 | 同上 |
| `evaluate_item_evidence`（KH8） | `has_text` 假 → **fail** `kh8_no_text` | 已守；需入闸探针 |
| AUTO-LIFT `activate` | 須 `source_key ∧ has_text` | 已守；抬層本體不憑 weight |
| 消費 `latest_weight_for_item` | honest view；合成／深度軸 | **权≠可答** 未單点 SSOT |

## §2 本窗目标（码闸 · no-merge）

1. SSOT：`pool_gate`——**weight 命中 ≠ 可答**；答池须 `has_text`（或等价：已入 CLEAN＋item_text 路径）。  
2. 探針：`check_kh8_pool_gate.py`——源码／selftest 锁上表不变式；红则 rc≠0。  
3. 轻接线：注释＋selftest 引用；**不**写主表、**不**併影。  
4. 禁：撤 E；宣告 depth≥8；假绿 disc。

## §3 明确非本窗

- MERGE T2→主表（另双明示 `merge-M3-go`）  
- A2-L1 公式码（∥可另刀）  
- SERVE／B3／sim-apply

```text
KH8-DISCRIM-M3-pool-gate-inventory | no-merge | E-keep | hold-#1
# next: GO → code+selftest → EXECUTED
```

*完。*
