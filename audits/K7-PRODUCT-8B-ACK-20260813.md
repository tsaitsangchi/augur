---
status: accepted
series: local_ai_kh
track: K7
date: 2026-08-13
viewpoint: 2026-08-13T10:46+08:00
prior: audits/KH-K7-PRODUCT-8B-EXECUTED-20260812.md
prior_4b: audits/KH-K7-ANCHOR-LIVE-EXECUTED-20260812.md
ssot: reports/augur_kh_opt_stepwise_best_next_plan_20260812.md
paste: "K7-ack | product=8b+960 | stepwise-4b→8b | 4b-weak-hold | no-LLM-rebench"
self_reported: true
layer: "[I]"
---

# ACK｜K7 產品 8b＋960／4b 弱守

```text
K7-ack | product=8b+960 | stepwise-4b→8b | 4b-weak-hold | no-LLM-rebench
```

## 釘

| 項 | 值 |
|---|---|
| 產品 compact `num_predict` | **960**（碼預設；ops drop-in 同） |
| 步驟／操作題 | **4b→8b**（`prefer_8b_for_stepwise`；可 `AUGUR_STEPWISE_FORCE_8B=0`） |
| 本機 serve（腳本） | 已 `--model qwen3:8b` |
| **4b 弱守** | 錨題 live＠4b 口吻未達（既帳）；**不**當產品逐步預設；不重跑重型 LLM 本窗 |

## 本窗自測

| 模組 | RC |
|---|---|
| `augur.advisor.effort --selftest` | **0**（含 stepwise 4b→8b） |
| `augur.knowledge.compact_answer --selftest` | **0** |

未：全量 8b 錨題重跑；改前端 default_tier；授 4b 為產品逐步主路徑。

*ack。*
