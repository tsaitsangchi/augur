---
status: executed
series: struct
kind: cycle_break
ring: advisor-knowledge
date: 2026-08-08
viewpoint: 2026-08-08T13:00+08:00
go: audits/STRUCT-CYCLE-BREAK-ADVISOR-KNOWLEDGE-GO-20260808.md
paste: "STRUCT-CYCLE-BREAK-go | ring=advisor-knowledge | FZ/GATE-keep | zero-predict | one-ring"
self_reported: true
layer: "[I]"
---

# EXECUTED｜STRUCT-CYCLE-BREAK · ring=advisor-knowledge · 2026-08-08

```text
STRUCT-CYCLE-BREAK-go | ring=advisor-knowledge | FZ/GATE-keep | zero-predict | one-ring
```

## 斷法

| 前 | 後 |
|---|---|
| `knowledge.compact_answer` → `advisor.ollama` | → **`augur.llm.ollama`** |
| `knowledge.answer_auto_lift` → `advisor.relevance` | → **`knowledge.token_overlap`** |
| token helpers 住 advisor.relevance | SSOT 抽至 `knowledge/token_overlap.py`；relevance 再匯入 |

保留：`advisor` → `knowledge`（編排／檢索單向）。

## 驗收

| 測 | 結果 |
|---|---|
| relevance／answer_auto_lift／compact_answer `--selftest` | **全通過** |
| `explore_struct_cycles` | `advisor`↔`knowledge` **消失**；三角 **0**；剩 `knowledge`↔`philosophy` |

*完。[I]*
