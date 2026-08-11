---
status: go
series: struct
kind: cycle_break
ring: advisor-deliberation
date: 2026-08-08
plan: reports/augur_struct_cycle_break_go_plan_20260808.md
prior: audits/STRUCT-CYCLE-BREAK-AUDIT-FEATURES-EXECUTED-20260808.md
paste: "STRUCT-CYCLE-BREAK-go | ring=advisor-deliberation | FZ/GATE-keep | zero-predict | one-ring"
self_reported: true
layer: "[I]"
---

# GO｜STRUCT-CYCLE-BREAK · ring=advisor-deliberation · 2026-08-08

```text
STRUCT-CYCLE-BREAK-go | ring=advisor-deliberation | FZ/GATE-keep | zero-predict | one-ring
# 斷：deliberation.engine → advisor.ollama
# 改：LLM 工廠 SSOT → augur.llm.ollama；advisor.ollama 再匯出 BC
```

## 授權

Steward AskQuestion：`next=advisor-tri` → `edge=advisor-delib` → `confirm=go`。

## 准許

| 項 | 內容 |
|---|---|
| 新包 | `src/augur/llm/ollama.py`（內容自 advisor.ollama） |
| 改 | `deliberation/engine.py` import；`advisor/ollama.py` shim；`import_isolation` 關 advisor 例外 |
| 保留 | `advisor.effort` → `deliberation`（單向 ultracode 路由） |

## 禁止

- 同窗動 knowledge／philosophy 邊  
- predict／B3／serve  

*go。*
