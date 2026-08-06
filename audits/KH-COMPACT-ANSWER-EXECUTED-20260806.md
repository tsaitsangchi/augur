---
status: executed
series: kh_loop_evolve
date: 2026-08-06
paste: "KH-COMPACT-ANSWER-EXECUTED | freeze-cites | short-prompt | strip-meta-quotes | auto-on-readout"
plan: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
trigger: "retrieve hit 277948; full advise 900s timeout; freeze~250s but model meta-quoted query → guard fail"
self_reported: true
---

# EXECUTED｜KH 緊湊作答（自動）· 2026-08-06

## 診斷（Steward）

| 層 | 結論 |
|---|---|
| KH／入庫／命中 | **OK**（可命中 277948） |
| 瓶頸 | **本機 LLM／prompt 體積**；模型「想題」長文＋把**用戶問句加引號** → guard `#1 引文非逐字` |

## 自動處置（always-on for readout／local 知-how）

1. **凍結引文**：`prefer_item_ids`（readout）獨占；`max_chars≈2400`／`max_n≈4`  
2. **短答 prompt**：`build_compact_knowhow_prompt`（禁想題／禁引號／禁複述問句／禁三姿態）  
3. **LLM**：`wrap_compact_llm` → `think=False`＋`num_predict`（預設 512，env `AUGUR_COMPACT_NUM_PREDICT`）  
4. **抛光**：去引號框＋剝「首先我需要理解…」頭 → 再進 guard  
5. **模式**：`answer_mode=auto|compact|full|two_phase`（two_phase＝同回合先凍再短答）

## 碼

| 檔 | 變更 |
|---|---|
| `src/augur/knowledge/compact_answer.py` | 新 |
| `src/augur/advisor/prompt.py` | `build_compact_knowhow_prompt` |
| `src/augur/advisor/advise.py` | `answer_mode`；自動緊湊 |

## 驗

```text
python -m augur.knowledge.compact_answer --selftest  # ✓
# 模擬先前失敗答：polish 後 guard pass ✓
```

*executed。開啟 full：`answer_mode=full` 或 `AUGUR_ANSWER_MODE=full`。*
