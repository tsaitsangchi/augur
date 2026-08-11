---
status: executed
series: local_ai_kh
kind: kh8_a2_l2
date: 2026-08-11
viewpoint: 2026-08-11T08:27+08:00
go: audits/KH8-DISCRIM-A2-L2-GO-20260811.md
log: /tmp/kh8-a2-l2/run.log
projection: /tmp/kh8-a2-l2/projection.json
prior_l1: audits/KH8-DISCRIM-A2-L1-EXECUTED-20260811.md
paste: "KH8-DISCRIM-A2-L2-EXECUTED | dry-run | proj-ok=False | no-write-main | E-keep | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜A2-L2 dry-run · 2026-08-11

```text
KH8-DISCRIM-A2-L2 | full-pop via compute_evidence_weight_a2_v1 | no-write | ok仍False
```

## 对拍（最新 weight／item · n=146,399）

| 尺 | live legacy | A2-v1 投影 |
|---|---|---|
| band | high **146003** · absent 380 · low 16 | medium **143057** · high **2946** · absent 385 · low 11 |
| minority | **0.0027** | **0.0228** |
| score p50 | 0.72 | **0.431** |
| disc | ok=**False** | 投影 ok=**False**（1′：0.0228＜0.05） |
| 默认公式 | **legacy** | （未切） |

## 判读

1. 入码公式复现 sim 方向：打破 high 墙，分数展开。  
2. **仍未过 θ**——与 L1／sim 诚实一致；**≠** 可撤 E／抬 8。  
3. **未写库**（`wrote_db=false`）。

## 未做

L3 UPDATE · 切默认 A2 · MERGE · 动 B3

```text
KH8-DISCRIM-A2-L2-EXECUTED | proj-ok=False | no-write-main | E-keep | hold-#1
# 主軸: hold tip≥08-11；L3 另双明示
```

*完。*
