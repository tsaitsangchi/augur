---
status: executed
series: local_ai_kh
kind: kh8_m3_pool_gate
date: 2026-08-11
viewpoint: 2026-08-11T08:25+08:00
go: audits/KH8-DISCRIM-M3-POOL-GATE-GO-20260811.md
inventory: audits/KH8-DISCRIM-M3-POOL-GATE-INVENTORY-20260811.md
paste: "KH8-DISCRIM-M3-pool-gate-EXECUTED | code-gate | no-merge | E-keep | hold-#1 | check-rc=0"
self_reported: true
layer: "[I]"
---

# EXECUTED｜M3 答池闸码 · no-merge · 2026-08-11

> **判定**：**码闸绿** · **未 MERGE** · 主表 disc 仍 **False** · E **stop-at-7** 不撤 · hold-#1 watcher 续。

## 1. 落地

| 产物 | 说明 |
|---|---|
| `src/augur/knowledge/pool_gate.py` | SSOT：`answer_pool_eligible`／`weight_alone_insufficient`／activate／KH8 text 谓词＋selftest |
| `scripts/check_kh8_pool_gate.py` | 静扫 retrieve／readout／evidence／AUTO-LIFT 不变式 |
| 接线 | `evidence.evaluate_item_evidence` → `kh8_evaluate_requires_text`；`answer_auto_lift.lift_items` → `activate_source_eligible`；readout／retrieve docstring 钉契约 |

## 2. 验收

```text
python -m augur.knowledge.pool_gate --selftest   # 全通过
python scripts/check_kh8_pool_gate.py --check    # ok=true fail_n=0
```

## 3. 明确未做

- 併 `shadow_t2` → 主表  
- 撤 E／抬 depth≥8  
- A2-L1 公式码  
- 动 B3／serve

```text
KH8-DISCRIM-M3-pool-gate-EXECUTED | code-gate | no-merge | E-keep | hold-#1
# 下一刀候選（另授）:
KH8-DISCRIM-merge-M3-go | dual-explicit | after-gate-green
KH8-DISCRIM-A2-L1-go | code+selftest | no-write-main
# 主軸: hold-#1 → B3@08-11 when tip ready
```

*完。*
