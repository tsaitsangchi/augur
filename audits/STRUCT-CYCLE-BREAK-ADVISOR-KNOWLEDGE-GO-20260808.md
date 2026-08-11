---
status: go
series: struct
kind: cycle_break
ring: advisor-knowledge
date: 2026-08-08
plan: reports/augur_struct_cycle_break_go_plan_20260808.md
prior: audits/STRUCT-CYCLE-BREAK-ADVISOR-DELIB-EXECUTED-20260808.md
paste: "STRUCT-CYCLE-BREAK-go | ring=advisor-knowledge | FZ/GATE-keep | zero-predict | one-ring | steward-mandate=continuous"
self_reported: true
layer: "[I]"
---

# GO｜STRUCT-CYCLE-BREAK · ring=advisor-knowledge · 2026-08-08

```text
STRUCT-CYCLE-BREAK-go | ring=advisor-knowledge | FZ/GATE-keep | zero-predict | one-ring
# steward-mandate=continuous（授權連做建議順位）
# 斷：knowledge → advisor（LLM／共用工具改走 llm 或倒置）
# 保留：advisor → knowledge（檢索／答覆編排單向）
```

## 授權

Steward：「可以依你建議一直往下做」。

## 准許

- 改 `knowledge/*` 內 `augur.advisor` import；必要時抽共用至 `augur.llm`  
- 驗：explore 無 `advisor`↔`knowledge`；相關 selftest  

## 禁止

- 同窗默斷 knowledge↔philosophy（下一刀）  
- predict／B3／serve  

*go。*
