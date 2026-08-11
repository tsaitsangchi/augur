---
status: executed
series: struct
kind: cycle_break
ring: advisor-deliberation
date: 2026-08-08
viewpoint: 2026-08-08T12:55+08:00
go: audits/STRUCT-CYCLE-BREAK-ADVISOR-DELIB-GO-20260808.md
paste: "STRUCT-CYCLE-BREAK-go | ring=advisor-deliberation | FZ/GATE-keep | zero-predict | one-ring"
self_reported: true
layer: "[I]"
---

# EXECUTED｜STRUCT-CYCLE-BREAK · ring=advisor-deliberation · 2026-08-08

```text
STRUCT-CYCLE-BREAK-go | ring=advisor-deliberation | FZ/GATE-keep | zero-predict | one-ring
```

## 斷法

| 前 | 後 |
|---|---|
| `deliberation.engine` → `advisor.ollama` | → **`augur.llm.ollama`** |
| `advisor.ollama` 本體 | **shim** 再匯出 BC |
| `import_isolation` 放行 deliberation→advisor | **禁** `augur.advisor`（LLM＝`augur.llm`） |

新包：`src/augur/llm/{__init__,ollama}.py`。

## 驗收

| 測 | 結果 |
|---|---|
| `llm.ollama`／`advisor.ollama`／`deliberation.engine` `--selftest` | **全通過** |
| `explore_struct_cycles` | `advisor`↔`deliberation` **消失**；剩餘 2＝advisor↔knowledge／knowledge↔philosophy |

## 不做

- knowledge／philosophy 邊（下刀另帳）  
- predict／B3／serve  

*完。[I]*
