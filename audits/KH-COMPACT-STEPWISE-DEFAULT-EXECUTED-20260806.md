# KH-COMPACT-STEPWISE-DEFAULT — EXECUTED 2026-08-06

```text
KH-COMPACT-STEPWISE-DEFAULT-executed | FZ/GATE-keep
# GO: audits/KH-COMPACT-STEPWISE-DEFAULT-GO-20260806.md
```

## 變更

- `COMPACT_KNOWHOW_PROMPT`：預設强制 `1. 2. 3.`、每行一步、禁一段摘要、禁整篇照抄  
- `AUGUR_COMPACT_STEPWISE=0` → `COMPACT_KNOWHOW_PROMPT_SUMMARY`（舊短摘要口吻）  
- `wrap` 仍保留呼叫端 llm_fn（前案）  
- 計畫 SSOT `rev=readout-compact-raw-v2`：K-02g／Ρ0.3d／#1g → ✅  

## 驗

`python -m augur.advisor.prompt --selftest`（compact 預設逐步／off→摘要）

*executed。*
