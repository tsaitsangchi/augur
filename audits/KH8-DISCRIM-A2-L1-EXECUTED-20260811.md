---
status: executed
series: local_ai_kh
kind: kh8_a2_l1
date: 2026-08-11
viewpoint: 2026-08-11T08:28+08:00
go: audits/KH8-DISCRIM-A2-L1-GO-20260811.md
spec: reports/augur_kh8_a2_land_design_spec_20260808.md
paste: "KH8-DISCRIM-A2-L1-EXECUTED | code+selftest | default=legacy | no-write-main | E-keep | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜A2-L1 · 公式入码 · 2026-08-11

> **判定**：**A2-v1 纯函数＋selftest 绿** · **默认仍 legacy** · **未写主表** · E／θ／depth 不动 · hold-#1 续。

## 落地

| 项 | 值 |
|---|---|
| `compute_evidence_weight_legacy` | 现行公式（默认） |
| `compute_evidence_weight_a2_v1` | land-spec §2.2 |
| `compute_evidence_weight(..., formula=)` | 默认 `legacy`；`A2-v1`／`a2` 显式 |
| selftest | 齐备+1句 A2≠high／≤0.55；0句≤0.35；legacy+1句仍 high |

```text
python -m augur.knowledge.evidence --selftest   # RC=0（含 A2-L1 锁）
```

## 未做

L2 对拍 · L3 UPDATE 主表 · 切默认 A2 · MERGE · 撤 E

```text
KH8-DISCRIM-A2-L1-EXECUTED | default=legacy | no-write-main | E-keep | hold-#1
# 下一刀候選: A2-L2-dry | no-write｜或 hold tip≥08-11
```

*完。*
